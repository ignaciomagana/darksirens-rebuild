# Phase 12E — A100 benchmark campaign record: darksirens-core vs darksirens, performance and end-to-end validation

Status: **PROPOSED RECORD / NOT ACCEPTED / PRODUCTION PIN UNCHANGED (8bf2bec5)**

Parent science phase: `phases/12_production_analysis_contract.md`

Previous core record: `phases/12D_core_deferred_followup_contract.md`

Active production core pin (unchanged by this record): `8bf2bec53ff7b557c6b930d4044008cb72008f61`

## Trigger

Before any real-data production run, the campaign measured two things:
1. whether darksirens-core is as fast as the frozen darksirens reference on real hardware, and where it is slower;
2. whether the two codes give the same answers end to end, from fixed-coordinate kernels up to full sampler runs on the real GWTC product.

The campaign ran on 2026-09-24 and 2026-09-25 on a Jetstream2 A100 host. An orchestrator (Fable) ran it in gates, delegating to workers, and every gate had an independent audit. This record summarises the gates, verdicts, headline numbers, pull requests and the owner's decisions taken at the end. It does not accept anything and does not move the production pin.

## References

```text
frozen reference (immutable, byte-identical after every stage):
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

candidate:
  ignaciomagana/darksirens-core main 88004d96ddeee37c47abc1d2dfd1c6fc3c203dfd

control (Phase-12C production pin, unchanged):
  ignaciomagana/darksirens-core 8bf2bec53ff7b557c6b930d4044008cb72008f61

Gate 4 experimental arm (O1):
  ignaciomagana/darksirens-core branch perf/jit-bound-analysis, f825906 (as measured)

gwcat:
  ignaciomagana/gwcat 8f9e2f12b499a6b2bf16ed938f66d020b12c44c2

darksirens-rebuild:
  main 733a11bf25cc8c0aeeadf5a7156ebc9afdc7a84d
  harness branch bench/a100-campaign, head 2ed841b (benchmarks/a100/; never merged to main)
```

**Host.** js2a100:
- GPU: GRID A100X-20C, 20 GB vGPU.
- CPU: 16 vCPU AMD EPYC-Milan.
- Driver 535 / CUDA 12.2.
- CPython 3.11.10; jax/jaxlib 0.4.34 with CUDA 12.2-line wheel pins, x64.
- No XLA compiler flags were set at any point.

**Real-data products** (fresh gwcat build from 282 raw PE files; 259-event canonical whitelist):
- PE: `A_pe_chieff_bbh259_n4096_v20.h5`, sha256 `a24a5903a7f7da6fdcdee22f58c4c0efa76447f2cf4d581dc19ec3e60ce478a5` (gwcat-pe-2.0, chieff, 259 x 4096);
- selection: `A_sel_chieffref_o3o4ab_v20.h5`, sha256 `bab92babf2d6958a6ed04ee536c44fa533f5c4822ca9a22f934347a089d21ab5` (gwcat-selection-2.0, chieff_reference, O3 endo3 + O4ab; n_det 1,067,946; ndraw 944,412,448).

## Parity standard

Applied at every gate:
- Every gate field must agree to rtol 1e-12, atol 0.
- Masks and guard decisions must be exactly equal.
- Repeated coordinates must be bit-identical.

Four judging rules were fixed in advance and gated on evidence: D-mcvar, D-neff2, D-catvals and D-rowmax. None relaxed a primary quantity. One was needed once: in Gate 2, a 4-ulp reduction-order difference in log_mu was amplified 278x in the derived n_eff (D-neff2). Sampler runs were judged as deterministic replicas: equal evaluation and iteration counts and identical `ncall` traces, plus bit-identical samples and logZ where both runs converged.

## What was measured: gates and verdicts

