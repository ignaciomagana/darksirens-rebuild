# Phase 7D — ordinary runtime binding

## Scope

Phase 7D binds the accepted Phase-7 public declarations and standardized data
stores to the already accepted Phase-4/5 fixed-theta likelihood kernels. It is
construction only: no prior-transform assembly, sampler dispatch, checkpoint
policy, result persistence, survey-native loading, LSS/Q machinery, lensing, or
companion-package runtime enters this slice.

Reference state:

```text
legacy repository:  ignaciomagana/darksirens
legacy SHA:         c042527238bd71421b792936bc48c3b815b90d6d
Phase-7 branch:     rebuild/phase7-public-api
7C3 accepted base:  7821c5d4cc6e0d7c21759b66db9fc406b9166939
7D first commit:    cadf829fbfc29bd3ec300f98bdb840aab39a575e
7D accepted head:   1df8f78bb70371b9dae07c6a59a3c9fea2cc8e77
accepted tree:      58e005450715e59456e3778b1431b909d6bb7636
```

## Accepted behavior

`src/darksirens/runtime_binding.py` adds a small sampler-free binding seam:

- `required_fit_columns(analysis)` resolves the selected population's actual
  fitted spin coordinates from the existing population registry;
- PE and detected-injection stores are rejected before likelihood construction
  when their fitted spin density is incompatible with the selected population;
- component-spin stores are stacked in the canonical
  `(a1, a2, cost1, cost2)` runtime order when required;
- RA/Dec are converted to global RING HEALPix IDs with the accepted 7C3
  dependency-free `ang2pix_ring` implementation;
- catalog analyses compact one PE-union-selection catalog with
  `compact_pe_selection_catalog` and replace every sample's global pixel ID by
  its compact catalog-row index;
- the compact catalog retains global HEALPix IDs in `unique_pixels`;
- compact catalog leaves cross the runtime boundary once as JAX arrays;
- `GWEvent` PE/selection containers are built with the already accepted runtime
  helper;
- the observed-density cache is built only for the incomplete-catalog path;
- theta is decoded in the 7C2 frozen order, cosmology -> population -> catalog;
- the ordinary catalog mapping preserves the frozen
  `n0 = 10**log10n0`, with `delta`, `sigma_kde`, and `z_depth` mapped directly;
- the resulting `BoundAnalysis` callable delegates explicitly to the accepted
  spectral, incomplete-catalog, or complete-catalog hierarchical likelihood.

No new science or likelihood arithmetic was introduced.

## Defect found during acceptance

The first 7D commit passed the host-side compaction logic but handed the compact
`GalaxyCatalog`'s NumPy leaves directly into a vmapped JAX catalog evaluator.
That produced a `TracerArrayConversionError` when a traced compact row index
attempted NumPy indexing.

This was a binding-boundary defect, not a Phase-5 kernel defect. Production
likelihood code was left untouched. The only production fix converts the
already validated compact catalog once at bind time:

```python
GalaxyCatalog(
    apix=jnp.asarray(catalog.apix),
    zgals=jnp.asarray(catalog.zgals),
    dzgals=jnp.asarray(catalog.dzgals),
    wgals=jnp.asarray(catalog.wgals),
    ngals=jnp.asarray(catalog.ngals, dtype=jnp.int32),
    unique_pixels=(
        None if catalog.unique_pixels is None
        else jnp.asarray(catalog.unique_pixels, dtype=jnp.int32)
    ),
)
```

The corrected exact head is
`1df8f78bb70371b9dae07c6a59a3c9fea2cc8e77`.

## Acceptance gates

Exact-head 7D gates:

```text
runtime binding:   34622477272 / 103339542168  SUCCESS
broad regression: 34622477307 / 103339541969  SUCCESS
```

The broad regression completed with:

```text
499 passed, 1 skipped
```

The single skip is the existing population-registry golden regeneration test,
which requires `DARKSIRENS_REGEN_GOLDEN=1` and is not a runtime failure.
The companion-import boundary also passed.

Earlier Phase-7 slices replayed green on the same exact 7D head:

```text
7A public loaders:       34622477196  SUCCESS
7B public specs:         34622477305  SUCCESS
7C1 joint-prior resolver:34622477258  SUCCESS
7C2 public model plan:   34622477275  SUCCESS
7C3 HEALPix geometry:    34622477253  SUCCESS
```

## Closure

Phase 7D is accepted at
`1df8f78bb70371b9dae07c6a59a3c9fea2cc8e77`.

The next slice is the thin public `ds.infer()` facade. It should bind the
analysis, build the already accepted portable prior transform, normalize public
sampler options into the existing Phase-6 option contract, and delegate to the
accepted `run_sampler` dispatcher. It must preserve the Phase-6 ordering in
which zero-free exact evidence is returned before sampler-name validation or
backend imports.