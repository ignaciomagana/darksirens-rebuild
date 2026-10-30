# Phase 12AS — decision 6A: the selection N_eff of the DESI target on catalog version 2, and the ring-averaged selection density (declaration)

## Status

**Declaration (location-free), written 30 Oct 2026 before any job of steps 1 and 2 was submitted.** The owner
approved the design of decision 6A on 30 Oct 2026 and gave the go for its steps 0, 1 and 2 with these answers:

- **Q1, what 6A delivers: parity.** The DESI target's wall should sit no closer than the spectral-only target's wall
  on 99% of the posterior, at both cells.
- **Q2, where the extra N_eff comes from: the ring-averaged host density (D3r),** adopted only if step 2's checks
  pass.
- **Q3, the first peak's width σ1:** decided after step 1's profile.
- **Q4, the soft-guard normalisation (decision 16): keep the unnormalised convention.**

Step 3 (D3r in the version-2 chain target) and the version-2 production chains are **not** approved; they wait for
the owner's reading of gates G1 and G2. Nothing here samples a chain.

Design: `darksirens-core-data/design_6A_2026-10-30/DESIGN_6A.md` (sizing from stored diagnostics, catalog version 1;
its scripts and outputs in `scratch/`). This record does not redo that sizing. Results go in later as labelled
amendments on this branch.

## Question

On catalog version 2, at the production cell (nside 64, sigma_kde 3e-3) and the fiducial cell (nside 128,
sigma_kde 1e-3):

1. **Step 1.** How close is the DESI target's selection N_eff to its variance guard over the population-free
   posterior, under the production host density (D0) and under the ring-averaged one (D3r)? How much more N_eff
   would put the DESI wall where the spectral-only wall is (parity, Q1), or clear it? And does the likelihood keep
   rewarding a narrower first mass peak (σ1) below a few tenths of a solar mass, within its Monte-Carlo error
   (Q3)?
2. **Step 2.** Is D3r valid for production: are the found injections uniform in right ascension within bins of
   redshift, mass and declination, and does D3r on the surrogate's synthetic injections (D4) agree with D0 on them
   (D3r's premise holds) or with the sky average D2 (it does not)?

## Names (in words)

- **A1**: the population-free spectral-only chains (H0 and all 17 population parameters sampled), at the variance
  limit 4 (eight chains, four per H0 part) and at limit 8 (four chains, two per part).
- **B2**: the population-free DESI chains at the production cell on catalog version 1 (record 12AF).
- **12AD**: A1's draws reweighted to the DESI target on version 1 (its stored per-draw evaluations are an input of
  gate G0).
- **x**: the selection N_eff over the guard's threshold max(5N, N² / (4 − Σσ²_PE)), N = 259. The wall is on for
  x < 1.
- **D0**: the selection term as production computes it (the catalog host density at each injection's pixel).
  **D3r**: the same with the host density averaged over the injection's iso-latitude HEALPix ring (records 12AL,
  12AN). **D2**: the full-sky average (12AL, 12AM). **D1**: the smooth model dN_exp(z), no catalog term (12AL; the
  catalog-free floor). **D4/X**: density X on the surrogate's synthetic detected injections (12AK model A, the
  record's D4 product, label systematic).

## The target (fixed now)

The catalog-version-2 DESI field target, built as `catalog_v2_scan.py --arm new` builds it (record 12AR's
validation): 12AG's ladder settings without their calibration prior, plus the cell's production overlay
(floor-hosts completeness, delta_in −0.641443, delta_out 0, log10 n0 with its calibration prior), the version-2
store of the cell and the version-2 footprint. Then, as B2:

- **population**: the 17 GWTC-5 parameters sampled, with A1's priors and in A1's order (`population.sampled`);
- **catalog nuisance**: log10 n0's quantile, drawn from its prior once per draw (B1's rule: a unit cube keyed by
  the draw set's seed, the chain's number and the stream), and kept for that draw at every cell, density and σ1
  value;
