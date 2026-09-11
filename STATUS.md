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
PHASE 7 — SMALL CORE EXTRAS + TARGET PUBLIC API
status:       INVENTORY / SLICE DESIGN NEXT
core repo:    ignaciomagana/darksirens-core
core main:    d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
legacy ref:   c042527238bd71421b792936bc48c3b815b90d6d
```

Phase 6 is complete, merged, and closed. Detailed integration/merge record:
`phases/06_phase_integration.md`.

Phase 7 owns only the remaining small, ordinary core construction/public
surfaces: standardized ordinary loaders, small parameter/prior/model assembly,
target `model` and `infer` APIs, and the ordinary angular-model surface where it
is part of the core contract. It must not resurrect the frozen
`universe_model`/`ParameterDecoder` switchboards or absorb staged survey,
Q/LSS/multitracer, campaign, or lensing internals.

### Remaining core phases

```text
Phase 7 — small core extras + target public API (`model`, `infer`, loaders, angular model)
Phase 8 — extension seam + final dependency/API/install/example audit and core freeze
```

Companion packages start only after Phase 8 freezes the core surface.

## Production repository state

### `darksirens-core`

Phase 6 was squash-merged through PR #5. Current `main`:

```text
d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
```

Accepted Phase-6 integration head before squash:

```text
d3e8dcdbf107d881405d1f14badab7bd0ea4d74f
```

The accepted head and squash merge have the identical Git tree:

```text
118e196b87538e387d433e4f71edff70b3b3385d
```

Post-merge `main` validation that actually auto-ran:

```text
workflow: reference-integrity
run:      34592289964
job:      103240104097 (frozen-reference)
status:   SUCCESS
```

Most Phase-6/historical workflows do not push-trigger on `main`; no nonexistent
post-merge broad run is claimed. The merged tree is byte-identical to the exact
PR head on which the complete cross-phase matrix passed.

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

### Phase 6 — inference / checkpointing / IO

```text
phase base:        86e0c88a51482d17fac70f111057d277df9387fd
accepted 6A:       194e246666e6901624347d09ec570696f3c62e4d
accepted 6B:       6a8a2c2c4a9e772f74a913b68c13264e55bef38f
accepted 6C1:      807687ccb5754af14f888df3089497f26706e234
accepted 6D:       5edc76c6c055e47a7e041d7f7477e347837f7554
accepted 6E:       fe845dcc87787d19c69bf30a89f211d9de68be03
accepted 6F:       05e7c339f190a04e0b92d40c16119e5bda56ef08
accepted 6G:       251590e82eb373bace7f1e277805b75423bf4f10
accepted 6H:       d1d39019ad2ca3750ef8171d0d451cdc0896adb0
accepted 6I:       0084e3b7c5cba14d8ac85528ce18185941e46c05
accepted 6J:       0373cc9055552dc003dd569b0dc10c515c04c4fe
accepted 6K:       ffe82c8e7948bb0f7b8d0ad3d224037cd702d75d
accepted 6L:       39d9ab8aef7b0b4e0847ce4e9894a6a2a8985087
accepted 6M:       cb74900cff9be07049243548d72eef5e5e77bfaf
accepted 6N:       39d4e36a8d5d3aa347761a9134e0c7c835cdb565
accepted 6O:       28c5f06ad0cc40d8fdbb587bcaa3e98dd89089b4
accepted 6P:       73115e1d403e1c6eefa646c7e68867d6831dc7df
accepted 6Q:       cfbde4a2d202398a531dab5646314ac1a485fcd5
accepted 6R:       7bab631a786d4ad3a54bc93833157b0f64a046d4
accepted 6S:       b620601e1a0cc776f7d9090c866e299f2138fbff
accepted 6T:       d3e8dcdbf107d881405d1f14badab7bd0ea4d74f
PR:                #5
squash-merge SHA:  d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
shared tree:       118e196b87538e387d433e4f71edff70b3b3385d
```

Final 6T exact-head gates:

```text
dedicated dispatcher: 34590483237 / 103234397114 SUCCESS
historical/scientific: 34590483006 / 103234396701 SUCCESS
runtime guards:        34590482964 / 103234396617 SUCCESS
```

PR-triggered integration matrix on the exact accepted tree also passed Phase 3,
Phase 4, Phase 5, Phase 6 integration, runtime, backend-specific, and reference
checks. Representative runs:

```text
Phase 3 population:     34591719751 SUCCESS
Phase 4 spectral:       34591719734 SUCCESS
Phase 5 catalog/sirens: 34591719712 SUCCESS
Phase 6 integration:    34591719769 SUCCESS
Phase 6 runtime:        34591719782 SUCCESS
```

The final frozen/core inference-surface audit found no legitimate 6U slice.
Record: `phases/06T_sampler_orchestration.md`. Integration closure:
`phases/06_phase_integration.md`.

## Frozen architecture direction

Core owns standardized catalog runtime/IO, ordinary catalog redshift kernels and
completeness evaluation, counterpart/host objects, generic host-property
weighting, runtime evaluation of ordinary serialized catalog-selection models,
explicit spectral/dark/complete/bright hierarchical composition, portable
inference/checkpoint/result infrastructure, and a small conventional public API.

Core must not learn DESI/KIBO/Legacy/GLADE-native schemas, masks, depth-map
construction, raw magnitude preparation, selection-function fitting, staged
survey loading, LSS/Q provenance, campaign-specific CLI assembly, or companion
runtime internals.

Q_LSS, Q ensembles, latent fields/counts and multitracer machinery belong in
`darksirens-lss`. Weak/strong lensing belongs in `darksirens-lensing`.

The reconstructed source tree contains no `universe_model` dispatcher and Phase
7 must not reintroduce one under another name.

## Scientific questions

None opened. No scientific behavior change is authorized during reconstruction.

## Current action — Phase 7 inventory and first slice

Inventory the frozen ordinary user path and current core public surface before
coding. Decompose, rather than copy, the ordinary parts of legacy
`inference/data.py`, `inference/loaders.py`, `inference/prior.py`,
`inference/parameters.py`, and `inference/pop_extractor.py`, plus any angular
model/public entrypoint actually required by the frozen conventional path.

Classify each responsibility as:

1. already reconstructed core functionality;
2. a small conventional Phase-7 core facade/helper;
3. survey-native staging owned by `darksirens-surveys`;
4. Q/LSS/multitracer state owned by `darksirens-lss`;
5. lensing state owned by `darksirens-lensing`;
6. legacy campaign/CLI glue that should not be reconstructed.

Then choose the smallest conventional core-only parity slice, create a new
Phase-7 branch from `d82becaf76bf62c0f72a71b32ebbf9b238ba4f13`, and gate it against the frozen
legacy behavior before advancing further.
