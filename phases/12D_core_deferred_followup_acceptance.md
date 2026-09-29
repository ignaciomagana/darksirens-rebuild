# Phase 12D — core deferred follow-up: acceptance

## Status

**ACCEPTED 2026-09-28 through Phase 12H (owner sign-off). Contract CI on the
consumer was waived by the owner (see Phase 12H).**

Contract: `phases/12D_core_deferred_followup_contract.md` (merged as a
proposed record, 733a11b, 2026-09-24). Its pin decision named three
conditions. This record shows the first two met on core and the third met by
the Phase 12H repin, and lists what the owner still has to decide.

## Condition 1: ordered merges, SHAs and trees recorded

Seven stacked PRs squash-merged to core `main` in order on 2026-09-23, tree
identity checked after each; then the CI fix:

```text
#17 .. #23  merged 2026-09-23 17:52-17:54 UTC
            core main c3bc005b41be7f24e2baa202bafa717f2237f1b3  tree ad4ab934
#24         pipefail in the real-backends step (closes the record's first
            "left open" item), merged 2026-09-24
            core main 88004d96ddeee37c47abc1d2dfd1c6fc3c203dfd  tree 00e4b9e5
```

## Condition 2: push-triggered gates green on the merged heads

```text
c3bc005b  reference-integrity 35898821948  real-backends 35898822004  phase8d-release-contract 35898822026  all SUCCESS
88004d96  reference-integrity 35954407573  real-backends 35954407608  phase8d-release-contract 35954407601  all SUCCESS
```

## Condition 3: a new core pin that contains the change

The pin the consumer adopted is not `88004d96` but the later core `main`
`a46dec7929c7343fef61e68b7c0c5f2c205daa0e` (tree
`6cfb71989f6eae112d5880801912fd386220af32`), which contains #17 through #24
and, on top of them, #25, #27, #29, #28 and #30. That pin, its gates and its
adoption are the subject of `phases/12H_core_repin_a46dec7_acceptance.md`.
Accepting 12H accepts 12D with it; 12D is not accepted separately.

## Left-open items of the contract, as of 2026-09-27

- `real-backends` piped pytest into `tee` without `pipefail`: closed by #24.
- `real-backends` as a required check: set on 2026-09-27 as branch protection
  on core `main` (required status check `backends`, linear history required,
  force pushes and deletions refused, no review requirement).
- The other items (frozen API names only, the unported package-directory
  check, the fingerprint corner cases, the sampler-dispatch stub, the
  `z_depth` treatment in `selection_budget_audit`) stay open by design and
  are unchanged.

## Owner sign-off

The owner signed off on 2026-09-28 by accepting Phase 12H. Nothing is owed on
the core side.

## Verdict

**Accepted through Phase 12H (owner, 2026-09-28).** No numerics of the fixed
parametric DESI population target are touched by 12D; the one numerics change
(the GP mass-ratio normaliser near the minimum mass) concerns GP models only.
