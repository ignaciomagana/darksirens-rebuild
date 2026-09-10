# darksirens rebuild

This repository is the durable control record for reconstructing the legacy `darksirens` codebase into a small core package plus three first-class companion packages.

## Repositories

- `ignaciomagana/darksirens` — frozen scientific reference implementation
- `ignaciomagana/darksirens-core` — new Python distribution/import `darksirens`
- `ignaciomagana/darksirens-surveys` — survey/catalog construction
- `ignaciomagana/darksirens-lss` — validated LSS/completion/latent-field extensions
- `ignaciomagana/darksirens-lensing` — validated weak/strong-lensing extensions

The legacy numerical reference is pinned at:

```text
c042527238bd71421b792936bc48c3b815b90d6d
```

## Purpose

This repo contains architecture decisions, migration inventories, numerical-parity contracts, phase status, and links to commits/PRs in the four production repositories. Production package code does **not** live here.

The central design principle is the user-facing API. A normal analysis should reduce to a small vocabulary:

```python
import darksirens as ds

events = ds.load_events("pe.h5")
injections = ds.load_injections("selection.h5")
catalog = ds.load_catalog("catalog.h5")

cosmo = ds.Cosmology(H0=(20, 140), Om0=0.3075)
pop = ds.Population("brokenpowerlaw+2peaks", fixed="gwtc5")
analysis = ds.model(cosmology=cosmo, population=pop, catalog=catalog)
result = ds.infer(analysis, events=events, injections=injections)
```

## Migration order

```text
0  inventory and dependency map
1  freeze legacy numerical reference
2  darksirens-core
3  freeze extension interfaces
4  darksirens-surveys
5  darksirens-lss
6  darksirens-lensing
7  cross-repository integration
8  final audit
```

Scientific changes and architecture changes are not mixed. Mature scientific paths must pass fixed-point numerical parity against the pinned legacy implementation before they are considered migrated.

Start with `STATUS.md`, then `ARCHITECTURE.md` and `DECISIONS.md`.
