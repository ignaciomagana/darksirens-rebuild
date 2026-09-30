# Phase 12S — P12.4 with the galaxy-density calibration marginalized: declaration

## Status

**DECLARED (owner, 2026-09-29) before any run. RESULTS appended 2026-09-30;
the owner decides what follows.** These are scratch runs on the consumer
branch `scratch/12s-marginalized`.

## Why

Phase 12R: with the recalibrated model, the catalog's H0 follows the smooth
density calibration. Whole-window and cross-check fits give 53.1 and 71.2 at
z_depth 0.245. The owner chose to sample the calibration instead of fixing
it.

## Target

P12.4 samples `(H0, M0hat, sigma_M, log10n0, delta)`:

- **log10n0:** h-scaled (`n0_units` "h_scaled", so n0 = 10**log10n0 (H0/100)^3
  at each proposal), uniform prior [-2.0, -1.6]. This spans the whole-window
  (-1.907) and cross-check (-1.723) fits with margin.
- **delta:** uniform prior [-3.0, 1.5], spanning 1.047 and -2.568.
- **M0hat, sigma_M:** normal priors N(-20.500, 0.199) and N(0.558, 0.130)
  (the 12P rule).
- **Anchor:** the P12.3 MAP H0, the LF prior means, and the whole-window
  (log10n0, delta).
- **Kernel pin:** "off", because delta is sampled; the marker records
  `{setting: off, active: false}`.
- **Fixed as before:** the population, the soft guard at cap 20, dynesty
  nlive 1000, dlogz 0.1, seed 22, core a935ef7, surveys 90f53a7, the 12K
  CUDA backend.
- **Test:** with the calibration sampled, the target equals the target with
  it fixed at the same values, to 1e-12 (consumer
  `tests/test_desi_target_jit.py`).

## Runs (declared)

```text
S1  z_depth 0.245   the depth the 12O criterion selects for the whole-window calibration
S2  z_depth 0.295   the only depth the criterion admits for the cross-check calibration
```

## What is reported

For each run:
- the H0 posterior;
- the (log10n0, delta) posterior, and whether it sits on either calibration
  or on a prior edge;
- the chain's gates.

No pass/fail threshold is set; the owner judges.

## Results (2026-09-30)

Both chains pass every stage. dynesty stopped on convergence: dlogz_final
0.09999 (S1) and 0.09995 (S2), against the 0.1 target. 12F gate 7 is met in
both. The soft guard penalises no point; the anchor N_eff is 7,224 (S1) and
7,149 (S2), 2.1 times the threshold.

Posterior medians with 68% intervals (90% for the calibration):

| | S1, z_depth 0.245 | S2, z_depth 0.295 |
|---|---|---|
| H0 | 69.4 [64.1, 74.8] | 69.2 [64.0, 74.6] |
| log10n0 | −1.82 [−1.93, −1.70], 90% [−1.97, −1.63] | −1.84 [−1.94, −1.72], 90% [−1.98, −1.65] |
| delta | −0.74 [−1.09, −0.38], 90% [−1.31, −0.15] | −0.70 [−1.06, −0.34], 90% [−1.30, −0.10] |
| M0hat | −20.50 ± 0.20 | −20.50 ± 0.20 |
| sigma_M | 0.56 ± 0.13 | 0.56 ± 0.13 |
| ln Z | −765.33 ± 0.07 | −765.77 ± 0.07 |

For comparison, at z_depth 0.245 (12R):

| Run | H0 |
|---|---|
| Whole-window calibration, fixed (A) | 53.1 [49.5, 57.3] |
| Cross-check calibration, fixed (B) | 71.2 [65.3, 75.6] |
| P12.3 spectral baseline | 64.5 [59.6, 69.7] |

**Findings:**

- **Depth.** With the calibration marginalized, H0 moves by 0.25 km/s/Mpc
  between the two depths, against a posterior std of 5.5. This is the
  question 12O left open.
- **delta.**
  - The data prefer delta ≈ −0.7 ± 0.36 at both depths.
  - The 90% interval excludes both fixed calibrations (+1.047 and −2.568).
  - It lies well inside the prior [−3.0, 1.5].
- **log10n0.**
  - The posterior std is 0.10 on a uniform prior of width 0.4 (a uniform
    distribution's std is 0.115), so the data constrain n0 only weakly.
  - The fraction of samples within 0.02 of the lower and upper edges is
    3.5% and 3.0% (S1) and 5.1% and 1.6% (S2); uniform would give 5% each.
    In S2 the lower edge is not suppressed, so the prior's lower bound
    matters there.
  - H0 follows n0 moderately: correlation 0.26 (S1) and 0.13 (S2).
  - The H0 median across thirds of the n0 range is 67.5 / 69.5 / 71.5 (S1)
    and 68.1 / 69.4 / 70.8 (S2).
  - So the n0 prior range carries about ±2 km/s/Mpc of the H0 result.
  - log10n0 and delta are anticorrelated (−0.62, −0.64).
- **Against the spectral baseline.** The catalog moves the H0 median by
  +4.9 (S1) and +4.7 (S2). The 68% width is 1.07 times the spectral one: after
  marginalizing the calibration, the catalog does not narrow H0.
- **Evidence.** ln Z differs by 0.45 between the depths, in favour of 0.245.
  Both use dynesty's default walk length. At 13-D that length was measured
  0.6–0.75 nat low on mocks (core #35); this target is 5-D.

**Incident (no effect on the posteriors).** The first attempt of each chain
sampled to convergence and then failed the P12.4 post-sampling check:
`unexpected dynesty sample array shape/content (N, 5)`. The scratch script
still required 3 columns.

- The fix (scratch commits 528d774 in S1 and 79323df in S2) compares against
  the sampled label count.
- Each chain was rerun with `DARKSIRENS_PHASE12_RESUME_FROM` on its own
  checkpoint, written 20 s before the failure. S1 resumed at iteration 6,799
  (116,059 calls), S2 at 6,940 (119,897 calls).
- The first-attempt logs, provenance and checkpoints are kept in
  `sensitivity_12r/S{1,2}_checkpoint_backup/`.

**Files** (under `/hildafs/projects/phy220048p/magana/darksirens-core-data/sensitivity_12r/`):
- `S1/results/phase12/fixed_population_desi_h0.json` (sha256 0eca0a649163baa3…);
- `S2/…` (79cd3e3a6415c17a…);
- the samples in each run's `samples_npz`;
- chain provenance `S{1,2}/provenance/fixed_population_chain.json`;
- logs `S{1,2}.resume.chain.out`.

**Input caveat.** Product A carries gwcat's interpolated chi_eff and
d_L priors: up to 8e-3 in ln p_pe per event and 1e-2 in ln pdraw per row
(measured by the gwpop-search session). gwcat #24 (merged, 8263ae9) now
evaluates them exactly. Product A was not rebuilt (owner, 2026-09-30), and the
effect on these posteriors was not measured.
