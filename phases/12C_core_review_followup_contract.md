# Phase 12C — core review follow-up: guards, independent anchors, inherited-defect fixes

Status: **PROPOSED PACKAGE-CHANGE CONTRACT / NOT ACCEPTED / PRODUCTION PIN UNCHANGED**

Parent science phase: `phases/12_production_analysis_contract.md`

Active production core pin (unchanged by this record): `bb4812dc2bf49fe7f4412ba797621b668ccc26a5`

## Trigger

A 130-agent adversarial parity review of `darksirens-core` against the frozen
reference `ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d`
confirmed 40 findings (9 split, 9 refuted). Every module with a CI parity probe
was numerically exact against the frozen tree (cosmology kernels bit-identical
over 180 cosmologies x 17 redshifts). The confirmed damage sat where the gates
do not reach:

1. guards the reference enforced that the reconstruction had dropped rather
   than ported (cosmology priors outside the tabulated distance grid, unknown
   prior/constraint kinds, mismatched PE/injection contracts, uncentered or
   view-dependent host marks);
2. one true parity drift: the complete-catalog empty-row default had flipped
   from the frozen `zero` to `volume`;
3. two inherited GP normaliser defects (z tabulation on the wrong coordinate;
   a fixed m1 table interpolated across the taper toe), measured at up to 2.5x
   and 2.4e25 departure from unit normalisation inside the prior box;
4. a 543-test suite that could not fail on a physics change: removing the
   detector-to-source mass conversion left it fully green while `dlnL/dH0` on a
   spectral fixture moved from +0.07 to +0.009.

The follow-up was implemented as a stacked series of pull requests, each
carrying a test that fails on the review's own mutant, and independently
reviewed on GitHub before this record was written.

## Frozen scientific reference

```text
legacy repository:
  ignaciomagana/darksirens@c042527238bd71421b792936bc48c3b815b90d6d

reconstruction freeze (historical, unchanged):
  af2488b0ccb48c65e63cffcae306a8a4a4bfeb66

Phase-12B production pin (active, unchanged by this record):
  bb4812dc2bf49fe7f4412ba797621b668ccc26a5
```

## Proposed core change

Repository: `ignaciomagana/darksirens-core`

Merged to `main` already (guards and public API; no scientific arithmetic
change for any input the frozen reference accepted):

```text
PR #10  Review 1/6: guard cosmology priors against the distance grid; anchor the kernels
        accepted head:  0f911120f70b57cebb23d6adb379e7404fc66e80
        squash merge:   4c0e960770551295858af340db0348b2c66faeaa
        tree:           dcce9a3e9727bee3fd378a8a09cf29c459d61e60

PR #16  Review 2/6: empty-pixel default, evidence correction, store pairing gate, selection guard mode
        (supersedes #11, closed by GitHub on base-branch deletion; identical tree)
        accepted head:  1bd7cc9e8480454d57c6a30c5b90664c88e8300d
        squash merge:   8bb1fc251d2cd87b84ead38253ebbc0e9a2c9b6d
        tree:           9e361724af691c7d9b93bcef477a148c3e708d93
```

Open, stacked in merge order, each based on the previous:

```text
PR #12  Review 3/6: fail-closed vocabularies, marked-host guards, independent likelihood anchors
        head:  b7304adb3a2c5b7ad69bdbc8fd1901a6c46f74df   tree: 26bd4bbb2256ad77e3aa3ed11d627fdd39ed1b24

PR #13  Review 4/6: GP normaliser coordinates, x64 latching, pairing-grid guard, population coverage
        head:  2c8e64619f7edf997965c0c9b2e7490c32003cc4   tree: 25f0f5de6337f9bc4762f4a72c184e3493b2b1c5

PR #14  Review 5/6: healpy-exact ang2pix_ring, angular anchors, real sampler backends, packaging
        head:  f5e070c71fbd104b92db64e0a4302962af88988e   tree: 571bafc328354790d23bacc8af133c2b97218eed

PR #15  Review 6/6: document the post-freeze seams and the review follow-up
        head:  2f89874f2824b1c150d6e24e8d67b32872d91f26   tree: 18b3bf93ad506fb289e080160cbb20cbb03d58d0
        (code-final head 9a87ffb0f8b5e20761f1cb7545931142b754b737; the last commit records the CI matrix below and changes no code)
```

The tree at the head of #15 is the candidate post-12C core.

### Scientific numerics that change, and for which inputs

Everything below is a deliberate departure from the frozen reference, each
chosen over the frozen behavior for a stated, measured reason. No parametric
population model, no golden-bank entry and no CI parity probe cell moves.

