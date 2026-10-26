# 12AJ — The ln L Monte-Carlo noise at fixed calibration: a bootstrap of the PE samples and the injections

## Status

**DECLARED (2026-10-19), before any 12AJ replicate or likelihood.** This record fixes the replicates, the cells, the
grid, the metrics, the readings and the controls before anything runs. Only one thing has run: a location-free check
on existing grids that the fine window holds the posteriors (see "Grid"; consumer commit ac2b5a4).

**Build (amendment B1, 2026-10-19, before any production job).** The code is written and tested, the 30
replicate files are built and pass every file check, and the preflight identity control passed bit for bit at both
nsides and on spectral only. The production is prepared, not submitted. Consumer commit 03a35ef (local, not pushed).

**Review fixes (amendment B2, 2026-10-19, before any production job).** One blocking risk fixed (the spectral
identity control now runs in one array task, on one node) and eight cheap non-blocking fixes. Nothing in the design
changes. Production runs from consumer commit 5f24519 (local, not pushed).

**Results (2026-10-19).** All eight controls pass. The shape noise is dominated by the catalog-added selection term (80% at nside 64, 82% at 128); core's per-point variance overstates the shape noise 24× and 16×; nside 64 vs 128 at 3e-3 reads "Monte-Carlo noise", and C1's 0.05 tolerance is not resolvable with the current injections. See "Results".

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
- Each comes with a 68% chi-square interval on 13 degrees of freedom (about −27%/+59% on a single variance, that
  is [0.73, 1.59] times the estimate; the earlier wording "about ±40%" is corrected in amendment B2).
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

- **K = 14.** A single variance from 14 replicates has a 68% interval of about −27%/+59% (corrected in B2 from
  "about ±40%"). The PE terms are much tighter,
  through the per-event estimate. The readings are about factors, not percent.
- **What the bootstrap sees.** It measures the noise of the estimator given these 4096 rows per event and these
  injections. It does not see:
  - errors common to every replicate, such as PE prior systematics or a mismatch of the injection set;
  - the upstream duplication of two events (sizes added in B2): event indices 0 and 58 keep 2383 and 1732 unique
    rows of 4096. Solving M(1 − e^(−4096/M)) = n_unique gives about 3400 and 1980 original samples, so their true
    ln Z_i variance is about 2.2 and 3.1 times what the bootstrap and core see. The summary reports these two
    events' share of the PE variance and the PE total and S(PE) with their v_i scaled by those factors.
- **One sigma_kde.** A third cell is left to the owner.

## Amendment B1 (2026-10-19, build; before any production job): code, tests, replicate files and the preflight

**Nothing in the design changes.** Every item below is either the declared design, built, or an addition that does
not change what is computed. Nothing in this amendment carries an H0 value beyond the a-priori points.

### Code

