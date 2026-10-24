# 12AI — Fiducial resolution near sigma_kde 3e-3: a convergence scan at nside 64 and 128

## Status

**RESULTS (2026-10-19, 11:02 UTC):** see "Results" at the end: fiducial candidate sigma_kde 3.5e-3 by the declared rule, with observations. **DECLARED (owner approval, 2026-10-19 about 11:00 UTC), before any 12AI grid.** No 12AI likelihood has been
evaluated. This record fixes the cells, the inputs, the criteria and the readings before anything runs.

**Blinding: location-free**, as in 12AG and 12AH. No H0 value appears here, in commit messages or in PR text. The
only H0 values in this record are fixed a priori: the grid [20, 140] at step 0.5, and the window [50, 90].

## Why

The 12AG ladder moved the width ratio R from 0.94 to 1.19 across nside × sigma_kde. When the owner looked at the
posteriors, two things stood out:

- **Small kernels are spiky.** At sigma_kde ≤ 1e-3 the catalog log-likelihood is rough point to point: 0.1 to 1.3
  nat, against 0.01 for spectral only. The spikes are about one grid step wide.
- **3e-3 is smooth but not converged in nside.** At sigma_kde 3e-3 every nside is smooth (0.05 to 0.07 nat). The
  catalog sharpens the main peak and adds structure on its high side. But nside 64 → 128 changes the posterior by a
  Hellinger distance of 0.053, most of the catalog's whole effect at nside 64 (0.064 from spectral only).

The owner asked for:
- more scans at nside 64 and 128 near sigma_kde 3e-3;
- a convergence criterion, stated and applied to the existing table before any run;
- tolerances: "Looser distance" (Hellinger ≤ 0.05);
- scope: "Grids only first" (half-sample runs later).

## Cells

The sigma_kde chain at nside 64 and at nside 128 is:

1.5e-3, 2e-3, 2.5e-3, **3e-3**, 3.5e-3, 4e-3, 5e-3, 7e-3, **1e-2**

- **Reused:** the bold values are 12AG's grids.
- **New:** the other seven at each nside, so 14 new grids.
- **Context only:** 12AG's 1e-3 cells are reported but are not on the chain.

Everything else is 12AG's ladder setting, unchanged:
- **Grid:** the 241-point exact grid [20, 140] at step 0.5.
- **Calibration:** log10 n0 −1.8216, M0hat −20.4975, sigma_M 0.5592, delta 0.
- **Model:** the population fixed as in the spectral-only reference; the selection guard (soft, variance limit 20);
  core e7c3007.

**Inputs** (sha256 prefix):

| Input | sha256 |
|---|---|
| catalog, nside 64 (production file) | c2d1ff36567419e4 |
| catalog, nside 128 (12AG build) | f26a20f0f3f8ca5a |
| footprint (nside 128) | 1e4e5c675dd59ab2 |
| PE (259 events × 4096) | c61507251609cb69 |
| injections | 56e51af209c99905 |

**Driver.** Each grid runs with `phase12ah_a_scan.py`. That is 12AG's grid driver plus each event's log evidence
(`events.npz`), so the per-event comparison of nside 64 and 128 needs no rerun.

## Convergence criteria (fixed now)

**Per cell, "can we trust this grid":**

- **N1:** the maximum total Monte-Carlo variance (PE plus selection) inside the cell's 90% interval is ≤ 1.2.
  Spectral only is 0.91, so the catalog may add at most about 0.3. LVK's cap is 1.0, and the owner chose 1.2.
- **N2:** roughness ≤ 0.1 nat. Roughness is the rms of the point-to-point second difference of ln L(catalog) − ln
  L(spectral only), over H0 in [50, 90].
- **N3:** half-sample stability. Deferred to a later amendment at the owner's request.

**Between neighbours that both pass N1 and N2, "the setting no longer matters":**

- **C1:** the Hellinger distance between the two posteriors is ≤ 0.05. For Gaussians that is a shift of 0.14
  spectral sd or a 10% width change.
- **Neighbours:**
  - consecutive sigma_kde on the chain at one nside;
  - nside 64 against 128 at one sigma_kde.

**Readings:**

1. **Per nside:** the C1 verdict for every consecutive pair of passing cells.
2. **Per sigma_kde:** "nside-converged" when 64 against 128 passes C1.
3. **Fiducial candidate:** the smallest sigma_kde on the chain where all of these hold:
   - both nsides pass N1 and N2;
   - 64 against 128 passes C1;
   - at both nsides, the pair (this sigma_kde, the next larger) passes C1.

   If no sigma_kde qualifies, the reading is "none within tolerance".
