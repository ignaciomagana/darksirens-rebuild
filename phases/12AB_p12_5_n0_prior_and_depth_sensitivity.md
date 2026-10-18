# Phase 12AB — P12.5: how the DESI catalog H0 depends on the n0 prior and the depth step (declaration)

## Status

**DRAFT DECLARATION (2026-10-10, for the owner), before any run.** Nothing in
this record has been run. No job is submitted until the owner approves; the
CPU work then runs on HENON **after the A1 chains finish (rita job 1376492)**.

**OWNER DECISION 2026-10-18.** Run as declared, **plus a north/south
host-density variant** (section "North/south variant (added 2026-10-18)"
below), **all on HENON CPU**: account phy220048p, partition HENON, qos henon,
32 CPUs and 200 GB per task, as declared. Part C, after B1, also runs on
HENON. This amendment is written before any production scan. What has run so
far: Part A on the 12Y chain, one-task smokes of Part B and of the step task,
and the north/south identity test; their results are under "Results
(2026-10-18)". The A1 chains (rita 1376492) have finished, so the dependency
declared under Compute is met.

**NORTH/SOUTH SCANS MOVED TO RITA (owner, later on 2026-10-18).** Of the
north/south array on HENON (job 1389006), tasks 0 to 5 are kept and tasks 6
to 23 were cancelled before they started. Those 18 tasks run on one rita
A100 as job 1389048, after a GPU check that matched the CPU scan of the same
node to 1.4e-12 in ln L. The analysis job (1389007) was re-chained. This is
recorded after the move; the scans' configuration, command, lattice and
analysis are unchanged. See "Moved to rita (2026-10-18)" in the north/south
section. The production jobs are listed under "Submitted (2026-10-18)" at
the end.

**PART C STOP RAISED TO 100 TASK-HOURS (owner, 2026-10-18, before Part C was
submitted).** The declared stop at 40 task-hours is raised to 100 task-hours,
so Part C can run through the night on HENON. Nothing else in Part C changes.
See Compute.

**Blinding.** No H0 value from real data (median, interval or shift) is
written here. Results will be appended location-free: shifts in units of the
baseline posterior sd, width ratios, effective sample sizes. The absolute
values stay in the output files and are not sent to the clean-room session.
The same rule holds for the north/south variant.

## Where this sits

P12.5 replaces the fixed GWTC-5 population by its uncertainty
(`phase12_5/P12_5_full_scope.md` under darksirens-core-data):

