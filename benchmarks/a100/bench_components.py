#!/usr/bin/env python3
"""Component timing and per-component parity (legacy darksirens vs darksirens-core).

Run mode (one implementation per process, exactly as ``bench_fixed_theta.py``):

    python bench_components.py --impl legacy|core --pe PE.h5 --sel SEL.h5 [--catalog CAT.h5] \\
        --plan PLAN --coords coords.json --out components.json [--device cpu|gpu|auto] \\
        [--n-calls 20 --warmup 3] [--sel-batch none --pe-block none] [--jit whole|asis] \\
        [--main-record MAIN.json] [--cache-dir DIR --cache-mode cold|warm|env] \\
        [--trace DIR] [--components a_cosmology,...] [--full-array-coords 0,1] [--no-aot]

Compare mode (A = the reference of the relative difference, normally legacy):

    python bench_components.py compare A.json B.json [--rtol 1e-12] [--out S.json] [--md S.md]

The model, data, block sizes and kernel are built by the SAME adapters the
fixed-coordinate harness uses (``impl_legacy.LegacyAdapter`` /
``impl_core.CoreAdapter``), for the same plan and coordinates. Every component
is then a separate ``jax.jit`` (each implementation's own
``threads_distance_table`` decorator, so the distance table and the ambient
jit channels are ARGUMENTS) whose data are ARGUMENTS too. Each is warm-timed as
the main harness times the whole likelihood: first call on coords[0] (compile +
run), ``--warmup`` warm-ups on coords[:warmup], ``--n-calls`` timed calls
cycling all coordinates, each ``jax.block_until_ready``; median/min/mean/std;
compile requests counted per phase (the timed loop must issue none).

Components (``COMPONENTS`` below holds the legacy <-> core references):

  a_cosmology     distance table -> dL grid, z(dL) inversion of every PE sample and
                  injection, log Jacobian; spectral plans also the dV/dz grid
  b_population    log p_pop(m1src, q, z, chi_eff | lambda) on PE samples and injections
  c_pop_norm      the normalisations log_p_pop computes: mass-component and spin
                  norms, per-sample pairing normalisers (not a separable kernel in
                  either code; timed as the calls MixtureModel.component_densities makes)
  w_weights       per-sample log importance weights (support mask + finite), given
                  the prepared redshift-prior state (encloses a + b + g)
  d_pe_reduce     per-event log-sum-exp log evidence and MC variance
  e_sel_reduce    selection reduction: log_mu, N_eff, log_sigma2, selection correction
  f_kernel_state  [dark] per-galaxy catalog kernel state (24-node CDF quadrature)
  h_completion    [dark] completion curves (dN_miss, N_miss, C_eff, f)
  fh_prior_state  [dark] the whole per-proposal prior state (encloses f + h)
  g_prior_eval    per-sample log p(z|row) given the state (spectral: volume prior)
  g_prior_eval_unrouted  [legacy dark, routing active] g without the empty-row routing
  i_whole         the whole likelihood: the main harness kernel, same values
  j_transfer      host -> device transfer of the kernel operands (device_put + sync)
  k_layout        [legacy] injection sort by pixel + permutation of the injection arrays

Each component's outputs are stored per coordinate (sha256, shape, min, max,
finite counts) in the record and as float64 arrays in ``<out>.components.npz``
(arrays above ``--big-array-elements`` only for ``--full-array-coords``), in the
FILE order of the PE and selection HDF5 datasets (legacy's pixel-sorted
injections are mapped back), so ``compare`` can check them element by element.

``--trace DIR`` adds an untimed-for-the-record pass per component wrapped in
``jax.profiler.trace`` (``trace_tools.py`` parses it into a top-N op table with
device busy time and idle gaps) and checks that every traced output is
bit-identical to the untraced one.

Exit status: 0 ok; 2 usage/input error; 3 plan assertion failed; 4 build error.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never write __pycache__ into either package tree

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import bench_common as bc  # noqa: E402
import plans  # noqa: E402

RECORD_SCHEMA = "darksirens-bench-components/1"
SUMMARY_SCHEMA = "darksirens-bench-components-compare/1"

# ---------------------------------------------------------------------------
# The name map: what each component measures in each implementation.
# kind: separable   = a public/module function of the implementation, timed as is
#       enclosing   = the smallest enclosing callable (it computes more than the
#                     component), labelled in ``note``
#       transcribed = the implementation computes it inline; the harness runs the
#                     implementation's own leaf functions in the kernel's order
#       isolated    = the calls the implementation makes, lifted out of a larger
#                     function into a kernel of their own
# ---------------------------------------------------------------------------
L_ = "darksirens/"          # legacy c042527 tree
C_ = "src/darksirens/"      # core 88004d9 tree
COMPONENTS = [
    {
        "name": "a_cosmology", "letter": "a", "universe": "both", "additive": True,
        "title": "cosmology tables / distance inversion",
        "legacy_ref": ("utils.cosmology.dL_of_z on utils.cosmology.zgrid (4-D table interpolation) + "
                       "z_of_dL_precomputed on the clamped dL of every PE sample and injection + "
                       "inference.utils.log_jacobian_m1src_q_z_to_m1det_q_dL; spectral: the "
                       "dV/dz grid of redshift.prior.prepare_redshift_prior_state('spectral_sirens') "
                       f"({L_}likelihood/core.py:848-850, {L_}inference/utils.py:64-96,109-163, "
                       f"{L_}redshift/prior.py:328-338)"),
        "core_ref": ("cosmology.distances.dL_of_z on cosmology.distances.zgrid + z_of_dL_precomputed "
                     "+ likelihood.weights.log_jacobian_m1src_q_z_to_m1det_q_dL; spectral: "
                     "cosmology.volume.normalized_comoving_volume_grid "
                     f"({C_}likelihood/hierarchical.py:131-133,262-263, {C_}likelihood/weights.py:67-94,112-164, "
                     f"{C_}cosmology/volume.py:16-30)"),
        "same_quantity": True, "kind": {"legacy": "isolated", "core": "isolated"},
        "note": ("outputs dL_grid, z and log|J| per sample (+ log_pvol for spectral plans). Both "
                 "kernels compute these inside the per-sample weight; here they run as one kernel."),
    },
    {
        "name": "b_population", "letter": "b", "universe": "both", "additive": True,
        "title": "population evaluation (log_p_pop) on PE samples and injections",
        "legacy_ref": ("gw.populations.pop_model_parser(...) = PopulationModel.log_p_pop at "
                       f"m1src = m1det/(1+z) ({L_}gw/populations/base.py:1131-1157, "
                       f"{L_}inference/utils.py:109-163)"),
        "core_ref": ("population.pop_model_parser(...) = PopulationModel.log_p_pop at m1src = "
                     f"m1det/(1+z) ({C_}population/base.py:1132-1158, {C_}likelihood/weights.py:149-164)"),
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": "z is the a_cosmology output; includes the normalisations of c_pop_norm",
    },
    {
        "name": "c_pop_norm", "letter": "c", "universe": "both", "additive": False,
        "title": "pairing / population normalisation",
        "legacy_ref": ("MassComponent._norm (trapezoid on the mass grid), SpinModel._norm and "
                       "PairingModel._panel_norm (exact 2-panel GL branch, per sample) as "
                       f"MixtureModel.component_densities calls them ({L_}gw/populations/base.py:"
                       "883-934 (norms at 896-900), 214-220, 741-748, pairing _panel_norm at 579)"),
        "core_ref": ("the same calls in core's MixtureModel.component_densities "
                     f"({C_}population/base.py:884-935 (norms at 897-901), 214-220, 742-749, pairing _panel_norm at 578)"),
        "same_quantity": True, "kind": {"legacy": "isolated", "core": "isolated"},
        "note": ("not a separable kernel in either code (the smallest enclosing callable is "
                 "log_p_pop = b_population); the normalisation calls are lifted out and timed "
                 "alone, on m1src of the PE samples and injections, one set per mixture component "
                 "(as written; XLA may CSE identical pairing normalisers inside the whole kernel)"),
    },
    {
        "name": "w_weights", "letter": "w", "universe": "both", "additive": False,
        "title": "per-sample log importance weights (encloses a + b + g)",
        "legacy_ref": ("the _ll_given_states weight closures: log_sample_weight on the clamped dL "
                       "with the prepared prior state, then the support/finite mask "
                       f"({L_}likelihood/core.py:1181-1287)"),
        "core_ref": ("hierarchical._weight / _log_weight: log_sample_weight on the clamped dL, "
                     f"then the support/finite mask ({C_}likelihood/hierarchical.py:138-161,268-289)"),
        "same_quantity": True, "kind": {"legacy": "transcribed", "core": "transcribed"},
        "note": ("the prepared prior state is an INPUT (dark: fh_prior_state output; spectral legacy: "
                 "the a_cosmology log_pvol grid), so w excludes the state build; core spectral "
                 "re-normalises dV/dz inside (log_comoving_volume_prior), as its kernel does"),
    },
    {
        "name": "d_pe_reduce", "letter": "d", "universe": "both", "additive": True,
        "title": "PE event reduction (per-event log-sum-exp and MC variance)",
        "legacy_ref": ("inline in _ll_given_states: structural mask + blocked vmap of "
                       "likelihood.selection.log_evidence_and_mc_variance with "
                       f"likelihood.core._pe_chunk_plan ({L_}likelihood/core.py:1360-1492); "
                       "TRANSCRIBED (no separable legacy function)"),
        "core_ref": ("likelihood.event.reduce_pe_events with a pass-through weight function over "
                     f"the precomputed weights ({C_}likelihood/event.py:28-140)"),
        "same_quantity": True, "kind": {"legacy": "transcribed", "core": "separable"},
        "note": "input: the w_weights PE log weights of the same coordinate",
    },
    {
        "name": "e_sel_reduce", "letter": "e", "universe": "both", "additive": True,
        "title": "selection reduction (log_mu, N_eff, selection correction)",
        "legacy_ref": ("likelihood.selection.selection_reduce_from_ldw_provider + "
                       f"selection_log_correction ({L_}likelihood/selection.py:414-461, 269-413)"),
        "core_ref": ("selection.gw.selection_reduce_from_ldw_provider + selection_log_correction "
                     f"({C_}selection/gw.py:415-471, 270-414)"),
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": ("the provider form is documented bit-identical to compute_selection_term's "
                 "reduction in both trees; input: the w_weights injection log weights (legacy in "
                 "its pixel-sorted injection order) and the d_pe_reduce variance sum"),
    },
    {
        "name": "f_kernel_state", "letter": "f", "universe": "dark", "additive": False,
        "title": "catalog kernel construction",
        "legacy_ref": ("redshift.completion.log_galaxy_measure_grid + redshift.catalog."
                       "catalog_kernel_state(log_g_grid, z_depth, pinned=em.pinned_kernels, "
                       f"kde_window) ({L_}redshift/catalog.py:1245-1312, {L_}redshift/prior.py:488,618-623)"),
        "core_ref": f"catalog.redshift.build_catalog_kernel_state ({C_}catalog/redshift.py:250-285)",
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": "legacy includes its H0 kernel pin when the factory installed one (never for dark_full)",
    },
    {
        "name": "h_completion", "letter": "h", "universe": "dark", "additive": False,
        "title": "completion curves",
        "legacy_ref": f"redshift.completion.completion_curves ({L_}redshift/completion.py:2050)",
        "core_ref": ("catalog.completeness.completion_curves(..., observed_cache) "
                     f"({C_}catalog/completeness.py:291-300)"),
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": "C_eff and f are diagnostics in both codes (informational); dN_miss / N_miss enter the prior",
    },
    {
        "name": "fh_prior_state", "letter": "f+h", "universe": "dark", "additive": True,
        "title": "per-proposal dark-siren prior state (encloses f + h)",
        "legacy_ref": ("redshift.prior.prepare_redshift_prior_state('dark_sirens', ..., "
                       "materialize_state, catalog_sky_weighting='conditional') "
                       f"({L_}redshift/prior.py:398-713); built ONCE per call (PE/selection share it, "
                       f"{L_}likelihood/core.py:1058-1087)"),
        "core_ref": ("catalog.models.build_incomplete_catalog_prior_state "
                     f"({C_}catalog/models.py:95-120); built TWICE per call as written "
                     f"({C_}likelihood/hierarchical.py:369-374)"),
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": "log_Nobs and log_Z per row; dN_miss equals h_completion's",
    },
    {
        "name": "g_prior_eval", "letter": "g", "universe": "both", "additive": True,
        "title": "redshift prior evaluation per sample",
        "legacy_ref": ("redshift.prior.eval_redshift_prior_with_state(model, state, z, pix, ...,"
                       "empty_routing=<factory plan>) for PE and injections "
                       f"({L_}redshift/prior.py:1234-1298)"),
        "core_ref": ("dark: catalog.models.eval_incomplete_catalog_prior_state_vmap "
                     f"({C_}catalog/models.py:123-153); spectral: cosmology.volume."
                     f"log_comoving_volume_prior ({C_}cosmology/volume.py:33-44)"),
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": ("z from a_cosmology, state from fh_prior_state. Spectral core is ENCLOSING: it "
                 "re-normalises the dV/dz grid per side, which legacy does once in its prepared "
                 "state (a_cosmology). Per-sample log densities are compared under D-catvals "
                 "(|delta log p| <= 1e-12 absolute, informational)"),
    },
    {
        "name": "g_prior_eval_unrouted", "letter": "g'", "universe": "dark", "additive": False,
        "title": "legacy redshift prior evaluation WITHOUT the empty-row routing plan",
        "legacy_ref": "g_prior_eval with empty_routing=None (layout effect of the routing plan)",
        "core_ref": "n/a (core has no routing)",
        "same_quantity": True, "kind": {"legacy": "separable", "core": "not_applicable"},
        "note": "only when the legacy factory built a routing plan for a side",
    },
    {
        "name": "i_whole", "letter": "i", "universe": "both", "additive": False,
        "title": "whole likelihood (the main harness kernel)",
        "legacy_ref": f"likelihood.factory.make_likelihood closure ({L_}likelihood/factory.py:945-1024)",
        "core_ref": "BoundAnalysis.__call__ under threads_distance_table jit (--jit whole) or eager",
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": "adapter.timed_call: must be bit-identical to the main harness at the same coordinates",
    },
    {
        "name": "j_transfer", "letter": "j", "universe": "both", "additive": False,
        "title": "host -> device transfer of the kernel operands",
        "legacy_ref": "jax.device_put of likelihood.operands + distance table + smoothing operator",
        "core_ref": "jax.device_put of gw_pe, gw_selection [, catalog, cache] + distance table",
        "same_quantity": True, "kind": {"legacy": "separable", "core": "separable"},
        "note": ("host numpy copies of the operands, device_put + block_until_ready per call; on CPU "
                 "this is a host copy (or alias), on GPU the real H2D transfer; outputs none"),
    },
    {
        "name": "k_layout", "letter": "k", "universe": "both", "additive": False,
        "title": "data layout: legacy injection sort before the kernel",
        "legacy_ref": ("likelihood.factory._injection_pixel_order (stable numpy argsort of the "
                       "per-injection compact pixel) + _permute_rows of the per-injection arrays "
                       f"({L_}likelihood/factory.py:1140-1163, 1506-1511, 2684-2693)"),
        "core_ref": "not applicable: core keeps the file order (no re-ordering before the kernel)",
        "same_quantity": False, "kind": {"legacy": "separable", "core": "not_applicable"},
        "note": ("a ONE-TIME build step (not per likelihood call), timed like a component; the "
                 "empty-row routing plans are built at factory time too (not timed here; their "
                 "per-call effect is g_prior_eval vs g_prior_eval_unrouted)"),
    },
]
COMPONENT_BY_NAME = {c["name"]: c for c in COMPONENTS}
ORDER = [c["name"] for c in COMPONENTS]

# Output classes: gate = rtol parity; catvals = D-catvals |delta| <= 1e-12 absolute
# (informational); info = diagnostic, informational; derived = a copy of another
# output, compared by digest only.
OUTPUT_CLASS = {
    ("g_prior_eval", "log_prior_pe"): "catvals", ("g_prior_eval", "log_prior_sel"): "catvals",
    ("g_prior_eval_unrouted", "log_prior_pe"): "catvals",
    ("g_prior_eval_unrouted", "log_prior_sel"): "catvals",
    ("h_completion", "C_eff"): "info", ("h_completion", "f"): "info",
    # digest only (== h_completion dN_miss inside each record; see DIGEST_ONLY)
    ("fh_prior_state", "dN_miss"): "derived",
}


def output_class(comp, key):
    return OUTPUT_CLASS.get((comp, key), "gate")


#: Outputs compared only where a same-component mask is 0. The per-row offset
#: ``log_kw_eff_rowmax`` is a don't-care value on galaxy-free rows: the evaluator
#: returns -inf there whatever the offset (``row_empty``; legacy redshift/catalog.py
#: CatalogKernelState.row_empty, core catalog/redshift.py:309). Legacy's H0-pinned
#: builder stores ``rowmax + shift`` (redshift/catalog.py:1218), i.e. the scalar
#: shift 3 ln(H0/67.74) on those rows, where the unpinned rule (and core) clamps to
#: 0.0 (legacy catalog.py:1136-1148). The unmasked difference is still reported.
MASKED_BY = {("f_kernel_state", "log_kw_eff_rowmax"): ("row_empty", "rows with row_empty == 1 "
                                                       "(offset unused: the evaluator returns -inf)")}


#: Outputs never written to the npz (digest only): fh_prior_state's dN_miss is the
#: h_completion array (the record checks the digests are equal per coordinate).
DIGEST_ONLY = {("fh_prior_state", "dN_miss")}


def store_policy(comp, key, size, k, big, full_coords):
    """Whether coordinate k's array of this output goes into the npz."""
    if (comp, key) in DIGEST_ONLY:
        return False
    if size <= big:
        return True
    if output_class(comp, key) == "info":
        return k == (full_coords[0] if full_coords else 0)
    return k in full_coords


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _sha(a) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _array_digest(a) -> dict:
    a = np.asarray(a)
    d = {"shape": list(a.shape), "dtype": a.dtype.str, "sha256": _sha(a)}
    if a.dtype.kind == "f":
        fin = np.isfinite(a)
        d.update(n_finite=int(fin.sum()), n_nan=int(np.isnan(a).sum()),
                 n_posinf=int(np.isposinf(a).sum()), n_neginf=int(np.isneginf(a).sum()),
                 min=bc.fval(a[fin].min()) if fin.any() else None,
                 max=bc.fval(a[fin].max()) if fin.any() else None)
    elif a.dtype.kind in "biu":
        d.update(sum=int(a.astype(np.int64).sum()))
    return d


