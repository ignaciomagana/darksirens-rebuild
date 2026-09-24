#!/usr/bin/env python3
"""Gate 4 (candidate O1) kernel matrix: campaign_run.py specs and the coordinate files.

    python gate4_specs.py --out SPEC.json [--coords-dir OUT/coords]

Every cell is run in four arms, one record each, strictly in this order so the O1 records
can be compared with the core-main whole record made in the same session:

    main_whole (env core, jit whole) -> main_asis (env core, jit asis)
    -> o1_asis (env core_o1, jit asis) -> o1_whole (env core_o1, jit whole)

All records: n-calls 50, warm-up 3, --steady-window 30, util window 10 s, cold empty
cache per record (D-cache), seed 20260924. Cells and their existing references (the
SAME coordinate files as those references; --coords-dir copies them in as
<plan>__<tag>.json, which campaign_run.py then uses unchanged):

* Gate 1 M1: {A first16_n1024 + stride100, A bbh259_n4096 + full} x {spectral_H0,
  spectral_full}, default blocks, default guard; legacy gate1/records/M1_legacy_whole_default_*;
* M5b: A bbh259_n4096 + full x {spectral_H0_gwtc5, spectral_full_gwtc5}, soft guard at
  max variance 1.0; legacy gate1/m5b/records/M5B_legacy_whole_default_*_soft1;
* Gate 2: {T, S} x dark_full, default blocks; legacy gate2/records/G2A_legacy_whole_default_*;
* Gate 3: R1 dark_full, default blocks; legacy gate3/records/G3A_legacy_whole_default_dark_full_R1;
  R2 {dark_H0, dark_full}, blocks 4096/6, default allocator, --catalog-npz digest;
  legacy gate3/retries/records/G3R_legacy_whole_b4096x6_*_R2_rc2048 (legacy --row_chunk 2048).

compare_to: every record against its legacy reference (A = legacy); the O1 records also
against the main_whole record of this matrix.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil

ROOT = "/media/volume/tbs/darksirens_benchmark"
B = f"{ROOT}/benchmarks"
EXP = f"{ROOT}/data/gwcat/exports"
MOCK = f"{ROOT}/data/mock"

PE16, SEL100 = f"{EXP}/A_pe_chieff_first16_n1024_v20.h5", f"{EXP}/A_sel_chieffref_o3o4ab_v20_stride100.h5"
PE4096, SELFULL = f"{EXP}/A_pe_chieff_bbh259_n4096_v20.h5", f"{EXP}/A_sel_chieffref_o3o4ab_v20.h5"

# (cell, plan, pe, sel, pe_label, sel_label, catalog, sel_batch, pe_block, guard, max_var,
#  coords source, coords tag, legacy reference record, extra args)
CELLS = []
for inp, pe, sel, pl, sl in (("A16s100", PE16, SEL100, "first16_n1024", "stride100"),
                             ("A4096full", PE4096, SELFULL, "bbh259_n4096", "full")):
    for plan in ("spectral_H0", "spectral_full"):
        CELLS.append(dict(cell=inp, plan=plan, pe=pe, sel=sel, pe_label=pl, sel_label=sl,
                          blocks=("default", "default"), coords=f"{B}/gate1/coords/{plan}.json",
                          tag="g1", legacy=f"{B}/gate1/records/M1_legacy_whole_default_{plan}_{pl}_{sl}.json",
                          matrix="G4-M1"))
for plan in ("spectral_H0_gwtc5", "spectral_full_gwtc5"):
    CELLS.append(dict(cell="A4096full", plan=plan, pe=PE4096, sel=SELFULL, pe_label="bbh259_n4096",
                      sel_label="full", blocks=("default", "default"), guard="soft", max_variance=1.0,
                      coords=f"{B}/gate1/m5b/coords/{plan}__gwtc5c05.json", tag="gwtc5c05",
                      legacy=f"{B}/gate1/m5b/records/M5B_legacy_whole_default_{plan}_bbh259_n4096_full_soft1.json",
                      matrix="G4-M5b", suffix="_soft1"))
for fx, ns in (("T", 16), ("S", 32)):
    CELLS.append(dict(cell=fx, plan="dark_full", pe=f"{MOCK}/{fx}/mock_gw_events.h5",
                      sel=f"{MOCK}/{fx}/mock_gw_selection.h5", pe_label=fx, sel_label=fx, fixture=fx,
                      catalog=f"{MOCK}/{fx}/catalog_pixelated_nside_{ns}.h5", blocks=("default", "default"),
                      coords=f"{B}/gate2/coords/dark_full.json", tag="g2",
                      legacy=f"{B}/gate2/records/G2A_legacy_whole_default_dark_full_{fx}.json", matrix="G4-G2"))
CELLS.append(dict(cell="R1", plan="dark_full", pe=f"{MOCK}/R1/mock_gw_events.h5",
                  sel=f"{MOCK}/R1/mock_gw_selection.h5", pe_label="R1", sel_label="R1", fixture="R1",
                  catalog=f"{MOCK}/R1/catalog_pixelated_nside_64.h5", blocks=("default", "default"),
                  coords=f"{B}/gate3/coords/dark_full.json", tag="g3",
                  legacy=f"{B}/gate3/records/G3A_legacy_whole_default_dark_full_R1.json", matrix="G4-G3"))
for plan in ("dark_H0", "dark_full"):
    CELLS.append(dict(cell="R2", plan=plan, pe=f"{MOCK}/R2/mock_gw_events.h5",
                      sel=f"{MOCK}/R2/mock_gw_selection.h5", pe_label="R2", sel_label="R2", fixture="R2",
                      catalog=f"{MOCK}/R2/catalog_pixelated_nside_128.h5", blocks=("4096", "6"),
                      coords=f"{B}/gate3/coords/{plan}.json", tag="g3",
                      legacy=f"{B}/gate3/retries/records/G3R_legacy_whole_b4096x6_{plan}_R2_rc2048.json",
                      matrix="G4-G3", extra=["--catalog-npz", "digest"]))

ARMS = (("main", "whole", "core"), ("main", "asis", "core"), ("o1", "asis", "core_o1"),
        ("o1", "whole", "core_o1"))


def rid(arm, jit, c):
    blk = "default" if c["blocks"] == ("default", "default") else f"b{c['blocks'][0]}x{c['blocks'][1]}"
    return f"G4_{arm}_{jit}_{blk}_{c['plan']}_{c['cell']}{c.get('suffix', '')}"


def specs():
    out = []
    for c in CELLS:
        main_whole = rid("main", "whole", c)
        for arm, jit, env in ARMS:
            sp = {"record_id": rid(arm, jit, c), "matrix": c["matrix"], "env": env, "impl": "core",
                  "jit": jit, "blocks": "default" if c["blocks"] == ("default", "default") else "explicit",
                  "sel_batch": c["blocks"][0], "pe_block": c["blocks"][1], "plan": c["plan"],
                  "pe": c["pe"], "sel": c["sel"], "pe_label": c["pe_label"], "sel_label": c["sel_label"],
                  "fixture": c.get("fixture", c["cell"]), "n_calls": 50, "warmup": 3, "util_window_s": 10,
                  "cache": "cold", "coords_tag": c["tag"],
                  "compare_to": [c["legacy"]] + ([main_whole] if arm == "o1" else []),
                  "extra_args": ["--steady-window", "30"] + list(c.get("extra") or []),
                  "flags": {"gate4_arm": arm, "gate4_cell": c["cell"], "coords_source": c["coords"],
                            "legacy_reference": c["legacy"]}}
            if c.get("catalog"):
                sp["catalog"] = c["catalog"]
            if c.get("guard"):
                sp["guard"], sp["max_variance"] = c["guard"], c["max_variance"]
            out.append(sp)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--coords-dir", default=None,
                    help="copy each cell's reference coordinate file here as <plan>__<tag>.json")
    a = ap.parse_args(argv)
    sp = specs()
    with open(a.out, "w") as f:
        json.dump(sp, f, indent=1)
    if a.coords_dir:
        os.makedirs(a.coords_dir, exist_ok=True)
        for c in CELLS:
            dst = os.path.join(a.coords_dir, f"{c['plan']}__{c['tag']}.json")
            if not os.path.exists(dst):
                shutil.copy2(c["coords"], dst)
    print(f"{len(sp)} specs -> {a.out}")


if __name__ == "__main__":
    main()
