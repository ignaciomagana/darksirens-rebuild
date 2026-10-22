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

**Amendment, the Laplace check (2026-10-22, about 23:45 UTC, before any table is built):** the eligibility now asks
the full covered-sky build, made as production makes it, for the builder's Laplace check at 4,096 draws (first
declared at 256, where the check reads its own Monte-Carlo noise) at seeds 3304 and 3301; every table build and the
T0 pre-check run the check at 4,096 draws. Rows, seed rule and tolerances are unchanged. Re-applied to all 35
settings, the eligible set, the primary (sigma 0.5, ell_grid 2) and the runner-up (sigma 0.5, ell_grid 4) are
unchanged. The choice is now `q_scans/cv/choice_v2.json`; the first is kept as `choice_v1.json`.

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
    full covered-sky table passes the mask-free certificate. *(Amended before any table was built: the Laplace check
    is asked of the full covered-sky build at 4,096 draws at seeds 3304 and 3301; see "Amendment: the Laplace
    check of the eligibility and of every table".)*
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

### Amendment: the Laplace check of the eligibility and of every table (2026-10-22, 22:40 to 23:40 UTC, before any table is built; location-free)

**Why an amendment.** The sealed rehearsal stopped because the primary's full covered-sky build failed the builder's
Laplace check at the production seed 3304 (amendment above). The declared eligibility had asked that check of the
10,000-row subset build only, never of the full covered-sky build that production makes. Under the declared rules the
pre-check after T0 would decide the Q arms on that check. No table exists and no GW likelihood with any Q table has
run, so the rule can still be amended before any table is used. Everything below is galaxy side and H0-free.

**What was measured first: how precise the check is** (`q_scans/cv/laplace_robustness.json` sha256
`c9c672f60845c1b6c3fd64822934b6d8d8110aa3a182ca4b28d3a5581c5a937b` and `laplace_robustness.md` sha256
`17f8e25e09ca069c62b2c432a9f729d6c8674dd5a6c358875d0c2a11f7074530`; HENON array 1391905 for 27 settings at consumer
2ee6633, one holder step for sigma 0.5 with ell_grid 16 at 8b59430, combined at 0a2139f; launcher
`q_scans/scratch_launcher/laplace_robust.sh` sha256 `882fa1e44acc77e79ed1fa48b99886999e1b69837e343c69f183fd0d68e65be3`).
For each of the 28 settings that passed the cross-validation filter: the full covered-sky build exactly as the T0
builder makes it (seed 3304), then the builder's own check function re-run at seeds 3301-3308, at 128 further seeds,
and at high precision (the builder's check with 256 rows and with the 64 declared rows, 4,096 draws per replicate, 8
replicates).
- **The true worst relative excess is well inside the tolerance for every setting.** At high precision it is
  0.012-0.014 at sigma 0.3, 0.023-0.025 at 0.4, 0.030-0.031 at 0.45 and 0.037-0.039 at 0.5, almost independent of
  ell_grid; the closest setting is about 10 Monte-Carlo errors below 0.05. The declared primary (sigma 0.5,
  ell_grid 2) is 0.0384 +- 0.0009. The excess grows roughly as sigma squared (about 0.15 sigma^2), as lss's own
  description of the Laplace mean's low-count bias says.
- **The declared check (64 rows x 256 draws) reads its own Monte-Carlo noise.** For the primary it reads 0.046-0.086
  across seeds 3301-3308 (3 of 8 pass) and passes at 31% of the 128 further seeds. Per row the 256-draw reads are
  unbiased (they agree with the high-precision values within 0.0054 on average) but heavy-tailed, and the check takes
  the largest of 64 rows. Its k-hat reads 0.65-1.01 at 256 draws against 0.22-0.39 at 4,096: lss's tail-shape
  estimator shrinks toward 0.5 with weight 10/(n_tail + 10), 17% with the 48-draw tail of 256 draws.
- **The builder's own check at 4,096 draws (64 rows) passes at all 8 replicate seeds for all 28 settings**
  (largest excess 0.0463, largest k-hat 0.615).
- A correction to the rehearsal amendment's reading: at 256 draws the runner-up (sigma 0.5, ell_grid 4) passes at
  seed 3304 (0.0486, k-hat 0.559); it failed at seed 3301. Under the unamended rules the pre-check would have
  promoted it on a margin of 0.0014, inside the check's noise.
- **Disclosed: values known before the rule was fixed.** A probe (HENON job 1391879, `q_scans/probes/laplace_noise/`,
  `laplace_noise.json` sha256 `32ba3cd48a5e27dbbe5533e7643d2f995278c6d2fbf807eb0ffa0da442457d13`) built the two
  declared settings with the 4,096-draw check at seeds 3304 and 3301 before the amended rule was written: largest
  excess 0.0396 and 0.0424 (primary), 0.0439 and 0.0407 (runner-up), all passing. No other setting's 4,096-draw value
  at those seeds was known.

**Options considered** (the owner was away; the researched recommendation is taken):
- keep the 256-draw check and require a pass at every seed 3301-3308 plus a high-precision run: closes the gap but
  selects on the check's noise; it would push the choice to sigma 0.3-0.4 for a reason unrelated to the table's
  accuracy (cross-validation score 0.132 against 0.171);
- change only the check (another seed, a larger tolerance, or more draws) without an eligibility change: seed or
  tolerance picking after the failure, and the eligibility gap stays;
- waive the Laplace check for the map table: breaks section 5.1 and check 10, erases the distinction from the
  rougher-field arm, and is not needed;
- keep the declared rules: the runner-up would be promoted on a margin inside the noise, the data-preferred setting
  replaced for a reason that is the check's noise, and the setting-sensitivity arm lost;
- **taken: add the full covered-sky build's check to the eligibility and make the check precise wherever 12AQ uses
  it.** The measurements support it: the true excess of every setting is far inside the tolerance, and the
  4,096-draw check resolves it. The standard (64 rows, k-hat <= 0.7, every relative excess <= 0.05) is unchanged;
  only the measurement's precision changes, uniformly for every setting and every build.

**The amended rule** (`choice_v2.json` "rule"; consumer `phase12aq/q-scans` at
`ef77d5db2aecd5bd6cea85d5cda79394c0b0e89e`, committed 23:00:16 UTC, and `ffccb39cc54603a632d9dc1dc6e1cd7de81b3f19`,
23:03:58 UTC, which only frees memory between the two builds; both commits come before the full-sky jobs below):
- eligible = the 10,000-row subset build converged on every row and had no fitted cell at the clip after the gauge
  (its 256-draw Laplace check is recorded, not used), **and** the full covered-sky build, made with the production
  builder call (the production grid at the build H0 70 with the stock target's decoded calibration; the 119,457
  fitted rows; bias 1, the per-redshift gauge, the clip at 7; the builder's Laplace check on 64 rows evenly spaced in
  expected count with **4,096 draws**), converged on every row, **passed the builder's Laplace check at seed 3304 (the
  production seed) and at seed 3301 (the cross-validation's check seed)**, gave the same table at both seeds (bit for
  bit), and passed lss's mask-free certificate (unchanged);
