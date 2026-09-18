# Phase 12C — core review follow-up acceptance

## Status

**ACCEPTED / MERGED — NEW POST-12B CORE PIN**

Contract: `phases/12C_core_review_followup_contract.md` (the trigger, the
frozen reference, the deliberate numerics changes and which models they touch,
the guards that now raise, the mutation gates and the exact-head CI matrix are
recorded there and are not repeated here).

Phase 12C admits the confirmed findings of the adversarial parity review into
the production core. It does not reopen or reinterpret the frozen
reconstruction; every module with a CI parity probe remains exact against the
frozen reference, and the departures from the reference are the four deliberate
ones enumerated in the contract.

## Core implementation

Repository:

```text
ignaciomagana/darksirens-core
```

Starting Phase-12B core pin:

```text
bb4812dc2bf49fe7f4412ba797621b668ccc26a5
```

Six stacked PRs, squash-merged to `main` in order. For #13, #14 and #15 the
branch was rebased onto the freshly merged `main` immediately before its own
merge; each rebased head has the same tree as the accepted head the CI matrix
ran on, and each squash merge reproduced that tree exactly (verified at every
step before proceeding).

```text
PR #10  cosmology-grid prior guard; astropy and scipy anchors
        accepted head:  0f911120f70b57cebb23d6adb379e7404fc66e80
        squash merge:   4c0e960770551295858af340db0348b2c66faeaa
        tree:           dcce9a3e9727bee3fd378a8a09cf29c459d61e60

PR #16  empty-pixel default, evidence correction, pairing gate, guard mode
        (supersedes #11, closed by GitHub on base-branch deletion; same tree)
        accepted head:  1bd7cc9e8480454d57c6a30c5b90664c88e8300d
        squash merge:   8bb1fc251d2cd87b84ead38253ebbc0e9a2c9b6d
        tree:           9e361724af691c7d9b93bcef477a148c3e708d93

PR #12  fail-closed vocabularies, marked-host guards, likelihood anchors
        accepted head:  b7304adb3a2c5b7ad69bdbc8fd1901a6c46f74df
        squash merge:   ead47e2fc251a514f6697a86ba88157f1180d6e2
        tree:           26bd4bbb2256ad77e3aa3ed11d627fdd39ed1b24

PR #13  GP normaliser coordinates, x64 latching, pairing-grid guard, coverage
        accepted head:  2c8e64619f7edf997965c0c9b2e7490c32003cc4
        rebased head:   79449cee41f287d345ae4f7d9702a70bad0bc9da  (same tree)
        squash merge:   e0aad5d5be9d2ed92d0b814430abf549f43040ac
        tree:           25f0f5de6337f9bc4762f4a72c184e3493b2b1c5

PR #14  healpy-exact ang2pix_ring, angular anchors, real backends, packaging
        accepted head:  f5e070c71fbd104b92db64e0a4302962af88988e
        rebased head:   557d84c6555587dd4edfb1af14957ed1f7848231  (same tree)
        squash merge:   2cf6449f0cff7c8bc3520bcc67baf23fa5fd674d
        tree:           571bafc328354790d23bacc8af133c2b97218eed

PR #15  documentation of the post-freeze seams and the review follow-up
        accepted head:  2f89874f2824b1c150d6e24e8d67b32872d91f26
        rebased head:   23c4581e242f59b8aed2c6f9b4131b30b468cf5a  (same tree)
        squash merge:   8bf2bec53ff7b557c6b930d4044008cb72008f61
        tree:           18b3bf93ad506fb289e080160cbb20cbb03d58d0
```

New Phase-12 core pin / `main`:

```text
8bf2bec53ff7b557c6b930d4044008cb72008f61
tree: 18b3bf93ad506fb289e080160cbb20cbb03d58d0
```

`main` is linear: each squash merge has one parent, the previous one, back to
the Phase-12B pin `bb4812dc...`. The reconstruction freeze `af2488b0...` and the
12A/12B pins remain well-defined historical states.

## Production diff

Scientific source changes, all recorded per model in the contract:

