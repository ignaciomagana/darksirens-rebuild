#!/usr/bin/env python3
"""One CSV row per Gate 1 record, from campaign_run.py's index, records and summaries.

    python gate1_table.py --outdir OUT [--outdir OUT2 ...] --csv gate1_matrix.csv [--json rows.json]

parity_vs_legacy (from the FIRST comparison of the record, whose A is the legacy
reference of the same input/plan/blocks label; for core_pin the legacy default):
pass | fail | mcvar-noise | n.a. | refused. mcvar-noise is used only under rule D-mcvar:
the one failing field is event_mc_variance, masks/guards equal, and its max_rel is
within MCVAR_FLOOR (the Gate 0 own-GPU-vs-own-CPU floor of that field). A failure whose
only failing field is event_mc_variance but above the floor is 'fail' and listed as
mcvar_only in the JSON rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import os

MCVAR_FLOOR = 1.05e-13
MIB = 1024.0 * 1024.0
COLUMNS = ["record_id", "matrix", "impl", "package_sha", "jit", "blocks", "sel_batch_size",
           "pe_event_block", "plan", "pe_label", "sel_label", "n_events", "nsamp", "n_injections",
           "ndraw", "cache_mode", "t_load_s", "t_build_s", "t_first_call_s", "compile_requests_first",
           "compiles_first", "warm_median_s", "warm_min_s", "warm_mean_s", "warm_std_s",
           "compiles_in_loop", "peak_vram_mib", "gpu_util_pct", "host_rss_mib", "transfer_sync_s",
           "repeat_consistent", "parity_vs_legacy", "parity_ref", "max_rel_vs_legacy", "worst_field",
           "bitwise_vs_legacy", "status", "wall_s"]


def _get(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d


def parity_of(summary_path):
    if not summary_path or not os.path.isfile(summary_path):
        return None
    with open(summary_path) as f:
        s = json.load(f)
    if s.get("status") != "compared":
        return {"parity": "refused", "reasons": s.get("refusal_reasons")}
    fields = s["fields"]
    failing = [k for k, v in fields.items() if not v["pass"]]
    mrel = {k: v["max_rel"] for k, v in fields.items() if k != "decoded_full_parameter_vector"}
    worst = max(mrel, key=lambda k: mrel[k])
    v = s["verdict"]
    masks = v["masks_equal"]
    if v["overall_pass"]:
        par = "pass"
    elif failing == ["event_mc_variance"] and masks and v["repeat_consistent_both"] and \
            fields["event_mc_variance"]["max_rel"] <= MCVAR_FLOOR:
        par = "mcvar-noise"
    else:
        par = "fail"
    return {"parity": par, "failing_fields": failing, "masks_equal": masks,
            "repeat_consistent_both": v["repeat_consistent_both"], "max_rel": mrel[worst],
            "worst_field": worst if mrel[worst] > 0 else "", "bitwise": v["bitwise_all_fields"],
            "mcvar_only": failing == ["event_mc_variance"],
            "fails": {k: {"max_rel": fields[k]["max_rel"], "max_abs": fields[k]["max_abs"],
                          "n_fail": fields[k].get("n_fail"),
                          "max_rel_per_coord": fields[k].get("max_rel_per_coord")} for k in failing}}


def row_for(entry):
    sp = entry["spec"]
    rec = None
    if entry.get("record") and os.path.isfile(entry["record"]):
        with open(entry["record"]) as f:
            rec = json.load(f)
    r = {c: "" for c in COLUMNS}
    r.update(record_id=entry["record_id"], matrix=sp.get("matrix"), impl=sp["env"], jit=sp["jit"],
             blocks=sp["blocks"], plan=sp["plan"], pe_label=sp["pe_label"], sel_label=sp["sel_label"],
             status=entry["status"], wall_s=round(entry.get("wall_s", 0.0), 2),
             cache_mode=("warm" if (sp.get("flags") or {}).get("warm_cache") else entry.get("cache_mode")),
             sel_batch_size=sp["sel_batch"], pe_event_block=sp["pe_block"])
    extra = {"record_id": entry["record_id"], "spec": sp, "status": entry["status"]}
    if rec is not None and rec.get("status") == "ok":
        pkg = rec.get("package") or {}
        t = rec["timing"]
        cfg = rec["config"]
        dims = rec["dims"]
        uw = t.get("util_window") or {}
        util = _get(uw, "smi", "util_pct_mean")
        if util is None and (t.get("gpu_util_timed_loop") or {}).get("rows", 0) >= 3:
            util = t["gpu_util_timed_loop"].get("util_pct_mean")
        r.update(
            package_sha=(pkg.get("known_digest_match") or {}).get("sha") or pkg.get("git_sha"),
            sel_batch_size=f"{cfg['sel_batch_size']['requested']}->{cfg['sel_batch_size']['resolved']}",
            pe_event_block=f"{cfg['pe_event_block']['requested']}->{cfg['pe_event_block']['resolved']}",
            n_events=dims.get("n_events"), nsamp=dims.get("nsamp"), n_injections=dims.get("n_injections"),
            ndraw=dims.get("ndraw"), t_load_s=t.get("t_load_s"), t_build_s=t.get("t_build_s"),
            t_first_call_s=t.get("t_first_call_s"),
            compile_requests_first=t["compile"]["first_call"]["requests"],
            compiles_first=t["compile"]["first_call"]["compiles"],
            warm_median_s=t["warm"]["median_s"], warm_min_s=t["warm"]["min_s"],
            warm_mean_s=t["warm"]["mean_s"], warm_std_s=t["warm"]["std_s"],
            compiles_in_loop=t["compile"]["timed_loop"]["requests"],
            peak_vram_mib=(None if t.get("peak_device_bytes") is None else round(t["peak_device_bytes"] / MIB, 1)),
            gpu_util_pct=(None if util is None else round(util, 1)),
            host_rss_mib=round(t["peak_host_rss_bytes"] / MIB, 1),
            transfer_sync_s=t.get("t_transfer_sync_s"),
            repeat_consistent=bool(rec["repeat_consistency"]["bitwise"]
                                   and rec["repeat_consistency"]["timed_loop_bitwise_consistent"]))
        extra.update(block_size_resolution=cfg.get("block_size_resolution"), xla_cache=rec.get("xla_cache"),
                     gaps=rec.get("gaps"), util_window=uw.get("smi"),
                     peak_device_bytes_all_phases=t.get("peak_device_bytes_all_phases"),
                     n_finite=sum(1 for pc in rec["values"]["per_coord"] if pc["total_finite"]),
                     t_load_s=t.get("t_load_s"), t_build_breakdown=t.get("t_build_breakdown"),
                     first_total_logL=rec["values"]["per_coord"][0]["total_logL"]["value"])
    comps = entry.get("compares") or {}
    if comps:
        ref, c = next(iter(comps.items()))
        p = parity_of(c.get("summary"))
        r["parity_ref"] = ref
        if p is None:
            r["parity_vs_legacy"] = "n.a."
        else:
            r["parity_vs_legacy"] = p["parity"]
            if p["parity"] != "refused":
                r.update(max_rel_vs_legacy=p["max_rel"], worst_field=p["worst_field"],
                         bitwise_vs_legacy=p["bitwise"])
        extra["compares"] = {k: parity_of(v.get("summary")) for k, v in comps.items()}
    else:
        r["parity_vs_legacy"] = "n.a."
    return r, extra


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", action="append", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--order", default=None, help="spec JSON giving the row order")
    a = ap.parse_args(argv)
    entries = {}
    for d in a.outdir:
        with open(os.path.join(d, "index.json")) as f:
            entries.update(json.load(f)["runs"])
    ids = list(entries)
    if a.order:
        with open(a.order) as f:
            order = [s["record_id"] for s in json.load(f)]
        ids = [i for i in order if i in entries] + [i for i in ids if i not in order]
    rows, extras = [], []
    for i in ids:
        r, e = row_for(entries[i])
        rows.append(r)
        extras.append(e)
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"rows": rows, "extra": extras}, f, indent=1, default=str)
    print(f"{len(rows)} rows -> {a.csv}")


if __name__ == "__main__":
    main()
