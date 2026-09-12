# Phase 10 L6 — online latent field and galaxy-count likelihood

Status: **ACCEPTED / FROZEN**

## Accepted LSS package

`ignaciomagana/darksirens-lss`

```text
main SHA: a4096e2b0c2c78b26f04ca45b61850efb2db6797
tree SHA: 8b012579e57254f0270c81ae91f85bc46764e732
```

No frozen-core or surveys source was modified.

## Frozen dependencies

```text
legacy oracle:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

frozen core:
  ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
  tree: 0608b75ff5c142bfba0fc15a4fad79e0fee1fa74

exact core wheel:
  darksirens-0.1.0.dev0-py3-none-any.whl
  SHA256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

## Frozen legacy oracle

Committed golden:

```text
references/lss_l6_latent_count_reference.json
schema: darksirens-lss-l6-latent-count-reference-1
```

Committed-golden replay:

```text
run/job: 34688379063 / 103539264509
result:  SUCCESS
```

Bootstrap/reference artifact:

```text
run/job:   34688216159 / 103538840812
artifact:  10296346167
name:      lss-l6-latent-count-legacy-reference
digest:    sha256:95b22bee9eca0404b043dd0f443844aa3f78f5aaa9fd9601971322838c903d9b
result:    SUCCESS
```

The L6 oracle freezes the online physics seam rather than the legacy monolithic
object graph:

- shell-total-conditioned multinomial galaxy-count likelihood;
- analytic gradient and exact Hessian, including the multinomial rank-1 subtraction;
- fixed-trip damped count MAP solve and Laplace evidence;
- shared-field multitracer arithmetic (data/Fisher terms add, Gaussian ridge once);
- closed-form latent `rho` budget normalizer;
- generated latent `logQ` with exact off-footprint and out-of-support zeros.

The oracle uses the mature 33-node Chebyshev interpolation grid for the bias
moments and constructs the moments from the same stored row-factor precision
consumed by the latent seam.  This avoids conflating interpolation error with a
row-factor precision mismatch.

## Exact frozen-core integration gate

The final public L6 source/API head before removal of the temporary signed-wheel
workflow was

```text
SHA: 66a3873e50a5cf69ffaf5e14c6f467fc834a3256
```

It was tested against the exact frozen core wheel above:

```text
run/job: 34713824946 / 103607258215
result:  SUCCESS
```

The exact-wheel job verified the wheel SHA256 before installation and ran the
pure L6 oracle suites plus the frozen-core host-density integration suite.  The
accepted main SHA differs only by deletion of that temporary workflow; no source
or test file changed after this exact-core gate.

An earlier corrected-source gate also passed:

```text
run: 34713736441
result: SUCCESS
pytest: 14 passed
```

The first temporary integration run had 13/14 tests pass; its sole failure was a
test fixture with an invalid one-node bias interpolation grid.  The fixture was
corrected to a valid two-node plan; no production numerical/model code was
changed to make that test pass.

## Final permanent package CI

GitHub Actions:

```text
run: 34713893587
head: a4096e2b0c2c78b26f04ca45b61850efb2db6797
```

Permanent jobs:

```text
standalone artifact/API firewall:
  job:    103607438006
  result: SUCCESS

radial + GP3D builder regression:
  job:    103607438027
  result: SUCCESS

latent count + Q oracle parity:
  job:    103607438062
  result: SUCCESS
