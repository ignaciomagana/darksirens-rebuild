# 12AM — The nside × sigma_kde ladder under the sky-averaged selection density (D2)

## Status

**DECLARED (2026-10-19, about 21:30 UTC), before any 12AM job or likelihood.** This record fixes the densities,
cells, grids, inputs, controls, readings and compute before anything runs. Nothing has run. The only things read for
it are:
- records 12AG, 12AI, 12AJ and 12AL;
- core's source at e7c3007 and the consumer's source at 5c2a096;
- location-free files: summaries, controls, cell records (timings, memory, table sizes), and the header lines and
  DONE markers of 12AL's Lane A logs (timestamps only);
- file sizes and sha256;
- the Slurm queue.

**BUILT (2026-10-19, about 22:30 UTC), amendment B1 below.** The code is written and tested. The CPU controls and a
short GPU control passed, after one declared fix (B1.6). No production job has run.

**Blinding: location-free**, as in 12AG to 12AL. No H0 location appears here, in commit messages, in code comments
or in any summary: no median, interval, MAP or shift in km/s/Mpc. The only H0 values in this record are fixed a
priori:
- the coarse grid [20, 140] at step 0.5;
- the fine window [50, 100] at step 0.1;
- the reference point 75;
- the five control points 50, 62.5, 75, 87.5 and 100 (12AJ's);
- core's constant 67.74 (`KERNEL_PIN_H0_REF`), at which the H0-invariant catalog tables are built.

Files holding absolute log-likelihoods are written by jobs and are not for agents to open. That includes the 12AG
and 12AL per-cell files that 12AM's jobs compare against. This record holds only their sha256.

**Experimental.** As in 12AL, this is a measurement, kept as a record. D2 is not a core option. Adopting it would be
a core PR, and that is the owner's call.

## Why

### The owner's question

The real DESI result shows no catalog information. The owner believes some analysis choice washes it out. The
suspects are the sky-pixel size (nside) and the minimum width of the galaxy redshift kernels (sigma_kde).

### Why 12AG does not settle it at the fine cells

12AG ran all 20 cells at fixed calibration with core's production selection term (D0). No cell narrowed H0. Its
verdict: the smearing scales tested "do not explain the missing information wherever the Monte-Carlo resolves them".

But at the fine cells the Monte-Carlo did not resolve much. Six cells had a total Monte-Carlo variance (PE sum plus
selection) above 2 inside their 90% interval:

| cell (nside, sigma_kde) | total MC variance, max inside 90% | R (12AG) | 12AG reading |
|---|---|---|---|
| 64, 1e-4 | 2.11 | 1.054 | no narrowing |
| 128, 1e-4 | 7.65 | 1.167 | no narrowing |
| 128, 3e-4 | 2.60 | 1.140 | no narrowing |
| 256, 1e-4 | 13.97 | 1.190 | limited by the Monte-Carlo variance |
| 256, 3e-4 | 4.18 | 1.165 | no narrowing |
| 256, 1e-3 | 2.20 | 1.021 | no narrowing |

- Five of them read "no narrowing" only because 12AG's variance condition gates "narrows" and "a hint", not "no
  narrowing". Their R values carry that variance.
- The variance there is mostly selection. In 12AG's probe at sigma_kde 1e-4, the largest selection variance over
  five points was 4.45, 24.46 and 6.33 at nside 64, 128 and 256. The largest PE sums were 0.55, 1.21 and 2.88.

### What 12AJ and 12AL add

- **12AJ:** the noise that moves the posterior is the catalog-added selection term: 80% of the shape variance at
  nside 64 and 82% at 128 (sigma_kde 3e-3).
- **12AL:** at four cells, (64, 128) × (3e-3, 1e-3), D2 removed 85–97% of the catalog-added selection variance.
  - It was consistent with D0 at D0's own noise level.
  - R against spectral only was 1.006–1.017, with Delta −0.03 to −0.01.
  - The nside-128 widening under D0 (R 1.15–1.16) was gone. It came from the selection noise, not from information.
  - D1 removes all of the catalog-added selection variance, but moves the median by −0.25 to −0.34 spectral sd.

### So

Redo all 20 cells of 12AG under D2. Where the selection noise was the limit, D2 should lift it, and the cell can then
be read. Where the PE samples are the limit, D2 cannot help. The spiky small-sigma_kde cells may be such cases. A
PE-limited cell is then read as "limited by the PE samples", not as "no narrowing".

## What stays as in 12AG and 12AL

**The 20 cells** are 12AG's: nside {32, 64, 128, 256} × sigma_kde {1e-4, 3e-4, 1e-3, 3e-3, 1e-2}. Names are 12AG's
(`ns64_sk3e-03`). The production cell is (64, 3e-3).

**Everything else is 12AG's ladder setting, unchanged:**
- calibration log10 n0 −1.8216 (h-scaled), M0hat −20.4975, sigma_M 0.5592, delta 0, z_depth 0.245, m_lim 21, the
  production k-correction;
- the population fixed as in the spectral-only reference (gamma 2.5439, mu_chi 0.04, sigma_chi 0.10, the other 14 at
  GWTC-5 values); Om0 0.3089, w0 −1, wa 0;
- the selection guard soft, variance limit 20; `core_numerics=core_defaults`, `kernel_pin=off`;
- the catalog at the cell's nside, 12AG's builds (same 22,785,279 galaxies at every nside, gates G1–G3);
- the footprint from the native nside-128 map: degraded equal-area at 32 and 64, native at 128, and 12AG's upgraded
  copy at 256 (every child inherits its parent's f_p);
- PE: 259 events × 4,096 samples; injections: 1,067,946 detected of 944,412,448 drawn;
- core e7c3007 in float64, through the consumer env `phase12t/envs/consumer_e7c3007_cuda12`, nothing installed into
  it.

Each target is built by `phase12t_common.build_target` exactly as 12AG's scan driver builds it
(`phase12ah_a_plan.scan_argv`).

## The densities (fixed now)

Three densities per cell. **D2 is the primary.** D0 is the paired reference. D1 is context and costs almost nothing.
D3 (12AL's coarse-sky variants) is not run.

| Density | Selection density n_D(z, i) at injection i | Role |
|---|---|---|
| **D0** | n_f(z, r_i), core's production field density in the injection's pixel | paired reference (12AG's grids) |
| **D2** | n̄(z) = (1/N_pix) Σ_p n_f(z, p), the mean over every sky pixel | primary |
| **D1** | dN_exp(z) = n0 a_pix g(z), the smooth model | context |

**Common to all, as in 12AL.** At every H0,

ln μ_D = ln[(1/N_draw) Σ_i b_i(H0) n_D(z_i(H0), i)],

where b_i is the density-free part of core's weight (population, Jacobian, 1/prior weight). Then

ln L_D = Σ_i ln Ẑ_i − N ln μ_D + N(N+3)/(2 N_eff,D), plus core's soft-guard wall.

- The PE evidences Ẑ_i and their variances σ_i² are D0's at the same H0, from Lane A (core's stock target). The PE
  side never changes between densities.
- The correction is core's `selection_log_correction`, in x64, with Lane A's PE variance sum.
- D0's ln L in every difference uses D0's selection-only ln μ and N_eff (12AL amendment B2.3). Control 3(d) ties them
  to Lane A.

**Closed forms (12AL).** Below the depth:

n̄(z) = dN_exp(z) [1 − f̄ C̄(z)] + S(z) / N_pix.

- f̄ is the mean of f_p over all N_pix pixels of the global footprint map at the cell's nside.
- C̄(z) is core's completeness curve.
- S(z) = Σ_p N_obs,p p_cat(z | p) is the catalog term summed over every occupied pixel. With unit galaxy weights it
  is the sum over every galaxy of its own unit-mass, g-tilted kernel, truncated at the depth.

Above the depth every density equals dN_exp(z), which is D0's value there.

### Algebra (12AL's, used here, plus one new statement)

- **(i) Normalisation.** Σ_p n_D2(z, p) = Σ_p n_f(z, p) at every z. So D2's normaliser equals core's field
  normaliser identically, at every H0. Nothing needs renormalising.
- **(ii) Identical pixels.** If every pixel has the same density, D2 equals D0 term by term (control 5).
- **(iii) Isotropy.** D2 is unbiased when p_det is isotropic, or uncorrelated with the catalog's sky structure at
  each z. It is then the Rao-Blackwellised D0, with no more variance. 12AL found no bias at D0's noise level at four
  cells, and no isotropy signal.
- **(iv) New: D2's selection term does not depend on nside, up to a constant.**
  - With unit weights, S(z) is a sum over galaxies. The galaxies are the same at every nside (12AG gate G1).
  - f̄ is the same at every nside: equal-area degrading and the inheriting upgrade both keep the mean (12AL measured
    4e-15 between 64 and 128).
  - dN_exp and S/N_pix both scale as 1/N_pix. So n̄ at nside N is n̄ at nside 64 times 64²/N², at every z.
  - Every injection gets n̄(z_i), whatever its pixel. So N ln μ_D2 moves by a constant across nside, and N_eff,D2
    does not move.
  - **Consequence:** under D2, the nside axis changes only the PE side. The distance between two nsides' D2
    posteriors is the PE side's resolution effect, plus the PE-sample noise of the difference. Control 9 checks the
    premise. 12AL's control 6 found it at 1.8e-12 nat between 64 and 128.

## Implementation (declared now; the code is the build stage)

### Why 12AL's path does not scale

12AL built its tables in one pass over the occupied view of the global catalog, on the card. It also built a native
per-row table for its control 3, with (occupied rows + 1) × 24,501 nodes in float64:

| nside | occupied rows | most galaxies in a row | native table | kernel terms for the D2 table |
|---|---|---|---|---|
| 32 | 7,834 | 5,180 | 1.5 GB | 9.9e11 |
| 64 | 30,411 | 1,719 | 6.0 GB | 1.3e12 |
| 128 | 119,524 | 774 | 23.4 GB (amendment B3's out-of-memory) | 2.3e12 |
| 256 | 473,384 | 569 | 92.8 GB: does not fit an 80 GB card | 6.6e12 |

D2 needs none of that. It needs one 1-D table, S(z) on 24,501 nodes: 196 kB.

### The streamed D2 table

**What is tabulated.** T(z_j) = S(z_j) / g(z_j), the catalog term without core's galaxy measure g, exactly as 12AL
amendment B4. It is computed as core's log N_obs + log p_cat − log g(z) in log space (12AL's
`catalog_term_pairs(..., without_g=True)`).

**Nodes.** 12AL's: z_j = 0.245 j / 24,500, j = 0 … 24,500 (step 1e-5), the last node exactly at the depth. Control 6
may refine them at one cell (below).

**Evaluation.** As 12AL after B4. The interpolant between nodes is log-linear where both nodes are positive, linear
otherwise. The result is multiplied by g(z) with core's own `log_interp_zgrid`, from the tables' own kernel state at
67.74. Zero above the depth.

**The stream.**
- The occupied rows of the global catalog are held on the host, in core's compact layout over every occupied pixel
  (core's compact builder, as 12AL B1.4).
- Core's kernel window is sized once on the host, over the whole occupied view, with the target's own evaluation
  settings (galaxy list; the default "auto" window, tolerance 1e-10), as 12AL did.
- The rows go to the card in blocks. Each block keeps its rows' window half-widths and the whole view's slot count.
  So each row's term is the term 12AL's single pass computed. Only the order of the sum over rows changes.
- For each block: core's kernel state at 67.74 (`build_catalog_kernel_state`), log N_obs, then the catalog term on
  the nodes, summed over the block's rows and added to the running T.
- The block size is fixed in the build so that a block's arrays and kernel state stay under about 4 GB.
- Every block's `log_g_grid` must equal the first block's bit for bit. The table file stores it.
- Recorded per cell: the window's slot count against the rows' slot count (whether the window is active), the
  number of blocks, unit galaxy weights (checked), f̄, and the seconds.

**Where.** A separate process per cell, before the target is built, on the cell's card (any A100). Nothing of it
stays on the card for the later stages. Output `runs/<cell>/table/d2_table.npz` (H0-free) with its sha256 in
`table.json`. The cell stage checks that sha256 before use.

**No native table and no D3 table** is built. 12AL's control 3 (the native table equals D0) is therefore not
repeated. Its role, the table path against core's evaluator, is covered by controls 1, 4 and 6.

### Selection-only evaluation (12AL's machinery)

- `patched_selection_density` routes the selection state to the density and leaves the PE side on the production
  density.
- The selection-only evaluator, with the PE operand a 259 × 1 stub, as 12AL.
- One jitted call per point evaluates D0, D1 and D2, one core `host_density_log_likelihood` per density, as 12AL
  amendment B1.1. The tables are jit arguments, never closure constants.
- D2's state is 12AL's `VariantTables`: one cell, `cell_frac` = f̄, the T table, `log_g`. D1's is one cell with
  `cell_frac` 0 and no table.

### Lane A and the spectral grid

- **Lane A** is `phase12ah_a_scan.py` unchanged, core's stock target with every event's evidence, on the 641 union
  points (`--h0`), as 12AL amendment B1.5.
- **Spectral only** is computed in the cell process on the same 641 points (12AL's `spectral_grid`, core's
  `spectral_siren_log_likelihood`, 12AG's spectral configuration). It records ln L, ln μ, N_eff and the PE variance
  sum per point.

## Grids (fixed now)

- **Coarse:** [20, 140] at step 0.5, 241 points.
- **Fine window:** [50, 100] at step 0.1, 501 points.
- **Union:** 641 distinct points. The 101 shared points have identical floats. Both are built as lo + step × arange,
  exactly as 12AJ and 12AL.

**Posteriors.** Flat prior. A window posterior is normalised on the window. A coarse posterior is normalised on
[20, 140].

**When the window is used (the rule).**
- For each density and cell, the coarse posterior's mass outside [50, 100] is computed.
- A comparison of X against Y uses the window posteriors when both X and Y have mass outside ≤ 1e-3. Spectral only
  passes this (12AJ).
- A density whose own mass outside exceeds 1e-3 has its 90% interval and its readings on the coarse grid, and every
  comparison involving it uses the coarse grid. The summary marks these "coarse".
- The coarse-grid metrics are reported for every density and cell anyway: they connect to 12AG.

**Which code computes them.** Window metrics use 12AL's functions (so control 1's comparison is like for like).
Coarse metrics use 12AG's summary functions (so D0's comparison with 12AG tests the grids, not two quantile codes).

## Inputs (sha256)

All paths are under `/hildafs/projects/phy230054p/magana/darksirens-core-data`. Every sha256 below was computed for
this record. Where 12AG or 12AL recorded one, it is the same.

**Ladder inputs (as 12AG and 12AL):**

| input | path | sha256 |
|---|---|---|
| catalog, nside 32 | `phase12_5/smearing_ladder/catalogs/desi_union_nside32.h5` | `59c95d89f6f29308871f3e1125b68dd292895ccf4f3ccd91fdb198ae249a3196` |
| catalog, nside 64 (= production) | `phase12_5/smearing_ladder/catalogs/desi_union_nside64.h5` | `c2d1ff36567419e42386f07daf30bd0af2e2da714c16f066ecde4eb94d9084e2` |
| catalog, nside 128 | `phase12_5/smearing_ladder/catalogs/desi_union_nside128.h5` | `f26a20f0f3f8ca5a9bc0aee0681cd0eba6f1a7b693055839cba83d6189cdb62c` |
| catalog, nside 256 | `phase12_5/smearing_ladder/catalogs/desi_union_nside256.h5` | `66c50dc4ac1ea3ffc593f8e19cc2baf3f0dd18c8a4953c77b10f262153a684d3` |
| footprint, native nside 128 | `phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| footprint, nside 256 (upgraded) | `phase12_5/smearing_ladder/catalogs/footprint/mth_map_nside256_from128.h5` | `c20e58e3b3570a5e131b3754002ea26024c43e647d3541ae9e1786fcdb181a67` |
| GW PE (259 × 4,096) | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| injections (O3/O4) | `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| configuration | consumer `config/desi.fixed_population.json` at 5c2a096 | `b79ad777f17126bcd78b9ebcff0d02724ae6cfe7ae957829009ca5143f349bb9` |
| spectral-only reference (12AG) | `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json` | `db9f7b80c4b799c18559c99040916a821ed99aa7feb06fcec1d6589a171a6f9f` |
| 12AG catalog gates | `phase12_5/smearing_ladder/catalogs/gates.json` | `ec66534717536bdc3001572ab5ef7ee475e1bf45fc0d69a9a2be181b497eb2db` |

**12AL references** (under `phase12_5/selection_denominators/`; consumer 5c2a096; every file read only by jobs,
except the location-free `summary.json` and `controls.json`):

| cell | `variants.npz` | `tables/tables.npz` | `lane_a/scan.json` | `lane_a/events.npz` |
|---|---|---|---|---|
| ns64_sk3e-03 | `c423ce2dabede9f66cb1e7de836947c8b536b1032cb795f0cda6cffc9d76a004` | `af26b8fa72a531f78eb1d156a35d898ad92fcef78335b2c4b27ec887b12b2592` | `431b38c182b4dc012d85f126d8ab31340d7fd6ec7bcb7a6d6633a91a5182e097` | `df092cf2740f810253d0d7ae2b3b47e8dad205c33f3ac89edd6ddcc40af16fcb` |
| ns64_sk1e-03 | `abef4cb493d02b4ea05f9bac586a38d5e081b1998fec8773d7dda85f422b23c5` | `b38d81718ec856ce3b856ea68ba2a7f0bbfbd3601f7ae88c0aafb8f8385ed2a3` | `e24fe7016f234bafea77391863a64514420a63918406206ea681274bc8b192ce` | `9f0ef10efe6ea791d6ea54a4a16e7370ecea8eb5617065f6f6b220bf8638e64a` |
| ns128_sk3e-03 | `2917a3d96e3f7e80e0c85ca7fd2e961ff647ce36aa986b2e88f029543aefaecb` | `d1d904f8e2c1a88a68ef04db0bbb302c9713a60405ed2f7198d1450299e9308c` | `ce9e1dd68cb101a7e9771c1e112f6b04e75473554d7608877bcba23cb74478fd` | `86780265396da9483be6d985ca1b223f6a231a55b99c80a2aa47bf1b7b4b1e13` |
| ns128_sk1e-03 | `2b09bd14a3408ee730eff41bd61dd68ee5cfcec3885349aa722912459f492484` | `b8f39a26f5a651588ab5b3b9d6004e8217aa10f7f2b2b88b3a1829d2ae686107` | `5a0530d64fa552beb9a510ecfea2958e9e57fa2b7bdddbbb6f917305531cdf21` | `d3db17d77897bbb672b3b4ab7f1bc0002b8f79ab40188e2f1d684afa95424a9d` |

- 12AL's in-lane spectral grid, `runs/<cell>/spectral/spectral.npz`, is the same file at all four cells:
  `fd738c07367c34d8ab8b02e537e3ada4fc683805687b0bcfb1f8912fccd43067`.
- `summary/summary.json` (location-free): `384274c12256a260882cb186db05911a39d94515a90ff5d2c907939777cfc183`.
- `summary/controls.json`: `aeb4b7265a66f9dd3cbefcd69b016c3682e28a9d1a51ed1053e025d02af75204`.

**12AG references** (under `phase12_5/smearing_ladder/`; the coarse grids that control 2 compares Lane A with):

| cell | `runs/<cell>/scan.json` sha256 | cell | `runs/<cell>/scan.json` sha256 |
|---|---|---|---|
| ns32_sk1e-04 | `08ded89c910a974405c567fa9256e0e33709ec7de9e0ea9b9b240c4800b6b4c5` | ns128_sk1e-04 | `5c84d33ebfc59f36dba449283b0a6022e8e19bdfc8c403c349fde4f691b29840` |
| ns32_sk3e-04 | `3c42746f85007a7fd1f8ec9563cb2dc38fb9263c7eaac830f327c7c6291257d1` | ns128_sk3e-04 | `dd3ab8e6cfa4347b8f08602b8ea4d1fadbdbf63b66a0b4b9ac573ddeace0287c` |
| ns32_sk1e-03 | `3189d57954f75c33952b88bb009034ad3e50add9f09cd2408125fb162f2020ec` | ns128_sk1e-03 | `12b2c2b2d4edff4233b84f1b873d172d7dfced9235981b437e1d28c86a1638ce` |
| ns32_sk3e-03 | `721d081dd6aa9c54df11ca239fb9a94fd4bf84df6d16139ae25f9faa5f00c379` | ns128_sk3e-03 | `215d62188ba031385fc5fa2ec129e4476f52f07ff7576fe907ea4bdb6f5ee43d` |
| ns32_sk1e-02 | `34be06829dea1d87f3cd2685797a2198b7345c78a9a7ed41bc785135bcdb068b` | ns128_sk1e-02 | `4dca2ad6662d1c3163761cb0c6cedb556ec7c452fa7bca9c08f430bdb682b778` |
| ns64_sk1e-04 | `7e08320dcf5159c9d141410449d46c59ace0c67e737d23c2d9c42c15d4d696f8` | ns256_sk1e-04 | `47246b0b01d1a0979ca540fef9b61dd88a74f2717dd3270aec0d8ae4a8d29664` |
| ns64_sk3e-04 | `54f861c40d882199e292fb6a55e7ec274bb2b393186c42f772ebf258ec0b902a` | ns256_sk3e-04 | `adddb60775d941ef795c9c2cdbc9b506293cecae7139bc5b72845cb9cf7b7972` |
| ns64_sk1e-03 | `ea9b6290791d5416244fb7cf0d1361da27be79416ee1ed6661b12c624aa08485` | ns256_sk1e-03 | `b4607602d5e79ee675069d314912ac6ca275e8e21e02d65b76291049be7e0d38` |
| ns64_sk3e-03 | `ce3be7a92eecdb28e7e6067ed538fe435a04bd1c421bcea0a41c32547671a608` | ns256_sk3e-03 | `459fb1b7fdb4ef568a21802df8151e9a5f2bda3d22d5776f416d2ecc3cfe4d66` |
| ns64_sk1e-02 | `0d0c8b885a14bf3ae2c9c58d1f305db2e569558d0b8aa8fdbb848cd9801bc434` | ns256_sk1e-02 | `0805087aa2e744bd333a4e1eebbae02d9da882603023e23f6c9e569181feb483` |

- 12AG `summary/summary.json` (location-free; its R per cell): `9269130e169bcaa64d5641e0b94b11f8d71d616b6d2f26e23b8345406fc5e002`.

**12AJ** `lnl_convergence/summary/summary.json` (location-free; the PE-mode floor quoted below):
`7ff83766d71097f2c967f0981c39570bf510f87c26f2f6f7f932ec4b80dc2ccf`.

Every job checks the sha256 of each file it reads against this table and refuses a mismatch.

## Controls (fixed now)

**Three kinds.**
- **Ladder gates:** a failure withholds every reading of the record.
- **Cell gates:** a failure withholds that cell's readings. The cell then counts as incomplete in the washout rule.
- **Marks:** a failure is reported, and the named readings are marked. Nothing is withheld.

The summary always writes its numbers and `STATUS.json`, whatever fails.

### 1. The new D2 path reproduces 12AL's D2 (ladder gate)

At 12AL's four cells, (64, 128) × (3e-3, 1e-3):
- **(a) In the job,** against 12AL's `variants.npz` on disk (sha256 above): N ln μ_D2 and N_eff,D2 at the five
  control points, relative difference ≤ 1e-10 each. The largest difference over all 641 points is reported. The
  same is reported for D0 and D1, not gating.
- **(b) In the summary,** against 12AL's location-free `summary.json`: D2's R, sd ratio, Delta and Hellinger
  distance, against D0 and against spectral only, each within 1e-6.

### 2. D0 Lane A reproduces the earlier grids

- **(a) Ladder gate.** At 12AL's four cells, Lane A equals 12AL's Lane A (`lane_a/scan.json`, `lane_a/events.npz`)
  bit for bit, compared in the job: ln L, ln μ, N_eff, the correction, every ln Ẑ_i and σ_i², at all 641 points.
  - 12AG's control C1 found an A100-40 and an A100-80 bit for bit on this target, so these cells may run on either.
  - **Declared fallback:** if a difference exists only at rounding (≤ 1e-12 relative) and the card model differs
    from 12AL's (A100-80), the cell's Lane A is rerun on a rita A100-80 before any reading. The gate is then read
    there, bit for bit.
- **(b) Cell gate.** At the other 16 cells, Lane A equals 12AG's coarse grid (`scan.json` above) at its 241 points:
  max |Δ ln L| ≤ 1e-9, compared in the job. The maximum is reported.
- **(c) Cell gate.** The in-lane spectral grid equals 12AL's spectral grid (`spectral.npz` above) at all 641 points
  to 1e-9 in ln L (bit for bit expected). Its largest difference from 12AG's reference grid at the 241 coarse points
  is reported.
- **Reported:** D0's coarse-grid R against 12AG's R, per cell (expected equal to rounding).

### 3. Per-event sum, x64, walls and code (12AL control 10, with B2.2 and B2.3)

- **(a) Cell gate.** Σ_i ln Ẑ_i + core's correction = ln L to 1e-9 at every Lane-A point.
- **(b) Ladder gate.** Every process records x64 on, and refuses to run otherwise.
- **(c) Ladder gate.** Every job runs from a worktree of a committed sha with a clean tree, and records the sha.
- **(d) Cell gate.** D0's selection-only ln μ and N_eff equal Lane A's to 1e-12 (absolute in ln μ, relative in
  N_eff) at all 641 points.
- **(e) Cell gate.** At the five control points, D2 from the three-density call equals a single D2 call to 1e-12
  (12AL control 1(d)).
- **(f) Cell gate.** D2's wall |wall| ≤ 1e-9 at every window point, and D2's total variance ≤ 20 at all 641 points.
- **Reported, not gating:** D0's and D1's walls and budgets. D0 already has a penalised point at (128, 1e-4), at the
  coarse grid's lower edge (12AG's probe). Penalised points enter the readings through 12AG's rules.

### 4. The streamed table equals 12AL's tables (ladder gate)

At 12AL's four cells, against 12AL's `tables/tables.npz` (sha256 above), in the job:
- the streamed S/N_pix on the 24,501 nodes against 12AL's `D2__cat`;
- f̄ against 12AL's `D2__fbar`;
- dN_exp and C̄ on core's grid against 12AL's `dN_exp` and `cbar`;
- each to 1e-10 relative, wherever the value exceeds 1e-8 of its array's maximum.

These fix n̄(z) completely. With the same nodes and interpolant, they fix D2's ln μ.

### 5. D2 = D0 on a synthetic catalog with identical pixels (mark; 12AL control 2)

- **The catalog:** every one of the N_pix rows holds the same galaxies: those of the first occupied row, in RING
  order, whose count equals the median (752 at nside 64, 185 at 128, 45 at 256). f_p = f̄ in every pixel.
- **The test:** for the first 100,000 injections at the five control points, |ln n_D2 − ln n_f| ≤ 1e-4 below the
  depth and ≤ 1e-12 above it; the population-free sum Σ_i n_D2 / Σ_i n_f within 1e-4 of 1; no finite-pattern
  mismatch. Tolerances are 12AL's (with B1.3).
- **Where:** nside 64 and 128 at sigma_kde 1e-3 and 3e-3 (12AL's cells), through the new streamed path; and nside
  256 at 3e-3.
- **nside 256 counts as affordable** if it runs on a single A100 within 2 hours. If it does not, it is reported as
  "not run: not affordable", and the control stands at 64 and 128. The summary says which.
- **A failure marks every D2 reading.** It does not withhold them.

### 6. Table accuracy (cell gate; 12AL control 7, D2 only)

- At every cell, 10,000 random z, uniform on [0, 0.245] (seeds 5101 to 5120, one per cell in nside-major order,
  sigma_kde ascending).
- The table's value (T interpolated, times core's g) is compared with core's exact sum over every galaxy, streamed
  the same way.
- Maximum relative error ≤ 1e-4 wherever the value exceeds 1e-8 of the table's maximum, for z ≥ 1e-3 (12AL's gate,
  amendment B1.2). Pairs below 1e-3 are reported.
- **Why it matters here.** At sigma_kde 1e-4 the spectroscopic kernels are about 1.0e-4 wide. One isolated kernel at
  step 1e-5 would allow (h/σ)²/8 ≈ 1.2e-3. The sum over 22.8 million galaxies is much smoother, but this control
  decides.
- **Declared fallback:** a cell that fails is rebuilt on nodes four times finer (step 2.5e-6, 98,001 nodes, still a
  1-D table), and its cell stage reruns (Lane A does not). If it still fails, the cell's D2 readings are withheld.
  Control 1 is not affected: its cells are at 1e-3 and 3e-3, on 12AL's nodes.

### 7. Kernel H0 invariance (cell gate; 12AL control 8)

At every cell, the catalog term of 64 spread rows on the table nodes, built at H0 = 50, 67.74 and 100, agrees to
1e-10 relative wherever above 1e-8 of its maximum. The table is built at 67.74 and used at every H0.

### 8. D1 is spectral only up to a constant (reported, not gating; 12AL control 4)

- ptp over the window of N[ln μ_D1 − ln μ_spec] ≤ 0.01 nat;
- |N_eff,D1/N_eff,spec − 1| ≤ 1e-4 at every grid point.

The tolerances are 12AL's and are not changed. In 12AL it missed narrowly at every cell, with the same numbers (0.0101
nat and 3.0e-4), from interpolating dV_c/dz on two grids. Here it marks only D1's numbers.