4. **Until N3 runs**, a C1 failure is not attributed either to Monte-Carlo noise or to a real resolution dependence.

Also reported for every cell: R, the sd ratio, Delta in spectral sd, and the Hellinger distance from spectral only
(the size of the catalog's effect). The per-event sum (Σ ln Z_i + core's selection correction = ln L, to 1e-9) is
checked on every new cell.

### The existing table under these criteria (before any 12AI run)

| Cell | Max total MC variance in 90% | Roughness (nat) | Passes N1 and N2 | Hellinger from spectral |
|---|---|---|---|---|
| (64, 1e-3) | 1.12 | 0.17 | no (N2) | 0.122 |
| (64, 3e-3) | 1.02 | 0.05 | yes | 0.064 |
| (64, 1e-2) | 0.96 | 0.05 | yes | 0.029 |
| (128, 1e-3) | 1.38 | 0.24 | no | 0.139 |
| (128, 3e-3) | 1.13 | 0.06 | yes | 0.098 |
| (128, 1e-2) | 1.00 | 0.05 | yes | 0.020 |

**C1 on the existing pairs:**

| Pair | Hellinger | C1 |
|---|---|---|
| 64 against 128, at 3e-3 | 0.053 | fails |
| 64 against 128, at 1e-2 | 0.017 | passes |
| nside 64, 3e-3 against 1e-2 | 0.062 | fails |
| nside 128, 3e-3 against 1e-2 | 0.094 | fails |

The 1e-2 column converges in nside, but the catalog does little there. With the existing cells, no fiducial
candidate qualifies.

## Compute

Fourteen grids, one nside-128 and one nside-64 grid per lane, on seven lanes:
- rita0 and rita1 (A100-80);
- twig0 to twig3 (A100-40);
- the free henon-gpu card (A100-40).

nside 128 peaked at 25 GB on twig in 12AG.

Every job requests its partition's maximum time. The summary runs on HENON CPU after all lanes (afterany) and
always writes `summary/STATUS.json`.

**Estimate:** about 10 to 15 minutes from submission if the cards are free, and about 20 minutes with the summary.

**Code:** consumer branch `phase12ai/fiducial-near-3e-3`, from 12AH's bf57e31:
- `scripts/phase12ai_plan.py`
- `scripts/phase12ai_summary.py`
- `slurm/phase12ai_*`
- `tests/test_phase12ai.py`

The commit that runs is 9827e3c (pushed before submission).

**Outputs:** under `phase12_5/fiducial_resolution/`:
- `runs/<cell>/` (scan.json and events.npz, not for agents);
- `summary/summary.json` (location-free);
- `summary/absolute.npz` (not for agents).

## Results (2026-10-19, 11:02 UTC; location-free)

**Runs.** Jobs 1390279–1390286 from 9827e3c all COMPLETED, in 7–8 minutes per lane. The per-event sum passes on all
14 new cells.

| sigma_kde | R (64) | R (128) | Delta (64) | Delta (128) | MC90 (64 / 128) | roughness (64 / 128) | Hellinger from spectral (64 / 128) | Hellinger 64 vs 128 |
|---|---|---|---|---|---|---|---|---|
| 1e-3 (context) | 1.024 | 1.153 | +0.02 | −0.00 | 1.12 / 1.38 | 0.17 / 0.24 | 0.122 / 0.139 | — |
| 1.5e-3 | 1.042 | 1.171 | +0.01 | −0.02 | 1.07 / 1.26 | 0.10 / 0.13 | 0.105 / 0.129 | 0.065 (not compared) |
| 2e-3 | 1.050 | 1.179 | +0.01 | −0.04 | 1.05 / 1.19 | 0.07 / 0.09 | 0.090 / 0.121 | 0.061 ✗ |
| 2.5e-3 | 1.051 | 1.169 | +0.00 | −0.06 | 1.03 / 1.16 | 0.06 / 0.07 | 0.077 / 0.110 | 0.057 ✗ |
| 3e-3 | 1.048 | 1.147 | +0.00 | −0.07 | 1.02 / 1.13 | 0.05 / 0.06 | 0.064 / 0.098 | 0.053 ✗ |
| **3.5e-3** | 1.044 | 1.120 | +0.01 | −0.07 | 1.01 / 1.11 | 0.05 / 0.06 | 0.054 / 0.085 | **0.049 ✓** |
| 4e-3 | 1.039 | 1.095 | +0.01 | −0.07 | 1.00 / 1.09 | 0.05 / 0.05 | 0.045 / 0.073 | 0.046 ✓ |
| 5e-3 | 1.029 | 1.056 | +0.03 | −0.06 | 0.99 / 1.06 | 0.05 / 0.05 | 0.034 / 0.052 | 0.039 ✓ |
| 7e-3 | 1.010 | 1.016 | +0.06 | −0.01 | 0.97 / 1.03 | 0.05 / 0.05 | 0.025 / 0.027 | 0.028 ✓ |
| 1e-2 | 0.990 | 0.992 | +0.08 | +0.03 | 0.96 / 1.00 | 0.05 / 0.05 | 0.029 / 0.020 | 0.017 ✓ |

