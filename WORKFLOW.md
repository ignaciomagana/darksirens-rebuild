# Reconstruction workflow

## Core rule

Do not refactor the legacy repository in place.

For each mature scientific path:

```text
identify exact legacy implementation
-> identify exact legacy regression tests
-> freeze small deterministic reference outputs
-> port the smallest coherent unit
-> compare at fixed parameters
-> simplify interfaces/private structure only after parity
-> rerun parity
```

Architecture and science are not changed in the same step.

## Phase order

### Phase 0 — inventory

Read the full legacy tree and classify every meaningful module/test/script/config/experiment as:

```text
CORE
SURVEYS
LSS
LENSING
LEGACY_ONLY
FUTURE_REVIEW
```

Map cross-domain imports and identify dependencies that must be inverted.

No production scientific porting.

### Phase 1 — freeze reference behavior

Build separate-process golden/parity runners against the pinned legacy SHA.

Freeze representative outputs for cosmology, GW stores, population models, catalog/redshift kernels, likelihoods, and selection effects before redesigning the implementation.

### Phase 2 — build core

Recommended sub-order:

```text
A  package scaffold + cosmology
B  GW PE/injection loaders and file contract
C  population models, including GP
D  spectral sirens + GW selection
E  catalog + complete/incomplete/bright sirens
F  inference/samplers/checkpointing/IO
G  optional mature flow support
H  small user-facing API
```

Every substep must preserve parity for the paths it touches.

### Phase 3 — freeze extension interfaces

After core is numerically stable, define only the small interfaces LSS and lensing require. Remove temporary LSS/lensing-specific state from core before freezing this boundary.

### Phase 4 — surveys

Port reusable catalog construction and prove that survey output loads directly through the core catalog contract.

### Phase 5 — LSS

Port table/lognormal mode first, then latent-field/count-likelihood mode. Require fixed-theta full core+LSS likelihood parity.

### Phase 6 — lensing

Port weak lensing first, then strong-lensing pair/cluster/partition machinery. Require fixed-theta full core+lensing parity and preserve the existing analytic-vs-Monte-Carlo validation paths.

### Phase 7 — cross-repository integration

Test clean installs and all allowed dependency combinations. Scan for forbidden imports and duplicated core physics.

### Phase 8 — final audit

Remove migration residue, stale compatibility shims, absolute paths, paper-specific state, unused hard dependencies, and lab-notebook/agent prose. Build distributions and run examples.

## Repository writes

Production code belongs only in:

```text
darksirens-core
darksirens-surveys
darksirens-lss
darksirens-lensing
```

This control repository records:

- architecture;
- decisions;
- file disposition;
- parity results;
- phase status;
- production commit/PR references;
- unresolved scientific questions.

## Scientific safety

Do not silently change:

- population normalization;
- PE-prior division;
- detector/source-frame Jacobians;
- injection draw-density handling;
- selection normalization;
- catalog weighting;
- completeness definitions;
- Q_LSS normalization;
- latent-field conventions;
- weak/strong lensing equations;
- clipping/floor behavior;
- JAX precision;
- quadrature/KDE definitions;
- random-number semantics;
- priors/fiducials;
- HDF5 schema interpretation.

If a legacy issue is discovered, record it under `Scientific questions` and keep migration parity separate from any later bug-fix PR.

## Commit discipline

Use small production commits with one migration purpose each. Do not make one giant cross-repository refactor commit.

After every material phase, update `STATUS.md` and `MIGRATION.md` in this repo with exact production SHAs and test results.
