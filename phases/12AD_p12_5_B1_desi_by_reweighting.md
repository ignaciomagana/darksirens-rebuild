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
sha256, in `config/record_envs/12AD.json`; `scripts/check_frozen_environment.py --record 12AD` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AD/<sha7>` on
GitHub (cc5fb8e). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was green at the
follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**What the reweighting reports, and the control's rule (consumer PR #22, merge 84a6b88; code commit 03794e5).**
Numbers from the review's probes, run in the record's environment consumer_e7c3007_cuda12 (this record's summary
rebuilt from its stored evaluations; the control's verdict from its stored draws).

1. **Reference of the reading (G4.5).** The declaration reads the catalog's effect against A1's combination of record
   (Delta = (median_B1 - median_A1)/sd_A1, R = sd_B1/sd_A1). The results table divided instead by the before-weights
   resample of the A1 chains (the B1 draws with unit weights, recombined). Against A1's combination the shift is
   +0.081 sd and R = 1.027 (1.03, not 1.04); against the matched resample they are +0.082 sd and 1.035. The two A1 sds
   differ by 0.8% (resample over combination 0.992), about 1.5 times the resampling error of the two sds: Monte Carlo
   of two resamples of the same chains. The matched ratio is a fair estimator, but not the declared one. The reading
   does not change. From the merge the summary reports both, labelled (`combined.reading.against_a1_combination` and
   `against_matched_resample`).
2. **Catalog nuisances under the weights (C115, G4.5).** Declared as reported, they were not. On the combined
   posterior they barely move: the medians shift by -0.010 (M0hat), +0.005 (sigma_M) and -0.014 (log10 n0 quantile) of
   their prior sd, and their sds change by -0.7%, -0.1% and -1.3%. From the merge the summary (per part and combined)
   and the control report them, with the physical log10 n0.
3. **Effective sample size (C119).** The Kish ESS counts the 4,096 rows per chain as independent draws, but the rows
   repeat nested points (14,450 and 14,567 distinct points of 16,384 per part). With the weights summed per distinct
   point the Kish ESS is 6,818 in the lower part and 9,035 in the upper (reported 8,506 and 10,898), and 9,823
   combined (reported 11,850). The effective size lies between the two counts, since a repeated row still carries its
   own nuisance draw. Both are far above the minimum of 500; the reading is unchanged. From the merge the summary
   reports both.
4. **The control's median rule (C116, G4.4).** The control's draws sit on the grid's H0 nodes, 0.5 apart, and the
   declared rule compared their midpoint-rule median, which is a node value, with the 12Y median within 0.3. One node
   lay in that window, so Monte Carlo alone decided the verdict about a quarter of the time (23-26% of bootstrap
   resamples of the stored draws fail), and the sentence "The tolerance covers the Monte Carlo of 4,096 draws" does
   not hold. The recorded median difference (-0.023 of the 12Y sd) is mostly that quantization. With each node's
   weight spread over its H0 cell, the interpolated median differs from the 12Y median by +0.006 of the 12Y sd. Its
   bootstrap error is 0.021 sd and the 12Y chain's own error of its median 0.015 sd (0.026 sd combined). From the
   merge the control's default rule (owner's default, 25 Oct 2026) is |interpolated median - 12Y median| within three
   combined Monte Carlo errors (here 0.077 sd), with the sd within 10% as before. On the stored control draws it
   passes, the difference being 0.08 of the tolerance. The rule as it ran stays available (`--median-rule node`) and
   is reported beside it. The control passed as recorded under its declared rule, and the main result is unaffected.
5. **The declared low-ESS extension (C041).** The rule "a part with Kish ESS below 500 is extended to every nested
   point of its chains" could not have run on the A1 chains. Each chain stores 226 to 287 initial points at dynesty's
   -1e300 stand-in for minus infinity, and some other zero-weight points match their stored value only to about 1e-7.
   Both fail the 1e-8 stored-value check, so the command stopped before any DESI call. The rule did not fire (both
   parts far above 500). From the merge the nested draw set holds only points of positive weight (37,575 to 40,067 per
   chain; the 3,548 to 3,769 zero-weight points carry no proposal weight). These match their stored values: on
   low_seed32, 12 rows including the six of lowest stored ln L match to 5e-13.
6. **Code only, no number of record changes (C114).** The importance weights are now stabilised over the points with
   proposal weight (in log q + log w). B1's equal-weight path is unchanged bit for bit. The stored summary is
   reproduced: every value of `summary.json` and every array of `summary.npz` is equal bit for bit, and only keys are
   added. The control's stored verdict, differences and bootstrap errors are reproduced bit for bit under the rule as
   it ran.

A unit test that compared an expression with itself now tests evaluate's slicing: the slices put together are the
whole draw set, nuisance draws included (C118).

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
short list of files, their sha256 (here, B1's summary hashes every evaluation file). The stored summaries are
unchanged; a summary rewritten from main carries the block.

**Launch files (consumer PR #30, merge 6d0f800; finding C137).** The launch files of this record predate the owner's
Slurm rules of 18-19 Oct 2026 (7-day limits; rita GPU jobs at 128 CPUs and 120G; holder steps only through the
wrapper) and break them. They are kept unchanged in what they launch, as the record of how the record ran, and from
the merge they refuse to run unless PHASE12_ALLOW_HISTORICAL names them (slurm/historical_launch_files.txt lists
them). The B1 and B2 pipelines' HENON fallback now clears every SLURM_* variable first.
*(27 Oct 2026: as run it did not, and this record's runs never started it; see "Amendment (27 Oct 2026): independent
review, final round".)*

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

### The catalog's effect at a common guard, and the gap to the direct chains (consumer PR #33, merge 901bb54; owner decisions 6B, 8C)

**At a common guard (finding C001).** Beside the declared result (+0.08 of the spectral sd) and the record's
diagnostic (the DESI likelihood with the spectral target's guard: -0.007 sd), the third reading is the spectral
likelihood with only the DESI target's guard penalty, no galaxy term: +0.076 sd, 93% of the declared shift. The
catalog's shift is the DESI guard's, as this record already says; at a common guard the galaxies move the
population-free H0 by -0.007 sd (both readings at the spectral target's guard) or +0.006 sd (both at the DESI target's
guard: the declared +0.082 against +0.076). The B1 summary now writes this third reading
(`diagnostic_spectral_with_the_desi_guard`, with its shift and the declared shift in the proposal's sd); rerun on this
record's evaluations it gives +0.0758 against the declared +0.0819, and every declared number of this record's summary
is unchanged (bit for bit).

**The direct chains (12AF) on the same target (finding C012).** They sit +0.12 A1 sd above this result (upper part
+0.129 A1 sd, 2.8 to 3.2 chain-scatter errors). The gap is unresolved; until the closure checks of decision 8C have
run, the population-free DESI result is quoted as both values with this gap, not as either alone.

**Without any guard (finding C001; decision 6B).** The fourth reading takes both guards off: the DESI likelihood
without its guard against the spectral likelihood without its own, both reweighted from A1's draws. Rerun on this
record's evaluations, the galaxies move the population-free H0 by -0.018 sd of the guard-free spectral posterior, with
sd ratio 1.04 (68% width ratio 1.08, 90% 1.03), the width set mostly by a larger low-H0 weight (ratio 1.28). Per part,
in each part's own sd: -0.074 in the lower part (sd ratio 0.78) and -0.002 in the upper part (1.03). The DESI guard
walls off 23% of the guard-free DESI posterior (30% of the lower part, 23% of the upper), the spectral guard 2.4% of
the guard-free spectral one; the guard-free DESI reweighting keeps a Kish ESS of about 2,900 of the 32,768 draws. A1's
draws stop at the spectral wall, so mass beyond it is missing from both. The B1 summary now writes this reading
(`diagnostic_guard_free`, with `catalog_effect` and per-point weights); every declared number of the summary is
unchanged (bit for bit). None of the three readings beside the declared one carries an estimator error yet. On the
merged code the B1 summary rerun on this record's evaluations reproduces every value of the stored summary.json and
every array of summary.npz exactly, and gives these readings to the last digit.

### Catalog model and GW inputs

**Catalog model (consumer PR #24, merge 402c947; findings C002, C091, C003, G3.1, C018, G2.1, G2.3, G2.4, G3.3,
G3.2).** Three properties of the catalog model behind this result were found by the review; their H0 effect is not
measured. (1) The catalog's absolute-magnitude floor is in no selection model (C002), and with m_lim 21 the Gaussian
luminosity function makes the union at least 99.7% complete to z_depth, so the sampled M0hat and sigma_M are inert and
the completeness is f_p alone (C091). (2) The footprint fraction is not the catalog's coverage: masked sources stay in
the catalog while f_p removes them (galaxies per unit f_p are 19, 5 and 2 times the median at f_p < 0.05, 0.05-0.2 and
0.2-0.5 at nside 128; C003), and covered sky without r-band or photo-z is read as voids and underdensities (G3.1,
C018); about 5% of PE samples sit in hole pixels. (3) The photometric kernel counts the volume prior twice (G2.1).
Smaller: 2.3% of rows are galaxies DESI measured above 0.30 (G2.3); spectroscopic redshifts are heliocentric (coherent
H0 effect about -0.12%, G2.4); about 5.8k rows under medium-bright-star masks are spurious halo fragments (G3.3); the
photo-z retention rule loses 0.84% of hosts averaged over the window (0.04% to 1.45%, rising with z), about one eighth
of the n0 prior width, with no completeness model (G3.2). The owner's decisions (1C: the hosts are the galaxies above
the floor, complete below the depth; 2A: a footprint built from the catalog's own construction, with the bright-star
mask veto BRIGHT and MEDIUM, maskbits 2050, chosen on 26 Oct; 3B: a re-centred photometric kernel) define catalog
version 2, which the merge adds as opt-in code: no record path changes. Its sizing step, one fixed-calibration H0 grid
pair at the fiducial cell, measures the effect before any chain is rerun; it waits for the owner's go. The
large-galaxy mask is not vetoed: it marks the low-redshift hosts themselves (in a smoke on about 1% of the rows it
removed 93% of the rows at z 0.02-0.03 against a footprint share of 7%).

**n0 window (consumer PR #24, merge 402c947; finding C020).** At delta fixed at 0 the n0 prior centre is matched over
[0.02, 0.30], but the likelihood uses the catalog only to z_depth 0.245; matching within the depth moves the centre by
-0.028 dex (0.78 prior sd). Record 12AB measured the in-depth centre (H0 shifts 0.000, -0.082 and -0.099 posterior sd
in its three parts, inside its declared band). `phase12u_calibrate.py --ridge-z-max 0.245` now gives the in-depth
ridge; the default window is unchanged.

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). No number of this record changes.

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

**The HENON fallback of the B1 and B2 pipelines (consumer PR #35, merge d036f1e; finding C137).** The launch-file
paragraph of the 25 Oct amendment says that this fallback now clears every SLURM_* variable first. As run it did not:
had the fallback started inside another allocation, its srun would have joined that allocation. In this record's runs
it never started (it runs only when no holder job runs, and every CPU step went to the holder): its caller here, B1's
summarize step, logged `host=miko job=1388940` (`phase12_5/B1/logs/summarize.20261018T095259Z.log`), and no pipeline,
summarize or combine log of B1 or B2 names HENON (HENON appears only in separately submitted check, test and smoke
jobs). So this record is not affected. A test of the clearing came with consumer PR #35.
