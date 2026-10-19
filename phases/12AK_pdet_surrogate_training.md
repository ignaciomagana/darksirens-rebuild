# 12AK — A detection-probability surrogate for the selection term, trained by us (stage 1: understand and declare)

## Status

**DECLARED (stage 1 of 4, 2026-10-19); stage 2 BUILT (amendment B1, 2026-10-19); review fixes and SUBMITTED
(amendment B2, 2026-10-19).** Stage 2 wrote the training sets, passed the pre-training gates, and ran a 50-epoch smoke
test of each model on one rita card. A review found no blocking defect and eleven non-blocking ones; B2 fixes or
records each before any training job, and then the 16-member ensemble was submitted (job ids in B2). Validation
(gates V1–U3) follows in a separate workflow.

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
| O3 BBH (endo3, LIGO-T2100113-v12) | 284,672 | **81,117** | 73,957,576 | 0.91102 | 1.09680e-3 |
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
| V1 | **Two-sample tests** of flow samples against the held-out test rows, as weighted statistics with each row's loss weight (w for A_O4, u for B; amended in B2, which replaces thinning by weight / max weight): KS and AD per marginal (13 inputs plus chi_eff, q and chirp mass), PQMass, classifier AUC, and the Cauchy-combined p | diagnostic |
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

**Stage 2 (B1):** both are resolved. The venv is built, and the pre-training gates pass, as amended for endo3's
float32 mass density. Core floors a fractional ndraw, so synthetic products write an integer ndraw and carry the exact N_k in
the row fractions.

## Amendment B1 (stage 2: build), 2026-10-19, before any training job

Stage 2 built the environment, the training sets, the training code and the tests, and ran a smoke test. Everything
below was fixed before the ensemble was submitted. Nothing here involves H0.

**Commits (local only, not pushed).**
- Consumer branch `phase12ak/pdet-surrogate` (worktree `phase12_5/repo_12AK`):
  - b65abca: the code (package `phase12ak/`, three scripts, four Slurm scripts, the tests);
  - 208bc9a: the joint-weight comparison with stage 1 at 1e-5 (item 6 below);
  - cf2a4bd: an integer ndraw for synthetic products (item 5), with its test.
- Jobs run from detached worktrees of a committed sha under `pdet_surrogate/ours/worktrees/` (the smoke from
  208bc9a). Their check is that the sha is on the local branch, since nothing is pushed.

**Environment.** Our GPU venv is `pdet_surrogate/venv_gpu`: jax[cuda12] 0.7.2, flowjax 17.2.1, equinox 0.13.8,
and the CPU venv's other pins.
- The freeze is `ours/env/venv_gpu.freeze.txt` (sha256 2666568d…); the build script and requirements are beside it.
- One change from the CPU venv: lineax is dropped. It needs jax ≥ 0.10, and nothing here requires it.
- The gwcat chi_eff prior is imported from the pinned gwcat 8263ae9 source tree, not copied.
- One graviflows file (`constrained_transform.py`, ba8d964) is vendored verbatim under `phase12ak/vendor/` with its
  MIT notice. Only control P uses it. The paper's interval values are transcribed in code: they are transform
  settings, not fitted values.

**Training sets** (HENON job 1390322, code 208bc9a; summary `ours/summary/12AK_stage2_training_sets.json`, sha256
865fedc3…):
- `ours/data/12AK_detected_O3.h5` (sha256 f41580d8…): 81,117 rows;
- `ours/data/12AK_detected_O4ab.h5` (sha256 9ed5dde9…): 986,829 rows.

Each holds the detected rows only, with:
- the 13 inputs and the monthly weight;
- the split label and the raw row index;
- both campaigns' draw densities and the joint weight u;
- the file's stored density, m1det, dL, chi_eff, and the product's pdraw for the same row.

The raw files and the product were re-hashed and match. The counts, the splits (58,404 / 14,601 / 8,112 and
710,517 / 177,629 / 98,683) and xi equal the design.

**Departures from the declared design, each with its reason.**
1. **psi is folded modulo pi.** endo3 draws psi on [0, 2pi) and O4 on [0, pi). The signal is unchanged by
   psi → psi + pi, so P(det) has period pi. The folded density is 1/pi in both campaigns, so the joint model sees one
   convention.
