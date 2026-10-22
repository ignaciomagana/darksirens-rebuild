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

**Amendment, the hyperparameter choice (2026-10-22, about 22:00 UTC, before any table is built):** primary sigma 0.5,
ell_grid 2; runner-up sigma 0.5, ell_grid 4; 20 of 35 settings eligible. **The early checks before T0 pass:** core
main against the stored grids within 1.1e-12, the gathered form equal to the grid form bit for bit, core's field
analysis equal to the stock target within 9.1e-13. **The sealed rehearsal stopped at its table builds:** the primary
setting fails the builder's Laplace check on its full covered-sky build (largest relative excess 0.0514 against
0.05). All three are under "Amendments" at the end.

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

## Amendments

### Amendment: the hyperparameter choice (2026-10-22, before any table is built; location-free)

The cross-validation ran on HENON from 19:26 to 19:54 UTC (jobs 1391843 reconstruct, 1391844 smoke, 1391845 spatial
scores, 1391855 random-galaxy scores, 1391856 full-sky builds and certificates, 1391857 choice; logs
`q_scans/logs/aq-cv-*.out`). Code: consumer `phase12aq/q-scans` at `77443ab884d3ace27d41b5f2e6363548eb36d6b1`
(detached worktree `q_scans/wt/77443ab`; `scripts/phase12aq_cv.py` is unchanged from there to the declared head
0d45dcb), the old grid env's python with the frozen core main `10224291eac92b391dc2a06925dc08e49980f9e5` and the
frozen lss integration head `881fce6c875943013c0da48327d4aff5b49b27f7` first on the path (both recorded by `__file__`
in every output). No GW data entered any step.

**The rule, as declared and as applied** (`choice.json` "rule"):
- eligible = the 10,000-row subset build converged on every row, passed the builder's Laplace check (k-hat <= 0.7,
  every relative excess <= 0.05) and had no fitted cell at the clip after the gauge, **and** the full covered-sky
  build (119,457 fitted rows) passed lss's mask-free certificate (worst |corr(Q, f_p) - corr(N/f_p, f_p)| <= 0.10 over
  9 redshift slices);
- primary = among eligible settings, those whose spatial score is within one fold sd (the best setting's) of the best
  are tied; the tie breaks toward smaller sigma, then larger ell_grid;
- runner-up = the best eligible setting whose ell_grid is at least 2x or at most 0.5x the primary's, same tie rule.

**Before the scores:**
- The reconstruction check passed: the sub-pixel positions rebuilt from the native table give the union file's
  per-pixel counts exactly (22,785,279 galaxies, 119,524 occupied pixels), so the spatial (sub-pixel sky) holdout is
  the primary scheme, as declared.
- The grid has 119,457 fitted rows (as expected), no galaxy in a zero-rate cell, and C equal to f_p Cbar to 4.6e-16.
  It counts 10,154,576 galaxies in cells above the depth (the design quoted 10,258,522 from an earlier probe;
  recorded beside, not a check).
- The cross-validation rows: 10,000 fitted rows (seed 3301), 1,050,615 galaxies below the depth; held out per fold
  about 213,000 (spatial, seed 3302) and about 210,000 (random galaxies, seed 3303).

**The choice:**

| role | sigma | ell_grid | spatial score, nat per held-out galaxy (fold sd) | random-galaxy score (fold sd) | certificate worst \|delta\| | margin to 0.10 |
|---|---|---|---|---|---|---|
| **primary** | 0.5 | 2 | 0.1712 (0.0014) | 0.1875 (0.0008) | 0.0891 | +0.0109 |
| **runner-up** | 0.5 | 4 | 0.1586 (0.0016) | 0.1749 (0.0009) | 0.0858 | +0.0142 |

- **No tie for the primary:** the next eligible setting (sigma 0.45, ell_grid 2) scores 0.1651, 4.2 fold sd below.
- **The runner-up's candidates** were the eligible settings with ell_grid 4, 6, 8 or 16 (ell_grid 1 is not eligible
  at any sigma). Sigma 0.5, ell_grid 3 (0.1650) is closer in score but excluded by the factor-of-2 rule, as declared.
- The random-galaxy holdout ranks the eligible settings the same way at the top: the same primary.
- The scores are Q against Q = 1 with a per-node amplitude fitted to the held-out total, so they score only the
  redistribution. Both settings beat Q = 1 on held-out sub-pixel sky by 0.16-0.17 nat per held-out galaxy.
