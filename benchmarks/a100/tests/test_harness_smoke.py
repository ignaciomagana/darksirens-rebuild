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
  BENCH_DARK_FIXTURE   dark-siren mock fixture directory with galaxy_density.json (default:
                       the campaign's fixture T on Hildafs); the dark tests skip without it
  BENCH_SMOKE_DARK_PLANS  comma-separated subset of dark plans (default: all six)
Run with JAX_PLATFORMS=cpu; the subprocesses force it.

The dark-siren part runs every dark plan on fixture T (8 events x 64 samples,
19,943 injections, nside 16) for legacy, core whole and core asis, with 5 timed
calls (timing is not what it checks), and asserts the record schema, the fixture
pre-flight, the catalog-side diagnostics and legacy-vs-core parity at rtol 1e-12
including the catalog structure, the empty-row sets and the catalog-side values.
"""

from __future__ import annotations

import concurrent.futures as cf
import copy
import json
import math
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
DARK_FIXTURE = os.environ.get("BENCH_DARK_FIXTURE", f"{_LOCAL}/mock/fixtures/T")
DARK_PLANS = [p for p in os.environ.get("BENCH_SMOKE_DARK_PLANS", ",".join(plans.DARK_PLANS)).split(",")
              if p]
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


GUARD_VARIANTS = (("soft", "1.0"), ("hard", "10"))


@pytest.fixture(scope="session")
def guard_smoke(smoke):
    """--guard / --max-variance in both adapters: soft at cap 1.0 and hard at cap 10."""
    work, plan = smoke["work"], PLANS[0]
    base = smoke["records"][(plan, "legacy", "whole")]
    pe, sel = base["inputs"]["pe"]["path"], base["inputs"]["sel"]["path"]
    coords = os.path.join(work, f"coords_{plan}.json")
    jobs = {}
    for guard, cap in GUARD_VARIANTS:
        for impl, py in (("legacy", LEGACY_PY), ("core", CORE_PY)):
            out = os.path.join(work, f"guard_{guard}_{cap}_{plan}_{impl}.json")
            cmd = [py, os.path.join(BENCH, "bench_fixed_theta.py"), "--impl", impl, "--pe", pe,
                   "--sel", sel, "--plan", plan, "--coords", coords, "--out", out,
                   "--n-calls", "5", "--warmup", "1", "--jit", "whole", "--sel-batch", "none",
                   "--pe-block", "none", "--seed", str(SEED), "--label",
                   f"guard_{guard}_{impl}", "--device", "cpu", "--guard", guard,
                   "--max-variance", cap]
            jobs[(guard, impl)] = (cmd, out)
    records = {}
    for key, (cmd, out) in jobs.items():
        r = _run(cmd, work)
        assert r["rc"] == 0, r
        with open(out) as f:
            records[key] = json.load(f)
            records[key]["_path"] = out
    return records


@pytest.mark.parametrize("guard,cap", GUARD_VARIANTS)
def test_guard_variants_recorded_and_in_parity(guard_smoke, guard, cap):
    for impl in ("legacy", "core"):
        cfg = guard_smoke[(guard, impl)]["config"]
        assert cfg["selection_neff_soft_guard"] is (guard == "soft")
        assert cfg["max_likelihood_variance"] == float(cap)
        assert cfg["guard"]["mode"] == guard and cfg["guard"]["cap"] == float(cap)
        assert cfg["guard"]["requested_mode"] == guard
    leg = guard_smoke[(guard, "legacy")]["config"]["legacy_cli_args"]
    assert leg[leg.index("--selection_neff_guard") + 1] == guard
    assert float(leg[leg.index("--max_likelihood_variance") + 1]) == float(cap)
    s = compare_records.compare(guard_smoke[(guard, "legacy")], guard_smoke[(guard, "core")],
                                rtol=1e-12, atol=0.0)
    assert s["status"] == "compared", s.get("refusal_reasons")
    assert s["verdict"]["overall_pass"] is True


def test_compare_refuses_different_guard_settings(guard_smoke, smoke):
    soft, hard = guard_smoke[("soft", "legacy")], guard_smoke[("hard", "core")]
    s = compare_records.compare(soft, hard, 1e-12, 0.0)
    assert s["status"] == "refused"
    assert any("selection_neff_soft_guard" in r for r in s["refusal_reasons"])
    assert any("max_likelihood_variance" in r for r in s["refusal_reasons"])
    default = smoke["records"][(PLANS[0], "core", "whole")]
    s = compare_records.compare(default, soft, 1e-12, 0.0)
    assert s["status"] == "refused"
    assert any("selection_neff_soft_guard" in r for r in s["refusal_reasons"])


# ---------------------------------------------------------------------------
# Dark sirens on the campaign's mock fixture T
# ---------------------------------------------------------------------------
def _dark_inputs(fixture_dir):
    with open(os.path.join(fixture_dir, "galaxy_density.json")) as f:
        sc = json.load(f)
    hi = sc["harness_inputs"]
    return (os.path.join(fixture_dir, hi["pe"]), os.path.join(fixture_dir, hi["sel"]),
            os.path.join(fixture_dir, hi["catalog"]), sc)


@pytest.fixture(scope="session")
def dark_smoke(tmp_path_factory):
    for p in (LEGACY_PY, CORE_PY, os.path.join(DARK_FIXTURE, "galaxy_density.json")):
        _need(p)
    pe, sel, cat, sc = _dark_inputs(DARK_FIXTURE)
    work = str(tmp_path_factory.mktemp("bench_dark_smoke"))
    jobs = {}
    for plan in DARK_PLANS:
        coords = os.path.join(work, f"coords_{plan}.json")
        r = _run([sys.executable, os.path.join(BENCH, "make_coords.py"), "--plan", plan,
                  "--seed", str(SEED), "--n", "4", "--out", coords], work)
        assert r["rc"] == 0, r
        for impl, jit, py in (("legacy", "whole", LEGACY_PY), ("core", "whole", CORE_PY),
                              ("core", "asis", CORE_PY)):
            out = os.path.join(work, f"{plan}_{impl}_{jit}.json")
            cmd = [py, os.path.join(BENCH, "bench_fixed_theta.py"), "--impl", impl, "--pe", pe,
                   "--sel", sel, "--catalog", cat, "--plan", plan, "--coords", coords,
                   "--out", out, "--n-calls", "5", "--warmup", "1", "--jit", jit,
                   "--sel-batch", "none", "--pe-block", "none", "--seed", str(SEED),
                   "--label", f"dark_smoke_{plan}_{impl}_{jit}", "--device", "cpu"]
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
    return {"work": work, "records": records, "sidecar": sc, "inputs": (pe, sel, cat)}


@pytest.mark.parametrize("plan", DARK_PLANS)
@pytest.mark.parametrize("impl,jit", [("legacy", "whole"), ("core", "whole"), ("core", "asis")])
def test_dark_record_schema_and_invariants(dark_smoke, plan, impl, jit):
    rec = dark_smoke["records"][(plan, impl, jit)]
    for k in REQUIRED_TOP + ("fixture_preflight", "catalog_arrays"):
        assert k in rec, k
    assert rec["status"] == "ok"
    assert rec["plan"]["universe"] == "dark"
    assert rec["plan_assertions"]["registry"] == "ok"
    assert rec["plan_assertions"]["decode"] == "ok"
    assert rec["fixture_preflight"]["status"] == "ok"
    assert rec["fixture_preflight"]["log10n0"] == -3.0
    assert all(rec["fixture_preflight"]["inside_prior"].values())
    cat = rec["dims"]["catalog"]
    assert cat["present"] is True and cat["nside"] == dark_smoke["sidecar"]["nside"]
    for k in ("n_rows", "n_max", "n_rows_occupied", "n_rows_empty", "z_depth", "union_pixels_sha256"):
        assert k in cat, k
    npz = os.path.join(os.path.dirname(rec["_path"]), rec["catalog_arrays"]["file"])
    assert os.path.isfile(npz)
    assert compare_records.bc.sha256_file(npz) == rec["catalog_arrays"]["sha256"]
    for pc in rec["values"]["per_coord"]:
        for k in REQUIRED_PER_COORD + ("catalog",):
            assert k in pc, k
        assert len(pc["catalog"]["event_log_evidence_catalog_branch"]["hex"]) == rec["dims"]["n_events"]
    assert rec["mask_order"]["pe_dL_equals_file"] is True
    assert rec["mask_order"]["sel_dL_equals_file"] is True
    assert rec["repeat_consistency"]["bitwise"] is True
    assert rec["repeat_consistency"]["timed_loop_bitwise_consistent"] is True
    assert rec["timing"]["compile"]["hook_selftest"]["ok"] is True
    # decoded vector: n0 = 10**log10n0 in the survey slot
    names = rec["values"]["per_coord"][0]["decoded_full"]["names"]
    assert names[-3:] == ["n0", "delta", "sigma_kde"]
    if rec["plan"]["sample_survey"] == "none":
        n0 = float.fromhex(rec["values"]["per_coord"][0]["decoded_full"]["hex"][-3])
        assert abs(n0 - 1.0e-3) <= 1e-18
    if (impl, jit) != ("core", "asis"):
        assert rec["timing"]["compile"]["timed_loop"]["requests"] == 0
        assert rec["jit_evidence"]["jaxpr"]["embeds_data_literal"] is False
    if impl == "legacy":
        assert rec["package"]["known_digest_match"]["sha"].startswith("c042527")
        res = rec["config"]["dark_settings"]["resolved"]
        assert res["catalog_sky_weighting"] == "conditional"
        assert res["kde_window_resolved"] is None and res["frozen_redshift_prior"] is False
        assert res["c_mode"] == "per_pixel" and res["use_LSS"] is False
        assert res["drop_full_catalog"] is False
        assert all(pc["kernel_vs_diag_total"]["bitwise"] for pc in rec["values"]["per_coord"])
    else:
        assert rec["config"]["universe_model"].startswith("dark_sirens")


@pytest.mark.parametrize("plan", DARK_PLANS)
@pytest.mark.parametrize("jit", ["whole", "asis"])
def test_dark_legacy_core_parity_1e12(dark_smoke, plan, jit):
    A = dark_smoke["records"][(plan, "legacy", "whole")]
    B = dark_smoke["records"][(plan, "core", jit)]
    s = compare_records.compare(A, B, rtol=1e-12, atol=0.0)
    assert s["status"] == "compared", s.get("refusal_reasons")
    bad = {f: v for f, v in s["fields"].items() if not v["pass"]}
    assert not bad, bad
    assert s["masks"]["all_equal"] is True
    assert s["catalog"]["structure_equal"] is True
    assert s["catalog"]["row_empty_equal"] is True
    assert s["catalog"]["arrays_compared"] is True
    assert s["verdict"]["catalog_values_pass"] is True, {
        f: v["max_rel"] for f, v in s["catalog_fields"].items() if not v["pass"]}
    assert s["verdict"]["overall_pass"] is True
    assert s["fields"]["decoded_full_parameter_vector"]["bitwise"] is True


def test_dark_compare_refuses_other_catalog(dark_smoke):
    plan = DARK_PLANS[0]
    A = dark_smoke["records"][(plan, "legacy", "whole")]
    B = copy.deepcopy(dark_smoke["records"][(plan, "core", "whole")])
    B["inputs"]["catalog"]["sha256"] = "0" * 64
    s = compare_records.compare(A, B, 1e-12, 0.0)
    assert s["status"] == "refused" and any("catalog" in r for r in s["refusal_reasons"])
    B = copy.deepcopy(dark_smoke["records"][(plan, "core", "whole")])
    B["plan"]["universe"] = "spectral"
    s = compare_records.compare(A, B, 1e-12, 0.0)
    assert s["status"] == "refused"


def _bench_rc(py, args, work):
    return _run([py, os.path.join(BENCH, "bench_fixed_theta.py")] + args, work)


def test_dark_preflight_refusals(dark_smoke, tmp_path):
    pe, sel, cat, sc = dark_smoke["inputs"] + (dark_smoke["sidecar"],)
    work = str(tmp_path)
    coords = os.path.join(work, "coords.json")
    r = _run([sys.executable, os.path.join(BENCH, "make_coords.py"), "--plan", "dark_H0",
              "--seed", str(SEED), "--n", "2", "--out", coords], work)
    assert r["rc"] == 0, r
    base = ["--impl", "core", "--pe", pe, "--sel", sel, "--plan", "dark_H0", "--coords", coords,
            "--out", os.path.join(work, "x.json"), "--jit", "whole", "--sel-batch", "none",
            "--pe-block", "none", "--seed", str(SEED), "--label", "refuse", "--device", "cpu"]
    # 1. dark plan without a catalog
    r = _bench_rc(CORE_PY, base, work)
    assert r["rc"] == 2 and "needs --catalog" in r["stderr"], r
    # 2. a fixture whose recorded density is outside the log10n0 prior (the PR-6a 5e-5)
    fx = os.path.join(work, "fixture_out_of_prior")
    os.makedirs(fx)
    for name in (sc["harness_inputs"]["pe"], sc["harness_inputs"]["sel"], sc["harness_inputs"]["catalog"]):
        os.symlink(os.path.join(DARK_FIXTURE, name), os.path.join(fx, name))
    bad = dict(sc, n0=5e-5, n0_arg="5e-5", log10n0=math.log10(5e-5),
               log10n0_hex=math.log10(5e-5).hex())
    with open(os.path.join(fx, "galaxy_density.json"), "w") as f:
        json.dump(bad, f)
    args = base[:]
    args[args.index("--pe") + 1] = os.path.join(fx, sc["harness_inputs"]["pe"])
    args[args.index("--sel") + 1] = os.path.join(fx, sc["harness_inputs"]["sel"])
    r = _bench_rc(CORE_PY, args + ["--catalog", os.path.join(fx, sc["harness_inputs"]["catalog"])], work)
    assert r["rc"] == 2 and "FIXTURE PREFLIGHT REFUSED" in r["stderr"], r
    assert "outside the legacy log10n0 prior" in r["stderr"] and "outside the core log10n0 prior" in r["stderr"]
    # 3. inputs that are not the sidecar's bytes (the fixture's PE swapped for its selection file)
    fx2 = os.path.join(work, "fixture_wrong_bytes")
    os.makedirs(fx2)
    for name in (sc["harness_inputs"]["sel"], sc["harness_inputs"]["catalog"], "galaxy_density.json"):
        os.symlink(os.path.join(DARK_FIXTURE, name), os.path.join(fx2, name))
    os.symlink(os.path.join(DARK_FIXTURE, sc["harness_inputs"]["sel"]),
               os.path.join(fx2, sc["harness_inputs"]["pe"]))
    args = base[:]
    args[args.index("--pe") + 1] = os.path.join(fx2, sc["harness_inputs"]["pe"])
    r = _bench_rc(CORE_PY, args + ["--catalog", os.path.join(fx2, sc["harness_inputs"]["catalog"])], work)
    assert r["rc"] == 2 and "is not the fixture's" in r["stderr"], r
    # 4. a catalog-free plan refuses --catalog
    sp_coords = os.path.join(work, "coords_sp.json")
    r = _run([sys.executable, os.path.join(BENCH, "make_coords.py"), "--plan", "spectral_H0",
              "--seed", str(SEED), "--n", "2", "--out", sp_coords], work)
    args = base[:]
    args[args.index("--plan") + 1] = "spectral_H0"
    args[args.index("--coords") + 1] = sp_coords
    r = _bench_rc(CORE_PY, args + ["--catalog", cat], work)
    assert r["rc"] == 2 and "catalog-free" in r["stderr"], r
    # 5. an out-of-prior FIXED survey override needs the explicit flag (log10n0 against both
    #    log10n0 priors, delta / sigma_kde against the shared survey bounds)
    for ovr in ({"log10n0": math.log10(5e-5)}, {"delta": 5.0}, {"sigma_kde": -0.01}):
        r = _bench_rc(CORE_PY, base + ["--catalog", cat, "--survey-fixed-override", json.dumps(ovr)],
                      work)
        assert r["rc"] == 2 and "allow-out-of-prior-fixed-survey" in r["stderr"], (ovr, r)
    # 6. a density LABEL that the data do not carry: the fixture's own products with a
    #    sidecar whose zmax (hence V_c) is wrong, so N_complete / V_c != n0
    fx3 = os.path.join(work, "fixture_mislabelled_density")
    os.makedirs(fx3)
    for name in (sc["harness_inputs"]["pe"], sc["harness_inputs"]["sel"], sc["harness_inputs"]["catalog"],
                 "mock_galaxy_catalog_complete.h5"):
        os.symlink(os.path.join(DARK_FIXTURE, name), os.path.join(fx3, name))
    with open(os.path.join(fx3, "galaxy_density.json"), "w") as f:
        json.dump(dict(sc, zmax=0.07), f)
    args = base[:]
    args[args.index("--pe") + 1] = os.path.join(fx3, sc["harness_inputs"]["pe"])
    args[args.index("--sel") + 1] = os.path.join(fx3, sc["harness_inputs"]["sel"])
    r = _bench_rc(CORE_PY, args + ["--catalog", os.path.join(fx3, sc["harness_inputs"]["catalog"])], work)
    assert r["rc"] == 2 and "the data imply n0" in r["stderr"], r


# ---------------------------------------------------------------------------
# Gate 3b memory knobs: legacy --row-chunk, --mem-fraction, --steady-window, npz digest
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def knobs_smoke(tmp_path_factory):
    for p in (LEGACY_PY, CORE_PY, os.path.join(DARK_FIXTURE, "galaxy_density.json")):
        _need(p)
    pe, sel, cat, _sc = _dark_inputs(DARK_FIXTURE)
    work = str(tmp_path_factory.mktemp("bench_knobs_smoke"))
    plan = "dark_full"
    coords = os.path.join(work, f"coords_{plan}.json")
    r = _run([sys.executable, os.path.join(BENCH, "make_coords.py"), "--plan", plan,
              "--seed", str(SEED), "--n", "4", "--out", coords], work)
    assert r["rc"] == 0, r

    def cmd(impl, py, out, extra):
        return [py, os.path.join(BENCH, "bench_fixed_theta.py"), "--impl", impl, "--pe", pe,
                "--sel", sel, "--catalog", cat, "--plan", plan, "--coords", coords, "--out", out,
                "--n-calls", "6", "--warmup", "1", "--jit", "whole", "--sel-batch", "none",
                "--pe-block", "none", "--seed", str(SEED), "--label", os.path.basename(out),
                "--device", "cpu", "--steady-window", "4", "--catalog-npz", "digest"] + extra

    recs, runs = {}, {}
    jobs = {"legacy": ("legacy", LEGACY_PY, ["--row-chunk", "64", "--mem-fraction", "0.5",
                                              "--slow-call-s", "1e-9", "--slow-n-calls", "5"]),
            "core": ("core", CORE_PY, ["--mem-fraction", "0.5"])}
    for key, (impl, py, extra) in jobs.items():
        out = os.path.join(work, f"knobs_{key}.json")
        runs[key] = _run(cmd(impl, py, out, extra), work)
        assert runs[key]["rc"] == 0, runs[key]
        with open(out) as f:
            recs[key] = json.load(f)
            recs[key]["_path"] = out
    refused = _run(cmd("core", CORE_PY, os.path.join(work, "knobs_refused.json"),
                       ["--row-chunk", "512"]), work)
    return {"records": recs, "refused": refused}


def test_memory_knobs_recorded_and_in_parity(knobs_smoke):
    L, C = knobs_smoke["records"]["legacy"], knobs_smoke["records"]["core"]
    mk = L["config"]["memory_knobs"]
    assert mk["row_chunk"]["legacy_cli_value"] == "64"
    assert mk["row_chunk"]["module_mode"] == 64 and mk["row_chunk"]["effective_for_catalog"] == 64
    args = L["config"]["legacy_cli_args"]
    assert args[args.index("--row_chunk") + 1] == "64"
    for R in (L, C):
        mf = R["config"]["memory_knobs"]["mem_fraction"]
        assert mf["effective"] == 0.5 and mf["allocator"] == "non-default"
        assert R["env"]["env_vars"]["XLA_PYTHON_CLIENT_MEM_FRACTION"] == "0.5"
        assert "catalog_arrays" not in R and R["catalog_arrays_digest"]
        assert R["timing"]["warm"]["steady"]["window"] == 4
    assert C["config"]["memory_knobs"]["row_chunk"]["module_mode"].startswith("auto")
    # slow-call rule: legacy's warm-up exceeded 1e-9 s -> 5 timed calls
    assert L["config"]["slow_call_rule"]["triggered"] is True and L["config"]["n_calls"] == 5
    assert L["timing"]["warm"]["n"] == 5 and C["timing"]["warm"]["n"] == 6
    s = compare_records.compare(L, C, rtol=1e-12, atol=0.0)
    assert s["status"] == "compared", s.get("refusal_reasons")
    assert s["verdict"]["overall_pass"] is True
    assert knobs_smoke["refused"]["rc"] == 2
    assert "--row-chunk" in knobs_smoke["refused"]["stderr"]
