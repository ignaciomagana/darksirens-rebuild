# Phase 12AR — catalog version 2: the full rebuild of the DESI union and its products (declaration and results)

## Status

**Declaration, amendments and results (location-free).** The rebuild agent drafted the declaration (every section
above "Amendments") on 27 Oct 2026, when the rebuild was launched and before stage A ran, and added the stage
amendments as the stages finished (27-28 Oct). The owner gave the go for this records PR on 30 Oct 2026, after
REBUILD_DONE, so the repository history alone does not fix the order of declaration and results; the design written
before submission (`darksirens-core-data/catalog_v2_2026-10-27/DESIGN_full_rebuild.md`) carries it. One gate was
set during the run: the agent set the two Q review-gate bands at [0.9, 1.1] on 27 Oct while stage B ran, before the
version-2 Q tables existed, and the owner accepted them that evening (version 1 read 1.52 and 0.48-0.84). Scope:
nside 32, 64 and 128 (owner decision of 28 Oct 2026: nside 256 out of version 2; see the stage-C amendment). Nothing
here samples a chain: the population-free production chains on version 2 (gamma sampled) are a later record.

Design: `darksirens-core-data/catalog_v2_2026-10-27/DESIGN_full_rebuild.md` (design B of the consumer review's
catalog package, updated with the owner's decisions of 27 Oct 2026), after the sizing (design A, run 26-27 Oct).

## Question

Rebuild the Phase 12 DESI union and every product that consumes it or its footprint under the owner's decisions,
so that later records (production chains, ladders, Q-table grids) can run on catalog version 2, and say how the
H0 likelihood at the production and fiducial cells moves against the catalog of records 12AF-12AQ.

## The model (owner's decisions)

- **Hosts** are the galaxies above the builder's absolute-magnitude floor; the completeness is 1 below z_depth
  0.245 (decision 1, option C; selection family `floor_hosts`). M0hat and sigma_M are dropped.
- **Footprint** f_p = S_r x S_enter from the catalog's own construction (the r-band share times the share of quality
  r <= 21 candidates that can enter the catalog and are not vetoed), with the bright-star mask veto BRIGHT and
  MEDIUM, Legacy Survey maskbits 2050 (decision 2, option A).
- **Photometric kernel**: each photometric row's centre is moved so that core's kernel has its mean at the photo-z
  (decision 3, option B), at the run's delta, sigma_kde and Om0; the leak-fixed union (spectra to z 0.5); CMB-frame
  redshifts.
