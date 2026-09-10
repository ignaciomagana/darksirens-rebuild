# Phase 1 report — frozen numerical reference harness

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
reference repo:    ignaciomagana/darksirens-core
reference HEAD:    74559ef33931b3fe0400ada9a0cb11d3f9fbe48b
```

## Status

COMPLETE.

## Work completed

- Initialized `darksirens-core` with validation infrastructure only; no reconstructed scientific implementation package exists yet.
- Copied `tests/golden/unified_k1_golden.json` into `tests/reference/legacy/unified_k1_golden.json` without modifying its bytes.
- Verified the copied file has the same Git blob SHA as the legacy source: `560e44adb712763893111a3607f6d7ca8b168b7a`.
- Recorded source-test provenance: legacy `tests/test_unified_k1_golden.py` blob `0f4e3301db2b4a73c574791a871d53fd56f0cad2`.
- Added a manifest recording the pinned source commit, validated CPU stack, backend banks, three coordinate fractions, cell ownership, and tolerances.
- Added a stdlib-only immutable-reference validator.
- Added a neutral candidate comparator with per-owner comparison (`core`, `lss`, `lensing`).
- Added a separate-import-root legacy replay runner that evaluates the pinned legacy test's own `_evaluate_cell` function for all 15 cells.
- Added CI for immutable-reference integrity and for replaying the pinned legacy implementation.

## Canonical golden bank

```text
15 cells
3 deterministic coordinates per cell
coordinate fractions: 0.5, 0.35, 0.65
canonical rtol: 1e-12
canonical atol: 0
recorded backends: cpu, gpu:NVIDIA H100 NVL
```

Core-owned cells:

```text
bright
complete_volume
complete_zero
empty_row_routing
field_k1
marks
plain_compact
plain_full
sel_batch
sky_dipole
spectral
```

LSS-owned cells:

```text
ensemble_marg
qdet
use_lss
```

Lensing-owned cell:

```text
wl_lognormal
```

The survey package has no direct cell in this bank; survey parity will be established with raw-survey -> standardized-catalog fixtures when survey migration begins.

## Legacy drift discovered and preserved honestly

The pinned legacy testing documentation records a pre-existing CPU discrepancy for `qdet`, `use_lss`, and `ensemble_marg`: maximum relative difference about `2.3e-12`, maximum absolute difference `3e-13`, against the nominal `1e-12` golden tolerance.

This was not hidden by globally weakening the reconstruction target.

Two comparison profiles now exist:

```text
canonical
    all reconstructed implementations target rtol=1e-12, atol=0

legacy-replay
    only the three documented CPU LSS cells may use rtol=3e-12
    every other cell remains at rtol=1e-12
```

The replay allowance describes the pinned legacy checkout. It is not the acceptance criterion for new LSS code.

## CI result

Reference integrity workflow at core HEAD `74559ef33931b3fe0400ada9a0cb11d3f9fbe48b`:

```text
run: 34429433913
status: success
```

Pinned legacy replay workflow:

```text
run: 34429433906
job: 102721583697
status: success
```

The replay job:

1. checked out `darksirens-core`;
2. checked out the pinned legacy SHA into a separate directory;
3. installed the pinned CPU validation stack;
4. validated the immutable reference files;
5. evaluated all 15 cells with the legacy implementation;
6. passed the all-cell pinned-checkout replay profile;
7. passed all core-owned cells at canonical `rtol=1e-12`;
8. passed the weak-lensing cell at canonical `rtol=1e-12`.

## Scientific changes

None. No mathematical kernel was copied, rewritten, or reorganized in Phase 1.

## Next phase

Phase 2: build the minimal installable `darksirens-core` foundation and begin migrating the lowest-level scientific contracts in small parity-gated slices. Start with package/import/JAX-runtime contracts and cosmology/GW data contracts before the hierarchical likelihood.
