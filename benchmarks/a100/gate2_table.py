#!/usr/bin/env python3
"""One CSV row per Gate 2 / M5 record (campaign_run.py index + records + summaries).

    python gate2_table.py --outdir OUT --csv gate2_matrix.csv [--json rows.json] [--order SPEC]

Columns: gate1_table.COLUMNS plus the catalog dimensions n_rows, row_width (n_max),
nside, n_pixels_occupied (occupied pixels of the full catalog), z_depth, n_galaxies
(galaxies in the full catalog); empty for spectral records.

parity_vs_legacy (first comparison of the record) is one of
pass | fail | mcvar-noise | neff-noise | refused | n.a., with the campaign's noise rules:

* D-mcvar: the only failing field is event_mc_variance, masks equal, repeat consistent,
  max_rel <= MCVAR_FLOOR (the Gate 0 device floor of that field) -> mcvar-noise;
* D-neff: the failing fields are n_eff (and possibly sigma2_lnL = pe_var + n^2/n_eff,
  which is derived from it), its source quantities log_mu and selection_log_correction
  pass, masks equal, repeat consistent, AND the legacy-vs-core-whole comparison of the same
  cell passes at the failing coordinates -> neff-noise; the amplification factor
  N_eff / N_draw at the failing coordinates is recorded in the JSON rows;
* D-catvals: catalog-side per-sample log-density arrays (pe_log_prior, sel_log_prior)
  are informational and judged as |delta log p| <= 1e-12 absolute; every other catalog
  field keeps rtol 1e-12; rows_f is informational. The catalog verdict is in the JSON
  rows (it never enters parity_vs_legacy).
"""

from __future__ import annotations

import argparse
import csv
import json
import os

import gate1_table as g1

CAT_COLUMNS = ["n_rows", "row_width", "nside", "n_pixels_occupied", "z_depth", "n_galaxies"]
COLUMNS = g1.COLUMNS + CAT_COLUMNS
CATVALS_ATOL = 1e-12
CATVALS_ABS_KEYS = ("catalog_arrays.pe_log_prior", "catalog_arrays.sel_log_prior")
CATVALS_INFO_KEYS = ("catalog_arrays.rows_f",)


def _load(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)


def catvals(summary):
    """D-catvals verdict of one comparison summary (None for spectral)."""
    if summary is None or "catalog_fields" not in summary:
        return None
    cat = summary.get("catalog") or {}
    fails, worst_rel, worst_abs = [], ("", 0.0), ("", 0.0)
    for k, v in summary["catalog_fields"].items():
        if k in CATVALS_INFO_KEYS:
            continue
        if k in CATVALS_ABS_KEYS:
            ok = v.get("n_nonfinite_mismatch", 0) == 0 and v["max_abs"] <= CATVALS_ATOL
            if v["max_abs"] > worst_abs[1]:
                worst_abs = (k, v["max_abs"])
        else:
            ok = bool(v["pass"])
            if v["max_rel"] > worst_rel[1]:
                worst_rel = (k, v["max_rel"])
        if not ok:
            fails.append(k)
    struct = bool(cat.get("structure_equal"))
    empty = bool(cat.get("row_empty_equal"))
    return {"pass": bool(not fails and struct and empty), "failing": fails,
            "structure_equal": struct, "row_empty_equal": empty,
            "worst_rel_field": worst_rel[0], "worst_rel": worst_rel[1],
            "worst_abs_logp_field": worst_abs[0], "worst_abs_logp": worst_abs[1],
            "comparator_catalog_values_pass": (summary.get("verdict") or {}).get("catalog_values_pass")}


def classify(summary, whole_summary=None, rec_b=None):
    """parity class of one summary under D-mcvar / D-neff (whole_summary = legacy vs core
    whole of the same cell, for D-neff)."""
    if summary is None:
        return None
    if summary.get("status") != "compared":
        return {"parity": "refused", "reasons": summary.get("refusal_reasons")}
    fields = summary["fields"]
    failing = [k for k, v in fields.items() if not v["pass"]]
    mrel = {k: v["max_rel"] for k, v in fields.items() if k != "decoded_full_parameter_vector"}
    worst = max(mrel, key=lambda k: mrel[k])
    v = summary["verdict"]
    masks, rep = v["masks_equal"], v["repeat_consistent_both"]
    out = {"failing_fields": failing, "masks_equal": masks, "repeat_consistent_both": rep,
           "max_rel": mrel[worst], "worst_field": worst if mrel[worst] > 0 else "",
           "bitwise": v["bitwise_all_fields"], "noise_rule": None,
           "fails": {k: {"max_rel": fields[k]["max_rel"], "max_abs": fields[k]["max_abs"],
                         "n_fail": fields[k].get("n_fail"),
                         "max_rel_per_coord": fields[k].get("max_rel_per_coord")} for k in failing}}
    if v["overall_pass"]:
        out["parity"] = "pass"
    elif failing == ["event_mc_variance"] and masks and rep and \
            fields["event_mc_variance"]["max_rel"] <= g1.MCVAR_FLOOR:
        out["parity"], out["noise_rule"] = "mcvar-noise", "D-mcvar"
    elif failing and set(failing) <= {"n_eff", "sigma2_lnL"} and "n_eff" in failing and masks and rep \
            and fields["log_mu"]["pass"] and fields["selection_log_correction"]["pass"]:
        bad = [i for i, r in enumerate(fields["n_eff"]["max_rel_per_coord"]) if r > summary["rtol"]]
        whole_ok = None
        if whole_summary is not None and whole_summary.get("status") == "compared":
            wf = whole_summary["fields"]
            whole_ok = bool(whole_summary["verdict"]["masks_equal"] and all(
                wf[f]["max_rel_per_coord"][i] <= summary["rtol"]
                for f in wf if f != "decoded_full_parameter_vector" for i in bad))
        amp = None
        if rec_b is not None:
            nd = float(rec_b["dims"]["ndraw"])
            amp = {str(i): float(rec_b["values"]["per_coord"][i]["n_eff"]["value"]) / nd for i in bad}
        out["neff"] = {"failing_coords": bad, "legacy_vs_core_whole_passes_there": whole_ok,
                       "amplification_N_eff_over_N_draw": amp,
                       "sigma2_lnL_also_fails": "sigma2_lnL" in failing}
        if whole_ok:
            out["parity"], out["noise_rule"] = "neff-noise", "D-neff"
        else:
            out["parity"] = "fail"
    else:
        out["parity"] = "fail"
    return out


