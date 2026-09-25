#!/bin/bash
# Gate 5 ladder under Fable decision D-ladder (2026-09-24): soft selection-N_eff guard at
# max_likelihood_variance 10 for every ladder run (both codes and the O1 arm); the rung-1 TinyNS
# hard-guard-at-1.0 pair kept as specified. Budgets: stop at the first of dlogz 0.1, 2,000,000
# likelihood evaluations, 2 h sampling wall (status budget-capped); core-main (and O1) dynesty
# rung 1: 20,000 evaluations. Everything else as the original matrix: data n4096 + full, nlive
# 1000, dlogz 0.1, seed 20260924, max_samples 0, tinyns preset recommended (jax_block_size 32),
# checkpointing off, single-pass blocks, cold empty XLA cache per run, gpu_run.sh, 4 h backstop.
# D-ladder2 (2026-09-24, supersedes the budget above): stop at the first of dlogz 0.1 or 300,000 evaluations;
# 3600 s sampling wall as a safety only; core-main dynesty rung 1 keeps 20,000 evaluations; O1 arm on the
# 300,000 rule. New runs are named ..._e300k. The v1 script (2e6 / 7200 s) is run_gate5_dladder_v1.sh.
# usage: run_gate5_dladder.sh PHASE...   (a1 a2 b c d)
set -u
R=/media/volume/tbs/darksirens_benchmark
G5=$R/benchmarks/gate5
H=$R/repos/darksirens-rebuild/benchmarks/a100
PE=$R/data/gwcat/exports/A_pe_chieff_bbh259_n4096_v20.h5
SEL=$R/data/gwcat/exports/A_sel_chieffref_o3o4ab_v20.h5
TIMEOUT_S=14400
MAX_EVALS=300000
MAX_WALL=3600
POLICY="Fable D-ladder + D-ladder2 2026-09-24: soft guard cap 10 for all ladder runs (hard 1.0 only for the rung-1 tinyns documentation pair); budget: first of dlogz 0.1 or 300,000 evaluations, 3600 s sampling wall as a safety only (core-main dynesty rung 1: 20,000 evaluations)"
S10=gate1/m5b/soft10/records
P_H0="$S10/M5B_legacy_whole_default_spectral_H0_gwtc5_bbh259_n4096_full_soft10 $S10/M5B_core_whole_default_spectral_H0_gwtc5_bbh259_n4096_full_soft10 $S10/M5B_core_asis_default_spectral_H0_gwtc5_bbh259_n4096_full_soft10"
P_FULL="$S10/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_n4096_full_soft10 $S10/M5B_core_whole_default_spectral_full_gwtc5_bbh259_n4096_full_soft10 $S10/M5B_core_asis_default_spectral_full_gwtc5_bbh259_n4096_full_soft10"
P_H0_HARD="gate1/m5/records/M5_legacy_whole_default_spectral_H0_gwtc5_bbh259_n4096_full gate1/m5/records/M5_core_whole_default_spectral_H0_gwtc5_bbh259_n4096_full gate1/m5/records/M5_core_asis_default_spectral_H0_gwtc5_bbh259_n4096_full"
P_PLP="gate1/records/M2_legacy_whole_default_spectral_full_bbh259_n4096_full gate1/records/M2_core_whole_default_spectral_full_bbh259_n4096_full gate1/records/M2_core_asis_default_spectral_full_bbh259_n4096_full"
P_O1_H0="gate4/records/G4_o1_asis_default_spectral_H0_gwtc5_A4096full_soft1 gate4/records/G4_o1_whole_default_spectral_H0_gwtc5_A4096full_soft1"
P_O1_FULL="gate4/records/G4_o1_asis_default_spectral_full_gwtc5_A4096full_soft1 gate4/records/G4_o1_whole_default_spectral_full_gwtc5_A4096full_soft1"

nm() { local arm=$1 rung=$2 sampler=$3 guard=$4; if [ $guard = hard ]; then echo G5_${arm}_r${rung}_${sampler}_hard1_e300k; else echo G5_${arm}_r${rung}_${sampler}_soft10_e300k; fi; }

