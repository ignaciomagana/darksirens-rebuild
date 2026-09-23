# Phase 12D — core deferred follow-up: release checks, probe arms, fingerprints, budget audit, GP mass-ratio normaliser

Status: **PROPOSED PACKAGE-CHANGE CONTRACT / NOT ACCEPTED / PRODUCTION PIN UNCHANGED**

Parent science phase: `phases/12_production_analysis_contract.md`

Previous core record: `phases/12C_core_review_followup_contract.md` and
`phases/12C_core_review_followup_acceptance.md`

Active production core pin (unchanged by this record): `8bf2bec53ff7b557c6b930d4044008cb72008f61`

## Trigger

The Phase 12C contract closed with a list of items deferred on purpose, each a
policy or scope call rather than a follow-up commit: the nested-sampler
startup-check advice that still named legacy command-line flags, run-fingerprint
value normalisation, the release-freeze workflow that no longer ran, the
missing-galaxy budget count check, and the two parity probes whose reference
side was written in the probe rather than taken from the frozen code. A check
of the Phase 12C GP fix added one more: the 128-node mass-ratio lattice fixed
the one point the review recorded (m1 = m_min + 0.25 dm_min at the fiducial
taper) but not the normalisation just above `m_min` in general.

Each item was implemented on its own branch from `main` `8bf2bec5`, reviewed
independently with its own mutation check, and then stacked, with a
documentation PR on top.

## Frozen scientific reference

```text
legacy repository:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

reconstruction freeze (historical, unchanged):
  af2488b0ccb48c65e63cffcae306a8a4a4bfeb66

Phase-12C production pin (active, unchanged by this record):
  8bf2bec53ff7b557c6b930d4044008cb72008f61
  tree: 18b3bf93ad506fb289e080160cbb20cbb03d58d0
```

## Proposed core change

Repository: `ignaciomagana/darksirens-core`

Open, stacked in merge order, each based on the previous (the bottom one on
`main` `8bf2bec5`). The six item PRs touch disjoint sets of files; the stack
was built by cherry-picking the reviewed item commits with no conflicts.

```text
PR #17  Follow-up 1/7: Revive the release-freeze checks and make the examples check real
        branch: stack/1-freeze-gate   base: main
        head:  2934bdc1615c8bf9255cc471fe8d46affd47a730   tree: d105c03c546239e035d9498e4dd8fb95f4b42adb

PR #18  Follow-up 2/7: Make two parity probes call the frozen code on the reference side
        branch: stack/2-probe-arms   base: stack/1-freeze-gate
        head:  42fda95ec52c3952277458325784e51b766ae405   tree: d7396f253a0cceac5912da898d100436e7da780c

PR #19  Follow-up 3/7: Name the public-API options in the nested-sampler preflight message
        branch: stack/3-preflight-text   base: stack/2-probe-arms
        head:  628e1040c1ec9ecba0ed6ebc062686dbbe75a483   tree: 71affd6def3762f83ddb76f510cfcd4ac3167838

PR #20  Follow-up 4/7: Hash run fingerprints on normalised values and record target-setting environment settings
        branch: stack/4-run-fingerprint   base: stack/3-preflight-text
        head:  828ad3b02d07df4da57f044473ed14029b6862d8   tree: 84c8ca7aabc6f961ff259a06474207da76418bd3

PR #21  Follow-up 5/7: Check the missing-galaxy budget against catalog counts under magnitude selection
        branch: stack/5-selection-budget-audit   base: stack/4-run-fingerprint
        head:  51f3179b13df493292ca266140166102f286ea40   tree: 68039798b0f5db2301c625a9e3bbdbac2a03c53f

PR #22  Follow-up 6/7: Confirm or fix the (q, chi) normalisation grid just above the minimum mass
        branch: stack/6-q-chi-normalisation   base: stack/5-selection-budget-audit
        head:  519100d0bc2c282820194a44ad6869f5209e1c1d   tree: 763f1187c827f30c7af58d3cbe86abc870b0328c

PR #23  Follow-up 7/7: Document the second review follow-up
        branch: stack/7-docs   base: stack/6-q-chi-normalisation
        head:  e7875c1ab2ab5f712f5d0d428ccac1b17c77765a   tree: ad4ab934318fcfa51600a90636194bf9ce1f3f18
```

The tree at the head of #23 is the candidate post-12D core. Its code tree is
the head of #22 (`519100d`); #23 changes only `MIGRATION.md`, `VALIDATION.md`
and `CONTRACT.md`.

### Scientific numerics that change, and for which inputs

One deliberate change. No parametric population model, no golden-bank entry,
no likelihood outside the four GP models below, and no CI parity probe cell
moves.

