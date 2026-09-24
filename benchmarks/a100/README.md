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
| `dark_fixture.py` | dark-siren mock fixtures: `galaxy_density.json` sidecar writer/verifier and the pre-flight |
| `dark_diag.py` | implementation-neutral catalog-side summaries (branch evidences, per-row/per-sample arrays) |
| `tests/test_harness_smoke.py` | smoke test: tiny spectral fixtures and dark fixture T; schema, invariants, parity at 1e-12 |
| `bench_components.py` | component timing (a-k) of one implementation + per-component legacy-vs-core parity (`compare`) |
| `trace_tools.py` | `jax.profiler` trace mode for the main harness and the components runner; trace -> top-N op table |
| `tests/test_components_smoke.py` | smoke test of the components runner and the trace tools (tiny spectral fixture, dark fixture T) |

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

Guard variants (`--guard default|hard|soft`, `--max-variance X`, in
`bench_fixed_theta.py` and `bench_components.py`): `default` passes nothing (the
defaults above). `hard` / `soft` pass legacy `--selection_neff_guard hard|soft` and
core `bind_analysis(selection_neff_soft_guard=False|True)`; `--max-variance X` passes
legacy `--max_likelihood_variance X` and core `bind_analysis(max_likelihood_variance=X)`.
The record stores the resolved values in `config.max_likelihood_variance`,
`config.selection_neff_soft_guard` and `config.guard` (`requested_mode`,
`requested_max_variance`, `mode`, `cap`), and every per-coordinate entry carries
`guard_mode`. `compare_records.py` (and `bench_components.py compare`, and the
components `--main-record` check) refuse a pair whose resolved guard mode or cap
differ. `campaign_run.py` spec keys: `guard`, `max_variance`; `tool: components`
with `main_record` / `trace` runs `bench_components.py` under the same driver.

## Dark sirens (`dark_*` plans, `--catalog`)

### Fixtures
The fixtures are made with the LEGACY mock machinery, unmodified
(`scripts/mock_dark_sirens/generate_mock_data.py` and `run_mock_data_test.sh` of
c042527, copied byte-identically) with an explicit `--n0 1e-3`
(log10n0 = -3, inside U(-4, -1) in both codes), never `--n-galaxies`, and
`RUN_INFERENCE=0` (generation and the legacy ingestion check only). Products:
`mock_gw_events.h5` (`gwcat-1.0` PE), `mock_gw_selection.h5` (`gwcat-selection-1.0`),
`catalog_pixelated_nside_N.h5` (attr `nside`; `zgals`/`dzgals`/`wgals` padded
`(n_pix, n_max)`, `ngals`; no `z_depth` attr), plus the complete catalog and the raw
survey. The generator records no density, so

```bash
python dark_fixture.py write --fixture-dir DIR --name T --generate-log DIR/generate.log \
    --generator-copy GEN --wrapper-copy RUN --reference-generator REF_GEN \
    --reference-wrapper REF_RUN --reference-sha c042527... --invocation "env ... sh -x RUN"
python dark_fixture.py verify --fixture-dir DIR     # SHA256SUMS + pre-flight
```

