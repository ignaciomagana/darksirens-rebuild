# Phase 11 L0D — lensing data / partition reference

Status: **ACCEPTED / FROZEN**

Date: 2026-09-14

## Frozen oracle

```text
legacy repository: ignaciomagana/darksirens
legacy SHA: c042527238bd71421b792936bc48c3b815b90d6d
probe: tools/probe_lensing_data_partitions.py
golden: references/lensing_l0d_data_partition_legacy_reference.json
workflow: .github/workflows/lensing-l0d-reference.yml
```

Bootstrap reference run:

```text
run: 34798679269
result: SUCCESS
artifact id: 10330348376
artifact zip SHA-256: 9296e016048cc4ce9adf658b04a13f76519aaea31189784464ea2910fb52d5da
```

Committed-golden replay:

```text
run: 34798749724
result: SUCCESS
repeated-process parity: PASS
committed-golden comparison: PASS
```

Golden commit:

```text
f361c2cc3c696162391b0ae2c771df6c519156fb
```

## Lensed-injection file contract frozen

The mature campaign is one HDF5 with one row per image. The J=2 both-detected
selection channel and the exactly-one-detected channel are **load-time views of
the same source campaign**, not independent injection campaigns.

Canonical per-image datasets are:

```text
source_id
image_id
m1_src
q_src
z_src
chieff
y_source
mu
detected
p_prop_src
p_prop_y
```

Optional pair/source diagnostics may be stored per image or per source where the
legacy loader permits it, including:

```text
log_p_tag_per_source / p_tag_per_source
snr_image0
snr_image1
delta_t_obs
true_delta_t
log_sky_overlap
p_tag_true
tagged_pair
```

The selection denominator is the **total source draws**. Both spellings below
are accepted by the mature reader:

```text
n_draw_sources
Ndraw_sources
```

The writer uses `n_draw_sources`. It validates the complete payload before disk
I/O and atomically replaces the destination only after a clean HDF5 close.
Malformed proposal densities, impossible tag probabilities and
`n_draw_sources < N_sources_in_file` fail before replacement.

## Pair / singleton view semantics

The loader sorts by `(source_id, image_id)` and requires exactly two images per
source with

```text
image_id = 0 -> mu_+
image_id = 1 -> mu_-
```

The two image rows must agree on every source-level field.

The both-detected view keeps only `det_plus & det_minus` sources.
The singleton view keeps only `det_plus XOR det_minus` sources and records

```text
mu_det
mu_partner
image_is_plus
```

In the frozen four-source fixture:

```text
source 0: both detected       -> pair view
source 1: plus only           -> singleton, image_is_plus=True
source 2: minus only          -> singleton, image_is_plus=False
source 3: neither detected    -> neither retained view

N_draw_sources = 10
pair n_kept = 1
singleton n_kept = 2
```

The missing `pair_orientation_mode` file attribute has legacy default
`independent`. An explicit `shared_iota` attribute is returned unchanged. The
Finn--Chernoff rendering attrs are also frozen:

```text
fc_rho_thr
fc_r0
fc_mc_bar
```

## Candidate-pair JSON contract frozen

Canonical format version:

```text
candidate-pairs-1.0
```

Required top-level information:

```text
n_events
pairs   # legacy alias candidate_pairs remains accepted
```

Each edge requires

```text
i
j
log_prior_odds
```

and may carry a label and `marks`.

Unordered endpoints are canonicalized `(min(i,j), max(i,j))`. Self-edges,
out-of-range endpoints, duplicate unordered edges and non-finite prior odds are
rejected.

Time marks are an inseparable pair:

```text
delta_t_obs
sigma_delta_t > 0
```

Known log marks plus custom keys beginning with `log_` are accepted. A
`folded_mark_keys` declaration prevents the same mark from being folded into
`log_prior_odds` a second time through runtime edge-prior keys.

## Exact partition semantics frozen

A partition is a graph matching: no event may appear in more than one selected
candidate edge. Its unnormalized log prior is

```text
sum(log_prior_odds of included effective edges).
```

The exact global enumerator uses deterministic edge-list DFS order and emits the
all-singleton state first.

The frozen six-event graph has components

```text
(events 0,1,2; edges 0,1) -> 3 local matchings
(events 3,4; edge 2)      -> 2 local matchings
(event 5; no edges)       -> 1 local matching
```

so the global product contains exactly six partitions. Global enumeration and
componentwise Cartesian composition have the same matching set and the same
partition-prior normalizer:

```text
log Z_partition_prior = 3.7281001672672174
```

The selected `log_sky_overlap` edge mark is added exactly once to each edge's
base prior odds. The oracle also freezes fail-closed behavior for

```text
folded-mark double counting
duplicate unordered candidate edges
incomplete time-mark pairs
max_partitions cap overflow
```

## L6 ownership boundary

L6 may now reconstruct, in `darksirens-lensing` only:

```text
canonical lensed-campaign HDF5 reader/writer + provenance
pair and exactly-one campaign views
candidate-pair JSON validation / mark bookkeeping
connected components
exact global and componentwise matching enumeration
partition-prior normalization
```

Do **not** copy the legacy CLI/factory or any core inference code. L7 owns the
partition-marginalized `InferenceTarget` integration.

The L5 fixed-campaign-cosmology rule remains in force: legacy detection flags
are pre-rendered. L6 must preserve campaign provenance strongly enough that L5
cannot accidentally combine pair and singleton subsets from unrelated source
campaigns.

## Next action

Proceed to **Phase 11 L6** in a fresh lensing branch, validate against this
committed L0D golden, merge only after clean-wheel / import-firewall CI and the
reference replay pass.
