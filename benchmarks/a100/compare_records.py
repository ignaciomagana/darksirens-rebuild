#!/usr/bin/env python3
"""Compare two fixed-coordinate benchmark records field by field.

    python compare_records.py A.json B.json --rtol 1e-12 --atol 0 --out summary.json [--md summary.md]

A is the reference of the relative differences: rel = |A - B| / |A|.
Pass criterion per element (the probes' policy, e.g. core
``tools/compare_spectral_probe.py:50-67``): ``|A - B| <= atol + rtol * |A|``,
NaN equals NaN, and +/-inf must match exactly.

Refuses (exit 2, summary ``status: refused``) when the two records do not
describe the same experiment: different schema, plan, coordinates (names or
bit patterns), input files (sha256), physical dims, selection-guard mode or
``max_likelihood_variance``, or a record whose own plan assertions failed.
Block sizes may differ (that is how the batched paths are checked against the
single pass); both sides' values are in the summary. Exit 1 when the comparison ran but parity (at the given
tolerances), mask equality or repeat consistency failed; 0 otherwise.
"""

from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_common as bc  # noqa: E402

SCALAR_FIELDS = (
    "total_logL",
    "diag_total_logL",
    "log_mu",
    "n_eff",
    "selection_log_correction",
    "sum_event_log_evidence",
    "pe_variance_sum",
    "sigma2_lnL",
    "guard_threshold",
)
ARRAY_FIELDS = ("event_log_evidence", "event_mc_variance")
MASK_KEYS = ("pe_structural", "pe_support", "pe_final", "sel_structural", "sel_support",
             "sel_final")
DIM_KEYS = ("n_events", "nsamp", "n_pe_samples", "n_injections", "ndraw")
LIKELIHOOD_SETTINGS = ("max_likelihood_variance", "selection_neff_soft_guard")


def _hexes(rec, field):
    out = []
    for pc in rec["values"]["per_coord"]:
        e = pc[field]
        out.extend(e["hex"] if isinstance(e["hex"], list) else [e["hex"]])
    return out


def _per_coord_hexes(rec, field):
    res = []
    for pc in rec["values"]["per_coord"]:
        e = pc[field]
        res.append(e["hex"] if isinstance(e["hex"], list) else [e["hex"]])
    return res


def compare_values(ha, hb, rtol, atol):
    a = np.asarray([float.fromhex(h) for h in ha], dtype=np.float64)
    b = np.asarray([float.fromhex(h) for h in hb], dtype=np.float64)
    if a.shape != b.shape:
        return {"error": f"shape {a.shape} vs {b.shape}", "pass": False, "bitwise": False}
    bitwise_mask = np.asarray([x == y for x, y in zip(ha, hb)], dtype=bool)
    both_nan = np.isnan(a) & np.isnan(b)
    both_fin = np.isfinite(a) & np.isfinite(b)
    same_inf = np.isinf(a) & np.isinf(b) & (np.sign(a) == np.sign(b))
    nonfinite_mismatch = ~(both_fin | both_nan | same_inf)
    with np.errstate(invalid="ignore", divide="ignore"):
        d = np.where(both_fin, np.abs(a - b), 0.0)
        rel = np.where(both_fin & (a != 0), d / np.abs(a),
                       np.where(both_fin & (a == 0) & (b != 0), np.inf, 0.0))
    ok = both_nan | same_inf | (a == b) | (both_fin & (d <= atol + rtol * np.abs(a)))
    ok &= ~nonfinite_mismatch
    return {
        "n": int(a.size),
        "n_finite_both": int(both_fin.sum()),
        "n_nonfinite_matched": int((both_nan | same_inf).sum()),
        "n_nonfinite_mismatch": int(nonfinite_mismatch.sum()),
        "bitwise": bool(bitwise_mask.all()),
        "n_bit_different": int((~bitwise_mask).sum()),
        "max_abs": float(d.max()) if d.size else 0.0,
        "max_rel": float(rel.max()) if rel.size else 0.0,
        "pass": bool(ok.all()),
        "n_fail": int((~ok).sum()),
    }


