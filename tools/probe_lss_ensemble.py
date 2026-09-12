#!/usr/bin/env python3
"""Pinned-legacy Phase-10 L0C probe for loaded Q-ensemble semantics.

Oracle only. It freezes the loaded-member contract before L3 production code:
mean-Q deterministic fallback, per-member priors/normalizers, full-likelihood
logmeanexp marginalization, depth-edge interpolation, and K>=2 shared-member
provenance.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile

import h5py
import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"
LOGQ_CLIP = 7.0
SLOPES = np.array([-5.0, -1.5, 1.5, 5.0], dtype=float)


def _hash_array(value) -> str:
    arr = np.ascontiguousarray(np.asarray(value))
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode())
    h.update(repr(arr.shape).encode())
    h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def _error(fn):
    try:
        fn()
    except Exception as exc:
        return {"type": type(exc).__name__, "message": str(exc)}
    raise AssertionError("expected call to fail")


def _runtime_fixture():
    import jax
    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    from jax.scipy.special import logsumexp

    from darksirens.core.types import CosmoParams, EMCatalog, GWEvent, SurveyParams
    from darksirens.gw.populations import get_fixed_population_params
    from darksirens.likelihood.core import darksiren_log_likelihood
    from darksirens.redshift import zgrid
    from darksirens.redshift.completion import (
        _resolve_lss_completion_row_tables,
        build_pixel_kde_cache,
        completion_curves,
    )
    from darksirens.redshift.prior import (
        eval_redshift_prior_members_with_state,
        eval_redshift_prior_with_state,
        prepare_redshift_prior_state,
    )
    from darksirens.utils.cosmology import H0Planck, Om0Planck

    z_np = np.asarray(zgrid, dtype=float)
    ng = int(z_np.size)
    m = int(SLOPES.size)
    cosmo = CosmoParams(H0=H0Planck, Om0=Om0Planck)
    survey = SurveyParams(
        n0=1.0, z50=0.15, w=0.08, delta=0.0,
        b_miss=0.0, alpha_miss=1.0,
    )
    pop = jnp.asarray(get_fixed_population_params("powerlaw+peak"))

    def member_logq(i):
        return SLOPES[i] * (z_np - 0.2)

    def members_table():
        return np.stack([
            np.broadcast_to(member_logq(i), (2, ng)) for i in range(m)
        ])

    def dark_catalog(*, logq=None, logq_members=None):
        rows = [np.array([0.10, 0.12, 0.15]), np.array([0.28, 0.32])]
        zg = np.full((2, 3), 100.0)
        dz = np.full((2, 3), 1.0)
        w = np.zeros((2, 3))
        n = np.zeros(2, dtype=np.int32)
        for i, row in enumerate(rows):
            zg[i, : row.size] = row
            dz[i, : row.size] = 0.003
            w[i, : row.size] = 1.0
            n[i] = row.size
        zg, dz, w, n = (jnp.asarray(a) for a in (zg, dz, w, n))
        kde, idx = build_pixel_kde_cache(
            np.arange(2, dtype=np.int32), zg, 2, ngals=n
        )
        return EMCatalog(
            apix=1.0, zgals=zg, dzgals=dz, wgals=w, ngals=n,
            delta_g_pix_z=jnp.zeros((2, ng)),
            dN_obs_kde=kde, pixel_to_cache_idx=idx, unique_pixels=None,
            lss_completion_logq=(None if logq is None else jnp.asarray(logq)),
            lss_completion_logq_members=(
                None if logq_members is None else jnp.asarray(logq_members)
            ),
        )

    members = members_table()
    cat_ens = dark_catalog(logq_members=members)
    q_fallback, _ = _resolve_lss_completion_row_tables(cat_ens)
    q_fallback = np.asarray(q_fallback)
    manual_q = np.mean(np.exp(np.clip(members, -LOGQ_CLIP, LOGQ_CLIP)), axis=0)
    np.testing.assert_allclose(q_fallback, manual_q, rtol=2e-15, atol=0.0)
    wrong_q = np.exp(np.clip(np.mean(members, axis=0), -LOGQ_CLIP, LOGQ_CLIP))
    assert float(np.max(np.abs(q_fallback - wrong_q))) > 1e-3

    curves = completion_curves(cosmo, survey, cat_ens)
    state = prepare_redshift_prior_state("dark_sirens", cosmo, survey, cat_ens)
    assert curves.base_miss is not None
    assert curves.N_miss_members.shape == (m, 2)
    assert state.log_Z_members.shape == (m, 2)

    query_z = jnp.asarray([0.0755, 0.1111, 0.14725, 0.211, 0.2995, 0.371])
    query_pix = jnp.asarray([0, 0, 0, 1, 1, 1], dtype=jnp.int32)
    scalar_lp = np.asarray(eval_redshift_prior_with_state(
        "dark_sirens", state, query_z, query_pix, cosmo, survey, cat_ens
    ))
    member_lp = np.asarray(eval_redshift_prior_members_with_state(
        "dark_sirens", state, query_z, query_pix, cosmo, survey, cat_ens
    ))
    bayes_prior_lp = np.asarray(
        logsumexp(jnp.asarray(member_lp), axis=0) - np.log(m)
    )
    assert member_lp.shape == (m, query_z.size)
    assert np.all(np.isfinite(member_lp))

    # Depth relaxation is nodewise before interpolation. A query just above a
    # non-grid-aligned depth may therefore straddle one below-depth Q node. Once
    # both nodes are above depth, the LOCAL missing numerator is member-independent
    # (Q=1), but the normalized prior still differs through each member's global
    # row normalizer Z_m, which integrated the member-dependent lower-z budget.
    survey_depth = survey._replace(z_depth=0.25)
    state_depth = prepare_redshift_prior_state(
        "dark_sirens", cosmo, survey_depth, cat_ens
    )
    depth_member_lp = np.asarray(eval_redshift_prior_members_with_state(
        "dark_sirens", state_depth,
        jnp.asarray([0.249, 0.251, 0.40]),
        jnp.asarray([1, 1, 1], dtype=jnp.int32),
        cosmo, survey_depth, cat_ens,
    ))
    depth_edge_spread = float(np.ptp(depth_member_lp[:, 1]))
    depth_far_spread = float(np.ptp(depth_member_lp[:, 2]))
    depth_logz = np.asarray(state_depth.log_Z_members)[:, 1]
    far_relative = depth_member_lp[:, 2] - depth_member_lp[0, 2]
    normalizer_relative = -(depth_logz - depth_logz[0])
    depth_far_normalizer_max_abs = float(
        np.max(np.abs(far_relative - normalizer_relative))
    )
    assert depth_edge_spread > 1e-8
    assert depth_far_spread > 1e-8
    assert depth_far_normalizer_max_abs < 1e-12

    def gw(n_events, n_samp, seed):
        rng = np.random.default_rng(seed)
        total = n_events * n_samp
        m1det = jnp.asarray(rng.uniform(20.0, 60.0, total))
        m2det = jnp.asarray(rng.uniform(8.0, 30.0, total))
        dL = jnp.asarray(rng.uniform(420.0, 1500.0, total))
        chieff = jnp.asarray(rng.uniform(-0.2, 0.2, total))
        prior_wt = jnp.asarray(rng.uniform(0.5, 1.5, total))
        pixels = jnp.asarray(rng.integers(0, 2, total), dtype=jnp.int32)
        valid = jnp.ones(total, dtype=jnp.bool_)
        return GWEvent(
            m1det=m1det, m2det=m2det, dL=dL, chieff=chieff,
            prior_wt=prior_wt, pixels=pixels, q=m2det / m1det, valid=valid,
        )

    n_ev, n_samp, n_sel = 4, 64, 300
    gw_pe = gw(n_ev, n_samp, 0)
    gw_sel = gw(n_sel, 1, 10)

    def ll(cat_pe, *, cat_sel=None, marginalize=False, impl="factored"):
        cat_sel = cat_pe if cat_sel is None else cat_sel
        return darksiren_log_likelihood(
            cosmo, survey, pop, gw_pe, cat_pe, gw_sel, cat_sel,
            n_ev, n_samp, float(n_sel),
            pop_model="powerlaw+peak", universe_model="dark_sirens",
            sel_batch_size=None, lss_marginalize=marginalize,
            lss_member_impl=impl,
        )

    per_member_ll = np.asarray([
        float(ll(dark_catalog(logq=np.broadcast_to(member_logq(i), (2, ng)))))
        for i in range(m)
    ])
    expected_ll = float(logsumexp(jnp.asarray(per_member_ll)) - np.log(m))
    ll_factored = float(ll(cat_ens, marginalize=True, impl="factored"))
    ll_reference = float(ll(cat_ens, marginalize=True, impl="reference"))
    assert np.isfinite(ll_factored)
    assert abs(ll_factored - expected_ll) < 1e-6
    assert abs(ll_reference - expected_ll) < 1e-6
    assert float(np.ptp(per_member_ll)) > 1e-3

    mean_logq = np.log(q_fallback)
    ll_scalar_ensemble = float(ll(cat_ens, marginalize=False))
    ll_mean_q = float(ll(dark_catalog(logq=mean_logq), marginalize=False))
    assert abs(ll_scalar_ensemble - ll_mean_q) < 1e-6

    one_members = np.broadcast_to(member_logq(2), (1, 2, ng))
    ll_one_marg = float(ll(dark_catalog(logq_members=one_members), marginalize=True))
    ll_one_det = float(ll(
        dark_catalog(logq=np.broadcast_to(member_logq(2), (2, ng)))
    ))
    assert abs(ll_one_marg - ll_one_det) < 1e-6

    asymmetric_error = _error(lambda: ll(
        cat_ens, cat_sel=dark_catalog(logq=np.zeros((2, ng))), marginalize=True
    ))
    assert asymmetric_error["type"] == "ValueError"
    assert "SELECTION catalog" in asymmetric_error["message"]
    no_members_error = _error(lambda: ll(
        dark_catalog(logq=np.zeros((2, ng))), marginalize=True
    ))
    assert no_members_error["type"] == "ValueError"
    assert "ENSEMBLE" in no_members_error["message"]

    return {
        "n_grid": ng,
        "n_members": m,
        "slopes": SLOPES.tolist(),
        "member_table_hash": _hash_array(members),
        "fallback_q_hash": _hash_array(q_fallback),
        "manual_mean_q_hash": _hash_array(manual_q),
        "fallback_vs_manual_max_abs": float(np.max(np.abs(q_fallback - manual_q))),
        "fallback_vs_exp_mean_logq_max_abs": float(np.max(np.abs(q_fallback - wrong_q))),
        "base_miss_hash": _hash_array(np.asarray(curves.base_miss)),
        "N_miss_members": np.asarray(curves.N_miss_members, dtype=float).tolist(),
        "log_Z_members": np.asarray(state.log_Z_members, dtype=float).tolist(),
        "query_z": np.asarray(query_z, dtype=float).tolist(),
        "query_pix": np.asarray(query_pix, dtype=int).tolist(),
        "scalar_logp_mean_q": scalar_lp.tolist(),
        "member_logp": member_lp.tolist(),
        "bayes_prior_logmeanexp": bayes_prior_lp.tolist(),
        "depth_query_z": [0.249, 0.251, 0.40],
        "depth_member_logp": depth_member_lp.tolist(),
        "depth_log_Z_members_row1": depth_logz.tolist(),
        "depth_edge_member_spread": depth_edge_spread,
        "depth_far_member_spread": depth_far_spread,
        "depth_far_normalizer_relation_max_abs": depth_far_normalizer_max_abs,
        "per_member_log_likelihood": per_member_ll.tolist(),
        "logmeanexp_expected": expected_ll,
        "marginalized_factored": ll_factored,
        "marginalized_reference": ll_reference,
        "factored_minus_expected": ll_factored - expected_ll,
        "reference_minus_expected": ll_reference - expected_ll,
        "factored_minus_reference": ll_factored - ll_reference,
        "per_member_spread": float(np.ptp(per_member_ll)),
        "scalar_ensemble": ll_scalar_ensemble,
        "scalar_mean_q": ll_mean_q,
        "scalar_fallback_delta": ll_scalar_ensemble - ll_mean_q,
        "single_member_marginalized": ll_one_marg,
        "single_member_deterministic": ll_one_det,
        "single_member_delta": ll_one_marg - ll_one_det,
        "asymmetric_selection_error": asymmetric_error,
        "missing_members_error": no_members_error,
    }


def _write_survey(path: Path, seed: int):
    rng = np.random.default_rng(seed)
    nside, npix, maxgals = 1, 12, 4
    zgals = np.zeros((npix, maxgals))
    dzgals = np.full((npix, maxgals), 0.02)
    wgals = np.zeros((npix, maxgals))
    ngals = np.zeros(npix, dtype=np.int32)
    for pix in range(0, npix, 2):
        n = int(rng.integers(2, maxgals + 1))
        zgals[pix, :n] = rng.uniform(0.05, 0.4, size=n)
        wgals[pix, :n] = 1.0
        ngals[pix] = n
    with h5py.File(path, "w") as handle:
        handle.attrs["nside"] = nside
        handle.create_dataset("zgals", data=zgals)
        handle.create_dataset("dzgals", data=dzgals)
        handle.create_dataset("wgals", data=wgals)
        handle.create_dataset("ngals", data=ngals)
    return str(path)


def _provenance_probe(tmp: Path):
    from darksirens.inference.loaders import load_multitracer_catalog_bundles
    from darksirens.redshift.grid import zgrid
    from darksirens.redshift.lognormal_completion import (
        load_lss_completion_hdf5,
        save_lss_completion_hdf5,
    )

    z = np.asarray(zgrid)
    ngrid, npix = z.size, 12

    def members(seed, m=3):
        return np.random.default_rng(seed).normal(
            size=(m, npix, ngrid)
        ).astype(float)

    def save_q(path, *, seed, m=3, rid=None, with_members=True):
        save_lss_completion_hdf5(
            str(path), logq_map=np.zeros((npix, ngrid)),
            logq_members=members(seed, m=m) if with_members else None,
            zgrid=z, realization_set_id=rid,
        )
        return str(path)

    def legacy_q(path, *, seed, m=3):
        with h5py.File(path, "w") as handle:
            grp = handle.create_group("lss_completion")
            grp.create_dataset("logq_map", data=np.zeros((npix, ngrid)))
            grp.create_dataset("logq_members", data=members(seed, m=m))
            grp.create_dataset("zgrid", data=z)
            grp.attrs["indexing"] = "compact"
        return str(path)

    def gw_inputs(n=4):
        rng = np.random.default_rng(0)
        return {
            "ra": rng.uniform(0.0, 2 * np.pi, n),
            "dec": rng.uniform(-np.pi / 2, np.pi / 2, n),
            "rasels": rng.uniform(0.0, 2 * np.pi, n),
            "decsels": rng.uniform(-np.pi / 2, np.pi / 2, n),
        }

    s1 = _write_survey(tmp / "surveyA.h5", 11)
    s2 = _write_survey(tmp / "surveyB.h5", 22)

    def opts(qs, **overrides):
        base = dict(
            survey_paths=[s1, s2], lss_completions=list(qs),
            universe_model="dark_sirens", lss_marginalize=True,
            use_LSS=False, mark_model="none", mark_names_by_catalog=None,
            catalog_sky_weighting="conditional", validate_completion=False,
            allow_unverified_shared_lss_members=False, n_catalogs=2,
        )
        base.update(overrides)
        return SimpleNamespace(**base)

    shared = "0123456789abcdef0123456789abcdef"
    qa = save_q(tmp / "qa.h5", seed=100, rid=shared)
    qb = save_q(tmp / "qb.h5", seed=200, rid=shared)
    la, lb = load_lss_completion_hdf5(qa), load_lss_completion_hdf5(qb)
    assert la["realization_set_id"] == lb["realization_set_id"] == shared
    assert la["member_content_sha256"] != lb["member_content_sha256"]
    assert la["n_members"] == lb["n_members"] == 3
    assert len(load_multitracer_catalog_bundles(opts([qa, qb]), gw_inputs())) == 2

    qx = save_q(tmp / "qx.h5", seed=300)
    qy = save_q(tmp / "qy.h5", seed=400)
    distinct_id_error = _error(lambda: load_multitracer_catalog_bundles(
        opts([qx, qy]), gw_inputs()
    ))
    assert distinct_id_error["type"] == "ValueError"
    assert "SHARED member index" in distinct_id_error["message"]
    assert "realization_set_id" in distinct_id_error["message"]

    legacy_a = legacy_q(tmp / "legacyA.h5", seed=500)
    legacy_b = legacy_q(tmp / "legacyB.h5", seed=600)
    legacy_error = _error(lambda: load_multitracer_catalog_bundles(
        opts([legacy_a, legacy_b]), gw_inputs()
    ))
    assert legacy_error["type"] == "ValueError"
    assert "LEGACY (no provenance)" in legacy_error["message"]

    q_short = save_q(tmp / "qshort.h5", seed=700, m=2, rid=shared)
    unequal_m_error = _error(lambda: load_multitracer_catalog_bundles(
        opts([qa, q_short], allow_unverified_shared_lss_members=True), gw_inputs()
    ))
    assert unequal_m_error["type"] == "ValueError"
    assert "EQUAL" in unequal_m_error["message"]

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        allowed = load_multitracer_catalog_bundles(
            opts([qx, qy], allow_unverified_shared_lss_members=True), gw_inputs()
        )
    warning = stdout.getvalue()
    assert len(allowed) == 2
    assert "INDEPENDENT-fields" in warning and "product prior" in warning

    deterministic = load_multitracer_catalog_bundles(
        opts([qx, qy], lss_marginalize=False), gw_inputs()
    )
    assert len(deterministic) == 2

    return {
        "shared_realization_set_id": shared,
        "shared_A_member_sha256": la["member_content_sha256"],
        "shared_B_member_sha256": lb["member_content_sha256"],
        "shared_content_hashes_differ": True,
        "shared_n_members": int(la["n_members"]),
        "shared_guard_passed": True,
        "distinct_id_error": distinct_id_error,
        "legacy_error": legacy_error,
        "unequal_m_error": unequal_m_error,
        "allow_unverified_warning_contains_independent_fields": True,
        "deterministic_skips_shared_member_guard": True,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-legacy-sha", default=LEGACY_SHA)
    args = parser.parse_args(argv)

    runtime = _runtime_fixture()
    with tempfile.TemporaryDirectory(prefix="darksirens-lss-l0c-") as td:
        provenance = _provenance_probe(Path(td))
    result = {
        "schema": "darksirens-lss-l0c-reference-1",
        "legacy_sha": args.expected_legacy_sha,
        "runtime": runtime,
        "provenance": provenance,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
