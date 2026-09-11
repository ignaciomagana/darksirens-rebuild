# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

Legacy is read-only throughout reconstruction.

## Current phase

```text
PHASE 6 — CORE INFERENCE / CHECKPOINTING / IO
status:         6A–6I ACCEPTED; 6J DEAD-POINT HDF5 PERSISTENCE NEXT
core repo:      ignaciomagana/darksirens-core
phase-6 base:   86e0c88a51482d17fac70f111057d277df9387fd
working branch: rebuild/phase6-inference-io
accepted 6A:    194e246666e6901624347d09ec570696f3c62e4d
accepted 6B:    6a8a2c2c4a9e772f74a913b68c13264e55bef38f
accepted 6C1:   807687ccb5754af14f888df3089497f26706e234
accepted 6D:    5edc76c6c055e47a7e041d7f7477e347837f7554
accepted 6E:    fe845dcc87787d19c69bf30a89f211d9de68be03
accepted 6F:    05e7c339f190a04e0b92d40c16119e5bda56ef08
accepted 6G:    251590e82eb373bace7f1e277805b75423bf4f10
accepted 6H:    d1d39019ad2ca3750ef8171d0d451cdc0896adb0
accepted 6I:    0084e3b7c5cba14d8ac85528ce18185941e46c05
```

Phase 6 reconstructs only portable inference infrastructure. The legacy
`inference/sampling.py` monolith is split into small backend-independent or
backend-specific adapters with an exact parity gate for each slice; it is never
copied wholesale.

### Remaining core phases

There are three core production phases remaining including the active Phase 6,
and two after Phase 6:

```text
Phase 6 — finish inference/sampler/result infrastructure and backend adapters
Phase 7 — small core extras + target public API (`model`, `infer`, loaders, angular model)
Phase 8 — extension seam + final dependency/API/install/example audit and core freeze
```

Flows remain deferred/optional unless the ordinary core path demonstrates that
they are required for the frozen core contract. Companion packages start only
after Phase 8 freezes the core surface.

## Production repository state

### `darksirens-core`

Verified `main` remains the Phase-5 squash merge:

```text
86e0c88a51482d17fac70f111057d277df9387fd
```

Accepted Phase-6 work is intentionally still on
`rebuild/phase6-inference-io`; Phase 6 is not ready to merge yet.

### Companion repositories

```text
darksirens-surveys: not started
darksirens-lss:     not started
darksirens-lensing: not started
```

## Completed production phases

### Phase 2

```text
core main after Phase 2: 450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
workflow run:            34431185197
job:                     102726848203
status:                  SUCCESS
```

### Phase 3 — population

```text
accepted head:     2461954c47df587ed70f711769a42779775be692
squash-merge SHA: e0b40fef65261a27b67aa9657a97216df3e8444f
```

Acceptance: 125 passed, 1 regeneration-only skip; population legacy/new parity
exact at `rtol=1e-12`, `atol=0`.

### Phase 4 — spectral likelihood

```text
accepted head:     cfdb138d40d66614bf9b1264c2574d0b497b812d
squash-merge SHA: 0f97feff7eb283a1f541bef9a776c9347084e70e
post-merge gate:  34447108888 / 102774202182 SUCCESS
```

Acceptance: 199 passed, 1 regeneration-only skip; spectral fixed-theta parity
exact.

### Phase 5 — catalog + dark/bright sirens

Accepted scientific checkpoints:

```text
5A catalog kernel:             f418174a7fc8734bfbcf553d5b5c36f9f4280987
5B ordinary completeness:     f4bc721496359f09fc58609fa23ccce21366f728
5C dark/complete/bright:      57af56158757ddd9272e0a2f2dc9bfbb624c1fec
5D1 generic marked hosts:     bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
5D2 magnitude-selection eval: 9d5624864ce7467d309c45125cbe5785c671e1a9
```

Final integration:

```text
PR:                 #4
PR integration head: b66221734e7564922ac1c12534abec77333923f6
squash-merge SHA:    86e0c88a51482d17fac70f111057d277df9387fd
post-merge gate:     34534097673 / 103061536070 SUCCESS
```

Phase-5 scientific parity is exact (`max_abs=max_rel=0`, `rtol=1e-12`,
`atol=0`).

## Phase 6 accepted slices

### 6A — atomic result artifact / completion protocol

```text
accepted head: 194e246666e6901624347d09ec570696f3c62e4d
```

JAX-free atomic result/completion behavior only. Exact legacy parity.

### 6B — checkpoint/resume planning

