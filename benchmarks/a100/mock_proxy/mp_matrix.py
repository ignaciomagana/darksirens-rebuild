#!/usr/bin/env python3
"""Mock-proxy ladder tables: mock_proxy_matrix.csv (one row per run) and matrix.json (runs,
legacy-vs-core pairs, parity precondition). numpy only; posterior stats via
compare_posteriors.param_stats. --manifest appends one state/manifest.json run entry per run
record not yet listed (gate mock_proxy, matrix MP-ladder)."""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import compare_posteriors as cp  # noqa: E402

ROOT = "/media/volume/tbs/darksirens_benchmark"
MP = f"{ROOT}/benchmarks/mock_proxy"
LOWL = -1e300
ENV = {"legacy": ("legacy", f"{ROOT}/envs/env_legacy.sh", f"{ROOT}/logs/envs/env_legacy.fingerprint.json"),
       "main": ("core", f"{ROOT}/envs/env_core.sh", f"{ROOT}/logs/envs/env_core.fingerprint.json")}
ORDER = [(fx, plan, arm) for fx in ("R1", "R2") for plan in ("dark_H0", "dark_full") for arm in ("legacy", "main")]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def smi_info(path):
    out = {"lock_acquired_utc": None, "released_utc": None, "rc": None, "smi_max_mem_mib": None}
    if not os.path.isfile(path):
        return out
    mx = None
    for line in open(path):
        if line.startswith("# lock_acquired_utc="):
            out["lock_acquired_utc"] = line.split("=", 1)[1].split()[0]
        elif line.startswith("# released_utc="):
            m = re.match(r"# released_utc=(\S+) rc=(\S+)", line)
            out["released_utc"], out["rc"] = m.group(1), m.group(2)
        else:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2 and parts[1].endswith("MiB"):
                try:
                    v = float(parts[1].split()[0])
                    mx = v if mx is None else max(mx, v)
                except ValueError:
                    pass
    out["smi_max_mem_mib"] = mx
    return out


def driver_walls():
    w = {}
    for lg in sorted(glob.glob(f"{MP}/logs/driver_*.log")):
        for line in open(lg):
            m = re.match(r"(\S+) end (\S+) rc=(\d+) status=\[(.*)\] wall=([0-9.]+)", line)
            if m:
                w[m.group(2)] = {"rc": int(m.group(3)), "driver_wall_s": float(m.group(5)), "end_utc": m.group(1),
                                 "driver_log": lg}
    return w


