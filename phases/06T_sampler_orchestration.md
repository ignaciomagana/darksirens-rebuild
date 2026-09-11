# Phase 6T — sampler orchestration

Status: **ACCEPTED**

```text
legacy reference: c042527238bd71421b792936bc48c3b815b90d6d
core parent:      b620601e1a0cc776f7d9090c866e299f2138fbff
accepted head:    d3e8dcdbf107d881405d1f14badab7bd0ea4d74f
branch:           rebuild/phase6-inference-io
```

## Scope

6T reconstructs only the thin top-level sampler orchestration seam. It does not
recreate the frozen `inference/sampling.py` monolith.

The accepted dispatcher preserves:

- the zero-free exact-evidence short circuit before sampler-method validation or
  any backend import;
- nested Dynesty/TinyNS checkpoint planning before fresh-run preflight;
- frozen resume behavior, including the exact preflight-skipped message;
- TinyNS delegation to accepted 6M/6N machinery;
- Dynesty delegation to accepted 6E/6F/6O/6P machinery;
- NumPyro composition through accepted 6Q static planning, 6R initialization and
  gradient preflight, then 6S execution;
- lazy backend/JAX imports;
- the frozen positive-dimensional unknown-sampler error.

## Acceptance

All required gates passed on the exact accepted head:

```text
dedicated dispatcher parity: 34590483237 / 103234397114 SUCCESS
runtime guards:              34590482964 / 103234396617 SUCCESS
historical/scientific gate:  34590483006 / 103234396701 SUCCESS
```

The broad gate passed the reconstructed test suite, dependency-boundary checks,
exact 6A–6F replay, pinned/reconstructed Phase-5 fixture generation, and exact
preservation of Phase-5 scientific parity.

## Phase-6 inference-surface closure audit

After 6T, every file under the frozen legacy `darksirens/inference/` tree was
classified so Phase 6 does not remain open merely because the old package
co-located construction, survey, LSS and sampler code.

| Frozen legacy file | Reconstruction disposition |
|---|---|
| `__init__.py` | Public exports belong to the Phase-7/8 root/API work, not sampler reconstruction. |
| `checkpointing.py` | Phase 6: reconstructed across checkpoint planning plus backend checkpoint state. |
| `data.py` | The frozen implementation is staged survey/LSS/multitracer/campaign assembly. Reimplement the ordinary public loading/model-construction facade in Phase 7; extension-owned parts remain outside core. |
| `loaders.py` | Split boundary: standardized ordinary loaders/public facade in Phase 7; staged survey construction is surveys-owned; Q/LSS/multitracer construction is LSS-owned. Do not port this module wholesale. |
| `parameters.py` | The frozen mega `ParameterDecoder` mixes core, per-catalog selection, sky/marks, LSS and lensing state. Phase 7 owns the small composable core parameter/model assembly and extension seam; no Phase-6 port is justified. |
| `pop_extractor.py` | Generic population-coordinate mapping is Phase-7 model/result assembly; multitracer stick post-processing is LSS-owned. The frozen helper is coupled to the legacy parameter switchboard and is not a missing sampler primitive. |
| `prior.py` | Phase 6 reconstructed the portable sampler-facing unit-cube transform. The remaining model/parameter-space registry belongs to Phase-7 composable model/prior assembly rather than the legacy `universe_model` switchboard. |
| `q_provenance.py` | LSS-owned by architecture; core must not learn Q_LSS provenance. |
| `run_fingerprint.py` | Phase 6: reconstructed semantic resume/provenance gate. |
| `sampling.py` | Phase 6: decomposed across 6D–6T with exact frozen-behavior gates; the monolith is intentionally not recreated. |
| `tinyns_config.py` | Phase 6M/6N. |
| `utils.py` | Its portable canonical Jacobian / sample-weight mathematics was already migrated in Phase 4 to `darksirens/likelihood/weights.py`; other helpers follow their physical owners. |
| `validation.py` | The frozen function is multitracer/config-assembly validation. Generic construction validation belongs to Phase 7; multitracer-specific invariants belong to the LSS extension boundary. It is not sampler infrastructure. |

## Conclusion

There is **no Phase 6U functional slice**. Portable sampler, checkpoint, result,
and provenance infrastructure is complete at 6T. Remaining core-owned inference
construction work is deliberately Phase 7 (`model`, `infer`, ordinary loaders,
small parameter/prior assembly, angular model), while Q/multitracer/LSS and
lensing-specific state stay with companion packages.

The next action is the Phase-6 completion/integration audit against the Phase-5
`main` base, followed by the Phase-6 PR/merge and post-merge validation. Phase 7
must not start before that checkpoint is recorded.
