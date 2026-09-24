#!/usr/bin/env python3
"""Compare the progress traces of two inference-ladder runs (any status: ok, budget-capped, timeout).

    python compare_progress.py A B [--out J] [--md M]

A and B are infer_ladder.py run directories. For the iterations present in both
``progress.csv`` traces it reports whether the traces are identical (logz, remaining dlogz,
cumulative ncall, logl_min compared as exact float reprs: same-seed same-sampler runs of two
implementations are deterministic replicas only if these agree), the first divergent row,
and the throughput of each run: evaluations per second, iterations per second and -log X per
second over the common window, plus the wall time each run needed to reach 25/50/75/100 %
of the common last iteration. Refuses (exit 2) runs with different rung, sampler, inputs or
matched settings. Informational: never a parity criterion.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

MATCHED = ("sampler", "nlive", "dlogz", "seed", "max_samples", "tinyns_preset", "sampler_preflight",
           "prior_transform_dispatch", "checkpointing", "sel_batch_size", "pe_event_block", "guard",
           "max_likelihood_variance")


def load(d):
    rec = json.load(open(os.path.join(d, "record.json")))
    rows = []
    p = os.path.join(d, "progress.csv")
    if os.path.isfile(p):
        with open(p) as f:
            for r in csv.DictReader(f):
                if r["phase"] == "main":
                    rows.append(r)
    return rec, rows


def f(x):
    return None if x in ("", None) else float(x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("A")
    ap.add_argument("B")
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    ra, pa = load(a.A)
    rb, pb = load(a.B)
    errs = []
    if ra["rung"]["rung"] != rb["rung"]["rung"]:
        errs.append("rung differs")
    for k in MATCHED:
        if ra["settings"]["requested"].get(k) != rb["settings"]["requested"].get(k):
            errs.append(f"setting {k} differs")
    for k in ("pe", "sel"):
        if ra["inputs"][k].get("sha256") != rb["inputs"][k].get("sha256"):
            errs.append(f"input {k} sha256 differs")
    if errs:
        print("REFUSED: " + "; ".join(errs), file=sys.stderr)
        return 2
    ia = {int(r["iteration"]): r for r in pa}
    ib = {int(r["iteration"]): r for r in pb}
    common = sorted(set(ia) & set(ib))
    first_div = None
    for it in common:
        x, y = ia[it], ib[it]
        diff = [k for k in ("logz", "dlogz_remaining", "ncall_cum", "logl_min") if x[k] != y[k]]
        if diff:
            first_div = {"iteration": it, "fields": diff, "A": {k: x[k] for k in diff}, "B": {k: y[k] for k in diff}}
            break
    ncall_identical = all(ia[it]["ncall_cum"] == ib[it]["ncall_cum"] for it in common)
    max_rel = {}
    for k in ("logz", "logl_min"):
        m = 0.0
        for it in common:
            x, y = f(ia[it][k]), f(ib[it][k])
            if x is None or y is None or x != x or y != y:
                continue
            if x != y:
                m = max(m, abs(y - x) / max(abs(x), 1e-300))
        max_rel[k] = m
    only_a = sorted(set(ia) - set(ib))
    only_b = sorted(set(ib) - set(ia))

    def perf(rows_by_it, rec):
        if len(common) < 2:
            return {}
        r0, r1 = rows_by_it[common[0]], rows_by_it[common[-1]]
        dt = f(r1["t_since_sampling_s"]) - f(r0["t_since_sampling_s"])
        out = {"window_iterations": [common[0], common[-1]], "seconds": dt,
               "iterations_per_s": (common[-1] - common[0]) / dt if dt > 0 else None,
               "evals_per_s": ((f(r1["ncall_cum"]) - f(r0["ncall_cum"])) / dt
                               if dt > 0 and r0["ncall_cum"] and r1["ncall_cum"] else None),
               "neg_log_volume_per_s": ((f(r0["log_volume"]) - f(r1["log_volume"])) / dt if dt > 0 else None),
               "t_reach_s": {}}
        for frac in (0.25, 0.5, 0.75, 1.0):
            target = common[0] + frac * (common[-1] - common[0])
            it = next(i for i in common if i >= target)
            out["t_reach_s"][str(frac)] = f(rows_by_it[it]["t_since_sampling_s"])
        lc = rec.get("likelihood_calls") or {}
        out.update(status=rec["status"], n_like_evals=lc.get("n_like_evals"),
                   evals_per_s_sampling=lc.get("evals_per_s_sampling"),
                   t_sampling_s=(rec.get("timing") or {}).get("t_sampling_s"),
                   last_iteration=int(rec["progress"].get("last_main_iteration") or 0),
                   last_dlogz_remaining=rec["progress"].get("last_dlogz_remaining"))
        return out

    PA, PB = perf(ia, ra), perf(ib, rb)
    ratio = {}
    for k in ("iterations_per_s", "evals_per_s", "neg_log_volume_per_s"):
        if PA.get(k) and PB.get(k):
            ratio[k] = PB[k] / PA[k]
    res = {"schema": "darksirens-infer-ladder-progress-compare/1",
           "A": {"dir": os.path.abspath(a.A), "label": ra["label"], "impl": ra["implementation"], "arm": ra.get("arm"),
                 "status": ra["status"]},
           "B": {"dir": os.path.abspath(a.B), "label": rb["label"], "impl": rb["implementation"], "arm": rb.get("arm"),
                 "status": rb["status"]},
           "rung": ra["rung"]["rung"], "sampler": ra["settings"]["requested"]["sampler"],
           "n_common_rows": len(common), "rows_only_in_A": len(only_a), "rows_only_in_B": len(only_b),
           "traces_identical_on_common_rows": first_div is None and len(common) > 0,
           "first_divergence": first_div,
           "ncall_cum_identical_on_common_rows": ncall_identical,
           "max_rel_diff_on_common_rows": max_rel,
           "performance": {"A": PA, "B": PB, "ratio_B_over_A": ratio},
           "note": "integration / throughput check; not a parity criterion"}
    js = json.dumps(res, indent=1, default=str)
    if a.out:
        open(a.out, "w").write(js)
    if a.md:
        L = [f"# progress compare: {res['A']['label']} vs {res['B']['label']}", "",
             f"* rung {res['rung']}, sampler {res['sampler']}; status A {res['A']['status']}, B {res['B']['status']}",
             f"* common rows {len(common)} (only A {len(only_a)}, only B {len(only_b)}); traces identical on "
             f"common rows: {res['traces_identical_on_common_rows']}; first divergence: {first_div}",
             f"* cumulative ncall identical on common rows: {ncall_identical}; max relative difference "
             f"logz {max_rel['logz']:.3g}, logl_min {max_rel['logl_min']:.3g}",
             "", "| metric | A | B | B/A |", "|---|---|---|---|"]
        for k in ("iterations_per_s", "evals_per_s", "neg_log_volume_per_s", "seconds"):
            L.append(f"| {k} | {PA.get(k)} | {PB.get(k)} | {ratio.get(k)} |")
        open(a.md, "w").write("\n".join(L) + "\n")
    print(f"common={len(common)} identical={res['traces_identical_on_common_rows']} "
          f"ncall_identical={ncall_identical} max_rel={max_rel} ratio={ratio}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
