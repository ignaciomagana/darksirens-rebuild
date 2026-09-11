# End-to-end dark-siren closure and H100 benchmark

This directory contains a reconstruction-validation suite built around the
**frozen** scientific core:

```text
darksirens-core main = af2488b0ccb48c65e63cffcae306a8a4a4bfeb66
legacy oracle        = c042527238bd71421b792936bc48c3b815b90d6d
```

Nothing here changes `darksirens-core`.  The generator deliberately executes the
pinned legacy mock generator and bridges only its output serialization into the
current core/gwcat contracts.

## What is generated

`generate_mock_dark_siren_closure.py` executes the legacy DAG:

```text
complete galaxy population
        |
        +--> draw GW host galaxies BEFORE EM incompleteness
        |        |
        |        +--> PowerLaw+Peak masses/q/chi_eff + rate evolution
        |        +--> recorded noisy SNR
        |        +--> detection on that same recorded SNR
        |        +--> PE conditional on that same measurement
        |
        +--> EM survey selection
                 |
                 +--> magnitude/depth selection
                 +--> sigmoid redshift completeness
                 +--> realised photo-z
```

Selection injections use the same legacy measurement family and detection
threshold as the events.  The generator produces:

```text
gw_events.h5          gwcat-pe-2.0
gw_selection.h5       gwcat-selection-2.0
catalog_complete.h5   every galaxy, true z
catalog_incomplete.h5 observed survey catalog, realised photo-z
manifest.json         truth, sizes and provenance
legacy/               original pinned-legacy outputs
```

The PE/selection pair is strict-validated with the latest installed `gwcat`
before generation is considered successful.

The synthetic bridge uses gwcat **2.0 intentionally**.  `gwcat2` still denotes
2.0; 2.1 is an opt-in production provenance contract.  A direct synthetic
likelihood should not invent production campaign/prior provenance just to fill a
2.1 contract.

## Recommended validation realization

For an H100-scale closure test, use a catalog deep enough that the GW detection
horizon is inside the complete host catalog and place the true number density
inside, not on the edge of, core's `log10n0` prior:

```bash
python examples/generate_mock_dark_siren_closure.py \
  --outdir data/mock_closure \
  --n0 1.25e-4 \
  --zmax 0.50 \
  --nside 16 \
  --nobs 100 \
  --nsamp 1024 \
  --nselection 500000 \
  --nbatches 1 \
  --proposal population+uniform \
  --snr-ref 10 \
  --snr-threshold 8 \
  --survey-z50 0.30 \
  --survey-width 0.08 \
  --survey-magnitude-limit 21.0
```

If the frozen legacy checkout is not a sibling of `darksirens-rebuild`, add
`--legacy-root /path/to/darksirens`.  The wrapper refuses any legacy checkout
whose `HEAD` is not the pinned oracle SHA.

## Test 1: spectral likelihood performance

First isolate the GW likelihood with the injected PowerLaw+Peak population fixed:

```bash
python examples/spectral_sirens_gwcat_h100.py \
  --mock-dir data/mock_closure \
  --population powerlaw+peak \
  --fixed-population legacy \
  --h0-min 40 --h0-max 100 \
  --require-gpu \
  --benchmark-only \
  --likelihood-evals 100 \
  --xla-cache /scratch/$USER/darksirens-xla \
  --output-prefix perf/spectral_fixed
```

Then run the real joint spectral-siren population/cosmology fit:

```bash
python examples/spectral_sirens_gwcat_h100.py \
  --mock-dir data/mock_closure \
  --population powerlaw+peak \
  --h0-min 40 --h0-max 100 \
  --require-gpu \
  --nlive 1000 --dlogz 0.1 \
  --xla-cache /scratch/$USER/darksirens-xla \
  --output-prefix runs/spectral_joint
```

## Test 2: complete-catalog dark sirens

This is the machinery closure gate.  It uses **the same GW realization** but
gives the likelihood every possible host at true redshift.  The missing-host
branch is off.

```bash
python examples/dark_sirens_gwcat_h100.py \
  --mock-dir data/mock_closure \
  --catalog-mode complete \
  --population powerlaw+peak \
  --fixed-population legacy \
  --h0-min 40 --h0-max 100 \
  --require-gpu \
  --nlive 1000 --dlogz 0.1 \
  --xla-cache /scratch/$USER/darksirens-xla \
  --output-prefix runs/dark_complete_fixed
```

If this does not recover the injected H0, do **not** blame catalog
incompleteness: the problem is in the GW/catalog machinery, finite-realization
statistics, selection support, or the generative/inference contract.

## Test 3: incomplete-catalog dark sirens

Now activate the ordinary frozen completeness model on the observed catalog:

```bash
python examples/dark_sirens_gwcat_h100.py \
  --mock-dir data/mock_closure \
  --catalog-mode incomplete \
  --population powerlaw+peak \
  --fixed-population legacy \
  --h0-min 40 --h0-max 100 \
  --require-gpu \
  --nlive 1000 --dlogz 0.1 \
  --xla-cache /scratch/$USER/darksirens-xla \
  --output-prefix runs/dark_incomplete_fixed
```

Finally remove `--fixed-population legacy` to test simultaneous population + H0
inference through the full incomplete-catalog likelihood.

## What to compare

Every benchmark JSON records the data sizes, JAX device, core/gwcat revisions,
load/bind time, XLA compile + first evaluation, steady synchronized likelihood
time, likelihood evaluations/s, sampler wall time and evidence.  Dark-siren
outputs additionally record catalog size and, for generated mock data, H0 and
`log10n0` posterior quantiles relative to truth when those coordinates are
sampled.

The useful comparison table is therefore:

| run | scientific purpose | performance purpose |
|---|---|---|
| spectral / fixed pop | GW-only H0 closure | base likelihood cost |
| complete / fixed pop | catalog machinery closure | catalog compaction/kernel overhead |
| incomplete / fixed pop | incompleteness closure | completeness/cache overhead |
| spectral / sampled pop | spectral-siren science | high-dimensional sampler cost |
| incomplete / sampled pop | full dark-siren science | end-to-end production-like cost |

For GPU comparisons, use the **steady synchronized likelihood time**, not only
nested-sampling wall time.  The latter mixes accelerator throughput with the
sampler's host-side proposal/control flow.
