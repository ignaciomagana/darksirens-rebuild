#!/usr/bin/env python3
"""Compare two inference-ladder runs (infer_ladder.py outputs): integration check only.

    python compare_posteriors.py A B [--out cmp.json] [--md cmp.md] [--cross-sampler]

A and B are run directories (holding ``record.json`` and ``posterior.npz``) or
``record.json`` paths; A is the reference (normally legacy). Reports, per sampled
parameter, mean / std / 16-50-84 % quantiles of both posteriors, the mean difference
in units of the posterior std and of the combined Monte-Carlo error of the means, and
the two-sample Kolmogorov-Smirnov statistic D (with an approximate p-value whose
effective sizes are the Kish ESS of each run's dead-point weights, since the
equal-weight resamples repeat points); the logZ difference in units of the combined
quoted error; and a performance / "effective sampler progress per wall time"
comparison (evaluations per second, iterations per second, compressed prior volume
-log X per second, time to reach common -log X levels, posterior ESS per second).

This is an INTEGRATION check of two production runs, never a parity criterion: two
nested-sampling runs agree only statistically, and the gate fields of the campaign's
parity rules are judged by compare_records.py on fixed coordinates. The comparator
refuses (exit 2) runs that differ in rung, parameter plan, inputs or any matched
sampler / likelihood setting (``--cross-sampler`` allows the sampler, and only the
sampler, to differ). Exit 0 otherwise; the verdict block is informational.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_common as bc  # noqa: E402

SCHEMA = "darksirens-infer-ladder/1"
MATCHED_SETTINGS = ("nlive", "dlogz", "seed", "max_samples", "tinyns_preset", "sampler_preflight",
                    "prior_transform_dispatch", "show_progress", "checkpointing",
                    "sel_batch_size", "pe_event_block", "guard", "max_likelihood_variance")


class Refused(Exception):
    pass


def load_run(path):
    rec_path = path if path.endswith(".json") else os.path.join(path, "record.json")
    with open(rec_path) as f:
        rec = json.load(f)
    run_dir = os.path.dirname(os.path.abspath(rec_path))
    npz = os.path.join(run_dir, "posterior.npz")
    if not os.path.isfile(npz):
        npz = (rec.get("result") or {}).get("posterior_npz")
    post = None
    if npz and os.path.isfile(npz):
        with np.load(npz, allow_pickle=False) as d:
            post = {k: d[k] for k in d.files}
    prog = []
    pcsv = os.path.join(run_dir, "progress.csv")
    if os.path.isfile(pcsv):
        with open(pcsv) as f:
            for row in csv.DictReader(f):
                prog.append(row)
    return {"record": rec, "path": rec_path, "dir": run_dir, "posterior": post, "progress": prog}


def check_comparable(A, B, cross_sampler=False):
    a, b = A["record"], B["record"]
    why = []
    for r, name in ((a, "A"), (b, "B")):
        if r.get("schema") != SCHEMA:
            why.append(f"{name}: schema {r.get('schema')!r} is not {SCHEMA}")
        if r.get("status") != "ok":
            why.append(f"{name}: status {r.get('status')!r} (only 'ok' runs are compared)")
    if why:
        raise Refused("; ".join(why))
    if a["rung"]["rung"] != b["rung"]["rung"]:
        why.append(f"rung {a['rung']['rung']} vs {b['rung']['rung']}")
    pa, pb = a["plan"]["implementation_view"], b["plan"]["implementation_view"]
    for k in ("labels", "lower_hex", "upper_hex", "prior_kinds", "joint_constraints"):
        if pa.get(k) != pb.get(k):
            why.append(f"parameter plan {k} differs")
    sa, sb = a["settings"]["requested"], b["settings"]["requested"]
    for k in MATCHED_SETTINGS:
        if sa.get(k) != sb.get(k):
            why.append(f"setting {k}: {sa.get(k)!r} vs {sb.get(k)!r}")
    if sa.get("sampler") != sb.get("sampler") and not cross_sampler:
        why.append(f"sampler {sa.get('sampler')} vs {sb.get('sampler')} (pass --cross-sampler)")
    for f in ("pe", "sel"):
        if a["inputs"][f]["sha256"] != b["inputs"][f]["sha256"]:
            why.append(f"input {f} sha256 differs")
    if A["posterior"] is None or B["posterior"] is None:
        why.append("posterior.npz missing")
    if why:
        raise Refused("; ".join(why))


def kish_ess(logwt):
    lw = np.asarray(logwt, dtype=np.float64)
    lw = lw[np.isfinite(lw)]
    if lw.size == 0:
        return None
    w = np.exp(lw - lw.max())
    return float(w.sum() ** 2 / np.sum(w * w))


def ks_D(x, y):
    x = np.sort(np.asarray(x, dtype=np.float64))
    y = np.sort(np.asarray(y, dtype=np.float64))
    allv = np.concatenate([x, y])
    c1 = np.searchsorted(x, allv, side="right") / x.size
    c2 = np.searchsorted(y, allv, side="right") / y.size
    return float(np.max(np.abs(c1 - c2)))


def ks_p_approx(D, n1, n2):
    """Kolmogorov asymptotic p-value with effective sizes (Numerical Recipes form)."""
    if not n1 or not n2:
        return None
    en = math.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / en) * D
    if lam < 1e-3:
        return 1.0
    s = 0.0
    for j in range(1, 101):
        term = 2.0 * (-1) ** (j - 1) * math.exp(-2.0 * j * j * lam * lam)
        s += term
        if abs(term) < 1e-12:
            break
    return float(min(max(s, 0.0), 1.0))


def param_stats(x):
    x = np.asarray(x, dtype=np.float64)
    q16, q50, q84 = np.quantile(x, [0.16, 0.5, 0.84])
    return {"n": int(x.size), "mean": float(np.mean(x)), "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
            "q16": float(q16), "q50": float(q50), "q84": float(q84)}


def _f(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def time_to_logvol(progress, levels):
    """Seconds since sampling start at which -log X first reached each level (main rows)."""
    rows = [(-_f(r["log_volume"]), _f(r["t_since_sampling_s"])) for r in progress
            if r.get("phase") == "main" and _f(r.get("log_volume")) is not None
            and _f(r.get("t_since_sampling_s")) is not None]
    out = []
    for L in levels:
        hit = next((t for nlx, t in rows if nlx >= L), None)
        out.append(hit)
    return out, (rows[-1][0] if rows else None)


def perf(run):
    r = run["record"]
    t = r.get("timing", {})
    lc = r.get("likelihood_calls", {})
    pr = r.get("progress", {})
    st = pr.get("steady_state") or {}
    res = r.get("result") or {}
    ev = t.get("sampling_events_s") or {}
    mon = (r.get("memory") or {}).get("monitor") or {}
    ess = res.get("dead_point_kish_ess")
    tsamp = t.get("t_sampling_s")
    last_lv = pr.get("last_log_volume")
    return {
        "t_load_s": t.get("t_load_s"), "t_build_s": t.get("t_build_s"),
        "t_first_call_s": t.get("t_first_call_s"), "t_sampling_s": tsamp,
        "t_to_first_progress_s": ev.get("first_progress"), "t_main_loop_s": t.get("t_main_loop_s"),
        "t_total_s": t.get("t_total_s"),
        "compile_sampling": r.get("compile", {}).get("sampling"),
        "n_like_evals": lc.get("n_like_evals"), "evals_per_s_sampling": lc.get("evals_per_s_sampling"),
        "evals_per_s_steady": lc.get("evals_per_s_steady"),
        "iterations": pr.get("last_main_iteration"), "iterations_per_s_steady": st.get("iterations_per_s"),
        "neg_log_volume_final": None if last_lv is None else -float(last_lv),
        "neg_log_volume_per_s_steady": st.get("log_volume_per_s"),
        "neg_log_volume_per_s_overall": (None if (last_lv is None or not tsamp) else -float(last_lv) / tsamp),
        "dead_point_kish_ess": ess, "ess_per_s_sampling": (None if (ess is None or not tsamp) else ess / tsamp),
        "peak_host_rss_bytes": (r.get("memory") or {}).get("peak_host_rss_bytes"),
        "device_peak_bytes_in_use": mon.get("device_peak_bytes_in_use"),
    }


def compare(A, B, cross_sampler=False, levels_frac=(0.25, 0.5, 0.75, 1.0)):
    check_comparable(A, B, cross_sampler)
    a, b = A["record"], B["record"]
    pa, pb = A["posterior"], B["posterior"]
    labels = [str(x) for x in pa["labels"]]
    essA, essB = kish_ess(pa["dead_logwt"]), kish_ess(pb["dead_logwt"])
    params = {}
    for i, lab in enumerate(labels):
        xa, xb = pa["samples"][:, i], pb["samples"][:, i]
        sa, sb = param_stats(xa), param_stats(xb)
        pooled = math.sqrt(0.5 * (sa["std"] ** 2 + sb["std"] ** 2))
        mcerr = (math.sqrt(sa["std"] ** 2 / essA + sb["std"] ** 2 / essB)
                 if (essA and essB) else None)
        D = ks_D(xa, xb)
        dm = sb["mean"] - sa["mean"]
        params[lab] = {
            "A": sa, "B": sb, "delta_mean": dm,
            "delta_mean_over_posterior_std": (dm / pooled if pooled > 0 else None),
            "delta_mean_over_mc_error": (dm / mcerr if mcerr else None),
            "delta_q50": sb["q50"] - sa["q50"],
            "std_ratio_B_over_A": (sb["std"] / sa["std"] if sa["std"] > 0 else None),
            "ks_D": D, "ks_p_approx_ess": ks_p_approx(D, essA, essB),
            "samples_bitwise_equal": bool(xa.shape == xb.shape and np.array_equal(xa, xb)),
        }
    ra, rb = a["result"], b["result"]
    za, zb = _f(ra.get("logZ")), _f(rb.get("logZ"))
    ea, eb = _f(ra.get("logZerr")), _f(rb.get("logZerr"))
    comb = math.sqrt(ea ** 2 + eb ** 2) if (ea is not None and eb is not None) else None
    logz = {"A": za, "B": zb, "A_err": ea, "B_err": eb,
            "A_hex": ra.get("logZ_hex"), "B_hex": rb.get("logZ_hex"),
            "bitwise_equal": ra.get("logZ_hex") == rb.get("logZ_hex"),
            "delta": None if (za is None or zb is None) else zb - za,
            "combined_err": comb,
            "n_sigma": (None if (za is None or zb is None or not comb) else abs(zb - za) / comb)}
    fa, fb = a.get("first_call") or {}, b.get("first_call") or {}
    va, vb = _f(fa.get("logL")), _f(fb.get("logL"))
    first = {"coordinate_equal": fa.get("coordinate_hex") == fb.get("coordinate_hex"),
             "A": va, "B": vb, "bitwise_equal": fa.get("logL_hex") == fb.get("logL_hex"),
             "rel_diff": (None if (va is None or vb is None or va == 0) else abs(vb - va) / abs(va)),
             "note": "the rung-centre likelihood value of each run's explicit first call (informational)"}
    PA, PB = perf(A), perf(B)
    ratios = {}
    for k in PA:
        x, y = PA.get(k), PB.get(k)
        num = (int, float)
        ok = isinstance(x, num) and isinstance(y, num) and not isinstance(x, bool) and x
        ratios[k] = (y / x) if ok else None
    _, fa_lv = time_to_logvol(A["progress"], [])
    _, fb_lv = time_to_logvol(B["progress"], [])
    common = min(v for v in (fa_lv, fb_lv) if v is not None) if (fa_lv and fb_lv) else None
    levels = [common * f for f in levels_frac] if common else []
    ta, _ = time_to_logvol(A["progress"], levels)
    tb, _ = time_to_logvol(B["progress"], levels)
    progress = {"levels_neg_log_volume": levels, "A_seconds": ta, "B_seconds": tb,
                "ratio_B_over_A": [(y / x) if (x and y) else None for x, y in zip(ta, tb)],
                "note": ("-log X levels at the given fractions of the smaller final -log X of the "
                         "two runs; seconds since sampling start (includes preflight, initial live "
                         "points and in-sampler compiles)")}
    all_bitwise = all(p["samples_bitwise_equal"] for p in params.values())
    max_D = max((p["ks_D"] for p in params.values()), default=None)
    max_mc = max((abs(p["delta_mean_over_mc_error"]) for p in params.values()
                  if p["delta_mean_over_mc_error"] is not None), default=None)
    verdict = {
        "integration_check_only": True,
        "not_a_parity_criterion": ("posterior agreement between two nested-sampling runs is "
                                   "statistical; parity is judged on fixed coordinates"),
        "posterior_samples_bitwise_equal": all_bitwise,
        "logZ_bitwise_equal": logz["bitwise_equal"],
        "logZ_within_2_combined_sigma": (None if logz["n_sigma"] is None else logz["n_sigma"] <= 2.0),
        "max_ks_D": max_D,
        "max_abs_delta_mean_over_mc_error": max_mc,
        "min_ks_p_approx": min((p["ks_p_approx_ess"] for p in params.values()
                                if p["ks_p_approx_ess"] is not None), default=None),
    }
    ident = {
        "A": {"path": A["path"], "implementation": a["implementation"], "label": a["label"],
              "sampler": a["settings"]["requested"]["sampler"],
              "package_sha": a["package"].get("git_sha") or (a["package"].get("known_digest_match") or {}).get("sha"),
              "harness_sha": a["harness"]["git"].get("git_sha"), "backend": a["device"]["backend"]},
        "B": {"path": B["path"], "implementation": b["implementation"], "label": b["label"],
              "sampler": b["settings"]["requested"]["sampler"],
              "package_sha": b["package"].get("git_sha") or (b["package"].get("known_digest_match") or {}).get("sha"),
              "harness_sha": b["harness"]["git"].get("git_sha"), "backend": b["device"]["backend"]},
        "rung": a["rung"]["rung"], "labels": labels,
        "settings": {k: a["settings"]["requested"].get(k) for k in MATCHED_SETTINGS},
        "inputs_sha256": {f: a["inputs"][f]["sha256"] for f in ("pe", "sel")},
        "ess_A": essA, "ess_B": essB,
        "n_samples": [int(pa["samples"].shape[0]), int(pb["samples"].shape[0])],
    }
    return {"schema": "darksirens-infer-ladder-compare/1", "identity": ident, "logZ": logz,
            "first_call_centre": first, "parameters": params,
            "performance": {"A": PA, "B": PB, "ratio_B_over_A": ratios}, "progress": progress,
            "verdict": verdict}


def _fmt(v, nd=4):
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if abs(v) >= 1e4 or (abs(v) < 1e-3 and v != 0):
        return f"{v:.{nd}e}"
    return f"{v:.{nd}g}"


def to_markdown(c):
    i = c["identity"]
    lines = [f"# Inference-ladder comparison: rung {i['rung']}",
             "",
             f"A = {i['A']['implementation']} ({i['A']['sampler']}, {i['A']['label']}); "
             f"B = {i['B']['implementation']} ({i['B']['sampler']}, {i['B']['label']}). "
             "Integration check only, not a parity criterion.",
             "",
             f"logZ: A {_fmt(c['logZ']['A'], 10)} +- {_fmt(c['logZ']['A_err'])}, "
             f"B {_fmt(c['logZ']['B'], 10)} +- {_fmt(c['logZ']['B_err'])}; "
             f"delta {_fmt(c['logZ']['delta'])} = {_fmt(c['logZ']['n_sigma'])} combined sigma; "
             f"bitwise {c['logZ']['bitwise_equal']}",
             f"Posterior samples bitwise equal: {c['verdict']['posterior_samples_bitwise_equal']}; "
             f"Kish ESS A {_fmt(i['ess_A'])}, B {_fmt(i['ess_B'])}",
             "",
             "| parameter | mean A | mean B | std A | std B | q16/q50/q84 A | q16/q50/q84 B | "
             "dmean/std | dmean/MCerr | KS D | KS p (ESS) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for lab, p in c["parameters"].items():
        A, B = p["A"], p["B"]
        lines.append(f"| `{lab}` | {_fmt(A['mean'])} | {_fmt(B['mean'])} | {_fmt(A['std'])} | "
                     f"{_fmt(B['std'])} | {_fmt(A['q16'])}/{_fmt(A['q50'])}/{_fmt(A['q84'])} | "
                     f"{_fmt(B['q16'])}/{_fmt(B['q50'])}/{_fmt(B['q84'])} | "
                     f"{_fmt(p['delta_mean_over_posterior_std'])} | {_fmt(p['delta_mean_over_mc_error'])} | "
                     f"{_fmt(p['ks_D'])} | {_fmt(p['ks_p_approx_ess'])} |")
    lines += ["", "| performance | A | B | B/A |", "|---|---|---|---|"]
    PA, PB, R = c["performance"]["A"], c["performance"]["B"], c["performance"]["ratio_B_over_A"]
    for k in ("t_load_s", "t_build_s", "t_first_call_s", "t_sampling_s", "t_to_first_progress_s",
              "t_main_loop_s", "n_like_evals", "evals_per_s_sampling", "evals_per_s_steady",
              "iterations", "iterations_per_s_steady", "neg_log_volume_final",
              "neg_log_volume_per_s_steady", "neg_log_volume_per_s_overall", "dead_point_kish_ess",
              "ess_per_s_sampling", "peak_host_rss_bytes", "device_peak_bytes_in_use"):
        lines.append(f"| {k} | {_fmt(PA.get(k))} | {_fmt(PB.get(k))} | {_fmt(R.get(k))} |")
    pr = c["progress"]
    if pr["levels_neg_log_volume"]:
        lines += ["", "| -log X reached | A s | B s | B/A |", "|---|---|---|---|"]
        for L, x, y, q in zip(pr["levels_neg_log_volume"], pr["A_seconds"], pr["B_seconds"],
                              pr["ratio_B_over_A"]):
            lines.append(f"| {_fmt(L)} | {_fmt(x)} | {_fmt(y)} | {_fmt(q)} |")
    f = c["first_call_centre"]
    lines += ["", f"Rung-centre logL (explicit first call): A {_fmt(f['A'], 17)}, B {_fmt(f['B'], 17)}, "
              f"bitwise {f['bitwise_equal']}, rel {_fmt(f['rel_diff'])}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("A")
    ap.add_argument("B")
    ap.add_argument("--out", default=None)
    ap.add_argument("--md", default=None)
    ap.add_argument("--cross-sampler", action="store_true")
    a = ap.parse_args(argv)
    try:
        c = compare(load_run(a.A), load_run(a.B), cross_sampler=a.cross_sampler)
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    if a.out:
        bc.write_json(a.out, c)
    md = to_markdown(c)
    if a.md:
        with open(a.md, "w") as f:
            f.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