- **Where the primary sits:** the surface still rises toward larger sigma, and every sigma 0.6 setting fails the
  builder's Laplace check on the subset. The primary is the largest eligible sigma, at the edge of the region where
  the Laplace table is accurate. That is what the declared filter is for. The rougher-field arm (ell_grid 2, sigma
  1.0) stays the declared sensitivity beyond that edge.
- **The certificate decides much of the eligible region:** ell_grid 1 fails it at every sigma (worst 0.104-0.106),
  and ell_grid 8 and 16 fail it at sigma 0.3 and 0.4. Margins of the eligible settings are 0.002-0.030. The primary's
  is 0.011, a thin margin as stated in the limits.

**Eligible settings (20):** sigma 0.3 x ell_grid {2, 3, 4, 6}; sigma 0.4 x {2, 3, 4, 6}; sigma 0.45 x {2, 3, 4, 6, 8,
16}; sigma 0.5 x {2, 3, 4, 6, 8, 16}.

**The full table** (35 settings; scores Q minus Q = 1 summed over 5 folds per held-out galaxy; fold sd over folds;
the certificate on the full covered-sky build; `choice.json` "table", "surfaces" and "certificate_table"):

| sigma | ell_grid | spatial score (fold sd) | random-galaxy score (fold sd) | subset stamps | certificate worst \|delta\| | margin | eligible |
|---|---|---|---|---|---|---|---|
| 0.3 | 1 | 0.1132 (0.0007) | 0.1218 (0.0004) | pass | 0.1061 | -0.0061 | no |
| 0.3 | 2 | 0.1296 (0.0009) | 0.1400 (0.0006) | pass | 0.0938 | +0.0062 | yes |
| 0.3 | 3 | 0.1324 (0.0010) | 0.1435 (0.0006) | pass | 0.0907 | +0.0093 | yes |
| 0.3 | 4 | 0.1318 (0.0011) | 0.1434 (0.0007) | pass | 0.0902 | +0.0098 | yes |
| 0.3 | 6 | 0.1282 (0.0012) | 0.1401 (0.0007) | pass | 0.0891 | +0.0109 | yes |
| 0.3 | 8 | 0.1239 (0.0012) | 0.1358 (0.0008) | pass | 0.1063 | -0.0063 | no |
| 0.3 | 16 | 0.1088 (0.0014) | 0.1199 (0.0009) | pass | 0.1390 | -0.0390 | no |
| 0.4 | 1 | 0.1481 (0.0010) | 0.1604 (0.0006) | pass | 0.1045 | -0.0045 | no |
| 0.4 | 2 | 0.1567 (0.0012) | 0.1704 (0.0007) | pass | 0.0936 | +0.0064 | yes |
| 0.4 | 3 | 0.1540 (0.0013) | 0.1682 (0.0008) | pass | 0.0894 | +0.0106 | yes |
| 0.4 | 4 | 0.1498 (0.0013) | 0.1641 (0.0008) | pass | 0.0884 | +0.0116 | yes |
| 0.4 | 6 | 0.1417 (0.0014) | 0.1561 (0.0008) | pass | 0.0978 | +0.0022 | yes |
| 0.4 | 8 | 0.1350 (0.0014) | 0.1491 (0.0009) | pass | 0.1093 | -0.0093 | no |
| 0.4 | 16 | 0.1161 (0.0015) | 0.1289 (0.0011) | pass | 0.1081 | -0.0081 | no |
| 0.45 | 1 | 0.1602 (0.0012) | 0.1740 (0.0007) | pass | 0.1050 | -0.0050 | no |
| 0.45 | 2 | 0.1651 (0.0013) | 0.1803 (0.0008) | pass | 0.0916 | +0.0084 | yes |
| 0.45 | 3 | 0.1604 (0.0014) | 0.1758 (0.0008) | pass | 0.0885 | +0.0115 | yes |
| 0.45 | 4 | 0.1550 (0.0015) | 0.1704 (0.0008) | pass | 0.0872 | +0.0128 | yes |
| 0.45 | 6 | 0.1456 (0.0015) | 0.1608 (0.0009) | pass | 0.0942 | +0.0058 | yes |
| 0.45 | 8 | 0.1381 (0.0015) | 0.1530 (0.0010) | pass | 0.0889 | +0.0111 | yes |
| 0.45 | 16 | 0.1182 (0.0015) | 0.1317 (0.0011) | pass | 0.0883 | +0.0117 | yes |
| 0.5 | 1 | 0.1692 (0.0013) | 0.1845 (0.0007) | pass | 0.1047 | -0.0047 | no |
| 0.5 | 2 | 0.1712 (0.0014) | 0.1875 (0.0008) | pass | 0.0891 | +0.0109 | yes **primary** |
| 0.5 | 3 | 0.1650 (0.0015) | 0.1813 (0.0009) | pass | 0.0874 | +0.0126 | yes |
| 0.5 | 4 | 0.1586 (0.0016) | 0.1749 (0.0009) | pass | 0.0858 | +0.0142 | yes **runner-up** |
| 0.5 | 6 | 0.1482 (0.0016) | 0.1642 (0.0009) | pass | 0.0827 | +0.0173 | yes |
| 0.5 | 8 | 0.1403 (0.0015) | 0.1559 (0.0010) | pass | 0.0797 | +0.0203 | yes |
| 0.5 | 16 | 0.1198 (0.0016) | 0.1338 (0.0012) | pass | 0.0696 | +0.0304 | yes |
| 0.6 | 1 | 0.1803 (0.0016) | 0.1979 (0.0008) | fail: Laplace check | not built (stamps failed) | — | no |
| 0.6 | 2 | 0.1783 (0.0017) | 0.1966 (0.0009) | fail: Laplace check | not built (stamps failed) | — | no |
| 0.6 | 3 | 0.1702 (0.0017) | 0.1882 (0.0010) | fail: Laplace check | not built (stamps failed) | — | no |
| 0.6 | 4 | 0.1628 (0.0017) | 0.1805 (0.0010) | fail: Laplace check | not built (stamps failed) | — | no |
| 0.6 | 6 | 0.1513 (0.0017) | 0.1685 (0.0010) | fail: Laplace check | not built (stamps failed) | — | no |
| 0.6 | 8 | 0.1428 (0.0017) | 0.1595 (0.0010) | fail: Laplace check | not built (stamps failed) | — | no |
| 0.6 | 16 | 0.1219 (0.0016) | 0.1367 (0.0013) | fail: Laplace check | not built (stamps failed) | — | no |

