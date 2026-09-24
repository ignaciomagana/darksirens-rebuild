"""Smoke test of the component-timing runner (bench_components.py) and trace_tools.py.

Fast unit tests (no JAX): the trace parser on a synthetic Chrome trace, the
element-wise comparator, the npz storage policy.

Subprocess tests (both implementations, separate interpreters, CPU):
* spectral_full on core's tiny gwcat 2.1 fixture (tools/make_gw_fixtures.py);
* dark_full on the campaign's dark fixture T (skipped without it).
Each runs the main harness (bench_fixed_theta.py) and bench_components.py with
--main-record for both implementations, then asserts: the record schema, every
available component timed with 0 compiles in its timed loop, i_whole bit-identical
to the main harness, every gate component at legacy-vs-core parity rtol 1e-12
(compare mode), the per-sample catalog densities under D-catvals, the trace pass
parsed with outputs unchanged, and trace_tools.py main + check-numerics.

Configuration (environment) as tests/test_harness_smoke.py: BENCH_LEGACY_PYTHON,
BENCH_CORE_PYTHON, BENCH_CORE_REPO, BENCH_DARK_FIXTURE.
"""

from __future__ import annotations

import concurrent.futures as cf
import gzip
import json
import os
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
sys.path.insert(0, BENCH)

import bench_components as bcmp  # noqa: E402
import trace_tools  # noqa: E402

_LOCAL = "/hildafs/projects/phy230014p/magana/darksirens_benchmark_local"
LEGACY_PY = os.environ.get("BENCH_LEGACY_PYTHON", f"{_LOCAL}/envs/legacy311_cpu/bin/python")
CORE_PY = os.environ.get(
    "BENCH_CORE_PYTHON",
    "/hildafs/home/magana/.claude/projects/-hildafs-projects-phy230014p-magana-darksirens-core/"
    "review-state/venv/bin/python")
CORE_REPO = os.environ.get("BENCH_CORE_REPO", "/hildafs/projects/phy230014p/magana/darksirens-core")
DARK_FIXTURE = os.environ.get("BENCH_DARK_FIXTURE", f"{_LOCAL}/mock/fixtures/T")
SEED = 20260924
PY = {"legacy": LEGACY_PY, "core": CORE_PY}


# ---------------------------------------------------------------------------
# unit tests (no JAX)
# ---------------------------------------------------------------------------
def _write_trace(path, events, procs, threads):
    ev = [{"ph": "M", "name": "process_name", "pid": p, "args": {"name": n}} for p, n in procs.items()]
    ev += [{"ph": "M", "name": "thread_name", "pid": p, "tid": t, "args": {"name": n}}
           for (p, t), n in threads.items()]
    ev += events
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        json.dump({"displayTimeUnit": "ns", "metadata": {}, "traceEvents": ev}, f)


def _x(pid, tid, name, ts, dur):
    return {"ph": "X", "pid": pid, "tid": tid, "name": name, "ts": ts, "dur": dur}


