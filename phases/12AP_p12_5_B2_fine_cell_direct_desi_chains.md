# Phase 12AP — P12.5: stage B2's direct DESI chains at the fiducial cell, nside 128 and sigma_kde 1e-3 (declaration)

## Status

**RESULTS (27 Oct 2026).** The four chains finished on 25 Oct 2026; the estimator error and the comparison at a common
guard and without the guard (owner decisions 7A and 6B) were attached on 27 Oct 2026. The location-free numbers are
under "Results (27 Oct 2026): against B2 with its estimator error, at a common guard and without the guard" at the
end; absolute values are on the owner page only.

**DECLARED (owner, 2026-10-21), before any chain.** No 12AP chain has run. This record fixes the question, the
changes against stage B2 (record 12AF), the inputs with their sha256, the checks before the go, what is reported
and the compute. The checks are recorded under "Results: before the chains" as they finish. The main session
launches the chains on the owner's go, with the commands under "How it runs".

**Checks 1 to 6: passed (2026-10-21, 13:30 UTC).** Check 1 needed one fix, to the help text of a new script;
nothing in the chains changed. The launch commit is 2c06a3d; see "The gate" at the end.

**Blinding: location-free.** No H0 location appears here, in commit messages or in the logs agents read: no median,
interval, MAP or shift in km/s/Mpc. The H0 values in this record are fixed a priori: the split prior's bounds (20,
45, 140), the start points 32.5 and 92.5, and the tie points of check 3 (20, 32.5, 45, 60, 70, 80, 92.5, 110, 125,
140). Results are appended at the end later, as in 12AF: absolute values go to the owner page only, never to the
clean-room session or to a coordinator.