The certificate per slice for the two chosen settings (signed corr(Q, f_p) - corr(N/f_p, f_p) at the 9 measured
redshift nodes; the certificate bounds its absolute value by 0.10):

| node | 0 | 15 | 30 | 46 | 61 | 76 | 92 | 107 | 122 |
|---|---|---|---|---|---|---|---|---|---|
| primary (0.5, 2) | +0.0020 | +0.0891 | +0.0540 | +0.0889 | +0.0323 | +0.0321 | +0.0474 | -0.0193 | -0.0024 |
| runner-up (0.5, 4) | -0.0123 | +0.0858 | +0.0283 | +0.0566 | -0.0193 | -0.0149 | -0.0107 | -0.0707 | -0.0429 |

**Files** (under `q_scans/cv/`; `choice.json` lists the sha256 of the others):

| file | sha256 |
|---|---|
| `choice.json` | `a7a77fabed6908dc720c567168d0ccded347ac9fed4aa4c6f84a06a300fb4382` |
| `certify.json` | `34e4175a6eb7f76417fc5c1faee8d0a4469500438788045968160293d9c58917` |
| `filter.json` | `bddf0dec38b8b40b4fe862f38cd0c5b8d62c395f58a63f8a09d1d3a07da0f3be` |
| `spatial.json` | `3600b884327c0c5710e78a03e47aeea04daa7c7444eda0ede226d3ba646582c8` |
| `random.json` | `a29bc54f3e90c7dde33d3f2a654a840e2dee0244c67b7e4b5fc641bc79464936` |
| `reconstruct.json` | `cc639f38e7db6215a94addd234a78e6b55eaec07149f774d69730fe82fce6418` |
| `rows.npy` (the 10,000 rows) | `839abdd6ebd9fca7fb90cc45fab590f5ddec2d7b433fd0a6efd8d7fd417ae183` |

**What this fixes for the tables:** `--ell-grid 2 --sigma 0.5` for `q_main_map`, `q_main_m16`, `q_main_map_h60`,
`q_main_map_h80` and every table derived from them; `--ell-grid 4 --sigma 0.5` for `q_runnerup_map`. At T0 the
pre-check rebuilds both on the final lss head with their certificates, and recomputes the primary's spatial score on
all 5 folds. If that score moves by more than one fold sd (0.0014), the whole cross-validation is rerun on the final
head before any table is built. The replacement rule (at most once) and the certificate fallback stand as declared.

### Amendment: the early checks before T0 (2026-10-22; location-free)

