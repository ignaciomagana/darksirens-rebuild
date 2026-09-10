# Phase 5D1 checkpoint — generic marked-host runtime

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
phase-5 branch:    rebuild/phase5-catalog-dark-bright
5C accepted head: 57af56158757ddd9272e0a2f2dc9bfbb624c1fec
5D1 candidate:    491f03fc919e3bfbb8a28a23a155c6286e4197bf
workflow run:     34473599144
```

Legacy remains read-only. Candidate and legacy parity probes run in separate
processes.

## Status

IN PROGRESS — candidate is under the exact-head Phase-5 gate. Do not treat 5D1
as accepted until the workflow and the frozen `marks` cell both pass.

## Ownership

5D1 reconstructs only generic host-property weighting in core:

```text
CenteredHostMarks                      standardized centered values
LogLinearHostModel                    log h = sum_k eta_k m_tilde_k
marked catalog kernel                 within-catalog host reweighting
N_obs * <h>_w                         observed marked amplitude
mu_miss(z) = E_obs[h|z]               missing-host efficiency
marked ordinary hierarchical path     same model in PE and selection
```

Raw survey property loading, raw native column names, and z-centering
`m - E[m|z]` remain assigned to `darksirens-surveys`. The stable
`GalaxyCatalog` type is not enlarged with `mark_logmstar`, `mark_logssfr`, or
other survey/campaign mark leaves.

Q_LSS, Q ensembles, latent fields, field/global normalization, survey masks,
depth-map construction, and selection fitting are explicitly excluded.

## Scientific pins

The legacy marked-host convention is preserved:

```text
log h_i = sum_k eta_k m_tilde_ik
log h clipped to +/- 7
catalog shape weights proportional to w_i h_i
observed amplitude = N_obs * <h>_w
```

The amplitude convention is count based, not raw weighted mass. Therefore a
catalog-wide rescaling `w -> c w` cannot change the catalog:missing odds, and
`eta=0` reduces to the ordinary galaxy-count model even for non-unit weights.

The missing branch uses a 40-bin empirical
`mu_miss(z|eta) = E_obs[h|z]`. Empty/out-of-coverage bins fall back to the
catalog-wide mean efficiency rather than one. Consequently a redshift-independent
mark multiplies observed and missing branches equally and cancels: eta remains a
shape parameter rather than a spurious completeness-amplitude parameter.

A host-side liveness guard rejects centered-mark tables for which more than half
of real galaxies can hit the `|log h| <= 7` rail somewhere inside the eta prior.
Survey-side construction must center raw marks before creating the core runtime
object.

## Frozen parity fixture

The immutable Phase-1 K=1 `marks` cell is the end-to-end target:

```text
NPIX = 12
z_gal per pixel = [0.06, 0.16]
marks per pixel = [m, -m]
m = 0.9 * linspace(-1, 1, 12)
eta prior = [-5, 5]
coordinate fractions = [0.50, 0.35, 0.65]
eta values = [0.0, -1.5, +1.5]
```

The gate compares event evidences, PE MC variances, selection `log_mu`, `N_eff`,
selection correction, assembled likelihood, and the final full likelihood in
separate legacy/candidate processes. Both final values are additionally checked
against `tests/reference/legacy/unified_k1_golden.json` at `rtol=1e-12`,
`atol=0`.

## Candidate diff

The provisional 5D1 commit adds only:

```text
src/darksirens/catalog/hosts.py
src/darksirens/likelihood/marked.py
tests/test_catalog_hosts.py
tools/probe_catalog_marks.py
.github/workflows/phase5-catalog-dark-bright.yml
```

No 5D2 parametric selection-function runtime is included in this candidate.

## Next action

Read workflow run `34473599144`. If it fails, fix only the first failing layer
and keep the frozen comparator unchanged. If it passes, record exact test counts
and parity residuals here and in `STATUS.md`, mark 5D1 accepted, then begin 5D2
from that exact accepted head with read-only selection-runtime inspection first.
