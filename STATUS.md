# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 3 — POPULATION MODELS
status: IN PROGRESS
working repo:   ignaciomagana/darksirens-core
working branch: rebuild/phase3-population
```

Do not advance to Phase 4 until the permanent `phase3-population` workflow is
fully green, including the separate-process pinned-legacy/new numerical probe.

## Completed

### Phase 0

- four-package ownership model confirmed against the legacy code;
- package, dependency, experiment/script and test inventories recorded;
- major cross-domain dependency inversions identified;
- GP population models assigned to core;
- LSS and lensing assigned to mature first-class companion packages.

### Phase 1

- unified K=1 legacy likelihood bank frozen byte-identically in `darksirens-core`;
- pinned legacy replay established in a separate import root;
- canonical reconstructed likelihood target fixed at `rtol=1e-12`, `atol=0`;
- known ~`2.3e-12` legacy CPU drift isolated to the three Q/LSS replay cells only.

### Phase 2

PR `ignaciomagana/darksirens-core#1` was squash-merged.

Core `main` is now:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

The reconstructed package contains:

- modern `src/darksirens` packaging;
- side-effect-free root import;
- explicit JAX runtime configuration;
- flat-CPL cosmology and shared redshift grids;
- standardized GW PE/selection store contracts;
- `GWStore` and `SelectionStore` records;
- PE/injection loaders with density-aware spin-basis negotiation;
- current `chieff_reference` selection support.

Phase-2 final scientific gate:

```text
workflow run: 34431185197
job:          102726848203
status:       SUCCESS
```

Results:

```text
ruff F/E9: PASS
14 candidate tests: PASS
cosmology legacy/new max_abs = 0
cosmology legacy/new max_rel = 0
GW-store legacy/new max_abs = 0
GW-store legacy/new max_rel = 0
GW-store comparison rtol = 0 (exact)
light package-root import: PASS
```

## Phase 3 progress

Population code is being reconstructed under `darksirens.population` on
`rebuild/phase3-population`. The migrated slice currently includes parametric
models, mixtures/components, component-spin, grammar/registry, fixed GWTC sets,
GP models and normalization machinery.

The first full population run reached the scientific tests and produced:

```text
Phase-2 regressions: 14 passed
population block:    86 passed, 14 failed, 1 skipped
```

All 14 failures were cross-phase test ownership leaks: four required the future
`darksirens.inference.prior` transform and ten required the old main/lensing
CLIs. No population numerical failure was reported in that run. The validation
has been split so Phase 3 tests only the core-owned scientific contracts while
preserving the omitted inference/CLI contracts for their later owner phases.

The corresponding detailed record is `phases/03_population.md`.

## Production repository state

### `darksirens-core`

Phase 2 is complete on `main` at:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Phase 3 is in progress on `rebuild/phase3-population`.

Catalog/redshift, hierarchical likelihood, GW selection, samplers and the
high-level `model/infer` API are not yet migrated.

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Architecture questions intentionally deferred

- minimal LSS redshift/auxiliary-likelihood protocol;
- minimal strong-lensing analysis protocol;
- exact optional flow API.

These remain deferred until ordinary core likelihood parity.

## Scientific questions

None opened. No scientific behavior change has been accepted in Phases 0-2.
Phase 3 remains unaccepted until its parity gate passes.

## Next action

Complete Phase 3 population validation. Require registry/grammar, component-spin,
normalization/support, GP tests, optional-dependency boundary and separate-process
legacy/new population parity at `rtol=1e-12` before opening the next phase.
