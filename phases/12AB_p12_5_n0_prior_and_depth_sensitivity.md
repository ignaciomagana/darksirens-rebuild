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

**PARTS A AND B, THE STEP AND NORTH/SOUTH: DONE (analysis job 1389007,
2026-10-18 21:10 UTC).** Every control passes. All 15 Part B variants read
robust, and so do both north/south variants. No variant is flagged, so
**Part C runs for d200 only.** The location-free results are under "Results
(2026-10-18)".

**PART C SUBMITTED (2026-10-18, 21:43 UTC): d200 only.** Part C runs on B1's
evaluated draws, through B1's own target.

- **Jobs:** HENON array 1389692, 9 tasks, six at a time: control 5 and eight
  slices of 128 draws. The analysis job 1389693 follows with `afterok` on
  the array.
- **Plan:** 1,056 calls, 13 to 24 task-hours, under the 100 task-hour stop.
- **Code:** before submission the driver was fitted to B1's actual outputs
  (commits 0d75a0a and 794cfde). It passed a timing check and a smoke on
  HENON.

See "Part C (2026-10-18): fitted to B1, tested, submitted" under Results,
and Compute.

**PART C DONE (2026-10-19, 00:48 UTC): the depth reads mild with the
population free.** d200 against d245: Δ = −0.277 ± 0.039 (resolved), R =
1.014. At a fixed population (Part B) the same depth read −0.155, robust.
With the n0 centre at −0.83 sd as well: Δ = −0.365 ± 0.078, mild. The n0
centre shifts on B1's full set are robust up to ±1 sd (|Δ| ≤ 0.13); ±2 sd
are not determined. Control 5 passed (1.3e-10). Per the declared bands, the
depth goes into the robustness matrix as a systematic; the baseline is
unchanged. Task 8 was rerun after a node fault (job 1389729). See "Part C
(2026-10-19)" at the end of Results.

**ERRATUM (independent review, 25 Oct 2026): the merged file predates Part C.** `n0_depth/summary_location_free.json`
was written once, by the analysis job at 21:10 UTC on 2026-10-18, before Part C ran, and was not rewritten; its
`part_c` block is stale. The record's text is right. See "Amendment (25 Oct 2026): independent review" at the end.

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
- **Part C as submitted (2026-10-18), d200 only:**
  - work: 1,056 calls (1,024 d200 draws plus the 32 draws of control 5), in
    9 tasks of 32 CPUs and 200 GB with a 4-hour limit;
  - rate: 41.5 s per call measured by the timing check on henon04, against
    79 s on the slowest HENON nodes (henon01 and henon02);
  - estimate: 13.1 to 24.1 task-hours, 1.6 to 2.9 hours per slice task,
    under the 100 task-hour stop;
  - the plan is `n0_depth/C/plan.json`.
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
- Part C: B1's own target, built from B1's recorded configuration with the
  variant's depth (and, for n0_w3 and n0_free, the uniform encoding); no
  change to the target.
- **Part C fitted to B1 (2026-10-18, before the Part C array):**
  - the commits: 0d75a0a and 794cfde on `phase12.5/n0-depth`, pushed (no
    PR, no merge);
  - the driver: `partc-prepare` reads B1's evaluation files and summary,
    `partc-evaluate` loads B1's script from its clean worktree at 596651c,
    and `partc-plan` gives a task-hour estimate and the stop;
  - `partc-analyse` gets a launcher,
    `slurm/phase12_5_n0_depth_C_analyse.sbatch`;
  - tests: 386 repository tests pass on HENON (job 1389684).

  See "Part C (2026-10-18): fitted to B1, tested, submitted" under Results.

## Not verified

- That scans at the outer n0 nodes, far from the counts, stay inside the
  selection guard. Penalised points are reported, not removed.
- That the 12O depth script, which ran end to end at two depths in the smoke,
  gives all ten values without change.