**The owner's reporting rule (2026-10-20) replaces 12AF's bands and its bootstrap agreement test.** Posteriors and
their differences are reported as numbers (shift in sd, width ratios, the lower part's weight). No bands,
thresholds, z-scores or verdicts.

**Results wait (independent review, 25 Oct 2026).** The results of this record wait for an estimator error on the
comparison against B2 and for a guard-free comparison (owner decisions 7A and 6B). See "Amendment (25 Oct 2026):
independent review" at the end.

## The question

Stage B2 (12AF) sampled H0, the three catalog nuisances and all seventeen GWTC-5 population parameters directly
against the DESI union target at the production cell, nside 64 and sigma_kde 3e-3. The owner's fiducial cell is
nside 128 and sigma_kde 1e-3 (owner, 2026-10-20: nside 64 is out). This record asks what the population-free DESI
posterior is at that cell: the same four chains, the same target, priors and sampler, on the nside-128 union with
the finer kernel. It is read against B2 (the same posterior at the production cell), B1 (B2's target by reweighting
A1) and A1 (spectral only).

What 12AG to 12AN measured at this cell, at the fixed calibration and population (location-free, for context; not a
reading of this record):

- 12AG: on the coarse grids no cell of the ladder narrowed H0 against spectral only.
- 12AL (as 12AM sums it up): under core's stock per-pixel target (D0, the target of B2 and of this record) the
  nside-128 cells were wider than spectral only (R 1.15 to 1.16), and the sky-averaged density D2 removed that
  widening; it came from the selection Monte-Carlo noise, not from information. The owner withdrew sky-averaging (2026-10-20), so this
  record keeps the stock per-pixel selection term, as B2.

## What changes against B2, and only this

| | B2 (12AF) | 12AP (this record) |
|---|---|---|
| catalog | the union at nside 64, `phase12u/inputs/catalogs/desi_union_nside64.h5` | **the union at nside 128**, `phase12_5/smearing_ladder/catalogs/desi_union_nside128.h5` (the file of 12AG to 12AO; build record `build_nside128.json` beside it) |
| footprint | `phase12t/inputs/mth_map_nside128.h5`, degraded equal-area to nside 64 by the loader | **the same file at its native nside 128** (the loader uses it as it is, as 12AH's Lane A) |
| kernel smoothing sigma_kde | 0.003 | **0.001** |
| log10 n0 prior | N(−1.810518, 0.036361) truncated to [−2.346, −1.146]: the union's count ridge at δ = 0, derived at nside 64 (preset `count_ridge_union_delta0`) | **the same recipe on the nside-128 catalog and footprint** ("The log10 n0 prior" below) |
| H0 comparison | against A1, with B1 beside; 12AB bands and a bootstrap test | against B2, B1 and A1, numbers only |
| outputs | `phase12_5/B2/` | `phase12_5/B2_fine/` |
| GPUs | Jetstream2 H100 (two chains) and the MIKO H100 NVL (two chains) | **the Jetstream2 H100 only**, the four chains one after another (MIKO is not used) |

The catalog has the same galaxies at both nsides: 12AG's gate G1 checked that the sorted rows of every nside equal
the native rows after the cuts (22,785,279 galaxies), and G2 that every galaxy sits in a child of its nside-64
pixel. Only the pixelation changes.

**Everything else is B2's:**

- **Target:** the 21-dimensional B2 target (12AF "The target"): H0 with the split prior 20 to 45 and 45 to 140,
  M0hat, sigma_M, log10n0_q and the seventeen GWTC-5 population parameters with A1's priors, read from
  `config/spectral_joint.json`; magnitude-limited Gaussian completeness times the per-pixel footprint fraction,
  z_depth 0.245, δ fixed at 0, flat ΛCDM with Om0 0.3089; M0hat N(−20.4997, 0.1987) and sigma_M N(0.5575, 0.1299)
  as 12Y.
- **Selection term:** core's stock per-pixel production target, as B2.
- **Guard:** variance limit 4 with the smooth guard (`selection_neff_soft_guard`).
- **Kernel pin:** auto (owner-approved for B2; equal to pin off to about 1e-12, not bitwise; a checkpoint never
  resumes across pin settings).
- **Sampler:** dynesty 2.1.4, bound multi, random walk, walks scaled (126 steps), nlive 1000, dlogz 0.1, call cap
  20 million, checkpoint every 30 minutes; core's batched pool at Q = 32 in the rows form (every value is the
  single-point value bit for bit; the chain is dynesty's own `queue_size=32` chain).
- **Seeds:** upper part 41 and 42, lower part 31 and 32. The parts are combined by evidence (prior mass times
  evidence, each part's ln Z the mean of its seeds'), with A1's `combine`.
- **Env and core:** `consumer_e7c3007batch_cuda12` (core e7c3007 with the 32c6210 backport of the batched pool).
- **GW inputs:** the LAL-consistent PE build (259 events, 4096 samples each) and the O3/O4 injections.

## The log10 n0 prior

B2's prior is the union's count ridge at δ = 0 (`phase12u_calibrate.py`, Phase 12U, run 2026-10-06; output
`phase12u/inputs/calibration/union.json`). For each δ on [−3, 1.5] the recipe finds the log10 n0 whose expected
count over z in [0.02, 0.30] equals the observed count, fits a line a + b δ through it, and takes sd as the rms over
the 28 bins of log10(observed/expected) at the density fit. At δ = 0 the prior is N(a, sd). The bounds are 12T's
(−2.4, −1.2), or, when the ridge ± 10 sd leaves them (as for the union), the ridge's centre ± 0.6 dex rounded to 3
decimals.

**The recompute.** The same script, imported unchanged, with its pixel resolution `NSIDE` set to 128 instead of 64
(`scripts/phase12ap_count_ridge.py --nside 128`): each galaxy's pixel index and the footprint fraction map are then
taken at nside 128, the map at its native resolution. It runs on the native table, as the 12U run did, with the same
cuts, the 12I mask judged at native nside 128, the luminosity fit, the photo-z mock with its fixed seeds and the
inversion. The nside-64 derivation is repeated in the same way beside it, so a difference can be told from a change
in the code or the environment (env `consumer_e7c3007_cuda12`, the 12U run's).

**Expected before the run.** In `darksirens_surveys` (the env's copy), `fit_density_selection` and
`density_completeness_curve` use the footprint only through its effective area, 4π/N_pix × Σ f_p, and the pixel index
only to refuse a galaxy in a pixel with f_p = 0. The effective area is 7.020816552786891 sr at nside 64 and
7.020816552786892 sr at nside 128 (one unit in the last place). The recompute should therefore return B2's prior.

**Rule.** Both priors are reported. If they differ by more than 0.5 prior sd in the mean or the sd, the checks do not
start and the owner decides. If they agree at the preset's precision (6 decimals in a and sd, the bounds as written)
the chains keep the preset `count_ridge_union_delta0`. Otherwise the re-derived prior is written into the
configuration inline (`scripts/phase12ap_make_manifest.py` decides by that rule).

## Inputs (sha256)

Paths under `/hildafs/projects/phy230054p/magana/darksirens-core-data` unless absolute.

| input | path | sha256 |
|---|---|---|
| union catalog, nside 128 (chains) | `phase12_5/smearing_ladder/catalogs/desi_union_nside128.h5` | `f26a20f0f3f8ca5a9bc0aee0681cd0eba6f1a7b693055839cba83d6189cdb62c` |
| its build record | `phase12_5/smearing_ladder/catalogs/build_nside128.json` | `e8e960586ac675c685354c1f98bfb2852d0d0d6e65941523596c02602e9dbb62` |
| footprint, native nside 128 (chains) | `phase12t/inputs/mth_map_nside128.h5` | `1e4e5c675dd59ab29dcaa9c3c748bd858af81bc89147cf0a40726c5303ba6b43` |
| GW PE, LAL-consistent build (chains) | `phase12t/gwcat_exact/lalcosmo/A_pe_chieff_bbh259_n4096_v20_exact_lalcosmo.h5` | `822b3181f55dd1d6d8e0dbdeba5901cb382c3f77f18e1c96ecf0a8ae1a23a075` |
| O3/O4 injections (chains) | `phase12t/gwcat_exact/A_sel_chieffref_o3o4ab_v20_exact.h5` | `56e51af209c999059c721d8c379d43eab9f4edef1700f36288e1fcf5e1fe49b6` |
| GW PE, exact-prior build (check 3 only, Lane A's) | `phase12t/gwcat_exact/A_pe_chieff_bbh259_n4096_v20_exact.h5` | `c61507251609cb6987bf0290ac45c10e059ea313e3f4d38dde57dbcf0c8d26dc` |
| native table (the n0 recompute) | `/hildafs/projects/phy230014p/magana/desi_darksirens_selection/final/experiments/experiment_loa_rebuild/inputs/rebuild_loa_faint_pixelate_input.h5` | `42e91b594572cfba716d0128ea3dcb24924a6c63e573078e7c4184fe24c0eaaa` |
| B2's n0 prior's source | `phase12u/inputs/calibration/union.json` | `dab0f1c4576e7ea1f9377d2e9d742efcd82bc41f5b8e7e2a9cf6054e3e4f81a2` |
| A1 chain configuration (population priors) | `config/spectral_joint.json` (consumer branch) | `3633109fcf9c303b8fa38c55822f7c3852ed18dcb99e77d5c4472b4df7e1f79d` |
| DESI base configuration | `config/desi.fixed_population.json` (consumer branch) | `b79ad777f17126bcd78b9ebcff0d02724ae6cfe7ae957829009ca5143f349bb9` |
| B2 combination (reference) | `phase12_5/B2/runs/combined/combined.json` | `f99a8a9e0b312fa109e6aedcf263d880412841bb260cc0b1899f8d6baaeb9779` |
| B1 summary (reference) | `phase12_5/B1/summary/summary.json` | `9236929db625e5351c7a88028f673f05939f3084f807f77de931f7853c2fbd83` |
| A1 combination (reference) | `phase12_5/A1/runs/combined/combined.json` | `05ea9b52b2830fc34495d5e60be0600068ff2593243099593450ab20df9f6bf5` |
| Lane A at nside 128 / 1e-3, 12AL (check 3, primary) | `phase12_5/selection_denominators/runs/ns128_sk1e-03/lane_a/scan.json` | `5a0530d64fa552beb9a510ecfea2958e9e57fa2b7bdddbbb6f917305531cdf21` |
| Lane A, 12AM (check 3, beside) | `phase12_5/d2_ladder/runs/ns128_sk1e-03/lane_a/scan.json` | `faabe1c4a6264c6ceded5abae38ae1fd2c6229c886a33158a0b207a213efce7b` |
| Lane A, 12AN (check 3, beside) | `phase12_5/d1_d4_fine/runs/ns128_sk1e-03/lane_a/scan.json` | `a7bf471d4850701abee05a761cab542a0cb7ab18a4ef01c98551280509ace95a` |
| 12AG coarse grid (check 3, beside) | `phase12_5/smearing_ladder/runs/ns128_sk1e-03/scan.json` | `12b2c2b2d4edff4233b84f1b873d172d7dfced9235981b437e1d28c86a1638ce` |

The four chain inputs are listed in the manifest's `input_checksums`; the runner refuses a chain whose input does
not match. **On js2h100** the five GW, catalog and footprint files are synced into its mirror and checked by sha256
on both sides by the runner (`B2_fine/logs/sync_sha256.{hildafs,js2h100}.txt`), with the same clean commit of the
consumer clone and the same batch env (pip freeze and core's sources).

## Code and environment

- **Consumer:** `ignaciomagana/desi_darksirens_selection`, new branch **`phase12ap/fine-cell`** from B2's
  `phase12.5/direct-desi` (78b84f9), in the clone `phase12_5/repo_12AP`. Committed locally, not pushed. It adds,
  without changing any B2 file:
  - `scripts/phase12ap_count_ridge.py`: the count ridge at a given nside (above);
  - `scripts/phase12ap_make_manifest.py`: the 12AP manifests derived from B2's with the changes above only
    (`--check` verifies the committed files);
  - `config/phase12ap_fine_cell_manifest.json` and its 8-live-point CPU smoke twin;
  - `scripts/phase12ap_compare.py`: against B2, B1 and A1, numbers only;
  - `scripts/phase12ap_checks.py`: checks 2, 3 and 4;
  - `slurm/phase12ap_run_js2h100.sh` (copy at `B2_fine/run_12ap.sh`), `slurm/phase12ap_js2h100_chains.sh`,
    `slurm/phase12ap_check5_timing_js2h100.sh`, `slurm/phase12ap_{count_ridge,pytest,smoke}_henon.sbatch`;
  - `tests/test_phase12ap.py`: the manifests are the generator's output and differ from B2's only as declared; the
    comparison, the ridge wrapper, the tie comparison and the chain order.
- **Env:** `phase12t/envs/consumer_e7c3007batch_cuda12` on Hildafs and on js2h100 (identical by pip freeze and core's
  sources). Nothing is installed into it.
- **Record:** `ignaciomagana/darksirens-rebuild`, branch `phase12ap/declare` from main (5595c54), clone
  `phase12_5/rebuild_12AP`. Committed locally, not pushed.

## Checks before the go

12AF's checks, adapted. Each result is recorded below before the go. Outputs in `phase12_5/B2_fine/checks/`.
12AF's check 5 (Q = 32 against a queue of 1) is not repeated: it tests the sampler, which is unchanged.

1. **Unit tests (CPU, HENON):** the full suite on the new branch in both envs, as 12AF check 1 (the batch env, where
   the core-pool tests run; the e7c3007 env, where they skip and the driver's refusal runs). Pass: no failure; the
   skips are the expected ones of 12AF.
2. **The pin on the new target (GPU):** pin auto against pin off at 16 prior draws and 16 points near the reference
   population per H0 part, single calls. Pass: largest |Δ ln L| ≤ 1e-9 and the same non-finite pattern (12AF's rule).
   Core's vmapped batch of 32 is reported beside; it is not the chains' form.
3. **A tie to a measured result (GPU):** at the 12AG ladder calibration (M0hat −20.4975, sigma_M 0.5592, log10 n0
   −1.8216) and Phase 12's fixed population (the reference population: GWTC-5 values with spin 0.04 and 0.10), the
   new target's ln L at the ten tie points must equal 12AH Lane A's at nside 128 / sigma_kde 1e-3 (259 events, 641
   points; 12AL's run is the primary reference). The tie runs the new target with Lane A's GW input (the exact-prior
   PE build), variance limit 20 and pin off, the three settings in which Lane A differs from the chains; pin auto is
   reported beside. In the same process it also builds Lane A's own fixed-population target on the same inputs.
   - **Pass:** the new target (pin off) equals the same-process fixed-population target to 1e-10, and Lane A's
     stored values to 1e-6 (12AG control C1's tolerance across cards; Lane A ran on A100s), in ln L, ln μ and
     relative N_eff, with the same flags; the population anchor equals the fixed population exactly.
   - Only ln L differences and the H0 values are read: the GPU step writes the absolute values to a file that only
     the comparison reads (`checks/tie/tie_values.json`); `checks/tie/tie*.json` hold differences only.
4. **The start check at limit 4 (GPU):** the reference population with the nuisances at their prior centres at the
   start H0 of each part (32.5 and 92.5), both pins. Pass: unpenalised and accepted. A part that fails does not
   start; the owner decides.
5. **GPU timing and memory on js2h100:** the real chain command for minutes in scratch directories: one chain alone
   (high_seed41), and two at once (high_seed41 with low_seed31), each for 300 s of sampling after its setup. It gives
   the seconds per call, the chain process's and the GPU's peak memory and the GPU use, against B2's 26 ms per call
   alone and 32 ms in its js2h100 chain (both in dynesty's first, unit-cube phase), and the summed calls per second of
   two chains against one. A single-call timing of the target is run beside.
6. **CPU smoke at 8 live points (HENON):** the four-chain smoke manifest and the combination with the comparison, as
   12AF check 7.

## What is reported

Per chain, per H0 part and for the combination, as 12AF ("What is reported"), and against each of B2, B1 and A1:

- **H0:** median, 68% and 90% intervals, sd (the absolute values on the owner page only).
- **Differences:** the shift of the median in the reference's sd, (median − median_ref) / sd_ref; the sd ratio; the
  68% and 90% width ratios.
- **The lower part's weight** (H0 20 to 45): the combination's, the two matched pairs' and the range over the four
  pairings, beside B2's, B1's and A1's.
- **Every sampled parameter:** median and 68% interval, and its shift in B2's sd and sd ratio against B2.
- **Evidence:** each chain's ln Z and error; per part, the seeds' difference.
- **The variance limit:** the fraction of samples it penalises; the selection N_eff over its threshold at the
  posterior mean, median and best point.
- **Convergence and cost:** final dlogz and stop reason, iterations, calls, evaluated points, wall time, seconds per
  call and per evaluated point; the resolved kernel pin and its digest.

`compare/compare.json` holds the location-free numbers; `compare/compare_absolute.json` the absolute ones. No band,
threshold or verdict is attached. A difference is stated with its size and direction, beside B2's own seed scatter
(B2's two upper-part seeds and the lower-part weights of its two matched pairs).
*(26 Oct 2026: added: the paired-bootstrap estimator error of every 12AP-against-B2 number, the comparison at a common
guard and without the guard with the walled share, per-part readings and the guard sample's fractions (findings G6.1,
G6.2, C013, C068); see "Amendment (26 Oct 2026): independent review, round 3".)*

## Compute

**Where:** the Jetstream2 H100 80GB (`ssh js2h100`; billed by the hour, idle when this was declared). The four
chains run one after another in the tmux session `ap_fine`: high_seed41, low_seed31, high_seed42, low_seed32. A first
combination is possible after the first two (one seed per part). MIKO is not used.

**The estimate** (revised under check 5):

- B2's chains (12AF results) made 4.70 to 5.00 million calls (3.45 to 3.78 million evaluated points) in 42,291,
  40,111, 42,389 and 40,192 iterations. On js2h100 they took 32.5 h (upper, seed 41) and 30.0 h (lower, seed 31) of
  sampling: 29.1 and 29.4 ms per evaluated point in the likelihood, 23.4 and 22.9 ms per dynesty call (calls outside
  the unit cube cost nothing), 1.8 to 1.9 h per chain outside the likelihood.
- A 12AP chain is estimated as B2's js2h100 chain scaled by the ratio of the per-call times measured in check 5 at
  the same phase on the same GPU (12AP over B2's 32 ms), plus the setup. The iterations are assumed to be B2's: the
  posterior's information is expected to be similar (to be seen).
- **Two chains at once:** if check 5 shows that two chains at once give more calls per second than one, the session
  can run in pairs (`pairs` mode: high_seed41 with low_seed31, then high_seed42 with low_seed32). Default: one after
  another, as declared. The owner chooses.

## How it runs

```
B=/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B2_fine
$B/run_12ap.sh js2h100            # sync, checks, then tmux session ap_fine on js2h100 (serial; "pairs" as 2nd argument)
nohup setsid $B/run_12ap.sh combine > $B/logs/run_12ap_combine.out 2>&1 < /dev/null &
$B/run_12ap.sh status             # any time, reads only
```

- `js2h100` mode: preflight (clean clone, the runner is the committed copy, the committed manifests are the
  generator's output for the re-derived ridge, the runner's dry run), refuses a busy GPU, syncs and checks the inputs
  by sha256 on both sides, the commit and the env, then starts `ap_fine` and returns. A chain with DONE is skipped; a
  stopped chain resumes its own checkpoint.
- `combine` mode: a code watcher (ssh every 10 minutes, no LLM). When the session's log ends `EXIT=0` it copies the
  four chain directories back, checks every file by sha256, and runs the combination and the comparison on HENON CPU
  (srun). It ends `AP DONE rc=<rc>`.

## Limits, stated in advance

- As B2: two seeds per part; one variance limit (4); the pin not bitwise; δ fixed at 0; the spin model; the luminosity
  function, m_lim, the depth and the footprint not varied.
- **One cell.** This record measures the population-free posterior at nside 128 / sigma_kde 1e-3 only. A difference
  against B2 is the joint effect of the two settings; it does not separate nside from sigma_kde.
- **The selection noise at nside 128.** Under the stock per-pixel target the nside-128 cells carried more selection
  Monte-Carlo variance than nside 64 (12AL). At limit 4 with the smooth guard this can change the fraction of
  penalised samples against B2's. It is reported.
  *(26 Oct 2026: measured: at this cell the wall lands on about a fifth (upper part) and two fifths (lower part) of
  B2's posterior draws, against under 1% at B2; the walled fraction and the guard-free comparison are reported instead
  of the penalised fraction (findings G6.2, C068); see "Amendment (26 Oct 2026): independent review, round 3".)*
- **The estimate assumes B2's iteration counts.**

## Results: before the chains (2026-10-21)

Recorded before any 12AP chain. No H0 value is quoted here. Paths relative to `phase12_5/B2_fine/`.

### The log10 n0 prior — recomputed; equal to B2's

HENON jobs 1391047 (nside 128) and 1391048 (nside 64 repeated), consumer 3b638a0, env `consumer_e7c3007_cuda12`, 27
and 26.5 minutes. Outputs `inputs/calibration/union_nside{128,64}.json` (sha256 `9e48c95f…a57a` and `a8b1dbb2…21ba`).

| | a (the mean at δ = 0) | b | sd | bounds | footprint nside, Σ f_p |
|---|---|---|---|---|---|
| B2's prior (12U run, 2026-10-06) | −1.8105180913918975 | −0.08944896694398258 | 0.03636106345065229 | [−2.346, −1.146] | 64, 27461.16486555487 |
| the recipe repeated at nside 64 | −1.8105180913918975 | −0.08944896694398258 | 0.03636107071569033 | [−2.346, −1.146] | 64, 27461.16486555487 |
| **the recipe at nside 128** | **−1.8105180883934107** | −0.08944896672067851 | **0.036361083914024636** | [−2.346, −1.146] | 128, 109844.6594622195 |

- **nside 128 against B2's prior:** the mean differs by 3.0e-9 dex (8e-8 prior sd), the sd by 2.0e-8 dex (5.6e-7 prior
  sd); the 91 ridge points by at most 3.4e-9 dex; the bounds are the same. Far below the 0.5-sd stop rule, so the
  checks went ahead.
- **At the preset's precision they are equal** (a −1.810518, sd 0.036361, bounds as written), so the chains keep the
  preset `count_ridge_union_delta0`: **12AP's log10 n0 prior is N(−1.810518, 0.036361) truncated to [−2.346, −1.146],
  as B2's.** `scripts/phase12ap_make_manifest.py --check --ridge inputs/calibration/union_nside128.json` confirms the
  committed manifests.
- The repeat at nside 64 reproduces a and b bit for bit and sd to 7e-9 (2e-7 prior sd); the luminosity inversion's
  result is bit for bit B2's. The nside-128 run moves the luminosity inversion by 4e-9 in M0hat: the effective area
  changes in its last digit and the mock's fit follows it. That is the whole effect of the nside, as expected.

### Copies of the js2h100 check outputs

The outputs of checks 2 to 5 were written on js2h100 and copied to Hildafs `checks/` (40 files), identical by sha256 on
both sides (`logs/checks_sha256.{hildafs,js2h100}.txt`). The sequence (`checks/logs/checks_js2h100.out`, consumer
aabf05b, clean) ran 12:33 to 13:04 UTC: pin and start check 343 s, the tie's values 322 s, the single-call timing
163 s, one chain alone 493 s, two at once 535 s, each exit 0.

### 1. Unit tests (CPU, HENON) — passed after one fix

- **The full suite at aabf05b** (`logs/pytest-1391052.out`, `logs/pytest-1391053.out`):
  - batch env (core 32c6210): job 1391052, 501 passed, 2 skipped, **1 failed**;
  - e7c3007 env: job 1391053, 492 passed, 11 skipped, **1 failed**.
- **The failure was 12AP's own, the same test in both envs:** the scripts' entry-point contract
  (`tests/test_script_entrypoint_contract.py`) runs every script in `scripts/` with `--help` alone and expects the
  usage text and exit 0. The new wrapper `scripts/phase12ap_count_ridge.py` refused `--help` without `--nside`
  ("--nside is required"). The script is new in 12AP, so this is not a failure carried over from B2's commit.
- **The fix (85073e2):** `--help` alone now prints the wrapper's usage and exits 0. With `--nside` the wrapper runs
  `phase12u_calibrate.py` exactly as before; without `--nside` (and without `--help`) it still refuses. Only the
  help path changes. No chain input, manifest, setting or target changes, and the chains never run the wrapper. The
  n0 recompute above ran with `--nside` and is unaffected. `tests/test_phase12ap.py` now also covers `--help` alone.
- **The rerun at 2c06a3d** (the launch commit; the runner change under "Code changes after the declaration"): the
  contract file and `tests/test_phase12ap.py`, **41 passed in each env** (HENON jobs 1391082, batch env, and 1391083,
  e7c3007 env; `logs/pytest-fix-2c06a3d-{batch,old}.out`). A first rerun at 85073e2 gave the same result but ran on
  miko as a short CPU step of the holder job, because srun inherited the session's allocation. The HENON rerun
  supersedes it.
- **The skips are 12AF's.** In the batch env there are 2: the frozen-stack gate refuses this env on the darksirens
  commit, and the frozen-core field-pin test skips on core 32c6210. In the e7c3007 env there are 11: the core-pool
  tests of `test_direct_chain_jit.py`, which need the pool. That is 12AF's 9 at 70a0731 plus the two kernel-pin
  resume cases added at 78b84f9.
- **The full suite at 2c06a3d** was resubmitted as a confirmation: HENON jobs 1391084 (batch env) and 1391085
  (e7c3007 env), `logs/pytest-<job>.out`. It is recorded when it ends. Against aabf05b's full run, the only changes
  are the wrapper's help path and the combine step's srun.
  *(26 Oct 2026: it passed: job 1391084 502 passed, 2 skipped; job 1391085 493 passed, 11 skipped; exit 0 in both
  (finding C067); see "Amendment (26 Oct 2026): independent review, round 3".)*

### 2. The pin on the new target (js2h100 H100) — passed

`checks/pin_start/pin_start.json`, at aabf05b. In each H0 part, 16 prior draws and 16 points near the reference
population, with H0 uniform in the part. Single calls, pin auto against pin off; core's batched form (batches of
32) is reported beside.

| H0 part | finite (both pins) | non-finite pattern | largest \|Δ ln L\|, single | largest \|Δ ln L\|, batches of 32 | bitwise equal, single |
|---|---|---|---|---|---|
| 20 to 45 | 29 of 32 | equal | 8.0e-13 | 1.1e-13 | 21 of 32 |
| 45 to 140 | 29 of 32 | equal | 1.1e-13 | 9.1e-13 | 31 of 32 |

- All are within 1e-9.
- **The pin:** digest `0c32ede0dc9b097e814c231eccdc1f48` (catalog_digest; B2's `0a1bcf7a…` belongs to the nside-64
  catalog). It holds 2.44 GB (B2: 1.35 GB) and builds in 74 s.
- **Per single call:** 20.4 ms with the pin and 158 ms without it.
- **The target:** 259 events with 4,096 samples each, a kernel window of 774 slots, and 196,577 compact rows (pixels)
  holding 22,782,073 galaxies. The 3,206 galaxies in the 19 occupied nside-128 pixels that no PE sample or injection
  falls in are outside the compact view, as in 12AG to 12AL. This is exact for the estimator, since such a galaxy
  contributes to no term. B2's nside-64 view held all 22,785,279.

### 3. The tie to Lane A (js2h100 H100) — passed

`checks/tie/tie_vs_{selection_denominators,d2_ladder,d1_d4_fine,smearing_ladder}.json` hold differences only.
`checks/tie/tie_values.json` holds the absolute values and is read only by `tie-compare`. The tie used the ten tie
points and the new target with Lane A's three settings (the exact-prior PE build, limit 20, pin off), at the 12AG
calibration and Phase 12's fixed population.

| comparison | largest \|Δ ln L\| | largest \|Δ ln μ\| | largest relative Δ N_eff | flags |
|---|---|---|---|---|
| new target, pin off, against 12AL's stored Lane A (primary; rita A100, 198046c) | 9.1e-13 (7 of 10 bitwise) | 3.6e-15 | 6.9e-15 | equal |
| the same against 12AM's (rita, 54d9815), 12AN's (twig, cb7c638) and 12AG's coarse grid (twig, 6337a56) | the same values | the same | the same | equal |
| new target, pin off, against Lane A's fixed-population builder in the same process | 0 (bitwise at all 10) | 0 | 0 | equal |
| new target, pin auto, against pin off | 1.1e-13 | 0 | 0 | equal |

- **Pass:** within 1e-10 in the same process and 1e-6 against the stored values. log10n0_q equals the reference's,
  and the population anchor equals the fixed population in all 17 entries exactly.
- **No constant:** Δ ln L spreads by 1.0e-12 over the ten points. The new target is Lane A's at this cell with no
  offset, on the H100 and on both A100 types.

### 4. The start check at limit 4 — passed in both parts

`checks/pin_start/pin_start.json`. The reference population at the start H0 of each part, with the nuisances at their
prior centres.

| H0 part | start H0 | penalised | MC-reliability gate | total MC variance (limit 4) | PE / selection | selection N_eff over its threshold | B2 (12AF): total, N_eff ratio |
|---|---|---|---|---|---|---|---|
| 20 to 45 | 32.5 | no | accepted | 1.82 | 0.35 / 1.47 | 2.48 | 1.33, 3.6 |
| 45 to 140 | 92.5 | no | accepted | 0.90 | 0.18 / 0.71 | 5.35 | 0.82, 5.9 |

- Both pins give the same flags and the same variances (to 1e-16).
- The selection variance is larger at nside 128, as 12AL measured. It is largest in the lower part, where it is
  1.47 against B2's 1.33 in total. Both parts start unpenalised.
  *(26 Oct 2026: like for like, the lower part's total variance is 1.82 here against B2's 1.33 (selection alone 1.47;
  B2 recorded no selection part) (finding C067); see "Amendment (26 Oct 2026): independent review, round 3".)*

### 5. GPU timing and memory on js2h100 — measured

`checks/timing_single/timing.json`, `checks/check5_one/timing.json` and `checks/check5_two/timing.json`. The H100
80GB HBM3 ran nothing else. The chain runs used the production command for high_seed41 (and low_seed31), in scratch
directories, with 300 s of sampling after the setup. Every stretch was in dynesty's first, unit-cube phase, where
every call is evaluated: one point per GPU call in the rows form.

| | 12AP (js2h100) | B2 (12AF) |
|---|---|---|
| single call, pin auto (median of 32) | **20.1 ms** | 26.0 ms (MIKO H100 NVL) |
| per point in core's vmap of 32 (not the chains' form) | 12.2 ms | 27.2 ms (MIKO) |
| **per dynesty call in the chain, unit-cube phase, alone** | **21.0 ms** (14,532 calls in 305 s) | **32.1 ms** (js2h100: 21,672 calls in 695 s) |
| GPU use in the chain | 97% | 87% (js2h100) |
| GPU memory of the chain process (nvidia-smi) | 33.6 GB | 17.2 GB (js2h100) |
| peak JAX bytes in use in the process | 17.5 GB (18.3 GB with the batch-of-32 probe) | — |
| setup to the sampling loop | 183 s | 192 s (MIKO, shared) |

- **Two chains at once** (high_seed41 with low_seed31, the same 306 s window): 7,026 and 7,001 calls, 43.5 and 43.6
  ms per call each. Together that is 45.9 calls per second, against 47.7 for one chain alone: **0.96 times the
  throughput**. The GPU showed 100% use and 67.2 GB for the two. Two at once give no gain, so the declared plan
  stands: one after another.

### 6. CPU smoke at 8 live points (HENON) — passed

- **Manifest:** `config/phase12ap_fine_cell_manifest.smoke_cpu8.json` at aabf05b, outputs in `smoke_runs_cpu8/`.
- **The four chains** ran in parallel: jobs 1391054 to 1391057, 14 to 21 minutes each, all exit 0. Each chain:
  - passed its anchor at the midpoint of its part (accepted, unpenalised);
  - had pin auto active and the nside-128 catalog (by sha256), with 196,577 rows, 22,782,073 galaxies and
    sigma_kde 0.001;
  - made 58 to 62 calls (capped and unconverged, as intended).
- **The combination and the comparison:** job 1391058, exit 0 in 2 s (the combination 0.33 s, the comparison 0.05
  s). At 8 live points there are a few dozen nested points; B2's real combination took 7 s.
  - The combination holds the 4 chains, 2 seeds per part, none without a result, with 40,000 pooled samples and 21
    labels.
  - `compare/compare.json` carries no median or interval (location-free); `compare/compare_absolute.json` holds
    the absolute values.
- **The random-walk queue:** at 8 live points (and in check 5's stretches) the chains stay in the unit-cube phase.
  On this target the random-walk queue first runs in the production chains. The sampler and the pool are B2's,
  unchanged, and B2 exercised them on its target.

### Code changes after the declaration

- **85073e2:** the wrapper's `--help` (check 1).
- **2c06a3d:** the combine mode of `slurm/phase12ap_run_js2h100.sh` unsets the `SLURM_*` variables before its
  `srun -p HENON`. Launched from inside the MIKO holder job, srun would otherwise run the combination as a step of that
  job on miko. B2's combination ran that way, for 7 s. `B2_fine/run_12ap.sh` is the same file again. Nothing in the
  chains changes.
- **The runner's sync mode at 2c06a3d** (`logs/pipeline.sync.20261021T132659Z.log`):
  - the five inputs are identical by sha256 on both sides;
  - repo_12AP is at 2c06a3d, clean, on js2h100;
  - the batch env is identical (5e89753cdebf);
  - the committed manifests are the generator's output for the re-derived ridge.

### The estimate (from check 5)

**B2's chains** (12AF results; calls, evaluated points and iterations from each chain's `result.json`):

| chain | calls | evaluated points | iterations | B2 on js2h100 (sampling) |
|---|---|---|---|---|
| high_seed41 | 4,995,414 | 3,779,183 | 42,291 | 116,969 s (stage 32.6 h) |
| low_seed31 | 4,703,940 | 3,452,232 | 40,111 | 107,928 s (stage 30.1 h) |
| high_seed42 | 5,001,164 | 3,777,419 | 42,389 | ran on MIKO; 32.6 h at js2h100's rates |
| low_seed32 | 4,726,508 | 3,487,498 | 40,192 | ran on MIKO; 30.1 h at js2h100's rates |

On js2h100, B2 spent 29.1 to 29.4 ms per evaluated point in the likelihood, plus 1.40 ms per call outside it (dynesty
and the prior transform, on the CPU).

**Two ways of scaling:**

- **The declared way:** B2's js2h100 time scaled by the ratio of the unit-cube per-call times on the same GPU, 21.0
  / 32.1 = 0.654.
- **The upper side:** B2's evaluated points times 12AP's cost per point (20.1 to 21.0 ms, the single call and the
  in-chain unit-cube call), plus B2's time outside the likelihood. That time is on the CPU and is not expected to
  shrink.

Each chain also adds about 0.12 h of setup and finish.

| chain | 12AP estimate on js2h100 |
|---|---|
| high_seed41 | 21.4 to 24.1 h |
| low_seed31 | 19.7 to 22.1 h |
| high_seed42 | 21.4 to 24.1 h |
| low_seed32 | 19.8 to 22.3 h |
| **the four, one after another** | **82 to 92 h (3.4 to 3.9 days), about 87 h at the centre** |
| the two pairs at once (0.96 times the throughput) | 86 to 96 h |
| for comparison, B2's four on js2h100 alone | about 126 h |

- **The first combination:** possible after the first two chains (one seed per part), 41 to 46 h after the start.
- **The final combination:** after the fourth chain. The watcher copies the chains back and runs the combination on
  HENON within minutes (it polls every 10 minutes).
- **The estimate assumes B2's iteration counts.** The 7-day limit is a ceiling, not the estimate.

### The gate

Checks 1 to 6 pass, and both H0 parts are allowed. **The launch commit is 2c06a3d.** The full-suite confirmation at
2c06a3d (jobs 1391084 and 1391085) is recorded when it ends.
*(26 Oct 2026: it passed in both environments (finding C067); see "Amendment (26 Oct 2026): independent review, round
3".)*

**How it is launched** (the chains in tmux on js2h100; the watcher as a HENON job, so that it outlives the MIKO
holder, which ends 2026-10-25 06:19 UTC, inside the estimate):

```
B=/hildafs/projects/phy230054p/magana/darksirens-core-data/phase12_5/B2_fine
nohup setsid $B/run_12ap.sh js2h100 serial > $B/logs/run_12ap_js2h100.out 2>&1 < /dev/null &
# after its last line reads "AP JS2H100 DONE rc=0":
env -u SLURM_JOB_ID sbatch -A phy220048p -p HENON --qos henon -n1 -c 1 --mem 2G -t 7-00:00:00 -J p12ap-combine \
  -o $B/logs/run_12ap_combine-%j.out --wrap "$B/run_12ap.sh combine"
```

**What signals the end:**

- **The chains:** the ap_fine log on js2h100 (its path is in `logs/js2h100.logpath`) ends `EXIT=<rc>`, and each chain
  writes `runs/<chain>/DONE` there.
- **The combination:** `logs/run_12ap_combine-<job>.out` ends `AP DONE rc=<rc>`. On success it writes
  `runs/combined/DONE` and `runs/compare/DONE` on Hildafs; on a failure, `FAILED_combine_<step>`.

## Amendment (25 Oct 2026): independent review

An independent multi-agent review of the consumer repo (desi_darksirens_selection at the review head 17a65bb, 24-25
Oct 2026; report `darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) found that this record's comparison
against B2 cannot yet be read as the effect of the finer cell: both cells share one PE and one injection realisation,
so the seed scatter does not measure the estimator noise that differs between them (finding G6.1), and at the fine
cell the variance guard is an active edge of the posterior (findings C001, G6.2). The owner accepted the recommended
options on 25 Oct 2026: an estimator error on the 12AP-against-B2 comparison from a paired bootstrap of PE and
injections at stored draws of both cells (decision 7A), and, beside each 12AP-against-B2 number, the spectral
likelihood with the DESI guard and a guard-free reweighted comparison (decision 6B; more injections, decision 6A,
before further production chains).

**The results of this record wait for both.** No results amendment is written, and no difference between this record
and B2 is read as the effect of the finer cell, until the estimator error and the guard-free comparison are attached.
Location-free; no number of record is stated or changed here.

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

### Before the results: the rule, what is reported, and three corrections (consumer PR #33, merge 901bb54; owner decisions 6B, 7A)

This record still has no results text: it waits for the estimator error and the guard-free comparison (design 4 of the
review's fixes, not yet run). The items below change no number and state no result.

**The rule for the results amendment (findings G6.1, G6.2, C001).** B2 and this cell share one PE build and one
injection campaign, and the chain seed drives only the sampler, so the PE and injection noise that differs between the
two cells is in no seed scatter; and at this cell the limit-4 variance guard walls off part of the posterior B2
sampled. The 12AP results amendment is written only after (a) the paired bootstrap of PE samples and injections at
stored draws of both cells has attached an estimator error to every 12AP-against-B2 number, and (b) the comparison has
been made at a common guard and without the guard, with the share of the posterior the wall removes. Until then no
12AP-against-B2 difference (median shift, sd or width ratio, lower-part weight, parameter shift) is read as the effect
of the finer cell, and none is written into this record. The tool is `scripts/phase12_5_estimator_noise.py` (capture,
compare), now on the consumer's main: it gives every H0 number and every other sampled parameter's shift and sd ratio
(the `parameters_against_B2` of `compare.json`) its error, and refuses capture sets that do not share one PE file and
one injection file. Its outputs record the commit that wrote them. The run is declared separately (its design states
the draws, the gates and the compute).

**What is reported, added (findings G6.1, G6.2, C013, C068).** Beside each 12AP-against-B2 number, H0's and every
other sampled parameter's, its paired-bootstrap estimator error (sd and 5/50/95% quantiles over replicates, with the
PE-only and selection-only parts), the same comparison at a common guard (either cell's guard on both) and without the
guard on B2's draws, and the share of the guard-free fine-cell posterior the wall removes; per H0 part, the
conditional shift and sd and width ratios, the lower-part weight with its pairing range, and the member mixed at B2's
part weights; and per chain, the guard sample's fractions below the wall and within 5% above it (N_eff from 1 to 1.05
times its threshold; the rows below the wall are not counted again) with sds that count the nested sample's effective
size (`phase12ap_compare.py --readings`, `compare_parts.json`). B2's seed scatter is reported as a yardstick for the
sampler only; it cannot contain the estimator noise that differs between the cells.

**The selection noise at nside 128, measured (findings G6.2, C068).** The last two sentences of this item under
"Limits, stated in advance" now read: at limit 4 with the smooth guard the wall then moves into the posterior B2
sampled: at this cell it lands on about a fifth (upper part) and two fifths (lower part) of B2's posterior draws,
against under 1% at B2 (a penalty below -1 nat on 0.05 to 0.15% of B2's own guard samples; N_eff lies just under its
threshold on 3 to 4% of them, with penalties under 1 nat) (consumer review, measured at both cells on 72 stored B2
draws and again on B2's 240 stored guard-sample draws: 19% upper, 39 to 42% lower). The fraction of penalised samples
counts only the thin layer at the wall and cannot show how much posterior the wall removed; the walled fraction and
the guard-free comparison are reported instead.

**Check 4 (finding C067).** The bullet "The selection variance is larger at nside 128 ..." compared this cell's
selection part with B2's total. Like for like, the lower part's total variance is 1.82 here against B2's 1.33
(selection alone 1.47 here; B2 recorded no selection part), and the selection N_eff over its threshold 2.48 against
3.6. Both parts start unpenalised.

**The full-suite confirmation (finding C067).** The full suite at 2c06a3d passed: HENON job 1391084 (batch env) 502
passed, 2 skipped, exit 0; job 1391085 (e7c3007 env) 493 passed, 11 skipped, exit 0. The skips are the expected ones
(2 in the batch env, 11 core-pool cases in the e7c3007 env). Check 1 and "The gate" said it was recorded when it ends.

### Catalog model and GW inputs

**Catalog model (consumer PR #24, merge 402c947; findings C002, C091, C003, G3.1, C018, G2.1, G2.3, G2.4, G3.3,
G3.2).** Three properties of the catalog model behind this result were found by the review; their H0 effect is not
measured. (1) The catalog's absolute-magnitude floor is in no selection model (C002), and with m_lim 21 the Gaussian
luminosity function makes the union at least 99.7% complete to z_depth, so the sampled M0hat and sigma_M are inert and
the completeness is f_p alone (C091). (2) The footprint fraction is not the catalog's coverage: masked sources stay in
the catalog while f_p removes them (galaxies per unit f_p are 19, 5 and 2 times the median at f_p < 0.05, 0.05-0.2 and
0.2-0.5 at nside 128; C003), and covered sky without r-band or photo-z is read as voids and underdensities (G3.1,
C018); about 5% of PE samples sit in hole pixels. (3) The photometric kernel counts the volume prior twice (G2.1).
Smaller: 2.3% of rows are galaxies DESI measured above 0.30 (G2.3); spectroscopic redshifts are heliocentric (coherent
H0 effect about -0.12%, G2.4); about 5.8k rows under medium-bright-star masks are spurious halo fragments (G3.3); the
photo-z retention rule loses 0.84% of hosts averaged over the window (0.04% to 1.45%, rising with z), about one eighth
of the n0 prior width, with no completeness model (G3.2). The owner's decisions (1C: the hosts are the galaxies above
the floor, complete below the depth; 2A: a footprint built from the catalog's own construction, with the bright-star
mask veto BRIGHT and MEDIUM, maskbits 2050, chosen on 26 Oct; 3B: a re-centred photometric kernel) define catalog
version 2, which the merge adds as opt-in code: no record path changes. Its sizing step, one fixed-calibration H0 grid
pair at the fiducial cell, measures the effect before any chain is rerun; it waits for the owner's go. The
large-galaxy mask is not vetoed: it marks the low-redshift hosts themselves (in a smoke on about 1% of the rows it
removed 93% of the rows at z 0.02-0.03 against a footprint share of 7%).

**n0 window (consumer PR #24, merge 402c947; finding C020).** At delta fixed at 0 the n0 prior centre is matched over
[0.02, 0.30], but the likelihood uses the catalog only to z_depth 0.245; matching within the depth moves the centre by
-0.028 dex (0.78 prior sd). Record 12AB measured the in-depth centre (H0 shifts 0.000, -0.082 and -0.099 posterior sd
in its three parts, inside its declared band). `phase12u_calibrate.py --ridge-z-max 0.245` now gives the in-depth
ridge; the default window is unchanged.

**Photo-z mock of the count ridge (consumer PR #24, merge 402c947; finding C070).** The nside-128 count ridge of this
record (`phase12ap_count_ridge.py`, driver `slurm/phase12ap_count_ridge_henon.sbatch`) runs the 12U calibration, whose
photo-z mock took about half the galaxies' ZERR from the next 0.01 bin up. The finding shows that lookup is wrong, so
the galaxy's own bin is now the default of `phase12u_calibrate.py`; the driver passes `--zerr-lookup
legacy_next_centre`, which reproduces the record's ridge bit for bit. With each galaxy's own bin the luminosity prior
centres move by about 1% (M0hat) and 4% (sigma_M) of their widths. The chains used the preset
count_ridge_union_delta0, which the ridge matched at the preset's precision.

**GW inputs (consumer PR #26, merge a152bed; findings C047, G1.1).** See the GW inputs addendum
(`phases/12_gw_inputs_addendum_2026-10-26.md`). This record reads the LAL-cosmology PE build (822b3181...), which
holds the same rows as the exact build, so it carries the same PE items. The addendum's numbers were measured on the
fixed-population spectral-only target, not on this record's DESI target. This record's chains carry the O3-support
bias and the PE items; their size at the DESI target has not been measured.

## Amendment (27 Oct 2026): independent review, final round

An independent multi-agent review of the consumer repo (desi_darksirens_selection; report
`darksirens-core-data/reviews/consumer-2026-10-24/out/REVIEW.md`) confirmed the findings cited in parentheses
below. The amendments of 25 and 26 Oct 2026 above cover the fix packages merged first. This one covers the two that
were still open: resume markers and fingerprints (consumer PR #25, merge 498a147) and the review follow-ups
(consumer PR #35, merge d036f1e), which carry the owner's decisions of 26 Oct 2026 on a delta outside its prior's
bounds and on the manifests' spectral-only note. Both were merged on 27 Oct 2026, after further fix rounds and an
independent check of each. The consumer's main is now d036f1e. Its code is the tree that was tested, #25 and #35 on
main bdf5150 (consumer commit ab9e656): `./ci.sh` passed there in all three record environments (HENON, CPU;
`ci_logs/20261026T213714Z_ab9e6569b881_<env>.log`: consumer_e7c3007_cuda12 1644 passed,
consumer_e7c3007batch_cuda12 1653, consumer_1022429_lss57afebe_cuda12 1668; none failed), and so did the steps of
the GitHub contract job, run without JAX (`ci_logs/20261026T214140Z_ab9e6569b881_contract_job_nojax.log`: 1105
passed, none failed). Location-free throughout. Unless an item says otherwise, no number of record changes.

**Chain resume (consumer PR #25, merge 498a147; findings C004, C042).** The chain drivers of this record resumed any
checkpoint in their output directory, guarded only by core's run fingerprint, which does not cover the catalog
settings (m_lim, the K-correction, a fixed log10n0; sigma_kde only under kernel pin auto) or, for the 12T chain stage,
the input files; and `--fresh` left the old checkpoint in place, so a fresh run killed before its first checkpoint
save could have resumed the old chain. Neither happened for this record: every chain of record ran with `resumed`
false in one session (the only production chain killed and resumed, A1's limit-2 chain high_seed41 of record 12AA,
sampled 3.9 million further calls after its resume, a real continuation), no manifest or launcher passes `--fresh`,
and each stage has its own output directory checked by the manifest runner's input checksums. Since the merge, the
drivers stamp a run identity (the resolved configuration's sha256, the inputs' sha256, the code, the package commits
and the backend) beside the checkpoint and resume only under it; a checkpoint without a stamp, as every checkpoint of
record is, is refused unless `--adopt-checkpoint` is passed; and `--fresh` moves the old chain aside (to
`<out>/superseded-<UTC>/`; nothing is deleted). Core's run fingerprint and the recorded `run_fingerprint_digest` are
unchanged. The 12AP launcher comment (`slurm/phase12ap_run_js2h100.sh`) that core refuses a checkpoint written under
other settings or env overclaimed: core's fingerprint covers the queue size, likelihood form and kernel pin, not the
catalog settings, and its env record is advisory. The 12AP chains ran from repo_12AP, before the identity stamp, from
one fixed manifest at one clean commit; the comment is corrected on main.

**DONE markers of the manifest runner (consumer PR #25, merge 498a147; finding C073).** The manifest runner treated a
stage's DONE as final without comparing its recorded command or the inputs' checksums. At the reviewed commit every
production run directory's DONE command equalled its manifest's (repository location aside); only smoke directories
held stale DONEs. Since the merge, DONE records the command, the repository and commit, and the sha256 of every
required input, and the runner refuses a DONE whose command or inputs changed and leaves its outputs untouched
(`--rerun-stale` moves the stage aside and reruns it); a DONE written before the change is judged against the
manifest's checksums. A read-only probe of the fixed runner on every production run directory, at the package's
fifth-round head with main 402c947 merged
(`darksirens-core-data/reviews/consumer-2026-10-24/fix/notes/p07-resume/probes/runner_dirs_of_record_37e6f26.json`),
gives the state below; since then the manifests' commands have changed only by the named delta override that consumer
PR #35 adds to two 12U stages already read stale (record 12U).

For this record every stage of the fine-cell manifest (`config/phase12ap_fine_cell_manifest.json`, 6 of 6) still reads
done.

**Misspelt `--set` keys (consumer PR #25, merge 498a147; finding C088).** A misspelt `--set` key outside the sampler
block was accepted, ignored and shown in config.resolved.json. No record path carries one: every `--set` key of the
manifests in config/, of the 12AG and 12AH Part B plan builders and of the shell and Slurm scripts (slurm/,
scripts/*.sh) is a key of the base configuration of the driver it reaches or a key that driver reads (a test of the
consumer checks each of them, command by command). Since the merge, such a key is refused before anything runs.

## Results (27 Oct 2026): against B2 with its estimator error, at a common guard and without the guard

*Location-free: shifts in the reference's posterior sd, sd and width ratios, part weights and their log-odds,
fractions and counts. The absolute values are in `runs/compare/compare_absolute.json` and in the noise run's
`compare_parts/compare_absolute.json`, for the owner page only. Numbers only, by the owner's rule of 20 Oct 2026: no
bands, thresholds or verdicts. B2 is the reference throughout; "B2's sd" is the sd of B2's pooled posterior, and a
per-part shift is in the sd of B2's same part.*

**The runs.** The four chains ran one after another on js2h100 from the launch commit 2c06a3d, each in one session
that did not resume: high_seed41 (41,962 iterations, 4.96 million calls, 22.1 h of sampling); low_seed31 (40,048
iterations, 4.70 million calls, 20.9 h of sampling); high_seed42 (43,040 iterations, 5.09 million calls, 23.2 h of
sampling); low_seed32 (40,428 iterations, 4.75 million calls, 20.7 h of sampling); dlogz 0.1 with 1000 live points,
and each chain's convergence is verified in the comparison. The combination (40,000 pooled samples) and
`runs/compare/compare.json` were written on 25 Oct 2026 at 04:49 UTC. The estimator error (owner decision 7A) and the
comparison at a common guard and without the guard (6B) followed the review's design
(`darksirens-core-data/reviews/consumer-2026-10-24/fix/notes/p04-guard-noise/design_12AP_vs_B2_estimator_error.md`) on
HENON CPU on 26-27 Oct 2026: 96 captures (capture array 1395866; one capture rerun as job 1396083 after a node's task
prolog failed twice) and the comparisons (job 1396084), with `scripts/phase12_5_estimator_noise.py` and
`scripts/phase12ap_compare.py --readings` at consumer commit 6992475 (consumer PR #37, which reads a cell's four
chains together; a clean checkout) in this record's environment, consumer_e7c3007batch_cuda12. Outputs:
`darksirens-core-data/reviews/consumer-2026-10-24/runs_2026-10-26/12AP_vs_B2_noise_r2/` (`compare_noise.json`,
`compare_noise_half.json`, `compare_parts/compare_parts.json`).

**How the error is made.** Each cell is read at 512 stored draws per H0 part (256 distinct equal-weight rows of each
chain). 200 paired bootstrap replicates resample the PE samples (each of the 259 events' 4096 samples with
replacement) and the injections (a Poisson(1) count for each of the 1,067,946 found injections) with one plan, so that
replicate b resamples the same rows at both cells; both cells read one PE file (sha256 822b3181...) and one injection
file (56e51af2...). All 64 captures at a chain's own draws reproduce its stored log-likelihood to at most 1.1e-12 (the
gate is 1e-8). The estimate is the reading at the draws; the error is the sd over the replicates, with its 5% to 95%
range; the PE-only and selection-only errors are given beside it. "At B2's draws" reweights B2's draws to the fine
cell, so both cells are read on one proposal: as run (each cell with its own guard), with either cell's guard on both,
and with no guard. B2's draws stop at B2's own wall, so posterior mass beyond it is in none of these readings.

**H0.**

| 12AP against B2 | Shift in B2's sd (5% to 95%) | sd ratio | 68% width ratio | 90% width ratio | Lower part's log-odds change |
|---|---|---|---|---|---|
| Pooled chains (`compare.json`, 40,000 samples per cell; no error) | −0.417 | 1.146 | 1.238 | 1.076 | +0.48 |
| Each cell at its own draws, as run | −0.548 ± 0.360 (−1.08 to +0.01) | 1.108 ± 0.172 | 1.286 ± 0.352 | 1.054 ± 0.177 | +0.48 ± 0.59 |
| &nbsp;&nbsp;PE part alone | ± 0.131 | ± 0.062 | ± 0.143 | ± 0.061 | ± 0.17 |
| &nbsp;&nbsp;selection part alone | ± 0.328 | ± 0.154 | ± 0.336 | ± 0.165 | ± 0.54 |
| Both cells at B2's draws, as run | −0.072 ± 0.326 (−0.90 to +0.15) | 1.104 ± 0.139 | 1.265 ± 0.270 | 1.113 ± 0.159 | +0.31 ± 0.58 |
| Both cells at B2's draws, both with the fine cell's guard | −0.119 ± 0.332 (−1.01 to +0.08) | 1.112 ± 0.122 | 1.302 ± 0.254 | 1.087 ± 0.137 | +0.52 ± 0.51 |
| Both cells at B2's draws, both with B2's guard | −0.256 ± 0.342 (−1.06 to +0.07) | 1.127 ± 0.131 | 1.287 ± 0.259 | 1.088 ± 0.154 | +0.58 ± 0.50 |
| Both cells at B2's draws, no guard | −0.249 ± 0.340 (−1.04 to +0.06) | 1.128 ± 0.131 | 1.288 ± 0.257 | 1.091 ± 0.153 | +0.58 ± 0.51 |

The lower part's weight is 0.083 in 12AP (matched pairs 0.105 and 0.066; range over the four pairings 0.066 to 0.105)
against 0.053 in B2 (0.047 and 0.060; 0.044 to 0.064); their ratio is 1.57 ± 1.24 (0.68 to 3.72) at the own draws.

**Per H0 part.**

| Own draws (pooled chains in brackets) | Shift (in the sd of B2's same part) | sd ratio | 68% width ratio | 90% width ratio |
|---|---|---|---|---|
| Lower part | −0.197 ± 0.406 (−0.148) | 0.862 ± 0.111 (0.848) | 0.857 ± 0.165 (0.833) | 0.857 ± 0.123 (0.898) |
| Upper part | −0.552 ± 0.392 (−0.364) | 1.154 ± 0.154 (1.180) | 1.374 ± 0.306 (1.356) | 1.042 ± 0.165 (1.060) |
| 12AP mixed at B2's part weights (shift in B2's sd) | −0.502 ± 0.345 (−0.365) | 1.073 ± 0.137 (1.110) | 1.277 ± 0.313 (1.228) | 0.976 ± 0.137 (0.992) |

**The wall.** At B2's draws the fine cell's wall removes 0.316 ± 0.092 (5% to 95%: 0.10 to 0.43) of the guard-free
fine-cell posterior, and 0.301 ± 0.089 with both cells at B2's guard. B2's own wall at its draws: 0.21% of B2's
posterior carries a penalty below −1 nat (0.39% of the lower part, 0.20% of the upper), 6.1% lies within 5% above its
threshold, and the fine cell's selection N_eff is under its threshold on 27% of it. The Kish effective size of the
reweighting to the fine cell is 224 and 316 of 512 (lower, upper part) as run and 253 and 344 without the guard; over
the replicates (as run, 5% to 95%) 24 to 148 and 23 to 179. In each chain's guard sample (sds from the nested sample's
effective size), N_eff is under its threshold for 4.4% to 4.9% of 12AP's rows against 3.1% to 3.6% of B2's, within 5%
above it for 7.1% to 9.5% against 6.2% to 6.9%, and the penalty is below −1 nat for 0.07% to 0.27% against 0.05% to
0.15%; some penalty applies to 21.5% to 26.1% of 12AP's pooled samples against 17.8% to 19.1% of B2's.

**Half the draws.** Read on the even slices only (256 draws per part), the errors are 1.02 to 1.14 times the full ones
(the shift at the own draws 0.410 against 0.360), against about 1.41 if the draw set's own reweighting noise made
them; the design reads this as the estimator's error making the spread.

**Seed scatter (the sampler only; it holds none of the PE and injection noise that differs between the cells).**
Against B2's upper part, 12AP's upper-part chains read −0.519 (seed 41) and −0.196 (seed 42), B2's own −0.040 and
+0.049; in the lower part 12AP's read −0.151 and −0.144, B2's +0.013 and −0.033. The matched pairs read −0.547 (seeds
31 and 41) and −0.245 (32 and 42) in 12AP, −0.028 and +0.045 in B2. The seeds' ln Z difference is −0.48 (lower part)
and +0.03 (upper) in 12AP, +0.34 and +0.07 in B2; each chain's reported ln Z error is 0.198 to 0.204.

**The other twenty sampled parameters** (shift in B2's sd and sd ratio):

| Parameter | Shift in B2's sd (pooled) | sd ratio (pooled) | Shift, own draws | sd ratio, own draws | Shift, B2's draws, no guard | sd ratio, B2's draws, no guard |
|---|---|---|---|---|---|---|
| M0hat | +0.009 | 0.992 | +0.032 ± 0.133 | 1.059 ± 0.074 | −0.031 ± 0.101 | 0.988 ± 0.042 |
| alpha1 | −0.054 | 1.052 | −0.152 ± 0.108 | 1.061 ± 0.130 | −0.021 ± 0.078 | 0.948 ± 0.074 |
| alpha2 | +0.056 | 0.985 | +0.144 ± 0.141 | 0.978 ± 0.074 | +0.013 ± 0.106 | 0.976 ± 0.047 |
| beta_q | +0.061 | 1.014 | +0.071 ± 0.163 | 1.069 ± 0.060 | +0.038 ± 0.103 | 0.983 ± 0.038 |
| delta_m1 | −0.090 | 0.978 | −0.029 ± 0.179 | 1.013 ± 0.057 | −0.205 ± 0.112 | 0.993 ± 0.036 |
| delta_m2 | −0.016 | 1.018 | −0.037 ± 0.149 | 0.978 ± 0.044 | −0.000 ± 0.113 | 0.981 ± 0.032 |
| gamma | +0.040 | 1.060 | +0.052 ± 0.133 | 1.167 ± 0.077 | +0.128 ± 0.129 | 1.015 ± 0.047 |
| lambda0 | −0.073 | 0.977 | −0.133 ± 0.132 | 1.029 ± 0.055 | −0.086 ± 0.082 | 0.971 ± 0.044 |
| lambda1 | +0.068 | 0.980 | +0.101 ± 0.138 | 1.028 ± 0.052 | +0.101 ± 0.095 | 0.967 ± 0.042 |
| log10n0_q | −0.220 | 0.988 | −0.208 ± 0.154 | 1.019 ± 0.040 | −0.060 ± 0.121 | 1.000 ± 0.030 |
| m1_low | +0.068 | 0.982 | +0.110 ± 0.175 | 0.933 ± 0.051 | +0.101 ± 0.131 | 1.002 ± 0.040 |
| m2_low | +0.079 | 1.042 | +0.064 ± 0.125 | 0.994 ± 0.062 | +0.096 ± 0.156 | 1.015 ± 0.039 |
| m_break | +0.124 | 0.968 | +0.185 ± 0.140 | 0.937 ± 0.052 | +0.102 ± 0.125 | 0.985 ± 0.050 |
| mu1 | +0.238 | 1.142 | +0.331 ± 0.265 | 1.091 ± 0.149 | +0.194 ± 0.266 | 1.131 ± 0.121 |
| mu2 | +0.048 | 1.025 | +0.098 ± 0.131 | 1.030 ± 0.140 | +0.062 ± 0.103 | 1.063 ± 0.106 |
| mu_chi | −0.020 | 0.996 | +0.018 ± 0.102 | 0.988 ± 0.081 | −0.008 ± 0.098 | 0.988 ± 0.038 |
| sigma1 | +0.197 | 0.978 | +0.136 ± 0.190 | 1.006 ± 0.077 | −0.099 ± 0.126 | 0.966 ± 0.070 |
| sigma2 | +0.198 | 1.108 | +0.233 ± 0.194 | 1.172 ± 0.100 | +0.101 ± 0.184 | 1.067 ± 0.067 |
| sigma_M | −0.035 | 1.018 | −0.182 ± 0.129 | 1.055 ± 0.065 | −0.047 ± 0.114 | 0.987 ± 0.042 |
| sigma_chi | −0.013 | 0.994 | −0.045 ± 0.116 | 1.059 ± 0.076 | −0.031 ± 0.105 | 0.980 ± 0.043 |

**Against B1 and A1** (pooled chains; the paired bootstrap covers the comparison with B2 only, so no estimator error
is attached). Against B1: shift −0.314 in B1's sd, sd ratio 1.177, 68% and 90% width ratios 1.245 and 1.131; B1's
lower-part weight is 0.042. Against A1: shift −0.242 in A1's sd, sd ratio 1.210, width ratios 1.314 and 1.146; A1's
lower-part weight is 0.037 (range over its pairings 0.021 to 0.065).

**In numbers.**

- Every H0 difference between the cells is at most 1.52 times its estimator sd. The largest is the shift at the own
  draws, −0.548 ± 0.360 (1.52 sd), then the upper part's, −0.552 ± 0.392 (1.41); at B2's draws every H0 number is at
  most 1.19 times its sd.
- Of the twenty other parameters, the largest at the own draws are the sd ratios of gamma (1.167 ± 0.077, 2.2 sd) and
  sigma2 (1.172 ± 0.100, 1.7), and at B2's draws without the guard the shift of delta_m1 (−0.205 ± 0.112, 1.8); every
  other is at most 1.4. The pooled chains give gamma's sd ratio as 1.060 and sigma2's as 1.108.
- Without the guard the H0 numbers at B2's draws are those with both cells at B2's guard to within 0.01 (shift −0.249
  against −0.256, sd ratio 1.128 against 1.127, log-odds change +0.58 against +0.58). With the fine cell's guard on
  both the shift is −0.119, and as run −0.072.
- The estimator's own error on the shift is 0.33 to 0.36 of B2's posterior sd, about a third; at the own draws its
  selection part alone is 0.33 and its PE part 0.13.
- The pooled shift (−0.417) and the shift at the own draws (−0.548) differ by the subsample's noise; the shift at the
  own draws and the one at B2's draws as run (−0.072) read the fine cell on different proposals.
- 12AP's two upper-part seeds differ by 0.32 of B2's upper-part sd; B2's two differ by 0.09.

No number of an earlier record changes. Location-free throughout.
