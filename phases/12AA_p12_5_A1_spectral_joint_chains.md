# Phase 12AA — P12.5 stage A1: spectral-only chains with H0 and the GWTC-5 population sampled (declaration)

## Status

**ERRATA (independent review, 25 Oct 2026).** Four corrections to the limit-4 and limit-2 results; no number of record
changes. σ2's GWTC-5 value also lies outside its 68% interval (marginally, at limit 4 only); σ1 (r = +0.19) belongs
among the upper part's H0 correlates; limit 2's ln Z errors use another definition than limit 4's; the chain times and
σ_chi's median are corrected. See "Amendment (25 Oct 2026): independent review" at the end.

**RESULTS APPENDED (2026-10-18). Owner decision 2026-10-18: the limit-4
run is the reference full-population spectral result.** Read "Results" at
the end first.

**LIMIT-2 RESULTS APPENDED (2026-10-18).** The direct limit-2 chains confirm
the reweighting by the declared rule; the median's agreement is marginal.
They are in the robust band against limit 4. σ1 follows the limit, and there
is no collapse. See "Results (2026-10-18)" at the end of the last section.

**LIMIT-2 CHAINS DECLARED (owner, 2026-10-18), before any limit-2 chain:**
direct chains at variance limit 2, two per H0 part, on the Jetstream2 H100
while the direct DESI chains of 12AF are written. See the last section,
"Limit-2 chains (declared 2026-10-18)".

**THIRD ATTEMPT DECLARED (owner, 2026-10-09): all seventeen population
parameters, the GWTC-5 paper's priors, variance limit 4. Read the last two
sections first: "Second attempt" gives the priors and what the variance
limit means; "Third attempt" replaces its limit of 1 by 4.** The first attempt was
cancelled after two of its eight chains and failed; what follows up to that
section is its declaration, kept as written.

**DECLARED (owner, 2026-10-09) before any chain.** The implementation, its
CPU checks and one 8-minute GPU timing job are done and recorded below. The
owner's decisions on the open points are in the next section and are applied
throughout. No production chain has been submitted; the owner submits after a
dry run.

## Owner decisions (2026-10-09)

The first draft proposed the model's own ranges for both spin priors and two
seeds per H0 part, and listed five open points. The owner decided:

1. **Spin priors narrowed:** the effective-spin mean flat on 0 to 0.3 and its
   width flat on 0.005 to 0.3. With the model ranges (0 to 1) the selection
   guard penalised 88% of the prior volume (check 2). Every other prior as
   proposed; the second peak width keeps its lower edge at 0.
2. **Four seeds per H0 part: eight chains.** The point of four is the seed
   scatter of each part's ln Z and of the low part's weight.
3. **Random-walk length 72** confirmed.
4. **No guard-cap control now.**

## Where this sits

P12.5 of the Phase 12 contract (`12_production_analysis_contract.md`)
replaces the fixed GWTC-5 population by its uncertainty. It is staged
(`phase12_5/P12_5_full_scope.md` under darksirens-core-data):

- Step 1 (12Y) sampled one population parameter, the merger-rate index, in
  the DESI catalog analysis: H0 = 67.6 [62.8, 73.9].
- Stage A0 (12Z) scanned the other parameters one at a time without a
  catalog. Seven mass parameters each move H0 by 4 to 9 km/s/Mpc per
  one-sigma step, and the fixed spin values were wrong (corrected to
  effective-spin mean 0.04, width 0.10; amendment in
  `12_summary_12M_to_12X.md`).
- **This stage, A1,** samples H0 together with the parameters A0 selected, in
  the spectral-only likelihood: the 259 events and the injections, no galaxy
  catalog.
- The DESI result follows by reweighting these chains to the catalog
  likelihood (stage B1), declared separately.

## Why

- A fixed population understates the H0 uncertainty (12Z). The one-parameter
  scans cannot say how much of each shift survives when the parameters move
  together.
- An archived spectral-only run with all 18 parameters free, made at the old
  spin values, had a second mode near H0 = 32 with the first mass peak near
  11.2 solar masses, holding about 16% of the posterior (12% to 22%). Single
  sampler runs gave it 6%, 7% and 32%. Whether that mode exists at the
  corrected spin, and with what weight, is not known.

## The model

The 12T spectral-only likelihood: the exact-prior GW inputs
(`A_pe_chieff_bbh259_n4096_v20_exact.h5`, `A_sel_chieffref_o3o4ab_v20_exact.h5`),
core e7c3007 with its defaults, the soft selection guard at cap 20, flat
ΛCDM with Om0 = 0.3089. The population is the GWTC-5 broken power law with
two peaks (17 parameters).

| | 12T, 12X spectral grids | these chains |
|---|---|---|
| H0 | grid, 20 to 140 | sampled |
| merger-rate index γ | fixed, or scanned | sampled |
| effective-spin mean and width | fixed | sampled |
| mass break, both mass slopes | fixed | sampled |
| both peak positions, second peak width | fixed | sampled |
| the two mixture fractions λ0 (power law) and λ1 (first peak) | fixed | sampled |
| first peak width σ1, pairing slope β_q, the two low-mass edges and their two taper widths | fixed | fixed at the GWTC-5 values |

Twelve sampled parameters. The second peak's fraction is 1 − λ0 − λ1.

### Priors

All flat. "Model range" is the range of core's GWTC-5 model.

| parameter | value on the fixed population | prior | what the guard map found (check 2) |
|---|---|---|---|
| H0 | — | 20 to 140, run in two parts: 20 to 45 and 45 to 140 | no dependence |
| rate index γ | 2.5439 | −2 to 6, as in step 1 (model range −10 to 10) | mild: penalised fraction rises with γ |
| effective-spin mean μ_χ | 0.04 | **0 to 0.3** (owner; model range 0 to 1) | above 0.5 nearly every draw is penalised; inside the prior, a third above 0.24 |
| effective-spin width σ_χ | 0.10 | **0.005 to 0.3** (owner; model range 0.005 to 1) | above 0.5 nearly every draw is penalised; inside the prior, half below 0.064 |
| mass break | 37.451 | 20 to 50 (model range) | none |
| first slope α1 | 1.4816 | −4 to 12 (model range) | mild: more penalised above 6 |
| second slope α2 | 5.4187 | −4 to 12 (model range) | mild: more penalised below −0.7 |
| first peak position μ1 | 9.9109 | 5 to 20 (model range) | none |
| second peak position μ2 | 32.3273 | 25 to 60 (model range) | none |
| second peak width σ2 | 5.7263 | 0 to 10 (model range; lower edge kept, owner) | **half of the draws below 2 penalised** |
| fractions λ0, λ1 | 0.4004, 0.5457 | uniform on the triangle λ0 ≥ 0, λ1 ≥ 0, λ0 + λ1 ≤ 1 | none in the prior draws (see below) |

- **The triangle.** Core maps the sampler's unit square onto the triangle, so
  the prior is uniform on it and no part of it has zero likelihood. Checked on
  20,000 draws: none outside, each fraction's mean 1/3.
- **Orderings.** The two peak positions cannot cross: their ranges (5 to 20,
  25 to 60) do not overlap. The model sets no order between the break and the
  peaks. The fixed low-mass edges (4.49 and 3.46 solar masses) lie below every
  sampled mass scale and satisfy the model's own order.
- **What 12Z adds on the fractions.** In the one-parameter scans, small
  fractions were penalised at low H0 only: λ0 ≤ 0.27 below H0 = 36 to 50, and
  λ1 ≤ 0.42 below H0 = 30 to 44. That is the region of the archived second
  mode. The prior draws here show no dependence on the fractions, because
  nearly all draws are far from the events' preferred masses.

### Split prior and seeds

- H0 is sampled in two parts, 20 to 45 and 45 to 140, each with its flat
  prior normalised on its own part. **Four seeds per part: eight chains**
  (seeds 31 to 34 for the low part, 41 to 44 for the high part).
- The parts are combined by evidence. With a flat prior on 20 to 140, a
  part's prior mass is its width over 120, so the low part's posterior mass
  is 25 Z_low / (25 Z_low + 95 Z_high).
- **Pooled estimate:** each part's ln Z is the mean of its seeds' ln Z.
- **Seed scatter, reported beside it:**
  - per part, every seed's ln Z, their sample sd, and the standard error of
    their mean;
  - the low part's mass for each of the four matched pairs (first low seed
    with first high seed, and so on), which are independent estimates, with
    their mean and sd;
  - the same for all sixteen pairings of one seed per part: mean, sd,
    smallest and largest.
- Combined samples: each part contributes its posterior mass, shared equally
  among its seeds.
- The combination uses the seeds that have a result (at least one per part),
  and names any chain left out.

### Sampler

dynesty only, through core's `ds.infer`: 1000 live points, stop at dlogz 0.1,
random-walk proposals. Checkpoint every 30 minutes.

**Random-walk length:** 72 steps per proposal (core's
`dynesty_walks="scaled"`, 6 per parameter; confirmed by the owner). dynesty's
own default would be 32. Core's record of 13-parameter mock runs has ln Z 0.6
to 0.75 low at the default and correct at 6 per parameter. The parts are
combined by their evidences, so an evidence bias matters here. It costs 2.25
times the likelihood calls.

## Implementation

Consumer repository `desi_darksirens_selection`, branch
`phase12.5/spectral-joint` at **008e780** (from
`phase12.5/free-rate-index`), pushed, no pull request. The checks below ran
on earlier commits of the branch with the same likelihood code; the final
guard map and the unit tests ran on the final commit.

- `phase12/spectral_joint.py` builds the target. The base stays the fully
  fixed population; every call writes the sampled values into the population
  vector, as step 1 does for γ. One compiled program serves the likelihood
  and its diagnostics, with the events, the injections and the population
  vector as arguments.
- The priors are in `config/spectral_joint.json`; the manifest sets only the
  H0 part, the seed and the sampler.
- `scripts/phase12_5_spectral_joint.py` has five commands: the control grid,
  the guard map, the timing, the chain, and the combination.
- The chain writes, per run: posterior summaries of the twelve parameters and
  of the second peak's fraction; ln Z and its error; the convergence record;
  the guard record at the posterior mean, the median and the best point; the
  guard record at 4000 posterior samples (the fraction penalised); the input
  files' sha256; the code commit. Samples are saved equal-weighted and as
  every nested-sampling point with its raw weight.
- A resumed chain must match the checkpoint's target, priors, H0 part, seed,
  sampler settings and input hashes; core refuses it otherwise.

**Why not core's own partial fixing** (`ds.Population(name, fixed={...})`
with `ds.infer`): it cannot set γ's prior to −2 to 6 (the model range is −10
to 10), it does not return the guard diagnostics from the compiled program,
and core fingerprints a checkpoint only for a target built by the caller.

## Checks before the chains

