# Phase 7F3 — angular composition and likelihood wiring

Status: **ACCEPTED**

```text
legacy reference: c042527238bd71421b792936bc48c3b815b90d6d
parent 7F2:      877bda4e5e2e10ac52c657f7990159afcfa1093a
accepted head:   be95e95bdf77144880cba5752ed5feafd40a697f
accepted tree:   55dfb24cb84edebb0175409bd33be2a6a57ecb8a
branch:          rebuild/phase7-public-api
```

## Frozen contract

The pinned legacy implementation establishes four load-bearing rules for the
ordinary angular source-population path:

1. the sky block is appended after cosmology, population and survey/catalog
   coordinates;
2. sky parameters decode as their own vector, with `isotropic` contributing an
   empty block;
3. the same mean-one factor `log g(nhat, z)` is applied to PE-sample and detected-
   injection target weights;
4. the redshift entering a 3-D angular model is obtained from luminosity distance
   using the same cosmology/distance table and the same clamp-before-interpolate
   reverse-mode discipline as the ordinary likelihood.

No scientific convention was changed in this slice.

## Reconstruction

The accepted implementation adds only the typed composition/wiring needed to
make the already parity-tested 7F1/7F2 angular models reachable from the public
ordinary API:

- `ds.model(..., angular=...)`, defaulting to exact frozen isotropy;
- normalized angular model identity on `Analysis`;
- angular metadata on `ParameterPlan`, appended after the catalog block;
- angular model constraint groups routed through the existing Phase-7C1 joint
  prior resolver (including the dipole `ball3` map), with no new transform
  layer;
- separate angular-coordinate decoding in the runtime binder;
- one optional PE angular-weight seam symmetric with the selection reducer's
  already-preserved optional sky seam;
- one shared clamped-`dL` -> `z` -> `log g(nhat,z)` closure used for both PE and
  selection weights;
- wiring for the three public ordinary analyses only: spectral, incomplete
  catalog and complete catalog.

`bright_siren_log_likelihood` was deliberately untouched: Phase 7 does not
expose a public bright-siren composition and there was no need to change the
accepted Phase-5 path.

Advanced angular geometry can be instantiated during `ds.model()`, so that lazy
facade configures the validated JAX x64 runtime immediately before construction.
Plain `import darksirens` remains dependency-light and does not initialize JAX.

## Scope audit

The accepted 7F2 -> 7F3 diff is exactly one commit and touches only:

```text
.github/workflows/phase7f3-angular-wiring.yml
src/darksirens/__init__.py
src/darksirens/analysis.py
src/darksirens/inference/joint_prior.py
src/darksirens/likelihood/event.py
src/darksirens/likelihood/hierarchical.py
src/darksirens/runtime_binding.py
tests/test_angular_wiring.py
tools/probe_angular_wiring.py
```

No population kernel, catalog-redshift/completeness kernel, sampler backend,
checkpoint/result layer, raw survey, LSS, lensing or campaign code changed.

## Acceptance gates

Exact-head dedicated gate:

```text
workflow: phase7f3-angular-wiring
run:      34632081722
job:      103371081194 (angular-wiring)
status:   SUCCESS
```

It passed focused tests, package-root lazy-import checks, the companion-package
firewall, separate-process pinned-legacy and reconstructed dipole PE/selection
evaluations, and exact dipole wiring parity.

Exact-head broad regression:

```text
workflow: phase7-regression
run:      34632081763
job:      103371080968 (regression)
status:   SUCCESS
result:   517 passed, 1 skipped
```

The single skip is the existing opt-in population-registry golden regeneration
test. The broad companion-import firewall also passed.

All earlier Phase-7 gates replayed successfully on the same accepted head:

```text
7A  public loaders:          34632081557 / 103371080345 SUCCESS
7B  public specs:            34632081698 / 103371081242 SUCCESS
7C1 joint-prior resolver:    34632081654 / 103371080964 SUCCESS
7C2 public model:            34632081670 / 103371080911 SUCCESS
7C3 HEALPix geometry:        34632081679 / 103371080994 SUCCESS
7D  runtime binding:         34632081612 / 103371081102 SUCCESS
7E  public infer:            34632081558 / 103371080182 SUCCESS
7F1 basic angular:           34632081584 / 103371080599 SUCCESS
7F2 advanced angular:        34632081637 / 103371081339 SUCCESS
```

## Verdict

Phase 7F3 is accepted at
`be95e95bdf77144880cba5752ed5feafd40a697f`. Isotropy remains an exact no-op
relative to the previously accepted ordinary likelihood path, while nontrivial
angular source populations enter the PE numerator and selection integral with
the frozen shared weighting convention.

The next action is a Phase-7 closure/integration audit. No additional production
slice should be invented unless that audit finds a concrete core-owned ordinary
capability still missing from the target architecture.