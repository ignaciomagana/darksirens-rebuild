# Phase 6F checkpoint — dynesty prior-transform dispatch

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only. Production implementation must not begin until the
preceding Phase 6E exact-head gate is accepted.

## Scope

6F reconstructs only the dynesty-facing prior-transform dispatch wrapper from
pinned `darksirens/inference/sampling.py`:

```text
_make_dynesty_ptform(prior_transform, ndims, n_probe=512, mode="auto")
```

It consumes the `host_native` and `prefer_jit` flags already established by the
accepted 6D `make_prior_transform`. It does not run dynesty.

A dedicated candidate module should own this adapter rather than recreating the
legacy `sampling.py` monolith.

## Frozen dispatch semantics

Accepted modes are exactly:

```text
auto
eager
```

Any other mode raises the frozen `ValueError` naming
`prior_transform_dispatch`.

### Forced eager

`mode="eager"` always evaluates:

```text
np.asarray(prior_transform(jnp.asarray(u)))
```

and labels/announces the wrapper as:

```text
eager-forced
```

This is the reproducibility escape hatch for runs predating fast dispatch.

### Host-native

If `prior_transform.host_native` is true under `mode="auto"`, dynesty's NumPy
cube is handed directly to the transform and only the result is passed through
`np.asarray`. No JAX array conversion occurs. The wrapper is labelled/announced:

```text
host
```

### Prefer-JIT

If `prior_transform.prefer_jit` is true:

1. construct an independent deterministic probe cube with
   `np.random.default_rng(0xB17C0DE)`;
2. compile `jax.jit(prior_transform)`;
3. prefer one batched eager reference call when it returns the expected cube
   shape;
4. otherwise restrict the probe to `min(32, n_probe)` rows and build the eager
   reference per row;
5. compare compiled per-row outputs to the eager reference with
   `np.array_equal` — bit identity, not tolerance;
6. use the compiled transform only if every probe row is exactly equal.

Accepted compiled dispatch is labelled:

```text
jit
```

If compilation succeeds but values differ, fall back to the eager JAX spelling
and label:

```text
eager-not-bit-identical
```

If compilation/probing raises, fall back to eager and label:

```text
eager-jit-unavailable
```

A JIT failure is a performance issue only; it must not abort inference.

### Unflagged transform

A transform with neither fast flag uses the eager JAX spelling and is labelled:

```text
eager
```

This includes all-uniform transforms with joint constraints and arbitrary
caller-supplied callables.

## Provenance/visibility

Every selected convention is printed using the frozen
`"  [i] dynesty prior transform: <dispatch> -- <detail>"` form and stored as the
wrapper's `.dispatch` attribute. Later sampler/result integration may persist
that attribute, but persistence is not part of 6F.

The JIT probe must never consume or mutate dynesty's sampler RNG stream; it owns
its independent `default_rng` above.

## Explicit non-scope

Do not port in 6F:

```text
run_sampler
NestedSampler construction/rstate
checkpoint plan composition
nested-sampler preflight
nlive/dlogz/maxcall policy
posterior resampling
dead-point/result normalization
diagnostics/plotting
TinyNS
NumPyro
CLI
```

## Dependency boundary

The adapter may depend on NumPy/JAX and the already reconstructed 6D transform
contract. It must not import dynesty itself, TinyNS, NumPyro, CLI, surveys, LSS,
lensing, sky, or HEALPix.

## Acceptance

Focused tests plus separate-process legacy/candidate probes must pin:

```text
invalid mode error text
forced eager values + dispatch label + announcement
host-native values + dispatch label + announcement
prefer_jit exact transform -> jit
prefer_jit value-moving transform -> eager-not-bit-identical
prefer_jit untraceable transform -> eager-jit-unavailable
unflagged transform -> eager
actual 6D uniform transform -> host and exact old eager values
actual 6D non-uniform transform -> whichever frozen live-backend decision occurs,
                                  with values identical to eager
probe RNG independence from NumPy global RNG / sampler state
```

No tolerance is allowed for transformed parameter values. All accepted 6A–6E
gates and preserved Phase-5 parity must remain green.
