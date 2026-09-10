# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 4 — SPECTRAL-SIREN LIKELIHOOD + GW SELECTION
status: NOT STARTED
base repo: ignaciomagana/darksirens-core
base SHA:  e0b40fef65261a27b67aa9657a97216df3e8444f
```

Phase 3 is complete and recorded. Phase 4 must begin with inventory/parity
fixtures before scientific code is ported.

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

```text
core main after Phase 2: 450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
workflow run:            34431185197
job:                     102726848203
status:                  SUCCESS
```

The reconstructed package contains modern `src/darksirens` packaging,
side-effect-free root import, explicit JAX runtime configuration, flat-CPL
cosmology/shared redshift grids, standardized GW PE/selection store contracts,
`GWStore`/`SelectionStore`, PE/injection loaders, and current
`chieff_reference` selection support.

### Phase 3

PR `ignaciomagana/darksirens-core#2` was squash-merged at the exact accepted
head after all branch and PR checks passed.

```text
accepted branch head: 2461954c47df587ed70f711769a42779775be692
final phase3 run:     34437645424
phase3 job:           102745952311
reference-integrity:  SUCCESS
phase2-foundation:    SUCCESS
phase3-population:    SUCCESS
squash-merge SHA:     e0b40fef65261a27b67aa9657a97216df3e8444f
core main:            e0b40fef65261a27b67aa9657a97216df3e8444f
```

Scientific acceptance included:

```text
full reconstructed suite: 125 passed, 1 regen-only skip
legacy/new max_abs = 0
legacy/new max_rel = 0
comparison rtol = 1e-12
ordinary population import leaves tinygp unloaded: PASS
```

The PR-level Phase-2 lint check caught three unused imports in migrated tests;
only those imports were removed and the complete gate was rerun. No scientific
source or tolerance changed. Final diff sanity contained exactly 23 intended
Phase-3 files and no temporary reconstruction artifacts.

Detailed record: `phases/03_population.md`.

## Production repository state

### `darksirens-core`

Phases 2 and 3 are complete on `main` at:

```text
e0b40fef65261a27b67aa9657a97216df3e8444f
```

Current reconstructed areas: foundation/cosmology/GW stores and loaders,
population models including GP models. Catalog/redshift, hierarchical
likelihood, GW selection, samplers and the high-level `model/infer` API are not
yet migrated.

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

Start Phase 4 from core `main` SHA
`e0b40fef65261a27b67aa9657a97216df3e8444f`. First inventory the pinned-legacy
ordinary spectral-siren likelihood and GW-selection machinery, identify its
true core-owned tests and dependencies, and define separate-process parity
fixtures. Do not port catalog, LSS, lensing, sampler, or application-CLI code
until ownership is frozen.
