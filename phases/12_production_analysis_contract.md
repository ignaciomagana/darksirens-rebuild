# Phase 12 — First post-reconstruction production analysis

Status: **ACTIVE — CONTRACT ONLY**

This phase is the first scientific consumer of the frozen four-repository `darksirens` ecosystem. It does **not** reopen any accepted reconstruction slice. The accepted package heads below are immutable inputs unless a genuinely missing reusable capability is demonstrated and accepted under a separate package-change contract.

## Frozen package inputs

```text
darksirens-core      af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
darksirens-surveys   f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss       3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing   43c450742b733d7b8d938116021e8ca52a31226e
```

The reconstruction acceptance records remain authoritative for package ownership, interfaces, legacy parity, and fail-closed behavior.

## Scientific target

The first production target is a GWTC-5 + DESI dark-siren Hubble-constant analysis using the frozen ecosystem as a consumer rather than extending the libraries speculatively.

The analysis ladder is ordered so that every new source of information is measured against a simpler baseline:

1. reproduce production input and selection diagnostics;
2. run a GWTC-5 catalog-free spectral-siren baseline with fixed population;
3. add the DESI-supported dark-siren likelihood at identical population and selection settings;
4. marginalize over supported GWTC-5 source-population uncertainty;
5. execute the predefined robustness matrix;
6. freeze numerical products separately from publication plotting.

The exact science sample, catalog cuts, and priors must be recorded in the consumer repository before the first production inference result is accepted. No result is considered production solely because a sampler completes.

## Architecture

Phase 12 uses a dedicated analysis/consumer repository. The consumer may import the frozen packages and contain analysis configuration, provenance manifests, adapters, run orchestration, diagnostics, result tables, and plotting code. It must not duplicate cosmology, population, GW likelihood, selection, survey, LSS, or lensing implementations already owned by the frozen packages; silently patch package behavior; vendor modified package source; or loosen a frozen fail-closed contract to make a run proceed.

A missing generic capability discovered by the consumer is handled by stopping that part of the analysis, opening a new explicit package-change phase, adding a scientific reference/acceptance test, and only then changing a frozen package. The consumer is subsequently repinned to the newly accepted package head.

## Required provenance manifest

Before inference, the consumer must emit a machine-readable manifest containing at minimum:

- exact consumer commit SHA;
- exact SHA/version of every `darksirens-*` dependency;
- Python and major numerical dependency versions;
- source data identifiers and checksums;
- GW PE release and event identifiers;
- selection/injection release and campaign identifiers;
- DESI product/release identifiers and catalog selection definition;
- sky mask and redshift support;
- cosmological parameters held fixed and cosmological priors sampled;
- population model and fixed hyperparameters or hyperposterior source;
- event/sample cuts and any support threshold;
- random seeds for deterministic validation products;
- sampler settings for production inference;
- output file hashes.

The manifest is a required analysis product, not optional bookkeeping.

## Acceptance gates

### P12.1 — consumer bootstrap
A clean environment must install or resolve the four exact frozen package heads and run a smoke test that imports the public consumer-facing interfaces. Recorded package SHAs must match this contract exactly.

### P12.2 — input and selection diagnostics
Before H0 inference, freeze machine-readable diagnostics containing the event list, PE sample counts after cuts, support inside the survey/redshift domain, DESI catalog support, selection/injection counts and effective-sample-size diagnostics, selection behavior over sampled cosmology where applicable, per-event Monte Carlo variance diagnostics, and explicit exclusion reasons. Frozen numerical guards fail closed.

### P12.3 — fixed-population baseline
Run the catalog-free GWTC-5 spectral-siren H0 baseline using the same event, selection, cosmology-prior, and fixed-population settings planned for the first DESI comparison. Freeze posterior samples and a compact numerical summary.

### P12.4 — DESI dark-siren comparison
At identical fixed-population settings, add DESI-supported galaxy information. Freeze per-event H0 products, the combined H0 posterior, selection contribution, and comparison against P12.3.

### P12.5 — population marginalization
Replace the fixed population with the declared GWTC-5 population uncertainty without changing unrelated analysis choices. Quantify the shift and broadening relative to the fixed-population DESI result.

### P12.6 — robustness matrix
Declare the robustness suite before reading its outcome. It must cover the scientifically relevant variants among DESI support/mask definition, event-support threshold, redshift ceiling/catalog cut, observing-run subsets, all-sky versus DESI-masked selection where meaningful, fixed versus population-marginalized inference, PE/selection Monte Carlo variance gates, and any catalog-completeness assumption used by the selected DESI product. All variants are written to one machine-readable summary table.

### P12.7 — production result freeze
Accepted numerical products are frozen independently of plotting code. Figures read frozen results and do not launch or recompute inference. Publication figures must regenerate from frozen numerical products in a clean checkout.

## Initial commit sequence

```text
phase12: define post-reconstruction production contract
phase12: bootstrap frozen ecosystem consumer
phase12: add standardized GWTC-5 and DESI inputs
phase12: add production input and selection diagnostics
phase12: run fixed-population spectral-siren baseline
phase12: add DESI dark-siren likelihood
phase12: add population-marginalized production inference
phase12: add declared robustness matrix
phase12: freeze numerical results and production figures
phase12: accept first production analysis
```

Commit names may be refined to match concrete implementation, but the scientific ordering and acceptance gates must not be collapsed merely to reach a final posterior faster.

## Completion

Phase 12 is complete only when the control repository records the exact accepted consumer SHA, exact package SHAs used, data and result hashes, accepted scientific sample and inference definition, required diagnostics and robustness outcomes, final fixed-population and population-marginalized numerical summaries, and successful reproducibility/CI identifiers.

Until then this file defines an active post-reconstruction production phase; the four reconstruction packages remain frozen.