def refusal_reasons(A, B):
    r = []
    if A.get("schema") != B.get("schema"):
        r.append(f"schema {A.get('schema')} vs {B.get('schema')}")
    for rec, tag in ((A, "A"), (B, "B")):
        if rec.get("status") != "ok":
            r.append(f"record {tag} status={rec.get('status')} (plan assertions failed or run incomplete)")
    if r:
        return r
    pa, pb = A["plan"], B["plan"]
    for k in ("name", "population_model", "sampled", "full_order"):
        if pa.get(k) != pb.get(k):
            r.append(f"plan.{k}: {pa.get(k)} vs {pb.get(k)}")
    fa = {k: bc.fhex(v) for k, v in pa["fixed"].items()}
    fb = {k: bc.fhex(v) for k, v in pb["fixed"].items()}
    if fa != fb:
        r.append("plan.fixed values differ")
    ca, cb = A["coords"], B["coords"]
    if ca["names"] != cb["names"]:
        r.append(f"coordinate names differ: {ca['names']} vs {cb['names']}")
    if ca["values_hex"] != cb["values_hex"]:
        r.append("coordinate values differ (bit patterns)")
    for side in ("pe", "sel"):
        if A["inputs"][side]["sha256"] != B["inputs"][side]["sha256"]:
            r.append(f"input {side} sha256 differs: {A['inputs'][side]['sha256']} vs "
                     f"{B['inputs'][side]['sha256']}")
    for k in DIM_KEYS:
        if A["dims"].get(k) != B["dims"].get(k):
            r.append(f"dims.{k}: {A['dims'].get(k)} vs {B['dims'].get(k)}")
    # The guard mode and the variance cap are part of the likelihood's definition:
    # two records built with different values evaluate different functions.
    for k in LIKELIHOOD_SETTINGS:
        va, vb = A["config"].get(k), B["config"].get(k)
        if va is None or vb is None or va != vb:
            r.append(f"config.{k}: {va} vs {vb} (different likelihood definition, or not recorded)")
    return r


def _ratio(x, y):
    try:
        x, y = float(x), float(y)
    except (TypeError, ValueError):
        return None
    if y == 0 or not math.isfinite(x) or not math.isfinite(y):
        return None
    return x / y


def _side(rec):
    pkg = rec["package"]
    return {
        "label": rec["label"],
        "implementation": rec["implementation"],
        "kernel": rec["config"]["kernel"],
        "jit_mode_requested": rec["config"]["jit_mode_requested"],
        "package_git_sha": pkg.get("git_sha"),
        "package_known_sha": (pkg.get("known_digest_match") or {}).get("sha"),
        "package_file": pkg["file"],
        "backend": rec["device"]["backend"],
        "device_kind": rec["device"]["device_kind"],
        "python": rec["env"]["python"],
        "jax": rec["env"]["versions"].get("jax"),
        "sel_batch_size": rec["config"]["sel_batch_size"],
        "pe_event_block": rec["config"]["pe_event_block"],
        "max_likelihood_variance": rec["config"].get("max_likelihood_variance"),
        "selection_neff_soft_guard": rec["config"].get("selection_neff_soft_guard"),
        "plan_adapter": rec["config"].get("plan_adapter") is not None,
        "record": rec.get("_path"),
    }