Consumer branch `phase12aj/lnl-bootstrap` (worktree `phase12_5/repo_12AJ`), local commits, not pushed:
- **044d02c**: the build:
  - `scripts/phase12aj_replicates.py` (the writer and the file checks);
  - `scripts/phase12aj_boot_scan.py` (one process per cell: the stock build once, then the swap);
  - `scripts/phase12aj_spectral.py` (12AH's spectral-only script with the window as the evaluation grid);
  - `scripts/phase12aj_plan.py`, `scripts/phase12aj_summary.py`;
  - `slurm/phase12aj_*` (worktree, lane, array, summary and submit scripts);
  - `tests/test_phase12aj.py`.
- **28ae66b**: the spectral half of the preflight (plan entries, its check and its submit script).
- **03a35ef**: every curve against H0 into `summary/bootstrap_absolute.npz`, as declared (summary code only).

The likelihood path (`phase12aj_boot_scan.py`, `phase12aj_spectral.py`, the 12AG/12AH drivers and the `phase12`
package) is the same in all three commits, so the preflight below, run from 044d02c (rita) and 28ae66b (HENON),
covers the production code. The production runs from **03a35ef**, every job from the worktree
`lnl_convergence/worktrees/03a35efd0c3a` (clean, at that commit).

### Tests

`JAX_PLATFORMS=cpu DARKSIRENS_ZMAX=6.0 <consumer python> -m pytest -q tests/test_phase12aj.py`: **19 passed** (about
36 s). They cover:
- **the plan:**
  - the window and control-point floats;
  - the 101 points shared with the coarse grid;
  - the lanes (rita0 and rita1 only), each partition's maximum time, and no MIKO, js2h100, twig or henon-gpu;
- **the writer:**
  - seeds and indices: per-event blocks, sorted, reproducible;
  - every attr copied with its HDF5 type, vlen and empty string arrays included;
  - the layout and the provenance attrs, and the identity files bit for bit;
  - a corrupted or misplaced replicate fails the checks;
- **the swap, on the synthetic P12.4 fixture:**
  - the replicate's operands swapped into the nominal target's jit equal a stock build on the replicate stores;
  - bit for bit when the pixel union equals the view, to 1e-9 when it is a strict subset;
  - with no trace and no compile;
- **the metrics, on curves with known noise:**
  - per-point variance, difference variance and the shape variance (constant offsets carry none);
  - H² ≈ Var_p(ε)/8, the Hellinger closed form, R and Delta, the floor and the count term;
  - the vectorised per-event-sum control against core's eager correction;
- **the readings and the location guards** (key names and values);
- **the whole summary on a synthetic run tree:**
  - controls 1–5, 7 and 8 pass;
  - the four shape terms add up to S(PE) + S(injections);
  - the injected noise is recovered;
  - the readings are withheld when control 1 fails.

### Replicate files (control 5)

Job 1390290 (HENON, henon04, 16 CPUs, 69 s), from 044d02c. `replicates/manifest.json`: **pass**. Its sha256 is
951fc6dab5dc62c44bf472e4ec34ef584178d6b39353a4274cb6a803e17fe2e2, with numpy 1.26.4 and h5py 3.12.1.

**Sources:** PE c61507251609cb69 and injections 56e51af209c99905, as declared.

**Every one of the 30 files passes:**
- re-read, it equals original[idx] bit for bit, dataset by dataset;
- same dtype, chunks, gzip level, filters, fill value and maxshape, in the same order;
- every original attr unchanged, with its HDF5 type;
- the provenance attrs added;
- PE rows stay in their event block;
- the identity files equal the originals bit for bit;
- core's loader (with the target's fit columns) reports 259 × 4096 PE rows, or 1,067,946 injections with ndraw
  944,412,448.

