"""Implementation-neutral catalog-side summaries of the dark-siren diagnostics.

Both adapters return, per coordinate, per-sample arrays in FILE order (masks,
log p(z|row), and the log weights with the full prior, with only its
catalog-host branch ``log N_obs + log p_cat - log Z`` and with only its
missing-host branch ``log dN_miss - log Z``) and per-row arrays (log N_obs,
log Z, N_miss, f, log depth mass, empty rows). The per-event and selection
BRANCH terms below are reduced here with the same numpy code in both
processes (same inputs in the same order give the same bits), so a difference
between two records is a difference of the implementations' per-sample
values, never of this reduction. Imports numpy only.
"""

from __future__ import annotations

import hashlib
import math

import numpy as np

ROW_KEYS = ("log_Nobs", "log_Z", "N_miss", "f", "log_depth_mass")
SAMPLE_KEYS = ("log_prior",)
CATALOG_SCALAR_FIELDS = ("log_mu_catalog_branch", "log_mu_missing_branch", "log_mu_harness",
                         "sum_N_miss", "sum_log_Z_finite")
CATALOG_ARRAY_FIELDS = ("event_log_evidence_catalog_branch", "event_log_evidence_missing_branch",
                        "event_log_evidence_harness")


def lse(x) -> float:
    """log(sum(exp(x))) over a 1-D array; exactly -inf when no entry is finite."""
    x = np.asarray(x, dtype=np.float64).ravel()
    fin = np.isfinite(x)
    if not fin.any():
        return float("-inf")
    m = float(np.max(x[fin]))
    return m + math.log(float(np.sum(np.exp(x[fin] - m))))


def _sha(a) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def coord_summary(pe, sel, rows, n_events, nsamp, ndraw) -> dict:
    """JSON-ready catalog-side summary of one coordinate (values as float.hex too)."""
    def ent(x):
        x = float(x)
        return {"value": x if math.isfinite(x) else ("nan" if math.isnan(x) else
                                                     ("inf" if x > 0 else "-inf")),
                "hex": x.hex()}

    def arr(xs):
        xs = np.asarray(xs, dtype=np.float64).ravel()
        return {"hex": [float(v).hex() for v in xs], "n": int(xs.size)}

    log_ns = math.log(nsamp)
    log_nd = math.log(ndraw)
    cat_ev, miss_ev, full_ev = [], [], []
    for i in range(n_events):
        sl = slice(i * nsamp, (i + 1) * nsamp)
        cat_ev.append(lse(pe["ldw_cat"][sl]) - log_ns)
        miss_ev.append(lse(pe["ldw_miss"][sl]) - log_ns)
        full_ev.append(lse(pe["ldw"][sl]) - log_ns)
    lz = np.asarray(rows["log_Z"], dtype=np.float64)
    return {
        "event_log_evidence_catalog_branch": arr(cat_ev),
        "event_log_evidence_missing_branch": arr(miss_ev),
        "event_log_evidence_harness": arr(full_ev),
        "log_mu_catalog_branch": ent(lse(sel["ldw_cat"]) - log_nd),
        "log_mu_missing_branch": ent(lse(sel["ldw_miss"]) - log_nd),
        "log_mu_harness": ent(lse(sel["ldw"]) - log_nd),
        "sum_N_miss": ent(float(np.sum(np.asarray(rows["N_miss"], dtype=np.float64)))),
        "sum_log_Z_finite": ent(float(np.sum(lz[np.isfinite(lz)]))),
        "n_rows_empty_state": int(np.asarray(rows["row_empty"], dtype=bool).sum()),
        "row_empty_sha256_u8": _sha(np.asarray(rows["row_empty"], dtype=bool).astype(np.uint8)),
        "rows_sha256": {k: _sha(np.asarray(rows[k], dtype=np.float64)) for k in ROW_KEYS},
        "pe_log_prior_sha256": _sha(np.asarray(pe["log_prior"], dtype=np.float64)),
        "sel_log_prior_sha256": _sha(np.asarray(sel["log_prior"], dtype=np.float64)),
        "pe_log_prior_n_finite": int(np.isfinite(pe["log_prior"]).sum()),
        "sel_log_prior_n_finite": int(np.isfinite(sel["log_prior"]).sum()),
        "note": ("branch evidences / log_mu: numpy logsumexp over the implementation's "
                 "per-sample masked log weights (catalog-host or missing-host branch of the "
                 "prior; harness = full prior), minus log nsamp / log ndraw"),
    }


def stack_npz(per_coord_rows, per_coord_pe, per_coord_sel) -> dict:
    """(n_coords, ...) arrays for the record's catalog sidecar .npz."""
    out = {}
    for k in ROW_KEYS:
        out[f"rows_{k}"] = np.stack([np.asarray(r[k], dtype=np.float64) for r in per_coord_rows])
    out["rows_row_empty"] = np.stack([np.asarray(r["row_empty"], dtype=bool) for r in per_coord_rows])
    out["pe_log_prior"] = np.stack([np.asarray(p["log_prior"], dtype=np.float64) for p in per_coord_pe])
    out["sel_log_prior"] = np.stack([np.asarray(s["log_prior"], dtype=np.float64)
                                     for s in per_coord_sel])
    return out
