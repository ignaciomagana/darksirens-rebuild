#!/usr/bin/env python3
"""Deterministic Phase-10 L0A probe of the pinned legacy Q/LSS artifact seam.

This freezes the smallest reusable LSS contract before ``darksirens-lss`` gets
any production code:

* Gaussian radial-field spectrum convention;
* radial Poisson-lognormal matched-count MAP behavior;
* deterministic Laplace members at fixed seed;
* per-z mean-one missing-budget renormalization for a map and member cube;
* zero-budget-bin no-op behavior;
* HDF5 table/member schema and provenance stamps;
* fail-closed writer behavior for poisoned tables / false budget claims.

It deliberately does NOT freeze GP3D, latent-field, multitracer, or GW
likelihood behavior. Those are later reference slices.

Run in a process whose PYTHONPATH resolves the pinned legacy ``darksirens``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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


def _f64_list(value):
    return np.asarray(value, dtype=np.float64).tolist()


def _spectrum_probe(api) -> dict:
    pk = api.gaussian_correlation_spectrum(
        64,
        ell_grid=5.0,
        sigma=0.3,
        floor_frac=1e-8,
    )
    return {
        "shape": list(pk.shape),
        "mean": float(np.mean(pk)),
        "min": float(np.min(pk)),
        "max": float(np.max(pk)),
        "first8": _f64_list(pk[:8]),
        "hash": _hash_array(pk),
    }


def _budget_probe(api) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(20260912)
    n_rows, n_grid = 5, 16

    logq = 0.7 * rng.standard_normal((n_rows, n_grid))
    weights = rng.uniform(0.1, 3.0, size=(n_rows, n_grid))
    weights[:, 3] = 0.0
    weights[0, 9] = 0.0

    map_out, map_mono = api.renormalize_q_mean_one(logq, weights)

    cube = 0.5 * rng.standard_normal((4, n_rows, n_grid))
    member_out, member_mono = api.renormalize_q_mean_one(cube, weights)

    den = np.sum(weights, axis=0)
    supported = den > 0.0
    map_mean = np.divide(
        np.sum(weights * np.exp(map_out), axis=0),
        den,
        out=np.ones_like(den),
        where=supported,
    )
    member_mean = np.stack(
        [
            np.divide(
                np.sum(weights * np.exp(member_out[m]), axis=0),
                den,
                out=np.ones_like(den),
                where=supported,
            )
            for m in range(member_out.shape[0])
        ]
    )

    assert np.max(np.abs(map_mean[supported] - 1.0)) < 1e-12
    assert np.max(np.abs(member_mean[:, supported] - 1.0)) < 1e-12
    assert map_mono[3] == 0.0
    np.testing.assert_array_equal(map_out[:, 3], logq[:, 3])
    np.testing.assert_array_equal(member_out[:, :, 3], cube[:, :, 3])

    result = {
        "shape": list(map_out.shape),
        "member_shape": list(member_out.shape),
        "zero_budget_bins": np.flatnonzero(~supported).astype(int).tolist(),
        "map_weighted_mean_q": _f64_list(map_mean),
        "member_weighted_mean_q": _f64_list(member_mean),
        "map_monopole": _f64_list(map_mono),
        "member_monopole_first": _f64_list(member_mono[0]),
        "map_hash": _hash_array(map_out),
        "map_monopole_hash": _hash_array(map_mono),
        "member_hash": _hash_array(member_out),
        "member_monopole_hash": _hash_array(member_mono),
        "zero_budget_map_column_unchanged": bool(
            np.array_equal(map_out[:, 3], logq[:, 3])
        ),
        "zero_budget_member_column_unchanged": bool(
            np.array_equal(member_out[:, :, 3], cube[:, :, 3])
        ),
    }
    return result, map_out, member_out, map_mono


def _radial_probe(api) -> tuple[dict, dict]:
    n = 64
    pk = api.gaussian_correlation_spectrum(n, ell_grid=5.0, sigma=0.2)
    zz = np.linspace(0.0, 1.0, n)
    dN_exp = 200.0 * np.exp(-0.5 * ((zz - 0.5) / 0.15) ** 2) + 1.0
    C = np.ones(n)
    N_obs = (C * dN_exp)[None, :]

    fit = api.poisson_lognormal_map(
        N_obs,
        C,
        dN_exp,
        pk,
        bias=1.0,
        prior_strength=1.0,
        maxiter=300,
    )
    hi = dN_exp > 20.0
    q = np.asarray(fit["q_map"])
    assert q.shape == (1, n)
    assert np.all(np.isfinite(q))
    assert float(np.max(np.abs(q[0, hi] - 1.0))) < 0.05

    members1 = api.laplace_lognormal_members(
        fit["s_map"],
        fit["lambda_map"],
        pk,
        n_members=4,
        seed=7,
    )
    members2 = api.laplace_lognormal_members(
        fit["s_map"],
        fit["lambda_map"],
        pk,
        n_members=4,
        seed=7,
    )
    np.testing.assert_array_equal(
        np.asarray(members1["logq_members"]),
        np.asarray(members2["logq_members"]),
    )

    diagnostics = dict(fit.get("diagnostics", {}))
    safe_diag = {}
    for key in (
        "converged",
        "n_converged",
        "n_rows",
        "n_failed",
        "maxiter",
        "last_failure",
    ):
        if key in diagnostics:
            value = diagnostics[key]
            if isinstance(value, np.generic):
                value = value.item()
            safe_diag[key] = value

    map_result = {
        "q_shape": list(q.shape),
        "q_min": float(np.min(q)),
        "q_max": float(np.max(q)),
        "high_count_max_abs_q_minus_one": float(np.max(np.abs(q[0, hi] - 1.0))),
        "s_map_first8": _f64_list(np.asarray(fit["s_map"])[0, :8]),
        "lambda_first8": _f64_list(np.asarray(fit["lambda_map"])[0, :8]),
        "q_hash": _hash_array(q),
        "s_hash": _hash_array(fit["s_map"]),
        "lambda_hash": _hash_array(fit["lambda_map"]),
        "diagnostics": safe_diag,
    }

    member_result = {
        "shape": list(np.asarray(members1["logq_members"]).shape),
        "mean_shape": list(np.asarray(members1["logq_mean"]).shape),
        "logq_members_hash": _hash_array(members1["logq_members"]),
        "logq_mean_hash": _hash_array(members1["logq_mean"]),
        "first_member_first8": _f64_list(
            np.asarray(members1["logq_members"])[0, 0, :8]
        ),
        "same_seed_bit_identical": True,
    }
    return map_result, member_result


def _hdf5_probe(api, tmp: Path, map_out, member_out, map_mono) -> dict:
    path = tmp / "q_contract.h5"
    z = np.linspace(0.0, 1.0, map_out.shape[-1])
    rid = "phase10-l0a-fixed-realization-set"

    api.save_lss_completion_hdf5(
        str(path),
        logq_map=map_out,
        logq_members=member_out,
        zgrid=z,
        indexing="global",
        completion_kind="laplace_members",
        metadata={
            "probe": "phase10-l0a",
            "converged": True,
            "n_converged": int(map_out.shape[0]),
            "n_rows": int(map_out.shape[0]),
            "allow_unconverged": False,
        },
        realization_set_id=rid,
        budget_renormalized=True,
        budget_monopole_logq=map_mono,
        c_mode="aggregate",
        f_p_aware=True,
        q_support_depth=0.55,
    )
    loaded = api.load_lss_completion_hdf5(str(path))

    np.testing.assert_array_equal(loaded["logq_map"], map_out)
    np.testing.assert_array_equal(loaded["logq_members"], member_out)
    np.testing.assert_array_equal(loaded["zgrid"], z)
    np.testing.assert_array_equal(loaded["budget_monopole_logq"], map_mono)
    assert loaded["indexing"] == "global"
    assert loaded["completion_kind"] == "laplace_members"
    assert loaded["realization_set_id"] == rid
    assert loaded["budget_renormalized"] is True
    assert loaded["c_mode"] == "aggregate"
    assert loaded["f_p_aware"] is True
    assert loaded["q_support_depth"] == 0.55
    assert loaded["n_members"] == member_out.shape[0]

    expected_member_sha = hashlib.sha256(
        np.ascontiguousarray(member_out).tobytes()
    ).hexdigest()
    assert loaded["member_content_sha256"] == expected_member_sha

    return {
        "indexing": loaded["indexing"],
        "model": loaded["model"],
        "completion_kind": loaded["completion_kind"],
        "realization_set_id": loaded["realization_set_id"],
        "member_content_sha256": loaded["member_content_sha256"],
        "expected_member_content_sha256": expected_member_sha,
        "n_members": loaded["n_members"],
        "budget_renormalized": loaded["budget_renormalized"],
        "budget_monopole_hash": _hash_array(loaded["budget_monopole_logq"]),
        "c_mode": loaded["c_mode"],
        "f_p_aware": loaded["f_p_aware"],
        "q_support_depth": loaded["q_support_depth"],
        "diagnostics": loaded["diagnostics"],
        "logq_map_hash": _hash_array(loaded["logq_map"]),
        "logq_members_hash": _hash_array(loaded["logq_members"]),
        "zgrid_hash": _hash_array(loaded["zgrid"]),
    }


def _fail_closed_probe(api, tmp: Path) -> dict:
    poisoned = tmp / "poisoned.h5"
    bad = np.zeros((2, 4), dtype=float)
    bad[0, 1] = np.nan
    poison_error = None
    try:
        api.save_lss_completion_hdf5(str(poisoned), logq_map=bad)
    except Exception as exc:
        poison_error = {"type": type(exc).__name__, "message": str(exc)}
    assert poison_error is not None
    assert not poisoned.exists()

    unauditable = tmp / "unauditable.h5"
    budget_error = None
    try:
        api.save_lss_completion_hdf5(
            str(unauditable),
            logq_map=np.zeros((2, 4)),
            budget_renormalized=True,
        )
    except Exception as exc:
        budget_error = {"type": type(exc).__name__, "message": str(exc)}
    assert budget_error is not None
    assert not unauditable.exists()

    return {
        "poisoned_table_error": poison_error,
        "poisoned_file_absent": not poisoned.exists(),
        "mean_one_without_monopole_error": budget_error,
        "unauditable_file_absent": not unauditable.exists(),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-legacy-sha", default=LEGACY_SHA)
    args = parser.parse_args(argv)

    from darksirens.redshift import lognormal_completion as api

    with tempfile.TemporaryDirectory(prefix="darksirens-lss-l0a-") as td:
        tmp = Path(td)
        spectrum = _spectrum_probe(api)
        budget, map_out, member_out, map_mono = _budget_probe(api)
        radial_map, laplace = _radial_probe(api)
        hdf5 = _hdf5_probe(api, tmp, map_out, member_out, map_mono)
        fail_closed = _fail_closed_probe(api, tmp)

    result = {
        "schema": "darksirens-lss-l0a-reference-1",
        "legacy_sha": args.expected_legacy_sha,
        "spectrum": spectrum,
        "budget_renormalization": budget,
        "radial_map": radial_map,
        "laplace_members": laplace,
        "hdf5_contract": hdf5,
        "fail_closed": fail_closed,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
