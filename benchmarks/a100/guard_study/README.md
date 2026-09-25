# guard_study: tools for the post-campaign selection-guard study

numpy-only helpers (no darksirens import, no JAX) for the study of the selection-N_eff guard
caps (hard / soft, max_likelihood_variance 1, 2, 5, 10, 20) in legacy darksirens c042527 and
darksirens-core O1 (perf/jit-bound-analysis f825906). The executable spec is
`$ROOT/benchmarks/guard_study/spec.json`, written by `gs_make_spec.py`.

| file | role |
|---|---|
| `gs_guard.py` | the shared guard formula in numpy (legacy `likelihood/selection.py:269-413` = core `selection/gw.py:270-414`); `validate`, `repro`, `curves`, `injections`, `inference`, `postmean-share` |
| `gs_coords.py` | coordinate files in the harness format: `h0grid` (rung-1 H0 wall map), `postmean` (posterior means of finished runs) |
| `gs_neff_subsample.py` | N_eff versus detected injections from a `bench_components.py` weight record (stride offsets, bootstrap) |
| `gs_make_spec.py` | writes `spec.json` and the `campaign_run.py` spec lists; `--dry-run-check` fills the equivalent GPU commands |
| `infer_ladder_nonfinite.patch` | optional observation-only counter of non-finite eager likelihood values (applied only if the user selects it) |

Checked on CPU before use: `gs_guard.py validate` reproduces the recorded selection correction
of the 30 M5b records (12 of them soft@1 / soft@10) to <= 2.5e-16 relative; the N_eff estimator of
`gs_neff_subsample.py` reproduces a components record's `e_sel_reduce` N_eff (bitwise at 8/9
coordinates, 3.6e-15 at the ninth); `bench_fixed_theta.py` accepts the `h0grid` and `postmean`
files in both codes (smoke data); the patched `infer_ladder.py` passes `tests/test_ladder_smoke.py`.
