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

**PART 2 DONE (2026-10-18, 22:40 UTC): robust, the same band as B1.** With γ
and μ1 free, the DESI chains give H0 65.85 [58.85, 73.68] (sd 7.29) against
the spectral 66.14 [59.40, 73.26] (sd 7.00), so Δ = −0.04 and R = 1.04. B1
is robust too, with Δ = +0.08 and R = 1.04. The same band in both supports
B1's reading on the parameter that carries most of the width: the catalog
leaves μ1 (10.02 in both members), and with it H0, where the spectral sirens
put them. All eight chains converged and none is penalised; the lower H0
part holds 4.5e-4 (DESI) and 3.3e-4 (spectral) of the mass. Part 2 frees
two of the seventeen parameters and is not the population-free result. See
"Results (2026-10-18)" at the end of Part 2.

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

### Results (2026-10-18): robust, the same band as B1

rita jobs 1389599 (14:53 to 22:40 UTC, 7.8 h) and 1389600 (13:28 to 21:11
UTC, 7.7 h), one A100 each; the combination and summary on HENON, job
1389601 (22:40 UTC, 4 s). Times from `sacct`. Env `consumer_e7c3007_cuda12`
(core e7c3007), worktree `phase12_5/repo_B2` (branch `phase12.5/direct-desi`).
Kernel pin auto, active in all four DESI chains (one pin digest); a queue of
1 and no batched pool; limit 4 with the smooth guard; the LAL-consistent PE.
Outputs in `phase12_5/gamma_mu1/` (`desi/`, `spectral/`, `combined/`,
`summary.json`).

**The chains ran at three commits of the working tree, all clean.** Each
chain reads the working tree when it starts, and the B2 work (12AF)
committed to it during the run:

- 0c9e6d7: spectral upper 42 and lower 32 (the commit job 1389600 logs at
  its start);
- fc5792c: DESI upper 42;
- 78b84f9: the other five chains and the combination.

From 0c9e6d7 to 78b84f9 the chain driver changes only in the batched pool
(it now refuses a dynesty other than 2.1.4), which these chains do not use.
The other changes are B2 scripts, a B2 smoke manifest and tests. The eight
chains ran the same code path.

