# Phase 11 — darksirens-lensing inventory / reference freeze

Status: **L0 INVENTORY ACTIVE — NO PRODUCTION PORT YET**

## Frozen references

```text
legacy oracle:       ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core dependency:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
core tree:           0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
exact core wheel:    darksirens-0.1.0.dev0-py3-none-any.whl
core wheel SHA256:   4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
surveys dependency:  none at runtime
LSS dependency:      none at runtime
lensing repository:  ignaciomagana/darksirens-lensing (empty at phase start)
```

The dependency direction is one way:

```text
darksirens-lensing -> darksirens-core
```

Core must never import the lensing companion.  The lensing companion must not
require `darksirens-surveys` or `darksirens-lss` at runtime.

## Core extension seam

The frozen core deliberately assigns lensing to a specialized companion.  The
sampler-facing contract is `darksirens.InferenceTarget`:

```python
InferenceTarget(
    log_likelihood=callable,
    parameters=ParameterPlan(...),
)
```

The companion constructs its own opaque lensing state and likelihood closure;
core owns the common parameter/prior/sampler execution contract.  Phase 11 must
therefore not recreate the legacy `universe_model` dispatch table or teach core
about lensing classes or modes.

Core remains the owner of reusable non-lensing machinery:

```text
cosmology
standardized GW PE / injection stores
population models
ordinary GW selection primitives
parameter / prior assembly
sampler adapters
checkpoint / result / provenance infrastructure
```

Lensing owns only the lensing forward model, lensing-specific event/selection
terms, lensing data contracts and partition composition.

## Legacy ownership audit

### Direct lensing owners

The pinned legacy tree contains the following dedicated package:

```text
darksirens/lensing/grids.py
  Gauss-Legendre ln(mu) and y grids; Gaussian/Hermite u grid

darksirens/lensing/wlmagnification.py
  weak-lensing p_WL(mu|z), lognormal and tabulated backends

darksirens/lensing/slmarks.py
  SIS optical depth, p(y), image magnifications and time-delay mark

darksirens/lensing/fcpdet.py
  Finn-Chernoff image detection probabilities and pair-orientation models

darksirens/lensing/clusters.py
  cluster / pair metadata containers and I/O

darksirens/lensing/lensed_injections.py
  lensed J=2 selection-injection representation and provenance

darksirens/lensing/pair_tag_selection.py
  candidate-pair tag selection model

darksirens/lensing/partitions.py
  singleton/pair partitions and partition enumeration

darksirens/lensing/observed_catalog.py
  unified observed-lensing catalog schema

darksirens/lensing/file_contract.py
  formal lensing file-contract validators

darksirens/lensing/preflight.py
  lensing-specific cross-file consistency checks

darksirens/lensing/simulation_config.py
  mock/simulation configuration contract

darksirens/lensing/marginal_diagnostics.py
  diagnostics for the lensing marginal likelihood
```

### Lensing physics living under the legacy likelihood package

Several mature lensing algorithms live in the old monolithic
`darksirens/likelihood` namespace.  Their behavior belongs to the companion,
not to frozen core:

```text
darksirens/likelihood/wl_weight.py
  weak-lensing event-sample weight / mu marginalization

darksirens/likelihood/pair_kde.py
  apparent-frame PE KDE used by image-pair likelihoods

darksirens/likelihood/cluster_likelihood.py
  J=2 pair likelihood / mark composition

darksirens/likelihood/cluster_selection.py
  lensed pair / singleton selection terms

darksirens/likelihood/likelihood_with_clusters.py
  old combined singleton + cluster reducer
```

`likelihood_with_clusters.py` is primarily an integration oracle.  Its
monolithic object graph is **not** a migration target.  Reconstruct the
lensing-owned arithmetic around frozen-core primitives and expose the result as
an `InferenceTarget`.

### Explicitly not lensing

```text
population models / source-frame population weights -> darksirens-core
ordinary spectral-siren likelihood                   -> darksirens-core
ordinary GW injection selection                      -> darksirens-core
sampler execution / priors / checkpoints / results   -> darksirens-core
survey-native products                               -> darksirens-surveys
Q / latent density fields                            -> darksirens-lss
campaign shell scripts / paper plotting              -> legacy-only
```

