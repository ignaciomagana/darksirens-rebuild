# Phase 12AE — P12.5: the ladder cell (DESI, population and rate index fixed) and direct DESI chains with γ and μ1 free (declaration)

## Status

**DECLARED (owner, 2026-10-18) before any run.** Nothing in this record has
been run. The configurations, inputs, controls, what is reported and how it
is read are fixed here, before any chain.

- **Part 1 runs now:** one DESI chain on a rita A100, with the population
  and the rate index fixed.
- **Part 2 runs later,** by a separate job, once the DESI target that takes
  population parameters other than γ as coordinates is committed by the
  stage B1 work (12AD, consumer branch `phase12.5/desi-reweight`, worktree
  `phase12_5/repo_B1`; uncommitted on 2026-10-18).

Results are appended under each part. Absolute H0 values are written here, as
in 12Y, 12AA and 12AD; none is sent to the clean-room session.

**AMENDED (owner, 2026-10-18), before any Part 2 chain: Part 2's DESI chains
use kernel pin "auto"** (equal to pin off to 1.8e-12 in ln L, not bitwise; a
checkpoint is never resumed across pin settings). Everything else in Part 2
is as declared. Part 1 keeps pin off and is running (rita job 1389044).
**Part 2 runs on the two rita A100s, queued behind job 1389044 and the 12AB
north/south GPU job 1389048.** See "Part 2 amendment (2026-10-18)" at the
end of Part 2.