- **guard**: variance limit 4 with the smooth guard, under the unnormalised convention of decision 16;
- **kernel pin**: `auto` (B2's), tied to `off` in G0;
- **GW inputs**: the 12AP PE build (lalcosmo, sha256 `822b3181…`) and the selection of record (sha256 `56e51af2…`).

The **spectral-only target** at every point is A1's own: each chain's configuration, inputs (its PE build
`c6150725…`, the same injections) and guard, rebuilt as the B1 reweighting rebuilds it, and checked against the
chain's stored log-likelihood at every draw (1e-8). Its x is taken at limit 4 for every chain.

**Densities in one call.** D0, D3r and D1 go through 12AL's scoped selection-density wrapper in one call per point
(one core call per density in the same trace); the PE side is D0's for all three. Each density's ln μ, N_eff,
selection correction and log-likelihood are core's. The per-sample PE and selection log weights are captured
(`phase12.estimator_capture`, decision 7A) and reduced in float64 numpy; the reduction must equal core's record at
every point (1e-8, the capture's mirror check) before anything is used.

**D3r tables (step 0).** 12AL's `build_tables` on each version-2 store (every occupied pixel of the global store,
core's kernel state at 67.74, the table nodes z_j = 0.245 j / 24,500), accumulated into the 4 nside − 1 rings;
each ring's mean footprint fraction over all its pixels of the version-2 footprint map. 12AL's control 7 on each
table: the table against core's exact ring sums at 10,000 random (z, ring) pairs, 1e-4 relative from z 1e-3. D2 is
accumulated in the same pass for step 2(b).

## Step 1: what is measured (fixed now)

**Draw sets** (both cells; densities D0, D3r and D1; the spectral-only target at every point):

| set | points | rule |
|---|---|---|
| (i) A1, limit 4 | 8 chains × 1,024 = 8,192 | `phase12.reweight.draw_rows` on each chain's equal-weighted samples, seed 20261030, stream 0, chain number = the chain's sampler seed |
| (ii) A1, limit 8 | 4 chains × 1,024 = 4,096 | the same, seed 20261031; these reach σ1 below A1's limit-4 wall |
| (iii) the σ1 ladder | 2 parts × 128 draws × 12 values = 3,072 per cell | 32 draws per chain of (i) (seed 20261032), each with σ1 set to 0.003, 0.006, 0.01, 0.02, 0.035, 0.05, 0.1, 0.2, 0.3, 0.5, 0.78 and 1.5 Msun and every other coordinate unchanged |

The ladder carries **64 paired-bootstrap replicates** per point (decision 7A's plan: each event's PE samples
resampled with replacement, the found injections with Poisson(1) counts; seed 20261033; one plan shared by every
point, both cells and both densities, so differences keep their correlated part).

**Per point and density**: ln μ, N_eff, Σσ²_PE (DESI and spectral-only), the threshold at limit 4, x, the guard
penalty, and the unguarded log-likelihood. Absolute log-likelihoods and the draw coordinates with H0 go only to
`*_absolute.npz` files, which no agent opens. The location-free files hold log-likelihood differences, x, N_eff,
ln μ, the PE variance and the non-H0 coordinates.

**Weights.** Guard-free DESI weights per density, as `phase12_5_b1_reweight.py` builds them: the density's
unguarded log-likelihood against the chain's own stored log-likelihood (the limit-8 draws carry their own
proposal), equal-weighted rows within a chain, each chain of a part carrying the same total weight. Readings are per
H0 part (upper, lower), never combined across parts.

## Step 2: what is measured (fixed now)

**(a) Right-ascension uniformity of the found injections** (CPU, numpy): per campaign of the selection of record
(O3 BBH rows, O4a+O4b rows), the first and second harmonic amplitudes of the right ascension, 2|mean(e^{i k ra})|
for k = 1, 2, beside their noise level sqrt(4/n), in 8 redshift bins (edges 0, 0.05, 0.1, 0.15, 0.2, 0.245, 0.4,
0.7, above), 6 source-frame m1 bins (edges 0, 10, 20, 30, 40, 60 Msun, above) and 10 declination bins (equal in
sin dec), each binning on its own and redshift × declination jointly. The same for each D4 member's rows (the
surrogate's own right-ascension marginal).

**(b) D4/D3r beside D4/D0 and D4/D2** at both version-2 cells, on 12AN's fixed-population grid (641 points: [20,
140] at 0.5 and the fine window [50, 100] at 0.1), with 12AN's pipeline: the five D4 members of the record's
product (D4_CHOICE.json, model A, each file sha256-checked), the version-2 target at the overlay's n0 with 12AG's
fixed population, selection only (12AL's PE stub) for each member and density, the PE side from the version-2
stock target with the real injections at the same points, the variance limit 20 with the smooth guard (12AN's), and
the spectral-only grid (the same PE build) as the unit of shifts. The real-injection D0, D2 and D3r ride along as
context.

## Gates (technical; a miss stops what depends on it and goes to the owner, never relaxed)

**G0 (step 0; all must pass before step 1 is submitted):**
1. **12AD tie.** On version-1 inputs (12AD's target configuration and inputs, read from its evaluation files), the
   measured D0 ln μ and N_eff equal 12AD's stored `target_log_mu` and `target_n_eff` at 64 A1 draws (eight per
   chain), to 1e-10 relative.
2. **12AN tie.** On version-1 inputs at (128, 1e-3), with 12AG's calibration and fixed population and a D3r table
   built by the step-0 code, D3r's (and D0's) ln μ and N_eff equal 12AN's at its five control points (50, 62.5,
   75, 87.5, 100), to 1e-12.
