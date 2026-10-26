# Phase 12U — the DESI catalog split into its spectroscopic and photometric parts (declaration)

## Status

**DECLARED (owner, 2026-10-05) before any run. RESULTS appended below (2026-10-07).**
The calibration values of each part come from a CPU preparation that runs
before the GPU job. They are added to this record, under "Calibration values",
before the owner submits the GPU job. The owner decides what follows.

## Why

12T (merged 20a1a84) left the catalog's role open:

- **No narrowing.** The DESI catalog never narrows H0. Every chain is 1.09 to
  1.15 times the spectral-only width (sd 5.05).
- **A shift.** It moves the median from the spectral 64.3 to about 69 to 70.

The catalog is a union of two kinds of redshift:
- DESI Loa BGS spectra (27% of the galaxies in the calibration window);
- Legacy Survey photometric redshifts (the rest).

Splitting it shows which part carries the shift.

**Evidence from the mock campaign** (darksirens-examples GAPS.md, "Modelling
notes"; tutorial 06, section 7; `examples_mock/diag_02_bias`).

Core's galaxy redshift kernel is N(z; z_obs, s) g(z) / Z, with
g = dV_c/dz (1+z)^delta (`catalog/redshift.py:1-14, 110-126`). It puts a smooth
comoving-volume prior on each galaxy's true redshift inside its photo-z
width. That moves each kernel's mean up by about s² d ln g/dz.

In clustered mocks this biases H0:
- by -1.65 ± 0.74 km/s/Mpc at s = 0.015 (1+z);
- by -0.39 ± 0.62 with the exact clustered kernel;
- by about -0.25 at s = 0.0075. The bias scales as s².

The DESI photo-z widths are larger than the mock's. The median ZERR is:
- 0.016 at z 0.10;
- 0.024 at z 0.19;
- 0.032 at z 0.23.

## Owner decisions (2026-10-05)

- **Step 4.** Run three chains:
  - the spectroscopic part, **BGS Bright only** (M_APP <= 19.5). BGS Faint
    is dropped.
  - the photometric part;
  - **one** sensitivity of the union, the re-centred kernel. The half-width
    run is dropped.
- **n0 prior.** count_ridge only. No flat_wide chains.
- **Compute.** ONE rita A100 job that runs every stage in order. The second
  A100 stays free.
  - The CPU preparation and its smoke test run before it on HENON (qos
    henon), not RM.
  - Output goes under
    `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12u/`.
- **Code.** Consumer branch `phase12u/split`, from `phase12t/core-repin`
  (4c44184); declared code at c074b07. It reuses the 12T environment (core
  e7c3007, surveys 0.2.0). No package changes.
- **Fixed as in 12T:**
  - one seed (22) per chain, dynesty nlive 1000, dlogz 0.1;
  - z_depth 0.245;
  - sigma_kde 0.003;
  - the soft guard at cap 20;
  - kernel pin off and core defaults;
  - the fixed GWTC-5 population;
  - H0 U[20, 140].
- **GW input.** The exact-prior files (gwcat 8263ae9).
- **Spectral-only baseline.** Reused, not rerun: the 12T grid on the same
  exact-prior inputs (median 64.27, sd 5.05). Its MAP is every chain's
  anchor H0.

## The catalog and its provenance

**How it is built.** The P12.4 catalog is built by the legacy builder
`experiment_loa_rebuild/scripts/build_loa_rebuild.py` (default arguments)
in desi_darksirens_selection. It writes `rebuild_loa_faint_pixelate_input.h5`.

The builder streams the Legacy Survey parents (DR10 south, DR9 north). For
each LS row it applies:
- the LS quality cut;
- r <= 21, and 0 < sigma_z < 0.1 for photometric rows;
- 0 < z <= 0.30;
- the faint floor M_r < -20.166 (h = 0.6774).

It takes the DESI spectroscopic redshift wherever the row matches a Loa BGS
spectrum, and the LS photometric redshift otherwise.

**Provenance survives in the native table but not in the analysis file.**
- The native table keeps each row's `SURVEY_CODE`:
  - 0: BGS Bright spectrum, 4,968,098 rows;
  - 2: BGS Faint spectrum, 1,189,386 rows;
  - 1: LS photometric redshift, 16,630,351 rows;
  - 268 DESI-only rows with no LS photometry, which the P12.4 cut removes.
- The standardized catalog `desi_union_nside64.h5` holds only z, dz, the
  apparent magnitude and the weight per pixel slot.
- So the spectroscopic part can be selected from the native table.
- The photometric redshift of a matched galaxy is not in the union at all.
  The photometric part is therefore rebuilt from the LS parents, in one pass
  of the same builder (see Stages, step P1).

## The parts

| Part | Galaxies | Redshifts | Footprint |
|---|---|---|---|
| **spec** | Union rows with a BGS Bright spectrum (code 0) and M_APP <= 19.5 | Spectroscopic | The LS map times c_p (below) |
| **photo** | Every LS galaxy of the union's parent, with its photometric redshift | Photometric | The LS map |
| **union_centred** | The union | Photometric rows: centre moved (below); width unchanged | The LS map |

**spec.**
- **The sample.** BGS Bright only (owner, 2026-10-05). 19.5 is its flux
  limit. BGS Faint (code 2) targeting depends on colour and fibre magnitude,
  which a single magnitude limit cannot model, so every code-2 row is left
  out, including those at M_APP <= 19.5.
- **The footprint.** DESI observed only part of the LS sky, and only a
  fraction of the targets there have spectra.
  - c_p is the per-pixel spectroscopic fraction (nside 64): among union
    galaxies with M_APP <= 19.5 in the pixel, the fraction with a BGS
    Bright redshift.
  - The spec map is f_p,spec = c_p f_p,LS. Pixels without spectra are off
    the footprint, where the catalog is completed entirely.
  - This assumes the spectroscopic fraction does not depend on magnitude
    below 19.5 inside a pixel.

**photo.**
- The photometric part is not the union's code-1 rows. Those have the
  spectroscopic galaxies punched out, and no completeness model describes
  that.
- It is the same LS galaxy sample with photometric redshifts throughout. It
  uses the builder's photometric retention rule and the faint floor, applied
  with the photometric redshift.

**union_centred.** This arm isolates the smooth-prior effect.
- Each photometric row's centre z_c is moved so that the mean of core's
  kernel N(z; z_c, s) g(z) / Z on [0, 6] equals the catalog photo-z, with:
  - s = sqrt(ZERR² + 0.003²);
  - g evaluated at delta = -0.84, the 12T count_ridge_exactGW posterior mean;
  - z_c floored at 1e-4.
- The kernel width, the galaxies, the anchor calibration and the
  luminosity prior are those of the 12T union chain. The count ridge is the
  union's full recomputation (below). Only the mean pull is removed.
- The mock diagnosis says the bias is this mean pull, about s² d ln g/dz.
  The pull at the median DESI width is about 0.004 at z 0.1 and 0.007 at
  z 0.2.
- Why centring rather than narrowing (the owner chose this run only):
  narrowing would also make every photometric galaxy overconfident and change
  the PE Monte-Carlo guard's behaviour (the mock lost low-H0 points at
  s <= 0.0145).
