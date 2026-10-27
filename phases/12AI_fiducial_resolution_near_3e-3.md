# 12AI — Fiducial resolution near sigma_kde 3e-3: a convergence scan at nside 64 and 128

## Status

**RESULTS (2026-10-19, 11:02 UTC):** see "Results" at the end: fiducial candidate sigma_kde 3.5e-3 by the declared rule, with observations. **DECLARED (owner approval, 2026-10-19 about 11:00 UTC), before any 12AI grid.** No 12AI likelihood has been
evaluated. This record fixes the cells, the inputs, the criteria and the readings before anything runs.

**Blinding: location-free**, as in 12AG and 12AH. No H0 value appears here, in commit messages or in PR text. The
only H0 values in this record are fixed a priori: the grid [20, 140] at step 0.5, and the window [50, 90].

## Why

The 12AG ladder moved the width ratio R from 0.94 to 1.19 across nside × sigma_kde. When the owner looked at the
posteriors, two things stood out:

- **Small kernels are spiky.** At sigma_kde ≤ 1e-3 the catalog log-likelihood is rough point to point: 0.1 to 1.3
  nat, against 0.01 for spectral only. The spikes are about one grid step wide.
- **3e-3 is smooth but not converged in nside.** At sigma_kde 3e-3 every nside is smooth (0.05 to 0.07 nat). The
  catalog sharpens the main peak and adds structure on its high side. But nside 64 → 128 changes the posterior by a
  Hellinger distance of 0.053, most of the catalog's whole effect at nside 64 (0.064 from spectral only).

The owner asked for:
- more scans at nside 64 and 128 near sigma_kde 3e-3;
- a convergence criterion, stated and applied to the existing table before any run;
- tolerances: "Looser distance" (Hellinger ≤ 0.05);
- scope: "Grids only first" (half-sample runs later).

## Cells

The sigma_kde chain at nside 64 and at nside 128 is:

1.5e-3, 2e-3, 2.5e-3, **3e-3**, 3.5e-3, 4e-3, 5e-3, 7e-3, **1e-2**

- **Reused:** the bold values are 12AG's grids.
- **New:** the other seven at each nside, so 14 new grids.
- **Context only:** 12AG's 1e-3 cells are reported but are not on the chain.

Everything else is 12AG's ladder setting, unchanged:
- **Grid:** the 241-point exact grid [20, 140] at step 0.5.
- **Calibration:** log10 n0 −1.8216, M0hat −20.4975, sigma_M 0.5592, delta 0.
- **Model:** the population fixed as in the spectral-only reference; the selection guard (soft, variance limit 20);
  core e7c3007.

**Inputs** (sha256 prefix):

| Input | sha256 |
|---|---|
| catalog, nside 64 (production file) | c2d1ff36567419e4 |
| catalog, nside 128 (12AG build) | f26a20f0f3f8ca5a |
| footprint (nside 128) | 1e4e5c675dd59ab2 |
| PE (259 events × 4096) | c61507251609cb69 |
| injections | 56e51af209c99905 |

**Driver.** Each grid runs with `phase12ah_a_scan.py`. That is 12AG's grid driver plus each event's log evidence
(`events.npz`), so the per-event comparison of nside 64 and 128 needs no rerun.

## Convergence criteria (fixed now)

**Per cell, "can we trust this grid":**

- **N1:** the maximum total Monte-Carlo variance (PE plus selection) inside the cell's 90% interval is ≤ 1.2.
  Spectral only is 0.91, so the catalog may add at most about 0.3. LVK's cap is 1.0, and the owner chose 1.2.
- **N2:** roughness ≤ 0.1 nat. Roughness is the rms of the point-to-point second difference of ln L(catalog) − ln
  L(spectral only), over H0 in [50, 90].
- **N3:** half-sample stability. Deferred to a later amendment at the owner's request.

**Between neighbours that both pass N1 and N2, "the setting no longer matters":**

- **C1:** the Hellinger distance between the two posteriors is ≤ 0.05. For Gaussians that is a shift of 0.14
  spectral sd or a 10% width change.
- **Neighbours:**
  - consecutive sigma_kde on the chain at one nside;
  - nside 64 against 128 at one sigma_kde.

**Readings:**