- step 1 (12Y): the DESI chain with δ fixed at 0 and the rate index sampled;
- stage A0 (12Z): one-parameter population scans, spectral-only;
- stage A1 (12AA, PR #49): spectral-only chains with H0 and the population
  sampled, variance limit 4, running as rita job 1376492;
- stage B1: the A1 posterior reweighted to the DESI catalog likelihood,
  declared separately (12AD, PR #52).

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
  varied in Parts A to C. The north/south variant (added 2026-10-18, next
  section) varies it at a fixed population.

## North/south variant (added 2026-10-18)

Added at the owner's decision of 2026-10-18, before any of its scans. It
uses the reading bands and the blinding rule of the rest of this record.

**Question.** Does a host density that differs between the two hemispheres
change the DESI H0? The cross-check of 2026-10-09
(`phase12_5/completeness_crosscheck/ns_and_n0/NOTE.md`) found about 15% more
galaxies per expected galaxy in the north of the union than in the south. The
DR9 north against DR10 south photometric redshifts carry most of it, and the
per-galaxy photo-z widths partly absorb it. Everything else in this record
uses one pooled n0.

Only the consumer changes; core e7c3007 is untouched.

### Why not core's catalog mixture

Core e7c3007 can mix catalogs, each with its own n0 and footprint. But each
catalog's host fraction is then a free mixture weight (the fcat sticks),
normalised by that catalog's own total. That is a different model from one
field catalog whose n0 depends on the hemisphere, unless the weights are tied
to those totals. The P12.4 target also builds its field state directly from
core's pieces and never goes through core's binder. So the variant is a
per-row n0 multiplier inside the consumer target.

### How the split works

- **Configuration.** A new block `catalog.north_south = {rule,
  log10n0_north, north_prior}`, in `phase12/desi_selection.py`
  (`NorthSouthSplit`, `north_row_mask`).
- **Rule `ls_dr9_north_pixel_centre`.** A catalog row (an nside-64 RING
  pixel) is north when its pixel centre has Dec > 32.375 deg and Galactic
  latitude b > 0. This is the 12Q/12U hemisphere rule applied at the pixel
  centre, as the north/south note of 2026-10-09 did. It marks 8,764 rows
  north (6,204 of them covered): 18.65% of the area and 21.37% of the
  galaxies. It disagrees with the galaxy-level rule for 0.12% of the
  galaxies, all in boundary pixels.
- **Coordinates.** With the split on, the existing calibration coordinate
  (`log10n0_q` under `catalog.calibration_prior`, δ fixed) is the south
  density. A new coordinate, `log10n0_north_q` (or `log10n0_north` under a
  uniform prior), comes right after it and is the north density. Coordinate
  order: H0, M0hat, sigma_M, log10n0_q, log10n0_north_q, gamma.
- **The multiplier.** The field state is built at n0_S. On north rows the
  missing-host density is multiplied by n0_N / n0_S. This is exact because
  that density is linear in n0 when the completeness is the magnitude
  selection f_p Cbar(z).
- **In code.** On north rows log_Nobs is lowered by g = ln(n0_N / n0_S), and
  g is added back to that row's density. The result is
  log(N_obs p_cat + (n0_N / n0_S) dN_miss): the observed galaxies are
  unchanged, the row-mass poison is kept, and at g = 0 it is bit for bit the
  pooled target.
- The north mask is a jit argument. Without a split, the operands, the
  compiled program and the provenance are unchanged.
- `scripts/phase12u_stage.py`: each scan row records the decoded log10 n0
  and log10 n0_north. `scripts/phase12t_common.py`: records the split in the
  build info.

### The baseline of every scan

The Part B baseline: `count_ridge_union_delta0`, δ 0, gamma sampled on
[-2, 6] and held at 2.5439, z_depth 0.245, spin pair 0.04 and 0.10, core
defaults, exact-prior GW inputs, the union catalog and the LS footprint,
M0hat and sigma_M at their prior means.

### The per-hemisphere priors

File `n0_depth/NS/priors/ns_priors.json`, from
`scripts/phase12ab_ns_priors.py` (298 s). The method is the one of the pooled
`count_ridge_union_delta0`:

- the 12U union sample: 22,778,800 galaxies, z 0.02 to 0.30, r <= 21,
  zero-coverage nside-128 pixels removed;
- the union's true luminosity function, M0hat -20.4984, sigma_M 0.5589;
- each hemisphere's own five-component ZERR mixture;
- per hemisphere, the forward fit (δ free), then
  `phase12u_calibrate.count_ridge` over 28 bins of 0.01;
- the prior is N(a, sd) at δ 0, with sd the rms of log10(observed/expected)
  at the forward fit, and bounds by the 12U rule.

**Control.** The same code on the whole union reproduces `union.json`: the
forward fit to 2.6e-8 in log10 n0hat and 3.9e-7 in δ, the ridge a and b to
1e-15, the sd to 6.8e-9.

| hemisphere | galaxies | log10 n0 prior | bounds | ridge slope b | exact ridge value at δ 0 | preset |
|---|---|---|---|---|---|---|
| north (DR9) | 4,867,155 | N(-1.762789, 0.043277) | [-2.298, -1.098] | -0.090265 | -1.761885 | `count_ridge_union_north_delta0` |
| south (DR10) | 17,911,645 | N(-1.822606, 0.036967) | [-2.358, -1.158] | -0.089252 | -1.821759 | `count_ridge_union_south_delta0` |

- **Weights.** Area: north 0.186499, south 0.813501. Expected count per unit
  n0: north 0.188153, south 0.811847.
- **Measured north/south density ratio** 1.1477 (log10 0.059817). With the
  pooled ZERR mixture instead it is 1.1686 (log10 0.067625); that
  sensitivity moves the north centre to -1.756330, about 0.15 north sd.
- **Consistency.** The expected-count-weighted mean of the two hemisphere
  densities differs from the pooled centre by -1.9e-4 dex, about 0.005
  pooled sd.
- **The pooled prior with the ratio imposed** has centres log10 n0_N
  -1.762603 and log10 n0_S -1.822420, essentially the per-hemisphere
  centres.
- As for the pooled prior, the sds measure the counts' departure from one
  power law, not a statistical error.

### The three priors

- **(i) per hemisphere:** the two priors of the table, independent;
- **(ii) pooled with the ratio:** the pooled prior N(-1.810518, 0.036361) on
  l, the log10 of the expected-count-weighted mean density, with the measured
  ratio imposed: log10 n0_S = l - 0.011902, log10 n0_N = l + 0.047915;
- **(iii) the baseline:** the pooled prior on the diagonal n0_N = n0_S.

Variants (i) and (ii) are read against (iii).

### The lattice and the scans

Grid file `n0_depth/NS/grid.json` (from `phase12ab_ns.py plan`). Both axes use
the pooled prior's nodes a + k sd (a -1.810518, sd 0.036361). These are
exactly Part B's dense nodes at z_depth 0.245, so the 7 diagonal nodes
(k = -3 to 3) can be checked against Part B's scans.

- North: k = -3 to 5, log10 n0_N from -1.919601 to -1.628713 (9 values).
- South: k = -4 to 3, log10 n0_S from -1.955962 to -1.701435 (8 values).
- 72 nodes. The lattice covers each of the three priors to at least 3 sd;
  the prior mass on the lattice is at least 0.997 for each.

Each node is one H0 scan, 30 to 120 in steps of 2.5 (37 points), of the split
target at the baseline above: 2,664 points in all. Three nodes per task,
interleaved over the lattice: 24 HENON tasks of 32 CPUs and 200 GB. A task
skips nodes already written, so a resubmission resumes. Output
`NS/scans/n0N_<x>_n0S_<y>/scan.json`, in the phase12u scan schema plus the
node record and the decoded n0.

All 72 nodes are scanned. The 7 diagonal nodes duplicate Part B's d245 scans
and serve as the identity check at production scale; skipping them when
Part B's d245 scans finish first would save about 10%.

### The analysis (`scripts/phase12ab_ns.py analyze`)

- At each H0, a bicubic spline of ln L over the (log10 n0_N, log10 n0_S)
  lattice, integrated on a 0.001-dex grid against each of the three priors.
- The H0 posterior: flat prior on 30 to 120; median, 68% interval and sd from
  a cubic spline in ln L.
- Variants (i) and (ii) against the baseline (iii), with this record's
  reading bands (robust, mild, material): Δ (median shift in baseline sd), R
  (sd ratio) and the 68%-width ratio.
- Also reported: the n0_N and n0_S posteriors under (i), unblinded as for the
  other n0 posteriors.
- **Controls:** leave-one-lattice-line-out interpolation (threshold 0.05 in
  ln L); lattice trapezoid against the spline quadrature; the decoded n0
  within 1e-9 of its node; rejected points; the selection N_eff range; the
  posterior mass within 5 of an H0 grid edge; the prior mass on the lattice;
  the lattice diagonal against Part B's d245 scans, when they exist (the
  identity at production scale).
- **Outputs:** `NS/summary_location_free.json` (no H0 values) and
  `NS/summary_absolute.json` (H0 values; output files only, never in this
  record).
- Tested on a synthetic lattice with a known answer: the posterior means and
  sds match the analytic Gaussian result to about 0.005.

### The identity test (run before any scan): PASSED

HENON job 1388978 through srun, henon02, 32 CPUs, 200 GB. Output
`NS/identity/identity.json`; log `NS/logs/identity_srun.out`.

1. **Split against pooled, plain log-likelihood.** The split target with
   n0_N = n0_S = x, both coordinates under the pooled prior, at six points:
   x = a - 3 sd, a - sd, a, a + 2 sd, a + 4 sd and -1.85, each at a different
   H0 grid value. The difference split minus pooled is exactly 0.0 at all six
   (tolerance 1e-10). The decoded log10 n0 equals x on both coordinates.
2. **Same comparison, diagnostics call,** at 2 points: the largest
   difference over every diagnostics field is exactly 0.0.
3. **The multiplier at full scale.** A third target with every row marked
   north, at (n0_N, n0_S) = (a + 2 sd, a - sd) and (a - 2 sd, a + sd),
   against the pooled target at n0_N: differences +2.3e-13 and -2.3e-13. For
   scale, the pooled ln L at n0_N minus that at n0_S is -0.148 and +0.633 at
   those two points, so the check is sensitive.
4. **Sanity value.** The real split at the per-hemisphere centres differs
   from the pooled target at a by -0.27 in ln L at one test point. This is a
   likelihood difference, not an H0 value.

**Timing** (steady state, henon02, 32 CPUs): 79 s per point for both the
jitted plain log-likelihood and the diagnostics call (78.0 to 80.0 s; a
repeat call took 82.6 s). The first call adds about 62 s of compilation;
building the target takes 12 to 20 s. Check e measured 41.5 s per point on
henon08, and the Part B smoke on henon02 also took 79 s, so the cost depends
on the node.

**Provenance caveat.** The run's log stamps the base commit 0d75b40 with the
working tree dirty. The committed 10a42de differs from what ran only in the
tests, the launchers' time limit and a trapezoid helper used by `analyze`;
the target code and the identity command are identical.

### Tests

`tests/test_north_south_n0.py`, 11 tests: the configuration and its
refusals; the identity at three n0 values and with gamma sampled; every row
marked north, or every row marked south, equals the pooled target at that
n0; a mixed mask, per sample, equals core's density stitched from states
built at n0_N and n0_S (to 1e-12); the mask is a jit argument and calls do
not recompile. Two existing tests were updated for the new optional operand
and the two new presets. The first full run gave 103 passed and 3 failed,
all three cases in those two tests before their update; after it they passed
on rerun. The new file passes.

### Moved to rita (2026-10-18)

A later owner decision of 2026-10-18 moved most of the north/south scans
from HENON to one rita A100.

- **Recorded after the move.** The configuration, the scan command, the
  lattice, the analysis and the blinding rule are unchanged. Only the
  machine that computes 54 of the 72 nodes changes.

**The jobs.**

- **Submitted first:** HENON array job 1389006, 24 tasks of three lattice
  nodes each, six at a time, as declared above.
- **Kept on HENON:** tasks 0 to 5 (18 nodes), started between 09:20 and
  09:58 UTC.
- **Cancelled on HENON:** tasks 6 to 23 (54 nodes), before any of them
  started.
- **Run on rita instead: job 1389048.**
  - Settings: account phy220048p, partition RITA-GPU, qos rita, one
    a100-80, 16 CPUs, 64 GB, a 6-hour limit. It started at 10:05 UTC.
  - Launcher: `n0_depth/NS/phase12ab_ns_scan_rita.sbatch`.
  - It runs tasks 6 to 23 one after another, through the GPU route committed
    on the north/south branch (`slurm/phase12ab_ns_scan_gpu.sh` at 10a42de,
    clean checkout). That is the same scan command, grid, arguments and
    output root (`NS/scans/`) as the HENON array.
  - A node already written is skipped, and the analysis reads node files
    wherever they were made.
  - No node is written by two runs: the rita job was submitted only after
    the HENON tasks for its indices had been cancelled.

**GPU check before the move** (rita job 1389046, 09:56 UTC;
`NS/gpu_check/compare.json`).

- The first node of task 0 (log10 n0_N −1.919601, log10 n0_S −1.955962) was
  scanned on a rita A100 with the same command.
- It was written into a separate grid and root (`NS/gpu_check/`), never into
  `NS/scans/`.
- It was compared at all 37 H0 values with HENON's CPU scan of the same node
  (task 0, henon08):

| field | largest \|GPU − CPU\| |
|---|---|
| ln L | 1.4e-12 |
| selection log correction | 1.4e-12 |
| ln μ | 3.6e-15 |
| selection N_eff | 7.1e-10 (relative about 1e-14) |
| total Monte Carlo variance | 8.0e-15 |
| sampled coordinates | 0 (identical) |
| accepted flags | identical at every point |

- These are likelihood differences, not H0 values.
- Time per point: 0.27 s on the A100 against 44 s on henon08. Building the
  target took 15 s on both.

**The split of the work.** 18 nodes (666 points) are scanned on HENON and 54
nodes (1,998 points) on rita. On rita each task of three nodes takes about 2
minutes, so the 18 tasks finish in under an hour. Each HENON task takes 1.4
to 2.4 hours at 44 to 79 s per point.

**The analysis job re-chained.** The analysis (HENON job 1389007,
`n0_depth/phase12ab_analysis_henon.sbatch`: Part B's analysis, the
north/south analysis, the merge) now waits for:

- the Part B array (1389004) to succeed (`afterok`);
- the rita job (1389048) to succeed (`afterok`);
- the HENON array's tasks (1389006) to end (`afterany`, because its
  cancelled tasks would never satisfy `afterok`).

