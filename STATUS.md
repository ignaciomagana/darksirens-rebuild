# Reconstruction status

## Reference

Legacy repository:

```text
ignaciomagana/darksirens
```

Pinned reference SHA:

```text
c042527238bd71421b792936bc48c3b815b90d6d
```

## Current phase

```text
PHASE 0 — INVENTORY AND DEPENDENCY MAP
status: IN PROGRESS
```

## Durable control repo

```text
ignaciomagana/darksirens-rebuild
```

The control repository has been initialized with the reconstruction architecture and frozen decisions. Production code will live only in the four target repositories.

## Target repositories

```text
ignaciomagana/darksirens-core
ignaciomagana/darksirens-surveys
ignaciomagana/darksirens-lss
ignaciomagana/darksirens-lensing
```

## Completed

- Architecture split agreed.
- Legacy repository designated read-only numerical reference.
- Legacy numerical target pinned to `c042527238bd71421b792936bc48c3b815b90d6d`.
- GP population models assigned to core.
- LSS assigned to first-class companion package.
- Weak/strong lensing assigned to first-class companion package.
- Survey construction assigned to first-class companion package.
- User-facing API chosen as the organizing principle.
- `darksirens-rebuild` control repository created and initialized.

## Tests

No new-package parity suite has been run yet.

## Numerical parity

Not established yet. Phase 1 will freeze reference fixtures before mathematical code is ported.

## Production repository changes

None yet.

## Legacy behavior deliberately not migrated

No final file-level decisions yet. Phase 0 will classify legacy files as `CORE`, `SURVEYS`, `LSS`, `LENSING`, `LEGACY_ONLY`, or `FUTURE_REVIEW`.

## Architecture questions

- Exact minimal extension protocol for LSS auxiliary count/field likelihood will be fixed after inventory of current call graph.
- Exact analysis interface for strong-lensing cluster likelihood will be fixed after inventory of current likelihood/inference coupling.
- Flow-surrogate migration is deliberately deferred until the ordinary core sample path is stable.

## Scientific questions

None opened. Any apparent legacy scientific bug found during migration will be recorded rather than silently fixed.

## Next action

Complete Phase 0: full legacy module/test/script inventory, cross-boundary dependency map, and concrete migration contracts for all four target repositories.
