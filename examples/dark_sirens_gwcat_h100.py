#!/usr/bin/env python3
"""Run/benchmark catalog dark sirens on the generative closure data set.

The same GW PE and selection realization can be run against either catalog:

``--catalog-mode complete``
    Machinery closure gate.  Every possible host is present at true redshift,
    and core uses the complete-catalog likelihood (no missing-host branch).

``--catalog-mode incomplete``
    End-to-end dark-siren closure.  The observed catalog has the legacy mock's
    magnitude/redshift/sigmoid selection and realised photo-z.  Core's frozen
    ordinary count-ratio completeness and missing-host branch are active.

Use complete first.  If complete fails to recover the injected cosmology, the
problem is upstream of incompleteness.  If complete closes but incomplete does
not, the completeness model/finite-realization regime is the thing to inspect.

Examples
--------
Fixed population, likelihood performance only::

    python examples/dark_sirens_gwcat_h100.py \
        --mock-dir data/mock_closure --catalog-mode complete \
        --fixed-population legacy --require-gpu --benchmark-only \
        --likelihood-evals 50 --output-prefix perf/dark_complete_fixed

    python examples/dark_sirens_gwcat_h100.py \
        --mock-dir data/mock_closure --catalog-mode incomplete \
        --fixed-population legacy --require-gpu --benchmark-only \
        --likelihood-evals 50 --output-prefix perf/dark_incomplete_fixed

Full joint population+H0 incomplete-catalog run::

    python examples/dark_sirens_gwcat_h100.py \
        --mock-dir data/mock_closure --catalog-mode incomplete \
        --population powerlaw+peak --require-gpu \
        --nlive 1000 --dlogz 0.1 \
        --xla-cache /scratch/$USER/darksirens-xla \
        --output-prefix runs/dark_incomplete_joint
"""
from __future__ import annotations

import argparse
from pathlib import Path
import time

import numpy as np

