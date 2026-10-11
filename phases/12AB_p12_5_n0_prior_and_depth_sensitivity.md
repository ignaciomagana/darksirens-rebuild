# Phase 12AB — P12.5: how the DESI catalog H0 depends on the n0 prior and the depth step (declaration)

## Status

**DRAFT DECLARATION (2026-10-10, for the owner), before any run.** Nothing in
this record has been run. No job is submitted until the owner approves; the
CPU work then runs on HENON **after the A1 chains finish (rita job 1376492)**.

**Blinding.** No H0 value from real data (median, interval or shift) is
written here. Results will be appended location-free: shifts in units of the
baseline posterior sd, width ratios, effective sample sizes. The absolute
values stay in the output files and are not sent to the clean-room session.

## Where this sits

P12.5 replaces the fixed GWTC-5 population by its uncertainty
(`phase12_5/P12_5_full_scope.md` under darksirens-core-data):

- step 1 (12Y): the DESI chain with δ fixed at 0 and the rate index sampled;
- stage A0 (12Z): one-parameter population scans, spectral-only;
- stage A1 (12AA, PR #49): spectral-only chains with H0 and the population
  sampled, variance limit 4, running as rita job 1376492;
- stage B1: the A1 posterior reweighted to the DESI catalog likelihood,
  declared separately.

This stage asks how much the DESI catalog H0 moves with two catalog choices
that P12.5 keeps fixed: **(a) the prior on the host density n0** and
**(b) the depth step**. It is a sensitivity check for the P12.6 robustness
matrix. It changes no setting of the baseline.

## Why

**The n0 prior.** The chains use log10 n0 ~ N(-1.810518, 0.036361) on
[-2.346, -1.146]: the union's count ridge at δ = 0 (12U, 12Y), fitted pooled
over both hemispheres on the window z in [0.02, 0.30]. The cross-check of
2026-10-09 (`phase12_5/completeness_crosscheck/ns_and_n0/NOTE.md`) found:

- in the ridge's own forward model, the counts at z 0.05 to 0.245 are 6.7%
  **below** the expectation, and those at 0.245 to 0.30 are 10% above; the
  pooled window balances the two;
- the counts below the depth alone imply log10 n0 = -1.8406, **0.83 prior sd
  lower** than the prior centre;
- the prior's sd (0.036) is the rms departure of the counts from one power
  law, not a statistical error (3e-4 dex);
- the 12Y chain's n0 posterior equals its prior: the events do not constrain
  n0, so the prior alone sets it.

**The depth step.** The catalog stops at z_depth. In core
(`catalog/completeness.py`), at every redshift above z_depth the host density
is the expected density dN_exp; at and below it, it is the catalogued
galaxies plus the missing budget. The host prior therefore jumps at z_depth.
12O defined the size of that jump as

```text
step(z_d) = T(z_d-) / E(z_d-) - 1
```

with T the field host-density numerator (galaxies plus missing budget) and E
the expected density, both summed over the covered nside-64 pixels at the last
z-grid node at or below z_d, at the 12O calibration point (fixed H0, M0hat and
sigma_M at their prior means). 12O chose z_depth 0.245, the largest depth with
|step| <= 0.05 on candidates 0.200 to 0.300 in steps of 0.005. The criterion
admits every depth from 0.200 to 0.245, and 12O found that H0 moved inside
that window at the setup of the time (δ free, old spin values, fixed
population). Whether it still moves at δ = 0 with the corrected spin is not
known.

**The two are coupled.** E is proportional to n0, while T below the depth is
almost all galaxies (the magnitude-selection completeness is 0.975 to 1.000
over [0.048, 0.245]). So T/E scales close to 1/n0: lowering log10 n0 by 0.83
sd raises T/E at the depth by about 7%. The data-preferred n0 changes the
depth step itself.

In code the depth is the configuration value `catalog.z_depth`. The consumer
relabels the loaded catalog store to it (`scripts/phase12t_common.py`,
`build_target`), so a depth variant needs no new catalog product.

## The baseline

**The P12.5 DESI catalog configuration**, as B1 uses it: the A1 limit-4
combined posterior (H0 and the GWTC-5 population, 12AA) reweighted to the
DESI union target with

| | baseline |
|---|---|
| catalog | the standardized union, nside 64 (`phase12u/inputs/catalogs/desi_union_nside64.h5`), LS footprint `mth_map_nside128.h5` |
| completeness | Gaussian luminosity function, m_lim 21, k-correction, times the per-pixel footprint fraction |
| z_depth | 0.245 |
| δ | fixed at 0 |
| log10 n0 | N(-1.810518, 0.036361) on [-2.346, -1.146] (`count_ridge_union_delta0`) |
| M0hat, sigma_M | sampled, 12T priors N(-20.500, 0.199), N(0.558, 0.130) |
| GW inputs | exact-prior PE and injections (12T), soft selection guard |
| core | e7c3007 with its defaults |

If B1 is declared with a different setting, this stage follows B1 in
everything except the one item each variant changes.

## The variations

One change at a time against the baseline.

### (a) n0 prior

All truncated to the baseline bounds [-2.346, -1.146].

| name | log10 n0 prior | why |
|---|---|---|
| n0_base | N(-1.810518, 0.036361) | baseline |
| n0_m083 | N(-1.8406, 0.036361) | centre at the value the counts below the depth give (-0.83 sd) |
| n0_p1, n0_m1 | centre ± 1 sd (-1.774157, -1.846879) | |
| n0_p2, n0_m2 | centre ± 2 sd (-1.737796, -1.883240) | |
| n0_w3 | N(-1.810518, 0.109083) | width × 3 |
| n0_free | flat on [-2.346, -1.146] | no count information |

### (b) depth step

z_depth on the 12O candidate grid; n0 prior as the baseline.

| name | z_depth | why |
|---|---|---|
| d245 | 0.245 | baseline; the largest depth admitted by the 12O criterion |
| d230 | 0.230 | the depth with the smallest step at 12O's setup |
| d215 | 0.215 | inside the admitted window |
| d200 | 0.200 | the smallest admitted depth |
| d260 | 0.260 | just outside the window; reported separately, not part of the window spread |

### (c) Interaction

At every depth of (b), also the n0_m083 prior: the data-preferred n0 with
each depth. This comes from the same scans as (b) at no extra cost (Part B).

## What is run

Three parts. Parts A and B need no new code in the target. Part C needs B1's
reweighting command.

### Part A — prior reweighting of existing samples (no likelihood calls)

A change of the n0 prior centre is a change of prior only. Where the samples
already cover it, it is a reweighting by p'(n0) / p_base(n0):

- **the 12Y chain** (`phase12_5/runs/union_gamma/samples.npz`, 8,299
  equal-weight samples; the DESI result with δ fixed and the rate index
  free): variants n0_m083, n0_p1, n0_m1, n0_p2, n0_m2;
- **the B1 sample set**, once B1 exists: the same variants, multiplying B1's
  weights by the prior ratio (B1 draws n0 from the baseline prior).

The width × 3 and flat priors put mass where these samples have none, so they
are not done by reweighting.

### Part B — fixed-population H0 grids on HENON (the map)

The union target at a fixed population, scanned in H0 and log10 n0 for each
depth, with the n0 prior applied afterwards by quadrature. This gives every
variant of (a), (b) and (c) from one set of scans.

- **Code:** `scripts/phase12u_stage.py scan`, consumer
  `phase12.5/free-rate-index` 0d75b40, the env
  `phase12t/envs/consumer_e7c3007_cuda12`, `JAX_PLATFORMS=cpu`. The settings
  are those of the corrected-spin union check (`phase12_5/checks/
  check_e_union_spin.sbatch`): `count_ridge_union_delta0`, δ 0,
  `population.sampled.gamma=[-2,6]` with `--gamma 2.5439`, spin pair fixed at
  0.04 and 0.10, core defaults, exact-prior GW inputs, union catalog and LS
  footprint.
- **Population:** GWTC-5 values with the corrected spin, rate index 2.5439.
- **M0hat, sigma_M:** at their prior means (as in 12W).
- **H0:** 30 to 120 in steps of 2.5 (37 values), flat prior, as in 12W.
- **log10 n0 nodes, z_depth 0.245 (22 scans):**
  - dense: the prior centre plus k sd, k = -6 to +6:
    -2.028684, -1.992323, -1.955962, -1.919601, -1.883240, -1.846879,
    -1.810518, -1.774157, -1.737796, -1.701435, -1.665074, -1.628713,
    -1.592352;
  - outer, for n0_w3 and n0_free: -2.34, -2.25, -2.15, -2.08, -1.54, -1.45,
    -1.35, -1.25, -1.15.
- **log10 n0 nodes, z_depth 0.200, 0.215, 0.230, 0.260 (11 scans each):**
  k = -5 to +5. This covers the baseline prior and n0_m083 at each depth.
- **Quadrature:** at each H0, a cubic spline of ln L in log10 n0 through the
  nodes, integrated against each prior on a 0.001-dex grid over its
  truncated support. The H0 posterior is then summarized as in 12W.
- **One scan per (depth, node), 66 in all**, one HENON task each.

### The step itself (one HENON task)

step(z_d) by the 12O definition, recomputed with the current target at the
five depths, at log10 n0 = -1.810518 and at -1.8406: ten values. 12O's script
(`desi_darksirens_selection-phase12-gpu/logs/analysis_depth_2026-09-29/
depth_criterion.py` under phy220048p darksirens-core-data) is ported to the
current consumer. These are catalog quantities at the fixed calibration
point; they contain no H0 posterior.

### Part C — population-marginalized check on the B1 samples (HENON)

The same variants on the baseline itself, by reweighting the A1 posterior to
the DESI target:

- 1024 equal-weight draws from the A1 limit-4 combined posterior, fixed
  seed; for each draw one value each of M0hat, sigma_M and a uniform number
  u, shared by every variant (common random numbers);
- each variant's n0 is its prior's quantile at u; it is passed to the
  unchanged target through the target's own quantile coordinate under the
  baseline prior;
- each variant's depth through `catalog.z_depth`;
- the variant's weight is L_DESI / L_spectral at the draw, as in B1.

**Centre shifts need no new calls** (Part A on the B1 set). New calls are
needed for n0_w3, n0_free and the four depth variants, 1024 per variant.
**Part C runs for the variants that Part B flags** (any reading band other
than "robust", below) **and always for d200** (the far end of the window).

A one-task timing check comes first: the jitted DESI log-likelihood alone on
a HENON task (the 41.5 s per point of the scans includes the diagnostics, so
it is an upper bound).

## Controls

1. **Part B reproduces the existing check.** The scan at z_depth 0.245 and
   log10 n0 = -1.810518 equals `phase12_5/checks/e_union_spin_gamma_2.5439`
   at the 13 H0 values they share (30 to 120 in steps of 7.5), to 1e-6 in
   ln L.
2. **Each scan records the n0 it used:** the decoded log10 n0 equals its
   node to 1e-9.
3. **Interpolation.** Leave-one-out on the dense nodes: the spline through
   the other nodes predicts each left-out node's ln L within 0.05 at every H0.
   Where a prior holds more than 1% of its mass in a gap that fails this,
   nodes are added there and scanned (about 28 minutes each).
4. **Quadrature.** Trapezoid and spline integration give the same H0 median
   and sd within 0.01 baseline sd for every variant.
5. **Part C baseline.** Part C's baseline reproduces B1's per-draw ln L_DESI
   at the same draws (same code, same inputs).
6. **Step scaling.** At each depth, the ratio of the two steps' (1 + step)
   values matches the n0 ratio, 10^0.0301, within the missing budget's share
   of T.

## What is reported

For each variant, against the baseline of the same part:

- **Δ = (median_variant - median_baseline) / sd_baseline**, the H0 median
  shift in units of the baseline posterior sd;
- **R = sd_variant / sd_baseline**, and the same ratio for the 68% interval
  widths;
- Parts A and C: the effective sample size of the variant's weights, and
  paired bootstrap errors on Δ and R (1000 resamples, the same resample for
  baseline and variant);
- Part B: the number of rejected scan points, the selection N_eff range, and
  the posterior mass within 5 of an H0 grid edge;
- the n0 posterior under each n0 prior (n0 values are not blinded).

Headline numbers:

1. **n0:** Δ and R for n0_m083 (the data-preferred centre); the largest |Δ|
   over ±1 sd; the same over ±2 sd; n0_w3; n0_free.
2. **Depth:** the spread of Δ across the admitted window
   {0.200, 0.215, 0.230, 0.245} (largest minus smallest); d260 separately;
   the step at each depth beside its Δ.
3. **Interaction:** the depth spread again under n0_m083.

Part C's numbers are the result for the baseline. Part B's numbers are the
map at a fixed population; where both exist, both are shown.

## Reading bands (declared before any run)

| band | condition | reading |
|---|---|---|
| robust | \|Δ\| < 0.2 and 0.9 <= R <= 1.1 | the choice does not matter at this precision |
| mild | 0.2 <= \|Δ\| < 0.5, or R in [0.8, 0.9) or (1.1, 1.25] | listed as a systematic in the robustness matrix |
| material | \|Δ\| >= 0.5, or R < 0.8, or R > 1.25 | the owner decides whether the n0 prior or the depth is revised before the result is frozen (P12.7) |

- The window spread of the depth is read with the same thresholds.
- A Δ is **resolved** only if it exceeds twice its bootstrap error. An
  unresolved Δ is reported with its error and read as "below the precision".
- A weighted variant with an effective sample size below **500 of 8,299
  (12Y)** or **200 of 1024 (Part C)** is reported as "not determined"; it is
  not read. Expected for n0_p2 and n0_m2 in Part A (about 2% kept).
- Nothing here changes the baseline automatically.

## Expectations, not thresholds

- **n0 centre shifts small:** the events do not constrain n0 (12Y), and the
  union's likelihood was within 0.7 in log of the empty catalog's (12V, 12W).
  For a centre shift of k sd, Δ is expected near k times the H0-n0
  correlation of the 12Y chain.
- **n0_free and n0_w3:** the events alone then set n0. A larger change than
  for the centre shifts is possible, because n0 sets the height of the host
  density above the depth relative to the galaxies below it.
- **Depth:** whether the window spread found by 12O survives at δ = 0 and the
  corrected spin is the open question; no direction is predicted.
- **Interaction:** n0_m083 is expected to shrink or reverse the step at
  0.245, so the depth spread may differ under it.

## Limits, stated in advance

- Part B is at a fixed population and at fixed M0hat and sigma_M; Part C
  carries the population but its precision depends on B1's effective sample
  size.
- The n0 prior is not re-derived for each depth: every depth uses the prior
  from the window [0.02, 0.30]. n0_m083 is the proxy for a calibration below
  0.245 only.
- δ stays at 0. The luminosity function, m_lim and the footprint map are not
  varied.
- Hemisphere-dependent density (the NOTE's north/south ratio of 1.15) is not
  varied here.

## Compute

All CPU on HENON, account phy220048p, 32 cores and 200 GB per task (as the
12W and 12Y checks), so two tasks per 128-core, 512 GB node.

| part | work | estimate |
|---|---|---|
| A | prior ratios on stored samples | seconds; no likelihood calls |
| step | 10 target states at the calibration point | one task, under 1 hour |
| B | 66 scans × 37 H0 values; 41.5 s per point measured in check e, plus about 2 min of build and compilation | about 28 min per task, **about 31 task-hours (about 1,000 core-hours, 16 node-hours)**; about 5 hours wall at 6 tasks at a time |
| timing | jitted DESI log-likelihood on one task | under 30 minutes |
| C | 1024 calls per flagged variant; at most 6 variants | at 41.5 s per call (upper bound) 12 task-hours per variant; at 10 s, 3 |

- **Expected total: 35 to 75 task-hours (17 to 38 node-hours)**, Part C
  being the uncertain term. If Part C would exceed 40 task-hours, it stops
  for the owner. (On a free A100, at 0.23 s per call, a Part C variant takes
  4 minutes; that is not planned.)
- **Order:** Part B and the step are submitted with
  `--dependency=afterany:1376492`, so they start when the A1 chains finish.
  Recommended also after HENON 1385555 (the A1 stricter-limit reweighting,
  which waits on the same job), so the A1 follow-ups go first. Part A on 12Y
  can run any time. Part C waits for B1 and its acceptance.
- **Outputs:** `/hildafs/projects/phy230054p/magana/darksirens-core-data/
  phase12_5/n0_depth/` (scans `B/d<depth>/n0_<node>/scan.json`, the step,
  Part A and C weights, one summary JSON). Small: under 1 GB.

## Code

- Part B and the controls: the existing scan command, no change.
- Part A, the quadrature, the step port and the summary: a new script on a
  consumer branch `phase12.5/n0-depth-sensitivity` (from `phase12.5/
  free-rate-index`), tested on CPU before the run.
- Part C: B1's reweighting command with the variant's n0 draw and depth; no
  change to the target.

## Not verified

- The jitted per-call CPU time of the DESI target (only the scan's 41.5 s
  per point, with diagnostics, is measured).
- That scans at the outer n0 nodes, far from the counts, stay inside the
  selection guard. Penalised points are reported, not removed.
- That the 12O depth script ports without change to the current consumer.
- B1 is not declared; Part C depends on it.
