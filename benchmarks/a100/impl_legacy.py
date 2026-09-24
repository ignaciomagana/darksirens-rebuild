"""Legacy (frozen darksirens c042527) adapter of the fixed-coordinate harness.

The kernel is the likelihood the legacy CLI builds and hands to its samplers:
the phase functions of ``darksirens.cli.inference`` in the CLI's own order,
ending in ``_build_likelihood`` -> ``likelihood.factory.make_likelihood``,
which jits the whole closure with the data operands, the distance table and
the smoothing operator passed as jit ARGUMENTS
(``darksirens/likelihood/factory.py:945-1024``). That one callable is both the
"whole-jit" and the "as-shipped" kernel for legacy: dynesty calls it as
``float(np.asarray(likelihood(jnp.asarray(theta))))``.

Legacy returns only the scalar log-likelihood. The per-event log evidences and
MC variances, log_mu, N_eff and the selection correction are RE-ASSEMBLED
here from legacy internals, transcribing the K = 1, non-frozen, isotropic,
non-WL, counterpart-free branch of ``darksiren_log_likelihood`` /
``_ll_given_states`` (``darksirens/likelihood/core.py:1030-1062`` prior
states, ``:1173-1500`` weights, selection and blocked PE reduction), under the
same ``sel_batch_size`` / ``pe_event_block``. It extends the recipe of core's
``tools/probe_spectral_likelihood.py::_legacy`` with the prepared redshift-prior
state the factory uses. Every record checks the re-assembled total against the
factory kernel's value.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import time

import numpy as np

IMPL = "legacy"


def import_package():
    """Import the legacy package and its CLI (the CLI import configures JAX)."""
    import darksirens
    from darksirens.cli import inference as cli  # noqa: F401  (configure_jax_runtime at import)
    from darksirens.core.jax_config import configure_jax_runtime

    configure_jax_runtime()
    if not hasattr(cli, "_build_likelihood"):
        raise RuntimeError("imported darksirens has no legacy CLI build path: not the legacy package")
    return darksirens


def _block_arg(flag, value):
    if value == "default":
        return []
    if value == "none":
        return [flag, "off"]
    return [flag, str(int(value))]


def legacy_cli_args(plan, pe_path, sel_path, save_path, sel_batch, pe_block, seed):
    """The exact darksirens_inference argument vector that configures ``plan``."""
    argv = [
        "--gw_path", pe_path,
        "--gwselection_path", sel_path,
        "--universe_model", "spectral_sirens",
        "--pop_model", plan["population_model"],
        "--sampler", "dynesty",
        "--save_path", save_path,
        "--seed", str(int(seed)),
    ]
    argv += _block_arg("--sel_batch_size", sel_batch)
    argv += _block_arg("--pe_event_block", pe_block)
    fixed_values = {}
    if plan["sample_H0"]:
        # H0 sampled on the target box; Om0 fixed individually; w0, wa fixed as
        # the dark-energy block (W0_FID, WA_FID).
        argv += ["--fix_de", "true",
                 "--prior_overrides", json.dumps({"H0": list(plan["H0_bounds"])})]
        fixed_values["Om0"] = plan["fixed"]["Om0"]
    else:
        # Whole cosmology block fixed at H0_FID, OM0_FID, W0_FID, WA_FID.
        argv += ["--fix_cosmology", "true"]
    k = plan["sample_population"]
    if k == "none":
        argv += ["--fix_population", "true", "--population_fiducials", plan["fiducial_set"]]
    elif k != "all":
        for lab in plan["population_labels"][int(k):]:
            fixed_values[lab] = plan["fixed"][lab]
    if fixed_values:
        argv += ["--fixed_parameter_values", json.dumps(fixed_values)]
    return argv


class LegacyAdapter:
    impl = IMPL

    def __init__(self, plan, pe_path, sel_path, *, sel_batch, pe_block, jit_mode, seed,
                 save_dir, counter):
        self.plan = plan
        self.pe_path = pe_path
        self.sel_path = sel_path
        self.jit_mode = jit_mode
        self.counter = counter
        self.gaps = []
        self.timing = {}
        self.save_dir = save_dir
        self.cli_argv = legacy_cli_args(plan, pe_path, sel_path, save_dir, sel_batch, pe_block, seed)
        self.requested_blocks = {"sel_batch_size": sel_batch, "pe_event_block": pe_block}
        self.cli_log = ""

    # ------------------------------------------------------------------ build
    def build(self):
        from darksirens.cli import inference as cli

        os.makedirs(self.save_dir, exist_ok=True)
        sink = io.StringIO()
        t0 = time.perf_counter()
        with contextlib.redirect_stdout(sink):
            opts = cli.build_parser().parse_args(self.cli_argv)
            cli._normalize_multitracer_paths(opts)
            cli._check_latent_field_mode(opts)
            cli._stamp_latent_artifact_fingerprint(opts)
            cli._resolve_catalog_sky_weighting(opts)
            cli._validate_multitracer_config(opts)
            cli._canonicalize_fixed_flags(opts)
            cli._configure_performance_grids(opts)
            prior_overrides, fixed = cli._parse_structured_options(opts)
            cli._resolve_sampler_config(opts)
            cli._apply_bright_siren_overrides(opts)
            cli._validate_run_config(opts)
            t1 = time.perf_counter()
            data = cli._load_and_report_data(opts)
            t2 = time.perf_counter()
            cli._resolve_single_catalog_marks(opts, data)
            pspace = cli._build_and_report_parameter_space(opts, data, prior_overrides, fixed)
            likelihood = cli._build_likelihood(opts, data, pspace, fixed)
            t3 = time.perf_counter()
        self.cli_log = sink.getvalue()
        self.timing.update(t_config_s=t1 - t0, t_load_s=t2 - t1, t_build_s=t3 - t2)
        self.opts, self.data, self.pspace, self.likelihood = opts, data, pspace, likelihood
        self.fixed_parameter_values = dict(fixed)
        self.prior_overrides = dict(prior_overrides or {})
        ops = likelihood.operands
        self.gw_pe, self.em_pe, self.gw_sel, self.em_sel = ops[0], ops[1], ops[2], ops[3]
        self.labels = [str(x) for x in pspace.labels]
        self.n_events = int(data["nEvents"])
        self.nsamp = int(data["nsamp"])
        self.ndraw = float(data["Ndraw"])
        self.n_injections = int(np.asarray(data["dLsels"]).shape[0])
        self.sel_batch_size = opts.sel_batch_size
        self.pe_event_block = opts.pe_event_block
        self.max_likelihood_variance = float(opts.max_likelihood_variance)
        self.soft_guard = bool(getattr(opts, "selection_neff_soft_guard", False))
        self._injection_order()
        self._build_diag_fns()

    def _injection_order(self):
        """Legacy's build-time injection permutation, recovered and verified.

        ``make_likelihood`` stably sorts the injections by their catalog pixel
        (``darksirens/likelihood/factory.py:1140-1163``, applied at
        ``:2687-2693``); a spectral run has no catalog and gets nside-1 pixels,
        so the selection arrays inside the kernel are a permutation of the file
        order that core keeps. Selection masks are mapped back to file order
        with this permutation, verified bit for bit against the loaded ``dLsels``.
        """
        import hashlib

        from darksirens.likelihood.factory import _injection_pixel_order

        n = self.n_injections
        pix = np.asarray(self.data["pixels_sel"])
        order = _injection_pixel_order(pix)
        permuted = order is not None
        if order is None:
            order = np.arange(n)
        order = np.asarray(order, dtype=np.int64)
        file_dL = np.asarray(self.data["dLsels"], dtype=np.float64)
        int_dL = np.asarray(self.gw_sel.dL, dtype=np.float64)[:n]
        verified = bool(np.array_equal(int_dL, file_dL[order]))
        if not verified:
            raise RuntimeError("could not reproduce legacy's injection permutation; "
                               "selection masks cannot be mapped to file order")
        self.sel_order = order
        self.injection_order_info = {
            "permuted": permuted,
            "n_unique_pixels_sel": int(np.unique(pix).size),
            "nside": self.data.get("nside"),
            "source": ("darksirens/likelihood/factory.py:1140-1163 _injection_pixel_order"
                       "(data['pixels_sel']), applied at :2687-2693"),
            "verified_internal_dL_equals_file_dL_permuted": verified,
            "order_sha256": hashlib.sha256(order.tobytes()).hexdigest(),
            "masks_reported_in": "file order (permutation undone)",
        }

    def operands_for_sync(self):
        lk = self.likelihood
        return (lk.operands, lk.distance_table, lk.smoothing_operator)

    def config(self):
        o = self.opts
        return {
            "kernel": "legacy_factory_closure",
            "kernel_note": ("legacy likelihood.factory.make_likelihood closure: whole-likelihood "
                            "jax.jit with data operands, distance table and smoothing operator "
                            "as jit arguments; the same callable is the as-shipped (dynesty) "
                            "kernel, so --jit whole and --jit asis run the same kernel"),
            "jit_mode_requested": self.jit_mode,
            "jit_mode_effective": "factory_whole_jit (== as-shipped)",
            "legacy_cli_args": self.cli_argv,
            "sel_batch_size": {"requested": self.requested_blocks["sel_batch_size"],
                               "resolved": o.sel_batch_size},
            "pe_event_block": {"requested": self.requested_blocks["pe_event_block"],
                               "resolved": o.pe_event_block},
            "block_size_resolution": getattr(o, "block_size_resolution", None),
            "max_likelihood_variance": float(o.max_likelihood_variance),
            "selection_neff_guard": getattr(o, "selection_neff_guard", None),
            "selection_neff_soft_guard": bool(getattr(o, "selection_neff_soft_guard", False)),
            "catalog_sky_weighting": getattr(o, "catalog_sky_weighting", None),
            "redshift_prior_barrier": getattr(o, "redshift_prior_barrier", None),
            "frozen_redshift_prior": bool(getattr(self.likelihood, "frozen_redshift_prior", False)),
            "kde_window": getattr(self.likelihood, "kde_window", None),
            "fixed_parameter_values": self.fixed_parameter_values,
            "prior_overrides": self.prior_overrides,
            "fix_cosmology": bool(o.fix_cosmology),
            "fix_de": bool(o.fix_de),
            "fix_population": bool(o.fix_population),
            "population_fiducials": getattr(o, "population_fiducials", None),
            "sampler_seed": getattr(o, "seed", None),
            "plan_adapter": None,
            "legacy_injection_order": self.injection_order_info,
        }

    def dims(self):
        return {
            "n_events": self.n_events,
            "nsamp": self.nsamp,
            "n_pe_samples": int(self.gw_pe.dL.shape[0]),
            "n_injections": self.n_injections,
            "n_injections_padded": int(self.gw_sel.dL.shape[0]),
            "ndraw": self.ndraw,
        }

    # ----------------------------------------------------------------- kernel
    def timed_call(self, coord_np):
        import jax.numpy as jnp

        return self.likelihood(jnp.asarray(coord_np))

    def implementation_coord(self, named_row):
        return np.asarray(named_row, dtype=np.float64)

    # -------------------------------------------------------- plan assertions
    def plan_labels_bounds(self):
        ps = self.pspace
        kinds = [list(k) if isinstance(k, (list, tuple)) else [k] for k in (ps.prior_kinds or [])]
        return {
            "labels": self.labels,
            "lower": [float(x) for x in np.asarray(ps.lower_bound, dtype=np.float64)],
            "upper": [float(x) for x in np.asarray(ps.upper_bound, dtype=np.float64)],
            "prior_kinds": kinds,
            "pop_params_fid": [float(x) for x in np.asarray(ps.pop_params_fid, dtype=np.float64)],
        }

    def registry_view(self):
        from darksirens.core import constants as C
        from darksirens.gw.populations import pop_model_prior_parser
        from darksirens.gw.populations.registry import get_fixed_population_params

        p = self.plan
        lo, hi, labels, kinds, _latex = pop_model_prior_parser(
            p["population_model"], shared_beta=p["shared_beta"], shared_spin=p["shared_spin"],
            shared_gamma=p["shared_gamma"])
        fid = get_fixed_population_params(
            p["population_model"], shared_beta=p["shared_beta"], shared_spin=p["shared_spin"],
            shared_gamma=p["shared_gamma"], fiducials=p["fiducial_set"])
        return {
            "labels": [str(x) for x in labels],
            "lower": [float(x) for x in np.asarray(lo, dtype=np.float64)],
            "upper": [float(x) for x in np.asarray(hi, dtype=np.float64)],
            "prior_kinds": [list(k) for k in kinds],
            "fiducials": [float(x) for x in np.asarray(fid, dtype=np.float64)],
            "H0_FID": float(C.H0_FID), "OM0_FID": float(C.OM0_FID),
            "W0_FID": float(C.W0_FID), "WA_FID": float(C.WA_FID),
            "sources": {
                "constants": "darksirens/core/constants.py:12-15",
                "registry": "darksirens.gw.populations.pop_model_prior_parser / "
                            "registry.get_fixed_population_params",
            },
        }

    def decode(self, coord_np):
        """Full (H0, Om0, w0, wa, population...) vector the kernel will see."""
        import jax.numpy as jnp

        cosmo, _survey, pop, _sky, _marks = self.decoder.decode(jnp.asarray(coord_np))
        cos = [float(np.asarray(getattr(cosmo, n))) for n in ("H0", "Om0", "w0", "wa")]
        return cos + [float(x) for x in np.asarray(pop, dtype=np.float64)]

    # ------------------------------------------------------ diagnostics build
    def _build_diag_fns(self):
        import jax
        import jax.numpy as jnp
        from jax import lax

        from darksirens.gw.populations import pop_model_parser
        from darksirens.inference.parameters import build_parameter_decoder
        from darksirens.inference.utils import log_sample_weight
        from darksirens.likelihood.core import (
            _pe_chunk_plan,
            redshift_prior_state_sharing,
            selection_prior_model,
        )
        from darksirens.likelihood.factory import _resolve_redshift_prior_materialization
        from darksirens.likelihood.selection import (
            compute_selection_term,
            log_evidence_and_mc_variance,
            selection_log_correction,
        )
        from darksirens.redshift.prior import (
            eval_redshift_prior_with_state,
            prepare_redshift_prior_state,
        )
        from darksirens.utils.cosmology import dL_of_z, threads_distance_table
        from darksirens.utils.cosmology import zgrid as cosmo_zgrid

        opts = self.opts
        p = self.plan
        self.decoder = build_parameter_decoder(
            opts, self.pspace.pop_params_fid,
            fixed_parameter_values=self.fixed_parameter_values,
            wl_params=self.data.get("wl_params"))
        dec = self.decoder
        pe_model = "spectral_sirens"
        sel_model = selection_prior_model("spectral_sirens")
        materialize = _resolve_redshift_prior_materialization(opts)
        sky_weighting = getattr(opts, "catalog_sky_weighting", "conditional")
        share = redshift_prior_state_sharing("spectral_sirens", (self.em_pe,), (self.em_sel,))
        share0 = bool(share[0]) if share else False
        nE, ns, Nd = self.n_events, self.nsamp, self.ndraw
        sel_bs, pe_eb = self.sel_batch_size, self.pe_event_block
        maxvar, soft = self.max_likelihood_variance, self.soft_guard
        pop_model = p["population_model"]
        kw_pop = dict(shared_beta=p["shared_beta"], shared_spin=p["shared_spin"],
                      shared_gamma=p["shared_gamma"])
        self.diag_provenance = {
            "kind": "reassembled_from_legacy_internals",
            "transcribes": "darksirens/likelihood/core.py:1030-1062 (prior states), "
                           ":1173-1500 (_ll_given_states: weights, compute_selection_term, "
                           "blocked PE reduction, selection_log_correction), :2070 (isfinite)",
            "decoder": "darksirens.inference.parameters.build_parameter_decoder(...).decode",
            "share_prior_state": share0,
            "materialize_redshift_prior_state": bool(materialize),
            "jit": "legacy darksirens.utils.cosmology.threads_distance_table (table as argument)",
        }

        def _weight_fns(coord, em_pe, em_sel):
            cosmo, survey, pop_params, _sky, _marks = dec.decode(coord)
            log_p_pop = pop_model_parser(pop_model=pop_model, **kw_pop)
            dL_grid = dL_of_z(cosmo_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dL_grid[0], dL_grid[-1]
            st_u = prepare_redshift_prior_state(
                pe_model, cosmo, survey, em_pe, mark_model="none", mark_params=None,
                mark_names=(), materialize_state=materialize,
                catalog_sky_weighting=sky_weighting, kde_window=None)
            st_s = st_u if share0 else prepare_redshift_prior_state(
                sel_model, cosmo, survey, em_sel, mark_model="none", mark_params=None,
                mark_names=(), materialize_state=materialize,
                catalog_sky_weighting=sky_weighting, kde_window=None)

            def prior_pe(z, pix, catalogs):
                return eval_redshift_prior_with_state(
                    pe_model, st_u, z, pix, cosmo, survey, catalogs[0],
                    catalog_sky_weighting=sky_weighting, empty_routing=None)

            def prior_sel(z, pix, catalogs):
                return eval_redshift_prior_with_state(
                    sel_model, st_s, z, pix, cosmo, survey, catalogs[0],
                    catalog_sky_weighting=sky_weighting, empty_routing=None)

            def make(prior_fn):
                def fn(m1det, q, dL, chieff, pix, prior_wt, catalogs, spin=None):
                    supported = (dL >= lo) & (dL <= hi)
                    dL_c = jnp.clip(dL, lo, hi)
                    ldw = log_sample_weight(m1det, q, dL_c, chieff, pix, prior_wt, cosmo, survey,
                                            pop_params, catalogs, log_p_pop, prior_fn,
                                            spin=spin, dL_grid=dL_grid)
                    return jnp.where(supported & jnp.isfinite(ldw), ldw, -jnp.inf)
                return fn

            return make(prior_pe), make(prior_sel), (lo, hi)

        @threads_distance_table()
        def diag(coord, gw_pe, em_pe, gw_sel, em_sel, distance_table=None):
            w_pe, w_sel, _ = _weight_fns(coord, em_pe, em_sel)
            log_mu, n_eff, _ = compute_selection_term(
                gw_sel, (em_sel,), w_sel, Nd, nE, sel_batch_size=sel_bs,
                sky_log_weight_fn=None)
            pe_block = nE if pe_eb is None else min(pe_eb, nE)

            def _pe_chunk_ldw(s, n):
                sl = lambda arr: lax.dynamic_slice_in_dim(arr, s, n)  # noqa: E731
                valid = sl(gw_pe.valid) & (sl(gw_pe.prior_wt) > 0.0)
                ldw = w_pe(sl(gw_pe.m1det), sl(gw_pe.q), sl(gw_pe.dL), sl(gw_pe.chieff),
                           sl(gw_pe.pixels), sl(gw_pe.prior_wt), (em_pe,),
                           spin=sl(gw_pe.spin) if gw_pe.spin is not None else None)
                return jnp.where(valid & jnp.isfinite(ldw), ldw, -jnp.inf)

            def _reduce_events(s, m):
                ldw = _pe_chunk_ldw(s, m * ns).reshape(m, ns)
                return jax.vmap(lambda row: log_evidence_and_mc_variance(row, ns))(ldw)

            def _chunk_scan(_, s):
                return None, _reduce_events(s, pe_block)

            block_samps = pe_block * ns
            n_full, rem, overlap_tail = _pe_chunk_plan(nE, pe_block)
            parts = []
            if overlap_tail:
                starts = jnp.asarray([i * block_samps for i in range(n_full)]
                                     + [(nE - pe_block) * ns])
                _, stacked = lax.scan(_chunk_scan, None, starts)
                parts.append(jax.tree_util.tree_map(
                    lambda a: a[:n_full].reshape((n_full * pe_block,) + a.shape[2:]), stacked))
                parts.append(jax.tree_util.tree_map(lambda a: a[n_full, pe_block - rem:], stacked))
            else:
                if n_full == 1:
                    parts.append(_reduce_events(0, pe_block))
                elif n_full > 1:
                    _, stacked = lax.scan(_chunk_scan, None, jnp.arange(n_full) * block_samps)
                    parts.append(jax.tree_util.tree_map(
                        lambda a: a.reshape((n_full * pe_block,) + a.shape[2:]), stacked))
                if rem > 0:
                    parts.append(_reduce_events(n_full * block_samps, rem))
            event_lls = jnp.concatenate([q[0] for q in parts])
            event_vars = jnp.concatenate([q[1] for q in parts])
            sel_ll = selection_log_correction(
                log_mu, n_eff, nE, soft_guard=soft, max_likelihood_variance=maxvar,
                pe_variance_sum=jnp.sum(event_vars))
            ll = sel_ll + jnp.sum(event_lls)
            total = jnp.where(jnp.isfinite(ll), ll, -jnp.inf)
            return total, event_lls, event_vars, log_mu, n_eff, sel_ll

        def _make_masks(is_selection):
            @threads_distance_table()
            def sample_masks(coord, gw, em_pe, em_sel, distance_table=None):
                w_pe, w_sel, (lo, hi) = _weight_fns(coord, em_pe, em_sel)
                w = w_sel if is_selection else w_pe
                cat = (em_sel,) if is_selection else (em_pe,)
                ldw = w(gw.m1det, gw.q, gw.dL, gw.chieff, gw.pixels, gw.prior_wt, cat,
                        spin=gw.spin)
                structural = gw.valid & (gw.prior_wt > 0.0)
                support = (gw.dL >= lo) & (gw.dL <= hi)
                final = structural & jnp.isfinite(ldw)
                return structural, support, final
            return sample_masks

        self._diag = diag
        self._sample_masks = {False: _make_masks(False), True: _make_masks(True)}
        self._jnp = jnp

    # ----------------------------------------------------------- diagnostics
    def diagnostics(self, coord_np):
        jnp = self._jnp
        out = self._diag(jnp.asarray(coord_np), self.gw_pe, self.em_pe, self.gw_sel, self.em_sel)
        total, ell, evar, log_mu, n_eff, sel_ll = [np.asarray(x) for x in out]
        return {
            "diag_total_logL": total,
            "event_log_evidence": ell,
            "event_mc_variance": evar,
            "log_mu": log_mu,
            "n_eff": n_eff,
            "selection_log_correction": sel_ll,
        }

    def masks(self, coord_np, chunk):
        import jax

        jnp = self._jnp
        coord = jnp.asarray(coord_np)

        def run(gw, n, is_sel):
            outs = []
            for s in range(0, n, chunk):
                e = min(n, s + chunk)
                sub = jax.tree_util.tree_map(lambda a: a[s:e], gw)
                outs.append([np.asarray(x) for x in
                             self._sample_masks[is_sel](coord, sub, self.em_pe, self.em_sel)])
            return [np.concatenate([o[i] for o in outs]) for i in range(3)]

        pe = run(self.gw_pe, int(self.gw_pe.dL.shape[0]), False)
        sel_internal = run(self.gw_sel, self.n_injections, True)  # unpadded prefix only
        sel = []
        for m in sel_internal:  # internal row j is file row sel_order[j]
            f = np.empty_like(m)
            f[self.sel_order] = m
            sel.append(f)
        return pe, sel

    def mask_order_dL(self):
        """(PE dL, selection dL) in the order the masks are reported."""
        pe = np.asarray(self.gw_pe.dL, dtype=np.float64)
        internal = np.asarray(self.gw_sel.dL, dtype=np.float64)[: self.n_injections]
        sel = np.empty_like(internal)
        sel[self.sel_order] = internal
        return pe, sel

    # ----------------------------------------------------------- jit evidence
    def jit_evidence(self, coord_np):
        import jax.numpy as jnp

        from bench_common import aot_report, jaxpr_const_report

        lk = self.likelihood
        args = (jnp.asarray(coord_np), lk.operands, lk.distance_table, lk.smoothing_operator)
        data_arrays = {
            "gw_pe.m1det": self.gw_pe.m1det, "gw_pe.dL": self.gw_pe.dL,
            "gw_pe.prior_wt": self.gw_pe.prior_wt,
            "gw_sel.m1det": self.gw_sel.m1det, "gw_sel.dL": self.gw_sel.dL,
            "gw_sel.prior_wt": self.gw_sel.prior_wt,
            "distance_table": lk.distance_table,
        }
        rep = {"kernel": "likelihood.jitted_body(coord, operands, distance_table, smoothing_operator)"}
        rep["jaxpr"] = jaxpr_const_report(lk.jitted_body, args, {}, data_arrays)
        rep["aot"] = aot_report(lk.jitted_body, args, {}, self.counter)
        return rep

    def cleanup(self):
        try:
            if os.path.isdir(self.save_dir) and not os.listdir(self.save_dir):
                os.rmdir(self.save_dir)
                return []
            return sorted(os.listdir(self.save_dir)) if os.path.isdir(self.save_dir) else []
        except OSError:
            return None

    def remove_save_dir(self):
        shutil.rmtree(self.save_dir, ignore_errors=True)