## Scientific pins

### 1. Weak-lensing PDF is a flux-conserving probability density

For the analytic backend,

```text
s^2(z) = a z^b
m(z)   = -s^2(z)/2
p_WL(mu|z) = (1/mu) N(ln mu | m(z), s^2(z))
```

so `<mu>=1`.  The implementation clips the variance redshift coordinate at
`z>=1e-3` and carries a gradient-safe `sqrt` at the `a=0` unlensed ablation.

The tabulated backend interpolates **log p(mu|z)** bilinearly in `(z, ln mu)`.
Queries outside the supplied grid use constant edge extrapolation by clipping
the query coordinate before bracketing.  Grids must be finite and strictly
increasing; NaN table cells fail closed while `-inf` is a valid log-zero.

### 2. The magnification-distance map is fixed

The apparent GW distance is

```text
dL_app = dL(z) / sqrt(mu).
```

Weak-lensing event weights marginalize over `mu` rather than replacing the
luminosity-distance posterior by an ad-hoc broadened Gaussian.

### 3. Weak-lensing quadrature semantics are part of the model

The legacy implementation has two distinct production quadratures:

```text
lognormal backend:
  standardized Gaussian u = (ln mu - m)/s
  Gauss-Hermite integration

tabulated backend:
  16-node Gauss-Legendre integration in ln mu on [-0.6, 0.6]
```

The tabulated path has an explicit startup coverage check for
`int p_WL(mu|z) dmu ~= 1`; under-resolved narrow low-z PDFs must fail rather
than silently deleting events.  The lognormal Hermite path has its own
convergence/validity guard for amplified variance schedules.

### 4. SIS image geometry is one-dimensional in y

For `y in (0,1)`,

```text
p(y) = 2 y
mu_+ = (1+y)/y
mu_- = (1-y)/y
mu_+ - mu_- = 2
Delta t = T0 y.
```

The pair integral is therefore over `y`; treating `(mu_+,mu_-)` as independent
magnifications changes the model.

The frozen scalar SIS delay calibration is

```text
DEFAULT_T0_SECONDS ~= 5.36e6 s
```

and a time-mark candidate with `|Delta t| >= T0` lies outside the SIS support.
The scalar approximation is a known physical simplification; Phase 11 preserves
it before any later model improvement.

### 5. Optical depth and optical-depth probability are distinct

The surrogate optical depth is

```text
tau_2(z) = A_tau z^n_tau.
```

Likelihood channels consume

```text
P_2(z) = clip(tau_2(z), 0, 1 - 1e-12),
```

not the raw power law.  The same clipped probability must be used by pair,
singleton and selection channels so one parameter point never carries
incompatible lensing probabilities.

### 6. Image detection must match the injection/rendering convention

The Finn-Chernoff model uses

```text
rho = 8 Theta (r0/dL_app) (Mc_det/mc_bar)^(5/6)
```

with the analytic polynomial survival of `Theta in (0,4)`.

The mature code supports two pair-orientation semantics:

```text
independent
shared_iota
```

`independent` is correct for the historical mocks that redraw orientation per
image.  `shared_iota` conditions the two image responses on one shared binary
inclination while allowing decorrelated antenna response at separated arrival
times.  The inference mode must match the campaign; silently mixing the two
changes the J=2 / exactly-one-detected normalization at order unity.

### 7. Both-detected and exactly-one-detected channels are separate

For independent image orientations, pair detection factors as the product of
per-image probabilities.  For a genuinely shared orientation it does not.
The exactly-one-detected singleton channel carries an explicit partner-missed
factor.  The mature analytic expressions and their Monte-Carlo validation are
part of the reference contract.

### 8. Pair PE density lives in apparent-frame coordinates

The legacy pair KDE uses the canonical coordinate order

```text
(m1det, q, dL_app, chieff).
```

Boundary/prior handling and PE-prior division are part of the likelihood, not a
plotting convenience.  A reconstructed KDE must be tested as a density and as a
pair-likelihood ingredient; a naive unconstrained SciPy KDE is not an accepted
replacement.

### 9. Cluster likelihood and selection terms are counted exactly once

