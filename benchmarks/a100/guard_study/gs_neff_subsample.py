#!/usr/bin/env python3
"""Guard study (GS): N_eff of the selection integral versus the number of detected injections,
from the per-injection log weights a bench_components.py record stores
(``w_weights__ldw_sel__c<k>`` in ``<record>.components.npz``, FILE order). numpy only.

    python gs_neff_subsample.py --record COMP.json --coords 0,1,...,8 --strides 2,5,10,20,50,100 \
        [--check STRIDE_RECORD.json ...] [--bootstrap 200] --seed 20260924 --out J --md M

N_eff is recomputed with the codes' own estimator (legacy darksirens/likelihood/selection.py:
185-196, identical in core): 1/N_eff = exp(lse2 - 2 lse) - 1/Ndraw over the finite log weights.
Subsets: every offset k of stride s (the strided product files are full[0::s], checked by dL
equality for s = 10 and 100), with Ndraw scaled by the subset's share of the detected
injections; offset 0 is compared against the strided-file records passed with --check (their
exact file Ndraw is used there). A bootstrap (resampling the detected injections with
replacement at full size) shows how representative the full-file N_eff is.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gs_guard as G  # noqa: E402


def neff_from_logw(lw, ndraw):
    f = np.isfinite(lw)
    if not f.any():
        return 0.0, -math.inf
    x = lw[f]
    m = x.max()
    lse = m + math.log(np.sum(np.exp(x - m)))
    lse2 = 2 * m + math.log(np.sum(np.exp(2 * (x - m))))
    inv = max(math.exp(lse2 - 2 * lse) - 1.0 / ndraw, 0.0)
    return (math.inf if inv == 0 else 1.0 / inv), lse - math.log(ndraw)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--record", required=True)
    ap.add_argument("--coords", default="0")
    ap.add_argument("--strides", default="2,5,10,20,50,100")
    ap.add_argument("--check", action="append", default=[])
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument("--caps", default="1,2,5,10,20")
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    rec = G.load(a.record)
    npz = a.record + ".components.npz"
    z = np.load(npz, allow_pickle=False)
    n_det = int(rec["dims"]["n_injections"])
    ndraw = float(rec["dims"]["ndraw"])
    n_obs = float(rec["dims"]["n_events"])
    strides = [int(s) for s in a.strides.split(",")]
    caps = [float(c) for c in a.caps.split(",")]
    checks = [G.load(p) for p in a.check]
    rng = np.random.default_rng(a.seed)
    out = {"schema": "gs-neff-subsample/1", "record": os.path.abspath(a.record), "npz": npz,
           "n_detected": n_det, "ndraw": ndraw, "coords": []}
    L = ["# N_eff versus the number of detected injections (per-injection weights)", "",
         f"Source: `{os.path.basename(a.record)}` ({n_det:,} detected injections, Ndraw {ndraw:.10g}).", ""]
    for c in [int(x) for x in a.coords.split(",")]:
        key = f"w_weights__ldw_sel__c{c}"
        if key not in z.files:
            print(f"coord {c}: {key} not stored (use --full-array-coords)", file=sys.stderr)
            continue
        lw = np.asarray(z[key], dtype=np.float64)
        assert lw.size == n_det, (lw.size, n_det)
        ne, lm = neff_from_logw(lw, ndraw)
        rec_ne = float(z[f"e_sel_reduce__n_eff__c{c}"]) if f"e_sel_reduce__n_eff__c{c}" in z.files else None
        w = np.exp(lw[np.isfinite(lw)] - np.max(lw[np.isfinite(lw)]))
        ws = np.sort(w)[::-1]
        tot = ws.sum()
        top = {str(k): float(ws[:k].sum() / tot) for k in (1, 10, 100, 1000) if k <= ws.size}
        ent = {"coord": c, "n_eff_full": ne, "n_eff_record": rec_ne,
               "n_eff_rel_diff_vs_record": (abs(ne - rec_ne) / rec_ne) if rec_ne else None,
               "log_mu": lm, "n_eff_per_detected": ne / n_det, "top_weight_share": top,
               "strides": [], "checks": [], "bootstrap": None}
        for s in strides:
            vals = []
            for k in range(s):
                sub = lw[k::s]
                vals.append(neff_from_logw(sub, ndraw * sub.size / n_det)[0])
            v = np.asarray(vals)
            ent["strides"].append({"stride": s, "n_subsets": s, "n_detected_each": int(lw[0::s].size),
                                   "n_eff_offset0": float(v[0]), "mean": float(v.mean()),
                                   "median": float(np.median(v)), "min": float(v.min()), "max": float(v.max()),
                                   "std": float(v.std(ddof=1)) if s > 1 else 0.0,
                                   "mean_ratio_to_full": float(v.mean() / ne), "linear_expectation": 1.0 / s})
        for cr in checks:
            m = G.rec_meta(cr)
            pc = cr["values"]["per_coord"][c]
            st = int(round(n_det / m["n_injections"]))
            sub = lw[0::st]
            mine = neff_from_logw(sub, float(m["ndraw"]))[0]
            theirs = G.val(pc["n_eff"])
            ent["checks"].append({"record": m["record"], "stride": st, "n_eff_record": theirs,
                                  "n_eff_numpy_offset0": mine, "rel": abs(mine - theirs) / theirs})
        if a.bootstrap:
            b = []
            idx_all = np.arange(n_det)
            for _ in range(a.bootstrap):
                idx = rng.choice(idx_all, size=n_det, replace=True)
                b.append(neff_from_logw(lw[idx], ndraw)[0])
            b = np.asarray(b)
            ent["bootstrap"] = {"n": a.bootstrap, "q16": float(np.quantile(b, 0.16)), "median": float(np.median(b)),
                                "q84": float(np.quantile(b, 0.84)), "min": float(b.min()), "max": float(b.max())}
        # extrapolation per cap, using the PE variance sum of the record's coordinate
        pv = G.val(rec["values"]["per_coord"][c]["pe_variance_sum"]) if rec.get("values") else None
        if pv is not None:
            ent["extrapolation"] = []
            for cap in caps:
                T = G.threshold(n_obs, cap, pv)
                ex = {"cap": cap, "threshold": T, "budget_exhausted": (cap - pv) <= G.MIN_BUDGET,
                      "n_det_needed_linear_from_full": None if (cap - pv) <= G.MIN_BUDGET else n_det * T / ne}
                if ent["bootstrap"] and not ex["budget_exhausted"]:
                    ex["n_det_needed_from_bootstrap_q16_q84"] = [n_det * T / ent["bootstrap"]["q84"],
                                                                 n_det * T / ent["bootstrap"]["q16"]]
                ent["extrapolation"].append(ex)
        out["coords"].append(ent)
        L += [f"## coordinate {c}", "",
              f"N_eff (full) {G.fmt(ne)} (record {G.fmt(rec_ne)}; rel diff {G.fmt(ent['n_eff_rel_diff_vs_record'],3)}); "
              f"N_eff per detected injection {G.fmt(ne / n_det, 4)}; top-weight share of the selection sum: "
              + ", ".join(f"top {k}: {G.fmt(v, 3)}" for k, v in top.items()), "",
              "| stride | subsets | detected each | N_eff offset 0 | mean | median | min | max | mean / full | linear expectation |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {s['stride']} | {s['n_subsets']} | {s['n_detected_each']:,} | {G.fmt(s['n_eff_offset0'])} | {G.fmt(s['mean'])} | "
              f"{G.fmt(s['median'])} | {G.fmt(s['min'])} | {G.fmt(s['max'])} | {G.fmt(s['mean_ratio_to_full'],4)} | {G.fmt(s['linear_expectation'],4)} |"
              for s in ent["strides"]]
        if ent["checks"]:
            L += [""] + [f"* offset-0 check vs `{k['record']}`: numpy {G.fmt(k['n_eff_numpy_offset0'])} vs record "
                         f"{G.fmt(k['n_eff_record'])} (rel {G.fmt(k['rel'],3)})" for k in ent["checks"]]
        if ent["bootstrap"]:
            bb = ent["bootstrap"]
            L += ["", f"Bootstrap at full size ({bb['n']} resamples): N_eff median {G.fmt(bb['median'])}, "
                      f"16-84% {G.fmt(bb['q16'])}-{G.fmt(bb['q84'])}, range {G.fmt(bb['min'])}-{G.fmt(bb['max'])}"]
        if ent.get("extrapolation"):
            L += ["", "| cap | T | detected needed (linear, from the full file) | from bootstrap 84%-16% N_eff |", "|---|---|---|---|"]
            L += [f"| {G.fmt(e['cap'])} | {G.fmt(e['threshold'])} | "
                  f"{'budget exhausted' if e['budget_exhausted'] else G.fmt(e['n_det_needed_linear_from_full'],4)} | "
                  f"{'-' if not e.get('n_det_needed_from_bootstrap_q16_q84') else ' - '.join(G.fmt(x,4) for x in e['n_det_needed_from_bootstrap_q16_q84'])} |"
                  for e in ent["extrapolation"]]
        L.append("")
    G.jdump(out, a.out)
    if a.md:
        with open(a.md, "w") as f:
            f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
