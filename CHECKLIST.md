# Reconstruction checklist

Reconstruction is complete. Detailed numerical provenance is recorded in the
phase acceptance files; this checklist is the live ownership/coverage summary.

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

## Final reconstruction ecosystem acceptance

- [x] clean wheel installs for core and each companion against its accepted dependency contract
- [x] package builds exercised at the final reconstruction freeze points
- [x] no duplicated core cosmology/population implementation in companions
- [x] forbidden-import firewalls enforced
- [x] no absolute campaign paths in reusable package contracts
- [x] no paper-specific event lists in reusable package contracts
- [x] meaningful mature legacy behavior has an ownership/disposition record
- [x] mature reconstructed scientific paths have documented numerical parity
- [x] legacy reference repository remained untouched
- [x] final reconstruction heads recorded in `STATUS.md`

Historical reconstruction heads remain:

```text
darksirens-core     af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
```

No reconstruction item is active. Phase 12 below is post-reconstruction science.

## Post-reconstruction Phase 12 — first production consumer

Active production stack:

```text
darksirens-core     bb4812dc2bf49fe7f4412ba797621b668ccc26a5
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
consumer main       2668ae7e2eb9325910e1a8bec9b7228003cb4942
```

### Contracts and package extensions

- [x] Phase 12 production-analysis contract recorded
- [x] exact four-package consumer manifest established
- [x] Phase 12A generic `CompletionCurves -> IncompleteCatalogPriorState` seam accepted
- [x] Phase 12A post-merge core integrity gate passed
- [x] pre-run audit performed before spending Hildafs compute
- [x] audit identified off-footprint radial-completeness error
- [x] audit identified conditional-vs-field sky-weighting mismatch
- [x] pre-correction P12.4 execution blocked before numerical inference
- [x] Phase 12B correction contract recorded
- [x] Phase 12B core per-row footprint-completeness seam implemented
- [x] Phase 12B field host-density numerator implemented separately from conditional path
- [x] single-catalog field-global-normalizer cancellation explicitly tested
- [x] old conditional path remained unchanged
- [x] Phase 12B core passed Phase-8 broad regression
- [x] Phase 12B core passed Phase-5 pinned-legacy catalog/likelihood parity
- [x] Phase 12B core post-merge integrity passed

### Corrected DESI consumer

- [x] consumer repinned to accepted Phase-12B core
- [x] fixed-population DESI target still uses sampler coordinates `(H0, M0hat, sigma_M)`
- [x] fixed GWTC-5 population retained
- [x] fixed DESI count calibration retained
- [x] legacy DESI Gaussian magnitude-selection fit/prior semantics retained
- [x] target uses `catalog sky weighting = field`
- [x] target uses `C_p(z)=f_p Cbar(z)`
- [x] off-footprint rows use full missing-host budget
- [x] full 259-event policy retained; no DESI-support event cut introduced
- [x] Q/LSS correction remains off for this target
- [x] legacy nside-128 footprint map is an explicit fingerprinted production input
- [x] surveys package owns footprint loading/degradation
- [x] occupied catalog pixels marked uncovered fail closed
- [x] direct P12.4 execution checks live footprint SHA256 and all upstream gates
- [x] hard PE+selection MC-reliability gate retained
- [x] corrected consumer final-head CI passed
- [x] corrected consumer post-merge CI passed
- [x] repository execution marker admits corrected target only
- [x] Phase 12B acceptance frozen in control

### Active production execution chain

- [x] chain order fixed to P12.1 -> input/footprint provenance -> P12.2 -> P12.2b -> P12.3 -> P12.4
- [x] footprint provenance regenerated even when standardized catalog rebuild is skipped
- [x] P12.2b records per-event and detected-injection footprint support without cuts
- [x] stage ledger / fail-closed orchestration retained
- [x] site-neutral Slurm wrapper and Phase-12B runbook present in consumer repo

### Numerical production — next work

