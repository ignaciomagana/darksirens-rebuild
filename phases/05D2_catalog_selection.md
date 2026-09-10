# Phase 5D2 checkpoint — generic magnitude-selection runtime

## Reference

```text
legacy repository:  ignaciomagana/darksirens
legacy SHA:         c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-5 branch:     rebuild/phase5-catalog-dark-bright
5D1 accepted head:  bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
first 5D2 candidate: b0fe30d889c3bee2284636c43b040f740f6b61ac
current 5D2 head:   031f649f139a3bd2429a11053634a34cc3632a91
```

Legacy remains read-only. Candidate and legacy parity probes run in separate
processes.

## Status

IN PROGRESS. Exact-head CI for `031f649f139a3bd2429a11053634a34cc3632a91`
is running. Nothing below is an acceptance claim until that run and the
separate-process parity gate are green.

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

`None`/empty K coefficients must be bit-identical to K=0. `sigma_M` must be
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

At fixed h-scaled luminosity-function parameters the **selection curve** must be
H0-invariant to the frozen numerical tolerance because the `+5 log10 h` in the
absolute-magnitude zero point cancels the `-5 log10 h` luminosity-distance
modulus scaling.

This does not make the full missing-host budget H0-invariant. The ordinary
selection-mode missing density is

```text
dN_miss = (1 - C_sel) * n0 * apix * dV_c/dz * (1 + z)^delta,
```

so its amplitude still scales as `n0 * H0^-3`. The legacy code explicitly
flags that this mode has no count-derived amplitude anchor. 5D2 preserves this
behavior; it does not reinterpret or repair the model.

### Finite-depth state semantics

The frozen legacy state keeps the raw radial `C_sel(z)` curve available even
above `z_depth`. Depth affects the **consumed** missing-host budget instead:

```text
z <= z_depth: dN_miss = (1 - C_sel) dN_exp
z >  z_depth: dN_miss = dN_exp
```

Therefore `C_eff=0` above the depth, but the raw diagnostic/state `C` remains
`C_sel`. This distinction is now pinned explicitly in candidate tests.

## Legacy anchors inspected

```text
darksirens/redshift/selection.py
    m0_absolute
    k_of_z
    c_sel_gaussian
    _a_off_zero
    _upper_gamma_scaled
    c_sel_schechter

darksirens/redshift/completion.py
    _decode_selection_family
    _precompute_grids selection branch
    _row_C C_bar_raw path
    _assemble_curves depth relaxation
tests/test_completion_selection_mode.py
tests/test_selection_kcorr.py
tests/test_selection_schechter.py
```

The legacy `_precompute_grids` forms `dN_exp` exactly as the already-rebuilt
ordinary core path does, then places `C_sel` into the same global curve slot
consumed by every row. Observed KDE/count-derived completeness is bypassed in
this mode.

## Implemented candidate shape

The implementation is intentionally explicit and leaves
`catalog/completeness.py` unchanged:

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

The core runtime serialization format is deliberately smaller than the legacy
survey-fit JSON:

```text
darksirens-catalog-selection-1.0
```

It contains only the quantities needed to evaluate the standardized runtime
curve. Survey covariance, optimizer information and background/provenance
checks stay survey-side.

## Candidate correction before acceptance

The first candidate commit
`b0fe30d889c3bee2284636c43b040f740f6b61ac` zeroed the returned raw `C` field
above a finite `z_depth`. Read-only inspection of frozen `_row_C` and
`_assemble_curves` showed that this was a state/diagnostic mismatch: legacy
leaves raw `C_sel` untouched and applies the depth relaxation only to
`dN_miss/C_eff`.

The correction commit
`031f649f139a3bd2429a11053634a34cc3632a91` removes that raw-C mutation and
changes the focused depth test to pin the frozen distinction. No selection
curve, expected-count physics, tolerance, or prior behavior changed.

## Acceptance gate

Required before marking 5D2 accepted:

```text
focused Gaussian runtime tests
focused Schechter runtime/domain tests
K(z) None/empty bit identity
Gaussian and Schechter H0-firewall tests
JIT dispatch for both runtime families
selection theta changes the ordinary missing budget
finite-depth raw-C versus consumed-budget behavior
explicit n0*H0^-3 amplitude check
full reconstructed regression suite
catalog/selection dependency + light-import audit
separate-process legacy/candidate runtime probe
unchanged comparator: rtol=1e-12, atol=0
```

No tolerance widening and no scientific cleanup during parity reconstruction.
