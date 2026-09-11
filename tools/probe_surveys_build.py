#!/usr/bin/env python3
"""Deterministic S0 survey-construction probe against the pinned legacy tree.

This probe freezes only the behavior needed for the first darksirens-surveys
production slice:

* normalized raw rows -> HEALPix RING pixelated catalog HDF5;
* depth/mask map -> degraded per-pixel survey fraction.

It deliberately does not probe selection-function fitting yet. That is S0b/S3
and carries a larger numerical dependency surface.

One legacy detail is deliberately *canonicalized* before comparison. The pinned
pixelizer groups rows with ``np.argsort(pixel)`` using NumPy's default unstable
sort, so the order of galaxies sharing one HEALPix pixel is not a deterministic
legacy contract. Galaxy membership and all coindexed values are deterministic.
The frozen core loader already stably sorts each real-galaxy row by redshift, so
this probe applies that same scientific normalization before serializing/hash
comparison. The raw equal-pixel ordering is explicitly recorded as unstable and
is not treated as a parity requirement.

Run in a process whose PYTHONPATH resolves the pinned legacy ``darksirens``.
The output is plain JSON so a future darksirens-surveys candidate can be run in
another process and compared without importing both implementations together.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import h5py
import numpy as np


PIXEL_DATASETS = (
    "zgals",
    "dzgals",
    "wgals",
    "ngals",
    "mark_logmstar",
    "gal_app_mag",
    "gal_stratum",
)
COINDEXED_DATASETS = (
    "zgals",
    "dzgals",
    "wgals",
    "mark_logmstar",
    "gal_app_mag",
    "gal_stratum",
)


def _hash_array(a: np.ndarray) -> str:
    arr = np.ascontiguousarray(np.asarray(a))
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode())
    h.update(repr(arr.shape).encode())
    h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def _write_raw_catalog(path: Path) -> dict:
    # Chosen to exercise multiple RING pixels, repeated occupancy, z-depth
    # propagation, weights, a mark and two offline survey properties.
    ra_deg = np.array([5.0, 35.0, 91.0, 181.0, 270.0, 359.0, 45.0, 46.0])
    dec_deg = np.array([-70.0, -25.0, 5.0, 31.0, 62.0, 80.0, -25.0, -25.0])
    z = np.array(
        [0.011, 0.043, 0.081, 0.127, 0.173, 0.219, 0.052, 0.036],
        dtype=np.float64,
    )
    dz = np.array(
        [0.0010, 0.0012, 0.0014, 0.0016, 0.0018, 0.0020, 0.0011, 0.0013],
        dtype=np.float64,
    )
    weight = np.array(
        [1.0, 1.2, 0.8, 1.5, 0.9, 1.1, 2.0, 0.7], dtype=np.float64
    )
    app_mag = np.array(
        [17.2, 18.1, 18.9, 19.4, 20.0, 20.5, 18.4, 17.9], dtype=np.float64
    )
    stratum = np.array([0, 0, 1, 1, 2, 2, 0, 0], dtype=np.int32)
    logmstar = np.array(
        [10.1, 10.3, 10.6, 10.9, 11.0, 11.2, 10.4, 10.2], dtype=np.float64
    )

    with h5py.File(path, "w") as f:
        f["TARGET_RA"] = ra_deg
        f["TARGET_DEC"] = dec_deg
        f["Z"] = z
        f["ZERR"] = dz
        f["WEIGHT"] = weight
        f["APP_MAG"] = app_mag
        f["STRATUM"] = stratum
        f["LOGMSTAR"] = logmstar

    return {
        "ra_deg": ra_deg.tolist(),
        "dec_deg": dec_deg.tolist(),
        "z": z.tolist(),
        "dz": dz.tolist(),
        "weight": weight.tolist(),
    }


def _canonicalize_pixel_rows(arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Sort every real pixel prefix by z while carrying all columns together.

    This is the same row normalization performed by frozen core's catalog
    loader. Padding remains untouched and therefore still tests the writer's
    exact sentinel convention.
    """
    out = {name: np.array(value, copy=True) for name, value in arrays.items()}
    ngals = np.asarray(out["ngals"])
    for p in np.flatnonzero(ngals > 1):
        n = int(ngals[p])
        order = np.argsort(out["zgals"][p, :n], kind="stable")
        for name in COINDEXED_DATASETS:
            real = np.array(out[name][p, :n], copy=True)
            out[name][p, :n] = real[order]
    return out


