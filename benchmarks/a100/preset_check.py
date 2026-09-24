#!/usr/bin/env python3
"""Load a fixed-population preset from BOTH implementations and assert it is identical.

    python preset_check.py check --preset gwtc5 --legacy-python PY --core-python PY [--out J]
    python preset_check.py dump --impl legacy|core --preset gwtc5      (inside one env)

``dump`` runs inside one implementation's environment (CPU, JAX_PLATFORMS=cpu) and
prints, as float hex, the preset vector that implementation fixes, the model's labels,
prior bounds, prior kinds and declared joint constraint groups:

* legacy (c042527): ``registry.get_fixed_population_params(model, fiducials=S)`` for both
  fiducial sets S (the vector ``--pop_model <model> --fix_population true`` fixes);
* core (88004d9): ``ds.model(cosmology=ds.Cosmology(), population=ds.Population(model,
  fixed="gwtc5")).parameters.fixed_population`` (the public preset spelling), plus the
  registry's ``get_fixed_population_params`` for both sets.

``check`` runs both dumps in subprocesses and compares every value bit for bit with each
other AND with ``plans.py`` (``POPULATION_MODELS[model]``). Any difference raises
``PresetMismatch`` whose message is the full diff; the CLI exits 1 and prints it.
Imports neither implementation itself.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plans  # noqa: E402

REMOTE_ROOT = "/media/volume/tbs/darksirens_benchmark"
DEFAULT_PY = {"legacy": f"{REMOTE_ROOT}/envs/env_legacy/bin/python",
              "core": f"{REMOTE_ROOT}/envs/env_core/bin/python"}


class PresetMismatch(RuntimeError):
    pass


def _hex(xs):
    return [float(x).hex() for x in xs]


def dump(impl, preset):
    import numpy as np

    pre = plans.POPULATION_PRESETS[preset]
    model = pre["population_model"]
    out = {"impl": impl, "preset": preset, "population_model": model}
    if impl == "legacy":
        import darksirens
        from darksirens.gw.populations import get_model, pop_model_prior_parser
        from darksirens.gw.populations.registry import get_fixed_population_params

        out["package_file"] = darksirens.__file__
        vecs = {s: get_fixed_population_params(model, fiducials=s) for s in ("legacy", "in_prior_v2")}
        out["preset_vector_source"] = ("darksirens.gw.populations.registry."
                                       "get_fixed_population_params(model, fiducials='legacy'), the "
                                       "vector --pop_model <model> --fix_population true fixes")
        out["preset_vector_hex"] = _hex(np.asarray(vecs["legacy"], dtype=np.float64))
    else:
        import darksirens as ds
        from darksirens.population import get_fixed_population_params, get_model, pop_model_prior_parser

        out["package_file"] = ds.__file__
        P = ds.Population(model, fixed=pre["core_population_fixed"])
        an = ds.model(cosmology=ds.Cosmology(), population=P)
        vecs = {s: get_fixed_population_params(model, fiducials=s) for s in ("legacy", "in_prior_v2")}
        out["core_population"] = {"name": P.name, "fixed": P.fixed, "model_name": P.model_name,
                                  "fiducial_set": P.fiducial_set}
        out["preset_vector_source"] = (f"ds.model(population=ds.Population({model!r}, fixed="
                                       f"{pre['core_population_fixed']!r})).parameters.fixed_population")
        out["preset_vector_hex"] = _hex(np.asarray(an.parameters.fixed_population, dtype=np.float64))
    lo, hi, labels, kinds, _latex = pop_model_prior_parser(model)
    out["registry_legacy_set_hex"] = _hex(np.asarray(vecs["legacy"], dtype=np.float64))
    out["registry_in_prior_v2_set_hex"] = _hex(np.asarray(vecs["in_prior_v2"], dtype=np.float64))
    out["labels"] = [str(x) for x in labels]
    out["lower_hex"] = _hex(np.asarray(lo, dtype=np.float64))
    out["upper_hex"] = _hex(np.asarray(hi, dtype=np.float64))
    out["prior_kinds"] = [[str(k[0])] + [None if v is None else float(v) for v in k[1:]] for k in kinds]
    groups = getattr(get_model(model), "constraint_groups", None) or ()
    out["constraint_groups"] = [[str(g[0]), [str(x) for x in g[1]]] for g in groups]
    return out


def _run_dump(py, impl, preset):
    env = dict(os.environ, JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    r = subprocess.run([py, os.path.abspath(__file__), "dump", "--impl", impl, "--preset", preset],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise PresetMismatch(f"{impl} preset dump failed (rc {r.returncode}) with {py}:\n"
                             f"{r.stderr[-3000:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def check(preset, legacy_python=None, core_python=None):
    """Both implementations' preset == each other == plans.py, bit for bit; else raise."""
    pre = plans.POPULATION_PRESETS[preset]
    model = pre["population_model"]
    spec = plans.POPULATION_MODELS[model]
    want = {
        "preset_vector_hex": _hex(spec["fiducials"]),
        "registry_legacy_set_hex": _hex(spec["fiducials"]),
        "registry_in_prior_v2_set_hex": _hex(spec["fiducials"]),
        "labels": list(spec["labels"]),
        "lower_hex": _hex(spec["lower"]),
        "upper_hex": _hex(spec["upper"]),
        "prior_kinds": [[str(k[0])] + [None if v is None else float(v) for v in k[1:]]
                        for k in spec["prior_kinds"]],
        "constraint_groups": [[g[0], list(g[1])] for g in spec.get("constraint_groups", [])],
    }
    pys = {"legacy": legacy_python or os.environ.get("DS_LEGACY_PYTHON") or DEFAULT_PY["legacy"],
           "core": core_python or os.environ.get("DS_CORE_PYTHON") or DEFAULT_PY["core"]}
    got = {impl: _run_dump(pys[impl], impl, preset) for impl in ("legacy", "core")}
    diffs = []
    for key, w in want.items():
        for impl in ("legacy", "core"):
            g = got[impl].get(key)
            if g != w:
                if isinstance(w, list) and isinstance(g, list) and len(w) == len(g):
                    idx = [i for i, (a, b) in enumerate(zip(w, g)) if a != b]
                    detail = "; ".join(f"[{i}] {spec['labels'][i] if i < len(spec['labels']) else i}: "
                                       f"plans {w[i]!r} vs {impl} {g[i]!r}" for i in idx)
                else:
                    detail = f"plans {w!r} vs {impl} {g!r}"
                diffs.append(f"{key}: {detail}")
        if got["legacy"].get(key) != got["core"].get(key):
            diffs.append(f"{key}: legacy {got['legacy'].get(key)!r} != core {got['core'].get(key)!r}")
    evidence = {
        "preset": preset,
        "population_model": model,
        "identical": not diffs,
        "fields_compared": list(want),
        "n_values": len(spec["fiducials"]),
        "preset_vector_hex": got["core"]["preset_vector_hex"],
        "pythons": pys,
        "dumps": got,
        "diffs": diffs,
    }
    if diffs:
        raise PresetMismatch(f"preset {preset!r} differs between the implementations / plans.py:\n  "
                             + "\n  ".join(diffs))
    return evidence


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("check", "dump"))
    ap.add_argument("--preset", default="gwtc5", choices=sorted(plans.POPULATION_PRESETS))
    ap.add_argument("--impl", choices=("legacy", "core"))
    ap.add_argument("--legacy-python", default=None)
    ap.add_argument("--core-python", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.what == "dump":
        if not a.impl:
            ap.error("dump needs --impl")
        print(json.dumps(dump(a.impl, a.preset)))
        return 0
    try:
        ev = check(a.preset, a.legacy_python, a.core_python)
    except PresetMismatch as exc:
        print(f"PRESET MISMATCH: {exc}", file=sys.stderr)
        return 1
    if a.out:
        with open(a.out, "w") as f:
            json.dump(ev, f, indent=1)
    print(f"preset {a.preset}: identical in legacy, core and plans.py ({ev['n_values']} values, "
          f"{len(ev['fields_compared'])} fields)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
