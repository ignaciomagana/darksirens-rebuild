# Phase 8C — frozen host-density extension contract

Status: **CONTRACT FROZEN; PRODUCTION NOT YET ACCEPTED**

```text
parent:            2e98ca1f1a67cf688f8da8444c3747d446a4e91d
parent tree:       a893564f982aaa1174b41367927c2708148fd2b6
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Purpose

Freeze the smallest explicit one-way redshift/host-density interface required by
a future `darksirens-lss` package. Phase 8C does not implement LSS physics and
does not add a new hierarchical likelihood engine.

The accepted core already contains the needed science arithmetic in the ordinary
hierarchical reducer: population weighting, the detector/source-frame Jacobian,
angular weighting, PE reduction, selection integration, effective-sample-size
and likelihood-variance guards. That arithmetic remains unchanged.

## Extension-side data ownership

A companion owns:

- construction of its redshift/host-density state;
- any latent fields, count data, tables or tracer-specific objects;
- the pixel frame in which that state is defined;
- the extension parameter block;
- all specialized provenance/diagnostics beyond the generic likelihood terms.

Core treats extension state as opaque. It never learns `Q_LSS`, tracer names,
latent fields, multitracer semantics, survey schemas or companion classes.

Advanced extension authors may construct pixelized `GWEvent` objects through the
already public `darksirens.gw.make_gw_event` surface. Ordinary users continue to
use `ds.load_events` / `ds.load_injections` and do not need `GWEvent`.

## `RedshiftModel` protocol

Add one explicit protocol in a specific likelihood namespace, not a plugin
registry:

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

Requirements:

- `parameter_spec()` returns only the extension's sampled coordinates;
- `log_density` is array-capable and returns the log redshift/host density used
  by the existing PE/selection sample weighting;
- PE and selection may receive different opaque state objects;
- `log_auxiliary_likelihood` is evaluated exactly once per full hierarchical
  likelihood, never once per event/sample/selection draw;
- a model with no auxiliary term returns scalar zero.

No registration by model name is added. Core receives the model object directly.

## Parameter-plan composition

Add a small deterministic `combine_parameter_plans(*plans)` helper to the
sampler-facing target module.

It concatenates:

```text
labels
lower / upper
prior kinds
```

and offsets each plan's joint-constraint indices by the preceding block sizes.
Duplicate labels are rejected. The returned plan is sampler-facing and uses
neutral ordinary-analysis metadata, because only its first five fields are
relevant to an `InferenceTarget`.

This is parameter/prior assembly, which is already core-owned. It is not an
extension registry.

## Generic host-density likelihood wrapper

Expose a public wrapper in the likelihood namespace that delegates to the
unchanged ordinary reducer:

```python
host_density_log_likelihood(
    cosmology,
    pop_params,
    redshift_params,
    gw_pe,
    pe_state,
    gw_selection,
    selection_state,
    n_events,
    nsamp,
    n_draw,
    *,
    redshift_model,
    pop_model,
    auxiliary_state=None,
    ... existing population/angular/reduction controls ...,
)
```

The wrapper creates only the two redshift-density callables expected by the
existing ordinary reducer:

```text
PE        -> redshift_model.log_density(..., pe_state)
selection -> redshift_model.log_density(..., selection_state)
```

After the ordinary reducer returns, evaluate
`redshift_model.log_auxiliary_likelihood(redshift_params, auxiliary_state)` once
and add it once to the total.

If diagnostics are requested, return the same ordinary diagnostic fields plus
one explicit `log_auxiliary_likelihood` field so the total remains auditable.

## Target builder

Add one explicit builder:

```python
make_host_density_target(
    base_analysis,
    *,
    redshift_model,
    gw_pe,
    gw_selection,
    pe_state,
    selection_state,
    auxiliary_state=None,
    n_events,
    nsamp,
    n_draw,
    ... reduction controls ...,
) -> InferenceTarget
```

Rules:

- `base_analysis` must be a catalog-free `SpectralRedshift` analysis from
  `ds.model()`; it supplies only the already-frozen cosmology, population and
  angular blocks;
- the extension block comes from `redshift_model.parameter_spec()`;
- target coordinate order is `base_analysis.parameters` followed by the
  extension block;
- the builder uses the existing core decoder for the base block and slices the
  extension parameters separately;
- no catalog/completeness marker is fabricated;
- no GW store loader/binder is reconstructed in this slice;
- returned execution object is the accepted Phase-8B `InferenceTarget`, so
  `ds.infer(target, sampler=...)` uses the same sampler stack.

## Acceptance probe

A fake model living only in tests must use the core normalized comoving-volume
redshift density for both PE and selection. With zero auxiliary term, the generic
host-density path must reproduce the accepted spectral-siren likelihood at fixed
coordinates exactly (or at the already frozen numerical tolerance if exact array
equality is not possible due solely to wrapper return structure).

A second fixed point gives the fake model one sampled extension parameter used
only as an auxiliary scalar. The returned total must equal the same ordinary
likelihood plus that scalar exactly once. Diagnostics must report the auxiliary
term separately.

Dedicated exact-head tests must also prove:

- PE and selection states are passed to the correct density evaluations;
- plan combination offsets joint-constraint indices correctly and rejects
  duplicate labels;
- the target builder rejects non-spectral/catalog-bearing base analyses;
- non-isotropic angular composition from the base analysis is preserved rather
  than dropped;
- no companion imports or LSS/lensing names enter production core;
- 8A, 8B and Phase-8 broad workflows replay green on the same exact head.

No companion repository or Phase 8D production change starts until 8C is
independently accepted.
