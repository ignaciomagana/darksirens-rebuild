"""darksirens-core adapter of the fixed-coordinate harness.

Kernels:

* ``asis`` (as-shipped): the ``BoundAnalysis`` returned by
  ``darksirens.runtime_binding.bind_analysis`` called EAGERLY, exactly what the
  core Dynesty adapter calls per point
  (``src/darksirens/inference/dynesty_adapter.py:79-82``) after
  ``ds.infer`` binds the analysis (``src/darksirens/inference/public.py:170-182``).
* ``whole``: the same ``BoundAnalysis.__call__`` traced under one ``jax.jit``
  whose ARGUMENTS are the coordinate, the PE and selection ``GWEvent`` pytrees,
  the comoving-distance table and core's ambient jit channels (the
  completeness smoothing operator). It uses core's own
  ``darksirens.cosmology.distances.threads_distance_table`` so the tables are
  jit parameters, never HLO literals; the record carries the jaxpr constant
  inventory and the AOT module size that prove it.

Diagnostics come from core's own
``likelihood.hierarchical.spectral_siren_log_likelihood(return_diagnostics=True)``
with the arguments ``BoundAnalysis.__call__`` passes, decoded with the private
``runtime_binding._decode_theta``; they are evaluated eagerly in ``asis`` mode
and under a table-threading jit in ``whole`` mode.
"""

from __future__ import annotations

import dataclasses
import time

import numpy as np

IMPL = "core"


def import_package():
    import darksirens as ds

    ds.configure_jax_runtime()
    import darksirens.runtime_binding as rb

    if not hasattr(rb, "bind_analysis"):
        raise RuntimeError("imported darksirens has no runtime_binding.bind_analysis: not core")
    try:
        import darksirens.cli  # noqa: F401
    except ImportError:
        pass
    else:
        raise RuntimeError("imported darksirens has a cli package: this is the legacy tree, not core")
    return ds


def _block_value(v):
    if v in ("default", "none"):
        return None
    return int(v)