2. **The stored redshift densities are now identified.** Each is dVc/dz (astropy, 67.9/0.3065), linearly
   interpolated on a uniform grid and normalised by the trapezoid rule on that grid:
   - endo3: 1001 points on [0, 1.9]; it reproduces the stored values to 4.8e-13;
   - O4: 3001 points on [0, 3]; it reproduces them to 8.4e-8.

   Linear interpolation of a z²-like function explains the small-z excess that stage 1 found. p_inj and the
   synthetic pdraw use these functions.
3. **O4's distances use the same grid.** O4's dL is astropy dL linearly interpolated on the same 3001 points
   (2.4e-8). That explains stage 1's 8e-5 at small z. endo3's dL is exact (1.6e-7, float32 storage).
   - Synthetic rows use their campaign's own map. The joint model uses O4's map, which differs from the exact one
     by under 8e-5 below z 0.003 and under 2e-6 above z 0.1.
   - The Jacobian uses the exact cosmological ddL/dz. O4 stores that derivative, and it matches to 5.7e-8.
4. **The 1e-6 gates hold except for one storage effect in endo3, which we keep.** endo3 stores its mass density
   in float32. The m2 factor 2 m2/(m1² − 4) loses precision near m1 = 2, so the stored density departs from the exact
   one by up to 9.2e-5 there. Our p_inj is the exact density.

   | Gate | Result |
   |---|---|
   | G1, O4 masses, spins and angles (log) | ≤ 5e-15 |
   | G1, O4 z (relative) | 8.4e-8 |
   | G1, endo3 z (relative) | 4.8e-13 |
   | G1, endo3 total, all 284,672 rows (log) | median 3.5e-7; 255 rows above 1e-6, all with m1 < 2.076; max 9.2e-5 |
   | G2, exporter vs product pdraw, O4 synthetic path | max 8.3e-8 |
   | G2, endo3 stored-input mode | max 3.7e-10 |
   | G2, endo3 synthetic path | 99th percentile 6.6e-7; 44 rows above 1e-6, all with m1 < 2.062; max 9.2e-5 |
   | G2, zero-weight rows | identical sets (1,333 endo3 and 5,129 O4) |
   | G3, z → dL | 1.6e-7 (endo3), 2.4e-8 (O4) |

   - "Stored-input mode" feeds the files' own densities, dL and m1det to the exporter. It isolates the conventions:
     the Jacobian, T, N_k/N, the chi_eff reference swap, and the sentinel.
   - The amended gate requires stored-input mode ≤ 1e-6 everywhere, and the synthetic path ≤ 1e-6 except on endo3
     rows with m1 < 2.1. Its effect on mu is about 1e-4 on 44 of 81,117 rows, which is negligible.
5. **Core does not accept a fractional ndraw.** Core e7c3007 reads ndraw with int(), in `gw/samples.py` and in the
   store check `_positive_count`. A value of 1234567.75 becomes 1234567 with no error.
   - Synthetic products therefore write ndraw = round(Σ_k N_s,k / xi_k). Each row carries the exact
     N_k = N_s,k / xi_k in its Essick fraction N_k / ndraw.
   - Core's mu then equals Σ_k (T_k / N_k) Σ_i p_pop / p_k exactly (`phase12ak/surrogate.py: synthetic_ndraw`).
   - For the joint model, the fraction is (N_s / Z) / ndraw, which is 1 to about 1e-9 rather than exactly 1.
6. **The joint normalisation moves slightly.** With the stored z functions, Z = 2.7022593e-3 yr. Stage 1, with exact
   dVc/dz, had 2.7022637e-3 (−1.6e-6). The Kish sizes are 38,757 / 945,283 / 414,085 (stage 1: 38,757 / 945,289 /
   414,083).
7. **Implementation details of the training loop:**
   - one epoch is a single jitted scan over its batches, with the same arithmetic as fit_to_data's per-batch loop;
   - the validation loss is the exact weighted mean over all validation rows (fit_to_data drops the last
     incomplete validation batch);
   - standardisation uses each model's training rows, unweighted and without bootstrap, and is shared by its five
     members;
   - checkpoints are written every 25 epochs, and a resubmitted lane resumes from them.