def test_trace_parser_cpu_self_time_union_and_gaps(tmp_path):
    d = tmp_path / "tr"
    p = d / "plugins" / "profile" / "2026_01_01_00_00_00" / "host.trace.json.gz"
    procs = {1: "/device:GPU:0", 7: "/host:CPU"}
    threads = {(7, 1): "python", (7, 2): "tf_XLATfrtCpuClient/1", (7, 3): "tf_XLAEigen/2"}
    events = [
        _x(7, 1, "bench_call", 0.0, 100.0), _x(7, 1, "bench_call", 200.0, 100.0),
        # call 1: a parent 'call.1' [10, 60) containing a fusion [20, 50); a parallel reduce
        _x(7, 2, "call.1", 10.0, 50.0), _x(7, 2, "add_multiply_fusion.clone", 20.0, 30.0),
        _x(7, 3, "reduce.16", 40.0, 40.0),
        # infrastructure events that must be ignored
        _x(7, 2, "ThreadpoolListener::Record", 0.0, 99.0), _x(7, 2, "ThunkExecutor::Execute (wait)", 0.0, 99.0),
        # call 2: one fusion [210, 290)
        _x(7, 2, "add_multiply_fusion.clone", 210.0, 80.0),
    ]
    _write_trace(str(p), events, procs, threads)
    s = trace_tools.summarize_trace_dir(str(d), top_n=5)
    assert s["mode"] == "cpu"  # the GPU process has no events
    assert s["n_op_events"] == 4
    rows = {r["name"]: r for r in s["top_ops"]}
    assert rows["call.1"]["self_s"] == pytest.approx(20e-6)          # 50 - 30 (nested fusion)
    assert rows["add_multiply_fusion.clone"]["self_s"] == pytest.approx(110e-6)
    assert rows["add_multiply_fusion.clone"]["category"] == "add_multiply_fusion"
    assert rows["add_multiply_fusion.clone"]["kind"] == "fusion"
    assert s["device_time"]["busy_union_s"] == pytest.approx((70 + 80) * 1e-6)  # [10,80) + [210,290)
    w = s["windows"]
    assert w["n"] == 2 and w["total_s"] == pytest.approx(200e-6)
    assert w["busy_s"] == pytest.approx(150e-6) and w["idle_s"] == pytest.approx(50e-6)
    assert s["gaps"]["count"] == 4  # [0,10) [80,100) [200,210) [290,300)
    md = trace_tools.summary_markdown(s)
    assert "| rank | op |" in md and "add_multiply_fusion.clone" in md


def test_trace_parser_gpu_prefers_xla_ops_line(tmp_path):
    d = tmp_path / "tr"
    p = d / "plugins" / "profile" / "s" / "h.trace.json.gz"
    procs = {1: "/device:GPU:0", 7: "/host:CPU"}
    threads = {(1, 1): "XLA Ops", (1, 2): "Stream #13(Compute)", (7, 1): "python"}
    events = [_x(1, 1, "fusion.3", 0.0, 10.0), _x(1, 2, "loop_fusion_kernel", 0.0, 10.0),
              _x(1, 1, "reduce.2", 20.0, 5.0)]
    _write_trace(str(p), events, procs, threads)
    s = trace_tools.summarize_trace_dir(str(d))
    assert s["mode"] == "gpu" and s["op_source"] == "GPU 'XLA Ops' line"
    assert s["n_op_events"] == 2
    assert s["windows"]["source"].startswith("span of the op events")
    assert s["gaps"]["count"] == 1 and s["gaps"]["top"][0]["duration_us"] == pytest.approx(10.0)


def test_trace_parser_gpu_stream_lines_use_hlo_op(tmp_path):
    d = tmp_path / "tr"
    p = d / "plugins" / "profile" / "s" / "h.trace.json.gz"
    procs = {1: "/device:GPU:0", 7: "/host:CPU"}
    threads = {(1, 2): "Stream #13(Compute)", (1, 3): "Stream #14(MemcpyH2D)", (7, 1): "python"}
    k = _x(1, 2, "loop_add_fusion_kernel", 0.0, 10.0)
    k["args"] = {"hlo_op": "add_fusion.7", "hlo_module": "jit_f"}
    events = [k, _x(1, 3, "MemcpyH2D", 12.0, 3.0), _x(7, 1, "bench_call", 0.0, 20.0)]
    _write_trace(str(p), events, procs, threads)
    s = trace_tools.summarize_trace_dir(str(d))
    assert s["mode"] == "gpu" and s["op_source"].startswith("GPU stream lines")
    names = {r["name"]: r for r in s["top_ops"]}
    assert "add_fusion.7" in names and names["add_fusion.7"]["kind"] == "fusion"
    assert names["MemcpyH2D"]["kind"] == "transfer"
    assert s["windows"]["busy_s"] == pytest.approx(13e-6) and s["windows"]["idle_s"] == pytest.approx(7e-6)


