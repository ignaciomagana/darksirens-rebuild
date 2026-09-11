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
DARKSIRENS-CORE RECONSTRUCTION — COMPLETE / FROZEN
status:             CORE FROZEN; STOP POINT REACHED
core repo:          ignaciomagana/darksirens-core
core main:          af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
main tree:          0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
Phase-8 branch:     rebuild/phase8-core-freeze
accepted 8D head:   53bf08fd3670da4d2e48a146319c193b9cff8858
accepted 8D tree:   0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
Phase-8 PR:         #7 — 34/34 SUCCESS
post-merge gate:    34642213518 / 103404444142 SUCCESS
legacy ref:         c042527238bd71421b792936bc48c3b815b90d6d
```

Phase 8 is integrated and closed. PR #7 was squash-merged with expected-head
protection. The merged `main` tree is byte-identical to the accepted Phase-8
tree, and the only push-triggered post-merge workflow, reference-integrity,
passed in exact mode. `darksirens-core` is therefore frozen.

No further core production work remains in this reconstruction. Companion
repositories remain unstarted at this stop point.

## Production repository state

### `darksirens-core` main — final frozen state

```text
Phase-7 base/main:         6ed3dc74aa0fcde4da128036cc3d56c29250d370
accepted Phase-8 head:     53bf08fd3670da4d2e48a146319c193b9cff8858
accepted Phase-8 tree:     0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
PR:                        #7
PR historical/science:     34/34 SUCCESS
squash merge SHA:          af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
merged tree:               0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
post-merge integrity:      34642213518 / 103404444142 SUCCESS
post-merge exact result:   max_relerr=0.000e+00
record:                     phases/08_phase_integration.md
```

The accepted branch tree and squash-merged `main` tree are identical. On merged
`main`, reference-integrity validated the frozen bundle and reported
`PASS backend=cpu owner=all cells=15 mode=exact max_relerr=0.000e+00`.
No nonexistent post-merge broad run is claimed; the full broad and historical
matrices were green on the exact accepted PR head.

### Phase-7 accepted slices

```text
7A:     c338bc8eaa5199775e6d1355f20406be8ade1eb1  ACCEPTED
7B:     b97d949f32c0eff3bb48c574b5a2258f92fe82d5  ACCEPTED
7C1:    02b54e25740ff7cce1a030f372b3190121ad2b0f  ACCEPTED
7C2:    102c233f132cd3b68faaebf4f2adbe71defa731e  ACCEPTED
7C3:    7821c5d4cc6e0d7c21759b66db9fc406b9166939  ACCEPTED
7D:     1df8f78bb70371b9dae07c6a59a3c9fea2cc8e77  ACCEPTED
7E:     f8aa93ed8bd7c7ebae3fe009f5e05db92cde456e  ACCEPTED
7F1:    6f4126792be9481860f893042e1efa253b46d1ec  ACCEPTED
7F2:    877bda4e5e2e10ac52c657f7990159afcfa1093a  ACCEPTED
7F3:    be95e95bdf77144880cba5752ed5feafd40a697f  ACCEPTED
```

### Phase-8 accepted slices

```text
8A public counterpart/bright:
  head:      5256141e00a2d96a72b9cbf2182a77174c8c269e
  tree:      6252d1725ee07562840f0ce48b0dc6fe90a4aee4
  dedicated: 34634374241 / 103378585284 SUCCESS
  broad:     34634374571 / 103378586398 SUCCESS
  result:    522 passed, 1 skipped

8B InferenceTarget:
  head:      2e98ca1f1a67cf688f8da8444c3747d446a4e91d
  tree:      a893564f982aaa1174b41367927c2708148fd2b6
  dedicated: 34635288617 / 103381567625 SUCCESS
  8A replay: 34635288475 / 103381567028 SUCCESS
  broad:     34635288518 / 103381567351 SUCCESS
  result:    528 passed, 1 skipped

