# Phase 12AG — P12.5: does catalog smearing wash out the DESI information? The nside × sigma_kde ladder at a fixed calibration (declaration)

## Status

**DECLARED (owner approval, 2026-10-19 about 05:30 UTC), before any ladder
grid.** No ladder grid has run. This record fixes, before anything runs: the
ladder and its fixed values, the inputs (with sha256), the code commit, the
controls, the compute plan and the reading rules.

What runs first:

1. the catalogs at nside 32, 64, 128 and 256 and their gates (HENON CPU);
2. the GPU controls C1 and C2 (henon-gpu) and the check C3;
3. a short probe of memory and speed (rita and twig).

The 20 ladder grids are then submitted from the prepared plan by a separate
step. Results will be appended below.

**CATALOGS, CONTROLS AND PROBE DONE (2026-10-19, 06:15 UTC). No ladder grid
has run.**

- Every catalog gate passes. The rebuilt nside 64 is the production file bit
  for bit (same sha256).
- **C1, C2 and C3 pass.** C1 and C2 match bit for bit: the largest |Δ ln L|
  is 0.0.
- **The probe moved one routing rule, before any ladder grid** (see
  "Amendment (2026-10-19, before any ladder grid)"). nside 256 ran out of
  memory on an A100-40. Its peak on an A100-80 is 33.8 GiB, just under the
  declared 34 GiB limit. So the limit is now 30 GiB, and a probe that ran out
  of memory on a 40 GB card also counts. The five nside-256 cells go to rita.
  The ladder code moves to commit 09c4b62. Only the plan code changed, so the
  controls stand.
- **The plan is ready and not submitted:** seven GPU lanes, about 15 minutes
  of GPU time on the longest lane. See "Plan and estimate" under Results.

**Blinding: location-free.** No H0 value is written here, in commit messages
or in PR text: no median, interval, MAP or absolute shift in km/s/Mpc. Results
are given as:

- Δ = (median_cell − median_spectral) / sd_spectral;
- R = half-width68_cell / half-width68_spectral;
- the sd ratio;
- counts, Monte-Carlo variances, memory and timings.

The absolute values go only to `summary_absolute.json`, which agents do not
read or quote. Nothing goes to the clean-room session.

## The question

The owner suspects that the real DESI × GWTC-5 dark-siren analysis shows no
catalog information because the catalog is smeared too much:

- **Angular smearing:** every galaxy counts at its HEALPix pixel, nside 64,
  0.84 deg² per pixel (about 0.9° on a side).
- **Radial smearing:** every galaxy's redshift kernel has width
  σ_i = max(sqrt(dz_i² + sigma_kde²), 1e-4), with sigma_kde = 3e-3 (core
  `catalog/redshift.py`).

At a fixed population the catalog adds nothing measurable. This is record
12AE Part 1, the ladder cell: the DESI union chain gives R = 1.01 and Δ = −0.01
against the spectral-only grid, with sd ratio 1.01.

The owner's experience is that runs like this do give catalog information. So
some choice may be washing it out. This record tests the two smearing scales
directly. It holds everything else fixed, so that **any change in R comes from
the smearing alone.**

## The ladder

**Approved by the owner (exact words of the proposal, unchanged):**

