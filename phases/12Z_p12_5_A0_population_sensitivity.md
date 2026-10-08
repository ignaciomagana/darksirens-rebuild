# Phase 12Z — P12.5 stage A0: which population parameters move H0 (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any run. Results will be appended here.**
Spectral-only likelihood grids on HENON CPU. No chain, no catalog and no GPU
job.

## Where this sits

P12.5 of the Phase 12 contract replaces the fixed GWTC-5 population by its
uncertainty. Sampling all 17 population parameters in the DESI target would
take about two GPU-weeks per run, so the marginalization is staged
(`phase12_5/P12_5_full_scope.md` under darksirens-core-data). Stage A0 is the
map that the later stages are chosen from. 12X did this for the rate index
γ: H0 moves from 64.5 to about 70 when γ is freed.

## Questions

1. Which of the other 16 population parameters move the spectral-only H0
   when changed within their GWTC-5 uncertainty, and by how much?
2. Where does the selection guard start to act as each parameter moves away
   from the fixed value?
3. Are the fixed spin values the right ones? The fixed population uses
   mu_chi = 0.0633 and sigma_chi = 0.3654 in a Gaussian on effective spin.
   The registry names the GWTC-5 run with a Gaussian on spin magnitude as
   their source. If they are spin-magnitude values, the effective-spin
   distribution in every Phase 12 result so far is too wide.

## What is run

`scripts/phase12t_stage.py spectral`: the 12T spectral-only grid (H0 from 20
to 140 in steps of 0.5, exact-prior GW inputs, consumer ab226d6, core e7c3007
with its defaults, soft guard at cap 20), once per (parameter, value). The
population is `gwtc5_fiducial_bpl2peaks` given as an explicit mapping with
one parameter changed and the other 16 at their fixed values, as in 12X.

**Parameters:** the 16 other than γ (α1, α2, m_break, μ1, σ1, μ2, σ2, m1_low,
δm1, λ0, λ1, β_q, m2_low, δm2, μ_χ, σ_χ).

**Values.** For each parameter, the fixed value plus k·s for
k = -3, -2, -1, -0.5, +0.5, +1, +2, +3, where s is the GWTC-5 90% interval
divided by 3.29:

| parameter | fixed | GWTC-5 5% to 95% | s |
|---|---|---|---|
| α1 | 1.4816 | 0.11 to 2.52 | 0.733 |
| α2 | 5.4187 | 3.86 to 6.84 | 0.906 |
| m_break | 37.451 | 29.6 to 48.3 | 5.68 |
| μ1 | 9.9109 | 9.25 to 10.29 | 0.316 |
| σ1 | 0.7841 | 0.50 to 1.35 | 0.258 |
| μ2 | 32.3273 | 26.5 to 36.8 | 3.13 |
| σ2 | 5.7263 | 1.9 to 9.5 | 2.31 |
| m1_low | 4.4856 | 3.15 to 6.46 | 1.006 |
| δm1 | 3.5302 | 0.3 to 8.8 | 2.58 |
| λ0 | 0.4004 | 0.19 to 0.62 | 0.131 |
| λ1 | 0.5457 | 0.33 to 0.76 | 0.131 |
| β_q | 1.0438 | 0.37 to 1.82 | 0.441 |
| m2_low | 3.4633 | 3.02 to 4.68 | 0.505 |
| δm2 | 4.8128 | 0.8 to 7.8 | 2.13 |

- Values outside the model's prior range, or breaking its constraints
  (λ0 + λ1 ≤ 1, m2_low ≤ m1_low), are dropped, not clipped.
- **μ1 is extended** to 11.0, 11.5 and 12.0: an archived 18-parameter run had
  a second mode near H0 = 32 with μ1 ≈ 11.2, and the grid shows whether a
  ridge leads there at this guard setting.
- **Spin:** μ_χ at 0, 0.03, 0.0633, 0.10, 0.15, 0.20; σ_χ at 0.05, 0.08,
  0.10, 0.15, 0.20, 0.25, 0.30, 0.3654, 0.45. These cover an effective-spin
  width of about 0.1 as well as the fixed 0.37.

**Spin source check.** The job first reads the GWTC-5 hyperposterior file
(`/hildafs/projects/phy220048p/share/LVK_population_analyses/popsummary_files/gwtc5_updated_default_mmax_..._popsummary_result.h5`)
and records its spin hyperparameters' names and 5%, 50%, 95% values, to
settle which quantity 0.0633 and 0.3654 are.

Outputs go to
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/A0/`.

## Control

The run at every fixed value is the 12T spectral-only grid: its
log-likelihood must match the stored one to rounding, as in 12X.

## What is reported

For each parameter:
- H0 (median, 68% interval, sd) against the parameter's value, and the slope
  dH0 per s, the shift for a one-sigma change;
- the peak log-likelihood against the value: which values the events prefer
  at fixed everything else;
- the selection N_eff over its threshold, and the number of H0 points the
  guard penalises or rejects.

Across parameters: a ranking by |dH0 per s|, the set that moves H0 by more
than 1 km/s/Mpc per s, and the values at which the guard starts to act. For
the spin question: what the file says, and the H0 shift between
σ_χ = 0.3654 and about 0.1.

## Limits, stated in advance

- One parameter at a time, with the others fixed: correlations between
  parameters are not measured here. λ0 and λ1 are 96% anti-correlated in the
  GWTC-5 posterior, so their separate scans overstate what each can do.
- The step s comes from a posterior that assumed the LVK cosmology. It is a
  yardstick for the scan, not a prior.
- A parameter that moves H0 little in a one-dimensional scan can still
  matter jointly. The ranking chooses the first reduced set for the chains
  of stage A1; it does not close the others.

## Expectations, not thresholds

- The mass scales (μ1, σ1, μ2, m_break, the low-mass edges) move H0 most,
  after γ.
- The guard acts first on the low-σ1 side.
