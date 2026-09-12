# Phase 10 L0C — loaded-Q ensemble reference freeze

Status: **ACCEPTED / FROZEN**

## Oracle

Pinned legacy repository:

- `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`

Accepted control-repo commit:

- commit `54ebcc52b6fa686b0440027831a7419d5ece672b`
- tree `5b3ce27f82f13844e969a8929ecfd72d96a23d14`

Accepted GitHub Actions replay:

- run `34685957172`
- job `103532869763`
- conclusion: **success**
- artifact id `10295113816`
- artifact digest `sha256:e38d2291fd8f67d7760d51839c5816c91a7148b3e003b7528c91cccbd4169188`

Frozen numerical oracle:

- `references/lss_l0c_legacy_reference.json`

Probe / workflow:

- `tools/probe_lss_ensemble.py`
- `.github/workflows/lss-l0c-reference.yml`

## Frozen semantics

1. Raw member tables are interpreted as `Q_m = exp(clip(logQ_m, -7, +7))`.
2. Deterministic ensemble fallback is `mean_m(Q_m)`, not `exp(mean_m(logQ_m))`.
3. Each member has its own missing density, integrated `N_miss,m`, and prior normalizer `Z_m`.
4. Depth relaxation is nodewise before interpolation. A query just above a non-grid-aligned depth can retain member dependence because its interpolation bracket straddles the depth edge.
5. Even where the local numerator has fully relaxed to `Q_m=1`, normalized conditional member priors can still differ through member-specific integrated `Z_m` values accumulated below the depth.
6. Bayesian LSS-member marginalization is over **complete likelihoods**:

   `log L = logsumexp_m(log L(Q_m)) - log M`.

   Averaging Q first is a distinct deterministic approximation and is not the Bayesian member marginalization.
7. PE and selection must use the same member realization. Member PE paired with posterior-mean-Q selection is rejected because the per-member prior normalizer cancellation is broken.
8. For K-catalog mixtures, member `m` is a shared realization across catalogs. Production verification requires equal non-null `realization_set_id` and equal `M`.
9. `member_content_sha256` is per-file provenance and is **not** required to match across surveys; different survey responses to the same shared field legitimately produce different member bytes.
10. Legacy / mismatched realization sets fail closed unless the explicit independent-fields approximation override is selected.

## Numerical anchors

Four-member likelihood fixture:

- per-member log likelihoods: `[0.539810404001166, 0.48005411106323237, 0.4409236688466933, 0.40925007984185413]`
- member spread: `0.13056032415931185`
- `logmeanexp`: `0.4687017948971439`
- legacy reference implementation: `0.4687017948971439`
- legacy factored implementation: `0.4687017948971475`

Deterministic fallback fixture:

- scalar ensemble: `0.46296655566007416`
- explicit mean-Q table: `0.46296655566007416`

Depth fixture:

- edge member spread: `0.06856150510352776`
- far-above-depth member spread: `0.00035056717219106304`
- far-above-depth relation to `-log Z_m`: exact within the probe (`max_abs = 0.0`)

## Numerical-comparison policy

Discrete structure, provenance, raw-input hashes, dimensions, and failure modes are compared exactly. Computed JAX/NumPy floating outputs are compared with tight numerical tolerances because independent runner processes can differ in last-bit arithmetic. This is the same portability class already observed in L0A/L2 and is not treated as a scientific-semantic difference.

## L3 constraint

L3 must first implement the transparent reference path: evaluate the complete frozen-core host-density likelihood once per matched Q member and reduce with `logmeanexp`. No factoring or performance optimization is accepted until this reference path reproduces L0C and preserves PE/selection member pairing and realization-set provenance.