3. **Identical pixels.** D3r equals D0 on a synthetic catalog whose pixels are all identical (12AL algebra (ii)),
   on the version-2 floor-hosts target with the delta split, in the test suite.
4. **The version-2 tables**: 12AL's control 7 passes on both D3r tables; the kernel pin `auto` equals `off` on the
   version-2 target at four points (1e-10 relative on ln μ, N_eff and the log-likelihood).
5. **CI**: `./ci.sh` is green in the version-2 record environment `consumer_1022429_lss57afebe_cuda12`.

**G1 (step 1; technical part):** every task complete; every row finite (x, N_eff, ln μ, Σσ²_PE of every density and
of the spectral-only target); the spectral-only stored check passes at every draw; the capture's mirror check passes
at every point; the stores', footprint's and overlays' sha256 equal record 12AR's (store ns64_sk3e-03
`6c59d63a8d2b0c85…`, ns128_sk1e-03 `20841d18308d2c43…`, footprint `4991f1af21d74555…`). The readings then go to the
owner (nothing launches on its own).

**G2 (step 2; technical part):** both parts complete and finite; the D4 files' sha256 equal 12AK's choice; at the
five control points the selection-only D0 on the real injections equals the full target's (1e-12) and the
three-density call equals single calls (1e-12). The owner then decides from (a) and (b) whether D3r goes into
production.

## Readings (declared now; Bayesian, location-free, no pass marks on statistics)

**Step 1**, per cell, H0 part, density (D0, D3r) and draw set ((i), (ii)), under that density's guard-free DESI
posterior:
1. the posterior mass beyond the wall (penalty below −1 nat) and with x < 1;
2. x at its 0.1%, 1%, 5% and 50% quantiles;
3. **clearance** k(p) = 1.02 / (the (1 − p) quantile of x), for p = 95%, 99%, 99.9%: the N_eff gain that puts
   x ≥ 1.02 on a share p of the posterior;
4. **parity** k_par(p) = 1 / (the (1 − p) quantile of x_DESI / x_spectral): the N_eff gain that puts the DESI wall
   no closer than the spectral-only wall on a share p (Q1 reads p = 99% at both cells); and the mass where
   x_DESI < 1 ≤ x_spectral;
5. both with floors σ1 ≥ 0.1, 0.2, 0.3, 0.5 and 0.78 Msun: the posterior mass kept, k(99%) and k_par(99%);
6. the N_eff ratios D3r/D0, D0/spectral, D3r/spectral and D1/spectral (5%, 50%, 95%), and the share of the
   catalog-added selection variance D3r removes per draw, (1/N_D0 − 1/N_D3r) / (1/N_D0 − 1/N_D1), and the same with
   the spectral-only N_eff as the floor (5%, 50%, 95%);
7. Σσ²_PE (DESI and spectral-only) and the threshold ratio DESI/spectral-only (5%, 50%, 95%).

**The σ1 profile** (set (iii)), per cell, part and density: at each σ1 value, the unguarded log-likelihood
difference against σ1 = 0.78 Msun, per draw and averaged over the 128 draws, each with its paired-bootstrap sd;
the slope b of ln x on ln σ1 below 0.05 Msun and between 0.05 and 0.5 Msun (per draw; 5%, 50%, 95%); Σσ²_PE and
the share of points beyond the wall at each σ1; the spectral-only target's difference at each σ1 (no replicates).
Whether the profile is flat is the owner's reading (Q3).

