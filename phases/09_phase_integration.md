# Phase 09 integration — darksirens-surveys

Status: **COMPLETE / FROZEN**

## Frozen repositories

```text
legacy oracle:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

core runtime:
  ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
  tree 0608b75ff5c142bfba0fc15a4fad79e0fee1fa74

surveys companion:
  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2
  tree 4c4043ee2bee2a5a8940242e2de37f5eb5dbab17
```

The core remains frozen. Phase 09 reconstructed survey/catalog construction in a
separate companion and proved that its standardized products are consumed by the
frozen core without an import cycle or duplicated runtime numerics.

## Accepted slices

```text
S0A  legacy catalog/depth reference fixture
S0B  legacy offline selection-fit reference fixture
S1   normalized rows / RING pixelization / standardized writer
S2   survey-fraction/depth maps
S3   offline Gaussian/Schechter magnitude-selection fitting
S4   DESI/Legacy native schema adapters
S5   host-property centering + survey validation
S6   clean wheels + exact frozen-core consumer integration
```

Production accepted heads:

```text
S1:  recorded in phases/09S1_catalog.md
S2:  recorded in phases/09S2_depth.md
S3:  c066f592 control checkpoint; surveys implementation accepted before S4
S4:  f0396ca95e08041c045ae16b616640d416142f32
S5:  f2c39a4265038a321f45e40a38a7284fb3280f6c
S6:  f027aef02d342041ce7259cdbf47fe689e6462f2
```

S6 supersedes the earlier surveys heads and is the sole frozen production
reference going forward.

## Final acceptance gates

```text
surveys ordinary CI:
  run/job: 34682603918 / 103523878119
  result:  SUCCESS
  tests:   36 passed
  firewall:PASS

surveys clean wheel:
  run/job: 34682603998 / 103523878256
  result:  SUCCESS
  wheel artifact id: 10294401705
  artifact digest:
    sha256:de910ec762d890660beb38ac7cde62adc9494e08e88204c0c4395afb0d406660

exact-wheel core-consumer integration:
  run/job: 34682629290 / 103523951273
  result:  SUCCESS
  core wheel sha256:
    4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

Detailed S6 record: `phases/09S6_final_surveys_freeze.md`.

## Final ownership boundary

### `darksirens-surveys`

Owns offline construction only:

```text
survey-native schema interpretation
survey quality-mask application supplied explicitly by caller
host/catalog weight-column selection supplied explicitly by caller
HEALPix catalog product construction
survey fraction / depth map construction
magnitude-selection fitting
raw host-property normalization and z-centering
survey-product validation/reporting
```

### `darksirens-core`

Remains the owner of runtime inference:

```text
standardized catalog loading
catalog redshift likelihood
ordinary completeness runtime
magnitude-selection runtime evaluation
marked-host runtime weighting
cosmology/population likelihood
sampler/public inference surface
```

### Explicitly outside Phase 09

```text
Q_LSS / Q ensembles / latent fields / lognormal fields / multitracer
  -> darksirens-lss

weak/strong lensing
  -> darksirens-lensing

campaign/paper glue and one-off analysis scripts
  -> not part of reusable companion reconstruction
```

## Scientific/data-contract decisions frozen in Phase 09

1. HEALPix catalog products use RING ordering and the core-compatible padding
   contract.
2. Legacy equal-pixel quicksort ordering is not preserved; coindexed rows are
   canonicalized without changing pixel membership.
3. DESI/LSS/systematic/FKP/PIP/completeness weights are never guessed or
   multiplied by a schema adapter.
4. Survey quality cuts such as ZWARN/DELTACHI2 are not silently applied by the
   adapter.
5. Mark centering retains the legacy 40-bin `m - E[m|z]` rule, with the redshift
   cap made explicit rather than inherited from import-time global state.
6. HEALPix occupied-cell fraction is not labelled as survey footprint area or
   completeness.
7. S3 fitting uses the frozen core cosmology lazily when available; S6 proves
   the real installed-core path against the S0B reference.
8. Core does not import `darksirens-surveys`.

## Phase closure

Phase 09 is complete. Do not add LSS completion machinery or lensing to
`darksirens-surveys` after this freeze unless a new, separately reviewed phase
explicitly reopens it.

The reconstruction now proceeds to the LSS companion. The first LSS slice must
be an inventory/reference-freeze step before any production port, following the
same pattern as surveys S0.
