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
| `darksirens-core` | core HBI/siren package | Phases 2–4 complete; Phase 5 catalog/dark/bright next | `0f97feff7eb283a1f541bef9a776c9347084e70e`, PR #3 |
| `darksirens-surveys` | survey/catalog construction | not started | |
| `darksirens-lss` | LSS/completion/latent fields | not started | |
| `darksirens-lensing` | weak/strong lensing | not started | |

## Accepted Phase-0 mapping

| Legacy domain | Destination | Mode | Status |
|---|---|---|---|
| `core` | core physical owners + lensing/LSS state removed | SPLIT | cosmology/GW runtime migrated; catalog split next |
| `utils` | core physical owners/private helpers | SPLIT | cosmology + likelihood numerics migrated; remainder selective |
| GW store/sample code | core `gw` | REIMPLEMENT_INTERFACE | Phase 2 complete, exact parity |
| `gw/populations` | core `population` | MOVE_AND_RENAME/SPLIT | Phase 3 complete, exact parity |
| GP population models | core `population` | MOVE_AND_RENAME | Phase 3 complete; optional tinygp boundary pinned |
| ordinary catalog runtime | core `catalog` | SPLIT | Phase 5 contract frozen; implementation next |
| depth/raw survey construction | surveys | SPLIT | pending |
| ordinary redshift/completeness | core cosmology/catalog/selection | SPLIT | volume/grid migrated; catalog/completeness Phase 5 |
| Q_LSS/lognormal/latent/multitracer | LSS | SPLIT | pending; explicitly excluded from Phase 5 |
| ordinary event/hierarchical likelihood | core likelihood | SPLIT | catalog-free spectral path Phase 4 complete; catalog composition Phase 5 |
| GW MC selection | core selection | MOVE_AND_RENAME | Phase 4 complete, exact parity |
| WL/pair/cluster likelihood | lensing | SPLIT | pending |
| inference orchestration | core + extension-owned state | SPLIT | pending after Phase 5 |
| Q provenance | LSS | MOVE_AND_RENAME | pending |
| generic host marks | core catalog/hosts | SPLIT | Phase 5D after ordinary catalog parity |
| reusable angular sky models | core population/angular | SPLIT | future core slice |
| ordinary results/settings | core IO | MOVE_AND_RENAME | pending |
| legacy CLIs | all owners or legacy | REIMPLEMENT_INTERFACE | pending; mega CLI not a migration target |
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

## Phase-2 accepted migration — cosmology + GW data contracts

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

## Phase-3 accepted migration — population models including GP

Merged through `darksirens-core` PR #2 as:

```text
e0b40fef65261a27b67aa9657a97216df3e8444f
```

Accepted owners:

```text
legacy gw/populations/base.py           -> darksirens/population/base.py
legacy gw/populations/components.py     -> darksirens/population/components.py
legacy component-spin population pieces -> darksirens/population/components.py
legacy gw/populations/parametric.py     -> darksirens/population/parametric.py
legacy gw/populations/grammar.py        -> darksirens/population/grammar.py
legacy gw/populations/registry.py       -> darksirens/population/registry.py
legacy gw/populations/gp.py             -> darksirens/population/gp.py
legacy population normalization helpers -> darksirens/population/_grids.py
```

The final Phase-3 branch/PR gates established exact fixed-point legacy/candidate
population parity (`max_abs=max_rel=0`, comparison `rtol=1e-12`) and preserved
the optional GP dependency boundary: an ordinary population import does not load
`tinygp`.

Detailed provenance is in `phases/03_population.md`.

## Phase-4 accepted migration — spectral likelihood + GW selection

Merged through `darksirens-core` PR #3 as:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

Accepted owners:

```text
legacy likelihood/selection.py        -> darksirens/selection/gw.py
legacy inference/utils likelihood math -> darksirens/likelihood/weights.py
legacy likelihood/events.py runtime    -> darksirens/gw/{types,runtime}.py
catalog-free likelihood/core.py branch -> darksirens/likelihood/{event,hierarchical}.py
legacy spectral volume prior           -> darksirens/cosmology/volume.py
```

Exact-head branch acceptance:

```text
head:  cfdb138d40d66614bf9b1264c2574d0b497b812d
run:   34445525661
job:   102769369532
result: SUCCESS
```

All historical PR workflows plus the Phase-4 workflow then passed at the same
head. Strict separate-process legacy/candidate fixed-theta spectral parity was
exact across per-event evidence/variance, `log_mu`, `N_eff`, selection correction,
and full likelihood at three fixed points:

```text
max_abs = 0
max_rel = 0
rtol    = 1e-12
atol    = 0
```

The merge was performed with expected-head protection, `main` was verified at
`0f97feff...`, and post-merge reference-integrity run `34447108888` passed.

Detailed provenance is in `phases/04_spectral_likelihood.md`.

## Phase-5 frozen migration plan — ordinary catalog + dark/bright sirens

Base:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

Planned branch:

```text
rebuild/phase5-catalog-dark-bright
```

Staged ownership:

```text
5A  catalogs/compact.py + ordinary catalog_views + redshift/catalog.py
    -> darksirens/catalog/{types,compact,redshift}.py

5B  non-LSS redshift/completion.py
    -> darksirens/catalog/completeness.py

5C  ordinary branches of redshift/prior.py + likelihood/core.py
    -> explicit catalog/counterpart models + existing hierarchical core

5D  generic host marks and serialized catalog-selection runtime only after
    5A–5C parity; raw mark/selection construction remains surveys
```

Do not reproduce `EMCatalog` or `SurveyParams` as mega containers. Q/latent/field
state remains LSS; raw survey schemas/depth-map construction/selection fitting
remain surveys; lensing remains lensing; the old mega likelihood factory and
`universe_model` dispatcher are not migration targets.

Primary end-to-end Phase-5 golden cells are the already frozen CPU cells:

```text
plain_full
plain_compact
complete_volume
complete_zero
bright
```

Canonical comparison remains `rtol=1e-12`, `atol=0`, with detailed
separate-process legacy/candidate probes in addition to the frozen golden bank.

Detailed contract: `phases/05_catalog_dark_bright.md`.

## Migration invariants

- Legacy remains the source of numerical truth for existing mature behavior.
- Frozen reference assets are not regenerated from reconstructed code.
- A mature implementation is not marked migrated until its mapped parity tests pass.
- Architecture cleanup after the first parity port reruns the same parity tests.
- Core never imports a companion package.
- Scientific behavior and architectural movement are not changed in the same initial migration step.
- File names do not determine ownership: generic-looking LSS tests remain LSS when their implementation is Q/lognormal/latent-specific.
