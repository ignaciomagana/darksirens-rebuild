# Phase 12L — soft selection guard at cap 20

## Status

**ACCEPTED CONTRACT CHANGE (owner, 2026-09-29).** Supersedes the cap 10 of
Phase 12F for P12.2, P12.3 and P12.4; the guard stays soft and every other
12F setting stands. Consumer implementation: `desi_darksirens_selection`
PR #18, merged as `c86629b` (2026-09-29). **Gates 2 to 4 met (2026-09-29):
see "Production-path evidence".**

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
`/hildafs/projects/phy220048p/magana/darksirens-core-data/desi_darksirens_selection-phase12-gpu/logs/diagnostics_2026-09-29/`,
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

## Production-path evidence (2026-09-29)

Gate 2: consumer #18 merged as `c86629b`. Stand-ins (billing): CI-equivalent
261 passed, 9 skipped; CUDA environment on the H100 294 passed. Gates 3 and 4
are shown by the GPU run:

The full record of the run is in
`phases/12F_selection_guard_and_gwcat_products_acceptance.md`, "Production-path
evidence". At cap 20:

- P12.2's calibration probe is 6e-16 (total ln L) and 7.1e-15 (N_eff) from
  the 12F reference.
- P12.3 has 0 of 241 points penalised; its maximum (64.5) and mean (64.643)
  are unchanged from cap 10.
- The P12.4 anchor has N_eff at 2.16 times the threshold, with penalty 0.
- P12.4 converged (final dlogz 0.0999), unpenalised at the posterior mean
  and median.

## Robustness of the P12.4 posterior (diagnostic, 2026-09-29)

These are re-runs of P12.4 alone on the MIKO H100 (consumer `c86629b`, 12K
backend), made with a copy of the runner that overrides only the cap used to
build the target, the dynesty seed and the output paths. The chain's gates ran
at the production cap 20. These are not production products; they live in the
GPU checkout under `logs/diagnostics_2026-09-29/diag_runs/<tag>/` (README there). Hashes are sha256, first 16 hex.

```text
run          cap  seed  H0 median  mean +- sd      68%             90%             log Z      gate 7  result.json
production    20   22    71.07     70.88 +- 4.49   [66.29, 75.13]  [63.57, 78.32]  -780.722   met     be23ce578ced2e62
cap15_s22     15   22    71.08     70.90 +- 4.49   [66.30, 75.14]  [63.62, 78.36]  -780.728   met     00280e6f71b73e6b
cap30_s22     30   22    71.11     70.95 +- 4.49   [66.35, 75.16]  [63.65, 78.37]  -780.725   met     b8e1c91afffa59a1
cap20_s23     20   23    71.02     70.77 +- 4.36   [66.29, 74.85]  [63.75, 78.15]  -780.682   met     e28d9a8b75081dff
cap20_s24     20   24    71.04     70.78 +- 4.44   [65.97, 74.96]  [63.65, 78.29]  -780.740   met     a03595f2c3ca9765
```

- The cap, from 15 to 30 at a fixed seed, moves the median by at most 0.05,
  about 0.01 posterior sd.
- The seed moves the median by 0.04 at cap 20 (standard deviation of the three
  medians 0.02), and the sd by up to 0.13.
- The cap's effect is therefore no larger than the sampler's scatter at
  nlive 1000. Every run converged to dlogz 0.1 and is unpenalised at its
  anchor, mean and median.
- Cap 10 is not in the table: there the guard penalises the field target
  below H0 of about 63 (see "Trigger"), so its P12.4 is truncated by
  construction.

## Verdict

**Accepted (owner, 2026-09-29).** The P12 chain's soft selection guard is at
cap 20.
