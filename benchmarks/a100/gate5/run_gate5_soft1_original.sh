#!/bin/bash
# Gate 5 real GWTC-5 spectral-siren inference ladder (Fable's matrix; do not change).
# Data: A_pe_chieff_bbh259_n4096_v20.h5 + A_sel_chieffref_o3o4ab_v20.h5. nlive 1000, dlogz 0.1,
# seed 20260924, max_samples 0, tinyns preset recommended (jax_block_size 32), checkpointing off,
# single-pass blocks, soft guard at max_likelihood_variance 1.0 (hard 1.0 for the documentation runs),
# cold empty XLA cache per run, every run through gpu_run.sh, per-run timeout 4 h (SIGTERM -> status timeout).
set -u
R=/media/volume/tbs/darksirens_benchmark
G5=$R/benchmarks/gate5
H=$R/repos/darksirens-rebuild/benchmarks/a100
PE=$R/data/gwcat/exports/A_pe_chieff_bbh259_n4096_v20.h5
SEL=$R/data/gwcat/exports/A_sel_chieffref_o3o4ab_v20.h5
TIMEOUT_S=14400
B=gate1
M5B_H0="$B/m5b/records/M5B_legacy_whole_default_spectral_H0_gwtc5_bbh259_n4096_full_soft1 $B/m5b/records/M5B_core_whole_default_spectral_H0_gwtc5_bbh259_n4096_full_soft1 $B/m5b/records/M5B_core_asis_default_spectral_H0_gwtc5_bbh259_n4096_full_soft1"
M5B_FULL="$B/m5b/records/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_n4096_full_soft1 $B/m5b/records/M5B_core_whole_default_spectral_full_gwtc5_bbh259_n4096_full_soft1 $B/m5b/records/M5B_core_asis_default_spectral_full_gwtc5_bbh259_n4096_full_soft1"
M5_H0_HARD="$B/m5/records/M5_legacy_whole_default_spectral_H0_gwtc5_bbh259_n4096_full $B/m5/records/M5_core_whole_default_spectral_H0_gwtc5_bbh259_n4096_full $B/m5/records/M5_core_asis_default_spectral_H0_gwtc5_bbh259_n4096_full"
M2_FULL="$B/records/M2_legacy_whole_default_spectral_full_bbh259_n4096_full $B/records/M2_core_whole_default_spectral_full_bbh259_n4096_full $B/records/M2_core_asis_default_spectral_full_bbh259_n4096_full"
G4_O1_H0="gate4/records/G4_o1_asis_default_spectral_H0_gwtc5_A4096full_soft1 gate4/records/G4_o1_whole_default_spectral_H0_gwtc5_A4096full_soft1"
G4_O1_FULL="gate4/records/G4_o1_asis_default_spectral_full_gwtc5_A4096full_soft1 gate4/records/G4_o1_whole_default_spectral_full_gwtc5_A4096full_soft1"