The pair channel combines one source with two observed images, SIS marks and the
appropriate pair selection.  Lensing optical-depth/mark factors must not be
repeated once per image or again in a global singleton term.  Legacy
`test_lensing_terms_once.py` is an explicit guard for this accounting.

### 10. Lensed selection is evaluated at the proposed cosmology

The lensed-injection files store the rendered source/image draws and detection
subsets, but detection depends on observables such as

```text
dL_app = dL(z; cosmology) / sqrt(mu).
```

Selection therefore cannot be replaced by fixed generation-time detection
flags when cosmology changes.  The mature cluster-selection path reevaluates
the detection factors under the sampled model.

### 11. Lensed-injection and observed-catalog provenance fail closed

The unified lensing analysis carries explicit schemas for the ordinary GW
selection store, lensed J=2 injections, observed event indexing, candidate pair
metadata and partitions.  Cross-file indexing, orientation mode and rendering
constants are inference provenance, not advisory metadata.

### 12. Partition marginalization is over mutually compatible partitions

Candidate edges cannot be multiplied independently when they share events.
The mature path enumerates / consumes partitions made of disjoint singleton and
pair assignments and marginalizes the complete likelihood over those
partitions.  The partition prior/weight belongs outside the per-edge pair KDE.

## Legacy test families to use as oracles

The pinned legacy test tree contains, at minimum:

```text
tests/test_lensing.py
  WL PDF/moments, SIS geometry/marks, basic cluster I/O, quadrature grids

tests/test_wl_weight.py
  weak-lensing event-weight marginalization and numerical guards

tests/test_cluster_likelihood.py
  pair KDE + J=2 cluster likelihood arithmetic

tests/test_cluster_selection.py
  lensed selection and detection-weight composition

tests/test_lensing_terms_once.py
  no double counting of optical-depth / lensing terms

tests/test_cluster_pe_variance_guard.py
  pair PE Monte-Carlo variance / fail-closed behavior

tests/test_lensed_singleton_channel.py
  exactly-one-detected censoring against direct Monte Carlo

tests/test_lensing_review_guards.py
  mature post-review scientific guard rails

tests/test_lensing_file_contract.py
  unified lensing file schema and provenance

tests/test_inference_lensing_fixed_parameters.py
  lens-only parameters stay outside ordinary core parameter space

tests/test_cli_wl_surface.py
  tabulated/lognormal weak-lensing surface

tests/test_cold_import_precision.py
  no eager precision-changing/device-array cache on import
```

The full test inventory will be frozen by the individual L0 probes rather than
ported wholesale as one monolithic suite.

## Planned Phase-11 slices

Reference first, then production:

```text
L0A  weak-lensing reference: PDF + quadratures + event-weight marginalization
L0B  SIS / Finn-Chernoff reference: marks + tau probability + image detection
L0C  pair/cluster reference: apparent-frame KDE + pair likelihood + selection
L0D  data/partition reference: lensed injections + schemas + exact partitions

L1   package scaffold + WL PDF/quadrature primitives
L2   weak-lensing spectral target through frozen-core InferenceTarget
L3   SIS marks + Finn-Chernoff detection primitives
L4   pair KDE + J=2 cluster likelihood
L5   lensed pair/singleton selection and exactly-one channel
L6   lensing data contracts + candidate graph / partition machinery
L7   full partition-marginalized lensing InferenceTarget
L8   clean install + fixed-theta full core/lensing parity + final freeze
```

The slice boundaries may be narrowed further if an L0 oracle reveals a tighter
scientific ownership boundary.  They may not be broadened by copying the legacy
factory or CLI wholesale.

## Immediate action

Build **L0A** as a separate-process probe against the pinned legacy SHA.  It must
freeze, with deterministic numerical fixtures:

```text
lognormal p_WL values and moments
flux conservation <mu>=1
a=0 unlensed / gradient-safe behavior
tabulated bilinear interpolation + edge clamping
tabulated grid validation and -inf/NaN semantics
Gauss-Legendre ln(mu) grid
Gauss-Hermite standardized-u grid
production tabulated quadrature constants and coverage check
weak-lensing event-sample marginal weight
unlensed limit of the event weight
finite gradients in the supported regime
```

No production file is created in `darksirens-lensing` until the L0A reference
artifact is green and committed in the control repository.
