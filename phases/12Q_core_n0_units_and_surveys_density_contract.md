# Phase 12Q — package changes for the catalog recalibration: core n0 units, surveys density fit

## Status

**PROPOSED PACKAGE CHANGES (2026-09-29), from the owner's Phase 12P
decisions.** There are two PRs, each tested locally. Acceptance needs green CI
(core; surveys CI may be blocked by billing, private repository), merges, the
new pins, and the consumer's recalibration and repin (Phase 12R).

## darksirens-core: opt-in h-scaled log10n0 (PR ignaciomagana/darksirens-core#31)

- **What changes.** `model(..., n0_units="h_scaled")` for incomplete-catalog
  analyses reads `log10n0` as h^3 Mpc^-3. The binding then uses
  `n0 = 10**log10n0 * (H0/100)**3` (new `darksirens.catalog.physical_n0`), so
  the expected count n0 dV_c/dz (1+z)^delta is H0-independent at fixed
  background shape.
- **What does not change.**
  - `"physical"` (Mpc^-3 at the sampled H0, the frozen legacy convention)
    stays the default. Every decode is bit for bit unchanged, so every parity
    gate against the frozen reference is unaffected.
  - The plan's fingerprint block gains the key only when the setting is
    non-default, so every existing fingerprint is unchanged.
  - The kernel pin does not read n0.
- **Why** (Phase 12P):
  - The legacy DESI log10n0 was a closed-form ratio at H0 = 67.74 in Mpc^-3,
    held fixed while H0 is sampled. The expected counts then match the
    catalog only at 67.74, which manufactures a density-based H0
    constraint.
  - The DESI consumer's P12.4 target builds its own CatalogParameters and
    uses `physical_n0` directly. The binding change serves every other
    consumer.
- **Tests:**
  - New `tests/test_n0_units.py`, 13 tests: the default is bitwise; the
    h-scaled decode; the h-scaled likelihood equals the physical one at
    `log10n0 + 3 log10(H0/100)` to 1e-12; the fingerprint; the domain errors.
  - Full suite locally (CPython 3.11, jax 0.4.34, CPU): 978 passed, 1 skipped
    (the golden-regeneration guard).

## darksirens-surveys 0.2.0: density fit; survey-specific adapters out (PR ignaciomagana/darksirens-surveys#1)

- **New general module `darksirens_surveys.density`:**
  - `fit_density_selection`: an extended Poisson likelihood in fine bins of
    observed redshift for `log10n0hat` (h^3 Mpc^-3) and `delta`, optionally
    joint with the frozen conditional magnitude likelihood for `M0hat` and
    `sigma_M`. Details:
    - the survey area comes from the selection-fraction map;
    - the observed-z window is required;
    - the Gaussian (or K-mixture) redshift error is forward-modelled before
      the cut;
    - a `z_exact` mask handles mixed exact/scattered catalogs: the exact
      galaxies' histogram is subtracted from the true-z model before the rest
      are forward-modelled;
    - it returns a Laplace covariance.
  - `density_completeness_curve`, `gaussian_completeness`, and a
    density-fit payload in its own format; core's selection-fit formats are
    untouched.
- **Survey-specific schemas leave the package.** `DESI_LEGACY_RAW_COLUMNS`,
  `desi_legacy_rows` and `load_desi_legacy_hdf5` move to the DESI consumer
  (`phase12/desi_adapters.py`). `rows_from_hdf5(path, column_map)` is the
  general loader. The frozen public surface and the version (0.2.0) are
  updated.
- **Tests** (synthetic catalogs drawn from the model):
  - every parameter is recovered within 4 sd;
  - with a hard observed-z cut and 0.02 scatter, the forward model recovers
    n0hat and delta while the kernel-free fit does not;
  - mixed exact/scattered catalogs and width mixtures are recovered.
  - Full suite 50 passed; ruff clean; the root import still does not
    initialize core.

## Acceptance

1. Core PR #31: green CI and merge, giving a new core pin. Surveys PR #1:
   merge (with local stand-ins if Actions is blocked), giving a new surveys
   pin.
2. The consumer (Phase 12R):
   - repin both;
   - move the DESI adapters in;
   - run the calibration on the production sample and adopt its block
     (log10n0hat with n0_units h_scaled, delta, M0hat and sigma_M with the
     widened priors);
   - scale n0 by (H0/100)^3 in the P12.4 target.
3. Re-derive z_depth with the continuity criterion over the whole H0 prior
   range, then rerun the chain and the relevant 12N rows.
