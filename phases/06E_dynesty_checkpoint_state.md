# Phase 6E checkpoint — dynesty state-only checkpoint serialization

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only. Production implementation must not begin until the
preceding Phase 6D exact-head acceptance gate is green.

## Scope

6E reconstructs only the dynesty checkpoint state serialization seam from the
backend-specific tail of pinned `darksirens/inference/checkpointing.py`:

```text
_DetachedCallable
_DETACHED
save_dynesty_checkpoint
install_dynesty_checkpointing
restore_dynesty_sampler
rebind_dynesty_callables
```

The already accepted 6B planning contract remains unchanged.

## Why this is separate

Dynesty pickles the sampler object, including its likelihood and prior-transform
callables. In darksirens those callables may be local closures over JAX-compiled
functions and large device-resident state, so serializing them is invalid or
needlessly huge. Frozen legacy checkpoints only sampler state by temporarily
replacing both live callables with a module-level pickleable placeholder.

This is a backend adapter primitive, not the full sampler runner.

## Frozen semantics

`_DetachedCallable.__call__` always raises the frozen defensive `RuntimeError`
explaining that the checkpoint contains state only and must be rebound before
running.

`save_dynesty_checkpoint(sampler, fname)`:

1. lazily imports `dynesty.utils.save_sampler`;
2. saves references to `sampler.loglikelihood.loglikelihood` and
   `sampler.prior_transform`;
3. removes an instance-level `sampler.__dict__["save"]` override before
   serialization, remembering it if present;
4. installs the same module-level `_DETACHED` object in both callable slots;
5. calls `save_sampler(sampler, fname)`;
6. in `finally`, restores the original likelihood, prior transform, and any
   removed instance-level save override exactly.

Restoration in `finally` is load-bearing: a failed checkpoint write must not
leave the live sampler detached.

`install_dynesty_checkpointing(sampler)`:

- installs an instance method named `save` with `types.MethodType`;
- that method routes to `save_dynesty_checkpoint(self, fname)`;
- returns the same sampler object.

`restore_dynesty_sampler(path, loglike, prior_transform)`:

- lazily imports `dynesty.NestedSampler`;
- restores sampler state through `NestedSampler.restore(path)`;
- calls `rebind_dynesty_callables` with the caller-supplied live functions;
- returns the restored sampler.

`rebind_dynesty_callables` writes the live likelihood back to
`sampler.loglikelihood.loglikelihood`, writes the live prior transform to
`sampler.prior_transform`, and returns the same sampler.

## Explicit non-scope

Do not port in 6E:

```text
run_sampler
_make_dynesty_ptform
nested-sampler preflight
seed / rstate construction
nlive / dlogz / maxcall policy
posterior resampling
dead-point/result normalization
dynesty diagnostics/plotting
TinyNS configuration or runtime
NumPyro runtime
CLI registration
```

A later sampler-adapter subphase will compose this primitive with the accepted
6B plan and 6D prior transform.

## Dependency boundary

`checkpointing.py` must remain importable with no dynesty installed. Dynesty is
imported only inside the save/restore calls. The module must not acquire JAX,
NumPyro, TinyNS, CLI, survey, LSS, lensing, sky, or HEALPix imports.

## Acceptance

Focused tests and a separate-process legacy/candidate probe should use a minimal
fake dynesty module/sampler so the primitive itself is isolated from dynesty
version/runtime behavior. They must establish exact behavior for:

```text
placeholder defensive error text
save sees both callable slots detached
instance save override is absent during serialization
successful save restores all live state
failed save still restores all live state
no original instance save override remains absent afterward
install hook is a bound method and returns same sampler
installed hook routes through state-only save
rebind returns same sampler and replaces both callables
restore calls NestedSampler.restore(path), then rebinds supplied functions
module import does not load dynesty or other sampler/plugin/runtime packages
```

The parity probe compares deterministic structural behavior and frozen exception
messages exactly. No scientific/numerical tolerance is involved. All accepted
6A–6D gates and preserved Phase-5 parity must remain green.
