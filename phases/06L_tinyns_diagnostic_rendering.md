# Phase 6L checkpoint — TinyNS diagnostic rendering

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   ffe82c8e7948bb0f7b8d0ad3d224037cd702d75d
accepted 6L head:  39d9ab8aef7b0b4e0847ce4e9894a6a2a8985087
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6L reconstructs only the frozen stdout renderer for an already-normalized TinyNS diagnostic dictionary.

Candidate surface:

```text
src/darksirens/inference/tinyns_output.py::print_tinyns_diagnostics
```

Frozen contract: empty input prints nothing; fixed header and field order; lower-case `true`/`false` success; boolean values as `yes`/`no`; frozen `:.6g` float formatting; absent values omitted; wall-time ` s` suffix only; no eager TinyNS/JAX import.

Exact legacy/new stdout behavior and the light-import guard remained green through the accepted 6O head.

## Next

6M reconstructs TinyNS runtime configuration resolution and validation without CLI registration or backend execution.
