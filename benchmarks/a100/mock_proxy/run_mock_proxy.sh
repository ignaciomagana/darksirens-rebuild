#!/bin/bash
# Mock-proxy dark-siren ladder (Fable spec 2026-09-25; MOCK fixtures only, Gate 6 real dark sirens is a hard stop).
# dynesty, nlive 1000, dlogz 0.1, seed 20260924, max_samples 0, checkpointing off, soft guard cap 10 in both codes.
# Budget: first of dlogz 0.1, 300,000 likelihood evaluations, 7200 s sampling wall; 9000 s timeout backstop.
# R1 single pass; R2 sel_batch 4096 / pe_event_block 6 in both codes + legacy --row_chunk 2048. Cold XLA cache per run.
# usage: run_mock_proxy.sh PHASE...   (r1 r2)
set -u
R=/media/volume/tbs/darksirens_benchmark
MP=$R/benchmarks/mock_proxy
H=$R/repos/darksirens-rebuild/benchmarks/a100
TIMEOUT_S=9000
MAX_EVALS=300000
MAX_WALL=7200
POLICY="Fable mock-proxy ladder spec 2026-09-25: dynesty nlive 1000 dlogz 0.1 seed 20260924; soft selection-N_eff guard cap 10 in both codes; budget = first of convergence (dlogz 0.1), 300,000 likelihood evaluations, 7200 s sampling wall (R2 ~0.45 s per evaluation); 9000 s timeout backstop; R1 single pass, R2 blocks 4096/6 (+ legacy --row_chunk 2048); cold cache; MOCK fixtures only"
mkdir -p $MP/runs $MP/logs $MP/smi $MP/compare
nm() { echo MP_$1_$2_$3_dynesty_soft10; }   # arm fixture plan
run() {  # arm fixture plan
  local arm=$1 fx=$2 plan=$3 impl env armlbl cat blk="" rc_arg=""
  case $arm in legacy) impl=legacy; env=$R/envs/env_legacy.sh; armlbl=legacy_c042527;;
               main) impl=core; env=$R/envs/env_core.sh; armlbl=core_main_43d273f;; esac
  case $fx in R1) cat=catalog_pixelated_nside_64.h5; blk="--sel-batch none --pe-block none";;
              R2) cat=catalog_pixelated_nside_128.h5; blk="--sel-batch 4096 --pe-block 6"; [ $arm = legacy ] && rc_arg="--row-chunk 2048";; esac
  local blocks=single; [ $fx = R2 ] && blocks=b4096x6
  local pr="--parity-ref mock_proxy/parity/records/MPP_legacy_whole_${blocks}_${plan}_${fx}_soft10 --parity-ref mock_proxy/parity/records/MPP_core_asis_${blocks}_${plan}_${fx}_soft10"
  local D=$R/data/mock/$fx name; name=$(nm $arm $fx $plan)
  local cdir=$R/xla_cache/runs/$name out=$MP/runs/$name
  if [ -e "$cdir" ] || [ -e "$out/record.json" ]; then echo "$(date -u +%FT%TZ) $name: cache or record exists, skipped"; return; fi
  mkdir -p "$cdir"
  local t0=$(date +%s.%N)
  echo "$(date -u +%FT%TZ) start $name ($blk $rc_arg)"
  env -u PYTHONPATH -u JAX_PLATFORMS PYTHONDONTWRITEBYTECODE=1 $R/bin/gpu_run.sh $MP/smi/$name.smi.csv bash -c "source $env && cd $MP && exec timeout -s TERM -k 300 $TIMEOUT_S python $H/infer_ladder.py --impl $impl --plan $plan --catalog $D/$cat --sampler dynesty --pe $D/mock_gw_events.h5 --sel $D/mock_gw_selection.h5 --nlive 1000 --dlogz 0.1 --seed 20260924 --max-samples 0 --guard soft --max-variance 10 $blk $rc_arg --out $out --device gpu --cache-dir $cdir --cache-mode cold --smi-log $MP/smi/$name.smi.csv --label $name --arm $armlbl --max-evals $MAX_EVALS --max-wall-s $MAX_WALL --policy-note '$POLICY' $pr" > $MP/logs/$name.stdout 2> $MP/logs/$name.stderr
  local rc=$?
  local st; st=$(python3 -c "import json;r=json.load(open('$out/record.json'));print(r['status'], (r.get('budget') or {}).get('stop_reason'))" 2>/dev/null)
  echo "$(date -u +%FT%TZ) end $name rc=$rc status=[$st] wall=$(python3 -c "import time;print(round(time.time()-$t0,1))") cache=$(du -sm $cdir | cut -f1)MB"
}
cmp() {  # nameA nameB tag
  local a=$MP/runs/$1 b=$MP/runs/$2 tag=$3
  [ -f $a/record.json ] && [ -f $b/record.json ] || { echo "$(date -u +%FT%TZ) compare $tag: missing record"; return; }
  ( source $R/envs/env_core.sh; export JAX_PLATFORMS=cpu
    python $H/compare_progress.py $a $b --out $MP/compare/$tag.progress.json --md $MP/compare/$tag.progress.md > $MP/compare/$tag.progress.log 2>&1
    echo "$(date -u +%FT%TZ) compare_progress $tag rc=$? $(tail -1 $MP/compare/$tag.progress.log | cut -c1-240)"
    sa=$(python3 -c "import json;print(json.load(open('$a/record.json'))['status'])"); sb=$(python3 -c "import json;print(json.load(open('$b/record.json'))['status'])")
    if [ "$sa" = ok ] && [ "$sb" = ok ]; then
      python $H/compare_posteriors.py $a $b --out $MP/compare/$tag.json --md $MP/compare/$tag.md > $MP/compare/$tag.log 2>&1
      echo "$(date -u +%FT%TZ) compare_posteriors $tag rc=$?"
    else echo "$(date -u +%FT%TZ) compare_posteriors $tag skipped (status $sa / $sb: posterior comparison only for converged pairs)"; fi )
}
pair() {  # fixture plan
  run legacy $1 $2; run main $1 $2
  cmp $(nm legacy $1 $2) $(nm main $1 $2) ${1}_${2}_legacy_vs_main
}
echo "# start $(date -u +%FT%TZ) phases: $* harness $(git -C $H rev-parse HEAD) dirty=$(git -C $H status --porcelain | wc -l)"
for PHASE in "$@"; do
 case $PHASE in
  r1) pair R1 dark_H0; pair R1 dark_full;;
  r2) pair R2 dark_H0; pair R2 dark_full;;
  *) echo "unknown phase $PHASE";;
 esac
done
echo "# end $(date -u +%FT%TZ)"
