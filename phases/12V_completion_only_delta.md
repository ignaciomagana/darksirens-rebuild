# Phase 12V — completion only: the host-density evolution sets H0

## Status

**RECORD (owner, 2026-10-07).** CPU likelihood scans only; no chain was run.
The owner approved a completion-only diagnostic after Phase 12U. The scans below
answer its question, so the declared GPU chain was not needed (owner decision).

## Question

Phase 12U found that the spectroscopic part, the photometric part and the
re-centred union all give H0 ≈ 70, against 64.27 for the spectral-only grid
on the same events. Do the galaxies cause that +6 km/s/Mpc offset, or does
something every catalog analysis shares?

## Inputs

Everything is under
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12v/`.
- `inputs/desi_empty_nside64.h5`: the standardized nside-64 layout with no
  galaxies (`ngals` 0 in every row; padding as the standardized catalogs).
- `inputs/footprint_zero_nside128.h5`: the LS map with `masked_frac = 1`, so
  f_p = 0 and every pixel is completed (C_p(z) = f_p Cbar(z) = 0).

Both are needed. With f_p = 0 alone, the catalog galaxies would still be hosts
on top of the full completed density.

Target: P12.4 as in the 12U union arm (consumer ab226d6, core e7c3007 with its
defaults, exact-prior GW inputs). `scripts/phase12u_stage.py scan`, HENON CPU,
with log10n0 and the luminosity values at the union anchor. With no galaxies
and C = 0 they do not enter. δ is set per scan.

## Results

The H0 posterior is computed from each scan's log-likelihood on [40, 90] with
a flat prior.

| Likelihood | δ | H0 median | sd |
|---|---|---|---|
| Spectral-only grid (12T, exact GW inputs) | — | 64.5 | 5.05 |
| Empty catalog | 0 | 64.5 | 5.04 |
| Empty catalog | -0.84 | 70.9 | 5.45 |
| Empty catalog | +1.05 | 53.5 | 4.24 |

Every scan point is accepted (selection N_eff 1.4 to 6.8 times its threshold).

At the union's anchor (δ = 1.05), the 12-point scan of the empty catalog and
that of union_centred (12U) peak at 53.5 and 53.8. Their log-likelihoods,
relative to their maxima, differ by at most 0.7 between H0 45 and 139.

## Reading

1. **With δ = 0 the dark-siren model without galaxies is the spectral-siren
   analysis**: the same median and width. The completion term then puts
   hosts at the comoving-volume rate that the spectral model assumes.
2. **δ, the redshift evolution of the host density, sets H0.**
   - H0 moves by about -6.7 km/s/Mpc per unit of δ.
   - At δ = -0.84, the posterior mean of every 12T and 12U chain, the empty
     catalog gives 70.9: the chains' H0.
3. **The galaxies do not move H0.** The union's likelihood at fixed
   calibration equals the empty catalog's to within 0.7 in log. This is
   consistent with every catalog chain being wider than the spectral-only
   grid (1.09 to 1.13).
4. **The chains' δ comes from the GW events, not from the galaxies.**
   - The chains sample δ on U[-3, 1.5]. The count ridge ties n0 to δ but
     leaves δ free, and the events pull it to -0.85 ± 0.35.
   - The galaxy counts measure δ = +1.05 (union), -0.13 (spec) and +1.54
     (photo; above the prior). These calibrations would place H0 at roughly
     54, 65 and below 54.
5. The +6 km/s/Mpc offset of the catalog analyses from the spectral-only
   result is therefore the freedom given to δ. How δ should enter, free, tied
   to the counts or fixed, is a modelling decision. It moves H0 by more than
   one posterior width. The owner decides.

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
sha256, in `config/record_envs/12V.json`; `scripts/check_frozen_environment.py --record 12V` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12V/<sha7>` on
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
