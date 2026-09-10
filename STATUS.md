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
status: BRANCH ACCEPTED; PR REVIEW/MERGE NEXT
base repo:      ignaciomagana/darksirens-core
base SHA:       e0b40fef65261a27b67aa9657a97216df3e8444f
working branch: rebuild/phase4-spectral-likelihood
accepted head:  cfdb138d40d66614bf9b1264c2574d0b497b812d
```

The complete catalog-free spectral hierarchical likelihood and GW-selection
slice is green at the exact accepted branch head. Strict separate-process
legacy/new fixed-theta parity is exact at every serialized quantity. No Phase-5
work should begin until the Phase-4 PR is exact-head green, diff-reviewed,
squash-merged, and the resulting `main` SHA is verified and recorded.

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

Detailed record: `phases/03_population.md`.

## Phase 4 progress

The legacy likelihood package was not migrated file-for-file. The frozen core
boundary is:

```text
darksirens/likelihood/selection.py
    -> darksirens/selection/gw.py

darksirens/inference/utils.py likelihood math
    -> darksirens/likelihood/weights.py

darksirens/likelihood/events.py runtime event/padding logic
    -> darksirens/gw/{types,runtime}.py

catalog-free branch of darksirens/likelihood/core.py
    -> darksirens/likelihood/{event,hierarchical}.py
```

The accepted Phase-4 implementation contains canonical coordinate/Jacobian math,
runtime `GWEvent` construction and padding, per-sample importance weights,
selection `mu`/`N_eff`, total-likelihood-variance guards, soft-wall behavior,
gradient-safe reductions, normalized comoving-volume spectral redshift prior,
per-event evidence/MC variance, and the catalog-free hierarchical assembly.

Clean lower-level acceptance:

```text
core branch head: 220375e6877d755f34131d9d793ad4db38f0b89a
workflow run:     34441480533
job:              102757247600
result:           SUCCESS
```

Final branch acceptance:

```text
accepted branch head: cfdb138d40d66614bf9b1264c2574d0b497b812d
workflow run:         34445525661
job:                  102769369532
workflow result:      SUCCESS
```

Acceptance details:

```text
ruff F/E9 + compileall:                PASS
coordinate/runtime tests:             9 passed
GW-selection focused tests:            50 passed
spectral-likelihood focused tests:     15 passed
full reconstructed suite:              199 passed, 1 regen-only skip
dependency-boundary audit:             PASS
pinned legacy spectral probe:          PASS
reconstructed spectral probe:          PASS
legacy/new fixed-theta spectral parity: PASS
max_abs:                               0.000e+00
max_rel:                               0.000e+00
comparison rtol:                       1e-12
comparison atol:                       0
```

The separate-process parity fixture contains 3 PE events with 8 samples/event,
257 found injections, `Ndraw=4096`, nonuniform proposal weights, masked samples,
and a selection batch of 64. Three fixed `(H0, population)` points compare
per-event log evidence, per-event MC variance, `log_mu`, `N_eff`, selection
correction, and full spectral log likelihood. Every serialized value is exactly
identical between pinned legacy and reconstructed core.

One integration run caught only the already documented PE-block XLA
reassociation class: `1.66533454e-16` absolute / about `1.92e-13` relative in a
unit-test event-variance comparison. The pinned legacy test already uses
`rtol=1e-12, atol=0` for this block-shape comparison. Only the reconstructed
block unit test was aligned to that existing contract; the legacy/new scientific
parity gate was not relaxed and subsequently achieved exact equality.

Relative to Phase-3 `main`, accepted head `cfdb138d...` is 21 commits ahead and
0 behind. The branch diff is restricted to Phase-4-owned runtime,
likelihood/selection code, tests/probes, and the Phase-4 workflow.

Explicitly excluded from Phase 4 remain catalog KDE/completeness, survey
selection, Q_LSS/latent fields, marks, sky anisotropy, weak/strong lensing,
cluster/pair likelihoods, flow surrogates/pdet emulators, samplers, inference
prior transforms, and the old application CLI/`universe_model` dispatcher.

Detailed record: `phases/04_spectral_likelihood.md`.

## Production repository state

### `darksirens-core`

Current verified `main` before Phase-4 merge:

```text
e0b40fef65261a27b67aa9657a97216df3e8444f
```

Accepted Phase-4 branch:

```text
rebuild/phase4-spectral-likelihood
base:          e0b40fef65261a27b67aa9657a97216df3e8444f
accepted head: cfdb138d40d66614bf9b1264c2574d0b497b812d
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

None opened. Phase 4 reproduces the pinned legacy catalog-free spectral
likelihood without a scientific behavior change.

## Next action

Open the Phase-4 PR from `rebuild/phase4-spectral-likelihood` into `main` at exact
head `cfdb138d40d66614bf9b1264c2574d0b497b812d`. Require all relevant historical
PR workflows (`reference-integrity`, `phase2-foundation`, `phase3-population`)
plus the new Phase-4 workflow to pass at that exact head. Review the complete
diff for ownership or scientific-boundary violations, squash merge with an
expected-head guard, verify the resulting core `main`, record the merge here,
and only then begin Phase 5.
