# Phase 10 L2 — deterministic fixed-table Q model

Status: **ACCEPTED / FROZEN**

## References

```text
legacy oracle:       ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
frozen core main:    ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
frozen core tree:    0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
L0B golden:          references/lss_l0b_legacy_reference.json
L0B record:          phases/10L0B_fixed_table_reference.md
accepted LSS main:   ignaciomagana/darksirens-lss@3dc0bca6677b06f2c8b14b0be014baa18ba663be
accepted LSS tree:   37e1c06a7b817f4a0b28d67664406fd45ee4ff4a
```

Core and surveys main branches were not modified.

## Production scope

L2 adds the first core-coupled runtime model to `darksirens-lss`:

```text
FixedTableState
build_fixed_table_state(...)
build_fixed_table_prior_state(...)
FixedTableQModel
```

The implementation composes the frozen core catalog machinery instead of
copying legacy `completion.py` or the GW hierarchical reducer. It reuses:

```text
build_observed_density_cache
build_catalog_kernel_state
completion_curves
IncompleteCatalogPriorState
eval_incomplete_catalog_prior_state[_vmap]
RedshiftModel host-density extension seam
```

The only scientific modification to the ordinary per-pixel missing branch is

```text
dN_miss,Q(row,z) = dN_miss,ordinary(row,z) * Q_eff(row,z)
```

followed by the same row normalization

```text
Z_row = N_obs,row + integral dN_miss,Q dz.
```

`FixedTableQModel` has an empty sampled parameter block and zero auxiliary
likelihood; deterministic Q is data, not a new sampled field in L2.

## Frozen deterministic-Q semantics

```text
Q_eff = exp(clip(logQ, -7, +7))
```

with exact identity behavior:

```text
Q_eff = 1 above q_support_depth, when the artifact carries one
Q_eff = 1 above catalog z_depth
bit-zero off-footprint logQ row => exactly Q=1
```

Compact and global artifacts are aligned to the same compact runtime row frame.
The Q table must have the exact frozen-core `N_grid`; a stored zgrid must match
within the mature loader tolerance. There is no silent Q interpolation.

L2 supports only the frozen-core ordinary `c_mode='per_pixel'` completeness
base. A missing historical c_mode stamp is interpreted as legacy per-pixel.
The following fail closed:

```text
c_mode='aggregate'
c_mode='selection'
f_p_aware=True
ensemble/member-only artifact without logq_map
wrong N_grid or mismatched stored zgrid
global table that does not cover required global pixels
```

Aggregate/selection bases and explicit `f_p` composition are later science
slices, not approximated through per-pixel completeness.

## Runtime-array correction found by the exact-core gate

The first genuine exact-wheel replay exposed one production bug: host-side
`GalaxyCatalog` objects may be NumPy-backed, while the frozen core vmap indexes
catalog rows with JAX tracers. Passing the NumPy arrays through unchanged caused
`TracerArrayConversionError` in `eval_log_catalog_prior_state`.

L2 now validates the standardized catalog host-side, then materializes one
runtime `GalaxyCatalog` with JAX arrays during `build_fixed_table_state`. This is
an execution-representation correction only: values, row ordering, global pixel
ids, catalog parameters and Q semantics are unchanged.

The first exact-wheel run before this fix was:

```text
run/job: 34685101233 / 103530617569
result:  FAILURE
pytest:  14 passed, 4 failed
```

Three failures were non-portable cross-runner byte hashes of JAX/libm-generated
floating values. All corresponding same-run structural assertions and numerical
ratios had already passed. The fourth was the real NumPy/JAX tracer-indexing bug
above.

## Cross-runner numerical parity policy

L0A and L0B retain their exact byte hashes in the control repo; those are valid
oracle products from their pinned acceptance runners. Replaying transcendental
NumPy/JAX arithmetic on different GitHub CPU images can move only the last few
floating-point bits, so package-level cross-runner tests do not claim those bits
are science.

