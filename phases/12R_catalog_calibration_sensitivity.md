# Phase 12R — recalibrated catalog: H0 sensitivity to the calibration (scratch runs)

## Status

**FINDING (2026-09-29), for the owner.** These are scratch runs, not
production: scratch branch `scratch/12r-sensitivity` of the consumer, not
for merge. No result of record exists; 12M stays suspended and 12O
provisional.

## Calibration (Phase 12P decisions, surveys 0.2.0 fit)

Production sample: quality cut, 12I mask, the f_p map; Om0 0.3089; h-scaled.
Record: `darksirens-core-data/calibration_12q/calibration_12q_run2_invertedLF.json`
(sha256 91e7a77a394fe604).

- **Luminosity function.** The fit on observed z gives -20.309, 0.714; the
  north/south offset is 0.054 mag. A mock with the catalog's own
  spectroscopic/photometric mix (27% exact) shows that fit is photo-z biased
  by +0.197 in M0hat and +0.130 in sigma_M. Inverted with common random
  numbers, converged in 3 iterations: true **M0hat -20.500, sigma_M
  0.558**. The prior widths follow the owner's rule, hypot(half the
  north/south offset, the mock bias): 0.199 and 0.130.
- **Density**, with the LF corrected and the forward model (5-component
  ZERR mixture, spectroscopic galaxies exact):
  - over the whole window [0.02, 0.30] (A): **log10n0hat -1.9065, delta
    1.047**;
  - the cross-check over [0.02, 0.172] (B): **-1.7229, -2.568**.
  - The statistical sd on delta is 0.004. The observed/expected residuals
    are +7 to +18% at z < 0.13, -5 to -8% at 0.15-0.23, and about +6% at the
    edge: structure that one power law in (1+z) does not follow. At the 0.3
    edge the model now matches within about 6%; the legacy calibration gave
    0.35-0.47 of the expected density there.

## Runs

Consumer scratch `8cd1ddb` plus the surveys required-symbol fix; core
`a935ef7` and surveys `90f53a7` (installed from git); 12K CUDA backend,
MIKO H100; n0_units "h_scaled"; z_depth 0.245. Both full chains pass,
converge (final dlogz 0.1) and meet 12F gate 7.

```text
calibration                    H0 median   68%              sd     MC variance at centre   result json
A  whole window (delta 1.05)     53.08     [49.46, 57.28]   4.08        11.6               1e6a2fd12afaa11e
B  cross-check (delta -2.57)     71.15     [65.33, 75.57]   5.15         3.2               b2d74836d549f168
reference: catalog-free 64.52 [59.63, 69.65]; legacy calibration at z_depth 0.245 (12O) 68.06 [64.47, 72.57]
```

The 12O continuity criterion, now with h-scaled n0:
- The jump at the cut is exactly H0-independent (identical at H0 60, 67.74
  and 80 for every depth), as expected, since E, Cbar and the galaxy term are
  all H0-free.
- A admits z_depth 0.21 to 0.245, so 0.245 is A's criterion depth.
- B admits only 0.295 (jumps of +31 to +37% below it). B at 0.245 violates
  its own criterion.

## Finding

At the fixed population, the catalog's H0 follows the smooth
expected-density calibration. Two fits of the same catalog, each reasonable
over its own window, give H0 of 53 and 71: a spread of 18, about 4 sd. The
catalog carries plus or minus 10-20% structure against any single power law,
so the missing-host budget's shape, not the galaxies' positions, sets the
catalog's pull (see also 12N: the angular and radial shuffles leave it
unchanged).

## Options (the owner's decision)

- Marginalize n0 and delta in P12.4, with priors spanning the calibrations.
- An empirical, catalog-shaped expected density (a core change).
- A more flexible n(z) model.
- Report the dark-siren result as calibration-limited.