### 9. D2 does not depend on nside, up to a constant (cell gate for nside 32, 128 and 256; 12AL control 6, extended)

In the summary, at each sigma_kde, for nside 32, 128 and 256 against 64:
- G = ptp over the window of N[ln μ_D2(nside) − ln μ_D2(64)] ≤ 1e-6 nat;
- max |N_eff,D2(nside)/N_eff,D2(64) − 1| ≤ 1e-10 over the 641 points.

Reported beside it: the tables' largest relative difference (S/N_pix scaled to nside 64) where above 1e-8 of the
maximum; f̄ at each nside; whether the kernel window is active.
- **Why a gate:** the nside-32 and nside-256 tables have no 12AL table to be compared with. This ties them to
  nside 64's, which control 4 ties to 12AL.
- **A failure** withholds that cell's D2 readings, and the nside-pair interpretation along that sigma_kde column.

### Order and stopping

- The four 12AL cells run first in their lanes.
- A cell stage checks control 3(d) (the D0 tie to Lane A) at the five control points first, and stops before its
  nominal grid if it fails there.
- No other control stops a job. Every failure is decided by the summary.

## What is reported per cell (fixed now; every number location-free)

**Notation.** p_X is the posterior of density X (window or coarse, by the rule above). I90_X is its central 90%
interval, used inside jobs only and never printed. "Spectral" is the in-lane spectral-only grid. H is the Hellinger
distance.

