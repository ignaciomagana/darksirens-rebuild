# Phase 7C1 — joint-prior constraint resolver

## Status

ACCEPTED

## Core branch / head

```text
repository: ignaciomagana/darksirens-core
branch:     rebuild/phase7-public-api
accepted:   02b54e25740ff7cce1a030f372b3190121ad2b0f
parent:     b97d949f32c0eff3bb48c574b5a2258f92fe82d5  (accepted 7B)
```

## Scope

Phase 6 already reconstructed and validated the sampler-facing joint cube maps,
but the model-driven resolver that decides which maps apply to the currently
sampled coordinates was still missing. 7C1 ports only that small ordinary
population responsibility from frozen `inference/prior.py`.

The new resolver:

- reads `constraint_groups` from the existing core population registry;
- resolves declared group labels onto the currently sampled indices;
- preserves the frozen admissibility rules for `ordered_le`, `simplex`,
  `ball3`, and `conditional_upper`;
- silently leaves a group to likelihood-side rejection when a member is fixed
  or absent;
- preserves the exact frozen `RuntimeWarning` and rejection fallback when
  bounds/prior kinds no longer make the cube map the declared normalized
  density;
- stays JAX-light at module import and discovers the population model lazily.

No sky-model switchboard was ported. The parity probe executes the frozen
resolver with `sky_model=None`, which is the ordinary core population path.

## Scientific necessity

The GWTC-5 fiducial BPL+2G population declares two load-bearing groups:

- a simplex prior for `lambda0 + lambda1 <= 1`;
- `conditional_upper` for the Table-5 conditional
  `m2_low | m1_low ~ U(lower, m1_low)`.

Likelihood-side rejection alone would leave invalid prior volume in the nested
sampling cube and would not reproduce the declared conditional density. 7C1
therefore restores a required construction step without changing the already
accepted transform or population model.

## Files

```text
src/darksirens/inference/joint_prior.py
tests/test_joint_prior_resolver.py
tools/probe_joint_prior_resolver.py
.github/workflows/phase7c1-joint-prior-resolver.yml
```

## Acceptance gates

Dedicated exact-head resolver gate:

```text
run: 34596093457
job: 103252070961 (joint-prior-resolver)
status: SUCCESS
```

This passed lint/compile, JAX-light import, focused resolver tests, AST-extracted
frozen resolver evaluation, reconstructed evaluation, and exact comparison of
results and warning text.

Broad Phase-7 regression:

```text
run: 34596093340
job: 103252070365 (regression)
status: SUCCESS
```

It passed the full reconstructed suite and companion-import boundary.

Earlier public-surface replay on the same head:

```text
7B public specs:   34596093404 / 103252070763 SUCCESS
7A public loaders: 34596093417 / 103252070885 SUCCESS
```

## Exclusions

7C1 does not reconstruct:

- the giant legacy `build_parameter_space`;
- `build_parameter_decoder`;
- sky/LSS/lensing constraints;
- `ds.model()`;
- `ds.infer()`.

## Next slice

Phase 7C2: add `ds.model()` as typed analysis construction only. Preserve the
frozen global sampled-coordinate order (cosmology -> population -> ordinary
catalog nuisance block), attach 7C1 joint constraints, and represent
spectral/incomplete-catalog/complete-catalog composition explicitly without a
`universe_model` switchboard. Keep execution and `ds.infer()` separate.
