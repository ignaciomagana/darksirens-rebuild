# Phase 6Q checkpoint — NumPyro static contract

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   73115e1d403e1c6eefa646c7e68867d6831dc7df
accepted 6Q head:  cfbde4a2d202398a531dab5646314ac1a485fcd5
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6Q reconstructs only the static NumPyro/NUTS contract that is resolved before model construction or NUTS initialization. NumPyro itself is not imported by this slice.

Candidate surface:

```text
src/darksirens/inference/numpyro_static.py
```

Frozen contract: finite ordered lower/upper bounds; NumPyro Beta compatibility restricted to the frozen [0,1] bounds; exact classification of `conditional_upper`; exact rejection/warning behavior for the other joint constraints; refusal of chained conditional bounds; midpoint `init_values`; frozen NUTS defaults and explicit overrides; validation of warmup/sample/chain/init-search counts. JAX array construction is lazy and module import loads neither JAX nor NumPyro.

## Acceptance

```text
dedicated 6Q gate: 34579421386 / 103199274439 SUCCESS
historical gate:   34579421315 / 103199274166 SUCCESS
runtime guards:    34579421323 / 103199274044 SUCCESS
```

The dedicated gate passed focused tests, lazy import checks, frozen legacy AST probing, reconstructed probing, and exact behavior/stdout/error parity. The broad exact-head gate preserved the full reconstructed suite, earlier Phase-6 parity, and Phase-5 scientific fixtures.

## Next

Proceed to 6R: reconstruct only NumPyro initial-point selection, `conditional_upper` initial-support repair, and JAX likelihood-gradient preflight. Keep NumPyro model/NUTS/MCMC execution for a later slice.
