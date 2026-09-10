# Legacy module ownership

Reference: `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`.

A destination denotes scientific ownership, not necessarily a literal file copy. Large modules are split only after Phase-1 parity fixtures exist.

## Package root and infrastructure

| Legacy path | Owner | Target/mode | Decision |
|---|---|---|---|
| `darksirens/__init__.py` | CORE | new root API / reimplement interface | preserve cold/light import behavior |
| `setup.py` | LEGACY_ONLY | do not migrate | use modern `pyproject.toml` |
| `pyproject.toml`, `requirements.txt` | mixed | split | derive per-package real dependencies |
| `.github/workflows/ci.yml` | mixed | reimplement per repo | preserve test intent, not monolithic layout |
| `docs/` | mixed | split/rewrite | retain scientific contracts; API docs follow new interface |

## `core/`

| Legacy file | Owner | Target |
|---|---|---|
| `constants.py` | mixed | cosmology/catalog/selection owners; SIS constants -> lensing |
| `jax_config.py` | CORE | `darksirens/_jax.py` |
| `model_kinds.py` | CORE transitional | thin model construction only; no public universe-model switchboard |
| `types.py` | mixed | `cosmology/parameters.py`, `gw/types.py`, `catalog/types.py`, companion state |

`SurveyParams` currently contains ordinary catalog selection/completeness plus LSS and weak-lensing state. The final core type must not.

## `utils/`

- cosmology -> CORE `cosmology/distances.py` / `cosmology/volume.py`;
- interpolation -> CORE private `cosmology/_interpolation.py`;
- numerical/log helpers -> CORE private helper or physical owner;
- plotting -> LEGACY_ONLY/FUTURE_REVIEW initially.

Final public `utils` namespace: none.

## `gw/`

The namespace currently fuses standardized GW data with population models.

| Legacy file | Owner | Target |
|---|---|---|
| `samples.py` | CORE | `gw/samples.py` public facade |
| `store_contract.py` | CORE | `gw/store.py` |
| `utils.py` | CORE | split into `gw/store.py` + `gw/samples.py` |
| `flows.py` | CORE deferred | optional `gw/flows.py` after sample path stable |
| `selection.py` | CORE deferred | optional `selection/emulator.py`; pdet-flow pseudo-injection path |
| `populations/base.py` | CORE | `population/base.py` |
| `populations/components.py` | CORE | `population/components.py` |
| `populations/component_spin.py` | CORE | components/parametric split |
| `populations/parametric.py` | CORE | `population/parametric.py` |
| `populations/gp.py` | CORE | `population/gp.py` |
| `populations/grammar.py` | CORE | `population/grammar.py` |
| `populations/registry.py` | CORE | `population/registry.py` |
| `populations/sampling.py` | CORE deferred/FUTURE_REVIEW | retain only generic reusable population sampling |
| `populations/utils.py` | CORE private | normalization grids/helpers under population |

The pinned SHA includes current `chieff_reference` selection-basis support. This is part of the file contract.

## `catalogs/`

| Legacy file | Owner | Target |
|---|---|---|
| `compact.py` | CORE | `catalog/compact.py` |
| `counterparts.py` | CORE | `catalog/counterparts.py` |
| `io.py` | CORE + SURVEYS seam | core owns standardized schema; raw survey interpretation moves to surveys |
| `depth_map.py` | SURVEYS | `darksirens_surveys/depth.py` |
| `lss.py` | LSS | LSS IO/completion loader |
| `marks.py` | mixed | generic runtime host property consumption -> core; survey construction -> surveys |

Stable public runtime object should become a `GalaxyCatalog` concept. `EMCatalog` can survive privately during parity only.

## `marks/`

Generic host-efficiency/host-property models and their registry are CORE and should become `catalog/hosts.py` or an equally explicit owner. The current lazy redshift import is a cycle symptom, not a reason to externalize marks.

## `sky/`

Reusable angular/source-rate models are CORE population models and move under `population/angular.py`. Analysis/plotting is LEGACY_ONLY/FUTURE_REVIEW.

## `redshift/`

The public namespace disappears.

| Legacy file | Owner | Target |
|---|---|---|
| `grid.py` | CORE private | `cosmology/_grid.py` |
| `volume.py` | CORE | `cosmology/volume.py` |
| `catalog.py` | CORE | `catalog/redshift.py` |
| `checks.py` | CORE tests/validation | catalog validation/tests |
| `selection.py` runtime evaluation | CORE | `selection/catalog.py` |
| `selection.py` offline fitting | SURVEYS | survey selection fitting |
| ordinary `completion.py` | CORE | `catalog/completeness.py` |
| LSS portions of `completion.py` | LSS | completion/models |
| `lognormal_completion.py` | LSS | `completion/lognormal.py` |
| `latent_field.py` | LSS | `field/basis.py`, `field/latent.py` |
| `latent_counts.py` | LSS | `field/counts.py`, `field/tracers.py` |
| `prior.py` | mixed | ordinary model composition in core; Q/latent implementations in LSS |

