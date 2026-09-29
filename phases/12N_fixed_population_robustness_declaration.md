# Phase 12N — fixed-population robustness matrix (P12.6): declaration

## Status

**DECLARED (owner, 2026-09-29), before any variant is run.** This fixes the
variants, their definitions and the comparison, as P12.6 of
`phases/12_production_analysis_contract.md` requires. Results are appended to
this record as they complete. Nothing here changes the result of record
(Phase 12M).

## Declared deviation from the contract order

P12.6 is run at the fixed population before P12.5 (population
marginalization). This is the owner's decision of 2026-09-29: the catalog
variants are cheap and bear on the Phase 12M result directly. P12.5 follows,
and "fixed vs population-marginalized" is added as a row when it exists.

## Reference

Phase 12M: H0 median 71.07, 68% [66.29, 75.13], sd 4.49 (consumer `c86629b`,
core `a46dec7`, soft guard cap 20, dynesty nlive 1000, seed 22).

## Comparison, fixed now

For each variant:
- the shift of the H0 median in units of the reference sd;
- the ratio of the 68% interval widths;
- the chain's own gates (P12.1 to P12.4, 12F gate 7).

The sampler scatter is measured at the reference (seeds 22 to 24: median sd
0.02, spread 0.04; 12L "Robustness"). A shift within 0.05 is indistinguishable
from it. There is no pass/fail threshold on the shift: the matrix reports
sizes, and the owner judges.

## Variants

Each variant runs the full chain (P12.1 to P12.4) in its own scratch checkout
at consumer `c86629b`. Only the named setting or input is changed. The
variant's input products are rebuilt by the chain's own input stage.

```text
id   family                   change from the reference                                         status
C1   catalog depth            z_depth 0.2 (reference 0.3)                                        runnable
C2   catalog depth            z_depth 0.4                                                        runnable
C3   completeness assumption  m_lim 20.5 and quality cut M_APP <= 20.5, with M0hat and sigma_M    needs the selection
                              refitted at 20.5 (the reference priors are the legacy fit at 21)    refit first
C4   DESI mask definition     12I alternative (b): remove only the rows in the 56 nside-64       runnable
                              pixels with f_p = 0 (941 rows), not every row in a native pixel
                              with f_p = 0 (2,287)
C5   no-structure control     angular shuffle: every galaxy keeps its redshift, magnitude and     runnable after the
                              weight, and gets a random sky position drawn from the footprint    shuffled catalog is
                              in proportion to the native f_p; this removes the angular          built
                              galaxy structure and keeps n(z) and the completeness
G1   all-sky vs DESI-masked   selection from the injections inside the DESI footprint, paired    needs a DAG-consistent
     selection                with the matching event cut                                        definition first
```

- C1 and C2 test the internal note on the shift of H0 against the catalog-free
  baseline, which traces it to events inside the catalog's depth.
- C5 isolates the angular cross-correlation of the GW localizations with the
  galaxies. One shuffle realization, seed recorded; a second one is run if
  C5 moves the median by more than 0.1 sd.
- G1: a footprint cut on the injections (true sky position) must be matched
  by the same cut on the detected events. The events have only posteriors, so
  a naive "localization inside the footprint" cut breaks the selection. The
  cut is defined and checked on injections before G1 runs.

Already measured at the reference, and recorded in 12L "Robustness": the soft
guard cap (15, 30) and the sampler seed (23, 24).

## Addition, declared 2026-09-29 before running

```text
id   family                   change from the reference                                         status
C6   smooth-n(z) control      every galaxy keeps its sky position, magnitudes, weight and ZERR;  runnable after the
                              its Z is replaced by a random draw from the catalog's global n(z)  control catalog is
                              (a random permutation of all Z) plus a Gaussian jitter of 0.02,    built (seed 20261001)
                              reflected at 0; this removes the radial structure along each line
                              of sight and keeps the catalog's overall fall-off with z
```

- Why (owner, 2026-09-29, after C1 to C5): it is the radial counterpart of the
  angular shuffle.
- Expectation, stated before the run, from the internal depth-cut note:
  - The mismatch between the model completeness and the observed counts near
    the depth cut should survive C6, because the global n(z) keeps the
    fall-off. H0 should then stay near the reference.
  - If instead C6 returns the catalog-free value, radial structure carries
    the shift.

## Results (2026-09-29)

Every variant ran the full chain P12.1 to P12.4 on the MIKO H100 (12K
backend) in its own worktree at consumer `c86629b`. Worktrees and logs are in
`/hildafs/projects/phy220048p/magana/darksirens-core-data/robustness_12N/`
(`<id>/`, `<id>.out`).
- Every chain passed; every P12.4 converged (final dlogz 0.1) and met 12F
  gate 7.
- C4's input stage removed exactly the declared 941 rows (22,786,625
  retained). C5's removed 0: no shuffled galaxy lands in a zero-f_p pixel.
- The shift is (median minus 71.07) divided by the reference sd 4.49. The
  width is the 68% width over the reference's. Hashes are sha256, first 16
  hex, of each P12.4 result JSON.

