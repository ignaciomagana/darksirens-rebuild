#!/usr/bin/env python3
"""Phase-11 L0C-S oracle for lensed selection and exactly-one evidence.

This probe runs only against the pinned legacy tree.  It freezes the
both-detected J=2 selection estimator, exactly-one-detected selection channel,
shared-campaign bookkeeping, and one-event lensed-singleton evidence before L5
production reconstruction.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _f64(x):
    return np.asarray(x, dtype=np.float64).tolist()


def _context(H0=67.74):
    import jax.numpy as jnp
    from darksirens.core.types import CosmoParams, SurveyParams, EMCatalog

    cosmo = CosmoParams(H0=H0, Om0=0.3075)
    survey = SurveyParams(
        n0=1e-3, z50=1.0, w=0.5, delta=0.0, b_miss=1.0, alpha_miss=0.5,
    )
    catalog = EMCatalog(
        apix=1.0,
        zgals=jnp.zeros((1, 1)),
        dzgals=jnp.ones((1, 1)),
        wgals=jnp.ones((1, 1)),
        ngals=jnp.ones((1,), dtype=jnp.int32),
        delta_g_pix_z=jnp.zeros((1, 1)),
        dN_obs_kde=None,
        pixel_to_cache_idx=None,
    )
    return cosmo, survey, catalog


def _toy_log_p_pop(m1src, q, z, chieff, pop_params):
    import jax.numpy as jnp
    del pop_params
    return (
        -0.5 * ((m1src - 30.0) / 8.0) ** 2
        - 0.5 * ((q - 0.7) / 0.15) ** 2
        - 0.5 * ((chieff + 0.05) / 0.2) ** 2
        + 0.3 * jnp.log1p(z)
    )


def _toy_volume_prior_fixed(z, pix, catalog):
    """Planck-fixed p(z), deliberately independent of the passed cosmo object."""
    from darksirens.redshift.volume import log_volume_prior_vmap
    del pix, catalog
    cosmo, survey, _ = _context(67.74)
    return log_volume_prior_vmap(z, cosmo, survey)


def _synth_campaign(n_sources=300, seed=3):
    import jax.numpy as jnp
    from darksirens.utils.cosmology import dL_of_z, H0Planck, Om0Planck

    rng = np.random.default_rng(seed)
    m1_src = rng.uniform(10.0, 70.0, n_sources)
    q = rng.uniform(0.3, 1.0, n_sources)
    z = rng.uniform(0.05, 2.0, n_sources)
    chieff = rng.uniform(-0.4, 0.4, n_sources)
    y = rng.uniform(0.05, 0.95, n_sources)
    p_prop_src = np.full(n_sources, 1.0 / (60 * 0.7 * 1.95 * 0.8))
    p_prop_y = np.full(n_sources, 1.0 / 0.9)

    mu_p = (1.0 + y) / y
    mu_m = (1.0 - y) / y
    dL_src = np.asarray(dL_of_z(jnp.asarray(z), H0Planck, Om0Planck))
    dL_p = dL_src / np.sqrt(mu_p)
    dL_m = dL_src / np.sqrt(mu_m)
    m1det = (1.0 + z) * m1_src
    det_p = (m1det > 25.0) & (dL_p < 4000.0)
    det_m = (m1det > 25.0) & (dL_m < 4000.0)

    n_img = 2 * n_sources
    data = {
        "source_id": np.repeat(np.arange(n_sources, dtype=np.int32), 2),
        "image_id": np.tile(np.array([0, 1], dtype=np.int32), n_sources),
        "m1_src": np.repeat(m1_src, 2),
        "q_src": np.repeat(q, 2),
        "z_src": np.repeat(z, 2),
        "chieff": np.repeat(chieff, 2),
        "y_source": np.repeat(y, 2),
        "p_prop_src": np.repeat(p_prop_src, 2),
        "p_prop_y": np.repeat(p_prop_y, 2),
    }
    mu = np.empty(n_img); mu[0::2] = mu_p; mu[1::2] = mu_m
    detected = np.empty(n_img, dtype=bool)
    detected[0::2] = det_p; detected[1::2] = det_m
    data["mu"] = mu
    data["detected"] = detected
    truth = {
        "m1_src": m1_src, "q": q, "z": z, "chieff": chieff, "y": y,
        "p_prop_src": p_prop_src, "p_prop_y": p_prop_y,
        "mu_p": mu_p, "mu_m": mu_m, "det_p": det_p, "det_m": det_m,
    }
    return data, truth, n_sources


def _manual_log_mu(mask, truth, sis, n_draw):
    import jax.numpy as jnp
    from scipy.special import logsumexp
    from darksirens.lensing.slmarks import tau_2_prob

    if not np.any(mask):
        return -np.inf
    log_pop = np.asarray(_toy_log_p_pop(
        jnp.asarray(truth["m1_src"][mask]), jnp.asarray(truth["q"][mask]),
        jnp.asarray(truth["z"][mask]), jnp.asarray(truth["chieff"][mask]), None,
    ))
    log_pz = np.asarray(_toy_volume_prior_fixed(
        jnp.asarray(truth["z"][mask]), None, None,
    ))
    log_tau = np.log(np.asarray(tau_2_prob(jnp.asarray(truth["z"][mask]), sis)))
    log_py = np.log(2.0 * truth["y"][mask])
    log_prop = (
        np.log(truth["p_prop_src"][mask]) + np.log(truth["p_prop_y"][mask])
    )
    return float(logsumexp(log_pop + log_pz + log_tau + log_py - log_prop) - np.log(n_draw))


def _selection_probe():
    import jax.numpy as jnp
    from darksirens.lensing.lensed_injections import (
        save_lensed_injections, load_lensed_injections,
        load_lensed_single_image_set,
    )
    from darksirens.lensing.slmarks import make_sis_lens_params
    from darksirens.likelihood.cluster_selection import (
        compute_cluster_selection_term,
        compute_lensed_single_selection_term,
        combined_selection_log_correction,
    )

    data, truth, n_draw = _synth_campaign()
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "lensed.h5")
        save_lensed_injections(path, n_draw_sources=n_draw, **data)
        pairs = load_lensed_injections(path)
        singles = load_lensed_single_image_set(path)

    both = truth["det_p"] & truth["det_m"]
    xor = truth["det_p"] ^ truth["det_m"]
    none = ~(truth["det_p"] | truth["det_m"])
    plus_only = truth["det_p"] & ~truth["det_m"]
    minus_only = ~truth["det_p"] & truth["det_m"]

    cosmo, survey, catalog = _context()
    alt_cosmo, _, _ = _context(90.0)
    pop = jnp.zeros(1)
    sis = make_sis_lens_params(A_tau=5e-4, n_tau=3.0)

    pair = compute_cluster_selection_term(
        pairs, cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior_fixed,
    )
    single = compute_lensed_single_selection_term(
        singles, cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior_fixed,
    )
    pair_alt = compute_cluster_selection_term(
        pairs, alt_cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior_fixed,
    )
    single_alt = compute_lensed_single_selection_term(
        singles, alt_cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior_fixed,
    )

    tag_half = compute_cluster_selection_term(
        pairs, cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior_fixed,
        log_p_tag_per_source=jnp.full(pairs.n_kept, -jnp.log(2.0)),
    )

    sis_zero = make_sis_lens_params(A_tau=0.0, n_tau=3.0)
    pair_zero = compute_cluster_selection_term(
        pairs, cosmo, survey, pop, catalog, sis_zero,
        _toy_log_p_pop, _toy_volume_prior_fixed,
    )
    single_zero = compute_lensed_single_selection_term(
        singles, cosmo, survey, pop, catalog, sis_zero,
        _toy_log_p_pop, _toy_volume_prior_fixed,
    )

    # A deterministic synthetic ordinary-singleton channel to pin the MFG
    # channel combination independently of the ordinary injection machinery.
    log_mu_u = jnp.asarray(1.35)
    log_sig2_u = jnp.asarray(-1.1)
    corr_pair_only = combined_selection_log_correction(
        log_mu_u, log_sig2_u,
        pair[0], pair[2],
        n_singletons_observed=3,
        n_clusters_observed=1,
        max_likelihood_variance=100.0,
    )
    corr_no_pair = combined_selection_log_correction(
        log_mu_u, log_sig2_u,
        jnp.asarray(-jnp.inf), jnp.asarray(-jnp.inf),
        n_singletons_observed=3,
        n_clusters_observed=0,
        max_likelihood_variance=100.0,
    )

    return {
        "counts": {
            "n_draw": int(n_draw),
            "both": int(both.sum()),
            "exactly_one": int(xor.sum()),
            "none": int(none.sum()),
            "plus_only": int(plus_only.sum()),
            "minus_only": int(minus_only.sum()),
            "loaded_pair_kept": int(pairs.n_kept),
            "loaded_single_kept": int(singles.n_kept),
        },
        "pair_selection": {
            "log_mu": float(pair[0]), "Neff": float(pair[1]),
            "log_sigma2": float(pair[2]),
            "manual_log_mu": _manual_log_mu(both, truth, sis, n_draw),
            "manual_delta": float(pair[0] - _manual_log_mu(both, truth, sis, n_draw)),
            "tag_half_log_mu": float(tag_half[0]),
            "tag_half_log_mu_delta": float(tag_half[0] - pair[0]),
            "tag_half_Neff_delta": float(tag_half[1] - pair[1]),
            "tag_half_log_sigma2_delta": float(tag_half[2] - pair[2]),
            "alt_cosmo_argument_delta": _f64(np.asarray(pair_alt) - np.asarray(pair)),
            "tau_zero_log_mu_is_neginf": bool(np.isneginf(float(pair_zero[0]))),
        },
        "single_selection": {
            "log_mu": float(single[0]), "Neff": float(single[1]),
            "log_sigma2": float(single[2]),
            "manual_log_mu": _manual_log_mu(xor, truth, sis, n_draw),
            "manual_delta": float(single[0] - _manual_log_mu(xor, truth, sis, n_draw)),
            "alt_cosmo_argument_delta": _f64(np.asarray(single_alt) - np.asarray(single)),
            "tau_zero_log_mu_is_neginf": bool(np.isneginf(float(single_zero[0]))),
        },
        "combined_correction": {
            "with_pair": float(corr_pair_only),
            "without_pair": float(corr_no_pair),
            "delta": float(corr_pair_only - corr_no_pair),
        },
    }


def _event_probe():
    import jax.numpy as jnp
    from darksirens.lensing.fcpdet import make_fc_pdet_params
    from darksirens.lensing.grids import make_y_grid
    from darksirens.lensing.slmarks import make_sis_lens_params
    from darksirens.likelihood.cluster_likelihood import lensed_single_log_likelihood_event

    rng = np.random.default_rng(5)
    n_pe, n_y = 40, 16
    event = {
        "m1det": jnp.asarray(rng.uniform(30.0, 50.0, n_pe)),
        "q": jnp.asarray(rng.uniform(0.5, 0.95, n_pe)),
        "dL": jnp.asarray(rng.uniform(800.0, 2000.0, n_pe)),
        "chieff": jnp.asarray(rng.uniform(-0.2, 0.2, n_pe)),
        "prior_wt": jnp.asarray(rng.uniform(0.5, 1.5, n_pe)),
        "valid": jnp.ones(n_pe, dtype=bool),
        "pixels": jnp.zeros(n_pe, dtype=jnp.int32),
    }
    cosmo, survey, catalog = _context()
    sis = make_sis_lens_params(A_tau=5e-4, n_tau=3.0)
    fc = make_fc_pdet_params(rho_thr=8.0, horizon_mpc=3000.0)
    y, log_wy = make_y_grid(n_y)

    default = lensed_single_log_likelihood_event(
        event, cosmo, survey, jnp.zeros(1), catalog, sis, fc,
        _toy_log_p_pop, _toy_volume_prior_fixed, y, log_wy,
        return_mc_variance=True,
    )
    explicit = lensed_single_log_likelihood_event(
        event, cosmo, survey, jnp.zeros(1), catalog, sis, fc,
        _toy_log_p_pop, _toy_volume_prior_fixed, y, log_wy,
        pair_orientation_mode="independent", return_mc_variance=True,
    )
    shared = lensed_single_log_likelihood_event(
        event, cosmo, survey, jnp.zeros(1), catalog, sis, fc,
        _toy_log_p_pop, _toy_volume_prior_fixed, y, log_wy,
        pair_orientation_mode="shared_iota", return_mc_variance=True,
    )
    zero = lensed_single_log_likelihood_event(
        event, cosmo, survey, jnp.zeros(1), catalog,
        make_sis_lens_params(A_tau=0.0, n_tau=3.0), fc,
        _toy_log_p_pop, _toy_volume_prior_fixed, y, log_wy,
    )
    return {
        "n_pe": n_pe,
        "n_y": n_y,
        "default_logL": float(default[0]),
        "default_mc_variance": float(default[1]),
        "explicit_independent_logL": float(explicit[0]),
        "explicit_independent_mc_variance": float(explicit[1]),
        "default_minus_explicit": float(default[0] - explicit[0]),
        "default_var_minus_explicit": float(default[1] - explicit[1]),
        "shared_iota_logL": float(shared[0]),
        "shared_iota_mc_variance": float(shared[1]),
        "shared_minus_independent": float(shared[0] - default[0]),
        "tau_zero_is_neginf": bool(np.isneginf(float(zero))),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    import jax
    jax.config.update("jax_enable_x64", True)

    out = {
        "schema": "darksirens-lensing-l0c-selection-reference-1",
        "legacy_sha": LEGACY_SHA,
        "selection": _selection_probe(),
        "lensed_single_event": _event_probe(),
        "selection_cosmology_contract": "pre-rendered detection subsets; fixed campaign cosmology required",
    }
    p = Path(args.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