def row_for(entry, entries, outdir):
    r1, extra = g1.row_for(entry)
    r = {c: r1.get(c, "") for c in COLUMNS}
    rec = _load(entry.get("record")) if entry.get("record") else None
    if rec is not None and rec.get("status") == "ok":
        c = rec["dims"].get("catalog") or {}
        if c:
            r.update(n_rows=c.get("n_rows"), row_width=c.get("n_max"), nside=c.get("nside"),
                     n_pixels_occupied=c.get("n_pixels_occupied_full_catalog"),
                     z_depth=("none" if c.get("z_depth") is None else c.get("z_depth")),
                     n_galaxies=c.get("n_galaxies_full_catalog"))
            extra["catalog_dims"] = {k: c.get(k) for k in (
                "nside", "npix", "n_rows", "n_max", "n_pixels_occupied_full_catalog", "z_depth",
                "n_galaxies_full_catalog", "n_galaxies_rows", "n_rows_occupied", "n_rows_empty",
                "pe_samples_on_empty_rows", "sel_samples_on_empty_rows")}
        extra["per_coord"] = [{
            "index": pc["index"], "kind": pc.get("kind"), "total_logL": pc["total_logL"]["value"],
            "total_finite": pc["total_finite"], "guard_pass": pc["guard_pass"],
            "n_eff": pc["n_eff"]["value"], "pe_variance_sum": pc["pe_variance_sum"]["value"],
            "guard_threshold": pc["guard_threshold"]["value"], "log_mu": pc["log_mu"]["value"]}
            for pc in rec["values"]["per_coord"]]
        extra["ndraw"] = rec["dims"].get("ndraw")
        extra["build_warnings"] = (rec.get("config") or {}).get("build_warnings")
        extra["t_first_call_s"] = rec["timing"]["t_first_call_s"]
        extra["peak_vram_all_phases_mib"] = (rec["timing"].get("peak_device_bytes_all_phases") or 0) / g1.MIB
    comps = entry.get("compares") or {}
    sp = entry["spec"]
    if comps:
        cls = {}
        for k, (ref, cmp_) in enumerate(comps.items()):
            s = _load(cmp_.get("summary"))
            # D-neff reference: legacy vs core whole of the same cell (for a core asis record,
            # its second comparison target is the core whole record, whose own first
            # comparison is legacy vs core whole)
            whole_sum = None
            if sp.get("jit") == "asis":
                wid = next((x for x in comps if "_core_whole_" in x), None)
                we = entries.get(wid) if wid else None
                if we and we.get("compares"):
                    whole_sum = _load(next(iter(we["compares"].values())).get("summary"))
            c = classify(s, whole_sum, rec)
            if c is not None:
                c["catvals"] = catvals(s)
            cls[ref] = c
        first_ref = next(iter(comps))
        c0 = cls[first_ref]
        r["parity_ref"] = first_ref
        if c0 is None:
            r["parity_vs_legacy"] = "n.a."
        else:
            r["parity_vs_legacy"] = c0["parity"]
            if c0["parity"] != "refused":
                r.update(max_rel_vs_legacy=c0["max_rel"], worst_field=c0["worst_field"],
                         bitwise_vs_legacy=c0["bitwise"])
        extra["compares"] = cls
    return r, extra


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", action="append", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--order", default=None, help="spec JSON giving the row order")
    ap.add_argument("--extra-rows", default=None,
                    help="JSON list of extra CSV rows (e.g. OOM / not-run cells) to append")
    a = ap.parse_args(argv)
    entries = {}
    for d in a.outdir:
        with open(os.path.join(d, "index.json")) as f:
            entries.update(json.load(f)["runs"])
    ids = list(entries)
    if a.order:
        with open(a.order) as f:
            order = [s["record_id"] for s in json.load(f)]
        ids = [i for i in order if i in entries] + [i for i in ids if i not in order]
    rows, extras = [], []
    for i in ids:
        r, e = row_for(entries[i], entries, a.outdir)
        rows.append(r)
        extras.append(e)
    if a.extra_rows:
        with open(a.extra_rows) as f:
            for r in json.load(f):
                rows.append({c: r.get(c, "") for c in COLUMNS})
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"columns": COLUMNS, "rows": rows, "extra": extras}, f, indent=1, default=str)
    print(f"{len(rows)} rows -> {a.csv}")


if __name__ == "__main__":
    main()
