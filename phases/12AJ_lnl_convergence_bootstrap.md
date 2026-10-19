# 12AJ — The ln L Monte-Carlo noise at fixed calibration: a bootstrap of the PE samples and the injections

## Status

**DECLARED (2026-10-19), before any 12AJ replicate or likelihood.** This record fixes the replicates, the cells, the
grid, the metrics, the readings and the controls before anything runs. Only one thing has run: a location-free check
on existing grids that the fine window holds the posteriors (see "Grid"; consumer commit ac2b5a4).

**Blinding: location-free**, as in 12AG to 12AI. No H0 value appears here, in commit messages or in PR text. The only
H0 values in this record are fixed a priori:
- the coarse grid [20, 140] at step 0.5;
- the fine window [50, 100] at step 0.1;
- the reference point 75, the window's centre;
- the five control points 50, 62.5, 75, 87.5 and 100 (window indices 0, 125, 250, 375 and 500).

## Why

Amendment 1 of 12AI records the owner's guidance of 2026-10-19:
1. **The ln L Monte-Carlo variance decides.** Roughness is supplemental.
2. **A 0.5 grid is too coarse.** Use the fine window [50, 100] at step 0.1.
3. **Measure first.** The selection-denominator variants come later, in another record: D1 p_vol, D2 the sky-averaged
   catalog density, D3 the catalog density on a coarse sky map, D4 a p_det surrogate.

Core's per-point variance (12AI's criterion N1) is a delta-method estimate at each H0 separately. It leaves two
questions open:
- **What reaches the posterior?**
  - An error that is the same at every H0 cancels in the posterior. Only the part that varies across the
    posterior's bulk moves it: the shape noise.
  - For a small error ε(H0), the posterior moves by a Hellinger distance H with H² ≈ Var_p(ε)/8, where Var_p is
    the posterior-weighted variance across H0.
  - So a shape variance of 0.02 nat² moves the posterior by about 0.05, 12AI's tolerance.
- **Is the nside 64 vs 128 difference real?** 12AI deferred this test (its N3).
  - Both nsides use the same samples, so their errors are correlated.
  - Only a paired resampling shows how much noise sits on their difference.

A bootstrap of the Monte-Carlo inputs measures both, at fixed calibration, on the production setting.

## What is measured

At fixed calibration, ln L(H0) = Σ_i ln Ẑ_i(H0) − N ln μ̂(H0), plus the guard penalty, which is zero here:
- Ẑ_i depends only on event i's 4096 PE rows;
- μ̂ depends only on the detected injections.

A replicate replaces one input file by a resample with replacement and recomputes ln L on the window. The spread of
the replicates around the nominal grid estimates the Monte-Carlo noise of the nominal grid.

## Cells and inputs

| Cell | nside | sigma_kde | catalog (sha256 prefix) |
|---|---|---|---|
| production | 64 | 3e-3 | c2d1ff36567419e4 |
| resolution partner | 128 | 3e-3 | f26a20f0f3f8ca5a |
| spectral only | — | — | — |

**Other inputs** (sha256 prefix):
- footprint (nside 128): 1e4e5c675dd59ab2;
- PE (259 events × 4096): c61507251609cb69;
- injections: 56e51af209c99905.

Everything else is 12AG's ladder setting:
- calibration log10 n0 −1.8216, M0hat −20.4975, sigma_M 0.5592, delta 0;
- the population fixed as in the spectral-only reference;
- the selection guard soft, with variance limit 20;
- core e7c3007, float64.

**No third cell.** The budget goes to more replicates at 3e-3 instead. A third cell, 3.5e-3 at both nsides on the
same replicate files, would add about 75 minutes per card. The replicate files are kept, so the owner can add it
later.

## Replicates

**Modes:**
- **PE only.** Each event's 4096 rows are resampled with replacement within the event. The injections stay as they
  are.
- **Injections only.** The 1,067,946 detected injections are resampled with replacement. Ndraw (944,412,448),
  campaign_ndraws, T_obs_yr and every other attr are kept. The PE stays as it is.
- **No joint runs.**
  - With no guard penalty, ln L is a PE part plus an injection part, exactly.
  - So the joint replicate k is PE replicate k + injection replicate k − nominal, built from the grids at no cost.
    The two replicates are drawn independently, so this is a valid joint resample.
  - The separability control checks it on one pair per cell, and every point is checked for a zero penalty.

**K = 14 per mode:** 28 replicate files, plus 2 identity files.