run() {  # arm rung sampler guard [max_evals]
  local arm=$1 rung=$2 sampler=$3 guard=$4 mev=${5:-$MAX_EVALS} impl env armlbl refs cap
  case $arm in legacy) impl=legacy; env=$R/envs/env_legacy.sh; armlbl=legacy_c042527;;
               main) impl=core; env=$R/envs/env_core.sh; armlbl=core_main_88004d96;;
               o1) impl=core; env=$R/envs/env_core_o1.sh; armlbl=o1_EXPERIMENTAL_perf-jit-bound-analysis_f825906_not_merged;; esac
  if [ $guard = hard ]; then cap=1.0; refs=$P_H0_HARD; else cap=10.0
    case $rung in 1) refs=$P_H0;; 5b) refs="$P_FULL $P_PLP";; *) refs=$P_FULL;; esac; fi
  if [ $arm = o1 ]; then case $rung in 1) refs="$refs $P_O1_H0";; *) refs="$refs $P_O1_FULL";; esac; fi
  local name; name=$(nm $arm $rung $sampler $guard)
  local pr=""; for r in $refs; do pr="$pr --parity-ref $r"; done
  local cdir=$R/xla_cache/runs/$name out=$G5/runs/$name
  if [ -e "$cdir" ] || [ -e "$out/record.json" ]; then echo "$(date -u +%FT%TZ) $name: cache or record exists, skipped"; return; fi
  mkdir -p "$cdir"
  local t0=$(date +%s.%N)
  echo "$(date -u +%FT%TZ) start $name (guard $guard cap $cap max_evals $mev max_wall_s $MAX_WALL)"
  env -u PYTHONPATH -u JAX_PLATFORMS PYTHONDONTWRITEBYTECODE=1 $R/bin/gpu_run.sh $G5/smi/$name.smi.csv bash -c "source $env && cd $G5 && exec timeout -s TERM -k 300 $TIMEOUT_S python $H/infer_ladder.py --impl $impl --rung $rung --sampler $sampler --pe $PE --sel $SEL --nlive 1000 --dlogz 0.1 --seed 20260924 --max-samples 0 --guard $guard --max-variance $cap --tinyns-preset recommended --sel-batch none --pe-block none --out $out --device gpu --cache-dir $cdir --cache-mode cold --smi-log $G5/smi/$name.smi.csv --label $name --arm $armlbl --max-evals $mev --max-wall-s $MAX_WALL --policy-note '$POLICY' $pr" > $G5/logs/$name.stdout 2> $G5/logs/$name.stderr
  local rc=$?
  local st; st=$(python3 -c "import json;r=json.load(open('$out/record.json'));print(r['status'], (r.get('budget') or {}).get('stop_reason'))" 2>/dev/null)
  echo "$(date -u +%FT%TZ) end $name rc=$rc status=[$st] wall=$(python3 -c "import time;print(round(time.time()-$t0,1))") cache=$(du -sm $cdir | cut -f1)MB"
}
cmp() {  # nameA nameB tag
  local a=$G5/runs/$1 b=$G5/runs/$2 tag=$3
  [ -f $a/record.json ] && [ -f $b/record.json ] || { echo "$(date -u +%FT%TZ) compare $tag: missing record"; return; }
  ( source $R/envs/env_core.sh; export JAX_PLATFORMS=cpu
    python $H/compare_progress.py $a $b --out $G5/compare/$tag.progress.json --md $G5/compare/$tag.progress.md > $G5/compare/$tag.progress.log 2>&1
    echo "$(date -u +%FT%TZ) compare_progress $tag rc=$? $(tail -1 $G5/compare/$tag.progress.log | cut -c1-240)"
    sa=$(python3 -c "import json;print(json.load(open('$a/record.json'))['status'])"); sb=$(python3 -c "import json;print(json.load(open('$b/record.json'))['status'])")
    if [ "$sa" = ok ] && [ "$sb" = ok ]; then
      python $H/compare_posteriors.py $a $b --out $G5/compare/$tag.json --md $G5/compare/$tag.md > $G5/compare/$tag.log 2>&1
      echo "$(date -u +%FT%TZ) compare_posteriors $tag rc=$?"
    else echo "$(date -u +%FT%TZ) compare_posteriors $tag skipped (status $sa / $sb: posterior comparison only for converged pairs)"; fi )
}
pair() {  # rung sampler guard
  run legacy $1 $2 $3; run main $1 $2 $3
  cmp $(nm legacy $1 $2 $3) $(nm main $1 $2 $3) ${2}_r${1}_$3_legacy_vs_main
}
echo "# start $(date -u +%FT%TZ) phases: $* harness $(git -C $H rev-parse HEAD) dirty=$(git -C $H status --porcelain | wc -l)"
for PHASE in "$@"; do
 case $PHASE in
  a1) pair 1 tinyns soft;;
  a2) for rung in 2 3 4 5 5b; do pair $rung tinyns soft; done;;
  b)  pair 1 tinyns hard;;
  c)  run main 1 dynesty soft 20000
      for rung in 1 2 3 4 5 5b; do run legacy $rung dynesty soft; done
      cmp $(nm legacy 1 dynesty soft) $(nm main 1 dynesty soft) dynesty_r1_soft_legacy_vs_main;;
  d)  run o1 5 tinyns soft
      cmp $(nm legacy 5 tinyns soft) $(nm o1 5 tinyns soft) tinyns_r5_soft_legacy_vs_o1
      cmp $(nm main 5 tinyns soft) $(nm o1 5 tinyns soft) tinyns_r5_soft_main_vs_o1
      run o1 1 dynesty soft
      cmp $(nm main 1 dynesty soft) $(nm o1 1 dynesty soft) dynesty_r1_soft_main_vs_o1
      cmp $(nm legacy 1 dynesty soft) $(nm o1 1 dynesty soft) dynesty_r1_soft_legacy_vs_o1
      run o1 5 dynesty soft
      cmp $(nm legacy 5 dynesty soft) $(nm o1 5 dynesty soft) dynesty_r5_soft_legacy_vs_o1;;
  *) echo "unknown phase $PHASE";;
 esac
done
echo "# end $(date -u +%FT%TZ)"