8C host-density extension seam:
  head:      875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2
  tree:      1219bba07d3327c83da0164602e60abe8083ba0b
  dedicated: 34636321077 / 103384995159 SUCCESS
  8B replay: 34636321027 / 103384994787 SUCCESS
  8A replay: 34636321033 / 103384994066 SUCCESS
  broad:     34636321017 / 103384994129 SUCCESS
  result:    534 passed, 1 skipped

8D packaging/API/install/examples final-freeze slice:
  head:      53bf08fd3670da4d2e48a146319c193b9cff8858
  tree:      0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
  dedicated: 34640864579 / 103399889477 SUCCESS
  8C replay: 34640864573 / 103399889300 SUCCESS
  8B replay: 34640864514 / 103399889791 SUCCESS
  8A replay: 34640864511 / 103399889303 SUCCESS
  broad:     34640864495 / 103399889097 SUCCESS
  result:    534 passed, 1 skipped
  firewall:  PASS
```

8D's dedicated clean-wheel gate proves `src/darksirens` has no diff from accepted
8C. Phase 8D therefore changes only packaging, documentation, examples and the
validation harness; it does not alter scientific/runtime implementation.

Two pre-acceptance 8D heads failed documentation assertions only:

```text
3f67c61900ae6513ad5dc23e69e7abc44d1551b9
  34640476226 / 103398636654 — harness-only docs grep
54dc2e3ad8817a7da693da57830b7e372fbb7721
  34640706728 / 103399379315 — harness-only case-sensitive docs grep
