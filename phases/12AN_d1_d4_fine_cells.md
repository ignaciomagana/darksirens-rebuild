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
