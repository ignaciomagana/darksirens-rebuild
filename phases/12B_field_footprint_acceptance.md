# Phase 12B — footprint-aware field DESI consumer acceptance

Status: **ACCEPTED / DEPLOYABLE — PRODUCTION NUMERICAL RUN PENDING**

Parent production phase: `phases/12_production_analysis_contract.md`

Scientific correction contract: `phases/12B_field_footprint_correction.md`

This record supersedes the pre-correction P12.4 deployment described by
`phases/12_fixed_population_execution_chain.md`. That historical record remains
unchanged as provenance; its DESI target must not be used for production H0
inference.

## Trigger

A final static audit before the first Hildafs numerical run found two
load-bearing mismatches between the reconstructed P12.4 consumer and the
intended mature full-259 estimator:

1. the radial Gaussian magnitude-selection completeness was broadcast to every
   HEALPix row, including sky outside the DESI footprint, so off-footprint rows
   incorrectly used `(1-C_sel)dN_exp` below the survey depth instead of the full
   missing-host density `dN_exp`;
2. the consumer used the reconstructed row-conditional catalog normalization,
   while the mature full-259 production line used
   `catalog_sky_weighting=field`, retaining relative host surface density across
   sky pixels.

The legacy production records independently show that the footprint treatment is
numerically large, not cosmetic. The old unmasked selection-mode line was near
H0 ~ 90 km/s/Mpc, whereas the corrected footprint-aware Q-free line was near
H0 ~ 71.5 km/s/Mpc. No pre-correction Phase-12 P12.4 result was therefore run or
accepted.

## Frozen scientific reference

```text
legacy repository:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

legacy footprint product:
  experiments/desi_ingest/data/mth_map_nside128.h5

legacy production conventions:
  C_p(z) = f_p Cbar(z)
  f_p = 0 off footprint
  catalog_sky_weighting = field
  c_mode = selection
  no Q/LSS correction in the accepted Phase-12B target
```

The surveys package remains the owner of footprint-map parsing and HEALPix
degradation. Core consumes only one already-resolved row fraction per catalog
row.

## Accepted core change

Repository: `ignaciomagana/darksirens-core`

```text
starting Phase-12A core:
  8b9dc64629cf11838a9fc1de233e46b91082caf7

Phase-12B PR:
  #9 — Phase 12B: footprint-aware field catalog estimator

accepted PR head:
  efaf98d611549c028948a459f1d65487ddd4f744

squash merge / main:
  bb4812dc2bf49fe7f4412ba797621b668ccc26a5

tree:
  ff29b5b67029889e27a25dd4b6c33d59d264d3d4
```

The core diff was additive and confined to exactly three files:

```text
src/darksirens/selection/footprint.py
src/darksirens/catalog/field.py
tests/test_phase12b_field_footprint.py
```

No accepted conditional production module was modified.

### Core semantics

`selection_completion_curves_with_row_fraction` applies

```text
C_p(z) = f_p Cbar(z)
```

before constructing the missing-host budget. Therefore an uncovered row with
`f_p=0` has `dN_miss=dN_exp` below depth as required.

`FieldIncompleteCatalogPriorState` reuses the accepted conditional state
assembly and restores the row host mass divided out by the conditional
evaluator. It returns the additive field numerator

```text
N_obs p_cat(z|row) + dN_miss(z|row).
```

For this **single-catalog** hierarchical likelihood the survey-global
normalizer is a common theta-dependent factor in every PE and selection
redshift density and cancels exactly between the N event evidences and
`-N log(mu)`. That cancellation is explicitly tested. This unnormalized field
surface is not an admitted substitute for explicit catalog-by-catalog global
normalization in a multi-catalog mixture.

### Core acceptance gates

All exact-head historical workflows completed successfully, including:

```text
Phase-8 full reconstructed regression:
  run 34872949605 — SUCCESS

Phase-5 catalog/dark/bright + pinned-legacy parity:
  run 34872949824 — SUCCESS

post-merge reference integrity on bb4812dc...:
  run 34873970805 — SUCCESS
```

