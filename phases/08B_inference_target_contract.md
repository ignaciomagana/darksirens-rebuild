# Phase 8B — InferenceTarget sampler seam

Status: **ACCEPTED**

```text
parent:            5256141e00a2d96a72b9cbf2182a77174c8c269e
parent tree:       6252d1725ee07562840f0ce48b0dc6fe90a4aee4
accepted head:     2e98ca1f1a67cf688f8da8444c3747d446a4e91d
accepted tree:     a893564f982aaa1174b41367927c2708148fd2b6
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Purpose

Phase 8B freezes the smallest one-way sampler-facing core contract required by a
future specialized companion analysis. It adds no lensing physics and no second
inference stack.

The accepted Phase-6 dispatcher already needs only:

```text
likelihood callable
labels
lower / upper
prior kinds
joint constraints
sampler options
```

Phase 8B exposes exactly that capability.

## Accepted public contract

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

The ordinary-analysis metadata fields (`n_cosmology`, `n_population`,
`n_catalog`, `n_angular`, fixed blocks and label blocks) now have neutral
defaults. A companion therefore does not fabricate ordinary dark-siren internals
merely to describe a sampler coordinate space. Existing plans produced by
`ds.model()` retain their full metadata and coordinate ordering.

The dependency-light specialized target is:

```python
InferenceTarget(
    log_likelihood=callable,
    parameters=ParameterPlan(...),
)
```

Construction validates only the stable sampler contract: callable likelihood,
consistent coordinate lengths, unique non-empty labels, finite ordered bounds,
and valid joint-constraint indices. It does not understand specialized physics.

## Execution seam

The existing `ds.infer()` is the single public execution surface:

```python
result = ds.infer(target, sampler="tinyns", ...)
```

For an `InferenceTarget`:

- `events` and `injections` are omitted;
- supplying either store is an error rather than being silently ignored;
- `bind_analysis()` is not called;
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

Ordinary analyses still require both stores and bind through `bind_analysis()`.

`ParameterPlan` and `InferenceTarget` are exposed lazily at package root. Merely
`import darksirens` still leaves JAX, HDF5, sampler backends and optional GP
packages unloaded.

## Deliberate non-goals

No lensing classes, cluster state, partitions, LSS state, callback discovery,
entry points, plugin registry, result format, checkpoint format, prior-transform
implementation, or sampler dispatcher was added.

## Exact-head validation

Dedicated Phase 8B gate:

```text
workflow: 34635288617
job:      103381567625
result:   SUCCESS
```

It passed:

- definite-error lint/compile;
- dependency-light package-root exposure of `ParameterPlan` and
  `InferenceTarget`;
- focused target and ordinary-infer contract tests;
- an external-style target smoke test;
- zero-free exact evidence with an intentionally invalid sampler name before
  backend validation/import.

Phase 8A replay on the same exact head:

```text
workflow: 34635288475
job:      103381567028
result:   SUCCESS
```

The frozen bright-siren public path and Phase-5 legacy/candidate bright parity
remain intact.

Phase-8 broad regression on the same exact head:

```text
workflow: 34635288518
job:      103381567351
result:   SUCCESS
suite:    528 passed, 1 skipped
```

The single skip is the existing opt-in population-registry golden regeneration
test. The same broad job passed the core -> companion import firewall.

## Verdict

Phase 8B is accepted at
`2e98ca1f1a67cf688f8da8444c3747d446a4e91d` / tree
`a893564f982aaa1174b41367927c2708148fd2b6`.

The next allowed production slice is **8C: the minimal RedshiftModel /
host-density likelihood seam**, using this accepted head as its parent. No
companion repository or Phase 8D production change starts before 8C is
independently accepted.
