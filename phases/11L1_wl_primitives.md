# Phase 11 L1 — weak-lensing PDF and quadrature primitives

Status: **ACCEPTED / FROZEN**

## Accepted lensing package

```text
repository: ignaciomagana/darksirens-lensing
main SHA:   4b02b5e754a423ac71c3ce293e7e58bc26e22764
tree SHA:   c8c9c51a792643b7ca274581c3d439be4f4057f5
version:    0.1.0
```

No frozen core, surveys, LSS, or legacy source was modified.

## Frozen reference

L1 is reconstructed against the accepted L0A reference:

```text
references/lensing_l0a_wl_legacy_reference.json
schema: darksirens-lensing-l0a-wl-reference-1
legacy SHA: c042527238bd71421b792936bc48c3b815b90d6d
committed-golden replay: 34734348866 / 103662929617 SUCCESS
```

## Clean-wheel acceptance

```text
workflow run: 34734529520
job:          103663424030
head:         4b02b5e754a423ac71c3ce293e7e58bc26e22764
result:       SUCCESS
pytest:       9 passed in 3.02 s
```

The job built `darksirens_lensing-0.1.0-py3-none-any.whl`, installed it
non-editably, and ran the tests from `/tmp`.  The import path therefore resolved
through `site-packages`, not the source checkout.

The ownership firewall also passed: importing `darksirens_lensing` did not
import `darksirens`, `darksirens_lss`, or `darksirens_surveys`.

## Public L1 surface

L1 exports:

```text
WLParams
WL_MU_QUADRATURE_NODES
WL_MU_QUADRATURE_LOG_MU_RANGE
make_log_mu_grid
make_wl_mu_quadrature
make_y_grid
make_hermite_u_grid
make_lognormal_wl_params
make_tabulated_wl_params
log_p_wl
make_lognormal_log_p_wl
make_tabulated_log_p_wl
make_log_p_wl_from_params
wl_mu_quadrature_coverage
validate_wl_mu_quadrature
```

## Scientific contract

The analytic backend preserves

```text
s^2(z) = a z^b
m(z) = -s^2(z)/2
p_WL(mu|z) = N(ln mu | m,s^2) / mu
```

with the frozen `z >= 1e-3` variance coordinate and the gradient-safe square
root used at zero variance.

The accepted tests reproduce all five frozen L0A log-density values and verify
normalization and `<mu>=1` by direct 200-node quadrature to `3e-13` absolute
tolerance.

The tabulated backend preserves:

```text
bilinear interpolation in (z, ln mu)
query-coordinate clipping before bracketing
constant edge extrapolation
strictly increasing finite grids
NaN rejection
-inf log-zero acceptance
broadcasting before flatten/vmap
```

The production tabulated quadrature remains exactly

```text
N_mu = 16
ln(mu) in [-0.6, 0.6]
```

and the 16-node Hermite and 32-node SIS-y rules reproduce the frozen L0A
normalizations.  The startup coverage validator accepts a deliberately exact
normalized table and rejects an under-normalized table rather than silently
renormalizing it.

## Boundary

L1 owns only PDF/interpolation/quadrature primitives.  It does **not** yet own:

```text
PE-sample weak-lensing marginalization
population / redshift-prior evaluation
selection beta
sampler parameter assembly
InferenceTarget construction
strong-lensing marks or clusters
```

Those remain outside this slice.

## Next slice

Proceed to **L2: weak-lensing PE-sample marginalization composed with the exact
frozen core and exposed as an `InferenceTarget`**.

L2 must reproduce the L0A event-weight golden, including the proposal-to-target
`p_WL(mu|z_s(mu))/p_WL(mu|z_app)` factor and the exact `a=0` value/gradient
limit, without copying the legacy monolithic likelihood factory.
