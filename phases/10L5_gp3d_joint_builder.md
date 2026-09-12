# Phase 10 L5 — GP3D and joint matched-survey builders

Status: **ACCEPTED / FROZEN**

## Accepted LSS package

`ignaciomagana/darksirens-lss`

```text
main SHA: fe8e0da67b58caef4dcbacfe297c234fdb18bb64
tree SHA: c5a0d2805c8846b62fe20d74edf15031c6bd6785
```

No frozen-core or surveys source was modified.

## Frozen legacy oracle

Pinned legacy source:

```text
ignaciomagana/darksirens
SHA: c042527238bd71421b792936bc48c3b815b90d6d
```

Committed golden:

```text
references/lss_l5_gp3d_legacy_reference.json
schema: darksirens-lss-l5-gp3d-reference-1
```

Committed-golden replay:

```text
run/job: 34687597616 / 103537209191
result:  SUCCESS
```

Regenerated oracle artifact from the bootstrap run:

```text
run:       34687470589
artifact:  10295568968
name:      lss-l5-gp3d-legacy-reference
digest:    sha256:4a4770265a0757a29aa43eb07db5d96e22f9c895e6b8f0c8bd27e99b36842478
```

The committed-golden workflow verifies the pinned legacy SHA, runs the probe twice in independent processes, compares all non-hash floating content numerically/structurally, and compares the regenerated result to the committed golden.

## Final package CI acceptance

GitHub Actions:

```text
run: 34687862003
```

Standalone artifact/API firewall:

```text
job:    103537912999
result: SUCCESS
```

Radial + GP3D builder gate:

```text
job:    103537913099
result: SUCCESS
pytest: 24 passed
```

The builder environment is pinned to Python 3.11, NumPy 1.26.4, SciPy 1.12.0, and h5py 3.12.1.

Three GP3D sphere-resolution warnings in the fixture are expected mature behavior: radial inducing under-resolution is a hard error; coarse Fibonacci-sphere resolution is a warning in fixed-table L5.

## Dependency boundary

Runtime package dependencies remain NumPy + HDF5 only. SciPy remains an optional offline-builder dependency and is imported lazily by the optimization path.

`import darksirens_lss` imports neither SciPy, JAX, frozen core, nor surveys. The final standalone gate checks this after exposing the L5 public API.

L5 contains a local NumPy implementation of the already-frozen sphere × `zeta=log1p(z)` kernel/inducing geometry. It does not runtime-import private core GP symbols.

## Public L5 API

Numerical GP3D surface:

- `fibonacci_sphere`
- `sphere_z_kernel`
- `lowrank_inducing_nodes`
- `build_lowrank_operator`
- `gp3d_resolution_guard`
- `poisson_lognormal_gp3d_map`
- `laplace_lognormal_gp3d_members`
- `eval_logq_gp3d`

Prepared-voxel artifact builders:

- `GP3DSurveyInput`
- `GP3DBuildResult`
- `JointGP3DBuildResult`
- `build_gp3d_q_artifact`
- `build_joint_gp3d_q_artifacts`

Survey ingestion is intentionally not part of this layer.

## Low-rank field model

The field lives on unit-vector direction and

```text
zeta = log(1 + z).
```

The covariance is a product of a chordal sphere RBF and radial RBF. With inducing points `Z`,

```text
Phi(X) = k(X,Z) L^{-T},
L L^T = k(Z,Z) + jitter I,
xi ~ N(0,I),
f(X) = Phi(X) xi.
```

Inducing nodes are a deterministic Fibonacci sphere crossed with uniformly spaced `zeta` nodes, ordered as

```text
i = i_sphere * M_z + i_z.
```

The frozen single-field fixture uses `M_sph=32`, `M_z=6` (`M=192`).

## GP3D MAP and posterior mean

For solve voxels,

```text
N_v ~ Poisson[base_v exp(b f_v - b^2 sigma_v^2/2)].
```

The MAP is solved in whitened latent coordinates with an analytic Newton/Hessian path, clip-aware KKT residuals, line search, and an L-BFGS-B fallback. The final Laplace precision is

