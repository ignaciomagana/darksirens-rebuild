#!/bin/bash
# status.sh WAIT_S DRIVERLOG : wait up to WAIT_S for a new driver line, then print a compact status
G=/media/volume/tbs/darksirens_benchmark/benchmarks/gate5
D=$G/$2; n0=$(wc -l < $D); end=$(( $(date +%s) + $1 ))
while [ $(date +%s) -lt $end ]; do [ $(wc -l < $D) -gt $n0 ] && break; sleep 10; done
date -u +%T; tail -n +2 $D | tail -6 | cut -c1-260
cur=$(ls -td $G/runs/*/ | head -1); echo "cur=$(basename $cur)"
tail -c 3000 $cur/run.log | tr "\r" "\n" | grep -o "iter=[0-9]* logz=[-0-9.]* dlogz=[0-9.e+]* ncall=[0-9]* logl_min=[-0-9.e+]* logl_live_max=[-0-9.e+]* repl_ncall=[0-9.]*" | tail -2
tail -c 3000 $cur/run.log | tr "\r" "\n" | grep -o "it=[0-9]* logz=[-0-9.]* dlogz=[-0-9.e+]* ncall=[0-9]*" | tail -1
[ -f $cur/progress.csv ] || python3 - "$cur" <<'PY' 2>/dev/null
import sys
PY
