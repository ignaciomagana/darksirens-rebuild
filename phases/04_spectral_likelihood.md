# Phase 4 report — spectral-siren likelihood and GW selection

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
base core SHA:     e0b40fef65261a27b67aa9657a97216df3e8444f
working branch:    rebuild/phase4-spectral-likelihood
accepted head:     cfdb138d40d66614bf9b1264c2574d0b497b812d
PR:                #3
squash merge SHA:  0f97feff7eb283a1f541bef9a776c9347084e70e
```

## Status

COMPLETE. Phase 4 was accepted at the exact branch head, all historical and
Phase-4 PR workflows passed at that same head, the complete changed-file diff was
reviewed for ownership/scientific-boundary violations, PR #3 was squash-merged
with `expected_head_sha`, and `main` was verified at the merge SHA above. The
post-merge frozen-reference workflow also passed.

## Scientific scope

Phase 4 owns the catalog-free hierarchical GW likelihood used by spectral
sirens, including:

- the canonical sample-coordinate transformation
  `(m1src, q, z) -> (m1det, q, dL)`;
- per-PE-sample and per-injection importance weights;
- per-event log-evidence Monte-Carlo reduction and variance estimate;
- GW selection integral `mu`, `N_eff`, and selection Monte-Carlo variance;
- the hard and soft reliability guards on the total log-likelihood variance;
- fixed-theta catalog-free spectral-siren hierarchical likelihood assembly;
- runtime GW-event construction, structural validity masks, spin-block plumbing,
  and selection padding/batching needed by that likelihood.

The spectral redshift prior is the normalized comoving-volume prior and uses only
the reconstructed core cosmology layer.

## Explicitly out of scope

The following legacy functionality remains outside Phase 4:

- galaxy catalogs and catalog KDEs;
- completeness corrections and survey selection functions;
- Q_LSS, latent fields, member marginalization, or multitracer machinery;
- marked-host models;
- weak or strong lensing;
- cluster/pair likelihoods;
- sky-anisotropy models;
- normalizing-flow PE surrogates or pdet emulators;
- sampler implementations and inference prior transforms;
- the old monolithic application CLI and `universe_model` dispatcher.

## Legacy ownership map

### CORE / migrated now

```text
darksirens/likelihood/selection.py
    -> darksirens/selection/gw.py

darksirens/inference/utils.py likelihood mathematics
    -> darksirens/likelihood/weights.py

darksirens/likelihood/events.py runtime event construction/padding
    -> darksirens/gw/{types,runtime}.py

catalog-free branch only of darksirens/likelihood/core.py
    -> darksirens/likelihood/{event,hierarchical}.py
