#!/usr/bin/env python3
"""Gate 3 / M5b tables: one CSV row per main record, one per component of a components record.

    python gate3_table.py matrix --outdir OUT [--outdir OUT2] --csv gate3_matrix.csv \\
        [--json rows.json] [--order SPEC] [--extra-rows EXTRA.json]
    python gate3_table.py components --outdir OUT --csv components_matrix.csv [--json rows.json]

matrix: gate2_table.COLUMNS (Gate 1 columns + catalog dims) plus guard_mode, guard_cap
(the RESOLVED values stored in the record's config), n_calls, n_coords and
finite_total_count (coordinates whose total logL is finite). parity_vs_legacy /
D-mcvar / D-catvals as in gate2_table; an n_eff-only failure is 'fail' with
``neff`` detail in the JSON rows (the D-neff2 evidence is assembled separately).

components: record, impl, fixture, plan, component, warm_median_s, compile_s (the AOT
XLA compile), first_call_s, parity_1e12 / max_rel / criterion (from the components
compare of the pair, legacy = A), share_of_whole (warm median / i_whole warm median of
the same record; informational: components are separate kernels).
"""

from __future__ import annotations

import argparse
import csv
import json
import os

import gate2_table as g2

COLUMNS = g2.COLUMNS + ["guard_mode", "guard_cap", "n_calls", "n_coords", "finite_total_count"]
COMP_COLUMNS = ["record", "impl", "fixture", "plan", "component", "available", "kind",
                "warm_median_s", "compile_s", "first_call_s", "timed_loop_compiles",
                "parity_1e12", "criterion", "max_rel", "worst_key", "catvals_max_abs",
                "share_of_whole", "share_ref", "status"]


def _load(p):
    if not p or not os.path.isfile(p):
        return None
    with open(p) as f:
        return json.load(f)


def matrix_rows(entries, ids):
    rows, extras = [], []
    for i in ids:
        e = entries[i]
        if (e["spec"].get("tool") == "components"):
            continue
        r2, ex = g2.row_for(e, entries, None)
        r = {c: r2.get(c, "") for c in COLUMNS}
        sp = e["spec"]
        r["n_calls"] = sp.get("n_calls", 20)
        rec = _load(e.get("record"))
        if rec is not None and rec.get("status") == "ok":
            cfg = rec["config"]
            r["guard_mode"] = "soft" if cfg.get("selection_neff_soft_guard") else "hard"
            r["guard_cap"] = cfg.get("max_likelihood_variance")
            pcs = rec["values"]["per_coord"]
            r["n_coords"] = len(pcs)
            r["finite_total_count"] = sum(1 for pc in pcs if pc["total_finite"])
        else:
            r["guard_mode"] = sp.get("guard") or "hard(default)"
            r["guard_cap"] = sp.get("max_variance") if sp.get("max_variance") is not None else "1.0(default)"
        rows.append(r)
        extras.append(ex)
    return rows, extras


def component_rows(entries, ids):
    rows = []
    for i in ids:
        e = entries[i]
        sp = e["spec"]
        if sp.get("tool") != "components":
            continue
        rec = _load(e.get("record"))
        fixture = sp.get("fixture") or f"{sp.get('pe_label')}+{sp.get('sel_label')}"
        base = {"record": i, "impl": sp["env"], "fixture": fixture, "plan": sp["plan"],
                "status": e["status"]}
        if rec is None or rec.get("status") != "ok":
            rows.append(dict(base, component="(record)"))
            continue
        # the pair's compare (legacy = A): this record's own, or the one naming it as A
        cmp_ = None
        for ent in entries.values():
            for ref, c in (ent.get("compares") or {}).items():
                if ref == i or ent["record_id"] == i:
                    cmp_ = _load(c.get("summary"))
        crow = {r["component"]: r for r in (cmp_ or {}).get("rows", [])}
        comps = rec["components"]
        whole = ((comps.get("i_whole") or {}).get("timing") or {}).get("warm") or {}
        wm = whole.get("median_s")
        whole_src = "i_whole of this record"
        if wm is None:  # split record: the whole-kernel median of its main record, if ok
            mr = _load(sp.get("main_record", "").replace("@OUT", os.path.dirname(os.path.dirname(e["record"]))))
            if mr is not None and mr.get("status") == "ok":
                wm = mr["timing"]["warm"]["median_s"]
                whole_src = "main record warm median"
        for name in rec.get("component_order") or list(comps):
            c = comps[name]
            if c.get("reason") == "not selected (--components)":
                continue
            t = c.get("timing") or {}
            warm = t.get("warm") or {}
            cr = crow.get(name) or {}
            med = warm.get("median_s")
            rows.append(dict(
                base, component=name, available=c.get("available"), kind=c.get("kind"),
                warm_median_s=med, compile_s=(c.get("aot") or {}).get("t_compile_s"),
                first_call_s=t.get("t_first_call_s"),
                timed_loop_compiles=(t.get("timed_loop_compile") or {}).get("requests"),
                parity_1e12=cr.get("parity_1e12"), criterion=cr.get("criterion"),
                max_rel=cr.get("max_rel"), worst_key=cr.get("worst_key"),
                catvals_max_abs=cr.get("catvals_max_abs"),
                share_of_whole=(med / wm if (med is not None and wm) else None),
                share_ref=whole_src if wm else None))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("matrix", "components"))
    ap.add_argument("--outdir", action="append", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--order", action="append", default=None)
    ap.add_argument("--extra-rows", default=None)
    a = ap.parse_args(argv)
    entries = {}
    for d in a.outdir:
        entries.update(_load(os.path.join(d, "index.json"))["runs"])
    ids = list(entries)
    if a.order:
        order = [s["record_id"] for f in a.order for s in _load(f)]
        ids = [i for i in order if i in entries] + [i for i in ids if i not in order]
    if a.what == "matrix":
        rows, extras = matrix_rows(entries, ids)
        if a.extra_rows:
            for r in _load(a.extra_rows):
                rows.append({c: r.get(c, "") for c in COLUMNS})
        cols = COLUMNS
        doc = {"columns": COLUMNS, "rows": rows, "extra": extras}
    else:
        rows = component_rows(entries, ids)
        cols = COMP_COLUMNS
        doc = {"columns": COMP_COLUMNS, "rows": rows}
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(doc, f, indent=1, default=str)
    print(f"{len(rows)} rows -> {a.csv}")


if __name__ == "__main__":
    main()