- The arm is also physically motivated: the LS photo-z is a regression
  estimate of z given the photometry. If it is already unbiased given z_phot,
  the extra volume prior counts the prior twice. The kernel-centre test in
  step P2 measures this directly.

## Calibration of each part

A wrong calibration would dominate any comparison, so each new catalog gets
its own. Each part is calibrated with the calibration_12q run 2 procedure
(the one P12.4 uses), generalized in `scripts/phase12u_calibrate.py`. Its
helpers are imported unchanged.

| | spec | photo | union_centred |
|---|---|---|---|
| Sample | spec rows after the quality cut and the Phase 12I mask, z in [0.02, 0.30] | the same, all rows | the union's (12T) |
| m_lim | 19.5 | 21.0 | 21.0 |
| Luminosity fit (M0hat, sigma_M) | Re-fit; redshifts exact, so no photo-z bias and no inversion | Re-fit; mock photo-z bias, then the fixed-point inversion to the true values | Not re-fit: 12T's N(-20.500, 0.199), N(0.557, 0.130) |
| Luminosity prior width | half the north–south offset | hypot(half the north–south offset, the mock bias) (12P rule) | 12T's |
| Count density (log10n0, delta) | `fit_density_selection` over [0.02, 0.30], exact; cross-check over [0.02, 0.245] | forward-modelled through the ZERR mixture over [0.02, 0.30]; cross-check over [0.02, 0.30 - 3 sigma_z(0.30)] | 12T's |
| Footprint (Omega_eff) | f_p,spec | the LS map | the LS map |
| Count ridge | re-derived | re-derived | the union's, re-derived (not 12T's; see below) |