def run_row(fx, plan, arm, walls, fps):
    name = f"MP_{arm}_{fx}_{plan}_dynesty_soft10"
    d = f"{MP}/runs/{name}"
    row = {"name": name, "fixture": fx, "plan": plan, "code": "legacy" if arm == "legacy" else "core main",
           "arm": arm}
    w = walls.get(name, {})
    row["driver_rc"], row["driver_wall_s"] = w.get("rc"), w.get("driver_wall_s")
    smi = smi_info(f"{MP}/smi/{name}.smi.csv")
    row["smi_max_mem_mib"] = smi["smi_max_mem_mib"]
    row["lock_acquired_utc"], row["released_utc"] = smi["lock_acquired_utc"], smi["released_utc"]
    rp = f"{d}/record.json"
    if not os.path.isfile(rp):
        row["status"] = "no_record"
        return row, None, None
    rec = json.load(open(rp))
    lc = rec.get("likelihood_calls") or {}
    nf = lc.get("nonfinite") or {}
    res = rec.get("result") or {}
    tim = rec.get("timing") or {}
    bud = rec.get("budget") or {}
    mem = rec.get("memory") or {}
    mon = mem.get("monitor") or {}
    eph = tim.get("sampling_eager_phases") or {}
    rs = (rec.get("settings") or {}).get("resolved") or {}
    ds = rs.get("dark_settings") or {}
    xc = rec.get("xla_cache") or {}
    row.update({
        "status": rec.get("status"), "stop_reason": bud.get("stop_reason"),
        "converged": bool(rec.get("status") == "ok" and str(bud.get("stop_reason") or "").startswith("converged")),
        "budget_max_evals": bud.get("max_evals"), "budget_max_wall_s": bud.get("max_wall_s_sampling"),
        "sampler_error": (json.dumps(rec.get("sampler_error"))[:300] if rec.get("sampler_error") else None),
        "t_total_s": tim.get("t_total_s"), "t_import_jax_s": tim.get("t_import_jax_s"),
        "t_import_package_s": tim.get("t_import_package_s"), "t_config_s": tim.get("t_config_s"),
        "t_load_s": tim.get("t_load_s"), "t_build_s": tim.get("t_build_s"),
        "t_first_call_s": tim.get("t_first_call_s"), "t_sampling_s": tim.get("t_sampling_s"),
        "t_preflight_s": (eph.get("preflight") or {}).get("seconds"),
        "n_initial_live_eager": (eph.get("initial_live_points") or {}).get("n_eager_calls"),
        "t_initial_live_points_s": (eph.get("initial_live_points") or {}).get("seconds"),
        "s_per_initial_live_point": (eph.get("initial_live_points") or {}).get("mean_s_per_call"),
        "t_first_progress_s": (tim.get("sampling_events_s") or {}).get("first_progress"),
        "t_main_loop_s": tim.get("t_main_loop_s"), "t_post_s": tim.get("t_post_s"),
        "n_evals": lc.get("n_like_evals"), "evals_per_s": lc.get("evals_per_s_sampling"),
        "evals_per_s_steady": lc.get("evals_per_s_steady"),
        "last_iteration": (rec.get("progress") or {}).get("last_main_iteration"),
        "last_dlogz_remaining": (rec.get("progress") or {}).get("last_dlogz_remaining"),
        "last_ncall_cum_dynesty": (rec.get("progress") or {}).get("last_ncall_cum"),
        "logZ": res.get("logZ"), "logZ_hex": res.get("logZ_hex"), "logZ_err": res.get("logZerr"),
        "n_dead": res.get("n_dead"), "kish_ess": res.get("dead_point_kish_ess"),
        "posterior_npz": res.get("posterior_npz"), "posterior_sha256": res.get("posterior_sha256"),
        "progress_csv": f"{d}/progress.csv",
        "nonfinite_sampling_eager": nf.get("sampling_eager_total"),
        "first_call_logL": (rec.get("first_call") or {}).get("logL"),
        "peak_vram_mib": (None if mon.get("device_peak_bytes_in_use") is None
                          else mon["device_peak_bytes_in_use"] / 2 ** 20),
        "host_rss_max_mib": (None if mon.get("host_rss_max_bytes") is None else mon["host_rss_max_bytes"] / 2 ** 20),
        "peak_host_rss_mib_rusage": (None if mem.get("peak_host_rss_bytes") is None else mem["peak_host_rss_bytes"] / 2 ** 20),
        "package_sha": (rec.get("package") or {}).get("git_sha") or
                       ((rec.get("package") or {}).get("known_digest_match") or {}).get("sha"),
        "harness_sha": ((rec.get("harness") or {}).get("git") or {}).get("git_sha"),
        "harness_dirty": ((rec.get("harness") or {}).get("git") or {}).get("git_dirty"),
        "env_fingerprint_file": ENV[arm][2], "env_fingerprint_sha256": fps.get(arm),
        "pe_sha256": (rec["inputs"].get("pe") or {}).get("sha256"),
        "sel_sha256": (rec["inputs"].get("sel") or {}).get("sha256"),
        "catalog_sha256": (rec["inputs"].get("catalog") or {}).get("sha256"),
        "preflight_status": (rec.get("fixture_preflight") or {}).get("status"),
        "cache_dir": xc.get("dir"), "cache_files_before": xc.get("files_before"),
        "cache_files_after": xc.get("files_after"), "cache_bytes_after": xc.get("bytes_after"),
        "sel_batch_size": rs.get("sel_batch_size"), "pe_event_block": rs.get("pe_event_block"),
        "resolved_guard": rs.get("selection_neff_guard"), "resolved_soft": rs.get("selection_neff_soft_guard"),
        "resolved_cap": rs.get("max_likelihood_variance"), "resolved_nlive": rs.get("nlive"),
        "resolved_dlogz": rs.get("dlogz"), "resolved_seed": rs.get("seed"),
        "row_chunk_effective": ds.get("row_chunk_effective"),
        "kernel_pin_active": (ds.get("kernel_pin") or {}).get("active"),
        "empty_row_routing_active": (ds.get("empty_row_routing") or {}).get("active"),
        "compile_sampling_requests": ((rec.get("compile") or {}).get("sampling") or {}).get("requests"),
    })
    post = None
    npz = f"{d}/posterior.npz"
    if os.path.isfile(npz):
        with np.load(npz, allow_pickle=False) as z:
            post = {k: z[k] for k in z.files}
        row["n_posterior_samples"] = int(post["samples"].shape[0])
        labels = [str(x) for x in post["labels"]]
        cols = [str(x) for x in post["columns"]]
        for i, (lab, col) in enumerate(zip(labels, cols)):
            if lab in ("H0", "log10n0", "delta", "sigma_kde"):
                s = cp.param_stats(post["samples"][:, i])
                for q in ("mean", "std", "q16", "q50", "q84"):
                    row[f"{col}_{q}"] = s[q]
    return row, rec, post