1. **Complete-catalog empty-row default** (#16). `empty_policy` returns to the
   frozen `zero`; the reconstruction had flipped it to `volume`. Both branches
   are bit-identical to the reference; only the selected default differs, and
   it is now exposed on `ds.model(..., empty_policy=...)`. Affects any
   complete-catalog analysis whose catalog has galaxy-free rows.
2. **GP z-conditional normaliser** (#13). Tabulated in the GP coordinate
   `log1p(z)` on 145 nodes instead of uniformly in z on 40. Affects
   `gp2d_m1_z, gp2d_q_z, gp2d_chi_z, gp3d_m1_q_z, gp3d_m1_chi_z, gp3d_q_chi_z,
   gp4d, gp4d_additive`. Measured conditional-density departure from unity at
   the `ls_z` prior floor: up to 2.5x before, below 1% after. Cost: about 3x
   per proposal on these models (CPU, `gp4d` gradient 84 s to 284 s).
3. **GP m1-conditional q-normaliser** (#13). The m1 table follows the sampled
   taper toe, and the coarse (q, chi) lattice on that branch tabulates q on 128
   nodes instead of 24. Affects `gp1d_q, gp2d_q_chi, gp2d_q_z, gp3d_q_chi_z`.
   Measured: up to 2.4e25 just above `m_min` before; below 6e-3 after; the
   lattice defect the reviewer flagged (0.876 for `gp3d_q_chi_z` at
   `m1 = m_min + 0.25 dm_min` on an independent grid) is 1.001 after, at no
   measurable cost.
4. **HEALPix RING pixelisation** (#14). `ang2pix_ring` now reproduces
   `healpy.ang2pix` exactly (2.4 million comparisons, zero mismatches);
   previously wrong within about one ulp of ring boundaries, in the polar caps
   and for right ascensions just below a multiple of 2 pi.

### Behavior that becomes an error (was silent)

`ds.Cosmology` outside the tabulated grid support; unknown prior or
joint-constraint kinds; an `InferenceTarget` non-uniform prior without explicit
loc and scale; PE and injection stores with different `contract_hash`; marked-host
PE and selection views over different pixels without a shared reference table;
an uncentered mark table; a short `redshift_params` vector at the host-density
seam; a non-divisible selection batch on the provider path. Each matches a
guard the frozen reference enforced, except the explicit loc/scale rule, which
is stricter than the reference's `ParamSpec` default and applies only at the
companion seam.

### Everything else

Tests and probes only: astropy, scipy-quadrature, healpy and hand-computed
anchors; real TinyNS, Dynesty and NumPyro runs and a real Dynesty checkpoint
round-trip; a Phase 4 spectral probe that now covers the out-of-table distance
mask (pristine core matches legacy to 8.8e-15, the mask mutant fails by a factor
3); coverage for the `@md` rate evolution and the `in_prior_v2` fiducial set;
two `@md` entries appended to the population golden bank with every
pre-existing entry byte-identical.

## Acceptance gates

Mutation-based, recorded in each PR: every fix ships with a test that fails on
the review's own mutant and passes after. The load-bearing ones:

```text
dV_of_z without 1/E(z)             astropy anchor fails, ratio 4.95
ddL_of_z one-off in (1+z)          finite-difference anchor fails, ratio 0.91
m1src = m1det (no source frame)    pinned weight fails (0.58 rel), dlnL/dH0 0.070 -> 0.009
distance mask removed              Phase 4 probe fails, max rel 3.1
GP z nodes uniform in z            all 9 z-normalisation checks fail (up to 1.19)
fixed 64-node m1 table             toe probes fail (1.25 at m1 = m_min + 0.25 dm_min)
24-node q lattice, m1-conditional  independent-grid check fails (0.876)
ang2pix_ring pre-fix               12 of 49 healpy parity cases fail
soft guard without double-where    Neff = inf gradient is NaN
```

Parity re-established after the changes: Phase 2 cosmology probe legacy vs
candidate at rtol 0 (`max_abs = 0`); widened Phase 4 spectral probe at rtol
1e-12 (`max_rel = 8.8e-15`); every other `tools/probe_*.py` candidate output
byte-identical to the pre-stack tree.

Local full suite on the validated Hildafs stack (jax 0.4.34, numpy 1.26.4,
scipy 1.12.0, h5py 3.12.1, astropy 6.1.4, healpy 1.17.3, dynesty 2.1.4, numpyro
0.17.0, tinyns 3f9e1b2, tinygp 0.3.0), every optional backend installed:

```text
tree fcba6cf5 (code-final head of #15):  714 passed, 1 skipped (golden regen guard)
main before the stack:        543 passed, 1 skipped
```

Each stack level was also verified alone (touched modules plus the CI lint) on
its own tree before the PRs were opened.

### Exact-head CI matrix

GitHub Actions was blocked on account billing between 2026-09-18 08:51 and
09:05 UTC; every affected run was re-run after the repository was made public.
Every PR-triggered workflow completed successfully on every head below (34 to
36 workflows per head, zero failures). Load-bearing runs:

```text
main after #10 (4c0e960)  reference-integrity          35326494368  SUCCESS
main after #16 (8bb1fc2)  reference-integrity          35326699909  SUCCESS

#12 head b7304ad          reference-integrity          35327466047  SUCCESS
                          phase2-foundation            35327466015  SUCCESS
                          phase3-population            35327465998  SUCCESS
                          phase4-spectral-likelihood   35327465851  SUCCESS
                          phase5-catalog-dark-bright   35327465922  SUCCESS
                          phase7-regression            35327465987  SUCCESS
                          phase8-regression            35327466013  SUCCESS
                          phase8b-inference-target     35327465899  SUCCESS
                          phase8c-host-density         35327465914  SUCCESS

#13 head 2c8e646          reference-integrity          35327467856  SUCCESS
                          phase2-foundation            35327467858  SUCCESS
                          phase3-population            35327467822  SUCCESS
                          phase4-spectral-likelihood   35327467787  SUCCESS
                          phase5-catalog-dark-bright   35327467821  SUCCESS
                          phase7-regression            35327467881  SUCCESS
                          phase8-regression            35327467785  SUCCESS
                          phase8b-inference-target     35327467855  SUCCESS
                          phase8c-host-density         35327467783  SUCCESS

#14 head f5e070c          reference-integrity          35327467253  SUCCESS
                          phase2-foundation            35327467533  SUCCESS
                          phase3-population            35327467255  SUCCESS
                          phase4-spectral-likelihood   35327467158  SUCCESS
                          phase5-catalog-dark-bright   35327467103  SUCCESS
                          phase7c3-healpix-geometry    35327467109  SUCCESS
                          phase7-regression            35327467039  SUCCESS
                          phase8-regression            35327467040  SUCCESS  714 passed, 1 skipped
                          phase8b-inference-target     35327467047  SUCCESS
                          phase8c-host-density         35327467172  SUCCESS
                          real-backends                35327467082  SUCCESS

#15 head 9a87ffb          reference-integrity          35327953070  SUCCESS
                          phase2-foundation            35327952962  SUCCESS
                          phase3-population            35327952933  SUCCESS
                          phase4-spectral-likelihood   35327952991  SUCCESS
                          phase5-catalog-dark-bright   35327952955  SUCCESS
                          phase7c3-healpix-geometry    35327952939  SUCCESS
                          phase7-regression            35327952966  SUCCESS
                          phase8-regression            35327952967  SUCCESS  714 passed, 1 skipped
                          phase8b-inference-target     35327953246  SUCCESS
                          phase8c-host-density         35327953033  SUCCESS
                          real-backends                35327953066  SUCCESS  75 passed, 0 skipped
```

The Phase-5 workflow's pinned-legacy parity comparisons (catalog kernel,
ordinary completeness, ordinary dark siren, marked host, catalog selection)
and the widened Phase-4 spectral gate passed on every head, so the frozen
conditional catalog path and the spectral likelihood remain parity-exact
after the stack; the `real-backends` job ran the end-to-end TinyNS, Dynesty
and NumPyro tests, the real Dynesty checkpoint round-trip and the healpy
parity suite with no skip.

## Pin decision

The Phase-12B production pin `bb4812dc...` stays active. The DESI P12.4 target
uses a fixed parametric population, which no numerics change above touches, but
the production consumer must not move to the post-12C core until:

1. #12 through #15 are merged in order and their merge SHAs and trees recorded
   (the exact-head matrix above is complete and green);
2. the Phase-5 legacy parity workflow and the widened Phase-4 spectral gate are
   green on the merged head;
3. this record is promoted to an acceptance record with a new core pin.

## Deferred on purpose

- The nested-sampler preflight remedy text still names legacy CLI flags; the
  Phase 6G gate compares that message verbatim against the legacy tree, so
  rewording it is a gate decision, not a follow-up commit.
- Run-fingerprint value normalisation (review S02); the dead phase8d
  freeze-gate trigger (S04/S06); `selection_budget_audit` (S08); the two
  hand-assembled legacy probe arms (C26/C27). Each is a policy or scope call.
- Making `real-backends` a required check is a branch-protection setting.

## Verdict

**Not accepted.** This is the package-change contract for the review
follow-up. The exact-head CI matrix is complete and green; acceptance requires
the ordered merges and the recorded merge SHAs listed under the pin decision.
