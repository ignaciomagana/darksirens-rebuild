# Phase 12X — spectral sirens with the rate evolution free (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any run. RESULTS appended below (2026-10-08).**
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

## Results (2026-10-08)

Twenty-two spectral-only grids (HENON job 1375896, 70 minutes, every run
accepted, no rejected H0 point). Outputs:
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12x/spectral/delta_<δ>/spectral_h0.json`;
the table below is also `phase12x/h0_vs_delta_spectral.json`.

### Controls

- **δ = 0 reproduces 12T.** The log-likelihood differs from the 12T
  spectral-only grid by at most 9e-13 over the 241 H0 values (median 64.52,
  mean 64.64, sd 5.05).
- **The empty catalog is the spectral analysis with γ = 2.5439 + δ.** The
  difference between 12V's empty-catalog log-likelihood and the spectral one,
  over the 19 shared H0 values, is constant to:
  - 0.002 at δ = 0;
  - 0.004 at δ = -0.84;
  - 0.08 at δ = +1.05.

### H0 at fixed δ

| δ | γ | spectral-only H0 [68%] | sd | peak logL | 12W union | union - spectral |
|---|---|---|---|---|---|---|
| -3.00 | -0.46 | 71.1 [65.7, 76.7] | 5.55 | -782.91 | 69.9 | -1.2 |
| -2.57 | -0.03 | 72.7 [67.2, 78.4] | 5.63 | -775.60 | 71.7 | -1.0 |
| -2.00 | 0.54 | 73.7 [68.2, 79.5] | 5.67 | -768.03 | 72.6 | -1.0 |
| -1.50 | 1.04 | 73.3 [67.9, 79.1] | 5.65 | -763.70 | 72.6 | -0.8 |
| -1.00 | 1.54 | 71.7 [66.3, 77.4] | 5.55 | -761.76 | 71.3 | -0.4 |
| -0.84 | 1.70 | 70.9 [65.6, 76.5] | 5.50 | -761.65 | 70.5 | -0.4 |
| -0.50 | 2.04 | 68.7 [63.5, 74.2] | 5.35 | -762.23 | 68.1 | -0.6 |
| 0.00 | 2.54 | 64.5 [59.6, 69.6] | 5.05 | -764.93 | 64.7 | +0.1 |
| +0.50 | 3.04 | 59.4 [54.8, 64.2] | 4.70 | -769.43 | 59.4 | 0.0 |
| +1.05 | 3.59 | 53.3 [49.2, 57.6] | 4.27 | -775.71 | 53.0 | -0.3 |
| +1.50 | 4.04 | 48.4 [44.4, 52.4] | 4.03 | -781.51 | 48.5 | +0.1 |

(The other eleven values of δ are in the JSON file.)

### Rate evolution free

With a flat prior on δ over [-3, 1.5], the chains' prior, and no catalog:

| | spectral-only, δ free (12X) | catalog chains (12T, 12U) |
|---|---|---|
| H0 median [68%] | 70.7 [65.1, 76.6] | 70.1 [64.6, 75.5] to 70.5 [65.2, 76.5] |
| H0 sd | 5.77 | 5.52 to 5.72 |
| δ | -0.85 ± 0.32 | -0.79 to -0.88 ± 0.33 to 0.35 |

The evidence prefers free δ to δ = 0 by 1.7 in log.

### Reading

1. **The catalog result is a spectral-siren result with free rate
   evolution.** Without any galaxy, freeing the rate index gives
   H0 = 70.7 [65.1, 76.6] and δ = -0.85 ± 0.32. The DESI chains gave
   70.1 to 70.5 and δ = -0.79 to -0.88.
2. **The offset from the fixed-population spectral result (64.5) is the
   rate index.** The events prefer a merger rate rising as (1+z)^(1.7 ± 0.3)
   to the GWTC-5 index of 2.54: the peak log-likelihood is higher by 3.3, and
   the evidence for a free index by 1.7 in log. A shallower rate needs a
   larger H0.
3. **The DESI catalog adds neither a shift nor precision on this event
   set.** At fixed δ the union and the spectral-only H0 agree to 0.1 to 0.6
   km/s/Mpc for δ ≥ -1. The union is lower by 0.8 to 1.2 for δ ≤ -1.5, where
   the events disfavour δ by 2 to 21 in log. Marginalized, the catalog chains
   are 0.2 to 0.6 below the spectral value and no narrower (sd 5.5 to 5.7
   against 5.77).
4. **Correction to earlier records.** The 12T table quotes the spectral-only
   median as 64.27 and its 68% interval as [59.4, 69.4]. The stored posterior
   gives 64.52 and [59.6, 69.6]; the mean (64.64) and sd (5.05) are as
   recorded. The 12T table is corrected in this change. The 12U and 12V
   records quote 64.27, so their "+6.0" offsets are +5.8 against the
   corrected median.
5. What the Phase 12 analysis should now report, and whether the rate index
   should be free in it, is the owner's decision.
