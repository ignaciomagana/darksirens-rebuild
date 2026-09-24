#!/usr/bin/env python3
"""Record specs of the Gate 1 spectral fixed-coordinate matrices (for campaign_run.py).

    python gate1_specs.py smoke --out smoke.json
    python gate1_specs.py autoblocks --out auto.json
    python gate1_specs.py matrices --sel-batch N --pe-block M --out gate1.json
    python gate1_specs.py m5 --out m5.json      (supplement M5: GWTC-5-centred coordinates)

record_id = <matrix>_<impl>_<jit>_<blocks>_<plan>_<pe_label>_<sel_label>, impl in
{legacy, core, corepin}. Within each (input, plan) group the legacy records come first,
so every core record can be compared with the legacy record of the same blocks label.
"""

from __future__ import annotations

import argparse
import json

ROOT = "/media/volume/tbs/darksirens_benchmark"
EXP = f"{ROOT}/data/gwcat/exports"
TINY = f"{ROOT}/benchmarks/harness_validation/tiny_fixtures"

PE_A = {"first16_n1024": "A_pe_chieff_first16_n1024_v20.h5",
        "first64_n1024": "A_pe_chieff_first64_n1024_v20.h5",
        "bbh259_n256": "A_pe_chieff_bbh259_n256_v20.h5",
        "bbh259_n1024": "A_pe_chieff_bbh259_n1024_v20.h5",
        "bbh259_n4096": "A_pe_chieff_bbh259_n4096_v20.h5"}
SEL_A = {"stride100": "A_sel_chieffref_o3o4ab_v20_stride100.h5",
         "stride10": "A_sel_chieffref_o3o4ab_v20_stride10.h5",
         "full": "A_sel_chieffref_o3o4ab_v20.h5"}
PE_B = {"B_first16_n1024": "B_pe_component_first16_n1024_v21.h5",
        "B_bbh259_n4096": "B_pe_component_bbh259_n4096_v21.h5"}
SEL_B = {"B_stride100": "B_sel_component_o3o4ab_v21_stride100.h5",
         "B_full": "B_sel_component_o3o4ab_v21.h5"}
PLANS4 = ("spectral_H0", "spectral_pop", "spectral_joint_small", "spectral_full")
IMPL_LABEL = {"legacy": "legacy", "core": "core", "core_pin": "corepin"}


def rid(matrix, env, jit, blocks, plan, pe_label, sel_label):
    return f"{matrix}_{IMPL_LABEL[env]}_{jit}_{blocks}_{plan}_{pe_label}_{sel_label}"


def spec(matrix, env, jit, blocks, plan, pe_label, sel_label, pe, sel, matched=None, **kw):
    if blocks == "matched":
        sb, pb = str(matched[0]), str(matched[1])
    else:
        sb = pb = blocks  # "default" or "none"
    s = {"record_id": rid(matrix, env, jit, blocks, plan, pe_label, sel_label), "matrix": matrix,
         "env": env, "impl": "legacy" if env == "legacy" else "core", "jit": jit, "blocks": blocks,
         "sel_batch": sb, "pe_block": pb, "plan": plan, "pe": pe, "sel": sel, "pe_label": pe_label,
         "sel_label": sel_label, "n_calls": 20, "warmup": 3, "util_window_s": 10, "cache": "cold",
         "compare_to": [], "flags": {}}
    s.update(kw)
    return s


def smoke():
    out = []
    for plan in PLANS4:
        L = spec("SMOKE", "legacy", "whole", "none", plan, "tiny", "tiny", f"{TINY}/pe_chieff.h5",
                 f"{TINY}/sel_chieff.h5", util_window_s=5)
        W = spec("SMOKE", "core", "whole", "none", plan, "tiny", "tiny", f"{TINY}/pe_chieff.h5",
                 f"{TINY}/sel_chieff.h5", util_window_s=5, compare_to=[L["record_id"]])
        S = spec("SMOKE", "core", "asis", "none", plan, "tiny", "tiny", f"{TINY}/pe_chieff.h5",
                 f"{TINY}/sel_chieff.h5", util_window_s=5,
                 compare_to=[L["record_id"], W["record_id"]])
        out += [L, W, S]
    return out


def m1(matched):
    out = []
    for pe_label, sel_label in (("first16_n1024", "stride100"), ("bbh259_n4096", "full")):
        pe, sel = f"{EXP}/{PE_A[pe_label]}", f"{EXP}/{SEL_A[sel_label]}"
        for plan in PLANS4:
            a = dict(plan=plan, pe_label=pe_label, sel_label=sel_label, pe=pe, sel=sel, matched=matched)
            Ld = spec("M1", "legacy", "whole", "default", **a)
            Lm = spec("M1", "legacy", "whole", "matched", compare_to=[Ld["record_id"]], **a)
            Wd = spec("M1", "core", "whole", "default", compare_to=[Ld["record_id"]], **a)
            Wm = spec("M1", "core", "whole", "matched", compare_to=[Lm["record_id"], Wd["record_id"]], **a)
            Sd = spec("M1", "core", "asis", "default", compare_to=[Ld["record_id"], Wd["record_id"]], **a)
            Pd = spec("M1", "core_pin", "whole", "default", compare_to=[Ld["record_id"], Wd["record_id"]], **a)
            out += [Ld, Lm, Wd, Wm, Sd, Pd]
    return out


