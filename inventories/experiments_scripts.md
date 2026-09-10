# Experiments, scripts and non-runtime material

Reference: `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`.

Nothing under `experiments/` or `scripts/` is migrated wholesale.

## Experiment groups

The pinned repository contains:

```text
experiments/CHECKPOINT.md
experiments/py_env.sh
experiments/completeness_viz/
experiments/desi_full259/
experiments/desi_ingest/
experiments/field_level_plan/
experiments/vollim/
```

### `desi_full259/`

Disposition: `LEGACY_ONLY` by default.

This is a production/science campaign, not a reusable package namespace. Package bugs, fixtures or generic loaders exposed by it can be promoted individually. Preserve the fact that this is the **259-event** analysis; no alternative historical count becomes a package assumption.

### `desi_ingest/`

Disposition: `FUTURE_REVIEW -> SURVEYS` selectively.

Reusable raw DESI column interpretation, filtering, mask construction or standardized-catalog writing can be promoted into `darksirens-surveys`. Campaign paths, manifests and analysis choices remain legacy.

### `field_level_plan/`

Disposition: `LEGACY_ONLY` for reports/PR history; `TEST_ONLY` selectively for independent verification programs.

The mature runtime implementation already lives in `redshift/latent_field.py`, `latent_counts.py`, completion/likelihood code. Its tests, not the PR diary, become the LSS acceptance contract. Independent scripts that rederive physics pins may be retained as LSS validation assets.

### `vollim/`

Disposition: `LEGACY_ONLY` as an analysis project, with survey construction pieces eligible for selective promotion to SURVEYS.

### `completeness_viz/`

Disposition: `LEGACY_ONLY/FUTURE_REVIEW`. Visualization is not part of the inference kernel.

## Root scripts

Known root scripts include block-size and TinyNS benchmarks, selection diagnostics, `build_mth_map.py`, dN/dz checks, flow diagnostics/comparison/convergence, flow launchers, K-correction studies, mock-lensing tooling and additional campaign utilities.

Ownership rule:

```text
benchmark of reusable core runtime             -> TEST_ONLY core validation
scientific selection diagnostic                -> TEST_ONLY core validation
raw survey/map/selection construction          -> SURVEYS if reusable
flow comparison/training campaign              -> LEGACY_ONLY, or optional-core validation later
mock lensing generator/independent validator   -> LENSING simulation/test asset if contract-defining
paper launcher/plot/path wrapper               -> LEGACY_ONLY
```

`scripts/benchmark_block_sizes.py` and TinyNS short-budget benchmarks are not runtime API; use them only if needed to preserve performance/runtime safety after the numerical port.

`scripts/build_mth_map.py` is a candidate survey-construction utility because the fast suite explicitly tests its output path; promote the underlying function, not necessarily the script CLI verbatim.

Flow scripts remain deferred until ordinary sample-based core inference is stable.

## CLI disposition

The legacy CLI is not preserved as an architecture. New package CLIs should be thin and call the Python API. Legacy option-language tests are useful only where they pin a scientific convention or result-file compatibility; option spelling itself is not sacred unless intentionally retained.

## Documentation and configs

- scientific derivations/conventions for migrated machinery: migrate/rewrite with owner;
- mock-lensing configs: lensing test/simulation assets if needed for validation;
- paper/campaign configs: legacy only;
- absolute HPC environment scripts: legacy only;
- test/CI documentation: replace with per-repo test tiers after migration.

## Promotion criterion

A non-runtime legacy file moves only when it does at least one of:

1. implements a reusable package capability;
2. provides an independent scientific validation of a migrated calculation;
3. supplies a small deterministic integration fixture;
4. is required to reproduce a stable file/data contract.

Everything else remains available in the frozen legacy repository and does not burden the new packages.