The step task (1389005) has already finished. A failed HENON task cannot
pass silently: `phase12ab_ns.py analyze` stops if any of the 72 node scans
is missing, and writes `missing_nodes.json`.

**Blinding.** The rule is unchanged.

- The rita log prints only, per point, whether it was accepted and the N_eff
  over its threshold.
- The analysis prints location-free numbers.
- Absolute H0 values go only to the `*_absolute.json` files.

## Compute

All CPU on HENON (owner decision 2026-10-18): account phy220048p, partition
HENON, qos henon, 32 cores and 200 GB per task (as the 12W and 12Y checks),
so two tasks per 128-core, 512 GB node. Part C, after B1, also on HENON.
**Exception (later owner decision, 2026-10-18):** 54 of the 72 north/south
nodes run on one rita A100 (section "Moved to rita (2026-10-18)").

The cost per point depends on the node: 41.5 s per scan point on henon08
(check e), 79 s on henon02 (the Part B smoke and the north/south identity
test). Each target adds about 1.5 minutes of build and first compilation.
The jitted log-likelihood alone is not faster than a scan point on CPU (77 s
per call in the step smoke, 79 s in the identity test), so the 41.5 s of the
draft is not an upper bound for Part C. The ranges below span the two
nodes.

| part | work | estimate |
|---|---|---|
| A | prior ratios on stored samples | done, about 6 seconds |
| step | 10 target states at the calibration point | one task, under 1 hour |
| B | 66 scans × 37 H0 values, one scan per task (array of 66, 6 at a time, 2-hour limit) | 30 to 55 task-hours |
| north/south | 72 nodes × 37 H0 values (2,664 points), 24 tasks of three nodes (6-hour limit), then one analysis task under 1 hour. As run since 2026-10-18: tasks 0 to 5 on HENON, tasks 6 to 23 on one rita A100 | declared 31 to 59 task-hours; as run, 8 to 14 HENON task-hours plus under 1 rita GPU-hour |
| C | 1024 calls per variant: d200 always, plus the variants Part B flags (at most 6 in all) | 12 to 22 task-hours per variant |

