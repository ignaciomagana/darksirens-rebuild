# Phase 12W — H0 against the host-density evolution δ on the real union (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any run. Results will be appended here.**
CPU likelihood scans only; no chain and no GPU job.

## Question

Phase 12V showed, on an empty catalog, that δ sets H0: about -6.7 km/s/Mpc
per unit of δ, with δ = 0 reproducing the spectral-only result. The chains
of 12T and 12U sample δ on U[-3, 1.5], and the GW events pull it to
-0.85 ± 0.35. How does H0 depend on δ with the real DESI union in place, and
where do the values the galaxy counts prefer fall on that curve?

## Why a grid and not a count-based prior

The owner asked for H0 under a δ prior taken from the counts. The counts do
not give one value. The union's calibration (12U) measures:
- δ = +1.05 from the whole window [0.02, 0.30];
- δ = -2.57 from z ≤ 0.172 (the cross-check fit).

The two differ by 3.6, with statistical errors near 0.001, so a single power
law does not describe the counts and a count-based prior is not defined. The
grid shows H0 at both values and at everything between (owner, 2026-10-08).

## What is run

`scripts/phase12u_stage.py scan` on HENON CPU, one job per δ.
- **Target:** P12.4 as in the 12U chains: consumer ab226d6, core e7c3007 with
  its defaults, exact-prior GW inputs, z_depth 0.245.
- **Catalog and footprint:** the standardized union
  (`phase12u/inputs/catalogs/desi_union_nside64.h5`) and the LS map.
- **δ:** -3.0, -2.57, -2.5, -2.0, -1.5, -1.0, -0.84, -0.5, 0.0, +0.5, +1.0,
  +1.05, +1.5. These are the prior range in steps of 0.5, plus the two count
  fits and the chains' posterior mean.
- **log10n0:** on the union's count ridge at each δ,
  -1.810518 - 0.089449 δ (12U, full recomputation).
- **Luminosity values:** the 12T anchor (M0hat -20.4997, sigma_M 0.5575).
- **H0:** 30 to 120 in steps of 2.5 (37 points).

Outputs go to
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12w/scans/`.

## What is reported

For each δ:
- the H0 posterior from the scan's log-likelihood with a flat prior on
  [30, 120]: median, 68% interval and sd;
- the number of rejected points and the selection N_eff range.

Across δ:
- the slope dH0/dδ;
- H0 at the two count fits and at the chains' δ;
- the difference from the empty-catalog scans of 12V at δ = 0, -0.84 and
  +1.05, which is the galaxies' contribution.

## Limits, stated in advance

- Each scan is at fixed calibration: the luminosity values are not
  marginalized, and n0 is on the ridge, not spread about it. 12V found the
  union's likelihood within 0.7 in log of the empty catalog's at fixed
  calibration, so these are expected to matter little. If the union scans
  differ from the empty-catalog ones by more than that, chains at pinned δ
  are the follow-up, and the owner decides.
- The posterior for the lowest δ may run into the upper edge of the H0 grid;
  if more than 1% of its mass lies within 5 of an edge, the grid is extended
  and the scan repeated.

## Expectations, not thresholds

- δ = 0: 64.5 ± 5.0, the spectral-only result.
- δ = -0.84: about 70 to 71, the chains' result.
- δ = +1.05 and -2.57: about 54 and about 82.
