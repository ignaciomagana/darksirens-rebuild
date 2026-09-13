# Phase 11 L4 — PairKDE / unmarked J=2 likelihood freeze

Status: **ACCEPTED / FROZEN**

## Accepted production state

```text
repository: ignaciomagana/darksirens-lensing
main SHA:   706bc4fc16aaaf2f0ec0b05b108c91499d8dde7e
tree:       204882d3ef3effd79db395e026eec11ff1c238bc
promotion:  PR #3
```

Frozen dependencies remain unchanged:

```text
core SHA:          af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
core tree:         0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
exact core wheel:  darksirens-0.1.0.dev0-py3-none-any.whl
core wheel SHA256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
legacy oracle:     c042527238bd71421b792936bc48c3b815b90d6d
L0C golden:        references/lensing_l0c_pair_legacy_reference.json
```

## Production surface

L4 adds:

```text
src/darksirens_lensing/pair_kde.py
  PairKDE
  make_pair_kde
  log_eval_pair_kde
  stack_pair_kdes / slice_stacked_pair_kde
  validate_pair_prior_wt

src/darksirens_lensing/pair_likelihood.py
  pair_log_likelihood
```

PairKDE remains entirely companion-owned. The pair-likelihood module imports
frozen-core cosmology and the accepted evidence/MC-variance reducer lazily at
call time, so importing `darksirens_lensing` still does not import core.

The public package root exposes the accepted L4 API. Time-delay marks, lensed
selection, singleton censoring, data contracts and partitions are not part of
this slice.

## Reference acceptance

The separate-process L0C oracle was accepted before production L4:

```text
bootstrap:         34736953526 / 103669971736  SUCCESS
committed replay:  34737008691 / 103670118958  SUCCESS
L0C freeze record: phases/11L0C_pair_reference.md
```

The frozen reference pins full-covariance apparent-frame KDE semantics,
q=1 query reflection, proposal-weight division, invalid-padding invariance,
the two image assignments, the +log(2) summed-assignment normalization, event
swap symmetry and the pair PE Monte-Carlo variance.

## Exact-core acceptance

A temporary branch-only workflow installed the exact frozen core wheel after
verifying SHA256 and installed the L4 companion from a built wheel.

Accepted phase-scoped run:

```text
head:    09e14368db01127bcf91dfc12c3f379c006ef027
run/job: 34737311809 / 103670881276
result:  SUCCESS
pytest:  3/3 L4 tests passed
```

After exposing the public L4 API, the exact-core gate was repeated on that
source head:

```text
head:    67c2119a6b81d5bd09b8f3c6f40d7d7c1777f19f
run/job: 34737351551 / 103670977249
result:  SUCCESS
pytest:  3/3 L4 tests passed
```

The temporary signed-artifact workflow was deleted before promotion.

An earlier combined L2+L4 exact-core run (`34737250787 / 103670735302`) had all
three L4 tests pass but the already-frozen L2 `a=0` bitwise equality test moved
by `1.77635684e-15` for one value on that runner. This was a cross-run floating
last-bit portability issue, not an L4 failure. The L4 acceptance workflow was
therefore scoped to L4 rather than modifying frozen L2 science.

## Clean-wheel / ownership gates

Public-API PR CI:

```text
run: 34737352604
result: SUCCESS
```

Cleanup-head CI after deleting the temporary exact-core workflow:

```text
head:    3b642e2ae5b9d3992f42aae07d6bca0ed51f92bf
run/job: 34737400428 / 103671101307
result:  SUCCESS
```

Accepted-main CI:

```text
head:    706bc4fc16aaaf2f0ec0b05b108c91499d8dde7e
run/job: 34737440985 / 103671202684
result:  SUCCESS
```

These gates build/install the wheel and preserve the ownership firewall:
`import darksirens_lensing` does not import `darksirens`, `darksirens_lss`, or
`darksirens_surveys`. L1 and L3 regressions remain green and the L4 standalone
PairKDE algebra passes from the installed wheel.

## Frozen L4 scientific contract

The accepted PairKDE uses coordinates

```text
(m1det, q, dL_app, chieff)
```

with full sample-covariance Cholesky whitening and an isotropic Silverman d=4
bandwidth in whitened space. Valid rows contribute `-log(prior_wt)` and the
normalization is by `N_valid`; invalid padded rows cannot change the density.
The physical q<=1 boundary is handled by query reflection about q=1.

The unmarked J=2 evidence uses SIS y as the one-dimensional lens coordinate.
For each assignment the driving event is the plus image, the partner is
queried through its PairKDE at the predicted minus-image apparent distance, and
the apparent-to-source Jacobian is

```text
-log(1+z_s) - log(ddL/dz) + 0.5 log(mu_driver).
```

The two image assignments are summed with `logaddexp`; they are not averaged.
The returned pair MC-variance retains the mature driving-sample delta-method
approximation and does not silently add partner-KDE sampling noise.

The exact-core L0C fixture reproduces the frozen pair likelihood, variance,
swap symmetry and bandwidth-sensitivity anchors.

## Next action

Read the current Phase-11 control ledger before beginning the next slice. Do not
infer later ownership from the old monolithic likelihood factory. Reference
oracles must precede any remaining selection/data/partition production ports.
