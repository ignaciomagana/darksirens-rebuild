# 12AK — A detection-probability surrogate for the selection term, trained by us (stage 1: understand and declare)

## Status

**DECLARED (stage 1 of 4, 2026-10-19). Nothing has been trained.** This record explains the method, reports what the
two raw injection files contain, and fixes the design and the validation gates before any training. Stage 2 trains,
stage 3 validates (a separate workflow), stage 4 reports.

**Blinding: location-free.** No H0 inference is involved. Later stages report only the H0-dependence of
ln mu_D4(H0) − ln mu_MC(H0), never ln mu on its own, never a posterior, never an H0 value. The only H0 numbers here
are fixed in advance: the grid [20, 140] at step 0.5, the window [50, 90], and the injections' generation cosmology
(67.9, 0.3065).

**Owner's instruction (verbatim):** "Just run the code yourself and fit O3+O4ab together. Or fit O3 and O4ab
separately yourself in a workflow. don't use his data product. We want to understand what we are doing more."
So we use the graviflows code (arXiv:2610.00306, MIT licence, read at graviflows-dev ba8d964) and our own raw
injection files. We use none of the student's checkpoints, constraint files or training sets. We fit both ways.

**Code and data:**
- Consumer branch `phase12ak/pdet-surrogate` (worktree `phase12_5/repo_12AK`):
  - b803b26: the read-only inspection scripts;
  - cf8367a: `config/phase12ak_design.json`, the machine-readable form of every number below.
- Outputs go under `phase12_5/pdet_surrogate/ours/`. The stage-1 JSONs are:
  - `summary/12AK_stage1_inspect_injections.json` (sha256 0cd84910…);
  - `summary/12AK_stage1_draw_density_checks.json` (b0738f3b…).

## Why

Our selection term estimates mu(H0) by Monte Carlo over the public sensitivity injections. Its ln L variance floor
is about 0.69, which corresponds to an effective sample size of about 1e5. A detection-probability surrogate can
produce as many synthetic detected injections as we like. So it could lower that floor, but only if the surrogate's
own error does not bend the H0-dependence of mu. That is variant D4. The bar is 0.3% in the H0-dependent part of
ln mu.

## Explainer: what is fitted, and why p_det = xi · p_flow / p_inj

**The idea.** An injection campaign draws source parameters theta from a known density p_inj(theta), simulates
each signal in real detector data, and records whether the searches found it. We want the detection probability
P(det | theta). The searches only tell us which draws were found. Bayes' theorem turns that into a density problem:

  P(det | theta) = P(det) · p(theta | det) / p_inj(theta).

- **p_inj** is the draw density. We know it exactly, because LVK chose it.
- **P(det) = xi** is the fraction of all draws that were detected under that density:
  xi = (number detected) / (number drawn).
  The number drawn counts every generated draw, including those discarded before the searches because their
  optimal SNR was too low.
- **p(theta | det)** is the density of the detected draws. Nobody knows it in closed form, but the detected rows
  are samples from it. A normalising flow is fitted to those rows. Its density p_flow then stands in for
  p(theta | det).

So the flow does not classify "found or missed". It is a density estimate of where found injections sit, and the
known draw density and the efficiency xi turn it into P(det | theta).

**The O4 weights.** The O4 release gives every row a monthly weight w_i, because the draws were spread unevenly
over the months relative to the analysis time. The correct detected density is the weighted density of the found
rows, and the efficiency is xi = Σ_det w_i / N_draw. The student's script ignores w in training but uses it in xi.
That mismatch matters (see Inspection). We train with the weights.

**The 13 inputs and their transforms.** The 13 inputs are:
- the source-frame masses m1 and m2;
- the redshift z;
- the spin magnitudes a1 and a2;
- the sky position: right ascension, and the sine of declination;
- the polarisation psi and the cosine of the inclination;
- the cosines of the two spin tilts, and the two spin azimuths phi1 and phi2.

A flow lives on all of R^13, so each input is first mapped there by a fixed invertible transform:
- **Paper:**
  - the masses use an ordered transform, m1 > m2 > 0, built from cumulative exponentials;
  - z uses exp (positive only);
  - every angle and spin uses a sigmoid onto its interval.
  The data are then standardised (mean 0, sd 1 per dimension). The flow's density includes the Jacobians of these
  maps.
- **Ours:** we keep the sigmoid intervals and the standardisation. Masses and redshift instead get the campaign's
  hard support:
  - log m1 lies in (log m_min, log m_max);
  - log m2 lies in (log m_min, log m1);
  - z lies in (0, z_max).

  The paper's maps put probability at m2 < 1, at m1 > 1000 and at z > 3. There p_inj is zero, so the ratio is
  undefined and the code clips it to 1. Bounded maps put no probability there. Masking stays as a guard.

