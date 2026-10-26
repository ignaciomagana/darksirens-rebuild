# GW inputs of record: addendum (26 Oct 2026)

Consumer review of 24 Oct 2026, fix package P03 (GW inputs); consumer PR #26 on desi_darksirens_selection, merge
a152bed (main 402c947 after the round-3 merges); owner decisions 4D and 5B of 25 Oct 2026, 4D kept on 26 Oct 2026;
findings C047, C057, G1.1, G1.2, G8.5. Records 12AA, 12AC, 12AF, 12AP and 12AQ cite this addendum with a line of their
own; 12M, 12T, 12U, 12Y, 12AD, 12AE and 12AG to 12AO cite it in their amendment of this date. Location-free
throughout. **No number of any record changes.** The fix adds declarations, checks and a gate. No record path reads
them, except that the gated P12.1 input stage also checks spin support, and that check passes on the record's
Product A file.

**Builds read.** Records from 12T on read gwcat 8263ae9 rebuilds of Product A with exact chi_eff and dL priors. They
do not read the gwcat 8f9e2f1 pair that `config/inputs.production.json` pins for the P12.2 to P12.4 stages. Two PE
builds hold the same rows: `A_pe_chieff_bbh259_n4096_v20_exact.h5` (sha256 c6150725..., with the astropy release
cosmology) and `lalcosmo/A_pe_chieff_bbh259_n4096_v20_exact_lalcosmo.h5` (822b3181..., with the LAL release
cosmology). One selection file, `A_sel_chieffref_o3o4ab_v20_exact.h5` (56e51af2...), goes with both. The consumer
declares them, and the attributes that tell them apart, in `config/gw_inputs_of_record.json`; a test of the consumer
checks every GW pin of the repository against it (G8.5).

**PE input defects (decision 5B; G1.1, G1.2).** Both PE builds carry the critical and high input items of the gwcat
review of 2026-10-20:

- 44 mixed-waveform O4a events whose mass prior misses NRSur7dq4's mass-ratio and total-mass edge;
- 1,168 exported rows in 54 events with a spin magnitude above the selection's 0.99 reference ceiling, counted again
  from the gwcat store on both builds (4,313 store samples in 57 events), all in SEOBNRv4PHM blocks of C01:Mixed
  events;
- 57 O1-O3 events whose SEOBNRv4PHM half was sampled to a spin of about 1 but divided by a 0.99 prior.

gwcat 8263ae9 validates the pair only with a self-derived spin-prior allow-list, and that list is NOT APPROVED. The
owner keeps the files as inputs of record without approving it. The consumer's spin check now reads each PE file's
spin-support status: a file with rows above the ceiling is accepted only through its declared status, and a count
measured from the store that differs from the declared one is refused (G1.2).

Fixing these items moves the fixed-population spectral-only H0 posterior by at most 0.0016 posterior sd (sd and width
ratios within 0.03%). The replicate scatter is 0.035 sd in location and 0.6% in width, so the bound is about 20 times
below it. The two PE builds agree to 1e-4. The catalog-against-spectral comparisons of record compare like with like
at the PE level. Dropping the affected events moves H0 by as much as random drops of the same size do, which is
information loss, not bias. The 10 O1/O2 events are record 12AC's item. At the next gwcat product the PE files are
rebuilt with the spin-ceiling cut and a constituent-aware NRSur prior.

**Events resampled with replacement (C057).** GW150914_095045 keeps 2,383 distinct rows of 4,096 and GW200129_065458
keeps 1,732. Core's per-event Monte-Carlo variance treats repeated rows as independent. The true variance of these
two events is larger by 2.205 and 3.066 (the sum of squared multiplicities over 4,096).

- In the fiducial-cell grids (12AL, 12AQ stock) the two events carry at most 0.75% of the PE variance sum: the
  largest sum goes from 0.523 to 0.528 with the factors applied. In the spectral grid they carry 0.08%.
- No accepted or penalised flag changes at the limit these grids use.
- The chains (limit 4) store no per-event variances. The shares imply a change of about 0.01 against the limit of 4.

**O3 injection support (decision 4D; C047).** The O3 campaign drew source-frame primary masses on [2, 100] Msun and
z <= 1.9, but the GWTC-5 population reaches 300 Msun. mu therefore misses the O3-detectable binaries above 100 Msun.
The injection-support gate (`scripts/check_injection_support.py`; CPU; core's per-row weights, tied to core's ln mu at
every fixed-population trial point and the first posterior draws, and to record 12AQ's stored spectral grid, to
4e-15; both record environments give the same numbers) gives:

- Fixed population: -N ln mu is too large by 0.20 to 0.54 nat over the H0 prior range (0.13 nat across [50, 100]).
  Removing it moves the spectral-only grid posterior of record 12AQ by -0.012 posterior sd (sd ratio 0.999).
- Over 800 draws of the A1 posterior (record 12AA): the excess is 0.10, 0.35 and 0.99 nat (5/50/95%; largest 2.6 nat;
  4.9% of draws above 1 nat). It correlates with alpha2 (correlation -0.85) and m_break (-0.41). A first-order
  correction (reweighting the draws by exp(-N dln mu)) moves A1's H0 mean by -0.019 ± 0.008 A1 sd and its median by
  -0.038 ± 0.016 A1 sd, with sd ratio 1.010 ± 0.005; alpha2's mean by +0.22 ± 0.01 sd and its median by +0.20 ± 0.03
  sd; m_break's mean by +0.11 ± 0.01 sd and its median by +0.14 ± 0.03 sd. The errors are bootstrap errors over the
  draws (1,000 resamples). With 800 draws the median shift is the noisier of the two (its error is about twice the
  mean-shift error); for H0 it is also about twice as large.

The injections are kept (owner, 25 and 26 Oct 2026: decision 4D stays). Before any new production chain, the gate is
run on the selection file and cited. Replacing the O3 campaign by injections that reach the population's support
(decision 4A) is a deferred design: the cumulative O1-O4b mixture on disk reaches 1,000 Msun but has no sky
positions, so the owner chooses the product if and when the design is restarted (design:
`darksirens-core-data/reviews/consumer-2026-10-24/fix/notes/p03-gwinputs/design_gwcat_product_rebuild.md`).

**Outputs** (CPU, HENON, consumer commit f55624e; the merged code computes the same numbers: the later commits let the
tests pass a small Product A contract and add the median-shift error to the posterior mode's output). Under
`darksirens-core-data/reviews/consumer-2026-10-24/fix/notes/p03-gwinputs/`:

- `runs/check_gw_inputs_exact_store_f55624e.json` and `runs/check_gw_inputs_lalcosmo_store_f55624e.json` (builds,
  store counts, resampling, variance budget, campaigns);
- `runs/injection_support_1022429_f55624e.json` (12AQ environment: fixed population, 12AQ grid tie, A1 draws), with
  the median-shift errors recomputed from its stored per-draw values in
  `round3/median_shift_errors_1022429_f55624e.json` (every stored number reproduces to 1e-16);
- `runs/injection_support_e7c3007batch_f55624e.json` (12AF/12AP environment: fixed population, 12AQ grid tie).

The consumer's `./ci.sh` passed at the package's round-3 head f7ca03a in all three record environments
(`ci_logs/20261026T073442Z_f7ca03a7ff78_<env>.log`; 1411 to 1435 passed, none failed) and on the merged main 402c947
(`ci_logs/20261026T124516Z_133bc47f981f_<env>.log`; 1568 to 1592 passed, none failed).
