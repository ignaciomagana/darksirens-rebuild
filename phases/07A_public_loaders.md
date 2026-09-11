# Phase 7A — standardized public loaders

## Status

ACCEPTED

## Core branch / head

```text
repository: ignaciomagana/darksirens-core
branch:     rebuild/phase7-public-api
accepted:   c338bc8eaa5199775e6d1355f20406be8ade1eb1
parent base:d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
```

The functional loader implementation first landed at
`83a7b7efcab39818306630742f914dcddfa162e8`; the accepted head additionally
contains the reusable Phase-7 broad regression workflow. No scientific code was
changed between those two commits.

## Scope

Phase 7A establishes the first conventional package-root user surface:

```python
import darksirens as ds

events = ds.load_events("pe.h5")
injections = ds.load_injections("selection.h5")
catalog = ds.load_catalog("catalog.h5")
```

The GW facades delegate to the already reconstructed, parity-tested
`GWStore` / `SelectionStore` loaders. The catalog facade consumes only the
standardized core catalog product: `nside`, `zgals`, `dzgals`, `wgals`,
`ngals`, and optional `z_depth`. It applies the frozen stable per-row
real-galaxy redshift ordering before constructing the existing Phase-5
`GalaxyCatalog` runtime object, and carries only the structural metadata needed
by ordinary core inference.

## Files added / changed

```text
src/darksirens/__init__.py
src/darksirens/catalog/io.py
src/darksirens/catalog/types.py
src/darksirens/catalog/__init__.py
tests/test_public_loaders.py
tools/probe_public_catalog_loader.py
.github/workflows/phase7a-public-loaders.yml
.github/workflows/phase7-regression.yml
```

## Frozen parity / acceptance gates

Dedicated exact-head loader gate:

```text
run: 34593088782
job: 103242605896 (public-loaders)
status: SUCCESS
```

This gate passed:

- definite-error lint / compile;
- package-root dependency-light import guard;
- focused 7A tests;
- AST-extracted frozen `load_survey` evaluation;
- reconstructed standardized catalog evaluation;
- exact legacy/new catalog-loader parity.

Broad Phase-7 regression gate:

```text
run: 34593088762
job: 103242605373 (regression)
status: SUCCESS
```

This gate passed:

- definite-error lint / compile;
- the full reconstructed test suite;
- the core-to-companion forbidden-import boundary.

## Architectural exclusions

7A does **not** migrate or re-create:

- DESI/KIBO/Legacy/GLADE-native schemas;
- masks, raw catalog pixelization or depth-map construction;
- survey selection-function fitting;
- Q/LSS tables, latent fields, multitracer state or provenance;
- weak/strong lensing inputs;
- staged legacy `load_all_data(opts)` assembly;
- a `universe_model` switchboard;
- campaign CLI configuration.

Those remain assigned to companion packages or legacy-only orchestration by the
frozen reconstruction architecture.

## Next slice

Phase 7B: small declarative public cosmology and population specifications,
feeding existing reconstructed parameter/population machinery. Do not build
`model()` or `infer()` in the same slice.
