# Phase 8C — host-density extension seam

Status: **ACCEPTED**

```text
parent:            2e98ca1f1a67cf688f8da8444c3747d446a4e91d
parent tree:       a893564f982aaa1174b41367927c2708148fd2b6
accepted head:     875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2
accepted tree:     1219bba07d3327c83da0164602e60abe8083ba0b
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Purpose

Phase 8C freezes the smallest explicit one-way redshift/host-density interface
required by a future `darksirens-lss` package. It implements no LSS physics and
adds no second hierarchical likelihood engine.

The accepted core arithmetic remains in the ordinary hierarchical reducer:
population weighting, detector/source-frame Jacobian, angular weighting, PE
reduction, selection integration, effective-sample-size and likelihood-variance
guards. Phase 8C leaves that reducer unchanged and adds only an adapter around
it.

## Accepted extension-side ownership

A companion owns construction of its redshift/host-density state, latent fields,
count data, tables or tracer objects, pixel frame, extension parameter block,
and specialized provenance/diagnostics. Core treats all extension state as
opaque and contains no `Q_LSS`, tracer, latent-field, multitracer, survey-schema,
or companion-package knowledge.

Advanced extension authors may construct pixelized `GWEvent` objects through the
already public `darksirens.gw.make_gw_event` surface. Ordinary users continue to
use `ds.load_events` / `ds.load_injections`.

## `RedshiftModel` protocol

The explicit protocol is:

```python
class RedshiftModel(Protocol):
    def parameter_spec(self) -> ParameterPlan: ...

    def log_density(
        self,
        z,
        pixel,
        cosmology,
        parameters,
        state,
    ): ...

    def log_auxiliary_likelihood(
        self,
        parameters,
        state,
    ): ...
```

`parameter_spec()` returns only the extension block. `log_density` is used for
PE and selection with their respective opaque states. The auxiliary term is
scalar and is evaluated exactly once per full hierarchical likelihood. No model
name registry or plugin discovery was introduced.

## Parameter-plan composition

`combine_parameter_plans(*plans)` now concatenates sampler-facing labels, bounds
and prior kinds, offsets joint-constraint indices, rejects duplicate labels, and
returns a neutral sampler-facing `ParameterPlan`. This is reusable core
parameter/prior assembly, not an extension registry.

## Generic host-density likelihood wrapper

`host_density_log_likelihood(...)` creates only the two redshift-density
callables expected by the accepted ordinary reducer:

```text
PE        -> redshift_model.log_density(..., pe_state)
selection -> redshift_model.log_density(..., selection_state)
```

It then delegates to the unchanged ordinary reducer, evaluates
`log_auxiliary_likelihood` once, and adds it once. Diagnostic mode preserves the
ordinary fixed-theta pieces and adds one explicit
`log_auxiliary_likelihood` field.

## Target builder

`make_host_density_target(...) -> InferenceTarget` requires a catalog-free
`SpectralRedshift` base analysis. The base contributes the already-frozen
cosmology, population and angular coordinates; the extension contributes its
own parameter block afterward. The builder decodes only the base block, treats
extension state as opaque, and returns the accepted Phase-8B `InferenceTarget`
for execution through `ds.infer()`.

No catalog/completeness marker, GW store loader, staged survey loader, LSS class,
or sampler backend is reconstructed here.

## Validation

Dedicated Phase 8C gate on the exact accepted head:

```text
workflow: 34636321077
job:      103384995159
result:   SUCCESS
```

The focused fixture uses a fake external model whose redshift density is exactly
the core normalized comoving-volume prior. It verifies that the generic
host-density wrapper reproduces the accepted spectral-siren likelihood at fixed
coordinates, routes PE/selection states independently, adds one sampled
auxiliary scalar exactly once, reports that term separately, offsets joint
constraints correctly, rejects duplicate labels/catalog-bearing bases, and
preserves non-isotropic angular composition.

Phase 8B replay on the same exact head:

```text
workflow: 34636321027
job:      103384994787
result:   SUCCESS
```

Phase 8A/frozen bright parity replay on the same exact head:

```text
workflow: 34636321033
job:      103384994066
result:   SUCCESS
```

Phase-8 broad regression on the same exact head:

```text
workflow: 34636321017
job:      103384994129
result:   SUCCESS
suite:    534 passed, 1 skipped
```

The single skip is the existing opt-in population-registry golden regeneration
test. The same broad job passed the core -> companion import firewall.

## Verdict

Phase 8C is accepted at
`875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2` / tree
`1219bba07d3327c83da0164602e60abe8083ba0b`.

The only remaining core production slice is **8D: final install, public API,
documentation, examples, dependency and freeze audit**, using this exact head as
its parent. No companion repository starts before 8D is accepted and Phase 8 is
integrated into `main`.
