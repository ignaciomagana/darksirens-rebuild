# Phase 12W — H0 against the host-density evolution δ on the real union (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any run. RESULTS appended below (2026-10-08).**
CPU likelihood scans only; no chain and no GPU job.

## Question

Phase 12V showed, on an empty catalog, that δ sets H0: about -6.7 km/s/Mpc
per unit of δ, with δ = 0 reproducing the spectral-only result. The chains
of 12T and 12U sample δ on U[-3, 1.5], and the GW events pull it to
-0.85 ± 0.35. How does H0 depend on δ with the real DESI union in place, and
where do the values the galaxy counts prefer fall on that curve?

## Why a grid and not a count-based prior

The owner asked for H0 under a δ prior taken from the counts. The counts do
not give one value. The union's calibration (12U) measures:
- δ = +1.05 from the whole window [0.02, 0.30];
- δ = -2.57 from z ≤ 0.172 (the cross-check fit).

The two differ by 3.6, with statistical errors near 0.001, so a single power
law does not describe the counts and a count-based prior is not defined. The
grid shows H0 at both values and at everything between (owner, 2026-10-08).

## What is run

`scripts/phase12u_stage.py scan` on HENON CPU, one job per δ.
- **Target:** P12.4 as in the 12U chains: consumer ab226d6, core e7c3007 with
  its defaults, exact-prior GW inputs, z_depth 0.245.
- **Catalog and footprint:** the standardized union
  (`phase12u/inputs/catalogs/desi_union_nside64.h5`) and the LS map.
- **δ:** -3.0, -2.57, -2.5, -2.0, -1.5, -1.0, -0.84, -0.5, 0.0, +0.5, +1.0,
  +1.05, +1.5. These are the prior range in steps of 0.5, plus the two count
  fits and the chains' posterior mean.
- **log10n0:** on the union's count ridge at each δ,
  -1.810518 - 0.089449 δ (12U, full recomputation).
- **Luminosity values:** the 12T anchor (M0hat -20.4997, sigma_M 0.5575).
- **H0:** 30 to 120 in steps of 2.5 (37 points).

Outputs go to
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12w/scans/`.

## What is reported

For each δ:
- the H0 posterior from the scan's log-likelihood with a flat prior on
  [30, 120]: median, 68% interval and sd;
- the number of rejected points and the selection N_eff range.

Across δ:
- the slope dH0/dδ;
- H0 at the two count fits and at the chains' δ;
- the difference from the empty-catalog scans of 12V at δ = 0, -0.84 and
  +1.05, which is the galaxies' contribution.

## Limits, stated in advance

- Each scan is at fixed calibration: the luminosity values are not
  marginalized, and n0 is on the ridge, not spread about it. 12V found the
  union's likelihood within 0.7 in log of the empty catalog's at fixed
  calibration, so these are expected to matter little. If the union scans
  differ from the empty-catalog ones by more than that, chains at pinned δ
  are the follow-up, and the owner decides.
- The posterior for the lowest δ may run into the upper edge of the H0 grid;
  if more than 1% of its mass lies within 5 of an edge, the grid is extended
  and the scan repeated.

## Expectations, not thresholds

- δ = 0: 64.5 ± 5.0, the spectral-only result.
- δ = -0.84: about 70 to 71, the chains' result.
- δ = +1.05 and -2.57: about 54 and about 82.

## Results (2026-10-08)

Thirteen CPU scans (HENON array 1375802; the δ = +1.5 task was resubmitted as
1375882 after a node start-up failure). Outputs:
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12w/scans/delta_<δ>/scan.json`,
and the table below as `phase12w/h0_vs_delta.json`. No scan point was
rejected, and no posterior has mass within 5 of an edge of the H0 grid.

