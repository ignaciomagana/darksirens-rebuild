# Phase 5A checkpoint — standardized catalog runtime and redshift kernel

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
base core SHA:     0f97feff7eb283a1f541bef9a776c9347084e70e
working branch:    rebuild/phase5-catalog-dark-bright
accepted 5A head:  f418174a7fc8734bfbcf553d5b5c36f9f4280987
```

## Status

ACCEPTED AS A PHASE-5 SUBPHASE CHECKPOINT. Phase 5 as a whole is not complete.

The 5A head passed the permanent Phase-5 workflow at the exact branch head,
including the full historical reconstructed suite and a separate-process
comparison against the frozen legacy implementation. Completeness, hierarchical
dark/complete/bright composition, marks, and catalog-selection runtime have not
been accepted yet.

## Scope reconstructed

```text
src/darksirens/catalog/types.py
src/darksirens/catalog/compact.py
src/darksirens/catalog/redshift.py
src/darksirens/catalog/__init__.py
```

The reconstructed core now owns only the ordinary standardized catalog runtime:

- compact row data (`zgals`, `dzgals`, `wgals`, `ngals`, `unique_pixels`);
- sparse/high global-pixel to compact-row mapping without `max(pixel)+1` storage;
- required empty-row retention;
- the ordinary observed-host redshift kernel;
- the 1e-4 effective-redshift-width floor;
- per-galaxy unit-mass volumetric kernel normalization;
- weighted row-mixture normalization;
- finite survey-depth truncation and below-depth mixture-mass bookkeeping;
- the mature row-chunk build boundary needed to avoid wide-catalog build OOMs;
- the mature legacy one-pass cached evaluator semantics.

No replacement `EMCatalog` or `SurveyParams` mega-container was introduced.
Survey-native schemas, HEALPix construction, LSS/Q state, lensing state, and the
old `universe_model` dispatcher remain outside this runtime.

## Legacy behavior checked explicitly

The first strict legacy/candidate probe exposed three cached-evaluator cells in
which legacy returned exact `-inf` while the first reconstruction returned a
finite but astronomically small Gaussian tail. This was not a physical support
cut. Inspection of frozen
`darksirens/redshift/catalog.py::eval_log_catalog_prior_state` showed that the
mature legacy hot path deliberately uses a one-pass linear-domain exponential
sum with a build-time row maximum. The backend therefore underflows sufficiently
remote terms to exact zero.

The reconstruction was changed to reproduce that exact numerical path:

```text
log_kw_eff          = log_kw - log(sigma_eff) - log(sqrt(2 pi))
inv_sig_eff         = 1 / sigma_eff
log_kw_eff_rowmax   = row-wise build-time maximum
s                    = sum exp(log_kw_eff - rowmax - 0.5 u^2)
log_mix              = rowmax + log(s), with s=0 -> -inf
```

The direct diagnostic evaluator remains log-space and may stay finite farther
into the tails. A focused regression test pins this distinction so a future
cleanup cannot silently replace the production cached estimator with a different
one.

The initial probe also failed once before comparison because JSON strict mode
cannot serialize physical `-inf`; the probe now encodes non-finite values
explicitly and compares those states rather than hiding them.

## Accepted validation

Permanent workflow:

```text
workflow: .github/workflows/phase5-catalog-dark-bright.yml
run:      34456764290
job:      102804866600
head:     f418174a7fc8734bfbcf553d5b5c36f9f4280987
result:   SUCCESS
```

Acceptance details:

```text
ruff F/E9 + compileall:                  PASS
standardized catalog/compaction tests:   5 passed
catalog redshift + distance-table tests: 11 passed
full reconstructed suite:                215 passed, 1 regen-only skip
dependency-boundary audit:               PASS
light darksirens.catalog import:         PASS
pinned legacy catalog probe:             PASS
reconstructed catalog probe:             PASS
legacy/new catalog-kernel parity:        PASS
max_abs:                                 7.105e-15
max_rel:                                 9.229e-14
comparison rtol:                         1e-12
comparison atol:                         0
```

The parity probe evaluates three fixed `(H0, delta, sigma_kde)` points and
serializes the galaxy-measure samples, per-galaxy kernel weights and widths,
empty-row state, direct and cached redshift-density evaluations, depth-truncated
kernel weights, depth mass, and above-depth/empty-row `-inf` semantics. Legacy
and reconstructed packages run in separate Python processes.

## Dependency boundary

The workflow statically rejects catalog-runtime imports of survey, LSS, lensing,
CLI, and HEALPix packages. It also verifies that importing `darksirens.catalog`
does not load JAX or the cosmology distance tables. Both checks pass at the
accepted head.

## Deferred from 5A

The following mature legacy optimizations or branches were deliberately not
pulled into the first parity slice:

```text
sample-local KDE windowing
tiered column caps
pinned-H0 kernel quadrature
z-space alternative quadrature
marked-host kernels
volume-weighted complete-catalog kernels
completion curves and missing-galaxy density
field/global normalizers
Q/LSS/latent branches
```

They enter only if required by the later owner-specific slice and must again be
checked against frozen legacy behavior.

## Next action

Begin Phase 5B on the same branch from accepted 5A head
`f418174a7fc8734bfbcf553d5b5c36f9f4280987`. Reinspect the frozen legacy
`redshift/completion.py` and its ordinary tests first. Reconstruct only the
non-LSS count-budget completeness/depth path in
`src/darksirens/catalog/completeness.py`. Do not port `delta_g`, Q, latent fields,
field/global normalizers, or survey-selection fitting. Add an independent
legacy/candidate completeness probe and require the same strict numerical gate
before starting 5C.
