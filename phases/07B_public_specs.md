# Phase 7B — public cosmology and population specifications

## Status

ACCEPTED

## Core branch / head

```text
repository: ignaciomagana/darksirens-core
branch:     rebuild/phase7-public-api
accepted:   b97d949f32c0eff3bb48c574b5a2258f92fe82d5
parent:     c338bc8eaa5199775e6d1355f20406be8ade1eb1  (accepted 7A)
```

## Scope

Phase 7B adds dependency-light public declarations for the two user-facing
scientific specifications promised by the frozen architecture:

```python
cosmo = ds.Cosmology(H0=(20.0, 140.0), Om0=0.3075)
pop = ds.Population("brokenpowerlaw+2peaks", fixed="gwtc5")
```

These are intent/specification objects only. They do not construct JAX arrays,
likelihoods, population model objects, parameter decoders, or sampler state.

### `Cosmology`

- canonical order: `H0`, `Om0`, `w0`, `wa`;
- finite scalar means fixed;
- `(lower, upper)` means a uniform sampled parameter;
- default samples only `H0` on `[20, 140]` and fixes
  `Om0=0.3075`, `w0=-1`, `wa=0`;
- exposes ordered `free_parameters` and `fixed_parameters` for later analysis
  assembly;
- rejects non-finite, reversed/equal, and malformed declarations.

### `Population`

- preserves the existing model-name registry; no population implementation or
  parameter vector is duplicated;
- `fixed=None/False` means sample the named model;
- `fixed=True` / `fixed="legacy"` selects the existing legacy fiducial set;
- `fixed="in_prior_v2"` selects the existing corrected in-prior set;
- the architecture shorthand
  `Population("brokenpowerlaw+2peaks", fixed="gwtc5")` resolves to the existing
  registered `gwtc5_fiducial_bpl2peaks` model and its already validated
  published-median 17-parameter vector;
- carries the existing `shared_beta`, `shared_spin`, and `shared_gamma` choices.

## Files

```text
src/darksirens/_specs.py
src/darksirens/__init__.py
tests/test_public_specs.py
.github/workflows/phase7b-public-specs.yml
```

## Acceptance gates

Dedicated exact-head 7B gate:

```text
run: 34595489924
job: 103250164326 (public-specs)
status: SUCCESS
```

It passed lint/compile, a fresh-process package-root import guard, and focused
public-spec tests. Root construction of `Cosmology` and `Population` loads no
JAX/HDF5/sampler backend.

Replayed 7A frozen-loader parity on the same exact head:

```text
run: 34595489912
job: 103250164428 (public-loaders)
status: SUCCESS
```

Broad Phase-7 regression on the same exact head:

```text
run: 34595489857
job: 103250163890 (regression)
status: SUCCESS
```

It passed the entire reconstructed test suite and the forbidden companion-import
boundary.

## Exclusions

7B does not add:

- `ds.model()`;
- `ds.infer()`;
- a global parameter decoder;
- survey/LSS/lensing state;
- new population fiducials or priors;
- a `universe_model` switchboard.

## Next slice

Before `ds.model()` can assemble a scientifically complete sampler parameter
plan, port the small generic joint-prior constraint resolver that the frozen
GWTC-5 population requires. Core already owns the accepted cube transform; the
missing resolver maps population-declared constraint groups onto sampled indices
and preserves the normalized simplex / conditional-upper prior. Treat this as a
narrow parity slice before analysis construction.