One background chain on the miko holder (job 1388940), 21:30:51 to 21:37:05 UTC. Every GPU step went through the
committed holder wrapper (`slurm/phase12aq_miko.sh`: `srun --overlap`, reniced, 48 GB host-RSS watchdog, one step
at a time). The chain script is outside the repo: `q_scans/scratch_launcher/early_chain.sh` (sha256
`ccb933de07180b5abd032a48495f578438a7a4bc60a6f1f6a9e548d02f11e88d`). It ran from the detached worktree
`q_scans/wt/0d45dcb` (consumer `0d45dcb09fa6dde0bdd03c832c2cc54b73f3ec70`, clean) with the old grid env's python and
the frozen core main `1022429` alone on the path (no lss in these arms). Marks: `q_scans/runs/early_chain/EARLY_DONE`
and `EARLY_CHAIN_END` (every step rc 0). The four inputs matched their declared sha256 in every step.

**Check 2 (early): core main on the stock target against the stored grids.** Lane A's driver, unchanged, on all 641
points (4.5 min on the H100, peak host RSS 3 GB), compared on the host (`q_scans/gates/early_core_tie/core_tie.json`,
differences only):

| against | points | ln L | ln mu | N_eff (relative) | per-event ln Z | selection log correction | PE / selection MC variance | flags, finite pattern |
|---|---|---|---|---|---|---|---|---|
| 12AL (primary Q = 1 reference) | 641 of 641 | 1.1e-12 | 3.6e-15 | 7.3e-15 | 3.6e-15 (event names equal) | 1.1e-12 | 3.1e-16 / 1.6e-14 | equal |
| 12AM, 12AN (beside) | 641 of 641 | the same | the same | the same | — | the same | the same | equal |

- Pass at the declared 1e-6, with no point above it. Nothing between e7c3007 and core main moves the stock target
  at this cell, so no bisection is needed.
- The spectral half of check 2 (the stored path rerun and the spectral arm) runs after T0 in the plumbing stage, as
  declared.

**Checks 3 and 4 (early): the same-process step** at the ten tie points, arms `stock`, `stock_grid`, `core_field`
and `core_field_grid`, each built after core's settings were set explicitly and its form asserted
(`q_scans/gates/early_same_process/{same_process,tiers}.json`, differences only; 82 s, peak RSS 14 GB):

| check | comparison | forms (arm vs reference) | worst \|Delta ln L\| | other fields | result |
|---|---|---|---|---|---|
| 3, gathered equals grid | `stock_grid` vs `stock` | grid vs gathered | 0 | every field bit for bit (ln mu, N_eff, per-event ln Z and MC variance, selection log correction); flags equal | pass (1e-10) |
| 4, core field = stock (gathered) | `core_field` vs `stock` | gathered vs gathered | 9.1e-13 | ln mu 3.6e-15, N_eff 6.9e-15 relative, per-event ln Z 1.8e-15, per-event MC variance 6e-17; flags equal | tier "equal" |
| 4, core field = stock (grid) | `core_field_grid` vs `stock_grid` | grid vs grid | 9.1e-13 | the same | tier "equal" |

- Check 4's identity block: the decoded population (all 17 entries, the two fixed spin values), log10 n0, the
  selection fields, sigma_kde and delta are equal exactly between the field analysis and the stock target.
- No arm was stopped (`stop_q_arms` false). Check 6 is listed as "check 8 stands in" only because no constant table
  existed yet. It is decided after T0.
- With checks 3 and 4 equal, Q = 1 through lss stays the reference of every Q difference, as declared.

**Provenance caveat.** Lane A's `scan.json` (and therefore the `run_packages` block of `core_tie.json`) records the
*installed* package metadata of the old env: darksirens `e7c3007`. That metadata is not what ran. The frozen-core
provenance is in `provenance.json` beside each run (`q_scans/runs/early_core_tie/provenance.json`,
`q_scans/gates/early_same_process/provenance.json`): `darksirens` resolves to
`q_scans/src/core_1022429/src/darksirens/__init__.py`, and the archives file records core
`10224291eac92b391dc2a06925dc08e49980f9e5`, lss `881fce6c875943013c0da48327d4aff5b49b27f7` and examples
`dea180b540d24a6f5f9daf2c36812639c07b4ad8`, taken 2026-10-22T18:57:09Z. `same_process.json` records the same module
file and `frozen_sources.darksirens: true`. `darksirens_lss` resolves to the installed copy in these two runs. It
is not used by any of these arms.