writes `galaxy_density.json` (n0, log10n0, zmax, delta, sigma_kde, n_complete, H0,
units, seed, generator sha256, the generator command parsed from the wrapper's
`sh -x` trace, the generator's stdout facts, both codes' log10n0 priors, every
product's sha256) and `SHA256SUMS`.

**Pre-flight.** Every dark record runs `dark_fixture.preflight` before JAX is
imported and exits 2 when the fixture's log10n0 lies outside the log10n0 prior of
either implementation (`plans.LOG10N0_PRIOR`), differs from the plans' survey
fiducial, was generated with `--n-galaxies`, when the density label disagrees with
the data (N_complete of `mock_galaxy_catalog_complete.h5` over a numpy V_c(z < zmax)
must equal n0 to `DENSITY_RTOL` = 1e-3 + 1/N_complete), or when the PE / selection /
catalog / complete-catalog files are not the bytes the sidecar lists. The record
keeps the evidence under `fixture_preflight` (`density_check` included).

### Plans
| plan | sampled | fixed |
|---|---|---|
| `dark_H0` | H0 | Om0, w0, wa; population; survey |
| `dark_pop` | the 12 population parameters | H0 = 67.74, Om0, w0, wa; survey |
| `dark_survey` | log10n0, delta, sigma_kde | H0, Om0, w0, wa; population |
| `dark_joint_cosmo_pop` | H0, `$v_1$`, `$\alpha_{\rm PL}$`, `$m_{\min,\rm PL}$` | Om0, w0, wa; other 9 population; survey |
| `dark_joint_cosmo_survey` | H0, log10n0, delta, sigma_kde | Om0, w0, wa; population |
| `dark_full` | H0 + population + survey | Om0, w0, wa |

Survey fiducials: log10n0 = -3 (the fixture density), delta = 0, sigma_kde = 0 (the
shared defaults; each record asserts both registries still give these defaults and
the bounds log10n0 [-4, -1], delta [-3, 3], sigma_kde [0, 0.05]).
`--survey-fixed-override '{"log10n0": X}'` replaces a FIXED survey value (plans whose
survey block is fixed only); a log10n0 outside either log10n0 prior, or a delta /
sigma_kde outside `plans.SURVEY_BOUNDS`, additionally needs
`--allow-out-of-prior-fixed-survey` and is recorded as a gap (the PR-6a 5e-5 density
is checked this way, at fixed coordinates only).

### Configuration at identical semantics
Core: `ds.model(cosmology, population, catalog=ds.load_catalog(CAT))` (the incomplete
conditional model, core's only dark estimand) and `bind_analysis` as for spectral.
Core always samples the catalog block, so a plan that fixes it (or part of the
population) runs through the harness embedding (`config.plan_adapter`). In `--jit
whole` the compact catalog and the observed-density cache are jit arguments.

Legacy: `--universe_model dark_sirens --survey_path CAT` plus, for the knobs core does
not have, the values that reproduce core's semantics (`impl_legacy.LEGACY_DARK_SETTINGS`,
recorded in `config.dark_settings`): `--catalog_sky_weighting conditional` (the CLI
default is field), `--kde_window 0` (full-row KDE), `--freeze_redshift_prior false`
(per-proposal prior), `--row_chunk auto`, `--kernel_gl_nodes 24 --kernel_gl_domain cdf`,
`--drop_full_catalog false` (one PE-union-selection table, as core), `--c_mode per_pixel`,
`--use_lss false`; a fixed survey is pinned individually in `--fixed_parameter_values`
(`--fix_survey true` would pin the registry's log10n0 = -2). Legacy behaviour with NO
knob, recorded per record: the build-time **H0 kernel pin** (active whenever none of
Om0, w0, wa, delta, sigma_kde is sampled: the per-galaxy quadrature is evaluated once
at H0 = 67.74 and shifted by 3 ln(H0/67.74)), the **empty-row sample routing** (per
side, when that side is one block and >= 10% of its samples sit on galaxy-free rows),
the injection pixel sort, and the PE/selection prior-state sharing. They are exact
analytically and move only the last bits.

### Catalog-side diagnostics
Per coordinate (`values.per_coord[].catalog`): per-event log evidences of the
catalog-host branch (`log N_obs + log p_cat - log Z`) and of the missing-host branch
(`log dN_miss - log Z`) of the prior, and of the full prior (`_harness`), the same
three log_mu, the sum of N_miss, sums/digests of the per-row arrays, empty-row counts.
The branch terms are reduced by `dark_diag.py` (numpy, identical code in both
processes) from each implementation's own per-sample masked log weights, so any
difference is the implementations'. The record's `<record>.catalog.npz` holds, per
coordinate, the per-row arrays (log N_obs, log Z, N_miss, f, log depth mass, empty
rows; union compact rows) and the per-sample log p(z|row) of the PE samples and the
injections in FILE order. `dims.catalog`: nside, npix, apix, z_depth, n_rows,
n_max (row width), occupied/empty rows and pixels, galaxy counts, sha256 of the union
pixel ids, row counts, real-galaxy tables and sample-to-row maps, and the number of PE
samples / injections on empty rows.

`compare_records.py` refuses dark records built on different catalog files. The
catalog structure (all of the above) and the empty-row sets must be equal (they
enter `masks_equal`); the catalog-side values are compared at the same rtol under
`verdict.catalog_values_pass` / `catalog_fields` / `catalog_max_rel_by_field`, so the
gate fields and `max_rel_by_field` keep their spectral definition. `rows_f` (f = 1 -
N_miss/N_exp, a diagnostic in both codes, not a likelihood input) is informational:
it cancels catastrophically on nearly empty rows (one ulp of N_miss reads as ~1e-10
relative there).

```bash
python make_coords.py --plan dark_full --seed 20260924 --n 8 --out coords.json
JAX_PLATFORMS=cpu $LEGACY_PY bench_fixed_theta.py --impl legacy --pe DIR/mock_gw_events.h5 \
    --sel DIR/mock_gw_selection.h5 --catalog DIR/catalog_pixelated_nside_16.h5 --plan dark_full \
    --coords coords.json --out legacy.json --n-calls 20 --warmup 3 --jit whole \
    --sel-batch none --pe-block none --seed 20260924 --label L --device cpu
python run_matrix.py ... --catalog DIR/catalog_pixelated_nside_16.h5 \
    --plans dark_H0,dark_pop,dark_survey,dark_joint_cosmo_pop,dark_joint_cosmo_survey,dark_full
```

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
`rows == 0` if the sampler had not flushed). The sampler runs at 1 Hz and a timed
loop of 20 calls usually lasts well under a second, so that join is mostly empty:
pass `--util-window-s S` (e.g. 15) to keep calling the kernel back to back for S
seconds after the timed loop and join the log over that window
(`timing.util_window.smi`). The record lists a gap when neither window holds 3
sampler rows. The nvidia-smi timestamps are parsed in the local time zone of the
benchmark process, which must be the sampler's host (UTC on js2a100). `run_matrix.py --wrap
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
different plan, coordinates, input sha256, dims, selection-guard mode or
`max_likelihood_variance`, or whose own plan assertions failed. Block sizes may
differ between the two records (that is how a blocked run is checked against the
single pass); both are listed in the summary. Exit 1 = compared but parity, masks or repeat consistency failed.

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

Peak memory: `peak_device_bytes` and `peak_host_rss_bytes` are the process peaks at
the END OF THE TIMED LOOP (the counters are cumulative, so they include the build,
the first call and the warm-ups, but not the untimed passes that follow).
`peak_device_bytes_all_phases` / `peak_host_rss_bytes_all_phases` also cover the jit
evidence, the diagnostics and the per-sample mask passes, which allocate their own
buffers and can exceed the kernel's peak (measured on CPU, core `asis` with
`sel 4096 / pe 6`: 3846 MiB at the end of the timed loop, 5141 MiB after the
diagnostics). Quote the kernel-phase value for the memory gate.

