# Phase 6I checkpoint — dead-point packaging

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
core main/base:    86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
accepted 6I head:  0084e3b7c5cba14d8ac85528ce18185941e46c05
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6I reconstructs only the backend-independent conversion of nested-sampler
retired-point arrays into the durable dead-point record. It does not run a
sampler, write HDF5, or import dynesty/tinyns/JAX.

## Frozen behavior

Pinned legacy source:

```text
darksirens/inference/sampling.py::_dead_point_block
```

Candidate surface:

```text
src/darksirens/inference/nested_output.py::package_dead_points
```

The contract is:

- absent `logl` or `logwt` -> `None`, no warning;
- both arrays are converted to float and flattened;
- empty or shape-mismatched arrays -> `None` with the frozen warning text;
- conversion `TypeError`/`ValueError` -> `None` with the frozen warning text;
- valid output contains `logl`, `logwt`, and integer `n_dead`;
- `n_live` is included only when supplied.

This is the sampler-output record needed for nested-evidence diagnostics. It is
not the equal-weight posterior sample table.

## Implementation / ownership

```text
src/darksirens/inference/nested_output.py
tests/test_nested_output.py
tools/probe_dead_point_block.py
.github/workflows/phase6i-dead-point-packaging.yml
```

`nested_output.py` is NumPy-only and has no sampler, JAX, survey, LSS, lensing,
HEALPix, or CLI dependency.

The legacy side of the final parity probe AST-extracts and executes exactly the
frozen `_dead_point_block` function definition from the pinned source file. This
is intentional: importing the legacy `sampling.py` monolith pulls unrelated
JAX/checkpoint/HDF5 modules before reaching this pure helper and would make the
probe depend on packages outside the seam being reconstructed.

## Harness corrections before acceptance

Two non-scientific harness attempts were rejected before acceptance:

1. importing the frozen legacy monolith under the minimal environment failed on
   its unrelated JAX import;
2. adding JAX exposed the next unrelated monolith import (`h5py`).

The final probe therefore executes the exact frozen function body directly.
Candidate source and frozen semantics were not changed, and no tolerance was
introduced.

## Acceptance

Dedicated 6I gate:

```text
workflow run: 34560606167
job:          103142368277
result:       SUCCESS
focused 6I tests: 5 passed
legacy/new dead-point behavior: EXACT
portable dependency/light-import audit: PASS
```

Broad exact-head Phase-6 gate:

```text
workflow run: 34560606182
job:          103142368473
result:       SUCCESS
full reconstructed suite: 362 passed, 1 regen-only skip
6A result-artifact parity: EXACT
6B checkpoint-plan parity: EXACT
6C1 fingerprint-gate parity: EXACT
6D prior-transform parity: BIT-EXACT
6E dynesty checkpoint-state parity: EXACT
6F dynesty transform-dispatch parity: EXACT
```

Runtime-guard exact-head gate:

```text
workflow run: 34560606263
job:          103142368451
result:       SUCCESS
6G nested-preflight parity: EXACT
6H zero-free exact-evidence parity: EXACT
```

Preserved Phase-5 scientific tail at the accepted 6I head:

```text
catalog kernel:      max_abs=max_rel=0
completeness:        max_abs=max_rel=0
ordinary likelihood:max_abs=max_rel=0
marked likelihood:  max_abs=max_rel=0
selection runtime:  max_abs=max_rel=0
rtol: 1e-12
atol: 0
```

## Next

Proceed to 6J: additive HDF5 persistence of a valid dead-point block
(`logl_dead`, `logwt_dead`, `n_dead`, optional `n_live`, and the explicit
non-row-alignment semantics). Keep generic result atomicity from 6A unchanged;
do not port the legacy `save_results_hdf5` monolith wholesale.