**Scheme, fixed now:**
- **Generator:** `numpy.random.default_rng(seed)` (PCG64), one per replicate.
- **PE replicate:** for event i = 0 to 258 in file order, the rows are idx_i = 4096 i + sort(rng.integers(0, 4096,
  4096)).
- **Injection replicate:** idx = sort(rng.integers(0, 1067946, 1067946)).
- **Writer:**
  - every dataset is written as original[idx], with the same dtype, chunking, gzip level, filters and order;
  - every file attr is copied verbatim;
  - added attrs: bootstrap_mode, bootstrap_seed, bootstrap_source and its sha256, bootstrap_writer (script and
    commit), and bootstrap_n_unique (per event for PE, in total for injections).
- **Identity file:** idx = arange, so every count is one, written through the same writer.

**Files and seeds,** under `phase12_5/lnl_convergence/replicates/`:

| PE file | seed | injection file | seed |
|---|---|---|---|
| pe_identity.h5 | none (every count one) | inj_identity.h5 | none (every count one) |
| pe_b01.h5 | 1201 | inj_b01.h5 | 2201 |
| pe_b02.h5 | 1202 | inj_b02.h5 | 2202 |
| pe_b03.h5 | 1203 | inj_b03.h5 | 2203 |
| pe_b04.h5 | 1204 | inj_b04.h5 | 2204 |
| pe_b05.h5 | 1205 | inj_b05.h5 | 2205 |
| pe_b06.h5 | 1206 | inj_b06.h5 | 2206 |
| pe_b07.h5 | 1207 | inj_b07.h5 | 2207 |
| pe_b08.h5 | 1208 | inj_b08.h5 | 2208 |
| pe_b09.h5 | 1209 | inj_b09.h5 | 2209 |
| pe_b10.h5 | 1210 | inj_b10.h5 | 2210 |
| pe_b11.h5 | 1211 | inj_b11.h5 | 2211 |
| pe_b12.h5 | 1212 | inj_b12.h5 | 2212 |
| pe_b13.h5 | 1213 | inj_b13.h5 | 2213 |
| pe_b14.h5 | 1214 | inj_b14.h5 | 2214 |

The joint replicate k pairs pe_bk with inj_bk. The writer records each file's sha256, seed, size, unique counts and
the numpy version in `replicates/manifest.json`. The results section will copy them.

**How the bootstrap compares with core's variances.** This follows from core's formulas, before any run:
- **PE.**
  - Core's per-event variance is σ_i² = Σw²/(Σw)² − 1/n (`selection/gw.py: log_evidence_and_mc_variance`).
  - That is the bootstrap variance of ln Ẑ_i to first order.
  - Prediction: the bootstrap PE variance ≈ core's `pe_mc_variance_sum` (12AI: 0.21 at the production cell, at the
    point nearest the median).
- **Injections.**
  - Core's 1/N_eff = Σw²/(Σw)² − 1/Ndraw counts all draws.
  - The bootstrap keeps the detected count fixed, so it leaves out the Poisson fluctuation of that count.
  - That fluctuation shifts ln L by the same amount at every H0. It cancels in every posterior and in every
    difference.
  - So the per-point comparison uses core's `selection_mc_variance` minus N²(1/N_det − 1/Ndraw) = 0.0627.
  - Prediction at the production cell: about 0.74 − 0.06 = 0.68.
- **Caveat: two events were resampled with replacement upstream.** The attr n_events_resampled_with_replacement is 2;
  the first event has 2383 unique rows of 4096. Both the bootstrap and core treat the 4096 rows as independent
  draws. For those two events, both understate the noise relative to the original posterior samples.

## Grid

- **Fine window:** [50, 100] at step 0.1, 501 points, built as the drivers build grids (lo + step × arange). It is
  used for the nominal grids, every replicate and spectral only.
- **Posteriors:** flat prior, normalised on the window. Every posterior metric in this record uses the window
  posterior.
- **The coarse grid is not rerun.**