**The combined members** (A1's combination, 40,000 draws). H0 in km/s/Mpc,
the slope in km/s/Mpc per solar mass:

| member | H0 median [68%] | 90% | sd | γ median [68%] | μ1 median [68%] | H0–μ1 correlation, slope |
|---|---|---|---|---|---|---|
| DESI | **65.85 [58.85, 73.68]** | [54.46, 78.49] | **7.29** | 2.34 [1.97, 2.73] | 10.02 [9.77, 10.27] | −0.64, −18.4 |
| spectral | **66.14 [59.40, 73.26]** | [55.46, 78.45] | **7.00** | 2.27 [1.91, 2.64] | 10.02 [9.77, 10.27] | −0.63, −17.7 |

The H0 means are 66.20 and 66.36.

| comparison | Δ | R | band |
|---|---|---|---|
| this record: DESI against spectral, γ and μ1 free | **−0.042** | **1.042** | **robust** |
| B1 (12AD): DESI against A1, all seventeen free, by importance weights | +0.082 | 1.035 | robust |

- **The catalog does not change H0 with γ and μ1 free.** The DESI median is
  0.04 spectral sd below the spectral one, and the width grows by 4%. B1 is
  in the same band.
- **The catalog leaves μ1 in place:** 10.022 against 10.017, 0.02 of its sd.
  γ moves by +0.07 (0.18 of its sd). H0 follows μ1, so with μ1 unmoved H0 is
  unmoved.
- **The band holds seed by seed.** Over the four pairings of one DESI upper
  seed with one spectral upper seed, Δ runs from −0.08 to −0.01 and R from
  1.02 to 1.06. The lower part, under 5e-4 of the mass, is left out there.
  Recombining from the nested points with their exact weights, instead of
  40,000 draws with replacement, gives Δ = −0.038 and R = 1.042.
- **H0 follows μ1 less than in A1:** correlation −0.64 and −0.63, a slope of
  about −18, and 41% and 40% of the H0 variance, against A1's −0.85, −30 and
  72%. σ1 and the other mass parameters are fixed here.
- **Against Part 1 (γ and μ1 fixed), freeing them widens both members
  alike:** the sd goes from 4.95 to 7.29 (1.47 times) with the catalog and
  from 4.89 to 7.00 (1.43 times) without. The medians move by −0.3 and
  −0.03. The spectral sd of 7.00 lies between the γ-free 5.40 and A1's
  12.4, as expected.
- **ln Z of the DESI member over 20 to 140** is −662.690, against Part 1's
  −656.916: the evidence prefers γ and μ1 fixed by 5.77, the Occam factor
  of two wide flat priors. The PE build and
  the variance limit differ between the two (LAL-consistent and 4 here, the
  earlier build and 20 in Part 1). Both differences are negligible for the
  spectral likelihood at the fixed population; neither is checked for the
  DESI one.

**Per chain.** ln Z with dynesty's error.

| chain | H0 median [68%] | 90% | sd | γ median [68%] | μ1 median [68%] | H0–μ1 correlation, slope | ln Z | commit |
|---|---|---|---|---|---|---|---|---|
| DESI upper 41 | 65.71 [58.59, 73.77] | [54.47, 78.63] | 7.38 | 2.34 [1.97, 2.74] | 10.02 [9.76, 10.28] | −0.65, −18.4 | −662.576 ± 0.106 | 78b84f9 |
| DESI upper 42 | 65.99 [59.00, 73.67] | [54.44, 78.33] | 7.20 | 2.33 [1.96, 2.71] | 10.02 [9.77, 10.26] | −0.64, −18.3 | −662.338 ± 0.104 | fc5792c |
| DESI lower 31 | 43.99 [42.45, 44.72] | [41.02, 44.92] | 1.33 | 3.25 [2.83, 3.67] | 10.58 [10.38, 10.78] | −0.21, −1.4 | −668.832 ± 0.110 | 78b84f9 |
| DESI lower 32 | 43.98 [42.48, 44.73] | [41.05, 44.92] | 1.29 | 3.25 [2.83, 3.68] | 10.58 [10.39, 10.78] | −0.18, −1.2 | −668.841 ± 0.110 | 78b84f9 |
| spectral upper 41 | 66.08 [59.34, 73.15] | [55.46, 78.34] | 6.94 | 2.27 [1.91, 2.64] | 10.01 [9.77, 10.27] | −0.62, −17.2 | −662.306 ± 0.107 | 78b84f9 |
| spectral upper 42 | 66.30 [59.48, 73.46] | [55.19, 78.48] | 7.03 | 2.27 [1.91, 2.63] | 10.02 [9.77, 10.27] | −0.63, −17.8 | −662.233 ± 0.106 | 0c9e6d7 |
| spectral lower 31 | 43.92 [42.29, 44.72] | [40.61, 44.92] | 1.44 | 3.18 [2.75, 3.58] | 10.59 [10.40, 10.80] | −0.19, −1.3 | −668.945 ± 0.110 | 78b84f9 |
| spectral lower 32 | 43.90 [42.24, 44.72] | [40.55, 44.92] | 1.46 | 3.18 [2.75, 3.60] | 10.59 [10.39, 10.81] | −0.18, −1.3 | −668.941 ± 0.110 | 0c9e6d7 |

**Per H0 part** (the two seeds pooled with equal mass, as in the
combination). ln Z is the mean of the two seeds, with their half-range.

| part, member | H0 median [68%] | 90% | sd | γ median [68%] | μ1 median [68%] | H0–μ1 correlation, slope | ln Z |
|---|---|---|---|---|---|---|---|
| upper (45 to 140), DESI | 65.86 [58.83, 73.71] | [54.46, 78.50] | 7.29 | 2.34 [1.96, 2.73] | 10.02 [9.76, 10.27] | −0.64, −18.4 | −662.457 (0.119) |
| lower (20 to 45), DESI | 43.98 [42.46, 44.73] | [41.04, 44.92] | 1.31 | 3.25 [2.83, 3.68] | 10.58 [10.38, 10.78] | −0.19, −1.3 | −668.837 (0.005) |
| upper (45 to 140), spectral | 66.18 [59.40, 73.28] | [55.38, 78.41] | 6.99 | 2.27 [1.91, 2.64] | 10.02 [9.77, 10.27] | −0.63, −17.5 | −662.269 (0.037) |
| lower (20 to 45), spectral | 43.91 [42.26, 44.72] | [40.57, 44.92] | 1.45 | 3.18 [2.75, 3.59] | 10.59 [10.39, 10.80] | −0.18, −1.3 | −668.943 (0.002) |

**The lower part's weight** by A1's rule: prior mass (25/120, 95/120) times
evidence, each part's ln Z the mean of its two seeds. Recomputed here from
the per-chain ln Z; it equals `combined.json`.

| member | weight of the lower part | over the four pairings of one seed per part | ln Z, lower minus upper |
|---|---|---|---|
| DESI | 4.46e-4 | 3.94e-4 to 5.05e-4 | −6.38 |
| spectral | 3.32e-4 | 3.20e-4 to 3.45e-4 | −6.67 |
| A1, for reference (12AA) | 0.037 | 0.021 to 0.065 (sixteen pairings) | |

- **No low-H0 mode with only γ and μ1 free.** The lower part's mass piles
  against its upper edge: medians 43.9 to 44.0, 90% upper bounds 44.92, and
  2% (DESI) and 3% (spectral) of its mass below H0 = 40. It sits at a higher
  μ1 (10.58) and γ (3.2), along the same degeneracy. It is the tail of the
  one mode, not A1's mode at H0 ≈ 40 and μ1 ≈ 10.8. With the other mass
  parameters fixed, that mode does not return.
- **The lower part's weight is 1.34 times larger with the catalog,** and the
  two pairing ranges do not overlap. At under 5e-4 of the mass it moves no
  number reported here.
- **The seed spread is small:** a factor of 1.28 (DESI) and 1.08 (spectral)
  between the extreme pairings, against a factor of three in A1. The DESI
  spread comes from its upper part, whose two ln Z differ by 0.24 (each
  ± 0.105).

**Penalised fraction: zero.**

- In each of the eight chains, none of the 4,000 guard points (posterior
  samples) is penalised by the variance limit: a 95% upper bound of 7.5e-4
  per chain. So the fraction is 0 for both members.
- The smallest selection N_eff over its threshold among those points is 3.30
  to 3.53 (DESI) and 3.98 to 4.20 (spectral). The total MC variance at the
  posterior mean is 0.98 (DESI upper), 1.12 (DESI lower), 0.89 (spectral
  upper) and 0.99 (spectral lower), against the limit of 4.
- **Precision: float64.** The samples, ln L and guard values on disk are
  float64, and none of the stored ln L or N_eff values is exactly a float32
  number (0 of 11,599 to 13,021 and 0 of 4,000 per chain). They were
  evaluated in float64; core sets x64 at runtime. No likelihood or guard
  quantity was recomputed for this write-up. The statistics here were
  computed in float64 from the stored samples.

**Convergence and the gate.**

| chain | stop reason | final dlogz (target 0.1) | iterations | calls | sampling time | per call | gate 7 |
|---|---|---|---|---|---|---|---|
| DESI upper 41 | convergence | 0.09996 | 11,197 | 312,622 | 13,168 s (3.66 h) | 42 ms | met |
| DESI upper 42 | convergence | 0.09996 | 10,941 | 304,207 | 12,765 s (3.55 h) | 42 ms | met |
| DESI lower 31 | convergence | 0.09993 | 11,988 | 337,274 | 13,466 s (3.74 h) | 40 ms | met |
| DESI lower 32 | convergence | 0.09992 | 12,021 | 337,101 | 13,592 s (3.78 h) | 40 ms | met |
| spectral upper 41 | convergence | 0.09990 | 10,669 | 198,880 | 353 s | 1.8 ms | met |
| spectral upper 42 | convergence | 0.09994 | 10,599 | 196,608 | 348 s | 1.8 ms | met |
| spectral lower 31 | convergence | 0.09993 | 11,561 | 219,028 | 357 s | 1.6 ms | met |
| spectral lower 32 | convergence | 0.09995 | 11,544 | 218,782 | 356 s | 1.6 ms | met |

- All eight stopped on convergence, each in one session, none resumed.
  Gate 7 is met in every chain: convergence verified, unpenalised at the
  posterior mean and median.
- **Both parts start for the DESI target:** the start points at H0 92.5 and
  32.5 pass the MC-reliability gate. This was listed under "Not verified".
- **The DESI target costs 40 to 42 ms per call** on the A100 with the pin on,
  against 0.23 s for 12Y with the pin off. Each DESI chain took 3.6 to 3.8 h
  of sampling, against the declared 8 to 12 h.

**Catalog nuisances (DESI member) against their priors.**

| nuisance | prior | posterior, mean ± sd | shift, in prior sd | width over prior |
|---|---|---|---|---|
| M0hat | N(−20.500, 0.199) | −20.50 ± 0.20 | +0.01 | 1.01 |
| sigma_M | N(0.557, 0.130) | 0.56 ± 0.13 | 0.00 | 0.99 |
| log10 n0 | N(−1.8105, 0.0364) | −1.816 ± 0.035 | −0.14 | 0.97 |

- Per chain, M0hat and sigma_M stay within 0.04 prior sd of the prior centre,
  with widths 0.99 to 1.01. log10 n0 moves by −0.12 and −0.15 prior sd in
  the upper part and by −0.24 and −0.26 in the lower.
- The catalog does not constrain them, as in Part 1 and 12Y. log10 n0 of the
  combined draws is mapped from its sampled prior quantile.

**Read within the limits.**

- **Not the population-free result.** Part 2 frees two of the seventeen
  parameters, and its H0 is conditional on the other fifteen (σ1 at 0.78
  among them). It gives the catalog's effect at this freedom, beside B1's.
  `summary.json` also sets the DESI member's median and sd against B1's
  (−0.25 of B1's sd, 0.57 of its width). Those are different freedoms and
  are not read.
- The μ1 samples stay between 8.9 and 11.5 in every chain, far from the prior
  edges at 5 and 20. The variance limit penalises neither member in its
  posterior; the edges themselves are not tested.
- The checks before the chains (1 to 6 above) are not written up in this
  record.

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
  parameters that move H0 (σ2, μ2, the break mass) stay fixed *(25 Oct 2026: σ2's fixed value 5.73 lies outside A1's 68% interval at limit 4, at its 87th percentile, inside 90%; 12AA, "Amendment (25 Oct 2026): independent review")*. Part 2 is not
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
sha256, in `config/record_envs/12AE.json`; `scripts/check_frozen_environment.py --record 12AE` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AE/<sha7>` on
GitHub (0c9e6d7, fc5792c, 78b84f9). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON);
it was green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main
(above).

**Population (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding C052).** This record's runs
declared `population.fixed_values` (0.04, 0.10) themselves, in their manifests. The base configuration's declaration
since the consolidation is the same pair, so they resolve the same configuration from main.

**The B1 row's reference (consumer PR #22, merge 84a6b88; finding G4.5).** The comparison table's B1 row ("DESI
against A1, all seventeen free, by importance weights", +0.082, 1.035) is against B1's matched resample of the A1
chains, not A1's combination of record. Against A1's combination it is +0.081 and 1.027. The reading does not change.
From the merge the direct chains' comparison file (`phase12_5_direct_chain.py compare`) names its B1 reference (the
matched resample) and carries the reading against A1's combination from the B1 summary beside it.

**Combination (consumer PR #31, merge b9ec283; findings C016, C120, C140).** The combination now requires every listed
chain and one consumer commit; this record's chains ran at 78b84f9 and fc5792c (DESI) or 0c9e6d7 (spectral), which
differ only in a dynesty-version guard, so its manifest's two combinations carry `--allow-mixed-commits` from the
merge and record the commits they admit. Rerun on the stored chains, both combinations give the same pooled samples
bit for bit (split weights equal to the last binary digit, as on main), and the summary file is unchanged apart from a
`blinding` key that marks it absolute (it holds the members' medians).

**Chains through the 12T stage (consumer PR #31, merge b9ec283; findings C029, C123, C125).** This record's chain
stages use the 12T chain driver: from the merge their `status.json` and logs are location-free, their `--anchor-from`
grid must be accepted (theirs is the accepted exact-GW grid of 12T) and a finished unconverged checkpoint is refused
before the build, except for the smoke chains run with `--allow-unconverged`, whose resume writes the capped result as
before.

**Unconverged checkpoints (consumer PR #31, merge b9ec283; finding C125).** From the merge a chain driver refuses,
before the build, a dynesty checkpoint whose run has finished without converging (a resume cannot extend it; restart
with `--fresh` and, if the call cap stopped it, a larger `sampler.max_samples`). A finished converged checkpoint
resumes as before, and the smoke chains run with `--allow-unconverged` still resume a finished capped run and write
its result. The production checkpoints of this record all finished converged (checked on disk), so its chains resume
as before.

**σ2's fixed value (consumer PR #23, merge edabeb6; finding G4.2).** "Limits, stated in advance" says the mass
parameters that move H0 (σ2, μ2, the break mass) stay fixed. σ2's fixed value 5.73 lies outside A1's 68% interval at
limit 4, at its 87th percentile, inside 90% (12AA, "Amendment (25 Oct 2026): independent review", errata item 1).

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

**Calibration anchor (consumer PR #29, merge 0989df4; finding C094).** A configured log10n0 outside the calibration
prior's log10n0 bounds is now refused, and so is an anchor whose sampler coordinate does not decode back to the
configured log10n0 within 1e-12 (which also happens inside the bounds, far in a conditional normal's tail, where the
quantile rounds to 0 or 1 and decodes to the bound). Before, such an anchor evaluated at the bound without an error in
the callers that did not check it themselves (the anchor gate before sampling, the 12U stage, the direct chains'
anchor and the ladder-cell check). Every record's anchor lies inside its prior's bounds and decodes to within 2.3e-16,
so this record is not affected.

**Writer commit (consumer PR #29, merge 0989df4; finding G4.10).** The summaries behind this record did not carry the
commit of the code that wrote them (the commit is in the job logs and the record). From the merge each summary carries
a `writer` block: the writing script, its checkout's commit, branch and changed-file count, and, where it reads a
short list of files, their sha256 (here, the member comparison hashes its member, reference and B1 files). The stored
summaries are unchanged; a summary rewritten from main carries the block. The ladder-cell chain result gets the
consumer commit from the chain-driver package (finding C124, consumer PR #31, merge b9ec283).

**Runner jobs (consumer PR #30, merge 6d0f800; finding C138).** This record's runner jobs ran from shared clones with
no commit pin. Part 2 mixed commits (its eight chains ran at three commits, already disclosed per chain here; the
differences do not touch the chain numerics). From the merge the runner job files refuse to start without
PHASE12_EXPECT_SHA naming the commit of a clean checkout, and the stage runner repeats that check before every stage,
stopping (exit 3) if the checkout moves.

**Launch files (consumer PR #30, merge 6d0f800; finding C137).** The launch files of this record predate the owner's
Slurm rules of 18-19 Oct 2026 (7-day limits; rita GPU jobs at 128 CPUs and 120G; holder steps only through the
wrapper) and break them. They are kept unchanged in what they launch, as the record of how the record ran, and from
the merge they refuse to run unless PHASE12_ALLOW_HISTORICAL names them (slurm/historical_launch_files.txt lists
them). The B1 and B2 pipelines' HENON fallback now clears every SLURM_* variable first.

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

**Chain resume (consumer PR #25, merge 498a147; findings C004, C042).** The chain drivers of this record resumed any
checkpoint in their output directory, guarded only by core's run fingerprint, which does not cover the catalog
settings (m_lim, the K-correction, a fixed log10n0; sigma_kde only under kernel pin auto) or, for the 12T chain stage,
the input files; and `--fresh` left the old checkpoint in place, so a fresh run killed before its first checkpoint
save could have resumed the old chain. Neither happened for this record: every chain of record ran with `resumed`
false in one session (the only production chain killed and resumed, A1's limit-2 chain high_seed41 of record 12AA,
sampled 3.9 million further calls after its resume, a real continuation), no manifest or launcher passes `--fresh`,
and each stage has its own output directory checked by the manifest runner's input checksums. Since the merge, the
drivers stamp a run identity (the resolved configuration's sha256, the inputs' sha256, the code, the package commits
and the backend) beside the checkpoint and resume only under it; a checkpoint without a stamp, as every checkpoint of
record is, is refused unless `--adopt-checkpoint` is passed; and `--fresh` moves the old chain aside (to
`<out>/superseded-<UTC>/`; nothing is deleted). Core's run fingerprint and the recorded `run_fingerprint_digest` are
unchanged.

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

For this record both stages of the ladder-cell manifest still read done. The consumer's chain-driver package (consumer
PR #31; findings C016, C120, C140) added `--allow-mixed-commits` and the result files of all four chains to the desi
and spectral split-prior combination stages of the gamma/mu1 manifest after they ran (the chains of record ran at two
consumer commits that differ only in a dynesty-version guard). Their DONEs hold the command before that edit, so the
fixed runner reports these two stages stale and refuses them (outputs untouched); the other nine stages still read
done.

**Misspelt `--set` keys (consumer PR #25, merge 498a147; finding C088).** A misspelt `--set` key outside the sampler
block was accepted, ignored and shown in config.resolved.json. No record path carries one: every `--set` key of the
manifests in config/, of the 12AG and 12AH Part B plan builders and of the shell and Slurm scripts (slurm/,
scripts/*.sh) is a key of the base configuration of the driver it reaches or a key that driver reads (a test of the
consumer checks each of them, command by command). Since the merge, such a key is refused before anything runs.

**The reused spectral-only grid's note (consumer PR #35, merge d036f1e; owner decision of 26 Oct 2026, blinding,
decision 13A).** `paths.spectral_exact_note` in `config/phase12_5_ladder_cell_manifest.json` and its smoke copy
described the reused 12T spectral-only grid by its absolute H0 summary. From the merge the note says only what the
grid is and that its MAP is the chain's anchor H0, and points to an owner-only file outside every repo that keeps the
note as it was. Only the note's text changes: no stage, path or input checksum does, and no runner reads it, so the
manifest reproduces the runs of record. A test checks that no manifest note quotes a summary.
