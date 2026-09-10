# Phase 5D2 checkpoint — generic magnitude-selection runtime

## Reference

```text
legacy repository:   ignaciomagana/darksirens
legacy SHA:          c042527238bd71421b792936bc48c3b815b90d6d
core repository:    ignaciomagana/darksirens-core
phase-5 branch:      rebuild/phase5-catalog-dark-bright
5D1 accepted head:   bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
first 5D2 candidate: b0fe30d889c3bee2284636c43b040f740f6b61ac
depth correction:   031f649f139a3bd2429a11053634a34cc3632a91
JIT-boundary fix:    df3ea207716928a8644060d83e1d8cd6f453d291
accepted 5D2 head:   9d5624864ce7467d309c45125cbe5785c671e1a9
```

Legacy remains read-only. Candidate and legacy parity probes run in separate
processes.

## Status

ACCEPTED AS A PHASE-5 SUBPHASE CHECKPOINT.

Exact-head CI at `9d5624864ce7467d309c45125cbe5785c671e1a9` passed the
complete Phase-5 branch workflow, including every historical reconstructed test,
the dependency/light-import audit, and all separate-process parity probes.

```text
workflow run: 34531001625
job:          103051412901
result:       SUCCESS
```

The comparison tolerance was not changed.

## Frozen ownership decision

5D2 reconstructs only the generic runtime evaluation of an already-standardized
magnitude-selection model. It does not move survey fitting into core.

Core owns:

```text
Gaussian C_sel(z; m_lim, M0hat, sigma_M, K(z))
Schechter C_sel(z; m_lim, Mstar_hat, alpha, M_faint_offset)
h-scaled magnitude convention / H0 firewall
runtime numerical/domain guards
ordinary missing-host budget formed from C_sel and the core expected-count model
small survey-independent serialized runtime contract
```

`darksirens-surveys` owns:

```text
raw apparent-magnitude columns
reference-magnitude construction for a survey catalog
SciPy MLE / optimization
Laplace covariance estimation
legacy/full fit JSON construction
fit-file background-cosmology provenance checks
survey-native K-correction choices
stratum-map construction
```

`darksirens-lss` owns every Q_LSS/Q-ensemble/latent/multitracer use of a
selection curve. 5D2 does not port the legacy field/global normalizer.

## Frozen scientific semantics

### Gaussian family

```text
M0 = M0hat + 5 log10(H0 / 100)
K(z) = sum_j c_j z^j       # no c0
C_sel = Phi[(m_lim - M0 - DM(z) - K(z)) / sigma_M]
```

`None`/empty K coefficients are bit-identical to K=0. `sigma_M` must be
strictly positive at standardized construction/load time.

### Schechter family

```text
Mstar = Mstar_hat + 5 log10(H0 / 100)
x_lim = 10^[-0.4 (m_lim - DM(z) - Mstar)]
x_faint = 10^[-0.4 M_faint_offset]
a = alpha + 1
C_sel = Gamma(a, x_lim) / Gamma(a, x_faint)
```

The implementation uses the frozen one-recurrence `a*Gamma(a,x)` spelling so
real faint-end slopes below -1 are legal. The pure runtime retains the frozen
last wall `alpha <= -2 -> NaN`; standardized runtime construction refuses that
domain before inference. `M_faint_offset` is a pinned protocol constant; finite
values must be greater than -7. Schechter + K(z) is refused rather than silently
dropping K. Schechter stratification is outside this slice.

### H0 firewall

At fixed h-scaled luminosity-function parameters the selection curve is
H0-invariant because the `+5 log10 h` absolute-magnitude shift cancels the
`-5 log10 h` luminosity-distance-modulus scaling.

This does not make the full missing-host budget H0-invariant. The ordinary
selection-mode missing density remains

```text
dN_miss = (1 - C_sel) * n0 * apix * dV_c/dz * (1 + z)^delta,
```

so its amplitude still scales as `n0 * H0^-3` at fixed background shape.

### Finite-depth state semantics

The frozen legacy state keeps the raw radial `C_sel(z)` curve available even
above `z_depth`. Depth affects the consumed missing-host budget instead:

```text
z <= z_depth: dN_miss = (1 - C_sel) dN_exp
z >  z_depth: dN_miss = dN_exp
```

Therefore `C_eff=0` above depth, while the raw diagnostic/state `C` remains
`C_sel`.