def _to_host(x):
    """Numpy copy of a component output leaf (bool -> uint8, numbers -> float64)."""
    a = np.asarray(x)
    if a.dtype == bool:
        return a.astype(np.uint8)
    if a.dtype.kind in "iu":
        return a.astype(np.int64)
    return a.astype(np.float64)


def _block_arg(v: str) -> str:
    v = str(v).strip().lower()
    if v in ("none", "default"):
        return v
    n = int(v)
    if n < 1:
        raise argparse.ArgumentTypeError("block size must be >= 1")
    return str(n)


class FirstCall:
    """Wraps a component kernel; records the first invocation (compile + run)."""

    def __init__(self, fn, counter, jax, context):
        self.fn = fn
        self.counter = counter
        self.jax = jax
        self.record = None
        self.context = context

    def __call__(self, *args, **kw):
        if self.record is not None:
            return self.fn(*args, **kw)
        snap = self.counter.snapshot()
        t0 = time.perf_counter()
        out = self.fn(*args, **kw)
        self.jax.block_until_ready(out)
        self.record = {"t_first_call_s": time.perf_counter() - t0,
                       "compile": self.counter.delta(snap), "context": self.context["phase"]}
        return out


# ---------------------------------------------------------------------------
# Shared (implementation-neutral) pieces operating on each implementation's objects
# ---------------------------------------------------------------------------
def pop_norm_terms(mix, theta_mix, m1_pe, m1_sel, quad, jnp):
    """The normalisation calls ``MixtureModel.component_densities`` makes
    (legacy gw/populations/base.py:883-934, core population/base.py:884-935; the
    MixtureModel class text is identical in both trees), lifted out: mass-component
    norms, spin norms, and per mixture component the exact-branch pairing normaliser
    ``_panel_norm`` (legacy base.py:579, core base.py:578) at every sample."""
    w, tm_list, tp_list, ts_list = mix._split_theta(theta_mix)
    out = {}
    for i, c in enumerate(mix.mass_components):
        out[f"mass_norm_{i}"] = c._norm(tm_list[i])
    for i, c in enumerate(mix.spin_components):
        out[f"spin_norm_{i}"] = c._norm(ts_list[0] if mix.shared_spin else ts_list[i])
    edge = mix._low_mass_edge(tm_list)
    t_p, w_p = quad()
    for i in range(mix.k):
        c_m = mix.mass_components[i]
        tm = tm_list[i]
        c_p = mix.pairing_components[0 if mix.shared_pairing else i]
        tp = tp_list[0 if mix.shared_pairing else i]
        mmin, dmmin = edge
        if hasattr(c_m, "m_min_spec"):
            mmin = tm[c_m.param_specs.index(c_m.m_min_spec)]
        if hasattr(c_m, "dm_min_spec"):
            dmmin = tm[c_m.param_specs.index(c_m.dm_min_spec)]
        for s, m1 in (("pe", m1_pe), ("sel", m1_sel)):
            n_sc, scale = c_p._panel_norm(jnp.atleast_1d(m1), mmin, dmmin, tp, t_p, w_p)
            out[f"pair_nsc_{s}_{i}"] = n_sc
            out[f"pair_scale_{s}_{i}"] = scale
    return out


def pop_norm_available(model, settings):
    mix = getattr(model, "mixture", None)
    if mix is None or not hasattr(model, "mixture_theta"):
        return False, (f"population model {type(model).__name__} is not a grammar mixture: the "
                       "normalisations are not separable from log_p_pop (use b_population)")
    if getattr(settings, "pairing_m1_grid", None) is not None:
        return False, ("pairing_m1_grid is set (opt-in grid branch): the per-sample pairing "
                       "normaliser is interpolated, not the exact branch this component times")
    return True, None


def pad_selection(jnp, ldw, valid, pwt, bs):
    """Pad to a multiple of the batch as compute_selection_term does (padded rows are
    invalid, so they contribute -inf either way)."""
    if bs is None:
        return ldw, valid, pwt
    n = int(ldw.shape[0])
    pad = (-n) % int(bs)
    if pad == 0:
        return ldw, valid, pwt
    return (jnp.concatenate([ldw, jnp.full((pad,), -jnp.inf, ldw.dtype)]),
            jnp.concatenate([valid, jnp.zeros((pad,), bool)]),
            jnp.concatenate([pwt, jnp.ones((pad,), pwt.dtype)]))


