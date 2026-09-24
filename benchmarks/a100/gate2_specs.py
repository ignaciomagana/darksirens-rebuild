#!/usr/bin/env python3
"""Record specs of Gate 2 (mock dark sirens, fixtures T and S) for campaign_run.py.

    python gate2_specs.py smoke --out smoke.json
    python gate2_specs.py matrix --sel-batch 4096 --pe-block 6 --out gate2.json

record_id = <matrix>_<impl>_<jit>_<blocks>_<plan>_<fixture>[_<tag>], impl in {legacy, core,
corepin}. Matrices (Fable's G2-run task):

* G2A: fixtures {T, S} x the six dark plans x {legacy default, core whole default, core asis
  default}; core whole is compared with legacy, core asis with legacy and with core whole.
* G2B: core_pin whole default on S x {dark_H0, dark_full}; compared with the legacy and the
  core whole G2A records of the same cell.
* G2C: blocked parity on S dark_full at the explicit (sel_batch, pe_event_block) that H2
  validated on CPU (4096, 6), {legacy, core whole, core asis}; legacy blocked vs legacy
  default, core whole blocked vs legacy blocked and vs core whole default, core asis blocked
  vs legacy blocked and vs core whole blocked. Parity check; timing recorded, not headline.
* G2D: PR-6a density n0 = 5e-5 (log10n0 = math.log10(5e-5)) pinned on fixture T dark_H0 in
  legacy and core whole at the G2A coordinates (the same coords/dark_H0.json);
  core whole vs legacy. A fixed-coordinate check, never a sampled run.

Within a group the reference records come first, so every comparison has its A record.
"""

from __future__ import annotations

import argparse
import json
import math

ROOT = "/media/volume/tbs/darksirens_benchmark"
MOCK = f"{ROOT}/data/mock"
FIXTURES = {"T": 16, "S": 32}  # fixture -> nside of its pixelated catalog
DARK_PLANS = ("dark_H0", "dark_pop", "dark_survey", "dark_joint_cosmo_pop",
              "dark_joint_cosmo_survey", "dark_full")
IMPL_LABEL = {"legacy": "legacy", "core": "core", "core_pin": "corepin"}
LOG10_N0_PR6A = math.log10(5e-5)  # -4.301029995663981, as H2 (run_n0_5e5.sh)


def fixture_paths(fx):
    d = f"{MOCK}/{fx}"
    return {"pe": f"{d}/mock_gw_events.h5", "sel": f"{d}/mock_gw_selection.h5",
            "catalog": f"{d}/catalog_pixelated_nside_{FIXTURES[fx]}.h5"}


def rid(matrix, env, jit, blocks, plan, fx, tag=None):
    s = f"{matrix}_{IMPL_LABEL[env]}_{jit}_{blocks}_{plan}_{fx}"
    return f"{s}_{tag}" if tag else s


def spec(matrix, env, jit, plan, fx, blocks="default", sel_batch="default", pe_block="default",
         tag=None, **kw):
    p = fixture_paths(fx)
    s = {"record_id": rid(matrix, env, jit, blocks, plan, fx, tag), "matrix": matrix, "env": env,
         "impl": "legacy" if env == "legacy" else "core", "jit": jit, "blocks": blocks,
         "sel_batch": str(sel_batch), "pe_block": str(pe_block), "plan": plan,
         "pe": p["pe"], "sel": p["sel"], "catalog": p["catalog"], "pe_label": fx, "sel_label": fx,
         "fixture": fx, "n_calls": 20, "warmup": 3, "util_window_s": 10, "cache": "cold",
         "compare_to": [], "flags": {}}
    s.update(kw)
    return s


def smoke():
    L = spec("G2SMOKE", "legacy", "whole", "dark_H0", "T")
    W = spec("G2SMOKE", "core", "whole", "dark_H0", "T", compare_to=[L["record_id"]])
    S = spec("G2SMOKE", "core", "asis", "dark_H0", "T", compare_to=[L["record_id"], W["record_id"]])
    return [L, W, S]


def g2a():
    out = []
    for fx in ("T", "S"):
        for plan in DARK_PLANS:
            L = spec("G2A", "legacy", "whole", plan, fx)
            W = spec("G2A", "core", "whole", plan, fx, compare_to=[L["record_id"]])
            S = spec("G2A", "core", "asis", plan, fx, compare_to=[L["record_id"], W["record_id"]])
            out += [L, W, S]
    return out


def g2b():
    out = []
    for plan in ("dark_H0", "dark_full"):
        out.append(spec("G2B", "core_pin", "whole", plan, "S",
                        compare_to=[rid("G2A", "legacy", "whole", "default", plan, "S"),
                                    rid("G2A", "core", "whole", "default", plan, "S")]))
    return out


def g2c(sel_batch, pe_block):
    blk = f"b{sel_batch}x{pe_block}"
    kw = dict(blocks=blk, sel_batch=sel_batch, pe_block=pe_block,
              flags={"blocked_parity_check": True, "headline_timing": False})
    L = spec("G2C", "legacy", "whole", "dark_full", "S",
             compare_to=[rid("G2A", "legacy", "whole", "default", "dark_full", "S")], **kw)
    W = spec("G2C", "core", "whole", "dark_full", "S",
             compare_to=[L["record_id"], rid("G2A", "core", "whole", "default", "dark_full", "S")],
             **kw)
    S = spec("G2C", "core", "asis", "dark_full", "S", compare_to=[L["record_id"], W["record_id"]],
             **kw)
    return [L, W, S]


def g2d():
    ovr = json.dumps({"log10n0": LOG10_N0_PR6A})
    extra = ["--survey-fixed-override", ovr, "--allow-out-of-prior-fixed-survey"]
    kw = dict(tag="n0_5e-5", extra_args=extra,
              flags={"pr6a_density": {"n0": 5e-5, "log10n0": LOG10_N0_PR6A},
                     "never_a_sampled_run": True})
    L = spec("G2D", "legacy", "whole", "dark_H0", "T", **kw)
    W = spec("G2D", "core", "whole", "dark_H0", "T", compare_to=[L["record_id"]], **kw)
    return [L, W]


def _block(v):
    v = str(v).strip().lower()
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError("block size must be >= 1")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("smoke", "matrix"))
    ap.add_argument("--sel-batch", type=_block, help="G2C explicit sel_batch_size (H2: 4096)")
    ap.add_argument("--pe-block", type=_block, help="G2C explicit pe_event_block (H2: 6)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.what == "smoke":
        specs = smoke()
    else:
        if a.sel_batch is None or a.pe_block is None:
            ap.error("matrix needs --sel-batch and --pe-block (the H2-validated explicit blocks)")
        specs = g2a() + g2b() + g2c(a.sel_batch, a.pe_block) + g2d()
    ids = [s["record_id"] for s in specs]
    assert len(ids) == len(set(ids)), "duplicate record ids"
    with open(a.out, "w") as f:
        json.dump(specs, f, indent=1)
    print(f"{len(specs)} specs -> {a.out}")


if __name__ == "__main__":
    main()
