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

Status: **PHASE 12C CORE ACCEPTED / CONSUMER PIN UPDATE PENDING / HILDAFS NUMERICAL RUN READY AFTER THAT**

**No new H0 result is accepted yet.**

Phase 12 began with a generic composition extension (12A), then a final pre-run
audit found that the first P12.4 consumer did not implement the intended DESI
footprint or field sky-weighting convention. Numerical execution was blocked
before an H0 run. Phase 12B corrects and supersedes that pre-correction target.

### Active Phase-12 package pins

```text
darksirens-core     8bf2bec53ff7b557c6b930d4044008cb72008f61   (Phase 12C; consumer still on bb4812dc until it adopts the pin)
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

### Next admissible action

Run the chain on Hildafs from consumer main
`2668ae7e2eb9325910e1a8bec9b7228003cb4942`, using the exact package pins above
and the site-neutral Slurm/runbook already in the consumer repository.

After the run:

1. freeze P12.1/P12.2/P12.2b/P12.3/P12.4 numerical provenance;
2. accept or reject the P12.4 posterior based on the hard diagnostics;
3. only then produce plots and begin the fixed-population robustness matrix.

The legacy footprint-map caveat remains explicit: Phase 12B preserves the
mature `masked_frac` product and does not claim that its source-count-based
construction is an unbiased geometric area estimator.
