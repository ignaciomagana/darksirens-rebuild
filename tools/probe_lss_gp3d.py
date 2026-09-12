#!/usr/bin/env python3
"""Pinned-legacy oracle for Phase-10 L5 GP3D/joint-table semantics.

This probe intentionally stays below survey ingestion and above HDF5 I/O.  It
freezes the pure low-rank sphere x log(1+z) field, the convex Poisson-lognormal
solve, Laplace members, posterior-mean evaluation, and the joint multi-survey
bias-absorption construction on already-prepared voxel arrays.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _hash_array(value) -> str:
    arr = np.ascontiguousarray(np.asarray(value))
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode())
    h.update(repr(arr.shape).encode())
    h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def _one_field():
    import jax
    jax.config.update("jax_enable_x64", True)

    from darksirens.redshift.lognormal_completion import (
        build_lowrank_operator,
        eval_logq_gp3d,
        laplace_lognormal_gp3d_members,
        lowrank_inducing_nodes,
        poisson_lognormal_gp3d_map,
    )

    M_sph, M_z = 8, 4
    Zn, Zz = lowrank_inducing_nodes(M_sph, M_z, z_node_hi=2.0)
    Zn = np.asarray(Zn, dtype=float)
    Zz = np.asarray(Zz, dtype=float)

    A = np.array([0.0, 0.0, 1.0])
    th = np.deg2rad(18.0)
    B = np.array([np.sin(th), 0.0, np.cos(th)])
    C = np.array([0.0, 0.0, -1.0])
    z_s = np.linspace(0.10, 1.40, 7)
    X_n = np.repeat(A[None, :], z_s.size, axis=0)
    X_z = np.log1p(z_s)

    amp, ls_sph, ls_z, bias = 0.9, 0.65, 0.55, 1.2
    Phi, L = build_lowrank_operator(
        Zn, Zz, X_n, X_z,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
    )
    Phi = np.asarray(Phi, dtype=float)
    L = np.asarray(L, dtype=float)

    base = np.full(z_s.size, 12.0)
    N = base.copy()
    N[3] = 70.0
    mp = poisson_lognormal_gp3d_map(N, base, Phi, bias=bias)
    assert mp["diagnostics"]["converged"]

    n_hat_out = np.stack([A, B, C])
    det = np.asarray(eval_logq_gp3d(
        mp["xi_map"], Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=n_hat_out, z_out=z_s, bias=bias,
        L=L, H_chol=mp["H_chol"], pix_chunk=2,
    ), dtype=float)
    assert det.shape == (3, z_s.size)

    xi_mem = laplace_lognormal_gp3d_members(
        mp["xi_map"], mp["H_chol"], n_members=6, seed=19
    )
    members = np.asarray(eval_logq_gp3d(
        xi_mem, Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=n_hat_out, z_out=z_s, bias=bias,
        L=L, pix_chunk=2,
    ), dtype=float)

    # Homogeneous posterior mean: xi=0, H=I => exact Q=1 to numerical precision.
    homogeneous = np.asarray(eval_logq_gp3d(
        np.zeros(Zn.shape[0]), Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=n_hat_out, z_out=z_s, bias=bias,
        L=L, H_chol=np.eye(Zn.shape[0]), pix_chunk=2,
    ), dtype=float)

    j = 3
    assert det[0, j] > det[1, j] > det[2, j]
    assert det[1, j] > 0.01

    return {
        "M_sph": M_sph,
        "M_z": M_z,
        "Zn_shape": list(Zn.shape),
        "Zz_shape": list(Zz.shape),
        "Zn_first4": Zn[:4].tolist(),
        "Zz_first8": Zz[:8].tolist(),
        "Zn_hash": _hash_array(Zn),
        "Zz_hash": _hash_array(Zz),
        "Phi_shape": list(Phi.shape),
        "Phi_first_row_first8": Phi[0, :8].tolist(),
        "Phi_hash": _hash_array(Phi),
        "L_diag_first8": np.diag(L)[:8].tolist(),
        "xi_map_first8": np.asarray(mp["xi_map"])[:8].tolist(),
        "xi_map_hash": _hash_array(mp["xi_map"]),
        "H_diag_first8": np.diag(np.asarray(mp["H_chol"]))[:8].tolist(),
        "sigma2_vox": np.asarray(mp["sigma2_vox"]).tolist(),
        "f_solve": np.asarray(mp["f_solve"]).tolist(),
        "lambda_solve": np.asarray(mp["lambda_solve"]).tolist(),
        "solver_diagnostics": dict(mp["diagnostics"]),
        "det_logq": det.tolist(),
        "det_hash": _hash_array(det),
        "member_xi": np.asarray(xi_mem).tolist(),
        "member_xi_hash": _hash_array(xi_mem),
        "member_logq_first": members[0].tolist(),
        "member_logq_hash": _hash_array(members),
        "homogeneous_max_abs": float(np.max(np.abs(homogeneous))),
        "borrow_at_structure": [float(det[k, j]) for k in range(3)],
    }


def _joint_field():
    import jax
    jax.config.update("jax_enable_x64", True)

    from darksirens.redshift.lognormal_completion import (
        build_lowrank_operator,
        eval_logq_gp3d,
        laplace_lognormal_gp3d_members,
        lowrank_inducing_nodes,
        poisson_lognormal_gp3d_map,
    )

    Zn, Zz = lowrank_inducing_nodes(8, 4, z_node_hi=2.0)
    Zn = np.asarray(Zn, dtype=float)
    Zz = np.asarray(Zz, dtype=float)
    amp, ls_sph, ls_z = 0.8, 0.7, 0.6
    z_s = np.linspace(0.10, 1.30, 6)
    Xz = np.log1p(z_s)

    A = np.array([0.0, 0.0, 1.0])
    B = np.array([1.0, 0.0, 0.0])
    C = np.array([0.0, 0.0, -1.0])
    biases = np.array([0.8, 1.35])

    # Survey A has structure at A. Survey B has its own occupied direction B.
    PhiA, L = build_lowrank_operator(
        Zn, Zz, np.repeat(A[None, :], z_s.size, axis=0), Xz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
    )
    PhiB, Lb = build_lowrank_operator(
        Zn, Zz, np.repeat(B[None, :], z_s.size, axis=0), Xz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
    )
    np.testing.assert_allclose(np.asarray(L), np.asarray(Lb), rtol=0.0, atol=0.0)

    baseA = np.full(z_s.size, 9.0)
    baseB = np.full(z_s.size, 11.0)
    NA = baseA.copy(); NA[2] = 55.0
    NB = baseB.copy(); NB[4] = 38.0

    Phi_stack = np.vstack([
        biases[0] * np.asarray(PhiA),
        biases[1] * np.asarray(PhiB),
    ])
    N_stack = np.concatenate([NA, NB])
    base_stack = np.concatenate([baseA, baseB])
    mp = poisson_lognormal_gp3d_map(N_stack, base_stack, Phi_stack, bias=1.0)
    assert mp["diagnostics"]["converged"]

    xi_members = laplace_lognormal_gp3d_members(
        mp["xi_map"], mp["H_chol"], n_members=10, seed=123
    )
    out_dirs = np.stack([A, B, C])
    mapA = np.asarray(eval_logq_gp3d(
        mp["xi_map"], Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=out_dirs, z_out=z_s, bias=float(biases[0]),
        L=L, H_chol=mp["H_chol"], pix_chunk=2,
    ))
    mapB = np.asarray(eval_logq_gp3d(
        mp["xi_map"], Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=out_dirs, z_out=z_s, bias=float(biases[1]),
        L=L, H_chol=mp["H_chol"], pix_chunk=2,
    ))
    memA = np.asarray(eval_logq_gp3d(
        xi_members, Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=out_dirs, z_out=z_s, bias=float(biases[0]),
        L=L, pix_chunk=2,
    ))
    memB = np.asarray(eval_logq_gp3d(
        xi_members, Zn, Zz,
        amp=amp, ls_sph=ls_sph, ls_z=ls_z,
        n_hat_out=out_dirs, z_out=z_s, bias=float(biases[1]),
        L=L, pix_chunk=2,
    ))

    # Same xi_m draw set must induce positively correlated member fluctuations
    # at the same physical output voxel across survey responses.
    sA = memA[:, 0, 2]
    sB = memB[:, 0, 2]
    corr = float(np.corrcoef(sA, sB)[0, 1])
    assert corr > 0.99

    return {
        "biases": biases.tolist(),
        "PhiA_hash": _hash_array(PhiA),
        "PhiB_hash": _hash_array(PhiB),
        "stack_shape": list(Phi_stack.shape),
        "xi_map_first8": np.asarray(mp["xi_map"])[:8].tolist(),
        "H_diag_first8": np.diag(np.asarray(mp["H_chol"]))[:8].tolist(),
        "solver_diagnostics": dict(mp["diagnostics"]),
        "shared_member_xi_hash": _hash_array(xi_members),
        "mapA": mapA.tolist(),
        "mapB": mapB.tolist(),
        "membersA_hash": _hash_array(memA),
        "membersB_hash": _hash_array(memB),
        "same_voxel_member_corr": corr,
        "same_member_count": int(memA.shape[0]),
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    out = {
        "schema": "darksirens-lss-l5-gp3d-reference-1",
        "legacy_sha": LEGACY_SHA,
        "single": _one_field(),
        "joint": _joint_field(),
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
