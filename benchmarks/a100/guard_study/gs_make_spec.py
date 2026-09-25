#!/usr/bin/env python3
"""Write the guard-study executable spec (spec.json) and the campaign_run.py spec lists it drives.

    python gs_make_spec.py --gs /media/volume/tbs/darksirens_benchmark/benchmarks/guard_study [--dry-run-check]

Every record / run / analysis step carries `when` = the decision options that include it; the
runner applies the user's selections (spec.selected, defaulting to the recommended options),
keeps the entries whose `when` matches, and executes each `cmd` verbatim in list order
(phases P0 .. P8). numpy/stdlib only; no GPU.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import time

ROOT = "/media/volume/tbs/darksirens_benchmark"
REPO = f"{ROOT}/repos/darksirens-rebuild"
H = f"{REPO}/benchmarks/a100"
T = f"{H}/guard_study"
PYT = f"{ROOT}/envs/env_legacy/bin/python"          # CPU tools: the immutable reference env
X = f"{ROOT}/data/gwcat/exports"
ENV = {"legacy": f"{ROOT}/envs/env_legacy.sh", "o1": f"{ROOT}/envs/env_core_o1.sh"}
CAMPAIGN_ENV = {"legacy": "legacy", "o1": "core_o1"}
IMPL = {"legacy": "legacy", "o1": "core"}
JIT = {"legacy": "whole", "o1": "asis"}              # legacy whole == as-shipped; O1 asis = jitted as-shipped
ARM = {"legacy": "legacy_c042527", "o1": "core_O1_perf-jit-bound-analysis_f825906"}
PKG = {"legacy": "c042527238bd71421b792936bc48c3b815b90d6d", "o1": "f825906278140b8bfd80a13007ddd0136db28d49"}
PE = {"n4096": f"{X}/A_pe_chieff_bbh259_n4096_v20.h5", "n1024": f"{X}/A_pe_chieff_bbh259_n1024_v20.h5",
      "n256": f"{X}/A_pe_chieff_bbh259_n256_v20.h5"}
SEL = {"full": f"{X}/A_sel_chieffref_o3o4ab_v20.h5", "stride10": f"{X}/A_sel_chieffref_o3o4ab_v20_stride10.h5",
       "stride100": f"{X}/A_sel_chieffref_o3o4ab_v20_stride100.h5"}
SEED = 20260924
CAPS = [1.0, 2.0, 5.0, 10.0, 20.0]
DIAG = [("n4096", "full"), ("n1024", "stride10"), ("n256", "stride100")]
PROBES = [("n4096", "stride100"), ("n256", "full")]
ALL_CELLS = [(p, s) for p in ("n4096", "n1024", "n256") for s in ("full", "stride10", "stride100")]
PLANS = {"spectral_full_gwtc5": {"coords_tag": "gwtc5c05", "coords_args": ["--center", "gwtc5", "--spread", "0.05"],
                                 "coords_src": f"{ROOT}/benchmarks/gate1/m5b/coords/spectral_full_gwtc5__gwtc5c05.json",
                                 "coords_dst": "coords/spectral_full_gwtc5__gwtc5c05.json"},
         "spectral_full": {"coords_tag": None, "coords_args": None,
                           "coords_src": f"{ROOT}/benchmarks/gate1/coords/spectral_full.json",
                           "coords_dst": "coords/spectral_full.json"}}
POISON = ["--center", "none"]   # make_coords refuses: a missing study coordinate file fails loudly
TIMEOUT_S = 7200
LOCAL_CLONE = "/hildafs/projects/phy230014p/magana/darksirens_benchmark_local/darksirens-rebuild"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def q(x):
    return shlex.quote(str(x))


DECISIONS = [
 {"id": "Q1", "name": "Curve-grid cells", "recommended": "B",
  "question": "Which (PE file x selection file) cells get a fresh fixed-coordinate record, per plan and per code?",
  "options": {
   "A": "Diagonal only: n4096+full, n1024+stride10, n256+stride100, both plans, both codes (12 records). The other 6 cells per plan are composed from them, because N_eff/log mu depend only on the selection file and the PE terms only on the PE file (bitwise in all Gate 1 3x3 grids, legacy and core main).",
   "B": "Diagonal + separability probes: A plus n4096+stride100 and n256+full on the GWTC-5-centred plan, both codes (16 records). Checks the composition rule on the O1 code and on the GWTC-5 model, where it has not been checked.",
   "C": "Full 3x3 measured: every cell, both plans, both codes (36 records).",
   "D": "Reuse: take legacy values from existing campaign records (Gate 1 M2 for all 9 registry-fiducial cells, M5b for 2 GWTC-5 cells); run the O1 diagonal and the missing legacy GWTC-5 diagonal cell (7 records). Mixes harness commits and block settings."}},
 {"id": "Q2", "name": "Soft-penalty source", "recommended": "A",
  "question": "How are the soft-guard penalty values at caps 1, 2, 5, 10, 20 obtained?",
  "options": {
   "A": "numpy recomputation from the hard@1 records only (gs_guard.py; shared formula legacy selection.py:269-413 = core selection/gw.py:270-414). Validated on 30 existing records, 12 of them soft@1/soft@10: max relative difference 2.5e-16.",
   "B": "A plus direct soft records at caps 2, 5, 20 on the GWTC-5-centred n4096+full cell, both codes (6 records), as a live check at caps never run so far.",
   "C": "A plus direct soft records at caps 2, 5, 20 on the n4096+full cell of both plans, both codes (12 records)."}},
 {"id": "Q3", "name": "Rung-1 H0 wall map", "recommended": "A",
  "question": "Add a fixed-coordinate H0 scan over the rung-1 prior [20, 140] (48 bin midpoints of width 2.5, plus the centre and its repeat; population at the GWTC-5 preset; n4096+full)?",
  "options": {"A": "Yes, both codes (2 records).", "B": "Yes, legacy only (1 record).", "C": "No scan."}},
 {"id": "Q4", "name": "Injection-count method", "recommended": "B",
  "question": "How is the injection count needed for the hard@1 budget estimated?",
  "options": {
   "A": "Linear scaling from the three selection files only (as specified), with the estimate from each file shown.",
   "B": "A plus one per-injection weight record (bench_components.py, legacy, n4096+full, GWTC-5-centred coordinates): numpy N_eff for every stride-10 and stride-100 offset, a bootstrap at full size, and the top-weight share (1 record, ~150 MB npz on the host).",
   "C": "B for both codes (2 records)."}},
 {"id": "Q5", "name": "Inference run set", "recommended": "A",
  "question": "Which dynesty runs (n4096+full, nlive 1000, dlogz 0.1, seed 20260924, 300,000 evaluations or 3600 s)?",
  "options": {
   "A": "As specified: rung 1 at soft 5/10/20 and hard 10/20; rung 3 at soft 5/10/20 and hard 10; legacy and core (O1): 18 runs.",
   "B": "A, but reuse the three Gate 5 soft@10 dynesty records with identical settings (legacy rung 1, O1 rung 1, legacy rung 3): 15 new runs.",
   "C": "A plus rung 1 at hard 5 (the cap at which the rung centre itself fails the hard guard) and rung 3 at hard 20, both codes: 22 runs."}},
 {"id": "Q6", "name": "-inf accounting for hard caps", "recommended": "A",
  "question": "How is time spent in the hard guard's -inf region measured?",
  "options": {
   "A": "Commit the observation-only counter to infer_ladder.py (non-finite eager calls per phase; CPU ladder smoke passes, 6/6) and also count dynesty's initial live points stored at its -1e300 floor.",
   "B": "Dead-point floor count only (initial live points drawn inside the -inf region); no count of rejected proposals; no harness change."}},
 {"id": "Q7", "name": "Penalty share at the posterior mean", "recommended": "A",
  "question": "Evaluate the likelihood at each run's posterior mean to get the soft penalty and its share of the total there?",
  "options": {"A": "Yes, both codes: one record per rung per code holding every run's posterior mean (4 records).",
              "B": "Yes, legacy only (2 records).",
              "C": "No; report the penalty only at the curve-grid and H0-scan coordinates."}},
 {"id": "Q8", "name": "Legacy vs core (O1) pass rule", "recommended": "A",
  "question": "What counts as agreement between legacy and core (O1) for a same-seed inference pair?",
  "options": {"A": "Bitwise: equal evaluation counts and ncall trace, bit-identical logZ and posterior samples; any difference is reported as a finding with the first diverging iteration.",
              "B": "Statistical: posterior means within 0.1 posterior sigma and logZ within 1 combined error (compare_posteriors)."}},
 {"id": "Q9", "name": "Execution order and stop rule", "recommended": "A",
  "question": "How are the GPU phases sequenced?",
  "options": {"A": "Fixed-coordinate records first, then a CPU audit gate (recomputation, separability, code parity); inference only if the gate passes; rung 1 before rung 3; posterior-mean records last.",
              "B": "One pass through every phase, auditing at the end."}},
 {"id": "Q10", "name": "Housekeeping defaults", "recommended": "A",
  "question": "Accept these defaults: single-pass blocks everywhere; 3 timed calls and 1 warm-up, no utilisation window (the 'n_calls=3 < 20' record gap is accepted); a cold XLA cache per GPU process, kept after the run; env_legacy python for every CPU tool (env_core is never used); manifest gate label 'guard_study'; a 7200 s process backstop; only JSON/MD/CSV summaries copied to Hildafs; study tools committed to bench/a100-campaign.",
  "options": {"A": "Accept all.", "B": "Change some (say which in the note)."}},
]


def when(**kw):
    return {k: list(v) for k, v in kw.items()}


def curve_entries():
    """campaign_run.py entries for every candidate fixed-coordinate record of the curve phase."""
    out = []

    def add(rid, code, plan, pe, sel, w, guard="hard", cap=1.0, tool=None, extra=None, tag=None, cargs=None,
            compare_to=None, role=None):
        e = {"record_id": rid, "matrix": "GS", "env": CAMPAIGN_ENV[code], "impl": IMPL[code], "jit": JIT[code],
             "blocks": "none", "sel_batch": "none", "pe_block": "none", "plan": plan, "pe": PE[pe], "sel": SEL[sel],
             "pe_label": f"bbh259_{pe}", "sel_label": sel, "n_calls": 3, "warmup": 1, "util_window_s": 0,
             "cache": "cold", "compare_to": compare_to or [],
             "flags": {"study": "guard_study", "role": role, "code": code, "cell": f"{pe}+{sel}"},
             "guard": guard, "max_variance": cap}
        t = PLANS.get(plan, {}).get("coords_tag") if tag is None else tag
        a = PLANS.get(plan, {}).get("coords_args") if cargs is None else cargs
        if t:
            e["coords_tag"] = t
            e["coords_args"] = a
        if tool:
            e["tool"] = tool
        if extra:
            e["extra_args"] = extra
        out.append({"campaign": e, "when": w})

    def cid(code, plan, pe, sel, suffix="hard1", kind="C"):
        return f"GS_{kind}_{code}_{JIT[code]}_{plan}_bbh259_{pe}_{sel}_{suffix}"

    for plan in PLANS:
        for pe, sel in ALL_CELLS:
            if (pe, sel) in DIAG:
                if plan == "spectral_full_gwtc5" and (pe, sel) == ("n256", "stride100"):
                    wl, wo = "ABCD", "ABCD"
                else:
                    wl, wo = "ABC", "ABCD"
                role = "diagonal"
            elif plan == "spectral_full_gwtc5" and (pe, sel) in PROBES:
                wl = wo = "BC"
                role = "separability probe"
            else:
                wl = wo = "C"
                role = "full grid"
            lid = cid("legacy", plan, pe, sel)
            add(lid, "legacy", plan, pe, sel, when(Q1=wl), role=role)
            refs = [lid]
            if plan == "spectral_full":  # the Gate 1 legacy record of the same cell (default guard = hard@1)
                refs.append(f"{ROOT}/benchmarks/gate1/records/M2_legacy_whole_default_spectral_full_bbh259_{pe}_{sel}.json")
            add(cid("o1", plan, pe, sel), "o1", plan, pe, sel, when(Q1=wo), role=role, compare_to=refs)
    # Q2 soft checks
    for plan in PLANS:
        for code in ("legacy", "o1"):
            for cap in (2.0, 5.0, 20.0):
                rid = cid(code, plan, "n4096", "full", f"soft{int(cap)}", "K")
                w = when(Q2="BC") if plan == "spectral_full_gwtc5" else when(Q2="C")
                add(rid, code, plan, "n4096", "full", w, guard="soft", cap=cap, role="soft-penalty check",
                    compare_to=[cid("legacy", plan, "n4096", "full", f"soft{int(cap)}", "K")] if code == "o1" else None)
    # Q3 H0 scan
    for code, w in (("legacy", "AB"), ("o1", "A")):
        add(cid(code, "spectral_H0_gwtc5", "n4096", "full", "hard1_h0grid", "S"), code, "spectral_H0_gwtc5",
            "n4096", "full", when(Q3=w), tag="h0grid49", cargs=POISON, role="rung-1 H0 wall map",
            compare_to=[cid("legacy", "spectral_H0_gwtc5", "n4096", "full", "hard1_h0grid", "S")] if code == "o1" else None)
    # Q4 per-injection weights
    for code, w in (("legacy", "BC"), ("o1", "C")):
        add(cid(code, "spectral_full_gwtc5", "n4096", "full", "hard1_selweights", "W"), code, "spectral_full_gwtc5",
            "n4096", "full", when(Q4=w), tool="components", role="per-injection selection weights",
            extra=["--components", "w_weights,e_sel_reduce", "--full-array-coords", "0,1,2,3,4,5,6,7,8", "--no-aot"])
    rank = {"diagonal": 0, "separability probe": 1, "full grid": 2, "soft-penalty check": 3,
            "rung-1 H0 wall map": 4, "per-injection selection weights": 5}
    out.sort(key=lambda e: (rank[e["campaign"]["flags"]["role"]], e["campaign"]["plan"] != "spectral_full_gwtc5",
                            e["campaign"]["flags"]["cell"], e["campaign"]["max_variance"],
                            0 if e["campaign"]["flags"]["code"] == "legacy" else 1))
    return out


def postmean_entries():
    out = []
    for rung, plan in (("1", "spectral_H0_gwtc5"), ("3", "spectral_full_gwtc5")):
        for code, w in (("legacy", "AB"), ("o1", "A")):
            rid = f"GS_P_{code}_{JIT[code]}_{plan}_bbh259_n4096_full_hard1_postmean_r{rung}"
            e = {"record_id": rid, "matrix": "GS", "env": CAMPAIGN_ENV[code], "impl": IMPL[code], "jit": JIT[code],
                 "blocks": "none", "sel_batch": "none", "pe_block": "none", "plan": plan, "pe": PE["n4096"],
                 "sel": SEL["full"], "pe_label": "bbh259_n4096", "sel_label": "full", "n_calls": 3, "warmup": 1,
                 "util_window_s": 0, "cache": "cold",
                 "compare_to": ([f"GS_P_legacy_whole_{plan}_bbh259_n4096_full_hard1_postmean_r{rung}"] if code == "o1" else []),
                 "flags": {"study": "guard_study", "role": f"posterior means, rung {rung}", "code": code},
                 "guard": "hard", "max_variance": 1.0, "coords_tag": f"postmean_r{rung}", "coords_args": POISON}
            out.append({"campaign": e, "when": when(Q7=w)})
    return out


def infer_runs():
    runs = []
    sets = [("1", "soft", 5.0, "ABC"), ("1", "soft", 10.0, "AC"), ("1", "soft", 20.0, "ABC"),
            ("1", "hard", 10.0, "ABC"), ("1", "hard", 20.0, "ABC"), ("1", "hard", 5.0, "C"),
            ("3", "soft", 5.0, "ABC"), ("3", "soft", 10.0, "AC"), ("3", "soft", 20.0, "ABC"),
            ("3", "hard", 10.0, "ABC"), ("3", "hard", 20.0, "C")]
    reuse = {("legacy", "1"): "G5_legacy_r1_dynesty_soft10_e300k", ("o1", "1"): "G5_o1_r1_dynesty_soft10_e300k",
             ("legacy", "3"): "G5_legacy_r3_dynesty_soft10_e300k"}
    refs = {"1": ["gate1/m5b/soft10/records/M5B_legacy_whole_default_spectral_H0_gwtc5_bbh259_n4096_full_soft10",
                  "gate1/m5b/soft10/records/M5B_core_asis_default_spectral_H0_gwtc5_bbh259_n4096_full_soft10",
                  "gate4/records/G4_o1_asis_default_spectral_H0_gwtc5_A4096full_soft1"],
            "3": ["gate1/m5b/soft10/records/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_n4096_full_soft10",
                  "gate1/m5b/soft10/records/M5B_core_asis_default_spectral_full_gwtc5_bbh259_n4096_full_soft10",
                  "gate4/records/G4_o1_asis_default_spectral_full_gwtc5_A4096full_soft1"]}
    GI = "@GS/inference"
    for rung, guard, cap, w in sets:
        for code in ("legacy", "o1"):
            ww = w
            if (guard, cap) == ("soft", 10.0) and (code, rung) in reuse:
                ww = w  # A, C run it fresh; B reuses the Gate 5 record
            elif (guard, cap) == ("soft", 10.0):
                ww = "ABC"  # O1 rung 3 soft10 has no Gate 5 record: always run
            name = f"GS_I_{code}_r{rung}_dynesty_{guard}{int(cap)}_e300k"
            note = (f"Guard study (user-ordered, post-campaign): dynesty only; guard {guard} cap {cap:g}; "
                    f"budget first of dlogz 0.1, 300000 evaluations, 3600 s sampling wall; "
                    f"arm {'core (O1) = perf/jit-bound-analysis f825906, the jitted as-shipped path' if code == 'o1' else 'legacy reference c042527'}")
            out = f"{GI}/runs/{name}"
            smi = f"{GI}/smi/{name}.smi.csv"
            cdir = f"{ROOT}/xla_cache/runs/{name}"
            inner = " ".join([
                "source", ENV[code], "&&", "cd", f"{GI}", "&&", "exec", "timeout", "-s", "TERM", "-k", "300", str(TIMEOUT_S),
                "python", f"{H}/infer_ladder.py", "--impl", IMPL[code], "--rung", rung, "--sampler", "dynesty",
                "--pe", PE["n4096"], "--sel", SEL["full"], "--nlive", "1000", "--dlogz", "0.1", "--seed", str(SEED),
                "--max-samples", "0", "--guard", guard, "--max-variance", repr(cap), "--tinyns-preset", "recommended",
                "--sel-batch", "none", "--pe-block", "none", "--out", out, "--device", "gpu", "--cache-dir", cdir,
                "--cache-mode", "cold", "--smi-log", smi, "--label", name, "--arm", ARM[code],
                "--max-evals", "300000", "--max-wall-s", "3600", "--policy-note", f"'{note}'"] +
                sum([["--parity-ref", r] for r in refs[rung]], []))
            cmd = (f"test ! -e {cdir} && test ! -e {out}/record.json && mkdir -p {cdir} {GI}/runs {GI}/smi {GI}/logs && "
                   f"env -u PYTHONPATH -u JAX_PLATFORMS PYTHONDONTWRITEBYTECODE=1 {ROOT}/bin/gpu_run.sh {smi} "
                   f"bash -c \"{inner}\" > {GI}/logs/{name}.stdout 2> {GI}/logs/{name}.stderr")
            runs.append({"name": name, "rung": rung, "code": code, "impl": IMPL[code], "env_script": ENV[code],
                         "arm": ARM[code], "guard": guard, "cap": cap, "when": when(Q5=ww), "cmd": cmd,
                         "expected_exit": {"0": "converged", "7": "budget-capped", "5": "sampler error (e.g. preflight abort)"},
                         "reuse_when_Q5_B": (f"{ROOT}/benchmarks/gate5/runs/{reuse[(code, rung)]}"
                                             if (guard, cap) == ("soft", 10.0) and (code, rung) in reuse else None)})
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gs", default=f"{ROOT}/benchmarks/guard_study")
    ap.add_argument("--dry-run-check", action="store_true")
    ap.add_argument("--page-url", default=None)
    a = ap.parse_args()
    GS = a.gs
    sub = lambda s: s.replace("@GS", GS)  # noqa: E731

    curves = curve_entries()
    pm = postmean_entries()
    runs = infer_runs()
    for r in runs:
        r["cmd"] = sub(r["cmd"])
        if r.get("reuse_when_Q5_B"):
            pass
    os.makedirs(f"{GS}/curves", exist_ok=True)
    os.makedirs(f"{GS}/inference/postmean", exist_ok=True)
    camp_curves = f"{GS}/curves/curves_campaign.json"
    camp_pm = f"{GS}/inference/postmean/postmean_campaign.json"
    for path, ents in ((camp_curves, curves), (camp_pm, pm)):
        with open(path, "w") as f:
            json.dump([e["campaign"] for e in ents], f, indent=1)
            f.write("\n")

    cr = (f"cd {H} && env -u PYTHONPATH -u JAX_PLATFORMS PYTHONDONTWRITEBYTECODE=1 {PYT} campaign_run.py "
          f"--driver-python {PYT} --gate guard_study --resume")
    dry = {}
    if a.dry_run_check:
        r = subprocess.run([PYT, f"{H}/campaign_run.py", "--spec", camp_curves, "--outdir", f"{GS}/curves",
                            "--driver-python", PYT, "--dry-run"], capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", JAX_PLATFORMS="cpu"))
        if r.returncode != 0:
            raise SystemExit("campaign_run --dry-run failed: " + r.stderr[-2000:])
        for line in r.stdout.splitlines():
            rid, _, cmd = line.partition(" ")
            dry[rid] = cmd
    records = []
    for e in curves:
        c = e["campaign"]
        rec = {"record_id": c["record_id"], "phase": "P1", "role": c["flags"]["role"], "code": c["flags"]["code"],
               "plan": c["plan"], "cell": c["flags"]["cell"], "guard": f"{c['guard']}@{c['max_variance']:g}",
               "tool": c.get("tool", "bench_fixed_theta"), "when": e["when"],
               "cmd": f"{cr} --spec {camp_curves} --outdir {GS}/curves --only {c['record_id']}",
               "equivalent_gpu_cmd": dry.get(c["record_id"]),
               "record_path": f"{GS}/curves/records/{c['record_id']}.json",
               "compare_to": c["compare_to"]}
        records.append(rec)
    for e in pm:
        c = e["campaign"]
        records.append({"record_id": c["record_id"], "phase": "P6", "role": c["flags"]["role"],
                        "code": c["flags"]["code"], "plan": c["plan"], "cell": "n4096+full", "guard": "hard@1",
                        "tool": "bench_fixed_theta", "when": e["when"],
                        "cmd": f"{cr} --spec {camp_pm} --outdir {GS}/inference/postmean --only {c['record_id']}",
                        "equivalent_gpu_cmd": None,
                        "record_path": f"{GS}/inference/postmean/records/{c['record_id']}.json",
                        "compare_to": c["compare_to"]})

    # --- input / coordinate checksums --------------------------------------------------------
    inputs = {os.path.basename(p): {"path": p, "sha256": sha256(p)} for p in list(PE.values()) + list(SEL.values())}
    with open(f"{GS}/inputs.sha256", "w") as f:
        for k, v in inputs.items():
            f.write(f"{v['sha256']}  {v['path']}\n")
    coords = {}
    for plan, d in PLANS.items():
        coords[plan] = {"source": d["coords_src"], "study_copy": f"{GS}/curves/{d['coords_dst']}",
                        "sha256": sha256(d["coords_src"])}
    h0 = f"{GS}/curves/coords/spectral_H0_gwtc5__h0grid49.json"
    coords["spectral_H0_gwtc5 (H0 scan)"] = {"source": f"{T}/gs_coords.py h0grid --seed {SEED} --step 2.5",
                                            "study_copy": h0, "sha256": sha256(h0) if os.path.isfile(h0) else None}
    with open(f"{GS}/coords.sha256", "w") as f:
        for k, v in coords.items():
            if v["sha256"]:
                f.write(f"{v['sha256']}  {v['study_copy']}\n")

    # --- phases --------------------------------------------------------------------------------
    TOOLENV = f"env -u PYTHONPATH JAX_PLATFORMS=cpu PYTHONDONTWRITEBYTECODE=1 {PYT}"
    A1 = f"{GS}/curves/analysis"
    A2 = f"{GS}/inference/analysis"
    m5b = f"{ROOT}/benchmarks/gate1/m5b"
    smoke_env = (f"env -u PYTHONPATH JAX_PLATFORMS=cpu JAX_ENABLE_X64=1 PYTHONDONTWRITEBYTECODE=1 "
                 f"BENCH_LEGACY_PYTHON={ROOT}/envs/env_legacy/bin/python BENCH_CORE_PYTHON={ROOT}/envs/env_core_o1/bin/python "
                 f"BENCH_PRODUCT_A_DIR={X} JAX_COMPILATION_CACHE_DIR={GS}/_smoke_cache")
    p0 = [
     {"id": "P0.1", "what": "harness at the study head (tools present), clean tree", "when": {},
      "cmd": f"cd {REPO} && git pull --rebase origin bench/a100-campaign && test -z \"$(git status --porcelain)\" && test -f {T}/gs_guard.py && git rev-parse HEAD | tee {GS}/harness_head.txt"},
     {"id": "P0.2a", "what": "observation-only non-finite counter in infer_ladder.py (Q6-A): apply, CPU ladder smoke, commit on js2a100", "when": when(Q6="A"), "host": "js2a100",
      "cmd": (f"cd {REPO} && (grep -q 'self.nonfinite = {{}}' benchmarks/a100/infer_ladder.py || "
              f"(git apply {T}/infer_ladder_nonfinite.patch && cd {H} && {smoke_env} {ROOT}/envs/env_core_o1/bin/python -m pytest -q tests/test_ladder_smoke.py --basetemp={GS}/_smoke_tmp "
              f"&& cd {REPO} && git add benchmarks/a100/infer_ladder.py && git -c user.name='Ignacio Magana' -c user.email=magana@miko.ib.vera.psc.edu commit -m 'bench/a100: infer_ladder counts non-finite eager likelihood values per phase (likelihood_calls.nonfinite; observation only) for the guard study')) "
              f"&& git rev-parse HEAD | tee {GS}/harness_head_inference.txt")},
     {"id": "P0.2b", "what": "push the counter commit (js2a100 has no GitHub credentials: relay through the Hildafs clone), then resync js2a100", "when": when(Q6="A"), "host": "Hildafs",
      "cmd": (f"cd {LOCAL_CLONE} && git fetch -q js2a100:{REPO} bench/a100-campaign && git merge --ff-only FETCH_HEAD && "
              f"git pull --rebase origin bench/a100-campaign && git push origin bench/a100-campaign && "
              f"ssh -o BatchMode=yes js2a100 'cd {REPO} && git pull --rebase -q origin bench/a100-campaign && git log --oneline -1'")},
     {"id": "P0.3", "what": "input checksums", "when": {}, "cmd": f"sha256sum -c {GS}/inputs.sha256"},
     {"id": "P0.4", "what": "coordinates of record copied into the curve campaign directory (never regenerated)", "when": {},
      "cmd": " && ".join([f"mkdir -p {GS}/curves/coords"] +
                         [f"cp -n {d['coords_src']} {GS}/curves/{d['coords_dst']}" for d in PLANS.values()] +
                         [f"(test -f {h0} || {TOOLENV} {T}/gs_coords.py h0grid --seed {SEED} --step 2.5 --out {h0})",
                          f"sha256sum -c {GS}/coords.sha256"])},
     {"id": "P0.5", "what": "the numpy guard recomputation reproduces every existing soft/hard M5b record (must pass)", "when": {},
      "cmd": f"mkdir -p {A1} && {TOOLENV} {T}/gs_guard.py validate {m5b}/records/M5B_*.json {m5b}/soft10/records/M5B_*.json --out {A1}/validate_existing_m5b.json"},
    ]
    p2 = [
     {"id": "P2.1", "what": "recomputation check on every new curve record", "when": {},
      "cmd": f"{TOOLENV} {T}/gs_guard.py validate {GS}/curves/records/GS_*.json --out {A1}/validate_new.json"},
     {"id": "P2.2", "what": "reproduction of campaign records (guard-independent fields bitwise)", "when": {},
      "cmd": " ; ".join([
        f"{TOOLENV} {T}/gs_guard.py repro --new {GS}/curves/records/GS_C_legacy_whole_spectral_full_gwtc5_bbh259_n4096_full_hard1.json --ref {m5b}/records/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_n4096_full_hard10.json --ref {m5b}/soft10/records/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_n4096_full_soft10.json --out {A1}/repro_legacy_gwtc5_n4096_full.json",
        f"{TOOLENV} {T}/gs_guard.py repro --new {GS}/curves/records/GS_C_legacy_whole_spectral_full_gwtc5_bbh259_n1024_stride10_hard1.json --ref {m5b}/records/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_n1024_stride10_hard10.json --out {A1}/repro_legacy_gwtc5_n1024_stride10.json",
        f"{TOOLENV} {T}/gs_guard.py repro --new {GS}/curves/records/GS_C_o1_asis_spectral_full_gwtc5_bbh259_n4096_full_hard1.json --ref {ROOT}/benchmarks/gate4/records/G4_o1_asis_default_spectral_full_gwtc5_A4096full_soft1.json --out {A1}/repro_o1_gwtc5_n4096_full.json",
        f"{TOOLENV} {T}/gs_guard.py repro --new {GS}/curves/records/GS_C_o1_asis_spectral_full_bbh259_n4096_full_hard1.json --ref {ROOT}/benchmarks/gate4/records/G4_o1_asis_default_spectral_full_A4096full.json --out {A1}/repro_o1_registry_n4096_full.json"]
        + [f"{TOOLENV} {T}/gs_guard.py repro --new {GS}/curves/records/GS_C_legacy_whole_spectral_full_bbh259_{p}_{s}_hard1.json --ref {ROOT}/benchmarks/gate1/records/M2_legacy_whole_default_spectral_full_bbh259_{p}_{s}.json --out {A1}/repro_legacy_registry_{p}_{s}.json" for p, s in DIAG]),
      "note": "a missing new record (not selected under Q1) makes that line fail harmlessly; the audit reads the JSON files that exist"},
     {"id": "P2.3", "what": "curve tables, separability, code agreement (+ reused legacy records under Q1-D)", "when": {},
      "cmd": f"{TOOLENV} {T}/gs_guard.py curves --records {GS}/curves/records/GS_C_*.json --caps 1,2,5,10,20 --out {A1}/curves.json --md {A1}/curves.md --csv {A1}/curves.csv",
      "cmd_when_Q1_D": f"{TOOLENV} {T}/gs_guard.py curves --records {GS}/curves/records/GS_C_*.json " + " ".join(
          [f"{ROOT}/benchmarks/gate1/records/M2_legacy_whole_default_spectral_full_bbh259_{p}_{s}.json" for p, s in ALL_CELLS] +
          [f"{m5b}/records/M5B_legacy_whole_default_spectral_full_gwtc5_bbh259_{c}_hard10.json" for c in ("n4096_full", "n1024_stride10")]) +
          f" --caps 1,2,5,10,20 --out {A1}/curves.json --md {A1}/curves.md --csv {A1}/curves.csv"},
     {"id": "P2.4", "what": "H0 wall map tables (Q3)", "when": when(Q3="AB"),
      "cmd": f"{TOOLENV} {T}/gs_guard.py curves --records {GS}/curves/records/GS_S_*.json --caps 1,2,5,10,20 --out {A1}/h0scan.json --md {A1}/h0scan.md --csv {A1}/h0scan.csv"},
     {"id": "P2.5", "what": "injection-count dependence at the GWTC-5 centre and the registry fiducial (coordinate 0)", "when": {},
      "cmd": f"{TOOLENV} {T}/gs_guard.py injections --records {GS}/curves/records/GS_C_*.json --coord 0 --caps 1,2,5,10,20 --out {A1}/injections.json --md {A1}/injections.md"},
     {"id": "P2.6", "what": "N_eff versus detected injections from per-injection weights (Q4-B/C)", "when": when(Q4="BC"),
      "cmd": " ; ".join([f"{TOOLENV} {T}/gs_neff_subsample.py --record {GS}/curves/records/GS_W_{c}_{JIT[c]}_spectral_full_gwtc5_bbh259_n4096_full_hard1_selweights.json --coords 0,1,2,3,4,5,6,7 --strides 2,5,10,20,50,100 --check {GS}/curves/records/GS_C_{c}_{JIT[c]}_spectral_full_gwtc5_bbh259_n1024_stride10_hard1.json --check {GS}/curves/records/GS_C_{c}_{JIT[c]}_spectral_full_gwtc5_bbh259_n256_stride100_hard1.json --bootstrap 200 --seed {SEED} --out {A1}/neff_subsample_{c}.json --md {A1}/neff_subsample_{c}.md" for c in ("legacy", "o1")]),
      "note": "the O1 line applies under Q4-C only; under Q4-B it fails harmlessly (no O1 weight record)"},
     {"id": "P2.7", "what": "soft-record live check (Q2-B/C): recomputation vs the recorded soft values", "when": when(Q2="BC"),
      "cmd": f"{TOOLENV} {T}/gs_guard.py validate {GS}/curves/records/GS_K_*.json --out {A1}/validate_soft_checks.json"},
    ]
    p4 = []
    pairs = sorted({(r["rung"], r["guard"], r["cap"]) for r in runs})
    for rung, guard, cap in pairs:
        a_ = f"GS_I_legacy_r{rung}_dynesty_{guard}{int(cap)}_e300k"
        b_ = f"GS_I_o1_r{rung}_dynesty_{guard}{int(cap)}_e300k"
        tag = f"r{rung}_{guard}{int(cap)}_legacy_vs_o1"
        wr = [r["when"]["Q5"] for r in runs if r["name"] == a_][0]
        p4.append({"id": f"P4.{tag}", "what": f"legacy vs core (O1), rung {rung}, {guard}@{cap:g}", "when": when(Q5=wr),
                   "cmd": (f"mkdir -p {GS}/inference/compare && cd {GS}/inference && {TOOLENV} {H}/compare_progress.py runs/{a_} runs/{b_} --out compare/{tag}.progress.json --md compare/{tag}.progress.md ; "
                           f"{PYT} -c \"import json,sys; sys.exit(0 if all(json.load(open(p))['status']=='ok' for p in sys.argv[1:]) else 3)\" runs/{a_}/record.json runs/{b_}/record.json && "
                           f"{TOOLENV} {H}/compare_posteriors.py runs/{a_} runs/{b_} --out compare/{tag}.json --md compare/{tag}.md"),
                   "note_when_Q5_B": "for the rung-1 soft@10 pair the Gate 5 records G5_legacy_r1_dynesty_soft10_e300k / G5_o1_r1_dynesty_soft10_e300k are already compared (gate5/compare/dynesty_r1_soft_legacy_vs_o1.*)"})
    p4.append({"id": "P4.cross", "what": "posterior sensitivity to the guard (cross-cap tables, dead-point floor, non-finite counts, legacy vs core bitwise)", "when": {},
               "cmd": f"mkdir -p {A2} && {TOOLENV} {T}/gs_guard.py inference --runs '{GS}/inference/runs/GS_I_*' --reference-cap 10 --out {A2}/inference.json --md {A2}/inference.md",
               "cmd_when_Q5_B": f"mkdir -p {A2} && {TOOLENV} {T}/gs_guard.py inference --runs '{GS}/inference/runs/GS_I_*' {ROOT}/benchmarks/gate5/runs/G5_legacy_r1_dynesty_soft10_e300k {ROOT}/benchmarks/gate5/runs/G5_o1_r1_dynesty_soft10_e300k {ROOT}/benchmarks/gate5/runs/G5_legacy_r3_dynesty_soft10_e300k --reference-cap 10 --out {A2}/inference.json --md {A2}/inference.md"})
    p5 = []
    for rung, plan in (("1", "spectral_H0_gwtc5"), ("3", "spectral_full_gwtc5")):
        extra = "" 
        p5.append({"id": f"P5.r{rung}", "what": f"posterior-mean coordinates, rung {rung} (every finished run of both codes)", "when": when(Q7="AB"),
                   "cmd": f"mkdir -p {GS}/inference/postmean/coords && {TOOLENV} {T}/gs_coords.py postmean --rung {rung} --seed {SEED} --runs {GS}/inference/runs/GS_I_*_r{rung}_dynesty_* --out {GS}/inference/postmean/coords/{plan}__postmean_r{rung}.json",
                   "cmd_when_Q5_B": f"mkdir -p {GS}/inference/postmean/coords && {TOOLENV} {T}/gs_coords.py postmean --rung {rung} --seed {SEED} --runs {GS}/inference/runs/GS_I_*_r{rung}_dynesty_* {ROOT}/benchmarks/gate5/runs/G5_*_r{rung}_dynesty_soft10_e300k --out {GS}/inference/postmean/coords/{plan}__postmean_r{rung}.json"})
    p7 = [{"id": "P7.1", "what": "recomputation check + soft-penalty share at the posterior means", "when": when(Q7="AB"),
           "cmd": (f"{TOOLENV} {T}/gs_guard.py validate {GS}/inference/postmean/records/GS_P_*.json --out {A2}/validate_postmean.json && "
                   f"{TOOLENV} {T}/gs_guard.py postmean-share --records {GS}/inference/postmean/records/GS_P_*.json --caps 1,2,5,10,20 --out {A2}/postmean_share.json --md {A2}/postmean_share.md")}]
    p8 = [{"id": "P8.1", "what": "small local copy (JSON/MD/CSV only; no npz, caches or logs)", "when": {},
           "cmd": ("rsync -a --prune-empty-dirs --include '*/' --include '*.json' --include '*.md' --include '*.csv' --exclude '*' "
                   f"js2a100:{GS}/ /hildafs/projects/phy230014p/magana/darksirens_benchmark_local/guard_study/"),
           "host": "Hildafs (run from the local side)"}]

    order = {"P1": "curve-grid GPU records, in this order: diagonal cells (both codes, legacy first), probes, full-grid cells, soft checks, H0 scans, weight records",
             "P3": "inference GPU runs: rung 1 then rung 3; within a rung soft 10, soft 20, soft 5, hard 20, hard 10 (hard 5 last); legacy then core (O1) for each cap"}
    rank = {("soft", 10.0): 0, ("soft", 20.0): 1, ("soft", 5.0): 2, ("hard", 20.0): 3, ("hard", 10.0): 4, ("hard", 5.0): 5}
    runs.sort(key=lambda r: (r["rung"], rank[(r["guard"], r["cap"])], 0 if r["code"] == "legacy" else 1))

    spec = {
     "schema": "gs-spec/1",
     "title": "Guard study: selection-N_eff guard caps, legacy darksirens vs darksirens-core (O1), A100",
     "status": "DESIGN - awaiting the user's selections (page 'Guard Study Design'); 'selected' holds the recommended options until then",
     "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
     "generator": f"{T}/gs_make_spec.py",
     "scope_note": "The study reports options and evidence; it does not choose the production guard setting (the user does).",
     "root": ROOT, "harness": {"repo": REPO, "branch": "bench/a100-campaign", "dir": H, "tools": T},
     "rules": ["every GPU process through bin/gpu_run.sh (flock; one GPU job at a time; wait for the lock)",
               "no XLA compiler flags; env scripts only (env_legacy.sh, env_core_o1.sh); env_core.sh is never used",
               "cold XLA cache per GPU process at xla_cache/runs/<id> (campaign_run.py cold mode / the run command's mkdir)",
               "no git push to main; harness changes only on bench/a100-campaign, pull --rebase before push, never force-push; js2a100 cannot push (no GitHub credentials): push from the Hildafs clone",
               "execute entries whose 'when' matches 'selected'; an entry with an empty 'when' always runs",
               "where an entry has cmd_when_<Q>_<opt> and that option is selected, run that command instead of cmd"],
     "codes": {"legacy": {"label": "legacy", "package": PKG["legacy"], "env_script": ENV["legacy"], "jit": "whole (= the as-shipped factory jit)", "arm": ARM["legacy"]},
               "o1": {"label": "core (O1)", "package": PKG["o1"], "branch": "perf/jit-bound-analysis", "env_script": ENV["o1"], "jit": "asis (the jitted as-shipped BoundAnalysis)", "arm": ARM["o1"]}},
     "inputs": inputs, "coordinates": coords,
     "decisions": DECISIONS,
     "selected": {d["id"]: d["recommended"] for d in DECISIONS},
     "selection_source": {"page": a.page_url, "how": "the page's db collection 'decisions' (doc id = Q1..Q10, fields 'choice' and 'note'); read with ArtifactData list; an absent doc means the recommended option"},
     "harness_head_at_design": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
     "naming": {
       "curve": "GS_C_<code>_<jit>_<plan>_bbh259_<pe>_<sel>_hard1",
       "soft_check": "GS_K_<code>_<jit>_<plan>_bbh259_n4096_full_soft<cap>",
       "h0_scan": "GS_S_<code>_<jit>_spectral_H0_gwtc5_bbh259_n4096_full_hard1_h0grid",
       "weights": "GS_W_<code>_<jit>_spectral_full_gwtc5_bbh259_n4096_full_hard1_selweights",
       "inference": "GS_I_<legacy|o1>_r<rung>_dynesty_<soft|hard><cap>_e300k",
       "postmean": "GS_P_<code>_<jit>_<plan>_bbh259_n4096_full_hard1_postmean_r<rung>",
       "code": "legacy (jit whole) | o1 (jit asis)",
       "dirs": {"curves": f"{GS}/curves/{{records,summaries,logs,smi,coords,analysis}}",
                "inference": f"{GS}/inference/{{runs,smi,logs,compare,analysis,postmean}}"}},
     "order": order,
     "phases": {
       "P0": {"title": "CPU preparation", "steps": p0},
       "P1": {"title": "GPU: fixed-coordinate curve records (campaign_run.py, one record per call, --resume)", "records": [r for r in records if r["phase"] == "P1"]},
       "P2": {"title": "CPU: curve analysis; audit gate G1 (Q9-A: inference starts only if G1 passes)", "steps": p2},
       "P3": {"title": "GPU: dynesty inference runs", "runs": runs},
       "P4": {"title": "CPU: inference comparisons", "steps": p4},
       "P5": {"title": "CPU: posterior-mean coordinates", "steps": p5},
       "P6": {"title": "GPU: posterior-mean fixed-coordinate records", "records": [r for r in records if r["phase"] == "P6"]},
       "P7": {"title": "CPU: posterior-mean analysis; audit gate G2", "steps": p7},
       "P8": {"title": "local copy and results report", "steps": p8}},
     "quantities_per_coordinate": [
       "N_eff (selection effective sample size; recorded)", "N_obs^2/N_eff (selection share of the variance)",
       "sigma2_PE (sum of the per-event MC variances; recorded)", "sigma2_lnL = sigma2_PE + N_obs^2/N_eff (total MC variance)",
       "log mu", "sum of per-event log evidences", "unguarded total = sum ln Z_i - N_obs log mu + N_obs(N_obs+3)/(2 N_eff)",
       "T(cap) = max(5 N_obs, N_obs^2 / max(cap - sigma2_PE, 1e-12)) for cap in 1, 2, 5, 10, 20", "N_eff / T(cap)",
       "budget exhausted (cap <= sigma2_PE)", "hard verdict per cap (N_eff > T)", "soft wall per cap",
       "Taylor-term freeze per cap", "soft penalty per cap (soft total - unguarded)", "soft total per cap",
       "penalty share of the total per cap", "unpenalised flag (soft total == unguarded total, bitwise)"],
     "audit_criteria": [],
     "estimates_inferred": {
       "fixed_coordinate_record_s": "40-60 (M5b walls 40-62 s with 20 calls and a 10 s window; H0 scan and weight records longer)",
       "rung1_run_s": "~345 (Gate 5 legacy/O1 dynesty rung 1 soft@10: 344.9 / 343.7 s total)",
       "rung3_run_s": "~830 (Gate 5 legacy dynesty rung 3 soft@10: 826 s)",
       "recommended_total_gpu_h": "about 3.4 (curves ~0.3, inference ~2.9, posterior means ~0.1); upper bound ~19 h if every run reaches the 3600 s wall",
       "disk_gb": "~5 (cold caches ~0.1 GB per GPU process, weight npz ~0.2 GB)"},
    }
    spec["audit_criteria"] = [
      {"id": "C1", "gate": "G1", "criterion": "Every fixed-coordinate record: status ok, rc 0; resolved guard and cap = requested; package = expected (legacy c042527 digest match; O1 f825906, clean); input sha256 = spec.inputs; coordinate sha256 = spec.coordinates; cold cache; the only accepted gap is 'n_calls=3 < 20'."},
      {"id": "C2", "gate": "G1", "criterion": "gs_guard.py validate passes on every new record: recomputed selection correction vs recorded <= 1e-12 relative; total = sum ln Z_i + correction <= 1e-12; threshold bitwise; hard verdict == total finite."},
      {"id": "C3", "gate": "G1", "criterion": "Reproduction: guard-independent fields (log mu, N_eff, sigma2_PE, per-event terms) of the new records bitwise equal to the campaign records of the same code, cell and coordinates (M5b legacy, Gate 1 M2 legacy, Gate 4 O1). A difference is reported with its max relative size; it does not block (block settings differ: none vs default/auto-single-pass)."},
      {"id": "C4", "gate": "G1", "criterion": "Separability: records sharing a selection file have bitwise-equal N_eff and log mu; records sharing a PE file have bitwise-equal PE terms. Composed cells are used only if every available pair passes; otherwise the missing cells are measured (switch Q1 to C)."},
      {"id": "C5", "gate": "G1", "criterion": "Fixed-coordinate code parity: compare_records.py core (O1) vs legacy per cell at rtol 1e-12, atol 0: pass, masks equal, guard verdicts and total finiteness equal."},
      {"id": "C6", "gate": "G1", "criterion": "Repeat consistency: every record's repeat coordinate bitwise equal to its first coordinate."},
      {"id": "C7", "gate": "G1", "criterion": "Recomputation pre-check P0.5 passes on the 30 existing M5b records (verified at design time: max 2.5e-16)."},
      {"id": "C8", "gate": "G2", "criterion": "Every inference run: status ok (converged) or budget-capped with the stop reason recorded, or sampler_error with preflight_abort for a hard cap (an outcome, not a failure); resolved guard/cap = requested; no timeout; cold cache; exactly one GPU job at a time (gpu_run.sh windows do not overlap)."},
      {"id": "C9", "gate": "G2", "criterion": "Legacy vs core (O1) per cap: under Q8-A the pair is a deterministic replica (compare_progress) and, when both converge, logZ and posterior samples are bit-identical; under Q8-B, posterior means within 0.1 posterior sigma and logZ within 1 combined error."},
      {"id": "C10", "gate": "G2", "criterion": "Cross-cap tables complete per rung and code: posterior mean, std, 16/50/84 % quantiles, logZ +- error, evaluations, stop reason; shifts relative to soft@10 in posterior sigma and in MC error, KS D."},
      {"id": "C11", "gate": "G2", "criterion": "Hard caps: dead points at dynesty's -1e300 floor counted (initial live points in the -inf region); under Q6-A the non-finite sampling count >= that floor count, and preflight counts agree with run.log."},
      {"id": "C12", "gate": "G2", "criterion": "Posterior means (Q7): the posterior-mean records pass C1, C2, C5, C6; each soft run's penalty at its own cap reported in nats and as a share of the total."},
      {"id": "C13", "gate": "G1", "criterion": "Injection count: N_eff vs detected count per selection file, T(cap) per PE file, linear extrapolation with the assumption stated; under Q4-B/C the numpy N_eff at stride offset 0 equals the stride10/stride100 records' N_eff within 1e-12."},
      {"id": "C14", "gate": "all", "criterion": "No production guard recommendation appears in any study output; the results report states evidence and options only."},
      {"id": "C15", "gate": "all", "criterion": "No XLA flags in any record's env; every GPU process has a gpu_run.sh smi log with lock acquired/released stamps."},
    ]
    counts = {}
    sel = spec["selected"]

    def on(w):
        return all(sel[k] in v for k, v in w.items())
    counts["curve_records_selected"] = sum(on(r["when"]) for r in records if r["phase"] == "P1")
    counts["inference_runs_selected"] = sum(on(r["when"]) for r in runs)
    counts["postmean_records_selected"] = sum(on(r["when"]) for r in records if r["phase"] == "P6")
    counts["curve_records_all_options"] = sum(1 for r in records if r["phase"] == "P1")
    spec["counts_at_selected"] = counts
    with open(f"{GS}/spec.json", "w") as f:
        json.dump(spec, f, indent=1)
        f.write("\n")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
