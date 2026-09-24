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

Dark sirens (``plan["universe"] == "dark"``): ``--universe_model dark_sirens``
with the knobs in ``LEGACY_DARK_SETTINGS`` (conditional sky weighting, full-row
KDE, per-proposal redshift prior, ...), chosen so the legacy kernel evaluates
core's semantics; the re-assembly follows ``core.py:1030-1062`` with the
factory's own prepared ``EMCatalog`` views (including any build-time H0 kernel
pin) and its empty-row routing plans, as ``tools/probe_catalog_likelihood.py::
_legacy`` does for the conditional prior. Catalog-side diagnostics (per-row
N_obs, N_miss, f, log Z, empty rows; per-sample log p(z|pix); per-event
catalog / missing-host branch terms) come from legacy's own
``prepare_redshift_prior_state`` / ``completion_curves`` /
``eval_redshift_prior_with_state`` / ``eval_log_catalog_prior_state``.
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

#: The legacy CLI knobs that core does not have, set to the value that makes the
#: legacy kernel evaluate core's dark-siren semantics (core is conditional-only,
#: full-row, per-proposal, fixed 24-node CDF quadrature, auto row chunking).
#: Every value is passed explicitly and recorded in ``config.dark_settings``.
LEGACY_DARK_SETTINGS = {
    "--universe_model": ("dark_sirens", "core ds.model(catalog=...) = IncompleteCatalogRedshift "
                         "(src/darksirens/analysis.py:187-188)"),
    "--catalog_sky_weighting": ("conditional", "CLI default resolves to field "
                                "(cli/inference.py:1451-1476); core implements only the "
                                "conditional estimand (likelihood/hierarchical.py:337-364)"),
    "--kde_window": ("0", "0 = full-row KDE (factory.py:1544-1566 returns None; "
                     "redshift/catalog.py:224 configure_catalog_kde_window(size=None)); "
                     "core evaluates full rows (catalog/redshift.py:288-317)"),
    "--freeze_redshift_prior": ("false", "per-proposal prior evaluation; the default true "
                                "freezes it at build time for population-only plans "
                                "(cli/inference.py:1837-1846, factory.py:1613-1762); core has "
                                "no frozen prior"),
    "--row_chunk": ("auto", "legacy default: chunk 512 above n_rows*n_max > 2**25 "
                    "(redshift/catalog.py:165-191) = core's fixed rule "
                    "(catalog/redshift.py:46-49,198-223)"),
    "--kernel_gl_nodes": ("24", "legacy default (redshift/catalog.py:105) = core _GL_NODES 24 "
                          "(catalog/redshift.py:37)"),
    "--kernel_gl_domain": ("cdf", "legacy default (redshift/catalog.py:106) = core's CDF-space "
                           "rule (catalog/redshift.py:106-133)"),
    "--drop_full_catalog": ("false", "keeps the flat union path: ONE PE-union-selection compact "
                            "table (likelihood/catalog_views.py:276-340), as core's "
                            "compact_pe_selection_catalog (catalog/compact.py:78)"),
    "--c_mode": ("per_pixel", "the per-row count-ratio completeness core reconstructs "
                 "(catalog/completeness.py)"),
    "--use_lss": ("false", "core has no LSS; b_miss is then inert (inference/prior.py:223-272)"),
}
#: Legacy dark-siren build behaviour with NO CLI knob. Each is recorded per
#: record (config.dark_settings) and discussed in the H2 report.
LEGACY_DARK_NO_KNOB = {
    "h0_kernel_pin": ("installed whenever none of Om0, w0, wa, delta, sigma_kde is sampled "
                      "(factory.py:1017-1137): the per-galaxy quadrature is evaluated once at "
                      "H0_ref = 67.74 and shifted by 3 ln(H0/H0_ref) per proposal; analytically "
                      "exact, arithmetically different from core's per-proposal quadrature; "
                      "self-verified in the graph to 1e-9 (redshift/catalog.py:1006)"),
    "empty_row_routing": ("per side, whenever that side is evaluated as ONE block and >= 10% of "
                          "its samples sit on galaxy-free rows (factory.py:1172-1503): the "
                          "empty-row samples skip the KDE (log p_cat = -inf substituted); "
                          "disabled on a side by an explicit sel_batch_size / pe_event_block < "
                          "n_events"),
    "injection_pixel_sort": ("injections stably sorted by compact catalog row "
                             "(factory.py:1140-1163, :2687-2693); masks are reported in file "
                             "order"),
    "redshift_prior_state_sharing": ("PE and selection share one prepared state on the union "
                                     "path (core.py:1004-1040); core builds the same state twice "
                                     "from the same catalog"),
}


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


