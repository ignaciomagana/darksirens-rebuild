# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

The legacy repository remained read-only throughout reconstruction. Numerical
behavior was frozen with deterministic reference probes before companion
production ports were accepted.

## Reconstruction state

**RECONSTRUCTION COMPLETE / PHASES 08–11 FROZEN**

The historical reconstruction freeze is unchanged:

```text
darksirens-core
  reconstruction freeze: af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
  tree:                  0608b75ff5c142bfba0fc15a4fad79e0fee1fa74
  phase:                 08 — COMPLETE / FROZEN

darksirens-surveys
  main:                  f027aef02d342041ce7259cdbf47fe689e6462f2
  phase:                 09 — COMPLETE / FROZEN

darksirens-lss
  main:                  3429bb2f420239bc731cc9e73e50bf5351181c14
  phase:                 10 — COMPLETE / FROZEN

darksirens-lensing
  main:                  43c450742b733d7b8d938116021e8ca52a31226e
  tree:                  9d79f113d5bf216c90beb13947d190c7da5bb9ca
  phase:                 11 — COMPLETE / FROZEN
```

No reconstruction production slice is active. Post-reconstruction science is
tracked separately and may use explicitly accepted extensions of the frozen
core without rewriting the Phase-08 reconstruction record.

## Dependency ownership

The ownership direction remains one-way:

```text
surveys  -> core contracts
lss      -> core contracts
lensing  -> core contracts

core     -X-> surveys
core     -X-> lss
core     -X-> lensing
lss      -X-> surveys at runtime
lensing  -X-> surveys/lss at runtime
```

Core owns cosmology, ordinary population models, ordinary GW likelihood and
selection machinery, common runtime records, parameter plans, and sampler
execution. Companion repositories own only their domain-specific data adapters,
state, likelihood extensions, selection extensions, and composition seams.

## Reconstruction acceptance ledger

```text
08 core:     phases/08_phase_integration.md
09 surveys:  phases/09S6_final_surveys_freeze.md
10 LSS:      phases/10L8_final_lss_freeze.md
11 lensing:  phases/11L8_full_parity_freeze.md
```

Final Phase-11 lensing acceptance remained:

```text
final merge/main:          43c450742b733d7b8d938116021e8ca52a31226e
final tree:                9d79f113d5bf216c90beb13947d190c7da5bb9ca
exact-core L8 acceptance:  34803362718 / 103850299537 — SUCCESS
post-merge main CI:        34803573222 / 103850905904 — SUCCESS
record:                    phases/11L8_full_parity_freeze.md
```

The mature lensed injection campaign still contains detection membership
rendered at a fixed campaign cosmology. Variable-cosmology strong-lensing work
therefore remains fail-closed until a cosmology-dependent detection rendering or
emulator is implemented. The frozen L4 pair likelihood also remains unmarked in
arrival time.

## Post-reconstruction Phase 12 — first production consumer

Status: **PHASE 12C CORE ACCEPTED / PHASE 12D ACCEPTED THROUGH 12H (2026-09-28) / PHASE 12E CAMPAIGN RECORD MERGED AS PROPOSED (d6b63f7) / PHASE 12F CONTRACT CHANGE PROPOSED, NOT ACCEPTED (consumer change merged without contract CI, 2026-09-27; acceptance status record drafted) / PHASE 12H CORE REPIN TO a46dec7 ACCEPTED (owner, 2026-09-28; consumer on it since e72c24a) / PHASE 12I MASK RULE ACCEPTED (2026-09-28; resolves the input-stage stop on 56 occupied pixels with f_p = 0)**

**No new H0 result is accepted yet.**

Phase 12 began with a generic composition extension (12A), then a final pre-run
audit found that the first P12.4 consumer did not implement the intended DESI
footprint or field sky-weighting convention. Numerical execution was blocked
before an H0 run. Phase 12B corrects and supersedes that pre-correction target.

### Active Phase-12 package pins

```text
darksirens-core     a46dec7929c7343fef61e68b7c0c5f2c205daa0e   (Phase 12H, accepted 2026-09-28; the consumer pins it since e72c24a)
                    supersedes 8bf2bec53ff7b557c6b930d4044008cb72008f61 (Phase 12C)
darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e
```