def compare(A, B, rtol, atol):
    reasons = refusal_reasons(A, B)
    summary = {
        "schema": "darksirens-bench-compare/1",
        "rtol": rtol,
        "atol": atol,
        "rel_definition": "|A-B|/|A| (A = first record)",
        "A": _side(A),
        "B": _side(B),
    }
    if reasons:
        summary["status"] = "refused"
        summary["refusal_reasons"] = reasons
        return summary
    summary["status"] = "compared"
    summary["plan"] = A["plan"]["name"]
    summary["inputs"] = {s: {"path": A["inputs"][s]["path"], "sha256": A["inputs"][s]["sha256"],
                             "format_version": A["inputs"][s]["attrs"].get("format_version")}
                         for s in ("pe", "sel")}
    summary["dims"] = {k: A["dims"].get(k) for k in DIM_KEYS + ("T_obs_yr", "n_coords")}
    fields = {}
    for f in SCALAR_FIELDS + ARRAY_FIELDS:
        res = compare_values(_hexes(A, f), _hexes(B, f), rtol, atol)
        pa, pb = _per_coord_hexes(A, f), _per_coord_hexes(B, f)
        res["max_rel_per_coord"] = [compare_values(x, y, rtol, atol)["max_rel"]
                                    for x, y in zip(pa, pb)]
        fields[f] = res
    dec = compare_values(_hexes_decoded(A), _hexes_decoded(B), 0.0, 0.0)
    fields["decoded_full_parameter_vector"] = dec
    summary["fields"] = fields
    summary["max_rel_by_field"] = {f: v["max_rel"] for f, v in fields.items()}
    summary["bitwise_by_field"] = {f: v["bitwise"] for f, v in fields.items()}

    mask_rows = []
    masks_equal = True
    for pa, pb in zip(A["values"]["per_coord"], B["values"]["per_coord"]):
        row = {"index": pa["index"]}
        for k in MASK_KEYS:
            eq = pa["masks"][k] == pb["masks"][k]
            row[k] = eq
            masks_equal &= eq
        eq = pa["masks"]["pe_final_per_event_count"] == pb["masks"]["pe_final_per_event_count"]
        row["pe_final_per_event_count"] = eq
        masks_equal &= eq
        row["guard_pass"] = pa["guard_pass"] == pb["guard_pass"]
        row["total_finite"] = pa["total_finite"] == pb["total_finite"]
        masks_equal &= row["guard_pass"] and row["total_finite"]
        row["counts_A"] = {k: pa["masks"][k]["count_true"] for k in MASK_KEYS}
        mask_rows.append(row)
    order_ok = all(
        rec.get("mask_order", {}).get("pe_dL_equals_file") is True
        and rec.get("mask_order", {}).get("sel_dL_equals_file") is True
        for rec in (A, B))
    masks_equal = bool(masks_equal and order_ok)
    summary["masks"] = {"all_equal": masks_equal, "order_verified_both": bool(order_ok),
                        "per_coord": mask_rows,
                        "note": "mask equality = identical length, count and sha256 of the "
                                "uint8 mask in FILE order (each record verifies its order "
                                "against the HDF5 dL datasets); guard verdict and finiteness "
                                "of the total must also agree"}

    summary["repeat_consistency"] = {
        "A": {"bitwise": A["repeat_consistency"]["bitwise"],
              "timed_loop": A["repeat_consistency"]["timed_loop_bitwise_consistent"]},
        "B": {"bitwise": B["repeat_consistency"]["bitwise"],
              "timed_loop": B["repeat_consistency"]["timed_loop_bitwise_consistent"]},
    }
    summary["kernel_vs_diag_total"] = {
        "A_all_bitwise": all(pc["kernel_vs_diag_total"]["bitwise"] for pc in A["values"]["per_coord"]),
        "B_all_bitwise": all(pc["kernel_vs_diag_total"]["bitwise"] for pc in B["values"]["per_coord"]),
    }
    ta, tb = A["timing"], B["timing"]
    issues = []
    for label, get in (("backend", lambda r: r["device"]["backend"]),
                       ("device_kind", lambda r: r["device"]["device_kind"]),
                       ("host", lambda r: r["env"]["host"]),
                       ("n_calls", lambda r: r["config"].get("n_calls")),
                       ("warmup", lambda r: r["config"].get("warmup"))):
        va, vb = get(A), get(B)
        if va != vb:
            issues.append(f"{label}: {va} vs {vb}")
    for tag, rec in (("A", A), ("B", B)):
        req = rec["timing"]["compile"]["timed_loop"]["requests"]
        if req:
            issues.append(f"{tag} compiles inside its timed loop ({req} requests)")
    summary["timing"] = {
        "comparable": not issues,
        "comparability_issues": issues,
        "first_call_s": {"A": ta["t_first_call_s"], "B": tb["t_first_call_s"],
                         "ratio_A_over_B": _ratio(ta["t_first_call_s"], tb["t_first_call_s"])},
        "warm_median_s": {"A": ta["warm"]["median_s"], "B": tb["warm"]["median_s"],
                          "ratio_A_over_B": _ratio(ta["warm"]["median_s"], tb["warm"]["median_s"])},
        "warm_min_s": {"A": ta["warm"]["min_s"], "B": tb["warm"]["min_s"],
                       "ratio_A_over_B": _ratio(ta["warm"]["min_s"], tb["warm"]["min_s"])},
        "t_load_s": {"A": ta["t_load_s"], "B": tb["t_load_s"]},
        "t_build_s": {"A": ta["t_build_s"], "B": tb["t_build_s"]},
        "compile_requests_timed_loop": {"A": ta["compile"]["timed_loop"]["requests"],
                                        "B": tb["compile"]["timed_loop"]["requests"]},
        "compile_first_call": {"A": ta["compile"]["first_call"], "B": tb["compile"]["first_call"]},
        "peak_device_bytes": {"A": ta.get("peak_device_bytes"), "B": tb.get("peak_device_bytes")},
        "peak_host_rss_bytes": {"A": ta.get("peak_host_rss_bytes"), "B": tb.get("peak_host_rss_bytes")},
        "peak_device_bytes_all_phases": {"A": ta.get("peak_device_bytes_all_phases"),
                                         "B": tb.get("peak_device_bytes_all_phases")},
        "peak_host_rss_bytes_all_phases": {"A": ta.get("peak_host_rss_bytes_all_phases"),
                                           "B": tb.get("peak_host_rss_bytes_all_phases")},
        "note": "ratio_A_over_B > 1 means B is faster",
    }
    parity = all(v["pass"] for v in fields.values()) and masks_equal
    repeat_ok = all(v["bitwise"] and v["timed_loop"] for v in summary["repeat_consistency"].values())
    summary["verdict"] = {
        "parity_pass": bool(parity),
        "bitwise_all_fields": bool(all(v["bitwise"] for v in fields.values())),
        "masks_equal": bool(masks_equal),
        "repeat_consistent_both": bool(repeat_ok),
        "overall_pass": bool(parity and repeat_ok),
    }
    return summary


