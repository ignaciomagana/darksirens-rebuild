# Phase 12AQ — P12.5: the DESI H0 grids at the fiducial cell with LSS-conditioned missing hosts (Q tables) (declaration)

## Status

**DECLARED (main session, 2026-10-22, on the owner's standing instruction of 2026-10-22: "after all the lss work is done,
try H0 scans with the DESI catalog and the Q tables"; ambiguous choices settled by research, recommended path
followed), before any GW likelihood with a Q table.** This record fixes the question, the Q tables and how their
settings were chosen (from galaxies only), the arms, the inputs with their sha256, the checks before the go, what is
reported and the compute. Two parts come later, as labelled amendments:
- the hyperparameter choice of the cross-validation (`q_scans/cv/choice.json`, with its sha256 and the certificate
  table), before any table is built;
- the table sha256s and the plumbing checks, before any grid uses those tables (the rehearsal's tables in their own
  amendment; the member tables in a second one).

The lss head the real tables are built on is added when it is pushed (T0, below). The owner may revise any choice on
return.

**Blinding: location-free.** No H0 location appears here, in commit messages or in the logs agents read: no median,
interval, MAP or shift in km/s/Mpc. The H0 values in this record are fixed a priori: the grid ([20, 140] step 0.5;
[50, 100] step 0.1), the tie points (20, 32.5, 45, 60, 70, 80, 92.5, 110, 125, 140), the member-count points (20, 45,
67.74, 92.5, 140), the share points (50, 67.74, 90) and the build values (60, 70, 80). Absolute values go to the
owner page only, never to the clean-room session or a coordinator.

**The owner's reporting rule (2026-10-20).** Posteriors and likelihood ratios are reported as numbers (shift in sd,
width ratios, the lower range's weight, ln L differences, Bayes factors). No bands, thresholds, z-scores or verdicts.
Each arm's ln L Monte-Carlo variance leads every convergence table; the accuracy of a difference between arms is the
spread over paired bootstrap replicates.

## The question

The fixed-population DESI result at the fiducial cell carries no catalog information: its width equals spectral
only's to within a few per cent. Its completion is smooth: the missing hosts of a pixel follow the mean density. A
Q table (darksirens-lss) makes the missing hosts below the survey depth follow the large-scale structure that the
observed galaxies trace in the same pixel. This record asks how the H0 likelihood and posterior change when the
fiducial-cell grid is evaluated with such tables, against the same grid with Q = 1 and against spectral only.

## What changes against the fiducial-cell grids of 12AG to 12AN, and only this

| | the stored fiducial-cell grids | 12AQ |
|---|---|---|
| missing-host density | `dN_miss` smooth (Q = 1) | `Q x dN_miss` below the depth on fitted rows, gauged per redshift at every proposal (lss `fixed_table_target`) |
| path | the consumer's stock target (gathered missing density) | lss's public target over a core `ds.model` field analysis with the selection completeness and f_p (grid missing density); the stock target rerun beside |
| core | e7c3007 | main 1022429 |
| lss | none | the final head of the fix PR `fix/review-2026-10-21` (full SHA added by amendment when it is pushed: T0) |
| env | `consumer_e7c3007_cuda12` | `consumer_1022429_lss<sha7 of the final head>_cuda12` (the same requirements with the core and lss lines changed) |
| grid | 641 points (coarse + window) | the same floats |

Everything else is the fiducial cell of the stored grids:
- union catalog at nside 128, sigma_kde 1e-3, z_depth 0.245;
- fixed calibration log10 n0 -1.8216 (h-scaled), M0hat -20.4975, sigma_M 0.5592, delta 0;
- Gaussian selection (m_lim 21, K-correction 1.13465, -4.88963, 8.58828) times the native-nside footprint fraction;
- field sky weighting; the per-pixel selection term; GWTC-5 population fixed (spin 0.04/0.10); Om0 0.3089;
- soft guard with variance limit 20; kernel pin off; core's current defaults, set explicitly before each target;
  `DARKSIRENS_ZMAX=6.0`; float64;
- the exact-prior PE build and the O3/O4 injections.

## The Q tables

- **Base and builder:** the selection base (C = f_p Cbar at the fixed calibration), certified against the Phase 12
  f_p by lss's mask-free certificate, with lss's radial builder (per-pixel radial Poisson-lognormal, exact-Hessian
  Laplace table, gauge per redshift, clip at 7).
- **Fitted rows:** covered pixels with at least one galaxy below the depth (119,457). Off-footprint and
  covered-but-empty pixels are exactly Q = 1. Bias 1. Built at H0 70; the inputs do not depend on H0 (check 7).
