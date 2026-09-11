# Phase 6C1 checkpoint — semantic fingerprint artifact and resume gate

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
phase-6 base:      86e0c88a51482d17fac70f111057d277df9387fd
working branch:    rebuild/phase6-inference-io
```

Legacy remains read-only.

## Why split the legacy module

Pinned `darksirens/inference/run_fingerprint.py` contains two different jobs:

1. a portable, safety-critical artifact/gating protocol for a fingerprint that
   has already been built;
2. discovery of the statistical target from the old monolithic runtime
   (redshift grid globals, population normalisation globals, sky-model globals,
   flow-surrogate directory walking, CLI option namespaces and code identity).

Only (1) is 6C1. Recreating (2) implicitly would reintroduce exactly the hidden
cross-package coupling the rebuild is removing.

## 6C1 core scope

Reconstruct the portable behavior of:

```text
FINGERPRINT_BASENAME
FINGERPRINT_BASENAME_STEM
FINGERPRINT_SCHEMA_VERSION = 3
ResumeFingerprintError
save_run_fingerprint
check_resume_fingerprint
gate_and_stamp_resume_fingerprint
resume_provenance_attrs
_semantic_diff                 # private implementation detail
_warn_code_identity_drift      # private advisory behavior
```

Core additionally exposes a tiny canonical constructor for a caller-supplied
`semantic` mapping:

```text
fingerprint_from_semantic(semantic, *, advisory=None)
```

Its digest is exactly SHA-256 of
`json.dumps(semantic, sort_keys=True, separators=(",", ":"), default=str)`.
This helper does not discover model state.

## Frozen behavior

- `run_fingerprint.json` is written atomically in the run directory using a
  same-directory temporary followed by `os.replace`.
- Any `BaseException` removes the temporary and does not publish a partial
  fingerprint.
- Missing or unreadable fingerprint fails closed unless `force=True`.
- Schema mismatch fails closed even when the semantic block happens to look
  equal; the error names `schema_version`.
- Equal digest is accepted. Advisory code-identity drift may warn but cannot
  reject a resume.
- Digest mismatch produces a human-readable semantic diff (up to the frozen
  display limit) and fails closed unless forced.
- `force=True` warns loudly and returns the stored fingerprint on a genuine
  mismatch; missing/unreadable forced legacy state returns `None`.
- `gate_and_stamp_resume_fingerprint` stamps the current digest onto opts only
  after the fingerprint is already constructed, so provenance cannot feed back
  into the digest.
- Fresh run: write `run_fingerprint.json`.
- Forced resume of a pre-fingerprint directory: write the current canonical
  fingerprint so later requeues can validate normally.
- Forced genuine mismatch: preserve the original fingerprint and write the
  current fingerprint beside it as
  `run_fingerprint.forced-<timestamp>.json`; stamp
  `resume_forced_mismatch=True`.
- Result provenance records current digest, whether the run resumed, the source
  checkpoint, whether force was requested, and whether force crossed a genuine
  mismatch.

## Explicit non-scope

6C1 must not import or discover:

```text
darksirens.redshift
darksirens.sky
darksirens.gw population normalisation globals
flow-surrogate directories
survey/LSS/lensing artifacts
CLI parsers/options beyond consuming a generic attribute namespace
sampler backends
JAX
```

`code_identity` is optional advisory input; it is not discovered by importing
CLI/settings machinery in this slice.

## Acceptance

Accepted at exact core head:

```text
807687ccb5754af14f888df3089497f26706e234
```

Workflow:

```text
run:    34536066003
job:    103067845905
result: SUCCESS
```

Acceptance results:

```text
6A result-artifact tests:       10 passed
6B checkpoint-plan tests:       36 passed
6C1 fingerprint-gate tests:     15 passed
full reconstructed suite:       312 passed, 1 regeneration-only skip
portable dependency audit:      PASS
6A separate-process parity:     exact
6B separate-process parity:     exact
6C1 separate-process parity:    exact
preserved Phase-5 parity:       exact, max_abs=max_rel=0 at rtol=1e-12, atol=0
```

The first 6C1 workflow attempt stopped before testing on one unused import in the
new parity probe. That lint-only defect was removed; no production or behavioral
code changed. The corrected exact head above then passed the complete gate.

The separate-process fingerprint fixture verified fresh atomic save/load,
BaseException rollback, missing/corrupt fail-closed behavior, force behavior,
schema mismatch, digest match, semantic mismatch and human-readable diff,
forced mismatch preservation plus sibling stamping, provenance attrs, and
advisory code-identity drift.

No target-specific semantic builder is accepted in 6C1.

## Next

Proceed to the generic unit-cube prior transform as the next small Phase-6 slice.
Port only the backend-independent transform and explicit joint cube maps from the
pinned legacy prior implementation. Do not port `build_parameter_space`, survey
registries, sky/LSS discovery, CLI configuration, or model lookup into this
slice. Nested-sampler dispatch and backend runners remain later subphases.
