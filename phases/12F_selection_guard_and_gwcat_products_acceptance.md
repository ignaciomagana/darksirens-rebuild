# Phase 12F — selection guard and GW input products: acceptance status

## Status

**NOT ACCEPTED. Consumer change merged without contract CI on the owner's
decision of 2026-09-27; gate 2 met by the owner's decision of 2026-09-28;
gates 3 to 6 open; gate 1's green run still owed.**

Contract: `phases/12F_selection_guard_and_gwcat_products_contract.md`
(merged as proposed, e9dc0b1, 2026-09-27). This record follows its acceptance
gates one by one and says what each still lacks. It changes no setting.

## Gate 1: consumer PRs merged under contract CI

Merged, but not under contract CI. The owner decided on 2026-09-27 that
`desi_darksirens_selection` stays private (it holds private material), so
its `phase12-contract` workflow cannot run until the GitHub Actions billing
block is cleared. On that decision the PRs were squash-merged in order, each
merged tree checked against the PR head it came from:

```text
#11  Phase 12F        head 5d97aab2                      -> main 40e0442  (tree b8cccf8f, identical)
#12  Phase 12G        head c8dd1d08, rebased as 86af9e9  -> main ba0b298  (tree identical)
#14  Phase 12H repin  head ffd9fda4, rebased as 5e4bc21  -> main e72c24a  (tree identical)
#13  script entry points  head c16977e2                  -> main 52389c6  (tree e38310ff, equal to a local merge)
runbook merge note                                       -> main 53ed335
```

Every workflow run ended with zero steps: PR runs 36285158529 (#11),
36336609638 (#12), 36339358665 (#13), 36340462060 (#14); post-merge push runs
36341717254, 36341971065, 36342377696, 36342404316.

Stand-ins on `main` `52389c6` (Hildafs, 2026-09-27):

```text
CI-equivalent, contract-only   Python 3.12.13, numpy 2.5.3, pytest 8.4.2   compileall clean; 250 passed, 7 skipped
frozen a46dec7 environment     CPython 3.11.10, numpy 1.26.4, jax 0.4.34,  check_frozen_environment ok;
                               dynesty 2.1.4, pytest 8.4.2                 281 passed, 0 skipped, 0 failed
```

Still owed: a green `phase12-contract` run on the merged `main` once Actions
is unblocked (billing).

## Gate 2: rebuilt products

The consumer does not rebuild the products. It pins the campaign's reference
build of Product A by file, bytes and sha256 and refuses anything else
(`config/inputs.production.json`, `gw_products`). The files on Hildafs were
re-hashed on 2026-09-27 and match:

```text
A_pe_chieff_bbh259_n4096_v20.h5     86136323 bytes   a24a5903a7f7da6fdcdee22f58c4c0efa76447f2cf4d581dc19ec3e60ce478a5
A_sel_chieffref_o3o4ab_v20.h5      126491918 bytes   bab92babf2d6958a6ed04ee536c44fa533f5c4822ca9a22f934347a089d21ab5
```

**Met (owner, 2026-09-28).** The owner confirmed that consuming the pinned
reference build directly satisfies this gate. This resolves the contract's
open question 3: the products are not rebuilt locally. A rebuild with
`gwcat validate --strict` 84/84 was done once, in the campaign (Phase 12E).

## Gate 3: the P12.4 builder accepts the rebuilt 2.0 pair

With gate 2 met by the reference build, "the rebuilt pair" is the pinned
Product A pair itself. Not yet shown on the production path: P12.2's spectral probe has not run
(gate 4). A measurement-only build of the P12.4 target on the Product A pair
was started on 2026-09-27 (Hildafs Slurm, `logs/measure_blocks.py` in the
production checkout); its outcome is not part of this record.

## Gate 4: regenerated P12.1 to P12.3

Open. First production execution on 2026-09-27 (Hildafs Slurm 1340521,
consumer `main` 53ed335, core `a46dec7`, frozen environment
`darksirens_benchmark_local/envs/consumer_repin_a46dec7`, production checkout
`/hildafs/projects/phy230014p/magana/desi_darksirens_selection-phase12`):

- P12.1 passed: `provenance/bootstrap_environment.json`, status ok for the
  four packages at their pinned commits and dynesty 2.1.4.
- The standardized-inputs stage rebuilt the catalog
  (`data/phase12/catalogs/desi_union_nside64.h5`, 22,787,566 rows after the
  M_APP <= 21 cut) and then failed closed by the Phase 12B rule: 56 occupied
  nside-64 pixels have `f_p = 0`. They hold 941 galaxies (4.1e-5 of the
  catalog); every one of their 224 native nside-128 children has counts > 0
  and `masked_frac = 1.0`; 55 of the 56 lie within 8 deg of the LMC or 5 deg
  of the SMC. Details and the options are in the production checkout's
  `logs/FOOTPRINT_FINDING_2026-09-27.md`.
- P12.2, P12.2b and P12.3 did not run.

Still owed: an explicit scientific contract for catalog rows in fully masked
pixels (the 12B rule requires one), then the chain re-run from P12.1.

## Gate 5: fixed-coordinate check at the calibration point

Open; it needs gate 4's products. The calibration point is
H0 = 67.74, M0hat = -20.309781546689074, sigma_M = 0.7144467727667887.

## Gate 6: promotion

Open. It needs gates 1 (green run), 4 and 5.

## Gate 7 (for a P12.4 result)

Not applicable yet. The consumer's runner now asserts dynesty convergence and
a zero soft-guard penalty at the posterior mean and median (core `a46dec7`
reports `dlogz_final` and `stop_reason`).

## Verdict

**Not accepted.** The 12F settings (soft guard at cap 10, Product A inputs,
dynesty 2.1.4) are in force in the consumer's `main` by the owner's merge
decision, without the green contract run the contract asked for, and the
chain has not passed its input stage on the production assets.
