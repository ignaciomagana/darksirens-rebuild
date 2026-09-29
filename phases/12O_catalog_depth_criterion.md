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

## Depth selected (2026-09-29)

**z_depth = 0.245.** Computed on the MIKO H100 with the target's own state at
each candidate, before any H0 at the new depth. Script
`logs/analysis_depth_2026-09-29/depth_criterion.py` in the GPU checkout;
product `depth_criterion_gpu.npz`, sha256 bb716bd625424a54.

```text
z_d     T/E - 1        z_d     T/E - 1        z_d     T/E - 1
0.200   +0.047         0.235   -0.012         0.270   -0.124
0.205   +0.040         0.240   -0.026         0.275   -0.150
0.210   +0.022         0.245   -0.044  <--    0.280   -0.177
0.215   +0.016         0.250   -0.053         0.285   -0.206
0.220   +0.011         0.255   -0.064         0.290   -0.240
0.225   +0.009         0.260   -0.080         0.295   -0.298
0.230   +0.001         0.265   -0.104         0.300   -0.378
```

The jump grows monotonically in magnitude beyond 0.23, so the largest depth
within 5% is unambiguous.

## Run

(appended)
