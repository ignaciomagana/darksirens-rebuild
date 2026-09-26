# Mock-proxy dark-siren ladder (MOCK fixtures R1, R2 only)

Fable's spec (2026-09-25): plans `dark_H0` and `dark_full` (plans.py), dynesty only, nlive 1000,
dlogz 0.1, seed 20260924, checkpointing off, soft selection-N_eff guard at max_likelihood_variance
10 in both codes; stop at the first of convergence, 300,000 likelihood evaluations or 7200 s of
sampling wall; 9000 s `timeout` backstop; legacy c042527 vs darksirens-core main 43d273f; R1 single
pass, R2 blocks sel_batch 4096 / pe_event_block 6 in both codes and legacy `--row_chunk 2048`;
cold XLA cache per run. Real dark sirens (Gate 6) are NOT run by these tools.

* `mp_make_spec.py OUT.json` - the parity-precondition spec for `campaign_run.py`: one fixed-
  coordinate record per (fixture, plan, code) at soft@10, n-calls 3 (legacy jit whole vs core
  main asis, i.e. the bound analysis core's samplers call); core compared to legacy at 1e-12.
* `run_mock_proxy.sh PHASE...` - the 8 inference runs (`r1`, `r2`) through `gpu_run.sh`, serial,
  with compare_progress / compare_posteriors after each pair.
* `mp_manifest_append.py` - one `state/manifest.json` run entry per run record not yet listed.
* `mp_matrix.py` - `mock_proxy_matrix.csv` + `matrix.json` (runs, pairs, parity).