```text
id    variant                         H0 median  mean +- sd     68%             shift    width   log Z     result
ref   z_depth 0.3 (Phase 12M)          71.07     70.88 +- 4.49  [66.29, 75.13]   --      1.000  -780.722  be23ce578ced2e62
C1    z_depth 0.2                      64.55     64.62 +- 3.56  [61.23, 67.81]  -1.45    0.744  -779.523  880911cdda8f0ae7
C2    z_depth 0.4                      67.66     68.03 +- 4.71  [63.58, 73.00]  -0.76    1.065  -782.050  8c1bd5dc0cdf5855
C4    mask rule (b), 941 rows          71.08     70.87 +- 4.49  [66.29, 75.10]  +0.00    0.997  -780.719  4e4b5fbf92de53b1
C5    angular shuffle, seed 20260929   71.55     71.51 +- 4.46  [67.03, 76.09]  +0.11    1.025  -780.252  ffb13bf4c3b8e336
C5b   angular shuffle, seed 20260930   71.17     71.25 +- 4.38  [66.92, 75.62]  +0.02    0.983  -780.381  0cc9c2f4ddb1e3a8
--    catalog-free baseline (P12.3)    64.52     64.64 +- 5.05  [59.63, 69.65]  -1.46      --        --     42d21f65d9fdce55
```

The shuffled catalogs:
- C5: `C5_inputs/`, sha256 2477a69bcc4e8c29, seed 20260929.
- C5b: `C5b_inputs/`, sha256 a84652d30fcf4baf, seed 20260930.
- Builder: `C5_build_shuffled_catalog.py`. C5b was run as declared, because
  C5 moved the median by more than 0.1 sd.

Findings. These are sizes; the owner judges.

- **The mask definition (C4) does not matter.** Shift 0.00 sd.
- **The angular galaxy structure does not carry the catalog's shift of H0**
  relative to the catalog-free baseline. Two shuffles give +0.11 and +0.02 sd.
  The +6.5 shift survives with the galaxies' sky positions randomized
  inside the footprint.
- **The catalog depth moves H0 at the 1-sigma level, non-monotonically:**
  64.6 at 0.2, 71.1 at 0.3, 67.7 at 0.4. At z_depth 0.2 the posterior sits on
  the catalog-free value, with a 26% narrower 68% interval.
  - In the core's semantics, z_depth is where the host prior switches from
    galaxies plus the (1 - C_sel) missing budget to the full expected
    density (`phases/05D2_catalog_selection.md`, "Finite-depth state
    semantics").
  - The value 0.3 was carried over from the legacy production line
    (`phases/12_P12.4_fixed_population_desi_implementation.md`). No record
    documents a physical basis for it.
- Not run, as declared: C3 needs a selection refit at m_lim 20.5; G1 needs a
  DAG-consistent event cut.

### Follow-up checks (2026-09-29, owner's choice)

**The input catalog is cut at z = 0.3 upstream.** The native DESI input has
max Z = 0.3000 exactly (99.9th percentile 0.2999), and its counts per 0.01
bin rise to the edge (1.03 M at 0.20 to 2.13 M at 0.29, then 0). C2
(z_depth 0.4) is therefore invalid by construction: the catalog is empty in
0.3 to 0.4 because of the cut, and the missing budget treats that shell as
50 to 75% complete. C2 is withdrawn as a robustness datum; the admissible
depths are at most 0.3.

**The host prior at the cut.** Internal note in the GPU checkout,
`logs/analysis_depth_2026-09-29/NOTE.md`. It is the target's exact state,
summed over the 32,143 covered pixels, at the prior means of M0hat and
sigma_M.
- At depth 0.3 the model completeness f_p Cbar(z) stays near 0.8 up to the
  cut. The observed galaxy term falls to 0.35 (H0 64.5) to 0.47 (H0 71) of the
  expected density at z = 0.3.
- The host prior therefore sits at 0.57 to 0.68 of the expectation just
  below the cut and jumps to 1.0 above it. At depth 0.2 the step is small
  (-8% to +18%).
- The jump's distance moves with H0, which pulls the events that reach it.
- Also, the expected density scales as n0 H0^-3 against fixed counts; that
  count-calibration channel is H0 information only if n0 and the
  luminosity-function calibration are independent of H0.

Reading (sizes and mechanism; the owner judges): at the fixed population,
the catalog's shift of H0 relative to the catalog-free baseline comes from
the completeness model near the catalog's upstream z = 0.3 edge, not from
galaxy structure. At z_depth 0.2 the catalog adds nothing over the
catalog-free H0.

### C6 result (2026-09-29)

```text
C6    smooth-n(z) control, seed 20261001   72.17   72.18 +- 4.50  [67.59, 76.72]  +0.24   1.033  -780.450  db482677b721ef8f
```

- The chain passed and converged, and met gate 7. The mask rule removed the
  declared 2,287 rows (positions unchanged). The control catalog is
  `C6_inputs/`, sha256 c78a93f47db48ab0.
- As predicted in the declaration, removing the radial structure along each
  line of sight leaves the catalog's shift in place (+0.24 sd, slightly up).
- Together with C5/C5b: neither the angular nor the radial galaxy structure
  carries the shift relative to the catalog-free baseline. The completeness
  model at the catalog's z = 0.3 edge does ("Follow-up checks" above).

Consequence for Phase 12M: the result of record stands as computed. At the
fixed population its catalog information is set mainly by the depth choice,
which is a modelling systematic at the level of the statistical error. How to
treat it is the owner's decision.
