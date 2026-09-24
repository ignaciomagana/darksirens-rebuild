#!/usr/bin/env python3
"""jax.profiler tracing for the benchmark harness, and a trace -> op-table parser.

Three uses:

1. The main harness with its timed loop traced (no edit of bench_fixed_theta.py):

       python trace_tools.py main --trace DIR [--top 25] -- <bench_fixed_theta.py arguments>

   ``bench_common.PhaseClock.mark`` is wrapped so that ``jax.profiler.start_trace(DIR)``
   runs right after the ``timed_loop_start`` stamp and ``stop_trace`` right after
   ``timed_loop_end``; each timed call is wrapped in a ``TraceAnnotation("bench_call")``
   that also blocks on the result (the loop blocks again, a no-op). Only the timed
   loop is traced (first call, warm-ups and the untimed passes are not). The record
   is then annotated with ``trace`` (the parsed summary) and a gap: its warm timings
   include profiler overhead; take timings from an untraced record.

2. ``bench_components.py --trace DIR`` calls :func:`trace_components`: after the
   untimed-for-the-record parity pass, each component's warm calls are re-run inside
   ``jax.profiler.trace(DIR/<component>)`` (perfetto file included) and every traced
   output is checked bit for bit against the untraced one.

3. Parsing / checking:

       python trace_tools.py parse DIR [--top 25] [--annotation bench_call] [--json F] [--md F]
       python trace_tools.py check-numerics TRACED.json UNTRACED.json [--out F.json]

The parser reads the newest ``DIR/plugins/profile/<session>/*.trace.json.gz``
(Chrome trace format written by ``jax.profiler``). Op events are
* GPU: the ``/device:GPU:N`` process, its ``XLA Ops`` line (else its stream lines);
* CPU: the XLA executor threads (``tf_XLA*``) of ``/host:CPU``, restricted to
  HLO-instruction-like names (no ``::``, spaces, parentheses or ``$``).
Per op name it reports self time (children on the same thread subtracted), count
and share of the total op self time; per category (suffixes ``.N`` / ``.clone``
stripped) and per kind (fusion, reduce, gather/slice, scatter, control, layout,
library, sort, other). "Device time" is the union of the op intervals (on CPU,
over all executor threads); idle gaps are the complement of that union inside each
``bench_call`` annotation window (or inside the op span if there is none).
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import glob  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SUMMARY_SCHEMA = "darksirens-trace-summary/1"
ANNOTATION = "bench_call"
_HLO_NAME = re.compile(r"[A-Za-z_][\w\-]*(\.[\w\-]+)*")
_SUFFIX = re.compile(r"\.(clone|\d+)$")


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------
def find_trace_file(trace_dir):
    """Newest ``plugins/profile/<session>/*.trace.json.gz`` under ``trace_dir``."""
    sessions = [p for p in glob.glob(os.path.join(trace_dir, "plugins", "profile", "*")) if os.path.isdir(p)]
    if not sessions:
        raise FileNotFoundError(f"no plugins/profile/<session> under {trace_dir}")
    sess = max(sessions, key=os.path.getmtime)
    files = [f for f in glob.glob(os.path.join(sess, "*.trace.json.gz"))
             if not os.path.basename(f).startswith("perfetto")]
    if len(files) != 1:
        raise FileNotFoundError(f"expected one *.trace.json.gz in {sess}, found {files}")
    return files[0]


def category(name):
    c = name
    while True:
        c2 = _SUFFIX.sub("", c)
        if c2 == c:
            return c
        c = c2


def kind(cat):
    c = cat.lower()
    if "memcpy" in c or "memset" in c:
        return "transfer"
    if "fusion" in c:
        return "fusion"
    if c.startswith("reduce") or c in ("all-reduce",):
        return "reduce"
    if c.startswith(("gather", "dynamic-slice", "slice")):
        return "gather/slice"
    if c.startswith(("scatter", "dynamic-update-slice")):
        return "scatter"
    if c in ("while", "call", "conditional") or c.startswith(("while", "conditional")):
        return "control"
    if c.startswith(("copy", "transpose", "bitcast", "concatenate", "pad", "broadcast", "reshape")):
        return "layout"
    if c.startswith(("custom-call", "cublas", "cudnn", "cutlass", "gemm", "dot")):
        return "library"
    if c.startswith("sort"):
        return "sort"
    return "other"


def _union(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            if e > out[-1][1]:
                out[-1][1] = e
        else:
            out.append([s, e])
    return out


def _clip(union, w0, w1):
    res = []
    for s, e in union:
        if e <= w0 or s >= w1:
            continue
        res.append([max(s, w0), min(e, w1)])
    return res


def _self_times(events):
    """Self time per event on ONE thread (children fully nested are subtracted)."""
    evs = sorted(events, key=lambda e: (e["ts"], -e["dur"]))
    selft = [e["dur"] for e in evs]
    stack = []  # indices of open events
    for i, e in enumerate(evs):
        while stack and evs[stack[-1]]["ts"] + evs[stack[-1]]["dur"] <= e["ts"]:
            stack.pop()
        if stack:
            p = stack[-1]
            selft[p] -= min(e["dur"], evs[p]["ts"] + evs[p]["dur"] - e["ts"])
        stack.append(i)
    return list(zip(evs, [max(0.0, s) for s in selft]))


def summarize_trace_file(path, top_n=25, annotation=ANNOTATION):
    with gzip.open(path, "rb") as f:
        doc = json.load(f)
    ev = doc.get("traceEvents", [])
    pname, tname = {}, {}
    for e in ev:
        if e.get("ph") == "M":
            if e.get("name") == "process_name":
                pname[e["pid"]] = e["args"]["name"]
            elif e.get("name") == "thread_name":
                tname[(e["pid"], e["tid"])] = e["args"]["name"]
    X = [e for e in ev if e.get("ph") == "X" and "dur" in e and "ts" in e]
    windows = sorted((float(e["ts"]), float(e["ts"]) + float(e["dur"])) for e in X
                     if e.get("name") == annotation)
    gpu_pids = [p for p, n in pname.items() if str(n).startswith("/device:GPU")]
    gpu_events = [e for e in X if e["pid"] in gpu_pids]
    if gpu_events:
        mode = "gpu"
        lines = {(e["pid"], e["tid"]) for e in gpu_events}
        ops_lines = [ln for ln in lines if str(tname.get(ln, "")).strip() == "XLA Ops"]
        if ops_lines:
            src = "GPU 'XLA Ops' line"
        else:
            ops_lines = [ln for ln in lines if str(tname.get(ln, "")).startswith("Stream")]
            src = "GPU stream lines (kernels; named by their hlo_op arg when present)"
        ops = [e for e in gpu_events if (e["pid"], e["tid"]) in set(ops_lines)]
        if not ops_lines or str(tname.get(ops_lines[0], "")).strip() != "XLA Ops":
            ops = [dict(e, name=str((e.get("args") or {}).get("hlo_op") or e["name"])) for e in ops]
    else:
        mode = "cpu"
        host = [p for p, n in pname.items() if str(n).startswith("/host:CPU")]
        ops = [e for e in X if e["pid"] in host
               and str(tname.get((e["pid"], e["tid"]), "")).startswith(("tf_XLA", "XLA"))
               and "::" not in e["name"] and " " not in e["name"] and "(" not in e["name"]
               and not e["name"].startswith("$") and _HLO_NAME.fullmatch(e["name"])]
        src = "CPU XLA executor threads (tf_XLA*), HLO-instruction-named events"
    by_thread = {}
    for e in ops:
        by_thread.setdefault((e["pid"], e["tid"]), []).append(e)
    rows = {}
    self_total = 0.0
    for evs in by_thread.values():
        for e, st in _self_times(evs):
            r = rows.setdefault(e["name"], {"count": 0, "self_us": 0.0, "total_us": 0.0})
            if "args" not in r and e.get("args"):
                # GPU op events carry e.g. the HLO long name / source metadata that maps a
                # fusion back to the code; CPU thunk events carry none.
                r["args"] = {str(k): str(v)[:300] for k, v in list(e["args"].items())[:8]}
            r["count"] += 1
            r["self_us"] += st
            r["total_us"] += e["dur"]
            self_total += st
    union = _union([[float(e["ts"]), float(e["ts"]) + float(e["dur"])] for e in ops])
    busy_union = sum(e - s for s, e in union)
    op_span = [union[0][0], union[-1][1]] if union else None
    if windows:
        wins = windows
        wsrc = f"TraceAnnotation '{annotation}' windows"
    elif op_span:
        wins = [tuple(op_span)]
        wsrc = "span of the op events (no annotation windows)"
    else:
        wins = []
        wsrc = "none"
    gaps, per_win = [], []
    for wi, (w0, w1) in enumerate(wins):
        segs = _clip(union, w0, w1)
        busy = sum(e - s for s, e in segs)
        cur = w0
        for s, e in segs:
            if s > cur:
                gaps.append({"window": wi, "start_offset_us": cur - w0, "duration_us": s - cur})
            cur = max(cur, e)
        if w1 > cur:
            gaps.append({"window": wi, "start_offset_us": cur - w0, "duration_us": w1 - cur,
                         "trailing": True})
        per_win.append({"window_us": w1 - w0, "busy_us": busy,
                        "dispatch_latency_us": (segs[0][0] - w0) if segs else None,
                        "tail_us": (w1 - segs[-1][1]) if segs else None})
    tot_w = sum(p["window_us"] for p in per_win)
    tot_b = sum(p["busy_us"] for p in per_win)

    def top(d, n):
        items = sorted(d.items(), key=lambda kv: -kv[1]["self_us"])[:n]
        return [dict({"rank": i + 1, "name": k, "count": v["count"], "self_s": v["self_us"] * 1e-6,
                      "share": (v["self_us"] / self_total) if self_total else None,
                      "mean_us": v["self_us"] / v["count"] if v["count"] else None},
                     **({"args_sample": v["args"]} if v.get("args") else {}))
                for i, (k, v) in enumerate(items)]
    cats, kinds = {}, {}
    for name, r in rows.items():
        c = category(name)
        cc = cats.setdefault(c, {"count": 0, "self_us": 0.0})
        cc["count"] += r["count"]
        cc["self_us"] += r["self_us"]
        kk = kinds.setdefault(kind(c), {"count": 0, "self_us": 0.0})
        kk["count"] += r["count"]
        kk["self_us"] += r["self_us"]
    top_ops = top(rows, top_n)
    for r in top_ops:
        r["category"] = category(r["name"])
        r["kind"] = kind(r["category"])
    top_cats = top(cats, top_n)
    for r in top_cats:
        r["kind"] = kind(r["name"])
    gl = [g["duration_us"] for g in gaps]
    return {
        "schema": SUMMARY_SCHEMA,
        "all_ops_self_s": {k: v["self_us"] * 1e-6 for k, v in rows.items()},
        "trace_file": os.path.abspath(path),
        "session_dir": os.path.dirname(os.path.abspath(path)),
        "mode": mode,
        "op_source": src,
        "n_events_total": len(ev),
        "n_op_events": len(ops),
        "n_op_threads": len(by_thread),
        "op_names": len(rows),
        "windows": {
            "source": wsrc, "n": len(wins), "total_s": tot_w * 1e-6, "busy_s": tot_b * 1e-6,
            "idle_s": (tot_w - tot_b) * 1e-6, "idle_fraction": ((tot_w - tot_b) / tot_w) if tot_w else None,
            "mean_window_s": (tot_w / len(wins) * 1e-6) if wins else None,
            "mean_busy_s": (tot_b / len(wins) * 1e-6) if wins else None,
            "dispatch_latency_mean_s": (sum(p["dispatch_latency_us"] for p in per_win
                                            if p["dispatch_latency_us"] is not None)
                                        / max(1, sum(p["dispatch_latency_us"] is not None for p in per_win))
                                        * 1e-6) if per_win else None,
            "tail_mean_s": (sum(p["tail_us"] for p in per_win if p["tail_us"] is not None)
                            / max(1, sum(p["tail_us"] is not None for p in per_win)) * 1e-6)
            if per_win else None,
        },
        "device_time": {
            "busy_union_s": busy_union * 1e-6,
            "op_self_total_s": self_total * 1e-6,
            "mean_concurrency": (self_total / busy_union) if busy_union else None,
            "op_span_s": ((op_span[1] - op_span[0]) * 1e-6) if op_span else None,
            "note": ("busy_union = union of op intervals (all executor threads on CPU); "
                     "op_self_total = sum of per-op self times (> busy_union when threads overlap)"),
        },
        "top_ops": top_ops,
        "top_categories": top_cats,
        "by_kind": {k: {"count": v["count"], "self_s": v["self_us"] * 1e-6,
                        "share": (v["self_us"] / self_total) if self_total else None}
                    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]["self_us"])},
        "gaps": {
            "count": len(gl), "gt_10us": sum(g > 10 for g in gl), "gt_100us": sum(g > 100 for g in gl),
            "gt_1ms": sum(g > 1000 for g in gl), "total_s": sum(gl) * 1e-6,
            "top": sorted(gaps, key=lambda g: -g["duration_us"])[:10],
        },
    }


def summarize_trace_dir(trace_dir, top_n=25, annotation=ANNOTATION):
    return summarize_trace_file(find_trace_file(trace_dir), top_n=top_n, annotation=annotation)


def summary_markdown(s, title=None):
    w, d = s["windows"], s["device_time"]
    lines = [f"# {title or 'Trace summary'}", "",
             f"Trace `{s['trace_file']}`; mode {s['mode']} ({s['op_source']}); {s['n_op_events']} op "
             f"events on {s['n_op_threads']} line(s), {s['op_names']} distinct op names.", "",
             f"* windows ({w['source']}): {w['n']}, total {_f(w['total_s'])} s, device busy "
             f"{_f(w['busy_s'])} s, idle {_f(w['idle_s'])} s (idle fraction {_f(w['idle_fraction'])}); "
             f"mean call {_f(w['mean_window_s'])} s, mean dispatch latency "
             f"{_f(w['dispatch_latency_mean_s'])} s, mean tail {_f(w['tail_mean_s'])} s",
             f"* device time: busy union {_f(d['busy_union_s'])} s, op self total "
             f"{_f(d['op_self_total_s'])} s, mean concurrency {_f(d['mean_concurrency'])}",
             f"* gaps: {s['gaps']['count']} (> 10 us: {s['gaps']['gt_10us']}, > 100 us: "
             f"{s['gaps']['gt_100us']}, > 1 ms: {s['gaps']['gt_1ms']}), total {_f(s['gaps']['total_s'])} s",
             "", "| rank | op | category | kind | count | self s | share | mean us | HLO shape (axis) | "
             "fused source lines (HLO) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["top_ops"]:
        srcs = ", ".join(f"{a} x{b}" for a, b in (r.get("hlo_sources") or []))
        shp = (r.get("hlo_shape") or "").split("{")[0]
        if r.get("hlo_axis"):
            shp += f" ({r['hlo_axis']})"
        lines.append(f"| {r['rank']} | `{r['name']}` | {r['category']} | {r['kind']} | {r['count']} | "
                     f"{_f(r['self_s'])} | {_f(r['share'])} | {_f(r['mean_us'])} | {shp} | {srcs} |")
    ha = s.get("hlo_annotation")
    if ha:
        lines += ["", f"Dominant-source attribution ({ha['note']}; {ha['top_ops_matched']}/{ha['top_ops']} "
                  f"top ops matched in `{os.path.basename(ha['hlo_file'])}`):", "",
                  "| file | self s | share |", "|---|---|---|"]
        for r in ha["by_dominant_file"]:
            lines.append(f"| {r['file']} | {_f(r['self_s'])} | {_f(r['share'])} |")
        if ha.get("by_max_lead_dim"):
            lines += ["", "Self time by the largest leading dimension among each op's result and "
                      "operands (heuristic; the axis the op works on):", "",
                      "| leading dim | self s | share |", "|---|---|---|"]
            for r in ha["by_max_lead_dim"]:
                lines.append(f"| {r['dim']} | {_f(r['self_s'])} | {_f(r['share'])} |")
    lines += ["", "| kind | count | self s | share |", "|---|---|---|---|"]
    for k, v in s["by_kind"].items():
        lines.append(f"| {k} | {v['count']} | {_f(v['self_s'])} | {_f(v['share'])} |")
    return "\n".join(lines) + "\n"


def _f(x):
    if x is None:
        return ""
    x = float(x)
    return f"{x:.4g}"


def write_summary(summary, json_path=None, md_path=None, title=None):
    if json_path:
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=1)
            f.write("\n")
    if md_path:
        with open(md_path, "w") as f:
            f.write(summary_markdown(summary, title))


def compact(summary, n=10):
    out = {k: summary[k] for k in ("mode", "op_source", "n_op_events", "windows", "device_time",
                                   "by_kind", "gaps")} | {"top_ops": summary["top_ops"][:n],
                                                          "trace_file": summary["trace_file"]}
    if summary.get("hlo_annotation"):
        ha = summary["hlo_annotation"]
        out["hlo_annotation"] = {k: ha.get(k) for k in ("hlo_file", "top_ops_matched", "top_ops",
                                                        "by_dominant_file", "by_max_lead_dim", "note")}
    return out


# ---------------------------------------------------------------------------
# optimized-HLO source map: trace op name -> the source lines it fuses
# ---------------------------------------------------------------------------
_H_INSTR = re.compile(r"^\s+(?:ROOT\s+)?%?([\w.\-]+)\s*=\s*(.*)$")
_H_CALLS = re.compile(r"\bcalls=%?([\w.\-]+)")
_H_META = re.compile(r"metadata=\{([^}]*)\}")
_H_OPN = re.compile(r'op_name="([^"]*)"')
_H_SF = re.compile(r'source_file="([^"]*)"')
_H_SL = re.compile(r"source_line=(\d+)")
_H_SHAPE = re.compile(r"^(\([^)]*\)|\S+)")
_H_ARR = re.compile(r"\b(?:pred|[suf]\d+|bf16|c64|c128)\[(\d*)")


def _short_source(path):
    i = path.rfind("darksirens/")
    return path[i:] if i >= 0 else os.path.basename(path)


def parse_hlo(text):
    """Optimized HLO text (``compiled.as_text()``) -> {instruction: {calls, meta, comp}}."""
    instrs, comp = {}, None
    comps = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line[0].isspace():
            if line.rstrip().endswith("{") and not line.startswith("HloModule"):
                head = line.split()[1] if line.startswith("ENTRY") else line.split()[0]
                comp = head.lstrip("%").split("(")[0]
                comps[comp] = []
            elif line.strip() == "}":
                comp = None
            continue
        m = _H_INSTR.match(line)
        if not m or comp is None:
            continue
        name, rest = m.group(1), m.group(2)
        meta = None
        mm = _H_META.search(rest)
        if mm:
            body = mm.group(1)
            on, sf, sl = _H_OPN.search(body), _H_SF.search(body), _H_SL.search(body)
            meta = (on.group(1) if on else None, _short_source(sf.group(1)) if sf else None,
                    int(sl.group(1)) if sl else None)
        calls = _H_CALLS.findall(rest)
        sm = _H_SHAPE.match(rest)
        head = rest.split("metadata=")[0]
        # leading dimensions of the result and operand arrays ("" = a scalar)
        leads = [int(x) for x in _H_ARR.findall(head) if x]
        instrs[name] = {"comp": comp, "calls": calls, "meta": meta,
                        "shape": sm.group(1) if sm else None,
                        "max_lead_dim": max(leads) if leads else None}
        comps[comp].append(name)
    return {"instrs": instrs, "comps": comps}


def op_sources(hmap, name, depth=3):
    """(match kind, Counter of 'file:line', Counter of op_name) over the instruction
    and every instruction of the computations it calls (fusions), recursively."""
    from collections import Counter

    instrs, comps = hmap["instrs"], hmap["comps"]
    match = "exact"
    if name not in instrs:
        base = name
        while True:
            b2 = re.sub(r"\.clone(\.\d+)?$", "", base)
            if b2 == base:
                break
            base = b2
        if base in instrs:
            name, match = base, "clone-stripped"
        else:
            return "none", Counter(), Counter()
    src, ops = Counter(), Counter()
    todo, seen = [(name, 0)], set()
    while todo:
        n, d = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        ins = instrs.get(n)
        if ins is None:
            continue
        if ins["meta"]:
            on, sf, sl = ins["meta"]
            if sf and sl is not None:
                src[f"{sf}:{sl}"] += 1
            if on:
                ops[on[-160:]] += 1
        if d < depth:
            for c in ins["calls"]:
                todo.extend((x, d + 1) for x in comps.get(c, ()))
    return match, src, ops


def dim_labels_from_dims(dims):
    """{leading dimension: label} from a record's ``dims`` (PE samples, events,
    injections, catalog rows); used to name the axis an op works on."""
    if not dims:
        return None
    lab = {}
    cat = dims.get("catalog") or {}
    for key, name in (("n_pe_samples", "PE samples"), ("n_events", "events"),
                      ("n_injections", "injections"), ("n_injections_padded", "injections"),
                      ("n_rows", "catalog rows")):
        v = dims.get(key, cat.get(key))
        if isinstance(v, int) and v > 1:
            lab.setdefault(v, [])
            if name not in lab[v]:
                lab[v].append(name)
    return {k: " / ".join(v) for k, v in lab.items()}


def _instr(hmap, name):
    ins = hmap["instrs"].get(name)
    if ins is None:
        ins = hmap["instrs"].get(re.sub(r"(\.clone(\.\d+)?)+$", "", name))
    return ins


def annotate_with_hlo(summary, hlo_path, n_sources=3, dim_labels=None):
    """Add the fused source lines / op names and the HLO result shape to each top op,
    a dominant-source time table (each op's self time goes to the file:line most of
    its instructions carry: a heuristic, labelled as such), and a table by the
    largest leading dimension among the op's result and operands (PE samples vs
    injections vs catalog rows when ``dim_labels`` names them; also a heuristic).
    Shared helpers (interpolation, population, logsumexp) carry the same source
    lines on the PE and the selection side; the shape tells the two apart."""
    with open(hlo_path) as f:
        hmap = parse_hlo(f.read())
    dim_labels = {int(k): v for k, v in (dim_labels or {}).items()}
    matched = 0
    for r in summary["top_ops"]:
        kind_, src, ops = op_sources(hmap, r["name"])
        r["hlo_match"] = kind_
        if kind_ != "none":
            matched += 1
            r["hlo_sources"] = src.most_common(n_sources)
            r["hlo_op_names"] = ops.most_common(n_sources)
            ins = _instr(hmap, r["name"])
            r["hlo_shape"] = ins.get("shape")
            r["hlo_max_lead_dim"] = ins.get("max_lead_dim")
            if ins.get("max_lead_dim") in dim_labels:
                r["hlo_axis"] = dim_labels[ins["max_lead_dim"]]
    by_dim = {}
    for name, self_s in summary.get("all_ops_self_s", {}).items():
        ins = _instr(hmap, name)
        d = None if ins is None else ins.get("max_lead_dim")
        key = ("unmatched" if ins is None else "scalar" if d is None
               else f"{d} ({dim_labels[d]})" if d in dim_labels else str(d))
        by_dim[key] = by_dim.get(key, 0.0) + self_s
    by_src, by_file, unmatched = {}, {}, 0.0
    for name, self_s in summary.get("all_ops_self_s", {}).items():
        kind_, src, _ops = op_sources(hmap, name)
        if kind_ == "none" or not src:
            unmatched += self_s
            continue
        top, _n = src.most_common(1)[0]
        by_src[top] = by_src.get(top, 0.0) + self_s
        f = top.rsplit(":", 1)[0]
        by_file[f] = by_file.get(f, 0.0) + self_s
    tot = sum(by_src.values()) + unmatched
    summary["hlo_annotation"] = {
        "hlo_file": os.path.abspath(hlo_path), "top_ops_matched": matched,
        "top_ops": len(summary["top_ops"]),
        "by_dominant_source": [{"source": k, "self_s": v, "share": v / tot if tot else None}
                               for k, v in sorted(by_src.items(), key=lambda kv: -kv[1])[:15]],
        "by_dominant_file": [{"file": k, "self_s": v, "share": v / tot if tot else None}
                             for k, v in sorted(by_file.items(), key=lambda kv: -kv[1])],
        "unmatched_self_s": unmatched,
        "by_max_lead_dim": [{"dim": k, "self_s": v, "share": v / tot if tot else None}
                            for k, v in sorted(by_dim.items(), key=lambda kv: -kv[1])[:12]],
        "dim_labels": {str(k): v for k, v in dim_labels.items()},
        "note": ("heuristic: each op's self time is assigned to the source line most of its "
                 "(fused) instructions carry in the optimized HLO metadata; by_max_lead_dim "
                 "assigns it to the largest leading dimension among the op's result and operand "
                 "arrays (the axis the op works on)"),
    }
    return summary


# ---------------------------------------------------------------------------
# bench_components.py --trace
# ---------------------------------------------------------------------------
def _sha(a):
    import numpy as np

    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _drop_xplane(summary):
    """Delete the session's *.xplane.pb (TensorBoard/XProf input, not needed by the
    parser or by Perfetto) after recording its size and sha256."""
    gone = []
    for p in glob.glob(os.path.join(summary["session_dir"], "*.xplane.pb")):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 22), b""):
                h.update(chunk)
        gone.append({"file": os.path.basename(p), "bytes": os.path.getsize(p), "sha256": h.hexdigest()})
        os.remove(p)
    return gone


def trace_components(trace_dir, names, calls, comps, comp_rec, whole_vals, n_coords, n_calls, jax,
                     top_n=25, title_prefix="", drop_xplane=False):
    """Re-run each component's warm calls inside jax.profiler.trace(trace_dir/<name>)."""
    import numpy as np

    import bench_common as bc

    trace_dir = os.path.abspath(trace_dir)
    os.makedirs(trace_dir, exist_ok=True)
    out = {"dir": trace_dir, "annotation": ANNOTATION, "n_calls": n_calls, "components": {},
           "numerics_unchanged": True,
           "note": ("a separate pass after the timed section: the record's timings are untraced; "
                    "each traced output is compared bit for bit with the untraced one")}
    for nm in names:
        if nm == "k_layout":
            continue
        d = os.path.join(trace_dir, nm)
        if os.path.isdir(d) and os.listdir(d):
            d = f"{d}_{int(time.time())}"
        os.makedirs(d, exist_ok=True)
        got = []
        t0 = time.perf_counter()
        jax.profiler.start_trace(d, create_perfetto_trace=True)
        try:
            for i in range(n_calls):
                k = i % n_coords
                with jax.profiler.TraceAnnotation(ANNOTATION):
                    v = calls[nm](k)
                    jax.block_until_ready(v)
                if nm == "i_whole":
                    got.append((k, bc.fhex(np.asarray(v))))
                elif nm != "j_transfer":
                    x = comps.extract(nm, v)
                    got.append((k, {q: _sha(a) for q, a in x.items()}))
                del v
        finally:
            jax.profiler.stop_trace()
        wall = time.perf_counter() - t0
        if nm == "i_whole":
            ok = all(h == whole_vals[k][0] for k, h in got)
        elif nm == "j_transfer":
            ok = None
        else:
            outs = comp_rec[nm]["outputs"]
            ok = all(dig[q] == outs[q]["per_coord"][k]["sha256"] for k, dig in got for q in dig)
        entry = {"dir": d, "numerics_unchanged": ok, "wall_s": wall}
        try:
            summ = summarize_trace_dir(d, top_n=top_n)
            write_summary(summ, os.path.join(d, "trace_summary.json"), os.path.join(d, "trace_summary.md"),
                          title=f"{title_prefix} {nm}".strip())
            entry["summary"] = compact(summ)
            entry["summary_json"] = os.path.join(d, "trace_summary.json")
            entry["parse_ok"] = True
            if drop_xplane:
                entry["xplane_removed"] = _drop_xplane(summ)
        except Exception as exc:
            entry["parse_ok"] = False
            entry["parse_error"] = f"{type(exc).__name__}: {exc}"
        out["components"][nm] = entry
        if ok is False:
            out["numerics_unchanged"] = False
    out["whole_bitwise_under_trace"] = (out["components"].get("i_whole") or {}).get("numerics_unchanged")
    out["all_parsed"] = all(e.get("parse_ok") for e in out["components"].values())
    return out


def annotate_trace_entry(entry, hlo_path, top_n=25, title=None, dim_labels=None):
    """Re-parse a trace_components entry and annotate it with the kernel's HLO."""
    summ = summarize_trace_dir(entry["dir"], top_n=top_n)
    annotate_with_hlo(summ, hlo_path, dim_labels=dim_labels)
    write_summary(summ, os.path.join(entry["dir"], "trace_summary.json"),
                  os.path.join(entry["dir"], "trace_summary.md"), title=title)
    entry["summary"] = compact(summ)
    return entry


# ---------------------------------------------------------------------------
# main harness with the timed loop traced
# ---------------------------------------------------------------------------
def run_main_traced(trace_dir, bench_args, top_n=25, hlo=None):
    import bench_common as bc
    import impl_core
    import impl_legacy

    trace_dir = os.path.abspath(trace_dir)
    if os.path.isdir(trace_dir) and os.listdir(trace_dir):
        print(f"--trace {trace_dir} is not empty", file=sys.stderr)
        return 2
    state = {"active": False, "started": None, "stopped": None, "n_annotated": 0}
    orig_mark = bc.PhaseClock.mark

    def mark(self, name):
        orig_mark(self, name)
        if name == "timed_loop_start":
            import jax

            os.makedirs(trace_dir, exist_ok=True)
            jax.profiler.start_trace(trace_dir, create_perfetto_trace=True)
            state["active"] = True
            state["started"] = bc.utc_now()
        elif name == "timed_loop_end" and state["active"]:
            import jax

            jax.profiler.stop_trace()
            state["active"] = False
            state["stopped"] = bc.utc_now()

    def wrap(cls):
        orig = cls.timed_call

        def timed_call(self, coord, _orig=orig):
            if not state["active"]:
                return _orig(self, coord)
            import jax

            with jax.profiler.TraceAnnotation(ANNOTATION):
                v = _orig(self, coord)
                jax.block_until_ready(v)
            state["n_annotated"] += 1
            return v
        cls.timed_call = timed_call

    bc.PhaseClock.mark = mark
    wrap(impl_core.CoreAdapter)
    wrap(impl_legacy.LegacyAdapter)
    import bench_fixed_theta as bft

    rc = bft.main(list(bench_args))
    out = None
    for i, x in enumerate(bench_args):
        if x == "--out" and i + 1 < len(bench_args):
            out = bench_args[i + 1]
    if out and os.path.isfile(out) and state["started"]:
        rec = bc.read_json(out)
        info = {"dir": trace_dir, "annotation": ANNOTATION, "annotated_calls": state["n_annotated"],
                "started_utc": state["started"], "stopped_utc": state["stopped"],
                "scope": "the timed loop only (first call, warm-ups and untimed passes not traced)"}
        try:
            summ = summarize_trace_dir(trace_dir, top_n=top_n)
            if hlo:
                annotate_with_hlo(summ, hlo, dim_labels=dim_labels_from_dims(rec.get("dims")))
            write_summary(summ, os.path.join(trace_dir, "trace_summary.json"),
                          os.path.join(trace_dir, "trace_summary.md"),
                          title=f"{rec.get('implementation')} {rec.get('plan', {}).get('name')} timed loop")
            info["summary"] = compact(summ)
            info["parse_ok"] = True
        except Exception as exc:
            info["parse_ok"] = False
            info["parse_error"] = f"{type(exc).__name__}: {exc}"
        rec["trace"] = info
        rec.setdefault("gaps", []).append(
            "timed loop ran under jax.profiler.trace (trace_tools.py main): warm timings include "
            "profiler overhead; take timings from an untraced record")
        bc.write_json(out, rec)
    return rc


# ---------------------------------------------------------------------------
# numerics check between a traced and an untraced record
# ---------------------------------------------------------------------------
_SCALAR = ("total_logL", "diag_total_logL", "log_mu", "n_eff", "selection_log_correction",
           "sigma2_lnL", "guard_threshold", "pe_variance_sum", "sum_event_log_evidence")
_ARRAY = ("event_log_evidence", "event_mc_variance")


def check_numerics(path_a, path_b):
    import bench_common as bc

    A, B = bc.read_json(path_a), bc.read_json(path_b)
    res = {"a": os.path.abspath(path_a), "b": os.path.abspath(path_b), "mismatches": [], "fields": []}
    if A.get("coords", {}).get("values_hex") != B.get("coords", {}).get("values_hex"):
        res["mismatches"].append("different coordinates")
    if str(A.get("schema", "")).startswith("darksirens-bench-fixed-theta"):
        pa, pb = A["values"]["per_coord"], B["values"]["per_coord"]
        res["fields"] = list(_SCALAR) + list(_ARRAY) + ["timed_values_hex", "masks"]
        for i, (x, y) in enumerate(zip(pa, pb)):
            for f in _SCALAR + _ARRAY:
                if x[f]["hex"] != y[f]["hex"]:
                    res["mismatches"].append(f"coord {i} {f}")
            if set(x["timed_values_hex"]) | set(y["timed_values_hex"]) != {x["total_logL"]["hex"]}:
                res["mismatches"].append(f"coord {i} timed values")
            if x["masks"] != y["masks"]:
                res["mismatches"].append(f"coord {i} masks")
        res["n_coords"] = len(pa)
    else:  # components records: every output digest
        ca, cb = A["components"], B["components"]
        for nm, e in ca.items():
            if not e.get("outputs") or not (cb.get(nm) or {}).get("outputs"):
                continue
            for q, v in e["outputs"].items():
                ha = [d["sha256"] for d in v["per_coord"]]
                hb = [d["sha256"] for d in cb[nm]["outputs"][q]["per_coord"]]
                res["fields"].append(f"{nm}.{q}")
                if ha != hb:
                    res["mismatches"].append(f"{nm}.{q}")
    res["bitwise"] = not res["mismatches"]
    return res


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "main":
        if "--" not in rest:
            print("usage: trace_tools.py main --trace DIR [--top N] -- <bench_fixed_theta args>", file=sys.stderr)
            return 2
        i = rest.index("--")
        ap = argparse.ArgumentParser(prog="trace_tools.py main")
        ap.add_argument("--trace", required=True)
        ap.add_argument("--top", type=int, default=25)
        ap.add_argument("--hlo", default=None, help="optimized HLO of the same whole kernel (e.g. "
                        "a components record's <out>.hlo/i_whole.hlo.txt) to annotate the table")
        x = ap.parse_args(rest[:i])
        return run_main_traced(x.trace, rest[i + 1:], top_n=x.top, hlo=x.hlo)
    if cmd == "parse":
        ap = argparse.ArgumentParser(prog="trace_tools.py parse")
        ap.add_argument("dir")
        ap.add_argument("--top", type=int, default=25)
        ap.add_argument("--annotation", default=ANNOTATION)
        ap.add_argument("--json", default=None)
        ap.add_argument("--md", default=None)
        ap.add_argument("--hlo", default=None, help="optimized HLO text of the traced module "
                        "(bench_components.py writes <out>.hlo/<component>.hlo.txt)")
        ap.add_argument("--record", default=None, help="a harness record of the traced run: its "
                        "dims name the axes (PE samples, injections, catalog rows) with --hlo")
        x = ap.parse_args(rest)
        s = summarize_trace_dir(x.dir, top_n=x.top, annotation=x.annotation)
        if x.hlo:
            labels = None
            if x.record:
                with open(x.record) as f:
                    labels = dim_labels_from_dims(json.load(f).get("dims"))
            annotate_with_hlo(s, x.hlo, dim_labels=labels)
        write_summary(s, x.json, x.md)
        print(summary_markdown(s))
        return 0
    if cmd == "check-numerics":
        ap = argparse.ArgumentParser(prog="trace_tools.py check-numerics")
        ap.add_argument("a")
        ap.add_argument("b")
        ap.add_argument("--out", default=None)
        x = ap.parse_args(rest)
        r = check_numerics(x.a, x.b)
        if x.out:
            with open(x.out, "w") as f:
                json.dump(r, f, indent=1)
        print(json.dumps({k: r[k] for k in ("bitwise", "mismatches")}, indent=1))
        return 0 if r["bitwise"] else 1
    print(f"unknown command {cmd!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
