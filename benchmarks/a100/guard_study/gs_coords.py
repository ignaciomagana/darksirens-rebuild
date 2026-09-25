#!/usr/bin/env python3
"""Guard study (GS) coordinate files in the harness format (schema darksirens-bench-coords/1,
read by bench_fixed_theta.py: plan, names = the plan's sampled labels, seed, values_hex,
kinds, repeat_of; coords_digest computed exactly as make_coords.py does). numpy only.

    # rung-1 wall map: H0 on 2.5-wide bin midpoints over the prior [20, 140] + the centre
    python gs_coords.py h0grid --seed 20260924 --step 2.5 --out COORDS.json
    # posterior means of finished infer_ladder runs (after the inference phase)
    python gs_coords.py postmean --rung 1 --seed 20260924 --runs RUN_DIR ... --out COORDS.json

Row 0 is the rung / plan centre (H0 = 67.74, GWTC-5 preset population) and the last row
repeats it (the harness repeat-consistency check). Posterior mean = the mean of the
equal-weight samples in each run's posterior.npz (the samples compare_posteriors.py uses).
Rung 1 maps to plan spectral_H0_gwtc5 (H0 sampled, population fixed at the preset);
rung 3 maps to plan spectral_full_gwtc5 with H0 = 67.74 and every population parameter
other than the three sampled ones at the preset: the decoded full vector is then the one
rung 3's likelihood sees.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import plans  # noqa: E402

SCHEMA = "darksirens-bench-coords/1"
RUNG_PLAN = {"1": "spectral_H0_gwtc5", "3": "spectral_full_gwtc5"}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _body(plan_name, seed, rows, kinds, extra):
    plan = plans.resolve_plan(plan_name)
    names = plan["sampled"]
    values = np.asarray(rows, dtype=np.float64)
    lo = np.asarray([plan["sampled_bounds"][k][0] for k in names])
    hi = np.asarray([plan["sampled_bounds"][k][1] for k in names])
    if np.any(values < lo) or np.any(values > hi):
        raise ValueError("a coordinate lies outside the plan's prior box")
    n = len(rows)
    body = {
        "schema": SCHEMA, "plan": plan_name, "population_model": plan["population_model"],
        "seed": int(seed), "n_distinct": n - 1, "names": list(names),
        "values": values.tolist(), "values_hex": [[float(x).hex() for x in r] for r in values],
        "kinds": kinds, "repeat_of": {str(n - 1): 0}, "fixed": plan["fixed"],
        "generator": {"script": os.path.abspath(__file__), "numpy": np.__version__}, **extra,
    }
    body["coords_digest"] = hashlib.sha256(json.dumps(
        {"names": body["names"], "values_hex": body["values_hex"]}, sort_keys=True).encode()).hexdigest()
    return body


def centre_row(plan_name):
    plan = plans.resolve_plan(plan_name)
    pre = plans.POPULATION_PRESETS["gwtc5"]
    vals = dict(plan["fiducials"])
    vals["H0"] = pre["H0"]
    return [vals[k] for k in plan["sampled"]]


def cmd_h0grid(a):
    plan_name = "spectral_H0_gwtc5"
    lo, hi = plans.H0_BOUNDS
    nb = int(round((hi - lo) / a.step))
    if abs(nb * a.step - (hi - lo)) > 1e-9:
        raise SystemExit("--step must divide the H0 prior width")
    mids = [lo + (k + 0.5) * a.step for k in range(nb)]
    c = centre_row(plan_name)
    rows = [c] + [[m] for m in mids] + [c]
    kinds = ["centre"] + ["h0_grid_midpoint"] * nb + ["repeat"]
    body = _body(plan_name, a.seed, rows, kinds, {"grid": {"lo": lo, "hi": hi, "step": a.step,
                                                        "n_bins": nb, "rule": "bin midpoints"}})
    _write(a.out, body)


def cmd_postmean(a):
    plan_name = RUNG_PLAN[str(a.rung)]
    plan = plans.resolve_plan(plan_name)
    names = plan["sampled"]
    c = centre_row(plan_name)
    rows, kinds, meta = [c], ["centre"], {}
    for d in a.runs:
        rec_p, npz = os.path.join(d, "record.json"), os.path.join(d, "posterior.npz")
        if not (os.path.isfile(rec_p) and os.path.isfile(npz)):
            print(f"[skip] {d}: no record.json + posterior.npz (run not ok)", file=sys.stderr)
            continue
        with open(rec_p) as f:
            rec = json.load(f)
        if str(rec["rung"]["rung"]) != str(a.rung):
            raise SystemExit(f"{d}: rung {rec['rung']['rung']} != --rung {a.rung}")
        with np.load(npz, allow_pickle=False) as z:
            labels = [str(x) for x in z["labels"]]
            mean = {lab: float(np.mean(z["samples"][:, i])) for i, lab in enumerate(labels)}
        row = list(c)
        for lab, m in mean.items():
            if lab not in names:
                raise SystemExit(f"{d}: posterior label {lab!r} is not sampled in {plan_name}")
            row[names.index(lab)] = m
        s = rec["settings"]["requested"]
        lab = rec["label"]
        rows.append(row)
        kinds.append(f"posterior_mean:{lab}")
        meta[lab] = {"dir": os.path.abspath(d), "guard": s.get("guard"), "cap": s.get("max_likelihood_variance"),
                     "implementation": rec.get("implementation"), "arm": rec.get("arm"),
                     "status": rec.get("status"), "posterior_sha256": _sha256(npz),
                     "mean": mean, "mean_hex": {k: float(v).hex() for k, v in mean.items()}}
    if len(rows) == 1:
        raise SystemExit("no finished run with a posterior")
    rows.append(c)
    kinds.append("repeat")
    body = _body(plan_name, a.seed, rows, kinds, {"rung": str(a.rung), "posterior_mean_runs": meta,
                                                  "posterior_mean_rule": "mean of the equal-weight samples in posterior.npz"})
    _write(a.out, body)


def _write(path, body):
    if os.path.exists(path):
        raise SystemExit(f"{path} exists: refusing to overwrite a coordinate file")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(body, f, indent=1)
        f.write("\n")
    print(f"wrote {path}: plan={body['plan']} rows={len(body['values'])} digest={body['coords_digest'][:16]}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("h0grid"); g.add_argument("--seed", type=int, required=True)
    g.add_argument("--step", type=float, default=2.5); g.add_argument("--out", required=True)
    p = sub.add_parser("postmean"); p.add_argument("--rung", required=True, choices=sorted(RUNG_PLAN))
    p.add_argument("--seed", type=int, required=True); p.add_argument("--runs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return {"h0grid": cmd_h0grid, "postmean": cmd_postmean}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
