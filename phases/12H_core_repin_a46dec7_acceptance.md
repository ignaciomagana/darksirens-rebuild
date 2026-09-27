# Phase 12H — core repin to a46dec7: acceptance

## Status

**PROPOSED ACCEPTANCE — owner sign-off pending. Consumer contract CI waived
by the owner; P12.1 passed under the pin; P12.2 to P12.4 not yet run.**

There is no separate 12H contract record: the change was prepared on the
owner's decision of 2026-09-27 (prepare the core repin that the Phase 12F and
12G acceptance path needs) and is described in the consumer's runbook
(`PHASE12_RUNBOOK.md`, "Phase 12H (proposed): core repin to a46dec7") and its
acceptance marker (`config/phase12b.accepted.json`, `core_acceptance`).

## The pin

```text
darksirens-core  a46dec7929c7343fef61e68b7c0c5f2c205daa0e   tree 6cfb71989f6eae112d5880801912fd386220af32
supersedes       8bf2bec53ff7b557c6b930d4044008cb72008f61   (Phase 12C; tree 18b3bf93)
push gates on a46dec7:  reference-integrity 36336267952, real-backends 36336267935,
                        phase8d-release-contract 36336267895 — all SUCCESS
```

What `a46dec7` adds over `8bf2bec5`, in merge order (core `main` after each):

```text
#17-#23  Phase 12D deferred follow-up            c3bc005b (tree ad4ab934)   2026-09-23
#24      real-backends pipefail (CI only)        88004d96 (tree 00e4b9e5)   2026-09-24
#25      bound analysis jitted once at bind      43d273f9 (tree bda0d733)   2026-09-25
#27      partial fixing of population/survey     d03d0cb  (tree 306cc361)   2026-09-26
#29      dynesty dlogz_final and stop_reason     e412e92  (tree dfae177e)   2026-09-27
#28      catalog kernel pin with catalog digest  a857dc4  (tree 4624a847)   2026-09-27
#30      field-seam kernel pin                   a46dec7  (tree 6cfb7198)   2026-09-27
```

Core's declared dependencies are identical at `8bf2bec5` and `a46dec7`
(jax and jaxlib 0.4.34, numpy 1.26.4, tinyns 3f9e1b2, the `dynesty` extra
`dynesty==2.1.4`). The surveys, LSS and lensing pins are unchanged.

## Adoption by the consumer

Consumer PR #14 (head `ffd9fda4`, rebased as `5e4bc21` with the same tree)
squash-merged on 2026-09-27 as `main` `e72c24a`, after #11 (12F) and #12
(12G) and before #13; `main` is `53ed335` with the runbook merge note. The
`phase12-contract` workflow did not run on any of them: the repository stays
private by the owner's decision and Actions is blocked by billing (runs
36340462060 and 36342377696 ended with zero steps). Stand-ins on `main`
`52389c6`: CI-equivalent 250 passed, 7 skipped; frozen `a46dec7` environment
281 passed, none skipped (full detail in
`phases/12F_selection_guard_and_gwcat_products_acceptance.md`, gate 1).

The consumer pins `a46dec7` in `requirements-frozen.txt`,
`config/frozen_packages.json` and the marker (`core_commit`, `core_tree`,
`core_post_merge_workflow` 36336267952, `core_acceptance` 12H,
`superseded_core_pins` 12B and 12C). Under it the P12.4 target's
`kernel_pin: "auto"` is served and the gate 7 convergence assertion is active.

## Evidence under the pin on the production path

P12.1 passed on 2026-09-27 (Hildafs Slurm 1340521, production checkout
`/hildafs/projects/phy230014p/magana/desi_darksirens_selection-phase12`,
frozen environment `darksirens_benchmark_local/envs/consumer_repin_a46dec7`,
CPython 3.11.10): `provenance/bootstrap_environment.json` reports status ok
for darksirens at `a46dec7`, darksirens-surveys at `f027aef0`, darksirens-lss
at `3429bb2f`, darksirens-lensing at `43c45074`, and dynesty 2.1.4. The next
stage failed closed on the footprint rule (12F record, gate 4); it is
independent of the pin.

## What this record still lacks

- the owner's sign-off;
- a green `phase12-contract` run on the consumer's merged `main` (billing);
- P12.2, P12.2b and P12.3 regenerated under the pin, which waits on the
  footprint contract decision;
- the control fields of the consumer's marker (`control_repository`,
  `control_commit`, `control_record`), to be filled with this record's merge
  once it is accepted.

## Verdict

**Proposed for acceptance.** Accepting it makes `a46dec7` the active
production core pin, accepts Phase 12D with it, and leaves Phase 12F's own
gates (products, regenerated P12.1 to P12.3, the fixed-coordinate check) to
the 12F acceptance record.
