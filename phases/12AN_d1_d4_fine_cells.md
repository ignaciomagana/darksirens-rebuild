# 12AN — Every selection density at the four fine cells, in one pipeline (D0 to D3 rerun, D4 from the surrogate)

## Status

**DECLARED (2026-10-20, about 01:30 UTC), before any 12AN job.** This record fixes the cells, the densities, the
grids, the inputs, the controls, what is reported, and the compute. Nothing has run. The only things read for it are:
- records 12AK, 12AL and 12AM;
- core's source at e7c3007 (in the consumer env), the consumer's source at 698504a, and repo_12AK's source at 2b31955;
- location-free files: 12AM's and 12AL's cell records (timings, memory, table sizes), 12AK's training `STATUS.json`
  (epochs, losses, model sha256), the attributes and column names of the injection product;
- file sizes and sha256;
- the Slurm queue.

No absolute file was opened.

**The 12AK validation that D4 needs is declared in record 12AK, amendment B3** (record branch `phase12ak/declare`),
also before any job. That amendment fixes the synthetic-injection product that D4 reads.

**Blinding: location-free**, as in 12AG to 12AM. No H0 location appears here, in commit messages, in code comments,
in logs that agents read, or in any summary: no median, interval, MAP or shift in km/s/Mpc, and no count of grid
points inside an interval. The only H0 values in this record are fixed a priori:
- the coarse grid [20, 140] at step 0.5;
- the fine window [50, 100] at step 0.1;
- the five control points 50, 62.5, 75, 87.5 and 100;
- core's constant 67.74 (`KERNEL_PIN_H0_REF`), at which the catalog tables are built;
- from 12AK: the generation cosmology (67.9, 0.3065) and the window [50, 90] of its use-case checks.

Files holding absolute log-likelihoods or posteriors are written by jobs and are never opened by agents. This record
holds only their sha256.

**The owner's reporting rule (binding).** No frequentist decision machinery in what is reported: no bands
("narrows", "a hint", "no narrowing"), no z-scores, no p-values, no noise-floor tests, no random-subset ranks. The
summary reports numbers per cell and per density (listed below). Controls are numerical gates about correctness.
They are allowed, and they decide only what is withheld, never a reading.

**Experimental.** D2, D3 and D4 are not core options. Adopting one would be a core PR, and that is the owner's call.

## Why

- **The owner's override.** The production setting is nside 64 and sigma_kde 3e-3. The owner overrode it and wants a
  full matrix for each density: every density at the 2 × 2 cells nside {128, 256} × sigma_kde {1e-3, 1e-4}, at the
  12AG fixed calibration, population and events.
- **One pipeline.** 12AM ran D0, D1 and D2 at these cells. 12AL ran D3r, D3a and D3b at one of them, (128, 1e-3). They
  came from different code, different commits and different jobs. Here every density at every cell is rerun in one
  pipeline from one committed sha. So each 2 × 2 matrix is internally consistent. The earlier results become
  reproduction controls, compared in the jobs.
- **D3 at nside 256.** 12AL's per-pixel native table does not fit an 80 GB card at nside 256 (92.8 GB). 12AM's
  streamed table does. 12AN streams the D3 coarse-cell tables the same way.
- **D4.** Every D0 to D3 density reweights the same 1,067,946 real detected injections. D4 replaces them by about ten
  times as many synthetic detected injections, drawn from 12AK's trained flows. D4/D0 is the production density with
  less Monte-Carlo noise and no isotropy approximation. D4/D2 is D2's sky-averaged density on the same synthetic
  injections.

## The cells (fixed now)

| cell | nside | sigma_kde | catalog (sha256 prefix) | footprint | table nodes |
|---|---|---|---|---|---|
| ns128_sk1e-03 | 128 | 1e-3 | f26a20f0f3f8ca5a | native nside 128 | 24,501 (12AM's rule) |
| ns128_sk1e-04 | 128 | 1e-4 | f26a20f0f3f8ca5a | native nside 128 | 98,001 (12AM amendment B2.2) |
| ns256_sk1e-03 | 256 | 1e-3 | 66c50dc4ac1ea3ff | 12AG's upgraded copy | 24,501 |
| ns256_sk1e-04 | 256 | 1e-4 | 66c50dc4ac1ea3ff | 12AG's upgraded copy | 98,001 |

Cell order, wherever an order is needed (seeds, plans): ns128_sk1e-04, ns128_sk1e-03, ns256_sk1e-04, ns256_sk1e-03
(nside-major, sigma_kde ascending, as 12AM).

**Everything else is 12AG's ladder setting, unchanged (as 12AM):**
- calibration log10 n0 −1.8216 (h-scaled), M0hat −20.4975, sigma_M 0.5592, delta 0, z_depth 0.245, m_lim 21, the
  production k-correction;
- the population fixed as in the spectral-only reference (gamma 2.5439, mu_chi 0.04, sigma_chi 0.10, the other 14 at
  GWTC-5 values); Om0 0.3089, w0 −1, wa 0;
- the selection guard soft, variance limit 20; `core_numerics=core_defaults`, `kernel_pin=off`;
- the catalog at the cell's nside, 12AG's builds (the same 22,785,279 galaxies at every nside);
- PE: 259 events × 4,096 samples;
- real injections: 1,067,946 detected of 944,412,448 drawn;
- core e7c3007 in float64, through the consumer env `phase12t/envs/consumer_e7c3007_cuda12`, nothing installed into
  it.

Each target is built by `phase12t_common.build_target` exactly as 12AM's cell stage builds it.

## The densities (fixed now)

Eight densities per cell. Six reweight the real injections. Two reweight the synthetic ones.

| density | selection density at injection i | injections | earlier result (now a control) |
|---|---|---|---|
| **D0** | n_f(z, r_i): core's production field density in the injection's pixel | real | 12AM, all four cells |
| **D1** | dN_exp(z) = n0 a_pix g(z): the smooth model | real | 12AM, all four cells |
| **D2** | n̄(z): the mean of n_f over every sky pixel | real | 12AM, all four cells |
| **D3r** | the mean of n_f over the injection's native iso-latitude ring (511 rings at 128, 1,023 at 256) | real | 12AL, (128, 1e-3) only |
| **D3a** | the mean of n_f over the injection's nside-8 cell (768 cells) | real | 12AL, (128, 1e-3) only |
| **D3b** | the mean of n_f over the injection's nside-16 cell (3,072 cells) | real | 12AL, (128, 1e-3) only |
| **D4/D0** | as D0 | synthetic (12AK amendment B3) | new |
| **D4/D2** | as D2 | synthetic | new |

So D0, D1 and D2 are reruns at all four cells. D3r, D3a and D3b are reruns at (128, 1e-3) and new at the other three
cells. D4/D0 and D4/D2 are new everywhere.

**Common to all (12AL and 12AM).** At every H0,

ln μ_D = ln[(1/N_draw) Σ_i b_i(H0) n_D(z_i(H0), i)],

where b_i is the density-free part of core's weight (population, Jacobian, 1/prior weight). Then

ln L_D = Σ_e ln Ẑ_e − N ln μ_D + N(N+3)/(2 N_eff,D), plus core's soft-guard wall.

- The PE evidences Ẑ_e and their variances σ_e² are D0's at the same H0, from Lane A (core's stock target with the
  real injections). The PE side is the same for all eight densities.
- The correction is core's `selection_log_correction`, in x64, with Lane A's PE variance sum.
- D0's ln L in every difference uses D0's selection-only ln μ and N_eff (12AL amendment B2.3).

**Closed forms (12AL).** Below the depth:
- n̄(z) = dN_exp(z) [1 − f̄ C̄(z)] + S(z) / N_pix;
- n_D3(z, P) = dN_exp(z) [1 − f̄_P C̄(z)] + S_P(z) / m_P, with m_P the number of pixels in cell P.

f̄ and f̄_P are means of f_p over all pixels of the global footprint map (over the cell, for f̄_P). S_P(z) is the
catalog term summed over every occupied pixel of the global catalog inside P. S is the same sum over the whole sky.
Above the depth every density equals dN_exp(z), which is D0's value there.

### Algebra (12AL's and 12AM's, plus two statements)

- **(i) Normalisation.** For D2 and the three D3 variants the cells partition the sky, and every pixel of a cell
  carries the cell's mean. So Σ_p n_D(z, p) = Σ_p n_f(z, p) at every z. Nothing needs renormalising.
- **(ii) Identical pixels.** If every pixel has the same density, D2 and every D3 equal D0 term by term (control C5).
- **(iii) Isotropy.** D2 is unbiased when p_det is isotropic, or uncorrelated with the catalog's sky structure at
  each z. D3r needs only that p_det not depend on right ascension; D3a and D3b that it be constant within their
  cells. D4/D0 needs none of these: it is D0 itself, on other injections.
- **(iv) nside independence (12AM, extended).** With unit galaxy weights and the same galaxies at every nside:
  - D2's ln μ moves by a constant between nside 128 and 256, and its N_eff does not move (12AM control 9 passed);
  - **new:** the same holds for D3a and D3b. Their cells are fixed coarse pixels. Each injection's coarse cell is the
    same at both nsides. 12AG's upgrade gives every child pixel its parent's f_p, so each cell's f̄_P is the same.
    dN_exp and S_P/m_P both scale as (128/nside)². 12AL's control 6 measured 1.8e-12 nat for D3a and D3b between 64
    and 128;
  - D3r does not have this property: its rings are the native rings, which double in number from 128 to 256;
  - D4/D2 has it too (the same synthetic injections at both nsides).
- **(v) New: D4 pooling.** The D4 product is five members' equal shares (12AK amendment B3). Each member's file has its
  own count of draws, N_k,m = N_s,k,m / ξ_k, per campaign k, and every member has the same N_s,k,m. Write ω_i for a
  row's normalised weight, μ = Σ_i ω_i. In the pooled file each row's ω is its member's ω divided by 5. So, exactly:
  - μ_pool = (1/5) Σ_m μ_m;
  - Σ ω²_pool = (1/25) Σ_m μ_m² (1/N_eff,m + 1/ndraw_m), from core's 1/N_eff = Σ ω²/μ² − 1/ndraw;
  - 1/N_eff,pool = Σ ω²_pool / μ_pool² − 1/ndraw_pool.

  So the pooled D4 can be built from per-member evaluations. Control D4-C ties it to core's own evaluation of the
  pooled file.

## D4: what it is, and how each D4 number is made

**The synthetic injections** (spec in 12AK amendment B3):
- They come from the model that 12AK's U3 chooses: A (separate O3 and O4 flows) or B (one joint flow).
- Each of the five members contributes two chunks of draws, each chunk the size of the real detected set of each
  campaign. So **N_s = 10 × 1,067,946 = 10,679,460 flow draws in all** (model A: O3 811,170 and O4ab 9,868,290;
  model B: 10,679,460). The kept count, after 12AK's support drop and clipping, is reported (X1 requires at least
  99.5%).
