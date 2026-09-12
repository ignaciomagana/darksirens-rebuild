# Phase 09 S6 — clean-install, core-consumer integration, and final surveys freeze

Status: **ACCEPTED / DARKSIRENS-SURVEYS FROZEN**

## Frozen references

```text
legacy oracle:          ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
frozen core main:       ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
frozen core tree:       0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
accepted surveys main:  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2
accepted surveys tree:  4c4043ee2bee2a5a8940242e2de37f5eb5dbab17
surveys package version:0.1.0
core package version:   0.1.0.dev0
```

The core scientific/runtime tree was not reopened. `darksirens-core/main` remains
at the Phase-8 frozen SHA above.

## Final surveys surface

The accepted surveys package contains the complete S1-S5 surface:

```text
S1  CatalogRows -> HEALPix RING pixelization -> standardized core-readable HDF5
S2  offline survey-fraction/depth maps
S3  Gaussian/Schechter magnitude-selection fitting + serialized fit payloads
S4  native DESI/Legacy column adapters into CatalogRows
S5  survey-side host-mark centering and descriptive validation
S6  clean wheel, public-surface, and exact frozen-core consumer integration
```

No LSS/Q/latent-field or weak/strong-lensing implementation enters this
companion.

## Exact-head ordinary CI

Accepted surveys head:

```text
head:       f027aef02d342041ce7259cdbf47fe689e6462f2
workflow:   ci
run:        34682603918
job:        103523878119
result:     SUCCESS
pytest:     36 passed
compile:    PASS
firewall:   PASS
```

The firewall confirms the surveys source does not import the LSS/lensing
companions and that its ordinary unit suite remains green at the exact accepted
head.

## Clean-wheel freeze

```text
workflow:   s6-final-freeze
run:        34682603998
job:        103523878256
head:       f027aef02d342041ce7259cdbf47fe689e6462f2
result:     SUCCESS
artifact:   darksirens-surveys-s6-wheel
artifact id:10294401705
artifact digest:
  sha256:de910ec762d890660beb38ac7cde62adc9494e08e88204c0c4395afb0d406660
```

The gate builds one wheel, installs it into a fresh Python 3.11 environment,
runs `pip check`, verifies the frozen public `__all__` surface, confirms that
importing `darksirens_surveys` does not initialize `darksirens`, and compiles the
cross-package integration probe.

## Exact frozen-core wheel used for S6

A wheel was exported from the already-accepted Phase-8 core tree solely for the
cross-package installation gate. The export-only branch change was reverted
after the test; the historical Phase-8 branch is again at its accepted head
`53bf08fd3670da4d2e48a146319c193b9cff8858`, and core `main` was never changed.

The exact core wheel installed by the S6 integration gate was:

```text
darksirens-0.1.0.dev0-py3-none-any.whl
sha256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

A direct sibling-private-repository artifact download using the surveys
repository `GITHUB_TOKEN` was tested first and failed with GitHub `Not Found` at
run `34682485938`; no scientific probe ran in that failed infrastructure-only
attempt. The accepted gate therefore used the already-downloaded artifact via a
transient signed URL and verified the wheel SHA-256 before installation.

No wheel or signed URL is committed to either production main branch.

## Final exact-wheel cross-package gate

The final candidate was replayed after pinning the real-core selection-fit output
to the frozen S0B numerical reference:

```text
surveys production head under test:
  f027aef02d342041ce7259cdbf47fe689e6462f2

temporary harness commit:
  494803bf7f448bdf8987720554d125050afee01c

workflow:   s6-private-crossrepo-probe
run:        34682629290
job:        103523951273
result:     SUCCESS
```

The temporary branch was force-reset to the accepted surveys main after the run,
so the signed-URL harness does not remain at its branch head.

The gate performed, in order:

1. checksum verification of the exact frozen core wheel;
2. build of the surveys wheel from the accepted production tree;
3. fresh Python 3.11 virtual environment;
4. joint installation of the two wheel distributions;
5. `pip check` with no broken requirements;
6. one-way import checks in fresh subprocesses;
7. native DESI/Legacy rows -> S5 centered mark -> S1 standardized catalog;
8. public `darksirens.load_catalog()` consumption of that file;
9. exact equality of core-loaded `zgals`, `dzgals`, `wgals`, and `ngals` to the
   surveys product;
10. real installed-core distance modulus in the S3 Gaussian selection-fitting
    path;
11. numerical comparison of that fit to the frozen S0B reference.

## Cross-package numerical result

Catalog replay:

```text
n_rows:                  6
nside:                    2
catalog shape:            [48, 1]
occupied pixels:          6
occupied_pixel_fraction:  0.125
z_depth:                  0.75
```

Real-core S3 selection replay:

```text
reference Mhat:
  -16.95943450499677
  -19.179360358561794
  -19.905330524840757

Gaussian fit, Ngal=2500:
M0hat:    -20.192377120331184
sigma_M:   0.9917827755129697
NLL:       3346.4622872061723
cov:
  [[4.510544008609971e-4, 6.153253217312926e-5],
   [6.153253217312927e-5, 2.5186823028816314e-4]]
```

The committed S6 probe pins these to the S0B reference with the established
numerical tolerances; the final exact-wheel run passed those assertions.

## Import / ownership result

Both clean subprocess checks passed:

```text
import darksirens_surveys  -> does not import darksirens
import darksirens          -> does not import darksirens_surveys
```

The dependency remains conceptually one-way at the product/API level: surveys
may lazily call core cosmology for offline selection fitting, but core does not
know survey-native schemas and does not import the surveys package.

## Cleanup

After acceptance:

```text
darksirens-surveys/s6-private-crossrepo-probe
  -> reset to accepted surveys main f027aef02d342041ce7259cdbf47fe689e6462f2

darksirens-core/rebuild/phase8-core-freeze
  -> restored to historical accepted head 53bf08fd3670da4d2e48a146319c193b9cff8858
```

No temporary signed-URL workflow is present on either production main branch.

## Verdict

Phase 09 S6 is accepted. `darksirens-surveys` is frozen at
`f027aef02d342041ce7259cdbf47fe689e6462f2`.

The next companion phase is `darksirens-lss`. It must consume only the frozen
core extension seam and standardized survey products; it must not reopen core or
move survey-native construction into the LSS package.
