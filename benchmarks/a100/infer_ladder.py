#!/usr/bin/env python3
"""Gate 5 inference ladder: one nested-sampling run of one implementation.

    python infer_ladder.py --impl legacy|core --rung 1|2|3|4|5|5b --sampler tinyns|dynesty \\
        --pe PE.h5 --sel SEL.h5 --nlive N --dlogz D --seed S --out DIR \\
        [--device cpu|gpu|auto] [--guard soft|hard|auto] [--max-variance 1.0] \\
        [--max-samples 0] [--tinyns-preset recommended] [--sel-batch none|N] [--pe-block none|N] \\
        [--cache-dir DIR --cache-mode cold|warm|env] [--smi-log PATH] [--mem-poll-s 1.0] \\
        [--label L] [--arm A] [--parity-ref ID ...] [--policy-note TEXT]
        [--max-evals N] [--max-wall-s S] [--describe]

The rungs (``ladder_configs/rungs.json``, Fable-owned) are expressed in each code's own
production path, with every sampler setting passed explicitly and identically:

* legacy: the ``darksirens_inference`` CLI's own phase functions in ``main()``'s order
  (``darksirens/cli/inference.py:4461-4529``): option resolution, ``_load_and_report_data``,
  ``_build_and_report_parameter_space``, ``_prepare_run_dir`` (checkpoint plan; off here),
  ``_build_likelihood``, then ``_run_sampling`` -> ``inference.sampling.run_sampler``.
  ``_save_outputs`` (samples.npy, results.hdf5, corner plot) is NOT run: this driver writes
  its own posterior file and times the sampler, not the plotting.
* core: ``ds.model`` + ``ds.load_events`` / ``ds.load_injections`` + ``bind_analysis`` (the
  binding ``ds.infer`` performs for an ordinary analysis, ``inference/public.py:162-181``),
  then ``ds.infer(ds.InferenceTarget(likelihood, plan), sampler=..., **options)`` (the same
  ``_execute_target`` call, ``public.py:139-160,183-188``). Rungs whose sampled set core
  cannot express publicly (a partially fixed population, rungs 3 and 4) go through the same
  public ``InferenceTarget`` seam with the non-sampled population parameters inserted at the
  preset by a harness closure (recorded under ``core_expression``).

Instrumentation (observation only; no sampler RNG or numerics touched):

* the likelihood handed to the sampler is wrapped in a counter (eager vs traced calls);
* ``tinyns.NestedSampler.run`` gets a ``callback`` (every outer iteration / JAX block)
  that records the sampler state; ``dynesty`` ``run_nested`` gets a ``print_func`` that
  records every iteration; both write ``progress.csv`` (iteration, log-volume, logZ,
  remaining dlogz, cumulative calls, wall time);
* a monitor thread samples ``memory_stats()`` (GPU) and the host RSS every ``--mem-poll-s``;
* XLA compile requests / compilations (and their seconds) are counted per phase.

Outputs in ``--out`` DIR: ``record.json`` (schema ``darksirens-infer-ladder/1``),
``progress.csv``, ``posterior.npz`` (equal-weight samples with named columns, dead-point
logl/logwt), ``memory.csv``, ``run.log`` (stdout+stderr tee), and ``legacy_run/`` (the
legacy CLI's run directory: settings.json, run_fingerprint.json).

Exit status: 0 ok (or described); 2 usage/input; 3 plan assertion failed; 4 build error;
5 sampler error (e.g. the nested-sampler preflight abort under the hard guard); 6 timeout
(SIGTERM during sampling, e.g. from ``timeout``: the record, with status ``timeout``, and the
progress trace up to that point are written); 7 budget-capped (``--max-evals`` or
``--max-wall-s`` reached during sampling: status ``budget-capped``, progress trace kept, no
posterior). The record is written in every case except 2.

Budgets (``--max-evals``, ``--max-wall-s``; 0 = none) are observation-side stops: the check
runs in the progress hook after each progress row is recorded (TinyNS: once per JAX block of
``jax_block_size`` iterations, so the evaluation count can overshoot by at most one block;
dynesty: every iteration) and, for the wall budget, also as a SIGALRM at the limit. The
evaluation count is the one reported in ``likelihood_calls.n_like_evals`` (TinyNS: preflight
eager calls + the sampler's ncall; dynesty: every eager call during sampling). The wall budget
is measured from the start of the sampling phase (preflight included). Nothing is passed to
the sampler, so a capped run is the same deterministic trajectory as an uncapped one up to the
stop.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import signal  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import bench_common as bc  # noqa: E402
import plans  # noqa: E402

SCHEMA = "darksirens-infer-ladder/1"
RUNGS_FILE = os.path.join(HERE, "ladder_configs", "rungs.json")


class LadderTimeout(BaseException):
    """Raised by the SIGTERM handler during sampling (external per-run timeout)."""


class LadderBudget(BaseException):
    """Raised by the progress hook / SIGALRM when a --max-evals / --max-wall-s budget is reached."""

    def __init__(self, kind, value, limit):
        super().__init__(f"budget reached: {kind} {value} >= {limit}")
        self.kind, self.value, self.limit = kind, value, limit


PROGRESS_COLUMNS = ("row", "phase", "iteration", "log_volume", "log_volume_source", "logz",
                    "dlogz_remaining", "ncall_cum", "logl_min", "logl_live_max", "t_since_sampling_s",
                    "t_unix")


# ----------------------------------------------------------------------------
# Rungs
# ----------------------------------------------------------------------------
def load_rungs(path=RUNGS_FILE):
    with open(path) as f:
        return json.load(f)


def resolve_rung(rung_id: str, doc: dict | None = None) -> dict:
    """Expand a rung into sampled labels, bounds, kinds, fixed values and the centre.

    Uses only ``plans.py`` constants (the population registry view both implementations
    are asserted against, the H0 box, the fixed cosmology and the GWTC-5 preset).
    """
    doc = doc or load_rungs()
    if rung_id not in doc["rungs"]:
        raise KeyError(f"unknown rung {rung_id!r}; known {sorted(doc['rungs'])}")
    r = doc["rungs"][rung_id]
    model = r["population_model"]
    pop = plans.population_spec(model)
    labels = list(pop["labels"])
    k = r["sample_population"]
    if k == "all":
        pop_sampled = list(labels)
    elif k == "none":
        pop_sampled = []
    else:
        pop_sampled = labels[: int(k)]
    preset = r.get("population_preset")
    if preset:
        pre = plans.POPULATION_PRESETS[preset]
        if pre["population_model"] != model:
            raise ValueError(f"rung {rung_id}: preset {preset} belongs to {pre['population_model']}")
    fid = {plans.H0_LABEL: plans.H0_FIDUCIAL, **plans.FIXED_COSMOLOGY}
    fid.update(dict(zip(labels, pop["fiducials"])))
    bounds = {plans.H0_LABEL: list(plans.H0_BOUNDS)}
    bounds.update({lab: [lo, hi] for lab, lo, hi in zip(labels, pop["lower"], pop["upper"])})
    kinds = {plans.H0_LABEL: ["uniform", None, None]}
    kinds.update({lab: list(kd) for lab, kd in zip(labels, pop["prior_kinds"])})
    sampled = ([plans.H0_LABEL] if r["sample_H0"] else []) + pop_sampled
    full_order = list(plans.COSMOLOGY_ORDER) + labels
    fixed = {n: fid[n] for n in full_order if n not in sampled}
    # Joint constraints over the SAMPLED vector: a declared group applies only when all
    # its members are sampled (legacy inference/prior.py:1382-1405 skips a group with a
    # non-sampled member; the preset satisfies every group, so the fixed ones hold).
    expected_constraints, skipped = [], []
    for kind, members in pop.get("constraint_groups") or []:
        if all(m in sampled for m in members):
            expected_constraints.append([kind, [sampled.index(m) for m in members]])
        else:
            skipped.append([kind, list(members)])
            if any(m in sampled for m in members):
                raise ValueError(f"rung {rung_id}: constraint {kind} {members} is partly sampled")
    return {
        "rung": rung_id,
        "title": r["title"],
        "population_model": model,
        "population_preset": preset,
        "kernel_plan": r.get("kernel_plan"),
        "sample_H0": bool(r["sample_H0"]),
        "sample_population": k,
        "population_labels": labels,
        "sampled": sampled,
        "sampled_lower": [bounds[n][0] for n in sampled],
        "sampled_upper": [bounds[n][1] for n in sampled],
        "sampled_prior_kinds": [kinds[n] for n in sampled],
        "fixed": fixed,
        "full_order": full_order,
        "centre": [fid[n] for n in sampled],
        "expected_full_at_centre": [fid[n] for n in full_order],
        "expected_joint_constraints": expected_constraints,
        "skipped_constraint_groups": skipped,
        "H0_bounds": list(plans.H0_BOUNDS),
        "fixed_cosmology": dict(plans.FIXED_COSMOLOGY),
        "H0_fiducial": plans.H0_FIDUCIAL,
        "core_population_fixed": (plans.POPULATION_PRESETS[preset]["core_population_fixed"]
                                  if (preset and k == "none") else (True if k == "none" else None)),
    }


def _block(v):
    v = str(v).strip().lower()
    if v in ("none", "off"):
        return "none"
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError("block size must be >= 1 or 'none'")
    return str(n)


# ----------------------------------------------------------------------------
# Invocations (the exact form each code is driven with)
# ----------------------------------------------------------------------------
def legacy_argv(rung, pe, sel, save_path, s):
    """The ``darksirens_inference`` argument vector for one rung and the matched settings."""
    blk = {"none": "off"}
    argv = [
        "--gw_path", pe,
        "--gwselection_path", sel,
        "--universe_model", "spectral_sirens",
        "--pop_model", rung["population_model"],
        "--sampler", s["sampler"],
        "--save_path", save_path,
        "--seed", str(int(s["seed"])),
        "--nlive", str(int(s["nlive"])),
        "--dlogz", repr(float(s["dlogz"])),
        "--max_samples", str(int(s["max_samples"])),
        "--tinyns_preset", s["tinyns_preset"],
        "--checkpoint_interval", "off",
        "--resume", "off",
        "--sampler_preflight", s["sampler_preflight"],
        "--prior_transform_dispatch", s["prior_transform_dispatch"],
        "--show_progress", "true",
        "--dynesty_diagnostics", "false",
        "--sel_batch_size", blk.get(s["sel_batch_size"], s["sel_batch_size"]),
        "--pe_event_block", blk.get(s["pe_event_block"], s["pe_event_block"]),
        "--selection_neff_guard", s["guard"],
        "--max_likelihood_variance", repr(float(s["max_likelihood_variance"])),
    ]
    fixed_values = {}
    if rung["sample_H0"]:
        # H0 on the target box, Om0 pinned individually, (w0, wa) = the dark-energy block.
        argv += ["--fix_de", "true", "--prior_overrides", json.dumps({"H0": list(rung["H0_bounds"])})]
        fixed_values["Om0"] = rung["fixed"]["Om0"]
    else:
        argv += ["--fix_cosmology", "true"]  # H0_FID, OM0_FID, W0_FID, WA_FID
    k = rung["sample_population"]
    if k == "none":
        # the bespoke GWTC-5 model's preset IS its fiducial vector for either set
        argv += ["--fix_population", "true", "--population_fiducials", "legacy"]
    elif k != "all":
        for lab in rung["population_labels"][int(k):]:
            fixed_values[lab] = rung["fixed"][lab]
    if fixed_values:
        argv += ["--fixed_parameter_values", json.dumps(fixed_values)]
    return argv


def core_expression(rung, s):
    """Human-readable core call for the record and the report."""
    h0 = (f"({rung['H0_bounds'][0]}, {rung['H0_bounds'][1]})" if rung["sample_H0"]
          else repr(rung["H0_fiducial"]))
    fx = rung["core_population_fixed"]
    pop = (f"ds.Population({rung['population_model']!r}, fixed={fx!r})" if fx
           else f"ds.Population({rung['population_model']!r})")
    k = rung["sample_population"]
    ordinary = k in ("all", "none")
    opts = (f"sampler={s['sampler']!r}, nlive={s['nlive']}, dlogz={s['dlogz']}, seed={s['seed']}, "
            f"max_samples={s['max_samples']}, tinyns_preset={s['tinyns_preset']!r}, "
            f"sampler_preflight={s['sampler_preflight']!r}, "
            f"prior_transform_dispatch={s['prior_transform_dispatch']!r}, show_progress=True, "
            "checkpoint_interval_seconds=0.0, checkpoint_file_resolved=None, "
            "resume_from_resolved=None, dynesty_diagnostics=False")
    model = (f"analysis = ds.model(cosmology=ds.Cosmology(H0={h0}, Om0=0.3075, w0=-1.0, wa=0.0), "
             f"population={pop})")
    lk = (f"bind_analysis(analysis, events=ds.load_events(PE), injections=ds.load_injections(SEL), "
          f"selection_neff_soft_guard={s['guard'] == 'soft'}, "
          f"max_likelihood_variance={float(s['max_likelihood_variance'])}, "
          f"sel_batch_size={None if s['sel_batch_size'] == 'none' else int(s['sel_batch_size'])}, "
          f"pe_event_block={None if s['pe_event_block'] == 'none' else int(s['pe_event_block'])})")
    if ordinary:
        public = (f"ds.infer(analysis, events=..., injections=..., selection_neff_guard={s['guard']!r}, "
                  f"max_likelihood_variance={float(s['max_likelihood_variance'])}, "
                  f"sel_batch_size=None, pe_event_block=None, {opts})")
        run = f"ds.infer(ds.InferenceTarget(log_likelihood={lk}, parameters=analysis.parameters), {opts})"
    else:
        public = None
        run = (f"ds.infer(ds.InferenceTarget(log_likelihood=lambda th: {lk}(full.at[idx].set(th)), "
               f"parameters=ParameterPlan(sampled subset of analysis.parameters)), {opts})")
    return {"model": model, "run": run, "ordinary_public_equivalent": public,
            "note": ("ds.infer(analysis, ...) = bind_analysis + _execute_target(likelihood, "
                     "analysis.parameters) + angular prior-volume correction "
                     "(src/darksirens/inference/public.py:162-189); the InferenceTarget form runs "
                     "the same _execute_target (public.py:139-160) with the bound likelihood "
                     "wrapped by the evaluation counter.")}


# ----------------------------------------------------------------------------
# Instrumentation
# ----------------------------------------------------------------------------
class TimedCompileCounter(bc.CompileCounter):
    """bench_common.CompileCounter plus the seconds spent in compile requests / compiles."""

    def __init__(self):
        super().__init__()
        self.request_seconds = 0.0
        self.compile_seconds = 0.0

    def install(self):
        import jax._src.compiler as comp

        orig_bc = comp.backend_compile
        orig_cgc = comp.compile_or_get_cached
        c = self

        def counting_backend_compile(*a, **k):
            c.compiles += 1
            t0 = time.perf_counter()
            try:
                return orig_bc(*a, **k)
            finally:
                c.compile_seconds += time.perf_counter() - t0

        def counting_compile_or_get_cached(*a, **k):
            c.requests += 1
            t0 = time.perf_counter()
            try:
                return orig_cgc(*a, **k)
            finally:
                c.request_seconds += time.perf_counter() - t0

        comp.backend_compile = counting_backend_compile
        comp.compile_or_get_cached = counting_compile_or_get_cached
        self.installed = True
        return self

    def snapshot(self):
        return (self.requests, self.compiles, self.request_seconds, self.compile_seconds)

    def delta(self, snap):
        return {"requests": self.requests - snap[0], "compiles": self.compiles - snap[1],
                "request_seconds": self.request_seconds - snap[2],
                "compile_seconds": self.compile_seconds - snap[3]}


class CountingLikelihood:
    """Transparent wrapper: counts eager (concrete) and traced calls per phase."""

    EAGER_LOG_CAP = 5000

    def __init__(self, fn):
        self.fn = fn
        self.phase = "init"
        self.counts = {}
        # (t_start, t_end) perf_counter of the first EAGER_LOG_CAP eager calls of the sampling
        # phase (preflight + initial live points); each eager result is block_until_ready'd
        # inside the wrapper so t_end includes the device work (the samplers convert every
        # eager value to a Python float right after the call anyway: values unchanged).
        self.eager_log = []

    def __call__(self, theta):
        import jax

        kind = "traced" if isinstance(theta, jax.core.Tracer) else "eager"
        key = (self.phase, kind)
        self.counts[key] = self.counts.get(key, 0) + 1
        if kind == "traced":
            return self.fn(theta)
        t0 = time.perf_counter()
        out = jax.block_until_ready(self.fn(theta))
        if self.phase == "sampling" and len(self.eager_log) < self.EAGER_LOG_CAP:
            self.eager_log.append((t0, time.perf_counter()))
        return out

    def count(self, phase=None, kind=None):
        return sum(v for (p, k), v in self.counts.items()
                   if (phase is None or p == phase) and (kind is None or k == kind))

    def table(self):
        return {f"{p}:{k}": v for (p, k), v in sorted(self.counts.items())}


def _rss_bytes():
    try:
        with open("/proc/self/statm") as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except Exception:
        return None


class Monitor(threading.Thread):
    """Samples the device allocator (memory_stats) and the host RSS every ``interval`` s."""

    def __init__(self, interval, device=None):
        super().__init__(daemon=True, name="infer-ladder-monitor")
        self.interval = float(interval)
        self.device = device
        self.phase = "init"
        self.rows = []
        self._halt = threading.Event()
        self._lock = threading.Lock()

    def sample(self):
        dev_in_use = dev_peak = None
        if self.device is not None:
            try:
                st = self.device.memory_stats() or {}
                dev_in_use, dev_peak = st.get("bytes_in_use"), st.get("peak_bytes_in_use")
            except Exception:
                pass
        with self._lock:
            self.rows.append((time.time(), self.phase, _rss_bytes(), dev_in_use, dev_peak))

    def run(self):
        while not self._halt.is_set():
            self.sample()
            self._halt.wait(self.interval)

    def stop(self):
        self._halt.set()
        self.join(timeout=10)
        self.sample()

    def summary(self):
        with self._lock:
            rows = list(self.rows)
        out = {"interval_s": self.interval, "n_samples": len(rows), "by_phase": {}}
        for _t, ph, rss, inuse, peak in rows:
            d = out["by_phase"].setdefault(ph, {"n": 0, "host_rss_max_bytes": None,
                                               "device_bytes_in_use_max": None,
                                               "device_peak_bytes_in_use_last": None})
            d["n"] += 1
            if rss is not None:
                d["host_rss_max_bytes"] = max(rss, d["host_rss_max_bytes"] or 0)
            if inuse is not None:
                d["device_bytes_in_use_max"] = max(inuse, d["device_bytes_in_use_max"] or 0)
            if peak is not None:
                d["device_peak_bytes_in_use_last"] = peak
        rss_all = [r[2] for r in rows if r[2] is not None]
        inuse_all = [r[3] for r in rows if r[3] is not None]
        peak_all = [r[4] for r in rows if r[4] is not None]
        out["host_rss_max_bytes"] = max(rss_all) if rss_all else None
        out["device_bytes_in_use_max"] = max(inuse_all) if inuse_all else None
        out["device_peak_bytes_in_use"] = max(peak_all) if peak_all else None
        return out

    def write_csv(self, path):
        with self._lock:
            rows = list(self.rows)
        with open(path, "w") as f:
            f.write("t_unix,phase,host_rss_bytes,device_bytes_in_use,device_peak_bytes_in_use\n")
            for t, ph, rss, inuse, peak in rows:
                f.write(f"{t:.3f},{ph},{'' if rss is None else rss},"
                        f"{'' if inuse is None else inuse},{'' if peak is None else peak}\n")


class SamplerProbe:
    """Progress trace of tinyns / dynesty through their own observation hooks."""

    def __init__(self, nlive, counting, log_every=500, sampler=None, max_evals=0, max_wall_s=0.0):
        self.nlive = int(nlive)
        self.counting = counting
        self.sampler = sampler
        self.max_evals = int(max_evals or 0)
        self.max_wall_s = float(max_wall_s or 0.0)
        self.budget_hit = None
        self.rows = []
        self.t_sampling0 = None
        self.events = {}
        self.log_every = int(log_every)
        self._restore = []
        self.print_progress_seen = None

    def mark(self, name):
        if name not in self.events:
            self.events[name] = {"t_unix": time.time(), "t_perf": time.perf_counter(),
                                 "eager_calls_so_far": self.counting.count("sampling", "eager")}

    def _row(self, phase, iteration, logvol, src, logz, dlogz, ncall, lmin, lmax):
        now = time.perf_counter()
        self.rows.append((len(self.rows), phase, int(iteration), logvol, src, logz, dlogz,
                          None if ncall is None else int(ncall), lmin, lmax,
                          now - self.t_sampling0 if self.t_sampling0 is not None else None,
                          time.time()))
        if len(self.rows) == 1:
            self.mark("first_progress")
        if self.log_every and len(self.rows) % self.log_every == 0:
            print(f"  [ladder] {phase} it={iteration} logz={logz:.4f} dlogz={dlogz:.4g} "
                  f"ncall={ncall} logvol={logvol:.3f}", flush=True)
        self._check_budget(ncall, now)

    def n_evals_now(self, ncall=None):
        """Likelihood evaluations so far, by the definition of likelihood_calls.n_like_evals."""
        if self.sampler == "dynesty":
            return self.counting.count("sampling", "eager")
        pre = (self.events.get("sampler_run_entry") or {}).get("eager_calls_so_far") or 0
        if ncall is None:
            main = [r for r in self.rows if r[7] is not None]
            ncall = main[-1][7] if main else None
        return None if ncall is None else int(pre) + int(ncall)

    def _check_budget(self, ncall, now):
        if self.budget_hit is not None:
            return
        if self.max_evals:
            n = self.n_evals_now(ncall)
            if n is not None and n >= self.max_evals:
                self.budget_hit = {"kind": "evals", "value": n, "limit": self.max_evals,
                                   "source": "progress hook", "row": len(self.rows) - 1}
                raise LadderBudget("evals", n, self.max_evals)
        if self.max_wall_s and self.t_sampling0 is not None:
            w = now - self.t_sampling0
            if w >= self.max_wall_s:
                self.budget_hit = {"kind": "wall", "value": w, "limit": self.max_wall_s,
                                   "source": "progress hook", "row": len(self.rows) - 1}
                raise LadderBudget("wall_s", w, self.max_wall_s)

    # tinyns: NestedSampler.run(..., callback=, callback_interval=) (tinyns/api.py:209-238);
    # the state dict is built every outer iteration regardless (tinyns/run.py:1999-2017).
    def install_tinyns(self):
        import tinyns

        orig = tinyns.NestedSampler
        probe = self

        class ProbedNestedSampler(orig):
            def run(self, key, **kw):
                probe.mark("sampler_run_entry")
                user_cb = kw.pop("callback", None)

                def cb(state):
                    it = int(state["iter"])
                    probe._row("main", it, -it / probe.nlive, "-iter/nlive", float(state["logz"]),
                               float(state["dlogz"]), int(state["ncall"]), float(state["logl_min"]),
                               float(state["logl_live_max"]))
                    return None if user_cb is None else user_cb(state)

                kw["callback"] = cb
                kw["callback_interval"] = 1
                try:
                    return super().run(key, **kw)
                finally:
                    probe.mark("sampler_run_exit")

        tinyns.NestedSampler = ProbedNestedSampler
        self._restore.append(lambda: setattr(tinyns, "NestedSampler", orig))

    # dynesty: run_nested(print_progress=True, print_func=...) (dynesty/sampler.py:920-1062);
    # results is the IteratorResult namedtuple (dynesty/utils.py:41-45).
    def install_dynesty(self):
        import dynesty

        orig = dynesty.NestedSampler
        probe = self

        def factory(*a, **k):
            probe.mark("sampler_construct_entry")
            s = orig(*a, **k)
            probe.mark("sampler_constructed")
            orig_run = s.run_nested

            def run_nested(*ra, **rk):
                probe.mark("sampler_run_entry")
                probe.print_progress_seen = rk.get("print_progress", True)
                if rk.get("print_func") is None:
                    rk["print_func"] = probe.dynesty_print_func
                try:
                    return orig_run(*ra, **rk)
                finally:
                    probe.mark("sampler_run_exit")

            s.run_nested = run_nested
            return s

        dynesty.NestedSampler = factory
        self._restore.append(lambda: setattr(dynesty, "NestedSampler", orig))

    def dynesty_print_func(self, results, niter, ncall, add_live_it=None, dlogz=None, **_kw):
        phase = "main" if add_live_it is None else "add_live"
        it = int(niter) if add_live_it is None else int(niter) + int(add_live_it)
        try:
            logvol = float(results.logvol)
            logz = float(results.logz)
            dl = float(results.delta_logz)
            lmin = float(results.loglstar)
        except AttributeError:  # IteratorResultShort (no integrals)
            logvol = logz = dl = float("nan")
            lmin = float(getattr(results, "loglstar", float("nan")))
        self._row(phase, it, logvol, "dynesty results.logvol", logz, dl, ncall, lmin, float("nan"))

    def restore(self):
        for f in self._restore:
            f()
        self._restore = []

    def write_csv(self, path):
        with open(path, "w") as f:
            f.write(",".join(PROGRESS_COLUMNS) + "\n")
            for row in self.rows:
                f.write(",".join("" if v is None else (repr(v) if isinstance(v, float) else str(v))
                                 for v in row) + "\n")

    def summary(self):
        if not self.rows:
            return {"n_rows": 0}
        main = [r for r in self.rows if r[1] == "main"]
        last = main[-1] if main else self.rows[-1]
        return {"n_rows": len(self.rows), "n_main_rows": len(main),
                "last_main_iteration": last[2], "last_log_volume": last[3],
                "last_logz": last[5], "last_dlogz_remaining": last[6], "last_ncall_cum": last[7],
                "t_first_row_s": self.rows[0][10], "t_last_row_s": self.rows[-1][10]}


def _jsonable(x, depth=0):
    if depth > 8:
        return str(x)
    if x is None or isinstance(x, (bool, int, str)):
        return x
    if isinstance(x, float):
        return bc.fval(x)
    if isinstance(x, np.generic):
        return _jsonable(x.item(), depth + 1)
    if isinstance(x, np.ndarray):
        if x.size > 64:
            return {"shape": list(x.shape), "dtype": str(x.dtype), "note": "array omitted"}
        return [_jsonable(v, depth + 1) for v in x.tolist()]
    if isinstance(x, dict):
        return {str(k): _jsonable(v, depth + 1) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [_jsonable(v, depth + 1) for v in x]
    try:
        import jax

        if isinstance(x, jax.Array):
            return _jsonable(np.asarray(x), depth + 1)
    except Exception:
        pass
    return str(x)


def _kinds_norm(kinds):
    out = []
    for k in kinds:
        k = list(k)
        out.append([str(k[0])] + [None if v is None else float(v) for v in k[1:]])
    return out


def _constraints_norm(cons):
    return [[str(kind), [int(i) for i in idx]] for kind, idx in (cons or ())]


def sampler_backend_fingerprint(name):
    """Version, file, py-blob digest and pip direct_url (commit) of tinyns / dynesty."""
    import importlib

    out = {"name": name}
    try:
        mod = importlib.import_module(name)
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    out["file"] = os.path.abspath(mod.__file__)
    out["version"] = getattr(mod, "__version__", None)
    try:
        digest, n = bc.py_package_digest(os.path.dirname(out["file"]))
        out["py_blob_digest"], out["n_py_files"] = digest, n
    except Exception:
        pass
    try:
        from importlib import metadata

        dist = metadata.distribution(name)
        out["dist_version"] = dist.version
        du = dist.read_text("direct_url.json")
        out["direct_url"] = json.loads(du) if du else None
    except Exception:
        out["direct_url"] = None
    root = bc._git(["rev-parse", "--show-toplevel"], os.path.dirname(out["file"]))
    if root:
        out["git_sha"] = bc._git(["rev-parse", "HEAD"], os.path.dirname(out["file"]))
        out["git_dirty_tracked"] = bool(bc._git(["status", "--porcelain", "--untracked-files=no"],
                                                os.path.dirname(out["file"])))
    return out


class Tee:
    def __init__(self, stream, fh):
        self.stream, self.fh = stream, fh

    def write(self, s):
        self.stream.write(s)
        self.fh.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()
        self.fh.flush()

    def isatty(self):
        return False

    def fileno(self):
        return self.stream.fileno()


# ----------------------------------------------------------------------------
# Implementation drivers
# ----------------------------------------------------------------------------
class LegacyRun:
    impl = "legacy"

    def __init__(self, rung, settings, pe, sel, out_dir):
        self.rung, self.s = rung, settings
        self.save_path = os.path.join(out_dir, "legacy_run")
        self.argv = legacy_argv(rung, pe, sel, self.save_path, settings)
        self.timing = {}

    def import_package(self):
        import darksirens
        from darksirens.cli import inference as cli  # noqa: F401  (configure_jax_runtime at import)

        if not hasattr(cli, "_run_sampling"):
            raise RuntimeError("imported darksirens has no legacy CLI sampling phase")
        return darksirens

    def build(self, counter):
        from darksirens.cli import inference as cli
        from darksirens.gw.populations.utils import normalization_grid_settings

        os.makedirs(self.save_path, exist_ok=True)
        t0 = time.perf_counter()
        optp = cli.build_parser()
        opts = optp.parse_args(self.argv)
        cli._normalize_multitracer_paths(opts)
        cli._check_latent_field_mode(opts)
        cli._stamp_latent_artifact_fingerprint(opts)
        cli._resolve_catalog_sky_weighting(opts)
        cli._validate_multitracer_config(opts)
        cli._canonicalize_fixed_flags(opts)
        cli._configure_performance_grids(opts)
        prior_overrides, fixed = cli._parse_structured_options(opts)
        cli._resolve_sampler_config(opts)
        cli._apply_bright_siren_overrides(opts)
        cli._print_all_cli_options(optp, opts,
                                   normalization_grid=normalization_grid_settings().to_dict())
        cli._validate_run_config(opts)
        cli._print_run_configuration(opts, prior_overrides, fixed)
        t1 = time.perf_counter()
        data = cli._load_and_report_data(opts)
        t2 = time.perf_counter()
        if cli._maybe_run_completion_validation(opts, data, prior_overrides, fixed):
            raise RuntimeError("legacy completion-validation mode returned early")
        cli._resolve_single_catalog_marks(opts, data)
        pspace = cli._build_and_report_parameter_space(opts, data, prior_overrides, fixed)
        t3 = time.perf_counter()
        run_dir, _ts, snap = cli._prepare_run_dir(opts, data, pspace, fixed, prior_overrides)
        t4 = time.perf_counter()
        likelihood = cli._build_likelihood(opts, data, pspace, fixed)
        t5 = time.perf_counter()
        self.timing.update(t_config_s=t1 - t0, t_load_s=t2 - t1, t_parameter_space_s=t3 - t2,
                           t_run_dir_s=t4 - t3, t_build_likelihood_s=t5 - t4,
                           t_build_s=(t3 - t2) + (t5 - t4))
        self.cli, self.opts, self.data, self.pspace = cli, opts, data, pspace
        self.fixed, self.prior_overrides = dict(fixed), dict(prior_overrides or {})
        self.likelihood, self.run_dir, self.run_dir_snapshot = likelihood, run_dir, snap
        self.labels = [str(x) for x in pspace.labels]
        self.lower = [float(x) for x in pspace.lower_bound]
        self.upper = [float(x) for x in pspace.upper_bound]
        self.prior_kinds = _kinds_norm(pspace.prior_kinds)
        self.joint_constraints = _constraints_norm(getattr(pspace, "joint_constraints", ()))
        from darksirens.inference.parameters import build_parameter_decoder

        self.decoder = build_parameter_decoder(opts, pspace.pop_params_fid,
                                               fixed_parameter_values=self.fixed,
                                               wl_params=data.get("wl_params"))

    def decode(self, coord):
        import jax.numpy as jnp

        cosmo, _survey, pop, _sky, _marks = self.decoder.decode(jnp.asarray(coord))
        return ([float(np.asarray(getattr(cosmo, n))) for n in ("H0", "Om0", "w0", "wa")]
                + [float(x) for x in np.asarray(pop, dtype=np.float64)])

    def fixed_population_check(self):
        return None  # covered by the decoded vector at the centre

    def sampler_likelihood(self):
        return self.likelihood

    def run_sampler(self, likelihood):
        results, wall = self.cli._run_sampling(self.opts, likelihood, self.pspace)
        return results, {"legacy_wall_sampling": str(wall)}

    def resolved_settings(self):
        o = self.opts
        from darksirens.inference.checkpointing import plan_from_opts

        keys = ("sampler", "nlive", "dlogz", "seed", "max_samples", "show_progress",
                "sampler_preflight", "prior_transform_dispatch", "dynesty_diagnostics",
                "tinyns_preset", "tinyns_resolved_config", "checkpoint_interval",
                "checkpoint_interval_seconds", "checkpoint_file_resolved", "resume",
                "resume_from_resolved", "sel_batch_size", "pe_event_block",
                "selection_neff_guard", "selection_neff_soft_guard", "max_likelihood_variance",
                "redshift_prior_barrier", "redshift_prior_barrier_resolved",
                "materialize_redshift_prior_state", "norm_nmass", "norm_nq", "norm_nchi",
                "pairing_norm_grid", "fix_cosmology", "fix_de", "fix_population",
                "population_fiducials", "prior_overrides", "fixed_parameter_values",
                "universe_model", "pop_model", "run_fingerprint_digest")
        out = {k: _jsonable(getattr(o, k)) for k in keys if hasattr(o, k)}
        try:
            out["checkpoint_plan"] = plan_from_opts(o, o.sampler).summary()
        except Exception as exc:
            out["checkpoint_plan"] = f"error: {exc}"
        from darksirens.gw.populations.utils import normalization_grid_settings

        out["normalization_grid"] = _jsonable(normalization_grid_settings().to_dict())
        out["run_dir"] = self.run_dir
        return out

    def invocation(self):
        return {"kind": "legacy darksirens_inference CLI phase functions (main() order, "
                        "_save_outputs not run)", "argv": self.argv}


class CoreRun:
    impl = "core"

    def __init__(self, rung, settings, pe, sel, out_dir):
        self.rung, self.s = rung, settings
        self.pe, self.sel = pe, sel
        self.timing = {}
        self.expression = core_expression(rung, settings)

    def import_package(self):
        import darksirens as ds

        ds.configure_jax_runtime()
        try:
            import darksirens.cli  # noqa: F401
        except ImportError:
            pass
        else:
            raise RuntimeError("imported darksirens has a cli package: legacy tree, not core")
        return ds

    def build(self, counter):
        import jax.numpy as jnp

        import darksirens as ds
        from darksirens.inference import public as dspub
        from darksirens.runtime_binding import bind_analysis

        r, s = self.rung, self.s
        t0 = time.perf_counter()
        h0 = tuple(r["H0_bounds"]) if r["sample_H0"] else r["H0_fiducial"]
        fc = r["fixed_cosmology"]
        cosmology = ds.Cosmology(H0=h0, Om0=fc["Om0"], w0=fc["w0"], wa=fc["wa"])
        population = ds.Population(r["population_model"], fixed=r["core_population_fixed"])
        analysis = ds.model(cosmology=cosmology, population=population)
        t1 = time.perf_counter()
        events = ds.load_events(self.pe)
        injections = ds.load_injections(self.sel)
        t2 = time.perf_counter()
        self.soft = bool(dspub._resolve_selection_neff_soft_guard(s["guard"], s["sampler"]))
        bound = bind_analysis(
            analysis, events=events, injections=injections,
            selection_neff_soft_guard=self.soft,
            max_likelihood_variance=float(s["max_likelihood_variance"]),
            sel_batch_size=None if s["sel_batch_size"] == "none" else int(s["sel_batch_size"]),
            pe_event_block=None if s["pe_event_block"] == "none" else int(s["pe_event_block"]))
        t3 = time.perf_counter()
        plan = analysis.parameters
        full_labels = [str(x) for x in plan.labels]
        sampled = list(r["sampled"])
        self.embedding = None
        if full_labels == sampled:
            self.likelihood_fn = bound
            self.plan = plan
        else:
            missing = [n for n in sampled if n not in full_labels]
            if missing:
                raise RuntimeError(f"rung samples {missing}, absent from core's plan {full_labels}")
            idx = [full_labels.index(n) for n in sampled]
            base = np.asarray([r["fixed"].get(n, np.nan) for n in full_labels], dtype=np.float64)
            base_j, idx_j = jnp.asarray(base), jnp.asarray(np.asarray(idx, dtype=np.int32))

            def embedded(theta, _b=bound, _base=base_j, _idx=idx_j):
                return _b(_base.at[_idx].set(jnp.asarray(theta)))

            keep, dropped = [], []
            for kind, ids in plan.joint_constraints:
                ids = tuple(int(i) for i in ids)
                if all(i in idx for i in ids):
                    keep.append((str(kind), tuple(idx.index(i) for i in ids)))
                else:  # legacy's rule: skip a group with any non-sampled member
                    dropped.append([str(kind), [full_labels[i] for i in ids]])
            self.plan = ds.ParameterPlan(
                labels=tuple(sampled),
                lower=tuple(float(plan.lower[i]) for i in idx),
                upper=tuple(float(plan.upper[i]) for i in idx),
                prior_kinds=tuple(tuple(plan.prior_kinds[i]) for i in idx),
                joint_constraints=tuple(keep))
            self.likelihood_fn = embedded
            self.embedding = {
                "kind": "InferenceTarget over core's full plan with the non-sampled parameters "
                        "inserted (base.at[idx].set(theta))",
                "reason": "ds.Population is either fully sampled or fully fixed "
                          "(src/darksirens/analysis.py:288-308); no public partial fixing",
                "core_full_plan_labels": full_labels,
                "sampled_indices_in_core_plan": idx,
                "fixed_inserted": {n: float(base[i]) for i, n in enumerate(full_labels)
                                   if n not in sampled},
                "dropped_joint_constraints": dropped,
            }
        self.ds, self.dspub, self.analysis, self.bound = ds, dspub, analysis, bound
        self.events, self.injections = events, injections
        self.full_labels = full_labels
        self.labels = [str(x) for x in self.plan.labels]
        self.lower = [float(x) for x in self.plan.lower]
        self.upper = [float(x) for x in self.plan.upper]
        self.prior_kinds = _kinds_norm(self.plan.prior_kinds)
        self.joint_constraints = _constraints_norm(self.plan.joint_constraints)
        self.timing.update(t_config_s=t1 - t0, t_load_s=t2 - t1, t_build_s=t3 - t2)

    def decode(self, coord):
        import jax.numpy as jnp

        from darksirens.runtime_binding import _decode_theta

        theta = jnp.asarray(coord, dtype=jnp.float64)
        if self.embedding is not None:
            base = np.asarray([self.rung["fixed"].get(n, np.nan) for n in self.full_labels])
            base[self.embedding["sampled_indices_in_core_plan"]] = np.asarray(coord)
            theta = jnp.asarray(base)
        cosmo, pop, _cat, _ang = _decode_theta(self.analysis, theta, z_depth=None)
        return ([float(np.asarray(getattr(cosmo, n))) for n in ("H0", "Om0", "w0", "wa")]
                + [float(x) for x in np.asarray(pop, dtype=np.float64)])

    def fixed_population_check(self):
        fp = self.analysis.parameters.fixed_population
        return None if fp is None else [float(x) for x in fp]

    def sampler_likelihood(self):
        return self.likelihood_fn

    def _sampler_options(self):
        s = self.s
        return dict(nlive=int(s["nlive"]), dlogz=float(s["dlogz"]), seed=int(s["seed"]),
                    max_samples=int(s["max_samples"]), show_progress=True,
                    sampler_preflight=s["sampler_preflight"],
                    prior_transform_dispatch=s["prior_transform_dispatch"],
                    tinyns_preset=s["tinyns_preset"], dynesty_diagnostics=False,
                    checkpoint_interval_seconds=0.0, checkpoint_file_resolved=None,
                    resume_from_resolved=None)

    def run_sampler(self, likelihood):
        target = self.ds.InferenceTarget(log_likelihood=likelihood, parameters=self.plan)
        result = self.ds.infer(target, sampler=self.s["sampler"], **self._sampler_options())
        # ordinary ds.infer applies this after _execute_target (public.py:189)
        result = self.dspub._apply_angular_prior_volume_correction(result, self.analysis)
        return result, {}

    def resolved_settings(self):
        ns = self.dspub._sampler_namespace(self.s["sampler"], self._sampler_options())
        out = {}
        if self.s["sampler"] == "tinyns":
            from darksirens.inference.tinyns_config import build_tinyns_config

            build_tinyns_config(ns)
        from darksirens.inference.checkpointing import plan_from_opts
        from darksirens.population.utils import normalization_grid_settings

        out.update({k: _jsonable(v) for k, v in vars(ns).items()})
        out["checkpoint_plan"] = plan_from_opts(ns, self.s["sampler"]).summary()
        out["selection_neff_guard"] = self.s["guard"]
        out["selection_neff_soft_guard"] = self.soft
        out["max_likelihood_variance"] = float(self.bound.max_likelihood_variance)
        out["sel_batch_size"] = self.bound.sel_batch_size
        out["pe_event_block"] = self.bound.pe_event_block
        out["normalization_grid"] = _jsonable(normalization_grid_settings().to_dict())
        out["core_expression"] = self.expression
        out["embedding"] = self.embedding
        return out

    def invocation(self):
        return {"kind": "core public API (ds.model / ds.load_* / bind_analysis / "
                        "ds.infer(InferenceTarget))", **self.expression}


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--impl", required=True, choices=("legacy", "core"))
    ap.add_argument("--rung", required=True)
    ap.add_argument("--sampler", required=True, choices=("tinyns", "dynesty"))
    ap.add_argument("--pe", required=True)
    ap.add_argument("--sel", required=True)
    ap.add_argument("--nlive", type=int, required=True)
    ap.add_argument("--dlogz", type=float, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True, help="output directory (created; must not hold a record)")
    ap.add_argument("--device", choices=("gpu", "cpu", "auto"), default="auto")
    ap.add_argument("--guard", choices=("soft", "hard", "auto"), default="soft")
    ap.add_argument("--max-variance", type=float, default=1.0)
    ap.add_argument("--max-samples", type=int, default=0,
                    help="0 = unlimited in both codes (dlogz is the only stopping rule)")
    ap.add_argument("--tinyns-preset", default="recommended")
    ap.add_argument("--sel-batch", type=_block, default="none")
    ap.add_argument("--pe-block", type=_block, default="none")
    ap.add_argument("--sampler-preflight", choices=("on", "off"), default="on")
    ap.add_argument("--rungs-file", default=RUNGS_FILE)
    ap.add_argument("--label", default=None)
    ap.add_argument("--arm", default=None,
                    help="free-text arm name stored in the record (e.g. an experimental branch)")
    ap.add_argument("--parity-ref", action="append", default=[],
                    help="fixed-coordinate parity record id(s) this run relies on (repeatable; stored)")
    ap.add_argument("--policy-note", default=None, help="free text stored in the record (run policy / decision)")
    ap.add_argument("--max-evals", type=int, default=0,
                    help="stop sampling (status budget-capped, exit 7) once n_like_evals >= N (0 = none)")
    ap.add_argument("--max-wall-s", type=float, default=0.0,
                    help="stop sampling (status budget-capped, exit 7) after S seconds of sampling (0 = none)")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--cache-mode", choices=("cold", "warm", "env"), default="env")
    ap.add_argument("--smi-log", default=None)
    ap.add_argument("--mem-poll-s", type=float, default=1.0)
    ap.add_argument("--progress-log-every", type=int, default=500)
    ap.add_argument("--describe", action="store_true",
                    help="build, assert the plan and make the first call; do not sample")
    return ap.parse_args(argv)


def _dir_inventory(path):
    n = b = 0
    if path and os.path.isdir(path):
        for root, _d, files in os.walk(path):
            for fn in files:
                n += 1
                try:
                    b += os.path.getsize(os.path.join(root, fn))
                except OSError:
                    pass
    return n, b


def _sanitize_name(label):
    s = re.sub(r"[^0-9A-Za-z]+", "_", label).strip("_")
    return s or "p"


def eager_phases(lk, probe, sampler):
    """Preflight and initial-live-point phases from the eager-call log (seconds relative to the
    start of sampling). tinyns: initial live points = eager calls after NestedSampler.run entry
    and before the first progress row (tinyns/run.py:65-75 evaluates them in a Python loop when
    the likelihood is not vectorized); dynesty: eager calls inside the NestedSampler constructor."""
    ev = probe.events
    t0 = probe.t_sampling0
    log = lk.eager_log
    if sampler == "tinyns":
        a_key, b_key = "sampler_run_entry", "first_progress"
    else:
        a_key, b_key = "sampler_construct_entry", "sampler_constructed"
    ta = (ev.get(a_key) or {}).get("t_perf")
    tb = (ev.get(b_key) or {}).get("t_perf")
    out = {"source": f"eager calls between events {a_key} and {b_key}", "eager_log_len": len(log),
           "eager_log_cap": lk.EAGER_LOG_CAP}
    if ta is None:
        return out
    pre = [c for c in log if c[1] <= ta]
    ini = [c for c in log if c[0] >= ta and (tb is None or c[1] <= tb)]
    if pre:
        out["preflight"] = {"n_eager_calls": len(pre), "t_start_s": pre[0][0] - t0, "t_end_s": pre[-1][1] - t0,
                            "seconds": pre[-1][1] - pre[0][0], "sum_call_s": sum(b - a for a, b in pre)}
    if ini:
        tot = sum(b - a for a, b in ini)
        out["initial_live_points"] = {"n_eager_calls": len(ini), "t_start_s": ini[0][0] - t0,
                                      "t_end_s": ini[-1][1] - t0, "seconds": ini[-1][1] - ini[0][0],
                                      "sum_call_s": tot, "mean_s_per_call": tot / len(ini),
                                      "log_truncated": len(log) >= lk.EAGER_LOG_CAP}
    return out


def main(argv=None):
    a = parse_args(argv)
    command_line = [sys.executable] + list(sys.argv if argv is None else ["infer_ladder.py"] + argv)
    started = bc.utc_now()
    t_start = time.perf_counter()
    if a.device == "cpu":
        cur = os.environ.get("JAX_PLATFORMS")
        if cur and cur != "cpu":
            print(f"--device cpu but JAX_PLATFORMS={cur}", file=sys.stderr)
            return 2
        os.environ["JAX_PLATFORMS"] = "cpu"
    try:
        rung = resolve_rung(str(a.rung), load_rungs(a.rungs_file))
    except (KeyError, ValueError) as exc:
        print(f"rung: {exc}", file=sys.stderr)
        return 2
    for f in (a.pe, a.sel):
        if not os.path.isfile(f):
            print(f"missing input {f}", file=sys.stderr)
            return 2
    out = os.path.abspath(a.out)
    if os.path.exists(os.path.join(out, "record.json")):
        print(f"{out} already holds a record.json", file=sys.stderr)
        return 2
    os.makedirs(out, exist_ok=True)
    settings = {
        "sampler": a.sampler, "nlive": int(a.nlive), "dlogz": float(a.dlogz), "seed": int(a.seed),
        "max_samples": int(a.max_samples), "tinyns_preset": a.tinyns_preset,
        "sampler_preflight": a.sampler_preflight, "prior_transform_dispatch": "auto",
        "show_progress": True, "checkpointing": "off", "dynesty_diagnostics": False,
        "sel_batch_size": a.sel_batch, "pe_event_block": a.pe_block,
        "guard": a.guard, "max_likelihood_variance": float(a.max_variance),
    }

    # ---- XLA persistent cache policy (before jax import) ---------------------------
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
            print(f"--cache-mode warm but {cdir} is empty", file=sys.stderr)
            return 2
        os.makedirs(cdir, exist_ok=True)
        os.environ["JAX_COMPILATION_CACHE_DIR"] = cdir
        cache_info.update(dir=cdir, files_before=n0, bytes_before=b0)
    else:
        cdir = os.environ.get("JAX_COMPILATION_CACHE_DIR")
        n0, b0 = _dir_inventory(cdir)
        cache_info.update(dir=cdir, files_before=n0, bytes_before=b0)

    log_fh = open(os.path.join(out, "run.log"), "w")
    sys.stdout = Tee(sys.__stdout__, log_fh)
    sys.stderr = Tee(sys.__stderr__, log_fh)

    clock = bc.PhaseClock()
    clock.mark("start")
    t0 = time.perf_counter()
    import jax

    counter = TimedCompileCounter().install()
    t_import_jax = time.perf_counter() - t0
    run = (LegacyRun if a.impl == "legacy" else CoreRun)(rung, settings, os.path.abspath(a.pe),
                                                         os.path.abspath(a.sel), out)
    t0 = time.perf_counter()
    pkg = run.import_package()
    t_import_pkg = time.perf_counter() - t0
    t0 = time.perf_counter()
    devs = jax.devices()
    t_backend = time.perf_counter() - t0
    device = bc.device_fingerprint(a.device)
    if a.device in ("gpu", "cpu") and device["backend"] != a.device:
        print(f"--device {a.device} but JAX backend is {device['backend']}", file=sys.stderr)
        return 2
    if not device["x64"]:
        print("jax_enable_x64 is off after the implementation configured JAX", file=sys.stderr)
        return 2
    monitor = Monitor(a.mem_poll_s, devs[0] if device["backend"] == "gpu" else None)
    monitor.start()

    record = {
        "schema": SCHEMA,
        "status": "running",
        "label": a.label or f"{a.impl}_r{a.rung}_{a.sampler}",
        "implementation": a.impl,
        "arm": a.arm,
        "fixed_coordinate_parity_refs": list(a.parity_ref),
        "policy_note": a.policy_note,
        "budget": {"max_evals": int(a.max_evals) or None, "max_wall_s_sampling": float(a.max_wall_s) or None,
                   "rule": ("stop at the first of: sampler convergence (dlogz), n_like_evals >= max_evals, "
                            "sampling wall >= max_wall_s; checked after each progress row (tinyns: per "
                            "JAX block; dynesty: per iteration) and by SIGALRM for the wall"),
                   "stop_reason": None},
        "command_line": command_line,
        "cwd": os.getcwd(),
        "started_utc": started,
        "harness": {"dir": HERE, "git": bc.package_fingerprint(type("M", (), {
            "__name__": "benchmarks.a100", "__file__": os.path.join(HERE, "plans.py")}))},
        "package": bc.package_fingerprint(pkg),
        "sampler_backends": {"tinyns": sampler_backend_fingerprint("tinyns"),
                             "dynesty": sampler_backend_fingerprint("dynesty")},
        "env": bc.env_fingerprint(),
        "device": device,
        "inputs": {"pe": bc.gwcat_file_info(a.pe), "sel": bc.gwcat_file_info(a.sel)},
        "rung": rung,
        "settings": {"requested": settings},
        "gaps": [],
    }
    record["harness"]["git"].pop("known_digest_match", None)
    record["invocation"] = run.invocation()
    mem = [bc.memory_checkpoint("after_import")]
    rec_path = os.path.join(out, "record.json")

    def finish(status, code):
        monitor.stop()
        monitor.write_csv(os.path.join(out, "memory.csv"))
        record["memory"] = {"checkpoints": mem, "monitor": monitor.summary(),
                            "peak_host_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024,
                            "memory_csv": os.path.join(out, "memory.csv")}
        cache_after = _dir_inventory(cache_info.get("dir"))
        cache_info.update(files_after=cache_after[0], bytes_after=cache_after[1])
        record["xla_cache"] = cache_info
        record["timing"]["t_total_s"] = time.perf_counter() - t_start
        record["timing"]["phase_clock"] = clock.stamps
        record["status"] = status
        record["finished_utc"] = bc.utc_now()
        bc.write_json(rec_path, record)
        sys.stdout.flush()
        print(f"[ladder] {record['label']}: status={status} record={rec_path}", flush=True)
        return code

    record["timing"] = {"t_import_jax_s": t_import_jax, "t_import_package_s": t_import_pkg,
                        "t_backend_init_s": t_backend}
    # ---- config + load + build --------------------------------------------------------
    clock.mark("build_start")
    monitor.phase = "build"
    snap = counter.snapshot()
    try:
        run.build(counter)
    except BaseException as exc:  # noqa: BLE001 - SystemExit from legacy _fatal included
        record["build_error"] = {"type": type(exc).__name__, "message": str(exc),
                                 "traceback_tail": traceback.format_exc()[-4000:],
                                 "stage_timing": dict(run.timing)}
        record["compile"] = {"build": counter.delta(snap)}
        return finish("build_error", 4)
    record["compile"] = {"build": counter.delta(snap)}
    clock.mark("build_end")
    mem.append(bc.memory_checkpoint("after_build"))
    record["timing"].update(run.timing)
    record["settings"]["resolved"] = run.resolved_settings()
    record["dims"] = {"n_events": int(record["inputs"]["pe"]["attrs"].get("nobs") or 0) or None,
                      "nsamp": record["inputs"]["pe"]["attrs"].get("nsamp"),
                      "ndraw": record["inputs"]["sel"]["attrs"].get("ndraw"),
                      "n_detected": record["inputs"]["sel"]["attrs"].get("n_detected"),
                      "ndim": len(run.labels)}

    # ---- plan assertions -------------------------------------------------------------
    errs = []
    impl_plan = {"labels": run.labels, "lower_hex": [bc.fhex(x) for x in run.lower],
                 "upper_hex": [bc.fhex(x) for x in run.upper], "prior_kinds": run.prior_kinds,
                 "joint_constraints": run.joint_constraints}
    if run.labels != rung["sampled"]:
        errs.append(f"labels {run.labels} != rung sampled {rung['sampled']}")
    else:
        if impl_plan["lower_hex"] != [bc.fhex(x) for x in rung["sampled_lower"]]:
            errs.append(f"lower bounds {run.lower} != {rung['sampled_lower']}")
        if impl_plan["upper_hex"] != [bc.fhex(x) for x in rung["sampled_upper"]]:
            errs.append(f"upper bounds {run.upper} != {rung['sampled_upper']}")
        if run.prior_kinds != _kinds_norm(rung["sampled_prior_kinds"]):
            errs.append(f"prior kinds {run.prior_kinds} != {rung['sampled_prior_kinds']}")
        if run.joint_constraints != rung["expected_joint_constraints"]:
            errs.append(f"joint constraints {run.joint_constraints} != "
                        f"{rung['expected_joint_constraints']}")
    centre = np.asarray(rung["centre"], dtype=np.float64)
    decoded = None
    try:
        decoded = run.decode(centre)
        if [bc.fhex(x) for x in decoded] != [bc.fhex(x) for x in rung["expected_full_at_centre"]]:
            errs.append(f"decoded centre {decoded} != expected {rung['expected_full_at_centre']}")
    except Exception as exc:  # noqa: BLE001
        errs.append(f"decode failed: {type(exc).__name__}: {exc}")
    fixed_pop = run.fixed_population_check()
    if fixed_pop is not None:
        exp = [rung["fixed"][lab] for lab in rung["population_labels"]]
        if [bc.fhex(x) for x in fixed_pop] != [bc.fhex(x) for x in exp]:
            errs.append("core fixed_population != the rung's fixed population values")
    record["plan"] = {"implementation_view": impl_plan,
                      "decoded_full_at_centre_hex": None if decoded is None else [bc.fhex(x) for x in decoded],
                      "core_fixed_population_hex": None if fixed_pop is None else [bc.fhex(x) for x in fixed_pop],
                      "assertions": {"ok": not errs, "errors": errs}}
    if errs:
        print("PLAN MISMATCH:\n  " + "\n  ".join(errs), file=sys.stderr)
        return finish("plan_mismatch", 3)

    # ---- first likelihood call (compile + run) at the rung centre -----------------------
    lk = CountingLikelihood(run.sampler_likelihood())
    lk.phase = "first_call"
    monitor.phase = "first_call"
    clock.mark("first_call_start")
    snap = counter.snapshot()
    t0 = time.perf_counter()
    v = lk(jax.numpy.asarray(centre))
    v = jax.block_until_ready(v)
    t_first = time.perf_counter() - t0
    record["compile"]["first_call"] = counter.delta(snap)
    record["timing"]["t_first_call_s"] = t_first
    v = float(np.asarray(v))
    record["first_call"] = {"coordinate_hex": [bc.fhex(x) for x in centre],
                            "coordinate": [float(x) for x in centre],
                            "logL": bc.fval(v), "logL_hex": bc.fhex(v), "finite": math.isfinite(v)}
    clock.mark("first_call_end")
    mem.append(bc.memory_checkpoint("after_first_call"))
    if a.describe:
        record["timing"]["t_sampling_s"] = None
        return finish("described", 0)

    # ---- sampling -------------------------------------------------------------------
    probe = SamplerProbe(a.nlive, lk, log_every=a.progress_log_every, sampler=a.sampler,
                         max_evals=a.max_evals, max_wall_s=a.max_wall_s)
    if a.sampler == "tinyns":
        probe.install_tinyns()
    else:
        probe.install_dynesty()
    lk.phase = "sampling"
    monitor.phase = "sampling"
    clock.mark("sampling_start")
    snap = counter.snapshot()
    probe.t_sampling0 = time.perf_counter()
    t_s0_unix = time.time()
    sampler_error = None
    result, extra = None, {}

    def _on_sigterm(signum, frame):
        raise LadderTimeout(f"signal {signum} during sampling (external timeout)")

    def _on_alarm(signum, frame):
        if probe.budget_hit is None:
            w = time.perf_counter() - probe.t_sampling0
            probe.budget_hit = {"kind": "wall", "value": w, "limit": float(a.max_wall_s),
                                "source": "SIGALRM", "row": len(probe.rows) - 1}
            raise LadderBudget("wall_s", w, float(a.max_wall_s))

    prev_term = signal.signal(signal.SIGTERM, _on_sigterm)
    prev_alrm = signal.signal(signal.SIGALRM, _on_alarm) if a.max_wall_s else None
    if a.max_wall_s:
        signal.setitimer(signal.ITIMER_REAL, float(a.max_wall_s))
    try:
        result, extra = run.run_sampler(lk)
    except BaseException as exc:  # noqa: BLE001 - legacy _fatal raises SystemExit
        sampler_error = {"type": type(exc).__name__, "message": str(exc)[:4000],
                         "traceback_tail": traceback.format_exc()[-4000:],
                         "preflight_abort": "preflight" in str(exc).lower(),
                         "timeout": isinstance(exc, LadderTimeout),
                         "budget": isinstance(exc, LadderBudget)}
    finally:
        if a.max_wall_s:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
            signal.signal(signal.SIGALRM, prev_alrm)
        signal.signal(signal.SIGTERM, prev_term)
    t_sampling = time.perf_counter() - probe.t_sampling0
    t_s1_unix = time.time()
    probe.restore()
    clock.mark("sampling_end")
    monitor.phase = "post"
    record["compile"]["sampling"] = counter.delta(snap)
    mem.append(bc.memory_checkpoint("after_sampling"))
    probe.write_csv(os.path.join(out, "progress.csv"))
    ev = {k: v["t_perf"] - probe.t_sampling0 for k, v in probe.events.items()}
    record["timing"].update(t_sampling_s=t_sampling, sampling_events_s=ev)
    try:
        record["timing"]["sampling_eager_phases"] = eager_phases(lk, probe, a.sampler)
    except Exception as exc:  # noqa: BLE001 - observation only
        record["timing"]["sampling_eager_phases"] = {"error": f"{type(exc).__name__}: {exc}"}
    record["progress"] = {"csv": os.path.join(out, "progress.csv"), "columns": list(PROGRESS_COLUMNS),
                          **probe.summary(),
                          "log_volume_note": ("tinyns: expected static-NS log X = -iteration/nlive; "
                                              "dynesty: its own results.logvol"),
                          "hook": ("tinyns NestedSampler.run(callback=, callback_interval=1)"
                                   if a.sampler == "tinyns" else
                                   "dynesty run_nested(print_func=) per iteration"),
                          "dynesty_print_progress": probe.print_progress_seen}
    # eager calls made before the sampler proper starts = the nested-sampler preflight
    # (dynesty evaluates its initial live points inside its constructor, tinyns inside run)
    pre_key = "sampler_run_entry" if a.sampler == "tinyns" else "sampler_construct_entry"
    pre_eager = probe.events.get(pre_key, {})
    record["likelihood_calls"] = {"by_phase_kind": lk.table(),
                                  "preflight_eager_calls": pre_eager.get("eager_calls_so_far")}
    if a.smi_log:
        record["timing"]["gpu_util_sampling"] = bc.smi_window_stats(a.smi_log, t_s0_unix, t_s1_unix)
    if sampler_error is not None:
        record["sampler_error"] = sampler_error
        record["result"] = None
        # throughput of the partial run (same definitions as an ok run)
        n_part = probe.n_evals_now()
        mrows = [r for r in probe.rows if r[1] == "main"]
        st_p = {}
        if len(mrows) >= 2 and mrows[-1][10] - mrows[0][10] > 0:
            r0, r1 = mrows[0], mrows[-1]
            dt = r1[10] - r0[10]
            st_p = {"window": [r0[2], r1[2]], "seconds": dt, "iterations_per_s": (r1[2] - r0[2]) / dt,
                    "evals_per_s": (None if r0[7] is None or r1[7] is None else (r1[7] - r0[7]) / dt),
                    "log_volume_per_s": (None if not (math.isfinite(r0[3]) and math.isfinite(r1[3]))
                                         else (r0[3] - r1[3]) / dt),
                    "note": "between the first and the last main-loop progress rows (partial run)"}
        record["progress"]["steady_state"] = st_p
        record["likelihood_calls"].update(
            n_like_evals=n_part,
            n_like_evals_source=("partial run up to the stop: " +
                                 ("every eager call during sampling" if a.sampler == "dynesty" else
                                  "preflight eager calls + tinyns ncall at the last progress row")),
            evals_per_s_sampling=(None if not n_part else n_part / t_sampling),
            evals_per_s_steady=st_p.get("evals_per_s"))
        if sampler_error["budget"]:
            record["budget"]["stop_reason"] = f"budget: {probe.budget_hit}"
            record["budget"]["hit"] = probe.budget_hit
            return finish("budget-capped", 7)
        if sampler_error["timeout"]:
            record["budget"]["stop_reason"] = "SIGTERM (external timeout / stop)"
            return finish("timeout", 6)
        record["budget"]["stop_reason"] = ("preflight abort" if sampler_error["preflight_abort"]
                                           else "sampler error")
        return finish("sampler_error", 5)

    # ---- result ---------------------------------------------------------------------
    clock.mark("post_start")
    t0 = time.perf_counter()
    samples = np.asarray(result.get("samples"), dtype=np.float64)
    dead = result.get("dead_points") or {}
    logz, logzerr = result.get("logZ"), result.get("logZerr")
    tdiag = _jsonable(result.get("tinyns_runtime_diagnostics")) if a.sampler == "tinyns" else None
    tsum = _jsonable(result.get("tinyns_summary")) if a.sampler == "tinyns" else None
    tdg = _jsonable(result.get("tinyns_diagnostics")) if a.sampler == "tinyns" else None
    sampler_ncall = None
    if a.sampler == "tinyns":
        for src in (tdiag, tdg, tsum):
            if isinstance(src, dict) and src.get("ncall") is not None:
                sampler_ncall = int(src["ncall"])
                break
    n_pre = int(record["likelihood_calls"]["preflight_eager_calls"] or 0)
    if a.sampler == "dynesty":
        n_evals = lk.count("sampling", "eager")
        n_src = "every eager call of the wrapped likelihood during sampling (preflight included)"
    else:
        n_evals = None if sampler_ncall is None else n_pre + sampler_ncall
        n_src = "preflight eager calls + tinyns result ncall (initial live points + replacement proposals)"
    wl = np.asarray(dead.get("logwt", []), dtype=np.float64)
    ess = None
    if wl.size:
        m = np.max(wl[np.isfinite(wl)]) if np.isfinite(wl).any() else None
        if m is not None:
            w = np.exp(wl - m)
            ess = float(w.sum() ** 2 / np.sum(w * w))
    t_main = None
    steady = {}
    main_rows = [r for r in probe.rows if r[1] == "main"]
    if "first_progress" in ev and probe.rows:
        t_main = probe.rows[-1][10] - ev["first_progress"]
    if len(main_rows) >= 2:
        r0, r1 = main_rows[0], main_rows[-1]
        dt = r1[10] - r0[10]
        if dt > 0:
            steady = {"window": [r0[2], r1[2]], "seconds": dt,
                      "iterations_per_s": (r1[2] - r0[2]) / dt,
                      "evals_per_s": (None if r0[7] is None or r1[7] is None else (r1[7] - r0[7]) / dt),
                      "log_volume_per_s": (None if not (math.isfinite(r0[3]) and math.isfinite(r1[3]))
                                           else (r0[3] - r1[3]) / dt),
                      "note": "between the first and the last main-loop progress rows "
                              "(excludes preflight, initial live points and the first compile)"}
    labels = list(run.labels)
    cols = []
    for lab in labels:
        c = _sanitize_name(lab)
        while c in cols:
            c += "_"
        cols.append(c)
    post_path = os.path.join(out, "posterior.npz")
    np.savez(post_path, samples=samples, labels=np.asarray(labels), columns=np.asarray(cols),
             dead_logl=np.asarray(dead.get("logl", []), dtype=np.float64), dead_logwt=wl,
             logZ=np.float64(np.nan if logz is None else logz),
             logZerr=np.float64(np.nan if logzerr is None else logzerr))
    record["result"] = {
        "logZ": None if logz is None else bc.fval(logz),
        "logZ_hex": None if logz is None else bc.fhex(logz),
        "logZerr": None if logzerr is None else bc.fval(logzerr),
        "logZ_corrected": _jsonable(result.get("logZ_corrected")),
        "log_prior_volume_fraction": _jsonable(result.get("log_prior_volume_fraction")),
        "n_samples": int(samples.shape[0]), "ndim": int(samples.shape[1]) if samples.ndim == 2 else None,
        "n_dead": dead.get("n_dead"), "n_live_reported": dead.get("n_live"),
        "nlive_actual": _jsonable(result.get("nlive_actual")),
        "prior_transform_dispatch": _jsonable(result.get("prior_transform_dispatch")),
        "dead_point_kish_ess": ess,
        "result_keys": sorted(result.keys()),
        "tinyns_runtime_diagnostics": tdiag, "tinyns_summary": tsum, "tinyns_diagnostics": tdg,
        "extra": _jsonable(extra),
        "posterior_npz": post_path, "posterior_sha256": bc.sha256_file(post_path),
        "columns": dict(zip(cols, labels)),
    }
    record["likelihood_calls"].update(
        n_like_evals=n_evals, n_like_evals_source=n_src, sampler_reported_ncall=sampler_ncall,
        evals_per_s_sampling=(None if not n_evals else n_evals / t_sampling),
        evals_per_s_steady=steady.get("evals_per_s"))
    record["progress"]["steady_state"] = steady
    record["seeds"] = {
        "seed": int(a.seed),
        "uses": {"preflight": "np.random.default_rng(seed ^ 0xC0FFEE) (legacy inference/sampling.py:388-389; "
                              "core inference/preflight.py:59)",
                 "dynesty": "rstate = np.random.default_rng(seed) for sampling and resample_equal "
                            "(legacy sampling.py:1185; core dynesty_adapter.py:136)",
                 "tinyns": "run_key, resample_key = jax.random.split(jax.random.PRNGKey(seed)) "
                           "(legacy sampling.py:560; core tinyns_adapter.py:104)"},
        "resolved_in_implementation": record["settings"]["resolved"].get("seed"),
    }
    record["budget"]["stop_reason"] = "converged (sampler returned: dlogz criterion)"
    record["budget"]["final_dlogz_remaining_last_row"] = (main_rows[-1][6] if main_rows else None)
    record["timing"]["t_main_loop_s"] = t_main
    record["timing"]["t_post_s"] = time.perf_counter() - t0
    clock.mark("post_end")
    if a.sampler == "dynesty" and probe.print_progress_seen is False:
        record["gaps"].append("dynesty ran with print_progress=False: no progress trace")
    if device["backend"] != "gpu":
        record["gaps"].append("CPU backend: no device memory_stats (peak VRAM not applicable)")
    return finish("ok", 0)


if __name__ == "__main__":
    sys.exit(main())
