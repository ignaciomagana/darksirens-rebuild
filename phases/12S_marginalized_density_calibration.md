# Phase 12S — P12.4 with the galaxy-density calibration marginalized: declaration

## Status

**DECLARED (owner, 2026-09-29) before any run.** These are scratch runs on the
consumer branch `scratch/12s-marginalized`. Results are appended below.

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
