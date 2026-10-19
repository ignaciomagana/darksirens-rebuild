# Phase 12AH — P12.5: why the DESI catalog shows no H0 information. Four diagnostics at the fixed calibration (declaration)

## Status

**DECLARED (owner approval, 2026-10-19 about 07:10 UTC), before anything
runs.** No likelihood has been evaluated for this record. This record fixes,
before any job: the settings, the cells and grids, the inputs (with sha256),
the metrics, the controls, the compute plan and the reading rules of four
diagnostics:

- **Part A, the per-event catalog share:** how much of each event's
  likelihood comes from catalog galaxies, and how much H0 structure the
  catalog adds per event.
- **Part B, the photometric redshift errors:** the 12AG grids with the
  photometric galaxies' redshift errors scaled down, and the spectroscopic-only
  catalog of record 12U.
- **Part C, the well-covered events:** the catalog and spectral-only grids on
  the events whose PE samples lie inside the footprint and below the catalog
  depth, and on the rest.
- **Part D, luminosity weighting:** whether the pinned core supports it
  consistently. **It does not** (evidence below). Part D is design only and
  stops here.

The only computation done for this declaration is a CPU count from the PE
samples and the footprint map alone (Part C's subset sizes). Its thresholds
were fixed before the count. No catalog or spectral likelihood entered it.

The code is not written yet. The consumer branch exists at its base commit
(below). The commit that runs, and its CPU tests, will be recorded here in an
amendment before any job is submitted.

**Status update (amendment R1, 2026-10-19 about 08:30 UTC, before any
production run).** No production grid of any part has run. A review of the
three build amendments found one blocking defect and seven smaller ones.
They are answered by amendments A2, C2, D1 and R1 below, all written before
any production job:

- **Part A and Part C are held.** Part A's consumer commits (f724d0f,
  440ef36) are still not on origin. The session's permission system refused
  the push a second time (about 08:30 UTC, "Out-of-Place Publication"), and
  it then refused every further shell command of that session, including
  read-only ones. Nothing was worked around. Part C reads only Part A's
  per-event grids, so it waits for Part A.
- **Part B is ready but was not submitted by that session.** Its controls
  passed at 416f5d7, which is on origin, and no defect blocks it. The
  submission (`slurm/phase12ah_b_submit_grids.sh 416f5d7`) needs a working
  shell.
- **The code for A2, C2 and the overall summary has not been committed,
  pushed or tested.** It is a working-tree change in `phase12_5/repo_12AH`.
  Its CPU tests must pass, and it must be committed and pushed, before any
  Part A or Part C job. The commit that runs is recorded here at that point.