## Implemented core surface

```text
src/darksirens/selection/catalog.py
    GaussianMagnitudeSelection
    SchechterMagnitudeSelection
    selection_from_mapping / selection_to_mapping
    m0_absolute / k_of_z
    c_sel_gaussian / c_sel_schechter
    selection_curve
    selection_completion_curves

tests/test_catalog_selection.py
tools/probe_catalog_selection.py
.github/workflows/phase5-catalog-dark-bright.yml
```

`selection_completion_curves` reuses the already accepted core
`build_completion_state` expected-count state. There is no reconstructed
`SurveyParams.c_mode` switchboard.

The runtime serialization format is intentionally survey-independent and small:

```text
darksirens-catalog-selection-1.0
```

Survey covariance, optimizer information, raw columns and background/provenance
checks stay survey-side.

## Corrections found by strict parity

### Finite-depth raw-state correction

The first candidate zeroed the returned raw `C` above a finite `z_depth`.
Read-only inspection of frozen `_row_C` / `_assemble_curves` showed that legacy
leaves raw `C_sel` untouched and applies depth relaxation only to
`dN_miss/C_eff`. Commit
`031f649f139a3bd2429a11053634a34cc3632a91` restored that distinction.

### Compilation-boundary correction

The corrected depth candidate then passed all focused and historical tests but
missed the new strict comparator at at most

```text
max_abs = 7.276e-11
max_rel = 1.778e-11
rtol    = 1e-12
atol    = 0
```

The copied Gaussian/Schechter equations were not the problem. Frozen legacy
`c_sel_*`, `_precompute_grids` and `completion_curves` are plain JIT-compatible
functions whose compilation boundary is supplied by the enclosing likelihood.
The candidate had added a new inner `@threads_distance_table()` JIT boundary to
`selection_curve` / `selection_completion_curves`, changing XLA lowering of the
normal-CDF/incomplete-gamma tail arithmetic by a few ulps.

Commit `df3ea207716928a8644060d83e1d8cd6f453d291` removes that extra compilation
boundary while retaining explicit distance-table threading. Commit
`9d5624864ce7467d309c45125cbe5785c671e1a9` pins the intended contract in tests:
the public eager dispatcher is bit-identical to its family evaluator, and both
families remain valid when an enclosing JIT compiles the expression.

No scientific equation, prior, expected-count normalization or comparator
threshold was changed.

## Exact-head acceptance result

At accepted head `9d5624864ce7467d309c45125cbe5785c671e1a9`:

```text
lint / compile:                           PASS
5A compact tests:                         5 passed
5A redshift/distance tests:              11 passed
5B completeness/HLO tests:               11 passed
5C explicit hierarchy tests:              3 passed
5D1 marked-host tests:                    7 passed
5D2 catalog-selection tests:              9 passed
full reconstructed suite:               251 passed, 1 regen-only skip
dependency/light-import audit:           PASS
5A legacy/new catalog-kernel parity:     PASS, max_abs=max_rel=0
5B legacy/new completeness parity:       PASS, max_abs=max_rel=0
5C legacy/new likelihood parity:         PASS, max_abs=max_rel=0
5D1 legacy/new marked-host parity:       PASS, max_abs=max_rel=0
5D2 legacy/new selection parity:         PASS, max_abs=max_rel=0
comparison rtol:                         1e-12
comparison atol:                         0
```

## Phase-5 integration audit

The full Phase-4-main to accepted-5D2 diff is bounded to the Phase-5 surface:
ordinary catalog types/compaction/redshift/completeness/models/counterparts,
generic marks, generic catalog selection, explicit catalog/bright likelihood
composition, tests/probes and the permanent Phase-5 workflow. The only
pre-existing scientific source file modified is
`src/darksirens/likelihood/hierarchical.py`; its Phase-4 spectral likelihood is
retained, with the new ordinary paths added explicitly around it.

No survey/LSS/lensing/CLI/HEALPix dependency enters the core catalog/selection
runtime, and no raw survey schema or campaign state is present in the new core
surface.

## Next action

Open the single Phase-5 PR from exact accepted head
`9d5624864ce7467d309c45125cbe5785c671e1a9` to `main`, require the PR-triggered
historical and Phase-5 gates at that same head, then squash merge only if all are
green.