For **D2** (primary) and **D0** (alongside), against spectral only:
1. **Width and shift.** R (the 68% half-width ratio), the 90% half-width ratio, the sd ratio, Delta in spectral sd
   with its band (robust |Delta| < 0.2, mild 0.2 to 0.5, material > 0.5), H from spectral.
2. **D2 against D0.** R_D2 − R_D0, Delta_D2 − Delta_D0 in spectral sd, H(p_D2, p_D0).
   - **Noise floor:** 12AL's H_floor,D2 at its four cells: 0.059 at (64, 3e-3), 0.097 at (64, 1e-3), 0.080 at
     (128, 3e-3) and 0.135 at (128, 1e-3). 12AL marked its noise source at the two 1e-3 cells.
   - **Elsewhere: not available.** No injection replicates are run in 12AM.
3. **Monte-Carlo variance**, over the union-grid points inside I90 of the density's own posterior:
   - V_sel = N²/N_eff, its maximum;
   - V_PE = Σ_i σ_i², the PE variance sum (the same for every density), its maximum, and its value at the point
     nearest the median;
   - V_tot = V_PE + V_sel, its maximum;
   - the catalog-added parts: the maxima of V_PE − V_PE,spec and of V_sel − V_sel,spec;
   - the two counterfactuals of the reading rules (below), E_PE and E_sel;
   - whether V_tot passes 12AI's N1 (≤ 1.2) and 12AG's limit (≤ 2).
