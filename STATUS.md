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
status:         5A + 5B + 5C + 5D1 ACCEPTED; 5D2 IN PROGRESS
core repo:      ignaciomagana/darksirens-core
phase-5 base:   0f97feff7eb283a1f541bef9a776c9347084e70e
working branch: rebuild/phase5-catalog-dark-bright
accepted 5A:    f418174a7fc8734bfbcf553d5b5c36f9f4280987
accepted 5B:    f4bc721496359f09fc58609fa23ccce21366f728
accepted 5C:    57af56158757ddd9272e0a2f2dc9bfbb624c1fec
accepted 5D1:   bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
```

Phase 4 remains complete on `darksirens-core/main`. Phase 5A reconstructed the
standardized ordinary catalog runtime/compaction and observed-galaxy redshift
kernel. Phase 5B reconstructed ordinary non-LSS completeness/count budget and
finite-depth behavior. Phase 5C reconstructed explicit incomplete-dark,
complete-catalog, and bright/counterpart likelihood composition. Phase 5D1
reconstructed generic marked-host weighting. Every accepted slice has
separate-process parity against the pinned legacy implementation. Phase 5 is not
yet merged; 5D2 and final Phase-5 integration remain.

## Completed phase heads

### Phase 2

```text
core main after Phase 2: 450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
workflow run:            34431185197
job:                     102726848203
status:                  SUCCESS
```

### Phase 3

```text
accepted branch head: 2461954c47df587ed70f711769a42779775be692
final phase3 run:     34437645424
phase3 job:           102745952311
squash-merge SHA:     e0b40fef65261a27b67aa9657a97216df3e8444f
core main:            e0b40fef65261a27b67aa9657a97216df3e8444f
```

Scientific acceptance: 125 passed, 1 regen-only skip; population legacy/new
parity `max_abs=max_rel=0` at `rtol=1e-12`, `atol=0`; optional-dependency gate
PASS. Detailed record: `phases/03_population.md`.

### Phase 4

```text
accepted branch head: cfdb138d40d66614bf9b1264c2574d0b497b812d
branch workflow run: 34445525661
branch job:          102769369532
squash-merge SHA:    0f97feff7eb283a1f541bef9a776c9347084e70e
verified core main:  0f97feff7eb283a1f541bef9a776c9347084e70e
post-merge run/job:  34447108888 / 102774202182 SUCCESS
```

Scientific acceptance: 199 passed, 1 regen-only skip; spectral fixed-theta
legacy/new parity exact (`max_abs=max_rel=0`, `rtol=1e-12`, `atol=0`). Detailed
record: `phases/04_spectral_likelihood.md`.

### Phase 5A — catalog runtime + observed redshift kernel

```text
accepted head:   f418174a7fc8734bfbcf553d5b5c36f9f4280987
workflow run:    34456764290
job:             102804866600
workflow result: SUCCESS
```

The strict probe caught a real numerical-semantic difference in remote Gaussian
tails; reconstructed code now reproduces frozen legacy's one-pass linear-domain
underflow behavior. After the later 5B operation-order correction, the 5A probe
is exactly equal to legacy (`max_abs=max_rel=0`). Detailed checkpoint:
`phases/05A_catalog_kernel.md`.

### Phase 5B — ordinary completeness + depth

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

A near-zero retained-fraction mismatch exposed the algebraically equivalent but
not bit-identical spelling `log(dV)+delta*log1p(z)` versus frozen legacy's
`log[dV*(1+z)^delta]`. Candidate now uses the exact frozen operation order; the
comparator was not loosened. Detailed checkpoint:
`phases/05B_catalog_completeness.md`.

### Phase 5C — explicit ordinary dark/complete/bright composition

```text
accepted head:   57af56158757ddd9272e0a2f2dc9bfbb624c1fec
workflow run:    34465661255
job:             102833519200
workflow result: SUCCESS
```

Scientific acceptance:

```text
Phase 5A compact tests:                    5 passed
Phase 5A redshift/distance tests:         11 passed
Phase 5B completeness/HLO tests:          11 passed
Phase 5C explicit hierarchy tests:         3 passed
full reconstructed suite:                235 passed, 1 regen-only skip
dependency/light-import audit:            PASS
legacy/new 5A catalog-kernel parity:      PASS, max_abs=max_rel=0
legacy/new 5B completeness parity:        PASS, max_abs=max_rel=0
legacy/new 5C detailed likelihood parity: PASS, max_abs=max_rel=0
comparison rtol:                          1e-12
comparison atol:                          0
```

The 5C detailed separate-process gate covers `plain_full`, `plain_compact`,
`complete_volume`, `complete_zero`, and `bright`, and compares event evidences,
PE MC variances, selection `log_mu`, `N_eff`, selection correction, assembled
likelihood, and final likelihood. Both implementations are additionally checked
against the immutable Phase-1 CPU K=1 bank. Detailed checkpoint:
`phases/05C_catalog_dark_bright.md`.

### Phase 5D1 — generic marked-host runtime

```text
accepted head:   bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
workflow run:    34498152895
job:             102941812699
workflow result: SUCCESS
```

Scientific acceptance:

```text
Phase 5D1 focused tests:                  7 passed
full reconstructed suite:              242 passed, 1 regen-only skip
dependency/light-import audit:          PASS
legacy/new 5A catalog-kernel parity:    PASS, max_abs=max_rel=0
legacy/new 5B completeness parity:      PASS, max_abs=max_rel=0
legacy/new 5C detailed likelihood parity: PASS, max_abs=max_rel=0
legacy/new 5D1 marked-host parity:      PASS, max_abs=max_rel=0
comparison rtol:                        1e-12
comparison atol:                        0
```

Core owns only the standardized centered mark table and generic log-linear host
runtime. Raw property loading and z-centering remain surveys. The first 5D1
parity run exposed a probe-fixture mismatch: the mature legacy factory computes
the marked prior on the compact PE/selection union rows, not all full-sky rows.
Only the probe was corrected; no scientific source or tolerance changed.
Detailed checkpoint: `phases/05D1_catalog_marks.md`.

## Production repository state

### `darksirens-core`

`main` remains the accepted Phase-4 merge:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

Phase 5 remains active on `rebuild/phase5-catalog-dark-bright`. 5A, 5B, 5C and
5D1 are accepted branch checkpoints but are intentionally not merged
separately. Exact current branch head at 5D2 start is the accepted 5D1 head
`bf45e0f5c0afc404d291d00a0ca267f8126b7e7b`.

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Frozen architecture direction for Phase 5

Core owns standardized catalog runtime/IO, ordinary catalog redshift kernels and
completeness evaluation, counterpart/host objects, generic host-property
weighting, runtime evaluation of ordinary serialized catalog-selection models,
and explicit spectral/dark/complete/bright hierarchical composition.

Core must not learn DESI/KIBO/Legacy/GLADE-native schemas, masks, depth-map
construction, raw magnitude preparation, or selection-function fitting; those
belong in `darksirens-surveys`.

Q_LSS, Q ensembles, latent fields/counts, multitracer machinery, and any
normalization intrinsically requiring those field quantities belong in
`darksirens-lss`. Weak/strong lensing belongs in `darksirens-lensing`.

The reconstructed source tree contains no `universe_model` dispatcher. The
Phase-4 spectral likelihood remains a first-class explicit path.

## Scientific questions

None opened. No scientific behavior change is authorized during Phase 5.

## Current action — 5D2

Start from exact accepted 5D1 head
`bf45e0f5c0afc404d291d00a0ca267f8126b7e7b` with read-only legacy inspection
first.

5D2 reconstructs only generic runtime evaluation of serialized non-LSS
magnitude-selection completeness. The admissible core slice is:

```text
Gaussian C_sel(z): h-scaled M0hat convention, sigma_M, optional structural K(z)
Schechter C_sel(z): h-scaled Mstar_hat, alpha, pinned M_faint_offset
H0 firewall: selection curve must be H0-invariant at fixed h-scaled LF params
runtime legality/domain guards required by those curves
ordinary per-row missing-host budget using the serialized runtime curve
```

The following remain outside core:

```text
SciPy/MLE/Laplace fitting
fit JSON construction and survey provenance
raw apparent-magnitude loading
survey column names, masks, depth maps and pixelization
stratum-map construction
Q_LSS/Q ensembles/latent fields/multitracer field normalization
```

Stratified or aggregate branches are not automatically part of 5D2. They move
only if they can be expressed as ordinary companion-free runtime state without
survey or LSS ownership leakage; otherwise they are explicitly deferred.

Acceptance requires focused runtime tests, exact H0-firewall tests,
separate-process frozen legacy/candidate probes at fixed coordinates, the full
historical reconstructed suite, dependency/light-import audits, and unchanged
`rtol=1e-12`, `atol=0`. After 5D2, run the exact-head full Phase-5 acceptance
matrix, audit the entire Phase-4-main -> Phase-5 diff, open a single Phase-5 PR,
require PR-head gates, and only then squash merge.