### Amendment: the sealed rehearsal stopped at its table builds (2026-10-22, 21:46 to 21:50 UTC; location-free)

**What ran.** Two HENON builds at the declared primary setting (sigma 0.5, ell_grid 2), built at H0 70 with the
declared member seed 3304:
- job 1391874, `q_main_map` (no members, 16 CPUs);
- job 1391875, `q_main_m4` (4 members, for the member-wiring rehearsal).

They ran from consumer `0d45dcb` (detached worktree, clean) with the old env's python, the frozen core main 1022429
and the frozen lss integration head 881fce6. The launcher is outside the repo:
`q_scans/scratch_launcher/rehearsal_tables.sh` (sha256 `bb64670860421f8365283bf485fbd0cd58e19dc678caa85264163b161dfcc5b6`), job ids in `q_scans/logs/rehearsal_table_jobs.txt`.

**What failed: the builder's Laplace check, in both builds.**
- Both builds converged on all 119,457 fitted rows: Newton took at most 7 iterations, the whitened gradient is below
  1e-8, and the missing-host budget at the clip is 0.0076.
- Both stopped at the Laplace check, which section 5.1 requires of every table but the rougher-field one. On 64 rows x
  256 draws, k-hat is 0.679 (limit 0.7) and the largest relative excess 0.0514 (tolerance 0.05).
- The records: `q_scans/rehearsal/tables/FAILED_q_main_map.json` (sha256 `712a7193ff571b2f39392a15dc805f55f38f8b52967085410a0ac0bea428101b`) and `FAILED_q_main_m4.json`
  (sha256 `6e00763ebffdadd1dfdca4d589a7780b05b093886b8fb0dcee665906174f7638`).
- The certificate was not reached.

**What followed:**
- No rehearsal table exists, so there are no sha256s to commit.
- Slurm cancelled the derived-table job (1391876) and the member check (1391878): their dependency could not be met.
- The table check (1391877) found no table and exited 4 (check 8 not evaluated).
- The holder rehearsal chain was not started.
- The rehearsal stopped here. Nothing in the design, the code or the tables was changed.

**Why the cross-validation did not catch it.** The declared eligibility is the builder's stamps on the 10,000-row
subset plus the certificate of the full covered-sky build. That build also ran the Laplace check (64 rows x 256
draws, seed 3301; `certify.json`, and `full_sky_build_ok` in `choice.json`), but its result is not part of the
declared rule. It failed for 5 of the 20 eligible settings, the runner-up among them:

| setting (sigma, ell_grid) | 10,000-row subset: k-hat, largest relative excess | full covered sky, seed 3301: k-hat, largest relative excess | full-sky check |
|---|---|---|---|
| 0.5, 2 (primary) | 0.467, 0.0491 | 0.528, 0.0499 | pass |
| 0.5, 4 (runner-up) | 0.480, 0.0486 | 0.552, 0.0514 | fail (excess) |
| 0.5, 3 | 0.478, 0.0484 | 0.489, 0.0505 | fail (excess) |
| 0.5, 6 | 0.529, 0.0468 | 0.707, 0.0499 | fail (k-hat) |
| 0.45, 6 | 0.537, 0.0417 | 0.754, 0.0438 | fail (k-hat) |
| 0.4, 6 | 0.560, 0.0363 | 0.760, 0.0375 | fail (k-hat) |
| the primary's production build, seed 3304 (this rehearsal) | — | 0.679, 0.0514 | fail (excess) |

- **At sigma 0.5, the Laplace table's largest relative excess sits on the 0.05 tolerance:** 0.0484 to 0.0514 across
  builds and seeds. In most full-sky builds of the cross-validation it comes from the same pixel row. Whether a build
  passes depends on the check's random rows and draws. The primary passed by 1e-4 at seed 3301 and fails by 1.4e-3
  at seed 3304. Every eligible setting with sigma 0.45 or below and ell_grid 2 to 4 passes the full-sky check, with
  excess 0.0194 to 0.0445.
- **After T0, under the declared rules (nothing changed here),** the pre-check builds the primary and the runner-up
  on the final head with the same seed, 3304.
  - If the final head leaves the solver and the check unchanged, the primary fails its Laplace check again.
  - The replacement rule (at most once) then makes the runner-up the primary if it passes at seed 3304. It failed at
    seed 3301.
  - If both fail, and not on the certificate alone, the pre-check writes HOLD=1 and every Q arm is held for the owner.
- **Open for the owner or the main session; no choice is made here.** The eligibility rule never asked the full-sky
  build for the Laplace check that every production table must pass.
