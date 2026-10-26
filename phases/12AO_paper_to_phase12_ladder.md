# 12AO — From the DESI paper line to Phase 12, one change per step (the like-for-like ladder)

## Status

**DONE (2026-10-21, summary 06:11 UTC).** Results in "Results" at the end (location-free); amendment B2 records
the one rerun (step I). As declared:

**DECLARED (2026-10-21, about 02:00 UTC), before any 12AO job.** Nothing has been submitted. This record fixes the
question, the steps, the inputs, the controls, what is reported and the compute. The build stage (code, CPU tests and
a CPU smoke on this node) is done and is recorded in amendment B1 at the end; the smoke is plumbing, not a result.

The only things read for this record:
- the location-free paper-repo notes (`phase12_5/paper_repo_notes/`: INDEX, legacy-code, pipeline-catalog,
  production, catalog-experiments), whose statements about the paper repo are treated as claims;
- the paper repo's code, file headers and attributes (read only): `build_loa_rebuild.py`, `build_combined_catalog.py`,
  the pin's `cli/pixelate.py`, the population JSON, the header line of the shipped `h0_scan.csv`, the dataset names of
  the shipped `components.h5`;
- core's source at e7c3007 (in the consumer env) and the consumer's source at cb7c638 (record 12AN);
- file sizes, sha256, event-name lists and the Slurm partition limits.

No absolute file was opened. The shipped `h0_scan.csv` and `components.h5` are read only by the summary job (and by
the smoke's summary for two events), only to compute max |Δ ln L| after removing a constant.

**Blinding: location-free**, as in 12AG to 12AN. No H0 location appears here, in commit messages, code comments,
logs agents read or summaries: no median, interval, MAP or shift in km/s/Mpc. The H0 values in this record are fixed a
priori: the grids ([20, 140] at step 0.25, [50, 100] at step 0.1), the smoke points (20 to 140 at step 10), the
control points 50, 75 and 100, the PE cosmology's 67.74, and core's kernel reference 67.74.

**The owner's reporting rule (binding).** Posteriors and ln L differences are reported as numbers; no bands, no
z-scores, no p-values, no noise-floor tests, no "narrows" or "rules out". When a step moves the result, its size and
direction are written (as a shift in spectral sd and a width ratio), and nothing more is read into it. Controls are
numerical gates; they decide only what is withheld.

## The question

The paper line (desi_darksirens_selection, the a14fix pin) reports catalog information on 21 events with a
complete-catalog likelihood on the DESI BGS v2 catalog. Phase 12 (the union catalog with a fill-in, core's production
selection term) finds almost none: its catalog posterior is about as wide as spectral-only (12AG to 12AN). The paper
notes list several differences, any of which could carry the gap:
- the paper's PE is cut at z <= 0.30 at the PE cosmology (dL <= 1601.9 Mpc); its injections are not (notes, verified);
- the pin's GWTC-5 mass normaliser is 3% off at the medians (pin-equivalent mixing fractions 0.393274, 0.552162,
  0.054564 against nominal 0.400383, 0.545692, 0.053925);
- its selection is the emulated pass probability beta_S, not all-sky detected injections;
- the complete-catalog model ends the universe at the catalog's edge (z 0.30), which dominates mu(H0) (notes);
- each occupied pixel has equal sky weight, whatever its galaxy count ("conditional");
- the union catalog has a spectra leak: spectra with z in (0.30, 0.50] stay photometric rows (notes, section 4.1);
- Phase 12 adds a fill-in, calibrated density, its own population, Om0 and guard.

**Question.** Starting from the paper as built in core, and changing one thing at a time toward Phase 12, where does
the catalog's effect on the posterior (its width against spectral-only, its shift, and ln L_cat − ln L_spec over the
window) change, by how much, and in which direction? Every catalog step is paired with spectral-only on the same
events, the same selection and the same population, so a step's effect is the catalog's, not a change of events,
selection or population.

## The core commit, and why

**darksirens-core e7c3007** (e7c3007c659205cf4d55279c8e016014c57aa9b3), through the consumer env
`phase12t/envs/consumer_e7c3007_cuda12` (nothing installed into it). Reasons:
- it is the pin of the 12AN consumer and env, so step I is Phase 12's treatment exactly as in 12AG to 12AN (Lane A of
  12AH, unchanged);
- it has every option the paper's likelihood needs: `completeness="complete"`, `empty_policy="zero"`,
  `catalog_sky_weighting="conditional"`, `fixed_survey={delta, sigma_kde}`, `max_likelihood_variance=inf` (the pin's
  hard 5N guard alone), the field weighting (step G0), `completeness="selection"` with `z_depth` (step G);