Phase 12A remains historical accepted provenance:

```text
record:     phases/12A_completion_curve_composition_acceptance.md
core merge: 8b9dc64629cf11838a9fc1de233e46b91082caf7
post-merge: 34807249732 / 103861422867 — SUCCESS
```

### Phase 12B accepted core

```text
core PR:              #9
accepted PR head:     efaf98d611549c028948a459f1d65487ddd4f744
merge/main:           bb4812dc2bf49fe7f4412ba797621b668ccc26a5
tree:                 ff29b5b67029889e27a25dd4b6c33d59d264d3d4
Phase-8 regression:   34872949605 — SUCCESS
Phase-5 legacy parity:34872949824 — SUCCESS
post-merge integrity: 34873970805 — SUCCESS
```

The Phase-12B core addition is generic and additive: per-row survey-fraction
magnitude-selection composition and a separate field incomplete-catalog
host-density numerator. The reconstructed conditional path was not modified.

### Phase 12B accepted consumer

```text
repository:            ignaciomagana/desi_darksirens_selection
pre-correction lockout merge:
  c42ddfed9bad8dbc0702eec957470dd6d7b71a46
corrected PR:          #8
final accepted head:   ebe6f1308b87183b05c25fb2af168e0069e263a4
final-head CI:         34894171602 / 104143891610 — SUCCESS
merge/main:            2668ae7e2eb9325910e1a8bec9b7228003cb4942
tree:                  6297fce9eee6679ebaed10bb3a081d46aaace9bc
post-merge CI:         34894224773 / 104144072068 — SUCCESS
control record:        phases/12B_field_footprint_acceptance.md
```

The accepted DESI target now uses:

```text
catalog sky weighting: field
per-row completeness:  C_p(z) = f_p Cbar(z)
off-footprint rule:    f_p = 0 -> dN_miss = dN_exp
event policy:          full 259-event sample; no DESI-support cut
Q/LSS correction:      off
```

The footprint map is an explicit input and is loaded/degraded through the frozen
surveys seam. Off-footprint PE and injection samples remain in the analysis;
they are not cut. Occupied catalog pixels marked uncovered fail closed.

The repository execution marker admits this corrected chain for execution only;
it does not certify a posterior.

### Active production chain

```text
P12.1 frozen environment
  -> standardized DESI input + footprint fingerprint
  -> P12.2 pre-inference diagnostics
  -> P12.2b footprint diagnostics
  -> P12.3 fixed-population spectral-siren baseline
  -> P12.4 fixed-population DESI field inference
```

Every stage fails closed. Direct P12.4 invocation independently rechecks the
Phase-12B marker, exact package pins, live footprint SHA256, P12.2b provenance,
P12.3 package provenance, and the hard PE+selection Monte-Carlo reliability
gate.

### Phase 12C — core review follow-up (ACCEPTED / MERGED)

```text
contract record:    phases/12C_core_review_followup_contract.md
acceptance record:  phases/12C_core_review_followup_acceptance.md
core PRs merged:    #10, #16, #12, #13, #14, #15 (in order, squash)
merge/main:         8bf2bec53ff7b557c6b930d4044008cb72008f61
tree:               18b3bf93ad506fb289e080160cbb20cbb03d58d0
exact-head matrix:  green on every accepted head (34-36 workflows each)
Phase-8 regression: 714 passed, 1 skipped; real-backends: 75 passed, 0 skipped
```

Guards and independent anchors from the adversarial parity review, plus three
deliberate numerics changes (complete-catalog empty-row default back to the
frozen `zero`; GP z- and m1-conditional normalisers corrected; healpy-exact
pixelisation). The DESI P12.4 fixed-population target is untouched by the
numerics changes. The consumer must adopt the new core pin (a consumer PR under
its contract CI) and regenerate P12.1-P12.3 provenance before P12.4 runs.

### Phase 12C consumer pin adoption (MERGED WITHOUT CONTRACT CI)

