# Phase 3 report — population models

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
working branch:    rebuild/phase3-population
pull request:      ignaciomagana/darksirens-core#2
current branch SHA: 2461954c47df587ed70f711769a42779775be692
```

## Status

PR VALIDATION IN PROGRESS. The population science/parity gate passed on the
previous clean head, but PR #2 exposed three test-only F401 lint errors in the
older Phase-2 workflow. Those imports were removed without touching scientific
source or tolerance. The complete Phase-3 and PR gate must pass again on current
head `2461954c47df587ed70f711769a42779775be692` before merge. Do not begin Phase 4.

## Scope

Move the population-density system from legacy `darksirens.gw.populations` to
`darksirens.population` without changing accepted scientific behavior.

Phase 3 owns population densities, model composition, registry and grammar,
fixed GWTC parameter sets, component-spin models, GP population models, and
population normalization machinery. It does not own sampler proposal/PPC
helpers, the hierarchical inference prior transform, or application/lensing
CLI wiring.

## Implemented

- migrated parametric models, mixtures/components, component-spin,
  grammar/registry, fixed fiducials, GP models, and population numerical helpers;
- exposed the stable registry API from `darksirens.population`;
- rewired population internals to reconstructed cosmology/grid owners;
- kept `tinygp` optional and lazy for ordinary population imports;
- added pinned-legacy population goldens and physics tests;
- added a separate-process pinned-legacy/new population probe;
- added a population-owned simplex-prior test independent of the future
  inference prior-transform implementation;
- separated genuine population-support validation from legacy flow/PPC sampling
  and old application/lensing CLI wiring.

## Validation history

The first broad copied-test run gave:

```text
Phase-2 regressions: 14 passed
population block:    86 passed, 14 failed, 1 skipped
```

All 14 failures were cross-phase ownership leaks: four depended on the future
`darksirens.inference.prior.make_prior_transform` and ten depended on the old
main/lensing CLI grid wiring. No population numerical failure was present.
The inference-dependent stick-prior checks were replaced with a direct
population-owned prior contract; CLI-only assertions were removed from this
phase for later validation by their actual owner.

A later probe-only failure came from assuming the reconstructed object layout
(`model.spin_component`) on the pinned legacy model, where spin components can
live on the mixture. The probe now feature-detects both layouts. Scientific
source and tolerances were unchanged.

## First fully clean scientific acceptance

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

The only full-suite skip is the explicit golden-regeneration guard.

Representative normalization diagnostics:

```text
pairing grid 2048: max |Delta log p_pop| = 2.937e-05, median = 4.077e-08
pairing grid 4096: max |Delta log p_pop| = 7.121e-06, median = 1.009e-08
pairing grid 8192: max |Delta log p_pop| = 1.717e-06, median = 2.540e-09
support-edge zero-pattern mismatches: 0
```

## PR #2 review finding

PR #2 was opened at the accepted scientific head. `reference-integrity` passed,
but the older `phase2-foundation` PR workflow failed at its broader Ruff command
because three migrated legacy test imports were unused:

```text
tests/test_component_spin_model.py: ComponentSpinModel
tests/test_pairing_norm_grid.py: get_q_grid
tests/test_population_grammar.py: ModelNameError
```

This was test hygiene, not a physics or numerical failure. A one-shot workflow
ran `ruff check tests --select F401 --fix` and changed only those three migrated
test files. Its fix commit was:

```text
29606d1e67a421da0ebddfde8c2c60246def2ade
```

The one-shot workflow was then deleted. Current candidate head is:

```text
2461954c47df587ed70f711769a42779775be692
```

Because the branch head changed, all prior acceptance evidence is treated as
historical. Both the full Phase-3 gate and all PR-triggered workflows must be
green at this exact head before merge.

## Cleanup

Temporary bootstrap, patch, cleanup, and lint-fix workflows/marker files and the
stale dependency report have been removed. The permanent
`phase3-population.yml` remains and contains no `-k` deselection. It explicitly
runs a plain:

```text
python -m pytest -q
```

## Accepted ownership decisions

1. Legacy `population.sampling` is not part of the population-density core; its
   proposal/PPC/flow functionality moves with the later inference/surrogate layer.
2. Application CLI wiring is not a population-model contract.
3. Mixture-weight priors are population contracts and are tested directly at the
   population layer without importing the future inference transform.
4. Cross-version parity probes feature-detect capabilities rather than requiring
   identical internal object layouts.
5. No scientific or numerical tolerance is relaxed to obtain acceptance.

## Next action

Require all branch and PR checks to pass at
`2461954c47df587ed70f711769a42779775be692`. Review the final PR diff and merge
only at that head. Then record the squash-merge/core `main` SHA here and mark
Phase 3 COMPLETE before Phase 4 begins.
