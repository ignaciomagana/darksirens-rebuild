"""Parameter plans of the fixed-coordinate benchmark (Fable-owned target).

This module is the ONE place where the plans, the population model, its
parameter names, prior bounds and fiducials are written down. It imports
neither implementation. ``bench_fixed_theta.py`` asserts at runtime that the
implementation under test reports exactly these names, bounds and fiducials
(bitwise, via ``float.hex``) and refuses to run otherwise.

Target (verbatim from the campaign brief):

* ordinary spectral plan: H0 sampled on [20, 140]; Om0 = 0.3075, w0 = -1,
  wa = 0 fixed; plus the population block that is identical in both
  implementations (default model, default priors, identical fiducials);
* ``spectral_H0``: H0 sampled, population fixed at its fiducials;
* ``spectral_pop``: population sampled, H0 fixed at the fiducial both
  implementations use (67.74, recorded in ``H0_FIDUCIAL``);
* ``spectral_joint_small``: H0 plus the first three population parameters in
  plan order, the rest of the population fixed at its fiducials;
* ``spectral_full``: H0 plus the full population block.

``spectral_full_component`` is NOT part of the ordinary target. It is the
Product-B (gwcat 2.1, ``parameter_space=component``) variant of
``spectral_full``: the ordinary chi_eff model is refused by both readers on
component-basis data, so the only model both implementations can evaluate
there is ``gwtc3_plpeak_component_spin`` (see README.md, "Product B").

Sources of the numbers (read and printed from both implementations):

* default population model ``powerlaw+peak``: legacy CLI default
  ``--pop_model`` (legacy ``darksirens/cli/inference.py:1300-1301``); core
  ``ds.Population`` has no default name and the harness passes it explicitly.
* H0 fiducial 67.74: legacy ``darksirens/core/constants.py:12``; core
  ``src/darksirens/cosmology/parameters.py:7``.
* H0 bounds [20, 140] and Om0/w0/wa fixed values: core ``ds.Cosmology()``
  default (``src/darksirens/_specs.py:103-106``). Legacy is configured to it
  with ``--prior_overrides '{"H0": [20, 140]}'``, ``--fix_de true`` and
  ``--fixed_parameter_values '{"Om0": 0.3075}'`` (its CLI default samples
  H0 in [20, 120], Om0, w0 and wa).
* population labels, bounds, prior kinds and the ``legacy`` fiducial set:
  ``pop_model_prior_parser`` / ``get_fixed_population_params`` (legacy
  ``darksirens/gw/populations/registry.py``; core
  ``src/darksirens/population/registry.py``), identical bit for bit.
"""

from __future__ import annotations

import copy

H0_LABEL = "H0"
H0_BOUNDS = (20.0, 140.0)
H0_FIDUCIAL = 67.74
FIXED_COSMOLOGY = {"Om0": 0.3075, "w0": -1.0, "wa": 0.0}
COSMOLOGY_ORDER = ("H0", "Om0", "w0", "wa")

#: The fiducial set both implementations resolve for a fixed population
#: (legacy ``--population_fiducials`` default; core ``Population(fixed=True)``).
FIDUCIAL_SET = "legacy"

DEFAULT_POPULATION_MODEL = "powerlaw+peak"

POPULATION_MODELS = {
    "powerlaw+peak": {
        "shared_beta": True,
        "shared_spin": True,
        "shared_gamma": True,
        "labels": [
            "$v_1$",
            "$\\alpha_{\\rm PL}$",
            "$m_{\\min,\\rm PL}$",
            "$m_{\\max,\\rm PL}$",
            "$\\delta m_{\\min,\\rm PL}$",
            "$\\delta m_{\\max,\\rm PL}$",
            "$\\mu_{\\rm G}$",
            "$\\sigma_{\\rm G}$",
            "$\\beta$",
            "$\\mu_\\chi$",
            "$\\sigma_\\chi$",
            "$\\gamma$",
        ],
        "lower": [0.0, -4.0, 2.0, 50.0, 0.01, 0.01, 20.0, 1.0, -2.0, -1.0, 0.01, -10.0],
        "upper": [1.0, 6.0, 10.0, 100.0, 10.0, 20.0, 50.0, 10.0, 7.0, 1.0, 1.0, 10.0],
        # beta(1, 1) on [0, 1] is the uniform density, so a box-uniform draw is
        # a prior draw for every entry.
        "prior_kinds": [["beta", 1.0, 1.0]] + [["uniform", None, None]] * 11,
        "fiducials": [0.1, 2.3, 5.0, 80.0, 3.0, 10.0, 35.0, 5.0, 1.0, 0.0, 0.1, 2.5],
    },
    "gwtc3_plpeak_component_spin": {
        "shared_beta": True,
        "shared_spin": True,
        "shared_gamma": True,
        "labels": [
            "$\\alpha$",
            "$m_{\\min}$",
            "$m_{\\max}$",
            "$\\lambda_{\\rm peak}$",
            "$\\mu_m$",
            "$\\sigma_m$",
            "$\\delta_m$",
            "$\\beta_q$",
            "$\\alpha_\\chi$",
            "$\\beta_\\chi$",
            "$\\zeta_{\\rm spin}$",
            "$\\sigma_t$",
            "$\\gamma$",
        ],
        "lower": [-4.0, 2.0, 30.0, 0.0, 20.0, 1.0, 0.0, -2.0, 1.0, 1.0, 0.0, 0.1, -10.0],
        "upper": [12.0, 10.0, 100.0, 1.0, 50.0, 10.0, 10.0, 7.0, 10.0, 10.0, 1.0, 4.0, 10.0],
        "prior_kinds": [["uniform", None, None]] * 13,
        "fiducials": [3.5, 5.0, 65.0, 0.038, 34.0, 5.5, 4.9, 1.1, 1.6, 4.5, 0.75, 0.9, 2.9],
    },
}

