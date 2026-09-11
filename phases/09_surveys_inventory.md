# Phase 09 — darksirens-surveys inventory / reference freeze

Status: **S0A ACCEPTED / S0B SELECTION-FIT REFERENCE ACTIVE — NO PRODUCTION PORT YET**

This is the first companion-repository stage after the frozen `darksirens-core`.
It corresponds to the reconstruction workflow's survey phase. The frozen core is
not reopened.

## Frozen references

```text
legacy oracle:       ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core dependency:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
core tree:           0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
control baseline:    ignaciomagana/darksirens-rebuild
```

Allowed dependency direction remains one-way:

```text
darksirens-surveys -> darksirens
```

Core must never import the surveys package or learn DESI/Legacy/GLADE native
column names.

## Purpose

`darksirens-surveys` builds reusable survey products. `darksirens-core`
evaluates the standardized products inside inference.

```text
darksirens-surveys: FIT / BUILD survey products
darksirens-core:    EVALUATE standardized products
```

The first acceptance target is not a real-survey adapter. It is the narrowest
schema/geometry seam: normalized galaxy rows -> HEALPix RING pixelization ->
core-readable standardized catalog HDF5.

## Frozen core catalog contract

The first surveys writer must produce the exact surface consumed by
`darksirens.load_catalog()`:

```text
attrs:
  nside      required integer
  z_depth    optional float

datasets:
  zgals      (npix, maxgals)
  dzgals     (npix, maxgals)
  wgals      (npix, maxgals)
  ngals      (npix,)

padding convention:
  z = 100
  dz = 1
  w = 0

ordering:
  HEALPix RING
```

Optional survey-owned/offline datasets such as apparent magnitude, stratum,
and raw host-property columns may be serialized as extensions, but the core
runtime contract above is not enlarged to accommodate native survey schemas.

## Legacy ownership audit

### Direct SURVEYS owners

```text
darksirens/catalogs/depth_map.py
  -> survey depth/mask fraction construction and degradation

darksirens/cli/pixelate.py
  -> generic pixelization / standardized catalog writer

darksirens/cli/fit_selection.py
  -> offline magnitude-selection fitting and provenance

redshift/selection.py (offline fitting portion only)
  -> selection-fit estimators / fit payload construction

catalogs/io.py (raw interpretation portion only)
  -> native/raw survey interpretation moves here; standardized runtime schema
     remains frozen in core

catalogs/marks.py (construction/centering portion only)
  -> raw host-property construction and z-centering; generic runtime host
     weighting remains core
```

### Explicitly NOT surveys

```text
ordinary catalog redshift likelihood       -> core
ordinary count-ratio completeness runtime  -> core
magnitude-selection runtime evaluation      -> core
Q_LSS / lognormal completion / latent field -> darksirens-lss
weak / strong lensing                       -> darksirens-lensing
campaign scripts / paper products           -> legacy-only or future review
```

## Legacy behavior that must be frozen before porting

### Pixelization / writer

Pinned implementation: `darksirens/cli/pixelate.py`.

Freeze deterministic fixtures for:

- RING `ang2pix` assignment;
- `ngals` per-pixel counts;
- stable association of z, dz, weight and optional property columns;
- padding values `z=100`, `dz=1`, `w=0`;
- optional `z_depth` attribute;
- rejection of non-finite/non-positive real-galaxy weights;
- rejection of invalid z / zerr rows;
- preservation of optional mark/property arrays under the real-galaxy prefix;
- emitted file loading directly through frozen `darksirens.load_catalog()`.

The production implementation need not retain the legacy plotting/tqdm/CLI
structure. Only scientific/data-contract behavior is parity-owned.

### Depth / footprint map

Pinned implementation: `darksirens/catalogs/depth_map.py`.

Freeze:

- RING -> NEST child grouping -> RING degradation;
- uncovered children contribute zero survey fraction;
- `f_p = 1 - masked_frac` clipping;
- equal-area degradation semantics;
- coverage report numbers.

Important legacy caveat retained as provenance, not silently fixed during
migration: the shipped `masked_frac` builder may estimate a source-count
fraction rather than an unbiased area fraction. Migration parity and a later
scientific correction are separate changes.

