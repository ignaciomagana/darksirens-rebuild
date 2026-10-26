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

**RESULTS (2026-10-19, 20:48 UTC; location-free), at the end.** No reading is withheld. D2 (the sky-averaged
density) is the recommendation: it points only. Under D2 the catalog-added selection variance is mostly gone and
the catalog still does not narrow H0. Control 4 missed its tolerance narrowly at every cell, so, as declared, D1's
consistency and the variance readings are marked.

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

## Amendment B2 (2026-10-19): review fixes, before any production job

An adversarial review of this record (at b8af8f8) and its build (consumer ecbcd83) found one blocking defect and six
non-blocking ones. The physics of D1, D2 and D3 and the normaliser held up. All are fixed in consumer commit
`198046c` (from ecbcd83), before any production job. Variants, cells, grid, metrics and reading rules are unchanged;
B2.2 and B2.3 change a control's tolerance or rule.

### B2.1: controls 1(c) and 1(d) gate every reading (blocking defect)

- **Problem:** the summary gated only on CPU controls 5 and 8 and on the per-cell controls 1(a), 1(b), 3, 7, 8 and
  10. Control 1(d) (B1.1) was not copied into `controls.json`, and CPU control 1(c) was not gated, although
  "a failure of control 1 withholds every reading".
- **Fix:** CPU controls 1(c), 5 and 8 and per-cell controls 1(a), 1(b), 1(d), 3, 7, 8 and 10 now gate. Control 1(d)
  is copied into `controls.json`. A test fails only 1(d), and one fails only 1(c); each withholds every reading.

### B2.2: control 10's guard-penalty gate is a tolerance (departure: tolerance)

- **Problem:** control 10 required the guard penalty (the "wall") to be exactly 0 at all 641 points. Core's soft gate
  is exactly 0 only when N_eff exceeds about 4.7 times its threshold, that is V_sel ≲ 4.2 here. 12AG already shows a
  selection variance of 3.67 at the (128, 1e-3) cell, so a slightly noisier density at a coarse-grid end could
  carry a wall of about 1e-300 nat and withhold every reading.
- **Fix:** the gate is |wall| ≤ 1e-9 nat on the fine window [50, 100] and V_tot ≤ 20 at all 641 points. The
  maximum |wall| over the full grid and an exact-zero flag are reported beside it.

### B2.3: D0's ln L uses the variants' path, and its tie to Lane A gates (departure: rule)

- **Problem:** D0's ln L was Lane A's, while every variant and every replicate used the selection-only path's
  correction. Any difference between the two D0s would enter ℓ_D and its replicate errors as a fixed curve and
  inflate the Hellinger floor. The tie was computed but not gated (the GPU controls found it bit for bit, but only
  at three points).
- **Fix:** D0's ln L for every difference is Σ ln Ẑ_i + core's correction at D0's selection-only ln μ and N_eff.
  Control 10 now also requires D0's selection-only ln μ and N_eff to equal Lane A's to 1e-12 (absolute in ln μ,
  relative in N_eff) at all 641 points. Control 10's per-event sum check stays on Lane A.

### B2.4: controls 2, 4, 6 and 9 mark their readings (as declared; the code did not)

The record says a failure of 2, 4, 6 or 9 marks the affected readings, and that a control-6 failure withholds
reading 4's interpretation. The summary computed controls 4 and 6 but used neither. Now:
- control 6 not passing → `readings.resolution[sigma_kde]` is "withheld (control 6)";
- control 4 not passing → D1's consistency and every variance reading (D1 is the floor) are marked;
- control 2 not passing → D2, D3r, D3a and D3b are marked;
- control 9 failing, or 12AJ's grids not being there → `noise_source` is marked;
- a mark on the recommended variant is repeated in the recommendation. A test covers controls 2, 4 and 6.

The GPU lanes still start only after every CPU control passes, control 2 included (B1.5). That is stricter than
"marked", and it is kept.

### B2.5: control 1(d) covers every density

Control 1(d) compared the all-densities call with single calls for D0, D1 and D2 only. It now covers D0, D1, D2, D3r,
D3a and D3b, so the cell maps and the large D3 tables (about 600 MB at nside 16) are checked too. This adds about
5 min per cell: three more compiles and their control points.

### B2.6: jobs (scheduling only)

- **Failed CPU controls:** the lanes are now submitted with `--kill-on-invalid-dep=yes`. If a CPU control fails,
  Slurm cancels both lanes, and the summary (`afterany` on the lanes) still runs and writes `STATUS.json` with the
  gating failure. Before this, the lanes and the summary would have stayed pending forever.
- **The watcher** ends on `STATUS.json` or on the first job in a failure state (FAILED, CANCELLED, TIMEOUT,
  OUT_OF_MEMORY, PREEMPTED). If it ends on a failed lane, the summary still runs afterwards.

