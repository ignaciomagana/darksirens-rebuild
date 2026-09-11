# Phase 6F checkpoint — dynesty prior-transform dispatch

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
6E accepted:       fe845dcc87787d19c69bf30a89f211d9de68be03
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

## Scope

6F reconstructs only the dynesty-facing prior-transform dispatch wrapper from
pinned `darksirens/inference/sampling.py`:

```text
_make_dynesty_ptform(prior_transform, ndims, n_probe=512, mode="auto")
```

It consumes the `host_native` and `prefer_jit` flags established by accepted 6D
`make_prior_transform`. It does not run dynesty.

Candidate ownership is `darksirens.inference.dynesty_transform`; the legacy
`sampling.py` monolith is not recreated.

## Frozen dispatch semantics

Accepted modes are exactly `auto` and `eager`. Any other mode raises the frozen
`ValueError` naming `prior_transform_dispatch`.

`mode="eager"` always evaluates
`np.asarray(prior_transform(jnp.asarray(u)))` and announces/records
`eager-forced`.

If `prior_transform.host_native` is true under `auto`, dynesty's NumPy cube is
handed directly to the transform and only the result is converted with
`np.asarray`; dispatch is `host`.

If `prior_transform.prefer_jit` is true, the wrapper:

1. owns an independent `np.random.default_rng(0xB17C0DE)` probe stream;
2. constructs `jax.jit(prior_transform)`;
3. prefers one batched eager reference when the returned shape matches the cube;
4. otherwise restricts to `min(32, n_probe)` rows and builds the eager reference
   row by row;
5. compares compiled per-row outputs with `np.array_equal`;
6. uses compiled dispatch only when every row is bit-identical.

Exact compilation is labelled `jit`; numerical drift falls back to
`eager-not-bit-identical`; compilation/probe failure falls back to
`eager-jit-unavailable`. An unflagged transform remains `eager`.

Every choice is printed in the frozen
`"  [i] dynesty prior transform: <dispatch> -- <detail>"` form and exposed as
the wrapper's `.dispatch` attribute.

## Explicit non-scope

6F does not port `run_sampler`, NestedSampler construction/rstate, checkpoint
plan composition, nested-sampler preflight, nlive/dlogz/maxcall policy,
posterior resampling, result normalization, diagnostics, TinyNS, NumPyro, or
CLI assembly.

## Dependency boundary

The adapter may depend on NumPy/JAX and the reconstructed transform contract. It
does not import dynesty, TinyNS, NumPyro, CLI, surveys, LSS, lensing, sky, or
HEALPix. Dynesty remains optional and absent from this module.

## Acceptance

Accepted at exact core head:

```text
05e7c339f190a04e0b92d40c16119e5bda56ef08
```

Workflow:

```text
run:    34551503882
job:    103115199277
result: SUCCESS
```

Results:

```text
6A result-artifact tests:                10 passed
6B checkpoint-plan tests:                36 passed
6C1 fingerprint-gate tests:              15 passed
6D prior-transform tests:                13 passed
6E dynesty checkpoint-state tests:        8 passed
6F dynesty transform-dispatch tests:     10 passed
full reconstructed suite:               343 passed, 1 regeneration-only skip
portable dependency audit:               PASS
6A separate-process parity:              exact
6B separate-process parity:              exact
6C1 separate-process parity:             exact
6D prior-transform parity:               bit-exact
6E dynesty checkpoint-state parity:      exact
6F dynesty transform-dispatch parity:    exact
preserved Phase-5 parity:                exact, max_abs=max_rel=0
comparison for Phase-5 probes:           rtol=1e-12, atol=0
```

The final head commit adds explicit coverage of the row-wise eager-reference
fallback used when a preferred-JIT transform cannot produce the expected batched
probe shape. No scientific source or tolerance changed in that final correction.
The probe stream remains independent of NumPy's global RNG and therefore of the
sampler RNG lineage.

## Next

Proceed to Phase 6G: reconstruct only the nested-sampler finite-logL preflight
shared by fresh dynesty/TinyNS runs. Preserve the frozen independent RNG,
early-stop rule, fail/warn thresholds and messages. Resume orchestration,
sampler construction, TinyNS configuration/runtime, NumPyro, diagnostics and
CLI remain outside that slice.
