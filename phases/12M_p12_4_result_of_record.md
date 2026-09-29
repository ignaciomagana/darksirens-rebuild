# Phase 12M — the first P12.4 posterior as a result of record

## Status

**ACCEPTED (owner, 2026-09-29).** The P12.4 fixed-population DESI field H0
posterior of 2026-09-29 is the first Phase 12 result of record. Its products
are frozen, read-only, at
`/hildafs/projects/phy220048p/magana/darksirens-core-data/phase12_frozen_2026-09-29/`.
Figures and text read only from there.

## The result

A fixed-population GWTC-5 + DESI dark-siren analysis: 259 events,
Product A inputs (chieff PE, chieff_reference selection), the DESI union
catalog at nside 64 under the Phase 12I mask rule (22,785,279 galaxies), and
the field footprint rule `C_p(z) = f_p Cbar(z)`. Om0 = 0.3089, and `M0hat` and
`sigma_M` carry their calibration priors.

```text
H0 median 71.07   mean 70.88   sd 4.49   68% [66.29, 75.13]   90% [63.57, 78.32]   (km/s/Mpc)
M0hat and sigma_M: posteriors equal to their priors within their widths
catalog-free (P12.3) baseline: median 64.52, 68% [59.63, 69.65]
```

## Provenance

- Consumer `desi_darksirens_selection` `c86629b`; core `a46dec7`.
- Settings under Phases 12B to 12L: soft selection guard at cap 20; single-pass
  sums; the kernel pin "auto"; dynesty 2.1.4 with nlive 1000, dlogz 0.1,
  seed 22.
- Environment: the frozen stack plus the 12K CUDA backend, on the MIKO NVIDIA
  H100 NVL; the chain ran 2026-09-29, 05:03 to 05:33 UTC.
- Evidence of the chain's gates:
  `phases/12F_selection_guard_and_gwcat_products_acceptance.md`,
  "Production-path evidence".
- Frozen files (sha256, first 16 hex; the full list is `MANIFEST.sha256` in
  the frozen directory):

```text
results/fixed_population_desi_h0.json          be23ce578ced2e62
results/fixed_population_desi_samples.npz      8767a38604b71289
results/fixed_population_spectral_h0.json      42d21f65d9fdce55
provenance/fixed_population_chain.json         92cd5a48f926592a
provenance/preinference_diagnostics.json       6aa5aeb9aa94492b
provenance/inputs.resolved.json                52d5fc6aad8218f9
provenance/bootstrap_environment.json          bff563bf1883f88d
inputs/desi_union_nside64.h5                   f6227dc0c31c82c8
```

## Reliability

- dynesty stopped on convergence at final dlogz 0.0999, with log Z
  -780.722 +- 0.058.
- The soft guard's penalty is exactly zero at the anchor, the posterior mean
  and the posterior median.
- The Monte-Carlo variance of ln L at the posterior centre is 7.8.
- The posterior is robust to the guard cap and the sampler seed. Caps 15 and
  30, and seeds 23 and 24, move the median by at most 0.05, about 0.01 sd
  (table in `phases/12L_selection_guard_cap_20_contract.md`, "Robustness").
- The P12.2 calibration probe equals the 12F reference to 6e-16. GPU and CPU
  agree to 1e-15 at single points (12K record).

## Scope

This is a fixed-population result. The population is held at its Phase 12
fixed values. The fixed-population robustness matrix (one population or
survey setting varied at a time) is the next step and is not part of this
record. Consumer contract CI is waived until GitHub Actions is unblocked, as
for 12H and 12F.

## Caveat: catalog depth (owner, 2026-09-29)

The result of record stands as computed, and it carries a systematic that
the robustness matrix found (`phases/12N_fixed_population_robustness_declaration.md`,
"Results"):

```text
z_depth 0.2   64.55   68% [61.23, 67.81]   -1.45 sd
z_depth 0.3   71.07   68% [66.29, 75.13]   (this record)
z_depth 0.4   67.66   68% [63.58, 73.00]   -0.76 sd
```

The catalog depth z_depth, carried over from the legacy line, moves H0 at
the level of the statistical error and non-monotonically. The mask
definition and the angular galaxy structure do not (at most 0.11 sd). No
paper text quotes this result until the depth question is settled. The
checks under way: the host prior at the depth cut, the catalog's
completeness against redshift, and a smooth-n(z) control.

## Verdict

**Accepted (owner, 2026-09-29), with the depth caveat above.**