def m2():
    combos = [(p, s) for p in ("first16_n1024", "first64_n1024", "bbh259_n1024")
              for s in ("stride100", "stride10", "full")]
    combos += [(p, s) for p in ("bbh259_n256", "bbh259_n4096") for s in ("stride100", "stride10", "full")]
    out = []
    for pe_label, sel_label in combos:
        pe, sel = f"{EXP}/{PE_A[pe_label]}", f"{EXP}/{SEL_A[sel_label]}"
        for plan in ("spectral_H0", "spectral_full"):
            a = dict(plan=plan, pe_label=pe_label, sel_label=sel_label, pe=pe, sel=sel)
            Ld = spec("M2", "legacy", "whole", "default", **a)
            Wd = spec("M2", "core", "whole", "default", compare_to=[Ld["record_id"]], **a)
            Sd = spec("M2", "core", "asis", "default", compare_to=[Ld["record_id"], Wd["record_id"]], **a)
            out += [Ld, Wd, Sd]
    return out


def m3():
    out = []
    for pe_label, sel_label in (("B_first16_n1024", "B_stride100"), ("B_bbh259_n4096", "B_full")):
        a = dict(plan="spectral_full_component", pe_label=pe_label, sel_label=sel_label,
                 pe=f"{EXP}/{PE_B[pe_label]}", sel=f"{EXP}/{SEL_B[sel_label]}")
        Ld = spec("M3", "legacy", "whole", "default", **a)
        Wd = spec("M3", "core", "whole", "default", compare_to=[Ld["record_id"]], **a)
        out += [Ld, Wd]
    return out


def m4(matched):
    pe, sel = f"{EXP}/{PE_A['bbh259_n4096']}", f"{EXP}/{SEL_A['full']}"
    a = dict(plan="spectral_full", pe_label="bbh259_n4096", sel_label="full", pe=pe, sel=sel)
    cold_L = rid("M1", "legacy", "whole", "default", "spectral_full", "bbh259_n4096", "full")
    cold_W = rid("M1", "core", "whole", "default", "spectral_full", "bbh259_n4096", "full")
    Lw = spec("M4", "legacy", "whole", "default", cache={"warm_from": cold_L}, compare_to=[cold_L],
              flags={"warm_cache": True}, **a)
    Lw["record_id"] += "_warm"
    Ww = spec("M4", "core", "whole", "default", cache={"warm_from": cold_W},
              compare_to=[cold_W, cold_L], flags={"warm_cache": True}, **a)
    Ww["record_id"] += "_warm"
    pe16, sel100 = f"{EXP}/{PE_A['first16_n1024']}", f"{EXP}/{SEL_A['stride100']}"
    Sm = spec("M4", "core", "asis", "matched", "spectral_full", "first16_n1024", "stride100", pe16, sel100,
              matched=matched, n_calls=5,
              compare_to=[rid("M1", "legacy", "whole", "matched", "spectral_full", "first16_n1024",
                              "stride100"),
                          rid("M1", "core", "whole", "matched", "spectral_full", "first16_n1024",
                              "stride100")],
              flags={"documents": "core as-shipped per-call recompilation and RSS growth"})
    return [Lw, Ww, Sm]


#: Gate 1 supplement M5 (spectral, real data, finite totals): coordinates centred on
#: H0 = 67.74 + the GWTC-5 fixed-population preset (make_coords.py --center gwtc5
#: --spread 0.05; the preset is checked identical in both implementations first).
M5_COORDS = {"coords_tag": "gwtc5c05", "coords_args": ["--center", "gwtc5", "--spread", "0.05"]}


def m5():
    out = []
    for pe_label, sel_label in (("bbh259_n4096", "full"), ("bbh259_n1024", "stride10")):
        pe, sel = f"{EXP}/{PE_A[pe_label]}", f"{EXP}/{SEL_A[sel_label]}"
        for plan in ("spectral_H0_gwtc5", "spectral_full_gwtc5"):
            a = dict(plan=plan, pe_label=pe_label, sel_label=sel_label, pe=pe, sel=sel, **M5_COORDS)
            Ld = spec("M5", "legacy", "whole", "default", **a)
            Wd = spec("M5", "core", "whole", "default", compare_to=[Ld["record_id"]], **a)
            Sd = spec("M5", "core", "asis", "default", compare_to=[Ld["record_id"], Wd["record_id"]], **a)
            out += [Ld, Wd, Sd]
    return out


def _matched(v):
    v = str(v).strip().lower()
    if v == "none":
        return v
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError("block size must be >= 1 or 'none'")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("smoke", "autoblocks", "matrices", "m5"))
    # The matched blocks are what legacy's auto sizing resolves on the A100 for
    # 259 x 4096 x 1,067,946: an int, or 'none' when it resolves to a single pass
    # (legacy block_sizing.resolve_block_sizes returns (None, None) when the single
    # pass fits; 'none' = legacy --sel_batch_size/--pe_event_block off, core None).
    ap.add_argument("--sel-batch", type=_matched)
    ap.add_argument("--pe-block", type=_matched)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.what == "smoke":
        specs = smoke()
    elif a.what == "m5":
        specs = m5()
    elif a.what == "autoblocks":
        pe, sel = f"{EXP}/{PE_A['bbh259_n4096']}", f"{EXP}/{SEL_A['full']}"
        specs = [spec("M1", "legacy", "whole", "default", "spectral_full", "bbh259_n4096", "full", pe, sel)]
    else:
        if a.sel_batch is None or a.pe_block is None:
            ap.error("matrices needs --sel-batch and --pe-block (int or 'none')")
        matched = (a.sel_batch, a.pe_block)
        specs = m1(matched) + m2() + m3() + m4(matched)
    ids = [s["record_id"] for s in specs]
    assert len(ids) == len(set(ids)), "duplicate record ids"
    with open(a.out, "w") as f:
        json.dump(specs, f, indent=1)
    print(f"{len(specs)} specs -> {a.out}")


if __name__ == "__main__":
    main()
