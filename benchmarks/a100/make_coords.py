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

Needs only numpy; imports neither implementation.
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


def make_coords(plan_name: str, seed: int, n: int) -> dict:
    if n < 1:
        raise ValueError("--n must be >= 1 (the fiducial point is row 0)")
    plan = plans.resolve_plan(plan_name)
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True, choices=sorted(plans.PLANS))
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument("--n", type=int, default=8, help="distinct coordinates incl. the fiducial (default 8)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    body = make_coords(a.plan, a.seed, a.n)
    body["command_line"] = [sys.executable] + list(sys.argv)
    with open(a.out, "w") as f:
        json.dump(body, f, indent=1)
        f.write("\n")
    print(f"wrote {a.out}: plan={a.plan} seed={a.seed} rows={len(body['values'])} "
          f"names={body['names']} digest={body['coords_digest'][:16]}")


if __name__ == "__main__":
    main()