| PE file | seed | sha256 (prefix) | unique rows per event (min / median / max) | injection file | seed | sha256 (prefix) | unique rows |
|---|---|---|---|---|---|---|---|
| pe_identity.h5 | none | e82c2d2f42fda36b | 4096 / 4096 / 4096 | inj_identity.h5 | none | 8a3a1fdbae863d1c | 1,067,946 |
| pe_b01.h5 | 1201 | f8220bae708975b4 | 2540 / 2588 / 2642 | inj_b01.h5 | 2201 | 2d1ea5e0c518d133 | 675,165 |
| pe_b02.h5 | 1202 | d0607ba074d110f8 | 2542 / 2589 / 2636 | inj_b02.h5 | 2202 | a013462be663933d | 675,166 |
| pe_b03.h5 | 1203 | 341780adb7d56f99 | 2531 / 2591 / 2646 | inj_b03.h5 | 2203 | 459d3f72fde592f5 | 674,746 |
| pe_b04.h5 | 1204 | e87e24fc2e6e8e93 | 2529 / 2590 / 2652 | inj_b04.h5 | 2204 | 4667dafda8c8439b | 674,731 |
| pe_b05.h5 | 1205 | 4ecc5b031c8f3d1a | 2527 / 2589 / 2639 | inj_b05.h5 | 2205 | 69d7a8aa285b6532 | 675,454 |
| pe_b06.h5 | 1206 | b716a51369648f09 | 2549 / 2586 / 2657 | inj_b06.h5 | 2206 | 6138b353bceee6f7 | 674,669 |
| pe_b07.h5 | 1207 | 63a31eaa45dd7893 | 2530 / 2588 / 2661 | inj_b07.h5 | 2207 | 2012bfad82ab784e | 675,557 |
| pe_b08.h5 | 1208 | 5a312987cb0888a4 | 2518 / 2590 / 2656 | inj_b08.h5 | 2208 | f069640b0878bffd | 675,320 |
| pe_b09.h5 | 1209 | 55437cdc33beb38a | 2529 / 2586 / 2659 | inj_b09.h5 | 2209 | e39ceb3a352defbc | 674,816 |
| pe_b10.h5 | 1210 | 85d7e458870a5540 | 2525 / 2588 / 2639 | inj_b10.h5 | 2210 | ab1e823db8f1fe07 | 674,873 |
| pe_b11.h5 | 1211 | 47524e7baa764873 | 2530 / 2592 / 2640 | inj_b11.h5 | 2211 | 804242ea6ce51ecc | 674,812 |
| pe_b12.h5 | 1212 | 398211e91bfa7531 | 2535 / 2590 / 2651 | inj_b12.h5 | 2212 | 0b2d3f47e0087cf1 | 675,206 |
| pe_b13.h5 | 1213 | 587f57da53cb71d1 | 2545 / 2588 / 2638 | inj_b13.h5 | 2213 | 6c4e0d62082182d7 | 675,109 |
| pe_b14.h5 | 1214 | 5683fcdcb590f51a | 2542 / 2589 / 2634 | inj_b14.h5 | 2214 | 7d31268b3c5b7668 | 675,047 |

The unique fractions are about 0.632, as a bootstrap gives (1 − 1/e).

### Preflight: the identity control before production (location-free)

Outputs under `lnl_convergence/preflight/`, check `preflight/controls_preflight.json`; the production summary does
not use them.

**On ONE rita card:** rita0, job 1390291, from 044d02c, 9 min 40 s.
- Per nside, the stock driver on pe_identity + inj_identity and on pe_b01 + inj_b01, at the five control points.
- Then the loop at the five control points: nominal, swap_identity, swap_pair01, pe_b01 and inj_b01.
- Check: job 1390292 (HENON).

**Its spectral half on HENON:** array 1390295, from 28ae66b. The nominal and the identity spectral-only grids, at
all 501 points. Check: job 1390296.

| Check | nside 64 | nside 128 | spectral only |
|---|---|---|---|
| 1. stock identity vs the loop's nominal | bit for bit (ln L, ln μ, N_eff, every ln Z_i and variance) | bit for bit | — |
| 1. the loop's swap of the identity files vs nominal | bit for bit | bit for bit | — |
| 1. identity grid vs nominal grid (501 points) | — | — | bit for bit |
| 2. stock pair 01 vs the loop's swap of pair 01 | bit for bit | **bit for bit** (718 view rows unused) | — |
| 3. separability at the five points | 0.0 | 0.0 | — |
| 4. per-event sum, every grid | ≤ 9.1e-13 | ≤ 3.4e-13 | ≤ 6.8e-13 |
| 6. against 12AG at the control points / the reference at the 101 shared points | 0.0 | 0.0 | 0.0 |
| 7. x64 on, clean committed tree | yes (044d02c) | yes | yes (28ae66b) |
| 8. view | equal (49,152 rows) for every grid | within the view; unused rows: pe_b01 77, inj_b01 269, pair 01 718 | — |
| 8. first point of a swapped grid; compilations | 0.26 s; 0 | 0.26 s; 0 | — |