- Ladder: nside {32, 64, 128, 256} x sigma_kde {1e-4, 3e-4, 1e-3, 3e-3, 1e-2} = 20 cells, plus a spectral-only grid.
- Each cell is an exact H0 likelihood grid on [20, 140] at step 0.5 (241 points), flat prior, everything else FIXED:
  log10 n0 = -1.8216 (h-scaled; the ladder chain's posterior median -1.82156), delta = 0, M0hat = -20.4975,
  sigma_M = 0.5592, z_depth 0.245, m_lim 21, production k-correction, production footprint; population fixed as the
  ladder cell (gamma 2.5439 not sampled, mu_chi 0.04, sigma_chi 0.10, other 14 at GWTC-5 values), Om0 0.3089; GW
  inputs = the ladder cell's exact-prior files (A_pe_chieff_bbh259_n4096_v20_exact.h5, A_sel_chieffref_o3o4ab_v20_exact.h5);
  core numerics as the ladder cell (core e7c3007 defaults, kernel pin off, variance limit 20, soft selection guard).
- Same galaxy set at every nside: re-pixelised from the native table (it has TARGET_RA/TARGET_DEC for 22,787,835 rows;
  production keeps 22,785,279 galaxies after its cuts). The rebuilt nside 64 must equal the production file.
- Record: DECLARE FIRST in a new rebuild record (12AG) before any ladder grid runs; location-free.

The 20 cells:

| nside | pixel area | pixel side | galaxies in the most crowded pixel |
|---|---|---|---|
| 32 | 3.36 deg² | 1.83° | 5,180 |
| 64 (production) | 0.84 deg² | 0.92° | 1,719 |
| 128 | 0.21 deg² | 0.46° | 774 |
| 256 | 0.052 deg² | 0.23° | 569 |

These crowded-pixel counts are from the native rows after the M_APP cut. The
catalog job records the exact ones.

The production cell is nside 64 with sigma_kde 3e-3.

**The fixed calibration is the ladder chain's posterior medians,** from
`phase12_5/ladder_cell/runs/union_fixed_pop/result.json`:

| parameter | median | fixed at |
|---|---|---|
| M0hat | −20.49752 | −20.4975 |
| sigma_M | 0.559188 | 0.5592 |
| log10 n0 | −1.821558 | −1.8216 |

The ladder cell's own 12-point scan (control C1) used a different point: the
prior means and the ridge centre.

### What sigma_kde changes

The kernel width is σ_i = max(sqrt(dz_i² + sigma_kde²), 1e-4). So sigma_kde
mostly changes the spectroscopic galaxies, which are 27% of the catalog. The
native rows after the cuts are:

- 4,967,798 with a BGS Bright spectrum;
- 1,189,375 with a BGS Faint spectrum;
- 16,628,106 with a photometric redshift.

The table gives the native ZERR by survey code, after the M_APP cut:

| | ZERR median | ZERR 5% to 95% |
|---|---|---|
| BGS Bright spectrum | 2.7e-5 | 4e-6 to 9.2e-5 |
| BGS Faint spectrum | 2.0e-5 | 5e-6 to 1.1e-4 |
| photometric redshift | 0.032 | 0.0086 to 0.074 |

The spectroscopic kernel width therefore tracks sigma_kde: 1.03e-4, 3.0e-4,
1.0e-3, 3.0e-3 and 1.0e-2 at the median. The photometric median width barely
moves: 0.0318 at sigma_kde 1e-4, 0.0320 at 3e-3 and 0.0334 at 1e-2. (The
owner's brief gave the photometric range as 0.006 to 0.022. The measured
values above replace it.)

So the radial axis of the ladder is really **the spectroscopic galaxies'
kernel width**. Most galaxies stay at their photometric width in every cell.

### Configuration of every cell

Each cell is the P12.4 DESI field target (`phase12/desi_selection.py`, the
target of the ladder cell). It is built by `phase12t_common.build_target`
exactly as `phase12u_stage.py scan` builds it for the ladder cell, from:

- `config/desi.fixed_population.json`;
- the fixed settings `catalog.calibration_prior=count_ridge_union_delta0`,
  `catalog.delta=0`, `catalog.z_depth=0.245`,
  `population.fixed_values.mu_chi=0.04`,
  `population.fixed_values.sigma_chi=0.1`,
  `numerics.core_numerics=core_defaults`, `numerics.kernel_pin=off`,
  `numerics.max_likelihood_variance=20` and
  `numerics.selection_neff_soft_guard=true`;
- the cell's own `catalog.sigma_kde` and `catalog.log10n0=-1.8216`.

At each H0 point, theta = (H0, M0hat −20.4975, sigma_M 0.5592, log10n0_q).

- log10n0_q is the ridge prior's quantile of log10 n0 = −1.8216. The quantile
  is a coordinate change only: the driver checks that it maps back to −1.8216
  within 1e-12.
- The calibration prior's density is not part of the likelihood.
- The footprint enters at the cell's nside (see Catalogs).
- The H0 grid is lo + 0.5 × arange(241) from 20, the spectral baseline's
  construction, so the points are equal floats in every cell and in the
  spectral grid.
- Evaluation is in float64 on one A100, with XLA preallocation off.

What each point records:

- ln L, ln μ and N_eff;
- the PE Monte-Carlo variance of each of the 259 events, with its sum and its
  maximum;
- the selection Monte-Carlo variance;
- the guard terms: the soft-guard penalty, whether the point is unpenalised,
  and whether it is accepted;
- the seconds of the call;
- the device memory (jax's allocator peak, and nvidia-smi's used memory).

The posterior is the flat-prior grid posterior, by trapezoid and interpolated
quantiles, as the spectral baseline's `_summary` computes it.

**The spectral-only grid** is the existing grid
`phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json`. Record 12AE
used the same grid as the ladder cell's row neighbour. It covers the same 241
points, with the same GW inputs, population, guard and core (control C3).

The plan also reruns this grid once on a GPU, as a 21st job (minutes). The
rerun records the GPU equality and is not used as the reference.

## Inputs (sha256)

| input | path (under `/hildafs/projects/phy230054p/magana/darksirens-core-data` unless absolute) | sha256 |
|---|---|---|
| native table (22,787,835 rows) | `/hildafs/projects/phy230014p/magana/desi_darksirens_selection/final/experiments/experiment_loa_rebuild/inputs/rebuild_loa_faint_pixelate_input.h5` | `42e91b594572cfba716d0128ea3dcb24924a6c63e573078e7c4184fe24c0eaaa` |
| production catalog, nside 64 | `phase12u/inputs/catalogs/desi_union_nside64.h5` | `c2d1ff36567419e42386f07daf30bd0af2e2da714c16f066ecde4eb94d9084e2` |
| footprint, native nside 128 | `phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| GW PE (259 events, 4096 samples) | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| injections (O3/O4) | `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| spectral-only grid (reference) | `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json` | `db9f7b80c4b799c18559c99040916a821ed99aa7feb06fcec1d6589a171a6f9f` |
| ladder cell scan (C1 reference) | `phase12_5/ladder_cell/runs/scan_union_fixed_pop/scan.json` | `3a2365370d8f4b4bcf2c415b1f9b142390ce8dd8959d326aa5c127958fc6ae69` |
| ladder chain result (calibration medians) | `phase12_5/ladder_cell/runs/union_fixed_pop/result.json` | `48d314fb52fa2578aab0a538f129f5997f4a412e93f10120239366fcb322badb` |

The catalogs built here (nside 32, 64, 128 and 256) and the upgraded nside-256
footprint get their sha256 in the catalog job's `build_nside<N>.json` and
`gates.json`. They will be appended under Results before any ladder grid.

## Code and environment

- **Consumer:** `ignaciomagana/desi_darksirens_selection`, branch
  `phase12ag/smearing-ladder`, **commit 304c8ae**. It branches from the
  ladder cell's `phase12.5/ladder-cell` (f549575) and is checked out at
  `phase12_5/repo_12AG`. It adds:
  - `scripts/phase12ag_catalogs.py`: the catalogs and their gates;
  - `scripts/phase12ag_scan.py`: the grid driver;
  - `scripts/phase12ag_plan.py`: the plans, lanes and checks;
  - `scripts/phase12ag_summary.py`: the reading;
  - `slurm/phase12ag_*`: the jobs;
  - `tests/test_phase12ag_ladder.py`: 13 CPU tests. They pass on tiny inputs:
    the driver equals `phase12u_stage.py scan` bit for bit, and nside 64
    equals the production builder byte for byte.

  Nothing in `phase12/`, `phase12t_*` or `phase12u_*` changes.
- **Jobs run from a git worktree of the submitted commit,** under
  `phase12_5/smearing_ladder/worktrees/<sha>`. The submit scripts refuse a
  dirty checkout and a commit that no origin branch contains. A later fix
  moves the commit, and an amendment here records it, before any ladder grid.
- **Environment:** `phase12t/envs/consumer_e7c3007_cuda12` (core e7c3007,
  darksirens-surveys 90f53a7, jax 0.4.34). It is the ladder cell's
  environment and is read-only: nothing is installed into it.
- **Outputs:** `phase12_5/smearing_ladder/`, with the subdirectories
  `catalogs/`, `controls/`, `probe/`, `runs/<cell>/`, `summary/`, `plans/`,
  `logs/` and `lanes/`.

## Catalogs

Every nside is built from the native table exactly as the production nside-64
file was built. That build is `phase12u_subcatalogs.standardize`, which
reproduced the 12S catalog bit for bit. The output nside is the only change.
The steps:

1. **Quality cut:** isfinite(M_APP) and M_APP ≤ 21. It keeps 22,787,566 rows
   and removes 269.
2. **The 12I mask:** rows whose native nside-128 RING footprint pixel has
   f_p = 0 are removed: 2,287 rows, leaving 22,785,279. The mask is judged at
   nside 128 for every output nside, so **the same rows survive at every
   nside.** The counts must equal these numbers, or the job fails.
3. **Column map:** z = Z, dz = ZERR, weight = WEIGHT (all 1), and the slot
   column `gal_app_mag` = M_APP.
4. Validation.
5. **Pixelation** at the cell's nside with z_depth 0.245. Each pixel's galaxies
   are in increasing z, with the native row order as the tie-break.
6. **A core load check.**
7. **The coverage check:** no occupied pixel may have f_p = 0.

**The footprint at each nside** comes from the same native nside-128 map
through the darksirens-surveys loader:

- nside 32 and 64: the map is degraded equal-area, as in production.
- nside 128: the map is used as it is.
- nside 256: the loader cannot upgrade a map, because it refuses to degrade
  128 to 256. So nside 256 uses an upgraded copy of the map,
  `catalogs/footprint/mth_map_nside256_from128.h5`, in which **every child
  pixel inherits its parent's masked_frac and counts.** The loader then gives
  every child its parent's f_p exactly. The build checks that, and checks that
  degrading the copy back to 128 returns the native f_p (to 1e-15).

**Gates.** The catalog job exits non-zero when one fails, and no GPU job then
starts.

- **G1: one galaxy multiset.** At every nside, the sorted (z, dz, weight,
  apparent magnitude) rows equal the native rows after the cuts, compared
  exactly.
- **G2: nesting.** For each adjacent pair (32 and 64, 64 and 128, 128 and
  256), the multiset of (coarse NEST pixel, galaxy) is the same in both
  files. So every galaxy sits in a child of its coarse pixel. The children's
  counts sum to their parent's.
- **G3: nside 64 equals the production file.**
  - First test: the sha256 values are equal.
  - If not, every dataset is compared exactly.
  - If only the slot order inside a pixel differs: per-pixel sorted equality
    here, and ln L equality in C2.

## Controls

All three must pass before any ladder grid is read.

- **C1: the ladder cell's 12-point scan is reproduced.** The new driver runs on
  the production nside-64 file at the ladder cell's scan calibration: log10 n0
  −1.810518, M0hat −20.499724068694622 and sigma_M 0.5574913738106552 (the
  prior means), with sigma_kde 0.003. It is evaluated at the same 12 H0 values
  as `ladder_cell/runs/scan_union_fixed_pop/scan.json`, and |Δ ln L| must be
  ≤ 1e-6 at all 12. That scan ran on a rita A100-80. C1 runs on the henon-gpu
  A100-40.
- **C2: the rebuilt nside 64 gives the production file's ln L.** At three of
  C1's H0 values (25, 66, 139), in the same job and on the same card as C1,
  |Δ ln L| must be ≤ 1e-10. When G3 is bitwise, C2 is a check of the file path
  only.
- **C3: the spectral-only grid matches.** The reference grid must have:
  - the 241 points, as equal floats;
  - the same GW input sha256 values;
  - the population equal to the ladder cell's: the GWTC-5 preset with mu_chi
    0.04 and sigma_chi 0.10, gamma 2.5439;
  - Om0 0.3089, w0 −1 and wa 0;
  - the soft guard at limit 20;
  - core e7c3007 with core defaults;
  - every point accepted and unpenalised.

  That grid ran on HENON CPU in float64. The GPU rerun in the plan reports its
  largest |Δ ln L| against it.

## Probe (before the plan)

The probe measures memory and speed before the ladder is planned:

- one entry per nside at sigma_kde 1e-4 and at 1e-2, so 8 entries;
- 5 H0 points each (20, 50, 80, 110, 140), at the ladder calibration;
- recorded per entry: jax's peak device memory, nvidia-smi's used memory, the
  build and first-call seconds, the seconds per later point, and the PE
  variance (sum and maximum).

Where they run:

- nside 32 runs on a rita A100-80. Its widest pixel (5,180 galaxies, three
  times nside 64's) is the memory risk.
- nside 64, 128 and 256 each run on a twig A100-40.

**Routing rule:** a cell whose probe peak, at either probed sigma_kde, is above
34 GiB goes to rita's 80 GB cards only. Probe numbers are not likelihood
results and are not read.

## Compute plan

There are seven GPU lanes:

- rita × 2 (A100-80): partition RITA-GPU, qos rita, account phy220048p, 128
  CPUs, 120G, 7 days;
- twig × 4 (A100-40): partition TWIG-GPU, qos twig, account phy220048p, 32
  CPUs, 120G, 2 days (twig's maximum);
- the free henon-gpu card (A100-40): partition HENON-GPU, qos henon-gpu, 64
  CPUs, 240G, 7 days.

The miko holder, the second miko card and js2h100 are not used, and other
users' jobs are left alone. Every job requests its partition's maximum time.
That is a ceiling, not the estimate.

- **Assignment:** `phase12ag_plan.py ladder` assigns the 20 cells and the
  spectral rerun, longest first. Each goes to the least-loaded lane allowed by
  the routing rule. Each cell's time is estimated from the probe as: build +
  first call + 240 × seconds per point + 60 s.
- **Lane jobs:** each lane is one job (`slurm/phase12ag_lane.sbatch`). It runs
  its cells in order, each in its own process. A cell with a DONE marker is
  skipped, and each grid resumes from its own `scan.json`. A lane can
  therefore be resubmitted.
- **Summary:** a HENON CPU job (`slurm/phase12ag_summary_henon.sbatch`) waits
  for all lanes with `--dependency=afterany`. It writes `summary/summary.json`
  (location-free), `summary/summary_absolute.json` and the R plane
  (`R_plane.svg`, and `R_plane.png`).
- **One submit script** does all of this: `slurm/phase12ag_submit_ladder.sh`.
  It creates the worktree, writes `plans/plan.json` from the probe, submits
  the lanes and then the summary.
- The estimate of the time to completion, from the probe, is appended under
  Results with the plan.

## What is reported, per cell

All against the spectral-only grid, on the same 241 points:

- **R:** the 68% half-width ratio, (q84 − q16)/2 for the cell over the same
  for the spectral grid. Also the 90% half-width ratio.
- **The sd ratio.**
- **Δ** in spectral sd.
- **The PE Monte-Carlo variance per event, as its sum and its maximum.** These
  are reported at the grid point nearest the cell's median, as the largest
  over the cell's 90% interval, and as the largest over the grid. The
  selection variance is reported too.
- **The variance guard:** the number of grid points it penalises (a non-zero
  soft-guard penalty, or a penalised point), the number it rejects (non-finite,
  or N_eff ≤ 5 N_obs), and whether any penalised point lies inside the cell's
  90% interval.
- **Memory and timing:** jax's peak, nvidia-smi's peak, seconds per point,
  and build time.

## Reading rules (fixed before any grid)

Per cell:

- **"The catalog narrows H0"** if R ≤ 0.90 and no penalised point lies inside
  the cell's 90% interval.
- **"A hint"** if 0.90 < R ≤ 0.97.
- **"No narrowing"** if R > 0.97.
- **"Limited by the Monte-Carlo variance"**, instead of any of the three
  above, if a penalised point lies inside the cell's 90% interval.
- A cell whose grid is incomplete or has a non-finite ln L is reported as
  incomplete, not read.

Shifts are reported in the program's usual bands: **robust** |Δ| < 0.2,
**mild** 0.2 to 0.5 and **material** > 0.5.

The axes:

- R is reported along nside at each fixed sigma_kde, and along sigma_kde at
  each fixed nside.
- **"Smearing washes out the information"** is said only if two things hold:
  - some cell reads "narrows";
  - R rises toward the production cell (nside 64, sigma_kde 3e-3) along that
    cell's row or column. R must not fall at any step from the narrowing cell
    to the production cell, and must be higher at the production cell.
- Otherwise the ladder says the smearing scales tested here do not explain the
  missing information.

Stated plainly:

- **Fixed-calibration grids are not the marginalised posterior.** M0hat,
  sigma_M and n0 are held at single values. The ladder measures how the
  likelihood's H0 width responds to smearing at that point. It is not a
  replacement for a chain.
- **sigma_kde mostly changes the ~27% spectroscopic galaxies.** Their kernel
  width follows sigma_kde. The photometric galaxies keep their own width,
  median about 0.032, because width = max(sqrt(dz² + sigma_kde²), 1e-4).
- **The narrowest kernels can raise the PE Monte-Carlo variance.** That is
  why the per-event variance and the guard are reported per cell, and why a
  penalised point inside the 90% interval changes the reading.

## Amendment (2026-10-19, before any ladder grid)

**The routing rule changes. Nothing else in the record changes.**

- **As declared:** a cell went to an 80 GB card when its probe peak was above
  34 GiB.
- **Now:** a cell goes to an 80 GB card when its probe peak is above
  **30 GiB**, or when its probe **ran out of memory on a 40 GB card**.

The reason: the nside-256 probe failed on a twig A100-40 (job 1390208). It
asked for a single 24.3 GiB allocation and was refused. On a rita A100-80
(job 1390216) the same entries ran with a jax peak of 33.8 GiB and an
nvidia-smi peak of 48.8 GiB. The declared rule would have sent nside 256 to a
40 GB card, where it does not fit.

- **The code** for this is consumer commit **09c4b62**, on the same branch.
  It changes `scripts/phase12ag_plan.py` (the limit, and out-of-memory
  attempts recorded per card in the probe report), the test of the plan, and
  `slurm/phase12ag_submit_ladder.sh` (which rewrites the probe report with
  this code and refuses a failed probe entry).
- **The ladder runs from 09c4b62.** The scan driver, the catalog code and the
  `phase12` package are identical at 304c8ae and 09c4b62, so C1 and C2 (run
  at 304c8ae) stand.

## Results

### Catalogs (HENON job 1390203, henon04, 10 min 41 s, 20 GB peak RSS)

The native table's sha256 matched the declared value. Every nside has the
same row counts: 22,787,835 rows; 22,787,566 after the M_APP cut; 2,287
removed by the 12I mask; **22,785,279 galaxies**.

| nside | occupied pixels | galaxies per occupied pixel: median, 99%, max | sum of f_p | file sha256 |
|---|---|---|---|---|
| 32 | 7,834 | 3,024; 4,370; 5,180 | 6,865.3 | `59c95d89f6f29308871f3e1125b68dd292895ccf4f3ccd91fdb198ae249a3196` |
| 64 | 30,411 | 752; 1,239; 1,719 | 27,461.2 | `c2d1ff36567419e42386f07daf30bd0af2e2da714c16f066ecde4eb94d9084e2` (= production) |
| 128 | 119,524 | 185; 361; 774 | 109,844.7 | `f26a20f0f3f8ca5a9bc0aee0681cd0eba6f1a7b693055839cba83d6189cdb62c` |
| 256 | 473,384 | 45; 110; 569 | 439,378.6 | `66c50dc4ac1ea3ffc593f8e19cc2baf3f0dd18c8a4953c77b10f262153a684d3` |

- At every nside, no occupied pixel has f_p = 0.
- **The upgraded nside-256 footprint** is
  `catalogs/footprint/mth_map_nside256_from128.h5`, sha256
  `c20e58e3b3570a5e131b3754002ea26024c43e647d3541ae9e1786fcdb181a67`. Every
  child's f_p equals its parent's exactly. Degrading the copy back to 128
  gives the native f_p with a largest difference of 0.0.

**Gates (`catalogs/gates.json`):**

- **G1 passes.** Every nside holds exactly the native rows after the cuts.
- **G2 passes.** For 32 and 64, 64 and 128, and 128 and 256, every galaxy
  sits in a child of its coarse pixel, and the children's counts sum to their
  parent's.
- **G3 passes bit for bit.** The rebuilt nside 64 has the production file's
  sha256.

### Controls

- **C1 passes.** henon-gpu A100-40, job 1390204, commit 304c8ae. At all 12
  H0 values the largest |Δ ln L| is **0.0**: bit for bit equal to the ladder
  cell's scan, which ran on a rita A100-80. The theta vectors are identical
  too. The first call took 90 s; later points took 0.285 s each; the jax peak
  was 13.4 GiB.
- **C2 passes.** It ran in the same job, on the rebuilt nside-64 file, at 3 H0
  values: largest |Δ ln L| **0.0**. The file is the production file byte for
  byte.
- **C3 passes.** All ten checks hold: the 241 points as equal floats, both GW
  sha256 values, the population equal to the ladder cell's, gamma 2.5439, the
  cosmology, the soft guard at 20, core e7c3007 with core defaults, every
  point accepted and unpenalised, and the grid accepted.

The record is `controls/controls.json`.

### Probe

Five H0 points per entry, at the ladder calibration (`probe/probe.json`).
Times are per process: load + build, the first call (with its compile), then
the median of the later calls. The PE variance columns are the largest over
the five points.

| nside | sigma_kde | card (job) | jax peak GiB | nvidia-smi peak GiB | load + build s | first call s | s per point | PE variance sum, max | largest single event | penalised points |
|---|---|---|---|---|---|---|---|---|---|---|
| 32 | 1e-4 | A100-80 (1390205) | 10.2 | 18.8 | 24 | 77 | 0.352 | 0.36 | 0.027 | 0 |
| 32 | 1e-2 | A100-80 (1390205) | 10.2 | 18.8 | 18 | 76 | 0.350 | 0.26 | 0.021 | 0 |
| 64 | 1e-4 | A100-40 (1390206) | 13.4 | 20.8 | 28 | 86 | 0.276 | 0.55 | 0.072 | 0 |
| 64 | 1e-2 | A100-40 (1390206) | 13.4 | 20.8 | 25 | 87 | 0.274 | 0.28 | 0.021 | 0 |
| 128 | 1e-4 | A100-40 (1390207) | 12.7 | 24.8 | 40 | 83 | 0.269 | 1.21 | 0.282 | 1 |
| 128 | 1e-2 | A100-40 (1390207) | 12.7 | 24.8 | 35 | 83 | 0.267 | 0.31 | 0.029 | 0 |
| 256 | 1e-4 | A100-40 (1390208) | out of memory | | | | | | | |
| 256 | 1e-4 | A100-80 (1390216) | 33.8 | 48.8 | 68 | 68 | 0.358 | 2.88 | 0.556 | 0 |
| 256 | 1e-2 | A100-80 (1390216) | 33.8 | 48.8 | 68 | 68 | 0.357 | 0.38 | 0.027 | 0 |

**Memory grows with fine nside, not coarse.** The target keeps one row per
pixel that a PE sample or an injection falls in. That is 12,288 rows at nside
32 (all of them), 49,152 at 64, 196,577 at 128 and 714,745 at 256. The
per-row curves dominate the memory. The width of the most crowded pixel
(5,180 down to 569 galaxies) matters less.

**The PE variance rises as the smearing gets finer.** It peaks at the lowest
probed H0 and stays far under the limit of 20. At sigma_kde 1e-4 the largest
sum over the five points is 0.36, 0.55, 1.21 and 2.88 at nside 32, 64, 128
and 256. At sigma_kde 1e-2 it is 0.26 to 0.38 at every nside.

**One probe point is penalised.** At nside 128 with sigma_kde 1e-4, the grid's
lowest point, the lower edge of the H0 prior, has a selection N_eff of 2,743
against the guard threshold of 3,570. The soft guard lowers its ln L by about
6,000. The other four points of that entry have N_eff of 40,000 or more. The
ladder's reading rule handles such points: a penalised point counts only if it
lies inside the cell's 90% interval. Probe numbers are not likelihood results
and are not read.

### Plan and estimate (prepared, not submitted)

`slurm/phase12ag_submit_ladder.sh` at commit 09c4b62 does the following:

- writes `plans/plan.json` from the probe;
- submits seven lane jobs, each at its partition's maximum time;
- submits the HENON summary job with `--dependency=afterany` on all of them.

A dry run gives these lanes:

| lane | card | cells, in order | estimated GPU time |
|---|---|---|---|
| rita0 | A100-80 | nside 256 at sigma_kde 1e-4, 1e-3, 1e-2 | 14 min |
| rita1 | A100-80 | nside 256 at 3e-4 and 3e-3; nside 64 at 3e-3 | 13 min |
| twig0 | A100-40 | nside 128 at 1e-4 and 1e-2; nside 64 at 1e-3 | 12 min |
| twig1 | A100-40 | nside 128 at 3e-4; nside 32 at 1e-4 and 1e-2 | 12 min |
| twig2 | A100-40 | nside 128 at 1e-3; nside 32 at 3e-4; nside 64 at 1e-4 | 12 min |
| twig3 | A100-40 | nside 128 at 3e-3; nside 32 at 1e-3; nside 64 at 3e-4 | 12 min |
| henon-gpu | A100-40 | the spectral-only rerun; nside 32 at 3e-3; nside 64 at 1e-2 | 15 min |

**How each cell is estimated:** load + build + first call + 240 × seconds per
point + 60 s of start-up. That is 4.0 to 4.7 minutes per cell. The spectral
rerun is budgeted at about 7 minutes.

**Estimated time to completion:** about 20 to 30 minutes from submission when
the cards are free, as rita, twig and the free henon-gpu card were at
06:10 UTC. That allows 15 minutes for the longest lane, a few minutes of
start-up and queue, and about 2 minutes for the summary.

- If another user holds a rita card, the nside-256 cells wait for it. Their
  jobs on rita ran about 4 hours on 2026-10-18, so the worst case is about
  4.5 hours.
- The partitions' maximum times (7 days, and 2 days on twig) are ceilings,
  not estimates.
