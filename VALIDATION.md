# Numerical validation contract

## Reference

All migration parity is measured against:

```text
ignaciomagana/darksirens
c042527238bd71421b792936bc48c3b815b90d6d
```

## Separate-process rule

The legacy and rebuilt core both import as `darksirens`. Never import them in the same Python interpreter.

Use separate environments/processes:

```text
legacy runner -> serialized reference output
new runner    -> serialized candidate output
neutral comparator -> parity report
```

A golden manifest records:

```text
legacy SHA
Python/NumPy/SciPy/JAX/JAXLIB versions
input hashes
configuration
fixed parameter points
output dtype/shape
rtol/atol
max absolute difference
max relative difference
```

Where a legacy test requires bit identity, preserve bit identity.

## Core parity matrix

### Cosmology

- luminosity distance;
- inverse luminosity distance;
- comoving distance;
- differential comoving volume;
- interpolation edges;
- precision/runtime configuration.

### GW I/O

- PE loading;
- selection loading;
- event/sample indexing;
- format-version checks;
- PE weights;
- injection `pdraw`;
- `chieff`;
- `chieff_reference`;
- component-spin basis;
- malformed metadata rejection;
- loader health checks.

### Population

- mass models;
- q/pairing models;
- spin models;
- mixtures;
- grammar/registry;
- fixed GWTC parameters;
- normalization;
- GP population models.

### Catalog/redshift

- spectral/volume redshift model;
- galaxy redshift kernels;
- compact pixel/row views;
- ordinary completeness;
- complete-catalog limit;
- bright/counterpart path;
- host-property weights.

### Likelihood/selection

- per-event fixed-theta contribution;
- full small-catalog fixed-theta likelihood;
- GW selection term;
- effective sample size;
- likelihood Monte Carlo variance;
- support/provenance guard behavior.

### Inference/IO

- parameter names/order where required for compatibility;
- prior transforms;
- fixed vs sampled values;
- sampler smoke tests;
- checkpoint/resume semantics;
- result serialization;
- settings/provenance;
- import-side-effect tests.

## LSS parity matrix

- ordinary-completeness/LSS boundary;
- Q_LSS table values;
- row/pixel gather order;
- missing-count conservation;
- ensemble/marginalization;
- single tracer;
- multitracer;
- provenance rejection;
- latent basis construction;
- latent count likelihood;
- field normalization;
- full fixed-theta core+LSS likelihood.

## Lensing parity matrix

- weak-lensing `p(mu|z)`;
- WL normalization/quadrature;
- WL event weighting;
- SIS optical depth;
- image marks;
- pair KDE;
- pair likelihood;
- cluster likelihood;
- cluster selection;
- both-detected approximation;
- exactly-one-detected channel;
- Finn-Chernoff analytic vs direct Monte Carlo;
- lensed-injection loading;
- cluster loading;
- partition enumeration/marginalization;
- file-contract/preflight behavior;
- full fixed-theta core+lensing likelihood.

## Acceptance standard

New tests that validate only the rebuilt code against itself are not sufficient. Existing legacy regression tests and deterministic legacy outputs are the primary scientific assets.

Stochastic posterior similarity may be used as an integration check, but it never replaces pointwise likelihood and selection parity.