| Gate | Verdict | Evidence in one line |
|---|---|---|
| 0 repo and environment sanity | PASS | core 759/1, pin 714/1, legacy Tier-0 841 with 8 skips on CPU; real-backends 75/0 on GPU; 10/10 paired probes bitwise equal (legacy = core main = core pin) on the A100 |
| 1 spectral kernels at fixed coordinates | PASS | 145 records, 173 pairs, 0 failures; legacy/core time ratio 0.970-1.111 (median 1.016 over 44 cells) |
| 2 simple mock dark sirens | PASS (D-neff2) | 58 records, 65/65 pairs; legacy 1.9-2.4x faster only where its build-time H0 kernel pin applies |
| 3 realistic mock scaling (R1, R2, R3, RC) | parity PASS, scale PARTIAL | 0 failures in 140 comparisons, including per-component ones; R2/R3 need explicit blocks in core and `--row_chunk 2048` in legacy; RC fits neither code on 20 GB |
| 4 optimisation | O1 accepted as parity-preserving (unmerged) | kernel total bitwise equal to core whole-jit in 22/22 GPU records; 37-221x faster than core as shipped |
| 5 real spectral ladder (1/3/4/13/17/18-D, TinyNS and dynesty) | PASS | 40/40 fixed-coordinate checks on the full product; every TinyNS legacy/core pair a deterministic replica; converged pairs bit-identical |
| 6 real dark sirens | HARD STOP | `REAL_DARK_READY.md` written; not cleared |

## Headline numbers

- **Kernel, like for like** (whole-jit, same data, same coordinates):
  - spectral, legacy/core: 0.970-1.111;
  - unpinned dark plans: 0.937-1.064;
  - core's first call is about 5.5% faster;
  - core uses about 19% less device memory at real-data spectral scale: 626 vs 769 MiB.
- **Where legacy is faster:**
  - Where its build-time H0 kernel pin applies, legacy is 1.2-2.3x faster (legacy/core 0.43-0.81), at +7-9 s of build and 2.3-2.9x the device memory.
  - Legacy is also 7-8% faster at R1-R3 and 5% faster on the Gate 5 rungs that fix part of the population. Core has no public partial fixing, so the fixed values do not fold to constants there.
- **Core as shipped is 33-221x slower per call.**
  - Cause: `BoundAnalysis` is evaluated eagerly and rebuilds its `lax.scan` bodies on every call.
  - Per call it pays 191-726 ms of flat dispatch overhead; the first call takes 15-29 s; it uses 2.6x the device memory.
  - In the real-data ladder this adds 195.6-229.7 s to every TinyNS run (1000 serial initial live points at about 0.2 s each). It makes dynesty 39.5x slower: 20,016 evaluations took 4,491 s, where legacy converged in 345 s.
  - With explicit blocks, every call recompiles and grows host memory by about 134 MiB.
- **O1** (core branch `perf/jit-bound-analysis`) jits the bound analysis once at bind time, with the data as jit arguments. It gives:
  - kernel totals bitwise equal to core whole-jit (22/22 GPU records);
  - a dynesty posterior and logZ bitwise equal to legacy;
  - 5.7 s for the 1000 TinyNS initial live points;
  - a 626 MiB device peak.
- **Core pin 8bf2bec5 vs core main 88004d96:** bitwise-identical values; time ratio 0.94-1.00.
- **Memory bounds on the 20 GB vGPU:**
  - R2 (nside 128, 196,608 rows x 70; DESI-like):
    - core whole-jit / O1: **12,055 MiB** (78.5% of the 16.1 GB allocator pool), only with explicit blocks 4096/6;
    - legacy: 7,669-8,330 MiB, only with `--row_chunk 2048`;
    - core as shipped: out of memory.
  - RC (nside 256, 786,432 rows x 159, 69.8M galaxies): **unevaluable in both codes**, with live lower bounds of 13.8 GB (core) and 15.2 GB (legacy).
- **The hard guard is infeasible on the real product.** At the GWTC-5 population centre:
  - the selection N_eff is **12,819.5**, against the cap-1.0 budget N_obs^2/(1 - sigma^2_PE) = **78,639.9**;
  - both codes abort at the sampler preflight, with 0/32 draws finite;
  - the soft guard at 1.0 is penalty-dominated and does not converge;
  - the ladder ran at the soft guard with cap 10, a measurement setting only;
  - on this product the P12.4 criterion evaluates to 5.38 > 1.
- **Convergence** under the soft guard with cap 10, in both codes alike:
  - 1-D and 3-D converged with both samplers; 4-D converged with dynesty only;
  - the 13/17/18-D rungs stalled at dlogz 23-32 (TinyNS) and 30-60 (dynesty) within 3e5 evaluations or 3,600 s;
  - within legacy, TinyNS and dynesty disagree at 3-D: logZ -767.660 vs -767.899 (2.09 sigma); m_break KS D 0.123 against a 1% critical value of 0.036.

## Measurement note: the dynesty call count

