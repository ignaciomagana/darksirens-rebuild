# Phase 6G plan — nested-sampler preflight

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
6F accepted:       05e7c339f190a04e0b92d40c16119e5bda56ef08
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only. Production code starts only from the exact accepted
6F head above.

## Scope

6G reconstructs only the finite-logL startup probe used by fresh nested-sampler
runs in pinned `darksirens/inference/sampling.py`:

```text
_nested_sampler_preflight(likelihood, prior_transform, ndims, opts, n_probe=32)
```

The candidate owns this as a small explicit-data helper in
`darksirens.inference.preflight`, rather than recreating the legacy sampler
monolith. The helper receives the resolved runtime values it actually needs:

```text
likelihood
prior_transform
ndims
seed
nlive
enabled
n_probe
```

The parity probe adapts the frozen legacy `opts` namespace to this explicit
interface. Resume policy is deliberately not hidden inside the helper; a future
sampler runner decides whether a preflight call is appropriate.

## Frozen semantics

When disabled, return immediately without drawing from the prior or evaluating
the likelihood.

For an enabled probe:

```python
rng = np.random.default_rng(int(seed) ^ 0xC0FFEE)
```

For each of at most `n_probe` draws:

```python
u = rng.random(ndims)
theta = prior_transform(jnp.asarray(u))
logl = float(np.asarray(likelihood(jnp.asarray(theta))))
```

Collect finite `logl` values. Stop immediately after the fourth finite value,
because both frozen verdicts are then settled. Thus `n_probed` can be smaller
than `n_probe`.

The summary line is frozen:

```text
[*] preflight: k/N prior draws have finite logL ... [T.TT s]
```

When finite values exist, include the frozen `:.4g` range. With zero finite
values, raise the frozen `RuntimeError` explaining that dynesty/TinyNS would
reject-sample forever, naming the selection-variance/Vitale criteria and the
existing remedies. With one to three finite values, print the frozen non-fatal
slow-initialization warning. Its estimated draw count is
`ceil(nlive / finite_fraction)` when `nlive > 0`, otherwise `many`.

The probe owns its RNG. It must not mutate NumPy's global RNG state and does not
receive or consume a sampler RNG object.

## Timing and parity

Wall time is diagnostic only, but the text is part of frozen behavior. The
separate-process parity probe must patch `time.perf_counter` identically on both
legacy and candidate sides so the emitted stdout can be compared exactly.
Production code continues to use real `time.perf_counter`.

## Explicit non-scope

Do not port in 6G:

```text
run_sampler
resume/checkpoint orchestration
NestedSampler construction or dynesty rstate
TinyNS configuration, construction, run/resume, or PRNG splitting
NumPyro/NUTS preflight or runtime
nlive/dlogz/maxcall policy beyond the warning's resolved nlive integer
posterior resampling
dead-point/result normalization
diagnostics/plotting
selection diagnostic formatter
CLI
```

## Dependency boundary

The helper may import NumPy/JAX and Python `time`. It must not import dynesty,
TinyNS, NumPyro, CLI, surveys, LSS, lensing, legacy redshift/sky namespaces, or
HEALPix.

## Acceptance matrix

Focused tests and separate-process legacy/candidate probes must pin:

```text
disabled probe -> no calls and no output
all -inf -> exact stdout + exact RuntimeError
one finite -> full probe + warning
three finite -> full probe + warning
fourth finite -> early stop at the exact draw where it appears
all finite -> stop after four draws
finite logL range formatting
nlive > 0 estimated initialization draw count
nlive == 0 warning uses "many"
seed XOR 0xC0FFEE draw sequence
NumPy global RNG independence
JAX array conversion on prior-transform and likelihood seams
```

No tolerance is used for structural behavior, messages, RNG draws, or call
counts. Accepted 6A–6F gates and all preserved Phase-5 parity must remain green.
