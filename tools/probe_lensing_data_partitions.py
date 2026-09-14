#!/usr/bin/env python3
"""Phase-11 L0D oracle for lensed data and exact partition contracts.

Run only against the pinned legacy tree.  The probe freezes the canonical
per-image lensed-injection HDF5 semantics, its pair/exactly-one load-time views,
and candidate-graph / exact-matching behavior before L6 production work.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
from pathlib import Path

import h5py
import numpy as np

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"


def _tolist(x):
    arr = np.asarray(x)
    if arr.dtype.kind == "b":
        return arr.astype(bool).tolist()
    if arr.dtype.kind in "iu":
        return arr.astype(np.int64).tolist()
    return arr.astype(np.float64).tolist()


def _error(fn):
    try:
        fn()
    except Exception as exc:
        return {"type": type(exc).__name__, "message": str(exc)}
    raise AssertionError("expected failure did not occur")


def _campaign_payload():
    y = np.asarray([0.2, 0.3, 0.4, 0.5], dtype=float)
    mu_plus = (1.0 + y) / y
    mu_minus = (1.0 - y) / y
    src = {
        "m1_src": np.asarray([20.0, 30.0, 40.0, 50.0]),
        "q_src": np.asarray([0.60, 0.70, 0.80, 0.90]),
        "z_src": np.asarray([0.10, 0.20, 0.30, 0.40]),
        "chieff": np.asarray([-0.10, 0.00, 0.10, 0.20]),
        "y_source": y,
        "p_prop_src": np.asarray([0.011, 0.012, 0.013, 0.014]),
        "p_prop_y": np.asarray([1.1, 1.2, 1.3, 1.4]),
    }
    detected_by_source = np.asarray(
        [[True, True], [True, False], [False, True], [False, False]],
        dtype=bool,
    )
    raw = {
        "source_id": np.repeat(np.arange(4, dtype=np.int32), 2),
        "image_id": np.tile(np.asarray([0, 1], dtype=np.int32), 4),
        **{k: np.repeat(v, 2) for k, v in src.items()},
        "mu": np.column_stack([mu_plus, mu_minus]).reshape(-1),
        "detected": detected_by_source.reshape(-1),
    }
    # Deliberately scramble image rows.  The mature loader canonicalizes by
    # stable (source_id, image_id) sorting and must recover the same views.
    order = np.asarray([5, 0, 7, 2, 1, 6, 3, 4], dtype=int)
    raw = {k: np.asarray(v)[order] for k, v in raw.items()}
    optional = {
        "p_tag_per_source": np.asarray([0.90, 0.80, 0.70, 0.60]),
        "snr_image0": np.asarray([15.0, 14.0, 13.0, 12.0]),
        "snr_image1": np.asarray([10.0, 7.0, 9.0, 6.0]),
        "delta_t_obs": np.asarray([100.0, 200.0, 300.0, 400.0]),
        "log_sky_overlap": np.log(np.asarray([0.9, 0.8, 0.7, 0.6])),
        "p_tag_true": np.asarray([0.91, 0.81, 0.71, 0.61]),
        "tagged_pair": np.asarray([True, False, True, False]),
    }
    return raw, optional


def _probe_hdf5(tmp: Path):
    from darksirens.lensing.lensed_injections import (
        load_lensed_injections,
        load_lensed_single_image_set,
        read_fc_pdet_attrs,
        read_pair_orientation_mode,
        save_lensed_injections,
    )

    raw, optional = _campaign_payload()
    path = tmp / "canonical_lensed.h5"
    save_lensed_injections(
        str(path),
        **raw,
        **optional,
        n_draw_sources=10,
        snr_model_attrs={"fc_rho_thr": 8.0, "fc_r0": 1500.0, "fc_mc_bar": 1.22},
    )

    with h5py.File(path, "r") as f:
        disk = {
            "datasets": sorted(f.keys()),
            "dataset_shapes": {k: list(f[k].shape) for k in sorted(f.keys())},
            "dataset_dtypes": {k: str(f[k].dtype) for k in sorted(f.keys())},
            "attrs": {
                k: (v.decode() if isinstance(v, bytes) else v.item() if hasattr(v, "item") else v)
                for k, v in sorted(f.attrs.items())
            },
        }

    pair = load_lensed_injections(str(path))
    singles, default_attrs = load_lensed_single_image_set(
        str(path), return_campaign_attrs=True
    )
    default_orientation = read_pair_orientation_mode(str(path))
    fc_attrs = read_fc_pdet_attrs(str(path))

    pair_view = {
        "source_id_kept": _tolist(pair.source_id_kept),
        "m1_src": _tolist(pair.m1_src),
        "q_src": _tolist(pair.q_src),
        "z_src": _tolist(pair.z_src),
        "chieff": _tolist(pair.chieff),
        "y_source": _tolist(pair.y_source),
        "mu_plus": _tolist(pair.mu_plus),
        "mu_minus": _tolist(pair.mu_minus),
        "p_prop_src": _tolist(pair.p_prop_src),
        "p_prop_y": _tolist(pair.p_prop_y),
        "log_p_tag_per_source": _tolist(pair.log_p_tag_per_source),
        "snr_image0": _tolist(pair.snr_image0),
        "snr_image1": _tolist(pair.snr_image1),
        "delta_t_obs": _tolist(pair.delta_t_obs),
        "log_sky_overlap": _tolist(pair.log_sky_overlap),
        "p_tag_true": _tolist(pair.p_tag_true),
        "tagged_pair": _tolist(pair.tagged_pair),
        "valid": _tolist(pair.valid),
        "n_draw_sources": float(pair.n_draw_sources),
        "n_kept": pair.n_kept,
    }
    single_view = {
        "m1_src": _tolist(singles.m1_src),
        "q_src": _tolist(singles.q_src),
        "z_src": _tolist(singles.z_src),
        "chieff": _tolist(singles.chieff),
        "y_source": _tolist(singles.y_source),
        "mu_det": _tolist(singles.mu_det),
        "mu_partner": _tolist(singles.mu_partner),
        "image_is_plus": _tolist(singles.image_is_plus),
        "p_prop_src": _tolist(singles.p_prop_src),
        "p_prop_y": _tolist(singles.p_prop_y),
        "valid": _tolist(singles.valid),
        "n_draw_sources": float(singles.n_draw_sources),
        "n_kept": singles.n_kept,
    }

    # Explicit campaign orientation overrides the legacy missing-attr default.
    with h5py.File(path, "r+") as f:
        f.attrs["pair_orientation_mode"] = "shared_iota"
    explicit_orientation = read_pair_orientation_mode(str(path))
    _, explicit_attrs = load_lensed_single_image_set(
        str(path), return_campaign_attrs=True
    )

    # The documented old spelling of the normalization attr must still load.
    alias_path = tmp / "alias_lensed.h5"
    with h5py.File(path, "r") as src, h5py.File(alias_path, "w") as dst:
        for key in src.keys():
            src.copy(key, dst)
        for key, val in src.attrs.items():
            if key != "n_draw_sources":
                dst.attrs[key] = val
        dst.attrs["Ndraw_sources"] = 10
    alias_pair = load_lensed_injections(str(alias_path))
    alias_single = load_lensed_single_image_set(str(alias_path))

    # Pin fail-before-replace semantics for a malformed campaign payload.
    guard = tmp / "atomic_guard.bin"
    guard.write_bytes(b"KEEP-ORIGINAL")
    bad_raw = dict(raw)
    bad_raw["p_prop_src"] = np.asarray(raw["p_prop_src"]).copy()
    bad_raw["p_prop_src"][0] = 0.0
    atomic_error = _error(
        lambda: save_lensed_injections(
            str(guard), **bad_raw, **optional, n_draw_sources=10
        )
    )

    # Additional semantic guard pins useful to L6's loader/writer contract.
    low_ndraw_error = _error(
        lambda: save_lensed_injections(
            str(tmp / "bad_ndraw.h5"), **raw, **optional, n_draw_sources=3
        )
    )
    bad_ptag = dict(optional)
    bad_ptag["p_tag_per_source"] = np.asarray([0.9, 1.1, 0.7, 0.6])
    bad_ptag_error = _error(
        lambda: save_lensed_injections(
            str(tmp / "bad_ptag.h5"), **raw, **bad_ptag, n_draw_sources=10
        )
    )

    return {
        "disk_contract": disk,
        "pair_view": pair_view,
        "single_view": single_view,
        "orientation": {
            "missing_attr_default": default_orientation,
            "single_loader_missing_attr": default_attrs["pair_orientation_mode"],
            "explicit_attr": explicit_orientation,
            "single_loader_explicit_attr": explicit_attrs["pair_orientation_mode"],
        },
        "fc_pdet_attrs": fc_attrs,
        "normalization_alias": {
            "pair_n_draw_sources": float(alias_pair.n_draw_sources),
            "single_n_draw_sources": float(alias_single.n_draw_sources),
        },
        "writer_guards": {
            "atomic_error": atomic_error,
            "destination_preserved": guard.read_bytes() == b"KEEP-ORIGINAL",
            "low_ndraw_error": low_ndraw_error,
            "bad_ptag_error": bad_ptag_error,
        },
    }


def _state(s):
    return {
        "singleton_indices": _tolist(s.singleton_indices),
        "pair_indices": _tolist(np.asarray(s.pair_indices).reshape((-1, 2))),
        "candidate_edge_indices": _tolist(s.candidate_edge_indices),
        "n_singletons": int(s.n_singletons),
        "n_pairs": int(s.n_pairs),
        "log_prior_weight": float(s.log_prior_weight),
    }


def _probe_partitions():
    from darksirens.lensing.partitions import (
        connected_components_from_candidate_pairs,
        exact_partition_components,
        exact_partitions_from_json,
        prepare_candidate_pairs_for_partitioning,
        validate_candidate_pairs,
    )

    data = {
        "format_version": "candidate-pairs-1.0",
        "n_events": 6,
        "folded_mark_keys": ["log_mass_distance_score"],
        "pairs": [
            {
                "i": 1, "j": 0, "log_prior_odds": math.log(2.0), "label": "e01",
                "marks": {
                    "delta_t_obs": 12.5, "sigma_delta_t": 2.0,
                    "log_sky_overlap": math.log(1.5),
                    "log_mass_distance_score": math.log(1.2),
                    "log_custom_score": math.log(1.1),
                },
            },
            {
                "i": 1, "j": 2, "log_prior_odds": math.log(3.0), "label": "e12",
                "marks": {
                    "delta_t_obs": 25.0, "sigma_delta_t": 3.0,
                    "log_sky_overlap": math.log(0.8),
                    "log_mass_distance_score": math.log(1.3),
                    "log_custom_score": math.log(0.9),
                },
            },
            {
                "i": 4, "j": 3, "log_prior_odds": math.log(5.0), "label": "e34",
                "marks": {
                    "delta_t_obs": 40.0, "sigma_delta_t": 4.0,
                    "log_sky_overlap": math.log(1.1),
                    "log_mass_distance_score": math.log(1.4),
                    "log_custom_score": math.log(1.05),
                },
            },
        ],
    }

    n_events, raw_pairs, effective_pairs, contributions = (
        prepare_candidate_pairs_for_partitioning(data, ["log_sky_overlap"])
    )
    components = connected_components_from_candidate_pairs(n_events, effective_pairs)
    _, global_states, log_z_global = exact_partitions_from_json(
        data, edge_mark_prior_keys=["log_sky_overlap"], component_mode="global"
    )
    _, componentwise_states, log_z_componentwise = exact_partitions_from_json(
        data,
        edge_mark_prior_keys=["log_sky_overlap"],
        component_mode="componentwise",
        max_total_partitions=100,
    )
    summaries, local_states, total = exact_partition_components(
        n_events, effective_pairs
    )

    folded_error = _error(
        lambda: prepare_candidate_pairs_for_partitioning(
            data, ["log_mass_distance_score"]
        )
    )
    duplicate = {
        "n_events": 2,
        "pairs": [
            {"i": 0, "j": 1, "log_prior_odds": 0.0},
            {"i": 1, "j": 0, "log_prior_odds": 0.0},
        ],
    }
    duplicate_error = _error(lambda: validate_candidate_pairs(duplicate))
    bad_marks = {
        "n_events": 2,
        "pairs": [{
            "i": 0, "j": 1, "log_prior_odds": 0.0,
            "marks": {"delta_t_obs": 1.0},
        }],
    }
    mark_error = _error(lambda: validate_candidate_pairs(bad_marks))
    cap_error = _error(
        lambda: exact_partitions_from_json(data, max_partitions=2)
    )

    def pair_record(p):
        return {
            "i": int(p.i), "j": int(p.j),
            "log_prior_odds": float(p.log_prior_odds),
            "label": p.label,
            "marks": p.marks.to_dict(),
        }

    global_serialized = [_state(s) for s in global_states]
    component_serialized = [_state(s) for s in componentwise_states]
    global_keyset = sorted(
        (tuple(map(tuple, s["pair_indices"])), tuple(s["candidate_edge_indices"]))
        for s in global_serialized
    )
    component_keyset = sorted(
        (tuple(map(tuple, s["pair_indices"])), tuple(s["candidate_edge_indices"]))
        for s in component_serialized
    )

    return {
        "n_events": n_events,
        "raw_pairs": [pair_record(p) for p in raw_pairs],
        "edge_prior_keys": ["log_sky_overlap"],
        "edge_prior_contributions": [float(x) for x in contributions],
        "effective_pairs": [pair_record(p) for p in effective_pairs],
        "components": [
            {
                "event_indices": list(c["event_indices"]),
                "candidate_edge_indices": list(c["candidate_edge_indices"]),
            }
            for c in components
        ],
        "global_states": global_serialized,
        "componentwise_states": component_serialized,
        "global_componentwise_same_matching_set": global_keyset == component_keyset,
        "global_log_z_prior": float(log_z_global),
        "componentwise_log_z_prior": float(log_z_componentwise),
        "component_summaries": [
            {
                "event_indices": list(x["event_indices"]),
                "candidate_edge_indices": list(x["candidate_edge_indices"]),
                "n_partitions": int(x["n_partitions"]),
            }
            for x in summaries
        ],
        "component_local_states": [[_state(s) for s in states] for states in local_states],
        "total_product_partitions": int(total),
        "errors": {
            "folded_mark_double_count": folded_error,
            "duplicate_unordered_pair": duplicate_error,
            "incomplete_time_marks": mark_error,
            "max_partition_cap": cap_error,
        },
    }


def build_reference():
    with tempfile.TemporaryDirectory() as td:
        hdf5 = _probe_hdf5(Path(td))
    partitions = _probe_partitions()
    return {
        "schema": "darksirens-lensing-l0d-data-partition-reference-1",
        "legacy_sha": LEGACY_SHA,
        "hdf5": hdf5,
        "partitions": partitions,
        "contract_notes": {
            "hdf5_storage": "one row per image; pair and exactly-one channels are load-time views of one source campaign",
            "normalization": "selection denominator is total source draws, not retained rows",
            "partition_prior": "unnormalized partition log prior is the sum of included effective edge log_prior_odds",
            "partition_order": "legacy exact enumeration emits the all-singleton matching first and preserves deterministic edge-list DFS order",
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = build_reference()
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
