# Phase 12AD — P12.5 stage B1: the DESI H0 with the population free, by importance reweighting (declaration)

## Status

**DONE (2026-10-18): results below, read robust.** The population-free DESI H0 by reweighting moves by +0.08 sd from the spectral value, width ratio 1.04; control passed. The text that follows is the declaration as written before any run.

**DECLARED (owner, 2026-10-18) before any run. Low priority.** Nothing in
this record has been run. The method, the control, what is reported and how
it is read are fixed here, before any weight is computed. The code it needs
(below) is written and tested on CPU before any GPU job.

**Compute changed (owner, 2026-10-18), before any production run.** B1 runs
on the **two H100s**: the Jetstream2 H100 (`js2h100`) and the H100 NVL of the
MIKO holder job. It does not run on rita. Both H100s were idle, and this
result decides whether a multi-day direct DESI chain with the population
free is needed, so it runs now and fast. The Jetstream2 machine is charged
in real compute, so it starts at once and is kept busy; the Vera GPUs cost
allocation units only. (The owner first put the work on rita, then on all
four GPUs; see "Compute".) The CPU checks and an 8-draw smoke of the whole
pipeline have run. They are code checks, not results.

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

**Work:** 32,768 DESI calls for the main run and 4,096 for the control, each
beside a recomputation of the spectral likelihood. Measured on the B1 target
itself in the smoke (2026-10-18): one DESI call takes **0.160 s on the
Jetstream2 H100 and 0.189 s on the MIKO H100 NVL**; the proposal
recomputation takes 6 and 10 ms; the first call, with compilation, 73 and
98 s. In all, about 1.8 GPU-hours of DESI calls.

**Plan (owner, 2026-10-18): the two H100s; rita is not used.**

| GPU | runs | about |
|---|---|---|
| Jetstream2 H100 80GB (`ssh js2h100`; charged) | starts first, at once, detached: five chains, `high_seed41`, `high_seed42`, `high_seed43`, `low_seed31`, `low_seed32`, 4,096 draws each, in one process | 60 minutes |
| MIKO holder job H100 NVL (steps inside the running job, `srun --overlap`) | the control (4,096 draws), then three chains, `high_seed44`, `low_seed33`, `low_seed34` | 15 + 45 minutes |
| MIKO CPU (HENON when there is no holder job) | the summary, after both | seconds |

The chains are split five and three, not four and four. The Jetstream2 H100
is faster per DESI call, and the MIKO GPU also runs the control. With this
split both finish together, in about an hour of wall time, and the charged
machine is not left waiting. It starts beside the control, not after it. The
control decides whether the main result is read, not whether it is computed
(see "Control"). A failed control stops the MIKO side at once; the Jetstream2
half finishes and its outputs are kept.

The draws and the nuisance draws are fixed by the seed (20261018) and the
chain, so the result does not depend on which GPU evaluated which chain. The
smoke checked this: one chain evaluated on each GPU gave bitwise-identical
likelihoods.

**The Jetstream2 copy.** The machine sees the Hildafs paths through a symlink
to its own mirror. Before the launch, these were copied there and checked by
sha256 on both sides: the union catalog, the footprint map, the A1 and the
LAL-consistent PE builds, the injection set, the 12Y chain's result and
configuration, and the result, configuration and sample files of its five
chains. That is 22 files and no checkpoints. The environment there is a copy
at the same path. It is identical by `pip freeze` and by the sources of core
e7c3007. The code is this branch's worktree at the same clean commit.

**Pipeline.** One script runs it all, and it is safe to rerun:
`phase12_5/B1/run_b1_h100.sh production`, a copy of
`slurm/phase12_5_B1_run_h100.sh` on the consumer branch
`phase12.5/desi-reweight`. It copies and checks the inputs, starts the
Jetstream2 half, then runs the control and the MIKO half. It checks the
Jetstream2 log by ssh every 5 minutes, copies the outputs back (checked by
sha256) and writes the summary. It never starts the ESS-rule job:
`summary/ess_flag.json` names any part below 500. Its last line is
`B1 DONE rc=<rc> summary=<path>`.

