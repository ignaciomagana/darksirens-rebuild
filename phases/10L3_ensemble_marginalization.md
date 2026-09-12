# Phase 10 L3 — fixed-Q ensemble marginalization

Status: **ACCEPTED / FROZEN**

## Accepted LSS package

`ignaciomagana/darksirens-lss`

```text
main SHA:  6145a12d57f04676d0a00591db8b1904df658e4e
tree SHA:  a042697d24f4ce98c04b6434cfba5bb598874d84
```

No frozen-core or surveys source was modified.

## Permanent standalone gate

GitHub Actions:

```text
run:       34686723728
job:       103534881021
result:    SUCCESS
standalone artifact/gauge tests: 11 passed
```

The permanent package remains a lightweight peer extension:

- runtime package dependencies remain NumPy + HDF5 only;
- root `import darksirens_lss` imports neither `darksirens` nor JAX;
- no surveys/lensing dependency is introduced;
- core coupling remains lazy and is exercised only in the integration gate.

## Exact frozen-core integration gate

Temporary integration branch: `l3-private-core-probe`.

Accepted run:

```text
run:       34686820687
job:       103535133869
result:    SUCCESS
head:      a318f7f61a6de9622345ad5d811abe47904d36f3
```

The temporary head differs from accepted main only by the signed artifact-download workflow used to install the exact frozen core wheel. The branch was force-reset after acceptance to:

```text
6145a12d57f04676d0a00591db8b1904df658e4e
```

so the signed URL/workflow is not retained on the branch.

Exact frozen core artifact:

```text
core artifact id: 10294880218
wheel:            darksirens-0.1.0.dev0-py3-none-any.whl
wheel SHA-256:    4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

The integration workflow verified the wheel SHA before installation and verified the pinned runtime versions before testing.

Integration test result:

```text
pytest -q tests/test_fixed_table.py tests/test_ensemble.py
11 passed in 24.44 s
```

This is the L2 deterministic regression surface plus the new L3 ensemble surface. Together with the separate 11-test standalone gate, the accepted L3 package has 22 passing checks across its two intended environments.

## Public L3 API

L3 adds:

- `FixedTableEnsembleState`
- `EnsembleLikelihoodResult`
- `build_fixed_table_ensemble_state`
- `build_posterior_mean_q_state`
- `validate_shared_ensemble_provenance`
- `fixed_table_ensemble_log_likelihood`

## Frozen science semantics

### Member construction

A loaded `QArtifact.logq_members` table must have shape `(M, N_rows, N_grid)`, be finite, and contain at least one realization. If an `n_members` provenance field is present it must agree with the table.

The first member is constructed through the accepted L2 `build_fixed_table_state` path. That keeps the L2 contracts authoritative for:

- compact/global row alignment;
- exact core-z-grid compatibility;
- `c_mode`;
- `f_p_aware` refusal;
- depth/support semantics;
- observed-catalog cache construction.

Subsequent members reuse the same validated catalog and observed cache and differ only in the aligned `logq_rows` leaf.

### Deterministic posterior-mean fallback

The fallback state is

```text
Q_bar = mean_m[ exp(clip(log Q_m, -7, +7)) ]
```

and then `log Q_bar` is stored in the deterministic L2 state. It is explicitly **not** `exp(mean_m log Q_m)`.

This is a deterministic approximation. It is not the Bayesian LSS-member marginalization.

### Shared-member provenance

For a joint member axis:

1. all ensemble states must have equal `M`;
2. distinct ensemble states must have equal non-null `realization_set_id`;
3. `member_content_sha256` is per-artifact provenance and is **not** required to match across surveys;
4. reusing the exact same state object on the PE and selection sides is unambiguous even for a legacy artifact lacking a realization id;
5. otherwise an unverifiable/mismatched realization set fails closed unless the explicit `allow_unverified_shared_lss_members=True` override is supplied, in which case a warning states that the calculation is an independent-fields approximation.

### Likelihood marginalization

L3 is intentionally the transparent reference implementation. For each member `m`, it calls the complete frozen-core `host_density_log_likelihood` with member `m` on both the PE and selection sides. Only the completed likelihoods are then reduced:

```text
log L = logsumexp_m(log L_m) - log M.
```

Thus the per-member redshift-prior normalizer and selection correction stay paired within the same realization. No PE term, observed-catalog term, missing-completion term, or selection term is averaged separately across members.

This directly implements the L0C oracle contract and avoids the invalid construction in which member-dependent PE numerators are paired with a posterior-mean-Q selection denominator.

### Single-member limit

For `M=1`, `fixed_table_ensemble_log_likelihood` is numerically identical to the accepted deterministic frozen-core host-density likelihood for that member.

## Tests frozen at L3

The exact-core L3 tests establish:

- member ensemble construction through the L2 seam;
- posterior-mean-Q fallback is the arithmetic mean of clipped member Q values;
- that fallback differs from exponentiating the mean log-Q for a nontrivial ensemble;
- shared-realization validation depends on realization id + equal M, not equal member-content hashes;
- mismatched realization ids fail closed;
- unequal M fails closed;
- legacy distinct states fail closed unless the explicit independent-fields override is supplied;
- same-state PE/selection reuse is accepted;
- full-member marginalization equals an independent manual loop over the frozen-core deterministic likelihoods followed by `logmeanexp`;
- full-member marginalization is distinguishable from the deterministic posterior-mean-Q approximation;
- the `M=1` limit equals the deterministic likelihood.

## Deliberate non-goals

L3 does **not** factor member-independent work across realizations. It intentionally reevaluates the complete frozen-core likelihood once per member so it can serve as the numerical reference for later optimization.

L3 also does not introduce multitracer catalog mixing, a radial Poisson-lognormal solver, GP3D, or a latent field. Those remain later Phase-10 slices.

## Next slice

Proceed to **L4: radial Poisson-lognormal builder**, using the frozen L0A radial primitives and producing L1/L3-compatible Q artifacts. Do not optimize/factor L3 before the builder surface is reconstructed and validated.