```text
repository:            ignaciomagana/desi_darksirens_selection
consumer PR:           #9 (no consumer code change; pins, marker, tests, runbook)
merged head:           3c8aa4d7c1afe039e8ee6aa0deeff3a889efde03
merge/main:            cc030f023f5fdee00caeada3af02566865dfcc72
tree:                  2048b624725856ab61b45911d235a6edbf5e2911
contract CI:           DID NOT RUN (private repo, Actions billing block; every run
                       on the branch and on main ended with zero steps)
local stand-in:        job commands on the merged tree, Python 3.12.14,
                       numpy 2.5.3, pytest 8.4.2: compileall clean,
                       36 passed, 1 skipped by design
```

Merged on the owner's decision on 2026-09-24. The `phase12-contract` workflow
must be re-run on consumer `main` once Actions is unblocked before the CI line
above can be replaced by a run ID. P12.1 will still verify the installed pins
exactly at run time.

### Phase 12D — core deferred follow-up (ACCEPTED THROUGH 12H, 2026-09-28)

```text
contract record:    phases/12D_core_deferred_followup_contract.md
core PRs merged:    #17 through #23 (in order, squash), then #24
core main:          c3bc005b41be7f24e2baa202bafa717f2237f1b3 (tree ad4ab934) after #23
                    88004d96ddeee37c47abc1d2dfd1c6fc3c203dfd (tree 00e4b9e5) after #24
push gates on c3bc005b: reference-integrity 35898821948, real-backends 35898822004,
                    phase8d-release-contract 35898822026 — all SUCCESS
push gates on 88004d96: reference-integrity 35954407573, real-backends 35954407608,
                    phase8d-release-contract 35954407601 — all SUCCESS
production pin:     UNCHANGED, 8bf2bec5
```

Conditions 1 and 2 of the record's pin decision are met; condition 3 is met
by the Phase 12H pin `a46dec7`, which contains #17 through #24. The draft
`phases/12D_core_deferred_followup_acceptance.md` records acceptance through
12H (owner sign-off 2026-09-28). Core #24 closes the
record's first "left open" item: the `real-backends` job now fails when pytest
fails behind `tee`. A post-12D pin, if adopted, should be `88004d96` or later.

### Phase 12E — A100 benchmark campaign record (PROPOSED RECORD / MERGED AS PROPOSED d6b63f7 / NOT ACCEPTED)

```text
record:        phases/12E_a100_benchmark_campaign_record.md (on main since d6b63f7, 2026-09-27)
control PR:    darksirens-rebuild #10, merged as proposed d6b63f7 (2026-09-27)
production pin: UNCHANGED, 8bf2bec5
```

The campaign compared darksirens-core with the frozen darksirens on a Jetstream2
A100, from fixed-coordinate kernels to full sampler runs on the real GWTC
product. It found parity everywhere it compared the codes. It also found that
the P12.4 hard guard at cap 1.0 admits no finite likelihood on the campaign's
real product. On the owner's decision, TinyNS is considered broken until
ignaciomagana/darksirens#462 is debugged. The record was merged into this repository's `main` as a proposed record (d6b63f7, 2026-09-27); it is not accepted and the production pin is unchanged.

### Phase 12F — selection guard and GW input products (PROPOSED CONTRACT CHANGE / NOT ACCEPTED)

Acceptance status record: `phases/12F_selection_guard_and_gwcat_products_acceptance.md`
(2026-09-27): gate 1 merged without contract CI on the owner's decision, gate 2
met by consuming the pinned reference build (owner, 2026-09-28), gates 3 to 6 open; the first
production execution passed P12.1 and failed closed at the input stage (56
occupied nside-64 pixels with f_p = 0, 941 galaxies, all children fully
masked, LMC/SMC region), which needs a scientific contract before P12.2.

