# Phase 12AC — P12.6: the 249 O3 and O4 events against the O3 and O4 injections (declaration)

## Status

**DONE (2026-10-18): results below, read robust.** Dropping the 10 O1/O2 events moves H0 by +0.11 sd (γ fixed) and −0.16 sd (γ free), width ratio 1.01 and 1.00; control 9.1e-13. The text that follows is the declaration as written before any run.

**DECLARED (owner, 2026-10-18), before any run.** Nothing in this record has
been run, and the 249-event file does not exist yet. The work is
fixed-population spectral-only grids on GPU, then a comparison on HENON CPU.
Results will be appended below.

This record quotes real-data H0 values, as the Phase 12 summary does. It is
not for the clean-room session.

## Where this sits

P12.6 is the robustness matrix of the Phase 12 result. This check is one row
of it: whether the H0 posterior depends on 10 events whose observing runs the
selection function does not describe. It changes no setting of the
baseline. The 259-event results stay the results of record.

## Why

**The events.** The PE file of every Phase 12 run
(`phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5`, sha256
c6150725…26dc) holds 259 events of 4096 samples each. The run is assigned
from the date in the event name: before 160120 is O1, before 170826 is O2,
before 200328 is O3, otherwise O4.

| run | events | first and last | median distance (Mpc) |
|---|---|---|---|
| O1 | 3 | GW150914 to GW151226 | 472 |
| O2 | 7 | GW170104 to GW170823 | 1074 |
| O3 | 59 | GW190408 to GW200316 | 1708 |
| O4 | 190 | GW230601 to GW250119 | 2503 |
| all | 259 | | |

The distance column is the median over the run's events of each event's
median luminosity distance. The names are sorted in the file, so the 10 O1
and O2 events are its first 10 events (rows 0 to 40,959).

**The injections.** The selection file
(`phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5`, sha256
56e51af2…49b6) holds two campaigns:

| campaign | source file | draws |
|---|---|---|
| O3 | `endo3_bbhpop-LIGO-T2100113-v12.hdf5` (end of O3) | 73,957,576 |
| O4a/b | `samples-rpo4ab-1366933504-55469568-clipped.hdf` (2023-04-30 to 2025-01-31) | 870,454,872 |
| total | | 944,412,448 |

1,067,946 injections are detected (FAR below 1 per year), and the observing
time is 2.5893 yr. There is no O1 or O2 campaign. Every O4 event lies
inside the O4a/b span (the GPS start and length in the file name).