def _hexes_decoded(rec):
    out = []
    for pc in rec["values"]["per_coord"]:
        out.extend(pc["decoded_full"]["hex"])
    return out


def to_markdown(s):
    L = []
    A, B = s["A"], s["B"]
    L.append(f"# Parity summary: {A['label']} vs {B['label']}")
    L.append("")
    L.append(f"- A: `{A['implementation']}` kernel `{A['kernel']}` ({A['record']})")
    L.append(f"- B: `{B['implementation']}` kernel `{B['kernel']}` ({B['record']})")
    L.append(f"- status: **{s['status']}**; rtol={s['rtol']}, atol={s['atol']}; rel = {s['rel_definition']}")
    if s["status"] != "compared":
        L.append("")
        L.append("Refused:")
        L.extend(f"- {r}" for r in s["refusal_reasons"])
        return "\n".join(L) + "\n"
    v = s["verdict"]
    L.append(f"- plan `{s['plan']}`; dims {s['dims']}")
    L.append(f"- verdict: parity_pass={v['parity_pass']}, bitwise_all_fields={v['bitwise_all_fields']}, "
             f"masks_equal={v['masks_equal']}, repeat_consistent_both={v['repeat_consistent_both']}")
    L.append("")
    L.append("| field | n | bitwise | n bit-different | max abs | max rel | pass |")
    L.append("|---|---|---|---|---|---|---|")
    for f, r in s["fields"].items():
        L.append(f"| {f} | {r['n']} | {r['bitwise']} | {r['n_bit_different']} | "
                 f"{r['max_abs']:.3e} | {r['max_rel']:.3e} | {r['pass']} |")
    t = s["timing"]
    L.append("")
    if t.get("comparability_issues"):
        L.append("Timing ratios are NOT like for like: " + "; ".join(t["comparability_issues"]))
        L.append("")
    L.append("| timing | A | B | A/B |")
    L.append("|---|---|---|---|")
    for k in ("first_call_s", "warm_median_s", "warm_min_s"):
        r = t[k]
        ratio = "n/a" if r["ratio_A_over_B"] is None else f"{r['ratio_A_over_B']:.3f}"
        L.append(f"| {k} | {r['A']:.6g} | {r['B']:.6g} | {ratio} |")
    L.append(f"| compile requests in timed loop | {t['compile_requests_timed_loop']['A']} | "
             f"{t['compile_requests_timed_loop']['B']} | |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--rtol", type=float, default=1e-12)
    ap.add_argument("--atol", type=float, default=0.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", default=None)
    args = ap.parse_args(argv)
    A = bc.read_json(args.a)
    B = bc.read_json(args.b)
    A["_path"], B["_path"] = os.path.abspath(args.a), os.path.abspath(args.b)
    s = compare(A, B, args.rtol, args.atol)
    s["command_line"] = [sys.executable] + list(sys.argv if argv is None else ["compare_records.py"] + argv)
    bc.write_json(args.out, s)
    if args.md:
        with open(args.md, "w") as f:
            f.write(to_markdown(s))
    if s["status"] != "compared":
        print("REFUSED:\n  " + "\n  ".join(s["refusal_reasons"]), file=sys.stderr)
        return 2
    v = s["verdict"]
    worst = max(s["max_rel_by_field"].items(), key=lambda kv: kv[1])
    print(f"{s['A']['label']} vs {s['B']['label']} plan={s['plan']}: parity_pass={v['parity_pass']} "
          f"bitwise_all={v['bitwise_all_fields']} masks_equal={v['masks_equal']} "
          f"repeat_ok={v['repeat_consistent_both']} worst max_rel={worst[0]}:{worst[1]:.3e} "
          f"warm A/B={s['timing']['warm_median_s']['ratio_A_over_B']}")
    return 0 if v["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