### Selection fitting

Pinned CLI: `darksirens/cli/fit_selection.py` plus the offline fitting portion
of `darksirens/redshift/selection.py`.

Freeze separately from runtime evaluation:

- reference absolute-magnitude convention (`H0=100` h-scaled);
- Gaussian and Schechter fit parameterization;
- magnitude-limit datum semantics;
- stratum handling;
- fixed faint-end protocol constant;
- covariance / Laplace uncertainty ordering;
- fit payload format/provenance;
- H0-invariance tests.

Do not move runtime `C_sel(z; theta)` evaluation out of core.

## S0A — catalog construction / depth-map reference — ACCEPTED

S0a freezes the geometry and standardized-catalog construction semantics before
any companion package exists.

Artifacts:

```text
tools/probe_surveys_build.py
references/surveys_s0a_legacy_reference.json
.github/workflows/surveys-s0a-reference.yml
```

Accepted gate:

```text
run: 34659489558
job: 103458826552
head: 95ad70ac09c4c46cdc2945d02da2694b7425badb
result: SUCCESS
```

The gate checks out the pinned legacy repository in a separate process, executes
the legacy pixelizer and depth-map routines on deterministic fixtures, runs the
probe twice, and requires both outputs to match each other and the committed
golden exactly.

### Legacy equal-pixel row ordering is explicitly NOT a contract

The first raw-array replay exposed a real determinism defect in the legacy
pixelizer:

```python
sort_idx = np.argsort(ind)
```

NumPy's default sort is not stable, so galaxies sharing a pixel can be permuted
between environments/runs. Their pixel membership and all coindexed values are
unchanged. The frozen core loader already normalizes each real pixel row by a
stable redshift sort.

Therefore the S0a comparison contract is:

1. preserve exact RING pixel membership;
2. preserve the complete coindexed galaxy tuple;
3. preserve `ngals`, schema, padding and `z_depth` exactly;
4. canonicalize each real row by stable `zgals` order before parity comparison;
5. do **not** preserve arbitrary legacy quicksort equal-key order.

This is a determinism/harness normalization, not a scientific change. The golden
records `legacy_raw_equal_pixel_order_is_unstable=true` so this exception cannot
be forgotten later.

Depth-map native and degraded `f_p` outputs are exact and did not show this
instability.

## Planned surveys slices

```text
S0  inventory + deterministic legacy reference fixtures
S1  package scaffold + generic normalized-row model + pixelizer + core writer
S2  depth/mask fraction maps and geometry parity
S3  offline selection-function fitting + serialized fit contract
S4  reusable real-survey adapters (DESI/Legacy first; GLADE only if mature)
S5  raw host-property / mark preparation and survey validation utilities
S6  clean-install + core-consumer integration + final surveys freeze
```

Each slice requires its dedicated parity gate plus replay of earlier surveys
slices. No LSS or lensing code enters this package.

## S1 public shape — provisional, not yet frozen

Keep it small and library-first; CLI is a thin wrapper. Conceptually:

```python
from darksirens_surveys import CatalogRows, pixelate_catalog, write_catalog

rows = CatalogRows(ra=..., dec=..., z=..., dz=..., weight=...)
catalog = pixelate_catalog(rows, nside=64, z_depth=0.3)
write_catalog(catalog, "catalog.h5")

# Acceptance condition:
import darksirens as ds
store = ds.load_catalog("catalog.h5")
```

Do not make survey-native column names part of this generic API. Adapters map
native products into `CatalogRows` later.

## Immediate next action

S0b: freeze the offline magnitude-selection fitting behavior separately from the
runtime selection curves that remain in core. The reference should cover at
least:

- Gaussian truncated-LF fit and covariance ordering;
- Schechter fit and `M_faint_offset` protocol semantics;
- reference-absolute-magnitude H0 firewall;
- K-correction handling for the Gaussian family;
- deterministic fit metadata needed by the later serialized selection-fit
  contract.

After S0b is accepted, scaffold `darksirens-surveys` and implement S1 against
S0a. S3 later ports the S0b-frozen fitting behavior.

No `darksirens-core` production write is permitted in this phase.
