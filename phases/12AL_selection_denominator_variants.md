# 12AL — The host density in the selection term: variants D1 to D3 at fixed calibration

## Status

**DECLARED (2026-10-19), before any 12AL job or likelihood.** This record fixes the variants, cells, grid,
metrics, readings, controls and compute before anything runs. Nothing has run. The only things read for it are
core's source, the consumer code, and catalog metadata: shapes, occupied-row counts and galaxy weights.

**BUILT (2026-10-19), amendment B1 below.** The code is written and tested, and two short GPU controls passed. No
production job has run.

**Blinding: location-free**, as in 12AG to 12AJ. No H0 location appears here, in commit messages or in any summary.
The only H0 values in this record are fixed a priori:
- the coarse grid [20, 140] at step 0.5;
- the fine window [50, 100] at step 0.1;
- the reference point 75;
- the five control points 50, 62.5, 75, 87.5 and 100 (12AJ's);
- core's constant 67.74 (`KERNEL_PIN_H0_REF`), at which the H0-invariant catalog tables are built.

Files holding absolute log-likelihoods are written by jobs and are not for agents to open.

**Experimental.** As everything in 12AG to 12AJ, this is a measurement, kept as a record. Adopting any variant as a
core option would be a core PR, and that is the owner's call.

## Why

The owner proposed (record 12AI, amendment 1): "not use pcat(z) in the denominator term where the injections are
evaluated and approximate this by the pvol term". The approved plan:
1. measure first (12AJ, a bootstrap, running in parallel);
2. then the selection-term variants D1 to D3 (this record);
3. then D4, a p_det surrogate (12AK, separate).

At the production cell (nside 64, sigma_kde 3e-3) the selection Monte-Carlo variance is 0.74. Of that, 0.69 is the
floor, the same as spectral only, and 0.05 comes from the catalog. The catalog's share grows with resolution:
about 0.2 at (128, 1e-3) and 1.5 at (128, 1e-4). The variants change only the host density at which the injections
are weighted. The PE numerator is untouched.

## How core builds the selection term (core e7c3007, consumer 9827e3c)

### The chain, with file and line

Core paths are under `src/darksirens/` at e7c3007. Consumer paths are at 9827e3c.

| Step | Where | What |
|---|---|---|
| Injection pixel | consumer `phase12/desi_selection.py:1049` | global RING pixel at the catalog's nside, from (ra, dec) |
| Compact view | `desi_selection.py:1050`, core `catalog/compact.py:78` | rows = union of the pixels hit by any PE sample or injection; nside 64: all 49,152; nside 128: 196,577 of 196,608 (12AJ) |
| Row per injection | `desi_selection.py:1098` | `gw_selection.pixels` = compact row r_i |
| Per proposal | `desi_selection.py:1212-1290` | curves (`:1244`), field state (`:1252`), one `prepared` state passed as both `pe_state` and `selection_state` (`:1260-1272`) |
| Model routing | core `likelihood/host_density.py:114-122` | PE and selection closures call the same `log_density`, with `pe_state` and `selection_state` respectively |
| Weight | `likelihood/hierarchical.py:332-357`, `likelihood/weights.py:112-165, 295` | log w_i = log p_pop(m1src, q, z, chi_eff) + log n(z_i, r_i) − log J(z→dL) − log prior_wt_i, with z_i = z(dL_i; H0, Om0, w0, wa) and dL clipped to the table |
| Selection sum | `selection/gw.py:474-607`, `:130-206` | ln mu = logsumexp(log w) − ln N_draw; 1/N_eff = Σw²/(Σw)² − 1/N_draw |
| Correction | `selection/gw.py:270-412` | −N ln mu + N(N+3)/(2 N_eff), plus the soft-guard wall (zero here) |
| Total | `likelihood/hierarchical.py:403-431` | ln L = correction + Σ_i ln Ẑ_i |

### The host density at one injection

`eval_field_incomplete_catalog_prior_state` (`catalog/field.py:300-314`) returns the conditional value
(`catalog/models.py:207-236`) plus `log_row_mass`. `log_row_mass` is the row normaliser `log_Z`
(`field.py:283-288`), so the field value is the unnormalised numerator:

n_f(z, r) = N_obs,r · p_cat(z | r) + dN_miss(z, r).

**Catalog term.** For each galaxy k of row r:
- p_cat(z | r) = g(z) Σ_k kw_rk N(z; z_rk, σ_rk) for z ≤ z_depth, and zero above (`catalog/redshift.py:1378-1413`);
- σ_rk = max(sqrt(dz_rk² + sigma_kde²), 1e-4) (`redshift.py:307-309`);
- the weights are normalised per row (w/Σw), divided by Z_k = ∫ g K_k dz, then renormalised below the depth
  (`redshift.py:310-331, 265-292`);
- N_obs,r = ngals_r × (the pre-renormalisation mass below the depth) (`models.py:140-142`).

With unit galaxy weights (true in both catalogs; checked on the metadata), the catalog term is a sum over the row's
galaxies of each galaxy's own unit-mass, g-tilted kernel, truncated at the depth and not renormalised:

N_obs,r p_cat(z | r) = Σ_{k∈r} g(z) K_k(z) / Z_k · 1[z ≤ z_depth].

**Completion term.** On core's log z grid (1000 nodes to z = 5; `cosmology/_grid.py:14-17`), linearly interpolated
(`models.py:217-229`):
- dN_miss(z, r) = [1 − f_r C̄(z)] dN_exp(z) for z ≤ z_depth, and dN_exp(z) above
  (`selection/footprint.py:60-118`, in particular `:99-104`);
- dN_exp = n0 · a_pix · g(z), with g = dV_c/dz (1+z)^delta (`catalog/completeness.py:228-229`,
  `catalog/redshift.py:110-125`);
- C̄(z) = Φ[(m_lim − M0 − μ(z) − K(z)) / sigma_M], with M0 = M0hat + 5 log10(H0/H0_REF)
  (`selection/catalog.py:205-208, 223-241`);
- f_r is the footprint fraction of the row's pixel.

**Shape of the data per injection.**

| Item | Value |
|---|---|
| Sky | compact row r_i: one HEALPix pixel at the cell's nside (RING) |
| Redshift | z_i(H0) from the injection's dL; the only place H0 enters the density |
| Catalog kernel | the row's galaxies, up to 1,719 slots at nside 64 and 774 at 128, Gaussian widths σ_rk |
| Depth | catalog term zero above z_depth = 0.245; the completion becomes dN_exp there |
| Completion | dN_miss[r, ·] on 1000 log-spaced nodes, f_r from the footprint map at the cell's nside |

The catalogs hold 22,785,279 galaxies at both nsides: 30,411 occupied pixels at 64 and 119,524 at 128.

### The field normaliser: where it enters, and a correction

**Where Z_f enters: nowhere in core.** `catalog/field.py:12-17` states it. The survey-global normalisation is
omitted, because it is common to the PE and selection samples at fixed hyperparameters and cancels exactly between
the N event evidences and −N ln mu. Written out:

ln L = Σ_i ln(Ẑ_i / Z_f) − N ln(μ̂ / Z_f) = Σ_i ln Ẑ_i − N ln μ̂,

with Z_f = Σ_p ∫ n_f(z, p) dz = Σ_p (N_obs,p + N_miss,p) = Σ_p exp(log_row_mass_p) over every sky pixel
(`models.py:143-144`; N_miss is the trapezoid over the grid to z = 5).

**Correction: in this configuration Z_f does not depend on H0.** The brief and 12AI's amendment 1 say it does. It
does not here, because every piece of n_f(z, p) is H0-invariant as a function of z:
- **Catalog term.** With Om0, w0, wa, delta and sigma_kde fixed, g(z; H0) = (H0_ref/H0)³ g(z; H0_ref) and
  Z_k ∝ (H0_ref/H0)³. The ratio g K_k / Z_k does not move, and neither does the depth mass. This is the kernel-pin
  premise (`redshift.py:609-625`).
- **dN_exp.** n0_units is "h_scaled" in the configuration (`config/desi.fixed_population.json:24`), so
  n0 = 10^log10n0 (H0/100)³ (`desi_selection.py:736-737`, core `catalog/types.py:18-30`). Then n0 g(z) is
  H0-invariant.
- **C̄.** M0 + μ(z) = M0hat + 5 log10(H0/H0_REF) + 5 log10(dL × 1e5), and dL ∝ 1/H0, so C̄(z) is H0-invariant.
- **The depth** is fixed in z, and so are f_p and a_pix.

So n_f(z, p) is one fixed function of (z, p). Z_f is a constant. H0 enters the selection term only through
z_i(H0), the Jacobian and the population. Control 5 checks this numerically.

**What this means for 12AH's amendment A2.** A2 noted that core's numerator omits a survey-wide, H0-dependent factor
g(H0). Its example was a common h³. That concerns how the curvature splits between the event evidences and the
selection term, for a convention in which such a factor exists. It never changes ln L. With physical n0 units, or a
sampled Om0, delta or sigma_kde, the factor would be real and H0-dependent. In this configuration it is a constant.

**For the variants: replace the density, keep the normaliser.** Each variant D replaces n_f only in the selection
term. The proper normaliser of its density is Z_D = Σ_p ∫ n_D dz.
- **D2 and D3** preserve Σ_p n_D(z, p) = Σ_p n_f(z, p) at every z (below), so Z_D = Z_f identically. Keeping Z_f is
  then exact, with no convention choice.
- **D1** has Z_D1 = N_pix ∫ dN_exp dz. Here Z_f / Z_D1 is an H0-independent number, since both densities are
  H0-free. Normalising D1 by its own total or by Z_f changes ln L by a constant only. Every posterior and every
  reference-removed metric below is the same either way. ln(Z_f / Z_D1) is reported as a diagnostic: it contains no
  H0.

## The variants (fixed now)

**Common to all.** At every H0,

ln μ_D = ln[(1/N_draw) Σ_i b_i(H0) n_D(z_i(H0), i)],

where b_i is the density-free part of core's weight: population, Jacobian and 1/prior_wt. This part is identical
for every variant. Then

ln L_D = Σ_i ln Ẑ_i(D0) − N ln μ_D + N(N+3)/(2 N_eff,D) (+ core's wall, expected zero).

The PE evidences Ẑ_i and their variances σ_i² are D0's at the same H0. The correction is core's
`selection_log_correction`, evaluated in x64 with D0's pe_variance_sum.

| Variant | Selection density n_D(z, i) | Assumption | Sky cells |
|---|---|---|---|
| **D0** (current) | n_f(z, r_i) | none (the production density) | every pixel |
| **D1** (owner's p_vol) | dN_exp(z) = n0 a_pix g(z) | the field density is the smooth model everywhere | 0 |
| **D2** | n̄(z) = (1/N_pix) Σ_{p=0}^{N_pix−1} n_f(z, p) | p_det isotropic | 1 |
| **D3r** | the mean of n_f over the native iso-latitude ring of the injection's pixel | p_det depends on declination only | 4 nside − 1 (255 or 511) |
| **D3a** | (1/m) Σ_{p∈P_i} n_f(z, p), with P_i the injection's nside-8 pixel, m = (nside/8)² | p_det constant within 7.3° cells | 768 |
| **D3b** | the same at nside 16, m = (nside/16)² | p_det constant within 3.7° cells | 3,072 |

**D3r is added here.** It uses the same machinery at no extra cost. A ground network's sidereal-averaged p_det depends
on declination but not on right ascension, and the DESI footprint is concentrated in the north. So D3r keeps the
footprint's declination structure, and isolates the one anisotropy expected to matter.

**Closed forms, using the expressions above.** Below the depth:
- n̄(z) = dN_exp(z) [1 − f̄ C̄(z)] + S(z) / N_pix;
- n_D3(z, P) = dN_exp(z) [1 − f̄_P C̄(z)] + S_P(z) / m.

Above the depth every variant equals dN_exp(z), which is D0's value there. Here:
- f̄ is the mean of f_p over all N_pix sky pixels of the global map, not the compact view;
- f̄_P is the mean over the cell's pixels (ring or coarse pixel);
- S_P(z) = Σ_{p∈P} N_obs,p p_cat(z | p), the catalog term summed over every occupied pixel of the global catalog in
  the cell. S is the same sum over all pixels. With unit weights, S_P is the sum over the cell's galaxies of their
  unit-mass kernels.

The injection's coarse pixel comes from its (ra, dec) at nside 8 or 16. It is the parent of its fine pixel. The ring
is the iso-latitude ring of its native RING pixel (healpy 1.19.0 in the consumer env).

**What D1 drops in addition, compared with D2:**
1. the catalog's footprint-averaged dN/dz structure: large-scale structure along the line of sight, and the
   photometric-redshift smearing (73% of galaxies, median ZERR 0.032);
2. any mismatch between the catalog's counts and n0 f̄ C̄(z), the completeness calibration;
3. the depth edge: the catalog term truncated at 0.245 with renormalised kernels below it, and the completion
   switching to dN_exp above;
4. all sky structure: footprint, coverage and depth.

D1 is exact only if n̄(z) = dN_exp(z) at every z. Metric 7 measures their ratio.

**D1 is the spectral-only selection density, up to a constant.** Core's spectral redshift prior is normalised dV_c/dz
(`cosmology/volume.py:16-30`, `likelihood/hierarchical.py:144-145`). With delta 0 and h-scaled n0, dN_exp is a fixed
multiple of it. So D1's N_eff is spectral only's, and D1 is exactly "catalog numerator, spectral denominator", up to an
H0-independent constant. Control 4 checks this.

### Algebra

**(i) Normalisation.** For D2, D3r, D3a and D3b, the cells partition the sky, each cell's value is the mean over its
pixels, and every pixel of a cell carries that mean. So Σ_p n_D(z, p) = Σ_p n_f(z, p) at every z, and Z_D = Z_f.

**(ii) D2 = D0 when every pixel has the same density.** If n_f(z, p) = n(z) for all p, then n̄ = n. Every term
b_i n_D2(z_i) equals the term b_i n_f(z_i, r_i). So μ̂_D2 = μ̂_D0 and N_eff,D2 = N_eff,D0, injection by injection, for
any injection set. A sky-uniform catalog (the same galaxies and the same f_p in every pixel) is such a case.
Conversely, if D2 equals D0 term by term for every injection, then n_f(z, p) = n̄(z) wherever an injection falls.

**(iii) Expectation, and when D2 or D3 is unbiased.** Write the detected injections' expectation as
∫ dθ q(θ) ⟨P_det(θ, Ω) n(z, Ω)⟩_Ω, where q collects the population over the draw and the injection sky draw is
isotropic. Then:
- ⟨P_det n_D2⟩ = ⟨P_det⟩ n̄;
- ⟨P_det n_f⟩ = ⟨P_det⟩ n̄ + Cov_Ω(P_det, n_f).

So E[μ̂_D0] − E[μ̂_D2] = ∫ dθ q Cov_Ω(P_det(θ, ·), n_f(z, ·)). This is zero when P_det is isotropic, or when it is
uncorrelated with the catalog's sky structure at each z.
- **D3:** the covariance is taken within each cell, Σ_P (A_P / 4π) Cov_{Ω∈P}. It is zero when P_det is constant
  within cells.
- **D3r:** it is zero when P_det depends on declination only.

**(iv) Variance.** Under (iii)'s condition, n_D2(z_i) is the conditional expectation of n_f(z_i, Ω_i) over the
injection's sky position. D2 is then the Rao-Blackwellised D0, and its variance is no larger. D3 is a partial
Rao-Blackwellisation. When the condition fails, the variance can still fall, but D2 or D3 then carries a bias. Metric
4 and reading 1 test for that bias at D0's noise level.

### Implementation (declared now; the code is stage 2)

**Tables.** The catalog parts S_P(z) are H0-invariant (above). They are tabulated once per cell:
- on the uniform grid z_j = j × 1e-5, j = 0 … 24,500, ending exactly at z_depth = 0.245;
- with core's own evaluator: `eval_log_catalog_prior_state` plus `log_Nobs`, from the cell's kernel state at
  core's `KERNEL_PIN_H0_REF` = 67.74;
- over every occupied row of the **global** catalog, accumulated into each variant's cells;
- interpolated linearly in z, and zero above the depth (core's truncation).

The linear-interpolation error for a Gaussian of width σ ≥ 1e-3 at this spacing is at most (1e-5/σ)²/8 ≈ 1.3e-5
relative (controls 3 and 7). The completion part is core's `selection_completion_curves_with_row_fraction` with
row_fraction = f̄_P per cell, on core's grid with core's interpolation. So the completion arithmetic is D0's.

**Selection-only evaluation.** Each variant's ln μ and N_eff come from a call to core's
`host_density_log_likelihood` with three changes:
- the selection density is the variant's, its tables being jit arguments, never closure constants (the nside-16
  table is about 600 MB);
- the PE operand is a stub, the first row of each of the 259 events (nsamp 1). Its evidences are discarded, and the
  diagnostics' ln μ and N_eff do not depend on it;
- everything else is the stock target's (`phase12t_common.build_target`, 12AG's settings).

**The scoped wrapper.** `patched_selection_density(variant)` is the inverse of 12AH's `patched_host_density`. It
replaces `darksirens.likelihood.host_density.host_density_log_likelihood` while a target is built. It routes the
**selection** state to the variant density and leaves the PE side on the production density. It:
- refuses a nested install (`RuntimeError`);
- restores the module attribute on exit, also after an exception;
- marks the wrapped function with its variant;
- has an identity mode, which routes the selection side to the production field evaluator.

## Cells (fixed now)

| Cell | nside | sigma_kde | Role | catalog (sha256 prefix) |
|---|---|---|---|---|
| production | 64 | 3e-3 | the production setting | c2d1ff36567419e4 |
| partner | 128 | 3e-3 | the resolution pair at 3e-3 | f26a20f0f3f8ca5a |
| fine | 128 | 1e-3 | catalog-added selection variance large (about 0.2) | f26a20f0f3f8ca5a |
| fine partner | 64 | 1e-3 | completes the 64-vs-128 pair at 1e-3 (added: about one card-hour) | c2d1ff36567419e4 |

**Every cell** uses the same six densities (D0, D1, D2, D3r, D3a and D3b) and 12AG's ladder setting:
- calibration log10 n0 −1.8216 (h-scaled), M0hat −20.4975, sigma_M 0.5592, delta 0, z_depth 0.245, m_lim 21,
  the production k-correction;
- the population fixed as in the spectral-only reference; Om0 0.3089, w0 −1, wa 0;
- the selection guard soft with variance limit 20; `core_numerics=core_defaults`, `kernel_pin=off`;
- the footprint at the cell's nside: native at 128, degraded equal-area at 64, from
  `phase12t/inputs/mth_map_nside128.h5` (1e4e5c675dd59ab2);
- PE: `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` (259 × 4096);
- injections: 12AG's O3/O4 file (1,067,946 detected of 944,412,448 drawn);
- core e7c3007 in float64, as `phase12ah_a_plan.scan_argv` builds them.

## Grid (fixed now)

- **Coarse:** [20, 140] at step 0.5, 241 points, built as lo + step × arange.
- **Fine window:** [50, 100] at step 0.1, 501 points, built the same way.
- **In all:** 641 distinct points. The 101 shared points have identical floats.

**Posteriors** use a flat prior on the fine window, normalised there, as in 12AJ. The coarse grid checks that each
variant's posterior stays inside the window: the mass outside must be ≤ 1e-3, or it is reported. It is also used for
the full-range variance figures.

Lane A, the stock D0 grid with every event's evidence, uses `phase12ah_a_scan.py` unchanged. The variants are
evaluated on all 641 points with the nominal injections, and on the window for every replicate.

## Monte-Carlo noise: 12AJ's injection replicates, paired (fixed now)

**The replicates.** The noise of every D-vs-D0 comparison comes from 12AJ's 14 injection-only resamples:
- seeds 2201–2214, idx = sort(rng.integers(0, 1067946, 1067946)), with PCG64;
- read from `lnl_convergence/replicates/inj_bNN.h5` when present, with sha256 checked against 12AJ's manifest;
- otherwise regenerated in memory from the same scheme, which gives the same indices. The summary says which.

On each replicate, D0 and every variant are evaluated selection-only on the window, on the nominal compact view, as
in 12AJ. The PE never changes, so PE noise cancels in every D-vs-D0 difference. **Noise source, stated as required:
12AJ's bootstrap (injection mode), paired.** Core's analytic per-point variances are reported beside it.

**Fallback.** If the replicate stage fails at a cell, the noise there comes from the variants' own variance
estimates: sqrt(V_sel,D + V_sel,D0) per point, which ignores their positive correlation and so overstates the
noise. The summary marks such readings.

## Metrics (fixed now; every reported number location-free)

**Notation:** per cell, variant D, window W, N = 259, H_ref = 75.
- Δ_D(H) = N[ln μ_D(H) − ln μ_D0(H)];
- ℓ_D(H) = ln L_D(H) − ln L_D0(H) = −Δ_D + (N(N+3)/2)(1/N_eff,D − 1/N_eff,D0);
- p_X is the window posterior of X;
- I90_X is its central 90% interval. It is used inside jobs only and never printed.

1. **Selection Monte-Carlo variance.** V_sel,D(H) = N²/N_eff,D(H), core's estimator. Reported per variant:
   - the maximum over I90_D0 and over I90_D;
   - the p_D0-weighted mean;
   - its ratio to D0's.

   The per-point values go only to `absolute.npz`.
2. **Total ln L variance (the owner's criterion).** V_tot,D(H) = Σ_i σ_i²(H) + V_sel,D(H), with D0's σ_i². Reported:
   the maximum over I90_D0 and over I90_D, and whether each passes 12AI's N1 (≤ 1.2).
3. **The H0 dependence of N Δ ln μ over W.** Constants never matter, so every number here is free of them. Here
   u = (H − 75)/10.
   - **A_D** = max over W of |Δ_D(H) − Δ_D(75)|, the largest excursion from the reference. Also ptp_W Δ_D, which is
     the range with or without the reference removed.
   - **B_D** = the ptp of Δ_D's residual after the least-squares line over W (the linearly detrended range).
   - **q_D** = twice the quadratic coefficient of the least-squares quadratic in u, in nats per (10 km/s/Mpc)².
   - **S_D** = ∫_W p_D0 (Δ_D − ⟨Δ_D⟩)² dH, the part that can move the posterior (H² ≈ S/8, 12AJ).
   - The same four for ℓ_D, which adds core's 1/N_eff term.
4. **The noise of metric 3.** Over the replicates k = 1 … 14, ε_k = Δ_D,k − Δ_D,nom:
   - ν_A = rms_k max_W |ε_k(H) − ε_k(75)|;
   - ν_B = rms_k B[ε_k];
   - s_ε = mean_k S[ε_k];
   - z_A = A_D/ν_A, z_B = B_D/ν_B, r_S = S_D/s_ε.

   **Also, the bootstrap variance of each variant itself:** the injection-mode shape variance S_inj,D of 12AJ, with
   e_k = δ_k − mean_k δ_k under p_D, against D0's.
5. **Posterior against D0.**
   - R = (68% half-width of D)/(that of D0);
   - the sd ratio;
   - Delta = (median_D − median_D0)/sd_spec, in spectral-only sd, from the spectral window grid computed in the same
     lane;
   - the Hellinger distance H(p_D, p_D0).

   **Noise floor:** H_floor,D = rms_k H(p_D0, p_D0 · exp(−ε^ℓ_k)), renormalised, with ε^ℓ_k the replicate error of
   ℓ_D. **Context:** each variant's R, Delta and Hellinger from spectral only, as in 12AI.
6. **nside 64 against 128, under each variant,** at 3e-3 and at 1e-3:
   - H_D(64,128), against H_D0(64,128);
   - G_D = ptp_W of N[ln μ_D(128) − ln μ_D(64)], the selection-side difference;
   - the paired injection-mode floor of the 64-vs-128 difference per variant, as 12AJ's metric 4 in injection mode.
     12AJ's PE-mode floor is quoted from its location-free summary when available.
7. **The D1 diagnostic (H0-free tables).**
   - ρ(z) = n̄(z)/dN_exp(z), averaged in bins of width 0.005 over [0, 0.245] (49 bins), split into the completion
     part 1 − f̄ C̄(z) and the catalog part S(z)/(N_pix dN_exp);
   - the below-depth ratio ∫_0^0.245 n̄ / ∫_0^0.245 dN_exp;
   - ln(Z_f / Z_D1);
   - **Anisotropy, alongside:** the coefficient of variation across D3b cells of n_D3b(z, P)/n̄(z), by the same z
     bins.

## Readings (fixed now)

1. **Consistent with D0 (per cell).** The multiple is 2 noise units.
   - "consistent" if z_B ≤ 2 **and** H(p_D, p_D0) ≤ 2 H_floor,D;
   - "inconsistent" if z_B > 3 **or** H(p_D, p_D0) > 3 H_floor,D;
   - "marginal" otherwise.

   z_A and r_S are reported and do not decide. "Consistent" means "no bias detectable at D0's own noise level", not
   "unbiased".
2. **Reduces variance (per cell).** Let V90_X = max over I90_D0 of V_sel,X, and a = V90_D0 − V90_D1, the
   catalog-added part (D1 is the floor, control 4).
   - If a < 0.02, the cell reads "no catalog-added selection variance to remove", and every variant is "n/a" there.
   - Otherwise D "reduces variance" if V90_D ≤ V90_D0 − 0.5 a, removing at least half of the catalog-added part.
   - Reported: φ_D = (V90_D0 − V90_D)/a, and S_inj,D against S_inj,D0 as a check.
3. **Recommendation (points only).** The order of simplicity, by sky cells, is D1, D2, D3r, D3a, D3b. The
   recommendation is the first variant that:
   - reads "consistent" at every cell;
   - reads "reduces variance" at every cell where a ≥ 0.02.

   Otherwise it is "none". The per-cell version is reported too. Adopting it as a core option is a core PR and the
   owner's call.
4. **Resolution (per variant, at 3e-3 and 1e-3).**
   - "the 64-vs-128 difference shrinks" if H_D(64,128) ≤ 0.75 H_D0(64,128) and the drop exceeds twice the
     injection-mode floor of the difference;
   - "grows" if H_D(64,128) ≥ 1.25 H_D0(64,128);
   - "unchanged" otherwise.

   **How to read it, declared now:** under D1, D2, D3a and D3b the selection term is the same at both nsides up to a
   constant (control 6). So H_D(64,128) is the PE side's resolution effect. The drop from H_D0(64,128) indicates the
   selection side's share. Hellinger distances do not add, so this is an indication, not a decomposition.
5. **Isotropy (supplemental, decides nothing).**
   - D2 inconsistent while D3r is consistent: p_det's declination dependence is the likely cause.
   - D3r also inconsistent while D3b is consistent: structure in right ascension matters. That is not expected for a
     sidereal-averaged network, and would be reported as an open question.

## Controls (fixed now)

1. **Wrapper identity, bit for bit (every cell, the five control points).**
   - **(a)** The stock target built under `patched_selection_density` in identity mode equals the unpatched stock
     target in ln L, the 259 ln Ẑ_i and σ_i², ln μ and N_eff.
   - **(b)** The selection-only path (PE stub) in identity mode equals (a) in ln μ and N_eff. If it differs only at
     rounding (|Δ ln μ| ≤ 1e-12 and |ΔN_eff/N_eff| ≤ 1e-12), this is recorded and the stage proceeds. Anything
     larger stops the stage.
   - **(c)** CPU tests: a nested install raises; the attribute is restored on normal exit and after an exception; a
     target built under the wrapper carries its variant mark.
2. **D2 = D0 on a synthetic catalog with identical pixels (HENON, x64).**
   - **The catalog:** every one of the 49,152 rows holds the same galaxies, those of the first occupied row in RING
     order whose count equals the median (752). f_p = f̄ in every pixel.
   - **The test:** for the first 100,000 injections at the five points, |ln n_D2 − ln n_f| ≤ 1e-4 below the depth and
     exactly 0 above it. The same for D3r, D3a and D3b. By algebra (ii), |ln μ_D2 − ln μ_D0| over those injections
     ≤ 1e-4.
3. **D3 at the native nside equals D0** (GPU, every cell, the five points, all injections). The cells are the
   native pixels.
   - per injection: max |Δ ln n| ≤ 1e-4 below the depth, and 0 above;
   - N |ln μ_table − ln μ_D0| ≤ 1e-3 nat.
4. **D1 is spectral only up to a constant.**
   - ptp over W of N[ln μ_D1 − ln μ_spec] ≤ 0.01 nat;
   - |N_eff,D1/N_eff,spec − 1| ≤ 1e-4, at every grid point.

   Differences come only from interpolating dV_c/dz on two grids.
5. **Z_f does not depend on H0 (HENON, x64).** Σ_p exp(log_row_mass_p) over the global catalog at each cell's
   configuration at H0 = 50, 75 and 100, and n_f at 1,000 fixed (z, p) pairs: maximum relative difference ≤ 1e-10.
   **If this fails,** the normalisation section is amended before any GPU job.
6. **64 against 128 under D1, D2, D3a and D3b:** G_D ≤ 1e-6 nat at each sigma_kde. This rests on:
   - unit galaxy weights, checked and recorded per catalog;
   - the nside-64 coverage being the equal-area mean of the 128 map, checked.

   **A failure** is reported and explained, and reading 4's interpretation is withheld.
7. **Table accuracy.** For 10,000 random (z, cell) pairs per variant and cell (seeds 3101 onward, one per
   cell × variant), the linear interpolant is compared with core's exact sum. The maximum relative error must be
   ≤ 1e-4 wherever the value exceeds 1e-8 of the cell's maximum.
8. **Kernel H0 invariance.** Tables for 64 fixed probe rows built at H0 = 50, 67.74 and 100 agree to 1e-10 relative.
9. **Replicates.**
   - When 12AJ's injection files exist, the in-memory resample equals them: the sha256 of every dataset after
     resampling matches.
   - When 12AJ's injection-mode grids exist, D0's replicate ℓ errors equal 12AJ's δ_k to 1e-9 at the five points.
   - Otherwise this is reported as not available.
10. **Per-event sum, x64, guard, code.**
    - Σ ln Ẑ_i + core's correction = ln L to 1e-9 on every Lane-A point.
    - Every process records x64 on and refuses to run otherwise.
    - Every variant point has a zero wall and V_tot ≤ 20.
    - Every job runs from a worktree of a committed sha with a clean tree.

**If a control fails:** a failure of control 1, 3, 5, 7, 8 or 10 withholds every reading. A failure of 2, 4, 6 or 9
is reported, and the affected readings are marked. The summary always writes its numbers and `STATUS.json`.

## Compute (estimate)

**Measured speeds (12AJ, rita):**
- 0.265 s per full point (PE and selection) at both nsides;
- start, load, build and first point about 120 s at nside 64 and 180 s at 128.

The selection-only D0 is about half a point: 0.13 s. The variants' selection, by table lookup with no kernel sum, is
not yet measured. It is taken as 0.05 s per point, with a range of 0.02 to 0.1.

**One process per cell (one A100-80):**

| Step | nside 64 | nside 128 |
|---|---|---|
| build, compile, Lane A (641 points with per-event evidence), spectral grid | about 8 min | about 9 min |
| control 1(a), wrapped rebuild and 5 points | about 3 min | about 4 min |
| tables: about 1.3e12 (64) and 2.3e12 (128) kernel terms, including the native table for control 3 | ≤ 5 min | ≤ 8 min |
| controls 1(b), 3, 7 and 8 | about 4 min | about 5 min |
| variants, nominal: 5 × (compile + 641 points) | about 9 min | about 9 min |
| replicates: D0 selection-only, 14 × 501 points | about 17 min | about 17 min |
| replicates: 5 variants × 14 × 501 points | about 29 min (12 to 59) | about 29 min |
| **total** | **about 75 min** | **about 80 min** |

**Jobs:**
- **Four GPU jobs, one per cell,** two at a time, on rita0 and rita1:
  -p RITA-GPU --qos rita -A phy220048p --gres=gpu:a100-80:1 --cpus-per-task=128 --mem=120G --time=7-00:00:00.
  The nside-128 cells need about 25 GB for the target plus about 23 GB for the native table of control 3.
- **HENON CPU, before the GPU jobs:** controls 1(c), 2, 5 and 8 (x64), under 10 min. These are waited on with a
  Bash until-loop, each call under 10 minutes.
- **HENON CPU, the summary:** afterany on the four GPU jobs, about 15 min. It always writes `summary/STATUS.json`.
- HENON flags: -p HENON --qos henon -A phy220048p --time=7-00:00:00 --exclude=henon06,henon08.
- **Not used:** MIKO, js2h100, twig or henon-gpu.

**Estimated total to the summary:**
- about 3 hours from when both rita cards start on 12AL: about 2.6 h of GPU per card, plus the CPU controls before
  and the summary after;
- range 2 to 4 hours, set by the unmeasured variant speed;
- **queueing:** 12AJ (about 78 min on both rita cards) and 12AK queue there too. Their remaining time adds to this.

## Code (stage 2; nothing written yet)

Consumer branch `phase12al/selection-denominators`, from 9827e3c, worktree `phase12_5/repo_12AL`:
- `scripts/phase12al_common.py`:
  - the variant definitions;
  - the tables;
  - `patched_selection_density`;
  - the variant selection model;
  - the PE stub;
  - metrics 3 to 7;
- `scripts/phase12al_cell.py`: one process per cell, in this order:
  - Lane A through `phase12ah_a_scan`'s per-event record;
  - the tables;
  - controls 1(a), 1(b), 3, 7 and 8;
  - the variants, nominal;
  - the replicates;
- `scripts/phase12al_cpu_controls.py`: controls 2, 5 and 8;
- `scripts/phase12al_plan.py`, `scripts/phase12al_summary.py`;
- `slurm/phase12al_*`;
- `tests/test_phase12al.py`, including control 1(c).

Every job runs from `selection_denominators/worktrees/<sha>/`.

## Outputs

Under `phase12_5/selection_denominators/`:
- `runs/<cell>/`:
  - `lane_a/` (scan.json and events.npz), `variants.npz` (ln μ and N_eff per density, point and replicate) and
    `spectral/`. These hold absolute values and are not for agents.
  - `tables/`: the H0-free catalog and coverage tables.
  - `controls.json`: location-free.
- `summary/`:
  - location-free: `summary.json`, `controls.json` and `STATUS.json`;
  - `absolute.npz`: not for agents.
- `plans/`, `logs/` and `worktrees/`.

## Known limits

- **K = 14.** A single variance from 14 replicates is uncertain by about ±40% (68%). The readings are about factors.
- **Power.** The bias test (reading 1) has only the power of D0's own noise. A bias smaller than that is not seen.
- **No independent p_det.** The anisotropy of p_det enters only through the detected injections. A model of it is
  D4's (12AK).
- **One calibration, the population fixed.** The H0 invariance of n_f (control 5) holds for this configuration. A
  sampled Om0, delta or sigma_kde, or physical n0 units, would make n_f and Z_f depend on H0. The normalisation
  argument for D2 and D3 still holds then, but D1's ratio would not be constant.
- **Table interpolation.** It is a small systematic, bounded by controls 3 and 7 at ≤ 1e-4 per injection and ≤ 1e-3
  nat in N ln μ.

## Amendment B1 (2026-10-19): the build (stage 2), before any production job

### Commits

Consumer branch `phase12al/selection-denominators`, local only (not pushed), from 9827e3c:

| Commit | Content |
|---|---|
| `2f849d9` | the wrapper, the tables, the cell process, the plan, the lanes, the CPU tests |
| `4823cbf` | the multi-density call (B1.1), control 1(d), the CPU controls script, the summary |
| `447a072` | the CPU-control, summary and production submit scripts; the lanes' jax memory fraction; tests |
| `ecbcd83` | CPU tests of the cell's controls 7 and 8 and of the replicate operand |

Files: `scripts/phase12al_common.py`, `phase12al_cell.py`, `phase12al_cpu_controls.py`, `phase12al_plan.py`,
`phase12al_summary.py`; `slurm/phase12al_{worktree.sh,lane.sbatch,cpu_controls.sbatch,summary.sbatch,
submit.sh,submit_control.sh}`; `tests/test_phase12al.py`. The grid-driver option is `phase12al_cell.py
--selection-variant` (repeatable; default all of D1 to D3b). Jobs run from `selection_denominators/worktrees/<sha>`,
a detached worktree of a committed local sha, which must be clean.

### CPU tests: 15 passed

On tiny synthetic inputs (an nside-8 catalog, 12 events, 4,096 injections):
- **control 1(c):** a nested install raises; the attribute is restored on a normal exit and after an exception;
  the wrapped function carries `selection_variant`;
- **identity:** the target built under the wrapper equals the stock target bit for bit (ln L, ln mu, N_eff, the
  correction, every event's evidence and variance), and the selection-only path (PE stub) reproduces ln mu and
  N_eff;
- **D3 at the native nside and the native table equal D0** per injection (≤ 1e-4 below the depth, ≤ 1e-12 above)
  and in N ln mu (≤ 1e-3);
- **D2, D3r, D3a and D3b equal D0 on an identical-pixel catalog** (algebra (ii)); D1 does not;
- **the PE side is bit-identical** across all five variants;
- **normalisation:** every cell variant keeps Σ_p of the catalog term at every table node (relative 1e-12) and
  Σ_c m_c fbar_c = Σ_p f_p (algebra (i));
- **the multi-density call equals the single calls** (B1.1);
- **controls 7 and 8** through the cell's own functions; the replicate operand equals the target's map of the
  resampled rows;
- **the metrics on known curves** (a line has B = 0 and q = 0; a quadratic gives its q and B), the shape variance and
  Hellinger floor, every reading rule, the recommendation, the location-key and location-value guard, the grids
  (641 points, 101 shared floats), the sky cells, the plan;
- **the summary on synthetic cells:** it runs, is location-free, falls back without replicates, withholds every
  reading when a gating control fails, and always writes STATUS.json.

### Short GPU controls (rita, one A100-80; jobs 1390324 and 1390325)

Production cell (nside 64, sigma_kde 3e-3), at H0 = 50, 75 and 100 of 12AG's grid:
- **identity mode against 12AG's own grid** (`smearing_ladder/runs/ns64_sk3e-03/scan.json`): **bit for bit** in
  ln L, ln mu, N_eff, the correction and all 259 PE variances; theta identical;
- **D0 through the selection-only path** equals it bit for bit (control 1(b) needs no rounding allowance here);
- **the multi-density call** (D0 and D1 to D3b in one jit) equals the single calls for D0, D1 and D2 bit for bit;
- **D2** is finite and repeats bit for bit.

**Measured speeds** (these replace the assumed ones):

| Step | Measured |
|---|---|
| a selection-only point, D0 alone | 0.25 s |
| a selection-only point, one variant alone | 0.22 s |
| a selection-only point, all six densities together | 0.25 s |
| first call of each new trace (compile) | 72 to 82 s |
| the D2 table at nside 64 (1.3e12 kernel terms) | 9 s |
| all four cell tables at nside 64 | 8 s |
| the occupied view and its kernel state | 12 s |
| device peak (jax / nvidia-smi) | 18.5 GB / 21.3 GB |

The variant's own density lookup is cheap, but the density-free part of each injection weight (population, z(dL),
Jacobian over 1.07M injections) is not: 0.22 s, not the 0.05 s assumed.

### B1.1: one call per point for every density (departure: implementation and compute)

At 0.22 s per variant point, the declared plan of one call per density costs about 3.3 h per cell, most of it in
the replicates (14 × 501 × 6 calls). Instead, one jitted call traces one core `host_density_log_likelihood` per
density (D0, D1, D2, D3r, D3a, D3b), each with its own selection state. The density-free work is the same
expression on the same operands, and XLA computes it once: 0.25 s for all six.

Each density is still core's own reduction, unchanged. **Control 1(d)** is added to every cell: at the five control
points, the multi-density values equal single calls for D0, D1 and D2 to 1e-12 (bit for bit in the GPU control). A
failure of 1(d) withholds every reading, as a failure of control 1 does.

### B1.2: the table interpolant is log-linear (departure: implementation)

Between two table nodes the catalog term is read **log-linearly** where both nodes are positive, and linearly
otherwise (zeros). Reasons:
- core's own g(z) is log-linear between its grid nodes (`log_interp_zgrid`);
- a Gaussian tail is log-quadratic, so the log-linear error is about (h/σ)²/8 relative everywhere, tails included.
  A linear interpolant's relative error grows like u²(h/σ)²/8 into the tails.

**Below core's first grid node** (z ≈ 1.8e-3), core's g is the z² law. No two-point interpolant follows z² to 1e-4
for z below about 5e-4, because the error is about (h/z)²/4. So:
- **control 7** gates on z ≥ 1e-3 (`Z_GATE_LOW`); the pairs below are reported, not gated;
- **injections:** the smallest injection distance is 8.2 Mpc, so z ≥ 1.4e-3 at H0 = 50 (controls 2 and 3 are
  unaffected). At H0 = 20 a handful of injections reach z ≈ 5.5e-4, where the error is ≤ 1e-4 on their density.
  Their weight in mu is negligible.

### B1.3: smaller precisions of the controls (departure: tolerances and rules)

- **"Exactly 0 above the depth"** (controls 2 and 3) becomes **≤ 1e-12**. Core's field value is
  (x − log Z) + log Z, which rounds differently from x by an ulp.
- **Control 7** draws its cells among those holding at least one occupied pixel. An empty cell's exact value is 0
  at every z and would fall under the floor anyway.
- **Control 2**'s ln mu check uses the population-free sum Σ_i n_D / Σ_i n_f over the first 100,000 injections. The
  per-injection bound (≤ 1e-4) already bounds any positively weighted sum to the same 1e-4, so this adds nothing.
- **Control 9's file check** builds the operand from 12AJ's file (sha256 checked against 12AJ's manifest) and
  compares it with the in-memory resample, leaf by leaf, bit for bit. This is stronger than a dataset sha256. 12AJ's
  manifest already records each file's datasets equal to the original's at its indices.

### B1.4: the tables use every occupied pixel of the global catalog (as declared; one fact recorded)

At nside 128, 19 occupied pixels (3,206 galaxies) lie outside the target's compact view, because no PE sample or
injection falls in them. At nside 64 none do. The tables are therefore built from a separate view: core's compact
builder over all occupied pixels, with the target's own evaluation settings. These are the galaxy list and the
kernel window; at nside 64 the window holds all 1,719 slots of a row. This is the declared "every occupied row of the
global catalog".

### B1.5: jobs and memory (departure: scheduling only)

- **CPU controls before the GPU lanes:** the lanes are submitted `--dependency=afterok` on the CPU-controls job,
  instead of an agent waiting on it. If a CPU control fails, the lanes never start and are cancelled. Control 5
  failing still means amending the normalisation section first.
- **Memory:** the lanes set `XLA_PYTHON_CLIENT_MEM_FRACTION=0.92`, up from jax's default of 0.75, which caps it at
  about 60 GB on an A100-80. This makes room for the native table of control 3 (about 23 GB at nside 128). It changes
  no number.
- **Lane A** is `phase12ah_a_scan.py` unchanged, given the 641 union points with `--h0`.

### B1.6: compute (re-estimated from the measured speeds)

| Step | nside 64 | nside 128 |
|---|---|---|
| Lane A (start, 641 points at 0.265 s, scan.json rewrites) | about 9 min | about 10 min |
| cell: two builds, five compiles, controls 1, 1(d), 3, 7, 8 | about 13 min | about 15 min |
| spectral grid, 641 points | about 3 min | about 3 min |
| nominal, 641 points × 6 densities at 0.25 s | about 3 min | about 3 min |
| replicates, 14 × 501 points × 6 densities at 0.25 s | about 30 min | about 30 min |
| **total per cell** | **about 60 min** | **about 65 min** |

- **Per card:** two cells, about 2.1 h.
- **CPU controls before:** controls 2, 5 and 8 at full size on HENON (32 CPUs), estimated 20 to 60 min. These are
  CPU kernel sums: about 9e11 terms for control 2's synthetic tables, and 12 global kernel builds for control 5.
- **Summary after:** about 5 min.
- **Total to the summary:** about 3 hours once the CPU controls start and both rita cards are free (range 2.5 to 4
  h), plus queueing behind 12AK on rita and on a busy HENON.

**Readings and metrics are unchanged.** Nothing here changes a variant, a cell, the grid, a metric, a reading or a
tolerance, except B1.2's control-7 gate and B1.3.
