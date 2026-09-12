# Phase 10 — darksirens-lss inventory / reference freeze

Status: **L0 INVENTORY ACTIVE — NO PRODUCTION PORT YET**

## Frozen references

```text
legacy oracle:       ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core dependency:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
core tree:           0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
surveys dependency:  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2
surveys tree:        4c4043ee2bee2a5a8940242e2de37f5eb5dbab17
LSS repository:      ignaciomagana/darksirens-lss (empty at phase start)
```

Dependency direction is one-way:

```text
darksirens-lss -> darksirens-core
darksirens-lss -> darksirens-surveys   only for explicit offline product inputs if needed
```

Core must never import `darksirens-lss`. Surveys must never learn LSS latent
state or Q semantics.

## Core extension seam

The frozen core already exposes the Phase-8C `RedshiftModel` protocol:

```python
parameter_spec() -> ParameterPlan
log_density(z, pixel, cosmology, parameters, state)
log_auxiliary_likelihood(parameters, state)
```

and the generic `host_density_log_likelihood` / `make_host_density_target`
wrappers. The LSS companion must use this seam rather than reconstructing a
second hierarchical GW reducer.

Core continues to own:

```text
population weighting
source/detector-frame Jacobians
PE reduction
GW selection integration
likelihood-variance / ESS guards
sampler execution
```

LSS owns only host-density construction/modulation and any count-field
auxiliary likelihood.

## Legacy ownership audit

### Direct LSS owners

```text
darksirens/redshift/lognormal_completion.py
  offline radial Poisson-lognormal builder
  low-rank sphere x z GP3D builder
  Laplace members
  per-z Q budget renormalization
  LSS completion HDF5 schema/provenance

darksirens/cli/build_lognormal_completion.py
  single-survey offline Q builder

darksirens/cli/build_joint_lognormal_completion.py
  matched multi-survey/shared-realization builder

darksirens/cli/diagnose_lognormal_completion.py
  offline Q diagnostics

darksirens/likelihood/latent_q.py
  latent-field Q seam, footprint mapping, b interpolation, rho budget gauge,
  static factored field state and rung shifts

darksirens/inference/q_provenance.py
  build-time conditioning/provenance checks
```

### Legacy runtime code to reconstruct through the core protocol, not copy verbatim

```text
darksirens/redshift/completion.py
  Q-modulated missing-host density and field/global normalization pieces

darksirens/redshift/prior.py
  fixed-table member evaluation and assembled redshift-prior state

darksirens/catalogs/lss.py
  legacy CLI/runtime loader glue

darksirens/inference/loaders.py
  multitracer realization-set matching and table attachment
```

These files mix reusable LSS physics with old monolithic catalog/CLI state. The
migration target is the behavior, not their legacy object graph.

### Explicitly NOT LSS

```text
survey-native catalog interpretation / masks / selection fitting -> darksirens-surveys
ordinary catalog likelihood / homogeneous completeness           -> darksirens-core
GW PE / injection stores and samplers                             -> darksirens-core
weak / strong lensing                                             -> darksirens-lensing
paper/campaign shell scripts                                      -> legacy-only
```

## Scientific pins that must be frozen before porting

### 1. Q is a placement field, not a missing-budget amplitude

The consumed missing density is schematically

```text
dN_miss(p,z) = base_miss(p,z) * Q(p,z)
```

but shipped Q tables are per-z renormalized under the actual missing-budget
weights so that

```text
sum_p w_p(z) Q_p(z) = sum_p w_p(z)
w_p(z) = (1 - C_p(z)) dN_exp(p,z)
```

on the fitted footprint, for the MAP table and for every ensemble member
independently. Thus C/n0 own **how much** missing budget exists; Q owns **where**
it is placed. This gauge convention is a scientific contract, not an optional
normalization cleanup.

### 2. Off-footprint / unsupported Q is exactly unity

At the log level:

```text
logQ = 0
```

outside the fitted footprint and outside the table/latent support. Do not leak a
footprint monopole, rho correction, or interpolation residue onto those rows.

### 3. Table indexing is explicit

Legacy artifacts support:

```text
indexing = compact   # row indexed
indexing = global    # global HEALPix indexed, gathered through row pixel ids
```

No silent shape-based guessing in the production companion.

