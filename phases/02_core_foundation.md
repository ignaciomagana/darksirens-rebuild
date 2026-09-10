# Phase 2 report — core foundation and GW data contracts

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
PR:               #1
merged core SHA:  450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

## Status

COMPLETE.

## Scope

This is the first scientific implementation slice in the reconstructed core.
It intentionally stops before population models, catalog/redshift models,
hierarchical likelihood, selection effects, samplers, LSS and lensing.

## Implemented

### Packaging and runtime

- modern `src/darksirens` package layout;
- side-effect-free root import;
- explicit `darksirens.configure_jax_runtime()`;
- JAX x64/highest-matmul configuration;
- allocator defaults applied before JAX backend import;
- optional persistent XLA compilation cache support.

### Cosmology

New owner: `darksirens.cosmology`.

Migrated from the legacy cosmology/constants/interpolation/redshift-grid code:

- flat-CPL expansion rate;
- precomputed distance table;
- comoving distance;
- luminosity distance;
- inverse `dL -> z`;
- differential comoving volume;
- `ddL/dz`;
- distance modulus;
- low-z interpolation correction;
- shared logarithmic redshift grid;
- distance-table threading across JIT boundaries.

The legacy `core`/`utils` ownership is not reproduced.

### Standardized GW input layer

New owner: `darksirens.gw`.

Implemented:

- explicit PE and selection store contracts;
- `GWStore` and `SelectionStore` records;
- PE/injection HDF5 loaders;
- format-version validation;
- 1-D/length/count/finite/range guards;
- detector/source mass ordering checks;
- sky-coordinate checks;
- PE proposal normalization per event;
- physical detected-injection `pdraw` scale;
- density-aware spin-basis negotiation;
- `chieff`, `component`, and `chieff_reference` support;
- lazy `gwcat` dependency only when an analytic chi_eff prior must actually be evaluated.

The new GW input layer has no HEALPix, population, LSS or lensing dependency.

## Validation

Final scientific gate before the documentation-only validation commit:

```text
workflow: phase2-foundation
run:      34431185197
job:      102726848203
status:   SUCCESS
```

Results:

```text
ruff F/E9 gate: PASS
candidate unit tests: 14 passed
cosmology legacy/new max_abs: 0.000e+00
cosmology legacy/new max_rel: 0.000e+00
GW store legacy/new max_abs: 0.000e+00
GW store legacy/new max_rel: 0.000e+00
GW store comparison: exact, rtol=0
light package-root import: PASS
```

The candidate and pinned legacy code were run in separate import roots against
the same deterministic fixtures.

## Review finding corrected before merge

The initial loader port set XLA allocator defaults after importing JAX. Although
numerical/store parity was already exact, that ordering could make allocator
settings ineffective once a backend initialized. It was corrected so explicit
or default allocator settings are established before the GW module imports JAX.
The full Phase-2 gate was rerun after this correction and passed.

A first test failure in this phase was only an over-specific error-message
regex for a component-basis mismatch. The implementation correctly rejected the
mismatch because `chieff` was advisory rather than part of the file density.
The test was changed to pin the semantic refusal instead of obsolete wording.

## Scientific changes

None intended or introduced. Cosmology and standardized GW store processing are
numerically identical on the Phase-2 parity probes.

## Merge

PR #1 was squash-merged to `main` as:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

## Next phase

Phase 3: migrate the population model system into `darksirens.population`,
including the GP models, registry/grammar, fixed GWTC parameter sets, component
spin models and normalization machinery. Establish direct pointwise and
normalization parity before the population API is used by the new likelihood.
