# Phase 6A checkpoint — atomic result artifact / completion semantics

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
accepted 6A head:  194e246666e6901624347d09ec570696f3c62e4d
workflow run:      34534605913
job:               103063178085
result:            SUCCESS
```

Legacy remains read-only. Candidate and legacy behavioral probes run in separate
processes.

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

The exact candidate head `194e246666e6901624347d09ec570696f3c62e4d`
passed the focused 6A contract, the full reconstructed suite, the portable
import/dependency audit, exact separate-process legacy/new artifact behavior,
and the complete preserved Phase-5 parity tail. No comparator or scientific
behavior was changed.

## Scope

6A reconstructs only the portable durability/completion contract that turns a
finished HDF5 result into a trustworthy run artifact.

Frozen source surface from pinned legacy:

```text
darksirens/io/__init__.py
darksirens/io/results.py:
    RESULT_COMPLETE_ATTR
    RESULT_SCHEMA_ATTR
    RESULT_SCHEMA_VERSION
    atomic_result_hdf5
    result_is_complete
```

Frozen reference tests include the LENS-01 cases in
`tests/test_result_atomicity_and_resume_provenance.py`.

## Runtime semantics

1. The final result path is never opened directly for a new write.
2. A sibling `<path>.tmp` is written first, so publication uses same-filesystem
   `os.replace` semantics.
3. The completion marker and schema version are the final HDF5 attributes written
   before close/publication.
4. Any `BaseException` (including `KeyboardInterrupt`/scheduler interruption)
   removes the temporary and leaves the previous final result unchanged.
5. A marked file is complete iff `result_complete` is truthy.
6. Old unmarked archives remain accepted when they contain a samples dataset
   (top-level or `posterior/samples`) plus some metadata (`labels` or any attr).
7. A samples-only truncated unmarked file is incomplete.
8. Missing, unreadable, or non-HDF5 paths are incomplete.

These semantics are load-bearing for automatic checkpoint resume: mere existence
of `results.hdf5` must never suppress recovery after a failed final write.

## Ownership boundary

Core 6A owns only the generic HDF5 artifact protocol above. It does **not** port:

```text
save_results_hdf5
sampler-specific metadata/dead-point decoration
CLI option metadata
sky-prior corrections
fixed-dark-energy CLI metadata
environment/device inspection
survey/LSS/lensing output schemas
```

Those are later explicit consumers or destination-specific layers. The generic
`darksirens.io` package remains JAX-free at import time.

## Implemented surface

```text
src/darksirens/io/__init__.py
src/darksirens/io/results.py
tests/test_result_artifact.py
tools/probe_result_artifact.py
.github/workflows/phase6-inference-io.yml
```

## Acceptance result

```text
focused Phase 6A tests:                    PASS
full reconstructed regression suite:      PASS
portable dependency/light-import audit:   PASS
legacy/new 6A artifact behavior:          EXACT
preserved 5A catalog-kernel parity:       PASS
preserved 5B completeness parity:         PASS
preserved 5C likelihood parity:           PASS
preserved 5D1 marked-host parity:         PASS
preserved 5D2 selection parity:           PASS
historical numerical comparator rtol:     1e-12
historical numerical comparator atol:     0
```

The 6A probe itself is discrete/structural and compares exact JSON behavior;
there is no floating-point tolerance to relax.

## Next

Proceed to Phase 6B, the backend-independent checkpoint/resume planning layer.
Do not migrate `inference/sampling.py`, backend checkpoint serialization,
`loaders.py`, `q_provenance.py`, or the old mega-factory wholesale.
