# Phase 6D checkpoint — generic unit-cube prior transform

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
6C1 accepted:      807687ccb5754af14f888df3089497f26706e234
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

## Scope

6D reconstructs only the generic, already-resolved unit-cube transform from
pinned `darksirens/inference/prior.py`:

```text
make_prior_transform(lower, upper, prior_kinds=None, joint_constraints=None)
```

The caller supplies final bounds, one prior-kind triple per sampled coordinate,
and any joint constraints already resolved to integer indices. Core does not
look up population, survey, sky, LSS, or lensing models in this slice.

## Frozen per-dimension semantics

- `lower` and `upper` are converted to NumPy float arrays once when the closure
  is built.
- `prior_kinds=None` means an all-uniform affine map.
- Supported frozen kind spellings are `uniform`, `normal`, `lognormal`, `beta`.
- `normal` is an inverse-CDF Gaussian truncated to `[lower, upper]`.
- `lognormal` applies the same truncated-normal inverse CDF in log space and
  exponentiates.
- `beta` is specifically Beta(1,b), with `b` in the scale slot and an analytic
  inverse CDF; `[lower, upper]` acts as truncation bounds.
- Beta(1,1) inside `[0,1]` is normalized to the uniform kind before dispatch.
- The truncated-normal probability passed to `ndtri` is clipped to
  `[1e-12, 1-1e-12]` exactly as in frozen legacy.
- Family branches absent from a resolved space are not evaluated at trace time.

## Frozen joint cube maps

`joint_constraints` is a sequence of `(kind, index_tuple)` entries applied
before the per-coordinate transforms:

```text
ordered_le         (i,j): sort the two cube coordinates
simplex            (i,j): fold across u_i + u_j = 1
conditional_upper  (i,j): u_i <- u_i * u_j, u_j unchanged
ball3              (i,j,k): polar map to a uniform unit ball
```

The `conditional_upper` product spelling is load-bearing: the `u_j=0` edge
returns the common lower bound exactly without introducing a denominator/NaN.
`ball3` uses `r=u^(1/3)`, `cos(theta)=2u-1`, and `phi=2*pi*u` before mapping
back to cube coordinates.

This slice accepts only already-resolved index maps. Validation that a requested
joint constraint is legal for model labels/bounds remains with the future
parameter-space resolver; 6D does not import model registries to recreate it.

## Numerical/dispatch semantics

- All-uniform/no-joint transform remains host-native: NumPy input produces a
  NumPy affine output with no forced JAX device round trip.
- That closure carries `host_native=True`.
- All-uniform with joint constraints is JAX-based but carries no fast-dispatch
  flag.
- Any genuinely non-uniform transform carries `prefer_jit=True`.
- 6D does **not** port `_make_dynesty_ptform`; acceptance tests only verify the
  flags and transform values. The sampler-specific bit-identity probe/dispatch
  remains a later sampler-adapter subphase.
- Batched `(..., ndim)` inputs retain the frozen `u[..., i]` behavior.

## Explicit non-scope

Do not port in 6D:

```text
build_parameter_space
resolve_joint_prior_constraints
population/survey/sky registries
prior override parsing
fixed-parameter validation
selection-fit prior discovery
CLI options
_make_dynesty_ptform
run_sampler
dynesty / TinyNS / NumPyro backends
LSS or lensing state
```

## Dependency boundary

`darksirens.inference.prior` imports NumPy at module scope. JAX and
`jax.scipy.special` remain lazy/branch-local exactly as the frozen transform
requires: importing the module or constructing an all-uniform/no-joint transform
does not eagerly import sampler backends, CLI, surveys, LSS, lensing, or HEALPix.

## Acceptance

Accepted at exact core head:

```text
5edc76c6c055e47a7e041d7f7477e347837f7554
```

Workflow:

```text
run:    34550319391
job:    103111665242
result: SUCCESS
```

Results:

```text
6D focused tests:                 13 passed
full reconstructed suite:        325 passed, 1 regeneration-only skip
portable dependency audit:       PASS
6A separate-process parity:       exact
6B separate-process parity:       exact
6C1 separate-process parity:      exact
6D separate-process parity:       bit-exact dtype/shape/raw bytes
preserved Phase-5 parity:         exact, max_abs=max_rel=0
comparison:                       rtol=1e-12, atol=0
```

The parity probe explicitly enables the validated JAX x64 convention on both
legacy and candidate processes, then records deterministic transform outputs as
dtype, shape, and raw bytes rather than rounded decimals. Uniform/Beta(1,1),
truncated normal/lognormal/Beta, all four joint maps, sequential maps, and
batched/per-row spellings matched exactly.

No target-specific parameter-space builder or sampler dispatch was accepted in
6D.

## Next

Proceed to Phase 6E: dynesty state-only checkpoint serialization/rebinding. Keep
dynesty optional and lazily imported. Do not introduce the full sampler runner,
TinyNS configuration/runtime, diagnostics, RNG policy, or CLI assembly in the
same slice.
