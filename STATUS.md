# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 2 — CORE FOUNDATION AND GW DATA CONTRACTS
status: COMPLETE
```

## Completed

### Phase 0

- four-package ownership model confirmed against the legacy code;
- package, dependency, experiment/script and test inventories recorded;
- major cross-domain dependency inversions identified;
- GP population models assigned to core;
- LSS and lensing assigned to mature first-class companion packages.

### Phase 1

- unified K=1 legacy likelihood bank frozen byte-identically in `darksirens-core`;
- pinned legacy replay established in a separate import root;
- canonical reconstructed likelihood target fixed at `rtol=1e-12`, `atol=0`;
- known ~`2.3e-12` legacy CPU drift isolated to the three Q/LSS replay cells only.

### Phase 2

PR `ignaciomagana/darksirens-core#1` was squash-merged.

Core `main` is now:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

The reconstructed package now contains:

- modern `src/darksirens` packaging;
- side-effect-free root import;
- explicit JAX runtime configuration;
- flat-CPL cosmology and shared redshift grids;
- standardized GW PE/selection store contracts;
- `GWStore` and `SelectionStore` records;
- PE/injection loaders with density-aware spin-basis negotiation;
- current `chieff_reference` selection support.

## Phase-2 validation

Final scientific branch gate:

```text
workflow run: 34431185197
job:          102726848203
status:       SUCCESS
```

Results:

```text
ruff F/E9: PASS
14 candidate tests: PASS
cosmology legacy/new max_abs = 0
cosmology legacy/new max_rel = 0
GW-store legacy/new max_abs = 0
GW-store legacy/new max_rel = 0
GW-store comparison rtol = 0 (exact)
light package-root import: PASS
```

The allocator-order issue found during review was corrected before merge and the
entire gate rerun successfully.

## Production repository state

### `darksirens-core`

Phase 2 complete on `main` at:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Population, catalog/redshift, hierarchical likelihood, GW selection, samplers
and high-level `model/infer` API are not yet migrated.

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Architecture questions intentionally deferred

- minimal LSS redshift/auxiliary-likelihood protocol;
- minimal strong-lensing analysis protocol;
- exact optional flow API.

These remain deferred until ordinary core likelihood parity.

## Scientific questions

None opened. No scientific behavior change has been accepted in Phases 0-2.

## Next action

Phase 3 — migrate the population system into `darksirens.population`, including
parametric and GP models, grammar/registry, fixed GWTC parameter sets, component
spin handling and normalization machinery. Require pointwise and normalization
parity before the new likelihood can depend on it.
