# Phase 5 report — core catalog + dark/bright sirens

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
base core SHA:     0f97feff7eb283a1f541bef9a776c9347084e70e
planned branch:    rebuild/phase5-catalog-dark-bright
```

## Status

CONTRACT FROZEN; IMPLEMENTATION NOT STARTED.

Phase 5 begins from the verified Phase-4 merge SHA above. The first production
write must be on a branch created from exactly that SHA. Legacy remains read-only.

The goal is not to copy `catalogs/`, `redshift/`, `likelihood/core.py`, or
`likelihood/factory.py`. The goal is to reconstruct the ordinary catalog-owned
scientific path inside the physical owners established by the new architecture.

## Scientific target

Phase 5 makes the Phase-4 catalog-free hierarchy capable of three additional
ordinary redshift/host models:

```text
incomplete dark siren
complete-catalog dark siren
bright/counterpart siren
```

while preserving the Phase-4 spectral path unchanged.

The ordinary incomplete model is the pinned additive-count-density model:

```text
p(z | row) = [N_obs(row) p_cat(z | row) + dN_miss(z | row)]
             / [N_obs(row) + N_miss(row)]
```

with

```text
dN_exp/dz = n0 * apix * dV_c/dz * (1+z)^delta
C(z|row)  = clip(dN_obs_s(z|row) / dN_exp_s(z), 0, 1)
dN_miss   = (1-C) dN_exp
N_miss    = integral dN_miss dz
```

for the ordinary non-LSS baseline. `delta`, not `delta-1`, belongs in the
galaxy measure. Merger-rate evolution remains in the GW population model.

The catalog term is the pinned weighted mixture of individually normalized,
volumetrically tilted galaxy kernels:

```text
p(z | galaxy i) = Normal(z; z_i, sigma_eff_i) g(z) / Z_i
sigma_eff_i = max(sqrt(dz_i^2 + sigma_kde^2), 1e-4)
g(z) = dV_c/dz * (1+z)^delta
p_cat(z|row) = sum_i [w_i/sum_j w_j] p(z|galaxy i)
```

Every real galaxy kernel carries unit mass on the modeled redshift interval.
Distance/volume weighting may tilt a galaxy kernel in z but must not change the
galaxy's total host weight merely because it lies farther away.

## Bright-siren contract

The bright path is not “an EM Gaussian instead of the population prior”. The
pinned numerator is:

```text
log p_bright(z) = log Normal(z; z_counterpart, dz_counterpart)
                  + log p_volume(z | cosmology)
