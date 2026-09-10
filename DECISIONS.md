# Architecture decisions

This file records decisions that should not be repeatedly reopened unless new evidence requires it.

## D001 — Legacy repo remains the reference

The existing `ignaciomagana/darksirens` repository is not refactored in place. The numerical reference is pinned at:

```text
c042527238bd71421b792936bc48c3b815b90d6d
```

The legacy implementation is read-only during reconstruction.

## D002 — Four new repositories

The ecosystem is:

```text
darksirens-core
darksirens-surveys
darksirens-lss
darksirens-lensing
```

No `darksirens-extra` junk drawer.

## D003 — Core package name stays `darksirens`

The GitHub repository is `darksirens-core`, but the Python distribution/import remains `darksirens`.

## D004 — GP population models stay in core

GP population models are a population-model backend and are part of the direction of the main package. Their heavy dependencies should remain optional where possible.

## D005 — LSS is a first-class companion

Validated LSS/completion/latent-field machinery becomes `darksirens-lss`. It depends on core; core never imports it.

## D006 — Lensing is a first-class companion

Validated weak/strong-lensing machinery becomes `darksirens-lensing`, separate from any existing `gwlensing` project. It depends on core; core never imports it.

## D007 — Survey construction is separate

Raw DESI/Legacy/GLADE ingestion, depth/mask construction, pixelization, survey weighting, and fitting of survey selection functions belong in `darksirens-surveys`. Core consumes standardized catalogs.

## D008 — Public API drives architecture

The target stable vocabulary is deliberately small:

```text
load_events
load_injections
load_catalog
Cosmology
Population
model
infer
```

Internal package boundaries exist to support that API, not to expose implementation complexity.

## D009 — No broad plugin framework

Use explicit composition and only small protocols/interfaces where LSS or lensing actually require an extension seam.

## D010 — Flows are deferred until the ordinary core path is stable

Mature generic PE/pdet flow-surrogate functionality may live in core as an optional feature after the standard PE-sample path passes parity. Do not create another repository solely for flows.

## D011 — Generic marks and angular models remain core concepts

Generic host-property weighting belongs to core catalog/host modeling. Reusable sky/angular source-rate models belong to core population modeling. Survey-specific construction of galaxy properties belongs in surveys.

## D012 — Experiments and scripts are not migrated wholesale

Every file is classified individually. One-off analyses, paper figures, campaign state, superseded diagnostics, and absolute cluster paths remain outside the reusable packages.

## D013 — Numerical parity precedes cleanup

For mature scientific code, first reproduce the legacy fixed-point behavior. Interface cleanup comes only after parity is established.

## D014 — Strong lensing is not forced into the ordinary independent-event likelihood

The core inference layer should expose a small analysis/log-likelihood interface so `darksirens-lensing` can supply cluster-aware likelihoods without contaminating the ordinary core model.

## D015 — Core must be import-clean

Importing lightweight IO/types modules should not initialize unnecessary JAX tables, plotting stacks, LSS, or lensing code. Existing import-side-effect regression behavior is treated as a migration asset.
