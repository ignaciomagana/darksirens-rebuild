# Phase 12F — selection guard and GW input products: acceptance status

## Status

**ACCEPTED (owner, 2026-09-29; promoted with contract CI waived, as for
12H).** Gates 2 to 5 and 7 are met on the production path (2026-09-29). Gate
1's green contract run stays owed until GitHub Actions is unblocked; the local
stand-ins recorded here replace it. The guard cap of this record (10) is
superseded by Phase 12L (20).

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
Product A pair itself. **Met on the production path (2026-09-29): the P12.4
target was built on the pinned pair and sampled; see "Production-path
evidence" below.** Earlier state: P12.2's spectral probe has not run
(gate 4). A measurement-only build of the P12.4 target on the Product A pair
was started on 2026-09-27 (Hildafs Slurm, `logs/measure_blocks.py` in the
production checkout); its outcome is not part of this record.

## Gate 4: regenerated P12.1 to P12.3

**Met (2026-09-29)** after Phase 12I: both runs below. Earlier state: first production execution on 2026-09-27 (Hildafs Slurm 1340521,
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

**Met (2026-09-29).** CPU: total ln L bitwise equal to the reference and
N_eff within 3.4e-15. GPU: 6e-16 and 7.1e-15. Both are within the 1e-12
relative criterion. The calibration point is
H0 = 67.74, M0hat = -20.309781546689074, sigma_M = 0.7144467727667887.

## Gate 6: promotion

**Met (owner, 2026-09-29).** Promoted with gate 1's green run waived (owed
once Actions is unblocked).

## Gate 7 (for a P12.4 result)

**Met by the GPU run below (2026-09-29).** dynesty stopped on convergence at
final dlogz 0.0999, and the penalty is exactly zero at the posterior mean and
median, under the Phase 12L cap 20.

## Production-path evidence (2026-09-29)

Two production-path executions from the merged consumer `main`, core `a46dec7`
(recorded 2026-09-29). Checkouts on Hildafs under
`/hildafs/projects/phy220048p/magana/darksirens-core-data/`. Hashes are sha256,
first 16 hex.

**CPU run: P12.1 to P12.3, cap 10.** Consumer `dc9c8a3`, frozen environment
`consumer_repin_a46dec7` (CPU jaxlib), Hildafs Slurm 1346044 on RM node r009,
2026-09-29 03:55 to 04:13 UTC, checkout `desi_darksirens_selection-phase12`.
The driver record `provenance/fixed_population_chain.p12_1_to_p12_3.json`
(3ee41c955ed560a1) has status `pass`.

```text
P12.1   pass                                                 bootstrap_environment.json      3db1aa79a63f933a
inputs  pass: 22,787,566 after the cut, 2,287 removed by the   inputs.resolved.json            441d08bcb9b2e3be
        12I rule, 22,785,279 retained; 0 occupied pixels       desi_union_nside64.h5           f6227dc0c31c82c8
        with f_p = 0
P12.2   pass; calibration probe total ln L -765.1371043921606  preinference_diagnostics.json   1c4719323d86cd7c
        (bitwise the 12F reference), N_eff 12837.827176048335
        (3.4e-15 relative)
P12.2b  pass
P12.3   pass; 241/241 accepted, 39 penalised (H0 21-40),       fixed_population_spectral_h0.json db3bc2a3b884aee4
        MAP 64.5 and mean 64.643 unpenalised
```

**GPU run: full chain P12.1 to P12.4, cap 20 (Phase 12L).** Consumer
`c86629b`, Phase 12K CUDA environment `consumer_a46dec7_cuda12`, MIKO NVIDIA
H100 NVL (driver 545.23.08) inside Slurm allocation 1345441, 2026-09-29 05:03
to 05:33 UTC (P12.4 28 min), checkout `desi_darksirens_selection-phase12-gpu`.
The chain record `provenance/fixed_population_chain.json` (92cd5a48f926592a)
has status `pass`.

```text
P12.1   pass                                                 bootstrap_environment.json      bff563bf1883f88d
inputs  pass, the same counts; the same standardized catalog   inputs.resolved.json            52d5fc6aad8218f9
        bytes (f6227dc0c31c82c8)
P12.2   pass; calibration probe total ln L -765.1371043921611  preinference_diagnostics.json   6aa5aeb9aa94492b
        (6e-16 relative to the reference), N_eff
        12837.827176048382 (7.1e-15)
P12.2b  pass
P12.3   pass; 241/241 accepted, 0 penalised, MAP 64.5 and      fixed_population_spectral_h0.json 42d21f65d9fdce55
        mean 64.643 unpenalised
P12.4   pass; dynesty 2.1.4, nlive 1000, seed 22, stop reason  fixed_population_desi_h0.json   be23ce578ced2e62
        convergence, final dlogz 0.0999 (target 0.1), log Z   fixed_population_desi_samples.npz 8767a38604b71289
        -780.722 +- 0.058; anchor (H0 64.5) N_eff 7,310 = 2.16 x
        threshold, penalty 0; posterior mean and median
        unpenalised (N_eff 8,808 and 8,854; total MC variance
        7.8); 12F gate 7 status "met"
```

An earlier GPU run at cap 10 (consumer `dc9c8a3`, 04:03 UTC) passed P12.1 to
P12.3 and stopped before sampling at the P12.4 anchor. That run is the trigger
of Phase 12L; its products are kept in the GPU checkout under
`logs/prior_runs/cap10_20260929T0403Z/`.

The P12.4 H0 posterior (median 71.07; 68% interval 66.29 to 75.13) is a
pipeline result. It is not a result of record until the owner accepts it.


## Verdict

**Accepted (owner, 2026-09-29).** The 12F settings are in force: Product A
inputs, dynesty 2.1.4 and the soft guard, at the Phase 12L cap 20. The chain
passes on the production assets (evidence above). The green contract run
(gate 1) is still owed.
