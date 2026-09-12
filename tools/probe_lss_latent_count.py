#!/usr/bin/env python3
"""Deterministic Phase-10 L6 probe of the pinned legacy latent/count seam.

Freezes the smallest online field contract needed before L6 production code:

* shell-total-conditioned single-tracer multinomial count likelihood;
* analytic gradient and exact Fisher Hessian including the rank-1 subtraction;
* damped fixed-trip count MAP and Laplace evidence;
* K-tracer shared-xi composition (one ridge, summed data/Fisher blocks);
* closed-form rho budget gauge and generated latent logQ;
* exact off-footprint and out-of-support logQ = 0 behavior.

It deliberately does not freeze artifact-loading/CLI glue, theta sensitivities,
PR-8 amplitude scans, or field-global K>=2 mixture normalization. Those remain
later L6/L7 slices.
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


def _f64(value):
    return np.asarray(value, dtype=np.float64).tolist()


def _single_count_probe(lc):
    import jax
    import jax.numpy as jnp

    proj = np.array([
        [0.80, -0.20],
        [0.25, 0.70],
        [-0.45, 0.55],
        [-0.65, -0.35],
    ], dtype=float)
    phi_z_fine = np.array([
        [1.00, 0.00],
        [0.75, 0.25],
        [0.40, 0.60],
        [0.10, 0.90],
        [-0.15, 1.05],
    ], dtype=float)
    W = np.array([
        [0.55, 0.30, 0.12, 0.03, 0.00],
        [0.05, 0.25, 0.40, 0.25, 0.05],
        [0.00, 0.03, 0.12, 0.30, 0.55],
    ], dtype=float)
    counts = np.array([
        [12, 5, 2],
        [7, 11, 4],
        [3, 8, 13],
        [2, 4, 9],
    ], dtype=float)
    fp = np.array([0.92, 0.78, 0.61, 0.44], dtype=float)
    tracer = lc.TracerCounts(
        pix=np.arange(4, dtype=np.int32),
        counts=counts,
        completeness=fp,
        bias=1.15,
        label="A",
    )
    op = lc.make_count_operator(proj, phi_z_fine, W, tracer)
    xi = jnp.asarray([0.12, -0.08, 0.17, 0.05], dtype=jnp.float64)

    logl = lc.shell_multinomial_logl(xi, op)
    obj = lc.objective(xi, op)
    grad = lc.gradient(xi, op)
    H = lc.hessian_separable(xi, op)
    H_ad = jax.hessian(lambda x: lc.objective(x, op))(xi)
    np.testing.assert_allclose(np.asarray(H), np.asarray(H_ad), rtol=2e-11, atol=2e-12)
    eig = np.linalg.eigvalsh(np.asarray(H))
    assert float(eig.min()) >= 1.0 - 2e-12

    sol = lc.count_map_solve(op, n_iter=13)
    evidence = lc.laplace_evidence(op, sol["xi_hat"], sol["H_chol"])
    assert float(sol["grad_inf"]) < 1e-8

    return {
        "proj_hash": _hash_array(proj),
        "phi_shell": _f64(np.asarray(op.phi_shell)),
        "shell_totals": _f64(np.asarray(op.shell_totals)),
        "logl": float(logl),
        "objective": float(obj),
        "gradient": _f64(np.asarray(grad)),
        "hessian": _f64(np.asarray(H)),
        "hessian_min_eig": float(eig.min()),
        "hessian_ad_max_abs": float(np.max(np.abs(np.asarray(H) - np.asarray(H_ad)))),
        "map_xi": _f64(np.asarray(sol["xi_hat"])),
        "map_grad_inf": float(sol["grad_inf"]),
        "map_objective": float(sol["J"]),
        "map_alpha": _f64(np.asarray(sol["alpha"])),
        "map_n_backtrack": np.asarray(sol["n_backtrack"], dtype=int).tolist(),
        "H_chol_diag": _f64(np.diag(np.asarray(sol["H_chol"]))),
        "laplace_evidence": float(evidence),
    }, (proj, phi_z_fine, W, tracer, op)


def _multi_count_probe(lc, single_bits):
    import jax.numpy as jnp

    proj, phi_z_fine, W, tracer_a, op_a = single_bits
    counts_b = np.array([
        [4, 8, 11],
        [9, 6, 3],
        [5, 7, 4],
        [8, 3, 2],
    ], dtype=float)
    tracer_b = lc.TracerCounts(
        pix=np.arange(4, dtype=np.int32),
        counts=counts_b,
        completeness=np.array([0.70, 0.82, 0.55, 0.68]),
        bias=0.75,
        label="B",
    )
    op_b = lc.make_count_operator(proj, phi_z_fine, W, tracer_b)
    mop = lc.MultiTracerCountOperator((op_a, op_b))
    xi = jnp.asarray([0.12, -0.08, 0.17, 0.05], dtype=jnp.float64)

    log_a = lc.shell_multinomial_logl(xi, op_a)
    log_b = lc.shell_multinomial_logl(xi, op_b)
    log_m = lc.multi_shell_multinomial_logl(xi, mop)
    obj_m = lc.multi_objective(xi, mop)
    grad_m = lc.multi_gradient(xi, mop)
    H_m = lc.multi_hessian_separable(xi, mop)
    g_expected = lc.gradient(xi, op_a) + lc.gradient(xi, op_b) - xi
    H_expected = lc.hessian_separable(xi, op_a) + lc.hessian_separable(xi, op_b) - jnp.eye(4)
    np.testing.assert_allclose(np.asarray(log_m), np.asarray(log_a + log_b), rtol=0, atol=0)
    np.testing.assert_allclose(np.asarray(grad_m), np.asarray(g_expected), rtol=2e-14, atol=2e-14)
    np.testing.assert_allclose(np.asarray(H_m), np.asarray(H_expected), rtol=2e-14, atol=2e-14)

    one = lc.MultiTracerCountOperator((op_a,))
    np.testing.assert_array_equal(
        np.asarray(lc.multi_gradient(xi, one)), np.asarray(lc.gradient(xi, op_a)))
    np.testing.assert_array_equal(
        np.asarray(lc.multi_hessian_separable(xi, one)),
        np.asarray(lc.hessian_separable(xi, op_a)))

    sol = lc.count_map_solve(mop, n_iter=13)
    assert float(sol["grad_inf"]) < 1e-8
    return {
        "logl_A": float(log_a),
        "logl_B": float(log_b),
        "logl_joint": float(log_m),
        "objective_joint": float(obj_m),
        "gradient_joint": _f64(np.asarray(grad_m)),
        "hessian_joint": _f64(np.asarray(H_m)),
        "one_tracer_wrapper_bit_identical": True,
        "map_xi": _f64(np.asarray(sol["xi_hat"])),
        "map_grad_inf": float(sol["grad_inf"]),
        "map_alpha": _f64(np.asarray(sol["alpha"])),
        "map_n_backtrack": np.asarray(sol["n_backtrack"], dtype=int).tolist(),
    }


def _latent_seam_probe(lq):
    import jax.numpy as jnp

    # One member, three fitted rows, one explicit zero pad row for off-footprint.
    row_fit = np.array([
        [0.20, -0.10],
        [0.10, 0.30],
        [-0.20, 0.05],
    ], dtype=float)
    row_fac = np.concatenate([row_fit, np.zeros((1, 2))], axis=0)[None, :, :]
    phi_z = np.array([
        [1.00, 0.00],
        [0.80, 0.20],
        [0.50, 0.50],
        [0.20, 0.80],
        [0.00, 0.00],
    ], dtype=float)
    below = np.array([True, True, True, True, False])
    fp = np.array([0.80, 0.60, 0.40], dtype=float)
    P_F, F_F = 3.0, float(fp.sum())
    b_nodes = np.array([0.0, 0.2928932188134524, 1.0, 1.7071067811865475, 2.0])
    field = row_fit @ phi_z.T
    A = np.empty((1, b_nodes.size, phi_z.shape[0]))
    B = np.empty_like(A)
    for j, b in enumerate(b_nodes):
        e = np.exp(b * field)
        A[0, j] = e.sum(axis=0)
        B[0, j] = fp @ e
    # Above support is an inert zero pad in the mature artifact convention.
    A[..., ~below] = 0.0
    B[..., ~below] = 0.0

    plan = lq.LatentQPlan(
        phi_z=jnp.asarray(phi_z),
        below_depth=jnp.asarray(below),
        row_fac=jnp.asarray(row_fac, dtype=jnp.float32),
        A=jnp.asarray(A),
        B=jnp.asarray(B),
        b_nodes=jnp.asarray(b_nodes),
        P_F=P_F,
        F_F=F_F,
        m_sph=1,
        m_z=2,
    )
    c = jnp.asarray([0.15, 0.25, 0.35, 0.45, 0.55])
    b = 0.9
    rho = lq.rho_from_moments(
        plan.A[0], plan.B[0], c, b, plan.b_nodes,
        plan.P_F, plan.F_F, plan.below_depth,
    )
    # Three footprint rows plus one off-footprint row.
    rows = jnp.asarray(row_fac[0])
    on_fp = jnp.asarray([True, True, True, False])
    block = lq.latent_logq_rows(plan, rows, rho, b, on_fp)
    block_np = np.asarray(block)
    assert np.all(block_np[3] == 0.0)
    assert np.all(block_np[:, ~below] == 0.0)

    # Exact consumed budget identity on fitted rows. Off-footprint contribution
    # is separately unchanged because Q=1 there.
    q = np.exp(block_np[:3])
    w = 1.0 - fp[:, None] * np.asarray(c)[None, :]
    lhs = np.sum(w * q, axis=0)
    rhs = np.sum(w, axis=0)
    np.testing.assert_allclose(lhs[below], rhs[below], rtol=3e-12, atol=3e-12)

    # Hot gathered-pair kernel must agree with the full-row block.
    row_idx = np.array([0, 1, 2, 3], dtype=int)
    z_idx = np.array([1, 2, 3, 1], dtype=int)
    hot = lq.latent_logq_at(
        rows[jnp.asarray(row_idx)],
        plan.phi_z[jnp.asarray(z_idx)],
        rho[jnp.asarray(z_idx)],
        b,
        on_fp[jnp.asarray(row_idx)],
    )
    np.testing.assert_allclose(
        np.asarray(hot), block_np[row_idx, z_idx], rtol=0.0, atol=2e-15)

    return {
        "b_nodes": _f64(b_nodes),
        "rho": _f64(np.asarray(rho)),
        "logq_rows": _f64(block_np),
        "budget_lhs": _f64(lhs),
        "budget_rhs": _f64(rhs),
        "budget_max_abs_supported": float(np.max(np.abs(lhs[below] - rhs[below]))),
        "off_footprint_bit_zero": bool(np.all(block_np[3] == 0.0)),
        "out_of_support_bit_zero": bool(np.all(block_np[:, ~below] == 0.0)),
        "hot_values": _f64(np.asarray(hot)),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    from darksirens.redshift import latent_counts as lc
    from darksirens.likelihood import latent_q as lq

    single, bits = _single_count_probe(lc)
    multi = _multi_count_probe(lc, bits)
    seam = _latent_seam_probe(lq)

    result = {
        "schema": "darksirens-lss-l6-latent-count-reference-1",
        "legacy_sha": LEGACY_SHA,
        "single_count": single,
        "multi_count": multi,
        "latent_seam": seam,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
