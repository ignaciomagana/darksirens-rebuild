# Migration ledger

This is the durable cross-repository migration ledger. It is updated as files/functions are assigned and ported.

## Reference

```text
legacy repo: ignaciomagana/darksirens
legacy SHA:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Dispositions

Allowed file/function dispositions:

```text
CORE
SURVEYS
LSS
LENSING
LEGACY_ONLY
FUTURE_REVIEW
```

Allowed migration modes:

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

## Legacy migration table

Phase 0 will populate the detailed inventory under `inventories/` and summarize the accepted mapping here.

| Legacy path/domain | Destination | Mode | Status | Notes |
|---|---|---|---|---|
| `core` | split across core scientific owners | `SPLIT` | planned | public `core` namespace will disappear |
| `utils` | split/private helpers | `SPLIT` | planned | no public `utils` junk drawer |
| `gw/populations` | core `population` | `MOVE_AND_RENAME` | planned | GP remains core |
| GW store/sample code | core `gw` | `REIMPLEMENT_INTERFACE` | planned | preserve gwcat contract including `chieff_reference` |
| ordinary catalog code | core `catalog` | `SPLIT` | planned | raw survey construction goes to surveys |
| ordinary redshift/completeness | core catalog/cosmology/selection | `SPLIT` | planned | no top-level redshift switchboard |
| LSS completion/latent code | `darksirens-lss` | `SPLIT` | planned | preserve table/latent distinctions |
| weak/strong lensing | `darksirens-lensing` | `SPLIT` | planned | remove current core->lensing inversion |
| survey depth/pixelization/fitting | `darksirens-surveys` | `SPLIT` | planned | core evaluates, surveys builds/fits |
| experiments/scripts | mixed | review individually | inventory pending | no wholesale migration |

## Rules

A mature scientific implementation is not marked complete until its mapped parity tests pass against the pinned legacy reference. Architectural cleanup after the initial parity port requires rerunning the same parity suite.
