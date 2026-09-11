"""Shared helpers for the darksirens-core H100 validation examples.

This module is intentionally not part of darksirens-core. It lives in the
reconstruction/validation repository so timing and provenance machinery cannot
become part of the frozen scientific API.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
from importlib import metadata
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

import h5py
import numpy as np

FROZEN_DARKSIRENS_CORE_SHA = "af2488b0ccb48c65e63cffcae306a8a4a4bfeb66"
GWCAT_HEAD_WHEN_WRITTEN = "8f9e2f12b499a6b2bf16ed938f66d020b12c44c2"


def decode(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode()
    if isinstance(value, np.ndarray):
        if value.ndim == 0:
            return decode(value.item())
        return [decode(v) for v in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    return value


def jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return str(value)


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def git_sha_for_module(module) -> str | None:
    try:
        path = Path(module.__file__).resolve()
    except Exception:
        return None
    for parent in (path.parent, *path.parents):
        if (parent / ".git").exists():
            try:
                return subprocess.check_output(
                    ["git", "-C", str(parent), "rev-parse", "HEAD"], text=True
                ).strip()
            except Exception:
                return None
    return None


def load_manifest(mock_dir: Path | None) -> tuple[Path | None, dict[str, Any] | None]:
    if mock_dir is None:
        return None, None
    root = mock_dir.expanduser().resolve()
    path = root / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"mock manifest not found: {path}")
    manifest = json.loads(path.read_text())
    if manifest.get("schema") != "darksirens-rebuild-mock-closure-1":
        raise RuntimeError(
            f"unsupported mock manifest schema {manifest.get('schema')!r} in {path}"
        )
    return root, manifest


def mock_file(root: Path, manifest: dict[str, Any], key: str) -> Path:
    rel = manifest.get("files", {}).get(key)
    if not rel:
        raise RuntimeError(f"mock manifest has no files.{key}")
    path = (root / rel).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def read_export_metadata(path: Path, kind: str) -> dict[str, Any]:
    attrs_to_show = (
        "format_version", "spin_basis", "parameter_space", "fit_columns",
        "advisory_columns", "nobs", "nsamp", "ndraw", "z_max", "far_max",
        "far_threshold", "snr_threshold", "significance_type",
        "source_class_filter", "cut_estimator", "chi_eff_amax",
        "spin_reference_amax", "spin_reference_coverage_ok",
        "selection_spec_digest", "event_list_digest", "contract_hash",
        "mock_data", "mock_direct_density", "bridge_legacy_sha",
    )
    with h5py.File(path, "r") as f:
        attrs = {key: decode(f.attrs[key]) for key in attrs_to_show if key in f.attrs}
        fmt = str(decode(f.attrs.get("format_version", "")))
        datasets = tuple(sorted(str(k) for k in f.keys()))
    expected = "gwcat-pe-2." if kind == "pe" else "gwcat-selection-2."
    if not fmt.startswith(expected):
        raise RuntimeError(
            f"{path} has format_version={fmt!r}; expected current gwcat v2 {kind} "
            f"({expected}x)."
        )
    return {"path": str(path), "format_version": fmt, "attrs": attrs, "datasets": datasets}


def validate_pair_with_gwcat(pe: Path, selection: Path, strict: bool = True) -> dict[str, Any]:
    try:
        import gwcat
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "gwcat is required so the PE/selection pair is validated before inference"
        ) from exc
    validator = getattr(gwcat, "validate_export", None)
    if validator is None:
        raise RuntimeError("installed gwcat has no public validate_export dispatcher")
    t0 = time.perf_counter()
    result = validator(str(pe), str(selection), strict=bool(strict))
    elapsed = time.perf_counter() - t0
    checks = (
        {str(k): bool(v) for k, v in result.items()}
        if isinstance(result, dict)
        else {"result": str(result)}
    )
    return {
        "elapsed_s": elapsed,
        "strict": bool(strict),
        "checks": checks,
        "all_checks_pass": (
            all(checks.values())
            if checks and all(isinstance(v, bool) for v in checks.values())
            else None
        ),
        "gwcat_version": package_version("gwcat"),
        "gwcat_git_sha": git_sha_for_module(gwcat),
        "reference_head_when_written": GWCAT_HEAD_WHEN_WRITTEN,
    }


def configure_xla_from_args(args) -> None:
    if getattr(args, "xla_cache", None) is not None:
        os.environ["DARKSIRENS_XLA_CACHE"] = str(args.xla_cache.expanduser().resolve())
    if getattr(args, "preallocate", False):
        os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "true"
    if getattr(args, "mem_fraction", None) is not None:
        frac = float(args.mem_fraction)
        if not 0.0 < frac <= 1.0:
            raise ValueError("--mem-fraction must lie in (0, 1]")
        os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = str(frac)


def nvidia_smi() -> list[str]:
    exe = shutil.which("nvidia-smi")
    if exe is None:
        return []
    try:
        out = subprocess.check_output(
            [
                exe,
                "--query-gpu=index,name,driver_version,memory.total,memory.used",
                "--format=csv,noheader",
            ],
            text=True,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []


def device_report(jax) -> dict[str, Any]:
    devices = []
    for dev in jax.devices():
        row = {
            "platform": getattr(dev, "platform", None),
            "id": getattr(dev, "id", None),
            "device_kind": getattr(dev, "device_kind", str(dev)),
        }
        try:
            stats = dev.memory_stats()
        except Exception:
            stats = None
        if stats:
            for key in (
                "bytes_in_use", "peak_bytes_in_use", "bytes_limit",
                "largest_free_block_bytes",
            ):
                if key in stats:
                    row[key] = int(stats[key])
        devices.append(row)
    return {
        "backend": jax.default_backend(),
        "jax_version": package_version("jax"),
        "jaxlib_version": package_version("jaxlib"),
        "devices": devices,
        "nvidia_smi": nvidia_smi(),
    }


def require_gpu(report: dict[str, Any]) -> None:
    if not any(row.get("platform") == "gpu" for row in report["devices"]):
        raise RuntimeError(
            "--require-gpu was set but JAX sees no GPU; activate the CUDA JAX build"
        )


def block_until_ready(jax, value: Any) -> Any:
    for leaf in jax.tree_util.tree_leaves(value):
        block = getattr(leaf, "block_until_ready", None)
        if block is not None:
            block()
    return value


def first_numeric_leaf(jax, value: Any) -> float | None:
    for leaf in jax.tree_util.tree_leaves(value):
        try:
            arr = np.asarray(leaf)
        except Exception:
            continue
        if arr.size == 1 and np.issubdtype(arr.dtype, np.number):
            return float(arr.reshape(()))
    return None


def benchmark_likelihood(*, analysis, events, injections, jax, jnp, n_evals: int) -> dict[str, Any]:
    """Time the exact bound likelihood used by public ds.infer."""
    from darksirens.inference.prior import make_prior_transform
    from darksirens.runtime_binding import bind_analysis

    t0 = time.perf_counter()
    likelihood = bind_analysis(analysis, events=events, injections=injections)
    bind_s = time.perf_counter() - t0

    plan = analysis.parameters
    transform = make_prior_transform(
        plan.lower,
        plan.upper,
        prior_kinds=plan.prior_kinds,
        joint_constraints=plan.joint_constraints,
    )
    u = np.full(len(plan.labels), 0.5, dtype=np.float64)
    theta = jnp.asarray(transform(u), dtype=jnp.float64)
    jitted = jax.jit(likelihood)

    t0 = time.perf_counter()
    first = block_until_ready(jax, jitted(theta))
    compile_s = time.perf_counter() - t0

    times = []
    last = first
    for _ in range(max(0, int(n_evals))):
        t0 = time.perf_counter()
        last = block_until_ready(jax, jitted(theta))
        times.append(time.perf_counter() - t0)
    arr = np.asarray(times, dtype=float)
    median = float(np.median(arr)) if arr.size else None
    return {
        "bind_s": bind_s,
        "compile_and_first_eval_s": compile_s,
        "steady_evals": int(arr.size),
        "steady_median_s": median,
        "steady_mean_s": float(np.mean(arr)) if arr.size else None,
        "steady_p10_s": float(np.quantile(arr, 0.10)) if arr.size else None,
        "steady_p90_s": float(np.quantile(arr, 0.90)) if arr.size else None,
        "steady_evals_per_s_from_median": (
            1.0 / median if median and median > 0 else None
        ),
        "reference_log_likelihood_leaf": first_numeric_leaf(jax, last),
        "theta_midpoint": np.asarray(theta).tolist(),
    }


def print_header(title: str) -> None:
    print(f"\n{'=' * 80}\n{title}\n{'=' * 80}", flush=True)


def runtime_provenance(jax, darksirens_module) -> dict[str, Any]:
    report = device_report(jax)
    report.update({
        "host": platform.node(),
        "platform_string": platform.platform(),
        "python": sys.version,
        "darksirens_version": package_version("darksirens"),
        "darksirens_git_sha": git_sha_for_module(darksirens_module),
        "frozen_core_sha": FROZEN_DARKSIRENS_CORE_SHA,
        "environment": {
            "DARKSIRENS_XLA_CACHE": os.environ.get("DARKSIRENS_XLA_CACHE"),
            "XLA_PYTHON_CLIENT_PREALLOCATE": os.environ.get(
                "XLA_PYTHON_CLIENT_PREALLOCATE"
            ),
            "XLA_PYTHON_CLIENT_MEM_FRACTION": os.environ.get(
                "XLA_PYTHON_CLIENT_MEM_FRACTION"
            ),
        },
    })
    return report


def write_outputs(prefix: Path, summary: dict[str, Any], result: dict[str, Any] | None, labels) -> None:
    prefix = prefix.expanduser().resolve()
    prefix.parent.mkdir(parents=True, exist_ok=True)
    jpath = prefix.with_suffix(".json")
    jpath.write_text(json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n")
    print(f"wrote {jpath}")
    if result is None:
        return
    arrays: dict[str, Any] = {"labels": np.asarray(labels, dtype=str)}
    for key in ("samples", "log_likelihood", "logZ", "logZerr"):
        if result.get(key) is not None:
            arrays[key] = np.asarray(result[key])
    npath = prefix.with_suffix(".npz")
    np.savez_compressed(npath, **arrays)
    print(f"wrote {npath}")


def add_h100_args(parser) -> None:
    parser.add_argument("--require-gpu", action="store_true")
    parser.add_argument("--xla-cache", type=Path, default=None)
    parser.add_argument("--preallocate", action="store_true")
    parser.add_argument("--mem-fraction", type=float, default=None)
    parser.add_argument("--likelihood-evals", type=int, default=20)
    parser.add_argument("--skip-likelihood-benchmark", action="store_true")
    parser.add_argument("--benchmark-only", action="store_true")
    parser.add_argument("--output-prefix", type=Path, default=None)


def add_sampler_args(parser) -> None:
    parser.add_argument(
        "--sampler", choices=("tinyns", "dynesty", "numpyro"), default="tinyns"
    )
    parser.add_argument("--nlive", type=int, default=1000)
    parser.add_argument("--dlogz", type=float, default=0.1)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--show-progress", action=argparse.BooleanOptionalAction, default=True
    )


def validate_numeric_args(args) -> None:
    if getattr(args, "h0_min", 0) >= getattr(args, "h0_max", 1):
        raise ValueError("--h0-min must be smaller than --h0-max")
    if getattr(args, "likelihood_evals", 0) < 0:
        raise ValueError("--likelihood-evals must be >= 0")
    if getattr(args, "nlive", 1) < 1:
        raise ValueError("--nlive must be positive")
    if getattr(args, "dlogz", 1) <= 0:
        raise ValueError("--dlogz must be positive")
