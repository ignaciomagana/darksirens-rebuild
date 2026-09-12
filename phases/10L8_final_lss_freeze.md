# Phase 10 L8 — final darksirens-lss freeze

Status: **ACCEPTED / FROZEN — PHASE 10 COMPLETE**

## Final frozen LSS repository

`ignaciomagana/darksirens-lss`

```text
main SHA:  3429bb2f420239bc731cc9e73e50bf5351181c14
tree SHA:  7dff94d9a79f12e821a7f40f8d31f1a30435a8e5
version:   darksirens-lss 0.1.0
```

L8 introduced **no production, test, packaging, documentation, or permanent-CI
change** to this accepted L7 source.  It was an audit/freeze slice only.

After the temporary L8 workflow was removed, the audit branch ended at

```text
branch: l8-final-audit
head:   26de916eb4df90ab2b97e5413f64fbe931232377
tree:   7dff94d9a79f12e821a7f40f8d31f1a30435a8e5
```

The branch tree is therefore byte-identical to frozen `main`.

## Frozen dependencies

```text
legacy oracle:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

core:
  ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
  tree: 0608b75ff5c142bfba0fc15a4fad79e0fee1fa74

exact frozen core wheel:
  darksirens-0.1.0.dev0-py3-none-any.whl
  SHA256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
  source artifact: 10294880218

surveys:
  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2
  tree: 4c4043ee2bee2a5a8940242e2de37f5eb5dbab17
```

Neither frozen core nor surveys was modified during Phase 10.

## L8 final audit

Accepted audit run:

```text
run: 34717469494
workflow-only head: 5f379626abcc7df50fca74ed5ffb54af5adfba98
```

Before either job ran, the workflow compared the audit branch to the frozen L7
source SHA over

```text
src/
tests/
pyproject.toml
README.md
.github/workflows/ci.yml
```

and required an empty diff.  Both jobs passed this gate.  The only live L8 file
was the temporary audit workflow itself.

### Clean minimal wheel

```text
job:    103617167559
result: SUCCESS
pytest: 11 passed in 0.24 s
```

The job:

1. built `darksirens_lss-0.1.0-py3-none-any.whl` from the frozen source;
2. installed it non-editably with only NumPy 1.26.4 + HDF5 3.12.1 as runtime
   dependencies;
3. ran `pip check` successfully;
4. changed working directory to `/tmp` and proved `darksirens_lss` imported from
   `site-packages`, not the source checkout;
5. proved root import did not import `darksirens`, `darksirens_surveys`, JAX, or
   SciPy;
6. replayed the artifact/gauge regression suite from the installed wheel.

This is the clean-install and dependency-firewall acceptance gate.

### Exact frozen-core full matrix

```text
job:    103617167445
result: SUCCESS
pytest: 69 passed, 3 warnings in 59.53 s
```

The exact core wheel SHA256 was verified before installation.  The job then
installed the frozen core and the non-editable LSS wheel into the pinned
numerical environment:

```text
NumPy   1.26.4
SciPy   1.12.0
h5py    3.12.1
JAX     0.4.34
jaxlib  0.4.34
```

From `/tmp`, it proved the LSS package was loaded from `site-packages` and ran
**the complete `darksirens-lss/tests` directory**.  The 69 passing tests include
the accepted numerical anchors and integration contracts from L1--L7:

- Q artifact roundtrip and mean-one budget gauge;
- fixed deterministic Q tables and frozen L0B numerical redshift-prior anchors;
- compact/global row semantics, support-depth relaxation and exact Q=1 outside
  support;
- Q-member full-likelihood marginalization and matched table-ensemble
  provenance;
- radial Poisson-lognormal builder;
- GP3D and joint multi-survey builders;
- latent count likelihood / Laplace evidence;
- latent Q gauge and footprint mapping;
- K=1 frozen-core latent HBI integration;
- K>=2 field-global normalization and shared latent member composition;
- `(N_samples, K_catalogs)` GW pixel-frame integration through frozen core;
- auxiliary count evidence entering the complete member likelihood exactly once.

The three warnings are the already-explicit GP3D resolution warnings in small
test fixtures; they are not convergence or numerical failures.

## Pre-acceptance L8 harness failure

The first L8 audit attempt

```text
run: 34717391937
jobs: 103616965209 / 103616965260
```

stopped before any wheel build or package test because `actions/checkout` used
its default shallow history and the frozen L7 baseline commit could not be
resolved by `git diff`:

```text
fatal: Invalid revision range 3429bb2...HEAD
```

