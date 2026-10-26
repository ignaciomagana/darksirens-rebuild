# Phase 12P — recalibrating the DESI catalog's count and luminosity model: scope

## Status

**SCOPE ACCEPTED, DECISIONS TAKEN (owner, 2026-09-29); implementation in
progress.** The decisions are listed below. The
owner asked for this scope, and for darksirens-surveys to stay general, with
the DESI specifics in the consumer.

## What the current calibration is

The production calibration block (log10n0 -2.397984, delta 0.940473, M0hat
-20.309782, sigma_M 0.714447, K(z) = 1.13465 z - 4.88963 z^2 + 8.58828 z^3)
comes from the legacy repo, `ignaciomagana/darksirens` at c042527.

- **n0 and delta**
  - Source: `experiments/desi_full259/data/n0_calibration.json`, which differs
    slightly from the `desi_ingest` copy because it used the ZMAX 6 grid.
  - delta is a weighted least-squares fit of the dN/dz shape over
    [0.05, z_depth].
  - n0 is a closed-form ratio: N_obs / (f_sky * integral from 0 to z_depth of
    C_sel (1+z)^delta dV), with H0 = 67.74 and Om0 = 0.3075, in Mpc^-3.
  - f_sky is the fraction of occupied pixels (0.620), not the survey mask.
- **M0hat and sigma_M**
  - A Gaussian luminosity function truncated at m_lim 21, conditional on each
    galaxy's redshift (legacy `fit_selection_from_mags`).
  - Magnitudes are M - 5 log10 h (H0 = 100), so the fit is exactly
    H0-independent. It sees no counts and no photo-z scatter.
  - The prior widths (1.6e-4 mag) are the statistical Hessian of 22.8 M
    galaxies. The north/south offset is 0.055 mag (139 sigma).
- **K(z):** a cubic fit to per-galaxy M_APP - MAG_R - DM(z; 67.74, 0.3075).
  H0 cancels; Om0 does not.
- **z_depth 0.3** is the input catalog's upstream cut on observed z, copied
  over. It is not a completeness estimate.

## What is wrong with it