**The count ridge**, defined as in 12T:
- For each delta on [-3.0, 1.5], take the log10n0 whose expected count over
  [0.02, 0.30] equals the part's observed count. The expected count is
  recomputed from the full model at each delta, photo-z kernels included,
  and is linear in n0 at fixed delta.
- Fit a line a + b delta through it.
- The width sd is the rms of log10(observed / expected) over the 28 bins at
  the fit.

12T evaluated this definition approximately. It rescaled the fit's stored
binned expected counts by (1+z)^(delta - delta_fit) at the bin centres,
which ignores how the photo-z kernels move galaxies between bins as delta
changes. It also quoted the scatter about the mean of log10(observed /
expected) rather than the rms. On the union the approximation gives
a -1.8158, b -0.0847, sd 0.0339 (12T's values). The full recomputation gives
a -1.8105, b -0.0894, sd 0.0364, 0.009 dex higher at the 12T posterior
delta (-0.84), about a quarter of sd. On the spectroscopic part, with no
photo-z kernels, the two agree to 1e-5. Every arm therefore uses the full
recomputation, the union arm included (owner, 2026-10-06).
- The hard bounds stay [-2.4, -1.2], unless the ridge comes within 10 sd of
  them. They are then re-centred on the ridge with the same width.

**Sensitivity arms.** union_centred moves some photometric rows out of
[0.02, 0.30], which changes the observed count. The preparation records the
change. The union's ridge is kept if the change is well below its sd.

**Control.** The same script, run on the union, must reproduce:
- calibration_12q run 2: log10n0 -1.9065 and delta 1.0475;
- the 12T ridge: a -1.815898, b -0.084675, sd 0.033846, when evaluated with
  12T's approximation.

## Priors on (log10n0 [h-scaled], delta)

Every chain uses count_ridge: delta U[-3.0, 1.5] and
log10n0 | delta ~ N(a + b·delta, sd), truncated to the bounds above. spec
and photo use their own (a, b, sd); union_centred uses the union's.

How the two 12T priors behaved on the union:
- **flat_wide** (log10n0 U[-2.4, -1.2]):
  - H0 69.41 ± 5.80, 1.15 times the spectral width;
  - the data alone place log10n0 at -1.82 ± 0.17.
- **count_ridge:**
  - H0 70.22 ± 5.55, or 70.11 ± 5.52 on the exact inputs;
  - log10n0 is three times tighter (± 0.05);
  - the evidence prefers it to flat_wide by 0.9 in log.

The n0 prior carried about 1 km/s/Mpc of H0. count_ridge is chosen because:
- it ties n0 to each catalog's own count, which is the quantity re-fitted
  here;
- a flat range would have to be re-centred for the spectroscopic part
  anyway.

Each part's ridge range is recorded. No flat_wide chain is run (owner,
2026-10-05).

## Stages

### CPU preparation (HENON, before the GPU job; `config/phase12u_prep_manifest.json`)

- **P1.** The LS photometric rebuild. One pass of the builder:
  - It writes the union, which must equal the legacy native table column by
    column (exact, or to 1e-9 with identical rows and nan pattern).
  - It writes every LS galaxy with its photometric redshift, keeping the
    DESI match in extra columns.
- **P2.** The sub-catalogs:
  - the native tables, the spec footprint map (checked: the loader returns
    c_p f_p,LS) and the standardized nside-64 catalogs, built as the P12.4
    union is;
  - a control that standardizes the union again and compares the result with
    the 12S catalog's sha256;
  - the **kernel-centre test**: on LS galaxies that also have a DESI
    redshift (all, and M_APP <= 19.5), the mean (z_spec - z_phot) per 0.01
    bin of z_phot, against the mean pull core's kernel gives them.