- **n0** of the floor hosts within the depth with the floor's photo-z migration forward-modelled by the colour-aware
  mock (each mock galaxy's colour and photo-z error drawn together from one DESI match of its redshift and
  magnitude cell; the default since consumer PR #41).
- **delta inside the depth** is fitted on the counts within [0.02, 0.245] (the host density n0 (1+z)^delta_in) and
  fixed in the calibration prior; every store is centred at it. On the round-1 build the colour-aware fit gave
  -0.64 +- 0.14; the rebuild refits it and records the value.
- **delta beyond the depth** is 0 (`catalog.delta_out`, consumer PR #40): the missing hosts beyond z_depth follow
  comoving volume. The delta-split test (27 Oct) found that 97% of the H0 sensitivity to delta came from beyond the
  depth, where the count fit says nothing; inside the window delta_in moves H0 by about 0.05 sd per unit.

## Products

| product | cells | where |
|---|---|---|
| version-2 union, footprint (nside 128 and its nside-256 upgrade), calibration sample, pair colours | | `build/` |
| n0 and the calibration prior (log10 n0 normal with its width; delta fixed at delta_in), production overlays (with delta_out 0) | nside 32, 64, 128, 256 | `calib/ns<N>/` |
| pixelated stores, photometric kernels centred at delta_in and each sigma_kde | nside 32, 64, 128 x sigma_kde 1e-4, 3e-4, 1e-3, 3e-3, 1e-2 (nside 256 out of scope, owner 28 Oct) | `stores/ns<N>_sk<S>/` |
| footprint diagnostics (the 12AG covariates) | each nside | `diagnose/` |
| Q tables (12AQ's build on version 2: selection base f_p below the depth) | nside 128, sigma_kde 1e-3 | `q/tables/` |
| D2 tables (12AM's streamed table on version 2) | the 15 cells at nside 32, 64, 128 | `d2/<cell>/table/` |

## Inputs

Legacy Survey DR10 south and DR9 north v2 parents (`phy220048p/share/legacysurvey/`); the DESI match with spectra
to z 0.5 (`loa_ls_match_z05.h5`); for the control, the legacy match and pixelation input. Old arm of the
validation: `smearing_ladder/catalogs/desi_union_nside128.h5` (f26a20f0...), `desi_union_nside64.h5` (c2d1ff36...,
the production file), `phase12t/inputs/mth_map_nside128.h5` (1e4e5c67...). GW: the 12AP PE (lalcosmo, 822b3181...)
and injections (56e51af2...). Code: consumer main 7cda3e5 (stage A) and the merge of the 12AQ/12AM input options
(stage B); environment `consumer_1022429_lss57afebe_cuda12` (core 1022429, lss 57afebe).

## Gates (declared; a miss stops what depends on the product and goes to the owner, never relaxed)

- **Control** of the builder: with its three changes off it reproduces the legacy union (to rounding) and the
  production map's counts.
- **Build**: pixels equal the files' HEALPix pixel on every row; the veto and the leak fix act (positive counts);
  the outputs written. Reported: the veto's loss per redshift bin against its footprint share.
- **Calibration** at nside 128: the luminosity inversion converged; log10 n0 width <= 0.1 dex; observed over
  expected counts within [0.8, 1.25] in every 0.01 bin with >= 1,000 expected rows, at the fitted delta_in; the
  delta fit converged and not at a bound. At nside 32, 64, 256 (delta fixed at delta_in): the same, and n0 within
  0.2 of the nside-128 width of the nside-128 value.
- **Stores**: per nside, no occupied pixel uncovered, at most 100 improbable empty covered pixels, galaxy density
  per unit f_p within [2/3, 1.5] of the clean bin in every f_p bin with >= 50 pixels; per sigma_kde, the centred
  kernel's PIT mean in [0.47, 0.53] and 68%/95% coverage in [0.62, 0.74]/[0.90, 0.97] on up to 1M non-training DESI
  matches.
- **Q tables**: record 12AQ's galaxy-side gates (the reconstruction of the galaxies at sub-pixel resolution equals
  the store; the cross-validation's eligibility and choice, rule v3 with v2 beside; every table's convergence,
  Laplace and rail stamps and certificate; H0-free inputs and tables, gate 7 (a, b); the consumed budget, gate 8;
  the certificates, gate 10; the member table's map equal to the primary's), and the two review gates: the
  budget-weighted Q of the rows with f_p < 2/3 over that of the rows with f_p >= 2/3 in [0.9, 1.1], and the
  budget-weighted Q of the rows with >= 10% of candidates lacking a photo-z in [0.9, 1.1] (record 12AQ on version 1:
  1.40, and 0.48-0.84 by class).
- **D2 tables**: 12AM's controls 6 (table accuracy) and 7 (kernel H0 invariance).
- **Spectral-only tie**: the spectral grid of the run commit, in the validation's environment and in the reference's,
  equals the record spectral grid with the same GW inputs (`lalcosmo_check`) within 1e-6 at all 241 points.

## Validation readings (declared now; Bayesian, location-free, no thresholds)

Fixed-calibration H0 grids (641 points, guard limit 4 with the smooth guard; each row also unguarded) at the
production cell (nside 64, sigma_kde 3e-3) and the fiducial cell (nside 128, 1e-3): version 2 (delta_in fitted,
delta_out 0, n0 of the cell's nside) against the old catalog (version 1, Gaussian completeness at M0hat -20.4975,
sigma_M 0.5592, log10 n0 -1.8216, delta 0). Reported per cell, with and without the guard: the shift of the
posterior mean in old-posterior sd, the sd ratio, the Hellinger distance and the spread of the log L difference over
the old 95% interval. The sizing (fiducial cell, round-1 build, empirical migration) read -0.12 sd at delta 0; the
delta-split test read about -0.10 sd at delta_in -0.40 to -0.66 with delta_out 0. These are context, not bands.

## Compute

HENON CPU (account phy230014p) for the build, calibration, stores, Q tables and D2 tables; one rita A100 (QOS rita)
for the validation grids (or the MIKO holder's H100 as a step, nice 19, 60 GB host cap). Every job has the 7-day
limit as a ceiling.

## What it does not do

No chain. The 12AQ H0 grids with the version-2 Q tables (the Q arms, the member arms, the replicates) and their
likelihood-side gates go with the analysis on version 2. The records 12AF-12AQ keep version 1.

## Amendments

**Amendment, stage A (27 Oct 2026, 19:18-20:43 UTC; code consumer 7cda3e5; location-free).**
- **Control and build pass.** With its three changes off the builder reproduces the legacy union to rounding and
  the production map's counts (C1, C2). The version-2 build passes every gate: pixels on every row, the veto
  removed 3.63M rows, 0.53M spectra above the window with a photo-z inside it moved out, 21,262,366 rows. Its
  union, footprint and calibration sample equal the sizing's round-1 build dataset by dataset. The veto's loss in
  the 0.02-0.03 bin is 9.7% (4.2-9.1% elsewhere). The pair colours pass their alignment and floor checks and equal
  the colour-mock run's.
- **Calibration (nside 128) passes.** delta_in = -0.641 +- 0.144 (4 iterations, converged, not at a bound; the same
  value as the colour-mock run on the round-1 build). log10 n0 width 0.016 dex. Per-bin ratios 0.907-1.034 in the
  23 gated bins (band [0.8, 1.25]). R = 1.017; the member-density value sits 0.44 sd above. The magnitude limit binds
  for 6.8% of window rows. At nside 32, 64 and 256 (delta fixed at delta_in) n0 equals the nside-128 value
  (difference 0).
- **Stores: 15 of 20 cells pass, the 5 nside-256 cells miss the coverage gate.** At nside 32, 64 and 128 every cell
  passes both gates (improbable empty covered pixels 5, 13 and 43 against the limit 100; the centred kernel's PIT
  mean 0.494-0.495 and 68%/95% coverage 0.679-0.728/0.931-0.949 over sigma_kde 1e-4 to 1e-2; 12.7k-16.9k
  photometric centres held at the 1e-4 floor). At nside 256 the kernel gate passes but 2,945 covered pixels are
  empty where at least 10 galaxies are expected (limit 100; 0.46% of the f_p sum, 0.69% of PE samples). 96% of them
  have an occupied nside-128 parent and 1-3 occupied siblings (median f_p 0.63, median expectation 30): the
  nside-256 footprint is the nside-128 map upgraded (each child its parent's f_p), so masks and holes smaller than
  an nside-128 pixel read as empty children. **For the owner** (no relaxation applied): a footprint built natively at
  nside 256, dropping nside 256 from version 2, or accepting the miss.
- **Spectral-only tie passes**, bit for bit (every difference 0.0 at all 241 points) in both environments.
- **Validation (location-free; guard limit 4, smooth guard; guarded and unguarded equal: one penalised point per
  arm at the fiducial cell, none at the production cell).** Version 2 against the old catalog:

  | cell | shift (old sd) | sd ratio | Hellinger | spread of d log L over the old 95% interval |
  |---|---|---|---|---|
  | production (nside 64, sigma_kde 3e-3) | -0.085 | 1.022 | 0.035 | 0.42 |
  | fiducial (nside 128, 1e-3) | -0.089 | 1.075 | 0.100 | 1.66 |

  The fiducial old arm reproduces the sizing's old arm to 1.1e-12. The grids ran as a step of the MIKO holder
  (H100), the rita queue being held by another user's jobs.

**Amendment, stage B (28 Oct 2026, to 00:50 UTC; code consumer f111a87, PR #42; location-free).**
- **Q tables (fiducial cell).** The reconstruction of the galaxies at sub-pixel resolution equals the store (per
  pixel, per cell; the CV rows' redshifts equal the store's bit for bit). The v3 rule leaves one eligible setting,
  sigma 0.3 and ell_grid 16, so there is no runner-up; the v2 rule, recorded beside it, would pick sigma 0.5 and
  ell_grid 2 among 27. Every table converges; the table check has no miss (gates 7(a), 7(b), 8, 10). The
  constant-per-redshift table fails its certificate, as expected. The 16-member map equals the primary's. Review
  gates (bands accepted by the owner on 27 Oct): R1 0.921 and R2 0.942, both inside [0.9, 1.1] (version 1: 1.52 and
  0.48-0.84).
- **D2 tables.** The 12 cells at nside 32, 64 and 128 with sigma_kde >= 3e-4 pass controls 6 and 7 on HENON CPU. The
  three sigma_kde 1e-4 cells were moved to rita GPUs (record 12AM's device) at their fine-table step.

- The three sigma_kde 1e-4 cells passed on rita GPUs (the nside-128 one rerun after a Slurm TaskProlog failure).
  All 15 cells at nside 32, 64 and 128 pass controls 6 and 7.

**Amendment, stage C and the scope (28 Oct 2026; location-free).**
- The owner asked for the footprint to be counted natively at nside 256 (consumer PR #43). The native map sums to
  the nside-128 counts in every pixel (sum f_p -0.33%), and n0 at nside 256 sits 0.087 sd from the nside-128 value.
  The five native-256 stores still miss the coverage gate: **189 improbable empty covered pixels against the limit
  of 100** (2,945 on the upgraded map; 43 at nside 128), 0.037% of the f_p sum and 0.094% of PE samples. 95% of
  them border uncovered sky: they are edge slivers of imaging whose f_p is high, because f_p = S_r x S_enter is a
  ratio of object counts with no area term. The gate's expectation fits interior pixels (overdispersed counts
  predict about 1 such pixel over the whole sky).
- **Scope (owner decision, 28 Oct 2026, about 03:10 UTC): nside 256 is out of catalog version 2.** Version 2 is the
  15 cells at nside 32, 64 and 128; the nside-256 files and marks stay on disk, labelled out of scope. No gate was
  relaxed. A possible version 2.1 adds an area term from Legacy Survey randoms (f_p = A_p x S_r x S_enter) at every
  nside.

**Amendment, the close (28 Oct 2026 03:09 UTC; location-free).** The final finish wrote REBUILD_DONE
(`finish finish_final`): every in-scope gate of stages A, B and C passes, and no gate was relaxed. The finish's
summary is `catalog_v2_2026-10-27/summary.json` (sha256 96166d95c6fce6c1...; it holds the full sha256 of every product
below). Products of record (first 16 hex digits of each sha256):
- Footprint (nside 128 native) `4991f1af21d74555`; calibration `b5f26a8b0388c1df`; pair colours
  `dc8d641d7d5a3a98`; build record `ff99fd577453a30a`.
- n0 and the calibration prior: delta_in = -0.641 +- 0.144
  (fitted on [0.02, 0.245], 4 iterations, not at a bound), delta_out 0, log10 n0
  width 0.016 dex, the same n0 at every in-scope nside.
- Stores and D2 tables, the 15 in-scope cells:

  | cell | store | D2 table |
  |---|---|---|
  | ns32_sk1e-04 | `17b9f4e563bb03b5` | `d5aab2c5ca3c9115` |
  | ns32_sk3e-04 | `0a079bd04064781b` | `b6f72ae85c0ae0f3` |
  | ns32_sk1e-03 | `658f5f7158dea25f` | `b60002a372cb1ef9` |
  | ns32_sk3e-03 | `da20cabee4667085` | `95c274d8bf923c34` |
  | ns32_sk1e-02 | `eed188684c9866b0` | `88eb12c063b84fb1` |
  | ns64_sk1e-04 | `27357c3964edeb65` | `9a590210270746cf` |
  | ns64_sk3e-04 | `a189d8522bf208eb` | `f483332f25651762` |
  | ns64_sk1e-03 | `c3fe6190c7d0d10a` | `de0d766005d70185` |
  | ns64_sk3e-03 | `6c59d63a8d2b0c85` | `7debcdd1895b5860` |
  | ns64_sk1e-02 | `244caaea420c044f` | `3686c7a811aedd51` |
  | ns128_sk1e-04 | `799e3a6f2b359e92` | `7cb733c6c365d4cc` |
  | ns128_sk3e-04 | `c7502e4d1070bb62` | `36031e2633d34eca` |
  | ns128_sk1e-03 | `20841d18308d2c43` | `b3a5bca287c2cec7` |
  | ns128_sk3e-03 | `76c89ad94792e5f1` | `974990ea123eefae` |
  | ns128_sk1e-02 | `4fd3ddfaedd28aa7` | `a66bc32d2fce08c6` |
- Q tables at nside 128, sigma_kde 1e-3 (rule v3: sigma 0.3, ell_grid 16): q_main_m16 `2cc8a2dad218f939`, q_main_map `5e35e901f8f49c4a`, q_main_map_h60 `aa8bcdf44c699387`, q_main_map_h80 `1705b6534c8e8987`, q_member0_map `ac080e114e47866f`, q_rough_map `deb9f9f959796e4a`, q_shuffled_s3305 `e2a5a2622377df83`, q_shuffled_s3306 `7baee36e064ad551`, q_shuffled_s3307 `7305479bc5f1ed86`, q_shuffled_s3308 `f22f93effa71dd89`, unit `8685163807724682`.

The smoke directories of this rebuild (`dev_smoke/`, `smoke_a/`, `smoke_c/`) were deleted on 30 Oct 2026
on the owner's go; their small files (runbooks, gate JSONs, logs; 368 files) are kept in
`catalog_v2_2026-10-27/smoke_small_files_2026-10-30.tar.gz`. The nside-256 files and marks stay on disk, out of scope.
