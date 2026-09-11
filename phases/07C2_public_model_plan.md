# Phase 7C2 — public `model()` parameter plan

## Status

ACCEPTED

## Core branch / head

```text
repository: ignaciomagana/darksirens-core
branch:     rebuild/phase7-public-api
accepted:   102c233f132cd3b68faaebf4f2adbe71defa731e
parent:     02b54e25740ff7cce1a030f372b3190121ad2b0f  (accepted 7C1)
```

## Scope

Phase 7C2 introduces the public analysis-construction surface promised by the
frozen architecture:

```python
analysis = ds.model(
    cosmology=cosmo,
    population=pop,
    catalog=catalog,
)
```

This slice is construction only. It does not load GW event/injection data,
construct runtime likelihood state, or call a sampler.

The new typed composition layer contains:

- `SpectralRedshift` for catalog-free spectral sirens;
- `IncompleteCatalogRedshift` for an ordinary catalog plus the core missing-host
  completeness branch;
- `CompleteCatalogRedshift` for the complete-catalog model;
- `ParameterPlan`, carrying sampled labels/bounds/prior kinds, resolved joint
  cube maps, fixed cosmology, and the fixed-or-sampled population block;
- `Analysis`, which combines the public cosmology, population, redshift model,
  and parameter plan.

There is deliberately no `universe_model` field or dispatcher.

## Frozen coordinate contract

The sampled-coordinate order matches the frozen ordinary parameter builder:

```text
cosmology -> population -> ordinary catalog nuisance block
```

For the K=1, no-LSS ordinary core surface, the frozen survey-registry matrix
requires:

```text
spectral:            []
incomplete catalog:  [log10n0, delta, sigma_kde]
complete catalog:    [delta, sigma_kde]
```

with bounds:

```text
log10n0:  [-4, -1]
delta:    [-3,  3]
sigma_kde:[ 0, 0.05]
```

`b_miss` is intentionally absent: the frozen registry marks it inert when
`use_lss=False`, and LSS fields do not belong to core.

The accepted 7C1 joint-prior resolver is applied after the full sampled plan is
assembled, so sampled GWTC-5 populations retain their normalized simplex and
conditional-upper maps.

## Files

```text
src/darksirens/analysis.py
src/darksirens/__init__.py
tests/test_public_model.py
tools/probe_public_model_plan.py
.github/workflows/phase7c2-public-model.yml
```

## Acceptance gates

Dedicated exact-head 7C2 gate:

```text
run: 34596633396
job: 103253806465 (public-model)
status: SUCCESS
```

This passed:

- definite-error lint / compile;
- fresh-process lazy root `ds.model` import guard;
- focused construction tests;
- frozen survey-registry extraction for spectral/incomplete/complete cells;
- reconstructed plan evaluation;
- exact frozen/new ordinary catalog-block labels and bounds.

Broad Phase-7 regression on the same head:

```text
run: 34596632992
job: 103253805105 (regression)
status: SUCCESS
```

It passed the full reconstructed test suite and companion-import boundary.

Earlier Phase-7 surfaces also re-passed on this exact head:

```text
7C1 resolver: 34596632909 / 103253805578 SUCCESS
7B specs:     34596633316 / 103253806135 SUCCESS
7A loaders:   34596633170 / 103253805984 SUCCESS
```

## Exclusions

7C2 does not add:

- `ds.infer()`;
- GW-store to `GWEvent` runtime binding;
- HEALPix RA/Dec -> row-index conversion;
- likelihood closures or JIT state;
- sampler configuration;
- bright-siren public composition;
- angular-model public configuration;
- survey/LSS/lensing extension state.

## Next slice

Before runtime analysis binding can consume `GWStore` / `SelectionStore` with a
pixelated catalog, core needs one portable piece of geometry that frozen staged
loading previously obtained from `healpy.ang2pix`: RING HEALPix pixelization of
GW RA/Dec at the catalog NSIDE. Reconstruct this as a small host-side core
utility with exact randomized parity against frozen `healpy`, without adding a
runtime `healpy` dependency. Only after that geometry slice should the runtime
binder decode an `Analysis` parameter vector and construct the ordinary
likelihood closure.
