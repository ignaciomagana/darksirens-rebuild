# Phase 8 — extension seam and final core-freeze inventory

Status: **INVENTORY FROZEN; NO PRODUCTION COMMIT YET**

```text
phase base / merged main: 6ed3dc74aa0fcde4da128036cc3d56c29250d370
base tree:                 55dfb24cb84edebb0175409bd33be2a6a57ecb8a
legacy reference:          c042527238bd71421b792936bc48c3b815b90d6d
companions:                NOT STARTED
```

## Phase goal

Freeze the smallest core surface that future one-way companion packages can use,
then complete the install/public-example/dependency audit. Phase 8 is not a new
science phase and must not migrate LSS or lensing physics into core.

Architecture constraints remain:

```text
darksirens-surveys -> darksirens
darksirens-lss     -> darksirens
darksirens-lensing -> darksirens
```

Core imports in the reverse direction are forbidden. There is no generic plugin
registry.

## Merged Phase-7 baseline

The ordinary public stack is complete for:

- spectral sirens;
- incomplete ordinary catalog sirens;
- complete ordinary catalog sirens;
- parametric and GP population models;
- isotropic/basic/advanced angular population models;
- TinyNS, Dynesty and NumPyro through the shared sampler stack.

The accepted/merged Phase-7 tree is byte-identical and passed the PR historical /
scientific matrix 30/30. Only reference-integrity push-triggered after merge and
it passed (`34633321021 / 103375170965`).

## Finding 1 — bright sirens are scientifically present but not public

Core already contains the parity-gated bright-siren primitives:

- `catalog.counterparts.Counterpart`;
- counterpart redshift-prior state/evaluator;
- `bright_siren_log_likelihood`;
- one-counterpart-per-event validation;
- the frozen selection convention: the bright PE numerator uses the counterpart
  Gaussian times normalized volume prior, while the selection integral remains
  catalog-free spectral/volume selection.

The frozen legacy input contract is one `RA DEC Z` triplet per GW event, resolved
onto a chosen counterpart HEALPix `nside`; sky-marginalized counterparts bypass
the pixel gate. The reconstructed core intentionally stores the resolved global
pixel in `Counterpart`, rather than carrying raw survey/input parsing.

What is missing is only composition:

- `Counterpart` is not exposed at package root;
- `ds.model()` cannot represent a bright-siren analysis;
- `bind_analysis()` has no bright branch;
- therefore `ds.infer()` cannot run the already-reconstructed bright likelihood.

This is a real Phase-8 gap because the architecture's final acceptance criterion
explicitly includes ordinary bright-siren workflows using the small public API.

### Required slice 8A

Add the smallest typed bright-siren composition over the accepted Phase-5
likelihood. Proposed shape:

- public `ds.Counterpart` (resolved `z`, `dz`, global `pixel`, optional
  `sky_marginalized`);
- a typed bright redshift marker carrying the counterpart tuple and the HEALPix
  `nside` used to map GW PE sky coordinates into the same global pixel frame;
- `ds.model(..., counterparts=..., counterpart_nside=...)` with catalog and
  completeness mutually excluded;
- no catalog nuisance coordinates for bright sirens;
- bind PE samples onto the counterpart pixel frame; selection remains
  catalog-free as in the frozen model;
- require exactly one counterpart per event at bind/runtime;
- initially require `angular='isotropic'` unless frozen parity explicitly proves
  the already-reconstructed bright path supports a non-isotropic factor. Never
  silently ignore an angular request.

No raw counterpart file/CLI parser belongs in core.

Acceptance must compare the public-bound result to the already parity-gated
low-level bright likelihood at fixed coordinates, and replay the Phase-5 legacy
bright parity gate on the exact candidate head.

## Finding 2 — specialized analyses cannot yet consume the sampler stack through a stable seam

The accepted Phase-6 `run_sampler` already takes exactly the reusable pieces:

```text
likelihood callable
prior transform
labels / lower / upper
prior kinds / joint constraints
sampler options
```

The frozen strong-lensing CLI constructs a specialized cluster likelihood and
then calls this same sampler machinery directly. The merged public `ds.infer()`,
however, accepts only ordinary `Analysis` + GW stores and always calls
`bind_analysis()`.

Future `darksirens-lensing` therefore needs a small **public target contract**,
not access to a core universe-model switchboard.

### Required slice 8B

Freeze a tiny sampler-facing analysis target, conceptually:

```python
InferenceTarget(
    log_likelihood=callable,
    parameters=ParameterPlan,
)
```

and one public execution seam that delegates to the exact accepted prior-transform
and Phase-6 sampler dispatcher. A companion owns construction of the specialized
likelihood; core owns only parameter/prior/sampler execution.

