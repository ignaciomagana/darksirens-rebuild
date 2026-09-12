# Phase 10 L4 — radial Poisson–lognormal builder

Status: **ACCEPTED / FROZEN**

## Accepted LSS package

`ignaciomagana/darksirens-lss`

```text
main SHA:  bff31c84ba593047babbd0fac6d46aeab57555d3
tree SHA:  1ac8cdae9a8cdb259bd3c657fda5a78fbee17e50
```

No frozen-core or surveys source was modified.

## Final CI acceptance

GitHub Actions run:

```text
run:       34687210262
```

Standalone artifact layer:

```text
job:       103536173762
result:    SUCCESS
pytest:    11 passed in 0.22 s
```

Radial builder:

```text
job:       103536173721
result:    SUCCESS
pytest:    15 passed in 1.39 s
```

The builder gate pins:

```text
Python: 3.11
NumPy:  1.26.4
SciPy:  1.12.0
h5py:   3.12.1
```

## Dependency boundary

Runtime package dependencies remain NumPy + HDF5 only.

SciPy is an optional offline-builder dependency:

```text
builder = ["scipy>=1.12,<2"]
```

`import darksirens_lss` imports neither SciPy, JAX, frozen core, nor surveys. The permanent standalone firewall asserts this directly. Radial optimization imports SciPy only when a builder function is executed.

## Public L4 API

L4 adds:

- `LOGQ_CLIP`
- `RadialBuildResult`
- `gaussian_correlation_spectrum`
- `poisson_lognormal_map`
- `laplace_lognormal_members`
- `build_radial_q_artifact`

The public `build_radial_q_artifact` is routed through `radial_builder.py`, which converts/validates the physical support-depth contract before calling the low-level numerical kernel in `radial.py`.

## Numerical model

For each row/pixel on a common solve grid,

```text
s ~ N(0, C[P])
N_v ~ Poisson(C_v dN_exp,v exp[b s_v - b^2 sigma_s^2/(2 prior_strength)])
```

with a circulant 1-D Gaussian covariance represented by its FFT spectrum.

The Gaussian spectrum is

```text
C(d) = sigma^2 exp[-0.5 (d/ell_grid)^2]
P = Re FFT[C]
```

with the mature positive floor applied relative to `max(P)`.

The prior precision is multiplied by `prior_strength`. Therefore the mean-one lognormal shift is

```text
0.5 * b^2 * sigma_s^2 / prior_strength.
```

This prior-strength scaling is frozen by data-free tests at `prior_strength = 0.25, 1, 4`.

## MAP objective and convergence

The per-row objective is the Poisson negative log likelihood plus the FFT-diagonal Gaussian prior. The gradient is analytic and the optimizer is SciPy L-BFGS-B.

The requested iteration budget cannot be silently pre-empted by SciPy's function-evaluation default:

```text
maxfun = 21 * maxiter.
```

Solver convergence is a production gate. By default, any unconverged row causes the artifact builder to fail. `allow_unconverged=True` exists only as an explicit research-ablation override; such an artifact is stamped unconverged and is not certified budget-renormalized.

## Deterministic Q semantics

The deterministic table is **not** the raw MAP transform `Q(s_MAP)`.

L4 reproduces the mature Laplace/Jensen correction using the local per-bin diagonal posterior variance:

```text
log Q_map = clip(
    b s_MAP
    - 0.5 b^2 sigma_s^2 / prior_strength
    + 0.5 b^2 Var_post(s_v),
    -7,
    +7,
)
```

where the local curvature contains the per-bin Poisson rate, not only a row-global approximation.

## Laplace members

The member generator reproduces the frozen FFT-diagonal approximation:

1. use the row median fitted rate to define a stationary approximate Hessian spectrum;
2. draw a correlated Gaussian perturbation in Fourier space;
3. rescale each bin to the local Laplace diagonal variance;
4. transform with the same mean-one shift and `±7` log-Q rail;
5. retain deterministic output for a fixed seed.

Members remain raw completion realizations until the missing-budget gauge is applied.

## Missing-budget gauge

The builder uses the frozen L1 mean-one convention. Unless an explicit weight table is supplied,

```text
w_p(z) = (1 - C_p(z)) dN_exp,p(z).
```

The map and **each member independently** are gauge-fixed so that, at every fitted z node with nonzero missing weight,