```text
src/darksirens/_cosmology_support.py      (new leaf module; grid support constants)
src/darksirens/_specs.py                  (Cosmology refuses out-of-grid Om0/w0/wa)
src/darksirens/cosmology/distances.py     (grids built from the shared constants; import-time drift check)
src/darksirens/analysis.py                (CompleteCatalogRedshift.empty_policy, default "zero")
src/darksirens/catalog/models.py          (empty_policy default "zero")
src/darksirens/likelihood/hierarchical.py (empty_policy default "zero")
src/darksirens/inference/public.py        (selection guard mode; logZ_corrected on results)
src/darksirens/runtime_binding.py         (likelihood options; pairing gate; pairing-grid guard)
src/darksirens/gw/samples.py              (require_matching_contract, warn_pair_cosmology)
src/darksirens/inference/prior.py         (closed prior/constraint vocabularies)
src/darksirens/inference/target.py        (seam validation; explicit loc/scale)
src/darksirens/catalog/hosts.py           (shared-view and centring guards)
src/darksirens/likelihood/marked.py       (calls the shared-view guard)
src/darksirens/likelihood/host_density.py (redshift-parameter length check)
src/darksirens/selection/gw.py            (non-divisible batch raises)
src/darksirens/population/gp.py           (z nodes in log1p(z); support-following m1 table; 128-node q lattice)
src/darksirens/population/utils.py        (x64 before the module grids; comment repairs)
src/darksirens/population/registry.py     (ensure_pairing_grid_covers)
src/darksirens/population/__init__.py     (export)
src/darksirens/population/base.py         (comment repairs only)
src/darksirens/catalog/geometry.py        (healpy-exact RING pixelisation)
src/darksirens/inference/dynesty_diagnostics.py (ImportError names the extra)
```

Packaging and harness: `matplotlib==3.9.2` in the `dynesty` extra; the pinned
TinyNS plus Dynesty, NumPyro, Matplotlib and healpy in the `phase8-regression`
install; the new `real-backends` workflow; the Phase-4 spectral probe widened
past the tabulated distance range; a minimal `.gitignore`. Tests: nine new
modules and 3.3k added lines; the population golden bank gained two `@md`
entries with every pre-existing entry byte-identical.

## Exact-head acceptance matrix

Recorded in full in the contract. Summary: every PR-triggered workflow
succeeded on every accepted head (34 to 36 workflows per head, zero failures),
including on every head the Phase-5 pinned-legacy parity comparisons
(catalog kernel, ordinary completeness, ordinary dark siren, marked host,
catalog selection) and the widened Phase-4 spectral gate. On the code-final
head `9a87ffb` of #15:

```text
phase8-regression   35327952967  SUCCESS   714 passed, 1 skipped (golden regen guard)
real-backends       35327953066  SUCCESS   75 passed, 0 skipped
```

## Post-merge validation

Push-triggered workflows on merged `main` `8bf2bec5...`:

```text
real-backends        35368777346  SUCCESS
reference-integrity  35368777356  SUCCESS
```

## Scientific meaning

For any input the frozen reference accepted, and for every parametric
population model, the likelihood, selection and catalog numerics are unchanged
to the parity-gate tolerances. The four deliberate departures are: the
complete-catalog empty-row default returns to the frozen `zero`; the GP
z-conditional and m1-conditional normalisers now integrate to one inside the
prior box (previously off by up to 2.5x and 2.4e25); `ang2pix_ring` is
healpy-exact at ring boundaries and in the polar caps. Inputs the reference
refused are refused again, at the place the user typed them.

The DESI P12.4 fixed-population target uses a parametric population and the
conditional or field catalog estimators, none of which the numerics changes
touch. Its declared cosmology prior is inside the tabulated grid, so the new
guard admits it unchanged.

## Phase 12 dependency pin

The active core pin for Phase 12 production work is now:

```text
darksirens-core = 8bf2bec53ff7b557c6b930d4044008cb72008f61
```

The companion packages remain unchanged:

```text
darksirens-surveys = f027aef02d342041ce7259cdbf47fe689e6462f2
darksirens-lss     = 3429bb2f420239bc731cc9e73e50bf5351181c14
darksirens-lensing = 43c450742b733d7b8d938116021e8ca52a31226e
```

The consumer `ignaciomagana/desi_darksirens_selection` still pins
`bb4812dc...`. Any P12.1/P12.2/P12.2b/P12.3 provenance generated against that
pin is stale by construction once the consumer adopts the new pin and must be
regenerated before P12.4 numerical inference. Adopting the pin in the consumer
is a separate consumer PR under its own contract CI.

## Deferred, unchanged from the contract

The preflight remedy text (Phase 6G gate compares it verbatim); run-fingerprint
value normalisation; the dead phase8d freeze-gate trigger;
`selection_budget_audit`; the two hand-assembled legacy probe arms; making
`real-backends` a required check (branch protection).

## Verdict

Phase 12C is accepted and merged. Phase 12 production work may depend on the
new core SHA above. No new H0 posterior, interval or headline result is
accepted by this record.