```text
accepted head: 6a8a2c2c4a9e772f74a913b68c13264e55bef38f
run/job:       34535140962 / 103064891308 SUCCESS
```

Backend-independent checkpoint-plan and resume-target resolution. Exact parity.

### 6C1 — semantic fingerprint resume gate

```text
accepted head: 807687ccb5754af14f888df3089497f26706e234
run/job:       34536066003 / 103067845905 SUCCESS
```

Semantic identity remains explicit rather than rediscovered from CLI/survey/LSS
state. Acceptance: 312 passed, 1 regeneration-only skip; exact parity.

### 6D — generic unit-cube prior transform

```text
accepted head: 5edc76c6c055e47a7e041d7f7477e347837f7554
```

Uniform, truncated-normal, truncated-lognormal, Beta(1,b), and explicit joint
cube-map behavior reconstructed without `build_parameter_space` or CLI assembly.
Separate-process parity is bit-exact.

### 6E — dynesty checkpoint state

```text
accepted head: fe845dcc87787d19c69bf30a89f211d9de68be03
```

Dynesty checkpoint/restore state kept behind lazy backend imports. Exact parity.

### 6F — dynesty prior-transform dispatch

```text
accepted head: 05e7c339f190a04e0b92d40c16119e5bda56ef08
run/job:       34551503882 / 103115199277 SUCCESS
```

Acceptance: 343 passed, 1 regeneration-only skip. Host/eager/JIT dispatch and
row-wise fallback parity exact; dynesty remains lazy.

### 6G — nested-sampler finite-logL preflight

```text
accepted head: 251590e82eb373bace7f1e277805b75423bf4f10
dedicated gate: 34555353379 / 103126770107 SUCCESS
historical gate: 34555353322 / 103126770206 SUCCESS
```

Acceptance: 8 focused tests; 351 passed, 1 regeneration-only skip overall;
preflight stdout/errors/RNG/call-count behavior exact. The probe owns
`seed ^ 0xC0FFEE`; import remains light.

### 6H — zero-free-parameter exact evidence

```text
accepted head: d1d39019ad2ca3750ef8171d0d451cdc0896adb0
dedicated gate: 34555964680 / 103128606105 SUCCESS
historical gate: 34555964712 / 103128605845 SUCCESS
```

Acceptance: 6 focused tests; 357 passed, 1 regeneration-only skip overall;
exact legacy behavior for the `dynesty`, `numpyro`, and `tinyns` method
spellings; no sampler backend imported on the zero-dimensional path. 6A–6G and
all Phase-5 parity remain exact.

### 6I — dead-point packaging

```text
accepted head: 0084e3b7c5cba14d8ac85528ce18185941e46c05
dedicated gate: 34560606167 / 103142368277 SUCCESS
historical gate: 34560606182 / 103142368473 SUCCESS
runtime guards:  34560606263 / 103142368451 SUCCESS
```

Acceptance: 5 focused tests; 362 passed, 1 regeneration-only skip overall.
Frozen `_dead_point_block` behavior is exact, candidate implementation is
NumPy-only, and all 6A–6H plus Phase-5 scientific parity remain green. Detailed
record: `phases/06I_dead_point_packaging.md`.

## Frozen architecture direction

Core owns standardized catalog runtime/IO, ordinary catalog redshift kernels and
completeness evaluation, counterpart/host objects, generic host-property
weighting, runtime evaluation of ordinary serialized catalog-selection models,
explicit spectral/dark/complete/bright hierarchical composition, and portable
inference/checkpoint/result infrastructure.

Core must not learn DESI/KIBO/Legacy/GLADE-native schemas, masks, depth-map
construction, raw magnitude preparation, selection-function fitting, staged
survey loading, LSS/Q provenance, campaign-specific CLI assembly, or companion
runtime internals.

Q_LSS, Q ensembles, latent fields/counts and multitracer machinery belong in
`darksirens-lss`. Weak/strong lensing belongs in `darksirens-lensing`.

The reconstructed source tree contains no `universe_model` dispatcher.

## Scientific questions

None opened. No scientific behavior change is authorized during reconstruction.

## Current action — Phase 6J

Reconstruct additive HDF5 persistence of the already standardized nested
sampler dead-point block: `logl_dead`, `logwt_dead`, `n_dead`, optional
`n_live`, and the explicit non-row-alignment semantics. Preserve the generic
6A atomic result protocol unchanged. Do not port `save_results_hdf5` or the
legacy sampling/result monolith wholesale.