- **Expected total: about 75 to 140 task-hours (38 to 70 node-hours)** with
  Part C at d200 only; each further Part C variant adds 12 to 22. If Part C
  would exceed 100 task-hours, it stops for the owner. The declared stop was
  40 task-hours; the owner raised it to 100 on 2026-10-18, before Part C was
  submitted.
- **Order:** Part A has run. The step task, Part B and the north/south scans
  are submitted after this amendment is pushed; the A1 chains (rita 1376492)
  and their follow-ups have finished, so there is no dependency. The
  north/south analysis is submitted with `--dependency=afterok` on its scan
  array, and Part B's analysis after Part B's scans. Part C waits for B1
  (12AD) and its acceptance.
- **To submit the north/south variant**, from the consumer worktree
  `phase12_5/repo_12AB_ns`:

  ```text
  sbatch slurm/phase12ab_ns_scan_henon.sbatch
  sbatch --dependency=afterok:<id> slurm/phase12ab_ns_analyze_henon.sbatch
  ```

- **Outputs:** `/hildafs/projects/phy230054p/magana/darksirens-core-data/
  phase12_5/n0_depth/`: `A/` (Part A), `B/d<depth>/n0_<node>/scan.json`,
  `step/`, `C/`, `NS/` (priors, grid, identity test, scans and the two
  summaries), `smoke/` and `logs/`. Small: under 1 GB.

