# Legacy test ownership and Phase-1 parity map

Reference: `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`.

The legacy `tests/fast_subset.txt` is the canonical CPU-fast gate: at the pinned state it records **69 files / 823 collected tests** on CPython 3.11.10, JAX 0.4.34 CPU, NumPy 1.26.4. It is explicitly the source of truth used by CI/documentation. We preserve its scientific intent but redistribute tests to their owners.

## Cross-domain golden bank

`tests/test_unified_k1_golden.py` + `tests/golden/unified_k1_golden.json` is the central Phase-1 reference.

It pins 15 K=1 fixed-coordinate cells covering:

```text
plain dark sirens
full-array and compact caller-view paths
deterministic Q_LSS
Q_LSS ensemble marginalization
marked hosts
live delta_g overdensity
anisotropic sky model
bright counterparts
complete catalog + both empty-pixel policies
spectral sirens
weak-lensing lognormal
field sky weighting
selection batching
```

It evaluates three deterministic coordinates/cell, requires `rtol <= 1e-12`, expects bit identity on the same backend, and has a second bank verifying each feature is live. Phase 1 must preserve the CPU reference bank before splitting cells by package ownership.

## CORE tests

### Import/packaging/runtime

From fast gate:

```text
test_no_deleted_import_paths.py          migration-only: replace with new contract
test_refactor_imports.py                 migration-only/reference
test_public_import_contract.py           rewrite around new root API
test_packaging_contract.py               port intent to src-layout packaging
test_import_side_effects.py              preserve
test_fast_subset_record.py               replace with per-repo manifests
test_jax_allocator_config.py             preserve
test_cold_import_precision.py            split core/lensing assertions by owner
test_xla_compilation_cache.py            preserve if runtime cache remains
```

`test_campaign_script_contract.py` is LEGACY_ONLY unless a migrated CLI/script needs its behavior.

### GW store/sample contract

Required anchors include:

```text
test_gwcat_v2_compat.py
test_store_layout_contract.py
test_array_shape_no_download.py
spin-basis / spin-block plumbing tests discovered in full suite
```

Phase 1 must explicitly freeze `chieff`, `chieff_reference`, component-spin basis, pdraw/PE prior semantics and malformed-file rejection.

### Selection

Fast gate and dedicated tests:

```text
test_selection_variance_guard.py
test_selection_gradient_safety.py
test_selection_soft_guard.py
test_selection_prior_model.py          transitional model-string behavior only
test_selection_batching.py
test_selection_correction_coefficient.py
test_spin_block_plumbing.py
```

`test_selection_correction_coefficient.py` pins the `N(N+3)` correction convention in both hard and soft guard branches. Preserve before redesign.

### Population

```text
test_population_fiducial_sets.py
test_population_support_contracts.py
test_gwtc5_fiducial_bpl2peaks.py
test_population_registry_golden.py
test_mass_pairing_support.py
test_gppop_population.py
```

`test_gppop_population.py` explicitly pins GP registration, parameter/prior contract, support, `(m1,q)` Jacobian and normalization. It belongs in core even though `tinygp` can remain optional.

### Ordinary catalog/redshift/completeness

```text
test_bright_siren_prior.py
test_catalog_prior_distance_table.py
test_completion_prior_strength.py
test_mask_free_criterion.py
test_complete_catalog_empty_pixel_policy.py
test_frozen_redshift_prior.py
test_redshift_prior_model.py
KDE window/batch tests where they exercise the ordinary catalog kernel
```

Selection-function runtime/fitting tests are split with surveys below.

### Parameters/inference/IO

```text
test_prior_defaults.py
test_parameter_table.py
test_joint_prior_constraints.py
test_pop_extractor_multitracer.py       core extension seam + LSS integration
test_dynesty_seed.py
test_sampler_zero_free_params.py
test_sampler_checkpoint_resume.py
test_tinyns_config.py
test_results_saving.py
test_run_provenance.py
test_run_fingerprint.py
test_result_atomicity_and_resume_provenance.py
```

