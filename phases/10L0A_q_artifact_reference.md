# Phase 10 L0A — Q artifact / radial primitive legacy reference

Status: **ACCEPTED**

## Frozen references

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
core runtime:     ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
surveys product:  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2
probe:            tools/probe_lss_q_artifact.py
golden:           references/lss_l0a_legacy_reference.json
```

No production `darksirens-lss` code existed during this reference freeze.

## Scope frozen by L0A

The deterministic reference covers the narrow reusable Q-table seam:

```text
gaussian_correlation_spectrum
renormalize_q_mean_one
poisson_lognormal_map on a matched-count radial fixture
laplace_lognormal_members with a fixed seed
save_lss_completion_hdf5 / load_lss_completion_hdf5 artifact contract
fail-closed non-finite / false-budget-provenance writer behavior
```

It deliberately does not freeze GP3D, latent fields, multitracer composition, or
the GW likelihood. Those receive separate reference slices.

## Acceptance gate

Bootstrap run after fixing only the legacy package import dependency:

```text
run/job: 34683234584 / 103525582386
result:  SUCCESS
```

The generated JSON was committed verbatim as the golden. The true acceptance
rerun then required two fresh pinned-legacy processes to agree with each other
and with the committed file exactly:

```text
workflow: lss-l0a-reference
run:      34683294037
job:      103525740072
head:     e4188c397c5b684ddddf786ec76bec2ca3cef183
result:   SUCCESS
```

Every workflow step passed, including the exact committed-golden comparison.

The first bootstrap attempt (`34683166451`) failed before any LSS arithmetic ran
because importing the legacy `darksirens.redshift` package transitively imports
Astropy. The reference environment was repaired by adding Astropy only; no probe
or scientific implementation changed.

## Frozen numerical anchors

### Gaussian radial spectrum

```text
n_grid: 64
ell_grid: 5
sigma: 0.3
mean(P): 0.0900000068191053
hash: 81f2d611b1e38885a3aafef59a2ba56fd7fbae67a9ddd6963975e3f0b54ff6d1
```

### Q budget gauge

For the deterministic map fixture:

```text
shape: [5,16]
zero-budget bin: 3
renormalized logQ hash:
  67b029dbfb716a5ff3389c2ec37c4c9cda5cc87e4b6f849cb88d69207810817d
removed-monopole hash:
  dcfd3e06b0088dc07cfae378c0c8e2c6554aa84698413e296bd32ba7ffb2ef06
```

For the four-member cube:

```text
shape: [4,5,16]
renormalized member hash:
  4d58161ae4c27869403487ab7aea4cf82a73c48c3aba579ebcb3f0657d4f6f0d
member-monopole hash:
  bd46979aeb9942cb6e351043337ba57e0f3748c6a09179380b9dcb27b4b0b5c9
```

The weighted mean of `exp(logQ)` is one to floating precision in every bin with
nonzero missing budget. The zero-budget bin is bitwise unchanged for both map
and members.

### Matched-count radial solve

```text
q shape: [1,64]
q min:   0.985720938054289
q max:   1.0046245661568396
max |Q-1| in high-count bins: 0.014279061945711047
Q hash:  cf2c39f64839a17997111ce10e15bcfdf3207d56b07bc68702a743ae61a65b8b
s hash:  54611a30ff5223b7b36b0e35172fa8c9c3c34e0a4804fb3dfd96f16a92850cbd
lambda hash:
  d7e2127c2bbf45a1ea7d34fb6ca3893be7aafbc14de540edd4f0f19e88360a64
converged: true
```

### Fixed-seed Laplace members

```text
shape:      [4,1,64]
mean shape: [1,64]
member hash:
  640d5d9f23b2785a1d49c19f2b015a8f11ccd3333fbb44da2e62c98a4be2095a
mean hash:
  de0528941d08547ea6825281e1febac4d1c1a4dfd9c88cefaf72c39391b8ec64
same-seed repeated result: bit-identical
```

## Frozen artifact contract

The reference HDF5 roundtrip uses:

```text
group: /lss_completion
indexing: global
model: poisson_lognormal
completion_kind: laplace_members
realization_set_id: phase10-l0a-fixed-realization-set
n_members: 4
member_content_sha256:
  7711daf227dd7894f5751dd4e10edfa3f1c64966415600de9b6daa58e3769395
budget_renormalized: true
c_mode: aggregate
f_p_aware: true
q_support_depth: 0.55
```

The removed budget monopole roundtrips exactly, as do the map, members and z
grid. Member content hashing is over the exact contiguous member bytes.

## Safety pins

The writer refuses and leaves no output file for:

```text
non-finite logQ content
budget_renormalized=True without budget_monopole_logq
```

Those are part of the L1 production acceptance contract.

## Next slice

L1 may now create the `darksirens-lss` package with only:

```text
Q artifact value/schema object
HDF5 loader/writer
per-z mean-one budget operator
provenance / finite-value validation needed by that artifact contract
```

Do not yet add the radial solver, deterministic Q RedshiftModel, GP3D, latent
field, multitracer logic, or GW likelihood plumbing. L1 must compare its gauge
and serialized contract to this exact L0A golden before acceptance.
