# Reconstruction status

## Reference

```text
legacy repository: ignaciomagana/darksirens
pinned SHA:        c042527238bd71421b792936bc48c3b815b90d6d
control repo:      ignaciomagana/darksirens-rebuild
```

## Current phase

```text
PHASE 0 — INVENTORY AND DEPENDENCY MAP
status: COMPLETE
```

## Completed

- Four-package ownership model confirmed against the actual legacy code.
- Full package-domain migration inventory recorded under `inventories/`.
- Major cross-domain dependency inversions identified and ordered.
- Experiment/script selective-promotion policy recorded.
- Legacy test assets mapped by new package ownership.
- CPU-fast legacy reference gate identified: 69 files / 823 collected tests.
- Unified K=1 fixed-coordinate golden bank selected as central Phase-1 parity anchor.
- GP population models confirmed as core.
- LSS and lensing confirmed as mature first-class companion packages.

## Production repository changes

None. `darksirens-core`, `darksirens-surveys`, `darksirens-lss`, and `darksirens-lensing` have not been modified by the rebuild work.

## Numerical parity

Not yet re-established in the new packages. Phase 1 freezes serialized legacy reference outputs and a separate-process comparator before runtime migration starts.

## Key dependency findings

- `core/types.py` mixes generic state with LSS and weak-lensing fields.
- ordinary `likelihood/core.py` imports weak-lensing machinery directly.
- `redshift/prior.py` combines ordinary priors with Q ensembles/latent fields and imports the latent seam from likelihood.
- `inference/loaders.py` stages ordinary catalog, counterpart, LSS, multitracer and mark state together.
- `likelihood/factory.py` is a multi-domain switchboard and will not be recreated as the target API.

## Architecture questions intentionally deferred

- minimal LSS redshift/auxiliary-likelihood protocol;
- minimal strong-lensing analysis protocol;
- exact optional flow API.

These are frozen only after ordinary core parity.

## Scientific questions

None opened. No scientific behavior was changed in Phase 0.

## Next action

Phase 1 — freeze the legacy numerical reference/golden harness. No mathematical kernel should be reorganized before that exists.