```

### REUSED, not duplicated

The reconstructed core cosmology layer provides the required flat-CPL operations:

```text
darksirens.cosmology.distances.z_of_dL
darksirens.cosmology.distances.z_of_dL_precomputed
darksirens.cosmology.distances.ddL_of_z
darksirens.cosmology.distances.ddL_of_z_precomputed
darksirens.cosmology.distances.dV_of_z
```

`darksirens.cosmology.volume` now also exposes the normalized catalog-free
comoving-volume density used by the spectral likelihood.

### LATER OWNER

```text
darksirens/likelihood/catalog_views.py      -> catalog phase
darksirens/likelihood/latent_q.py           -> darksirens-lss
darksirens/likelihood/wl_weight.py          -> darksirens-lensing
darksirens/likelihood/cluster_likelihood.py -> darksirens-lensing
darksirens/likelihood/cluster_selection.py  -> darksirens-lensing
darksirens/likelihood/pair_kde.py           -> darksirens-lensing
darksirens/likelihood/likelihood_with_clusters.py -> darksirens-lensing
darksirens/likelihood/flow_events.py        -> future optional flow layer
darksirens/likelihood/block_sizing.py       -> later inference/runtime phase
darksirens/likelihood/factory.py            -> later high-level model/infer API
```

The legacy `likelihood/core.py` and `factory.py` remain mixed monoliths and were
not migrated as units.

## Core equations preserved

### Canonical coordinate Jacobian

For

```text
m1det = (1 + z) m1src
q     = q
dL    = dL(z)
```

the target density in `(m1det, q, dL)` carries

```text
log |J| = log[d(dL)/dz] + log(1 + z)
```

and the importance weight subtracts this quantity.

### Per-event Monte-Carlo term

For `n_i` PE samples with log weights `ldw_ij`,

```text
log Z_i = logsumexp(ldw_i) - log(n_i)
var(log Z_i) = sum_j w_ij^2 / (sum_j w_ij)^2 - 1/n_i
```

Masked samples remain zero-weight members of the same PE sample set and count in
`n_i`.

### GW selection term

For detected injections drawn from `Ndraw` total injections,

```text
mu = (1/Ndraw) sum_k w_k
1/N_eff = sum_k w_k^2/(sum_k w_k)^2 - 1/Ndraw
```

The accepted selection correction is

```text
-Nobs log(mu) + Nobs(Nobs + 3)/(2 N_eff)
```

with reliability boundary

```text
N_eff > max(
    5 Nobs,
    Nobs^2 / (max_likelihood_variance - sum_i var(log Z_i)),
)
```

using the existing finite variance-budget floor and validated soft wall for
gradient samplers. Default `max_likelihood_variance = 1.0` is retained. No
coefficient or guard threshold changed.

## Implementation history

The first low-level Phase-4 slice introduced:

```text
src/darksirens/_numerics.py
src/darksirens/gw/types.py
src/darksirens/gw/runtime.py
src/darksirens/likelihood/weights.py
src/darksirens/selection/gw.py
src/darksirens/selection/__init__.py
```

Clean lower-level acceptance was reached at:

```text
head:         220375e6877d755f34131d9d793ad4db38f0b89a
workflow run: 34441480533
job:          102757247600
result:       SUCCESS
```

Two non-scientific issues were caught before that checkpoint: intended GW runtime
exports were missing from `__all__`, and one copied soft-guard test contained a
future `likelihood.factory` assertion. A temporary bootstrap workflow also raced
that cleanup and rewrote the test once. The bootstrap was deleted and the clean
owner-local rerun passed. No numerical behavior or scientific tolerance changed.

The spectral assembly then added:

```text
src/darksirens/cosmology/volume.py
src/darksirens/likelihood/event.py
src/darksirens/likelihood/hierarchical.py
src/darksirens/likelihood/__init__.py

tests/test_event_mc_variance.py
tests/test_pe_event_reduction.py
tests/test_spectral_volume_prior.py
tests/test_spectral_likelihood.py

tools/probe_spectral_likelihood.py
tools/compare_spectral_probe.py
```

The block-reduction tests initially used `rtol=1e-13`. One full-suite run exposed
a single XLA reassociation difference of `1.66533454e-16` absolute / about
`1.92e-13` relative in the event-variance vector. The pinned legacy
`test_pe_event_vectorization.py` already documents this exact class of
reassociation and uses `rtol=1e-12, atol=0` for PE-block comparisons. Only the
candidate's block-shape unit test was aligned to that existing legacy contract.
The strict legacy/new fixed-theta parity tolerance was not changed.

## Final branch acceptance

Permanent workflow:

```text
branch head:      cfdb138d40d66614bf9b1264c2574d0b497b812d
workflow run:     34445525661
job:              102769369532
workflow result:  SUCCESS
```

Acceptance details:

```text
ruff F/E9 + compileall:                PASS
coordinate/runtime tests:             9 passed
GW-selection focused tests:            50 passed
spectral-likelihood focused tests:     15 passed
full reconstructed suite:              199 passed, 1 regen-only skip
dependency-boundary audit:             PASS
pinned legacy spectral probe:          PASS
reconstructed spectral probe:          PASS
legacy/new fixed-theta spectral parity: PASS
```

The parity fixture contains 3 PE events, 8 samples/event, 257 found injections,
`Ndraw=4096`, nonuniform PE/injection proposal weights, masked samples, and a
selection batch of 64. It evaluates three fixed `(H0, population)` points and
serializes:

```text
per-event log Z_i
per-event MC variance_i
log_mu
N_eff
selection correction
full spectral log likelihood
```

The legacy and reconstructed outputs are exactly identical at all serialized
values:

```text
max_abs = 0.000e+00
max_rel = 0.000e+00
comparison rtol = 1e-12
comparison atol = 0
```

The workflow imports legacy and reconstructed `darksirens` in separate Python
processes, so package-name collision cannot mask parity errors.

## PR exact-head gate

PR #3 was opened with base `main` at Phase-3 SHA `e0b40fef...` and head fixed at
`cfdb138d...`. The head remained unchanged through review. All required
PR-triggered workflows passed at that exact head:

```text
reference-integrity
  run: 34446633557
  job: 102772728746
  result: SUCCESS

