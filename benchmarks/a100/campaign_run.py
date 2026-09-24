#!/usr/bin/env python3
"""Sequential campaign driver: one benchmark record per spec entry, on the A100 host.

    python campaign_run.py --spec SPEC.json --outdir OUT [--only ID,ID] [--resume] [--dry-run]

SPEC is a JSON list of record specs::

    {"record_id": ..., "matrix": "M1", "env": "legacy|core|core_pin|core_o1", "impl": "legacy|core",
     "jit": "whole|asis", "blocks": "default|matched|none", "sel_batch": "default|none|N",
     "pe_block": "default|none|N", "plan": ..., "pe": PATH, "sel": PATH,
     "pe_label": ..., "sel_label": ..., "n_calls": 20, "warmup": 3, "util_window_s": 10,
     "cache": "cold" | {"warm_from": RECORD_ID},
     "compare_to": [RECORD_ID | /abs/path/record.json, ...],
     "flags": {...},
     # optional (Gate 2 / M5):
     "catalog": CAT.h5,            # dark-siren plans: passed as --catalog
     "extra_args": [ARG, ...],     # appended to the bench_fixed_theta.py command line
     "coords_tag": TAG, "coords_args": [ARG, ...],   # coordinates OUT/coords/<plan>__<TAG>.json
                                                     # made with make_coords.py ... ARGS
     # optional (Gate 3):
     "guard": "hard|soft", "max_variance": X,        # --guard / --max-variance (both adapters)
     "tool": "components",                           # bench_components.py instead of
     "main_record": PATH, "trace": true}             # bench_fixed_theta.py (--main-record,
                                                     # --trace OUT/traces/<id>); compare_to
                                                     # then uses ``bench_components.py compare``

For every entry, strictly one at a time:

* coordinates ``OUT/coords/<plan>.json`` (make_coords.py, seed from the spec) are made
  once per plan and shared by every record of that plan;
* ``cold``: ``<cache_root>/<record_id>`` is removed and re-created empty right before the
  run and passed as ``--cache-dir ... --cache-mode cold``; ``warm_from``: the cache
  directory of that earlier record is reused (``--cache-mode warm``);
* the benchmark runs as ``gpu_run.sh OUT/smi/<id>.smi.csv bash -c 'source <env script>;
  python bench_fixed_theta.py ... --smi-log OUT/smi/<id>.smi.csv'`` (campaign lock + 1 Hz
  sampler), stdout/stderr in ``OUT/logs/<id>.{stdout,stderr}``, record in
  ``OUT/records/<id>.json``;
* the run is classified ok / plan_mismatch / build_error / oom / error (oom = a non-zero
  exit whose stderr or build error reports RESOURCE_EXHAUSTED / out of memory);
* each ``compare_to`` record is compared with compare_records.py (rtol 1e-12, atol 0, the
  earlier record is A): the first into ``OUT/summaries/<id>.{json,md}``, the others into
  ``OUT/summaries/<id>__vs__<ref>.{json,md}``;
* ``OUT/index.json`` is rewritten after every record and a run entry is appended to the
  campaign manifest (``--manifest``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/media/volume/tbs/darksirens_benchmark"
ENV_SCRIPTS = {"legacy": f"{ROOT}/envs/env_legacy.sh", "core": f"{ROOT}/envs/env_core.sh",
               "core_pin": f"{ROOT}/envs/env_core_pin.sh",
               # Gate 4 experimental arm: darksirens-core perf/jit-bound-analysis (not merged)
               "core_o1": f"{ROOT}/envs/env_core_o1.sh"}
ENV_PY = {"legacy": f"{ROOT}/envs/env_legacy/bin/python", "core": f"{ROOT}/envs/env_core/bin/python",
          "core_pin": f"{ROOT}/envs/env_core_pin/bin/python",
          "core_o1": f"{ROOT}/envs/env_core_o1/bin/python"}
PKG_SHA = {"legacy": "c042527238bd71421b792936bc48c3b815b90d6d",
           "core": "88004d96ddeee37c47abc1d2dfd1c6fc3c203dfd",
           "core_pin": "8bf2bec53ff7b557c6b930d4044008cb72008f61",
           "core_o1": "f825906278140b8bfd80a13007ddd0136db28d49"}
OOM_RE = re.compile(r"RESOURCE_EXHAUSTED|[Oo]ut of memory|OOM|Failed to allocate|CUDA_ERROR_OUT_OF_MEMORY")


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path, bufsize=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def write_json_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(tmp, path)


def git_head(path):
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True,
                             text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=path,
                                    capture_output=True, text=True).stdout.strip())
        return {"sha": sha, "dirty": dirty}
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}


def manifest_append(manifest, entry):
    if not manifest:
        return
    with open(manifest) as f:
        doc = json.load(f)
    doc.setdefault("runs", []).append(entry)
    write_json_atomic(manifest, doc)
    with open(manifest) as f:  # must stay valid JSON
        json.load(f)


def classify(rc, rec_path, stderr_path):
    rec = None
    if os.path.isfile(rec_path):
        try:
            with open(rec_path) as f:
                rec = json.load(f)
        except Exception:
            rec = None
    err = ""
    try:
        with open(stderr_path, errors="replace") as f:
            err = f.read()
    except OSError:
        pass
    if rc == 0 and rec is not None and rec.get("status") == "ok":
        return "ok", rec
    blob = err
    if rec is not None and rec.get("build_error"):
        blob += json.dumps(rec["build_error"])
    if rec is not None and rec.get("failure"):
        blob += json.dumps(rec["failure"].get("message"))
    if OOM_RE.search(blob):
        return "oom", rec
    if rec is not None and rec.get("status") in ("plan_mismatch", "build_error"):
        return rec["status"], rec
    return f"error_rc{rc}", rec


def ensure_coords(outdir, plan, seed, n, py, tag=None, extra=None):
    name = f"{plan}__{tag}.json" if tag else f"{plan}.json"
    path = os.path.join(outdir, "coords", name)
    if not os.path.isfile(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run([py, os.path.join(HERE, "make_coords.py"), "--plan", plan, "--seed",
                            str(seed), "--n", str(n), "--out", path] + list(extra or []),
                           capture_output=True, text=True,
                           env=dict(os.environ, JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1"))
        if r.returncode != 0:
            raise SystemExit(f"make_coords failed for {plan}: {r.stderr}")
    return path


def compare(py, a_rec, b_rec, out_json, out_md, components=False):
    env = dict(os.environ, JAX_PLATFORMS="cpu", PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    if components:
        cmd = [py, os.path.join(HERE, "bench_components.py"), "compare", a_rec, b_rec,
               "--rtol", "1e-12", "--out", out_json, "--md", out_md]
    else:
        cmd = [py, os.path.join(HERE, "compare_records.py"), a_rec, b_rec, "--rtol", "1e-12",
               "--atol", "0", "--out", out_json, "--md", out_md]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return {"rc": r.returncode, "summary": out_json, "md": out_md,
            "last_line": (r.stdout.strip().splitlines() or [""])[-1], "stderr_tail": r.stderr[-1500:]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--cache-root", default=f"{ROOT}/xla_cache/runs")
    ap.add_argument("--manifest", default=f"{ROOT}/state/manifest.json")
    ap.add_argument("--gpu-run", default=f"{ROOT}/bin/gpu_run.sh")
    ap.add_argument("--driver-python", default=ENV_PY["core"])
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--gate", default="gate1", help="gate label written into the manifest entries")
    ap.add_argument("--only", default=None)
    ap.add_argument("--resume", action="store_true", help="skip records already in the index with rc 0")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    out = os.path.abspath(a.outdir)
    for sub in ("records", "summaries", "smi", "logs", "coords", "traces"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    with open(a.spec) as f:
        specs = json.load(f)
    only = set(a.only.split(",")) if a.only else None
    index_path = os.path.join(out, "index.json")
    index = {"runs": {}}
    if os.path.isfile(index_path):
        with open(index_path) as f:
            index = json.load(f)
    harness = git_head(os.path.dirname(os.path.dirname(HERE)))
    input_sha = {}

    for sp in specs:
        rid = sp["record_id"]
        if only and rid not in only:
            continue
        prev = index["runs"].get(rid)
        if a.resume and prev and prev.get("status") == "ok":
            print(f"[skip] {rid} (already ok)", flush=True)
            continue
        plan = sp["plan"]
        coords = ensure_coords(out, plan, a.seed, a.n, a.driver_python, sp.get("coords_tag"),
                               sp.get("coords_args"))
        rec = os.path.join(out, "records", rid + ".json")
        smi = os.path.join(out, "smi", rid + ".smi.csv")
        so, se = (os.path.join(out, "logs", rid + ext) for ext in (".stdout", ".stderr"))
        cache = sp.get("cache", "cold")
        warm = isinstance(cache, dict)
        if warm:
            cdir = os.path.join(a.cache_root, cache["warm_from"])
            mode = "warm"
        else:
            cdir = os.path.join(a.cache_root, rid)
            mode = "cold"
        components = sp.get("tool") == "components"
        tool = "bench_components.py" if components else "bench_fixed_theta.py"
        bench = ["python", os.path.join(HERE, tool), "--impl", sp["impl"],
                 "--pe", sp["pe"], "--sel", sp["sel"], "--plan", plan, "--coords", coords,
                 "--out", rec, "--n-calls", str(sp.get("n_calls", 20)),
                 "--warmup", str(sp.get("warmup", 3)), "--jit", sp["jit"],
                 "--sel-batch", str(sp["sel_batch"]), "--pe-block", str(sp["pe_block"]),
                 "--seed", str(a.seed), "--label", rid, "--device", "gpu",
                 "--cache-dir", cdir, "--cache-mode", mode]
        if components:
            if sp.get("main_record"):
                mr = str(sp["main_record"])
                if mr.startswith("@OUT/"):
                    mr = os.path.join(out, mr[len("@OUT/"):])
                bench += ["--main-record", mr]
            if sp.get("trace"):
                bench += ["--trace", os.path.join(out, "traces", rid), "--trace-drop-xplane"]
        else:
            bench += ["--util-window-s", str(sp.get("util_window_s", 10)), "--smi-log", smi]
        if sp.get("guard"):
            bench += ["--guard", str(sp["guard"])]
        if sp.get("max_variance") is not None:
            bench += ["--max-variance", repr(float(sp["max_variance"]))]
        if sp.get("catalog"):
            bench += ["--catalog", sp["catalog"]]
        bench += [str(x) for x in (sp.get("extra_args") or [])]
        inner = (f"source {shlex.quote(ENV_SCRIPTS[sp['env']])} && cd {shlex.quote(HERE)} && "
                 f"exec {' '.join(shlex.quote(x) for x in bench)}")
        cmd = [a.gpu_run, smi, "bash", "-c", inner]
        if a.dry_run:
            print(rid, " ".join(shlex.quote(c) for c in cmd))
            continue
        for p in (sp["pe"], sp["sel"]) + ((sp["catalog"],) if sp.get("catalog") else ()):
            if p not in input_sha:
                input_sha[p] = sha256_file(p)
        if not warm:
            if os.path.exists(cdir):
                shutil.rmtree(cdir)
            os.makedirs(cdir)
        for p in (rec, so, se):
            if os.path.exists(p):
                os.remove(p)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONPATH", None)
        env.pop("JAX_PLATFORMS", None)
        started = utc()
        t0 = time.time()
        with open(so, "w") as fo, open(se, "w") as fe:
            rc = subprocess.run(cmd, stdout=fo, stderr=fe, env=env, cwd=HERE).returncode
        wall = time.time() - t0
        status, recd = classify(rc, rec, se)
        entry = {"record_id": rid, "matrix": sp.get("matrix"), "spec": sp, "status": status, "rc": rc,
                 "wall_s": wall, "started_utc": started, "finished_utc": utc(), "record": rec,
                 "stdout": so, "stderr": se, "smi": smi, "cache_dir": cdir, "cache_mode": mode,
                 "command_line": cmd, "compares": {}}
        # comparisons (A = the earlier reference record)
        for k, ref in enumerate(sp.get("compare_to") or []):
            if os.path.isabs(ref):
                # a record of another campaign directory (e.g. Gate 3 retries vs gate3/records)
                ref_rec = ref
                ref_name = os.path.basename(ref)
                ref_name = ref_name[:-len(".json")] if ref_name.endswith(".json") else ref_name
                try:
                    with open(ref_rec) as f:
                        ref_ok = json.load(f).get("status") == "ok"
                except (OSError, ValueError):
                    ref_ok = False
            else:
                ref_rec = os.path.join(out, "records", ref + ".json")
                ref_name = ref
                ref_ok = index["runs"].get(ref, {}).get("status") == "ok"
            base = rid if k == 0 else f"{rid}__vs__{ref_name}"
            if status != "ok" or not ref_ok:
                entry["compares"][ref] = {"rc": None, "skipped": "record or reference not ok"}
                continue
            entry["compares"][ref] = compare(a.driver_python, ref_rec, rec,
                                             os.path.join(out, "summaries", base + ".json"),
                                             os.path.join(out, "summaries", base + ".md"),
                                             components=components)
        index["runs"][rid] = entry
        index["harness"] = harness
        write_json_atomic(index_path, index)
        manifest_append(a.manifest, {
            "record_id": rid, "gate": a.gate, "matrix": sp.get("matrix"),
            "command_line": cmd, "env": sp["env"], "env_script": ENV_SCRIPTS[sp["env"]],
            "package_sha": PKG_SHA[sp["env"]],
            "package_git_sha_recorded": ((recd or {}).get("package") or {}).get("git_sha")
            or (((recd or {}).get("package") or {}).get("known_digest_match") or {}).get("sha"),
            "harness": harness,
            "inputs": {p: input_sha[p] for p in
                       (sp["pe"], sp["sel"]) + ((sp["catalog"],) if sp.get("catalog") else ())},
            "cache_dir": cdir, "cache_mode": mode,
            "outputs": {"record": rec, "stdout": so, "stderr": se, "smi": smi,
                        "summaries": [c.get("summary") for c in entry["compares"].values()]},
            "rc": rc, "status": status, "wall_s": wall, "started_utc": started,
            "finished_utc": entry["finished_utc"]})
        cmp_txt = "; ".join(f"vs {r}: rc={c.get('rc')}" for r, c in entry["compares"].items())
        print(f"[{utc()}] {rid}: {status} rc={rc} wall={wall:.1f}s {cmp_txt}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
