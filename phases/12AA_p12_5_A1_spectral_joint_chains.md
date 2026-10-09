# Phase 12AA — P12.5 stage A1: spectral-only chains with H0 and eleven population parameters sampled (declaration)

## Status

**DECLARED (draft for the owner's review, 2026-10-09) before any chain.**
The implementation, its CPU checks and one 8-minute GPU timing job are done
and recorded below. No production chain has been submitted. The owner reviews
this record, settles the open decisions at its end, and gives the go.

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
| effective-spin mean μ_χ | 0.04 | 0 to 1 (model range) | **every draw above 0.5 penalised** |
| effective-spin width σ_χ | 0.10 | 0.005 to 1 (model range) | **every draw above 0.5 penalised**; half of those below 0.06 |
| mass break | 37.451 | 20 to 50 (model range) | none |
| first slope α1 | 1.4816 | −4 to 12 (model range) | mild: more penalised above 6 |
| second slope α2 | 5.4187 | −4 to 12 (model range) | mild: more penalised below −0.7 |
| first peak position μ1 | 9.9109 | 5 to 20 (model range) | none |
| second peak position μ2 | 32.3273 | 25 to 60 (model range) | none |
| second peak width σ2 | 5.7263 | 0 to 10 (model range) | **half of the draws below 2 penalised** |
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
  prior normalised on its own part. Two seeds per part: four chains.
- The parts are combined by evidence. With a flat prior on 20 to 140, a
  part's prior mass is its width over 120, so the low part's posterior mass
  is 25 Z_low / (25 Z_low + 95 Z_high).
- Each part's ln Z is the mean of its two seeds. The low part's mass is also
  given for all four pairings of one seed per part; their spread is the seed
  scatter.
- Combined samples: each part contributes its posterior mass, shared equally
  between its two seeds.

### Sampler

dynesty only, through core's `ds.infer`: 1000 live points, stop at dlogz 0.1,
random-walk proposals. Checkpoint every 30 minutes.

**Random-walk length (proposed, owner to confirm):** 72 steps per proposal
(core's `dynesty_walks="scaled"`, 6 per parameter). dynesty's own default
would be 32. Core's record of 13-parameter mock runs has ln Z 0.6 to 0.75 low
at the default and correct at 6 per parameter. The parts are combined by
their evidences, so an evidence bias matters here. It costs 2.25 times the
likelihood calls.

## Implementation

Consumer repository `desi_darksirens_selection`, branch
`phase12.5/spectral-joint` at d0b58cb (from `phase12.5/free-rate-index`),
pushed, no pull request.

- `phase12/spectral_joint.py` builds the target. The base stays the fully
  fixed population; every call writes the sampled values into the population
  vector, as step 1 does for γ. One compiled program serves the likelihood
  and its diagnostics, with the events, the injections and the population
  vector as arguments.
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

2000 draws from the priors above, 1000 in each H0 part
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

**The same map with the spin priors narrowed** to μ_χ in 0 to 0.3 and σ_χ in
0.005 to 0.3 (`checks/b_guard_map_spin03_low`, `_high`):

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

**Reading.** The corrected spin values (0.04, 0.10) lie well inside the
unpenalised region, and at the fixed population the selection N_eff is 22 to
37 times its threshold on the whole H0 grid. The guard's cut is far from
where the posterior is expected. It is still a cut on the declared prior,
and the evidences are relative to the declared prior including the cut
volume. Whether to narrow the spin priors is the owner's decision 1 below.

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
- The smoke manifest (the four chains at 40 live points and 1500 calls each,
  then the combination) ran through the stage runner with 0 failed stages.
  Its numbers mean nothing: no chain is converged.

### 4. Unit tests

406 pass on CPU at the branch head d0b58cb (375 before; 31 new).

They include: the target at the fixed values equals the grid stage's
likelihood; each coordinate lands in its own population entry; no call
retraces; a run killed mid-sampling resumes and converges; a checkpoint is
refused for another H0 part, seed or input file; the combination of the
parts reproduces hand-computed weights.

### 5. GPU timing (rita A100-80, job 1376403, 8 minutes)

| | seconds |
|---|---|
| one likelihood call, compiled (300 prior draws per H0 part) | 0.0018 |
| first call, with compilation | 6 |
| one prior transform (core evaluates the triangle map step by step on the GPU) | 0.0037 measured alone |
| **one call inside a running chain, all included** | **0.0038** |

- The last line is the production command itself (H0 45 to 140, 1000 live
  points, 72 steps) run for 407 s and then killed: 108,434 calls. It is the
  figure used below.
- No call after the first retraced or recompiled.
- This is 60 times faster than the 0.23 s per call of the DESI target.
- The progress line of that run showed "logz +/- nan". It is dynesty's
  running estimate, upset by the −∞ points at the start. Recomputed over the
  stored run as dynesty does at the end, the evidence error is finite (0.089
  at that stage); the finished CPU smoke's is finite too.

## What will be reported

For the combined posterior and for each of the four chains:

- H0: median, 68% and 90% intervals, sd. Against the fixed-population
  spectral value 66.2 [61.4, 71.1] and the value with only the rate index
  free, 67.9 [62.7, 73.4]: the shift in km/s/Mpc and the ratio of widths.
- **The posterior mass of H0 below 45**, with its seed scatter (four
  pairings), and whether a separate mode is there: the H0 and first-peak
  position of the low part's posterior.
- Each population parameter's posterior against its GWTC-5 value and
  interval, and against its prior: which are measured, which follow the
  prior, which pile up at an edge.
- The spin pair against (0.04, 0.10), the values now fixed in step 1.
- The correlation of each parameter with H0.
- ln Z of each chain and of the combination, and the two seeds' difference in
  each part.
- Convergence, and the guard: N_eff over threshold at the posterior mean,
  median and best point, and the fraction of posterior samples penalised, per
  chain.

## Expectations, not thresholds

- In the high part, H0 near 66 to 68 with a wider posterior than the
  fixed-population sd of 5.
- The spin posterior near (0.04, 0.10), far narrower than its prior.
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
  `config/phase12_5_A1_manifest.json` in order: H0 45 to 140 seed 41; 20 to
  45 seed 31; 45 to 140 seed 42; 20 to 45 seed 32; then the combination. A
  first complete answer exists after two chains.
- A finished stage is skipped and an unfinished chain resumes its
  checkpoint, so resubmitting the same file continues the run.
- Outputs: `phase12_5/A1/runs/<chain>/result.json`, `samples.npz`, and
  `runs/combined/`.
- **Estimated cost.** The archived 18-parameter split runs needed 49
  iterations per live point. With 35 to 50 here, 1000 live points and 72
  calls per iteration, a chain is 2.5 to 3.6 million calls: **about 3 to 4
  hours per chain, 11 to 15 GPU-hours for the four**, at 0.0038 s per call.
  Treat it as uncertain by a factor of two. With dynesty's default 32 steps
  it would be under half of that.

## Risks

- **The guard as a prior cut.** With the model-range spin priors, 88% of the
  prior volume is cut. If the posterior of any chain touches the cut, the
  guard shapes it. The fraction of posterior samples penalised says so.
- **The low part.** Its preferred region (small fractions at low H0, 12Z) is
  where the one-parameter scans met the guard. If the low mode's weight
  depends on the guard cap, a control at another cap is needed before it is
  quoted.
- **Evidence accuracy.** The low part's mass rests on a difference of two
  ln Z. Two seeds per part give one difference each; a scatter above about
  0.3 means more seeds or more steps before a weight is quoted.
- **More than one mode inside a part.** The split separates H0 below and
  above 45 only.
- **Conditional results.** Six population parameters stay fixed, and the
  cosmology has one free parameter.
- **Not exercised yet:** a chain run to convergence on the real events (the
  smokes are capped); a resume on the GPU (done on CPU only).

## Decisions for the owner before the run

1. **Spin priors.** Keep the model ranges (0 to 1; 0.005 to 1), with 88% of
   the prior cut by the guard; or narrow them to 0 to 0.3 and 0.005 to 0.3,
   where 78% of the prior is unpenalised and the two H0 parts agree (78.0%,
   78.9%). The posterior should not differ; the evidences then refer to a
   prior the guard mostly leaves alone.
2. **Second peak width.** Keep 0 to 10, or raise the lower edge (half of the
   draws below 2 are penalised; the GWTC-5 5% value is 1.9).
3. **Random-walk length.** 72 steps (proposed) or dynesty's default 32.
4. **Seeds.** Two per part as declared. At 3 to 4 hours per chain, four per
   part would cost about a day and give a real scatter.
5. **A guard-cap control** (the scope proposed cap 30 beside cap 20): now, or
   only if a chain's posterior touches the cut.
