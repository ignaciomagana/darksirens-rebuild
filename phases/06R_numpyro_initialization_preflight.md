# Phase 6R — NumPyro initialization and gradient preflight

## Status

ACCEPTED

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted head:     7bab631a786d4ad3a54bc93833157b0f64a046d4
```

## Scope

This slice reconstructs only the frozen NumPyro/NUTS initialization behavior that follows the accepted 6Q static plan and precedes NumPyro kernel/MCMC construction.

Included:

- midpoint likelihood check;
- deterministic seeded finite-point restart search when the midpoint is non-finite;
- selection of the best finite restart under the frozen likelihood ordering;
- exact failure message when no finite start is found;
- `conditional_upper` initial-support repair, strictly inside the dependent support;
- lazy JAX import for the actual preflight;
- likelihood-gradient evaluation at the chosen initial point;
- frozen finite-logL / finite-gradient acceptance check;
- exact per-parameter failure diagnostics, including boundary proximity and finite/NaN/Inf gradient flags.

Excluded deliberately:

- NumPyro prior-site/model construction;
- NUTS kernel construction;
- MCMC execution;
- posterior likelihood recovery;
- sampler-health/result diagnostics.

Those belong to the following execution-adapter slice.

## Production files

```text
src/darksirens/inference/numpyro_init.py
tests/test_numpyro_init.py
tools/probe_numpyro_init.py
.github/workflows/phase6r-numpyro-initialization.yml
```

The module imports neither JAX nor NumPyro at module import time. JAX is loaded only when initialization/preflight is executed; NumPyro remains outside this slice entirely.

## Acceptance gates

```text
dedicated gate:  34580141816 / 103201551957 SUCCESS
historical gate: 34580141630 / 103201551061 SUCCESS
runtime guards:  34580141611 / 103201550056 SUCCESS
```

The dedicated gate checks focused tests, the light-import boundary, frozen legacy behavior extracted from the pinned monolith, reconstructed behavior, and exact legacy/new parity.

The broad historical gate re-runs the complete reconstructed regression suite, exact 6A–6F replay, pinned and reconstructed Phase-5 fixtures, and preserved Phase-5 scientific parity. Runtime guards re-run the accepted 6G/6H contracts and full reconstructed suite.

## Scientific status

No scientific model, likelihood, population assumption, catalog treatment, or selection treatment changed in this slice. This is a behavior-preserving extraction of the frozen NumPyro initialization/preflight contract.

## Next slice

Phase 6S: reconstruct the NumPyro execution adapter only — prior-site/model construction, NUTS/MCMC wiring, post-run likelihood recovery, and frozen sampler-health/result diagnostics — while keeping JAX/NumPyro lazy outside execution paths.
