# Phase 3 report — population models

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
working branch:    rebuild/phase3-population
current branch SHA: df4f17ccca5e6777286838f5340c10af1f845254
```

## Status

IN PROGRESS. Do not advance to Phase 4 until the full Phase-3 gate is green.

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

## Implemented so far

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

The first full scientific run reached the population block and reported:

```text
Phase-2 regressions: 14 passed
population block:    86 passed, 14 failed, 1 skipped
```

All 14 failures were ownership leaks rather than population numerical failures:

```text
4  tests called darksirens.inference.prior.make_prior_transform
10 tests called the old main/lensing CLI normalization-grid wiring
```

The underlying population normalization diagnostics in the same run passed,
including:

```text
pairing grid 2048: max |Delta log p_pop| = 2.937e-05
pairing grid 4096: max |Delta log p_pop| = 7.121e-06
pairing grid 8192: max |Delta log p_pop| = 1.717e-06
median at 8192:                     2.540e-09
zero-pattern mismatches in support-edge sweeps: 0
```

These mixed-owner tests are now separated from the Phase-3 gate rather than
pulling inference/CLI code into the population package.

## Acceptance gate

Phase 3 is complete only when one permanent `phase3-population` workflow run
passes all of the following after the final scientific commit:

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

## Ownership decisions made in this phase

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

## Next action

Run the revised permanent Phase-3 gate from commit
`df4f17ccca5e6777286838f5340c10af1f845254`, fix any genuine population or
parity failures, and remain in Phase 3 until the entire workflow is green.