```text
record:           phases/12F_selection_guard_and_gwcat_products_contract.md
owner decisions:  2026-09-26
guard:            hard, max_likelihood_variance 1.0  ->  soft, max_likelihood_variance 10
                  (P12.2 probes, P12.3 grid, P12.4)
GW products:      gwcat-1.0 PE + gwcat-selection-1.0 (chi_eff swap)  ->
                  gwcat 8f9e2f1: chieff PE (gwcat-pe-2.0) + chieff_reference
                  selection (gwcat-selection-2.0), strict validation 84/84
reference build:  PE  a24a5903a7f7da6fdcdee22f58c4c0efa76447f2cf4d581dc19ec3e60ce478a5
                  sel bab92babf2d6958a6ed04ee536c44fa533f5c4822ca9a22f934347a089d21ab5
sampler:          P12.4 TinyNS bounded_multi -> dynesty (TinyNS under debug, darksirens#462)
production pin:   UNCHANGED, 8bf2bec5; no core change required
```

Why:
- P12.4's own GW inputs fail the accepted hard guard at all 14 P12.2 probes. At
  H0 = 67.74, N_eff is 46,306 against 78,467 needed. By the consumer's own code
  the chain stops at P12.2.
- The guard study found that caps 10 and 20 leave the posteriors unchanged,
  that cap 5 cuts them, and that the hard guard at cap 1 would need about 14-20
  million detected injections.
- The chi_eff-swap selection file gives 3.6 times the N_eff of the reference
  reweighting on identical injection rows. The O4ab injected spins are not
  isotropic, so the swap does not hold for them.

The acceptance criterion is re-expressed. The soft cap-10 penalty must be
exactly zero, as measured, at the P12.4 anchor, the posterior mean and the
posterior median, at the P12.3 grid maximum and grid posterior mean, and at the
P12.2 anchor H0 = 67.74. The soft and hard terms are compared in one float64
arithmetic. Probes and grid points with a nonzero penalty are reported, not
failed.

Unchanged: the population preset, the DESI calibration block, the
magnitude-selection model, the footprint, the catalog, the sky weighting, the
event policy and the pins.

Acceptance requires, in the consumer and in this repository:
- the consumer PR implementing 12F (desi_darksirens_selection PR #11) merged
  under contract CI, with a green run on the merged main. Status 2026-09-27:
  the owner decided the consumer repository stays private (private material),
  so PR #11, the 12G PR #12, the 12H repin PR #14 and the script entry-point
  PR #13 were squash-merged without contract CI (consumer `main` `53ed335`,
  tree of `52389c6` checked against each PR head); the stand-ins on that
  `main` are the job's own commands in a matching Python 3.12 environment
  (250 passed, 7 skipped) and the full suite in the frozen `a46dec7`
  environment (281 passed). The green contract run on `main` is still owed
  once Actions is unblocked. Consumer PR #10 (jit the P12.4 target) was
  merged on 2026-09-26 as `5efa8da` without contract CI, on the owner's
  decision;
- the products rebuilt and validated against the reference build;
- P12.1-P12.3 regenerated;
- a fixed-coordinate check that the DESI field target's soft cap-10 total is
  finite and unpenalised at the calibration point;
- promotion of the record.

### Phase 12H — core repin to a46dec7 (ACCEPTED 2026-09-28 / CONSUMER ON IT / CONTRACT CI WAIVED)

```text
record:          phases/12H_core_repin_a46dec7_acceptance.md (accepted by the owner, 2026-09-28)
core pin:        a46dec7929c7343fef61e68b7c0c5f2c205daa0e (tree 6cfb7198), contains #17-#30
push gates:      reference-integrity 36336267952, real-backends 36336267935,
                 phase8d-release-contract 36336267895 — all SUCCESS
consumer:        PR #14 merged as e72c24a (2026-09-27), main 53ed335, without contract CI
                 (private repository, Actions billing; owner's decision)
core protection: main requires the real-backends check (`backends`), linear history (2026-09-27)
P12.1 under it:  PASS (Hildafs Slurm 1340521); input stage failed closed on the footprint rule
```

### Phase 12I — catalog rows in fully masked native pixels (ACCEPTED CONTRACT CHANGE, 2026-09-28)

```text
record:        phases/12I_masked_pixel_catalog_rows_contract.md
trigger:       first production input stage (2026-09-27) failed closed: 56 occupied nside-64 pixels with f_p = 0
               (941 galaxies, all native children fully masked, LMC/SMC region)
rule:          remove rows whose native nside-128 pixel has f_p = 0 (2,287 rows; 22,787,566 -> 22,785,279)
owner:         accepted the rule 2026-09-28
consumer PR:   desi_darksirens_selection #15
evidence run:  P12.1-P12.3 PASS on the PR branch, Hildafs Slurm 1340556; to be repeated from merged main
```