All on the real 259 events. CPU jobs on HENON; one GPU job on rita. Outputs:
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/A1/`
(`checks/`, `smoke_runs/`, `logs/`).

### 1. Control: the pinned target is the spectral grid

With every sampled population parameter at its fixed value, the new target on
the 241-point H0 grid against the stored grids at the corrected spin
(`phase12_5/spectral_gamma/runs/`):

| rate index | largest difference in ln L | ln L range on the grid | H0 median [68%], new / stored |
|---|---|---|---|
| 2.5439 (GWTC-5) | 9.1e-13 | −717.9 to −654.5 | 66.17 [61.45, 71.15] / the same |
| 2.25 | 9.1e-13 | −719.7 to −654.1 | 68.00 [63.12, 73.14] / the same |

- The selection N_eff agrees to 7e-15 (relative); no grid point is penalised
  in either.
- After the first point the 240 others caused no retrace and no
  recompilation.

### 2. Guard map: how much of the prior the selection guard penalises

**With the model-range spin priors (the first proposal, superseded).** 2000
draws, 1000 in each H0 part, both spin priors on their model ranges up to 1
(`checks/b_guard_map_low`, `_high`).

| | H0 20 to 45 | H0 45 to 140 |
|---|---|---|
| no penalty | 10.4% | 12.6% |
| finite penalty | 88.6% | 86.1% |
| likelihood −∞ | 1.0% | 1.3% |
| N_eff over threshold: 16%, median, 84% | 0.003, 0.041, 0.32 | 0.003, 0.051, 0.59 |
| N_eff over threshold: 95%, 99% | 5.6, 23 | 9.0, 34 |
| typical penalty where penalised (median, in ln L) | −3.4e5 | −1.3e5 |

- **The spin priors drive it.** Of the 1,502 draws with either spin parameter
  above 0.5, six are unpenalised. With both below 0.3 (186 draws), 82% are.
- The penalty is so large that a penalised region is excluded in practice.
  The guard acts as a cut on the prior, not as a gentle weight.
- The two H0 parts lose the same share (10.4 ± 1.0% against 12.6 ± 1.0%
  kept), so the cut does not favour one part by itself.

**With the final priors** (spin mean on 0 to 0.3, width on 0.005 to 0.3),
1000 draws per part on the final configuration and commit (job 1376407,
`checks/b_guard_map_final_low`, `_high`). An earlier job with the same priors
given on the command line (1376400) has the same draws and the same
likelihoods, bit for bit.

| | H0 20 to 45 | H0 45 to 140 |
|---|---|---|
| no penalty | 78.0% | 78.9% |
| finite penalty | 21.4% | 20.2% |
| likelihood −∞ | 0.6% | 0.9% |
| N_eff over threshold: 16%, median, 84% | 0.69, 6.2, 21 | 0.67, 6.7, 21 |

What is still penalised there, by parameter (fraction of draws penalised in
the lowest and highest fifth of each prior, both parts together):

| parameter | lowest fifth | highest fifth |
|---|---|---|
| second peak width σ2 | 49% (below 1.9) | 11% |
| effective-spin width σ_χ | 48% (below 0.064) | 23% (above 0.24) |
| effective-spin mean μ_χ | 13% | 33% (above 0.24) |
| first slope α1 | 14% | 29% (above 9) |
| rate index γ | 17% | 30% (above 4.6) |
| second slope α2 | 30% (below −0.7) | 21% |
| H0, the break, both peak positions, both fractions | 20% to 23% | 19% to 25% |

With σ2 above 2, σ_χ above 0.03 and γ below 4.5 as well, 93% of the draws
are unpenalised.

**Reading.** With the final priors the guard leaves 78% to 79% of the prior
alone, the same share in both H0 parts. The corrected spin values (0.04,
0.10) lie well inside the unpenalised region, and at the fixed population the
selection N_eff is 22 to 37 times its threshold on the whole H0 grid. What
is still cut lies at the edges named in the table. The penalty is still so
large that a penalised region is excluded in practice, and the evidences are
relative to the declared prior including the cut 21% to 22%.

### 3. CPU smoke with a kill and a resume

The low-H0 chain at 40 live points, checkpoint every 20 s
(`checks/c_kill_resume`):

- Session 1 was killed (SIGKILL) after 420 s, at iteration 151 with 2,645
  likelihood calls, leaving a checkpoint and no result.
- Session 2, the same command, resumed "at iteration 150 (2501 likelihood
  calls already spent)", sampled to its call cap (8,549 calls in all) and
  wrote the result and the samples, with all 273 nested points and their
  weights.
- A run that stops at its own call cap is finished for dynesty and cannot be
  continued. Only a killed or requeued run resumes. The production cap is
  20 million calls, far above the estimate.
- The smoke manifest as first drafted (four chains at 40 live points and 1500
  calls each, with the model-range spin priors, then the combination) ran
  through the stage runner with 0 failed stages. Its numbers mean nothing: no
  chain is converged. The eight-chain manifest was dry-run, not smoked again.

### 4. Unit tests

408 pass on CPU at the final commit 008e780 (job 1376408; 375 before this
branch, 33 new).

They include: the target at the fixed values equals the grid stage's
likelihood; each coordinate lands in its own population entry; no call
retraces; a run killed mid-sampling resumes and converges; a checkpoint is
refused for another H0 part, seed or input file; the combination of the
parts reproduces hand-computed weights and seed scatter, with unequal seed
counts and with a chain that has no result yet.

### 5. GPU timing (rita A100-80, job 1376403, 8 minutes)

| | seconds |
|---|---|
| one likelihood call, compiled (300 prior draws per H0 part) | 0.0018 |
| first call, with compilation | 6 |
| one prior transform (core evaluates the triangle map step by step on the GPU) | 0.0037 measured alone |
| **one call inside a running chain, all included** | **0.0038** |

- The last line is the production chain command (H0 45 to 140, 1000 live
  points, 72 steps; at that time with the model-range spin priors, which do
  not change the cost of a call) run for 407 s and then killed: 108,434
  calls. It is the
  figure used below.
- No call after the first retraced or recompiled.
- This is 60 times faster than the 0.23 s per call of the DESI target.
- The progress line of that run showed "logz +/- nan". It is dynesty's
  running estimate, upset by the −∞ points at the start. Recomputed over the
  stored run as dynesty does at the end, the evidence error is finite (0.089
  at that stage); the finished CPU smoke's is finite too.

## What will be reported

For the combined posterior and for each of the eight chains:

- H0: median, 68% and 90% intervals, sd. Against the fixed-population
  spectral value 66.2 [61.4, 71.1] and the value with only the rate index
  free, 67.9 [62.7, 73.4]: the shift in km/s/Mpc and the ratio of widths.
- **The posterior mass of H0 below 45**: the pooled value, the four
  matched-pair values with their sd, and the range over the sixteen
  pairings; and whether a separate mode is there: the H0 and first-peak
  position of the low part's posterior.
- Each population parameter's posterior against its GWTC-5 value and
  interval, and against its prior: which are measured, which follow the
  prior, which pile up at an edge.
- The spin pair against (0.04, 0.10), the values now fixed in step 1.
- The correlation of each parameter with H0.
- ln Z of each chain and of the combination, and per part the seeds' sd
  against the errors dynesty reports.
- Convergence, and the guard: N_eff over threshold at the posterior mean,
  median and best point, and the fraction of posterior samples penalised, per
  chain.

## Expectations, not thresholds

- In the high part, H0 near 66 to 68 with a wider posterior than the
  fixed-population sd of 5.
- The spin posterior near (0.04, 0.10), well inside its prior of 0 to 0.3.
- The low part is not predicted. The archived mode was found at the old spin
  values with 18 parameters free; 12Z's one-parameter ridge toward low H0
  along the first peak's position was mildly disfavoured (4 in ln L at 11
  solar masses).
- A posterior that piles up at a prior edge, sits where the guard penalises,
  or differs between seeds by more than the evidence errors is reported as
  such and not interpreted.

## Run plan

- One job on one rita A100: `sbatch slurm/phase12_5_A1_runner.sbatch` in the
  consumer worktree `phase12_5/repo_A1`. It runs
  `config/phase12_5_A1_manifest.json` in order, alternating the parts so
  that one seed of each finishes first:

  | order | H0 part | seed |
  |---|---|---|
  | 1 | 45 to 140 | 41 |
  | 2 | 20 to 45 | 31 |
  | 3 | 45 to 140 | 42 |
  | 4 | 20 to 45 | 32 |
  | 5 | 45 to 140 | 43 |
  | 6 | 20 to 45 | 33 |
  | 7 | 45 to 140 | 44 |
  | 8 | 20 to 45 | 34 |
  | 9 | the combination | |

- A first complete answer exists after two chains. The combination can be run
  by hand at any time on the chains that have finished.
- A finished stage is skipped and an unfinished chain resumes its
  checkpoint, so resubmitting the same file continues the run.
- Outputs: `phase12_5/A1/runs/<chain>/result.json`, `samples.npz`, and
  `runs/combined/`.
- **Estimated cost.** The archived 18-parameter split runs needed 49
  iterations per live point. With 35 to 50 here, 1000 live points and 72
  calls per iteration, a chain is 2.5 to 3.6 million calls: about 3 to 4
  hours per chain at 0.0038 s per call, **21 to 30 GPU-hours for the eight**.
  Treat it as uncertain by a factor of two. The job's limit is 7 days.

## Risks

- **The guard as a prior cut.** With the final priors, 21% to 22% of the
  prior volume is cut, at small second-peak width, at the narrow and wide
  ends of the spin width, and at high spin mean, rate index and first slope.
  If the posterior of any chain touches the cut, the guard shapes it. The
  fraction of posterior samples penalised says so.
- **The spin prior's upper edges.** If either spin posterior reaches 0.3, the
  narrowed prior is shaping it and the result says so.
- **The low part.** Its preferred region (small fractions at low H0, 12Z) is
  where the one-parameter scans met the guard. If the low mode's weight
  depends on the guard cap, a control at another cap is needed before it is
  quoted. The owner decided against that control for now.
- **Evidence accuracy.** The low part's mass rests on a difference of two
  ln Z. Four seeds per part measure the scatter; a seed sd well above the
  errors dynesty reports means the weight is quoted with the seed scatter,
  not the reported error.
- **More than one mode inside a part.** The split separates H0 below and
  above 45 only.
- **Conditional results.** Six population parameters stay fixed, and the
  cosmology has one free parameter.
- **Not exercised yet:** a chain run to convergence on the real events (the
  smokes are capped); a resume on the GPU (done on CPU only); the eight-chain
  manifest beyond its dry run.

---

## Second attempt (2026-10-09): all seventeen population parameters, the GWTC-5 paper's priors, variance limit 1

### What happened to the first attempt

- Job 1376409 on rita ran the first two chains (H0 45 to 140 with seed 41,
  H0 20 to 45 with seed 31) to convergence, 3.4 and 3.5 hours each. The owner
  cancelled it during the third chain.
- **It failed.** The width of the second mass peak, with a prior flat on 0 to
  10 solar masses, collapsed:

  | | H0 45 to 140, seed 41 | H0 20 to 45, seed 31 |
  |---|---|---|
  | H0 (median, 68%) | 86.1 [76.1, 91.7] | 40.5 [40.2, 41.6] |
  | second peak width, median (solar masses) | 0.022 | 0.0008 |
  | ln Z | −670.36 ± 0.21 | −672.39 ± 0.24 |
  | highest ln L | −630.4 | −629.4 |
  | variance of ln L at that point | 19.7 (limit 20) | 19.9 (limit 20) |
  | posterior points the selection guard penalises | 54% | 52% |
  | selection N_eff over its threshold, median | 1.12 | 1.13 |

  In the high part 98% of the posterior has the width below 0.1 solar
  masses. In the low part the posterior is a few repeated points near
  H0 = 40.38. Weight of the low part: 0.033.
- A Gaussian that narrow puts its weight on single posterior samples of
  single events. The Monte Carlo sums over those samples are then not
  estimates of an integral. The run allowed a variance of 20 on the
  log-likelihood estimator, and its best points sit at 19.7 and 19.9: the
  sampler climbed until it met the limit.
- These numbers are a record of the failure, not results.
- Its outputs are kept under `phase12_5/A1/runs_attempt1/`: the two finished
  chains, the unfinished third (`high_seed42`, 8 minutes) and the runner's
  status file. `phase12_5/A1/runs/` starts empty.

### Owner decision

The setup of the GWTC-5 population paper (arXiv:2605.27226): every mass
parameter sampled with the paper's priors, the paper's limit of 1 on the
variance of the likelihood estimator, and the ranges of the paper's
effective-spin model for our spin pair. Kept from before: H0 flat on 20 to
140 split at 45, four seeds per part (41 to 44 above 45, 31 to 34 below),
dynesty with 1000 live points and dlogz 0.1, the same inputs, cosmology and
core version.

### The priors

18 sampled dimensions: H0 and all 17 parameters of core's
`brokenpowerlaw+2peaks` GWTC-5 model. All flat on the range given.

| parameter | prior | source |
|---|---|---|
| H0 | 20 to 140, run as 20 to 45 and 45 to 140 | owner (not sampled in the paper) |
| first slope α1 | −4 to 12 | paper Table 5 |
| second slope α2 | −4 to 12 | Table 5 |
| break mass | 20 to 50 | Table 5 |
| first peak position μ1 | 5 to 20 | Table 5 |
| first peak width σ1 | 0 to 10 | Table 5 |
| second peak position μ2 | 25 to 60 | Table 5 |
| second peak width σ2 | 0 to 10 | Table 5 |
| lower mass edge m1,low | 3 to 10 | Table 5 |
| taper range δm1 | 0 to 10 | Table 5 |
| peak fractions λ0, λ1 | uniform on λ0 + λ1 ≤ 1 | Table 5, Dirichlet(1, 1, 1) |
| mass-ratio slope βq | −2 to 7 | Table 5 |
| lower edge of the secondary m2,low | 3 to m1,low (conditional) | Table 5 |
| taper range of the secondary δm2 | 0 to 10 | Table 5 |
| maximum mass | fixed at 300 | Table 5 |
| rate index γ (the paper's κz) | −10 to 10 | Table 7 |
| effective-spin mean | 0 to 1 | Table 8 gives −1 to 1; our model admits 0 to 1 |
| effective-spin width | 0.05 to 1 | Table 8 |

- Each Table 5 range was read from the paper's text and compared with the
  ranges of core's model class at the installed version (e7c3007): they are
  the same, entry by entry. A test in the consumer repository holds a typed
  copy of the paper's ranges and compares the configuration with it and with
  the model.
- The two joint priors are core's cube maps, so no prior volume has zero
  likelihood: the fractions uniform on the triangle (which is
  Dirichlet(1, 1, 1)), and m2,low = 3 + u (m1,low − 3) with u uniform.
- Six parameters are new relative to the first attempt: the first peak's
  width, both lower edges, both taper ranges and the mass-ratio slope. The
  rate index widens from [−2, 6]; the spin mean from [0, 0.3]; the spin width
  from [0.005, 0.3] to [0.05, 1].

### The variance limit, in our code and in the paper

The paper (Sec. 3): "we require a maximum variance of 1 on the population
likelihood estimator ... implemented as a sharp or smoothly-tapered cutoff".
It gives no formula.

What `numerics.max_likelihood_variance = 1.0` does in core e7c3007
(`selection/gw.py`, `selection_log_correction`, called by
`spectral_siren_log_likelihood`):

- **It limits the total variance of the log-likelihood estimator:** the sum
  over the 259 events of each event's Monte Carlo variance of ln Z_i (from
  its 4096 reweighted posterior samples, Σw²/(Σw)² − 1/n), plus
  N_obs²/N_eff for the selection term. This is the estimator of Talbot &
  Golomb (2023) that the paper cites. Covariances between the terms are
  neglected.
- **It is applied as a threshold on the selection N_eff:**
  N_eff > N_obs² / (1 − Σ event variances), and never below 5 N_obs. If the
  events alone exceed 1, no N_eff passes.
- **With `selection_neff_soft_guard = true` (ours) the cutoff is smooth, not
  a rejection.** Below the threshold the log-likelihood gets a steep finite
  penalty that grows with the distance below it and with the size of the
  selection term. The penalty is numerically zero above about 1.15 times the
  threshold and overwhelms the likelihood below about 0.95 times it. Points
  over the limit therefore stay finite and ordered, which nested sampling
  needs to start from a prior that is mostly over the limit.
- **The limit and the selection guard are one mechanism.** The first number
  sets the threshold; the second switch chooses a hard wall or the smooth
  penalty. "Penalised by the selection guard" and "over the variance limit"
  describe the same test. Our records call a point penalised when the smooth
  and the hard corrections differ at all, which includes the band from 1.0
  to 1.15 times the threshold where the penalty is tiny.

Differences from the paper, as far as its text allows a comparison:

- The shape of our smooth cutoff is core's own, not the taper of Callister &
  Farr (2024) that the paper names as an example.
- Core's likelihood also carries the Farr (2019) term N(N+3)/(2 N_eff) for
  the uncertainty of the selection integral. Inside the limit it is at most
  about 0.5 in ln L. The paper does not say it uses this term (not verified).
- The paper's exact estimator is not written out; that it is the total
  variance above is our reading of its references.

### What is not like the paper

- **The spin model.** The paper's default has spin magnitudes and tilts
  (Table 6). Ours is a Gaussian in the effective spin, so the owner chose
  the ranges of the paper's effective-spin model (Table 8) for the mean and
  width. That model also has a second spin, a correlation and a skewness;
  ours has none of them.
- **The inputs.** Our 259 events with 4096 posterior samples each and our
  injection set (`A_sel_chieffref_o3o4ab_v20_exact.h5`). The variance, and
  so where the limit falls, depends on both.
- **H0 is sampled.** The paper fixes the cosmology.
- **The sampler** (dynesty, split H0 prior, four seeds per part).

### Known before any check: the reference population is at the limit

From the stored spectral grid at the reference population (GWTC-5 values,
spin 0.04 and 0.10), made with limit 20:

| H0 | variance from the events | from the selection (N_eff) | total |
|---|---|---|---|
| 20 | 0.24 | 0.88 (76,500) | 1.12 |
| 32.5 | 0.25 | 0.80 (83,800) | 1.05 |
| 45 | 0.24 | 0.75 (89,600) | 0.98 |
| 66 | 0.20 | 0.66 (101,000) | 0.86 |
| 92.5 | 0.17 | 0.59 (113,900) | 0.76 |
| 140 | 0.16 | 0.54 (124,200) | 0.70 |

- With limit 1 the reference population itself is over the limit below
  H0 ≈ 42, and inside the band where the smooth penalty is not exactly zero
  below H0 ≈ 60.
- Consequence 1: the limit will act as a cut that depends on H0 near the
  GWTC-5 values. A posterior pressed against it is shaped by our injection
  set, and the result must say how much of the posterior is there.
- Consequence 2: the chain command checks, before sampling, that the
  reference population at the middle of its H0 range is free of any penalty.
  In the high part (H0 92.5) it is. **In the low part it is not, at any H0 in
  20 to 45.** How the low-part chains are started is recorded under the
  checks below before any chain is submitted.

### Sampler

As the first attempt: dynesty, 1000 live points, dlogz 0.1, random walk with
the walks setting "scaled" (six steps per dimension). In 18 dimensions that
is 108 steps per iteration, where the 12-dimensional first attempt had 72.

### Checks before the chains

Outputs in `phase12_5/A1/checks2/`. Results are added here before any chain
is submitted.

1. **Control.** The 18-dimensional target at the reference values against
   the stored spectral grids (rate index 2.5439 and 2.25): with the limit set
   back to 20 it must equal them at every H0 to 1e-8; with limit 1 it must
   equal them wherever neither limit acts.
2. **The first attempt's spike.** The 200 highest-likelihood points of each
   finished chain, with the six parameters that attempt held fixed at their
   fixed values: at limit 20 they must reproduce the stored likelihoods; at
   limit 1 their variance must be over the limit and their likelihood
   penalised. **If limit 1 does not reject them, no chain is submitted.**
3. **Guard map on the prior.** 2000 prior draws in each H0 part: the fraction
   inside the limit. A large rejected fraction is expected. Below about 1%
   accepted, the start of nested sampling is a concern and is reported.
4. **Unit tests** of the consumer repository's two test files for this stage.
5. **GPU timing** on rita: seconds per call, and a 7-minute stretch of the
   real chain command in a scratch directory.

### Results of the checks (2026-10-09, consumer commit 3ebc505)

HENON job 1376479 (control, spike, guard map), HENON job 1376480 (tests),
rita job 1376481 (timing).

**1. Control: passed.**

- Limit set back to 20: the 18-dimensional target equals the stored grid at
  all 241 H0 values, largest difference 9e-13 in ln L, at both rate indices.
  No recompilation after the first point.
- Limit 1: equal to 9e-13 at the 162 H0 values where no penalty acts
  (H0 ≥ 59.5). The reference population is inside the limit for H0 ≥ 42.5 and
  over it for H0 ≤ 42. Its penalty in ln L: −0.003 at H0 45, −0.17 at 42,
  −10,400 at 32.5, −84,400 at 20. The smooth cutoff is close to a wall.
- H0 from the reference-population grid is unchanged by the limit:
  66.2 [61.4, 71.1].

**2. The first attempt's spike: rejected by limit 1.**

| 200 best points of | H0 45 to 140, seed 41 | H0 20 to 45, seed 31 |
|---|---|---|
| total variance of ln L | 17.2 to 20.1 | 14.2 to 20.0 |
| of which from the events alone | 6.1 to 7.5 | 9.3 to 9.9 |
| ln L at limit 20 (as stored) | −631.8 to −630.4 | −630.1 to −629.4 |
| ln L at limit 1 | −509,000 to −463,000 | −690,000 to −686,000 |

- All 400 points are over the limit and penalised. The events' variance
  alone is six to ten times the limit, so no selection N_eff could admit
  them.
- At limit 20 the embedded points reproduce the stored likelihoods to 1e-9,
  so the embedding is right.

**3. Guard map on the prior: 0.2% to 0.3% of the prior is inside the limit.**

| 2000 prior draws | H0 20 to 45 | H0 45 to 140 |
|---|---|---|
| inside the variance limit | 4 (0.20%) | 6 (0.30%) |
| inside it with a finite likelihood | 3 | 5 |
| free of any penalty | 0 | 4 (0.20%) |
| penalised, finite | 76.8% | 74.2% |
| minus infinity (no support for some event) | 23.2% | 25.7% |
| events' variance alone over 1 | 79% | 79% |
| total variance, median | 224 | 208 |
| inside limit 20, for comparison | 11.1% | 9.9% |

- **This is below the 1% mark.** Almost the whole prior is over the limit,
  mostly because the events' own Monte Carlo sums fail there. The sampler
  starts on the penalty's slope, not on the likelihood.
- The 7-minute stretch of the real chain command (H0 45 to 140) did start
  and climb: 3926 iterations, the worst live point's ln L from below
  −400,000 to −22,200. It had not reached the region inside the limit.

**4. Unit tests:** 32 passed.

**5. GPU timing (rita A100-80).**

- Likelihood: 0.0018 s per call, no recompilation. Prior transform: 0.0056 s
  per call (0.0037 s in the first attempt; it now carries two joint maps).
- Chain stretch: 76,300 calls in 406 s, 0.0053 s per call, 108 calls per
  iteration.
- **Estimated cost.** The first attempt's production chains ran 1.2 times
  slower per call than its stretch, so about 0.006 s per call. With 50 to 80
  iterations per live point (the archived 18-parameter runs needed 49; the
  priors here are wider), a chain is 5.4 to 8.6 million calls: **9 to 14
  hours per chain, 3 to 5 days for the eight** in one job. Uncertain by a
  factor of two; the job's limit is 7 days. The walks setting is kept.

### The low-part chains are held (decision needed)

- The chain command refuses to start unless the reference population at one
  H0 inside its range is free of any penalty. Under limit 1 that holds only
  for H0 ≥ 59.5. The four chains on H0 20 to 45 would therefore stop before
  sampling, whatever anchor H0 is chosen.
- That check has not been changed. Whether to record the anchor instead of
  refusing, for this stage, is the owner's decision.
- More than the start is at stake. In the low part the GWTC-5 values
  themselves are over the limit below H0 42, with our injection set. A low
  mode can only live at other population values, and the weight of the low
  part against the high part will depend on where the limit falls.

### Run plan

- **Submitted now: the four chains on H0 45 to 140** (seeds 41 to 44), in one
  job on one rita A100:
  `PHASE12_5_A1_ONLY="high_seed41 high_seed42 high_seed43 high_seed44" sbatch slurm/phase12_5_A1_runner.sbatch`
  in `phase12_5/repo_A1`. Outputs in `phase12_5/A1/runs/`.
- **Not submitted: the four chains on H0 20 to 45 and the combination.**
  After the decision above, the same file without the selection runs what is
  left; finished chains are skipped and an unfinished one resumes.
- The high part alone is not the result. It is H0 conditional on H0 ≥ 45.

### Risks specific to this attempt

- **The limit as a cut in H0.** At the GWTC-5 values the total variance
  falls from 1.12 at H0 20 to 0.70 at H0 140. The limit therefore removes
  low H0 first. The posterior's low-H0 edge may be the limit's, not the
  data's. The fraction of posterior points penalised, and their H0, will be
  reported for every chain.
- **A posterior on the limit.** The first attempt's posterior sat on its
  limit (54% and 52% of points in the penalty band). The same may happen at
  limit 1; then the result depends on the limit.
- **Start of sampling** from a prior that is 99.7% over the limit: shown to
  work for 7 minutes, not to convergence.

---

## Third attempt (2026-10-09): variance limit 4

### What happened to the second attempt

- The four chains on H0 45 to 140 were submitted at limit 1 (rita job
  1376483). The owner cancelled the job after 3 minutes, on the check results
  above. Nothing was sampled to any purpose.
- Its partial output (the first chain's checkpoint and log) is kept under
  `phase12_5/A1/runs_attempt2_var1/`. `phase12_5/A1/runs/` starts empty.

### Why limit 1 was dropped

- **With our injection set, limit 1 falls on the GWTC-5 values themselves.**
  Total variance of ln L at the reference population:

  | H0 | total variance | under limit 1 |
  |---|---|---|
  | 20 | 1.12 | over the limit, penalty −84,400 in ln L |
  | 32.5 | 1.05 | over the limit, penalty −10,400 |
  | 42 | 1.00 | over the limit, penalty −0.17 |
  | 45 | 0.98 | inside, penalty −0.003 |
  | 59.5 and above | 0.90 and below | no penalty |
  | 140 | 0.70 | no penalty |

  The limit would have cut low H0 first, and the weight of the low part
  against the high part would have been set by it.
- **Only 0.2% to 0.3% of the prior is inside limit 1** (4 and 6 of 2000 draws
  in the two H0 parts).
- The chains on H0 20 to 45 could not start: their start check needs the
  reference population free of any penalty somewhere in the range.

### Owner decision

**Variance limit 4**, the paper's relaxed cut ("for some models, we also show
results with a more relaxed variance cut in App. B"; its figures compare
"var=1" and "var=4"). Everything else as the second attempt: the priors
table, the 18 dimensions, the split at 45, four seeds per part, the sampler,
the inputs, the smooth cutoff.

Source of the value, checked in the released LVK result files
(`/hildafs/projects/phy220048p/share/LVK_population_analyses/popsummary_files/`,
the two `gwtc5_updated_default_*` files for the broken power law + 2 peaks
model, 259 events each):

| file | posterior samples | `variance` column: median | maximum |
|---|---|---|---|
| default | 8200 | 0.968 | 0.999994 |
| `var_4` | 8842 | 3.05 | 3.999982 |

- The relaxed cut is 4, and it is sharp in those runs.
- The files also settle the definition left open above. They carry one
  variance column per event and the selection N_eff. In the default file the
  median of the summed event variances is 0.50 and 259²/N_eff at the median
  N_eff (147,400) is 0.46: together the reported total, to the precision of
  comparing medians. **The paper's variance is the same total as ours.**
- The LVK posterior itself sits on its limit: 90% of the default file's
  samples have a variance above 0.9. A posterior pressed against the limit
  is a property of the method, not only of our inputs.
- Their selection N_eff is higher than ours at comparable populations
  (median 147,400 in the default file; ours is 76,500 to 124,200 at the
  GWTC-5 values). Limit 1 costs us more than it costs them.

### Expected at limit 4

- At the reference population the threshold on N_eff is about 17,900
  (259²/(4 − 0.25)); N_eff there is 76,500 to 124,200. No penalty at any H0
  from 20 to 140 is expected. **Checked before the chains; if any H0 is
  penalised, no chain is submitted.**
- The first attempt's spike had the events' variance alone at 6.1 to 9.9, so
  limit 4 should still reject it. **Checked before the chains; if it is not
  rejected, no chain is submitted.**
- From the limit-1 guard map's recorded variances, about 3% to 4% of the
  prior is inside limit 4.

### Checks before the chains

Outputs in `phase12_5/A1/checks3/`; results are added here before any chain
is submitted.

1. Control at the declared limit 4 against the stored spectral grids, at
   both rate indices: equal at every H0 to 1e-8, and no penalty at any H0.
2. Total variance and penalty against H0 at the reference population, 20 to
   140, from the same run.
3. The first attempt's 400 best points at limit 4 (must be rejected) and at
   limit 20 (must reproduce the stored likelihoods).
4. Guard map on the prior, 2000 draws per H0 part.
5. Unit tests; a short GPU timing.

### Results of the checks (2026-10-09, consumer commit cc5fb8e)

HENON job 1376484 (control, spike, guard map), HENON job 1376485 (tests),
rita job 1376486 (timing). **All pass.**

**1. Control at limit 4: passed.** Equal to the stored grids at all 241 H0
values (largest difference 9e-13 in ln L), at both rate indices, with no
recompilation. H0 from the reference-population grid: 66.2 [61.4, 71.1].

**2. The reference population is free of any penalty from H0 20 to 140.**

| H0 | variance from the events | from the selection | total | N_eff over its threshold | penalty |
|---|---|---|---|---|---|
| 20 | 0.25 | 0.88 | 1.12 | 4.3 | 0 |
| 32.5 | 0.25 | 0.80 | 1.05 | 4.7 | 0 |
| 45 | 0.24 | 0.75 | 0.98 | 5.0 | 0 |
| 66 | 0.20 | 0.66 | 0.86 | 5.7 | 0 |
| 92.5 | 0.17 | 0.59 | 0.76 | 6.5 | 0 |
| 140 | 0.16 | 0.54 | 0.70 | 7.1 | 0 |

The penalty is exactly zero at all 241 H0 values, also at rate index 2.25
(total variance 0.74 to 1.13). Both start points of the chains (H0 32.5 and
92.5) pass the unchanged start check.

**3. The first attempt's spike: still rejected.** All 400 points are over
limit 4 (total variance 14.2 to 20.1; from the events alone 6.1 to 9.9) and
penalised: ln L −463,000 to −690,000, where the first attempt had about
−630. At limit 20 they reproduce the stored likelihoods to 1e-9.

**4. Guard map on the prior.**

| 2000 prior draws | H0 20 to 45 | H0 45 to 140 |
|---|---|---|
| inside the variance limit | 76 (3.8%) | 56 (2.8%) |
| inside it with a finite likelihood | 3.2% | 2.5% |
| free of any penalty | 2.8% | 2.2% |
| penalised, finite | 74.1% | 72.2% |
| minus infinity (no support for some event) | 23.2% | 25.7% |
| events' variance alone over 4 | 39% | 35% |

About 3% of the prior is inside the limit, above the 1% mark (0.2% to 0.3%
at limit 1).

**5. Unit tests:** 32 passed.

**6. GPU timing (rita A100-80).** Likelihood 0.0018 s per call, no
recompilation; prior transform 0.0058 s. The 7-minute chain stretch (H0 45
to 140) made 67,400 calls in 406 s, 0.006 s per call, and reached ln L
−1358 for its worst live point after 3760 iterations (at limit 1 it was at
−22,200 after as many). **Estimated cost, as before: 9 to 14 hours per
chain, 3 to 5 days for the eight** in one job, uncertain by a factor of two;
the job's limit is 7 days.

### Risks at limit 4

- **A posterior on the limit.** Likely: the first attempt's posterior sat on
  limit 20 and the LVK posteriors sit on theirs. The fraction of posterior
  points penalised, their variance and their H0 are reported for every
  chain. If the second peak's width, or any width, collapses again, the
  attempt has failed like the first.
- **The limit against H0.** At the GWTC-5 values the limit is now 3.5 to 5.7
  times away in variance, at every H0. Away from them it is not known.
- **A result that depends on the limit.** One limit is run. The paper shows
  both of its limits for that reason.
- **Minus infinity in a quarter of the prior.** Its cause was not
  investigated (taken to be an event left without support).

### Run plan

`sbatch slurm/phase12_5_A1_runner.sbatch` in `phase12_5/repo_A1`: all eight
chains in the alternating order, then the combination, one job on one rita
A100. The start check of the chain command is unchanged.

---

## Limit-8 bracket (declared 2026-10-10, coordinator for the owner)

### Why

- The limit-4 chains are running (rita job 1376492). In the two finished ones
  (H0 45 to 140 seed 41, H0 20 to 45 seed 31) about 20% of the posterior is
  penalised by the smooth limit, and 14% to 16% of points lie within 10% of
  the N_eff threshold. The first mass peak's width presses on the limit: its
  median is 0.17 to 0.19 solar masses, and penalised points are about half as
  wide as unpenalised ones. The second peak's width is healthy.
- A posterior on the limit may depend on it. The stricter side is tested
  without new chains, by reweighting the limit-4 posteriors to limits 3 and 2
  (outputs in `phase12_5/A1/checks4/`). Limit 1 is excluded, as recorded
  above. **This bracket tests the looser side.**

### Setup

- **Variance limit 8; everything else identical to the limit-4 run:** the
  priors table, 18 dimensions, inputs, cosmology, core e7c3007, the smooth
  cutoff, dynesty with 1000 live points, dlogz 0.1, walks "scaled" (108).
- **Two chains per H0 part:** 45 to 140 with seeds 41 and 42; 20 to 45 with
  seeds 31 and 32. Run in that alternating order, then their combination by
  evidence.
- The limit-8 configuration is the limit-4 configuration with one override,
  `numerics.max_likelihood_variance=8.0`, in its own manifest
  (`config/phase12_5_A1_var8_manifest.json`). It runs from a second worktree
  (`phase12_5/repo_A1b`, branch `phase12.5/spectral-joint-brackets`) because
  the limit-4 job reads `repo_A1` at every stage.
- Outputs in `phase12_5/A1/runs_var8/`; `A1/runs/` is not touched.
- One rita job, submitted with `--dependency=afterany:1376492`, so it starts
  when the limit-4 job frees the GPU. Estimated 9 to 14 hours per chain,
  1.5 to 2.5 days for the four.

### Check before submission

- **The first attempt's spike must still be rejected at limit 8.** Its 400
  best points have a variance of 6.1 to 9.9 from the events alone and 14 to
  20 in total. **If limit 8 does not reject them, nothing is submitted.**
- Control at limit 8 against the stored spectral grids (equal at every H0,
  no penalty at the reference population).
- Outputs in `phase12_5/A1/checks_var8/`.

### What will be compared with limit 4

Per H0 part and after the evidence combination:

- the H0 median shift and width ratio, in units of the limit-4 posterior
  standard deviation;
- the first peak's width (median and lower tail);
- the penalised fraction and the quantiles of N_eff over its threshold;
- the evidence ratio between the parts.

**Read as heading toward the first attempt's collapse:** the first (or
second) peak's width running to its lower bound, or the pile-up at the
limit moving with the limit.

### Check results (2026-10-10, HENON job 1385447, brackets commit a611f51)

- **The first attempt's spike is rejected at limit 8.** All 400 points are
  over the limit and penalised. Their ln L is −408,000 to −690,000 (about
  −630 in the first attempt), and N_eff over its threshold is at most 0.16.
  At limit 20 they reproduce the stored likelihoods to 1e-9.
- Control at limit 8: equal to the stored grids at all 241 H0 values (9e-13),
  at both rate indices. No penalty at the reference population at any H0;
  N_eff is at least 8.7 times its threshold.
- Submitted: rita job, dependency `afterany:1376492` (job ID in the report).

---

## Results (2026-10-18)

Outputs under `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/A1/`:
`runs/` (limit 4), `runs_var8/` (limit 8), `checks4/` (reweighting and the
comparison). Consumer commits as declared (cc5fb8e for limit 4, the brackets
branch 0934239 for limit 8 and the comparison).

### Limit 4: the eight chains (rita job 1376492, 9 to 11 October)

Every chain converged and met its gate, in 5.9 to 6.3 hours on one A100. *(25 Oct 2026: 5.73 to 6.45 hours of sampling; 5.9 and 6.3 are the per-part means. See the errata in "Amendment (25 Oct 2026): independent review".)*

| H0 part | seed | H0 median [68%] | ln Z | posterior penalised |
|---|---|---|---|---|
| 45 to 140 | 41 | 67.9 [55.9, 80.0] | −681.23 ± 0.20 | 20.1% |
| 45 to 140 | 42 | 68.8 [56.6, 80.2] | −681.48 ± 0.20 | 20.0% |
| 45 to 140 | 43 | 68.8 [57.0, 80.1] | −681.53 ± 0.21 | 19.6% |
| 45 to 140 | 44 | 69.2 [57.1, 81.1] | −682.00 ± 0.20 | 19.8% |
| 20 to 45 | 31 | 40.2 [34.6, 43.6] | −683.55 ± 0.20 | 19.3% |
| 20 to 45 | 32 | 39.9 [34.0, 43.7] | −683.76 ± 0.20 | 21.5% |
| 20 to 45 | 33 | 40.3 [34.7, 43.7] | −683.33 ± 0.20 | 20.4% |
| 20 to 45 | 34 | 40.5 [34.8, 43.8] | −683.36 ± 0.20 | 19.8% |

- **Combination** (prior mass times evidence, 40,000 pooled samples):
  ln Z −683.50 ± 0.10 (lower part) and −681.56 ± 0.16 (upper). Weight of
  the lower part 0.037; over the 16 seed pairings 0.021 to 0.065.
  *(25 Oct 2026: these ln Z errors are the seed scatter's standard error; limit 2 quotes the propagated reported errors. See the errata in "Amendment (25 Oct 2026): independent review", item 3.)*
- **H0 = 68.0 [55.0, 80.1] km/s/Mpc, sd 12.4; 90% [46.7, 86.6].** The
  population-fixed spectral result with γ free is 67.9 [62.7, 73.4], sd 5.40
  (12Y amendment): the median does not move and the width grows by 2.3.
- **Population.** Every parameter's 68% interval contains its GWTC-5 value
  except the first peak's width σ1, 0.20 [0.10, 0.42] against 0.78, and the
  second peak's position μ2, 34.1 [32.7, 35.7] against 32.3. The spin pair is
  0.035 [0.025, 0.046] and 0.110 [0.099, 0.121], consistent with the
  corrected fixed values (0.04, 0.10). γ is 2.41 [1.97, 2.88]. The second
  peak's width is 1.8 [0.47, 5.1]: the first attempt's collapse did not
  recur.
  *(25 Oct 2026: σ2's 68% interval also excludes its GWTC-5 value 5.73 (87th percentile, inside 90%); σ_chi's median is 0.109. See the errata in "Amendment (25 Oct 2026): independent review", items 1 and 4.)*

### What sets the width

In the upper part (38,540 of the 40,000 pooled samples), H0 follows the
position of the first mass peak:

- correlation of H0 with μ1: −0.85; a linear fit gives −30.3 km/s/Mpc per
  solar mass and explains 72% of the H0 variance; the residual sd is 5.9;
- the next correlations: σ2 −0.40, μ2 −0.38, break mass −0.32, γ −0.18;
  every other parameter |r| ≤ 0.11 *(25 Oct 2026: except σ1, +0.19; see the errata in "Amendment (25 Oct 2026): independent review", item 2)*; a linear fit on all 17 explains 83%;
- μ1 = 10.04 [9.70, 10.34] (GWTC-5 value 9.91). The lower part sits at
  μ1 ≈ 10.8 (median 10.84).

The population-fixed runs hold μ1 at the GWTC-5 value, which was fitted with
the cosmology fixed. The residual sd once the μ1 trend is removed (5.9) is
close to the population-fixed width (5.4): most of the difference between the
two widths is that one parameter.

### Limit-8 bracket (rita job 1385547, 11 to 12 October)

| H0 part | seed | H0 median [68%] | ln Z | posterior penalised |
|---|---|---|---|---|
| 45 to 140 | 41 | 66.2 [57.6, 73.5] | −679.94 ± 0.21 | 41.8% |
| 45 to 140 | 42 | 67.2 [59.0, 74.5] | −679.49 ± 0.21 | 41.3% |
| 20 to 45 | 31 | 32.5 [31.4, 38.5] | −680.45 ± 0.21 | 55.7% |
| 20 to 45 | 32 | 32.6 [31.5, 41.3] | −680.87 ± 0.22 | 55.6% |

Against limit 4 (`checks4/var8_vs_var4.json`, HENON job 1385556):

- **σ1 runs to its lower bound**: median 0.049, 51% of the combined
  posterior below 0.05 solar masses (1.0% at limit 4); 74% in the lower part.
  This is the declared reading of "heading toward the first attempt's
  collapse".
- Penalised share 41% to 56% (19% to 21% at limit 4).
- Weight of the lower part 0.093 (0.062 to 0.137 over pairings), and its H0
  moves from about 40 to about 32.5, the known low mode.
- Combined H0 65.9 [54.2, 73.3], sd 12.5; shift −0.19 limit-4 sd. The upper
  part is narrower (sd 8.6 against 11.3, 68% width ratio 0.66), which comes
  with the collapse and is not read as information.
- σ2 is unchanged (median 1.9).

**Reading: limit 8 is not usable.** The pile-up at the limit moves with the
limit.

### The stricter side, by reweighting (HENON jobs 1385554 and 1385555; the last slice rerun as 1388950 and 1388951 after a node start-up failure)

Each limit-4 chain reweighted to limits 3 and 2 (`checks4/<chain>/reweight.json`):

| chain | σ1 median at 4 | limit 3: Kish ESS, H0 shift (sd), sd ratio, σ1 | limit 2: Kish ESS, H0 shift (sd), sd ratio, σ1 |
|---|---|---|---|
| high 41 | 0.19 | 56%, +0.00, 1.03, 0.27 | 25%, −0.04, 1.07, 0.38 |
| high 42 | 0.20 | 58%, +0.01, 1.03, 0.29 | 26%, −0.12, 1.06, 0.40 |
| high 43 | 0.20 | 57%, +0.02, 1.04, 0.28 | 26%, −0.03, 1.06, 0.39 |
| high 44 | 0.20 | 57%, +0.00, 1.04, 0.28 | 26%, −0.04, 1.08, 0.39 |
| low 31 | 0.17 | 60%, +0.12, 0.98, 0.26 | 29%, +0.15, 1.02, 0.39 |
| low 32 | 0.17 | 58%, +0.18, 0.97, 0.26 | 29%, +0.22, 1.00, 0.41 |
| low 33 | 0.16 | 56%, +0.12, 0.97, 0.24 | 26%, +0.15, 1.00, 0.38 |
| low 34 | 0.17 | 59%, +0.10, 0.98, 0.25 | 29%, +0.13, 1.00, 0.39 |

- Every reweighting is trusted by its declared rule (Kish ESS ≥ 200 and
  ≥ 5% of the chain's).
- **H0 does not depend on the limit on the stricter side:** shifts at most
  0.22 sd, sd ratios 0.97 to 1.08.
- **σ1 does:** its median follows the limit (about 0.19, 0.27, 0.39 at 4, 3,
  2). The first peak's width is set by the Monte Carlo budget, not measured.

### Owner decision (2026-10-18)

The limit-4 run is the reference full-population spectral result. The
reweighting to limits 3 and 2 is quoted as its stability check, with the
statement that σ1 is set by the limit. Not done here: the DESI target with
the population free (decided separately).

---

## Limit-2 chains (declared 2026-10-18)

Declared at the owner's decision of 2026-10-18, before any limit-2 chain.
Nothing in this section has been run.

### Why

- **The stability check rests on reweighting.** The owner adopted the
  limit-4 run as the reference, with its reweighting to limits 3 and 2 as the
  stability check (above). At limit 2 the reweighting keeps 25% to 29% of
  each chain's samples (Kish effective sample size). It moves H0 by at most
  0.22 limit-4 sd, with sd ratios of 1.00 to 1.08, and it moves σ1's median
  from about 0.19 to about 0.39.
- **Direct chains test the reweighting.** The reweighting is valid in
  principle: a point inside limit 2 is inside limit 4, so the stricter
  target has no mass outside what the limit-4 chains sampled. But it rests
  on a quarter of the samples. It also cannot sample more densely where the
  limit-4 chains were sparse.
- **They keep the charged Jetstream2 H100 busy** while the code of the
  direct DESI chains (12AF, PR #54) is written.

### Setup

- **Variance limit 2** (`numerics.max_likelihood_variance=2.0`). Everything
  else is as in the limit-4 run:
  - the priors table of the second attempt and the 18 dimensions;
  - the smooth cutoff, the cosmology and core e7c3007;
  - dynesty with 1000 live points, dlogz 0.1, walks "scaled" (108 steps) and
    a queue size of 1;
  - the unchanged start check.
- **Inputs as in the limit-4 run:** `A_pe_chieff_bbh259_n4096_v20_exact.h5`
  and `A_sel_chieffref_o3o4ab_v20_exact.h5`, not the LAL-consistent build.
  The comparison with the limit-4 chains and their reweighting is then like
  for like.
- **Two chains per H0 part:** H0 45 to 140 with seeds 41 and 42, H0 20 to 45
  with seeds 31 and 32. They run in the order upper 41, lower 31, upper 42,
  lower 32, followed by their combination by evidence.
- **No new code.** One new manifest, `config/phase12_5_A1_var2_manifest.json`:
  the limit-8 manifest with the limit set to 2.0 and outputs in
  `A1/runs_var2/`.
  - It is committed on `phase12.5/spectral-joint-brackets` (worktree
    `phase12_5/repo_A1b`, now at 0934239).
  - Before the launch, the checkout at the same path on the Jetstream2 H100
    is moved, clean, to that commit.
  - The chain code is that of the limit-8 bracket.

### Expected at limit 2 (from the limit-4 checks)

- **No penalty at the reference population at any H0 from 20 to 140.**
  - The threshold on N_eff is 259²/(2 − v), with v the events' variance
    (0.16 to 0.25 in check 2 of the third attempt).
  - N_eff there is 2.0 (H0 20) to 3.4 (H0 140) times that threshold. The
    smooth penalty is numerically zero above about 1.15 times.
  - Both start points (H0 32.5 and 92.5) pass the start check.
- **The first attempt's spike is rejected.** The events' variance alone is
  6.1 to 9.9 there, above the limit, so no N_eff admits it.
- **Inside the limit:** expected between the 0.2% to 0.3% of the prior
  inside limit 1 and the 3% inside limit 4. The sampler starts on the
  penalty's slope, as at limit 1, where a 7-minute stretch climbed steadily.
- **From the reweighting:** H0 within about 0.2 limit-4 sd of limit 4, an
  sd ratio near 1.05, and σ1's median near 0.39. The posterior is expected
  to press on the limit again, as it did at 4 and 8. Its penalised share is
  not predicted.

### Checks before the launch (HENON CPU, existing commands)

The checks of the limit-8 bracket (HENON job 1385447), with the commands of
`slurm/phase12_5_A1_var8_preflight_henon.sbatch` at limit 2, into
`A1/checks_var2/`. A copy of that launcher with the limit at 2 is the only
change.

- **Control at limit 2** against the stored spectral grids at both rate
  indices: equal to 1e-8 at every H0, and no penalty at the reference
  population at any H0.
- **The first attempt's 400 best points:** penalised at limit 2, and
  reproduced at limit 20 to 1e-9.

**If either fails, nothing is launched.**

### Run plan

- **On the Jetstream2 H100:** one process in a tmux session through
  `/media/volume/datasets/phase12/tools/launch_tmux.sh` (its log ends
  `EXIT=<rc>`), running
  `scripts/phase12t_runner.py --manifest config/phase12_5_A1_var2_manifest.json`.
- **Changed on 2026-10-18, from about 11:22 UTC: the four chains run concurrently on the Jetstream2 H100, settings unchanged** (one tmux session per chain, each the runner's `--only <chain>` stage; upper 41 resumed its 11:22 checkpoint; pause and resume in `A1/runs_var2_PAUSE_RESUME.md`).
- **Queued behind B1.** It starts when B1's Jetstream2 half ends. A shell
  loop on the Jetstream2 machine waits for B1's log there
  (`/media/volume/datasets/phase12/logs/b1_eval.20261018T095315Z.log`) to
  print its `EXIT=` line, then launches. No agent polls it, and B1 and these
  chains never share the GPU.
- **Inputs.** The two GW files are in the Jetstream2 mirror: they were
  copied for B1 and checked by sha256 against Hildafs. The runner checks
  them again against the manifest's checksums.
- **Checkpoint every 30 minutes**, as for every A1 chain.
- **Outputs** are written in the Jetstream2 mirror of `phase12_5/A1/runs_var2/`.
  They are copied back to Hildafs and checked by sha256 at the pause and at
  the end. `A1/runs/` and `A1/runs_var8/` are not touched.
- **Estimated cost.**
  - The limit-4 chains took 5.9 to 6.3 hours *(25 Oct 2026: per-part means; 5.73 to 6.45 hours each)* each on a rita A100 (4.0 to
    4.3 million calls at about 0.006 s).
  - On the Jetstream2 H100, dynesty's single-call path ran at 5.9 ms per
    call (12AF's batching test, from the A1 checkpoint), about the A100's
    rate.
  - That is 6 to 8 hours per chain if limit 2 needs as many iterations as
    limit 4. It may need more, because the allowed region is smaller.
    **About 1 to 1.5 days for the four.**

### Pause and resume

- **Paused** when 12AF's direct DESI chains are ready on the Jetstream2 H100
  (12AF, "What pauses the limit-2 chains"):
  - the process is stopped right after its next checkpoint write, so at most
    30 minutes are lost;
  - the stop and the checkpoint's sha256 are logged;
  - the checkpoint and the finished chains are copied to Hildafs.
- **Resumed later** with the same manifest, from the same commit.
  - A finished chain is skipped, and the unfinished one resumes its
    checkpoint.
  - A resumed chain must match the checkpoint's target, priors, H0 part,
    seed, sampler settings and input hashes; core refuses it otherwise.
  - By default it resumes on the Jetstream2 H100 after the 12AF chains
    there; the owner may decide otherwise.
- **If 12AF's chains are ready before B1's half ends**, the limit-2 chains
  do not start.
- **The combination** uses the chains that have a result (at least one per
  part) and names any chain left out, as for limits 4 and 8.

### What will be compared

Against the limit-4 chains and against their reweighting to limit 2
(`checks4/<chain>/reweight.json`), per chain, per H0 part and combined:

- H0: the median shift and the sd ratio in units of the limit-4 sd, for the
  direct limit-2 chains beside the reweighting;
- σ1 (median, and the fraction below 0.05 solar masses) and σ2;
- the fraction of posterior samples penalised, and N_eff over its threshold
  (quantiles);
- ln Z per chain, and the lower part's weight against limit 4's 0.037 and
  the reweighting's;
- convergence.

### Reading (declared now)

- **The reweighting is confirmed** if the direct limit-2 combined H0 median
  and sd agree with the reweighted ones within twice their combined Monte
  Carlo error.
  - The reweighting's error comes from its bootstrap.
  - The chains' error is the larger of two estimates: a bootstrap of the
    nested samples with each part's ln Z drawn from its error, and half the
    spread between the two matched-pair combinations.
- **"H0 does not depend on the limit on the stricter side" stands** if, in
  addition, the direct limit-2 result falls in 12AB's robust band against
  limit 4: |shift| < 0.2 limit-4 sd and an sd ratio of 0.9 to 1.1.
  - In the mild band it is quoted as a systematic.
  - In the material band the owner decides.
- **σ1 is expected to follow the limit**, as in the reweighting. That is the
  known statement that σ1 is set by the limit, not a failure.
- **Read as a collapse**, as at limit 8, if σ1 or σ2 runs to its lower
  bound. That is not expected at a stricter limit.

### Results (2026-10-18)

The four chains ran concurrently on the Jetstream2 H100 from about 11:22 UTC
and the combination finished at 19:58 UTC. The outputs were copied back to
Hildafs and checked by sha256.

Outputs under `phase12_5/A1/`:

- `runs_var2/`: the chains and their combination;
- `checks_var2/compare/var2_vs_var4.json`: the location-free comparison
  (HENON job 1389633);
- `checks_var2/confirm/confirm_var2.json`: the declared reading below (HENON
  job 1389663), from `scripts/phase12_5_a1_confirm_var2.py` at consumer
  commit 16e0062 on `phase12.5/spectral-joint-var2`. The chains ran at
  5591811 on the same branch.

Statistics are taken on the nested points with their weights. The parts are
combined as for limits 4 and 8: each part's weight is its prior mass times
its evidence, taken from the mean of its seeds' ln Z.

#### The chains

| H0 part | seed | H0 median [68%] | ln Z | posterior penalised | calls | hours |
|---|---|---|---|---|---|---|
| 45 to 140 | 41 | 69.5 [56.1, 82.0] | −683.02 ± 0.21 | 27.1% | 3.94 M | 7.8 |
| 45 to 140 | 42 | 68.6 [56.0, 80.6] | −683.07 ± 0.20 | 26.2% | 4.05 M | 8.6 |
| 20 to 45 | 31 | 41.0 [35.6, 43.9] | −685.05 ± 0.20 | 20.8% | 3.84 M | 8.1 |
| 20 to 45 | 32 | 40.9 [35.3, 43.9] | −684.68 ± 0.20 | 24.4% | 3.82 M | 8.1 |

- **Every chain converged and met its gate.** Each stopped on convergence at
  dlogz 0.1, after 38,600 to 40,700 iterations; limit 4 took 4.0 to 4.3
  million calls. Upper 41 was resumed once from its checkpoint (11:24 UTC).
  The hours are with four chains sharing the GPU.
- **Like for like.** The inputs (by sha256), priors, sampler settings and
  core commit equal those of the eight limit-4 chains. Only the limit
  differs.
- **Combination.** ln Z is −684.86 ± 0.14 for the lower part (its two seeds
  differ by 0.37) and −683.04 ± 0.14 for the upper. The lower part's weight
  is 0.041 (0.034 and 0.050 over the pairings). Limit 4 gives 0.037 and its
  reweighting to limit 2 gives 0.040.
  *(25 Oct 2026: ±0.14 is the propagated reported error; the seeds' standard error is ±0.19 (lower) and ±0.02 (upper). See the errata in "Amendment (25 Oct 2026): independent review", item 3.)*
- **H0 = 68.3 [54.3, 81.0] km/s/Mpc, sd 13.4; 90% [46.1, 89.0].**

#### The reweighting is confirmed

The eight limit-4 chains are reweighted to limit 2 at their nested points.
Each chain's ln Z becomes ln Z₄ plus the log of its mean weight, so each
part's evidence moves with its samples.

| H0 | direct | reweighted | difference | reweighting error | chains' error (a) / (b) | combined error | difference / combined |
|---|---|---|---|---|---|---|---|
| median | 68.34 | 67.34 | +1.00 | 0.18 | 0.19 / **0.57** | 0.60 | 1.67 |
| sd | 13.36 | 13.03 | +0.33 | 0.14 | **0.21** / 0.05 | 0.26 | 1.30 |

- **Confirmed by the declared rule:** both differences are within twice
  their combined error. In limit-4 sd they are +0.08 (median) and +0.03
  (sd).
- **How the errors were computed.**
  - The bootstrap takes 1000 resamples of each chain's nested points. In
    each, every chain's ln Z is drawn from its reported error, and a part's
    ln Z is the mean of its seeds'.
  - The reweighting's error is its bootstrap, with ln Z₄ drawn the same way.
  - (b) is half the spread between the matched pairs 41 + 31 (median 68.89,
    sd 13.43) and 42 + 32 (67.76, 13.32).
  - The chains' error is the larger of (a) and (b), in bold.
- **The median's agreement is marginal, and it depends on the pairing.**
  The other pairing is 41 + 32 (68.60, 13.80) and 42 + 31 (68.07, 12.94). It
  gives (b) = 0.26 for the median and 0.43 for the sd. With it, the median
  differs by 3.1 combined errors and the sd by 0.7.
- **The bootstrap understates the scatter between chains.**
  - Over the four limit-4 seeds of each part, the single-chain H0 medians
    scatter 4.3 to 4.6 times their bootstrap error, and the sds 3.3 to 3.5
    times. The reweighted chains scatter 0.9 to 2.7 times theirs.
  - Outside the declared rule, the reweighting's error can be taken as the
    larger of its bootstrap and the standard error over its four matched
    pairs: 0.23 for the median, 0.34 for the sd.
  - With the declared pairing, the median and sd then differ by 1.6 and 0.8
    combined errors. With the other pairing the median differs by 2.9.
- **Per part.**
  - The lower part agrees: median 40.96 in both, sd 4.37 against 4.35.
  - The difference is in the upper part: median 69.02 against 68.07, and sd
    12.25 against 11.99.
  - There the two direct seeds differ by 0.9 in median, and the four
    reweighted chains span 67.4 to 68.8.
- **Evidence.** The reweighted ln Z at limit 2 is −682.92 for the upper part
  (four seeds, −682.63 to −683.34) and −684.75 for the lower (−684.58 to
  −684.99). The direct chains give −683.04 and −684.86, within 0.12 in each
  part.

#### Against limit 4 (12AB bands)

| | shift (limit-4 sd) | sd ratio | 68% width ratio | band |
|---|---|---|---|---|
| direct, combined | +0.02 ± 0.02 | 1.08 ± 0.02 | 1.07 | robust |
| direct, 45 to 140 | +0.03 ± 0.01 | 1.09 ± 0.01 | 1.07 | robust |
| direct, 20 to 45 | +0.16 ± 0.01 | 1.01 ± 0.01 | 0.92 | robust |
| reweighting, combined | −0.06 ± 0.01 | 1.06 ± 0.004 | 1.06 | robust |

- **"H0 does not depend on the limit on the stricter side" stands.** The
  direct limit-2 result is in the robust band. The errors are the
  bootstrap's, which understate the scatter between chains (see above). The
  combined shift is not resolved.
- **The sd ratio, 1.08, is 0.02 inside the band's edge.** Both matched pairs
  are inside the band: shifts +0.06 and −0.03, ratios 1.088 and 1.079.
- The earlier comparison, on pooled equal-weighted samples, gave +0.02 and
  1.08.

#### Peak widths and the guard

- **σ1 follows the limit, as expected.**
  - Median 0.39 [0.25, 0.57]; the reweighting gives 0.39 and limit 4 0.20.
    Across limits 4, 3 and 2 the median is 0.20, 0.27 (reweighted) and 0.39.
  - Its 1% quantile is 0.13 (limit 4: 0.050). No posterior lies below 0.05
    solar masses (limit 4: 1.0%).
- **σ2.** Median 2.4 [0.86, 6.0]; the reweighting gives 2.35 and limit 4
  1.8. Its 1% quantile is 0.28 (limit 4: 0.13), and 0.01% lies below 0.05
  (limit 4: 0.09%).
- **No collapse.** Neither width runs to its lower bound of 0; both move
  away from it. The comparison's rule raises no flag.
- **The posterior presses on the limit again, as at 4 and 8.**
  - Penalised share: 26% to 27% in the upper part and 21% to 24% in the
    lower. Limit 4 has 19% to 21%, and the reweighting at limit 2 has 22% to
    28%.
  - N_eff over its threshold: 1% quantile 0.996 to 0.999, median 1.32 to
    1.39, 95% quantile 2.11 to 2.25. The reweighting gives a median of 1.30
    to 1.37 and a 95% quantile of 2.10 to 2.25.

#### Reading

- **The reweighting to limit 2 is confirmed** by the declared rule. The
  median's agreement is marginal: 1.7 combined errors, and 3.1 with the
  other pairing. The difference is 1.0 km/s/Mpc, or 0.08 limit-4 sd.
  *(26 Oct 2026: read together with the gap between 12AF's direct chains and 12AD's reweighting, this is one
  unresolved difference between direct chains and reweighting, not seed scatter; "confirmed" holds only with the
  declared pairing (finding C012); see "Amendment (26 Oct 2026): independent review, round 3".)*
- **H0 does not depend on the limit on the stricter side.** The direct
  result is in the robust band against limit 4 (shift +0.02 sd, ratio
  1.08).
- **σ1 is set by the limit** (0.39 at 2). σ2 moves away from 0. There is no
  collapse.
- **Two points on the method, for the owner.** The declared rule requires
  no action.
  - The bootstrap of nested points understates the scatter between chains,
    by up to 4.6 times.
  - With two seeds per part, the matched-pair spread rests on a single
    difference, and its value depends on the pairing.

#### Notes

- **The earlier analyse step ran in float32.** The reweighting's analyse
  step (`phase12_5_a1_guard_reweight.py analyse`, HENON jobs 1385554 and
  1385555) recomputed core's selection correction without core's float64
  runtime, which rounds ln L by about 1e-4.
  - Its weights, Kish ESS and H0 numbers are unaffected: they are reproduced
    here in float64 to 3e-7.
  - Its penalised flags count that rounding as a penalty: about 30% at
    limit 4, against the chains' own 20%. This affects its
    `fraction_penalised` fields and its penalised/unpenalised split.
    Neither is quoted in this record; the penalised shares here come from
    the chains' own guard samples.
  - Here the corrections are float64, and they match the chains' to 2e-13.
  - The first run of this reading (job 1389638) was in float32. It is kept
    in `checks_var2/confirm/smoke/` and differs only in the penalised
    shares.
- No point gains weight at the stricter limit: the largest change in ln L
  is 0. The evaluated nested points hold at least 0.9999 of each chain's
  weight.

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
sha256, in `config/record_envs/12AA.json`; `scripts/check_frozen_environment.py --record 12AA` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AA/<sha7>` on
GitHub (008e780, 3ebc505, cc5fb8e, a611f51, 16e0062). The full test suite is run by `./ci.sh` in the record
environments (CPU, HENON); it was green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and
is green at the final main (above).

