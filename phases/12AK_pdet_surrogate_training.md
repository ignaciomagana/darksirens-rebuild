# 12AK — A detection-probability surrogate for the selection term, trained by us (stage 1: understand and declare)

## Status

**DECLARED (stage 1 of 4, 2026-10-19); stage 2 BUILT (amendment B1, 2026-10-19); review fixes and SUBMITTED
(amendment B2, 2026-10-19).** Stage 2 wrote the training sets, passed the pre-training gates, and ran a 50-epoch smoke
test of each model on one rita card. A review found no blocking defect and eleven non-blocking ones; B2 fixes or
records each before any training job, and then the 16-member ensemble was submitted (job ids in B2). Validation
(gates V1–U3) follows in a separate workflow. **Training DONE (2026-10-19, 22:26 UTC): 16/16. VALIDATION DECLARED
(amendment B3, 2026-10-20), before any validation job:** V1 as distances, the core-format writer, the null products
and the plumbing gate, X1, X2, U1 and U2 as numerical gates, U3's choice, and the synthetic product for record 12AN's
D4.

**VALIDATION DONE (2026-10-20); results recorded on 25 Oct 2026, after the independent review.** Every validation step
finished (`validation/STATUS.json`: complete, no product failure) from a clean worktree of repo_12AK ad0c0b9;
`D4_CHOICE.json` at 03:56 UTC and `VALIDATION.json` at 05:17 UTC on 2026-10-20. U3 chose **model A**, and every D4
number is labelled **systematic**: X1, X2 and U2 fail for both models; U1 and the plumbing gate pass. Record 12AN's
Results carry the same gate outcomes. See "Amendment (25 Oct 2026): independent review" at the end.

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

## Training done (2026-10-19, 22:26 UTC)

All 16 entries trained, and every model reloads bit for bit: A_O3 m1 to m5, A_O4 m1 to m5, B_joint m1 to m5, and
P_control. The run was paused once, for 12AL ("D1–D3 first"). Lanes 1390413 and 1390335 were cancelled at 19:10 UTC,
and the work resumed from checkpoints as 1390498 (1 h 29 min) and 1390499 (59 min). Both COMPLETED, released at
20:47 UTC.

The first status job, 1390336, ran early when the lanes were cancelled; its partial file is kept as
`summary/STATUS_1390336_paused_partial.json`. The status job 1390500 wrote `summary/STATUS.json`.

Validation (V1/V2/X1/X2/U1–U3, the ensemble spread, the core-format writer, the null-surrogate check) is a separate
step and has not started. *(25 Oct 2026: it ran on 2026-10-20; see "Validation results" in "Amendment (25 Oct 2026): independent review" at the end.)*

## Amendment B3 (validation, declared 2026-10-20 about 01:30 UTC, before any validation job)

This amendment fixes the validation (V1, V2, X1, X2, U0 to U3), the two pieces that B2 item 7 left open (a
core-format writer for synthetic products and the null-surrogate gate), and the synthetic product that record 12AN's
D4 reads. Nothing has run. It was written together with record 12AN's declaration (record branch
`phase12an/declare`), which uses it.

**Blinding: unchanged.** No posterior and no H0 value is computed or written here. The core-side checks write only
H0-shapes of ln μ differences, ensemble spreads, and ratios of μ. Per-point ln μ goes to an absolute file that agents
never open. The H0 values used are the a-priori ones: the 241-point grid [20, 140] at step 0.5, the windows [50, 90]
(12AK's) and [50, 100] (12AN's), and the generation cosmology (67.9, 0.3065). The spectral-only posterior with D4
injections is computed in record 12AN, under its rules, not here.

**The owner's reporting rule applies.** No p-values and no σ-based decisions. V1 reports two-sample distances. The
gates below are numerical-accuracy checks with fixed tolerances.

### B3.1 Inputs (sha256)

All under `phase12_5/pdet_surrogate/ours/`. Each `model.npz` equals the sha256 in `summary/STATUS.json`
(`edf9e5594953f95a7ddc8810a0e70bfe4efd4e535f351003257688d06811a7cb`); all 16 trained, all reload bit for bit.

