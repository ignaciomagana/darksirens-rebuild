# Phase 8D — final core freeze contract

Status: **ACCEPTED ON EXACT HEAD; PHASE-8 INTEGRATION PENDING**

```text
parent:            875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2
parent tree:       1219bba07d3327c83da0164602e60abe8083ba0b
accepted head:     53bf08fd3670da4d2e48a146319c193b9cff8858
accepted tree:     0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Purpose

Close the reconstructed core without changing scientific arithmetic. Phase 8D
owns only packaging truth, the frozen public surface, user-facing examples and
final installation/documentation validation.

No likelihood, selection, cosmology, population, catalog, GW-data or sampler
algorithm may change in this slice.

## Packaging contract

The base distribution must install everything required by the advertised
ordinary public path and its default sampler:

```text
jax == 0.4.34
jaxlib == 0.4.34
numpy == 1.26.4
scipy == 1.12.0
h5py == 3.12.1
TinyNS pinned to
3f9e1b2537f32b59f17ee9ce68b2d725681a024c
```

`scipy` is a base dependency because ordinary completeness code imports
`scipy.special` at runtime. TinyNS is a base dependency because
`ds.infer(..., sampler="tinyns")` is the public default. The default public
example must not require an undeclared backend.

Optional integrations remain extras and lazy:

```text
gp       -> tinygp/equinox
dynesty  -> Dynesty backend
numpyro  -> NumPyro backend
gwcat    -> pinned gwcat consumer dependency used only when a store needs
            the canonical chi_eff prior
test     -> test-only validation dependencies
```

Installing or importing base core must not install/import survey, LSS or lensing
companion packages.

## Public API freeze

The package-root public surface is frozen to the current explicit contract:

```python
configure_jax_runtime
Cosmology
Population
Counterpart
ParameterPlan
InferenceTarget
load_events
load_injections
load_catalog
model
infer
```

Root import remains dependency-light: `import darksirens` must not import JAX,
h5py, TinyNS, Dynesty, NumPyro, tinygp, gwcat or any companion package.

Specialized extension seams remain explicit subpackage APIs; they are not added
to the ordinary package-root surface in 8D.

## Documentation freeze

The stale Phase-2-era README/CONTRACT/MIGRATION/VALIDATION text was replaced by
the actual accepted state through Phase 8C. The frozen documentation states:

- the pinned legacy reference and parity-first reconstruction rule;
- ordinary dark, complete-catalog, bright/counterpart and spectral paths live in
  core;
- reusable angular models and sampler/checkpoint/result plumbing live in core;
- `InferenceTarget` and the host-density seam are the intended one-way extension
  boundaries;
- core never imports companions;
- raw survey ingestion/depth/masks remain surveys;
- Q/LSS/latent/count/multitracer state remains LSS;
- lensing-specific physics/state remains lensing;
- no `universe_model` or generic plugin registry exists.

## Example contract

Two public examples were added using only frozen root APIs:

1. ordinary inference: standardized PE/injection/catalog loaders -> `Cosmology`
   -> `Population` -> `model` -> `infer`;
2. custom `InferenceTarget`: explicit `ParameterPlan` -> target -> `infer`.

The examples are syntax checked in CI and contain no private core imports.

## Fresh-install gate

The dedicated workflow tests the built wheel rather than an editable checkout:

1. requires zero scientific-source diff from accepted 8C;
2. builds the wheel;
3. creates a clean Python 3.11 virtual environment;
4. installs the wheel with declared dependencies and runs `pip check`;
5. proves package-root import remains light and the frozen public API is exact;
6. proves the validated base runtime and pinned TinyNS default backend import;
7. inspects installed metadata for the base pins and optional extras;
8. executes a zero-parameter `InferenceTarget` with the default sampler argument,
   preserving the exact-evidence short circuit;
9. compiles the public examples and rejects private imports;
10. rejects stale reconstruction documentation.

The zero-dimensional smoke deliberately does not run a stochastic nested
sampling campaign; backend execution parity was already accepted in Phase 6.

## Acceptance

All required gates passed on the same exact head:

```text
8D wheel/install/API/docs: 34640864579 / 103399889477 SUCCESS
8C host-density replay:    34640864573 / 103399889300 SUCCESS
8B target replay:          34640864514 / 103399889791 SUCCESS
8A bright/parity replay:   34640864511 / 103399889303 SUCCESS
Phase-8 broad regression:  34640864495 / 103399889097 SUCCESS
broad result:              534 passed, 1 skipped
companion import firewall: PASS
```

The dedicated 8D gate also proved that `src/darksirens` has **no diff** from the
accepted 8C head `875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2`.
Thus 8D changes packaging, documentation, examples and validation only; it does
not alter scientific/runtime implementation.

### Harness-only repair history

Two earlier candidate heads reached the same successful wheel/install/API checks
but failed brittle final documentation assertions:

```text
3f67c61900ae6513ad5dc23e69e7abc44d1551b9
  run/job: 34640476226 / 103398636654
  failure: documentation grep assertion only

54dc2e3ad8817a7da693da57830b7e372fbb7721
  run/job: 34640706728 / 103399379315
  failure: case-sensitive host-density documentation grep only
```

Both repairs changed the workflow harness only. Package metadata, documentation,
examples and all scientific source files were unchanged after the initial 8D
candidate.

## Next integration step

Integrate `rebuild/phase8-core-freeze` through a PR. Merge only after the PR's
required historical/scientific matrix is green. Then verify that merged `main`
has tree `0608b75ff5c142bfba0fc15a4fad79e0fee1fa74`, run the post-merge integrity
gate, update the control-plane status, and mark `darksirens-core` frozen before
creating any companion repository.