- They are written in core's injection format, `gwcat-selection-2.0`: the real product's 16 columns and its
  attributes, with ndraw and the counts replaced. Core reads them with `ds.load_injections`, exactly as it reads the
  real file.
- The number is fixed now as the target. The build stage measures memory and speed (below). If a D4 stage does not
  fit, core's `sel_batch_size` is set first (a layout option: core documents it as a reassociation of the same sums,
  rtol 1e-12). N_s is lowered only if that fails, by an amendment before production, to the largest of 8, 6 or 5
  times the real count that fits. The number used is stated in amendment B1.

**How the numbers are made.**
- **Member entries.** For each cell and member: core's target built under 12AL's `patched_selection_density` with
  the member's file as the injection set and the PE stub. One jitted call per point evaluates D4/D0 and D4/D2 (one
  core `host_density_log_likelihood` per density, 12AL B1.1). D4/D2 uses the cell's streamed D2 table. All 641 union
  points.
- **Pooling.** By algebra (v), from (ln μ_m, N_eff,m, ndraw_m), in the summary.
- **ln L.** Lane A's PE side plus core's correction at the pooled ln μ and N_eff, as for every density.
- **The tie entry** (one per cell) checks the plumbing at the cell: controls D4-N, D4-P and D4-C below.

**What D4's variance figure means.** V_sel,D4 = N²/N_eff from core's estimator on the synthetic rows. It is the
Monte-Carlo variance of D4's estimate. It does not include the flow's own error. That error is what 12AK's X1, X2,
U1 and U2 measure.

**The label on every D4 number** (12AK's rule): D4 counts as a noise reduction only if X1, X2, U1 and U2 pass.
Otherwise every D4 number carries the label "systematic": its effect is then a systematic of the surrogate, reported
with its size and direction.

**Context: spectral only with the D4 injections (S/D4).** Core's spectral-only grid on the 641 points, with the
pooled D4 file as its injections. It is the same at every cell, so it runs once. It shows D4's own effect on a
posterior that has no catalog. It is reported beside the spectral-only reference (real injections).

## Implementation (declared now; the code is the build stage)

### The streamed tables: D2 and the three D3 variants in one pass

- **What is tabulated.** T_c(z_j) = S_c(z_j) / g(z_j), the catalog term without core's galaxy measure g, for every
  cell c of every table variant. This is 12AL amendment B4's factoring. It is computed as core's
  log N_obs + log p_cat − log g in log space (`catalog_term_pairs(..., without_g=True)`).
- **Evaluation.** As 12AL after B4 and 12AM: log-linear between nodes where both are positive, linear otherwise;
  multiplied by g(z) with core's `log_interp_zgrid` from the tables' own kernel state at 67.74; zero above the depth.
- **The stream.** 12AM's: the host view of every occupied row of the global catalog, core's kernel window sized once
  on the host, rows to the card in blocks with the whole view's slot count, core's kernel state per block, every
  block's `log_g_grid` equal to the first block's bit for bit.
- **Per chunk of rows,** two accumulations:
  - **D2:** 12AM's sum over the chunk's rows, by 12AM's code unchanged. So D2's table is 12AM's, bit for bit
    expected (control R1(a)).
  - **D3r, D3a, D3b:** a scatter-add of the chunk's rows into their cells (12AL's `build_tables` accumulation), the
    accumulators donated. Rows meet the cells in a different order than in 12AL's single pass, so the D3 tables equal
    12AL's to rounding (control R2(a)).
- **Cell maps:** 12AL's `cell_of_pixel` (healpy 1.19.0 in the consumer env): native RING rings for D3r; the parent
  pixel at nside 8 or 16 for D3a and D3b.
- **Nodes.** 12AL's 24,501 nodes (step 1e-5) and 12AM's 98,001 (step 2.5e-6), both ending at the depth.
  - **sigma_kde 1e-4:** every table on 98,001 nodes (12AM B2.2, extended to D3).
  - **sigma_kde 1e-3:** 24,501 nodes, unless control C6 fails for that variant at that cell. Then 98,001.
  - **Fallback, new:** a variant that still fails C6 is rebuilt four times finer again (392,001 nodes, step
    6.25e-7). If it fails there, that variant's numbers at that cell are withheld.
  - Reason for the fallback: at sigma_kde 1e-4 one isolated kernel on 98,001 nodes allows (h/σ)²/8 ≈ 7.8e-5 against
    the 1e-4 gate. The D3 cells hold fewer galaxies than the whole sky, so isolated kernels matter more there than for
    D2.
  - Every cell builds the 24,501-node tables at 1e-3 and the 98,001-node tables at 1e-4 whatever its numbers use.
    Controls R1, R2 and C9 compare those, so they always compare like with like.
- **Sizes on the card** (float64): at 98,001 nodes, D3b 2.41 GB, D3a 0.60 GB, D3r 0.40 GB (128) or 0.80 GB (256),
  D2 0.8 MB. At 392,001 nodes, D3b would be 9.6 GB.
- **Where.** A separate table process per cell on the cell's card, before the target is built. Output
  `runs/<cell>/table/tables.npz` (H0-free) with its sha256 in `table.json`. Later stages check the sha256.

**No native per-row table** is built (12AM). 12AL's control 3 (the native table equals D0) is not repeated. Its role is
covered by R2 (the D3 path equals 12AL's at the cell where 12AL's control 3 passed), C5 and C6.

### Selection-only evaluation