4. **Guard.** The number of penalised points and of materially penalised points (|penalty| > 0.01 nat) of the 641;
   whether one lies inside I90 or inside the 99% interval of the uncapped coarse grid; the uncapped grid's R, sd ratio
   and Delta. "Penalised" is as 12AG's summary defines it.
5. **Roughness** (supplemental; decides nothing; the owner's rule is that the ln L variance decides):
   - on the window: the rms of the second difference of ln L_X − ln L_spec at step 0.1 (499 values);
   - the same split into the PE part (Σ ln Ẑ_i minus spectral's) and the selection part (the correction minus
     spectral's);
   - 12AI's N2 form, for comparison with 12AI: the coarse grid at step 0.5 over [50, 90], with N2's 0.1 nat.
   - The two forms are different numbers: a smooth curve's second difference is 25 times smaller at step 0.1.
6. **Context.** The catalog-added selection variance a = V90_D0 − V90_D1 and φ_D2 = (V90_D0 − V90_D2)/a, as in 12AL
   (V90 is the maximum of V_sel over I90_D0). D1's R, Delta and H, against spectral and against D0, and its V_sel.
7. **The coarse grid.** Item 1 on the coarse grid for D0, D1 and D2, with the mass outside the window. D0's coarse R
   beside 12AG's.
8. **Bookkeeping.** Compact rows and galaxies, occupied rows, kernel window active or not, table blocks, device
   memory (jax peak and nvidia-smi), seconds per stage.

**Per sigma_kde column: nside pairs.**
- H between adjacent nsides (32–64, 64–128, 128–256), under D2 and under D0.
- **How to read it under D2, declared now:** by algebra (iv) and control 9, the selection term is the same at every
  nside up to a constant. So H_D2 between nsides is the PE side's resolution effect plus the PE-sample noise of the
  difference.
- **Its floor:** only 12AJ's PE-mode floor of the 64-vs-128 difference at 3e-3 exists, 0.019. There the ratio
  H_D2(64, 128)/0.019 is reported. Elsewhere the floor is not available. 12AI's C1 tolerance (0.05) is shown as
  context.

**Ladder level.** R and Delta along nside at each sigma_kde and along sigma_kde at each nside, for D2 and D0.

## Readings (fixed now)

### Per cell: 12AG amendment 2's rules, applied to D2 against spectral only, with one declared change

1. **R band:** R ≤ 0.90 reads "narrows", 0.90 < R ≤ 0.97 reads "a hint", R > 0.97 reads "no narrowing". Recorded as
   `R_band`.
2. **The cell reads "limited by the Monte-Carlo variance" instead** if any of these holds:
   - a penalised D2 point lies inside I90_D2;
   - a penalised D2 point lies inside the 99% interval of D2's uncapped coarse grid (ln L minus the wall);
   - **max over I90_D2 of V_tot,D2 > 2.**
3. **The declared change.** In 12AG the variance condition (the third bullet) applied only to "narrows" and "a hint".
   Here it applies to every R band, as the 12AM brief asks. A cell over the limit is never read "no narrowing".
   Reason: at the fine cells the question is whether the grid can see a narrowing at all.
4. **Which part limits it.** At the trigger points (the I90 points with V_tot > 2, and any penalised point that
   triggered), with spectral only's parts at the same H0:
   - E_PE = max of V_PE + V_sel,spec: the total if the selection were spectral only's;
   - E_sel = max of V_PE,spec + V_sel: the total if the PE were spectral only's.

   | E_PE | E_sel | reading |
   |---|---|---|
   | > 2 | ≤ 2 | **limited by the PE samples** |
   | ≤ 2 | > 2 | **limited by the selection Monte Carlo** |
   | > 2 | > 2 | **limited by both** |
   | ≤ 2 | ≤ 2 | **limited jointly** (only the two catalog-added parts together exceed the limit) |

   - "Limited by the PE samples" says that more PE samples per event, not a change of selection density, would
     resolve the cell (12AJ reading 4's pointer).
   - The R band is still reported beside the reading.
5. A cell with a failed cell gate, an incomplete grid or a non-finite ln L is "incomplete", and is not read.

**D0 is read by the same rules,** on the same grids, alongside. Its readings are not the record's verdict.

### The washout rule: 12AG amendment 2's, unchanged, on the D2 readings

"Smearing washes out the information" is said only when all of these hold:
1. **The direction is right.** A cell reads "narrows" at finer-or-equal smearing on both axes than the production
   cell (nside ≥ 64 and sigma_kde ≤ 3e-3, at least one strictly finer).
2. **A path exists.** A staircase path joins it to the production cell (64, 3e-3), each step one place in nside or
   sigma_kde, always toward the production cell.
3. **R does not fall along the path** by more than 0.02 at any step.
4. **R rises enough.** The production cell reads "no narrowing", or its R is at least 0.10 above the narrowing
   cell's. The production cell must itself be read: not incomplete and not limited by the Monte-Carlo variance.

The other verdicts, unchanged:
- **"Coarser smearing narrows (not a washout)":** every narrowing cell is at coarser smearing (nside ≤ 64 and
  sigma_kde ≥ 3e-3, not the production cell).
- **"Undetermined":** some cell narrows, but no qualifying path exists.
- **"Not explained":** no cell narrows, and every finer cell was read.
- **"Not explained where the Monte-Carlo resolves it":** no cell narrows, but some finer cells are limited or
  incomplete. The summary lists them, each with the part that limits it.

The same rule is also applied to D0's 12AM readings, as context.

### The verdict sentence (declared form)

The summary writes one ladder-level sentence. It must state:
- the washout verdict;
- the range of R and of Delta over the read cells, under D2, with their direction relative to spectral only;
- the largest change of R between adjacent read cells along nside and along sigma_kde, with its size, direction and
  cells;
- the largest change from D0 to D2 (R_D2 − R_D0), with its size, direction and cell;
- the counts of cells limited by the PE samples, by the selection, by both and jointly.

**A setting that moves R by more than 0.02 between adjacent read cells is said to move the result, with the size and
direction. No setting is called "ruled out".**

**What a null result does not test** (12AG, unchanged): the photometric galaxies' own redshift errors. They are 73%
of the catalog, and their median kernel width moves only from 0.0318 to 0.0334 across the ladder.

## Compute (estimate)

### Per cell: three processes in one lane

Each is its own process, with a DONE marker, so a lane can be resubmitted and continues.

| Stage | What | Measured basis | Estimate |
|---|---|---|---|
| **table** | load the catalog, the host view, the window, the streamed T; controls 4 (at 12AL's cells), 6, 7 | 12AL: the D2 table 9–18 s on the card; view and kernel state about 12 s; control 7 about 30 s per table | 3–5 min (nside 256: up to 8) |
| **lane_a** | `phase12ah_a_scan.py`, 641 points with every event's evidence | 12AL's Lane A: 6.6–7.5 min at nside 64 and 128 on rita; 0.35 s per point at 32 and 256 (12AG probe) | about 7 min (8 at 32 and 256) |
| **cell** | the wrapped target; the three-density compile; control 3(e)'s single D2 compile; controls 1, 2 and 3 in the job; spectral (641 points); D0, D1 and D2 on 641 points | 12AL: target build 21–87 s; a compile 70–80 s; spectral 8–9 s for 641 points; six densities 0.25 s per point | about 8–10 min (nside 256: about 12) |

So about 18–22 minutes per cell at nside 32 to 128, and about 25–27 at nside 256. The fine window is the bulk of the
641 points: 501 points at 0.27–0.35 s, 2.3–2.9 min per grid, inside the figures above. 12AL's cells took about 47 min
each, but 29 min of that was its 14 injection replicates and 8 min its six-density controls. Neither is in 12AM.

**Control 5** runs as its own GPU entry in one A100-40 lane, after that lane's first cell (nside 64 and 128, then
256 at 3e-3). About
20–30 min in all. If nside 256 runs out of memory on the 40 GB card, it moves to the end of a rita lane. It runs on
a GPU, not HENON, because HENON is nearly full (21:06 UTC).

**GPU total:** 15 × about 20 min + 5 × about 26 min + control 5 ≈ **7.5 card-hours** (range 6 to 10).

### Lanes

- **rita0, rita1** (A100-80): `-p RITA-GPU --qos rita -A phy220048p --gres=gpu:a100-80:1 --cpus-per-task=128
  --mem=120G --time=7-00:00:00 --dependency=afterany:1390498:1390499`. They queue behind our surrogate-training
  lanes 1390498 and 1390499, which are not touched and are expected to end about 23:00 UTC. Another user's standby
  (`rita-s`) jobs are queued there. Qos rita preempts them by the cluster's policy; nothing is cancelled by hand.
- **twig** (A100-40): `-p TWIG-GPU --qos twig -A phy220048p --gres=gpu:a100-40:1 --cpus-per-task=32 --mem=120G
  --time=2-00:00:00` (twig's maximum). Only the cards free at submission get a lane. At 21:06 UTC two of four are
  free; another user holds two.
- **henon-gpu** (A100-40): `-p HENON-GPU --qos henon-gpu -A phy220048p --gres=gpu:a100-40:1 --cpus-per-task=64
  --mem=240G --time=7-00:00:00`. One of two cards is free at 21:06 UTC.
- **Summary** on HENON CPU: `-p HENON --qos henon -A phy220048p --time=7-00:00:00 --exclude=henon06,henon08`, a few
  CPUs, `--dependency=afterany` on every lane. It always writes `summary/STATUS.json`.
- The lanes set `XLA_PYTHON_CLIENT_MEM_FRACTION=0.92` and XLA preallocation off, as 12AL. This changes no number.
- **Not used:** MIKO (no job, no step; job 1388940 is not touched) and js2h100.

**Routing (12AG amendment 2's rule).** A stage goes to an 80 GB card when the larger of nvidia-smi's peak and 1.6 ×
jax's peak is above 34 GiB, or when it ran out of memory on a 40 GB card.
- nside 256 goes to rita only (12AG: out of memory on an A100-40).
- nside 32 to 128 may run anywhere. The build stage's short GPU control measures the cell stage at nside 128 and 32
  on an A100-40. If either breaks the rule, those cells go to rita, by an amendment before production.

**Assignment.** As 12AG's planner: longest first, each to the least-loaded lane the routing allows. The four 12AL
cells are first in their lanes. The five nside-256 cells take rita, with one or two smaller cells after them to
balance.

**The watcher** is a shell until-loop held by the main session. It ends on `summary/STATUS.json` or on the first job
in a failure state. No agent polls.

### Estimated time to completion

- **Build stage first** (code, CPU tests, a short GPU control of about 15 min on an A100-40): about 2–3 hours of
  agent time. Not counted in the GPU total.
- **Production, with three A100-40 cards from submission and both rita cards from about 23:00 UTC:**
  - the A100-40 lanes (about 13 cells and control 5): about 1.5 hours;
  - the rita lanes (5 nside-256 cells and about 2 others): about 1.4 hours once rita is free;
  - the summary: about 5–10 minutes after the last lane.
- **So about 2 hours from submission to the summary** if rita is free by then, or about 1.5 hours after rita frees
  if it is not.
- **On the clock:** if the build is submitted by about midnight UTC, the summary is due about 01:30–02:30 UTC on
  2026-10-20.
- **Range** 1.5 to 4 hours after submission. Longer if 1390498/1390499 overrun, if the nside-128 cells must move to
  rita (then about 2 hours on rita), or if HENON queues the summary.
- The 7-day and 2-day limits are ceilings, not the estimate.

## Code (the build stage; nothing written yet)

**Consumer repo** `phase12_5/repo_12AM`: a clone of `phase12_5/repo_12AL`, origin set to repo_12AL's GitHub remote
(`ignaciomagana/desi_darksirens_selection`), new branch `phase12am/d2-ladder` from 5c2a096. Local commits only.

Planned files:
- `scripts/phase12am_common.py`: the streamed D2 table, the densities (12AL's machinery reused, not changed), the
  window rule, the MC split, the readings, the location guard;
- `scripts/phase12am_table.py`: the table stage (controls 4, 6 and 7);
- `scripts/phase12am_cell.py`: the cell stage (controls 1(a), 2, 3; spectral; the three densities);
- `scripts/phase12am_control5.py`: control 5;
- `scripts/phase12am_plan.py`, `scripts/phase12am_summary.py` (controls 1(b) and 9, every metric and reading);
- `slurm/phase12am_*`;
- `tests/test_phase12am.py`: CPU tests on tiny synthetic inputs, including the streamed table against 12AL's single
  pass bit for bit or to rounding, block-wise windows, the MC split's four cases, the declared reading change, the
  washout rule on synthetic ladders, and the summary withholding on each gate kind.

Nothing in `phase12/`, `phase12t_*`, `phase12ag_*`, `phase12ah_*` or `phase12al_*` changes. Lane A runs
`phase12ah_a_scan.py` unchanged. Every job runs from `d2_ladder/worktrees/<sha>/`, a worktree of a committed sha
with a clean tree.

## Outputs

Under `phase12_5/d2_ladder/`:
- `plans/`: the plan and the job ids.
- `runs/<cell>/`:
  - `table/`: `d2_table.npz` (H0-free) and `table.json` (location-free);
  - `lane_a/`: `scan.json`, `events.npz`. Absolute: not for agents;
  - `cell/`: `variants.npz` (ln μ and N_eff per density and point) and `spectral/`. Absolute: not for agents;
  - `controls.json`, `cell.json`: location-free.
- `controls/control5/`: location-free results.
- `summary/`: `summary.json`, `controls.json` and `STATUS.json` (location-free, with the location guard of 12AJ and
  12AL: forbidden key names, and no float equal to any absolute posterior location); `absolute.npz` (not for
  agents).
- `logs/`, `worktrees/`.

Printed progress carries no likelihood value.

## Known limits

- **Fixed calibration.** Each grid is at one point of M0hat, sigma_M and n0. It measures how the likelihood's H0 width
  responds to the settings there. It is not a marginalised posterior.
- **The photometric redshift errors are not tested** (above).
- **The per-point variance rule is conservative for shape noise.** 12AJ found core's per-point variance overstates the
  shape noise 16 to 24 times at 3e-3. It also found core's PE variance about 20% low against the bootstrap. The
  limit of 2 is applied to core's per-point numbers, as in 12AG.
- **No replicates.** The noise floor of D2 against D0 exists only at 12AL's four cells. The bias test of D2 against
  D0 (12AL reading 1) is not repeated at the other 16 cells.
- **D2 assumes p_det isotropic** (algebra iii). Any real anisotropy of the selection is averaged out. 12AL found no
  bias at D0's noise level, and no isotropy signal, at four cells only.
- **Under D2 the nside axis tests only the PE side.** The selection term no longer sees pixels (algebra iv). That
  removes the selection noise, which was the point, but it also means the ladder under D2 cannot show a
  selection-side resolution effect.
- **Table nodes at the narrowest kernels.** Control 6 decides at each cell, with a declared refinement.
- **The upgraded nside-256 footprint** carries no information finer than nside 128. The nside axis is also mildly
  confounded with the area of covered pixels that hold no galaxy (12AG's covariate: 3.1% of the f_p-weighted
  footprint at nside 32, 6.3% at 256).
- **Two events were resampled with replacement upstream** (12AJ). Their PE variance is understated by both core and
  any bootstrap.
- **D1's shift** (12AL: −0.25 to −0.34 spectral sd) is reported as context. D1 is not a candidate here.

## Amendment B1 (2026-10-19): the build, before any production job

### Commits

Consumer branch `phase12am/d2-ladder` in `phase12_5/repo_12AM`, local only (not pushed), from 5c2a096:

| Commit | Content |
|---|---|
| `729d609` | the streamed D2 table, the table, cell and control-5 stages, the plan, the summary, the slurm scripts, the CPU tests |
| `8a08ae7` | test fixes; x64 checked after core's float64 modules load (CPU controls, control 5); a probe switch for the CPU job |
| `7a86caf` | control 5's synthetic footprint (B1.6); measured stage estimates; control 5 placed after its lane's first cell |
| `cbb1ae9` | the production submit drops dependency jobs that have left the queue (scheduling only) |

Files: `scripts/phase12am_{common,table,cell,control5,cpu,plan,summary}.py`, `slurm/phase12am_*`,
`tests/test_phase12am.py`. Nothing in `phase12/`, `phase12t_*`, `phase12ag_*`, `phase12ah_*` or `phase12al_*`
changed. Jobs run from `d2_ladder/worktrees/<sha>`, a detached worktree of a committed local sha, which must be
clean. **Production runs from `cbb1ae9`.** Its Python is that of `7a86caf`; only a shell script changed.

### Tests: 37 passed

On HENON (job 1390535, at 7a86caf): 17 new 12AM tests and 12AL's 20, all passing. On tiny synthetic inputs they
check:
- the streamed table equals 12AL's single pass to 1e-12, for one-chunk, two-chunk and default blocks (padded last
  blocks), with every block's g grid equal; the exact sum with g equals the per-row sum of core's evaluator;
- per-row values from block sub-views equal the whole view's, also with an active kernel window (sliced
  half-widths, the whole view's window size);
- D2 from the streamed table equals 12AL's D2 in ln mu and N_eff; the three-density call equals single calls;
- D2 = D0 on an identical-pixel catalog through the streamed path;
- controls 6 and 7 through the table stage's own functions, on 24,501 and 98,001 nodes;
- the four cases of the Monte-Carlo split, the declared change (a cell over the variance limit is never "no
  narrowing"), 12AG's washout rule on synthetic ladders, the verdict sentence (sizes and directions; it refuses
  "ruled out");
- the guard terms against 12AG's own `_guard_terms`, bit for bit (B1.4);
- the location guard, the plan, and the summary on a synthetic 20-cell root: it runs and is location-free; a ladder
  gate withholds every reading; a cell gate withholds that cell under D2 and D0; a D2 gate withholds only that
  cell's D2 reading; `STATUS.json` is always written.

### CPU controls (HENON, job 1390535 at 7a86caf; x64, clean tree): all pass

- **The streamed sum is 12AL's single pass on real rows.** At (64, 3e-3), 326 occupied rows in two blocks against
  12AL's `build_tables` on the same rows: 2.0e-15 relative. Eight rows from one-row sub-views against 12AL's whole
  occupied view: 7.3e-15.
- **Control 9's premises.** The four catalogs hold 22,785,279 galaxies each, all with unit weights. f̄ is equal bit
  for bit at nside 32, 64, 128 and 256. Core's kernel window is never active: its size equals the rows' slot count
  at every cell (5,180, 1,719, 774 and 569 at nside 32 to 256).
- **Block layout** (B1.2): 2, 3, 4 and 11 blocks of 4,727, 14,507, 32,274 and 43,847 rows. Kernel terms per table on
  24,501 nodes: 9.9e11, 1.3e12, 2.3e12 and 6.6e12.

### The nside-256 memory and speed probe on HENON CPU (job 1390531 at 729d609, 8 CPUs)

- One full block of 43,847 rows: load, the host view, the block's kernel state and three 163-row chunks.
- **Peak host memory 24.2 GiB** (`ru_maxrss`; 25.4 GB by `time -v`). The host view takes about 11 s, a block's
  kernel state about 23 s.
- 2.5e8 kernel terms per second on 8 CPUs: the whole table would take about 7.5 hours there. So the tables run on
  the cell's card, as declared. On an A100-40 the build measured 3.6e10 to 4.3e10 terms per second (below), so about
  3 minutes at nside 256.

### The short GPU control (twig A100-40; jobs 1390529 and 1390530 at 729d609)

**Table stage:**

| cell | blocks | T on 24,501 nodes | control 4 (S/N_pix; f̄, dN_exp, C̄, g) | control 6 | control 7 |
|---|---|---|---|---|---|
| (64, 3e-3) | 3 | 36 s | 2.2e-14; the others bit for bit | 4.5e-7 | 9.9e-15 |
| (128, 1e-3) | 4 | 53 s | 4.3e-14; the others bit for bit | 1.9e-6 | pass |
| (32, 3e-4) | 2 | about 27 s | not a 12AL cell | 7.0e-6 | pass |
| (32, 1e-4) | 2 | 27 s | not a 12AL cell | **1.5e-4 (fails) on 24,501 nodes; 1.1e-5 on 98,001** | 1.1e-14 |

- At (32, 1e-4), 4 of the 9,952 compared pairs exceeded 1e-4, all at z 0.009 to 0.012, where the value is 0.13% to
  0.19% of the table's maximum. There the sum is carried by few narrow spectroscopic kernels. The declared fallback
  (B1.3) rebuilt T on 98,001 nodes in 43 s and passed. S is the same at every nside (algebra iv), so the four other
  1e-4 cells are expected to take the fine table too.
- Device peak of a table stage: jax 3.2 to 3.4 GB, nvidia-smi 4.7 GB. Host memory 5.6 to 8.8 GiB.

**Lane A** at (64, 3e-3), on the five control points: **bit for bit** with 12AL's Lane A (ln L, ln mu, N_eff, the
correction, every ln Ẑ_i and σ_i², every theta). It ran on an A100-40; 12AL's ran on an A100-80.

**Cell stage** (control mode, the five control points):

| cell | 3(d): D0 against | 3(e) | 1(a): D0, D1, D2 against 12AL | 2(c): spectral against 12AL |
|---|---|---|---|---|
| (64, 3e-3) | this Lane A: bit for bit | bit for bit | bit for bit (relative difference 0) | bit for bit |
| (128, 1e-3) | 12AL's Lane A: bit for bit | bit for bit | bit for bit | bit for bit |
| (32, 1e-4) | 12AG's coarse grid: bit for bit | bit for bit (on the 98,001-node table) | not a 12AL cell | bit for bit |

- The in-lane spectral grid differs from 12AG's CPU reference by 9.1e-13 at most at these points.
- **Control 2(a)'s fallback** (a rerun on rita when an A100-40 differs from 12AL at rounding) was not needed here.
  Production decides it on all 641 points.

**Memory of the cell stage on an A100-40, and the routing rule** (the larger of nvidia-smi's peak and 1.6 × jax's
peak, against 34 GiB):

| nside | jax peak | nvidia-smi peak | rule value | route |
|---|---|---|---|---|
| 32 | 13.3 GB | 18.8 GiB | 19.8 GiB | any A100 |
| 64 | 14.1 GB | 20.8 GiB | 21.1 GiB | any A100 |
| 128 | 13.8 GB | 24.8 GiB | 24.8 GiB | any A100 |

So the routing stands as declared: nside 32 to 128 anywhere, nside 256 on rita only. No amendment of the routing is
needed.

**Speeds** (A100-40): the target build 15 to 24 s; three compiles of 83 to 103 s each (D0 single, D2 single, the
three-density call); then 0.253 s (nside 64), 0.255 s (128) and 0.305 s (32) per point for all three densities;
the spectral grid about 8 s.

### Control 5 (twig, jobs 1390533 at 8a08ae7 and 1390534 at 7a86caf)

- **As declared (1390533):** (64, 3e-3) passes (below the depth 1.1e-7, above 4.7e-13, sum 1.3e-10). (256, 3e-3) fails
  above the depth only: 9.8e-12 against 1e-12. Below the depth it is 3.0e-8 (tolerance 1e-4), the sum 2.0e-10, and
  no pattern mismatch.
- **Cause.** The synthetic footprint holds the plain mean f̄ in every pixel. D2's own cell mean (12AL's `bincount`
  over the N_pix equal values) adds them up with a rounding error of up to about N_pix × 1e-16. Above the depth that
  enters only where core's grid bracket straddles the depth (the lower node carries 1 − f C̄). The error scales with
  N_pix: 4.7e-13 at nside 64, 9.8e-12 at 256. It is a property of the test construction, not of the table path.
- **After B1.6 (1390534):** both cells pass. Above the depth the difference is 0.0. Below it is 1.1e-7 (64) and 3.1e-8
  (256). The sum is 1.3e-10 and 2.0e-10. The rounded f̄ differs from the plain mean by 3.5e-10 relative.
- **nside 256 is affordable:** 112 s on an A100-40, jax peak 7.5 GB, nvidia-smi 8.6 GB. So control 5 runs entirely
  in its A100-40 lane, nside 256 included.

### Departures from the declaration (implementation and scheduling; written before any production job)

**B1.1 The target is built once, under the scoped wrapper in identity mode.** 12AL built the stock target and then
rebuilt it under the wrapper (its control 1(a) found them bit for bit). Here the cell stage builds only the wrapped
target. Control 3(d) ties its D0 to Lane A (the stock target) at all 641 points. In the GPU control it was bit for
bit at three cells.

**B1.2 Blocks.** A block holds about 25 million slots (rows × the view's slot count), a whole number of 163-row
chunks, so its arrays and kernel state stay under about 4 GB (measured device peak 3.2 to 3.4 GB). The last block is
padded with empty rows, which add exact zeros. Core's kernel builder sees the block with core's galaxy list. The
per-sample evaluator sees it without the list: the evaluator does not read it, and its length varies by block,
which would recompile the evaluator.

**B1.3 Control 6's fallback runs inside the table stage.** If control 6 fails on 24,501 nodes, the same stage
rebuilds T on 98,001 nodes and repeats the control on the same 10,000 pairs. The cell stage then reads the fine
table. The declaration said the cell stage "reruns". Since the table stage runs first, the cell stage runs once.
The 24,501-node T is kept in the file as well, for control 4 and for control 9's table comparison.

**B1.4 Penalised points and the uncapped grid** use 12AG's definitions (`_guard_terms`). Core's correction is
called on the 641-point arrays, elementwise. A CPU test ties this to 12AG's scalar function bit for bit. The tests
"a penalised point inside I90" and "inside the uncapped coarse grid's 99% interval" are taken over all 641 points
(12AG had 241).

**B1.5 Controls 3(b) and 3(c)** are checked on every stage that ran: table, Lane A and cell. A stage that did not
run leaves its cell incomplete, which is a cell gate. Without this, one failed cell would have withheld every reading
through the ladder gate.

**B1.6 Control 5's synthetic footprint** holds f̄ rounded to 2^-30 in every pixel, so that D2's cell mean equals f_p
exactly. The identical-pixel premise then holds in floating point. The catalog, the injections, the points and the
tolerances are unchanged. The control also records that the cell mean equals f_p, and requires it.

**B1.7 x64 in the CPU scripts.** Core switches x64 on when its float64 modules are imported
(`darksirens/_jax.py`). The CPU controls and control 5 check x64 after that import, as every target process does.

**B1.8 Scheduling.**
- The planner gives the rita lanes a starting load (`RITA_OFFSET_MIN`) for their wait behind 1390498. With 15
  minutes, 12AL's (64, 1e-3) cell goes to rita0 and the other three to the A100-40 lanes.
- 1390499 completed at 21:46 UTC. A finished job leaves Slurm's controller after a few minutes, and a dependency on
  an unknown id is refused. So the submit script keeps only dependency jobs still in the queue (now 1390498).
- Control 5 is a 12-minute entry after the first cell of one A100-40 lane.

Nothing here changes a density, a cell, the grids, an input, a control's tolerance, a gate or a reading rule.

### The prepared production (not submitted)

- **Plan:** `d2_ladder/plans/production.json` (61 entries on 5 lanes, `RITA_OFFSET_MIN=15`). The submit script
  writes it again at submission.
- **Submit:** `RITA_OFFSET_MIN=<minutes until 1390498 ends> slurm/phase12am_submit.sh cbb1ae9`, from
  `phase12_5/repo_12AM`. It submits the five lanes and a HENON summary afterany on all of them, and prints a shell
  watcher for the main session.

| lane | card | cells, in order |
|---|---|---|
| rita0 | A100-80, after 1390498 | (64, 1e-3), (256, 3e-4), (256, 3e-3) |
| rita1 | A100-80, after 1390498 | (256, 1e-4), (256, 1e-3), (256, 1e-2) |
| twig0 | A100-40 | (128, 3e-3), (128, 1e-4), (64, 1e-4), (32, 3e-3), (64, 1e-2) |
| twig1 | A100-40 | (128, 1e-3), (32, 1e-4), (128, 1e-2), (32, 1e-3), (64, 3e-4) |
| henongpu | A100-40 | (64, 3e-3), control 5, (128, 3e-4), (32, 3e-4), (32, 1e-2) |

### Compute, revised from the measurements

| stage | nside 32 to 128 (A100-40) | nside 256 (A100-80) |
|---|---|---|
| table | 2 to 2.5 min; plus 1 to 3 min for the fine table at 1e-4 | about 5 min; plus about 13 min at 1e-4 |
| Lane A (641 points) | about 6 to 6.5 min | about 8 min |
| cell | about 8 to 8.5 min | about 12 min |
| **per cell** | **about 16 to 17.5 min** | **about 25 min (38 at 1e-4)** |

- **GPU total:** about 6.8 card-hours (408 card-minutes in the plan), within the declared 6 to 10.
- **Wall time:** the longest lane is about 1.4 to 1.7 hours (rita1, with the 1e-4 cell at nside 256), counted from
  when rita frees. The A100-40 lanes take about 1.3 to 1.5 hours from submission. Then the summary, 5 to 10 minutes.
- **On the clock:** if submitted about 22:45 UTC and 1390498 ends near 23:00, the summary is due about 00:45 to
  01:15 UTC on 2026-10-20. The range is 1.5 to 3 hours after submission. It is longer if 1390498 overruns, or if
  another user's job takes the free twig or henon-gpu card first.

### What could still block production

- **rita.** 1390498 still runs. Another user's rita jobs are queued with qos rita-s; qos rita preempts them by the
  cluster's policy, and nothing is cancelled by hand.
- **The free A100-40 cards.** Two twig cards and one henon-gpu card were free at the build. If fewer are free at
  submission, pass fewer lanes (`LANES="rita0 rita1 twig0 henongpu"`); the planner reassigns.
- **No blocking defect is known.**