**Step 2:** (a) the amplitudes and their noise per bin and campaign, and per D4 member; (b) per cell: N × S_W in
nat on the fine window (S_W the largest |Δ − mean_W Δ| over the window, Δ the difference of two densities' ln μ;
12AK's U1 form) for D4/D3r against D4/D0, D4/D3r against D4/D2 and D4/D0 against D4/D2, per member and pooled
over members, each beside D4's member spread (the sd over members of the mean-removed N ln μ, its largest value
over the window); the shift of the posterior median in spectral-only sd, the sd ratio and the Hellinger distance
for the same pairs; the same three numbers on the real injections (D3r and D2 against D0) as context. Under D3r's
premise, D4/D3r follows D4/D0 up to D4's own noise; if it follows D4/D2 instead, right-ascension structure matters
and D3r is not adopted (the owner's call at G2).

## Inputs (sha256 checked by the jobs)

- Catalog version 2 (record 12AR): stores `stores/ns64_sk3e-03/desi_union_v2_nside64.h5` (`6c59d63a8d2b0c85…`),
  `stores/ns128_sk1e-03/desi_union_v2_nside128.h5` (`20841d18308d2c43…`); footprint `build/footprint_v2_nside128.h5`
  (`4991f1af21d74555…`); production overlays `calib/ns64/` and `calib/ns128/overlay_production.json`
  (`7020c286f0fb3c88…`, the same content).
- GW: PE lalcosmo `822b3181…` (DESI target), A1's PE `c6150725…` (spectral-only target), injections `56e51af2…`.
- A1's chains (`phase12_5/A1/runs/`, `runs_var8/`): their samples, configurations and stored nested log-likelihoods.
- G0: 12AD's evaluation files (`phase12_5/B1/evals/`); 12AN's cell `ns128_sk1e-03` (`phase12_5/d1_d4_fine/runs/`),
  read by the job and compared there.
- Step 2(b): 12AK's D4 product, model A, members m1 to m5 (`57555046…`, `9dd04568…`, `da83d2ba…`, `45a30f36…`,
  `baab930c…`; pooled `f01a6270…`).
- Code: the consumer repository's `scripts/phase6a_measure.py` at the commit of its PR (consumer main 2ef2701 plus
  the step-0 branch), environment `phase12t/envs/consumer_1022429_lss57afebe_cuda12` (core 1022429, lss 57afebe),
  CPU float64 on HENON for steps 0, 1 and 2(a), one rita A100-80 (QOS rita) for step 2(b).

## Compute (estimates; every Slurm job has the 7-day limit as a ceiling)

- Step 0: the two version-2 D3r tables and the version-1 tie table on HENON CPU (about 1 to 1.5 h each, in
  parallel); the ties about 30 min; CI about 1 h per environment.
- Step 1: HENON arrays (`-A phy230014p -p HENON --qos=henon --exclude=henon05,henon08`), 8 CPUs per task, both cells:
  the draw sets (i) and (ii) and the ladder, and a finish job (`--dependency=afterany`) that writes
  `design_6A_2026-10-30/step1/summary.json` and `STEP1_DONE` or `STEP1_FAILED`. About 1 to 3 h wall with a free
  HENON.
- Step 2: (a) one HENON CPU job, minutes; (b) one rita GPU job, about 2 to 4 h; a finish job writes
  `design_6A_2026-10-30/step2/summary.json` and `STEP2_DONE` or `STEP2_FAILED`.

## What it does not do

No chain, no change to the version-2 chain target, no change to any record's numbers. D3r stays an experimental
selection density until the owner's G2 decision and a step-3 PR. D4 numbers carry 12AK's systematic label.

## Amendments