- main's later commits (13: #52 to #68) are off this path or layout only: the README; `ds.log_likelihood` (#56; this
  record binds with `bind_analysis` instead); galaxy-list and memory work (#57, #58, #63); the GWTC-5 registry spin
  pair (#60; the paper line passes its own 17 values); input checks (#61); host mass from weights (#62, opt-in);
  tabulated completeness (#64, opt-in); the refusal of galaxies outside the kernel's redshift range (#65; padding
  only here); the pooled count ratio (#66, and #68 makes it the default; e7c3007 keeps the per-row ratio that 12AN ran).
- The one consequence: tabulated completeness (#64) is not at e7c3007, so step G uses core's selection completeness,
  made saturated, with the store's `z_depth` (below). It gives C = 1 below the depth and C = 0 above it, which is what
  a tabulated C(z) = 1(z <= 0.30) would give on core's grid.

## The steps (fixed now)

Grid for every entry: the paper's 481 points (20 + 0.25 k) plus the window [50, 100] at step 0.1; 881 points in all.

| entry | what it is | PE | selection | catalog | population | pair |
|---|---|---|---|---|---|---|
| **A** | the paper as built in core | paper 21 (cut at 1601.9 Mpc) | beta_S (21) | v2 | pin-equivalent fractions | E_A |
| **B** | A with the nominal fractions (exact normaliser) | paper 21 | beta_S | v2 | nominal | E_B |
| **C** | B with the trusted uncut PE | trusted 21 | beta_S | v2 | nominal | E_C |
| **D** | C with the paper's all-sky detected injections | trusted 21 | paper all-sky | v2 | nominal | E_D |
| **D2** | C with the trusted all-sky injections | trusted 21 | trusted all-sky | v2 | nominal | E_D2 |
| **E_\*** | spectral only on the same events, selection and population | as its step | as its step | none | as its step | — |
| **F** | C on the radial-null catalog | trusted 21 | beta_S | v2 radial null | nominal | E_C |
| **F2** | D2 on the radial-null catalog | trusted 21 | trusted all-sky | v2 radial null | nominal | E_D2 |
| **G0** | C with pixel weights by galaxy count (core's field weighting) | trusted 21 | beta_S | v2 | nominal | E_C |
| **G0_2** | D2, the same | trusted 21 | trusted all-sky | v2 | nominal | E_D2 |
| **G** | C with the soft edge (fill above 0.30) | trusted 21 | beta_S | v2 | nominal | E_C |
| **G2** | D2 with the soft edge | trusted 21 | trusted all-sky | v2 | nominal | E_D2 |
| **H_asis_bS / _D / _D2** | the union, the paper's treatment as in C/D | trusted 44 | beta_S (44) / paper all-sky / trusted all-sky | union as is (the paper's store) | nominal | E_HbS / E_HD / E_HD2 |
| **H_fix_bS / _D / _D2** | the same, spectra leak fixed | trusted 44 | as above | union, leak fixed | nominal | as above |
| **I_0245, I_030** | Phase 12's own treatment | trusted 44 | trusted all-sky | Phase 12's union (f26a20f0) | Phase 12's | E_I |

**Common to A to H (the paper's likelihood in core; the core-vs-pin settings table, checked in every job):**
- `ds.model(..., completeness="complete", empty_policy="zero", catalog_sky_weighting="conditional",
  fixed_survey={"delta": 0.0, "sigma_kde": 0.003}, kernel_pin="off")`; cosmology Om0 0.3075, w0 −1, wa 0, H0 the only
  label;
- population `gwtc5_fiducial_bpl2peaks` fixed at the paper's JSON (17 values by label);
- bound with `max_likelihood_variance=inf` (the pin's guard: −inf at N_eff <= 5N, and the +N(N+3)/(2 N_eff) term),
  no soft guard, `sel_batch_size=16384` (the paper's; a layout option), all events in one block;
- `DARKSIRENS_ZMAX` unset (core's default 5, the paper's: 1000 grid nodes);
- the pin's catalog arithmetic: `kernel_layout="padded"`, `missing_density="grid"`, `kernel_window="off"`.

**The events.** The paper's 21 (`marg_s05_noom/members.txt`) and 44 (`experiment_loa_rebuild/results/members44.txt`,
which contains the 21). A and B use the paper's own PE file (21 × 20,000 samples, cut at 1601.9 Mpc). C onward use the
same events taken from the trusted uncut file (`A_pe_chieff_bbh259_n4096_v20_exact.h5`, 4,096 samples per event) by
an exact subset: every kept event's block is copied bitwise and the event-set attributes are recomputed with gwcat
8263ae9's recipes (the validated 249-event tool, generalised; `scripts/phase12ao_subset_events.py`). One event of the
44 (GW200129_065458, also in the 21) was resampled with replacement upstream.

**The selections.**
- beta_S (21): `production_final/betas/selection_betaS_v2_r_v2_marg_s05_noom.h5` (435,184 rows; pdraw divided by the
  emulated pass probability; ndraw the global 944,412,448);
- beta_S (44): `experiment_loa_rebuild/inputs/selection_betaS_v2_loaFaint_marg_s0495_noom.h5`, the paper's own beta_S
  for the 44 (union footprint, threshold 0.495); used only in H (the beta_S analogue of C);
- the paper's all-sky detected injections: `selection_systematics/betaS/selection_o3o4ab_allsky_snr.h5`;
- the trusted all-sky injections: `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` (Phase 12's).

**Step A's population.** The pin's mass normaliser was a coarse grid; core's is exact. Passing λ0 = 0.393274 and
λ1 = 0.552162 (λ2 = 0.054564) to core reproduces the pin's mass shape (notes). B undoes only that.

**Step F, the radial null.** The v2 store with every galaxy's redshift redrawn from the catalog's global n(z): one
permutation of the redshifts of all 2,126,567 real galaxies, `numpy.random.default_rng(20261020).permutation`, applied
in the store's row-major real-galaxy order. Each galaxy keeps its pixel, its kernel width (`dzgals`) and its weight
(`wgals`); per-pixel counts, the footprint and padding are unchanged; the global n(z) is kept exactly (a draw without
replacement from the empirical n(z)). **Seed: 20261020.** (`scripts/phase12ao_radial_null.py`.)

**Step G, the soft edge (choice and justification).** "v2 complete below z 0.30 and a fill-in above it at the
catalog's own mean density", with core's options at e7c3007:
- **Chosen: the z_depth semantics with a saturated selection completeness.** `completeness="selection"` with a
  Gaussian magnitude selection (m_lim 30, M0hat −20, sigma_M 0.5, no K-correction) whose curve is exactly 1.0 in
  float64 at every grid node up to 0.30 (the normal-CDF argument is about 19 there), plus the store's own
  `z_depth = 0.30`, under which core sets C = 0 above the depth. So the missing-host density is exactly zero below 0.30
  and is n0 a_pix dV_c/dz above it. `n0_units="h_scaled"` with log10 n0 the catalog's own mean count density below
  0.30 (N_gal / (N_occupied a_pix ∫_0^0.30 dV_c/dz at h = 1); the job writes it), so the fill does not move with H0.
  Conditional rows, as in C; `kernel_pin="off"`.
- **Not chosen:** the count-ratio completeness with z_depth 0.30 (C(z) is the smoothed count ratio, below 1 in
  underdense pixels and near the edge (smoothing width 0.05): it adds hosts below 0.30, so it is not "complete below");
  tabulated completeness (not at e7c3007).
- **What is equal to C below 0.30, exactly.** In every pixel the host density below 0.30 is N_obs p_C(z | p): step C's
  per-pixel prior shape, unchanged (the catalog term is C's kernel sum; above the depth the galaxies' own Gaussian
  tails are replaced by the fill). Control G-T2 tests this row by row.
- **What is not, and why.** Core normalises each row by itself: p_G(z | p) = [N_obs p_C(z | p) + fill(z)] /
  (N_obs + N_miss). The fill's mass N_miss is the same in every pixel (equal solid angle), so below 0.30 pixel p holds
  N_obs / (N_obs + N_miss) of its mass: pixels with more galaxies weigh more. G therefore changes two things against C:
  the edge and the pixel weights. **Step G0** isolates the second: C with core's field weighting (each pixel weighted by
  its galaxy count, empty pixels zero, no fill). So C → G0 is the pixel weighting, G0 → G the soft edge (up to the
  fill's small departure from pure count weighting: N_obs / (N_obs + N_miss) against N_obs / ΣN_obs, which differ by
  at most N_obs / N_miss, about 2% for the fullest pixels). Empty pixels are zero below 0.30 in G (as in C) and carry the
  fill above it.
- An alternative that keeps C's equal pixel weights (a per-pixel fill at each pixel's own density) is not a core option;
  it is listed under decisions.

**Step H, the union.** As is: the paper's own store
(`experiment_loa_rebuild/inputs/rebuild_loa_faint_pixelated/catalog_pixelated_nside_128.h5`, 22,787,835 galaxies, up to
774 per pixel). Leak fixed: the paper's `build_loa_rebuild.py` run with the z <= 0.5 spectroscopic match file
(`loa_ls_match_z05.h5`, built from `loa_spec_z05.h5`), so a galaxy with a spectroscopic z in (0.30, 0.50] gets that z
and is removed by the z <= 0.30 cut, instead of staying a photometric row. The build is this branch's copy of the
paper's script (`scripts/phase12ao_build_loa_rebuild.py`): outputs go to `--out-dir`, `--match-file` is a path, no
`__pycache__` is written into the paper repo; every catalog rule is the paper's (a test checks the copy line by line).
The fixed flat table is pixelated in the paper's store layout (`scripts/phase12ao_pixelate.py`: the legacy
`darksirens.cli.pixelate` arithmetic, vectorised), all in the new directory `paper_ladder/union_rebuild/`. HENON CPU
Slurm job; nothing existing is overwritten.

**Step I, Phase 12's own treatment.** Lane A of 12AH (`phase12ah_a_scan.py`, unchanged) on the trusted 44: the union at
nside 128 (`smearing_ladder/catalogs/desi_union_nside128.h5`, f26a20f0, built from the same flat input as the paper's
store with Phase 12I's footprint mask: 2,556 fewer galaxies), the native nside-128 footprint, the fill-in under
core's production field model, the D0 selection term (core's stock target), the 12AG ladder calibration (log10 n0
−1.8216 h-scaled, M0hat −20.4975, sigma_M 0.5592, delta 0, m_lim 21, the production K-correction), sigma_kde 1e-3
(the owner's proposed fiducial cell), the population of Phase 12's config (core's GWTC-5 fixed values with mu_chi
0.04 and sigma_chi 0.10), Om0 0.3089, the soft guard with variance limit 20, `DARKSIRENS_ZMAX` 6.0, the trusted
all-sky injections. Depths 0.245 and 0.30 (the same calibration at both). Its spectral pair E_I is Phase 12's
spectral-only target (same population, cosmology and guard). H_asis_D2 → I_0245 is therefore a bundle (Phase 12's
treatment as a whole), as the question defines it.

## Inputs (sha256; every job checks them and refuses a mismatch)

Paths: R = `/hildafs/projects/phy230014p/magana/desi_darksirens_selection` (read only), D =
`/hildafs/projects/phy230054p/magana/darksirens-core-data`, L = `R/final/experiments/experiment_loa_rebuild`.

| input | path | sha256 |
|---|---|---|
| paper PE, 21 events (cut) | `R/production_final/events/marg_s05_noom/gw.h5` | `dbf6b7976993d43e9d3d9dcc58a5f74ec86cd62297d926dd54772a77518b6902` |
| 21 members | `R/production_final/events/marg_s05_noom/members.txt` | `1c6c926604bb443b797ac5a6f9e5360e97a4ace408701097932cae1a9b62606f` |
| 44 members | `L/results/members44.txt` | `9ff825446dd703d45f19c1db80564fe3ea67b9fc5a0c4ba0bf26933170761071` |
| trusted PE, 259 events | `D/phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| beta_S (21) | `R/production_final/betas/selection_betaS_v2_r_v2_marg_s05_noom.h5` | `b023e095377f81ef66735c88ccab3e45cb8990565251438f580c9800684cc024` |
| beta_S (44) | `L/inputs/selection_betaS_v2_loaFaint_marg_s0495_noom.h5` | `1ad1a65934fffa405ac5544af29da5f52a784af4213152e1fb738831238679ab` |
| paper all-sky injections | `R/selection_systematics/betaS/selection_o3o4ab_allsky_snr.h5` | `f18d8cd50e146bfbd0a8a9d1770cd3b84a341a257eab2962ac47b7be0ae2c412` |
| trusted all-sky injections | `D/phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| v2 catalog (nside 128) | `R/selection_systematics/catalogs/v2/catalog_pixelated_nside_128_native.h5` | `7eac8c548e979c6055757e4ba6018c60880e88eb408cb5b399dc0f67ea7f871c` |
| union store, as is (paper) | `L/inputs/rebuild_loa_faint_pixelated/catalog_pixelated_nside_128.h5` | `0ce1781f05b3b2e301c6b1b8d794d20f567bcb12886cd5fd9e92d29bfc5b86a7` |
| union flat input, as is | `L/inputs/rebuild_loa_faint_pixelate_input.h5` | `42e91b594572cfba716d0128ea3dcb24924a6c63e573078e7c4184fe24c0eaaa` |
| spec table z <= 0.3 / match | `L/inputs/loa_spec_z03.h5`, `L/inputs/loa_ls_match.h5` | `4a6b11243aa7689508590e15fdc80b6e530cb1c904fdd256993266b73ab099d9`, `c10a06ea60d6fdabfc424385bcf0db3789a9b4aa6d0ed4ab5d4d46653218dc9f` |
| spec table z <= 0.5 / match | `L/inputs/loa_spec_z05.h5`, `L/inputs/loa_ls_match_z05.h5` | `578df088bdf38c87a3a38092c978717811264ebf5c6f5cac490ff7620a7cbe85`, `b9e97ac686cd1de2bb1659a889bd16b0b888a376350a6a859ec3e6db66002a4e` |
| the paper's build scripts | `L/scripts/build_loa_rebuild.py`; `R/final/experiments/experiment_combined_desi_ls_des/scripts/build_combined_catalog.py` | `616867374057e518ad31c407fcab2fa27cd461cf37c966f0f066775a241bb13c`; `3453cce65e41eeab7fdec356ef352a5dc75a3a41c64dc3daeb8b030db7e2a326` |
| v2 flat table (DESI-only rows of the build) | `R/selection_systematics/catalogs/v2/pixelate_input.h5` | `9a4f909c66cc12b5374c6e0dda5676ff62a1f89badfcc5b1d1e781d8a96bc323` |
| paper population | `R/production_final/configs/gwtc5_pop_fiducial.json` | `4559b22eae3add73e7dfd622aeffe652570233086fdb80ccf3ce728f5ad63499` |
| A0: shipped curve | `R/production_final/runs/p2_v2_marg_s05_noom/h0_scan.csv` | `0198eec0de7c3ec72110601b9f385a8696fcaed451c78ba3ae6d807cef0989cf` |
| A0: shipped components | `R/production_final/runs/p2_v2_marg_s05_noom_components/components.h5` | `31deb606724dce11105e5ca14683f7d8e54e5fec938a765a9e029060a4e09e11` |
| Phase 12 union, nside 128 | `D/phase12_5/smearing_ladder/catalogs/desi_union_nside128.h5` | `f26a20f0f3f8ca5a9bc0aee0681cd0eba6f1a7b693055839cba83d6189cdb62c` |
| Phase 12 footprint, nside 128 | `D/phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| Phase 12 configuration | consumer `config/desi.fixed_population.json` | `b79ad777f17126bcd78b9ebcff0d02724ae6cfe7ae957829009ca5143f349bb9` |

**Made by this record's CPU jobs** (their sha256 are written by the job that makes them, and every consumer checks
them): `paper_ladder/inputs/pe_trusted21_n4096_v20_exact.h5`, `pe_trusted44_n4096_v20_exact.h5`,
`catalogs/v2_radial_null_seed20261020_nside128.h5` (`inputs/inputs.json`);
`paper_ladder/union_rebuild/pixelated/catalog_pixelated_nside_128.h5` (`union_rebuild/rebuild.json`).

## Controls (fixed now)

**Kinds.** An *entry gate* withholds that entry's numbers and every transition touching it. A *mark* is reported
beside the numbers; nothing is withheld. The summary always writes its numbers and STATUS.json.

- **A0 (mark on A; the ladder's anchor).** A's per-point ln L against the shipped `h0_scan.csv` on the 481 shared
  nodes, reported only as **max |Δ ln L| after removing a constant** (the mean difference over the finite nodes), and
  the count of nodes where one is finite and the other not. Per component against the shipped `components.h5`: each
  event's ln Z, ln mu and N_eff, each as max |Δ| after removing a constant (relative for N_eff), and the likelihood
  rebuilt from those components. **A reproduces the paper if max |Δ ln L| <= 0.02 nat with no finiteness mismatch.**
  Expected below that: the pin's pairing normaliser (at most 4e-4 nat per sample, at m1 about 5), rounding of the
  fractions to six digits, the z² law below the first grid cell (notes). No H0 value or posterior summary of the
  shipped files is computed or written.
- **The core-vs-pin settings table (entry gate on A to H and their pairs).** Every job records the settings it ran
  (completeness, empty policy, weighting, fixed survey and cosmology, population model and the sha256 of its 17
  values, the mixing fractions, the variance limit, the soft guard, sel_batch_size, DARKSIRENS_ZMAX, the z grid's
  nodes and top, the kernel layout, missing density and window, whether a kernel pin is active, core's commit) and the
  summary refuses any departure from the table above.
- **C3 (entry gate).** At 50, 75 and 100, the diagnostics' total equals the binding's own ln L to 1e-9 nat, with the
  same finiteness.
- **G-T2 (entry gate on G and G2).** At 50, 75 and 100, on 3,000 occupied and 300 empty rows of the compact catalog
  (seeded sample), against step C's prior on the same rows: the missing density is exactly zero at every grid node up
  to the last node <= 0.30; C_sel is exactly 1.0 there; below that node log p_G − log p_C = log N_obs − log Z_G per
  row to 1e-10 nat, the zero sets agree and empty rows are zero; at the nodes above, p_G is the fill alone to 1e-10
  and the fill is n0 a_pix dV_c/dz to 1e-12 relative. The pixels' catalog mass fractions N_obs / (N_obs + N_miss)
  (minimum, p50, maximum) are reported. (Between the last node below 0.30 and the first above it, core interpolates
  the missing density linearly: a ramp one grid cell wide, about 0.0023 in z.)
- **G-T1 (mark on G and G2; plumbing).** The same fill machinery with the fill switched off (log10 n0 = −30, no depth)
  against the complete catalog whose empty pixels carry the normalised volume prior (`empty_policy="volume"`), at the
  three control points. Empty pixels differ by interpolation only: the fill interpolates dN_exp linearly between grid
  nodes (with no z² law below the first node), the volume prior log-linearly. Tolerances (amended in B1, before any
  job; the first declaration, 1e-6 in ln mu, came from a wrong estimate of that difference): |Δ ln mu| <= 2e-3,
  each event's |Δ ln Z| <= 1e-4, |Δ ln L| <= N (1e-4 + 2e-3).
- **F's seed and build (entry gate on F and F2).** Seed 20261020; ngals, dzgals, wgals and padding bitwise unchanged;
  the sorted redshift multiset bitwise unchanged; the permutation reproduces bitwise from the seed; more than 90% of the
  galaxies' redshifts change.
- **The subsets (prep gate).** Every dataset of each subset equals the source's blocks bitwise; per-event attributes
  equal the kept entries; 21 and 44 events.
- **U0 (entry gate on H_fix).** This branch's copy of the build, run with the paper's own z <= 0.30 match file,
  reproduces the paper's as-is flat input column by column and row by row. If it does not, H_fix is withheld and the
  owner decides (the leak fix would then be confounded with an environment difference).
- **U1 (entry gate on H_fix).** This branch's pixelator, run on the paper's as-is flat input, equals the paper's own
  store per pixel (counts, and the sorted (z, dz, w) of each pixel; core sorts rows by z on load, so the order within
  a pixel is not part of the model).

## What is reported (fixed now; every number location-free)

**Per catalog entry, against its spectral pair** (`summary/summary.json`):
1. **Width:** R68 and R90, the ratios of the central 68% and 90% half-widths, and the sd ratio.
2. **Shift:** (median_cat − median_spec) / sd_spec.
3. **Hellinger distance** from spectral only.
4. **ln L_cat − ln L_spec over the fine window, mean removed:** its peak-to-peak and rms, and the same for its PE part
   (Σ ln Z) and its selection part. The curves themselves go to `summary/lnl_difference_window.npz` for the owner's
   plot (absolute; not for agents).
5. **ln L Monte-Carlo variance:** V_sel = N²/N_eff, V_PE = Σ σ²_e and V_tot, at their maximum over the entry's own
   central 90% interval, and over the window; the same for the pair.
6. Bookkeeping: the grid used (window or coarse, by 12AM's window rule: window posteriors when both have coarse mass
   outside [50, 100] at most 1e-3; the mass itself is never written), non-finite counts, timings (`p50_seconds`),
   memory, sizes.

**Per transition (one change; the table in `scripts/phase12ao_common.py`):** the shift between the two posteriors in
the destination pair's spectral sd, the change of R68 and of R90, and their Hellinger distance. The transitions: A→B
(fractions), B→C (PE), C→D and C→D2 and D→D2 (selection), C→F and D2→F2 (radial null), C→G0 and D2→G0_2 (pixel
weights), G0→G and G0_2→G2 (soft edge), C→G (both), H_asis→H_fix at each selection (the leak), H_asis_bS→H_asis_D and
H_asis_D→H_asis_D2 (selection on the union), H_asis_D2→I_0245 (Phase 12's treatment), I_0245→I_030 (depth).

**Controls** (`summary/controls.json`): A0 and its components, C3, the settings table, G-T1, G-T2, the prep and union
build records.

**Not written:** no band, verdict, z-score or p-value; no absolute posterior location; no count of points inside an
interval. The location guard (12AM's key list plus `logL`, `log_likelihood`, `lnL`; and no float equal to any median
computed in the job) refuses any write that would hold one. `summary/absolute.npz` (every entry's ln L on its grid)
is for the owner only.

## Compute (estimate; nothing submitted)

Per-point costs from the build's CPU smoke (8 cores of this node; amendment B1) and from 12AM/12AN's GPU stages.

| job / entry | card or CPU | per entry | basis |
|---|---|---|---|
| prep: subsets (21, 44) and the radial null | HENON CPU, 4 CPUs | about 5 min | smoke: a 2-event subset 15 s; the v2 store is 0.7 GB |
| union rebuild: the two builds in parallel, U0, U1, the fixed store, statistics | HENON CPU, 16 CPUs, 96 GB | about 35 to 45 min | the paper's log: 16.5 min per build |
| E_* spectral pairs (9) | GPU | about 1 min each | smoke: 0.08 s per point on CPU |
| v2 complete entries (A, B, C, D, D2, F, F2, G0, G0_2) | A100-80 | about 4 to 7 min each | smoke: 13 s per point on 8 CPU cores (152,147 compact rows × 145 slots, 435k injections); about 0.2 to 0.4 s per point on an A100 |
| G, G2 (with G-T1, G-T2) | A100-80 | about 6 to 10 min each | the incomplete path and four extra bindings |
| H entries (6), union complete, 774 slots, 44 events | A100-40 | about 15 to 30 min each | about 5 times v2's slots; the kernel build runs in 512-row chunks |
| I_0245, I_030 (Lane A, 44 events, nside 128) | A100-80 | about 8 to 10 min each | 12AN Lane A: 6.5 min for 641 points with 259 events |
| summary | HENON CPU | about 5 min | |

**Lanes** (one process per entry; a resubmitted lane skips finished entries):
- `v2` on rita (A100-80; `-p RITA-GPU --qos rita -A phy220048p --gres=gpu:a100-80:1 --cpus-per-task=128 --mem=120G
  --time=7-00:00:00`): E_A, E_B, E_C, E_D, E_D2, A, B, C, D, D2, F, F2, G0, G0_2, G, G2: about 1 to 1.5 card-hours.
  v2's kernel build is not chunked by core at these sizes (rows × slots below 2^25), so it needs host and device memory
  of about 25 GB: an 80 GB card.
- `phase12` on rita (same flags): E_I, I_0245, I_030: about 0.3 to 0.5 card-hours.
- `union_asis` on twig (`-p TWIG-GPU --qos twig -A phy220048p --gres=gpu:a100-40:1 --cpus-per-task=32 --mem=120G
  --time=2-00:00:00`, twig's partition maximum): E_HbS, E_HD, E_HD2, H_asis_bS, H_asis_D, H_asis_D2: about 0.8 to
  1.5 card-hours.
- `union_fixed` on twig (same flags), after the union rebuild: H_fix_bS, H_fix_D, H_fix_D2: about 0.8 to 1.5
  card-hours.
- Device memory of a union entry is estimated at about 20 to 25 GB (two kernel states of the compact union, 196,608
  rows × 774 slots, five float64 arrays each; the catalog; the PE and selection blocks); it was not measured (a CPU
  run would exceed this node's limit). If a union entry runs out of memory on a 40 GB card, its lane is resubmitted
  with the rita flags (the lane skips finished entries); that adds about 1 hour.
- HENON CPU jobs (`-p HENON --qos henon -A phy220048p --time=7-00:00:00 --exclude=henon06,henon08`): prep, union,
  summary.
- Dependencies are `afterany` everywhere (an entry whose inputs are missing fails at once and its lane goes on), so the
  summary always runs and always writes STATUS.json. Not used: MIKO (no job, no step; the holder is not touched),
  js2h100.

**In all, about 3 to 5 card-hours on four cards, and about 1.5 CPU-hours on HENON.**

**Estimated time to completion: about 2 to 2.5 hours from submission to the summary** (range 1.5 to 5 hours): prep
about 10 minutes with HENON's queue; the two rita lanes about 1 to 1.5 hours after it; the union rebuild about 45
minutes, then the fixed lane about 1 to 1.5 hours on twig; the summary about 5 minutes after the last lane. Longer if
twig's cards are held by other users or HENON queues. The 7-day and 2-day limits are ceilings, not the estimate.

**Submit command (prepared, not run; on the owner's go):**

```
bash /hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/repo_12AO/slurm/phase12ao_submit.sh <consumer commit>
```

It creates the clean worktree `paper_ladder/worktrees/<sha>/`, submits the seven jobs, writes `plans/jobs.json` and
prints the watcher for the main session (a shell until-loop on `slurm/phase12ao_watch_check.sh`, every 600 s; no agent
polls).

## Code (consumer branch `phase12ao/ladder`, worktree `phase12_5/repo_12AO`)

A worktree of the consumer repo (`repo_12AN`'s clone of `ignaciomagana/desi_darksirens_selection`), branch
`phase12ao/ladder` from cb7c638 (12AN's build). Local commits only; the main session pushes. Nothing in the earlier
records' scripts changes; Lane A runs `phase12ah_a_scan.py` unchanged.
- `scripts/phase12ao_common.py`: inputs and sha256, entries, transitions, lanes, grids, populations, metrics, guard;
- `scripts/phase12ao_scan.py`: one entry per process (and the lane loop), the in-job controls (settings, C3, G-T1,
  G-T2);
- `scripts/phase12ao_subset_events.py`: the exact event subsets;
- `scripts/phase12ao_radial_null.py`: step F's catalog;
- `scripts/phase12ao_build_loa_rebuild.py`: the paper's union build with paths as arguments;
- `scripts/phase12ao_pixelate.py`: the legacy store layout and the order-free comparison;
- `scripts/phase12ao_prep.py`, `scripts/phase12ao_union.py`: the CPU jobs;
- `scripts/phase12ao_summary.py`: every reported number, A0, withholding, the guard;
- `slurm/phase12ao_{prep,union,lane,summary}.sbatch`, `phase12ao_submit.sh`, `phase12ao_watch_check.sh`,
  `phase12ao_worktree.sh`;
- `tests/test_phase12ao.py`: CPU tests.

## Outputs

Under `phase12_5/paper_ladder/`: `inputs/` (subsets, radial null, `inputs.json`), `union_rebuild/` (the two flat
builds, U1's pixelation, the fixed store, `rebuild.json`), `runs/<entry>/` (`scan.npz` absolute; `entry.json`
location-free; Lane A's own files under `lane_a/` for I, absolute), `lanes/`, `summary/`, `plans/`, `logs/`,
`worktrees/`, `.cache/`. Printed progress carries no likelihood value.

## Known limits

- **The paper's event cut is not modelled.** The 21 and 44 were chosen by the support statistic S̄ (and its
  emulated pass probability is in beta_S); the all-sky selections (D, D2, H_D, H_D2, I) do not encode that choice. The
  pairing with spectral-only on the same events and selection keeps each step like for like, but neither member is
  the event-selection-consistent likelihood.
- **The subset's absolute H0 is not meaningful.** 21 or 44 events chosen for catalog support, with a fixed population,
  are not a population-level H0 measurement; only the differences between paired grids are read.
- **A and B keep the paper's cut PE** (cut at dL 1601.9 Mpc in the PE cosmology) with injections that are not cut;
  C removes the cut and nothing else.
- **G changes the pixel weights too** (core's per-row normalisation); G0 separates the two effects only up to the
  fill's departure from pure count weighting (at most about 2% per pixel).
- **G's fill extends to core's grid top (z 5)** and covers the whole sky above 0.30, empty pixels included.
- **H's leak fix removes only spectra up to z 0.5** (the z05 tables); a spectrum above 0.5 with a photo-z below 0.30
  would still leak. The fix can also change, for a few LS rows, which spectrum wins a positional match; the build
  counts are reported.
- **beta_S (44) was built on the as-is union's footprint**; H_fix_bS reuses it (the footprint moves by at most the few
  pixels the fix empties).
- **I's calibration is the 12AG ladder's at both depths**; it is not re-derived at 0.30. I also changes the population
  (Phase 12's GWTC-5 values against the paper's medians), Om0 (0.3089 against 0.3075), the guard and DARKSIRENS_ZMAX,
  as a bundle.
- **Fixed population everywhere**; the spectral channel's dependence on it (notes: per-draw medians spread by many
  widths) is common to each pair, not removed.
- **One event (GW200129_065458) was resampled with replacement upstream**; its PE variance is understated (12AJ).
- **CPU smoke ≠ GPU numerics bit for bit**; the GPU grids are the record's.

## Decisions for the owner before launch

1. **Launch** (all approved cards: two rita, two twig; HENON for CPU): go or not.
2. **G's definition.** As declared (core's conditional rows with a global fill, plus G0 to separate the pixel
   weighting), or add a consumer-side G′ that keeps C's equal pixel weights (a fill at each pixel's own density; not a
   core option, a patched density as in 12AL). Default: as declared, no G′.
3. **Step I's cell.** Declared at the owner's proposed fiducial (nside 128, sigma_kde 1e-3) with the 12AG calibration
   (delta 0). The alternative is sigma_kde 3e-3, the paper's kernel width, to make H→I change one thing less.
4. **H_fix needs U0 and U1.** If either fails, H_fix is withheld and the owner decides.
5. **Merges and pushes** are the owner's and the main session's: this record and the consumer branch are local commits.

## Amendment B1 (build stage and CPU smoke), 2026-10-21, before any 12AO job

Written before any submission. Nothing here was read from an absolute file; every number is a control value, a time,
a memory figure, a count, or a location-free plumbing number.

### B1.1 What was built

Consumer branch `phase12ao/ladder` in the worktree `phase12_5/repo_12AO`, head **6cc7ae8** (f6100fc, the build, from
cb7c638; then 6cc7ae8, the smoke script only), the files listed under "Code", 13 CPU tests (`tests/test_phase12ao.py`,
all pass). Production runs from a clean worktree of the
submitted commit (`paper_ladder/worktrees/<sha>/`).

### B1.2 Build checks on real inputs (scratch outputs; not the production files)

- **Event subsets.** Two of the 21 (GW200202_154313, GW240413_022019) from the trusted 259-event file: every dataset
  block bitwise equal to the source's, per-event attributes the kept entries, the gwcat event-set attributes
  recomputed; 15 s, 0.13 GB. The same two from the paper's gwcat-1.0 file (minimal mode, for A's smoke): bitwise.
  Core loads both.
- **The radial null on the real v2 store** (seed 20261020): counts, widths, weights and padding bitwise unchanged; the
  redshift multiset bitwise unchanged; reproduces bitwise from the seed; 2,126,567 galaxies, all but one in about two
  million change redshift; 8 s, 1.9 GB.
- **The pixelator against a real legacy store.** Pixelating v2's own flat input (`v2/pixelate_input.h5`) reproduces
  the paper's v2 store exactly per pixel (68,309 occupied pixels, 2,126,567 galaxies, at most 145 per pixel; no pixel
  differs). This is U1's check on the smaller catalog; U1 itself (the union) runs in the HENON job.
- **The build copy.** The test checks that every line of the paper's `build_loa_rebuild.py` is in the copy except the
  five output and match-file lines, and that every added line is marked or is the new path handling.

### B1.3 The CPU smoke (two events, the 13 smoke points; plumbing, not results)

`slurm/phase12ao_cpu_smoke.sh` on this node: JAX on CPU, 8 cores, niced; the two events above (A and E_A from the
paper's file; C, F, G0, G, E_C, E_D, E_D2 from the trusted file; E_HbS and E_I on the same two events as stand-ins for
the 44). Run twice: once on the working tree during the build, then in full from commit f6100fc (29 minutes, every
process at or below 5.0 GB); the second run's ln L, ln mu, N_eff and per-event ln Z equal the first's bitwise for every
entry they share, and its G-T1 passes the amended tolerance. Its summary ran after 6cc7ae8's inputs record (F's
checks): every smoke entry reported, none withheld, no guard violation.

- **C3:** the diagnostics' total equals the binding's ln L exactly (|Δ| = 0) at 50, 75 and 100, in every entry.
- **The settings table:** no departure in A, C, F, G0, G, E_A, E_C, E_D, E_D2, E_HbS. E_I records Phase 12's settings
  (DARKSIRENS_ZMAX 6.0, 1,086 grid nodes, Om0 0.3089, variance limit 20 with the soft guard).
- **A0 on two events** (against the shipped `components.h5`, 13 nodes, constant removed): the likelihood rebuilt from
  the shipped components, max |Δ ln L| = 2.8e-5 nat; each event's ln Z 3.4e-7 and 2.9e-5; ln mu 1.0e-6; N_eff 3.2e-6
  relative; no finiteness mismatch. A reproduces the pin's components for these events well inside 0.02 nat. (The full
  A0 against `h0_scan.csv` needs all 21 events: production.)
- **G's fill density:** log10 n0 = −2.5999 (h³ Mpc⁻³): 2,126,567 galaxies in 68,309 occupied pixels, 31.1 per pixel,
  below z 0.30.
- **G-T2 passes** at 50, 75 and 100 on 3,300 rows (300 empty): the missing density is exactly zero at all 147 grid
  nodes up to 0.30; C_sel is exactly 1.0 there; below the edge log p_G − log p_C − (log N_obs − log Z_G) is at most
  3.0e-13; zero sets agree; empty rows are zero; above the edge p_G is the fill alone (8.9e-16) and the fill is
  n0 a_pix dV_c/dz exactly. The catalog's mass fraction per pixel, N_obs / (N_obs + N_miss), runs from 1.2e-4 to 9.9e-3
  (p50 3.6e-3): below 0.30 the pixels are weighted by their galaxy count to within 1% (N_obs / N_miss), which bounds
  G0's departure from the pixel weighting G implies.
- **G-T1, amended.** Measured: |Δ ln L| 7.8e-4 to 1.1e-3 nat, |Δ ln mu| 3.9e-4 to 5.4e-4, each event's ln Z at most
  7.3e-6. The declared tolerances (1e-5 and 1e-6) came from a wrong estimate of the interpolation difference between
  the fill (linear between grid nodes, no z² law below the first node) and core's volume prior (log-linear), which
  the injections in empty pixels carry into ln mu. Amended before any job to |Δ ln mu| <= 2e-3, each event's
  |Δ ln Z| <= 1e-4, |Δ ln L| <= N (1e-4 + 2e-3) (code: `G_T1_TOL`). G-T1 is a mark; G is gated by G-T2.
- **Memory and the row chunks.** Core builds the complete catalog's kernels without chunking when rows × slots is
  below 2^25 (v2's compact view: 152,147 × 145). The first C smoke ran that way and reached 25 GB of resident memory
  for about four minutes (above this node's 8 GB guidance; no harm, the holder's limit is 250 GB). The smoke then
  lowered core's chunk threshold to 0 (`--row-chunk-threshold 0`, a layout option: the same row-local arithmetic in
  512-row chunks): C's ln L, ln mu, N_eff and every event's ln Z are bitwise equal to the unchunked run, at 2.7 GB.
  Production keeps core's default on the 80 GB card (rita); every smoke process after that stayed at or below 5 GB.
- **Timings** (p50 seconds per point, 8 CPU cores): spectral pairs 0.08; v2 complete 13 to 16 (A 13.2, C 13.0, F 15.1,
  G0 16.0); G 22.3. Resident memory: spectral 0.8 to 1.0 GB; complete 2.7 to 2.9 GB; G 4.8 GB.
- **The summary** runs on the smoke's outputs, writes `summary.json`, `controls.json` and `STATUS.json` through the
  location guard, and fills the transitions it has (C→F, C→G0, G0→G, C→G). On two events and a 10-unit grid these
  numbers test the plumbing only and are not reported as results.
- **The lane loop** runs each entry in its own process with its own DARKSIRENS_ZMAX (unset for the paper line even
  when the parent sets 6.0), records each rc, and an entry whose produced inputs are missing fails at once (E_C before
  prep) while the lane goes on.
- **Not smoked:** the H entries (the union complete catalog on CPU would exceed the node's memory guidance), Lane A
  for I (12AH's script, unchanged, which 12AN ran at this cell on GPU), the HENON prep and union jobs (their parts are
  tested above: the subset tool, the radial-null builder and the pixelator on real data; the build copy line by line).

### B1.4 Ready to launch

Nothing is submitted. On the owner's go:

```
bash /hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/repo_12AO/slurm/phase12ao_submit.sh 6cc7ae8
```

(or the branch's later head, if the owner's decisions change the code). The estimate stands: about 3 to 5
card-hours and about 1.5 HENON CPU-hours; about 2 to 2.5 hours from submission to the summary (range 1.5 to 5).

## Amendment B2 (step I rerun), 2026-10-21, before the summary

Lane `phase12` (job 1391027, consumer 6cc7ae8) ran E_I to completion, then both I entries stopped at argument parsing
(rc 2, before any computation): `phase12ao_scan.py` called `phase12ah_a_scan.py` without the 12AG parser's `scan`
subcommand. Consumer b0e9f03 adds it (one token; the rest of the argv unchanged; parse checked on CPU). The lane was
resubmitted alone (job 1391032, rita A100-80, worktree `paper_ladder/worktrees/b0e9f039197c`); E_I's DONE was kept, so
only I_0245 and I_030 ran; the summary job's dependency was extended to it. Nothing else changed.

## Results (2026-10-21; location-free)

Jobs: prep 1391024, union 1391025, lanes v2 1391026, phase12 1391027 + 1391032 (B2), union_asis 1391028, union_fixed
1391029, summary 1391030; all COMPLETED, every entry rc 0. STATUS: 28 entries present, 19 reported, no guard
violation, nothing withheld. Every grid is the coarse one (the window rule did not hold for every pair).

**Controls.** A0: A reproduces the paper's shipped scan, max |Δ ln L| 4.6e-5 nat after a constant, no finiteness
mismatch (per-event ln Z within 2.4e-5, ln mu 1.0e-6, N_eff 3.2e-6 relative). Settings table: 0 mismatches. C3 ok on
every entry. G-T2 ok. **G-T1 (mark) misses its tolerance on G and G2**: per-event |Δ ln Z| up to 4.5e-3 (tolerance
1e-4) on both; |Δ ln mu| up to 5e-4 on G (within 2e-3) and 0.016 to 0.040 on G2 (outside); |Δ ln L| 0.007 to 0.010 on
G, 0.32 to 0.83 on G2 at the three control points. U0 and U1: the branch's build reproduces the paper's as-is union
exactly (22,787,835 rows, every column; every pixel); the leak-fixed union has 22,269,369 rows (518,466 fewer).

**Per entry against its spectral pair** (R = catalog over spectral-only; shift in spectral sd; H = Hellinger; V_tot =
ln L MC variance, maximum over the entry's own central 90%, nats; the pair's V_tot in brackets):

| entry | pair | R68 | R90 | sd ratio | shift | H | V_tot |
|---|---|---|---|---|---|---|---|
| A | E_A | 0.775 | 0.689 | 0.717 | −0.12 | 0.25 | 0.41 (0.03) |
| B | E_B | 0.771 | 0.687 | 0.715 | −0.11 | 0.25 | 0.40 (0.03) |
| C | E_C | 0.785 | 0.751 | 0.756 | −0.22 | 0.22 | 0.53 (0.04) |
| D | E_D | 0.557 | 0.593 | 0.584 | +2.61 | 0.82 | 0.33 (0.01) |
| D2 | E_D2 | 0.595 | 0.581 | 0.595 | +2.73 | 0.82 | 0.49 (0.01) |
| F | E_C | 0.594 | 0.690 | 0.661 | +0.06 | 0.25 | 0.36 (0.04) |
| F2 | E_D2 | 0.537 | 0.582 | 0.570 | +2.44 | 0.82 | 0.41 (0.01) |
| G0 | E_C | 0.790 | 0.780 | 0.763 | −0.34 | 0.23 | 0.48 (0.04) |
| G0_2 | E_D2 | 0.530 | 0.563 | 0.552 | +2.75 | 0.83 | 0.47 (0.01) |
| G | E_C | 1.278 | 1.142 | 1.201 | +0.05 | 0.19 | 0.49 (0.04) |
| G2 | E_D2 | (0.068) | (0.079) | (0.087) | (−1.32) | 0.80 | 0.64 (0.01) |
| H_asis_bS | E_HbS | 0.843 | 0.802 | 0.814 | −0.43 | 0.18 | 0.23 (0.09) |
| H_fix_bS | E_HbS | 0.816 | 0.784 | 0.801 | −0.47 | 0.20 | 0.24 (0.09) |
| H_asis_D | E_HD | 0.626 | 0.641 | 0.642 | +3.76 | 0.95 | 0.21 (0.03) |
| H_fix_D | E_HD | 0.628 | 0.643 | 0.642 | +3.70 | 0.94 | 0.22 (0.03) |
| H_asis_D2 | E_HD2 | 0.648 | 0.643 | 0.651 | +3.76 | 0.95 | 0.31 (0.03) |
| H_fix_D2 | E_HD2 | 0.650 | 0.643 | 0.650 | +3.69 | 0.94 | 0.32 (0.03) |
| I_0245 | E_I | 0.812 | 0.898 | 0.865 | −0.01 | 0.13 | 0.17 (0.04) |
| I_030 | E_I | 0.768 | 0.865 | 0.823 | −0.06 | 0.15 | 0.16 (0.04) |

**Two readings the summary numbers do not carry by themselves (main session, from the owner-only curves; no
location written):**
- **G2 is not a width.** Its ln L is monotone over the whole grid (about 23 nats end to end) and its posterior piles
  against one edge of the grid; R and shift above are those of a truncated posterior (bracketed). G-T1 also misses on
  G2 by 0.3 to 0.8 nat. G2 is reported, not read.
- **The 21-event spectral pairs under all-sky selection (E_D, E_D2) are bounded by one grid edge**: their ln L is flat
  within 0.1 nat over about a third of the grid. Their medians and sd depend on the grid's bound, so the shifts of D,
  D2, F2 and G0_2 (in E_D2's sd) are measured against a prior-bounded reference; the catalog curves themselves are
  not edge-bounded (they fall by about 23 nats toward that edge). The 44-event pairs (E_HD, E_HD2, E_I) and the
  beta_S pairs fall on both sides inside the grid.

**Per transition** (shift in the destination's spectral sd; ΔR68, ΔR90; H between the two posteriors):

| from → to | change | shift | ΔR68 | ΔR90 | H |
|---|---|---|---|---|---|
| A → B | exact mass normaliser | +0.01 | −0.004 | −0.001 | 0.004 |
| B → C | trusted uncut PE | −0.23 | +0.013 | +0.064 | 0.13 |
| C → D | beta_S → paper all-sky | +1.38 | −0.228 | −0.158 | 0.62 |
| C → D2 | beta_S → trusted all-sky | +1.46 | −0.190 | −0.170 | 0.61 |
| D → D2 | all-sky: paper → trusted | +0.08 | +0.038 | −0.012 | 0.09 |
| C → F | radial null (beta_S) | +0.28 | −0.191 | −0.062 | 0.24 |
| D2 → F2 | radial null (all-sky) | −0.28 | −0.058 | +0.001 | 0.19 |
| C → G0 | pixel weights by count | −0.11 | +0.005 | +0.029 | 0.08 |
| G0 → G | soft edge (beta_S) | +0.38 | +0.488 | +0.362 | 0.29 |
| D2 → G0_2 | pixel weights (all-sky) | +0.02 | −0.065 | −0.018 | 0.07 |
| G0_2 → G2 | soft edge (all-sky) | (−4.06) | (−0.463) | (−0.484) | 1.00 |
| H_asis → H_fix (bS / D / D2) | spectra leak fixed | −0.05 / −0.06 / −0.07 | −0.027 / +0.002 / +0.002 | −0.018 / +0.003 / −0.000 | 0.02 / 0.03 / 0.04 |
| H_asis_bS → H_asis_D | union: beta_S → all-sky | +2.37 | −0.218 | −0.161 | 0.81 |
| H_asis_D2 → I_0245 | Phase 12's treatment (bundle) | −3.84 | +0.164 | +0.255 | 0.97 |
| I_0245 → I_030 | depth 0.245 → 0.30 | −0.05 | −0.044 | −0.033 | 0.03 |

**ln L_cat − ln L_spec over the window (mean removed; peak-to-peak, nats):** total / PE part / selection part: C 1.5 /
8.5 / 8.2; G0 1.9 / 8.0 / 7.0; G 1.8 / 1.9 / 2.3; F 2.8 / 7.5 / 6.0; D2 12.0 / 8.5 / 19.7; G0_2 12.0 / 8.0 / 19.2; F2
13.1 / 7.5 / 19.3; G2 3.8 / 1.9 / 5.2; I_0245 2.1 / 2.3 / 0.5.

**What the numbers say, and no more.**
1. Core reproduces the paper's likelihood (A0 4.6e-5 nat). The mass normaliser moves nothing; the uncut PE moves the
   result by −0.23 spectral sd and widens R90 by 0.06.
2. The selection is the largest single step on the paper's catalog: beta_S → all-sky moves the catalog posterior by
   +1.4 to +1.5 spectral sd (H 0.61 to 0.62); with all-sky selection the catalog posterior sits +2.6 to +2.7 E_D2 sd
   from spectral-only (against a prior-bounded reference, above), and +3.7 to +3.8 sd on the union's 44.
3. The paper-mode catalog's width and location survive the radial null (F: R68 0.59, R90 0.69; F2: R 0.54 to 0.58,
   F2 within 0.3 sd of D2): in complete mode with the hard edge, galaxy redshift structure carries little of it.
4. The soft edge removes it under beta_S (G: R 1.14 to 1.28, catalog wider than spectral-only, shift +0.05), and it
   removes most of both the PE and the selection parts of ln L_cat − ln L_spec (C 8.5 / 8.2 → G 1.9 / 2.3 nats ptp).
   Under all-sky selection the soft edge gives the edge-bounded G2 (not read).
5. The catalog-construction changes tested move little: pixel weights by count H 0.07 to 0.08; the spectra-leak fix
   at most 0.07 sd and 0.03 in R; depth 0.245 → 0.30 0.05 sd.
6. Phase 12's treatment on the 44 (I) sits at −0.01 to −0.06 spectral sd from its spectral pair, R68 0.77 to 0.81,
   R90 0.87 to 0.90, ln L_cat − ln L_spec 2.1 nats ptp over the window, of which 0.5 from the selection part.
7. Not tested here: the v2 (volume-limited Kibo x BGS) catalog against the union on the same events (A to G use the
   21 on v2, H and I the 44 on the union); the paper's event cut in the all-sky selections (known limits).

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
sha256, in `config/record_envs/12AO.json`; `scripts/check_frozen_environment.py --record 12AO` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AO/<sha7>` on
GitHub (f6100fc, 6cc7ae8, b0e9f03). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON);
it was green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main
(above).

**Population of the spectral-only grids (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** The spectral-only grids gave the population as an explicit mapping at the corrected pair (0.04, 0.10). From
the consolidated main of PR #20 they evaluated the same values but recorded a `population.fixed_values` record (the
declaration written over equal entries); after the follow-up (PR #21) they resolve and record exactly what they did
when they ran (no `fixed_values` record; checked on the 12AG spectral reference at three H0 points: ln L difference
0).

**Input (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).** The declared input `phase12_config`
(sha256 b79ad777...) now names `config/desi.fixed_population.core_preset.json`, the file this record ran with, and
step I reads it through the sha256 check (it read `config/desi.fixed_population.json` unchecked before). The
configuration step I resolves is unchanged (the 12AG overrides set the spin pair).

**Run fingerprints (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).** The code digests that the
12AG to 12AQ drivers put into their run fingerprints cover the consumer code, so a run stored before the consolidation
(or its follow-up) is evaluated again rather than resumed when it is rerun from main; the values it computes are the
same.

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

**Writer commit (consumer PR #29, merge 0989df4; finding G4.10).** The summaries behind this record did not carry the
commit of the code that wrote them (the commit is in the job logs and the record). From the merge each summary carries
a `writer` block: the writing script, its checkout's commit, branch and changed-file count, and, where it reads a
short list of files, their sha256. The stored summaries are unchanged; a summary rewritten from main carries the
block.

**Operations (consumer PR #30, merge 6d0f800; finding C139).** The build-stage CPU smoke (amendment B1) ran on the
holder's CPUs with no memory check; its first C smoke held 25 GB resident there. From the merge
slurm/phase12ao_cpu_smoke.sh is a HENON CPU job (the job's cgroup caps it) and refuses to run outside a Slurm job or
inside the holder. The smoke's results are unchanged.