def test_compare_arrays_semantics():
    a = np.array([1.0, -np.inf, np.nan, 0.0, 2.0])
    r = bcmp.compare_arrays(a, a.copy(), 1e-12)
    assert r["pass_rel"] and r["bitwise"] and r["max_rel"] == 0.0
    b = a.copy()
    b[4] = 2.0 * (1 + 3e-12)
    r = bcmp.compare_arrays(a, b, 1e-12)
    assert not r["pass_rel"] and r["pass_abs"] is False  # |d| = 6e-12 > 1e-12
    b = a.copy()
    b[1] = np.inf
    assert not bcmp.compare_arrays(a, b, 1e-12)["pass_rel"]
    b = a.copy()
    b[2] = 0.0
    assert not bcmp.compare_arrays(a, b, 1e-12)["pass_rel"]
    assert bcmp.compare_arrays(np.zeros(3), np.zeros(4), 1e-12)["shape_mismatch"]


def test_storage_policy_and_classes():
    assert bcmp.output_class("g_prior_eval", "log_prior_sel") == "catvals"
    assert bcmp.output_class("h_completion", "f") == "info"
    assert bcmp.output_class("fh_prior_state", "dN_miss") == "derived"
    assert bcmp.output_class("e_sel_reduce", "n_eff") == "gate"
    assert not bcmp.store_policy("fh_prior_state", "dN_miss", 10, 3, 100, [0, 1])
    assert bcmp.store_policy("h_completion", "dN_miss", 10, 3, 100, [0, 1])
    assert bcmp.store_policy("h_completion", "dN_miss", 1000, 1, 100, [0, 1])
    assert not bcmp.store_policy("h_completion", "dN_miss", 1000, 2, 100, [0, 1])
    assert not bcmp.store_policy("h_completion", "C_eff", 1000, 1, 100, [0, 1])
    assert set(bcmp.ORDER) == {c["name"] for c in bcmp.COMPONENTS}
    for c in bcmp.COMPONENTS:
        assert c["legacy_ref"] and c["core_ref"] and set(c["kind"]) == {"legacy", "core"}


# ---------------------------------------------------------------------------
# subprocess smoke runs
# ---------------------------------------------------------------------------
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


def _pipeline(work, plan, pe, sel, catalog=None, n_calls=5, trace_impl="core"):
    """main harness (both impls) -> components (both impls, --main-record) -> compare."""
    coords = os.path.join(work, f"coords_{plan}.json")
    r = _run([sys.executable, os.path.join(BENCH, "make_coords.py"), "--plan", plan, "--seed", str(SEED),
              "--n", "8", "--out", coords], work)
    assert r["rc"] == 0, r
    cat = ["--catalog", catalog] if catalog else []
    common = ["--pe", pe, "--sel", sel, "--plan", plan, "--coords", coords, "--device", "cpu"] + cat
    mains = {}
    jobs = {}
    for impl in ("legacy", "core"):
        out = os.path.join(work, f"main_{plan}_{impl}.json")
        mains[impl] = out
        jobs[impl] = [PY[impl], os.path.join(BENCH, "bench_fixed_theta.py"), "--impl", impl] + common + [
            "--out", out, "--n-calls", str(n_calls), "--warmup", "3", "--jit", "whole", "--sel-batch", "none",
            "--pe-block", "none", "--seed", str(SEED), "--label", f"main_{impl}"]
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        res = dict(zip(jobs, ex.map(lambda c: _run(c, work), jobs.values())))
    for impl, r in res.items():
        assert r["rc"] == 0, r
    comps, jobs = {}, {}
    for impl in ("legacy", "core"):
        out = os.path.join(work, f"comp_{plan}_{impl}.json")
        comps[impl] = out
        cmd = [PY[impl], os.path.join(BENCH, "bench_components.py"), "--impl", impl] + common + [
            "--out", out, "--n-calls", str(n_calls), "--warmup", "3", "--main-record", mains[impl],
            "--label", f"comp_{impl}", "--cache-dir", os.path.join(work, f"cache_{plan}_{impl}"),
            "--cache-mode", "cold"]
        if impl == trace_impl:
            cmd += ["--trace", os.path.join(work, f"trace_{plan}_{impl}"), "--trace-calls", "3",
                    "--trace-drop-xplane"]
        jobs[impl] = cmd
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        res = dict(zip(jobs, ex.map(lambda c: _run(c, work), jobs.values())))
    for impl, r in res.items():
        assert r["rc"] == 0, r
    summ = os.path.join(work, f"cmp_{plan}.json")
    r = _run([sys.executable, os.path.join(BENCH, "bench_components.py"), "compare", comps["legacy"],
              comps["core"], "--out", summ, "--md", summ[:-5] + ".md"], work)
    return {"mains": mains, "comps": comps, "compare_rc": r, "summary": summ, "coords": coords,
            "common": common}


