"""Implementation-neutral helpers for the fixed-coordinate benchmark harness.

Nothing here imports darksirens. ``install_compile_hooks`` must run before the
implementation is imported so that every XLA compile request is counted.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import os
import platform
import re
import resource
import socket
import subprocess
import sys
import time

import numpy as np

RECORD_SCHEMA = "darksirens-bench-fixed-theta/1"

#: sha256 over the sorted ``relpath\0git-blob-sha1\n`` lines of every ``*.py``
#: file of the ``darksirens`` package (``__pycache__`` and dot-directories
#: skipped). Computed from ``git ls-tree -r <sha> <pkgdir>``; lets a record
#: prove which commit a non-editable install (no .git) was built from.
KNOWN_PACKAGE_DIGESTS = {
    "96fb44f56a3a247c6a5dfd7d1161789b10557d0678dd6c663528dc900d67bf58": {
        "repo": "ignaciomagana/darksirens (reference, frozen)",
        "sha": "c042527238bd71421b792936bc48c3b815b90d6d",
        "n_py": 108,
    },
    "3fb7954df25625c7370dbb09a3223486fdab2875017ed8563a982fa29366e4e8": {
        "repo": "darksirens-core main (candidate)",
        "sha": "88004d96ddeee37c47abc1d2dfd1c6fc3c203dfd",
        "n_py": 74,
    },
    "7e15c2c12fad8ad04a02397d8fc15addd6976e26c71bfdf427569b12213cb5fb": {
        "repo": "darksirens-core pin (control)",
        "sha": "8bf2bec53ff7b557c6b930d4044008cb72008f61",
        "n_py": 74,
    },
}


# ----------------------------------------------------------------------------
# Compile hooks (same JAX internals as legacy scripts/benchmarks/
# bench_likelihood_call.py:85-104)
# ----------------------------------------------------------------------------
class CompileCounter:
    """Counts ``compile_or_get_cached`` (requests) and ``backend_compile``.

    ``compile_or_get_cached`` runs once per executable JAX asks for, whether it
    is compiled or served from the persistent cache; ``backend_compile`` runs
    only on a cache miss. Both are module globals of ``jax._src.compiler``
    looked up per call (``jax._src.interpreters.pxla`` calls
    ``compiler.compile_or_get_cached``; ``compile_or_get_cached`` calls the
    module-global ``backend_compile``), so patching the module attributes is
    enough.
    """

    def __init__(self):
        self.requests = 0
        self.compiles = 0
        self.installed = False

    def install(self):
        import jax._src.compiler as comp

        orig_bc = comp.backend_compile
        orig_cgc = comp.compile_or_get_cached
        counter = self

        def counting_backend_compile(*a, **k):
            counter.compiles += 1
            return orig_bc(*a, **k)

        def counting_compile_or_get_cached(*a, **k):
            counter.requests += 1
            return orig_cgc(*a, **k)

        comp.backend_compile = counting_backend_compile
        comp.compile_or_get_cached = counting_compile_or_get_cached
        self.installed = True
        return self

    def snapshot(self):
        return (self.requests, self.compiles)

    def delta(self, snap):
        return {"requests": self.requests - snap[0], "compiles": self.compiles - snap[1]}


def compile_hook_selftest(counter: CompileCounter) -> dict:
    """Force a fresh compilation and check that both counters move.

    A jitted function of a shape no other code uses (a prime length derived
    from the pid) cannot be in the in-memory cache; its compile time is far
    below JAX's persistent-cache threshold, so it is compiled, not served.
    """
    import jax
    import jax.numpy as jnp

    n = 7919 + (os.getpid() % 97) * 2
    snap = counter.snapshot()
    f = jax.jit(lambda x: jnp.sin(x) * 3.0 + 1.0)
    jax.block_until_ready(f(jnp.ones((n,), dtype=jnp.float64)))
    d = counter.delta(snap)
    snap2 = counter.snapshot()
    jax.block_until_ready(f(jnp.ones((n,), dtype=jnp.float64)))  # cached: must not move
    d2 = counter.delta(snap2)
    return {
        "forced_shape": [n],
        "first_call": d,
        "repeat_call": d2,
        "ok": bool(d["requests"] >= 1 and d2["requests"] == 0),
        "compiles_moved": bool(d["compiles"] >= 1),
    }


# ----------------------------------------------------------------------------
# Float / array encoding
# ----------------------------------------------------------------------------
def fhex(x) -> str:
    return float(x).hex()


def fval(x):
    """JSON-safe float: finite numbers as numbers, non-finite as strings."""
    x = float(x)
    if math.isfinite(x):
        return x
    if math.isnan(x):
        return "nan"
    return "inf" if x > 0 else "-inf"


def scalar_entry(x) -> dict:
    x = float(np.asarray(x))
    return {"value": fval(x), "hex": fhex(x)}


def array_entry(a) -> dict:
    a = np.asarray(a, dtype=np.float64).ravel()
    return {"hex": [fhex(v) for v in a], "n": int(a.size)}


def from_hex_list(hexes):
    return np.asarray([float.fromhex(h) for h in hexes], dtype=np.float64)


def mask_entry(mask) -> dict:
    m = np.asarray(mask, dtype=bool).ravel()
    return {
        "n": int(m.size),
        "count_true": int(m.sum()),
        "sha256_u8": hashlib.sha256(m.astype(np.uint8).tobytes()).hexdigest(),
    }


# ----------------------------------------------------------------------------
# Files and fingerprints
# ----------------------------------------------------------------------------
def sha256_file(path, bufsize=1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _decode_attr(v):
    if isinstance(v, bytes):
        return v.decode()
    if isinstance(v, np.ndarray):
        if v.dtype.kind in "SO":
            return [x.decode() if isinstance(x, bytes) else str(x) for x in v.tolist()]
        return v.tolist()
    if isinstance(v, np.generic):
        return v.item()
    return v


def gwcat_file_info(path: str) -> dict:
    """sha256 and the contract-relevant attributes of a gwcat HDF5 file."""
    import h5py

    info = {
        "path": os.path.abspath(path),
        "bytes": os.path.getsize(path),
        "sha256": sha256_file(path),
    }
    keys = (
        "format_version", "parameter_space", "spin_basis", "spin_basis_kind",
        "contract_hash", "nobs", "nsamp", "ndraw", "n_detected", "T_obs_yr",
        "analysis_time_yr", "fit_columns", "advisory_columns",
        "subset_stride", "subset_parent_sha256",
    )
    with h5py.File(path, "r") as f:
        attrs = {}
        for k in keys:
            if k in f.attrs:
                attrs[k] = _decode_attr(f.attrs[k])
        info["attrs"] = attrs
        info["datasets"] = sorted(f.keys())
    return info


def py_package_digest(pkgdir: str) -> tuple[str, int]:
    rows = []
    for root, dirs, files in os.walk(pkgdir):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__" and not d.startswith("."))
        for fn in sorted(files):
            if fn.endswith(".py"):
                p = os.path.join(root, fn)
                with open(p, "rb") as f:
                    data = f.read()
                blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
                rows.append((os.path.relpath(p, pkgdir).replace(os.sep, "/"), blob))
    rows.sort()
    h = hashlib.sha256()
    for rel, blob in rows:
        h.update(f"{rel}\0{blob}\n".encode())
    return h.hexdigest(), len(rows)


def _git(args, cwd):
    try:
        return subprocess.run(["git", "-C", cwd] + args, capture_output=True, text=True,
                              timeout=20).stdout.strip()
    except Exception:  # pragma: no cover
        return ""


def package_fingerprint(module) -> dict:
    pkgdir = os.path.dirname(os.path.abspath(module.__file__))
    digest, n_py = py_package_digest(pkgdir)
    out = {
        "name": module.__name__,
        "file": os.path.abspath(module.__file__),
        "package_dir": pkgdir,
        "py_blob_digest": digest,
        "n_py_files": n_py,
        "known_digest_match": KNOWN_PACKAGE_DIGESTS.get(digest),
        "git_sha": None,
        "git_dirty": None,
        "git_root": None,
        "git_sha_source": "not a git checkout (non-editable install); see known_digest_match",
    }
    root = _git(["rev-parse", "--show-toplevel"], pkgdir)
    if root:
        out["git_root"] = root
        out["git_sha"] = _git(["rev-parse", "HEAD"], pkgdir) or None
        status = _git(["status", "--porcelain", "--untracked-files=no", "--", pkgdir], pkgdir)
        out["git_dirty"] = bool(status)
        out["git_sha_source"] = "git rev-parse HEAD in the package checkout"
    return out


def _dist_version(name):
    try:
        from importlib import metadata

        return metadata.version(name)
    except Exception:
        return None


def env_fingerprint() -> dict:
    from importlib import metadata

    cuda = {}
    for dist in metadata.distributions():
        n = (dist.metadata.get("Name") or "").lower()
        if n.startswith("nvidia-") or n.startswith("jax-cuda") or n.startswith("jax_cuda"):
            cuda[n] = dist.version
    env_vars = {k: v for k, v in sorted(os.environ.items())
                if k.startswith(("JAX_", "XLA_", "DARKSIRENS_", "CUDA_", "TF_", "OMP_", "MKL_",
                                 "OPENBLAS_", "PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE"))}
    return {
        "python": sys.version.split()[0],
        "python_full": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "host": socket.gethostname(),
        "versions": {n: _dist_version(n) for n in ("jax", "jaxlib", "numpy", "scipy", "h5py",
                                                   "astropy", "equinox", "gwcat")},
        "cuda_wheels": dict(sorted(cuda.items())),
        "env_vars": env_vars,
    }


def _nvidia_smi():
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version,uuid",
             "--format=csv,noheader"], capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return None
        rows = []
        for line in r.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                rows.append({"name": parts[0], "memory_total": parts[1],
                             "driver_version": parts[2],
                             "uuid": parts[3] if len(parts) > 3 else None})
        return rows or None
    except Exception:
        return None


def _nvidia_smi_extra():
    """Optional GPU details; any failure (old driver, unknown field) returns None."""
    out = {}
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap,pci.bus_id,persistence_mode,mig.mode.current,"
             "clocks.max.sm,clocks.max.memory,power.limit,ecc.mode.current",
             "--format=csv,noheader"], capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            keys = ("compute_cap", "pci_bus_id", "persistence_mode", "mig_mode", "clocks_max_sm",
                    "clocks_max_memory", "power_limit", "ecc_mode")
            out["gpus"] = [dict(zip(keys, [p.strip() for p in line.split(",")]))
                           for line in r.stdout.strip().splitlines()]
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=20)
        m = re.search(r"CUDA Version:\s*([0-9.]+)", r.stdout)
        out["driver_cuda_version"] = m.group(1) if m else None
    except Exception:
        pass
    return out or None


def _platform_version():
    """XLA backend platform version (e.g. the CUDA runtime jaxlib was built against)."""
    try:
        from jax.lib import xla_bridge

        return str(xla_bridge.get_backend().platform_version)
    except Exception:
        return None


def _cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or None


def device_fingerprint(requested: str) -> dict:
    import jax

    devs = jax.devices()
    backend = jax.default_backend()
    out = {
        "requested": requested,
        "backend": backend,
        "devices": [str(d) for d in devs],
        "device_kind": [getattr(d, "device_kind", None) for d in devs],
        "platform": devs[0].platform if devs else None,
        "x64": bool(jax.config.jax_enable_x64),
        "matmul_precision": str(jax.config.jax_default_matmul_precision),
        "xla_cache_dir": jax.config.jax_compilation_cache_dir,
        "platform_version": _platform_version(),
        "cpu": {"model": _cpu_model(), "os_cpu_count": os.cpu_count(),
                "affinity": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None},
        "gpu": None,
    }
    if backend == "gpu":
        stats = None
        try:
            stats = devs[0].memory_stats()
        except Exception:
            stats = None
        out["gpu"] = {
            "nvidia_smi": _nvidia_smi(),
            "nvidia_smi_extra": _nvidia_smi_extra(),
            "compute_capability": [getattr(d, "compute_capability", None) for d in devs],
            "bytes_limit": (stats or {}).get("bytes_limit"),
        }
    return out


# ----------------------------------------------------------------------------
# Memory
# ----------------------------------------------------------------------------
def memory_checkpoint(tag: str) -> dict:
    import jax

    stats = None
    try:
        stats = jax.devices()[0].memory_stats()
    except Exception:
        stats = None
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "tag": tag,
        "host_maxrss_bytes": int(ru.ru_maxrss) * 1024,
        "device_peak_bytes_in_use": None if not stats else stats.get("peak_bytes_in_use"),
        "device_bytes_in_use": None if not stats else stats.get("bytes_in_use"),
        "device_bytes_limit": None if not stats else stats.get("bytes_limit"),
    }


# ----------------------------------------------------------------------------
# Timing helpers
# ----------------------------------------------------------------------------
def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds")


class PhaseClock:
    """Wall-clock stamps (unix seconds + UTC ISO) for joining nvidia-smi logs."""

    def __init__(self):
        self.stamps = {}

    def mark(self, name):
        self.stamps[name] = {"unix": time.time(), "utc": utc_now()}


def stats(times) -> dict:
    t = np.asarray(times, dtype=np.float64)
    return {
        "n": int(t.size),
        "median_s": float(np.median(t)),
        "min_s": float(np.min(t)),
        "mean_s": float(np.mean(t)),
        "std_s": float(np.std(t)),  # population std (ddof=0)
        "max_s": float(np.max(t)),
    }


def tree_nbytes(tree) -> int:
    import jax

    total = 0
    for leaf in jax.tree_util.tree_leaves(tree):
        nb = getattr(leaf, "nbytes", None)
        if nb is not None:
            total += int(nb)
    return total


# ----------------------------------------------------------------------------
# jaxpr / HLO evidence that data operands are ARGUMENTS, not literals
# ----------------------------------------------------------------------------
def _iter_closed_jaxprs(closed):
    """Yield every ClosedJaxpr reachable from ``closed`` (including itself)."""
    from jax import core as jcore

    seen = set()
    stack = [closed]
    while stack:
        cj = stack.pop()
        if id(cj) in seen:
            continue
        seen.add(id(cj))
        yield cj
        jaxpr = cj.jaxpr if hasattr(cj, "jaxpr") else cj
        for eqn in jaxpr.eqns:
            for v in eqn.params.values():
                vals = v if isinstance(v, (list, tuple)) else (v,)
                for x in vals:
                    if isinstance(x, jcore.ClosedJaxpr):
                        stack.append(x)
                    elif isinstance(x, jcore.Jaxpr):
                        stack.append(jcore.ClosedJaxpr(x, ()))


def jaxpr_const_report(fn, args, kwargs, data_arrays: dict) -> dict:
    """Inventory of constants captured anywhere in ``fn``'s jaxpr.

    ``data_arrays``: name -> concrete array. A captured constant with the same
    shape and dtype as one of them and equal content is reported as an
    embedded data literal (the failure mode the whole-jit kernel must avoid).
    """
    import jax

    t0 = time.perf_counter()
    closed = jax.make_jaxpr(fn)(*args, **kwargs)
    t_trace = time.perf_counter() - t0
    consts = []
    for cj in _iter_closed_jaxprs(closed):
        for c in getattr(cj, "consts", ()) or ():
            try:
                arr = np.asarray(c)
            except Exception:
                continue
            consts.append(arr)
    by_shape = {}
    for name, a in data_arrays.items():
        a = np.asarray(a)
        by_shape.setdefault((a.shape, a.dtype.str), []).append((name, a))
    embedded = []
    for arr in consts:
        for name, a in by_shape.get((arr.shape, arr.dtype.str), []):
            if arr.size and np.array_equal(arr, a, equal_nan=arr.dtype.kind == "f"):
                embedded.append(name)
    sizes = sorted(((int(a.size), list(a.shape), a.dtype.str) for a in consts), reverse=True)
    return {
        "t_make_jaxpr_s": t_trace,
        "n_consts": len(consts),
        "const_bytes_total": int(sum(a.nbytes for a in consts)),
        "largest_consts": [{"size": s, "shape": sh, "dtype": dt} for s, sh, dt in sizes[:5]],
        "embedded_data_arrays": sorted(set(embedded)),
        "embeds_data_literal": bool(embedded),
        "n_invars": len(closed.jaxpr.invars),
    }


_HEX_LITERAL = re.compile(r'dense<"0x([0-9A-Fa-f]+)">')


def aot_report(jitted, args, kwargs, counter: CompileCounter) -> dict:
    """Trace + lower + compile ``jitted`` from cold in-memory caches.

    ``jax.clear_caches()`` first, otherwise ``lower``/``compile`` are served from
    the executable the timed calls already built. Large array constants are
    printed by MLIR as hex ``dense<"0x...">`` literals; their count and byte
    size are the direct measure of data embedded in the module.
    """
    import jax

    jax.clear_caches()
    snap = counter.snapshot()
    t0 = time.perf_counter()
    lowered = jitted.lower(*args, **kwargs)
    t_lower = time.perf_counter() - t0
    text = lowered.as_text()
    t1 = time.perf_counter()
    lowered.compile()
    t_compile = time.perf_counter() - t1
    hex_lits = [len(m) // 2 for m in _HEX_LITERAL.findall(text)]
    return {
        "t_trace_lower_s": t_lower,
        "t_compile_s": t_compile,
        "lowered_text_bytes": len(text),
        "hex_literals": len(hex_lits),
        "hex_literal_bytes": int(sum(hex_lits)),
        "largest_hex_literal_bytes": int(max(hex_lits)) if hex_lits else 0,
        "compile_counter_delta": counter.delta(snap),
        "note": ("AOT trace/lower/compile after jax.clear_caches(), run after the timed "
                 "section; compile_counter_delta.compiles == 0 means the executable was "
                 "served from the persistent XLA cache."),
    }


# ----------------------------------------------------------------------------
# nvidia-smi log join (gpu_run.sh writes timestamp, memory.used, utilization.gpu)
# ----------------------------------------------------------------------------
def smi_window_stats(smi_log: str, t_start: float, t_end: float) -> dict:
    """Utilisation / memory rows of a gpu_run.sh nvidia-smi log inside a window.

    nvidia-smi timestamps are host-local wall clock without a zone; they are
    parsed as local time. Best effort: returns ``rows == 0`` when nothing falls
    in the window (e.g. the sampler has not flushed yet).
    """
    out = {"path": os.path.abspath(smi_log), "window_unix": [t_start, t_end], "rows": 0}
    try:
        with open(smi_log) as f:
            lines = f.readlines()
    except OSError as exc:
        out["error"] = str(exc)
        return out
    util, mem = [], []
    for line in lines:
        if line.startswith("#") or line.startswith("timestamp"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            ts = _dt.datetime.strptime(parts[0], "%Y/%m/%d %H:%M:%S.%f").timestamp()
        except ValueError:
            continue
        if t_start <= ts <= t_end:
            try:
                mem.append(float(parts[1].split()[0]))
                util.append(float(parts[2].split()[0]))
            except (ValueError, IndexError):
                continue
    out["rows"] = len(util)
    if util:
        out.update(util_pct_mean=float(np.mean(util)), util_pct_median=float(np.median(util)),
                   util_pct_max=float(np.max(util)), mem_used_mib_max=float(np.max(mem)))
    return out


# ----------------------------------------------------------------------------
# JSON
# ----------------------------------------------------------------------------
def _json_default(o):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    return str(o)


def _sanitize(o):
    if isinstance(o, float):
        return fval(o)
    if isinstance(o, dict):
        return {str(k): _sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_sanitize(v) for v in o]
    return o


def write_json(path, obj):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(_sanitize(obj), f, indent=1, default=_json_default, allow_nan=False)
        f.write("\n")
    os.replace(tmp, path)


def read_json(path):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Selection-guard configuration (both adapters)
GUARD_CHOICES = ("default", "hard", "soft")


def add_guard_args(ap):
    """--guard / --max-variance: the sparse-selection N_eff guard of both codes.

    default = each implementation's own default (legacy ``--selection_neff_guard auto``
    resolves to hard for its dynesty sampler; core ``bind_analysis`` soft guard False);
    hard / soft are passed explicitly (legacy ``--selection_neff_guard``, core
    ``bind_analysis(selection_neff_soft_guard=...)``). --max-variance sets
    ``max_likelihood_variance`` in both (legacy ``--max_likelihood_variance``, core
    ``bind_analysis(max_likelihood_variance=...)``); unset = the implementation default.
    """
    ap.add_argument("--guard", choices=GUARD_CHOICES, default="default",
                    help="selection N_eff guard: default (implementation default), hard, soft")
    ap.add_argument("--max-variance", type=float, default=None,
                    help="max_likelihood_variance (cap on sigma^2_lnL); unset = implementation "
                         "default")


def guard_request(a):
    mode = getattr(a, "guard", "default") or "default"
    return {"mode": None if mode == "default" else mode,
            "requested": mode, "max_variance": getattr(a, "max_variance", None)}


def guard_record(req, config):
    """Requested vs resolved guard settings, as stored in ``config.guard``."""
    soft = bool(config.get("selection_neff_soft_guard"))
    return {"requested_mode": req["requested"],
            "requested_max_variance": req["max_variance"],
            "mode": "soft" if soft else "hard",
            "cap": config.get("max_likelihood_variance")}