1. **n0 is H0-circular.** Fitted at H0 = 67.74 in Mpc^-3 and held fixed while
   H0 is sampled, the expected counts (proportional to n0 dV(H0), so to
   H0^-3) match the observed counts only at 67.74. The legacy repo's own
   notes flag this (`field_level_plan/PLAN.md`: "manufactures a
   standard-density H0 constraint"). Core computes dN_exp = n0 apix
   dV_c(z; H0) (1+z)^delta with dV in Mpc^3 (core
   `catalog/completeness.py:201`, `cosmology/distances.py:334`).
2. **The calibration footprint differs from production.** Occupied-pixel
   f_sky is 0.620, while production's sum of f_p times the pixel area is
   0.559 of the sky. The expected counts are about 10% low, which is the
   10-38% low-z excess of observed over model (12N, "Follow-up checks").
3. **The edge is not modelled.** The input is cut at observed z = 0.3, and
   most redshifts are photometric. Scatter across a hard observed-z cut makes
   dN/dz fall towards the edge, which neither the one global normalization
   nor the magnitude model reproduces. This is the prior deficit and jump at
   the cut (12N, 12O).
4. **Om0 is inconsistent:** 0.3075 in the calibration, the magnitude fit and
   K(z), against 0.3089 in the analysis.
5. **The M0hat and sigma_M priors are statistical only** and ignore the
   north/south offset and the photo-z bias of the magnitude fit.

## Proposed changes

### darksirens-surveys (general, a package-change record and a new pin)

darksirens-surveys already fits the magnitude selection in h-units
(`selection.py:230-379`, Gaussian and Schechter). It has no n0 or delta fit,
no count likelihood, no redshift ceiling, and no observed-versus-expected
diagnostic. Proposal:

- **New `density.py`: `fit_density_selection(m, z, pix, *, f_p, m_lim, z_min,
  z_max, sigma_z=None, free=..., fixed=..., k_corr_coeffs=None, Om0, w0, wa)`.**
  An extended Poisson likelihood over galaxies:
  - the density n0hat Omega_eff dVhat/dz (1+z)^delta times the magnitude
    density, normalized over [z_min, z_max];
  - Omega_eff = sum of f_p apix, from the survey map, not from occupancy;
  - dVhat in (Mpc/h)^3 at H0 = 100, so n0hat is in h^3 Mpc^-3 and the fit is
    H0-independent;
  - z_max is required. With per-galaxy sigma_z, the redshift density is
    forward-modelled into observed z before the cut, so a hard observed-z cut
    is handled;
  - n0hat profiles out in closed form. The magnitude part reduces to the
    existing conditional fit, so frozen S0B parity is kept for M0hat and
    sigma_M when sigma_z is None;
  - it returns a Laplace covariance.
- **New `density_completeness_curve(...)`**, returning observed, expected and
  their ratio against z. This is the general form of the 12N check.
- A lazy core `dV_of_z` import next to the existing distance-modulus one; a
  selection-fit payload v1.2 (log10n0hat, delta, z_min, z_max, Omega_eff,
  H0_ref); the frozen public-surface list updated.
- Tests: synthetic catalogs at two true H0 values, with a hard observed-z
  cut and photo-z scatter, recovering n0hat and delta H0-independently.
- Optional, purist: move the `desi_legacy_*` column adapters
  (`adapters.py:48-232`) to the consumer.

### Consumer desi_darksirens_selection (DESI specifics)

- A calibration script. It runs the surveys fit on the production catalog:
  - the M_APP <= 21 cut, the 12I mask rule, the production f_p map;
  - Om0 0.3089, K(z) refit at Om0 0.3089;
  - z_max 0.3 on observed z, ZERR as sigma_z;
  - fitted over all of [z_min, 0.3] with the edge forward-modelled, and
    checked against a fit on [z_min, 0.3 - 3 sigma_z].
  It writes a new calibration block with its provenance.
- A widened, systematics-driven prior on M0hat and sigma_M: at least the
  north/south offset, and the photo-z bias measured on a mock.
- **The H0 coupling fix, in the consumer only.** The P12.4 target builds its
  CatalogParameters itself (`phase12/desi_selection.py:184-192`), and the
  kernel pin does not read n0. The target can pass
  n0 = n0hat (H0/100)^3 on every proposal, with no core change.
- Re-derive z_depth from the recalibrated model (the 12O continuity
  criterion, now required over the whole H0 prior range), then rerun the
  chain, the 12N matrix rows, and the depth check.

### darksirens-core (not needed for DESI)

- The generic binding has the same coupling (`runtime_binding.py:210`:
  n0 = 10**log10n0 in Mpc^-3).
- Making log10n0 h-scaled there is a separate package-change record, for other
  consumers. It is not required here, because the DESI target builds its own
  parameters.

## Order and size (estimates)

```text
1  surveys: density.py + diagnostic + tests + payload v1.2 + package-change record   ~1-2 days
2  consumer: calibration script on the DESI catalog; K(z) refit; widened LF prior    ~1 day
3  consumer: n0 = n0hat (H0/100)^3 in the P12.4 target; tests; repin surveys         ~0.5 day
4  depth re-derivation, chain run, 12N rows, depth check                             ~0.5 day (GPU)
```

## Owner decisions (2026-09-29)

1. **Edge:** forward-model each galaxy's sigma_z (ZERR) into observed z
   before the 0.3 cut, and fit over the whole [z_min, 0.3]. Cross-check
   against a fit restricted to z < 0.3 - 3 sigma_z.
2. **Luminosity-function prior:** widened to the north/south hemisphere offset
   combined with the photo-z bias measured on a mock catalog.
3. **DESI adapters:** move `DESI_LEGACY_RAW_COLUMNS`, `desi_legacy_rows` and
   `load_desi_legacy_hdf5` out of darksirens-surveys into the consumer.
4. **Core:** fix the n0 H0 coupling in core now, with its own package-change
   record, a new core pin, re-validation and a consumer repin. The generic
   binding gains an h-scaled count normalization. The legacy convention stays
   available, because the frozen parity gates compare against it.

## Amendment (26 Oct 2026): independent review, round 3

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses below.
The fix packages merged first (25-26 Oct 2026) did not touch this record. This one covers five more, merged on 26 Oct
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

**K(z) refit (consumer PR #24, merge 402c947; finding C072).** The scope lists a K(z) refit at Om0 0.3089. It was not
done: every calibration from 12Q on reads the legacy coefficients (1.13465, -4.88963, 8.58828), fitted at Om0 0.3075.
The distance-modulus difference between the two Om0 is at most 7e-4 mag for z <= 0.3, and the magnitude-limited
completeness changes by at most 5e-5 (relative). The refit is negligible and is not done.
