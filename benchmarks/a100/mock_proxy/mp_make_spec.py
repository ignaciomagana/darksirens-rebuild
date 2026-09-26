#!/usr/bin/env python3
"""Parity-precondition spec of the mock-proxy ladder (campaign_run.py format). Usage: mp_make_spec.py OUT.json"""
import json
import sys

ROOT = "/media/volume/tbs/darksirens_benchmark"
FIX = {"R1": ("catalog_pixelated_nside_64.h5", "none", "none", []),
       "R2": ("catalog_pixelated_nside_128.h5", "4096", "6", ["--catalog-npz", "digest"])}
specs = []
for fx, (cat, sb, pb, extra) in FIX.items():
    d = f"{ROOT}/data/mock/{fx}"
    blocks = "single" if sb == "none" else f"b{sb}x{pb}"
    for plan in ("dark_H0", "dark_full"):
        ids = {}
        for impl, jit, env in (("legacy", "whole", "legacy"), ("core", "asis", "core")):
            rid = f"MPP_{impl}_{jit}_{blocks}_{plan}_{fx}_soft10"
            ids[impl] = rid
            x = list(extra)
            if impl == "legacy" and fx == "R2":
                x += ["--row-chunk", "2048"]
            specs.append({
                "record_id": rid, "matrix": "MP-parity", "env": env, "impl": impl, "jit": jit,
                "blocks": blocks, "sel_batch": sb, "pe_block": pb, "plan": plan,
                "pe": f"{d}/mock_gw_events.h5", "sel": f"{d}/mock_gw_selection.h5",
                "catalog": f"{d}/{cat}", "pe_label": fx, "sel_label": fx, "fixture": fx,
                "n_calls": 3, "warmup": 3, "util_window_s": 10, "cache": "cold",
                "guard": "soft", "max_variance": 10.0,
                "compare_to": [ids["legacy"]] if impl == "core" else [],
                "extra_args": x, "flags": {}})
json.dump(specs, open(sys.argv[1], "w"), indent=1)
print(f"{len(specs)} specs -> {sys.argv[1]}")