| model | m1 | m2 | m3 | m4 | m5 |
|---|---|---|---|---|---|
| A_O3 | `7ad25dc42f0a3d0954eff5d2b7c6e1740f0fbd2443d491b5b3b0fdc9a26f5e73` | `9f0d92e36525003009646f8fa5e990b44ce850ac832d0c23345e37eb490316c3` | `6edc4bc0530dfadb8a8437bba02291748bfbbabf3e5d08051ba2862362f8646d` | `25f4fc50dac586e7bb61aa4fe468e7fc32dbfc02e9a6ecd7f001d995eaa2c69c` | `1a74ce4413fe74ab7fa6dee6b1f0500de43eb2f371c4f98e1c9b98c0f0c64ab7` |
| A_O4 | `9cbc3f13dda09ded4f3f6f49eafa682361e37c1f59174dd55c54f42be630ba68` | `d1f26b2aa6ccdbda6b249ad7fb1c4e9f7b0ebbfedfb01b16ae18ccd58282c8d1` | `bc3d3a5ab3fbda2a13b3e516775d539e98a1e4cd0efaf325d95c54bbd14933df` | `f0f62a2e2020c176bd3c7d88f0733ce4a35627435122da0e0113d7ab22a27980` | `5b5a3b2c13818608241e79a0392c94e57aa3d0e28a9ff8d35766c9472450ed8c` |
| B_joint | `49c2495538de4fc4c337e1a6a866a72a0cbfc80583b93f553b7b58527936b8f5` | `10463a7ae72b096fc4a3199aff038faae143534b4cbe386525de09241e2e45ea` | `9b6dc2380d47a259f92bdc3e30bb79f762b3c8cba0543c9e2aa3fb835602f56e` | `c1acd6648f260486ed4cb82f733f008bf1a4c5fd4e4e76113df7d61edd550f5e` | `08db9cb2b1552fe8a14ed3d051ca42eaf041547157216b1c76f58179df3987d8` |
| P_control | `8e7dbd20dce0acd7cf1b13980f5a9f18123561a50035765b15261e42713c84df` | | | | |

- Training sets: `data/12AK_detected_O3.h5` `f41580d87e15db3dc8d14da3d61ccef0fc369b339033545f621104ffe8b1be32`,
  `data/12AK_detected_O4ab.h5` `9ed5dde953a9cd31606da32248199993daec9a602bd1bd29a433149dcc9249b7`. They hold the 13
  inputs, the weights, the split labels, the raw row index and the product's pdraw per row.
- The product `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5`:
  `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6`.
- The raw files (endo3 `86e7e481…`, O4ab `d5d28b77…`, full values in `config/phase12ak_design.json`) were re-hashed
  in stage 2. The writer re-hashes them when it reads them.
- The spectral-only population block: `phase12_5/spectral_gamma/runs/gamma_+2.5439/spectral_h0.json`
  `db9f7b80c4b799c18559c99040916a821ed99aa7feb06fcec1d6589a171a6f9f`.

Every validation job checks these and refuses a mismatch.

### B3.2 Code, environments and precision

- **Code:** repo_12AK, a new branch `phase12ak/validation` from 2b31955 (the build stage writes it). Local commits
  only. Every validation entry runs from a clean worktree of one committed sha under `ours/worktrees/<sha>/`.
