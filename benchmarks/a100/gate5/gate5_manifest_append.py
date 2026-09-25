#!/usr/bin/env python3
"""Append one manifest run entry per Gate 5 ladder run (runs/*/record.json) not yet in the manifest."""
import glob, json, os, re, datetime as dt
ROOT = "/media/volume/tbs/darksirens_benchmark"
G5 = f"{ROOT}/benchmarks/gate5"
MAN = f"{ROOT}/state/manifest.json"
ENV = {"legacy": ("legacy", f"{ROOT}/envs/env_legacy.sh"), "main": ("core", f"{ROOT}/envs/env_core.sh"),
       "o1": ("core_o1", f"{ROOT}/envs/env_core_o1.sh")}
m = json.load(open(MAN))
have = {r.get("record_id") for r in m["runs"]}
added = []
for rp in sorted(glob.glob(f"{G5}/runs/*/record.json")):
    r = json.load(open(rp)); name = os.path.basename(os.path.dirname(rp))
    if name in have:
        continue
    arm = name.split("_")[1]
    smi = f"{G5}/smi/{name}.smi.csv"
    acq = rel = rc = None
    if os.path.isfile(smi):
        for line in open(smi):
            if line.startswith("# lock_acquired_utc="):
                acq = line.split("=", 1)[1].split()[0]
            elif line.startswith("# released_utc="):
                mm = re.match(r"# released_utc=(\S+) rc=(\S+)", line); rel, rc = mm.group(1), mm.group(2)
    f = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    pk = r.get("package", {})
    e = {"record_id": name, "gate": "gate5", "matrix": "G5-ladder", "tool": "infer_ladder.py",
         "env": ENV[arm][0], "env_script": ENV[arm][1], "arm": r.get("arm"),
         "package_sha": pk.get("git_sha") or (pk.get("known_digest_match") or {}).get("sha"),
         "harness": {"sha": r["harness"]["git"].get("git_sha"), "dirty": r["harness"]["git"].get("git_dirty")},
         "command_line": r.get("command_line"),
         "inputs": {r["inputs"]["pe"]["path"] if "path" in r["inputs"]["pe"] else "pe": r["inputs"]["pe"].get("sha256"),
                    r["inputs"]["sel"]["path"] if "path" in r["inputs"]["sel"] else "sel": r["inputs"]["sel"].get("sha256")},
         "guard": r["settings"]["requested"]["guard"], "max_likelihood_variance": r["settings"]["requested"]["max_likelihood_variance"],
         "budget": {k: (r.get("budget") or {}).get(k) for k in ("max_evals", "max_wall_s_sampling", "stop_reason")},
         "policy_note": r.get("policy_note"),
         "outputs": {"record": rp, "progress": f"{G5}/runs/{name}/progress.csv", "posterior": f"{G5}/runs/{name}/posterior.npz",
                     "smi": smi, "stdout": f"{G5}/logs/{name}.stdout", "stderr": f"{G5}/logs/{name}.stderr"},
         "cache_dir": f"{ROOT}/xla_cache/runs/{name}", "cache_mode": "cold",
         "status": r["status"], "rc": None if rc is None else int(rc),
         "wall_s": (f(rel) - f(acq)).total_seconds() if acq and rel else None,
         "started_utc": acq, "finished_utc": rel}
    m["runs"].append(e); added.append(name)
tmp = MAN + ".tmp"
json.dump(m, open(tmp, "w"), indent=1)
json.load(open(tmp))
os.replace(tmp, MAN)
print(f"added {len(added)}; runs now {len(m['runs'])}")
for a in added:
    print(" ", a)
