# darksirens reconstruction architecture

## Goal

Reconstruct the current monolithic `darksirens` implementation into a small core package plus three first-class companion packages, while preserving the mature scientific calculations.

The legacy repository is the numerical reference, pinned at:

```text
c042527238bd71421b792936bc48c3b815b90d6d
```

The target repositories are:

```text
darksirens-core
darksirens-surveys
darksirens-lss
darksirens-lensing
```

The Python package produced by `darksirens-core` remains `darksirens`.

## Dependency direction

Allowed runtime dependencies:

```text
darksirens-surveys -> darksirens
darksirens-lss     -> darksirens
darksirens-lensing -> darksirens
```

Forbidden:

```text
darksirens -> darksirens_surveys
darksirens -> darksirens_lss
darksirens -> darksirens_lensing

darksirens_lss -> darksirens_surveys
darksirens_lensing -> darksirens_lss
darksirens_lensing -> darksirens_surveys
```

No generic plugin framework. Extensions enter through small explicit interfaces.

## Public API is the organizing principle

A normal user should be able to understand the workflow from a short script:

```python
import darksirens as ds

events = ds.load_events("pe.h5")
injections = ds.load_injections("selection.h5")
catalog = ds.load_catalog("catalog.h5")

cosmo = ds.Cosmology(H0=(20.0, 140.0), Om0=0.3075)
pop = ds.Population("brokenpowerlaw+2peaks", fixed="gwtc5")

analysis = ds.model(
    cosmology=cosmo,
    population=pop,
    catalog=catalog,
)

result = ds.infer(
    analysis,
    events=events,
    injections=injections,
    sampler="tinyns",
)
```

The user should not need to construct `CosmoParams`, `SurveyParams`, `GWEvent`, call `get_redshift_prior`, `make_likelihood`, `build_parameter_decoder`, or understand `model_kinds` for an ordinary run.

## darksirens-core

Target scientific namespaces:

```text
src/darksirens/
    cosmology/
    population/
    gw/
    catalog/
    selection/
    likelihood/
    inference/
    io/
```

Core owns:

- JAX-compatible cosmology and interpolation;
- GW PE and injection representation/loaders;
- the gwcat HDF5 consumer contract, including spin-basis negotiation and `chieff_reference`;
- PE importance weighting;
- parametric GW population models;
- GP population models;
- reusable angular population models;
- standardized galaxy-catalog representation;
- ordinary catalog redshift kernels;
- ordinary completeness;
- reusable host-property weighting;
- bright-siren counterparts;
- GW selection integrals and diagnostics;
- ordinary hierarchical likelihood;
- parameter/prior assembly;
- sampler adapters;
- checkpointing, results and provenance IO;
- mature generic flow-surrogate support only after the ordinary sample path is stable.

Core explicitly does not own raw survey construction, LSS field reconstruction, or lensing-specific physics.

Do not recreate public junk-drawer namespaces such as `core`, `utils`, or a giant `redshift` dispatcher.

## darksirens-surveys

Purpose: turn real survey products into the standardized catalog representation consumed by core.

Owns:

- catalog pixelization;
- survey masks and depth maps;
- reusable DESI/Legacy/GLADE ingestion;
- survey weights and raw-column interpretation;
- selection-function fitting;
- standardized catalog export and validation.

The boundary is strict:

```text
darksirens-surveys: FIT/BUILD survey products
darksirens:         EVALUATE them inside inference
```

Core must never know DESI-specific column names.

## darksirens-lss

Purpose: mature LSS-conditioned missing-galaxy and latent-field inference.

Owns:

- Q_LSS tables;
- lognormal completion;
- LSS table ensembles/marginalization;
- latent-field bases;
- count likelihoods;
- single- and multi-tracer machinery;
- missing-count normalization;
- LSS provenance and diagnostics.

LSS consumes the standardized core catalog and exposes a redshift/host-density model. Core must not know what `Q_LSS` or a latent field is.

## darksirens-lensing

Purpose: mature weak- and strong-lensing extensions.

Owns:

- weak-lensing magnification PDFs and quadrature;
- SIS optical depth and image marks;
- pair KDEs and pair likelihoods;
- cluster selection/likelihoods;
- exactly-one/both-detected logic;
- lensed-injection formats;
- partition enumeration/marginalization;
- lensing file contracts, preflight, simulation and diagnostics.

Core must contain no `WLParams`, `SISLensParams`, cluster state, lensed-injection state, or imports from the lensing package.

## Composition replaces universe-model switchboards

Do not reconstruct a giant `get_redshift_prior(universe_model=...)` or make a `universe_model` string the primary architecture.

Examples:

```python
# spectral
analysis = ds.model(cosmology=cosmo, population=pop)

# ordinary dark siren
analysis = ds.model(cosmology=cosmo, population=pop, catalog=catalog)

# complete catalog
analysis = ds.model(
    cosmology=cosmo,
    population=pop,
    catalog=catalog,
    completeness="complete",
)
```

Specialized packages supply specialized model objects through small interfaces.

## Minimal extension seams

Core needs a small redshift/host-density interface capable of ordinary catalog models and LSS extensions, conceptually:

```python
class RedshiftModel(Protocol):
    def parameter_spec(self): ...
    def log_density(self, z, pixel, cosmology, parameters, state): ...
    def log_auxiliary_likelihood(self, parameters, state): ...
```

Ordinary models return zero auxiliary likelihood; latent LSS may contribute a galaxy-count/field term.

Core inference also needs a small analysis interface so strong-lensing cluster likelihoods can use core parameter/sampler infrastructure without forcing cluster physics into the ordinary independent-event model.

## Legacy disposition

Every meaningful legacy file receives one disposition:

```text
CORE
SURVEYS
LSS
LENSING
LEGACY_ONLY
FUTURE_REVIEW
```

Do not migrate `experiments/` or `scripts/` wholesale. Extract only reusable algorithms, validation fixtures/tests, and thin CLI functions. Paper-specific campaigns remain outside the reusable packages.

## Scientific migration rule

Architecture and science are not changed simultaneously.

For a mature path:

```text
identify legacy implementation
-> identify legacy tests
-> freeze numerical reference
-> port smallest coherent unit
-> compare at fixed parameters
-> only then simplify internals/API
-> rerun parity
```

Fixed-theta likelihood and selection parity are mandatory. Posterior similarity alone is not sufficient.

## Final acceptance

The reconstruction is complete only when ordinary spectral/dark/bright/population/GP workflows use the small public API; surveys produce core-readable catalogs; LSS and lensing integrate through one-way interfaces; mature fixed-point likelihood paths match the pinned legacy implementation; core imports no companion package; and campaign-specific code has not leaked into the reusable packages.