**Smoke (2026-10-18; code check, not a result).** The whole pipeline ran at 8
draws per chain with a 64-draw control, under `B1/smoke/`, once with a four
and four split and once with this one. The second run was interrupted during
the control and rerun, and it picked up the running Jetstream2 half. Every
recomputed proposal value matched its stored one within 1.4e-12. The
proposal's part weights equalled `combined.json`'s exactly. The two runs gave
identical summaries. The control's tolerance is not tested at 64 draws.

**If the ESS rule fires:** 166,000 to 172,000 DESI calls per part, about 7.5
to 9 GPU-hours per part on these H100s, split between the two by slices.

**Outputs** under `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B1/`:
`control/` (`control.json`, `control.npz`); `evals/`, one file per chain (the
points, the stored and recomputed ln L_proposal, ln L_target, the nuisance
draws, both guards' diagnostics, the seconds per call, and a record of the
seeds, draw digest, configurations, inputs and code); `summary/`
(`summary.json`, `summary.npz`, `ess_flag.json`); and `logs/`. Under 1 GB.

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

Checked since, on 2026-10-18 (see "Compute"): the per-call cost on both
H100s; that only the first call compiles (later chains' first calls take
0.2 s); and the Jetstream2 environment and inputs. The last item below
stands.

- The per-call cost of the DESI target with seventeen population
  coordinates: 0.23 s is the γ-only figure (12Y) on an A100. The H100 figure
  is not measured.
- That the generalized target compiles once and does not recompile when the
  population changes.
- The Jetstream2 environment: access and an idle GPU are confirmed; the
  environment and the inputs are not set up.
- Whether the DESI target is penalised by the variance limit at draws where
  the spectral one is not. Reported, not assumed.

---

## Results (2026-10-18)

Pipeline `phase12_5/B1/run_b1_h100.sh production` on the two H100s (control and three chains on miko, five chains on js2h100),
09:53 to 10:56 UTC. Outputs `phase12_5/B1/control/` and `phase12_5/B1/summary/summary.json`.

**Control (fixed population, γ free):** reweighted spectral draws give H0 67.50, sd 5.54, against the 12Y DESI chain's 67.63,
sd 5.59: a difference of −0.13 with a Monte Carlo error of 0.22, sd ratio 0.99, Kish ESS 3,501 of 4,096, largest weight share
0.16%, nothing penalised. Pass.

**Main run:** 4,096 draws per chain, 32,768 in all. The recomputed proposal likelihood matches every stored chain value
(largest difference 3e-12). Kish ESS 8,506 in the lower part and 10,898 in the upper, 11,850 combined; largest weight share 0.07%;
no part needed the nested-point extension.

| | spectral (A1 proposal) | DESI, population free | shift | width ratio |
|---|---|---|---|---|
| H0 combined | 68.0 [55.2, 79.9], sd 12.31 | **69.0 [53.9, 80.4], sd 12.75** | +1.0 (+0.08 sd) | 1.04 |
| H0, upper part | 68.6 [56.6, 80.1] | 69.8 [56.4, 80.7] | | |
| H0, lower part | 40.3 [34.4, 43.7] | 40.3 [36.9, 43.7] | | |
| lower part's weight | 3.65% | 4.22% (2.4% to 7.3% over seed pairings) | | |
| γ | 2.41 ± 0.47 | 2.45 ± 0.47 | | |
| μ1 | 10.05 ± 0.35 | 10.04 ± 0.37 | | |

**Reading: robust.** The catalog moves the population-free H0 by 0.08 sd and widens it by 4%.

**Where the +1.0 comes from:** with the DESI likelihood but the spectral target's guard penalty in place of its own (a diagnostic,
not the declared result), the median is 67.9 [53.2, 80.0]. Most of the shift therefore comes from the DESI target's guard at limit 4,
which penalises more draws than the spectral one does, not from the galaxies.
