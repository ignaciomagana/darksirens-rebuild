# Phase 11 L0A — weak-lensing legacy reference

Status: **ACCEPTED / FROZEN**

## Frozen oracle

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
schema:            darksirens-lensing-l0a-wl-reference-1
```

Committed golden:

```text
references/lensing_l0a_wl_legacy_reference.json
```

No production file in `darksirens-lensing` existed when this reference was
accepted.

## Bootstrap evidence

```text
run/job:   34734277278 / 103662732502
head:      a8964934b2affaa0067304918de9a8042866ad78
artifact:  10310665848
name:      lensing-l0a-wl-legacy-reference
digest:    sha256:ae3f26c991cc9b1d46a1b5050f5413b45c49336ce4a0828d767703da8963bc91
result:    SUCCESS
```

The immediately preceding run `34734197409` failed before any scientific
assertion because the probe attempted to mutate a read-only NumPy view returned
from a JAX array while constructing a poisoned tabulated-PDF fixture.  The
fixture was changed to a writable copy; no legacy source or scientific
assertion changed.

## Committed-golden replay

```text
run/job:   34734348866 / 103662929617
head:      e17cbc23a5d6558903e584c9873769188a3b8cf6
artifact:  10309983457
digest:    sha256:c4bc75603325d937bee80133c3eff03b2ae9cad4e21388d380627174ac385019
result:    SUCCESS
```

The workflow evaluates the oracle in two independent Python processes, checks
scientific structure, then compares the regenerated output to the committed
golden with tight floating tolerances.  The replay passed all three gates.

## Frozen analytic weak-lensing PDF

For the default reference parameters

```text
a = 0.004
b = 1.5
s^2(z) = a z^b
m(z) = -s^2(z)/2
```

at

```text
mu = [0.72, 0.91, 1.0, 1.13, 1.42]
z  = [0.2,  0.5,  1.0, 1.5,  2.0]
```

the pinned legacy log density is

```text
[-147.27410664645961,
   -0.6417405859341362,
    1.8412919257264506,
    0.33710377868583696,
   -4.639594271828027]
```

A deliberately broad lognormal checked by direct 200-node Gauss-Legendre
quadrature gives both normalization and flux conservation to
`1.98e-13` maximum absolute error.  Thus L1 must preserve both

```text
int p_WL(mu|z) dmu = 1
<mu> = 1.
```

## Frozen tabulated-PDF semantics

The L0A fixture uses an exactly bilinear synthetic `log p` table.  Interpolation
reproduces the analytic bilinear surface exactly in the frozen run, including
queries outside both grids after edge clamping.

The accepted safety semantics are:

```text
-inf log-density cell: allowed
NaN log-density cell:  rejected
duplicate grid node:   rejected
outside-grid query:    constant edge extrapolation after coordinate clipping
```

## Frozen quadrature conventions

Production tabulated-WL quadrature:

```text
N_mu = 16
ln(mu) range = [-0.6, 0.6]
```

First four magnification nodes:

```text
[0.5523128914289362,
 0.5673692152791341,
 0.5948900256068521,
 0.6355638985045634]
```

Last four:

```text
[1.5734059192992693,
 1.6809829665237568,
 1.7625207238429748,
 1.8105679145254312]
```

The 16-node standardized Gauss-Hermite rule has unit total Gaussian weight.
The 32-node SIS `y` rule integrates `p(y)=2y` to exactly one at the stored
precision.

For the calibrated lognormal `(a,b)=(0.004,1.5)`, the production Hermite
importance-ratio rule has absolute log-integral errors

```text
z_app = [0.05, 0.5, 1.0, 2.0]
error = [4.3826162317295303e-16,
         6.073854602290052e-07,
         3.63344406162792e-07,
         8.179959007609088e-08]
```

against the dense reference.  At `a=0` the same errors are exactly zero.

## Frozen event-weight seam

The structural dispatcher invariant is exact:

```text
wl_enabled=False  ->  standard log_sample_weight bit-for-bit
```

The lognormal Hermite kernel also has an exact unlensed reduction on the frozen
toy PE batch:

```text
wl_a = 0
max |logw_WL - logw_standard| = 0.0
```

The reverse-mode derivative through that point is finite.  For the frozen toy
batch,

```text
d/da sum_i logw_i | a=0 = -0.21676225311904412
```

so the gradient-safe zero-variance construction is part of the accepted
contract, not only a value-level special case.

At the calibrated `a=0.004`, the seven frozen per-sample shifts relative to the
standard path are

```text
[-5.6935673994118474e-05,
  2.7637844276817700e-04,
 -2.8991019005708550e-04,
  3.2055513965367766e-04,
 -1.5000496456707424e-04,
 -8.4443676716006170e-05,
 -1.5741869731300540e-05]
```

All are finite.

## Scientific interpretation frozen by L0A

The Hermite path is not merely a quadrature of `p_WL(mu|z_app)`.  Its nodes are
sampled from the apparent-redshift proposal, while the stated target density is
`p_WL(mu|z_s(mu))`; the mature kernel therefore carries the explicit
proposal-to-target ratio

```text
p_WL(mu | z_s(mu)) / p_WL(mu | z_app).
```

The physical distance/Jacobian convention remains

```text
dL_app = dL(z_s) / sqrt(mu).
```

Any L2 event-weight implementation must preserve this complete algebra and the
`a=0` value/gradient limit.

## Next slice

Proceed to **L1: package scaffold plus weak-lensing PDF and quadrature
primitives** in `ignaciomagana/darksirens-lensing`.

L1 must not yet own PE event weighting or a core `InferenceTarget`; those belong
to L2 and are already pinned by this L0A reference.