```text
H = I + Phi^T diag(b^2 lambda) Phi
```

on unpinned data curvature.

The deterministic table is the Laplace posterior mean, not merely the MAP transform:

```text
log Q_mean(X)
 = b f_MAP(X)
   - 0.5 b^2 [Var_prior f(X) - Var_post f(X)].
```

A homogeneous prior/posterior fixture evaluates to numerical zero (`Q=1`) as required.

## Angular borrowing oracle

The frozen single-survey fixture places a strong count excess on direction A, evaluates at A, a nearby direction B separated by 15 degrees, and the antipodal direction C. At the structure node the legacy oracle gives

```text
logQ(A) = 1.1713436392672394
logQ(B) = 1.1210361007715635
logQ(C) = 0.008893919911189381
```

thus freezing the angular-borrowing semantics directly.

## Laplace member semantics

Members are drawn in the shared whitened coordinates:

```text
xi_m = xi_MAP + L_H^{-T} g_m.
```

Evaluation of a member uses the prior mean-one shift, while deterministic map evaluation uses the posterior-variance correction above. Fixed seeds reproduce the frozen legacy member anchors numerically.

## Joint matched-survey solve

For K surveys with tracer responses/biases `b_k`, L5 follows the mature construction exactly:

```text
Phi'_k = b_k Phi_k
```

and stacks all survey voxels into one solve with solver `bias=1`. Therefore

```text
sigma_v^2 = sum_j (Phi'_{v j})^2
```

already contains the required `b_k^2` scaling in each survey's mean-one shift.

The result is one shared `xi_MAP`, one shared Hessian, and one shared Laplace member axis across all K survey products.

The frozen two-survey oracle uses biases `[0.8, 1.35]`, a 32-dimensional shared latent field, and yields same-member correlation 1.0 at the tested voxel before gauge removal.

## Per-survey missing-budget gauge

Sharing the latent field does **not** mean sharing the Q monopole.

Each output survey is independently gauge-fixed under its own supplied missing-budget weights:

```text
sum_p w_{k,p}(z) Q_{k,p}(z) / sum_p w_{k,p}(z) = 1,
```

with `w_k=(1-C_k)dN_exp,k` prepared upstream.

Map and every member are gauge-fixed independently for each survey. This preserves the Phase-10 rule that Q only places each catalog's missing budget; it cannot transfer or rescale budget between surveys.

All matched survey artifacts carry the same `realization_set_id`. Joint diagnostics also carry a SHA-256 of the shared latent member matrix so member-axis identity is auditable across files.

## Support-depth discipline

`q_support_depth` is active, not decorative. A prepared survey whose solve voxels extend above its declared support fails before optimization.

After evaluation and after gauge removal, all output nodes above support are repinned to exactly

```text
logQ = 0.
```

The persisted map monopole and returned member monopoles are also zeroed above support so provenance describes the emitted table.

## Empty-field behavior

If a single prepared survey has no solve voxels, its builder emits exact unity Q. If **all** surveys in a joint build are empty, every matched artifact is exact unity while retaining the shared realization-set identity.

In a non-empty joint solve, a survey with no own voxels can still receive the shared field at its output directions: borrowing from the other surveys is part of the joint model.

## Ownership boundary

L5 owns:

- low-rank angular × radial GP geometry;
- fixed-table GP3D MAP/Laplace evaluation;
- matched multi-survey shared-latent construction;
- per-survey Q budget gauge;
- portable L1 `QArtifact` production/provenance.

L5 deliberately does not own:

- native survey file ingestion or cuts;
- construction of cosmological solve grids / expected-count arrays;
- online latent count likelihood;
- GW host-density likelihood math.

The prepared-voxel seam prevents the LSS package from reabsorbing the accepted surveys/core responsibilities.

## Next slice

Proceed to **L6: latent-field / galaxy-count likelihood**.

L6 is the first online field slice. It must preserve the same gauge/support/indexing semantics while making the field/count channel proposal-dependent rather than precomputing a fixed Q table. It must not silently reuse the fixed-table posterior mean as though it were a latent likelihood.
