# Phase 6M checkpoint — TinyNS configuration resolution

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   39d9ab8aef7b0b4e0847ce4e9894a6a2a8985087
accepted 6M head:  cb74900cff9be07049243548d72eef5e5e77bfaf
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6M reconstructs the standalone TinyNS runtime configuration contract: presets, defaults, explicit overrides, validation, semantic mirroring, and sampler/run kwargs. CLI registration and sampler execution remain outside this slice.

Frozen behavior includes the 10,000-attempt floor `max(10000, walks * max_active_chains)`, strict positive/increasing chain schedules, eager invalid-combination errors, uncapped `maxiter` for `max_samples <= 0`, and stripping checkpoint/progress fields from the semantic fingerprint mirror. Module import requires neither JAX, TinyNS, nor CLI modules.

Dedicated exact-parity and broad historical/scientific gates remained green through the accepted 6O head.

## Next

6N extracts only the TinyNS execution adapter, reusing 6B/6I/6K/6L/6M rather than reopening their contracts.