- **P3.** Calibrations and count ridges: the union (control), spec and
  photo.
- **P4.** `scripts/phase12u_make_manifest.py` writes the GPU manifest from
  P3's values. The CPU smoke of that manifest then runs on HENON.

### GPU job (rita, one A100, `config/phase12u_manifest.json`, in this order)

For each part, an H0 scan comes first. It evaluates the likelihood and the
per-point Monte-Carlo record at 12 H0 values over [25, 139], at the anchor
calibration, and takes minutes. The chain follows. All chains use the
exact-prior GW inputs.

| # | Stage | Estimate |
|---|---|---|
| 1-2 | scan, then chain **spec_only** | 3–6 h (about a quarter of the union's galaxies) |
| 3-4 | scan, then chain **photo_only** | 7–9 h |
| 5-6 | scan, then chain **union_centred** | 7–9 h |

The estimates come from the 12T chains (6.9 to 8.9 h each on the union).
The total is about 18 to 25 h, against the 7-day limit. Resubmitting
continues from the DONE markers and the dynesty checkpoints.

## What is reported

For each chain:
- the H0 posterior: median, 68%, sd, and sd against the spectral-only 5.05;
- the shift against the spectral median (64.27) and against
  count_ridge_exactGW (70.11 ± 5.52);
- the (log10n0, delta) posterior and its offset from the part's ridge;
- the fraction of samples near a prior edge;
- logZ;
- the chain's gates: convergence, 12F gate 7, selection N_eff;
- the H0 scan's rejected points, if any.

For the preparation:
- the union parity;
- the control calibration against calibration_12q and 12T;
- each part's calibration, ridge and observed/expected curve;
- the spec footprint's c_p summary;
- the kernel-centre test.

## Expectations, not thresholds

No pass/fail threshold is set; the owner judges.

- **spec_only.** Exact redshifts, but the sample is shallow: r <= 19.5 meets
  the faint floor only to z ≈ 0.16, and the footprint is smaller. Most of
  the volume is completed rather than catalogued. Expected: close to the
  spectral width (1.0 to 1.1 times) and a smaller shift than the union. A
  union-sized shift from spectra alone would say the shift is not a photo-z
  effect.
- **photo_only.** 73% of the union is already photometric. Expected: close
  to the union (median about 69 to 71, width 1.1 times the spectral).
- **union_centred.** If the smooth prior pulls H0 down, as in the mocks,
  removing the pull moves H0 up. Expected: an upward shift of 0 to a few
  km/s/Mpc against 70.11, at the same width. No shift means the smooth
  prior does not drive the union's result.
- **Kernel-centre test.** Core's kernel pull is positive and grows with s.
  If the LS photo-z are unbiased given z_phot, the measured
  mean (z_spec - z_phot) is near zero.

## Calibration values

From the CPU preparation (`phase12u/prep/`, HENON job 1361250, consumer
c074b07). log10n0 is h-scaled. The GPU manifest and the count-ridge presets
are at consumer ab226d6.
- The CPU smoke of that manifest (HENON 1361251, nlive 8) passed all six
  stages.
- The union_centred stages, re-smoked with the union's ridge (HENON
  1361514), also passed.
- The smoke scans at H0 30, 64 and 130 rejected no point. The selection
  N_eff is 1.2 to 4.9 times its threshold, and lowest for photo_only at
  H0 30 (1.25).

