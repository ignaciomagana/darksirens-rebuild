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
status:         6A–6P ACCEPTED; 6Q NUMPYRO STATIC CONTRACT NEXT
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
accepted 6J:    0373cc9055552dc003dd569b0dc10c515c04c4fe
accepted 6K:    ffe82c8e7948bb0f7b8d0ad3d224037cd702d75d
accepted 6L:    39d9ab8aef7b0b4e0847ce4e9894a6a2a8985087
accepted 6M:    cb74900cff9be07049243548d72eef5e5e77bfaf
accepted 6N:    39d4e36a8d5d3aa347761a9134e0c7c835cdb565
accepted 6O:    28c5f06ad0cc40d8fdbb587bcaa3e98dd89089b4
accepted 6P:    73115e1d403e1c6eefa646c7e68867d6831dc7df
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

Phase count is broader than commit count: Phase 6 intentionally contains several
small parity slices before its final PR/merge. Flows remain deferred/optional
unless the ordinary core path demonstrates that they are required for the
frozen core contract. Companion packages start only after Phase 8 freezes the
core surface.

## Production repository state

### `darksirens-core`

`main` remains the Phase-5 squash merge:

```text
86e0c88a51482d17fac70f111057d277df9387fd
```

Accepted Phase-6 work remains intentionally on
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

```text
5A catalog kernel:             f418174a7fc8734bfbcf553d5b5c36f9f4280987
5B ordinary completeness:     f4bc721496359f09fc58609fa23ccce21366f728
5C dark/complete/bright:      57af56158757ddd9272e0a2f2dc9bfbb624c1fec
5D1 generic marked hosts:     bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
5D2 magnitude-selection eval: 9d5624864ce7467d309c45125cbe5785c671e1a9
PR integration head:          b66221734e7564922ac1c12534abec77333923f6
squash-merge SHA:             86e0c88a51482d17fac70f111057d277df9387fd
post-merge gate:              34534097673 / 103061536070 SUCCESS
```

Phase-5 scientific parity is exact (`max_abs=max_rel=0`, `rtol=1e-12`,
`atol=0`).

## Phase 6 accepted slices

### 6A–6J

6A atomic result publication/completion; 6B checkpoint planning; 6C1 semantic
resume fingerprint gate; 6D generic unit-cube prior transform; 6E Dynesty
state-only checkpointing; 6F Dynesty prior-transform dispatch; 6G nested
finite-logL preflight; 6H zero-free exact evidence; 6I dead-point packaging;
6J dead-point HDF5 persistence. Each slice has exact frozen-behavior parity and
its own checkpoint record under `phases/` where applicable.

### 6K — TinyNS diagnostic normalization

```text
accepted head: ffe82c8e7948bb0f7b8d0ad3d224037cd702d75d
```

Backend-independent, defensive JSON-safe diagnostic normalization. Record:
`phases/06K_tinyns_diagnostic_normalization.md`.

### 6L — TinyNS diagnostic rendering

```text
accepted head: 39d9ab8aef7b0b4e0847ce4e9894a6a2a8985087
```

Frozen stdout renderer and formatting only. Record:
`phases/06L_tinyns_diagnostic_rendering.md`.

### 6M — TinyNS configuration resolution

```text
accepted head: cb74900cff9be07049243548d72eef5e5e77bfaf
```

Presets/defaults/overrides/validation/mirroring plus sampler/run kwargs; no CLI
or backend import. Record: `phases/06M_tinyns_config_resolution.md`.

### 6N — TinyNS execution adapter

```text
accepted head:    39d4e36a8d5d3aa347761a9134e0c7c835cdb565
dedicated gate:  34570968708 / 103172778145 SUCCESS
historical gate: 34570968720 / 103172778202 SUCCESS
runtime guards:  34570968671 / 103172778199 SUCCESS
```

Lazy JAX/TinyNS execution, deterministic split run/resampling streams,
fresh/resume checkpoint routing, dead-point/diagnostic handoff, and lazy HDF5
checkpoint I/O. Record: `phases/06N_tinyns_execution_adapter.md`.

### 6O — Dynesty execution adapter

```text
accepted head:    28c5f06ad0cc40d8fdbb587bcaa3e98dd89089b4
dedicated gate:  34571461016 / 103174270237 SUCCESS
historical gate: 34571460958 / 103174269936 SUCCESS
runtime guards:  34571460969 / 103174269973 SUCCESS
```

Lazy Dynesty execution, accepted 6F transform dispatch, accepted 6B/6E
checkpoint/resume state, deterministic RNG contract, robust weighted resampling,
accepted 6I dead points, and sampler provenance. Record:
`phases/06O_dynesty_execution_adapter.md`.

### 6P — Dynesty periodic diagnostics

```text
accepted head:    73115e1d403e1c6eefa646c7e68867d6831dc7df
dedicated gate:  34578815115 / 103197379751 SUCCESS
historical gate: 34578815027 / 103197379324 SUCCESS
runtime guards:  34578815086 / 103197379648 SUCCESS
6O rerun:        34578815084 / 103197379721 SUCCESS
```

Optional 10-minute diagnostic plotting is isolated behind lazy plotting imports.
Concurrent live-result reads and plotting failures are contained, filenames and
stdout preserve frozen behavior, and daemon shutdown is guaranteed in `finally`
without changing 6O sampling semantics. Record:
`phases/06P_dynesty_periodic_diagnostics.md`.

The accepted 6P historical gate re-ran the full reconstructed suite, exact
6A–6F parity, Phase-5 legacy and reconstructed fixtures, and preserved Phase-5
scientific parity. Runtime guards and the dedicated 6O gate also reran green on
the exact accepted 6P head.

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

## Current action — Phase 6Q

Reconstruct only the static NumPyro/NUTS contract: finite ordered bounds,
NumPyro-compatible Beta bounds, joint-constraint classification and exact
warnings, midpoint initial-value seed, and NUTS option resolution/validation.
Keep initialization search/gradient preflight and actual NumPyro model/NUTS
execution for later slices.
