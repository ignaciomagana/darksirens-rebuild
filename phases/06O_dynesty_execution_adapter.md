# Phase 6O checkpoint — Dynesty execution adapter

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   39d4e36a8d5d3aa347761a9134e0c7c835cdb565
accepted 6O head:  28c5f06ad0cc40d8fdbb587bcaa3e98dd89089b4
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6O extracts the Dynesty execution core from the frozen `run_sampler` branch while deliberately leaving periodic plotting diagnostics for a later small slice.

Candidate surface:

```text
src/darksirens/inference/dynesty_adapter.py::run_dynesty
```

Frozen contract: lazy Dynesty/JAX/checkpoint/transform-dispatch imports; tracked finite-likelihood setup wrapper; accepted 6F prior-transform dispatch; accepted 6B/6E fresh/resume checkpoint behavior; deterministic fresh RNG and checkpoint-carried resumed RNG; exact `run_nested` kwargs; robust log-weight normalization; `resample_equal(..., rstate=dynesty_rstate)`; accepted 6I dead-point packaging; final evidence/error; `nlive_actual` and prior-transform-dispatch provenance. `dynesty_diagnostics=True` is explicitly deferred rather than silently ignored.

## Acceptance

```text
dedicated 6O gate: 34571461016 / 103174270237 SUCCESS
historical gate:   34571460958 / 103174269936 SUCCESS
runtime guards:    34571460969 / 103174269973 SUCCESS
```

The dedicated gate passed focused tests, lazy dependency guards, frozen legacy execution probing, reconstructed execution probing, and exact parity. The broad gate passed the full reconstructed suite, exact 6A–6F historical parity, pinned/reconstructed Phase-5 fixtures, and preserved Phase-5 scientific parity. 6I–6N dedicated gates also reran green at the 6O head.

## Next

Proceed to 6P: isolate Dynesty periodic diagnostic plotting/thread orchestration as a separate optional helper and then wire it into the accepted 6O adapter without changing sampling semantics.