`host_loadavg_timed_loop` records the host load averages before and after the timed
loop (competing processes on a shared CPU host). A record whose timed loop issued
compile requests lists a gap: its warm statistics and peak memory are not a steady
state. `compare_records.py` sets `timing.comparable = false` and lists why when the two
records ran on different backends, device kinds or hosts, with different `--n-calls` /
`--warmup`, or when either compiled inside its timed loop; the ratios are still
reported.

With `JAX_COMPILATION_CACHE_DIR` set (the campaign env scripts set it), a first call
can be served from the persistent cache: compare `compile.first_call.requests` with
`compile.first_call.compiles`, and never compare first-call times across different
cache states.

### Memory knobs (Gate 3b retries)

Only documented knobs, applied identically to both codes where both have them, every value
recorded in `config.memory_knobs` (requested and effective, plus `non_default_settings`):

* `--row-chunk auto|off|N` (legacy only, dark plans): legacy's own CLI `--row_chunk`
  (`cli/inference.py:1853-1866` -> `redshift/catalog.py:169-191`, `lax.map` over N-row chunks
  of the kernel-state build). Unset = `auto`, the H2 setting. Refused for core (exit 2): core's
  row chunking is fixed (auto, 512 rows above n_rows*n_max > 2^25, `catalog/redshift.py:46-49`),
  recorded as such.
