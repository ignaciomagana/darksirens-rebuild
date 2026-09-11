# Phase 7 — closure and integration audit

Status: **COMPLETE / MERGED**

```text
phase base:       d82becaf76bf62c0f72a71b32ebbf9b238ba4f13
accepted head:    be95e95bdf77144880cba5752ed5feafd40a697f
accepted tree:    55dfb24cb84edebb0175409bd33be2a6a57ecb8a
PR:               #6
squash merge:     6ed3dc74aa0fcde4da128036cc3d56c29250d370
merged tree:      55dfb24cb84edebb0175409bd33be2a6a57ecb8a
legacy reference: c042527238bd71421b792936bc48c3b815b90d6d
```

The accepted Phase-7 head and the squash-merged `main` commit point to the
**same Git tree**. The integration therefore changed commit history only; the
scientific/public contents validated on the accepted head are byte-identical to
the merged core.

## Closure question

Phase 7 was defined to add only the small conventional ordinary-core construction
and public surfaces deliberately deferred until the scientific kernels and
inference machinery were frozen. The closure audit asked whether any concrete
core-owned ordinary behavior still required a production slice before
integration.

The answer was **no**. There is no Phase 7G.

## Accepted Phase-7 surface

The target ordinary library path is fully represented:

```python
import darksirens as ds

events = ds.load_events("pe.h5")
injections = ds.load_injections("selection.h5")
catalog = ds.load_catalog("catalog.h5")

cosmo = ds.Cosmology(H0=(20.0, 140.0), Om0=0.3075)
pop = ds.Population("brokenpowerlaw+2peaks", fixed="gwtc5")
analysis = ds.model(
    cosmology=cosmo,
    population=pop,
    catalog=catalog,
    angular="isotropic",
)
result = ds.infer(
    analysis,
    events=events,
    injections=injections,
    sampler="tinyns",
)
```

Accepted slices:

```text
7A  standardized public GW/catalog loaders
7B  declarative Cosmology / Population specifications
7C1 model-declared joint-prior resolver
7C2 typed public model() / parameter plan
7C3 portable HEALPix RING geometry
7D  ordinary runtime binding
7E  thin public infer() facade
7F1 basic angular models
7F2 advanced angular models
7F3 angular parameter/likelihood composition
```

## Whole-phase architecture audit

Relative to merged Phase-6 main, the accepted Phase-7 branch was exactly 14
commits ahead and zero behind. Production changes were confined to:

- lazy package-root public facades;
- declarative public specs and typed analysis construction;
- standardized catalog runtime IO and host-side HEALPix geometry;
- a small model-declared joint-prior bridge;
- the public inference facade and runtime binder;
- reusable core angular population models;
- the minimal PE/hierarchical seams required to apply the same angular factor to
  PE and selection weights.

No raw-survey, LSS/Q, multitracer, lensing, or campaign module was added. No
`universe_model` dispatcher or replacement mega-switchboard was introduced.
Core imports no future companion package.

The intentionally excluded domains remain excluded:

```text
raw DESI/KIBO/Legacy/GLADE schemas and masks       -> darksirens-surveys
Q_LSS / ensembles / latent fields / multitracer    -> darksirens-lss
weak / strong lensing                              -> darksirens-lensing
campaign-specific staged loading and CLI glue      -> not core
```

## Final accepted-head validation

Final Phase-7 head:

```text
be95e95bdf77144880cba5752ed5feafd40a697f
```

7F3 dedicated gate:

```text
34632081722 / 103371081194 SUCCESS
```

7F3 broad regression:

```text
34632081763 / 103371080968 SUCCESS
517 passed, 1 skipped
```

The single skip is the existing opt-in population-registry golden regeneration
test. The same broad job passed the core/companion import firewall.

All earlier Phase-7 workflows replayed successfully on the same exact head:

```text
7A  34632081557 / 103371080345 SUCCESS
7B  34632081698 / 103371081242 SUCCESS
7C1 34632081654 / 103371080964 SUCCESS
7C2 34632081670 / 103371080911 SUCCESS
7C3 34632081679 / 103371080994 SUCCESS
7D  34632081612 / 103371081102 SUCCESS
7E  34632081558 / 103371080182 SUCCESS
7F1 34632081584 / 103371080599 SUCCESS
7F2 34632081637 / 103371081339 SUCCESS
```

## PR #6 integration matrix

PR #6 (`Phase 7: public API and angular composition`) was opened from
`rebuild/phase7-public-api` at the exact accepted head. GitHub reported the PR
mergeable, with no review comments, review submissions, or unresolved threads.

The PR-triggered historical/scientific matrix completed **30/30 green**.
Representative load-bearing runs:

```text
reference integrity:          34632621092 SUCCESS
Phase 2 foundation:           34632621020 SUCCESS
Phase 3 population:           34632621110 / 103372863900 SUCCESS
Phase 4 spectral likelihood:  34632621037 / 103372863644 SUCCESS
Phase 5 catalog/dark/bright:  34632621119 / 103372864460 SUCCESS
Phase 6 inference / IO:       34632620969 / 103372863674 SUCCESS
Phase 6 runtime guards:       34632621113 / 103372864247 SUCCESS
Phase 6 sampler dispatch:     34632621066 SUCCESS
Phase 7 regression:           34632621022 / 103372864337 SUCCESS
Phase 7A public loaders:      34632621085 SUCCESS
Phase 7B public specs:        34632621043 SUCCESS
Phase 7C1 joint prior:        34632621118 SUCCESS
Phase 7C2 public model:       34632621051 SUCCESS
Phase 7C3 HEALPix geometry:   34632621036 SUCCESS
Phase 7D runtime binding:     34632621093 SUCCESS
Phase 7E public infer:        34632621138 SUCCESS
Phase 7F1 basic angular:      34632621053 SUCCESS
Phase 7F2 advanced angular:   34632621019 SUCCESS
Phase 7F3 angular wiring:     34632621071 SUCCESS
```

The Phase-6 adapter/persistence/diagnostic chain (6I–6S) also passed on the PR
head. No integration-only patch was required.

## Merge

PR #6 was squash-merged with an expected-head guard against
`be95e95bdf77144880cba5752ed5feafd40a697f`:

```text
merge SHA:  6ed3dc74aa0fcde4da128036cc3d56c29250d370
merge tree: 55dfb24cb84edebb0175409bd33be2a6a57ecb8a
```

The merge tree is exactly the accepted Phase-7 tree.

## Actual post-merge validation

Only `reference-integrity` push-triggered on `main` after the squash merge:

```text
workflow: reference-integrity
run:      34633321021
job:      103375170965 (frozen-reference)
status:   SUCCESS
```

No post-merge broad regression is claimed: the heavy historical/Phase-7 workflows
do not push-trigger on `main`. Their PR matrix already validated the exact tree
that was merged.

## Verdict

Phase 7 is complete, merged, and frozen at:

```text
main: 6ed3dc74aa0fcde4da128036cc3d56c29250d370
tree: 55dfb24cb84edebb0175409bd33be2a6a57ecb8a
```

Phase 8 must start from this exact merged `main`. Companion repositories remain
unstarted until Phase 8 freezes the core extension/API surface.