| | union (control) | spec | photo |
|---|---|---|---|
| Rows in [0.02, 0.30] | 22,778,800 | 4,907,325 | 22,498,606 |
| Exact-redshift fraction | 0.270 | 1.000 | 0.000 |
| m_lim | 21.0 | 19.5 | 21.0 |
| Luminosity fit on observed z (M0hat, sigma_M) | -20.309, 0.714 | -20.187, 0.816 | -20.304, 0.711 |
| After the photo-z inversion | -20.498, 0.559 | (no inversion) | -20.536, 0.510 |
| Luminosity prior: M0hat | N(-20.498, 0.199) | N(-20.187, 0.010) | N(-20.536, 0.252) |
| Luminosity prior: sigma_M | N(0.559, 0.130) | N(0.816, 0.006) | N(0.510, 0.168) |
| Forward fit (log10n0, delta) | -1.9067, 1.050 | -1.7141, -0.127 | -1.9479, 1.537 |
| Cross-check fit (log10n0, delta) | -1.7229, -2.568 (z <= 0.172) | -1.7415, 0.341 (z <= 0.245) | -1.8303, -0.223 (z <= 0.176) |
| Count ridge a, b, sd | -1.810518, -0.089449, 0.036361 | -1.724559, -0.076030, 0.030334 | -1.807815, -0.089445, 0.035470 |
| Ridge range over the delta prior | [-1.947, -1.545] | [-1.841, -1.498] | [-1.944, -1.542] |
| log10n0 bounds (re-centred) | [-2.346, -1.146] | [-2.270, -1.070] | [-2.343, -1.143] |

- **Control.**
  - With calibration_12q's luminosity values held fixed, the 12U script
    reproduces its forward fit to 1e-7: -1.906534, 1.047456.
  - The photo-z inversion itself moves the union's luminosity values by
    about 1e-3 (-20.4997, 0.5575 in 12q; -20.4984, 0.5589 here). Its
    "common" random numbers stop being common once a single mock galaxy
    crosses the magnitude cut, so the result carries Monte Carlo noise of
    the order of its 2e-3 tolerance. That is 0.01 of the prior widths and
    moves delta by 0.003. It is accepted and reported (owner, 2026-10-06).
  - 12T's ridge approximation, evaluated on these outputs, gives
    a -1.815834, b -0.084672, sd 0.033892, against 12T's -1.815898,
    -0.084675, 0.033846.
- **union_centred** removes 41,581 rows from the window (-0.0008 dex in the
  count, against sd 0.036), so it keeps the union's ridge and bounds.
- **photo's forward-fit delta (1.537) lies just above the delta prior
  (U[-3.0, 1.5]).** The chain samples the prior, and the anchor is used only
  for the H0 scan. On the union the GW-weighted posterior sat far from the
  forward fit (delta -0.84 against 1.05).
- **spec's luminosity prior is narrow** (0.010, 0.006). The 12P rule then
  reduces to half the north–south offset, because exact redshifts have no
  photo-z bias.
- **Kernel-centre test** (LS galaxies with a DESI redshift, 5.9 million; per
  0.01 bin of z_phot):
  - core's kernel moves each kernel's mean above z_phot by +0.003 at z 0.02,
    rising to +0.006 to +0.008 over z 0.08 to 0.30;
  - the measured mean (z_spec - z_phot) is within ±0.002 of zero over z 0.08
    to 0.22, and +0.001 to +0.003 below 0.08;
  - above 0.22 it falls to -0.023 in the last bin. The test cannot tell a
    photo-z bias there from the selection of which galaxies have spectra
    (brighter galaxies, at lower true z for a given z_phot);
  - over z 0.08 to 0.22, the LS photo-z are unbiased while core's
    kernel pulls galaxies to higher z, which is the effect union_centred
    removes;
  - the M_APP <= 19.5 subsample gives the same picture.

## Results (2026-10-07)

All six stages ran in one rita A100 job (1361525, 17.6 h, 0 failed stages),
consumer ab226d6. Outputs are under
`/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12u/runs/`
(each stage directory holds result.json and samples.npz; the runner summary is
in runner_status.json).

### Chains (dynesty nlive 1000, dlogz 0.1, seed 22, exact-prior GW inputs)

| Chain | H0 median [68%] | H0 sd | sd / spectral | log10n0 | delta | logZ |
|---|---|---|---|---|---|---|
| spec_only | 70.32 [64.7, 76.1] | 5.65 | 1.12 | -1.663 ± 0.040 | -0.86 ± 0.33 | -765.79 ± 0.07 |
| photo_only | 70.53 [65.2, 76.5] | 5.72 | 1.13 | -1.734 ± 0.051 | -0.88 ± 0.35 | -765.49 ± 0.07 |
| union_centred | 70.06 [64.6, 75.5] | 5.58 | 1.11 | -1.744 ± 0.052 | -0.79 ± 0.35 | -765.50 ± 0.07 |
| 12T count_ridge_exactGW (reference) | 70.11 [64.6, 75.5] | 5.52 | 1.09 | -1.747 ± 0.048 | -0.84 ± 0.35 | -765.20 ± 0.07 |

