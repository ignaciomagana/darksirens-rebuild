# Phase 6P checkpoint — Dynesty periodic diagnostics

## Reference

```text
legacy repository: ignaciomagana/darksirens
legacy SHA:        c042527238bd71421b792936bc48c3b815b90d6d
core repository:   ignaciomagana/darksirens-core
working branch:    rebuild/phase6-inference-io
accepted parent:   28c5f06ad0cc40d8fdbb587bcaa3e98dd89089b4
accepted 6P head:  73115e1d403e1c6eefa646c7e68867d6831dc7df
```

## Status

ACCEPTED AS A PHASE-6 SUBPHASE CHECKPOINT.

6P reconstructs only the optional periodic Dynesty diagnostic side effect and wires it into the accepted 6O execution adapter without changing sampling semantics.

Candidate surfaces:

```text
src/darksirens/inference/dynesty_diagnostics.py
src/darksirens/inference/dynesty_adapter.py
```

Frozen contract: diagnostic directory prefers `run_dir`, then `save_path`, then `.`; diagnostic plotting dependencies remain lazy unless enabled; the first pass waits one full 600-second interval; concurrent/torn `sampler.results` reads are skipped rather than killing the daemon; runplot and traceplot failures are contained independently; files are indexed as `runplot_####.pdf` / `traceplot_####.pdf`; the outer daemon catches any remaining diagnostic-pass exception; the diagnostics thread is daemonized; sampling always stops and joins it with a 120-second timeout in `finally`, including when `run_nested` raises.

An initial dedicated gate failure was only a legacy-probe isolation bug: the legacy-only process imported the candidate diagnostic module. Commit `73115e1d...` corrected the harness without changing source semantics.

## Acceptance

```text
dedicated 6P gate: 34578815115 / 103197379751 SUCCESS
historical gate:   34578815027 / 103197379324 SUCCESS
runtime guards:    34578815086 / 103197379648 SUCCESS
6O rerun:          34578815084 / 103197379721 SUCCESS
```

Dedicated acceptance includes 11 focused tests, lazy dependency checks, frozen legacy probing, reconstructed probing, and exact behavioral parity. The historical gate preserves all earlier Phase-6 parity and the Phase-5 scientific fixture comparison.

## Next

Proceed to 6Q: reconstruct only the static NumPyro/NUTS contract—bounds/prior compatibility, joint-constraint classification and warnings, and NUTS option resolution/validation. Keep initialization/gradient preflight and NUTS execution for later slices.
