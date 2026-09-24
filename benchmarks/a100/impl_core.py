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

Dark sirens (``plan["universe"] == "dark"``): ``ds.model(..., catalog=
ds.load_catalog(CAT))`` (the incomplete conditional model, core's only dark
estimand), bound by ``bind_analysis`` exactly as ``ds.infer`` binds it. The
survey block is ALWAYS sampled in core (``src/darksirens/analysis.py:310-315``),
so a plan that fixes it is evaluated through the harness embedding (the fixed
survey values are inserted into the coordinate). In ``whole`` mode the compact
catalog and the observed-density cache are jit ARGUMENTS too. Diagnostics:
``dark_siren_log_likelihood(return_diagnostics=True)``; catalog-side terms from
``build_incomplete_catalog_prior_state`` / ``completion_curves`` /
``eval_incomplete_catalog_prior_state_vmap`` / ``eval_log_catalog_prior_state``.
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
                 save_dir, counter, catalog_path=None):
        if jit_mode not in ("whole", "asis"):
            raise ValueError("--jit must be whole or asis")
        self.plan = plan
        self.pe_path = pe_path
        self.sel_path = sel_path
        self.catalog_path = catalog_path
        self.dark = plan.get("universe", "spectral") == "dark"
        if self.dark and not catalog_path:
            raise ValueError("a dark-siren plan needs --catalog")
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
        if self.dark:
            # completeness=None = the incomplete conditional model (analysis.py:187-188)
            return ds.model(cosmology=cosmology, population=population,
                            catalog=self.catalog_store)
        return ds.model(cosmology=cosmology, population=population)

    def build(self):
        import jax
        import jax.numpy as jnp

        import darksirens as ds
        from darksirens.runtime_binding import bind_analysis, required_fit_columns

        p = self.plan
        t_cat = 0.0
        self.catalog_store = None
        if self.dark:
            tc = time.perf_counter()
            self.catalog_store = ds.load_catalog(self.catalog_path)
            t_cat = time.perf_counter() - tc
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
        # either fully sampled or fully fixed, src/darksirens/analysis.py:288-308)
        # and no survey fixing at all (the catalog block is always sampled,
        # analysis.py:310-315), so a plan sampling a strict subset of core's labels
        # is evaluated on core's plan with the other parameters inserted at the
        # plan's fixed values. The insertion is part of the kernel (inside the jit
        # for --jit whole, one eager scatter for --jit asis).
        self.adapter_info = None
        full_names = self.labels
        if full_names != list(p["sampled"]):
            missing = [n for n in p["sampled"] if n not in full_names]
            if missing:
                raise RuntimeError(f"plan samples {missing}, which core's plan {full_names} lacks")
            base = np.asarray([p["fixed"][n] if n in p["fixed"] else p["fiducials"][n]
                               for n in full_names], dtype=np.float64)
            idx = np.asarray([full_names.index(n) for n in p["sampled"]], dtype=np.int32)
            self._embed_base = jnp.asarray(base)
            self._embed_idx = jnp.asarray(idx)

            def embed(theta):
                return self._embed_base.at[self._embed_idx].set(theta)

            self.embed = embed
            reasons = []
            if p["sample_population"] not in ("all", "none"):
                reasons.append("core ds.Population cannot fix part of the population "
                               "(src/darksirens/analysis.py:288-308)")
            if self.dark and p.get("sample_survey", "none") == "none":
                reasons.append("core always samples the catalog block log10n0, delta, sigma_kde "
                               "(src/darksirens/analysis.py:310-315)")
            self.adapter_info = {
                "kind": "embed_sampled_into_full_plan",
                "reason": "; ".join(reasons) + ("; the harness evaluates core's BoundAnalysis with "
                                                "the non-sampled parameters inserted at the plan's "
                                                "fixed values"),
                "core_plan_labels": full_names,
                "sampled_indices_in_core_plan": idx.tolist(),
                "fixed_inserted": {n: float(base[i]) for i, n in enumerate(full_names)
                                   if n not in p["sampled"]},
            }
            self.gaps.append(f"{p['name']}: core cannot fix {', '.join(sorted(set(full_names) - set(p['sampled'])))} "
                             "publicly; evaluated through a harness embedding into core's plan")
        else:
            self.embed = lambda theta: theta

        from darksirens.cosmology.distances import threads_distance_table

        bound_ = bound
        embed_ = self.embed

        @threads_distance_table()
        def whole(theta, gw_pe, gw_sel, catalog=None, cache=None, distance_table=None):
            if catalog is None:
                b = dataclasses.replace(bound_, gw_pe=gw_pe, gw_selection=gw_sel)
            else:  # dark: the compact catalog and its cache are jit ARGUMENTS too
                b = dataclasses.replace(bound_, gw_pe=gw_pe, gw_selection=gw_sel,
                                        catalog=catalog, observed_density_cache=cache)
            return b(embed_(theta))

        self._whole = whole
        # t_load = catalog + PE + selection reads (the catalog is read before the model
        # is configured because ds.model takes the loaded store); t_build = bind only.
        self.timing.update(t_config_s=t1 - t0, t_load_s=(t2 - t1) + t_cat, t_build_s=t3 - t2,
                           t_model_s=t1 - t0, t_bind_s=t3 - t2, t_catalog_load_s=t_cat)
        self._build_diag_fns()
        self._jax, self._jnp = jax, jnp

    def operands_for_sync(self):
        from darksirens.cosmology.distances import distance_table

        if self.dark:
            return (self.bound.gw_pe, self.bound.gw_selection, self.bound.catalog,
                    self.bound.observed_density_cache, distance_table())
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
            "universe_model": "dark_sirens (IncompleteCatalogRedshift)" if self.dark else "spectral",
            "dark_settings": ({
                "estimand": "conditional (the only one core implements, "
                            "likelihood/hierarchical.py:337-364)",
                "kde": "full row, one-pass build-time offset (catalog/redshift.py:288-317)",
                "kernel_gl": "24-node CDF space, fixed (catalog/redshift.py:37-40,106-133)",
                "row_chunk": "auto: 512 above n_rows*n_max > 2**25 (catalog/redshift.py:46-49)",
                "prior_state": "rebuilt per proposal, PE and selection each "
                               "(likelihood/hierarchical.py:357-362)",
                "z_depth": b.z_depth,
                "catalog_sort_rows_by_z": True,
            } if self.dark else None),
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
            "catalog": (self._catalog_dims() if self.dark else {
                "present": b.catalog is not None,
                "zgals_shape": None if b.catalog is None else list(np.shape(b.catalog.zgals)),
                "note": "BoundAnalysis.catalog (None for a SpectralRedshift analysis)",
            }),
        }

    def _catalog_dims(self):
        import hashlib

        b, cs = self.bound, self.catalog_store
        full_ng = np.asarray(cs.catalog.ngals).astype(np.int64)
        ng = np.asarray(b.catalog.ngals).astype(np.int64)
        up = np.asarray(b.catalog.unique_pixels).astype(np.int64)
        z = np.asarray(b.catalog.zgals, dtype=np.float64)
        dz = np.asarray(b.catalog.dzgals, dtype=np.float64)
        w = np.asarray(b.catalog.wgals, dtype=np.float64)
        real = np.arange(z.shape[1])[None, :] < ng[:, None]
        pe_rows = np.asarray(b.gw_pe.pixels).astype(np.int64)
        n_inj = int(self.injections.n_injections)
        sel_rows = np.asarray(b.gw_selection.pixels).astype(np.int64)[:n_inj]
        empty = ng == 0

        def h(a):
            return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

        return {
            "present": True,
            "survey_path": self.catalog_path,
            "nside": int(cs.nside),
            "npix": int(12 * cs.nside * cs.nside),
            "apix_hex": float(np.asarray(b.catalog.apix)).hex(),
            "z_depth": b.z_depth,
            "n_rows": int(z.shape[0]),
            "n_max": int(z.shape[1]),
            "n_galaxies_full_catalog": int(full_ng.sum()),
            "n_pixels_occupied_full_catalog": int((full_ng > 0).sum()),
            "n_galaxies_rows": int(ng.sum()),
            "n_rows_occupied": int((~empty).sum()),
            "n_rows_empty": int(empty.sum()),
            "max_ngals_row": int(ng.max()) if ng.size else 0,
            "union_pixels_sha256": h(up),
            "row_ngals_sha256": h(ng),
            "real_zgals_sha256": h(z[real]),
            "real_dzgals_sha256": h(dz[real]),
            "real_wgals_sha256": h(w[real]),
            "pe_samples_on_empty_rows": int(empty[pe_rows].sum()),
            "pe_samples_on_empty_rows_per_event": empty[pe_rows].reshape(
                int(b.n_events), int(b.nsamp)).sum(axis=1).astype(int).tolist(),
            "sel_samples_on_empty_rows": int(empty[sel_rows].sum()),
            "pe_sample_rows_sha256": h(pe_rows),
            "sel_sample_rows_file_order_sha256": h(sel_rows),
            "row_semantics": ("row r = r-th sorted global RING pixel of the PE-union-selection "
                              "sample pixels (catalog/compact.py:78-104, runtime_binding.py:371-392); "
                              "galaxies z-sorted within rows at load (catalog/io.py:152-176)"),
        }

    # ----------------------------------------------------------------- kernel
    def timed_call(self, coord_np):
        jnp = self._jnp
        theta = jnp.asarray(coord_np)
        if self.jit_mode == "asis":
            return self.bound(self.embed(theta))
        if self.dark:
            return self._whole(theta, self.bound.gw_pe, self.bound.gw_selection,
                               self.bound.catalog, self.bound.observed_density_cache)
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
            "n_catalog": int(pl.n_catalog),
            "fixed_inserted": (self.adapter_info or {}).get("fixed_inserted"),
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
            "survey": self._survey_registry(),
        }

    def _survey_registry(self):
        """Catalog-block prior bounds and defaults straight from core."""
        from darksirens.analysis import _INCOMPLETE_CATALOG_PRIORS
        from darksirens.catalog.types import CatalogParameters

        block = {n: [float(lo), float(hi)] for n, lo, hi in _INCOMPLETE_CATALOG_PRIORS}
        d = CatalogParameters._field_defaults
        return {
            "bounds": {n: block[n] for n in ("log10n0", "delta", "sigma_kde")},
            "defaults": {n: float(d[n]) for n in ("delta", "sigma_kde")},
            "sources": {"bounds": "src/darksirens/analysis.py:17-21 (_INCOMPLETE_CATALOG_PRIORS)",
                        "defaults": "src/darksirens/catalog/types.py:14-26 (CatalogParameters)"},
        }

    def pow10(self, x):
        """``10.0 ** log10n0`` exactly as core's decoder spells it (eager jnp)."""
        jnp = self._jnp
        return float(10.0 ** jnp.asarray(x, dtype=jnp.float64))

    def decode(self, coord_np):
        from darksirens.runtime_binding import _decode_theta

        jnp = self._jnp
        theta = self.embed(jnp.asarray(coord_np))
        cosmo, pop, cat, _ang = _decode_theta(self.analysis, theta, z_depth=self.bound.z_depth)
        cos = [float(np.asarray(getattr(cosmo, n))) for n in ("H0", "Om0", "w0", "wa")]
        out = cos + [float(x) for x in np.asarray(pop, dtype=np.float64)]
        if self.dark:
            out += [float(np.asarray(cat.n0)), float(np.asarray(cat.delta)),
                    float(np.asarray(cat.sigma_kde))]
        return out

    # ------------------------------------------------------ diagnostics build
    def _build_diag_fns(self):
        import jax.numpy as jnp
        from jax import vmap

        from darksirens.cosmology.distances import dL_of_z, threads_distance_table
        from darksirens.cosmology.distances import zgrid as distance_zgrid
        from darksirens.cosmology.volume import log_comoving_volume_prior
        from darksirens.likelihood.hierarchical import (
            dark_siren_log_likelihood,
            spectral_siren_log_likelihood,
        )
        from darksirens.likelihood.weights import log_sample_weight
        from darksirens.population import pop_model_parser
        from darksirens.runtime_binding import _decode_theta

        analysis, b, embed = self.analysis, self.bound, self.embed
        pop = analysis.population
        dark = self.dark
        z_depth = b.z_depth

        def diag_impl(theta, gw_pe, gw_sel, catalog=None, cache=None):
            cosmo, pop_params, cat_params, ang = _decode_theta(analysis, embed(theta),
                                                               z_depth=z_depth)
            common = dict(
                pop_model=pop.model_name, shared_beta=pop.shared_beta,
                shared_spin=pop.shared_spin, shared_gamma=pop.shared_gamma,
                angular_model=analysis.angular_model, angular_params=ang,
                sel_batch_size=b.sel_batch_size, pe_event_block=b.pe_event_block,
                selection_neff_soft_guard=b.selection_neff_soft_guard,
                max_likelihood_variance=b.max_likelihood_variance,
                return_diagnostics=True)
            if dark:
                # BoundAnalysis.__call__'s argument list (runtime_binding.py:269-284)
                return dark_siren_log_likelihood(
                    cosmo, cat_params, pop_params, gw_pe, catalog, cache, gw_sel, catalog,
                    cache, b.n_events, b.nsamp, b.n_draw, **common)
            return spectral_siren_log_likelihood(
                cosmo, pop_params, gw_pe, gw_sel, b.n_events, b.nsamp, b.n_draw, **common)

        @threads_distance_table()
        def diag_jit(theta, gw_pe, gw_sel, catalog=None, cache=None, distance_table=None):
            return diag_impl(theta, gw_pe, gw_sel, catalog, cache)

        def _ctx(theta, catalog, cache):
            cosmo, pop_params, cat_params, _ang = _decode_theta(analysis, embed(theta),
                                                                z_depth=z_depth)
            log_p_pop = pop_model_parser(pop_model=pop.model_name, shared_beta=pop.shared_beta,
                                         shared_spin=pop.shared_spin,
                                         shared_gamma=pop.shared_gamma)
            dL_grid = dL_of_z(distance_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            ctx = {"cosmo": cosmo, "pop_params": pop_params, "cat_params": cat_params,
                   "log_p_pop": log_p_pop, "dL_grid": dL_grid,
                   "lo": dL_grid[0], "hi": dL_grid[-1]}
            if dark:
                from darksirens.catalog.models import (
                    build_incomplete_catalog_prior_state,
                    eval_incomplete_catalog_prior_state_vmap,
                )

                state = build_incomplete_catalog_prior_state(cosmo, cat_params, catalog, cache)
                ctx["state"] = state
                ctx["prior"] = (lambda z, pix, cat_:
                                eval_incomplete_catalog_prior_state_vmap(z, pix, state, cat_))
            else:
                ctx["prior"] = lambda z, _p, _c: log_comoving_volume_prior(z, cosmo)
            return ctx

        def _ldw(ctx, gw, prior_fn, catalog):
            lo, hi = ctx["lo"], ctx["hi"]
            support = (gw.dL >= lo) & (gw.dL <= hi)
            ldw = log_sample_weight(
                gw.m1det, gw.q, jnp.clip(gw.dL, lo, hi), gw.chieff, gw.pixels, gw.prior_wt,
                ctx["cosmo"], None, ctx["pop_params"], catalog, ctx["log_p_pop"], prior_fn,
                spin=gw.spin, dL_grid=ctx["dL_grid"])
            return jnp.where(support & jnp.isfinite(ldw), ldw, -jnp.inf), support

        # Per-sample masks: hierarchical.py:131-163 (support + finite weight),
        # event.py:39,55 (valid & prior_wt > 0), selection/gw.py:564-565.
        @threads_distance_table()
        def sample_masks(theta, gw, catalog=None, cache=None, distance_table=None):
            ctx = _ctx(theta, catalog, cache)
            ldw, support = _ldw(ctx, gw, ctx["prior"], catalog)
            structural = gw.valid & (gw.prior_wt > 0.0)
            final = structural & jnp.isfinite(ldw)
            return structural, support, final

        self._diag_impl, self._diag_jit, self._sample_masks = diag_impl, diag_jit, sample_masks
        self.diag_provenance = {
            "kind": "core_return_diagnostics",
            "function": ("darksirens.likelihood.hierarchical."
                         + ("dark_siren_log_likelihood" if dark else "spectral_siren_log_likelihood")
                         + "(..., return_diagnostics=True) with BoundAnalysis.__call__'s arguments"),
            "decoder": "darksirens.runtime_binding._decode_theta (private)",
            "execution": ("eager (same as the as-shipped kernel)" if self.jit_mode == "asis"
                          else "jit via core threads_distance_table (tables as arguments)"),
            "masks": ("rebuilt with core log_sample_weight + "
                      + ("build_incomplete_catalog_prior_state / "
                         "eval_incomplete_catalog_prior_state_vmap" if dark
                         else "log_comoving_volume_prior")
                      + ", transcribing hierarchical.py:131-163, event.py:39,55, "
                        "selection/gw.py:564-565"),
        }
        if not dark:
            return
        self.diag_provenance["catalog_terms"] = (
            "per-row: build_incomplete_catalog_prior_state log_Nobs / log_Z / kernels.row_empty / "
            "kernels.log_depth_mass and completion_curves N_miss / f (catalog/models.py:95-120, "
            "catalog/completeness.py:290-300); per-sample: eval_incomplete_catalog_prior_state_vmap "
            "and its two branches log_Nobs[row] + log p_cat - log_Z[row] (catalog hosts) and "
            "log dN_miss - log_Z[row] (missing hosts), transcribing catalog/models.py:123-145")

        from darksirens.catalog.completeness import completion_curves
        from darksirens.catalog.models import _grid_bracket, _interp_row
        from darksirens.catalog.redshift import eval_log_catalog_prior_state

        def _branches(state):
            def cat_branch(z, pix, catalog):
                lp = vmap(lambda zi, ri: eval_log_catalog_prior_state(zi, ri, state.kernels,
                                                                      catalog))(z, pix)
                lp = jnp.nan_to_num(lp, nan=-jnp.inf, neginf=-jnp.inf)
                return state.log_Nobs[pix] + lp - state.log_Z[pix]

            def miss_branch(z, pix, catalog):
                idx, t = _grid_bracket(z)
                miss = _interp_row(state.dN_miss[pix, idx], state.dN_miss[pix, idx + 1], t)
                log_miss = jnp.where(miss > 0.0, jnp.log(jnp.maximum(miss, 1.0e-300)), -jnp.inf)
                return log_miss - state.log_Z[pix]
            return cat_branch, miss_branch

        @threads_distance_table()
        def catalog_rows(theta, catalog, cache, distance_table=None):
            ctx = _ctx(theta, catalog, cache)
            st = ctx["state"]
            curves = completion_curves(ctx["cosmo"], ctx["cat_params"], catalog, cache)
            return {"log_Nobs": st.log_Nobs, "log_Z": st.log_Z, "N_miss": curves.N_miss,
                    "f": curves.f, "row_empty": st.kernels.row_empty,
                    "log_depth_mass": jnp.broadcast_to(st.kernels.log_depth_mass, st.log_Z.shape)}

        @threads_distance_table()
        def sample_terms(theta, gw, catalog, cache, distance_table=None):
            ctx = _ctx(theta, catalog, cache)
            cat_b, miss_b = _branches(ctx["state"])
            cap = {}

            def capture(z, pix, cat_):
                v = ctx["prior"](z, pix, cat_)
                cap["lp"] = v
                return v

            ldw_full, support = _ldw(ctx, gw, capture, catalog)
            ldw_cat, _ = _ldw(ctx, gw, cat_b, catalog)
            ldw_miss, _ = _ldw(ctx, gw, miss_b, catalog)
            structural = gw.valid & (gw.prior_wt > 0.0)
            final = structural & jnp.isfinite(ldw_full)

            def masked(x):
                return jnp.where(structural & jnp.isfinite(x), x, -jnp.inf)

            return {"structural": structural, "support": support, "final": final,
                    "log_prior": cap["lp"], "ldw": masked(ldw_full),
                    "ldw_cat": masked(ldw_cat), "ldw_miss": masked(ldw_miss)}

        self._catalog_rows_fn = catalog_rows
        self._sample_terms_fn = sample_terms

    # ----------------------------------------------------------- diagnostics
    def diagnostics(self, coord_np):
        jnp = self._jnp
        theta = jnp.asarray(coord_np)
        b = self.bound
        extra = (b.catalog, b.observed_density_cache) if self.dark else ()
        if self.jit_mode == "asis":
            d = self._diag_impl(theta, b.gw_pe, b.gw_selection, *extra)
        else:
            d = self._diag_jit(theta, b.gw_pe, b.gw_selection, *extra)
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
        b = self.bound
        extra = (b.catalog, b.observed_density_cache) if self.dark else ()

        def run(gw, n):
            outs = []
            for s in range(0, n, chunk):
                e = min(n, s + chunk)
                sub = jax.tree_util.tree_map(lambda a: a[s:e], gw)
                outs.append([np.asarray(x) for x in self._sample_masks(theta, sub, *extra)])
            return [np.concatenate([o[i] for o in outs]) for i in range(3)]

        return run(b.gw_pe, int(b.gw_pe.dL.shape[0])), run(b.gw_selection, self.dims()["n_injections"])

    def sample_terms(self, coord_np, chunk):
        """Per-sample masks, log p(z|row) and the branch weights, in FILE order (dark only)."""
        jax, jnp = self._jax, self._jnp
        theta = jnp.asarray(coord_np)
        b = self.bound

        def run(gw, n):
            outs = []
            for s in range(0, n, chunk):
                e = min(n, s + chunk)
                sub = jax.tree_util.tree_map(lambda a: a[s:e], gw)
                d = self._sample_terms_fn(theta, sub, b.catalog, b.observed_density_cache)
                outs.append({k: np.asarray(v) for k, v in d.items()})
            return {k: np.concatenate([o[k] for o in outs]) for k in outs[0]}

        return (run(b.gw_pe, int(b.gw_pe.dL.shape[0])),
                run(b.gw_selection, int(self.injections.n_injections)))

    def catalog_rows(self, coord_np):
        jnp = self._jnp
        b = self.bound
        d = self._catalog_rows_fn(jnp.asarray(coord_np), b.catalog, b.observed_density_cache)
        return {k: np.asarray(v) for k, v in d.items()}

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
        if self.dark:
            args = args + (b.catalog, b.observed_density_cache)
        kwargs = {"distance_table": table, "_ambient_extras": extras}
        data_arrays = {
            "gw_pe.m1det": b.gw_pe.m1det, "gw_pe.dL": b.gw_pe.dL,
            "gw_pe.prior_wt": b.gw_pe.prior_wt,
            "gw_sel.m1det": b.gw_selection.m1det, "gw_sel.dL": b.gw_selection.dL,
            "gw_sel.prior_wt": b.gw_selection.prior_wt,
            "distance_table": table,
        }
        if self.dark:
            data_arrays.update({
                "catalog.zgals": b.catalog.zgals, "catalog.dzgals": b.catalog.dzgals,
                "catalog.wgals": b.catalog.wgals,
                "cache.dN_obs_kde": b.observed_density_cache.dN_obs_kde,
            })
        for i, x in enumerate(extras):
            if hasattr(x, "shape"):
                data_arrays[f"ambient_channel_{i}"] = x
        rep = {"kernel": ("threads_distance_table-jitted BoundAnalysis.__call__"
                          "(theta, gw_pe, gw_sel, [catalog, cache,] distance_table, "
                          "_ambient_extras)"),
               "n_ambient_channels": len(extras)}
        rep["jaxpr"] = jaxpr_const_report(self._whole.jitted, args, kwargs, data_arrays)
        rep["aot"] = aot_report(self._whole.jitted, args, kwargs, self.counter)
        return rep

    def cleanup(self):
        return []

    def remove_save_dir(self):
        return None
