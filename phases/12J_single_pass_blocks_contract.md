# Phase 12J — single-pass likelihood sums in the P12 chain

## Status

**ACCEPTED RUN-SETTING CHANGE (owner, 2026-09-28).** Consumer
implementation: `desi_darksirens_selection` PR #16, merged after this record
and after the Phase 12I change. No scientific content changes; the setting is a memory knob that
fixes the reduction order of the selection and PE sums.

## Trigger

The A100 benchmark campaign (Phase 12E) found that the consumer's P12.4
target ran its selection and PE sums in explicit blocks
(`sel_batch_size` 131072, `pe_event_block` 32) and that this cost about 2.5x
per call against a single pass on that device (`FINAL_REPORT.md`, 2026-09-27
close; `FINAL_ANSWERS.md` "explicit blocks" row: 1.87 to 2.16x slower warm at
4096/6 on the spectral target). The owner listed the setting as a follow-up
on 2026-09-27.

## Frozen reference

The frozen reference (`darksirens` c042527) sizes its blocks automatically
per device ("matched explicit" decision D-blocks of the campaign). Core's
public functions default to `None`, a single pass. The blocks 131072/32 were
a consumer choice made before the target was jitted (Phase 12F, PR #10);
after the jit the scan no longer re-traces per call, and the blocks only
partition the reductions.

## Measurement

2026-09-27, Hildafs CPU node r001 (28 threads, Slurm 1340541), consumer
`main` 53ed335, core `a46dec7`, frozen environment
`darksirens_benchmark_local/envs/consumer_repin_a46dec7`; the production
P12.4 target built by the consumer's own builder on the Product A pair, the
standardized catalog (before the 12I mask; the builder's fail-closed check on
the 56 pixels was turned off for the measurement only) and the footprint,
`kernel_pin: "auto"`, soft guard at cap 10. Script and result:
`logs/measure_blocks.py` and `logs/blocks_measurement_1340541.json` in
`/hildafs/projects/phy230014p/magana/desi_darksirens_selection-phase12`.

```text
setting                        build   first call   warm call (median of 5)   log L (67.74, M0hat*, sigma_M*)   log L (70, ...)        peak host RSS
blocks 131072 / 32             173 s   25.5 s       18.22 s                   -778.5717091985837                -778.4375076705919     9.0 GiB
one block each (1067946 / 259) 176 s   21.9 s       12.94 s                   -778.5717091985834                -778.4375076705908     20.7 GiB
single pass (core None / None) 173 s   20.5 s       12.98 s                   -778.5717091985834                -778.4375076705908     20.8 GiB
```

- Single pass and one block are equal at both points. Both differ from the
  blocks by 4e-16 relative (reduction order), far inside the 1e-12 parity
  criterion of Phase 12C and 12F.
- 1.40x faster per warm call on this CPU node; the campaign's 2.5x is the
  A100 figure for the same change (scan steps serialise small kernels on
  the GPU).
- The soft cap-10 diagnostics accept all three settings with no penalty.
- Working memory: about 12 GiB more than the blocks at this scale
  (cumulative peak RSS 9.0 to 20.7 GiB). This fits the Hildafs GPUs (A100
  40 and 80 GB, H100 96 GB) and not a 20 GB device such as the campaign's.

## Proposed setting

`sel_batch_size` and `pe_event_block` are `null` in the P12.2, P12.3 and
P12.4 configurations, and each stage forwards them to core as `None`
through `block_size` (defined with the target, re-exported by
`phase12.blocks`), which accepts `null` or a positive int and refuses
anything else. The consumer's target builder accepts `int | None`. Nothing
else changes: the guard, the sampler, the kernel pin, the inputs, the pins.

Consequences:

- P12.2's spectral probe values move at the 1e-16 level from the Phase 12F
  reference values, which were reproduced bitwise under the blocks in the
  12I evidence run (P12.2 pass, 2026-09-27); the 12F criterion is 1e-12.
- The chain regenerates P12.1 to P12.3 before P12.4, so the products carry
  the setting they were made with.
- A production device must have the memory for a single pass at the
  production scale; the runbook names the Hildafs GPUs that do.

## Alternatives

1. Keep the blocks. Costs 1.4x (CPU) to 2.5x (A100) per call for nothing.
2. One block each with data-sized ints. Same numbers and cost as the single
   pass, but hard-codes the data sizes in the configuration.
3. Device-sized blocks as the frozen reference does. Reintroduces a
   device-dependent reduction order.

## Acceptance gates

1. The owner accepts the setting. **Met 2026-09-28: single pass (`null`
   block sizes) in P12.2, P12.3 and P12.4.**
2. Consumer PR #16 merged (contract CI blocked by billing; local stand-ins
   recorded: CI-equivalent 260 passed, 8 skipped; frozen-environment
   target, jit, baseline, diagnostics, kernel-pin, chain, guard, sampler,
   entry-point and block tests 0 failed).
3. P12.1 to P12.3 regenerated under the setting; P12.2's calibration-point
   probe within 1e-12 of the Phase 12F reference values.
4. Promotion to an acceptance record with the merge SHA and the P12.1 to
   P12.3 record hashes.

## Verdict

**Accepted (owner, 2026-09-28).** The P12.2, P12.3 and P12.4 likelihood sums
run in a single pass. The production P12.4 device must hold the extra working
memory (the Hildafs A100 and H100 devices do; a 20 GB device does not).