**Architecture and loss.** The flow is FlowJAX's triangular spline flow:
- a standard normal base distribution;
- 10 layers, each of which:
  - squashes every dimension with a tanh,
  - applies a monotone rational-quadratic spline with 10 knots,
  - then mixes the dimensions with a learned lower-triangular affine map;
- random permutations between the layers;
- about 6,100 parameters in all.

Because every Jacobian is triangular, the log-density is cheap and exact. Training minimises the mean negative
log-likelihood of the found rows (Adam, learning rate 1e-3, batch 4096, up to 5000 epochs). It stops after 500
epochs without improvement on a validation set, and keeps the best parameters.

**Time and phase.** Coalescence time and phase are not inputs. The found rows are spread over the whole run and
over all phases, so the flow learns P(det | theta) averaged over the run's times (weighted by w for O4) and over
phase. That is the quantity our selection term needs, since our population is stationary in time and has no
preferred phase. The same averaging smooths right ascension: the Earth turns under the sky during the run.

**From a flow to synthetic injections for our selection term.** Core estimates

  mu = (1/N_draw) Σ_{detected i} p_pop(theta_i) / pdraw_i.

Substituting P(det | theta) = xi · p_flow / p_inj into mu = ∫ P(det | theta) p_pop dtheta gives

  mu = xi · E_{theta ~ p_flow}[ p_pop(theta) / p_inj(theta) ].

So we draw N_s samples from the flow and give each sample:
- the campaign's own draw density as its pdraw;
- a "number drawn" of N_s / xi.

The flow's density value cancels. Only its samples matter. The synthetic file is therefore an injection set in
exactly core's format, built in gwcat's conventions:
- detector-frame masses and distance at the generation cosmology;
- the same Jacobian;
- the same reference spin prior with a_max 0.99;
- time normalisation and the campaign mixture (pdraw × (N_k/N)/T_k).

Core runs unchanged. The Monte Carlo noise falls as 1/N_s. The flow's own error does not fall: it sets the floor
that stage 3 must measure.

## Inspection of our raw files (reproduced)

Both raw files are byte-identical (sha256) to the files gwcat used for our product. The product's sha256 is
56e51af2…, the same as in 12AI.

**Detected counts per campaign**, on gwcat's rule: any search FAR below 1/yr, each campaign over its own searches.

| Campaign | Rows in file | Detected | Drawn | T (yr) | xi |
|---|---|---|---|---|---|
| O1+O2+O3 BBH (endo3) | 284,672 | **81,117** | 73,957,576 | 0.91102 | 1.09680e-3 |
| O4a+O4b | 2,959,534 | **986,829** | 870,454,872 | 1.67829 | 1.14802e-3 weighted (1.13369e-3 unweighted) |
| **Sum** | | **1,067,946** | 944,412,448 | 2.58931 | |

The sum equals the product's n_detected. The product's first 81,117 rows equal the endo3 detected rows (m1det and
dL, exactly), and the rest equal the O4 rows. The two FAR rules (any below 1, and minimum below 1) agree on every
row: there are no NaN FARs. Of the 6,462 rows with zero weight because a spin exceeds 0.99, 1,333 are endo3 and
5,129 are O4.

**Inputs.**
- **endo3:** has no stored spin-azimuth columns, but carries Cartesian spins. So all 13 inputs exist:
  - a = |s|;
  - cos tilt = s_z/|s|;
  - phi = atan2(s_y, s_x).

  The O4 file confirms that this phi convention equals its stored azimuth to 9e-16 rad. Nothing has to be dropped
  or marginalised.
- **O4:** carries all 13 directly.

Neither file is used for time or phase (see above).

**Draw densities.**
- **endo3:**
  - m1 ∝ m1^-2.35 on [2, 100], to 6e-7;
  - m2 ∝ m2 on [2, m1], to 9e-5 (float32 storage);
  - z ∝ dVc/dz on [0, 1.9] at 67.9/0.3065;
  - isotropic spins with a uniform on [0, 0.998];
  - angles uniform.
- **O4:** the 5-piece broken power law, 2m2/(m1²−1), a ∝ exp(−2a²), and the tilt mixture match the stored lnpdraw to
  1e-14; z ∝ dVc/dz on [0, 3].
- **The stored z densities depart from exact dVc/dz at very small z.** endo3 departs by up to 12% at z ≈ 0.002, and
  by under 5e-4 above z 0.04. O4 departs by up to 4% below z 0.003, and by under 6e-5 above z 0.06. This touches
  0.2–0.4% of rows. The densities are probably tabulated on a coarse grid. Synthetic pdraw must use the stored
  function, not the exact one (stage-2 gate).
