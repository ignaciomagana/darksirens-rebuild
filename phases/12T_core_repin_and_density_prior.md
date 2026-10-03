# Phase 12T — P12.4 on current core: reproduction, the n0 prior, exact GW priors (declaration)

## Status

**DECLARED (owner, 2026-10-03) before any run.** Results will be appended
here. The owner decides what follows and which run, if any, becomes the
result of record.

## Why

12S (H0 69.4 [64.1, 74.8], z_depth 0.245) left three questions open:

1. **The n0 prior.** The prior range of log10n0, [-2.0, -1.6], carries about
   ±2 km/s/Mpc of H0. In S2 the lower edge was not suppressed.
2. **The catalog's information.** The catalog moves the H0 median by +4.9
   against the spectral baseline (64.5), but the width is 1.07 times wider.
3. **The GW input.** It still carries gwcat's interpolated chi_eff and d_L
   priors. gwcat 8263ae9 (#24) evaluates them exactly.

Since 12S, core has moved from a935ef7 to e7c3007. The speed defaults are
now on:
- the one-pass pairing scale and the per-point pairing normaliser;
- the galaxy list and the gathered missing density;
- the kernel window at 1e-10.

Each one falls back silently where it does not apply.

## Owner decisions (2026-10-03)

- **Code.** Consumer branch `phase12t/core-repin`. It is based on
  `phase12q/catalog-recalibration` plus the 12S marginalized sampling in
  clean form, repinned to core e7c3007. Surveys, lss and lensing keep their
  pins unless core requires otherwise.
- **Compute.** ONE rita A100 job that runs every stage sequentially. The
  second A100 stays free. Output goes under
  `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12t/`.
- **Seeds.** One seed (22) per chain. Everything else is fixed as in 12S:
  - z_depth 0.245;
  - LF priors N(-20.500, 0.199) and N(0.558, 0.130);
  - the soft guard at cap 20;
  - dynesty nlive 1000, dlogz 0.1;
  - kernel pin off;
  - the fixed GWTC-5 population.

## Priors on (log10n0 [h-scaled], delta)

| Name | log10n0 | delta |
|---|---|---|
| 12S | U[-2.0, -1.6] | U[-3.0, 1.5] |
| flat_wide | U[-2.4, -1.2] | U[-3.0, 1.5] |
| count_ridge | N(a + b·delta, s), truncated to [-2.4, -1.2] | U[-3.0, 1.5] |

**count_ridge.** For each delta, the catalog's total count fixes n0.

- **The ridge.** For each delta, log10n0 is the value whose expected count
  over [0.02, 0.30] equals the observed count. It is computed from the
  binned expected counts of the calibration's forward fit (calibration_12q
  run 2). It reproduces:
  - the whole-window fit (-1.9065 at delta 1.047) to 0.001 dex;
  - restricted to z < 0.172, the cross-check fit (-1.7229 at delta -2.568)
    to 0.014 dex.
- **The linear form.** a = -1.815898 and b = -0.084675, accurate to
  0.0019 dex over the delta prior.
- **The width.** s = 0.033846 dex: the rms of log10(observed/expected) over
  the 28 bins, i.e. the catalog's structure about one power law. The fit's
  statistical error (3e-4 dex) is negligible.

## Stages (in this order, one job)

1. **Parity.** Evaluate the P12.4 target at about 512 posterior points from
   12S S1 and about 64 prior points, including the prior edges, in three
   arms:
   - the old env at a935ef7;
   - core e7c3007 with the old settings stated explicitly;
   - core e7c3007 with the new defaults.

   Report |dlogL| and the importance-reweighted H0 median. Then a timing
   benchmark.
2. **Spectral-only H0 grid** (the P12.3 equivalent) on the current GW input,
   on core e7c3007.
3. Chain **repro_12S**: the 12S prior, new defaults. It is compared with
   69.4 [64.1, 74.8].
4. Chain **flat_wide**.
5. Chain **count_ridge**.
6. **Exact GW input.** The spectral-only grid, then chain
   **count_ridge_exactGW**, on GW input files rebuilt with gwcat 8263ae9.
   - The same build recipe, events, samples and injection rows.
   - Control: `--legacy-grid-priors` reproduces the current files.

## What is reported

For each chain:
- the H0 posterior and its width against the spectral-only grid;
- the (log10n0, delta) posterior;
- the fraction of samples near any prior edge;
- the chain's gates.

For the parity stage:
- the maximum |dlogL| of each arm;
- the reweighted H0 shift.

**Expectations, not thresholds.** With the old settings, the target should
equal a935ef7 to rounding. The new defaults should agree to well below the
sampler noise. No pass/fail threshold is set; the owner judges.