L2 therefore keeps the following **exact** inside one run:

```text
compact/global row alignment
bit-zero off-footprint Q == unity-Q result
Q == 1 above support
Q == 1 above survey depth
artifact persistence of caller-supplied bytes
zgrid stored-data hash
all fail-closed semantic walls
```

and compares the frozen legacy cross-run numerical anchors at tight tolerance.
In particular the accepted fixture reproduces

```text
N_miss(Q=3,Q=5):
  5061691991.54231
  8436153322.667488

clip rails:
  exp(+7) = 1096.6331584284585
  exp(-7) = 0.0009118819655545162

assembled-prior query values:
  -6.293368583194001
  -4.88357092152026
  -4.446413977412931
  -3.9113798761872545
  -3.381789866503734
  -2.067680206864374
```

The L0B oracle remains the authoritative exact-hash record.

## Permanent standalone gate

Permanent `darksirens-lss` CI deliberately remains independently installable
without core. Core/JAX coupling is lazy and no core dependency was added to
`pyproject.toml`.

```text
workflow: ci
run:      34685194226
job:      103530866293
head:     3dc0bca6677b06f2c8b14b0be014baa18ba663be
result:   SUCCESS
pytest:   11 passed in 0.21 s
compile:  PASS
pip check:PASS
firewall: PASS
```

The root-import firewall proves importing `darksirens_lss` does not initialize
`darksirens` or `darksirens_surveys`, even though the root exposes the L2 model
symbols. Runtime package metadata still contains only the standalone NumPy/h5py
dependencies; SciPy, JAX and core remain peer/runtime concerns.

## Private-sibling Actions limitation

An attempted permanent job using `actions/checkout` on the private sibling core
repository failed before any L2 code ran:

```text
run:      34684934927
job:      103530175262
failure:  remote: Repository not found.
          fatal: repository 'https://github.com/ignaciomagana/darksirens-core/' not found
```

This is the same repository-scoped GitHub Actions token limitation already
observed in surveys S6 and is infrastructure-only evidence.

## Exact frozen-core wheel acceptance

The accepted cross-package replay used the previously exported frozen core wheel:

```text
core source SHA:   af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
core artifact run: 34682157415
core artifact job: 103522654109
artifact id:       10294880218
wheel:             darksirens-0.1.0.dev0-py3-none-any.whl
wheel SHA-256:     4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

A temporary branch contained only signed artifact-download plumbing on top of
the accepted main candidate. The final replay was:

```text
branch:   l2-private-core-probe
run:      34685214822
job:      103530920879
result:   SUCCESS
pytest:   18 passed in 8.72 s
pip check:PASS
root import one-way: PASS
```

Resolved frozen-core dependency stack included:

```text
jax       0.4.34
jaxlib    0.4.34
numpy     1.26.4
scipy     1.12.0
h5py      3.12.1
tinyns    3f9e1b2537f32b59f17ee9ce68b2d725681a024c
darksirens 0.1.0.dev0
```

After success, `l2-private-core-probe` was force-reset to the accepted main SHA
`3dc0bca6677b06f2c8b14b0be014baa18ba663be`. The temporary workflow and signed
URL therefore do not remain at the branch head.

## Explicitly not in L2

No code for the following was migrated in this slice:

```text
Q-ensemble/member marginalization
matched realization-set marginalization across catalogs
field/global sky normalization
aggregate or parametric-selection completeness bases
f_p-aware Q runtime composition
GP3D fitting
latent LSS fields / count likelihood
marks+Q joint field normalization
survey construction
lensing
```

## Next action

Freeze an L0C oracle for **Q-ensemble/member marginalization and matched
provenance** before adding L3. The next slice should capture the mature
posterior-mean deterministic fallback, per-member effective Q, member-specific
missing normalizers, log-mean-exp likelihood marginalization, and the
K>=2 shared-member realization-set guard. GP3D/latent reconstruction remains
out of scope until that loaded-ensemble contract is accepted.