@pytest.fixture(scope="session")
def spectral(tmp_path_factory):
    for p in (LEGACY_PY, CORE_PY, os.path.join(CORE_REPO, "tools", "make_gw_fixtures.py")):
        _need(p)
    work = str(tmp_path_factory.mktemp("comp_spectral"))
    fx = os.path.join(work, "fixtures")
    r = _run([CORE_PY, os.path.join(CORE_REPO, "tools", "make_gw_fixtures.py"), fx], work)
    assert r["rc"] == 0, r
    return dict(_pipeline(work, "spectral_full", os.path.join(fx, "pe_chieff.h5"),
                          os.path.join(fx, "sel_chieff.h5")), work=work)


@pytest.fixture(scope="session")
def dark(tmp_path_factory):
    for p in (LEGACY_PY, CORE_PY, os.path.join(DARK_FIXTURE, "galaxy_density.json")):
        _need(p)
    work = str(tmp_path_factory.mktemp("comp_dark"))
    cat = [f for f in os.listdir(DARK_FIXTURE) if f.startswith("catalog_pixelated_nside_")][0]
    return dict(_pipeline(work, "dark_full", os.path.join(DARK_FIXTURE, "mock_gw_events.h5"),
                          os.path.join(DARK_FIXTURE, "mock_gw_selection.h5"),
                          catalog=os.path.join(DARK_FIXTURE, cat), trace_impl="legacy"), work=work)


def _check_record(path, impl, dark_plan):
    r = json.load(open(path))
    assert r["schema"] == bcmp.RECORD_SCHEMA and r["status"] == "ok" and r["implementation"] == impl
    for k in ("components", "components_npz", "whole_vs_main_record", "sum_check", "xla_cache",
              "timing_context", "repeat_consistency"):
        assert k in r, k
    assert r["whole_vs_main_record"]["bitwise"], r["whole_vs_main_record"]
    assert r["repeat_consistency"]["bitwise"]
    assert r["xla_cache"]["mode"] == "cold" and r["xla_cache"]["files_before"] == 0
    assert r["aot_policy"].startswith("persistent compilation cache disabled")
    expect = {"a_cosmology", "b_population", "c_pop_norm", "w_weights", "d_pe_reduce", "e_sel_reduce",
              "g_prior_eval", "i_whole", "j_transfer"}
    if dark_plan:
        expect |= {"f_kernel_state", "h_completion", "fh_prior_state"}
    if impl == "legacy":
        expect.add("k_layout")
    got = {n for n, e in r["components"].items() if e["available"]}
    assert expect <= got, expect - got
    for n in got:
        e = r["components"][n]
        t = e["timing"]
        assert t["timed_loop_compile"]["requests"] == 0, n
        assert t["warm"]["n"] == r["config"]["n_calls"] and t["warm"]["median_s"] > 0
        if n not in ("j_transfer", "k_layout", "i_whole"):
            assert e["repeat_bitwise"], n
            assert not e["jaxpr"]["embeds_data_literal"], n
            assert "t_compile_s" in e["aot"], (n, e["aot"])
            assert e["aot"]["compile_counter_delta"]["compiles"] >= 1, (n, e["aot"])  # a real compile
    if impl == "legacy":
        lay = r["components"]["k_layout"]["layout"]
        assert lay["order_reproduces_adapter_order"] and lay["permuted_equals_kernel_operands"]
    return r


