# Dependency edges and required cuts

Reference: `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`.

## Required final direction

```text
darksirens-surveys -> darksirens
darksirens-lss     -> darksirens
darksirens-lensing -> darksirens
```

Forbidden final runtime edges:

```text
darksirens -> darksirens_surveys
darksirens -> darksirens_lss
darksirens -> darksirens_lensing

darksirens_lss -> darksirens_surveys
darksirens_lensing -> darksirens_lss
darksirens_lensing -> darksirens_surveys
```

## Legacy cross-domain edges that must be removed

### 1. Core type contamination

`core/types.py` defines shared containers but `SurveyParams` carries LSS and weak-lensing state. This makes extension concepts structurally mandatory even when unused.

Cut strategy after parity:

- `CosmoParams` -> cosmology owner;
- `GWEvent`/store types -> GW owner;
- standardized catalog type -> catalog owner;
- ordinary survey/completeness parameters -> catalog/selection owner;
- Q/latent/multitracer state -> `darksirens-lss` objects;
- WL/lensing state -> `darksirens-lensing` objects.

Do not make one replacement mega dataclass.

### 2. Ordinary likelihood -> lensing

`likelihood/core.py` directly imports weak-lensing grids/PDFs from `darksirens.lensing`. The ordinary core therefore depends on a specialized extension.

Cut strategy:

- first freeze no-WL and WL golden cells;
- make ordinary event/hierarchical likelihood lensing-free;
- expose only the small event-weight/analysis seam needed by lensing;
- move WL integration into `darksirens-lensing`.

### 3. Redshift prior -> LSS -> likelihood cycle

`redshift/prior.py` owns ordinary spectral/bright/complete/incomplete models, Q ensembles and latent state, and imports `likelihood.latent_q` as its latent seam.

Cut strategy:

- ordinary spectral/catalog/counterpart models remain core;
- define a small redshift/host-density interface;
- LSS objects implement density plus optional auxiliary count/field likelihood;
- remove any core knowledge of `Q_LSS`, latent basis or `latent_q`.

### 4. Inference loader as extension hub

`inference/loaders.py` imports ordinary GW/catalog loaders plus redshift completion builders, compact catalog views, LSS completion and galaxy marks. It constructs multitracer bundles and branches on legacy model-kind strings.

Cut strategy:

- core loader only stages GW, injections, standardized catalog and counterparts;
- `darksirens-lss` constructs its own table/latent state from a core catalog;
- host-property runtime weighting stays core but survey-specific mark construction leaves;
- extension objects contribute parameter specs/state rather than being attached by a global loader.

### 5. Global prior/parameter tables

`inference/prior.py` and `inference/parameters.py` currently encode many feature-specific parameter branches. This is manageable in the monolith but prevents clean companions.

Cut strategy:

- preserve current parameter ordering/priors during parity;
- then let a core parameter space compose parameter specifications from the selected cosmology, population, host/redshift model and analysis extension;
- companion packages own their own parameter declarations.

Do not introduce a general plugin registry.

### 6. Mega likelihood factory

`likelihood/factory.py` is ~148 KB and composes ordinary, LSS, marked, flow and lensing behavior. It is evidence of accumulated orchestration, not a target abstraction.

Cut strategy:

- freeze fixed-coordinate behavior first;
- extract ordinary `model()` construction into a thin core object;
- let LSS provide a redshift/auxiliary-likelihood object;
- let strong lensing provide a specialized analysis object for cluster structure;
- leave sampler orchestration in inference.

### 7. Catalog schema vs survey construction

`catalogs/io.py`, depth maps, selection fitting and experiment ingestion currently blur the boundary between runtime representation and survey-specific preprocessing.

Cut strategy:

- core owns the canonical standardized `GalaxyCatalog` runtime/file contract;
- surveys consumes raw DESI/Legacy/GLADE and emits that contract;
- core never imports survey-specific columns, masks or K-correction builders.

### 8. Selection name collision

There are three distinct ideas called selection:

- `gw/selection.py`: pdet flow -> pseudo-injections;
- `likelihood/selection.py`: canonical Monte-Carlo GW selection integral;
- `redshift/selection.py`: catalog magnitude selection plus fitting.

Final ownership:

```text
core selection/gw.py        canonical injection integral
core selection/diagnostics  Neff/variance/support guards
core selection/catalog.py   runtime catalog-selection evaluation
core selection/emulator.py  optional pdet-flow path
surveys selection/fit.py    fit models from raw survey data
```

## Migration cut order

The safest sequence is:

```text
A  freeze legacy goldens/tests
B  cosmology/types without extension redesign
C  GW store/sample contract
D  populations incl. GP
E  ordinary event likelihood + GW selection
F  ordinary catalog/complete/bright paths
G  inference/samplers/IO
H  freeze minimal redshift/analysis extension interfaces
I  surveys
J  LSS table then latent
K  weak then strong lensing
```

The extension interfaces are frozen only after ordinary core parity, preventing LSS/lensing from independently inventing incompatible core APIs.
