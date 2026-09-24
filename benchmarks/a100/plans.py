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

Dark-siren target (incomplete-catalog conditional estimand, the only one core
implements; ``--catalog_sky_weighting conditional`` in legacy):

* ``dark_H0``: H0 sampled; population and survey fixed;
* ``dark_pop``: population sampled; H0 = 67.74 and survey fixed;
* ``dark_survey``: ``log10n0``, ``delta``, ``sigma_kde`` sampled; H0 and
  population fixed;
* ``dark_joint_cosmo_pop``: H0 + the first three population parameters; the
  rest of the population and the survey fixed;
* ``dark_joint_cosmo_survey``: H0 + the survey block; population fixed;
* ``dark_full``: H0 + population + survey.

Om0, w0, wa are fixed as in the spectral plans. Survey fiducials: ``log10n0``
= -3 (the fixtures' injected density, n0 = 1e-3 Mpc^-3, from their
``galaxy_density.json`` sidecar; ``dark_fixture.preflight`` asserts that the
fixture carries exactly this value), ``delta`` = 0 and ``sigma_kde`` = 0, the
defaults both implementations share (legacy ``darksirens/core/constants.py``
``SURVEY_PARAMS_FID_BY_NAME``; core ``src/darksirens/catalog/types.py``
``CatalogParameters``; asserted at runtime from each implementation). Survey
prior bounds: legacy ``darksirens/inference/prior.py:290-297`` (``_SURVEY_BLOCK``),
core ``src/darksirens/analysis.py:17-21`` (``_INCOMPLETE_CATALOG_PRIORS``),
identical; ``b_miss`` is inert in legacy without ``--use_lss`` and absent in core.
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
    # GWTC-5 fiducial BPL+2G (Gate 1 supplement M5 only). Labels, bounds, kinds and the
    # published-median preset vector are the registry entry both implementations ship
    # (legacy darksirens/gw/populations/registry.py:460-492, parametric.py:623-670; core
    # src/darksirens/population/registry.py:460-492); every record re-reads them from the
    # implementation under test and asserts them bit for bit (check_registry).
    "gwtc5_fiducial_bpl2peaks": {
        "shared_beta": True,
        "shared_spin": True,
        "shared_gamma": True,
        "labels": [
            "$\\alpha_1$",
            "$\\alpha_2$",
            "$m_{\\rm break}$",
            "$\\mu_1$",
            "$\\sigma_1$",
            "$\\mu_2$",
            "$\\sigma_2$",
            "$m_{1,{\\rm low}}$",
            "$\\delta m_1$",
            "$\\lambda_0$",
            "$\\lambda_1$",
            "$\\beta_q$",
            "$m_{2,{\\rm low}}$",
            "$\\delta m_2$",
            "$\\mu_\\chi$",
            "$\\sigma_\\chi$",
            "$\\gamma$",
        ],
        "lower": [-4.0, -4.0, 20.0, 5.0, 0.0, 25.0, 0.0, 3.0, 0.0, 0.0, 0.0, -2.0, 3.0, 0.0,
                  0.0, 0.005, -10.0],
        "upper": [12.0, 12.0, 50.0, 20.0, 10.0, 60.0, 10.0, 10.0, 10.0, 1.0, 1.0, 7.0, 10.0,
                  10.0, 1.0, 1.0, 10.0],
        "prior_kinds": [["uniform", None, None]] * 17,
        "fiducials": [1.4816, 5.4187, 37.451, 9.9109, 0.7841, 32.3273, 5.7263, 4.4856, 3.5302,
                      0.4004, 0.5457, 1.0438, 3.4633, 4.8128, 0.0633, 0.3654, 2.5439],
        # Joint conditions the model's log_p_pop enforces by rejection and that the
        # samplers' prior transforms map out (legacy inference/prior.py:1382-1420
        # resolve_joint_prior_constraints; model.constraint_groups). make_coords.py
        # rejects box draws outside them; preset_check.py asserts both implementations
        # declare exactly these groups.
        "constraint_groups": [["simplex", ["$\\lambda_0$", "$\\lambda_1$"]],
                              ["conditional_upper", ["$m_{2,{\\rm low}}$", "$m_{1,{\\rm low}}$"]]],
    },
}

#: Fixed-population presets both implementations ship (Gate 1 supplement M5). A plan
#: carrying ``population_preset`` fixes (or centres) its population at the preset's
#: vector, which is the ``fiducials`` of ``population_model`` above; preset_check.py loads
#: the preset from BOTH implementations and asserts every value identical to it.
#: Spelling per implementation: legacy c042527 has no ``--fix_population gwtc5`` value
#: (``--fix_population`` is a bool, ``--population_fiducials`` in {legacy, in_prior_v2});
#: its GWTC-5 preset is the bespoke registry model's own vector, which
#: ``--pop_model gwtc5_fiducial_bpl2peaks --fix_population true`` fixes for either
#: fiducial set (registry.py:882-887 ``_CUSTOM_FIDUCIALS``). Core:
#: ``ds.Population("gwtc5_fiducial_bpl2peaks", fixed="gwtc5")`` (src/darksirens/_specs.py:147-202).
POPULATION_PRESETS = {
    "gwtc5": {
        "population_model": "gwtc5_fiducial_bpl2peaks",
        "H0": 67.74,
        "legacy_cli": ["--pop_model", "gwtc5_fiducial_bpl2peaks", "--fix_population", "true"],
        "core_population_fixed": "gwtc5",
    },
}