The Phase-5 job passed catalog-kernel, ordinary-completeness, ordinary-siren,
marked-host, and catalog-selection legacy/new parity after the Phase-12B
addition. The Phase-8 broad suite and companion-import firewall also passed.

## Pre-correction consumer lockout

Repository: `ignaciomagana/desi_darksirens_selection`

Before the corrected consumer was admitted, PR #7 added a hard execution block
so the old conditional/unmasked P12.4 target could not be launched accidentally.

```text
PR #7 CI:
  34873105917 / 104073602863 — SUCCESS

PR #7 merge:
  c42ddfed9bad8dbc0702eec957470dd6d7b71a46
```

## Accepted corrected consumer

Repository: `ignaciomagana/desi_darksirens_selection`

```text
PR #8:
  Phase 12B: corrected footprint-aware field DESI consumer

final accepted PR head:
  ebe6f1308b87183b05c25fb2af168e0069e263a4

final-head contract CI:
  34894171602 / 104143891610 — SUCCESS

squash merge / main:
  2668ae7e2eb9325910e1a8bec9b7228003cb4942

tree:
  6297fce9eee6679ebaed10bb3a081d46aaace9bc

post-merge contract CI:
  34894224773 / 104144072068 — SUCCESS
```

The corrected consumer pins the accepted Phase-12B core and keeps the other
three package pins unchanged:

```text
darksirens-core     bb4812dc2bf49fe7f4412ba797621b668ccc26a5
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
```

## Corrected production chain

The active chain is now fixed to:

```text
P12.1  frozen four-package environment
       ->
       standardized DESI input + footprint fingerprint/provenance
       ->
P12.2  pre-inference GW/selection diagnostics
       ->
P12.2b footprint support diagnostics
       ->
P12.3  fixed-population catalog-free spectral-siren baseline
       ->
P12.4  fixed-population DESI field inference
```

The chain stops on the first failed gate.

The footprint source is explicit in input schema v2. It is loaded through the
frozen surveys seam, degraded nside 128 -> 64 using the accepted equal-area
operation, and SHA256-fingerprinted on every production-chain invocation even
when the standardized galaxy catalog is not rebuilt.

P12.2b records the footprint fraction seen by every PE event and the detected
injection campaign. It does **not** remove off-footprint samples or events. They
remain in the full 259-event analysis and enter P12.4 with `f_p=0`. An occupied
catalog pixel marked uncovered is a hard error.

Direct invocation of P12.4 also fails closed unless all of the following match:

- the repository Phase-12B execution marker;
- the active core pin and target schema;
- live footprint path and SHA256 against resolved input provenance;
- accepted P12.2 plus Phase-12B footprint diagnostics;
- accepted P12.3 under the exact active package stack;
- the hard PE+selection Monte-Carlo reliability gate.

The repository execution marker admits **execution only**. It does not accept a
numerical H0 result.

## Remaining legacy caveat

The frozen `mth_map_nside128.h5` path preserves the mature legacy
`masked_frac` construction. The surveys extraction explicitly records that the
legacy builder can estimate `masked_frac` from a source-count fraction rather
than an unbiased geometric area fraction. Phase 12B does not change or bless
that estimator; it only restores the already-designated footprint semantics to
the reconstructed production consumer.

No Q/LSS correction is active in the Phase-12B P12.4 target.

## Acceptance decision

**Phase 12B implementation and deployment chain are ACCEPTED.**

The previous pre-correction P12.4 target is superseded. The next admissible step
is the real Hildafs numerical chain under consumer main
`2668ae7e2eb9325910e1a8bec9b7228003cb4942` and the exact package pins above.

No new H0 posterior, interval, or headline scientific result is accepted by
this record. Numerical products must be generated on Hildafs, pass every gate,
and then be frozen separately before plotting or interpretation.
