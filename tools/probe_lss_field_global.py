#!/usr/bin/env python3
"""Deterministic Phase-10 L7 probe of the pinned legacy field-global seam.

Freezes the minimum algebra needed before production L7 code:

* survey-global field normalizer with aggregate C_p = f_p C(z);
* latent/gauge-conserving Q members leave each tracer's global Z unchanged;
* K=1 global-Z cancellation between PE and selection reductions;
* K>=2 catalog mixtures depend on RELATIVE per-tracer global Z_k;
* a common shift of every Z_k remains an overall normalization and cancels;
* matched member indices are a composition property, not a table provenance id.

The probe intentionally excludes marked hosts, stratified selection, and the
rung-1 theta-response approximation. Those are not needed to freeze L7's
normalization/composition boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _f64(x):
    return np.asarray(x, dtype=np.float64).tolist()


def _hash_array(x):
    a = np.ascontiguousarray(np.asarray(x))
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(repr(a.shape).encode())
    h.update(a.tobytes(order="C"))
    return h.hexdigest()


def _logmeanexp(x):
    import jax.numpy as jnp
    from jax.scipy.special import logsumexp

    x = jnp.asarray(x)
    return logsumexp(x) - jnp.log(jnp.asarray(x.size, dtype=x.dtype))


def _build_tracer(label: str, *, variant: int):
    import jax.numpy as jnp

    from darksirens.core.types import (
        C_MODE_AGGREGATE_STRUCT,
        CosmoParams,
        EMCatalog,
        SurveyParams,
    )
    from darksirens.redshift import zgrid
    from darksirens.redshift.completion import (
        build_field_depth_inputs,
        build_field_normalization_inputs,
    )

    n_pix, maxg = 4, 4
    z = np.zeros((n_pix, maxg), dtype=float)
    w = np.zeros_like(z)
    n = np.zeros(n_pix, dtype=np.int32)

    if variant == 0:
        vals = ((0, [0.075, 0.125, 0.175]), (1, [0.235, 0.285]))
        fp = np.asarray([0.88, 0.57, 0.0, 0.0], dtype=float)
        n0 = 1.0e-8
        delta = 0.15
    else:
        vals = ((0, [0.095, 0.155]), (1, [0.205, 0.255, 0.305, 0.335]))
        fp = np.asarray([0.72, 0.93, 0.0, 0.0], dtype=float)
        n0 = 1.65e-8
        delta = -0.10

    for p, zz in vals:
        n[p] = len(zz)
        z[p, : len(zz)] = zz
        w[p, : len(zz)] = 1.0
    dz = np.full_like(z, 0.012)

    fobs, n_empty, nobs, occ = build_field_normalization_inputs(
        jnp.asarray(z), jnp.asarray(w), jnp.asarray(n)
    )
    depth = build_field_depth_inputs(
        jnp.asarray(z), jnp.asarray(dz), jnp.asarray(w), jnp.asarray(n)
    )
    apix = np.pi  # four equal pixels span 4*pi in this toy
    empty = np.setdiff1d(np.arange(n_pix), np.asarray(occ))
    cat = EMCatalog(
        apix=apix,
        zgals=jnp.asarray(z),
        dzgals=jnp.asarray(dz),
        wgals=jnp.asarray(w),
        ngals=jnp.asarray(n),
        delta_g_pix_z=jnp.zeros((1, len(zgrid))),
        dN_obs_kde=None,
        pixel_to_cache_idx=None,
        field_dN_obs_s=fobs,
        field_n_empty=jnp.asarray(float(n_empty)),
        field_N_obs_total=jnp.asarray(float(nobs)),
        field_occupied_pixels=jnp.asarray(occ, dtype=jnp.int32),
        field_depth_z=depth.z,
        field_depth_dz=depth.dz,
        field_depth_c=depth.c,
        f_p_rows=jnp.asarray(fp, dtype=jnp.float32),
        field_f_p_occ=jnp.asarray(fp[np.asarray(occ)], dtype=jnp.float32),
        field_f_p_empty_sum=jnp.asarray(float(fp[empty].sum())),
        f_p_total_sum=jnp.asarray(float(fp.sum())),
    )
    survey = SurveyParams(
        n0=n0,
        z50=0.6,
        w=0.2,
        delta=delta,
        b_miss=1.0,
        alpha_miss=1.0,
        sigma_kde=0.012,
        z_depth=0.35,
        c_mode=C_MODE_AGGREGATE_STRUCT,
    )
    cosmo = CosmoParams(H0=67.74, Om0=0.3075, w0=-1.0, wa=0.0)
    return label, cosmo, survey, cat, fp


def _gauge_members(cosmo, survey, cat, fp, amplitudes):
    from darksirens.redshift import zgrid
    from darksirens.redshift.completion import _precompute_grids

    grids = _precompute_grids(cosmo, survey, cat)
    cbar = np.clip(np.asarray(grids.C_bar_raw, dtype=float), 0.0, 1.0)
    occ = np.asarray(cat.field_occupied_pixels, dtype=int)
    assert occ.size == 2
    f = fp[occ]
    w0 = 1.0 - f[0] * cbar
    w1 = 1.0 - f[1] * cbar
    support = np.asarray(zgrid) <= float(survey.z_depth)
    shape = np.exp(-0.5 * ((np.asarray(zgrid) - 0.19) / 0.095) ** 2)

    members = []
    for amp in amplitudes:
        q0 = np.exp(float(amp) * shape)
        q1 = 1.0 - (w0 / w1) * (q0 - 1.0)
        q0 = np.where(support, q0, 1.0)
        q1 = np.where(support, q1, 1.0)
        if not (np.all(q0 > 0.0) and np.all(q1 > 0.0)):
            raise RuntimeError("toy gauge member left positive-Q support")
        members.append(np.stack([q0, q1], axis=0))
    return cbar, np.asarray(members)


def _global_probe(label, cosmo, survey, cat, fp, amplitudes):
    from darksirens.redshift.completion import _field_missing_curve, field_global_log_Z

    cbar, members = _gauge_members(cosmo, survey, cat, fp, amplitudes)
    unity = np.ones_like(members[0])
    logz0 = float(field_global_log_Z(cosmo, survey, cat, latent_q_rows=unity))
    V0, _ = _field_missing_curve(cosmo, survey, cat, latent_q_rows=unity)
    logzs, vdiff, gauge_resid = [], [], []
    occ = np.asarray(cat.field_occupied_pixels, dtype=int)
    f = fp[occ]
    for q in members:
        logzs.append(float(field_global_log_Z(cosmo, survey, cat, latent_q_rows=q)))
        V, _ = _field_missing_curve(cosmo, survey, cat, latent_q_rows=q)
        vdiff.append(float(np.max(np.abs(np.asarray(V) - np.asarray(V0)))))
        ww = 1.0 - f[:, None] * cbar[None, :]
        lhs = np.sum(ww * q, axis=0)
        rhs = np.sum(ww, axis=0)
        gauge_resid.append(float(np.max(np.abs(lhs - rhs))))

    return {
        "label": label,
        "cbar_min": float(np.min(cbar)),
        "cbar_max": float(np.max(cbar)),
        "cbar_hash": _hash_array(cbar),
        "unity_logZ": logz0,
        "member_logZ": logzs,
        "member_logZ_spread": float(np.ptp(logzs)),
        "missing_curve_max_abs_vs_unity": vdiff,
        "gauge_max_abs": gauge_resid,
        "member_q_hash": _hash_array(members),
    }, members


def _eval_field(state, cosmo, survey, cat, z, pix):
    import jax.numpy as jnp
    from darksirens.redshift.prior import eval_redshift_prior_with_state

    return np.asarray(
        eval_redshift_prior_with_state(
            "dark_sirens",
            state,
            jnp.asarray(z, dtype=float),
            jnp.asarray(pix, dtype=jnp.int32),
            cosmo,
            survey,
            cat,
            catalog_sky_weighting="field",
        ),
        dtype=float,
    )


def _mixture_logp(logps, logw):
    import jax.numpy as jnp
    from jax.scipy.special import logsumexp

    arr = jnp.stack([jnp.asarray(x) for x in logps], axis=0)
    return np.asarray(logsumexp(jnp.asarray(logw)[:, None] + arr, axis=0))


def _composition_probe(A, B):
    import jax.numpy as jnp
    from darksirens.redshift.prior import prepare_redshift_prior_state

    _, ca, sa, cata, _ = A
    _, cb, sb, catb, _ = B
    sta = prepare_redshift_prior_state(
        "dark_sirens", ca, sa, cata, catalog_sky_weighting="field"
    )
    stb = prepare_redshift_prior_state(
        "dark_sirens", cb, sb, catb, catalog_sky_weighting="field"
    )

    pe_z = np.asarray([0.09, 0.13, 0.18, 0.24, 0.29])
    pe_p = np.asarray([0, 0, 1, 1, 0], dtype=np.int32)
    se_z = np.asarray([0.07, 0.16, 0.21, 0.30, 0.34, 0.11, 0.27])
    se_p = np.asarray([1, 0, 0, 1, 1, 1, 0], dtype=np.int32)
    N = 3.0

    lpa_pe = _eval_field(sta, ca, sa, cata, pe_z, pe_p)
    lpa_se = _eval_field(sta, ca, sa, cata, se_z, se_p)
    ll1 = float(N * (_logmeanexp(lpa_pe) - _logmeanexp(lpa_se)))
    shift = 0.731
    sta_shift = sta._replace(log_Z_global=sta.log_Z_global + shift)
    lpa_pe_s = _eval_field(sta_shift, ca, sa, cata, pe_z, pe_p)
    lpa_se_s = _eval_field(sta_shift, ca, sa, cata, se_z, se_p)
    ll1s = float(N * (_logmeanexp(lpa_pe_s) - _logmeanexp(lpa_se_s)))

    lpb_pe = _eval_field(stb, cb, sb, catb, pe_z, pe_p)
    lpb_se = _eval_field(stb, cb, sb, catb, se_z, se_p)
    logw = np.log(np.asarray([0.37, 0.63]))
    mix_pe = _mixture_logp((lpa_pe, lpb_pe), logw)
    mix_se = _mixture_logp((lpa_se, lpb_se), logw)
    ll2 = float(N * (_logmeanexp(mix_pe) - _logmeanexp(mix_se)))

    stb_rel = stb._replace(log_Z_global=stb.log_Z_global + shift)
    lpb_pe_rel = _eval_field(stb_rel, cb, sb, catb, pe_z, pe_p)
    lpb_se_rel = _eval_field(stb_rel, cb, sb, catb, se_z, se_p)
    ll2_rel = float(
        N
        * (
            _logmeanexp(_mixture_logp((lpa_pe, lpb_pe_rel), logw))
            - _logmeanexp(_mixture_logp((lpa_se, lpb_se_rel), logw))
        )
    )

    sta_com = sta._replace(log_Z_global=sta.log_Z_global + shift)
    stb_com = stb._replace(log_Z_global=stb.log_Z_global + shift)
    ll2_com = float(
        N
        * (
            _logmeanexp(
                _mixture_logp(
                    (
                        _eval_field(sta_com, ca, sa, cata, pe_z, pe_p),
                        _eval_field(stb_com, cb, sb, catb, pe_z, pe_p),
                    ),
                    logw,
                )
            )
            - _logmeanexp(
                _mixture_logp(
                    (
                        _eval_field(sta_com, ca, sa, cata, se_z, se_p),
                        _eval_field(stb_com, cb, sb, catb, se_z, se_p),
                    ),
                    logw,
                )
            )
        )
    )

    za, zb = float(sta.log_Z_global), float(stb.log_Z_global)
    num_a = lpa_pe + za
    num_b = lpb_pe + zb
    mix_manual = np.asarray(
        jnp.logaddexp(
            logw[0] + jnp.asarray(num_a) - za,
            logw[1] + jnp.asarray(num_b) - zb,
        )
    )

    return {
        "logZ_A": za,
        "logZ_B": zb,
        "logZ_difference_B_minus_A": zb - za,
        "K1_reduced": ll1,
        "K1_shifted": ll1s,
        "K1_shift_delta": ll1s - ll1,
        "K2_reduced": ll2,
        "K2_relative_B_shifted": ll2_rel,
        "K2_relative_shift_delta": ll2_rel - ll2,
        "K2_common_shifted": ll2_com,
        "K2_common_shift_delta": ll2_com - ll2,
        "mixture_manual_max_abs": float(np.max(np.abs(mix_manual - mix_pe))),
        "mixture_pe": _f64(mix_pe),
        "mixture_selection": _f64(mix_se),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    amplitudes = np.asarray([-0.065, -0.020, 0.035, 0.070])
    A = _build_tracer("A", variant=0)
    B = _build_tracer("B", variant=1)
    ga, qa = _global_probe(*A, amplitudes)
    gb, qb = _global_probe(*B, amplitudes)

    center = min(200, qa.shape[-1] - 1)
    a_series = qa[:, 0, center]
    b_series = qb[:, 0, center]
    corr = float(np.corrcoef(a_series, b_series)[0, 1])
    corr_reversed = float(np.corrcoef(a_series, b_series[::-1])[0, 1])

    result = {
        "schema": "darksirens-lss-l7-field-global-reference-1",
        "legacy_sha": LEGACY_SHA,
        "amplitudes": _f64(amplitudes),
        "tracer_A": ga,
        "tracer_B": gb,
        "shared_member_axis": {
            "q_at_node_A": _f64(a_series),
            "q_at_node_B": _f64(b_series),
            "matched_correlation": corr,
            "reversed_correlation": corr_reversed,
        },
        "composition": _composition_probe(A, B),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
