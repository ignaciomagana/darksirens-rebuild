#!/usr/bin/env python3
"""Phase-11 L0C oracle for the pinned legacy pair-evidence path.

Freezes the full-covariance apparent-frame PairKDE and the unmarked J=2 SIS
pair likelihood before they are reconstructed in the lensing companion.
Run with PYTHONPATH resolving the pinned legacy darksirens tree.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _f64(x):
    return np.asarray(x, dtype=np.float64).tolist()


def _event_numpy(z_true, m1src_true, q_true, chieff_true, y_true, n_pe, seed):
    import jax.numpy as jnp
    from darksirens.utils.cosmology import H0Planck, Om0Planck, dL_of_z

    rng = np.random.default_rng(seed)
    dL_src = float(dL_of_z(jnp.asarray(z_true), H0Planck, Om0Planck))
    mu_p = (1.0 + y_true) / y_true
    mu_m = (1.0 - y_true) / y_true
    dL_i = dL_src / np.sqrt(mu_p)
    dL_j = dL_src / np.sqrt(mu_m)
    m1det_true = (1.0 + z_true) * m1src_true

    def one(dL0):
        m1 = m1det_true + rng.normal(0.0, 1.0, n_pe)
        q = np.clip(q_true + rng.normal(0.0, 0.05, n_pe), 0.05, 0.999)
        dl = dL0 + rng.normal(0.0, 0.05 * dL0, n_pe)
        chi = chieff_true + rng.normal(0.0, 0.03, n_pe)
        # Deliberately non-uniform positive proposal density: this pins the
        # pi_PE/p_prop estimand instead of a posterior-only KDE.
        pwt = 0.65 + 0.55 * (1.0 + np.sin(np.arange(n_pe) * 0.173)) / 2.0
        valid = np.ones(n_pe, dtype=bool)
        valid[[7, 83]] = False
        return dict(m1det=m1, q=q, dL=dl, chieff=chi, prior_wt=pwt, valid=valid)

    return one(dL_i), one(dL_j)


def _jax_event(ev):
    import jax.numpy as jnp
    n = len(ev["m1det"])
    return {
        "m1det": jnp.asarray(ev["m1det"]),
        "q": jnp.asarray(ev["q"]),
        "dL": jnp.asarray(ev["dL"]),
        "chieff": jnp.asarray(ev["chieff"]),
        "prior_wt": jnp.asarray(ev["prior_wt"]),
        "valid": jnp.asarray(ev["valid"]),
        "pixels": jnp.zeros(n, dtype=jnp.int32),
    }


def _toy_context():
    import jax.numpy as jnp
    from darksirens.core.types import CosmoParams, SurveyParams, EMCatalog
    from darksirens.utils.cosmology import H0Planck, Om0Planck

    cosmo = CosmoParams(H0=H0Planck, Om0=Om0Planck)
    survey = SurveyParams(n0=1e-3, z50=1.0, w=0.5, delta=0.0,
                          b_miss=1.0, alpha_miss=0.5)
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


def _toy_volume_prior(z, pix, catalog):
    from darksirens.redshift.volume import log_volume_prior_vmap
    del pix, catalog
    cosmo, survey, _ = _toy_context()
    return log_volume_prior_vmap(z, cosmo, survey)


def _kde_probe(evi, evj):
    import jax.numpy as jnp
    from darksirens.likelihood.pair_kde import (
        make_pair_kde, log_eval_pair_kde, validate_pair_prior_wt,
    )

    k_i = make_pair_kde(evi["m1det"], evi["q"], evi["dL"], evi["chieff"],
                        evi["prior_wt"], valid=evi["valid"])
    k_j = make_pair_kde(evj["m1det"], evj["q"], evj["dL"], evj["chieff"],
                        evj["prior_wt"], valid=evj["valid"])

    mean_j = np.asarray(k_j.mean)
    queries = np.asarray([
        mean_j,
        mean_j + np.asarray([0.5, 0.015, 35.0, 0.01]),
        np.asarray([mean_j[0], 0.995, mean_j[2], mean_j[3]]),
        np.asarray([mean_j[0], 1.005, mean_j[2], mean_j[3]]),
    ])
    vals = np.asarray(log_eval_pair_kde(k_j, jnp.asarray(queries)))

    # Padding invariance: append invalid NaN rows. Density and valid-row
    # normalization must not move.
    pad = 17
    evj_pad = {}
    for key in ("m1det", "q", "dL", "chieff"):
        evj_pad[key] = np.concatenate([evj[key], np.full(pad, np.nan)])
    evj_pad["prior_wt"] = np.concatenate([evj["prior_wt"], np.zeros(pad)])
    evj_pad["valid"] = np.concatenate([evj["valid"], np.zeros(pad, dtype=bool)])
    k_pad = make_pair_kde(evj_pad["m1det"], evj_pad["q"], evj_pad["dL"],
                          evj_pad["chieff"], evj_pad["prior_wt"], valid=evj_pad["valid"])
    vals_pad = np.asarray(log_eval_pair_kde(k_pad, jnp.asarray(queries)))

    bad_rejected = False
    try:
        validate_pair_prior_wt(np.zeros(4), context="L0C malformed fixture")
    except ValueError:
        bad_rejected = True

    return {
        "n_total": int(len(evj["m1det"])),
        "n_valid": int(np.sum(evj["valid"])),
        "mean": _f64(k_j.mean),
        "l_inv": np.asarray(k_j.l_inv, dtype=np.float64).tolist(),
        "log_h": _f64(k_j.log_h),
        "log_norm": float(k_j.log_norm),
        "queries": queries.tolist(),
        "log_eval": vals.tolist(),
        "padding_log_eval": vals_pad.tolist(),
        "padding_max_abs_delta": float(np.max(np.abs(vals_pad - vals))),
        "q_reflection_pair_delta": float(abs(vals[2] - vals[3])),
        "has_offdiagonal_whitening": bool(
            np.max(np.abs(np.asarray(k_j.l_inv) - np.diag(np.diag(np.asarray(k_j.l_inv))))) > 1e-8
        ),
        "malformed_prior_rejected": bad_rejected,
        "kde_i_log_norm": float(k_i.log_norm),
    }, k_i, k_j


def _cluster_probe(evi_np, evj_np, kde_i, kde_j):
    import jax.numpy as jnp
    from jax.scipy.special import logsumexp
    from darksirens.lensing.grids import make_y_grid
    from darksirens.lensing.slmarks import (
        make_sis_lens_params, mu_plus_minus_from_y, log_p_y_SIS,
    )
    from darksirens.likelihood.cluster_likelihood import (
        _pair_branch_log_integrand, cluster_log_likelihood_pair,
    )

    evi = _jax_event(evi_np)
    evj = _jax_event(evj_np)
    cosmo, survey, catalog = _toy_context()
    sis = make_sis_lens_params()
    y, log_wy = make_y_grid(32)
    pop = jnp.asarray([0.0])

    pair, var = cluster_log_likelihood_pair(
        evi, evj, kde_i, kde_j, cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior, y, log_wy,
        return_mc_variance=True,
    )
    pair_swap, var_swap = cluster_log_likelihood_pair(
        evj, evi, kde_j, kde_i, cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior, y, log_wy,
        return_mc_variance=True,
    )

    mup, mum = mu_plus_minus_from_y(y)
    logpy = log_p_y_SIS(y)
    inta = _pair_branch_log_integrand(
        evi["m1det"], evi["q"], evi["dL"], evi["chieff"],
        evi["prior_wt"], evi["valid"], evi["pixels"],
        mup, mum, logpy, log_wy, kde_j,
        cosmo, survey, pop, catalog, sis, _toy_log_p_pop, _toy_volume_prior,
    )
    intb = _pair_branch_log_integrand(
        evj["m1det"], evj["q"], evj["dL"], evj["chieff"],
        evj["prior_wt"], evj["valid"], evj["pixels"],
        mum, mup, logpy, log_wy, kde_i,
        cosmo, survey, pop, catalog, sis, _toy_log_p_pop, _toy_volume_prior,
    )
    na = jnp.sum((evi["valid"] & (evi["prior_wt"] > 0)).astype(jnp.float64))
    nb = jnp.sum((evj["valid"] & (evj["prior_wt"] > 0)).astype(jnp.float64))
    logza = logsumexp(inta) - jnp.log(na)
    logzb = logsumexp(intb) - jnp.log(nb)
    manual_sum = jnp.logaddexp(logza, logzb)
    manual_average = manual_sum - jnp.log(2.0)

    # Bandwidth sensitivity is an explicit diagnostic, not an alternative
    # accepted estimator.
    from darksirens.likelihood.pair_kde import make_pair_kde
    ki_half = make_pair_kde(evi_np["m1det"], evi_np["q"], evi_np["dL"],
                            evi_np["chieff"], evi_np["prior_wt"],
                            valid=evi_np["valid"], bandwidth_scale=0.5)
    kj_half = make_pair_kde(evj_np["m1det"], evj_np["q"], evj_np["dL"],
                            evj_np["chieff"], evj_np["prior_wt"],
                            valid=evj_np["valid"], bandwidth_scale=0.5)
    pair_half = cluster_log_likelihood_pair(
        evi, evj, ki_half, kj_half, cosmo, survey, pop, catalog, sis,
        _toy_log_p_pop, _toy_volume_prior, y, log_wy,
    )

    return {
        "y_nodes": int(y.shape[0]),
        "branch_a_logZ": float(logza),
        "branch_b_logZ": float(logzb),
        "manual_assignment_sum": float(manual_sum),
        "manual_assignment_average": float(manual_average),
        "pair_logL": float(pair),
        "pair_mc_variance": float(var),
        "swapped_pair_logL": float(pair_swap),
        "swapped_pair_mc_variance": float(var_swap),
        "pair_minus_manual_sum": float(pair - manual_sum),
        "pair_minus_manual_average": float(pair - manual_average),
        "swap_abs_delta": float(abs(pair_swap - pair)),
        "swap_variance_abs_delta": float(abs(var_swap - var)),
        "bandwidth_half_logL": float(pair_half),
        "bandwidth_half_minus_default": float(pair_half - pair),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    import jax
    jax.config.update("jax_enable_x64", True)

    evi, evj = _event_numpy(
        z_true=0.7, m1src_true=30.0, q_true=0.7, chieff_true=0.0,
        y_true=0.4, n_pe=300, seed=260913,
    )
    kde, ki, kj = _kde_probe(evi, evj)
    cluster = _cluster_probe(evi, evj, ki, kj)

    out = {
        "schema": "darksirens-lensing-l0c-pair-reference-1",
        "legacy_sha": LEGACY_SHA,
        "pair_kde": kde,
        "cluster_pair": cluster,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
