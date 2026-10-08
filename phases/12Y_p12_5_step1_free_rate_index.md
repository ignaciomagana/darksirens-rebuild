# Phase 12Y — P12.5 step 1: the DESI chain with δ fixed and the rate index free (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any chain. Results will be appended here.**
The implementation and its CPU checks come first; the GPU chain is submitted
only after the owner's go.

## Where this sits

The Phase 12 contract (`12_production_analysis_contract.md`) has seven
steps. P12.4, the DESI comparison at a fixed population, is recorded in 12M to
12X and summarized in `12_summary_12M_to_12X.md`. P12.5 replaces the fixed
population by its uncertainty. This is its first step: one population
parameter, the merger-rate index γ, is sampled. The full marginalization is
scoped separately, and the owner decides it after seeing that scope.

## Why

12V to 12X found that the catalog model's host-density evolution δ acts as
free redshift evolution of the merger rate, and that this freedom, not the
galaxies, moves H0 from 64.5 to about 70. δ therefore duplicates the
population's rate index wherever the catalog is incomplete. The owner
decided to keep the freedom in one parameter, the one that carries it
physically: δ is fixed and γ is sampled.

## The model

P12.4 as in the 12T and 12U chains (the DESI union at nside 64, the LS
footprint, z_depth 0.245, exact-prior GW inputs, core e7c3007 with its
defaults, kernel pin off), with two changes:

| | 12T / 12U chains | this chain |
|---|---|---|
| δ | sampled, U[-3.0, 1.5] | fixed at 0 |
| γ | fixed at 2.5439 (GWTC-5) | sampled, flat on [-2, 6] |
| log10n0 | count ridge N(a + b δ, sd) | N(a, sd): the union's ridge at δ = 0, a = -1.810518, sd 0.036361, on [-2.346, -1.146] |
| M0hat, sigma_M | 12T priors | unchanged |
| effective-spin mean and width | 0.0633, 0.3654 | fixed at 0.04, 0.10 (amendment below) |
| the other 14 population parameters | GWTC-5 values | unchanged |

Sampled: H0, M0hat, sigma_M, log10n0, γ (five parameters, as before).
dynesty, nlive 1000, dlogz 0.1, seed 22.

The γ prior is wider than 2.5439 plus the old δ range, which would be
[-0.46, 4.04] (owner, 2026-10-08).

**The model is not identical to the 12T one.** With an empty catalog, δ = d
with γ fixed equals δ = 0 with γ = 2.5439 + d, up to a constant (12X). With
galaxies in the catalog the two differ: δ also tilts the catalogued hosts'
weights and the split between catalogued and completed hosts. The result can
therefore differ from the 12T and 12U chains by construction.

## Checks before the chain (CPU, HENON)

1. **Unit tests** of the change, including:
   - the new target at γ = 2.5439 and δ = 0 equals the existing target at
     δ = 0;
   - on a catalog with no galaxies, γ = 2.5439 + d with δ = 0 matches δ = d
     with γ fixed, up to a constant.
2. **Real-data equivalence.** A scan of the new target at γ = 2.5439 on the
   union reproduces the 12W scan at δ = 0, point by point.
3. **Real-data identity.** On the empty catalog of 12V, scans at
   γ = 2.5439 + d reproduce the 12V scans at δ = d (d = -0.84 and +1.05), up
   to a constant.
4. **The prior's edges.** Scans at γ = -2 and γ = 6 record the rejected H0
   points and the selection N_eff against its threshold. The owner sees them
   before the chain, because the selection guard has not been exercised that
   far from the GWTC-5 value.
5. A CPU smoke of the two production stages (an H0 scan, then the chain at
   nlive 8).

## What is reported

- The H0 posterior (median, 68%, sd), against:
  - the fixed-population union chain: 70.1 [64.6, 75.5] with δ free (12T);
  - spectral-only with the fixed index: 64.5 [59.6, 69.6];
  - spectral-only with the index free on the narrower range: 70.7
    [65.1, 76.6] (12X).
