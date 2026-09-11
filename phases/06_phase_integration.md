# Phase 6 — integration, merge, and closure

Status: **COMPLETE / MERGED**

```text
legacy reference:    c042527238bd71421b792936bc48c3b815b90d6d
Phase-5 main base:   86e0c88a51482d17fac70f111057d277df9387fd
accepted Phase-6:   d3e8dcdbf107d881405d1f14badab7bd0ea4d74f
PR:                 ignaciomagana/darksirens-core#5
squash-merge SHA:   d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
accepted/main tree: 118e196b87538e387d433e4f71edff70b3b3385d
```

## Integration audit

Before opening the integration PR, the accepted Phase-6 branch was compared to
the Phase-5 `main` base. It was 53 commits ahead and 0 behind. The changed files
were confined to Phase-6 inference/IO implementation, focused tests/probes, and
Phase-6 workflows.

The audit found:

- no `pyproject.toml` dependency changes;
- no catalog, population, or likelihood-science edits;
- no accidental Phase-7 public API/model-construction modules;
- no production imports of `darksirens-surveys`, `darksirens-lss`, or
  `darksirens-lensing`;
- no DESI/KIBO/Legacy/GLADE survey-native construction leakage;
- no `Q_LSS`/multitracer/lensing-specific state in core;
- companion-package names in the PR diff only where guard code explicitly
  forbids those imports.

The final frozen/core inference-surface audit is recorded in
`06T_sampler_orchestration.md`. It found no legitimate Phase 6U functional
slice: portable sampler, checkpoint, result, provenance, and backend-adapter
work was complete at 6T.

## PR integration gate

PR #5 was opened from `rebuild/phase6-inference-io` at the exact accepted head
`d3e8dcdbf107d881405d1f14badab7bd0ea4d74f` onto the unchanged Phase-5 `main`.
The branch was held fixed while the PR-triggered matrix ran.

Every PR-triggered workflow on that exact head completed **SUCCESS**, including:

- Phase 3 population regression/parity;
- Phase 4 spectral regression/parity;
- Phase 5 catalog/completeness/dark/bright/marked-host regression/parity;
- Phase 6 full integration/historical/scientific replay;
- Phase 6 runtime guards;
- all backend/slice-specific Phase-6 gates;
- repository reference-integrity checks.

Representative integration runs on the exact PR head:

```text
Phase 3 population:           34591719751  SUCCESS
Phase 4 spectral:             34591719734  SUCCESS
Phase 5 catalog/sirens:       34591719712  SUCCESS
Phase 6 integration:          34591719769  SUCCESS
Phase 6 runtime guards:       34591719782  SUCCESS
```

The Phase-6 integration run passed the full reconstructed suite, portable
inference dependency checks, exact 6A–6F frozen replay, pinned/reconstructed
Phase-5 fixture generation, and exact preserved Phase-5 scientific parity.

## Merge

PR #5 was squash-merged with expected-head protection requiring
`d3e8dcdbf107d881405d1f14badab7bd0ea4d74f`. The new `main` commit is:

```text
d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
```

Raw Git commit metadata verifies both the accepted PR head and squash-merge
commit point to the **same tree**:

```text
118e196b87538e387d433e4f71edff70b3b3385d
```

Therefore the code bytes on merged `main` are exactly the code bytes exercised
by the fully green PR matrix; only commit history was squashed.

## Post-merge validation

Only the repository's `reference-integrity` workflow is configured to run on the
`main` push for this merge. On the exact squash-merge SHA it ran and passed:

```text
workflow: reference-integrity
run:      34592289964
job:      103240104097  (frozen-reference)
status:   SUCCESS
```

That job successfully validated the frozen legacy bundle and self-tested the
comparator against the CPU reference.

Most Phase-6/backend/historical workflows are branch/pull-request/manual
workflows and do **not** automatically push-trigger on `main`. Consequently this
record does not claim a nonexistent second broad post-merge run. Scientific and
behavioral post-merge equivalence is instead established by the exact shared
Git tree above plus the fully green PR-triggered cross-phase matrix on that tree,
with the `main` push reference-integrity run as an independent merged-commit
check.

## Closure

Phase 6 is complete and merged. `darksirens-core/main` is now
`d82becaf76bf62c0f72a71b32ebbf9b238ba4f13`.

The next production phase is **Phase 7 — small core extras and target public
API**. Phase 7 must decompose the remaining frozen construction/public surfaces
rather than resurrecting the legacy switchboards. Ordinary standardized loaders,
small parameter/prior/model assembly, `model`, `infer`, and the ordinary angular
model are core candidates; survey-native staging, Q/LSS/multitracer machinery,
and lensing-specific internals remain outside core.
