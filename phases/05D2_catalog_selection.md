# Phase 5D2 checkpoint — generic magnitude-selection runtime

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
phase-5 branch:    rebuild/phase5-catalog-dark-bright
5D1 accepted head: bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
```

Legacy remains read-only. Candidate and legacy parity probes must run in
separate processes.

## Status

IN PROGRESS.

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
```

`darksirens-surveys` owns:

```text
raw apparent-magnitude columns
reference-magnitude construction for a survey catalog
SciPy MLE / optimization
Laplace covariance estimation
fit JSON construction
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
strictly positive.

### Schechter family

```text
Mstar = Mstar_hat + 5 log10(H0 / 100)
x_lim = 10^[-0.4 (m_lim - DM(z) - Mstar)]
x_faint = 10^[-0.4 M_faint_offset]
a = alpha + 1
C_sel = Gamma(a, x_lim) / Gamma(a, x_faint)
```

The implementation uses the frozen one-recurrence `a*Gamma(a,x)` spelling so
real faint-end slopes below -1 are legal. `alpha <= -2` yields NaN at the
runtime wall. `M_faint_offset` is a pinned protocol constant; finite values must
be greater than -7. Schechter + K(z) is refused rather than silently dropping
K. Schechter stratification is outside this slice.

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
tests/test_completion_selection_mode.py
tests/test_selection_kcorr.py
tests/test_selection_schechter.py
```

The legacy `_precompute_grids` forms `dN_exp` exactly as the already-rebuilt
ordinary core path does, then places `C_sel` into the same global curve slot
consumed by every row. A concrete `z_depth` still means `C := 0` above the
depth, so the missing branch returns to the full expected count density there.

## 5D2 implementation shape

Do not resurrect the `SurveyParams.c_mode` switchboard in core. Add explicit
runtime objects/functions instead:

```text
selection/catalog.py
    standardized Gaussian/Schechter runtime models
    pure C_sel evaluation
catalog/completeness.py
    explicit selection-completeness assembly entry point
```

The ordinary per-pixel count-ratio entry point remains unchanged and is the
regression baseline.

## Acceptance gate

Required before marking 5D2 accepted:

```text
focused Gaussian runtime tests
focused Schechter runtime/domain tests
K(z) None/empty bit identity
Gaussian and Schechter H0-firewall tests
selection theta changes the ordinary missing budget
finite-depth selection budget behavior
full reconstructed regression suite
catalog/core dependency + light-import audit
separate-process legacy/candidate runtime probe
unchanged comparator: rtol=1e-12, atol=0
```

No tolerance widening and no scientific cleanup during parity reconstruction.
