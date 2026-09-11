# Phase 6H plan — zero-free-parameter exact evidence

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
6G accepted:       251590e82eb373bace7f1e277805b75423bf4f10
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

## Scope

6H reconstructs only the `ndim == 0` short-circuit at the start of frozen
`darksirens.inference.sampling.run_sampler`.

Candidate ownership is `darksirens.inference.run`, with a small helper such as

```text
zero_free_parameter_result(likelihood, ndim)
```

that returns `None` when `ndim != 0` and otherwise returns the exact fixed-point
result. A later sampler runner may call this before any backend/preflight/
checkpoint dispatch.

## Frozen semantics

For zero free dimensions:

```python
log_l_fixed = float(np.asarray(likelihood(jnp.zeros(0))))
```

The likelihood is evaluated exactly once. The unit-cube prior transform is not
called. No sampler option is read and no sampler package is imported.

The exact returned structure is:

```text
samples:        float array with shape (1, 0)
logZ:           log_l_fixed
logZerr:        0.0
log_likelihood: float array [log_l_fixed]
```

This follows directly from the point-mass prior: `Z = L(theta_fixed)`.

The frozen messages are:

```text
[*] 0 free parameters (all blocks fixed) - skipping nested sampling; evidence is exact at the fixed point.
    log Z = log L(fixed point) = <value with .6f>
```

For nonzero dimension the helper must return `None` without evaluating the
likelihood.

## Explicit non-scope

Do not port in 6H:

```text
sampler method dispatch
prior transform dispatch
nested-sampler preflight
resume/checkpoint policy
dynesty/TinyNS/NumPyro construction
RNG policy
posterior resampling
dead-point packaging
diagnostics
CLI
```

## Dependency boundary

`darksirens.inference.run` may import NumPy eagerly and JAX only inside the
zero-dimensional call path. Importing the module itself must not load JAX or any
sampler/backend/plugin. It must not import CLI, surveys, LSS, lensing, legacy
redshift/sky, HEALPix, dynesty, TinyNS or NumPyro.

## Acceptance matrix

Focused tests and separate-process legacy/candidate probes must pin:

```text
ndim > 0 -> None, no likelihood call
ndim == 0 -> exactly one likelihood call on a zero-length JAX array
samples shape/dtype
logZ/logZerr/log_likelihood values and dtypes
exact stdout
prior transform never called on the legacy adapter
method-independent behavior for dynesty/numpyro/tinyns
no sampler backend imported by the short-circuit
non-finite fixed-point values pass through exactly as frozen
```

No numerical tolerance is needed. Accepted 6A–6G gates and all preserved
Phase-5 parity must remain green at the exact 6H head.
