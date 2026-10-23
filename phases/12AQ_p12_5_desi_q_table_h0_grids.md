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

**Amendment, the sealed rehearsal's tables (2026-10-23, about 00:10 UTC, before the rehearsal chain uses them):** the
rehearsal's table builds were rerun with the amended code (consumer `ffccb39`, the 4,096-draw check). All five jobs
completed: the primary's map table and its 4-member build pass the builder's Laplace check (largest relative excess
0.0396, k-hat 0.415, as the full-sky record of the choice) and the certificate; the unit, shuffled and member-0
tables are written; the table checks have no miss. The sha256s are under "Amendments".

**Amendment, the sealed rehearsal's results (2026-10-23, about 01:00 UTC, after T0 and before any table on the final
lss head is built; tiers and differences only):** the holder chain at the ten tie points on the pre-T0 sources
finished. Every same-process check is "equal" or passes except core's extension path for the primary table against
lss's target (check 11), which is in the "fallback" tier (worst 2.1e-3, in the selection log correction) and is
recorded only, as declared; with Q = 1 the two paths agree (ln L bit for bit). The wrapper ties to lss within
1.1e-13, so the wrapper tie is reached. The member-wiring check passes (worst 1.1e-13), so its tolerance stays at the
declared 1e-10. The replicate path is bit for bit. Details under "Amendments".

**Amendment, T0 (2026-10-23, about 01:10 UTC; location-free):** the final lss head is
`57afebe31191d565d30b0f068a7d5db3c3373abe` (pushed 2026-10-23T00:50:58Z). The pre-check on it passes the primary
(sigma 0.5, ell_grid 2) and the runner-up (sigma 0.5, ell_grid 4) with the same stamps as on the pre-T0 pin; no
fallback, no hold, no replacement; the recheck of the cross-validation reads the same score to the bit ("keep").
The env on the final head passes its gate on CPU and GPU. The table builds, the mock tie and the holder chain are
submitted. Details under "Amendments".

**Amendment 1, the tables on the final lss head (2026-10-23, about 01:35 UTC, before any GW likelihood with a Q
table on the final head; galaxy side only):** every table build and check completed (HENON 1392006-1392012). The
primary's map table, its builds at H0 60 and 80, the runner-up and the rougher-field table converge on all 119,457
fitted rows. The builder's Laplace check passes everywhere except the rougher-field table, which fails it as
declared; the primary reads 0.0396 (k-hat 0.415), as on the pre-T0 pin, and its log Q array equals the rehearsal's
bit for bit. Every certificate passes (margins +0.0052 to +0.0239). The constant-per-redshift table fails its
certificate, as expected, so the budget identity stands in for the gauge check. The table check has no miss: the
inputs are H0-free to 3.0e-15 (normwise), the H0 60 and 80 tables differ from the H0 70 table by at most 7.5e-11 in
log Q (bound 1e-8, no row above it), and the consumed budget closes to 4.9e-14 at the five a-priori points. The
sha256s are under "Amendments"; the member tables follow in amendment 2.

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

### Amendment: the sealed rehearsal's tables (2026-10-22 23:55 to 2026-10-23 00:02 UTC; location-free; before the rehearsal chain uses them)

**What ran.** The rehearsal's table chain of DESIGN 11.1 at the primary setting of `choice_v2.json` (sigma 0.5,
ell_grid 2), built at H0 70 with the member seed 3304, on the pre-T0 pin: the old env's python, the frozen core main
`10224291eac92b391dc2a06925dc08e49980f9e5` and the frozen lss integration head
`881fce6c875943013c0da48327d4aff5b49b27f7`, from the detached worktree `q_scans/wt/ffccb39` (consumer
`ffccb39cc54603a632d9dc1dc6e1cd7de81b3f19`, clean; every build runs the builder's Laplace check on 64 rows with
4,096 draws, as amended above). HENON, henon03, all five jobs COMPLETED:
- 1391982, the map table `q_main_map` (16 CPUs; 72 s; peak RSS 16.4 GB);
- 1391983, the 4-member build `q_main_m4` (16 CPUs; 179 s; peak RSS 25.0 GB);
- 1391984, the derived tables after the map: `unit`, `constant`, the stratified shuffle at seed 3305;
- 1391985, the table check (after the map build and the derived job, `afterany`);
- 1391986, member 0 of the 4-member build and the member check (after the member build, `afterok`, and the map
  build, `afterany`).

