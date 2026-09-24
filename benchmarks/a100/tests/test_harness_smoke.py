"""Smoke test of the fixed-coordinate harness on core's tiny gwcat fixtures.

Runs both implementations (separate interpreters: both install ``darksirens``)
on ``darksirens-core/tools/make_gw_fixtures.py`` output (2 events x 3 samples,
5 injections, gwcat 2.1 chieff pair), for every ordinary plan, legacy with its
factory kernel and core in both jit modes, then asserts the record schema,
the harness invariants and legacy-vs-core parity at rtol 1e-12, atol 0.

The fixture has 5 injections for 2 events, so the selection guard
(N_eff <= 5 N_obs) makes every total log-likelihood -inf; the parity of the
finite diagnostics (per-event log evidence and variance, log_mu, N_eff,
guard threshold) and of the -inf verdicts is what this test exercises.

Configuration (environment):
  BENCH_LEGACY_PYTHON  interpreter with the legacy package (default: the campaign's
                       legacy311_cpu env on Hildafs)
  BENCH_CORE_PYTHON    interpreter with darksirens-core (default: the review venv)
  BENCH_CORE_REPO      darksirens-core checkout providing tools/make_gw_fixtures.py
  BENCH_SMOKE_PLANS    comma-separated subset of plans (default: the four ordinary plans)
Run with JAX_PLATFORMS=cpu; the subprocesses force it.
"""

from __future__ import annotations

import concurrent.futures as cf
import copy
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path.insert(0, BENCH)

import compare_records  # noqa: E402
import plans  # noqa: E402

_LOCAL = "/hildafs/projects/phy230014p/magana/darksirens_benchmark_local"
LEGACY_PY = os.environ.get("BENCH_LEGACY_PYTHON", f"{_LOCAL}/envs/legacy311_cpu/bin/python")
CORE_PY = os.environ.get(
    "BENCH_CORE_PYTHON",
    "/hildafs/home/magana/.claude/projects/-hildafs-projects-phy230014p-magana-darksirens-core/"
    "review-state/venv/bin/python")
CORE_REPO = os.environ.get("BENCH_CORE_REPO", "/hildafs/projects/phy230014p/magana/darksirens-core")
PLANS = [p for p in os.environ.get("BENCH_SMOKE_PLANS", ",".join(plans.ORDINARY_PLANS)).split(",") if p]
SEED = 20260924

REQUIRED_TOP = ("schema", "status", "label", "implementation", "command_line", "package", "env",
                "device", "inputs", "plan", "config", "dims", "coords", "timing", "jit_evidence",
                "values", "repeat_consistency", "plan_assertions", "diagnostics_provenance", "gaps")
REQUIRED_TIMING = ("t_load_s", "t_build_s", "t_transfer_sync_s", "t_first_call_s", "warm",
                   "compile", "memory", "peak_host_rss_bytes", "phase_clock")
REQUIRED_PER_COORD = ("total_logL", "diag_total_logL", "event_log_evidence", "event_mc_variance",
                      "log_mu", "n_eff", "selection_log_correction", "sigma2_lnL",
                      "guard_threshold", "guard_pass", "masks", "decoded_full")


def _need(path):
    if not os.path.exists(path):
        pytest.skip(f"not available: {path}")


def _env():
    env = dict(os.environ)
    env["JAX_PLATFORMS"] = "cpu"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    return env


def _run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, env=_env(), capture_output=True, text=True, timeout=3600)
    return {"cmd": cmd, "rc": r.returncode, "stdout": r.stdout[-4000:], "stderr": r.stderr[-6000:]}


