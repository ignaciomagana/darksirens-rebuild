# Phase 0 inventory

Reference: `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`.

This document is the high-level inventory. Detailed file-by-file tables will be added under `inventories/` as Phase 0 proceeds.

## Legacy package namespaces

```text
darksirens/
    catalogs/
    cli/
    core/
    gw/
    inference/
    io/
    lensing/
    likelihood/
    marks/
    redshift/
    sky/
    utils/
```

The refactor deliberately removes `core`, `utils`, and the catch-all public `redshift` namespace from the target architecture.

## Initial domain mapping

### CORE

```text
core/jax_config.py
core/types.py                           split by physical owner
core/constants.py                       split by physical owner
utils/cosmology.py
utils/interp2d.py
GW PE/selection store/load logic
gw/populations/* including gp.py
ordinary catalog compact/io/counterpart logic
ordinary redshift catalog/completeness/volume logic
marks generic host-weight models
sky reusable angular source-rate models
ordinary event/hierarchical likelihood
ordinary GW selection integral/diagnostics
parameter/prior/sampler/checkpoint/result IO
```

### SURVEYS

```text
catalogs/depth_map.py
cli/pixelate.py
cli/fit_selection.py
offline fitting portions of redshift/selection.py
reusable DESI/Legacy/GLADE/KIBO ingestion and survey weighting
```

`cli/skymaps_to_samples.py` is explicitly not classified as survey functionality; it remains `FUTURE_REVIEW`/legacy pending evaluation as GW-input tooling.

### LSS

```text
catalogs/lss.py
redshift/lognormal_completion.py
redshift/latent_field.py
redshift/latent_counts.py
LSS-specific redshift/completion.py
likelihood/latent_q.py
inference/q_provenance.py
cli/build_lognormal_completion.py
cli/build_joint_lognormal_completion.py
cli/build_latent_field.py
cli/diagnose_lognormal_completion.py
```

### LENSING

```text
lensing/*
likelihood/wl_weight.py
likelihood/pair_kde.py
likelihood/cluster_likelihood.py
likelihood/cluster_selection.py
likelihood/likelihood_with_clusters.py
cli/inference_lensing.py
configs/mock_lensing/*
reusable mock-lensing validation/simulation scripts
```

### LEGACY_ONLY / FUTURE_REVIEW

Paper/campaign workflows, result directories, one-off figures, superseded experiments, temporary benchmarks, absolute cluster-path scripts, and diagnostics with no reusable library role are not migrated automatically.

## Known large coupling points

The legacy architecture has several files that are too broad to move wholesale and must be split by responsibility:

```text
core/types.py
redshift/completion.py
redshift/catalog.py
likelihood/core.py
likelihood/factory.py
likelihood/block_sizing.py
inference/loaders.py
inference/prior.py
inference/sampling.py
cli/inference.py
cli/inference_lensing.py
```

These are migration sources, not target modules.

## Known dependency inversions to remove

1. Ordinary likelihood code imports lensing grid machinery.
2. Core types contain weak-lensing/LSS-specific state.
3. Core constants contain lensing-specific constants.
4. Likelihood contains weak/strong-lensing implementations.
5. Catalog and redshift code cross-import survey/LSS-specific concepts.
6. Marks currently require lazy redshift imports to avoid cycles.
7. Runtime/block-sizing concerns sit inside the likelihood namespace.
8. The CLI has accumulated substantial scientific orchestration that belongs in importable inference modules.

## Existing validation assets to preserve

The legacy test suite already contains strong regression coverage. Phase 0/1 will map exact filenames and fixtures for:

```text
packaging/import-side-effect behavior
array shapes/no-download behavior
cosmology/grid interpolation
GW store format and spin-basis compatibility
pdet/selection parity
selection N_eff and likelihood variance
catalog completeness, including bit-identical paths where required
parameter/prior construction
sampler checkpoint/resume
LSS provenance and latent-field guards
multitracer parameter-space semantics
weak-lensing integration
strong-lensing analytic-vs-Monte-Carlo validation
pair/cluster/partition behavior
```

These tests are migration inputs, not disposable legacy clutter.

## Phase 0 remaining work

- enumerate every package module and exact disposition;
- enumerate legacy tests and map them to target repositories;
- inventory scripts/experiments/configs individually;
- map concrete cross-package imports/functions;
- derive actual base/optional dependencies per target repo;
- create per-repository `CONTRACT.md`, `MIGRATION.md`, and `VALIDATION.md` before runtime porting starts.