Feature-specific lensing/LSS assertions inside shared files should be split into the owning companion tests rather than copied twice.

## SURVEYS tests

Primary ownership:

```text
test_completion_depth_map_build.py
test_build_mth_map.py
test_selection_fit_background_gate.py
```

Split ownership with core runtime evaluator:

```text
test_selection_kcorr.py
test_selection_schechter.py
test_selection_strata.py
test_completion_stratified.py
```

The rule is: fitting/constructing a selection/depth product from survey inputs belongs in surveys; evaluating the serialized model in inference belongs in core.

A new integration test must establish:

```text
small raw survey fixture
 -> darksirens-surveys
 -> standardized catalog HDF5
 -> darksirens.load_catalog
 -> arrays identical to the legacy standardized output
```

## LSS tests

Fast gate already includes the mature latent ladder:

```text
test_latent_field.py
test_q_provenance_guard.py
test_per_pixel_completeness.py
test_latent_counts.py
test_latent_anchor.py
test_latent_seam.py
test_latent_factory.py
```

Additional known LSS anchors from the full suite/review record include:

```text
test_latent_multitracer.py
test_latent_amp.py
test_latent_seam_e2e.py
test_latent_p13.py
test_latent_p17.py
test_latent_b_gal_dispersion.py
test_latent_solve_damping.py
test_latent_guards.py
```

Table/completion ownership from fast gate:

```text
test_completion_q_support_depth.py
test_lss_floor_conservation.py
test_per_pixel_clustering_cancellation.py
test_percatalog_selection.py
test_multitracer_selection.py
```

The field-level development reports explicitly identify `test_latent_counts.py`, `test_latent_anchor.py`, `test_latent_multitracer.py` and guard tests as physics pins. Treat the reports as provenance and the tests as migration assets.

Phase-1 LSS reference must record at minimum:

```text
Q_LSS rows and normalization
missing-galaxy count budget
single/multitracer table behavior
provenance refusal cases
latent basis/count likelihood
latent normalization
fixed-coordinate full likelihood cells from unified K=1 bank
```

## LENSING tests

Primary unit/contract tests include:

```text
test_lensing.py
test_lensing_file_contract.py
test_cluster_selection.py
test_lensed_singleton_channel.py
test_both_detected_approx_gate.py
test_inference_lensing_fixed_parameters.py
test_cli_wl_surface.py
test_lensing_cli_defects.py
test_simulation_config.py
test_ultra_lensing_labels.py
```

Validation/integration assets include:

```text
test_lensing_validation_script.py
test_lensing_evidence_validation_script.py
```

`test_lensed_singleton_channel.py` is especially important: it pins the independent-orientation convention and validates the analytic Finn-Chernoff detection/censoring factor against direct Monte Carlo of the mock rendering. This must migrate intact in scientific meaning.

Shared result/provenance/cold-import tests contain lensing-specific branches; move those branches to lensing while core retains generic behavior.

The `wl_lognormal` cell in the unified K=1 golden bank is the cross-package WL parity anchor.

## LEGACY_ONLY / TEST_ONLY analysis tests

Post-processing tests such as:

```text
test_analyze_fcat_weights.py
test_analyze_bayes_factors.py
test_dndz_ppd_shell_integral.py
```

are not prerequisites for the first core runtime. Keep as legacy/reference unless the corresponding reusable analysis API is intentionally migrated later.

## Phase-1 execution principle

Do not copy the whole legacy test directory and then patch imports until green. Instead:

1. freeze serialized legacy values/guards in a separate legacy process;
2. identify the scientific owner of each test;
3. port the smallest fixture required by that owner;
4. compare candidate values externally;
5. retain exact/bit-level tests where the legacy contract demands them.

For stochastic samplers, fixed-coordinate likelihood/selection parity is primary; seeded tiny runs test orchestration only.
