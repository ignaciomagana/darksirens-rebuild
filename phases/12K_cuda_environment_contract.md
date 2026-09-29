# Phase 12K — CUDA backend for GPU runs of the Phase 12 chain

## Status

**ACCEPTED ENVIRONMENT CHANGE (owner, 2026-09-28).** Consumer
implementation: `desi_darksirens_selection` `requirements-cuda12.txt`, its
runbook section and a contract test. No package of the frozen stack changes;
no setting or numerics of the chain changes. **Gates 3 and 4 met on
2026-09-29** (see "GPU evidence"); gate 2 is this PR's consumer counterpart.

## Trigger

P12.4 is to run on a GPU. The frozen stack (`requirements-frozen.txt`,
core `a46dec7`) installs the CPU jaxlib 0.4.34, so JAX falls back to the CPU
on a GPU node. The owner decided on 2026-09-28 to run the chain on the
Hildafs H100 (MIKO partition, NVIDIA H100 NVL, 96 GB) with the CUDA backend
of the same jaxlib.

## Change

The CUDA backend is added on top of the frozen stack:

```text
jax-cuda12-plugin     0.4.34   (must equal the frozen jaxlib)
jax-cuda12-pjrt       0.4.34
nvidia-cublas-cu12    12.3.4.1
nvidia-cuda-cupti-cu12 12.3.101
nvidia-cuda-nvcc-cu12 12.3.107
nvidia-cuda-nvrtc-cu12 12.3.107
nvidia-cuda-runtime-cu12 12.3.101
nvidia-cudnn-cu12     9.1.0.70
nvidia-cufft-cu12     11.0.12.1
nvidia-cusolver-cu12  11.5.4.101
nvidia-cusparse-cu12  12.2.0.103
nvidia-nccl-cu12      2.20.5
nvidia-nvjitlink-cu12 12.3.101
```

- The NVIDIA wheels are the CUDA 12.3 series, matching the Hildafs driver
  (545.23.08, CUDA 12.3). An unpinned install resolved the 12.9 toolkit, on
  which XLA disables parallel PTX compilation for this driver.
- Every other distribution is unchanged: the environment's `pip freeze`
  differs from the frozen environment's by exactly these 13 lines. P12.1's
  check (`scripts/check_frozen_environment.py`) passes: the four packages at
  their pinned commits, dynesty 2.1.4, numpy 1.26.4, scipy 1.12.0, jax and
  jaxlib 0.4.34, h5py 3.12.1.
- Core enables float64 on import, so the GPU stages run in double precision.
  Sums differ from the CPU in reduction order only.

Environment on Hildafs:
`/hildafs/projects/phy220048p/magana/darksirens-core-data/darksirens_benchmark_local/envs/consumer_a46dec7_cuda12`
(a copy of the frozen `consumer_repin_a46dec7`, CPython 3.11.10, plus the
lines above; freeze file alongside it).

## Acceptance gates

1. The owner accepts the change. **Met 2026-09-28** (run P12.4 on the H100 of
   the MIKO partition, from this session's allocation).
2. The consumer change merged with its contract test; contract CI blocked
   (billing), local stand-ins recorded in the consumer PR.
3. The first GPU chain run agrees with the CPU run of the same consumer
   commit at P12.2's calibration point to 1e-12 relative (total ln L and
   selection N_eff; the Phase 12F criterion), and its P12.3 grid maximum and
   posterior mean equal the CPU values.
4. P12.4 is accepted under the Phase 12F gate 7 criterion (dynesty converged
   to dlogz 0.1; zero soft-guard penalty at the posterior mean and median).

## GPU evidence (2026-09-29)

In the environment above on the MIKO H100 (driver 545.23.08), the consumer's
test suite passes (297 passed at the 12K branch; 294 passed at `c86629b`).
The chain runs are recorded in full in
`phases/12F_selection_guard_and_gwcat_products_acceptance.md`, "Production-path
evidence".

- Gate 3, at P12.2's calibration point. The CPU run (consumer `dc9c8a3`,
  frozen environment, Slurm 1346044) gives total ln L -765.1371043921606 and
  N_eff 12837.827176048335. The GPU runs (`dc9c8a3` at cap 10, and `c86629b`
  at cap 20) give -765.1371043921611 and 12837.827176048382. The differences
  are 6.5e-16 and 3.7e-15 relative, within 1e-12. P12.3's grid maximum
  (64.5) and posterior mean (64.643) are equal on both devices.
- The P12.4 field target itself was also compared at single points: at ten
  values of H0 from 60 to 72 (at the prior means of `M0hat` and `sigma_M`),
  GPU and CPU agree to 2.9e-16 (ln L) and 7.2e-15 (N_eff), and the
  soft-guard penalties agree.
- Gate 4: the GPU P12.4 run at cap 20 (consumer `c86629b`) converged (final
  dlogz 0.0999). It is unpenalised at the anchor, the posterior mean and the
  posterior median: 12F gate 7 is met.
- Wall time of the whole chain on the H100: 30 min (P12.4 28 min).

## Verdict

**Accepted (owner, 2026-09-28)** as an environment change for GPU runs.
Results from it are accepted only through gates 3 and 4.
