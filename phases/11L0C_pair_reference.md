# Phase 11 L0C — PairKDE / J=2 pair-evidence reference freeze

Status: **ACCEPTED / FROZEN**

## Oracle

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
probe:             tools/probe_lensing_pair_kde_cluster.py
golden:            references/lensing_l0c_pair_legacy_reference.json
schema:            darksirens-lensing-l0c-pair-reference-1
```

This is a separate-process legacy oracle. No `darksirens-lensing` production
module is imported by the probe.

## Acceptance evidence

First harness run:

```text
run/job: 34736864252 / 103669727288
result:  FAILED AFTER BOTH LEGACY PROBES COMPLETED
```

The failure was a control-harness reconstruction bug, not a legacy numerical
failure: the hand-built second image-assignment branch swapped the event roles
*and* reversed `(mu_plus, mu_minus)`, reversing the physical assignment twice.
The mature likelihood makes event j the driving event for branch B and again
passes `(mu_driver=mu_plus, mu_partner=mu_minus)` to the low-level branch
integrand. The probe was corrected accordingly; no production code existed or
changed.

Accepted bootstrap:

```text
head:     ca0b531bece7fe96fecb7b369854e0e730c3d1b3
run/job:  34736953526 / 103669971736
result:   SUCCESS
artifact: 10310759560
artifact digest: sha256:fffb98de8a1b98d9670f8cbec5f46230b69c38fc40e4267d5bfef73a58cc02cb
```

Committed-golden replay:

```text
head:     7007fe776adce0111ebd510b7184fd93f6493803
run/job:  34737008691 / 103670118958
result:   SUCCESS
artifact: 10310684671
artifact digest: sha256:cc7c50940154299f27d3787dd7d92b1b9cc9fbcfc4e1cec91e73f4a31112f222
```

The regenerated numerical JSON matched the committed golden within the pinned
cross-process tolerance.

## PairKDE contract frozen

Canonical apparent-frame coordinates are

```text
(m1det, q, dL_app, chieff)
```

and the estimator is the mature full-covariance PairKDE:

- valid PE rows determine the sample mean and covariance;
- Cholesky whitening carries the full sample covariance, not marginal-only
  bandwidths;
- Silverman's d=4 factor is applied isotropically in whitened coordinates;
- valid-row `prior_wt` values are used as supplied via `-log(prior_wt)`;
- padded invalid rows do not enter either the kernel sum or its 1/N
  normalization;
- the physical q<=1 boundary is handled by reflecting the **query** about q=1;
- malformed valid proposal weights fail closed;
- `bandwidth_scale` is a diagnostic/sensitivity handle, not a second accepted
  estimator.

Frozen fixture anchors include

```text
N_total = 300
N_valid = 298
log_norm(event j) = 0.6161826826138701
padding max |delta log p| = 0
q-reflection pair delta = 4.618527782440651e-14
```

The whitening matrix has nonzero off-diagonal entries, explicitly pinning the
full-covariance implementation.

## J=2 pair-likelihood contract frozen

For each SIS y node, one PE event is the driving image and the other enters
through its PairKDE. The branch maps

```text
dL_true = dL_app,driver * sqrt(mu_plus)
z_s      = z(dL_true)
m1_src   = m1det / (1 + z_s)
```

and predicts the partner at

```text
(m1det, q, dL(z_s)/sqrt(mu_minus), chieff).
```

The source-frame density is multiplied by the redshift prior,
`tau_2_prob(z_s)`, PairKDE density, SIS `p(y)`, quadrature weight, PE proposal
correction, and the apparent-to-source Jacobian

```text
-log(1+z_s) - log[d dL(z_s)/dz] + 0.5 log(mu_driver).
```

Each branch divides by the number of **valid positive-prior** driving PE rows.
The two image assignments are then **summed**, not averaged:

```text
log L2 = logaddexp(log L[i -> +, j -> -],
                   log L[j -> +, i -> -]).
```

The frozen fixture gives

```text
branch A logZ             = -25.40620303827156
branch B logZ             = -61.260513847311216
pair logL                 = -25.40620303827156
pair - manual SUM         = 0
pair - manual AVERAGE     = 0.6931471805599436
pair PE MC variance       = 0.0023482968434553374
swap |delta logL|         = 0
swap |delta variance|     = 0
bandwidth_scale=0.5 shift = +0.1843651377888733 nat
```

The +log(2) offset relative to averaging is part of the normalization contract:
the observed datum is an unordered pair, while the two image assignments are
distinct microstates whose intensities add.

The returned PE Monte-Carlo variance is the mature driving-sample delta-method
quantity. It does **not** include the partner KDE's sampling noise; that known
limitation remains explicit rather than being silently reinterpreted in L4.

## Scope boundary

L0C freezes the **unmarked** J=2 pair evidence only. It does not migrate:

- time-delay pair marks;
- lensed pair/singleton selection;
- exactly-one-detected censoring;
- lensed injection schemas;
- observed-catalog / candidate-edge contracts;
- partition enumeration or marginalization.

Those remain later Phase-11 slices.

## Next slice

Proceed to **Phase 11 L4** in `ignaciomagana/darksirens-lensing`, starting from
the accepted L3 main tree. Reconstruct only PairKDE and the unmarked J=2 pair
likelihood against this golden. Frozen core supplies cosmology/population/redshift
machinery; the lensing companion owns the pair estimator and SIS composition.
