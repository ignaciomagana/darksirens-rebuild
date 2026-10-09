# Phase 12AA — P12.5 stage A1: spectral-only chains with H0 and eleven population parameters sampled (declaration)

## Status

**SECOND ATTEMPT DECLARED (owner, 2026-10-09). Read the last section,
"Second attempt", first: it replaces the priors, the number of sampled
parameters and the variance limit given below.** The first attempt was
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
