# Phase 12F — selection-N_eff guard (soft, cap 10) and latest-gwcat reference-reweighting GW products for the DESI chain

Status: **PROPOSED CONTRACT CHANGE / NOT ACCEPTED / PRODUCTION PIN UNCHANGED (8bf2bec5)**

Parent science phase: `phases/12_production_analysis_contract.md`

Records this change would amend if accepted:
`phases/12_P12.4_fixed_population_desi_implementation.md` (GW input files at
lines 47-51, sampler and guard settings at 120-132, hard reliability rule at
163-171), `phases/12_fixed_population_execution_chain.md` (hard gates at 129,
TinyNS resume at 114) and `phases/12B_field_footprint_acceptance.md` (hard
gate at 218).

Previous records: `phases/12D_core_deferred_followup_contract.md` (merged as a
proposed record) and `phases/12E_a100_benchmark_campaign_record.md` (proposed;
darksirens-rebuild PR #10, open, not on `main`).

Active production core pin (unchanged by this record): `8bf2bec53ff7b557c6b930d4044008cb72008f61`

## Trigger

Measurements made after Phase 12D, before any production run, show that the
DESI chain as accepted cannot pass its own Monte-Carlo reliability gate, and
that the selection file it names uses a spin draw density that the latest gwcat
refuses for the O4ab injections. Paths below are relative to the campaign
mirror `/hildafs/projects/phy230014p/magana/darksirens_benchmark_local/reports/`.

1. **The hard guard at cap 1.0 admits no finite likelihood on the campaign's
   real product.** On Product A (defined in section 2 below) at the GWTC-5
   population centre (H0 = 67.74), the selection N_eff is 12,819.5 against the
   cap-1.0 budget N_obs^2 / (1 - sum sigma_i^2) = 78,639.9, and the total
   Monte-Carlo variance of ln L is 5.38. Both codes abort at the sampler
   preflight (0/32 finite draws). The soft guard at cap 1.0 is dominated by the
   penalty and did not converge (dlogz 37 after 544k evaluations)
   (`FINAL_REPORT.md:58`).
2. **Guard study** (`guard_study.md`). The study used Product A, dynesty, the
   fixed GWTC-5 population model, a 1-D H0 run and a 3-D population run, in
   legacy darksirens and in core. All 9 same-cap pairs of runs have bitwise
   equal samples in the two codes (`:29`).
   - Caps 10 and 20, soft or hard, give the same posteriors: shifts at most
     0.026 posterior sigma, every KS D below its 95% critical value, and
     Delta logZ within 0.2 of its error (`:32-35`, `:443-449`).
   - Cap 5 cuts the posterior at the guard wall. H0 moves from 64.73 +- 4.90
     to 73.85 +- 2.35 (+1.86 sigma), with Delta logZ = -2.42 +- 0.09.
     Reweighting the cap-10 posterior with the cap-5 penalty reproduces the
     cap-5 run (`:36-39`, `:458-475`).
   - At cap 10 the hard -inf region on the H0 grid is H0 ~ 23.4-33.2, 13 units
     below the lowest posterior sample (46.5). The soft cap-10 penalty is
     exactly zero at every 1-D posterior sample (on the measured H0 map) and at
     every cap-10 and cap-20 posterior mean (`:40-42`, `:455`, `:526-529`).
   - The hard guard at cap 1 or 2 is -inf at all 50 H0 grid points and at all
     22 posterior means. Passing it would need about 14 M detected injections
     at the centre (10-23 M; 5.6-36 M with realisation scatter) and about 20 M
     over the 1-D posterior. That is 13-19 times the current 1,067,946,
     because N_eff grows as m^0.70, not linearly (`:43-51`, `:561-575`).
3. **P12.4's own GW inputs fail the hard guard at cap 1.0 at all 14 P12.2
   probes.** At H0 = 67.74, N_eff is 46,305.66 against a threshold of
   78,466.91 (ratio 0.590), with total variance 1.594. Over the grid the ratio
   is 0.293-0.721 and the total variance 1.348-3.011. By the consumer's own
   code, P12.2 then exits 3 and the chain stops before P12.4
   (`consumer_jit_target.md:135-136`, `:146-147`). An independent review
   reproduced these numbers bitwise, and legacy darksirens confirmed them
   (`consumer_jit_target_review.md:84-94`).
4. **The two selection draw densities differ on identical injection rows.**
   - The P12.4 selection file (`selection_o3o4ab_allsky.h5`,
     gwcat-selection-1.0) replaces the per-injection spin draw with the
     isotropic chi_eff prior (the "chi_eff swap").
   - Product A's selection file (gwcat-selection-2.0, `chieff_reference`)
     divides out the campaign's exact component spin density and reweights to
     a declared isotropic, uniform-magnitude reference with a_ref = 0.99.
   - The detected rows are bitwise equal in m1det, m2det, dL, chieff, ra, dec,
     redshift and m1src. The pdraw ratio (P12.4 / A) is 0.103-32.1 (median
     0.70). The swap gives 3.6 times Product A's N_eff at H0 = 67.74: 46,305.66
     against 12,837.83 at the consumer's settings
     (`consumer_jit_target_review.md:100-110`).
   - The O4ab injected spins are neither uniform in magnitude nor isotropic
     (isotropy deviation 0.6419). The latest gwcat therefore refuses the swap
     for O4ab and builds `chieff_reference` instead
     (`phase1_gwcat_contract.md:194-206`; `phase1_gwcat_exports.md:69-70`).
     The review's reading, that the swap misstates the O4 draw density, is
     labelled an inference there (`consumer_jit_target_review.md:112`).

Owner decisions, 2026-09-26:

1. The production guard for the real 259-event chi_eff spectral analysis is
   the **soft selection-N_eff guard at `max_likelihood_variance` 10**.
2. The DESI P12.4 contract changes to that guard through this Phase 12
   contract-change record.
3. P12.4's selection draw density is **reference reweighting**, built with the
   latest gwcat (8f9e2f1) in the campaign's Product A definition: chieff PE at
   gwcat-pe-2.0 paired with a chieff_reference selection at
   gwcat-selection-2.0. P12.4's PE and selection products are rebuilt with the
   latest gwcat. The chi_eff-swap selection file is superseded.

## Frozen references

```text
legacy repository:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

reconstruction freeze (historical, unchanged):
  af2488b0ccb48c65e63cffcae306a8a4a4bfeb66

Phase-12C production core pin (active, unchanged by this record):
  8bf2bec53ff7b557c6b930d4044008cb72008f61
  tree: 18b3bf93ad506fb289e080160cbb20cbb03d58d0

companion pins (unchanged):
  darksirens-surveys  f027aef02d342041ce7259cdbf47fe689e6462f2
  darksirens-lss      3429bb2f420239bc731cc9e73e50bf5351181c14
  darksirens-lensing  43c450742b733d7b8d938116021e8ca52a31226e

GW product writer:
  ignaciomagana/gwcat master 8f9e2f12b499a6b2bf16ed938f66d020b12c44c2
  (head of master when this record was written)

consumer:
  ignaciomagana/desi_darksirens_selection main cc030f023f5fdee00caeada3af02566865dfcc72
    (the consumer file references below)
  PR #10 (jit the P12.4 target once), head 898a119abdbff13059bac4d8a555adcfcc962354:
    squash-merged 2026-09-26T03:45:49Z as main 5efa8da8c10a16c908fd5231b8b4da078f9f3b56
    (tree d96c33051730e0c5da8320e64a0054ca3506b9fe, the PR head's tree), without
    contract CI, on the owner's decision (recorded in the merge commit message)
  PR #11 (implements this record; proposed, open):
    branch phase12f/soft-guard-and-gwcat-products
```

Consumer file references below are to `main` `cc030f02`.

## Proposed change

### 1. Selection-N_eff guard: soft mode at cap 10 for the whole P12 chain

**Scope.** The change covers every stage that evaluates the GW selection term
for the primary 259-event sample:
- P12.2: the 14-point H0 probe;
- P12.3: the 241-point H0 grid. The Phase 12 contract requires P12.3 to use
  the same selection settings as the DESI comparison
  (`12_production_analysis_contract.md:69-72`);
- P12.4: the anchor, the sampler run and the posterior gates.

```text
setting                     before  after   where (consumer)
selection_neff_soft_guard   false   true    config/desi.fixed_population.json:57,
                                            config/baseline.fixed_population.json:23;
                                            hard-coded False in scripts/run_preinference_diagnostics.py:184,
                                            scripts/run_fixed_population_spectral_baseline.py:261,
                                            phase12/desi_selection.py:312
max_likelihood_variance     1.0     10.0    config/desi.fixed_population.json:56,
                                            config/baseline.fixed_population.json:22,
                                            config/diagnostics.production.json:9
soft guard refused          yes     no      phase12/desi_selection.py:201-202,
                                            scripts/run_fixed_population_spectral_baseline.py:232-233
N_eff > 5 N_obs floor       kept    kept    config/diagnostics.production.json:10
```

For an `InferenceTarget`, core takes the guard settings from the target's own
likelihood, not from `infer()` (core `inference/public.py:139-160` at
`8bf2bec5`). The switch is therefore made where the consumer builds its
target, and no core change is needed.

**What the soft penalty is** (core `selection/gw.py:346-408` at `8bf2bec5`).
Let N be the number of events, sum sigma_i^2 the summed per-event PE
Monte-Carlo variance, and

```text
T = max(5 N, N^2 / max(cap - sum sigma_i^2, 1e-12))      x = N_eff / T

hard:  -N ln mu + N (N+3) / (2 N_eff)                 if N_eff > T, else -inf
soft:  -N ln mu + N (N+3) / (2 max(N_eff, T))  -  g(x) (100 + 2 N softplus(-ln mu))
       g(x) = softplus(200 (1 - x) - 10)
```

- The soft term never returns -inf when mu is finite.
- Below about 0.95 T the penalty outweighs the -N ln mu reward it guards
  against, so the sampler is pushed out of under-sampled regions rather than
  walled off.
- Well above T the penalty falls below float64 resolution, and the soft total
  equals the hard total bitwise. The core comment puts the underflow at about
  1.05 T (`selection/gw.py:366-367`); the guard study measured exact equality
  from about 1.14 T (`guard_study.md:12`).
- Between the two is a thin boundary layer.

**What the cap means.** The cap is the total Monte-Carlo variance of the ln L
estimator, sigma^2_lnL = sum sigma_i^2 + N^2 / N_eff, that is admitted without
penalty.
- It was 1 (standard deviation 1 nat); it becomes 10 (3.16 nats).
- Core documents 1.0 as the GWTC-4.0/5.0 threshold
  (`selection/gw.py:107-112`). This is a deliberate departure from that
  convention for this analysis.
- The guard study shows the posteriors do not change between caps 10 and 20,
  or between soft and hard. It does not measure how much Monte-Carlo noise in
  ln L the analysis can tolerate (`guard_study.md:540`, `:559`).
- The realised sigma^2_lnL is 5.38 (2.32 nats) at the Product A centre, under
  every cap that admits the point (`guard_study.md:233`). On the superseded
  P12.4 inputs it was 1.594 at H0 = 67.74 (`consumer_jit_target.md:135`).

**Where the chain now fails closed.** The contract requires frozen numerical
guards to fail closed (`12_production_analysis_contract.md:66`).
- Under the hard guard, the likelihood itself fails closed (-inf), and the
  stage gates test finiteness.
- Under the soft guard, the likelihood is finite by construction, so a
  finiteness test no longer detects an under-sampled point. The reliability
  condition becomes a measured statement about the penalty at named points,
  and a stage fails if that statement does not hold.

**Re-expressed acceptance criterion.**

A point theta is **unpenalised** when, with the same data and settings, the
soft cap-10 selection term at theta equals the hard cap-10 selection term
exactly: their float64 difference is 0.0 and the hard term is finite. Every
gate records at its points: N_eff, sum sigma_i^2, N^2/N_eff, sigma^2_lnL,
T(10), N_eff/T(10) and the penalty in nats.

"Same data and settings" means one arithmetic. Both terms are evaluated from
the ln mu, N_eff and sum sigma_i^2 that the stage's likelihood returns at
theta, and the likelihood's own selection term must also be finite. A jitted
likelihood can round the same term one ulp differently from an eager
evaluation. The 12F review measured this on CPU (`p12f_review/jit_check/`):
the jitted DESI target of consumer main `5efa8da` differed from the eager hard
term by one ulp at 2 of 20 points of a synthetic fixture, at N_eff/T about
6.2. Compared that way, those points would read as penalised.

- **P12.2 exit criterion.**
  - Unchanged checks, at every probe: the exact event count, finite event
    evidences, a finite ln mu, N_eff > 5 N, and nonzero cosmology support for
    every event.
  - The two cap-1.0 checks (`total_mc_variance_within_budget` and
    `hard_selection_correction_finite`,
    `scripts/run_preinference_diagnostics.py:208-211`) are replaced by:
    - a finite soft cap-10 total at every probe;
    - the penalty recorded at every probe;
    - an unpenalised anchor at H0 = 67.74.
  - A probe with a nonzero penalty is reported, not failed.
  - Why [inference from the Product A H0 map at the campaign's settings,
    `guard_study.md:252-260`]:
    - the rebuilt products are expected to be penalised at the H0 = 30 probe
      (hard cap 10 is -inf at 28.75 and 31.25; the soft penalty there is -5,984
      and -66 nats);
    - they may carry a tiny nonzero penalty near H0 = 20 and 40 (-6.2e-10 at
      21.25, -6.8e-11 at 38.75);
    - so a "zero at every probe" rule would fail on a region that holds no
      posterior mass.
- **P12.3 grid acceptance.**
  - Every grid point must be finite under soft cap 10, and the grid posterior
    is built from the soft cap-10 total.
  - The penalty must be exactly zero at the grid posterior mean and at the MAP.
  - Two things are reported: the grid points with a nonzero penalty, and the
    posterior mass that the unpenalised terms (-N ln mu + N(N+3)/(2 N_eff))
    would put on them.
  - This replaces "all 241 points pass the cap-1.0 hard gate"
    (`scripts/run_fixed_population_spectral_baseline.py:271-277`, `:294`),
    which would fail on the H0 ~ 23.4-33.2 region [inference, as above].
- **P12.4 anchor gate** (`scripts/run_fixed_population_desi.py:312-325`). At
  (P12.3 MAP, M0hat prior mean, sigma_M prior mean) the total must be finite,
  N_eff > 5 N, and the point unpenalised.
- **P12.4 posterior gate: the owner's requirement.**
  - The penalty must be exactly zero at the accepted posterior mean, measured
    by evaluating the target's diagnostics at the mean of the equal-weight
    samples, not inferred from a map or a neighbouring point.
  - The existing check at the posterior median
    (`scripts/run_fixed_population_desi.py:347-354`) is kept, with the same
    criterion.
  - Both records are written to `results/phase12/fixed_population_desi_h0.json`
    together with the guard settings (mode soft, cap 10).

### 2. GW input products: latest gwcat, reference reweighting (Product A definition)

**Superseded** (`12_P12.4_fixed_population_desi_implementation.md:47-51`;
consumer `config/inputs.production.json:38-46`). Both sha256 values were
recomputed and the format attributes read for this record:

```text
PE         gwsamples_bbh_whitelist_all_events_final.h5   gwcat-1.0, 259 x 4096
           sha256 c7c2fd08fa1e4b32975abc670767c1ac284dfca308fd71957896ff207af2caf6
selection  selection_o3o4ab_allsky.h5                     gwcat-selection-1.0, chi_eff swap,
           n_detected 1,067,946, ndraw 944,412,448
           sha256 91f1b924f013936c7e1374e49c9a62ce05f2042a5ea44d9dc50abe7182a14abd
```

**New definition:**

```text
writer     gwcat 8f9e2f12b499a6b2bf16ed938f66d020b12c44c2
PE         gwcat-pe-2.0, spin_basis chieff, 259 events x 4096 samples, chi_eff_amax 0.99
selection  gwcat-selection-2.0, spin_basis chieff_reference, spin_reference_amax 0.99,
           O3 endo3 + O4ab, FAR < 1/yr on any search,
           n_detected 1,067,946, ndraw 944,412,448
pair       gwcat validate PE SEL --strict: 84/84 checks, exit 0
           (format 2.0 carries no contract hash)
```

**Why format 2.0.** The chi_eff analysis needs the unequal pair (chieff PE,
chieff_reference selection).
- The 2.1 pairing hash covers `parameter_space` verbatim, so this pair fails
  `xcheck_contract_hash` at 2.1 and validates only at 2.0. Upstream has not
  extended 2.1 to it (`phase1_gwcat_contract.md:10-13`; `FINAL_REPORT.md:53`).
- The only 2.1 pair that can be built on the real O3+O4ab injections is
  (component, component) (`phase1_gwcat_contract.md:190`). The DESI target
  requires the chi_eff fit columns (`phase12/desi_selection.py:211-216`).

**Build** (the commands that made the reference build;
`phase1_gwcat_ingest.md:25-47`, `:88-93`; `phase1_gwcat_exports.md:15-77`).
`D` is `.../share/GWTC-PESamples/latest/GWTC`:

```text
inputs     282 raw released PE files: GWTC-2p1 54, GWTC-3 36 (the v2 files), GWTC-4p1 88, GWTC-5 104
           O3 injections:   endo3_bbhpop-LIGO-T2100113-v12.hdf5
                            sha256 86e7e48116c75da586fd2b7dc4f059dfd135148f20523874ec7d89cdcd8993c5
           O4ab injections: samples-rpo4ab-1366933504-55469568-clipped.hdf
                            sha256 d5d28b7712097251dab554af317984bc6e571222984c1b01f8ba13d5876c0d09

ingest     gwcat ingest --glob "$D/GWTC-2p1/*.h5" --glob "$D/GWTC-3/*.h5" \
               --glob "$D/GWTC-4p1/*.hdf5" --glob "$D/GWTC-5/*.hdf5" \
               --out store.h5 --cache-dir cache
           (default --sample-sets preferred; GWOSC FAR fetched online)
           reference store: schema 1.3, 282 events,
           sha256 61fda9a8800ff6835248edf1f38ae09e1e04ad2f8ba6a28ab2571d8bfead207c

population gwcat.resolve_gwtc5_bbh_population_names(...) -> 259 names in store order,
           list sha256 fe6e33da7e8de381aaa7c95f7e2905c5e8b868206eab837aaf0074f89b8c9da6

PE         gwcat export pe store.h5 --out <PE>.h5 --format gwcat2 --parameter-space chieff \
               --event-list population_events.txt --waveform-policy mixed-first --seed 0 --nsamp 4096

selection  gwcat export selection <O3 endo3 file> <O4ab file> --out <SEL>.h5 --format gwcat2 \
               --parameter-space chieff_reference --spin-reference-amax 0.99 --far-threshold 1.0

validate   gwcat validate <PE>.h5 <SEL>.h5 --strict
```

The documented `*.h5` example glob misses the GWTC-4p1 and GWTC-5 files, which
end in `.hdf5`; the per-directory globs above are the ones that ran
(`phase1_gwcat_ingest.md:35`). The GWTC-3 concept DOI now resolves to a v3
record with different files. The rebuild must use the pinned v2 files on disk,
or `gwcat fetch --no-resolve` (`phase1_gwcat_contract.md:17`, `:245-246`;
ignaciomagana/gwcat#21, open).

**Reference build** (the campaign's Product A). The sha256 values were
recomputed for this record and match `$LOCAL/gwcat/SHA256SUMS`, where `$LOCAL`
is `/hildafs/projects/phy230014p/magana/darksirens_benchmark_local`. Copies are
at `$LOCAL/gwcat/exports/` and at
`js2a100:/media/volume/tbs/darksirens_benchmark/data/gwcat/exports/`:

```text
a24a5903a7f7da6fdcdee22f58c4c0efa76447f2cf4d581dc19ec3e60ce478a5  A_pe_chieff_bbh259_n4096_v20.h5   86,136,323 bytes
bab92babf2d6958a6ed04ee536c44fa533f5c4822ca9a22f934347a089d21ab5  A_sel_chieffref_o3o4ab_v20.h5     126,491,918 bytes
```

Properties of the reference build that carry into the rebuilt products
(`phase1_gwcat_exports.md:61-72`; `consumer_jit_target_review.md:103-104`):
- Two events are resampled with replacement: GW150914_095045 (2,383 unique
  samples) and GW200129_065458 (1,732 unique).
- Six events have an assumed, unverified uniform-detector-frame mass prior.
- The PE prior uses each event's stored cosmology, with no `--cosmology`
  override: 190 events at (67.90, 0.3065) and 69 at (67.74, 0.3075). The
  superseded gwcat-1.0 file used an Om0 = 0.3089 override.
- The 6,462 selection rows above a_ref carry zero weight.
- `writer_commit` is `unknown`, because gwcat was installed from an archive of
  8f9e2f1.

**Rebuild rule.** P12.4's products are rebuilt with the commands above, and the
result is compared with the reference build. A re-export of the 256-sample PE
file was byte-identical (`phase1_gwcat_exports.md:114`). Two attributes of the
PE file depend on how the export is run, not on the data:
- `event_list_filter` and `selection_spec` store the `--event-list` argument
  string verbatim (gwcat `catalog.py:797-800` at 8f9e2f1). The reference build
  passed
  `/hildafs/projects/phy230014p/magana/darksirens_benchmark_local/gwcat/population_events.txt`
  (read from its attributes). The PE command above, with a relative
  `population_events.txt`, writes a different string.
- `writer_commit` is `git -C <installed gwcat package directory> rev-parse
  HEAD`, or `unknown` when that fails (gwcat `validation_summary.py:80-112`).
  An editable install, or a run from the checkout, stamps the commit. A
  non-editable install, like the reference build's, records `unknown`.

The selection file stores no path. Of the two, only `writer_commit` applies to
it (attributes read from the reference build).
- Expected to reproduce both reference sha256 values [inference]: a rebuild
  from the same store, with the reference build's `--event-list` string and a
  non-editable install of 8f9e2f1. The same HDF5, h5py and zlib builds may
  also be needed (campaign environment `$LOCAL/envs/gwcat311.freeze.txt`:
  h5py 3.16.0, numpy 2.3.5).
- Any other rebuild can at best be dataset-identical. The consumer's pinned
  sha256 must then be re-pinned by a reviewed change (gate 2).

**Provenance to regenerate.** Every P12.1, resolved-input, P12.2, P12.2b and
P12.3 record made with the gwcat-1.0 files is stale. P12.2b's PE footprint
support changes because 143 of the 259 events have different PE samples. The
injection rows themselves are unchanged (`consumer_jit_target_review.md:103`,
`:106`).

**Input fingerprints.**
- Today the two GW files are fingerprinted into the resolved-input provenance
  (`scripts/prepare_standardized_inputs.py:263-264`), but no stage compares
  them with a pinned value. Only the footprint map is re-hashed before P12.4
  (`scripts/run_fixed_population_desi.py:115-124`).
- Under this record, the input contract names the rebuilt files and pins, for
  each: sha256, `format_version` and `spin_basis`.
- P12.2, P12.3 and P12.4 re-hash the live files and fail closed on any
  mismatch.
- Format and basis are pinned because a mixed 2.0/2.1 pair passes both gwcat's
  validator and the readers (`phase1_gwcat_contract.md:14`, `:285`;
  ignaciomagana/gwcat#21).

### 3. Sampler

- **dynesty for P12.4** and for any further run. TinyNS is considered broken
  until ignaciomagana/darksirens#462 (open) is debugged. That is the owner's
  decision of 2026-09-25, recorded in the Phase 12E campaign record.
- **The P12.4 TinyNS configuration does not stand as written**
  (`12_P12.4_fixed_population_desi_implementation.md:120-132`; consumer
  `config/desi.fixed_population.json:59-72`). With tinyns 3f9e1b2, the preset
  `bounded_multi` raises at sampler construction: `ValueError:
  rwalk_proposal='live-cov' has been removed`
  (`consumer_jit_target.md:116`; `consumer_jit_target_review.md:121`). tinyns
  is not in the consumer's frozen package set.
- **Proposed dynesty settings** (`REAL_DARK_READY.md:46`): nlive 1000,
  dlogz 0.1, a fixed seed, checkpointing as for production, and
  `sampler_preflight` on. The guard study's converged runs used nlive 1000 and
  dlogz 0.1 (`guard_study.md:401`).
- **Core support at the pin.** `infer(target, sampler="dynesty")` runs the
  nested preflight, then the dynesty adapter (core
  `inference/sampling.py:112-157` at `8bf2bec5`). With the soft guard, the
  preflight draws are finite whenever mu is finite. Under the hard guard at
  cap 1.0, 0 of 32 draws were finite on Product A.
- **What else changes.** The TinyNS checkpoint and resume path becomes dynesty's
  (`12_fixed_population_execution_chain.md:114`; consumer
  `PHASE12_RUNBOOK.md:106-113`, `:187`).

### What does not change

- The population preset: `brokenpowerlaw+2peaks`, fixed `gwtc5` (consumer
  `config/desi.fixed_population.json:7-10`).
- The DESI calibration block: log10n0 -2.397984028005907, delta
  0.9404729599861055, sigma_kde 0.003, z_depth 0.3 (`:18-24`).
- The magnitude-selection family and priors: m_lim 21, the M0hat and sigma_M
  truncated normals, the K(z) coefficients, and the legacy fit provenance
  (`:32-52`; P12.4 record `:78-108`).
- The footprint: `mth_map_nside128.h5`, loaded through darksirens-surveys,
  with C_p(z) = f_p Cbar(z), f_p = 0 giving dN_miss = dN_exp, and occupied but
  uncovered pixels failing closed (`:25-31`; `config/inputs.production.json:72-79`).
- The catalog: the standardized DESI union, nside 64 RING, from the declared
  native input with quality cut `M_APP <= 21.0` (`inputs.production.json:47-71`).
- The weighting: field sky weighting (`desi.fixed_population.json:23`), and the
  `WEIGHT` column copied exactly (`inputs.production.json:61-62`).
- The event policy (the full 259-event whitelist, with no DESI-support cut),
  zmax 6.0, the cosmology (H0 in [20, 140], Om0 0.3089, w0 -1, wa 0), the
  sampled coordinates (H0, M0hat, sigma_M), and the blocks 131072 and 32.
- Q/LSS stays off. The core and companion pins are unchanged, and so is the
  44-event low-z robustness pair (`inputs.production.json:81-95`).

### Gates that change

| gate | before | after | where |
|---|---|---|---|
| P12.2 exit | all 14 probes: total variance <= 1.0 and hard correction finite, plus the unchanged checks | all probes finite under soft cap 10, plus the unchanged checks; penalty recorded per probe; H0 = 67.74 unpenalised | consumer `scripts/run_preinference_diagnostics.py:184`, `:204-216`; `config/diagnostics.production.json:9`, `:13-21` |
| P12.3 grid | all 241 points pass hard cap 1.0 | all points finite under soft cap 10; mean and MAP unpenalised; penalised points reported | `scripts/run_fixed_population_spectral_baseline.py:232-233`, `:261`, `:271-277`, `:294`; `config/baseline.fixed_population.json:19-24` |
| P12.4 guard fields | `max_likelihood_variance` 1.0, soft guard false and refused | 10.0, soft guard true | `config/desi.fixed_population.json:53-58`; `phase12/desi_selection.py:201-202`, `:312-313`; `tests/test_desi_target_contract.py:97`, `:121-122` |
| P12.4 anchor and posterior gates | sum sigma_i^2 + N^2/N_eff <= 1, N_eff > 5 N, finite hard correction (anchor and median) | unpenalised at the anchor, the posterior mean and the median; N_eff > 5 N; finite | `scripts/run_fixed_population_desi.py:184-207`, `:324-325`, `:347-354` |
| P12.4 sampler | TinyNS `bounded_multi`, nlive 1000, dlogz 0.1, seed 22 | dynesty (settings fixed in the consumer PR) | `config/desi.fixed_population.json:59-72`; `tests/test_desi_target_contract.py:125`, `:130` |
| input fingerprints | GW files fingerprinted, not checked against a pinned value | sha256, `format_version` and `spin_basis` pinned; every stage fails closed on mismatch | `config/inputs.production.json:38-46`; `scripts/prepare_standardized_inputs.py:263-264`; `scripts/run_fixed_population_desi.py:103-125` |
| control text | "hard MC-reliability gates" | the re-expressed criterion above | `12_fixed_population_execution_chain.md:129`; `12B_field_footprint_acceptance.md:218`; `STATUS.md` Phase 12B chain paragraph |

### What the evidence does not settle

- The guard study used the spectral (catalog-free) likelihood on Product A.
  The DESI field target's N_eff and penalty have not been evaluated at any
  point, because the standardized catalog has not been built
  (`consumer_jit_target.md:150`). The dark target's N_eff can be higher or
  lower than the spectral one.
- The evidence covers the fixed-population 1-D and 3-D runs. In the +-5% box
  around the GWTC-5 preset, 3 of 7 population draws are heavily penalised at
  cap 10 (`guard_study.md:195-203`, `:546`), and no run above 4-D converged.
  Whether cap 10 holds for P12.5 (population marginalisation) is not settled by
  this record.
- How much Monte-Carlo noise in ln L the analysis can tolerate is not measured
  (`guard_study.md:540`).

## Acceptance gates

To accept this contract change:

1. **Consumer PRs merged under contract CI.**
   - `desi_darksirens_selection` PR #10 (jit the P12.4 target), head
     `898a119`, was squash-merged on 2026-09-26 as `main` `5efa8da` without
     contract CI, on the owner's decision. A run on its exact head can no
     longer be made. The green run on the merged `main` below covers its change.
   - The consumer PR implementing this record (`desi_darksirens_selection`
     PR #11) must be merged with a green `phase12-contract` run on its exact
     head and on the merged `main`. It carries soft cap 10 in P12.2, P12.3 and
     P12.4; the new input contract with pinned product sha256, format and
     basis; the dynesty configuration; and the updated contract tests. At the
     2026-09-26 review, PR #11 does not yet carry the dynesty configuration.
   - The workflow cannot run today: the private repository's GitHub Actions is
     blocked by billing, and runs 36190414909 and 36193148216 ended with 0 steps
     (`consumer_jit_target_review.md:147`).
2. **Rebuilt products.**
   - Both files are built with gwcat 8f9e2f1 using the commands in section 2.
   - `gwcat validate --strict` passes 84/84 with exit 0.
   - The sha256 values are recorded and compared with the reference build: the
     files must be byte-identical, or every dataset must be bitwise equal, with
     the differing attributes listed.
3. **The P12.4 builder accepts the rebuilt 2.0 pair.** Its fit-column check,
   (m1det, q, dL, chieff) at `phase12/desi_selection.py:211-216`, has not yet
   been run on a chieff_reference file. P12.2's spectral probe has been
   (`consumer_jit_target.md:139`).
4. **Regenerated P12.1-P12.3.** P12.1, the resolved inputs, P12.2, P12.2b and
   P12.3 are regenerated under the active pins with the rebuilt products, and
   P12.2 and P12.3 are accepted under the re-expressed criterion.
5. **Fixed-coordinate check at the calibration point.**
   - Build the P12.4 DESI field target on the rebuilt products, the
     standardized catalog and the footprint.
   - Evaluate it at H0 = 67.74, M0hat = -20.309781546689074 and
     sigma_M = 0.7144467727667887, with the calibration block fixed as above.
     Evaluate it again at the P12.3 MAP.
   - At both points the soft cap-10 total must be finite and unpenalised, with
     N_eff, sum sigma_i^2, sigma^2_lnL, T(10) and N_eff/T(10) recorded.
   - If the rebuilt products are byte-identical to the reference build, the
     P12.2 spectral probe at H0 = 67.74 must also reproduce the Product A
     values at the consumer's settings (Om0 0.3089, `DARKSIRENS_ZMAX` 6.0,
     blocks 131072/32, core 8bf2bec5) to 1e-12 relative.
   - The comparison uses the full-precision values
     (`p12f_consumer.md:201-209`; the 12F review reproduced them bitwise on
     CPU with jax 0.4.34):

     ```text
     total ln L, soft cap 10 (= hard cap 10)   -765.1371043921606
     N_eff                                     12837.827176048291
     sum sigma_i^2                             0.1469512815852833
     sigma^2_lnL                               5.372212463255803
     N_eff / T(10)                             1.8856566927176437
     ```

     The rounded values of `consumer_jit_target.md:139` (12,837.83, 0.146951,
     5.372) cannot be compared at 1e-12.
6. **Promotion.** This record is promoted to an acceptance record listing the
   consumer merge SHAs and trees, the CI run IDs, the product sha256 values and
   the P12.1-P12.3 record hashes.

To accept a P12.4 result under it:

7. **The dynesty run converges** to dlogz 0.1, and the penalty is measured to
   be exactly zero at the posterior mean and at the posterior median, with both
   records written to the result JSON.

## Pin decision

The Phase-12C production pin `8bf2bec53ff7b557c6b930d4044008cb72008f61` stays
the active production core pin, and no core change is required:
- The soft guard and the cap are existing options of the core likelihood
  functions the consumer calls.
- dynesty is dispatched by core at the pin.
- The jitted consumer target imports `threads_distance_table`, which exists at
  the pin (`consumer_jit_target.md:61`).
- Core main has moved on: O1 was merged as `43d273f` (`FINAL_REPORT.md:84`),
  and the partial-fixing API is open as core PR #27. P12.4 needs neither: O1
  cannot reach the consumer's target (`consumer_jit_target.md:62`).
- Whether to adopt a post-12D pin stays a separate decision
  (`12D_core_deferred_followup_contract.md`, status note).

## Open questions

1. Should the penalty also be zero at every posterior sample, or at a declared
   random subset, as the guard study checked on the 1-D map? The owner's
   requirement names only the posterior mean.
2. What threshold applies to the posterior mass that the unpenalised
   likelihood would put on P12.3 grid points with a nonzero penalty? Is the
   H0 = 67.74 anchor, or the P12.3 MAP, the right P12.2 point to require
   unpenalised?
3. Must the rebuilt products be byte-identical to the reference build, or is
   dataset-level identity enough? Should the consumer consume the campaign's
   Product A files directly?
4. The PE prior cosmology: Product A uses each event's stored cosmology, and
   the superseded file used an Om0 = 0.3089 override. This record adopts the
   Product A definition, with no override. Please confirm.
5. GWTC-3 v2, which the reference build used, or v3, which the concept DOI now
   resolves to? Moving to v3 would change the reference sha256.
6. The 44-event low-z robustness pair keeps its own files. Should it also be
   rebuilt under reference reweighting?
7. The dynesty sampling method and settings, and pinning the dynesty version in
   the frozen set (the campaign used 2.1.4).
8. Should cap 20, or the hard guard at cap 10, be declared a P12.6 robustness
   variant, alongside the "PE/selection Monte Carlo variance gates" already
   named there (`12_production_analysis_contract.md:78`)?
9. Does cap 10 carry over to P12.5 (population marginalisation)? See "What the
   evidence does not settle".

## Verdict

**Not accepted.** This is the proposed contract change that carries the
owner's decisions of 2026-09-26 into the Phase 12 DESI chain. Until the gates
above are met, the accepted chain keeps the hard guard at cap 1.0 and the
gwcat-1.0 inputs, and on those inputs it stops at P12.2. The production core
pin stays `8bf2bec5`.

## Where the evidence lives

Hildafs mirror `/hildafs/projects/phy230014p/magana/darksirens_benchmark_local/reports/`
(the campaign root is `js2a100:/media/volume/tbs/darksirens_benchmark/reports/`).
sha256 of each report when this record was written:

```text
1a6ec80190cb02e9596d5cff7c62542079bb26bba5b02fc8911b95d3941383cb  guard_study.md
feb4f94edd0370f02535a9094372bc034f1994b33875364ca5822750b06ee8c2  consumer_jit_target.md
a5320df32920e2fcdb8cbc2f250a9fa9cbecc12f611318375a233d12940421bb  consumer_jit_target_review.md
7c86d2461d6c68046df61c9223ded7ee67cc9fe63f43045a6d3225ad63fca532  phase1_gwcat_contract.md
5a1ade87cf1ac084037874a3f2ad83a88beeeb3e5339ed1e7699f2ffc944813c  phase1_gwcat_exports.md
20c1e548e8f1f4b858c9ef51fb7d59571251e37d93e0421d4a31d0b80afa9a39  phase1_gwcat_ingest.md
9b20122db1a03ff842e6bd4d14303ca4a24ba891da52862f180e7d358d491af1  FINAL_REPORT.md
4d494efee2a1d8bdc6a9ee707a2915882c6e3e4e6f41286bfe956ce511be73e0  REAL_DARK_READY.md
```

Added by the 12F review (2026-09-26). Paths are relative to the campaign mirror
`/hildafs/projects/phy230014p/magana/darksirens_benchmark_local/`:

```text
30587e56e391aeee218798d109c2bcd1368371799346a0672d35f315fd55d4b3  reports/p12f_consumer.md
cf25b2fb0a359b5fa78dee07544a8c3f368b92175502ec4ee88832e3c7e7c564  p12f_review/fixed_coord/fixed_coord_review.json
c5a842e9654069a8ba7d5dbd7c3bdb10fa908543f3f93a9c784502c3a5862112  p12f_review/jit_check/jit_unpenalised_check.json
```
