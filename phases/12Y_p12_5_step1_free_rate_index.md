# Phase 12Y — P12.5 step 1: the DESI chain with δ fixed and the rate index free (declaration and results)

## Status

**DECLARED (owner, 2026-10-08) before any chain. RESULTS appended below (2026-10-08).**
The implementation and its CPU checks come first; the GPU chain is submitted
only after the owner's go.

## Where this sits

The Phase 12 contract (`12_production_analysis_contract.md`) has seven
steps. P12.4, the DESI comparison at a fixed population, is recorded in 12M to
12X and summarized in `12_summary_12M_to_12X.md`. P12.5 replaces the fixed
population by its uncertainty. This is its first step: one population
parameter, the merger-rate index γ, is sampled. The full marginalization is
scoped separately, and the owner decides it after seeing that scope.

## Why

12V to 12X found that the catalog model's host-density evolution δ acts as
free redshift evolution of the merger rate, and that this freedom, not the
galaxies, moves H0 from 64.5 to about 70. δ therefore duplicates the
population's rate index wherever the catalog is incomplete. The owner
decided to keep the freedom in one parameter, the one that carries it
physically: δ is fixed and γ is sampled.

## The model

P12.4 as in the 12T and 12U chains (the DESI union at nside 64, the LS
footprint, z_depth 0.245, exact-prior GW inputs, core e7c3007 with its
defaults, kernel pin off), with two changes:

| | 12T / 12U chains | this chain |
|---|---|---|
| δ | sampled, U[-3.0, 1.5] | fixed at 0 |
| γ | fixed at 2.5439 (GWTC-5) | sampled, flat on [-2, 6] |
| log10n0 | count ridge N(a + b δ, sd) | N(a, sd): the union's ridge at δ = 0, a = -1.810518, sd 0.036361, on [-2.346, -1.146] |
| M0hat, sigma_M | 12T priors | unchanged |
| effective-spin mean and width | 0.0633, 0.3654 | fixed at 0.04, 0.10 (amendment below) |
| the other 14 population parameters | GWTC-5 values | unchanged |

Sampled: H0, M0hat, sigma_M, log10n0, γ (five parameters, as before).
dynesty, nlive 1000, dlogz 0.1, seed 22.

The γ prior is wider than 2.5439 plus the old δ range, which would be
[-0.46, 4.04] (owner, 2026-10-08).

**The model is not identical to the 12T one.** With an empty catalog, δ = d
with γ fixed equals δ = 0 with γ = 2.5439 + d, up to a constant (12X). With
galaxies in the catalog the two differ: δ also tilts the catalogued hosts'
weights and the split between catalogued and completed hosts. The result can
therefore differ from the 12T and 12U chains by construction.

## Checks before the chain (CPU, HENON)

1. **Unit tests** of the change, including:
   - the new target at γ = 2.5439 and δ = 0 equals the existing target at
     δ = 0;
   - on a catalog with no galaxies, γ = 2.5439 + d with δ = 0 matches δ = d
     with γ fixed, up to a constant.
2. **Real-data equivalence.** A scan of the new target at γ = 2.5439 on the
   union reproduces the 12W scan at δ = 0, point by point.
3. **Real-data identity.** On the empty catalog of 12V, scans at
   γ = 2.5439 + d reproduce the 12V scans at δ = d (d = -0.84 and +1.05), up
   to a constant.
4. **The prior's edges.** Scans at γ = -2 and γ = 6 record the rejected H0
   points and the selection N_eff against its threshold. The owner sees them
   before the chain, because the selection guard has not been exercised that
   far from the GWTC-5 value.
5. A CPU smoke of the two production stages (an H0 scan, then the chain at
   nlive 8).

## What is reported

- The H0 posterior (median, 68%, sd), against:
  - the fixed-population union chain: 70.1 [64.6, 75.5] with δ free (12T);
  - spectral-only with the fixed index: 64.5 [59.6, 69.6];
  - spectral-only with the index free on the narrower range: 70.7
    [65.1, 76.6] (12X).