`redshift/prior.py` currently supports spectral, bright, complete and incomplete priors but also owns Q-ensemble/latent state and imports `likelihood.latent_q`. Do not reproduce that coupling.

## `likelihood/`

| Legacy file | Owner | Target |
|---|---|---|
| `events.py` | CORE | `likelihood/event.py` |
| ordinary parts of `core.py` | CORE | `likelihood/event.py` + `hierarchical.py` |
| `selection.py` | CORE | `selection/gw.py` + diagnostics |
| ordinary `catalog_views.py` | CORE | catalog/runtime preparation |
| LSS augmentation in `catalog_views.py` | LSS | LSS model preparation |
| `block_sizing.py` | CORE | `inference/runtime.py` |
| `factory.py` | mixed | thin core model + extension-owned construction; do not preserve mega factory |
| `flow_events.py` | CORE deferred | optional `likelihood/flows.py` |
| `latent_q.py` | LSS | LSS model/field seam |
| `wl_weight.py` | LENSING | `weak/weights.py` |
| `pair_kde.py` | LENSING | `strong/pair_kde.py` |
| `cluster_likelihood.py` | LENSING | strong/package likelihood |
| `cluster_selection.py` | LENSING | `strong/selection.py` |
| `likelihood_with_clusters.py` | LENSING | lensing analysis/model interface |

Confirmed inversion: ordinary `likelihood/core.py` imports weak-lensing grids/PDFs directly.

## `inference/`

| Legacy file | Owner | Target |
|---|---|---|
| `checkpointing.py` | CORE | `inference/checkpoint.py` |
| `data.py` | CORE | `inference/data.py` |
| `loaders.py` | mixed | ordinary loading -> core; LSS/multitracer construction -> LSS |
| `parameters.py` | CORE + extension seam | composable `inference/parameters.py` |
| `pop_extractor.py` | CORE | population/parameter mapping helper |
| `prior.py` | CORE + extension seam | composable `inference/prior.py` |
| `q_provenance.py` | LSS | `completion/provenance.py` |
| `run_fingerprint.py` | CORE | inference or `io/provenance.py` |
| `sampling.py` | CORE | split sampler adapters/run orchestration |
| `tinyns_config.py` | CORE optional | TinyNS adapter |
| `utils.py` | mixed | `log_sample_weight` -> likelihood weights; private helpers to owners |
| `validation.py` | CORE | `inference/validation.py` |

Confirmed coupling: `inference/loaders.py` imports redshift completion, compact catalog views, LSS completion and galaxy marks while branching on legacy model-kind strings.

## `io/`

`io/results.py` and `io/settings.py` are CORE. Port conservatively and preserve lightweight/JAX-free read paths. Run provenance/fingerprints may be colocated here if clean.

## `lensing/`

All substantive modules are LENSING:

```text
clusters.py
fcpdet.py
file_contract.py
grids.py
lensed_injections.py
marginal_diagnostics.py
observed_catalog.py
pair_tag_selection.py
partitions.py
preflight.py
simulation_config.py
slmarks.py
wlmagnification.py
```

These migrate with the lensing-owned likelihood modules above. Do not rewrite the reviewed mathematics during extraction.

## `cli/`

| Legacy file | Owner | Target |
|---|---|---|
| `inference.py` | mixed | thin core CLI over `infer()`; extension options leave |
| `inference_lensing.py` | LENSING | thin lensing CLI |
| `pixelate.py` | SURVEYS | survey library/CLI |
| `fit_selection.py` | SURVEYS | selection fitting |
| `build_lognormal_completion.py` | LSS | LSS library/CLI |
| `build_joint_lognormal_completion.py` | LSS | LSS library/CLI |
| `build_latent_field.py` | LSS | LSS library/CLI |
| `diagnose_lognormal_completion.py` | LSS | LSS diagnostics |
| `skymaps_to_samples.py` | FUTURE_REVIEW | GW input/gwcat concern, not surveys |
| `analyze.py` | LEGACY_ONLY/FUTURE_REVIEW | result/paper analysis |
| `common.py` | mixed | helpers follow owner; no new common junk drawer |

## Infrastructure disposition

No legacy namespace is copied wholesale. Compatibility aliases may exist temporarily inside `darksirens-core` while parity is established, but new public ownership is by physical/scientific domain.
