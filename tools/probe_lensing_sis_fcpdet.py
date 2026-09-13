#!/usr/bin/env python3
"""Deterministic Phase-11 L0B probe of pinned legacy SIS/Finn-Chernoff physics.

Run with PYTHONPATH resolving the pinned legacy ``darksirens``.  This freezes
strong-lensing marks, optical-depth-as-probability semantics, the single-image
Finn-Chernoff detection law, and both supported two-image orientation modes.
It imports no production companion code.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _f64(x):
    return np.asarray(x, dtype=np.float64).tolist()


def _sis_probe():
    import jax.numpy as jnp
    from darksirens.lensing.slmarks import (
        DEFAULT_T0_SECONDS,
        TAU_PROB_MAX,
        delta_t_from_y,
        log_p_y_SIS,
        make_sis_lens_params,
        mu_plus_minus_from_y,
        tau_2_SIS,
        tau_2_prob,
        y_from_mu_plus,
    )

    p = make_sis_lens_params()
    z = jnp.asarray([0.0, 0.2, 1.0, 2.0, 5.0], dtype=jnp.float64)
    tau = tau_2_SIS(z, p)
    prob = tau_2_prob(z, p)

    # Prior-corner stress point where optical depth is not a probability.
    stress = make_sis_lens_params(A_tau=1.0e-2, n_tau=6.0)
    z_stress = jnp.asarray([1.0, 2.0, 5.0], dtype=jnp.float64)
    raw_stress = tau_2_SIS(z_stress, stress)
    prob_stress = tau_2_prob(z_stress, stress)

    y = jnp.asarray([0.05, 0.2, 0.5, 0.9], dtype=jnp.float64)
    lp = log_p_y_SIS(y)
    mu_p, mu_m = mu_plus_minus_from_y(y)
    y_back = y_from_mu_plus(mu_p)
    dt = delta_t_from_y(y, p)

    y_bad = jnp.asarray([-0.1, 0.0, 1.0, 1.1], dtype=jnp.float64)
    bad_lp = np.asarray(log_p_y_SIS(y_bad))

    return {
        "defaults": {
            "A_tau": float(p.A_tau),
            "n_tau": float(p.n_tau),
            "T0_seconds": float(p.T0),
            "DEFAULT_T0_SECONDS": float(DEFAULT_T0_SECONDS),
            "TAU_PROB_MAX": float(TAU_PROB_MAX),
        },
        "z": _f64(z),
        "tau_raw": _f64(tau),
        "tau_prob": _f64(prob),
        "stress_z": _f64(z_stress),
        "stress_tau_raw": _f64(raw_stress),
        "stress_tau_prob": _f64(prob_stress),
        "stress_clips_above_one": bool(np.any(np.asarray(raw_stress) > 1.0)),
        "stress_prob_strictly_below_one": bool(np.all(np.asarray(prob_stress) < 1.0)),
        "y": _f64(y),
        "log_p_y": _f64(lp),
        "mu_plus": _f64(mu_p),
        "mu_minus": _f64(mu_m),
        "mu_difference": _f64(mu_p - mu_m),
        "inverse_y": _f64(y_back),
        "delta_t_seconds": _f64(dt),
        "bad_y_all_neginf": bool(np.all(np.isneginf(bad_lp))),
        "max_abs_inverse_error": float(np.max(np.abs(np.asarray(y_back - y)))),
        "max_abs_mu_difference_minus_two": float(
            np.max(np.abs(np.asarray(mu_p - mu_m) - 2.0))
        ),
    }


def _fc_distance_for_threshold(x, m1_src, q, z, rho_thr, r0, mc_bar):
    m2 = q * m1_src
    mc_src = (m1_src * m2) ** 0.6 / (m1_src + m2) ** 0.2
    mc_det = mc_src * (1.0 + z)
    mass_factor = (mc_det / mc_bar) ** (5.0 / 6.0)
    return np.asarray(x, dtype=np.float64) * 8.0 * r0 * mass_factor / rho_thr


def _fcpdet_probe():
    import jax.numpy as jnp
    from darksirens.lensing.fcpdet import (
        PAIR_ORIENTATION_MODES,
        log_one_minus_pdet_fc,
        log_pmiss_partner_fc,
        make_fc_pdet_params,
        pdet_fc,
        pdet_pair_both_fc,
        pdet_pair_exactly_one_fc,
        theta_fc_from_antenna,
        theta_threshold_fc,
    )

    p = make_fc_pdet_params()
    rho_thr, r0, mc_bar = float(p.rho_thr), float(p.r0), float(p.mc_bar)
    m1 = 30.0
    q = 0.8
    z = 1.2

    desired_x = np.asarray([0.5, 1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    dL = _fc_distance_for_threshold(desired_x, m1, q, z, rho_thr, r0, mc_bar)
    m1v = jnp.full(desired_x.shape, m1, dtype=jnp.float64)
    qv = jnp.full(desired_x.shape, q, dtype=jnp.float64)
    zv = jnp.full(desired_x.shape, z, dtype=jnp.float64)
    dLv = jnp.asarray(dL)
    x = theta_threshold_fc(m1v, qv, zv, dLv, p)
    pd = pdet_fc(m1v, qv, zv, dLv, p)
    logmiss = log_one_minus_pdet_fc(m1v, qv, zv, dLv, p)

    # The exact geometric Theta decomposition is a separate contract from the
    # independent-mode polynomial marginal.
    fplus = jnp.asarray([1.0, 0.5, 0.0, 0.3], dtype=jnp.float64)
    fcross = jnp.asarray([0.0, 0.5, 1.0, 0.4], dtype=jnp.float64)
    ci = jnp.asarray([1.0, 0.0, 1.0, 0.6], dtype=jnp.float64)
    theta_geom = theta_fc_from_antenna(fplus, fcross, ci)

    # Threshold pairs highlighted in the legacy module documentation plus one
    # asymmetric support-edge stress point.
    pair_x = np.asarray([[1.0, 2.0], [1.5, 3.0], [0.8, 1.0], [4.5, 0.5]])
    dLp = _fc_distance_for_threshold(pair_x[:, 0], m1, q, z, rho_thr, r0, mc_bar)
    dLm = _fc_distance_for_threshold(pair_x[:, 1], m1, q, z, rho_thr, r0, mc_bar)
    n = pair_x.shape[0]
    m1p = jnp.full((n,), m1, dtype=jnp.float64)
    qp = jnp.full((n,), q, dtype=jnp.float64)
    zp = jnp.full((n,), z, dtype=jnp.float64)
    dLp_j = jnp.asarray(dLp)
    dLm_j = jnp.asarray(dLm)

    ind_both = pdet_pair_both_fc(
        m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="independent"
    )
    ind_one = pdet_pair_exactly_one_fc(
        m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="independent"
    )
    pp = pdet_fc(m1p, qp, zp, dLp_j, p)
    pm = pdet_fc(m1p, qp, zp, dLm_j, p)
    ind_both_manual = pp * pm
    ind_one_manual = pp * (1.0 - pm) + (1.0 - pp) * pm

    shared_both = pdet_pair_both_fc(
        m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="shared_iota"
    )
    shared_one = pdet_pair_exactly_one_fc(
        m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="shared_iota"
    )
    shared_both_swap = pdet_pair_both_fc(
        m1p, qp, zp, dLm_j, dLp_j, p, pair_orientation_mode="shared_iota"
    )
    shared_one_swap = pdet_pair_exactly_one_fc(
        m1p, qp, zp, dLm_j, dLp_j, p, pair_orientation_mode="shared_iota"
    )

    # Conditional partner-miss factor.  In independent mode the detected
    # image's distance is mathematically irrelevant; pin that identity.
    ind_log_cond = log_pmiss_partner_fc(
        m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="independent"
    )
    ind_log_cond_alt_det = log_pmiss_partner_fc(
        m1p, qp, zp, dLp_j * 1.7, dLm_j, p,
        pair_orientation_mode="independent",
    )
    partner_marginal = log_one_minus_pdet_fc(m1p, qp, zp, dLm_j, p)
    shared_log_cond = log_pmiss_partner_fc(
        m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="shared_iota"
    )

    invalid_mode_rejected = False
    try:
        pdet_pair_both_fc(
            m1p, qp, zp, dLp_j, dLm_j, p, pair_orientation_mode="not-a-mode"
        )
    except ValueError:
        invalid_mode_rejected = True

    # Tiny/huge-distance support limits for the independent polynomial model.
    dL_tiny = jnp.asarray([1.0e-12], dtype=jnp.float64)
    dL_huge = jnp.asarray([1.0e15], dtype=jnp.float64)
    one = jnp.asarray([m1], dtype=jnp.float64)
    qone = jnp.asarray([q], dtype=jnp.float64)
    zone = jnp.asarray([z], dtype=jnp.float64)
    pdet_tiny = pdet_fc(one, qone, zone, dL_tiny, p)
    pdet_huge = pdet_fc(one, qone, zone, dL_huge, p)
    logmiss_tiny = log_one_minus_pdet_fc(one, qone, zone, dL_tiny, p)

    ratio_both = np.asarray(shared_both) / np.maximum(np.asarray(ind_both), 1e-300)
    ratio_one = np.asarray(shared_one) / np.maximum(np.asarray(ind_one), 1e-300)

    return {
        "defaults": {
            "rho_thr": rho_thr,
            "r0": r0,
            "mc_bar": mc_bar,
            "pair_orientation_modes": list(PAIR_ORIENTATION_MODES),
        },
        "single": {
            "desired_threshold": _f64(desired_x),
            "dL_app": _f64(dL),
            "threshold": _f64(x),
            "pdet": _f64(pd),
            "log_miss": _f64(logmiss),
            "max_abs_threshold_error": float(
                np.max(np.abs(np.asarray(x) - desired_x))
            ),
            "pdet_tiny_distance": float(pdet_tiny[0]),
            "pdet_huge_distance": float(pdet_huge[0]),
            "logmiss_tiny_is_neginf": bool(np.isneginf(float(logmiss_tiny[0]))),
        },
        "theta_geometry": {
            "f_plus": _f64(fplus),
            "f_cross": _f64(fcross),
            "cos_iota": _f64(ci),
            "theta": _f64(theta_geom),
            "optimal_theta": float(theta_geom[0]),
        },
        "pairs": {
            "threshold_pairs": _f64(pair_x),
            "dL_plus": _f64(dLp),
            "dL_minus": _f64(dLm),
            "independent_both": _f64(ind_both),
            "independent_exactly_one": _f64(ind_one),
            "independent_both_manual": _f64(ind_both_manual),
            "independent_exactly_one_manual": _f64(ind_one_manual),
            "independent_both_max_abs_identity": float(
                np.max(np.abs(np.asarray(ind_both - ind_both_manual)))
            ),
            "independent_one_max_abs_identity": float(
                np.max(np.abs(np.asarray(ind_one - ind_one_manual)))
            ),
            "shared_iota_both": _f64(shared_both),
            "shared_iota_exactly_one": _f64(shared_one),
            "shared_over_independent_both": _f64(ratio_both),
            "shared_over_independent_exactly_one": _f64(ratio_one),
            "shared_both_swap_max_abs": float(
                np.max(np.abs(np.asarray(shared_both - shared_both_swap)))
            ),
            "shared_one_swap_max_abs": float(
                np.max(np.abs(np.asarray(shared_one - shared_one_swap)))
            ),
            "independent_log_partner_miss": _f64(ind_log_cond),
            "independent_log_partner_miss_alt_detected_distance": _f64(
                ind_log_cond_alt_det
            ),
            "partner_log_miss_marginal": _f64(partner_marginal),
            "independent_partner_miss_max_abs_identity": float(
                np.max(np.abs(np.asarray(ind_log_cond - partner_marginal)))
            ),
            "independent_partner_miss_detected_distance_max_abs": float(
                np.max(np.abs(np.asarray(ind_log_cond - ind_log_cond_alt_det)))
            ),
            "shared_iota_log_partner_miss": _f64(shared_log_cond),
            "invalid_mode_rejected": invalid_mode_rejected,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    import jax
    jax.config.update("jax_enable_x64", True)

    result = {
        "schema": "darksirens-lensing-l0b-sis-fcpdet-reference-1",
        "legacy_sha": LEGACY_SHA,
        "sis": _sis_probe(),
        "finn_chernoff": _fcpdet_probe(),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