**Part 2 SUBMITTED (2026-10-18, 13:28 UTC) on rita**, from the consumer
worktree `phase12_5/repo_B2` (branch `phase12.5/direct-desi`, commit
0c9e6d7, clean), manifest `config/phase12_5_12AE_gamma_mu1_manifest.json`,
env `consumer_e7c3007_cuda12` (core e7c3007), outputs in
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/gamma_mu1/`.

| rita job | what | dependency | runs, in order | state at 13:29 UTC |
|---|---|---|---|---|
| 1389599 | A100 number 1 | `afterany:1389044` (Part 1) | spectral upper 41, spectral lower 31, DESI upper 41, DESI lower 31 | pending, waits for 1389044 |
| 1389600 | A100 number 2 | none | spectral upper 42, spectral lower 32, DESI upper 42, DESI lower 32 | running on rita (started 13:28 UTC) |
| 1389601 | HENON CPU | `afterok:1389599:1389600` | both members' combinations, then the summary (Δ and R, B1 beside) | pending, waits for both |

- Each GPU job: account phy220048p, partition RITA-GPU, qos rita, one
  a100-80, 16 CPUs, 64G, 7 days, through the shared
  `slurm/phase12_5_12AE_gamma_mu1_rita.sbatch`. Logs in
  `gamma_mu1/logs/`.
- Two changes from the amendment's table, in scheduling only:
  - Each job runs its spectral chains first, then its DESI chains. This is
    the manifest order.
  - The second job has no dependency. Job 1389048 finished at 10:40 UTC
    and has left the controller, so a dependency on it would be refused.
    The second A100 was free.
- Chains, settings and inputs are as declared and amended: kernel pin auto
  for the DESI chains, no batching, limit 4 with the smooth guard, and the
  LAL-consistent PE.
- **The jobs run from the repo_B2 working tree.** Job 1389599 reads it when
  it starts, after Part 1. Each job logs the commit it ran.

**PART 1 DONE (2026-10-18, 14:53 UTC): robust.** The ladder cell gives H0
66.1 [61.7, 71.7] against the spectral 66.2 [61.4, 71.2], so Δ = −0.01 and
R = 1.01. The control passed bit for bit. See "Results (2026-10-18)" at the
end of Part 1. Job 1389599 started after it, as queued.

## Where this sits

P12.5 reports a ladder of three population rows, each with and without the
DESI catalog:

| population | spectral only (the 259 events alone) | DESI union catalog |
|---|---|---|
| fixed: corrected spin (0.04, 0.10), rate index γ = 2.5439 | 66.17 [61.45, 71.15], sd 4.89 | **Part 1 of this record** (today only the corrected-spin union scans, 13 H0 values at a fixed calibration) |
| fixed, γ free (12Y) | 67.95 [62.7, 73.4], sd 5.40 | 67.63 [62.81, 73.87], sd 5.59 |
| all 17 parameters free (12AA, variance limit 4) | 68.0 [55.0, 80.1], sd 12.4 | stage B1 (12AD, PR #52) |

H0 in km/s/Mpc, median and 68% interval. The spectral γ-fixed value is the
grid `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json`; the
DESI γ-free value is the step-1 chain `phase12_5/runs/union_gamma/`.

**The owner decided (2026-10-18) that the population-free DESI value, the
bottom right cell, leads.** The two fixed-population rows are shown as
results conditional on the population. Part 1 fills the one empty cell of
those rows.

**Part 2 is an independent check of B1** on the parameter that sets the
width of the population-free H0. In the A1 posterior, H0 follows the
position of the first mass peak, μ1: correlation −0.85, a slope of
−30 km/s/Mpc per solar mass, and 72% of the H0 variance explained (12AA
results). The reason is the spectral-siren measurement itself: the detector
sees masses redshifted by (1 + z), so placing the peak higher in the source
frame means a lower redshift at the measured distance, and a lower H0. The
galaxies carry redshift information that does not go through the masses. If
the catalog changes the population-free H0, it has to do so along μ1. B1
reads that through importance weights on the A1 chains; Part 2 reads it
directly, with DESI chains that sample μ1 and γ, beside spectral chains with
the same freedom.

## Part 1 — the ladder cell: DESI, population and rate index fixed

### Configuration

The 12Y chain with one change: **γ is not sampled.** The override
`population.sampled.gamma=[-2.0,6.0]` is dropped, and γ stays at the fixed
population's 2.5439. Everything else is identical to 12Y (manifest
`config/phase12_5_step1_manifest.json`, consumer `phase12.5/free-rate-index`
0d75b40, in `phase12_5/repo`):

| | 12Y chain | this chain |
|---|---|---|
| γ | sampled, flat on [−2, 6] | **fixed at 2.5439** |
| catalog | the standardized union, nside 64 (`phase12u/inputs/catalogs/desi_union_nside64.h5`) | same |
| completeness | Gaussian luminosity function, m_lim 21, k-correction, times the per-pixel footprint fraction (`phase12t/inputs/mth_map_nside128.h5`) | same |
| z_depth | 0.245 | same |
| δ (host-density evolution) | fixed at 0 | same |
| log10 n0 | N(−1.810518, 0.036361) on [−2.346, −1.146] (`count_ridge_union_delta0`) | same |
| M0hat, sigma_M | N(−20.500, 0.199), N(0.557, 0.130) | same |
| spin pair | fixed at 0.04, 0.10 | same |
| other 14 population parameters | GWTC-5 values | same |
| GW PE | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | same |
| injections | the O3/O4 set `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | same |
| variance limit, guard | 20, smooth | same |
| core | e7c3007 with its defaults, kernel pin off | same |
| sampler | dynesty, nlive 1000, dlogz 0.1, seed 22; the start H0 from the 12T spectral grid | same |

**Sampled: H0, M0hat, sigma_M, log10n0_q** (n0 through the quantile of its
prior), four parameters. H0 flat on 20 to 140.

### Why these inputs

The cell must be comparable with its two neighbours: the spectral γ-fixed
grid in its row and the DESI γ-free chain in its column. Both use the PE
build above, the same injections and variance limit 20. **The
LAL-consistent PE build is not used here.** Its measured effect on the
spectral H0 at this population is −0.0006 km/s/Mpc (66.1742 against
66.1748; ln L differences at most 0.002 over H0 20 to 140,
`phase12_5/lalcosmo_check/grid_comparison.json`), far below anything this
cell can resolve. Using it would give one cell of the fixed-population rows
different inputs from its neighbours for no measurable gain.

