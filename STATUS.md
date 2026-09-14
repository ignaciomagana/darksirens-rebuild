# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

The legacy repository remained read-only throughout reconstruction. Numerical
behavior was frozen with deterministic reference probes before companion
production ports were accepted.

## Current state

**RECONSTRUCTION COMPLETE / FOUR-REPOSITORY ECOSYSTEM FROZEN**

```text
darksirens-core
  main: af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
  tree: 0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
  phase: 08 — COMPLETE / FROZEN

darksirens-surveys
  main: f027aef02d342041ce7259cdbf47fe689e6462f2
  phase: 09 — COMPLETE / FROZEN

darksirens-lss
  main: 3429bb2f420239bc731cc9e73e50bf5351181c14
  phase: 10 — COMPLETE / FROZEN

darksirens-lensing
  main: 43c450742b733d7b8d938116021e8ca52a31226e
  tree: 9d79f113d5bf216c90beb13947d190c7da5bb9ca
  phase: 11 — COMPLETE / FROZEN
```

There is no active reconstruction production slice. New scientific development
should start as a post-reconstruction phase rather than modifying an accepted
slice without a new reference/acceptance contract.

## Dependency ownership

The final ownership direction is intentionally one-way:

```text
surveys  -> core contracts
lss      -> core contracts
lensing  -> core contracts

core     -X-> surveys
core     -X-> lss
core     -X-> lensing
lss      -X-> surveys at runtime
lensing  -X-> surveys/lss at runtime
```

Core owns cosmology, ordinary population models, ordinary GW likelihood and
selection machinery, common runtime records, parameter plans, and sampler
execution. Companion repositories own only their domain-specific data adapters,
state, likelihood extensions, selection extensions, and composition seams.

## Phase 08 — core

Status: **ACCEPTED / FROZEN**

```text
final main:             af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
final tree:             0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
Phase-8 PR:             #7
post-merge integrity:   34642213518 / 103404444142 — SUCCESS
record:                 phases/08_phase_integration.md
```

The frozen core includes the reconstructed foundation, population models,
spectral and catalog siren likelihoods, selection machinery, inference and
checkpointing, public specifications/loaders, host-density extension seam, and
final clean packaging/API surface. The final accepted broad result was 534
passed and 1 skipped; the merged Phase-8 tree is byte-identical to the accepted
branch tree.

## Phase 09 — surveys

Status: **ACCEPTED / FROZEN**

```text
final main: f027aef02d342041ce7259cdbf47fe689e6462f2
record:     phases/09S6_final_surveys_freeze.md
integration: phases/09_phase_integration.md
```

The frozen surveys companion owns generic catalog construction, pixel/depth
maps, magnitude-selection fitting, native DESI/Legacy adapters, host-property
preparation/validation, and the clean installed-core consumer integration.
It does not own GW likelihood, LSS, or lensing runtime physics.

## Phase 10 — LSS

Status: **ACCEPTED / FROZEN**

```text
final main: 3429bb2f420239bc731cc9e73e50bf5351181c14
record:     phases/10L8_final_lss_freeze.md
```

The frozen LSS companion closes Q_LSS/missing-count behavior, row/pixel
ordering, ensemble and multitracer likelihoods, latent-field basis/count
likelihoods and normalization, provenance guards, and full fixed-theta
core+LSS parity. It has no runtime dependency on surveys.

## Phase 11 — lensing

Status: **ACCEPTED / FROZEN**

```text
L1-L6 accepted base:       44ba42ce16a9b8cff803787e3f95f2e3439ad0ff
L7 partition target merge: 90f5af30b21a94578cdcc17b3abd0261cbaca7be
L8 final PR:               #7
L8 cleaned head:           47de69eb0af88f9b5624f413edbc4514faa0eeaa
final merge/main:          43c450742b733d7b8d938116021e8ca52a31226e
final tree:                9d79f113d5bf216c90beb13947d190c7da5bb9ca
```

Final L8 acceptance provenance:

```text
legacy full-stack oracle:
  run/job:      34801979805 / 103846292519 — SUCCESS
  artifact ID:  10331633680
  ZIP SHA256:   0799a503b0f5a0df53fa3b6fd2be91e88d2a5bce9840eec831d35719bc09c8e1

exact frozen-core wheel:
  artifact ID:  10294880218
  wheel SHA256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273

exact-core L8 acceptance:
  run/job:      34803362718 / 103850299537 — SUCCESS

cleaned PR permanent CI:
  run/job:      34803511407 / 103850725790 — SUCCESS

post-merge main CI:
  run/job:      34803573222 / 103850905904 — SUCCESS

final record:
  phases/11L8_full_parity_freeze.md
```

Phase 11 freezes weak-lensing PDF/quadrature and spectral composition, SIS and
Finn-Chernoff primitives, pair KDE/evidence, both-detected and exactly-one
selection channels with shared-campaign covariance, campaign I/O and provenance,
exact graph-match partitions, and the full partition-marginalized lensing
`InferenceTarget`.

The mature lensed injection campaign contains detection membership rendered at
a fixed campaign cosmology. The reconstructed target therefore fails closed for
variable-cosmology use; a future cosmology-dependent strong-lensing analysis
requires a new detection rendering/emulator rather than silently reusing those
flags. The frozen L4 pair surface is also explicitly unmarked in arrival time;
time-marked edges fail closed until a marked likelihood is implemented.

## Final acceptance ledger

The detailed phase records, not historical unchecked checklist items, are the
authoritative scientific provenance. The final freeze points are:

```text
08 core:     phases/08_phase_integration.md
09 surveys:  phases/09S6_final_surveys_freeze.md
10 LSS:      phases/10L8_final_lss_freeze.md
11 lensing:  phases/11L8_full_parity_freeze.md
```

The reference-generating control files remain in this repository and the legacy
oracle remains pinned at `c042527238bd71421b792936bc48c3b815b90d6d`.

## Post-reconstruction Phase 12 — first production consumer

Status: **IMPLEMENTATION ACCEPTED / PRODUCTION NUMERICAL RUN PENDING**

The historical reconstruction freeze above remains authoritative for Phases 08–11. Phase 12 is a separately accepted post-reconstruction extension and consumer; it does not rewrite the reconstruction freeze.

Active Phase 12 pins:

```text
darksirens-core     8b9dc64629cf11838a9fc1de233e46b91082caf7
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
```

Phase 12A composition-only core extension:

```text
record:     phases/12A_completion_curve_composition_acceptance.md
core merge: 8b9dc64629cf11838a9fc1de233e46b91082caf7
post-merge: 34807249732 / 103861422867 — SUCCESS
```

First production consumer:

```text
repository:      ignaciomagana/desi_darksirens_selection
P12.4 merge:     35bb591718a83e302bfa37356071917f241b841d
chain merge:     1870466391e930e9b90f92adf97723a89f30b2c3
chain tree:      101fa5001c1e3d5d7084802979750074dd844dac
post-merge CI:   34808164659 / 103864028184 — SUCCESS
control record:  phases/12_fixed_population_execution_chain.md
```

The accepted chain is P12.1 frozen-environment verification → optional standardized DESI rebuild/fingerprint → P12.2 diagnostics → P12.3 fixed-population spectral baseline → P12.4 fixed-population DESI inference. It stops on the first failed gate. No new H0 result is accepted yet; old P12.1/P12.2/P12.3 products produced before the Phase 12A core repin are stale and must be regenerated on Hildafs under the exact active Phase 12 pins.
