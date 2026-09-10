# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 1 — FROZEN NUMERICAL REFERENCE
status: COMPLETE
```

## Completed

- Phase 0 scientific ownership/dependency inventory completed.
- `darksirens-core` initialized with validation infrastructure only.
- Legacy unified K=1 golden bank frozen byte-identically in the core repository.
- Source golden blob SHA pinned: `560e44adb712763893111a3607f6d7ca8b168b7a`.
- Source fixture/test blob SHA pinned: `0f4e3301db2b4a73c574791a871d53fd56f0cad2`.
- Manifest records validated CPU stack, backend banks, cell ownership, coordinate fractions and comparison rules.
- Neutral per-owner candidate comparator added.
- Separate-import-root pinned-legacy replay runner added.
- Immutable-reference CI passes.
- Pinned legacy replay of all 15 cells passes.
- Core-owned cells pass the canonical `rtol=1e-12`, `atol=0` comparison in replay.
- Weak-lensing cell passes the canonical `rtol=1e-12`, `atol=0` comparison in replay.
- Legacy's documented ~`2.3e-12` CPU drift in the three Q/LSS cells is recorded explicitly and isolated to a `legacy-replay` profile; it does not weaken the canonical reconstruction target.

## Production repository state

### `darksirens-core`

Reference/validation infrastructure exists at HEAD:

```text
74559ef33931b3fe0400ada9a0cb11d3f9fbe48b
```

There is intentionally no reconstructed scientific `darksirens` package yet.

### `darksirens-surveys`

Not started.

### `darksirens-lss`

Not started.

### `darksirens-lensing`

Not started.

## Validation results

```text
reference-integrity workflow
run 34429433913
SUCCESS

legacy-reference-replay workflow
run 34429433906
job 102721583697
SUCCESS
```

The replay checkout uses the pinned legacy SHA in a separate directory/process root and calls the legacy unified-golden fixture's own evaluator. No reconstructed scientific code participates.

## Key dependency findings carried forward

- `core/types.py` mixes generic state with LSS and weak-lensing fields.
- ordinary `likelihood/core.py` imports weak-lensing machinery directly.
- `redshift/prior.py` combines ordinary priors with Q ensembles/latent fields and imports the latent seam from likelihood.
- `inference/loaders.py` stages ordinary catalog, counterpart, LSS, multitracer and mark state together.
- `likelihood/factory.py` is a multi-domain switchboard and will not be recreated as the target API.

## Architecture questions intentionally deferred

- minimal LSS redshift/auxiliary-likelihood protocol;
- minimal strong-lensing analysis protocol;
- exact optional flow API.

These remain deferred until ordinary core parity is established.

## Scientific questions

None opened. No scientific behavior changed in Phases 0-1.

## Next action

Phase 2 — build the minimal installable `darksirens-core` foundation, then migrate low-level scientific contracts in parity-gated slices. Start with package/import/JAX runtime, cosmology, and GW data contracts before moving hierarchical likelihood code.
