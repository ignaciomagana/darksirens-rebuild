# Phase 6B checkpoint — portable checkpoint/resume planning

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

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

The private `_resume_spec` / `_UNRESOLVED` helpers may be retained as
implementation details because they are part of the frozen behavior above.

## Explicit non-scope

Do not port in 6B:

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

The dynesty state serialization/rebind seam is a later sampler-adapter subphase.

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
  artifacts using the 6A contract, and selects the checkpoint with newest mtime.
- `auto` with no eligible checkpoint starts fresh silently.
- Explicit resume may name a run directory containing the sampler checkpoint or
  an existing file; missing paths/error cases retain the frozen messages/shape.
- An explicit path may resume a directory that already has a complete result;
  the finished-run exclusion is auto-only.
- `resolve_checkpoint_plan` records JSON-able mirrors back onto `opts`:
  `checkpoint_interval_seconds`, `checkpoint_file_resolved`,
  `resume_from_resolved`.
- When callers already resolved auto-resume, passing `resume_from` must prevent a
  second filesystem lookup/race.
- `plan_from_opts` gives bare library namespaces checkpointing OFF by default.
- `CheckpointPlan.summary()` must not claim a wall-clock cadence for tinyns,
  whose actual cadence is iteration based.

## Dependency boundary

The 6B planning module may depend on Python stdlib and
`darksirens.io.results.result_is_complete`. It must not import JAX, dynesty,
numpyro, tinyns, CLI, surveys, LSS, lensing, or HEALPix at module scope.

## Acceptance

Focused tests are reconstructed from the resolution section of pinned
`tests/test_sampler_checkpoint_resume.py`, plus the truncated-result auto-resume
case pinned by `tests/test_result_atomicity_and_resume_provenance.py`.
Candidate/legacy probes must run separately and match exactly for parse results,
errors, auto selection, complete/partial result filtering, explicit paths,
resolved plans, mirrored opts state, and summaries.

No sampler backend is invoked in 6B.