The launcher is outside the repo: `q_scans/scratch_launcher/rehearsal_tables_v2.sh` (sha256
`514d4ce168cf845ad251c9e51267be505d30839d2fbffcfdeffcec66f2ccb89b`), the chain of the first launcher pinned to
`ffccb39`; job ids in `q_scans/logs/rehearsal_table_jobs.txt`. The first attempt's failure records (consumer
`0d45dcb`, 256-draw check; the rehearsal amendment above) were moved, bytes unchanged, to
`q_scans/rehearsal/tables/attempt1_0d45dcb/`, and its table-check output to
`q_scans/rehearsal/gates/attempt1_0d45dcb/tables/`. The galaxy-count cache `grid_counts.npy` of the first attempt was
kept: its sha256 equals its metadata (`978d5f10c32caa3b116e8b59a921f36ca8e97ec89dd44b39c02d2970af6f7247`), and the builds
reuse it only when the catalog digest and the shape match.

**The rehearsal tables** (`q_scans/rehearsal/tables/`; each sha256 recomputed after the jobs and equal to the one
the writer stored beside the file):

| table | what it is | sha256 |
|---|---|---|
| `q_main_map.h5` | the primary's map table (no members) | `0a6d4ed702aeb8b068232a6cdd84bb696ecab4cc29c1cf06af894eeec338743d` |
| `unit.h5` | derived from the map table: log Q = 0 everywhere | `be9fa75fd75229906a51d430b2128706233056d2d006a92dce8f05a7d375c837` |
| `q_shuffled_s3305.h5` | derived: fitted rows permuted within 20 f_p quantile strata, seed 3305 | `73d73993aae85a3e05359e5efe7454ce4810fd3590534f61d7c578b347fd5b4e` |
| `q_main_m4.h5` | the primary with 4 members, seed 3304 (for the member-wiring rehearsal) | `e9cced86a67cd37f2f1fdcf36eadfb04af4a99f19d37f725ba0efbb5b977039d` |
| `q_member0_map.h5` | derived from the 4-member build: member 0 as the map, no members | `708205406f025cc67809c2947e2ec9f72808a528db2685654c84284fd9f90595` |

Records beside them: `q_main_map.json` (sha256 `c257c81af8162abba1bf40d9fd170424a10f7a3751b0fb685b0f42a3da85e413`),
`q_main_m4.json` (`50c3a8e1c31b3ea2069603d641a81c16eb6c37572f7903413705e5f167faab4c`), `shuffle_seeds.json`
(`cec3a1642b27d282537f3f9625e4004837c85160158e885df6d1e0449c39230e`; seed 3305 certified, no replacement drawn),
`FAILED_constant.json` (`bb8eae589be5395df96fbbfd6dc7173914cc9204bace434959e361f6bcb1f228`); the table checks
`q_scans/rehearsal/gates/tables/check.json` (`86f7abd47b716f5d7a43af5b93a83e1d4c437e86ecf80c57609794df1d16648e`) and
`q_scans/rehearsal/gates/tables_m4/check.json` (`0bbbb622b7e27c1021aa611151eb6978e8b269758e92d355701b78738726cf9c`).

**What the builds and checks say (galaxy side, H0-free):**
- **Both builds converged on all 119,457 fitted rows** (the expected count): Newton at most 7 iterations, missing-host
  budget at the clip 0.0076 before the gauge, no fitted cell at the clip after it, consumed gauge residual 3.6e-14.
- **Both pass the builder's Laplace check at 4,096 draws:** largest relative excess 0.0396, k-hat 0.415, the same
  values as the primary's full covered-sky record of the choice at seed 3304. The 4-member build's stamps equal the
  map build's.
- **Certificates** (lss's mask-free measurement, tolerance 0.10 on the worst |corr(Q, f_p) - corr(N/f_p, f_p)| over
  9 redshift slices; off the footprint log Q is exactly 0 in every table):

| table | worst \|delta\| | margin |
|---|---|---|
| map table | 0.0891 | +0.0109 (as in the choice) |
| 4-member stack (lss measures the member mean) | 0.0903 | +0.0097 |
| member 0 | 0.0957 | +0.0043 |
| stratified shuffle, seed 3305 | 0.0925 | +0.0075 |
| unit (no angular structure; passes on the off-footprint check) | — | pass |
| constant per redshift | 0.205 | fails (`FAILED_constant.json`), as section 5.2 expects: check 8 stands in for check 6 |