@pytest.fixture(scope="session")
def smoke(tmp_path_factory):
    for p in (LEGACY_PY, CORE_PY, os.path.join(CORE_REPO, "tools", "make_gw_fixtures.py")):
        _need(p)
    work = str(tmp_path_factory.mktemp("bench_smoke"))
    fx = os.path.join(work, "fixtures")
    r = _run([CORE_PY, os.path.join(CORE_REPO, "tools", "make_gw_fixtures.py"), fx], work)
    assert r["rc"] == 0, r
    pe, sel = os.path.join(fx, "pe_chieff.h5"), os.path.join(fx, "sel_chieff.h5")
    jobs = {}
    for plan in PLANS:
        coords = os.path.join(work, f"coords_{plan}.json")
        r = _run([sys.executable, os.path.join(BENCH, "make_coords.py"), "--plan", plan,
                  "--seed", str(SEED), "--n", "8", "--out", coords], work)
        assert r["rc"] == 0, r
        for impl, jit, py in (("legacy", "whole", LEGACY_PY), ("core", "whole", CORE_PY),
                              ("core", "asis", CORE_PY)):
            out = os.path.join(work, f"{plan}_{impl}_{jit}.json")
            cmd = [py, os.path.join(BENCH, "bench_fixed_theta.py"), "--impl", impl, "--pe", pe,
                   "--sel", sel, "--plan", plan, "--coords", coords, "--out", out,
                   "--n-calls", "20", "--warmup", "3", "--jit", jit, "--sel-batch", "none",
                   "--pe-block", "none", "--seed", str(SEED), "--label",
                   f"smoke_{plan}_{impl}_{jit}", "--device", "cpu"]
            jobs[(plan, impl, jit)] = (cmd, out)
    results = {}
    with cf.ThreadPoolExecutor(max_workers=min(len(jobs), max(2, (os.cpu_count() or 4) // 2))) as ex:
        futs = {ex.submit(_run, cmd, work): key for key, (cmd, _out) in jobs.items()}
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()
    records = {}
    for key, (_cmd, out) in jobs.items():
        assert results[key]["rc"] == 0, results[key]
        with open(out) as f:
            records[key] = json.load(f)
            records[key]["_path"] = out
    return {"work": work, "records": records}


@pytest.mark.parametrize("plan", PLANS)
@pytest.mark.parametrize("impl,jit", [("legacy", "whole"), ("core", "whole"), ("core", "asis")])
def test_record_schema_and_invariants(smoke, plan, impl, jit):
    rec = smoke["records"][(plan, impl, jit)]
    for k in REQUIRED_TOP:
        assert k in rec, k
    for k in REQUIRED_TIMING:
        assert k in rec["timing"], k
    assert rec["status"] == "ok"
    assert rec["plan_assertions"]["registry"] == "ok"
    assert rec["plan_assertions"]["decode"] == "ok"
    assert rec["implementation"] == impl
    assert rec["device"]["backend"] == "cpu" and rec["device"]["x64"] is True
    assert rec["coords"]["names"] == plans.resolve_plan(plan)["sampled"]
    n = len(rec["coords"]["values_hex"])
    assert n == 9 and rec["coords"]["values_hex"][0] == rec["coords"]["values_hex"][-1]
    assert len(rec["values"]["per_coord"]) == n
    for pc in rec["values"]["per_coord"]:
        for k in REQUIRED_PER_COORD:
            assert k in pc, k
    assert rec["mask_order"]["pe_dL_equals_file"] is True
    assert rec["mask_order"]["sel_dL_equals_file"] is True
    assert rec["repeat_consistency"]["bitwise"] is True
    assert rec["repeat_consistency"]["timed_loop_bitwise_consistent"] is True
    assert rec["timing"]["warm"]["n"] == 20
    assert rec["timing"]["compile"]["hook_selftest"]["ok"] is True
    assert rec["timing"]["compile"]["first_call"]["requests"] >= 1
    if (impl, jit) != ("core", "asis"):
        assert rec["timing"]["compile"]["timed_loop"]["requests"] == 0
        assert rec["jit_evidence"]["jaxpr"]["embeds_data_literal"] is False
    if impl == "legacy":
        assert rec["package"]["known_digest_match"]["sha"].startswith("c042527")
    else:
        assert rec["package"]["file"].startswith(CORE_REPO) or rec["package"]["known_digest_match"]


@pytest.mark.parametrize("plan", PLANS)
@pytest.mark.parametrize("jit", ["whole", "asis"])
def test_legacy_core_parity_1e12(smoke, plan, jit):
    A = smoke["records"][(plan, "legacy", "whole")]
    B = smoke["records"][(plan, "core", jit)]
    s = compare_records.compare(A, B, rtol=1e-12, atol=0.0)
    assert s["status"] == "compared", s.get("refusal_reasons")
    bad = {f: v for f, v in s["fields"].items() if not v["pass"]}
    assert not bad, bad
    assert s["masks"]["all_equal"] is True
    assert s["verdict"]["overall_pass"] is True
    # decoded parameter vectors are the plan identity: must be bit-identical
    assert s["fields"]["decoded_full_parameter_vector"]["bitwise"] is True


def test_compare_refuses_mismatched_experiments(smoke):
    plan = PLANS[0]
    A = smoke["records"][(plan, "legacy", "whole")]
    B = copy.deepcopy(smoke["records"][(plan, "core", "whole")])
    B["coords"]["values_hex"][1][0] = float.fromhex(B["coords"]["values_hex"][1][0]).__add__(1.0).hex()
    s = compare_records.compare(A, B, 1e-12, 0.0)
    assert s["status"] == "refused" and any("coordinate values" in r for r in s["refusal_reasons"])
    B = copy.deepcopy(smoke["records"][(plan, "core", "whole")])
    B["inputs"]["pe"]["sha256"] = "0" * 64
    s = compare_records.compare(A, B, 1e-12, 0.0)
    assert s["status"] == "refused" and any("input pe" in r for r in s["refusal_reasons"])
    for key, value in (("max_likelihood_variance", 2.0), ("selection_neff_soft_guard", True)):
        B = copy.deepcopy(smoke["records"][(plan, "core", "whole")])
        B["config"][key] = value
        s = compare_records.compare(A, B, 1e-12, 0.0)
        assert s["status"] == "refused" and any(key in r for r in s["refusal_reasons"])


@pytest.mark.parametrize("plan", PLANS)
@pytest.mark.parametrize("impl,jit", [("legacy", "whole"), ("core", "whole"), ("core", "asis")])
def test_likelihood_settings_are_the_dynesty_defaults(smoke, plan, impl, jit):
    cfg = smoke["records"][(plan, impl, jit)]["config"]
    assert cfg["max_likelihood_variance"] == 1.0
    assert cfg["selection_neff_soft_guard"] is False