**Code of the limit-2 chains (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding G4.1).**
`phase12.5/spectral-joint-var2` (up to 16e0062: the limit-2 manifest, the pre-flight and js2h100 queue launchers and
`scripts/phase12_5_a1_confirm_var2.py`) is merged into the consumer's main (merge e01fb02 on the consolidation
branch); the branch tip is tagged `side-branch/phase12.5/spectral-joint-var2`.

**The guard reweighting's checks (consumer PR #22, merge 84a6b88; code commit 03794e5; finding C117).** The guard
reweighting (`phase12_5_a1_guard_reweight.py`, outputs `A1/checks4/*/reweight.json`) computed its consistency checks
without enforcing them. It skipped the code check on a dirty tree at the chain's own commit and did not record core's
version. From the merge, evaluate refuses any uncommitted change whatever the commit, records core's version and
refuses a core other than the chain's. Analyse stops (exit 4) on a failed check:

- the stored log-likelihood, tolerance 1e-8;
- the recomputed selection correction, tolerance 1e-5 relative (it runs at float32);
- slices that disagree on the limit, the soft guard or the number of events;
- a slice commit whose target files differ from the chain's;
- a slice evaluated with another core.

Re-run on the stored evaluations, all eight chains pass. The stored log-likelihood matches to at most 3.9e-12, the
correction to at most 1.5e-7 relative, and the slice commits 920eade and 0934239 hold the chains' target code
(cc5fb8e). The evaluation files predate the core record; the chains ran with core e7c3007. The `reweight.json` values
are reproduced, apart from 16 values at four chains that differ in the last bit (at most 6e-16 relative). Main's own
script gives the same last-bit differences, both in the record's environment (consumer_e7c3007_cuda12) and in the 12AF
one, so they predate this change. Since evaluate now refuses a core other than the chain's, a rerun of the evaluations
uses the record's environment (core e7c3007); the 12AF environment (core 32c6210) is refused.