1. **Per nside:** the C1 verdict for every consecutive pair of passing cells.
2. **Per sigma_kde:** "nside-converged" when 64 against 128 passes C1.
3. **Fiducial candidate:** the smallest sigma_kde on the chain where all of these hold:
   - both nsides pass N1 and N2;
   - 64 against 128 passes C1;
   - at both nsides, the pair (this sigma_kde, the next larger) passes C1.

   If no sigma_kde qualifies, the reading is "none within tolerance".
4. **Until N3 runs**, a C1 failure is not attributed either to Monte-Carlo noise or to a real resolution dependence.

Also reported for every cell: R, the sd ratio, Delta in spectral sd, and the Hellinger distance from spectral only
(the size of the catalog's effect). The per-event sum (Σ ln Z_i + core's selection correction = ln L, to 1e-9) is
checked on every new cell.

### The existing table under these criteria (before any 12AI run)

| Cell | Max total MC variance in 90% | Roughness (nat) | Passes N1 and N2 | Hellinger from spectral |
|---|---|---|---|---|
| (64, 1e-3) | 1.12 | 0.17 | no (N2) | 0.122 |
| (64, 3e-3) | 1.02 | 0.05 | yes | 0.064 |
| (64, 1e-2) | 0.96 | 0.05 | yes | 0.029 |
| (128, 1e-3) | 1.38 | 0.24 | no | 0.139 |
| (128, 3e-3) | 1.13 | 0.06 | yes | 0.098 |
| (128, 1e-2) | 1.00 | 0.05 | yes | 0.020 |

**C1 on the existing pairs:**

| Pair | Hellinger | C1 |
|---|---|---|
| 64 against 128, at 3e-3 | 0.053 | fails |
| 64 against 128, at 1e-2 | 0.017 | passes |
| nside 64, 3e-3 against 1e-2 | 0.062 | fails |
| nside 128, 3e-3 against 1e-2 | 0.094 | fails |

The 1e-2 column converges in nside, but the catalog does little there. With the existing cells, no fiducial
candidate qualifies.

## Compute

Fourteen grids, one nside-128 and one nside-64 grid per lane, on seven lanes:
- rita0 and rita1 (A100-80);
- twig0 to twig3 (A100-40);
- the free henon-gpu card (A100-40).

nside 128 peaked at 25 GB on twig in 12AG.

Every job requests its partition's maximum time. The summary runs on HENON CPU after all lanes (afterany) and
always writes `summary/STATUS.json`.

**Estimate:** about 10 to 15 minutes from submission if the cards are free, and about 20 minutes with the summary.

**Code:** consumer branch `phase12ai/fiducial-near-3e-3`, from 12AH's bf57e31:
- `scripts/phase12ai_plan.py`
- `scripts/phase12ai_summary.py`
- `slurm/phase12ai_*`
- `tests/test_phase12ai.py`

The commit that runs is 9827e3c (pushed before submission).

**Outputs:** under `phase12_5/fiducial_resolution/`:
- `runs/<cell>/` (scan.json and events.npz, not for agents);
- `summary/summary.json` (location-free);
- `summary/absolute.npz` (not for agents).

## Results (2026-10-19, 11:02 UTC; location-free)

**Runs.** Jobs 1390279–1390286 from 9827e3c all COMPLETED, in 7–8 minutes per lane. The per-event sum passes on all
14 new cells.