from _h100_common import (
    FROZEN_DARKSIRENS_CORE_SHA,
    add_h100_args,
    add_sampler_args,
    benchmark_likelihood,
    configure_xla_from_args,
    load_manifest,
    mock_file,
    print_header,
    read_export_metadata,
    require_gpu,
    runtime_provenance,
    validate_numeric_args,
    validate_pair_with_gwcat,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pe", type=Path, nargs="?", help="gwcat-pe-2.x product")
    p.add_argument(
        "selection", type=Path, nargs="?", help="gwcat-selection-2.x product"
    )
    p.add_argument(
        "catalog", type=Path, nargs="?", help="standardized darksirens catalog HDF5"
    )
    p.add_argument(
        "--mock-dir",
        type=Path,
        default=None,
        help="Closure directory containing manifest.json; replaces positional files.",
    )
    p.add_argument(
        "--catalog-mode",
        choices=("complete", "incomplete"),
        default="incomplete",
        help="Select complete-catalog gate or missing-host dark-siren likelihood.",
    )
    p.add_argument("--population", default="powerlaw+peak")
    p.add_argument(
        "--fixed-population",
        default=None,
        choices=("legacy", "in_prior_v2", "gwtc5"),
        help="Fix population; omit for joint population+cosmology inference.",
    )
    p.add_argument("--h0-min", type=float, default=20.0)
    p.add_argument("--h0-max", type=float, default=140.0)
    p.add_argument("--Om0", type=float, default=0.3075)
    p.add_argument("--w0", type=float, default=-1.0)
    p.add_argument("--wa", type=float, default=0.0)
    p.add_argument(
        "--no-shared-beta", action="store_false", dest="shared_beta", default=True
    )
    p.add_argument(
        "--no-shared-spin", action="store_false", dest="shared_spin", default=True
    )
    p.add_argument(
        "--no-shared-gamma", action="store_false", dest="shared_gamma", default=True
    )
    p.add_argument(
        "--strict-gwcat",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Strict-validate the current gwcat v2 PE/selection pair first.",
    )
    add_h100_args(p)
    add_sampler_args(p)
    return p


def _resolve_inputs(args):
    root, manifest = load_manifest(args.mock_dir)
    if root is not None:
        if any(x is not None for x in (args.pe, args.selection, args.catalog)):
            raise ValueError(
                "use either --mock-dir or positional PE SELECTION CATALOG, not both"
            )
        pe = mock_file(root, manifest, "gw_events")
        selection = mock_file(root, manifest, "gw_selection")
        key = "catalog_complete" if args.catalog_mode == "complete" else "catalog_incomplete"
        catalog = mock_file(root, manifest, key)
    else:
        if args.pe is None or args.selection is None or args.catalog is None:
            raise ValueError("provide PE SELECTION CATALOG or --mock-dir")
        pe = args.pe.expanduser().resolve()
        selection = args.selection.expanduser().resolve()
        catalog = args.catalog.expanduser().resolve()
    return pe, selection, catalog, root, manifest


def _posterior_coordinate_summary(samples, labels, truth):
    """Compact closure summary for coordinates whose truth is known by name."""
    arr = np.asarray(samples)
    if arr.ndim != 2 or not len(arr):
        return {}
    known = {
        "H0": truth.get("H0"),
        "log10n0": (
            None
            if truth.get("n0_requested") is None
            else float(np.log10(truth["n0_requested"]))
        ),
    }
    out = {}
    for name, value in known.items():
        if value is None or name not in labels:
            continue
        j = labels.index(name)
        q = np.quantile(arr[:, j], [0.05, 0.16, 0.50, 0.84, 0.95])
        out[name] = {
            "truth": float(value),
            "q05": float(q[0]),
            "q16": float(q[1]),
            "median": float(q[2]),
            "q84": float(q[3]),
            "q95": float(q[4]),
        }
    return out


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validate_numeric_args(args)
    configure_xla_from_args(args)
    pe, selection, catalog_path, mock_root, manifest = _resolve_inputs(args)

    print_header("Closure input")
    if manifest is not None:
        print(f"mock directory: {mock_root}")
        print(f"truth: {manifest.get('truth')}")
    print(f"catalog mode: {args.catalog_mode}")
    print(f"PE: {pe}")
    print(f"selection: {selection}")
    print(f"catalog: {catalog_path}")
    pe_meta = read_export_metadata(pe, "pe")
    selection_meta = read_export_metadata(selection, "selection")

    print_header("gwcat pair validation")
    validation = validate_pair_with_gwcat(pe, selection, strict=args.strict_gwcat)
    print(
        f"validation: all_pass={validation.get('all_checks_pass')} "
        f"elapsed={validation['elapsed_s']:.3f} s"
    )

    import darksirens as ds

    ds.configure_jax_runtime()
    import darksirens
    import jax
    import jax.numpy as jnp
    from darksirens.runtime_binding import required_fit_columns

    runtime = runtime_provenance(jax, darksirens)
    print_header("Runtime")
    print(f"core reference: {FROZEN_DARKSIRENS_CORE_SHA}")
    print(f"installed core git SHA: {runtime.get('darksirens_git_sha')}")
    print(f"JAX backend: {runtime['backend']}")
    for dev in runtime["devices"]:
        print(f"JAX device: {dev['platform']} {dev['id']} {dev['device_kind']}")
    for line in runtime["nvidia_smi"]:
        print(f"nvidia-smi: {line}")
    if args.require_gpu:
        require_gpu(runtime)

    print_header("Load catalog")
    t0 = time.perf_counter()
    catalog = ds.load_catalog(catalog_path)
    catalog_load_s = time.perf_counter() - t0
    n_gal = int(np.asarray(catalog.catalog.ngals).sum())
    shape = tuple(int(v) for v in np.shape(catalog.catalog.zgals))
    print(
        f"catalog: mode={args.catalog_mode}, nside={catalog.nside}, "
        f"z_depth={catalog.z_depth}, galaxies={n_gal:,}, padded_shape={shape}, "
        f"load={catalog_load_s:.3f} s"
    )

    print_header("Dark-siren model")
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
        catalog=catalog,
        completeness=args.catalog_mode,
    )
    model_build_s = time.perf_counter() - t0
    fit_columns = required_fit_columns(analysis)
    print(f"population: {analysis.population.model_name}")
    print(f"population fixed: {analysis.population.is_fixed}")
    print(f"fit columns: {fit_columns}")
    print(f"sampled dimension: {len(analysis.parameters.labels)}")
    for i, label in enumerate(analysis.parameters.labels):
        print(
            f"  {i:02d} {label}: [{analysis.parameters.lower[i]}, "
            f"{analysis.parameters.upper[i]}] {analysis.parameters.prior_kinds[i]}"
        )

    print_header("Load GW stores")
    t0 = time.perf_counter()
    events = ds.load_events(pe, fit_columns=fit_columns)
    pe_load_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    injections = ds.load_injections(selection, fit_columns=fit_columns)
    selection_load_s = time.perf_counter() - t0
    print(
        f"PE: {events.n_events} x {events.nsamp} = "
        f"{events.n_events * events.nsamp:,} rows; {pe_load_s:.3f} s"
    )
    print(
        f"selection: {injections.n_injections:,} detected / "
        f"{injections.ndraw:,} proposed; {selection_load_s:.3f} s"
    )

    benchmark = None
    if not args.skip_likelihood_benchmark:
        print_header(f"Dark-siren likelihood benchmark: {args.catalog_mode}")
        benchmark = benchmark_likelihood(
            analysis=analysis,
            events=events,
            injections=injections,
            jax=jax,
            jnp=jnp,
            n_evals=args.likelihood_evals,
        )
        print(f"bind (includes catalog compaction/cache): {benchmark['bind_s']:.3f} s")
        print(
            "compile + first synchronized eval: "
            f"{benchmark['compile_and_first_eval_s']:.3f} s"
        )
        if benchmark["steady_median_s"] is not None:
            print(
                "steady synchronized eval: "
                f"median={1e3 * benchmark['steady_median_s']:.3f} ms; "
                f"{benchmark['steady_evals_per_s_from_median']:.2f} eval/s"
            )
        print(f"reference likelihood leaf: {benchmark['reference_log_likelihood_leaf']}")

    result = None
    inference = None
    closure = None
    if not args.benchmark_only:
        print_header(f"Full dark-siren inference: {args.catalog_mode} / {args.sampler}")
        options = dict(
            nlive=args.nlive,
            dlogz=args.dlogz,
            seed=args.seed,
            show_progress=args.show_progress,
        )
        if args.max_samples is not None:
            options["max_samples"] = args.max_samples
        t0 = time.perf_counter()
        result = ds.infer(
            analysis,
            events=events,
            injections=injections,
            sampler=args.sampler,
            **options,
        )
        elapsed = time.perf_counter() - t0
        samples = np.asarray(result.get("samples", np.empty((0, 0))))
        inference = {
            "elapsed_s": elapsed,
            "sampler": args.sampler,
            "nlive": args.nlive,
            "dlogz": args.dlogz,
            "max_samples": args.max_samples,
            "seed": args.seed,
            "logZ": result.get("logZ"),
            "logZerr": result.get("logZerr"),
            "samples_shape": samples.shape,
        }
        if manifest is not None:
            closure = _posterior_coordinate_summary(
                samples,
                list(analysis.parameters.labels),
                manifest.get("truth", {}),
            )
        print(f"elapsed: {elapsed:.3f} s")
        print(f"logZ: {result.get('logZ')} +/- {result.get('logZerr')}")
        print(f"posterior samples: {samples.shape}")
        if closure:
            print(f"closure summary: {closure}")

    summary = {
        "script": "dark_sirens_gwcat_h100.py",
        "mode": "dark_siren",
        "catalog_mode": args.catalog_mode,
        "mock_manifest": manifest,
        "pe": pe_meta,
        "selection": selection_meta,
        "gwcat_validation": validation,
        "runtime": runtime,
        "catalog": {
            "path": str(catalog_path),
            "nside": catalog.nside,
            "z_depth": catalog.z_depth,
            "n_galaxies": n_gal,
            "padded_shape": shape,
            "load_s": catalog_load_s,
        },
        "analysis": {
            "population_requested": args.population,
            "population_resolved": analysis.population.model_name,
            "population_fixed": analysis.population.is_fixed,
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
        "inference": inference,
        "closure": closure,
    }
    if args.output_prefix is not None:
        write_outputs(args.output_prefix, summary, result, analysis.parameters.labels)

    print_header("Done")
    print(
        "benchmark-only"
        if args.benchmark_only
        else f"dark-siren {args.catalog_mode} run complete"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