**Split-prior combination (consumer PR #31, merge b9ec283; findings C016, C120).** From the merge the split-prior
combination refuses chains that did not run one analysis (one resolved configuration apart from the H0 part and the
seed, one commit, the same inputs, guard, priors and packages, no seed twice in a part, converged) and needs every
listed chain's result (`--allow-missing` keeps the earlier behaviour); the A1, limit-2 and limit-8 manifests now
require all their chains. The compare-limits script checks the chains the same way and files each chain by its
recorded H0 bounds. Rerun on the stored chains of all three variance limits, the combinations give the same pooled
samples bit for bit and the compare-limits output is unchanged apart from the low part's weight at the last binary
digit (a host floating-point effect that main shows identically).

**Unconverged checkpoints (consumer PR #31, merge b9ec283; finding C125).** From the merge a chain driver refuses,
before the build, a dynesty checkpoint whose run has finished without converging (a resume cannot extend it; restart
with `--fresh` and, if the call cap stopped it, a larger `sampler.max_samples`). A finished converged checkpoint
resumes as before, and the smoke chains run with `--allow-unconverged` still resume a finished capped run and write
its result. The production checkpoints of this record all finished converged (checked on disk), so its chains resume
as before.

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

**Writer commit (consumer PR #29, merge 0989df4; finding G4.10).** The summaries behind this record did not carry the
commit of the code that wrote them (the commit is in the job logs and the record). From the merge each summary carries
a `writer` block: the writing script, its checkout's commit, branch and changed-file count, and, where it reads a
short list of files, their sha256 (here, the A1 limit comparison hashes every chain file it reads, each chain's
resolved configuration included). The stored summaries are unchanged; a summary rewritten from main carries the block.

**Runner jobs (consumer PR #30, merge 6d0f800; finding C138).** This record's runner jobs ran from shared clones with
no commit pin. Only 12AE Part 2 mixed commits; this record's runs did not. From the merge the runner job files refuse
to start without PHASE12_EXPECT_SHA naming the commit of a clean checkout, and the stage runner repeats that check
before every stage, stopping (exit 3) if the checkout moves.

**Launch files (consumer PR #30, merge 6d0f800; finding C137).** The launch files of this record predate the owner's
Slurm rules of 18-19 Oct 2026 (7-day limits; rita GPU jobs at 128 CPUs and 120G; holder steps only through the
wrapper) and break them. They are kept unchanged in what they launch, as the record of how the record ran, and from
the merge they refuse to run unless PHASE12_ALLOW_HISTORICAL names them (slurm/historical_launch_files.txt lists
them). The B1 and B2 pipelines' HENON fallback now clears every SLURM_* variable first.

### Errata to the results (consumer PR #23, merge edabeb6; findings G4.2, G4.3, G4.8)

Four corrections to the results above. No number of record changes: the H0 combination, the lower part's weight, the
reweighting's confirmation and the bands stand. The numbers are recomputed from the stored outputs by
`scripts/phase12_5_record_errata.py a1` (consumer commit 9a76252, merged with PR #23), which writes no H0 value.

**1. σ2 is a third parameter whose GWTC-5 value lies outside its 68% interval (limit 4).** "Results (2026-10-18)",
Population, names only σ1 and μ2. The second peak's width σ2 is 1.8 [0.47, 5.1] at limit 4 (pooled samples), and its
GWTC-5 value 5.73 lies outside that interval:

- the exclusion is marginal: 5.73 sits at the 87th percentile, inside the 90% interval [0.24, 8.2]; only σ1 lies
  outside its 90% interval;
- it depends on the limit: at limit 2 σ2 is 2.4 [0.86, 6.0] ("Peak widths and the guard": the direct chains' weighted
  nested points, `checks_var2/confirm/confirm_var2.json`; the pooled equal-weight samples of `runs_var2/combined` give
  2.3 [0.86, 5.9]), which contains 5.73. At limit 2 (pooled samples) the values outside their 68% intervals are σ1's
  and, marginally, σ_chi's (0.10 against 0.111 [0.101, 0.123]); μ2's and σ2's are inside;
- σ2 is the second-strongest H0 correlate in the upper part (r = −0.40, "What sets the width");
- every population-fixed rung (12Y, 12AE and the fixed-calibration ladder 12AG to 12AO) holds σ2 at 5.73: a value
  outside the free fit's 68% interval at limit 4, inside its 90% interval.

At limit 4 the other fourteen parameters' 68% intervals contain their GWTC-5 values.

**2. σ1 belongs among the upper part's H0 correlates.** "What sets the width" lists σ2 −0.40, μ2 −0.38, break mass
−0.32 and γ −0.18 and says every other parameter has |r| ≤ 0.11. σ1 has r = +0.19 (+0.188), larger in size than γ's
(−0.178); the largest of the rest is α2's −0.108, and every other is at most 0.063 in size. The corrected list: σ2
−0.40, μ2 −0.38, break mass −0.32, σ1 +0.19, γ −0.18; every other parameter |r| ≤ 0.11. σ1's correlation runs mostly
through μ1 (corr(μ1, σ1) = −0.37 in the upper part): with μ1 held fixed its partial correlation with H0 is −0.26, and
dropping σ1 from the fit on all 17 parameters lowers the explained share of the H0 variance from 83% (0.826) to 82%
(0.818). σ1 is set by the variance limit; what the limit does to H0 is measured directly by the reweighting to limits
3 and 2 and by the limit-2 chains, so the omission hides no effect on H0.

**3. The two limits quote different ln Z error definitions.** Limit 4's part errors (±0.10 lower part, ±0.16 upper,
"Limit 4: the eight chains", Combination) are the standard error of the four seeds' mean (seed sd 0.20 and 0.32), as
`runs/combined/combined.json` stores them. Limit 2's ±0.14 for both parts ("Results (2026-10-18)" of the limit-2
section, Combination) is the dynesty-reported errors propagated through the mean of the two seeds, √(e₁² + e₂²)/2 =
0.143 and 0.144; no output file stores it. On each definition:

| | lower part (20 to 45) | upper part (45 to 140) |
|---|---|---|
| limit 4, standard error of the seeds' mean (4 seeds) | 0.10 | 0.16 |
| limit 4, reported errors propagated | 0.10 | 0.10 |
| limit 2, standard error of the seeds' mean (2 seeds) | 0.19 | 0.02 |
| limit 2, reported errors propagated | 0.14 | 0.14 |

With two seeds, the seed-scatter error rests on one difference (0.37 in the lower part, 0.045 in the upper). The lower
part's weight and the H0 combination use the ln Z means and the seed pairings, and the confirmation's bootstrap draws
each chain's ln Z from its reported error, as declared, so no number changes.

**4. Two transcriptions.**

- The limit-4 chains sampled for 5.73 to 6.45 hours each (5.75 to 6.47 hours of runner time per stage), not "5.9 to
  6.3 hours": 5.9 and 6.3 are the per-part means (lower part 5.87, upper 6.33 hours of runner time). The same figure
  in the limit-2 section's cost estimate ("The limit-4 chains took 5.9 to 6.3 hours each") is corrected the same way;
  the estimate does not change.
- σ_chi's median at limit 4 is 0.109 (0.1095), not 0.110 (its mean is 0.1099); the interval [0.099, 0.121] is right.

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

### The limit-2 reweighting check and the guard sample's sd (consumer PR #33, merge 901bb54; findings C012, C068)

**The limit-2 reweighting check, restated (finding C012).** The direct limit-2 chains sit above the limit-4 chains
reweighted to limit 2 by +0.08 limit-4 sd in the median, all of it in the upper H0 part (the lower part agrees): 1.7
combined errors with the declared pairing of seeds and 3.1 with the other. This has the sign and about the size of the
gap between the direct DESI chains (12AF) and the reweighted DESI result (12AD) on one target, +0.12 A1 sd, also in
the upper part, about three chain-scatter errors. Read together they are one unresolved difference between direct
chains and reweighting, not seed scatter; "confirmed by the declared rule" holds only with the declared pairing, and
the owner's rule of 20 Oct reads the gap itself instead of a pass mark. The closure checks declared for 12AF and 12AD
(decision 8C) test where the gap comes from; until they have run, the limit-2 comparison is quoted as the direct and
the reweighted values with this gap. The direct limit-2 chains read against limit 4 are not affected by this item.

**The guard sample's sd (finding C068).** The penalised shares of this record (the "posterior penalised" columns and
the penalised-share bullets) are read on 4,000 equal-weighted rows per chain. The binomial sd stored beside them
(`fraction_penalised_binomial_sd` in each chain's result) treats repeated equal-weighted rows as independent; with the
effective size of the nested sample behind the rows the sd is 1.10 to 1.11 times larger at limit 4 and 1.11 to 1.12
times at limit 2 (measured on each chain's guard sample and nested weights). No number of this record quotes that sd.
New chains also write the effective-size-aware sds and, as separate numbers, the fractions below the wall (N_eff under
its threshold: 1.1 to 1.7% of the guard samples at limit 4, 1.1 to 1.6% at limit 2) and within 5% above it (N_eff from
1 to 1.05 times its threshold: 7.3 to 8.6% at limit 4, 8.3 to 10.0% at limit 2).

### GW inputs

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). The O3-support bias acts most on the high-mass slope. A first-order
correction over 800 A1 draws moves alpha2's mean by +0.22 ± 0.01 sd (median +0.20 ± 0.03 sd) and H0's mean by -0.019 ±
0.008 sd (median -0.038 ± 0.016 sd). The resampled events' variance inflation (2.205, 3.066) enters the variance limit
through their per-event variances. In the stored grids those carry under 1% of the PE variance sum; the chains store
none, so the share at the chain's points is not measured.

## Amendment (27 Oct 2026): independent review, final round

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses
below. The amendments of 25 and 26 Oct 2026 above cover the fix packages merged first. This one covers the two that
were still open: resume markers and fingerprints (consumer PR #25, merge 498a147) and the review follow-ups
(consumer PR #35, merge d036f1e), which carry the owner's decisions of 26 Oct 2026 on a delta outside its prior's
bounds and on the manifests' spectral-only note. Both were merged on 27 Oct 2026, after further fix rounds and an
independent check of each. The consumer's main is now d036f1e. Its code is the tree that was tested, #25 and #35 on
main bdf5150 (consumer commit ab9e656): `./ci.sh` passed there in all three record environments (HENON, CPU;
`ci_logs/20261026T213714Z_ab9e6569b881_<env>.log`: consumer_e7c3007_cuda12 1644 passed,
consumer_e7c3007batch_cuda12 1653, consumer_1022429_lss57afebe_cuda12 1668; none failed), and so did the steps of
the GitHub contract job, run without JAX (`ci_logs/20261026T214140Z_ab9e6569b881_contract_job_nojax.log`: 1105
passed, none failed). Location-free throughout. Unless an item says otherwise, no number of record changes.

**Chain resume (consumer PR #25, merge 498a147).** The A1 chain driver (`scripts/phase12_5_spectral_joint.py`) resumed
any checkpoint in its output directory under core's run fingerprint alone, and its `--fresh` left the old checkpoint
in place, as the two DESI chain drivers did (findings C004 and C042, confirmed for those drivers). One chain of this
record was killed and resumed, limit-2's high_seed41 (`runs_var2`): it sampled 3.9 million further calls after its
resume, a real continuation of the same chain. Every other chain of this record ran with `resumed` false in one
session, and no manifest or launcher passes `--fresh`. Since the merge, the A1 driver too stamps a run identity (the
resolved configuration's sha256, the inputs' sha256, the code, the package commits and the backend) beside the
checkpoint and resumes only under it; a checkpoint without a stamp, as every checkpoint of record is, is refused
unless `--adopt-checkpoint` is passed; and `--fresh` moves the old chain aside (to `<out>/superseded-<UTC>/`). Core's
run fingerprint and the recorded `run_fingerprint_digest` are unchanged.

**DONE markers of the manifest runner (consumer PR #25, merge 498a147; finding C073).** The manifest runner treated a
stage's DONE as final without comparing its recorded command or the inputs' checksums. At the reviewed commit every
production run directory's DONE command equalled its manifest's (repository location aside); only smoke directories
held stale DONEs. Since the merge, DONE records the command, the repository and commit, and the sha256 of every
required input, and the runner refuses a DONE whose command or inputs changed and leaves its outputs untouched
(`--rerun-stale` moves the stage aside and reruns it); a DONE written before the change is judged against the
manifest's checksums. A read-only probe of the fixed runner on every production run directory, at the package's
fifth-round head with main 402c947 merged
(`darksirens-core-data/reviews/consumer-2026-10-24/fix/notes/p07-resume/probes/runner_dirs_of_record_37e6f26.json`),
gives the state below; since then the manifests' commands have changed only by the named delta override that consumer
PR #35 adds to two 12U stages already read stale (record 12U).

For this record every stage of the A1, limit-8 and limit-2 manifests (9, 5 and 5 stages) still reads done.

**Misspelt `--set` keys (consumer PR #25, merge 498a147; finding C088).** A misspelt `--set` key outside the sampler
block was accepted, ignored and shown in config.resolved.json. No record path carries one: every `--set` key of the
manifests in config/, of the 12AG and 12AH Part B plan builders and of the shell and Slurm scripts (slurm/,
scripts/*.sh) is a key of the base configuration of the driver it reaches or a key that driver reads (a test of the
consumer checks each of them, command by command). Since the merge, such a key is refused before anything runs.
