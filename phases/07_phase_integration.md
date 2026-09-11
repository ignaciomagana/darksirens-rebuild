# Phase 7 — closure and integration audit

Status: **CLOSED FOR PRODUCTION SLICES; READY FOR PR INTEGRATION**

```text
phase base:       d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
accepted head:    be95e95bdf77144880cba5752ed5feafd40a697f
accepted tree:    55dfb24cb84edebb0175409bd33be2a6a57ecb8a
active branch:    rebuild/phase7-public-api
legacy reference: c042527238bd71421b792936bc48c3b815b90d6d
```

## Closure question

Phase 7 was defined to add only the small conventional ordinary-core construction
and public surfaces deliberately deferred until the scientific kernels and
inference machinery were frozen. The closure audit asks whether any concrete
core-owned ordinary behavior still requires a production slice before
integration.

The answer is **no**. There is no Phase 7G.

## Accepted Phase-7 surface

The target ordinary library path is now fully represented:

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
    angular="isotropic",
)
result = ds.infer(
    analysis,
    events=events,
    injections=injections,
    sampler="tinyns",
)
```

The accepted slices cover every Phase-7 inventory item:

```text
7A  standardized public GW/catalog loaders
7B  declarative Cosmology / Population specifications
7C1 model-declared joint-prior resolver
7C2 typed public model() / parameter plan
7C3 portable HEALPix RING geometry
7D  ordinary runtime binding
7E  thin public infer() facade
7F1 basic angular models
7F2 advanced angular models
7F3 angular parameter/likelihood composition
```

## Whole-phase diff audit

Relative to merged Phase-6 main, the accepted Phase-7 head is exactly 14 commits
ahead and zero behind. Production changes are confined to:

- lazy package-root public facades;
- declarative public specs and typed analysis construction;
- standardized catalog runtime IO and host-side HEALPix geometry;
- a small model-declared joint-prior bridge;
- the public inference facade and runtime binder;
- reusable core angular population models;
- the minimal PE/hierarchical seams required to apply the same angular factor to
  PE and selection weights.

The remainder of the diff is focused tests, parity probes, and Phase-7 workflows.
No raw-survey, LSS/Q, multitracer, lensing, or campaign module was added.

## Architecture audit

The phase satisfies the frozen ownership boundary:

- package-root import remains dependency-light;
- standardized products are consumed directly; raw survey preparation is not in
  core;
- no `universe_model` dispatcher or replacement mega-switchboard was introduced;
- ordinary composition is typed (`SpectralRedshift`,
  `IncompleteCatalogRedshift`, `CompleteCatalogRedshift`);
- parameter order is explicit and compact rather than reconstructed through the
  legacy `ParameterDecoder` machinery;
- `ds.infer()` delegates to the accepted Phase-6 transform/sampler stack rather
  than defining a new backend abstraction;
- angular models are reusable population components and share frozen PE /
  selection weighting semantics;
- the exact-head broad Phase-7 firewall verifies that core imports none of the
  future companion packages.

The intentionally excluded domains remain excluded:

```text
raw DESI/KIBO/Legacy/GLADE schemas and masks       -> darksirens-surveys
Q_LSS / ensembles / latent fields / multitracer    -> darksirens-lss
weak / strong lensing                              -> darksirens-lensing
campaign-specific staged loading and CLI glue      -> not core
```

## Final accepted-head validation

Phase 7F3 exact head:

```text
be95e95bdf77144880cba5752ed5feafd40a697f
```

Dedicated final-slice gate:

```text
34632081722 / 103371081194 SUCCESS
```

Broad regression:

```text
34632081763 / 103371080968 SUCCESS
517 passed, 1 skipped
```

The skip is the existing opt-in population-registry golden regeneration test.
The same broad job passed the core/companion import firewall.

All earlier Phase-7 slice workflows replayed successfully on the same exact
head:

```text
7A  34632081557 / 103371080345 SUCCESS
7B  34632081698 / 103371081242 SUCCESS
7C1 34632081654 / 103371080964 SUCCESS
7C2 34632081670 / 103371080911 SUCCESS
7C3 34632081679 / 103371080994 SUCCESS
7D  34632081612 / 103371081102 SUCCESS
7E  34632081558 / 103371080182 SUCCESS
7F1 34632081584 / 103371080599 SUCCESS
7F2 34632081637 / 103371081339 SUCCESS
```

## Verdict

No legitimate Phase-7 production slice remains. Phase 7 is closed at the
accepted tree `55dfb24cb84edebb0175409bd33be2a6a57ecb8a` and should now be integrated
through a pull request into `main`.

The PR must be evaluated on its actual head/merge state. After merge, record only
post-merge workflows that really run; do not infer or invent a broad post-merge
validation. Phase 8 starts only after the Phase-7 merge is frozen and recorded.