```text
sum_p w_p Q_p / sum_p w_p = 1.
```

The removed map monopole is persisted through `budget_monopole_logq`. Member monopoles are returned in the build result for diagnostics/provenance.

Thus Q redistributes the ordinary missing-galaxy budget; it does not silently change that budget's monopole.

## Active support-depth contract

`q_support_depth` is not a metadata-only stamp.

The public builder uses the supplied z grid to set

```text
n_fit = count(z <= q_support_depth)
```

and only those nodes see data. Output nodes above support are exactly

```text
logQ = 0  (Q = 1)
```

for the deterministic table and every member.

If `q_support_nodes` and `q_support_depth` are both supplied, they must describe the same restriction or the builder fails before optimization. If only a truncating node count is supplied, the artifact is automatically stamped with `zgrid[n_fit-1]` so downstream runtime behavior is self-describing.

A support depth below the first grid node and a non-monotonic z grid fail closed.

## Circulant wrap protection

When support truncates the solve domain, the numerical solve receives a pure-prior wrap pad

```text
n_pad = max(32, ceil(4 ell_grid)).
```

The padded nodes have exactly zero data pull (`C=0`, `dN_exp=0`). A dedicated test verifies that changing arbitrary `N_obs` values in those masked pad cells cannot alter the fitted region.

The pad is numerical only and is discarded before artifact construction.

## Frozen L0A parity anchors

The L4 gate reproduces the already-frozen L0A radial oracle, including:

- Gaussian correlation spectrum first nodes and moments;
- MAP `s` first nodes;
- fitted Poisson `lambda` first nodes;
- deterministic Q extrema / high-density deviation;
- seeded Laplace member first nodes.

Representative frozen values:

```text
s_MAP[:8] =
[0.00021835525439618063,
 0.00024731182291349386,
 0.00030129252880937437,
 0.0003760665437801624,
 0.00047143224186378197,
 0.000592976474030909,
 0.0007503228241733021,
 0.0009538232931587965]

lambda_MAP[:8] =
[1.738452187766063,
 2.0531035998670197,
 2.4814987438371747,
 3.0576169245864815,
 3.82287914616312,
 4.826841169949377,
 6.127615935533018,
 7.791889274523248]

Q_min = 0.985720938054289
Q_max = 1.0046245661568396
```

The original L0A raw spectrum SHA remains frozen in the control repository. Package CI compares computed FFT outputs numerically rather than by bytes because independent hosted-runner FFT/libm dispatch differs in the final bits.

One intermediate L4 run (`34687162752`) demonstrated exactly this portability class: 14/15 tests passed and the only failure was a spectrum difference of `2.22e-16` absolute (`1.07e-14` relative). No solver, support, member, gauge, or artifact test failed. The final acceptance policy therefore mirrors L0A/L2: exact structural/provenance checks and tight numerical comparison for computed floating outputs.

## Artifact contract

The builder emits the accepted L1 `QArtifact` and is therefore directly consumable by L2/L3 after the relevant runtime provenance constraints are satisfied.

It records:

- `model = poisson_lognormal`
- map and optional member tables
- exact supplied z grid
- indexing convention
- `c_mode`
- `f_p_aware`
- `q_support_depth`
- `realization_set_id`
- `n_members`
- convergence/build diagnostics
- budget-renormalization certification and removed map monopole

HDF5 write/read round-trip of map, members, member count, realization identity, completion metadata, support depth, and budget certification is frozen by the L4 tests.

## Ownership boundary

L4 owns the **LSS numerical solver on already-prepared common-grid count/base arrays**.

It deliberately does not own:

- survey-native file ingestion;
- photometric/spectroscopic quality cuts;
- catalog mask/depth construction;
- cosmological distance/grid construction;
- host-density runtime likelihood math.

Those remain in their accepted survey/core layers or in a thin upstream data-preparation adapter. This prevents the radial solver from reabsorbing responsibilities already separated during reconstruction.

## Next slice

Proceed to **L5: GP3D and joint matched multi-survey builders**.

L5 is still an offline fixed-table builder. It must reconstruct the low-rank angular×radial field, GP3D MAP/Laplace member machinery, and matched realization construction across multiple survey responses while emitting the same L1 artifact contract and shared `realization_set_id`/member-axis semantics required by L3.

Do **not** cross into latent-field/count-likelihood inference here; that remains L6.
