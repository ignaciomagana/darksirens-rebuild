# Phase 11 L6 — campaign contracts and exact partitions

Status: **ACCEPTED / FROZEN**

Date: 2026-09-14

## Frozen identities

```text
legacy oracle: ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
L0D golden: references/lensing_l0d_data_partition_legacy_reference.json
lensing PR: #5
lensing main: 44ba42ce16a9b8cff803787e3f95f2e3439ad0ff
acceptance run: 34799072051 / 103837875978 SUCCESS
```

## Scope accepted

L6 reconstructs the startup/data layer only:

```text
src/darksirens_lensing/campaign.py
src/darksirens_lensing/partitions.py
```

It adds canonical per-image lensed-campaign HDF5 I/O; pair and exactly-one
views derived from one source-draw campaign; source-campaign provenance and a
semantic campaign fingerprint; candidate-pair JSON validation and edge-mark
bookkeeping; connected components; exact global matching enumeration; and exact
componentwise matching composition.

Partition likelihood / HBI integration is deliberately not in L6. That belongs
to L7.

## Campaign contract

The pair and exactly-one channels are views of one campaign. L6 therefore
returns them inside one `LensedCampaign` object, with shared

```text
n_draw_sources
pair_orientation_mode
campaign_fingerprint
campaign_id (optional)
campaign_cosmology (optional)
Finn-Chernoff rendering attrs
```

`campaign_fingerprint` is a SHA-256 semantic fingerprint of the canonical
source/image/detection campaign plus its total source-draw normalization. It is
independent of file path and row order. `assert_same_campaign()` rejects use of
the L5 shared-campaign covariance across unrelated campaigns.

Legacy files without cosmology provenance remain readable for diagnostics, but
`LensedCampaign.selection_sets()` fails closed until the campaign cosmology is
supplied explicitly. New files may stamp

```text
campaign_H0
campaign_Om0
campaign_w0
campaign_wa
campaign_id
pair_orientation_mode
```

The mature `n_draw_sources` / `Ndraw_sources` normalization alias is retained.
The legacy missing-orientation default remains `independent`.

The writer retains validation-before-I/O and atomic replacement semantics.

## Partition contract

L6 preserves the frozen L0D semantics exactly:

```text
candidate format: candidate-pairs-1.0
unordered pair canonicalization
folded-mark double-count protection
connected components including isolates
matching constraint: one selected edge per event at most
partition log prior: sum of included effective edge log_prior_odds
deterministic explicit-stack DFS order
all-singleton partition emitted first
componentwise/global matching-set equivalence
```

The legacy SciPy dependency was not copied: the only operation needed here is a
stable scalar `logsumexp`, implemented locally with NumPy. Runtime HDF5 support
adds `h5py` as the only new dependency.

## Frozen L0D replay

The six-event fixture reproduces:

```text
components: 3 x 2 x 1 local matchings
N_global_partitions = 6
log Z_partition_prior = 3.7281001672672174
```

The HDF5 fixture reproduces:

```text
N_draw_sources = 10
pair n_kept = 1
exactly-one n_kept = 2
single image identities = [plus, minus]
legacy orientation default = independent
legacy Ndraw_sources alias = accepted
```

Fail-closed tests cover malformed proposal densities, impossible tag
probabilities, too-small draw normalization, folded mark reuse, duplicate
unordered edges, incomplete time marks and partition-cap overflow.

## Acceptance

PR #5 clean-wheel run:

```text
34799072051 / 103837875978 SUCCESS
ownership firewall: PASS
L1 frozen tests: PASS
L3 frozen tests: PASS
L4 standalone tests: PASS
L5 standalone tests: PASS
L6 L0D-backed tests: PASS
```

Squash merge:

```text
44ba42ce16a9b8cff803787e3f95f2e3439ad0ff
```

Core, surveys and LSS were untouched.

## Next action

Proceed to **Phase 11 L7** only from this frozen L6 main. L7 owns the
partition-marginalized lensing `InferenceTarget` and must compose, rather than
reimplement:

```text
frozen core InferenceTarget seam
L4 pair likelihood
L5 exactly-one evidence + lensed selection/covariance
L6 exact partition states and campaign provenance
```

No legacy CLI/factory port is permitted. L8 remains the clean-install,
fixed-theta full core/lensing parity and final ecosystem freeze.
