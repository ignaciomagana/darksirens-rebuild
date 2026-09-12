# Phase 10 L1 — Q artifact and missing-budget gauge

Status: **ACCEPTED**

## References

```text
legacy oracle:       ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
L0A golden:          references/lss_l0a_legacy_reference.json
frozen core:         ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
frozen surveys:      ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2
LSS accepted head:   ignaciomagana/darksirens-lss@4c565aa3a542385d4f251c78403f3f9c4e656365
LSS accepted tree:   29ac4ec69b25e2f3b2a6059be5d2063bfdde91a7
```

## Scope

L1 initializes the previously empty `darksirens-lss` repository and ports only:

```text
QArtifact
renormalize_q_mean_one(...)
write_q_artifact(...)
load_q_artifact(...)
```

There is no radial solver, GP3D builder, latent field, core RedshiftModel,
multitracer composition, GW likelihood, or survey-native code in this slice.
The package runtime dependencies are only NumPy and h5py.

## Scientific convention

The budget operator preserves the mature gauge exactly:

```text
sum_p w_p(z) Q_p(z) = sum_p w_p(z)
```

in every nonzero-budget redshift bin. Zero-budget bins are bitwise unchanged and
have zero removed monopole. No extra finite-input guard was introduced into the
operator: non-finite persistence is rejected at the artifact I/O boundary, as
in the mature implementation.

The L1 tests regenerate the L0A deterministic fixture and require exact hashes:

```text
map logQ:
  67b029dbfb716a5ff3389c2ec37c4c9cda5cc87e4b6f849cb88d69207810817d
map removed monopole:
  dcfd3e06b0088dc07cfae378c0c8e2c6554aa84698413e296bd32ba7ffb2ef06
member logQ cube:
  4d58161ae4c27869403487ab7aea4cf82a73c48c3aba579ebcb3f0657d4f6f0d
member removed monopoles:
  bd46979aeb9942cb6e351043337ba57e0f3748c6a09179380b9dcb27b4b0b5c9
```

Those exact-hash tests passed even under the clean L1 resolver's NumPy 2.4.6,
which is a useful independent check that this deterministic gauge fixture is not
an artifact of the NumPy 1.26.4 oracle environment.

## Artifact contract

The new `QArtifact` represents the mature `/lss_completion` product with:

```text
logq_map / logq_members / zgrid
indexing
model
completion_kind
diagnostics
realization_set_id
member_content_sha256
n_members
budget_renormalized
budget_monopole_logq
c_mode
f_p_aware
q_support_depth
```

The writer keeps `f_p_aware` optional rather than manufacturing an explicit
False stamp when the caller supplied no provenance. The loader retains the
mature conservative interpretation: an absent historical `f_p_aware` stamp
loads as False.

The writer is atomic and fails closed on non-finite Q content and on a
`budget_renormalized=True` claim without the removed monopole curve. Member
content SHA-256 is computed over the exact contiguous member bytes.

Legacy unstamped budget artifacts remain readable with a runtime warning rather
than being silently upgraded.

## Acceptance gate

```text
workflow: ci
run:      34683496384
job:      103526278421
head:     4c565aa3a542385d4f251c78403f3f9c4e656365
result:   SUCCESS
pytest:   11 passed
compile:  PASS
pip check:PASS
firewall: PASS
```

The dependency/ownership firewall confirms:

```text
root import does not import darksirens-core
root import does not import darksirens-surveys
no source import of darksirens-surveys or darksirens-lensing
no SciPy/JAX/core distribution dependency in L1
```

## Post-acceptance portability note

During L2 integration, the same deterministic fixture was regenerated on
additional GitHub-hosted CPU runners. The weighted mean-one values and all
scientific invariants agreed at floating-point precision, but arrays involving
NumPy/JAX `exp`/`log` did not retain one universal SHA-256 across runner CPU/libm
paths, including when NumPy was pinned back to 1.26.4.

This does **not** invalidate the accepted L0A golden or the L1 acceptance above.
The exact hashes remain the immutable record of the pinned L0A oracle run. What
changed after L2 was the package-level replay policy: cross-runner tests now pin
the actual frozen numerical monopoles with tight tolerance and exact mean-one /
zero-budget invariants, rather than treating backend last bits as part of the
science.

Byte identity is still required where bytes are genuinely the contract:

```text
HDF5 round-trip of caller-supplied Q arrays
member_content_sha256 over the exact supplied member bytes
zero-budget bins copied unchanged within one run
```

The portability correction was accepted as part of L2; see
`phases/10L2_fixed_table_model.md`. The original L1 workflow evidence and exact
L0A hashes above are intentionally retained rather than rewritten.

## Next action

Before adding a production fixed-table Q `RedshiftModel`, freeze L0B from the
legacy oracle. L0B must capture the deterministic table interpolation/indexing,
Q-support cutoff, off-footprint unity behavior, completion-base semantics, and
the fixed-table effect on the redshift/likelihood path. Only after that reference
is accepted may L2 connect this package to the frozen core host-density seam.
