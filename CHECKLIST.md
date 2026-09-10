# Reconstruction checklist

## Before porting scientific code

- [x] `darksirens-rebuild` control repo exists
- [x] legacy numerical reference SHA frozen
- [x] architecture and dependency direction recorded
- [x] GP assigned to core
- [x] surveys/LSS/lensing assigned to companion repos
- [ ] complete file-by-file legacy inventory
- [ ] complete test/fixture inventory
- [ ] complete cross-boundary import map
- [ ] write per-repo contracts
- [ ] freeze core golden/parity fixtures

## Core acceptance

- [ ] package uses `src/darksirens`
- [ ] cosmology parity
- [ ] inverse-distance parity
- [ ] GW PE loader parity
- [ ] GW selection loader parity
- [ ] gwcat schema/version guards
- [ ] `chieff` parity
- [ ] `chieff_reference` parity
- [ ] component-spin basis parity
- [ ] parametric population parity
- [ ] GP population parity
- [ ] spectral siren parity
- [ ] complete-catalog parity
- [ ] incomplete-catalog parity
- [ ] bright/counterpart parity
- [ ] host-weight parity
- [ ] GW selection beta parity
- [ ] selection N_eff/variance parity
- [ ] parameter/prior parity
- [ ] TinyNS integration
- [ ] dynesty integration
- [ ] NumPyro smoke path where applicable
- [ ] checkpoint/resume behavior
- [ ] result/provenance IO
- [ ] import-side-effect behavior
- [ ] small root public API examples
- [ ] core imports no companion package

## Surveys acceptance

- [ ] pixelization parity
- [ ] depth-map parity
- [ ] mask/area behavior
- [ ] selection-fitting parity
- [ ] standardized catalog serialization
- [ ] survey-built catalog loads directly in core
- [ ] no GW likelihood/LSS/lensing runtime code

## LSS acceptance

- [ ] Q_LSS table parity
- [ ] missing-count conservation
- [ ] row/pixel ordering
- [ ] ensemble/marginalization
- [ ] single-tracer parity
- [ ] multitracer parity
- [ ] provenance guards
- [ ] latent basis parity
- [ ] latent count likelihood parity
- [ ] latent field normalization
- [ ] full fixed-theta core+LSS parity
- [ ] no runtime dependency on surveys

## Lensing acceptance

- [ ] weak-lensing PDF parity
- [ ] WL quadrature/normalization
- [ ] WL event weighting
- [ ] SIS optical-depth parity
- [ ] image mark parity
- [ ] pair KDE parity
- [ ] pair likelihood parity
- [ ] cluster selection/likelihood parity
- [ ] both-detected approximation behavior
- [ ] exactly-one-detected behavior
- [ ] analytic vs Monte Carlo detection validation
- [ ] lensed-injection/file-contract parity
- [ ] partition enumeration/marginalization
- [ ] full fixed-theta core+lensing parity
- [ ] no LSS/surveys runtime dependencies

## Final ecosystem acceptance

- [ ] clean installs for core and every companion combination
- [ ] wheels/sdists build
- [ ] no duplicated core cosmology/population implementations
- [ ] no forbidden imports
- [ ] no absolute campaign paths
- [ ] no paper-specific event lists in reusable packages
- [ ] all meaningful legacy files have a disposition
- [ ] all mature scientific paths have documented numerical parity
- [ ] legacy reference repository remains untouched
