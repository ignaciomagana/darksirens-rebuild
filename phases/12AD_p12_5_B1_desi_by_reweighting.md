# Phase 12AD — P12.5 stage B1: the DESI H0 with the population free, by importance reweighting (declaration)

## Status

**DECLARED (owner, 2026-10-18) before any run. Low priority.** Nothing in
this record has been run. The method, the control, what is reported and how
it is read are fixed here, before any weight is computed. The code it needs
(below) is written and tested on CPU before any GPU job.

The owner first placed the work on rita. The owner then asked (2026-10-18)
that it use all the GPUs at hand, **the Jetstream2 H100 first**, then the
H100 of the MIKO holder job, then the two rita A100s (see "Compute").

## Where this sits

P12.5 replaces the fixed GWTC-5 population by its uncertainty. The staged
plan (`phase12_5/P12_5_full_scope.md` under darksirens-core-data) reports a
ladder of three rows, each with and without the DESI catalog:

| population | spectral only (the 259 events alone) | DESI union catalog |
|---|---|---|
| fixed (corrected spin, rate index 2.5439) | 66.2 [61.4, 71.1] (12Y amendment) | scans only (corrected-spin union check, 13 H0 values) |
| fixed, rate index free (12Y) | 67.9 [62.7, 73.4], sd 5.40 | 67.6 [62.8, 73.9], sd 5.59 |
| all 17 parameters free (12AA) | 68.0 [55.0, 80.1], sd 12.4 | **this record** |

H0 in km/s/Mpc, median and 68% interval. The bottom right cell is stage B1
of the plan: the DESI catalog with the population free. A direct DESI chain
over all seventeen population parameters would take 13 to 17 GPU-days at
0.23 s per call. B1 gets the same posterior from the A1 chains instead, by
reweighting them from the spectral likelihood to the DESI one.

