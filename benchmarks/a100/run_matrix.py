#!/usr/bin/env python3
"""Run the legacy / core-whole / core-asis matrix for a set of plans and compare.

    python run_matrix.py --legacy-python L --core-python C --pe PE.h5 --sel SEL.h5 \\
        --plans spectral_H0,spectral_pop,spectral_joint_small,spectral_full \\
        --seed 20260924 --n 8 --outdir DIR --tag T [--device cpu] \\
        [--sel-batch none] [--pe-block none] [--n-calls 20] [--parallel 1] \\
        [--wrap "/path/gpu_run.sh {smi}"] [--cold-cache-root DIR] [--catalog CAT.h5]

For every plan: make_coords.py, then bench_fixed_theta.py for legacy (factory
kernel), core --jit whole and core --jit asis, then compare_records.py for
legacy vs core-whole, legacy vs core-asis and core-whole vs core-asis. Writes
``DIR/<tag>_index.json`` listing every record, summary and return code.

``--wrap`` prefixes every benchmark process (``{smi}`` is replaced by a per-run
nvidia-smi log path), e.g. the campaign's ``gpu_run.sh``. GPU runs must use
``--parallel 1``. ``--cold-cache-root DIR`` gives every benchmark process its own
empty persistent XLA cache ``DIR/<run name>`` (``--cache-mode cold``), so each
first call is a true compile.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd, env, log):
    t0 = time.time()
    with open(log, "w") as f:
        f.write("# " + " ".join(shlex.quote(c) for c in cmd) + "\n")
        f.flush()
        rc = subprocess.run(cmd, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    return {"cmd": cmd, "rc": rc, "log": log, "wall_s": time.time() - t0}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--legacy-python", required=True)
    ap.add_argument("--core-python", required=True)
    ap.add_argument("--pe", required=True)
    ap.add_argument("--sel", required=True)
    ap.add_argument("--plans", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--device", default="cpu", choices=("cpu", "gpu", "auto"))
    ap.add_argument("--sel-batch", default="none")
    ap.add_argument("--pe-block", default="none")
    ap.add_argument("--n-calls", type=int, default=20)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--wrap", default=None)
    ap.add_argument("--impls", default="legacy:whole,core:whole,core:asis")
    ap.add_argument("--util-window-s", type=float, default=0.0)
    ap.add_argument("--cold-cache-root", default=None,
                    help="per-run empty JAX_COMPILATION_CACHE_DIR under this root")
    ap.add_argument("--catalog", default=None,
                    help="pixelated galaxy catalog, passed to the dark_* plans only")
    a = ap.parse_args(argv)

    os.makedirs(a.outdir, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    if a.device == "cpu":
        env["JAX_PLATFORMS"] = "cpu"
    plans = [p for p in a.plans.split(",") if p]
    impls = [tuple(x.split(":")) for x in a.impls.split(",") if x]
    py = {"legacy": a.legacy_python, "core": a.core_python}

    index = {"tag": a.tag, "argv": [sys.executable] + sys.argv, "pe": a.pe, "sel": a.sel,
             "seed": a.seed, "runs": {}, "compares": {}}
    jobs = []
    for plan in plans:
        coords = os.path.join(a.outdir, f"{a.tag}_{plan}_coords.json")
        r = run([sys.executable, os.path.join(HERE, "make_coords.py"), "--plan", plan,
                 "--seed", str(a.seed), "--n", str(a.n), "--out", coords], a.outdir, env,
                os.path.join(a.outdir, f"{a.tag}_{plan}_coords.log"))
        if r["rc"] != 0:
            raise SystemExit(f"make_coords failed: {r}")
        for impl, jit in impls:
            name = f"{a.tag}_{plan}_{impl}_{jit}"
            out = os.path.join(a.outdir, name + ".json")
            cmd = [py[impl], os.path.join(HERE, "bench_fixed_theta.py"), "--impl", impl,
                   "--pe", a.pe, "--sel", a.sel, "--plan", plan, "--coords", coords,
                   "--out", out, "--n-calls", str(a.n_calls), "--warmup", str(a.warmup),
                   "--jit", jit, "--sel-batch", a.sel_batch, "--pe-block", a.pe_block,
                   "--seed", str(a.seed), "--label", name, "--device", a.device,
                   "--util-window-s", str(a.util_window_s)]
            if a.catalog and plan.startswith("dark_"):
                cmd += ["--catalog", a.catalog]
            if a.cold_cache_root:
                cmd += ["--cache-dir", os.path.join(os.path.abspath(a.cold_cache_root), name),
                        "--cache-mode", "cold"]
            if a.wrap:
                smi = os.path.join(a.outdir, name + ".smi.csv")
                cmd = shlex.split(a.wrap.replace("{smi}", smi)) + cmd + ["--smi-log", smi]
            jobs.append((name, plan, impl, jit, cmd, out))

    with cf.ThreadPoolExecutor(max_workers=max(1, a.parallel)) as ex:
        futs = {ex.submit(run, cmd, a.outdir, env, os.path.join(a.outdir, name + ".log")):
                (name, plan, impl, jit, out) for name, plan, impl, jit, cmd, out in jobs}
        for fut in cf.as_completed(futs):
            name, plan, impl, jit, out = futs[fut]
            res = fut.result()
            res.update(plan=plan, impl=impl, jit=jit, record=out)
            index["runs"][name] = res
            print(f"{name}: rc={res['rc']} wall={res['wall_s']:.1f}s", flush=True)

    pairs = [(("legacy", "whole"), ("core", "whole")), (("legacy", "whole"), ("core", "asis")),
             (("core", "whole"), ("core", "asis"))]
    for plan in plans:
        for (ia, ja), (ib, jb) in pairs:
            na, nb = f"{a.tag}_{plan}_{ia}_{ja}", f"{a.tag}_{plan}_{ib}_{jb}"
            if na not in index["runs"] or nb not in index["runs"]:
                continue
            cname = f"{a.tag}_{plan}__{ia}_{ja}__vs__{ib}_{jb}"
            out = os.path.join(a.outdir, cname + ".summary.json")
            md = os.path.join(a.outdir, cname + ".summary.md")
            r = run([sys.executable, os.path.join(HERE, "compare_records.py"),
                     index["runs"][na]["record"], index["runs"][nb]["record"],
                     "--rtol", "1e-12", "--atol", "0", "--out", out, "--md", md],
                    a.outdir, env, os.path.join(a.outdir, cname + ".log"))
            r.update(summary=out, md=md, A=na, B=nb, plan=plan)
            index["compares"][cname] = r
            with open(r["log"]) as f:
                print(f"{cname}: rc={r['rc']} {f.read().splitlines()[-1]}", flush=True)
    with open(os.path.join(a.outdir, f"{a.tag}_index.json"), "w") as f:
        json.dump(index, f, indent=1)
    bad = [k for k, v in index["runs"].items() if v["rc"] != 0]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