More from the preflight:
- No point is penalised or unaccepted in any preflight grid.
- The configured H0 range of every spectral run stays [20, 140].
- Replicate loads take 0.7 to 1.7 s, against the 10 s assumed.
- The nominal grid's first point compiles in 72 s (nside 64) and 64 s (nside 128).
- Points take 0.256 to 0.268 s on rita.
- A spectral-only grid takes 441 s on 8 HENON CPUs.

**On the nside-128 prediction:** a replicate evaluated on the nominal view gives exactly the stock result, as expected.
- The kernel window is 774, from the nominal view.
- The 1e-9 tolerance of control 2 was not needed at pair 01.

### Additions that do not change the design

1. **The preflight above.**
2. **The loop's self-check.** Before any grid, the swap path applied to the original files must rebuild the target's
   own PE and injection operands, leaf by leaf and bit for bit. Otherwise the process exits with code 4. It passed at
   both nsides.
3. **Diagnostics in the loop.**
   - Each replicate's sha256 is checked against the manifest before use.
   - Each grid records its XLA compilations and traces, beside the declared first-point time.
4. **The per-event-sum control (4) is vectorised.**
   - Core's `selection_log_correction` is evaluated for all points at once, as a jit of a vmap in float64.
   - It is cross-checked against the eager per-point evaluation (12AH's checker) at the control points, to 1e-12.
     The difference was 0 to 4.5e-13.
   - Reason: the eager call takes about 24 ms per point, and there are about 45,000 points.
5. **The location guard.**
   - `summary.json` and `controls.json` are checked for forbidden key names (median, mean, map, interval, H0, …).
   - They are also checked for any float equal to an absolute posterior location the summary computed (medians,
     means, MAPs and interval ends of every nominal and replicate posterior), with the a-priori points excepted.
   - On a violation the file is not written, and `STATUS.json` names the paths only.
6. **`scan.json` is rewritten every 50 points, not every point.** This only changes the resume granularity.

### Choices where the declaration is silent

1. **The joint S of readings 1 and 2** is S(PE) + S(injections), the sum of the modes, which is what splits exactly
   into the four terms. The S of the joint replicates, and the Q from it, are reported alongside.
2. **Intervals.**
   - Single variances and the two floor terms: the 68% chi-square interval on 13 degrees of freedom.
   - The catalog-added terms and Q: ± one delete-one jackknife sd over k.
   - The per-event PE estimate: ± one sd, from 2v_i²/(K − 1) per event.
3. **Reading 2's "match" test.**
   - PE uses the per-event estimate; selection uses the bootstrap after the count term.
   - Each is reported at the point nearest the median and as the p_c-weighted mean, with a verdict for each.
4. **Metric 3's "own spectral grid"** is the spectral replicate of the same mode and k. For the joint mode it is
   spectral PE k + spectral injection k − spectral nominal.
5. **Penalised points.** They are counted per replicate. If there are any, every metric is also computed without
   those k (the joint drops both modes' k). The readings are shown for both; the primary set uses all replicates.
6. **The count term** comes from each run's own N, N_det and N_draw: 259² (1/1,067,946 − 1/944,412,448) = 0.0627.

**Not built as declared:** nothing.

**A residual risk (not a change).**
- The spectral identity control is bit for bit across two tasks. In the preflight both ran on henon04 (AMD EPYC
  7542).
- In production the array may place the nominal and identity tasks on different HENON nodes.
- The evidence suggests HENON's CPU numerics are deterministic across nodes:
  - the nominal reproduced the earlier reference exactly at the 101 shared points;
  - 12AH's spectral rerun also matched it exactly.
- Each run records its node and CPU model, so a failure there can be traced.

### Production (prepared, not submitted)

`slurm/phase12aj_submit.sh 03a35ef`, from `phase12_5/repo_12AJ`. The replicate manifest passes, so the replicates
are not rebuilt and nothing waits on them.
- **Lanes:** rita0 (nside 64) and rita1 (nside 128), each with the two stock controls and the loop (nominal on 501
  points, the two control swaps on five, and the 28 replicates on 501).
- **Spectral only:** HENON array 0–30, at most 8 at once.
- **Summary:** HENON, afterany on everything; it always writes `summary/STATUS.json`.

**Estimate:**
- **This record's declared speeds:** rita0 75 min and rita1 78 min (2.6 card-hours); spectral 28 min; the summary
  about 10 min.
- **The preflight's measured speeds** (faster replicate loads): about 70 to 72 min per lane, and about 30 min for
  the spectral array alongside.
- **About 1.3 h from submission to `summary/STATUS.json`** if rita is free. It was idle at 12:40 UTC.

## Amendment B2 (2026-10-19, review fixes; before any production job)

A review of the build (record, code, Slurm scripts, tests) found one blocking risk and nine non-blocking points.
Every fix below is in consumer commit **5f24519** on `phase12aj/lnl-bootstrap` (local, not pushed), on top of
03a35ef. **The likelihood path is unchanged** (the drivers, the loop and the spectral wrapper are byte-identical to
03a35ef), so the B1 preflight still covers production. **Nothing in the design changes**; the declared metrics,
readings, rules and controls stand. Tests: 22 passed on CPU (19 from B1 plus three new ones), about 39 s.

### The blocking risk: the spectral identity control could cross nodes (fixed)

- Control 1 on spectral only requires the nominal and identity grids to match bit for bit, and a failure withholds
  every reading.
- In B1 they were tasks 0 and 1 of the HENON array, free to land on different nodes. HENON nodes differ in CPU model
  (henon01 and henon02 have 256 CPUs; henon03, 04, 05 and 07 have 128; henon04 is an AMD EPYC 7542), and XLA on CPU
  compiles for the host, so the last bit could differ for no physical reason.
- **Fix:** array task 0 now runs `spectral_nominal` and then `spectral_identity` in the same task, on the same node,
  through the lane runner (entry names joined by ':'). The array has 30 tasks instead of 31; every grid still runs
  once. The summary also records whether the two grids ran on the same node and CPU model. The bit-for-bit rule
  stays.
- This replaces B1's "residual risk" note.

### Non-blocking fixes

1. **Wall time with one rita card busy.** The 1.3 h estimate holds only with both A100-80 cards free. At submission
   another session's job (`p12al-gpu-control`, not ours, not touched) holds one card and 128 CPUs, so the two lanes
   run one after the other: about 2.5–2.8 h from submission to `summary/STATUS.json`, longer if that job outlasts
   our first lane and still holds its card. The submit script prints the RITA-GPU queue before submitting.
2. **Heavy tails in the per-event PE estimate.** Some events have a prior-reweighting ESS near 10, so the Gaussian sd
   2v_i²/(K − 1) can understate the uncertainty. The summary now gives three sds of Σ_i v_i: the Gaussian one, a
   fourth-moment one, Σ_i (m4_i − (K − 3)/(K − 1)·v_i²)/K with each event's term clipped at zero, and a delete-one
   jackknife over k. The ±1 sd interval and reading 2's "matches" flag use the largest of the three. (This replaces
   B1's choice 2, third bullet.)
3. **The two upstream-resampled events.** For each system (spectral and both cells) the summary reports these
   events' share of Σ_i v_i (bootstrap) and of core's per-event variances, at the point nearest the median and
   posterior-weighted; the PE total with their v_i multiplied by (1 + 4096/M_i); and the change this makes to S(PE)
   (their per-event shape variances times (factor − 1)). The sizes are in Known limits.
4. **Wording of the K = 14 interval.** "About ±40%" is corrected to "about −27%/+59%" in "Metrics" and "Known limits".
   Supplementary only, with the declared rule unchanged: reading 1 also reports each fraction's jackknife sd and
   flags the verdict as marginal when the largest fraction's ±1 sd straddles 1/2.
5. **The H² check.** B is built from the sample mean of δ_k, so it carries about S/K of noise, and the average over k
   of Var_p(δ_k) is exactly B + (K − 1)/K·S. The check now reports H² against (B + (K − 1)/K·S)/8 beside the B1
   (S + B)/8, and the debiased bias B − S/K.
6. **12AI's core values.** They are now labelled `12AI_core_values_raw_incl_count_term` (its 0.69 selection floor
   includes the 0.0627 count term), and a count-corrected copy (0.69 − 0.0627) is written beside it, so it compares
   directly with the bootstrap floors.
7. **A test that the resampling reproduces core's variance.** On synthetic lognormal weights (three events of 4096
   rows, 600 seeds of `pe_indices`), the variance over replicates of ln mean(w[idx]) matches core's
   `log_evidence_and_mc_variance` within 15% per event and 10% in total. For injections (30,000 rows, Ndraw 900
   times larger, 1500 seeds of `inj_indices`), N² Var of ln(Σw[idx]/Ndraw) matches core's N²/N_eff minus the count
   term within 10%, where the count term is large enough that leaving it in would fail. Core runs with x64 on.