- **Flows** (sampling and log densities): our GPU venv `pdet_surrogate/venv_gpu` (jax 0.7.2, flowjax 17.2.1),
  loaded through `load_model`, which refuses any version or structure mismatch (B2 item 3). **x64 on, as in
  training** (the design JSON's `x64: true`). The flows are not run in float32.
- **Core-side checks:** core e7c3007 through the consumer env, x64 on and enforced, `core_defaults`, the soft guard at
  20 (as declared).
- **The writer:** numpy in the GPU venv, with the gwcat chi_eff prior imported from the pinned 8263ae9 source tree
  (as B1).
- No pip into a shared env. Caches on the project disk.

### B3.3 Sampling

- **Members.** Model A's member m is the pair (A_O3_m, A_O4_m). Model B's member m is B_joint_m. P_control is one
  member.
- **Chunks.** Each member draws 10 chunks. A chunk is the size of the campaign's real detected set: A_O3 81,117 and
  A_O4 986,829 (so model A's chunk has 1,067,946 draws), B_joint 1,067,946, P_control 986,829. So each member draws 10
  times the real count, as declared in stage 1.
- **Seeds.** Model index as B2 item 2 (A_O3 0, A_O4 1, B_joint 2, P_control 3); member m = 1 to 5, P_control 42.
  - flow draws: `jax.random.fold_in(jax.random.key(s), j)` for chunk j = 0 to 9, with s the first uint32 of
    `SeedSequence([7300 + m, model index])`;
  - the thinning above the clip: `default_rng(SeedSequence([7400 + m, model index, j]))`.
- **Per draw:** θ from the flow's full theta-space distribution; ln p_flow(θ); ln p_inj(θ) (the campaign's for A and
  P; ln q_mix for B); the raw p_det = ξ p_flow / p_inj; the keep mask of `surrogate.synthetic_keep` (support drop,
  and keep with probability clip / p_det above the clip; the clip is 1 for A and P, and the summed T_k of the
  campaigns whose support holds θ for B).
- **N_draw for the product** counts every draw before masking (as declared): N_k = N_s,k / ξ_k.
- Outputs: `validation/samples/<model>/<member>/chunk_<j>.npz` (θ, both log densities, the raw p_det, the mask).
  H0-free.

### B3.4 The core-format writer

- **Format:** `gwcat-selection-2.0`, the real product's 16 datasets in float64: `a1`, `a2`, `chieff`, `chip`,
  `cost1`, `cost2`, `dL`, `dec`, `m1det`, `m1src`, `m2det`, `m2src`, `pdraw`, `q`, `ra`, `redshift`.
- **Columns from the 13 inputs:** m1src, m2src, redshift = z; m1det = m1 (1+z) and m2det = m2 (1+z); dL from the
  campaign's own z → dL map (B1 item 3; model B uses O4's); q = m2/m1; a1, a2, cost1, cost2 as drawn; chieff =
  (m1 a1 cost1 + m2 a2 cost2)/(m1 + m2); chip by gwcat 8263ae9's own function; ra as drawn (in [0, 2π)); dec =
  arcsin(sin dec).
- **pdraw:** gwcat's chieff-reference convention through `injections.export_pdraw` (A and P: each campaign's
  p_k, T_k and fraction N_k/ndraw; weight 1) and `export_pdraw_joint` (B: q_mix, T = 1, fraction (N_s/Z)/ndraw). The
  sentinel 1e300 where a spin exceeds 0.99 or chi_eff leaves the reference prior's support.
- **ndraw** = round(Σ_k N_k), with the exact N_k in each row's fraction (`surrogate.synthetic_ndraw`, B1 item 5).
- **Attributes:** the real product's, with ndraw and the row counts (`n_detected`, `n_injections_before_filter`,
  `n_injections_after_filter`) replaced and `campaign_ndraws` set to the rounded N_k. Added, as provenance: the
  model, the members, the chunks, N_s per campaign, the exact N_k, ξ, the kept counts, every model's sha256, the
  repo_12AK sha, the seeds, and the writer mode. A CPU test checks that core e7c3007 loads every kind of product
  (A, B, P, both nulls) through `ds.load_injections`, and that each attribute core reads (`ndraw`,
  `chi_eff_swap_applied`, `format_version`, the spin basis, `sky_position_available`) keeps its meaning.
- **Row order:** member, then chunk, then draw order, kept rows only. The null products keep the real product's order.
- **Products written** (under `validation/products/`, each with its sha256 in `manifest.json`):
  - `val/<A|B>/m<k>.h5`: each member's 10 chunks (about 10.6 million kept rows each). For U1 and U2.
  - `val/P/m0.h5`: P_control's 10 chunks (O4 rows only).
  - `d4/<A|B>/m<k>.h5`: chunks 0 and 1 of member k (2,135,892 draws). For 12AN's member entries.
  - `d4/<A|B>/pooled.h5`: chunks 0 and 1 of all five members in one file. **N_s = 10,679,460 draws, ten times the
    real count** (A: O3 811,170 and O4ab 9,868,290). For 12AN's D4-C check and its S/D4 grid.
  - `null/null_P.h5`, `null/null_S.h5` and `null/null_S_O4.h5` (B3.5).
