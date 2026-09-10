# Phase 0 report — inventory and dependency map

## Reference

`ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`

## Status

COMPLETE.

## Work completed

- Inspected all top-level package domains and the full scientific ownership split.
- Enumerated exact module trees for core, GW/populations, likelihood, inference, redshift, catalogs, lensing, marks/sky/io/utils/CLI.
- Inspected experiment groups and root script classes; established selective-promotion policy rather than bulk migration.
- Read the central coupling points `core/types.py`, `likelihood/core.py`, `likelihood/factory.py`, `inference/loaders.py`, and `redshift/prior.py`.
- Mapped the legacy CPU-fast test manifest and specialized GP/LSS/lensing regression assets to new owners.
- Identified `test_unified_k1_golden.py` as the central cross-domain fixed-coordinate parity bank for Phase 1.

## Main dependency cuts

1. remove LSS/WL fields from generic core runtime containers;
2. remove ordinary core likelihood -> lensing imports;
3. split ordinary redshift models from Q/latent LSS state;
4. split global loader/factory orchestration into explicit model composition;
5. make parameter/prior construction composable without a plugin framework;
6. separate standardized catalog schema from raw survey construction.

## Tests/reference assets

Canonical fast gate at the reference state:

```text
69 files
823 collected tests
```

Central cross-domain golden:

```text
tests/test_unified_k1_golden.py
tests/golden/unified_k1_golden.json
15 cells x 3 deterministic coordinates
rtol <= 1e-12
same-backend bit identity expected
```

Specialized anchors include GP population contract/normalization, gwcat store/basis tests, selection correction/variance/gradient tests, LSS provenance/latent/multitracer tests, lensing cluster/file/singleton direct-MC tests, and sampler checkpoint/result-provenance tests.

## Production repositories changed

None.

## Scientific changes

None.

## Open architecture items

The exact shape of two interfaces is deliberately **not** frozen in Phase 0:

- LSS redshift/host-density + optional auxiliary field-likelihood protocol;
- specialized analysis/log-likelihood protocol for strong-lensing clusters.

They will be designed only after ordinary core reaches parity, so the interface follows real call requirements rather than speculation.

## Next phase

Phase 1: create a separate-process legacy/candidate parity harness and freeze reference outputs before moving mathematical code.
