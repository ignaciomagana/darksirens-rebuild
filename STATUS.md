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
status:         5A + 5B ACCEPTED; 5C ORDINARY PRIOR/LIKELIHOOD COMPOSITION NEXT
core repo:      ignaciomagana/darksirens-core
phase-5 base:   0f97feff7eb283a1f541bef9a776c9347084e70e
working branch: rebuild/phase5-catalog-dark-bright
accepted 5A:    f418174a7fc8734bfbcf553d5b5c36f9f4280987
accepted 5B:    f4bc721496359f09fc58609fa23ccce21366f728
```

Phase 4 remains complete on `darksirens-core/main`. Phase 5A reconstructed the
standardized ordinary catalog runtime/compaction and observed-galaxy redshift
kernel. Phase 5B reconstructed the ordinary non-LSS completeness/count budget
and finite-depth behavior. Both have strict separate-process parity against the
pinned legacy implementation. Phase 5 as a whole is not complete.

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

PR `ignaciomagana/darksirens-core#2` was squash-merged.

```text
accepted branch head: 2461954c47df587ed70f711769a42779775be692
final phase3 run:     34437645424
phase3 job:           102745952311
squash-merge SHA:     e0b40fef65261a27b67aa9657a97216df3e8444f
core main:            e0b40fef65261a27b67aa9657a97216df3e8444f
```

Scientific acceptance:

```text
full reconstructed suite: 125 passed, 1 regen-only skip
legacy/new max_abs:        0
legacy/new max_rel:        0
comparison rtol:           1e-12
optional-dependency gate:  PASS
```

Detailed record: `phases/03_population.md`.

### Phase 4

PR `ignaciomagana/darksirens-core#3` was squash-merged after all exact-head
branch and PR gates passed.

```text
accepted branch head: cfdb138d40d66614bf9b1264c2574d0b497b812d
branch workflow run: 34445525661
branch job:          102769369532
squash-merge SHA:    0f97feff7eb283a1f541bef9a776c9347084e70e
verified core main:  0f97feff7eb283a1f541bef9a776c9347084e70e
post-merge reference run/job: 34447108888 / 102774202182 SUCCESS
```

Scientific acceptance:

```text
full reconstructed suite:               199 passed, 1 regen-only skip
dependency-boundary audit:              PASS
pinned legacy spectral probe:           PASS
reconstructed spectral probe:           PASS
legacy/new fixed-theta spectral parity: PASS
max_abs:                                0.000e+00
max_rel:                                0.000e+00
comparison rtol:                        1e-12
comparison atol:                        0
```

Detailed record: `phases/04_spectral_likelihood.md`.

### Phase 5A — catalog runtime + observed redshift kernel

Accepted on the still-open Phase-5 branch:

```text
accepted head:   f418174a7fc8734bfbcf553d5b5c36f9f4280987
workflow run:    34456764290
job:             102804866600
workflow result: SUCCESS
```

Scientific acceptance at the 5A checkpoint:

```text
catalog/compaction tests:                5 passed
catalog redshift + distance-table tests: 11 passed
full reconstructed suite:                215 passed, 1 regen-only skip
dependency/light-import audit:           PASS
pinned legacy catalog probe:             PASS
reconstructed catalog probe:             PASS
legacy/new catalog-kernel parity:        PASS
max_abs:                                 7.105e-15
max_rel:                                 9.229e-14
comparison rtol:                         1e-12
comparison atol:                         0
```

The strict probe caught a cached-evaluator numerical-semantic difference: the
mature legacy one-pass linear-domain sum underflows sufficiently remote Gaussian
tails to exact `-inf`, while the first reconstruction's log-space reduction kept
them finite. The candidate now reproduces the frozen legacy one-pass path; no
physical support threshold was invented.

After the 5B operation-order parity correction, the 5A catalog-kernel probe is
now exactly equal to frozen legacy (`max_abs=max_rel=0`).

Detailed checkpoint: `phases/05A_catalog_kernel.md`.

### Phase 5B — ordinary completeness + depth

Accepted on the still-open Phase-5 branch:

```text
accepted head:   f4bc721496359f09fc58609fa23ccce21366f728
workflow run:    34461981743
job:             102821696680
workflow result: SUCCESS
```

Scientific acceptance:

```text
Phase 5A compact tests:                  5 passed
Phase 5A redshift/distance tests:       11 passed
Phase 5B completeness/HLO tests:        11 passed
full reconstructed suite:              226 passed, 1 regen-only skip
dependency/light-import audit:          PASS
legacy/new 5A catalog-kernel parity:    PASS, max_abs=max_rel=0
legacy/new 5B completeness parity:      PASS, max_abs=max_rel=0
comparison rtol:                        1e-12
comparison atol:                        0
```

The 5B layer contains only the ordinary matched count-KDE/smoothing estimator,
expected-count grid, clipped differential completeness, missing-host count
budget, and finite-depth relaxation. The theta-independent observed KDE is a
separate `ObservedDensityCache`; proposal-dependent expected grids live in
`CompletionState`. `GalaxyCatalog` was not enlarged with cache/state.

A strict parity failure in near-zero retained fractions exposed a last-bit
operation-order difference in the already-owned galaxy measure. Candidate had
used `log(dV) + delta*log1p(z)`; frozen legacy forms
`log[dV * (1+z)^delta]`. Core now uses the exact frozen operation order. The
comparator was not loosened; final 5A and 5B parity are both exact zero.

Detailed checkpoint: `phases/05B_catalog_completeness.md`.

## Production repository state

### `darksirens-core`

Verified `main` remains:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

Phases 2, 3, and 4 are complete. Phase 5 is active on
`rebuild/phase5-catalog-dark-bright`; 5A and 5B are accepted subphase
checkpoints but are not merged separately.

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Frozen architecture direction for Phase 5

Core owns the standardized catalog runtime contract, generic catalog IO,
ordinary catalog redshift kernels/completeness evaluation, counterpart/host
objects, and complete/incomplete/bright-siren likelihood composition.

Core must not learn survey-native schemas or column names. Survey ingestion,
masks, depth maps, DESI/KIBO/Legacy/GLADE-specific construction and offline
selection-function fitting belong in `darksirens-surveys`.

Q_LSS/latent fields/multitracer auxiliary likelihoods remain for
`darksirens-lss`. Weak/strong lensing remains for `darksirens-lensing`.

The Phase-4 spectral likelihood remains a first-class catalog-free path; do not
bury it behind a giant `universe_model` dispatcher.

## Scientific questions

None opened. No scientific behavior change is authorized for Phase 5. Ordinary
complete/incomplete dark-siren and bright-siren behavior must be reproduced
against the pinned legacy implementation before API cleanup.

## 5C frozen facts

Read-only inspection of the pinned legacy source fixes the next composition:

```text
ordinary dark PE + selection:
    [N_obs p_cat(z|row) + dN_miss(z|row)] / [N_obs + N_miss]

complete occupied row:
    p_cat(z|row)

complete empty row:
    zero policy   -> -inf
    volume policy -> normalized comoving-volume prior

bright PE numerator:
    Normal(z; z_counterpart, dz_counterpart) * normalized volume prior
    with optional resolved-global-pixel gate

bright selection:
    normalized volume prior only
```

Ordinary dark and complete selection must use the same redshift/host model as
the PE numerator. Phase 4 already exposes the required redshift-prior callback
inside `log_sample_weight`; 5C must compose through that seam rather than copy
the legacy likelihood factory.

## Next action

Start 5C from exact accepted 5B head
`f4bc721496359f09fc58609fa23ccce21366f728`. Reconstruct the smallest explicit
ordinary catalog/counterpart prior states and hierarchical composition needed for
`plain_full`, `plain_compact`, `complete_zero`, `complete_volume`, and `bright`.
Use separate-process detailed legacy/candidate probes for event evidences, PE MC
variances, selection `log_mu`, `N_eff`, selection correction, and final
likelihood. Require `rtol=1e-12`, `atol=0` against the frozen legacy SHA before
starting 5D or any survey/LSS/lensing work.