class CoreAdapter:
    impl = IMPL

    def __init__(self, plan, pe_path, sel_path, *, sel_batch, pe_block, jit_mode, seed,
                 save_dir, counter):
        if jit_mode not in ("whole", "asis"):
            raise ValueError("--jit must be whole or asis")
        self.plan = plan
        self.pe_path = pe_path
        self.sel_path = sel_path
        self.jit_mode = jit_mode
        self.counter = counter
        self.requested_blocks = {"sel_batch_size": sel_batch, "pe_event_block": pe_block}
        self.sel_batch_req = _block_value(sel_batch)
        self.pe_block_req = _block_value(pe_block)
        self.seed = seed
        self.gaps = []
        self.timing = {}

    # ------------------------------------------------------------------ build
    def _analysis(self):
        import darksirens as ds

        p = self.plan
        h0 = tuple(p["H0_bounds"]) if p["sample_H0"] else p["fixed"]["H0"]
        cosmology = ds.Cosmology(H0=h0, Om0=p["fixed_cosmology"]["Om0"],
                                 w0=p["fixed_cosmology"]["w0"], wa=p["fixed_cosmology"]["wa"])
        k = p["sample_population"]
        fixed = True if k == "none" else None
        population = ds.Population(p["population_model"], fixed=fixed,
                                   shared_beta=p["shared_beta"], shared_spin=p["shared_spin"],
                                   shared_gamma=p["shared_gamma"])
        return ds.model(cosmology=cosmology, population=population)

    def build(self):
        import jax
        import jax.numpy as jnp

        import darksirens as ds
        from darksirens.runtime_binding import bind_analysis, required_fit_columns

        p = self.plan
        t0 = time.perf_counter()
        analysis = self._analysis()
        fit_columns = required_fit_columns(analysis)
        t1 = time.perf_counter()
        events = ds.load_events(self.pe_path, fit_columns=fit_columns)
        injections = ds.load_injections(self.sel_path, fit_columns=fit_columns)
        t2 = time.perf_counter()
        bound = bind_analysis(
            analysis, events=events, injections=injections,
            selection_neff_soft_guard=False,
            sel_batch_size=self.sel_batch_req, pe_event_block=self.pe_block_req)
        t3 = time.perf_counter()
        self.analysis, self.events, self.injections, self.bound = analysis, events, injections, bound
        self.fit_columns = tuple(fit_columns)
        self.labels = [str(x) for x in analysis.parameters.labels]

        # Plan adapter: core has no partial population fixing (ds.Population is
        # either fully sampled or fully fixed, src/darksirens/analysis.py:288-308),
        # so a plan sampling the first k population parameters is evaluated on
        # the full H0+population plan with the other parameters inserted at the
        # fiducials. The insertion is part of the kernel (inside the jit for
        # --jit whole, one eager scatter for --jit asis).
        k = p["sample_population"]
        self.adapter_info = None
        if k not in ("all", "none"):
            full_names = self.labels
            base = np.asarray([p["fiducials"][n] for n in full_names], dtype=np.float64)
            idx = np.asarray([full_names.index(n) for n in p["sampled"]], dtype=np.int32)
            self._embed_base = jnp.asarray(base)
            self._embed_idx = jnp.asarray(idx)

            def embed(theta):
                return self._embed_base.at[self._embed_idx].set(theta)

            self.embed = embed
            self.adapter_info = {
                "kind": "embed_sampled_into_full_plan",
                "reason": ("core ds.Population cannot fix part of the population "
                           "(src/darksirens/analysis.py:288-308); the harness evaluates the "
                           "full H0+population BoundAnalysis with the non-sampled population "
                           "parameters at their fiducials"),
                "core_plan_labels": full_names,
                "sampled_indices_in_core_plan": idx.tolist(),
                "fixed_inserted": {n: p["fiducials"][n] for n in full_names if n not in p["sampled"]},
            }
            self.gaps.append("spectral_joint_small: core has no public partial-population "
                             "fixing; evaluated through a harness embedding into the full plan")
        else:
            self.embed = lambda theta: theta

        from darksirens.cosmology.distances import threads_distance_table

        bound_ = bound
        embed_ = self.embed

        @threads_distance_table()
        def whole(theta, gw_pe, gw_sel, distance_table=None):
            b = dataclasses.replace(bound_, gw_pe=gw_pe, gw_selection=gw_sel)
            return b(embed_(theta))

        self._whole = whole
        self.timing.update(t_config_s=t1 - t0, t_load_s=t2 - t1, t_build_s=t3 - t2,
                           t_model_s=t1 - t0, t_bind_s=t3 - t2)
        self._build_diag_fns()
        self._jax, self._jnp = jax, jnp

    def operands_for_sync(self):
        from darksirens.cosmology.distances import distance_table

        return (self.bound.gw_pe, self.bound.gw_selection, distance_table())

    def config(self):
        b = self.bound
        kernel = "core_bound_eager" if self.jit_mode == "asis" else "core_bound_whole_jit"
        note = ("BoundAnalysis called eagerly (as the core Dynesty adapter calls it)"
                if self.jit_mode == "asis" else
                "BoundAnalysis.__call__ under one jax.jit via core threads_distance_table; "
                "coordinate, gw_pe, gw_selection, distance table and ambient channels are "
                "jit arguments")
        return {
            "kernel": kernel,
            "kernel_note": note,
            "jit_mode_requested": self.jit_mode,
            "jit_mode_effective": kernel,
            "sel_batch_size": {"requested": self.requested_blocks["sel_batch_size"],
                               "resolved": b.sel_batch_size},
            "pe_event_block": {"requested": self.requested_blocks["pe_event_block"],
                               "resolved": b.pe_event_block},
            "max_likelihood_variance": float(b.max_likelihood_variance),
            "selection_neff_soft_guard": bool(b.selection_neff_soft_guard),
            "fit_columns": list(self.fit_columns),
            "required_fit_columns": list(b.required_fit_columns),
            "population_fixed": self.analysis.population.fixed,
            "population_fiducial_set": self.analysis.population.fiducial_set,
            "plan_adapter": self.adapter_info,
            "bind_call": ("bind_analysis(analysis, events, injections, selection_neff_soft_guard="
                          "False, sel_batch_size, pe_event_block) with the default "
                          "max_likelihood_variance (ds.infer with sampler='dynesty' binds the same)"),
        }

    def dims(self):
        b = self.bound
        return {
            "n_events": int(b.n_events),
            "nsamp": int(b.nsamp),
            "n_pe_samples": int(b.gw_pe.dL.shape[0]),
            "n_injections": int(self.injections.n_injections),
            "n_injections_padded": int(b.gw_selection.dL.shape[0]),
            "ndraw": float(b.n_draw),
        }

    # ----------------------------------------------------------------- kernel
    def timed_call(self, coord_np):
        jnp = self._jnp
        theta = jnp.asarray(coord_np)
        if self.jit_mode == "asis":
            return self.bound(self.embed(theta))
        return self._whole(theta, self.bound.gw_pe, self.bound.gw_selection)

    # -------------------------------------------------------- plan assertions
    def plan_labels_bounds(self):
        pl = self.analysis.parameters
        return {
            "labels": self.labels,
            "lower": [float(x) for x in pl.lower],
            "upper": [float(x) for x in pl.upper],
            "prior_kinds": [list(k) for k in pl.prior_kinds],
            "fixed_cosmology": {n: float(v) for n, v in pl.fixed_cosmology},
            "fixed_population": (None if pl.fixed_population is None
                                 else [float(x) for x in pl.fixed_population]),
            "population_labels": list(pl.population_labels),
        }

    def registry_view(self):
        from darksirens.cosmology import parameters as C
        from darksirens.population import get_fixed_population_params, pop_model_prior_parser

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
                "constants": "src/darksirens/cosmology/parameters.py:7-10",
                "registry": "darksirens.population.pop_model_prior_parser / "
                            "get_fixed_population_params",
            },
        }

    def decode(self, coord_np):
        from darksirens.runtime_binding import _decode_theta

        jnp = self._jnp
        theta = self.embed(jnp.asarray(coord_np))
        cosmo, pop, _cat, _ang = _decode_theta(self.analysis, theta, z_depth=None)
        cos = [float(np.asarray(getattr(cosmo, n))) for n in ("H0", "Om0", "w0", "wa")]
        return cos + [float(x) for x in np.asarray(pop, dtype=np.float64)]

    # ------------------------------------------------------ diagnostics build
    def _build_diag_fns(self):
        import jax.numpy as jnp

        from darksirens.cosmology.distances import dL_of_z, threads_distance_table
        from darksirens.cosmology.distances import zgrid as distance_zgrid
        from darksirens.cosmology.volume import log_comoving_volume_prior
        from darksirens.likelihood.hierarchical import spectral_siren_log_likelihood
        from darksirens.likelihood.weights import log_sample_weight
        from darksirens.population import pop_model_parser
        from darksirens.runtime_binding import _decode_theta

        analysis, b, embed = self.analysis, self.bound, self.embed
        pop = analysis.population

        def diag_impl(theta, gw_pe, gw_sel):
            cosmo, pop_params, _cat, ang = _decode_theta(analysis, embed(theta), z_depth=None)
            return spectral_siren_log_likelihood(
                cosmo, pop_params, gw_pe, gw_sel, b.n_events, b.nsamp, b.n_draw,
                pop_model=pop.model_name, shared_beta=pop.shared_beta,
                shared_spin=pop.shared_spin, shared_gamma=pop.shared_gamma,
                angular_model=analysis.angular_model, angular_params=ang,
                sel_batch_size=b.sel_batch_size, pe_event_block=b.pe_event_block,
                selection_neff_soft_guard=b.selection_neff_soft_guard,
                max_likelihood_variance=b.max_likelihood_variance,
                return_diagnostics=True)

        @threads_distance_table()
        def diag_jit(theta, gw_pe, gw_sel, distance_table=None):
            return diag_impl(theta, gw_pe, gw_sel)

        # Per-sample masks: hierarchical.py:138-160 (support + finite weight),
        # event.py:39,55 (valid & prior_wt > 0), selection/gw.py:564-565.
        @threads_distance_table()
        def sample_masks(theta, gw, distance_table=None):
            cosmo, pop_params, _cat, _ang = _decode_theta(analysis, embed(theta), z_depth=None)
            log_p_pop = pop_model_parser(pop_model=pop.model_name, shared_beta=pop.shared_beta,
                                         shared_spin=pop.shared_spin,
                                         shared_gamma=pop.shared_gamma)
            dL_grid = dL_of_z(distance_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dL_grid[0], dL_grid[-1]
            support = (gw.dL >= lo) & (gw.dL <= hi)
            ldw = log_sample_weight(
                gw.m1det, gw.q, jnp.clip(gw.dL, lo, hi), gw.chieff, gw.pixels, gw.prior_wt,
                cosmo, None, pop_params, None, log_p_pop,
                lambda z, _p, _c: log_comoving_volume_prior(z, cosmo),
                spin=gw.spin, dL_grid=dL_grid)
            ldw = jnp.where(support & jnp.isfinite(ldw), ldw, -jnp.inf)
            structural = gw.valid & (gw.prior_wt > 0.0)
            final = structural & jnp.isfinite(ldw)
            return structural, support, final

        self._diag_impl, self._diag_jit, self._sample_masks = diag_impl, diag_jit, sample_masks
        self.diag_provenance = {
            "kind": "core_return_diagnostics",
            "function": ("darksirens.likelihood.hierarchical.spectral_siren_log_likelihood("
                         "..., return_diagnostics=True) with BoundAnalysis.__call__'s arguments"),
            "decoder": "darksirens.runtime_binding._decode_theta (private)",
            "execution": ("eager (same as the as-shipped kernel)" if self.jit_mode == "asis"
                          else "jit via core threads_distance_table (tables as arguments)"),
            "masks": ("rebuilt with core log_sample_weight + log_comoving_volume_prior, "
                      "transcribing hierarchical.py:138-160, event.py:39,55, "
                      "selection/gw.py:564-565"),
        }

    # ----------------------------------------------------------- diagnostics
    def diagnostics(self, coord_np):
        jnp = self._jnp
        theta = jnp.asarray(coord_np)
        b = self.bound
        if self.jit_mode == "asis":
            d = self._diag_impl(theta, b.gw_pe, b.gw_selection)
        else:
            d = self._diag_jit(theta, b.gw_pe, b.gw_selection)
        return {
            "diag_total_logL": np.asarray(d.log_likelihood),
            "event_log_evidence": np.asarray(d.event_log_evidence),
            "event_mc_variance": np.asarray(d.event_mc_variance),
            "log_mu": np.asarray(d.log_mu),
            "n_eff": np.asarray(d.n_eff),
            "selection_log_correction": np.asarray(d.selection_log_correction),
        }

    def masks(self, coord_np, chunk):
        jax, jnp = self._jax, self._jnp
        theta = jnp.asarray(coord_np)

        def run(gw, n):
            outs = []
            for s in range(0, n, chunk):
                e = min(n, s + chunk)
                sub = jax.tree_util.tree_map(lambda a: a[s:e], gw)
                outs.append([np.asarray(x) for x in self._sample_masks(theta, sub)])
            return [np.concatenate([o[i] for o in outs]) for i in range(3)]

        b = self.bound
        return run(b.gw_pe, int(b.gw_pe.dL.shape[0])), run(b.gw_selection, self.dims()["n_injections"])

    def mask_order_dL(self):
        """(PE dL, selection dL) in the order the masks are reported."""
        b = self.bound
        return (np.asarray(b.gw_pe.dL, dtype=np.float64),
                np.asarray(b.gw_selection.dL, dtype=np.float64)[: self.dims()["n_injections"]])

    # ----------------------------------------------------------- jit evidence
    def jit_evidence(self, coord_np):
        from bench_common import aot_report, jaxpr_const_report
        from darksirens.cosmology import distances as D

        jnp = self._jnp
        b = self.bound
        if self.jit_mode == "asis":
            return {
                "kernel": "eager BoundAnalysis (no whole-likelihood jit)",
                "note": ("eager dispatch: every primitive and every jitted leaf kernel is "
                         "compiled separately on first use; see timing.compile.first_call"),
            }
        table = D.distance_table()
        extras = tuple(res() for res, _ in D._AMBIENT_JIT_CHANNELS)
        args = (jnp.asarray(coord_np), b.gw_pe, b.gw_selection)
        kwargs = {"distance_table": table, "_ambient_extras": extras}
        data_arrays = {
            "gw_pe.m1det": b.gw_pe.m1det, "gw_pe.dL": b.gw_pe.dL,
            "gw_pe.prior_wt": b.gw_pe.prior_wt,
            "gw_sel.m1det": b.gw_selection.m1det, "gw_sel.dL": b.gw_selection.dL,
            "gw_sel.prior_wt": b.gw_selection.prior_wt,
            "distance_table": table,
        }
        for i, x in enumerate(extras):
            if hasattr(x, "shape"):
                data_arrays[f"ambient_channel_{i}"] = x
        rep = {"kernel": ("threads_distance_table-jitted BoundAnalysis.__call__"
                          "(theta, gw_pe, gw_sel, distance_table, _ambient_extras)"),
               "n_ambient_channels": len(extras)}
        rep["jaxpr"] = jaxpr_const_report(self._whole.jitted, args, kwargs, data_arrays)
        rep["aot"] = aot_report(self._whole.jitted, args, kwargs, self.counter)
        return rep

    def cleanup(self):
        return []

    def remove_save_dir(self):
        return None