| δ | H0 median [68%] | sd | peak logL | selection N_eff / threshold |
|---|---|---|---|---|
| -3.00 | 69.9 [64.8, 74.8] | 5.13 | -779.82 | 3.5–6.7 |
| -2.57 | 71.7 [65.9, 76.7] | 5.30 | -773.34 | 3.3–7.2 |
| -2.50 | 71.8 [66.1, 76.9] | 5.32 | -772.40 | 3.3–7.2 |
| -2.00 | 72.6 [67.0, 78.1] | 5.46 | -766.67 | 3.0–7.6 |
| -1.50 | 72.6 [66.9, 78.1] | 5.49 | -762.86 | 2.7–7.6 |
| -1.00 | 71.3 [65.7, 76.6] | 5.40 | -761.24 | 2.4–7.2 |
| -0.84 | 70.5 [65.1, 75.8] | 5.33 | -761.22 | 2.3–7.0 |
| -0.50 | 68.1 [63.7, 73.6] | 5.14 | -761.75 | 2.2–6.5 |
| 0.00 | 64.7 [60.0, 69.3] | 4.84 | -764.09 | 1.9–5.6 |
| +0.50 | 59.4 [54.6, 64.4] | 4.78 | -768.52 | 1.7–4.7 |
| +1.00 | 53.5 [49.8, 57.8] | 4.18 | -773.33 | 1.4–3.8 |
| +1.05 | 53.0 [49.3, 57.3] | 4.12 | -773.83 | 1.4–3.7 |
| +1.50 | 48.5 [44.5, 52.4] | 3.90 | -778.91 | 1.3–3.1 |

Against the empty-catalog scans of 12V (their H0 grid is 40 to 90 in steps of
2 to 5, this one 30 to 120 in steps of 2.5):

| δ | union (12W) | empty catalog (12V) | difference |
|---|---|---|---|
| 0 | 64.7 ± 4.84 | 64.5 ± 5.04 | +0.2 |
| -0.84 | 70.5 ± 5.33 | 70.9 ± 5.45 | -0.4 |
| +1.05 | 53.0 ± 4.12 | 53.5 ± 4.24 | -0.5 |

### Reading

1. **H0 is not linear in δ.**
   - For δ ≥ 0 it falls steeply, by about 11 km/s/Mpc per unit of δ.
   - It peaks at 72.6 near δ = -1.5 to -2.
   - It turns back to 69.9 at δ = -3.
   The declared expectation of about 82 at δ = -2.57 assumed 12V's local
   slope and was wrong: the value is 71.7.
2. **For every δ ≤ -0.8, H0 lies between 70 and 73.** The union's H0 of
   about 70 is what any strongly negative δ gives. The low values, 65 and
   below, need δ ≥ 0.
3. **The two count fits give 71.7 (δ = -2.57) and 53.0 (δ = +1.05).** They
   are 19 km/s/Mpc apart, more than three posterior widths, so the counts
   cannot be used to fix δ without first deciding which redshift range they
   describe.
4. **The GW events choose δ.** The peak log-likelihood is highest at
   δ = -0.84 to -1.0. Relative to that it is:
   - -2.9 at δ = 0;
   - -12.6 at δ = +1.05;
   - -12.1 at δ = -2.57.
   Both count fits are strongly disfavoured by the events. δ = 0, the
   spectral-only model, is mildly disfavoured. This is at fixed luminosity
   values with n0 on the ridge.
5. **The galaxies do not move H0.** The union differs from the empty catalog
   by +0.2, -0.4 and -0.5 km/s/Mpc at the three shared δ, within the
   difference between the two H0 grids. No chains at pinned δ are needed as
   a follow-up.
6. δ multiplies the host density by (1+z)^δ, so in the completed volume it
   acts as extra redshift evolution of the merger rate on top of the
   population's fixed evolution. The catalog analyses therefore differ from
   the spectral-only one by a free rate-evolution term, which the events
   constrain to δ = -0.85 ± 0.35 and which moves H0 from 64.7 to about 70.
   How that term should enter, free, fixed at 0, or tied to an independent
   measurement of the host evolution, is the owner's decision.

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
sha256, in `config/record_envs/12W.json`; `scripts/check_frozen_environment.py --record 12W` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12W/<sha7>` on
GitHub (ab226d6). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was green at the
follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Population of the base configuration (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** This record's runs built the 'gwtc5' preset of their core as it is (core e7c3007: mu_chi 0.0633, sigma_chi
0.3654); `population.fixed_values` did not exist yet (it came with 12Y's commit 0d75b40). Since the consolidation the
base configurations declare `population.fixed_values` (0.04, 0.10) for the preset, so that they mean one population on
every core (core #60 changed the preset to that pair). On a core before #60, a stage run from the consumer's main with
the base configuration therefore uses (0.04, 0.10), not this record's population, and the gated P12.3 and P12.4
runners refuse the base configuration there. This record is reproduced from its tagged commit (ab226d6), or from main
with `--set population.fixed_values=null` (the configuration as it ran;
`config/desi.fixed_population.core_preset.json` is the old base configuration byte for byte).
