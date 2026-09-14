# Phase 11 L5 — lensed selection and exactly-one channel

Status: **ACCEPTED / FROZEN**

Date: 2026-09-14

## Frozen identities

Legacy numerical oracle:

```text
ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d
```

Frozen core:

```text
ignaciomagana/darksirens-core@af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
wheel: darksirens-0.1.0.dev0-py3-none-any.whl
artifact id: 10294880218
wheel SHA-256: 4a0d72072f3abd97edc71b9f1086ec50f4fba1de397a7db3c332775eaf970273
```

Accepted lensing production state:

```text
repository: ignaciomagana/darksirens-lensing
PR: #4
main SHA: 3dbb70eb989644cf26b47d411531e5c3a5b028fc
main tree: a20775812c0185c183985c5ddee4ebebcd4e7d75
version: 0.1.0
```

Frozen L0C-S reference:

```text
references/lensing_l0c_selection_legacy_reference.json
phases/11L0CS_selection_singleton_reference.md
```

## Scope accepted in L5

L5 reconstructs only the in-memory lensed selection arithmetic and the
exactly-one-detected event evidence. HDF5/file contracts, candidate graphs and
partition objects remain deliberately deferred to L6.

New production modules:

```text
src/darksirens_lensing/selection.py
src/darksirens_lensing/singleton_likelihood.py
```

The public package surface now exposes:

```text
LensedSelectionSet
make_lensed_selection_set
compute_cluster_selection_term
compute_lensed_single_selection_term
combine_shared_campaign_selection_statistics
combined_selection_log_correction
validate_campaign_cosmology
validate_pair_orientation
lensed_single_log_likelihood_event
```

## Scientific contracts frozen

### Source-campaign normalization

Both the J=2 both-detected subset and the exactly-one-detected subset are
normalized by the total number of source draws in their parent lensed campaign,
not by the number of retained rows.

### Pair tag ownership

An optional pair-tag factor multiplies the J=2 selection channel only. The
exactly-one channel has no pair-tag factor.

### Shared-campaign covariance

The both-detected and exactly-one subsets are mutually exclusive outcomes of the
same source draw. L5 therefore composes their Monte-Carlo variance with

```text
Cov(mu_hat_1L, mu_hat_2) = -mu_1L * mu_2 / N_draw_sources

Var(mu_hat_1L + mu_hat_2)
  = Var(mu_hat_1L) + Var(mu_hat_2)
    - 2 mu_1L mu_2 / N_draw_sources.
```

The ordinary unlensed campaign remains independent of this lensed campaign and
is combined by variance addition after the lensed covariance is applied.

### Fixed campaign cosmology

The mature legacy lensed-injection files contain pre-rendered detection subset
membership. They do **not** re-render image detection at each proposed
cosmology. L5 therefore stores the campaign cosmology in `LensedSelectionSet`
and fails closed when a caller supplies a different cosmology. Variable-
cosmology lensed selection would require a new rendering/emulator model and is
not a parity-preserving reconstruction.

### Orientation provenance

The rendered campaign's pair-orientation convention is explicit and checked.
The accepted modes remain:

```text
independent
shared_iota
```

Mixing conventions within one rendered campaign is rejected.

### Exactly-one event evidence

`lensed_single_log_likelihood_event` sums the two distinct SIS image-identity
branches. The partner image enters through the Finn-Chernoff censoring factor.
PE normalization uses the full PE row count, with invalid rows retained as
zero-weight draws, matching the mature implementation and frozen-core
Monte-Carlo variance semantics.

## Frozen numerical replay

The exact-core gate replays the L0C-S synthetic campaign:

```text
N_draw_sources = 300
both detected = 106
exactly one detected = 59
neither detected = 135
plus only = 59
minus only = 0
```

Accepted selection anchors:

```text
J=2:
  log mu      = -10.393679636707375
  N_eff       =   9.336650923921662
  log sigma^2 = -23.021306887896742

exactly-one:
  log mu      =  -9.985850690106737
  N_eff       =  18.14702555666866
  log sigma^2 = -22.870208046319068
```

Pair-tag half-probability anchor:

```text
Delta log mu      = -log(2)
Delta N_eff       = 0
Delta log sigma^2 = -2 log(2)
```

`A_tau = 0` kills both lensed selection channels exactly (`log mu = -inf`).

Accepted exactly-one event anchors (`N_PE=40`, `N_y=16`):

```text
independent/default:
  log L = -24.14280869121646
  MC variance = 0.03877501441781569

shared_iota:
  log L = -24.252969689017338
  MC variance = 0.03839011220180665

Delta log L(shared-independent) = -0.11016099780087885
```

The legacy pair-only combined-selection correction anchor is also preserved.

## Acceptance evidence

Temporary exact frozen-core gate:

```text
workflow run: 34798254015
job: 103835495569
result: SUCCESS
L5 exact-core tests: 3 passed
```

The temporary workflow was removed after acceptance; it is not part of the
production tree.

PR clean-wheel/ownership gate:

```text
workflow run: 34798275468
result: SUCCESS
L1 frozen tests: 9 passed
L3 frozen tests: 4 passed
L4 standalone tests: 3 passed
L5 standalone tests: 3 passed
ownership firewall: PASS
```

Post-merge main gate:

```text
workflow run: 34798388287
result: SUCCESS
```

The installed-wheel import firewall still proves that importing
`darksirens_lensing` does not import `darksirens`, `darksirens_surveys`, or
`darksirens_lss`.

## What is intentionally not in L5

Still deferred:

```text
lensed HDF5/file schemas and loaders
candidate graph contracts
exact partition enumeration/marginalization
time/image marks beyond the frozen L3 primitives and unmarked L4 pair surface
full partition-marginalized InferenceTarget
full fixed-theta core+lensing parity
final clean-install ecosystem freeze
```

## Next action

Proceed to **Phase 11 L6**:

1. freeze/port lensed file contracts and loaders without importing legacy runtime
   code;
2. reconstruct candidate graph representation;
3. reconstruct exact partition enumeration and bookkeeping;
4. preserve source-campaign identity/provenance so L5 shared-campaign covariance
   cannot be applied to unrelated injection campaigns;
5. keep core/surveys/LSS frozen and untouched.

Do not begin L7 until L6 file/partition contracts have their own accepted
reference and production gate.
