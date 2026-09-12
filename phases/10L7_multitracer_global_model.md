# Phase 10 L7 — matched multitracer latent composition and field-global normalization

Status: **ACCEPTED / FROZEN**

## Accepted LSS package

`ignaciomagana/darksirens-lss`

```text
main SHA: 3429bb2f420239bc731cc9e73e50bf5351181c14
tree SHA: 7dff94d9a79f12e821a7f40f8d31f1a30435a8e5
```

No frozen-core or surveys source was modified.

The final accepted SHA is the clean promoted L7 tree plus a README-only
contract note.  The temporary exact-wheel workflow and its expiring signed URL
are not present on `main`.

## Frozen dependencies

```text
legacy oracle:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

frozen core:
  ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
  tree: 0608b75ff5c142bfba0fc15a4fad79e0fee1fa74

exact core wheel:
  darksirens-0.1.0.dev0-py3-none-any.whl
  SHA256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

## Frozen legacy oracle

Committed golden:

```text
references/lss_l7_field_global_legacy_reference.json
schema: darksirens-lss-l7-field-global-reference-1
```

Bootstrap/reference replay:

```text
run/job: 34714416771 / 103608881421
artifact: 10304287348
artifact digest: sha256:6b8f627f9e3018ab2a34f7a0f4dbb1c82d3da9c398131606575347d7695cfae9
result: SUCCESS
```

Committed-golden replay:

```text
run/job: 34714518561 / 103609209392
result: SUCCESS
```

The oracle pins the field/global algebra rather than the old monolithic object
graph:

- one survey-global normalizer `Z_k` per tracer;
- latent gauge conservation makes `Z_{k,m}` independent of member `m`;
- a K=1 global-normalizer shift cancels between PE and selection;
- a common shift of every `Z_k` also cancels for K>=2;
- a **relative** shift between tracer normalizers changes the K-catalog mixture;
- member `m` is one shared latent-field realization across every tracer;
- tracer-specific response tables are not a table-era realization identity.

## Exact frozen-core integration

The final public source/API head before removal of the temporary signed-wheel
workflow was

```text
SHA: c8d9ff8670d41a95b48d9e16adf28808903cd8f2
```

It passed the exact frozen core wheel gate:

```text
run/job: 34717116921 / 103616244405
result: SUCCESS
pytest: 20 passed
```

The job verified the exact core wheel SHA256 before installation, then ran L6
regressions plus the L7 global/multitracer integration suite.  In particular,
the frozen core accepted the L7 GW pixel frame

```text
GWEvent.pixels.shape == (N_samples, K_catalogs)
```

and routed the trailing catalog axis through the L7 `RedshiftModel` without a
core modification.

A pre-public-API source head also passed the same 20-test gate:

```text
head: 5f9b19187bcc4368ac81f3bcf260b86b06aefaf6
run/job: 34716907637 / 103615688041
result: SUCCESS
pytest: 20 passed
```

Two pre-acceptance failures are retained as diagnostic provenance, not accepted
evidence:

```text
34716626527 / 103614924115
  infrastructure-only: temporary signed wheel URL expired (curl 403);
  no package test ran.

34716662643 / 103615199080
  exact core installed and verified;
  19 passed, 1 failed;
  sole failure: 2.72e-15 log/exp roundoff against a 2e-15 test tolerance in
  the analytic stick-breaking check.
```

The latter was corrected by widening only the last-bit numerical test tolerance
to `5e-15`; production algebra was unchanged.

## Final permanent package CI

GitHub Actions:

```text
run: 34717224922
head: 3429bb2f420239bc731cc9e73e50bf5351181c14
```

Permanent jobs:

```text
standalone artifact/API/ownership firewall:
  job: 103616536715
  result: SUCCESS

radial + GP3D builder regression:
  job: 103616536842
  result: SUCCESS

latent count + Q + L7 multitracer algebra:
  job: 103616536839
  result: SUCCESS
```

The standalone firewall confirms that exposing L7 from the package root does
not make `import darksirens_lss` import frozen core, JAX, SciPy, surveys, or
lensing. Runtime package dependencies remain NumPy + HDF5 only.

## Public L7 API

The accepted root API adds:

- `FieldGlobalMemberState`
- `FieldGlobalTracerEnsembleState`
- `MultiTracerLatentMemberState`
- `MultiTracerLatentSideState`
- `MultiTracerLikelihoodResult`
- `MultiTracerLatentQModel`
- `build_field_global_tracer_state`
- `build_multitracer_side_state`
- `validate_multitracer_pair`
- `field_global_log_Z`
- `field_tracer_log_density`
- `field_mixture_log_density`
- `shared_latent_field_sha256`
- `stick_breaking_log_weights`
- `multitracer_latent_ensemble_log_likelihood`

Core/JAX imports remain call-site lazy.

## Field-global normalizer

L7 retains the L6 aggregate-selection convention

```text
C_{k,p}(z) = f_{k,p} C_k(z).
```

For tracer `k`, the latent gauge enforces

```text
sum_p [1 - f_{k,p} C_k(z)] Q_{k,m}(p,z)
  = sum_p [1 - f_{k,p} C_k(z)].
