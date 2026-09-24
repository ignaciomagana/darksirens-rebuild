#!/usr/bin/env python3
"""Write the fixed coordinates of one plan as named parameter values.

    python make_coords.py --plan spectral_full --seed 20260924 --n 8 --out coords.json

Layout (``n`` distinct coordinates plus one repeat, ``n + 1`` rows):

* row 0: the fiducial point (H0 = 67.74 when sampled, population fiducials);
* rows 1 .. n-1: prior-uniform draws inside the plan's prior box, from
  ``numpy.random.default_rng(seed)``: one ``rng.random(ndim)`` vector per row,
  mapped to ``lower + u * (upper - lower)``. Every sampled prior in these plans
  is uniform or beta(1, 1) (itself uniform on [0, 1]), so a box draw is a prior
  draw. No joint-constraint rejection is applied: the likelihood is evaluated
  wherever the sampler could propose.
* row n: an exact copy of row 0 (the repeat-consistency check).

Centred layout (Gate 1 supplement M5), ``--center gwtc5 --spread 0.05``:

* the plan must carry ``population_preset == "gwtc5"`` (plans.py); before anything is
  written, ``preset_check.check`` loads the GWTC-5 fixed-population preset from BOTH
  implementations (legacy / core pythons from ``--legacy-python`` / ``--core-python``, or
  ``DS_LEGACY_PYTHON`` / ``DS_CORE_PYTHON``, or the campaign envs) and asserts every value
  identical to each other and to plans.py; any difference aborts with the diff;
* row 0 (the centre): H0 = 67.74 and the preset vector for every sampled population
  parameter; fixed parameters take the preset values (``plan["fixed"]``);
* rows 1 .. n-1: prior-uniform draws inside ``centre +- spread * (upper - lower)``
  intersected with the prior box, from the same ``default_rng(seed).random(ndim)`` stream;
  a draw outside a joint constraint group the model declares (simplex: sum <= 1;
  conditional_upper: x_i <= x_j) is outside the prior and is redrawn; the number of
  rejected draws is recorded;
* row n: the repeat of row 0.

Needs only numpy; imports neither implementation (the preset check runs them in
subprocesses).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plans  # noqa: E402

SCHEMA = "darksirens-bench-coords/1"


def _violates(groups, names, x):
    """True when x breaks a declared joint constraint among the SAMPLED names."""
    for kind, members in groups:
        if not all(m in names for m in members):
            continue
        v = [x[names.index(m)] for m in members]
        if kind == "simplex" and sum(v) > 1.0:
            return True
        if kind == "conditional_upper" and v[0] > v[1]:
            return True
        if kind == "ordered_le" and v[0] > v[1]:
            return True
    return False


def make_coords(plan_name: str, seed: int, n: int, center: str | None = None,
                spread: float | None = None, legacy_python: str | None = None,
                core_python: str | None = None) -> dict:
    if n < 1:
        raise ValueError("--n must be >= 1 (the fiducial point is row 0)")
    plan = plans.resolve_plan(plan_name)
    if center is not None:
        return _make_centred(plan, plan_name, seed, n, center, spread, legacy_python, core_python)
    names = plan["sampled"]
    for name in names:
        kind = plan["sampled_prior_kinds"][name]
        if not (kind[0] == "uniform" or (kind[0] == "beta" and kind[1] == 1.0 and kind[2] == 1.0)):
            raise ValueError(f"{name}: prior kind {kind} is not box-uniform")
    lo = np.asarray([plan["sampled_bounds"][k][0] for k in names], dtype=np.float64)
    hi = np.asarray([plan["sampled_bounds"][k][1] for k in names], dtype=np.float64)
    fid = np.asarray([plan["fiducials"][k] for k in names], dtype=np.float64)
    if np.any(fid < lo) or np.any(fid > hi):
        raise ValueError("a fiducial lies outside its prior box")

    rng = np.random.default_rng(seed)
    rows = [fid]
    for _ in range(n - 1):
        u = rng.random(len(names))
        rows.append(lo + u * (hi - lo))
    rows.append(fid.copy())
    values = np.asarray(rows, dtype=np.float64)

    body = {
        "schema": SCHEMA,
        "plan": plan_name,
        "population_model": plan["population_model"],
        "seed": int(seed),
        "n_distinct": int(n),
        "names": list(names),
        "values": values.tolist(),
        "values_hex": [[float(x).hex() for x in row] for row in values],
        "kinds": ["fiducial"] + ["prior_uniform"] * (n - 1) + ["repeat"],
        "repeat_of": {str(n): 0},
        "fixed": plan["fixed"],
        "generator": {
            "rng": "numpy.random.default_rng(seed).random(ndim) per draw",
            "numpy": np.__version__,
            "script": os.path.abspath(__file__),
        },
    }
    digest = hashlib.sha256(
        json.dumps({"names": body["names"], "values_hex": body["values_hex"]},
                   sort_keys=True).encode()
    ).hexdigest()
    body["coords_digest"] = digest
    return body


def _make_centred(plan, plan_name, seed, n, center, spread, legacy_python, core_python):
    import preset_check

    if center not in plans.POPULATION_PRESETS:
        raise ValueError(f"--center {center!r}: known presets {sorted(plans.POPULATION_PRESETS)}")
    if plan.get("population_preset") != center:
        raise ValueError(f"--center {center!r} needs a plan whose population_preset is {center!r}; "
                         f"{plan_name!r} has {plan.get('population_preset')!r}")
    if spread is None or not (0.0 < spread <= 0.5):
        raise ValueError("--spread must be in (0, 0.5] (fraction of each prior width)")
    # Fails loudly (PresetMismatch with the diff) unless both implementations ship the
    # identical preset and it equals plans.py.
    evidence = preset_check.check(center, legacy_python, core_python)
    pre = plans.POPULATION_PRESETS[center]
    names = plan["sampled"]
    for name in names:
        kind = plan["sampled_prior_kinds"][name]
        if not (kind[0] == "uniform" or (kind[0] == "beta" and kind[1] == 1.0 and kind[2] == 1.0)):
            raise ValueError(f"{name}: prior kind {kind} is not box-uniform")
    lo = np.asarray([plan["sampled_bounds"][k][0] for k in names], dtype=np.float64)
    hi = np.asarray([plan["sampled_bounds"][k][1] for k in names], dtype=np.float64)
    centre_vals = dict(plan["fiducials"])  # population fiducials of this model = the preset
    centre_vals["H0"] = pre["H0"]
    ctr = np.asarray([centre_vals[k] for k in names], dtype=np.float64)
    pop_hex = [float(x).hex() for x in plans.POPULATION_MODELS[pre["population_model"]]["fiducials"]]
    if pop_hex != evidence["preset_vector_hex"]:
        raise preset_check.PresetMismatch("plans.py fiducials != the checked preset vector")
    if np.any(ctr < lo) or np.any(ctr > hi):
        raise ValueError("the centre lies outside the prior box")
    width = hi - lo
    blo = np.maximum(lo, ctr - spread * width)
    bhi = np.minimum(hi, ctr + spread * width)
    groups = plan.get("population_constraint_groups") or []
    if _violates(groups, names, ctr):
        raise ValueError("the centre violates a declared joint constraint")
    rng = np.random.default_rng(seed)
    rows, rejected = [ctr], 0
    while len(rows) < n:
        x = blo + rng.random(len(names)) * (bhi - blo)
        if _violates(groups, names, x):
            rejected += 1
            if rejected > 10000:
                raise RuntimeError("could not draw inside the joint constraints")
            continue
        rows.append(x)
    rows.append(ctr.copy())
    values = np.asarray(rows, dtype=np.float64)
    body = {
        "schema": SCHEMA,
        "plan": plan_name,
        "population_model": plan["population_model"],
        "seed": int(seed),
        "n_distinct": int(n),
        "names": list(names),
        "values": values.tolist(),
        "values_hex": [[float(x).hex() for x in row] for row in values],
        "kinds": ["centre"] + ["prior_uniform_in_box"] * (n - 1) + ["repeat"],
        "repeat_of": {str(n): 0},
        "fixed": plan["fixed"],
        "centre": {
            "preset": center,
            "spread_fraction_of_prior_width": float(spread),
            "centre_hex": [float(x).hex() for x in ctr],
            "box_lower_hex": [float(x).hex() for x in blo],
            "box_upper_hex": [float(x).hex() for x in bhi],
            "box_lower": blo.tolist(),
            "box_upper": bhi.tolist(),
            "joint_constraint_groups": groups,
            "rejected_draws": int(rejected),
            "preset_check": {k: evidence[k] for k in ("identical", "fields_compared", "n_values",
                                                      "preset_vector_hex", "pythons", "diffs")},
            "preset_dumps": evidence["dumps"],
        },
        "generator": {
            "rng": ("numpy.random.default_rng(seed).random(ndim) per draw, mapped into the "
                    "centred box; draws outside a declared joint constraint are redrawn"),
            "numpy": np.__version__,
            "script": os.path.abspath(__file__),
        },
    }
    body["coords_digest"] = hashlib.sha256(
        json.dumps({"names": body["names"], "values_hex": body["values_hex"]},
                   sort_keys=True).encode()).hexdigest()
    return body


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True, choices=sorted(plans.PLANS))
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument("--n", type=int, default=8, help="distinct coordinates incl. the fiducial (default 8)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--center", default=None, choices=sorted(plans.POPULATION_PRESETS),
                    help="centre row 0 on H0 = 67.74 + this fixed-population preset (checked in "
                         "both implementations) and draw the other rows inside +-spread")
    ap.add_argument("--spread", type=float, default=None,
                    help="with --center: half-width of the draw box as a fraction of each prior width")
    ap.add_argument("--legacy-python", default=None, help="legacy env python for the preset check")
    ap.add_argument("--core-python", default=None, help="core env python for the preset check")
    a = ap.parse_args(argv)
    if (a.center is None) != (a.spread is None):
        ap.error("--center and --spread go together")
    try:
        body = make_coords(a.plan, a.seed, a.n, a.center, a.spread, a.legacy_python, a.core_python)
    except Exception as exc:
        print(f"make_coords: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    body["command_line"] = [sys.executable] + list(sys.argv)
    with open(a.out, "w") as f:
        json.dump(body, f, indent=1)
        f.write("\n")
    print(f"wrote {a.out}: plan={a.plan} seed={a.seed} rows={len(body['values'])} "
          f"names={body['names']} digest={body['coords_digest'][:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
