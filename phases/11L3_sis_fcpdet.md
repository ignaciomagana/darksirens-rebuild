# Phase 11 L3 — SIS and Finn–Chernoff primitives freeze

Status: **ACCEPTED / FROZEN**

## Accepted production state

```text
repository: ignaciomagana/darksirens-lensing
main SHA:   2abf9c21d2818c4ef02f48b3ca0dde48b0d2994a
tree:       72974544252d0d2187fcbfd1ff1052e7c81764bb
promotion:  PR #2
```

Frozen dependencies remain unchanged:

```text
core SHA:      af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
legacy oracle: c042527238bd71421b792936bc48c3b815b90d6d
L0B golden:    references/lensing_l0b_legacy_reference.json
```

## Production surface

L3 adds:

```text
src/darksirens_lensing/sis.py
  DEFAULT_T0_SECONDS
  TAU_PROB_MAX
  SISLensParams
  make_sis_lens_params
  tau_2_SIS
  tau_2_prob
  log_p_y_SIS
  mu_plus_minus_from_y
  y_from_mu_plus
  delta_t_from_y
  tau_4_SIS

src/darksirens_lensing/fcpdet.py
  FCPdetParams
  make_fc_pdet_params
  theta_threshold_fc
  pdet_fc
  log_one_minus_pdet_fc
  PAIR_ORIENTATION_MODES
  theta_fc_from_antenna
  pdet_pair_both_fc
  pdet_pair_exactly_one_fc
  log_pmiss_partner_fc
```

Both modules are companion-owned and import no frozen-core package code.

## Reference gate

L0B bootstrap:

```text
run/job: 34735672261 / 103666540691
result:  SUCCESS
```

Committed-golden replay:

```text
run/job: 34735732062 / 103666701435
result:  SUCCESS
```

The reference freezes raw-vs-clipped optical depth, SIS magnifications and time
marks, the Finn–Chernoff polynomial single-image marginal, and both
`independent` and `shared_iota` two-image orientation models.

## Production acceptance gates

PR clean-wheel CI:

```text
run:   34735906284
job:   103667178972
result: SUCCESS
L1 WL regression: 9 passed in 3.32 s
L3 SIS/FCPdet:     4 passed in 2.71 s
```

Accepted-main clean-wheel CI:

```text
run:   34735974625
job:   103667362756
result: SUCCESS
```

The installed-wheel ownership firewall passed in both cases: importing
`darksirens_lensing` does not import `darksirens`, `darksirens_lss`, or
`darksirens_surveys`.

## Frozen L3 implementation choices

The scalar SIS calibration `T0=5.36e6 s` is owned by the lensing companion;
frozen core deliberately contains no lensing constant. `tau_2_prob` clips the
raw `A_tau z^n_tau` surrogate to `1-1e-12` before it is interpreted as a
Bernoulli probability.

The shared-inclination Finn–Chernoff implementation preserves the exact L0B
table construction and resolutions:

```text
n_c    = 64
n_x    = 1025
n_cheb = 384
n_f    = 8193
n_u    = 2049
```

The table is built lazily and cached. It uses the exact geometric
conditional-inclination model; it is not replaced by, or calibrated to, the
independent polynomial marginal.

## Repository-isolation correction

During L3 setup the first `sis.py` commit was accidentally written to `main`
before the isolated branch existed. The work was preserved on
`l3-sis-fcpdet`, and `main` was then force-restored exactly to the accepted L2
SHA `83980f3932371287652b584774ae527b8c8319b5` before any further L3 work.
The temporary branch marker was removed. L3 was subsequently promoted only
through PR #2 after the clean-wheel gates above.

## Next slice

Proceed to **Phase 11 L0C**. Freeze the mature pair-evidence path before L4:

1. full-covariance apparent-frame PairKDE construction/evaluation;
2. image-assignment pair likelihood and SIS y marginalization;
3. the J=2 cluster evidence seam and its normalization/reduction identities.

Lensed-injection selection, file contracts and partition machinery remain for
later reference slices.
