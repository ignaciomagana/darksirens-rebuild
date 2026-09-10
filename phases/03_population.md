# Phase 3 report — population models

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
working branch:    rebuild/phase3-population
current branch SHA: c204c1dd7281c4099b3e86098b912e3778f15b86
```

## Status

IN PROGRESS. The scientific/parity gate has passed once. Do not advance to
Phase 4 until the same permanent gate passes again on the cleaned branch.

## Scope

Move the population-density system from the legacy `darksirens.gw.populations`
namespace into `darksirens.population` without changing accepted scientific
behavior. This phase owns population densities, model composition, registry and
grammar, fixed GWTC parameter sets, component-spin models, GP population models,
and population normalization machinery.

It does not own sampler proposal/PPC helpers, the hierarchical inference prior
transform, the application CLI, or lensing CLI wiring. Those are validated in
their later owner phases rather than being reintroduced here to satisfy mixed
legacy tests.

## Implemented

- migrated `base.py`, `components.py`, `mixtures.py`, `parametric.py`,
  `component_spin.py`, `blueprints.py`, `grammar.py`, `registry.py`, `gp.py`,
  and population numerical utilities;
- rewired internal imports to the reconstructed cosmology/grid owners;
- exposed the stable registry API from `darksirens.population`;
- kept `tinygp` optional and lazy on ordinary `darksirens.population` import;
- declared the GP dependency as an optional package extra;
- imported pinned legacy population goldens and physics tests;
- added a separate-process legacy/new population probe;
- added a population-owned simplex-prior test independent of the future
  `darksirens.inference.prior` implementation;
- split true population-support validation away from the old flow/PPC sampling
  helpers.

## Validation history

The first broad copied-test run reported:

```text
Phase-2 regressions: 14 passed
population block:    86 passed, 14 failed, 1 skipped
```

All 14 failures were ownership leaks rather than population numerical failures:

```text
4  tests called darksirens.inference.prior.make_prior_transform
10 tests called the old main/lensing CLI normalization-grid wiring
```

These mixed-owner tests were separated rather than pulling inference/CLI code
back into the population package.

A later permanent run (`34436206907`) passed every reconstructed scientific test
stage and then exposed a bug in the newly written legacy parity probe: it assumed
all `PopulationModel` objects exposed `model.spin_component` directly. The
pinned legacy generic model stores spin components on its mixture. The probe was
fixed to feature-detect direct and mixture-owned component-spin implementations.
No scientific source or tolerance changed.

### First complete permanent gate

```text
workflow run: 34436516606
job:          102742588084
branch SHA:   a934f5c3700d53ebd11c84ef3e20d6fd40e86fe7
status:       SUCCESS
```

Results:

```text
ruff F/E9:                                  PASS
Phase-2 regressions:                        14 passed
population registry golden:                 13 passed, 1 regen-only skip
population grammar:                         34 passed, 4 cross-phase deselected
population simplex-prior contract:          4 passed
component-spin:                             9 passed
pairing normalization/support:              19 passed, 10 CLI tests deselected
population model support:                   3 passed
gradient NaN safety:                        8 passed
GP population tests:                        21 passed
legacy population probe:                    PASS
reconstructed population probe:             PASS
legacy/new max_abs:                         0.000e+00
legacy/new max_rel:                         0.000e+00
comparison tolerance:                       rtol=1.0e-12
ordinary population import tinygp-lazy:     PASS
```

Representative normalization diagnostics retained from the legacy tests:

```text
pairing grid 2048: max |Delta log p_pop| = 2.937e-05
pairing grid 4096: max |Delta log p_pop| = 7.121e-06
pairing grid 8192: max |Delta log p_pop| = 1.717e-06
median at 8192:                     2.540e-09
zero-pattern mismatches in support-edge sweeps: 0
```

The legacy warnings about archived curated fixed-population vectors lying
outside the current sampled prior were emitted identically by both probes and
are preserved behavior, not a reconstruction discrepancy.

## Branch cleanup before acceptance

After the first complete pass, the temporary reconstruction scaffolding was
removed in one commit:

```text
cleanup commit: c204c1dd7281c4099b3e86098b912e3778f15b86
```

Removed:

```text
.github/workflows/phase3-bootstrap.yml
.github/workflows/phase3-extra-tests-bootstrap.yml
.github/workflows/phase3-patch.yml
.github/workflows/phase3-test-bootstrap.yml
.phase3_bootstrapped
.phase3_extra_tests_bootstrapped
.phase3_patched
.phase3_tests_bootstrapped
```

The permanent `phase3-population.yml` workflow remains. A second full pass on
this cleaned branch is required before Phase 3 is accepted.

## Acceptance gate

Phase 3 is complete only when the cleaned branch passes:

```text
ruff F/E9: PASS
Phase-2 regressions: PASS
population registry/grammar: PASS
population simplex-prior contract: PASS
component-spin: PASS
normalization-grid and support tests: PASS
GP population tests: PASS
legacy population probe: PASS
reconstructed population probe: PASS
legacy/new numerical comparison at rtol=1e-12: PASS
ordinary population import leaves tinygp unloaded: PASS
```

No tolerance is to be relaxed to obtain acceptance.

## Ownership decisions

1. `population.sampling` from the legacy tree is not part of the population
   density core. Its truncated-normal/proposal/PPC functionality moves with the
   inference/surrogate layer later.
2. CLI tests are not population tests. The core owns the grid sizing and
   normalization math; application wiring will be retested when the new compact
   CLI exists.
3. The mixture-weight prior distribution is a population contract, but its
   correctness can be tested directly from the declared Beta stick priors and
   `_stick_breaking_weights`; it does not require importing the future inference
   prior-transform implementation.
4. Cross-version parity probes must feature-detect scientific capabilities and
   must not assume identical internal object layouts between the legacy and
   reconstructed packages.

## Next action

Run the permanent Phase-3 gate on clean commit
`c204c1dd7281c4099b3e86098b912e3778f15b86`. Only after that run succeeds should
the Phase-3 PR be reviewed/merged and this report be marked COMPLETE.