**Blinding: location-free.** No H0 value is written here, in commit messages
or in PR text: no median, interval, MAP, absolute shift in km/s/Mpc, and no
per-event H0 location (no peak or slope position of any event's likelihood).
The H0 values in this record are fixed a priori and are not results: the grid
[20, 140], the reference values 50, 67.74 (core's fiducial `H0_FID`) and 90,
and the window [50, 90]. Results are given as:

- R = half-width68 / half-width68 of the spectral-only grid on the same
  events;
- the sd ratio, and Δ = (median − spectral median) / spectral sd;
- shares, counts, spreads and curvatures of per-event log-likelihood
  differences, ranks, Monte-Carlo variances.

Absolute values go only to `summary/summary_absolute.json`, which agents do
not read or quote. Grid rows (`scan.json`), per-event evidence files
(`events.npz`) and stage logs carry absolute log-likelihoods and are not for
agents to read or quote either; only the summary script reads them. Nothing
goes to the clean-room session or to the coordinator session.

**Amendment R1 (2026-10-19, before any production run): the complete list of
files that agents do not open, read or quote.** Paths are under
`phase12_5/no_info_diagnostics/`.

- **Grid rows and per-event evidence:** `runs/<cell>/scan.json`,
  `runs/<cell>/events.npz`, and the same files under every Part B cell
  directory and every control directory.
- **Branch evaluations:** `branches/<cell>/branches.npz`. Agents use only the
  Part A summary's account of the sibling `branches.json` (identities, memory,
  timings), not the file itself.
- **Spectral-only reruns:** `spectral_events/spectral_h0.json` and
  `spectral_events/events.npz`, and
  `controls/part_a/spectral_events/spectral_h0.json` and `events.npz`. The
  spectral stage writes its posterior into `spectral_h0.json`.
- **Absolute summaries:** `summary/part_a/summary_a_absolute.json`,
  `summary/part_b/summary_b_absolute.json`,
  `summary/part_c/part_c_absolute.json` and `summary/part_c/part_c_grids.npz`.
- **Logs:** every `stage.log`, including the 12U spectroscopic scan rerun's
  (it prints ln L), and the Slurm `logs/*.out` lines that print a likelihood
  or a posterior.

The location-free files are `summary/part_a/summary_a.json`,
`summary/part_b/summary_b.json`, `summary/part_c/part_c.json`,
`summary/summary.json`, the `controls/**` json written by the control
checkers (differences only), `coverage/` and every `STATUS*.json`. An agent
checks a running job only through device, dtype, memory, timing and
exit-code lines, never likelihood values.

## Why

Record 12AG (darksirens-rebuild PR #55, results commit e5384e0) ran the
smearing ladder: fixed-calibration H0 grids at nside {32, 64, 128, 256} ×
sigma_kde {1e-4, 3e-4, 1e-3, 3e-3, 1e-2}.

- **No cell narrows H0.** Only nside 256 at sigma_kde 1e-2 reads "a hint"
  (R 0.942). Less radial smearing and finer pixels **widen** H0 (R up to
  1.19), while the selection Monte-Carlo variance rises.
- **sigma_kde moves mostly the spectroscopic galaxies,** 27% of the catalog
  (ZERR about 2 to 3e-5). The 73% photometric galaxies keep their own width:
  ZERR median 0.032, 5% to 95% from 0.0086 to 0.074.
- With the population fixed, the DESI chain's sd is within about 1% of the
  spectral-only sd.

So the smearing scales tested do not explain the missing information. Four
questions remain, and the owner approved one diagnostic for each:

1. Does the catalog reach the events at all, and does it add H0 structure
   where it does (Part A)?
2. Do the photometric redshift errors wash it out (Part B)?
3. Is information present in the well-covered events but diluted by the rest
   (Part C)?
4. Would weighting hosts by luminosity, rather than uniformly, change the
   picture (Part D)?

## Common to every part

### The target and the fixed calibration (as 12AG)

Every catalog grid is the P12.4 DESI field target of 12AG ("Configuration of
every cell"), built by `phase12t_common.build_target` with
`config/desi.fixed_population.json` and 12AG's fixed settings:

- `catalog.calibration_prior=count_ridge_union_delta0`, `catalog.delta=0`,
  `catalog.z_depth=0.245`;
- the population fixed as the ladder cell: gamma 2.5439 not sampled,
  `population.fixed_values.mu_chi=0.04`, `population.fixed_values.sigma_chi=0.1`,
  the other 14 at their GWTC-5 values; Om0 0.3089, w0 −1, wa 0;
- `numerics.core_numerics=core_defaults`, `numerics.kernel_pin=off`,
  `numerics.max_likelihood_variance=20`,
  `numerics.selection_neff_soft_guard=true`;
- m_lim 21, the production k-correction (1.13465, −4.88963, 8.58828), the
  production footprint at the cell's nside (degraded from nside 128 at 64; the
  upgraded copy at 256, as 12AG);
- the fixed calibration theta = (H0, M0hat −20.4975, sigma_M 0.5592,
  log10n0_q), with log10n0_q the quantile of log10 n0 = −1.8216 (h-scaled);
  the driver checks the round trip to 1e-12;
- the GW inputs: the exact-prior PE file (259 events, 4096 samples each) and
  the O3/O4 injections;
- core e7c3007 defaults; float64 on one A100, XLA preallocation off;
- the H0 grid lo + 0.5 × arange(241) from 20, the spectral baseline's
  construction, so every grid has the same floats as the spectral-only grid.

Part B's spectroscopic-only cells change the catalog, its footprint and its
calibration, as declared under Part B. Nothing else changes anywhere.

**The spectral-only reference** is the 12AG reference
`phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json`. Parts A and C
also need each event's own spectral-only evidence on the same grid, which that
file does not hold. So the spectral-only grid is rerun once with the per-event
evidence recorded (HENON CPU, float64, as the reference was made). It must
equal the reference (controls below).

### Reading bands (12AG, amendment 2, unchanged)

Per grid:

- **"narrows":** R ≤ 0.90; **"a hint":** 0.90 < R ≤ 0.97; **"no narrowing":**
  R > 0.97.
- "narrows" and "a hint" also need the total Monte-Carlo variance (PE sum +
  selection, N²/N_eff) ≤ 2 at every grid point inside the grid's 90%
  interval.
- **"limited by the Monte-Carlo variance"** replaces any of the three when a
  penalised point lies inside the grid's 90% interval or inside the uncapped
  grid's 99% interval (ln L minus the soft-guard penalty).
- An incomplete grid, or one with a non-finite ln L, is reported as
  incomplete and not read.
- Shifts: robust |Δ| < 0.2, mild 0.2 to 0.5, material > 0.5. Shifts are
  reported, not read as findings.

### Inputs (sha256)

Paths are under `/hildafs/projects/phy230054p/magana/darksirens-core-data`
unless absolute.

| input | path | sha256 |
|---|---|---|
| native union table (22,787,835 rows) | `/hildafs/projects/phy230014p/magana/desi_darksirens_selection/final/experiments/experiment_loa_rebuild/inputs/rebuild_loa_faint_pixelate_input.h5` | `42e91b594572cfba716d0128ea3dcb24924a6c63e573078e7c4184fe24c0eaaa` |
| production catalog, nside 64 | `phase12u/inputs/catalogs/desi_union_nside64.h5` | `c2d1ff36567419e42386f07daf30bd0af2e2da714c16f066ecde4eb94d9084e2` |
| 12AG catalog, nside 256 | `phase12_5/smearing_ladder/catalogs/desi_union_nside256.h5` | `66c50dc4ac1ea3ffc593f8e19cc2baf3f0dd18c8a4953c77b10f262153a684d3` |
| footprint, native nside 128 | `phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| footprint, upgraded to nside 256 (12AG) | `phase12_5/smearing_ladder/catalogs/footprint/mth_map_nside256_from128.h5` | `c20e58e3b3570a5e131b3754002ea26024c43e647d3541ae9e1786fcdb181a67` |
| GW PE (259 events, 4096 samples) | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| injections (O3/O4) | `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| spectral-only grid (reference) | `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json` | `db9f7b80c4b799c18559c99040916a821ed99aa7feb06fcec1d6589a171a6f9f` |
| 12AG production cell grid (control) | `phase12_5/smearing_ladder/runs/ns64_sk3e-03/scan.json` | `ce3be7a92eecdb28e7e6067ed538fe435a04bd1c421bcea0a41c32547671a608` |
| 12AG hint cell grid (control) | `phase12_5/smearing_ladder/runs/ns256_sk1e-02/scan.json` | `0805087aa2e744bd333a4e1eebbae02d9da882603023e23f6c9e569181feb483` |
| 12AG summary (the unscaled R values of Part B) | `phase12_5/smearing_ladder/summary/summary.json` | `9269130e169bcaa64d5641e0b94b11f8d71d616b6d2f26e23b8345406fc5e002` |
| 12U spectroscopic native table (BGS Bright, M_APP ≤ 19.5; 4,909,210 rows) | `phase12u/inputs/native/spec.h5` | `d1b695fab5bd389b917fa3e8853b70ffb62ef79264148e062809ed592cf215c5` |
| 12U spectroscopic catalog, nside 64 | `phase12u/inputs/catalogs/desi_spec_nside64.h5` | `2879a5e299e8de7f58e10d8eb9e50fc662ab72d06fd1ca3faa2b80a3a9be797d` |
| 12U spectroscopic footprint (c_p f_p, native nside 128) | `phase12u/inputs/footprint_spec_nside128.h5` | `e96bcfd8e1890351c3aa578edfd7335dc4e371892f540c1e36d480880d66067a` |
| 12U spectroscopic calibration | `phase12u/inputs/calibration/spec.json` | `5f4a1619462ae78ccfef44ce4c33a73879ddf1293b6d0a964621a81110b11284` |
| 12U spectroscopic chain result (its M0hat and sigma_M medians) | `phase12u/runs/spec_only/result.json` | `2eb34e1b9e039aef4c93a7caf2e777146f3b1204f13d01f13a81c5c47087820c` |
| 12U spectroscopic chain configuration | `phase12u/runs/spec_only/config.resolved.json` | `073243beb79e2587e366cef7a8a6b1f4c337921cdca7b91135dac1e70034a80b` |
| 12U spectroscopic 12-point scan (control) | `phase12u/runs/scan_spec_only/scan.json` | `2abadd4b9176c9c74c89484010fb574c64f984329b8b75f9ac0ee30a96de0dfd` |

Files built here (the scaled and spectroscopic catalogs, the upgraded
spectroscopic footprint, Part C's subset lists) get their sha256 in their
build records, appended under Results before any grid is read.

### Code and environment

- **Consumer:** `ignaciomagana/desi_darksirens_selection`, new branch
  `phase12ah/no-info-diagnostics`, from `phase12ag/smearing-ladder` at
  **6337a56** (the 12AG ladder code), checked out at `phase12_5/repo_12AH`.
  The branch is created at 6337a56 with no new commit yet.
- **Declared additions** (none changes a 12AG number):
  - `scripts/phase12ah_scan.py`: the 12AG grid driver (`phase12ag_scan.py`,
    imported, not copied) with each event's log evidence added to every row
    (`event_log_evidence`, all 259), written to `events.npz` beside
    `scan.json`.
  - A **density branch** option on the DESI target's prepared field model
    (`phase12/desi_selection.py`), default `full`, which leaves the production
    program unchanged. The other values replace the host density on the PE
    side by one additive part of it (Part A). The grid reproduction control
    runs on the new commit.
  - `scripts/phase12ah_branches.py`: Part A's branch evaluations.
  - `scripts/phase12ah_spectral_events.py`: the spectral-only grid with the
    per-event evidence (the `phase12t_stage.py spectral` path, plus the
    per-event output).
  - `scripts/phase12ah_catalogs.py`: the scaled union catalogs and the
    spectroscopic catalogs, built with `phase12ag_catalogs.build` and two
    declared options (a dz scale for the photometric rows; a native table
    and footprint other than the union's), and their gates.
  - `scripts/phase12ah_coverage.py`: the PE and footprint shares and Part C's
    subset lists.
  - `scripts/phase12ah_summary.py`: the readings of Parts A, B and C.
  - `slurm/phase12ah_*`: the jobs; `config/desi.fixed_population.json` gains
    one preset, `count_ridge_spec_delta0` (Part B).
  - `tests/test_phase12ah_*.py`: CPU tests on tiny inputs (below).
- **Jobs run from a git worktree of the submitted commit,** under
  `phase12_5/no_info_diagnostics/worktrees/<sha>`, as in 12AG.
- **Environment:** `phase12t/envs/consumer_e7c3007_cuda12` (core e7c3007,
  darksirens-surveys 90f53a7, jax 0.4.34), read-only.
- **Outputs:** `phase12_5/no_info_diagnostics/`, with `catalogs/`,
  `coverage/`, `spectral_events/`, `runs/<cell>/`, `branches/<cell>/`,
  `controls/`, `summary/`, `plans/`, `lanes/`, `logs/`.

## Part A — the per-event catalog share

### What is computed

**Cells:** the production cell (nside 64, sigma_kde 3e-3) is the primary;
the 12AG hint cell (nside 256, sigma_kde 1e-2) is secondary. Both are rerun as
241-point grids with every event's log evidence recorded: ev_i(H0) for the
catalog target, and ev_i^spec(H0) from the spectral-only rerun.

**Branch evaluations** at the three reference values H_ref = 50, 67.74 and 90.
The host density at a PE sample is the field numerator

    n(z, p) = N_obs(p) p_cat(z | p) + dN_miss(z | p)

(catalog galaxies plus the smooth missing-host term; core
`catalog/models.py:207-236`, `catalog/field.py:300-314`). The same target is
evaluated with the PE-side density replaced by:

| branch | density |
|---|---|
| full | n(z, p) (the production density) |
| catalog | N_obs(p) p_cat(z \| p) only |
| completion | dN_miss(z \| p) only |
| below depth | n(z, p) × 1[z ≤ 0.245] |
| in footprint | n(z, p) × 1[f_p(p) > 0], with the cell's own f_p at its nside |

Each branch gives every event's log evidence ev_i,b (core's own PE reduction,
`log_evidence_and_mc_variance`). The evidence is a sum over PE samples, so the
branches add: the catalog and completion evidences sum to the full one.

### Per-event quantities

From the branches (likelihood-weighted: the PE samples weighted by the
population, the PE prior and the host density):

- **catalog share** c_i(H) = exp(ev_i,catalog − ev_i,full): the share of the
  event's likelihood that comes from catalog galaxies; 1 − c_i is the share
  of the smooth missing-host term;
- **depth share** d_i^w(H) = exp(ev_i,below − ev_i,full);
- **footprint share** p_i^w(H) = exp(ev_i,in − ev_i,full).

From the PE samples and the footprint alone (no likelihood):

- p_i: the share of the event's 4096 PE samples whose direction lies in a
  pixel with f_p > 0 of the native nside-128 footprint;
- d_i(H): the share with z(dL; H, Om0 0.3089, flat) ≤ 0.245;
- j_i(H): the share with both (Part C's statistic).

From the grids, the **per-event catalog-minus-spectral log-likelihood**:

    D_i(H0) = [ev_i(H0) − ln mu(H0)] − [ev_i^spec(H0) − ln mu^spec(H0)]

Each event's own likelihood is ev_i − ln mu; the field numerator's global
normalisation cancels in that difference, so D_i is normalisation-free. The
sum of the D_i is the total catalog-minus-spectral ln L up to the
Monte-Carlo correction terms. On the window W = [50, 90] (81 grid points,
fixed a priori), and also on the full grid:

- **spread** S_i: the range of D_i over W after removing its least-squares
  straight line (a tilt shifts an event's likelihood but cannot narrow it);
  the raw range is also reported;
- **curvature** q_i: twice the quadratic coefficient of the least-squares
  quadratic of D_i over W, in nats per (10 km/s/Mpc)². q_i < 0 means the
  catalog sharpens that event's likelihood;
- σ_i: the square root of the event's PE Monte-Carlo variance in the full
  branch at 67.74 (context for the size of S_i).

Aggregates, all location-free:

- the counts of **catalog-dominated** (c_i ≥ 0.5), **mixed** (0.1 ≤ c_i < 0.5)
  and **completion-dominated** (c_i < 0.1) events at each H_ref and at all
  three;
- the distribution of S_i and q_i in each class (median, 90th percentile);
- the Spearman rank correlations of S_i with c_i(67.74) and with j_i(67.74);
- **curvature budget:** Q = Σ_i q_i (the events), q_sel (the curvature over W
  of −259 [ln mu − ln mu^spec], the selection terms), q_tot = Q + q_sel, and
  q_spec (the curvature over W of the spectral-only ln L). F = q_tot / q_spec
  (F > 0 sharpens, F < 0 widens); R ≈ (1 + F)^(−1/2) is checked against
  12AG's R of the same cell;
- **cancellation** K = |Σ_i q_i| / Σ_i |q_i|;
- **concentration:** the share of Σ_i |q_i| carried by the 10 events with the
  largest |q_i|;
- a table of the 20 events with the largest S_i: event name, c_i at the three
  H_ref, p_i, d_i(67.74), j_i(67.74), S_i, the raw range, q_i, σ_i. It holds
  no H0 location.

### What "the catalog can carry information for an event" means

**An event can carry catalog information when its catalog share at the
fiducial reference is at least one half: c_i(67.74) ≥ 0.5.** Below that, the
smooth missing-host term, which carries no galaxy structure, dominates the
event's likelihood. The number of such events, N_carry, is reported with the
counts at 50 and 90 and at all three. All 259 events are evaluated.

### Reading rules (fixed now)

The readings are not exclusive; every one that holds is reported.

1. **Reach.** N_carry ≤ 26 (10% of the events) reads **"the catalog reaches
   few events"**; 27 to 77 reads "some"; 78 or more (30%) reads "many".
2. **"Where the catalog reaches, it adds little H0 structure"** if the median
   S_i over the catalog-dominated events (c_i(67.74) ≥ 0.5) is below
   **0.5 nat**. Scale: a total R of 0.90 needs F of about 0.23, the catalog
   adding about a quarter of the spectral-only curvature. The range over W of
   a quadratic with the spectral-only curvature is reported with the results
   (it carries no location), so S_i can be read against it.
3. **"The catalog adds per-event structure that cancels across events"** if
   at least 10 events have S_i ≥ 0.5 nat and K ≤ 0.2.
4. **"The selection term offsets the events' added curvature"** if
   Q / q_spec ≥ 0.10 (the events alone sharpen by at least 10% of the
   spectral curvature) while F < 0.05.
5. Per-event bands, for the tables: S_i < 0.5 nat negligible, 0.5 to 2
   modest, ≥ 2 strong.

The hint cell is reported the same way and read only as support of the
production cell.

### Amendment A1 (2026-10-19, before any Part A job): code, CPU tests, three clarifications, jobs

**Status.** The code is written and passes its CPU tests. **No Part A job has
been submitted and no Part A likelihood has been evaluated on the real data.**
Two steps were refused by the session's permission system, and neither was
worked around:

- the push of the two consumer commits below;
- the submission of the short GPU controls from the unpushed commit.

Both are left to the owner. The next step is to push the two commits, then run
`slurm/phase12ah_a_submit_controls.sh <commit>`.

**Code.** Consumer `ignaciomagana/desi_darksirens_selection`, branch
`phase12ah/no-info-diagnostics`, two local commits, **not yet on origin**:

- **f724d0f:** the code, tests and jobs;
- **440ef36:** a smaller HENON CPU request.

They sit on top of Part B's 416f5d7 and Part C's a90e7b9 and 38f104d. Several
parts work on the branch in parallel, so the files carry the part's prefix.
The declared names map as follows:

| declared | Part A file |
|---|---|
| `scripts/phase12ah_scan.py` | `scripts/phase12ah_a_scan.py` |
| `scripts/phase12ah_branches.py` | `scripts/phase12ah_a_branches.py`, with `scripts/phase12ah_a_common.py` |
| `scripts/phase12ah_spectral_events.py` | `scripts/phase12ah_a_spectral_events.py` |
| Part A of `scripts/phase12ah_summary.py` | `scripts/phase12ah_a_summary.py` (controls 1 to 4 on the outputs, then the readings) |
| plans, lanes, jobs | `scripts/phase12ah_a_plan.py`, `slurm/phase12ah_a_*` |
| tests | `tests/test_phase12ah_a_part_a.py` |

**Clarification 1: where the density branch lives.** The declaration put it as
an option of `phase12/desi_selection.py`. It is in Part A's own module instead:

- Core's `host_density_log_likelihood` is wrapped only while one branch
  target is built, and restored on exit. The builder imports it inside the
  function, so only that target's jit sees the wrapper.
- `phase12/desi_selection.py` is not changed, nor is any production program.
- The wrapper replaces the PE-side state and density only. The injections are
  evaluated by the production model, so ln mu and N_eff are the production
  ones in every branch.
- `full` is core's field evaluator itself. `catalog` and `completion` mirror
  core's `eval_incomplete_catalog_prior_state` term by term, with the same row
  normaliser and row host mass.

**Clarification 2: the curvature budget.** As declared, "Q = Σ_i q_i (the
events)" takes q_i from D_i. Each D_i already subtracts ln mu, so Q would
already hold the selection terms, and q_tot = Q + q_sel would count them
twice. Fixed now, before any number exists:

- q_i comes from D_i, as declared, and **q_tot = Σ_i q_i**;
- **Q_ev** is the curvature over W of Σ_i (ln Z_i − ln Z_i^spec), the events
  alone;
- q_sel is as declared, and Q_ev + q_sel = q_tot exactly, since the fits are
  linear;
- F = q_tot / q_spec, K and the concentration use the q_i, as declared;
- reading 4 reads Q_ev / q_spec ≥ 0.10 while F < 0.05.

This caveat is stated with the result. Core's field numerator leaves out a
survey-wide normalisation, which cancels between the event evidences and
−N ln mu. So Q_ev and q_sel each depend on that convention, while q_tot, F and
every D_i do not. Reading 4 is evaluated in core's convention and says so.

**Clarification 3: control 4 pass lines** for two checks the declaration did
not list:

- the full density through the wrapper (`full_wrapped`, control runs only)
  against the production target: within 1e-12 per event;
- ln mu and N_eff of every branch against the full branch: within 1e-12.

Bit-for-bit equality is recorded for both. The 1e-12 line allows a different
XLA fusion of a different program.

**Per-event evidence files** (Part C's input):

- `runs/<cell>/events.npz` and `spectral_events/events.npz`;
- keys: `H0` (241), `event_log_evidence` and `event_mc_variance`
  (241 × 259), `log_mu`, `n_eff`, `log_likelihood`, `selection_log_correction`
  (241), `event_names` (259);
- absolute values: not for agents to read.

**CPU tests.** `tests/test_phase12ah_a_part_a.py` has 11 tests on tiny
synthetic inputs. All pass at 440ef36, in about 60 s on CPU:

1. **Per PE sample, inside the target's own jit:** `full` and `full_wrapped`
   equal the production density bit for bit, and logaddexp(catalog,
   completion) equals it to within 1e-12. The below-depth and in-footprint
   branches are the production density, masked. On the selection state, the
   branch model gives the production density bit for bit.
2. **The patch is scoped:** a nested install is refused, and the original is
   restored afterwards. A fresh production build then equals the first, bit
   for bit. Per event, catalog plus completion equals full to within 1e-12,
   and ln mu and N_eff are bit for bit the same in every branch.
3. **The scan driver** equals the 12AG driver bit for bit (ln L, theta, PE
   variances) and records every event. Σ ln Z_i plus core's correction equals
   ln L to within 1e-9, and the check fails with a wrong N.
4. **The branch job end to end:** the identities pass, and the full branch
   equals the scan's per-event evidence at 50 and 90.
5. **The spectral-only grid** records the per-event evidence in grid order and
   prints no posterior.
6. **Metrics and readings:** spread and curvature on curves with known
   answers; shares, classes and bands; readings 1 to 4 on synthetic per-event
   data; no location key in the summary record (it refuses to write one).
7. **Plans:** memory routing (nside 256 is refused on a 40 GB lane) and each
   partition's maximum time.
8. **Coverage:** the PE-only fractions p_i, d_i and j_i on a case built by
   hand.

**Jobs (prepared, not submitted).** Every job uses its partition's maximum
time. The times below are estimates once a job runs, from 12AG's measured
build, compile and per-point times; queue wait is not included.

- **Short controls**, `slurm/phase12ah_a_submit_controls.sh <commit>`:
  - **nside-64 lane** (A100-40, twig): the production cell at H0 25, 50, 66,
    90 and 139, with the per-event evidence; then its branches at 50, 67.74
    and 90, `full_wrapped` included. About 12 min.
  - **nside-256 lane** (rita, A100-80): the hint cell at 50, 90 and 139; then
    its branches. About 16 min.
  - **HENON CPU** (8 CPUs, 64 GB): the spectral-only grid with the per-event
    evidence. About 7 min.
  - **HENON CPU, after the three:** controls 1 to 4, written to
    `controls/part_a/controls_a.json`. About 2 min.
- **Production**, `slurm/phase12ah_a_submit.sh <commit>`, which refuses to
  run unless the controls passed:
  - **nside-64 lane:** the 241-point grid plus the branches. About 13 min.
  - **nside-256 lane (rita):** the same for the hint cell. About 17 min, the
    longest.
  - **HENON CPU:** the spectral-only grid. About 7 min.
  - **HENON summary, after all three:** controls 1 to 4 on these outputs,
    then the readings, in `summary/part_a/summary_a.json` (location-free).
    About 3 min.
- **Time to completion:** about 1 hour from the push, if a rita card and a
  twig card are free (controls about 25 min, production about 25 min). HENON
  was nearly full at 08:00 UTC, which is why the CPU request is small.

**Controls and results.** None has run. Controls 1 to 4 must pass before any
Part A result is read.

### Amendment A2 (2026-10-19, before any Part A job): reading 4 withdrawn; status

**Status.** About 08:30 UTC, the push of f724d0f and 440ef36 was refused a
second time by the session's permission system. It was not worked around.
**Part A is held** until the owner (or the main session with the owner's
approval) pushes the branch. The push is a fast-forward from origin's
38f104d, and 440ef36 adds only `phase12ah_a_*` files, so Part B's controls at
416f5d7 stay valid. Until it is pushed, no part pushes from the shared clone.
Any push from it publishes these commits.

**Reading 4 is withdrawn as a reading.** As declared, "the selection term
offsets the events' added curvature" (Q_ev / q_spec ≥ 0.10 while F < 0.05) is
decided by core's normalisation of the field numerator, not by the data:

- core leaves a survey-wide, H0-dependent factor g(H0) out of the numerator;
- that factor cancels between the event evidences and −N ln mu, so q_tot, F
  and every D_i do not depend on it;
- but it adds 259 × curv(ln g) to Q_ev and removes the same amount from q_sel;
- a common factor h³, for example, changes Q_ev by about 16 nats per
  (10 km/s/Mpc)² at the window centre, several times the spectral-only
  curvature.

Two fixes were possible. Normalising each field numerator by its full-sky host
total would make the split convention-free. The simpler one is chosen
instead: Q_ev, q_sel, Q_ev / q_spec and the old test's outcome are
**reported as diagnostics only**, in `curvature_budget`, with the convention
note. No Part A statement and no overall reading uses them; the overall
reading's rule 6 is amended below. Readings 1, 2, 3 and 5 are unchanged.

**Code (working tree, not yet committed or tested):**

- `scripts/phase12ah_a_summary.py`: the boolean is now
  `curvature_budget.diagnostic_selection_offsets_events`, with
  `diagnostic_note`. `readings` no longer has `selection_offsets_events`; its
  `withdrawn` entry says why.
- `tests/test_phase12ah_a_part_a.py`: the reading test checks that the key
  is gone. The fourth-reading test becomes
  `test_the_selection_offset_is_a_diagnostic_not_a_reading`: the diagnostic
  is computed, and no statement uses it.

The lane code is unchanged (scan, branches and spectral driver). So the
short GPU controls test the same likelihood code as at 440ef36. The 11 CPU
tests must pass on the new commit before any Part A job.

## Part B — the photometric redshift errors

### The scaled union catalogs (a diagnostic, not a physical model)

**Scaling the photometric redshift errors is a diagnostic, not a model of
the data.** It makes 16.6 million photometric redshifts deliberately
overconfident: each kernel narrows around the same photometric redshift,
whose real error it then understates. A narrowing that appears only with
scaled-down errors says how much information the photometric errors remove,
under the assumption that the photometric redshifts are unbiased at the
narrower width. It is not an H0 measurement, and the fixed calibration
(n0, M0hat, sigma_M) is not re-derived for the scaled catalogs.

The catalogs:

- Built from the native union table exactly as 12AG builds its nside 64 and
  256 files (`phase12ag_catalogs.build`), with **one change: rows with
  SURVEY_CODE 1 (Legacy Survey photometric redshift) get dz = s × ZERR.**
  Spectroscopic rows (codes 0 and 2) keep their ZERR.
- s ∈ {0.5, 0.25}: powers of two, so the scaled dz are exact in binary
  floating point.
- nside 64 and 256, with 12AG's footprints. Four files.
- The photometric median kernel width at sigma_kde 3e-3 then moves from 0.032
  to about 0.016 (s = 0.5) and 0.009 (s = 0.25).

Gates (the build exits non-zero on a failure, and no grid of that catalog
starts):

- the 12AG row counts: 22,785,279 galaxies; 16,628,106 scaled
  (code 1) and 6,157,173 unscaled (codes 0 and 2);
- against the 12AG file of the same nside: `zgals`, `wgals`, `gal_app_mag` and
  `ngals` equal exactly, slot by slot (z is unchanged, so the slot order is
  too); in `dzgals`, exactly 16,628,106 real slots differ from 12AG's value,
  each by the factor s exactly, and every other slot (padding included)
  equals 12AG's value;
- the multiset of (z, dz, weight, apparent magnitude) equals the native rows
  after the cuts with the scaled dz;
- the core load check and the coverage check (no occupied pixel with
  f_p = 0).

### The spectroscopic-only catalog (record 12U)

- **Sample:** 12U's BGS Bright rows with M_APP ≤ 19.5 (native table above,
  4,909,210 rows). The 12AG builder with the native table and the footprint
  replaced: the quality cut M_APP ≤ 21 removes none; the 12I mask, judged at
  nside 128 on the spectroscopic footprint, removes 33; 4,909,177 galaxies.
- **Footprint:** 12U's c_p f_p,LS map (c_p, the per-pixel spectroscopic
  fraction, is measured at nside 64; f_p-weighted area 7,872 deg² against
  the union's about 23,000 deg²). nside 64 is degraded from it as in 12U. **nside
  256 can be rebuilt the 12AG way:** the map is upgraded from 128 to 256 by
  inheritance (every child keeps its parent's masked_frac and counts), and
  the native table is re-pixelised. c_p keeps its nside-64 resolution at every
  nside; that is stated with the results.
- **Gates:** the rebuilt nside 64 equals 12U's file (sha256 `2879a5e2…`); both
  nsides hold the same 4,909,177 galaxies (exact multiset); nesting from 64 to
  256; the upgraded map gives every child its parent's f_p and degrades back
  to the native f_p to 1e-15; coverage check.
- **Its own calibration, fixed, with delta 0 on its count ridge:**
  - log10 n0 = **−1.724559** (h-scaled): 12U's spectroscopic count ridge
    a + b × delta at delta 0 (a −1.724559, b −0.07603, sd 0.030334);
  - M0hat **−20.1870** and sigma_M **0.8160**: the 12U spectroscopic chain's
    posterior medians, rounded at 4 decimals as 12AG rounded the union's
    (12U's luminosity prior means are −20.1869 and 0.8158; prior sd 0.010 and
    0.006);
  - m_lim 19.5, and 12U's luminosity priors in the configuration (they do
    not enter a fixed-calibration likelihood);
  - a new calibration preset `count_ridge_spec_delta0` (12U's spectroscopic
    ridge with delta fixed at 0), the analogue of 12AG's
    `count_ridge_union_delta0`.
  Everything else is 12AG's: the ladder population, the GW inputs, core,
  numerics, the H0 grid and the spectral-only reference.

### The cells (241-point grids, per-event evidence recorded)

| | nside 64 | nside 256 |
|---|---|---|
| union, photometric dz × 0.5 | sigma_kde 3e-3, 1e-3 | sigma_kde 3e-3, 1e-3 |
| union, photometric dz × 0.25 | sigma_kde 3e-3, 1e-3 | sigma_kde 3e-3, 1e-3 |
| spectroscopic only | sigma_kde 3e-3, 1e-3 | sigma_kde 3e-3, 1e-3 |

Twelve grids: eight scaled union grids and four spectroscopic-only grids
(sigma_kde 3e-3 is 12U's; 1e-3 is the second ladder value).

**The unscaled union (s = 1) is 12AG's, reused and not rerun:** R 1.048 at
(64, 3e-3), 1.024 at (64, 1e-3), 1.030 at (256, 3e-3) and 1.021 at
(256, 1e-3), all "no narrowing". (The production cell is rerun in Part A and
must reproduce 12AG's grid.)

Reported per grid, as 12AG: R, the 90% half-width ratio, the sd ratio, Δ, the
PE, selection and total Monte-Carlo variances (nearest the median, largest
inside the 90% interval, largest over the grid), penalised and rejected
points, the uncapped grid's R, memory and timings, and the compact view's
rows and galaxies.

### Reading rules (fixed now)

Per grid: the bands above.

**The scaled union, along the scale axis** (at fixed nside and sigma_kde,
the path s = 0.25 → 0.5 → 1):

- **"The photometric errors wash out the information"** when a scaled grid
  reads "narrows" and its path to s = 1 at the same nside and sigma_kde
  qualifies: R does not fall by more than 0.02 at any step, and the s = 1 grid
  reads "no narrowing" or has R at least 0.10 above the narrowing grid's.
- **"Undetermined"** when a scaled grid narrows but no path qualifies.
- **"The photometric errors may contribute (a hint)"** when no scaled grid
  narrows and at least one reads "a hint" while its s = 1 grid reads "no
  narrowing".
- **"The photometric errors alone do not explain it"** when no scaled grid
  narrows or hints and every scaled grid was read. When some are limited by
  the Monte-Carlo variance or incomplete: **"… where the Monte-Carlo resolves
  it"**, with the list.

**The spectroscopic-only grids:**

- **"Exact redshifts alone carry information"** if a spectroscopic grid reads
  "narrows"; "a hint" likewise.
- **"The spectroscopic galaxies alone carry none"** if all four read "no
  narrowing". This catalog is shallower (m_lim 19.5) and covers a smaller
  effective area, so this null does not show that photometric errors are
  harmless; it is read together with the scaled grids.

### Amendment B1 (2026-10-19, before any Part B grid): code, catalogs, controls, prepared jobs

**Status.** The code is written and pushed, and its CPU tests pass. The
catalogs are built and gated, and the short GPU controls ran and passed.
**No Part B production grid has been submitted.** The twelve declared grids
are prepared (below). The controls compare likelihoods only as differences, so
nothing below carries an H0 value. The only H0 values named are the a priori
grid and the probe points (20, 50, 80, 110 and 140, 12AG's probe points).

**Code.** Consumer `ignaciomagana/desi_darksirens_selection`, branch
`phase12ah/no-info-diagnostics`, commit **416f5d7** (pushed), directly on
6337a56. Parts work on the branch in parallel, so the files carry the part's
prefix:

| declared | Part B file |
|---|---|
| `scripts/phase12ah_catalogs.py` (the scaled and spectroscopic catalogs, gates) | `scripts/phase12ah_b_catalogs.py` |
| `scripts/phase12ah_scan.py` (grid driver with per-event evidence) | `scripts/phase12ah_b_scan.py`: `phase12ag_scan.py` imported unchanged, plus `events.npz` and the per-event sum check (control 2) at every point of every Part B grid |
| plans, lanes, control checks | `scripts/phase12ah_b_plan.py` |
| Part B of `scripts/phase12ah_summary.py` | `scripts/phase12ah_b_summary.py` (12AG's per-cell summary and bands, imported; the scale-axis and spectroscopic readings above) |
| `slurm/phase12ah_*` | `slurm/phase12ah_b_*` |
| `tests/test_phase12ah_*.py` | `tests/test_phase12ah_b.py`: 12 CPU tests pass (the dz-scaling gates on a synthetic table, the spectroscopic build against 12U's builder byte for byte, the driver against `phase12ag_scan.py` bit for bit with the per-event sum, resume, the spectroscopic preset, the plans and the readings) |

**Two clarifications (no number changes):**

1. The preset `count_ridge_spec_delta0` is passed as a `--set` override
   (`phase12ah_b_plan.SPEC_SET`). It is not written into the shared
   `config/desi.fixed_population.json`, so that file stays untouched while the
   parts work in parallel. The resolved configuration is the same either way,
   and control 6 checks it.
2. The scaled catalogs come from the 12AG builder run on a small HDF5 table.
   Its columns are external links to the native table (sha256 checked),
   except ZERR, which holds the scaled values. This avoids copying the
   1.4 GB table. The same path at s = 1 is a control: it must write 12AG's
   files byte for byte.

**Catalogs** (HENON CPU, jobs 1390239 to 1390242, about 7 minutes each, peak
16 GB). Paths are under `phase12_5/no_info_diagnostics/catalogs/`.

| family | nside 64 sha256 | nside 256 sha256 | gates |
|---|---|---|---|
| s = 1 (control) | `c2d1ff36567419e42386f07daf30bd0af2e2da714c16f066ecde4eb94d9084e2`, the production and 12AG file | `66c50dc4ac1ea3ffc593f8e19cc2baf3f0dd18c8a4953c77b10f262153a684d3`, the 12AG file | pass; byte for byte |
| s = 0.5 | `b921dc354986ed3b2e42f09919c7db840ad922acb77cb16f178d1b58ed86eccd` | `a9046679ef5bdb290e509ad5e1daabcd4796be0a42dae38949a78945eacac344` | pass |
| s = 0.25 | `35fae5542d00ee281e61e8134fe52c7ad86edebceb30b6513be9cc0ac531b83b` | `f54b430180c59be385408940af9a33c069c30a1da1f2432a338a55902244241e` | pass |
| spectroscopic | `2879a5e299e8de7f58e10d8eb9e50fc662ab72d06fd1ca3faa2b80a3a9be797d`, 12U's file | `729ce2c28f829173ddfd5987c901c9cf139163569857a3d9c2f580f419fb10f2` | pass |

- **Scaled tables:** s = 0.5 `a24572878fcb2921cd431752d48c9e5cfb27352844045b90c960097db4a73cb8`;
  s = 0.25 `fbfeba921ddd143ae5b487567d70d77ff4e68fe3006d9f547f02d148632afec0`;
  s = 1 `66354de1d6ab5c3b0a45cc9e6c016148d0ab0412eebc746dee720922c2f70c4f`.
- **Scaled gates, at both nsides:**
  - 22,785,279 galaxies after the cuts: 16,628,106 photometric (code 1, none
    with dz = 0) and 6,157,173 spectroscopic (codes 0 and 2);
  - `ngals`, `zgals`, `wgals` and `gal_app_mag` equal 12AG's slot by slot,
    padding included;
  - in `dzgals`, exactly 16,628,106 real slots differ, each by the factor s
    exactly, and no padding slot differs;
  - the multiset of (z, dz, weight, apparent magnitude) equals the native rows
    after the cuts with the scaled dz;
  - at s = 1, no dz slot differs and both files are 12AG's byte for byte.
- **Spectroscopic gates:**
  - 4,909,210 rows; the M_APP ≤ 21 cut removes none and the 12I mask removes
    33, leaving 4,909,177 galaxies, one multiset at both nsides;
  - nesting from 64 to 256 passes, and the nside-64 file is 12U's byte for
    byte;
  - the upgraded footprint
    (`spec_only/footprint/mth_map_nside256_from128.h5`, sha256
    `ddc87f4a96fe28428b046b68ba7a7928fd07654c858bb1c9aff1a86a04c74683`) gives
    every child its parent's f_p exactly and degrades back to the native f_p
    with difference 0;
  - no occupied pixel has f_p = 0;
  - the f_p-weighted area is 7,872 deg² at both nsides; galaxies per occupied
    pixel, median 289 at nside 64 and 18 at nside 256.

**Controls: all pass** (`controls/part_b/controls.json`, location-free).

- **The unscaled catalog through the Part B path** (s = 1, the production
  cell, 241 points; twig, job 1390243) equals 12AG's production-cell grid
  (`ce3be7a9…`) at every point:
  - max |Δ ln L| = 0, bit for bit (tolerance 1e-10);
  - theta, the selection variance and the PE variance are equal;
  - per-event sum (control 2): 259 events at all 241 points, max |residual|
    4.5e-13.
- **Control 6, 12U's spectroscopic scan:** rerun from 416f5d7 with its
  recorded arguments (twig, job 1390244). Against 12U's scan (`2abadd4b…`)
  at all 12 points, max |Δ ln L| = 0 (tolerance 1e-6), and theta is
  identical.
- **Control 6, configuration:** the spectroscopic cells' resolved
  configuration differs from 12U's chain configuration (`073243be…`) only in
  the declared keys:
  - the calibration preset, plus 12AG's union preset, which is present in the
    shared configuration and unused here;
  - delta, log10 n0, sigma_kde (in the 1e-3 cells) and the population's spin
    pair.

  The selection block (m_lim 19.5 and 12U's luminosity priors), numerics and
  sampler block are identical. The M0hat and sigma_M medians of 12U's chain
  (`2eb34e1b…`) round at 4 decimals to the declared −20.1870 and 0.8160.
- **Control 5:** every catalog gate above passes.
- **Control 2** also passes on the three probes (max |residual| ≤ 2.3e-13).

**Probes** (5 H0 points each, for memory and time):

| probe | card | jax peak (GiB) | nvidia-smi (MiB) | s per point | first point (s) | route |
|---|---|---|---|---|---|---|
| s = 0.25, nside 64, sigma_kde 1e-3 | twig A100-40 | 13.4 | 21,290 | 0.28 | 87 | any A100 |
| s = 0.25, nside 256, sigma_kde 1e-3 | rita A100-80 | 33.8 | 49,921 | 0.36 | 69 | rita (80 GB) |
| spectroscopic, nside 64, sigma_kde 1e-3 | twig A100-40 | 2.1 | 4,756 | 0.07 | 84 | any A100 |

- Memory and time equal 12AG's at the same nside. The compact view and the
  kernel window (1,719 slots at nside 64, 569 at 256) are set by the pixel
  slots, not by dz.
- The narrowest scaled kernel at nside 256 reaches a total Monte-Carlo
  variance of 7.2 at one of its five probe points. Under the reading rules
  this matters only inside a grid's 90% interval, and the summary checks it
  there.

**Prepared, not submitted:** `slurm/phase12ah_b_submit_grids.sh 416f5d7`. It
refuses to run unless `controls/part_b/controls.json` passes. It writes
`plans/part_b_grids.json`, then submits these lanes, each at its partition's
maximum time:

- **rita0** (A100-80): s = 0.5 and 0.25 at nside 256 and sigma_kde 3e-3, then
  the spectroscopic grid at nside 256 and 3e-3. About 15 minutes.
- **rita1** (A100-80): the same three at sigma_kde 1e-3. About 15 minutes.
- **twig0 to twig3 and henon-gpu** (A100-40): the six nside-64 grids, about
  4 minutes each. henon-gpu holds two, about 8 minutes.
- **HENON CPU summary**, `--dependency=afterany` on every lane: writes
  `summary/part_b/summary_b.json` (location-free), `summary_b_absolute.json`
  (not for agents) and always `STATUS_B.json`.

The spectroscopic grids at nside 256 stay on rita as declared, although their
memory is likely far under 40 GB. Part A also has a rita lane (the hint cell).
If both are submitted together, the rita lanes run one after the other.

**Estimated time to completion of Part B:** about 20 minutes from submission
with both rita cards free (rita lanes about 15 minutes, summary about 2). It is
about 35 to 40 minutes if Part A's rita lane runs first, and hours if another
user holds rita.

## Part C — the well-covered events

### The subset rule (fixed before the count, from PE and footprint only)

For each event, j_i is the share of its 4096 PE samples that both:

- lie in a pixel with **f_p > 0** of the native nside-128 production
  footprint (`mth_map_nside128.h5`), and
- have **z(dL; 67.74, Om0 0.3089, flat) ≤ 0.245**, the catalog depth, with
  H0 at core's fiducial 67.74 fixed a priori.

- **Subset S (primary): j_i ≥ 0.5.**
- **Subset S′ (secondary): j_i ≥ 0.25.**
- **Complement:** the events with j_i < 0.5.

**The count** (computed for this declaration after the thresholds were
fixed; PE samples and footprint only, no likelihood; all samples are in
support):

| j_i ≥ | 0.1 | 0.25 | 0.5 | 0.75 |
|---|---|---|---|---|
| events at the reference 67.74 | 93 | **69** | **45** | 27 |
| for context: at 50 | 123 | 86 | 67 | 43 |
| for context: at 90 | 69 | 40 | 25 | 13 |

So **S holds 45 events, S′ 69, and the complement 214.** Context: 165 events
have at least half their samples in the footprint (p_i ≥ 0.5; 64% of the sky
has f_p > 0), and 72 have at least half below the depth at 67.74. The subset
lists (event names) are written by `phase12ah_coverage.py` from the same rule,
and their sha256 is recorded before any subset grid is read.

### Grids: reconstructed from the per-event evidence, with core's own correction

No new GPU grid is needed. The subset log-likelihood is assembled from the
full grids (Part A's catalog grids and the spectral-only rerun) exactly as
core assembles a run on those events alone:

    ln L_S(H0) = Σ_{i∈S} ev_i(H0)
                 + selection_log_correction(ln mu, N_eff, N_S, soft guard, 20,
                                            Σ_{i∈S} var_i)

`selection_log_correction` is core's function
(`selection/gw.py:270-408` at e7c3007); ln mu and N_eff do not depend on the
number of events. Same injections, N = subset size, the same guard. The
uncapped grid and the penalised points use 12AG's guard terms at N = N_S.
Controls: with S = all 259 events this reproduces every recorded ln L; a CPU
test on tiny inputs checks it against a direct core evaluation on a store
holding only the subset's events.

Cells: the production cell and the 12AG hint cell (nside 256, sigma_kde
1e-2), for S, S′ and the complement, against the spectral-only grid on the
same events.

Reported per subset and cell: R, the sd ratio, Δ, the Monte-Carlo variance
(Σ_S var_i + N_S²/N_eff) inside the subset's 90% interval, the penalised
points, the uncapped R.

**Random-subset control:** 1000 random subsets of N_S = 45 events (and 1000
of 69), drawn without replacement with numpy `default_rng(20261019)`. R for
each, at each cell. The percentile of R_S among them is reported.

**Edge flag:** if a subset's catalog or spectral posterior has its 99%
interval within one grid step of 20 or 140, its R is reported as
"edge-limited" and not read.

### Reading rules (fixed now)

At the production cell:

- **"The catalog informs the well-covered events"** if R_S ≤ 0.90 (with the
  Monte-Carlo condition) and R_S is below the 5th percentile of the random
  subsets. If the complement also reads "no narrowing": **"… and the other
  events dilute it."**
- **"A hint in the well-covered events"** if 0.90 < R_S ≤ 0.97 (Monte-Carlo
  condition) and below the 5th percentile of the random subsets.
- **"Coverage and depth do not explain it"** if R_S > 0.97, or R_S lies inside
  the random subsets' 5% to 95% range.
- S′ and the hint cell are read the same way, as support only.

**Stated plainly:** the subsets are chosen from the events' own PE samples
(their sky positions and distances), and the injections are not cut the same
way. Neither subset posterior is a valid H0 inference. Only the catalog
against spectral-only comparison on the same events is read; Δ is reported
and not read as a bias.

### Part C amendment: code, subset lists and controls (2026-10-19, before any subset grid)

No Part C subset grid exists yet, and none has been read. This amendment
records Part C's code, the subset lists with their sha256, the details fixed
before any grid, and the controls.

**Code.** Consumer branch `phase12ah/no-info-diagnostics`, commits **a90e7b9**
(the code) and **38f104d** (a CPU-lane option in the submit script). Part C's
files use the prefix `phase12ah_c_`:

- `scripts/phase12ah_c_coverage.py` builds p_i, d_i(H), j_i(H) and the subset
  lists. This is the declared `phase12ah_coverage.py`, under Part C's prefix.
  Each PE sample is pixelised with core's `ang2pix_ring` at nside 128, as the
  target pixelises it. dL is inverted with core's own distance table
  (`dL_of_z`, `z_of_dL_precomputed`), as the likelihood inverts it. The
  script exits non-zero if any count differs from this record's table.
  `coverage_events.csv` holds every event's p_i, d_i and j_i at 50, 67.74 and
  90, for Part A's tables.
- `scripts/phase12ah_c_subsets.py` builds the subset grids, runs the
  random-subset control and applies the readings. It reads Part A's per-event
  grids: `runs/ns64_sk3e-03/`, `runs/ns256_sk1e-02/` and `spectral_events/`,
  each an `events.npz` beside its `scan.json` or `spectral_h0.json`. Each
  subset grid is read with 12AG's own machinery
  (`phase12ag_summary.cell_summary`), against the spectral-only grid on the
  same events.
- `scripts/phase12ah_c_controls.py` runs the direct-subset controls below.
- `slurm/phase12ah_c_*` holds the jobs and their submit script.
- `tests/test_phase12ah_c_subsets.py` has 12 CPU tests on tiny inputs, all
  passing:
  - the coverage shares equal shares built into a synthetic store;
  - the guard terms equal 12AG's point by point, including penalised points;
  - the reconstruction equals core run directly on a store holding only a
    subset's events. This is checked through the control script itself, for
    the DESI target (12AG's driver) and for the spectral-only likelihood
    (`phase12t_stage.py spectral`);
  - the random draws, the edge flag and every reading rule;
  - end to end on synthetic grids, the run reads "informs … dilute" when only
    the subset's events carry catalog curvature, and "do not explain it" when
    none do. It fails closed when one recorded point is altered by 1e-6.
    `part_c.json` holds no H0 location.

**The subset lists.** Built 2026-10-19 at 07:58 UTC by job 1390251 from a
worktree of a90e7b9, from the PE samples and the footprint only.

- Every count equals the declared table, at all three references and all four
  thresholds. The context counts match too: 165 events have p_i ≥ 0.5, and 72
  have d_i(67.74) ≥ 0.5.
- 64.46% of the nside-128 pixels have f_p > 0.
- No PE sample lies beyond core's distance table at 50, 67.74 or 90.
- The files are under `phase12_5/no_info_diagnostics/coverage/`:

| file | events | sha256 |
|---|---|---|
| `subset_S.txt` (j_i ≥ 0.5) | 45 | `09835a1326c952cd75e497359b56946e5f2a08e2f57ff2f17c8091dbb3d7c2e8` |
| `subset_S_prime.txt` (j_i ≥ 0.25) | 69 | `be00dc46075a4b6fed8fe802cf3d0c39e99ef5fa5599e2232371d4b207310cda` |
| `subset_complement.txt` (j_i < 0.5) | 214 | `73d1c3c93ce8cc191128d186c97e9ddcb6c96f92e26adfb23a547051b593cfff` |
| `coverage_events.csv` (p_i, d_i, j_i) | 259 | `91b80ad9c76038d374c242cbd54feee4be40945945dda5ea65ebb92522274ad0` |
| `coverage.json` | | `16ce8683bf75ebff9021421512dbe3af94d1d1a5c673d353d467055616467f4e` |

**Details fixed here, before any subset grid,** where the declaration left a
choice:

1. **The readings are applied in this order:**
   - "incomplete";
   - "edge-limited";
   - "limited by the Monte-Carlo variance" (in 12AG it replaces the R bands);
   - "the catalog informs the well-covered events (… and the other events
     dilute it)";
   - "a hint in the well-covered events";
   - "coverage and depth do not explain it";
   - otherwise "not covered by the declared rules". This is the case of
     R_S ≤ 0.97 above the random subsets' 95th percentile. It is reported
     with its numbers and not read.
2. **"Below the 5th percentile"** means R_S is below the 5th percentile of the
   finite R of the 1000 random subsets of the same size. Edge-limited random
   subsets stay in the distribution. Their count, and the percentiles without
   them, are reported.
3. **The draws** come from one `default_rng(20261019)`: first the 1000 subsets
   of 45 events, then the 1000 of 69, each `rng.choice(259, n,
   replace=False)`. The same subsets are used at both cells.
4. **A subset grid's Monte-Carlo condition** is 12AG's at N = N_S:
   Σ_S var_i + N_S²/N_eff ≤ 2 inside its 90% interval. Penalised points come
   from core's correction at N_S.
5. **Part C fails closed.** Nothing of it is read unless all of these hold:
   - the per-event sum reproduces every recorded ln L of the three grids, to
     1e-9;
   - the spectral rerun equals the reference, to 1e-9;
   - the catalog reruns equal 12AG's grids, to 1e-10;
   - the all-events subset reproduces 12AG's R of each cell, to 1e-6.

**Controls (passed).** Core is run directly on PE stores holding only the
events of S, S′ or the complement. Everything else is unchanged, and the run
is compared with the reconstruction from the full run's per-event terms. Ten
grid points were fixed a priori: 20, 30, 45, 50, 60, 67.5, 75, 90, 110 and 140.
The outputs (`controls/c_direct_*.json`) hold differences only.

- **Spectral-only, CPU (job 1390251):**
  - The full run equals the reference grid exactly (difference 0).
  - Its per-event sum reproduces the reference to 1.4e-12.
  - The direct subset runs equal the reconstruction to 1.1e-13 (S), 2.3e-13
    (S′) and 1.4e-12 (complement).
  - Their per-event log evidences and variances, log mu and N_eff equal the
    full run's bit for bit.
  - The guard terms agree. No control point is penalised at the subset sizes.
- **DESI target, production cell (nside 64, sigma_kde 3e-3), one twig A100-40 (job 1390252):**
  - The full run equals 12AG's production grid exactly at the ten points
    (difference 0; tolerance 1e-10).
  - Its per-event sum reproduces it to 9.1e-13.
  - The direct subset runs equal the reconstruction to 1.1e-13 (S), 1.1e-13
    (S′) and 6.8e-13 (complement).
  - Their per-event log evidences and variances, log mu and N_eff equal the
    full run's bit for bit.
  - The guard terms agree. No control point is penalised at the subset sizes.
  - Each build plus ten points took about 100 s.
  - Output sha256: `c_direct_catalog.json` `d151d5f9056ba32480ca04cfb330cd7fd5eef04d133eb807774085f9e4ef1bf6`,
    `c_direct_spectral.json` `7bbc5b77aab318c399fddac64cfc3f5cd5178831cd8faceb1132c1c42c1f5527`.

  So a run of core on a subset's events alone is reproduced by the per-event
  reconstruction to about 1e-12, on both the catalog and the spectral-only
  side. This is the exactness Part C relies on.

**Production job, prepared and not submitted.** Part C needs no new GPU grid.
One CPU job, `slurm/phase12ah_c_summary_henon.sbatch`, is submitted by
`slurm/phase12ah_c_submit.sh production --after <ids of Part A's lanes and of
the spectral rerun> [COMMIT]`.

- It starts after those jobs, whatever their exit (afterany). The script
  itself refuses to read anything when a control fails.
- It runs on HENON (7-day maximum). With `CPU_LANE=twig` it runs on the twig
  node without a GPU (2-day maximum). At 07:55 UTC every HENON CPU was
  allocated, so the controls ran on twig.
- It writes `summary/part_c/part_c.json` (location-free),
  `part_c_absolute.json` and `part_c_grids.npz` (absolute values, not for
  agents), and `STATUS_C.json`.
- **Estimate:** about 5 minutes once Part A's production grids and the
  spectral rerun are done.

### Amendment C2 (2026-10-19, before any subset grid): per-cell gating, a curvature fallback, the CPU lane

**Status.** Part C is **held** with Part A, whose per-event grids it reads
(amendment A2). No subset grid exists.

**1. Each cell gates only itself.** The declared gate was global. So the
support-only hint cell (nside 256, sigma_kde 1e-2) also gated the primary
reading: a rita lane that stopped part way would leave a partial `scan.json`,
and Part C would then read "not read: a control failed" even with a clean
production cell. Fixed now:

- **The spectral controls gate everything:** the spectral rerun reproduces
  its own ln L from the per-event terms, and it equals the reference.
- **The production cell's own controls gate the primary S reading and its
  S′ support reading.** They are: it loads, with the PE file's event order;
  it reproduces its own ln L; it equals 12AG's grid; its guard and H0 grid
  equal the spectral grid's; and all events give 12AG's R.
- **The hint cell's own controls (the same list) gate only the hint cell's
  support readings.** A hint cell that is missing is "absent". One that is
  partial, does not load or fails a control is "not read". Neither blocks
  the production reading.
- A cell that fails is not analysed at all.
- `part_c.json` records `controls_passed` (the primary gate),
  `controls_passed_by_cell`, `spectral_controls_passed` and
  `all_controls_passed`.
- The job exits 2 only when a spectral or production-cell control fails.

**2. A curvature fallback when a subset grid is edge-limited.** S holds the
45 low-redshift events, where the spectral-only likelihood has little lever
arm. So S's 99% interval, catalog or spectral, may come within one grid step
of 20 or 140, and the declared edge rule would then leave Part C with no
reading. Fixed now, before any subset grid. The fallback is used **only when
the subset grid is edge-limited**; otherwise the declared R reading stands
unchanged.

- **Statistic.** a_I is the curvature over the window W = [50, 90] (Part A's
  window, 81 grid points, fixed a priori) of ln L_I^cat(H0) − ln L_I^spec(H0).
  Both are core's own assembly for the subset's events, guard included.
  a_I is twice the quadratic coefficient of the least-squares quadratic in
  u = (H0 − 70)/10, in nats per (10 km/s/Mpc)², Part A's convention.
  a_I < 0 means the catalog sharpens. The selection terms are those of a run
  on I alone, so a_I is the subset's catalog-minus-spectral curvature, and
  no H0 location enters it.
- **Monte-Carlo condition.** The catalog subset grid has no penalised point in
  W, and its total Monte-Carlo variance (Σ_I var_i + N_I²/N_eff) is at most 2
  at every point of W (12AG's limit). Otherwise the reading is "limited by the
  Monte-Carlo variance (curvature fallback)".
- **Random control.** The same statistic on the same 1000 random subsets of
  the same size, using the declared draws. The comparison uses the finite
  values.
- **Readings, for an edge-limited S:**
  - a_S < 0 and below the random subsets' 5th percentile reads **"the catalog
    informs the well-covered events (curvature fallback)"**. If the complement
    reads "no narrowing", it adds **"… and the other events dilute it"**.
  - a_S not below the 5th percentile reads **"coverage and depth do not
    explain it (curvature fallback)"**.
  - Anything else is "not covered by the declared rules".
  - If the curvature cannot be evaluated (not finite over W), the reading
    stays "edge-limited (not read)".
  - The fallback has no "hint" level.
- S′ and the hint cell are read the same way, as support only.
- **Reported for every subset**, edge-limited or not: a_I, the subset's
  catalog and spectral curvatures over W, F_I = a_I / q_I^spec (when
  q_I^spec < 0), the window's Monte-Carlo numbers, and a_S's percentile
  among the random subsets.
- **Overall reading.** Reading 1 counts the fallback's "informs" the same as
  the R reading's, and says which was used.

**3. The CPU lane.** The production summary uses `CPU_LANE=henon`, the default.
`CPU_LANE=twig` puts the 8-CPU job on the twig node. Each twig GPU lane asks
for 32 of its 128 CPUs, so while that job runs only three GPU lanes can
start. Twig is used only when no twig GPU lane is queued.

**Code (working tree, not yet committed or tested):**

- `scripts/phase12ah_c_subsets.py`: `_load_grid`, per-cell `cell_ok`,
  `window_mask`, `window_curvatures`, `window_record`, `curvature_rank` and
  `fallback_key`. `c_reading` takes the curvature rank. `random_control`
  adds each random subset's a. The schema is `darksirens-phase12ah-c-subsets-2`.
- `tests/test_phase12ah_c_subsets.py` adds the fallback rules to the
  reading-rules test, and adds three tests:
  - the window curvature against Part A's `curve_metrics`, and the random
    rank;
  - end to end, an edge-limited synthetic S reads the fallback's "informs …
    dilute", with a_S equal to the constructed −8 × (10/18)²;
  - a partial hint cell, and a hint cell that fails its 12AG comparison, leave
    the production reading standing; with its true reference the hint cell is
    read as support.

  The fail-closed test now also checks the per-cell status.

The reconstruction (`subset_terms`, `terms_from_sums`, `correction`) is
unchanged, so the direct-subset controls of the first Part C amendment
(jobs 1390251 and 1390252) still apply. The CPU tests must pass on the new
commit before Part C's job.

## Part D — luminosity weighting: what core e7c3007 supports

### Verdict: not supported consistently. Design only; nothing is built or run.

Core e7c3007 (the pinned core; paths under `src/darksirens/` at
e7c3007c659205cf4d55279c8e016014c57aa9b3):

1. **Per-galaxy weights only redistribute inside a pixel.**
   `catalog/redshift.py:310-319` (`_row_kernel_state`): the weights `wgals`
   are normalised to unit total in each pixel,
   `log_w_norm = log_w - logsumexp(log_w)`. A weight changes which galaxy in a
   pixel hosts. It reaches the pixel's host mass only through an average: the
   depth mass that scales N_obs is the weight-averaged below-depth mass of the
   galaxies' kernels (`_renormalize_below_depth`, called from
   `_row_kernel_state`). It never enters as an amplitude. (Corrected by
   amendment D1. The declaration said "never how much host mass the pixel
   holds".)
2. **The pixel's catalog amplitude is the galaxy count.**
   `catalog/models.py:140-143` (`assemble_incomplete_catalog_prior_state`):
   `Nobs = ngals × (kernel mass below the depth)`, and the pixel normaliser is
   N_obs + N_miss. The DESI field target takes this state unchanged
   (`catalog/field.py:276-287`, evaluated at `field.py:300-314` as the
   numerator N_obs p_cat + dN_miss).
3. **The completion term is missing number, not missing luminosity.**
   `selection/footprint.py:101-104` (the DESI target's
   `selection_completion_curves_with_row_fraction`): dN_miss =
   (1 − f_p C̄(z)) n0 dV/dz, with C̄ the number completeness of the Gaussian
   luminosity function, `selection/catalog.py:223-241`
   (`ndtr((m_lim − M0 − DM)/sigma_M)`). The count-ratio estimator says so
   explicitly: "Raw galaxy counts are used. Catalog host weights ... do not
   enter" (`catalog/completeness.py:169-171`).
4. **The one weighted-host model in core is not a luminosity model and is not
   on this path.** `catalog/hosts.py` (marked hosts, h = exp(η · m̃) on
   z-centred marks) gives the observed branch N_obs ⟨h⟩ (`hosts.py:380-390`),
   but it gives the missing hosts the observed galaxies' mean mark,
   mu_miss = E_obs[h | z] (`hosts.py:454-516`, used at `hosts.py:536-540`),
   not the luminosity of the galaxies below the flux limit; it uses the
   count-ratio completion (`hosts.py:536`); and it is wired only to the
   conditional likelihood (`likelihood/marked.py:74-77`), not to the field
   target, the footprint or the selection completeness.
5. Core main today (1022429) is the same at `catalog/models.py:140`.

Writing luminosities into `wgals` would therefore give a half-consistent
model: hosts weighted by luminosity inside each pixel, but pixels weighted by
galaxy number and completed by missing number. **It is not run.**

### Design (for the owner; a core change is a PR and the owner's call)

**The model.** In units of the luminosity function's mean luminosity ⟨L⟩,
each galaxy's host weight is ℓ_i = L_i / ⟨L⟩, and the field numerator of
pixel p becomes

    n_L(z, p) = Σ_{i∈p} ℓ_i m_i K_i(z)
                + Ω_p n0 g(z) [1 − f_p C_L(z)]        (z ≤ z_depth)
                + Ω_p n0 g(z)                          (z > z_depth)

with K_i the unit-mass kernel, m_i its mass below the depth (per galaxy, not
per pixel), g = dV_c/dz (1+z)^δ, and n0 then the number density of an ⟨L⟩
galaxy, so that n0 ⟨ℓ⟩ is the luminosity density.

**Weights from apparent magnitude, redshift and the k-correction.**
M̂_i = m_i − DM(z_i; H0 = 100, Om0 0.3089) − K(z_i), with the production
k-correction K(z) = 1.13465 z − 4.88963 z² + 8.58828 z³. For the Gaussian
luminosity function N(M0, σ_M):

    ℓ_i = 10^(−0.4 (M̂_i − M0hat)) / exp((0.4 ln 10 σ_M)² / 2)

**How the H0 dependence of L is handled.** In the h-scaled convention core
already uses (`selection/catalog.py:9-14`), M_i = M̂_i + 5 log10 h and
M0 = M0hat + 5 log10 h. The h terms cancel in ℓ_i, so **ℓ_i does not depend
on H0.** It depends on the nuisances M0hat and σ_M only through a factor
common to every galaxy, which core would carry as one theta-dependent scalar
times a theta-free per-pixel sum Σ 10^(−0.4 M̂_i). The fixed reference
cosmology enters only through DM at H0 = 100 and Om0 0.3089.

**The matching completion.** Luminosity-weighting a Gaussian in magnitude
shifts its mean by −0.4 ln 10 σ_M², so

    C_L(z) = Φ((m_lim − DM(z) − K(z) − M0 + 0.4 ln 10 σ_M²) / σ_M)

in closed form (Schechter: Γ(α+2, x_lim) / Γ(α+2, x_faint)). The faint
galaxies are below the limit, so C_L > C̄ at every z: luminosity weighting
shrinks the completion term.

**One approximation to state:** ℓ_i is evaluated at the catalog redshift.
For a photometric galaxy the true redshift is spread over the kernel; a 1σ
photo-z error of 0.03 at z 0.2 moves DM by about 0.35 mag, so L by about 30%.
The exact form folds 10^(0.4 DM(z)) into each kernel, which changes the
per-galaxy normaliser.

**What core would need (one opt-in, the count model staying the default):**

1. A weighted observed amplitude on the field path: Σ_i ℓ_i m_i in place of
   `ngals` × the pixel's depth mass (`catalog/models.py:140-143`, and the
   field assembly), with the per-galaxy depth mass.
2. The luminosity-weighted completion curve beside `c_sel_gaussian` and
   `c_sel_schechter` (`selection/catalog.py`), and in the footprint
   composition (`selection/footprint.py:60-118`) and its gathered form.
3. The M0hat and σ_M factor threaded into the observed amplitude as a traced
   scalar.
4. The kernel pin, the galaxy list and the kernel window kept: the weights
   enter only amplitudes and within-pixel mixtures, not the kernel shapes.
5. Tests: the count model is recovered exactly when every ℓ_i = 1 and
   C_L = C̄; a closure test on a luminosity-weighted mock universe
   (darksirens-examples).
6. The consumer then writes 10^(−0.4 M̂_i) into `wgals` from M_APP, Z and the
   k-correction; the catalog file already has the column (all 1 now).

**Amendment D1 (2026-10-19, design only; nothing runs).**

- **Item 1 is corrected above.** The weights do shift N_obs, through the
  weight-averaged depth mass, but never as an amplitude. The verdict, "not
  supported consistently", is unchanged.
- **A seventh change core would need: n0 must match the luminosity sum.**
  In a luminosity-weighted model, the fixed n0 must match the observed
  luminosity sum: Σ_i ℓ_i against n0 ∫ f_p C_L(z) g(z) dz over the
  footprint. That equals the count calibration (Σ_i 1 against n0 ∫ f_p C̄ g)
  only if the luminosity function is exact. So the count-ridge n0 is either
  re-derived from the luminosity sum or checked against it, and the
  difference is reported.
- **Optional for change 2.** Core main's tabulated completeness family
  (PR #64, opt-in `completeness="selection"` with family `tabulated`) could
  carry C_L(z) as a table. It is not in the pinned e7c3007.

**Part D stops here.**

## Controls (all must pass before any result is read)

1. **Grid reproduction.** The production cell, rerun at the new commit with
   the per-event evidence, equals 12AG's grid at all 241 points:
   |Δ ln L| ≤ 1e-10 (12AG's control reproduced across A100-40 and A100-80 bit
   for bit). The hint cell likewise against 12AG's.
2. **Per-event sum.** At every point of every new catalog and spectral grid,
   Σ_i ev_i + core's `selection_log_correction(ln mu, N_eff, 259, soft guard,
   20, Σ_i var_i)` equals the recorded ln L to ≤ 1e-9. This is what makes
   Part C's reconstruction exact.
3. **The spectral-only rerun** equals the reference grid (`db9f7b80…`) at all
   241 points to ≤ 1e-9 and passes control 2.
4. **Branch identities (Part A).** For every event at each H_ref:
   logaddexp(catalog, completion) equals full to ≤ 1e-8; the full branch at
   50 and 90 (grid points) equals the grid's ev_i to ≤ 1e-10; the depth and
   footprint shares lie in [0, 1].
5. **The scaled catalogs' gates** and **the spectroscopic catalogs' gates**
   (Part B).
6. **The spectroscopic configuration.** The spectroscopic cells' resolved
   configuration equals 12U's chain configuration (`073243be…`) except the
   declared keys: the population's fixed values, the calibration preset,
   delta, log10 n0, sigma_kde of the 1e-3 cells, the sampler block and the
   input paths at nside 256. And 12U's 12-point spectroscopic scan, rerun from
   the new commit with its recorded arguments, equals 12U's scan
   (`2abadd4b…`) to ≤ 1e-6 at all 12 points.
7. **CPU tests on tiny inputs:** the branch identity; the subset
   reconstruction against a direct core evaluation on a store holding only
   the subset's events; the full branch equals the production density bit for
   bit; the dz-scaling gates on a synthetic table; the detrended spread and
   the quadratic curvature on synthetic curves with known answers.

A control that fails stops the part it guards. The record says so, and
nothing of that part is read.

## Compute plan

**Amendment R1 (2026-10-19): the plan below is superseded by the per-part
submit scripts.** Stages 1 and 2 already ran as Part B's catalog builds and
controls (B1) and Part C's coverage and controls (the first Part C amendment).
The one-script plan and its "11:00 to 12:00 UTC" estimate no longer apply.
From here, every job uses its partition's maximum time, and the order is:

1. **Part B, now (no dependency on the push):**
   `slurm/phase12ah_b_submit_grids.sh 416f5d7`.
   - Lanes: rita0 and rita1 (A100-80), twig0 to twig3, and henon-gpu.
   - Then the Part B summary on HENON (afterany), which always writes
     `summary/part_b/STATUS_B.json`.
   - About 20 minutes from submission if both rita cards are free.
2. **Before Part A and Part C:**
   - the CPU tests of A, B and C, and the new overall test, pass on the
     working tree;
   - one commit holds A2, C2 and the overall summary;
   - the owner (or the main session with the owner's approval) pushes the
     branch;
   - that commit is recorded here.
   About 15 minutes after a working shell is back, plus the owner's push.
3. **Part A's short controls:** `slurm/phase12ah_a_submit_controls.sh <commit>`.
   The nside-64 lane (twig) takes about 12 min, the nside-256 lane (rita) about
   16 min, the spectral grid on HENON CPU about 7 min, and the checks about
   2 min. About 25 minutes, or about 40 if Part B's rita lanes still hold both
   rita cards.
4. **When `controls/part_a/controls_a.json` passes:**
   - **Part A's production:** `slurm/phase12ah_a_submit.sh <commit>`, about
     25 minutes. The rita lane for the hint cell is the longest, about
     17 minutes.
   - **Part C:** `CPU_LANE=henon slurm/phase12ah_c_submit.sh production --after
     <Part A's lane ids, the spectral one included> <commit>`, about 5 minutes
     after them.
   - **The overall summary:** `slurm/phase12ah_summary_henon.sbatch` on HENON,
     with afterany on the A, B and C summary jobs. It always writes
     `summary/STATUS.json`. About 1 minute.

**Estimated time to completion:**

- Part B: about 20 minutes after its submission.
- Parts A and C and the overall summary: about 1 hour 10 minutes after the
  push. That is about 50 minutes for A (controls, then production), 5 for C,
  1 for the overall summary, and about 15 for tests and the commit before
  the push.
- All of this assumes a rita card and a twig card are free. If another user
  holds rita, the nside-256 lanes wait for it, as on 2026-10-18 (about
  4 hours).

## Compute plan as declared (superseded; kept for the record)

Every job requests its partition's maximum time (a ceiling, not the
estimate). The miko holder, the second miko card and js2h100 are not used;
other users' jobs are left alone.

- **Stage 1, HENON CPU** (`--time=7-00:00:00 --exclude=henon06,henon08`,
  about 32 CPUs, 120 GB): the four scaled union catalogs, the two
  spectroscopic catalogs and the upgraded spectroscopic footprint, their
  gates, the configuration check, and the coverage shares and subset lists.
  About 25 minutes (12AG's four builds took 11 minutes).
- **Stage 2, HENON CPU,** in parallel with stage 1: the spectral-only rerun
  with per-event evidence, and controls 2 and 3. About 5 minutes.
- **Stage 3, GPU lanes,** after stage 1 (`--dependency=afterok`):
  - rita × 2 (A100-80; `-p RITA-GPU --qos rita --gres=gpu:a100-80:1
    --cpus-per-task=128 --mem=120G --time=7-00:00:00`, account as 12AG): the
    nside-256 work, routed there by 12AG's memory rule (device peak about
    49 GiB). rita0: the hint cell rerun and its branches; the scaled union
    at s 0.5 and 0.25, sigma_kde 3e-3; the spectroscopic grid at 3e-3.
    rita1: the scaled union at s 0.5 and 0.25, sigma_kde 1e-3; the
    spectroscopic grid at 1e-3.
  - twig × 4 (A100-40; `-p TWIG-GPU -A phy220048p --qos twig
    --gres=gpu:a100-40:1 --cpus-per-task=32 --mem=120G --time=2-00:00:00`)
    and the free henon-gpu card (`-p HENON-GPU --qos henon-gpu
    --gres=gpu:a100-40:1 --cpus-per-task=64 --mem=240G --time=7-00:00:00`):
    the nside-64 work. The production cell rerun and its branches; the four
    scaled union grids; the two spectroscopic grids; 12U's spectroscopic scan
    check.
  - Each grid is about 4 to 5 minutes (12AG: three nside-256 grids per rita
    lane in 10 to 11 minutes; nside 64 about 4.3 minutes each). Branch
    evaluations: one compile per branch (about 90 s) plus seconds per point,
    under 10 minutes per cell. Longest lane: rita0, about 25 minutes.
- **Stage 4, HENON CPU summary** (`--dependency=afterany` on every lane, a few
  minutes): the readings of A, B and C, `summary.json` (location-free) and
  `summary_absolute.json`.
- One submit script does stages 1 to 4, from a worktree of the recorded
  commit, after the amendment with that commit is pushed.

**Estimated time to completion:** about 3 to 4 hours from now (07:40 UTC),
so results around 11:00 to 12:00 UTC. That is about 2 to 3 hours to write the
code, run the CPU tests and push the amendment, then about 1 hour from
submission: catalogs 25 minutes, GPU lanes 25 minutes, summary 5 minutes. At
07:35 UTC both rita cards and all four twig cards were idle and one henon-gpu
card was free. If another user takes rita, the nside-256 grids wait for it
(about 4 hours on 2026-10-18), so the worst case is about 8 hours.

## The overall reading across A to D (fixed now)

Every statement whose trigger holds is reported; they are not exclusive.

1. **"Information exists but is diluted"**: Part C reads "the catalog informs
   the well-covered events".
2. **"The photometric redshift errors wash the information out"**: Part B
   reads "the photometric errors wash out the information".
3. **"Exact redshifts carry information"**: Part B's spectroscopic grids read
   "narrows".
4. **"The catalog dominates where it reaches but carries no H0 structure"**:
   Part A's reading 2 holds and none of 1 to 3 does. The null is then a
   property of this catalog and event set at this depth, at the redshift
   precision and pixel scales tested, not a coverage, smearing or
   photometric-redshift artefact within the ranges tested.
5. **"The catalog reaches too few events"**: Part A reads "few" and none of
   1 to 3 holds. The null is then mostly a coverage and depth fact.
6. Part A's readings 3 (structure that cancels) and 4 (the selection term
   offsets it) are reported beside whichever of 1 to 5 holds.
7. **"Not localised"** if none of 1 to 5 holds.

Part D adds no reading: it is design only.

**Amendment R1 (2026-10-19, before any production run):**

- **Rule 6** reports only Part A's reading 3 (structure that cancels).
  Reading 4 was withdrawn by amendment A2; its quantities are reported as
  Part A diagnostics.
- **Rule 1** counts Part C's curvature-fallback "informs" (amendment C2) the
  same as the R reading's, and says which was used.
- **A part that was not read** (held, a primary control failed, or its summary
  is missing) makes the overall reading **"incomplete"**, naming the part.
  Rules 4 and 5 are then conditional on the parts read, and rule 7 ("not
  localised") is not stated.
- **The overall reading is computed by `scripts/phase12ah_summary.py`** from
  the three location-free part summaries only. It writes
  `summary/summary.json` and always `summary/STATUS.json`; the test is
  `tests/test_phase12ah_overall.py`. These are working-tree changes, not yet
  committed or tested.

Any part limited by the Monte-Carlo variance is named with its reading. A
"no information" reading of any part does not test what lies outside it:
luminosity weighting (Part D, not run), the footprint and catalog
disagreement noted in 12AG (about 1,000 deg² of covered pixels with no
galaxy), the calibration held fixed, and the population held fixed.

## Results

Not run. The code commit, its CPU tests, the build records and the subset
lists are appended here, as an amendment, before any job is submitted.
