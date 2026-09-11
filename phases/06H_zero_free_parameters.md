# Phase 6H checkpoint — zero-free-parameter exact evidence

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
`darksirens.inference.sampling.run_sampler`. Candidate ownership is
`darksirens.inference.run.zero_free_parameter_result`.

For nonzero dimension the helper returns `None` without evaluating the
likelihood. For zero free dimensions it evaluates exactly once at
`jnp.zeros(0)` and returns the exact point-mass evidence:

```text
samples:        float array with shape (1, 0)
logZ:           log L(fixed point)
logZerr:        0.0
log_likelihood: float array [log L(fixed point)]
```

The unit-cube prior transform is not called. No sampler option is read and no
sampler backend is imported. The two frozen stdout lines, including `.6f`
formatting, are preserved exactly. Non-finite fixed-point likelihood values pass
through exactly as in legacy.

## Ownership / dependency boundary

`darksirens.inference.run` imports NumPy eagerly and JAX only inside the
zero-dimensional call path. Importing the module remains light: no JAX,
dynesty, TinyNS, NumPyro, HEALPix, CLI, survey, LSS, lensing or legacy
redshift/sky module is loaded.

6H does not port sampler dispatch, prior-transform dispatch, preflight,
checkpoint/resume policy, RNG policy, backend construction, posterior
resampling, dead-point packaging, diagnostics or CLI assembly.

## Acceptance

Accepted exact core head:

```text
d1d39019ad2ca3750ef8171d0d451cdc0896adb0
```

Dedicated runtime-guard workflow:

```text
run:    34555964680
job:    103128606105
result: SUCCESS
```

Historical Phase-6 / preserved-Phase-5 replay at the same head:

```text
run:    34555964712
job:    103128605845
result: SUCCESS
```

Results:

```text
6G focused preflight tests:                8 passed
6H focused zero-free tests:                6 passed
full reconstructed suite:                357 passed, 1 regeneration-only skip
6G/6H dependency/light-import audit:      PASS
6G legacy/new preflight parity:           exact
6H legacy/new zero-free parity:           exact
6H method spellings checked:              dynesty, numpyro, tinyns
6A result-artifact parity:                 exact
6B checkpoint-plan parity:                 exact
6C1 fingerprint-gate parity:              exact
6D prior-transform parity:                bit-exact
6E dynesty checkpoint-state parity:       exact
6F dynesty transform-dispatch parity:     exact
preserved Phase-5 parity:                 exact, max_abs=max_rel=0
Phase-5 comparison:                       rtol=1e-12, atol=0
```

The 6G -> 6H scientific diff is one fast-forward commit. It adds only
`inference/run.py`, its focused test/probe, and extends the existing small
runtime-guards workflow. Accepted 6G source is unchanged.

## Next

Inspect the generic nested-sampler dead-point packaging helper as the next
possible portable slice. Do not port a full sampler runner unless that smaller
seam is exhausted and independently accepted.