@pytest.mark.parametrize("impl", ["legacy", "core"])
def test_spectral_records(spectral, impl):
    _check_record(spectral["comps"][impl], impl, dark_plan=False)


def test_spectral_parity(spectral):
    assert spectral["compare_rc"]["rc"] == 0, spectral["compare_rc"]
    s = json.load(open(spectral["summary"]))
    rows = {r["component"]: r for r in s["rows"]}
    for n in ("a_cosmology", "b_population", "c_pop_norm", "w_weights", "d_pe_reduce", "e_sel_reduce",
              "g_prior_eval", "i_whole"):
        assert rows[n]["parity_1e12"] is True, rows[n]
    assert s["whole_vs_main_bitwise"] == {"a": True, "b": True}


def test_spectral_trace_numerics_unchanged(spectral):
    r = json.load(open(spectral["comps"]["core"]))
    t = r["trace"]
    assert t["numerics_unchanged"] and t["whole_bitwise_under_trace"] and t["all_parsed"]
    assert t["components"]["i_whole"]["summary"]["n_op_events"] > 0
    assert t["components"]["i_whole"]["xplane_removed"]


def test_main_harness_trace_mode(spectral):
    work = spectral["work"]
    out = os.path.join(work, "main_traced_core.json")
    tdir = os.path.join(work, "trace_main_core")
    cmd = [CORE_PY, os.path.join(BENCH, "trace_tools.py"), "main", "--trace", tdir, "--",
           "--impl", "core"] + spectral["common"] + [
        "--out", out, "--n-calls", "5", "--warmup", "3", "--jit", "whole", "--sel-batch", "none",
        "--pe-block", "none", "--seed", str(SEED), "--label", "main_traced"]
    r = _run(cmd, work)
    assert r["rc"] == 0, r
    rec = json.load(open(out))
    assert rec["trace"]["parse_ok"] and rec["trace"]["annotated_calls"] == 5
    assert any("jax.profiler.trace" in g for g in rec["gaps"])
    assert os.path.isfile(os.path.join(tdir, "trace_summary.md"))
    r = _run([sys.executable, os.path.join(BENCH, "trace_tools.py"), "check-numerics", out,
              spectral["mains"]["core"]], work)
    assert r["rc"] == 0 and '"bitwise": true' in r["stdout"], r


@pytest.mark.parametrize("impl", ["legacy", "core"])
def test_dark_records(dark, impl):
    r = _check_record(dark["comps"][impl], impl, dark_plan=True)
    assert r["fh_dN_miss_equals_h_dN_miss"]


def test_dark_parity(dark):
    assert dark["compare_rc"]["rc"] == 0, dark["compare_rc"]
    s = json.load(open(dark["summary"]))
    rows = {r["component"]: r for r in s["rows"]}
    for n in ("a_cosmology", "b_population", "c_pop_norm", "w_weights", "d_pe_reduce", "e_sel_reduce",
              "f_kernel_state", "h_completion", "fh_prior_state", "i_whole"):
        assert rows[n]["parity_1e12"] is True, rows[n]
        assert rows[n]["criterion"].startswith("rtol"), rows[n]
    assert rows["g_prior_eval"]["parity_1e12"] is True
    assert rows["g_prior_eval"]["criterion"].startswith("D-catvals")
    assert rows["h_completion"]["coords_elementwise_min"] >= 1


def test_dark_trace_numerics_unchanged(dark):
    t = json.load(open(dark["comps"]["legacy"]))["trace"]
    assert t["numerics_unchanged"] and t["whole_bitwise_under_trace"] and t["all_parsed"]