def pair_row(fx, plan, rows, posts):
    L_ = rows[(fx, plan, "legacy")]
    C_ = rows[(fx, plan, "main")]
    tag = f"{fx}_{plan}_legacy_vs_main"
    pj = f"{MP}/compare/{tag}.progress.json"
    pj = json.load(open(pj)) if os.path.isfile(pj) else {}
    rep = pj.get("replica") or {}
    p = {"fixture": fx, "plan": plan, "legacy": L_["name"], "core": C_["name"],
         "status": [L_.get("status"), C_.get("status")],
         "stop_reason": [L_.get("stop_reason"), C_.get("stop_reason")],
         "n_evals": [L_.get("n_evals"), C_.get("n_evals")],
         "last_iteration": [L_.get("last_iteration"), C_.get("last_iteration")],
         "replica": rep.get("deterministic_replica"),
         "replica_detail": rep,
         "traces_identical_on_common_rows": pj.get("traces_identical_on_common_rows"),
         "progress_max_rel": pj.get("max_rel_diff_on_common_rows"),
         "performance": pj.get("performance"),
         "logZ_bitwise": (L_.get("logZ_hex") is not None and L_.get("logZ_hex") == C_.get("logZ_hex")),
         "logZ_rel": (abs(C_["logZ"] - L_["logZ"]) / abs(L_["logZ"])
                      if L_.get("logZ") is not None and C_.get("logZ") is not None else None),
         "logZerr_rel": (abs(C_["logZ_err"] - L_["logZ_err"]) / abs(L_["logZ_err"])
                         if L_.get("logZ_err") and C_.get("logZ_err") is not None else None),
         "samples_bitwise": None, "posterior_sha256_equal": None,
         "compare_posteriors": f"{MP}/compare/{tag}.json" if os.path.isfile(f"{MP}/compare/{tag}.json") else None,
         "compare_progress": f"{MP}/compare/{tag}.progress.json" if pj else None}
    pl, pc = posts.get(L_["name"]), posts.get(C_["name"])
    if pl is not None and pc is not None:
        p["samples_bitwise"] = bool(pl["samples"].shape == pc["samples"].shape
                                    and np.array_equal(pl["samples"], pc["samples"]))
        p["posterior_sha256_equal"] = L_.get("posterior_sha256") == C_.get("posterior_sha256")
        x, y = pl["dead_logl"], pc["dead_logl"]
        if x.shape == y.shape:
            fin = np.isfinite(x) & np.isfinite(y) & (x > LOWL * 0.1) & (y > LOWL * 0.1)
            diff = x != y
            p["dead_logl_n"], p["dead_logl_n_diff"] = int(x.size), int(diff.sum())
            p["dead_logl_floor_mismatch"] = int(np.sum(diff & ~fin))
            if np.any(diff & fin):
                p["dead_logl_max_rel"] = float((np.abs(y[fin] - x[fin]) / np.abs(x[fin])).max())
                p["dead_logl_max_abs"] = float(np.abs(y[fin] - x[fin]).max())
            else:
                p["dead_logl_max_rel"] = p["dead_logl_max_abs"] = 0.0
        else:
            p["dead_logl_shape"] = [list(x.shape), list(y.shape)]
    return p