### One chain

At the fixed population the H0 posterior has one mode. The spectral γ-fixed
grid has 8e-7 of its mass below H0 = 45, and its highest log-likelihood
there is 11.4 below the peak; the 12Y chain's samples run from 49 to 94. The
low-H0 mode near 32 to 40 appears only with the mass parameters free (12AA).
So one chain with one seed, without the split prior.

### Before the chain

1. **CPU smoke** of both stages (the H0 scan, then the chain at nlive 8)
   with the smoke twin of the manifest, as for 12Y: one short HENON task.
2. **Control: the same likelihood as 12Y at γ = 2.5439.** The chain's scan
   stage (H0 at the anchor calibration) reproduces the 12Y scan stage
   (`phase12_5/runs/scan_union_gamma/scan.json`, made with γ sampled and held
   at 2.5439) at all 12 of its H0 values to 1e-6 in ln L, and the
   corrected-spin union check (`phase12_5/checks/e_union_spin_gamma_2.5439/`)
   at the H0 values they share. The two targets are the same likelihood at
   that γ (12Y unit tests: bit for bit). A failed control means the chain is
   not read.

### What is reported

- H0: median, 68% and 90% intervals, sd.
- **Against the spectral γ-fixed grid (its row neighbour):**
  Δ = (median − 66.17) / 4.89 and R = sd / 4.89, read with the bands of
  Part 2 below.
- **Against the DESI γ-free chain (its column neighbour):** the difference
  of medians and the sd ratio, beside the same two numbers for the spectral
  pair (+1.8 km/s/Mpc, 5.40 / 4.89).
- ln Z against the 12Y chain's −658.845 ± 0.078: the evidence for a free γ
  with the catalog, beside the spectral −1.2 to −1.8.
- The calibration parameters against their priors.
- Convergence, the gate, the guard (selection N_eff over threshold at the
  posterior mean and median), the scan's rejected points.

### Compute and outputs