- **Departure from stage 1's export (for D4 only).** Stage 1 declared 10 times the real rows per member. The
  validation keeps that (the `val/` files). The product that 12AN uses holds ten times the real rows in all, split
  equally over the five members (two chunks each). Reason: the owner's brief for 12AN, and the cost of a catalog
  likelihood per point grows with the row count. Pooling the members samples the ensemble-mean surrogate (12AN
  algebra v). The D4 product is a subset of the validated draws.

### B3.5 The null products and the plumbing gate (B2 item 7, completed, with one departure)

**The null products** are the 1,067,946 real detected rows, written by the writer:
- **null_P (synthetic path):** from the rows' 13 inputs, exactly as flow draws are written (maps, Jacobian, pdraw),
  but with each row's own monthly weight w_i in pdraw (O3: 1) and N_k = N_draw,k, the campaign's real number drawn.
  Then ndraw = 944,412,448 exactly.
- **null_S (stored-input mode, B1 item 4):** every column except pdraw copied from the product row (aligned by the raw
  row index); pdraw from the writer with the raw files' own stored densities. This isolates the file format, the
  attributes and the pdraw conventions (Jacobian, T, fractions, chi_eff swap, sentinel).
- **null_S_O4:** null_S restricted to the O4 rows, with N_O4 and T_O4 only. It is P_control's reference.

**Departure from B2 item 7.** B2 wrote "with `synthetic_ndraw` and N_s,k = n_det,k". With O4's weighted ξ that gives
N_O4 = n_det N_draw / Σw, 1.26% off N_draw for O4 and not for O3. That moves O4's part of μ against O3's by a constant
factor, which bends the H0-shape wherever O3's share of μ changes with H0. The real rows are draws from the
unweighted detected density, not from the weighted one that a flow learns. So the null carries their weights and the
real N_draw,k. The flow path is unchanged.