- [x] adopt the Phase-12C core pin 8bf2bec5 in the consumer (consumer PR #9, merged cc030f02 on 2026-09-24 without contract CI: Actions billing block, local stand-in run green)
- [ ] re-run the consumer `phase12-contract` workflow on main once Actions is unblocked
- [ ] promote phases/12D_core_deferred_followup_contract.md to an acceptance record with a post-12D core pin (88004d96 or later), or record why not
- [ ] run P12.1 on Hildafs under the exact active package pins
- [ ] resolve/fingerprint the live `mth_map_nside128.h5` footprint product
- [ ] rebuild/fingerprint standardized DESI input if needed
- [ ] regenerate and accept P12.2 pre-inference diagnostics
- [ ] regenerate and accept P12.2b footprint diagnostics
- [ ] regenerate and accept P12.3 fixed-population spectral-siren baseline
- [ ] execute P12.4 fixed-population DESI field inference
- [ ] freeze numerical JSON/NPZ/checkpoint/run provenance
- [ ] accept or reject the H0 posterior from hard diagnostics
- [ ] produce production plots only from accepted frozen numerical products
- [ ] run fixed-population robustness matrix before headline interpretation

### Phase 12E campaign record and Phase 12F guard / GW-product contract change

- [x] A100 campaign measured that the hard guard at cap 1.0 has no finite likelihood on the campaign's real product (N_eff 12,819.5 against 78,639.9 at the GWTC-5 centre)
- [ ] owner decision on the Phase 12E campaign record (darksirens-rebuild PR #10; open, not on `main`)
- [x] guard study: caps 10 and 20 (soft or hard) leave the 1-D and 3-D posteriors unchanged; cap 5 cuts them; the hard guard at cap 1 needs about 14-20 M detected injections
- [x] consumer re-check: P12.4's own GW inputs fail the hard guard at cap 1.0 at all 14 P12.2 probes (N_eff 46,306 against 78,467 at H0 67.74)
- [x] chi_eff-swap and reference-reweighted selection files compared on identical injection rows (the swap gives 3.6x the N_eff)
- [x] owner decisions of 2026-09-26 recorded: soft guard at cap 10; the P12.4 contract changes through a Phase 12 record; reference-reweighting products from gwcat 8f9e2f1
- [x] Phase 12F contract-change record written (proposed, not accepted; pin unchanged)
- [ ] owner accepts or rejects `phases/12F_selection_guard_and_gwcat_products_contract.md`
- [ ] consumer `phase12-contract` CI able to run (Actions billing)
- [x] consumer PR #10 (jit the P12.4 target) merged 2026-09-26 as `5efa8da`, without contract CI (owner's decision)
- [ ] consumer PR implementing 12F (desi_darksirens_selection PR #11) merged under green contract CI on its head and on the merged main (soft cap 10 in P12.2/P12.3/P12.4; dynesty; pinned product sha256, format and spin basis; contract tests updated)
- [ ] PE and selection products rebuilt with gwcat 8f9e2f1 in the Product A definition; `gwcat validate --strict` 84/84; compared with the reference build (a24a5903 / bab92bab)
- [ ] P12.4 builder shown to accept the rebuilt chieff / chieff_reference 2.0 pair
- [ ] P12.1, resolved inputs, P12.2, P12.2b and P12.3 regenerated with the rebuilt products and accepted under the 12F criterion
- [ ] fixed-coordinate check: DESI field target's soft cap-10 total finite and unpenalised at the calibration point and at the P12.3 MAP
- [ ] P12.4 dynesty run converged; penalty measured exactly zero at the posterior mean and median
- [ ] promote 12F to an acceptance record, or record why not

No new H0 posterior is accepted at this checkpoint.

Authoritative post-reconstruction records:

```text
phases/12A_completion_curve_composition_acceptance.md
phases/12_fixed_population_desi_implementation.md
phases/12_fixed_population_execution_chain.md          # historical pre-correction chain
phases/12B_field_footprint_correction.md
phases/12B_field_footprint_acceptance.md
phases/12C_core_review_followup_contract.md
phases/12C_core_review_followup_acceptance.md
phases/12F_selection_guard_and_gwcat_products_contract.md   # proposed, not accepted
```