```

### Phase-8 integration

```text
PR:                    #7
PR matrix:             34/34 SUCCESS
accepted head:         53bf08fd3670da4d2e48a146319c193b9cff8858
accepted tree:         0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
squash merge:          af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
merged tree:           0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
post-merge integrity:  34642213518 / 103404444142 SUCCESS
record:                 phases/08_phase_integration.md
```

There is no further Phase-8 production slice. The accepted and merged trees are
byte-identical and the core reconstruction is closed.

### Companion repositories

```text
darksirens-surveys: not started
darksirens-lss:     not started
darksirens-lensing: not started
```

## Completed production phases

### Phase 2 — foundation

```text
core main after Phase 2: 450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
workflow:                34431185197 / 102726848203 SUCCESS
```

### Phase 3 — population

```text
accepted head:     2461954c47df587ed70f711769a42779775be692
squash-merge SHA:  e0b40fef65261a27b67aa9657a97216df3e8444f
```

Acceptance: 125 passed, 1 regeneration-only skip; population legacy/new parity
exact at `rtol=1e-12`, `atol=0`.

### Phase 4 — spectral likelihood

```text
accepted head:     cfdb138d40d66614bf9b1264c2574d0b497b812d
squash-merge SHA:  0f97feff7eb283a1f541bef9a776c9347084e70e
post-merge gate:   34447108888 / 102774202182 SUCCESS
```

Acceptance: 199 passed, 1 regeneration-only skip; spectral fixed-theta parity
exact.

### Phase 5 — catalog + dark/bright sirens

```text
5A catalog kernel:             f418174a7fc8734bfbcf553d5b5c36f9f4280987
5B ordinary completeness:      f4bc721496359f09fc58609fa23ccce21366f728
5C dark/complete/bright:       57af56158757ddd9272e0a2f2dc9bfbb624c1fec
5D1 generic marked hosts:      bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
5D2 magnitude-selection eval:  9d5624864ce7467d309c45125cbe5785c671e1a9
PR integration head:           b66221734e7564922ac1c12534abec77333923f6
squash-merge SHA:              86e0c88a51482d17fac70f111057d277df9387fd
post-merge gate:               34534097673 / 103061536070 SUCCESS
```

Phase-5 scientific parity is exact (`max_abs=max_rel=0`, `rtol=1e-12`,
`atol=0`).

### Phase 6 — inference / checkpointing / IO

```text
base:  86e0c88a51482d17fac70f111057d277df9387fd
6A:    194e246666e6901624347d09ec570696f3c62e4d
6B:    6a8a2c2c4a9e772f74a913b68c13264e55bef38f
6C1:   807687ccb5754af14f888df3089497f26706e234
6D:    5edc76c6c055e47a7e041d7f7477e347837f7554
6E:    fe845dcc87787d19c69bf30a89f211d9de68be03
6F:    05e7c339f190a04e0b92d40c16119e5bda56ef08
6G:    251590e82eb373bace7f1e277805b75423bf4f10
6H:    d1d39019ad2ca3750ef8171d0d451cdc0896adb0
6I:    0084e3b7c5cba14d8ac85528ce18185941e46c05
6J:    0373cc9055552dc003dd569b0dc10c515c04c4fe
6K:    ffe82c8e7948bb0f7b8d0ad3d224037cd702d75d
6L:    39d9ab8aef7b0b4e0847ce4e9894a6a2a8985087
6M:    cb74900cff9be07049243548d72eef5e5e77bfaf
6N:    39d4e36a8d5d3aa347761a9134e0c7c835cdb565
6O:    28c5f06ad0cc40d8fdbb587bcaa3e98dd89089b4
6P:    73115e1d403e1c6eefa646c7e68867d6831dc7df
6Q:    cfbde4a2d202398a531dab5646314ac1a485fcd5
6R:    7bab631a786d4ad3a54bc93833157b0f64a046d4
6S:    b620601e1a0cc776f7d9090c866e299f2138fbff
6T:    d3e8dcdbf107d881405d1f14badab7bd0ea4d74f
PR:    #5
merge: d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
```

Final 6T exact-head gates:

```text
dedicated dispatcher: 34590483237 / 103234397114 SUCCESS
historical/scientific: 34590483006 / 103234396701 SUCCESS
runtime guards:        34590482964 / 103234396617 SUCCESS
```

Detailed records: `phases/06T_sampler_orchestration.md` and
`phases/06_phase_integration.md`.

## Phase 7 — public/core construction surface

### 7A — standardized public loaders

```text
head:        c338bc8eaa5199775e6d1355f20406be8ade1eb1
dedicated:   34593088782 / 103242605896 SUCCESS
broad:       34593088762 / 103242605373 SUCCESS
record:      phases/07A_public_loaders.md
```

### 7B — public cosmology/population specifications

```text
head:        b97d949f32c0eff3bb48c574b5a2258f92fe82d5
dedicated:   34595489924 / 103250164326 SUCCESS
7A replay:   34595489912 / 103250164428 SUCCESS
broad:       34595489857 / 103250163890 SUCCESS
record:      phases/07B_public_specs.md
```

### 7C1 — joint-prior resolver

```text
head:        02b54e25740ff7cce1a030f372b3190121ad2b0f
dedicated:   34596093457 / 103252070961 SUCCESS
broad:       34596093340 / 103252070365 SUCCESS
record:      phases/07C1_joint_prior_resolver.md
```

### 7C2 — public `model()` / parameter plan

```text
head:        102c233f132cd3b68faaebf4f2adbe71defa731e
dedicated:   34596633396 / 103253806465 SUCCESS
broad:       34596632992 / 103253805105 SUCCESS
record:      phases/07C2_public_model_plan.md
```

### 7C3 — portable HEALPix RING geometry

```text
head:        7821c5d4cc6e0d7c21759b66db9fc406b9166939
dedicated:   34599757756 / 103263901736 SUCCESS
broad:       34599757799 / 103263901914 SUCCESS
record:      phases/07C3_healpix_geometry.md
```

### 7D — ordinary runtime binding

```text
head:        1df8f78bb70371b9dae07c6a59a3c9fea2cc8e77
tree:        58e005450715e59456e3778b1431b909d6bb7636
dedicated:   34622477272 / 103339542168 SUCCESS
broad:       34622477307 / 103339541969 SUCCESS
result:      499 passed, 1 skipped
record:      phases/07D_runtime_binding.md
```

### 7E — thin public `ds.infer()`

```text
head:        f8aa93ed8bd7c7ebae3fe009f5e05db92cde456e
dedicated:   34623252701 / 103342078953 SUCCESS
broad:       34623252604 / 103342078653 SUCCESS
result:      502 passed, 1 skipped
record:      phases/07E_public_infer.md
```

### 7F1 — basic angular source-population models

```text
head:        6f4126792be9481860f893042e1efa253b46d1ec
dedicated:   34624190605 / 103345183970 SUCCESS
broad:       34624190465 / 103345183648 SUCCESS
result:      506 passed, 1 skipped
record:      phases/07F1_angular_basic.md
```

### 7F2 — advanced angular source-population models

```text
head:        877bda4e5e2e10ac52c657f7990159afcfa1093a
tree:        9188244eea1f71bf3fbbb6f9e1e7162151e6df77
dedicated:   34625983191 / 103351075167 SUCCESS
broad:       34625983125 / 103351074718 SUCCESS
result:      511 passed, 1 skipped
record:      phases/07F2_angular_advanced.md
```

### 7F3 — angular composition and likelihood wiring

```text
head:        be95e95bdf77144880cba5752ed5feafd40a697f
tree:        55dfb24cb84edebb0175409bd33be2a6a57ecb8a
dedicated:   34632081722 / 103371081194 SUCCESS
broad:       34632081763 / 103371080968 SUCCESS
result:      517 passed, 1 skipped
record:      phases/07F3_angular_wiring.md
```

### Phase-7 integration

```text
PR:                       #6
PR matrix:                30/30 SUCCESS
accepted head:            be95e95bdf77144880cba5752ed5feafd40a697f
accepted tree:            55dfb24cb84edebb0175409bd33be2a6a57ecb8a
squash merge:             6ed3dc74aa0fcde4da128036cc3d56c29250d370
merged tree:              55dfb24cb84edebb0175409bd33be2a6a57ecb8a
post-merge integrity:     34633321021 / 103375170965 SUCCESS
record:                    phases/07_phase_integration.md
```

There is no Phase 7G. The accepted and merged trees are byte-identical.

## Frozen architecture direction

Core owns standardized catalog runtime/IO, ordinary catalog redshift kernels and
completeness evaluation, counterpart/host objects, generic host-property
weighting, runtime evaluation of ordinary serialized catalog-selection models,
explicit spectral/dark/complete/bright hierarchical composition, portable
inference/checkpoint/result infrastructure, reusable angular population models,
and a small conventional public API.

Phase 8 additionally freezes:

- public counterpart/bright composition;
- `InferenceTarget` as the sampler-facing specialized-analysis seam;
- the explicit `RedshiftModel`/host-density extension seam;
- the package-root API and dependency/install contract;
- public ordinary/custom-target examples.

Core must not learn DESI/KIBO/Legacy/GLADE-native schemas, masks, depth-map
construction, raw magnitude preparation, selection-function fitting, staged
survey loading, LSS/Q provenance, campaign-specific CLI assembly, or companion
runtime internals.

Q_LSS, Q ensembles, latent fields/counts and multitracer machinery belong in
`darksirens-lss`. Weak/strong lensing belongs in `darksirens-lensing`.

No generic plugin framework. Extensions enter through small explicit interfaces.
Core must import no companion package.

## Scientific questions

None opened. No scientific behavior change was authorized during Phase 8. The
accepted 8D clean-wheel gate verifies that scientific source is unchanged from
accepted 8C.

## Final state

`darksirens-core` reconstruction is complete and frozen at:

```text
main SHA:  af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
tree:      0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
```

Stop here. Do not start `darksirens-surveys`, `darksirens-lss`, or
`darksirens-lensing` as part of this closeout.