```

and the GW selection integral uses the same catalog-free normalized volume
prior. This population-volume factor is z-dependent and must remain live.

Per-event counterpart metadata must support:

```text
counterpart global pixel
counterpart z
counterpart dz
active event index
sky-marginalized yes/no
```

When sky marginalization is disabled, samples outside the active counterpart
pixel have zero probability. When enabled, the counterpart redshift likelihood
applies independent of sample pixel.

Core runtime must not require `healpy` merely to evaluate this model. A thin
RA/Dec-to-pixel construction helper may use a lazy/optional HEALPix dependency
later, but the scientific runtime contract consumes already-resolved pixel ids.

## Complete-catalog contract

For an occupied row, the complete model is exactly `p_cat(z|row)`.

For an empty row under the conditional ordinary model:

```text
policy = zero    -> log p = -inf
policy = volume  -> normalized comoving-volume fallback
```

Both policies must be pinned. The field/global-normalizer variants are not part
of the first ordinary Phase-5 slice because they are extension-facing and are
not needed to reproduce the ordinary conditional K=1 model.

## Ordinary completeness details that are scientific pins

The default completeness estimator uses the same linear smoothing operator on
observed and expected counts. Legacy width:

```text
sigma_smooth = 0.05
```

The observed numerator uses galaxy point estimates `zgals`; it does not fold
`dzgals` into the completeness smoothing. This is a known legacy caveat and is
NOT corrected during migration.

A finite `z_depth` is ordinary core behavior and must be supported in Phase 5:

- completeness is exactly zero above `z_depth`;
- above depth, `dN_miss = dN_exp` in the ordinary non-LSS model;
- `N_miss` integrates over the full modeled z range;
- observed catalog-kernel support is truncated so a catalogued galaxy contributes
  no observed-host probability above the survey depth;
- `z_depth=None` remains the legacy full-grid behavior.

## Runtime catalog contract

The first stable core runtime type is an ordinary `GalaxyCatalog` concept. It
must not reproduce legacy `EMCatalog`, whose leaf set is contaminated by LSS,
field-normalizer, mark-construction, weak-lensing, and campaign state.

Minimum ordinary runtime data:

```text
apix
zgals              # (N_rows, N_max)
dzgals             # (N_rows, N_max)
wgals               # (N_rows, N_max)
ngals               # (N_rows,)
unique_pixels       # optional global HEALPix id per compact row
sample_to_unique    # belongs to a sample view, not immutable catalog physics
ordinary KDE cache/state where appropriate
```

A row's first `ngals[row]` columns are the real-galaxy prefix. Real rows must be
z-sorted when the windowed KDE optimization is enabled. Sparse/high global pixel
ids must not require a dense `max(pixel)+1` cache lookup: cache row k corresponds
directly to compact catalog row k.

The canonical file contract belongs to core. Raw DESI/Legacy/GLADE column
interpretation, masks, depth-map construction, survey weighting, and fitting of
selection functions remain in `darksirens-surveys`.

## Parameter ownership

Do not create a replacement `SurveyParams` mega container.

The ordinary catalog/redshift model may carry only parameters it actually
consumes, initially:

```text
n0
delta
sigma_kde
z_depth                 # structural/fixed runtime datum
complete empty-row policy
```

Additional runtime selection-function parameters enter only in the dedicated
5D slice after their ownership is separated from survey fitting. Legacy truth
parameters such as `z50`/`w`, LSS bias state, Q/latent leaves, and lensing state
do not belong in this ordinary parameter object.

## Migration slices

### 5A — standardized runtime catalog + compact views + catalog kernel

Target owners:

```text
src/darksirens/catalog/types.py
src/darksirens/catalog/compact.py
src/darksirens/catalog/redshift.py
src/darksirens/catalog/__init__.py
```

Migrate scientific behavior from:

```text
legacy catalogs/compact.py
ordinary standardized-schema pieces of catalogs/io.py
redshift/catalog.py
ordinary compact-view pieces of likelihood/catalog_views.py
```

Required lower-level parity:

- real-galaxy prefix masking;
- compact row and sample-to-row mapping;
- required empty pixels retained in compact row sets;
- row-direct KDE cache indexing;
- sparse/high global pixel ids are value-inert;
- sigma_eff floor = 1e-4;
- per-galaxy volumetric kernel normalization;
- row weighted-mixture normalization;
- NaN/impossible inputs return `-inf` rather than probability one;
- scalar/vector boundaries agree;
- comoving-distance table is threaded as an argument rather than embedded in a
  giant HLO constant;
- cold repeated shape specialization works.

The first implementation should preserve the legacy 24-node CDF-space
Gauss-Legendre normalization. Mature row-chunk/KDE-window optimizations may be
ported in this slice when they can be shown numerically inert; do not rewrite the
kernel mathematics while moving it.

### 5B — ordinary completeness + depth

Target owner:

```text
src/darksirens/catalog/completeness.py
```

Migrate only the non-LSS count-budget path from `redshift/completion.py`.

Required parity:

- `log g(zgrid)`;
- expected count density;
- shared smoothing operator;
- calibrated constant/sigmoid completeness fixtures;
- count-odds identity `N_obs : N_miss`;
- empty row becomes pure missing density;
- `z_depth=None` full-grid behavior;
- finite-depth relaxation to `dN_exp` above depth;
- full-grid `N_miss` integral;
- observed kernel truncation above depth.

Do NOT port `delta_g`, Q_LSS, Q ensembles, latent state, field/global
normalizers, mask-free diagnostics, or lognormal reconstruction.

### 5C — ordinary redshift models + hierarchical composition

Target owners:

```text
src/darksirens/catalog/models.py       # or equally explicit catalog-owned model file
src/darksirens/catalog/counterparts.py
src/darksirens/likelihood/hierarchical.py
```

Do not introduce a public string registry. Compose explicit spectral/catalog/
counterpart behavior into the existing Phase-4 hierarchical machinery.

Required fixed-theta end-to-end legacy cells:

```text
plain_full
plain_compact
complete_volume
complete_zero
bright
```

The frozen Phase-1 CPU values already live in:

```text
tests/reference/legacy/unified_k1_golden.json
```

with canonical `rtol=1e-12`, `atol=0`.

In addition to frozen-bank comparison, run separate-process legacy/candidate
probes that serialize event evidences, PE MC variances, selection `log_mu` and
`N_eff`, selection correction, and final likelihood for small dark/complete/
bright fixtures. Selection must use the same redshift/host model as the PE
numerator where the legacy ordinary dark model requires it; bright uses the
volume prior in selection.

### 5D — generic marks and non-LSS catalog-selection runtime

This slice is conditional on clean ownership after 5A–5C parity is accepted.
Generic host-property weighting is core by D011. Survey-specific construction
and centering of raw properties remain in surveys.

Likewise, runtime evaluation of serialized magnitude-selection models is core;
fitting them is surveys. Aggregate/stratified/parametric selection modes may be
ported here only if they can be made ordinary and companion-free. Anything whose
normalization intrinsically requires field/Q state waits for the LSS interface.

Do not block 5A–5C on 5D.

## Explicit non-owners / deferred code

```text
catalogs/depth_map.py                         -> SURVEYS
catalogs/lss.py                               -> LSS
raw survey ingestion/column interpretation   -> SURVEYS
selection-function fitting                    -> SURVEYS
redshift/lognormal_completion.py              -> LSS
redshift/latent_field.py                      -> LSS
redshift/latent_counts.py                     -> LSS
Q/ensemble/latent branches of prior.py        -> LSS
field/global normalization                     -> LSS seam / later extension freeze
likelihood/latent_q.py                        -> LSS
weak/strong lensing                            -> LENSING
flows                                           -> later optional core phase
samplers/inference parameter orchestration     -> next core phase
mega likelihood factory / universe dispatcher -> DO NOT RECREATE
```

`test_completion_prior_strength.py` and `test_mask_free_criterion.py` are LSS
artifact/reconstruction tests despite their generic-looking names and are not
Phase-5 core gates.

## Primary legacy test assets

Ordinary catalog/redshift anchors:

```text
tests/test_redshift_prior_model.py
tests/test_complete_catalog_empty_pixel_policy.py
tests/test_bright_siren_prior.py
tests/test_catalog_prior_distance_table.py
tests/test_cache_row_indexing.py
tests/test_completion_depth.py
```

Additional KDE row/window/chunk tests should be migrated when their corresponding
performance optimization enters 5A.

Factory-specific frozen-prior optimization (`test_frozen_redshift_prior.py`) is
deferred to the inference/runtime orchestration phase. Its numerical redshift
model is covered here, but Phase 5 does not recreate the old factory merely to
preserve that optimization gate.

## Final Phase-5 acceptance

Phase 5 is accepted only if:

1. the Phase-4 spectral likelihood remains green and numerically unchanged;
2. the ordinary catalog namespace has no LSS/lensing/surveys imports;
3. direct catalog-kernel/completeness/counterpart legacy probes pass;
4. `plain_full == plain_compact` at the pinned ordinary fixture;
5. complete zero/volume empty-row semantics match legacy;
6. dark/complete/bright fixed-theta full likelihood cells match the pinned legacy
   reference at `rtol=1e-12`, `atol=0`;
7. the separate-process detailed legacy/candidate probes pass without importing
   both packages into one interpreter;
8. no raw survey schema or campaign-specific state appears in core;
9. the exact accepted branch head passes all historical workflows plus the new
   Phase-5 workflow before squash merge.

## Next action

Create `rebuild/phase5-catalog-dark-bright` from exactly
`0f97feff7eb283a1f541bef9a776c9347084e70e`. Implement only slice 5A first,
with a permanent Phase-5 workflow and lower-level legacy/candidate parity. Do not
start completeness or hierarchical composition until 5A is green.