- The γ posterior, against 2.5439 and the 12X value of 1.7 ± 0.3; the
  fraction of samples near either edge of [-2, 6].
- The (log10n0, M0hat, sigma_M) posteriors against their priors.
- logZ, convergence, the gate, the selection N_eff at the posterior mean,
  and the scan's rejected points.

## Expectations, not thresholds

- H0 near 70 to 71 with γ near 1.7, as for spectral-only with the index
  free: the catalog added nothing at fixed δ in 12W and 12X.
- A posterior that piles up at an edge of the γ prior, or a guard that
  removes part of the prior, is reported as such and not interpreted.

## Amendment before the chain (owner, 2026-10-08): corrected spin, and the checks

**Spin.** Stage A0 (`12Z_p12_5_A0_population_sensitivity.md`) found that the
fixed population's spin pair (0.0633, 0.3654) are the GWTC-5 spin-magnitude
values, applied here to effective spin, and that the events reject them by
107 in log-likelihood. The owner decided to fix the spin at corrected values
and still sample only γ. A joint spectral-only scan of the effective-spin
mean (0 to 0.10) and width (0.06 to 0.14) has its best evidence at
**mean 0.04, width 0.10**: 110 above the old pair in peak log-likelihood, with
the neighbouring grid points 0.6 to 3.7 lower
(`phase12_5/A0/spin2d_summary.json`). These two values are fixed in this
chain. They come from this scan at otherwise fixed GWTC-5 values, not from an
external measurement.

**Reference values at the corrected spin** (spectral-only grids, 29 of 34
values of γ at the time of writing; `phase12_5/spectral_gamma/`):

| | old spin | corrected spin |
|---|---|---|
| H0, γ fixed at 2.5439 | 64.5 [59.6, 69.6] | 66.2 [61.4, 71.1] |
| H0, γ free | 70.7 [65.1, 76.6] | 67.9 [62.6, 73.5] |
| γ | 1.7 ± 0.3 | 2.22 ± 0.38 |
| ln evidence, free γ against 2.5439 | +1.7 | -1.2 to -1.8 |

With the corrected spin the events' rate index agrees with the GWTC-5 value,
and freeing it moves H0 by 1.7 km/s/Mpc, not 6. The expectations above are
superseded: this chain is expected near H0 = 68 with γ near 2.2.

**Checks, all done on CPU** (consumer branch `phase12.5/free-rate-index`):
1. Unit tests: 375 pass. With the spin override equal to the old values the
   target is the old one bit for bit; with γ = 2.5439 and δ = 0 it equals the
   existing target at δ = 0.
2. Real-data equivalence at the old spin: the scan at γ = 2.5439 equals the
   12W scan at δ = 0 exactly (37 H0 values).
3. Real-data identity on the empty catalog: γ = 2.5439 + d matches δ = d to
   1e-4 in log-likelihood (d = -0.84, +1.05), over a range of 20 to 26.
4. The spectral stage with the override reproduces the 12T grid (9e-13) and
   the A0 and joint-scan grids at the same spin values (0.0).
5. **The prior's edges.** At the old spin the guard rejected every H0 at
   γ = 6 and started at γ = 4.5. At the corrected spin, on the union:

   | γ | H0 values penalised (of 13) | selection N_eff / threshold |
   |---|---|---|
   | -2.0 | 0 | 7.1 to 10.6 |
   | 2.5439 | 0 | 17.2 to 34.4 |
   | 4.0 | 0 | 20.6 to 40.9 |
   | 5.0 | 0 | 22.5 to 31.0 |
   | 6.0 | 0 | 17.9 to 25.1 |

   The prior stays flat on [-2, 6]. The table is at the anchor calibration
   and luminosity values; other corners of the prior were not scanned.
6. CPU smoke of the two stages at the corrected spin: 0 failed stages.

The chain's starting H0 is still read from the 12T spectral grid (64.5). It
only starts the sampler, and the point was accepted in the smoke.
