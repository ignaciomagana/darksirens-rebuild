# Phase 09 S5 — host-property preparation and survey validation

Status: **ACCEPTED (offline mark preparation / validation); exact installed-core replay remains an S6 integration gate**

## References

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core runtime:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
surveys repo:     ignaciomagana/darksirens-surveys
accepted S5 head: f2c39a4265038a321f45e40a38a7284fb3280f6c
accepted S5 tree: c91592ebe01fe19225d95b7dbf821061fc1627c6
```

`darksirens-core` remains frozen. Runtime marked-host weighting, eta parameters,
log-h clipping, missing-host modulation, and likelihood evaluation remain
core-owned. S5 constructs only survey-side centered host properties and audit
summaries.

## Scope

S5 adds:

```python
MARK_CENTER_NBINS = 40
center_mark_values(...)
center_catalog_marks(...)
SurveyValidationReport
validate_catalog_rows(...)
```

The centering rule is the pinned legacy `darksirens/catalogs/marks.py`
convention:

1. equal-width redshift bins on `[0, z_max]`;
2. `searchsorted(edges, z, side="right") - 1`;
3. clip the resulting bin index to `[0, n_bins-1]`;
4. subtract the survey-wide mean host property in each occupied bin;
5. default to 40 bins.

The flat-row implementation is mathematically the same operation as the legacy
padded-catalog implementation before pixelization. Non-finite real-galaxy mark
values are rejected rather than repaired.

## Explicit redshift-grid firewall

Legacy centering obtained its upper edge from the imported package `zgrid`,
which is itself controlled by the run-defining `DARKSIRENS_ZMAX` environment
value. S5 therefore requires `z_max` explicitly and does not import or guess the
core grid cap.

A production workflow must use the same cap for mark preparation and the core
analysis. This preserves the mature convention while making the dependency
visible in provenance instead of import order.

The legacy endpoint-clipping behavior is retained deliberately: a row above
`z_max` is assigned to the final centering bin. Survey/sample cuts remain an
upstream scientific choice and are not silently added here.

## Validation semantics

`validate_catalog_rows` reuses S1's exact row/nside validation helpers and
reports deterministic summaries of:

- retained row count;
- HEALPix cells containing at least one retained galaxy;
- redshift range;
- redshift-error median/maximum;
- weight range/sum;
- normalized extra-column names.

The reported `occupied_pixel_fraction` is explicitly **not** called sky or
footprint fraction. For a sparse catalog, occupied HEALPix cells are not an area
estimator and must not be reused as completeness.

## Acceptance gate

```text
workflow:  ci
run:       34682021528
job:       103522272053
head:      f2c39a4265038a321f45e40a38a7284fb3280f6c
result:    SUCCESS
pytest:    36 passed
firewall:  PASS
```

The accepted exact-head suite replays S1-S4 and adds S5 checks for:

- exact frozen legacy bin/search/clipping semantics;
- default centering of all normalized `mark_*` extras;
- explicit mark-subset selection;
- preservation of non-mark galaxy properties;
- rejection of non-finite/missing/duplicate marks and invalid centering config;
- centered-mark coindexing through the S1 pixelizer;
- validation-report HEALPix occupancy and scalar summaries;
- explicit prevention of occupancy being labelled footprint/sky area;
- reuse of the S1 invalid-row boundary.

## Next slice

S6 is the final surveys companion integration/freeze:

- build/install `darksirens-surveys` from a clean wheel;
- install the frozen `darksirens-core` package at exactly
  `af2488b0ccb48c65e63cffcae306a8a4a4bfeb66`;
- construct a standardized catalog with surveys and consume it through the
  public `darksirens.load_catalog()` API;
- replay the S3 real-core distance-modulus selection-fit path rather than the
  test-only NumPy interpolation helper;
- verify the one-way import boundary after both packages are installed;
- freeze the accepted surveys head only after the cross-package gate is real.

Do not vendor or duplicate core numerics merely to make the integration gate
self-contained.
