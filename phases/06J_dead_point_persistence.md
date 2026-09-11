# Phase 6J checkpoint — dead-point HDF5 persistence

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   0084e3b7c5cba14d8ac85528ce18185941e46c05
accepted 6J head:  0373cc9055552dc003dd569b0dc10c515c04c4fe
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6J reconstructs only additive persistence of the already-standardized nested
sampler dead-point record. It does not port the legacy `save_results_hdf5`
monolith, sampler execution, CLI metadata, sidecars, or plotting.

## Frozen behavior

Pinned legacy source:

```text
darksirens/io/results.py::DEAD_POINT_SEMANTICS
darksirens/io/results.py::write_dead_point_datasets
```

Candidate surface:

```text
src/darksirens/io/results.py::DEAD_POINT_SEMANTICS
src/darksirens/io/results.py::write_dead_point_datasets
```

The contract is:

- missing/falsey `results['dead_points']` writes nothing and returns `False`;
- `logl` and `logwt` are converted to float arrays;
- only non-empty, one-dimensional, equal-shape arrays are persisted;
- datasets are named `logl_dead` and `logwt_dead`;
- `n_dead` is derived from the written array length, not trusted from input;
- `n_live` is written only when supplied;
- the exact dead-point semantics string explicitly states that dead points are
  NOT row-aligned with the equal-weight posterior `samples` table;
- caller dataset kwargs are forwarded to both arrays;
- existing posterior datasets are untouched.

## Implementation / ownership

```text
src/darksirens/io/results.py
tests/test_dead_point_persistence.py
tools/probe_dead_point_persistence.py
.github/workflows/phase6j-dead-point-persistence.yml
```

The generic Phase-6A atomic publication/completion protocol remains unchanged.
The legacy parity probe AST-extracts only the frozen semantics constant and
writer definition from the pinned source, avoiding unrelated legacy result/CLI
imports.

## Acceptance

Dedicated 6J gate:

```text
workflow run: 34561210994
job:          103144139413
result:       SUCCESS
focused 6J tests: 6 passed
legacy/new HDF5 structure + values + attrs: EXACT
portable dependency/light-import audit: PASS
```

Broad exact-head Phase-6 gate:

```text
workflow run: 34561210794
job:          103144138884
result:       SUCCESS
full reconstructed suite: 368 passed, 1 regen-only skip
6A result-artifact parity: EXACT
6B checkpoint-plan parity: EXACT
6C1 fingerprint-gate parity: EXACT
6D prior-transform parity: BIT-EXACT
6E dynesty checkpoint-state parity: EXACT
6F dynesty transform-dispatch parity: EXACT
```

Runtime guard exact-head gate:

```text
workflow run: 34561210855
job:          103144138824
result:       SUCCESS
6G nested-preflight parity: EXACT
6H zero-free exact-evidence parity: EXACT
```

Phase 6I also reran successfully at the 6J head:

```text
workflow run: 34561210788
job:          103144138719
result:       SUCCESS
```

Preserved Phase-5 scientific tail at the accepted 6J head:

```text
catalog kernel:       max_abs=max_rel=0
completeness:         max_abs=max_rel=0
ordinary likelihood: max_abs=max_rel=0
marked likelihood:   max_abs=max_rel=0
selection runtime:   max_abs=max_rel=0
rtol: 1e-12
atol: 0
```

## Next

Proceed to 6K: normalize TinyNS runtime diagnostics into a backend-independent,
JSON-safe dictionary. Reconstruct only `_TINYNS_DIAGNOSTIC_FIELDS`, JSON-safe
value conversion, defensive mapping access, and derived scalar rates. Keep
TinyNS execution, diagnostic printing, HDF5 decoration, and JSON sidecars out of
this slice.
