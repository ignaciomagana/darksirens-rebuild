# Migration ledger

Reference:

```text
legacy: ignaciomagana/darksirens
SHA:    c042527238bd71421b792936bc48c3b815b90d6d
```

Allowed dispositions:

```text
CORE
SURVEYS
LSS
LENSING
LEGACY_ONLY
FUTURE_REVIEW
```

Allowed modes:

```text
COPY
MOVE_AND_RENAME
SPLIT
REIMPLEMENT_INTERFACE
TEST_ONLY
DO_NOT_MIGRATE
```

## Production repositories

| Repository | Role | Status | Latest migration SHA/PR |
|---|---|---|---|
| `darksirens-core` | core HBI/siren package | Phase 2 foundation + GW data contracts complete | `450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6`, PR #1 |
| `darksirens-surveys` | survey/catalog construction | not started | |
| `darksirens-lss` | LSS/completion/latent fields | not started | |
| `darksirens-lensing` | weak/strong lensing | not started | |

## Accepted Phase-0 mapping

| Legacy domain | Destination | Mode | Status |
|---|---|---|---|
| `core` | core physical owners + lensing/LSS state removed | SPLIT | migration active |
| `utils` | core physical owners/private helpers | SPLIT | cosmology migrated; remainder pending |
| GW store/sample code | core `gw` | REIMPLEMENT_INTERFACE | Phase 2 complete, exact parity |
| `gw/populations` | core `population` | MOVE_AND_RENAME/SPLIT | next phase |
| GP population models | core `population` | MOVE_AND_RENAME | next phase |
| ordinary catalog runtime | core `catalog` | SPLIT | pending |
| depth/raw survey construction | surveys | SPLIT | pending |
| ordinary redshift/completeness | core cosmology/catalog/selection | SPLIT | cosmology/grid part complete; remainder pending |
| Q_LSS/lognormal/latent/multitracer | LSS | SPLIT | pending |
| ordinary event/hierarchical likelihood | core likelihood | SPLIT | pending |
| GW MC selection | core selection | MOVE_AND_RENAME | pending |
| WL/pair/cluster likelihood | lensing | SPLIT | pending |
| inference orchestration | core + extension-owned state | SPLIT | pending |
| Q provenance | LSS | MOVE_AND_RENAME | pending |
| generic host marks | core catalog/hosts | SPLIT | pending |
| reusable angular sky models | core population/angular | SPLIT | pending |
| ordinary results/settings | core IO | MOVE_AND_RENAME | pending |
| legacy CLIs | all owners or legacy | REIMPLEMENT_INTERFACE | pending |
| experiments/scripts | selective only | TEST_ONLY/DO_NOT_MIGRATE | ongoing as needed |

Detailed ownership is in `inventories/`.

## Phase-1 numerical reference assets

`darksirens-core` owns the neutral reconstruction reference harness:

```text
tests/reference/legacy/unified_k1_golden.json
tests/reference/legacy/unified_k1_manifest.json
tools/validate_reference.py
tools/compare_reference.py
tools/replay_legacy_unified.py
.github/workflows/reference.yml
.github/workflows/legacy-reference-replay.yml
```

The frozen golden JSON is byte-identical to the legacy Git blob
`560e44adb712763893111a3607f6d7ca8b168b7a`. Candidate scientific code is judged
against this bank; it may not rewrite it.

Pinned legacy replay at run `34429433906` succeeded. The known CPU drift of the
three legacy Q/LSS cells is described by the `legacy-replay` profile only; the
reconstructed LSS target remains the canonical `rtol=1e-12` bank.

## Phase-2 accepted migration

Merged through `darksirens-core` PR #1 as:

```text
450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
```

Accepted owners:

```text
legacy core/jax_config       -> darksirens/_jax.py
legacy cosmology constants   -> darksirens/cosmology/parameters.py + distances.py
legacy utils/interp2d        -> darksirens/cosmology/_interpolation.py
legacy utils/cosmology       -> darksirens/cosmology/distances.py + volume.py
legacy redshift/grid         -> darksirens/cosmology/_grid.py
legacy CosmoParams           -> darksirens/cosmology/parameters.py
legacy gw/store_contract     -> darksirens/gw/store.py
legacy GW/Selection records  -> darksirens/gw/types.py
legacy standard GW loaders   -> darksirens/gw/samples.py
```

Phase-2 final branch validation run `34431185197` passed 14 unit tests, definite-
error lint, zero-difference cosmology parity, exact GW store parity (`rtol=0`),
and the light package-root import contract.

## Migration invariants

- Legacy remains the source of numerical truth for existing mature behavior.
- Frozen reference assets are not regenerated from reconstructed code.
- A mature implementation is not marked migrated until its mapped parity tests pass.
- Architecture cleanup after the first parity port reruns the same parity tests.
- Core never imports a companion package.
- Scientific behavior and architectural movement are not changed in the same initial migration step.