- 12AL's machinery, as 12AM: `patched_selection_density`, the PE stub, the tables as jit arguments.
- **Real injections:** one jitted call per point evaluates D0, D1, D2, D3r, D3a and D3b (12AL's six-density call).
- **Synthetic injections:** one jitted call per point evaluates D4/D0 and D4/D2.
- Members are padded with invalid rows (weight zero) to one shape, so one compile serves a cell's five members if
  the persistent compilation cache is used. A CPU test checks that the padding changes nothing.

### Lane A and the spectral grids

- **Lane A** is `phase12ah_a_scan.py` unchanged, core's stock target with every event's evidence, on the 641 union
  points (`--h0`), as 12AM.
- **Spectral only** is computed in the cell process on the 641 points with the real injections (12AL's
  `spectral_grid`), as 12AM.
- **S/D4** is the same function with the pooled D4 file, in its own entry.

## Grids (fixed now; 12AM's)

- **Coarse:** [20, 140] at step 0.5, 241 points.
- **Fine window:** [50, 100] at step 0.1, 501 points.
- **Union:** 641 distinct points; the 101 shared points have identical floats; both built as lo + step × arange.
- **Posteriors:** flat prior; a window posterior is normalised on the window, a coarse one on [20, 140].
- **The window rule (12AM, with B2.5):** a comparison of X against Y uses the window posteriors when both have coarse
  mass outside [50, 100] at most 1e-3 (the trapezoid over the window's own coarse nodes). Otherwise it uses the
  coarse grid. Only `window_holds` is written, never the mass.
- **Which code computes them:** window metrics with 12AL's functions, coarse metrics with 12AG's (12AM).

## Inputs (sha256)

All paths are under `/hildafs/projects/phy230054p/magana/darksirens-core-data`. Every sha256 was computed for this
record. Where 12AM, 12AL or 12AK recorded one, it is the same.

**Ladder inputs (as 12AM):**

| input | path | sha256 |
|---|---|---|
| catalog, nside 128 | `phase12_5/smearing_ladder/catalogs/desi_union_nside128.h5` | `f26a20f0f3f8ca5a9bc0aee0681cd0eba6f1a7b693055839cba83d6189cdb62c` |
| catalog, nside 256 | `phase12_5/smearing_ladder/catalogs/desi_union_nside256.h5` | `66c50dc4ac1ea3ffc593f8e19cc2baf3f0dd18c8a4953c77b10f262153a684d3` |
| footprint, native nside 128 | `phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| footprint, nside 256 (upgraded) | `phase12_5/smearing_ladder/catalogs/footprint/mth_map_nside256_from128.h5` | `c20e58e3b3570a5e131b3754002ea26024c43e647d3541ae9e1786fcdb181a67` |
| GW PE (259 × 4,096) | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| real injections (O3/O4) | `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| configuration | consumer `config/desi.fixed_population.json` at 698504a | `b79ad777f17126bcd78b9ebcff0d02724ae6cfe7ae957829009ca5143f349bb9` |
| spectral-only reference (12AG; population block) | `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json` | `db9f7b80c4b799c18559c99040916a821ed99aa7feb06fcec1d6589a171a6f9f` |
| 12AG catalog gates | `phase12_5/smearing_ladder/catalogs/gates.json` | `ec66534717536bdc3001572ab5ef7ee475e1bf45fc0d69a9a2be181b497eb2db` |

**12AM references** (under `phase12_5/d2_ladder/runs/<cell>/`; written by consumer 54d9815; read only by jobs, except
the location-free `controls.json` and `cell.json`):

| cell | `table/d2_table.npz` | `lane_a/scan.json` | `lane_a/events.npz` | `cell/variants.npz` |
|---|---|---|---|---|
| ns128_sk1e-03 | `59e6c69e22a6a075e0018d1e911ce522c3fbe96ab07ee59be3d7ebe0ccc60d67` | `faabe1c4a6264c6ceded5abae38ae1fd2c6229c886a33158a0b207a213efce7b` | `dc400d4150f6d76f7f9f91af47d5da7a08e3b7695365ec3349a2e8d9e8ac9a61` | `7afc83cf10307ca9be32a7a45ba29addbaf08169ff0b9206c668ab3165e89f3f` |
| ns128_sk1e-04 | `ac0106c8cbcc47273a77c59c78c190aa45f334ed9509ddcad133dd20fdd5240f` | `93b187bcfc833732bdc5049b70c5d3554c8ab0e34cf3d06edcc571abba95b439` | `972bdb6799a7d9405662137dff15ea91d3ccef0a028ca32199d4cd4d9b0e80a3` | `14f721a9cd862cd4c8183b1470bbe7de9cae63e54fc82182c7cad1227db35969` |
| ns256_sk1e-03 | `d19fb8633c391f123b142b7b229e8a7a87ec5cbb563fd1b420dbc683d388fe28` | `5317b51cbd124cf09dc19ca2ebe80d8e2059fd3fe991c03d163e8a02a4015bbb` | `b8d64aa17d70c4386900f6d6a07f32638b5ac0eab408547a22ac8e602e0ef10e` | `0eb717b02841565a027bb938ea9da7b49db06adc8724a5877c77c27e08406e41` |
| ns256_sk1e-04 | `4497a495166409481782ef4a1a8a34c47448eaefdc3ea6988403c1c2406e2981` | `bee1b528ef1f558ed26b92c310ff331efb3c4ca2c58152fb5fc4c5fe45dc4540` | `08d36b7dcaef7f8a04d905ef4bd01d4c32ff45890b6a11de4b5bc8fd5622f316` | `fe5aa30e548f5f65105c700e4fa9f0a94d974b56d16319fe46608d522b208d5b` |

- 12AM's in-lane spectral grid, `cell/spectral/spectral.npz`, is the same file at all four cells:
  `fd738c07367c34d8ab8b02e537e3ada4fc683805687b0bcfb1f8912fccd43067` (also 12AL's).
- 12AM `summary/summary.json` (location-free): `c82dde9ca5eeb5552c9befe99a7adf313eaf8c00f235d2630e17f1ab114af915`;
  `summary/controls.json`: `ef9e614a5be35aea01179f208c5b5c6d9dca842c3f71c30cf8169b5a58bbedd2`.

**12AL references at (128, 1e-3)** (under `phase12_5/selection_denominators/runs/ns128_sk1e-03/`; consumer 5c2a096):

| file | sha256 |
|---|---|
| `variants.npz` (ln μ and N_eff of D0, D1, D2, D3r, D3a, D3b) | `2b09bd14a3408ee730eff41bd61dd68ee5cfcec3885349aa722912459f492484` |
| `tables/tables.npz` (D2, D3r, D3a, D3b tables, f̄ per cell, `log_g_grid`) | `b8f39a26f5a651588ab5b3b9d6004e8217aa10f7f2b2b88b3a1829d2ae686107` |
| `lane_a/scan.json` | `5a0530d64fa552beb9a510ecfea2958e9e57fa2b7bdddbbb6f917305531cdf21` |
| `lane_a/events.npz` | `d3db17d77897bbb672b3b4ab7f1bc0002b8f79ab40188e2f1d684afa95424a9d` |

**12AG coarse grids** (context only; 12AM already tied them; under `phase12_5/smearing_ladder/runs/<cell>/scan.json`):
ns128_sk1e-03 `12b2c2b2d4edff4233b84f1b873d172d7dfced9235981b437e1d28c86a1638ce`, ns128_sk1e-04
`5c84d33ebfc59f36dba449283b0a6022e8e19bdfc8c403c349fde4f691b29840`, ns256_sk1e-03
`b4607602d5e79ee675069d314912ac6ca275e8e21e02d65b76291049be7e0d38`, ns256_sk1e-04
`47246b0b01d1a0979ca540fef9b61dd88a74f2717dd3270aec0d8ae4a8d29664`.

**12AK inputs** (the trained models and their status; under `phase12_5/pdet_surrogate/ours/`). The 16 `model.npz`
files, each equal to the sha256 in 12AK's `summary/STATUS.json`
(`edf9e5594953f95a7ddc8810a0e70bfe4efd4e535f351003257688d06811a7cb`), are listed in 12AK amendment B3. The
synthetic products are written by 12AK's writer; their sha256 go into 12AK's validation outputs, and every 12AN
stage checks them before use.

Every job checks the sha256 of each file it reads against this record and refuses a mismatch.

## Controls (fixed now)

**Kinds.**
- **Record gates:** a failure withholds every number of the record.
- **Cell gates:** a failure withholds every density's numbers at that cell.
- **Density gates:** a failure withholds the named densities' numbers where stated.
- **D4 gates:** a failure withholds D4/D0 and D4/D2 where stated.
- **Marks:** a failure is reported beside the named numbers. Nothing is withheld.

The summary always writes its numbers and `STATUS.json`, whatever fails. Withheld numbers are written as "withheld"
with the failing control. "Relative" below means |a − b| ≤ tol × max(|a|, |b|, 1) for log quantities and
|a/b − 1| ≤ tol otherwise.

### R1. 12AM reproduced at all four cells (cell gate; in the job)

Against 12AM's files (sha256 above):
- **(a) Tables.** The streamed D2 T on 24,501 nodes, and on 98,001 at 1e-4, against `d2_table.npz`; f̄ and
  `log_g_grid` too. Bit for bit expected (12AM's code path, unchanged). Gate: 1e-10 relative wherever above 1e-8 of
  the array's maximum.
- **(b) Lane A.** ln L, ln μ, N_eff, the correction, every ln Ẑ_e and σ_e², at all 641 points, against 12AM's
  `scan.json` and `events.npz`. Bit for bit expected. Gate: 1e-10 relative.
- **(c) The cell.** D0, D1 and D2: N ln μ and N_eff at all 641 points, against 12AM's `variants.npz`. The in-lane
  spectral grid (ln L, ln μ, N_eff, PE variance sum) against `spectral.npz`. Bit for bit expected: 12AL's GPU control
  found the six-density call equal to single calls bit for bit. Gate: 1e-10 relative.
- Whether each is bit for bit is reported. The largest difference is reported. D0's coarse ln L against 12AG's
  `scan.json` is reported, not gating.

### R2. 12AL's D3 reproduced at (128, 1e-3) (density gate: D3r, D3a and D3b at all four cells; in the job)

- **(a) Tables.** The streamed D3r, D3a and D3b tables on 24,501 nodes (T × g on the nodes, as 12AL stores them)
  against 12AL's `tables.npz`, and the cells' f̄. Gate: 1e-10 relative wherever above 1e-8 of the array's maximum.
- **(b) ln μ and N_eff.** N ln μ and N_eff of D3r, D3a and D3b at the five control points against 12AL's
  `variants.npz`. Gate: 1e-10 relative each. The largest difference over all 641 points is reported. D0, D1 and D2
  against 12AL are reported too.
- **Why it gates all four cells:** the streamed D3 path has no other external tie. A failure means the new path is not
  12AL's, wherever it runs.
- If C6 sends a D3 variant at (128, 1e-3) to finer nodes, R2 still compares the 24,501-node evaluation, which the cell
  stage then computes separately at the five points.

### C3. Per-event sum, x64, code, ties and walls (12AM control 3, extended)

- **(a) Cell gate.** Σ_e ln Ẑ_e + core's correction = ln L to 1e-9 at every Lane-A point.
- **(b) Record gate.** Every process records x64 on, and refuses to run otherwise. The flows of 12AK also run in
  float64 (12AK trained in x64; amendment B3).
- **(c) Record gate.** Every compute stage runs from a worktree of one committed sha with a clean tree: one consumer
  sha (repo_12AN) for every 12AN stage, and one repo_12AK sha for every 12AK validation stage. Only the summary may run
  from a later consumer commit, and only when the change touches the summary alone, by an amendment (as 12AM B3).
- **(d) Cell gate.** D0's selection-only ln μ and N_eff equal Lane A's to 1e-12 (absolute in ln μ, relative in
  N_eff) at all 641 points.
- **(e)** At the five control points, each density from its multi-density call equals a single call of that density
  to 1e-12. Cell gate for the six real densities (12AL B2.5). D4 gate for D4/D0 and D4/D2, checked in each cell's
  member-1 entry (the other members run the same code on other rows).
- **(f) Density gate at the cell.** |wall| ≤ 1e-9 at every window point, and total variance ≤ 20 at all 641 points,
  for every density except D0. D0's walls are reported (12AG's probe found a penalised D0 point at (128, 1e-4) at the
  coarse grid's lower edge).

### C5. Identical pixels (mark; 12AM control 5, extended to D3)

- 12AM's construction: every pixel holds the galaxies of the first occupied RING row whose count equals the median
  (185 at nside 128, 45 at 256); f_p = f̄ rounded to 2^-30 in every pixel (12AM B1.6).
- At nside 128 and 256, sigma_kde 1e-3, for D2, D3r, D3a and D3b against D0: the first 100,000 real injections at the
  five points; |ln n_D − ln n_f| ≤ 1e-4 below the depth and ≤ 1e-12 above; Σ_i n_D / Σ_i n_f within 1e-4 of 1; no
  finite-pattern mismatch.
- A failure marks that density's numbers at every cell.

### C6. Table accuracy (density gate per variant and cell; 12AM control 6, extended)

- At every cell and for each of D2, D3r, D3a and D3b: 10,000 random pairs. z is uniform on [0, 0.245]. For a D3
  variant, the cell is uniform among cells holding at least one occupied pixel (12AL B1.3).
- The table's value (T interpolated, times core's g) is compared with core's exact sum over the cell's galaxies,
  streamed the same way.
- Gate: maximum relative error ≤ 1e-4 wherever the value exceeds 1e-8 of the cell's maximum, for z ≥ 1e-3. Pairs below
  1e-3 are reported.
- Seeds: for D2, 12AM's at these cells (5111, 5113, 5116 and 5118), so D2's pairs repeat 12AM's. For D3r, D3a and D3b,
  6101 + 3 × (cell order) + (0, 1, 2), that is 6101 to 6112.
- A failure starts the node fallback above. The variant's numbers at that cell are withheld only if 392,001 nodes fail.

### C7. Kernel H0 invariance (cell gate; 12AM control 7)

At every cell, the catalog term of 64 spread rows on the table nodes, built at H0 = 50, 67.74 and 100, agrees to 1e-10
relative wherever above 1e-8 of its maximum.

### C8. D1 is spectral only up to a constant (mark; 12AM control 8)

ptp over the window of N[ln μ_D1 − ln μ_spec] ≤ 0.01 nat, and |N_eff,D1/N_eff,spec − 1| ≤ 1e-4 at every point. The
tolerances are 12AL's. 12AL and 12AM missed them narrowly at every cell (0.0101 nat and 3.0e-4), from interpolating
dV_c/dz on two grids. A failure marks D1's numbers, and the shares removed (D1 is their floor).

### C9. nside independence, 128 against 256 (density gate for D3a and D3b at nside 256; mark for D2 and D4/D2)

At each sigma_kde, for D2, D3a, D3b and D4/D2:
- G = ptp over the window of N[ln μ_D(256) − ln μ_D(128)] ≤ 1e-6 nat;
- max |N_eff,D(256)/N_eff,D(128) − 1| ≤ 1e-10 over the 641 points.

Computed in the summary, on the node counts every cell builds (24,501 at 1e-3, 98,001 at 1e-4). Why it gates D3a and
D3b at 256: those tables have no external reference, and this ties them to nside 128, which R2 ties to 12AL. D2 is
already tied at both nsides by R1. A failure for D4/D2 marks its numbers.

### D4 gates and checks

**P. The plumbing gate (12AK amendment B3).** Real detected rows through 12AK's synthetic writer must reproduce the
H0-shape of the real product's spectral-only ln μ over the 241 coarse points to ≤ 1e-6 in core. **If it fails or does
not run, no D4 entry runs.** D4/D0, D4/D2 and S/D4 are then written "not run: plumbing gate".

At each cell, in the tie entry:
- **D4-N (D4 gate at the cell).** The stored-input null product (12AK B3: the real rows with their own densities,
  distances, sky positions and weights, through the writer) is evaluated through the D4 path at the five control
  points. Against this run's real-injection D0 and D2 at the same points:
  - ptp over the five points of (ln μ_null − ln μ_real) ≤ 1e-6, for D0 and for D2;
  - |N_eff,null/N_eff,real − 1| ≤ 1e-6 at each point.

  This checks the file format, the conventions and the sky columns through the catalog path at every cell.
- **D4-N′ (mark).** The same with the synthetic-path null product (distances, detector masses and pdraw recomputed from
  the 13 inputs, as for flow samples). Reported, not gating. Reason: the recomputed distances differ from the stored
  ones by up to 1.6e-7 relative (12AK B1, gate G3). At sigma_kde 1e-4 the per-pixel density is spiky in z, and such a
  shift can move single injections' densities at the 1e-4 level. That is a property of the coordinates, not of the
  plumbing.
- **D4-P (D4 gate at the cell).** Core's stock target built with the pooled D4 file: at the five points, every ln Ẑ_e
  and σ_e² equals Lane A's to 1e-10 relative. The injection file must not change the PE side. This justifies using
  Lane A's PE side for D4.
- **D4-C (D4 gate at the cell).** The same stock target: at the five points, its selection ln μ and N_eff equal the
  members' pooled values (algebra v) to 1e-10 relative, and its ln L equals Σ_e ln Ẑ_e + core's correction at the
  pooled values to 1e-9. This ties the per-member path to core's own evaluation of the whole file.
- **Order.** A member entry checks the D4 product's sha256 and the plumbing result before it runs, and refuses
  otherwise.

**Numerical checks of the surrogate (12AK amendment B3): X1, X2, U1 and U2.** They are reported beside every D4
number, and they set its label: "noise reduction" if all four pass, "systematic" otherwise. **U3** picks the model.

### What gates what (summary)

| control | kind | what a failure withholds or marks |
|---|---|---|
| R1 | cell gate | every density at that cell |
| R2 | density gate | D3r, D3a, D3b at all four cells |
| C3(a), C3(d), C7 | cell gate | every density at that cell |
| C3(b), C3(c) | record gate | everything |
| C3(e) | cell gate (real) / D4 gate (D4) | the cell, or D4 at the cell |
| C3(f) | density gate | that density at that cell |
| C5 | mark | that density everywhere |
| C6 | density gate (after the node fallback) | that variant at that cell |
| C8 | mark | D1, and the shares removed |
| C9 | density gate / mark | D3a, D3b at nside 256 / D2, D4/D2 marked |
| P | D4 gate | D4/D0, D4/D2 and S/D4 everywhere (not run) |
| D4-N, D4-P, D4-C | D4 gate | D4 at that cell |
| D4-N′ | mark | D4 at that cell |
| X1, X2, U1, U2 | label | every D4 number: "noise reduction" or "systematic" |

**Stopping.** A cell stage checks C3(d) at the five control points first, and stops before its 641 points if it
fails (12AM). No other control stops a job. Every failure is decided by the summary.

## What is reported (fixed now; every number location-free)

**Notation.** p_X is the posterior of density X (window or coarse, by the window rule). I90_X is its central 90%
interval, used inside jobs only and never printed. "Spectral" is the in-lane spectral-only grid (real injections).
H is the Hellinger distance. N = 259. Variances are core's estimators.

**Per cell and per density** (D0, D1, D2, D3r, D3a, D3b, D4/D0, D4/D2), the summary writes:
1. **Var ln L, selection:** V_sel = N²/N_eff, its maximum over the union-grid points inside I90 of the density's own
   posterior.
2. **Var ln L, PE:** V_PE = Σ_e σ_e² (the same curve for every density), its maximum over the same points.
3. **Var ln L, total:** V_tot = V_PE + V_sel, its maximum over the same points.
4. **The share of the catalog-added selection variance removed:** φ_D = (V90_D0 − V90_D)/(V90_D0 − V90_D1). Here
   V90_X is the maximum of V_sel,X over I90_D0, so all three are taken at the same H0 (12AL's convention). D1 is the
   floor. φ above 1 means the density's selection variance is below D1's: possible for D4, which has ten times the
   rows. The denominator is written beside it.
5. **Width against spectral only:** R, the 68% half-width ratio; and the sd ratio.
6. **Median shift, in spectral-only sd:** against D0 at the same cell, (median_D − median_D0)/sd_spec; and against
   spectral only, (median_D − median_spec)/sd_spec. Only these ratios are written.
7. **Hellinger distance** from spectral only, and from D0 at the same cell.
8. **Roughness (supplemental; decides nothing):** on the window, the rms of the second difference of ln L_D − ln L_spec
   at step 0.1 (499 values), and the same for its PE part and its selection part (12AM item 5's window form).
9. **Bookkeeping:** the grid used for each comparison (window or coarse; `window_holds` per density), table nodes per
   variant, blocks, device memory, seconds per stage (`p50_seconds`, never "median"), the commit of every stage.

**Beside every D4 number:** the model (A or B), N_s drawn and kept, X1 (the smallest over members), X2 (four ratios),
U1 (S_W on [50, 90] and on [50, 100], per event and times N in nat), U2, the plumbing result, D4-N, D4-N′, D4-P,
D4-C, and the label. Also, as context, the spread over the five members at the cell: the sd over members of the
window-detrended N ln μ_D4,m, its maximum over the window. It includes each member's own Monte-Carlo noise (2.14
million rows each).

**Context rows:** S/D4 against spectral only (items 5 to 7). D0's coarse ln L against 12AG's (R1).

**Per sigma_kde column:** C9's G and N_eff ratio for D2, D3a, D3b and D4/D2, and the Hellinger distance between
nside 128 and 256 for every density.

**The absolute file** `summary/absolute.npz` (written by the summary job; never opened by agents): for every cell and
density, and for spectral only and S/D4, the posterior on the 501-point fine window (normalised on the window), the
posterior on the 241-point coarse grid, and the per-point ln L, ln μ, N_eff and PE variance sum. The fine-window
posteriors are for the owner's plot.

**Not written, by the owner's rule:** no R band or other band, no "narrows", "a hint", "no narrowing" or "limited by",
no washout verdict, no z-score or p-value, no noise floor, no replicate ranks. 12AM's reading code is not called.

**The location guard:** 12AM's `FORBIDDEN_KEYS` (12AJ's and 12AL's names, and 12AM B2.1's
`n_union_points_in_I90`, `n_trigger_points`, `mass_outside_window`, `coarse_mass_outside_window`, `mass_outside`),
and no float equal to any absolute posterior location. Every write that would hold one is refused. Timing fields are
named `p50_seconds` where they are written (12AM B3), never "median".

## Compute (estimate)

### The entries

Every entry is its own process with a DONE marker, so a resubmitted lane continues. Minutes are on one card, from
12AM's measured stages (A100-40 at nside 128, A100-80 at 256), scaled where new work is added.

| entry | per | nside 128 | nside 256 | basis |
|---|---|---|---|---|
| table: D2 + D3 stream, R1(a), R2(a), C6 for four tables, C7 | cell | 6 (1e-3), 12 (1e-4) | 10 (1e-3), 22 (1e-4) | 12AM: 2–5 min at 128; 134 s plus 271 s for the fine table at (256, 1e-4); D3 adds three scatter-adds and three C6 sums |
| Lane A, 641 points | cell | 6.5 | 8 | 12AM, unchanged |
| cell: six densities, spectral, R1(b, c), R2(b), C3 | cell | 14 | 18 | 12AM 8–12 min, plus three more single-density compiles (12AL B2.5) |
| control C5 (four densities, two nsides) | once | 15 (one A100-40) | | 12AM: 112 s for D2 alone at 256 |
| D4 member: two densities, 641 points, 2.14 M rows | cell × member | 8 (member 1: 11) | 10.5 (member 1: 13.5) | 0.25 s (128) and 0.345 s (256) per point at 1.07 M rows, scaled by 2; compiles 80–100 s |
| D4 tie: D4-N, D4-N′, D4-P, D4-C at five points | cell | 12 | 15 | a stock build and compile with the 10.7 M file |
| S/D4: spectral, 641 points, 10.7 M rows | once | 5 | | 12AM: 8 s for 641 points at 1.07 M rows |
| 12AK validation entries (amendment B3) | once | about 120 card-minutes, 40 of them CPU work on a lane's node | | 12AK B3 |

**Card totals:**
- real-injection work: 26.5 + 32.5 + 36 + 48 ≈ 143 min, plus C5 15 min: **about 2.6 card-hours**;
- D4: 2 × (5 × 8 + 3 + 12) + 2 × (5 × 10.5 + 3 + 15) + 5 ≈ 256 min: **about 4.3 card-hours**;
- 12AK validation: **about 2 card-hours**;
- **in all, about 9 card-hours (range 7 to 14).** 12AM used about 6.8.

### Lanes (the owner approved all eight cards)

- **rita0, rita1** (A100-80): `-p RITA-GPU --qos rita -A phy220048p --gres=gpu:a100-80:1 --cpus-per-task=128
  --mem=120G --time=7-00:00:00`. Another user's standby (`rita-s`) jobs run there at 01:16 UTC. Qos rita preempts
  them by the cluster's policy. Nothing is cancelled by hand.
- **twig0 to twig3** (A100-40, one lane per card): `-p TWIG-GPU --qos twig -A phy220048p --gres=gpu:a100-40:1
  --cpus-per-task=32 --mem=120G --time=2-00:00:00` (twig's maximum). At 01:04 UTC another user holds two of the four
  cards (jobs with 12-hour and 2-day limits).
- **henongpu0, henongpu1** (A100-40): `-p HENON-GPU --qos henon-gpu -A phy220048p --gres=gpu:a100-40:1
  --cpus-per-task=64 --mem=240G --time=7-00:00:00`. At 01:04 UTC other users hold both cards; one job ends by about
  02:25 UTC (its limit), the other may hold its card for up to about 1.25 days.
- **Summary** on HENON CPU: `-p HENON --qos henon -A phy220048p --time=7-00:00:00 --exclude=henon06,henon08`, 8 CPUs,
  `--dependency=afterany` on every lane. It runs 12AK's validation summary first, then 12AN's. It always writes both
  `STATUS.json` files.
- The lanes set `XLA_PYTHON_CLIENT_MEM_FRACTION=0.92`, XLA preallocation off, `XDG_CACHE_HOME` and `CUDA_CACHE_PATH`
  on the project disk (12AM B2.9). No cache in the home directory. Nothing is installed into a shared env.
- **Not used:** MIKO (no job and no step; job 1388940 is not touched) and js2h100.

### Scheduling: one pool, pulled by eight lanes (departure from 12AM's fixed assignment)

- **What.** Every entry, 12AK's validation entries included, is in one plan. Each entry names its prerequisites (DONE
  markers), its card class and its priority. Each lane repeatedly claims the highest-priority entry it may run whose
  prerequisites are DONE (an atomic `mkdir` claim holding the job id). It runs it as its own process, with that
  entry's interpreter and worktree.
- **Why.** The owner wants every card busy. At 01:04 UTC other users held four of the eight cards (two twig, both
  henon-gpu) until unknown times, and rita's two ran standby jobs. A fixed assignment would leave work stranded on a
  lane that has not started. A dependency chain of separate Slurm jobs would leave our own lanes holding the cards
  that the validation needs. With a pool, a lane that starts late takes whatever remains, and a lane that finds
  nothing left exits at once.
- **The dependency order is the declared chain:** 12AK sampling → writing (and the null products) → the plumbing gate
  and the numerical checks → the model choice → the D4 entries → the summary (afterany). D4 member entries also need
  their cell's table. A tie entry needs its cell's Lane A and cell stage.
- **Priority:** the 12AK validation chain first (it is the critical path); then the nside-256 work on the A100-80s;
  then the rest, longest first.
- **Routing (12AM's rule):** a stage goes to an 80 GB card when the larger of nvidia-smi's peak and 1.6 × jax's peak
  is above 34 GiB, or when it ran out of memory on a 40 GB card. nside-256 table, Lane A and cell stages go to rita
  only (12AM measured 50 GB at 256). rita lanes take 80-GB-only entries first. Whether D4 member and tie entries at
  nside 256, and the new nside-128 stages, fit a 40 GB card is measured in the build; the plan follows the
  measurement.
- **CPU entries** (12AK's writer and V1/V2) run on a lane's node CPUs (32 to 128 CPUs per lane). That card idles for
  about 20 minutes each time. This avoids queueing on HENON, which is nearly full.
- **Waiting and exit.** A lane with nothing claimable while some entry waits on a running prerequisite checks again
  every 60 s. An entry whose prerequisite failed, or whose claiming job ended without DONE twice, is "blocked" and is
  not waited for. A lane exits when nothing is runnable or pending.
- **The end.** The lane that finds the pool finished cancels this record's own still-pending lane jobs (only ours,
  only PENDING, by the job ids in `plans/jobs.json`), so the summary's afterany is not held for a day by a lane queued
  behind another user's job. These cancellations are recorded in `plans/cancelled.json`. Other users' jobs are never
  touched.
- **The watcher** is a shell until-loop held by the main session (12AM B2.10). It ends on the summary's
  `STATUS.json`, or on a running job in a failure state. It ignores the lanes listed in `plans/cancelled.json`. No
  agent polls.
- CPU tests cover the claim, the priorities, the routing, blocking, and the exit and cancel rule.

### Estimated time to completion

- **Build stage first:** code, CPU tests, a short GPU control, and a review. New: 12AK's validation code (sampler,
  writer, null products, distances, X1, X2, U0 to U3), the streamed D3 tables and controls, the D4 member and tie
  entries, S/D4, the pool lanes, and the summary's metrics. About **3 to 6 hours of agent time**. The short GPU control
  (about 45 minutes on one A100-40 and one rita card) measures the new stages' memory and speed at nside 128 and 256,
  including D4 at 10.7 million rows. Not counted in the card total.
- **Production, after submission,** assuming the cards free at 01:04 UTC (both rita cards after preemption, two twig
  cards) plus the henon-gpu card whose job ends by about 02:25 UTC, so four to five cards:
  - the 12AK validation chain and the model choice: about 1 to 1.3 hours;
  - meanwhile, the real-injection work on the other cards: about 2.6 card-hours, done by about 1.3 hours;
  - then D4: about 4.3 card-hours on four to five cards, about 1 to 1.3 hours. If the nside-256 D4 entries must stay
    on 80 GB cards, they load rita with about 2.4 card-hours (about 1.2 hours on its two cards); then rita sets the
    end;
  - then the summaries: about 10 minutes, if HENON has 8 CPUs free.
- **So about 3 hours from submission to the summary** (range 2.5 to 5 hours). More cards freeing earlier shortens it
  (about 2 hours with all eight). It is longer if rita's standby jobs are not preempted at once, if a D3 table needs
  392,001 nodes (up to about 40 more minutes at nside 256), or if HENON queues the summary.
- **On the clock:** declared at about 01:30 UTC on 2026-10-20. If the build and review end by about 05:00 to 07:30
  UTC, the summary is due about **08:00 to 10:30 UTC on 2026-10-20** (range to about 13:00 UTC).
- The 7-day and 2-day limits are ceilings, not the estimate.

## Code (the build stage; nothing written yet)

**Consumer repo** `phase12_5/repo_12AN`: a clone of `phase12_5/repo_12AM`, with origin set to repo_12AM's GitHub
remote (`ignaciomagana/desi_darksirens_selection`). Branch `phase12an/d1-d4` was created at 698504a when this record
was declared. It has no commits yet. Local commits only; the main session pushes.

Planned files:
- `scripts/phase12an_common.py`: the cells, the eight densities, the streamed D2 + D3 tables (12AM's stream and 12AL's
  cell maps and densities reused, not changed), the node rule and fallback, the D4 pooling algebra, the metrics, the
  location guard;
- `scripts/phase12an_table.py`: the table stage (R1(a), R2(a), C6, C7);
- `scripts/phase12an_cell.py`: the cell stage (six densities; spectral; R1(b, c), R2(b), C3);
- `scripts/phase12an_d4.py`: the D4 member entry and the tie entry (D4-N, D4-N′, D4-P, D4-C), and S/D4;
- `scripts/phase12an_control5.py`: C5;
- `scripts/phase12an_pool.py`: the plan, the pool, the lane loop, the claim and exit rules;
- `scripts/phase12an_summary.py`: C8, C9, the pooling, every reported number, `absolute.npz`, `STATUS.json`;
- `slurm/phase12an_*`: the lane, the summary, the submit script with its watcher;
- `tests/test_phase12an.py`: CPU tests on tiny synthetic inputs. Among them: the D3 stream equals 12AL's single pass to
  rounding and the D2 sum equals 12AM's bit for bit; D3a and D3b scale exactly between two nsides; the pooling algebra
  equals one call on the concatenated rows; padding with invalid rows changes nothing; the summary writes no band,
  reading or verdict, and withholds correctly for each gate kind; the location guard; the pool's rules.

Nothing in `phase12/`, `phase12t_*`, `phase12ag_*`, `phase12ah_*`, `phase12al_*` or `phase12am_*` changes. Lane A runs
`phase12ah_a_scan.py` unchanged.

**repo_12AK** `phase12_5/repo_12AK`: a new branch `phase12ak/validation` from 2b31955, for the validation code and the
writer (12AK amendment B3). Local commits only.

Every job runs from a clean worktree of a committed sha: `d1_d4_fine/worktrees/<sha>/` for the consumer and
`pdet_surrogate/ours/worktrees/<sha>/` for repo_12AK.

## Outputs

Under `phase12_5/d1_d4_fine/`:
- `plans/`: the plan, `jobs.json`, `cancelled.json`; `pool/`: the claims.
- `runs/<cell>/`:
  - `table/`: `tables.npz` (H0-free) and `table.json` (location-free);
  - `lane_a/`: `scan.json`, `events.npz`. Absolute: not for agents;
  - `cell/`: `variants.npz` (ln μ and N_eff per density and point) and `spectral/`. Absolute: not for agents;
  - `d4/m1` … `d4/m5`: each member's ln μ and N_eff per density and point. Absolute: not for agents;
  - `d4/tie/`: the D4 controls, location-free;
  - `controls.json`, `cell.json`: location-free.
- `spectral_d4/`: S/D4's grid. Absolute: not for agents.
- `controls/control5/`: location-free.
- `summary/`: `summary.json`, `controls.json` and `STATUS.json` (location-free, guarded); `absolute.npz` (not for
  agents).
- `logs/`, `worktrees/`, `.cache/`.

12AK's validation outputs go under `phase12_5/pdet_surrogate/ours/validation/` (12AK amendment B3).

Printed progress carries no likelihood value.

## Known limits

- **Fixed calibration.** Each grid is at one point of M0hat, sigma_M and n0. It is not a marginalised posterior.
- **The photometric redshift errors are not tested** (12AG).
- **D2 and D3 assume p_det isotropic, or isotropic within their cells.** Any real anisotropy finer than the cells is
  averaged out. 12AL found no bias at D0's noise level at four cells.
- **D4 inherits the flow's error.** Its Monte-Carlo variance is small, but the flow's own error does not fall with
  more samples. 12AK's U1 bar is per event: 3e-3 in the H0 shape of ln μ over [50, 90]. Times N = 259 it allows an
  H0-dependent change of ln L of up to about 0.8 nat there. That is larger than some differences D4 is meant to
  resolve. So U1 is also reported times N, and S/D4 shows D4's own effect on a posterior directly.
- **The flow's sky dependence is the run-averaged one.** The flows do not see time or phase (12AK). So right
  ascension is averaged over the Earth's rotation, as it is for the real injections in expectation. D4/D0 has no
  isotropy approximation, but its sky structure is what the flow learned, mostly in declination.
- **D4 rests on the real injections.** The flows were trained on the same 1,067,946 detected rows. D4 smooths their
  noise; it cannot add information about p_det that they do not hold.
- **Under D2, D3a, D3b and D4/D2 the nside axis tests only the PE side** (algebra iv). D0, D3r and D4/D0 keep pixel
  structure in the selection.
- **The upgraded nside-256 footprint** carries no information finer than nside 128 (12AG).
- **Two events were resampled with replacement upstream** (12AJ). Their PE variance is understated.
- **D1's known shift** (12AL: about −0.3 spectral sd) is reported as it comes out. D1 is the floor of the shares
  removed, not a candidate.

## Amendment B1 (build stage and review fixes), 2026-10-20, before any production job

Written before the production submission. Nothing here was read from an absolute file. Every number below is a
deviation, a time, a memory figure, a count or a gate result.

### B1.1 What was built

**Consumer** `phase12_5/repo_12AN`, branch `phase12an/d1-d4` from 698504a (local commits; the main session pushes):
- D0 to D3: 8317e58, 3b5b388, c12c5b5, c1a27e7. Files `scripts/phase12an_{common,table,cell,control5,plan_d03}.py`,
  `tests/test_phase12an.py`, and the build-control scripts in `slurm/`.
- D4: 3de5efc, 81a6622, 72116ea, 28b9639, 7097130, 8054532, 8fdbe71. Files `scripts/phase12an_d4.py` (modes member,
  tie, spectral, measure), `scripts/phase12an_plan_d4.py`, `tests/test_phase12an_d4.py`.
- Review fixes: d3cbd97, cabb3b6 and cb7c638 (this amendment). New files `scripts/phase12an_pool.py`,
  `scripts/phase12an_summary.py`, `tests/test_phase12an_pool.py`, `tests/test_phase12an_summary.py`, and in `slurm/`
  the lane, the HENON fallback summary, the submit script, the watcher check, the final CPU tests and the D4 smoke.
- Nothing in `phase12/`, `phase12t_*`, `phase12ag_*`, `phase12ah_*`, `phase12al_*` or `phase12am_*` changed.

**repo_12AK** branch `phase12ak/validation` from 2b31955: ec2e3eb, 9173947, 170fae2, a136a28, 00eb483, c8d29e4 and
ad0c0b9 (this amendment). The validation code of 12AK amendment B3 (`phase12ak/{writer,sampling,validation,
core_eval,vcommon}.py`, `scripts/phase12ak_{sample,write,v1v2,core_null,core_model,choose,validation_summary}.py`).

The production shas are stated in the Production section. Every stage runs from a clean worktree of one of them.

### B1.2 Build checks (not results)

**D0 to D3, GPU control** (cell stages in control mode, tied to 12AM's Lane A):
- R1(a): the streamed D2 table equals 12AM's bit for bit at (128, 1e-3), (128, 1e-4) and (256, 1e-4), both node
  counts, with f̄, the g grid, dN_exp and C̄.
- R2(a) at (128, 1e-3): D3r, D3a and D3b equal 12AL's tables to 1.1e-15, 1.1e-15 and 9.7e-16 relative; f̄ and m bit
  for bit.
- R1(c) (D0, D1, D2 and the spectral grid against 12AM) and R2(b) (D3 at the five points against 12AL): bit for bit.
- C3(d) and C3(e): bit for bit at the five points, all six densities.
- C6: D2 fails on 24,501 nodes at sigma_kde 1e-4 (as in 12AM) and passes on 98,001. D3r and D3a pass on 98,001 (7.8e-5
  to 9.0e-5 against 1e-4). D3b fails on 98,001 at both nsides and passes on 392,001 (1.2e-5 and 9.1e-6). The declared
  fallback works; the `--d3-fine-base` switch stays off.
- C7 1.4e-14. C5 passes at both nsides for all four variants.

**D4, build checks** (12AK's full-size build tree; not the validation):
- The plumbing gate's null_P shape: 3.9e-9 against 1e-6. The level 7.1e-8, N_eff 4.7e-8, null_S shape 5.2e-9.
- D4-P preview: the stock target with a pooled synthetic file gives Lane A's PE side bit for bit at the five points.
- A 5%-scale end-to-end run of the whole 12AK chain ran every step to exit 0. The pooled file against the algebra:
  4e-15.
- X1 on one full-size chunk: A_O3 member 1 0.9495, A_O4 member 1 0.9993, B members 0.9943 to 0.9958. If production
  confirms this, no model passes X1, U3 compares two failing models, and every D4 number is labelled "systematic".

**CPU tests** (each at its commit): 48 D0 to D3 and 12AM/12AL tests; the D4 tests; 12AK's validation and core-load
tests. The final run at the production shas is in the Production section.

### B1.3 Memory, speed and the injection count

| stage | card | time | routing value (GiB) |
|---|---|---|---|
| table (128, 1e-3) | A100-40 | 2.6 min | 6.1 |
| table (128, 1e-4) | A100-40 | 9.6 min | 24.6 |
| table (256, 1e-4) | A100-80 | 25.3 min (13.6 of it the 392,001-node pass for D3b) | 24.6 |
| cell (128, 1e-3) | A100-40 | 7 compiles of 71 to 105 s, then 0.255 s per point | 24.8 |
| cell (256, 1e-4) | A100-80 | 0.348 s per point | 64.8 |
| cell (128, 1e-4) | A100-40 | out of memory building the 392,001-node D3b table | (32.8 before) |
| D4 member, 2.1 M rows | A100-40 at 128 / A100-80 at 256 | 0.286 / 0.365 s per point | 24.8 / 58.1 |
| D4 stock target, 10.6 M rows, sel_batch_size 2^20 | A100-40 at 128 | 0.41 s per point | 25.9 |
| D4 stock target, unbatched | A100-80 at 256 | 0.51 s per point | 101 (too close to the card) |

The routing value is the larger of nvidia-smi's peak and 1.6 × jax's peak (12AM's rule).

**N_s used: 10,679,460 draws** (10 × 1,067,946, two chunks from each of the five members), as declared. It fits
with no reduction. In the build probe of model B, 10,627,184 draws were kept (99.51%).

### B1.4 Departures (each before any production job)

1. **The (128, 1e-4) cell stage runs on an 80 GB card.** It ran out of memory on an A100-40 in the build (12AM's
   rule). All nside-256 work stays on rita.
2. **D4 members are not padded to one shape.** The record said they would be, with a CPU test. The target's compact
   catalog view holds the pixels of the PE samples and of the injections. Members with different sky draws have views
   of different sizes, so padding the injection rows cannot give one shape. Each member entry compiles once (about
   1.5 minutes). No number changes.
3. **The tie entries set core's `sel_batch_size` to 2^20 at both nsides.** This is the record's first remedy: the
   stock target with the pooled 10.6-million-row file does not fit an A100-40 unbatched at nside 128 and sits at the
   edge of an A100-80 at 256. Core documents it as a reassociation of the same sums (rtol 1e-12). The member entries
   run unbatched.
4. **Writer details** (12AK B3.4): ra is taken modulo 2π (core refuses ra = 2π); `spin_reference_excluded_rows` is
   the product's own count; `T_obs_yr` and `campaign_ndraws` are set per product (model B: one pseudo-campaign;
   P_control: O4 only). Core reads none of these three attributes (checked in core's source).
5. **12AK's sample chunks are written where 12AK B3.3 declares them,** `validation/samples/<model>/<member>/`. The
   build code doubled the directory (`validation/validation/samples/`). Fixed in ad0c0b9 before any validation job.
6. **The null products are named by explicit keys** `null_S` (D4-N) and `null_P` (D4-N′) in `D4_CHOICE.json`. The tie
   looked them up by a description's prefix before. A choice without the keys is refused.
7. **V1 and V2 for P_control use its loss weight, 1.** P_control was trained unweighted. 12AK B3.6's "w for O4"
   applies to A_O4 (and u to B). Noted in 12AK.
8. **The plumbing gate's coverage (the review's item 5), stated as a limit.** null_P sets each campaign's fraction
   directly as N_draw,k/ndraw. So the gate does not exercise the per-campaign ξ normalisation of `synthetic_ndraw`,
   nor model B's `export_pdraw_joint` path (q_mix, T = 1, the joint fraction). Those are checked only by 12AK's CPU
   closed-form tests. Not changed.
9. **The S/D4 stage turns jax x64 on itself,** before its spectral grid, then checks it (C3(b)). In the build smoke it
   refused, because only a target build had turned x64 on. No number changes.
10. **The tie releases the compiled executables between its three targets** (the two null products, then the stock
    target with the pooled file), to bound its peak memory. No number changes.
11. **Build-only options** in `phase12an_d4.py`: `--points control` (a member on the five points), `--lane-a` and
    `--cell-dir` (the tie's inputs). The production plan sets none of them.

### B1.5 The pool (the record's "Scheduling", made concrete; departures marked)

- **State.** An attempt is a directory `pool/claims/<entry>/attempt_<k>` made by `mkdir`. A lane that saw an older
  state loses the race. Each attempt holds the claiming job and card, and, when the process ends, its exit code.
- **Blocked:** an exit of 3, 4 or 5 (the plumbing gate failed, C3(d) failed, a D4 entry refused; deliberate gate
  outcomes, never retried); or two failed attempts (an exit other than 0, an exit 0 without DONE, or a claiming job
  that ended without a result); or a blocked hard prerequisite.
- **New: the retry goes to an 80 GB card.** The record routes a stage that ran out of memory on a 40 GB card to an
  80 GB card. The pool does this for any failed attempt on a 40 GB card, because it does not parse the cause. It also
  covers the review's item 6: D4 memory at sigma_kde 1e-4 was not probed.
- **New: a soft prerequisite.** 12AK's `ak_core_P` (P_control, context only, never a candidate) is a soft prerequisite
  of `ak_choose`: the choice waits for it while it may finish, but its failure never blocks the choice or any D4
  entry (the review's item 4). The choice handles a missing `core_P.json`.
- **New: V1/V2's priority is 900,** below every GPU entry (it was 3100). Nothing waits for it. It runs when a lane has
  nothing else (the review's item 7).
- **Order.** A100-40 lanes take the highest priority first. Rita lanes, while one of our A100-40 lanes runs, take the
  80-GB-only entries first, then the other GPU entries, then CPU entries. With no A100-40 lane running, rita takes
  the highest priority first, so the 12AK chain never waits for a lane that has not started.
- **Waiting and exit.** A lane with nothing claimable waits 60 s while an entry it could run later is pending or
  running. Otherwise it exits. Lanes exit 0 whatever their entries did (exit 2 only when the pool itself fails); the
  summary decides every failure.
- **New: the summary runs as the pool's last entry,** on a lane's node CPUs, when every other entry is done or blocked.
  It runs 12AK's validation summary first, then 12AN's. Reason: on 2026-10-20 HENON held our 8-CPU test jobs pending
  for more than two hours (the 7-day limit leaves them out of backfill), so a HENON-only summary could wait hours.
  The HENON summary (afterany on every lane) stays as the fallback. If the pool's summary wrote `STATUS.json` at rc 0,
  the lane that ends the pool cancels the HENON job while it is still pending; if it starts anyway, it finds rc 0 and
  exits without rewriting.
- **The end.** That lane cancels our own still-pending lane jobs from `plans/jobs.json` (only ours, only PENDING) and,
  as above, the pending HENON fallback. Each cancellation is written to `plans/cancelled.json` before the `scancel`, so
  the watcher never reads our own cancellation as a failure.
- **The watcher** (`slurm/phase12an_watch_check.sh` inside the main session's until-loop, sleep 600) ends on
  `summary/STATUS.json`, or on one of our jobs not in `cancelled.json` in FAILED, CANCELLED, TIMEOUT, OUT_OF_MEMORY or
  NODE_FAIL, or pending with DependencyNeverSatisfied. A failed squeue or sacct counts as "keep watching".
- CPU tests cover the claim race, the priorities and rita's order, the soft prerequisite, the gate exits, the retry on
  an 80 GB card, a dead claim, the summary's place, and the end's cancel rule (with a fake squeue and scancel).

### B1.6 The summary (the record's "What is reported", made concrete)

- ln L of every density from Lane A's PE side and core's correction (x64). D4/D0 and D4/D2 pooled from the five
  members by algebra (v), with the pooled file's ndraw from `D4_CHOICE.json` (checked against the tie's).
- Per cell and density: items 1 to 9 of the record. The share removed uses I90 of D0 for all three variances; its
  denominator is written beside it. The comparison grid follows the window rule; only `window_holds` is written.
- **Every reported quantity is also written as a 2 × 2 matrix per density** (rows nside 128, 256; columns sigma_kde
  1e-3, 1e-4) in `summary.json` and as plain text in `summary/matrices.txt`. A withheld entry reads "withheld" with
  the failing control.
- **Withholding, by the record's table:** C3(b) and C3(c) are record gates. C3(c) counts every compute stage's commit
  (table, Lane A, cell, D4 members, tie, S/D4, C5) and requires one consumer sha, one repo_12AK sha and clean trees;
  the summary's own commit is not counted. Cell gates: R1(a), R1(b), R1(c) and its spectral part, C3(a), C3(d) (job
  and summary side), C3(e), C7 and unit galaxy weights. R2 withholds D3r, D3a and D3b everywhere. C6 (after the
  fallback) withholds the variant at the cell, and D4/D2 with it when the variant is D2. C3(f) withholds the density
  at the cell (D0's walls are reported). C9 withholds D3a and D3b at nside 256 and marks D2 and D4/D2. D4: no choice
  or a failed plumbing gate writes "not run"; a failed D4-N, D4-P, D4-C or C3(e) for D4, or a missing member,
  withholds D4 at that cell. Marks: C5, C8, C9 (D2, D4/D2), D4-N′.
- Beside every D4 number: the model, N_s drawn and kept, X1, X2, U1, U2, U3, the plumbing result, the tie's gates and
  the members' spread. The label comes from `D4_CHOICE.json`.
- No band, reading, verdict, z-score, p-value, noise floor or rank is computed or written. 12AM's reading code is not
  called. The location guard (12AM's `FORBIDDEN_KEYS`, and every computed median and 90% bound as forbidden values)
  covers `summary.json` and `controls.json`; `matrices.txt` is written only when both pass.
- `summary/absolute.npz` (never opened by agents): per cell and density, and for the in-lane spectral grid and S/D4,
  the posterior on the 501-point window and the 241-point coarse grid, ln L, ln μ, N_eff, the PE variance sum, and
  whether the window rule holds and whether the density is withheld.
- A CPU test on a synthetic run tree checks the matrices, the guard, the shares (0 for D0, 1 for D1), the pooling, and
  withholding by a D4 gate at one cell, by C6, by a failed plumbing gate and by two consumer commits.

### B1.7 The review's findings and what was done

| finding | done |
|---|---|
| 1. pool, lane, submit, watcher and summary missing | written (B1.5, B1.6); plans regenerated from the production sha; CPU tests at that sha |
| 2. build departures without an amendment | this amendment (B1.4); 12AK note B3.8 |
| 3. tie and spectral modes never ran | run in a GPU smoke on an A100-40 (B1.8) |
| 4. one failed 12AK core entry blocks all D4 | `ak_core_P` a soft prerequisite (B1.5) |
| 5. plumbing gate coverage | stated as a limit (B1.4 item 8) |
| 6. D4 memory at 1e-4 not probed | any failure on a 40 GB card retries on rita (B1.5) |
| 7. CPU entries can idle the bottleneck cards | rita takes CPU entries last; V1/V2 at 900 (B1.5) |
| 8. tests at the production commits queued | the final CPU tests run at the production shas before submission |
| 9. doubled sample directory | fixed (B1.4 item 5) |
| 10. null lookup fragile | explicit keys (B1.4 item 6) |
| 11. minor issues in `phase12an_d4.py` | the tie checks the cell's DONE first; the dead branch removed |
| 12. old watcher loop | the production watcher uses sacct states and the summary's `STATUS.json` (B1.5) |
| 13. every D4 number likely "systematic" | not a code defect; reported as it comes out |

### B1.8 The D4 smoke and the final CPU tests (build stage; not results)

**The smoke** (job 1390622, twig A100-40, consumer cabb3b6, repo_12AK ad0c0b9; outputs under
`controls/smoke_d4`, outside the production tree). The tie and S/D4 modes ran for the first time, on 12AK's
5%-scale end-to-end products (model A, about 106,000 rows per member; full-size null products), at (128, 1e-3),
against the build control's cell stage and 12AM's Lane A:
- the five member entries at the five points: exit 0; C3(e) for D4 passes (member 1);
- the tie: exit 0. D4-N: ptp of ln μ_null − ln μ_real 3.5e-9 (D0) and 3.5e-9 (D2), N_eff 6.0e-8 and 2.2e-8, against
  1e-6. D4-N′ (mark): 6.2e-9 and 1.8e-9, N_eff 4.9e-8 and 4.2e-8. D4-P: bit for bit. D4-C: ln μ 4.1e-16, N_eff
  8.1e-15 relative, ln L 9.1e-13. Peak 24.8 GiB (nvidia-smi) on the A100-40 with three targets in one process; host
  15.4 GiB; 5.4 minutes;
- S/D4: exit 0 on the 641 points, x64 on, 16 s;
- the first smoke (job 1390621) found the S/D4 x64 refusal (B1.4 item 9) and a missing log directory; fixed in
  cabb3b6. Between cabb3b6 and the production consumer sha only new files were added (the pool, the summary, their
  tests and scripts); `phase12an_d4.py` is the same.

**The final CPU tests** at the production shas (consumer cb7c638, repo_12AK ad0c0b9; run niced in a shell on the
session's node, `controls/cpu_final/STATUS.json`): the consumer's 24 tests (`test_phase12an.py`,
`test_phase12an_d4.py`, `test_phase12an_pool.py`, `test_phase12an_summary.py`), 12AK's 38 tests (12AK venv) and its 3
core-load tests (consumer env): all pass. The smoke job also ran the D0 to D3, D4 and 12AK tests at cabb3b6: all
pass. The submit script refuses unless this file records every test passing at exactly the submitted shas.

## Production (submitted 2026-10-20 03:42 UTC)

- **Shas.** Consumer cb7c638 (worktree `d1_d4_fine/worktrees/cb7c6386afc9`); repo_12AK ad0c0b9 (worktree
  `pdet_surrogate/ours/worktrees/ad0c0b970d95`). Every entry runs from one of these two clean worktrees.
- **Plan.** `d1_d4_fine/plans/pool.json`: 47 entries (13 D0 to D3, 8 of 12AK's validation chain, 25 D4, the summary),
  358 card-minutes of GPU work (184 of them on 80 GB cards only) and 51 CPU minutes on lanes' nodes. Written from
  the production sha with `plans/d03_entries.json` and `plans/d4_entries.json`.
- **Jobs** (`d1_d4_fine/plans/jobs.json`): lanes rita0 1390631, rita1 1390632, twig0 1390633, twig1 1390634,
  twig2 1390635, twig3 1390636, henongpu0 1390637, henongpu1 1390638; the HENON fallback summary 1390639
  (afterany on every lane). No MIKO job, no js2h100 job, no other user's job touched.
- **At submission** five lanes started at once: rita0, rita1, twig0, twig1 and henongpu0. Another user holds two twig
  cards (12-hour and 2-day jobs) and the second henon-gpu card, so twig2, twig3 and henongpu1 wait; the lane that ends
  the pool cancels them if they are still pending. The first claims: twig0 12AK's sampling (the critical path), rita0
  the (256, 1e-4) table, rita1 the (256, 1e-4) Lane A, henongpu0 the (128, 1e-4) table, twig1 the (128, 1e-4) Lane A.
- **Estimate** (five cards). The 12AK chain to the D4 choice: about 50 minutes (sampling 15, writing 20, core
  checks 12, choice 1). Rita's 80-GB-only work: about 97 card-minutes of D0 to D3 in the first 50 minutes on its two
  cards, then about 87 card-minutes of nside-256 D4 work after the choice, about 45 minutes. The summary entry about 10
  minutes. **So the summary is due about 05:45 to 06:30 UTC on 2026-10-20**, later (to about 08:00 UTC) if an entry
  needs its retry on rita or the D3 work runs long. The 7-day and 2-day limits are ceilings, not the estimate.
- **The watcher** (for the main session; sleep 600):
  `until bash d1_d4_fine/worktrees/cb7c6386afc9/slurm/phase12an_watch_check.sh; do sleep 600; done` followed by
  sacct for every job and the first 3000 bytes of `d1_d4_fine/summary/STATUS.json`.
- Nothing pushed. No absolute file was opened.

## Results (summary 2026-10-20 05:17 UTC; location-free; numbers only under the owner's reporting rule)

- **Run.** Summary entry on lane rita0 (job 1390631), rc 0; record gate failures none; guard violations none; R2 failures none. All 47 pool entries done; the three pending lanes (twig2, twig3, henongpu1) and the HENON fallback summary were cancelled by the pool when it ended. Outputs: `d1_d4_fine/summary/{summary.json, matrices.txt, controls.json, STATUS.json}`. The absolute file was not opened.
- **D4.** Model A chosen by U3 (A has the smaller ensemble S_W[50, 90]; S_W A 9.28e-04, B 1.49e-03). Label **systematic**, because not every numerical check passes: X1 smallest xi_emu/xi 0.9450 (fail); X2 ratio − 1 p_O3 -0.0074, p_O4 -0.0132, q_mix -0.0126, spectral_population_gen_cosmology -0.0027 against 0.01 (fail); U2 max member sd on [50, 90] 0.0028 against 0.0015 (fail); U1 S_W[50, 90] 9.28e-04 against 0.003 (pass); plumbing gate pass (shape max |Δ| 3.9e-09). Pooled rows 10,634,443; pooled draws 9,335,484,607.
- **Spectral-only through D4's selection** against the stock spectral-only (reference cell 128/1e-3, window grid): R 0.9921, hellinger 0.00446, sd_ratio 0.9919, shift_in_spectral_sd 0.00493.
- **Withheld:** D4/D0 at (256, 1e-4), by C3(f): effective-sample walls outside the window, total variance 71.2 against the limit 20. D0's walls are reported, not gating: (128, 1e-4) total variance 25.7, walls outside the window; (256, 1e-4) total variance 74.4, walls inside it.
- **Marks:** D1 at every cell (C8: D1 is spectral-only up to a constant, so its shares removed are 1 by construction); D4/D0 and D4/D2 at both sigma_kde 1e-4 cells (the synthetic-path null D4-N′ does not pass there).
- **C9** (nside independence of the D2, D3a, D3b and D4/D2 tables, 128 against 256): pass at both sigma_kde.
- **Hellinger, nside 128 against 256** (window grid; D0 at 1e-4 on the coarse grid): sigma_kde 1e-03: D0 0.145, D1 0.068, D2 0.067, D3a 0.065, D3b 0.066, D3r 0.067, D4/D0 0.069, D4/D2 0.067; sigma_kde 1e-04: D0 0.284, D1 0.185, D2 0.187, D3a 0.189, D3b 0.187, D3r 0.189, D4/D0 withheld, D4/D2 0.186.

Columns are the cells (nside / sigma_kde). Spectral-only reference: Var sel 0.69, total 0.91.

### D0

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 1.141 | 7.330 | 1.935 | 16.766 |
| Var ln L, PE | 0.263 | 0.399 | 0.297 | 0.714 |
| Var ln L, total | 1.387 | 7.650 | 2.229 | 17.360 |
| share of catalog-added selection variance removed (D1 = 1) | 0.000 | 0.000 | 0.000 | 0.000 |
| width R vs spectral-only | 1.156 | 1.237 | 1.022 | 1.190 |
| sd ratio vs spectral-only | 1.070 | 1.077 | 1.013 | 1.122 |
| median shift vs spectral-only (spectral sd) | -0.0042 | -0.093 | 0.184 | -0.439 |
| median shift vs D0 (spectral sd) | 0.000 | 0.000 | 0.000 | 0.000 |
| Hellinger vs spectral-only | 0.138 | 0.252 | 0.196 | 0.349 |
| roughness (window) | 0.028 | 0.790 | 0.033 | 537 |

### D1

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.700 | 0.700 | 0.700 | 0.699 |
| Var ln L, PE | 0.266 | 0.402 | 0.311 | 0.714 |
| Var ln L, total | 0.964 | 1.100 | 1.011 | 1.386 |
| share of catalog-added selection variance removed (D1 = 1) | 1.000 | 1.000 | 1.000 | 1.000 |
| width R vs spectral-only | 1.010 | 1.000 | 0.968 | 1.008 |
| sd ratio vs spectral-only | 1.006 | 1.006 | 0.979 | 0.977 |
| median shift vs spectral-only (spectral sd) | -0.314 | -0.290 | -0.408 | -0.388 |
| median shift vs D0 (spectral sd) | -0.309 | -0.197 | -0.592 | 0.230 |
| Hellinger vs spectral-only | 0.143 | 0.169 | 0.151 | 0.242 |
| roughness (window) | 0.012 | 0.282 | 0.014 | 0.573 |

### D2

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.710 | 0.710 | 0.709 | 0.710 |
| Var ln L, PE | 0.266 | 0.399 | 0.304 | 0.714 |
| Var ln L, total | 0.976 | 1.109 | 1.013 | 1.394 |
| share of catalog-added selection variance removed (D1 = 1) | 0.966 | 0.998 | 0.988 | 0.999 |
| width R vs spectral-only | 1.017 | 1.024 | 1.003 | 1.012 |
| sd ratio vs spectral-only | 1.012 | 1.009 | 1.008 | 1.004 |
| median shift vs spectral-only (spectral sd) | -0.015 | 0.018 | -0.141 | -0.093 |
| median shift vs D0 (spectral sd) | -0.011 | 0.111 | -0.325 | 0.452 |
| Hellinger vs spectral-only | 0.061 | 0.113 | 0.063 | 0.202 |
| roughness (window) | 0.020 | 0.282 | 0.022 | 0.574 |

### D3a

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.729 | 0.732 | 0.726 | 0.732 |
| Var ln L, PE | 0.265 | 0.373 | 0.302 | 0.714 |
| Var ln L, total | 0.994 | 1.105 | 1.028 | 1.421 |
| share of catalog-added selection variance removed (D1 = 1) | 0.925 | 0.993 | 0.975 | 0.997 |
| width R vs spectral-only | 1.041 | 1.049 | 1.029 | 1.037 |
| sd ratio vs spectral-only | 1.016 | 1.011 | 1.015 | 1.006 |
| median shift vs spectral-only (spectral sd) | 0.033 | 0.074 | -0.076 | -0.069 |
| median shift vs D0 (spectral sd) | 0.037 | 0.168 | -0.260 | 0.482 |
| Hellinger vs spectral-only | 0.072 | 0.123 | 0.060 | 0.207 |
| roughness (window) | 0.025 | 0.289 | 0.026 | 0.579 |

### D3b

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.752 | 0.781 | 0.752 | 0.781 |
| Var ln L, PE | 0.257 | 0.350 | 0.299 | 0.714 |
| Var ln L, total | 1.009 | 1.129 | 1.052 | 1.447 |
| share of catalog-added selection variance removed (D1 = 1) | 0.871 | 0.987 | 0.952 | 0.994 |
| width R vs spectral-only | 1.046 | 1.056 | 1.037 | 1.052 |
| sd ratio vs spectral-only | 1.012 | 1.007 | 1.014 | 1.008 |
| median shift vs spectral-only (spectral sd) | 0.032 | 0.077 | -0.077 | -0.067 |
| median shift vs D0 (spectral sd) | 0.036 | 0.170 | -0.261 | 0.478 |
| Hellinger vs spectral-only | 0.071 | 0.124 | 0.066 | 0.206 |
| roughness (window) | 0.024 | 0.308 | 0.026 | 0.600 |

### D3r

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.713 | 0.715 | 0.713 | 0.718 |
| Var ln L, PE | 0.266 | 0.399 | 0.304 | 0.714 |
| Var ln L, total | 0.978 | 1.112 | 1.017 | 1.393 |
| share of catalog-added selection variance removed (D1 = 1) | 0.961 | 0.996 | 0.987 | 0.998 |
| width R vs spectral-only | 1.024 | 1.033 | 1.006 | 1.006 |
| sd ratio vs spectral-only | 1.012 | 1.010 | 1.007 | 1.002 |
| median shift vs spectral-only (spectral sd) | -0.00685 | 0.021 | -0.127 | -0.089 |
| median shift vs D0 (spectral sd) | -0.00264 | 0.114 | -0.311 | 0.456 |
| Hellinger vs spectral-only | 0.061 | 0.113 | 0.060 | 0.202 |
| roughness (window) | 0.020 | 0.286 | 0.022 | 0.574 |

### D4/D0 (label: systematic)

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.117 | 0.285 | 0.171 | withheld: C3(f) |
| Var ln L, PE | 0.251 | 0.350 | 0.299 | withheld: C3(f) |
| Var ln L, total | 0.368 | 0.614 | 0.467 | withheld: C3(f) |
| share of catalog-added selection variance removed (D1 = 1) | 2.287 | 1.062 | 1.419 | withheld: C3(f) |
| width R vs spectral-only | 0.927 | 0.939 | 0.935 | withheld: C3(f) |
| sd ratio vs spectral-only | 0.962 | 0.961 | 0.968 | withheld: C3(f) |
| median shift vs spectral-only (spectral sd) | 0.068 | 0.104 | -0.056 | withheld: C3(f) |
| median shift vs D0 (spectral sd) | 0.072 | 0.198 | -0.240 | withheld: C3(f) |
| Hellinger vs spectral-only | 0.073 | 0.147 | 0.068 | withheld: C3(f) |
| roughness (window) | 0.015 | 0.417 | 0.018 | withheld: C3(f) |

### D4/D2 (label: systematic)

| metric | 128 / 1e-3 | 128 / 1e-4 | 256 / 1e-3 | 256 / 1e-4 |
|---|---|---|---|---|
| Var ln L, selection (max in I90) | 0.073 | 0.073 | 0.073 | 0.073 |
| Var ln L, PE | 0.265 | 0.399 | 0.304 | 0.714 |
| Var ln L, total | 0.338 | 0.472 | 0.377 | 0.784 |
| share of catalog-added selection variance removed (D1 = 1) | 2.393 | 1.094 | 1.498 | 1.039 |
| width R vs spectral-only | 1.011 | 1.018 | 0.999 | 1.008 |
| sd ratio vs spectral-only | 1.006 | 1.003 | 1.002 | 0.998 |
| median shift vs spectral-only (spectral sd) | -0.016 | 0.018 | -0.146 | -0.094 |
| median shift vs D0 (spectral sd) | -0.011 | 0.111 | -0.330 | 0.451 |
| Hellinger vs spectral-only | 0.059 | 0.112 | 0.063 | 0.201 |
| roughness (window) | 0.013 | 0.283 | 0.015 | 0.574 |

### Decision after the results (owner, 2026-10-20)

- The sky-averaged selection density (D2) had been proposed as part of the fiducial. It is **withdrawn**: the owner asked why DESI would be sky-averaged. D2 stays a diagnostic that separates selection noise from physics; a production estimator must keep DESI's sky structure. The fiducial (nside 128, sigma_kde 1e-3, density) is open.

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
sha256, in `config/record_envs/12AN.json`; `scripts/check_frozen_environment.py --record 12AN` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AN/<sha7>` on
GitHub (cabb3b6, cb7c638, ad0c0b9). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON);
it was green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main
(above).

**Population of the spectral-only grids (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** The spectral-only grids gave the population as an explicit mapping at the corrected pair (0.04, 0.10). From
the consolidated main of PR #20 they evaluated the same values but recorded a `population.fixed_values` record (the
declaration written over equal entries); after the follow-up (PR #21) they resolve and record exactly what they did
when they ran (no `fixed_values` record; checked on the 12AG spectral reference at three H0 points: ln L difference
0).

**Inputs: the pinned base configuration (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).**
12AM's cell and table stages (`scripts/phase12am_cell.py`, `scripts/phase12am_table.py`), which 12AN's cell, D4 and
table stages use, check the sha256 of the base configuration against the value 12AM pins (b79ad777...). The
consolidation's spin declaration changed `config/desi.fixed_population.json`, so from the consolidated main of PR #20
these stages refused to run ("inputs are not the declared files: [config]"). Since the follow-up (PR #21) they read
`config/desi.fixed_population.core_preset.json`, which is that file byte for byte
(`phase12t_stage.DESI_CONFIG_AS_RUN`); the 12AG overrides they apply set the spin pair (0.04, 0.10), so the
configuration they resolve is the one this record ran. Checked with the record's own inputs in its environment: both
checks pass at the review head and after the follow-up, and refused at PR #20's main. The input record names the new
path with the pinned sha256.

**The D4 path's code (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding G4.1).**
repo_12AK's sampler and writer at ad0c0b9 are now on the consumer's main with 12AK's merge.

**Run fingerprints (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).** The code digests that the
12AG to 12AQ drivers put into their run fingerprints cover the consumer code, so a run stored before the consolidation
(or its follow-up) is evaluated again rather than resumed when it is rerun from main; the values it computes are the
same.

**D0's wall at (256, 1e-4) (consumer PR #28, merge 8f8a7b2; finding C126).** D0 is reported, never withheld (C3(f) for
D0 is reported). At (256, 1e-4) its guard wall lies inside the window (largest |wall| there about 1.3e4 nat; total
variance up to 74), and the tables give D0's numbers there unmarked. D0's window roughness there, 537, is that wall
(selection part 537.1, PE part 0.57), not PE structure. Every density's shift and Hellinger distance against D0 at
that cell, and D0's nside 128-against-256 Hellinger at 1e-4, carry the wall. D0's own R and shift there are unchanged
by the wall to the third decimal (12AM's uncapped coarse values equal the capped ones). Since the merge the summary
marks D0, and every entry against D0, at a cell where D0's wall lies inside the window, and matrices.txt stars them.
Re-run on the stored grids, (256, 1e-4) is the only such cell; no number of the summary changes.

**Control C8's cause (consumer PR #28, merge 8f8a7b2; finding C127).** "dV_c/dz on two grids" should read: one grid,
two interpolants (see 12AL's amendment of the same date).

**The D4 member spread (consumer PR #28, merge 8f8a7b2; finding C128).** The spread over the five members is the sd of
the **mean-removed** N ln mu_D4,m (each member's mean over the window removed), not "window-detrended": no line is
removed, so each member's tilt stays in the spread. That is the quantity that matters for the posterior (a constant
cancels, a tilt moves it); the number is unchanged. Since the merge the summary key is
`max_over_window_sd_N_log_mu_mean_removed` (it was `..._detrended`).

**The D4 spectral mode's options (consumer PR #28, merge 8f8a7b2; finding C132).** `phase12an_d4.py --mode spectral`
accepted `--nside`, `--sigma-kde` and `--sel-batch-size` and ignored them (it runs one declared cell with the baseline
numerics). No run of record passed them. Since the merge it refuses them.

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

**Operations (consumer PR #30, merge 6d0f800; finding C133).** If squeue had failed persistently, the pool's lanes
would have counted every dead claim as alive and held their GPUs until the job limit. All lanes ended normally, so
nothing was affected. From the merge a lane that would wait while squeue has failed for 30 minutes in a row exits with
code 2 and records why.
