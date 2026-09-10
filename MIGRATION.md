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
| `darksirens-core` | core HBI/siren package | not started | |
| `darksirens-surveys` | survey/catalog construction | not started | |
| `darksirens-lss` | LSS/completion/latent fields | not started | |
| `darksirens-lensing` | weak/strong lensing | not started | |

## Accepted Phase-0 mapping

| Legacy domain | Destination | Mode | Status |
|---|---|---|---|
| `core` | core physical owners + lensing/LSS state removed | SPLIT | inventoried |
| `utils` | core physical owners/private helpers | SPLIT | inventoried |
| GW store/sample code | core `gw` | REIMPLEMENT_INTERFACE | inventoried |
| `gw/populations` | core `population` | MOVE_AND_RENAME/SPLIT | inventoried |
| GP population models | core `population` | MOVE_AND_RENAME | inventoried |
| ordinary catalog runtime | core `catalog` | SPLIT | inventoried |
| depth/raw survey construction | surveys | SPLIT | inventoried |
| ordinary redshift/completeness | core cosmology/catalog/selection | SPLIT | inventoried |
| Q_LSS/lognormal/latent/multitracer | LSS | SPLIT | inventoried |
| ordinary event/hierarchical likelihood | core likelihood | SPLIT | inventoried |
| GW MC selection | core selection | MOVE_AND_RENAME | inventoried |
| WL/pair/cluster likelihood | lensing | SPLIT | inventoried |
| inference orchestration | core + extension-owned state | SPLIT | inventoried |
| Q provenance | LSS | MOVE_AND_RENAME | inventoried |
| generic host marks | core catalog/hosts | SPLIT | inventoried |
| reusable angular sky models | core population/angular | SPLIT | inventoried |
| ordinary results/settings | core IO | MOVE_AND_RENAME | inventoried |
| legacy CLIs | all owners or legacy | REIMPLEMENT_INTERFACE | inventoried |
| experiments/scripts | selective only | TEST_ONLY/DO_NOT_MIGRATE | inventoried |

Detailed ownership is in `inventories/`.

## Migration invariants

- No production code changes occurred during Phase 0.
- Legacy remains the source of numerical truth for existing mature behavior.
- A mature implementation is not marked migrated until its mapped parity tests pass.
- Architecture cleanup after the first parity port reruns the same parity tests.
- Core never imports a companion package.