- The γ posterior, against 2.5439 and the 12X value of 1.7 ± 0.3; the
  fraction of samples near either edge of [-2, 6].
- The (log10n0, M0hat, sigma_M) posteriors against their priors.
- logZ, convergence, the gate, the selection N_eff at the posterior mean,
  and the scan's rejected points.

## Expectations, not thresholds

- H0 near 70 to 71 with γ near 1.7, as for spectral-only with the index
  free: the catalog added nothing at fixed δ in 12W and 12X.
- A posterior that piles up at an edge of the γ prior, or a guard that
  removes part of the prior, is reported as such and not interpreted.

## Amendment before the chain (owner, 2026-10-08): corrected spin, and the checks

**Spin.** Stage A0 (`12Z_p12_5_A0_population_sensitivity.md`) found that the
fixed population's spin pair (0.0633, 0.3654) are the GWTC-5 spin-magnitude
values, applied here to effective spin, and that the events reject them by
107 in log-likelihood. The owner decided to fix the spin at corrected values
and still sample only γ. A joint spectral-only scan of the effective-spin
mean (0 to 0.10) and width (0.06 to 0.14) has its best evidence at
**mean 0.04, width 0.10**: 110 above the old pair in peak log-likelihood, with
the neighbouring grid points 0.6 to 3.7 lower
(`phase12_5/A0/spin2d_summary.json`). These two values are fixed in this
chain. They come from this scan at otherwise fixed GWTC-5 values, not from an
external measurement.

**Reference values at the corrected spin** (spectral-only grids, 29 of 34
values of γ at the time of writing; `phase12_5/spectral_gamma/`):

| | old spin | corrected spin |
|---|---|---|
| H0, γ fixed at 2.5439 | 64.5 [59.6, 69.6] | 66.2 [61.4, 71.1] |
| H0, γ free | 70.7 [65.1, 76.6] | 67.9 [62.6, 73.5] |
| γ | 1.7 ± 0.3 | 2.22 ± 0.38 |
| ln evidence, free γ against 2.5439 | +1.7 | -1.2 to -1.8 |

With the corrected spin the events' rate index agrees with the GWTC-5 value,
and freeing it moves H0 by 1.7 km/s/Mpc, not 6. The expectations above are
superseded: this chain is expected near H0 = 68 with γ near 2.2.

**Checks, all done on CPU** (consumer branch `phase12.5/free-rate-index`):
1. Unit tests: 375 pass. With the spin override equal to the old values the
   target is the old one bit for bit; with γ = 2.5439 and δ = 0 it equals the
   existing target at δ = 0.
2. Real-data equivalence at the old spin: the scan at γ = 2.5439 equals the
   12W scan at δ = 0 exactly (37 H0 values).
3. Real-data identity on the empty catalog: γ = 2.5439 + d matches δ = d to
   1e-4 in log-likelihood (d = -0.84, +1.05), over a range of 20 to 26.
4. The spectral stage with the override reproduces the 12T grid (9e-13) and
   the A0 and joint-scan grids at the same spin values (0.0).
5. **The prior's edges.** At the old spin the guard rejected every H0 at
   γ = 6 and started at γ = 4.5. At the corrected spin, on the union:

   | γ | H0 values penalised (of 13) | selection N_eff / threshold |
   |---|---|---|
   | -2.0 | 0 | 7.1 to 10.6 |
   | 2.5439 | 0 | 17.2 to 34.4 |
   | 4.0 | 0 | 20.6 to 40.9 |
   | 5.0 | 0 | 22.5 to 31.0 |
   | 6.0 | 0 | 17.9 to 25.1 |

   The prior stays flat on [-2, 6]. The table is at the anchor calibration
   and luminosity values; other corners of the prior were not scanned.
6. CPU smoke of the two stages at the corrected spin: 0 failed stages.

The chain's starting H0 is still read from the 12T spectral grid (64.5). It
only starts the sampler, and the point was accepted in the smoke.