**Amendment, step 0 (30 Oct 2026, before any step-1 or step-2 job; location-free).** Code: consumer PR #44
(branch `design/6a-v2-sizing`); the ties ran from the clean commit 4e7c0f5; the later commits do not touch the tie
paths (the spectral-only profile without guard or floor, the task slicing, a D4 smoke mode, the summaries, the
pin declaration).
- **Tables.** Built by `phase6a_measure.py tables` (commit 6b9115a) on one rita A100-80 (12AN's device) in 8 to 19
  s per cell; the HENON CPU builds declared under "Compute" used about 7 cores each and were cancelled after 10
  minutes (departure, compute only). 12AL's control 7 passes on every table: D3r 7.9e-7 (ns64_sk3e-03), 9.1e-6
  (ns128_sk1e-03) and 1.0e-5 (the version-1 tie table) against 1e-4; D2 4.3e-7 to 1.9e-6. 255 and 511 rings.
  Table sha256: ns64_sk3e-03 `3deacbd9e791e43a…`, ns128_sk1e-03 `05947a59221bfeae…`, version-1 (128, 1e-3)
  `9b2d9976acb12f76…`; the stores are 12AR's (`6c59d63a…`, `20841d18…`).
- **G0 (2), the 12AN tie: passes, bit for bit.** D0 and D3r ln mu and N_eff at the five control points equal 12AN's
  with difference 0.0 (tolerance 1e-12); the capture's mirror 4.5e-13.
- **G0 (3), identical pixels: passes** (`tests/test_phase6a.py`, D3r and D2 equal D0 within 1e-4 per injection on
  the floor-hosts target with the delta split; D1 does not).
- **G0 (4): passes.** 12AL's control 7 on both version-2 tables (above). The kernel pin auto against off on the
  version-2 target at four A1 draws: at most 7.1e-15 relative (ns64_sk3e-03) and 1.8e-16 (ns128_sk1e-03) on ln mu,
  N_eff and the log-likelihood of D0, D3r and D1, against 1e-10.
- **G0 (1), the 12AD tie: passes.** 12AD's target rebuilt from its evaluation files (version 1, production cell,
  its population order restored: B1 wrote its configuration with sorted keys), D0 through the measuring path at 64
  A1 draws (8 per chain): ln mu at most 6.1e-16 relative and N_eff 7.2e-15 relative from 12AD's stored values
  (tolerance 1e-10), on CPU with core 1022429 against 12AD's GPU run with core e7c3007. Reported beside: the PE
  variance sum 1.6e-15 relative, the log-likelihood 1.2e-10 nat absolute.
- **G0 (5), CI: passes.** `./ci.sh` at a1b4f24 on HENON: consumer_1022429_lss57afebe_cuda12 1,744 passed and 18
  skipped; consumer_e7c3007batch_cuda12 1,722 and 40; consumer_e7c3007_cuda12 1,713 and 49; no failure (logs in the
  consumer's `ci_logs/`, commit 76dacaf). The contract job reproduced without JAX: 1,143 passed, 221 skipped. The
  first run (d29657d) failed one contract test: the new script pins the selection of record by sha256 and was not
  listed in `config/gw_inputs_of_record.json` (`pinned_by.modules`); a1b4f24 adds the entry (no build changes).
  Consumer PR #44 merged (3c8a5ee) after the three environments were green.

**Amendment, submission (30 Oct 2026, 18:10 UTC; location-free).** Every job runs from the clean worktree of
a1b4f24 in `consumer_1022429_lss57afebe_cuda12`, with the tables of step 0.
- **Step 1** (HENON, `-A phy230014p --qos=henon --exclude=henon05,henon08`, 8 CPUs and 48 GB per task): arrays
  1399681 (production cell, tasks 0-127) and 1399682 (fiducial cell, tasks 128-255), 256 tasks; finish 1399683
  (afterany) writes `design_6A_2026-10-30/step1/summary.json` and `STEP1_DONE` or `STEP1_FAILED`.
- **Step 2:** (a) 1399684 (HENON CPU); (b) 1399685 (one rita A100-80, both cells in turn); finish 1399686 (afterany)
  writes `design_6A_2026-10-30/step2/summary.json` and `STEP2_DONE` or `STEP2_FAILED`.
- **Smoke (not results; outputs in `design_6A_2026-10-30/smoke/`).** One point costs about 16 s (production cell)
  and 9 s (fiducial cell) on 8 HENON CPUs with 19 to 23 GB resident; the step-1 tasks are therefore 128 draws (or 8
  ladder draws, 96 points) each, 256 tasks in all. The right-ascension and D4 paths ran end to end (the D4
  controls bit for bit on the real injections and member 1).
- **Added beside the declared readings (before any result):** `k_parity_capped`, the gain putting
  x_DESI >= min(x_spectral, 1.02), i.e. parity only where either wall is within reach (the declared k_par compares
  x everywhere, including far from both walls); the slope b also on 0.01 to 0.05 Msun; for the profile, the
  log-likelihood without guard and without core's 5N floor (sum ln Z - N ln mu + N(N+3)/(2 N_eff)), since the
  floor makes the unguarded value minus infinity at the smallest widths.