The proposal is the reference full-population spectral posterior, adopted by
the owner on 2026-10-18: stage A1 at variance limit 4 (12AA, PR #49). In it
the width of H0 is set mostly by the position of the first mass peak, μ1
(correlation -0.85; a linear fit explains 72% of the H0 variance). The
question here is whether the galaxies, which carry redshift information that
does not depend on the source-frame masses, narrow or move that posterior.

## Method

### Proposal

The A1 limit-4 posterior: eight dynesty chains under
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/A1/runs/`,

- H0 45 to 140: `high_seed41` to `high_seed44`;
- H0 20 to 45: `low_seed31` to `low_seed34`;

combined in `runs/combined/` (`combined.json`: each H0 part enters with its
prior mass times its evidence, shared equally among its four seeds). Eighteen
sampled dimensions: H0 and the seventeen GWTC-5 parameters (the rate index
γ; the effective-spin mean and width μ_χ, σ_χ; the broken power law α1, α2
and break mass; the two peaks μ1, σ1, μ2, σ2; the primary low edge and
taper m1_low, δm1; the mixing fractions λ0, λ1; the mass-ratio index β_q;
the secondary low edge and taper m2_low, δm2). Consumer checkout of the
chains: `phase12_5/repo_A1` (limit 4, commit cc5fb8e) and `phase12_5/repo_A1b`
(branch `phase12.5/spectral-joint-brackets`, 0934239).

**Proposal likelihood.** L_proposal is the A1 spectral likelihood,
**recomputed in the same job** with the A1 settings: the A1 PE input
(`phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5`), the injection
set `A_sel_chieffref_o3o4ab_v20_exact.h5`, variance limit 4, the smooth
(soft) selection guard, core e7c3007 with its defaults. At every draw the
recomputed value must equal the chain's stored log-likelihood **to 1e-8;
any mismatch stops the job.**

### Target

The DESI union likelihood at the same H0 and the same seventeen population
parameters, in the 12Y configuration otherwise:

| | target |
|---|---|
| catalog | the standardized union, nside 64 (`phase12u/inputs/catalogs/desi_union_nside64.h5`) |
| completeness | magnitude-limited (Gaussian luminosity function, m_lim 21, k-correction) times the per-pixel footprint fraction of `phase12t/inputs/mth_map_nside128.h5` |
| z_depth | 0.245 |
| δ (host-density evolution) | fixed at 0 |
| kernel pin | off |
| log10 n0 | N(-1.810518, 0.036361) on [-2.346, -1.146] (preset `count_ridge_union_delta0`) |
| M0hat, sigma_M | the configured priors, N(-20.500, 0.199) on [-23, -18] and N(0.557, 0.130) on [0.05, 3.0] |
| injection set | as the proposal |
| variance limit, guard | 4, smooth, as the proposal |
| GW PE input | the LAL-consistent build `phase12t/gwcat_exact/lalcosmo/A_pe_chieff_bbh259_n4096_v20_exact_lalcosmo.h5` (n4096) |
| core | e7c3007 with its defaults |

**Catalog nuisances.** log10 n0, M0hat and sigma_M are drawn from their
priors, **one draw per sample**, with a recorded seed. The weight then
estimates the likelihood marginalized over them without bias, at the cost of
some extra scatter. In 12Y the events did not update any of the three: their
posteriors equalled their priors.

**Why the LAL-consistent PE build in the target.** The owner decided that the
stages after A1 use it. Its measured effect on the spectral H0 is
-0.0006 km/s/Mpc (`phase12_5/lalcosmo_check/grid_comparison.json`), so it
enters the weights at a negligible level. If the build is missing when the
job starts, the A1 input is used for both proposal and target, and the
report says so.

Because the injections, the variance limit and the guard are the same on
both sides, the selection term cancels in the weight except where the two
targets differ.

### Weights, per H0 part

- **Weight** w = L_target / L_proposal at each draw.
- **Within a part,** the normalized weights give that part's posterior.
- **The part's evidence** scales by the mean weight:
  Z_target = Z_proposal × ⟨w⟩, with Z_proposal the part's evidence as
  `combined.json` takes it (ln Z -683.50 ± 0.10 for H0 20 to 45,
  -681.56 ± 0.16 for 45 to 140).
- **Recombination:** the parts are combined with prior mass × Z_target, as
  `combined.json` does with Z_proposal. H0 is flat on 20 to 140, so the
  prior masses are 25/120 and 95/120.

### Draws

**4,096 equal-weight draws per chain, 32,768 in all**, from each chain's
equal-weighted samples, with one common seed recorded in the output. Each
draw keeps the stored log-likelihood of the nested point it repeats, which is
what the 1e-8 check compares with.

### Effective sample size rule

If a part's **Kish effective sample size** ((Σw)² / Σw²) is **below 500**,
a second job evaluates the target at **all nested points of that part's four
chains** (166,146 points for H0 20 to 45, 172,261 for 45 to 140), with the
weights multiplied by each point's nested-sampling posterior weight. The
part is then read from that job. Nothing is guessed from a part below 500.

## Control

**The same command at the fixed population**, with γ free:

- the population at the GWTC-5 values with the corrected spin pair (0.04,
  0.10);
- **proposal:** 4,096 draws of (H0, γ) from the 259-event spectral posterior
  on the γ grids (`phase12_5/spectral_gamma/runs/`; γ flat on [-2, 6] in
  steps of 0.25, the 33 grids without 2.5439; H0 20 to 140 in steps of 0.5).
  The draws sit at grid nodes, so each has a stored log-likelihood, and the
  same 1e-8 recomputation check applies;
- **target:** the 12Y DESI configuration, with the target PE input of the
  main run. The 12Y chain and the grids were made at variance limit 20; the
  control keeps limit 20 on both sides so that it compares like with like;
- **pass:** the reweighted H0 reproduces the 12Y chain
  (`phase12_5/runs/union_gamma/`, H0 67.63 [62.81, 73.87], sd 5.59,
  γ 2.27 ± 0.35): **median within 0.3 km/s/Mpc and sd within 10%**. The
  tolerance covers the Monte Carlo of 4,096 draws and the PE build. **The
  control job exits non-zero if it fails**, and the main result is then not
  read.

## What is reported

Per H0 part and for the combination:

- Kish effective sample size (and as a fraction of the draws);
- H0 median, 68% and 90% intervals, sd;
- γ and μ1 (median and 68% interval);
- the weight of the lower part (H0 20 to 45) before and after the
  reweighting; also, as A1 reported it, its spread over the 16 pairings of
  one seed from each part;
- the largest single weight's share of the total;
- the proposal check: the largest |recomputed − stored| log-likelihood;
- the guard: the fraction of draws penalised by the variance limit under
  each likelihood;
- the catalog nuisances under the weights (n0 values are not blinded).

The before values come from the same draws with unit weights, recombined
with Z_proposal; they are shown beside `combined.json` as a check of the draw
set. The control reports the same items for its single part, beside the 12Y
chain.

## Reading (declared now)

The catalog's effect is read on the **combined** posterior, against A1:

- **Δ = (median_B1 − median_A1) / sd_A1**, the shift of the H0 median in
  units of the A1 sd;
- **R = sd_B1 / sd_A1**, the width ratio.

| band | condition | reading |
|---|---|---|
| robust | \|Δ\| < 0.2 and 0.9 <= R <= 1.1 | the catalog does not change the population-free H0 at this precision |
| mild | 0.2 <= \|Δ\| < 0.5, or R in [0.8, 0.9) or (1.1, 1.25] | the catalog changes it slightly; quoted with the result |
| material | \|Δ\| >= 0.5, or R < 0.8, or R > 1.25 | the catalog changes it; the owner decides what is quoted |

A part read under the ESS rule is read from the second job. A combination
whose control failed is not read.

## Expectation, not threshold

**High effective sample size and no material change.** At the fixed
population, the catalog likelihood equalled the spectral one up to a constant
(within 0.7 in log, 12V to 12X), and with γ free the union moved H0 by
-0.3 km/s/Mpc against spectral-only, with an sd of 5.59 against 5.40 (12Y).
On the A1 scale that is a shift of about -0.02 sd. If the ratio of the two
likelihoods stays constant away from the fixed population, the weights are
flat and B1 equals A1. What would change it is a ratio that varies along the
μ1-H0 direction that sets the A1 width.

## Limits, stated in advance

- **Catalog nuisances from their priors**, one draw per sample: their
  posteriors are not refined, and they add scatter to the weights.
- **δ fixed at 0**, as 12Y. δ and γ are never sampled together.
- **The population-fixed control is the only external check.** There is no
  direct DESI chain with the population free to compare with (stage B2 of the
  plan, not declared).
- **Importance sampling cannot find target mass where the proposal has
  none.** The effective sample size and the largest weight's share are the
  only guard against that.
- **Inherited from A1:** one variance limit; the first peak's width σ1 is
  set by the limit, not measured; the lower part's weight has a seed scatter
  of about a factor of three (0.021 to 0.065).

## Compute

**Work:** 32,768 DESI calls for the main run and 4,096 for the control, at
about 0.23 s per call on an A100 (12Y: 127,829 calls in 8.0 h of sampling):
**about 2.4 GPU-hours of DESI calls, 2.5 to 3 GPU-hours with the proposal
recomputation (about 2 to 6 ms per call) and the build and compilation of
each job.** On two A100s alone, about 1.5 hours of wall time; on all four
GPUs, under an hour once the Jetstream2 machine is set up.

**Slices:** nine independent pieces of about 16 minutes of DESI calls each:
the control, and the 4,096 draws of each of the eight chains. Each slice
writes its own file; the draws and the nuisance draws are fixed by the seed
before any slice runs, so the result does not depend on which GPU ran which
slice.

| GPU | how | takes | state on 2026-10-18 |
|---|---|---|---|
| Jetstream2 H100 80GB (`ssh js2h100`) | priority; inputs copied over (about 0.9 GB: catalog, two PE files, injections, footprint, the A1 sample files; checked by sha256) and a fresh environment of its own at core e7c3007 (no shared env is touched); outputs copied back to `B1/` | the four upper-part chains, after a one-slice timing | reachable, GPU idle; no core e7c3007 environment or inputs there yet |
| MIKO holder job H100 NVL (job 1388940) | a step inside the running job; it sees Hildafs and the consumer environment `phase12t/envs/consumer_e7c3007_cuda12` | the control first, then lower-part chains | GPU idle |
| rita, two A100-80 (Slurm) | account phy220048p, partition RITA-GPU, qos rita, `--gres=gpu:a100-80:1`, 16 CPUs, 64G per job | whatever slices remain; the ESS-rule job if needed | shared; queue behind other jobs |
| HENON (CPU) | after all slices | weights, recombination, summary, the readings | |

**If the ESS rule fires:** about 166,000 to 172,000 DESI calls per part,
about 11 GPU-hours per part at 0.23 s, split the same way.

**Outputs** under `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B1/`:
`draws/` (the draw indices, the nuisance draws and the seed), `slices/` (per
chain: points, stored and recomputed ln L_proposal, ln L_target, the guard
diagnostics of both), `control/`, and one `summary.json`. Under 1 GB.

## Code

On a new consumer branch from `phase12.5/spectral-joint-brackets` (0934239,
which contains the step-1 branch `phase12.5/free-rate-index`):

1. **The DESI target with all seventeen population parameters as
   coordinates.** Today the DESI target can sample only γ: it overwrites the
   γ entry of its population operand at every call
   (`phase12/desi_selection.py`, `PopulationPrior`). This generalizes the
   overwrite to the whole population vector. Tests: at the fixed population
   it equals the existing target bit for bit; with only γ moved it equals the
   step-1 target; with the 12Y inputs and variance limit it reproduces the
   corrected-spin union scan (`phase12_5/checks/e_union_spin_gamma_2.5439/`)
   at its 13 H0 values.
2. **The reweighting command:** `draw` (fixes the draws and nuisance draws by
   seed), `evaluate` (one slice: the proposal check, then the target),
   `analyse` (weights, per-part evidence, recombination, readings), and the
   control as the same command at the fixed population.

CPU tests and a CPU smoke of one small slice before any GPU job.

## Not verified

- The per-call cost of the DESI target with seventeen population
  coordinates: 0.23 s is the γ-only figure (12Y) on an A100. The H100 figure
  is not measured.
- That the generalized target compiles once and does not recompile when the
  population changes.
- The Jetstream2 environment: access and an idle GPU are confirmed; the
  environment and the inputs are not set up.
- Whether the DESI target is penalised by the variance limit at draws where
  the spectral one is not. Reported, not assumed.
