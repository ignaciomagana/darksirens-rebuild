# Phase 6A checkpoint — atomic result artifact / completion semantics

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only. Candidate and legacy behavioral probes run in separate
processes.

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
`darksirens.io` package must remain JAX-free at import time.

## Acceptance gate

At an exact candidate head:

```text
focused 6A tests                              PASS
BaseException rollback                        PASS
previous-complete-result preservation          PASS
legacy unmarked top-level/grouped layouts      PASS
truncated/non-HDF5/missing rejection           PASS
`import darksirens.io.results` imports no JAX  PASS
full historical reconstructed suite            PASS
all Phase-2..5 permanent parity gates           PASS
separate-process legacy/new 6A behavior probe   exact
```

No tolerance relaxation is applicable: the 6A probe is discrete/structural and
must match exactly.

## Next

Only after 6A acceptance proceed to the semantic checkpoint/resume and run-
fingerprint layer. Do not migrate `inference/sampling.py`, `loaders.py`,
`q_provenance.py`, or the old mega-factory wholesale.