```

The standalone gate confirms that exposing the L6 public API does **not** make
`import darksirens_lss` import JAX, SciPy, frozen core, or surveys.  Runtime
package dependencies remain NumPy + HDF5 only.

## Public L6 API

The accepted root API adds:

- `LatentQPlan`
- `LatentCountEvidence`
- `LatentFieldState`
- `LatentFieldEnsembleState`
- `LatentLikelihoodResult`
- `LatentQModel`
- `build_latent_count_evidence`
- `build_latent_field_ensemble_state`
- `build_latent_field_prior_state`
- `latent_field_ensemble_log_likelihood`
- `validate_latent_pair`

The lower-level latent count/Q kernels remain in `latent_counts.py` and
`latent_q.py`; JAX and core imports are lazy.

## Count channel

The galaxy field is inferred from the shell-total-conditioned angular count
likelihood

```text
pi_pg = f_p exp(eta_pg) / sum_p' f_p' exp(eta_p'g)
eta_pg = b_gal Phi_pg xi
log L_count = sum_pg N_pg log pi_pg .
```

The Gaussian prior on the whitened field gives

```text
J(xi) = 0.5 ||xi||^2 - log L_count.
```

The Hessian retains the multinomial covariance term

```text
H = I + b_gal^2 sum_g [Phi_g^T diag(T_g pi_g) Phi_g
                        - T_g u_g u_g^T],
u_g = Phi_g^T pi_g.
```

Dropping the rank-1 subtraction would overstate the information and
under-disperse the latent posterior, so the term is a frozen scientific pin.

The MAP uses the mature fixed 13-trip damped Fisher/Newton solve.  Non-finite or
non-converged solves fail closed.  The galaxy-side auxiliary likelihood is the
Laplace evidence

```text
log L_gal = log L_count(xi_hat)
            - 0.5 ||xi_hat||^2
            - 0.5 log det H.
```

The Occam determinant is not optional.

## Latent Q and missing-budget gauge

L6 does not load a resident Q table.  For member `m`, fitted footprint row `p`
and supported redshift node `z`,

```text
log Q_m(p,z) = b_GW [row_fac_m(p) . phi_z(z)] - rho_m(z).
```

Outside the fitted footprint or outside the latent support,

```text
log Q = 0
Q = 1
```

exactly.

The closed-form normalizer is

```text
rho_m(z) = log[(A_m(z;b_GW) - C(z) B_m(z;b_GW))
               /(P_F - C(z) F_F)].
```

Positive `A`/`B` moments are interpolated in log space over the artifact's
Chebyshev nodes.  Bias values outside the node interval are not silently clamped.

The normalizer enforces, member by member,

```text
sum_{p in F} [1 - f_p C(z)] Q_m(p,z)
  = sum_{p in F} [1 - f_p C(z)].
```

Thus the latent field places the missing budget without changing its monopole.

## Aggregate/selection completeness boundary

Frozen core's ordinary completeness implementation is deliberately per-pixel.
L6 must therefore not approximate the latent aggregate/selection base with that
core estimator.

The LSS state receives explicitly:

```text
C(z)          one scalar aggregate/selection completeness curve
f_p           one full/global-pixel survey fraction map
fit_pixels    the latent fitted footprint
```

and constructs

```text
C_p(z) = f_p C(z)
base_miss_p(z) = [1 - f_p C(z)] dN_exp(z).
```

The state constructor verifies:

- `P_F` equals the fitted-footprint size;
- `sum_{p in F} f_p` matches the artifact `F_F`;
- every catalog row outside `fit_pixels` has `f_p == 0`;
- the scalar completeness curve is finite, bounded in `[0,1]`, and lies on the frozen core z grid.

These checks prevent Q footprint semantics from drifting away from the
completeness budget consumed by the likelihood.

## Frozen-core composition

`LatentQModel` implements the frozen core `RedshiftModel` protocol rather than
reconstructing the GW hierarchical reducer.

L6 reuses core for:

- observed-galaxy redshift kernels;
- source/population weighting;
- PE event reduction;
- detector-selection integration;
- likelihood-variance/ESS behavior;
- sampler-facing `ParameterPlan` semantics.

The only L6 sampled extension coordinate is

```text
b_miss
```

for legacy sampler-label compatibility.  **In latent mode its physical meaning
is `b_GW`**, the bias with which GW hosts trace the latent field.  It is not the
offline count-channel galaxy bias.  Its admissible interval is the artifact's
bias-interpolation node interval.

## Full member marginalization

PE and selection must consume the same latent field/budget ensemble.  L6 hashes
the field leaves plus footprint/completeness inputs and refuses mismatched
PE/selection states.

For each matched member `m`, L6 evaluates the **complete frozen-core** likelihood,
including both PE and selection, then performs

```text
log L = logsumexp_m(log L_m) - log M.
```

It does not average Q or redshift priors before the GW likelihood.

The count Laplace evidence is common to every member because the members are
draws from one conditional count posterior.  Supplying the same scalar auxiliary
term to each complete-member call and only then taking `logmeanexp` adds that
evidence exactly once to the marginalized result; the frozen-core integration
test pins this explicitly.

## Rung-1 response leaves

The reconstructed numerical seam retains `S`, `dA`, `dB`, `theta_shift`, and
`moments_at` for the mature linear-response route.  L6's core-facing constructor,
however, accepts only the rung-0 anchor and **fails closed** when active response
leaves/labels are present.

This is deliberate.  The artifact does not itself define sampler bounds/priors
for arbitrary response coordinates, so silently ignoring them or inventing a
`ParameterPlan` would change the inference contract.  The numerical response
machinery is preserved for the later explicit theta-coupled slice.

## L6/L7 boundary

L6 is intentionally:

```text
K = 1
conditional redshift shape per catalog row
matched latent member marginalization
count-channel auxiliary likelihood
```

L6 does **not** claim to finish:

```text
K >= 2 matched latent catalog composition
survey-global/field-global host normalization
catalog-mixture weights across tracers
shared-field multi-survey GW composition
```

Those are **L7**.  Keeping this boundary explicit prevents the field-global
normalizer from being folded into a per-row conditional prior, where it would
cancel or be counted in the wrong place.

## Next slice

Proceed to **L7: matched multitracer latent composition and field-global
normalization**.

L7 must freeze the legacy survey-global count normalizer and the K-catalog
mixture algebra before production code.  In particular it must establish where
the per-catalog global `Z_k` cancels at K=1, where it does not cancel for K>=2,
and how one shared latent member index is consumed across all tracers without
reintroducing table-era realization-ID semantics.
