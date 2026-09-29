# Phase 12L — soft selection guard at cap 20

## Status

**ACCEPTED CONTRACT CHANGE (owner, 2026-09-29).** Supersedes the cap 10 of
Phase 12F for P12.2, P12.3 and P12.4; the guard stays soft and every other
12F setting stands. Consumer implementation: `desi_darksirens_selection`
PR (branch `phase12l/guard-cap-20`). Gates 2 to 4 are recorded when the chain
has run at cap 20.

## Trigger

The first P12.4 run under Phases 12I and 12J (MIKO H100, consumer `dc9c8a3`,
core `a46dec7`, Phase 12K CUDA backend, started 2026-09-29T04:03Z) passed
P12.1 to P12.3 and stopped before sampling:

```text
DESIRunError: P12.4 anchor point fails the unpenalised MC-reliability gate
```

The anchor is the P12.3 MAP H0 = 64.5 with the prior means of `M0hat`
(-20.309781546689074) and `sigma_M` (0.7144467727667887). Its diagnostics
(reproduced by a copy of the runner that stops before sampling, on the GPU
and on the CPU in the frozen environment, equal to 1e-15):

```text
log L -779.1627642318965   N_eff 7,309.9   N_eff / T(cap 10) 1.069
MC variance: PE 0.189 + selection 9.177 = 9.366 (<= 10)
soft-guard penalty -4.5e-9 nats  -> not "unpenalised" (exact float64 equality required)
```

The penalty is not a rounding artefact of one point. The P12.4 field target
has fewer effective injections than the P12.3 spectral baseline at the same
H0 (7,310 against about 12,000 at H0 = 64.5), and at cap 10 the soft guard
penalises every H0 below about 63. Scan of the field target at the anchor's
`M0hat` and `sigma_M` (GPU; penalty at cap 20 from the 12F formula):

```text
 H0   N_eff   N_eff/T10  penalty cap 10   N_eff/T20  penalty cap 20
 40   3,573     0.52       -8.6e3           1.05        -1e-7
 50   4,817     0.70       -5.0e3           1.42        ~0
 56   5,642     0.82       -2.5e3           1.67        ~0
 58   5,999     0.88       -1.5e3           1.77        ~0
 60   6,382     0.93       -346             1.88        ~0
 62   6,781     0.99       -0.07            2.00        ~0
 64   7,201     1.05       -1.1e-7          2.13        ~0
 66   7,645     1.12       -2.3e-13         2.26        ~0
 67   7,874     1.15        0               2.30        0
 70   8,590     1.26        0               2.54        0
```

The P12.3 posterior is H0 = 64.6 +- 5.1 (5% and 95% points 56.5 and 73.0),
with 29% of its mass below H0 = 62. At cap 10 the P12.4 posterior would be
truncated on its low-H0 side by the guard, not by the data.

Diagnostic files (Hildafs GPU checkout
`/hildafs/projects/phy220048p/magana/darksirens-core-data/desi_darksirens_selection-phase12-gpu/logs/`,
sha256 first 16 hex): `diag_anchor_gpu.json` fd159326568ac9d2,
`diag_anchor_cpu.json` ff3e9559bba31285, `diag_neff_scan_gpu.json`
481df8eebdcfe2ee.

## Decision

The owner raised the cap from 10 to 20 on 2026-09-29, over (b) doubling the
detected injections (a new Product A build) and (c) keeping cap 10.

- At cap 20 the field target is unpenalised down to H0 about 40, below the
  P12.3 posterior's 5% point (56.5); the anchor's penalty is exactly zero.
- The Phase 12F guard study found caps 10 and 20 to leave the rung-1 and
  rung-3 posteriors unchanged (<= 0.026 sigma) on the spectral likelihood.
- Cost: the tolerated Monte-Carlo variance of ln L doubles. At H0 = 60 the
  total is 10.7 (standard deviation about 3.3 nats); the budget check at cap
  20 admits it.
- More injections remain the principled way to lower the variance and are
  not excluded by this record.

## Change

- `max_likelihood_variance` 20.0 in `config/diagnostics.production.json`
  (P12.2), `config/baseline.fixed_population.json` (P12.3) and
  `config/desi.fixed_population.json` (P12.4).
- The acceptance marker's `selection_guard`: cap 20, phase 12L, this record;
  `supersedes` names the 12F cap-10 soft guard (which superseded the hard cap
  1); the unpenalised definition reads cap 20.
- Every cap-10 P12.2 to P12.4 product is stale; the chain regenerates them.
- Unchanged: the soft guard's form, the `N_eff > 5 N_obs` floor, the
  unpenalised requirement at the P12.2 calibration anchor, the P12.3 grid
  maximum and mean, the P12.4 anchor, median and mean, and gate 7.

## Acceptance gates

1. The owner accepts the change. **Met 2026-09-29.**
2. The consumer change merged with its tests (contract CI blocked by billing;
   stand-ins recorded in the PR).
3. The chain re-run at cap 20: P12.2's calibration probe equals the Phase 12F
   reference to 1e-12 relative (the point is unpenalised at both caps, so the
   total is cap-independent), P12.3 accepted with its maximum and mean
   unpenalised, and the P12.4 anchor accepted.
4. P12.4 accepted under 12F gate 7.

## Verdict

**Accepted (owner, 2026-09-29).** The P12 chain's soft selection guard is at
cap 20.
