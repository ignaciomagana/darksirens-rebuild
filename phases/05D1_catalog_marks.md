# Phase 5D1 checkpoint — generic marked-host runtime

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
phase-5 branch:    rebuild/phase5-catalog-dark-bright
5C accepted head: 57af56158757ddd9272e0a2f2dc9bfbb624c1fec
5D1 accepted head: bf45e0f5c0afc404d291d00a0ca267f8126b7e7b
```

Legacy remained read-only. Candidate and legacy were evaluated in separate
processes.

## Status

ACCEPTED.

5D1 reconstructs only generic host-property weighting for the ordinary
conditional incomplete-catalog model. Survey-native property loading and
z-centering remain outside core. LSS/Q/latent/field normalization is not part of
this slice.

## Core ownership

Added:

```text
src/darksirens/catalog/hosts.py
src/darksirens/likelihood/marked.py
```

`GalaxyCatalog` is unchanged. Mark values live in a separate
`CenteredHostMarks` object aligned with standardized catalog rows. The host
model is explicit (`LogLinearHostModel`); no string registry or
`universe_model` dispatcher was introduced.

The generic model is

```text
log h_i = sum_k eta_k m_tilde_ik
|log h| <= 7
eta_k in [-5, 5] by default
```

and preserves the mature marked-host count convention

```text
N_host,obs = N_obs * <h>_w
```

rather than the raw weighted mass `sum_i w_i h_i`. Therefore a global rescaling
`w -> c w` is exactly inert in the catalog:missing odds.

The ordinary missing-host efficiency is the frozen 40-bin empirical estimator

```text
mu_miss(z | eta) = E_obs[h | z].
```

Uninformed bins use the catalog-wide mean host efficiency, not one. Hence a
redshift-independent mark multiplies observed and missing branches equally and
is an exact shape null rather than changing the completeness odds.

Finite catalog depth uses the same marked-kernel pre-renormalization depth mass
as the unmarked model, so the observed marked amplitude is scaled consistently
with the truncated observed kernel.

## Survey/core boundary

Core consumes already-standardized z-centered mark arrays. The following remain
survey construction responsibilities:

```text
raw LOGMSTAR/LOGSSFR/metallicity/colour column interpretation
survey file loading
z-bin centering m -> m - E[m|z]
pixelization and mask construction
```

Core includes only a liveness guard that rejects a supplied mark table when more
than half of the real galaxies can reach the `|log h|=7` rail inside the eta
prior. It does not attempt to repair or center raw marks.

## Validation

Accepted exact-head workflow:

```text
workflow run: 34498152895
job:          102941812699
result:       SUCCESS
```

Focused and historical gates:

```text
Phase 5A compact tests:                  5 passed
Phase 5A redshift/distance tests:       11 passed
Phase 5B completeness/HLO tests:        11 passed
Phase 5C explicit hierarchy tests:       3 passed
Phase 5D1 marked-host tests:             7 passed
full reconstructed suite:              242 passed, 1 regen-only skip
dependency/light-import audit:          PASS
```

Separate-process parity at the accepted head:

```text
5A catalog-kernel parity:       max_abs=max_rel=0
5B completeness parity:         max_abs=max_rel=0
5C detailed likelihood parity:  max_abs=max_rel=0
5D1 marked-host parity:          max_abs=max_rel=0
rtol:                            1e-12
atol:                            0
```

The 5D1 detailed probe compares event evidence, PE Monte-Carlo variance,
selection `log_mu`, `N_eff`, selection correction, assembled likelihood, and
full likelihood at the three immutable K=1 mark coordinates. Legacy and
candidate are additionally checked against the frozen CPU `marks` values in
`tests/reference/legacy/unified_k1_golden.json`.

## Failed-gate record

The first 5D1 parity run failed only when the manual legacy probe was compared to
the frozen Phase-1 `marks` bank. Candidate and manual legacy agreed with each
other, but the off-center eta coordinates did not equal the factory-generated
golden.

Cause: the golden starts from a 12-row full-sky catalog, but the mature legacy
factory first compacts the flat source to the PE/selection pixel union. For this
fixture the only visited global pixels are 2 and 7, so the runtime catalog and
mark table contain exactly rows `[2, 7]`; PE rows map to `[1, 1]` and selection
rows to `[0, 1, 0, 1, 0, 1, 0, 1]`. The manual probe had evaluated
`mu_miss=E_obs[h|z]` over all 12 rows. This is identical at eta=0 but changes the
marked missing-host efficiency away from the null.

Only the probe was corrected to reproduce the legacy union view. No host physics
or tolerance changed. The next exact-head run passed with zero numerical
difference.

## Diff audit

Compared 5C accepted head to 5D1 accepted head. The branch is three commits ahead
and zero behind. Changed files are exactly:

```text
.github/workflows/phase5-catalog-dark-bright.yml
src/darksirens/catalog/hosts.py
src/darksirens/likelihood/marked.py
tests/test_catalog_hosts.py
tools/probe_catalog_marks.py
```

No standardized catalog type, cosmology, population, selection, survey, LSS, or
lensing file changed.

## Next action

Proceed to 5D2 from exact accepted head
`bf45e0f5c0afc404d291d00a0ca267f8126b7e7b`. Reconstruct only the generic
runtime evaluation of non-LSS parametric magnitude-selection completeness.
Keep SciPy fitting, survey data preparation, fit CLI, raw magnitudes, masks and
survey-native schemas in `darksirens-surveys`. Preserve the H0 firewall and the
legacy Gaussian/Schechter curve semantics before adding hierarchical
composition or moving to final Phase-5 acceptance.