1. **GP mass-ratio normaliser just above the minimum mass** (#22). Affects
   `gp1d_q, gp2d_q_chi, gp2d_q_z, gp3d_q_chi_z`, which share the normaliser.
   The density over mass ratio (and spin) at fixed primary mass must integrate
   to 1. Before, on an independent grid spanning only the allowed mass-ratio
   range: at the fiducial taper (m_min = 6, dm_min = 5) and
   m1 = m_min + 0.05 dm_min, 0.81 for three models and 0.58 for
   `gp3d_q_chi_z`; for a narrow taper inside the priors (m_min = 10,
   dm_min = 0.05), 0.055 to 0.085 at m_min + 0.25 dm_min and up to 12% off at
   m_min + 2 dm_min. Cause: two errors of opposite sign, a fixed mass-ratio
   grid that cannot follow the narrow allowed range just above `m_min`, and
   interpolation of the log-normaliser across the sharp low-mass taper. After:
   mass ratio is integrated on nodes spanning the allowed range, and the table
   holds the normaliser divided by the taper, which is smooth. Every probe at
   m_min + 0.1 dm_min or above is within 0.4% of 1 (m_min + 0.05 dm_min: 1.1%
   at the fiducial taper, 3.9% at dm_min = 0.05). About 10% error remains at
   m_min + 0.02 dm_min, where the taper suppresses the density by about
   exp(-50). Away from the taper values move at the 1e-4 level (`log_p_pop` at
   m1 = m_min + 0.5 dm_min and m1 = 30 equal to 3 decimals before and after).
   Gradients stay finite below, at and just above `m_min`. Cost per proposal
   (CPU, 20k queries): `gp1d_q` value about 2.5 times slower (1.8 to 4.3 ms),
   value plus gradient 10 to 13 ms; `gp2d_q_chi` 58 to 31 ms and 199 to 156 ms;
   `gp2d_q_z` 37 to 46 ms and 203 to 143 ms; `gp3d_q_chi_z` 535 to 597 ms and
   4410 to 3877 ms. The commit message's "unchanged within timing noise" is not
   right for `gp1d_q`; the PR body and `MIGRATION.md` carry the numbers above.

No item was found already fixed: the mass-ratio normaliser had been fixed only
at the recorded point, and the other items were open.

### Behaviour that changes without a likelihood change

- **Run fingerprints** (#20). The semantic block is hashed in a canonical form:
  arrays as dtype, shape and every value at full precision, tuples as lists,
  numpy scalars as Python scalars, NaN and infinity written out. The old rule,
  `json.dumps(..., default=str)`, hashed arrays at print precision, so the
  resume gate could accept a different target. Schema 3 to 4; older
  checkpoints are refused with a message saying why. Plain-JSON semantic
  blocks hash exactly as before (probe digests equal the frozen reference's).
  Semantic blocks with non-string keys, sets, complex numbers, datetimes or
  bytes now raise `TypeError`. New opt-in helpers `core_numerics_semantic()` and
  `core_environment_advisory()` record the settings core resolved at import
  from `DARKSIRENS_*` variables. `infer()` calls neither, nor the resume gate,
  so no ordinary run changes.
- **Nested-sampler startup-check advice** (#19). It names
  `infer(..., selection_neff_guard="soft")`,
  `infer(..., max_likelihood_variance=<cap>)` and
  `infer(..., sampler_preflight="off")` instead of the legacy command-line
  flags, and no longer points to a diagnostic script core does not ship.
  Conditions, exception types and probe draws are unchanged.
- **Missing-galaxy budget count check** (#21). New host-side diagnostic
  `darksirens.selection.catalog.selection_budget_audit`, ported from the frozen
  reference (single-curve branch). Not exported from the package root; nothing
  calls it.

### Gates that change

- **Release checks** (#17). `phase8d-final-freeze.yml` no longer checks for no
  science source change since accepted 8C (that check failed on every tree
  after Phases 12A and 12B, so nothing behind it ran). It runs on pull
  requests, pushes to `main` and manual dispatch, installs the wheel, and runs
  the packaging contract and both public examples against it, failing on any
  failure or skip (`pipefail` set).
- **Angular-wiring probe** (#18, Phase 7F3). The reference side runs the frozen
  likelihood module's own per-event PE reduction; the data now exercise the PE
  sample mask.
- **Sampler-dispatch probe** (#18, Phase 6T). The reference side runs the frozen
  `run_sampler` end to end; the candidate runs core's real dispatcher, adapters
  and NumPyro preparation. External backends are the same recording fakes on
  both sides; the checkpoint plan and nested preflight are the same stubs.
- **Nested-preflight gate** (#19, Phase 6G). Word for word except for the
  documented `LEGACY_REMEDY_MAP`.
- **Fingerprint gate** (#20, Phase 6 inference I/O). Allows exactly the schema
  change from 3 to 4 and the reworded schema-mismatch line; every other part
  of the probe output must match the frozen reference exactly.

## Acceptance gates

Mutation-based, recorded in each PR and reproduced by an independent reviewer:

```text
package-root name renamed                 5 wheel-mode packaging/example tests fail;
                                          the release job now fails with them
PE sample mask removed from core          angular-wiring probe fails; old probe passed
NumPyro plan/initialisation dropped       sampler-dispatch probe fails; old probe passed
preflight text reworded outside the map   nested-preflight comparison fails (5 rewordings)
fingerprint hashed via json default=str   12 of 34 fingerprint tests fail
budget audit without completeness         scipy anchor fails, 1041.25 against 2.656
budget audit without (1+z)^delta          scipy anchor fails, 2.139 against 2.656
previous GP mass-ratio normaliser         8 of 8 near-minimum-mass cases fail
                                          (0.81 / 0.58 at m_min + 0.05 dm_min)
```

Local full suite on the validated Hildafs stack (jax 0.4.34, numpy 1.26.4,
scipy 1.12.0, h5py 3.12.1, every optional backend installed), CPU:

```text
tree 763f1187 (head 519100d of #22, code-final):  759 passed, 1 skipped (golden regen guard)
main 8bf2bec5 before the stack:                    714 passed, 1 skipped
```

Each intermediate stack head was also checked with its own item's tests:

```text
#17 2934bdc  test_packaging_contract, test_examples                    11 passed
#18 42fda95  test_angular_wiring, test_sampler_dispatch,
             test_pe_event_reduction                                   16 passed
#19 628e104  test_nested_sampler_preflight, test_sampler_dispatch,
             test_public_infer                                         30 passed
#20 828ad3b  test_run_fingerprint_canonical, test_run_fingerprint_gate 34 passed
#21 51f3179  test_selection_budget_audit                               5 passed
#23 e7875c1  test_packaging_contract, test_cold_import_precision       8 passed
```

### Exact-head CI matrix

Every PR-triggered workflow completed successfully on every head below: 36 of
36 workflows per head, 252 runs, zero failures, all on the first attempt. The
table lists the load-bearing runs; the workflows each item touched are
`phase8d-final-freeze` (#17), `phase7f3-angular-wiring` and
`phase6t-sampler-dispatch` (#18), `phase6-runtime-guards`, the workflow in
`phase6g-nested-preflight.yml` (#19), and `phase6-inference-io` (#20). The
logs show the new gates doing their job: the release-contract step ran 11
wheel-mode tests with no skip; Phase 7F3 and Phase 6T printed exact parity with
the frozen code on the reference side; Phase 6G printed "exact (legacy CLI
remedies mapped to core keywords)"; the fingerprint gate printed "exact apart
from the documented schema 3 -> 4 bump". `phase8-regression` ran 759 passed,
1 skipped at the code-final head, the same count as the local suite.

```text
#17 head 2934bdc  reference-integrity          35847291093  SUCCESS
                  phase3-population            35847290945  SUCCESS
                  phase4-spectral-likelihood   35847291237  SUCCESS
                  phase5-catalog-dark-bright   35847291392  SUCCESS
                  phase6-inference-io          35847291210  SUCCESS
                  phase6-runtime-guards        35847291062  SUCCESS
                  phase6t-sampler-dispatch     35847291154  SUCCESS
                  phase7f3-angular-wiring      35847291115  SUCCESS
                  phase8-regression            35847291081  SUCCESS
                  phase8d-final-freeze         35847291065  SUCCESS  wheel mode: 11 passed
                  real-backends                35847290973  SUCCESS

#18 head 42fda95  reference-integrity          35847292464  SUCCESS
                  phase3-population            35847292334  SUCCESS
                  phase4-spectral-likelihood   35847292401  SUCCESS
                  phase5-catalog-dark-bright   35847292315  SUCCESS
                  phase6-inference-io          35847292354  SUCCESS
                  phase6-runtime-guards        35847292526  SUCCESS
                  phase6t-sampler-dispatch     35847292295  SUCCESS
                  phase7f3-angular-wiring      35847292430  SUCCESS
                  phase8-regression            35847292237  SUCCESS
                  phase8d-final-freeze         35847292280  SUCCESS
                  real-backends                35847292262  SUCCESS

#19 head 628e104  reference-integrity          35847296860  SUCCESS
                  phase3-population            35847296921  SUCCESS
                  phase4-spectral-likelihood   35847296782  SUCCESS
                  phase5-catalog-dark-bright   35847296589  SUCCESS
                  phase6-inference-io          35847296633  SUCCESS
                  phase6-runtime-guards        35847297067  SUCCESS
                  phase6t-sampler-dispatch     35847296986  SUCCESS
                  phase7f3-angular-wiring      35847296724  SUCCESS
                  phase8-regression            35847296889  SUCCESS
                  phase8d-final-freeze         35847296621  SUCCESS
                  real-backends                35847296655  SUCCESS

#20 head 828ad3b  reference-integrity          35847298573  SUCCESS
                  phase3-population            35847298668  SUCCESS
                  phase4-spectral-likelihood   35847298375  SUCCESS
                  phase5-catalog-dark-bright   35847298478  SUCCESS
                  phase6-inference-io          35847298614  SUCCESS
                  phase6-runtime-guards        35847298374  SUCCESS
                  phase6t-sampler-dispatch     35847298308  SUCCESS
                  phase7f3-angular-wiring      35847298557  SUCCESS
                  phase8-regression            35847298494  SUCCESS
                  phase8d-final-freeze         35847298675  SUCCESS
                  real-backends                35847298595  SUCCESS

#21 head 51f3179  reference-integrity          35847301516  SUCCESS
                  phase3-population            35847301648  SUCCESS
                  phase4-spectral-likelihood   35847301622  SUCCESS
                  phase5-catalog-dark-bright   35847301676  SUCCESS
                  phase6-inference-io          35847301837  SUCCESS
                  phase6-runtime-guards        35847301873  SUCCESS
                  phase6t-sampler-dispatch     35847301907  SUCCESS
                  phase7f3-angular-wiring      35847301621  SUCCESS
                  phase8-regression            35847301482  SUCCESS
                  phase8d-final-freeze         35847301771  SUCCESS
                  real-backends                35847301768  SUCCESS

#22 head 519100d  reference-integrity          35847304803  SUCCESS
                  phase3-population            35847304913  SUCCESS
                  phase4-spectral-likelihood   35847304727  SUCCESS
                  phase5-catalog-dark-bright   35847304997  SUCCESS
                  phase6-inference-io          35847304826  SUCCESS
                  phase6-runtime-guards        35847304939  SUCCESS
                  phase6t-sampler-dispatch     35847304943  SUCCESS
                  phase7f3-angular-wiring      35847304926  SUCCESS
                  phase8-regression            35847304820  SUCCESS  759 passed, 1 skipped
                  phase8d-final-freeze         35847304863  SUCCESS
                  real-backends                35847304797  SUCCESS  75 passed, 0 skipped

#23 head e7875c1  reference-integrity          35847620658  SUCCESS
                  phase3-population            35847620759  SUCCESS
                  phase4-spectral-likelihood   35847620863  SUCCESS
                  phase5-catalog-dark-bright   35847620663  SUCCESS
                  phase6-inference-io          35847620695  SUCCESS
                  phase6-runtime-guards        35847620823  SUCCESS
                  phase6t-sampler-dispatch     35847620675  SUCCESS
                  phase7f3-angular-wiring      35847620716  SUCCESS
                  phase8-regression            35847620737  SUCCESS  759 passed, 1 skipped
                  phase8d-final-freeze         35847620891  SUCCESS
                  real-backends                35847620756  SUCCESS  75 passed, 0 skipped
```

## Pin decision

The Phase-12C production pin `8bf2bec53ff7b557c6b930d4044008cb72008f61` stays
the active production core pin. The DESI P12.4 target uses a fixed parametric
population, which the one numerics change above does not touch, but the
production consumer must not move to a post-12D core until:

1. #17 through #23 are merged in order and their merge SHAs and trees recorded;
2. the push-triggered workflows, including the Phase-5 legacy parity workflow,
   `phase8d-final-freeze` and `real-backends`, are green on the merged head;
3. this record is promoted to an acceptance record with a new core pin.

The consumer's adoption of the Phase-12C pin `8bf2bec5` is separate and is not
changed by this record.

## Left open on purpose

- `real-backends.yml` pipes pytest into `tee` without `pipefail`, so a failing
  test there does not by itself fail that job. Same class of bug as the one
  fixed in the release workflow; it needs its own small fix.
- Only the names of the package-root API are frozen, not their signatures; the
  example checks are smoke checks, not numerical anchors.
- The frozen reference's check that every source directory is a package the
  build finds was not ported.
- Run fingerprints: a `str` subclass (for example a `str` Enum member) is hashed
  through its `__str__`; a caller's own `{"__float__": ...}` or
  `{"__ndarray__": ...}` dict collides with the internal tags. Nothing in core
  triggers either, and `infer()` does not use the resume gate.
- The sampler-dispatch probe's checkpoint-plan stub always reports
  checkpointing off, so the checkpointing branches are covered only by their
  own gates. The angular probe runs a single PE block.
- `selection_budget_audit` ignores `z_depth` like the frozen function.
- Making `real-backends` a required check is a branch-protection setting.

## Verdict

**Not accepted.** This is the package-change contract for the deferred
follow-up. Acceptance requires the ordered merges, the recorded merge SHAs and
trees, and green push-triggered gates on the merged head, listed under the pin
decision.