- B1 (12AD) has no outputs yet; Part C depends on them. *(2026-10-18: B1 is
  done and accepted. Control 5 at full size, 32 draws, and the d200 run are
  checked by the Part C array and its analysis. The no-call centre shifts on
  B1's set are computed in that analysis.)*
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

### Part B — the map at a fixed population

The 66 scans (HENON array 1389004 plus the rerun 1389664) cover 37 H0 values
each, 2,442 points in all, at the committed code 4cf6bd5. They were analysed
by job 1389007 (`phase12_5_n0_depth.py analyse --require-complete`, 21:10
UTC). Outputs: `n0_depth/B/summary.json` (location-free) and
`B/summary_absolute.json` (absolute values, blinded). The merged file is
`n0_depth/summary_location_free.json` *(25 Oct 2026: written before Part C; its Part C block is stale. See the erratum in Status.)*.

Δ is in units of the sd of the baseline (d245, n0_base) and R is the sd
ratio. Each variant is a quadrature over the same scans, so Part B has no
bootstrap errors.

| variant | depth | n0 prior | Δ | R | 68%-width ratio | reading |
|---|---|---|---|---|---|---|
| baseline | 0.245 | n0_base | 0 | 1 | 1 | |
| n0_m083 | 0.245 | -0.83 sd | +0.000 | 0.993 | 0.995 | robust |
| n0_p1 | 0.245 | +1 sd | +0.008 | 1.009 | 1.006 | robust |
| n0_m1 | 0.245 | -1 sd | +0.001 | 0.992 | 0.993 | robust |
| n0_p2 | 0.245 | +2 sd | +0.026 | 1.017 | 1.012 | robust |
| n0_m2 | 0.245 | -2 sd | +0.012 | 0.984 | 0.987 | robust |
| n0_w3 | 0.245 | width × 3 | +0.022 | 0.992 | 0.993 | robust |
| n0_free | 0.245 | flat | +0.056 | 0.988 | 0.988 | robust |
| d230 | 0.230 | n0_base | -0.060 | 0.988 | 0.988 | robust |
| d215 | 0.215 | n0_base | -0.119 | 0.996 | 0.984 | robust |
| d200 | 0.200 | n0_base | -0.155 | 1.018 | 1.007 | robust |
| d260 | 0.260 | n0_base | +0.046 | 1.021 | 1.022 | robust |
| d230/n0_m083 | 0.230 | -0.83 sd | -0.068 | 0.984 | 0.982 | robust |
| d215/n0_m083 | 0.215 | -0.83 sd | -0.130 | 0.997 | 0.986 | robust |
| d200/n0_m083 | 0.200 | -0.83 sd | -0.156 | 1.023 | 1.015 | robust |
| d260/n0_m083 | 0.260 | -0.83 sd | +0.054 | 1.010 | 1.011 | robust |

**Diagnostics.**

- No scan point is rejected (0 of 2,442).
- The selection N_eff over its threshold is 8.3 to 37.1 at z_depth 0.245,
  where the lowest values sit at the outer n0 nodes. At the other depths it
  is 13.2 to 36.2.
- For every variant, the posterior mass within 5 of an H0 grid edge is below
  2e-13.
- The scan nodes cover at least 0.999996 of every prior's mass.

**Controls.**

| control | result | tolerance | |
|---|---|---|---|
| 1. reference scan (check e) | max \|d ln L\| 0.0 at the 13 shared H0 values; decoded n0 identical | 1e-6 | PASS |
| 2. decoded n0 | max \|decoded − node\| 0.0 over all 66 scans | 1e-9 | PASS |
| 3. leave-one-out interpolation | largest error 2.6e-4 in ln L, at any H0 and node; no node added | 0.05 | PASS |
| 4. trapezoid against spline | medians within 0.0010 baseline sd, sds within 7.5e-5 | 0.01 | PASS |

Control 6 belongs to the step and is reported in the step's section below.

**Headline numbers** (as declared under "What is reported"):

1. **n0.** n0_m083 gives Δ +0.000 (R 0.993). The largest |Δ| over ±1 sd is
   0.008 (n0_p1) and over ±2 sd 0.026 (n0_p2). n0_w3 gives +0.022 (R 0.992)
   and n0_free +0.056 (R 0.988).
2. **Depth.** The window spread is 0.155, from d200 (-0.155) to d245 (0),
   and the R farthest from 1 is 1.018 (d200). That is robust. d260 gives
   +0.046 (R 1.021).
3. **Interaction.** Under n0_m083 the window spread is 0.157, and the R
   farthest from 1 is 1.023 (d200). That is robust. Measured against d245
   under n0_m083 itself: d200 -0.158 (R 1.030), d215 -0.131, d230 -0.069,
   d260 +0.054.

**The n0 posterior** (n0 values are not blinded):

- under the baseline: median -1.821, sd 0.035 (prior sd 0.036);
- under n0_w3 (prior sd 0.109): median -1.859, sd 0.076;
- under n0_free (flat on [-2.346, -1.146]): median -1.898, sd 0.102.

**Readings.**

- All 15 variants read robust: every |Δ| is below 0.2 and every R lies in
  [0.98, 1.03].
- With a prior wide enough, the events alone do constrain n0, but the H0
  median moves by at most 0.056 sd.
- The depth is the larger of the two effects, and it moves the median
  monotonically from d260 to d200. The whole window still stays inside the
  robust band.
- **Part C runs for d200 only.** No variant is flagged, and d200 runs
  always, as declared.
- **Compared with Part A.** On the 12Y chain the centre shifts followed
  k × corr (corr +0.098), for example Δ -0.082 for n0_m083. At a fixed
  population, with M0hat and sigma_M at their prior means, the same shifts
  give |Δ| ≤ 0.026 up to ±2 sd. What separates the two is what the chain
  samples and Part B holds fixed: the rate index, M0hat and sigma_M.

### The step (HENON job 1389005, henon04)

The step was computed at the five depths and two n0 values (ten values), at
12O's calibration point. Output `n0_depth/step/step.json`. These are catalog
quantities, not blinded.

| depth | step, log10 n0 -1.810518 (baseline) | step, -1.8406 (n0_m083) | missing share of T (baseline) | control 6: deviation |
|---|---|---|---|---|
| 0.200 | +0.041 | +0.105 | 14.0% | 0.94% |
| 0.215 | +0.018 | +0.081 | 14.3% | 0.96% |
| 0.230 | +0.009 | +0.071 | 14.5% | 0.97% |
| 0.245 | -0.034 | +0.024 | 15.2% | 1.02% |
| 0.260 | -0.072 | -0.016 | 15.9% | 1.06% |

- **Above the depth.** T/E just above the depth is 1.000 at every depth and
  both n0.
- **Gathered state.** The target's gathered state equals the grid state
  exactly (relative difference 0.0).
- **Control 6 (step scaling): PASS at every depth.** The ratio of the two
  (1 + step) values is 1.0603 to 1.0617, against the n0 ratio
  10^0.0301 = 1.0717. The relative deviation, 0.94 to 1.06%, lies inside the
  missing budget's share of T (14 to 16%).
- **The sign of the step.** At the baseline n0 the step changes sign
  between 0.230 and 0.245. Under n0_m083 it changes sign between 0.245 and
  0.260, and the negative step at 0.245 becomes +0.024, as expected.
- **The step against Δ.** Across depths the two move in opposite
  directions, each monotonically. From d200 to d260 the step falls from
  +0.041 to -0.072, while Δ rises from -0.155 to +0.046.
- **Timing** (henon04, 32 CPUs). The jitted log-likelihood takes 42.5 s per
  call (median of 5, range 42.3 to 42.5). The first call, with compilation,
  takes 86 s, and the diagnostics call 43.2 s. The smoke on henon01 took
  77 s.

### North/south

The 72 lattice nodes (2,664 points) ran as HENON array 1389006 (tasks 0 to
5) and rita job 1389048 (tasks 6 to 23). They were analysed by job 1389007
(`phase12ab_ns.py analyze`, 10a42de). Output `NS/summary_location_free.json`;
`NS/summary_absolute.json` holds the blinded absolute values. Both variants
are read against the baseline (iii).

| variant | Δ | R | 68%-width ratio | prior mass on the lattice | reading |
|---|---|---|---|---|---|
| (i) per-hemisphere priors | +0.006 | 1.002 | 1.001 | 0.998 | robust |
| (ii) pooled prior with the ratio | +0.011 | 1.000 | 0.999 | 0.999 | robust |

**n0 under (i)** (not blinded):

- north: mean -1.777, sd 0.041, against the prior N(-1.763, 0.043);
- south: mean -1.824, sd 0.034, against the prior N(-1.823, 0.037);
- posterior over prior sd: 0.94 (north) and 0.93 (south);
- log10(n0_N / n0_S): +0.047 ± 0.051, against the measured 0.060.

**Controls: all pass.**

- No point is rejected.
- The selection N_eff over its threshold is 14.4 to 35.7.
- Each decoded n0 lies within 1.1e-15 of its node.
- Leave-one-lattice-line-out: the largest ln L error is 2.5e-4 (tolerance
  0.05).
- Lattice trapezoid against the spline: Δ and R each differ by 3e-6.
- **Identity at production scale:** the 7 diagonal nodes equal Part B's d245
  scans to 1.1e-12 in ln L.
- The posterior mass within 5 of an H0 grid edge is below 4e-14.
- The baseline prior's mass on the lattice is 0.997.

**Reading.** A host density that differs between the hemispheres does not
change the DESI H0 at this precision.

**Compute used.**

- Part B: 32.9 HENON task-hours, 0.44 to 0.83 hours per task (65 tasks plus
  the rerun; declared 30 to 55).
- The step: 0.7 task-hours.
- North/south: 9.2 HENON task-hours plus 0.6 rita GPU-hours.
- The analysis: 14 seconds.

### Part C (2026-10-18): fitted to B1, tested, submitted

B1 is done and accepted, and its population-free DESI value is the headline
(owner, 2026-10-18). This entry is written before any Part C result, and
records how Part C uses B1.

**What B1 provides.**

- B1 evaluated 4,096 equal-weight draws of each of the 8 A1 chains: two H0
  parts, 16,384 points in each.
- Each point carries one draw from the priors of M0hat, sigma_M and u (u is
  the target's `log10n0_q`), and B1 stored ln L_DESI and ln L_spectral for
  it.
- B1 has no command that evaluates a given draw set, which is what the
  draft driver assumed. The driver was rewritten around what B1 does have.

**How Part C reads B1** (`partc-prepare`).

- **B1's weights.** It rebuilds B1's combined weights from the evaluation
  files and checks them against B1's summary. The largest weight difference
  is 1.9e-18 (the largest weight is 6.7e-4), and the A1 part weights are
  identical. B1 exited 0 and is complete.
- **The draw set.** It takes the declared 1024 equal-weight draws of the A1
  combined posterior (seed 20261018) from B1's points:
  - each H0 part gets a share by its A1 part weight (largest remainders);
  - within a part, the draws are uniform without replacement;
  - the set is put in a random order;
  - each draw keeps B1's coordinates and nuisance draws, so M0hat, sigma_M
    and u are shared by every variant, as declared;
  - each draw's mass in the A1 mixture (its part's weight over the part's
    number of draws) corrects the rounding.
- **The baseline weight** is that mass times L_DESI / L_spectral, with B1's
  stored values. It is B1's estimator on the 1024 draws. Against B1's full
  set this baseline has Δ -0.059 and R 0.946 (ESS 639, limit 200). Every
  variant is compared with this baseline on the same draws.
- **d200** keeps B1's own n0 coordinate, the baseline prior's quantile at u,
  as declared; only `catalog.z_depth` changes, to 0.200. n0_w3 and n0_free,
  which are not run, would use Part B's uniform encoding.
- **The centre shifts** (Part A on the B1 set) are prior ratios on B1's full
  weighted set: 32,768 points, ESS 11,850, with the ESS limit of 500 used for
  12Y. They need no calls and are computed by `partc-analyse`.

**How a task runs** (`partc-evaluate`).

- It loads B1's script from its worktree (`phase12_5/repo_B1`) and refuses
  unless that worktree is clean at B1's commit 596651c.
- It rebuilds B1's target from B1's recorded configuration, with the inputs
  sha256-checked.
- It calls B1's per-point diagnostics, as B1 did.
- **Checks:** the baseline variant's configuration must equal B1's digest,
  and the coordinate and guard must equal B1's.
- It checkpoints every 8 draws, and a rerun resumes.

**Code** (on `phase12.5/n0-depth`, pushed; no PR):

- **0d75a0a** puts Part C on B1's outputs.
- **794cfde** fixes the population order. B1 stores its records with sorted
  keys, so the population entries of its recorded configuration come back
  in alphabetical order, not in the target's coordinate order. They are now
  put back in coordinate order, with B1's digest unchanged.
- The first smoke and timing jobs (1389681 and 1389680) stopped at the
  coordinate check, after the build and before any call. That is how the
  order problem showed up.
- **Tests:** 386 repository tests pass on HENON (job 1389684, henon05, 14
  minutes). That is 381 from before plus 5 new Part C tests on a synthetic
  B1: weights, selection, encoding, plan and stop, evaluation with resume,
  and the analysis against direct weights.

**Timing check: PASS** (job 1389682, henon04; the control-5 task on its
first 4 draws, written to `n0_depth/smoke/C_timing/`).

- The jitted log-likelihood alone takes 41.5 s per call (median of 5, range
  41.3 to 41.6). Its first call, with compilation, takes 85 s.
- B1's diagnostics call, which Part C uses, takes 41.4 s per call.
- Building the target takes 15 s.
- At these 4 draws, Part C's baseline equals B1's stored ln L_DESI, computed
  on an H100, to 4.5e-13.

**Smoke: PASS** (job 1389683, henon06; the first d200 slice on 3 draws,
written to `n0_depth/smoke/C/`).

- It ran end to end: 41.3 s per call, with the target built in 18 s.
- ln L at d200 minus B1's baseline ln L is -0.33 to -0.10 at the three
  draws. These are likelihood differences, not H0 values.

**Plan** (`n0_depth/C/plan.json`).

- d200 only, because Part B flags no variant.
- 9 tasks: control 5 (the first 32 baseline draws) and 8 slices of 128 d200
  draws, 1,056 calls in all.
- 13.1 to 24.1 task-hours at 41.5 to 79 s per call, or 1.6 to 2.9 hours per
  slice task. That is under the 100 task-hour stop.

**Submitted** (21:43 UTC).

- **The scans:** HENON array 1389692, tasks 0 to 8, six at a time, each with
  32 CPUs, 200 GB and a 4-hour limit (`slurm/phase12_5_n0_depth_C.sbatch` at
  794cfde).
- **The analysis:** HENON job 1389693, with `afterok` on the array
  (`slurm/phase12_5_n0_depth_C_analyse.sbatch`). It writes
  `n0_depth/C/summary.json` (location-free) and `C/summary_absolute.json`
  (blinded).
- The analysis exits 3 if control 5 fails or any draw is missing.

### Part C (2026-10-19): the depth reads mild with the population free

**Jobs.** HENON array 1389692: tasks 0 to 7 finished in 0.4 to 1.5 hours
each. Task 8 failed at node start-up ("TaskProlog failed", 0 s, henon06),
the same node fault as Part B's task 65. It was rerun unchanged as job
1389729 (henon05, 1.5 h), excluding henon06 and henon08, and the analysis
1389693 was re-chained onto it. The analysis ran on 2026-10-19 at 00:46 UTC
at the committed code 794cfde, clean, and wrote `n0_depth/C/summary.json`
(location-free) and `C/summary_absolute.json` (blinded). In all: 1,056
calls, about 12.5 task-hours, under the 100 task-hour stop.

**Control 5: PASS.** At the first 32 baseline draws, Part C's baseline
equals B1's stored ln L_DESI to 1.3e-10 (tolerance 1e-6). No draw is
missing.

**The baseline.** On its 1024 draws (37 in the lower H0 part, 987 in the
upper, by A1's part weights), Part C's baseline has an effective sample
size of 639. Against B1's full set (ESS 11,850) it gives Δ = −0.059, R =
0.946 and a 68%-width ratio of 0.927. That is the subsampling noise of 1024
draws. The variants below are read against this baseline: the same draws,
weights and random numbers (common random numbers), so their errors are
paired.

**The variants** (Δ in the sd of Part C's baseline; errors from 1000 paired
bootstrap resamples):

| variant | ESS (of 1024) | Δ | R | 68%-width ratio | reading | Part B at a fixed population |
|---|---|---|---|---|---|---|
| d200 | 658 | **−0.277 ± 0.039** | 1.014 ± 0.009 | 1.016 ± 0.030 | **mild**, resolved | Δ −0.155, R 1.018: robust |
| d200 with n0_m083 | 306 | **−0.365 ± 0.078** | 0.982 ± 0.026 | 0.946 ± 0.037 | **mild**, resolved | Δ −0.156, R 1.023: robust |

**Centre shifts on B1's full set** (no new calls; Δ in the sd of B1's full
set; ESS limit 500):

| variant | n0 centre shift | ESS (of 11,850) | Δ | R | reading |
|---|---|---|---|---|---|
| n0_m083 | −0.83 sd | 4,605 | −0.099 ± 0.014 | 0.970 | robust |
| n0_p1 | +1 sd | 4,755 | +0.129 ± 0.014 | 1.031 | robust |
| n0_m1 | −1 sd | 3,283 | −0.123 ± 0.018 | 0.964 | robust |
| n0_p2 | +2 sd | 391 | (+0.26 ± 0.05) | (1.013) | not determined (ESS below 500); not read |
| n0_m2 | −2 sd | 244 | (−0.28 ± 0.07) | (0.941) | not determined (ESS below 500); not read |

**The n0 posterior** (not blinded): log10 n0 = −1.803 ± 0.034 at d200 and
−1.834 ± 0.036 at d200 with n0_m083. The prior is −1.8105 ± 0.036 and
−1.840 respectively, so the events still do not constrain n0 with the
population free.

**Reading, as declared.**

- **Depth: mild.** Moving the depth from 0.245 to 0.200 with the population
  free shifts the H0 median by −0.28 baseline sd, seven times its bootstrap
  error, and leaves the width unchanged (R 1.01). Under the declared bands
  this is listed as a systematic in the robustness matrix. It does not
  change the baseline, and it does not go to the owner as a revision
  decision, which only "material" would.
- **The population roughly doubles the depth effect.** At a fixed
  population, Part B gave −0.155 for the same depth (robust). With the
  population free the shift is −0.277 and has the same sign. Part B's map
  therefore understates the depth sensitivity of the population-free result
  by about a factor of 1.8.
- **Interaction: mild.** With the depth at 0.200 and the n0 centre at
  −0.83 sd together, Δ is −0.365 ± 0.078. That is the sum of the two
  separate shifts (−0.277 and −0.099) within its error.
- **n0 centre: robust.** Up to ±1 sd, |Δ| ≤ 0.13 on B1's full set. On the
  12Y chain Part A gave −0.082 for n0_m083; here it is −0.099. The ±2 sd
  shifts keep 1.2% and 0.7% of the effective sample size and are not read,
  as expected in advance.
- **The window spread with the population free** is at least 0.28 (d200
  against d245), mild. Only the far end, d200, was run, as declared, so the
  intermediate depths are not measured with the population free.

**Limits of this reading.**

- One depth only.
- The 1024-draw baseline sits 0.06 sd from B1's full set. The variants are
  paired to it, so the shifts are not affected at their quoted errors.
- The lower H0 part carries 37 draws. Its share of the shift is inside the
  bootstrap error but is not separated here.

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
sha256, in `config/record_envs/12AB.json`; `scripts/check_frozen_environment.py --record 12AB` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AB/<sha7>` on
GitHub (4cf6bd5, 0d75a0a, 794cfde, 10a42de, 596651c). The full test suite is run by `./ci.sh` in the record
environments (CPU, HENON); it was green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and
is green at the final main (above).

**Code of record (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding G4.1).**
`phase12.5/n0-depth` (Parts A, B and C and the depth step, up to 794cfde) is merged into the consumer's main (merge
cbbe0c3). The north/south part (`phase12.5/n0-north-south`, 10a42de) changes the stock target
(`phase12/desi_selection.py`, +278 lines) and the base configuration and is **not merged**: it is tagged
`side-branch/phase12.5/n0-north-south` and listed for review before any merge.

**The merged file predates Part C (consumer PR #23, merge edabeb6; finding G4.9).**
`n0_depth/summary_location_free.json` was written once, by the analysis job at 21:10 UTC on 2026-10-18, before Part C
ran, and was not rewritten. Its Part B, Part A, north/south and step blocks equal their part files, but its `part_c`
block is stale:

- it says Part C is "not submitted: waits for stage B1's summary";
- it looks for B1's summary at `phase12_5/B1/summary.json`, a path that does not exist (B1's summary is
  `B1/summary/summary.json`, there from 10:56 UTC that day);
- it stores d200 under `variants_flagged_by_part_b`, but Part B flagged no variant: d200 runs by the declared rule.

The record's text is right: no variant was flagged, Part C ran for d200 only, and its results come from
`n0_depth/C/summary.json`. The merge helper was never committed (it lived in the n0_depth directory). It is now
`scripts/phase12_5_n0_depth.py merge` (consumer commits 9a76252 and a883683, merged with PR #23), which reads B1's
summary where Part C reads it, carries Part C's summary and status, and lists Part C's variants as flagged by Part B
or run by rule. It refuses to write when any number of the location-free file equals an H0 location of the absolute
part files. It writes new names beside the as-run files, which are kept as written. The merged file after Part C is
`n0_depth/summary_combined_location_free.json` (written 2026-10-26 17:33 UTC by `phase12_5_n0_depth.py merge
--require-part-c` from a clean checkout of consumer main at 402c947; sha256 3893c4c2d8f6...): missing none; Part C
"done"; variants run ['d200'], flagged by Part B [], run by rule only ['d200']. Its absolute counterpart is
`n0_depth/summary_combined_absolute.json`. A preview written to a scratch directory on 25 Oct 2026 gave: missing none; Part C "done"; variants
run ['d200'], flagged by Part B [], run by rule only ['d200']; its Part A, Part B, north/south and step blocks equal
the part files and the as-run merged file's; its Part C summary equals `C/summary.json`; and none of its numbers
equals any of the 142 H0 locations of the absolute part files.

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

**Writer commit (consumer PR #29, merge 0989df4; finding G4.10).** The summaries rewritten from main now carry the
commit of the code that wrote them; 12AB's north/south summary is written by code on the side branch n0-north-south,
which is not on main (tagged only), so its writer is not stamped.

**Launch files (consumer PR #30, merge 6d0f800; finding C137).** The launch files of this record predate the owner's
Slurm rules of 18-19 Oct 2026 (7-day limits; rita GPU jobs at 128 CPUs and 120G; holder steps only through the
wrapper) and break them. They are kept unchanged in what they launch, as the record of how the record ran, and from
the merge they refuse to run unless PHASE12_ALLOW_HISTORICAL names them (slurm/historical_launch_files.txt lists
them). The B1 and B2 pipelines' HENON fallback now clears every SLURM_* variable first.

## Amendment (26 Oct 2026): independent review, round 3

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses below.
The amendment of 25 Oct 2026 above covers the fix packages merged first. This one covers five more, merged on 26 Oct
2026 after a third fix round and an independent check of each: the 12AQ readings and mock (consumer PR #32, merge
97ec978), the 12AO ladder (PR #27, merge ebb12ff), the GW inputs (PR #26, merge a152bed), the variance guard and
estimator noise (PR #33, merge 901bb54) and catalog version 2 (PR #24, merge 402c947). The consumer's main is now
402c947. `./ci.sh` passed on the merged tree in all three record environments (HENON, CPU;
`ci_logs/20261026T124516Z_133bc47f981f_<env>.log`: consumer_e7c3007_cuda12 1568 passed, consumer_e7c3007batch_cuda12
1577, consumer_1022429_lss57afebe_cuda12 1592; none failed). On 26 Oct 2026 the owner decided that catalog version 2
vetoes the bright-star masks, BRIGHT and MEDIUM (Legacy Survey maskbits 2050), not the large-galaxy bit, and that the
injections stay at the support gate for now (decision 4D; the replacement of the O3 campaign, 4A, is deferred and no
new injection product is made). Location-free throughout. Unless an item says otherwise, no number of record changes.
Still open and not amended here: resume markers and fingerprints (consumer PR #25) and the follow-ups of consumer PR
#35, among them the refusal of a delta outside its prior's bounds.

**Empty covered pixels (consumer PR #24, merge 402c947; finding C018).** The n0 recipe's area (sum f_p) includes 7,214
covered nside-128 pixels that hold no catalog galaxy (5.48% of sum f_p): if they are outside the catalog, the prior
mean sits 0.0245 dex (0.67 prior sd) low. This record's robustness of the n0 centre bounds that part; the void part is
unmeasured.
