# Reconstruction checklist

Reconstruction is complete. Detailed numerical provenance is recorded in the
phase acceptance files; this checklist is only the final ownership/coverage
summary.

## Reference and architecture

- [x] `darksirens-rebuild` control repo exists
- [x] legacy numerical reference SHA frozen and kept read-only
- [x] architecture and dependency direction recorded
- [x] GP assigned to core
- [x] surveys/LSS/lensing assigned to companion repos
- [x] legacy scientific/file inventories completed through per-phase inventories
- [x] test/fixture and cross-boundary ownership maps frozen where each port required them
- [x] per-repo contracts recorded
- [x] core golden/parity fixtures frozen

## Core acceptance — Phase 08

- [x] package uses `src/darksirens`
- [x] cosmology and inverse-distance parity
- [x] GW PE and selection loader parity
- [x] gwcat schema/version guards
- [x] `chieff`, `chieff_reference`, and component-spin basis parity
- [x] parametric and GP population parity
- [x] spectral-siren parity
- [x] complete/incomplete catalog dark-siren parity
- [x] bright/counterpart parity
- [x] host-weight/marked-host parity
- [x] GW selection beta and N_eff/variance parity
- [x] parameter/prior parity
- [x] TinyNS integration
- [x] dynesty integration
- [x] NumPyro smoke path where applicable
- [x] checkpoint/resume behavior
- [x] result/provenance IO
- [x] import-side-effect behavior
- [x] small root public API examples
- [x] core imports no companion package
- [x] final clean-wheel/API freeze

Authoritative record: `phases/08_phase_integration.md`.

## Surveys acceptance — Phase 09

- [x] pixel/catalog construction parity
- [x] depth-map and selection-fraction parity
- [x] mask/area behavior
- [x] selection-fitting parity
- [x] standardized catalog serialization
- [x] native DESI/Legacy adapters
- [x] host-property preparation/validation
- [x] survey-built products consume frozen core contracts directly
- [x] no GW likelihood/LSS/lensing runtime code
- [x] clean-wheel exact frozen-core consumer integration

Authoritative records: `phases/09S6_final_surveys_freeze.md` and
`phases/09_phase_integration.md`.

## LSS acceptance — Phase 10

- [x] Q_LSS table parity
- [x] missing-count conservation
- [x] row/pixel ordering
- [x] ensemble/marginalization
- [x] single-tracer parity
- [x] multitracer parity
- [x] provenance guards
- [x] latent basis parity
- [x] latent count likelihood parity
- [x] latent field normalization
- [x] full fixed-theta core+LSS parity
- [x] no runtime dependency on surveys
- [x] final clean-wheel/frozen-core freeze

Authoritative record: `phases/10L8_final_lss_freeze.md`.

## Lensing acceptance — Phase 11

- [x] weak-lensing PDF parity
- [x] WL quadrature/normalization
- [x] WL event/selection weighting and spectral target composition
- [x] SIS optical-depth/magnification/time-delay primitive parity
- [x] Finn-Chernoff detection validation and orientation convention
- [x] pair KDE parity
- [x] symmetric J=2 pair likelihood parity
- [x] both-detected selection behavior
- [x] exactly-one-detected singleton behavior
- [x] shared-campaign covariance
- [x] lensed-injection/file-contract parity and campaign provenance
- [x] exact partition enumeration/marginalization
- [x] partition-prior normalization
- [x] terms evaluated once and reused across matchings
- [x] fixed campaign-cosmology fail-closed guard
- [x] time-marked edges fail closed while pair surface remains unmarked
- [x] full fixed-theta core+lensing parity
- [x] no LSS/surveys runtime dependencies
- [x] final clean-wheel/frozen-core freeze

Authoritative record: `phases/11L8_full_parity_freeze.md`.

## Final ecosystem acceptance

- [x] clean wheel installs for core and each companion against its accepted dependency contract
- [x] package builds exercised at the final freeze points
- [x] no duplicated core cosmology/population implementation in companions
- [x] forbidden-import firewalls enforced
- [x] no absolute campaign paths in reusable package contracts
- [x] no paper-specific event lists in reusable package contracts
- [x] meaningful mature legacy behavior has an ownership/disposition record
- [x] mature reconstructed scientific paths have documented numerical parity
- [x] legacy reference repository remained untouched
- [x] final repository heads recorded in `STATUS.md`

## Frozen heads

```text
darksirens-core     af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
```

No reconstruction item is currently active. New work belongs in a new
post-reconstruction phase with its own scientific reference and acceptance gate.

## Post-reconstruction Phase 12 — first production consumer

Historical reconstruction freeze remains unchanged. The active Phase 12 consumer uses the separately accepted post-reconstruction core pin `8b9dc64629cf11838a9fc1de233e46b91082caf7`.

- [x] Phase 12 production-analysis contract recorded
- [x] exact four-package consumer manifest established
- [x] Phase 12A generic `CompletionCurves -> IncompleteCatalogPriorState` composition contract recorded
- [x] Phase 12A core implementation accepted on full historical/scientific CI matrix
- [x] Phase 12A post-merge core integrity gate passed
- [x] consumer repinned to accepted Phase 12A core
- [x] fixed-population DESI target implemented with sampler coordinates `(H0, M0hat, sigma_M)`
- [x] fixed GWTC-5 population and fixed DESI count calibration retained
- [x] legacy DESI Gaussian magnitude-selection fit and independent prior semantics retained
- [x] hard PE+selection MC-reliability gate retained
- [x] P12.4 consumer contract CI passed before merge
- [x] P12.4 consumer post-merge CI passed
- [x] fail-closed P12.1 -> P12.4 execution chain implemented
- [x] execution-chain exact-head CI passed
- [x] execution-chain post-merge CI passed
- [x] deployment/runbook and stage ledger contract recorded
- [ ] regenerate P12.1 under the active Phase 12 core pin on the authorized production environment
- [ ] rebuild/fingerprint standardized DESI input if needed
- [ ] regenerate and accept P12.2 pre-inference diagnostics
- [ ] regenerate and accept P12.3 fixed-population spectral-siren baseline
- [ ] execute P12.4 fixed-population DESI inference
- [ ] freeze numerical JSON/NPZ products and run provenance
- [ ] produce production plots only from accepted frozen numerical products
- [ ] run fixed-population robustness matrix before any headline interpretation

Authoritative post-reconstruction records:

```text
phases/12A_completion_curve_composition_acceptance.md
phases/12_fixed_population_desi_implementation.md
phases/12_fixed_population_execution_chain.md
```
