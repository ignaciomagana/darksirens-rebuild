# Fixed-coordinate benchmark harness (legacy darksirens vs darksirens-core)

This directory holds the instrument for the A100 performance and numerical-parity
campaign (Gates 1-5). It evaluates the ordinary spectral-siren likelihood of the
frozen reference `darksirens` (c042527) and of `darksirens-core` at the same fixed
coordinates, on the same gwcat products, and writes one self-describing JSON record
per (implementation, plan, kernel mode, block settings, device). A comparator turns
two records into per-field parity verdicts and speed ratios.

Both implementations install the import name `darksirens`. Every run is therefore
its own process with its own interpreter. The harness never modifies either
package: it imports them, calls their APIs (plus the private functions the core
parity probes already use), and sets `sys.dont_write_bytecode`.

| file | role |
|---|---|
| `plans.py` | the plans, model, labels, bounds and fiducials, written once |
| `make_coords.py` | named coordinates: fiducial + prior-uniform draws + one repeat |
| `bench_fixed_theta.py` | builds one implementation for one plan, times it, records diagnostics |
| `impl_legacy.py`, `impl_core.py` | per-implementation adapters used by `bench_fixed_theta.py` |
| `bench_common.py` | compile hooks, fingerprints, encoding, jaxpr/AOT evidence, nvidia-smi join |
| `compare_records.py` | parity verdicts (bitwise, max abs, max rel), masks, repeat flags, speed ratios |
| `run_matrix.py` | convenience driver: plans x {legacy, core whole, core asis} + all comparisons |
| `tests/test_harness_smoke.py` | tiny-fixture smoke test: schema, invariants, parity at 1e-12 |

## Target definitions (Fable-owned; do not change here without the orchestrator)

Ordinary spectral plan: `H0` sampled on [20, 140]; `Om0 = 0.3075`, `w0 = -1`,
`wa = 0` fixed; the population block of the default model `powerlaw+peak` with its
default priors and the `legacy` fiducial set. These are identical in both
implementations: the harness asserts at runtime that labels, bounds, prior kinds and
fiducials match `plans.py` bit for bit (`float.hex`), and that every coordinate
decodes to the expected full parameter vector.

| plan | sampled | fixed |
|---|---|---|
| `spectral_H0` | H0 | Om0, w0, wa; the 12 population parameters at their fiducials |
| `spectral_pop` | the 12 population parameters | H0 = 67.74, Om0, w0, wa |
| `spectral_joint_small` | H0, `$v_1$`, `$\alpha_{\rm PL}$`, `$m_{\min,\rm PL}$` | Om0, w0, wa; the other 9 population parameters at their fiducials |
| `spectral_full` | H0 + the 12 population parameters | Om0, w0, wa |
| `spectral_full_component` | H0 + the 13 `gwtc3_plpeak_component_spin` parameters | Om0, w0, wa |

`H0 = 67.74` is the fiducial both implementations use (legacy
`darksirens/core/constants.py:12`, core `src/darksirens/cosmology/parameters.py:7`).
Population fiducials (`powerlaw+peak`, legacy set): `$v_1$` 0.1, `$\alpha_{\rm PL}$`
2.3, `$m_{\min,\rm PL}$` 5, `$m_{\max,\rm PL}$` 80, `$\delta m_{\min,\rm PL}$` 3,
`$\delta m_{\max,\rm PL}$` 10, `$\mu_{\rm G}$` 35, `$\sigma_{\rm G}$` 5, `$\beta$` 1,
`$\mu_\chi$` 0, `$\sigma_\chi$` 0.1, `$\gamma$` 2.5.

`spectral_full_component` is not part of the ordinary target. It exists for the
latest-format compatibility benchmark on gwcat 2.1 `parameter_space=component`
data (Product B), which both readers refuse to pair with the chi_eff model
`powerlaw+peak` (legacy `darksirens/gw/utils.py:190-197`, core
`src/darksirens/gw/samples.py:77-83`: `chieff` is only an advisory column there).
`gwtc3_plpeak_component_spin` is registered identically in both
(`darksirens/gw/populations/registry.py:548-573` in each).

### How each implementation is configured

Legacy (the CLI's own phase functions, as `scripts/benchmarks/bench_likelihood_call.py`
does): `--universe_model spectral_sirens --pop_model <model> --sampler dynesty`, plus

