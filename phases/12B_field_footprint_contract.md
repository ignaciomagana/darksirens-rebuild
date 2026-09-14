# Phase 12B — footprint-aware field catalog estimator

Status: **ACTIVE PACKAGE-CHANGE CONTRACT / P12.4 NUMERICAL RUN BLOCKED**

Parent science phase: `phases/12_production_analysis_contract.md`

Supersedes for numerical execution only: `phases/12_fixed_population_desi_implementation.md`

## Trigger

The first Phase-12 DESI consumer reached a deployable state, but the final pre-run audit found two load-bearing estimator mismatches before any accepted numerical P12.4 result was produced.

The current consumer composes the accepted radial magnitude-selection curves through the reconstructed ordinary incomplete-catalog state. That state is scientifically valid for the reconstructed **conditional** catalog estimator, but the owner-designated GWTC-5 259-event production line used the legacy **field** estimator and a footprint-limited DESI survey.

Two corrections are therefore required before the first P12.4 numerical execution.

### B1 — footprint-aware completeness

The accepted core `selection_completion_curves()` currently applies the same radial selection curve `Cbar(z)` to every HEALPix row. A zero-galaxy row outside DESI coverage therefore receives

```text
dN_miss = (1 - Cbar) dN_exp
```

below the survey depth, which incorrectly treats an unobserved sky pixel as partially catalogued.

The legacy full-259 diagnostics explicitly measured this defect and the accepted correction:

```text
C_p(z) = f_p Cbar(z)
```

where `f_p` is the survey coverage fraction, with `f_p = 0` off footprint. The missing density is then

```text
dN_miss(p,z) = [1 - f_p Cbar(z)] dN_exp(z)
```

below the finite catalog depth and reverts to the full `dN_exp` above the depth exactly as before.

The frozen surveys companion already owns the reusable map-consumption contract:

```python
darksirens_surveys.load_selection_fraction(...)
```

which constructs `f_p = 1 - masked_frac` on covered native pixels, sets uncovered pixels to zero, and performs the frozen equal-area RING degradation. Phase 12B must reuse this owner; core must never parse the survey HDF5 map.

### B2 — field sky weighting

The reconstructed `IncompleteCatalogPriorState` is intentionally conditional: it divides each pixel by its own

```text
Z_p = N_obs(p) + N_miss(p)
```

and therefore removes relative angular host density.

The owner-designated full-259 legacy line instead used

```text
--catalog_sky_weighting field
```

whose numerator is

```text
N_obs(p) p_cat(z|p) + dN_miss(p,z)
```

with a single survey-global normalization. This preserves the relative host surface density between pixels.

For the present single-catalog hierarchical likelihood that global factor is common to every PE and injection sample at fixed hyperparameters. It therefore cancels exactly between the sum of `N_obs_events` event log evidences and the `-N_obs_events log(mu)` selection correction. The reusable implementation may consequently expose the field **numerator** directly, with no row-wise normalization, provided this cancellation is explicitly tested. A future multi-catalog mixture requiring absolute catalog fractions must construct and carry its full-survey global normalization separately; that is outside Phase 12B.

## Frozen starting points

```text
legacy scientific reference:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

active Phase-12 core input:
  ignaciomagana/darksirens-core@8b9dc64629cf11838a9fc1de233e46b91082caf7

accepted surveys input:
  ignaciomagana/darksirens-surveys@f027aef02d342041ce7259cdbf47fe689e6462f2

Phase-12 consumer before this correction:
  ignaciomagana/desi_darksirens_selection@334087e16bac08606d32da0c16a453149c7c3db8
```

LSS and lensing remain frozen. No Q/LSS correction is part of this slice.

## Legacy reference facts

The legacy full-259 production configuration used:

```text
c_mode = selection
catalog_sky_weighting = field
use_lss = false                         # Q-free comparison relevant here
per-pixel completeness = DESI depth/footprint map for corrected arm
```

The legacy S-3 footprint diagnostic records that the unmasked radial-selection construction applied `Cbar(z)` to every pixel, including empty off-footprint rows, and identified `C_p=f_p Cbar` as the correction.

The Q-free full-259 contrast was approximately:

```text
unmasked radial selection: H0 median ~90.25 km/s/Mpc
footprint-aware:           H0 median ~71.5  km/s/Mpc
```

This contrast is provenance for the importance of the correction, not a Phase-12 target value and not an acceptance oracle for a new posterior.

The later Q-table double-counting episode is explicitly irrelevant to Phase 12B because this slice has `use_lss=false` and introduces no Q table.

## Allowed core changes

### 12B.1 — optional row-fraction composition in selection curves

Extend the generic magnitude-selection completion seam with an optional row-fraction input, API conceptually of the form

```python
selection_completion_curves(
    cosmo,
    params,
    catalog,
    model,
    *,
    row_fraction=None,
)
```

or an equivalently narrow generic helper.

Requirements:

- default `row_fraction=None` must preserve the existing accepted output exactly;
- a row fraction is one value per catalog row and must lie in `[0,1]`;
- with row fractions, below `z_depth`:

  ```text
  C_p(z) = f_p Cbar(z)
  dN_miss(p,z) = [1 - C_p(z)] dN_exp(z)
  ```

- above `z_depth`, `dN_miss=dN_exp` exactly as in the existing finite-depth convention;
- diagnostics `C` / `C_eff` must have unambiguous semantics and tests must pin them;
- no DESI names, paths, HEALPix-map loader, or survey dependency may enter core.