8. **Control P.** It uses our split (its test rows are held out), init and batch-order seed 4242, no bootstrap, and
   unweighted training. Its xi is the weighted one, as in the student's script.

**CPU tests.** `tests/test_phase12ak.py` holds 16 tests, all passing: in HENON job 1390322 (15 tests, at 208bc9a), and
locally (16, at cf2a4bd). They check:
- **the detection rule** against gwcat 8263ae9's own `SelectionSet.detected_mask`, on 400-row copies of both raw
  files with edge rows: FAR exactly 1, 0.999, and +inf;
- **the splits:** sizes, disjointness and seeding;
- **the out-of-domain mask** and the clips for A and B;
- **normalisation:** each draw density integrates to 1;
- **xi with monthly weights** against a closed form, where the unweighted estimate is shown to be biased;
- **the joint weight u** against a closed form on a two-campaign toy;
- **the bounded transforms:** round trip, and the log-det against an autodiff Jacobian;
- **a toy flow fit:** a weighted fit recovers a known density (KL < 0.03), and an unweighted fit does not;
- **resume:** a run that is stopped and resumed is identical to an uninterrupted one;
- **save → reload:** bitwise;
- **the exporter:** the sentinel and the scaling;
- **the plan:** 16 entries with the declared seeds;
- **the design constants** against `config/phase12ak_design.json`;
- **the integer ndraw**, whose rounding cancels.

**Smoke test** (rita job 1390323, one A100-80, code 208bc9a, 50 epochs each, outputs `ours/runs_smoke/`; summary
`ours/summary/12AK_stage2_smoke.json`, sha256 782485e8…):

| Model | Steps/epoch | s/epoch | ms/step | Validation NLL at epochs 1 / 10 / 50 | Peak GPU memory | Reload |
|---|---|---|---|---|---|---|
| A_O3 | 14 | 0.107 | 7.7 | 51.52 / 22.94 / 17.81 | 0.28 GB | bitwise |
| A_O4 | 173 | 1.292 | 7.5 | 20.66 / 17.62 / 17.59 | 0.44 GB | bitwise |
| B_joint | 187 | 1.393 | 7.5 | 20.14 / 17.62 / 17.59 | 0.44 GB | bitwise |
| P_control | 173 | 1.294 | 7.5 | 20.78 / 17.66 / 17.58 | 0.44 GB | bitwise |

The loss falls in every model, the jax backend is the GPU, and the save → reload check is bitwise on 1e4 test rows.

**Epoch budget: unchanged** (5000 epochs at most, patience 500). From the smoke timings:
- **Worst case:** every member runs all 5000 epochs:
  - lane 0 (A_O4 × 5, then P) takes 10.8 h;
  - lane 1 (A_O3 × 5, then B × 5) takes 10.4 h;
  - that is 21.2 GPU-hours in total, under the 30 ceiling.
- **Expected:** if training stops near 2000 epochs, as the paper reports, about 8.5 GPU-hours, or about 4.5 h of wall
  time on the two cards.
- **The estimate for completion:** 5–11 h of wall time with both cards; up to about 21 h if the two lanes run one
  after the other (record 12AJ also queues on rita; corrected in B2).

**Prepared submission** (not yet run; from the consumer worktree):

    slurm/phase12ak_submit.sh cf2a4bd

It writes `ours/plans/12AK_train_plan.json` and submits two lane jobs, one per rita A100-80 card:
- the flags are `-p RITA-GPU --qos rita -A phy220048p --gres=gpu:a100-80:1 --cpus-per-task=128 --mem=120G
  --time=7-00:00:00`;
- each entry writes `ours/runs/<name>/`: `ckpt/`, `model.npz`, `metrics.json`, `train.log` and `DONE`;
- the script prints a shell watcher.

A resubmission of the same command continues unfinished entries from their checkpoints.

## Amendment B2 (stage 4: review fixes), 2026-10-19, before any training job