def _is_dark(plan):
    return plan.get("universe", "spectral") == "dark"


def legacy_cli_args(plan, pe_path, sel_path, save_path, sel_batch, pe_block, seed,
                    catalog_path=None):
    """The exact darksirens_inference argument vector that configures ``plan``."""
    dark = _is_dark(plan)
    argv = [
        "--gw_path", pe_path,
        "--gwselection_path", sel_path,
        "--universe_model", "dark_sirens" if dark else "spectral_sirens",
        "--pop_model", plan["population_model"],
        "--sampler", "dynesty",
        "--save_path", save_path,
        "--seed", str(int(seed)),
    ]
    if dark:
        if not catalog_path:
            raise ValueError("a dark-siren plan needs --catalog")
        argv += ["--survey_path", catalog_path]
        for flag, (value, _why) in LEGACY_DARK_SETTINGS.items():
            if flag == "--universe_model":
                continue
            argv += [flag, value]
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
    if dark and plan.get("sample_survey", "none") == "none":
        # Survey block fixed INDIVIDUALLY at the plan's values (fixture density,
        # shared defaults): --fix_survey true would pin the registry fiducials
        # (log10n0 = -2, core/constants.py SURVEY_PARAMS_FID_BY_NAME) instead.
        for lab in plan["survey_labels"]:
            fixed_values[lab] = plan["fixed"][lab]
    if fixed_values:
        argv += ["--fixed_parameter_values", json.dumps(fixed_values)]
    return argv


