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
status: LOW-LEVEL CORE GATE COMPLETE; SPECTRAL ASSEMBLY NEXT
base repo:      ignaciomagana/darksirens-core
base SHA:       e0b40fef65261a27b67aa9657a97216df3e8444f
working branch: rebuild/phase4-spectral-likelihood
accepted lower-level head: 220375e6877d755f34131d9d793ad4db38f0b89a
```

The Phase-4 coordinate/runtime/GW-selection slice is now green on a clean branch.
No catalog, LSS, lensing, sampler, flow, or application-factory code has been
pulled into the phase. The next slice is the catalog-free spectral hierarchical
likelihood plus strict separate-process parity against the pinned legacy SHA.

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

## Phase 4 progress

The legacy likelihood package is not being migrated file-for-file. The frozen
Phase-4 core boundary is:

```text
darksirens/likelihood/selection.py
    -> darksirens/selection/gw.py

darksirens/inference/utils.py likelihood math
    -> darksirens/likelihood/weights.py

darksirens/likelihood/events.py runtime event/padding logic
    -> darksirens/gw/{types,runtime}.py

catalog-free branch of darksirens/likelihood/core.py
    -> small spectral likelihood implementation under darksirens/likelihood/
```

The first implementation slice now contains the canonical coordinate/Jacobian
math, runtime `GWEvent` construction and padding, per-sample importance weights,
selection `mu`/`N_eff`, total-likelihood-variance guards, soft-wall behavior, and
gradient-safe reductions.

Clean lower-level acceptance:

```text
core branch head: 220375e6877d755f34131d9d793ad4db38f0b89a
workflow run:     34441480533
job:              102757247600
lint:             PASS
coordinate/runtime tests: PASS
GW-selection tests:       PASS
full reconstructed suite: PASS
dependency-boundary audit: PASS
workflow result:          SUCCESS
```

Two non-scientific issues were caught before this checkpoint: intended GW runtime
exports were missing from `__all__`, and one copied soft-guard test contained a
future `likelihood.factory` assertion. A temporary bootstrap workflow then raced
that cleanup and rewrote the test once; the bootstrap was deleted, the owner-local
test was restored, and the clean branch rerun above passed. No numerical behavior
or tolerance was changed.

Explicitly excluded from Phase 4 remain catalog KDE/completeness, survey
selection, Q_LSS/latent fields, marks, sky anisotropy, weak/strong lensing,
cluster/pair likelihoods, flow surrogates/pdet emulators, samplers, inference
prior transforms, and the old application CLI/`universe_model` dispatcher.

The reconstructed cosmology layer already provides `z_of_dL`, `dV_of_z`,
`ddL_of_z`, and precomputed variants. The spectral redshift prior will reuse
those primitives and add only the normalized comoving-volume density required by
the catalog-free likelihood.

Separate-process fixed-theta parity will compare:

```text
per-event log Z_i
per-event MC variance_i
log_mu
N_eff
selection correction
full spectral log likelihood
```

at `rtol=1e-12`, `atol=0` unless exact equality is achieved. Tolerances are not
to be relaxed to make the phase pass.

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
current accepted lower-level head 220375e6877d755f34131d9d793ad4db38f0b89a
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

Implement the smallest catalog-free spectral-redshift prior and hierarchical
likelihood assembly around the already-accepted weight/selection primitives.
Add deterministic separate-process legacy/new probes at several fixed `(H0,
population)` points, require `rtol=1e-12`, `atol=0`, then rerun the full Phase-4
gate before opening a PR.
