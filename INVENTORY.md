# Phase 0 inventory summary

Reference implementation: `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`.

Phase 0 assigns scientific ownership before any runtime code is migrated. The detailed module map is in `inventories/legacy_modules.md`, dependency cuts in `inventories/dependency_edges.md`, tests in `inventories/tests.md`, and non-package material in `inventories/experiments_scripts.md`.

## Main result

The proposed four-repository split is compatible with the actual legacy code, but it cannot be obtained by directory moves alone. Four large legacy seams must be cut after numerical reference fixtures exist:

1. `core/types.py` mixes cosmology/GW/catalog state with LSS and weak-lensing state.
2. `redshift/prior.py` mixes ordinary spectral/catalog priors with Q_LSS ensembles and latent fields, and imports the latent seam back from `likelihood`.
3. `likelihood/core.py` directly imports weak-lensing machinery; `likelihood/factory.py` dispatches ordinary, LSS, flow, marked-host and lensing paths.
4. `inference/loaders.py` stages ordinary catalog data, bright counterparts, LSS products, multitracer bundles and galaxy marks in one layer.

These are dependency inversions/ownership problems, not evidence that the companion packages belong in core.

## Final ownership

```text
CORE
  cosmology
  GW PE/injection schema and loading
  parametric + GP + reusable angular populations
  standardized catalog runtime
  ordinary completeness
  generic host-property weighting
  bright counterparts
  GW selection and diagnostics
  ordinary hierarchical likelihood
  priors/parameters/samplers/checkpoint/results
  optional mature flows after base parity

SURVEYS
  raw survey -> standardized catalog
  pixelization, masks, depth
  selection-function fitting
  reusable DESI/Legacy/GLADE ingest/weights

LSS
  Q_LSS/lognormal completion
  table ensembles and provenance
  latent fields and count likelihood
  single/multitracer field machinery

LENSING
  weak-lensing magnification
  strong-lensing SIS/image marks
  pair/cluster likelihood and selection
  lensed injections, partitions, contracts, preflight
```

## Explicit non-goals

- no `darksirens-extra`;
- no public `core`, `utils`, or catch-all `redshift` namespace in the new package;
- no bulk copy of `experiments/` or `scripts/`;
- no scientific cleanup mixed with migration;
- no companion import from core;
- no second implementation of core cosmology, population weighting or GW store semantics in a companion package.

## Phase 1 reference anchors

The existing legacy test suite already provides the right safety net:

- CPU-fast manifest: 69 files / 823 collected tests at the pinned state;
- `test_unified_k1_golden.py`: 15 cross-domain fixed-coordinate cells with backend-specific legacy values and `rtol <= 1e-12`;
- `test_gppop_population.py`: GP registry, parameter contract, support/Jacobian/normalization;
- selection coefficient/variance/gradient/batching tests;
- gwcat v2/store-layout/spin-basis tests;
- LSS provenance, latent field/count/anchor/seam/multitracer tests;
- weak/strong-lensing unit, file-contract, cluster-selection and direct-Monte-Carlo singleton checks;
- sampler checkpoint/resume and atomic result/provenance tests.

Phase 1 should freeze these behaviors before any mathematical kernel is reorganized.
