# Phase 09 S2 — survey selection-fraction/depth maps

Status: **ACCEPTED**

## References

```text
legacy oracle:    ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
S0a golden:       references/surveys_s0a_legacy_reference.json
surveys repo:     ignaciomagana/darksirens-surveys
accepted S2 head: e7a8839348b491dab33ce733b35159e8adbc2f1c
accepted S2 tree: 2d90f98b65576d3a1e02dbae81489b99f431be5a
```

Core remains frozen at `af2488b0ccb48c65e63cffcae306a8a4a4bfeb66`.

## Scope

S2 ports only the reusable consumption/degradation semantics from the legacy
`darksirens/catalogs/depth_map.py`:

```text
SelectionFractionMap
selection_fraction_from_arrays(...)
load_selection_fraction(...)
```

No raw survey depth-map builder, DESI schema, LSS completion or inference-time
completeness logic enters this slice.

The frozen behavior is:

- RING input only;
- native covered pixel: `f_p = clip(1 - masked_frac, 0, 1)`;
- native `counts == 0`: `f_p = 0`;
- degradation: RING -> NEST child grouping -> equal-area average -> RING;
- uncovered child area participates as zero, rather than being omitted and
  renormalized over covered children;
- area and coverage diagnostics match legacy.

The implementation explicitly preserves the actual frozen code rather than an
old misleading legacy comment: degradation uses unit weights over all children,
so uncovered children reduce the output area fraction.

## Exact S0a parity

Native nside-2 hash:

```text
1df9bb6ef0181dc0820abf5a8d676303348817e7a4ebb6d4ae067d6c3120aec5
```

Degraded nside-1 hash:

```text
bfb2e4ce6fcb3d8a278e8d3a3e1972ce34ec885c44209991f1295836c602b0b3
```

Frozen diagnostics also match:

```text
area_deg2: 33088.31266880504
native:    n_covered=44, n_zero=4
degraded:  n_covered=12, n_zero=0
coverage:  n_occupied=3, n_empty_covered=9,
           f_p_occupied_mean=0.8541666666666666,
           f_p_occupied_min=0.8125
```

## Acceptance gate

```text
workflow:  ci
run:       34676792487
job:       103507957433
head:      e7a8839348b491dab33ce733b35159e8adbc2f1c
result:    SUCCESS
pytest:    14 passed
firewall:  PASS
```

The exact-head suite replays all S1 catalog tests plus the S2 native/degraded
hashes, coverage report, uncovered-child convention, HDF5 loader/RING guard and
input validation.

## Legacy caveat deliberately retained

The historical `build_mth_map.py` may construct `masked_frac` from a source-count
fraction rather than an unbiased area fraction. S2 does not silently repair that
scientific estimator. It faithfully consumes the artifact semantics. Any later
area-unbiased estimator must be introduced as a separate scientifically
validated change.

## Next slice

S3 ports only the **offline** magnitude-selection fitting frozen by S0b:
Gaussian and Schechter fits, h-scaled `H0=100` reference magnitudes,
K-correction handling where supported, strata, covariance ordering and
serialized fit provenance. Runtime `C_sel(z; theta)` evaluation remains in
frozen `darksirens-core`.