#: ``sample_population``: "none" (population fixed at its fiducials), "all",
#: or an int k = the first k population parameters in plan order.
PLANS = {
    "spectral_H0": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "sample_H0": True,
        "sample_population": "none",
        "target": "ordinary",
    },
    "spectral_pop": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "sample_H0": False,
        "sample_population": "all",
        "target": "ordinary",
    },
    "spectral_joint_small": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "sample_H0": True,
        "sample_population": 3,
        "target": "ordinary",
    },
    "spectral_full": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "sample_H0": True,
        "sample_population": "all",
        "target": "ordinary",
    },
    "spectral_full_component": {
        "population_model": "gwtc3_plpeak_component_spin",
        "sample_H0": True,
        "sample_population": "all",
        "target": "product_b_variant",
    },
}

ORDINARY_PLANS = tuple(k for k, v in PLANS.items() if v["target"] == "ordinary")


def population_spec(model: str) -> dict:
    if model not in POPULATION_MODELS:
        raise KeyError(f"population model {model!r} is not encoded in plans.py")
    return copy.deepcopy(POPULATION_MODELS[model])


def resolve_plan(name: str) -> dict:
    """Expand a plan name into sampled names, bounds, fixed values and fiducials.

    ``full_order`` is H0, Om0, w0, wa followed by the population labels; every
    name in it has a fiducial, and every name is either sampled or fixed.
    """
    if name not in PLANS:
        raise KeyError(f"unknown plan {name!r}; known: {sorted(PLANS)}")
    p = PLANS[name]
    pop = population_spec(p["population_model"])
    labels = pop["labels"]
    k = p["sample_population"]
    if k == "all":
        pop_sampled = list(labels)
    elif k == "none":
        pop_sampled = []
    else:
        pop_sampled = list(labels[: int(k)])

    fiducials = {H0_LABEL: H0_FIDUCIAL, **FIXED_COSMOLOGY}
    fiducials.update(dict(zip(labels, pop["fiducials"])))
    bounds = {H0_LABEL: list(H0_BOUNDS)}
    bounds.update({lab: [lo, hi] for lab, lo, hi in zip(labels, pop["lower"], pop["upper"])})
    kinds = {H0_LABEL: ["uniform", None, None]}
    kinds.update(dict(zip(labels, pop["prior_kinds"])))

    sampled = ([H0_LABEL] if p["sample_H0"] else []) + pop_sampled
    full_order = list(COSMOLOGY_ORDER) + list(labels)
    fixed = {n: fiducials[n] for n in full_order if n not in sampled}
    return {
        "name": name,
        "target": p["target"],
        "population_model": p["population_model"],
        "shared_beta": pop["shared_beta"],
        "shared_spin": pop["shared_spin"],
        "shared_gamma": pop["shared_gamma"],
        "fiducial_set": FIDUCIAL_SET,
        "sample_H0": bool(p["sample_H0"]),
        "sample_population": k,
        "population_labels": list(labels),
        "population_lower": list(pop["lower"]),
        "population_upper": list(pop["upper"]),
        "population_prior_kinds": [list(x) for x in pop["prior_kinds"]],
        "population_fiducials": list(pop["fiducials"]),
        "sampled": sampled,
        "sampled_bounds": {n: bounds[n] for n in sampled},
        "sampled_prior_kinds": {n: kinds[n] for n in sampled},
        "fixed": fixed,
        "fiducials": fiducials,
        "full_order": full_order,
        "H0_bounds": list(H0_BOUNDS),
        "H0_fiducial": H0_FIDUCIAL,
        "fixed_cosmology": dict(FIXED_COSMOLOGY),
    }


def plan_summary(name: str) -> dict:
    """Compact {sampled, fixed, model, fiducials} view (used in reports)."""
    r = resolve_plan(name)
    return {
        "sampled": r["sampled"],
        "fixed": r["fixed"],
        "model": r["population_model"],
        "fiducials": r["fiducials"],
        "H0_bounds": r["H0_bounds"],
    }


if __name__ == "__main__":  # pragma: no cover - convenience printer
    import json
    import sys

    names = sys.argv[1:] or list(PLANS)
    print(json.dumps({n: plan_summary(n) for n in names}, indent=1))
