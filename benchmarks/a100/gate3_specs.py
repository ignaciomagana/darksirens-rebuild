#!/usr/bin/env python3
"""Record specs of the Gate 1 supplement M5b and Gate 3 (realistic mocks) for campaign_run.py.

    python gate3_specs.py smoke   --out smoke.json      # fixture T, components --trace (GPU path)
    python gate3_specs.py m5b     --out m5b.json        # OUT = benchmarks/gate1/m5b
    python gate3_specs.py g3      --out g3.json         # OUT = benchmarks/gate3 (G3-A, G3-B)
    python gate3_specs.py g3c     --out g3c.json        # OUT = benchmarks/gate3 (components)

Guard variants (Fable's D-guard): ``soft1`` = --guard soft --max-variance 1.0,
``hard10`` = --guard hard --max-variance 10; no tag = each implementation's default
(hard, 1.0). Every comparison is guard-matched (compare_records refuses otherwise).

* M5b: {A bbh259_n4096 + A full, A bbh259_n1024 + A stride10} x {spectral_H0_gwtc5,
  spectral_full_gwtc5} x {soft1, hard10} x {legacy, core whole, core asis} default blocks;
  coordinates = M5's (tag gwtc5c05; copy M5's coords/ into OUT/coords/ first).
* G3-A: {R1, R2, R3, RC} x {dark_H0, dark_full} x {legacy, core whole} default; core asis
  dark_full on all four (n_calls 10); core_pin whole R2 dark_full.
* G3-B: dark_full soft1 on all four x {legacy, core whole}; hard10 on R1 x {legacy, core whole}.
* G3-C: bench_components.py --trace (main record = the G3-A record of the cell) on
  {R1, R2, RC} x {dark_H0, dark_full} x {legacy, core}; spectral_full_gwtc5 on the two M5
  inputs x {legacy, core} (main record = the M5 record; coords tag gwtc5c05).
"""

from __future__ import annotations

import argparse
import json

import gate1_specs as g1
import gate2_specs as g2

ROOT = g1.ROOT
MOCK = f"{ROOT}/data/mock"
NSIDE = {"T": 16, "R1": 64, "R2": 128, "R3": 128, "RC": 256}
GUARDS = {"soft1": {"guard": "soft", "max_variance": 1.0},
          "hard10": {"guard": "hard", "max_variance": 10.0}}
M5_RECORDS = f"{ROOT}/benchmarks/gate1/m5/records"
M5_INPUTS = (("bbh259_n4096", "full"), ("bbh259_n1024", "stride10"))


def fx_paths(fx):
    d = f"{MOCK}/{fx}"
    return {"pe": f"{d}/mock_gw_events.h5", "sel": f"{d}/mock_gw_selection.h5",
            "catalog": f"{d}/catalog_pixelated_nside_{NSIDE[fx]}.h5"}


def dspec(matrix, env, jit, plan, fx, guard=None, tag=None, **kw):
    p = fx_paths(fx)
    t = "_".join(x for x in (guard, tag) if x) or None
    s = {"record_id": g2.rid(matrix, env, jit, "default", plan, fx, t), "matrix": matrix,
         "env": env, "impl": "legacy" if env == "legacy" else "core", "jit": jit,
         "blocks": "default", "sel_batch": "default", "pe_block": "default", "plan": plan,
         "pe": p["pe"], "sel": p["sel"], "catalog": p["catalog"], "pe_label": fx,
         "sel_label": fx, "fixture": fx, "n_calls": 20, "warmup": 3, "util_window_s": 10,
         "cache": "cold", "compare_to": [], "flags": {}}
    if guard:
        s.update(GUARDS[guard])
        s["flags"]["guard_variant"] = guard
    s.update(kw)
    return s


def smoke():
    out = []
    for impl, env in (("legacy", "legacy"), ("core", "core")):
        M = dspec("G3SMOKE", env, "whole", "dark_full", "T")
        out.append(M)
    L, W = out
    W["compare_to"] = [L["record_id"]]
    comps = []
    for M in (L, W):
        C = dict(M, record_id=M["record_id"].replace("G3SMOKE_", "G3SMOKE_comp_"),
                 tool="components", trace=True, compare_to=[],
                 main_record=f"@OUT/records/{M['record_id']}.json")
        comps.append(C)
    comps[1]["compare_to"] = [comps[0]["record_id"]]
    return [L, W] + comps


