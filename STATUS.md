# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 5 — CORE CATALOG + DARK/BRIGHT SIRENS
status: NOT STARTED; CONTRACT REVIEW NEXT
base repo:      ignaciomagana/darksirens-core
base SHA:       0f97feff7eb283a1f541bef9a776c9347084e70e
```

Phase 4 is complete and verified on `darksirens-core/main`. Phase 5 must begin
only from the merge SHA above and only after rereading the control-plane
catalog/dark/bright-siren prompt, data contract, package boundaries, migration
policy, and validation contract. Do not recreate the legacy monolithic
`redshift`/`catalogs`/`likelihood.factory` architecture.

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

Scientific acceptance:

```text
full reconstructed suite: 125 passed, 1 regen-only skip
legacy/new max_abs = 0
legacy/new max_rel = 0
comparison rtol = 1e-12
ordinary population import leaves tinygp unloaded: PASS
```

Detailed record: `phases/03_population.md`.

### Phase 4

PR `ignaciomagana/darksirens-core#3` was squash-merged after the accepted branch
head remained unchanged through all historical and Phase-4 PR gates.

```text
accepted branch head: cfdb138d40d66614bf9b1264c2574d0b497b812d
branch workflow run: 34445525661
branch job:          102769369532

PR #3 exact-head workflows:
reference-integrity   run 34446633557  job 102772728746  SUCCESS
phase2-foundation     run 34446633595  job 102772729079  SUCCESS
phase3-population     run 34446633551  job 102772729151  SUCCESS
phase4-spectral       run 34446633527  job 102772728950  SUCCESS

squash-merge SHA:     0f97feff7eb283a1f541bef9a776c9347084e70e
verified core main:   0f97feff7eb283a1f541bef9a776c9347084e70e
post-merge reference: run 34447108888 job 102774202182 SUCCESS
```

Scientific acceptance:

```text
coordinate/runtime focused tests:          9 passed
GW-selection focused tests:                50 passed
spectral-likelihood focused tests:         15 passed
full reconstructed suite:                  199 passed, 1 regen-only skip
dependency-boundary audit:                 PASS
pinned legacy spectral probe:              PASS
reconstructed spectral probe:              PASS
legacy/new fixed-theta spectral parity:    PASS
max_abs:                                   0.000e+00
max_rel:                                   0.000e+00
comparison rtol:                           1e-12
comparison atol:                           0
```

The Phase-4 source/test/probe diff was reviewed before merge. No concrete catalog,
survey, LSS, lensing, flow, sampler, or CLI dependency entered the core spectral
likelihood/selection runtime. Component-spin runtime shape is separately pinned
by construction, padding, batched-selection, and population-forwarding tests.

Detailed record: `phases/04_spectral_likelihood.md`.

## Production repository state

### `darksirens-core`

Verified `main`:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

Phases 2, 3, and 4 are complete.

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Frozen architecture direction for Phase 5

Core may own the standardized catalog runtime contract, generic catalog IO,
ordinary catalog redshift kernels/completeness evaluation, counterpart/host
objects, and complete/incomplete/bright-siren likelihood composition.

Core must not learn survey-native schemas or column names. Survey ingestion,
masks, depth maps, DESI/KIBO/Legacy/GLADE-specific construction and offline
selection-function fitting belong in `darksirens-surveys`.

Q_LSS/latent fields/multitracer auxiliary likelihoods remain for
`darksirens-lss`. Weak/strong lensing remains for `darksirens-lensing`.

The Phase-4 spectral likelihood must remain a first-class catalog-free path; do
not bury it behind a giant `universe_model` dispatcher when adding catalog
composition.

## Architecture questions intentionally deferred

- minimal LSS redshift/auxiliary-likelihood protocol;
- minimal strong-lensing analysis protocol;
- exact optional flow API.

## Scientific questions

None opened. No scientific behavior change is authorized for Phase 5; ordinary
complete/incomplete dark-siren and bright-siren behavior must be reproduced
against the pinned legacy implementation before broader API cleanup.

## Next action

Read `prompts/06_core_catalog_dark_bright.md` plus the current control-plane
architecture/data-contract/validation documents. Reinspect the pinned legacy
catalog, redshift-prior/completeness, counterpart, and ordinary likelihood code
against the now-merged Phase-4 core. Freeze the smallest Phase-5 ownership map
and parity matrix, record it in a new phase report, then create the Phase-5 core
branch from exactly `0f97feff7eb283a1f541bef9a776c9347084e70e`.
