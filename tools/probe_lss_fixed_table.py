#!/usr/bin/env python3
"""Deterministic Phase-10 L0B probe of fixed-table Q consumption.

This is a pinned-legacy oracle, not production code.  It freezes the mature
DETERMINISTIC table path before ``darksirens-lss`` is allowed to implement a
``RedshiftModel``:

* compact vs global row alignment;
* off-footprint unity when the global table carries bit-zero logQ there;
* table logQ clipping at +/-7 before exponentiation;
* exact Q=1 behavior above an explicitly pinned support block;
* hard N_grid/zgrid mismatch errors (no silent Q interpolation);
* c_mode provenance mismatch failure in the loader;
* interpolation of the fully assembled redshift prior at off-grid query z.

Run in a process whose PYTHONPATH resolves the pinned legacy repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile

import numpy as np


LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


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


def _catalog_helpers(zgrid):
    import jax.numpy as jnp
    from darksirens.core.types import EMCatalog
    from darksirens.redshift.completion import build_pixel_kde_cache

    ng = int(zgrid.size)

    def tiny(unique_pixels=None, **extra):
        zg = np.full((2, 3), 100.0)
        zg[0, :2] = [0.10, 0.15]
        zg[1, :1] = [0.20]
        n = np.array([2, 1], dtype=np.int32)
        base = dict(
            apix=1.0,
            zgals=jnp.asarray(zg),
            dzgals=jnp.asarray(np.full((2, 3), 0.01)),
            wgals=jnp.zeros((2, 3)),
            ngals=jnp.asarray(n),
            delta_g_pix_z=jnp.zeros((1, ng)),
            dN_obs_kde=None,
            pixel_to_cache_idx=None,
            unique_pixels=(
                None
                if unique_pixels is None
                else jnp.asarray(unique_pixels, jnp.int32)
            ),
        )
        base.update(extra)
        return EMCatalog(**base)

    def prior(**extra):
        rows = [np.array([0.10, 0.12, 0.15]), np.array([0.30, 0.34])]
        n_rows, nmax = 2, 3
        zg = np.full((n_rows, nmax), 100.0)
        dz = np.full((n_rows, nmax), 1.0)
        w = np.zeros((n_rows, nmax))
        n = np.zeros(n_rows, dtype=np.int32)
        for i, r in enumerate(rows):
            zg[i, : len(r)] = r
            dz[i, : len(r)] = 0.003
            w[i, : len(r)] = 1.0
            n[i] = len(r)
        zg, dz, w, n = (jnp.asarray(a) for a in (zg, dz, w, n))
        kde, idx = build_pixel_kde_cache(
            np.arange(n_rows, dtype=np.int32), zg, n_rows, ngals=n
        )
        return EMCatalog(
            apix=1.0,
            zgals=zg,
            dzgals=dz,
            wgals=w,
            ngals=n,
            delta_g_pix_z=jnp.zeros((1, ng)),
            dN_obs_kde=kde,
            pixel_to_cache_idx=idx,
            unique_pixels=None,
            **extra,
        )

    return tiny, prior


def _runtime_probe():
    import jax.numpy as jnp
    from darksirens.core.types import CosmoParams, SurveyParams
    from darksirens.redshift import zgrid
    from darksirens.redshift.completion import completion_curves
    from darksirens.redshift.prior import (
        eval_redshift_prior_with_state,
        prepare_redshift_prior_state,
    )

    z = np.asarray(zgrid, dtype=float)
    ng = int(z.size)
    cosmo = CosmoParams(H0=67.74, Om0=0.3075)
    survey = SurveyParams(
        n0=1e-2,
        z50=0.3,
        w=0.1,
        delta=0.0,
        b_miss=0.0,
        alpha_miss=1.0,
    )
    tiny, prior_catalog = _catalog_helpers(zgrid)

    unity = completion_curves(
        cosmo,
        survey,
        tiny(lss_completion_logq=jnp.zeros((2, ng))),
    )

    compact_table = np.stack(
        [np.full(ng, np.log(3.0)), np.full(ng, np.log(5.0))]
    )
    compact = completion_curves(
        cosmo,
        survey,
        tiny(
            lss_completion_logq=jnp.asarray(compact_table),
            lss_completion_indexing=1,
        ),
    )

    global_table = np.zeros((6, ng))
    global_table[5] = np.log(3.0)
    global_table[2] = np.log(5.0)
    global_curves = completion_curves(
        cosmo,
        survey,
        tiny(
            unique_pixels=[5, 2],
            lss_completion_logq=jnp.asarray(global_table),
            lss_completion_indexing=2,
        ),
    )

    compact_arr = np.asarray(compact.dN_miss)
    global_arr = np.asarray(global_curves.dN_miss)
    np.testing.assert_array_equal(compact_arr, global_arr)

    # A global row representing off-footprint sky is encoded as bit-zero logQ,
    # hence exactly Q=1 when consumed.  Pixel 5 is deliberately modulated;
    # pixel 8 is the off-footprint identity row.
    off_table = np.zeros((9, ng))
    off_table[5] = np.log(3.0)
    off = completion_curves(
        cosmo,
        survey,
        tiny(
            unique_pixels=[5, 8],
            lss_completion_logq=jnp.asarray(off_table),
            lss_completion_indexing=2,
        ),
    )
    off_unity = completion_curves(
        cosmo,
        survey,
        tiny(
            unique_pixels=[5, 8],
            lss_completion_logq=jnp.zeros((9, ng)),
            lss_completion_indexing=2,
        ),
    )
    np.testing.assert_array_equal(
        np.asarray(off.dN_miss[1]), np.asarray(off_unity.dN_miss[1])
    )

    # Synthetic support table: Q=2 only through z<=0.30, then bit-zero logQ.
    # This isolates the CONSUMER contract: above the builder-pinned support the
    # table is the exact identity, not a small extrapolated correction.
    support = np.zeros((2, ng))
    support[:, z <= 0.30] = np.log(2.0)
    supported = completion_curves(
        cosmo,
        survey,
        tiny(lss_completion_logq=jnp.asarray(support)),
    )
    unity_arr = np.asarray(unity.dN_miss)
    support_arr = np.asarray(supported.dN_miss)
    live = unity_arr > 0.0
    ratio = np.divide(
        support_arr,
        unity_arr,
        out=np.ones_like(support_arr),
        where=live,
    )
    below = (z <= 0.30)[None, :] & live
    above = (z > 0.30)[None, :] & live
    assert np.max(np.abs(ratio[below] - 2.0)) < 2e-12
    assert np.max(np.abs(ratio[above] - 1.0)) == 0.0

    # Mature table rail: clip logQ to +/-7 before exponentiation.
    clipped_table = np.stack([np.full(ng, 20.0), np.full(ng, -20.0)])
    clipped = completion_curves(
        cosmo,
        survey,
        tiny(lss_completion_logq=jnp.asarray(clipped_table)),
    )
    clip_ratio = np.divide(
        np.asarray(clipped.dN_miss),
        unity_arr,
        out=np.ones_like(unity_arr),
        where=live,
    )
    np.testing.assert_allclose(
        clip_ratio[0, live[0]], np.exp(7.0), rtol=2e-12, atol=0.0
    )
    np.testing.assert_allclose(
        clip_ratio[1, live[1]], np.exp(-7.0), rtol=2e-12, atol=0.0
    )

    grid_error = _error(
        lambda: completion_curves(
            cosmo,
            survey,
            tiny(lss_completion_logq=jnp.zeros((2, ng + 1))),
        )
    )

    # Freeze the assembled-prior interpolation separately from Q-table
    # consumption.  Q itself lives node-for-node on package zgrid; the prior is
    # queried at arbitrary event redshifts after preparation.
    phase = np.linspace(0.0, 2.0 * np.pi, ng)
    prior_logq = np.stack(
        [0.40 * np.sin(phase), -0.30 * np.cos(phase)]
    )
    cat_q = prior_catalog(lss_completion_logq=jnp.asarray(prior_logq))
    cat_1 = prior_catalog(lss_completion_logq=jnp.zeros((2, ng)))
    state_q = prepare_redshift_prior_state("dark_sirens", cosmo, survey, cat_q)
    state_1 = prepare_redshift_prior_state("dark_sirens", cosmo, survey, cat_1)
    query_z = jnp.asarray([0.055, 0.1105, 0.13725, 0.251, 0.3333, 0.701])
    query_pix = jnp.asarray([0, 0, 0, 1, 1, 1], dtype=jnp.int32)
    lp_q = np.asarray(
        eval_redshift_prior_with_state(
            "dark_sirens", state_q, query_z, query_pix, cosmo, survey, cat_q
        )
    )
    lp_1 = np.asarray(
        eval_redshift_prior_with_state(
            "dark_sirens", state_1, query_z, query_pix, cosmo, survey, cat_1
        )
    )
    assert np.all(np.isfinite(lp_q))
    assert np.max(np.abs(lp_q - lp_1)) > 1e-5

    return {
        "n_grid": ng,
        "zgrid_hash": _hash_array(z),
        "unity_dN_miss_hash": _hash_array(unity_arr),
        "compact_dN_miss_hash": _hash_array(compact_arr),
        "global_dN_miss_hash": _hash_array(global_arr),
        "compact_global_bit_identical": True,
        "compact_N_miss": np.asarray(compact.N_miss, dtype=float).tolist(),
        "off_footprint_row_hash": _hash_array(np.asarray(off.dN_miss[1])),
        "off_footprint_unity_hash": _hash_array(np.asarray(off_unity.dN_miss[1])),
        "off_footprint_bit_identical_to_unity": True,
        "support_logq_hash": _hash_array(support),
        "support_dN_miss_hash": _hash_array(support_arr),
        "support_below_max_abs_ratio_minus_2": float(
            np.max(np.abs(ratio[below] - 2.0))
        ),
        "support_above_max_abs_ratio_minus_1": float(
            np.max(np.abs(ratio[above] - 1.0))
        ),
        "clip_row0_ratio": float(np.median(clip_ratio[0, live[0]])),
        "clip_row1_ratio": float(np.median(clip_ratio[1, live[1]])),
        "clip_dN_miss_hash": _hash_array(np.asarray(clipped.dN_miss)),
        "grid_mismatch_error": grid_error,
        "prior_query_z": np.asarray(query_z, dtype=float).tolist(),
        "prior_query_pix": np.asarray(query_pix, dtype=int).tolist(),
        "prior_logq_table_hash": _hash_array(prior_logq),
        "prior_logp_q": lp_q.tolist(),
        "prior_logp_unity": lp_1.tolist(),
        "prior_logp_q_hash": _hash_array(lp_q),
        "prior_logp_unity_hash": _hash_array(lp_1),
        "prior_max_abs_q_effect": float(np.max(np.abs(lp_q - lp_1))),
    }


def _loader_probe(tmp: Path):
    from darksirens.catalogs.lss import maybe_load_lss_completion
    from darksirens.redshift import zgrid
    from darksirens.redshift.lognormal_completion import save_lss_completion_hdf5

    z = np.asarray(zgrid, dtype=float)
    ng = int(z.size)
    path = tmp / "fixed_q.h5"
    table = np.zeros((4, ng))
    table[1] = 0.1
    table[3] = -0.2
    save_lss_completion_hdf5(
        str(path),
        logq_map=table,
        zgrid=z,
        indexing="global",
        completion_kind="map",
        metadata={"converged": True, "n_converged": 4, "n_rows": 4},
        realization_set_id="phase10-l0b-fixed",
        budget_renormalized=False,
        c_mode="aggregate",
        f_p_aware=True,
        q_support_depth=0.3,
    )

    def opts(**overrides):
        base = dict(
            lss_completion=str(path),
            survey_path=None,
            universe_model="dark_sirens",
            c_mode="aggregate",
            lss_marginalize=False,
        )
        base.update(overrides)
        return SimpleNamespace(**base)

    loaded = maybe_load_lss_completion(opts(), zgrid=zgrid)
    assert loaded["lss_completion_indexing"] == 2
    np.testing.assert_array_equal(loaded["lss_completion_logq"], table)
    assert loaded["lss_completion_provenance"]["realization_set_id"] == "phase10-l0b-fixed"
    assert loaded["lss_completion_provenance"]["f_p_aware"] is True

    cmode_error = _error(
        lambda: maybe_load_lss_completion(opts(c_mode="per_pixel"), zgrid=zgrid)
    )

    # Same N_grid but numerically shifted zgrid: loader must refuse rather than
    # silently interpolate Q onto the package grid.
    shifted = np.asarray(zgrid, dtype=float).copy()
    shifted[1:] += 2e-4
    shifted_path = tmp / "shifted_q.h5"
    save_lss_completion_hdf5(
        str(shifted_path),
        logq_map=table,
        zgrid=shifted,
        indexing="global",
        completion_kind="map",
        metadata={"converged": True, "n_converged": 4, "n_rows": 4},
        budget_renormalized=False,
        c_mode="aggregate",
    )
    zgrid_error = _error(
        lambda: maybe_load_lss_completion(
            opts(lss_completion=str(shifted_path)), zgrid=zgrid
        )
    )

    return {
        "table_hash": _hash_array(table),
        "loaded_table_hash": _hash_array(loaded["lss_completion_logq"]),
        "indexing_enum": int(loaded["lss_completion_indexing"]),
        "provenance": loaded["lss_completion_provenance"],
        "c_mode_mismatch_error": cmode_error,
        "shifted_zgrid_error": zgrid_error,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-legacy-sha", default=LEGACY_SHA)
    args = parser.parse_args(argv)

    runtime = _runtime_probe()
    with tempfile.TemporaryDirectory(prefix="darksirens-lss-l0b-") as td:
        loader = _loader_probe(Path(td))

    result = {
        "schema": "darksirens-lss-l0b-reference-1",
        "legacy_sha": args.expected_legacy_sha,
        "runtime": runtime,
        "loader": loader,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