8. **STATUS.json errors.** On an exception, STATUS.json now holds only the exception type, each frame's file, line
   and function, and the message with every number replaced by '#'. No traceback text with values is written.
9. **The watcher.** The submit script now prints two watchers: `watch`, which also ends early on any failed job so
   the main session can act before the summary (the form the workflow asks for), and `watch-summary`, which ends
   only on `summary/STATUS.json` or the summary job's own terminal state.

### Production

`slurm/phase12aj_submit.sh 5f24519` from `phase12_5/repo_12AJ`, from the clean worktree
`lnl_convergence/worktrees/5f24519430c0`. The replicate manifest passes (sha256 951fc6da…), so nothing is rebuilt.
Lanes, flags and outputs are as in B1, except that the spectral array is 0–29 (at most 8 at once).

**Submitted 2026-10-19 12:56 UTC** from worktree `5f24519430c0`: rita0 (nside 64) job 1390326, running; rita1
(nside 128) job 1390327, pending on the rita card held by `p12al-gpu-control` (another session's job, not touched);
spectral array job 1390328 (tasks 0–29, at most 8 at once; tasks 0 and 1 started on henon04, the rest waiting for
HENON resources); summary job 1390329, afterany on all three. Expected `summary/STATUS.json` about 2.5–2.8 h after
submission (the lanes run one after the other), sooner if the other rita job ends early.

## Results (2026-10-19, location-free)

**Runs.** rita0 1390326 (nside 64) and rita1 1390327 (nside 128) completed (1 h 12 min and 1 h 10 min). Spectral array
1390328: tasks 0–28 completed; task 29 (`spectral_inj_b14`) failed in 2 s before any code ran (`slurmstepd: error:
TaskProlog failed status=1` on henon04, a node set-up failure). The afterany summary 1390329 then ran on incomplete
inputs: rc 3, readings withheld, controls 4 and 7 failing only on the missing spectral grid (kept as
`summary/STATUS_1390329_incomplete.json`). Task 29 was resubmitted unchanged from the same clean worktree
(`5f24519430c0`, same plan, same flags): job 1390383, completed in 6 min 34 s on henon04; summary 1390384 (afterok)
rc 0, inputs complete, readings released.

**Controls.** All eight pass (1 identity, 2 swap, 3 separability, 4 event sums, 5 files, 6 against the existing
grids, 7 commits and x64, 8 view compilation). No guard violations.

**Reading 1: what dominates the shape noise (joint S, nat², p_c-weighted).**

| term | nside 64 | share | nside 128 | share |
|---|---|---|---|---|
| PE floor (spectral only, PE) | 0.0010 | 2% | 0.0010 | 2% |
| selection floor (spectral only, injections) | 0.0020 | 5% | 0.0022 | 3% |
| catalog-added PE | 0.0048 | 12% | 0.0082 | 13% |
| catalog-added selection | 0.0317 | 80% | 0.0533 | 82% |
| **total S** | **0.0395** | | **0.0647** | |

Verdict at both nsides: **catalog-added selection dominates** (jackknife sd of its share 0.03 at 64 and 0.05 at 128;
not marginal at one half). The per-point split at the point nearest the median is the other way round: the
selection floor is about 0.63 nat² (bootstrap; core 0.60 after the count term), the PE floor about 0.30 (bootstrap;
core 0.20), and the catalog-added terms near zero in the bootstrap (core: 0.08 at 64, 0.15 at 128). The floors are
almost constant in H0, so they shift ln L as a whole and barely move the posterior; the catalog's selection noise
varies with H0 and is what moves it.

**Reading 2: core's per-point variance against the shape noise.** Q = S(joint) / V̄_core = 0.041 at nside 64 and
0.062 at 128: **core's value overstates the shape noise by 24× and 16×** (Q_D, with D in place of S: 0.097 and
0.154; Q from the joint replicates 0.046 and 0.069). Matches: the selection variance matches the bootstrap at both
nsides (ratio bootstrap/core 0.93 and 0.80 at the point nearest the median; 68% intervals contain 1). The PE variance
does not: the bootstrap's per-event estimate is 1.19–1.20 times core's (68% interval about [1.13, 1.26] at both
nsides), so core's PE per-point variance runs about 20% low. The two upstream-resampled events contribute 0.1% of it.