- **One rita A100:** account phy220048p, partition RITA-GPU, qos rita (it
  preempts the scavenger rita-s jobs; the owner's usual priority),
  `--gres=gpu:a100-80:1`, 16 CPUs, 64G. The runner checkpoints every 30
  minutes.
- **About 6 to 8 hours.** 12Y took 8.0 h of sampling (127,829 calls) with
  five sampled parameters; this chain has four.
- **Code:** no change to the target. A new manifest and its smoke twin on a
  consumer branch `phase12.5/ladder-cell` from 0d75b40: the step-1 manifest
  with the γ override removed from both stages and new output paths.
- **Outputs:** `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/ladder_cell/`
  (`scan_union_fixed/`, `union_fixed/`).

### Results (2026-10-18): the ladder cell is robust

rita job 1389044, 09:53 to 14:53 UTC (5.0 h), consumer branch
`phase12.5/ladder-cell` (worktree `phase12_5/repo_12AE`), env
`consumer_e7c3007_cuda12`, kernel pin off, seed 22. Outputs in
`phase12_5/ladder_cell/runs/` (`scan_union_fixed_pop/`, `union_fixed_pop/`).

**Control: passed, bit for bit.** The chain's scan stage reproduces the 12Y
scan stage (`phase12_5/runs/scan_union_gamma/scan.json`) at all 12 of its H0
values with a difference of exactly 0 in ln L (declared tolerance 1e-6). It
also reproduces the corrected-spin union check
(`phase12_5/checks/e_union_spin_gamma_2.5439/scan.json`) at the 3 H0 values
they share, again exactly. The anchor matches the step-1 target at γ =
2.5439 bit for bit (`ladder_cell/checks/anchor_equality.json`). The scan
rejected no point.

**H0: 66.1 [61.7, 71.7] km/s/Mpc** (median and 68%), 90% [58.6, 74.9], sd
4.95, mean 66.5.

| comparison | value | reading |
|---|---|---|
| against the spectral γ-fixed grid (66.17, sd 4.89): Δ, R | Δ = −0.01, R = 1.01 | **robust** |
| against the DESI γ-free chain (12Y, 67.63, sd 5.59): γ free minus γ fixed | +1.5 km/s/Mpc, sd ratio 1.13 | beside the spectral pair's +1.8 and 1.10 |
| ln Z: 12Y (γ free) minus this chain (γ fixed) | −658.845 − (−656.916) = **−1.93 ± 0.10** | beside the spectral −1.2 to −1.8 |

- **The catalog does not change H0 with the population and γ fixed either.**
  This fills the last cell of the ladder: Δ is −0.01 here, against +0.08 for
  B1 with everything free (12AD). Both are in the robust band.
- **Freeing γ moves H0 by about the same with and without the catalog**
  (+1.5 and +1.8), and widens it by about the same (1.13 and 1.10).
- **The evidence prefers the fixed γ by 1.9 in ln Z** with the catalog, as
  without it. That is the Occam factor of a free γ whose GWTC-5 value is
  within the posterior.
- **Calibration nuisances:** M0hat −20.50 ± 0.20, σ_M 0.56 ± 0.13, log10 n0
  −1.822 ± 0.034. The prior on log10 n0 is centred at −1.8105 with sd 0.036,
  so the posterior is the prior shifted by −0.3 of its sd and 0.95 times as
  wide. The catalog does not constrain n0 at this depth, as in 12Y.
- **Guard and gate:** unpenalised at the posterior mean and median, with
  selection N_eff 26.6 times its threshold and total MC variance 0.95 (limit
  20). Gate 7 is met.
- **Convergence:** stop reason "convergence", final dlogz 0.09999986 against
  0.1, ln Z −656.916 ± 0.059, 5,372 iterations, 78,946 calls, 17,836 s of
  sampling.

## Part 2 — direct DESI chains with γ and μ1 free

### Configuration

**Two population parameters free, the rest fixed** at the corrected GWTC-5
values (the spin pair 0.04, 0.10; the other thirteen as the fixed
population, e.g. the first peak's width σ1 at 0.78).

| | DESI chains | spectral chains |
|---|---|---|
| sampled | H0, γ, μ1, M0hat, sigma_M, log10n0_q (six) | H0, γ, μ1 (three) |
| γ prior | flat on −10 to 10 (GWTC-5 paper, Table 7; as A1) | same |
| μ1 prior | flat on 5 to 20 solar masses (GWTC-5 paper, Table 5; as A1) | same |
| H0 prior | flat on 20 to 140, run as two parts, 20 to 45 and 45 to 140 | same |
| seeds | 41, 42 (45 to 140); 31, 32 (20 to 45): four chains | the same four |
| catalog | the Part 1 / 12Y configuration (union, footprint, z_depth 0.245, δ 0, the n0, M0hat and sigma_M priors) | none |
| GW PE | the LAL-consistent build `phase12t/gwcat_exact/lalcosmo/A_pe_chieff_bbh259_n4096_v20_exact_lalcosmo.h5` | same |
| injections | the O3/O4 set `A_sel_chieffref_o3o4ab_v20_exact.h5` | same |
| variance limit, guard | 4, smooth (as A1) | same |
| sampler | dynesty, 1000 live points, dlogz 0.1 (as A1 and 12Y) | same |
| core | e7c3007 with its defaults; **kernel pin auto** (amended 2026-10-18; first declared off) | e7c3007 with its defaults (no catalog, so no kernel pin) |

The seed numbers follow A1's convention (its limit-8 bracket used these
four); the owner set two seeds per part. The two members of each pair use
the same sampler settings.

### Why these choices

- **γ and μ1.** μ1 carries most of the population-free H0 width (above). γ
  is the rate evolution, which the catalog's host-density evolution
  duplicated before δ was fixed (12V to 12Y). Together they are the two
  directions in which a catalog effect is most likely.
- **The paper's ranges**, as A1, so the freedom matches the reference
  full-population run.
- **The split H0 prior.** With μ1 free the low-H0 mode can return: in A1 the
  lower part sits at μ1 ≈ 10.8 and H0 ≈ 40, with weight 0.037. A single
  chain over 20 to 140 can misweight such a mode by a factor of two to three.
  Each part's prior is normalised on its own range; the parts are combined
  with prior mass (25/120, 95/120) times evidence, each part's evidence
  shared equally between its two seeds, as A1's `combined.json`.
- **The LAL-consistent build in both members** (the owner's rule for the
  stages after A1), so the two members of each pair differ only by the
  catalog.
- **Variance limit 4 with the smooth guard**, as A1 and B1.
- **The catalog nuisances are sampled**, as in 12Y, where B1 draws them from
  their priors.

### Reading (declared now)

On the combined posteriors of each pair:

- **Δ = (median_DESI − median_spectral) / sd_spectral**, the shift of the
  DESI median in units of the spectral sd;
- **R = sd_DESI / sd_spectral**, the width ratio.

| band | condition | reading |
|---|---|---|
| robust | \|Δ\| < 0.2 and 0.9 <= R <= 1.1 | the catalog does not change H0 at this freedom and precision |
| mild | 0.2 <= \|Δ\| < 0.5, or R in [0.8, 0.9) or (1.1, 1.25] | the catalog changes it slightly |
| material | \|Δ\| >= 0.5, or R < 0.8, or R > 1.25 | the catalog changes it |

The bands are those of 12AB. Then, **beside B1's Δ and R** (B1 against A1):
the two are estimates of the catalog's effect under different freedom. The
same band in both supports B1's reading on the parameter that carries most of
the width. Different bands are reported to the owner and not resolved here.

### Before the chains

Check 6 was added by the amendment of 2026-10-18 (below).

1. **B1's tests of the generalized target** (12AD) pass at the committed
   code: at the fixed population it equals the existing target bit for bit;
   with only γ moved it equals the step-1 target.
2. **Spectral control:** at γ = 2.5439 and μ1 = 9.9109 the Part 2 spectral
   likelihood with the LAL-consistent build reproduces
   `phase12_5/lalcosmo_check/runs/lalcosmo/spectral_h0.json` to 1e-8 in ln L
   at every H0 where neither is penalised. That grid is at limit 20; at the
   fixed population the spectral likelihood is penalty-free at limit 4 at
   every H0 (12AA).
3. **DESI control:** the Part 2 DESI target at the fixed population with the
   Part 1 PE input reproduces the Part 1 scan stage at its 12 H0 values to
   1e-6; with the LAL-consistent build, the difference at the same points is
   reported (expected a few times 1e-3, as for the spectral grid).
4. **Guard map at limit 4:** 2000 prior draws per H0 part for each member,
   the fraction penalised; and the four corners of (γ, μ1) at three H0
   values. Recorded here before the chains are submitted.
5. **CPU smoke** of both chain commands at nlive 8.
6. **Kernel pin on the Part 2 DESI target** (added 2026-10-18):
   - pin auto against pin off, at the 12 H0 values of control 3 and at 64
     prior draws per H0 part. Pass: largest |Δ ln L| at most 1e-9 and the
     same non-finite pattern;
   - a 10-minute timing stretch of the DESI chain command on a rita A100,
     giving the seconds per call with the pin on.

   Control 3 itself runs with the pin on, at its declared tolerance of 1e-6.

### What is reported

Per chain, per H0 part and for each combined member:

- H0 median, 68% and 90% intervals, sd; γ and μ1 (median, 68%), and the
  H0-μ1 correlation and slope;
- ln Z per chain, the lower part's weight, and its spread over the four
  pairings of one seed from each part;
- the fraction of posterior samples penalised by the variance limit;
- convergence and the gate of every chain;
- the catalog nuisances against their priors (DESI chains);
- Δ and R, with their band; and B1's Δ and R beside them.

### Compute and outputs

- **Both rita A100s**, the same job settings as Part 1. The queue order is
  under "Part 2 amendment (2026-10-18)" below.
- **The DESI chains:** six sampled parameters; at the 12Y rate (about
  0.23 s per call, 8 h for five parameters), about 8 to 12 hours each, in
  two rounds on the two GPUs. **The spectral chains:** three parameters at a
  few milliseconds per call, well under an hour each.
- **About 1 to 1.5 days in all.**
- **Code:** a consumer branch from the committed B1 branch: the DESI chain
  command with μ1 as a sampled population coordinate (on B1's generalized
  target), the spectral chain command with γ and μ1 only, and the
  combination with A1's code. CPU tests first.
- **Outputs:** `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/gamma_mu1/`
  (`desi/<part>_seed<n>/`, `spectral/<part>_seed<n>/`, `combined/`, one
  `summary.json`).

### Part 2 amendment (2026-10-18): kernel pin auto, and the rita queue

Owner decision of 2026-10-18, before any Part 2 chain.

**Kernel pin "auto" for Part 2's DESI chains.**

- **What changes.** Only the DESI member's pin, from off to auto. Everything
  else in Part 2 is as declared:
  - the DESI and spectral members, γ flat on −10 to 10, μ1 flat on 5 to 20;
  - the split at 45 and two seeds per part;
  - variance limit 4 with the smooth guard, and the LAL-consistent GW inputs;
  - dynesty with 1000 live points and dlogz 0.1, a queue size of 1, and no
    batched pool.

  Part 1 keeps pin off, as its column neighbour 12Y. It is already running.
- **What the pin does.** Core's catalog kernel pin (darksirens-core #28 and
  #30) builds the catalog kernel quadrature once per target, at a reference
  H0. It then serves the kernel with the scalar shift 3 ln(H0/H0_ref)
  instead of redoing the quadrature on every call. It applies exactly when
  none of Om0, w0, wa, δ and σ_kde is sampled. That holds in Part 2, whose
  coordinates are H0, γ, μ1 and the three catalog nuisances. Details are in
  12AF (PR #54), "Kernel pin".
- **The equality figure.** Pin auto equals pin off to **1.8e-12 in ln L**
  (relative 2.1e-15), and is **not bitwise**.
  - Measured on the Jetstream2 H100 on 2026-10-18, on the step-1 target
    (union, δ 0, γ sampled, limit 20).
  - 128 points were used, half prior draws and half near the reference
    point. They were evaluated with the pin on, in batches of 1 to 64,
    against single pin-off calls.
  - 71% to 79% of the values are bitwise equal.
  - Source: `phase12_5/batching/results/run_desi_vmap_K*_pinauto.json`.
  - Core's own test (darksirens-core #30) gives rtol 1e-12, at worst 4.1e-13
    relative.
- **Never resumed across pin settings.** Each DESI checkpoint is stamped
  with the resolved pin (setting, active, the pin's catalog digest). A
  resume under another setting or digest is refused.
- **The acceptance marker.** The consumer's acceptance marker admits only
  pin off today. The Part 2 chain command admits auto for this record, on
  the owner's decision, and records the resolved pin, as in 12AF.
- **The reading does not change** at the precision of Δ and R. Part 2's
  catalog effect is set beside B1's, which was computed with pin off; the
  two likelihoods agree to about 2e-12.
- **Cost.** On the H100 one DESI likelihood call took 27.6 ms with the pin
  on, against 152 ms with it off: 5.5 times faster.
  - The A100 figure is not measured; check 6 measures it.
  - The declared 8 to 12 hours per DESI chain (at 0.23 s per call) is now an
    upper bound.
  - Core's dynesty adapter still evaluates the prior transform point by
    point, so a chain gains less than the likelihood alone.

**The rita queue.** Both rita A100s are held now, so Part 2 is queued
behind:

- **job 1389044:** Part 1 of this record, the ladder cell. It started on
  2026-10-18 at 09:53 UTC and is estimated at 6 to 8 hours (limit 3 days);
- **job 1389048:** the 12AB north/south scans moved to rita. It started at
  10:05 UTC and takes about 2 minutes per task of three lattice nodes over
  18 tasks, so it should finish within an hour (limit 6 hours).

Part 2 is submitted when its code and checks are done: two GPU jobs with
Part 1's settings (account phy220048p, partition RITA-GPU, qos rita, one
a100-80, 16 CPUs, 64G), plus one short HENON task.

| job | dependency | runs, in order |
|---|---|---|
| A | `afterany:1389048` (the north/south GPU job) | DESI upper part seed 41, DESI lower part seed 31, spectral upper 41, spectral lower 31 |
| B | `afterany:1389044` (the ladder cell) | DESI upper part seed 42, DESI lower part seed 32, spectral upper 42, spectral lower 32 |
| combination | `afterok` on A and B (HENON, CPU) | both members' combinations, Δ and R, `summary.json` |

- `afterany` waits only for the GPU to be freed; Part 2 needs nothing from
  those two jobs.
- Each job checkpoints every 30 minutes. A resubmission skips finished
  chains and resumes an unfinished one, under the same pin setting only.

## Expectations, not thresholds

- **Part 1: between the spectral γ-fixed value (66.17) and the DESI
  γ-free value (67.63), with the catalog inert:** Δ near 0 and R near 1
  against its row neighbour, with an sd near 4.9. With γ free the union sat
  0.3 below its spectral twin (12Y); the same offset here would put the cell
  near 65.9, just under the spectral value, which still reads as an inert
  catalog.
- **Part 2: robust.** At the fixed population the catalog likelihood
  equalled the spectral one up to a constant (within 0.7 in log, 12V to
  12X), and with γ free the union moved H0 by −0.06 spectral sd (12Y).
  Freeing μ1 widens both members; the catalog would change the pair only if
  the ratio of the two likelihoods varies along the μ1-H0 direction.
- The spectral member is expected wider than the γ-free fixed population
  (5.40) and narrower than A1 (12.4), since it frees two of the seventeen.

## Limits, stated in advance

- **Part 1 is conditional on the fixed population**, as its row. Stage A0
  (12Z) found shifts of 4 to 9 km/s/Mpc per one-sigma step of several mass
  parameters.
- **Part 1 is one chain with one seed;** no seed scatter is measured.
- **Part 1 keeps variance limit 20,** as its neighbours, where A1, B1 and
  Part 2 use 4. At the fixed population the spectral likelihood is
  penalty-free at limit 4 at every H0 (12AA), so the choice is not expected
  to matter; it is not checked for the DESI target.
- **Part 2 frees two of the seventeen parameters.** σ1 stays at 0.78, where
  A1 found 0.20 and found it set by the variance limit; the other mass
  parameters that move H0 (σ2, μ2, the break mass) stay fixed. Part 2 is not
  the population-free result and is not quoted as one.
- **Part 2 against B1 compares catalog effects, not H0 values:** the two
  have different freedom and different PE inputs on the spectral side (A1
  used the earlier build).
- **Two seeds per part,** against four in A1; the seed scatter of the lower
  part's weight, a factor of three in A1, is measured only coarsely.
- δ is fixed at 0 throughout; δ and γ are never sampled together.

## Not verified

- That the chain command runs with δ fixed and no population parameter
  sampled: the equivalence is a unit test of 12Y, not a chain.
- The per-call cost of the generalized DESI target with μ1 free on an A100
  (0.23 s is the γ-only figure).
- That the A1 spectral command samples a named subset of the population
  without change.
- That the DESI target at limit 4 starts in the lower H0 part: the start
  check needs the reference population free of penalty there (true for the
  spectral likelihood, 12AA; not checked for the DESI one).
- Whether the variance limit penalises the DESI target where it does not
  penalise the spectral one, near the edges of the μ1 prior. Reported, not
  assumed.
