# Phase 12O — the catalog depth, set by a continuity criterion

## Status

**CRITERION DECLARED (owner, 2026-09-29) before the depth or any H0 is
computed from it.** The depth it selects, the consumer change, and the chain
run are appended below as they happen. The result is a candidate for the
result of record; its acceptance is the owner's.

## Why

- Phase 12N: z_depth 0.3 sits on the input catalog's upstream z = 0.3 edge.
  There the model completeness overestimates the observed galaxy density, so
  the host prior dips below the expected density and jumps back at the cut;
  that jump carries the catalog's pull on H0.
- Phase 12M (the z_depth 0.3 result) is suspended.
- The first proposed criterion (model completeness within 10% of the counts
  at every z below the depth) admits no depth: at the calibration point the
  nearby catalog is 10 to 38% above the model at z < 0.18.

## Criterion

z_depth is the largest value at most 0.3 for which the host prior is
continuous at the cut within 5%:

```text
| T(z_d-) / E(z_d-) - 1 | <= 0.05
```

- T is the P12.4 field host-density numerator (galaxy term plus missing
  budget), summed over the covered nside-64 pixels. E is the expected density,
  summed the same way.
- Both are evaluated at the last core z-grid node at or below z_d, from the
  target's own per-proposal state built with that z_d.
- The evaluation point is the calibration point: H0 = 67.74, and M0hat and
  sigma_M at their prior means.
- Candidates are z_d = 0.200 to 0.300 in steps of 0.005. Everything else is
  as in the result of record (consumer `c86629b`, core `a46dec7`).

## Depth selected

(appended)

## Run

(appended)