- **Settings, chosen from galaxies only:** a five-fold cross-validation on 10,000 random fitted rows, holding out
  sub-pixel sky (nside-1024 children of each pixel; masks uniform within a pixel).
  - Score: the held-out Poisson log likelihood with a per-redshift amplitude fitted to the held-out total, Q against
    Q = 1, with the fold sd.
  - Candidates: sigma {0.3, 0.4, 0.45, 0.5, 0.6} x ell_grid {1, 2, 3, 4, 6, 8, 16} nodes.
  - Eligible only if every row converges, the builder's Laplace check passes, no cell sits at the clip, and the
    full covered-sky table passes the mask-free certificate.
  - The primary setting is the best score, with settings within one fold sd tied and the tie broken toward smaller
    sigma, then larger ell_grid. The runner-up is the best eligible setting whose ell_grid differs by a factor of 2
    or more.
  - Random-galaxy holdout reported beside (an upper bound for the use). Seeds 3301-3303.
  - Result: added by a later amendment, before any table is built: the primary and runner-up settings, the
    certificate margins and the sha256 of `q_scans/cv/choice.json`.
- **Rougher-field arm:** ell_grid 2, sigma 1.0, declared in advance: the builder's Laplace check fails there (the
  table overstates a row's missing hosts by up to 8-14%). A sensitivity with a known numerical bias, labelled so.
- **Members:** 16 exact Laplace draws (seed 3304), doubled once to 32 if the member Monte-Carlo noise of ln L at the
  member-count points exceeds a tenth of the size of the Q effect there (with a floor).
- **Placement controls:** the primary table with its fitted rows permuted within 20 f_p quantile strata, seeds
  3305-3308, each re-certified.
- Derived tables (Q = 1, constant per redshift, the placement controls, member 0) are made with lss's own types,
  keep the source's budget stamps and fitted rows, are certified again, and are never consumed ungauged.

## The arms

References:
- the stock target in the new env;
- core's field analysis;
- **Q = 1 through lss** (the reference of every Q difference);
- **spectral only**.

Q arms:
- **the primary table** (Laplace posterior mean);
- the member posterior mean;
- **the 16 members marginalised** (the estimand);
- the runner-up setting;
- the rougher-field setting;
- the four placement controls.