Diagnostics for every chain:
- converged (stop reason "convergence", final dlogz 0.0999);
- the 12F gate 7 is met, unpenalised at the posterior mean and median;
- selection N_eff is 5.4 to 5.5 times the threshold;
- the H0 scans (12 points over [25, 139]) rejected no point.

Prior edges: no sample lies within 2% of the prior range of an edge, in
log10n0, delta or H0. log10n0 sits on each part's ridge (median offset -0.09
to -0.13 of the ridge sd).

### Reading

1. **Spectroscopic redshifts alone give the union's H0.** spec_only, with
   exact redshifts for BGS Bright galaxies only, lands at 70.32, 0.2 from the
   union and +6.0 from the spectral-only median of 64.27. The shift of the
   catalog analyses against the spectral-only grid is therefore not a
   photometric-redshift effect.
2. **The photometric part carries the union's result.** photo_only gives
   70.53, 0.4 from the union.
3. **Removing the smooth-prior pull does not move H0.** union_centred moves
   every photometric kernel's mean back onto its photo-z and gives 70.06,
   -0.05 from the union (the ridge also changed by 0.009 dex, see "The count
   ridge"). On this event set the smooth prior on true redshift does not drive
   the union's H0, although in the clustered mocks it biases a complete
   catalog low by about half a posterior width at sigma_z 0.015.
4. **No part of the catalog adds precision.** All three chains are 1.11 to
   1.13 times wider than the spectral-only grid, as the union was (1.09). A
   catalog that carries little information leaves little for a redshift-prior
   pull to act on, which is consistent with point 3.
5. The three arms agree within 0.5 km/s/Mpc, a tenth of their width. The
   spectroscopic/photometric split and the kernel centres are not the source
   of the +6 km/s/Mpc offset from the spectral-only result. The owner decides
   what follows.

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
sha256, in `config/record_envs/12U.json`; `scripts/check_frozen_environment.py --record 12U` checks that an
environment is exactly it. The consumer commits this record names as code that ran are tagged `record/12U/<sha7>` on
GitHub (c074b07, ab226d6). The full test suite is run by `./ci.sh` in the record environments (CPU, HENON); it was
green at the follow-up head (`ci_logs/20261025T163303Z_2b5695027bbb_<env>.log`) and is green at the final main
(above).

**Population of the base configuration (consolidation, consumer PRs #20 and #21, merges 3e27e1f and 77b3d0a; finding
C052).** This record's runs built the 'gwtc5' preset of their core as it is (core e7c3007: mu_chi 0.0633, sigma_chi
0.3654); `population.fixed_values` did not exist yet (it came with 12Y's commit 0d75b40). Since the consolidation the
base configurations declare `population.fixed_values` (0.04, 0.10) for the preset, so that they mean one population on
every core (core #60 changed the preset to that pair). On a core before #60, a stage run from the consumer's main with
the base configuration therefore uses (0.04, 0.10), not this record's population, and the gated P12.3 and P12.4
runners refuse the base configuration there. This record is reproduced from its tagged commit (c074b07, ab226d6), or
from main with `--set population.fixed_values=null` (the configuration as it ran;
`config/desi.fixed_population.core_preset.json` is the old base configuration byte for byte). The committed manifests
(`config/phase12t_manifest*.json`, `config/phase12u_manifest*.json`) drop the base configuration's spin declaration in
every stage that builds a target (`population.fixed_values=null`) and point the 12T parity arms at
`config/desi.fixed_population.core_preset.json`: they resolve the configuration these runs used.

**Chains through the 12T stage (consumer PR #31, merge b9ec283; findings C029, C123, C125).** This record's chain
stages use the 12T chain driver: from the merge their `status.json` and logs are location-free, their `--anchor-from`
grid must be accepted (theirs is the accepted exact-GW grid of 12T) and a finished unconverged checkpoint is refused
before the build, except for the smoke chains run with `--allow-unconverged`, whose resume writes the capped result as
before.

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
so this record is not affected. A delta outside its prior's bounds is still accepted: the 12U photometric stage ran
with delta 1.5375 against the count_ridge_photo prior's [-3, 1.5], so refusing it is an owner decision.

**Runner jobs (consumer PR #30, merge 6d0f800; finding C138).** This record's runner jobs ran from shared clones with
no commit pin. Only 12AE Part 2 mixed commits; this record's runs did not. From the merge the runner job files refuse
to start without PHASE12_EXPECT_SHA naming the commit of a clean checkout, and the stage runner repeats that check
before every stage, stopping (exit 3) if the checkout moves.

**Launch files (consumer PR #30, merge 6d0f800; finding C137).** The launch files of this record predate the owner's
Slurm rules of 18-19 Oct 2026 (7-day limits; rita GPU jobs at 128 CPUs and 120G; holder steps only through the
wrapper) and break them. They are kept unchanged in what they launch, as the record of how the record ran, and from
the merge they refuse to run unless PHASE12_ALLOW_HISTORICAL names them (slurm/historical_launch_files.txt lists
them). The B1 and B2 pipelines' HENON fallback now clears every SLURM_* variable first.

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

**Photometric kernel (consumer PR #24, merge 402c947; finding G2.1).** Core's row kernel N(z; z_i, s) dV_c/dz
(1+z)^delta / Z_i treats the Legacy Survey photo-z as a likelihood centre and multiplies by the volume prior again,
while the photo-z behaves as a posterior-mean estimate (unbiased given z_phot). On 7.8M non-training DESI matches the
kernel of record has PIT mean 0.406 and 68%/95% coverage 0.633/0.911, against 0.492 and 0.699/0.937 for the plain
truncated Gaussian; the log score favours the plain kernel by 0.083 nat per galaxy. Its mass below z_depth is 11.5%
low for the photometric rows (7.9% for the union's observed-branch count). This record's re-centred arm (nside 64,
sigma_kde 3e-3, delta sampled) moved H0 by about 1% of its sd; no later record used it.

**Kernel-centre test (consumer PR #24, merge 402c947; finding G2.3).** The drop of the mean z_spec - z_phot to -0.023
at z_phot 0.29 is an artefact of the test's own spectroscopic match, cut at z <= 0.30: 42.9% of matched galaxies at
z_phot 0.29-0.30 have z_spec > 0.30. With the z <= 0.5 match the mean offset at z_phot 0.22-0.29 is +0.0008 to
+0.0018: the photo-z are unbiased given z_phot over the whole window, and neither offered reading (a photo-z bias, the
selection of galaxies with spectra) holds.

**Photo-z error calibration (consumer PR #24, merge 402c947; finding G2.5).** The photometric widths have Gaussian
cores (robust pull width 0.944; north 0.890, south 0.971) but heavier tails (pull sd 1.076; 1.26% beyond 3 sigma
against 0.27%), and the DR9 north photo-z sit low by 0.002 to 0.004 at z_phot 0.08-0.16. Even a fully catalog-driven
H0 would move by about 0.1% from the north/south part.

**Spectroscopic arm (consumer PR #24, merge 402c947; finding C019).** The spectroscopic luminosity fit truncates at r
<= 19.5 only, but the floor is the tighter cut for 32.5% of spectroscopic rows (every row below z 0.15). With the
floor in the truncation the fit moves by +0.47 mag in M0hat and +0.19 in sigma_M (45 and 33 prior widths); the chain
does not move off this prior, and core's completeness cannot represent the floor (true completeness about 0.65 below z
0.16 against the model's 0.99). The spectroscopic-only arm is a diagnostic; its H0 effect is not measured.

**Photo-z mock (consumer PR #24, merge 402c947; finding C070).** The photo-z mock paragraph of 12R's amendment of this
date applies to this record's calibrations: the finding shows the old ZERR lookup is wrong, so the galaxy's own bin is
now the default; `phase12u_calibrate.py --zerr-lookup legacy_next_centre` reproduces this record's calibrations, and
`config/phase12u_prep_manifest.json` now passes that option to the union and photometric parts, so the manifest keeps
producing this record's numbers.

**GW inputs (consumer PR #26, merge a152bed; findings C047, C057, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). No number of this record changes.
