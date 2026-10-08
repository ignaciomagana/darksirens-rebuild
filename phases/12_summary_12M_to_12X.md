# Phase 12 summary — what the DESI dark-siren H0 is made of (12M to 12X)

## Status

**SUMMARY RECORD (owner, 2026-10-08).** No new run. It ties together the
records 12M to 12X; each number below is taken from the record named beside
it.

## The result in one paragraph

On the 259 GWTC events with the fixed GWTC-5 population, the spectral-siren
analysis gives H0 = 64.5 [59.6, 69.6] km/s/Mpc. Adding the DESI catalog gives
about 70 [65, 76]. The difference does not come from the galaxies. The
catalog model multiplies the host density by (1+z)^δ and samples δ, and in
the volume the catalog does not cover this is a free redshift evolution of
the merger rate. A spectral-siren analysis with no catalog and the same
freedom gives H0 = 70.7 [65.1, 76.6]. The DESI catalog adds neither a shift
nor precision on this event set.

## The two numbers

| Analysis | H0 median [68%] | sd | Record |
|---|---|---|---|
| Spectral-only, rate index fixed at the GWTC-5 value (γ = 2.54) | 64.5 [59.6, 69.6] | 5.05 | 12T (corrected in 12X) |
| Spectral-only, rate index free (γ = 2.54 + δ, δ flat on [-3, 1.5]) | 70.7 [65.1, 76.6] | 5.77 | 12X |
| DESI union, calibration marginalized, count-ridge n0 prior | 70.1 [64.6, 75.5] | 5.52 | 12T |
| DESI spectroscopic part only (BGS Bright) | 70.3 [64.7, 76.1] | 5.65 | 12U |
| DESI photometric part only | 70.5 [65.2, 76.5] | 5.72 | 12U |
| DESI union, photometric kernels re-centred | 70.1 [64.6, 75.5] | 5.58 | 12U |

Every catalog analysis is no narrower than the catalog-free analysis with the
same freedom (5.5 to 5.7 against 5.77), and wider than the fixed-index one.

## How the explanation was reached

1. **The fixed calibrations disagreed (12M, 12R).**
   - The first result of record, 71.1 ± 4.5 at an earlier calibration and
     depth 0.3, was suspended (12M).
   - With the density calibration fixed at depth 0.245, H0 was 53.1 at the
     whole-window count fit (δ = +1.05) and 71.2 at the cross-check fit
     (δ = -2.57) (12R).
2. **Marginalizing the calibration gave about 69 to 70 (12S, 12T).**
   Sampling n0 and δ gave 69.4 [64.1, 74.8]. The n0 prior carried about
   1 km/s/Mpc (69.4 with a flat prior, 70.2 on the count ridge). The catalog
   depth moved H0 by 0.25. The posterior was no narrower than the spectral
   one.
3. **The offset is not a photo-z effect (12U).** Spectroscopic redshifts
   alone gave 70.3. Removing the smooth-prior pull on every photometric
   kernel moved the union by -0.05.
4. **The galaxies do not move H0 (12V, 12W).** With an empty catalog and
   every pixel completed, the likelihood at fixed calibration matched the
   union's to within 0.7 in log. Across δ from -3 to +1.5 the union and the
   empty catalog agree in H0 to within 0.5 km/s/Mpc.
5. **δ sets H0 (12W).** At fixed δ on the real union, H0 is 48.5 at
   δ = +1.5, 64.7 at 0, 70.5 at -0.84, and between 70 and 73 for every
   δ ≤ -0.8. The fixed calibrations of step 1 are two points of this curve.
6. **δ is the rate evolution (12X).** The empty-catalog likelihood equals
   the spectral-only likelihood with the rate index γ = 2.54 + δ, up to a
   constant (0.002 to 0.08 in log). With δ free and no catalog, H0 is
   70.7 [65.1, 76.6] and δ = -0.85 ± 0.32. The catalog chains found δ between
   -0.79 and -0.88.

## What the events say about the rate

- The events prefer a merger rate rising as (1+z)^(1.7 ± 0.3). The GWTC-5
  index of 2.54 is lower in peak log-likelihood by 3.3, and a free index is
  preferred by 1.7 in log evidence (12X).
- A shallower rate needs a larger H0: about -7 km/s/Mpc per unit of the
  index near the preferred value, steeper above the GWTC-5 value (12W, 12X).
- The galaxy counts do not fix δ. The union's count fit gives +1.05 over the
  whole window and -2.57 below z = 0.172; the spectroscopic part gives -0.13
  and the photometric part +1.54 (12U). The events disfavour both union
  values by about 12 in log-likelihood (12W).

## What was checked along the way

- **Calibration.** The union calibration reproduces the earlier one to 1e-7
  with the luminosity values held fixed. The photo-z inversion of the
  luminosity function carries Monte Carlo noise of about 1e-3 in its values
  (12U).
- **Count ridge.** The 12T ridge was an approximation that ignored the
  photo-z kernels, 0.009 dex off on the union at δ = -0.84. The 12U arms use
  the full recomputation (12U).
- **Photo-z centres.** Between z 0.08 and 0.22 the DESI Legacy photo-z are
  unbiased to within 0.002, while core's kernel moves each galaxy's mean
  redshift up by 0.006 to 0.008 (12U).
- **Convergence and guards.** Every chain converged, met its gate and has no
  posterior mass at a prior edge. No scan point was rejected (12T to 12X).
- **Correction.** 12T recorded the spectral-only median as 64.27
  [59.4, 69.4], half a grid step low. It is 64.52 [59.6, 69.6], as 12M and
  12R had it (12X).

## What this does and does not show

- It shows that, for this event set and catalog depth (z_depth 0.245), the
  dark-siren H0 is determined by the GW events and the assumed merger-rate
  evolution. The catalog term reduces to a rate-evolution parameter.
- It does not show that a galaxy catalog cannot inform H0. The mock campaign
  of the examples (150 events per realisation, catalog to z 0.95, 100
  realisations) has complete-catalog posteriors narrower than the spectral
  ones on the same events (sd 5.4 against 8.5). There the catalog covers the
  events' volume.
- The value of H0 quoted from a catalog analysis must state how the rate
  evolution is treated: 64.5 with the GWTC-5 index, 70.7 with it free.

## Owner decisions (2026-10-08)

1. **Phase 12 reports both values, side by side:** 64.5 [59.6, 69.6] with the
   GWTC-5 rate index and 70.7 [65.1, 76.6] with the index free, with the
   statement that the DESI catalog changes neither.
2. **δ will be fixed and the population's rate index freed instead.** The
   freedom then sits in one parameter, the one that carries it physically.
   This changes the catalog model, so it is declared before any run.
3. **A mock study will measure what limits the catalog's information:** a
   scan over catalog depth and event localisation on the existing mock
   universe, declared in the examples repository first.