| sigma_kde | R (64) | R (128) | Delta (64) | Delta (128) | MC90 (64 / 128) | roughness (64 / 128) | Hellinger from spectral (64 / 128) | Hellinger 64 vs 128 |
|---|---|---|---|---|---|---|---|---|
| 1e-3 (context) | 1.024 | 1.153 | +0.02 | −0.00 | 1.12 / 1.38 | 0.17 / 0.24 | 0.122 / 0.139 | — |
| 1.5e-3 | 1.042 | 1.171 | +0.01 | −0.02 | 1.07 / 1.26 | 0.10 / 0.13 | 0.105 / 0.129 | 0.065 (not compared) |
| 2e-3 | 1.050 | 1.179 | +0.01 | −0.04 | 1.05 / 1.19 | 0.07 / 0.09 | 0.090 / 0.121 | 0.061 ✗ |
| 2.5e-3 | 1.051 | 1.169 | +0.00 | −0.06 | 1.03 / 1.16 | 0.06 / 0.07 | 0.077 / 0.110 | 0.057 ✗ |
| 3e-3 | 1.048 | 1.147 | +0.00 | −0.07 | 1.02 / 1.13 | 0.05 / 0.06 | 0.064 / 0.098 | 0.053 ✗ |
| **3.5e-3** | 1.044 | 1.120 | +0.01 | −0.07 | 1.01 / 1.11 | 0.05 / 0.06 | 0.054 / 0.085 | **0.049 ✓** |
| 4e-3 | 1.039 | 1.095 | +0.01 | −0.07 | 1.00 / 1.09 | 0.05 / 0.05 | 0.045 / 0.073 | 0.046 ✓ |
| 5e-3 | 1.029 | 1.056 | +0.03 | −0.06 | 0.99 / 1.06 | 0.05 / 0.05 | 0.034 / 0.052 | 0.039 ✓ |
| 7e-3 | 1.010 | 1.016 | +0.06 | −0.01 | 0.97 / 1.03 | 0.05 / 0.05 | 0.025 / 0.027 | 0.028 ✓ |
| 1e-2 | 0.990 | 0.992 | +0.08 | +0.03 | 0.96 / 1.00 | 0.05 / 0.05 | 0.029 / 0.020 | 0.017 ✓ |

**N1 and N2.** Every chain cell passes N1 and N2 except sigma_kde 1.5e-3:
- nside 64 fails N2 (roughness 0.101);
- nside 128 fails N1 (1.26) and N2 (0.134).

**C1 along the chain.** At both nsides every consecutive pair of passing cells passes, with Hellinger 0.010–0.028.

**Reading: fiducial candidate sigma_kde 3.5e-3**, by the declared rule:
- nside 64 vs 128 gives Hellinger 0.049, within 0.05;
- the step to 4e-3 gives 0.010 (64) and 0.013 (128).

### Observations (not readings; for the owner)

1. **A tolerance crossing, not a plateau.** The nside 64 vs 128 distance falls steadily as sigma_kde grows:
   0.061 → 0.017. The catalog's own effect, its Hellinger distance from spectral only, falls with it: 0.090 → 0.029
   at nside 64. At 3.5e-3 the 64 vs 128 difference (0.049) is still about as large as the catalog effect at nside 64
   (0.054). No sigma_kde on the chain leaves the catalog effect stable while nside stops mattering.
2. **C1 along the chain depends on the step size.** With fine steps the neighbouring distances stay small even
   while the result drifts from 2e-3 to 1e-2. The informative test is nside 64 vs 128.
3. **The chain is smooth above 2e-3.** Roughness reaches its plateau (about 0.05) by 2.5e-3. The 64 vs 128
   difference changes smoothly with sigma_kde. Both point to a systematic resolution effect rather than Monte-Carlo
   noise, but only N3 can decide that.
4. **What differs between the nsides.** nside 128 is wider (R up to 1.18 against 1.05) and sits slightly lower
   (Delta about −0.07 against 0). The per-event evidences are recorded at both nsides for every new cell, so a
   per-event attribution needs no rerun.

## Amendment 1 (2026-10-19, after the results): owner guidance; plan for the ln L convergence (nothing run)

**Status.** Everything in 12AG to 12AI is experimental, and is kept as a record.

**The owner's guidance** (suggestions, not fixed rules):

1. **The 0.5 grid is too coarse** to show the roughness, given that the posterior lies mostly in about H0 50–100.
   Future grids add a fine window, [50, 100] at step 0.1 (501 points), next to the coarse [20, 140] grid at step 0.5
   for the tails and normalisation. At nside 64 that is about 2.5 minutes per grid.
2. **The ln L variance criterion (N1) decides.** Roughness (N2) is supplemental and is reported only.
3. **Ways to improve the ln L convergence:**
   - more injections (the simplest for the current core);
   - surrogates for the PE samples or the injections (harder);
   - not using p_cat(z) in the selection (denominator) term where the injections are evaluated, and using the p_vol
     term instead.

**Where the variance comes from at the production cell** (nside 64, sigma_kde 3e-3; 12AG, at the point nearest the
median):
- **Selection, 0.74:**
  - 0.69 is the floor from the injections and the fixed population, the same as spectral-only;
  - 0.05 is added by the catalog.
