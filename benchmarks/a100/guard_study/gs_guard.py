#!/usr/bin/env python3
"""Guard study (GS): numpy recomputation of the selection-N_eff guard from fixed-coordinate
records, curve tables over caps, PE x selection separability, injection-count scaling, and
cross-cap summaries of nested-sampling runs. numpy only (imports no darksirens package, no JAX).

    python gs_guard.py validate REC.json [REC.json ...] [--out J]
    python gs_guard.py curves --records R1.json R2.json ... --caps 1,2,5,10,20 --out J --md M --csv C
    python gs_guard.py repro --new NEW.json --ref REF.json [--ref REF2.json ...] [--out J]
    python gs_guard.py injections --records ... --coord 0 --caps 1,2,5,10,20 --out J --md M
    python gs_guard.py inference --runs DIR [DIR ...] --out J --md M [--reference-cap 10]
    python gs_guard.py postmean-share --records P1.json P2.json --coords-map MAP.json --out J --md M

The guard formula is shared, byte-identical, by the two codes (checked by diff for this study):
legacy darksirens c042527 ``darksirens/likelihood/selection.py:269-413`` and darksirens-core
``src/darksirens/selection/gw.py:270-414`` (main 88004d9 and O1 f825906). With n = N_obs,
sigma2_PE = sum of the per-event MC variances, cap = max_likelihood_variance:

    budget    = max(cap - sigma2_PE, 1e-12)                        (selection.py:349)
    T(cap)    = max(5 n, n^2 / budget)                             (selection.py:350)
    hard      : -inf unless N_eff > T, else -n log mu + n(n+3)/(2 N_eff)   (:402-407)
    soft      : x = N_eff/T; gate = softplus(200 (1 - x) - 10);
                wall = -gate (100 + 2 n softplus(-log mu));
                corr = -n log mu + n(n+3)/(2 max(N_eff, T)); total = corr + wall,
                -inf if not finite                                  (:382-400)

The soft PENALTY reported here is soft_total - unguarded, where unguarded = -n log mu +
n(n+3)/(2 N_eff) (the hard valid branch without the verdict): the wall plus the Taylor-term
freeze n(n+3)/2 (1/max(N_eff,T) - 1/N_eff). The harness threshold is recomputed with the
harness's own arithmetic (bench_fixed_theta.py:704-707). N_eff, log mu, the per-event terms
and the PE variance sum do not depend on the guard (bitwise across hard10/soft1/soft10
records of M5b, both codes), so one record per cell at any guard setting gives every cap.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)
MIN_BUDGET = 1e-12            # _MIN_VARIANCE_BUDGET, selection.py:122 (legacy) / gw.py:123 (core)
DYNESTY_LOWL = -1e300         # dynesty 2.1.4 utils.py:52 _LOWL_VAL (initial -inf live points)
GUARD_INDEPENDENT = ("log_mu", "n_eff", "pe_variance_sum", "sum_event_log_evidence",
                     "event_log_evidence", "event_mc_variance")
SEL_FIELDS = ("log_mu", "n_eff")
PE_FIELDS = ("pe_variance_sum", "sum_event_log_evidence", "event_log_evidence", "event_mc_variance")


# ----------------------------------------------------------------------------- formula
def softplus(x):
    return float(np.logaddexp(x, 0.0))   # jax.nn.softplus = logaddexp(x, 0)


def threshold(n, cap, pe_var):
    budget = max(cap - pe_var, MIN_BUDGET)
    return max(5.0 * n, (n * n) / budget)


def unguarded_correction(n, log_mu, n_eff):
    if n_eff == 0 or not math.isfinite(log_mu):
        return -math.inf
    return -n * log_mu + n * (3.0 + n) / (2.0 * n_eff)


def hard_correction(n, log_mu, n_eff, T):
    if not (n_eff > T):
        return -math.inf
    return -n * log_mu + n * (3.0 + n) / (2.0 * n_eff)


def soft_parts(n, log_mu, n_eff, T):
    """(total, wall, correction) of the soft branch, as selection.py:382-400."""
    x = n_eff / T if math.isfinite(n_eff) else math.inf
    gate = softplus(200.0 * (1.0 - x) - 10.0)
    reward = n * softplus(-log_mu)
    wall = -gate * (100.0 + 2.0 * reward)
    corr = -n * log_mu + n * (3.0 + n) / (2.0 * max(n_eff, T))
    total = corr + wall
    return (total if math.isfinite(total) else -math.inf), wall, corr


# ----------------------------------------------------------------------------- records
def val(entry):
    if isinstance(entry, dict):
        if "hex" in entry and isinstance(entry["hex"], str):
            return float.fromhex(entry["hex"])
        return float(entry["value"])
    return float(entry)


def hexes(entry):
    if isinstance(entry, dict) and "hex" in entry:
        return entry["hex"]
    return None


def load(path):
    with open(path) as f:
        r = json.load(f)
    r["_path"] = os.path.abspath(path)
    return r


def rec_meta(r):
    g = (r.get("config") or {}).get("guard") or {}
    pkg = r.get("package") or {}
    kdm = pkg.get("known_digest_match") or {}
    inp = r.get("inputs") or {}
    return {
        "record": os.path.basename(r["_path"]),
        "label": r.get("label"),
        "implementation": r.get("implementation"),
        "package_sha": pkg.get("git_sha") or kdm.get("sha"),
        "plan": (r.get("plan") or {}).get("name"),
        "pe": os.path.basename((inp.get("pe") or {}).get("path", "")),
        "sel": os.path.basename((inp.get("sel") or {}).get("path", "")),
        "pe_sha256": (inp.get("pe") or {}).get("sha256"),
        "sel_sha256": (inp.get("sel") or {}).get("sha256"),
        "n_events": (r.get("dims") or {}).get("n_events"),
        "nsamp": (r.get("dims") or {}).get("nsamp"),
        "n_injections": (r.get("dims") or {}).get("n_injections"),
        "ndraw": (r.get("dims") or {}).get("ndraw"),
        "coords_sha256": (r.get("coords") or {}).get("source_sha256"),
        "coords_digest": (r.get("coords") or {}).get("coords_digest"),
        "guard_mode": g.get("mode"), "guard_cap": g.get("cap"),
        "status": r.get("status"),
        "harness_sha": ((r.get("harness") or {}).get("git") or {}).get("sha")
        if isinstance((r.get("harness") or {}).get("git"), dict) else (r.get("harness") or {}).get("sha"),
    }


def code_key(r):
    """legacy | core arm label from the package sha (O1 = f825906)."""
    m = rec_meta(r)
    sha = (m["package_sha"] or "")
    if (r.get("implementation") or "").startswith("legacy"):
        return "legacy"
    if sha.startswith("f825906"):
        return "core_o1"
    if sha.startswith("88004d9"):
        return "core_main"
    return "core_" + (sha[:7] or "unknown")


def coord_rows(r, caps):
    n = float(r["dims"]["n_events"])
    out = []
    names = (r.get("coords") or {}).get("names")
    values = (r.get("coords") or {}).get("values")
    for pc in r["values"]["per_coord"]:
        i = pc["index"]
        lm, ne, pv = val(pc["log_mu"]), val(pc["n_eff"]), val(pc["pe_variance_sum"])
        se = val(pc["sum_event_log_evidence"])
        ug = unguarded_correction(n, lm, ne)
        ug_total = se + ug
        row = {
            "index": i, "kind": pc.get("kind"),
            "coord": (values[i] if values else None), "coord_names": names,
            "log_mu": lm, "n_eff": ne, "N2_over_neff": (n * n / ne) if ne else math.inf,
            "sigma2_pe": pv, "sigma2_lnL": pv + ((n * n / ne) if ne else math.inf),
            "sum_event_log_evidence": se, "unguarded_correction": ug,
            "unguarded_total": ug_total,
            "record_total_logL": val(pc["total_logL"]),
            "record_guard_pass": pc.get("guard_pass"),
            "caps": {},
        }
        for cap in caps:
            T = threshold(n, cap, pv)
            st, wall, corr = soft_parts(n, lm, ne, T)
            soft_total = se + st
            pen = (st - ug) if (math.isfinite(st) and math.isfinite(ug)) else -math.inf
            taylor_delta = n * (3.0 + n) / 2.0 * (1.0 / max(ne, T) - 1.0 / ne) if ne else None
            row["caps"][repr(float(cap))] = {
                "cap": float(cap), "threshold": T, "budget_exhausted": (cap - pv) <= MIN_BUDGET,
                "neff_over_threshold": ne / T,
                "variance_criterion_pass": (pv + n * n / ne) < cap if ne else False,
                "floor_5N_pass": ne > 5.0 * n,
                "hard_pass": bool(ne > T), "hard_total": se + hard_correction(n, lm, ne, T),
                "soft_wall": wall, "soft_taylor_delta": taylor_delta, "soft_penalty": pen,
                "soft_total": soft_total,
                "soft_unpenalised_bitwise": bool(soft_total == ug_total),
                "penalty_share_of_total": (pen / soft_total) if (math.isfinite(pen) and soft_total
                                                                 and math.isfinite(soft_total)) else None,
            }
        out.append(row)
    return out


def _rel(a, b):
    if a == b or (math.isnan(a) and math.isnan(b)):
        return 0.0
    if math.isinf(a) or math.isinf(b):
        return math.inf
    return abs(a - b) / abs(a) if a else math.inf


def jdump(obj, path):
    def enc(o):
        if isinstance(o, float):
            if math.isnan(o):
                return "nan"
            if math.isinf(o):
                return "inf" if o > 0 else "-inf"
        if isinstance(o, dict):
            return {k: enc(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [enc(v) for v in o]
        if isinstance(o, (np.floating,)):
            return enc(float(o))
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        return o
    txt = json.dumps(enc(obj), indent=1)
    if path:
        with open(path, "w") as f:
            f.write(txt + "\n")
    return txt


def fmt(x, nd=6):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"
    x = float(x)
    if math.isnan(x):
        return "nan"
    if math.isinf(x):
        return "-inf" if x < 0 else "inf"
    if x != 0 and (abs(x) < 1e-3 or abs(x) >= 1e7):
        return f"{x:.{max(nd - 2, 2)}e}"
    return f"{x:.{nd}g}"


# ----------------------------------------------------------------------------- validate
def cmd_validate(a):
    """Recompute each record's selection_log_correction from its own guard settings and
    compare; check total_logL == sum_event_log_evidence + selection_log_correction and, for
    hard records, total_finite == guard_pass."""
    res = []
    ok_all = True
    for p in a.records:
        r = load(p)
        m = rec_meta(r)
        n = float(r["dims"]["n_events"])
        cap, mode = m["guard_cap"], m["guard_mode"]
        worst, bitwise, worst_tot, worst_thr, verdict_ok = 0.0, 0, 0.0, 0.0, True
        for pc in r["values"]["per_coord"]:
            lm, ne, pv = val(pc["log_mu"]), val(pc["n_eff"]), val(pc["pe_variance_sum"])
            T = threshold(n, cap, pv)
            worst_thr = max(worst_thr, _rel(val(pc["guard_threshold"]), T))
            c = soft_parts(n, lm, ne, T)[0] if mode == "soft" else hard_correction(n, lm, ne, T)
            s = val(pc["selection_log_correction"])
            worst = max(worst, _rel(s, c))
            bitwise += int(c == s)
            tot, se = val(pc["total_logL"]), val(pc["sum_event_log_evidence"])
            if math.isfinite(tot):
                worst_tot = max(worst_tot, _rel(tot, se + s))
            else:
                verdict_ok &= not math.isfinite(se + s)
            if mode == "hard":
                verdict_ok &= bool(pc["total_finite"]) == bool(pc["guard_pass"])
        ok = worst <= a.rtol and worst_tot <= a.rtol and worst_thr == 0.0 and verdict_ok
        ok_all &= ok
        res.append({**m, "n_coords": len(r["values"]["per_coord"]),
                    "recompute_vs_record_max_rel": worst, "recompute_bitwise_coords": bitwise,
                    "total_eq_sumev_plus_slc_max_rel": worst_tot, "threshold_max_rel": worst_thr,
                    "hard_verdict_consistent": verdict_ok, "pass": ok})
        print(f"{m['record']}: {mode}@{cap} recompute max_rel {worst:.3g} (bitwise {bitwise}), "
              f"total=sumev+slc max_rel {worst_tot:.3g}, threshold max_rel {worst_thr:.3g}, "
              f"verdict {verdict_ok} -> {'PASS' if ok else 'FAIL'}")
    jdump({"schema": "gs-validate/1", "rtol": a.rtol, "pass": ok_all, "records": res}, a.out)
    return 0 if ok_all else 1


# ----------------------------------------------------------------------------- repro
def cmd_repro(a):
    """Bitwise equality of the guard-independent per-coordinate fields of NEW vs REF records
    (same plan, coordinates and inputs; guard settings may differ)."""
    new = load(a.new)
    out = {"schema": "gs-repro/1", "new": rec_meta(new), "refs": []}
    ok_all = True
    for rp in a.ref:
        ref = load(rp)
        why = []
        mn, mr = rec_meta(new), rec_meta(ref)
        for k in ("plan", "pe_sha256", "sel_sha256", "coords_digest"):
            if mn[k] != mr[k]:
                why.append(f"{k} differs ({mn[k]} vs {mr[k]})")
        entry = {"ref": mr, "refused": why or None, "fields": {}}
        if not why:
            for f in GUARD_INDEPENDENT:
                nb, mx = 0, 0.0
                for pn, pr in zip(new["values"]["per_coord"], ref["values"]["per_coord"]):
                    if hexes(pn[f]) != hexes(pr[f]):
                        nb += 1
                        if f in ("event_log_evidence", "event_mc_variance"):
                            mx = math.inf if mx == 0 else mx
                        else:
                            mx = max(mx, _rel(val(pr[f]), val(pn[f])))
                entry["fields"][f] = {"coords_bit_different": nb, "max_rel_scalar": mx}
            entry["bitwise"] = all(v["coords_bit_different"] == 0 for v in entry["fields"].values())
            ok_all &= entry["bitwise"]
        out["refs"].append(entry)
        print(f"{mn['record']} vs {mr['record']}: " + ("REFUSED " + "; ".join(why) if why else
              f"bitwise {entry['bitwise']}"))
    out["all_bitwise"] = ok_all
    jdump(out, a.out)
    return 0


# ----------------------------------------------------------------------------- curves
def cmd_curves(a):
    caps = [float(c) for c in a.caps.split(",")]
    recs = [load(p) for p in a.records]
    table, csv_rows = [], []
    by_cell = {}
    for r in recs:
        m = rec_meta(r)
        code = code_key(r)
        rows = coord_rows(r, caps)
        by_cell[(code, m["plan"], m["pe"], m["sel"])] = (r, rows)
        table.append({"meta": {**m, "code": code}, "rows": rows})
        for row in rows:
            for ck, c in row["caps"].items():
                csv_rows.append({
                    "code": code, "plan": m["plan"], "pe": m["pe"], "sel": m["sel"],
                    "n_injections": m["n_injections"], "ndraw": m["ndraw"], "coord": row["index"],
                    "kind": row["kind"], "n_eff": row["n_eff"], "N2_over_neff": row["N2_over_neff"],
                    "sigma2_pe": row["sigma2_pe"], "sigma2_lnL": row["sigma2_lnL"],
                    "log_mu": row["log_mu"], "unguarded_total": row["unguarded_total"],
                    "cap": c["cap"], "threshold": c["threshold"],
                    "neff_over_threshold": c["neff_over_threshold"],
                    "budget_exhausted": c["budget_exhausted"], "hard_pass": c["hard_pass"],
                    "soft_penalty": c["soft_penalty"], "soft_total": c["soft_total"],
                    "soft_unpenalised_bitwise": c["soft_unpenalised_bitwise"],
                    "penalty_share_of_total": c["penalty_share_of_total"]})
    # separability: within (code, plan): same sel -> SEL_FIELDS equal; same pe -> PE_FIELDS equal
    sep = []
    keys = sorted(by_cell)
    for i, k1 in enumerate(keys):
        for k2 in keys[i + 1:]:
            if k1[:2] != k2[:2]:
                continue
            r1, r2 = by_cell[k1][0], by_cell[k2][0]
            if rec_meta(r1)["coords_digest"] != rec_meta(r2)["coords_digest"]:
                continue
            for same, fields in ((k1[3] == k2[3], SEL_FIELDS), (k1[2] == k2[2], PE_FIELDS)):
                if not same:
                    continue
                eq = all(hexes(p1[f]) == hexes(p2[f]) for f in fields
                         for p1, p2 in zip(r1["values"]["per_coord"], r2["values"]["per_coord"]))
                sep.append({"code": k1[0], "plan": k1[1], "a": k1[2:], "b": k2[2:],
                            "shared": "selection file" if fields is SEL_FIELDS else "PE file",
                            "fields": list(fields), "bitwise_equal": eq})
    # composed 3x3 grid from separability (every PE file x every selection file seen per code/plan)
    composed = []
    groups = {}
    for (code, plan, pe, sel), (r, rows) in by_cell.items():
        groups.setdefault((code, plan), {}).setdefault("pe", {}).setdefault(pe, (r, rows))
        groups[(code, plan)].setdefault("sel", {}).setdefault(sel, (r, rows))
    for (code, plan), g in sorted(groups.items()):
        for pe, (rp, rows_p) in sorted(g["pe"].items()):
            for sel, (rs, rows_s) in sorted(g["sel"].items()):
                measured = (code, plan, pe, sel) in by_cell
                n = float(rp["dims"]["n_events"])
                for rowp, rows_ in zip(rows_p, rows_s):
                    lm, ne, pv = rows_["log_mu"], rows_["n_eff"], rowp["sigma2_pe"]
                    se = rowp["sum_event_log_evidence"]
                    ug = unguarded_correction(n, lm, ne)
                    cell = {"code": code, "plan": plan, "pe": pe, "sel": sel,
                            "n_injections": rs["dims"]["n_injections"], "coord": rowp["index"],
                            "kind": rowp["kind"], "source": "measured" if measured else
                            "composed: PE terms from the PE-file record, N_eff/log_mu from the "
                            "selection-file record (separability)",
                            "n_eff": ne, "N2_over_neff": n * n / ne if ne else math.inf,
                            "sigma2_pe": pv, "sigma2_lnL": pv + (n * n / ne if ne else math.inf),
                            "unguarded_total": se + ug, "caps": {}}
                    for cap in caps:
                        T = threshold(n, cap, pv)
                        st = soft_parts(n, lm, ne, T)[0]
                        cell["caps"][repr(cap)] = {
                            "threshold": T, "hard_pass": bool(ne > T),
                            "soft_penalty": (st - ug) if math.isfinite(st) and math.isfinite(ug) else -math.inf,
                            "neff_over_threshold": ne / T}
                    composed.append(cell)
    # code agreement per measured cell
    agree = []
    for (code, plan, pe, sel), (r, rows) in sorted(by_cell.items()):
        if code == "legacy":
            continue
        k = ("legacy", plan, pe, sel)
        if k not in by_cell:
            continue
        rl, rows_l = by_cell[k]
        if rec_meta(rl)["coords_digest"] != rec_meta(r)["coords_digest"]:
            continue
        f_rel = {}
        for f in ("n_eff", "log_mu", "sigma2_pe", "sum_event_log_evidence", "unguarded_total"):
            f_rel[f] = max(_rel(x[f], y[f]) for x, y in zip(rows_l, rows))
        verdicts = all(x["caps"][c]["hard_pass"] == y["caps"][c]["hard_pass"]
                       for x, y in zip(rows_l, rows) for c in x["caps"])
        pen = max(_rel(x["caps"][c]["soft_penalty"], y["caps"][c]["soft_penalty"])
                  for x, y in zip(rows_l, rows) for c in x["caps"])
        agree.append({"code": code, "plan": plan, "pe": pe, "sel": sel, "max_rel": f_rel,
                      "hard_verdicts_equal_all_caps": verdicts, "soft_penalty_max_rel": pen})
    out = {"schema": "gs-curves/1", "caps": caps, "records": table, "separability": sep,
           "composed_grid": composed, "code_agreement": agree}
    jdump(out, a.out)
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            w.writeheader()
            for row in csv_rows:
                w.writerow({k: (fmt(v, 17) if isinstance(v, float) else v) for k, v in row.items()})
    if a.md:
        L = ["# Guard study: per-coordinate guard quantities", "",
             f"Caps: {', '.join(fmt(c) for c in caps)}. soft penalty = soft total - unguarded "
             "(wall + Taylor freeze), nats; 'none' = the soft total equals the unguarded total "
             "bitwise.", ""]
        for t in table:
            m = t["meta"]
            L += [f"## {m['code']} | {m['plan']} | {m['pe']} + {m['sel']} "
                  f"({fmt(m['n_injections'])} detected injections)", "",
                  "| coord | kind | N_eff | N^2/N_eff | sigma2_PE | sigma2_lnL | " +
                  " | ".join(f"hard@{fmt(c)}" for c in caps) + " | " +
                  " | ".join(f"soft pen.@{fmt(c)}" for c in caps) + " |",
                  "|" + "---|" * (6 + 2 * len(caps))]
            for row in t["rows"]:
                cs = [row["caps"][repr(c)] for c in caps]
                L.append(f"| {row['index']} | {row['kind']} | {fmt(row['n_eff'])} | "
                         f"{fmt(row['N2_over_neff'])} | {fmt(row['sigma2_pe'])} | "
                         f"{fmt(row['sigma2_lnL'])} | " +
                         " | ".join("pass" if c["hard_pass"] else "-inf" for c in cs) + " | " +
                         " | ".join("none" if c["soft_unpenalised_bitwise"] else fmt(c["soft_penalty"], 4)
                                    for c in cs) + " |")
            L.append("")
        if sep:
            L += ["## Separability (bitwise)", "", "| code | plan | cell A | cell B | shared file | equal |",
                  "|---|---|---|---|---|---|"]
            L += [f"| {s['code']} | {s['plan']} | {'+'.join(s['a'])} | {'+'.join(s['b'])} | "
                  f"{s['shared']} | {s['bitwise_equal']} |" for s in sep]
            L.append("")
        if agree:
            L += ["## Code agreement (legacy = reference)", "",
                  "| code | plan | cell | max rel N_eff | log_mu | sigma2_PE | unguarded total | "
                  "hard verdicts equal | soft penalty max rel |", "|---|---|---|---|---|---|---|---|---|"]
            L += [f"| {g['code']} | {g['plan']} | {g['pe']}+{g['sel']} | {fmt(g['max_rel']['n_eff'],3)} | "
                  f"{fmt(g['max_rel']['log_mu'],3)} | {fmt(g['max_rel']['sigma2_pe'],3)} | "
                  f"{fmt(g['max_rel']['unguarded_total'],3)} | {g['hard_verdicts_equal_all_caps']} | "
                  f"{fmt(g['soft_penalty_max_rel'],3)} |" for g in agree]
        with open(a.md, "w") as f:
            f.write("\n".join(L) + "\n")
    print(f"curves: {len(table)} records, {sum(len(t['rows']) for t in table)} coordinate rows, "
          f"{len(sep)} separability pairs (all equal: {all(s['bitwise_equal'] for s in sep)}), "
          f"{len(agree)} code-agreement cells")
    return 0


# ----------------------------------------------------------------------------- injections
def cmd_injections(a):
    """N_eff and the threshold vs the number of detected injections at one coordinate, and the
    injection count at which N_eff would reach T(cap) under the stated scaling assumption."""
    caps = [float(c) for c in a.caps.split(",")]
    recs = [load(p) for p in a.records]
    groups = {}
    for r in recs:
        m = rec_meta(r)
        groups.setdefault((code_key(r), m["plan"]), []).append(r)
    out = {"schema": "gs-injections/1", "coord": a.coord, "caps": caps,
           "assumption": ("N_eff scales linearly with the number of detected injections at fixed "
                          "population and injection distribution (iid draws; ndraw rescaled in "
                          "proportion, as in the strided files). Checked, not assumed, by the "
                          "N_eff/N_det column across the three selection files."),
           "groups": []}
    L = ["# Injection-count dependence of N_eff and the hard-guard threshold", "",
         out["assumption"], ""]
    for (code, plan), rs in sorted(groups.items()):
        sel_pts, pe_pts = {}, {}
        for r in rs:
            m = rec_meta(r)
            pc = r["values"]["per_coord"][a.coord]
            sel_pts[m["sel"]] = {"n_det": m["n_injections"], "ndraw": m["ndraw"],
                                 "n_eff": val(pc["n_eff"]), "log_mu": val(pc["log_mu"])}
            pe_pts[m["pe"]] = {"sigma2_pe": val(pc["pe_variance_sum"]), "n": float(m["n_events"]),
                               "nsamp": m["nsamp"]}
        full = max(sel_pts.values(), key=lambda s: s["n_det"])
        g = {"code": code, "plan": plan, "selection": [], "pe": [], "extrapolation": []}
        for sel, s in sorted(sel_pts.items(), key=lambda kv: kv[1]["n_det"]):
            g["selection"].append({"sel": sel, **s, "n_eff_per_detected": s["n_eff"] / s["n_det"],
                                   "ratio_to_full_n_eff": s["n_eff"] / full["n_eff"],
                                   "ratio_to_full_n_det": s["n_det"] / full["n_det"]})
        for pe, p in sorted(pe_pts.items(), key=lambda kv: -(kv[1]["nsamp"] or 0)):
            thr = {repr(c): threshold(p["n"], c, p["sigma2_pe"]) for c in caps}
            g["pe"].append({"pe": pe, **p, "threshold": thr})
            for c in caps:
                T = thr[repr(c)]
                exhausted = (c - p["sigma2_pe"]) <= MIN_BUDGET
                ex = {"pe": pe, "cap": c, "threshold": T, "budget_exhausted": exhausted}
                for sel, s in sel_pts.items():
                    ex[f"n_det_needed_from_{sel}"] = (None if exhausted else
                                                      s["n_det"] * T / s["n_eff"])
                    ex[f"ndraw_needed_from_{sel}"] = (None if exhausted else s["ndraw"] * T / s["n_eff"])
                g["extrapolation"].append(ex)
        out["groups"].append(g)
        L += [f"## {code} | {plan} | coordinate {a.coord}", "",
              "| selection file | detected | ndraw | N_eff | N_eff / detected | N_eff ratio to full | "
              "detected ratio to full |", "|---|---|---|---|---|---|---|"]
        L += [f"| {s['sel']} | {fmt(s['n_det'])} | {fmt(s['ndraw'])} | {fmt(s['n_eff'])} | "
              f"{fmt(s['n_eff_per_detected'],4)} | {fmt(s['ratio_to_full_n_eff'],4)} | "
              f"{fmt(s['ratio_to_full_n_det'],4)} |" for s in g["selection"]]
        L += ["", "| PE file | sigma2_PE | " + " | ".join(f"T({fmt(c)})" for c in caps) + " |",
              "|" + "---|" * (2 + len(caps))]
        L += [f"| {p['pe']} | {fmt(p['sigma2_pe'])} | " +
              " | ".join(fmt(p["threshold"][repr(c)]) for c in caps) + " |" for p in g["pe"]]
        sels = sorted(sel_pts, key=lambda k: -sel_pts[k]["n_det"])
        L += ["", "Detected injections needed for N_eff > T(cap) (linear scaling from each file):", "",
              "| PE file | cap | T | " + " | ".join(f"from {s}" for s in sels) + " |",
              "|" + "---|" * (3 + len(sels))]
        for ex in g["extrapolation"]:
            L.append(f"| {ex['pe']} | {fmt(ex['cap'])} | {fmt(ex['threshold'])} | " +
                     " | ".join("budget exhausted" if ex["budget_exhausted"] else
                                fmt(ex[f'n_det_needed_from_{s}'], 4) for s in sels) + " |")
        L.append("")
    jdump(out, a.out)
    if a.md:
        with open(a.md, "w") as f:
            f.write("\n".join(L) + "\n")
    print("\n".join(L[:40]))
    return 0


# ----------------------------------------------------------------------------- inference
def _cp():
    sys.path.insert(0, HARNESS)
    import compare_posteriors as cp  # noqa: E402  (numpy + bench_common only)
    return cp


def _run_summary(d, cp):
    rec = load(os.path.join(d, "record.json"))
    s = (rec.get("settings") or {}).get("requested") or {}
    res = rec.get("result") or {}
    lc = rec.get("likelihood_calls") or {}
    post = None
    npz = os.path.join(d, "posterior.npz")
    if os.path.isfile(npz):
        with np.load(npz, allow_pickle=False) as z:
            post = {k: z[k] for k in z.files}
    out = {"dir": os.path.abspath(d), "label": rec.get("label"), "status": rec.get("status"),
           "implementation": rec.get("implementation"), "arm": rec.get("arm"),
           "rung": (rec.get("rung") or {}).get("rung"), "sampler": s.get("sampler"),
           "guard": s.get("guard"), "cap": s.get("max_likelihood_variance"),
           "seed": s.get("seed"), "nlive": s.get("nlive"), "dlogz": s.get("dlogz"),
           "stop_reason": (rec.get("budget") or {}).get("stop_reason"),
           "n_like_evals": lc.get("n_like_evals"), "nonfinite": lc.get("nonfinite"),
           "logZ": res.get("logZ"), "logZ_hex": res.get("logZ_hex"), "logZerr": res.get("logZerr"),
           "n_dead": res.get("n_dead"), "sampler_error": rec.get("sampler_error"),
           "t_total_s": (rec.get("timing") or {}).get("t_total_s"),
           "t_sampling_s": (rec.get("timing") or {}).get("t_sampling_s")}
    if post is not None:
        labels = [str(x) for x in post["labels"]]
        out["labels"] = labels
        out["kish_ess"] = cp.kish_ess(post["dead_logwt"])
        out["params"] = {lab: cp.param_stats(post["samples"][:, i]) for i, lab in enumerate(labels)}
        dl = post["dead_logl"]
        n_floor = int(np.sum(dl <= DYNESTY_LOWL * 0.1))  # dynesty stores -inf live points as -1e300
        out["dead_points_at_dynesty_floor"] = n_floor
        out["initial_live_fraction_minus_inf"] = (n_floor / out["nlive"]) if out["nlive"] else None
        out["_samples"] = post["samples"]
        out["posterior_mean_hex"] = [float(np.mean(post["samples"][:, i])).hex()
                                     for i in range(len(labels))]
    return out


def cmd_inference(a):
    cp = _cp()
    runs = []
    for d in a.runs:
        for dd in sorted(glob.glob(d)):
            if os.path.isfile(os.path.join(dd, "record.json")):
                runs.append(_run_summary(dd, cp))
    # cross-cap within (rung, implementation/arm), reference = soft@reference_cap
    cross = []
    for key in sorted({(r["rung"], r["arm"]) for r in runs}):
        group = [r for r in runs if (r["rung"], r["arm"]) == key]
        ref = next((r for r in group if r["guard"] == "soft" and r["cap"] == a.reference_cap
                    and r.get("params")), None)
        for r in group:
            row = {"rung": key[0], "arm": key[1], "label": r["label"], "guard": r["guard"],
                   "cap": r["cap"], "status": r["status"], "stop_reason": r["stop_reason"],
                   "n_like_evals": r["n_like_evals"], "logZ": r["logZ"], "logZerr": r["logZerr"],
                   "dead_points_at_dynesty_floor": r.get("dead_points_at_dynesty_floor"),
                   "nonfinite": r.get("nonfinite"), "params": r.get("params"), "vs_reference": None}
            if ref is not None and r.get("params") and r is not ref:
                v = {"reference": ref["label"], "params": {}}
                for i, lab in enumerate(ref["labels"]):
                    pa, pb = ref["params"][lab], r["params"][lab]
                    mc = math.sqrt(pa["std"] ** 2 / (ref["kish_ess"] or math.inf) +
                                   pb["std"] ** 2 / (r["kish_ess"] or math.inf))
                    v["params"][lab] = {"dmean": pb["mean"] - pa["mean"],
                                        "dmean_over_ref_std": (pb["mean"] - pa["mean"]) / pa["std"] if pa["std"] else None,
                                        "dmean_over_mc_err": (pb["mean"] - pa["mean"]) / mc if mc else None,
                                        "std_ratio": pb["std"] / pa["std"] if pa["std"] else None,
                                        "ks_D": cp.ks_D(ref["_samples"][:, i], r["_samples"][:, i])}
                if ref["logZ"] is not None and r["logZ"] is not None:
                    comb = math.hypot(ref["logZerr"] or 0.0, r["logZerr"] or 0.0)
                    v["dlogZ"] = r["logZ"] - ref["logZ"]
                    v["dlogZ_over_err"] = v["dlogZ"] / comb if comb else None
                row["vs_reference"] = v
            cross.append(row)
    # legacy vs core per (rung, guard, cap)
    pairs = []
    for key in sorted({(r["rung"], r["guard"], r["cap"]) for r in runs}, key=str):
        g = [r for r in runs if (r["rung"], r["guard"], r["cap"]) == key]
        leg = [r for r in g if (r["implementation"] or "").startswith("legacy")]
        core = [r for r in g if not (r["implementation"] or "").startswith("legacy")]
        for L_ in leg:
            for C_ in core:
                pr = {"rung": key[0], "guard": key[1], "cap": key[2], "legacy": L_["label"],
                      "core": C_["label"], "status": [L_["status"], C_["status"]],
                      "n_like_evals": [L_["n_like_evals"], C_["n_like_evals"]],
                      "logZ_bitwise": (L_["logZ_hex"] is not None and L_["logZ_hex"] == C_["logZ_hex"]),
                      "samples_bitwise": None}
                if L_.get("_samples") is not None and C_.get("_samples") is not None:
                    pr["samples_bitwise"] = bool(L_["_samples"].shape == C_["_samples"].shape and
                                                 np.array_equal(L_["_samples"], C_["_samples"]))
                pairs.append(pr)
    for r in runs:
        r.pop("_samples", None)
    out = {"schema": "gs-inference/1", "reference_cap": a.reference_cap, "runs": runs,
           "cross_cap": cross, "legacy_vs_core": pairs}
    jdump(out, a.out)
    if a.md:
        L = ["# Guard study: posterior sensitivity to the guard", ""]
        L += ["| rung | arm | guard@cap | status (stop) | evals | logZ +- err | initial live pts at -inf | "
              "non-finite evals | posterior (mean +- std; q16/q50/q84) | shift vs soft@%s (std / MC err; KS D) |"
              % fmt(a.reference_cap), "|---|---|---|---|---|---|---|---|---|---|"]
        for c in cross:
            ps = "; ".join(f"{k}: {fmt(v['mean'],5)} +- {fmt(v['std'],3)} ({fmt(v['q16'],4)}/{fmt(v['q50'],4)}/{fmt(v['q84'],4)})"
                           for k, v in (c["params"] or {}).items()) or "-"
            vs = "-"
            if c["vs_reference"]:
                vs = "; ".join(f"{k}: {fmt(v['dmean_over_ref_std'],3)} / {fmt(v['dmean_over_mc_err'],3)}; D {fmt(v['ks_D'],3)}"
                               for k, v in c["vs_reference"]["params"].items())
                if c["vs_reference"].get("dlogZ") is not None:
                    vs += f"; dlogZ {fmt(c['vs_reference']['dlogZ'],3)} ({fmt(c['vs_reference']['dlogZ_over_err'],3)} sigma)"
            nf = c["nonfinite"]
            L.append(f"| {c['rung']} | {c['arm']} | {c['guard']}@{fmt(c['cap'])} | {c['status']} ({c['stop_reason']}) | "
                     f"{fmt(c['n_like_evals'])} | {fmt(c['logZ'],8)} +- {fmt(c['logZerr'],3)} | "
                     f"{fmt(c['dead_points_at_dynesty_floor'])} | {json.dumps(nf) if nf else '-'} | {ps} | {vs} |")
        L += ["", "## Legacy vs core, same seed, same guard and cap", "",
              "| rung | guard@cap | legacy | core | evals | logZ bitwise | samples bitwise |",
              "|---|---|---|---|---|---|---|"]
        L += [f"| {p['rung']} | {p['guard']}@{fmt(p['cap'])} | {p['legacy']} | {p['core']} | "
              f"{p['n_like_evals']} | {p['logZ_bitwise']} | {p['samples_bitwise']} |" for p in pairs]
        with open(a.md, "w") as f:
            f.write("\n".join(L) + "\n")
    print(f"inference: {len(runs)} runs, {len(cross)} cross-cap rows, {len(pairs)} legacy/core pairs")
    return 0


# ----------------------------------------------------------------------------- postmean-share
def cmd_postmean_share(a):
    """Penalty share of the total at posterior means: fixed-coordinate records whose
    coordinates were written by gs_coords.py postmean (kinds 'posterior_mean:<run label>');
    for each run, the penalty and share at THAT run's own cap (soft runs) and at every cap."""
    caps = [float(c) for c in a.caps.split(",")]
    out = {"schema": "gs-postmean-share/1", "caps": caps, "records": []}
    L = ["# Soft-penalty share of the total at the posterior means", "",
         "| record | coordinate (run) | run guard@cap | N_eff | sigma2_PE | unguarded total | "
         "penalty at the run's cap (nats) | share of total | " +
         " | ".join(f"hard@{fmt(c)}" for c in caps) + " |", "|" + "---|" * (8 + len(caps))]
    for p in a.records:
        r = load(p)
        cm = r.get("coords") or {}
        src = cm.get("source_file")
        runs_meta = {}
        if src and os.path.isfile(src):
            with open(src) as f:
                runs_meta = (json.load(f).get("posterior_mean_runs") or {})
        rows = coord_rows(r, caps + [c for c in (v.get("cap") for v in runs_meta.values()) if c is not None])
        ents = []
        for row in rows:
            kind = row["kind"] or ""
            lab = kind.split(":", 1)[1] if kind.startswith("posterior_mean:") else None
            meta = runs_meta.get(lab or "", {})
            own = row["caps"].get(repr(float(meta["cap"]))) if meta.get("cap") is not None else None
            ents.append({"index": row["index"], "kind": kind, "run": lab, "run_guard": meta.get("guard"),
                         "run_cap": meta.get("cap"), "n_eff": row["n_eff"], "sigma2_pe": row["sigma2_pe"],
                         "unguarded_total": row["unguarded_total"],
                         "penalty_at_run_cap": own["soft_penalty"] if own else None,
                         "share_at_run_cap": own["penalty_share_of_total"] if own else None,
                         "caps": row["caps"]})
            L.append(f"| {os.path.basename(p)} | {row['index']} ({lab}) | {meta.get('guard')}@{fmt(meta.get('cap'))} | "
                     f"{fmt(row['n_eff'])} | {fmt(row['sigma2_pe'])} | {fmt(row['unguarded_total'],10)} | "
                     f"{fmt(own['soft_penalty'],4) if own else '-'} | {fmt(own['penalty_share_of_total'],4) if own else '-'} | " +
                     " | ".join("pass" if row["caps"][repr(c)]["hard_pass"] else "-inf" for c in caps) + " |")
        out["records"].append({"meta": rec_meta(r), "code": code_key(r), "rows": ents})
    jdump(out, a.out)
    if a.md:
        with open(a.md, "w") as f:
            f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("records", nargs="+")
    v.add_argument("--rtol", type=float, default=1e-12); v.add_argument("--out")
    r = sub.add_parser("repro"); r.add_argument("--new", required=True)
    r.add_argument("--ref", action="append", required=True); r.add_argument("--out")
    c = sub.add_parser("curves"); c.add_argument("--records", nargs="+", required=True)
    c.add_argument("--caps", default="1,2,5,10,20"); c.add_argument("--out"); c.add_argument("--md")
    c.add_argument("--csv")
    i = sub.add_parser("injections"); i.add_argument("--records", nargs="+", required=True)
    i.add_argument("--coord", type=int, default=0); i.add_argument("--caps", default="1,2,5,10,20")
    i.add_argument("--out"); i.add_argument("--md")
    n = sub.add_parser("inference"); n.add_argument("--runs", nargs="+", required=True)
    n.add_argument("--reference-cap", type=float, default=10.0); n.add_argument("--out"); n.add_argument("--md")
    p = sub.add_parser("postmean-share"); p.add_argument("--records", nargs="+", required=True)
    p.add_argument("--caps", default="1,2,5,10,20"); p.add_argument("--out"); p.add_argument("--md")
    a = ap.parse_args(argv)
    return {"validate": cmd_validate, "repro": cmd_repro, "curves": cmd_curves,
            "injections": cmd_injections, "inference": cmd_inference,
            "postmean-share": cmd_postmean_share}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