**Window check (done now).** Script `scripts/phase12aj_window_check.py` (ac2b5a4), output `plans/window_check.json`.
It reads the existing 241-point grids (12AI's `absolute.npz`) and writes only location-free numbers:
- the posterior mass outside [50, 100], as a power-of-ten ceiling;
- how much each summary changes when the coarse posteriors are cut to the window and renormalised.

**Rule:** the window is enough when, in every case below,
- the mass outside is ≤ 1e-3;
- the cut changes R and the sd ratio by ≤ 0.002, Delta by ≤ 0.01 and every Hellinger distance by ≤ 0.002.

| Case | Mass outside | Change in R | Change in sd ratio | Change in Delta | Change in Hellinger from spectral |
|---|---|---|---|---|---|
| (64, 3e-3) | ≤ 1e-3 | 3.5e-5 | 3.1e-5 | 2.0e-5 | 3.3e-6 |
| (128, 3e-3) | ≤ 1e-3 | 1.3e-4 | 2.3e-4 | 2.9e-5 | 8.8e-6 |
| (64, 3.5e-3) | ≤ 1e-3 | 2.6e-5 | 1.1e-5 | 1.3e-5 | 2.8e-6 |
| (128, 3.5e-3) | ≤ 1e-3 | 1.1e-4 | 2.2e-4 | 3.6e-5 | 1.0e-5 |
| spectral only | ≤ 1e-3 | — | — | — | — |

**Nside 64 vs 128:** the cut changes the Hellinger distance between them by 2.4e-5 at both 3e-3 (0.0533) and 3.5e-3
(0.0494).

**Result: the window is enough.** Every change is at least ten times below its limit.

## Evaluation: one process per cell, compiled once

**Why a stock run per replicate is costly.**
- The target's jit takes the PE and injection samples, the compact catalog and the footprint fractions as arguments
  (`phase12/desi_selection.py`, `_TargetOperands`).
- But each target builds its own jit and its own compact catalog view. That view is the union of the HEALPix pixels
  where any PE sample or injection falls.
- So a stock run per replicate loads, builds and compiles again. On rita in 12AI, starting, loading, building and
  evaluating the first point (which compiles) took about 120 s at nside 64 and 180 s at 128.

**What resampling does to the view.** Measured now from the sky positions only:
- **nside 64:**
  - the union holds all 49,152 pixels;
  - every pixel holds at least 5 injections;
  - no resample removes a pixel (expected loss: 1e-7 pixels per replicate);
  - so every replicate's own view is the nominal view.
- **nside 128:**
  - the union holds 196,577 of 196,608 pixels, and 969 pixels hold no injection;
  - a replicate drops on average about 75 pixels (PE mode) or 250 (injection mode), pixels occupied only by rows it
    did not draw;
  - so its own view is a strict subset of the nominal view.

**The design.**
- One process per cell builds the nominal target once. This is the stock build: `phase12t_common.build_target`, as
  `phase12ah_a_scan.py` does.
- It evaluates the nominal grid.
- It then evaluates each replicate by swapping the PE or the injection operand into the same jit:
  - the replicate file is read with core's loader;
  - samples are mapped to catalog rows with core's sample-to-row map against the nominal view;
  - the operand is built with the target's own `_make_runtime_event`.
- Same shapes, so there is no rebuild and no recompile. A replicate grid takes about 145 s, against 250 to 310 s for
  a stock run.

**Per nside:**
- **nside 64:** this is exactly the stock computation, since the view is the same. The process checks, for every
  replicate, that its pixel union is the nominal one.
- **nside 128:** the replicate is evaluated on the nominal view, a superset of its own view. The extra rows hold
  catalog galaxies but no sample.
  - The field numerator is per row and has no survey-wide sum (core's `catalog/field.py`). So a row that no sample
    uses changes only the array sizes.
  - The padding width (774) is set by the densest row. That row's pixel holds both PE samples and injections, so it
    stays in every single-mode replicate.
  - The kernel window (774) is as wide as the padding, so it is inactive.
  - Expected: bit-identical to a stock run. The tolerance is 1e-9 (the swap control).

**The process also records:**
- every replicate's first-point time (a recompile would show as about 65 s);
- the number of catalog rows that no sample uses.

## Metrics (fixed now)

**Scope:** each metric is computed for each cell and for spectral only, in each mode: PE, injections and joint.

**Notation:**
- k = 1 to 14 is the replicate of one mode.
- δ_k(H0) = ln L_k(H0) − ln L_nom(H0) is replicate k's error.
- δ^s_k is the same on spectral only, from the same files (paired).
- p_c is the cell's nominal window posterior.

**Estimates:**
- Every variance is over k, with ddof 1.
- Each comes with a 68% chi-square interval on 13 degrees of freedom (about ±40% on a single variance).
- **PE terms also get a more precise estimate** from the per-event evidences: Σ_i Var_k of event i's δ ln Ẑ_i. It has
  the same expectation to first order, because the events are resampled independently.

1. **Per-point variance.** V(H0) = Var_k δ_k(H0), for the catalog cell and spectral only, per mode. The joint value
   is reported both as the sum of the modes and from the joint replicates.
   - **Compared with core's** analytic values at the same points, from the nominal run:
     - PE against `pe_mc_variance_sum`;
     - injections against `selection_mc_variance` − 0.0627.
   - **Reported:** at the point nearest the nominal median, as the p_c-weighted mean, and as the maximum inside the
     nominal 90% interval. Each comes with its ratio to core's value.
2. **Variance of differences.** D(H0) = Var_k[δ_k(H0) − δ_k(75)], split the same way. Reported as the p_c-weighted
   mean and as the maximum inside the 90% interval.
   - **Shape variance,** reported with it:
     - S = (1/(K−1)) Σ_k ∫ p_c (e_k − ē_k)² dH0, where e_k = δ_k − mean_k δ_k and ē_k = ∫ p_c e_k dH0.
     - S has no reference point. It is the part of the noise that moves the posterior (H² ≈ S/8).
   - **Shape bias** B: the same integral applied to mean_k δ_k.
   - **The readings use S, not D.** D depends on where 75 sits relative to the posterior, and that is blinded.
3. **Posterior noise.** For each replicate:
   - R_k, the 68% half-width ratio against the replicate's own spectral grid;
   - the sd ratio;
   - Delta_k, the median shift in spectral sd;
   - the Hellinger distance to the nominal posterior, for the cell and for spectral only;
   - the Hellinger distance from spectral only.

   **Reported:**
   - the nominal value on the window, then the mean, sd, minimum and maximum over k;
   - the shift bias mean_k Delta_k − Delta_nom;
   - the check of mean_k H² against (S + B)/8.
4. **Nside 64 vs 128, paired (12AI's deferred N3).** The joint mode decides. The PE and injection modes are reported.
   - **Nominal:** H_nom, the Hellinger distance between the two nominal posteriors; dR_nom = R(128) − R(64);
     dDelta_nom.
   - **Bootstrap:** the mean and sd over k of the replicates' 64-vs-128 Hellinger distance, dR_k and dDelta_k.
   - **Noise floor:**
     - ε_k = δ_k(128) − δ_k(64) is the error on the 64-vs-128 difference.
     - H_floor,k is the Hellinger distance between p and p·exp(ε_k), renormalised. It is computed with p the nominal
       64 posterior and again with the nominal 128 posterior; the larger counts.
     - H_floor is the rms over k. It includes the bootstrap bias, so it is the mean-squared error of the difference.
       The floor without the bias is also reported.
   - **Test statistics:**
     - z_R = |dR_nom| / sd_k(dR_k);
     - z_Δ = |dDelta_nom| / sd_k(dDelta_k);
     - ρ = H_nom / H_floor.
   - **Also reported:** |mean_k − nominal| / sd_k for each quantity.
5. **What the catalog adds, paired.** Metrics 1 to 3 are also computed for the catalog cell minus spectral only,
   replicate by replicate:
   - the difference of variances ΔV = V_c − V_s. It is comparable with core's difference: 0.05 in selection at the
     production cell.
   - the variance of the paired change, Var_k(δ_k − δ^s_k): the noise in what the catalog changes;
   - the shape terms S_c − S_s.

All curves against H0 go to `summary/bootstrap_absolute.npz`, which is not for agents. `summary/summary.json` holds
only the scalars above.

## Readings (fixed now)

1. **What dominates the shape noise.** For each cell, the joint shape variance S splits exactly into four terms, all
   weighted by p_c:
   - **PE floor:** S on spectral only, PE mode;
   - **selection floor:** S on spectral only, injection mode;
   - **catalog-added PE:** S_c − S_s, PE mode;
   - **catalog-added selection:** S_c − S_s, injection mode.

   **Verdict:**
   - The largest term "dominates" when it is at least half of the total.
   - Otherwise the reading is "shared", naming every term that is at least a quarter.

   Each term is reported with its interval. The same split of the per-point variance, at the point nearest the
   median, is shown next to 12AI's values: 0.69 (selection floor), 0.05 (catalog-added selection) and 0.21 (PE).
2. **Whether core's per-point variance overstates the shape noise.** Q = S(joint) / V̄_core, where V̄_core is the
   p_c-weighted mean of core's total per-point variance, the quantity behind N1.
   - **Verdict:**
     - Q ≤ 0.5: core's value overstates the shape noise, by a factor 1/Q;
     - 0.5 < Q ≤ 1: comparable;
     - Q > 1: core's value understates it.
   - **Also reported:**
     - Q_D, with D in place of S;
     - whether core's per-point numbers match the bootstrap: the PE ratio, and the selection ratio after the count
       term. They "match" when the 68% interval of the ratio contains 1.
3. **The N3 verdict for nside 64 vs 128 at 3e-3** (joint mode):
   - **"real resolution difference"** if ρ ≥ 3;
   - **"Monte-Carlo noise"** if ρ < 1.5 and z_R < 2 and z_Δ < 2;
   - otherwise **"inconclusive"**.

   Two more readings:
   - **"C1's 0.05 tolerance is resolvable"** if H_floor ≤ 0.05/3.
   - **12AI's C1 failure at 3e-3** (0.053) is "within noise of the tolerance" when |H_nom − 0.05| < 2 sd_k of the
     replicates' 64-vs-128 distance.
4. **Which fix the numbers point to.** This reading only points; it decides nothing.
   - **Selection floor:** more injections (its variance falls as 1/N_inj) or D4.
   - **Catalog-added selection:** D1 to D3.
   - **PE floor or catalog-added PE:** more PE samples.
   - **"Shared":** the fixes of the two largest terms, in order.

## Controls (fixed now)

1. **Identity, bit for bit, on rita.**
   - **Stock run:** at both nsides, the stock driver (`phase12ah_a_scan.py`, its own process) runs on pe_identity.h5
     with inj_identity.h5 at the five control points. It must reproduce the loop's nominal grid there bit for bit.
   - **Swap:** the loop's own swap of the identity files must reproduce it too.
   - **Spectral only (HENON):** the grid from the identity files must equal the nominal spectral grid bit for bit at
     all 501 points.
2. **Swap.** At both nsides, the stock driver runs on pe_b01.h5 with inj_b01.h5 at the five control points. It must
   equal the loop's swap of the same pair: bit for bit at nside 64, and to 1e-9 at nside 128 (expected bit for bit).
3. **Separability.**
   - ln L(pe_b01, inj_b01) − ln L(pe_b01, nominal) − ln L(nominal, inj_b01) + ln L(nominal) = 0 to 1e-9:
     - at the five points at both nsides;
     - at all 501 points on spectral only.
   - **Every point of every replicate must be unpenalised and accepted:** zero soft-guard penalty, and total variance
     within the limit of 20.
   - **If a point is penalised:** it is counted, and the joint metrics are reported with and without its replicate.
4. **Per-event sum.** Σ_i ln Z_i + core's selection correction = ln L, to 1e-9, at every point of every grid, catalog
   and spectral.
5. **Files.**
   - Every replicate passes core's loader (`ds.load_events` and `ds.load_injections`, with the target's fit
     columns).
   - Sizes equal the originals: 1,060,864 PE rows (259 × 4096) and 1,067,946 injections.
   - nsamp, nobs, ndraw and every original attr are unchanged.
   - The PE rows of event i stay in block i.
   - The identity files' datasets equal the originals bit for bit.
6. **Nominal against the existing grids.** The coarse grid shares 101 points with the window: 50, 50.5, …, 100. At
   those points the floats are identical, and:
   - the nominal fine grids must match 12AG's 241-point grids at 3e-3 to 1e-6 (12AG's cross-job tolerance; observed
     0 so far);
   - the nominal spectral grid must match the reference to 1e-9.

   The spectral runs override only the evaluation grid. The configuration's H0 range (20 to 140) stays.
7. **Float64 and code.**
   - Every run records x64 on. The drivers refuse to run otherwise, and any CPU recomputation with core functions
     enables x64 (12AH amendment A3).
   - Every job runs from a worktree of a committed sha, with a clean tree.
8. **Compact view and compilation.**
   - **nside 64:** every replicate's pixel union must equal the nominal 49,152 pixels.
   - **nside 128:** every replicate's union must lie within the nominal view. The counts of rows that no sample uses
     are reported.
   - **No recompile:** every replicate's first point must take under 10 s. This affects cost only.

**If a control fails:** a failure of control 1, 2, 3, 4 or 5 withholds every reading. The summary still writes its
numbers and `STATUS.json`.

## Compute and lanes

**Measured speeds:**
- 12AI on rita: 0.263 to 0.268 s per point at both nsides. Start, load, build and first point take about 120 s at
  nside 64 and 180 s at 128.
- Spectral only on HENON (12AH, 8 CPUs): about 0.77 s per point.

| Job | Where | Work | Estimate |
|---|---|---|---|
| replicates | HENON CPU, 16 CPUs, 32 GB | write and check the 30 files and the manifest | 5 to 10 min |
| lane rita0 | RITA-GPU, A100-80 | nside 64: the two stock controls (5 points each), then one process with the nominal (501 points), the two control swaps (5 points each) and 28 replicates (501 points each) | about 75 min |
| lane rita1 | RITA-GPU, A100-80 | nside 128: the same | about 78 min |
| spectral | HENON CPU: an array of 31 tasks, 8 CPUs and 16 GB each, at most 8 at once | nominal, identity, pair 01 and the 28 replicates, 501 points each | about 7 min per task; about 30 min in all, alongside the lanes |
| summary | HENON CPU, 8 CPUs, 32 GB | metrics, controls, readings; always writes `summary/STATUS.json` | about 10 min |

**Per lane:**
- **nside 64:**
  - the stock controls take 2 × 120 s;
  - the build takes 120 s;
  - the nominal takes 501 × 0.265 s;
  - the replicates take 28 × (10 s to load + 501 × 0.265 s);
  - total: about 4,500 s.
- **nside 128:** about 4,700 s.

**GPU total:** about 2.6 card-hours.
- **Wall time:** about 78 min, inside the 1.5 h budget with about 12 min to spare.
- **Why not K = 16:** about 88 min, too tight for the budget.

**Lanes:**
- **rita0** (nside 64) and **rita1** (nside 128), with `phase12ag_plan.LANES`' flags: -p RITA-GPU --qos rita
  -A phy220048p --gres=gpu:a100-80:1 --cpus-per-task=128 --mem=120G --time=7-00:00:00.
- **HENON CPU,** for the replicates, spectral-only and summary jobs: -p HENON --qos henon -A phy220048p
  --time=7-00:00:00 --exclude=henon06,henon08.
- **Dependencies:**
  - the two lanes and the spectral array start after the replicates job (afterok);
  - the summary starts after both lanes and the array (afterany).
- **Not used:** MIKO, js2h100, twig or henon-gpu.

**Total from submission to the summary:** about 1.6 to 1.7 h, if rita is free. It was idle when this record was
written.

## Code

Consumer branch `phase12aj/lnl-bootstrap` from 9827e3c, worktree `phase12_5/repo_12AJ`:
- **Already committed:** `scripts/phase12aj_window_check.py` (ac2b5a4), run for this record.
- **To be written before any job:**
  - `scripts/phase12aj_replicates.py`: the writer and the file checks;
  - `scripts/phase12aj_boot_scan.py`: the one-process-per-cell loop;
  - `scripts/phase12aj_spectral.py`: spectral only on the window, with the per-event evidence;
  - `scripts/phase12aj_plan.py` and `scripts/phase12aj_summary.py`;
  - `slurm/phase12aj_*`;
  - `tests/test_phase12aj.py`.

Every job runs from `lnl_convergence/worktrees/<sha>/`.

## Outputs

Under `phase12_5/lnl_convergence/`:
- `replicates/`: the 30 files and `manifest.json`.
- `runs/ns64_sk3.0e-03/`, `runs/ns128_sk3.0e-03/` and `runs/spectral/`:
  - one directory per grid: nominal, ctl_stock_identity, ctl_stock_pair01, swap_identity, swap_pair01, pe_b01 to
    pe_b14, and inj_b01 to inj_b14 (spectral has nominal, identity, pair01 and the replicates);
  - each holds `scan.json` or `spectral_h0.json`, `events.npz` and `DONE`, which are not for agents.
- `summary/`:
  - location-free: `summary.json`, `controls.json` and `STATUS.json`;
  - `bootstrap_absolute.npz`, which is not for agents.
- `plans/` (`plan.json`, `window_check.json`), `logs/` and `worktrees/`.

## Known limits

- **K = 14.** A single variance from 14 replicates is uncertain by about ±40% (68%). The PE terms are much tighter,
  through the per-event estimate. The readings are about factors, not percent.
- **What the bootstrap sees.** It measures the noise of the estimator given these 4096 rows per event and these
  injections. It does not see:
  - errors common to every replicate, such as PE prior systematics or a mismatch of the injection set;
  - the upstream duplication of two events.
- **One sigma_kde.** A third cell is left to the owner.