* H0 sampled: `--fix_de true --prior_overrides '{"H0": [20.0, 140.0]}'` and
  `Om0` in `--fixed_parameter_values`;
* H0 fixed (`spectral_pop`): `--fix_cosmology true` (H0_FID, OM0_FID, W0_FID, WA_FID);
* population fixed (`spectral_H0`): `--fix_population true --population_fiducials legacy`;
* partial population (`spectral_joint_small`): the non-sampled labels in
  `--fixed_parameter_values`;
* blocks: `--sel_batch_size` / `--pe_event_block` `N`, `off` (`none`) or omitted
  (`default` = legacy `auto`: single pass on CPU, memory model on GPU).

The exact argument vector is stored in `config.legacy_cli_args`.

Core: `ds.model(cosmology=ds.Cosmology(H0=(20, 140) or 67.74, Om0=0.3075, w0=-1,
wa=0), population=ds.Population(<model>, fixed=True or None))`,
`ds.load_events/ds.load_injections(..., fit_columns=required_fit_columns(analysis))`
and `bind_analysis(..., selection_neff_soft_guard=False, sel_batch_size,
pe_event_block)`, which is what `ds.infer(..., sampler="dynesty")` binds. Core has no
partial population fixing (`ds.Population` is fully fixed or fully sampled), so
`spectral_joint_small` runs the full H0+population `BoundAnalysis` with the 9
non-sampled parameters inserted at their fiducials by the harness
(`config.plan_adapter`). The insertion is part of the kernel. Both implementations
use the hard selection guard and `max_likelihood_variance = 1.0` (their defaults
for dynesty).

## Kernel modes (`--jit`)

* **legacy**: the `likelihood.factory.make_likelihood` closure, which jits the whole
  likelihood with the data operands, distance table and smoothing operator as jit
  arguments (`darksirens/likelihood/factory.py:945-1024`). It is both the whole-jit
  and the as-shipped kernel (dynesty calls it directly); `--jit whole` and `--jit asis`
  run the same callable, and the record says so.
* **core `asis`**: `BoundAnalysis(theta)` called eagerly, as the core Dynesty adapter
  does (`src/darksirens/inference/dynesty_adapter.py:79-82`).
* **core `whole`**: `BoundAnalysis.__call__` under one `jax.jit` built with core's own
  `darksirens.cosmology.distances.threads_distance_table`. Its arguments are the
  coordinate, `gw_pe`, `gw_selection`, the distance table and core's ambient jit
  channels (the smoothing operator). The record proves the operands are
  arguments: `jit_evidence.jaxpr` lists every constant captured anywhere in the
  jaxpr and flags any constant equal to a data array
  (`embeds_data_literal`). `jit_evidence.aot` re-traces and re-compiles the kernel
  from cold in-memory caches and reports the lowered module size and the count and
  bytes of hex `dense<"0x...">` literals. `timing.compile.first_call` shows
  1 compile request for a whole-jit kernel and hundreds for the eager path.

Each timed call is `jnp.asarray(coord)` + kernel + `jax.block_until_ready`, as in
legacy `bench_likelihood_call.py:352`.

## Usage

```bash
# 1. coordinates (numpy only)
python make_coords.py --plan spectral_full --seed 20260924 --n 8 --out coords.json

# 2. one record per implementation / mode (separate interpreters)
JAX_PLATFORMS=cpu $LEGACY_PY bench_fixed_theta.py --impl legacy --pe PE.h5 --sel SEL.h5 \
    --plan spectral_full --coords coords.json --out legacy.json --n-calls 20 --warmup 3 \
    --jit whole --sel-batch none --pe-block none --seed 20260924 --label L --device cpu
JAX_PLATFORMS=cpu $CORE_PY bench_fixed_theta.py --impl core ... --jit whole --out core_whole.json
JAX_PLATFORMS=cpu $CORE_PY bench_fixed_theta.py --impl core ... --jit asis  --out core_asis.json

# 3. compare (A is the reference of the relative difference)
python compare_records.py legacy.json core_whole.json --rtol 1e-12 --atol 0 \
    --out summary.json --md summary.md

# or everything at once
python run_matrix.py --legacy-python $LEGACY_PY --core-python $CORE_PY --pe PE.h5 --sel SEL.h5 \
    --plans spectral_H0,spectral_pop,spectral_joint_small,spectral_full \
    --seed 20260924 --n 8 --outdir OUT --tag T --device cpu --parallel 1

# smoke test (driver interpreter needs pytest + numpy; it spawns both implementations)
JAX_PLATFORMS=cpu BENCH_LEGACY_PYTHON=$LEGACY_PY BENCH_CORE_PYTHON=$CORE_PY \
    BENCH_CORE_REPO=/path/to/darksirens-core $CORE_PY -m pytest -q tests/test_harness_smoke.py
```

