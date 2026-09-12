# Phase 09 S1 — generic catalog construction

Status: **ACCEPTED (scientific/schema parity); frozen-core cross-repo replay deferred to S6 integration**

## Frozen references

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core consumer:    ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
S0a golden:       references/surveys_s0a_legacy_reference.json
surveys repo:     ignaciomagana/darksirens-surveys
accepted S1 head: 91ed709a47b78182f065be89219d65a7eda2c5dd
accepted S1 tree: ff149a06538fc5846a4317990182c60a4a6a9ab6
```

`darksirens-core` remains frozen. No core production file changed in S1.

## Scope

S1 establishes only the survey-independent construction seam:

```text
normalized per-galaxy rows
    -> validation
    -> HEALPix RING assignment
    -> deterministic within-pixel coindexing
    -> standardized padded catalog arrays
    -> HDF5 writer
```

Public S1 surface:

```python
from darksirens_surveys import CatalogRows, pixelate_catalog, write_catalog
```

No DESI/Legacy/GLADE native columns, depth-map semantics, selection fitting,
LSS, or lensing state enter this slice.

## Legacy parity contract

The candidate is checked against the accepted S0a golden derived from
`darksirens/cli/pixelate.py` at the pinned legacy SHA.

The frozen comparison requires:

- exact RING pixel membership;
- exact `ngals`;
- exact z/dz/weight/property coindexing;
- exact padding (`z=100`, `dz=1`, `w=0`, extras=0);
- optional `z_depth` preservation;
- the same invalid-row boundary for z, dz, weight and non-finite properties;
- exact canonical array hashes after the S0a-approved stable within-pixel
  redshift ordering.

The one intentional determinism normalization remains the S0a decision: legacy
uses unstable `np.argsort(pixel)` for equal-pixel rows, while S1 writes a
canonical `(pixel, z, original-index)` order. This preserves every galaxy and
coindexed value and agrees with the frozen core loader's stable z sorting.

Canonical S0a hashes embedded in the S1 tests:

```text
zgals            4850c2aa6599e33634dbcfb37994f4ca0abc552638a28a5c380e079dec0c2da3
dzgals           00449cc60ac4fbdd0d9584f203f43a35b8b09489d5d0aebbd81fdfb6a5789769
wgals            ff5b17436bdcd694f6a1e96caaff864ae63d4ca894a6326eb6dbfdd0ff629cfa
ngals            9b25c4d5bed699df86a799b8db018b839b742338792588bc452fc34f4b109426
mark_logmstar    ed88c18d1c784045b5f7b82acaa53baaa6718f4b1d7420dd6110756dbd2d67f9
gal_app_mag      5d17ab37aebebdc771109128a68dc34b54b97ea33806989cba89d3636342acc2
gal_stratum      17c2d5e6a33c1d07cd3cb42bccda6677f5643faae29d400f73f6124e3567e4e6
```

## Acceptance evidence

S0 references:

```text
S0a accepted: 34659489558 / 103458826552 SUCCESS
S0b accepted: 34659818827 / selection-reference workflow SUCCESS
```

S1 package CI on exact accepted head:

```text
run:    34660004095
job:    103460346705
head:   91ed709a47b78182f065be89219d65a7eda2c5dd
result: SUCCESS
pytest: 8 passed
firewall: PASS
```

The S1 tests include the exact S0a canonical hashes, standardized writer
surface, optional `z_depth`, real-row validation, non-finite-extra rejection,
DEC bounds, and RA periodicity.

## Cross-private Actions limitation

A control-repo workflow attempted to clone both private sibling repositories
with the rebuild repository's default `GITHUB_TOKEN`:

```text
run: 34660044272
job: 103460469657
result: FAILURE before candidate execution
```

The failure was:

```text
remote: Repository not found.
fatal: repository 'https://github.com/ignaciomagana/darksirens-surveys/' not found
```

This is an Actions authorization limitation, not a production/scientific
failure. The job failed at checkout; no S1 code, golden comparison, or core
consumer was executed. The automatically failing workflow was removed from the
control repository.

The actual clean-install, sibling-package, frozen-`ds.load_catalog()` replay is
therefore retained as an explicit **S6 cross-repository integration gate**. S1
is accepted on its scientific/schema contract now; S6 must still prove the
installed frozen core consumes a surveys-produced catalog in one environment
before the surveys package is finally frozen.

## Next slice

S2: port the depth/mask fraction map semantics already frozen in S0a:

- `SelectionFractionMap`;
- native `f_p = 1 - masked_frac` handling;
- uncovered-pixel convention;
- RING -> NEST child grouping -> RING degradation;
- area/coverage reporting;
- exact S0a native and degraded hashes.

Do not yet port the raw `build_mth_map.py` campaign builder or fix its known
source-count-vs-area caveat. S2 owns reusable map consumption/degradation first.
