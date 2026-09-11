# Phase 6K checkpoint — TinyNS diagnostic normalization

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   0373cc9055552dc003dd569b0dc10c515c04c4fe
accepted 6K head:  ffe82c8e7948bb0f7b8d0ad3d224037cd702d75d
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6K reconstructs only backend-independent TinyNS runtime-diagnostic normalization. It does not execute TinyNS, print diagnostics, persist sidecars, or eagerly import TinyNS/JAX.

Candidate surface:

```text
src/darksirens/inference/tinyns_output.py::normalize_tinyns_diagnostics
```

Frozen contract: defensive `diagnostics()` / `summary()` / attribute collection; JSON-safe NumPy/JAX scalar/array/container conversion; derived call/iteration rates and replacement-failure rate only when inputs exist; light import boundary preserved.

Exact-head rerun at the later accepted 6O head remained green. The dedicated 6K workflow and all broad Phase-6/Phase-5 guards passed.

## Next

6L reconstructs only the frozen human-readable TinyNS diagnostic renderer.
