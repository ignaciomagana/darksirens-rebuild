# Phase 4 report — spectral-siren likelihood and GW selection

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:  ignaciomagana/darksirens-core
base core SHA:     e0b40fef65261a27b67aa9657a97216df3e8444f
working branch:    rebuild/phase4-spectral-likelihood
```

## Status

INVENTORY / PARITY DESIGN IN PROGRESS. No Phase-4 scientific code is accepted
yet. Do not advance to catalog/redshift work until this phase passes its own
focused gate, the full reconstructed regression suite, and separate-process
legacy/new spectral-likelihood parity.

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

The spectral redshift prior is the normalized comoving-volume prior and must use
only the reconstructed core cosmology layer.

## Explicitly out of scope

The following legacy functionality is not to be pulled into Phase 4 merely
because it shares a file with the ordinary likelihood:

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

### CORE / migrate now

```text
darksirens/likelihood/selection.py
    -> darksirens/selection/gw.py

# likelihood mathematics currently misplaced under inference
darksirens/inference/utils.py:
    M1DET_Q_DL_COORDS
    log_jacobian_m1src_q_z_to_m1det_q_dL
    log_jacobian_dL_to_z
    log_target_density_m1det_q_dL
    log_sample_weight
    -> darksirens/likelihood/weights.py

# generic runtime event construction
darksirens/likelihood/events.py
    -> runtime helpers owned by darksirens/gw and/or darksirens/likelihood
       after adapting to reconstructed GW types

# catalog-free branch only
darksirens/likelihood/core.py
    -> a small spectral-siren likelihood implementation under
       darksirens/likelihood/{event,hierarchical}.py
```

### REUSE, do not duplicate

The reconstructed core already owns the required flat-CPL cosmology operations:

```text
darksirens.cosmology.distances.z_of_dL
darksirens.cosmology.distances.z_of_dL_precomputed
darksirens.cosmology.distances.ddL_of_z
darksirens.cosmology.distances.ddL_of_z_precomputed
darksirens.cosmology.distances.dV_of_z
```

`darksirens.cosmology.volume` already exposes the differential comoving volume.
Phase 4 should add only the normalized spectral-volume-prior helper if needed;
it must not recreate the distance implementation.

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

The legacy `likelihood/core.py` and `factory.py` are mixed monoliths and are not
migration units. Only the catalog-free code path may be reconstructed here.

## Core equations that must remain unchanged

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

with the reliability boundary

```text
N_eff > max(
    5 Nobs,
    Nobs^2 / (max_likelihood_variance - sum_i var(log Z_i)),
)
```

using the existing finite variance-budget floor and the existing validated soft
wall for gradient samplers. Default `max_likelihood_variance = 1.0` is retained.

No coefficient or guard threshold may change during reconstruction.

## Initial focused legacy tests

The following are Phase-4-owned or contain Phase-4-owned assertions and should
be migrated/adapted rather than replaced by weaker tests:

```text
tests/test_likelihood_coordinates.py
tests/test_selection_batching.py
tests/test_selection_gradient_safety.py
tests/test_selection_correction_coefficient.py
tests/test_selection_variance_guard.py
tests/test_selection_soft_guard.py
tests/test_selection_consolidation.py
tests/test_spin_block_plumbing.py   # runtime/padding + selection spin assertions
```

`tests/test_selection_prior_model.py` is primarily a legacy `universe_model`
string-dispatch contract and is not automatically part of the new architecture.
Survey/completeness tests named `test_selection_*` belong to later survey/catalog
work, not to this GW-selection phase.

The legacy full test tree must not be run CPU-only; the legacy testing guide
records pathological memory use for that mode. Phase 4 uses explicit pinned
legacy probes/tests plus the full, much smaller reconstructed-core suite.

## Spectral fixed-theta parity target

Build a deterministic synthetic fixture containing multiple PE events and a
found-injection set in the canonical `(m1det, q, dL, chieff)` basis, including:

- non-uniform PE proposal weights;
- non-uniform injection draw weights;
- at least one invalid/masked sample;
- selection length not divisible by the chosen batch size;
- one chi_eff-only population case;
- one component-spin population case if the legacy/new runtime shape permits a
  clean common fixture.

Evaluate in separate processes against pinned legacy and reconstructed core at
several fixed points in `(H0, population parameters)` and serialize:

```text
per-event log Z_i
per-event MC variance_i
log_mu
N_eff
selection correction
full spectral log likelihood
```

The comparison target is `rtol=1e-12`, `atol=0` unless exact equality is
achieved. Any larger discrepancy must be investigated; the tolerance is not to
be relaxed to make the gate pass.

## Phase-4 acceptance gate

Before a PR may be opened:

```text
ruff F/E9 over src/tests/tools: PASS
Phase-2/3 regression surface: PASS
full reconstructed pytest suite: PASS
canonical-coordinate/Jacobian tests: PASS
GW-event padding and spin plumbing: PASS
selection batching: PASS
selection hard/soft guard tests: PASS
selection gradient NaN-safety: PASS
per-event MC variance tests: PASS
pinned legacy spectral probe: PASS
reconstructed spectral probe: PASS
legacy/new fixed-theta parity at rtol=1e-12: PASS
package-root import remains light: PASS
no catalog/LSS/lensing/flow imports in core Phase-4 modules: PASS
```

After the branch gate is green, open the PR and require all older PR workflows
(`reference-integrity`, `phase2-foundation`, `phase3-population`) plus the new
Phase-4 workflow to pass at the exact accepted head. Then diff-review, squash
merge with an expected-head guard, verify core `main`, and record the merge here
before Phase 5.

## Next action

Finish exact unit-test/function inventory, then implement the smallest
catalog-free slice. Do not copy legacy `likelihood/core.py` or `factory.py`
wholesale.
