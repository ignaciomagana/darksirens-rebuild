# Phase 12I — catalog rows in fully masked native footprint pixels

## Status

**ACCEPTED CONTRACT CHANGE (owner, 2026-09-28): the proposed rule.**
Consumer implementation: `desi_darksirens_selection` PR #15, merged as
`3845085` (2026-09-28). **Gates 2 to 5 met on the production path
(2026-09-29): see "Production-path evidence".**

## Trigger

The first production execution of the accepted Phase 12 chain on the
production assets (2026-09-27; Hildafs Slurm 1340521 on r021; consumer
`main` `53ed335`; core `a46dec7`; frozen environment
`darksirens_benchmark_local/envs/consumer_repin_a46dec7`; production
checkout `/hildafs/projects/phy230014p/magana/desi_darksirens_selection-phase12`)
passed P12.1 and stopped at the standardized-inputs stage:

```text
InputContractError: occupied DESI catalog pixels are marked off-footprint: 56
```

The rule is Phase 12B contract item 4: "fail closed if any catalog-occupied
nside-64 row has `f_p = 0`, unless a later explicit scientific contract
explains why such a row is valid" (`12B_field_footprint_contract.md:255`),
restated in the 12B acceptance record ("an occupied catalog pixel marked
uncovered is a hard error"). This is that contract.

## What the rows are

Standardized catalog `data/phase12/catalogs/desi_union_nside64.h5` (nside 64,
RING; 22,787,566 rows after the `isfinite(M_APP) & (M_APP <= 21.0)` cut;
30,470 occupied pixels). Footprint map `mth_map_nside128.h5` (nside 128,
RING; `f_p = 1 - masked_frac` on counts > 0, `f_p = 0` on counts == 0;
degraded to nside 64 by equal-area child average).

- The 56 pixels hold 941 galaxies, 4.1e-5 of the catalog (ngals 1 to 644,
  median 3.5; a typical occupied pixel holds 752).
- Every one of their 224 native children has counts > 0 and
  `masked_frac = 1.0`; none has counts == 0. The degrade therefore gives
  exactly 0.
- RA 10.7 to 95.4 deg, Dec -74.6 to -61.9 deg: 53 pixels (288 galaxies)
  within 8 deg of the LMC, 2 (9 galaxies) within 5 deg of the SMC, and one
  (RING 46217, RA 69.9, Dec -61.9, 644 galaxies) 9.5 deg from the LMC.
- Over the whole sky the native map has 520 fully masked pixels
  (counts > 0, `masked_frac = 1`); 2,287 catalog rows sit in them, of which
  the 941 above are in nside-64 pixels whose four children are all fully
  masked. The other 1,346 sit in fully masked children of partially covered
  nside-64 pixels, where they pass the 12B rule today.
- The legacy selection fit (`selection_fit_union.json`) used 22,786,660
  galaxies, 906 fewer than the cut catalog. That number matches neither 941
  nor 2,287; the legacy cut is not identified by it. The frozen reference's
  `run_s3_footprint.py` applies `C_p = f_p Cbar` with `f_p = 0`
  off-footprint and does not remove catalog rows.

The map was built from the same source catalog (its counts are the objects
per pixel), so a fully masked pixel with counts > 0 is area the mask
declares unobserved that still carries catalog objects: dense Magellanic
Cloud fields, where the objects are not the survey's galaxy sample.

## Proposed rule

After the quality cut and before pixelation, remove every row whose native
nside-128 RING pixel of the footprint map has `f_p = 0` (counts == 0, or
counts > 0 with `masked_frac = 1`). The pixel index is healpy's `ang2pix`
in RING ordering at the map's native nside, the call darksirens-surveys
pixelates the catalog with, so a row is judged by the pixel it would be
counted in.

Consequences on the production inputs:

```text
rows after the quality cut     22,787,566
rows removed by the mask            2,287   (941 in the 56 pixels; 1,346 elsewhere)
rows after the mask            22,785,279
occupied nside-64 pixels with f_p = 0 after the mask:  0  (the 12B check is kept)
```

The counts are declared in the consumer's input contract
(`desi_native.catalog_mask`: `expected_rows_removed` 2287,
`expected_rows_after_mask` 22785279) and the stage fails closed on any other
count, so a different map or source catalog cannot pass silently. The input
provenance records the rule, the map fingerprint, both counts and the sky
range of the removed rows. Nothing else changes: the quality cut, the
pixelation, `z_depth`, the footprint semantics and degrade, the field rule
`C_p(z) = f_p Cbar(z)`, the off-footprint rule for PE samples and
injections, the guard, the sampler and the pins.

Why this form and not the minimal one: with `C_p = f_p Cbar`, a galaxy in
area with `f_p = 0` is one the model says cannot be in the catalog. Removing
rows only where the degraded nside-64 `f_p` is 0 (941 rows) satisfies the
12B check but leaves 1,346 rows in masked area inside partially covered
pixels, where the same inconsistency is merely diluted. Removing rows at
the map's own resolution makes the catalog consistent with the mask
everywhere.

## Alternatives

1. Remove only the rows of the 56 nside-64 pixels with degraded `f_p = 0`
   (941 rows). Minimal; leaves the 1,346 rows in masked children.
2. Treat the 56 pixels as covered, with `f_p` from counts alone. Contradicts
   the declared mask semantics and keeps Magellanic-field objects as hosts.
3. Regenerate the native catalog under the same mask upstream (the ingest
   experiment of the frozen reference). Same result as the proposed rule if
   the same mask is applied at nside 128, at the cost of a new source file
   and new expected counts.
4. Keep the fail-closed rule and do not run. The chain then has no path to
   P12.2 on the production assets.

## What the evidence does not settle

- Whether the 941 or 2,287 objects are galaxies at all; no per-object check
  was made. Their number is 1e-4 of the catalog either way.
- The effect on P12.2 to P12.4 numbers: not measured before the rule is
  applied. The evidence run below reports P12.2, P12.2b and P12.3 under the
  rule; there is no comparison run without it, since the chain cannot pass
  the input stage without it.
- The legacy selection fit's own row set (906 fewer rows than the cut
  catalog) is unexplained by this record.