### Phase 12J — single-pass likelihood sums (ACCEPTED RUN-SETTING CHANGE, 2026-09-28)

```text
record:       phases/12J_single_pass_blocks_contract.md
measurement:  Hildafs CPU node, Slurm 1340541 (2026-09-27): single pass = one block, 1.40x faster than
              blocks 131072/32, 4e-16 relative difference, +12 GiB working memory (fits the Hildafs GPUs)
owner:        accepted 2026-09-28
consumer PR:  desi_darksirens_selection #16 (merged after #15)
```

### Phase 12K — CUDA backend for GPU runs (ACCEPTED ENVIRONMENT CHANGE, 2026-09-28)

```text
record:       phases/12K_cuda_environment_contract.md
change:       jax-cuda12-plugin/pjrt 0.4.34 + NVIDIA CUDA 12.3 wheels on top of the frozen stack; nothing else
device:       Hildafs MIKO H100 NVL 96 GB, driver 545.23.08 (CUDA 12.3)
consumer:     requirements-cuda12.txt (desi_darksirens_selection)
gates:        GPU vs CPU at the P12.2 calibration point 6.5e-16 / 3.7e-15 (met); P12.4 under 12F gate 7 (met), 2026-09-29
```

### Phase 12L — soft selection guard at cap 20 (ACCEPTED CONTRACT CHANGE, 2026-09-29)

```text
record:    phases/12L_selection_guard_cap_20_contract.md
trigger:   first P12.4 run (MIKO H100, consumer dc9c8a3) stopped before sampling: anchor H0 = 64.5 penalised at cap 10
           (N_eff 7,310 = 1.07 x threshold); the field target is penalised below H0 ~ 63 at cap 10, 29% of the P12.3 mass
change:    max_likelihood_variance 10 -> 20 in P12.2, P12.3 and P12.4 (soft guard unchanged otherwise)
evidence:  CPU P12.1-P12.3 at cap 10 from consumer main dc9c8a3 PASS (Hildafs Slurm 1346044, 2026-09-29)
```

### First P12.4 production run (2026-09-29): PASS, pipeline result

```text
chain:     consumer c86629b, core a46dec7, 12K CUDA backend, MIKO H100; P12.1-P12.4 all PASS (30 min)
P12.4:     dynesty converged (final dlogz 0.0999), unpenalised at anchor, mean and median (cap 20)
H0:        median 71.07, 68% [66.29, 75.13] (pipeline result, not a result of record)
CPU check: P12.1-P12.3 at cap 10 from dc9c8a3 PASS (Slurm 1346044); calibration probe bitwise the 12F reference
records:   evidence in phases/12F_selection_guard_and_gwcat_products_acceptance.md ("Production-path evidence")
```

### Next admissible action

As of 2026-09-29 the chain passes end to end on the production assets:
P12.1 to P12.4 under core `a46dec7`, with Phases 12I (catalog mask rule), 12J
(single-pass sums), 12K (CUDA backend) and 12L (soft guard at cap 20). What
remains:

1. robustness of the P12.4 posterior to the guard cap and the sampler seed:
   done 2026-09-29. Caps 15 and 30 and seeds 23 and 24 move the H0 median by
   at most 0.05 (0.01 sd); see `phases/12L_selection_guard_cap_20_contract.md`,
   "Robustness";
2. the owner accepts or rejects the P12.4 posterior as a result of record, and
   promotes Phase 12F (its gate 6);
3. the green contract run on the merged consumer `main`, owed once GitHub
   Actions is unblocked (the repository stays private);
4. only then: freeze the P12.1 to P12.4 numerical provenance, produce plots,
   and begin the fixed-population robustness matrix.

The legacy footprint-map caveat remains explicit: Phase 12B preserves the
mature `masked_frac` product and does not claim that its source-count-based
construction is an unbiased geometric area estimator.
