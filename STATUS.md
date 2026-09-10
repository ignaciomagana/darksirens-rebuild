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
status: READY FOR GUARDED SQUASH MERGE
working repo:   ignaciomagana/darksirens-core
working branch: rebuild/phase3-population
pull request:   #2
accepted SHA:   2461954c47df587ed70f711769a42779775be692
```

Do not begin Phase 4 until PR #2 is squash-merged at the exact accepted head and
the merged core `main` SHA is recorded here.

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

## Phase 3 — ready for merge

Population models are reconstructed under `darksirens.population`: parametric
models, mixtures/components, component-spin, grammar/registry, fixed GWTC sets,
GP models and normalization machinery. Legacy proposal/PPC
`population.sampling` and application CLI wiring remain intentionally outside
this phase.

The first clean scientific acceptance passed at
`b4e476db727036fea9e97cdb8fb111206a5fba5d`, with:

```text
full reconstructed suite: 125 passed, 1 regen-only skip
legacy/new max_abs = 0
legacy/new max_rel = 0
comparison rtol = 1e-12
ordinary population import leaves tinygp unloaded: PASS
```

PR #2 then exposed three test-only F401s in the older Phase-2 PR lint workflow.
Only those unused imports were removed; scientific code and tolerances were
unchanged. The complete gate was rerun from scratch at the final accepted head:

```text
2461954c47df587ed70f711769a42779775be692
```

All PR-triggered checks pass at that exact SHA:

```text
reference-integrity: SUCCESS
phase2-foundation:   SUCCESS
phase3-population:   SUCCESS
```

Final Phase-3 run:

```text
workflow run: 34437645424
job:          102745952311
status:       SUCCESS
```

Final diff sanity contains exactly 23 intended Phase-3 files and no temporary
workflow, marker, stale dependency report, or unrelated file. No scientific or
numerical tolerance was relaxed.

Detailed record: `phases/03_population.md`.

## Production repository state

### `darksirens-core`

`main` remains Phase 2 until PR #2 merges:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Phase 3 accepted head:

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

Squash-merge `ignaciomagana/darksirens-core#2` with expected head
`2461954c47df587ed70f711769a42779775be692`. Verify the merged core `main` SHA,
record it here and in `phases/03_population.md`, mark Phase 3 COMPLETE, and only
then start Phase 4.
