# Phase 12U — the DESI catalog split into its spectroscopic and photometric parts (declaration)

## Status

**DECLARED (owner, 2026-10-05) before any run. Results will be appended here.**
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

- **Step 4.** Run the spectroscopic part, the photometric part, and a
  sensitivity of the union that isolates the smooth-prior effect.
- **Compute.** ONE rita A100 job that runs every stage in order. The second
  A100 stays free.
  - The CPU preparation runs before it on RM.
  - Output goes under
    `/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12u/`.
- **Code.** Consumer branch `phase12u/split`, from `phase12t/core-repin`
  (4c44184); declared code at 65870af. It reuses the 12T environment (core
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
| **spec** | Union rows with a DESI spectrum (codes 0, 2) and M_APP <= 19.5 | Spectroscopic | The LS map times c_p (below) |
| **photo** | Every LS galaxy of the union's parent, with its photometric redshift | Photometric | The LS map |
| **union_centred** | The union | Photometric rows: centre moved (below); width unchanged | The LS map |
| **union_halfwidth** | The union | Photometric rows: ZERR halved | The LS map |

**spec.**
- **The magnitude limit.** 19.5 is the BGS Bright flux limit. Above it, BGS
  Faint targeting depends on colour and fibre magnitude, which a single
  magnitude limit cannot model. Those rows are left out.
- **The footprint.** DESI observed only part of the LS sky, and only a
  fraction of the targets there have spectra.
  - c_p is the per-pixel spectroscopic fraction (nside 64): among union
    galaxies with M_APP <= 19.5 in the pixel, the fraction with a DESI
    redshift.
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
- The kernel width, the galaxies, the calibration and the luminosity prior
  are those of the 12T union chain. Only the mean pull is removed.
- The mock diagnosis says the bias is this mean pull, about s² d ln g/dz.
  The pull at the median DESI width is about 0.004 at z 0.1 and 0.007 at
  z 0.2.
- Why centring rather than narrowing: narrowing would also make every
  photometric galaxy overconfident and change the PE Monte-Carlo guard's
  behaviour (the mock lost low-H0 points at s <= 0.0145).
- The arm is also physically motivated: the LS photo-z is a regression
  estimate of z given the photometry. If it is already unbiased given z_phot,
  the extra volume prior counts the prior twice. The kernel-centre test in
  step P2 measures this directly.

**union_halfwidth.**
- This is the owner's suggested 0.5x width. It runs last and can be dropped.
- If the mean pull is the mechanism, it should move H0 by about three
  quarters of the union_centred shift, since the pull scales as s².

## Calibration of each part

A wrong calibration would dominate any comparison, so each new catalog gets
its own. Each part is calibrated with the calibration_12q run 2 procedure
(the one P12.4 uses), generalized in `scripts/phase12u_calibrate.py`. Its
helpers are imported unchanged.

| | spec | photo | union_centred, union_halfwidth |
|---|---|---|---|
| Sample | spec rows after the quality cut and the Phase 12I mask, z in [0.02, 0.30] | the same, all rows | the union's (12T) |
| m_lim | 19.5 | 21.0 | 21.0 |
| Luminosity fit (M0hat, sigma_M) | Re-fit; redshifts exact, so no photo-z bias and no inversion | Re-fit; mock photo-z bias, then the fixed-point inversion to the true values | Not re-fit: 12T's N(-20.500, 0.199), N(0.557, 0.130) |
| Luminosity prior width | half the north–south offset | hypot(half the north–south offset, the mock bias) (12P rule) | 12T's |
| Count density (log10n0, delta) | `fit_density_selection` over [0.02, 0.30], exact; cross-check over [0.02, 0.245] | forward-modelled through the ZERR mixture over [0.02, 0.30]; cross-check over [0.02, 0.30 - 3 sigma_z(0.30)] | 12T's |
| Footprint (Omega_eff) | f_p,spec | the LS map | the LS map |
| Count ridge | re-derived | re-derived | 12T's count_ridge |

**The count ridge**, as in 12T:
- For each delta on [-3.0, 1.5], take the log10n0 whose expected count over
  [0.02, 0.30] equals the part's observed count. The expected count comes
  from the fitted model's binned counts and is linear in n0 at fixed delta.
- Fit a line a + b delta through it.
- The width sd is the rms of log10(observed / expected) over the 28 bins at
  the fit.
- The hard bounds stay [-2.4, -1.2], unless the ridge comes within 10 sd of
  them. They are then re-centred on the ridge with the same width.

**Sensitivity arms.** union_centred moves some photometric rows out of
[0.02, 0.30], which changes the observed count. The preparation records the
change. The 12T ridge is kept if the change is well below its sd of 0.034 dex.

**Control.** The same script, run on the union, must reproduce:
- calibration_12q run 2: log10n0 -1.9065 and delta 1.0475;
- the 12T ridge: a -1.815898, b -0.084675, sd 0.033846.

## Priors on (log10n0 [h-scaled], delta)

Every chain uses count_ridge: delta U[-3.0, 1.5] and
log10n0 | delta ~ N(a + b·delta, sd), truncated to the bounds above. spec
and photo use their own (a, b, sd); the two union arms use 12T's.

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

Each part's ridge range is recorded, so a flat_wide-style chain can be added
later. It is not run here.

## Stages

### CPU preparation (RM, before the GPU job; `config/phase12u_prep_manifest.json`)

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
  P3's values. The CPU smoke of that manifest then runs on RM.

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
| 7-8 | scan, then chain **union_halfwidth** (optional, last) | 7–9 h |

The estimates come from the 12T chains (6.9 to 8.9 h each on the union).
The total is about 25 to 33 h, against the 7-day limit. Resubmitting
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
- **union_halfwidth.** About three quarters of the union_centred shift if
  the mean pull is the mechanism. The scan may show the Monte-Carlo guard
  cutting low H0.
- **Kernel-centre test.** Core's kernel pull is positive and grows with s.
  If the LS photo-z are unbiased given z_phot, the measured
  mean (z_spec - z_phot) is near zero.

## Calibration values

To be added from the CPU preparation record (`phase12u/prep/`) before the
GPU job is submitted.
