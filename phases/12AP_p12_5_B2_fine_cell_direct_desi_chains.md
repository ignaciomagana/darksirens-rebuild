# Phase 12AP — P12.5: stage B2's direct DESI chains at the fiducial cell, nside 128 and sigma_kde 1e-3 (declaration)

## Status

**DECLARED (owner, 2026-10-21), before any chain.** No 12AP chain has run. This record fixes the question, the
changes against stage B2 (record 12AF), the inputs with their sha256, the checks before the go, what is reported
and the compute. The checks are recorded under "Results: before the chains" as they finish. The main session
launches the chains on the owner's go, with the commands under "How it runs".

**Blinding: location-free.** No H0 location appears here, in commit messages or in the logs agents read: no median,
interval, MAP or shift in km/s/Mpc. The H0 values in this record are fixed a priori: the split prior's bounds (20,
45, 140), the start points 32.5 and 92.5, and the tie points of check 3 (20, 32.5, 45, 60, 70, 80, 92.5, 110, 125,
140). Results are appended at the end later, as in 12AF: absolute values go to the owner page only, never to the
clean-room session or to a coordinator.

**The owner's reporting rule (2026-10-20) replaces 12AF's bands and its bootstrap agreement test.** Posteriors and
their differences are reported as numbers (shift in sd, width ratios, the lower part's weight). No bands,
thresholds, z-scores or verdicts.

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
- **The estimate assumes B2's iteration counts.**
