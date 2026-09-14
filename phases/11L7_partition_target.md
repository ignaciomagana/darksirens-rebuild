# Phase 11 L7 — exact partition-marginalized lensing target

## Status

**ACCEPTED / FROZEN**

Phase 11 L7 is integrated in `ignaciomagana/darksirens-lensing` and the merged
`main` clean-wheel gate is green.  This slice is the sampler-facing integration
of the already accepted Phase-11 primitives; it adds no new lensing oracle or
survey/LSS dependency.

```text
legacy oracle:          ignaciomagana/darksirens
legacy SHA:             c042527238bd71421b792936bc48c3b815b90d6d
frozen core:            ignaciomagana/darksirens-core
core SHA:               af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
L6 base/main:            44ba42ce16a9b8cff803787e3f95f2e3439ad0ff
L7 branch:               rebuild/phase11-l7-partition-target
accepted clean head:     b144ed496848be125c8989711b9bef35b671af73
PR:                      darksirens-lensing #6
squash merge:            90f5af30b21a94578cdcc17b3abd0261cbaca7be
```

Core, surveys and LSS were not modified.

## Production surface accepted

L7 adds `src/darksirens_lensing/hierarchical.py` and public exports for:

```text
LensRateSpec
PartitionMarginalizationPlan
PartitionedLensingDiagnostics
build_partition_marginalization_plan
make_event_pair_kdes
partitioned_lensing_log_likelihood
make_partitioned_lensing_target
```

The implementation composes rather than copies the legacy monolith:

```text
frozen core
  ParameterPlan / InferenceTarget
  population parser
  volume-redshift prior
  ordinary PE reducer
  ordinary selection reducer/correction

accepted lensing companion
  L2 weak-lensing event weights
  L4 apparent-frame PairKDE + unmarked J=2 evidence
  L5 exactly-one evidence + lensed selection/covariance
  L6 canonical campaign provenance + exact graph matchings
```

No legacy CLI/factory was ported.

## Exact partition contract

For one proposed hyperparameter point, L7 evaluates each reusable scientific
term once:

```text
one singleton evidence row per observed event
one J=2 evidence row per candidate edge
one ordinary selection estimate
one exactly-one lensed selection estimate
one J=2 lensed selection estimate
```

L6 exact matching masks assemble complete partitions from those rows.  The
partition prior is explicitly normalized:

```text
log L_marg = logsumexp_P(log L_P + log pi_P) - logsumexp_P(log pi_P)
```

The MFG/Talbot-Golomb selection correction is still partition dependent because
an observed pair is one source rather than two events.  L7 therefore groups
partitions by

```text
N_source,obs = N_singleton + N_pair
```

and reuses frozen core's `selection_log_correction` once per distinct static
source count.  Per-partition PE Monte-Carlo variance is assembled from the same
singleton/edge masks before the guard is evaluated.

False-mask arithmetic is explicit (`where(mask, value, 0)`), so unused `-inf`
channel rows cannot produce `0 * -inf -> NaN` contamination.

## Lensed-channel accounting

The accepted L5 shared-campaign contract is preserved unchanged:

```text
mu_total = mu_unlensed + mu_exactly_one + mu_J2
Cov(mu_exactly_one, mu_J2) = -mu_exactly_one * mu_J2 / N_draw_sources
```

The pair-tag probability enters only the J=2 selection estimate.  The
exactly-one selection channel remains untagged.

Ordinary singleton evidence/selection carries the accepted `(1 - tau_2)`
suppression whenever the strong-lensing channels are present.  With the
realistic exactly-one channel enabled, the observed singleton evidence is the
mixture of that unlensed/WL branch and the strongly-lensed single-image branch;
their shared-PE Monte-Carlo error uses the accepted conservative correlated
branch variance.

## Lens-only sampler coordinates

`LensRateSpec` keeps SIS optical-depth parameters outside the frozen ordinary
core model construction.  A scalar fixes a parameter; a two-element tuple is a
uniform prior block appended locally to the base core `ParameterPlan`:

```text
log10_tau_A
tau_n
```

