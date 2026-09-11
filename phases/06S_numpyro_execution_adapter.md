# Phase 6S — NumPyro execution adapter

## Status

ACCEPTED

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted head:     b620601e1a0cc776f7d9090c866e299f2138fbff
```

## Scope

This slice reconstructs only the frozen NumPyro/NUTS execution path that follows the accepted 6Q static contract and 6R initialization/gradient preflight.

Included:

- lazy JAX and NumPyro imports on the execution path only;
- frozen prior-site construction for uniform, truncated-normal, transformed log-normal, and beta priors;
- dependent `conditional_upper` site ordering after all unconditioned sites;
- exact NUTS kernel arguments and `init_to_value` initialization;
- exact MCMC warmup/sample/chain/chain-method/progress wiring;
- frozen PRNG seed construction;
- exact execution stdout;
- posterior stacking in label order;
- sequential `jax.lax.map` likelihood recovery when `log_likelihood` is not already present;
- frozen divergence, acceptance, leapfrog-step, and max-tree-depth diagnostics;
- standardized result mapping with `logZ=None` and `logZerr=None`.

Excluded deliberately:

- top-level sampler selection/orchestration;
- nested-sampler preflight and resume policy;
- TinyNS and Dynesty implementation changes;
- Phase-7 public API work.

Those orchestration concerns belong to the following 6T slice.

## Production files

```text
src/darksirens/inference/numpyro_adapter.py
tests/test_numpyro_adapter.py
tools/probe_numpyro_adapter.py
.github/workflows/phase6s-numpyro-adapter.yml
```

The production adapter was unchanged after its initial implementation commit. Two subsequent commits corrected only test/probe expectations: JAX/NumPy representation fidelity and primitive JSON serialization in the frozen-behavior harness.

## Acceptance gates

```text
dedicated gate:  34589903572 / 103232549996 SUCCESS
historical gate: 34589903506 / 103232549931 SUCCESS
runtime guards:  34589903512 / 103232549984 SUCCESS
```

The dedicated gate checks focused tests, lazy JAX/NumPyro import boundaries, AST-extracted frozen legacy execution, reconstructed execution, and exact legacy/new behavior under a deterministic fake backend.

The broad gate re-runs the full reconstructed suite, exact 6A–6F replay, pinned and reconstructed Phase-5 fixtures, and preserved Phase-5 scientific parity. Runtime guards re-run the accepted 6G/6H contracts and the full reconstructed suite.

## Scientific status

No scientific model, likelihood, prior semantics, population assumption, catalog treatment, or selection treatment changed in this slice. This is a behavior-preserving extraction of the frozen NumPyro execution contract.

## Next slice

Phase 6T: reconstruct only the thin top-level sampler orchestration seam — zero-free short circuit, nested resume/preflight policy, accepted backend delegation, and frozen unknown-sampler behavior — without duplicating backend implementations.
