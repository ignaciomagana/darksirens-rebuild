# Phase 10 L0B — deterministic fixed-table Q legacy reference

Status: **ACCEPTED**

## References

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
L0A golden:       references/lss_l0a_legacy_reference.json
L0B golden:       references/lss_l0b_legacy_reference.json
probe:            tools/probe_lss_fixed_table.py
frozen core:      ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
accepted L1 LSS:  ignaciomagana/darksirens-lss@4c565aa3a542385d4f251c78403f3f9c4e656365
```

No L2 production fixed-table model existed while this reference was frozen.

## Scope frozen by L0B

The deterministic oracle freezes the mature fixed-table consumer rather than the
offline Q builder:

```text
compact-table row alignment
global-table -> compact-row gathering semantics
off-footprint Q = 1 identity behavior
logQ clipping to +/-7 before exponentiation
explicit Q support truncation to exact unity above support
N_grid mismatch failure
stored-zgrid mismatch failure; no silent Q interpolation
c_mode provenance mismatch failure
interpolation of the fully assembled conditional redshift prior at arbitrary z
```

The Q table itself is node-for-node on the package redshift grid. It is not
silently interpolated to a new Q grid. The only interpolation in the frozen
runtime fixture is the already-assembled redshift-prior evaluation at event
redshifts.

## Acceptance history

The first bootstrap run:

```text
run/job: 34683754040 / 103526978612
```

executed both numerical probes successfully. Its post-probe determinism check
failed only because the legacy loader includes the random temporary directory in
its provenance path and error text. No numerical or scientific quantity differed
between the two processes.

The harness was repaired only by canonicalizing
`/tmp/darksirens-lss-l0b-* -> <TMP>` after each process. The probe arithmetic and
physics assertions were unchanged.

Bootstrap after that normalization:

```text
run/job: 34683835370 / 103527195676
result:  SUCCESS
```

The generated normalized JSON was committed verbatim as the golden. The true
exact-golden acceptance rerun was:

```text
workflow: lss-l0b-reference
run:      34683927830
job:      103527448610
head:     5a98b3292d5f6ada810e6d1e365238b7437458a9
result:   SUCCESS
```

Every step passed, including the exact committed-golden comparison.

## Frozen numerical anchors

Core package redshift grid:

```text
N_grid: 1000
zgrid hash:
  daa2790273939e0a61030562f47d381ba2d1028e222e53b2909eda857faded99
```

### Compact/global alignment

Two compact rows carrying constant Q=3 and Q=5 are bit-identical to a global
Q table gathered through global pixel ids `[5,2]`:

```text
dN_miss hash:
  be066242f07fd4c6314b508903c1d9a79b010075e5046a5e2b3efafe37d699a7
N_miss:
  5061691991.54231
  8436153322.667488
```

### Off-footprint identity

A global pixel whose stored logQ row is exactly zero produces exactly the unity-Q
missing curve:

```text
row hash:
  eebe6289294deb0c55982d63cdc9f02cd1d5dbfb2f13530c1437abc5a2a37640
bit-identical to unity: true
```

### Explicit support cutoff

A synthetic table with Q=2 through z<=0.30 and Q=1 above gives:

```text
max |ratio-2| below support: 0
max |ratio-1| above support: 0
support table hash:
  f7464254e8e219cb35b07edef6ea957714c63c89518c3e8f5ac6517d261280f9
modulated missing-density hash:
  8d82a6c759c427dcc61856ebd0720c3b91241c05f67322426b8e123989a6fd45
```

This freezes the consumer-side contract that a builder-supported region ends in
bit-zero logQ / exact Q=1 rather than extrapolated structure.

### logQ rail

The mature consumer clips loaded deterministic logQ to +/-7:

```text
exp(+7) = 1096.6331584284585
exp(-7) = 0.0009118819655545162
```

The frozen clipped missing-density hash is
`060dbca6b80e1fdde9231947b7d348751b8cec0ac80eb6d2054cf55c8b9e16bc`.

### No silent table interpolation

A `(N_rows,1001)` table against the 1000-node package grid is rejected with
`ValueError`. A 1000-node table carrying a numerically shifted stored zgrid is
also rejected with:

```text
LSS completion zgrid does not match the package zgrid (no silent interpolation).
```

### c_mode provenance

The loader rejects an aggregate-base Q table when the requested run uses the
per-pixel completeness base. This fail-closed behavior is frozen because the two
bases differ by the observed clustering signal itself.

### Assembled-prior evaluation

The fixture queries six off-grid event redshifts after constructing the mature
conditional dark-siren prior. The fixed sinusoidal Q table changes the prior by
up to

```text
max |Delta log p| = 0.32494751977939274
```

Frozen hashes:

```text
Q prior logp:
  853a5dc6db042b447e6f1bacf62de889947e7c0c5e88ffd4cc6e74a0e46f064e
unity prior logp:
  6d0f7fa0562a48ed0ebf36d48dd42ab35cd7d32171291e874c8bdd0b8e2c53cd
```

## L2 production boundary

L2 may now implement only deterministic fixed-table Q on top of the frozen core
catalog machinery.

The first L2 implementation must reuse core's accepted:

```text
build_catalog_kernel_state / eval_log_catalog_prior_state
ordinary per-pixel completion_curves
IncompleteCatalogPriorState evaluator
host_density RedshiftModel extension seam
```

and change only the missing branch:

```text
dN_miss_Q(row,z) = dN_miss_ordinary(row,z) * Q_eff(row,z)
```

with:

```text
Q_eff = exp(clip(logQ,-7,+7))
Q_eff = 1 above q_support_depth when supplied
Q_eff = 1 above catalog z_depth, matching mature beyond-depth relaxation
```

Then recompute the same row normalizer `Nobs + integral dN_miss_Q dz` and use the
core evaluator for the additive observed+missing prior.

For L2 specifically, support **only `c_mode=per_pixel`** (including a legacy
artifact with no c_mode stamp, interpreted as per_pixel). Frozen core currently
owns only that ordinary completeness base. `aggregate` and `selection` tables
must fail closed until a later slice explicitly reconstructs those bases; do not
approximate them by reusing per-pixel completeness.

Likewise, L2 should not add field/global normalization, member marginalization,
latent state, or GP3D. Those remain later slices.