- **Cosmology:** both campaigns were generated at 67.9/0.3065. dL(z) matches to 2e-7 (endo3) and 8e-5 (O4), and
  O4's stored ddL/dz to 6e-8.

**The monthly weights matter.** There are 19 values from 0.73 to 1.12, rising through the run as sensitivity
improved.

| | Result |
|---|---|
| Detected z distribution, weighted ÷ unweighted, by z decile | 0.996 at low z, 1.040 in the top decile |
| Detected log m1 distribution, weighted ÷ unweighted | up to 1.011 |
| Kish effective size of the weights | 975,800 of 986,829 |

Ignoring the weights would tilt the O4 surrogate by about 4% across z. z is the H0-sensitive axis, and 4% is ten
times our 0.3% bar. The prior assessment had put this effect at 1% or less, which is wrong.

**Two observations on the student's code (not used for anything):**
- The shipped training script uses all detected rows for training plus early-stopping validation. Its evaluation
  then runs on that same validation set, so it has no independent test set, unlike the 0.9/0.8 split the paper
  describes.
- p_inj is an analytic re-implementation of the O4 model. There is none for O3.

## Design (fixed)

**(A) Separate models.** One flow per campaign, each with its own support, xi and p_inj:
- **A-O3:** trained on the 81,117 endo3 rows, unweighted. xi = 81,117 / 73,957,576.
- **A-O4:** trained on the 986,829 O4 rows with the monthly weights. xi = Σ w / 870,454,872.
- **Combination:** mu = T_O3 mu_O3 + T_O4 mu_O4, which is exactly gwcat's mixture. Campaigns cover disjoint times,
  so each row's draw density is its own campaign's (N_k/N) p_k / T_k.

**(B) One joint model: which version is correct.** A single flow trained on the pooled found rows, unweighted, is
wrong. It learns Σ_k (N_k/N) p_k(theta) P_k(det | theta). That mixes the campaigns in proportion to the number
drawn (O3 is 8% of draws but 35% of time). It also mixes two different injection densities. The term mu needs
Σ_k T_k ∫ P_k(det | theta) p_pop.

The correct joint model reweights every found row to one common reference density q:

  u_i = T_k w_i q(theta_i) / (N_k p_k(theta_i)).

