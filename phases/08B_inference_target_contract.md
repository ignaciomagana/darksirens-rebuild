# Phase 8B — frozen InferenceTarget contract

Status: **CONTRACT FROZEN; PRODUCTION NOT YET ACCEPTED**

```text
parent:            5256141e00a2d96a72b9cbf2182a77174c8c269e
parent tree:       6252d1725ee07562840f0ce48b0dc6fe90a4aee4
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Purpose

Freeze the smallest one-way sampler-facing core contract required by a future
specialized companion analysis. This slice does not add lensing physics and does
not create a second inference stack.

The already accepted Phase-6 dispatcher needs only:

```text
likelihood callable
labels
lower / upper
prior kinds
joint constraints
sampler options
```

Phase 8B exposes exactly that existing capability.

## Public contract

`ParameterPlan` remains the coordinate container. Its five sampler-facing fields
remain explicit and required:

```python
ParameterPlan(
    labels=...,
    lower=...,
    upper=...,
    prior_kinds=...,
    joint_constraints=...,
)
```

The existing ordinary-analysis metadata fields (`n_cosmology`, `n_population`,
`n_catalog`, `n_angular`, fixed blocks and label blocks) receive neutral defaults
so a companion does not have to fabricate ordinary dark-siren internals merely
to describe a sampler coordinate space. Existing ordinary `ds.model()` plans are
unchanged.

Add one dependency-light target:

```python
InferenceTarget(
    log_likelihood=callable,
    parameters=ParameterPlan(...),
)
```

Construction validates only the stable sampler contract: callable likelihood,
consistent coordinate lengths, unique labels, finite ordered bounds, and valid
joint-constraint indices. It does not understand specialized physics.

## Execution seam

Use the existing public `ds.infer()` rather than adding `run_target`, a plugin
registry, or another sampler API.

```python
result = ds.infer(target, sampler="tinyns", ...)
```

For an `InferenceTarget`:

- `events` and `injections` are omitted;
- supplying either store is an error rather than being silently ignored;
- core constructs the accepted prior transform from the target plan;
- core delegates directly to the accepted Phase-6 `run_sampler`;
- zero-free exact evidence remains before sampler-name validation/backend import.

For an ordinary `Analysis`, the existing call remains unchanged:

```python
result = ds.infer(
    analysis,
    events=events,
    injections=injections,
    sampler="tinyns",
)
```

Ordinary analyses still require both stores and still bind through
`bind_analysis()` before execution.

## Public exposure

Expose `ParameterPlan` and `InferenceTarget` lazily at package root. Merely
`import darksirens` must still leave JAX, HDF5, sampler backends and optional GP
packages unloaded.

## Non-goals

Phase 8B must not add:

- lensing classes, cluster state, partitions or marks;
- LSS/redshift extension state;
- callbacks discovered by name;
- entry points or generic plugin registration;
- a new result/checkpoint format;
- a new prior-transform implementation;
- a new sampler dispatcher.

## Acceptance

Dedicated exact-head tests must prove:

1. an external-style five-field `ParameterPlan` can construct an
   `InferenceTarget` without ordinary-analysis metadata;
2. target inference delegates the exact target likelihood and parameter plan to
   the accepted prior/sampler stack;
3. target inference never imports/calls `bind_analysis`;
4. passing GW stores with a target is rejected;
5. ordinary `ds.infer(Analysis, events=..., injections=...)` behavior and
   delegation are unchanged;
6. a zero-parameter target with an intentionally unknown sampler returns exact
   evidence before sampler validation or backend import;
7. package-root import remains dependency-light;
8. the Phase-8 broad regression and companion-import firewall pass on the same
   exact head.

No Phase 8C production change starts until this contract is accepted.