**Metric 3: posterior noise per replicate (joint, over k = 14).** R sd 0.099 (64) and 0.128 (128); Delta sd 0.115
and 0.161 spectral sd; Hellinger to the nominal posterior mean 0.072 and 0.088 (spectral only: 0.014). Shift bias
(mean_k Delta_k − Delta_nom) −0.013 and −0.029 spectral sd (injection mode −0.014 and −0.042). The H² check holds
(mean_k H² over (S + B)/8, exact form: 1.01 and 0.99).

**Reading 3: N3, nside 64 vs 128 at 3e-3 (joint decides).** H_nom 0.053 on the window, H_floor 0.055 (without the
bootstrap bias 0.054); ρ = 0.97, z_R = 1.18, z_Δ = 0.66: **"Monte-Carlo noise"**. Replicates' 64-vs-128 distance
0.075 ± 0.022. **C1's 0.05 tolerance is not resolvable** with these inputs (H_floor 0.055 > 0.05/3 = 0.017), and 12AI's
C1 failure at 3e-3 (0.053) is **within noise of the tolerance**. By mode: injections ρ = 1.02 (z_R 1.51, z_Δ 0.63);
PE ρ = 2.77 (z_R 3.28, z_Δ 2.82, H_floor 0.019). Under PE noise alone the difference would sit just below the
"real" threshold; the injection noise is what hides it.