## Results (2026-10-08)

One chain on a rita A100 (job 1376256, 8.0 h of sampling, 127,829 likelihood
calls). Consumer `phase12.5/free-rate-index` 0d75b40, core e7c3007 with its
defaults, exact-prior GW inputs, union catalog, depth 0.245, nlive 1000,
seed 22. Outputs:
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/runs/`.

### H0 and the rate index

| Analysis (corrected spin 0.04, 0.10) | H0 median [68%] | sd | γ |
|---|---|---|---|
| **DESI union, δ = 0, γ flat on [-2, 6] (this chain)** | **67.6 [62.8, 73.9]** | 5.59 | 2.28 ± 0.35 |
| Spectral-only, γ flat on [-2, 6] (34 grids) | 67.9 [62.7, 73.4] | 5.40 | 2.22 ± 0.34 |
| Spectral-only, γ fixed at 2.5439 | 66.2 [61.4, 71.1] | | |

- **The catalog adds neither a shift nor precision.** The union differs
  from spectral-only with the same freedom by -0.3 km/s/Mpc in the median,
  and its posterior is not narrower (5.59 against 5.40).
- **γ:** 2.28 ± 0.35, 68% interval [1.93, 2.62], consistent with the GWTC-5
  value of 2.5439. Samples run from 0.87 to 3.97; none lies within 0.4 of
  either edge of [-2, 6].
- **H0 and γ are anti-correlated** (coefficient -0.40).
- The comparisons listed in "What is reported" against 70.1, 64.5 and 70.7
  are comparisons with results made at the old spin. They are not like for
  like and are not interpreted.

### Calibration parameters against their priors

| Parameter | Posterior | Prior |
|---|---|---|
| log10 n0 | -1.815 ± 0.035 | count ridge at δ = 0: -1.811 ± 0.036 |
| M0hat | -20.498 ± 0.199 | -20.500 ± 0.199 |
| sigma_M | 0.564 ± 0.131 | 0.557 ± 0.130 |

The events do not update any of the three.

### Sampler and guard

- **Convergence:** verified; final dlogz 0.0999 against 0.1, stop reason
  convergence, 7,299 iterations. logZ = -658.845 ± 0.078.
- **Gate:** met, no open items.
- **Guard:** unpenalised at the posterior mean and median; selection N_eff
  24.8 times the threshold at both.
- **Scan stage** (H0 grid at the anchor calibration, γ = 2.5439): 0 of 12
  points rejected.

### What this settles and what it does not

- With δ fixed at 0 and the freedom moved to the population's rate index,
  the DESI analysis reproduces the spectral-only result. The 12V to 12X
  conclusion, made at the old spin, holds at the corrected spin.
- It is one chain with one seed, and the mass model is fixed. Stage A0
  (12Z) found H0 shifts of 4 to 9 km/s/Mpc per one-sigma step of several
  mass parameters, so the value is conditional on the fixed mass model.
- Core main now carries the corrected spin pair in the preset (core #60,
  4b97f4a). This chain used core e7c3007 with the pair passed explicitly.

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
sha256, in `config/record_envs/12Y.json`; `scripts/check_frozen_environment.py --record 12Y` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12Y/<sha7>` on
GitHub (0d75b40). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was green at the
follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Population (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding C052).** This record's runs
declared `population.fixed_values` (0.04, 0.10) themselves, in their manifests. The base configuration's declaration
since the consolidation is the same pair, so they resolve the same configuration from main.

**Chains through the 12T stage (consumer PR #31, merge b9ec283; findings C029, C123, C125).** This record's chain
stages use the 12T chain driver: from the merge their `status.json` and logs are location-free, their `--anchor-from`
grid must be accepted (theirs is the accepted exact-GW grid of 12T) and a finished unconverged checkpoint is refused
before the build, except for the smoke chains run with `--allow-unconverged`, whose resume writes the capped result as
before.

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

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). No number of this record changes.