dynesty 2.1.4's `rwalk` increments `ncall` when a ball proposal fails to land in the unit cube, without calling the likelihood (`dynesty/sampling.py:241-244`). It also re-evaluates without counting when no proposal is accepted (`:258-263`). Its `ncall` therefore over-counts likelihood calls by 6-41% at 3-D and above: 1.064 at 3-D, 1.067 at 4-D, 1.392 at 13-D and 17-D, and 1.409-1.410 at 18-D.
- The campaign's budgets and its `n_like_evals` used true counted calls, so the evaluation totals and budget stops are correct.
- The harness's dynesty `evals_per_s_steady` column is built from `ncall` and inherits the over-count.
- Rate ratios within a pair are unaffected, because the traces are identical.

## Pull requests from the campaign

```text
ignaciomagana/darksirens-core PR #25   O1: jit the bound analysis once at bind time (data as arguments)
  branch perf/jit-bound-analysis   base main
  as measured: f825906 (src/darksirens/runtime_binding.py +73/-16, tests/test_runtime_binding_jit.py +259)
  head at the time of this record: c9394b51bd7465ecd975f400430a80e16f1cad43
    (adds a test-only commit: two fused-vs-eager fixed-theta tests compare at
     rtol 1e-14 instead of exactly, since GitHub's x64 runner differs by 1-2 ulp)
  status: OPEN, pending merge

ignaciomagana/darksirens PR #460   mock-data n0/log10n0 prior guard
  branch fix/mock-log10n0-prior-guard (0e76fdd)   base master c042527
  status: MERGED 2026-09-25 as 675ff4637b3bb90eef02d2068c5a8bfecdd87b30
  (the generated mock products are bit-identical to before in all 61 datasets
   and attributes; only a galaxy_density metadata key is added)
```

Issues filed from the campaign findings, on the owner's decision:

```text
ignaciomagana/darksirens#462        TinyNS: debug ticket from the A100 benchmark campaign
ignaciomagana/gwcat#21              Validator gap for mixed 2.0/2.1 pairs; stale README; GWTC-3 concept DOI moved
ignaciomagana/darksirens-core#26    Samplers that trace the likelihood embed the distance table and data as HLO constants
ignaciomagana/darksirens#461        Samplers that trace the likelihood embed the distance table and data as HLO constants
```

## Owner decisions, 2026-09-25

1. **Guard study first.** No production spectral or dark run starts until the selection N_eff guard cap is chosen:
   - hard@1.0 is infeasible on the real product;
   - soft@1.0 does not converge;
   - soft@10 was a measurement setting only.
2. **dynesty only; TinyNS is considered broken** until darksirens#462 is debugged. As a result, the TinyNS lines of `REAL_DARK_READY.md` section 4 ("Sampler: TinyNS (production)") and the P12.4 configuration (TinyNS, preset `bounded_multi`, which also raises `ValueError` with the pinned tinyns 3f9e1b2) do not stand as written.
3. **A partial-fixing API for darksirens-core is to come.** Core's population is either fully sampled or fully fixed. That forces the harness `InferenceTarget` embedding at the partially fixed rungs (5% slower) and blocks a port of legacy's H0 kernel pin.
4. **A consumer PR is to come** for `desi_darksirens_selection`. Its un-jitted P12.4 `InferenceTarget`, with blocks 131072/32, recompiles its scans on every eager call; O1 cannot reach it.
5. **Gate 6 stays a hard stop.** `REAL_DARK_READY.md` is the release gate for the real-data dark-siren branch. It lists the survey assets still required under the Phase 12 contract, the proposed configuration, the cost estimate at DESI-like scale (12,055 MiB; 469-472 ms per evaluation; about 13 h per 1e5 evaluations for core whole-jit/O1) and the blockers.
6. **Next validation step: a mock-proxy ladder on the R1/R2 realistic mock fixtures** before any real dark-siren run.

## Pin decision

