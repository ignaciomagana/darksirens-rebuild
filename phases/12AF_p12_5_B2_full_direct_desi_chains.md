# Phase 12AF — P12.5 stage B2: direct DESI chains with H0 and all seventeen GWTC-5 population parameters sampled (declaration)

## Status

**DECLARED (owner, 2026-10-18) before any run.** Nothing in this record has
been run. The target, the priors, the sampler, the checks, what is reported
and how it is read are fixed here, before any chain. The chain code is being
written now. No chain starts until the checks under "Before the chains" have
passed and are recorded here.

While the code is written, the Jetstream2 H100 runs the limit-2 spectral
chains declared in 12AA (PR #49, section "Limit-2 chains (declared
2026-10-18)"). They are paused when these chains are ready; the conditions
are under "What pauses the limit-2 chains".

Results are appended at the end. Absolute H0 values are written there, as in
12Y, 12AA, 12AD and 12AE; none is sent to the clean-room session. This
declaration quotes no H0 value.

**AMENDED (owner, 2026-10-18, 12:50 UTC): the limit-2 filler is not
paused.** The Jetstream2 half of B2 waits until the limit-2 chains have
finished. It then starts on the same GPU. "What pauses the limit-2 chains"
below is superseded and kept as declared. Nothing on MIKO waits.

**LAUNCH PLANNED (recorded 2026-10-18, 13:30 UTC).** The coordinating session
starts it with the commands below. No B2 chain had started when this was
written.

- **Code.** Consumer worktree `phase12_5/repo_B2`, branch
  `phase12.5/direct-desi`, commit 0c9e6d7, clean. The per-GPU pipeline is
  commits 2d8007b and 6f2fb1c.
  - Manifest: `config/phase12_5_B2_full_manifest.json`.
  - Env: `consumer_e7c3007batch_cuda12`.
  - Batched pool at Q = 32 with the likelihood form "rows". Kernel pin
    "auto".
- **Launcher.** `phase12_5/B2/run_b2_h100.sh` is byte-identical to the
  committed `slurm/phase12_5_B2_run_h100.sh` at 0c9e6d7. This was checked
  with cmp at 13:30 UTC.

  ```
  B=/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B2
  $B/run_b2_h100.sh js2h100
  nohup setsid $B/run_b2_h100.sh miko    > $B/logs/run_b2_miko.out 2>&1 < /dev/null &
  nohup setsid $B/run_b2_h100.sh combine > $B/logs/run_b2_combine.out 2>&1 < /dev/null &
  ```

- **The Jetstream2 H100 (`js2h100` mode).**
  - It syncs repo_B2 and the inputs, then checks them: sha256 of every
    input on both sides, the same clean commit, the same batch env.
  - It then starts the tmux session `b2_full` and returns.
  - `b2_full` waits until `VAR2 DONE` appears in the limit-2 combination
    log and no `a1_var2` chain session is left. It then runs upper part
    seed 41, then lower part seed 31.
  - It never touches the limit-2 sessions or their pause file.
  - To start earlier is the owner's call. First stop the limit-2 chains,
    then `ssh js2h100 touch /media/volume/datasets/phase12/b2_full.GO_NOW`.
- **MIKO (`miko` mode).** Upper part seed 42, then lower part seed 32, in
  the holder job. They start at once.
  - B1's MIKO half has finished (B1 DONE at 10:56 UTC), so the GPU is free.
  - The holder job ends on 2026-10-25 at 06:19 UTC. A chain still running
    then resumes from its checkpoint in the next holder job.
- **The combination (`combine` mode).**
  - It waits for both halves.
  - It copies the Jetstream2 chain directories back and checks every file
    by sha256.
  - It then runs the split-prior combination and the comparison with A1
    and B1, and ends with `B2 DONE rc=<rc>`.
  - The status at any time: `$B/run_b2_h100.sh status`.
- **GPU timing (check 6) passed** on the MIKO H100 NVL, for the full target
  with the pin on. At Q = 32:
  - 27.2 ms per point, against the 60 ms limit;
  - 47 ms per point that costs a call, counting the padding of the
    vmapped form;
  - 26 ms per point in the rows form that the chains use.

  This gives about 1 day per chain (1 to 2 days), which is not measured on a
  full run. Records: `B2/checks/gpu_timing/timing.json` and
  `B2/checks/gpu_timing.20261018T130744Z/timing.json`.
- **Not yet in this record:** the results of the other checks under "Before
  the chains". Their outputs are in `B2/checks/`. At 13:28 UTC the unit
  tests at 0c9e6d7 were still running on HENON (jobs 1389593, batch env, and
  1389594, e7c3007 env).

**CHECKS RECORDED (2026-10-18, 14:35 UTC), before any B2 chain.** Checks 1
to 4, 6 and 7 passed; both H0 parts may start. **Check 5 is running; the gate
is pending on it.** See "Results: before the chains" at the end. The code
moved from 0c9e6d7 to the commit named there: one change to the chain
command (it refuses a dynesty other than 2.1.4, as check 1 declares), plus
check scripts, a smoke manifest and tests. The launcher is unchanged.

## Where this sits

P12.5 replaces the fixed GWTC-5 population by its uncertainty. Its ladder
(12AD, 12AE) has three population rows, each with and without the DESI
catalog:

| population | spectral only (the 259 events alone) | DESI union catalog |
|---|---|---|
| fixed (corrected spin, rate index 2.5439) | spectral grid | 12AE Part 1 (rita job 1389044, running) |
| fixed, rate index free | spectral grids (12X, 12Y) | the step-1 chain (12Y) |
| all seventeen free | stage A1, variance limit 4 (12AA) | stage B1 by reweighting (12AD, running); **this record, by direct chains** |

The owner decided on 2026-10-18 that the population-free DESI value, the
bottom right cell, leads (12AE). Stage B1 fills it by importance weights on
the A1 chains. This record fills it a second time, by sampling the same
target directly.