These counts were read from the two files on 2026-10-18 (h5py, read-only,
with the consumer environment's Python).

**The mismatch.** In the spectral likelihood every event is divided by the
same detection fraction, computed from these injections. It describes the O3
and O4 detectors. The O1 and O2 events were found by less sensitive
detectors, and they are nearer: median distance 1.04 Gpc against 2.21 Gpc
for the O3 and O4 events. A detection fraction for all 259 events would be
the mixture of the four runs, weighted by their observing time. Here the O1
and O2 time is missing, so these 10 events are counted against a selection
deeper than the one that found them. They are 3.9% of the events.

## The owner decision

**As a systematic check, drop the 10 O1 and O2 events and rerun the
fixed-population spectral grids on the same O3 and O4 injections.** Event
set and injections then describe the same observing runs, at the cost of 10
events.

The alternative stays open: rebuild the selection from the LVK mixture
injection file that covers O1 to O4, and keep all 259 events. It is taken up
if this check moves the result much. Nothing else changes.

## What is run

### The 249-event PE file

**An exact subset of the 259-event file, not a rebuild.** The builder
(`gwcat export pe ... --seed 0 --nsamp 4096`, `phase12t/gwcat_exact/tools/build.sh`)
draws each event's 4096 samples from one random stream, consumed in event
order (`gwcat/export/pe_builder.py`, gwcat 8263ae9). The 10 dropped events
come first in that order. A rebuild from a 249-name list would therefore
redraw the samples of every remaining event, and the comparison would mix
the change of events with a change of samples.

The subset:

- the rows of the 249 O3 and O4 events (rows 40,960 onward, 249 × 4096 =
  1,019,904 rows), every column unchanged;
- the per-event attributes cut to the same 249 events; the event-count
  attributes (`nobs`, `n_allowed_names`) set to 249 and the name-list digests
  recomputed with gwcat's recipe; every other attribute copied;
- new attributes naming the parent file, its sha256 and the 10 dropped
  events;
- written to `o1o2_check/inputs/A_pe_chieff_bbh249_o3o4_n4096_v20_exact.h5`.

Checks on the file, before any grid:

1. every column equals the parent's rows 40,960 onward, bitwise;
2. the event names are the parent's minus the 10 O1 and O2 names, in the
   parent's order;
3. core's loader reads 249 events of 4096 samples, and its per-event
   reweighting ESS equals the parent's for the same events.

### The grids

The 259-event reference grids of the corrected spin, with one change: the PE
file.

| setting | 259-event reference | this check |
|---|---|---|
| PE file | 259 events, c6150725…26dc | the 249-event subset |
| selection file | O3 and O4a/b, 56e51af2…49b6 | same |
| population | `gwtc5_fiducial_bpl2peaks`, GWTC-5 fixed values, spin pair 0.04 and 0.10 | same |
| rate index γ | -2 to 6 in steps of 0.25 (33 values), plus 2.5439 | same |
| H0 | 20 to 140 in steps of 0.5 (241 points), flat prior; Om0 0.3089, w0 -1 | same |
| selection guard | soft selection-N_eff guard, likelihood variance cap 20 | same |
| code | `scripts/phase12t_stage.py spectral`, consumer ab226d6 (`phase12u/repo`), core e7c3007 with its defaults, env `consumer_e7c3007_cuda12` | same |
| driver | `phase12_5/spectral_gamma/gamma_grid_spin.py` | a copy with the PE path and the output directory changed |
| hardware | HENON CPU | rita GPU |

**34 grids with the 249-event file**, one per value of γ.

### The control

**One grid with the 259-event file at γ = 2.5439, on the same GPU**, compared
with the stored CPU grid at its 241 H0 points. It runs first. With the 34 grids
above, 35 grids in all.

1. **GPU against CPU:** max |d ln L| ≤ 1e-6 over the 241 points. If it fails,
   the GPU grids are not used and the 34 grids run on HENON CPU, as the
   reference did (about 1.5 hours on one 32-core task, under 20 minutes on
   six).
2. **The summary reproduces the reference:** applied to the stored 259-event
   grids, the comparison script gives the reference values below to 1e-3 in
   every median, interval end and sd.

## Where

- **Two rita GPU jobs:** partition RITA-GPU (two A100 80 GB), qos rita,
  account phy220048p, one GPU each, as the earlier rita jobs. The first runs
  the control, then 17 grids; the second the other 17.
- **One HENON comparison job** (CPU, account phy220048p), submitted with a
  dependency on both rita jobs. It writes the summary.
- If the grids run on another GPU instead (the Jetstream2 H100 or the GPU of
  the owner's miko job), the control grid runs first on that same GPU, and
  the outputs are copied back to the same directory.
- **Outputs:** `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/o1o2_check/`:
  `inputs/` (the subset and its checks), `runs/gamma_<+g.gggg>/spectral_h0.json`,
  `control/gamma_+2.5439/spectral_h0.json`, `logs/`, `summary.json`. Under 1 GB.
- **Compute:** a reference grid took 145 s on 32 CPU cores. On an A100 a grid
  is expected to take well under that after compilation, so the two jobs
  should finish within an hour. Not measured.

## The reference

The 259-event grids at the corrected spin
(`phase12_5/spectral_gamma/runs/gamma_<+g.gggg>/spectral_h0.json`). These
values were recomputed from the stored grids on 2026-10-18 and match the
stored summaries.

| | γ fixed at 2.5439 | γ free |
|---|---|---|
| H0 median [68%] | 66.17 [61.45, 71.15] | 67.95 [62.73, 73.45] |
| sd | 4.887 | 5.398 |
| γ | | 2.220 ± 0.342 |
| points penalised by the guard | 0 | 0 |

- γ free: flat prior on [-2, 6], trapezoid rule over the 33 grids without
  2.5439.
- H0 summaries: the posterior on the 0.5 grid; the median and the 68%
  interval (16% and 84%) from the interpolated CDF; the sd from the pdf.
- The smallest selection N_eff over the 34 grids is 28,331.

The 249-event results are summarized the same way.

## What is reported

With γ fixed at 2.5439 and with γ free, 249 against 259 events:

- the H0 median and 68% interval, and the sd;
- **Δ = (median_249 - median_259) / sd_259**, the shift in units of the
  259-event sd;
- **R = sd_249 / sd_259**, and the same ratio for the 68% interval widths;
- the γ posterior (mean and sd) with γ free, and its shift in units of the
  259-event γ sd;
- the guard summary: the number of penalised points over the 34 grids, the
  smallest selection N_eff, and the posterior mass on penalised points;
- the control's max |d ln L|, and the difference of its H0 median from the
  stored grid's.

## Reading bands (declared before any run)

| band | condition | reading |
|---|---|---|
| robust | \|Δ\| < 0.2 and 0.9 <= R <= 1.1 | the 10 O1 and O2 events do not matter at this precision |
| mild | 0.2 <= \|Δ\| < 0.5, or R in [0.8, 0.9) or (1.1, 1.25] | the event set is a systematic |
| material | \|Δ\| >= 0.5, or R < 0.8, or R > 1.25 | the selection mismatch matters |

- γ fixed and γ free are read separately. The check's reading is the more
  severe of the two.
- The γ shift is reported, not read.

## Expectations, not thresholds

- **Width:** with equal information per event, the posterior widens by
  sqrt(259/249) = 1.02. The O1 and O2 events are nearer, and a near event's
  small redshift gives its masses less leverage on H0, so R may be closer
  to 1.
- **Shift:** for Gaussian posteriors and equal information per event,
  removing any 10 of 259 consistent events moves the median by about
  sqrt(10/249) = 0.20 sd (rms). A shift near 0.2 sd is what the loss of 10
  events does by itself. Only a shift well above that points at the
  selection.
- **No direction is predicted.**

## What follows

- **robust:** recorded here and closed; the 259-event results stand.
- **mild:** listed as a systematic in the robustness matrix (P12.6), with
  Δ and R.
- **material:** the owner decides between the full-population chains with
  249 events and the selection rebuilt from the O1 to O4 mixture injection
  file.

## Not covered

- **The catalog target.** At a fixed population the DESI catalog result
  follows the spectral-only one: the galaxies move H0 by under 0.5 km/s/Mpc
  (12V, 12W), and the step-1 chain gives 67.6 against 67.9 without the
  catalog (12Y). It is not rerun here.
- **The full-population chains** (12AA). They are rerun only if the reading
  is material and the owner chooses them.
- **The mixture-file rebuild** of the selection.
- A calibration of Δ by dropping 10 randomly chosen O3 and O4 events instead.
  The expected scatter above stands in for it.

## Code

- The subset builder, the grid driver (a copy of `gamma_grid_spin.py` with
  the PE path and output directory changed, plus the control) and the
  comparison script, under `o1o2_check/`. The comparison is tested on the
  stored 259-event grids (control 2) before the jobs are submitted.
- No change to core, the consumer or gwcat.

## Not verified

- The GPU time per grid.
- That the selection guard stays unpenalised with 249 events. The selection
  variance term scales as N² / N_eff, so 249 events lower it by 8%; no change
  in the guard is expected.
- That core's loader takes the subset without a complaint about the cut
  per-event attributes.
- gwcat's own validation of the subset. The 259-event file passes it only
  with a spin-prior allow-list that is not approved; the Phase 12 runs use it
  by its sha256, and the subset is used the same way.

---

## Results (2026-10-18)

Rita jobs 1388969 (control, then 17 grids) and 1388970 (17 grids), both on A100-80, 20 minutes each; comparison HENON job
1388971. Output `phase12_5/o1o2_check/compare.json`.

- **Control:** the 259-event grid at γ = 2.5439 on the GPU equals the stored CPU grid to 9.1e-13 in ln L at all 241 H0
  values (declared tolerance 1e-6). Pass.
- **No grid point is penalised** by the selection guard, for either event set (smallest N_eff 28,331 at γ = −2, H0 = 140).

| | 259 events | 249 events (O3 and O4) | shift in 259-event sd | sd ratio | band |
|---|---|---|---|---|---|
| γ fixed at 2.5439 | 66.17 [61.45, 71.15], sd 4.89 | 66.71 [61.92, 71.75], sd 4.95 | +0.11 | 1.01 | robust |
| γ free (flat on [−2, 6]) | 67.95 [62.73, 73.45], sd 5.40 | 67.08 [61.86, 72.59], sd 5.41 | −0.16 | 1.00 | robust |
| γ (γ free) | 2.22 ± 0.34 | 2.45 ± 0.35 | +0.67 (γ sd) | 1.02 | not read |

**Reading: robust.** Dropping the 10 O1/O2 events moves H0 by 0.11 and 0.16 of its sd, below the 0.20 sd expected from
dropping any 10 of 259 events, and leaves the width unchanged. The rate index moves up by 0.23, toward the GWTC-5 value
2.54; it is reported, not read. As declared, the check is recorded and closed. The rebuild of the selection from the LVK
O1 to O4 mixture file stays a standing alternative, not triggered.

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
sha256, in `config/record_envs/12AC.json`; `scripts/check_frozen_environment.py --record 12AC` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AC/<sha7>` on
GitHub (ab226d6). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was green at the
follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Population of the spectral-only grids (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** The spectral-only grids gave the population as an explicit mapping at the corrected pair (0.04, 0.10). From
the consolidated main of PR #20 they evaluated the same values but recorded a `population.fixed_values` record (the
declaration written over equal entries); after the follow-up (PR #21) they resolve and record exactly what they did
when they ran (no `fixed_values` record; checked on the 12AG spectral reference at three H0 points: ln L difference
0).

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