The Phase-12C production pin `8bf2bec53ff7b557c6b930d4044008cb72008f61` stays the active production core pin. This record measures and summarises; it changes no package and adopts no pin.
- O1 (darksirens-core #25) is a pure performance change that preserves parity (bitwise kernel totals). It is not merged. If merged, adopting it would need its own record, with the merge SHA and tree and green push-triggered gates.
- Core main 88004d96 is bitwise equal to the pin wherever the campaign compared them.

## Left open

- The production guard cap (decision 1), and whether P12.4's hard-guard acceptance rule holds on P12.4's own inputs. The campaign did not reuse those inputs.
- No converged posterior above 4-D in either code; which sampler to trust at production dimension (decision 2).
- RC-scale catalogs: a larger device, or row-chunked catalog-side arrays in core.
- A sampler that traces the likelihood embeds the 106 MB distance table and the data as HLO constants, in both codes. The TinyNS traced kernel at R2 scale was not measured and may need more than 12.1 GB (darksirens-core#26, darksirens#461).
- The `desi_darksirens_selection` `phase12-contract` CI has still not run (Actions billing).
- The harness branch `bench/a100-campaign` (2ed841b) is not merged to `main`, and this record does not propose merging it.

## Where the evidence lives

Campaign root: `js2a100:/media/volume/tbs/darksirens_benchmark` (`$ROOT`):

```text
$ROOT/state/BENCHMARK_STATE.md          state of record; every D-* decision with its reason
$ROOT/state/REAL_DARK_READY.md          Gate 6 release gate (not cleared)
$ROOT/state/manifest.json               470 runs
$ROOT/reports/FINAL_REPORT.md           final report
$ROOT/reports/FINAL_ANSWERS.md          answers to the campaign questions, with evidence paths
$ROOT/reports/FINDINGS_REGISTER.md      112 findings (owner, class, status, evidence)
$ROOT/reports/final_tables/             T1-T6 (.csv, .md)
$ROOT/reports/*.md                      26 worker reports and audits (gate0..gate5, harness, phase1)
$ROOT/benchmarks/gate{0..5}/            records, summaries, smi logs, raw stdout/stderr
$ROOT/benchmarks/gate5/runs/<id>/       the 26 ladder runs (record.json, progress.csv, posterior.npz)
```

Hildafs mirror: `/hildafs/projects/phy230014p/magana/darksirens_benchmark_local/`. The reports are under `reports/`. Audit tables and raw copies are under `gate5_final_audit/`, `gate4_o1/`, `gate34_audit/` and `gate3b_retries/`.

sha256 of the key mirrored reports at the time of this record:

```text
0051267614b4a0239be9d53cdb5ae04891ac3a4a6dd3ca0e27202ae144ec420f  reports/FINAL_REPORT.md
d4b4045cfa66119e39b0f6ea95673705de8994d886d62415e8397e7db5190c26  reports/REAL_DARK_READY.md
59173937afde47e54bd0f90c423e5e51aaf403633ad4dfbe08b9851f2e521192  reports/FINDINGS_REGISTER.md
2a52238695daa39091f133a6d28bfbf0d45301734f03564ec0a28b40b83ee9a4  reports/FINAL_ANSWERS.md
c557ed6e7f56aa465ffd3fdf2e3190026b400888dff48c8e3c3d7aacb625ba25  reports/gate5_final_audit.md
174c4e6bd15dd2e42dba1c026a540af48f50d0f257dd032db4a1797599501422  reports/gate5_run.md
3bb40538414739147c2b617bf29494f26670a87dc28a359faf77ad76d43853af  reports/gate4_o1_prototype.md
6db0b3c5c657be9fe8c10de9b410eee40534f88bfd62229113fdc88abebecb6c  reports/gate34_audit.md
7c86d2461d6c68046df61c9223ded7ee67cc9fe63f43045a6d3225ad63fca532  reports/phase1_gwcat_contract.md
336e10581fb573ecc40ed0aae997650119acd7bf09204d8bac58ed3eba4138ca  reports/phase1_archaeology_likelihood.md
```

Where to find the headline numbers:
- Gate ledger, speed, memory and readiness: `FINAL_REPORT.md` sections 1-10.
- Gate 5 ladder, cross-sampler check and the dynesty call count: `gate5_final_audit.md` §0, §2.4, §3.7, §4.
- O1 root cause and the constants embedding: `gate4_o1_prototype.md` §3 and §8.
- R2/RC memory: `gate34_audit.md` and `gate3b_retries.md`.
- Hard-guard infeasibility: `gate5_final_audit.md` §4.1 and `REAL_DARK_READY.md` §4.
- gwcat contract: `phase1_gwcat_contract.md`.

## Verdict

**Not accepted.** This is a proposed control record of the campaign. The production core pin stays `8bf2bec5`. Real dark sirens stay stopped at Gate 6.
