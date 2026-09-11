# Phase 6G checkpoint — nested-sampler preflight

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
6F accepted:       05e7c339f190a04e0b92d40c16119e5bda56ef08
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

## Scope

6G reconstructs only the finite-logL startup probe used by fresh nested-sampler
runs in pinned `darksirens/inference/sampling.py`:

```text
_nested_sampler_preflight(likelihood, prior_transform, ndims, opts, n_probe=32)
```

Candidate ownership is `darksirens.inference.preflight`. The helper consumes
only the resolved values it needs: likelihood, prior transform, dimension,
seed, nlive, enabled flag and probe count. Resume policy stays outside the
helper for later sampler-runner composition.

## Frozen semantics

When disabled, the helper returns without drawing or evaluating the likelihood.
When enabled it owns

```python
rng = np.random.default_rng(int(seed) ^ 0xC0FFEE)
```

and for each probe evaluates the exact frozen sequence

```python
u = rng.random(ndims)
theta = prior_transform(jnp.asarray(u))
logl = float(np.asarray(likelihood(jnp.asarray(theta))))
```

It stops immediately on the fourth finite likelihood. Zero finite draws raise
the frozen fail-fast `RuntimeError`; one to three finite draws print the frozen
slow-initialization warning; four finite draws need no warning. The finite range,
elapsed-time summary, `ceil(nlive/fraction)` estimate, `nlive==0 -> many`
spelling and selection-guard remedy text are unchanged.

The parity probe fixes `time.perf_counter` identically for legacy and candidate,
so stdout/error text can be compared exactly without changing production timing.

## Ownership / dependency boundary

The module imports NumPy and Python `time` eagerly and JAX only when the probe
is actually called. Importing `darksirens.inference.preflight` therefore remains
light and does not load JAX, dynesty, TinyNS, NumPyro or any companion package.

6G does not port sampler construction, resume/checkpoint orchestration,
dynesty/TinyNS configuration, NumPyro, posterior resampling, dead-point/result
normalization, diagnostics, plotting or CLI assembly.

## Acceptance

Accepted exact core head:

```text
251590e82eb373bace7f1e277805b75423bf4f10
```

6G workflow:

```text
run:    34555353379
job:    103126770107
result: SUCCESS
```

Historical Phase-6 replay at the same head:

```text
run:    34555353322
job:    103126770206
result: SUCCESS
```

Results:

```text
6G focused tests:                         8 passed
full reconstructed suite:               351 passed, 1 regeneration-only skip
6G dependency/light-import audit:        PASS
6G legacy/new separate-process parity:   exact
6A result-artifact parity:               exact
6B checkpoint-plan parity:               exact
6C1 fingerprint-gate parity:             exact
6D prior-transform parity:               bit-exact
6E dynesty checkpoint-state parity:      exact
6F dynesty transform-dispatch parity:    exact
preserved Phase-5 parity:                exact, max_abs=max_rel=0
Phase-5 comparison:                      rtol=1e-12, atol=0
```

The 6F -> 6G production diff is one commit and exactly four files: the new
runtime helper, focused tests, parity probe and dedicated workflow gate. No
previously accepted scientific module changed.

## Next

Proceed to the zero-free-parameter exact-evidence short-circuit as a separate
slice. It is backend-independent and must return before any sampler package,
preflight, checkpoint or backend option is touched. Full dynesty/TinyNS/NumPyro
runner assembly remains later work.
