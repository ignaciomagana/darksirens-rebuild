# Phase 09 S4 — DESI/Legacy native survey adapters

Status: **ACCEPTED (native-schema adaptation); exact installed-core replay remains an S6 integration gate**

## References

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core runtime:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
surveys repo:     ignaciomagana/darksirens-surveys
accepted S4 head: f0396ca95e08041c045ae16b616640d416142f32
accepted S4 tree: 2dc134386b06c28b70299df50667ac27e8bb0690
```

`darksirens-core` remains frozen. S4 adds no new catalog evaluator, pixelizer,
completion model, or inference path. Native survey interpretation stops at the
already-accepted S1 `CatalogRows` seam.

## Scope

S4 adds:

```python
SurveyColumnMap
DESI_LEGACY_RAW_COLUMNS
rows_from_columns(...)
desi_legacy_rows(...)
load_desi_legacy_hdf5(...)
```

The pinned DESI/Legacy raw-table contract is:

```text
TARGET_RA, TARGET_DEC   degrees
Z, ZERR                 redshift and uncertainty
WEIGHT                  legacy catalog/host weight column

optional:
APP_MAG   -> gal_app_mag
STRATUM   -> gal_stratum
LOGMSTAR  -> mark_logmstar
LOGSSFR   -> mark_logssfr
LOGZ      -> mark_metallicity
GR_COLOR  -> mark_color
```

After adaptation, callers must use S1:

```python
rows = load_desi_legacy_hdf5(...)
catalog = pixelate_catalog(rows, nside=..., z_depth=...)
write_catalog(catalog, ...)
```

There is no second writer or survey-specific pixelizer.

## Scientific firewall

The adapter deliberately does **not** infer survey analysis choices.

### Weights

`weight_mode="column"` copies the declared weight column exactly.
`weight_mode="unity"` uses one for every retained galaxy.

No DESI systematic, FKP, PIP, targeting-completeness, luminosity, or
host-property weight is discovered or multiplied automatically. In particular,
the presence of another column such as `WEIGHT_SYS` does not alter the
`CatalogRows.weight` measure.

This is intentional: LSS/systematics weights and astrophysical host weights are
not interchangeable objects and must not be silently conflated at ingestion.

### Quality cuts

No `ZWARN`, `DELTACHI2`, targeting, footprint, magnitude, or redshift-quality
selection is applied implicitly. The adapter accepts only a caller-supplied
boolean `quality_mask`, applies it coherently to every native column, and rejects
integer 0/1 masks rather than silently coercing them.

Survey sample definition therefore remains an explicit upstream scientific
choice rather than hidden adapter behavior.

## Acceptance gate

```text
workflow:  ci
run:       34681814431
job:       103521697860
head:      f0396ca95e08041c045ae16b616640d416142f32
result:    SUCCESS
pytest:    28 passed
firewall:  PASS
```

The accepted exact-head suite replays all S1-S3 tests and adds S4 tests for:

- exact native column mapping and degree -> radian conversion;
- no implicit ZWARN/DELTACHI2 filtering;
- caller-owned boolean quality masks with exact coindexing;
- exact legacy `WEIGHT` copying;
- explicit unity-weight mode;
- no hidden multiplication by `WEIGHT_SYS`;
- generic schemas with required explicit weight policy;
- eager HDF5 loading;
- termination through the S1 pixelizer with identical standardized arrays;
- hard failure on missing required native columns.

## Next slice

S5 owns raw host-property / mark preparation and survey validation utilities.

Keep the boundary narrow:

- construct/clean host-property columns and redshift-centered mark products
  offline;
- add survey validation/reporting that can audit native -> normalized row counts,
  finite-value failures, sky/redshift coverage, and declared weight policy;
- do not move generic runtime marked-host weighting out of core;
- do not add Q/LSS completion or lensing code;
- do not reopen the frozen core.

S6 remains the clean-install and exact cross-private core-consumer integration
freeze for the completed surveys companion.
