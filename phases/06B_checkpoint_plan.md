# Phase 6B checkpoint — portable checkpoint/resume planning

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
accepted 6A head:  194e246666e6901624347d09ec570696f3c62e4d
accepted 6B head:  6a8a2c2c4a9e772f74a913b68c13264e55bef38f
workflow run:      34535140962
job:               103064891308
result:            SUCCESS
```

Legacy remains read-only.

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

The exact head `6a8a2c2c4a9e772f74a913b68c13264e55bef38f` passed the
focused 6A/6B suites, the full reconstructed regression suite, the portable
light-import/dependency audit, exact separate-process 6A and 6B behavioral
parity, and the complete preserved Phase-5 numerical parity tail.

## Scope

6B reconstructs the backend-independent checkpoint/resume *decision layer* from
pinned `darksirens/inference/checkpointing.py`:

```text
CHECKPOINT_BASENAMES
DEFAULT_CHECKPOINT_INTERVAL_SECONDS
CheckpointPlan
parse_checkpoint_interval
find_resume_target
resolve_checkpoint_plan
plan_from_opts
```

The private `_resume_spec` / `_UNRESOLVED` helpers are implementation details.

## Explicit non-scope

Not ported in 6B:

```text
add_checkpoint_arguments              # CLI registration
_DetachedCallable / dynesty pickle surgery
save_dynesty_checkpoint
install_dynesty_checkpointing
restore_dynesty_sampler
rebind_dynesty_callables
tinyns backend mechanics
run_sampler
```

The dynesty state serialization/rebind seam remains a later sampler-adapter
subphase.

## Frozen semantics

- Supported checkpoint basenames are sampler-specific (`dynesty`, `tinyns`).
- Default wall-clock checkpoint interval is 1800 s.
- `off`/`none`/`no`/`false`/`disabled`/empty and numeric zero disable.
- `None` disables; boolean interval values are rejected rather than acting like
  integers; negative and malformed values are rejected.
- A trailing `s` on a numeric string is accepted.
- `--resume off` resolves to `(None, None)` even for unsupported samplers.
- Non-off resume on an unsupported sampler is an error.
- `auto` searches only the selected sampler basename below `save_path`, may be
  restricted by a run-directory `name_prefix`, skips COMPLETE final result
  artifacts using the accepted 6A contract, and selects the checkpoint with
  newest mtime.
- A truncated/incomplete `results.hdf5` does not suppress recovery.
- `auto` with no eligible checkpoint starts fresh silently.
- Explicit resume may name a run directory containing the sampler checkpoint or
  any existing checkpoint file; explicit paths are not filtered by final-result
  completion.
- `resolve_checkpoint_plan` records JSON-able mirrors back onto `opts`:
  `checkpoint_interval_seconds`, `checkpoint_file_resolved`,
  `resume_from_resolved`.
- Passing an already-resolved `resume_from`, including explicit `None`, prevents
  the second `auto` filesystem lookup/race.
- `plan_from_opts` gives bare library namespaces checkpointing OFF by default.
- `CheckpointPlan.summary()` does not invent a wall-clock cadence for tinyns;
  its actual checkpoint cadence is iteration-based.

## Dependency boundary

The 6B planning module depends only on Python stdlib and
`darksirens.io.results.result_is_complete`. It imports no JAX, dynesty, numpyro,
tinyns, CLI, surveys, LSS, lensing, or HEALPix at module scope.

## Implemented surface

```text
src/darksirens/inference/__init__.py
src/darksirens/inference/checkpointing.py
tests/test_checkpoint_plan.py
tools/probe_checkpoint_plan.py
.github/workflows/phase6-inference-io.yml
```

## Acceptance result

```text
focused Phase 6A tests:                    PASS
focused Phase 6B tests:                    PASS
full reconstructed regression suite:      PASS
portable dependency/light-import audit:   PASS
legacy/new 6A artifact behavior:          EXACT
legacy/new 6B checkpoint-plan behavior:   EXACT
preserved 5A catalog-kernel parity:       PASS
preserved 5B completeness parity:         PASS
preserved 5C likelihood parity:           PASS
preserved 5D1 marked-host parity:         PASS
preserved 5D2 selection parity:           PASS
historical numerical comparator rtol:     1e-12
historical numerical comparator atol:     0
```

The 6A/6B probes are discrete/structural and compare exact JSON behavior.

## Next

Proceed to Phase 6C1, the portable semantic fingerprint artifact/resume gate.
Do not resurrect target discovery through redshift/sky/LSS globals, flow-directory
walking, CLI state, or the old mega factory. Backend checkpoint serialization
also remains outside 6C1.
