# Phase 12A — completion-curve composition acceptance

## Status

**ACCEPTED / MERGED**

Phase 12A is the first post-reconstruction core extension admitted by the Phase 12 production-analysis contract. It does not reopen or reinterpret the frozen reconstruction. Its only purpose is to expose one generic composition seam already implicit in the accepted ordinary catalog implementation so the DESI magnitude-selection consumer can reuse the frozen scientific kernels without copying them into the analysis repository.

## Contract

Control contract:

```text
repository:  ignaciomagana/darksirens-rebuild
contract PR: #3
contract merge: 90bf40ae90a534020d69f51aa9b44ec381d80e00
file: phases/12A_completion_curve_composition.md
```

The contract allowed exactly one scientific-library change:

```text
CompletionCurves
    -> build_incomplete_catalog_prior_state_from_curves(...)
    -> IncompleteCatalogPriorState
```

No new completeness prescription, magnitude-selection equation, likelihood reducer, sampler, survey adapter, LSS state, lensing state, or public `ds.model()` dispatcher was permitted.

The pre-existing count-derived ordinary path had to be refactored through the same constructor and remain exactly unchanged.

## Core implementation

Repository:

```text
ignaciomagana/darksirens-core
```

Historical frozen reconstruction base:

```text
af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
```

PR:

```text
#8  Phase 12A: generic CompletionCurves composition seam
```

First candidate head:

```text
4ed98e1fab455dd7b9ad21695a017cc7e592e20a
```

Corrected accepted PR head:

```text
4d307b3034ca9702db84943b402064366adf35c9
```

Squash merge / new Phase-12 core pin:

```text
8b9dc64629cf11838a9fc1de233e46b91082caf7
```

Merged tree:

```text
95325a34e62d9edd034ee3dfa834820e0fdd41ed
```

The merge has one parent, the historical frozen core SHA `af2488b0...`. The reconstruction freeze therefore remains a well-defined historical state; Phase 12 consumers must explicitly opt into the new post-reconstruction pin.

## Production diff

Only the generic catalog-model module changed scientifically:

```text
src/darksirens/catalog/models.py
```

plus the focused acceptance test:

```text
tests/test_completion_curve_composition.py
```

The merged production change:

1. imports the already-accepted `CompletionCurves` type;
2. adds `build_incomplete_catalog_prior_state_from_curves(cosmo, params, catalog, curves)`;
3. constructs the already-existing `IncompleteCatalogPriorState` from the supplied `curves.dN_miss` / `curves.N_miss` and the already-existing catalog-kernel state;
4. refactors `build_incomplete_catalog_prior_state(...)` so its pre-existing count-derived `completion_curves(...)` output is passed through the new constructor;
5. exports the new constructor from `darksirens.catalog.models`.

No equation in `selection/catalog.py`, `catalog/completeness.py`, `likelihood/hierarchical.py`, `likelihood/host_density.py`, population code, inference code, or sampler code was changed.

## Harness-only correction before acceptance

The first production candidate `4ed98e1...` was not accepted because its new test contained two incorrect assertions. The production implementation was not changed by the correction.

The test mistakes were:

1. demanding bit-for-bit equality between a separately evaluated NumPy `log` expression and the JAX runtime expression; the observed discrepancy was approximately `1.8e-15` and was only operation-order rounding;
2. requiring every Schechter log-density grid value to be finite, although a valid zero-density support point is represented by `-inf` in log space.

Representative failed workflows on the first head were:

```text
phase8-regression          34806252003
phase6-inference-io        34806251694
phase4-spectral-likelihood 34806251655
phase7-regression          34806251550
phase6-runtime-guards      34806251663
phase5-catalog-dark-bright 34806251787
phase3-population          34806251862
```

The correction changed only `tests/test_completion_curve_composition.py`:

- the normalization check now evaluates the accepted runtime arithmetic in JAX;
- `-inf` is accepted as a legitimate zero-density log value while NaN and `+inf` remain forbidden;
- row densities must still be finite/non-negative after exponentiation and normalized on the shared redshift grid;
- the old count-completeness path remains pinned by strict `assert_array_equal` checks on the complete state and evaluated prior.

Corrected head:

```text
4d307b3034ca9702db84943b402064366adf35c9
```

## Exact-head acceptance matrix

Every PR-triggered workflow on the corrected head completed successfully. Load-bearing runs include:

```text
reference-integrity          34806757741  SUCCESS
phase2-foundation            34806757837  SUCCESS
phase3-population            34806757883  SUCCESS
phase4-spectral-likelihood   34806757876  SUCCESS
phase5-catalog-dark-bright   34806757858  SUCCESS
phase6-inference-io          34806757964  SUCCESS
phase6-runtime-guards        34806757859  SUCCESS
phase7-regression            34806757878  SUCCESS
phase8-regression            34806757776  SUCCESS
phase8b-inference-target     34806757905  SUCCESS
phase8c-host-density         34806758021  SUCCESS
```

All Phase-6 adapter/persistence workflows and Phase-7 public-interface workflows triggered by PR #8 also passed on the same exact head.

Most importantly, the Phase-5 scientific parity workflow completed all of its pinned-legacy comparisons successfully on the corrected head:

```text
catalog-kernel parity              PASS
ordinary count-completeness parity PASS
ordinary dark-siren likelihood     PASS
marked-host parity                 PASS
catalog-selection parity           PASS
```

This establishes that the refactor did not perturb the historical ordinary catalog path and that the already-frozen magnitude-selection runtime remains unchanged.

## Merge and post-merge validation

PR #8 was squash-merged with the expected-head guard set to the exact accepted head:

```text
expected head: 4d307b3034ca9702db84943b402064366adf35c9
merge SHA:     8b9dc64629cf11838a9fc1de233e46b91082caf7
merge tree:    95325a34e62d9edd034ee3dfa834820e0fdd41ed
```

The only push-triggered post-merge workflow is the frozen-reference integrity gate:

```text
run: 34807249732
job: 103861422867 (frozen-reference)
status: SUCCESS
```

It passed both the frozen legacy bundle validation and comparator self-test on merged `main`.

## Scientific meaning

Phase 12A adds **composition, not science**.

For any already-computed `CompletionCurves`, the ordinary incomplete-catalog prior remains

```text
N_obs p_cat(z | row) + dN_miss(z | row)
-----------------------------------------
             N_obs + N_miss
```

with the same finite-depth observed-host factor, catalog kernel, row normalization, and redshift-grid interpolation already accepted during reconstruction.

The new seam lets the Phase 12 DESI consumer obtain `CompletionCurves` from the already-frozen magnitude-selection runtime and then enter the ordinary hierarchical reducer without reproducing private core algebra in the analysis repository.

## Phase 12 dependency pin

For Phase 12 production work, the active core pin is now:

```text
darksirens-core = 8b9dc64629cf11838a9fc1de233e46b91082caf7
```

The companion packages remain unchanged:

```text
darksirens-surveys = f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss     = 3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing = 43c450742b733d7b8d938116021e8ca52a31226e
```

Any Phase 12 P12.1/P12.2/P12.3 provenance generated against the earlier historical core pin is stale by construction and must be regenerated before P12.4 numerical inference is allowed.

## Verdict

Phase 12A is accepted and merged. The DESI production consumer may depend on the new core SHA above. No further core change is required for the fixed-population DESI magnitude-selection comparison currently planned as P12.4.