Rules:

- no lensing types in core;
- no callback registry or entry-point discovery;
- no companion imports;
- preserve zero-free exact evidence before sampler validation/import;
- ordinary `ds.infer()` behavior must remain unchanged.

A fake external target in tests is sufficient to prove the one-way contract.

## Finding 3 — the redshift/host-density extension contract is absent

The architecture requires a small interface capable of future LSS-conditioned
host-density models, conceptually:

```python
class RedshiftModel(Protocol):
    def parameter_spec(self): ...
    def log_density(self, z, pixel, cosmology, parameters, state): ...
    def log_auxiliary_likelihood(self, parameters, state): ...
```

No such protocol or equivalent stable public contract exists on merged main.
`Analysis.redshift` is a closed union of spectral/incomplete/complete markers and
`bind_analysis()` dispatches those types explicitly.

Critically, the scientific arithmetic needed by an extension is already present:
`likelihood.hierarchical._ordinary_hierarchical_likelihood` is generic over PE
and selection redshift log-density callables. It already owns the frozen
population weight, angular factor, PE reduction, selection integral and total
Monte-Carlo variance guard.

### Required slice 8C

Expose a **small explicit redshift-model contract and generic ordinary reducer**
rather than building a new likelihood layer. The companion should own its state
construction and specialized parameters; core should:

1. call the supplied redshift density for PE and selection samples;
2. run the existing ordinary hierarchical reducer unchanged;
3. add `log_auxiliary_likelihood(parameters, state)` exactly once to the returned
   log likelihood (zero for ordinary/no-auxiliary models);
4. expose enough parameter-block metadata for a companion to combine its block
   with core cosmology/population coordinates and produce an `InferenceTarget`.

The state object may contain a standardized core catalog or latent/count inputs;
core must treat it as opaque and must never learn `Q_LSS`, tracer, or latent-field
semantics.

Acceptance requires a fake external redshift model that reproduces a known core
ordinary density at fixed coordinates plus an auxiliary scalar term. The fake
must live only in tests; no companion package is created in Phase 8.

## Finding 4 — final user/install contract documentation is stale

Merged main builds and tests, but the human-facing freeze files still describe
Phase 2 as current:

- `README.md`;
- `CONTRACT.md`;
- `MIGRATION.md`;
- `VALIDATION.md`.

There is no top-level ordinary public-API example despite the now-stable
`load_* -> Cosmology/Population -> model -> infer` path. The current
`pyproject.toml` is intentionally small and must be verified from a clean wheel /
sdist install rather than expanded speculatively.

### Required slice 8D — final freeze/audit

- update README/CONTRACT/MIGRATION/VALIDATION to the actually merged surface;
- add short executable examples for spectral, catalog and bright ordinary usage;
- build wheel + sdist in CI, install into a clean environment, and smoke-test
  package root plus ordinary examples without the repository on `PYTHONPATH`;
- verify `import darksirens` still does not import JAX, HDF5 or optional sampler /
  GP backends;
- verify core source imports no companion package;
- verify companion-facing contract modules remain dependency-light;
- verify public `__all__` is deliberate and no legacy junk-drawer namespace or
  universe-model dispatcher has reappeared;
- rerun the full historical/scientific matrix before the final Phase-8 merge.

Do not add dependencies merely because the frozen validation environment uses
them. Optional GP/sampler requirements stay lazy unless clean-install testing
proves a real packaging defect.

## Planned slice order

```text
8A — public bright-siren composition
8B — public InferenceTarget / specialized sampler seam
8C — RedshiftModel + generic host-density likelihood seam
8D — install/docs/examples/dependency audit and core freeze
```

This order keeps ordinary core completeness ahead of extension contracts, then
freezes companion-facing APIs only after their underlying sampler/likelihood
primitives are already stable.

Each slice must use the established workflow:

```text
freeze contract / probe
-> smallest production change
-> dedicated exact-head gate
-> Phase-8 broad + historical/scientific replays
-> acceptance record
```

## Explicit non-goals

Phase 8 must not implement:

- DESI/KIBO/Legacy/GLADE ingestion or masks;
- Q_LSS tables or their ensembles;
- latent fields/count likelihood internals;
- multitracer machinery;
- weak/strong lensing physics;
- lensing cluster partition logic;
- campaign CLIs;
- plugin discovery/registries;
- a generalized replacement for `universe_model`.

## Next action

Create a new production branch from exact merged main
`6ed3dc74aa0fcde4da128036cc3d56c29250d370` and implement **8A only**. Do not
start 8B/8C while 8A is unaccepted.