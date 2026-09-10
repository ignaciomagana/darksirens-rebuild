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
status: VALIDATION COMPLETE / PENDING PR MERGE
working repo:   ignaciomagana/darksirens-core
working branch: rebuild/phase3-population
accepted SHA:   b4e476db727036fea9e97cdb8fb111206a5fba5d
```

Do not begin Phase 4 until the Phase-3 PR is reviewed, merged to core `main`, and
the merge SHA is recorded in this repository.

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

Core `main` after Phase 2:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Phase-2 final scientific gate:

```text
workflow run: 34431185197
job:          102726848203
status:       SUCCESS
```

The reconstructed package contains modern `src/darksirens` packaging,
side-effect-free root import, explicit JAX runtime configuration, flat-CPL
cosmology/shared redshift grids, standardized GW PE/selection store contracts,
`GWStore`/`SelectionStore`, PE/injection loaders, and current
`chieff_reference` selection support.

## Phase 3 — validation complete

Population models are reconstructed under `darksirens.population` on
`rebuild/phase3-population`. The accepted branch contains parametric models,
mixtures/components, component-spin, grammar/registry, fixed GWTC sets, GP
models and normalization machinery. Legacy proposal/PPC `population.sampling`
and application CLI wiring remain intentionally outside this phase.

Final clean acceptance gate:

```text
workflow run: 34437051423
job:          102744211460
head SHA:     b4e476db727036fea9e97cdb8fb111206a5fba5d
status:       SUCCESS
```

Results:

```text
ruff F/E9: PASS
Phase-2 regressions: 14 passed
full reconstructed suite: 125 passed, 1 regen-only skip
legacy population probe: PASS
reconstructed population probe: PASS
legacy/new max_abs = 0
legacy/new max_rel = 0
comparison rtol = 1e-12
ordinary population import leaves tinygp unloaded: PASS
```

The copied cross-phase inference/CLI assertions were physically separated from
the Phase-3 tests rather than hidden by permanent deselection. The permanent
workflow now runs plain `python -m pytest -q` in addition to focused physics
tests. No scientific tolerance was relaxed.

Detailed record: `phases/03_population.md`.

## Production repository state

### `darksirens-core`

Phase 2 is complete on `main` at:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Phase 3 is validation-complete on branch:

```text
rebuild/phase3-population
b4e476db727036fea9e97cdb8fb111206a5fba5d
```

Pending: PR review and merge. Catalog/redshift, hierarchical likelihood, GW
selection, samplers and the high-level `model/infer` API are not yet migrated.

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

None opened. No scientific behavior change has been accepted through the
Phase-3 reconstruction. Phase-3 legacy/new population parity is exact on the
accepted branch.

## Next action

Open/review the Phase-3 pull request against core `main`; merge only at accepted
head SHA `b4e476db727036fea9e97cdb8fb111206a5fba5d` after checks pass. Record the
PR and merged `main` SHA here before Phase 4 begins.
