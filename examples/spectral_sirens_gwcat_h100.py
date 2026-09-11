#!/usr/bin/env python3
"""
Run and benchmark a catalog-free spectral-siren analysis with darksirens-core.

This driver is intentionally tied to the frozen darksirens-core public analysis
surface and the current gwcat v2 export contract. It consumes *exported* gwcat
PE/selection products, not raw PESummary or injection-release files.

Expected inputs
---------------
PE:
    format_version = "gwcat-pe-2.0" or "gwcat-pe-2.1"

Selection:
    format_version = "gwcat-selection-2.0" or "gwcat-selection-2.1"

Before darksirens loads either file, the script calls

    gwcat.validate_export(pe, selection, strict=True)

by default. This matters for modern mixed injection campaigns: a valid chi_eff
population analysis may use a PE file in the ``chieff`` basis paired with a
selection file in the ``chieff_reference`` basis. Let gwcat validate that
pairing instead of forcing basis-name equality downstream.

The default population is the sampled LVK-style ``powerlaw+peak`` model. For
the larger model use ``--population brokenpowerlaw+2peaks`` and leave
``--fixed-population`` unset to infer the population jointly with H0.

H100 notes
----------
Install a CUDA-enabled JAX/JAXLIB matching the darksirens-core validated JAX
version. This script never forces a CUDA platform; it reports the devices JAX
actually sees and ``--require-gpu`` makes a CPU fallback fatal.

For repeated runs, use ``--xla-cache`` to enable darksirens-core's persistent
compilation cache. ``--preallocate`` can be useful on a dedicated GPU node.

Examples
--------
Full sampled PowerLaw+Peak run:

    python spectral_sirens_gwcat_h100.py pe.h5 selection.h5 \
        --population powerlaw+peak \
        --require-gpu \
        --nlive 1000 --dlogz 0.1 \
        --likelihood-evals 20 \
        --output-prefix ppp_h100

Larger BrokenPowerLaw+2Peaks spectral run:

    python spectral_sirens_gwcat_h100.py pe.h5 selection.h5 \
        --population brokenpowerlaw+2peaks \
        --require-gpu \
        --nlive 2000 --dlogz 0.05 \
        --xla-cache /scratch/$USER/darksirens-xla \
        --output-prefix bpl2p_h100

Compile/likelihood benchmark only, without nested sampling:

    python spectral_sirens_gwcat_h100.py pe.h5 selection.h5 \
        --population powerlaw+peak \
        --require-gpu \
        --likelihood-evals 100 \
        --benchmark-only
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

import h5py
import numpy as np


FROZEN_DARKSIRENS_CORE_SHA = "af2488b0ccb48c65e63cffcae306a8a4a4bfeb66"
GWCAT_HEAD_WHEN_WRITTEN = "8f9e2f12b499a6b2bf16ed938f66d020b12c44c2"


def _decode(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode()
    if isinstance(value, np.ndarray):
        if value.ndim == 0:
            return _decode(value.item())
        return [_decode(v) for v in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def _package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def _git_sha_for_module(module) -> str | None:
    """Best-effort SHA for editable installs; wheels normally return None."""
    try:
        path = Path(module.__file__).resolve()
    except Exception:
        return None
    for parent in (path.parent, *path.parents):
        if (parent / ".git").exists():
            try:
                proc = subprocess.run(
                    ["git", "-C", str(parent), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return proc.stdout.strip()
            except Exception:
                return None
    return None


def _read_export_metadata(path: Path, kind: str) -> dict[str, Any]:
    attrs_to_show = (
        "format_version",
        "spin_basis",
        "parameter_space",
        "fit_columns",
        "advisory_columns",
        "nobs",
        "nsamp",
        "ndraw",
        "z_max",
        "far_max",
        "far_threshold",
        "snr_threshold",
        "significance_type",
        "source_class_filter",
        "cut_estimator",
        "chi_eff_amax",
        "spin_reference_amax",
        "spin_reference_coverage_ok",
        "selection_spec_digest",
        "event_list_digest",
        "contract_hash",
    )
    with h5py.File(path, "r") as f:
        attrs = {key: _decode(f.attrs[key]) for key in attrs_to_show if key in f.attrs}
        fmt = str(_decode(f.attrs.get("format_version", "")))
        datasets = tuple(sorted(str(k) for k in f.keys()))

    expected_prefix = "gwcat-pe-2." if kind == "pe" else "gwcat-selection-2."
    if not fmt.startswith(expected_prefix):
        raise RuntimeError(
            f"{path} is format_version={fmt!r}; this benchmark requires the "
            f"current gwcat v2 {kind} format ({expected_prefix}x). Re-export "
            "with `gwcat export pe` / `gwcat export selection`."
        )

    return {
        "path": str(path),
        "format_version": fmt,
        "attrs": attrs,
        "datasets": datasets,
    }


def _validate_pair_with_gwcat(pe: Path, selection: Path, strict: bool) -> dict[str, Any]:
    try:
        import gwcat
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "gwcat is required by this benchmark so the PE/selection pair can "
            "be validated before darksirens runs. Install the current gwcat "
            "checkout/environment used to create the export products."
        ) from exc

    validator = getattr(gwcat, "validate_export", None)
    if validator is None:
        raise RuntimeError(
            "Installed gwcat has no public validate_export dispatcher; update "
            "gwcat before benchmarking current v2 products."
        )

    t0 = time.perf_counter()
    result = validator(str(pe), str(selection), strict=bool(strict))
    elapsed = time.perf_counter() - t0

    return {
        "elapsed_s": elapsed,
        "strict": bool(strict),
        "result_type": type(result).__name__,
        "gwcat_version": _package_version("gwcat"),
        "gwcat_git_sha": _git_sha_for_module(gwcat),
        "reference_head_when_script_written": GWCAT_HEAD_WHEN_WRITTEN,
    }


def _nvidia_smi() -> list[str]:
    exe = shutil.which("nvidia-smi")
    if exe is None:
        return []
    try:
        proc = subprocess.run(
            [
                exe,
                "--query-gpu=index,name,driver_version,memory.total",
                "--format=csv,noheader",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _block_until_ready(jax, value: Any) -> Any:
    for leaf in jax.tree_util.tree_leaves(value):
        block = getattr(leaf, "block_until_ready", None)
        if block is not None:
            block()
    return value


def _first_numeric_leaf(jax, value: Any) -> float | None:
    for leaf in jax.tree_util.tree_leaves(value):
        try:
            arr = np.asarray(leaf)
        except Exception:
            continue
        if arr.size == 1 and np.issubdtype(arr.dtype, np.number):
            return float(arr.reshape(()))
    return None


def _device_report(jax) -> dict[str, Any]:
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
                "bytes_in_use",
                "peak_bytes_in_use",
                "bytes_limit",
                "largest_free_block_bytes",
            ):
                if key in stats:
                    row[key] = int(stats[key])
        devices.append(row)

    return {
        "backend": jax.default_backend(),
        "jax_version": _package_version("jax"),
        "jaxlib_version": _package_version("jaxlib"),
        "devices": devices,
        "nvidia_smi": _nvidia_smi(),
    }


def _benchmark_likelihood(
    *,
    analysis,
    events,
    injections,
    jax,
    jnp,
    n_evals: int,
) -> dict[str, Any]:
    """Benchmark the exact bound core likelihood used by ds.infer.

    This intentionally uses two execution-adjacent core helpers so the timing
    isolates the scientific likelihood rather than the nested sampler:
    ``bind_analysis`` and ``make_prior_transform``. The actual inference below
    still enters through public ``ds.infer``.
    """
    from darksirens.inference.prior import make_prior_transform
    from darksirens.runtime_binding import bind_analysis

    t_bind = time.perf_counter()
    likelihood = bind_analysis(
        analysis,
        events=events,
        injections=injections,
    )
    bind_s = time.perf_counter() - t_bind

    plan = analysis.parameters
    transform = make_prior_transform(
        plan.lower,
        plan.upper,
        prior_kinds=plan.prior_kinds,
        joint_constraints=plan.joint_constraints,
    )
    u_mid = np.full(len(plan.labels), 0.5, dtype=np.float64)
    theta = jnp.asarray(transform(u_mid), dtype=jnp.float64)

    jitted = jax.jit(likelihood)

    t0 = time.perf_counter()
    first = _block_until_ready(jax, jitted(theta))
    compile_and_first_s = time.perf_counter() - t0

    timings = []
    last = first
    for _ in range(max(0, int(n_evals))):
        t0 = time.perf_counter()
        last = _block_until_ready(jax, jitted(theta))
        timings.append(time.perf_counter() - t0)

    timings_np = np.asarray(timings, dtype=float)
    if timings_np.size:
        median_s = float(np.median(timings_np))
        mean_s = float(np.mean(timings_np))
        p10_s = float(np.quantile(timings_np, 0.10))
        p90_s = float(np.quantile(timings_np, 0.90))
        evals_per_s = float(1.0 / median_s) if median_s > 0 else float("inf")
    else:
        median_s = mean_s = p10_s = p90_s = evals_per_s = None

    return {
        "bind_s": bind_s,
        "compile_and_first_eval_s": compile_and_first_s,
        "steady_evals": int(timings_np.size),
        "steady_median_s": median_s,
        "steady_mean_s": mean_s,
        "steady_p10_s": p10_s,
        "steady_p90_s": p90_s,
        "steady_evals_per_s_from_median": evals_per_s,
        "reference_log_likelihood_leaf": _first_numeric_leaf(jax, last),
        "theta_midpoint": np.asarray(theta).tolist(),
    }


def _print_header(title: str) -> None:
    print(f"\n{'=' * 80}\n{title}\n{'=' * 80}", flush=True)


def _write_outputs(
    prefix: Path,
    summary: dict[str, Any],
    result: dict[str, Any] | None,
    labels: tuple[str, ...],
) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_suffix(".json")
    json_path.write_text(json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n")
    print(f"wrote {json_path}", flush=True)

    if result is None:
        return

    arrays: dict[str, Any] = {"labels": np.asarray(labels, dtype=str)}
    if result.get("samples") is not None:
        arrays["samples"] = np.asarray(result["samples"])
    if result.get("log_likelihood") is not None:
        arrays["log_likelihood"] = np.asarray(result["log_likelihood"])
    if result.get("logZ") is not None:
        arrays["logZ"] = np.asarray(result["logZ"])
    if result.get("logZerr") is not None:
        arrays["logZerr"] = np.asarray(result["logZerr"])

    npz_path = prefix.with_suffix(".npz")
    np.savez_compressed(npz_path, **arrays)
    print(f"wrote {npz_path}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate current gwcat v2 products and run/benchmark a "
            "darksirens-core spectral-siren analysis."
        )
    )
    parser.add_argument("pe", type=Path, help="gwcat-pe-2.x posterior export")
    parser.add_argument(
        "selection",
        type=Path,
        help="gwcat-selection-2.x detected-injection export",
    )

    parser.add_argument(
        "--population",
        default="powerlaw+peak",
        help=(
            "darksirens population registry model to sample "
            "(default: powerlaw+peak; e.g. brokenpowerlaw+2peaks)"
        ),
    )
    parser.add_argument(
        "--fixed-population",
        default=None,
        choices=("legacy", "in_prior_v2", "gwtc5"),
        help=(
            "Fix population instead of doing a joint spectral fit. "
            "fixed=gwtc5 is only valid for brokenpowerlaw+2peaks."
        ),
    )
    parser.add_argument("--h0-min", type=float, default=20.0)
    parser.add_argument("--h0-max", type=float, default=140.0)
    parser.add_argument("--Om0", type=float, default=0.3075)
    parser.add_argument("--w0", type=float, default=-1.0)
    parser.add_argument("--wa", type=float, default=0.0)

    parser.add_argument(
        "--no-shared-beta",
        action="store_false",
        dest="shared_beta",
        default=True,
        help="Use separate mass-ratio slopes where supported.",
    )
    parser.add_argument(
        "--no-shared-spin",
        action="store_false",
        dest="shared_spin",
        default=True,
        help="Use separate spin hyperparameters where supported.",
    )
    parser.add_argument(
        "--no-shared-gamma",
        action="store_false",
        dest="shared_gamma",
        default=True,
        help="Use separate redshift-evolution slopes where supported.",
    )

    parser.add_argument("--sampler", default="tinyns")
    parser.add_argument("--nlive", type=int, default=1000)
    parser.add_argument("--dlogz", type=float, default=0.1)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--show-progress",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "--likelihood-evals",
        type=int,
        default=20,
        help=(
            "Number of synchronized post-JIT likelihood evaluations for the "
            "H100 timing microbenchmark. Set 0 to measure compile only."
        ),
    )
    parser.add_argument(
        "--skip-likelihood-benchmark",
        action="store_true",
        help="Skip direct JIT compile/evaluation timing.",
    )
    parser.add_argument(
        "--benchmark-only",
        action="store_true",
        help="Run validation/load/bind/JIT timing but do not launch the sampler.",
    )

    parser.add_argument(
        "--strict-gwcat",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run gwcat.validate_export(..., strict=True) before loading.",
    )
    parser.add_argument(
        "--require-gpu",
        action="store_true",
        help="Fail unless JAX sees at least one GPU device.",
    )
    parser.add_argument(
        "--xla-cache",
        type=Path,
        default=None,
        help="Set DARKSIRENS_XLA_CACHE before JAX initialization.",
    )
    parser.add_argument(
        "--preallocate",
        action="store_true",
        help="Set XLA_PYTHON_CLIENT_PREALLOCATE=true before JAX initialization.",
    )
    parser.add_argument(
        "--mem-fraction",
        type=float,
        default=None,
        help="Optional XLA_PYTHON_CLIENT_MEM_FRACTION override.",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=None,
        help="Write PREFIX.json timing/provenance and PREFIX.npz posterior arrays.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    pe = args.pe.expanduser().resolve()
    selection = args.selection.expanduser().resolve()
    if not pe.is_file():
        raise FileNotFoundError(pe)
    if not selection.is_file():
        raise FileNotFoundError(selection)
    if not args.h0_min < args.h0_max:
        raise ValueError("--h0-min must be smaller than --h0-max")
    if args.likelihood_evals < 0:
        raise ValueError("--likelihood-evals must be >= 0")
    if args.nlive < 1:
        raise ValueError("--nlive must be positive")
    if args.dlogz <= 0:
        raise ValueError("--dlogz must be positive")
    if args.mem_fraction is not None and not (0.0 < args.mem_fraction <= 1.0):
        raise ValueError("--mem-fraction must lie in (0, 1]")

    if args.xla_cache is not None:
        os.environ["DARKSIRENS_XLA_CACHE"] = str(args.xla_cache.expanduser().resolve())
    if args.preallocate:
        os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "true"
    if args.mem_fraction is not None:
        os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = str(args.mem_fraction)

    _print_header("Input contract")
    pe_meta = _read_export_metadata(pe, "pe")
    sel_meta = _read_export_metadata(selection, "selection")
    print(json.dumps(_jsonable(pe_meta["attrs"]), indent=2, sort_keys=True))
    print(json.dumps(_jsonable(sel_meta["attrs"]), indent=2, sort_keys=True))

    _print_header("gwcat pair validation")
    validation = _validate_pair_with_gwcat(
        pe,
        selection,
        strict=args.strict_gwcat,
    )
    print(json.dumps(_jsonable(validation), indent=2, sort_keys=True))

    import darksirens as ds

    ds.configure_jax_runtime()

    import jax
    import jax.numpy as jnp
    import darksirens

    devices = _device_report(jax)
    _print_header("Runtime")
    print(f"host: {platform.node()}")
    print(f"python: {sys.version.split()[0]}")
    print(f"darksirens package version: {_package_version('darksirens')}")
    print(f"darksirens editable git SHA: {_git_sha_for_module(darksirens)}")
    print(f"frozen core reference SHA: {FROZEN_DARKSIRENS_CORE_SHA}")
    print(f"jax backend: {devices['backend']}")
    for row in devices["devices"]:
        print(
            "JAX device: "
            f"platform={row['platform']} id={row['id']} "
            f"kind={row['device_kind']}"
        )
    for row in devices["nvidia_smi"]:
        print(f"nvidia-smi: {row}")

    if args.require_gpu and not any(
        row["platform"] == "gpu" for row in devices["devices"]
    ):
        raise RuntimeError(
            "--require-gpu was set but JAX sees no GPU. Install/activate the "
            "CUDA-enabled JAX/JAXLIB build before using this as an H100 benchmark."
        )

    _print_header("Analysis construction")
    population = ds.Population(
        args.population,
        fixed=args.fixed_population,
        shared_beta=args.shared_beta,
        shared_spin=args.shared_spin,
        shared_gamma=args.shared_gamma,
    )
    cosmology = ds.Cosmology(
        H0=(args.h0_min, args.h0_max),
        Om0=args.Om0,
        w0=args.w0,
        wa=args.wa,
    )

    t0 = time.perf_counter()
    analysis = ds.model(
        cosmology=cosmology,
        population=population,
    )
    model_build_s = time.perf_counter() - t0

    from darksirens.runtime_binding import required_fit_columns

    fit_columns = required_fit_columns(analysis)
    print(f"population model: {analysis.population.model_name}")
    print(f"population fixed: {analysis.population.is_fixed}")
    print(f"required fit columns: {fit_columns}")
    print(f"parameter dimension: {len(analysis.parameters.labels)}")
    for i, (name, lo, hi, kind) in enumerate(
        zip(
            analysis.parameters.labels,
            analysis.parameters.lower,
            analysis.parameters.upper,
            analysis.parameters.prior_kinds,
        )
    ):
        print(f"  {i:02d} {name}: [{lo}, {hi}] prior={kind}")

    _print_header("Load standardized stores")
    t0 = time.perf_counter()
    events = ds.load_events(pe, fit_columns=fit_columns)
    pe_load_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    injections = ds.load_injections(selection, fit_columns=fit_columns)
    selection_load_s = time.perf_counter() - t0

    print(
        f"PE: {events.n_events} events x {events.nsamp} samples "
        f"({events.n_events * events.nsamp:,} rows), load={pe_load_s:.3f} s"
    )
    print(
        f"selection: {injections.n_injections:,} detected rows / "
        f"ndraw={injections.ndraw:,}, load={selection_load_s:.3f} s"
    )

    benchmark = None
    if not args.skip_likelihood_benchmark:
        _print_header("JIT likelihood benchmark")
        benchmark = _benchmark_likelihood(
            analysis=analysis,
            events=events,
            injections=injections,
            jax=jax,
            jnp=jnp,
            n_evals=args.likelihood_evals,
        )
        print(
            f"bind: {benchmark['bind_s']:.3f} s\n"
            f"compile + first eval: {benchmark['compile_and_first_eval_s']:.3f} s"
        )
        if benchmark["steady_median_s"] is not None:
            print(
                "steady synchronized likelihood: "
                f"median={1e3 * benchmark['steady_median_s']:.3f} ms "
                f"mean={1e3 * benchmark['steady_mean_s']:.3f} ms "
                f"p10={1e3 * benchmark['steady_p10_s']:.3f} ms "
                f"p90={1e3 * benchmark['steady_p90_s']:.3f} ms "
                f"~{benchmark['steady_evals_per_s_from_median']:.2f} eval/s"
            )
        print(
            "reference likelihood leaf: "
            f"{benchmark['reference_log_likelihood_leaf']}"
        )

    result = None
    inference_summary = None
    if not args.benchmark_only:
        _print_header(f"Spectral-siren inference ({args.sampler})")
        sampler_options = {
            "nlive": args.nlive,
            "dlogz": args.dlogz,
            "seed": args.seed,
            "show_progress": args.show_progress,
        }
        if args.max_samples is not None:
            sampler_options["max_samples"] = args.max_samples

        t0 = time.perf_counter()
        result = ds.infer(
            analysis,
            events=events,
            injections=injections,
            sampler=args.sampler,
            **sampler_options,
        )
        inference_s = time.perf_counter() - t0

        samples = np.asarray(result.get("samples", np.empty((0, 0))))
        logz = result.get("logZ")
        logzerr = result.get("logZerr")
        print(f"elapsed: {inference_s:.3f} s")
        print(f"logZ: {logz}")
        print(f"logZerr: {logzerr}")
        print(f"posterior samples: {samples.shape}")

        inference_summary = {
            "elapsed_s": inference_s,
            "sampler": args.sampler,
            "nlive": args.nlive,
            "dlogz": args.dlogz,
            "max_samples": args.max_samples,
            "seed": args.seed,
            "logZ": logz,
            "logZerr": logzerr,
            "samples_shape": tuple(int(v) for v in samples.shape),
        }

    summary = {
        "script": "spectral_sirens_gwcat_h100.py",
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "frozen_darksirens_core_sha": FROZEN_DARKSIRENS_CORE_SHA,
        "pe": pe_meta,
        "selection": sel_meta,
        "gwcat_validation": validation,
        "runtime": devices,
        "environment": {
            "DARKSIRENS_XLA_CACHE": os.environ.get("DARKSIRENS_XLA_CACHE"),
            "XLA_PYTHON_CLIENT_PREALLOCATE": os.environ.get(
                "XLA_PYTHON_CLIENT_PREALLOCATE"
            ),
            "XLA_PYTHON_CLIENT_MEM_FRACTION": os.environ.get(
                "XLA_PYTHON_CLIENT_MEM_FRACTION"
            ),
        },
        "analysis": {
            "population_requested": args.population,
            "population_resolved": analysis.population.model_name,
            "population_fixed": analysis.population.is_fixed,
            "shared_beta": args.shared_beta,
            "shared_spin": args.shared_spin,
            "shared_gamma": args.shared_gamma,
            "H0_prior": [args.h0_min, args.h0_max],
            "Om0": args.Om0,
            "w0": args.w0,
            "wa": args.wa,
            "fit_columns": fit_columns,
            "labels": analysis.parameters.labels,
            "lower": analysis.parameters.lower,
            "upper": analysis.parameters.upper,
            "prior_kinds": analysis.parameters.prior_kinds,
            "joint_constraints": analysis.parameters.joint_constraints,
            "model_build_s": model_build_s,
        },
        "data": {
            "n_events": events.n_events,
            "nsamp": events.nsamp,
            "n_pe_rows": events.n_events * events.nsamp,
            "n_detected_injections": injections.n_injections,
            "ndraw": injections.ndraw,
            "pe_load_s": pe_load_s,
            "selection_load_s": selection_load_s,
        },
        "likelihood_benchmark": benchmark,
        "inference": inference_summary,
    }

    if args.output_prefix is not None:
        _write_outputs(
            args.output_prefix.expanduser().resolve(),
            summary,
            result,
            analysis.parameters.labels,
        )

    _print_header("Done")
    if args.benchmark_only:
        print("benchmark-only mode: sampler was not launched")
    else:
        print("spectral-siren run completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