## Code

Consumer repository `ignaciomagana/desi_darksirens_selection`. Both branches
are pushed to origin; neither is merged and no PR is opened.

- **`phase12.5/n0-depth`, 4cf6bd5f6cc55fdc4bec882b8dec16b147088a5d** (from
  `phase12.5/free-rate-index` 0d75b40; worktree `phase12_5/repo_12AB`; the
  draft called it `phase12.5/n0-depth-sensitivity`).
  `scripts/phase12_5_n0_depth.py`: Part A, the Part B task map and analysis
  (controls 1 to 4, the cubic-spline quadrature of each declared n0 prior on
  a 0.001-dex grid, the reading bands, the variants Part C must run), the
  step task (12O's `depth_criterion.py` ported, plus the jitted timing) and
  the Part C driver. Launchers `slurm/phase12_5_n0_depth_{B,step,C}.sbatch`.
  The Part C driver is written against B1's interface as this record
  describes it; it is untested until B1's outputs exist.
- **One configuration change in Part B.** The scans use the existing scan
  command, but declare a uniform calibration prior on the baseline bounds
  [-2.346, -1.146] with δ fixed at 0, so the scan coordinate is log10 n0
  itself. Under the baseline prior the quantile coordinate rounds to 1 beyond
  about +8 prior sd and cannot carry the outer nodes. The likelihood never
  sees the prior density; the n0 priors are applied afterwards by quadrature,
  as declared. The Part B smoke reproduces check e exactly.
- **`phase12.5/n0-north-south`, 10a42dea9e4ebc7237d2129c54e21b1b319ec1e2**
  (from `phase12.5/free-rate-index` 0d75b40; worktree
  `phase12_5/repo_12AB_ns`): the north/south split in the target
  (`phase12/desi_selection.py`), `scripts/phase12ab_ns_priors.py`,
  `scripts/phase12ab_ns.py` (plan, identity, scan, analyze), the scan-row and
  build-info records, the HENON launchers and `tests/test_north_south_n0.py`.
- Part C: B1's reweighting command with the variant's n0 draw and depth; no
  change to the target.

## Not verified

- That scans at the outer n0 nodes, far from the counts, stay inside the
  selection guard. Penalised points are reported, not removed.
- That the 12O depth script, which ran end to end at two depths in the smoke,
  gives all ten values without change.
- B1 (12AD) has no outputs yet; Part C depends on them.
- North/south: the identity at production scale (the lattice diagonal
  against Part B's d245 scans) and the lattice interpolation are checked only
  after the scans. The 0.12% of galaxies on which the pixel-centre rule and
  the galaxy-level rule disagree are not propagated.

## Results (2026-10-18)

Location-free, as the blinding rule requires. Absolute values are in the
output files only.

### Part A — prior reweighting of the 12Y chain

Run on the 12Y chain (8,299 equal-weight samples) at the committed code
4cf6bd5, in about 6 seconds. Outputs `n0_depth/A/part_a.json`
(location-free) and `part_a_absolute.json` (absolute values, blinded). The
correlation between H0 and log10 n0 in the chain is +0.098. Δ is in units of
the baseline sd and R is the sd ratio, each with a paired-bootstrap error
(1000 resamples).

| variant | centre shift | ESS (fraction kept) | Δ | R | 68%-width ratio | k × corr | reading |
|---|---|---|---|---|---|---|---|
| n0_m083 | -0.83 sd | 4,438 (53%) | -0.082 ± 0.014 | 0.995 ± 0.007 | 1.026 ± 0.011 | -0.081 | robust |
| n0_p1 | +1 sd | 3,414 (41%) | +0.099 ± 0.027 | 0.999 ± 0.009 | 0.985 ± 0.017 | +0.098 | robust |
| n0_m1 | -1 sd | 3,375 (41%) | -0.099 ± 0.017 | 0.993 ± 0.009 | 1.036 ± 0.012 | -0.098 | robust |
| n0_p2 | +2 sd | 594 (7%) | +0.194 ± 0.091 | 0.997 ± 0.026 | 1.032 ± 0.039 | +0.196 | robust, close to the 0.2 band edge |
| n0_m2 | -2 sd | 440 (5%) | | | | | not determined (ESS below 500); not read |

- Every Δ follows k times the correlation, as the record expected. Every
  determined Δ is resolved (more than twice its error).
- The ±2 sd variants keep 5 to 7% of the weight, not the 2% the record
  expected; n0_p2 is just above the limit of 500.
- The n0 posterior equals the prior: baseline posterior sd 0.0354 against a
  prior sd of 0.0364 (posterior median -1.8145, prior centre -1.8105).
- Headline n0 numbers from Part A: Δ for n0_m083 is -0.082 (R 0.995); the
  largest |Δ| over ±1 sd is 0.099; over ±2 sd, only +2 sd is determined, at
  0.194. n0_w3 and n0_free come from Part B.

### Part B smoke: PASS on HENON

- One task of the actual sbatch (job 1388972, array index 6: depth 0.245,
  log10 n0 -1.810518, at the H0 grid values 45, 67.5 and 90; henon02).
  Compared with `phase12_5/checks/e_union_spin_gamma_2.5439/scan.json`, the
  corrected-spin, gamma 2.5439, δ 0 union scan of 2026-10-08 and control 1's
  declared reference: max |d ln L| = 0.0 at all 3 points. The decoded
  log10 n0 equals the node exactly, and the selection N_eff per threshold is
  identical. Output `n0_depth/smoke/B/`.
- An earlier srun attempt ran as a step inside the miko holder allocation,
  not on HENON. It is kept in `n0_depth/smoke/B_miko_step` and also matched
  (max |d ln L| 2.3e-13).
- **Step-task smoke** (job 1388974, henon01, depths 0.245 and 0.260 at the
  baseline n0): it ran end to end. The step is -0.034 at 0.245 and -0.072 at
  0.260 (catalog quantities, not blinded). T/E just above the depth is
  1.000, the missing budget is about 15% of T, and the target's gathered
  state equals the grid state exactly. The jitted log-likelihood took 77 s
  per call on CPU and the diagnostics call 50 s. This is the declared timing
  check.
- **The Part B analysis on synthetic scans** matches a direct 2-D integral
  to 7e-6 in Δ and R; all four controls pass, and the failure paths were
  exercised.
- Repository tests on `phase12.5/n0-depth`: 381 pass.

### North/south identity test: PASSED

See "The identity test" in the north/south section above.

### Submitted (2026-10-18)

The production jobs submitted since the amendment above. No results yet;
they are appended location-free.

- **The step task:** HENON job 1389005 (finished).
- **Part B:** HENON array 1389004, 66 tasks, six at a time.
- **North/south:** HENON array 1389006, tasks 0 to 5, and rita job 1389048,
  tasks 6 to 23 (section "Moved to rita (2026-10-18)").
- **The analysis:** HENON job 1389007, after Part B and both north/south
  jobs.
- **Rerun of one Part B task (2026-10-18, 20:45 UTC).** Task 65 of 1389004
  failed at start-up on henon08 ("TaskProlog failed", 0 s, nothing run). The
  other 65 scans completed. Task 65 was resubmitted unchanged as HENON job
  1389664 (array index 65, henon08 excluded). The analysis job 1389007,
  which the failed task had left unable to start, now depends on
  `afterok:1389664`. Its other dependencies were already met.
- **Part C** waits for B1 (12AD) and its acceptance.
