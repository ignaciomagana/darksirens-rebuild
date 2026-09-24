#!/usr/bin/env python3
"""Gate 4 (candidate O1) tables: the kernel matrix CSV and the end-to-end CSV.

    python gate4_table.py --outdir OUT --csv gate4_matrix.csv [--json rows.json]
        [--e2e-dir OUT/e2e --e2e-csv e2e_table.csv]

Kernel CSV: the Gate 1 columns (gate1_table.COLUMNS; parity_vs_legacy etc. from the FIRST
comparison of the record, whose A is the legacy reference of the cell) plus
arm (main | o1), cell, fixture, n_calls, warm20_median_s (first 20 timed calls),
steady30_median_s (last 30), parity_vs_main_whole / max_rel_vs_main_whole / worst_field_vs_main_whole
(second comparison, O1 records only), bitwise_total_vs_legacy / bitwise_total_vs_main_whole
(total_logL bitwise at every coordinate, non-finite pattern included), n_finite_total,
kernel_vs_diag_total_bitwise (the record's kernel total against its own diagnostics total),
smi_peak_mib and gpu_wall_s (gpu_run.sh lock window), fail_stage / failed_alloc_bytes /
device_in_use_at_failure for failed records.

E2E CSV: one row per infer_ladder.py record (record.json) under --e2e-dir: impl, arm,
sampler, status, t_total_s and the phases (load, build, first call, sampler construct,
first progress, main loop, sampling, post), n_like_evals, evals/s (sampling and steady),
logZ, logZ_hex, logZerr, iterations, compile requests/compiles by phase, peak device and
host memory, posterior sha256.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re

import gate1_table as g1
import gate3b_table as g3b

ALLOC_RE = re.compile(r"allocate\s+([\d,]+)\s+bytes")
COLUMNS = (["record_id", "arm", "cell", "fixture"] + [c for c in g1.COLUMNS if c != "record_id"]
           + ["n_calls", "warm20_median_s", "steady30_median_s", "parity_vs_main_whole",
              "max_rel_vs_main_whole", "worst_field_vs_main_whole", "bitwise_total_vs_legacy",
              "bitwise_total_vs_main_whole", "n_finite_total", "kernel_vs_diag_total_bitwise",
              "smi_peak_mib", "gpu_wall_s", "fail_stage", "failed_alloc_bytes",
              "device_in_use_at_failure"])


def _load(p):
    if not p or not os.path.isfile(p):
        return None
    with open(p) as f:
        return json.load(f)


def total_bitwise(summary_path):
    s = _load(summary_path)
    if not s or s.get("status") != "compared":
        return None
    f = (s.get("fields") or {}).get("total_logL") or {}
    return bool(f.get("bitwise")) and not f.get("n_nonfinite_mismatch")


def kernel_row(entry):
    r, extra = g1.row_for(entry)
    sp = entry["spec"]
    fl = sp.get("flags") or {}
    r.update(arm=fl.get("gate4_arm"), cell=fl.get("gate4_cell"), fixture=sp.get("fixture"),
             n_calls=sp.get("n_calls"))
    rec = _load(entry.get("record"))
    r["smi_peak_mib"], r["gpu_wall_s"] = g3b.smi_peak_and_wall(entry.get("smi"))
    if rec and rec.get("status") == "ok":
        w = rec["timing"]["warm"]
        r["warm20_median_s"] = (w.get("first20") or {}).get("median_s")
        r["steady30_median_s"] = (w.get("steady") or {}).get("median_s")
        r["n_calls"] = w.get("n")
        r["n_finite_total"] = sum(1 for pc in rec["values"]["per_coord"] if pc["total_finite"])
    elif rec is not None or entry["status"] != "ok":
        fail = (rec or {}).get("failure") or (rec or {}).get("build_error") or {}
        msg = fail.get("message") or ""
        if not msg:
            try:
                with open(entry.get("stderr"), errors="replace") as f:
                    msg = f.read()
            except (OSError, TypeError):
                pass
        m = ALLOC_RE.search(msg)
        r["failed_alloc_bytes"] = int(m.group(1).replace(",", "")) if m else None
        r["fail_stage"] = fail.get("stage") or ("build" if (rec or {}).get("build_error") else
                                                "no record (see stderr)")
        maf = fail.get("memory_at_failure") or {}
        r["device_in_use_at_failure"] = maf.get("device_bytes_in_use")
        if maf.get("device_peak_bytes_in_use"):
            r["peak_vram_mib"] = round(maf["device_peak_bytes_in_use"] / g1.MIB, 1)
    comps = list((entry.get("compares") or {}).items())
    if comps:
        s0 = comps[0][1].get("summary")
        r["bitwise_total_vs_legacy"] = total_bitwise(s0)
        s = _load(s0)
        if s and isinstance(s.get("kernel_vs_diag_total"), dict):
            r["kernel_vs_diag_total_bitwise"] = s["kernel_vs_diag_total"].get("B_all_bitwise")
    if len(comps) > 1:
        ref, c = comps[1]
        p = g1.parity_of(c.get("summary"))
        if p is not None:
            r["parity_vs_main_whole"] = p["parity"]
            if p["parity"] != "refused":
                r["max_rel_vs_main_whole"] = p["max_rel"]
                r["worst_field_vs_main_whole"] = p["worst_field"]
            r["bitwise_total_vs_main_whole"] = total_bitwise(c.get("summary"))
        else:
            r["parity_vs_main_whole"] = "n.a."
    return r, extra


E2E_COLUMNS = ["name", "impl", "arm", "sampler", "status", "package_git_sha", "t_total_s", "t_load_s",
               "t_build_s", "t_first_call_s", "t_sampler_constructed_s", "t_first_progress_s",
               "t_main_loop_s", "t_sampling_s", "t_post_s", "n_like_evals", "evals_per_s_sampling",
               "evals_per_s_steady", "iterations", "logZ", "logZ_hex", "logZerr", "n_samples",
               "compile_requests_first_call", "compile_requests_sampling", "compiles_sampling",
               "compile_s_sampling", "eager_calls_sampling", "traced_calls_sampling",
               "peak_device_bytes", "peak_host_rss_bytes", "posterior_sha256", "gpu_wall_s",
               "smi_peak_mib"]


def e2e_row(d):
    rec = _load(os.path.join(d, "record.json"))
    name = os.path.basename(d.rstrip("/"))
    r = {"name": name}
    if rec is None:
        r["status"] = "no record"
        return r
    t = rec.get("timing") or {}
    ev = t.get("sampling_events_s") or {}
    lc = rec.get("likelihood_calls") or {}
    res = rec.get("result") or {}
    cp = rec.get("compile") or {}
    mon = ((rec.get("memory") or {}).get("monitor") or {})
    bpk = lc.get("by_phase_kind") or {}
    arm = name.split("_")[1] if name.startswith("G4E_") else None
    r.update(impl=rec.get("implementation"), arm=arm, sampler=(rec.get("settings") or {}).get(
        "requested", {}).get("sampler"), status=rec.get("status"),
        package_git_sha=(rec.get("package") or {}).get("git_sha"),
        t_total_s=t.get("t_total_s"), t_load_s=t.get("t_load_s"), t_build_s=t.get("t_build_s"),
        t_first_call_s=t.get("t_first_call_s"), t_sampler_constructed_s=ev.get("sampler_constructed"),
        t_first_progress_s=ev.get("first_progress"), t_main_loop_s=t.get("t_main_loop_s"),
        t_sampling_s=t.get("t_sampling_s"), t_post_s=t.get("t_post_s"),
        n_like_evals=lc.get("n_like_evals"), evals_per_s_sampling=lc.get("evals_per_s_sampling"),
        evals_per_s_steady=lc.get("evals_per_s_steady"),
        iterations=(rec.get("progress") or {}).get("last_main_iteration"),
        logZ=res.get("logZ"), logZ_hex=res.get("logZ_hex"), logZerr=res.get("logZerr"),
        n_samples=res.get("n_samples"),
        compile_requests_first_call=(cp.get("first_call") or {}).get("requests"),
        compile_requests_sampling=(cp.get("sampling") or {}).get("requests"),
        compiles_sampling=(cp.get("sampling") or {}).get("compiles"),
        compile_s_sampling=(cp.get("sampling") or {}).get("compile_seconds"),
        eager_calls_sampling=sum(v for k, v in bpk.items() if k.endswith(":eager") and not k.startswith(("first_call", "build", "init"))),
        traced_calls_sampling=sum(v for k, v in bpk.items() if k.endswith(":traced")),
        peak_device_bytes=mon.get("device_peak_bytes_in_use"),
        peak_host_rss_bytes=(rec.get("memory") or {}).get("peak_host_rss_bytes"),
        posterior_sha256=res.get("posterior_sha256"))
    smi = d.rstrip("/") + ".smi.csv"
    r["smi_peak_mib"], r["gpu_wall_s"] = g3b.smi_peak_and_wall(smi)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--e2e-dir", default=None)
    ap.add_argument("--e2e-csv", default=None)
    a = ap.parse_args(argv)
    idx = _load(os.path.join(a.outdir, "index.json"))["runs"]
    order = _load(os.path.join(a.outdir, "specs", "g4.json")) or []
    ids = [s["record_id"] for s in order if s["record_id"] in idx] + [i for i in idx if i not in
                                                                         {s["record_id"] for s in order}]
    rows, extras = [], []
    for i in ids:
        r, x = kernel_row(idx[i])
        rows.append(r)
        extras.append(x)
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"columns": COLUMNS, "rows": rows, "extra": extras}, f, indent=1, default=str)
    print(f"{len(rows)} kernel rows -> {a.csv}")
    if a.e2e_dir and a.e2e_csv:
        dirs = sorted(d for d in glob.glob(os.path.join(a.e2e_dir, "G4E_*")) if os.path.isdir(d))
        erows = [e2e_row(d) for d in dirs]
        with open(a.e2e_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=E2E_COLUMNS, extrasaction="ignore")
            w.writeheader()
            w.writerows(erows)
        print(f"{len(erows)} e2e rows -> {a.e2e_csv}")


if __name__ == "__main__":
    main()
