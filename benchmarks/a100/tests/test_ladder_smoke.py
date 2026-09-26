"""Smoke test of the Gate 5 inference-ladder driver (infer_ladder.py, compare_posteriors.py).

CPU only, small: Product A ``first16_n1024`` + ``stride100``.

* unit checks (no JAX): every rung resolves to the Fable ladder (sampled / fixed sets,
  joint constraints), the legacy argument vector carries every matched setting;
* ``--describe`` for every rung in both implementations: the implementation's own
  parameter plan (labels, bounds, prior kinds, joint constraints) and the decoded full
  vector at the rung centre equal the rung definition bit for bit;
* rung 1 sampled with tinyns and dynesty in both implementations (nlive 20, dlogz 2):
  complete records, progress rows, evaluation counts, posterior files, and
  compare_posteriors.py accepting the pair (and refusing a cross-sampler pair unless asked);
* the sampler-error path: the hard guard with a variance cap (0.001) below the PE variance sum
  makes every draw -inf, and both codes abort in the nested-sampler preflight (exit 5,
  ``sampler_error.preflight_abort``).

Configuration (environment):
  BENCH_LEGACY_PYTHON  interpreter with the legacy package (default: legacy311_cpu on Hildafs)
  BENCH_CORE_PYTHON    interpreter with darksirens-core (default: the review venv)
  BENCH_PRODUCT_A_DIR  directory with A_pe_chieff_first16_n1024_v20.h5 and
                       A_sel_chieffref_o3o4ab_v20_stride100.h5 (default: $LOCAL/gwcat/exports)
"""

from __future__ import annotations

import concurrent.futures as cf
import json
import os
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path.insert(0, BENCH)

import compare_posteriors  # noqa: E402
import infer_ladder  # noqa: E402

_LOCAL = "/hildafs/projects/phy230014p/magana/darksirens_benchmark_local"
LEGACY_PY = os.environ.get("BENCH_LEGACY_PYTHON", f"{_LOCAL}/envs/legacy311_cpu/bin/python")
CORE_PY = os.environ.get(
    "BENCH_CORE_PYTHON",
    "/hildafs/home/magana/.claude/projects/-hildafs-projects-phy230014p-magana-darksirens-core/"
    "review-state/venv/bin/python")
DATA = os.environ.get("BENCH_PRODUCT_A_DIR", f"{_LOCAL}/gwcat/exports")
PE = os.path.join(DATA, "A_pe_chieff_first16_n1024_v20.h5")
SEL = os.path.join(DATA, "A_sel_chieffref_o3o4ab_v20_stride100.h5")
SEED = 20260924
PY = {"legacy": LEGACY_PY, "core": CORE_PY}
RUNGS = ("1", "2", "3", "4", "5", "5b")
REQUIRED_TOP = ("schema", "status", "label", "implementation", "command_line", "harness", "package",
                "sampler_backends", "env", "device", "inputs", "rung", "settings", "invocation",
                "timing", "compile", "plan", "first_call", "memory", "xla_cache", "gaps")
REQUIRED_OK = ("progress", "likelihood_calls", "result", "seeds")


def _need(path):
    if not os.path.exists(path):
        pytest.skip(f"not available: {path}")


def _env():
    env = dict(os.environ)
    env["JAX_PLATFORMS"] = "cpu"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    return env


def _ladder(impl, rung, sampler, out, *extra):
    cmd = [PY[impl], os.path.join(BENCH, "infer_ladder.py"), "--impl", impl, "--rung", rung,
           "--sampler", sampler, "--pe", PE, "--sel", SEL, "--nlive", "20", "--dlogz", "2.0",
           "--seed", str(SEED), "--out", out, "--device", "cpu", *extra]
    r = subprocess.run(cmd, cwd=os.path.dirname(out), env=_env(), capture_output=True, text=True,
                       timeout=3600)
    rec = None
    if os.path.isfile(os.path.join(out, "record.json")):
        with open(os.path.join(out, "record.json")) as f:
            rec = json.load(f)
    return {"cmd": cmd, "rc": r.returncode, "stdout": r.stdout[-3000:], "stderr": r.stderr[-4000:],
            "record": rec, "out": out}


