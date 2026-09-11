# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 6 — CORE INFERENCE / CHECKPOINTING / IO
status:         6A–6C1 ACCEPTED; GENERIC PRIOR TRANSFORM NEXT
core repo:      ignaciomagana/darksirens-core
phase-6 base:   86e0c88a51482d17fac70f111057d277df9387fd
working branch: rebuild/phase6-inference-io
```

Phase 5 is closed. Phase 6 reconstructs only portable inference infrastructure:
composable parameter/prior decoding, sampler-facing contracts, semantic
checkpoint/resume state, run fingerprints, and JAX-free settings/results IO.
Survey/LSS staging, raw catalog construction, `q_provenance`, campaign/CLI
assembly, and the legacy mega factory are not Phase-6 migration units.

## Completed phase heads

### Phase 2

```text
core main after Phase 2: 450b9bdb66d2dc2d6e7f927143f9b4b4b9f9cec6
workflow run:            34431185197
job:                     102726848203
status:                  SUCCESS
```

### Phase 3

```text
accepted branch head: 2461954c47df587ed70f711769a42779775be692
final phase3 run:     34437645424
phase3 job:           102745952311
squash-merge SHA:     e0b40fef65261a27b67aa9657a97216df3e8444f
core main:            e0b40fef65261a27b67aa9657a97216df3e8444f
```

Scientific acceptance: 125 passed, 1 regen-only skip; population legacy/new
parity `max_abs=max_rel=0` at `rtol=1e-12`, `atol=0`; optional-dependency gate
PASS. Detailed record: `phases/03_population.md`.

### Phase 4

```text
accepted branch head: cfdb138d40d66614bf9b1264c2574d0b497b812d
branch workflow run: 34445525661
phase3 job:           102769369532
squash-merge SHA:     0f97feff7eb283a1f541bef9a776c9347084e70e
verified core main:   0f97feff7eb283a1f541bef9a776c9347084e70e
post-merge run/job:   34447108888 / 102774202182 SUCCESS
```

Scientific acceptance: 199 passed, 1 regen-only skip; spectral fixed-theta
legacy/new parity exact (`max_abs=max_rel=0`, `rtol=1e-12`, `atol=0`). Detailed
record: `phases/04_spectral_likelihood.md`.

### Phase 5A — catalog runtime + observed redshift kernel

```text
accepted head:   f418174a7fc8734bfbcf553d5b5c36f9f4280987
workflow run:    34456764290
job:             102804866600
workflow result: SUCCESS
```

The strict probe caught a real numerical-semantic difference in remote Gaussian
tails; reconstructed code now reproduces frozen legacy's one-pass linear-domain
underflow behavior. After the later 5B operation-order correction, the 5A probe
is exactly equal to legacy (`max_abs=max_rel=0`). Detailed checkpoint:
`phases/05A_catalog_kernel.md`.

### Phase 5B — ordinary completeness + depth

```text
accepted head:   f4bc721496359f09fc58609fa23ccce21366f728
workflow run:    34461981743
job:             102821696680
workflow result: SUCCESS
```

Scientific acceptance: 226 passed, 1 regeneration-only skip; 5A and 5B
separate-process parity exact at `rtol=1e-12`, `atol=0`. Detailed checkpoint:
`phases/05B_catalog_completeness.md`.

### Phase 5C — explicit ordinary dark/complete/bright composition

```text
accepted head:   57af56158757ddd9272e0a2f2dc9bfbb624c1fec
workflow run:    34465661255
job:             102833519200
workflow result: SUCCESS
```

Scientific acceptance: 235 passed, 1 regeneration-only skip; full ordinary
likelihood parity exact. Detailed checkpoint: `phases/05C_catalog_dark_bright.md`.

### Phase 5D1 — generic marked-host runtime

```text
accepted head:   bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
workflow run:    34498152895
job:             102941812699
workflow result: SUCCESS
```

Scientific acceptance: 242 passed, 1 regeneration-only skip; marked-host parity
exact. Detailed checkpoint: `phases/05D1_catalog_marks.md`.

### Phase 5D2 — generic magnitude-selection runtime

```text
accepted scientific head: 9d5624864ce7467d309c45125cbe5785c671e1a9
workflow run:             34531001625
job:                      103051412901
workflow result:          SUCCESS
```

Scientific acceptance: 251 passed, 1 regeneration-only skip; 5A through 5D2
separate-process parity all exact (`max_abs=max_rel=0`, `rtol=1e-12`, `atol=0`).
Strict parity first caught the finite-depth raw-`C` state mismatch and then a
new inner JIT boundary that perturbed Gaussian/Schechter tails. Both were fixed
without changing equations or widening the comparator. Detailed checkpoint:
`phases/05D2_catalog_selection.md`.

### Phase 5 — final integration

```text
scientific head:        9d5624864ce7467d309c45125cbe5785c671e1a9
PR integration head:    b66221734e7564922ac1c12534abec77333923f6
PR:                     #4
PR exact-head gates:    ALL SUCCESS
squash-merge SHA:       86e0c88a51482d17fac70f111057d277df9387fd
verified core main:     86e0c88a51482d17fac70f111057d277df9387fd
post-merge run/job:     34534097673 / 103061536070 SUCCESS
```

The only change between the accepted scientific head and PR integration head was
CI-only: the historical Phase-4 dependency audit originally prohibited any
`darksirens.catalog` import anywhere below `likelihood/selection`, which became
obsolete once catalog became a first-class core namespace in Phase 5. The rule
was narrowed to preserve the actual boundary against legacy-redshift/LSS/lensing/
CLI imports. No production/scientific source changed, and all historical plus
Phase-5 PR workflows passed before merge.

### Phase 6A — atomic result artifact/completion protocol

```text
accepted head: 194e246666e6901624347d09ec570696f3c62e4d
status:        SUCCESS
```

6A reconstructs only the JAX-free atomic result/completion contract used by
resume logic. It does not port the full legacy results writer or CLI metadata.
Focused behavior and separate-process legacy parity are exact.

### Phase 6B — checkpoint/resume planning

```text
accepted head: 6a8a2c2c4a9e772f74a913b68c13264e55bef38f
workflow run:  34535140962
job:           103064891308
result:        SUCCESS
```

6B reconstructs only backend-independent checkpoint-plan resolution and
resume-target selection. Sampler serialization remains separate. Exact 6A/6B
parity and all preserved Phase-5 parity passed.

### Phase 6C1 — semantic fingerprint artifact/resume gate

```text
accepted head: 807687ccb5754af14f888df3089497f26706e234
workflow run:  34536066003
job:           103067845905
result:        SUCCESS
```

Acceptance: 312 passed, 1 regeneration-only skip; the portable dependency audit
passed; 6A, 6B and 6C1 separate-process behavior matched frozen legacy exactly;
all Phase-5 comparators remained exact (`max_abs=max_rel=0`, `rtol=1e-12`,
`atol=0`). 6C1 keeps semantic identity explicit and does not rediscover the
statistical target from CLI/survey/LSS/sky globals. Detailed checkpoint:
`phases/06C1_run_fingerprint_gate.md`.

## Production repository state

### `darksirens-core`

`main` is still the verified Phase-5 squash merge:

```text
86e0c88a51482d17fac70f111057d277df9387fd
```

Accepted Phase-6 work lives on:

```text
rebuild/phase6-inference-io
latest accepted checkpoint: 807687ccb5754af14f888df3089497f26706e234
```

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Frozen architecture direction

Core owns standardized catalog runtime/IO, ordinary catalog redshift kernels and
completeness evaluation, counterpart/host objects, generic host-property
weighting, runtime evaluation of ordinary serialized catalog-selection models,
explicit spectral/dark/complete/bright hierarchical composition, and portable
inference/checkpoint/result infrastructure.

Core must not learn DESI/KIBO/Legacy/GLADE-native schemas, masks, depth-map
construction, raw magnitude preparation, selection-function fitting, staged
survey loading, LSS/Q provenance, or campaign-specific CLI assembly; those
remain outside core.

Q_LSS, Q ensembles, latent fields/counts, multitracer machinery, and any
normalization intrinsically requiring those field quantities belong in
`darksirens-lss`. Weak/strong lensing belongs in `darksirens-lensing`.

The reconstructed source tree contains no `universe_model` dispatcher. The
Phase-4 spectral and Phase-5 ordinary likelihoods remain first-class explicit
paths.

## Phase-6 inventory correction

The older migration inventory mentions `darksirens/inference/runtime.py`, but no
such file exists at pinned legacy SHA
`c042527238bd71421b792936bc48c3b815b90d6d`. Phase 6 is derived from the actual
pinned source tree, not that stale entry.

Legacy `inference/sampling.py` is not a migration unit as a whole: it mixes
sampler adapters, diagnostics, checkpointing and backend/GPU behavior. Likewise,
results/settings already live in a JAX-free `darksirens.io` namespace in the
pinned tree; preserve that separation rather than collapsing all IO under
inference.

## Scientific questions

None opened. No scientific behavior change is authorized during reconstruction.

## Current action — Phase 6

Reconstruct the generic unit-cube prior transform from pinned
`inference/prior.py` as the next small subphase. Preserve the frozen uniform,
truncated-normal, truncated-lognormal, Beta(1,b), and explicit joint cube-map
semantics with exact legacy/candidate probes. Do not migrate `build_parameter_space`,
survey/LSS/sky discovery, CLI assembly, or sampler backend dispatch in the same
step.