### B2.7: text corrections

- **Control 6's premises** were called "checked", but no code checked them. The review measured them:
  - the nside-64 footprint equals the mean of its nside-128 children exactly;
  - the cell f̄ values of D2, D3a and D3b agree between nside 64 and 128 to 4e-15;
  - the two catalogs hold the same galaxies in every nside-16 cell (equal counts, and z sums equal to 2e-11).

  Galaxy weights are checked per cell in the production run (`unit_galaxy_weights`).
- **Implementation section:**
  - the completion part uses core's gathered row-fraction form (`GatheredCompletionCurves`,
    `gathered_missing_density`) with f̄ per cell. Its arithmetic is the same as
    `selection_completion_curves_with_row_fraction`;
  - the table interpolant is B1.2's log-linear one, not a linear one.

### B2.8: tests and compute

- **Tests:** 20 12AL CPU tests pass (15 from B1 plus 5 new ones for B2.1 to B2.4). The 3 12AI tests also pass.
- **Compute:** about 65 min per cell at nside 64 and 70 min at nside 128, so about 2.3 h per card.
- **Queue:** rita runs 12AJ's two jobs first (about 1 h left), then 12AK's two lanes (5–11 h with both cards), then
  12AL's lanes.
- **Total from submission to the summary:** about 8.5–14.5 h, and up to about 25 h if 12AK's lanes run one after the
  other. The 7-day limit is a ceiling, not the estimate.

## Production (2026-10-19, location-free)

**Order (owner, 2026-10-19: "D1–D3 first").** 12AL's lanes run on rita before 12AK's: 12AK's two lanes (1390334,
1390335) are held and are released by a shell watcher once both 12AL lanes have left the queue.

**CPU controls in the miko holder (departure: scheduling only).** HENON was full, so the HENON controls job 1390345
was cancelled before it started. The same script (`slurm/phase12al_cpu_controls.sbatch`, clean worktree
`198046cae2f8`, x64, `JAX_PLATFORMS=cpu`) ran as a 32-CPU step of the miko holder job (step 1388940.48, reniced to
19; peak RSS about 9 GB). The lanes' `afterok` dependency on 1390345 was replaced by a hold, released only when the
step exited 0. 13:42–15:03 UTC; all pass:
- **1(c):** pass.
- **5:** pass at all four cells (relative deviations ≤ 7e-15; tolerance 1e-10).
- **8:** pass at all four cells (relative deviations ≤ 1.1e-14; tolerance 1e-10).
- **2:** pass for D2, D3a, D3b and D3r. Worst deviation below the depth 2.2e-6 (tolerance 1e-4), above 4.7e-13
  (tolerance 1e-12), log-sum 2.0e-10 (tolerance 1e-4), no finite-pattern mismatch. 2,258 s.

