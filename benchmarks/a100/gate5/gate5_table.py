#!/usr/bin/env python3
"""Gate 5 table: one row per infer_ladder run under runs/, joined with compare/*.json.
Writes gate5_matrix.csv and gate5_facts.json in the gate5 directory. Read-only on runs."""
import csv, glob, json, os, re, sys, datetime as dt
G5 = (sys.argv[1] if len(sys.argv) > 1 else
      os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # gate5 dir (default: tools/..)
ROOT = os.path.dirname(os.path.dirname(G5))
MiB = 1024 * 1024


def smi_window(path):
    acq = rel = None; peak = None; rc = None; n = 0; first = None
    if not os.path.isfile(path):
        return {}
    for line in open(path):
        if line.startswith("# lock_acquired_utc="):
            acq = line.split("=", 1)[1].split()[0]
        elif line.startswith("# released_utc="):
            m = re.match(r"# released_utc=(\S+) rc=(\S+)", line); rel, rc = m.group(1), m.group(2)
        elif re.match(r"\d{4}/", line):
            p = [x.strip() for x in line.split(",")]
            try:
                mem = float(p[1].split()[0]); n += 1
                first = mem if first is None else first
                peak = mem if peak is None else max(peak, mem)
            except Exception:
                pass
    f = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    wall = (f(rel) - f(acq)).total_seconds() if acq and rel else None
    return {"lock_acquired_utc": acq, "released_utc": rel, "rc": rc, "gpu_lock_wall_s": wall,
            "smi_peak_mib": peak, "smi_first_mib": first, "smi_samples": n}


def load_cmp(pattern):
    out = {}
    for p in glob.glob(os.path.join(G5, "compare", pattern)):
        try:
            out[os.path.basename(p)] = json.load(open(p))
        except Exception:
            pass
    return out


post_cmp = {k[:-5]: v for k, v in load_cmp("*.json").items() if not k.endswith(".progress.json")}
prog_cmp = {k[:-len(".progress.json")]: v for k, v in load_cmp("*.progress.json").items()}

rows = []
for rp in sorted(glob.glob(os.path.join(G5, "runs", "*", "record.json"))):
    r = json.load(open(rp)); name = os.path.basename(os.path.dirname(rp))
    t = r.get("timing", {}); lc = r.get("likelihood_calls", {}) or {}; res = r.get("result") or {}
    mon = (r.get("memory") or {}).get("monitor") or {}
    pg = r.get("progress") or {}
    st = pg.get("steady_state") or {}
    comp = r.get("compile") or {}
    sm = smi_window(os.path.join(G5, "smi", name + ".smi.csv"))
    arm = name.split("_")[1]
    req = r["settings"]["requested"]; res_s = r["settings"].get("resolved") or {}
    sampler = req["sampler"]; rung = str(r["rung"]["rung"]); guard = req["guard"]
    pk = r.get("package", {})
    bud = r.get("budget") or {}
    ev = t.get("sampling_events_s") or {}
    row = {
        "name": name, "rung": rung, "sampler": sampler, "impl": r["implementation"], "arm": arm,
        "arm_label": r.get("arm"), "guard": guard, "max_variance": req["max_likelihood_variance"],
        "resolved_guard": res_s.get("selection_neff_guard"), "resolved_max_variance": res_s.get("max_likelihood_variance"),
        "status": r["status"], "stop_reason": bud.get("stop_reason"),
        "budget_max_evals": bud.get("max_evals"), "budget_max_wall_s": bud.get("max_wall_s_sampling"),
        "ndim": (r.get("dims") or {}).get("ndim"),
        "wall_s": t.get("t_total_s"), "gpu_lock_wall_s": sm.get("gpu_lock_wall_s"),
        "t_import_s": (t.get("t_import_jax_s") or 0) + (t.get("t_import_package_s") or 0),
        "t_config_s": t.get("t_config_s"), "t_load_s": t.get("t_load_s"), "t_build_s": t.get("t_build_s"),
        "t_parameter_space_s": t.get("t_parameter_space_s"), "t_run_dir_s": t.get("t_run_dir_s"),
        "t_build_likelihood_s": t.get("t_build_likelihood_s"),
        "t_first_call_s": t.get("t_first_call_s"), "sampling_wall_s": t.get("t_sampling_s"),
        "t_to_first_progress_s": ev.get("first_progress"), "t_main_loop_s": t.get("t_main_loop_s"),
        "t_post_s": t.get("t_post_s"),
        "t_preflight_s": ((t.get("sampling_eager_phases") or {}).get("preflight") or {}).get("seconds"),
        "initial_live_points_n": ((t.get("sampling_eager_phases") or {}).get("initial_live_points") or {}).get("n_eager_calls"),
        "t_initial_live_points_s": ((t.get("sampling_eager_phases") or {}).get("initial_live_points") or {}).get("seconds"),
        "initial_live_s_per_point": ((t.get("sampling_eager_phases") or {}).get("initial_live_points") or {}).get("mean_s_per_call"),
        "n_evals": lc.get("n_like_evals"), "evals_per_s": lc.get("evals_per_s_sampling"),
        "evals_per_s_steady": lc.get("evals_per_s_steady"),
        "sampling_eager_calls": (lc.get("by_phase_kind") or {}).get("sampling:eager"),
        "preflight_eager_calls": lc.get("preflight_eager_calls"),
        "iterations": pg.get("last_main_iteration"), "last_dlogz_remaining": pg.get("last_dlogz_remaining"),
        "last_logz_trace": pg.get("last_logz"),
        "iterations_per_s_steady": st.get("iterations_per_s"),
        "neg_log_volume_per_s_steady": st.get("log_volume_per_s"),
        "logZ": res.get("logZ"), "logZ_hex": res.get("logZ_hex"), "logZ_err": res.get("logZerr"),
        "n_samples": res.get("n_samples"), "n_dead": res.get("n_dead"), "dead_point_kish_ess": res.get("dead_point_kish_ess"),
        "posterior_sha256": res.get("posterior_sha256"),
        "first_call_logL": (r.get("first_call") or {}).get("logL"), "first_call_hex": (r.get("first_call") or {}).get("logL_hex"),
        "peak_vram_mib": (None if mon.get("device_peak_bytes_in_use") is None else mon["device_peak_bytes_in_use"] / MiB),
        "smi_peak_mib": sm.get("smi_peak_mib"), "smi_first_mib": sm.get("smi_first_mib"),
        "peak_host_rss_gib": ((r.get("memory") or {}).get("peak_host_rss_bytes") or 0) / 1024**3,
        "compile_first_call": (comp.get("first_call") or {}).get("compiles"),
        "compile_first_call_s": (comp.get("first_call") or {}).get("compile_seconds"),
        "compile_sampling": (comp.get("sampling") or {}).get("compiles"),
        "compile_sampling_s": (comp.get("sampling") or {}).get("compile_seconds"),
        "package_sha": pk.get("git_sha") or (pk.get("known_digest_match") or {}).get("sha"),
        "package_dirty": pk.get("git_dirty"),
        "harness_sha": r["harness"]["git"].get("git_sha"), "harness_dirty": r["harness"]["git"].get("git_dirty"),
        "pe_sha256": r["inputs"]["pe"].get("sha256"), "sel_sha256": r["inputs"]["sel"].get("sha256"),
        "seed": req["seed"], "nlive": req["nlive"], "dlogz": req["dlogz"],
        "sampler_error": (r.get("sampler_error") or {}).get("type"),
        "preflight_abort": (r.get("sampler_error") or {}).get("preflight_abort"),
        "parity_refs": ";".join(r.get("fixed_coordinate_parity_refs") or []),
        "policy_note": r.get("policy_note"),
        "started_utc": r.get("started_utc"), "finished_utc": r.get("finished_utc"),
    }
    gtag = "hard" if guard == "hard" else "soft"
    tag = f"{sampler}_r{rung}_{gtag}_legacy_vs_{arm}"
    c = post_cmp.get(tag); pc = prog_cmp.get(tag)
    if arm == "legacy":
        row["samples_bitwise_vs_legacy"] = None; row["posterior_agreement_summary"] = "reference"
    else:
        s = []
        if c is not None:
            v = c["verdict"]; lz = c["logZ"]
            row["samples_bitwise_vs_legacy"] = v.get("posterior_samples_bitwise_equal")
            row["logZ_bitwise_vs_legacy"] = lz.get("bitwise_equal")
            s.append(f"posterior: samples bitwise={v.get('posterior_samples_bitwise_equal')}, logZ bitwise="
                     f"{lz.get('bitwise_equal')} (n_sigma {lz.get('n_sigma')}), max|dmean|/MCerr="
                     f"{v.get('max_abs_delta_mean_over_mc_error')}, max KS D={v.get('max_ks_D')}")
        else:
            row["samples_bitwise_vs_legacy"] = None
            s.append("no posterior comparison (pair not both converged)" if pc is not None else "no comparison")
        if pc is not None:
            row["trace_identical_vs_legacy"] = pc.get("traces_identical_on_common_rows")
            row["trace_ncall_identical_vs_legacy"] = pc.get("ncall_cum_identical_on_common_rows")
            row["deterministic_replica_vs_legacy"] = (pc.get("replica") or {}).get("deterministic_replica")
            s.append(f"replica={(pc.get('replica') or {}).get('deterministic_replica')}")
            s.append(f"trace: {pc.get('n_common_rows')} common rows, identical={pc.get('traces_identical_on_common_rows')}, "
                     f"ncall identical={pc.get('ncall_cum_identical_on_common_rows')}, max rel "
                     f"{pc.get('max_rel_diff_on_common_rows')}, B/A rates {pc['performance'].get('ratio_B_over_A')}")
        row["posterior_agreement_summary"] = "; ".join(s)
    rows.append(row)

cols = []
for r in rows:
    for k in r:
        if k not in cols:
            cols.append(k)
with open(os.path.join(G5, "gate5_matrix.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]

# GPU wall: every gpu_run.sh window of this gate (ladder runs + the soft@10 parity records)
wins = []
for p in sorted(glob.glob(os.path.join(G5, "smi", "*.smi.csv")) +
                glob.glob(os.path.join(ROOT, "benchmarks", "gate1", "m5b", "soft10", "smi", "*.smi.csv"))):
    w = smi_window(p); w["file"] = p; wins.append(w)
tot = sum(w["gpu_lock_wall_s"] or 0 for w in wins)
facts = {"rows": rows, "gpu_windows": wins, "total_gpu_wall_s": tot,
         "compare_posteriors": {k: {"verdict": v["verdict"], "logZ": v["logZ"], "first_call_centre": v.get("first_call_centre"),
                                    "parameters": v.get("parameters"),
                                    "progress": v.get("progress"), "ratio_B_over_A": v["performance"].get("ratio_B_over_A")}
                                for k, v in post_cmp.items()},
         "compare_progress": prog_cmp}
json.dump(facts, open(os.path.join(G5, "gate5_facts.json"), "w"), indent=1, default=str)
print(f"{len(rows)} rows, {len(post_cmp)} posterior comparisons, {len(prog_cmp)} progress comparisons, "
      f"{len(wins)} GPU windows, total GPU wall {tot:.1f} s")