* `--mem-fraction X`: `XLA_PYTHON_CLIENT_MEM_FRACTION` for the benchmark process, set before JAX
  is imported; unset = the default allocator (0.75). The resulting `bytes_limit` is recorded.
* `--steady-window N`: `timing.warm.steady` = statistics of the last N timed calls;
  `timing.warm.first20` = the first 20 (the 20-call protocol median inside a longer run).
* `--slow-call-s S --slow-n-calls N`: if a warm-up call exceeds S seconds, N timed calls.
* `--catalog-npz digest`: no `.catalog.npz` sidecar (about 1.2 GB on R2); each array's shape
  and sha256 go into `catalog_arrays_digest`. compare_records then checks the empty-row sets
  through the per-coordinate `row_empty_sha256_u8`; every JSON catalog field is still compared.
* Failure records carry the full device `memory_stats()` at the failure point
  (`failure.memory_at_failure.device_memory_stats`, incl. `largest_free_block_bytes`).
* `gate3_specs.py g3b_retries` lists the candidate records; `gate3b_table.py` builds the CSV.

## Record schema (`darksirens-bench-fixed-theta/1`)

Top level: `schema`, `status` (`ok` | `plan_mismatch`), `label`, `implementation`,
`command_line`, `cwd`, `started_utc`, `finished_utc`, `harness` (directory and git
state of this harness), `package` (`file`, `git_sha`, `git_dirty`, `py_blob_digest`
and `known_digest_match`: sha256 over the git blob ids of the package's `*.py` files,
matched to c042527 / core 88004d9 / core pin 8bf2bec5, so a non-editable install is
still tied to a commit), `env` (python, jax, jaxlib, numpy, scipy, h5py, astropy,
equinox, gwcat versions, CUDA wheels, `JAX_*`/`XLA_*`/`DARKSIRENS_*` variables),
`device` (backend, devices, kind, x64, matmul precision, XLA cache dir, XLA platform
version, CPU model; on GPU: name/VRAM/driver/uuid via nvidia-smi, plus, best effort,
compute capability, PCI bus id, persistence/MIG/ECC mode, max clocks, power limit
and the driver's CUDA version), `inputs.{pe,sel}` (path, bytes, sha256,
`format_version`, `parameter_space`, `spin_basis`, `contract_hash`, `nobs`, `nsamp`,
`ndraw`, `n_detected`, `T_obs_yr`, fit/advisory columns), `plan` (the resolved plan),
`config` (kernel, jit mode, legacy CLI args, requested/resolved blocks, guard,
max variance, plan adapter, seed, n_calls, warmup), `dims` (`n_events`, `nsamp`,
`n_pe_samples`, `n_injections`, `n_injections_padded`, `ndraw`, `T_obs_yr`,
`n_coords`, and `catalog`: whether a galaxy catalog enters the kernel and its
shape; absent for every spectral plan, the full catalog dimensions for a dark plan),
dark records also `inputs.catalog`, `fixture_preflight`, `catalog_arrays` (the
`.catalog.npz` sidecar) and `values.per_coord[].catalog`,
`coords` (names, implementation labels, values and `float.hex`,
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
* Core `--jit asis` with an explicit `--sel-batch N` and/or `--pe-block N` re-traces and
  re-compiles its `lax.scan` bodies on every call (measured on CPU, Product A first16 +
  stride100, `sel 4096 / pe 6`: 2 compile requests per call in the timed loop, 4.9 s
  median per call against 26 ms for `--jit whole`, 3846 MiB peak RSS at the end of the
  timed loop against 623 MiB for `--jit whole`). Check `timing.compile.timed_loop`
  before reading an eager timing.
* The legacy selection sum runs over pixel-sorted injections and core's over file
  order, so `log_mu` / `n_eff` can differ in the last bits between the two while
  every mask is identical.

## Component timing and profiling (`bench_components.py`, `trace_tools.py`)

For the attribution question (where does a likelihood call spend its time?)
`bench_components.py` builds the SAME model as `bench_fixed_theta.py` (the same
adapters, plan, coordinates, inputs and block sizes) and times its pieces as
separate `jax.jit` kernels, each with its data as ARGUMENTS (each implementation's
own `threads_distance_table`, so the distance table and the smoothing operator are
arguments too; every record carries the jaxpr constant inventory per component).
Every component is warm-timed exactly like the whole likelihood in the main harness:
first call on coords[0] (compile + run), 3 warm-ups, `--n-calls` timed calls cycling
the coordinates, `block_until_ready` each, median/min/mean/std, compile requests per
phase (0 in every timed loop). When a component already ran on coords[0] while the
inputs of later components were precomputed, that invocation is its first call
(`first_call_context`). After timing, each component is re-lowered and re-compiled
from cold in-memory caches with the persistent compilation cache disabled for that
pass (`aot`: trace+lower and compile seconds, module size; `aot_policy`), so an AOT
compile time is never a cache read. With `--cache-mode cold` the first call is a true
compile too (`first_call_compile.compiles`).

| component | legacy (c042527) | core (88004d9) |
|---|---|---|
| `a_cosmology` | `utils.cosmology.dL_of_z` grid, `z_of_dL_precomputed`, `inference.utils.log_jacobian_*`; spectral: prepared dV/dz grid | `cosmology.distances.*`, `likelihood.weights.log_jacobian_*`; spectral: `normalized_comoving_volume_grid` |
| `b_population` | `gw.populations.pop_model_parser` -> `log_p_pop` | `population.pop_model_parser` -> `log_p_pop` |
| `c_pop_norm` | mass/spin `_norm` + per-sample pairing `_panel_norm`, lifted out of `component_densities` | the same calls (identical class text) |
| `w_weights` | the `_ll_given_states` weight closures, state as input (encloses a+b+g) | the hierarchical `_weight` closures, state as input |
| `d_pe_reduce` | TRANSCRIBED block reduction (inline in `_ll_given_states`) with legacy `log_evidence_and_mc_variance` | `likelihood.event.reduce_pe_events` (pass-through weights) |
| `e_sel_reduce` | `selection_reduce_from_ldw_provider` + `selection_log_correction` | same names in `selection.gw` |
| `f_kernel_state` | `redshift.catalog.catalog_kernel_state` (+ `log_galaxy_measure_grid`) | `catalog.redshift.build_catalog_kernel_state` |
| `h_completion` | `redshift.completion.completion_curves` | `catalog.completeness.completion_curves` |
| `fh_prior_state` | `prepare_redshift_prior_state('dark_sirens')`, built once per call | `build_incomplete_catalog_prior_state`, built twice per call as written |
| `g_prior_eval` | `eval_redshift_prior_with_state` (with the factory's empty-row routing plan) | `eval_incomplete_catalog_prior_state_vmap`; spectral: `log_comoving_volume_prior` (enclosing) |
| `g_prior_eval_unrouted` | the same without the routing plan (legacy dark, when routing is active) | n/a |
| `i_whole` | the factory closure (= the main harness kernel) | `--jit whole` (default) or `asis` |
| `j_transfer` | `device_put` of the kernel operands + sync | same |
| `k_layout` | `_injection_pixel_order` + `_permute_rows` (a one-time build step) | n/a: core keeps the file order |

`COMPONENTS` in `bench_components.py` holds the full references with `path:line`
and says, per implementation, whether a component is `separable` (a function of the
implementation), `enclosing`, `transcribed` or `isolated` (per plan universe where it
differs: core's spectral `g_prior_eval` is `enclosing`, since `log_comoving_volume_prior`
rebuilds and normalises the dV/dz grid per call); the compare table shows both kinds and
names the enclosing components (`w_weights` = a+b+g, `fh_prior_state` = f+h). Outputs are stored per
coordinate (sha256, shape, min, max, finite counts) and as float64 arrays in FILE
order (legacy's pixel-sorted injections mapped back) in `<out>.components.npz`;
arrays larger than `--big-array-elements` (1e6) only for `--full-array-coords`
(0,1), informational ones only for the first of them, and `fh_prior_state.dN_miss`
never (digest-checked equal to `h_completion.dN_miss`).

```bash
python make_coords.py --plan dark_full --seed 20260924 --n 8 --out coords.json
$PY bench_fixed_theta.py --impl legacy ... --out main_legacy.json          # the main record
$PY bench_components.py --impl legacy --pe PE --sel SEL --catalog CAT --plan dark_full \
    --coords coords.json --out comp_legacy.json --device cpu --n-calls 20 --warmup 3 \
    --main-record main_legacy.json --cache-dir CACHE --cache-mode cold [--trace TRACEDIR]
python bench_components.py compare comp_legacy.json comp_core.json --out cmp.json --md cmp.md
```

`--main-record` makes `i_whole` prove it is the main harness's number: same
implementation, plan, coordinates, inputs, blocks and kernel, and a bit-identical
total (and timed values) at every coordinate (`whole_vs_main_record.bitwise`).
`component_vs_main_diagnostics` compares `d`/`e` with the record's diagnostics
(informational).

`compare` refuses (exit 2) two records that `compare_records.py` would refuse (record
status, plan name / model / sampled / fixed values, catalog, coordinates, input files,
dims, guard mode and variance cap). `compare` (A = the reference, normally legacy) checks each output element by
element: `|A-B| <= rtol |A|` (rtol 1e-12, atol 0), NaN == NaN, infinities exact;
`g_prior_eval*` outputs (per-sample catalog log densities) under D-catvals
(`|delta log p| <= 1e-12` absolute, informational); `C_eff` and `f` informational. A coordinate whose array was not stored (above
`--big-array-elements`, outside `--full-array-coords`) counts only if its digests are
equal; otherwise it is listed in `unverified_coords` and the table says so
(`all_gate_coverage_complete`); pass `--full-array-coords 0,1,...,8` to compare all.
`f_kernel_state.log_kw_eff_rowmax` (the evaluator's per-row stabilising offset) is
compared on occupied rows only (`MASKED_BY`): on a galaxy-free row the evaluator
returns -inf whatever the offset, and legacy's H0-pinned builder stores the scalar
shift 3 ln(H0/67.74) there (`redshift/catalog.py:1218`) where the unpinned rule and
core store 0.0; the unmasked difference is reported next to it.
It flags an `e_sel_reduce` failure confined to `n_eff` (with N_eff/N_draw) and a
`d_pe_reduce` failure confined to `event_vars` for the orchestrator's rules; it
does not apply them. `sum_check` (informational) sets the sum of the component warm
medians (a+b+g+d+e and w+d+e, plus the prior-state builds per call) against the
whole: the whole jit fuses and CSEs across components, so they need not agree.

### Tracing (`trace_tools.py`)

* `bench_components.py --trace DIR [--trace-calls N] [--trace-drop-xplane]`: after
  the untraced timing, each component's calls run again inside
  `jax.profiler.trace(DIR/<component>)` with a `TraceAnnotation("bench_call")` per
  call; every traced output is checked bit for bit against the untraced one
  (`trace.numerics_unchanged`, `trace.whole_bitwise_under_trace`). The record's
  timings are never taken under the profiler.
* `python trace_tools.py main --trace DIR -- <bench_fixed_theta.py arguments>`: the
  main harness with its timed loop traced (hooks on `PhaseClock.mark`, no edit of
  `bench_fixed_theta.py`); the record gets `trace` and a gap (its warm timings include
  profiler overhead). `python trace_tools.py check-numerics TRACED.json UNTRACED.json`
  compares every per-coordinate value hex (exit 0 = bit-identical).
* `python trace_tools.py parse DIR [--top 25] [--json F] [--md F]`: the newest
  `plugins/profile/<session>/*.trace.json.gz` -> top-N ops by self time (children on
  the same thread subtracted) with shares, per category and per kind (fusion, reduce,
  gather/slice, scatter, control, layout, library, sort, transfer, other), device busy time
  (union of the op intervals) and the idle gaps inside each `bench_call` window. On
  GPU the ops are the `/device:GPU:N` "XLA Ops" line (else its stream lines, each
  kernel named by its `hlo_op` arg when present; the GPU branch is so far checked on a
  synthetic trace only); on CPU
  the HLO-named events of the `tf_XLA*` executor threads (so "device time" there is
  host-thread time). The `perfetto_trace.json.gz` next to it opens in ui.perfetto.dev.
* Source attribution: the components runner saves each kernel's OPTIMIZED HLO
  (`<out>.hlo/<component>.hlo.txt`, from its AOT compile) and annotates its trace
  table: for every top op, the `source_file:line` and `op_name` metadata of the HLO
  instructions it fuses (`hlo_sources`, `hlo_op_names`), plus a dominant-source table
  (each op's self time assigned to the source line most of its instructions carry: a
  heuristic, labelled as such). Each top op also carries its HLO result shape and the
  largest leading dimension among its result and operands, named from the record's dims
  (PE samples, events, injections, catalog rows), with a self-time table by that axis:
  shared helpers (interpolation, population, logsumexp) carry the same source lines on the
  PE and the selection side, and the axis is what tells them apart. `trace_tools.py parse
  DIR --hlo FILE [--record REC]` and `trace_tools.py main --hlo FILE` do the same for any
  trace whose module that HLO is (the op names of the main harness's whole kernel and the
  components runner's `i_whole` agree).

## Gate 5 inference ladder (`infer_ladder.py`, `compare_posteriors.py`)

Real-data spectral-siren nested sampling on Product A
(`A_pe_chieff_bbh259_n4096_v20.h5` + `A_sel_chieffref_o3o4ab_v20.h5`), one run of one
implementation per process. The rungs are Fable's (`ladder_configs/rungs.json`); one
population model throughout, the one that carries the shared GWTC-5 preset
(`gwtc5_fiducial_bpl2peaks`), except rung 5b (the Gate 1 kernel model `powerlaw+peak`).

| rung | sampled | fixed | legacy (beyond the common flags) | core |
|---|---|---|---|---|
| 1 | H0 [20, 140] | population = GWTC-5 preset; Om0, w0, wa | `--fix_population true --population_fiducials legacy --fix_de true --prior_overrides '{"H0":[20,140]}' --fixed_parameter_values '{"Om0":0.3075}'` | `Cosmology(H0=(20,140))`, `Population(m, fixed="gwtc5")` |
| 2 | 17 population | H0 67.74, Om0, w0, wa | `--fix_cosmology true` | `Cosmology(H0=67.74)`, `Population(m)` |
| 3 | first 3 population | H0 and the other 14 at the preset | `--fix_cosmology true --fixed_parameter_values '{14 labels: preset}'` | `InferenceTarget` over rung 2's plan with the 14 inserted |
| 4 | H0 + first 3 population | the other 14 at the preset; Om0, w0, wa | `--fix_de true --prior_overrides H0 --fixed_parameter_values '{Om0, 14 labels}'` | `InferenceTarget` over rung 5's plan with the 14 inserted |
| 5 | H0 + 17 population | Om0, w0, wa | `--fix_de true --prior_overrides H0 --fixed_parameter_values '{"Om0":0.3075}'` | `Cosmology(H0=(20,140))`, `Population(m)` |
| 5b | H0 + 12 `powerlaw+peak` | Om0, w0, wa | as 5 with `--pop_model powerlaw+peak` | as 5 with `Population("powerlaw+peak")` |

Every run passes the same settings to both codes (`ladder_configs/settings_gate5.json`;
the driver records each code's resolved values under `settings.resolved`):
`nlive`, `dlogz`, `seed`, `max_samples` (0 = no cap, so dlogz is the only stopping rule),
TinyNS preset `recommended` (`jax_block_size` 32), preflight on, prior-transform dispatch
`auto`, progress printing on, checkpointing off (legacy `--checkpoint_interval off
--resume off`; core `checkpoint_interval_seconds=0.0`), single-pass selection and PE
blocks, and the selection guard (`--guard soft|hard`, `--max-variance`).

How each code is driven:

* legacy: the `darksirens_inference` CLI's phase functions in `main()`'s order, with the
  exact argument vector stored in `invocation.argv`; `_save_outputs` (samples.npy,
  results.hdf5, corner plot) is not run, the driver writes its own posterior file.
* core: `ds.model` + `ds.load_events` / `ds.load_injections` + `bind_analysis` (what
  `ds.infer` binds for an ordinary analysis), then `ds.infer(ds.InferenceTarget(...))`,
  the same `_execute_target` path; rungs 3 and 4 need the target form because
  `ds.Population` is either fully fixed or fully sampled. `invocation` holds the
  expression and, for rungs 1, 2, 5 and 5b, the one-line ordinary `ds.infer` equivalent.

Instrumentation (observation only): the likelihood handed to the sampler is wrapped by a
counter (eager / traced calls per phase); `tinyns.NestedSampler.run` receives a
`callback` (callback_interval 1: every outer iteration, i.e. every JAX block of 32
iterations with the recommended preset) and dynesty's `run_nested` a `print_func`;
a monitor thread samples `memory_stats()` (GPU) and the host RSS; XLA compile requests,
compilations and their seconds are counted per phase (build, first call, sampling).
`--describe` stops after the plan assertions and the first call.

```bash
# one run (CPU)
JAX_PLATFORMS=cpu $CORE_PY infer_ladder.py --impl core --rung 5 --sampler tinyns \
    --pe PE.h5 --sel SEL.h5 --nlive 1000 --dlogz 0.1 --seed 20260924 --guard soft \
    --max-variance 1.0 --max-samples 0 --out OUT/core_r5_tinyns --device cpu \
    --cache-dir CACHE/core_r5_tinyns --cache-mode cold
# on the A100 (one GPU job at a time, through the campaign lock and sampler)
$ROOT/bin/gpu_run.sh RUN.smi.csv bash -c "source $ROOT/envs/env_core.sh; cd RUNDIR; \
    python infer_ladder.py --impl core ... --device gpu --smi-log RUN.smi.csv"
# posterior / evidence / progress comparison (integration check, never parity)
python compare_posteriors.py OUT/legacy_r5_tinyns OUT/core_r5_tinyns --out cmp.json --md cmp.md
```

Outputs per run directory: `record.json` (schema `darksirens-infer-ladder/1`: the
fixed-theta records' provenance fields `harness`, `package`, `env`, `device`, `inputs`,
`xla_cache`, plus `sampler_backends` (tinyns / dynesty versions, digests, pip
`direct_url`), `rung`, `settings.{requested,resolved}`, `invocation`, `plan` (the
implementation's labels, bounds, kinds, joint constraints and the decoded full vector at
the rung centre, asserted against the rung), `first_call`, `timing` (import, config,
load, build, first call, sampling with sub-events, main loop, post), `compile`,
`likelihood_calls` (`n_like_evals`: every eager call for dynesty; preflight calls +
TinyNS `ncall` for tinyns), `progress` (+ steady-state iterations / evaluations /
-log X per second), `result` (logZ, logZerr, n_samples, n_dead, Kish ESS of the dead
points, TinyNS diagnostics), `seeds`, `memory`), `progress.csv` (iteration, log-volume,
logZ, remaining dlogz, cumulative calls, wall time), `posterior.npz` (`samples`,
`labels`, sanitized `columns`, `dead_logl`, `dead_logwt`, `logZ`, `logZerr`),
`memory.csv`, `run.log`, and `legacy_run/` (legacy's own run directory with
settings.json and run_fingerprint.json). Exit 0 ok / described, 2 usage, 3 plan
mismatch, 4 build error, 5 sampler error (the record's `sampler_error.preflight_abort`
flags the nested-sampler preflight abort that the hard guard triggers when every prior
draw is -inf).

`compare_posteriors.py A B` refuses runs that differ in rung, plan, inputs or any matched
setting (`--cross-sampler` lets the sampler differ). It reports per-parameter means,
stds, 16/50/84 % quantiles, the mean difference in units of the posterior std and of the
combined Monte-Carlo error (Kish ESS of the dead points), two-sample KS D (approximate
p-value with the ESS as effective sizes), logZ agreement in units of the combined quoted
error, the rung-centre first-call values, and performance: evaluations per second,
steady-state iterations and -log X per second, time to reach common -log X levels, ESS
per second, peak memory.

`tests/test_ladder_smoke.py` (CPU): rung and argument-vector unit checks, `--describe`
of all six rungs in both codes (plans and decoded centres identical), rung 1 with tinyns
and dynesty in both codes, the comparator, and the preflight-abort path.