### 12B.2 — separate field prior state/evaluator

Do **not** change the tuple layout or behavior of `IncompleteCatalogPriorState`.

Add a separate generic field state/evaluator, conceptually:

```python
FieldIncompleteCatalogPriorState
build_field_incomplete_catalog_prior_state_from_curves(...)
eval_field_incomplete_catalog_prior_state[_vmap](...)
```

The field evaluator must return the additive host-density numerator

```text
N_obs(p) p_cat(z|p) + dN_miss(p,z)
```

without dividing by a row-specific `Z_p`.

It may omit a global survey normalization for the Phase-12 single-catalog use because that factor cancels exactly in the hierarchical PE/selection likelihood. The API/documentation must state this scope explicitly so it is not silently reused as an absolute normalized density in a future multi-catalog mixture.

The builder must use the same accepted catalog kernel and finite-depth observed-count mass as the conditional state.

## Explicit exclusions

Phase 12B must **not**:

- change the old conditional `IncompleteCatalogPriorState` behavior;
- change count-derived ordinary completeness behavior;
- add DESI map parsing to core;
- add Q/LSS fields or LSS dependencies;
- add a general multi-catalog field-normalization framework;
- change the GW hierarchical reducer or GW selection correction;
- change population models or samplers;
- change hard MC-reliability thresholds;
- change the DESI luminosity-function fit or its priors;
- change surveys/LSS/lensing package science;
- interpret the legacy ~71.5 value as a numerical acceptance target.

## Core acceptance gates

### 12B.C1 — old-path identity

All existing conditional catalog and magnitude-selection paths must remain numerically identical with the new optional functionality unused.

At minimum:

- existing Phase-5 catalog parity workflow;
- existing Phase-12A composition tests;
- broad Phase-3 through Phase-8 regression matrix.

Focused tests must use strict array identity where the operation graph is intended to remain unchanged.

### 12B.C2 — footprint algebra

On deterministic fixtures:

- `f_p=1` reproduces the old radial magnitude-selection curves;
- `f_p=0` gives full missing density `dN_miss=dN_exp` below the depth and zero effective completeness;
- intermediate `f_p` matches `[1-f_p Cbar] dN_exp` pointwise;
- above depth remains full missing regardless of `f_p`;
- invalid shape, NaN, or values outside `[0,1]` fail closed at the host construction boundary.

### 12B.C3 — field-vs-conditional semantics

For a fixed state, verify pointwise

```text
log p_field(z,p) = log p_cond(z,p) + log Z_p
```

up to floating-point tolerance wherever finite.

Construct rows with deliberately different host counts and show that:

- conditional rows independently integrate to unit mass;
- field rows retain their relative integrated host mass rather than being row-normalized.

### 12B.C4 — hierarchical global-factor cancellation

For one catalog, multiply every field numerator by a common positive hyperparameter-dependent scalar `A(theta)`. The complete hierarchical log likelihood must be unchanged because the event term gains `N log A` and the selection correction loses the same `N log A`.

This test is load-bearing justification for omitting the full-survey scalar normalization from the Phase-12 field evaluator.

### 12B.C5 — ownership firewall

Core must remain independent of surveys/LSS/lensing. Surveys remains the owner of `load_selection_fraction` and map degradation. No raw survey schema enters core.

## Consumer changes after core acceptance

The Phase-12 consumer may repin only after the core change passes the full acceptance matrix.

Required consumer updates:

1. Add the footprint/depth map as an explicit production input with provenance. The expected legacy source is the DESI `mth_map_nside128.h5` product; its actual production path and SHA256 must be resolved/fingerprinted, not guessed in this contract.
2. Load/degrade the map through frozen `darksirens-surveys` to nside 64.
3. Record a coverage report including:
   - footprint area;
   - `n_covered`;
   - `n_off_footprint`;
   - `n_empty_covered`;
   - `n_occupied_uncovered`;
   - occupied-pixel `f_p` range/mean.
4. Fail closed if any catalog-occupied nside-64 row has `f_p=0`, unless a later explicit scientific contract explains why such a row is valid.
5. Gather `f_p` onto the compact catalog by global pixel id.
6. Build footprint-aware selection completion curves.
7. Use the new **field** prior state/evaluator, not the conditional state.
8. Retain the sampler coordinates `(H0, M0hat, sigma_M)`, fixed GWTC-5 population, fixed `(log10n0,delta,sigma_kde)`, accepted Gaussian fit priors, and hard MC-variance gate.
9. P12.2 must report PE and detected-injection probability/sample fractions on/off footprint so the angular support entering the likelihood is visible before nested sampling.
10. The production chain remains blocked unless the new map provenance and corrected target are present.

## Numerical execution barrier

The currently merged P12.4 implementation and execution chain remain historical code records, but **no numerical P12.4 output produced by the pre-12B target is scientifically acceptable**.

The Slurm launcher may remain as scheduler infrastructure, but the chain must fail closed or be explicitly marked blocked until the consumer is repinned to an accepted Phase-12B core and the footprint-aware field target is merged.

## Completion

Phase 12B is accepted only after the control repository records:

- exact accepted core head, merge SHA and tree;
- focused footprint and field tests;
- the complete historical/regression matrix on the exact head;
- post-merge core integrity;
- consumer repin and corrected target merge;
- consumer contract and post-merge CI;
- production footprint-map fingerprint/coverage provenance contract.

Only then may P12.1 -> P12.4 numerical production execution resume.
