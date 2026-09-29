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

## Run (2026-09-29)

The full chain P12.1 to P12.4 ran on the MIKO H100 (12K backend) from consumer
`main` `559540e` (z_depth 0.245), 17:25 to 17:57 UTC, in the GPU checkout.
Every stage passed. P12.4 converged (final dlogz 0.100, log Z -779.880 +-
0.059) and is unpenalised at the anchor, mean and median (total MC variance
at the centre 8.4); 12F gate 7 is met.

```text
H0 (z_depth 0.245)   median 68.06   mean 68.35 +- 3.95   68% [64.47, 72.57]   90% [62.29, 74.95]
catalog-free         median 64.52   68% [59.63, 69.65]
z_depth 0.3 (12M)    median 71.07   68% [66.29, 75.13]   (suspended)
z_depth 0.2 (12N C1) median 64.55   68% [61.23, 67.81]
```

Products (sha256, first 16 hex), GPU checkout:

```text
results/phase12/fixed_population_desi_h0.json       35e5ebaa806bcb81
results/phase12/fixed_population_desi_samples.npz   7e2d47821302f6ae
results/phase12/fixed_population_spectral_h0.json   a4772f498ba47742
provenance/fixed_population_chain.json              64d2672031f8da37
provenance/preinference_diagnostics.json            2cec3c2a6b56384b
provenance/inputs.resolved.json                     fc19bf80c0ee6ba5
provenance/bootstrap_environment.json               7fa49d90c35008ab
data/phase12/catalogs/desi_union_nside64.h5         c2d1ff36567419e4
```

**Residual depth sensitivity.** z_depth 0.2 and 0.245 both pass the 5%
continuity criterion (+4.7% and -4.4% at the calibration point), yet give H0
68.06 and 64.55: a spread of 3.5 (0.8 sd) inside the admissible window.
Continuity at one H0 does not remove the depth dependence. The jump's own
H0 dependence (through the n0 H0^-3 scaling of the expected density against
fixed counts) is the likely carrier. The owner decides whether this run is
the result of record.