- primary, tie and runner-up rules unchanged (best spatial score; settings within the best setting's fold sd tied,
  the tie broken toward smaller sigma, then larger ell_grid; runner-up = the best eligible setting whose ell_grid is
  at least 2x or at most 0.5x the primary's);
- **production:** every table build (`phase12aq_build.production_build`: the map tables, the member build, the H0 60
  and 80 builds, the rougher-field build) and the T0 pre-check run the builder's check at 4,096 draws, with the same
  64-row rule, the build seed 3304 and lss's tolerances. The table check (check 10) refuses a table stamped at another
  precision. The rougher-field arm stays a declared Laplace failure.
- unchanged: the candidates, the scores, the certificate and its tolerance, the seeds, the replacement rule (at most
  once, after T0), decision 19's fallback.

**What ran.** `phase12aq_cv.py fullsky` for all 35 candidates, from the detached worktree `q_scans/wt/ffccb39`
(clean) with the old env's python, the frozen core main `10224291eac92b391dc2a06925dc08e49980f9e5` and the frozen
lss integration head `881fce6c875943013c0da48327d4aff5b49b27f7` (both recorded by `__file__` in every output): HENON
array 1391955 (tasks 0-5, six groups of five settings, 8 CPUs each, 23:04-23:34 UTC; task 6 failed at the node's
TaskProlog on henon05 before running anything and its five settings ran as job 1391972, 23:26-23:37 UTC). The
dependent choice job 1391956 was cancelled (its dependency could no longer be met) and `choose` (rule v2) ran once all
35 records existed, on the host at nice 19 from the same worktree (23:39 UTC; log `q_scans/logs/aq-choose2.local.out`).
Launcher outside the repo: `q_scans/scratch_launcher/fullsky.sh` (sha256
`567cd91f27648f101ae5105b42a0a2ae027fbfff6f84c61e6359ab92fe8d1f99`); job ids in `q_scans/logs/fullsky_jobs.txt`.
- **Inputs:** the production grid (119,457 fitted rows) equals the cross-validation arrays bit for bit on the 10,000
  rows (counts, C, dN_exp, the redshift grid; the decoded calibration round-trips exactly).
- **The check seed moves no table value:** the seed-3304 and seed-3301 tables are identical bit for bit in all 35
  settings, and all 35 check the same 64 rows.
- **The certificate is unchanged:** on the 28 settings that `certify` had measured, the worst |delta| is identical
  (difference 0.0) with the same verdict. The 7 sigma 0.6 settings were certified here for the first time: ell_grid 1
  fails (0.1025), the other six pass (margins +0.013 to +0.029).
- **The Laplace check at 4,096 draws** passes at both seeds for every setting with sigma 0.5 or below (largest
  relative excess 0.0461, sigma 0.5 with ell_grid 8 at seed 3304; largest k-hat 0.49) and fails at both seeds for
  every sigma 0.6 setting (0.053-0.062; k-hat at most 0.51). At sigma 0.6 the excess sits above the tolerance at both
  seeds, as the measured scaling with sigma squared expects (about 0.055).
- The declared pair reproduces the probe's values (across jobs, within 3e-11 in the excess and 4e-8 in k-hat):
  primary 0.0396 (seed 3304) and 0.0424 (seed 3301);
  runner-up 0.0439 and 0.0407. The runner-up's worst row at seed 3304 (row 114261, a heavy-tailed low-count row) has
  an importance-sampling error of 0.0066, about one error from the tolerance; the primary's worst rows have errors of
  0.0017-0.0021.

**The amended choice** (`q_scans/cv/choice_v2.json`, schema `phase12aq-cv-choice-2`, sha256
`390c28c5d2bed0a23258b96b7623a5e80bd23738d36199abd36f9206b9a9a4f5`; it lists the sha256 of every cross-validation file and of the 35 records
`q_scans/cv/fullsky/<setting>.json`):

| role | sigma | ell_grid | spatial score, nat per held-out galaxy (fold sd) | full sky, 4,096 draws: largest relative excess, seed 3304 / 3301 | k-hat, seed 3304 / 3301 | certificate worst \|delta\|, margin |
|---|---|---|---|---|---|---|
| **primary** | 0.5 | 2 | 0.1712 (0.0014) | 0.0396 / 0.0424 | 0.415 / 0.471 | 0.0891, +0.0109 |
| **runner-up** | 0.5 | 4 | 0.1586 (0.0016) | 0.0439 / 0.0407 | 0.458 / 0.455 | 0.0858, +0.0142 |

- **The eligible set is unchanged: the same 20 settings, the same primary and the same runner-up as the first
  choice.** No setting became eligible and none dropped out. The sigma 0.6 settings, which the first rule excluded on
  the subset's 256-draw check, are excluded by the full covered-sky check at 4,096 draws at both seeds; every setting
  excluded by the certificate before is excluded by it again.
- No tie for the primary (the next eligible setting, sigma 0.45 with ell_grid 2, scores 0.1651, 4.2 fold sd below).
  The runner-up's candidates are the eligible settings with ell_grid 4, 6, 8 or 16, as before.
- **The first choice is kept unchanged as `q_scans/cv/choice_v1.json`** (the same bytes as the `choice.json` of the
  hyperparameter amendment, sha256 `a7a77fabed6908dc720c567168d0ccded347ac9fed4aa4c6f84a06a300fb4382`). `choice.json`
  no longer exists, so a stale consumer fails rather than reading it.

**The full table** (35 settings; `choice_v2.json` "table"; the subset's 256-draw check recorded, not used; FAIL
marks a failed 4,096-draw check):

| sigma, ell_grid | score (fold sd) | subset 256-draw check (recorded) | full sky, seed 3304: k-hat, max abs excess | full sky, seed 3301: k-hat, max abs excess | same table | certificate worst, margin | eligible first / amended |
|---|---|---|---|---|---|---|---|
| 0.3, 1 | 0.1132 (0.0007) | pass (0.0151) | 0.332, 0.0119 | 0.334, 0.0111 | yes | 0.1061, -0.0061 | no / no |
| 0.3, 2 | 0.1296 (0.0009) | pass (0.0195) | 0.443, 0.0145 | 0.329, 0.0146 | yes | 0.0938, +0.0062 | yes / **yes** |
| 0.3, 3 | 0.1324 (0.0010) | pass (0.0221) | 0.399, 0.0153 | 0.388, 0.0160 | yes | 0.0907, +0.0093 | yes / **yes** |
| 0.3, 4 | 0.1318 (0.0011) | pass (0.0238) | 0.400, 0.0170 | 0.388, 0.0166 | yes | 0.0902, +0.0098 | yes / **yes** |
| 0.3, 6 | 0.1282 (0.0012) | pass (0.0250) | 0.380, 0.0196 | 0.339, 0.0168 | yes | 0.0891, +0.0109 | yes / **yes** |
| 0.3, 8 | 0.1239 (0.0012) | pass (0.0249) | 0.419, 0.0212 | 0.382, 0.0165 | yes | 0.1063, -0.0063 | no / no |
| 0.3, 16 | 0.1088 (0.0014) | pass (0.0209) | 0.377, 0.0149 | 0.388, 0.0158 | yes | 0.1390, -0.0390 | no / no |
| 0.4, 1 | 0.1481 (0.0010) | pass (0.0288) | 0.316, 0.0233 | 0.356, 0.0233 | yes | 0.1045, -0.0045 | no / no |
| 0.4, 2 | 0.1567 (0.0012) | pass (0.0337) | 0.433, 0.0264 | 0.383, 0.0273 | yes | 0.0936, +0.0064 | yes / **yes** |
| 0.4, 3 | 0.1540 (0.0013) | pass (0.0353) | 0.429, 0.0257 | 0.385, 0.0278 | yes | 0.0894, +0.0106 | yes / **yes** |
| 0.4, 4 | 0.1498 (0.0013) | pass (0.0364) | 0.404, 0.0289 | 0.376, 0.0275 | yes | 0.0884, +0.0116 | yes / **yes** |
| 0.4, 6 | 0.1417 (0.0014) | pass (0.0363) | 0.423, 0.0313 | 0.444, 0.0271 | yes | 0.0978, +0.0022 | yes / **yes** |
| 0.4, 8 | 0.1350 (0.0014) | pass (0.0349) | 0.435, 0.0326 | 0.398, 0.0264 | yes | 0.1093, -0.0093 | no / no |
| 0.4, 16 | 0.1161 (0.0015) | pass (0.0270) | 0.410, 0.0257 | 0.410, 0.0255 | yes | 0.1081, -0.0081 | no / no |
| 0.45, 1 | 0.1602 (0.0012) | pass (0.0372) | 0.355, 0.0309 | 0.380, 0.0311 | yes | 0.1050, -0.0050 | no / no |
| 0.45, 2 | 0.1651 (0.0013) | pass (0.0414) | 0.429, 0.0329 | 0.408, 0.0347 | yes | 0.0916, +0.0084 | yes / **yes** |
| 0.45, 3 | 0.1604 (0.0014) | pass (0.0420) | 0.440, 0.0311 | 0.421, 0.0342 | yes | 0.0885, +0.0115 | yes / **yes** |
| 0.45, 4 | 0.1550 (0.0015) | pass (0.0426) | 0.454, 0.0360 | 0.444, 0.0337 | yes | 0.0872, +0.0128 | yes / **yes** |
| 0.45, 6 | 0.1456 (0.0015) | pass (0.0417) | 0.460, 0.0381 | 0.428, 0.0329 | yes | 0.0942, +0.0058 | yes / **yes** |
| 0.45, 8 | 0.1381 (0.0015) | pass (0.0395) | 0.491, 0.0391 | 0.432, 0.0315 | yes | 0.0889, +0.0111 | yes / **yes** |
| 0.45, 16 | 0.1182 (0.0015) | pass (0.0331) | 0.403, 0.0320 | 0.444, 0.0312 | yes | 0.0883, +0.0117 | yes / **yes** |
| 0.5, 1 | 0.1692 (0.0013) | pass (0.0462) | 0.398, 0.0391 | 0.393, 0.0399 | yes | 0.1047, -0.0047 | no / no |
| 0.5, 2 | 0.1712 (0.0014) | pass (0.0491) | 0.415, 0.0396 | 0.471, 0.0424 | yes | 0.0891, +0.0109 | yes / **yes** |
| 0.5, 3 | 0.1650 (0.0015) | pass (0.0484) | 0.431, 0.0380 | 0.454, 0.0414 | yes | 0.0874, +0.0126 | yes / **yes** |
| 0.5, 4 | 0.1586 (0.0016) | pass (0.0486) | 0.458, 0.0439 | 0.455, 0.0407 | yes | 0.0858, +0.0142 | yes / **yes** |
| 0.5, 6 | 0.1482 (0.0016) | pass (0.0468) | 0.468, 0.0455 | 0.434, 0.0384 | yes | 0.0827, +0.0173 | yes / **yes** |
| 0.5, 8 | 0.1403 (0.0015) | pass (0.0439) | 0.464, 0.0461 | 0.439, 0.0394 | yes | 0.0797, +0.0203 | yes / **yes** |
| 0.5, 16 | 0.1198 (0.0016) | pass (0.0405) | 0.430, 0.0389 | 0.462, 0.0381 | yes | 0.0696, +0.0304 | yes / **yes** |
| 0.6, 1 | 0.1803 (0.0016) | fail (0.0684) | 0.441, 0.0570 FAIL | 0.438, 0.0600 FAIL | yes | 0.1025, -0.0025 | no / no |
| 0.6, 2 | 0.1783 (0.0017) | fail (0.0641) | 0.471, 0.0567 FAIL | 0.510, 0.0600 FAIL | yes | 0.0874, +0.0126 | no / no |
| 0.6, 3 | 0.1702 (0.0017) | fail (0.0606) | 0.476, 0.0550 FAIL | 0.511, 0.0574 FAIL | yes | 0.0847, +0.0153 | no / no |
| 0.6, 4 | 0.1628 (0.0017) | fail (0.0595) | 0.466, 0.0621 FAIL | 0.492, 0.0544 FAIL | yes | 0.0823, +0.0177 | no / no |
| 0.6, 6 | 0.1513 (0.0017) | fail (0.0560) | 0.496, 0.0624 FAIL | 0.462, 0.0544 FAIL | yes | 0.0781, +0.0219 | no / no |
| 0.6, 8 | 0.1428 (0.0017) | fail (0.0519) | 0.494, 0.0617 FAIL | 0.481, 0.0540 FAIL | yes | 0.0741, +0.0259 | no / no |
| 0.6, 16 | 0.1219 (0.0016) | fail (0.0599) | 0.442, 0.0542 FAIL | 0.489, 0.0533 FAIL | yes | 0.0707, +0.0293 | no / no |

**Consumers of the choice** (consumer `ffccb39`): the T0 pre-check (`phase12aq_build.py precheck`, default
`$Q/cv/choice_v2.json`) and the recheck (`phase12aq_cv.py recheck`) refuse any other choice file; every table build
and the pre-check use the 4,096-draw check; the summary embeds `choice_v2.json` with `choice_v1.json` beside it;
`q_scans/RUNBOOK_T0.md` now passes `choice_v2.json` and stops if the run head lacks `ffccb39`. Tests: 19
cross-validation tests and 40 others pass on the frozen sources (2 slow tests skipped).

**No table has been used.** No Q table exists (the rehearsal's builds failed before writing one), and no GW
likelihood with any Q table has run. This amendment, the choice and its sha256 are committed before any table is
built.

**Still open:**
- The sealed rehearsal must be rerun with the amended code (consumer `ffccb39` or later, 4,096-draw check) before T0:
  its launcher `q_scans/scratch_launcher/rehearsal_tables.sh` is pinned to `0d45dcb`, which builds with the 256-draw
  check.
- These are pre-T0 numbers. The pre-check on the final lss head decides, with the replacement rule unchanged. With
  radial.py unchanged on the final head the pre-check should reproduce the seed-3304 values; a changed solver or
  stream could move the runner-up, whose worst row sits about one error from the tolerance.
- The mock's per-seed choice (`phase12aq_mock.py`, running) still applies the first eligibility (the subset's
  256-draw check and the certificate); the mock does not choose the real setting.
