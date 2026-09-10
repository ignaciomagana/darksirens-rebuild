# Phase 5B checkpoint — ordinary catalog completeness

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
phase-5 branch:    rebuild/phase5-catalog-dark-bright
5A accepted head: f418174a7fc8734bfbcf553d5b5c36f9f4280987
5B accepted head: f4bc721496359f09fc58609fa23ccce21366f728
```

Legacy remained read-only. Candidate and legacy were evaluated in separate
processes.

## Status

ACCEPTED.

Phase 5B reconstructs only the ordinary non-LSS catalog completeness/count
budget. Phase 5 as a whole remains open; 5C is next.

## Accepted behavior

The core ordinary completeness path preserves the frozen legacy estimator:

```text
g(z)       = dV_c/dz * (1 + z)^delta
dN_exp/dz  = n0 * apix * g(z)
C(z|row)   = clip[dN_obs_s(z|row) / dN_exp_s(z), 0, 1]
dN_miss    = (1 - C) * dN_exp
N_miss     = integral dN_miss dz
```

The observed and expected sides use the same truncated-Gaussian smoothing
operator with fixed `sigma_smooth = 0.05`. The observed estimator uses raw real
galaxy counts and does not use `dzgals` or host weights.

For finite `z_depth`:

```text
- expected counts are truncated at z_depth before smoothing the denominator;
- C is discarded above z_depth;
- dN_miss = dN_exp above z_depth;
- N_miss integrates over the full modeled redshift grid;
- C_eff = 0 above z_depth.
```

`z_depth=None` retains the frozen full-grid behavior.

## Ownership

Added to core:

```text
src/darksirens/catalog/completeness.py
```

The accepted reconstruction keeps two deliberately separate state classes:

```text
ObservedDensityCache  # theta-independent data cache
CompletionState       # proposal-dependent expected-count grids
```

The stable `GalaxyCatalog` runtime type was not enlarged with completeness
cache/state. `darksirens.catalog` remains a light import and does not import the
completeness module eagerly.

The large 1000 x 1000 smoothing operator is threaded through the existing JIT
ambient-channel boundary instead of being captured as a dense HLO constant.

## Explicit exclusions

The following legacy branches were inspected and intentionally not migrated in
5B:

```text
delta_g / local-overdensity modulation
Q_LSS deterministic tables
Q ensembles
latent fields / latent counts
aggregate or stratified completeness
serialized magnitude-selection models
field/global catalog normalization
marks
survey-native depth/mask construction
survey-selection fitting
weak or strong lensing
```

Those remain assigned to later core extension work, `darksirens-surveys`, or
`darksirens-lss` according to the frozen ownership map.

## Diff audit

Compared accepted 5A head `f418174a7fc8734bfbcf553d5b5c36f9f4280987`
to accepted 5B head `f4bc721496359f09fc58609fa23ccce21366f728`.
The branch is eight commits ahead and zero behind. Changed files are exactly:

```text
.github/workflows/phase5-catalog-dark-bright.yml
src/darksirens/catalog/completeness.py
src/darksirens/catalog/redshift.py
tests/test_catalog_completeness.py
tests/test_catalog_completeness_hlo.py
tools/probe_catalog_completeness.py
tools/compare_catalog_completeness_probe.py
```

`catalog/redshift.py` changed only to reproduce the frozen legacy floating-point
operation order for the already-owned galaxy measure.

## Validation

Accepted exact-head workflow:

```text
workflow run: 34461981743
job:          102821696680
result:       SUCCESS
```

Focused and historical gates:

```text
Phase 5A compact tests:                    5 passed
Phase 5A redshift/distance tests:         11 passed
Phase 5B completeness/HLO tests:          11 passed
full reconstructed suite:                 226 passed, 1 regen-only skip
catalog dependency-boundary audit:        PASS
light catalog import audit:               PASS
```

Separate-process frozen-legacy parity:

```text
5A catalog-kernel parity:
    max_abs = 0.000e+00
    max_rel = 0.000e+00
    rtol    = 1e-12
    atol    = 0

5B ordinary-completeness parity:
    max_abs = 0.000e+00
    max_rel = 0.000e+00
    rtol    = 1e-12
    atol    = 0
```

The completeness probe serializes the smoothing-operator sample, galaxy-measure
grid, raw and smoothed expected counts, per-row completeness, missing-density
curves, effective completeness, retained fraction, and integrated missing count
for both full-grid and finite-depth points.

## Failed-gate record

The first 5B legacy probe failed before numerical comparison because the probe
used the reconstructed field name `log_g_grid`; frozen legacy names the same
`_CompletionGrids` leaf `log_g`. Only the probe was corrected.

The next strict comparison isolated three near-zero retained-fraction `f` values
with absolute differences of about 1e-16 while the underlying arrays were
otherwise within the numerical gate. The cause was a real last-bit operation-
ordering difference:

```text
candidate first spelling: log(dV) + delta * log1p(z)
frozen legacy spelling:   log[dV * (1 + z)^delta]
```

These are analytically identical but not bit-identical. Because
`f = 1 - N_miss/N_exp` is cancellation-sensitive near zero, the last-bit drift
was amplified in relative error. Core now uses the frozen legacy operation
order. The strict comparator was not loosened. The final run gives exact
zero-difference parity for both 5A and 5B probes.

## 5C legacy facts frozen before implementation

Read-only reconnaissance against the same legacy SHA establishes the ordinary
conditional composition to reconstruct next:

```text
dark:
    p(z|row) = [N_obs * p_cat(z|row) + dN_miss(z|row)]
               / [N_obs + N_miss]

complete, occupied row:
    p(z|row) = p_cat(z|row)

complete, empty row:
    policy=zero   -> -inf
    policy=volume -> normalized comoving-volume prior

bright PE numerator:
    Normal(z; z_counterpart, dz_counterpart)
    * normalized comoving-volume prior
    * optional resolved-global-pixel gate
```

For ordinary dark/complete models, the selection integral must use the same
redshift/host model as the PE numerator. Bright-siren selection intentionally
uses the catalog-free normalized volume prior. This asymmetry is a frozen
scientific requirement, not a dispatcher convenience.

The accepted Phase-4 `log_sample_weight` already exposes a redshift-prior
callback seam, so 5C must compose through that seam rather than recreate the
legacy `universe_model`/likelihood-factory switchboard.

## Next action

Start 5C from exact accepted head
`f4bc721496359f09fc58609fa23ccce21366f728`. Add the smallest explicit
catalog/counterpart prior state and hierarchical composition needed to reproduce
ordinary conditional `plain_full`, `plain_compact`, `complete_zero`,
`complete_volume`, and `bright` fixed-theta cells. Compare detailed PE event
evidences, MC variances, selection `log_mu`/`N_eff`, selection correction, and
final likelihood in separate legacy/candidate processes at `rtol=1e-12`,
`atol=0`. Do not start 5D or any field/LSS/survey/lensing extension until 5C is
green.