### 4. Completion-base mode is provenance

A Q fit may be residual to:

```text
per_pixel
aggregate
selection
```

These are not interchangeable. Missing or legacy `c_mode` means historical
`per_pixel`; consumers must fail closed on incompatible requested semantics.

### 5. Footprint-awareness is provenance

`f_p_aware` records whether the survey footprint factor was divided out of Q at
build time. Applying `f_p` again to a table that already absorbed the mask is a
double-completeness error. The migration must preserve this guard explicitly.

### 6. Q support depth is explicit

`q_support_depth` defines the redshift support of the fitted field. Above support,
Q returns exactly one. This is distinct from the catalog's overall redshift grid
or ordinary completeness depth.

### 7. Ensemble members carry realization identity

When Q members are present, artifacts carry:

```text
realization_set_id
member_content_sha256
n_members
```

Multi-survey member marginalization may pair member index m across surveys only
when the realization-set provenance says those ensembles are matched.
Independent single-survey builder runs must not be silently paired.

### 8. Convergence and non-finite outputs fail loudly

Non-finite logQ cells are fatal at save/load. Convergence diagnostics are
provenance with a historically nuanced legacy warning path; migration must not
turn failed fits into apparently valid tables.

### 9. Latent mode uses the same budget gauge

The latent seam does not simply exponentiate a Gaussian field. It subtracts the
closed-form per-z `rho` so the consumed missing-budget identity is exact for each
member and sampled bias/completeness configuration. Off-footprint and
out-of-support logQ remain bit-zero.

### 10. Field/global sky normalization is separate from conditional redshift shape

The mature LSS path contains a field/global count normalization in addition to
per-pixel conditional redshift density. The new companion must express this
through `log_auxiliary_likelihood` / explicit extension state without changing
the frozen GW reducer.

## Legacy test families to use as oracles

```text
tests/test_lss_completion.py
  deterministic Q, compact/global indexing, member shapes, normalization,
  offline spectrum/MAP/Laplace behavior, HDF5 roundtrip

tests/test_q_budget_renormalization.py
  exact per-z mean-one gauge; builder budget identity; HDF5 budget stamps

tests/test_lss_provenance.py
  realization-set / member hash semantics

tests/test_completion_convergence_gate.py
  nonfinite/convergence safety

tests/test_completion_aggregate_mode.py
  aggregate-vs-per-pixel semantics

tests/test_completion_q_support_depth.py
  explicit Q support truncation

tests/test_lss_completion_gp3d.py
  low-rank sphere x z GP behavior

tests/test_joint_lognormal_completion.py
  matched multi-survey realization production

latent/field tests and frozen feature-matrix cells
  latent Q seam, field normalization, theta shifts, multitracer composition
```

## Planned Phase-10 slices

Keep the migration incremental:

```text
L0A  deterministic legacy reference: Q gauge + artifact schema + radial primitives
L0B  deterministic legacy reference: fixed-table Q redshift/likelihood behavior
L0C  deterministic legacy reference: latent/field and matched multitracer cells

L1   package scaffold + Q artifact dataclass/loader/writer + budget operator
L2   fixed deterministic Q table RedshiftModel through frozen core seam
L3   Q-member ensemble marginalization and matched-realization provenance
L4   radial Poisson-lognormal offline builder
L5   GP3D / joint multi-survey offline builders
L6   latent-field/count-likelihood mode using log_auxiliary_likelihood
L7   matched multitracer latent composition / field-global normalization
L8   clean-install, fixed-theta full core+LSS parity, final LSS freeze
```

Do not start with GP3D or latent state. The first production port must be the
small Q artifact/gauge contract and deterministic fixed-table mode.

## Immediate action

Build L0A as a separate-process pinned-legacy probe. It must freeze:

```text
gaussian_correlation_spectrum
renormalize_q_mean_one for map + member cube
zero-budget-bin behavior
radial MAP matched-count behavior
Laplace member deterministic seed behavior
HDF5 map/member roundtrip
compact/global indexing metadata
budget_renormalized + removed monopole
c_mode
f_p_aware
q_support_depth
realization_set_id / member hash / n_members
fail-closed nonfinite writer behavior
```

No production file is created in `darksirens-lss` until that reference is green
and committed.