def _pixelate_probe(tmp: Path) -> dict:
    from darksirens.cli.pixelate import main as pixelate_main

    raw = tmp / "raw.h5"
    input_rows = _write_raw_catalog(raw)
    outdir = tmp / "pixelated"
    pixelate_main(
        [
            "--survey_path",
            str(raw),
            "--save_path",
            str(outdir),
            "--nside",
            "2",
            "--z_depth",
            "0.25",
        ]
    )
    out = outdir / "catalog_pixelated_nside_2.h5"
    with h5py.File(out, "r") as f:
        arrays_raw = {key: np.asarray(f[key]) for key in PIXEL_DATASETS}
        attrs = {
            "nside": int(f.attrs["nside"]),
            "z_depth": float(f.attrs["z_depth"]),
        }

    arrays = _canonicalize_pixel_rows(arrays_raw)
    occupied = np.flatnonzero(arrays["ngals"] > 0)
    rows = {}
    for p in occupied:
        n = int(arrays["ngals"][p])
        rows[str(int(p))] = {
            "n": n,
            "z": arrays["zgals"][p, :n].tolist(),
            "dz": arrays["dzgals"][p, :n].tolist(),
            "w": arrays["wgals"][p, :n].tolist(),
            "mark_logmstar": arrays["mark_logmstar"][p, :n].tolist(),
            "gal_app_mag": arrays["gal_app_mag"][p, :n].tolist(),
            "gal_stratum": arrays["gal_stratum"][p, :n].tolist(),
        }

    return {
        "input": input_rows,
        "attrs": attrs,
        "shape": list(arrays["zgals"].shape),
        "occupied_pixels": occupied.tolist(),
        "ngals": arrays["ngals"].tolist(),
        "occupied_rows_canonical_z_order": rows,
        "canonical_hashes": {k: _hash_array(v) for k, v in arrays.items()},
        "comparison_convention": {
            "real_pixel_rows": "stable sort by zgals over the ngals prefix",
            "coindexed_columns": list(COINDEXED_DATASETS),
            "legacy_raw_equal_pixel_order_is_unstable": True,
            "reason": "legacy pixelizer uses np.argsort(pixel) without a stable sort kind",
            "core_alignment": "frozen darksirens.load_catalog stably sorts each real row by z",
        },
        "padding": {
            "z_all_100_after_ngals": bool(
                all(
                    np.all(
                        arrays["zgals"][p, int(arrays["ngals"][p]) :] == 100.0
                    )
                    for p in range(arrays["zgals"].shape[0])
                )
            ),
            "dz_all_1_after_ngals": bool(
                all(
                    np.all(
                        arrays["dzgals"][p, int(arrays["ngals"][p]) :] == 1.0
                    )
                    for p in range(arrays["dzgals"].shape[0])
                )
            ),
            "w_all_0_after_ngals": bool(
                all(
                    np.all(
                        arrays["wgals"][p, int(arrays["ngals"][p]) :] == 0.0
                    )
                    for p in range(arrays["wgals"].shape[0])
                )
            ),
        },
    }


def _depth_probe(tmp: Path) -> dict:
    import healpy as hp
    from darksirens.catalogs.depth_map import load_selection_fraction

    nside_in = 2
    npix = hp.nside2npix(nside_in)
    # Deterministic native RING map with full, partial and uncovered pixels.
    counts = np.ones(npix, dtype=np.int64)
    masked_frac = np.zeros(npix, dtype=np.float64)
    masked_frac[::5] = 0.25
    masked_frac[1::7] = 0.50
    counts[[3, 11, 27, 35]] = 0
    masked_frac[counts == 0] = np.nan

    path = tmp / "mth_map_nside2.h5"
    with h5py.File(path, "w") as f:
        f.attrs["nside"] = nside_in
        f.attrs["ordering"] = "RING"
        f["masked_frac"] = masked_frac
        f["counts"] = counts

    native = load_selection_fraction(path, 2)
    degraded = load_selection_fraction(path, 1)
    fake_ngals = np.zeros_like(degraded.f_p, dtype=np.int64)
    fake_ngals[[0, 2, 5]] = [2, 1, 3]
    report = degraded.coverage_report(fake_ngals)

    return {
        "input": {
            "nside": nside_in,
            "counts": counts.tolist(),
            "masked_frac": [
                None if not np.isfinite(x) else float(x) for x in masked_frac
            ],
        },
        "native": {
            "f_p": native.f_p.tolist(),
            "hash": _hash_array(native.f_p),
            "area_deg2": float(native.area_deg2),
            "n_covered": int(native.n_covered),
            "n_zero": int(native.n_zero),
        },
        "degraded_nside1": {
            "f_p": degraded.f_p.tolist(),
            "hash": _hash_array(degraded.f_p),
            "area_deg2": float(degraded.area_deg2),
            "n_covered": int(degraded.n_covered),
            "n_zero": int(degraded.n_zero),
            "coverage_report": report,
        },
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--expected-legacy-sha",
        default="c042527238bd71421b792936bc48c3b815b90d6d",
    )
    args = p.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="darksirens-surveys-probe-") as td:
        tmp = Path(td)
        result = {
            "schema": "darksirens-surveys-s0a-reference-2",
            "legacy_sha": args.expected_legacy_sha,
            "pixelate": _pixelate_probe(tmp),
            "depth": _depth_probe(tmp),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
