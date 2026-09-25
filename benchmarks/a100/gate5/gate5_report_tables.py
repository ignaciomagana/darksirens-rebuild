#!/usr/bin/env python3
"""Markdown tables for gate5_run.md from gate5_facts.json (read-only)."""
import json, os, sys
G5 = (sys.argv[1] if len(sys.argv) > 1 else
      os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # gate5 dir (default: tools/..)
F = json.load(open(os.path.join(G5, "gate5_facts.json")))
rows = F["rows"]
ORDER = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "5b": 6}
ARM = {"legacy": 0, "main": 1, "o1": 2}


def g(x, nd=1):
    if x is None or x == "":
        return "-"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def key(r):
    return (r["guard"] != "soft" or r["max_variance"] != 10.0, r["sampler"] != "tinyns", ORDER.get(r["rung"], 9), ARM.get(r["arm"], 9), r["name"])


rs = sorted(rows, key=key)
print("### Ladder table\n")
print("| run | rung | sampler | impl (arm) | guard/cap | status (stop) | wall s | sampling s | n_evals | evals/s (sampling / steady) | iterations | logZ +- err | agreement vs legacy |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rs:
    stop = r["stop_reason"] or ""
    if stop.startswith("budget:"):
        import ast
        try:
            h = ast.literal_eval(stop[len("budget: "):])
            stop = f"{h['kind']} {h['value'] if h['kind'] == 'evals' else round(h['value'], 1)} >= {h['limit']}"
        except Exception:
            pass
    lz = "-" if r["logZ"] in (None, "") else f"{float(r['logZ']):.4f} +- {float(r['logZ_err']):.4f}"
    ag = r.get("posterior_agreement_summary") or ""
    if r["arm"] != "legacy":
        bits = []
        if r.get("samples_bitwise_vs_legacy") is not None:
            bits.append(f"samples bitwise {r['samples_bitwise_vs_legacy']}, logZ bitwise {r.get('logZ_bitwise_vs_legacy')}")
        if r.get("deterministic_replica_vs_legacy") is not None:
            bits.append(f"replica {r['deterministic_replica_vs_legacy']}")
        ag = "; ".join(bits) if bits else ag
    print(f"| {r['name']} | {r['rung']} | {r['sampler']} | {r['impl']} ({r['arm']}) | {r['guard']}/{g(r['max_variance'])} | "
          f"{r['status']} ({stop}) | {g(r['wall_s'])} | {g(r['sampling_wall_s'])} | {g(r['n_evals'])} | "
          f"{g(r['evals_per_s'])} / {g(r['evals_per_s_steady'])} | {g(r['iterations'])} | {lz} | {ag} |")

print("\n### Phases (seconds)\n")
print("| run | import | config | load | build | first call | preflight | initial live points (n, s, s/point) | to first progress | main loop | total |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for r in rs:
    ilp = "-" if not r.get("initial_live_points_n") else f"{r['initial_live_points_n']}, {g(r['t_initial_live_points_s'])}, {g(r['initial_live_s_per_point'], 4)}"
    print(f"| {r['name']} | {g(r['t_import_s'],2)} | {g(r['t_config_s'],2)} | {g(r['t_load_s'],2)} | {g(r['t_build_s'],2)} | {g(r['t_first_call_s'],2)} | "
          f"{g(r.get('t_preflight_s'),2)} | {ilp} | {g(r['t_to_first_progress_s'])} | {g(r['t_main_loop_s'])} | {g(r['wall_s'])} |")

print("\n### Memory and compile\n")
print("| run | peak VRAM MiB (memory_stats) | smi peak MiB | host RSS GiB | compiles first call (s) | compiles sampling (s) | GPU lock wall s |")
print("|---|---|---|---|---|---|---|")
for r in rs:
    print(f"| {r['name']} | {g(r['peak_vram_mib'])} | {g(r['smi_peak_mib'])} | {g(r['peak_host_rss_gib'],2)} | "
          f"{g(r['compile_first_call'])} ({g(r['compile_first_call_s'])}) | {g(r['compile_sampling'])} ({g(r['compile_sampling_s'])}) | {g(r['gpu_lock_wall_s'])} |")

print("\n### Pair comparisons (compare_progress over the common iteration range)\n")
print("| pair | replica | common rows | evals A / B | last iteration A / B | max rel logz / logl_min | B/A iterations/s | B/A evals/s | B/A -logX/s | A: it/s, ev/s | B: it/s, ev/s |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for k, c in sorted(F["compare_progress"].items()):
    rp = c.get("replica") or {}; P = c["performance"]; ra = P.get("ratio_B_over_A") or {}
    A, B = P.get("A") or {}, P.get("B") or {}
    mr = c.get("max_rel_diff_on_common_rows") or {}
    print(f"| {k} | {rp.get('deterministic_replica')} | {c['n_common_rows']} | {rp.get('n_like_evals')} | {rp.get('last_iteration')} | "
          f"{g(mr.get('logz'),3) if not isinstance(mr.get('logz'), float) else format(mr.get('logz'), '.2g')} / {format(mr.get('logl_min', 0) or 0, '.2g')} | "
          f"{g(ra.get('iterations_per_s'),4)} | {g(ra.get('evals_per_s'),4)} | {g(ra.get('neg_log_volume_per_s'),4)} | "
          f"{g(A.get('iterations_per_s'),2)}, {g(A.get('evals_per_s'),1)} | {g(B.get('iterations_per_s'),2)}, {g(B.get('evals_per_s'),1)} |")

print("\n### Posterior comparisons (converged pairs, compare_posteriors)\n")
for k, c in sorted(F["compare_posteriors"].items()):
    v = c["verdict"]; lz = c["logZ"]
    print(f"* {k}: samples bitwise {v.get('posterior_samples_bitwise_equal')}, logZ bitwise {lz.get('bitwise_equal')} "
          f"(A {lz.get('A')} +- {lz.get('A_err')}; B {lz.get('B')} +- {lz.get('B_err')}; n_sigma {lz.get('n_sigma')}), "
          f"max KS D {v.get('max_ks_D')}, max |dmean|/MCerr {v.get('max_abs_delta_mean_over_mc_error')}")
    for p, s in (c.get("parameters") or {}).items():
        A = s["A"]
        print(f"  * {p}: mean {A['mean']:.4f}, std {A['std']:.4f}, q16/50/84 {A.get('q16', float('nan')):.4f} / {A.get('q50', float('nan')):.4f} / {A.get('q84', float('nan')):.4f}; B mean {s['B']['mean']:.4f}; KS D {s['ks_D']}")
print(f"\nTotal GPU wall (gpu_run.sh windows of this gate incl. soft@10 parity records): {F['total_gpu_wall_s']:.1f} s over {len(F['gpu_windows'])} windows")