The correction was workflow-only: `fetch-depth: 0`.  No science or package file
changed.

## Phase-10 accepted slice ledger

The final package is the composition of the accepted incremental slices:

```text
L0A  pinned legacy Q/artifact/radial reference
L0B  pinned legacy fixed-table runtime reference
L0C  pinned legacy ensemble/member reference
L1   Q artifact + budget-gauge package layer
L2   deterministic fixed-table RedshiftModel
L3   Q-member full-likelihood marginalization + provenance
L4   radial Poisson-lognormal builder
L5   GP3D + joint multi-survey builders
L6   latent field/count K=1 online model
L7   field-global normalization + matched K-tracer latent composition
L8   clean-wheel/full-matrix audit and final freeze
```

The detailed L6 and L7 closure records are

```text
phases/10L6_latent_count_model.md
phases/10L7_multitracer_global_model.md
```

and the earlier slice/reference records under `phases/10L*` and
`references/lss_l*` remain the immutable evidence for their respective
contracts.

## Final scientific contracts

### Q semantics

`Q` is a **placement field**, not a missing-budget amplitude.  Its accepted
mean-one gauge is

```text
sum_p w_p(z) Q_p(z) = sum_p w_p(z),
w_p(z) = (1 - C_p(z)) dN_exp(p,z).
```

Off-footprint and unsupported Q is exactly unity (`logQ=0`).  Table indexing,
`c_mode`, `f_p_aware`, support depth, convergence state and ensemble provenance
are explicit; consumers do not guess them from shapes.

### Table ensembles

For persisted table ensembles, member marginalization is over **complete** GW
likelihoods, including PE and selection, and only then applies `logmeanexp`.
Matched multi-survey table ensembles use equal member count plus a common
non-null `realization_set_id`; per-survey member-content hashes are not required
to match.

### Latent field

The latent mode uses the same missing-budget gauge.  The field is one shared
member coordinate across K tracers.  Each tracer retains its own

```text
C_k(z), f_{k,p}, b_GW,k, Z_k
```

against that common field.  Table-era realization IDs are not used to certify
this structural shared-member relation.

### Field/global normalization

Under the accepted aggregate convention

```text
C_{k,p}(z) = f_{k,p} C_k(z),
```

the gauge reduces the tracer's all-sky missing curve to

```text
V_k(z) = N_pix,k - C_k(z) F_{F,k},
F_{F,k} = sum_p f_{k,p}.
```

The online L7 constructor verifies the complete full-sky `f_p` frame rather
than trusting only the artifact scalar `F_F`.

The survey-global tracer normalizer is

```text
Z_k = N_obs,k(global) + integral dz dN_exp,k(z) V_k(z).
```

`Z_k` cancels for K=1 and under a common K-tracer shift, but relative `Z_k`
values remain inside a K>=2 catalog mixture and therefore matter physically.

### K-tracer parameterization

Latent host-field biases stay per tracer under legacy-compatible labels

```text
b_miss, b_miss_c2, ..., b_miss_cK
```

and catalog fractions retain the legacy stick coordinates

```text
fcat_2, ..., fcat_K,
fcat_m ~ Beta(1, K-m+1),
```

which implement a uniform simplex prior.  Boundary sticks are handled in log
space without NaNs.

## Final ownership / dependency boundary

`darksirens-lss` owns:

```text
Q artifacts and budget gauge
offline radial / GP3D / joint LSS builders
fixed-Q and Q-ensemble RedshiftModel state
latent count-field state and Laplace evidence
latent Q member construction
field/global tracer normalization
matched K-tracer latent host-density composition
```

Frozen core owns:

```text
cosmology grids and transforms
population models and weighting
GW PE reduction
GW detector-selection integration
likelihood variance / ESS guards
sampler construction and execution
```

Surveys owns survey-native catalog interpretation and selection products.
Lensing remains a separate companion package.

Dependency direction remains one-way.  `darksirens-core` does not import LSS,
and importing `darksirens-lss` itself requires neither core nor JAX/SciPy.
Runtime package dependencies remain NumPy + HDF5; heavier numerical packages are
used only by builder/online paths when invoked.

## Final Phase-10 decision

**Phase 10 is closed. `darksirens-lss` main is frozen at
`3429bb2f420239bc731cc9e73e50bf5351181c14`, tree
`7dff94d9a79f12e821a7f40f8d31f1a30435a8e5`.**

No further LSS production work is part of this reconstruction unless a later
ecosystem integration audit exposes a concrete cross-package defect.
