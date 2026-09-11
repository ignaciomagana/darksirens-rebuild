# Phase 6N checkpoint — TinyNS execution adapter

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   cb74900cff9be07049243548d72eef5e5e77bfaf
accepted 6N head:  39d4e36a8d5d3aa347761a9134e0c7c835cdb565
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6N extracts only TinyNS backend execution from frozen `run_sampler`, reusing accepted configuration, checkpoint, dead-point, and diagnostic seams.

Frozen contract: JAX/TinyNS load only on execution; likelihood/prior wrappers preserve JAX convention; seed is split before sampling into independent run/resample streams; fresh/resume routing and checkpoint-path precedence are exact; checkpoint planning is lazy so HDF5 is not imported on adapter import; output contains equal-weight samples, evidence/error, dead points, raw diagnostics/summary when available, normalized diagnostics, and frozen diagnostic stdout.

Dedicated gate: `34570968708 / 103172778145` SUCCESS. Broad historical gate: `34570968720 / 103172778202` SUCCESS. Runtime guards: `34570968671 / 103172778199` SUCCESS. The broad gate preserved full Phase-5 scientific parity.

## Next

6O extracts Dynesty execution with periodic plotting diagnostics deliberately left for a separate later slice.
