# Phase 8D — final core freeze contract

Status: **CONTRACT FROZEN; PRODUCTION NOT YET ACCEPTED**

```text
parent:            875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2
parent tree:       1219bba07d3327c83da0164602e60abe8083ba0b
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
8C dedicated:      34636321077 / 103384995159 SUCCESS
8C broad:          34636321017 / 103384994129 SUCCESS
8C broad result:   534 passed, 1 skipped
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
jax >= 0.4.34
jaxlib >= 0.4.34
numpy >= 1.26, < 3
scipy >= 1.11
h5py >= 3.10
TinyNS pinned to the validated legacy campaign commit
3f9e1b2537f32b59f17ee9ce68b2d725681a024c
```

`scipy` is a base dependency because ordinary completeness code imports
`scipy.special` at runtime. TinyNS is a base dependency because
`ds.infer(..., sampler="tinyns")` is the public default. The default public
example must not require an undeclared backend.

Optional integrations remain extras and lazy:

```text
gp       -> tinygp/equinox
backends -> dynesty and NumPyro through explicit extras
 gwcat    -> the pinned gwcat consumer dependency used only when a store needs
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

Replace the stale Phase-2-era README/CONTRACT/MIGRATION/VALIDATION text with the
actual accepted state through Phase 8C. Documentation must state clearly:

- the pinned legacy reference and parity-first reconstruction rule;
- ordinary dark, complete-catalog, bright/counterpart and spectral paths now
  live in core;
- reusable angular models and sampler/checkpoint/result plumbing live in core;
- `InferenceTarget` and the host-density seam are the intended one-way extension
  boundaries;
- core never imports companions;
- raw survey ingestion/depth/masks remain surveys;
- Q/LSS/latent/count/multitracer state remains LSS;
- lensing-specific physics/state remains lensing;
- no `universe_model` or generic plugin registry exists.

Documentation may summarize accepted validation but must not invent parity runs
that did not occur.

## Example contract

Add small public examples that use only frozen APIs:

1. ordinary inference: standardized PE/injection/catalog loaders -> `Cosmology`
   -> `Population` -> `model` -> `infer`;
2. custom `InferenceTarget`: explicit `ParameterPlan` -> target -> `infer`.

Examples are syntax checked in CI. They must not contain private imports or
campaign-specific paths.

## Fresh-install gate

The dedicated 8D workflow must test the built wheel, not an editable checkout:

1. build a wheel from the exact candidate head;
2. create a clean Python 3.11 virtual environment;
3. install the wheel with dependencies;
4. prove the package-root import is still light;
5. prove declared base runtime imports required by ordinary core are available;
6. prove the pinned TinyNS default backend imports from the installed wheel;
7. construct a zero-parameter `InferenceTarget` and execute
   `ds.infer(target)` with the default sampler argument, preserving the accepted
   zero-dimensional exact-evidence short circuit;
8. compile the public examples;
9. inspect installed metadata and require the expected base/extra dependency
   declarations.

The zero-dimensional smoke deliberately does not run a stochastic nested
sampling campaign; backend execution parity was already accepted in Phase 6.
This gate checks installation and dispatch truth only.

## Acceptance

Phase 8D is accepted only if, on one exact head:

- the dedicated wheel/install/API/documentation gate is green;
- 8C host-density replay is green;
- 8B target replay is green;
- 8A bright/frozen Phase-5 parity replay is green;
- Phase-8 broad regression + companion-import firewall is green;
- the branch tree contains no companion implementation and no scientific
  arithmetic change relative to accepted 8C.

After acceptance, integrate the Phase-8 branch through a PR, verify the merged
`main` tree matches the accepted branch tree, run the post-merge integrity gate,
and mark `darksirens-core` frozen before creating any companion repository.
