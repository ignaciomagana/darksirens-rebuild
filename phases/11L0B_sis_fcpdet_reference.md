# Phase 11 L0B — SIS / Finn–Chernoff legacy reference

Status: **ACCEPTED / FROZEN**

## Oracle and harness

```text
legacy oracle: c042527238bd71421b792936bc48c3b815b90d6d
probe:         tools/probe_lensing_sis_fcpdet.py
workflow:      .github/workflows/lensing-l0b-reference.yml
golden:        references/lensing_l0b_legacy_reference.json
schema:        darksirens-lensing-l0b-sis-fcpdet-reference-1
```

Bootstrap acceptance after correcting one over-strong harness assumption:

```text
run:      34735672261
job:      103666540691
head:     418180f83d64754647222135b2c60c645d4f0392
artifact: 10310638001
digest:   sha256:73b9c5093cd0864dd5b189e9c84d7ed0af231669f9ca8f92149ceecc8f6fea1f
result:   SUCCESS
```

Committed-golden replay:

```text
run:    34735732062
job:    103666701435
head:   8c104c4a47e95df182fe5b6cb14d1a211bfd0e15
result: SUCCESS
```

The initial failed run `34735602548 / 103666359344` was harness-only: it
incorrectly required `log(1-Pdet)=-inf` at a tiny but finite positive apparent
distance. The legacy implementation keeps a strictly positive Finn–Chernoff
threshold for every finite positive distance; the miss CDF can remain nonzero
(and its log finite) even when `Pdet` rounds to one. No legacy or production
physics changed.

## Frozen SIS contract

Default lens parameters:

```text
A_tau = 5e-4
n_tau = 3
T0    = 5.36e6 s
TAU_PROB_MAX = 1 - 1e-12
```

The optical-depth surrogate is

```text
tau_2(z) = A_tau z^n_tau
```

but likelihood channels consume the Bernoulli probability

```text
P_2(z) = clip(tau_2(z), 0, 1 - 1e-12).
```

The distinction is load-bearing. At the frozen prior-corner stress point
`A_tau=1e-2, n_tau=6`, the oracle gives

```text
z                 = [1, 2, 5]
raw tau_2          = [0.01, 0.64, 156.25]
probability P_2    = [0.01, 0.64, 0.999999999999]
```

For SIS impact `y in (0,1)`:

```text
p(y)    = 2 y
mu_+    = (1+y)/y
mu_-    = (1-y)/y
mu_+ - mu_- = 2 exactly on the fixture
Delta t = T0 y
```

Frozen y fixture:

```text
y          = [0.05, 0.2, 0.5, 0.9]
mu_+       = [21, 6, 3, 2.111111111111111]
mu_-       = [19, 4, 1, 0.11111111111111109]
Delta t(s) = [268000, 1072000, 2680000, 4824000]
```

`log p(y)` is `-inf` outside the open interval `(0,1)`.

## Frozen Finn–Chernoff single-image contract

Defaults:

```text
rho_thr = 8
horizon = 3000 Mpc
r0      = rho_thr * horizon / 32 = 750 Mpc
mc_bar  = 1.22 Msun
```

The detector-frame chirp mass and threshold are

```text
Mc_det = Mc_src (1+z)
x = rho_thr / [8 (r0/dL_app) (Mc_det/mc_bar)^(5/6)].
```

Independent-orientation image detection uses the Finn–Chernoff polynomial CDF
on `x in [0,4]`:

```text
CDF(x) = (160 x^2 - 80 x^3 + 15 x^4 - x^5)/256
Pdet   = 1 - CDF.
```

Frozen threshold/Pdet fixture:

```text
x    = [0.5, 1, 2, 3, 4, 5]
Pdet = [0.8792724609375, 0.6328125, 0.1875, 0.015625, 0, 0]
```

The endpoint implementation clips the CDF coordinate to `[0,4]`.

## Frozen pair-orientation contract

Supported modes are exactly

```text
independent
shared_iota
```

`independent` preserves the historical mock convention: image orientations are
redrawn independently and the pair probabilities factor through the polynomial
single-image marginal:

```text
P(both) = P_+ P_-
P(exactly one) = P_+(1-P_-) + (1-P_+)P_-.
```

The oracle verifies both identities exactly on the fixture.

`shared_iota` is a different physical model, not a correction factor applied to
the polynomial marginal. It uses the exact geometric Finn–Chernoff relation

```text
Theta^2 = 4 [F_+^2 (1+c^2)^2 + 4 F_x^2 c^2], c=cos(iota),
```

with one inclination shared across the two images and conditionally independent
antenna responses at separated arrival times. The legacy implementation builds
and interpolates deterministic conditional-survival tables `S(x|c)` and then
integrates over `c`.

For threshold pairs

```text
[(1,2), (1.5,3), (0.8,1.0), (4.5,0.5)]
```

the frozen pair probabilities are

```text
independent both:
[0.11865234375, 0.0059604644775390625, 0.46656, 0]

shared_iota both:
[0.1790446383497588, 0.030096444899018228,
 0.5548948251100949, 0]

independent exactly-one:
[0.5830078125000001, 0.3851737976074219,
 0.4369725, 0.8792724609375]

shared_iota exactly-one:
[0.5122058171647027, 0.38303057929312445,
 0.32605225074971284, 0.8966672289949726]
```

Both shared-mode pair quantities are symmetric under swapping the image labels
on the frozen fixture.

## Frozen partner-miss conditional

For `independent`, conditioning on the detected image carries no information
about the independently redrawn partner orientation, so

```text
log P(partner missed | detected image)
= log[1 - Pdet(partner)]
```

and is exactly independent of the detected image's apparent distance. Both
identities are exact on the oracle fixture.

For `shared_iota`, the detected image updates the inclination distribution and
the conditional is

```text
log [ integral dc S_det(c) (1-S_partner(c))
      / integral dc S_det(c) ].
```

Frozen shared conditional values for the four threshold pairs are

```text
[-0.31334726573412225,
 -0.077147340265313,
 -1.2743987283987819,
 -2.114219015656577]
```

An unsupported orientation-mode string fails closed with `ValueError`.

## Next slice

Phase 11 may now begin **L3** in `darksirens-lensing`: port only the frozen SIS
marks/optical-depth and Finn–Chernoff detection/orientation primitives. Pair
KDE, pair likelihood, lensed selection reducers, file contracts and partition
machinery remain out of scope until their own reference slices.
