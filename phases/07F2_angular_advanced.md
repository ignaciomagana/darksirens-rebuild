# Phase 7F2 — advanced angular source-population models

## Scope

Reconstruct the remaining reusable frozen angular source-population models in
`darksirens-core` without wiring them into the public analysis/likelihood yet.
The frozen reference is `ignaciomagana/darksirens` at
`c042527238bd71421b792936bc48c3b815b90d6d`.

Models accepted in this slice:

- `sphere_gp`
- `sphere_gp_z`
- `overdensity_gp`
- `multipole` (`lmax=2`)
- `multipole_l3` (`lmax=3`)

This remains core-owned population structure. No survey-native schema, LSS/Q,
lensing, campaign CLI, or `healpy` runtime dependency was introduced.

## Accepted core head

```text
branch: rebuild/phase7-public-api
head:   877bda4e5e2e10ac52c657f7990159afcfa1093a
tree:   9188244eea1f71bf3fbbb6f9e1e7162151e6df77
parent: 6f4126792be9481860f893042e1efa253b46d1ec  (accepted 7F1)
```

## Frozen behavior preserved

- deterministic Fibonacci-sphere inducing/quadrature geometry;
- chordal-distance sphere RBF and sphere×redshift product kernel;
- whitened finite-rank GP parameterization and normal `xi` priors;
- field clipping and frozen jitter constants;
- sphere-GP mean-one normalization;
- sphere×z GP per-redshift-shell mean-one normalization on the resolved
  `zeta=log1p(z)` grid;
- 3-D overdensity GP global mean-one normalization using the frozen fiducial
  comoving-volume weight `dV_c/dz * (1+z)`;
- NaN-redshift propagation rather than replacement by a finite sentinel;
- explicit orthonormal real spherical harmonics through `l=3`;
- multipole global positivity on the 2048-point Fibonacci grid;
- multipole coefficient ordering and exact frozen lmax error string;
- multipole prior-volume correction `log(f_valid)`, which is part of the
  evidence contract and must be subtracted from raw `logZ`;
- frozen registry names, LaTeX labels, prior bounds/kinds, machine names, and
  isotropic fiducials;
- compile-time-eager registry construction via `jax.ensure_compile_time_eval()`.

The only ownership adaptation is that `OverdensityGP3DAngular` imports the
already reconstructed core cosmology rather than the legacy
`darksirens.utils.cosmology` path. The parity probe checks the resulting
`_log_vol_w` values directly.

## Acceptance gates

Dedicated advanced-angular gate:

```text
workflow: phase7f2-angular-advanced
run:      34625983191
job:      103351075167
status:   SUCCESS
```

The dedicated gate separately executes the pinned legacy and candidate models
and requires exact JSON equality for bounds, labels, prior kinds, LaTeX,
fiducials, machine names, representative GP/multipole `log_g` values,
normalization diagnostics, 3-D volume weights, multipole `(l,m)` ordering, and a
deterministic multipole prior-volume fraction.

Broad exact-head regression:

```text
workflow: phase7-regression
run:      34625983125
job:      103351074718
status:   SUCCESS
result:   511 passed, 1 skipped
```

The skip is the existing opt-in population-registry golden regeneration test.
The broad companion-boundary scan also passed.

Representative same-head replays:

```text
7F1 basic angular: 34625983180 / 103351075009 SUCCESS
7E public infer:   34625983179 / 103351074824 SUCCESS
7D runtime bind:   34625983282 / 103351075883 SUCCESS
7C3 geometry:      34625983437 / 103351076407 SUCCESS
7C2 public model:  34625983106 / 103351074717 SUCCESS
7C1 prior resolver:34625984063 / 103351078805 SUCCESS
7B public specs:   34625983242 / 103351075262 SUCCESS
7A public loaders: 34625983270 / 103351075561 SUCCESS
```

## Decision

Phase 7F2 is accepted at exact head
`877bda4e5e2e10ac52c657f7990159afcfa1093a`.

The next legitimate slice is not more angular-model physics. It is the thin
composition/wiring layer that appends an angular parameter block to the public
`ParameterPlan`, decodes that block separately, and applies the same
`log g(nhat,z)` factor to PE and selection weights. The catalog redshift model
itself must remain unchanged.