# ---------------------------------------------------------------------------
# core
# ---------------------------------------------------------------------------
class CoreComponents:
    impl = "core"

    def __init__(self, adapter, plan):
        import jax
        import jax.numpy as jnp
        from jax import lax

        from darksirens.cosmology import distances as D
        from darksirens.cosmology.distances import dL_of_z, threads_distance_table, z_of_dL_precomputed
        from darksirens.cosmology.distances import zgrid as distance_zgrid
        from darksirens.cosmology.volume import log_comoving_volume_prior, normalized_comoving_volume_grid
        from darksirens.gw.types import GWEvent
        from darksirens.likelihood.event import reduce_pe_events
        from darksirens.likelihood.weights import log_jacobian_m1src_q_z_to_m1det_q_dL, log_sample_weight
        from darksirens.population import pop_model_parser
        from darksirens.population.registry import get_model
        from darksirens.population.utils import get_pairing_panel_quadrature, normalization_grid_settings
        from darksirens.runtime_binding import _decode_theta
        from darksirens.selection.gw import selection_log_correction, selection_reduce_from_ldw_provider

        self.jax, self.jnp = jax, jnp
        self.adapter = adapter
        a = adapter
        b = a.bound
        an = a.analysis
        embed = a.embed
        pop = an.population
        dark = a.dark
        self.dark = dark
        tdt = threads_distance_table
        self.n_inj = int(a.injections.n_injections)
        self.n_pe = int(b.gw_pe.dL.shape[0])
        self.gw_pe, self.gw_sel = b.gw_pe, b.gw_selection
        self.catalog, self.cache = b.catalog, b.observed_density_cache
        self.ambient = D._AMBIENT_JIT_CHANNELS
        self.distance_table = D.distance_table
        popkw = dict(shared_beta=pop.shared_beta, shared_spin=pop.shared_spin,
                     shared_gamma=pop.shared_gamma)
        log_p_pop = pop_model_parser(pop_model=pop.model_name, **popkw)
        model = get_model(pop.model_name, **popkw)
        self.norm_available, self.norm_reason = pop_norm_available(model, normalization_grid_settings())
        z_depth = b.z_depth
        n_ev, ns = int(b.n_events), int(b.nsamp)
        peb, sbs, n_draw = b.pe_event_block, b.sel_batch_size, float(b.n_draw)
        soft, maxvar = b.selection_neff_soft_guard, b.max_likelihood_variance
        self.routing_active = False

        def decode(theta):
            return _decode_theta(an, embed(theta), z_depth=z_depth)

        @tdt()
        def comp_a(theta, dL_pe, dL_sel, distance_table=None):
            cosmo = decode(theta)[0]
            dLg = dL_of_z(distance_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dLg[0], dLg[-1]
            out = {"dL_grid": dLg}
            for s, dL in (("pe", dL_pe), ("sel", dL_sel)):
                dLc = jnp.clip(dL, lo, hi)
                z = z_of_dL_precomputed(dLc, dLg)
                out["z_" + s] = z
                out["logJ_" + s] = log_jacobian_m1src_q_z_to_m1det_q_dL(
                    z, dLc, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            if not dark:
                pvol = normalized_comoving_volume_grid(cosmo)
                out["log_pvol"] = jnp.log(jnp.maximum(pvol, jnp.finfo(pvol.dtype).tiny))
            return out

        @tdt()
        def comp_b(theta, gw_pe, gw_sel, z_pe, z_sel, distance_table=None):
            p = decode(theta)[1]
            out = {}
            for s, gw, z in (("pe", gw_pe, z_pe), ("sel", gw_sel, z_sel)):
                m1src = gw.m1det / (1.0 + z)
                if gw.spin is None:
                    out["lpop_" + s] = log_p_pop(m1src, gw.q, z, gw.chieff, p)
                else:
                    out["lpop_" + s] = log_p_pop(m1src, gw.q, z, gw.chieff, p, spin=gw.spin)
            return out

        @tdt()
        def comp_c(theta, m1src_pe, m1src_sel, distance_table=None):
            p = decode(theta)[1]
            return pop_norm_terms(model.mixture, model.mixture_theta(p), m1src_pe, m1src_sel,
                                  get_pairing_panel_quadrature, jnp)

        if dark:
            from darksirens.catalog.completeness import completion_curves
            from darksirens.catalog.models import (
                build_incomplete_catalog_prior_state,
                eval_incomplete_catalog_prior_state_vmap,
            )
            from darksirens.catalog.redshift import build_catalog_kernel_state

        @tdt()
        def comp_w(theta, gw_pe, gw_sel, catalog, state, distance_table=None):
            cosmo, p, _cat, _ang = decode(theta)
            dLg = dL_of_z(distance_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dLg[0], dLg[-1]
            if dark:
                def prior(z, pix, cat_):
                    return eval_incomplete_catalog_prior_state_vmap(z, pix, state, cat_)
            else:
                def prior(z, _pix, _cat):
                    return log_comoving_volume_prior(z, cosmo)

            def weight(gw):
                supported = (gw.dL >= lo) & (gw.dL <= hi)
                dLc = jnp.clip(gw.dL, lo, hi)
                ldw = log_sample_weight(gw.m1det, gw.q, dLc, gw.chieff, gw.pixels, gw.prior_wt,
                                        cosmo, None, p, catalog, log_p_pop, prior, spin=gw.spin,
                                        dL_grid=dLg)
                return jnp.where(supported & jnp.isfinite(ldw), ldw, -jnp.inf)
            return {"ldw_pe": weight(gw_pe), "ldw_sel": weight(gw_sel)}

        def passthrough(m1det, q, dL, chieff, pix, pwt, spin=None):
            return m1det

        @tdt()
        def comp_d(ldw_pe, valid_pe, pwt_pe, distance_table=None):
            ev = GWEvent(m1det=ldw_pe, m2det=ldw_pe, dL=ldw_pe, chieff=ldw_pe, prior_wt=pwt_pe,
                         pixels=ldw_pe, q=ldw_pe, valid=valid_pe)
            lls, var = reduce_pe_events(ev, n_ev, ns, passthrough, pe_event_block=peb)
            return {"event_lls": lls, "event_vars": var}

        @tdt()
        def comp_e(ldw_sel, valid_sel, pwt_sel, pe_var_sum, distance_table=None):
            ldw, valid, pwt = pad_selection(jnp, ldw_sel, valid_sel, pwt_sel, sbs)
            n_sel = int(ldw.shape[0])

            def provider(start, size):
                sl = lambda arr: lax.dynamic_slice_in_dim(arr, start, size)  # noqa: E731
                x = sl(ldw)
                ok = sl(valid) & (sl(pwt) > 0.0)
                return jnp.where(ok & jnp.isfinite(x), x, -jnp.inf)
            log_mu, n_eff, log_s2 = selection_reduce_from_ldw_provider(provider, n_sel, n_draw, sbs)
            sel_ll = selection_log_correction(log_mu, n_eff, n_ev, soft_guard=soft,
                                              max_likelihood_variance=maxvar,
                                              pe_variance_sum=pe_var_sum)
            return {"log_mu": log_mu, "n_eff": n_eff, "log_sigma2": log_s2,
                    "selection_log_correction": sel_ll}

        fns = {"a_cosmology": comp_a, "b_population": comp_b, "c_pop_norm": comp_c,
               "w_weights": comp_w, "d_pe_reduce": comp_d, "e_sel_reduce": comp_e}
        if dark:
            @tdt()
            def comp_f(theta, catalog, distance_table=None):
                cosmo, _p, cat, _ang = decode(theta)
                return build_catalog_kernel_state(cosmo, cat, catalog)

            @tdt()
            def comp_h(theta, catalog, cache, distance_table=None):
                cosmo, _p, cat, _ang = decode(theta)
                return completion_curves(cosmo, cat, catalog, cache)

            @tdt()
            def comp_state(theta, catalog, cache, distance_table=None):
                cosmo, _p, cat, _ang = decode(theta)
                return build_incomplete_catalog_prior_state(cosmo, cat, catalog, cache)

            @tdt()
            def comp_g(z_pe, pix_pe, z_sel, pix_sel, state, catalog, distance_table=None):
                return {"log_prior_pe": eval_incomplete_catalog_prior_state_vmap(z_pe, pix_pe, state, catalog),
                        "log_prior_sel": eval_incomplete_catalog_prior_state_vmap(z_sel, pix_sel, state,
                                                                                  catalog)}
            fns.update(f_kernel_state=comp_f, h_completion=comp_h, fh_prior_state=comp_state,
                       g_prior_eval=comp_g)
        else:
            @tdt()
            def comp_g(theta, z_pe, z_sel, distance_table=None):
                cosmo = decode(theta)[0]
                return {"log_prior_pe": log_comoving_volume_prior(z_pe, cosmo),
                        "log_prior_sel": log_comoving_volume_prior(z_sel, cosmo)}
            fns["g_prior_eval"] = comp_g
        self.fns = fns
        self.n_state_builds = 2 if dark else 0
        self.state_builds_note = ("core builds the incomplete-catalog prior state twice per call "
                                  "(PE and selection, likelihood/hierarchical.py:369-374) from the "
                                  "same catalog; XLA may CSE the duplicate inside the whole jit"
                                  if dark else None)

    # -- per-coordinate inputs (untimed) --------------------------------------
    def sel_to_file(self, a):
        """Selection-side per-sample array in FILE order (core keeps it; unpadded prefix)."""
        return np.asarray(a)[: self.n_inj]

    def state_args(self, state):
        return state

    def build_calls(self, coords, fc):
        """Return {component: call(k)} plus the precomputed per-coordinate inputs."""
        jnp = self.jnp
        pe, sel = self.gw_pe, self.gw_sel
        cat, cache = self.catalog, self.cache
        n = coords.shape[0]
        th = lambda k: jnp.asarray(coords[k])  # noqa: E731  (as the main harness: inside the call)
        A, S, W, Dd, PV = {}, {}, {}, {}, {}
        for k in range(n):
            A[k] = fc["a_cosmology"](th(k), pe.dL, sel.dL)
            if self.dark:
                S[k] = fc["fh_prior_state"](th(k), cat, cache)
            W[k] = fc["w_weights"](th(k), pe, sel, cat, S.get(k))
            Dd[k] = fc["d_pe_reduce"](W[k]["ldw_pe"], pe.valid, pe.prior_wt)
            PV[k] = jnp.sum(Dd[k]["event_vars"])
        M1 = {k: (pe.m1det / (1.0 + A[k]["z_pe"]), sel.m1det / (1.0 + A[k]["z_sel"])) for k in range(n)}
        calls = {
            "a_cosmology": lambda k: fc["a_cosmology"](th(k), pe.dL, sel.dL),
            "b_population": lambda k: fc["b_population"](th(k), pe, sel, A[k]["z_pe"], A[k]["z_sel"]),
            "w_weights": lambda k: fc["w_weights"](th(k), pe, sel, cat, S.get(k)),
            "d_pe_reduce": lambda k: fc["d_pe_reduce"](W[k]["ldw_pe"], pe.valid, pe.prior_wt),
            "e_sel_reduce": lambda k: fc["e_sel_reduce"](W[k]["ldw_sel"], sel.valid, sel.prior_wt, PV[k]),
        }
        if self.norm_available:
            calls["c_pop_norm"] = lambda k: fc["c_pop_norm"](th(k), M1[k][0], M1[k][1])
        if self.dark:
            calls.update({
                "f_kernel_state": lambda k: fc["f_kernel_state"](th(k), cat),
                "h_completion": lambda k: fc["h_completion"](th(k), cat, cache),
                "fh_prior_state": lambda k: fc["fh_prior_state"](th(k), cat, cache),
                "g_prior_eval": lambda k: fc["g_prior_eval"](A[k]["z_pe"], pe.pixels, A[k]["z_sel"],
                                                             sel.pixels, S[k], cat),
            })
        else:
            calls["g_prior_eval"] = lambda k: fc["g_prior_eval"](th(k), A[k]["z_pe"], A[k]["z_sel"])
        # component (args for jaxpr / AOT evidence at coordinate 0)
        args0 = {
            "a_cosmology": ((th(0), pe.dL, sel.dL), {}),
            "b_population": ((th(0), pe, sel, A[0]["z_pe"], A[0]["z_sel"]), {}),
            "c_pop_norm": ((th(0), M1[0][0], M1[0][1]), {}),
            "w_weights": ((th(0), pe, sel, cat, S.get(0)), {}),
            "d_pe_reduce": ((W[0]["ldw_pe"], pe.valid, pe.prior_wt), {}),
            "e_sel_reduce": ((W[0]["ldw_sel"], sel.valid, sel.prior_wt, PV[0]), {}),
        }
        if self.dark:
            args0.update({
                "f_kernel_state": ((th(0), cat), {}),
                "h_completion": ((th(0), cat, cache), {}),
                "fh_prior_state": ((th(0), cat, cache), {}),
                "g_prior_eval": ((A[0]["z_pe"], pe.pixels, A[0]["z_sel"], sel.pixels, S[0], cat), {}),
            })
        else:
            args0["g_prior_eval"] = ((th(0), A[0]["z_pe"], A[0]["z_sel"]), {})
        self._keep = (A, S, W, Dd, PV, M1)
        return calls, args0

    def data_arrays(self):
        b = self.adapter.bound
        d = {"gw_pe.m1det": b.gw_pe.m1det, "gw_pe.dL": b.gw_pe.dL, "gw_pe.prior_wt": b.gw_pe.prior_wt,
             "gw_sel.m1det": b.gw_selection.m1det, "gw_sel.dL": b.gw_selection.dL,
             "gw_sel.prior_wt": b.gw_selection.prior_wt, "distance_table": self.distance_table()}
        if self.dark:
            d.update({"catalog.zgals": b.catalog.zgals, "catalog.dzgals": b.catalog.dzgals,
                      "catalog.wgals": b.catalog.wgals,
                      "cache.dN_obs_kde": b.observed_density_cache.dN_obs_kde})
        return d

    def jit_kwargs(self):
        return {"distance_table": self.distance_table(),
                "_ambient_extras": tuple(res() for res, _ in self.ambient)}

    def extract(self, name, out):
        """Component output -> {key: numpy array} in FILE order."""
        return extract_outputs(name, out, self.sel_to_file)

    def layout_call(self):
        return None, ("not applicable: core keeps the PE and selection samples in file order "
                      "and re-orders nothing before the kernel")


# ---------------------------------------------------------------------------
# legacy
# ---------------------------------------------------------------------------
class LegacyComponents:
    impl = "legacy"

    def __init__(self, adapter, plan):
        import jax
        import jax.numpy as jnp
        from jax import lax

        from darksirens.gw.populations import pop_model_parser
        from darksirens.gw.populations.registry import get_model
        from darksirens.gw.populations.utils import get_pairing_panel_quadrature, normalization_grid_settings
        from darksirens.inference.utils import log_jacobian_m1src_q_z_to_m1det_q_dL, log_sample_weight
        from darksirens.likelihood.core import _pe_chunk_plan, redshift_prior_state_sharing, selection_prior_model
        from darksirens.likelihood.factory import _resolve_redshift_prior_materialization
        from darksirens.likelihood.selection import (
            log_evidence_and_mc_variance,
            selection_log_correction,
            selection_reduce_from_ldw_provider,
        )
        from darksirens.redshift.prior import eval_redshift_prior_with_state, prepare_redshift_prior_state
        from darksirens.utils import cosmology as UC
        from darksirens.utils.cosmology import dL_of_z, threads_distance_table, z_of_dL_precomputed
        from darksirens.utils.cosmology import zgrid as cosmo_zgrid

        self.jax, self.jnp = jax, jnp
        self.adapter = a = adapter
        lk, opts, dec = a.likelihood, a.opts, a.decoder
        dark = a.dark
        self.dark = dark
        tdt = threads_distance_table
        self.n_inj = int(a.n_injections)
        self.n_pe = int(a.gw_pe.dL.shape[0])
        self.sel_order = np.asarray(a.sel_order, dtype=np.int64)
        self.gw_pe, self.gw_sel, self.em_pe, self.em_sel = a.gw_pe, a.gw_sel, a.em_pe, a.em_sel
        self.ambient = UC._AMBIENT_JIT_CHANNELS
        self.distance_table = UC.distance_table
        self.lk = lk
        p = plan
        popkw = dict(shared_beta=p["shared_beta"], shared_spin=p["shared_spin"],
                     shared_gamma=p["shared_gamma"])
        log_p_pop = pop_model_parser(pop_model=p["population_model"], **popkw)
        model = get_model(p["population_model"], **popkw)
        self.norm_available, self.norm_reason = pop_norm_available(model, normalization_grid_settings())
        pe_model = a.universe_model
        sel_model = selection_prior_model(pe_model)
        materialize = bool(_resolve_redshift_prior_materialization(opts))
        sw = getattr(opts, "catalog_sky_weighting", "conditional")
        kde_window = getattr(lk, "kde_window", None)
        share = redshift_prior_state_sharing(pe_model, (a.em_pe,), (a.em_sel,))
        self.share0 = bool(share[0]) if share else False
        routing = lk.empty_row_routing if dark else ()
        self.rt_pe = routing[0][0] if routing else None
        self.rt_sel = routing[0][1] if routing else None
        self.routing_active = (self.rt_pe is not None) or (self.rt_sel is not None)
        n_ev, ns = int(a.n_events), int(a.nsamp)
        peb, sbs, n_draw = a.pe_event_block, a.sel_batch_size, float(a.ndraw)
        soft, maxvar = a.soft_guard, a.max_likelihood_variance

        def decode(coord):
            return dec.decode(coord)

        @tdt()
        def comp_a(coord, dL_pe, dL_sel, distance_table=None):
            cosmo, survey, _p, _sky, _marks = decode(coord)
            dLg = dL_of_z(cosmo_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dLg[0], dLg[-1]
            out = {"dL_grid": dLg}
            for s, dL in (("pe", dL_pe), ("sel", dL_sel)):
                dLc = jnp.clip(dL, lo, hi)
                z = z_of_dL_precomputed(dLc, dLg)
                out["z_" + s] = z
                out["logJ_" + s] = log_jacobian_m1src_q_z_to_m1det_q_dL(
                    z, dLc, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            if not dark:
                st = prepare_redshift_prior_state(pe_model, cosmo, survey, None,
                                                  materialize_state=materialize,
                                                  catalog_sky_weighting=sw, kde_window=kde_window)
                out["log_pvol"] = st.log_pvol
            return out

        @tdt()
        def comp_b(coord, gw_pe, gw_sel, z_pe, z_sel, distance_table=None):
            pp = decode(coord)[2]
            out = {}
            for s, gw, z in (("pe", gw_pe, z_pe), ("sel", gw_sel, z_sel)):
                m1src = gw.m1det / (1.0 + z)
                if gw.spin is None:
                    out["lpop_" + s] = log_p_pop(m1src, gw.q, z, gw.chieff, pp)
                else:
                    out["lpop_" + s] = log_p_pop(m1src, gw.q, z, gw.chieff, pp, spin=gw.spin)
            return out

        @tdt()
        def comp_c(coord, m1src_pe, m1src_sel, distance_table=None):
            pp = decode(coord)[2]
            return pop_norm_terms(model.mixture, model.mixture_theta(pp), m1src_pe, m1src_sel,
                                  get_pairing_panel_quadrature, jnp)

        @tdt()
        def comp_w(coord, gw_pe, gw_sel, em_pe, em_sel, st_u, st_s, rt_pe, rt_sel,
                   distance_table=None):
            cosmo, survey, pp, _sky, _marks = decode(coord)
            dLg = dL_of_z(cosmo_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dLg[0], dLg[-1]

            def prior_pe(z, pix, catalogs):
                return eval_redshift_prior_with_state(pe_model, st_u, z, pix, cosmo, survey,
                                                      catalogs[0], catalog_sky_weighting=sw,
                                                      empty_routing=rt_pe)

            def prior_sel(z, pix, catalogs):
                return eval_redshift_prior_with_state(sel_model, st_s, z, pix, cosmo, survey,
                                                      catalogs[0], catalog_sky_weighting=sw,
                                                      empty_routing=rt_sel)

            def weight(gw, prior, cats):
                supported = (gw.dL >= lo) & (gw.dL <= hi)
                dLc = jnp.clip(gw.dL, lo, hi)
                ldw = log_sample_weight(gw.m1det, gw.q, dLc, gw.chieff, gw.pixels, gw.prior_wt,
                                        cosmo, survey, pp, cats, log_p_pop, prior, spin=gw.spin,
                                        dL_grid=dLg)
                return jnp.where(supported & jnp.isfinite(ldw), ldw, -jnp.inf)
            return {"ldw_pe": weight(gw_pe, prior_pe, (em_pe,)),
                    "ldw_sel": weight(gw_sel, prior_sel, (em_sel,))}

        @tdt()
        def comp_d(ldw_pe, valid_pe, pwt_pe, distance_table=None):
            # Transcription of likelihood/core.py:1433-1492 (block-vectorised PE reduction).
            pe_block = n_ev if peb is None else min(peb, n_ev)

            def _pe_chunk_ldw(s, n):
                sl = lambda arr: lax.dynamic_slice_in_dim(arr, s, n)  # noqa: E731
                valid = sl(valid_pe) & (sl(pwt_pe) > 0.0)
                ldw = sl(ldw_pe)
                return jnp.where(valid & jnp.isfinite(ldw), ldw, -jnp.inf)

            def _reduce_events(s, m):
                ldw = _pe_chunk_ldw(s, m * ns).reshape(m, ns)
                return jax.vmap(lambda row: log_evidence_and_mc_variance(row, ns))(ldw)

            def _chunk_scan(_, s):
                return None, _reduce_events(s, pe_block)

            block_samps = pe_block * ns
            n_full, rem, overlap_tail = _pe_chunk_plan(n_ev, pe_block)
            parts = []
            if overlap_tail:
                starts = jnp.asarray([i * block_samps for i in range(n_full)] + [(n_ev - pe_block) * ns])
                _, stacked = lax.scan(_chunk_scan, None, starts)
                parts.append(jax.tree_util.tree_map(
                    lambda x: x[:n_full].reshape((n_full * pe_block,) + x.shape[2:]), stacked))
                parts.append(jax.tree_util.tree_map(lambda x: x[n_full, pe_block - rem:], stacked))
            else:
                if n_full == 1:
                    parts.append(_reduce_events(0, pe_block))
                elif n_full > 1:
                    _, stacked = lax.scan(_chunk_scan, None, jnp.arange(n_full) * block_samps)
                    parts.append(jax.tree_util.tree_map(
                        lambda x: x.reshape((n_full * pe_block,) + x.shape[2:]), stacked))
                if rem > 0:
                    parts.append(_reduce_events(n_full * block_samps, rem))
            return {"event_lls": jnp.concatenate([q[0] for q in parts]),
                    "event_vars": jnp.concatenate([q[1] for q in parts])}

        @tdt()
        def comp_e(ldw_sel, valid_sel, pwt_sel, pe_var_sum, distance_table=None):
            ldw, valid, pwt = pad_selection(jnp, ldw_sel, valid_sel, pwt_sel, sbs)
            n_sel = int(ldw.shape[0])

            def provider(start, size):
                sl = lambda arr: lax.dynamic_slice_in_dim(arr, start, size)  # noqa: E731
                x = sl(ldw)
                ok = sl(valid) & (sl(pwt) > 0.0)
                return jnp.where(ok & jnp.isfinite(x), x, -jnp.inf)
            log_mu, n_eff, log_s2 = selection_reduce_from_ldw_provider(provider, n_sel, n_draw, sbs)
            sel_ll = selection_log_correction(log_mu, n_eff, n_ev, soft_guard=soft,
                                              max_likelihood_variance=maxvar,
                                              pe_variance_sum=pe_var_sum)
            return {"log_mu": log_mu, "n_eff": n_eff, "log_sigma2": log_s2,
                    "selection_log_correction": sel_ll}

        fns = {"a_cosmology": comp_a, "b_population": comp_b, "c_pop_norm": comp_c,
               "w_weights": comp_w, "d_pe_reduce": comp_d, "e_sel_reduce": comp_e}

        if dark:
            from darksirens.redshift.catalog import catalog_kernel_state
            from darksirens.redshift.completion import completion_curves, log_galaxy_measure_grid

            @tdt()
            def comp_f(coord, em, distance_table=None):
                cosmo, survey, _p, _sky, _marks = decode(coord)
                log_g = log_galaxy_measure_grid(cosmo, survey)
                return catalog_kernel_state(cosmo, survey, em, log_g_grid=log_g,
                                            z_depth=survey.z_depth, pinned=em.pinned_kernels,
                                            kde_window=kde_window)

            @tdt()
            def comp_h(coord, em, distance_table=None):
                cosmo, survey, _p, _sky, _marks = decode(coord)
                return completion_curves(cosmo, survey, em)

            @tdt()
            def comp_state(coord, em, distance_table=None):
                cosmo, survey, _p, _sky, _marks = decode(coord)
                return prepare_redshift_prior_state(
                    pe_model, cosmo, survey, em, mark_model="none", mark_params=None,
                    mark_names=(), materialize_state=materialize, catalog_sky_weighting=sw,
                    kde_window=kde_window)

            def make_g(route):
                @tdt()
                def comp_g(coord, z_pe, pix_pe, z_sel, pix_sel, st_u, st_s, em_pe, em_sel, rt_pe,
                           rt_sel, distance_table=None):
                    cosmo, survey, _p, _sky, _marks = decode(coord)
                    return {
                        "log_prior_pe": eval_redshift_prior_with_state(
                            pe_model, st_u, z_pe, pix_pe, cosmo, survey, em_pe,
                            catalog_sky_weighting=sw, empty_routing=rt_pe if route else None),
                        "log_prior_sel": eval_redshift_prior_with_state(
                            sel_model, st_s, z_sel, pix_sel, cosmo, survey, em_sel,
                            catalog_sky_weighting=sw, empty_routing=rt_sel if route else None),
                    }
                return comp_g
            fns.update(f_kernel_state=comp_f, h_completion=comp_h, fh_prior_state=comp_state,
                       g_prior_eval=make_g(True))
            if self.routing_active:
                fns["g_prior_eval_unrouted"] = make_g(False)
        else:
            @tdt()
            def comp_g(coord, z_pe, pix_pe, z_sel, pix_sel, st_u, st_s, em_pe, em_sel,
                       distance_table=None):
                cosmo, survey, _p, _sky, _marks = decode(coord)
                return {
                    "log_prior_pe": eval_redshift_prior_with_state(
                        pe_model, st_u, z_pe, pix_pe, cosmo, survey, em_pe,
                        catalog_sky_weighting=sw),
                    "log_prior_sel": eval_redshift_prior_with_state(
                        sel_model, st_s, z_sel, pix_sel, cosmo, survey, em_sel,
                        catalog_sky_weighting=sw),
                }
            fns["g_prior_eval"] = comp_g
        self.fns = fns
        self.n_state_builds = (1 if self.share0 else 2) if dark else 0
        self.state_builds_note = (("legacy builds ONE prior state per call and shares it between "
                                   "PE and selection (union path, likelihood/core.py:1058-1087)")
                                  if (dark and self.share0) else
                                  ("legacy builds separate PE and selection states" if dark else None))
        self._SpectralPriorState = None
        if not dark:
            from darksirens.redshift.prior import SpectralPriorState
            self._SpectralPriorState = SpectralPriorState

    def sel_to_file(self, a):
        """Internal (pixel-sorted, maybe padded) selection array -> FILE order."""
        x = np.asarray(a)[: self.n_inj]
        f = np.empty_like(x)
        f[self.sel_order] = x
        return f

    def build_calls(self, coords, fc):
        jnp = self.jnp
        pe, sel, em_pe, em_sel = self.gw_pe, self.gw_sel, self.em_pe, self.em_sel
        rt_pe, rt_sel = self.rt_pe, self.rt_sel
        n = coords.shape[0]
        th = lambda k: jnp.asarray(coords[k])  # noqa: E731
        A, S, W, Dd, PV = {}, {}, {}, {}, {}
        for k in range(n):
            A[k] = fc["a_cosmology"](th(k), pe.dL, sel.dL)
            if self.dark:
                st = fc["fh_prior_state"](th(k), em_pe)
                S[k] = (st, st)  # one shared state (share_prior_state_by_catalog)
                if not self.share0:
                    S[k] = (st, fc["fh_prior_state"](th(k), em_sel))
            else:
                st = self._SpectralPriorState(log_pvol=A[k]["log_pvol"])
                S[k] = (st, st)
            W[k] = fc["w_weights"](th(k), pe, sel, em_pe, em_sel, S[k][0], S[k][1], rt_pe, rt_sel)
            Dd[k] = fc["d_pe_reduce"](W[k]["ldw_pe"], pe.valid, pe.prior_wt)
            PV[k] = jnp.sum(Dd[k]["event_vars"])
        M1 = {k: (pe.m1det / (1.0 + A[k]["z_pe"]), sel.m1det / (1.0 + A[k]["z_sel"])) for k in range(n)}
        calls = {
            "a_cosmology": lambda k: fc["a_cosmology"](th(k), pe.dL, sel.dL),
            "b_population": lambda k: fc["b_population"](th(k), pe, sel, A[k]["z_pe"], A[k]["z_sel"]),
            "w_weights": lambda k: fc["w_weights"](th(k), pe, sel, em_pe, em_sel, S[k][0], S[k][1],
                                                   rt_pe, rt_sel),
            "d_pe_reduce": lambda k: fc["d_pe_reduce"](W[k]["ldw_pe"], pe.valid, pe.prior_wt),
            "e_sel_reduce": lambda k: fc["e_sel_reduce"](W[k]["ldw_sel"], sel.valid, sel.prior_wt, PV[k]),
        }
        args0 = {
            "a_cosmology": ((th(0), pe.dL, sel.dL), {}),
            "b_population": ((th(0), pe, sel, A[0]["z_pe"], A[0]["z_sel"]), {}),
            "c_pop_norm": ((th(0), M1[0][0], M1[0][1]), {}),
            "w_weights": ((th(0), pe, sel, em_pe, em_sel, S[0][0], S[0][1], rt_pe, rt_sel), {}),
            "d_pe_reduce": ((W[0]["ldw_pe"], pe.valid, pe.prior_wt), {}),
            "e_sel_reduce": ((W[0]["ldw_sel"], sel.valid, sel.prior_wt, PV[0]), {}),
        }
        if self.norm_available:
            calls["c_pop_norm"] = lambda k: fc["c_pop_norm"](th(k), M1[k][0], M1[k][1])
        if self.dark:
            gargs = lambda k: (th(k), A[k]["z_pe"], pe.pixels, A[k]["z_sel"], sel.pixels,  # noqa: E731
                               S[k][0], S[k][1], em_pe, em_sel, rt_pe, rt_sel)
            calls.update({
                "f_kernel_state": lambda k: fc["f_kernel_state"](th(k), em_pe),
                "h_completion": lambda k: fc["h_completion"](th(k), em_pe),
                "fh_prior_state": lambda k: fc["fh_prior_state"](th(k), em_pe),
                "g_prior_eval": lambda k: fc["g_prior_eval"](*gargs(k)),
            })
            args0.update({
                "f_kernel_state": ((th(0), em_pe), {}),
                "h_completion": ((th(0), em_pe), {}),
                "fh_prior_state": ((th(0), em_pe), {}),
                "g_prior_eval": (gargs(0), {}),
            })
            if "g_prior_eval_unrouted" in fc:
                calls["g_prior_eval_unrouted"] = lambda k: fc["g_prior_eval_unrouted"](*gargs(k))
                args0["g_prior_eval_unrouted"] = (gargs(0), {})
        else:
            gargs = lambda k: (th(k), A[k]["z_pe"], pe.pixels, A[k]["z_sel"], sel.pixels,  # noqa: E731
                               S[k][0], S[k][1], em_pe, em_sel)
            calls["g_prior_eval"] = lambda k: fc["g_prior_eval"](*gargs(k))
            args0["g_prior_eval"] = (gargs(0), {})
        self._keep = (A, S, W, Dd, PV, M1)
        return calls, args0

    def data_arrays(self):
        lk = self.lk
        d = {"gw_pe.m1det": self.gw_pe.m1det, "gw_pe.dL": self.gw_pe.dL,
             "gw_pe.prior_wt": self.gw_pe.prior_wt, "gw_sel.m1det": self.gw_sel.m1det,
             "gw_sel.dL": self.gw_sel.dL, "gw_sel.prior_wt": self.gw_sel.prior_wt,
             "distance_table": lk.distance_table}
        if self.dark:
            d.update({"em_pe.zgals": self.em_pe.zgals, "em_pe.dzgals": self.em_pe.dzgals,
                      "em_pe.wgals": self.em_pe.wgals, "em_pe.dN_obs_kde": self.em_pe.dN_obs_kde})
        return d

    def jit_kwargs(self):
        return {"distance_table": self.distance_table(),
                "_ambient_extras": tuple(res() for res, _ in self.ambient)}

    def extract(self, name, out):
        return extract_outputs(name, out, self.sel_to_file)

    def layout_call(self):
        """(k): the build-time injection sort, re-run on file-order inputs."""
        jax, jnp = self.jax, self.jnp
        from darksirens.likelihood.factory import _injection_pixel_order, _permute_rows

        n = self.n_inj
        fields = ("m1det", "m2det", "dL", "chieff", "prior_wt", "q", "nx", "ny", "nz", "spin", "pixels")
        internal = {f: getattr(self.gw_sel, f) for f in fields}
        host_file, dev_file = {}, {}
        for f, v in internal.items():
            if v is None:
                host_file[f] = None
                dev_file[f] = None
                continue
            x = np.asarray(v)[:n]
            y = np.empty_like(x)
            y[self.sel_order] = x
            host_file[f] = y
            dev_file[f] = jnp.asarray(y)
        rows_file = host_file["pixels"]
        order = _injection_pixel_order(rows_file)
        same = order is not None and np.array_equal(np.asarray(order), self.sel_order)
        src = "the file-order compact catalog rows (factory: catalogs.sample_to_unique_sel)"
        pix_in = rows_file
        if not same:
            raw = np.asarray(self.adapter.data["pixels_sel"])
            order2 = _injection_pixel_order(raw)
            if order2 is not None and np.array_equal(np.asarray(order2), self.sel_order):
                pix_in, src, same = raw, "data['pixels_sel'] (the adapter's verified source)", True
        jax.block_until_ready([v for v in dev_file.values() if v is not None])

        def call(_k):
            o = _injection_pixel_order(pix_in)
            return tuple(_permute_rows(dev_file[f], o) for f in fields)

        permuted = call(0)
        check = all(v is None or np.array_equal(np.asarray(v)[:n], np.asarray(internal[f])[:n])
                    for f, v in zip(fields, permuted))
        info = {
            "timed": ("stable numpy argsort of the per-injection pixel ids (host) + device gather of "
                      f"the {sum(v is not None for v in dev_file.values())} per-injection arrays "
                      "(_permute_rows, which also applies legacy's optimization barrier), each call "
                      "block_until_ready"),
            "sort_key_source": src,
            "order_reproduces_adapter_order": bool(same),
            "permuted_equals_kernel_operands": bool(check),
            "n_injections": n,
            "one_time_build_cost": True,
        }
        return call, info


# ---------------------------------------------------------------------------
# output extraction (implementation-neutral names, FILE order)
# ---------------------------------------------------------------------------
KERNEL_STATE_FIELDS = ("log_g_grid", "log_kw", "sig_eff", "log_sig_eff", "log_depth_mass", "row_empty",
                       "log_kw_eff", "log_kw_eff_rowmax", "inv_sig_eff")
CURVE_FIELDS = ("dN_miss", "N_miss", "C_eff", "f")
STATE_FIELDS = ("log_Nobs", "log_Z", "dN_miss")


def _is_sel_key(key):
    return key.endswith("_sel") or "_sel_" in key


def extract_outputs(name, out, sel_to_file):
    if name == "f_kernel_state":
        d = {k: getattr(out, k) for k in KERNEL_STATE_FIELDS}
    elif name == "h_completion":
        d = {k: getattr(out, k) for k in CURVE_FIELDS}
    elif name == "fh_prior_state":
        d = {k: getattr(out, k) for k in STATE_FIELDS}
    elif name == "i_whole":
        d = {"total_logL": out}
    elif isinstance(out, dict):
        d = dict(out)
    else:
        raise TypeError(f"{name}: unexpected output type {type(out).__name__}")
    res = {}
    for k, v in d.items():
        a = _to_host(v)
        if _is_sel_key(k) and a.ndim >= 1:
            a = sel_to_file(a)
        res[k] = a
    return res


# ---------------------------------------------------------------------------
# timing (the main harness's loop, bench_fixed_theta.py timed section)
# ---------------------------------------------------------------------------
def time_component(call, n_coords, n_calls, warmup, counter, jax, first_record=None, keep=None):
    """First call on coords[0] (unless the component already ran there during the
    input precompute: then that invocation IS the first call), ``warmup`` warm-ups on
    coords[:warmup], ``n_calls`` timed calls cycling the coordinates."""
    out = {}
    if first_record is None:
        snap = counter.snapshot()
        t0 = time.perf_counter()
        v = call(0)
        jax.block_until_ready(v)
        out["t_first_call_s"] = time.perf_counter() - t0
        out["first_call_compile"] = counter.delta(snap)
        out["first_call_context"] = "timing (coords[0])"
        if keep is not None:
            keep(0, v)
        del v
    else:
        out["t_first_call_s"] = first_record["t_first_call_s"]
        out["first_call_compile"] = first_record["compile"]
        out["first_call_context"] = f"{first_record['context']} (coords[0])"
    snap = counter.snapshot()
    wt = []
    for i in range(warmup):
        k = i % n_coords
        t0 = time.perf_counter()
        v = call(k)
        jax.block_until_ready(v)
        wt.append(time.perf_counter() - t0)
        if keep is not None:
            keep(k, v)
        del v
    out["warmup_s"] = wt
    out["warmup_compile"] = counter.delta(snap)
    snap = counter.snapshot()
    times, idx = [], []
    t_start = time.time()
    for i in range(n_calls):
        k = i % n_coords
        t0 = time.perf_counter()
        v = call(k)
        jax.block_until_ready(v)
        times.append(time.perf_counter() - t0)
        idx.append(k)
        if keep is not None:
            keep(k, v)
        del v
    out["loop_unix"] = [t_start, time.time()]
    out["timed_loop_compile"] = counter.delta(snap)
    w = bc.stats(times)
    w["calls_s"] = times
    w["coord_index"] = idx
    out["warm"] = w
    return out


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--impl", required=True, choices=("legacy", "core"))
    ap.add_argument("--pe", required=True)
    ap.add_argument("--sel", required=True)
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--plan", required=True, choices=sorted(plans.PLANS))
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", choices=("gpu", "cpu", "auto"), default="auto")
    ap.add_argument("--n-calls", type=int, default=20)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--sel-batch", type=_block_arg, default="none")
    ap.add_argument("--pe-block", type=_block_arg, default="none")
    ap.add_argument("--jit", choices=("whole", "asis"), default="whole",
                    help="kernel of i_whole for core (legacy: always its factory closure)")
    ap.add_argument("--seed", type=int, default=None, help="must equal the coords file seed")
    ap.add_argument("--label", default=None)
    ap.add_argument("--main-record", default=None,
                    help="bench_fixed_theta record at the same plan/coords/inputs/blocks: i_whole "
                         "must reproduce its per-coordinate totals bit for bit")
    ap.add_argument("--components", default=None,
                    help="comma-separated subset of component names (default: all available)")
    ap.add_argument("--full-array-coords", default="0,1",
                    help="coordinates whose arrays above --big-array-elements are stored in the npz")
    ap.add_argument("--big-array-elements", type=int, default=1_000_000)
    ap.add_argument("--trace", default=None,
                    help="DIR: after timing, run each component's warm calls again inside "
                         "jax.profiler.trace(DIR/<component>) and parse them (trace_tools.py)")
    ap.add_argument("--trace-top", type=int, default=25)
    ap.add_argument("--trace-calls", type=int, default=None,
                    help="calls per traced component (default: --n-calls)")
    ap.add_argument("--trace-drop-xplane", action="store_true",
                    help="delete the (large) *.xplane.pb after a successful parse; its size and "
                         "sha256 are recorded, the trace.json.gz and perfetto_trace.json.gz stay")
    ap.add_argument("--no-aot", action="store_true", help="skip the per-component AOT evidence")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--cache-mode", choices=("cold", "warm", "env"), default="env")
    ap.add_argument("--survey-fixed-override", default=None)
    ap.add_argument("--allow-out-of-prior-fixed-survey", action="store_true")
    return ap.parse_args(argv)


def _dir_inventory(path):
    n = b = 0
    if path and os.path.isdir(path):
        for root, _dirs, files in os.walk(path):
            for fn in files:
                n += 1
                try:
                    b += os.path.getsize(os.path.join(root, fn))
                except OSError:
                    pass
    return n, b


def _check_main_record(main_path, record, whole_hex):
    """i_whole vs a bench_fixed_theta record: same experiment, bit-identical totals."""
    m = bc.read_json(main_path)
    res = {"main_record": os.path.abspath(main_path), "main_label": m.get("label"),
           "main_schema": m.get("schema"), "checks": {}, "mismatches": []}
    chk = res["checks"]
    chk["implementation"] = m.get("implementation") == record["implementation"]
    chk["plan"] = (m.get("plan") or {}).get("name") == record["plan"]["name"]
    chk["coords"] = (m.get("coords") or {}).get("values_hex") == record["coords"]["values_hex"]
    chk["inputs"] = all(((m.get("inputs") or {}).get(k) or {}).get("sha256")
                        == ((record.get("inputs") or {}).get(k) or {}).get("sha256")
                        for k in ("pe", "sel", "catalog"))
    mc, rc = m.get("config") or {}, record.get("config") or {}
    chk["blocks"] = all((mc.get(k) or {}).get("resolved") == (rc.get(k) or {}).get("resolved")
                        for k in ("sel_batch_size", "pe_event_block"))
    chk["kernel"] = mc.get("kernel") == rc.get("kernel")
    main_status = m.get("status")
    chk["main_status_ok"] = main_status == "ok"
    per = (m.get("values") or {}).get("per_coord") or []
    n_bitwise = 0
    for i, hx in enumerate(whole_hex):
        if i >= len(per):
            res["mismatches"].append(f"coord {i}: missing in the main record")
            continue
        mh = per[i]["total_logL"]["hex"]
        timed = set(per[i].get("timed_values_hex") or [mh])
        if hx == mh and timed == {mh}:
            n_bitwise += 1
        else:
            res["mismatches"].append(f"coord {i}: components {hx} vs main {mh} (timed {sorted(timed)})")
    res["n_coords"] = len(whole_hex)
    res["n_bitwise"] = n_bitwise
    res["experiment_matches"] = all(chk.values())
    res["bitwise"] = bool(res["experiment_matches"] and n_bitwise == len(whole_hex) and len(per) == len(whole_hex))
    return res, m


def _cross_check_main(main, parity_arrays, n):
    """Informational: d/e component outputs vs the main record's diagnostics."""
    if main is None:
        return None
    per = (main.get("values") or {}).get("per_coord") or []
    out = {}
    pairs = (("d_pe_reduce", "event_lls", "event_log_evidence"),
             ("d_pe_reduce", "event_vars", "event_mc_variance"),
             ("e_sel_reduce", "log_mu", "log_mu"), ("e_sel_reduce", "n_eff", "n_eff"),
             ("e_sel_reduce", "selection_log_correction", "selection_log_correction"))
    for comp, key, field in pairs:
        worst, bitwise, ncmp = 0.0, True, 0
        for k in range(min(n, len(per))):
            a = parity_arrays.get((comp, key, k))
            if a is None:
                continue
            ent = per[k][field]
            b = (bc.from_hex_list(ent["hex"]) if isinstance(ent["hex"], list)
                 else np.asarray([float.fromhex(ent["hex"])]))
            a = np.asarray(a, dtype=np.float64).ravel()
            if a.shape != b.shape:
                bitwise = False
                worst = float("inf")
                continue
            ncmp += 1
            bitwise &= bool(np.array_equal(a.view(np.int64), b.view(np.int64)))
            fin = np.isfinite(a) & np.isfinite(b) & (b != 0)
            if fin.any():
                worst = max(worst, float(np.max(np.abs(a[fin] - b[fin]) / np.abs(b[fin]))))
            if np.any(np.isfinite(a) != np.isfinite(b)):
                worst = float("inf")
        out[f"{comp}.{key}"] = {"vs_main_field": field, "n_coords": ncmp, "bitwise": bitwise,
                                "max_rel": bc.fval(worst)}
    out["note"] = ("informational: the main record's diagnostics come from a different jitted "
                   "graph (core: return_diagnostics jit; legacy: the harness re-assembly), so "
                   "last-bit differences from fusion are expected")
    return out


def main(argv=None):
    a = parse_args(argv)
    command_line = [sys.executable] + list(sys.argv if argv is None else ["bench_components.py"] + argv)
    started = bc.utc_now()
    if a.device == "cpu":
        cur = os.environ.get("JAX_PLATFORMS")
        if cur and cur != "cpu":
            print(f"--device cpu but JAX_PLATFORMS={cur}", file=sys.stderr)
            return 2
        os.environ["JAX_PLATFORMS"] = "cpu"
    override = json.loads(a.survey_fixed_override) if a.survey_fixed_override else None
    try:
        plan = plans.resolve_plan(a.plan, survey_fixed_override=override)
    except ValueError as exc:
        print(f"plan: {exc}", file=sys.stderr)
        return 2
    dark = plans.is_dark(plan)
    fixture_preflight = None
    if dark:
        import dark_fixture

        if not a.catalog or not os.path.isfile(a.catalog):
            print(f"plan {a.plan} is a dark-siren plan and needs --catalog", file=sys.stderr)
            return 2
        try:
            fixture_preflight = dark_fixture.preflight(a.catalog, a.pe, a.sel, plan)
        except dark_fixture.FixturePreflightError as exc:
            print(f"FIXTURE PREFLIGHT REFUSED: {exc}", file=sys.stderr)
            return 2
        if override and not a.allow_out_of_prior_fixed_survey:
            for lab, val in override.items():
                x = float(val)
                if lab == "log10n0":
                    bad = any(not lo <= x <= hi for lo, hi, _s in plans.LOG10N0_PRIOR.values())
                else:
                    lo, hi = plans.SURVEY_BOUNDS[lab]
                    bad = not lo <= x <= hi
                if bad:
                    print(f"--survey-fixed-override {lab}={x} outside its prior; pass "
                          "--allow-out-of-prior-fixed-survey", file=sys.stderr)
                    return 2
    elif a.catalog or override:
        print(f"plan {a.plan} is catalog-free: --catalog / --survey-fixed-override refused",
              file=sys.stderr)
        return 2
    coords_doc = bc.read_json(a.coords)
    if coords_doc.get("plan") != a.plan or list(coords_doc["names"]) != plan["sampled"]:
        print("coords file does not match the plan", file=sys.stderr)
        return 2
    seed = int(coords_doc["seed"]) if a.seed is None else int(a.seed)
    if seed != int(coords_doc["seed"]):
        print(f"--seed {a.seed} != coords seed {coords_doc['seed']}", file=sys.stderr)
        return 2
    coords = np.asarray([[float.fromhex(h) for h in row] for row in coords_doc["values_hex"]],
                        dtype=np.float64)
    n_coords = coords.shape[0]
    selected = None
    if a.components:
        selected = [c.strip() for c in a.components.split(",") if c.strip()]
        unknown = [c for c in selected if c not in COMPONENT_BY_NAME]
        if unknown:
            print(f"unknown components {unknown}; known {ORDER}", file=sys.stderr)
            return 2
    full_coords = sorted({int(x) for x in a.full_array_coords.split(",") if x.strip() != ""})

    cache_info = {"mode": a.cache_mode, "requested_dir": a.cache_dir,
                  "env_dir_before_override": os.environ.get("JAX_COMPILATION_CACHE_DIR")}
    if a.cache_mode in ("cold", "warm") and not a.cache_dir:
        print(f"--cache-mode {a.cache_mode} needs --cache-dir", file=sys.stderr)
        return 2
    if a.cache_dir:
        cdir = os.path.abspath(a.cache_dir)
        n0, b0 = _dir_inventory(cdir)
        if a.cache_mode == "cold" and n0:
            print(f"--cache-mode cold but {cdir} already holds {n0} files", file=sys.stderr)
            return 2
        if a.cache_mode == "warm" and not n0:
            print(f"--cache-mode warm but {cdir} is empty or missing", file=sys.stderr)
            return 2
        os.makedirs(cdir, exist_ok=True)
        os.environ["JAX_COMPILATION_CACHE_DIR"] = cdir
        cache_info.update(dir=cdir, files_before=n0, bytes_before=b0)
    else:
        cdir = os.environ.get("JAX_COMPILATION_CACHE_DIR")
        n0, b0 = _dir_inventory(cdir)
        cache_info.update(dir=cdir, files_before=n0, bytes_before=b0)

    # ---- JAX + hooks before the implementation ------------------------------
    t0 = time.perf_counter()
    import jax

    counter = bc.CompileCounter().install()
    t_import_jax = time.perf_counter() - t0
    t0 = time.perf_counter()
    if a.impl == "legacy":
        import impl_legacy as impl
    else:
        import impl_core as impl
    pkg = impl.import_package()
    t_import_pkg = time.perf_counter() - t0
    jax.devices()
    device = bc.device_fingerprint(a.device)
    if a.device in ("gpu", "cpu") and device["backend"] != a.device:
        print(f"--device {a.device} but JAX backend is {device['backend']}", file=sys.stderr)
        return 2
    if not device["x64"]:
        print("jax_enable_x64 is off after the implementation configured JAX", file=sys.stderr)
        return 2
    import bench_fixed_theta as bft

    label = a.label or f"components_{a.impl}_{a.plan}"
    record = {
        "schema": RECORD_SCHEMA, "status": "running", "label": label, "implementation": a.impl,
        "command_line": command_line, "cwd": os.getcwd(), "started_utc": started,
        "harness": {"dir": HERE, "git": bc.package_fingerprint(type("M", (), {
            "__name__": "benchmarks.a100", "__file__": os.path.join(HERE, "plans.py")}))},
        "package": bc.package_fingerprint(pkg), "env": bc.env_fingerprint(), "device": device,
        "inputs": {"pe": bc.gwcat_file_info(a.pe), "sel": bc.gwcat_file_info(a.sel)},
        "plan": plan, "gaps": [],
    }
    record["harness"]["git"].pop("known_digest_match", None)
    if dark:
        import dark_fixture

        record["inputs"]["catalog"] = dict(dark_fixture.catalog_summary(a.catalog),
                                           path=os.path.abspath(a.catalog),
                                           bytes=os.path.getsize(a.catalog),
                                           sha256=bc.sha256_file(a.catalog))
        record["fixture_preflight"] = fixture_preflight
    out_dir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(out_dir, exist_ok=True)
    save_dir = os.path.abspath(a.out) + ".legacy_save"
    adapter_cls = impl.LegacyAdapter if a.impl == "legacy" else impl.CoreAdapter
    adapter_kw = {"catalog_path": os.path.abspath(a.catalog)} if dark else {}
    adapter = adapter_cls(plan, os.path.abspath(a.pe), os.path.abspath(a.sel),
                          sel_batch=a.sel_batch, pe_block=a.pe_block, jit_mode=a.jit,
                          seed=seed, save_dir=save_dir, counter=counter, **adapter_kw)
    mem = [bc.memory_checkpoint("after_import")]
    snap = counter.snapshot()
    try:
        adapter.build()
    except Exception as exc:
        import traceback

        record.update(status="build_error", build_error={
            "type": type(exc).__name__, "message": str(exc),
            "traceback_tail": traceback.format_exc()[-4000:]}, finished_utc=bc.utc_now())
        if a.impl == "legacy":
            adapter.remove_save_dir()
        bc.write_json(a.out, record)
        print(f"BUILD ERROR ({a.impl}): {type(exc).__name__}: {exc}", file=sys.stderr)
        return 4
    compile_build = counter.delta(snap)
    record["config"] = adapter.config()
    record["config"].update(seed=seed, n_calls=a.n_calls, warmup=a.warmup, device=a.device,
                            full_array_coords=full_coords, big_array_elements=a.big_array_elements)
    dims = adapter.dims()
    dims["n_coords"] = int(n_coords)
    record["dims"] = dims
    plan_errors = bft.check_plan_structure(adapter, plan)
    if plan_errors:
        record.update(status="plan_mismatch", plan_errors=plan_errors, finished_utc=bc.utc_now())
        bc.write_json(a.out, record)
        print("PLAN MISMATCH:\n  " + "\n  ".join(plan_errors), file=sys.stderr)
        return 3
    decode_errors = []
    for i in range(n_coords):
        dec = adapter.decode(coords[i])
        exp = bft.expected_full_vector(plan, coords_doc["names"], coords[i],
                                       pow10=getattr(adapter, "pow10", None))
        if [bc.fhex(x) for x in dec] != [bc.fhex(x) for x in exp]:
            decode_errors.append(f"coord {i}: decoded {dec} != expected {exp}")
    record["coords"] = {
        "source_file": os.path.abspath(a.coords), "source_sha256": bc.sha256_file(a.coords),
        "coords_digest": coords_doc.get("coords_digest"), "seed": seed,
        "names": list(coords_doc["names"]), "implementation_labels": adapter.labels,
        "values_hex": [[bc.fhex(x) for x in row] for row in coords], "values": coords.tolist(),
        "kinds": coords_doc.get("kinds"), "repeat_of": coords_doc.get("repeat_of"),
    }
    record["plan_assertions"] = {"structure": "ok", "decode": decode_errors or "ok"}
    mem.append(bc.memory_checkpoint("after_build"))

    # ---- component kernels -------------------------------------------------------
    comps = (LegacyComponents if a.impl == "legacy" else CoreComponents)(adapter, plan)
    context = {"phase": "input precompute"}
    fc = {name: FirstCall(fn, counter, jax, context) for name, fn in comps.fns.items()}
    t0 = time.perf_counter()
    calls, args0 = comps.build_calls(coords, fc)
    jax.block_until_ready(comps._keep)
    t_precompute = time.perf_counter() - t0
    context["phase"] = "timing"
    mem.append(bc.memory_checkpoint("after_input_precompute"))

    universe = "dark" if dark else "spectral"
    avail = {}
    for c in COMPONENTS:
        nm = c["name"]
        if c["universe"] not in ("both", universe):
            avail[nm] = (False, f"{universe} plan: component applies to {c['universe']} plans only")
        elif nm == "c_pop_norm" and not comps.norm_available:
            avail[nm] = (False, comps.norm_reason)
        elif nm == "g_prior_eval_unrouted" and "g_prior_eval_unrouted" not in calls:
            avail[nm] = (False, ("legacy only, when the factory built an empty-row routing plan"
                                 if a.impl == "legacy" else "core has no empty-row routing"))
        elif nm == "k_layout" and a.impl == "core":
            avail[nm] = (False, comps.layout_call()[1])
        else:
            avail[nm] = (True, None)
        if selected is not None and nm not in selected and avail[nm][0]:
            avail[nm] = (False, "not selected (--components)")

    # (j) transfer: host numpy copies of the kernel operands
    ops = adapter.operands_for_sync()
    leaves, treedef = jax.tree_util.tree_flatten(ops)
    host_leaves = [np.asarray(x) if isinstance(x, jax.Array) else x for x in leaves]
    host_tree = jax.tree_util.tree_unflatten(treedef, host_leaves)
    operand_bytes = int(sum(x.nbytes for x in host_leaves if isinstance(x, np.ndarray)))
    layout_info = None
    if avail["k_layout"][0]:
        layout_fn, layout_info = comps.layout_call()
        calls["k_layout"] = layout_fn

    def transfer_call(_k):
        return jax.device_put(host_tree)

    calls["j_transfer"] = transfer_call
    whole_vals = {i: [] for i in range(n_coords)}

    def keep_whole(k, v):
        whole_vals[k].append(bc.fhex(np.asarray(v)))

    calls["i_whole"] = lambda k: adapter.timed_call(coords[k])

    comp_rec = {}
    load_before = os.getloadavg() if hasattr(os, "getloadavg") else None
    for c in COMPONENTS:
        nm = c["name"]
        ok, why = avail[nm]
        entry = {"letter": c["letter"], "title": c["title"], "legacy_ref": c["legacy_ref"],
                 "core_ref": c["core_ref"], "same_quantity": c["same_quantity"],
                 "kind": c["kind"][a.impl], "note": c["note"], "available": bool(ok)}
        if not ok:
            entry["reason"] = why
            comp_rec[nm] = entry
            continue
        first = fc[nm].record if nm in fc else None
        t = time_component(calls[nm], n_coords, a.n_calls, a.warmup, counter, jax,
                           first_record=first, keep=keep_whole if nm == "i_whole" else None)
        entry["timing"] = t
        entry["memory_after"] = bc.memory_checkpoint(f"after_{nm}")
        if t["timed_loop_compile"]["requests"]:
            record["gaps"].append(f"{nm}: {t['timed_loop_compile']['requests']} compile requests in "
                                  "its timed loop (not a steady state)")
        comp_rec[nm] = entry
        print(f"  [{a.impl}] {nm:24s} first {t['t_first_call_s']:8.3f} s  warm median "
              f"{t['warm']['median_s'] * 1e3:10.3f} ms  (min {t['warm']['min_s'] * 1e3:.3f})  "
              f"loop compiles {t['timed_loop_compile']['requests']}", flush=True)
    load_after = os.getloadavg() if hasattr(os, "getloadavg") else None
    if "j_transfer" in comp_rec and comp_rec["j_transfer"].get("available"):
        med = comp_rec["j_transfer"]["timing"]["warm"]["median_s"]
        comp_rec["j_transfer"]["operand_bytes"] = operand_bytes
        comp_rec["j_transfer"]["GB_per_s_median"] = (operand_bytes / med / 1e9) if med > 0 else None
    if layout_info is not None:
        comp_rec["k_layout"]["layout"] = layout_info
    mem.append(bc.memory_checkpoint("after_timing"))

    # ---- untimed parity pass: outputs per coordinate, determinism --------------
    arrays_npz = {}
    parity_arrays = {}
    for nm in ORDER:
        e = comp_rec[nm]
        if not e.get("available") or nm in ("j_transfer", "k_layout"):
            continue
        outs = {}
        repeat_ok = True
        for k in range(n_coords):
            if nm == "i_whole":
                vals = whole_vals[k]
                if not vals:
                    v = calls[nm](k)
                    jax.block_until_ready(v)
                    vals.append(bc.fhex(np.asarray(v)))
                x = {"total_logL": np.asarray([float.fromhex(vals[0])])}
                repeat_ok &= len(set(vals)) == 1
            else:
                v1 = calls[nm](k)
                jax.block_until_ready(v1)
                x = comps.extract(nm, v1)
                del v1
                v2 = calls[nm](k)
                jax.block_until_ready(v2)
                x2 = comps.extract(nm, v2)
                del v2
                repeat_ok &= all(np.array_equal(np.ascontiguousarray(x[q]).view(np.uint8),
                                                np.ascontiguousarray(x2[q]).view(np.uint8)) for q in x)
            for key, arr in x.items():
                dg = _array_digest(arr)
                store = store_policy(nm, key, arr.size, k, a.big_array_elements, full_coords)
                dg["stored"] = bool(store)
                if store:
                    arrays_npz[f"{nm}__{key}__c{k}"] = arr
                parity_arrays[(nm, key, k)] = arr if arr.size <= 4_000_000 else None
                outs.setdefault(key, {"class": output_class(nm, key), "per_coord": []})
                outs[key]["per_coord"].append(dict(dg, coord=k))
        e["outputs"] = outs
        e["repeat_bitwise"] = bool(repeat_ok)
        if not repeat_ok:
            record["gaps"].append(f"{nm}: outputs of repeated calls at one coordinate differ")
    mem.append(bc.memory_checkpoint("after_parity_pass"))
    if comp_rec.get("fh_prior_state", {}).get("outputs") and comp_rec.get("h_completion", {}).get("outputs"):
        ha = [d["sha256"] for d in comp_rec["fh_prior_state"]["outputs"]["dN_miss"]["per_coord"]]
        hb = [d["sha256"] for d in comp_rec["h_completion"]["outputs"]["dN_miss"]["per_coord"]]
        record["fh_dN_miss_equals_h_dN_miss"] = ha == hb
        if ha != hb:
            record["gaps"].append("fh_prior_state dN_miss differs from h_completion dN_miss "
                                  "(digest-only output; not compared across implementations)")

    whole_hex = [whole_vals[k][0] for k in range(n_coords)] if comp_rec["i_whole"].get("available") else []
    main = None
    if a.main_record and whole_hex:
        res, main = _check_main_record(a.main_record, record, whole_hex)
        record["whole_vs_main_record"] = res
        if not res["bitwise"]:
            record["gaps"].append("i_whole is NOT bit-identical to --main-record: "
                                  + "; ".join(res["mismatches"][:4] + [k for k, v in res["checks"].items() if not v]))
    elif whole_hex:
        record["whole_vs_main_record"] = None
        record["gaps"].append("no --main-record: i_whole was not checked against the main harness")
    record["component_vs_main_diagnostics"] = _cross_check_main(main, parity_arrays, n_coords)
    rep = coords_doc.get("repeat_of") or {}
    record["repeat_consistency"] = {
        "pairs": [(int(k), int(v)) for k, v in rep.items()],
        "bitwise": all(
            all(comp_rec[nm]["outputs"][q]["per_coord"][int(j)]["sha256"]
                == comp_rec[nm]["outputs"][q]["per_coord"][int(i)]["sha256"]
                for q in comp_rec[nm]["outputs"])
            for nm in ORDER if comp_rec[nm].get("outputs") for j, i in rep.items()),
    }

    # ---- optional trace pass -------------------------------------------------------
    if a.trace:
        import trace_tools

        record["trace"] = trace_tools.trace_components(
            a.trace, [nm for nm in ORDER if comp_rec[nm].get("available")], calls, comps,
            comp_rec, whole_vals, n_coords, a.trace_calls or a.n_calls, jax, top_n=a.trace_top,
            title_prefix=f"{a.impl} {a.plan}", drop_xplane=a.trace_drop_xplane)
        if not record["trace"]["numerics_unchanged"]:
            record["gaps"].append("traced outputs differ from the untraced outputs")

    # ---- evidence: jaxpr constants, AOT trace/lower/compile ---------------------------
    kw = comps.jit_kwargs()
    data_arrays = comps.data_arrays()
    for nm in ORDER:
        e = comp_rec[nm]
        if not e.get("available") or nm not in comps.fns:
            continue
        try:
            e["jaxpr"] = bc.jaxpr_const_report(comps.fns[nm].jitted, args0[nm][0], kw, data_arrays)
            if e["jaxpr"]["embeds_data_literal"]:
                record["gaps"].append(f"{nm}: a data array is embedded as a jaxpr constant")
        except Exception as exc:  # evidence must not kill the record
            e["jaxpr"] = {"error": f"{type(exc).__name__}: {exc}"}
    if not a.no_aot:
        # The first calls compiled into the (cold) persistent cache; executables that took
        # longer than jax_persistent_cache_min_compile_time_secs were written there, and an
        # AOT compile after jax.clear_caches() would be served from it. Disable the cache
        # for this pass (the timed section is over) so every AOT compile is a real one.
        try:
            from jax._src import compilation_cache as _cc

            jax.config.update("jax_enable_compilation_cache", False)
            _cc.reset_cache()
            record["aot_policy"] = ("persistent compilation cache disabled for the AOT pass "
                                    "(jax_enable_compilation_cache=False + "
                                    "jax._src.compilation_cache.reset_cache()) after the timed "
                                    "section: each aot.t_compile_s is a real XLA compile")
        except Exception as exc:  # pragma: no cover
            record["aot_policy"] = (f"could not disable the persistent cache ({type(exc).__name__}: "
                                    f"{exc}); an aot entry with compile_counter_delta.compiles == 0 "
                                    "was served from it")
        for nm in ORDER:
            e = comp_rec[nm]
            if not e.get("available") or nm not in comps.fns:
                continue
            try:
                e["aot"] = bc.aot_report(comps.fns[nm].jitted, args0[nm][0], kw, counter)
            except Exception as exc:
                e["aot"] = {"error": f"{type(exc).__name__}: {exc}"}
        if comp_rec["i_whole"].get("available"):
            try:
                ev = adapter.jit_evidence(coords[0])
                comp_rec["i_whole"]["jaxpr"] = ev.get("jaxpr")
                comp_rec["i_whole"]["aot"] = ev.get("aot")
                comp_rec["i_whole"]["jit_evidence_kernel"] = ev.get("kernel")
            except Exception as exc:
                comp_rec["i_whole"]["aot"] = {"error": f"{type(exc).__name__}: {exc}"}
    mem.append(bc.memory_checkpoint("after_evidence"))

    # ---- informational sum check ------------------------------------------------------
    def med(nm):
        e = comp_rec.get(nm) or {}
        return (e.get("timing") or {}).get("warm", {}).get("median_s")

    nb = comps.n_state_builds
    parts1 = ["a_cosmology", "b_population", "g_prior_eval", "d_pe_reduce", "e_sel_reduce"]
    parts2 = ["w_weights", "d_pe_reduce", "e_sel_reduce"]
    whole_med = med("i_whole")
    sums = {}
    for tag, parts in (("a+b+g+d+e", parts1), ("w+d+e", parts2)):
        vals = [med(p) for p in parts]
        if any(v is None for v in vals):
            continue
        s = float(sum(vals))
        for nbs in sorted({nb, 1} if dark else {0}):
            st = med("fh_prior_state")
            tot = s + (nbs * st if (dark and st is not None) else 0.0)
            name = tag + (f"+{nbs}x(f+h)" if dark else "")
            sums[name] = {"sum_median_s": tot, "whole_median_s": whole_med,
                          "ratio_sum_over_whole": (tot / whole_med) if whole_med else None}
    record["sum_check"] = {
        "informational": True, "sums": sums, "n_state_builds_as_written": nb,
        "state_builds_note": comps.state_builds_note,
        "note": ("warm medians of separately jitted kernels; the whole jit fuses and CSEs across "
                 "components, so the sum is not expected to equal the whole"),
    }

    # ---- write ------------------------------------------------------------------------
    npz_path = os.path.abspath(a.out) + ".components.npz"
    np.savez_compressed(npz_path, **arrays_npz)
    record["components_npz"] = {"file": os.path.basename(npz_path), "sha256": bc.sha256_file(npz_path),
                                "n_arrays": len(arrays_npz), "bytes": os.path.getsize(npz_path),
                                "full_array_coords": full_coords,
                                "big_array_elements": a.big_array_elements}
    record["components"] = comp_rec
    record["component_order"] = ORDER
    record["timing_context"] = {
        "t_import_jax_s": t_import_jax, "t_import_package_s": t_import_pkg,
        "t_build_breakdown": dict(adapter.timing), "compile_during_build": compile_build,
        "t_input_precompute_s": t_precompute,
        "host_loadavg": {"before": list(load_before) if load_before else None,
                         "after": list(load_after) if load_after else None,
                         "os_cpu_count": os.cpu_count()},
        "memory": mem,
        "timed_call_note": ("each timed call = the component kernel (theta-taking kernels get "
                            "jnp.asarray(coord) inside the call, as the main harness) + "
                            "jax.block_until_ready"),
    }
    cache_info["files_at_end"], cache_info["bytes_at_end"] = _dir_inventory(cache_info.get("dir"))
    record["xla_cache"] = cache_info
    record["gaps"].extend(adapter.gaps)
    if a.n_calls < 20:
        record["gaps"].append(f"n_calls={a.n_calls} < 20: below the campaign minimum")
    leftovers = adapter.cleanup()
    if leftovers:
        record["gaps"].append(f"legacy save_path not empty after build: {leftovers}")
    record["status"] = "ok" if not decode_errors else "plan_mismatch"
    record["finished_utc"] = bc.utc_now()
    bc.write_json(a.out, record)
    print(f"[{label}] {a.impl} plan={a.plan} components written -> {a.out} (status {record['status']}"
          + (f", whole vs main bitwise={record['whole_vs_main_record']['bitwise']}"
             if record.get("whole_vs_main_record") else "") + ")")
    return 0 if record["status"] == "ok" else 3


# ---------------------------------------------------------------------------
# compare mode
# ---------------------------------------------------------------------------
def compare_arrays(a, b, rtol, atol_abs=1e-12):
    """Element-wise |A-B| <= rtol*|A| (A the reference), NaN == NaN, +/-inf exact;
    also the D-catvals absolute criterion |A-B| <= atol_abs."""
    a = np.asarray(a)
    b = np.asarray(b)
    if a.shape != b.shape:
        return {"shape_mismatch": [list(a.shape), list(b.shape)], "pass_rel": False,
                "pass_abs": False, "bitwise": False, "max_rel": "inf", "max_abs": "inf"}
    if a.dtype.kind != "f" or b.dtype.kind != "f":
        eq = bool(np.array_equal(a, b))
        return {"pass_rel": eq, "pass_abs": eq, "bitwise": eq, "max_rel": 0.0 if eq else "inf",
                "max_abs": 0.0 if eq else "inf", "n_different": int(np.sum(a != b))}
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    bitwise = bool(np.array_equal(a.view(np.int64), b.view(np.int64)))
    na, nb_ = np.isnan(a), np.isnan(b)
    nan_ok = bool(np.array_equal(na, nb_))
    inf_a, inf_b = np.isinf(a), np.isinf(b)
    inf_ok = bool(np.array_equal(inf_a, inf_b) and np.array_equal(a[inf_a], b[inf_b]))
    fin = np.isfinite(a) & np.isfinite(b)
    d = np.abs(a[fin] - b[fin])
    ref = np.abs(a[fin])
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(ref > 0, d / np.where(ref > 0, ref, 1.0), np.where(d > 0, np.inf, 0.0))
    max_rel = float(rel.max()) if rel.size else 0.0
    max_abs = float(d.max()) if d.size else 0.0
    pass_rel = bool(nan_ok and inf_ok and np.all(d <= rtol * ref))
    pass_abs = bool(nan_ok and inf_ok and np.all(d <= atol_abs))
    return {"pass_rel": pass_rel, "pass_abs": pass_abs, "bitwise": bitwise, "max_rel": bc.fval(max_rel),
            "max_abs": bc.fval(max_abs), "nan_pattern_equal": nan_ok, "inf_equal": inf_ok,
            "n_bit_different": int(np.sum(a.view(np.int64) != b.view(np.int64)))}


def _load_npz(rec_path, rec):
    info = rec.get("components_npz") or {}
    p = os.path.join(os.path.dirname(os.path.abspath(rec_path)), info.get("file", ""))
    if not info.get("file") or not os.path.isfile(p):
        return None, p
    return np.load(p), p


def _num(x):
    if x is None:
        return None
    if isinstance(x, str):
        return float(x)
    return float(x)


def compare(path_a, path_b, rtol=1e-12):
    A, B = bc.read_json(path_a), bc.read_json(path_b)
    for r, p in ((A, path_a), (B, path_b)):
        if r.get("schema") != RECORD_SCHEMA:
            raise SystemExit(f"{p}: not a {RECORD_SCHEMA} record")
    refusals = []
    if A["plan"]["name"] != B["plan"]["name"]:
        refusals.append("different plans")
    if A["coords"]["values_hex"] != B["coords"]["values_hex"]:
        refusals.append("different coordinates")
    for k in ("pe", "sel", "catalog"):
        if (A["inputs"].get(k) or {}).get("sha256") != (B["inputs"].get(k) or {}).get("sha256"):
            refusals.append(f"different {k} input")
    for k in ("n_events", "nsamp", "n_injections"):
        if A["dims"].get(k) != B["dims"].get(k):
            refusals.append(f"different dims.{k}")
    if refusals:
        return {"schema": SUMMARY_SCHEMA, "refused": refusals, "a": path_a, "b": path_b}
    za, pa = _load_npz(path_a, A)
    zb, pb = _load_npz(path_b, B)
    ndraw = float(A["dims"].get("ndraw") or 0.0)
    rows = []
    for nm in ORDER:
        ea, eb = A["components"].get(nm) or {}, B["components"].get(nm) or {}
        meta = COMPONENT_BY_NAME[nm]
        row = {"component": nm, "letter": meta["letter"], "title": meta["title"],
               "legacy_ref": meta["legacy_ref"], "core_ref": meta["core_ref"],
               "same_quantity": meta["same_quantity"],
               "kind_a": ea.get("kind"), "kind_b": eb.get("kind"),
               "available_a": bool(ea.get("available")), "available_b": bool(eb.get("available")),
               "reason_a": ea.get("reason"), "reason_b": eb.get("reason")}
        for side, e in (("a", ea), ("b", eb)):
            t = e.get("timing") or {}
            row[f"warm_median_s_{side}"] = (t.get("warm") or {}).get("median_s")
            row[f"warm_min_s_{side}"] = (t.get("warm") or {}).get("min_s")
            row[f"t_first_call_s_{side}"] = t.get("t_first_call_s")
            row[f"timed_loop_compiles_{side}"] = (t.get("timed_loop_compile") or {}).get("requests")
            aot = e.get("aot") or {}
            hit = (aot.get("compile_counter_delta") or {}).get("compiles") == 0
            row[f"aot_compile_s_{side}"] = None if hit else aot.get("t_compile_s")
            row[f"aot_trace_lower_s_{side}"] = aot.get("t_trace_lower_s")
            row[f"aot_persistent_cache_hit_{side}"] = bool(hit) if aot else None
            row[f"first_call_compiles_{side}"] = (t.get("first_call_compile") or {}).get("compiles")
            row[f"first_call_context_{side}"] = t.get("first_call_context")
        ma, mb = row["warm_median_s_a"], row["warm_median_s_b"]
        row["ratio_b_over_a"] = (mb / ma) if (ma and mb) else None
        oa, ob = ea.get("outputs") or {}, eb.get("outputs") or {}
        if not (row["available_a"] and row["available_b"]) or not (oa and ob):
            row["parity_1e12"] = None
            row["parity_note"] = ("no outputs to compare" if nm in ("j_transfer", "k_layout")
                                  else "not available in both records")
            rows.append(row)
            continue
        keys = {}
        missing = sorted(set(oa) ^ set(ob))
        gate_pass, worst_key, worst_rel = True, None, 0.0
        cat_abs_pass, cat_worst_abs = True, 0.0
        n_elem_min = None
        for key in sorted(set(oa) & set(ob)):
            cls = oa[key]["class"]
            per = []
            elem, rel_worst, abs_worst, ok_rel, ok_abs, digest_eq = 0, 0.0, 0.0, True, True, True
            for da, db in zip(oa[key]["per_coord"], ob[key]["per_coord"]):
                k = da["coord"]
                same = da["sha256"] == db["sha256"] and da["shape"] == db["shape"]
                digest_eq &= same
                nk = f"{nm}__{key}__c{k}"
                if da.get("stored") and db.get("stored") and za is not None and zb is not None \
                        and nk in za.files and nk in zb.files:
                    xa, xb = za[nk], zb[nk]
                    mask_info = None
                    if (nm, key) in MASKED_BY:
                        mkey, why = MASKED_BY[(nm, key)]
                        mk = f"{nm}__{mkey}__c{k}"
                        if mk in za.files and mk in zb.files and np.array_equal(za[mk], zb[mk]):
                            keep = np.asarray(za[mk]) == 0
                            full = compare_arrays(xa, xb, rtol)
                            mask_info = {"masked_by": mkey, "excluded": why,
                                         "n_excluded": int((~keep).sum()),
                                         "unmasked_max_abs": full["max_abs"],
                                         "unmasked_pass_rel": full["pass_rel"]}
                            xa, xb = np.asarray(xa)[keep], np.asarray(xb)[keep]
                    r = compare_arrays(xa, xb, rtol)
                    if mask_info is not None:
                        r["mask"] = mask_info
                    elem += 1
                    ok_rel &= r["pass_rel"]
                    ok_abs &= r["pass_abs"]
                    rel_worst = max(rel_worst, _num(r["max_rel"]))
                    abs_worst = max(abs_worst, _num(r["max_abs"]))
                    per.append(dict(r, coord=k, elementwise=True))
                else:
                    per.append({"coord": k, "elementwise": False, "digest_equal": same})
            keys[key] = {"class": cls, "coords_elementwise": elem, "digest_equal_all": digest_eq,
                         "pass_rel": ok_rel if elem else None, "pass_abs": ok_abs if elem else None,
                         "max_rel": bc.fval(rel_worst), "max_abs": bc.fval(abs_worst), "per_coord": per}
            if cls in ("gate", "catvals"):
                n_elem_min = elem if n_elem_min is None else min(n_elem_min, elem)
            if cls == "gate":
                if elem == 0 or not ok_rel:
                    gate_pass = False
                if rel_worst >= worst_rel:
                    worst_rel, worst_key = rel_worst, key
            elif cls == "catvals":
                cat_abs_pass &= bool(ok_abs) and elem > 0
                cat_worst_abs = max(cat_worst_abs, abs_worst)
                if rel_worst >= worst_rel and worst_key is None:
                    worst_rel, worst_key = rel_worst, key
        has_gate = any(v["class"] == "gate" for v in keys.values())
        if has_gate:
            row["parity_1e12"] = bool(gate_pass) and not missing
            row["criterion"] = f"rtol {rtol:g}, atol 0 on the gate outputs"
        else:
            row["parity_1e12"] = bool(cat_abs_pass) and not missing
            row["criterion"] = "D-catvals: |delta log p| <= 1e-12 absolute (informational)"
        row["max_rel"] = bc.fval(max((_num(v["max_rel"]) for v in keys.values()
                                      if v["class"] in ("gate", "catvals")), default=0.0))
        row["worst_key"] = worst_key
        row["catvals_max_abs"] = bc.fval(cat_worst_abs) if any(v["class"] == "catvals" for v in keys.values()) else None
        row["info_max_rel"] = bc.fval(max((_num(v["max_rel"]) for v in keys.values()
                                           if v["class"] == "info"), default=0.0))
        row["coords_elementwise_min"] = n_elem_min
        row["coords_elementwise_note"] = ("minimum over the gate/catvals outputs of the coordinates "
                                          "compared element by element (arrays above "
                                          "--big-array-elements only at --full-array-coords)")
        row["bitwise_all"] = all(v["digest_equal_all"] for v in keys.values())
        row["keys_missing_in_one"] = missing
        row["keys"] = keys
        # rule annotations (the orchestrator applies the rules; these are flags)
        failing = [k for k, v in keys.items() if v["class"] == "gate" and v["pass_rel"] is False]
        if nm == "e_sel_reduce" and failing == ["n_eff"]:
            ne = [d.get("max") for d in oa["n_eff"]["per_coord"]]
            amp = max(_num(x) for x in ne if x is not None) / ndraw if ndraw else None
            row["rule_flag"] = {"rule": "D-neff candidate", "amplification_N_eff_over_N_draw": amp,
                                "source_quantities_pass": all(keys[q]["pass_rel"] for q in
                                                              ("log_mu", "log_sigma2") if q in keys)}
        if nm == "d_pe_reduce" and failing == ["event_vars"]:
            row["rule_flag"] = {"rule": "D-mcvar candidate (event_mc_variance only)"}
        rows.append(row)
    wa, wb = A.get("whole_vs_main_record"), B.get("whole_vs_main_record")
    summary = {
        "schema": SUMMARY_SCHEMA, "a": os.path.abspath(path_a), "b": os.path.abspath(path_b),
        "a_label": A["label"], "b_label": B["label"], "a_impl": A["implementation"],
        "b_impl": B["implementation"], "plan": A["plan"]["name"], "rtol": rtol, "atol": 0.0,
        "npz": {"a": pa, "b": pb, "a_loaded": za is not None, "b_loaded": zb is not None},
        "rows": rows,
        "all_gate_parity": all(r["parity_1e12"] for r in rows
                               if r["parity_1e12"] is not None and r.get("criterion", "").startswith("rtol")),
        "whole_vs_main_bitwise": {"a": (wa or {}).get("bitwise"), "b": (wb or {}).get("bitwise")},
        "sum_check": {"a": A.get("sum_check"), "b": B.get("sum_check")},
        "trace_numerics_unchanged": {"a": (A.get("trace") or {}).get("numerics_unchanged"),
                                     "b": (B.get("trace") or {}).get("numerics_unchanged")},
        "timing_comparable": (A["device"].get("backend") == B["device"].get("backend")
                              and A["env"].get("host") == B["env"].get("host")
                              and A["config"].get("n_calls") == B["config"].get("n_calls")),
        "blocks": {s: {k: (r["config"].get(k) or {}).get("resolved") for k in ("sel_batch_size", "pe_event_block")}
                   for s, r in (("a", A), ("b", B))},
        "aot_policy": {"a": A.get("aot_policy"), "b": B.get("aot_policy")},
    }
    return summary


def _ms(x):
    return "" if x is None else f"{1e3 * float(x):.3f}"


def _f2(x):
    return "" if x is None else f"{float(x):.2f}"


def _aot(r, side):
    if r.get(f"aot_persistent_cache_hit_{side}"):
        return "cache hit"
    return _f2(r.get(f"aot_compile_s_{side}"))


def summary_markdown(s):
    if s.get("refused"):
        return f"# components compare REFUSED\n\n{s['refused']}\n"
    lines = [f"# Component parity and timing: {s['plan']} ({s['a_impl']} = A vs {s['b_impl']} = B)",
             "", f"A `{s['a_label']}`, B `{s['b_label']}`, rtol {s['rtol']:g}, atol 0. "
             f"Whole vs main harness bit-identical: A {s['whole_vs_main_bitwise']['a']}, "
             f"B {s['whole_vs_main_bitwise']['b']}. Trace numerics unchanged: "
             f"A {s['trace_numerics_unchanged']['a']}, B {s['trace_numerics_unchanged']['b']}.", "",
             "| component | parity 1e-12 | criterion | worst key | max_rel | A warm ms | B warm ms | B/A | "
             "A first s | B first s | A AOT compile s | B AOT compile s | coords elem. |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        par = {True: "pass", False: "FAIL", None: "n/a"}[r["parity_1e12"]]
        crit = "D-catvals abs" if r.get("criterion", "").startswith("D-catvals") else (
            "rtol" if r.get("criterion") else "")
        first_a, first_b = r.get("t_first_call_s_a"), r.get("t_first_call_s_b")
        ratio = r.get("ratio_b_over_a")
        lines.append(
            f"| {r['component']} | {par} | {crit} | {r.get('worst_key') or ''} | "
            f"{'' if r.get('max_rel') is None else r['max_rel']} | {_ms(r['warm_median_s_a'])} | "
            f"{_ms(r['warm_median_s_b'])} | {'' if ratio is None else f'{ratio:.2f}'} | "
            f"{_f2(first_a)} | {_f2(first_b)} | {_aot(r, 'a')} | {_aot(r, 'b')} | "
            f"{'' if r.get('coords_elementwise_min') is None else r['coords_elementwise_min']} |")
    lines += ["", "Sum of component warm medians vs whole (informational):", ""]
    for side in ("a", "b"):
        sc = (s.get("sum_check") or {}).get(side) or {}
        for k, v in (sc.get("sums") or {}).items():
            rr = v.get("ratio_sum_over_whole")
            lines.append(f"* {side.upper()} {k}: {_ms(v['sum_median_s'])} ms vs whole "
                         f"{_ms(v['whole_median_s'])} ms (ratio {'' if rr is None else f'{rr:.2f}'})")
    notes = [r for r in s["rows"] if r.get("rule_flag")]
    if notes:
        lines += ["", "Rule flags:", ""] + [f"* {r['component']}: {r['rule_flag']}" for r in notes]
    return "\n".join(lines) + "\n"


def compare_main(argv):
    ap = argparse.ArgumentParser(prog="bench_components.py compare")
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--rtol", type=float, default=1e-12)
    ap.add_argument("--out", default=None)
    ap.add_argument("--md", default=None)
    x = ap.parse_args(argv)
    s = compare(x.a, x.b, x.rtol)
    if x.out:
        bc.write_json(x.out, s)
    md = summary_markdown(s)
    if x.md:
        with open(x.md, "w") as f:
            f.write(md)
    print(md)
    if s.get("refused"):
        return 2
    return 0 if s["all_gate_parity"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        sys.exit(compare_main(sys.argv[2:]))
    sys.exit(main())
