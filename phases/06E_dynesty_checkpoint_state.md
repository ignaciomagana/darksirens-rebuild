# Phase 6E checkpoint — dynesty state-only checkpoint serialization

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
6D accepted:       5edc76c6c055e47a7e041d7f7477e347837f7554
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

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

Candidate ownership is deliberately split into
`darksirens.inference.dynesty_checkpoint` so the accepted 6B planning module
remains backend-independent.

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

`install_dynesty_checkpointing(sampler)` installs a bound instance method that
routes through `save_dynesty_checkpoint` and returns the same sampler.

`restore_dynesty_sampler(path, loglike, prior_transform)` lazily restores through
`dynesty.NestedSampler.restore(path)`, rebinds the caller-supplied live
functions, and returns the restored sampler.

`rebind_dynesty_callables` replaces both callable slots and returns the same
sampler.

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

## Dependency boundary

The dedicated adapter is importable with no dynesty installed. Dynesty is
imported only inside save/restore operations. It does not import JAX, NumPyro,
TinyNS, CLI, surveys, LSS, lensing, sky, or HEALPix.

## Acceptance

Accepted at exact core head:

```text
fe845dcc87787d19c69bf30a89f211d9de68be03
```

Workflow:

```text
run:    34550891118
job:    103113378025
result: SUCCESS
```

Results:

```text
6E focused tests:                 8 passed
full reconstructed suite:        333 passed, 1 regeneration-only skip
portable dependency audit:       PASS
6A separate-process parity:       exact
6B separate-process parity:       exact
6C1 separate-process parity:      exact
6D prior-transform parity:        bit-exact
6E checkpoint-state parity:       exact structural/error behavior
preserved Phase-5 parity:         exact, max_abs=max_rel=0
comparison:                       rtol=1e-12, atol=0
```

The 6E probe used a minimal fake dynesty module on both legacy and candidate
sides. This isolates the actual migration contract: both live callable slots are
detached during serialization, instance save overrides are absent from the
pickle, state is restored on success and failure, the installed bound hook uses
the same protocol, and restored samplers are rebound identically.

No dynesty runtime policy or nested-sampling result behavior was accepted here.

## Next

Proceed to Phase 6F: the dynesty prior-transform dispatch wrapper consuming the
accepted 6D `host_native`/`prefer_jit` contract. Keep full sampler construction,
checkpoint-plan composition, preflight, RNG policy, diagnostics, TinyNS and
NumPyro outside that slice.