# ---------------------------------------------------------------- unit (no JAX)
def test_rungs_resolve_to_the_ladder():
    n_sampled = {"1": 1, "2": 17, "3": 3, "4": 4, "5": 18, "5b": 13}
    for rid in RUNGS:
        r = infer_ladder.resolve_rung(rid)
        assert len(r["sampled"]) == n_sampled[rid], rid
        assert set(r["sampled"]).isdisjoint(r["fixed"]), rid
        assert set(r["sampled"]) | set(r["fixed"]) == set(r["full_order"]), rid
        assert ("H0" in r["sampled"]) == (rid in ("1", "4", "5", "5b")), rid
        if rid != "5b":
            assert r["population_model"] == "gwtc5_fiducial_bpl2peaks"
            assert r["population_preset"] == "gwtc5"
        else:
            assert r["population_model"] == "powerlaw+peak"
        if "H0" not in r["sampled"]:
            assert r["fixed"]["H0"] == 67.74
        assert r["fixed"]["Om0"] == 0.3075 and r["fixed"]["w0"] == -1.0 and r["fixed"]["wa"] == 0.0
    assert infer_ladder.resolve_rung("1")["core_population_fixed"] == "gwtc5"
    assert infer_ladder.resolve_rung("2")["expected_joint_constraints"] == [
        ["simplex", [9, 10]], ["conditional_upper", [12, 7]]]
    assert infer_ladder.resolve_rung("5")["expected_joint_constraints"] == [
        ["simplex", [10, 11]], ["conditional_upper", [13, 8]]]
    for rid in ("1", "3", "4", "5b"):
        assert infer_ladder.resolve_rung(rid)["expected_joint_constraints"] == []
    r3 = infer_ladder.resolve_rung("3")
    assert r3["sampled"] == r3["population_labels"][:3]


def test_legacy_argv_carries_every_matched_setting():
    s = {"sampler": "tinyns", "nlive": 1000, "dlogz": 0.1, "seed": SEED, "max_samples": 0,
         "tinyns_preset": "recommended", "sampler_preflight": "on", "prior_transform_dispatch": "auto",
         "sel_batch_size": "none", "pe_event_block": "none", "guard": "soft",
         "max_likelihood_variance": 1.0}
    for rid in RUNGS:
        r = infer_ladder.resolve_rung(rid)
        argv = infer_ladder.legacy_argv(r, "PE", "SEL", "SAVE", s)
        kv = dict(zip(argv[::2], argv[1::2]))
        assert kv["--checkpoint_interval"] == "off" and kv["--resume"] == "off"
        assert kv["--seed"] == str(SEED) and kv["--nlive"] == "1000" and float(kv["--dlogz"]) == 0.1
        assert kv["--max_samples"] == "0" and kv["--tinyns_preset"] == "recommended"
        assert kv["--sel_batch_size"] == "off" and kv["--pe_event_block"] == "off"
        assert kv["--selection_neff_guard"] == "soft" and float(kv["--max_likelihood_variance"]) == 1.0
        assert kv["--pop_model"] == r["population_model"]
        fixed = json.loads(kv.get("--fixed_parameter_values", "{}"))
        if r["sample_H0"]:
            assert json.loads(kv["--prior_overrides"]) == {"H0": [20.0, 140.0]}
            assert kv["--fix_de"] == "true" and fixed["Om0"] == 0.3075
        else:
            assert kv["--fix_cosmology"] == "true"
        if r["sample_population"] == "none":
            assert kv["--fix_population"] == "true"
        elif r["sample_population"] != "all":
            k = int(r["sample_population"])
            for lab in r["population_labels"][k:]:
                assert fixed[lab] == r["fixed"][lab]