**Lanes.** Both started on rita: rita0 1390346 at 15:10 UTC and rita1 1390347 at 15:17 UTC. Each start
preempted a standby (`rita-s`) job by the cluster's QOS policy; no job was cancelled by hand. Summary 1390348
(HENON) follows. **Expected summary about 17:35 UTC** (B2.8's 2.3 h per card; range 17:15 to 18:45).

## Amendment B3 (2026-10-19): the nside-128 cells ran out of GPU memory; one-line fix, rerun of those two cells

**What failed.** Both nside-128 cells stopped at the same place, right after their tables were built: rita0's
`al_cell_ns128_sk1e-03` (job 1390346) and rita1's `al_cell_ns128_sk3e-03` (job 1390347). In both, controls 1(a),
1(b) and 10 had already passed bit for bit. The error was `RESOURCE_EXHAUSTED: Out of memory while trying to
allocate 23427856200 bytes`, in `build_tables` at `native = native.at[n_rows].set(0.0)`. That eager scatter copies
the whole per-row native table, (n_rows + 1) × n_z in float64, about 23 GB at nside 128. Both nside-64 cells
completed (`al_cell_ns64_sk3e-03` on rita0, `al_cell_ns64_sk1e-03` on rita1), as did all four Lane A grids.

**Fix (departure: implementation only).** Consumer commit 2de1cc3 does the same set inside a jit whose argument is
donated, so XLA writes the row in place. The values are bit for bit the same: the last row only ever receives
`where(valid, vals, 0.0)` = 0.0, and is then set to 0.0. The 20 12AL CPU tests pass at 2de1cc3. Nothing in the
variants, cells, grid, metrics, readings, controls or tolerances changes.

**Rerun.** Only the two nside-128 cell stages are rerun, from the clean worktree `2de1cc311911`, on the same plan
(`plans/production.json`); their Lane A grids are complete and are not rerun:
- `al_cell_ns128_sk1e-03`: job 1390414 (rita, one A100-80);
- `al_cell_ns128_sk3e-03`: job 1390415 (rita, one A100-80);
- summary: job 1390416 (HENON, afterany on both).

Each cell's control 10 records its own commit: 198046c for the nside-64 cells, 2de1cc3 for the nside-128 cells. The
summary has no rule tying cells to one commit.

**The partial summary.** The first summary job (1390348, afterany on both lanes) ran at 16:23 UTC on the two
nside-64 cells only. Its files are kept as `summary/*_1390348_partial.*` and are not this record's reading.

**Queue (owner: "D1–D3 first").** The shell watcher released 12AK's lanes when 12AL's first lanes ended. 12AK lane 0
(job 1390334) started and was cancelled about one minute in, before it wrote any output; Slurm refuses requeue for
it. It was resubmitted unchanged and held, as job 1390413, from the same worktree `2b31955040f1`, plan and names.
12AK's status job 1390336 now waits on 1390413 and 1390335. Both 12AK lanes are released by a shell watcher once
both nside-128 cells complete; if either fails, they stay held.

**Expected:** about 70 min per nside-128 cell with both cards in parallel (B2.8), so the summary at about 17:45 UTC
once both cards are ours (range 17:30 to 18:30).

## Amendment B4 (2026-10-19): control 7 failed at every cell; the tables leave out core's g (declared before the rerun)

**What failed.** All four cells completed (B3's nside-128 reruns 1390414 and 1390415, the nside-64 cells from the
first lanes). The summary (1390416) withheld every reading, because control 7 gates and failed at all four cells.
The worst relative errors at z ≥ 1e-3 were 1.7e-4 to 8.3e-4 against the declared 1e-4:

| cell | D2 | D3r | D3a | D3b | native |
|---|---|---|---|---|---|
| ns64_sk3e-03 | 2.9e-4 | 8.3e-4 | 2.3e-4 | 5.1e-4 | 1.7e-4 |
| ns64_sk1e-03 | 2.4e-4 | 1.7e-4 | 4.5e-4 | 4.7e-5 (pass) | 4.5e-4 |
| ns128_sk3e-03 | 3.7e-5 (pass) | 2.2e-5 (pass) | 2.9e-4 | 2.5e-5 (pass) | 5.3e-4 |
| ns128_sk1e-03 | 4.8e-4 | 6.8e-5 (pass) | 2.4e-4 | 2.8e-4 | 6.2e-4 |

Every other control passed. Those include control 3 (the native table equals D0 per injection, ≤ 1e-4) and
control 2 (CPU).

**Diagnosis (H0-free; CPU, the saved tables and core's evaluator).** Control 7's pairs were reproduced bit for bit
at ns64_sk3e-03 (D3r) and ns64_sk1e-03 (D3a, D2). Findings:
- **Few pairs, all at core's nodes.** Only 3 or 4 of about 9,960 compared pairs exceed 1e-4. Every one lies
  within one table step (1e-5) of a node of core's redshift grid: z_k = expm1(k ln 7 / 1085), which is 1.7951e-3,
  3.5934e-3, 5.3949e-3 and so on with `DARKSIRENS_ZMAX` = 6.
- **The tables are right at their nodes.** A dense evaluation across each failing table interval shows the
  table's nodes equal core's exact values (≤ 5e-15) and no jumps.
- **The cause.** Core's galaxy measure g(z) is interpolated linearly in log between those nodes
  (`log_interp_zgrid`), so log g bends at each node. A two-point table interpolant that straddles a bend errs by
  up to the slope change × h/4. That is about 8e-4 at the first node and falls as 1/z. The kernel window plays no
  part: at nside 64 it spans every slot.
- **Not a scale effect.** The error does not grow from sigma_kde 3e-3 to 1e-3, as interpolating the kernels
  would, and declaration Implementation's bound (h/σ)²/8 holds for the kernel part.

**The fix (departure: implementation; the owner chose it over changing the check).** g(z) is common to every
row: core's catalog term is exp(log N_obs + log g(z) + log mix_r(z)). So the tables now hold the catalog term
without g:
- **Table quantity:** T_c(z_j) = Σ_r N_obs,r mix_r(z_j) / m_c. It is computed as core's
  log N_obs + lp − log g(z) in log space (`catalog_term_pairs(..., without_g=True)`; at z = 0, where both S and g
  underflow, this keeps the finite mixture).
- **Evaluation:** the interpolated T is multiplied by g(z) from the tables' own kernel state (`log_g_grid` at the
  kernel pin, 67.74), with core's own `log_interp_zgrid`. This is done in the variants' density, in control 7 and
  in `table_lookup`. So the bends are core's, exactly, and only the smooth Gaussian mixture is interpolated.
- **The saved tables keep their meaning:** `tables.npz` holds T × g on the nodes, S_c/m_c as before; metric 7 is
  unchanged. It also holds `log_g_grid`.
- **Controls, tolerances, gates, metrics and readings are unchanged.** Control 7's floor is S's cell maximum on
  the nodes, as declared. Control 8 still checks S, the product. Separately, T and g each move with H0: a first
  edit that checked them apart failed a test, by about 0.6 relative, and was reverted. Only the product is
  H0-invariant, and the tables use both factors from one kernel state.

**Checks before the rerun.**
- **Tests:** 20 12AL CPU tests pass at consumer commit 5c2a096. These include a new test at core's nodes: pairs
  within 3e-6 and 7e-6 of core's first nodes, ≤ 1e-4, and T × g = S on the nodes to 1e-12.
- **Control 7 in the new form:** control 7's own pairs and seeds on the saved nside-64 tables, converted to the
  new form (T = S/g on the nodes), give:
  - ns64_sk3e-03 D3r 9.6e-7 (was 8.3e-4);
  - ns64_sk1e-03 D3a 2.3e-5 (was 4.5e-4);
  - below the gate, about 1e-6 at both.

**Rerun (all four cells, from scratch, at 5c2a096).**
- The CPU controls (1(c), 2, 5, 8) run first, as a miko holder step (HENON has no 32-CPU slot free), reniced.
- The two rita lanes, each with its two cells, are held until the CPU controls pass. The Lane A grids are core's
  stock D0, unchanged, and are skipped by their DONE.
- The superseded cell outputs move to `runs/<cell>/superseded_pre_B4/`, and the withheld summary to
  `summary/*_1390416_pre_B4.*`.
- 12AK's lanes are paused for 12AL ("D1–D3 first"). They resume from their checkpoints.

**Expected:** CPU controls about 80 min, then about 1.6 h per card. The summary is due about 3 h after the CPU
controls start.

## Results (2026-10-19, 20:48 UTC; location-free)

**Runs.** The CPU controls ran as a reniced miko holder step from 17:50 to 19:10 UTC at 5c2a096 with a clean tree:
rc 0, every control passed, no guard violation. The 12AK lanes were then paused: they were cancelled and
resubmitted held as 1390498 and 1390499. rita0 1390484 (ns64_sk3e-03, ns128_sk1e-03) and rita1 1390485
(ns128_sk3e-03, ns64_sk1e-03) both COMPLETED, 19:11 to 20:47 UTC (1 h 35 min and 1 h 36 min). The HENON summary
1390486 COMPLETED in 33 s with rc 0: gating failures none, guard violations none, readings not withheld. The 12AK
lanes were released at 20:47 UTC.

Outputs: `summary/summary.json`, `controls.json` and `STATUS.json` are location-free. `absolute.npz` is not for agents.

**Controls.**
- Controls 1, 2, 3, 5, 6, 7, 8 and 10 pass at every cell.
- Control 6: G_D = 1.8e-12 nat for D1, D2, D3a and D3b at both sigma_kde.
- Control 10: per-event sum ≤ 6.8e-13, zero walls, D0 tied to Lane A to 0.0.
- **Control 4 does not pass, narrowly, at all four cells, with identical numbers:**
  - ptp_W N[ln μ_D1 − ln μ_spec] = 0.0101 nat against ≤ 0.01;
  - max |N_eff,D1/N_eff,spec − 1| = 3.0e-4 against ≤ 1e-4.

  It is the same at every cell, as expected of the dV_c/dz interpolation on two grids. As declared (B2.4), D1's
  consistency and every variance reading are **marked**, not withheld. Not a reading: a relative N_eff difference of
  3e-4 moves V_sel,D1 by about 2e-4, against a ≥ 0.10 at every cell.
- Control 9: the noise source is marked at the two sigma_kde 1e-3 cells (12AJ ran at 3e-3 only).

**The catalog-added selection variance a (reading 2's base).** It is at least 0.02 at every cell, so reading 2
applies everywhere:
- 0.100 at (64, 3e-3);
- 0.196 at (64, 1e-3);
- 0.192 at (128, 3e-3);
- 0.446 at (128, 1e-3).

**Per cell and variant.**
- φ is the fraction of a removed.
- S_inj is the injection-mode shape variance of 12AJ's replicates, in nat².
- V_tot90 is the largest total variance over I90_D0; N1 is ≤ 1.2.
- "vs D0" is reading 1's comparison. "vs spectral" is the context, as in 12AI.

| cell | variant | φ | S_inj (D0's) | V_tot90 | H vs D0 (floor) | z_B | Delta vs D0 | reading 1 | R vs spectral | Delta vs spectral |
|---|---|---|---|---|---|---|---|---|---|---|
| 64, 3e-3 | D0 | — | 0.034 | 1.02 | — | — | — | — | 1.047 | −0.00 |
| | D1 | 1.00 | 0.0020 | 0.92 | 0.139 (0.060) | 1.03 | −0.31 | marginal (marked) | 1.016 | −0.32 |
| | **D2** | 0.85 | 0.0023 | 0.94 | 0.052 (0.059) | 0.84 | −0.01 | consistent | 1.007 | −0.01 |
| | D3r | 0.83 | 0.0029 | 0.94 | 0.054 (0.059) | 0.85 | +0.01 | consistent | 1.007 | +0.01 |
| | D3a | 0.73 | 0.0084 | 0.95 | 0.045 (0.053) | 0.77 | +0.04 | consistent | 1.024 | +0.04 |
| | D3b | 0.58 | 0.0137 | 0.96 | 0.038 (0.049) | 0.84 | +0.04 | consistent | 1.022 | +0.04 |
| 64, 1e-3 | D0 | — | 0.080 | 1.12 | — | — | — | — | 1.030 | +0.01 |
| | D1 | 1.00 | 0.0020 | 0.93 | 0.175 (0.097) | 1.02 | −0.34 | consistent (marked) | 1.013 | −0.32 |
| | **D2** | 0.92 | 0.0023 | 0.94 | 0.101 (0.097) | 0.91 | −0.03 | consistent | 1.006 | −0.01 |
| | D3r | 0.91 | 0.0034 | 0.94 | 0.103 (0.097) | 0.95 | −0.01 | consistent | 1.013 | +0.00 |
| | D3a | 0.84 | 0.0117 | 0.96 | 0.087 (0.088) | 0.75 | +0.02 | consistent | 1.027 | +0.04 |
| | D3b | 0.70 | 0.0236 | 0.99 | 0.080 (0.079) | 0.86 | +0.02 | consistent | 1.038 | +0.03 |
| 128, 3e-3 | D0 | — | 0.055 | 1.13 | — | — | — | — | 1.147 | −0.07 |
| | D1 | 1.00 | 0.0020 | 0.94 | 0.130 (0.080) | 1.00 | −0.25 | consistent (marked) | 1.013 | −0.33 |
| | **D2** | 0.92 | 0.0022 | 0.95 | 0.073 (0.080) | 0.98 | +0.04 | consistent | 1.008 | −0.03 |
| | D3r | 0.92 | 0.0028 | 0.95 | 0.076 (0.081) | 1.02 | +0.06 | consistent | 1.009 | −0.02 |
| | D3a | 0.86 | 0.0083 | 0.96 | 0.073 (0.077) | 1.04 | +0.09 | consistent | 1.027 | +0.02 |
| | D3b | 0.79 | 0.0137 | 0.98 | 0.067 (0.073) | 1.02 | +0.08 | consistent | 1.023 | +0.01 |
| 128, 1e-3 | D0 | — | 0.146 | **1.39** | — | — | — | — | 1.156 | −0.00 |
| | D1 | 1.00 | 0.0020 | 0.96 | 0.167 (0.136) | 0.93 | −0.31 | consistent (marked) | 1.010 | −0.31 |
| | **D2** | 0.97 | 0.0023 | 0.97 | 0.107 (0.135) | 0.98 | −0.01 | consistent | 1.017 | −0.02 |
| | D3r | 0.96 | 0.0033 | 0.98 | 0.110 (0.136) | 1.02 | −0.00 | consistent | 1.024 | −0.01 |
| | D3a | 0.92 | 0.0116 | 0.99 | 0.102 (0.131) | 0.90 | +0.04 | consistent | 1.041 | +0.03 |
| | D3b | 0.87 | 0.0236 | 1.01 | 0.094 (0.123) | 0.91 | +0.04 | consistent | 1.046 | +0.03 |

Every variant "reduces variance" at every cell (marked, control 4).

**Reading 3, recommendation (points only): D2.** D1 is first in simplicity, but it reads "marginal" at (64, 3e-3):
there H(p_D1, p_D0) is 0.139, against 2 H_floor = 0.120. D2 is consistent and reduces the variance at every cell.
D2's reading 1 does not depend on D1. Its reading 2 is marked through a, like every variance reading. B2.4 says a
mark on the recommended variant is repeated in the recommendation. The summary's recommendation entry does not
repeat it, so it is repeated here: **D2 (variance reading marked, control 4).** Adopting D2 as a core option is a core PR and the owner's call.

**Reading 4, resolution: "unchanged" for every variant, at both sigma_kde.**

| sigma_kde | H_D0(64,128) (injection floor of the difference) | D1 | D2 | D3r | D3a | D3b | G_D0 (nat) |
|---|---|---|---|---|---|---|---|
| 3e-3 | 0.053 (0.052) | 0.019 | 0.018 | 0.020 | 0.018 | 0.018 | 0.66 |
| 1e-3 | 0.076 (0.090) | 0.028 | 0.027 | 0.030 | 0.027 | 0.026 | 1.08 |

The distances fall to about a third under every variant, so the 0.75 ratio condition holds. But the drop (0.035 and
0.049) is smaller than twice the injection floor of D0's own difference (0.10 and 0.18). So, as declared, the
reading is "unchanged". D0's 64-against-128 distance sits at its own injection floor, in line with 12AJ's N3
reading of "Monte-Carlo noise". The declared interpretation, an indication rather than a decomposition, is that
what remains under D1 to D3b (0.018 at 3e-3) is the PE side's resolution effect.

**Reading 5, isotropy: "no isotropy signal"** at every cell. D2 and D3r are both consistent.

**Metric 7, the D1 diagnostic** at (64, 3e-3):
- ∫n̄ / ∫dN_exp below the depth is 1.037;
- ln(Z_f/Z_D1) is 5.8e-5;
- ρ(z) rises from about 0.75 at z 0.005–0.01 to above 1 by z 0.02.

The first bin, z < 0.005, is not finite (2.6e295), because dN_exp → 0 at z = 0. This is a defect of the diagnostic,
not a reading, and only bin 1 is affected. The nside-16 anisotropy coefficient of variation falls from about 1 at
z < 0.01 to 0.21 at z 0.24.

**Observations (not readings; for the owner).**
1. **Under D2 the catalog still does not narrow H0.** R against spectral only is 1.006–1.017 at all four cells, and
   Delta −0.03 to −0.01. The nside-128 widening under D0 (R 1.15 to 1.16) is gone (1.008 and 1.017). It came from
   the catalog-added selection noise, not from information.
2. **The noise fix is large.** D2's injection-mode shape variance is 0.0022–0.0023 nat² at every cell, against
   D0's 0.034–0.146: 15 to 64 times smaller, and about spectral only's floor (12AJ: 0.0020–0.0022). V_tot90 passes
   N1 at every cell under every variant, including (128, 1e-3), where D0 does not (1.39).
3. **D1 moves the median by −0.25 to −0.34 spectral sd at every cell.** Against spectral only it is −0.31 to −0.33.
   D2 and D3r stay within ±0.06. D1 keeps the catalog in the numerator, but drops the catalog's sky-averaged
   redshift structure from the denominator. Metric 7 shows that structure differs from the smooth model at low z,
   and is 3.7% above it integrated below the depth. Reading 1 calls the shift "consistent" at three cells only
   because H_floor there is large. It is the same size at all four cells.
4. **What this means for 12AI and 12AJ.** At the current injection count, the D2 selection term brings the shape
   noise down to about spectral only's. That should make C1's 0.05 resolvable. That would need a 12AJ-type bootstrap
   under D2, which has not been run.

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
sha256, in `config/record_envs/12AL.json`; `scripts/check_frozen_environment.py --record 12AL` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12AL/<sha7>` on
GitHub (2f849d9, 4823cbf, 447a072, ecbcd83, 198046c, 2de1cc3, 5c2a096). The full test suite is run by `./ci.sh` in the
record environments (CPU, HENON); it was green at the follow-up head
(`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main (above).

**Population of the spectral-only grids (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** The spectral-only grids gave the population as an explicit mapping at the corrected pair (0.04, 0.10). From
the consolidated main of PR #20 they evaluated the same values but recorded a `population.fixed_values` record (the
declaration written over equal entries); after the follow-up (PR #21) they resolve and record exactly what they did
when they ran (no `fixed_values` record; checked on the 12AG spectral reference at three H0 points: ln L difference
0).

**Run fingerprints (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a).** The code digests that the
12AG to 12AQ drivers put into their run fingerprints cover the consumer code, so a run stored before the consolidation
(or its follow-up) is evaluated again rather than resumed when it is rerun from main; the values it computes are the
same.

**Reading 1 cannot see a tilt (consumer PR #28, merge 8f8a7b2; finding C043).** Reading 1 decides on z_B and on the
Hellinger distance. z_B is the range of N Delta ln mu after its least-squares line over [50, 100] is removed, so it is
blind to a linear tilt of ln L, which is the mode that moves the median. Algebra (iv)'s "metric 4 and reading 1 test
for that bias" therefore holds for the Hellinger arm only. D1's shift against D0 (-0.25 to -0.34 spectral sd at every
cell) reads "consistent" at three cells through the Hellinger arm alone (observation 3 says so for another reason);
its undetrended statistics are z_A 1.85 to 2.73 and r_S 1.80 to 5.45, against z_B 0.93 to 1.03. D2's recommendation
holds under any statistic: shift -0.025 to +0.040 sd, z_A 1.02 to 1.25, r_S 0.63 to 1.07. The declared rules stand for
this record (owner decision 12B). Future bias and narrowing tests report the posterior shift and width ratio with
their paired-replicate spread, no threshold. Since the merge the 12AL summary reports this as metric 8 (shift against
D0 in spectral-only sd, width ratio, and their spread over 12AJ's 14 paired injection replicates). Re-run on the
stored grids (shift ± its paired-replicate sd, in spectral-only sd; 14 replicates):

| cell | D1 | D2 | D3r | D3a | D3b |
|---|---|---|---|---|---|
| 64, 3e-3 | -0.31 ± 0.10 | -0.00 ± 0.10 | +0.01 ± 0.10 | +0.04 ± 0.10 | +0.04 ± 0.09 |
| 64, 1e-3 | -0.34 ± 0.14 | -0.02 ± 0.13 | -0.01 ± 0.14 | +0.02 ± 0.13 | +0.02 ± 0.11 |
| 128, 3e-3 | -0.25 ± 0.16 | +0.04 ± 0.16 | +0.06 ± 0.16 | +0.09 ± 0.16 | +0.08 ± 0.15 |
| 128, 1e-3 | -0.31 ± 0.23 | -0.01 ± 0.23 | -0.00 ± 0.23 | +0.04 ± 0.24 | +0.04 ± 0.22 |

The spread is about the same for every variant at a cell: it is D0's own selection noise, which the pairing cannot
remove because the variants remove it. D1's shift is 1.3 to 3.1 of these spreads, the same sign at every cell; D2's is
within 0.3 of a spread everywhere. Width ratios against D0 are 0.93 to 1.02 with spreads 0.03 to 0.06. These numbers
agree with the record's Delta against D0 (the nominal shift is that Delta).

**Incomplete cells and fallback noise (consumer PR #28, merge 8f8a7b2; finding C044).** The summary of record recorded
each cell's `DONE` marker but did not gate on it; a cell that died during the replicates would have been read on the
fallback noise, which overstates the noise and favours "consistent", without a mark. All four cells finished and used
12AJ's replicates, so nothing changes. Since the merge a cell without `DONE` withholds every reading and the
recommendation (as 12AM and 12AN do), and a finished cell whose replicates are not all finite marks every reading of
the cell and the recommendation, and is named in STATUS.json.

**The recommendation's mark (consumer PR #28, merge 8f8a7b2; finding C130).** Amendment B2.4 says a mark on the
recommended variant is repeated in the recommendation; the code repeated only a mark on the consistency reading, and
control 4 marks the variance readings. The Results add the mark by hand ("D2 (variance reading marked, control 4)"),
which stays correct. Since the merge the summary's recommendation carries it (D2: "control 4" at all four cells) and
lists the marks on the readings that rejected earlier variants (D1: "control 4").

**The mass outside the window (consumer PR #28, merge 8f8a7b2; finding C046; owner decision 13A).** The location-free
summary of record writes `coarse_mass_outside_window` per density. 12AM amendment B2.1 later forbade that key: with a
width it gives a location (12AM noted 12AL's copy and flagged it). The key is withdrawn: since the merge the 12AL
summary writes only `window_holds`, and its location guard refuses the key. The window rule now integrates the
window's own nodes, as 12AM B2.5 does (the masked form understated the mass outside by 0.5 x step x (p(50) + p(100)));
every `window_holds` of record stays true. The file of record
(`phase12_5/selection_denominators/summary/summary.json`) still carries the key; its redaction is the owner's step. A
redacted copy (the file of record without its four `coarse_mass_outside_window` entries, otherwise byte-identical in
formatting) is prepared at `reviews/consumer-2026-10-24/fix/scratch_p11/12AL_summary_redacted.json` (sha256
1c03ed753127fef74cfdd2a6fadfd6c763039846826f58ef0584206948a63efc). 12AM, which pins this file's sha256, also accepts
the redacted copy's since the merge (`phase12am_common.SHA256_ALSO`), with the same 12AM summary.

**Control 4's cause (consumer PR #28, merge 8f8a7b2; finding C127).** "Differences come only from interpolating
dV_c/dz on two grids" (Controls, item 4) and "the dV_c/dz interpolation on two grids" (Results) should read: **one
grid, two interpolants**. D1 reads core's dN_exp linearly between the nodes of core's shared log z grid; spectral only
reads the normalised dV_c/dz on the same grid log-linearly (z^2 below the first node). The two differ mostly below z
0.05. Swapping the interpolant accounts for the window miss (0.0101 nat) exactly; the N_eff-ratio miss (3.0e-4) comes
from the coarse-grid edge at H0 = 20 (6.1e-5 inside the window). Under the run's DARKSIRENS_ZMAX = 6 the grid has
1,086 nodes to z = 6 (the text says 1000 nodes to z = 5; same step). The effect on these BBH records is bounded by the
0.0101 nat over the window.

**gpu-control options (consumer PR #28, merge 8f8a7b2; finding C132).** `phase12al_cell.py --mode gpu-control`
accepted `--nside`, `--sigma-kde` and `--selection-variant` and ignored them (it always checks 12AG's production cell
with every variant). No run of record passed them. Since the merge it refuses them.

**Core settings at trace time (consumer PR #29, merge 0989df4; findings C054, C055).** Core reads its
normalisation-grid settings and its missing-density form when a likelihood program is traced, at its first call, not
when the target is built. From the merge the stock target and the spectral joint target take a snapshot of those
settings at build and refuse a trace under other ones, as core's own bindings do since core 3cf8df7. Both numerics
modes now also set the normalisation grid sizes, the pairing m1 grid (off) and the pairing edge rule, and the builder
refuses a `DARKSIRENS_*` variable core reads as a numerics setting; the values set are the defaults of every record
core (e7c3007, 32c6210, 1022429) and of the 12S pin, which this record ran with (no launcher set a `DARKSIRENS_GW_*`
variable), so this record's numbers are unchanged. The target's record and provenance now carry every grid and
catalog-evaluation setting and core's numerics semantic under `core_numerics.core_settings`. Because the provenance
enters core's run fingerprint, a checkpoint written by an earlier main is not resumed by this one (it is refused,
loudly); a run started afresh computes the same numbers.

**Calibration anchor (consumer PR #29, merge 0989df4; finding C094).** A configured log10n0 outside the calibration
prior's log10n0 bounds is now refused, and so is an anchor whose sampler coordinate does not decode back to the
configured log10n0 within 1e-12 (which also happens inside the bounds, far in a conditional normal's tail, where the
quantile rounds to 0 or 1 and decodes to the bound). Before, such an anchor evaluated at the bound without an error in
the callers that did not check it themselves (the anchor gate before sampling, the 12U stage, the direct chains'
anchor and the ladder-cell check). Every record's anchor lies inside its prior's bounds and decodes to within 2.3e-16,
so this record is not affected.

**Writer commit (consumer PR #29, merge 0989df4; finding G4.10).** The summaries behind this record did not carry the
commit of the code that wrote them (the commit is in the job logs and the record). From the merge each summary carries
a `writer` block: the writing script, its checkout's commit, branch and changed-file count, and, where it reads a
short list of files, their sha256. The stored summaries are unchanged; a summary rewritten from main carries the
block.

## Amendment (26 Oct 2026): independent review, round 3

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses below.
The amendment of 25 Oct 2026 above covers the fix packages merged first. This one covers five more, merged on 26 Oct
2026 after a third fix round and an independent check of each: the 12AQ readings and mock (consumer PR #32, merge
97ec978), the 12AO ladder (PR #27, merge ebb12ff), the GW inputs (PR #26, merge a152bed), the variance guard and
estimator noise (PR #33, merge 901bb54) and catalog version 2 (PR #24, merge 402c947). The consumer's main is now
402c947. `./ci.sh` passed on the merged tree in all three record environments (HENON, CPU;
`ci_logs/20261026T124516Z_133bc47f981f_<env>.log`: consumer_e7c3007_cuda12 1568 passed, consumer_e7c3007batch_cuda12
1577, consumer_1022429_lss57afebe_cuda12 1592; none failed). On 26 Oct 2026 the owner decided that catalog version 2
vetoes the bright-star masks, BRIGHT and MEDIUM (Legacy Survey maskbits 2050), not the large-galaxy bit, and that the
injections stay at the support gate for now (decision 4D; the replacement of the O3 campaign, 4A, is deferred and no
new injection product is made). Location-free throughout. Unless an item says otherwise, no number of record changes.
Still open and not amended here: resume markers and fingerprints (consumer PR #25) and the follow-ups of consumer PR
#35, among them the refusal of a delta outside its prior's bounds.

**Catalog model (consumer PR #24, merge 402c947; findings C020, C002, G2.4).** These grids fix the calibration at
log10 n0 = -1.8216 (12AB's baseline median, set almost entirely by the [0.02, 0.30] count ridge) and the luminosity
prior means; the in-depth ridge and the floor are discussed in 12AF's amendment of this date (C020, C002). Cells below
sigma_kde about 1e-3 are not physical host-redshift kernels (G2.4, see 12AG's amendment of this date).

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). No number of this record changes.
