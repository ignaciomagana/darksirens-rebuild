# Phase 5C checkpoint — ordinary dark, complete, and bright sirens

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
phase-5 branch:    rebuild/phase5-catalog-dark-bright
5B accepted head: f4bc721496359f09fc58609fa23ccce21366f728
5C accepted head: 57af56158757ddd9272e0a2f2dc9bfbb624c1fec
```

Legacy remained read-only. Candidate and legacy likelihood probes ran in separate
Python processes because both distributions expose the import package
`darksirens`.

## Status

ACCEPTED.

Phase 5C reconstructs the ordinary incomplete dark-siren, complete-catalog, and
bright/counterpart redshift models and composes them into the already accepted
Phase-4 hierarchical PE/selection machinery. Phase 5 as a whole remains open;
5D is the only remaining planned catalog slice before final Phase-5 integration.

## Accepted architecture

Phase 5C added explicit physical model objects/functions rather than recreating
the legacy `universe_model` switchboard.

```text
src/darksirens/catalog/models.py
src/darksirens/catalog/counterparts.py
src/darksirens/likelihood/hierarchical.py
```

The catalog layer owns the redshift-prior states/evaluators. The hierarchical
layer only wires those evaluators into the existing shared sample-weight,
per-event, and selection reductions.

The accepted public composition seam now has explicit entry points:

```text
dark_siren_log_likelihood
complete_catalog_siren_log_likelihood
bright_siren_log_likelihood
spectral_siren_log_likelihood       # pre-existing Phase-4 path, kept explicit
```

A final architecture search of reconstructed `src/darksirens` at the accepted
head found zero occurrences of `universe_model`.

`GalaxyCatalog` and `CatalogParameters` were not enlarged during 5C. The
ordinary parameter contract remains only the state actually consumed by this
layer (`n0`, `delta`, `sigma_kde`, structural `z_depth`); complete empty-row
policy is an explicit model argument rather than another mega-container field.

## Accepted scientific behavior

### Incomplete dark siren

The frozen conditional K=1 model is

```text
p(z|row) = [N_obs(row) p_cat(z|row) + dN_miss(z|row)]
           / [N_obs(row) + N_miss(row)].
```

PE and selection use the same catalog-completed redshift model.

### Complete catalog

For occupied rows, the prior is the same unit-mass observed-catalog kernel used
by frozen legacy. For empty rows:

```text
zero   -> -inf
volume -> normalized comoving-volume prior
```

Both policies are explicitly live in focused tests and frozen K=1 parity.

### Bright/counterpart siren

The PE numerator is

```text
Normal(z; z_counterpart, dz_counterpart)
* normalized comoving-volume prior
```

with an optional resolved-global-pixel gate. Bright selection intentionally uses
the catalog-free normalized volume prior. A focused regression checks that the
bright selection `log_mu`, `N_eff`, and selection correction are exactly equal
to the spectral/catalog-free selection calculation on the same injections.

## Frozen five-cell parity fixture

The 5C detailed replay uses the Phase-1 K=1 fixture directly:

```text
cells:
    plain_full
    plain_compact
    complete_volume
    complete_zero
    bright

N_events = 1
N_PE/event = 2
N_detected_injections = 8
N_draw = 8
NSIDE = 1 equivalent pixel area = pi/3
H0 = 67.74
Om0 = 0.3075
n0 = 1e-2
delta = 0
sigma_kde = 0
```

At each of the three frozen population-coordinate fractions `(0.50, 0.35,
0.65)`, both implementations serialize and compare:

```text
event_log_evidence
event_mc_variance
log_mu
n_eff
selection_log_correction
assembled_from_parts
full_log_likelihood
```

The final likelihoods are additionally compared against the immutable Phase-1
CPU bank `tests/reference/legacy/unified_k1_golden.json`.

## Validation

Accepted exact-head workflow:

```text
workflow run: 34465661255
job:          102833519200
result:       SUCCESS
```

Focused and historical gates:

```text
Phase 5A compact tests:                    5 passed
Phase 5A redshift/distance tests:         11 passed
Phase 5B completeness/HLO tests:          11 passed
Phase 5C explicit hierarchy tests:         3 passed
full reconstructed suite:                235 passed, 1 regen-only skip
catalog dependency-boundary audit:        PASS
light catalog import audit:               PASS
```

Separate-process parity on the accepted 5C head:

```text
5A catalog-kernel parity:
    max_abs = 0.000e+00
    max_rel = 0.000e+00

5B ordinary-completeness parity:
    max_abs = 0.000e+00
    max_rel = 0.000e+00

5C detailed ordinary/bright likelihood parity:
    max_abs = 0.000e+00
    max_rel = 0.000e+00

all comparisons:
    rtol = 1e-12
    atol = 0
```

The 5C comparator also requires both legacy and reconstructed final values to
match the frozen Phase-1 CPU K=1 bank for all five cells.

## Test-gap found and fixed before acceptance

The first hierarchical composition commit (`0a231ceac2d5ca476fc3d6460b988c37b4a35009`)
passed the existing Phase-5 workflow, but an audit showed that none of the
existing tests directly executed the three newly added hierarchy entry points.
That green run was therefore not accepted as evidence for 5C.

The accepted gate commit added `tests/test_catalog_hierarchical.py` plus the
separate-process detailed likelihood replay. No candidate physics change was
needed after the real gate existed; the first fully instrumented 5C run passed.

## Diff audit

Compared accepted 5B head `f4bc721496359f09fc58609fa23ccce21366f728`
to accepted 5C head `57af56158757ddd9272e0a2f2dc9bfbb624c1fec`.
The branch is three commits ahead and zero behind. Changed files are exactly:

```text
.github/workflows/phase5-catalog-dark-bright.yml
src/darksirens/catalog/counterparts.py
src/darksirens/catalog/models.py
src/darksirens/likelihood/hierarchical.py
tests/test_catalog_hierarchical.py
tests/test_catalog_models.py
tools/compare_catalog_likelihood_probe.py
tools/probe_catalog_likelihood.py
```

No survey, LSS, lensing, sampler, inference-runtime, or campaign file changed.
No raw survey schema was added to core.

## Next action

Begin Phase 5D with read-only inspection of frozen legacy generic marks and
ordinary non-LSS serialized catalog-selection runtime. Preserve D011: generic
host-property weighting may live in core, but raw-property construction and
z-centering belong in `darksirens-surveys`. Runtime evaluation of serialized
magnitude-selection models may live in core; fitting them belongs in surveys.

Do not import Q/LSS/latent/field-normalizer machinery into 5D. If an aggregate,
stratified, or selection-mode branch intrinsically needs field/Q normalization,
defer that branch to the LSS extension seam instead of forcing it into core.
