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
| core | e7c3007 with its defaults, kernel pin off | same |

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

- **Both rita A100s**, the same job settings as Part 1.
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
