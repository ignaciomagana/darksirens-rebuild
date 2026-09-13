# Phase 11 L0C-S — lensed selection / exactly-one reference freeze

Status: **ACCEPTED / FROZEN**

## Immutable reference

```text
legacy oracle:  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
golden:         references/lensing_l0c_selection_legacy_reference.json
probe:          tools/probe_lensing_selection_singleton.py
workflow:       .github/workflows/lensing-l0c-selection-reference.yml
```

Bootstrap oracle run:

```text
run / job:      34737659849 / 103671802147
conclusion:     SUCCESS
artifact id:    10311720727
artifact zip:   sha256:98489c7abc28fa171212225bfedd0e664af60970bcfa350d4b053708234297dc
```

Committed-golden replay:

```text
run / job:      34737762451 / 103672093616
conclusion:     SUCCESS
artifact id:    10312160046
artifact zip:   sha256:4ac7db2a59210760fc1b1cd1c0f26df34d2da67fff4651efbd9db72fc7edafd7
```

The replay regenerated the reference in two independent processes, passed all structural/scientific pins, and printed `Lensing L0C-S committed golden comparison PASS` against the committed JSON.

## Frozen selection semantics

The J=2 and exactly-one channels are two mutually exclusive subsets of the same source-level lensed-injection campaign:

```text
both detected        -> J=2 cluster selection
exactly one detected -> lensed-singleton selection
neither detected     -> contributes neither detected channel
```

The estimator normalization is the total number of source draws `N_draw_sources`, not the number retained in either detected subset.  The importance weight is

```text
w_s = p_pop(theta_src) p_z(z_s) tau_2(z_s) p(y_s)
      / [p_prop_src(theta_src) p_prop_y(y_s)]
```

with an optional pair-tag probability multiplying only the J=2 channel.

Frozen synthetic campaign counts:

```text
N_draw_sources = 300
both detected = 106
exactly one detected = 59
neither detected = 135
plus only = 59
minus only = 0
```

The loaders recover exactly those counts.

## Frozen numerical anchors

J=2 both-detected selection:

```text
log mu_2       = -10.393679636707375
N_eff,2        = 9.336650923921662
log sigma^2_2  = -23.021306887896742
manual delta   = 0.0
```

Multiplying every retained source by `p_tag=1/2` gives exactly

```text
Delta log mu       = -log 2
Delta N_eff        = 0
Delta log sigma^2  = -2 log 2
```

Exactly-one selection:

```text
log mu_1L       = -9.985850690106737
N_eff,1L        = 18.14702555666866
log sigma^2_1L  = -22.870208046319068
manual delta    = 0.0
```

For `A_tau=0`, both lensed selection channels have `log mu=-inf`.

The frozen combined-selection fixture gives

```text
with J=2 pair channel = -5.086845924178854
without pair channel  = -3.8486630532945103
difference            = -1.2381828708843434
```

## Fixed campaign-cosmology contract

This point corrects the older Phase-11 inventory text.

The pinned mature lensed-selection implementation does **not** recompute image detection at each proposed cosmology.  Its files contain pre-rendered detection flags/subsets.  Detection depends on apparent observables such as

```text
dL_app = dL(z; Theta_campaign) / sqrt(mu),
```

so those flags correspond to the campaign cosmology.  The lensed selection estimators are therefore valid only at that fixed campaign cosmology.  The mature CLI enforces this by rejecting variable-cosmology use of these channels.

The oracle pins the implementation fact directly: changing the otherwise-unused `cosmo` argument while holding the redshift-prior closure fixed changes `(log mu, N_eff, log sigma^2)` by exactly zero for both J=2 and exactly-one estimators.  There is no hidden cosmology-dependent redetection inside the estimator.

A future variable-cosmology implementation requires a different campaign representation carrying the full source draws and a detection-efficiency model evaluated at the proposed cosmology.  That is a model extension, not Phase-11 parity work.

## Exactly-one event evidence

The exactly-one event channel integrates over SIS `y` and sums the two distinct observed-image identities.  The unobserved partner contributes a Finn-Chernoff censoring factor.

Frozen fixture:

```text
N_PE = 40
N_y  = 16

independent/default:
  log L       = -24.14280869121646
  MC variance = 0.03877501441781569

shared_iota:
  log L       = -24.252969689017338
  MC variance = 0.03839011220180665

shared_iota - independent = -0.11016099780087885
```

The default is bit-identical to explicitly requesting `pair_orientation_mode="independent"`.  `shared_iota` is finite and distinct.  `A_tau=0` gives `log L=-inf` for the lensed-single branch.

## L5 acceptance requirements carried forward

L5 production must preserve the reference above and additionally compose the two lensed selection channels correctly when they originate from the **same** campaign.  Their per-draw indicators are mutually exclusive, so

```text
Cov(mu_hat_1L, mu_hat_2) = - mu_1L mu_2 / N_draw_sources
```

and the variance of their union contains the corresponding `-2 mu_1L mu_2/N` term.  The mature master likelihood folds this shared-campaign covariance into the combined selection variance before the MFG finite-sample correction.  This composition term belongs to L5 integration and is not retroactively added to the already accepted standalone L0C-S golden.

L5 must also preserve:

- total-draw rather than kept-row normalization;
- no pair-tag factor in the exactly-one channel;
- pair-tag scaling only in J=2;
- exact `tau_2=0` dead-channel limits;
- campaign orientation provenance;
- fixed-campaign-cosmology fail-closed behavior;
- finite/zero-variance `N_eff` semantics consistent with frozen core selection helpers;
- no runtime dependency on surveys or LSS.

No production lensing source was modified by this reference freeze.
