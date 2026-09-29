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

## Results

(appended as they complete)
