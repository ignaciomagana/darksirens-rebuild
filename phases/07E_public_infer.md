# Phase 7E — thin public `infer()` facade

## Scope

Phase 7E exposes the conventional public execution seam over already accepted
runtime binding, prior transforms, and sampler dispatch. It introduces no new
likelihood arithmetic, sampler algorithm, result type, persistence convention,
or checkpoint filesystem policy.

Reference state:

```text
legacy repository:  ignaciomagana/darksirens
legacy SHA:         c042527238bd71421b792936bc48c3b815b90d6d
Phase-7 branch:     rebuild/phase7-public-api
7D accepted base:   1df8f78bb70371b9dae07c6a59a3c9fea2cc8e77
7E accepted head:   f8aa93ed8bd7c7ebae3fe009f5e05db92cde456e
accepted tree:      b109c62b9a80c64342a89e8c80a905f2270f98ca
```

## Accepted behavior

`src/darksirens/inference/public.py` adds a deliberately thin public facade:

1. call accepted 7D `bind_analysis`;
2. read the exact 7C2 parameter plan;
3. build accepted Phase-6 `make_prior_transform` from
   `lower`, `upper`, `prior_kinds`, and `joint_constraints`;
4. normalize public keyword options onto the existing attribute-based sampler
   contract with a `SimpleNamespace`;
5. delegate unchanged to accepted Phase-6 `run_sampler`;
6. return the existing standardized sampler result mapping directly.

The package-root `darksirens.infer` remains lazy and calls
`configure_jax_runtime()` only when inference is actually requested.

The facade creates no sampler class, no result wrapper, no run directory, and no
new backend-specific abstraction. Existing backend option names remain valid
(`tinyns_*`, `nuts_*`, and the existing Dynesty/shared fields).

Checkpointing remains off by default unless the caller supplies the already
resolved checkpoint fields consumed by Phase 6.

## Ordering invariant

The facade intentionally does **not** validate the sampler name before the
Phase-6 dispatcher. This preserves the accepted Phase-6 ordering in which a
zero-free analysis returns exact evidence before backend-name validation or
optional-backend imports.

The focused test pins this with an analysis containing zero free parameters and
`sampler="definitely-not-a-backend"`: exact evidence is returned and no Dynesty,
TinyNS, or NumPyro module is imported.

## Acceptance gates

Exact-head gates:

```text
public infer:       34623252701 / 103342078953  SUCCESS
broad regression:  34623252604 / 103342078653  SUCCESS
7D runtime binding:34623252608 / 103342078316  SUCCESS
7C2 public model:  34623252561 / 103342078490  SUCCESS
7C3 geometry:      34623252582 / 103342078443  SUCCESS
7C1 resolver:      34623252610 / 103342078721  SUCCESS
7B specs:          34623252606 / 103342078486  SUCCESS
7A loaders:        34623252591 / 103342078552  SUCCESS
```

The exact-head broad suite completed with:

```text
502 passed, 1 skipped
```

The skip is the existing opt-in population-registry golden regeneration test.
The companion-import boundary passed.

## Closure

Phase 7E is accepted at
`f8aa93ed8bd7c7ebae3fe009f5e05db92cde456e`.

The remaining legitimate Phase-7 scientific-core item is the reusable angular
source-population model surface. It must be migrated independently, parity-gated
against the pinned legacy sky registry/models, and only later wired into the
public parameter plan and fixed-theta likelihood. Do not mix angular-model
migration into `infer()`.