#: Survey (incomplete-catalog) block of the dark-siren plans, in plan order.
SURVEY_LABELS = ("log10n0", "delta", "sigma_kde")
SURVEY_BOUNDS = {"log10n0": (-4.0, -1.0), "delta": (-3.0, 3.0), "sigma_kde": (0.0, 0.05)}
SURVEY_PRIOR_KINDS = {n: ["uniform", None, None] for n in SURVEY_LABELS}
#: log10n0 = the fixtures' injected density (n0 = 1e-3 Mpc^-3); delta and
#: sigma_kde = the defaults both implementations share (asserted per record).
SURVEY_FIDUCIALS = {"log10n0": -3.0, "delta": 0.0, "sigma_kde": 0.0}
#: The log10n0 inference prior of each implementation: (lower, upper, source).
#: ``dark_fixture.preflight`` refuses a fixture outside either one; every dark
#: record re-reads both registries and asserts they still equal these bounds.
LOG10N0_PRIOR = {
    "legacy": (-4.0, -1.0, "darksirens/inference/prior.py:290 (_SURVEY_BLOCK log10n0)"),
    "core": (-4.0, -1.0, "src/darksirens/analysis.py:17-18 (_INCOMPLETE_CATALOG_PRIORS)"),
}

#: ``sample_population``: "none" (population fixed at its fiducials), "all",
#: or an int k = the first k population parameters in plan order.
#: ``universe``: "spectral" (no catalog) or "dark" (incomplete-catalog
#: conditional dark sirens, needs ``--catalog``); ``sample_survey``: "none"
#: (survey block fixed at SURVEY_FIDUCIALS) or "all" (dark plans only).
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
    "dark_H0": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "universe": "dark",
        "sample_H0": True,
        "sample_population": "none",
        "sample_survey": "none",
        "target": "dark",
    },
    "dark_pop": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "universe": "dark",
        "sample_H0": False,
        "sample_population": "all",
        "sample_survey": "none",
        "target": "dark",
    },
    "dark_survey": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "universe": "dark",
        "sample_H0": False,
        "sample_population": "none",
        "sample_survey": "all",
        "target": "dark",
    },
    "dark_joint_cosmo_pop": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "universe": "dark",
        "sample_H0": True,
        "sample_population": 3,
        "sample_survey": "none",
        "target": "dark",
    },
    "dark_joint_cosmo_survey": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "universe": "dark",
        "sample_H0": True,
        "sample_population": "none",
        "sample_survey": "all",
        "target": "dark",
    },
    "dark_full": {
        "population_model": DEFAULT_POPULATION_MODEL,
        "universe": "dark",
        "sample_H0": True,
        "sample_population": "all",
        "sample_survey": "all",
        "target": "dark",
    },
    # Gate 1 supplement M5 (spectral, real data, finite totals): the ordinary spectral_H0 /
    # spectral_full layouts on the GWTC-5 BPL+2G model, centred on H0 = 67.74 plus the
    # GWTC-5 fixed-population preset (make_coords.py --center gwtc5 --spread 0.05);
    # spectral_H0_gwtc5 fixes the population AT the preset.
    "spectral_H0_gwtc5": {
        "population_model": "gwtc5_fiducial_bpl2peaks",
        "population_preset": "gwtc5",
        "sample_H0": True,
        "sample_population": "none",
        "target": "m5_gwtc5",
    },
    "spectral_full_gwtc5": {
        "population_model": "gwtc5_fiducial_bpl2peaks",
        "population_preset": "gwtc5",
        "sample_H0": True,
        "sample_population": "all",
        "target": "m5_gwtc5",
    },
}

ORDINARY_PLANS = tuple(k for k, v in PLANS.items() if v["target"] == "ordinary")
DARK_PLANS = tuple(k for k, v in PLANS.items() if v.get("universe") == "dark")


def population_spec(model: str) -> dict:
    if model not in POPULATION_MODELS:
        raise KeyError(f"population model {model!r} is not encoded in plans.py")
    return copy.deepcopy(POPULATION_MODELS[model])


def is_dark(plan) -> bool:
    """True for a resolved dark-siren plan (or a plan name)."""
    if isinstance(plan, str):
        return PLANS[plan].get("universe", "spectral") == "dark"
    return plan.get("universe", "spectral") == "dark"


