#!/usr/bin/env python3
"""Freeze one full fixed-theta strong-lensing partition oracle for L8.

This is intentionally an end-to-end *legacy* probe, not another primitive
fixture. It is derived from the mature ``tests/test_lensing_terms_once.py``
configuration at the pinned legacy SHA, but enumerates every compatible
matching and records the normalized exact-partition marginal likelihood.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import jax
jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp
import numpy as np
from scipy.special import logsumexp

from darksirens.core.types import CosmoParams, EMCatalog, GWEvent, SurveyParams
from darksirens.gw.populations.registry import get_fixed_population_params
from darksirens.lensing.lensed_injections import make_lensed_injection_set
from darksirens.lensing.slmarks import make_sis_lens_params
from darksirens.likelihood.likelihood_with_clusters import (
    CLUSTER_MODE_J2,
    WL_BACKEND_DISABLED,
    darksiren_likelihood_diagnostics_with_clusters,
)
from darksirens.likelihood.pair_kde import make_pair_kde, stack_pair_kdes

LEGACY_SHA = "c042527238bd71421b792936bc48c3b815b90d6d"
N_EVENTS = 8
N_SAMP = 60
N_SEL = 300
N_DRAW = 1000.0
A_TAU = 5.0e-4
EDGES = ((0, 3), (6, 0), (2, 5))
LOG_PRIOR_ODDS = (math.log(1.2), math.log(0.8), math.log(2.0))


def _fixture():
    rng = np.random.default_rng(3)
    total = N_EVENTS * N_SAMP
    gw_pe = GWEvent(
        m1det=jnp.asarray(rng.uniform(20.0, 60.0, total)),
        m2det=jnp.asarray(rng.uniform(10.0, 30.0, total)),
        dL=jnp.asarray(rng.uniform(400.0, 3000.0, total)),
        chieff=jnp.asarray(rng.uniform(-0.3, 0.3, total)),
        prior_wt=jnp.asarray(rng.uniform(0.5, 1.5, total)),
        pixels=jnp.zeros(total, dtype=jnp.int32),
        q=jnp.asarray(rng.uniform(0.3, 1.0, total)),
        valid=jnp.ones(total, dtype=jnp.bool_),
    )
    gw_sel = GWEvent(
        m1det=jnp.asarray(rng.uniform(15.0, 70.0, N_SEL)),
        m2det=jnp.asarray(rng.uniform(8.0, 35.0, N_SEL)),
        dL=jnp.asarray(rng.uniform(200.0, 3000.0, N_SEL)),
        chieff=jnp.asarray(rng.uniform(-0.3, 0.3, N_SEL)),
        prior_wt=jnp.asarray(rng.uniform(0.5, 1.5, N_SEL)),
        pixels=jnp.zeros(N_SEL, dtype=jnp.int32),
        q=jnp.asarray(rng.uniform(0.3, 1.0, N_SEL)),
        valid=jnp.ones(N_SEL, dtype=jnp.bool_),
    )

    n = 300
    y = rng.uniform(0.05, 0.95, n)
    lensed = make_lensed_injection_set(
        source_id=np.repeat(np.arange(n, dtype=np.int32), 2),
        image_id=np.tile(np.array([0, 1], dtype=np.int32), n),
        m1_src=np.repeat(rng.uniform(10.0, 70.0, n), 2),
        q_src=np.repeat(rng.uniform(0.3, 1.0, n), 2),
        z_src=np.repeat(rng.uniform(0.05, 1.5, n), 2),
        chieff=np.repeat(rng.uniform(-0.4, 0.4, n), 2),
        y_source=np.repeat(y, 2),
        mu=np.stack([(1.0 + y) / y, (1.0 - y) / y], axis=1).reshape(-1),
        detected=np.ones(2 * n, dtype=bool),
        p_prop_src=np.full(2 * n, 1.0 / (60 * 0.7 * 1.45 * 0.8)),
        p_prop_y=np.full(2 * n, 1.0 / 0.9),
        n_draw_sources=3000,
    )

    kdes = []
    for e in range(N_EVENTS):
        sl = slice(e * N_SAMP, (e + 1) * N_SAMP)
        kdes.append(
            make_pair_kde(
                np.asarray(gw_pe.m1det[sl]),
                np.asarray(gw_pe.q[sl]),
                np.asarray(gw_pe.dL[sl]),
                np.asarray(gw_pe.chieff[sl]),
                np.asarray(gw_pe.prior_wt[sl]),
            )
        )

    catalog = EMCatalog(
        apix=1.0,
        zgals=jnp.zeros((1, 1)),
        dzgals=jnp.ones((1, 1)),
        wgals=jnp.ones((1, 1)),
        ngals=jnp.ones((1,), dtype=jnp.int32),
        delta_g_pix_z=jnp.zeros((1, 1)),
        dN_obs_kde=None,
        pixel_to_cache_idx=None,
    )
    return dict(
        cosmo=CosmoParams(H0=67.74, Om0=0.3075),
        survey=SurveyParams(
            n0=1e-3,
            z50=1.0,
            w=0.5,
            delta=0.0,
            b_miss=1.0,
            alpha_miss=0.5,
        ),
        pop_params=get_fixed_population_params("powerlaw+peak"),
        gw_pe=gw_pe,
        gw_sel=gw_sel,
        catalog=catalog,
        lensed=lensed,
        pair_kdes=stack_pair_kdes(kdes),
        sis=make_sis_lens_params(A_tau=A_TAU, n_tau=0.0, T0_seconds=1.0),
    )


def _master(fx, singleton_indices, pair_indices, *, pair_batch_size=0):
    singleton_indices = np.asarray(singleton_indices, dtype=np.int32)
    pair_indices = np.asarray(pair_indices, dtype=np.int32).reshape((-1, 2))
    return darksiren_likelihood_diagnostics_with_clusters(
        fx["cosmo"],
        fx["survey"],
        fx["pop_params"],
        fx["gw_pe"],
        fx["catalog"],
        fx["gw_sel"],
        fx["catalog"],
        N_EVENTS,
        N_SAMP,
        N_DRAW,
        singleton_indices=jnp.asarray(singleton_indices),
        pair_indices=jnp.asarray(pair_indices),
        n_singletons=int(singleton_indices.size),
        n_pairs=int(pair_indices.shape[0]),
        lensed_injections=fx["lensed"],
        pair_kdes=fx["pair_kdes"],
        sis_params=fx["sis"],
        log_p_tag_per_source=jnp.zeros(fx["lensed"].n_kept),
        pop_model="powerlaw+peak",
        universe_model="spectral_sirens",
        sel_batch_size=None,
        cluster_mode=CLUSTER_MODE_J2,
        wl_backend=WL_BACKEND_DISABLED,
        pe_event_block=None,
        pair_batch_size=pair_batch_size,
        y_nodes_pair=8,
        singleton_lensing=0,
        selection_neff_soft_guard=True,
        max_likelihood_variance=1e6,
    )


def _valid_matchings():
    out = []
    for r in range(len(EDGES) + 1):
        for subset in itertools.combinations(range(len(EDGES)), r):
            used = set()
            ok = True
            for edge_idx in subset:
                a, b = EDGES[edge_idx]
                if a in used or b in used:
                    ok = False
                    break
                used.update((a, b))
            if ok:
                out.append(tuple(subset))
    return tuple(out)


def _f(x):
    return float(np.asarray(x))


def _flist(x):
    return [float(v) for v in np.asarray(x, dtype=float).ravel()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    fx = _fixture()

    terms = _master(
        fx,
        np.arange(N_EVENTS, dtype=np.int32),
        np.asarray(EDGES, dtype=np.int32),
        pair_batch_size=2,
    )

    partitions = []
    numerators = []
    priors = []
    for subset in _valid_matchings():
        used = {event for edge_idx in subset for event in EDGES[edge_idx]}
        singletons = tuple(i for i in range(N_EVENTS) if i not in used)
        pairs = tuple(EDGES[i] for i in subset)
        diag = _master(fx, singletons, pairs)
        log_prior = sum(LOG_PRIOR_ODDS[i] for i in subset)
        logl = _f(diag["logL_total"])
        priors.append(log_prior)
        numerators.append(log_prior + logl)
        partitions.append({
            "edge_indices": list(subset),
            "singleton_indices": list(singletons),
            "pair_indices": [list(p) for p in pairs],
            "n_singletons": len(singletons),
            "n_pairs": len(pairs),
            "n_sources": len(singletons) + len(pairs),
            "log_prior_weight": log_prior,
            "logL_total": logl,
            "singleton_logL_sum": _f(diag["singleton_logL_sum"]),
            "pair_logL_sum": _f(diag["pair_logL_sum"]),
            "selection_correction_total": _f(diag["selection_correction_total"]),
            "singleton_variance_sum": _f(diag["singleton_variance_sum"]),
            "pair_variance_sum": _f(diag["pair_variance_sum"]),
            "pe_variance_sum": _f(diag["pe_variance_sum"]),
        })

    log_z_prior = float(logsumexp(priors))
    logl_marg = float(logsumexp(numerators) - log_z_prior)

    payload = {
        "schema": "darksirens-lensing-l8-full-parity-1",
        "legacy_sha": LEGACY_SHA,
        "fixture": {
            "seed": 3,
            "n_events": N_EVENTS,
            "nsamp": N_SAMP,
            "n_selection": N_SEL,
            "n_draw_unlensed": N_DRAW,
            "n_draw_lensed": 3000,
            "cosmology": [67.74, 0.3075, -1.0, 0.0],
            "sis": {"A_tau": A_TAU, "n_tau": 0.0, "T0_seconds": 1.0},
            "edges": [list(e) for e in EDGES],
            "log_prior_odds": list(LOG_PRIOR_ODDS),
            "y_nodes_pair": 8,
            "singleton_lensing": "off",
            "weak_lensing": "disabled",
            "selection_neff_soft_guard": True,
        },
        "once_terms": {
            "per_event_logL": _flist(terms["per_event_logL"]),
            "per_event_var": _flist(terms["per_event_var"]),
            "per_pair_logL": _flist(terms["per_pair_logL"]),
            "per_pair_var": _flist(terms["per_pair_var"]),
        },
        "partitions": partitions,
        "log_partition_prior_normalizer": log_z_prior,
        "marginalized_logL": logl_marg,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