**The plumbing gate (gates 12AN's D4).** It passes when all of these hold:
- **Shape:** with core's spectral-only selection term (the population block above, the 241 coarse points), δ(H) =
  ln μ_null_P − ln μ_product has max |δ − mean δ| ≤ 1e-6 over the 241 points (12AK's declared gate). Reported beside:
  the level mean δ and max |N_eff,null/N_eff,product − 1|. The same for null_S, reported.
- **Rows, the columns the catalog path reads:** null_P's ra (modulo 2π) and dec within 1e-12 rad of the product's;
  dL and m1det within 1e-6 relative.
- **Reported, not gating:** every other column's largest difference; pdraw's (with B1 item 4's endo3 rows at
  m1 < 2.1 counted apart); the number of rows whose nside-256 pixel differs from the product's.

If the plumbing gate fails or does not run, record 12AN runs no D4 entry, and U1 to U3 are not computed (they use the
same writer).

### B3.6 The checks: V1 and V2 (diagnostic), X1, X2, U1 and U2 (numerical gates), U0 (scale), U3 (choice)

**V1, amended: two-sample distances, no p-values.** Flow draws (the kept draws of chunk 0, per member, and the five
members' chunk 0 pooled) against the held-out test rows, each test row weighted by its loss weight (w for O4, u for B,
1 for O3), as B2 item 6:
- per marginal, for the 13 inputs and chi_eff, q and the chirp mass: the weighted Kolmogorov distance
  sup |F_flow − F_test|, and the weighted 1-Wasserstein distance divided by the test rows' weighted sd;
- jointly, on the standardised 13 inputs: PQMass's region-count total-variation distance, ½ Σ_r |f_flow,r − f_test,r|,
  over 100 nearest-reference regions (references drawn from the pooled set, seed 7601; our implementation of PQMass's
  construction);
- a classifier two-sample distance: the held-out AUC of a gradient-boosted classifier (scikit-learn's
  HistGradientBoostingClassifier in the GPU venv; balanced, weighted, 50/50 split, seed 7602), written as the AUC and
  2|AUC − 0.5|.
- **Scale, beside each:** the same distance between the test rows and an equal-size, equally weighted subset of the
  validation rows (two real samples; seed 7603). It is a scale, not a test. No decision is taken from it.
- No KS or AD p-value, no PQMass p-value, no Cauchy combination. V1 decides nothing.

**V2, amended.** The per-bin ratios as declared (z, m1, q, chi_eff, sin dec and RA; bins straddle O3's m1 = 100 and
z = 1.9; also on the training rows). The summary lists the bins with |r − 1| > 3%. The "3σ" clause is removed: no
σ-based flag. V2 decides nothing.

**X1 (gate).** Per member and campaign: ξ_emu/ξ = E_flow[min(1, clip/p_det) · 1_support], computed as the mean over
the drawn samples (the kept fraction is reported beside it). Passes when every member of the model is at least 0.995.

**X2, amended (gate).** μ_flow/μ_MC − 1 for four populations: p_O3, p_O4 and q_mix (in θ space, numpy, with 12AK's
own densities; μ_MC from the real rows with their weights), and the spectral-only population at the generation
cosmology (67.9, 0.3065) through core. On each model's pooled `val/` members; per member reported. Passes when
|μ_flow/μ_MC − 1| ≤ 1% for all four. The "or 2σ_MC" clause is removed: no σ-based decision. Core's relative Monte-Carlo
sd of μ_MC is printed beside it, as a number. P_control's X2 is on the O4 part, under both its ξ values (B2 item 8).

**U0 (scale; decides nothing).** 100 Poisson(1) bootstraps of the real rows (seeds 7501 to 7600; each row repeated by
its count, ndraw unchanged), spectral-only ln μ on the 241 points: the rms and the largest S_W[50, 90] of
ln μ_boot − ln μ_MC. It shows the size of the real Monte Carlo's own shape noise inside U1.

**U1 (gate).** Per model, with the spectral-only population on the 241 points:
- Δ_m(H) = ln μ_m − ln μ_MC for each member's `val/` file, and Δ_ens for the five members pooled exactly (12AN
  algebra v);
- S_W = max over the coarse points in the window of |Δ − mean_W Δ|, with mean_W the plain mean over those points;
- reported: S_W on [50, 90] and on [50, 100], S over all 241 points, the level mean_W Δ, and N × S_W in nat (N = 259);
- also U1 of the D4 product itself (`d4/<model>/pooled.h5`), reported beside;
- **passes when S_W[50, 90] of Δ_ens ≤ 3e-3** (as declared).

**U2 (gate).** The sd over the five members (ddof 1) of Δ_m − mean_W Δ_m. Passes when its maximum over the coarse
points in [50, 90] is at most 1.5e-3 (as declared). The maximum over [50, 100] is reported.

**U3 (the choice), amended.**
1. A model that passes the plumbing gate, X1, X2, U1 and U2 is preferred to one that does not. **New.** Reason: U3
   alone could pick a model that fails X1 or U2, which would make every D4 number a systematic when the other model
   would have counted as a noise reduction.
2. Between two models in the same state, the smaller ensemble S_W[50, 90] wins; ties within 5e-4 go to A (as
   declared).
3. P_control is never a candidate. Its S_W is reported as context.

**The label (as declared):** D4 counts as a noise reduction only if X1, X2, U1 and U2 pass for the chosen model.
Otherwise 12AN labels every D4 number "systematic".

### B3.7 Order, outputs and compute

**Order.** The entries run in record 12AN's pool (12AN, Compute), in this order of prerequisites:
1. **sample** (GPU, venv_gpu): all 16 models, 10 chunks each, and X1. About 15 minutes.
2. **write** (CPU on a lane's node, 16 to 32 processes): every product of B3.4 and B3.5, and the manifest. About 20
   minutes.
3. **V1 and V2** (CPU on a lane's node). About 20 minutes. Nothing waits for it.
4. **core: null** (GPU, consumer env): the plumbing gate, X2's core part, U0. About 15 minutes.
5. **core: A** and **core: B** (GPU, consumer env, in parallel): U1 and U2 per model; U1 of the D4 products; P's U1.
   About 25 minutes each.
6. **choose** (CPU, seconds): X1, X2, U1, U2, the plumbing gate and U3. It writes `validation/D4_CHOICE.json`
   (location-free: the model, the gate results, the label, the D4 product's paths and sha256). It exits non-zero
   when the plumbing gate failed or did not run, and 12AN's D4 entries are then blocked.
7. **the validation summary** (HENON, in 12AN's summary job, afterany on every lane): `validation/VALIDATION.json`
   and `validation/STATUS.json`, V1 and V2 included. The results are then recorded here.

**Outputs** under `pdet_surrogate/ours/validation/`: `samples/`, `products/` (with `manifest.json`), `metrics/`
(location-free: distances, ratios, Δ shapes, spreads), `absolute/` (per-point ln μ and N_eff: never opened by
agents), `D4_CHOICE.json`, `VALIDATION.json`, `STATUS.json`, `logs/`. About 50 GB on the project disk (14 TB free at
01:10 UTC).

**Compute.** About 2 card-hours in all, 40 minutes of it CPU work on a lane's node, and about 1 to 1.3 hours of wall
time from 12AN's submission to `D4_CHOICE.json` when four cards are free. Not counted: the build stage's tests and
short GPU control (12AN).

**Tests (the build stage).** CPU tests on tiny inputs: the writer's columns and attributes, and core loading each
product kind; the null products equal the real product where they should; pooling five members equals one file of
their rows; X1 against a closed form; U1 and U2 on known curves; U3's rule in each case; V1's distances against
closed forms (two equal samples give 0); the seeds and chunking (a chunk is the same whatever else is drawn).

### B3.8 Build notes (record 12AN amendment B1), 2026-10-20, before any validation job

- **Code.** The validation runs from branch `phase12ak/validation` of `phase12_5/repo_12AK` (from 2b31955): ec2e3eb,
  9173947, 170fae2, a136a28, 00eb483, c8d29e4, ad0c0b9. The production sha is stated in record 12AN's Production
  section; every validation step runs from a clean worktree of it.
- **The sample chunks** are written to `validation/samples/<model>/<member>/chunk_<j>.npz`, as B3.3 declares. The build
  code had doubled the directory (`validation/validation/samples/`). Fixed in ad0c0b9.
- **`D4_CHOICE.json` names the null products by explicit keys,** `null_S` (12AN's D4-N, stored inputs) and `null_P`
  (D4-N′, the synthetic path).
- **V1 and V2 for P_control use its loss weight, 1.** P_control was trained unweighted. B3.6's "w for O4" applies to
  A_O4, and u to B.
- **V1's classifier scale** weights the validation subset instead of resampling it (c8d29e4). Resampling a weighted
  set repeats rows, and the classifier memorised them.
- **Order (12AN's pool).** `core: P` is a soft prerequisite of `choose`: the choice waits for it while it may finish,
  and its failure never blocks the choice. V1/V2 runs below every GPU entry (nothing waits for it). A failed step on a
  40 GB card is retried on an 80 GB card. The choice's exit 3 (plumbing gate failed) blocks every D4 entry at once.
- **The validation summary (step 7)** runs in 12AN's summary entry, the pool's last entry, on a lane's node CPUs, before
  12AN's summary. The HENON summary job stays as the fallback.
- **The plumbing gate's coverage, stated as a limit.** null_P sets each campaign's fraction directly as N_draw,k/ndraw.
  The gate does not exercise `synthetic_ndraw`'s per-campaign ξ normalisation, nor model B's `export_pdraw_joint`
  path. Those rest on the build stage's CPU closed-form tests.
- **Writer details:** ra modulo 2π; `spin_reference_excluded_rows` the product's own count; `T_obs_yr` and
  `campaign_ndraws` per product. Core reads none of these attributes.
- **Build-stage indication, not the validation:** X1 on one full-size chunk was 0.9495 for A_O3 member 1 and 0.9943
  to 0.9958 for B's members (A_O4 member 1: 0.9993). If production confirms this, no model passes X1 and every D4
  number is labelled "systematic". The production numbers are recorded here after the run.

## Amendment (25 Oct 2026): independent review

An independent multi-agent review of the consumer repo (desi_darksirens_selection at the review head 17a65bb, 24-25
Oct 2026; report `darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in
parentheses below; only confirmed findings are fixed. The owner took the review's recommended option in every decision
on 25 Oct 2026. Each item names the consumer pull request that fixes it and its merge commit on the consumer's main
branch. The final main is 6d0f800 (26 Oct 2026); `./ci.sh` passes there in both record environments (HENON, CPU;
`ci_logs/20261026T051301Z_7566d8eb6d34_consumer_e7c3007batch_cuda12.log`, 1349 passed, and
`ci_logs/20261026T051301Z_7566d8eb6d34_consumer_1022429_lss57afebe_cuda12.log`, 1364 passed; none failed).
Location-free throughout. Unless an item says otherwise, no number of record changes. Findings whose fix packages are
not merged yet (the catalog model, the GW inputs, the variance guard and estimator noise, resume markers, the 12AQ
readings and 12AO's causes) are not amended here; the review's per-record table lists them.

**The code and environment of record (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; findings
C008, C010, C050, C051, C143, G4.1).** The code of this record is on the consumer's main branch since the
consolidation (PR #20) and its follow-up (PR #21). The environment it ran in is named, with its full pip freeze and
sha256, in `config/record_envs/12AK.json`; `scripts/check_frozen_environment.py --record 12AK` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AK/<sha7>` on
GitHub (b803b26, cf8367a, 208bc9a, cf2a4bd, f5c33cd, 2b31955, ec2e3eb, 9173947, 170fae2, a136a28, 00eb483, c8d29e4,
ad0c0b9). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was green at the
follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Code of record (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding G4.1).**
`phase12ak/validation` (which contains `phase12ak/pdet-surrogate`; up to ad0c0b9) is merged into the consumer's main
(merge c03e04a); tags `side-branch/phase12ak/pdet-surrogate` and `side-branch/phase12ak/validation`. Its CPU tests
pass in the 12AK venv at the consolidation (38 passed) and skip, with the reason, in the consumer environments (no
equinox, flowjax, paramax). Environment manifest `config/record_envs/12AK.json` (the 12AK venv's freeze, unchanged
since 19 Oct).

**Operations (consumer PR #30, merge 6d0f800; finding C049).** This record's afterok Slurm submissions now carry
--kill-on-invalid-dep=yes, so a failed upstream job ends its dependants instead of leaving them pending (as in 12AG).
The flag changes only what happens when an upstream job fails.

### Validation results (2026-10-20; recorded 25 Oct 2026; consumer PR #23, merge edabeb6; finding G4.11)

B3.7 step 7 and B3.8 said the production numbers would be recorded here after the run; until the independent review
they were only in record 12AN's Results. They are recorded here from `validation/VALIDATION.json` (2026-10-20 05:17
UTC) and `validation/D4_CHOICE.json` (03:56 UTC), both at repo_12AK ad0c0b9 with no dirty file.
`scripts/phase12_5_record_errata.py ak` (consumer commit 9a76252, merged with PR #23) recomputes every gate from its
metric and tolerance, and U3's choice and the label from their rules; all agree with the stored verdicts. No posterior
and no H0 value is involved; the H0 numbers are the declared windows [50, 90] and [50, 100].

**Status.** All eight steps done (sample, write, V1/V2, core: null, core: A, core: B, core: P, choose); every product
written and checked by sha256, no failure. The D4 product of the chosen model, `products/d4/A/pooled.h5`: 10,634,443
rows, 9,335,484,607 draws, sha256 f01a6270aebe….

**The gates and the choice** (B3.6):

| check (tolerance) | model A | model B |
|---|---|---|
| X1: smallest ξ_emu/ξ over members (≥ 0.995) | 0.9450 (fail) | 0.9943 (fail) |
| X2: μ_flow/μ_MC − 1, `p_O3` (≤ 0.01 in size) | -0.0074 | -0.0109 |
| X2: μ_flow/μ_MC − 1, `p_O4` (≤ 0.01 in size) | -0.0132 | -0.0042 |
| X2: μ_flow/μ_MC − 1, `q_mix` (≤ 0.01 in size) | -0.0126 | -0.0049 |
| X2: μ_flow/μ_MC − 1, `spectral_population_gen_cosmology` (≤ 0.01 in size) | -0.0027 | +0.0069 |
| X2 verdict | fail | fail |
| U1: ensemble S_W[50, 90] (≤ 0.003) | 9.28e-04 (pass) | 1.49e-03 (pass) |
| U1: ensemble S_W[50, 100] (reported) | 1.04e-03 | 1.61e-03 |
| U1: members' S_W[50, 90] (reported) | 8.0e-04 to 4.0e-03 | 1.4e-03 to 5.9e-03 |
| U2: largest member sd on [50, 90] (≤ 0.0015) | 0.0028 (fail) | 0.0032 (fail) |
| U2: largest member sd on [50, 100] (reported) | 0.0034 | 0.0040 |
| every check | fail | fail |

- **X1.** Model A's smallest is O3 member 2 (O3 members 0.945 to 0.960; O4 members 0.9991 to 0.9994); B's members are
  0.9943 to 0.9958. The build-stage indication of B3.8 (0.9495 for A's O3 member 1) is confirmed: no model passes X1.
- **X2.** Core's relative Monte-Carlo sd of μ_MC, printed beside it: 0.0018 (p_O3), 0.0016 (p_O4), 0.0016 (q_mix),
  0.0031 (the spectral population at the generation cosmology).
- **U1.** Level mean_W Δ on [50, 90]: −0.0025 (A), +0.0071 (B). N × S_W[50, 90] with N = 259: 0.24 nat (A), 0.39 nat
  (B). U1 of the D4 products themselves: S_W[50, 90] 5.0e-4 (A), 1.3e-3 (B).
- **The plumbing gate passes:** shape max |δ − mean δ| 3.9e-9 against 1e-6 (null_S, reported: 5.2e-9); the rows the
  catalog path reads match; no row changes its nside-256 pixel.
- **U3:** both models fail some check, so the smaller ensemble S_W[50, 90] wins: **model A** (9.28e-4 against 1.49e-3,
  outside the 5e-4 tie). **Label: systematic** (X1, X2 and U2 fail for A).
- **P_control** (context, never a candidate): X1 0.9990 and X2 within 0.01 (both pass); its single-member S_W[50, 90]
  is 2.95e-3.
- **The ensemble's effective sample size** over the real Monte Carlo's, at its smallest over the grid: 46 (A) and 70
  (B).

**Diagnostics that decide nothing** (V1, V2, U0; B3.6). V1: flow draws (each model's five members' chunk 0 pooled;
P_control's one member) against the held-out test rows, each beside its scale, the same distance between the test rows
and an equal-size subset of the validation rows:

| flow model | largest KS (scale) | largest W1/sd (scale) | PQMass TV (scale) | classifier 2\|AUC − 0.5\| (scale) | members: PQMass TV; classifier |
|---|---|---|---|---|---|
| A_O3 | 0.029 m2_src (0.018) | 0.043 m2_src (0.020) | 0.045 (0.067) | 0.026 (0.024) | 0.046 to 0.051; 0.030 to 0.065 |
| A_O4 | 0.007 q (0.006) | 0.017 q (0.009) | 0.015 (0.017) | 0.002 (0.005) | 0.016 to 0.020; 0.016 to 0.022 |
| B_joint | 0.011 m2_src (0.007) | 0.018 q (0.006) | 0.023 (0.024) | 0.008 (0.001) | 0.022 to 0.027; 0.015 to 0.027 |
| P_control | 0.009 ra (0.003) | 0.018 z (0.007) | 0.013 (0.017) | 0.016 (0.005) | 0.013 to 0.013; 0.016 to 0.016 |

V2, the per-bin ratios:

| flow model | V2 bins off by more than 3%: against test | largest \|r − 1\| | against train | largest \|r − 1\| |
|---|---|---|---|---|
| A_O3 | 67 of 120 | 0.185 | 17 of 120 | 0.131 |
| A_O4 | 13 of 122 | 0.063 | 1 of 122 | 0.033 |
| B_joint | 30 of 122 | 0.105 | 3 of 122 | 0.086 |
| P_control | 13 of 122 | 0.195 | 7 of 122 | 0.160 |

U0 (100 Poisson bootstraps of the real rows, the real Monte Carlo's own shape noise): S_W[50, 90] rms 1.1e-03, largest
3.1e-03. Beside it, model A's ensemble S_W[50, 90] is 9.3e-4 and its single members 8.0e-4 to 4.0e-3.

**Reading.** The ensembles meet the shape bar (U1) but not the accuracy checks: model A's O3 flows keep 0.945 to 0.960
of ξ under the clip and B's members 0.994 to 0.996, against 0.995 (X1); the μ ratios miss by up to 1.3% (A) and 1.1%
(B) against 1% (X2); and the members' shapes scatter by 1.8 (A) and 2.1 (B) times the declared 1.5e-3 (U2). Every D4
number in 12AN is therefore labelled systematic, as declared, and the D4 product is model A's.