def resolve_plan(name: str, survey_fixed_override: dict | None = None) -> dict:
    """Expand a plan name into sampled names, bounds, fixed values and fiducials.

    ``full_order`` is H0, Om0, w0, wa followed by the population labels (and,
    for a dark plan, the survey labels); every name in it has a fiducial, and
    every name is either sampled or fixed.

    ``survey_fixed_override`` (dark plans whose survey block is FIXED only)
    replaces fixed survey values, e.g. ``{"log10n0": log10(5e-5)}`` for the
    PR-6a fixed-coordinate density check; the resolved plan records it under
    ``survey_fixed_override`` and the values appear in ``fixed``.
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
    dark = p.get("universe", "spectral") == "dark"
    survey_labels = list(SURVEY_LABELS) if dark else []
    ks = p.get("sample_survey", "none")
    survey_sampled = list(survey_labels) if (dark and ks == "all") else []

    fiducials = {H0_LABEL: H0_FIDUCIAL, **FIXED_COSMOLOGY}
    fiducials.update(dict(zip(labels, pop["fiducials"])))
    bounds = {H0_LABEL: list(H0_BOUNDS)}
    bounds.update({lab: [lo, hi] for lab, lo, hi in zip(labels, pop["lower"], pop["upper"])})
    kinds = {H0_LABEL: ["uniform", None, None]}
    kinds.update(dict(zip(labels, pop["prior_kinds"])))
    if dark:
        fiducials.update({n: SURVEY_FIDUCIALS[n] for n in survey_labels})
        bounds.update({n: list(SURVEY_BOUNDS[n]) for n in survey_labels})
        kinds.update({n: list(SURVEY_PRIOR_KINDS[n]) for n in survey_labels})

    sampled = ([H0_LABEL] if p["sample_H0"] else []) + pop_sampled + survey_sampled
    full_order = list(COSMOLOGY_ORDER) + list(labels) + survey_labels
    fixed = {n: fiducials[n] for n in full_order if n not in sampled}
    if survey_fixed_override:
        if not dark or survey_sampled:
            raise ValueError(f"survey_fixed_override needs a dark plan with a FIXED survey block; "
                             f"{name!r} is not one")
        unknown = set(survey_fixed_override) - set(survey_labels)
        if unknown:
            raise ValueError(f"survey_fixed_override: unknown survey labels {sorted(unknown)}")
        fixed.update({n: float(v) for n, v in survey_fixed_override.items()})
    out = {
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
    if p.get("population_preset"):
        pre = POPULATION_PRESETS[p["population_preset"]]
        if pre["population_model"] != p["population_model"]:
            raise ValueError(f"{name}: preset {p['population_preset']!r} belongs to "
                             f"{pre['population_model']!r}, not {p['population_model']!r}")
        out.update(population_preset=p["population_preset"],
                   core_population_fixed=pre["core_population_fixed"],
                   population_constraint_groups=pop.get("constraint_groups") or [])
    if dark:
        out.update({
            "universe": "dark",
            "sample_survey": ks,
            "survey_labels": survey_labels,
            "survey_lower": [SURVEY_BOUNDS[n][0] for n in survey_labels],
            "survey_upper": [SURVEY_BOUNDS[n][1] for n in survey_labels],
            "survey_prior_kinds": [list(SURVEY_PRIOR_KINDS[n]) for n in survey_labels],
            "survey_fiducials": [SURVEY_FIDUCIALS[n] for n in survey_labels],
            "survey_fixed_override": dict(survey_fixed_override or {}),
            "log10n0_prior": {k2: list(v[:2]) for k2, v in LOG10N0_PRIOR.items()},
            # The decoded full vector reports n0 = 10**log10n0 (both decoders
            # return n0, not its log): ``decoded_order`` names that slot.
            "decoded_order": [("n0" if n == "log10n0" else n) for n in full_order],
        })
    return out


def label_bounds(plan: dict, label: str) -> list:
    """[lower, upper] of any sampleable label of a resolved plan."""
    if label == H0_LABEL:
        return list(plan["H0_bounds"])
    if label in plan["population_labels"]:
        i = plan["population_labels"].index(label)
        return [plan["population_lower"][i], plan["population_upper"][i]]
    if label in plan.get("survey_labels", ()):
        i = plan["survey_labels"].index(label)
        return [plan["survey_lower"][i], plan["survey_upper"][i]]
    raise KeyError(label)


def label_kind(plan: dict, label: str) -> list:
    if label == H0_LABEL:
        return ["uniform", None, None]
    if label in plan["population_labels"]:
        return list(plan["population_prior_kinds"][plan["population_labels"].index(label)])
    if label in plan.get("survey_labels", ()):
        return list(plan["survey_prior_kinds"][plan["survey_labels"].index(label)])
    raise KeyError(label)


def plan_summary(name: str) -> dict:
    """Compact {sampled, fixed, model, fiducials} view (used in reports)."""
    r = resolve_plan(name)
    return {
        "sampled": r["sampled"],
        "fixed": r["fixed"],
        "model": r["population_model"],
        "universe": r.get("universe", "spectral"),
        "fiducials": r["fiducials"],
        "H0_bounds": r["H0_bounds"],
    }


if __name__ == "__main__":  # pragma: no cover - convenience printer
    import json
    import sys

    names = sys.argv[1:] or list(PLANS)
    print(json.dumps({n: plan_summary(n) for n in names}, indent=1))
