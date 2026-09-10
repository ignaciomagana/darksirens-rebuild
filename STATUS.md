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
status: PR VALIDATION IN PROGRESS
working repo:   ignaciomagana/darksirens-core
working branch: rebuild/phase3-population
pull request:   #2
current SHA:    2461954c47df587ed70f711769a42779775be692
```

Do not begin Phase 4 until PR #2 is green at the exact current head, squash-
merged to core `main`, and the merged SHA is recorded here.

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

## Phase 3 progress

Population models are reconstructed under `darksirens.population`: parametric
models, mixtures/components, component-spin, grammar/registry, fixed GWTC sets,
GP models and normalization machinery. Legacy proposal/PPC
`population.sampling` and application CLI wiring remain intentionally outside
this phase.

The fully cleaned scientific gate previously passed at
`b4e476db727036fea9e97cdb8fb111206a5fba5d`:

```text
workflow run: 34437051423
job:          102744211460
full reconstructed suite: 125 passed, 1 regen-only skip
legacy/new max_abs = 0
legacy/new max_rel = 0
comparison rtol = 1e-12
ordinary population import leaves tinygp unloaded: PASS
```

PR #2 then exposed three test-only F401s in the older Phase-2 PR lint workflow:

```text
ComponentSpinModel
get_q_grid
ModelNameError
```

Only those unused imports were removed. The one-shot lint-fix workflow was then
deleted. Scientific code and numerical tolerances were unchanged. Because the
head changed, the full branch and PR acceptance gates are being rerun from
scratch at:

```text
2461954c47df587ed70f711769a42779775be692
```

Detailed record: `phases/03_population.md`.

## Production repository state

### `darksirens-core`

`main` remains Phase 2 at:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Phase 3 is under PR #2 at current head:

```text
rebuild/phase3-population
2461954c47df587ed70f711769a42779775be692
```

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

None opened. No scientific behavior change has been accepted through Phase 3.
No tolerance has been relaxed.

## Next action

Require `reference-integrity`, `phase2-foundation`, and `phase3-population` to
all pass for PR #2 at head `2461954c47df587ed70f711769a42779775be692`.
Review the final diff, squash-merge only at that head, and record the merged
core `main` SHA before starting Phase 4.