run() {  # arm rung sampler guard
  local arm=$1 rung=$2 sampler=$3 guard=$4 impl env name refs extra=""
  case $arm in legacy) impl=legacy; env=$R/envs/env_legacy.sh;; main) impl=core; env=$R/envs/env_core.sh;;
               o1) impl=core; env=$R/envs/env_core_o1.sh; extra="--arm o1_experimental_perf_jit-bound-analysis_f825906";; esac
  name=G5_${arm}_r${rung}_${sampler}; [ "$guard" = hard ] && name=${name}_hard
  case $rung in 1) if [ "$guard" = hard ]; then refs=$M5_H0_HARD; else refs=$M5B_H0; fi;;
                5b) refs="$M5B_FULL $M2_FULL";; *) refs=$M5B_FULL;; esac
  if [ $arm = o1 ]; then case $rung in 1) refs="$refs $G4_O1_H0";; *) refs="$refs $G4_O1_FULL";; esac; fi
  [ $arm = main ] && extra="--arm core_main_88004d96"
  [ $arm = legacy ] && extra="--arm legacy_c042527"
  local pr=""; for r in $refs; do pr="$pr --parity-ref $r"; done
  local cdir=$R/xla_cache/runs/$name out=$G5/runs/$name
  if [ -e "$cdir" ] || [ -e "$out/record.json" ]; then echo "$(date -u +%FT%TZ) $name: cache or record exists, skipped"; return; fi
  mkdir -p "$cdir"
  local t0=$(date +%s.%N)
  echo "$(date -u +%FT%TZ) start $name"
  env -u PYTHONPATH -u JAX_PLATFORMS PYTHONDONTWRITEBYTECODE=1 $R/bin/gpu_run.sh $G5/smi/$name.smi.csv bash -c "source $env && cd $G5 && exec timeout -s TERM -k 300 $TIMEOUT_S python $H/infer_ladder.py --impl $impl --rung $rung --sampler $sampler --pe $PE --sel $SEL --nlive 1000 --dlogz 0.1 --seed 20260924 --max-samples 0 --guard $guard --max-variance 1.0 --tinyns-preset recommended --sel-batch none --pe-block none --out $out --device gpu --cache-dir $cdir --cache-mode cold --smi-log $G5/smi/$name.smi.csv --label $name $extra $pr" > $G5/logs/$name.stdout 2> $G5/logs/$name.stderr
  local rc=$?
  echo "$(date -u +%FT%TZ) end $name rc=$rc wall=$(python3 -c "import time;print(round(time.time()-$t0,1))") cache=$(du -sm $cdir | cut -f1)MB"
}
cmp() {  # A B tag [extra]
  local a=$G5/runs/$1 b=$G5/runs/$2 tag=$3; shift 3
  ( source $R/envs/env_core.sh; export JAX_PLATFORMS=cpu; python $H/compare_posteriors.py $a $b --out $G5/compare/$tag.json --md $G5/compare/$tag.md "$@" > $G5/compare/$tag.log 2>&1; echo "$(date -u +%FT%TZ) compare $tag rc=$?" )
}
echo "# start $(date -u +%FT%TZ) harness $(git -C $H rev-parse HEAD) dirty=$(git -C $H status --porcelain | wc -l)"
PHASE=${1:-all}
if [ $PHASE = all ] || [ $PHASE = a ]; then
 for rung in 1 2 3 4 5 5b; do
  run legacy $rung tinyns soft; run main $rung tinyns soft
  cmp G5_legacy_r${rung}_tinyns G5_main_r${rung}_tinyns tinyns_r${rung}_legacy_vs_main
 done
fi
if [ $PHASE = all ] || [ $PHASE = b ]; then
 run legacy 1 tinyns hard; run main 1 tinyns hard
 cmp G5_legacy_r1_tinyns_hard G5_main_r1_tinyns_hard tinyns_r1_hard_legacy_vs_main
fi
if [ $PHASE = all ] || [ $PHASE = c ]; then
 run main 1 dynesty soft
 for rung in 1 2 3 4 5 5b; do
  run legacy $rung dynesty soft
  [ $rung = 1 ] && cmp G5_legacy_r1_dynesty G5_main_r1_dynesty dynesty_r1_legacy_vs_main
 done
fi
if [ $PHASE = all ] || [ $PHASE = d ]; then
 run o1 5 tinyns soft
 cmp G5_legacy_r5_tinyns G5_o1_r5_tinyns tinyns_r5_legacy_vs_o1; cmp G5_main_r5_tinyns G5_o1_r5_tinyns tinyns_r5_main_vs_o1
 run o1 1 dynesty soft
 cmp G5_legacy_r1_dynesty G5_o1_r1_dynesty dynesty_r1_legacy_vs_o1; cmp G5_main_r1_dynesty G5_o1_r1_dynesty dynesty_r1_main_vs_o1
 run o1 5 dynesty soft
 cmp G5_legacy_r5_dynesty G5_o1_r5_dynesty dynesty_r5_legacy_vs_o1
fi
echo "# end $(date -u +%FT%TZ)"
