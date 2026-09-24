#!/usr/bin/env python3
"""Gate 3b memory-retry table: one CSV row per record of a campaign_run.py outdir.

    python gate3b_table.py --outdir OUT --csv g3b_matrix.csv [--json rows.json] [--order SPEC]

Columns: record, impl (env/jit), fixture, plan, row_chunk, blocks, mem_fraction (the
EFFECTIVE allocator fraction and whether it is the default), status, fail_stage,
failed_alloc_bytes (parsed from the RESOURCE_EXHAUSTED message), device_in_use_at_failure,
largest_free_block_at_failure (memory_stats), peak_device_bytes (memory_stats
peak_bytes_in_use at the end of the timed loop, or at failure), smi_peak_mib (1 Hz
nvidia-smi over the gpu_run.sh lock window), t_first_call_s, warm20_median_s (first 20
timed calls), steady_median_s + steady_window (last N timed calls), warm_median_s (all
timed calls), n_calls, finite_total_count, parity_vs / parity_pass / max_rel / worst_field
(every compare_records summary in OUT/summaries naming this record, A or B), gpu_wall_s.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re

COLUMNS = ["record", "impl", "fixture", "plan", "row_chunk", "blocks", "mem_fraction",
           "allocator", "status", "fail_stage", "failed_alloc_bytes", "device_in_use_at_failure",
           "largest_free_block_at_failure", "peak_device_bytes", "peak_device_mib",
           "smi_peak_mib", "t_first_call_s", "warm20_median_s", "steady_median_s",
           "steady_window", "warm_median_s", "n_calls", "finite_total_count", "parity_vs",
           "parity_pass", "max_rel", "worst_field", "gpu_wall_s"]
ALLOC_RE = re.compile(r"allocate\s+([\d,]+)\s+bytes")


def _load(p):
    if not p or not os.path.isfile(p):
        return None
    with open(p) as f:
        return json.load(f)


def smi_peak_and_wall(path):
    """(peak memory.used MiB, lock window seconds) of a gpu_run.sh smi log."""
    import datetime as dt

    peak, t0, t1 = None, None, None
    if not path or not os.path.isfile(path):
        return None, None
    with open(path, errors="replace") as f:
        for line in f:
            if line.startswith("# lock_acquired_utc="):
                t0 = line.split("=", 1)[1].split()[0]
            elif line.startswith("# released_utc="):
                t1 = line.split("=", 1)[1].split()[0]
            elif not line.startswith(("#", "timestamp")):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2 and parts[1].endswith("MiB"):
                    try:
                        v = int(parts[1].split()[0])
                    except ValueError:
                        continue
                    peak = v if peak is None else max(peak, v)
    wall = None
    if t0 and t1:
        f = "%Y-%m-%dT%H:%M:%S.%fZ"
        wall = (dt.datetime.strptime(t1, f) - dt.datetime.strptime(t0, f)).total_seconds()
    return peak, wall


def parity_for(rid, sdir):
    out = []
    for p in sorted(glob.glob(os.path.join(sdir, "*.json"))):
        name = os.path.basename(p)[:-5]
        if not (name == rid or name.startswith(rid + "__vs__") or name.endswith("__vs__" + rid)):
            continue
        s = _load(p)
        if not s or "verdict" not in s:
            continue
        if name.startswith(rid + "__vs__"):
            other = name[len(rid + "__vs__"):]
        elif name.endswith("__vs__" + rid):
            other = name[:-len("__vs__" + rid)]
        else:  # campaign_run's first compare: <rid>.json, A = the reference
            A = s.get("A") or {}
            other = A.get("label") if isinstance(A, dict) else str(A)
        mr = {**(s.get("max_rel_by_field") or {}), **{f"catalog.{k}" if not k.startswith("catalog") else k: v
                                                      for k, v in (s.get("catalog_max_rel_by_field") or {}).items()}}
        mr = {k: v for k, v in mr.items() if isinstance(v, (int, float))}
        worst = max(mr, key=mr.get) if mr else None
        out.append({"vs": other, "pass": s["verdict"].get("overall_pass"),
                    "status": s.get("status"), "max_rel": mr.get(worst) if worst else None,
                    "worst": worst, "summary": p})
    return out


def row_for(e, outdir):
    sp = e["spec"]
    rec = _load(e.get("record"))
    rid = e["record_id"]
    extra = sp.get("extra_args") or []
    rc = extra[extra.index("--row-chunk") + 1] if "--row-chunk" in extra else (
        "auto" if sp["impl"] == "legacy" else "core fixed auto (512 above 2^25)")
    mf_req = float(extra[extra.index("--mem-fraction") + 1]) if "--mem-fraction" in extra else None
    r = {"record": rid, "impl": f"{sp['env']}_{sp['jit']}", "fixture": sp.get("fixture"),
         "plan": sp["plan"], "row_chunk": rc, "blocks": f"{sp['sel_batch']}/{sp['pe_block']}",
         "mem_fraction": mf_req if mf_req is not None else 0.75,
         "allocator": "non-default" if mf_req is not None else "default", "status": e["status"],
         "n_calls": sp.get("n_calls")}
    smi_peak, wall = smi_peak_and_wall(e.get("smi"))
    r["smi_peak_mib"], r["gpu_wall_s"] = smi_peak, wall
    if rec is None:
        err = ""
        try:
            with open(e.get("stderr"), errors="replace") as f:
                err = f.read()
        except (OSError, TypeError):
            pass
        m = ALLOC_RE.search(err)
        r["failed_alloc_bytes"] = int(m.group(1).replace(",", "")) if m else None
        r["fail_stage"] = "no record (see stderr)"
        return r
    mk = (rec.get("config") or {}).get("memory_knobs") or {}
    mfr = mk.get("mem_fraction") or ((rec.get("memory_knobs_requested") or {}).get("mem_fraction"))
    if mfr:
        r["mem_fraction"] = mfr.get("effective")
        r["allocator"] = mfr.get("allocator")
    if mk.get("row_chunk") and sp["impl"] == "legacy":
        r["row_chunk"] = f"{mk['row_chunk'].get('legacy_cli_value')} (effective " \
                         f"{mk['row_chunk'].get('effective_for_catalog')})"
    fail = rec.get("failure") or rec.get("build_error")
    if fail:
        r["fail_stage"] = fail.get("stage") or ("build" if rec.get("build_error") else None)
        m = ALLOC_RE.search(fail.get("message") or "")
        r["failed_alloc_bytes"] = int(m.group(1).replace(",", "")) if m else None
        maf = fail.get("memory_at_failure") or {}
        r["device_in_use_at_failure"] = maf.get("device_bytes_in_use")
        r["peak_device_bytes"] = maf.get("device_peak_bytes_in_use")
        ms = maf.get("device_memory_stats") or {}
        r["largest_free_block_at_failure"] = ms.get("largest_free_block_bytes")
    t = rec.get("timing") or {}
    if t:
        r["t_first_call_s"] = t.get("t_first_call_s")
        w = t.get("warm") or {}
        r["warm_median_s"] = w.get("median_s")
        r["warm20_median_s"] = (w.get("first20") or {}).get("median_s") if w.get("first20") else (
            w.get("median_s") if w.get("n") == 20 else None)
        st = w.get("steady")
        if st:
            r["steady_median_s"], r["steady_window"] = st.get("median_s"), st.get("window")
        if t.get("peak_device_bytes") is not None:
            r["peak_device_bytes"] = t.get("peak_device_bytes")
        r["n_calls"] = (rec.get("config") or {}).get("n_calls", r["n_calls"])
    if r.get("peak_device_bytes"):
        r["peak_device_mib"] = round(r["peak_device_bytes"] / 2**20, 1)
    if rec.get("values"):
        pcs = rec["values"]["per_coord"]
        r["finite_total_count"] = sum(1 for pc in pcs if pc["total_finite"])
    par = parity_for(rid, os.path.join(outdir, "summaries"))
    if par:
        r["parity_vs"] = ";".join(p["vs"] for p in par)
        r["parity_pass"] = ";".join(str(p["pass"]) for p in par)
        r["max_rel"] = ";".join(repr(p["max_rel"]) for p in par)
        r["worst_field"] = ";".join(str(p["worst"]) for p in par)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--order", default=None)
    a = ap.parse_args(argv)
    entries = _load(os.path.join(a.outdir, "index.json"))["runs"]
    ids = list(entries)
    if a.order:
        order = [s["record_id"] for s in _load(a.order)]
        ids = [i for i in order if i in entries] + [i for i in ids if i not in order]
    rows = [row_for(entries[i], a.outdir) for i in ids]
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"columns": COLUMNS, "rows": rows}, f, indent=1, default=str)
    print(f"{len(rows)} rows -> {a.csv}")


if __name__ == "__main__":
    main()