def parity_rows():
    out = []
    idx = f"{MP}/parity/index.json"
    if not os.path.isfile(idx):
        return out
    ind = json.load(open(idx))["runs"]
    for rid, e in sorted(ind.items()):
        if not rid.startswith("MPP_core_") or (rid + "_diagjit") in ind:
            continue  # a record superseded by its --diag-mode jit rerun is listed via the rerun
        sp = e["spec"]
        s = f"{MP}/parity/summaries/{rid}.json"
        d = json.load(open(s)) if os.path.isfile(s) else {}
        mr = d.get("max_rel_by_field") or {}
        worst = max(mr.items(), key=lambda kv: (kv[1] or 0)) if mr else (None, None)
        out.append({"fixture": sp["fixture"], "plan": sp["plan"], "record_core": rid,
                    "record_legacy": sp["compare_to"][0], "status_core": e.get("status"),
                    "status_legacy": ind.get(sp["compare_to"][0], {}).get("status"),
                    "overall_pass": (d.get("verdict") or {}).get("overall_pass"), "summary": s,
                    "worst_field": worst[0], "max_rel": worst[1], "max_rel_by_field": mr,
                    "verdict": d.get("verdict"),
                    "superseded_attempt": (rid[:-len("_diagjit")] if rid.endswith("_diagjit") else None),
                    "superseded_attempt_status": (ind.get(rid[:-len("_diagjit")], {}).get("status")
                                                  if rid.endswith("_diagjit") else None)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", action="store_true")
    a = ap.parse_args()
    fps = {arm: (sha256(v[2]) if os.path.isfile(v[2]) else None) for arm, v in ENV.items()}
    walls = driver_walls()
    rows, posts, recs = {}, {}, {}
    for fx, plan, arm in ORDER:
        r, rec, post = run_row(fx, plan, arm, walls, fps)
        rows[(fx, plan, arm)] = r
        posts[r["name"]], recs[r["name"]] = post, rec
    cols = []
    for r in rows.values():
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(f"{MP}/mock_proxy_matrix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows.values():
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})
    pairs = [pair_row(fx, plan, rows, posts) for fx in ("R1", "R2") for plan in ("dark_H0", "dark_full")
             if (fx, plan, "legacy") in rows]
    out = {"schema": "mock-proxy-matrix/1", "runs": list(rows.values()), "pairs": pairs,
           "parity": parity_rows(), "env_fingerprint_sha256": fps,
           "total_driver_wall_s": sum(r.get("driver_wall_s") or 0 for r in rows.values())}
    json.dump(out, open(f"{MP}/matrix.json", "w"), indent=1, default=str)
    print(json.dumps({"pairs": pairs, "parity": out["parity"], "total_driver_wall_s": out["total_driver_wall_s"]},
                     indent=1, default=str))
    if a.manifest:
        mp = f"{ROOT}/state/manifest.json"
        doc = json.load(open(mp))
        have = {e.get("record_id") for e in doc["runs"]}
        added = []
        for (fx, plan, arm), r in rows.items():
            name = r["name"]
            rec = recs.get(name)
            if name in have or rec is None:
                continue
            doc["runs"].append({
                "record_id": name, "gate": "mock_proxy", "matrix": "MP-ladder", "tool": "infer_ladder.py",
                "env": ENV[arm][0], "env_script": ENV[arm][1], "arm": rec.get("arm"),
                "package_sha": r.get("package_sha"),
                "harness": {"sha": r.get("harness_sha"), "dirty": r.get("harness_dirty")},
                "command_line": rec.get("command_line"),
                "inputs": {(rec["inputs"].get(k) or {}).get("path"): (rec["inputs"].get(k) or {}).get("sha256")
                           for k in ("pe", "sel", "catalog")},
                "fixture": fx, "plan": plan, "guard": "soft", "max_likelihood_variance": 10.0,
                "budget": rec.get("budget"), "policy_note": rec.get("policy_note"),
                "parity_refs": rec.get("fixed_coordinate_parity_refs"),
                "outputs": {"record": f"{MP}/runs/{name}/record.json", "progress": f"{MP}/runs/{name}/progress.csv",
                            "posterior": f"{MP}/runs/{name}/posterior.npz", "smi": f"{MP}/smi/{name}.smi.csv",
                            "stdout": f"{MP}/logs/{name}.stdout", "stderr": f"{MP}/logs/{name}.stderr"},
                "cache_dir": f"{ROOT}/xla_cache/runs/{name}", "cache_mode": "cold",
                "status": r.get("status"), "rc": r.get("driver_rc"), "wall_s": r.get("driver_wall_s"),
                "started_utc": rec.get("started_utc"), "finished_utc": rec.get("finished_utc"),
                "n_like_evals": r.get("n_evals"), "stop_reason": r.get("stop_reason")})
            added.append(name)
        tmp = mp + ".tmp"
        json.dump(doc, open(tmp, "w"), indent=1)
        json.load(open(tmp))
        os.replace(tmp, mp)
        print(f"manifest: added {len(added)}; runs now {len(doc['runs'])}")


if __name__ == "__main__":
    main()