def m5b():
    out = []
    for pe_label, sel_label in M5_INPUTS:
        pe, sel = f"{g1.EXP}/{g1.PE_A[pe_label]}", f"{g1.EXP}/{g1.SEL_A[sel_label]}"
        for plan in ("spectral_H0_gwtc5", "spectral_full_gwtc5"):
            for guard, gkw in GUARDS.items():
                a = dict(plan=plan, pe_label=pe_label, sel_label=sel_label, pe=pe, sel=sel,
                         **g1.M5_COORDS, **gkw)
                Ld = g1.spec("M5B", "legacy", "whole", "default", **a)
                Wd = g1.spec("M5B", "core", "whole", "default", compare_to=[Ld["record_id"]], **a)
                Sd = g1.spec("M5B", "core", "asis", "default",
                             compare_to=[Ld["record_id"], Wd["record_id"]], **a)
                for s in (Ld, Wd, Sd):
                    s["record_id"] += f"_{guard}"
                    s["flags"] = {"guard_variant": guard}
                Wd["compare_to"] = [Ld["record_id"]]
                Sd["compare_to"] = [Ld["record_id"], Wd["record_id"]]
                out += [Ld, Wd, Sd]
    return out


def g3a():
    out = []
    for fx in ("R1", "R2", "R3", "RC"):
        for plan in ("dark_H0", "dark_full"):
            L = dspec("G3A", "legacy", "whole", plan, fx)
            W = dspec("G3A", "core", "whole", plan, fx, compare_to=[L["record_id"]])
            out += [L, W]
            if plan == "dark_full":
                out.append(dspec("G3A", "core", "asis", plan, fx, n_calls=10,
                                 compare_to=[L["record_id"], W["record_id"]]))
                if fx == "R2":
                    out.append(dspec("G3A", "core_pin", "whole", plan, fx,
                                     compare_to=[L["record_id"], W["record_id"]]))
    return out


def g3b():
    out = []
    for fx in ("R1", "R2", "R3", "RC"):
        L = dspec("G3B", "legacy", "whole", "dark_full", fx, guard="soft1")
        W = dspec("G3B", "core", "whole", "dark_full", fx, guard="soft1", compare_to=[L["record_id"]])
        out += [L, W]
    L = dspec("G3B", "legacy", "whole", "dark_full", "R1", guard="hard10")
    W = dspec("G3B", "core", "whole", "dark_full", "R1", guard="hard10", compare_to=[L["record_id"]])
    return out + [L, W]


def g3c():
    out = []
    for fx in ("R1", "R2", "RC"):
        for plan in ("dark_H0", "dark_full"):
            pair = []
            for env in ("legacy", "core"):
                main = dspec("G3A", env, "whole", plan, fx)["record_id"]
                C = dspec("G3C", env, "whole", plan, fx, tool="components", trace=True,
                          main_record=f"@OUT/records/{main}.json")
                pair.append(C)
            pair[1]["compare_to"] = [pair[0]["record_id"]]
            out += pair
    for pe_label, sel_label in M5_INPUTS:
        pe, sel = f"{g1.EXP}/{g1.PE_A[pe_label]}", f"{g1.EXP}/{g1.SEL_A[sel_label]}"
        plan = "spectral_full_gwtc5"
        pair = []
        for env in ("legacy", "core"):
            main = g1.rid("M5", env, "whole", "default", plan, pe_label, sel_label)
            C = g1.spec("G3C", env, "whole", "default", plan=plan, pe_label=pe_label,
                        sel_label=sel_label, pe=pe, sel=sel, **g1.M5_COORDS, tool="components",
                        trace=True, main_record=f"{M5_RECORDS}/{main}.json")
            pair.append(C)
        pair[1]["compare_to"] = [pair[0]["record_id"]]
        out += pair
    return out


def retry(sel_batch, pe_block, fixtures=("R2", "R3", "RC")):
    """OOM policy: every G3-A / G3-B cell of ``fixtures`` again at explicit blocks
    (sel_batch, pe_block), tag ``b<sel>x<pe>``; comparisons as in g3a/g3b, against the
    legacy record of the same cell at the same blocks and guard."""
    blk = f"b{sel_batch}x{pe_block}"
    kw = dict(blocks=blk, sel_batch=str(sel_batch), pe_block=str(pe_block))

    def fix(s):
        s.update(kw)
        s["record_id"] = s["record_id"].replace("_default_", f"_{blk}_")
        s["compare_to"] = [c.replace("_default_", f"_{blk}_") for c in s["compare_to"]]
        s["flags"] = dict(s.get("flags") or {}, oom_retry_of=s["record_id"].replace(f"_{blk}_", "_default_"))
        return s
    out = [fix(s) for s in g3a() + g3b() if s["fixture"] in fixtures]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("smoke", "m5b", "g3", "g3c", "retry"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--sel-batch", type=int, default=4096)
    ap.add_argument("--pe-block", type=int, default=6)
    ap.add_argument("--fixtures", default="R2,R3,RC")
    a = ap.parse_args(argv)
    specs = {"smoke": smoke, "m5b": m5b, "g3": lambda: g3a() + g3b(), "g3c": g3c,
             "retry": lambda: retry(a.sel_batch, a.pe_block, tuple(a.fixtures.split(",")))}[a.what]()
    ids = [s["record_id"] for s in specs]
    assert len(ids) == len(set(ids)), "duplicate record ids"
    with open(a.out, "w") as f:
        json.dump(specs, f, indent=1)
    print(f"{len(specs)} specs -> {a.out}")


if __name__ == "__main__":
    main()
