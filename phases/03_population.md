# Phase 3 report — population models

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
working branch:    rebuild/phase3-population
accepted branch SHA: b4e476db727036fea9e97cdb8fb111206a5fba5d
```

## Status

VALIDATION COMPLETE. The cleaned Phase-3 branch passed the permanent acceptance
gate. Phase 3 should be marked COMPLETE after PR review and merge to core `main`.
Do not begin Phase 4 before that merge is recorded here.

## Scope

Move the population-density system from legacy `darksirens.gw.populations` to
`darksirens.population` without changing accepted scientific behavior.

Phase 3 owns population densities, model composition, registry and grammar,
fixed GWTC parameter sets, component-spin models, GP population models, and
population normalization machinery. It does not own sampler proposal/PPC
helpers, the hierarchical inference prior transform, or application/lensing
CLI wiring.

## Implemented

- migrated the parametric population models, mixtures/components, component-spin,
  grammar/registry, fixed fiducials, GP models, and population numerical helpers;
- exposed the stable registry API from `darksirens.population`;
- rewired population internals to reconstructed cosmology/grid owners;
- retained GP models in the population namespace while keeping `tinygp` optional
  and lazy for ordinary population imports;
- added pinned-legacy population goldens and physics tests;
- added a separate-process pinned-legacy/new population probe;
- added a population-owned simplex-prior test independent of the future
  `darksirens.inference.prior` implementation;
- separated genuine population-support tests from legacy flow/PPC sampling tests.

## Ownership corrections made during validation

The first broad copied-test run gave:

```text
Phase-2 regressions: 14 passed
population block:    86 passed, 14 failed, 1 skipped
```

All 14 failures were cross-phase ownership leaks:

```text
4  depended on darksirens.inference.prior.make_prior_transform
10 depended on the old main/lensing CLI grid wiring
```

No population numerical failure was present. These tests were not hidden with
permanent deselection. The inference-dependent stick-prior checks were replaced
by a direct population-owned prior contract, and the CLI-only assertions were
removed from the Phase-3 test file for later validation in their actual owner
phase.

A later parity run exposed a probe-only compatibility bug: the new probe assumed
a direct `model.spin_component`, while the pinned legacy generic population model
can keep spin components on its mixture. The probe was changed to feature-detect
both layouts. No scientific source or tolerance was changed.

## Cleanup

Before final acceptance, all temporary reconstruction scaffolding and stale
artifacts were removed, including bootstrap workflows/marker files, the temporary
cleanup workflow, and `phase3_population_dependency_report.txt`.

The permanent Phase-3 workflow was then tightened so it contains no `-k`
deselection and explicitly runs a plain full-suite:

```text
python -m pytest -q
```

## Final clean acceptance gate

```text
workflow run: 34437051423
job:          102744211460
branch SHA:   b4e476db727036fea9e97cdb8fb111206a5fba5d
status:       SUCCESS
```

Results:

```text
ruff F/E9:                                  PASS
Phase-2 regressions:                        14 passed
population registry golden:                 13 passed, 1 regen-only skip
population grammar:                         34 passed
population simplex-prior contract:          4 passed
component-spin:                             9 passed
pairing normalization/support:              19 passed
population model support:                   3 passed
gradient NaN safety:                        8 passed
GP population tests:                        21 passed
full reconstructed test suite:              125 passed, 1 regen-only skip
legacy population probe:                    PASS
reconstructed population probe:             PASS
legacy/new max_abs:                         0.000e+00
legacy/new max_rel:                         0.000e+00
comparison tolerance:                       rtol=1.0e-12
ordinary population import tinygp-lazy:     PASS
```

The only full-suite skip is the explicit golden-regeneration guard:

```text
tests/test_population_registry_golden.py: set DARKSIRENS_REGEN_GOLDEN=1 to regenerate
```

Representative normalization diagnostics retained from the legacy tests:

```text
pairing grid 2048: max |Delta log p_pop| = 2.937e-05, median = 4.077e-08
pairing grid 4096: max |Delta log p_pop| = 7.121e-06, median = 1.009e-08
pairing grid 8192: max |Delta log p_pop| = 1.717e-06, median = 2.540e-09
support-edge zero-pattern mismatches: 0
```

The archived curated fixed-population sets that lie outside the current sampled
prior still emit the same warning in both legacy and reconstructed probes. This
is preserved legacy behavior and does not contribute to the parity difference.

## Accepted ownership decisions

1. Legacy `population.sampling` is not part of the population-density core. Its
   proposal/PPC/flow functionality moves with the later inference/surrogate layer.
2. Application CLI wiring is not a population-model contract.
3. Mixture-weight priors are population contracts and are tested directly at the
   population layer without importing the future inference transform.
4. Cross-version parity probes feature-detect scientific capabilities rather than
   requiring identical internal object layouts.
5. No numerical tolerance was relaxed during Phase 3.

## Next action

Open and review the Phase-3 PR from `rebuild/phase3-population` to core `main`.
Merge only if the PR head remains
`b4e476db727036fea9e97cdb8fb111206a5fba5d` and its checks pass. Then record the
PR number and merged core `main` SHA here and mark Phase 3 COMPLETE before Phase 4.
