# Phase 09 S3 — offline magnitude-selection fitting

Status: **ACCEPTED (offline fit parity); exact installed-core replay remains an S6 integration gate**

## References

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core runtime:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
S0b golden:       references/surveys_s0b_selection_fit_reference.json
surveys repo:     ignaciomagana/darksirens-surveys
accepted S3 head: 4953bfdb2a71d8cfc2b0c748a9e187e826516ce6
accepted S3 tree: fdfc8c7d0123ece02cb45da9ab2baeb5a0ff548e
```

`darksirens-core` remains frozen. Runtime evaluation of the standardized
selection curves remains core-owned; S3 ports only the offline fit/build side.

## Scope

S3 adds the surveys-owned offline selection fitter:

```python
SelectionFit
fit_selection_from_mags(...)
fit_selection_strata(...)
reference_absolute_mags(...)
selection_fit_payload(...)
write_selection_fit(...)
```

Supported frozen families/conventions:

- upper-truncated Gaussian luminosity function;
- Schechter luminosity function in the alpha < -1 real-catalog regime;
- h-scaled reference magnitudes at `H0_REF=100`;
- fixed polynomial K(z) template for the Gaussian family;
- Gaussian multi-stratum fitting;
- covariance ordering in `SELECTION_SAMPLED_FIELDS`;
- legacy-compatible `darksirens-selection-fit-1.0/1.1` serialization.

The production fitter does **not** duplicate cosmology.  The `(m,z) -> Mhat`
conversion lazily imports the frozen core `distance_modulus` in the allowed
one-way direction `darksirens-surveys -> darksirens`. Importing the surveys
package itself remains JAX-free.

## S0b contract

The S0b reference was frozen with:

```text
numpy  1.26.4
scipy  1.12.0
jax    0.4.34
astropy 6.1.4
```

Representative frozen results include:

```text
Gaussian:
  M0hat   -20.19237712
  sigma_M   0.99178277551
  nll     3346.4622872

Gaussian + K(z):
  M0hat   -20.210929012
  sigma_M   1.0006223873
  nll     3320.1951416

K(z) ignored:
  M0hat shift = +0.12757647848 mag

Schechter:
  Mstar_hat      -19.782769362
  alpha           -1.1449313822
  M_faint_offset   5.0
  nll            2452.6984896
```

The S3 exact-head suite reproduces those MLEs/covariances with a test-only
NumPy spelling of the frozen fiducial distance-table slice. Because the real
core uses JAX `interpnd_scalar_head`, that test helper is not bit-identical to
the real consumer; tolerances are explicit and remain roughly 1e5--1e6 smaller
than the fitted Laplace standard deviations. The actual installed-core replay
is retained for S6 rather than copying more core cosmology into the companion
test harness.

## First candidate / harness classification

The first S3 test head was:

```text
4d0bcdb4abdf257a77dc73d5e43ca3e9a862aed2
run 34677087047 / job 103508749529 — FAILURE
17 passed, 4 failed
```

Install and compile succeeded. The four failures were all in the S0b comparison
harness:

1. one assertion rounded the generated anchor to 10 significant digits while
   comparing against the 11-significant-digit frozen reference;
2. the test-only NumPy distance interpolation differed from core's JAX
   interpolation at ~1e-9--1e-7 in fitted coordinates.

No S3 production file changed in the repair. Only `tests/test_selection.py`
was updated to use the correct anchor precision and explicit harness tolerances.

## Acceptance gate

```text
workflow:  ci
run:       34677186653
job:       103509022033
head:      4953bfdb2a71d8cfc2b0c748a9e187e826516ce6
result:    SUCCESS
pytest:    21 passed
firewall:  PASS
```

The accepted exact-head suite includes all S1 catalog and S2 depth-map parity
checks plus S3 Gaussian, K-corrected Gaussian, Schechter, h-scaled/H0 firewall,
strata/serialization and validation-wall tests.

## Dependency decision

SciPy is now a real surveys runtime dependency because the offline optimizer and
Schechter special functions are surveys-owned.  The S0b reference numerical
pair is pinned only in the test extra (`numpy==1.26.4`, `scipy==1.12.0`) so CI
does not confuse optimizer last-bit drift with migration changes.

No hard `darksirens-core` package dependency is declared yet because the sibling
repository is private and clean cross-private installation is part of S6. The
production fit raises a direct message if the core cosmology is unavailable at
fit time.

## Next slice

S4 is survey-native ingestion/adaptation into the already-frozen `CatalogRows`
contract.  Start with reusable normalized-column adapters and explicit weight /
quality-cut semantics; do not migrate DESI campaign scripts, LSS/Q builders, or
paper-specific paths.  Each survey adapter must terminate at S1's generic
pixelizer rather than implement another catalog writer.