The original plan (`phase12_5/P12_5_full_scope.md` under darksirens-core-data)
ran a direct DESI chain only if B1's effective sample size was poor, and on a
reduced parameter set, at 40 to 75 hours. The owner decided on 2026-10-18 to
run it with **all seventeen parameters free**, whatever B1 gives. Two things
make that affordable: core's catalog kernel pin, and a batched dynesty pool.
Together they bring one DESI likelihood evaluation from 152 ms to 23.6 ms on
the H100 (measured on the step-1 target; sections "Kernel pin" and "The
batched pool").

## Why

- **B1 can fail without saying so.** Importance sampling cannot find target
  mass where the A1 proposal has none. B1's only guards are its effective
  sample size and the share of its largest weight (12AD, "Limits"). B1 also
  draws the catalog nuisances from their priors, one draw per sample, so its
  weights carry their scatter.
- **B2 samples the same target directly**: the same likelihood, the same
  priors on H0 and the population, with the catalog nuisances sampled. If
  the two agree within Monte Carlo error, B1 is confirmed and the result does
  not rest on one method. If they disagree, one of them has failed, and the
  diagnostics below say which is more likely.
- **12AE Part 2** (γ and the first peak's position μ1 free) checks the
  catalog's effect along the one direction that carries most of the A1
  width. B2 frees all seventeen.

## The target

The B1 target (12AD, "Target"), sampled instead of reweighted.

| | B2 (these chains) | B1 target (12AD) |
|---|---|---|
| catalog | the standardized union, nside 64 (`phase12u/inputs/catalogs/desi_union_nside64.h5`) | same |
| completeness | magnitude-limited: Gaussian luminosity function, m_lim 21, k-correction, times the per-pixel footprint fraction of `phase12t/inputs/mth_map_nside128.h5` | same |
| z_depth | 0.245 | same |
| host-density evolution δ | fixed at 0 | same |
| kernel smoothing σ_kde | fixed at 0.003 | same |
| cosmology | flat ΛCDM, Om0 0.3089 (w0 −1, wa 0) | same |
| GW posterior samples | the LAL-consistent build `phase12t/gwcat_exact/lalcosmo/A_pe_chieff_bbh259_n4096_v20_exact_lalcosmo.h5` (259 events, 4096 samples each) | same |
| injections | the O3/O4 set `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | same |
| variance limit, guard | 4, smooth (`selection_neff_soft_guard`) | same |
| catalog kernel pin | **auto** | off |
| catalog nuisances M0hat, sigma_M, log10 n0 | **sampled** | one prior draw per sample |
| population | **seventeen parameters sampled**, A1 priors | A1 posterior draws |
| core | e7c3007 with its defaults | same |
| target code | B1's generalized target (`make_fixed_population_desi_target` with `population_sampled`), consumer branch `phase12.5/desi-reweight` 596651c | same |

**Coordinate**, in order: H0, M0hat, sigma_M, log10n0_q, then the seventeen
population parameters in A1's order (γ, μ_χ, σ_χ, α1, α2, the break mass, μ1,
σ1, μ2, σ2, m1_low, δm1, λ0, λ1, β_q, m2_low, δm2). That is 21 sampled
dimensions. The population operand holds the GWTC-5 values with the
corrected spin pair (0.04, 0.10) as reference values. Every call overwrites
the sampled entries inside the jit, as B1's target does (12AD, "Code",
item 1), so no call retraces.

**The step-1 configuration.** Catalog, completeness, depth, δ = 0 and the
catalog nuisance priors are those of the 12Y chain. Relative to it, the
population is sampled in full, the variance limit is 4 instead of 20, the GW
posterior samples are the LAL-consistent build, and the kernel pin is auto.

### Priors

All flat on the range given unless stated. The population priors are those
of the A1 chains, `config/spectral_joint.json` in `phase12_5/repo_A1b`
(consumer branch `phase12.5/spectral-joint-brackets`, 0934239). A consumer
test compares that file entry by entry with a typed copy of the GWTC-5
paper's ranges (arXiv:2605.27226; 12AA, "Second attempt"). The B2 chain
command reads them from the A1 chain configuration, as B1 does, not from a
copy.

| coordinate | prior | source |
|---|---|---|
| H0 | 20 to 140, run as two parts, 20 to 45 and 45 to 140, each normalised on its own part | owner (A1) |
| M0hat | normal(−20.4997, 0.1987), truncated to [−23, −18] | 12Y (the union's luminosity-function fit) |
| sigma_M | normal(0.5575, 0.1299), truncated to [0.05, 3.0] | 12Y |
| log10 n0 | normal(−1.810518, 0.036361), truncated to [−2.346, −1.146]; sampled through its quantile coordinate log10n0_q, flat on [0, 1] | 12Y, preset `count_ridge_union_delta0` (the union's count ridge at δ = 0) |
| rate index γ | −10 to 10 | paper Table 7 (its κz) |
| effective-spin mean μ_χ | 0 to 1 | Table 8 gives −1 to 1; our model admits 0 to 1 |
| effective-spin width σ_χ | 0.05 to 1 | Table 8 |
| first slope α1 | −4 to 12 | Table 5 |
| second slope α2 | −4 to 12 | Table 5 |
| break mass | 20 to 50 | Table 5 |
| first peak position μ1 | 5 to 20 | Table 5 |
| first peak width σ1 | 0 to 10 | Table 5 |
| second peak position μ2 | 25 to 60 | Table 5 |
| second peak width σ2 | 0 to 10 | Table 5 |
| lower mass edge m1_low | 3 to 10 | Table 5 |
| taper range δm1 | 0 to 10 | Table 5 |
| peak fractions λ0, λ1 | uniform on λ0 + λ1 ≤ 1 (Dirichlet(1, 1, 1), core's cube map onto the triangle) | Table 5 |
| mass-ratio slope β_q | −2 to 7 | Table 5 |
| secondary lower edge m2_low | 3 to m1_low (conditional; core's cube map m2_low = 3 + u (m1_low − 3)) | Table 5 |
| secondary taper range δm2 | 0 to 10 | Table 5 |
| maximum mass | fixed at 300 | Table 5 |

Fixed: δ = 0, σ_kde 0.003, z_depth 0.245, m_lim 21 and the k-correction
coefficients of the 12Y configuration, the cosmology above.

### Split prior, seeds and combination

As A1 and 12AE Part 2:

- **Four chains:** H0 45 to 140 with seeds 41 and 42; H0 20 to 45 with seeds
  31 and 32.
- The parts are combined by evidence: prior mass (25/120 and 95/120) times
  evidence, each part's ln Z the mean of its two seeds' ln Z, each part's
  mass shared equally between its seeds. This uses A1's `combine` command.
- **Seed scatter:** per part, both seeds' ln Z and their difference against
  the errors dynesty reports; the lower part's weight for the two matched
  pairs (first low seed with first high seed, and so on) and for the four
  pairings of one seed per part.

## Sampler

dynesty 2.1.4 (the production environment's), bound "multi", random-walk
proposals, 1000 live points, stop at dlogz 0.1.

- **Walks "scaled"**, core's six steps per sampled dimension, as A1: **126
  steps** here (A1 had 108 in 18 dimensions).
- **Checkpoint every 30 minutes.**
- **Call cap 20 million**, as A1. The DESI configuration's cap of 2 million
  would stop a chain early.
- **Queue size Q = 32 with the batched pool** (next section). A1 and 12Y ran
  with a queue size of 1.

### The batched pool

**What it is.**

- **dynesty's own parallel mode.** With a pool and `queue_size=Q`, dynesty
  fills a queue with Q independent random walks at once. Each walk starts
  from a live point, has its own random seed, and runs under the current
  likelihood threshold. dynesty then uses the queued points in order, and
  accepts a point only if it still beats the threshold when its turn comes. A
  point that no longer does is discarded, and its calls are counted. The
  proposal scale is updated once per queue fill. This is what dynesty does
  with Q worker processes; it is its documented parallel behaviour.
- **The pool** (prototype `phase12_5/batching/batched_rwalk.py`) does not run
  the Q walks one after another. It runs them in lockstep. At each of the 126
  steps every walk proposes with its own generator: the same draws, in the
  same order, as dynesty's own walk function. The proposals that land inside
  the unit cube go to one batched prior transform and one batched likelihood
  call on the GPU. A walk that accepts nothing re-evaluates its start point,
  as dynesty's walk does. The evaluation of the initial live points is
  batched too.
- **The pool changes how the Q walks are computed, not what they are.**

**Why it is equivalent.**

1. **Bitwise equal to dynesty's own queue path wherever the batched
   likelihood is bitwise equal to the single call.** This was measured on the
   Jetstream2 H100 (2026-10-18) with the A1 spectral target: 18 dimensions,
   1000 live points, 108 steps, seed 41, Q = 32. The pool was run against
   dynesty's own `queue_size=32` path with single calls
   (`phase12_5/batching/results/shim_spectral_Q32.json` and
   `shim_spectral_Q32_ckpt.json`):
   - **from a fresh start**, 3,458 unit-cube iterations and then 300
     random-walk iterations: all 3,759 dead points have bitwise-equal ln L
     and identical unit-cube positions;
   - **from the last checkpoint of A1's upper-part chain with seed 41**
     (iteration 41,610, 4.16 million calls, at the end of its random-walk
     phase), switched to Q = 32 and run for 301 iterations: all 301 dead
     points are bitwise equal. Here the pool was **7.0 times faster per
     call** (0.84 ms against 5.9 ms).
2. **On the DESI target a batched call is not bitwise equal to a single
   call.** It differs by at most 1.8e-12 in ln L (relative 2e-15), with the
   pin on or off (section "Kernel pin"). A DESI chain with the pool therefore
   equals dynesty's queue path up to that rounding: an accept or reject
   decision can differ only for a proposal that lies within about 2e-12 of
   the threshold. The batched prior transform equals core's point-by-point
   transform to 1.1e-16 (one unit in the last place).
3. **Against A1's queue size of 1:** Q = 32 gives a different sequence of
   draws from the same sampler, not a different target. Evidence and
   posterior are estimated as with a queue of 1. The cost is the queued
   points that are discarded: 4 of 304 walks (1.3%) in the fresh-start test,
   5 of 306 from the checkpoint. Check 5 below tests this on the real A1
   target, run to convergence.

**What the chain code must do with it.**

- Use the pool for the random-walk sampler only. A map of any other function
  falls back to the builtin map, as in the prototype.
- Refuse a dynesty other than 2.1.4. The pool reproduces that version's walk
  function.
- Keep the pool out of the checkpoint and rebuild it on resume. The
  checkpoint records Q. A resume with another Q, another kernel pin setting
  or pin digest, another configuration or other inputs is refused.
- Compile the batched likelihood for batch sizes 1, 2, 4, 8, 16 and 32. A
  partial batch is padded to the next size with copies of its first point,
  and the padding is discarded, as in the prototype.

### Kernel pin "auto"

**What it is.** Core's catalog kernel pin (darksirens-core #28 and #30). The
catalog kernel quadrature is built once per target, at core's reference H0,
from the compact catalog, the fixed cosmology and the DESI calibration.
Every call then serves the kernel with the scalar shift 3 ln(H0/H0_ref)
instead of redoing the quadrature. Each call re-derives eight probe rows from
the live proposal, and a failed probe makes the likelihood −∞. On the host,
where the target assembles its operands, the pin is checked against the
catalog view by its digest (`check_field_kernel_pin`).

**Why it applies exactly here.** The pin holds whenever none of Om0, w0, wa,
δ and σ_kde is sampled. In B2 none of them is. M0hat, sigma_M and n0 enter
only the completion curves and the missing-host density. The population
parameters do not enter the catalog kernel at all.

**Measured equality** (Jetstream2 H100, 2026-10-18, on the step-1 target:
union, δ = 0, γ sampled, the A1 GW posterior samples, limit 20;
`phase12_5/batching/results/run_desi_vmap_K*_pinauto.json`). 128 points
were used, half prior draws and half near the reference point. Each was
evaluated with the pin on, in batches of 1 to 64, against single calls with
the pin off:

- largest |Δ ln L| **1.8e-12** (relative 2.1e-15); 9.1e-13 at batch size 1;
- 71% to 79% of the values bitwise equal, depending on batch size; **not
  bitwise**;
- all 128 values finite with the pin both on and off.

Core's own test of the pin (darksirens-core #30) finds the same: rtol 1e-12
on synthetic and mock fixtures, at worst 4.1e-13 relative.

**Cost** (same measurement), milliseconds per point:

| points per GPU call | pin off | pin auto |
|---|---|---|
| 1 | 152 (single production call); 154 (batched program) | 27.6 |
| 2 | 113 | 27.0 |
| 4 | 110 | 24.5 |
| 8 | out of memory (one allocation of 78.6 GB) | 24.3 |
| 16 | — | 23.7 |
| **32** | — | **23.6** |
| 64 | 110 to 112 (sequential chunks of 2 or 4) | 24.0 |

- **The pin gives most of the gain**, a factor 5.5 at one point per call.
  Batching adds a factor 1.17 on the likelihood.
- In a chain, batching also removes the point-by-point prior transform of
  core's dynesty adapter: 11 ms per point measured on this target, against
  0.004 to 0.02 ms per point batched (64 and 8 points per call).
- Peak GPU memory with the pin: 28 GB at 32 points per call, 54 GB at 64.

**Owner decision (2026-10-18).** Pin auto is approved: equal to pin off to
1.8e-12, not bitwise. **A checkpoint is never resumed across pin settings.**

- The configuration declares `numerics.kernel_pin` "auto".
- The consumer's Phase 12B acceptance marker (`config/phase12b.accepted.json`)
  admits only "off" today. The B2 chain command admits "auto" for this stage
  on this record and the owner's decision, and does not change the marker
  for the other stages.
- It records the resolved pin (setting, active, the pin's catalog digest)
  and stamps each checkpoint with it, as the P12.4 runner does.

## Inputs

- The union catalog and the footprint map, as above.
- The LAL-consistent GW posterior-sample build (the owner's rule for the
  stages after A1); its measured effect on the spectral H0 at the fixed
  population is −0.0006 km/s/Mpc
  (`phase12_5/lalcosmo_check/grid_comparison.json`).
- The O3/O4 injection set.
- The A1 chain configuration, read for the population priors.
- The chain records the sha256 of every input, as A1 does.
- **On the Jetstream2 H100** these files are already in its mirror and were
  checked by sha256 against Hildafs for B1. That is 22 files, among them the
  catalog, the footprint map, both GW posterior-sample builds and the
  injections. The environment there is identical to the production
  environment (`phase12t/envs/consumer_e7c3007_cuda12`) by `pip freeze` and
  by core's sources (12AD, "Compute").

## Before the chains

All with the committed B2 code. Outputs in
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B2/checks/`.
The results are recorded here before any chain is submitted.

1. **Unit tests (CPU):**
   - on a small spectral fixture, the pool equals dynesty's own queue path
     bit for bit; on the DESI target, to 1e-9 in ln L;
   - the pool refuses any sampler other than the random walk, and any
     dynesty other than 2.1.4;
   - a chain killed mid-sampling resumes from its checkpoint and converges;
   - a resume with another Q, pin setting or pin digest is refused;
   - B1's tests of the generalized target pass.
2. **The pin on the B2 target (GPU).** Pin auto against pin off, at 64 prior
   draws and 64 points near the reference population in each H0 part,
   single and in batches of 32. Pass: largest |Δ ln L| at most 1e-9 and the
   same non-finite pattern. Expected: near 2e-12, as measured on the step-1
   target.
3. **The tie to B1 (GPU).** The B2 target with the pin off is evaluated at
   256 of B1's draws, with B1's nuisance values. Pass: it reproduces B1's
   stored ln L_target to 1e-8 (same code, same inputs). With the pin on, the
   difference is reported.
4. **The start check at limit 4.** The reference population (GWTC-5 values,
   spin 0.04 and 0.10, nuisances at their prior centres) must be free of any
   penalty in the DESI target at the start H0 of each part (32.5 and 92.5).
   For the spectral likelihood this holds at every H0 (12AA); for the DESI
   target it is not checked yet (12AE, "Not verified"). If the low part
   fails, its chains do not start and the owner decides, as in 12AA's second
   attempt.
5. **Control: the batched pool at Q = 32 against A1's queue of 1, on the A1
   target, to convergence.** One spectral chain in the A1 limit-4
   configuration (H0 45 to 140, seed 41, the A1 GW posterior samples), run
   with the pool at Q = 32.
   - **Pass:** ln Z within twice the seed sd of the four A1 upper-part
     chains (0.32) of their mean; the H0 median and sd each within twice the
     seed sd of the same four chains' medians and sds.
   - It takes about an hour on an H100 (A1's 4.2 million calls at 0.84 ms).
     It runs on the MIKO H100 NVL after B1's MIKO half has finished, or on
     the Jetstream2 H100 before the first B2 chain.
   - **If it fails, no B2 chain starts,** and the owner decides.
6. **GPU timing and memory on each H100.** A 10-minute stretch of the real
   chain command (H0 45 to 140, Q = 32) is run in a scratch directory. It
   gives the seconds per call, the points per GPU call and the peak memory.
   The estimate under "Compute" is revised with it before submission.
7. **CPU smoke** of the four-chain manifest and the combination at 8 live
   points.

## What is reported

Per chain, per H0 part and for the combination:

- **H0:** median, 68% and 90% intervals, sd.
- **Every population parameter:** median and 68% interval, against A1 and
  against its prior.
- **The H0–μ1 relation:** correlation and slope, against A1's.
- **The first peak's width σ1:** median and the fraction below 0.05 solar
  masses. A1 found σ1 set by the variance limit (12AA).
- **The catalog nuisances against their priors.** n0 values are not blinded.
- **Evidence:** ln Z of each chain and its error; per part, the difference
  between the seeds; the lower part's weight for the matched pairs and the
  four pairings.
- **The variance limit:** the fraction of posterior samples it penalises,
  and the selection N_eff over its threshold at the posterior mean, median
  and best point.
- **Convergence:** the final dlogz and stop reason, iterations, calls, wall
  time, seconds per call; the fraction of queued walks discarded; the pool's
  record (Q, GPU calls, points per call); the resolved kernel pin and its
  digest.

## Reading (declared now)

### 1. Agreement with B1

B1 and B2 target the same posterior in H0 and the population:

- the same likelihood (pin off in B1 and auto in B2, equal to about 2e-12);
- the same GW inputs and the same priors (B1 through the A1 chains);
- the same catalog nuisance priors: B1 marginalises over them with one prior
  draw per sample, and B2 samples them.

They must agree within Monte Carlo error. On the combined posteriors:

- **The differences:** d_med = median_B2 − median_B1 and
  d_sd = sd_B2 − sd_B1, each also given in units of the A1 sd for scale.
- **B1's Monte Carlo error** comes from a bootstrap of its weighted draws:
  draws resampled within each part, then recombined.
- **B2's Monte Carlo error** is the larger of two estimates. The first is a
  bootstrap of each part's nested samples with their weights, with each
  part's ln Z drawn from its reported error, then recombined. The second is
  half the spread between the two matched-pair combinations.
- **Agreement:** |d_med| and |d_sd| each within twice the combined error,
  the square root of the sum of the two squared errors. The lower part's
  weight is compared and reported with both seed ranges, but not tested:
  with two seeds per part its scatter is measured only coarsely.

| outcome | condition | reading |
|---|---|---|
| agree | both differences within twice the combined error | B1 is confirmed. This record proposes B2, the direct estimate, as the population-free DESI result, with B1 as its check; the owner decides what is quoted |
| disagree | either difference beyond twice the combined error | Reported to the owner with the diagnostics: B1's effective sample size and largest weight share; B2's seed differences, convergence and the control of check 5. Neither is preferred automatically |

### 2. The catalog's effect, against A1

- **Δ = (median_B2 − median_A1) / sd_A1**, the shift of the H0 median in
  units of the A1 sd;
- **R = sd_B2 / sd_A1**, the width ratio, and the same for the 68% widths.

| band | condition | reading |
|---|---|---|
| robust | \|Δ\| < 0.2 and 0.9 <= R <= 1.1 | the catalog does not change the population-free H0 at this precision |
| mild | 0.2 <= \|Δ\| < 0.5, or R in [0.8, 0.9) or (1.1, 1.25] | the catalog changes it slightly; quoted with the result |
| material | \|Δ\| >= 0.5, or R < 0.8, or R > 1.25 | the catalog changes it; the owner decides what is quoted |

- These are the bands of 12AB, as used in 12AD and 12AE.
- A Δ is **resolved** only if it exceeds twice its Monte Carlo error. An
  unresolved Δ is reported with its error and read as "below the precision".
- Shown beside B1's Δ and R (12AD) and 12AE Part 2's.

## Expectations, not thresholds

- **Agreement with B1**, if B1's effective sample size is high. B1 expected
  nearly flat weights (12AD).
- **A robust catalog effect.** At the fixed population the catalog
  likelihood equalled the spectral one up to a constant, within 0.7 in log
  (12V to 12X). With γ free, the union moved H0 by −0.06 spectral sd (12Y).
  The catalog would change the population-free H0 only if the ratio of the
  two likelihoods varied along the μ1–H0 direction that sets the A1 width.
- **μ1 sets the width, as in A1.** σ1 is pressed against the variance limit,
  as in A1.
- **The lower part's weight near A1's (a few percent)**, unless the catalog
  likelihood differs between the two parts.
- **The catalog nuisances follow their priors**, as in 12Y.

## Limits, stated in advance

- **Two seeds per part** (A1 had four): the seed scatter of ln Z and of the
  lower part's weight is measured only coarsely. A1's lower-part weight
  varied by a factor of three over its pairings.
- **One variance limit (4).** In A1, σ1 is set by the limit, not measured.
  The limit-2 chains (12AA amendment) test the stricter side for the
  spectral likelihood only.
- **Q = 32 against a queue of 1:** a different random sequence of the same
  sampler. It is tested once to convergence, on the spectral target
  (check 5).
- **Pin auto is not bitwise equal to pin off.** A checkpoint is never resumed
  across pin settings.
- **A1 and B2 use different GW posterior-sample builds** (the earlier build
  and the LAL-consistent one). The measured effect on the spectral H0 is
  −0.0006 km/s/Mpc at the fixed population.
- **δ is fixed at 0;** δ and γ are never sampled together. The luminosity
  function, m_lim, the depth and the footprint are not varied (12AB varies
  the n0 prior and the depth).
- **The spin model** is a Gaussian in the effective spin, not the GWTC-5
  paper's default (12AA).
- **The cost is unmeasured for the full target** (check 6).

## Compute

| GPU | runs, in order | estimate per chain |
|---|---|---|
| Jetstream2 H100 80GB (`ssh js2h100`; charged) | upper part seed 41, then lower part seed 31 | 1.4 to 1.7 days |
| MIKO holder job, H100 NVL (`srun --jobid=<holder> --overlap -n1`) | upper part seed 42, then lower part seed 32 | 1.6 to 2.0 days |

**The estimate.**

- The owner's figure, about 1.1 days per chain on an H100, is A1's call count
  (4.0 to 4.3 million) at the measured 23.6 ms per call.
- Three things raise it:
  - 126 walk steps instead of 108 (a factor 1.17);
  - the queue's discarded walks (about 1.5%);
  - B1's target is 5% slower per call than the step-1 target on the
    Jetstream2 H100 (0.160 s against 0.152 s single).
- A1 needed 40,100 to 42,800 iterations. The three catalog nuisances follow
  their priors (12Y) and add little information, so 41,000 to 48,000 are
  assumed here. That gives **4.8 to 5.7 million calls per chain at about
  25 ms**.
- The MIKO H100 NVL was 1.18 times slower per DESI call in B1 (0.189 s
  against 0.160 s).
- **Two chains per GPU:** about 3 to 3.5 days on the Jetstream2 H100 and 3.3
  to 4 days on MIKO. This is uncertain by a factor of two and unmeasured for
  the full target; check 6 revises it.
- **The MIKO holder job ends on 2026-10-25 at 06:19 UTC.** The MIKO pair fits
  at the estimate but not at twice it. A chain still running then resumes
  from its checkpoint in the next holder job, with the same Q, kernel pin,
  configuration and inputs.

**How it runs.**

- **Jetstream2:** through `/media/volume/datasets/phase12/tools/launch_tmux.sh`
  (its log ends `EXIT=<rc>`), from a clean checkout of the B2 branch at the
  same path as on Hildafs.
- **MIKO:** as steps inside the holder job.
- One manifest serves both machines, with each machine running its own
  chains. A finished chain is skipped and an unfinished one resumes its
  checkpoint, so a resubmission continues.
- The outputs written on the Jetstream2 H100 land in its mirror. They are
  copied back to Hildafs and checked by sha256, as for B1.
- **Outputs:**
  `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B2/`
  (`runs/<part>_seed<n>/`, `combined/`, `checks/`, `logs/`, `summary.json`).

**Order.**

1. Now, while the code is written: B1 finishes on both H100s. The Jetstream2
   H100 then runs the limit-2 spectral chains (12AA amendment). MIKO runs
   checks 2 to 6 when B1's MIKO half has finished.
2. When the code is committed and pushed, checks 1 to 7 have passed and are
   recorded here, and the manifest has been dry-run on both machines, the
   chains start: upper part seed 41 on the Jetstream2 H100 (after the pause
   below), and upper part seed 42 on MIKO.
3. The combination runs when one chain of each part has finished, and again
   when all four have.

### What pauses the limit-2 chains

The limit-2 spectral chains (12AA amendment) keep the charged Jetstream2 H100
busy while the code is written.

**When:** all three conditions of step 2 above hold. The
B2 chain on that machine is then ready to start.

**How:**

1. The limit-2 process is stopped right after its next checkpoint write. It
   checkpoints every 30 minutes, so at most 30 minutes of sampling are lost.
2. The stop and the checkpoint's sha256 are logged, and the checkpoint is
   copied to Hildafs.
3. B2's upper part, seed 41, starts at once on the same GPU, so the machine
   is not left idle.

**Afterwards:**

- The limit-2 chains resume later from their checkpoints, under the same
  manifest and settings (12AA amendment).
- If B2 is ready before the limit-2 chains have started, they do not start,
  and B2 follows B1's Jetstream2 half directly.
- Nothing on MIKO is paused.

## Code (to be written)

Consumer repository `ignaciomagana/desi_darksirens_selection`, a new branch
from `phase12.5/desi-reweight` (596651c, B1's branch, which contains the A1
code):

1. **The DESI chain command** on B1's generalized target. The sampler is
   built as core's dynesty adapter builds it (bound "multi", random walk, the
   generator seeded from the chain's seed), with the pool and the queue size
   added; core's adapter passes neither. The command has:
   - the seventeen population coordinates with the A1 priors read from the
     A1 chain configuration;
   - the catalog nuisances sampled as in 12Y;
   - `numerics.kernel_pin` "auto", admitted for this stage as above;
   - the H0 part and the seed from the manifest;
   - the result, samples and guard records of A1's chain command.
2. **The batched pool**, from the prototype, with the requirements under
   "The batched pool".
3. **The manifest** of the four chains and their combination, with launchers
   for the Jetstream2 H100 and the MIKO holder job.
4. **The tests and the checks** listed under "Before the chains".

## Not verified

- **Cost and memory** of the 21-dimensional target with pin auto at Q = 32.
  Measured on the step-1 target only.
- **The pin's equality on the B2 target.** Measured on the step-1 target (γ
  only, limit 20, the A1 GW inputs).
- **The pool on the DESI target inside a chain.** Equality with dynesty's
  queue path is shown on the spectral target only.
- **The start in the lower part** at limit 4 for the DESI target.
- **A resumed chain with the pool** is not expected to be bitwise equal to
  the uninterrupted chain, because the queue is refilled on resume. That it
  converges is tested on CPU only.
- **B1's result**, which is not yet available (running).

## Results: before the chains (2026-10-18)

Recorded before any B2 chain started. No H0 value is quoted here.

**Code.**

- Consumer branch `phase12.5/direct-desi`, pushed. The commit in force is
  given under "The gate" below.
- The chain command and the target code are those of fc5792c. Later commits
  change only tests, check scripts and a smoke manifest.
- Env `consumer_e7c3007batch_cuda12`: core 32c6210, the backport of the
  batched pool to e7c3007.
- Likelihood form "rows" at Q = 32, kernel pin "auto".
- Outputs: `phase12_5/B2/checks/` (paths below are relative to `phase12_5/B2/`).

**Two departures from the text above** came out of the checks.

- **The likelihood form is "rows", not the vmapped program.** Core's pool
  hands each batch of proposals to the target. In the rows form each
  distinct proposal is evaluated by the single-point call. Core's padding
  copies are not evaluated again.
  - On this target one point already fills the H100: 26.0 ms alone and
    27.2 ms per point in a vmap of 32. Vmapping saves nothing and pays for
    the padding.
  - In the rows form every value is the single-point value bit for bit. The
    chain is dynesty's own `queue_size=32` chain exactly, not "up to 2e-12"
    as under "Why it is equivalent", item 2.
  - The vmapped form stays available as a setting (`sampler.dynesty_batch_form`
    "pytree"). The form is stamped in the run fingerprint, so a checkpoint
    never resumes under the other form.
- **The point-by-point prior transform costs as much as the likelihood.** On
  this 21-dimensional target it is 25.6 ms per point on the MIKO H100 NVL,
  against the 11 ms measured on the step-1 target. Batched, it is 0.39 ms
  per point (64 points per call).
  - That is most of what the pool gains on this target: on one 6,072-call
    run, the rows form took 111 s, against 177 s for dynesty's own queue
    path with single calls.
  - A chain with a queue of 1 (A1, 12Y, and 12AE Part 2 as declared) pays
    it on every call.

### 1. Unit tests (CPU, HENON) — passed

- **Full suite at 70a0731:**
  - batch env (core 32c6210): job 1389610, 487 passed and 2 skipped;
  - e7c3007 env: job 1389611, 480 passed and 9 skipped (the core-pool tests, which need
    the pool).
- **At 78b84f9** (which adds the kernel-pin resume test), the two direct-chain
  test files: batch env 50 passed (job 1389612); e7c3007 env 39 passed and
  11 skipped (job 1389613). The core-pool tests skip there because that core
  has no pool.
- **The two skips in the batch env are expected.**
  - The frozen-stack gate refuses that env on the darksirens commit, as it
    must. The test asserts exactly that refusal before it skips. The env
    differs from the frozen stack in that one line of `pip freeze`.
  - The test that the frozen core carries the field pin skips whenever the
    installed core is not e7c3007 itself. The pinned-target tests run in
    that env and pass.
- **The declared items:**
  - **The pool equals dynesty's own queue path bit for bit** on the spectral
    fixture, at Q = 4 in the rows form (dead points, samples, ncall, ln Z).
    Core's own tests (`tests/test_dynesty_batched.py`, CI on #69) show the
    same on its fixtures.
  - **On the DESI target**, core's batched form of both targets equals
    single calls to 1e-10 on the synthetic fixture, with the pin on and
    off. On the real target the chain equality is under check 2 below.
  - **Only the random walk, only dynesty 2.1.4.**
    - Core's adapter builds the sampler with `sample="rwalk"` and has no
      option for another sampler. The pool passes any other function to the
      builtin map (core test).
    - The chain command refuses `dynesty_batch` with any dynesty other than
      2.1.4 (new at fc5792c, tested).
  - **A killed chain resumes:**
    - core's test: a resumed batched chain is the uninterrupted chain bit
      for bit;
    - this branch: killed in the middle of a queue fill, then resumed;
    - on the real target, under check 2 below.
  - **A resume is refused** with another Q, unbatched, under the other
    likelihood form, or under another kernel pin setting or pin digest. The
    pin is stamped in the target's provenance, so core's run fingerprint
    refuses the resume. Tested in each case.
  - **B1's tests of the generalized target pass** (in the full suite).

### 2. The pin on the B2 target (MIKO H100 NVL) — passed

**The declared check** (`checks/prechecks.20261018T135727Z/prechecks.json`,
at 78b84f9). The target is the B2 target with pin auto and with pin off.

- **Points.** In each H0 part, 64 prior draws and 64 points near the
  reference population, with the nuisances near their prior centres and H0
  uniform in the part.
- **Evaluated** with pin auto in single calls and in batches of 32 (core's
  vmapped form), and with pin off in single calls.

| H0 part | finite (both pins) | non-finite pattern | largest \|Δ ln L\|, single | largest \|Δ ln L\|, batches of 32 | bitwise equal, single |
|---|---|---|---|---|---|
| 20 to 45 | 107 of 128 | equal | 3.6e-12 | 4.0e-11 | 87 of 128 |
| 45 to 140 | 115 of 128 | equal | 2.3e-13 | 3.6e-12 | 116 of 128 |

All are within 1e-9. The pin's digest is `0a1bcf7a237c01e20405b3695793bb35`
(catalog_digest).

**The pool inside a chain on this target** (`checks/gpu_equality_*`). The
check uses a tiny run of the B2 target:

- upper part, seed 41, 64 live points, 8 walk steps, Q = 32;
- capped at 6,000 calls: 600 iterations, 17 random-walk queue fills.

It is run three ways:

- **A:** core's pool, through `ds.infer(..., dynesty_batch=32)`;
- **B:** dynesty's own `queue_size=32` path, with single calls;
- **C:** A killed in the middle of the sixth random-walk fill, then resumed.

Results:

- **Rows form:** A equals B bit for bit (664 dead points: ln L, unit-cube
  and physical positions, equal-weighted samples, ncall, ln Z). C equals A
  bit for bit on A's 600 iterations.
- **Vmapped form** (at 2b3d086): the same positions and ncall, ln L within
  7.5e-11. C equals A bit for bit.
- **The rows result** above is the rerun from the clean commit:
  `checks/gpu_equality_rows.20261018T141829Z/` at 78b84f9, clean. A first
  rows run from the uncommitted working tree gave the same result.

### 3. The tie to B1 (MIKO H100 NVL) — passed

- **Draws:** 256 of B1's draws, with B1's nuisance values:
  - 128 from the B1 evaluation of the A1 chain `high_seed44`;
  - 128 from `low_seed33`;
  - both evaluated by B1 on the MIKO H100 NVL, at B1's 596651c.
- **Pin off** reproduces B1's stored ln L_target **bit for bit** at all 256
  draws, all finite.
- **Pin auto** differs from B1 by at most 1.3e-10 in ln L. 166 of 256 values
  are bitwise equal.

### 4. The start check at limit 4 — passed in both parts

The reference population at the start H0 of each part, with the nuisances at
their prior centres. Both pins give the same flags.

| H0 part | start H0 | penalised | MC-reliability gate | total MC variance (limit 4) | selection N_eff over its threshold |
|---|---|---|---|---|---|
| 20 to 45 | 32.5 | no | accepted | 1.33 | 3.6 |
| 45 to 140 | 92.5 | no | accepted | 0.82 | 5.9 |

- **The lower part starts.** This was listed as not verified (12AE).
- The anchor gates of the GPU smoke and of the CPU smoke (check 7) find the
  same at both H0 values.

### 5. Control: Q = 32 against A1's queue of 1 — passed

- **Started** 2026-10-18 at 13:41 UTC on the MIKO H100 NVL, in the holder job
  1388940.
- **Configuration:** the A1 chain configuration (`config/spectral_joint.json`,
  limit 4 with the smooth guard), H0 45 to 140, seed 41, 1000 live points,
  walks scaled (108), the A1 GW posterior samples. The input sha256 is
  checked against A1's record.
- **Sampler:** core's pool at Q = 32 in the rows form, env
  `consumer_e7c3007batch_cuda12`, at fc5792c.
- **Script:** `checks/check5/run_check5.sh`, byte-identical to the committed
  `slurm/phase12_5_B2_check5_miko.sh`. Log: `logs/check5.20261018T134128Z.log`.
- **Progress:** 1.5 million calls at 14:18 UTC, in the random-walk phase.
- **The pass rule** is the declared one: ln Z, the H0 median and the H0 sd
  each within twice the seed sd (ddof 1) of A1's four upper-part chains, from
  their mean. It is applied by the script. The script also requires the same
  inputs and a converged chain.
- **The verdict** goes to `checks/check5/result.json`, and the log ends
  `CHECK5 DONE pass=<true|false>`.
- **If it fails, no B2 chain starts,** and the owner decides.
- **Result (2026-10-18, 15:33 UTC): PASSED** (`checks/check5/result.json`).
  The chain converged (stop reason "convergence", final dlogz 0.09998 against
  0.1) on the same inputs as A1 (sha256 checked). It took 4.25 million calls
  (A1's four: 4.16 to 4.28 million), 41,902 iterations and 6,672 s of
  sampling, partly while sharing the GPU with checks 2, 3 and 6. The pool
  ran 1,050 unit-cube and 1,220 random-walk queue fills, and its startup
  probe matched single calls bit for bit at all 32 points. Against the four
  A1 upper-part chains, in units of their seed sd (limit 2):

  | quantity | difference from the A1 mean, in seed sd |
  |---|---|
  | ln Z | +0.82 (+0.27 in ln Z) |
  | H0 median | +0.36 |
  | H0 sd | +0.51 |

### 6. GPU timing and memory — MIKO measured; Jetstream2 at the start of its chain

**MIKO H100 NVL**, a 10-minute stretch of the real chain command
(`checks/check6/timing_stretch.json`):

- Stage `high_seed41`, in a scratch directory, at 70a0731.
- **It shared the GPU with check 5** (a spectral chain, 1.1 GB, which keeps
  the GPU busy), so the timing is an upper bound.
- **Setup:** 192 s to the start of the sampling loop. That covers the build,
  the anchor, the preflight and the 1,000 initial live points.
- **The stretch:** 606 s, 13,661 calls, **44 ms per call**. The whole stretch
  was in dynesty's first, unit-cube phase. There every call is evaluated, one
  point per GPU call in the rows form.
- **Memory:** the chain process held 17.8 GB of GPU memory, and the GPU 18.9
  GB in all.

**Unshared figures** from the same day, on the same GPU:

- **26.0 ms** per single call, and **27.2 ms** per point in a vmap of 32
  (`checks/gpu_timing*/timing.json`). The vmap of 64 runs out of memory.
- **In the tiny chain of check 2** (rows form): 25.9 ms per evaluated point
  in the random-walk queue, and 18 ms per dynesty call. Calls outside the
  unit cube cost nothing.

**The estimate under "Compute", revised:**

- 4.8 to 5.7 million calls at 18 to 27 ms per call gives **1.0 to 1.8 days
  per chain**, on an H100 that is not shared.
- A MIKO pair takes 2 to 3.6 days. The holder job ends 2026-10-25 at 06:19
  UTC.
- On a shared GPU the cost rises toward 44 ms per call. **No other GPU work
  should run on MIKO with the B2 chains.** Check 5 ends before they start.

**Jetstream2 H100: a scheduling deviation.** Its GPU is fully used by the four
limit-2 chains (12AA), which are not to be disturbed (owner, 12:50 UTC).

- Its 10-minute figure will therefore come from the first 10 minutes of its
  production chain (`runs/high_seed41/stage.log`, and the samples the
  launcher's log carries). It is not measured before the start.
- The prototype measured 23.6 ms per point there on the step-1 target.
- **Measured (2026-10-18), production chain `high_seed41`, unshared:** the
  four limit-2 chains were combined at 19:58 UTC. The chain started at 19:59
  and began sampling at 20:01:14, after the build and the anchor. Over its
  first 695 s of sampling it made 21,672 calls, all in the unit-cube phase:
  **32 ms per call**. The GPU showed 87% use, and the chain process held
  17.2 GB.
- **For comparison, MIKO's production chain `high_seed42`** (unshared since
  check 5 ended) made 1.03 million calls in its first 4.5 hours of sampling,
  through the random-walk phase. That is 15.8 ms per dynesty call on average;
  calls outside the unit cube cost nothing.
- **Prior transform:** both production chains report "prior transform form
  eager". On these GPUs the compiled transform does not reproduce the eager
  one bit for bit, so the pinned values come from the eager, point-by-point
  path. That is the declared behaviour of the pin. The measured rates above
  already include it.
- **The estimate stands** at 1.0 to 1.8 days per chain.

### 7. CPU smoke at 8 live points — passed

- **Manifest:** `config/phase12_5_B2_full_manifest.smoke_cpu8.json`, the
  production manifest capped: 8 live points, 48 calls, walks 2, Q = 4 in the
  rows form.
- **Run:** on HENON with `--cpu` at 70a0731.
  - The four chains ran in parallel: jobs 1389605 to 1389608, 13 to 14
    minutes each.
  - Then the combination and the comparison: job 1389609.
  - All exit 0. Outputs in `smoke_runs_cpu8/`.
- **Each chain** passed its anchor at the midpoint of its part, ran core's
  pool and wrote its result.
- **At 8 live points** the chains stay in the unit-cube phase. The
  random-walk queue is exercised by the GPU smoke at 24 live points instead
  (`smoke_runs_gpu/`, at 2b3d086: 38 to 79 random-walk queue fills per
  chain, all four chains and the combination exit 0).

### The gate

- `phase12_5/B2/checks/gate_pre5.json`: checks 1 to 4, 6 and 7 pass, and
  both H0 parts are allowed. Commit in force: 78b84f9 (78b84f91564fdf7a1082bbfadd27f2de9396c928).
- **The launch also needs check 5's pass.** The coordinating session watches
  for `CHECK5 DONE pass=true`. If check 5 fails, no B2 chain starts.
- **Check 5 passed at 15:33 UTC, so the gate is open** for both H0 parts.
  The coordinating session starts the launcher after this entry is pushed:
  MIKO at once, and Jetstream2 when the limit-2 chains have been combined.

## Results: the chains (2026-10-21)

All four chains converged (convergence "verified", the start check met): MIKO H100 NVL ran both seeds of the lower part
and seed 42 of the upper; Jetstream2 ran seed 41 of the upper part (and its lower seed 31 copy; files copied back,
identical by sha256). Combined at 2026-10-21 10:39 UTC (, ),
commit 78b84f9, 40,000 pooled samples.

**H0 (absolute; owner page only, never to the clean-room):**

| | median | 68% | 90% | sd |
|---|---|---|---|---|
| **B2, DESI, all 17 population parameters sampled (direct)** | **70.4** | **[54.7, 81.3]** | [44.6, 87.1] | 13.1 |
| B1, the same posterior by reweighting A1 (12AD) | 69.0 | [53.9, 80.4] | | 12.7 |
| A1, spectral only, population sampled (12AA) | 68.0 | [55.2, 79.9] | | 12.4 |

Per chain: upper part seeds 41 and 42: 70.8 [56.9, 81.4] and 71.8 [59.0, 81.8] (ln Z −682.19 ± 0.20 and −682.12 ± 0.20);
lower part seeds 31 and 32: 40.3 [36.8, 43.7] and 40.2 [36.8, 43.7] (ln Z −683.87 ± 0.20 and −683.53 ± 0.20).
Fraction of samples the variance limit penalises: 0.178 to 0.191.

**The lower part's weight:** 0.047 and 0.060 for the two matched pairs (B1 after reweighting: 0.042, range 0.024 to
0.073 over its pairings; A1: 0.037).

**1. Against B1** (the owner's rule of 2026-10-20 replaces the declared bootstrap test and bands: differences are
reported as they are): d_med = +1.46 (+0.11 B1 sd, +0.12 A1 sd), d_sd = +0.35 (width ratio 1.03). The two upper-part
seeds differ by 1.0 in their medians, so the difference is of the size of B2's own seed scatter. μ1 and γ agree: μ1
10.01 [9.64, 10.34] against B1's 10.04 [9.67, 10.37]; γ 2.47 [2.03, 2.93] against 2.45 [2.00, 2.92].

**2. The catalog's effect, against A1:** Δ = (median_B2 − median_A1) / sd_A1 = +0.20; R = sd_B2 / sd_A1 = 1.06; 68%
widths 26.7 against 24.7 (ratio 1.08). B1's were +0.08 and 1.03 (12AD).

**Every sampled parameter** (median [68%]; B1 and A1 shown where their summaries carry the parameter):

| parameter | B2 direct (median [68%]) | B1 reweighted | A1 spectral (proposal) |
|---|---|---|---|
| H0 | 70.4 [54.7, 81.3] | 69 [53.9, 80.4] | 68 [55.2, 79.9] |
| M0hat | -20.5 [-20.7, -20.3] | — | — |
| alpha1 | 1.7 [1.03, 2.23] | — | — |
| alpha2 | 5.2 [4.26, 6.21] | — | — |
| beta_q | 1.23 [0.707, 1.8] | — | — |
| delta_m1 | 3.28 [1, 6.31] | — | — |
| delta_m2 | 4.66 [1.97, 6.71] | — | — |
| gamma | 2.47 [2.03, 2.93] | 2.45 [2, 2.92] | 2.41 [1.97, 2.88] |
| lambda0 | 0.404 [0.296, 0.523] | — | — |
| lambda1 | 0.552 [0.434, 0.66] | — | — |
| lambda2 | 0.0402 [0.0262, 0.0581] | — | — |
| log10n0_q | 0.525 [0.179, 0.848] | — | — |
| m1_low | 4.37 [3.44, 5.47] | — | — |
| m2_low | 3.44 [3.09, 4.19] | — | — |
| m_break | 37.7 [29.5, 45.1] | — | — |
| mu1 | 10 [9.64, 10.3] | 10 [9.67, 10.4] | 10 [9.7, 10.3] |
| mu2 | 34 [32.6, 35.6] | — | — |
| mu_chi | 0.0355 [0.0247, 0.0459] | — | — |
| sigma1 | 0.243 [0.121, 0.47] | — | — |
| sigma2 | 1.63 [0.418, 4.78] | — | — |
| sigma_M | 0.558 [0.435, 0.686] | — | — |
| sigma_chi | 0.11 [0.0993, 0.121] | — | — |

σ1 sits at 0.24 [0.12, 0.47], pressed toward the variance limit as in A1. The catalog nuisances (M0hat, σ_M,
log10 n0) are reported above; their priors are in "The target".

**Not done here:** B2's Monte Carlo error by the declared bootstrap (superseded by the owner's rule); the H0–μ1
correlation and slope; the selection N_eff at the posterior points. They can be computed from the chains on request.
