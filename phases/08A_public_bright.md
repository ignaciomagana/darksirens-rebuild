# Phase 8A — public bright-siren composition

Status: **ACCEPTED**

```text
phase base:        6ed3dc74aa0fcde4da128036cc3d56c29250d370
accepted head:     5256141e00a2d96a72b9cbf2182a77174c8c269e
accepted tree:     6252d1725ee07562840f0ce48b0dc6fe90a4aee4
branch:            rebuild/phase8-core-freeze
legacy reference:  c042527238bd71421b792936bc48c3b815b90d6d
```

## Scope

Phase 8A closes the remaining public ordinary bright-siren gap without changing
the already parity-gated Phase-5 bright likelihood.

The accepted slice adds only composition/binding:

- lazy public `darksirens.Counterpart` exposure;
- typed bright-siren analysis construction through
  `ds.model(..., counterparts=..., counterpart_nside=...)`;
- explicit bright redshift marker carrying one resolved counterpart per event
  and the HEALPix `nside` defining its global-pixel frame;
- mutual exclusion of bright counterparts with ordinary catalog/completeness
  composition;
- explicit rejection of non-isotropic angular composition for bright sirens
  rather than silently dropping the requested angular factor;
- host-side PE pixelization into the counterpart HEALPix frame using the
  accepted dependency-free RING geometry;
- a zero-galaxy compact `GalaxyCatalog` used only to preserve the accepted
  compact-row -> global-pixel mapping consumed by the counterpart prior;
- bright dispatch from the existing runtime binder to the accepted
  `bright_siren_log_likelihood`;
- selection remains catalog-free volume/spectral selection exactly as in the
  frozen model.

No raw counterpart parser, survey schema, completeness path, LSS state, lensing
state, or new scientific arithmetic was introduced.

## Frozen behavior

`Counterpart` remains the existing core resolved object:

```text
z, dz, global pixel, sky_marginalized
```

The public layer deliberately does not recreate the legacy CLI's raw
`RA DEC Z` parser. Input preparation may resolve a counterpart onto the chosen
HEALPix frame; core inference consumes the resolved object.

Exactly one counterpart per GW event is required at binding/runtime. The bright
PE numerator remains the counterpart Gaussian times normalized volume prior,
with the resolved-pixel gate unless `sky_marginalized=True`. The selection
integral intentionally remains the catalog-free normalized volume prior.

## Validation

Dedicated 8A gate on the exact accepted head:

```text
workflow: 34634374241
job:      103378585284
result:   SUCCESS
```

It passed:

- definite-error lint/compile;
- fresh-process package-root import check (`jax`/`h5py` remain unloaded);
- focused public bright construction/binding tests;
- separate-process frozen legacy ordinary/bright likelihood fixture;
- reconstructed candidate fixture;
- unchanged Phase-5C legacy/candidate bright parity requirement.

Phase-8 broad regression on the same exact head:

```text
workflow: 34634374571
job:      103378586398
result:   SUCCESS
suite:    522 passed, 1 skipped
```

The single skip is the existing opt-in population-registry golden regeneration
test. The same broad job passed the core -> companion import firewall.

## Verdict

Phase 8A is accepted at
`5256141e00a2d96a72b9cbf2182a77174c8c269e` / tree
`6252d1725ee07562840f0ce48b0dc6fe90a4aee4`.

The next allowed production slice is **8B: the minimal public InferenceTarget /
specialized sampler seam**, using this accepted head as its parent. No 8C or
companion implementation starts before 8B is independently accepted.
