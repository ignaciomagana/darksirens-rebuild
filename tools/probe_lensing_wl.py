#!/usr/bin/env python3
"""Deterministic Phase-11 L0A probe of the pinned legacy weak-lensing seam.

Run in a process whose PYTHONPATH resolves the pinned legacy ``darksirens``.
No production companion code is imported.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _f64(value):
    return np.asarray(value, dtype=np.float64).tolist()


def _finite(value) -> bool:
    return bool(np.all(np.isfinite(np.asarray(value, dtype=np.float64))))


def _toy_objects():
    import jax.numpy as jnp
    from darksirens.core.types import CosmoParams, SurveyParams, EMCatalog
    from darksirens.utils.cosmology import H0Planck, Om0Planck

    cosmo = CosmoParams(H0=H0Planck, Om0=Om0Planck)
    survey = SurveyParams(
        n0=1e-3, z50=1.0, w=0.5, delta=0.0, b_miss=1.0, alpha_miss=0.5
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


def _toy_samples(n=7, seed=20260912):
    import jax.numpy as jnp

    rng = np.random.default_rng(seed)
    return (
        jnp.asarray(rng.uniform(24.0, 55.0, n)),
        jnp.asarray(rng.uniform(0.45, 0.95, n)),
        jnp.asarray(rng.uniform(500.0, 2600.0, n)),
        jnp.asarray(rng.uniform(-0.25, 0.25, n)),
        jnp.zeros(n, dtype=jnp.int32),
        jnp.asarray(rng.uniform(0.6, 1.4, n)),
    )


def _toy_log_p_pop(m1src, q, z, chieff, pop_params):
    import jax.numpy as jnp

    del pop_params
    return (
        -0.5 * ((m1src - 31.0) / 7.5) ** 2
        -0.5 * ((q - 0.72) / 0.16) ** 2
        -0.5 * ((chieff + 0.03) / 0.22) ** 2
        +0.25 * jnp.log1p(z)
    )


def _flat_log_prior_z(z, pix, catalog):
    import jax.numpy as jnp

    del pix, catalog
    return jnp.zeros_like(z, dtype=jnp.float64)


def _pdf_probe():
    import jax.numpy as jnp
    from jax.scipy.special import logsumexp

    from darksirens.lensing.grids import make_log_mu_grid
    from darksirens.lensing.wlmagnification import (
        make_lognormal_wl_params,
        log_p_wl,
    )

    params = make_lognormal_wl_params(a=4.0e-3, b=1.5)
    mu = jnp.asarray([0.72, 0.91, 1.0, 1.13, 1.42])
    z = jnp.asarray([0.2, 0.5, 1.0, 1.5, 2.0])
    logp = np.asarray(log_p_wl(mu, z, params))

    wide = make_lognormal_wl_params(a=0.2, b=0.5)
    mu_nodes, log_w = make_log_mu_grid(200, (-4.0, 4.0))
    norm = []
    mean = []
    for z0 in (0.5, 1.0, 2.0):
        zz = jnp.full_like(mu_nodes, z0)
        lp = log_p_wl(mu_nodes, zz, wide)
        norm.append(float(jnp.exp(logsumexp(lp + jnp.log(mu_nodes) + log_w))))
        mean.append(float(jnp.exp(logsumexp(lp + 2.0 * jnp.log(mu_nodes) + log_w))))

    return {
        "a": 4.0e-3,
        "b": 1.5,
        "mu": _f64(mu),
        "z": _f64(z),
        "logp": _f64(logp),
        "wide_moment_z": [0.5, 1.0, 2.0],
        "normalization": norm,
        "mean_mu": mean,
        "max_abs_norm_minus_one": float(np.max(np.abs(np.asarray(norm) - 1.0))),
        "max_abs_mean_minus_one": float(np.max(np.abs(np.asarray(mean) - 1.0))),
    }


def _tabulated_probe():
    import jax.numpy as jnp
    from darksirens.lensing.wlmagnification import (
        make_tabulated_log_p_wl,
        make_tabulated_wl_params,
    )

    zg = jnp.asarray([0.1, 0.8, 1.6, 2.4])
    lg = jnp.asarray([-1.0, -0.2, 0.5, 1.0])
    # Bilinear function: interpolation must reproduce it exactly up to roundoff.
    table = 0.7 * zg[:, None] + 1.3 * lg[None, :] - 0.2
    fn = make_tabulated_log_p_wl(zg, lg, table)
    qmu = jnp.exp(jnp.asarray([-2.0, -0.55, 0.1, 2.0]))
    qz = jnp.asarray([-0.5, 0.45, 1.95, 4.0])
    got = np.asarray(fn(qmu, qz))
    zc = np.clip(np.asarray(qz), float(zg[0]), float(zg[-1]))
    lc = np.clip(np.log(np.asarray(qmu)), float(lg[0]), float(lg[-1]))
    expected = 0.7 * zc + 1.3 * lc - 0.2

    minus_inf_ok = False
    bad = np.asarray(table)
    bad[1, 2] = -np.inf
    try:
        make_tabulated_wl_params(zg, lg, jnp.asarray(bad))
        minus_inf_ok = True
    except Exception:
        minus_inf_ok = False

    nan_rejected = False
    poisoned = np.asarray(table)
    poisoned[1, 2] = np.nan
    try:
        make_tabulated_wl_params(zg, lg, jnp.asarray(poisoned))
    except ValueError:
        nan_rejected = True

    duplicate_grid_rejected = False
    try:
        make_tabulated_wl_params(
            jnp.asarray([0.1, 0.8, 0.8, 2.4]), lg, table
        )
    except ValueError:
        duplicate_grid_rejected = True

    return {
        "query_mu": _f64(qmu),
        "query_z": _f64(qz),
        "logp": _f64(got),
        "expected_clamped_linear": _f64(expected),
        "max_abs_interp_error": float(np.max(np.abs(got - expected))),
        "minus_inf_allowed": minus_inf_ok,
        "nan_rejected": nan_rejected,
        "duplicate_grid_rejected": duplicate_grid_rejected,
    }


def _quadrature_probe():
    import jax.numpy as jnp
    from darksirens.lensing.grids import (
        WL_MU_QUADRATURE_LOG_MU_RANGE,
        WL_MU_QUADRATURE_NODES,
        make_hermite_u_grid,
        make_log_mu_grid,
        make_wl_mu_quadrature,
        make_y_grid,
    )
    from darksirens.lensing.wlmagnification import wl_hermite_quadrature_errors

    mu, lw = make_wl_mu_quadrature()
    mu2, lw2 = make_log_mu_grid(
        WL_MU_QUADRATURE_NODES, WL_MU_QUADRATURE_LOG_MU_RANGE
    )
    u, lwh = make_hermite_u_grid(16)
    y, lwy = make_y_grid(32)

    np.testing.assert_array_equal(np.asarray(mu), np.asarray(mu2))
    np.testing.assert_array_equal(np.asarray(lw), np.asarray(lw2))

    zcheck = np.asarray([0.05, 0.5, 1.0, 2.0], dtype=np.float64)
    zret, errors = wl_hermite_quadrature_errors(
        4.0e-3, 1.5, u, lwh, z_app_test=zcheck
    )
    zzero, errors_zero = wl_hermite_quadrature_errors(
        0.0, 1.5, u, lwh, z_app_test=zcheck
    )

    return {
        "production_mu_nodes": int(WL_MU_QUADRATURE_NODES),
        "production_log_mu_range": list(WL_MU_QUADRATURE_LOG_MU_RANGE),
        "mu_first4": _f64(mu[:4]),
        "mu_last4": _f64(mu[-4:]),
        "logw_first4": _f64(lw[:4]),
        "hermite_u_first4": _f64(u[:4]),
        "hermite_u_last4": _f64(u[-4:]),
        "hermite_weight_sum": float(jnp.sum(jnp.exp(lwh))),
        "y_weighted_p_integral": float(jnp.sum(jnp.exp(lwy) * 2.0 * y)),
        "hermite_error_z": _f64(zret),
        "hermite_abs_logI_error": _f64(errors),
        "a0_error_z": _f64(zzero),
        "a0_abs_logI_error": _f64(errors_zero),
    }


def _event_weight_probe():
    import jax
    import jax.numpy as jnp

    from darksirens.inference.utils import log_sample_weight
    from darksirens.lensing.grids import make_hermite_u_grid, make_log_mu_grid
    from darksirens.lensing.wlmagnification import make_lognormal_log_p_wl
    from darksirens.likelihood.wl_weight import (
        log_sample_weight_wl_lognormal_hermite,
        log_sample_weight_wl_or_standard,
    )

    cosmo, survey, catalog = _toy_objects()
    samples = _toy_samples()
    m1det, q, dL, chieff, pix, prior_wt = samples
    pop_params = jnp.asarray([])

    standard = log_sample_weight(
        *samples,
        cosmo,
        survey,
        pop_params,
        catalog,
        _toy_log_p_pop,
        _flat_log_prior_z,
    )

    mu, lw = make_log_mu_grid(16, (-0.6, 0.6))
    off = log_sample_weight_wl_or_standard(
        *samples,
        cosmo,
        survey,
        pop_params,
        catalog,
        _toy_log_p_pop,
        _flat_log_prior_z,
        make_lognormal_log_p_wl(4.0e-3, 1.5),
        mu,
        lw,
        wl_enabled=False,
    )
    np.testing.assert_array_equal(np.asarray(off), np.asarray(standard))

    u, lwh = make_hermite_u_grid(16)
    hermite_zero = log_sample_weight_wl_lognormal_hermite(
        *samples,
        cosmo,
        survey,
        pop_params,
        catalog,
        _toy_log_p_pop,
        _flat_log_prior_z,
        jnp.asarray(0.0),
        jnp.asarray(1.5),
        u,
        lwh,
    )
    hermite_default = log_sample_weight_wl_lognormal_hermite(
        *samples,
        cosmo,
        survey,
        pop_params,
        catalog,
        _toy_log_p_pop,
        _flat_log_prior_z,
        jnp.asarray(4.0e-3),
        jnp.asarray(1.5),
        u,
        lwh,
    )

    zero_delta = np.asarray(hermite_zero - standard)

    def scalar_a(a):
        out = log_sample_weight_wl_lognormal_hermite(
            *samples,
            cosmo,
            survey,
            pop_params,
            catalog,
            _toy_log_p_pop,
            _flat_log_prior_z,
            a,
            jnp.asarray(1.5),
            u,
            lwh,
        )
        return jnp.sum(out)

    grad_a0 = float(jax.grad(scalar_a)(jnp.asarray(0.0)))

    return {
        "standard": _f64(standard),
        "dispatcher_off_bit_identical": bool(
            np.array_equal(np.asarray(off), np.asarray(standard))
        ),
        "hermite_a0": _f64(hermite_zero),
        "hermite_a0_max_abs_delta": float(np.max(np.abs(zero_delta))),
        "hermite_default": _f64(hermite_default),
        "default_minus_standard": _f64(np.asarray(hermite_default - standard)),
        "all_default_finite": _finite(hermite_default),
        "grad_sum_weight_wrt_a_at_zero": grad_a0,
        "grad_at_zero_finite": bool(np.isfinite(grad_a0)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()

    import jax
    jax.config.update("jax_enable_x64", True)

    out = {
        "schema": "darksirens-lensing-l0a-wl-reference-1",
        "legacy_sha": LEGACY_SHA,
        "pdf": _pdf_probe(),
        "tabulated": _tabulated_probe(),
        "quadrature": _quadrature_probe(),
        "event_weight": _event_weight_probe(),
    }

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