A review of stage 2 (code, data, jobs, provenance, licence) found **no blocking defect**. It confirmed the detection
rule against gwcat 8263ae9 (`np.any(fars < 1, axis=1)`, the single-campaign branch, each campaign's own search columns;
986,829 O4 detections re-counted), the coordinates and Jacobians, xi with the monthly weights, the joint mixture, the
splits (no leakage), the masks, the Slurm flags and the licence. It found eleven non-blocking defects. Each is fixed
or recorded below, before any training job. Nothing here involves H0.

**Commits (local only, not pushed).**
- Consumer branch `phase12ak/pdet-surrogate`:
  - f5c33cd: the fixes and their tests;
  - 2b31955: the status job's job-id list is passed joined by ':' (a comma splits `sbatch --export`; caught in a dry
    run of the submit script).
- The ensemble runs from the detached worktree `pdet_surrogate/ours/worktrees/2b31955040f1`.

**The eleven items.**
1. **endo3 is O3 only, not O1+O2+O3.** Its GPS span is 1238166018–1269561618 (O3a start to O3b end), its analysis
   time (28,749,576 s = 0.911 yr) is O3's alone, and it has no semianalytic SNR column. Relabelled "O3 BBH (endo3,
   LIGO-T2100113-v12)" in the inspection table and the builder's docstring. The task brief carried the same mislabel.
   Every number is unchanged; only the name was wrong.
2. **Shared random streams between models (fixed; it could not be fixed after training).** Before B2, B_joint's
   training rows (O3 rows, then O4 rows) received the same Poisson bootstrap factors as A_O3 on all 58,404 O3 training
   rows, and A_O4 and B_joint shared initialisation and batch order. Now every stream derives from
   SeedSequence([declared seed, model index]), with model index A_O3 0, A_O4 1, B_joint 2, P_control 3:
   - init: `flow_key_seed` = the first uint32 of that sequence (stored in each model's config);
   - batch order: the same derivation from the batch seed;
   - bootstrap: `default_rng(SeedSequence([boot seed, model index]))`.
   The declared seeds (1001–1005, 3001–3005, 2001–2005, 4242) are unchanged. The separate-vs-joint comparison is
   therefore unpaired, and the five members of each model are independent of the other models' members.
3. **Model files carry provenance.** `model.npz` now also holds the jax, jaxlib, flowjax, equinox and paramax versions,
   the skeleton's treedef string and every leaf's shape and dtype. `load_model` refuses a file without provenance, with
   any version mismatch, or with a different tree structure or leaf layout. This closes the flowjax-19 silent
   mis-load trap for every later reader. The 50-epoch smoke models (no provenance) are not loadable any more, by
   design; they are not used.
4. **A run's identity.** Each checkpoint and each `metrics.json` carries (code sha, code dirty flag, sha256 of the
   canonical plan entry). A checkpoint of another identity is refused (never resumed), and a DONE run of another
   identity is refused (exit 3, never skipped). A rerun of the same commit and plan resumes as before.
5. **Training sets are checked.** Each plan entry carries the gated sha256 of the files it reads (O3 f41580d8…, O4ab
   9ed5dde9…); training refuses (exit 4) on any mismatch.
6. **V1 for the joint model uses weighted statistics.** Thinning by u / max u would keep about 3,300 B test rows (2.8%
   of O4's, 6.7% of O3's), far below PQMass's 30,000. V1 instead uses each row's loss weight as a sample weight:
   weighted KS and AD, weighted PQMass region counts, and classifier sample weights. The same applies to A_O4 (weights
   w). The V1 row of the validation table and the design JSON are amended.
7. **The joint model's exporter.** `injections.export_pdraw_joint` is added: q_mix does not factor into a
   mass-redshift part times a spin part, so ln q_mix − LN_ANGLES goes through the mass-redshift slot, the spin slot is
   0, T = 1 and the fraction is (N_s / Z) / ndraw; dL and the Jacobian follow O4's maps (B1 item 3). A closed-form test
   checks it against the O4 exporter times q_mix / p_4. **Still open, required before the use-case gates (U1–U3):** a
   core-format writer for synthetic products and a **null-surrogate gate**: the real detected rows run through the
   synthetic writer (with `synthetic_ndraw` and N_s,k = n_det,k) must reproduce the H0-shape of the product's ln mu over
   the 241-point grid to ≤ 1e-6 in core. That checks the plumbing independently of any flow. It needs no retraining.
