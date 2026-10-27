# Phase 12T — P12.4 on current core: reproduction, the n0 prior, exact GW priors (declaration)

## Status

**DECLARED (owner, 2026-10-03) before any run. RESULTS appended below
(2026-10-05).** The owner decides what follows and which run, if any, becomes
the result of record.

## Why

12S (H0 69.4 [64.1, 74.8], z_depth 0.245) left three questions open:

1. **The n0 prior.** The prior range of log10n0, [-2.0, -1.6], carries about
   ±2 km/s/Mpc of H0. In S2 the lower edge was not suppressed.
2. **The catalog's information.** The catalog moves the H0 median by +4.9
   against the spectral baseline (64.5), but the width is 1.07 times wider.
3. **The GW input.** It still carries gwcat's interpolated chi_eff and d_L
   priors. gwcat 8263ae9 (#24) evaluates them exactly.

Since 12S, core has moved from a935ef7 to e7c3007. The speed defaults are
now on:
- the one-pass pairing scale and the per-point pairing normaliser;
- the galaxy list and the gathered missing density;
- the kernel window at 1e-10.

Each one falls back silently where it does not apply.

## Owner decisions (2026-10-03)

- **Code.** Consumer branch `phase12t/core-repin`. It is based on
  `phase12q/catalog-recalibration` plus the 12S marginalized sampling in
  clean form, repinned to core e7c3007. Surveys, lss and lensing keep their
  pins unless core requires otherwise.
- **Compute.** ONE rita A100 job that runs every stage sequentially. The
  second A100 stays free. Output goes under
  `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12t/`.
- **Seeds.** One seed (22) per chain. Everything else is fixed as in 12S:
  - z_depth 0.245;
  - LF priors N(-20.500, 0.199) and N(0.558, 0.130);
  - the soft guard at cap 20;
  - dynesty nlive 1000, dlogz 0.1;
  - kernel pin off;
  - the fixed GWTC-5 population.

## Priors on (log10n0 [h-scaled], delta)

| Name | log10n0 | delta |
|---|---|---|
| 12S | U[-2.0, -1.6] | U[-3.0, 1.5] |
| flat_wide | U[-2.4, -1.2] | U[-3.0, 1.5] |
| count_ridge | N(a + b·delta, s), truncated to [-2.4, -1.2] | U[-3.0, 1.5] |

**count_ridge.** For each delta, the catalog's total count fixes n0.

- **The ridge.** For each delta, log10n0 is the value whose expected count
  over [0.02, 0.30] equals the observed count. It is computed from the
  binned expected counts of the calibration's forward fit (calibration_12q
  run 2). It reproduces:
  - the whole-window fit (-1.9065 at delta 1.047) to 0.001 dex;
  - restricted to z < 0.172, the cross-check fit (-1.7229 at delta -2.568)
    to 0.014 dex.
- **The linear form.** a = -1.815898 and b = -0.084675, accurate to
  0.0019 dex over the delta prior.
- **The width.** s = 0.033846 dex: the rms of log10(observed/expected) over
  the 28 bins, i.e. the catalog's structure about one power law. The fit's
  statistical error (3e-4 dex) is negligible.

## Stages (in this order, one job)

1. **Parity.** Evaluate the P12.4 target at about 512 posterior points from
   12S S1 and about 64 prior points, including the prior edges, in three
   arms:
   - the old env at a935ef7;
   - core e7c3007 with the old settings stated explicitly;
   - core e7c3007 with the new defaults.

   Report |dlogL| and the importance-reweighted H0 median. Then a timing
   benchmark.
2. **Spectral-only H0 grid** (the P12.3 equivalent) on the current GW input,
   on core e7c3007.
3. Chain **repro_12S**: the 12S prior, new defaults. It is compared with
   69.4 [64.1, 74.8].
4. Chain **flat_wide**.
5. Chain **count_ridge**.
6. **Exact GW input.** The spectral-only grid, then chain
   **count_ridge_exactGW**, on GW input files rebuilt with gwcat 8263ae9.
   - The same build recipe, events, samples and injection rows.
   - Control: `--legacy-grid-priors` reproduces the current files.

