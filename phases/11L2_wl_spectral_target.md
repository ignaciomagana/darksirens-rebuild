# Phase 11 L2 — weak-lensing spectral target freeze

Status: **ACCEPTED / FROZEN**

## Accepted production state

```text
repository:  ignaciomagana/darksirens-lensing
main SHA:    83980f3932371287652b584774ae527b8c8319b5
tree:        a3a7205deae763b2cc62ad42890b59568d9ef532
promotion:   PR #1
```

Frozen dependencies remain unchanged:

```text
core SHA:          af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
core tree:         0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
exact core wheel:  darksirens-0.1.0.dev0-py3-none-any.whl
core wheel SHA256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
legacy oracle:     c042527238bd71421b792936bc48c3b815b90d6d
```

## Production surface

L2 adds:

```text
src/darksirens_lensing/weights.py
  log_sample_weight_wl_lognormal_hermite
  log_sample_weight_wl_or_standard

src/darksirens_lensing/spectral.py
  WeakLensingSpectralDiagnostics
  weak_lensing_spectral_log_likelihood
  make_weak_lensing_spectral_target
```

The companion owns only the magnification integral. Frozen core still owns:

```text
cosmology and dL(z) / z(dL)
population density
canonical (m1det,q,dL) Jacobian
PE event reduction
ordinary selection reduction and N_eff
Talbot-Golomb / total likelihood-variance guard
sampler ParameterPlan and InferenceTarget execution
```

`wl_a` and `wl_b` are fixed lensing run configuration. They are not appended to
the ordinary core sampler coordinate vector. The specialized target reuses the
base spectral analysis `ParameterPlan` exactly.

## Exact-core acceptance gate

Temporary branch workflow:

```text
run: 34735312529
job: 103665575267
head during gate: 87e29a1d4f797a81bee66286e743e23216db1f56
result: SUCCESS
pytest: 4 passed in 36.16 s
```

The job downloaded the previously frozen core-wheel artifact, verified the wheel
against the immutable SHA256

```text
4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

and installed both core and the L2 companion from wheels before running the
acceptance tests. The short-lived signed artifact URL and temporary workflow
were deleted before promotion to `main`.

The four accepted tests establish:

1. The exact seven-sample L0A legacy event-weight fixture is reproduced by the
   companion on frozen core, including the default `a=4e-3,b=1.5` Hermite
   weights.
2. At `a=0`, the Hermite weight is exactly the ordinary core sample weight and
   the gradient with respect to `a` remains finite, reproducing the frozen L0A
   gradient anchor.
3. The complete PE + selection hierarchical diagnostics reduce to core's
   ordinary spectral-siren likelihood at `a=0` for both
   `wl_selection='standard'` and `wl_selection='lognormal'`.
4. `make_weak_lensing_spectral_target` returns an `InferenceTarget` carrying the
   exact base `ParameterPlan`; lens-only configuration does not leak into the
   core parameter space.

## Ordinary clean-wheel regression gates

PR clean-wheel CI:

```text
run: 34735397145
job: 103665807481
result: SUCCESS
```

Accepted-main clean-wheel CI:

```text
run: 34735440255
job: 103665922698
result: SUCCESS
```

Both retain the L1 ownership firewall: importing `darksirens_lensing` from the
installed wheel does not import `darksirens`, `darksirens_lss`, or
`darksirens_surveys`; the frozen L0A-backed L1 tests continue to pass.

## Scientific contract frozen at L2

For the lognormal backend the proposal nodes are drawn from
`p_WL(mu|z_app)` but the target is `p_WL(mu|z_s(mu))`. The node integrand
therefore carries the explicit proposal-to-target log-density ratio. The
apparent-distance Jacobian contributes `+0.5 log(mu)` and the Hermite measure
already carries the WL PDF, so no extra `+log(mu)` substitution term is added.

The `a=0` ablation is a full hierarchical reduction, not merely a PDF-level
limit: PE weights, selection weights when requested, event evidences,
Monte-Carlo variances, selection normalization and final likelihood all reduce
to the frozen core spectral model.

## Next slice

Phase 11 proceeds to **L0B** first: freeze SIS marks/optical-depth probability
and Finn-Chernoff image-detection/orientation semantics against the pinned legacy
oracle. Production L3 must not begin until that reference is accepted.
