# Phase 12 — fixed-population production execution chain

## Status

**DEPLOYABLE / NUMERICAL EXECUTION PENDING**

This record closes the code-acceptance path for the first post-reconstruction production consumer. It does **not** record a cosmological result. The accepted software stack can now execute P12.1 through P12.4 in a strict fail-closed chain on the authorized production filesystem.

## Active Phase 12 package pins

```text
darksirens-core     8b9dc64629cf11838a9fc1de233e46b91082caf7
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
```

The historical reconstruction freeze remains `af2488b0...` for core. The Phase 12 core pin above is the separately accepted post-reconstruction extension recorded in `phases/12A_completion_curve_composition_acceptance.md`.

## Consumer implementation

Repository:

```text
ignaciomagana/desi_darksirens_selection
```

P12.4 implementation merge:

```text
35bb591718a83e302bfa37356071917f241b841d
```

P12.4 post-merge contract CI:

```text
run: 34807932614
job: 103863360517
status: SUCCESS
```

The implementation samples `(H0, M0hat, sigma_M)` while retaining the GWTC-5 population and DESI count calibration fixed. It uses the accepted Phase 12A completion-curve composition seam and does not duplicate catalog-likelihood algebra in the consumer repository.

## Execution-chain implementation

Consumer PR:

```text
#6 — Phase 12: fail-closed fixed-population execution chain
```

Accepted PR head:

```text
1267ef0ce30bf9fbd104b48d6c85394130758c2e
```

Exact-head PR CI:

```text
run: 34808135123
job: 103863944539
status: SUCCESS
```

Squash merge / consumer main:

```text
1870466391e930e9b90f92adf97723a89f30b2c3
```

Merged tree:

```text
101fa5001c1e3d5d7084802979750074dd844dac
```

Post-merge main CI:

```text
run: 34808164659
job: 103864028184
status: SUCCESS
```

## Fixed gate order

The accepted chain is:

```text
P12.1 frozen environment
optional standardized-input rebuild/fingerprint
P12.2 pre-inference diagnostics
P12.3 fixed-population spectral baseline
P12.4 fixed-population DESI inference
```

The orchestration contains no scientific likelihood or prior implementation. Each stage remains owned by its dedicated runner. The chain stops on the first non-zero return code and writes a stage-by-stage ledger to:

```text
provenance/fixed_population_chain.json
```

The lightweight GitHub CI bypass variable is explicitly removed from the child environment before any production stage is launched.

## Production command

With the exact private package stack installed and the Hildafs roots accessible:

```bash
python scripts/run_phase12_fixed_population_chain.py --prepare-inputs
```

For a pre-existing accepted standardized catalog, omit `--prepare-inputs`. A P12.4 TinyNS checkpoint may be supplied through `--resume-from`; P12.1–P12.3 are still regenerated first.

## Acceptance rule for numerical science

No H0 result is accepted until all of the following exist from one successful chain execution:

```text
provenance/bootstrap_environment.json
provenance/preinference_diagnostics.json
results/phase12/fixed_population_spectral_h0.json
results/phase12/fixed_population_desi_h0.json
results/phase12/fixed_population_desi_samples.npz
provenance/fixed_population_chain.json
```

The chain record must have `status: pass`; both posterior JSON records must be accepted; the package commits must exactly match the active Phase 12 pins; and the hard MC-reliability gates must remain satisfied.

## Current boundary

The code path is accepted and deployable. Numerical P12.1/P12.2/P12.3 records generated before the Phase 12A core repin are stale and must be regenerated. No fixed-population DESI H0 posterior has yet been accepted under the new core pin.