**Reading 4 (points only):** the selection-denominator variants D1 to D3 (record 12AL), which target the
catalog-added selection term. More injections reduce it too (variance as 1/N_inj): resolving C1's 0.05 needs H_floor
three times smaller, about nine times less shape variance.

## Amendment (25 Oct 2026): independent review

An independent multi-agent review of the consumer repo (desi_darksirens_selection at the review head 17a65bb, 24-25
Oct 2026; report `darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in
parentheses below; only confirmed findings are fixed. The owner took the review's recommended option in every decision
on 25 Oct 2026. Each item names the consumer pull request that fixes it and its merge commit on the consumer's main
branch. The final main is 6d0f800 (26 Oct 2026); `./ci.sh` passes there in both record environments (HENON, CPU;
`ci_logs/20261026T051301Z_7566d8eb6d34_consumer_e7c3007batch_cuda12.log`, 1349 passed, and
`ci_logs/20261026T051301Z_7566d8eb6d34_consumer_1022429_lss57afebe_cuda12.log`, 1364 passed; none failed).
Location-free throughout. Unless an item says otherwise, no number of record changes. Findings whose fix packages are
not merged yet (the catalog model, the GW inputs, the variance guard and estimator noise, resume markers, the 12AQ
readings and 12AO's causes) are not amended here; the review's per-record table lists them.

**The code and environment of record (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; findings
C008, C010, C050, C051, C143, G4.1).** The code of this record is on the consumer's main branch since the
consolidation (PR #20) and its follow-up (PR #21). The environment it ran in is named, with its full pip freeze and
sha256, in `config/record_envs/12AJ.json`; `scripts/check_frozen_environment.py --record 12AJ` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AJ/<sha7>` on
GitHub (ac2b5a4, 044d02c, 28ae66b, 03a35ef, 5f24519). The full test suite is run by `./ci.sh` in the record
environments (CPU, HENON); it was green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and
is green at the final main (above).

**Code of record (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding G4.1).**
`phase12aj/lnl-bootstrap` (up to 5f24519: the replicates 12AL, 12AM and 12AQ read) is merged into the consumer's main
(merge 951e353); tag `side-branch/phase12aj/lnl-bootstrap`.

**Population of the spectral-only grids (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** The spectral-only grids gave the population as an explicit mapping at the corrected pair (0.04, 0.10). From
the consolidated main of PR #20 they evaluated the same values but recorded a `population.fixed_values` record (the
declaration written over equal entries); after the follow-up (PR #21) they resolve and record exactly what they did
when they ran (no `fixed_values` record; checked on the 12AG spectral reference at three H0 points: ln L difference
0).

**Run fingerprints (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).** The code digests that the
12AG to 12AQ drivers put into their run fingerprints cover the consumer code, so a run stored before the consolidation
(or its follow-up) is evaluated again rather than resumed when it is rerun from main; the values it computes are the
same.

**Core settings at trace time (consumer PR #29, merge 0989df4; findings C054, C055).** Core reads its
normalisation-grid settings and its missing-density form when a likelihood program is traced, at its first call, not
when the target is built. From the merge the stock target and the spectral joint target take a snapshot of those
settings at build and refuse a trace under other ones, as core's own bindings do since core 3cf8df7. Both numerics
modes now also set the normalisation grid sizes, the pairing m1 grid (off) and the pairing edge rule, and the builder
refuses a `DARKSIRENS_*` variable core reads as a numerics setting; the values set are the defaults of every record
core (e7c3007, 32c6210, 1022429) and of the 12S pin, which this record ran with (no launcher set a `DARKSIRENS_GW_*`
variable), so this record's numbers are unchanged. The target's record and provenance now carry every grid and
catalog-evaluation setting and core's numerics semantic under `core_numerics.core_settings`. Because the provenance
enters core's run fingerprint, a checkpoint written by an earlier main is not resumed by this one (it is refused,
loudly); a run started afresh computes the same numbers.

**Calibration anchor (consumer PR #29, merge 0989df4; finding C094).** A configured log10n0 outside the calibration
prior's log10n0 bounds is now refused, and so is an anchor whose sampler coordinate does not decode back to the
configured log10n0 within 1e-12 (which also happens inside the bounds, far in a conditional normal's tail, where the
quantile rounds to 0 or 1 and decodes to the bound). Before, such an anchor evaluated at the bound without an error in
the callers that did not check it themselves (the anchor gate before sampling, the 12U stage, the direct chains'
anchor and the ladder-cell check). Every record's anchor lies inside its prior's bounds and decodes to within 2.3e-16,
so this record is not affected.

**Writer commit (consumer PR #29, merge 0989df4; finding G4.10).** The summaries behind this record did not carry the
commit of the code that wrote them (the commit is in the job logs and the record). From the merge each summary carries
a `writer` block: the writing script, its checkout's commit, branch and changed-file count, and, where it reads a
short list of files, their sha256. The stored summaries are unchanged; a summary rewritten from main carries the
block.

**Operations (consumer PR #30, merge 6d0f800; finding C049).** This record's afterok Slurm submissions now carry
--kill-on-invalid-dep=yes, so a failed upstream job ends its dependants instead of leaving them pending (as in 12AG).
The flag changes only what happens when an upstream job fails.