8. **Control P's normalisation.** P is trained unweighted but its xi is the weighted one (1.148022e-3, as the student's
   script); the self-consistent value for an unweighted flow is 1.133693e-3, 1.26% lower. Its config now records both.
   P's X1 and X2 are reported under both values; with the weighted xi they are not comparable to A and B. The offset
   is constant in H0, so U1–U3 are unaffected.
9. **Design JSON wording.** It now says that no constraint JSON is read or used as fitted values, and that the paper's
   `pdet_13d.json` interval values are transcribed as transform settings for control P only (as B1 said).
10. **The watcher.** The old `until ! squeue … | grep -q .` loop ends early on a transient `squeue` failure. The new
    watcher polls `sacct` states and the STATUS.json file; a failing `sacct` keeps it waiting.
11. **The time estimate** assumed both rita cards free. Corrected in B1: 5–11 h with both cards, up to about 21 h if
    the lanes run one after the other.

**Added for stage 4.** A HENON CPU job (`slurm/phase12ak_status_henon.sbatch`, `--dependency=afterany` on both lanes)
runs `scripts/phase12ak_status.py` and writes `pdet_surrogate/ours/summary/STATUS.json`: for each of the 16 entries,
whether it trained, stopped part-way or never started; epochs, best epoch, stop reason; final train and validation
losses and the best validation loss; the theta-space train/val/test NLL; the reload check; the run identity and
derived seeds; and the paths (model.npz with its sha256, metrics.json, train.log). It also records the lanes' sacct
states. An earlier STATUS.json is moved aside at submission.

**Tests.** `tests/test_phase12ak.py` now holds 22 tests; all pass on CPU at 2b31955 (from its worktree; log
`ours/logs/12AK_stage4_tests_2b31955.txt`) and at f5c33cd. The six new ones check:
- that equal declared seeds give different bootstrap factors (A_O3 against B_joint's leading O3 rows), different
  derived seeds and different initial flows across models, and that the streams stay seeded;
- that `load_model` refuses a file without provenance, with a flowjax version of 19.0.0, or with a changed treedef;
- that a checkpoint of another identity is refused and the same identity resumes;
- that the train script refuses an ungated training set (exit 4) and a DONE run of another identity (exit 3);
- `export_pdraw_joint` in closed form (ratio to the O4 exporter = q_mix / p_4; = N_4/N outside O3's support) and its
  refusal outside both supports;
- that the status script reports a trained, a partial and a missing entry correctly.

A CPU dry run of one real entry (A_O3, 2 epochs, scratch directory, then discarded) passed the data-hash check,
derived its seeds, saved with provenance, reloaded bitwise, skipped itself on rerun with the same identity, and was
summarised correctly by the status script.

**Submission.** `slurm/phase12ak_submit.sh 2b31955` from repo_12AK, plan `ours/plans/12AK_train_plan.json` (16
entries; up to 5000 epochs, patience 500, unchanged). Lane 0 (rita card 1 of 2): A_O4 ×5, then P. Lane 1 (card 2):
A_O3 ×5, then B_joint ×5. At submission both rita cards were running record 12AJ's GPU jobs (declared at about 75–78
min each), so the lanes queue behind them. Job ids follow below.

**Submitted 2026-10-19T13:07Z** (code 2b31955, worktree `ours/worktrees/2b31955040f1`, plan sha256 480ce7ec…, job list
`ours/plans/12AK_train_jobs.json`):

| Job | Lane | Entries | Resources |
|---|---|---|---|
| 1390334 | rita lane 0 | A_O4_m1–m5, then P_control | RITA-GPU, one A100-80 |
| 1390335 | rita lane 1 | A_O3_m1–m5, then B_joint_m1–m5 | RITA-GPU, one A100-80 |
| 1390336 | HENON status | writes `ours/summary/STATUS.json` | afterany:1390334:1390335 |

**Estimated total time to completion:** the lanes wait about 1–1.5 h for 12AJ's two rita jobs to end. Then 5–11 h with
both cards (expected near the low end if training stops near 2000 epochs), so about 6–12.5 h from submission, and at
most about 22.5 h if the lanes run one after the other. The 7-day limit is a ceiling, not the estimate.