## What is reported

For each chain:
- the H0 posterior and its width against the spectral-only grid;
- the (log10n0, delta) posterior;
- the fraction of samples near any prior edge;
- the chain's gates.

For the parity stage:
- the maximum |dlogL| of each arm;
- the reweighted H0 shift.

**Expectations, not thresholds.** With the old settings, the target should
equal a935ef7 to rounding. The new defaults should agree to well below the
sampler noise. No pass/fail threshold is set; the owner judges.

## Results (2026-10-05)

All 14 stages ran in one rita A100 job (1351923, 31.4 h, 0 failed stages).
Outputs are under
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12t/runs/`
(each stage directory holds result.json and samples.npz; the runner summary is
in runner_status.json).

### Parity and speed

576 points: 512 from the 12S S1 posterior, 48 prior points, 16 prior edges.

| Arm vs the old env (a935ef7) | max abs dlogL | bitwise equal | reweighted H0 shift | s per call (A100) |
|---|---|---|---|---|
| e7c3007, old settings stated | 0 | 100% | 0 | 0.576 vs 0.584 |
| e7c3007, new defaults | 4.5e-12 | 6% | -6e-14 | 0.264 vs 0.584 |

The new defaults agree with the old code to rounding and are 2.2 times faster
per call. The first call is slower: about 70 s instead of 8 s of compilation.

### Spectral-only H0 (grid, step 0.5 over [20, 140])

| GW input | median | mean | 68% | sd |
|---|---|---|---|---|
| current (interpolated priors) | 64.52 | 64.64 | [59.6, 69.6] | 5.05 |
| exact priors (gwcat 8263ae9) | 64.52 | 64.64 | [59.6, 69.6] | 5.05 |

(Corrected 2026-10-08, Phase 12X: the median and interval were first recorded
as 64.27 and [59.4, 69.4], half a grid step low. The stored posteriors give
the values above; the mean and sd were right.)

The exact priors move the posterior mean by 0.002 km/s/Mpc.

### P12.4 chains (dynesty nlive 1000, dlogz 0.1, seed 22)

| Chain | H0 median [68%] | H0 sd | sd / spectral | log10n0 | delta | logZ |
|---|---|---|---|---|---|---|
| repro_12S | 69.33 [64.1, 74.9] | 5.52 | 1.09 | -1.819 ± 0.105 | -0.73 ± 0.36 | -765.33 ± 0.07 |
| flat_wide | 69.41 [64.1, 75.5] | 5.80 | 1.15 | -1.820 ± 0.170 | -0.72 ± 0.45 | -766.12 ± 0.08 |
| count_ridge | 70.22 [64.6, 75.6] | 5.55 | 1.10 | -1.749 ± 0.049 | -0.84 ± 0.35 | -765.18 ± 0.07 |
| count_ridge_exactGW | 70.11 [64.6, 75.5] | 5.52 | 1.09 | -1.747 ± 0.048 | -0.84 ± 0.35 | -765.20 ± 0.07 |

Diagnostics for every chain:
- converged (stop reason "convergence", final dlogz 0.0999);
- the 12F gate 7 is met, unpenalised at the posterior mean and median;
- selection N_eff is 5.2 to 5.4 times the threshold.

Prior edges, as the fraction of samples within 2% of the prior range of an
edge:
- log10n0: 2.5% for repro_12S (prior [-2.0, -1.6]); 0 for the other chains;
- delta: 0 for every chain.

### Reading

1. **Reproduction.** On current core with the new defaults, repro_12S gives
   69.33 [64.1, 74.9]. 12S gave 69.4 [64.1, 74.8].
2. **The n0 prior.**
   - Widening log10n0 to [-2.4, -1.2] moves H0 by +0.08 and widens it by 5%.
     The data alone place log10n0 at -1.82 ± 0.17, inside the old prior.
   - Tying n0 to the catalog's total count moves H0 by +0.9, about a sixth of
     its width. It pins log10n0 three times tighter, at -1.75 ± 0.05.
   - The evidence prefers count_ridge to flat_wide by 0.9 in log.
   - With one seed per chain, the prior carries about 1 km/s/Mpc of H0, not
     ±2.
3. **The catalog's information.** The catalog still does not narrow H0:
   - every chain is 1.09 to 1.15 times wider than the spectral-only grid;
   - it moves the median by +5 to +6 against the spectral median of 64.3.
4. **Exact GW priors.** They shift the chain by -0.11 and the spectral grid by
   0.002: negligible.

Per the declared plan, step 4 (splitting the catalog into its spectroscopic
and photometric parts) is the next candidate, because the catalog still adds
no precision. The owner decides.

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
sha256, in `config/record_envs/12T.json`; `scripts/check_frozen_environment.py --record 12T` checks that an
environment is exactly it. This record names no consumer commit, so no run commit is tagged. The full test suite is
run by `./ci.sh` in the record environments (CPU, HENON); it was green at the follow-up head
(`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Population of the base configuration (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** This record's runs built the 'gwtc5' preset of their core as it is (core e7c3007: mu_chi 0.0633, sigma_chi
0.3654); `population.fixed_values` did not exist yet (it came with 12Y's commit 0d75b40). Since the consolidation the
base configurations declare `population.fixed_values` (0.04, 0.10) for the preset, so that they mean one population on
every core (core #60 changed the preset to that pair). On a core before #60, a stage run from the consumer's main with
the base configuration therefore uses (0.04, 0.10), not this record's population, and the gated P12.3 and P12.4
runners refuse the base configuration there. This record is reproduced from main with `--set
population.fixed_values=null` (the configuration as it ran; `config/desi.fixed_population.core_preset.json` is the old
base configuration byte for byte). The committed manifests (`config/phase12t_manifest*.json`,
`config/phase12u_manifest*.json`) drop the base configuration's spin declaration in every stage that builds a target
(`population.fixed_values=null`) and point the 12T parity arms at `config/desi.fixed_population.core_preset.json`:
they resolve the configuration these runs used.

**Chain stages (consumer PR #31, merge b9ec283; findings C029, C121, C122, C123, C124, C125).** From the merge: a
chain stage given `--anchor-from` refuses a missing, unreadable or unaccepted spectral grid (it fell back to the
default anchor silently), and the manifest's chain stages require their anchor grid (this record's two grids are
accepted, so its anchors are unchanged); the spectral stage refuses a `numerics.core_numerics` override that differs
from `--core-numerics` (no manifest gave one); the chain's result records the consumer commit and core's run
fingerprint digest, its `status.json` and log carry no H0 location, a non-finite diagnostic value is written as null
instead of aborting, and a finished checkpoint that did not converge is refused before the build (a chain run with
`--allow-unconverged`, as the smoke manifest's are, resumes it and writes the capped result, as before).

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

**Runner jobs (consumer PR #30, merge 6d0f800; finding C138).** This record's runner jobs ran from shared clones with
no commit pin. Only 12AE Part 2 mixed commits; this record's runs did not. From the merge the runner job files refuse
to start without PHASE12_EXPECT_SHA naming the commit of a clean checkout, and the stage runner repeats that check
before every stage, stopping (exit 3) if the checkout moves.

**Launch files (consumer PR #30, merge 6d0f800; finding C137).** The launch files of this record predate the owner's
Slurm rules of 18-19 Oct 2026 (7-day limits; rita GPU jobs at 128 CPUs and 120G; holder steps only through the
wrapper) and break them. They are kept unchanged in what they launch, as the record of how the record ran, and from
the merge they refuse to run unless PHASE12_ALLOW_HISTORICAL names them (slurm/historical_launch_files.txt lists
them). The B1 and B2 pipelines' HENON fallback now clears every SLURM_* variable first.

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

**Union leak (consumer PR #24, merge 402c947; findings G2.3, C002).** The union's spectra come from a match cut at z
<= 0.30, so 518,466 Legacy Survey galaxies that DESI measured above 0.30 (2.28% of the union, 3.12% of photometric
rows; 65,910 with photo-z <= 0.245) are photometric hosts in the window. Record 12AO documented and built the
leak-fixed union; Phase 12 has not adopted it. Catalog version 2 uses the z <= 0.5 match. The floor paragraph of 12R's
amendment of this date applies here too (C002).

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** The last stage of this record reads the
gwcat 8263ae9 exact-prior rebuilds; see the GW inputs addendum (`phases/12_gw_inputs_addendum_2026-10-26.md`). No
number of this record changes.

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

**Chain resume (consumer PR #25, merge 498a147; findings C004, C042).** The chain drivers of this record resumed any
checkpoint in their output directory, guarded only by core's run fingerprint, which does not cover the catalog
settings (m_lim, the K-correction, a fixed log10n0; sigma_kde only under kernel pin auto) or, for the 12T chain stage,
the input files; and `--fresh` left the old checkpoint in place, so a fresh run killed before its first checkpoint
save could have resumed the old chain. Neither happened for this record: every chain of record ran with `resumed`
false in one session (the only production chain killed and resumed, A1's limit-2 chain high_seed41 of record 12AA,
sampled 3.9 million further calls after its resume, a real continuation), no manifest or launcher passes `--fresh`,
and each stage has its own output directory checked by the manifest runner's input checksums. Since the merge, the
drivers stamp a run identity (the resolved configuration's sha256, the inputs' sha256, the code, the package commits
and the backend) beside the checkpoint and resume only under it; a checkpoint without a stamp, as every checkpoint of
record is, is refused unless `--adopt-checkpoint` is passed; and `--fresh` moves the old chain aside (to
`<out>/superseded-<UTC>/`; nothing is deleted). Core's run fingerprint and the recorded `run_fingerprint_digest` are
unchanged.

**DONE markers of the manifest runner (consumer PR #25, merge 498a147; finding C073).** The manifest runner treated a
stage's DONE as final without comparing its recorded command or the inputs' checksums. At the reviewed commit every
production run directory's DONE command equalled its manifest's (repository location aside); only smoke directories
held stale DONEs. Since the merge, DONE records the command, the repository and commit, and the sha256 of every
required input, and the runner refuses a DONE whose command or inputs changed and leaves its outputs untouched
(`--rerun-stale` moves the stage aside and reruns it); a DONE written before the change is judged against the
manifest's checksums. A read-only probe of the fixed runner on every production run directory, at the package's
fifth-round head with main 402c947 merged
(`darksirens-core-data/reviews/consumer-2026-10-24/fix/notes/p07-resume/probes/runner_dirs_of_record_37e6f26.json`),
gives the state below; since then the manifests' commands have changed only by the named delta override that consumer
PR #35 adds to two 12U stages already read stale (record 12U).

The consolidation of the consumer onto main (consumer PRs #20 and #21) added `--set population.fixed_values=null` to
the six 12T spectral and chain stages and to all six 12U scan and chain stages, and the pinned base configuration
(`--config config/desi.fixed_population.core_preset.json`) to the four 12T parity and benchmark stages that evaluate
the DESI target, so that the resolved configuration stays the one of record after the base configuration gained its
spin declaration. The DONEs of ten 12T stages and of all six 12U stages hold the command before that edit, so the
fixed runner reports them stale and refuses them (outputs untouched); the other four 12T stages, three of the five 12U
preparation stages and every stage of 12.5 step 1, A1, A1 var8, A1 var2, B2, the ladder cell and 12AP still read done,
and so do nine of the eleven 12AE (gamma/mu1) stages.

**Misspelt `--set` keys (consumer PR #25, merge 498a147; finding C088).** A misspelt `--set` key outside the sampler
block was accepted, ignored and shown in config.resolved.json. No record path carries one: every `--set` key of the
manifests in config/, of the 12AG and 12AH Part B plan builders and of the shell and Slurm scripts (slurm/,
scripts/*.sh) is a key of the base configuration of the driver it reaches or a key that driver reads (a test of the
consumer checks each of them, command by command). Since the merge, such a key is refused before anything runs.