class LegacyAdapter:
    impl = IMPL

    def __init__(self, plan, pe_path, sel_path, *, sel_batch, pe_block, jit_mode, seed,
                 save_dir, counter, catalog_path=None):
        self.plan = plan
        self.pe_path = pe_path
        self.sel_path = sel_path
        self.catalog_path = catalog_path
        self.dark = _is_dark(plan)
        self.jit_mode = jit_mode
        self.counter = counter
        self.gaps = []
        self.timing = {}
        self.save_dir = save_dir
        self.build_warnings = []
        self.cli_argv = legacy_cli_args(plan, pe_path, sel_path, save_dir, sel_batch, pe_block, seed,
                                        catalog_path=catalog_path)
        self.requested_blocks = {"sel_batch_size": sel_batch, "pe_event_block": pe_block}
        self.cli_log = ""

    # ------------------------------------------------------------------ build
    def build(self):
        from darksirens.cli import inference as cli

        import warnings

        os.makedirs(self.save_dir, exist_ok=True)
        sink = io.StringIO()
        t0 = time.perf_counter()
        with contextlib.redirect_stdout(sink), warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
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
        # Only warnings raised by the darksirens package (third-party deprecation
        # noise, e.g. pyparsing via matplotlib, is dropped).
        self.build_warnings = [
            {"category": w.category.__name__, "message": str(w.message),
             "filename": w.filename, "lineno": w.lineno} for w in caught
            if "darksirens" in str(w.filename or "")]
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
        self.universe_model = str(opts.universe_model)
        self._injection_order()
        if self.dark:
            self._dark_build_checks()
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

    def _dark_build_checks(self):
        """Record (and require) the dark-siren build state the parity target needs."""
        import hashlib

        from darksirens.redshift import catalog as rcat

        lk, opts = self.likelihood, self.opts
        if lk.kde_window is not None:
            raise RuntimeError(f"legacy KDE window resolved to {lk.kde_window}, not the full row")
        if lk.frozen_redshift_prior:
            raise RuntimeError("legacy froze the redshift prior; the plan needs per-proposal evaluation")
        if getattr(opts, "catalog_sky_weighting", None) != "conditional":
            raise RuntimeError(f"catalog_sky_weighting={opts.catalog_sky_weighting!r}, not conditional")
        em = self.em_pe
        if not (em.zgals is self.em_sel.zgals or np.array_equal(np.asarray(em.zgals),
                                                               np.asarray(self.em_sel.zgals))):
            raise RuntimeError("legacy PE and selection catalog views differ (no union path)")
        pin = getattr(em, "pinned_kernels", None)
        routing = lk.empty_row_routing

        def _side(plan_):
            if plan_ is None:
                return None
            tiers = tuple(plan_.tiers or ())
            n_occ = (sum(int(t.idx.shape[0]) for t in tiers) if tiers
                     else int(plan_.idx_occ.shape[0]))
            return {"n_occupied": n_occ, "n_empty": int(plan_.idx_empty.shape[0]),
                    "n_width_tiers": len(tiers), "tier_caps": [int(t.cap) for t in tiers]}

        routing_info = {"active": bool(routing),
                        "pe": _side(routing[0][0]) if routing else None,
                        "sel": _side(routing[0][1]) if routing else None}
        pin_info = {"active": pin is not None}
        if pin is not None:
            pin_info.update(H0_ref=float(np.asarray(pin.H0_ref)),
                            probe_rows=np.asarray(pin.probe_rows).tolist(),
                            tol=float(rcat.KERNEL_PIN_TOL),
                            source="likelihood/factory.py:1017-1137, redshift/catalog.py:995-1360")
        share = None
        try:
            from darksirens.likelihood.core import redshift_prior_state_sharing

            share = [bool(x) for x in redshift_prior_state_sharing(
                self.universe_model, (self.em_pe,), (self.em_sel,))]
        except Exception as exc:  # pragma: no cover
            share = f"{type(exc).__name__}: {exc}"
        self.dark_settings = {
            "cli_knobs": {k: {"value": v, "why": why} for k, (v, why) in LEGACY_DARK_SETTINGS.items()},
            "no_knob_behaviour": {k: v for k, v in LEGACY_DARK_NO_KNOB.items()},
            "resolved": {
                "universe_model": self.universe_model,
                "catalog_sky_weighting": opts.catalog_sky_weighting,
                "kde_window_opt": getattr(opts, "kde_window", None),
                "kde_window_resolved": lk.kde_window,
                "kde_window_module": rcat._KDE_WINDOW_SIZE,
                "freeze_redshift_prior_opt": bool(getattr(opts, "freeze_redshift_prior", True)),
                "frozen_redshift_prior": bool(lk.frozen_redshift_prior),
                "row_chunk_opt": getattr(opts, "row_chunk", None),
                "row_chunk_module": rcat._ROW_CHUNK_MODE,
                "row_chunk_threshold": rcat._ROW_CHUNK_AUTO_THRESHOLD,
                "row_chunk_size": rcat._ROW_CHUNK_SIZE,
                "kernel_gl": {"nodes": rcat._GL_NODES, "domain": rcat._GL_DOMAIN,
                              "nsigma": rcat._GL_NSIGMA},
                "c_mode": getattr(opts, "c_mode", None),
                "use_LSS": bool(getattr(opts, "use_LSS", False)),
                "drop_full_catalog": bool(getattr(opts, "drop_full_catalog", False)),
                "survey_z_depth_opt": getattr(opts, "survey_z_depth", None),
                "resolved_survey_z_depths": list(getattr(opts, "resolved_survey_z_depths", None) or []),
                "redshift_prior_barrier": getattr(opts, "redshift_prior_barrier", None),
                "materialize_redshift_prior_state": None,
                "share_prior_state_by_catalog": share,
                "kernel_pin": pin_info,
                "empty_row_routing": routing_info,
            },
        }
        from darksirens.likelihood.factory import _resolve_redshift_prior_materialization

        self.dark_settings["resolved"]["materialize_redshift_prior_state"] = bool(
            _resolve_redshift_prior_materialization(opts))

        # ---- catalog dimensions (union compact rows = kernel rows) ------------------
        data = self.data
        full_ng = np.asarray(data["ngals_catalog"]).astype(np.int64)
        ng = np.asarray(em.ngals).astype(np.int64)
        up = np.asarray(em.unique_pixels).astype(np.int64)
        z = np.asarray(em.zgals, dtype=np.float64)
        dz = np.asarray(em.dzgals, dtype=np.float64)
        w = np.asarray(em.wgals, dtype=np.float64)
        real = np.arange(z.shape[1])[None, :] < ng[:, None]
        pe_rows = np.asarray(self.gw_pe.pixels).astype(np.int64)
        sel_rows_internal = np.asarray(self.gw_sel.pixels).astype(np.int64)[: self.n_injections]
        sel_rows = np.empty_like(sel_rows_internal)
        sel_rows[self.sel_order] = sel_rows_internal
        empty = ng == 0

        def h(a):
            return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

        nside = int(data["nside"])
        self.catalog_dims = {
            "present": True,
            "survey_path": self.catalog_path,
            "nside": nside,
            "npix": int(12 * nside * nside),
            "apix_hex": float(np.asarray(em.apix)).hex(),
            "z_depth": (self.dark_settings["resolved"]["resolved_survey_z_depths"] or [None])[0],
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
                self.n_events, self.nsamp).sum(axis=1).astype(int).tolist(),
            "sel_samples_on_empty_rows": int(empty[sel_rows].sum()),
            "pe_sample_rows_sha256": h(pe_rows),
            "sel_sample_rows_file_order_sha256": h(sel_rows),
            "row_semantics": ("row r = r-th sorted global HEALPix pixel of the PE-union-selection "
                              "sample pixels (likelihood/catalog_views.py:318-340); galaxies z-sorted "
                              "within rows at load (catalogs/io.py:488)"),
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
            "universe_model": self.universe_model,
            "dark_settings": getattr(self, "dark_settings", None),
            "build_warnings": self.build_warnings,
        }

    def dims(self):
        return {
            "n_events": self.n_events,
            "nsamp": self.nsamp,
            "n_pe_samples": int(self.gw_pe.dL.shape[0]),
            "n_injections": self.n_injections,
            "n_injections_padded": int(self.gw_sel.dL.shape[0]),
            "ndraw": self.ndraw,
            "catalog": (dict(self.catalog_dims, n_catalogs=int(getattr(self.opts, "n_catalogs", 1)))
                        if self.dark else {
                "present": bool(getattr(self.opts, "survey_path", None)),
                "survey_path": getattr(self.opts, "survey_path", None),
                "n_catalogs": int(getattr(self.opts, "n_catalogs", 1)),
                "em_catalog_zgals_shape": list(np.shape(self.em_pe.zgals)),
                "note": ("spectral_sirens reads no galaxy catalog; legacy still threads a "
                         "placeholder EMCatalog through the kernel"),
            }),
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
            "fixed_parameter_values": dict(self.fixed_parameter_values),
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
            "survey": self._survey_registry(),
        }

    def _survey_registry(self):
        """Survey-block prior bounds and shared defaults straight from the legacy registry."""
        from darksirens.core.constants import SURVEY_PARAMS_FID_BY_NAME
        from darksirens.inference.prior import _SURVEY_BLOCK

        block = {spec.label: [float(spec.lower), float(spec.upper)] for spec in _SURVEY_BLOCK}
        return {
            "bounds": {n: block[n] for n in ("log10n0", "delta", "sigma_kde")},
            "defaults": {n: float(SURVEY_PARAMS_FID_BY_NAME[n]) for n in ("delta", "sigma_kde")},
            "registry_log10n0_fiducial": float(SURVEY_PARAMS_FID_BY_NAME["log10n0"]),
            "sources": {"bounds": "darksirens/inference/prior.py:290-297 (_SURVEY_BLOCK)",
                        "defaults": "darksirens/core/constants.py SURVEY_PARAMS_FID_BY_NAME"},
        }

    def pow10(self, x):
        """``10.0 ** log10n0`` exactly as the legacy decoder spells it (eager jnp)."""
        import jax.numpy as jnp

        return float(10.0 ** jnp.asarray(x, dtype=jnp.float64))

    def decode(self, coord_np):
        """Full (H0, Om0, w0, wa, population...) vector the kernel will see."""
        import jax.numpy as jnp

        cosmo, survey, pop, _sky, _marks = self.decoder.decode(jnp.asarray(coord_np))
        cos = [float(np.asarray(getattr(cosmo, n))) for n in ("H0", "Om0", "w0", "wa")]
        out = cos + [float(x) for x in np.asarray(pop, dtype=np.float64)]
        if self.dark:
            out += [float(np.asarray(survey.n0)), float(np.asarray(survey.delta)),
                    float(np.asarray(survey.sigma_kde))]
        return out

    # ------------------------------------------------------ diagnostics build
    def _build_diag_fns(self):
        import jax
        import jax.numpy as jnp
        from jax import lax, vmap

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
        dark = self.dark
        self.decoder = build_parameter_decoder(
            opts, self.pspace.pop_params_fid,
            fixed_parameter_values=self.fixed_parameter_values,
            wl_params=self.data.get("wl_params"))
        dec = self.decoder
        pe_model = self.universe_model
        sel_model = selection_prior_model(self.universe_model)
        materialize = _resolve_redshift_prior_materialization(opts)
        sky_weighting = getattr(opts, "catalog_sky_weighting", "conditional")
        share = redshift_prior_state_sharing(self.universe_model, (self.em_pe,), (self.em_sel,))
        share0 = bool(share[0]) if share else False
        # The factory's own empty-row routing plans (dark_sirens only); None per
        # side when inadmissible. ``eval_redshift_prior_with_state`` applies a plan
        # only to the full sample vector it was built for (prior.py:851-874).
        routing = self.likelihood.empty_row_routing if dark else ()
        routing_pe = routing[0][0] if routing else None
        routing_sel = routing[0][1] if routing else None
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
            "universe_model": pe_model,
            "selection_prior_model": sel_model,
            "share_prior_state": share0,
            "materialize_redshift_prior_state": bool(materialize),
            "catalog_sky_weighting": sky_weighting,
            "empty_row_routing_passed": {"pe": routing_pe is not None, "sel": routing_sel is not None},
            "jit": "legacy darksirens.utils.cosmology.threads_distance_table (table as argument)",
        }
        if dark:
            self.diag_provenance["catalog_terms"] = (
                "per-row: prepare_redshift_prior_state('dark_sirens') log_Nobs / log_Z / "
                "kernels.row_empty / kernels.log_depth_mass and completion_curves N_miss / f "
                "(redshift/prior.py:395-713, redshift/completion.py:2050); per-sample: "
                "eval_redshift_prior_with_state (unrouted, chunked) and its two branches "
                "log_Nobs[pix] + log p_cat - log_Z[pix] (catalog hosts) and log dN_miss - log_Z[pix] "
                "(missing hosts), transcribing _eval_dark_scalar (prior.py:914-937)")

        def _states(coord, em_pe, em_sel):
            cosmo, survey, pop_params, _sky, _marks = dec.decode(coord)
            st_u = prepare_redshift_prior_state(
                pe_model, cosmo, survey, em_pe, mark_model="none", mark_params=None,
                mark_names=(), materialize_state=materialize,
                catalog_sky_weighting=sky_weighting, kde_window=None)
            st_s = st_u if share0 else prepare_redshift_prior_state(
                sel_model, cosmo, survey, em_sel, mark_model="none", mark_params=None,
                mark_names=(), materialize_state=materialize,
                catalog_sky_weighting=sky_weighting, kde_window=None)
            return cosmo, survey, pop_params, st_u, st_s

        def _weight_fns(coord, em_pe, em_sel, rt_pe=None, rt_sel=None):
            cosmo, survey, pop_params, st_u, st_s = _states(coord, em_pe, em_sel)
            log_p_pop = pop_model_parser(pop_model=pop_model, **kw_pop)
            dL_grid = dL_of_z(cosmo_zgrid, cosmo.H0, cosmo.Om0, cosmo.w0, cosmo.wa)
            lo, hi = dL_grid[0], dL_grid[-1]

            def prior_pe(z, pix, catalogs):
                return eval_redshift_prior_with_state(
                    pe_model, st_u, z, pix, cosmo, survey, catalogs[0],
                    catalog_sky_weighting=sky_weighting, empty_routing=rt_pe)

            def prior_sel(z, pix, catalogs):
                return eval_redshift_prior_with_state(
                    sel_model, st_s, z, pix, cosmo, survey, catalogs[0],
                    catalog_sky_weighting=sky_weighting, empty_routing=rt_sel)

            def make(prior_fn):
                def fn(m1det, q, dL, chieff, pix, prior_wt, catalogs, spin=None):
                    supported = (dL >= lo) & (dL <= hi)
                    dL_c = jnp.clip(dL, lo, hi)
                    ldw = log_sample_weight(m1det, q, dL_c, chieff, pix, prior_wt, cosmo, survey,
                                            pop_params, catalogs, log_p_pop, prior_fn,
                                            spin=spin, dL_grid=dL_grid)
                    return jnp.where(supported & jnp.isfinite(ldw), ldw, -jnp.inf)
                return fn

            ctx = {"cosmo": cosmo, "survey": survey, "pop_params": pop_params,
                   "st_u": st_u, "st_s": st_s, "log_p_pop": log_p_pop, "dL_grid": dL_grid,
                   "prior_pe": prior_pe, "prior_sel": prior_sel}
            return make(prior_pe), make(prior_sel), (lo, hi), ctx

        @threads_distance_table()
        def diag(coord, gw_pe, em_pe, gw_sel, em_sel, rt_pe, rt_sel, distance_table=None):
            w_pe, w_sel, _, _ = _weight_fns(coord, em_pe, em_sel, rt_pe, rt_sel)
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
                w_pe, w_sel, (lo, hi), _ = _weight_fns(coord, em_pe, em_sel)
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
        self._routing = (routing_pe, routing_sel)
        self._sample_masks = {False: _make_masks(False), True: _make_masks(True)}
        self._jnp = jnp
        if not dark:
            return

        # ---- dark-siren catalog-side diagnostics (untimed) ------------------------
        from darksirens.redshift.catalog import eval_log_catalog_prior_state
        from darksirens.redshift.completion import completion_curves
        from darksirens.redshift.prior import _grid_bracket, _interp_row

        def _branches(state):
            def cat_branch(z, pix, catalogs):
                em = catalogs[0]
                lp = vmap(lambda zi, pi: eval_log_catalog_prior_state(zi, pi, state.kernels, em))(z, pix)
                lp = jnp.nan_to_num(lp, nan=-jnp.inf, neginf=-jnp.inf)
                return state.log_Nobs[pix] + lp - state.log_Z[pix]

            def miss_branch(z, pix, catalogs):
                idx, t = _grid_bracket(z)
                miss = _interp_row(state.dN_miss[pix, idx], state.dN_miss[pix, idx + 1], t)
                log_miss = jnp.where(miss > 0.0, jnp.log(jnp.maximum(miss, 1e-300)), -jnp.inf)
                return log_miss - state.log_Z[pix]
            return cat_branch, miss_branch

        @threads_distance_table()
        def catalog_rows(coord, em_pe, em_sel, distance_table=None):
            cosmo, survey, _pop, st_u, _st_s = _states(coord, em_pe, em_sel)
            curves = completion_curves(cosmo, survey, em_pe)
            return {"log_Nobs": st_u.log_Nobs, "log_Z": st_u.log_Z, "N_miss": curves.N_miss,
                    "f": curves.f, "row_empty": st_u.kernels.row_empty,
                    "log_depth_mass": jnp.broadcast_to(st_u.kernels.log_depth_mass,
                                                       st_u.log_Z.shape)}

        def _make_terms(is_selection):
            @threads_distance_table()
            def sample_terms(coord, gw, em_pe, em_sel, distance_table=None):
                _w_pe, _w_sel, (lo, hi), ctx = _weight_fns(coord, em_pe, em_sel)
                cat = (em_sel,) if is_selection else (em_pe,)
                state = ctx["st_s"] if is_selection else ctx["st_u"]
                full_prior = ctx["prior_sel"] if is_selection else ctx["prior_pe"]
                cat_b, miss_b = _branches(state)
                cap = {}

                def capture(z, pix, catalogs):
                    v = full_prior(z, pix, catalogs)
                    cap["lp"] = v
                    return v

                def ldw_with(prior_fn):
                    supported = (gw.dL >= lo) & (gw.dL <= hi)
                    dL_c = jnp.clip(gw.dL, lo, hi)
                    ldw = log_sample_weight(gw.m1det, gw.q, dL_c, gw.chieff, gw.pixels,
                                            gw.prior_wt, ctx["cosmo"], ctx["survey"],
                                            ctx["pop_params"], cat, ctx["log_p_pop"], prior_fn,
                                            spin=gw.spin, dL_grid=ctx["dL_grid"])
                    return jnp.where(supported & jnp.isfinite(ldw), ldw, -jnp.inf)

                ldw_full = ldw_with(capture)
                ldw_cat = ldw_with(cat_b)
                ldw_miss = ldw_with(miss_b)
                structural = gw.valid & (gw.prior_wt > 0.0)
                support = (gw.dL >= lo) & (gw.dL <= hi)
                final = structural & jnp.isfinite(ldw_full)

                def masked(x):
                    return jnp.where(structural & jnp.isfinite(x), x, -jnp.inf)

                return {"structural": structural, "support": support, "final": final,
                        "log_prior": cap["lp"], "ldw": masked(ldw_full),
                        "ldw_cat": masked(ldw_cat), "ldw_miss": masked(ldw_miss)}
            return sample_terms

        self._catalog_rows = catalog_rows
        self._sample_terms = {False: _make_terms(False), True: _make_terms(True)}

    # ----------------------------------------------------------- diagnostics
    def diagnostics(self, coord_np):
        jnp = self._jnp
        rt_pe, rt_sel = self._routing
        out = self._diag(jnp.asarray(coord_np), self.gw_pe, self.em_pe, self.gw_sel, self.em_sel,
                         rt_pe, rt_sel)
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

    def sample_terms(self, coord_np, chunk):
        """Per-sample masks, log p(z|pix) and the branch weights, in FILE order (dark only)."""
        import jax

        jnp = self._jnp
        coord = jnp.asarray(coord_np)

        def run(gw, n, is_sel):
            outs = []
            for s in range(0, n, chunk):
                e = min(n, s + chunk)
                sub = jax.tree_util.tree_map(lambda a: a[s:e], gw)
                d = self._sample_terms[is_sel](coord, sub, self.em_pe, self.em_sel)
                outs.append({k: np.asarray(v) for k, v in d.items()})
            return {k: np.concatenate([o[k] for o in outs]) for k in outs[0]}

        pe = run(self.gw_pe, int(self.gw_pe.dL.shape[0]), False)
        sel_internal = run(self.gw_sel, self.n_injections, True)
        sel = {}
        for k, m in sel_internal.items():
            f = np.empty_like(m)
            f[self.sel_order] = m
            sel[k] = f
        return pe, sel

    def catalog_rows(self, coord_np):
        jnp = self._jnp
        d = self._catalog_rows(jnp.asarray(coord_np), self.em_pe, self.em_sel)
        return {k: np.asarray(v) for k, v in d.items()}

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
        if self.dark:
            data_arrays.update({
                "em_pe.zgals": self.em_pe.zgals, "em_pe.dzgals": self.em_pe.dzgals,
                "em_pe.wgals": self.em_pe.wgals, "em_pe.dN_obs_kde": self.em_pe.dN_obs_kde,
            })
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