- **PE, 0.21.**

At finer settings the catalog's added selection part grows: about 0.2 at (128, 1e-3) and 1.5 at (128, 1e-4). The PE
part grows to 0.3–0.5.

**Facts checked for the plan:**
- **Injections:** the selection file already holds every detected injection of the public O3 and O4 sets at the FAR
  < 1/yr threshold: 1,067,946 found of 944,412,448 draws. The floor (0.69) means an effective number of about 1e5.
  It falls as 1/N_inj.
- **PE samples:** they are capped at 4096 per event.
- **How core evaluates the selection term:** with the catalog sliced at each injection's pixel
  (`selection/gw.py: compute_selection_term`, `em_catalog_sel`).
- **The field weighting's normaliser:** it divides the host density by the survey-global total, which depends on
  H0. That normaliser cancels between the event evidences and −N ln mu only because both use the same density.

**Plan, in the order proposed to the owner:**
1. Measure first.
2. Then the selection-term variants D1–D3.
3. Then more injections or more PE samples.
4. Surrogates only if needed.

The owner decides each step; the reply to the owner gives the details.

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
sha256, in `config/record_envs/12AI.json`; `scripts/check_frozen_environment.py --record 12AI` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AI/<sha7>` on
GitHub (9827e3c). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was green at the
follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Population of the spectral-only grids (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** The spectral-only grids gave the population as an explicit mapping at the corrected pair (0.04, 0.10). From
the consolidated main of PR #20 they evaluated the same values but recorded a `population.fixed_values` record (the
declaration written over equal entries); after the follow-up (PR #21) they resolve and record exactly what they did
when they ran (no `fixed_values` record; checked on the 12AG spectral reference at three H0 points: ln L difference
0).

**Run fingerprints (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).** The code digests that the
12AG to 12AQ drivers put into their run fingerprints cover the consumer code, so a run stored before the consolidation
(or its follow-up) is evaluated again rather than resumed when it is rerun from main; the values it computes are the
same.

**The per-event sum (consumer PR #28, merge 8f8a7b2; finding C075).** The record checks every new cell's per-event
sum, and all 14 pass (largest |Delta ln L| 4.5e-13 against 1e-9). In the summary of record the result fed no reading,
no comparison and no exit code, so a failed sum would have left the fiducial reading unchanged. Since the merge a new
cell whose sum fails, or that has no `events.npz`, is withheld from every comparison and from the fiducial candidate,
and the summary exits 4. Also new with the merge, the summary exits 4 when any cell, 12AG's included, is not complete
(before it, an incomplete cell gave exit 0). *(Reworded 26 Oct 2026; see "Amendment (26 Oct 2026): independent review,
round 3".)* On the run of record nothing changes: re-run from the branch on the stored grids, the summary is the
recorded one with two added (empty) lists, the fiducial candidate is unchanged and the exit code is 0.

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

## Amendment (26 Oct 2026): independent review, round 3

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses below.
The amendment of 25 Oct 2026 above covers the fix packages merged first. This one covers five more, merged on 26 Oct
2026 after a third fix round and an independent check of each: the 12AQ readings and mock (consumer PR #32, merge
97ec978), the 12AO ladder (PR #27, merge ebb12ff), the GW inputs (PR #26, merge a152bed), the variance guard and
estimator noise (PR #33, merge 901bb54) and catalog version 2 (PR #24, merge 402c947). The consumer's main is now
402c947. `./ci.sh` passed on the merged tree in all three record environments (HENON, CPU;
`ci_logs/20261026T124516Z_133bc47f981f_<env>.log`: consumer_e7c3007_cuda12 1568 passed, consumer_e7c3007batch_cuda12
1577, consumer_1022429_lss57afebe_cuda12 1592; none failed). On 26 Oct 2026 the owner decided that catalog version 2
vetoes the bright-star masks, BRIGHT and MEDIUM (Legacy Survey maskbits 2050), not the large-galaxy bit, and that the
injections stay at the support gate for now (decision 4D; the replacement of the O3 campaign, 4A, is deferred and no
new injection product is made). Location-free throughout. Unless an item says otherwise, no number of record changes.
Still open and not amended here: resume markers and fingerprints (consumer PR #25) and the follow-ups of consumer PR
#35, among them the refusal of a delta outside its prior's bounds.

**Catalog model (consumer PR #24, merge 402c947; findings C020, C002, G2.4).** These grids fix the calibration at
log10 n0 = -1.8216 (12AB's baseline median, set almost entirely by the [0.02, 0.30] count ridge) and the luminosity
prior means; the in-depth ridge and the floor are discussed in 12AF's amendment of this date (C020, C002). Cells below
sigma_kde about 1e-3 are not physical host-redshift kernels (G2.4, see 12AG's amendment of this date).

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). No number of this record changes.

**Correction to the 25 Oct amendment (consumer PR #28, merge 8f8a7b2; finding C075).** The paragraph "The per-event
sum" said that the summary exits 4 on a failed per-event sum "(as it does for an incomplete cell)". Before consumer PR
#28 an incomplete cell gave exit 0 (the summary exited 3 only for a missing cell); exit 4 for an incomplete cell is
also new with that pull request, and it covers every cell, 12AG's included (`summary_rc` in
`scripts/phase12ai_summary.py`). The clause is reworded in place; nothing else changes.

## Amendment (27 Oct 2026): independent review, final round

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses
below. The amendments of 25 and 26 Oct 2026 above cover the fix packages merged first. This one covers the two that
were still open: resume markers and fingerprints (consumer PR #25, merge 498a147) and the review follow-ups
(consumer PR #35, merge d036f1e), which carry the owner's decisions of 26 Oct 2026 on a delta outside its prior's
bounds and on the manifests' spectral-only note. Both were merged on 27 Oct 2026, after further fix rounds and an
independent check of each. The consumer's main is now d036f1e. Its code is the tree that was tested, #25 and #35 on
main bdf5150 (consumer commit ab9e656): `./ci.sh` passed there in all three record environments (HENON, CPU;
`ci_logs/20261026T213714Z_ab9e6569b881_<env>.log`: consumer_e7c3007_cuda12 1644 passed,
consumer_e7c3007batch_cuda12 1653, consumer_1022429_lss57afebe_cuda12 1668; none failed), and so did the steps of
the GitHub contract job, run without JAX (`ci_logs/20261026T214140Z_ab9e6569b881_contract_job_nojax.log`: 1105
passed, none failed). Location-free throughout. Unless an item says otherwise, no number of record changes.

**Grid resume, DONE markers and the lane runner (consumer PR #25, merge 498a147; findings C023, C074, C077, C095).**
The grid driver's resume fingerprint left out the base configuration file, the package commits and the backend, the
lane runner skipped any entry whose DONE existed, the driver wrote DONE before 12AH Part A's events.npz, a `--set` of
catalog.sigma_kde would have been evaluated while scan.json recorded the `--sigma-kde` value, and a failing git was
recorded as commit '' with 0 changed files. None of this touched an output of record: all 58 grids of 12AG-12AI carry
one commit each, a clean tree and a DONE fingerprint equal to scan.json's; 0 of 215 completed scans resumed across
sessions; the base configuration's sha256 is unchanged since 8 Oct; no plan passes a `--set` of sigma_kde; every Lane
A DONE has its events.npz beside it, both spectral DONEs record equal grids and every branch DONE records passing
identities. Since the merge, the fingerprint holds the run identity (the resolved configuration, the commit and
tracked changes, the package commits and the backend), DONE is written last with its outputs' sha256, the lane runner
skips an entry only when its lane record holds the entry's argv, code and python and that python's core build and
backend (measured in a short probe process; the DONEs of record carry no lane record, so a resubmission into the
record's output root refuses those entries and leaves their outputs untouched), and the driver refuses a `--set` of
the keys its own flags set.

**Misspelt `--set` keys (consumer PR #25, merge 498a147; finding C088).** A misspelt `--set` key outside the sampler
block was accepted, ignored and shown in config.resolved.json. No record path carries one: every `--set` key of the
manifests in config/, of the 12AG and 12AH Part B plan builders and of the shell and Slurm scripts (slurm/,
scripts/*.sh) is a key of the base configuration of the driver it reaches or a key that driver reads (a test of the
consumer checks each of them, command by command). Since the merge, such a key is refused before anything runs.
