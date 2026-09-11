#!/usr/bin/env python3
"""Freeze the pinned-legacy offline magnitude-selection fit for surveys S0b.

The future surveys package owns fitting/building these products; frozen core
continues to own runtime evaluation of the standardized selection model.  This
probe therefore records the fit outputs and serialization contract, while also
pinning the H0 firewall that makes the h-scaled magnitude convention safe.

Run with PYTHONPATH pointing at the pinned legacy repository and the campaign
numerics stack. Floating outputs are canonicalized to 11 significant decimal
places before JSON serialization: optimizer/Hessian last bits are not a
scientific contract, whereas parameter values, covariance ordering and fit
metadata are.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROUND_SIG = 11
KC = (0.39, 0.11)
H0_REF = 100.0


def _r(x):
    if x is None:
        return None
    if isinstance(x, (bool, str, int)):
        return x
    if isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, float):
        if not np.isfinite(x):
            return str(x)
        return float(f"{x:.{ROUND_SIG}g}")
    if isinstance(x, np.ndarray):
        return _r(x.tolist())
    if isinstance(x, (list, tuple)):
        return [_r(v) for v in x]
    if isinstance(x, dict):
        return {str(k): _r(v) for k, v in x.items()}
    return x


def _gaussian_sample(rng, n, h0_true, *, m0=-21.0, sigma=1.0, m_lim=22.5,
                     k_corr_coeffs=()):
    import jax.numpy as jnp
    from darksirens.redshift.selection import k_of_z
    from darksirens.utils.cosmology import distance_modulus

    z = rng.uniform(0.03, 0.45, size=5 * n) ** (1.0 / 1.5)
    z = z[(z > 0.02) & (z < 0.5)][:3 * n]
    M = rng.normal(m0, sigma, size=z.size)
    dm = np.asarray(distance_modulus(jnp.asarray(z), h0_true))
    K = (
        0.0
        if not k_corr_coeffs
        else np.asarray(k_of_z(z, k_corr_coeffs, xp=np))
    )
    m = M + dm + K
    keep = m <= m_lim
    m, z = m[keep][:n], z[keep][:n]
    if m.size != n:
        raise RuntimeError(f"gaussian fixture produced {m.size}/{n} requested rows")
    return m, z


def _schechter_sample(rng, n, h0_true, *, Mstar=-20.5, alpha=-1.10,
                      m_lim=21.5, offset=5.0, zlo=0.08, zhi=0.5):
    import jax.numpy as jnp
    from scipy.special import gammaincc, gammainccinv
    from darksirens.utils.cosmology import distance_modulus

    a = alpha + 1.0
    x_faint = 10.0 ** (-0.4 * offset)
    N = 40 * n
    z = rng.uniform(zlo ** 1.5, zhi ** 1.5, size=N) ** (1.0 / 1.5)
    if a > 0.0:
        x = gammainccinv(a, rng.uniform(size=N) * gammaincc(a, x_faint))
    else:
        x_hi = 40.0
        chunks = []
        got = 0
        while got < N:
            v = rng.uniform(size=2 * N)
            xx = (x_faint ** a + v * (x_hi ** a - x_faint ** a)) ** (1.0 / a)
            xx = xx[rng.uniform(size=xx.size) < np.exp(-xx)]
            chunks.append(xx)
            got += xx.size
        x = np.concatenate(chunks)[:N]
    M = Mstar - 2.5 * np.log10(x)
    m = M + np.asarray(distance_modulus(jnp.asarray(z), h0_true))
    keep = m <= m_lim
    m, z = m[keep][:n], z[keep][:n]
    if m.size != n:
        raise RuntimeError(f"schechter fixture produced {m.size}/{n} requested rows")
    return m, z


def _fit_record(fit):
    payload = fit.to_jsonable()
    meta_keep = {
        k: payload.get("meta", {}).get(k)
        for k in (
            "Om0", "w0", "wa", "H0_ref", "nll",
            "M_faint_offset_constrained", "M_faint_offset_protocol",
            "m_faint_cut", "m_faint_implied", "frac_complete_at_m_faint",
            "n_gal_faintward_of_m_faint",
        )
        if k in payload.get("meta", {})
    }
    out = {
        "json_key_order": list(payload.keys()),
        "family": payload["family"],
        "m_lim": payload["m_lim"],
        "cov": payload["cov"],
        "n_gal": payload["n_gal"],
        "stratum": payload["stratum"],
        "k_corr_coeffs": payload.get("k_corr_coeffs", []),
        "meta": meta_keep,
    }
    for key in ("M0hat", "sigma_M", "Mstar_hat", "alpha", "M_faint_offset"):
        if key in payload:
            out[key] = payload[key]
    return _r(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--expected-legacy-sha",
        default="c042527238bd71421b792936bc48c3b815b90d6d",
    )
    args = p.parse_args(argv)

    import jax
    jax.config.update("jax_enable_x64", True)
    import jax.numpy as jnp
    import scipy
    import astropy
    from darksirens.redshift.selection import (
        c_sel_gaussian,
        fit_selection_from_mags,
        reference_absolute_mags,
    )

    # Gaussian truncated-LF reference.
    m_g, z_g = _gaussian_sample(np.random.default_rng(21), 2500, 70.0)
    gfit = fit_selection_from_mags(m_g, z_g, 22.5, stratum="all")

    # Same family with a fixed K(z) template.
    m_k, z_k = _gaussian_sample(
        np.random.default_rng(11), 2500, 70.0, k_corr_coeffs=KC
    )
    kfit = fit_selection_from_mags(
        m_k, z_k, 22.5, stratum="kcorr", k_corr_coeffs=KC
    )
    kfit_ignored = fit_selection_from_mags(m_k, z_k, 22.5, stratum="kcorr_noK")

    # Schechter reference in the real-catalog alpha < -1 regime.
    m_s, z_s = _schechter_sample(np.random.default_rng(7), 2500, 70.0)
    sfit = fit_selection_from_mags(
        m_s,
        z_s,
        21.5,
        family="schechter",
        M_faint_offset=5.0,
        stratum="all",
    )

    # H0 firewall at fixed h-scaled theta, with and without K correction.
    z_fire = jnp.linspace(1e-4, 0.5, 200)
    theta = dict(m_lim=24.0, M0hat=-20.2, sigma_M=1.0)
    h0_values = (50.0, 67.74, 100.0, 140.0)
    curves = {
        str(h): np.asarray(c_sel_gaussian(z_fire, H0=h, **theta))
        for h in h0_values
    }
    curves_k = {
        str(h): np.asarray(
            c_sel_gaussian(z_fire, H0=h, k_corr_coeffs=KC, **theta)
        )
        for h in h0_values
    }
    ref = curves["100.0"]
    ref_k = curves_k["100.0"]
    max_h0_delta = max(float(np.max(np.abs(v - ref))) for v in curves.values())
    max_h0_delta_k = max(
        float(np.max(np.abs(v - ref_k))) for v in curves_k.values()
    )

    # Reference-magnitude convention and K subtraction on simple points.
    z_anchor = np.array([0.05, 0.2, 0.4])
    m_anchor = np.array([19.0, 20.0, 21.0])
    Mhat = reference_absolute_mags(m_anchor, z_anchor)
    Mhat_k = reference_absolute_mags(m_anchor, z_anchor, k_corr_coeffs=KC)

    gtruth = -21.0 - 5.0 * np.log10(70.0 / H0_REF)
    struth = -20.5 - 5.0 * np.log10(70.0 / H0_REF)

    result = {
        "schema": "darksirens-surveys-s0b-selection-fit-reference-1",
        "legacy_sha": args.expected_legacy_sha,
        "numerics": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "jax": jax.__version__,
            "astropy": astropy.__version__,
            "round_significant_digits": ROUND_SIG,
        },
        "conventions": {
            "H0_ref": H0_REF,
            "gaussian_sample_truth_M0hat": gtruth,
            "schechter_sample_truth_Mstar_hat": struth,
            "schechter_sample_truth_alpha": -1.10,
            "schechter_M_faint_offset": 5.0,
            "k_corr_coeffs": list(KC),
        },
        "gaussian": _fit_record(gfit),
        "gaussian_kcorr": _fit_record(kfit),
        "gaussian_kcorr_ignored": _fit_record(kfit_ignored),
        "schechter": _fit_record(sfit),
        "firewall": {
            "h0_values": list(h0_values),
            "max_abs_delta_gaussian": max_h0_delta,
            "max_abs_delta_gaussian_kcorr": max_h0_delta_k,
            "curve_anchor_indices": [0, 40, 100, 199],
            "curve_anchor_H0ref": ref[[0, 40, 100, 199]].tolist(),
            "curve_anchor_H0ref_kcorr": ref_k[[0, 40, 100, 199]].tolist(),
        },
        "reference_absolute_mags": {
            "z": z_anchor.tolist(),
            "m": m_anchor.tolist(),
            "Mhat": Mhat.tolist(),
            "Mhat_kcorr": Mhat_k.tolist(),
            "K_subtracted": (Mhat - Mhat_k).tolist(),
        },
        "diagnostics": {
            "kcorr_M0hat_shift_if_ignored": float(kfit_ignored.M0hat - kfit.M0hat),
            "gaussian_cov_fields": ["M0hat", "sigma_M"],
            "schechter_cov_fields": ["Mstar_hat", "alpha"],
        },
    }
    result = _r(result)

    # Scientific sanity checks before writing the reference.
    assert abs(gfit.M0hat - gtruth) < 4.0 * np.sqrt(gfit.cov[0, 0])
    assert abs(gfit.sigma_M - 1.0) < 4.0 * np.sqrt(gfit.cov[1, 1])
    assert tuple(kfit.k_corr_coeffs) == KC
    assert kfit_ignored.M0hat > kfit.M0hat
    assert abs(sfit.Mstar_hat - struth) < 4.0 * np.sqrt(sfit.cov[0, 0])
    assert abs(sfit.alpha - (-1.10)) < 4.0 * np.sqrt(sfit.cov[1, 1])
    assert max_h0_delta <= 1e-12
    assert max_h0_delta_k <= 1e-12

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