# ---------------------------------------------------------------- integration
@pytest.fixture(scope="session")
def runs(tmp_path_factory):
    for p in (LEGACY_PY, CORE_PY, PE, SEL):
        _need(p)
    work = str(tmp_path_factory.mktemp("ladder_smoke"))
    jobs = {}
    for impl in ("legacy", "core"):
        for rid in RUNGS:
            jobs[("describe", impl, rid)] = (impl, rid, "dynesty",
                                             os.path.join(work, f"describe_{impl}_{rid}"), "--describe")
        for sampler in ("tinyns", "dynesty"):
            jobs[("run", impl, sampler)] = (impl, "1", sampler, os.path.join(work, f"run_{impl}_{sampler}"),
                                            "--cache-dir", os.path.join(work, f"cache_{impl}_{sampler}"),
                                            "--cache-mode", "cold")
        jobs[("abort", impl)] = (impl, "1", "tinyns", os.path.join(work, f"abort_{impl}"),
                                 "--guard", "hard", "--max-variance", "0.001")
    out = {}
    with cf.ThreadPoolExecutor(max_workers=min(len(jobs), max(2, (os.cpu_count() or 4) // 2))) as ex:
        futs = {ex.submit(_ladder, *args): key for key, args in jobs.items()}
        for fut in cf.as_completed(futs):
            out[futs[fut]] = fut.result()
    return work, out


def test_describe_every_rung_matches_both_codes(runs):
    _work, out = runs
    for impl in ("legacy", "core"):
        for rid in RUNGS:
            r = out[("describe", impl, rid)]
            assert r["rc"] == 0, r
            rec = r["record"]
            assert rec["status"] == "described"
            assert rec["plan"]["assertions"]["ok"], rec["plan"]["assertions"]
            assert rec["first_call"]["finite"], rec["first_call"]
    for rid in RUNGS:
        a = out[("describe", "legacy", rid)]["record"]["plan"]
        b = out[("describe", "core", rid)]["record"]["plan"]
        assert a["implementation_view"] == b["implementation_view"], rid
        assert a["decoded_full_at_centre_hex"] == b["decoded_full_at_centre_hex"], rid


def test_sampled_runs_complete(runs):
    _work, out = runs
    for impl in ("legacy", "core"):
        for sampler in ("tinyns", "dynesty"):
            r = out[("run", impl, sampler)]
            assert r["rc"] == 0, r
            rec = r["record"]
            for k in REQUIRED_TOP + REQUIRED_OK:
                assert k in rec, (impl, sampler, k)
            assert rec["schema"] == infer_ladder.SCHEMA and rec["status"] == "ok"
            assert rec["settings"]["resolved"]["checkpoint_plan"] == "off"
            assert rec["settings"]["resolved"]["seed"] == SEED
            assert rec["settings"]["resolved"]["selection_neff_soft_guard"] is True
            lc = rec["likelihood_calls"]
            assert lc["n_like_evals"] and lc["n_like_evals"] > 20
            assert lc["preflight_eager_calls"] and lc["preflight_eager_calls"] >= 1
            assert rec["progress"]["n_main_rows"] >= 1
            assert rec["timing"]["t_sampling_s"] > 0 and rec["timing"]["t_first_call_s"] > 0
            assert rec["xla_cache"]["files_before"] == 0
            res = rec["result"]
            assert np.isfinite(res["logZ"]) and np.isfinite(res["logZerr"])
            with np.load(os.path.join(r["out"], "posterior.npz")) as d:
                assert list(d["labels"]) == ["H0"]
                assert d["samples"].shape[1] == 1 and d["samples"].shape[0] == res["n_samples"]
                assert d["dead_logwt"].size == res["n_dead"]
            with open(os.path.join(r["out"], "progress.csv")) as f:
                head = f.readline().strip().split(",")
            assert tuple(head) == infer_ladder.PROGRESS_COLUMNS
            if sampler == "tinyns":
                assert lc["sampler_reported_ncall"] and lc["n_like_evals"] == (
                    lc["preflight_eager_calls"] + lc["sampler_reported_ncall"])


def test_compare_posteriors(runs):
    work, out = runs
    for sampler in ("tinyns", "dynesty"):
        a, b = out[("run", "legacy", sampler)]["out"], out[("run", "core", sampler)]["out"]
        c = compare_posteriors.compare(compare_posteriors.load_run(a), compare_posteriors.load_run(b))
        assert c["verdict"]["integration_check_only"] is True
        assert set(c["parameters"]) == {"H0"}
        assert c["logZ"]["n_sigma"] is not None and c["logZ"]["n_sigma"] <= 3.0
        assert c["performance"]["A"]["n_like_evals"] and c["performance"]["B"]["n_like_evals"]
        rc = compare_posteriors.main([a, b, "--out", os.path.join(work, f"cmp_{sampler}.json"),
                                      "--md", os.path.join(work, f"cmp_{sampler}.md")])
        assert rc == 0
    x, y = out[("run", "legacy", "tinyns")]["out"], out[("run", "legacy", "dynesty")]["out"]
    assert compare_posteriors.main([x, y]) == 2
    assert compare_posteriors.main([x, y, "--cross-sampler"]) == 0


def test_preflight_abort_is_recorded(runs):
    _work, out = runs
    for impl in ("legacy", "core"):
        r = out[("abort", impl)]
        assert r["rc"] == 5, r
        rec = r["record"]
        assert rec["status"] == "sampler_error"
        assert rec["sampler_error"]["preflight_abort"] is True
        assert "-inf on ALL 32" in rec["sampler_error"]["message"]
        assert rec["settings"]["resolved"]["selection_neff_soft_guard"] is False
        assert not rec["first_call"]["finite"]


# ----------------------------------------------------------------------------
# Dark-siren plans (--plan / --catalog; mock-proxy ladder)
# ----------------------------------------------------------------------------
FIXTURE_T = os.environ.get("BENCH_FIXTURE_T_DIR", f"{_LOCAL}/mock/fixtures/T")


def test_dark_plans_resolve_and_legacy_argv():
    import impl_legacy
    import plans

    for name in ("dark_H0", "dark_full"):
        r = infer_ladder.resolve_dark_plan(name)
        p = plans.resolve_plan(name)
        assert r["sampled"] == p["sampled"] and r["universe"] == "dark"
        assert r["full_order"][r["expected_full_pow10_index"]] == "log10n0"
        argv = infer_ladder.legacy_argv(r, "PE", "SEL", "OUT", {
            "sampler": "dynesty", "seed": 1, "nlive": 10, "dlogz": 1.0, "max_samples": 0,
            "tinyns_preset": "recommended", "sampler_preflight": "on", "prior_transform_dispatch": "auto",
            "sel_batch_size": "4096", "pe_event_block": "6", "guard": "soft",
            "max_likelihood_variance": 10.0}, catalog="CAT", row_chunk="2048")
        assert argv[argv.index("--universe_model") + 1] == "dark_sirens"
        assert argv[argv.index("--survey_path") + 1] == "CAT"
        assert argv[argv.index("--row_chunk") + 1] == "2048"
        for flag, (value, _w) in impl_legacy.LEGACY_DARK_SETTINGS.items():
            if flag not in ("--universe_model", "--row_chunk"):
                assert argv[argv.index(flag) + 1] == value
        fixed = json.loads(argv[argv.index("--fixed_parameter_values") + 1])
        if name == "dark_H0":
            assert fixed == {"Om0": 0.3075, "log10n0": -3.0, "delta": 0.0, "sigma_kde": 0.0}
        else:
            assert fixed == {"Om0": 0.3075}
    with pytest.raises(ValueError):
        infer_ladder.resolve_dark_plan("spectral_H0")


@pytest.mark.parametrize("impl", ["legacy", "core"])
def test_dark_describe_fixture_T(impl, tmp_path):
    cat = os.path.join(FIXTURE_T, "catalog_pixelated_nside_16.h5")
    _need(cat)
    _need(PY[impl])
    outs = {}
    for plan in ("dark_H0", "dark_full"):
        out = str(tmp_path / f"{impl}_{plan}")
        cmd = [PY[impl], os.path.join(BENCH, "infer_ladder.py"), "--impl", impl, "--plan", plan,
               "--catalog", cat, "--sampler", "dynesty", "--pe", os.path.join(FIXTURE_T, "mock_gw_events.h5"),
               "--sel", os.path.join(FIXTURE_T, "mock_gw_selection.h5"), "--nlive", "20", "--dlogz", "2.0",
               "--seed", str(SEED), "--guard", "soft", "--max-variance", "10", "--out", out,
               "--device", "cpu", "--describe"]
        r = subprocess.run(cmd, env=_env(), capture_output=True, text=True, timeout=1800)
        assert r.returncode == 0, r.stderr[-3000:]
        rec = json.load(open(os.path.join(out, "record.json")))
        assert rec["status"] == "described" and rec["plan"]["assertions"]["ok"]
        assert rec["fixture_preflight"]["status"] == "ok"
        assert rec["inputs"]["catalog"]["sha256"]
        assert rec["settings"]["resolved"]["dark_settings"]
        outs[plan] = rec["first_call"]["logL_hex"]
    # the plans share the centre (fiducial population, fixture survey values)
    assert outs["dark_H0"] == outs["dark_full"]
