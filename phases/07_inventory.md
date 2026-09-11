# Phase 7 — public API inventory and slice design

Status: **IN PROGRESS**

```text
legacy reference: c042527238bd71421b792936bc48c3b815b90d6d
core base:        d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
core tree:        118e196b87538e387d433e4f71edff70b3b3385d
```

## Goal

Phase 7 adds only the small conventional core construction/public surface that
was deliberately deferred until the scientific kernels and inference machinery
were frozen. It must compose accepted core objects rather than recreate the
legacy CLI-era `universe_model`, `load_all_data`, or `ParameterDecoder`
switchboards.

Target ordinary library path remains:

```python
import darksirens as ds

events = ds.load_events("pe.h5")
injections = ds.load_injections("selection.h5")
catalog = ds.load_catalog("catalog.h5")

cosmo = ds.Cosmology(H0=(20.0, 140.0), Om0=0.3075)
pop = ds.Population("brokenpowerlaw+2peaks", fixed="gwtc5")
analysis = ds.model(cosmology=cosmo, population=pop, catalog=catalog)
result = ds.infer(analysis, events=events, injections=injections, sampler="tinyns")
```

## Frozen ordinary-path inventory

### Root/public API

Frozen legacy `darksirens/__init__.py` only exposes `__version__`; legacy
`darksirens/inference/__init__.py` is empty. The mature ordinary user path is
therefore CLI-centric rather than an existing library API. Phase 7 may expose a
small new facade, but every facade must delegate to already frozen scientific
behavior and be separately gated.

### GW posterior and selection loading

Disposition: **already reconstructed core functionality + Phase-7 facade**.

Current core already provides the parity-tested standardized gwcat consumers:

```text
darksirens.gw.samples.load_gw_store        -> GWStore
darksirens.gw.samples.load_selection_store -> SelectionStore
```

They enforce format/layout/quality contracts, spin-basis negotiation including
`chieff_reference`, PE/injection prior weights, counts, attrs and provenance.
Phase 7 should not duplicate this logic. `ds.load_events` and
`ds.load_injections` should be lazy wrappers over these accepted loaders so
`import darksirens` remains lightweight.

### Standardized catalog loading

Disposition: **small conventional Phase-7 core loader**.

Frozen `darksirens.catalogs.io.load_survey` reads only the standardized
pixelated catalog product:

```text
attr:     nside
optional: z_depth
datasets: zgals, dzgals, wgals, ngals
```

It establishes the row-z sort invariant before inference and returns
`(nside, ngals, zgals, dzgals, wgals, z_depth)`. This is an inference-time
consumer of an already-standardized product and therefore belongs in core.

The same frozen module also contains performance machinery and optional
mark/property readers. Raw survey ingestion/pixelization/selection fitting
remain surveys-owned and are not part of 7A. LSS groups/tables are ignored by
the ordinary core loader.

The public catalog object must carry the structural metadata needed later by
model construction (`nside`, `z_depth`) while exposing the accepted Phase-5
`GalaxyCatalog` runtime representation (`apix`, padded rows, optional compact
pixel map). Do not put Q/LSS/marks/lensing state into that object.

### `inference/data.py` and `inference/loaders.py`

Disposition: **do not port wholesale**.

Frozen `load_all_data(opts)` and staged helpers mix ordinary loading with:

- CLI `opts` mutation/provenance recording;
- HEALPix sample mapping and giant flat dictionaries;
- multitracer bundles;
- Q_LSS and LSS overdensity state;
- per-pixel completeness campaign options;
- marks and weak-lensing attachments;
- flow-surrogate/campaign paths.

Phase 7 should replace the ordinary portion with typed objects and explicit
composition. Multitracer/Q/LSS remain `darksirens-lss`; weak/strong lensing
remains `darksirens-lensing`; campaign glue is not reconstructed.

### Parameters, priors and population extraction

Disposition: **later Phase-7 slices, decomposed**.

The frozen `ParameterDecoder`, parameter-space builder and population extractor
are coupled to the legacy switchboard. Their portable pieces will be rebuilt as
small typed construction helpers only after the public loader surface is stable.
The accepted Phase-6 sampler prior transform remains authoritative and is not
rewritten here.

### Angular population model

Disposition: **later Phase-7 slice after ordinary model assembly inventory**.

It is core-owned by architecture, but is independent of the loader facade and
must not be bundled into 7A.

## 7A — standardized public loaders

Chosen first slice:

1. add a tiny ordinary standardized catalog store/metadata record;
2. add a core catalog HDF5 consumer preserving the frozen `load_survey`
   row-sort and `z_depth` semantics;
3. expose lazy root facades:
   - `load_events`
   - `load_injections`
   - `load_catalog`
4. no `model`, `infer`, cosmology/population facade, CLI, companion interface,
   marks, LSS, lensing, or raw-survey logic in this slice;
5. gate the catalog arrays/metadata against frozen `load_survey` on deterministic
   HDF5 fixtures and verify the GW facades return the already accepted store
   objects without changing their behavior;
6. verify importing `darksirens` through the new facade does not eagerly import
   HDF5/JAX/healpy/backend modules.

The Phase-7 branch must start exactly from merged Phase-6 main
`d82becaf76bf62c0f72a71b32ebbf9b238ba4f13`.
