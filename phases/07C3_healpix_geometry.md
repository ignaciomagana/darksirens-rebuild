# Phase 7C3 — portable HEALPix RING geometry

## Status

ACCEPTED

## Exact accepted core head

```text
7821c5d4cc6e0d7c21759b66db9fc406b9166939
```

Parent accepted Phase 7C2 head:

```text
102c233f132cd3b68faaebf4f2adbe71defa731e
```

Production implementation commit:

```text
a729189c819b6ff238d5efc297483f775d83773c
```

The accepted head adds only a workflow dependency correction on top of that production commit.

## Scope

Phase 7C3 reconstructs the one ordinary runtime sky-geometry operation still supplied by legacy `healpy`:

```python
healpy.ang2pix(nside, pi / 2 - dec, ra, nest=False)
```

Core now provides a dependency-free host-side NumPy RING mapper, `darksirens.catalog.geometry.ang2pix_ring`, and exports it from `darksirens.catalog`.

No likelihood, population, model-plan, sampler, survey, LSS, or lensing behavior changed.

## Acceptance probes

Dedicated geometry gate:

```text
workflow: phase7c3-healpix-geometry
run:      34599757756
job:      103263901736
status:   SUCCESS
```

The gate compares the reconstructed mapper element-for-element with the frozen validated reference environment `healpy==1.17.3` over:

- NSIDE = 1, 2, 3, 4, 8, 16, 64, 128, 1024;
- 20,000 deterministic random sky positions per NSIDE;
- RA wrap/quadrant boundaries;
- both poles;
- the HEALPix `|z| = 2/3` equatorial/polar transition and adjacent floating-point values;
- scalar/broadcast behavior and candidate RA periodicity.

Parity is exact (`np.array_equal`). The focused gate also verifies importing the core geometry does not import `healpy` at runtime.

The first dedicated run failed before tests because the focused workflow omitted `h5py`, which the existing `darksirens.catalog` package initializer imports. This was a harness-only failure; production geometry was unchanged. The accepted-head follow-up adds only pinned `h5py==3.12.1` to the focused workflow.

Broad Phase-7 regression:

```text
workflow: phase7-regression
run:      34599757799
job:      103263901914
status:   SUCCESS
```

Exact-head earlier-slice replays:

```text
7A public loaders:      34599757746 / 103263901609 SUCCESS
7B public specs:        34599757739 / 103263901425 SUCCESS
7C1 joint-prior:        34599757883 / 103263902125 SUCCESS
7C2 public model plan:  34599757836 / 103263902059 SUCCESS
```

## Frozen next seam

The next slice is runtime binding, not sampling:

1. consume the accepted `Analysis`, `GWStore`, and `SelectionStore` objects;
2. resolve each store's required spin basis against the selected population model;
3. convert RA/Dec to global RING pixels with accepted `ang2pix_ring`;
4. for catalog analyses, compact one PE-union-selection catalog and remap sample pixels to compact row ids;
5. construct barriered `GWEvent` runtime containers;
6. build the observed-density cache only for the incomplete-catalog path;
7. decode sampler theta into `CosmologyParameters`, the existing population vector, and ordinary `CatalogParameters` (`n0 = 10**log10n0` exactly as frozen legacy);
8. expose a fixed-theta callable delegating only to the already accepted spectral/dark/complete hierarchical likelihood functions.

No `ds.infer()` or sampler orchestration belongs in that slice. Sampling is added only after runtime binding has its own fixed-theta acceptance gate.
