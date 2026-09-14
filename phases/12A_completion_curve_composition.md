# Phase 12A — generic completion-curve composition seam

Status: **ACTIVE PACKAGE-CHANGE CONTRACT**

Parent science phase: `phases/12_production_analysis_contract.md`

## Trigger

Phase 12 reached the DESI dark-siren step after freezing the consumer bootstrap,
production input contract, pre-inference diagnostics, and fixed-population
spectral-siren baseline implementation. The reconstructed core already owns and
strictly parity-tests the generic magnitude-selection physics:

```text
GaussianMagnitudeSelection / SchechterMagnitudeSelection
selection_curve
selection_completion_curves
```

and the ordinary incomplete-catalog redshift model already owns:

```text
IncompleteCatalogPriorState
eval_incomplete_catalog_prior_state[_vmap]
```

However, `build_incomplete_catalog_prior_state()` constructs its completion
curves internally through the count-derived `completion_curves()` path. There is
no public generic constructor that combines an already-computed
`CompletionCurves` object with the ordinary catalog kernels. Consequently the
Phase-12 consumer cannot use the already-reconstructed magnitude-selection
completion curves through the accepted `make_host_density_target()` extension
seam without either duplicating core prior-state arithmetic or importing a
private implementation detail.

That duplication is forbidden by the Phase-12 architecture. This contract opens
the smallest reusable core change needed to continue.

## Frozen starting points

```text
legacy scientific reference:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

accepted core input:
  ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66

accepted surveys input:
  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2

Phase-12 consumer before this extension:
  ignaciomagana/desi_darksirens_selection@3855aa2a1e027a10c29a806a1f7a1f995ce2b086
```

The surveys, LSS, and lensing repositories remain frozen throughout Phase 12A.

## Scientific reference

The scientific semantics are already frozen by Phase 5:

1. `completion_curves()` gives the accepted ordinary count-derived missing-host
   budget.
2. `selection_completion_curves()` gives the accepted legacy `c_mode=selection`
   missing-host budget, including finite-depth behavior and the h-scaled H0
   firewall.
3. The ordinary incomplete-catalog numerator and row normalization are

   ```text
   N_obs p_cat(z|row) + dN_miss(z|row)
   Z_row = N_obs + N_miss
   ```

   with the accepted below-depth observed-count factor.

Phase 12A changes none of these equations.

## Allowed core change

Add one generic constructor in `darksirens.catalog.models`, with an API of the
form

```python
build_incomplete_catalog_prior_state_from_curves(
    cosmo,
    params,
    catalog,
    curves,
)
```

where `curves` is the existing core `CompletionCurves` contract.

Refactor the existing `build_incomplete_catalog_prior_state()` to obtain its
count-derived curves exactly as before and delegate only the state-assembly
step to the new constructor.

The new constructor must:

- build the same accepted observed-host catalog kernel state;
- apply the same finite-depth observed-count factor;
- consume `curves.dN_miss` and `curves.N_miss` without reinterpretation;
- build the identical row normalization;
- return the existing `IncompleteCatalogPriorState` type;
- introduce no survey, LSS, lensing, CLI, or fitting dependency.

It may be exported from `darksirens.catalog.models`; no package-root export is
required for Phase 12A.

## Explicit exclusions

Phase 12A must **not**:

- modify the equations in `completion_curves()` or
  `selection_completion_curves()`;
- add a `c_mode` dispatcher or `universe_model` switchboard;
- add survey-fit parsing to core;
- modify `ds.model()` or the ordinary public parameter plan;
- add selection-fit nuisance coordinates or priors to core;
- modify samplers;
- modify the accepted GW likelihood or GW selection correction;
- modify surveys/LSS/lensing repositories;
- add DESI-specific names or paths to core.

Selection-fit nuisance composition remains a Phase-12 consumer concern through
the existing `InferenceTarget` / `make_host_density_target()` seam and core's
already-supported per-coordinate normal priors.

## Acceptance gates

### 12A.1 — ordinary path identity

For deterministic fixtures spanning finite and infinite catalog depth, the
existing `build_incomplete_catalog_prior_state()` result must be numerically
identical to calling:

```python
curves = completion_curves(...)
state = build_incomplete_catalog_prior_state_from_curves(..., curves)
```

Compare every state field and evaluated log prior on fixed `(z,row)` points at
strict floating-point tolerance. The existing ordinary catalog tests and
historical reconstructed suite must remain green.

### 12A.2 — selection-curve composition

Construct accepted Gaussian and, where already supported by the frozen fixture,
Schechter magnitude-selection `CompletionCurves` using
`selection_completion_curves()`, pass them through the new constructor, and
verify:

- finite state values inside the supported domain;
- exact use of `curves.dN_miss` / `curves.N_miss` in the returned state;
- row normalization `Z=N_obs+N_miss` with the same finite-depth observed-count
  convention;
- the accepted evaluator returns finite values and normalized row densities on
  the existing redshift grid to the numerical accuracy of the existing
  catalog tests.

No new approximation is allowed.

### 12A.3 — ownership / dependency audit

The core dependency and companion-import firewall must remain unchanged. The
diff must be confined to the generic catalog-model seam, focused tests, and
acceptance workflow/documentation if needed.

### 12A.4 — downstream proof

Only after the core extension is accepted may the Phase-12 consumer repin core
and add its DESI selection-host `RedshiftModel`. That consumer must use:

- frozen surveys selection-fit output;
- frozen core `selection_completion_curves()`;
- the accepted new generic state constructor;
- frozen core `eval_incomplete_catalog_prior_state_vmap()`;
- frozen core `make_host_density_target()` / `InferenceTarget` sampling seam.

No copied incomplete-catalog state arithmetic is allowed in the consumer.

## Completion

Phase 12A is accepted only when the control repository records the accepted
core SHA/tree, focused acceptance results, broad regression result, package
diff scope, and the Phase-12 consumer has been repinned to that accepted core
head. Until then the prior core SHA remains the only accepted production core.
