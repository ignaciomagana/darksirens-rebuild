# Phase 7F1 — basic angular source-population models

## Scope

Phase 7F1 reconstructs only the reusable isotropic and dipole source-population
angular factors from the pinned legacy `darksirens.sky` layer. It deliberately
does not wire angular parameters into the public `Analysis` plan or hierarchical
likelihood yet, and it does not migrate the sphere-GP, 3-D GP, or multipole
models in the same slice.

Reference state:

```text
legacy repository:  ignaciomagana/darksirens
legacy SHA:         c042527238bd71421b792936bc48c3b815b90d6d
Phase-7 branch:     rebuild/phase7-public-api
7E accepted base:   f8aa93ed8bd7c7ebae3fe009f5e05db92cde456e
7F1 production:     fee40504cb765dfb34efed1d9a0243ac077d991f
7F1 accepted head:  6f4126792be9481860f893042e1efa253b46d1ec
accepted tree:      8d947f40ea3f72e07859ad08c450a47c348c2e50
```

## Ownership

The migrated models are source-population factors

```text
R(theta, z, n-hat) = R_pop(theta, z) * g(n-hat, z)
```

and therefore live under `darksirens.population.angular`, not under survey,
LSS, or lensing ownership. No companion-package import is introduced.

## Accepted behavior

The slice adds:

- canonical names `isotropic` and `dipole`;
- exact frozen LaTeX display strings;
- cached construction under `jax.ensure_compile_time_eval()`;
- parameter-bound/prior-kind parsing;
- isotropic-limit fiducials;
- fixed-parameter helpers;
- prior-volume-correction helper;
- the frozen dipole `ball3` joint-prior declaration;
- exact frozen dipole global-validity backstop `|d| <= 1`;
- exact mean-one angular factor
  `g = 1 + nx*dx + ny*dy + nz*dz`.

The isotropic model is an exact no-op (`log g == 0`) with no parameters.
The dipole uses the exact frozen labels, bounds, and machine names:

```text
$d_x$  [-1, 1]  sky_dx
$d_y$  [-1, 1]  sky_dy
$d_z$  [-1, 1]  sky_dz
```

and declares:

```python
("ball3", (r"$d_x$", r"$d_y$", r"$d_z$"))
```

so the accepted Phase-6 prior transform maps the unit cube onto the normalized
unit-ball prior rather than rejecting a cube outside the physical region.

## Parity method

`tools/probe_angular_basic.py` evaluates the pinned legacy implementation and
the reconstructed candidate in separate Python processes. The JSON records
compare exactly:

- lower/upper bounds as `float.hex()` values;
- labels;
- prior-kind triples;
- display LaTeX;
- isotropic fiducials as `float.hex()` values;
- joint constraint groups;
- deterministic `log_g` values as `float.hex()` values;
- prior-volume corrections.

The exact record comparison passed.

## Harness-only failure

The first dedicated run failed before the legacy model was evaluated because
the focused legacy process imported a frozen cosmology module that required
`astropy`, while the narrow parity workflow had not installed it. Candidate
production tests were already green.

No production code changed. The only fix was to pin the already validated
`astropy==6.1.4` in the dedicated workflow.

## Acceptance gates

Exact-head gates:

```text
basic angular parity: 34624190605 / 103345183970  SUCCESS
broad regression:     34624190465 / 103345183648  SUCCESS
7E public infer:       34624190500 / 103345183869  SUCCESS
7D runtime binding:   34624190458 / 103345183723  SUCCESS
7C3 HEALPix geometry: 34624190424 / 103345183254  SUCCESS
7C2 public model:     34624190648 / 103345184332  SUCCESS
7C1 prior resolver:   34624190393 / 103345183331  SUCCESS
7B public specs:      34624190431 / 103345183346  SUCCESS
7A public loaders:    34624190690 / 103345184421  SUCCESS
```

The exact-head broad suite completed with:

```text
506 passed, 1 skipped
```

The skip is the existing opt-in population-registry golden regeneration test.
The companion-import boundary passed.

## Closure

Phase 7F1 is accepted at
`6f4126792be9481860f893042e1efa253b46d1ec`.

The next angular migration slice, 7F2, is limited to the remaining reusable
source-population model/registry primitives: `sphere_gp`, `sphere_gp_z`,
`overdensity_gp`, `multipole`, and `multipole_l3`. It must preserve their
normalization contracts and multipole prior-volume correction, remain free of a
runtime healpy dependency, and be parity-gated before any public-plan or
likelihood wiring.