On the A100 host, every GPU process goes through the campaign lock and sampler,
one at a time, with the campaign env scripts (no extra XLA flags):

```bash
ROOT=/media/volume/tbs/darksirens_benchmark
$ROOT/bin/gpu_run.sh RUN.smi.csv bash -c "source $ROOT/envs/env_core.sh; cd RUNDIR; \
    python bench_fixed_theta.py --impl core ... --device gpu --smi-log RUN.smi.csv"
```

`--smi-log` joins the gpu_run.sh nvidia-smi log over the timed loop (best effort;
`rows == 0` if the sampler had not flushed). `run_matrix.py --wrap
"$ROOT/bin/gpu_run.sh {smi}" --parallel 1` does the same per run, but then the
env script has to be sourced by the caller.

`--sel-batch` / `--pe-block`: an integer, `none` (single pass) or `default` (each
implementation's own default: legacy `auto`, core `None`). The requested and the
resolved values are recorded.

## Parity semantics

`compare_records.py A B` compares, over all coordinates, `total_logL` (the timed
kernel's value), `diag_total_logL`, `event_log_evidence`, `event_mc_variance`,
`log_mu`, `n_eff`, `selection_log_correction`, `sum_event_log_evidence`,
`pe_variance_sum`, `sigma2_lnL` (= sum of event variances + N^2/N_eff),
`guard_threshold` (= max(5N, N^2/max(max_var - sum var, 1e-12))), and the decoded
full parameter vector (which must be bit-identical). Per field it reports
`bitwise`, `n_bit_different`, `max_abs`, `max_rel` (= |A-B|/|A|) and `pass` under
`|A-B| <= atol + rtol*|A|`, NaN == NaN, +/-inf exact. Masks (`pe_structural`
= valid & prior_wt > 0, `pe_support` = dL inside the distance table, `pe_final` =
the samples that contribute, and the same three for the unpadded injections), the
per-event count of contributing samples, the guard verdict and the finiteness of the
total must be exactly equal. The comparator refuses (exit 2) records with a
different plan, coordinates, input sha256 or dims, or whose own plan assertions
failed. Exit 1 = compared but parity, masks or repeat consistency failed.

Repeat consistency (inside one record): the last coordinate repeats the first; every
recorded value and mask of the pair, and every timed-loop value of each coordinate,
must be bit-identical (`repeat_consistency.bitwise`,
`repeat_consistency.timed_loop_bitwise_consistent`).

Diagnostics provenance (`diagnostics_provenance`):

* core: `likelihood.hierarchical.spectral_siren_log_likelihood(...,
  return_diagnostics=True)` with `BoundAnalysis.__call__`'s arguments, decoded with the
  private `runtime_binding._decode_theta`; eager in `asis`, jitted in `whole`.
* legacy: legacy returns only the scalar, so the per-event values, log_mu, N_eff
  and the selection correction are re-assembled from legacy internals, transcribing
  the K = 1, non-frozen, isotropic, non-WL branch of `darksiren_log_likelihood`
  (prepared redshift-prior state, `compute_selection_term`, the blocked PE reduction
  with `_pe_chunk_plan`, `selection_log_correction`) under the same block sizes. Each
  record reports `kernel_vs_diag_total` (bitwise flag and relative difference
  between the re-assembled and the kernel total).
* masks: both rebuilt from each implementation's `log_sample_weight` and redshift
  prior, in chunks of `--mask-chunk` samples, and reported in the FILE order of the
  HDF5 datasets. Legacy's factory stably sorts the injections by catalog pixel
  (`darksirens/likelihood/factory.py:1140-1163`, applied at `:2687-2693`; a spectral
  run gets nside-1 pixels), so its selection arrays are a permutation of the file
  order core keeps. The adapter recovers that permutation with legacy's own
  `_injection_pixel_order`, verifies it bit for bit, and undoes it for the masks
  (`config.legacy_injection_order`). Every record checks the reported order against
  the files' `dL` datasets (`mask_order`); the comparator only accepts mask
  equality when both records verified it.

## Timing semantics

`timing` holds `t_import_jax_s`, `t_import_package_s`, `t_backend_init_s`,
`t_config_s` (legacy option resolution; core `ds.model`), `t_load_s` (the data
loaders; includes any lazy imports they trigger), `t_build_s` (legacy parameter space
+ `_build_likelihood`; core `bind_analysis`), `t_transfer_sync_s`
(`block_until_ready` on the device operands right after the build) and
`operand_bytes`, `t_first_call_s` (compile + first execution on coords[0]),
`warmup_s` (3 explicit warm-ups on coords[:3]), `warm` (median/min/mean/std(ddof=0)/max
and every call time over `--n-calls` calls cycling all coordinates), compile counters
per phase (`compile_or_get_cached` requests and `backend_compile` compilations,
hooked as in `bench_likelihood_call.py:85-104`; a forced-recompile self-test in
`hook_selftest` proves the hooks count), memory checkpoints (host `ru_maxrss`; device
`peak_bytes_in_use` from `memory_stats()` on GPU, `None` on CPU), and wall-clock
phase stamps (`phase_clock`) for joining the nvidia-smi log.

With `JAX_COMPILATION_CACHE_DIR` set (the campaign env scripts set it), a first call
can be served from the persistent cache: compare `compile.first_call.requests` with
`compile.first_call.compiles`, and never compare first-call times across different
cache states.

## Record schema (`darksirens-bench-fixed-theta/1`)

Top level: `schema`, `status` (`ok` | `plan_mismatch`), `label`, `implementation`,
`command_line`, `cwd`, `started_utc`, `finished_utc`, `harness` (directory and git
state of this harness), `package` (`file`, `git_sha`, `git_dirty`, `py_blob_digest`
and `known_digest_match`: sha256 over the git blob ids of the package's `*.py` files,
matched to c042527 / core 88004d9 / core pin 8bf2bec5, so a non-editable install is
still tied to a commit), `env` (python, jax, jaxlib, numpy, scipy, h5py, astropy,
equinox, gwcat versions, CUDA wheels, `JAX_*`/`XLA_*`/`DARKSIRENS_*` variables),
`device` (backend, devices, kind, x64, matmul precision, XLA cache dir, CPU model,
GPU name/VRAM/driver via nvidia-smi), `inputs.{pe,sel}` (path, bytes, sha256,
`format_version`, `parameter_space`, `spin_basis`, `contract_hash`, `nobs`, `nsamp`,
`ndraw`, `n_detected`, `T_obs_yr`, fit/advisory columns), `plan` (the resolved plan),
`config` (kernel, jit mode, legacy CLI args, requested/resolved blocks, guard,
max variance, plan adapter, seed, n_calls, warmup), `dims` (`n_events`, `nsamp`,
`n_pe_samples`, `n_injections`, `n_injections_padded`, `ndraw`, `T_obs_yr`,
`n_coords`), `coords` (names, implementation labels, values and `float.hex`,
source sha256, seed, repeat map), `timing` (above), `jit_evidence`,
`values.per_coord[]` (per coordinate: `total_logL`, `total_finite`,
`diag_total_logL`, `kernel_vs_diag_total`, `event_log_evidence`, `event_mc_variance`,
`sum_event_log_evidence`, `log_mu`, `n_eff`, `selection_log_correction`,
`pe_variance_sum`, `sigma2_lnL`, `guard_threshold`, `guard_pass`, `masks`,
`decoded_full`, `timed_values_hex`; scalars as `{value, hex}`, arrays as `{hex, n}`),
`mask_order`, `repeat_consistency`, `plan_assertions` (structure, registry, decode,
and the registry view), `diagnostics_provenance`, `gaps`, and for legacy `legacy_cli_log`
(sidecar path, sha256, tail).

## Notes and hazards

* The tiny `make_gw_fixtures.py` pair (2 events, 5 injections) always trips the
  N_eff <= 5 N_obs guard, so every total there is -inf; the finite diagnostics carry
  the parity check.
* Prior-uniform draws of a 12-parameter population mostly fail the selection guard on
  real data too; the fiducial row is the one finite point to rely on.
* On Hildafs the first import after a cold file cache can take tens of seconds;
  import times are recorded separately and are not part of any gate.
* Legacy `default` block sizes on a GPU come from its H100-calibrated memory model;
  record `config.block_size_resolution` when comparing defaults.
