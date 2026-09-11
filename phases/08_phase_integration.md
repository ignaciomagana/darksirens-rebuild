# Phase 8 — integration and core freeze

Status: **COMPLETE — DARKSIRENS-CORE FROZEN**

```text
legacy reference:      c042527238bd71421b792936bc48c3b815b90d6d
Phase-7 main/base:     6ed3dc74aa0fcde4da128036cc3d56c29250d370
Phase-8 branch:        rebuild/phase8-core-freeze
accepted Phase-8 head: 53bf08fd3670da4d2e48a146319c193b9cff8858
accepted Phase-8 tree: 0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
PR:                    #7
PR matrix:             34/34 SUCCESS
squash merge:          af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
merged tree:           0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
post-merge integrity:  34642213518 / 103404444142 SUCCESS
```

## Accepted Phase-8 slices

```text
8A public counterpart / bright composition
  head:      5256141e00a2d96a72b9cbf2182a77174c8c269e
  tree:      6252d1725ee07562840f0ce48b0dc6fe90a4aee4
  dedicated: 34634374241 / 103378585284 SUCCESS
  broad:     34634374571 / 103378586398 SUCCESS

8B sampler-facing InferenceTarget
  head:      2e98ca1f1a67cf688f8da8444c3747d446a4e91d
  tree:      a893564f982aaa1174b41367927c2708148fd2b6
  dedicated: 34635288617 / 103381567625 SUCCESS
  8A replay: 34635288475 / 103381567028 SUCCESS
  broad:     34635288518 / 103381567351 SUCCESS

8C host-density / RedshiftModel extension seam
  head:      875a949d5a9f5ffb89f3a64cad030dcfc6daf6a2
  tree:      1219bba07d3327c83da0164602e60abe8083ba0b
  dedicated: 34636321077 / 103384995159 SUCCESS
  8B replay: 34636321027 / 103384994787 SUCCESS
  8A replay: 34636321033 / 103384994066 SUCCESS
  broad:     34636321017 / 103384994129 SUCCESS

8D package/API/install/example freeze
  head:      53bf08fd3670da4d2e48a146319c193b9cff8858
  tree:      0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
  dedicated: 34640864579 / 103399889477 SUCCESS
  8C replay: 34640864573 / 103399889300 SUCCESS
  8B replay: 34640864514 / 103399889791 SUCCESS
  8A replay: 34640864511 / 103399889303 SUCCESS
  broad:     34640864495 / 103399889097 SUCCESS
  result:    534 passed, 1 skipped
```

The accepted 8D clean-wheel gate required zero `src/darksirens` diff from the
accepted 8C head. The final slice therefore changed packaging, documentation,
examples and validation only; it did not alter scientific/runtime implementation.

Two pre-acceptance 8D candidates failed only documentation assertions and were
not accepted:

```text
3f67c61900ae6513ad5dc23e69e7abc44d1551b9
54dc2e3ad8817a7da693da57830b7e372fbb7721
```

## PR integration

PR #7 was opened from the immutable accepted head
`53bf08fd3670da4d2e48a146319c193b9cff8858` onto Phase-7 `main`.

The complete pull-request historical/scientific matrix finished 34/34 SUCCESS.
The PR was squash-merged with expected-head protection, producing:

```text
merge SHA:   af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
merge tree:  0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
```

The merge tree is exactly the accepted Phase-8 tree. Git `main` resolves to the
merge SHA above.

## Post-merge integrity

Only the push-triggered reference-integrity workflow ran on merged `main`:

```text
run/job: 34642213518 / 103404444142
result:  SUCCESS
```

The job validated the frozen reference bundle and compared the CPU reference in
exact mode:

```text
PASS backend=cpu owner=all cells=15 mode=exact max_relerr=0.000e+00
```

No nonexistent post-merge broad run is claimed; the full broad and historical
matrices were already green on the exact accepted PR head.

## Frozen core contract

`darksirens-core` is now frozen at:

```text
main SHA:  af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
tree:      0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
```

The frozen core owns:

- JAX cosmology and interpolation;
- standardized GW PE/injection loaders and gwcat-store consumption;
- population models and reusable angular models;
- standardized galaxy catalog runtime;
- ordinary completeness/redshift kernels and host weighting;
- counterpart/bright-siren objects;
- spectral/dark/complete/bright hierarchical likelihoods;
- selection, prior, sampler, checkpoint, result and provenance infrastructure;
- the small public API built in Phases 7–8;
- explicit `InferenceTarget` and host-density / `RedshiftModel` extension seams.

Core does not own survey-native ingestion/masks/depth construction, LSS/Q/latent
field state, lensing-specific physics/state, or campaign-specific orchestration.
Core imports no companion package and has no generic plugin registry or
`universe_model` switchboard.

## Stop point

Reconstruction of `darksirens-core` is complete. Companion repositories remain
unstarted in this closeout. No further production work is authorized by this
record.