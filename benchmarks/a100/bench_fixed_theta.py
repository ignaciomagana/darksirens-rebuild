#!/usr/bin/env python3
"""Fixed-coordinate likelihood benchmark for legacy darksirens and darksirens-core.

    python bench_fixed_theta.py --impl legacy|core --pe PE.h5 --sel SEL.h5 \\
        --plan spectral_full --coords coords.json --out record.json \\
        --n-calls 20 --warmup 3 --jit whole|asis --sel-batch N|none|default \\
        --pe-block N|none|default --seed S --label L [--device gpu|cpu] \\
        [--mask-chunk 131072] [--smi-log PATH] [--util-window-s 0] \\
        [--cache-dir DIR --cache-mode cold|warm|env] \\
        [--catalog CAT.h5] [--survey-fixed-override JSON [--allow-out-of-prior-fixed-survey]]

Dark-siren plans (``dark_*``) need ``--catalog``; the fixture's
``galaxy_density.json`` sidecar must pass ``dark_fixture.preflight`` (log10n0
inside both implementations' priors, the plan's survey fiducial, the sidecar's
bytes) or the run is refused (exit 2) before JAX is imported.

One process evaluates ONE implementation (both install as ``darksirens``) and
writes ONE record JSON (schema in README.md). Order of work:

1. install the XLA compile-request hooks, import the implementation, init JAX;
2. configure the plan, load the data (t_load), build the model (t_build),
   sync the device operands (t_transfer_sync), assert the plan's labels,
   bounds and fixed values against ``plans.py`` (fail loudly);
3. first call on coords[0] (compile + execution), 3 explicit warm-ups on
   coords[:3], then ``--n-calls`` timed calls cycling all coordinates, each
   ``jax.block_until_ready``; compile requests are counted per phase;
4. untimed: compile-hook self-test, jit evidence (jaxpr constants, AOT module
   size and compile time), per-coordinate diagnostics, sample masks, decoded
   parameter vectors, registry/decoder plan assertions, repeat consistency.

Exit status: 0 = record written and the plan assertions held; 3 = plan
assertion failed (record still written with ``status: plan_mismatch``);
4 = the implementation refused to load or build (record written with
``status: build_error`` and the exception); 2 = usage / input error.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never write __pycache__ into either package tree

import argparse  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import bench_common as bc  # noqa: E402
import plans  # noqa: E402


def _block_arg(v: str) -> str:
    v = str(v).strip().lower()
    if v in ("none", "default"):
        return v
    try:
        n = int(v)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a positive integer, 'none' or 'default'") from exc
    if n < 1:
        raise argparse.ArgumentTypeError("block size must be >= 1")
    return str(n)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--impl", required=True, choices=("legacy", "core"))
    ap.add_argument("--pe", required=True)
    ap.add_argument("--sel", required=True)
    ap.add_argument("--plan", required=True, choices=sorted(plans.PLANS))
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-calls", type=int, default=20)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--jit", required=True, choices=("whole", "asis"))
    ap.add_argument("--sel-batch", type=_block_arg, required=True,
                    help="N, 'none' (single pass) or 'default' (implementation default)")
    ap.add_argument("--pe-block", type=_block_arg, required=True,
                    help="N, 'none' (single pass) or 'default' (implementation default)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--device", choices=("gpu", "cpu", "auto"), default="auto")
    ap.add_argument("--mask-chunk", type=int, default=131072,
                    help="samples per chunk for the (untimed) per-sample mask pass")
    ap.add_argument("--smi-log", default=None,
                    help="gpu_run.sh nvidia-smi log to join over the timed loop (best effort)")
    ap.add_argument("--util-window-s", type=float, default=0.0,
                    help="after the timed loop, keep calling the kernel for this many seconds "
                         "(untimed per call) so a 1 Hz nvidia-smi sampler sees the steady state; "
                         "0 = off. The timed loop itself is usually far shorter than 1 s.")
    ap.add_argument("--cache-dir", default=None,
                    help="set JAX_COMPILATION_CACHE_DIR to DIR before JAX is imported "
                         "(overrides the env script's value); recorded in xla_cache")
    ap.add_argument("--catalog", default=None,
                    help="pixelated galaxy catalog (catalog_pixelated_nside_N.h5) for dark_* plans")
    ap.add_argument("--survey-fixed-override", default=None,
                    help="JSON {label: value} replacing FIXED survey values of a dark plan whose "
                         "survey block is fixed (fixed-coordinate checks only, e.g. the PR-6a "
                         "density {\"log10n0\": -4.301029995663981})")
    ap.add_argument("--allow-out-of-prior-fixed-survey", action="store_true",
                    help="accept a --survey-fixed-override value outside its prior: log10n0 "
                         "outside the log10n0 prior of either implementation, delta / sigma_kde "
                         "outside plans.SURVEY_BOUNDS (fixed coordinate only; recorded as a gap)")
    ap.add_argument("--cache-mode", choices=("cold", "warm", "env"), default="env",
                    help="cold: DIR must be absent or empty (created), so the first call is a "
                         "true compile; warm: DIR must already hold entries (a persistent-cache "
                         "rerun); env: no check (legacy behaviour). cold/warm need --cache-dir")
    return ap.parse_args(argv)


def _dir_inventory(path):
    """(files, bytes) under ``path``; (0, 0) when it does not exist."""
    n = b = 0
    if path and os.path.isdir(path):
        for root, _dirs, files in os.walk(path):
            for fn in files:
                n += 1
                try:
                    b += os.path.getsize(os.path.join(root, fn))
                except OSError:
                    pass
    return n, b


# ---------------------------------------------------------------------------
# Plan assertions
# ---------------------------------------------------------------------------
def _hex_list(xs):
    return [bc.fhex(x) for x in xs]


def _kinds_norm(kinds):
    out = []
    for k in kinds:
        k = list(k)
        out.append([str(k[0])] + [None if v is None else float(v) for v in k[1:]])
    return out


def check_plan_structure(adapter, plan) -> list:
    """Labels / bounds / kinds / fixed values of the BUILT model vs plans.py."""
    errs = []
    v = adapter.plan_labels_bounds()
    cfg = adapter.config()
    expected_labels = list(plan["sampled"])
    if cfg.get("plan_adapter"):
        expected_labels = list(cfg["plan_adapter"]["core_plan_labels"])
    if v["labels"] != expected_labels:
        errs.append(f"labels {v['labels']} != expected {expected_labels}")
        return errs
    bounds = dict(plan["sampled_bounds"])
    for n in expected_labels:
        if n not in bounds:
            bounds[n] = plans.label_bounds(plan, n)
    exp_lo = [bounds[n][0] for n in expected_labels]
    exp_hi = [bounds[n][1] for n in expected_labels]
    if _hex_list(v["lower"]) != _hex_list(exp_lo):
        errs.append(f"lower bounds {v['lower']} != {exp_lo}")
    if _hex_list(v["upper"]) != _hex_list(exp_hi):
        errs.append(f"upper bounds {v['upper']} != {exp_hi}")
    kinds = dict(plan["sampled_prior_kinds"])
    for n in expected_labels:
        if n not in kinds:
            kinds[n] = plans.label_kind(plan, n)
    exp_k = _kinds_norm([kinds[n] for n in expected_labels])
    if v.get("prior_kinds") and _kinds_norm(v["prior_kinds"]) != exp_k:
        errs.append(f"prior kinds {v['prior_kinds']} != {exp_k}")
    if plans.is_dark(plan):
        # Fixed survey values must be the plan's, in whichever form each side carries them.
        fixed_survey = {n: plan["fixed"][n] for n in plan["survey_labels"] if n in plan["fixed"]}
        got = (v.get("fixed_parameter_values") if adapter.impl == "legacy"
               else (v.get("fixed_inserted") or {}))
        for n, want in fixed_survey.items():
            if n not in got or bc.fhex(got[n]) != bc.fhex(want):
                errs.append(f"{adapter.impl} fixed survey {n}={got.get(n)!r} != plan {want!r}")
    if adapter.impl == "legacy":
        if _hex_list(v["pop_params_fid"]) != _hex_list(plan["population_fiducials"]):
            errs.append(f"legacy pop_params_fid {v['pop_params_fid']} != plan fiducials")
    else:
        exp_cos = {n: plan["fixed"][n] for n in ("H0", "Om0", "w0", "wa") if n in plan["fixed"]}
        got = v["fixed_cosmology"]
        if set(got) != set(exp_cos) or any(bc.fhex(got[n]) != bc.fhex(exp_cos[n]) for n in exp_cos):
            errs.append(f"core fixed_cosmology {got} != {exp_cos}")
        if plan["sample_population"] == "none":
            if v["fixed_population"] is None or _hex_list(v["fixed_population"]) != _hex_list(
                    plan["population_fiducials"]):
                errs.append(f"core fixed_population {v['fixed_population']} != plan fiducials")
        elif v["fixed_population"] is not None:
            errs.append("core fixed_population set for a plan that samples the population")
        if list(v["population_labels"]) != plan["population_labels"]:
            errs.append("core population_labels differ from plan")
    return errs


def check_registry(adapter, plan) -> tuple[list, dict]:
    errs = []
    r = adapter.registry_view()
    if r["labels"] != plan["population_labels"]:
        errs.append(f"registry labels {r['labels']} != plan")
    if _hex_list(r["lower"]) != _hex_list(plan["population_lower"]):
        errs.append("registry lower bounds differ from plan")
    if _hex_list(r["upper"]) != _hex_list(plan["population_upper"]):
        errs.append("registry upper bounds differ from plan")
    if _kinds_norm(r["prior_kinds"]) != _kinds_norm(plan["population_prior_kinds"]):
        errs.append("registry prior kinds differ from plan")
    if _hex_list(r["fiducials"]) != _hex_list(plan["population_fiducials"]):
        errs.append(f"registry fiducials {r['fiducials']} != plan")
    for key, name in (("H0_FID", "H0"), ("OM0_FID", "Om0"), ("W0_FID", "w0"), ("WA_FID", "wa")):
        if bc.fhex(r[key]) != bc.fhex(plan["fiducials"][name]):
            errs.append(f"{key}={r[key]} != plan {name} fiducial {plan['fiducials'][name]}")
    if plans.is_dark(plan):
        sv = r.get("survey") or {}
        for n in plan["survey_labels"]:
            want = list(plans.SURVEY_BOUNDS[n])
            got = (sv.get("bounds") or {}).get(n)
            if got is None or _hex_list(got) != _hex_list(want):
                errs.append(f"{adapter.impl} survey prior bounds {n} {got} != plans {want}")
        lo, hi, _src = plans.LOG10N0_PRIOR[adapter.impl]
        got = (sv.get("bounds") or {}).get("log10n0")
        if got is None or _hex_list(got) != _hex_list([lo, hi]):
            errs.append(f"{adapter.impl} log10n0 prior {got} != plans.LOG10N0_PRIOR {[lo, hi]}")
        for n in ("delta", "sigma_kde"):
            got = (sv.get("defaults") or {}).get(n)
            if got is None or bc.fhex(got) != bc.fhex(plans.SURVEY_FIDUCIALS[n]):
                errs.append(f"{adapter.impl} shared default {n}={got} != plans.SURVEY_FIDUCIALS "
                            f"{plans.SURVEY_FIDUCIALS[n]}")
    return errs, r


def _checkpoint(mem, tag):
    for m in mem:
        if m["tag"] == tag:
            return m
    raise KeyError(f"memory checkpoint {tag!r} missing")


def expected_full_vector(plan, names, row, pow10=None):
    """The full parameter vector the kernel must see; for a dark plan the
    log10n0 slot is reported as n0 = 10**log10n0, spelled as both decoders do."""
    vals = dict(plan["fixed"])
    vals.update(dict(zip(names, row)))
    out = [vals[n] for n in plan["full_order"]]
    if plans.is_dark(plan):
        i = plan["full_order"].index("log10n0")
        out[i] = pow10(out[i])
    return out


# ---------------------------------------------------------------------------
def main(argv=None):
    a = parse_args(argv)
    command_line = [sys.executable] + list(sys.argv if argv is None else ["bench_fixed_theta.py"] + argv)
    clock = bc.PhaseClock()
    clock.mark("start")
    started = bc.utc_now()

    if a.device == "cpu":
        cur = os.environ.get("JAX_PLATFORMS")
        if cur and cur != "cpu":
            print(f"--device cpu but JAX_PLATFORMS={cur}", file=sys.stderr)
            return 2
        os.environ["JAX_PLATFORMS"] = "cpu"

    override = None
    if a.survey_fixed_override:
        import json as _json

        override = _json.loads(a.survey_fixed_override)
    try:
        plan = plans.resolve_plan(a.plan, survey_fixed_override=override)
    except ValueError as exc:
        print(f"plan: {exc}", file=sys.stderr)
        return 2
    dark = plans.is_dark(plan)
    fixture_preflight = None
    override_gap = None
    if dark:
        import dark_fixture

        if not a.catalog or not os.path.isfile(a.catalog):
            print(f"plan {a.plan} is a dark-siren plan and needs --catalog (got {a.catalog!r})",
                  file=sys.stderr)
            return 2
        try:
            fixture_preflight = dark_fixture.preflight(a.catalog, a.pe, a.sel, plan)
        except dark_fixture.FixturePreflightError as exc:
            print(f"FIXTURE PREFLIGHT REFUSED: {exc}", file=sys.stderr)
            return 2
        # Every overridden survey value is checked against the prior bounds (log10n0
        # against BOTH implementations' priors, delta / sigma_kde against the shared
        # survey bounds): an out-of-bounds pin is a fixed-coordinate ablation only and
        # needs the explicit flag, and the record carries it as a gap.
        outside_all = []
        for lab, val in (override or {}).items():
            x = float(val)
            if lab == "log10n0":
                outside = [k for k, (lo, hi, _s) in plans.LOG10N0_PRIOR.items() if not lo <= x <= hi]
                if outside:
                    outside_all.append(f"log10n0={x!r} outside the log10n0 prior of {outside}")
            else:
                lo, hi = plans.SURVEY_BOUNDS[lab]
                if not lo <= x <= hi:
                    outside_all.append(f"{lab}={x!r} outside the survey bounds [{lo}, {hi}]")
        if outside_all and not a.allow_out_of_prior_fixed_survey:
            print(f"--survey-fixed-override: {'; '.join(outside_all)}; pass "
                  "--allow-out-of-prior-fixed-survey for a fixed-coordinate check", file=sys.stderr)
            return 2
        if outside_all:
            override_gap = (f"fixed-coordinate survey override {'; '.join(outside_all)}: parity "
                            "at a pinned coordinate only, never a sampled run")
    elif a.catalog or override:
        print(f"plan {a.plan} is catalog-free: --catalog / --survey-fixed-override refused",
              file=sys.stderr)
        return 2
    coords_doc = bc.read_json(a.coords)
    if coords_doc.get("plan") != a.plan:
        print(f"coords file is for plan {coords_doc.get('plan')!r}, not {a.plan!r}", file=sys.stderr)
        return 2
    if list(coords_doc["names"]) != plan["sampled"]:
        print(f"coords names {coords_doc['names']} != plan sampled {plan['sampled']}", file=sys.stderr)
        return 2
    if int(coords_doc["seed"]) != int(a.seed):
        print(f"--seed {a.seed} != coords seed {coords_doc['seed']}", file=sys.stderr)
        return 2
    coords = np.asarray([[float.fromhex(h) for h in row] for row in coords_doc["values_hex"]],
                        dtype=np.float64)
    n_coords = coords.shape[0]
    for f in (a.pe, a.sel):
        if not os.path.isfile(f):
            print(f"missing input {f}", file=sys.stderr)
            return 2

    # ---- persistent XLA cache policy (must precede ``import jax``) --------------
    cache_info = {"mode": a.cache_mode, "requested_dir": a.cache_dir,
                  "env_dir_before_override": os.environ.get("JAX_COMPILATION_CACHE_DIR")}
    if a.cache_mode in ("cold", "warm") and not a.cache_dir:
        print(f"--cache-mode {a.cache_mode} needs --cache-dir", file=sys.stderr)
        return 2
    if a.cache_dir:
        cdir = os.path.abspath(a.cache_dir)
        n0, b0 = _dir_inventory(cdir)
        if a.cache_mode == "cold" and n0:
            print(f"--cache-mode cold but {cdir} already holds {n0} files", file=sys.stderr)
            return 2
        if a.cache_mode == "warm" and not n0:
            print(f"--cache-mode warm but {cdir} is empty or missing", file=sys.stderr)
            return 2
        os.makedirs(cdir, exist_ok=True)
        os.environ["JAX_COMPILATION_CACHE_DIR"] = cdir
        cache_info.update(dir=cdir, files_before=n0, bytes_before=b0)
    else:
        cdir = os.environ.get("JAX_COMPILATION_CACHE_DIR")
        n0, b0 = _dir_inventory(cdir)
        cache_info.update(dir=cdir, files_before=n0, bytes_before=b0)

    # ---- JAX + hooks before the implementation is imported ----------------
    t0 = time.perf_counter()
    import jax

    counter = bc.CompileCounter().install()
    t_import_jax = time.perf_counter() - t0

    t0 = time.perf_counter()
    if a.impl == "legacy":
        import impl_legacy as impl
    else:
        import impl_core as impl
    pkg = impl.import_package()
    t_import_pkg = time.perf_counter() - t0

    t0 = time.perf_counter()
    jax.devices()
    t_backend = time.perf_counter() - t0
    device = bc.device_fingerprint(a.device)
    if a.device in ("gpu", "cpu") and device["backend"] != a.device:
        print(f"--device {a.device} but JAX backend is {device['backend']}", file=sys.stderr)
        return 2
    if not device["x64"]:
        print("jax_enable_x64 is off after the implementation configured JAX", file=sys.stderr)
        return 2

    record = {
        "schema": bc.RECORD_SCHEMA,
        "status": "running",
        "label": a.label,
        "implementation": a.impl,
        "command_line": command_line,
        "cwd": os.getcwd(),
        "started_utc": started,
        "harness": {"dir": HERE, "git": bc.package_fingerprint(type("M", (), {
            "__name__": "benchmarks.a100", "__file__": os.path.join(HERE, "plans.py")}))},
        "package": bc.package_fingerprint(pkg),
        "env": bc.env_fingerprint(),
        "device": device,
        "inputs": {"pe": bc.gwcat_file_info(a.pe), "sel": bc.gwcat_file_info(a.sel)},
        "plan": plan,
        "gaps": [],
    }
    if dark:
        import dark_fixture

        record["inputs"]["catalog"] = dict(dark_fixture.catalog_summary(a.catalog),
                                           path=os.path.abspath(a.catalog),
                                           bytes=os.path.getsize(a.catalog),
                                           sha256=bc.sha256_file(a.catalog))
        record["fixture_preflight"] = fixture_preflight
        if override_gap:
            record["gaps"].append(override_gap)
    record["harness"]["git"].pop("known_digest_match", None)

    mem = [bc.memory_checkpoint("after_import")]
    out_dir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(out_dir, exist_ok=True)
    save_dir = os.path.abspath(a.out) + ".legacy_save"
    adapter_cls = impl.LegacyAdapter if a.impl == "legacy" else impl.CoreAdapter
    adapter_kw = {"catalog_path": os.path.abspath(a.catalog)} if dark else {}
    adapter = adapter_cls(plan, os.path.abspath(a.pe), os.path.abspath(a.sel),
                          sel_batch=a.sel_batch, pe_block=a.pe_block, jit_mode=a.jit,
                          seed=a.seed, save_dir=save_dir, counter=counter, **adapter_kw)

    # ---- load + build ------------------------------------------------------
    clock.mark("build_start")
    snap = counter.snapshot()
    try:
        adapter.build()
    except Exception as exc:
        import traceback

        record["status"] = "build_error"
        record["build_error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback_tail": traceback.format_exc()[-4000:],
            "stage_timing": dict(adapter.timing),
        }
        record["xla_cache"] = cache_info
        if a.impl == "legacy":
            record["build_error"]["legacy_cli_args"] = adapter.cli_argv
            adapter.remove_save_dir()
        record["finished_utc"] = bc.utc_now()
        bc.write_json(a.out, record)
        print(f"BUILD ERROR ({a.impl}, plan {a.plan}): {type(exc).__name__}: {exc}", file=sys.stderr)
        return 4
    compile_build = counter.delta(snap)
    clock.mark("build_end")
    mem.append(bc.memory_checkpoint("after_build"))

    t0 = time.perf_counter()
    ops = adapter.operands_for_sync()
    jax.block_until_ready(ops)
    t_sync = time.perf_counter() - t0
    operand_bytes = bc.tree_nbytes(ops)

    record["config"] = adapter.config()
    record["config"].update(seed=a.seed, n_calls=a.n_calls, warmup=a.warmup, device=a.device,
                            mask_chunk=a.mask_chunk)
    dims = adapter.dims()
    dims["T_obs_yr"] = record["inputs"]["sel"]["attrs"].get("T_obs_yr")
    dims["n_coords"] = int(n_coords)
    record["dims"] = dims
    if a.impl == "legacy":
        log_path = os.path.abspath(a.out) + ".legacy_cli.log"
        with open(log_path, "w") as f:
            f.write(adapter.cli_log)
        record["legacy_cli_log"] = {"path": log_path, "sha256": bc.sha256_file(log_path),
                                    "tail": adapter.cli_log[-2500:]}

    plan_errors = check_plan_structure(adapter, plan)
    if plan_errors:
        record["status"] = "plan_mismatch"
        record["plan_errors"] = plan_errors
        bc.write_json(a.out, record)
        print("PLAN MISMATCH:\n  " + "\n  ".join(plan_errors), file=sys.stderr)
        return 3

    record["coords"] = {
        "source_file": os.path.abspath(a.coords),
        "source_sha256": bc.sha256_file(a.coords),
        "coords_digest": coords_doc.get("coords_digest"),
        "seed": int(coords_doc["seed"]),
        "names": list(coords_doc["names"]),
        "implementation_labels": adapter.labels,
        "values_hex": [[bc.fhex(x) for x in row] for row in coords],
        "values": coords.tolist(),
        "kinds": coords_doc.get("kinds"),
        "repeat_of": coords_doc.get("repeat_of"),
    }

    # ---- timed section -------------------------------------------------------
    per_call_values = {i: [] for i in range(n_coords)}
    clock.mark("first_call_start")
    snap = counter.snapshot()
    t0 = time.perf_counter()
    v = adapter.timed_call(coords[0])
    jax.block_until_ready(v)
    t_first = time.perf_counter() - t0
    compile_first = counter.delta(snap)
    per_call_values[0].append(v)
    clock.mark("first_call_end")
    cache_info["files_after_first_call"], cache_info["bytes_after_first_call"] = \
        _dir_inventory(cache_info.get("dir"))
    mem.append(bc.memory_checkpoint("after_first_call"))

    snap = counter.snapshot()
    warm_times = []
    for i in range(a.warmup):
        k = i % n_coords
        t0 = time.perf_counter()
        v = adapter.timed_call(coords[k])
        jax.block_until_ready(v)
        warm_times.append(time.perf_counter() - t0)
        per_call_values[k].append(v)
    compile_warm = counter.delta(snap)
    clock.mark("warmup_end")

    snap = counter.snapshot()
    times, idx = [], []
    load_before = os.getloadavg() if hasattr(os, "getloadavg") else None
    clock.mark("timed_loop_start")
    for i in range(a.n_calls):
        k = i % n_coords
        t0 = time.perf_counter()
        v = adapter.timed_call(coords[k])
        jax.block_until_ready(v)
        times.append(time.perf_counter() - t0)
        idx.append(k)
        per_call_values[k].append(v)
    clock.mark("timed_loop_end")
    compile_loop = counter.delta(snap)
    load_after = os.getloadavg() if hasattr(os, "getloadavg") else None
    mem.append(bc.memory_checkpoint("after_timed_loop"))

    # ---- optional utilisation window (steady-state calls for the 1 Hz sampler) --
    util_window = None
    if a.util_window_s > 0:
        snap = counter.snapshot()
        clock.mark("util_window_start")
        t0 = time.perf_counter()
        n_u = 0
        while True:
            v = adapter.timed_call(coords[n_u % n_coords])
            jax.block_until_ready(v)
            n_u += 1
            if time.perf_counter() - t0 >= a.util_window_s:
                break
        wall_u = time.perf_counter() - t0
        clock.mark("util_window_end")
        util_window = {"seconds_requested": a.util_window_s, "wall_s": wall_u, "n_calls": n_u,
                       "mean_call_s": wall_u / n_u, "compile": counter.delta(snap),
                       "note": "back-to-back kernel calls cycling the coordinates, each "
                               "block_until_ready; values not recorded (same kernel as the "
                               "timed loop)"}

    # ---- untimed: hook self-test, jit evidence ------------------------------
    selftest = bc.compile_hook_selftest(counter)
    try:
        jit_ev = adapter.jit_evidence(coords[0])
    except Exception as exc:  # evidence must not kill the record
        jit_ev = {"error": f"{type(exc).__name__}: {exc}"}
    mem.append(bc.memory_checkpoint("after_jit_evidence"))

    # ---- per-coordinate values -----------------------------------------------
    timed_hex = {k: [bc.fhex(np.asarray(x)) for x in vals] for k, vals in per_call_values.items()}
    timed_consistent = all(len(set(h)) <= 1 for h in timed_hex.values())
    per_coord = []
    cat_rows_all, cat_pe_all, cat_sel_all = [], [], []
    if dark:
        import dark_diag
    n = dims["n_events"]
    maxvar = float(record["config"]["max_likelihood_variance"])
    plan_value_errors = []
    for i in range(n_coords):
        row = coords[i]
        if timed_hex[i]:
            total = float.fromhex(timed_hex[i][0])
        else:  # coordinate never hit by the timed loop (n_calls < n_coords)
            vv = adapter.timed_call(row)
            jax.block_until_ready(vv)
            total = float(np.asarray(vv))
            timed_hex[i] = [bc.fhex(total)]
        d = adapter.diagnostics(row)
        ell = np.asarray(d["event_log_evidence"], dtype=np.float64)
        evar = np.asarray(d["event_mc_variance"], dtype=np.float64)
        n_eff = float(d["n_eff"])
        pe_var = float(np.sum(evar))
        budget = max(maxvar - pe_var, 1e-12)
        threshold = max(5.0 * n, (n * n) / budget)
        sigma2 = pe_var + (n * n) / n_eff if n_eff != 0 else float("inf")
        dt = float(d["diag_total_logL"])
        rel = (abs(dt - total) / abs(total)) if (np.isfinite(total) and total != 0) else (
            0.0 if (dt == total or (np.isnan(dt) and np.isnan(total))) else float("inf"))
        cat_summary = None
        if dark:
            pe_t, sel_t = adapter.sample_terms(row, a.mask_chunk)
            rows_t = adapter.catalog_rows(row)
            pe_s, pe_sup, pe_fin = pe_t["structural"], pe_t["support"], pe_t["final"]
            se_s, se_sup, se_fin = sel_t["structural"], sel_t["support"], sel_t["final"]
            cat_summary = dark_diag.coord_summary(pe_t, sel_t, rows_t, n, dims["nsamp"],
                                                  dims["ndraw"])
            cat_rows_all.append(rows_t)
            cat_pe_all.append({"log_prior": pe_t["log_prior"]})
            cat_sel_all.append({"log_prior": sel_t["log_prior"]})
        else:
            (pe_s, pe_sup, pe_fin), (se_s, se_sup, se_fin) = adapter.masks(row, a.mask_chunk)
        per_event_counts = pe_fin.reshape(n, dims["nsamp"]).sum(axis=1).astype(int).tolist()
        decoded = adapter.decode(row)
        expected = expected_full_vector(plan, coords_doc["names"], row,
                                        pow10=getattr(adapter, "pow10", None))
        if _hex_list(decoded) != _hex_list(expected):
            plan_value_errors.append(f"coord {i}: decoded {decoded} != expected {expected}")
        per_coord.append({
            "index": i,
            "kind": (coords_doc.get("kinds") or [None] * n_coords)[i],
            "total_logL": bc.scalar_entry(total),
            "total_finite": bool(np.isfinite(total)),
            "diag_total_logL": bc.scalar_entry(dt),
            "kernel_vs_diag_total": {"bitwise": bc.fhex(dt) == bc.fhex(total), "rel": bc.fval(rel)},
            "event_log_evidence": bc.array_entry(ell),
            "event_mc_variance": bc.array_entry(evar),
            "sum_event_log_evidence": bc.scalar_entry(float(np.sum(ell))),
            "log_mu": bc.scalar_entry(d["log_mu"]),
            "n_eff": bc.scalar_entry(n_eff),
            "selection_log_correction": bc.scalar_entry(d["selection_log_correction"]),
            "pe_variance_sum": bc.scalar_entry(pe_var),
            "sigma2_lnL": bc.scalar_entry(sigma2),
            "guard_threshold": bc.scalar_entry(threshold),
            "guard_pass": bool(n_eff > threshold),
            "masks": {
                "pe_structural": bc.mask_entry(pe_s),
                "pe_support": bc.mask_entry(pe_sup),
                "pe_final": bc.mask_entry(pe_fin),
                "pe_final_per_event_count": per_event_counts,
                "sel_structural": bc.mask_entry(se_s),
                "sel_support": bc.mask_entry(se_sup),
                "sel_final": bc.mask_entry(se_fin),
            },
            "decoded_full": {"names": plan.get("decoded_order", plan["full_order"]),
                             "hex": _hex_list(decoded)},
            "timed_values_hex": timed_hex[i],
        })
        if cat_summary is not None:
            per_coord[-1]["catalog"] = cat_summary
    mem.append(bc.memory_checkpoint("after_diagnostics"))
    if dark:
        npz_path = os.path.abspath(a.out) + ".catalog.npz"
        arrays = dark_diag.stack_npz(cat_rows_all, cat_pe_all, cat_sel_all)
        np.savez_compressed(npz_path, **arrays)
        record["catalog_arrays"] = {
            "file": os.path.basename(npz_path),
            "sha256": bc.sha256_file(npz_path),
            "arrays": {k: {"shape": list(v.shape), "dtype": v.dtype.str} for k, v in arrays.items()},
            "note": ("per coordinate: per-row (union compact rows) log_Nobs, log_Z, N_miss, f, "
                     "log_depth_mass, row_empty; per-sample log p(z|row) of the PE samples and "
                     "the injections in FILE order; loaded by compare_records.py from the "
                     "record's directory"),
        }

    # ---- masks are reported in FILE order: prove it against the HDF5 datasets --
    import h5py

    pe_dL, sel_dL = adapter.mask_order_dL()
    with h5py.File(a.pe, "r") as f:
        file_pe_dL = np.asarray(f["dL"][()], dtype=np.float64)
    with h5py.File(a.sel, "r") as f:
        file_sel_dL = np.asarray(f["dL"][()], dtype=np.float64)
    record["mask_order"] = {
        "order": "file order of the PE and selection HDF5 datasets",
        "pe_dL_equals_file": bool(np.array_equal(pe_dL, file_pe_dL)),
        "sel_dL_equals_file": bool(np.array_equal(sel_dL, file_sel_dL)),
    }
    if not (record["mask_order"]["pe_dL_equals_file"] and record["mask_order"]["sel_dL_equals_file"]):
        record["gaps"].append("mask order could not be verified against the file order "
                              "(dL arrays differ): mask sha256 comparisons are not meaningful")

    # ---- repeat consistency ---------------------------------------------------
    rep_pairs = [(int(k), int(v)) for k, v in (coords_doc.get("repeat_of") or {}).items()]
    mismatches = []
    fields = ("total_logL", "diag_total_logL", "log_mu", "n_eff", "selection_log_correction",
              "sigma2_lnL")
    for j, i in rep_pairs:
        A, B = per_coord[i], per_coord[j]
        if _hex_list(coords[i]) != _hex_list(coords[j]):
            mismatches.append(f"coords {i} and {j} are not identical")
        for fld in fields:
            if A[fld]["hex"] != B[fld]["hex"]:
                mismatches.append(f"{fld}: coord {i} {A[fld]['hex']} vs coord {j} {B[fld]['hex']}")
        for fld in ("event_log_evidence", "event_mc_variance"):
            if A[fld]["hex"] != B[fld]["hex"]:
                mismatches.append(f"{fld} differs between coord {i} and {j}")
        for mk in A["masks"]:
            if A["masks"][mk] != B["masks"][mk]:
                mismatches.append(f"mask {mk} differs between coord {i} and {j}")
        if "catalog" in A and A["catalog"] != B["catalog"]:
            mismatches.append(f"catalog-side diagnostics differ between coord {i} and {j}")
        if set(A["timed_values_hex"]) | set(B["timed_values_hex"]) != {A["total_logL"]["hex"]}:
            mismatches.append(f"timed-loop values of coords {i}/{j} not all bit-identical")
    record["repeat_consistency"] = {
        "pairs": rep_pairs,
        "bitwise": not mismatches,
        "mismatches": mismatches,
        "timed_loop_bitwise_consistent": timed_consistent,
        "fields_checked": list(fields) + ["event_log_evidence", "event_mc_variance", "masks",
                                          "timed_values"] + (["catalog"] if dark else []),
    }

    # ---- registry / decoder assertions (untimed, JAX ops allowed) -------------
    reg_errors, reg_view = check_registry(adapter, plan)
    record["plan_assertions"] = {
        "structure": "ok",
        "registry": reg_errors or "ok",
        "decode": plan_value_errors or "ok",
        "registry_view": reg_view,
    }

    # ---- timing summary --------------------------------------------------------
    warm = bc.stats(times)
    warm["calls_s"] = times
    warm["coord_index"] = idx
    record["timing"] = {
        "t_import_jax_s": t_import_jax,
        "t_import_package_s": t_import_pkg,
        "t_backend_init_s": t_backend,
        "t_config_s": adapter.timing.get("t_config_s"),
        "t_load_s": adapter.timing.get("t_load_s"),
        "t_build_s": adapter.timing.get("t_build_s"),
        "t_build_breakdown": {k: v for k, v in adapter.timing.items()
                              if k not in ("t_config_s", "t_load_s", "t_build_s")},
        "t_transfer_sync_s": t_sync,
        "transfer_sync_note": ("jax.block_until_ready on the device operands right after the "
                               "build (PE/selection GWEvents + distance table [+ legacy "
                               "smoothing operator]): residual host-to-device transfer"),
        "operand_bytes": operand_bytes,
        "t_first_call_s": t_first,
        "first_call_note": "compile + first execution on coords[0]",
        "warmup_s": warm_times,
        "warm": warm,
        "timed_call_note": ("each timed call = jnp.asarray(coord) + kernel + "
                            "jax.block_until_ready (as legacy bench_likelihood_call.py:352)"),
        "compile": {
            "during_build": compile_build,
            "first_call": compile_first,
            "warmup": compile_warm,
            "timed_loop": compile_loop,
            "total": {"requests": counter.requests, "compiles": counter.compiles},
            "hook_selftest": selftest,
            "hooks": "jax._src.compiler.compile_or_get_cached (requests) and backend_compile",
            "xla_cache_dir": device.get("xla_cache_dir"),
        },
        "memory": mem,
        # Kernel-phase peaks: the process peak at the END of the timed loop. The
        # counters are cumulative (ru_maxrss, memory_stats peak_bytes_in_use), so
        # this includes the build, first call and warm-ups, but NOT the untimed
        # jit-evidence / diagnostics / mask passes that follow, which allocate
        # their own buffers and can exceed the kernel's own peak.
        "peak_device_bytes": _checkpoint(mem, "after_timed_loop")["device_peak_bytes_in_use"],
        "peak_host_rss_bytes": _checkpoint(mem, "after_timed_loop")["host_maxrss_bytes"],
        "peak_device_bytes_all_phases": max([m["device_peak_bytes_in_use"] or 0 for m in mem]) or None,
        "peak_host_rss_bytes_all_phases": max(m["host_maxrss_bytes"] for m in mem),
        "peak_note": ("peak_device_bytes / peak_host_rss_bytes = process peak at the end of the "
                      "timed loop (import + build + first call + warm-ups + timed loop); "
                      "*_all_phases also covers the untimed jit evidence, diagnostics and "
                      "mask passes"),
        "phase_clock": clock.stamps,
    }
    record["timing"]["host_loadavg_timed_loop"] = {
        "before": list(load_before) if load_before else None,
        "after": list(load_after) if load_after else None,
        "os_cpu_count": os.cpu_count(),
        "note": "1/5/15-min host load averages: other processes competing for the host",
    }
    if a.n_calls < 20:
        record["gaps"].append(f"n_calls={a.n_calls} < 20: below the campaign minimum")
    if compile_loop["requests"] > 0:
        record["gaps"].append(
            f"{compile_loop['requests']} compile requests inside the timed loop: the warm "
            "statistics and the peak memory include per-call compilation and are not a "
            "steady state (peak memory grows with --n-calls)")
    if a.smi_log:
        time.sleep(2.5)
        record["timing"]["gpu_util_timed_loop"] = bc.smi_window_stats(
            a.smi_log, clock.stamps["timed_loop_start"]["unix"],
            clock.stamps["timed_loop_end"]["unix"])
        if util_window is not None:
            util_window["smi"] = bc.smi_window_stats(
                a.smi_log, clock.stamps["util_window_start"]["unix"],
                clock.stamps["util_window_end"]["unix"])
        if record["timing"]["gpu_util_timed_loop"].get("rows", 0) < 3 and (
                util_window is None or util_window["smi"].get("rows", 0) < 3):
            record["gaps"].append("fewer than 3 nvidia-smi rows fall inside the timed loop and no "
                                  "--util-window-s window covers the steady state: GPU "
                                  "utilisation is not measured by this record")
    else:
        record["timing"]["gpu_util_timed_loop"] = None
    record["timing"]["util_window"] = util_window

    # ---- persistent-cache state: cold/warm evidence for the first call ----------
    cache_info["files_at_end"], cache_info["bytes_at_end"] = _dir_inventory(cache_info.get("dir"))
    cache_info["jax_config"] = {
        k: getattr(jax.config, k, None) for k in (
            "jax_compilation_cache_dir", "jax_enable_compilation_cache",
            "jax_persistent_cache_min_compile_time_secs",
            "jax_persistent_cache_min_entry_size_bytes")}
    cache_info["first_call_requests"] = compile_first["requests"]
    cache_info["first_call_compiles"] = compile_first["compiles"]
    cache_info["first_call_cache_hits"] = compile_first["requests"] - compile_first["compiles"]
    cache_info["first_call_all_compiled"] = compile_first["requests"] == compile_first["compiles"]
    cache_info["note"] = ("compile_or_get_cached requests minus backend_compile calls = executables "
                          "served from the persistent cache; cold mode starts from an empty "
                          "directory, so any hit there is an in-process reuse, not a stale entry. "
                          "Entries are written only for compiles above "
                          "jax_persistent_cache_min_compile_time_secs.")
    if cache_info["jax_config"]["jax_compilation_cache_dir"] != cache_info.get("dir"):
        record["gaps"].append(
            f"jax_compilation_cache_dir={cache_info['jax_config']['jax_compilation_cache_dir']!r} "
            f"differs from the requested cache dir {cache_info.get('dir')!r}")
    if a.cache_mode == "cold" and not cache_info["first_call_all_compiled"]:
        record["gaps"].append("cold cache mode but the first call had persistent-cache hits")
    record["xla_cache"] = cache_info

    record["jit_evidence"] = jit_ev
    record["diagnostics_provenance"] = adapter.diag_provenance
    record["values"] = {"per_coord": per_coord}
    record["gaps"].extend(adapter.gaps)
    leftovers = adapter.cleanup()
    if leftovers:
        record["gaps"].append(f"legacy save_path not empty after build: {leftovers}")
    record["finished_utc"] = bc.utc_now()
    status = "ok"
    if reg_errors or plan_value_errors:
        status = "plan_mismatch"
    record["status"] = status
    bc.write_json(a.out, record)

    fin = sum(1 for r in per_coord if r["total_finite"])
    print(f"[{a.label}] {a.impl} plan={a.plan} jit={a.jit} backend={device['backend']} "
          f"events={dims['n_events']}x{dims['nsamp']} inj={dims['n_injections']} "
          f"first={t_first:.3f}s warm median={warm['median_s'] * 1e3:.3f} ms "
          f"(min {warm['min_s'] * 1e3:.3f}) loop compiles={compile_loop} "
          f"repeat_bitwise={record['repeat_consistency']['bitwise']} finite={fin}/{n_coords} "
          f"status={status} -> {a.out}")
    if status != "ok":
        print("PLAN MISMATCH:\n  " + "\n  ".join(reg_errors + plan_value_errors), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
