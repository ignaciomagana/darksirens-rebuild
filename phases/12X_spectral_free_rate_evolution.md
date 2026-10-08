# Phase 12X — spectral sirens with the rate evolution free (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any run. Results will be appended here.**
CPU likelihood grids only; no chain, no catalog and no GPU job.

## Question

Phases 12V and 12W found that the catalog analyses' H0 of about 70 comes
from the host-density evolution δ, sampled on U[-3, 1.5], and not from the
galaxies. In the completed volume, (1+z)^δ multiplies the merger rate, which
the fixed GWTC-5 population already evolves as (1+z)^γ with γ = 2.5439. If
that reading is right, the spectral-only analysis must give the same H0 once
its own rate index is shifted by δ, and about 70 once the index is free.

## What is run

`scripts/phase12t_stage.py spectral` on HENON CPU: the spectral-only grid of
12T (H0 from 20 to 140 in steps of 0.5, exact-prior GW inputs, consumer
ab226d6, core e7c3007 with its defaults).
- **Population:** `gwtc5_fiducial_bpl2peaks` with every parameter at its
  GWTC-5 value, given as an explicit mapping, and the rate index set to
  γ = 2.5439 + δ.
- **δ:** -3.0 to +1.5 in steps of 0.25, plus -2.57, -0.84 and +1.05: the δ
  prior of the chains, the 12W values and the chains' posterior mean
  (22 values; γ from -0.456 to 4.044).

Outputs go to
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12x/spectral/`.

## Controls

- **δ = 0** must reproduce the 12T spectral-only grid (median 64.27, mean
  64.64, sd 5.05) with the population given as a mapping instead of the
  preset.
- **Identity with the empty catalog.** At δ = 0, -0.84 and +1.05 the
  log-likelihood as a function of H0 is compared with 12V's empty-catalog
  scans at their shared H0 values. If δ is only a rate-evolution term, the
  two curves differ by a constant.

## What is reported

- For each δ: the H0 posterior (median, 68% interval, sd) and the peak
  log-likelihood, next to the 12W union value at the same δ.
- With a flat prior on δ over [-3, 1.5], the chains' prior:
  - the marginal H0 posterior, compared with the catalog chains
    (70.1 [64.6, 75.5]);
  - the posterior of δ, compared with the chains' -0.85 ± 0.35;
  - the evidence ratio between free δ and δ = 0.

## Expectations, not thresholds

- The spectral H0 at each δ matches the 12W union value to within the
  0.5 km/s/Mpc found there.
- Marginalized over δ, the spectral-only H0 is about 70, with δ near -0.85.
  If so, the catalog result is a spectral-siren result with free rate
  evolution, and the DESI catalog adds neither a shift nor precision on this
  event set.
- If the marginal spectral H0 stays near 64, the reading of 12V and 12W is
  wrong and the catalog term does more than change the rate evolution.