```

Therefore the all-sky missing-budget curve reduces to

```text
V_k(z) = N_pix,k - C_k(z) F_{F,k},
F_{F,k} = sum_p f_{k,p},
```

independent of latent member and `b_GW,k`.  The survey-global normalizer is

```text
Z_k = N_obs,k(global)
      + integral dz dN_exp,k(z) V_k(z).
```

With an active catalog depth, the observed term uses the same depth-kernel mass
as the numerator.  Above the depth the completeness curve is relaxed to zero,
so a catalogued above-depth object is not double counted in both observed and
missing branches.

## Full-sky footprint guard

A production issue was found before acceptance: an early L7 constructor trusted
the scalar artifact stamp `F_F` without proving that the caller's **full-sky**
`f_p` map actually represented the same footprint.  L6 only needs compact
GW-union rows; L7's global normalizer cannot make that assumption.

The accepted constructor therefore requires the full global pixel frame and
checks:

- `full_catalog.unique_pixels is None`;
- exactly one row exists per equal-area global sky pixel;
- `N_pix * A_pix = 4 pi` within numerical tolerance;
- full and compact catalog pixel areas agree;
- every fitted pixel is in range and unique;
- `f_p_global` has exactly one entry per global pixel and lies in `[0,1]`;
- `f_p_global == 0` outside the latent fitted footprint;
- `sum_{p in F} f_p_global` agrees with the artifact `F_F`;
- values on compact GW-union rows agree with the L6 row-state `f_p` values.

`F_F` used by the online global normalizer is thus derived from the validated
full-sky vector, not blindly trusted from a scalar stamp.

## Shared latent realization theorem

The K>=2 latent artifact represents one field, not K separately generated Q
tables.  The reconstructed L7 state therefore checks a shared-field content
identity built from the common field leaves/member ordering, including the
radial basis/support, row factors, bias interpolation nodes, fitted pixel frame,
and draw count.

It deliberately excludes tracer-response objects such as

```text
A_k, B_k, F_{F,k}, C_k(z), f_{k,p}
```

because those are each tracer's response/selection budget against the same
field.  Requiring their byte hashes to match would incorrectly reject two
surveys observing the same latent realization through different selection
functions.

There is no `realization_set_id` check in this latent K-tracer mode.  That stamp
belonged to independently persisted table ensembles.  Here member `m` is shared
structurally because every tracer state is indexed by the same field-member
axis.

## Per-tracer host bias and catalog fractions

The shared field does **not** imply a shared host response.  The sampled bias
block remains per tracer:

```text
b_miss
b_miss_c2
...
b_miss_cK
```

where, in latent mode, these labels mean `b_GW,k` for legacy sampler/API
compatibility.  Each tracer uses its own `b_GW,k`, completeness/selection
response and `Z_k` against the common member field.

Catalog mixture fractions preserve the pinned legacy stick construction exactly.
For labels `fcat_2 .. fcat_K`,

```text
fcat_m ~ Beta(1, K-m+1)
```

and the sticks map to the uniform Dirichlet simplex.  The implementation uses a
shifted inclusive cumulative sum of `log(1-v)` so boundary sticks `v=0` or `1`
produce exact zero-weight catalogs through `-inf` log weights without NaNs.
L7 does not replace this contract with softmax coordinates.

## K-tracer density and normalizer placement

For tracer `k`, L7 converts the L6 row-conditional density to a globally
normalized density by restoring the row normalizer and applying the survey
normalizer:

```text
log p_k(z,p) = log p_k(z | p)
               + log Z_{k,p}
               - log Z_k.
```

The catalog mixture is then

```text
log p_mix = logsumexp_k [ log w_k + log p_k ].
```

This placement is the L7 science pin.  At K=1 the global `Z_1` is an overall
factor and cancels from the reduced GW likelihood.  At K>=2, relative `Z_k`
values live **inside** the tracer mixture and therefore change the inferred
catalog fractions and the GW likelihood.

## Full member marginalization

PE and selection states must have the same tracer ordering, member count and
shared latent field.  For each shared field member `m`, L7 evaluates the
**complete frozen-core** hierarchical likelihood with all K tracers, including
both PE and detector-selection terms.  Only after that does it compute

```text
log L = logsumexp_m(log L_m) - log M.
```

No Q field, tracer prior, or catalog fraction is averaged before the complete GW
likelihood.

The galaxy-count Laplace evidence is common to all member draws from the same
conditional field posterior.  Passing it through core's auxiliary seam in every
complete-member call and then taking `logmeanexp` adds the scalar evidence once;
the exact-core integration test pins this explicitly.

## L7/L8 boundary

L7 now owns and freezes:

```text
K >= 2 matched latent member composition
per-tracer b_GW,k
full-sky field/global Z_k
relative-Z_k catalog-mixture physics
legacy uniform-simplex stick parameterization
(N,K) GW pixel-frame integration with frozen core
```

L7 does not reopen the already frozen radial, GP3D, table-ensemble, survey, or
core contracts.

## Next slice

Proceed to **L8: final Phase-10 freeze and integration audit**.

L8 should be a packaging/audit pass, not a new physical model: reconcile the
L0A-L7 contracts, run the complete permanent regression matrix, verify the final
public ownership/dependency boundary, and freeze the Phase-10 LSS package as a
whole.  New science should not be introduced during L8 unless an audit exposes a
real inconsistency.