Accuracy: 8 paired bootstrap replicates (the replicate-noise record's files b01-b08) through the primary table,
Q = 1 and spectral.

Conditional, in this order: the spectroscopic-only pair (only if an nside-128 spectroscopic catalog passes the 12AG
catalog gates), then GP3D (only if stage C's GP3D package passes its all-sky budget test).

**If lss refuses every table** (the certificate fails on the final head for the primary and the runner-up): the
primary and the placement controls run through the consumer's scoped wrapper on the stock target, each table gauged
once, labelled "uncertified", provided the wrapper tied to lss in the rehearsal; otherwise the Q arms are held for
the owner.

## Expected size, stated in advance (an estimate, not a rule)

- At this cell Cbar is about 1 below the depth. Q can move only the masked sub-area of covered pixels with galaxies:
  18% of the below-depth missing-host budget. 80.5% is off the footprint, where Q = 1.
- The part of an event's host weight Q can move is about 0.15 of its catalog share: about 0.001 for the median event
  and up to about 0.06 for the nearby, catalog-dominated events. It is larger at low H0.
- Part of Q is the pixel's coupling to f_p rather than structure; the placement controls keep that coupling.
- Expected: ln L_Q - ln L_(Q=1) changes shape by a small fraction (at most about 15% if Q were exact) of today's
  ln L_cat - ln L_spec structure, carried by about 40-80 nearby events. The posterior moves by a small fraction of
  its sd.
- A larger change is a finding to explain with the per-event split.

## Inputs (sha256)

| input | path (under `/hildafs/projects/phy230054p/magana/darksirens-core-data` unless absolute) | sha256 |
|---|---|---|
| union catalog, nside 128 | `phase12_5/smearing_ladder/catalogs/desi_union_nside128.h5` | `f26a20f0f3f8ca5a9bc0aee0681cd0eba6f1a7b693055839cba83d6189cdb62c` |
| footprint, native nside 128 | `phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| GW PE, exact-prior build | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| O3/O4 injections | `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| PE and injection bootstrap replicates b01-b08 and identity | `phase12_5/lnl_convergence/replicates/` | per file in its `manifest.json`; the manifest: `951fc6dab5dc62c44bf472e4ec34ef584178d6b39353a4274cb6a803e17fe2e2` |
| native table (the cross-validation's positions) | `/hildafs/projects/phy230014p/magana/desi_darksirens_selection/final/experiments/experiment_loa_rebuild/inputs/rebuild_loa_faint_pixelate_input.h5` | `42e91b594572cfba716d0128ea3dcb24924a6c63e573078e7c4184fe24c0eaaa` |
| DESI base configuration | consumer `config/desi.fixed_population.json` | `b79ad777f17126bcd78b9ebcff0d02724ae6cfe7ae957829009ca5143f349bb9` |
| stored per-event grid, the selection-denominator record (12AL; primary Q = 1 reference) | `phase12_5/selection_denominators/runs/ns128_sk1e-03/lane_a/scan.json` / `events.npz` | `5a0530d64fa552beb9a510ecfea2958e9e57fa2b7bdddbbb6f917305531cdf21` / `d3db17d77897bbb672b3b4ab7f1bc0002b8f79ab40188e2f1d684afa95424a9d` |
| stored per-event grid, the denominator ladder (12AM; beside) | `phase12_5/d2_ladder/runs/ns128_sk1e-03/lane_a/scan.json` | `faabe1c4a6264c6ceded5abae38ae1fd2c6229c886a33158a0b207a213efce7b` |
| stored per-event grid, the fine denominator record (12AN; beside) | `phase12_5/d1_d4_fine/runs/ns128_sk1e-03/lane_a/scan.json` | `a7bf471d4850701abee05a761cab542a0cb7ab18a4ef01c98551280509ace95a` |
| stored spectral-only grid, 641 points | `phase12_5/d2_ladder/runs/ns128_sk1e-03/cell/spectral/spectral.npz` | `fd738c07367c34d8ab8b02e537e3ada4fc683805687b0bcfb1f8912fccd43067` |
| stored spectral-only grid, 241 points (12AG) | `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json` | `db9f7b80c4b799c18559c99040916a821ed99aa7feb06fcec1d6589a171a6f9f` |
| mock universe (100 quick seeds) and its stored complete-catalog results | `examples_mock/quick/seedNNN/` | per-seed `manifest.json`, seeds 001-100, listed in `phase12_5/q_scans/inputs/mock_quick_seed001-100_manifests.sha256`: `0839c24a4f2f636c11343076ca72e884b4fc37814b3de889a605f82a81be6ff8` |
| Q tables | `phase12_5/q_scans/tables/*.h5` (the rehearsal's under `phase12_5/q_scans/rehearsal/tables/`) | added by amendment before use |

## Code and environment

- **Consumer:** `ignaciomagana/desi_darksirens_selection`, new branch `phase12aq/q-scans` from `phase12ao/ladder`
  (b0e9f03), developed in `phase12_5/repo_12AQ_dev` and run from detached worktrees of `phase12_5/repo_12AQ` at
  committed SHAs. It adds the `phase12aq_*` scripts, job templates and tests, and changes no existing file (19 added
  files at declaration, head `0d45dcb09fa6dde0bdd03c832c2cc54b73f3ec70`; every output records the commit it ran
  from).
- **Env:** `phase12t/envs/consumer_1022429_lss<sha7 of the final head>_cuda12`, core main
  `10224291eac92b391dc2a06925dc08e49980f9e5`. Nothing is installed into any other env. Before the
  lss head is pushed, the old grid env (`phase12t/envs/consumer_e7c3007_cuda12`) with `git archive` copies of core
  main `10224291eac92b391dc2a06925dc08e49980f9e5`, the lss integration head
  `881fce6c875943013c0da48327d4aff5b49b27f7` and darksirens-examples `dea180b540d24a6f5f9daf2c36812639c07b4ad8`
  first on the path (`phase12_5/q_scans/src/`, `ARCHIVES.txt`; taken 2026-10-22T18:57:09Z). The installed core and
  lss are shadowed, so every output records the `__file__` of `darksirens` and `darksirens_lss`, not the installed
  metadata.
- **Record:** `ignaciomagana/darksirens-rebuild`, branch `phase12aq/declare`, clone `phase12_5/rebuild_12AQ`.

## Checks before the go (in order; results recorded below before the Q arms)

Tiers for checks 4, 5 and 11: at most 1e-10 equal; 1e-10 to 1e-6 recorded and continued; above 1e-6 the stated
fallback.
1. The env: pinned commits, lss capability checks, 1,086 redshift nodes, the lss footprint equal bit for bit to the
   Phase 12 f_p, diagnostics on the targets, a tiny mock target with every keyword used here, the GPU in float64.
2. Core main on the stock target against the stored grids (641 points, ln L, ln mu, N_eff, per-event ln Z, flags):
   1e-6. Spectral: the stored path rerun against the stored grid, and the spectral arm against the rerun. A stock
   miss is bisected to a core commit and recorded; the Q comparisons stay within the new env.
3. The gathered against the grid form of the missing density, built with the settings set explicitly and the form
   asserted, same process, at the ten tie points: 1e-10 (also before the lss head is pushed).
4. Core's field analysis against the stock target, same process: tiers (also before the lss head is pushed).
5. Q = 1 through lss against core's field analysis, grid form, same process: tiers.
6. A constant-per-redshift table through lss against Q = 1 (the gauge at consumption): 1e-10; check 8 stands in if
   that table cannot be certified.
7. H0 does not enter the tables: the builder inputs gridded at H0 60, 70 and 80 equal to 1e-13 relative; the tables
   equal to the solver's convergence bound (about 1e-8 in log Q), rounding-size differences recorded.
8. The consumed primary and placement tables keep the missing-host count per redshift on fitted rows at the
   member-count points: 1e-10 relative.
9. Member 0 inside the marginalised target against a single-table target of member 0: 1e-10.
10. Table stamps: convergence, Laplace check (failing only for the rougher-field arm, as declared), clip share, the
    mask-free certificate with its margin (before the choice, at the lss head before any build, at each build and on
    the member stack), the map of the 16-member build equal to the map-only build.
11. The primary table through lss's core-extension path against lss's target, at the tie points: tiers (recorded).
12. The identity replicate files through the replicate path equal the nominal arms bit for bit.
13. **Mock validation** on the 100 shared-mock seeds, run before the lss head is pushed and tied on 10 seeds
    afterwards. It has no pass rule and never holds the real grids; the summary waits for it, or for 8 h after the
    lss head is pushed. Arms: spectral, Q = 1, radial Q cross-validated per seed, the narrow-photo-z twins, members
    marginalised (10 seeds), an oracle Q from the true field, an antipodal Q, and the complete catalogs (stored
    results, tied on 5 seeds). The truth-calibrated selection is used in the likelihood. Primary reading: the mean
    log posterior density at the true H0 and the paired shift against Q = 1. The mock has no sub-pixel structure,
    so its DESI-like Part 2 (shallow depth, a 36% footprint cap, sub-pixel masks with f_p 0.875) is an upper bound
    for DESI.

## What is reported

Per arm, against Q = 1 through lss and against spectral only:
- the H0 posterior (flat prior; absolute values on the owner page only); shift of the median in the reference's sd;
  sd ratio; 68% and 90% width ratios; Hellinger distance; the weight of H0 20-45; `window_holds`;
- ln L_Q - ln L_(Q=1) and ln L_cat - ln L_spec per point, on the coarse grid and the window, each split into an event
  part and a selection part (the difference of core's selection log correction) that sum to the difference;
- the Bayes factor of each Q table against Q = 1 over the flat H0 prior on [20, 140] and on [50, 100], on zero-wall
  points only (exclusions reported), with each arm's low-H0 weight;
- the accuracy of every difference and Bayes factor: the spread over 8 paired bootstrap replicates;
- per event, the spread of ln Z_Q - ln Z_(Q=1) over the window against its Q-sensitive host share;
- each arm's ln L Monte-Carlo variance per point (PE, selection, members, total), its maximum inside the 90%
  interval and its change against Q = 1; penalised and accepted counts;
- the Q tables' galaxy-side diagnostics (cross-validation surfaces, certificate table, stamps, sd of log Q, clip
  share, correlation with the footprint and the imaging-depth maps, the f_p-coupled share of the redistribution);
- the mock tables; timing and memory.

## Compute

- The miko holder's H100 NVL through `srun --overlap`: one reniced step at a time in one background chain, a 48 GB
  host-RSS watchdog, no step after 25 Oct 03:00 UTC.
- rita A100-80 for the member arms, and for everything if the holder is gone.
- HENON CPU for the cross-validation, the tables and the mock.
- Estimate: about 1 GPU-hour on the H100 before the lss head is pushed and about 3.5 after, about 1.3 on rita, about
  3 HENON node-hours of builds and about 50 task-hours of mock (before the push).
- Wall time about 5.5 h after the lss head is pushed.

## Limits, stated in advance

- One cell, one calibration (fixed), one PE build, one variance limit (20).
- Fixed tables cannot follow a sampled calibration; chains with Q need the latent targets.
- Radial tables move only the masked sub-area of covered pixels below the depth: nothing above the depth or off the
  footprint.
- Redshift errors are not modelled by the builder: the union's Q is the field seen through the photometric redshifts
  of most of its galaxies (median dz about 0.023, about 10 redshift nodes).
- GW hosts are assumed to trace the galaxies with bias 1. Part of Q is the pixel's coupling to f_p.
- The Laplace table is biased at about one galaxy per node; the setting filter and the marginalised arm bound this.
- The mask-free certificate passes with a thin margin (about 0.09 against 0.10).
- 16 members; 9 of the 100 mock seeds carry recorded gate failures (reported with and without them); the mock has no
  sub-pixel structure.
