#!/usr/bin/env python3
"""Device-memory probe of the whole-likelihood kernel (OOM attribution; no kernel execution).

    python probe_memory.py --impl legacy|core --pe PE --sel SEL [--catalog CAT] --plan P \\
        --coords C --sel-batch N|none|default --pe-block N|none|default --seed S \\
        [--guard default|hard|soft] [--max-variance X] --out probe.json

Builds the implementation exactly as bench_fixed_theta.py does (same adapters), then
lowers and compiles the whole kernel (legacy: the factory's jitted body; core: the
--jit whole kernel) WITHOUT running it, and records

* the device memory_stats after the build (operands resident on the device),
* ``compiled.memory_analysis()`` (argument / output / temp / generated-code bytes: the temp
  size is the scratch XLA must allocate at the first call),
* the largest materialised buffers of the optimized HLO (instructions outside fused
  computations), with shape, opcode, op_name and source line: which axis (catalog rows x
  row width x quadrature nodes, injections, PE samples) the scratch comes from.

A build that itself runs out of memory is recorded with its traceback and memory_stats.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback

import numpy as np

import bench_common as bc
import plans

_DT = {"f64": 8, "s64": 8, "u64": 8, "c128": 16, "f32": 4, "s32": 4, "u32": 4, "c64": 8,
       "f16": 2, "bf16": 2, "s16": 2, "u16": 2, "s8": 1, "u8": 1, "pred": 1}
_INSTR = re.compile(r"^\s*(?:ROOT\s+)?%?([\w.\-]+)\s*=\s*([a-z0-9]+)\[([\d,]*)\]\{?[^ ]*\s+([\w\-]+)\(")
_COMP = re.compile(r"^\s*(?:ENTRY\s+)?%?([\w.\-]+)\s*\(.*\)\s*->.*\{\s*$")
_META = re.compile(r'op_name="([^"]*)"')
_SRC = re.compile(r'source_file="([^"]*)"\s+source_line=(\d+)')


def largest_buffers(hlo_text, top=15, dims=None):
    comp, rows = None, []
    for line in hlo_text.splitlines():
        m = _COMP.match(line)
        if m:
            comp = m.group(1)
            continue
        m = _INSTR.match(line)
        if not m or comp is None or comp.startswith("fused_") or "fused_computation" in comp:
            continue
        name, dt, shape, opcode = m.groups()
        if dt not in _DT or opcode in ("parameter", "constant", "get-tuple-element", "bitcast"):
            continue
        dims_ = [int(x) for x in shape.split(",") if x]
        nbytes = int(np.prod(dims_, dtype=np.int64)) * _DT[dt] if dims_ else _DT[dt]
        meta = _META.search(line)
        src = _SRC.search(line)
        rows.append({"computation": comp, "name": name, "dtype": dt, "shape": dims_,
                     "bytes": nbytes, "opcode": opcode,
                     "op_name": meta.group(1)[-160:] if meta else None,
                     "source": f"{src.group(1)}:{src.group(2)}" if src else None})
    rows.sort(key=lambda r: -r["bytes"])
    seen, out = set(), []
    for r in rows:
        key = (r["computation"], r["name"])
        if key in seen:
            continue
        seen.add(key)
        if dims:
            r["axes"] = [dims.get(d, "") for d in r["shape"]]
        out.append(r)
        if len(out) >= top:
            break
    return out


def _harness_git():
    import subprocess

    here = os.path.dirname(os.path.abspath(__file__))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=here, capture_output=True,
                             text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=here,
                                    capture_output=True, text=True).stdout.strip())
        return {"sha": sha, "dirty": dirty}
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("--impl", "--pe", "--sel", "--plan", "--coords", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--sel-batch", default="default")
    ap.add_argument("--pe-block", default="default")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--hlo-out", default=None)
    bc.add_guard_args(ap)
    a = ap.parse_args(argv)
    plan = plans.resolve_plan(a.plan)
    dark = plans.is_dark(plan)
    coords_doc = bc.read_json(a.coords)
    coord0 = np.asarray([float.fromhex(h) for h in coords_doc["values_hex"][0]], dtype=np.float64)
    import jax

    counter = bc.CompileCounter().install()
    impl = __import__("impl_legacy" if a.impl == "legacy" else "impl_core")
    pkg = impl.import_package()
    try:  # HLO metadata names the package's own lines (the legacy env is a site-packages install)
        from jax._src import source_info_util as _siu

        _siu.register_inclusion(os.path.dirname(os.path.abspath(pkg.__file__)))
    except Exception:  # pragma: no cover
        pass
    rec = {"schema": "darksirens-bench-probe-memory/1", "impl": a.impl, "plan": a.plan,
           "inputs": {"pe": a.pe, "sel": a.sel, "catalog": a.catalog},
           "blocks_requested": {"sel_batch": a.sel_batch, "pe_block": a.pe_block},
           "guard_requested": bc.guard_request(a), "device": bc.device_fingerprint("auto"),
           "harness": _harness_git(),
           "started_utc": bc.utc_now(), "mem": [bc.memory_checkpoint("after_import")]}
    cls = impl.LegacyAdapter if a.impl == "legacy" else impl.CoreAdapter
    kw = {"catalog_path": os.path.abspath(a.catalog)} if dark else {}
    ad = cls(plan, os.path.abspath(a.pe), os.path.abspath(a.sel), sel_batch=a.sel_batch,
             pe_block=a.pe_block, jit_mode="whole", seed=a.seed,
             save_dir=os.path.abspath(a.out) + ".legacy_save", counter=counter,
             guard=bc.guard_request(a)["mode"], max_variance=a.max_variance, **kw)
    try:
        t0 = time.perf_counter()
        ad.build()
        rec["t_build_s"] = time.perf_counter() - t0
    except Exception as exc:
        rec.update(status="build_error", error=f"{type(exc).__name__}: {exc}"[:3000],
                   traceback_tail=traceback.format_exc()[-6000:],
                   memory_at_failure=bc.memory_checkpoint("at_build_failure"))
        bc.write_json(a.out, rec)
        print(rec["error"][:300], file=sys.stderr)
        return 4
    rec["mem"].append(bc.memory_checkpoint("after_build"))
    rec["dims"] = ad.dims()
    rec["config_blocks"] = {k: (ad.config().get(k) or {}) for k in ("sel_batch_size", "pe_event_block")}
    import jax.numpy as jnp

    if a.impl == "legacy":
        lk = ad.likelihood
        fn, args, kwargs = lk.jitted_body, (jnp.asarray(coord0), lk.operands, lk.distance_table,
                                            lk.smoothing_operator), {}
    else:
        from darksirens.cosmology import distances as D

        b = ad.bound
        args = (jnp.asarray(coord0), b.gw_pe, b.gw_selection)
        if dark:
            args = args + (b.catalog, b.observed_density_cache)
        fn = ad._whole.jitted
        kwargs = {"distance_table": D.distance_table(),
                  "_ambient_extras": tuple(res() for res, _ in D._AMBIENT_JIT_CHANNELS)}
    t0 = time.perf_counter()
    compiled = fn.lower(*args, **kwargs).compile()
    rec["t_lower_compile_s"] = time.perf_counter() - t0
    ma = compiled.memory_analysis()
    rec["memory_analysis"] = {k: int(getattr(ma, k)) for k in (
        "argument_size_in_bytes", "output_size_in_bytes", "temp_size_in_bytes",
        "alias_size_in_bytes", "generated_code_size_in_bytes") if hasattr(ma, k)}
    d = rec["dims"]
    cat = d.get("catalog") or {}
    axis = {}
    for k, lab in ((cat.get("n_rows"), "catalog rows"), (cat.get("n_max"), "row width (n_max)"),
                   (d.get("n_injections"), "injections"), (d.get("n_events"), "events"),
                   (d.get("nsamp"), "PE samples per event"),
                   ((d.get("n_events") or 0) * (d.get("nsamp") or 0), "PE samples"), (24, "CDF nodes")):
        if k:
            axis.setdefault(int(k), lab)
    hlo = compiled.as_text()
    if a.hlo_out:
        with open(a.hlo_out, "w") as f:
            f.write(hlo)
    rec["largest_buffers"] = largest_buffers(hlo, dims=axis)
    rec["axis_labels"] = {str(k): v for k, v in axis.items()}
    rec["status"] = "ok"
    rec["finished_utc"] = bc.utc_now()
    bc.write_json(a.out, rec)
    ma_ = rec["memory_analysis"]
    print(f"temp {ma_.get('temp_size_in_bytes', 0) / 2**30:.2f} GiB, args "
          f"{ma_.get('argument_size_in_bytes', 0) / 2**30:.2f} GiB, in use after build "
          f"{(rec['mem'][-1]['device_bytes_in_use'] or 0) / 2**30:.2f} GiB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