**N1 and N2.** Every chain cell passes N1 and N2 except sigma_kde 1.5e-3:
- nside 64 fails N2 (roughness 0.101);
- nside 128 fails N1 (1.26) and N2 (0.134).

**C1 along the chain.** At both nsides every consecutive pair of passing cells passes, with Hellinger 0.010–0.028.

**Reading: fiducial candidate sigma_kde 3.5e-3**, by the declared rule:
- nside 64 vs 128 gives Hellinger 0.049, within 0.05;
- the step to 4e-3 gives 0.010 (64) and 0.013 (128).

### Observations (not readings; for the owner)

1. **A tolerance crossing, not a plateau.** The nside 64 vs 128 distance falls steadily as sigma_kde grows:
   0.061 → 0.017. The catalog's own effect, its Hellinger distance from spectral only, falls with it: 0.090 → 0.029
   at nside 64. At 3.5e-3 the 64 vs 128 difference (0.049) is still about as large as the catalog effect at nside 64
   (0.054). No sigma_kde on the chain leaves the catalog effect stable while nside stops mattering.
2. **C1 along the chain depends on the step size.** With fine steps the neighbouring distances stay small even
   while the result drifts from 2e-3 to 1e-2. The informative test is nside 64 vs 128.
3. **The chain is smooth above 2e-3.** Roughness reaches its plateau (about 0.05) by 2.5e-3. The 64 vs 128
   difference changes smoothly with sigma_kde. Both point to a systematic resolution effect rather than Monte-Carlo
   noise, but only N3 can decide that.
4. **What differs between the nsides.** nside 128 is wider (R up to 1.18 against 1.05) and sits slightly lower
   (Delta about −0.07 against 0). The per-event evidences are recorded at both nsides for every new cell, so a
   per-event attribution needs no rerun.

## Amendment 1 (2026-10-19, after the results): owner guidance; plan for the ln L convergence (nothing run)

**Status.** Everything in 12AG to 12AI is experimental, and is kept as a record.

**The owner's guidance** (suggestions, not fixed rules):

1. **The 0.5 grid is too coarse** to show the roughness, given that the posterior lies mostly in about H0 50–100.
   Future grids add a fine window, [50, 100] at step 0.1 (501 points), next to the coarse [20, 140] grid at step 0.5
   for the tails and normalisation. At nside 64 that is about 2.5 minutes per grid.
2. **The ln L variance criterion (N1) decides.** Roughness (N2) is supplemental and is reported only.
3. **Ways to improve the ln L convergence:**
   - more injections (the simplest for the current core);
   - surrogates for the PE samples or the injections (harder);
   - not using p_cat(z) in the selection (denominator) term where the injections are evaluated, and using the p_vol
     term instead.

**Where the variance comes from at the production cell** (nside 64, sigma_kde 3e-3; 12AG, at the point nearest the
median):
- **Selection, 0.74:**
  - 0.69 is the floor from the injections and the fixed population, the same as spectral-only;
  - 0.05 is added by the catalog.
- **PE, 0.21.**

At finer settings the catalog's added selection part grows: about 0.2 at (128, 1e-3) and 1.5 at (128, 1e-4). The PE
part grows to 0.3–0.5.

**Facts checked for the plan:**
- **Injections:** the selection file already holds every detected injection of the public O3 and O4 sets at the FAR
  < 1/yr threshold: 1,067,946 found of 944,412,448 draws. The floor (0.69) means an effective number of about 1e5.
  It falls as 1/N_inj.
- **PE samples:** they are capped at 4096 per event.
- **How core evaluates the selection term:** with the catalog sliced at each injection's pixel
  (`selection/gw.py: compute_selection_term`, `em_catalog_sel`).
- **The field weighting's normaliser:** it divides the host density by the survey-global total, which depends on
  H0. That normaliser cancels between the event evidences and −N ln mu only because both use the same density.

**Plan, in the order proposed to the owner:**
1. Measure first.
2. Then the selection-term variants D1–D3.
3. Then more injections or more PE samples.
4. Surrogates only if needed.

The owner decides each step; the reply to the owner gives the details.