phase2-foundation
  run: 34446633595
  job: 102772729079
  result: SUCCESS

phase3-population
  run: 34446633551
  job: 102772729151
  result: SUCCESS

phase4-spectral-likelihood
  run: 34446633527
  job: 102772728950
  result: SUCCESS
```

The Phase-4 PR job again passed its focused tests, full reconstructed suite,
dependency audit, independent legacy and candidate probes, and strict fixed-theta
parity. The historical Phase-3 job again passed its population legacy/candidate
comparison and optional-dependency boundary.

## Diff review

Relative to Phase-3 `main`, the accepted branch was 21 commits ahead and 0
behind, with 25 changed files, 3254 additions and 2 deletions. The review covered
the Phase-4 workflow; `_numerics`; cosmology volume helper; GW runtime/type and
namespace deltas; likelihood event/hierarchical/weight code; selection estimator
and guard code; focused coordinate, variance, batching, gradient, spectral and
spin tests; and both parity tools.

No blocker was found. The changed scientific/runtime code stays within the
frozen Phase-4 ownership boundary. No concrete catalog, survey, LSS, lensing,
flow, sampler, or CLI dependency entered the reconstructed likelihood/selection
runtime. The component-spin shape not present in the chi-eff-only legacy parity
fixture is separately pinned by runtime, padding, batched-selection, and
population-forwarding tests.

## Merge and main verification

PR #3 was squash-merged with:

```text
expected head:    cfdb138d40d66614bf9b1264c2574d0b497b812d
merge method:     squash
merge SHA:        0f97feff7eb283a1f541bef9a776c9347084e70e
merged:           2026-09-10 06:51:15 UTC
```

GitHub `main` was then fetched directly and points exactly to:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

The merge commit has parent `e0b40fef65261a27b67aa9657a97216df3e8444f`
and tree `da49fb40eb97c63707314751fc3ce0bd3643a42e`, the accepted branch tree.
The post-merge push-triggered frozen-reference check also passed:

```text
reference-integrity run: 34447108888
job:                    102774202182
result:                 SUCCESS
```

## Phase-4 conclusion

Phase 4 reproduces the pinned legacy catalog-free spectral likelihood and GW
selection machinery without a scientific behavior change. The accepted core
`main` for the next phase is:

```text
0f97feff7eb283a1f541bef9a776c9347084e70e
```

## Next action

Begin Phase 5 only from the verified merge SHA above. Read the control-plane
catalog/dark/bright-siren phase prompt and ownership documents before creating a
branch. Phase 5 must add the smallest core catalog contract and complete/incomplete
dark-siren likelihood composition while preserving the existing spectral path;
bright-siren counterpart support is included only according to the frozen phase
contract. LSS, survey construction, lensing, flows, samplers, and the old
application dispatcher remain out of scope.
