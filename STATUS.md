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
status: INVENTORY / PARITY DESIGN IN PROGRESS
base repo:      ignaciomagana/darksirens-core
base SHA:       e0b40fef65261a27b67aa9657a97216df3e8444f
working branch: rebuild/phase4-spectral-likelihood
```

No Phase-4 scientific implementation is accepted yet. Ownership and parity
fixtures are being frozen before code is moved.

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

No scientific source or tolerance changed during final PR cleanup.
Detailed record: `phases/03_population.md`.

## Phase 4 inventory decisions so far

The legacy likelihood package is not being migrated file-for-file. The Phase-4
core boundary is:

```text
darksirens/likelihood/selection.py
    -> darksirens/selection/gw.py

darksirens/inference/utils.py likelihood math
    -> darksirens/likelihood/weights.py

darksirens/likelihood/events.py runtime event/padding logic
    -> reconstructed GW/likelihood runtime owner

catalog-free branch of darksirens/likelihood/core.py
    -> small spectral likelihood implementation
```

The reconstructed cosmology layer already provides `z_of_dL`, `dV_of_z`,
`ddL_of_z`, and precomputed variants, so Phase 4 will reuse those rather than
recreating legacy redshift/distance machinery.

Explicitly excluded from Phase 4: catalog KDE/completeness, survey selection,
Q_LSS/latent fields, marks, sky anisotropy, weak/strong lensing, cluster/pair
likelihoods, flow surrogates/pdet emulators, samplers, inference prior transforms,
and the old application CLI/`universe_model` dispatcher.

Focused legacy tests identified so far include likelihood-coordinate/Jacobian,
selection batching, selection gradient safety, N(N+3) correction coefficient,
total-likelihood variance guard, soft guard, selection consolidation, and spin
block plumbing. Separate-process fixed-theta spectral parity will compare
per-event evidence/variance, `log_mu`, `N_eff`, selection correction, and total
spectral log likelihood at `rtol=1e-12`, `atol=0` unless exact equality is
achieved.

Detailed record: `phases/04_spectral_likelihood.md`.

## Production repository state

### `darksirens-core`

Phases 2 and 3 are complete on `main` at:

```text
e0b40fef65261a27b67aa9657a97216df3e8444f
```

Phase 4 branch:

```text
rebuild/phase4-spectral-likelihood
base e0b40fef65261a27b67aa9657a97216df3e8444f
```

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

## Scientific questions

None opened. No scientific behavior change is authorized in Phase 4. The
reconstruction must reproduce the pinned legacy catalog-free spectral likelihood
before any later architecture is layered on top.

## Next action

Finish the exact Phase-4 unit-test/function inventory, freeze the deterministic
spectral parity fixture, then port the smallest catalog-free likelihood + GW
selection slice. Require the full reconstructed regression suite and strict
legacy/new parity before opening the Phase-4 PR.