- **The table check (map, unit, shuffled): no miss.** The consumed per-redshift budget closes to 4.3e-14 at the five
  a-priori points (as stored, before the per-proposal gauge: 0.020 for the map table, 0.031 for the shuffle); the
  inputs at build H0 60 and 80 equal those at 70 to 3.0e-15 normwise (tolerance 1e-13); the footprint loader is bit
  equal to the surveys f_p; check 7(b) is not evaluated (the rehearsal builds no H0 60 or 80 table). Systematics of the
  map table: budget-weighted sd of log Q 0.33 / 0.44 / 0.48 at z 0.08 / 0.15 / 0.22; row-mean log Q below the depth
  correlates with f_p at -0.25 and with the imaging-depth maps at 0.03-0.05; the share of the redistribution between
  f_p strata is 0.035; budget ratio per f_p tercile 1.057 / 0.940 / 0.932. The shuffle keeps the f_p coupling (-0.20)
  and removes the imaging-depth correlations (-0.03 to 0.00).
- **The member check: no miss.** The 4-member build's map equals `q_main_map.h5` bit for bit.

**Next (no GW likelihood with any Q table has run yet):** the holder rehearsal chain (`phase12aq_miko_chain.sh
rehearsal`, from the same worktree and the frozen sources; differences only under `q_scans/rehearsal/`): the
same-process step at the ten tie points with every arm and the wrapper's ties, the shuffled table at the tie points,
the member-wiring check on the 4-member build (it sets the post-T0 member-wiring tolerance by the runbook's rule) and
the replicate identity check.

### Amendment: the sealed rehearsal's results (chain 2026-10-23 00:06 to 00:15 UTC; recorded about 01:00 UTC, after T0 and before any table on the final lss head is built; location-free: tiers and differences only)

**What ran.** The holder chain stage `rehearsal` (`slurm/phase12aq_miko_chain.sh rehearsal` through the committed
wrapper, one `srun --overlap` step at a time in the owner's miko job), from the detached worktree `q_scans/wt/ffccb39`
(consumer `ffccb39cc54603a632d9dc1dc6e1cd7de81b3f19`, clean), with the old env's python and the frozen core main
`10224291eac92b391dc2a06925dc08e49980f9e5` and lss integration head `881fce6c875943013c0da48327d4aff5b49b27f7` first
on the path, on the rehearsal tables of the amendment above, at the ten a-priori tie points. Four steps, all rc 0:
the same-process step (ten arms; 246 s; process peak RSS 16.1 GB), the shuffled table (seed 3305) at the tie points,
the member-wiring check on the 4-member build, and the replicate identity check (replicate b01). End mark
`q_scans/rehearsal/runs/CHAIN_DONE_rehearsal`; log `q_scans/logs/chain_rehearsal.log`. The watchdog's host RSS stayed
at or below 20 GB (limit 48 GB). Nobody read an absolute value: the numbers below come from the gate files only.

**The same-process step** (`q_scans/rehearsal/gates/same_process/tiers.json`, sha256
`53843d7280b8797513d3df629ec4b43e1fc2dfbf6c837f71cf55fee5f197edd7`; `same_process.json`, sha256
`f9b201ae1616e0ea3f6ab04b720ce99b7e9d1880567fb2dc27c73d87c641b8a1`). Worst absolute difference over ln L, ln mu, the
selection log correction, per-event ln Z and their MC variances at the ten points (N_eff as a relative difference);
flags and finite patterns equal in every comparison; forms asserted:

| check (in words) | compared | forms | worst | tier |
|---|---|---|---|---|
| 3, gathered equals grid | the stock target in the grid form against the gathered form | grid / gathered | 0 (bit for bit) | pass (1e-10) |
| 4, field analysis equals the stock target (gathered) | core's field analysis against the stock target | gathered / gathered | 9.1e-13 | equal |
| 4, the same in the grid form | | grid / grid | 9.1e-13 | equal |
| 4, decoded population, calibration, selection | | | all equal exactly | equal |
| 5, Q = 1 through lss equals core | lss's target with the unit table against core's field analysis (grid) | grid / grid | 1.8e-15 (per-event ln Z; ln L, ln mu, N_eff and the selection correction bit for bit); consumption `unit` | equal |
| 6, gauge at consumption | the constant-per-redshift table cannot be certified | | not run | check 8 stands in, as declared |
| 11, Q = 1 through core's extension path | lss's core-extension target with the unit table against lss's target with the unit table | grid / grid | 1.8e-15 (ln L, ln mu, N_eff and the selection correction bit for bit) | equal |
| **11, the primary table through core's extension path** | the extension target with `q_main_map.h5` against lss's target with it (consumption `proposal`) | grid / grid | **2.1e-3** in the selection log correction; ln L 8.1e-4, per-event ln Z 1.5e-4, ln mu 7.9e-6, per-event MC variance 1.7e-6, N_eff 1.1e-5 relative | **fallback** |
| the wrapper with the unit table | the scoped wrapper on the stock target against the stock target (grid) | grid / grid | 0 (bit for bit) | equal |
| the wrapper with the primary table | the scoped wrapper, the table gauged once, against lss's target | grid / grid | 1.1e-13 (ln mu, N_eff and the selection correction bit for bit) | equal |

- `stop_q_arms` false, no stop reason, no recorded failure; **the wrapper tie is reached** (`wrapper_tie_reached`
  true), so decision 19's fallback path stays available after T0.
- **Check 11 with the primary table is "fallback" and is recorded only, as declared:** lss's values stay primary and
  the difference goes to the lss line. With Q = 1 the two paths agree, so the difference is in how the extension
  path consumes a non-trivial table: on the pre-T0 lss pin the multi-catalog extension does not gauge the table at
  the proposal (its tracer metadata carries no gauge flag), while lss's target does. The final lss head's fix makes
  the multi-catalog path gauge at the proposal; check 11 re-checks it on the final head in the same-process step
  after amendment 1.

**The shuffled table at the tie points** (`q_shuffled_s3305.h5` through lss's target, map mode): ran to its end
mark. It has no check of its own in the rehearsal; it shows that a placement-control table loads and evaluates.

**The member-wiring check (check 9)** (`q_scans/rehearsal/gates/member_wiring/gate9.json`, sha256
`2522e47a7245cc48f84c0a6ea4bf71ce791fd54be258f452cdc3f80b0e2abcbf`): member 0 inside the 4-member marginalised
target against a single-table target of member 0 (`q_member0_map.h5`), both consumed `proposal`: **pass**, worst
absolute 1.1e-13 (ln L; per-event ln Z 3.6e-15, MC variance 2.7e-17, ln mu, N_eff and the selection correction bit
for bit), worst relative in ln L 1.7e-16; finite patterns equal, consumption equal. By the runbook's rule (worst at
most 1e-10, patterns and consumption equal) **the post-T0 member-wiring tolerance stays at the declared 1e-10**. It
is not revised after a post-T0 miss.

**The replicate path identity (check 12)** (`q_scans/rehearsal/gates/replicates/gate12.json`, sha256
`aa72611ecbd07a51d25857a679b65726ed048e36078daa04146f438e206b265c`): the identity replicate files through the
primary table, Q = 1 through lss and spectral, by operand swap: **pass, bit for bit** in all three arms.

**Next:** the T0 inputs (lss final head `57afebe31191d565d30b0f068a7d5db3c3373abe`, pushed 2026-10-23T00:50:58Z),
the run worktree, the pre-check on the final head, the env and the table builds, by `q_scans/RUNBOOK_T0.md`. No GW
likelihood with a Q table on the final lss head has run.

### Amendment: T0, the pre-check on the final lss head, the env and the submissions (2026-10-23 00:50 to 01:10 UTC; location-free)

**T0.** The final head of the lss fix PR (darksirens-lss branch `fix/review-2026-10-21`, PR #16, not merged) is
`57afebe31191d565d30b0f068a7d5db3c3373abe`, pushed to GitHub at **2026-10-23T00:50:58Z** (`q_scans/env/LSS_SHA_TARGET`,
`q_scans/env/T0_UTC`). The time box (T0 + 8 h) is 2026-10-23T08:50:58Z.
- Frozen archive of the final head: `q_scans/src/lss_final/` (`git archive` of that SHA from the local lss repo,
  taken 2026-10-23T00:54:43Z; `q_scans/src/ARCHIVES_FINAL.txt`; sha256 of the sorted per-file sha256 list
  `bad71aaa7e5e5c70c95845d02d34c0b40433925c324dde478b7b96fd17caf3a4`).
- Run worktree: `q_scans/wt/ffccb39`, consumer `ffccb39cc54603a632d9dc1dc6e1cd7de81b3f19` (the branch head at T0;
  it contains the amendment of the Laplace check), clean (`q_scans/env/RUN.txt`). Every post-T0 job runs from it.

**The pre-check on the final head** (HENON job 1392003, henon03, COMPLETED in 2.5 min; the old env's python with the
frozen core main and `lss_final` first on the path, `JAX_PLATFORMS=cpu`; `q_scans/gates/precheck/`: `precheck.json`
sha256 `b14d5c480bc987defe493a62784b8a2c9b522302b0e97101f90fa5f83c64d235`, `recheck.json`
`8cb8c013b9d3973b48b3642793864b4ac2406044f8b11e02db968c588c2cb930`, `settings.env`
`216c2b96dd6920d6f64e2ba10df7cad5d1e92ea2989eb966416ac21e9be454bd`):

| setting | converged rows | Laplace check (4,096 draws, 64 rows, seed 3304) | certificate worst \|delta\| | margin |
|---|---|---|---|---|
| primary, sigma 0.5, ell_grid 2 | 119,457 of 119,457 | largest relative excess 0.0396, k-hat 0.415: pass | 0.0891 | +0.0109 |
| runner-up, sigma 0.5, ell_grid 4 | 119,457 of 119,457 | 0.0439, k-hat 0.458: pass | 0.0858 | +0.0142 |

- `settings.env`: PRIMARY "--ell-grid 2 --sigma 0.5", RUNNER "--ell-grid 4 --sigma 0.5", FALLBACK 0, HOLD 0,
  REPLACED 0 ("the primary passes on the final head"). The values equal those of the pre-T0 pin and of the
  rehearsal's tables.
- The recheck of the cross-validation (the primary's spatial score on all 5 folds on the final head): the builder
  inputs (galaxy counts, completeness, expected counts, redshift grid) equal those of the pre-T0 pin exactly, and the
  score equals the pre-T0 score fold by fold (difference 0 against a fold sd of 0.0014 nat per held-out galaxy; the
  runner-up likewise). Decision **keep**: the cross-validation is not rerun.
- Bookkeeping note: `precheck.json`'s "archives" block repeats `ARCHIVES.txt` (the pre-T0 pin's archive list), while
  the lss it imported is `lss_final` (its module file, and `recheck.json` records the lss SHA as the final head).

**The env** `phase12t/envs/consumer_1022429_lss57afebe_cuda12` (built at nice 19 on the session host, 00:55 to
00:59 UTC, from GitHub; lss from GitHub at the final SHA): the freeze equals that of `consumer_e7c3007_cuda12`
except the core and lss lines (`FREEZE_SAME_EXCEPT_CORE_AND_LSS`, `BUILD_OK`; freeze sha256
`e9437a0611d883f0e2405481281bbb6fe35ae93033b121d5a4798dabcc7bcecd`), core `10224291eac92b391dc2a06925dc08e49980f9e5`,
lss `57afebe31191d565d30b0f068a7d5db3c3373abe`. **The env check (check 1) passes:** on CPU at nice 19 (pinned
commits, lss capabilities, the missing-density form, the footprint loader bit equal to the surveys f_p, a tiny
target on mock seed 1 with every keyword; peak RSS 3.5 GB; `q_scans/gates/env/env_cpu.json` sha256
`fc871f7f3790787f62a466d0ae2da022a51a621138eeaf6660be1b88d25662e0`) and on the holder GPU through the wrapper (GPU
backend in float64, the union catalog loaded with no warning; `env_gpu.json` sha256
`d1002279fe9df77b8218cae091b57f8590a734ca6626fb43de01576b393808b8`).

**Submitted (runbook sections 2 to 4 and 6), from the run worktree with the new env's python:**
- HENON table builds and checks, 2026-10-23T01:02:13Z (`q_scans/logs/table_jobs.txt`): the primary's map table
  1392006, the 16-member build 1392005 (henon03; submitted first so it takes the room there), the H0 60 and 80 builds
  1392007 and 1392008, the runner-up 1392009, the rougher-field table 1392010, the derived tables 1392011 (after the
  map build, `afterok`), the table check 1392012 (`afterany` on every build and the derived job; it excludes the member
  tables), the member check 1392013 (`afterok` on the member build and `afterany` on the map build). The nested
  submissions unset the holder session's Slurm variables.
- The mock tie in the final env: HENON array 1392014 (seeds 1-10).
- The holder chain stage "plumbing" (stock, spectral, core field, then the core-version tie), and a second chain
  "q" then "replicates" that waits for `q_scans/gates/AMENDMENT1_COMMITTED` before any step.
- The table builds were submitted a few minutes before this amendment (the runbook asks for it before them); they
  are galaxy-side only. **No GW likelihood with a Q table on the final lss head has run**, and none runs before
  amendment 1 (the table sha256s).

### Amendment 1: the tables on the final lss head (builds and checks 2026-10-23 01:02 to 01:20 UTC; recorded about 01:35 UTC; location-free; before any GW likelihood with a Q table on the final head)

**What ran.** Runbook section 2, from the run worktree `q_scans/wt/ffccb39` (consumer
`ffccb39cc54603a632d9dc1dc6e1cd7de81b3f19`, clean) with the final env's python
(`phase12t/envs/consumer_1022429_lss57afebe_cuda12`: core `10224291eac92b391dc2a06925dc08e49980f9e5`, lss
`57afebe31191d565d30b0f068a7d5db3c3373abe`), `JAX_PLATFORMS=cpu`, at the settings of
`q_scans/gates/precheck/settings.env` (primary "--ell-grid 2 --sigma 0.5", runner-up "--ell-grid 4 --sigma 0.5",
no fallback). HENON, henon01, every job COMPLETED with exit 0 (`q_scans/logs/table_jobs.txt`):
- 1392006, the primary's map table `q_main_map`, built at H0 70, seed 3304 (1 min 41 s; peak RSS 16.4 GB);
- 1392007 and 1392008, the same at build H0 60 and 80 (2 min 34 s and 1 min 31 s; 16.4 GB each);
- 1392009, the runner-up's map table `q_runnerup_map` (1 min 31 s; 16.4 GB);
- 1392010, the rougher-field table `q_rough_map`, ell_grid 2, sigma 1.0 (1 min 35 s; 16.4 GB);
- 1392011, the derived tables after the map build: `unit`, `constant`, the stratified shuffles at seeds 3305-3308
  (2 min 32 s; 10.8 GB);
- 1392012, the table check (`afterany` on every build and the derived job; the member tables excluded; 9 min 3 s;
  26.9 GB).

The 16-member build (1392005, henon03) and its member check (1392013) are in amendment 2. The galaxy-count cache
`grid_counts.npy` has sha256 `978d5f10c32caa3b116e8b59a921f36ca8e97ec89dd44b39c02d2970af6f7247`, the same as the
rehearsal's.

**The tables** (`q_scans/tables/`; each sha256 recomputed after the jobs, and equal to the one the writer stored
beside the file, to the build record's and to the table check's):

| table | what it is | sha256 |
|---|---|---|
| `q_main_map.h5` | the primary's map table, built at H0 70 (`q-map`) | `4ab478024d3b49be9f4b1058b7e76b41c21f5929f1316f93651dc8369f2a7fd9` |
| `q_main_map_h60.h5` | the same, gridded at H0 60 (gate 7) | `dc02f15950cf8715dab7974b4b17b47bd43ae43bf436e49cf74a7df192860fac` |
| `q_main_map_h80.h5` | the same, gridded at H0 80 (gate 7) | `4a0e88c394113d368ab4e68daa4967f13e329a1d00f3646287c45b8afa67cea3` |
| `q_runnerup_map.h5` | the runner-up, sigma 0.5, ell_grid 4 (`q-runnerup`) | `bd35cc7a85a3d6b84f0742e480ac6d15676b3c273b9e6f885b3f9e3eebf26e05` |
| `q_rough_map.h5` | the rougher field, ell_grid 2, sigma 1.0: a sensitivity with a known Laplace bias (`q-rough`) | `051f90fc1dfed358ead96acd1d3f05f594bf0f898893346f7c7a3e3111c04307` |
| `unit.h5` | derived from the map table: log Q = 0 everywhere (`unit-lss`, the Q = 1 reference) | `b67fdcb781833597f661233856e9d8f5948162ba3edafaa706c70189fe1e3c04` |
| `q_shuffled_s3305.h5` | derived: fitted rows permuted within 20 f_p quantile strata, seed 3305 | `d0afb7a2c5257ec5b11bf930cbdcceab8f2431e7ef18c752a033d20a3ee297e6` |
| `q_shuffled_s3306.h5` | the same, seed 3306 | `8a55bafca20c088925e217587fb02d1d2de003e33a9542ea3f18f8e4abb0240a` |
| `q_shuffled_s3307.h5` | the same, seed 3307 | `d48f648eb603cd701e85d89062dae6bd59e0f8835b312d72c070a9979a9b379e` |
| `q_shuffled_s3308.h5` | the same, seed 3308 | `86061d72f011979ca0c6b92037f78e3e216567fa175f57b315d47ee846823971` |

The primary's log Q array equals the rehearsal's map table bit for bit (`logq_map_sha256`
`e58351fa86c27c83f3e2fa19539c6f2fc5ba5378d1a65a124749187ed05425aa` in both); the file digests differ only through
the records the final lss writes beside the array.

Records beside them (sha256): `q_main_map.json` `9a0b6c9e838ec8eaf9d45756e5452eba3d0ea1f9a805ec7f51b0f58a159e55f7`,
`q_main_map_h60.json` `8e29f30e7d864cf10106115e412de87f724e15f27a08cac1e63fc6a75f8d83c4`, `q_main_map_h80.json`
`4f1b8cec81224a580d01ebfd28c1cd0d5e18c7b60585dbaf0c0976468ba77c6f`, `q_runnerup_map.json`
`fcb7d1c9b451d49f2a604bc603638ed9e10f4a1864853150ae134fb589ae849b`, `q_rough_map.json`
`31f7747ea9ac046374b49ef178e4d47df4f7609cb89c58b5af985d05ffad626c`, `unit.json`
`6751c444fbb0298d78c81e8536a700af1535604bc97c28cabcf7dc008ded7e67`, `q_shuffled_s3305.json` to `_s3308.json`
`0a1b1d96a54912832537e5f71880e761b827a8e9335bed003d30387305f0caa1`,
`a4d532d267fbe5fa9dafc6b53336a98844a066fbb78db176175d24ec8ae0579c`,
`5ad6d90e973219f8ae85c3d248c767d36f447d6a9313815f9f7daabbcb5e1234`,
`902738615fe7475199b12262e669f131c75b1ca988ecdfabb04a4644a2ab73f9`; `shuffle_seeds.json`
`1384efae1551eae6c292129643c6745f27de318c634fb29cab4306377b1811d0` (seeds 3305-3308 each certified at the first
draw, no replacement); `FAILED_constant.json` `7b2eea119ab61dc15950aa9e1183ccd0e2e42979be5b1ffaf6c6b4cbf09e09f9`
(the only failure record); the table check `q_scans/gates/tables/check.json`
`7120984688fb103ad38312c1378045ba5519bcd77023589b6f6c52a02f2c4fb1`.

**The stamps and the certificates** (build records; galaxy side, H0-free). Every build runs the builder's Laplace
check on 64 rows with 4,096 draws at seed 3304. The certificate is lss's mask-free measurement, tolerance 0.10 on the
worst |corr(Q, f_p) - corr(N/f_p, f_p)| over 9 redshift slices. In every table log Q is exactly 0 on the 69,870
rows off the footprint, and after the gauge no fitted cell sits at the clip.

| table | converged rows | Newton, most iterations | Laplace check: largest relative excess, k-hat | missing hosts at the clip before the gauge | consumed gauge residual | certificate worst \|delta\| | margin |
|---|---|---|---|---|---|---|---|
| primary map, H0 70 | 119,457 of 119,457 | 7 | 0.0396, 0.415: pass | 0.0076 | 3.6e-14 | 0.0891 | +0.0109 |
| primary map, H0 60 | 119,457 of 119,457 | 7 | 0.0396, 0.415: pass | 0.0076 | 3.6e-14 | 0.0891 | +0.0109 |
| primary map, H0 80 | 119,457 of 119,457 | 7 | 0.0396, 0.415: pass | 0.0076 | 3.6e-14 | 0.0891 | +0.0109 |
| runner-up | 119,457 of 119,457 | 7 | 0.0439, 0.458: pass | 0.0074 | 3.5e-14 | 0.0858 | +0.0142 |
| rougher field | 119,457 of 119,457 | 8 | 0.169, 0.703: **fails, as declared** (stamped `laplace_declared_fail`) | 0.050 | 3.2e-14 | 0.0761 | +0.0239 |
| shuffle, seed 3305 | the map table's rows | — | the map table's stamps | — | — | 0.0925 | +0.0075 |
| shuffle, seed 3306 | the map table's rows | — | the map table's stamps | — | — | 0.0948 | +0.0052 |
| shuffle, seed 3307 | the map table's rows | — | the map table's stamps | — | — | 0.0938 | +0.0062 |
| shuffle, seed 3308 | the map table's rows | — | the map table's stamps | — | — | 0.0925 | +0.0075 |
| unit | — | — | — | — | — | no angular structure; passes on the off-footprint check | pass |
| constant per redshift | — | — | — | — | — | 0.205 | **fails** (`FAILED_constant.json`), as expected |

- The primary's and the runner-up's stamps equal those of the T0 pre-check on the final head.
- **The expected failure.** The constant-per-redshift table is two-valued across the covered rows (the empty
  covered rows stay at Q = 1), and lss refuses to stamp it as footprint-aware (0.205 against 0.10). As declared
  (DESIGN 5.2 and 9.1), the derived job wrote `FAILED_constant.json` and went on with exit 0. `constant.h5` is not
  written, gate 6 is not run, and **gate 8 (the budget identity) stands in for gate 6.**

**The table check: no miss** (`q_scans/gates/tables/check.json`, 10 tables; the footprint loader bit equal to the
surveys f_p, sha256 `27174bdcbef3a36b21032d589fe969ac75758cb316313ca4c939308c4882d581`):
- **Gate 7(a), the inputs are H0-free.** `grid.C`, `grid.dN_exp` and the gauge weights (1 - C), gridded at H0 60
  and 80 against 70: worst normwise relative difference 3.0e-15 (tolerance 1e-13). The elementwise maximum, recorded
  beside, is 1.0e-11 in C, where C or 1 - C is tiny and the difference cancels. The galaxy counts are equal.
- **Gate 7(b), the tables are H0-free.** Against the H0 70 table, the largest absolute difference in log Q is
  7.5e-11 for the H0 60 table and 9.3e-15 for the H0 80 table. Every fitted row differs at rounding size, and no row
  is above the solver's bound of 1e-8. The Newton counts (most iterations 7, total 560,973) are the same in all
  three builds; the builds do not record per-row counts. These rounding-size differences are recorded and are not a
  stop. Gate 7(c), the GW ln L of the 60 and 80 tables, runs in the same-process step after this amendment.
- **Gate 8, the budget identity.** At the five a-priori points (20, 45, 67.74, 92.5, 140), on the 119,457 fitted
  rows and 123 nodes, the consumed tables (clipped, then re-gauged by lss's moments gauge) close to a worst relative
  residual of 3.8e-14 for the map table and 4.3e-14 to 4.9e-14 for the four shuffles (tolerance 1e-10). Before the
  per-proposal gauge, as stored, the residuals are 0.020 (map) and 0.030 to 0.033 (shuffles).
- **Gate 10, the certificates.** All 10 tables pass as stamped: converged; the Laplace check passes, or fails as
  declared for the rougher field; the certificate passes with the margins above.

**Systematics** (`check --systematics`, galaxy side):

| table | budget-weighted sd of log Q at z 0.08 / 0.15 / 0.22 | corr. of row-mean log Q below the depth with f_p | with median m5 / mth_eff / stratum map | share of the variance between f_p strata | budget ratio per f_p tercile |
|---|---|---|---|---|---|
| primary map | 0.33 / 0.44 / 0.48 | -0.25 | 0.055 / 0.032 / 0.038 | 0.035 | 1.057 / 0.940 / 0.932 |
| runner-up | 0.41 / 0.51 / 0.53 | -0.27 | 0.058 / 0.033 / 0.040 | 0.048 | 1.088 / 0.907 / 0.896 |
| rougher field | 0.64 / 0.70 / 0.68 | -0.30 | 0.085 / 0.033 / 0.040 | 0.039 | 1.137 / 0.853 / 0.840 |
| shuffles 3305-3308 | 0.330-0.331 / 0.437-0.438 / 0.468-0.469 | -0.19 to -0.20 | -0.035 to -0.026 / -0.003 to +0.003 / -0.003 to +0.001 | 0.022-0.023 | 1.022-1.025 / 0.939-0.940 / 0.932 |

- No fitted cell is at the clip in any table. The primary's numbers equal the rehearsal's. The shuffles keep most
  of the f_p coupling and remove the correlation with imaging depth, as designed.
- The full covered-sky Laplace evidence of the counts, relative to the primary: runner-up -0.0039 nat per galaxy,
  rougher field +0.0107 nat per galaxy. The rougher field's Laplace approximation is biased, as declared.

**Bookkeeping.** The check's and the builds' "archives" block repeats `q_scans/src/ARCHIVES.txt`, the pre-T0 pin's
archive list with lss `881fce6`. The lss they import is the env's, at `57afebe` (the "packages" block; no frozen
sources on the path). This is the same note as in the T0 amendment.

**Next.** After this commit, `q_scans/gates/AMENDMENT1_COMMITTED` is touched. That releases the holder chain "q",
which has waited since 01:03 UTC. It runs `unit-lss`; then the same-process step (gates 3 to 7(c) and 11), which
includes the first GW likelihoods with these tables; then the Q arms; then the chain "replicates". The member
tables and the rita member job are in amendment 2.