The flow then learns H(theta) q(theta) / Z, where:
- H = Σ_k T_k P_k(det | theta) · 1[theta in campaign k's support], the run-integrated detection probability in years;
- Z = Σ u_i.

We take q = q_mix = Σ_k (N_k/N) p_k. That is the pooled draw density of the two campaigns, the "gwcat mixture draw
density" in theta-space, so u_i = q_mix / (N · pdraw_i). Then:
- **p_inj → q_mix and xi → Z** = 2.70226e-3 yr, an equivalent 1.0436e-3 over 2.589 yr;
- **effective size:** O3 rows 38,757 of 81,117 and O4 rows 945,289 of 986,829, so 414,083 for the union.
  The reference q = p_O4 gives 380,422.

A flow conditioned on a campaign label would also be correct. But FlowJAX's conditioning is a linear shift, and the
two campaigns need different hard supports, so we do not use it.

**Known limitation of B.** H steps down at the edges of O3's injection support (m1 = 100, z = 1.9), because the MC
has no O3 draws beyond them. The flow will smooth those steps. Validation bins straddle these edges.

**(P) Paper control.** One O4 flow with the paper's transforms, unweighted, seed 4242, so that our two changes can
be seen against the paper's set-up.

**Data split.** By row, seeded (20261019), per campaign: 10% held out for testing, and the rest split 80/20 into
training and validation. B uses the union of the same splits, so A and B are tested on identical rows.

| | Train | Validation | Test |
|---|---|---|---|
| O3 | 58,404 | 14,601 | 8,112 |
| O4ab | 710,517 | 177,629 | 98,683 |
| B (union) | 768,921 | 192,230 | 106,795 |

The O3 test set is below the paper's 30,000 needed for PQMass power. PQMass on O3 is reported as underpowered.

**Ensemble.** K = 5 members per model. Each member gets:
- its own initialisation seed (1001–1005);
- its own batch-order seed (3001–3005);
- Poisson(1) bootstrap weights on the training rows (seeds 2001–2005).

So the spread includes training-data noise as well as optimisation noise. In total there are 3 × 5 + 1 = 16
trainings.

**Training.** The paper's settings:
- triangular spline flow, normal base;
- 10 layers, 10 knots, tanh limit 3;
- standardised inputs, x64;
- Adam at 1e-3, batch 4096;
- up to 5000 epochs, patience 500 on the validation loss, best parameters kept.

Our changes, each with its reason:
- **Bounded mass and redshift maps:** no probability outside the support.
- **A weighted NLL:** w for O4, u for B, times the bootstrap weights, normalised to mean 1. This is a small custom
  loop, because FlowJAX 17.2.1's fit_to_data has no sample weights. It mirrors fit_to_data otherwise.
- **A real test set.**
- **We keep 10 layers.** The paper says 10; the shipped checkpoints reportedly use 6.

The flow has about 6,100 parameters, so even O3's 58k training rows are ample.

**Software.** Our own GPU venv under `pdet_surrogate/`: jax[cuda12] 0.7.2 and flowjax 17.2.1. flowjax 19 silently
mis-loads weights, so a save → reload log-density check, bitwise on 1e4 points, gates every model. A few graviflows
files (the transforms used by control P) are vendored with their MIT notice and the sha ba8d964.

**GPU budget.** Rita A100-80 only, one job per card:
- **Expected:** about 1 h per O4 or B training, about 0.2 h per O3 training, so about 13 GPU-hours, about 7 h of
  wall time on the two cards;
- **Ceiling:** 30 GPU-hours.

A 50-epoch smoke test per model times this before the full submission.

**Masking.**
- **Evaluation path:**
  - p_det = 0 where p_inj = 0;
  - p_det is clipped to 1 (A);
  - H is clipped to the summed T of the campaigns whose support contains theta (B).
- **Synthetic path:**
  - samples outside the support are dropped;
  - samples with p_det > 1 are kept with probability 1/p_det, which is the same as clipping.

  N_draw is unchanged in both cases, and both counts are reported.

**Synthetic export.** For each member, 10 × the real detected rows: O3 811,170, O4 9,868,290, B 10,679,460. Each
synthetic row carries:
- weight 1, because the monthly weights already live in the flow and in xi;
- gwcat's chieff-reference pdraw.

**Stage-2 gates before any training:**
- **Our p_inj:** reproduces the stored per-row densities, to 1e-12 in log for O4 masses and spins, and to 1e-6
  relative for z (the stored small-z grid, or interpolation in the stored values).
- **Our exporter:** applied to the real rows, reproduces the product's pdraw to 1e-6 relative, including the 6,462
  zero-weight rows.
- **The z → dL map:** reproduces the files to 1e-4.

## Validation metrics (fixed now; run in stage 3)

| Id | Metric | Gate |
|---|---|---|
| V1 | **Two-sample tests** of flow samples against the held-out test rows (O4 and B rows thinned by weight / max weight): KS and AD per marginal (13 inputs plus chi_eff, q and chirp mass), PQMass, classifier AUC, and the Cauchy-combined p | diagnostic |
| V2 | **Per-bin ratios** of detected marginals in z, m1, q, chi_eff, sin dec and RA: flow fraction ÷ weighted test fraction. Bins straddle O3's m1 = 100 and z = 1.9. The same ratios are computed on the training rows to check overfitting | flag \|r−1\| > max(3%, 3σ); diagnostic |
| X1 | **Own xi parity**: xi_emu / xi = E_flow[min(1, 1/p_det) · 1_support], the mass kept after masking and clipping | ≥ 0.995 |
| X2 | **Cross parity**: mu_flow against mu_MC for p_O3, p_O4, q_mix, and the spectral-only population at the generation cosmology | within 1% or 2σ_MC |
| U0 | **MC noise reference**: 100 Poisson bootstraps of the real rows give the spread of the flatness statistic for MC against MC | reported; says whether 0.3% is resolvable |
| U1 | **Use case**: Δ(H0) = ln mu_D4 − ln mu_MC on the 241-point grid [20, 140] at step 0.5. S_W = max over H0 in [50, 90] of \|Δ − mean_W Δ\|. Also S over the full grid, and the level mean_W Δ (a constant, which does not affect H0) | **ensemble-mean S_W ≤ 3e-3** |
| U2 | **Ensemble spread**: sd over members of (Δ_m − mean_W Δ_m) | **max over [50, 90] ≤ 1.5e-3** |
| U3 | **Separate against joint**: Δ_A − Δ_B, and each model's S_W | smaller S_W wins; ties within 5e-4 go to A |

**The population for U1–U3** is that of records 12AG–12AI (the spectral-only reference):
- gwtc5_fiducial_bpl2peaks, with the population block of `spectral_gamma/runs/gamma_+2.5439/spectral_h0.json`;
- core e7c3007 (consumer env), core_defaults, soft guard at 20.

Only the population block is read from that file. D4 counts as a noise reduction only if X1, X2, U1 and U2 pass.
Otherwise its effect is a systematic to report, as the assessment advised.

## Blockers

None for stage 1. Stage 2 needs:
- our GPU venv;
- a check that core accepts a synthetic product whose ndraw = N_s / xi is not an integer (if not, N_s is chosen so
  the rounding is below 1e-9).
