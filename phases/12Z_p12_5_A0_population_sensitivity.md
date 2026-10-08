# Phase 12Z — P12.5 stage A0: which population parameters move H0 (declaration)

## Status

**DECLARED (owner, 2026-10-08) before any run. RESULTS appended below (2026-10-08).**
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

## Results (2026-10-08)

105 spectral-only grids on HENON (array 1376061; one task was resubmitted as
1376194 after a node start-up failure). Outputs:
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/A0/runs/<parameter>/<value>/spectral_h0.json`;
the tables below are in `phase12_5/A0/a0_summary.json`
(`a0_analyze.py`), and the spin source check in
`phase12_5/A0/lvk_hyperparameters.json`.

**Control.** The run at the fixed values reproduces the 12T grid to 9e-13 in
log-likelihood (H0 64.52, sd 5.05).

### 1. The fixed spin values are spin-magnitude values, and the events reject them

The GWTC-5 hyperposterior file (the run with a Gaussian on spin magnitude)
has `mu_chi` 0.0633 [0.005, 0.173] and `sigma_chi` 0.3654 [0.305, 0.421].
These are the two numbers of the fixed population, which applies them as a
Gaussian on effective spin.

| σ_χ (effective-spin width) | H0 median [68%] | peak logL − fixed | selection N_eff / threshold at the peak |
|---|---|---|---|
| 0.05 | 67.7 [62.9, 72.8] | +78.8 | 15.5 |
| 0.08 | 67.0 [62.2, 72.0] | +103.3 | 24.7 |
| 0.10 | 66.7 [61.9, 71.6] | +106.9 | 29.8 |
| 0.15 | 66.3 [61.6, 71.3] | +99.8 | 39.3 |
| 0.20 | 66.3 [61.5, 71.3] | +81.2 | 43.2 |
| 0.25 | 66.2 [61.4, 71.2] | +57.1 | 37.8 |
| 0.30 | 65.9 [61.0, 70.9] | +31.2 | 17.4 |
| 0.3654 (fixed) | 64.5 [59.6, 69.6] | 0 | 3.6 |
| 0.45 | guard penalises 144 of 241 H0 values | −29.5 | 1.0 |

- The events prefer an effective-spin width near 0.10 to the fixed 0.3654
  by 107 in log-likelihood.
- At that width H0 is 66.7, 2.1 km/s/Mpc above the fixed-population value,
  and the selection estimate has 8 times more effective injections.
- The mean: μ_χ = 0 is preferred to 0.0633 by 11.8 at the fixed width, with
  H0 64.97. μ_χ ≥ 0.15 runs into the guard.
- Every Phase 12 result so far (spectral and catalog) used the fixed pair.

### 2. H0 against each mass and pairing parameter

Shift of the H0 median for a one-sigma step s of the parameter (from the
±1 s runs), and the change in peak log-likelihood at −1 s and +1 s:

| parameter | dH0 per s (km/s/Mpc) | peak logL at −1 s / +1 s |
|---|---|---|
| m_break | −9.4 | +0.8 / −5.6 |
| α1 | +7.4 | −12.7 / +2.1 |
| μ2 | −5.2 | −0.4 / −2.3 |
| μ1 | −4.8 | −2.7 / +0.9 |
| σ2 | −4.6 | +0.7 / −1.4 |
| λ0 | −4.6 (from −1 s only) | −22.3 / — |
| α2 | +4.3 | −4.5 / −0.2 |
| λ1 | −2.6 (from −1 s only) | −27.0 / — |
| β_q | −2.1 | −0.9 / +0.1 |
| σ1 | −1.6 | +1.7 / −2.3 |
| m1_low | −1.3 | +1.1 / −2.8 |
| δm2 | −1.2 | −2.3 / +1.7 |
| δm1 | −0.9 | −0.4 / −1.4 |
| m2_low | −0.2 (from −0.5 s only) | −0.5 / — |

For comparison, the rate index γ moves H0 by about −6.7 per unit near its
preferred value (12X), and the fixed-population posterior sd is 5.05.

- **Seven parameters each move H0 by 4 to 9 km/s/Mpc per one-sigma step**:
  m_break, α1, μ2, μ1, σ2, λ0 and α2. That is as much as the whole
  fixed-population posterior width.
- The low-mass edges and taper widths (m1_low, m2_low, δm1, δm2), σ1 and β_q
  move it by 2 or less.
- Within ±1 s the peak log-likelihood changes by a few units at most for
  most parameters: the events do not separate these values strongly at fixed
  everything else. The exceptions are α1 (−12.7 at −1 s) and the peak
  weights λ0 and λ1 (−22 and −27 at −1 s), whose separate scans overstate
  their freedom because the two are anti-correlated.
- μ1 extended: H0 falls to 50.5 at μ1 = 11.0 and 42.9 at 12.0, with the
  peak log-likelihood lower by 4.1 and 22.2. A one-dimensional ridge toward
  low H0 exists and is mildly disfavoured near μ1 = 11.

### 3. Where the selection guard acts

At the fixed population the selection N_eff is 3.6 times its threshold at
the peak and 1.9 times at its lowest (low H0). The guard penalises H0 values
in these runs only:

| run | H0 values penalised |
|---|---|
| σ1 = 0.010 (−3 s) | 191 of 241 (H0 20 to 138) |
| σ2 = 1.11 (−2 s) | 23 (H0 36 to 47) |
| λ0 = 0.269, 0.138, 0.007 | 22, 48, 61 (below H0 36, 44, 50) |
| λ1 = 0.415, 0.284, 0.153 | 4, 37, 47 (below H0 30, 40, 44) |
| μ_χ = 0.15, 0.20 | 55, 98 (below H0 47, 68) |
| σ_χ = 0.45 | 144 |

No other run has a penalised point. The guard therefore acts on narrow peaks
(small σ1, σ2), on low peak weights, and on effective-spin distributions
shifted or widened beyond the fixed one. With the effective-spin width near
0.1 the margin grows eightfold.

### Reading

1. **The fixed population's effective-spin distribution is wrong, and
   correcting it comes before any further fixed-spin result.** The pair
   (0.0633, 0.3654) describes spin magnitudes. With a width near 0.10 the
   spectral-only H0 is about 66.7.
2. **A fixed population understates the H0 uncertainty.** Seven mass
   parameters each carry a shift as large as the quoted width. The
   fixed-population values of P12.3 and P12.4 are conditional on the GWTC-5
   medians, which were themselves measured at the LVK cosmology.
3. **Parameter set for the chains of stage A1:** γ, the two spin parameters,
   and m_break, α1, α2, μ1, μ2, σ2 and the peak weights λ0, λ1 (which must
   be sampled together). σ1, β_q and the low-mass edges and tapers move H0
   least and are the candidates to stay fixed.
4. **Guard:** sampling σ1, σ2, the peak weights and the spin parameters
   reaches guarded volume inside their priors. The guard diagnostics of the
   chains must report it.
5. The scans are one parameter at a time. What the joint posterior does, and
   how much of these shifts survives marginalization, is the question of
   stage A1.