## Acceptance gates

1. The owner accepts the rule (or an alternative) in this record.
   **Met 2026-09-28: the proposed rule (remove rows whose native nside-128
   pixel has `f_p = 0`); alternatives (b) to (e) not taken.**
2. Consumer PR #15 merged with the runbook section and the contract tests;
   contract CI remains blocked (billing), so the local stand-ins are
   recorded (CI-equivalent 251 passed, 8 skipped; frozen environment input
   and chain tests 12 passed).
3. The input stage passes on the production assets with exactly the declared
   counts, and `provenance/inputs.resolved.json` records them.
4. P12.2, P12.2b and P12.3 run to completion under `a46dec7` on the masked
   catalog and are accepted under the 12F criterion (soft guard, cap 10).
   Shown on the PR branch by the evidence run below; to be repeated from
   the merged `main`.
5. Promotion to an acceptance record listing the merge SHA, the input
   provenance hashes and the P12.1 to P12.3 record hashes.

## Evidence run

P12.1 to P12.3 on the PR #15 branch (`e0eb170`) in a separate checkout
(`/hildafs/projects/phy230014p/magana/desi_darksirens_selection-phase12-12i`),
Hildafs Slurm 1340556, started 2026-09-27.

- P12.1: pass (same environment as the production run).
- Standardized inputs: **pass**, with exactly the declared counts:
  rows after the cut 22,787,566; removed by the mask 2,287; retained
  22,785,279 (`provenance/inputs.resolved.json`, `desi.catalog_mask`). The
  removed rows span RA 6.5 to 259.1 deg and Dec -75.4 to +37.1 deg: the
  1,346 outside the 56 pixels are spread over the sky's fully masked
  children (bright-object masks), not only the Magellanic fields. The
  nside-64 coverage report now has 30,411 occupied pixels (59 fewer) and
  **0 occupied pixels with `f_p = 0`**; the occupied `f_p` mean is 0.8632
  (0.8616 before). Standardized catalog sha256 `f6227dc0c31c82c8...`;
  footprint sha256 `1e4e5c675dd59ab2...`; Product A pair accepted.
- P12.2: **pass**, `accepted: true`, `phase12b_accepted: true`. All 14
  spectral probes (H0 20 to 140) accepted under the soft guard at cap 10.
  The probe at the calibration point reproduces the Phase 12F reference
  values exactly (total ln L -765.1371043921606, selection N_eff
  12837.827176048291), the bitwise form of 12F gate 5's 1e-12 requirement,
  under the production blocks 131072/32.
- P12.2b: **pass** (footprint diagnostics on the masked catalog).
- P12.3: **pass**, `accepted: true`. 241 grid points (H0 20 to 140, step
  0.5), all accepted; 39 penalised by the soft guard (H0 21.0 to 40.0, where
  the selection N_eff falls under the cap-10 threshold; 20 of them outside
  the budget); grid N_eff 6,348 to 18,990. The grid maximum (H0 = 64.5) and
  the grid posterior mean (64.64) are unpenalised, with penalty exactly 0;
  the unpenalised likelihood mass on penalised points is 6.3e-8. This is
  the P12.3 spectral baseline of the chain, a diagnostic gate for P12.4,
  not a result of record.
- Whole run: 1 h 17 min on one RM node (28 threads, CPU-only jaxlib);
  P12.3 took about 1 h of it. Driver record
  `provenance/fixed_population_chain.p12_1_to_p12_3.json` status `pass`.

Record hashes (sha256, first 16 hex) of the products in the evidence
checkout, for gate 5:

```text
provenance/bootstrap_environment.json              e9ce1fd99be9f503
provenance/inputs.resolved.json                    164771ae03e305db
provenance/preinference_diagnostics.json           f17f642ab1eda3cc
results/phase12/fixed_population_spectral_h0.json  5548b0307a23b2d3
data/phase12/catalogs/desi_union_nside64.h5        f6227dc0c31c82c8
```

These were made on the PR branch (`e0eb170`), not on `main`; on acceptance
the chain regenerates them from the merged `main` before P12.4.

## Production-path evidence (2026-09-29)

Gate 2: consumer #15 merged as `3845085`. Stand-ins (billing): CI-equivalent
251 passed, 8 skipped; frozen environment 283 passed. Gates 3 to 5:

The full record of both runs (commits, environments, hashes) is in
`phases/12F_selection_guard_and_gwcat_products_acceptance.md`, "Production-path
evidence". For this record: the input stage passed in both runs with exactly
the declared counts (22,787,566 after the cut, 2,287 removed, 22,785,279
retained; 0 occupied nside-64 pixels with `f_p = 0`). Both runs produced the
same standardized catalog bytes as the evidence run (f6227dc0c31c82c8).
P12.2 to P12.3 were accepted at cap 10 (CPU) and at cap 20 (GPU), and P12.4
was accepted at cap 20.

## Verdict

**Accepted (owner, 2026-09-28).** The production catalog is admitted under
the mask-consistency rule above: rows whose native nside-128 pixel has
`f_p = 0` are removed after the quality cut and before pixelation (2,287 of
22,787,566 rows on the production assets). The chain regenerates P12.1 to
P12.3 from the merged consumer `main` before P12.4.