`T0_seconds` remains fixed run configuration.  This preserves the legacy
ownership decision tested by `test_inference_lensing_fixed_parameters.py`.

## Fail-closed scientific guards

L7 rejects unsupported configurations at construction time:

```text
sampled cosmology
  rejected because the accepted lensed campaign stores pre-rendered detection
  membership at one campaign cosmology

fixed cosmology different from campaign cosmology
  rejected

time-marked candidate edges
  rejected because Phase-11 L4 is the unmarked J=2 pair surface

component-spin GWEvent blocks
  rejected because PairKDE is defined in (m1det, q, dL_app, chieff)

non-isotropic angular model
  rejected in this Phase-11 surface

exactly-one evidence without Finn-Chernoff campaign constants
  rejected
```

These are not silent approximations.

## Acceptance gates

### Permanent core-free gate on accepted clean head

```text
head:                    b144ed496848be125c8989711b9bef35b671af73
workflow:                34801372297
job:                     103844564699
result:                  SUCCESS
```

The clean wheel was installed without core and passed:

```text
ownership/import firewall
L1 weak-lensing tests
L3 SIS/Finn-Chernoff tests
L4 PairKDE tests
L5 selection algebra tests
L6 data/partition tests
L7 core-free partition algebra tests
```

### Exact frozen-core acceptance gate

A temporary acceptance workflow used the already frozen Phase-8 core wheel:

```text
core wheel artifact:     10294880218
wheel SHA-256:           4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
acceptance head:         81782eff36e7f8473546f6ce6b81ebe8649e6fd0
workflow:                34801235560
exact-core job:          103844172834 SUCCESS
core-free job:           103844172905 SUCCESS
```

The exact-core job first replayed the accepted L2/L4/L5 core-dependent gates,
then ran `tests/test_l7_target.py`.  All passed.

The L7 integration gate pins, independently:

```text
lens-only coordinates append to, but do not mutate, the core plan
sampler likelihood closure is JIT-compatible
sampled cosmology fails before inference
partition posterior weights normalize exactly
partition marginal likelihood uses the explicit prior normalizer
A_tau = 0 + no candidate edges reduces to frozen-core spectral sirens
```

The temporary signed artifact-fetch plumbing was removed before the accepted
clean head; no frozen-core wheel or signed URL is retained in the companion.

### Infrastructure-only pre-acceptance failure

```text
workflow:                34801138805
job:                     103843890141
result:                  FAILURE during cross-private-repo checkout
```

The PR-scoped `GITHUB_TOKEN` could not checkout private
`ignaciomagana/darksirens-core`; no core-dependent science test ran in that job.
It is not a scientific or production-code failure.  The permanent core-free job
in that same run passed.

### Merge and post-merge

```text
PR:                      #6
merge:                   90f5af30b21a94578cdcc17b3abd0261cbaca7be
post-merge workflow:     34801437682
post-merge job:          103844754864
result:                  SUCCESS
```

Merged `main` therefore preserves the clean-wheel ownership firewall and the
entire permanent L1/L3/L4/L5/L6/L7 core-free regression chain.

## Files changed by the accepted L7 slice

```text
src/darksirens_lensing/hierarchical.py
src/darksirens_lensing/__init__.py
tests/test_l7_partition_algebra.py
tests/test_l7_target.py
.github/workflows/ci.yml
```

The final CI file contains no temporary frozen-core artifact machinery.

## Next action

Proceed to **Phase 11 L8 — final ecosystem freeze**.

L8 is freeze/validation work, not a new-physics slice.  It must:

```text
1. build the final lensing wheel from a clean checkout;
2. verify the public import/API and ownership firewall;
3. run the permanent L1-L7 regression chain;
4. run fixed-theta end-to-end parity against the pinned legacy lensing stack,
   including complete partition assembly rather than only isolated primitives;
5. verify the frozen core/lensing composition with the exact frozen core wheel;
6. reconcile package documentation and the control-repo status ledger;
7. freeze darksirens-lensing main and close Phase 11.
```

Do not reopen core, surveys or LSS during L8.
