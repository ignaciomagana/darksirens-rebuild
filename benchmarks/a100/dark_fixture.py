#!/usr/bin/env python3
"""Dark-siren mock fixtures: sidecar writer, verifier and the harness pre-flight.

    python dark_fixture.py write --fixture-dir DIR --name T --generate-log LOG \\
        --generator-copy GEN.py --wrapper-copy RUN.sh --reference-generator REF_GEN.py \\
        --reference-wrapper REF_RUN.sh --reference-sha SHA --invocation "env ... sh -x RUN.sh"
    python dark_fixture.py verify --fixture-dir DIR

The legacy generator (``scripts/mock_dark_sirens/generate_mock_data.py``) records
neither ``n0`` nor ``log10n0`` in its products (Phase-1 log10n0 audit, section
4.2). ``write`` therefore stores the injected density next to the products in
``galaxy_density.json`` (parsed from the generator's own command line, which the
wrapper's ``sh -x`` trace prints verbatim, and cross-checked against the
generator's "Derived N galaxies" line and the complete catalog), together with
the sha256 of every product, and writes ``SHA256SUMS``.

``preflight`` (used by ``bench_fixed_theta.py`` for every dark-siren record)
REFUSES a fixture whose ``log10n0`` lies outside the ``log10n0`` inference prior
of either implementation (``plans.LOG10N0_PRIOR``), whose sidecar density is not
the dark plans' survey fiducial, whose density LABEL disagrees with its DATA
(N_complete / V_c(zmax) of the complete catalog, to ``DENSITY_RTOL``), or whose PE /
selection / catalog / complete-catalog files are not the bytes the sidecar
describes. Imports neither implementation (numpy, h5py).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plans  # noqa: E402

SIDECAR_NAME = "galaxy_density.json"
SUMS_NAME = "SHA256SUMS"
SCHEMA = "darksirens-bench-dark-fixture/1"
PE_NAME = "mock_gw_events.h5"
SEL_NAME = "mock_gw_selection.h5"
COMPLETE_NAME = "mock_galaxy_catalog_complete.h5"
RAW_SURVEY_NAME = "mock_survey_raw.h5"
UNITS = ("comoving galaxy number density in Mpc^-3 at the generating H0 (not h^3 Mpc^-3), "
         "full sky: N = round(n0 * int_0^zmax dV_c/dz (1+z)^delta dz) "
         "(generate_mock_data.py:1571-1573, 110-116); the likelihood's log10n0 is log10 of the "
         "same density (legacy inference/prior.py:283-290, core analysis.py:17-21)")


class FixturePreflightError(RuntimeError):
    pass


#: |N_complete / (n0 V_c) - 1| allowed between the density LABEL and the DATA (the
#: generator draws round(n0 * int dV_c (1+z)^delta), so the true gap is ~1/N plus its
#: 20000-node trapezoid; a mislabelled fixture is off by a factor, not a permille).
DENSITY_RTOL = 1.0e-3
_C_KM_S = 299792.458


def comoving_volume_np(zmax, H0, Om0, w0, wa, delta=0.0, n=200_001) -> float:
    """int_0^zmax dV_c/dz (1+z)^delta dz in Mpc^3, full sky, flat w0waCDM, no radiation
    (astropy ``Flatw0waCDM`` with its default Tcmb0 = 0, as the generator builds it);
    numpy trapezoid on ``n`` nodes (relative error ~1e-10 here). Imports numpy only."""
    import numpy as np

    z = np.linspace(0.0, float(zmax), int(n))
    de = (1.0 + z) ** (3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * z / (1.0 + z))
    ez = np.sqrt(Om0 * (1.0 + z) ** 3 + (1.0 - Om0) * de)
    dh = _C_KM_S / float(H0)
    inv = 1.0 / ez
    dc = dh * np.concatenate([[0.0], np.cumsum(0.5 * (inv[1:] + inv[:-1]) * np.diff(z))])
    dvdz = 4.0 * np.pi * dh * dc ** 2 / ez * (1.0 + z) ** float(delta)
    return float(np.sum(0.5 * (dvdz[1:] + dvdz[:-1]) * np.diff(z)))


def density_check(n_complete, n0, zmax, H0, Om0, w0, wa, delta) -> dict:
    """The density the DATA carry (N_complete / V_c) against the LABEL n0."""
    vc = comoving_volume_np(zmax, H0, Om0, w0, wa, delta)
    ratio = (n_complete / vc) / float(n0)
    tol = DENSITY_RTOL + 1.0 / max(int(n_complete), 1)
    return {"n_complete": int(n_complete), "V_c_Mpc3_numpy": vc, "n_complete_over_V_c": n_complete / vc,
            "ratio_to_n0": ratio, "tol": tol, "ok": bool(abs(ratio - 1.0) <= tol),
            "note": "numpy flat-w0waCDM volume (dark_fixture.comoving_volume_np), independent of astropy"}


def sha256_file(path, bufsize=1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def git_blob_sha1(path) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _catalog_name(fixture_dir):
    names = sorted(n for n in os.listdir(fixture_dir)
                   if re.fullmatch(r"catalog_pixelated_nside_\d+\.h5", n))
    if len(names) != 1:
        raise FixturePreflightError(f"{fixture_dir}: expected one catalog_pixelated_nside_N.h5, got {names}")
    return names[0]


def _parse_generator_command(log_text):
    """The generator command line as the wrapper's ``sh -x`` trace printed it."""
    lines = [ln for ln in log_text.splitlines()
             if ln.startswith("+ python ") and "generate_mock_data.py" in ln]
    if len(lines) != 1:
        raise ValueError(f"expected one traced generator command, found {len(lines)}")
    cmd = lines[0][2:]
    toks = cmd.split()
    args = {}
    i = toks.index("scripts/mock_dark_sirens/generate_mock_data.py") + 1
    while i < len(toks):
        t = toks[i]
        if t.startswith("--"):
            if i + 1 < len(toks) and not toks[i + 1].startswith("--"):
                args[t[2:]] = toks[i + 1]
                i += 2
            else:
                args[t[2:]] = True
                i += 1
        else:
            i += 1
    return cmd, args


def _stdout_facts(log_text):
    facts = {}
    m = re.search(r"Derived ([\d,]+) galaxies from n0=([0-9.eE+-]+) Mpc\^-3 over z=\[0, ([0-9.eE+-]+)\]",
                  log_text)
    if m:
        facts["derived_galaxies"] = int(m.group(1).replace(",", ""))
        facts["derived_n0_printed"] = m.group(2)
        facts["derived_zmax_printed"] = m.group(3)
    m = re.search(r"GW selection\s+:.*\(([\d,]+)/([\d,]+) detected injections, Neff_fiducial=([0-9.]+)",
                  log_text)
    if m:
        facts["n_detected"] = int(m.group(1).replace(",", ""))
        facts["ndraw"] = int(m.group(2).replace(",", ""))
        facts["Neff_fiducial_printed"] = float(m.group(3))
    m = re.search(r"observed survey\s+:.*\(([\d,]+) galaxies retained", log_text)
    if m:
        facts["observed_galaxies"] = int(m.group(1).replace(",", ""))
    facts["ingestion_validation_passed"] = "Ingestion validation passed." in log_text
    facts["inference_started"] = "Starting optional darksirens_inference sampler run" in log_text
    return facts


def _h5_attrs(path, keys):
    import h5py

    out = {}
    with h5py.File(path, "r") as f:
        for k in keys:
            if k in f.attrs:
                v = f.attrs[k]
                if isinstance(v, bytes):
                    v = v.decode()
                elif hasattr(v, "item") and getattr(v, "shape", None) == ():
                    v = v.item()
                out[k] = v
        out["_datasets"] = sorted(f.keys())
    return out


def catalog_summary(path) -> dict:
    """nside, shape and occupancy of a pixelated catalog (host-side, h5py/numpy)."""
    import h5py
    import numpy as np

    with h5py.File(path, "r") as f:
        ng = np.asarray(f["ngals"][()])
        shape = list(f["zgals"].shape)
        nside = int(f.attrs["nside"])
        z_depth = float(f.attrs["z_depth"]) if "z_depth" in f.attrs else None
        datasets = sorted(f.keys())
    return {
        "nside": nside,
        "npix": int(12 * nside * nside),
        "n_rows": shape[0],
        "n_max": shape[1],
        "n_galaxies": int(ng.sum()),
        "n_pixels_occupied": int((ng > 0).sum()),
        "n_pixels_empty": int((ng == 0).sum()),
        "z_depth_attr": z_depth,
        "datasets": datasets,
    }


def write_sidecar(a) -> dict:
    import h5py
    import numpy as np

    d = os.path.abspath(a.fixture_dir)
    log_text = open(a.generate_log).read()
    cmd, gargs = _parse_generator_command(log_text)
    facts = _stdout_facts(log_text)
    if "n-galaxies" in gargs:
        raise SystemExit("the fixture was generated with --n-galaxies: refused (use --n0)")
    if "n0" not in gargs:
        raise SystemExit("the generator command has no explicit --n0: refused")
    if facts.get("inference_started"):
        raise SystemExit("the wrapper started an inference run: refused")
    n0_arg = gargs["n0"]
    n0 = float(n0_arg)
    log10n0 = math.log10(n0)
    zmax = float(gargs["zmax"])
    delta = float(gargs.get("galaxy-density-delta", 0.0))
    cat_name = _catalog_name(d)
    with h5py.File(os.path.join(d, COMPLETE_NAME), "r") as f:
        n_complete = int(f["z"].shape[0])
        zmax_complete = float(np.max(f["z"][()]))
    if facts.get("derived_galaxies") != n_complete:
        raise SystemExit(f"generator stdout says {facts.get('derived_galaxies')} galaxies but the "
                         f"complete catalog holds {n_complete}")
    printed = facts.get("derived_n0_printed")
    if printed is None or abs(float(printed) - n0) > 1e-5 * n0:
        raise SystemExit(f"generator stdout n0={printed!r} does not match the traced --n0 {n0_arg!r}")
    H0 = float(gargs.get("H0", 67.74))
    Om0 = float(gargs.get("Om0", 0.3075))
    w0 = float(gargs.get("w0", -1.0))
    wa = float(gargs.get("wa", 0.0))
    dens = density_check(n_complete, n0, zmax, H0, Om0, w0, wa, delta)
    if not dens["ok"]:
        raise SystemExit(f"the complete catalog implies n0 = {dens['n_complete_over_V_c']!r}, not the "
                         f"traced --n0 {n0_arg!r} (ratio {dens['ratio_to_n0']!r}): refused")
    # Implied density check: N_complete / V_c(z < zmax), full sky (astropy, as the generator).
    implied = None
    try:
        import astropy.units as u
        from astropy.cosmology import Flatw0waCDM

        cosmo = Flatw0waCDM(H0=H0 * u.km / u.s / u.Mpc, Om0=Om0, w0=w0, wa=wa)
        vc = float(cosmo.comoving_volume(zmax).to_value(u.Mpc ** 3))
        implied = {"V_c_Mpc3": vc, "n_complete_over_V_c": n_complete / vc,
                   "ratio_to_n0": (n_complete / vc) / n0,
                   "note": "delta = 0: the count is round(n0 V_c) up to the generator's "
                           "20000-node trapezoid (generate_mock_data.py:110-116, 1571-1573)"}
    except Exception as exc:  # pragma: no cover
        implied = {"error": f"{type(exc).__name__}: {exc}"}

    files = {}
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if not name.endswith(".h5") or not os.path.isfile(p):
            continue
        info = {"bytes": os.path.getsize(p), "sha256": sha256_file(p)}
        attrs = _h5_attrs(p, ("format_version", "nobs", "nsamp", "ndraw", "nside", "z_depth",
                              "Neff_fiducial", "selection_proposal", "pop_model"))
        info["datasets"] = attrs.pop("_datasets")
        info["attrs"] = attrs
        files[name] = info
    pe_attrs, sel_attrs = files[PE_NAME]["attrs"], files[SEL_NAME]["attrs"]
    cat = catalog_summary(os.path.join(d, cat_name))
    with h5py.File(os.path.join(d, SEL_NAME), "r") as f:
        n_det = int(f["dL"].shape[0])
    prior = {impl: {"lower": lo, "upper": hi, "source": src}
             for impl, (lo, hi, src) in plans.LOG10N0_PRIOR.items()}
    inside = {impl: bool(v["lower"] <= log10n0 <= v["upper"]) for impl, v in prior.items()}
    ref_gen_sha = sha256_file(a.reference_generator)
    gen_sha = sha256_file(a.generator_copy)
    wrap_sha = sha256_file(a.wrapper_copy)
    ref_wrap_sha = sha256_file(a.reference_wrapper)
    body = {
        "schema": SCHEMA,
        "name": a.name,
        "n0": n0,
        "n0_arg": n0_arg,
        "log10n0": log10n0,
        "log10n0_hex": float(log10n0).hex(),
        "log10n0_formula": "math.log10(float(n0_arg)) (= run_mock_data_test.sh:34)",
        "units": UNITS,
        "zmax": zmax,
        "delta": delta,
        "delta_source": "generator --galaxy-density-delta (SurveyConfig.delta)",
        "sigma_kde": 0.0,
        "sigma_kde_note": ("the generator has no sigma_kde: it realises photo-z z_obs and records "
                           "dzgals; 0.0 is the shared inference default of both implementations "
                           "(legacy core/constants.py SURVEY_PARAMS_FID_BY_NAME['sigma_kde'], core "
                           "catalog/types.py CatalogParameters.sigma_kde)"),
        "n_complete": n_complete,
        "n_complete_source": f"len({COMPLETE_NAME}:/z); equals the generator's 'Derived N galaxies' line",
        "z_max_complete_catalog": zmax_complete,
        "implied_density_check": implied,
        "implied_density_check_numpy": dens,
        "H0": H0, "Om0": Om0, "w0": w0, "wa": wa,
        "seed": int(gargs["seed"]),
        "nside": int(gargs["nside"]),
        "nobs": int(pe_attrs.get("nobs")),
        "nsamp": int(pe_attrs.get("nsamp")),
        "ndraw": int(sel_attrs.get("ndraw")),
        "n_detected": n_det,
        "n_galaxies_observed": cat["n_galaxies"],
        "catalog": dict(cat, file=cat_name),
        "inference_prior_log10n0": prior,
        "inside_inference_prior": inside,
        "inside_both": bool(all(inside.values())),
        "generator": {
            "copy": os.path.abspath(a.generator_copy),
            "sha256": gen_sha,
            "git_blob": git_blob_sha1(a.generator_copy),
            "reference_path": os.path.abspath(a.reference_generator),
            "reference_sha256": ref_gen_sha,
            "identical_to_reference": gen_sha == ref_gen_sha,
            "reference_commit": a.reference_sha,
            "reference_relpath": "scripts/mock_dark_sirens/generate_mock_data.py",
        },
        "wrapper": {
            "copy": os.path.abspath(a.wrapper_copy),
            "sha256": wrap_sha,
            "reference_sha256": ref_wrap_sha,
            "identical_to_reference": wrap_sha == ref_wrap_sha,
            "invocation": a.invocation,
            "note": "RUN_INFERENCE=0: generator + load_all_data ingestion check only; no sampler",
        },
        "command": cmd,
        "command_args": gargs,
        "generator_stdout": {"log": os.path.basename(a.generate_log),
                             "sha256": sha256_file(a.generate_log), "facts": facts},
        "harness_inputs": {"pe": PE_NAME, "sel": SEL_NAME, "catalog": cat_name},
        "formats": {
            "pe": pe_attrs.get("format_version"),
            "sel": sel_attrs.get("format_version"),
            "catalog": ("pixelated catalog: attr nside; zgals/dzgals/wgals (n_pix, n_max) f8, "
                        "ngals (n_pix,) i4, gal_app_mag; no z_depth attr"),
        },
        "files": files,
        "written_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "writer": os.path.abspath(__file__),
    }
    if not body["inside_both"]:
        raise SystemExit(f"log10n0 = {log10n0} is outside the inference prior of "
                         f"{[k for k, v in inside.items() if not v]}: refused")
    with open(os.path.join(d, SIDECAR_NAME), "w") as f:
        json.dump(body, f, indent=1)
        f.write("\n")
    names = sorted(n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n)) and n != SUMS_NAME)
    with open(os.path.join(d, SUMS_NAME), "w") as f:
        for n in names:
            f.write(f"{sha256_file(os.path.join(d, n))}  {n}\n")
    return body


def verify_sums(fixture_dir) -> dict:
    d = os.path.abspath(fixture_dir)
    bad, n = [], 0
    if not os.path.isfile(os.path.join(d, SUMS_NAME)):
        return {"n_files": 0, "mismatch": [], "ok": False, "error": f"no {SUMS_NAME} in {d}"}
    with open(os.path.join(d, SUMS_NAME)) as f:
        for line in f:
            h, name = line.strip().split("  ", 1)
            n += 1
            if sha256_file(os.path.join(d, name)) != h:
                bad.append(name)
    return {"n_files": n, "mismatch": bad, "ok": not bad}


def load_sidecar_for(catalog_path) -> tuple[str, dict]:
    d = os.path.dirname(os.path.abspath(catalog_path))
    p = os.path.join(d, SIDECAR_NAME)
    if not os.path.isfile(p):
        raise FixturePreflightError(f"no {SIDECAR_NAME} next to {catalog_path}: the fixture's "
                                    "injected density is unrecorded")
    with open(p) as f:
        return p, json.load(f)


def preflight(catalog_path, pe_path, sel_path, plan) -> dict:
    """Refuse a fixture the dark plans cannot use; return the evidence dict."""
    path, sc = load_sidecar_for(catalog_path)
    errs = []
    if sc.get("schema") != SCHEMA:
        errs.append(f"sidecar schema {sc.get('schema')!r} != {SCHEMA!r}")
    log10n0 = float(sc["log10n0"])
    if float.fromhex(sc["log10n0_hex"]) != log10n0:
        errs.append("sidecar log10n0 and log10n0_hex disagree")
    if math.log10(float(sc["n0_arg"])) != log10n0:
        errs.append("sidecar log10n0 != log10(n0_arg)")
    if "n-galaxies" in (sc.get("command_args") or {}):
        errs.append("fixture generated with --n-galaxies")
    inside = {}
    for impl, (lo, hi, src) in plans.LOG10N0_PRIOR.items():
        inside[impl] = bool(lo <= log10n0 <= hi)
        if not inside[impl]:
            errs.append(f"fixture log10n0 = {log10n0!r} is outside the {impl} log10n0 prior "
                        f"[{lo}, {hi}] ({src})")
    fid = plans.SURVEY_FIDUCIALS
    if float(fid["log10n0"]).hex() != float(log10n0).hex():
        errs.append(f"fixture log10n0 {log10n0!r} != the dark plans' survey fiducial "
                    f"{fid['log10n0']!r} (plans.SURVEY_FIDUCIALS)")
    for k in ("delta", "sigma_kde"):
        if float(sc[k]).hex() != float(fid[k]).hex():
            errs.append(f"fixture {k} {sc[k]!r} != plans.SURVEY_FIDUCIALS[{k!r}] {fid[k]!r}")
    files = sc.get("files", {})
    checked = {}
    # The density LABEL must be the density of the DATA: recount the fixture's complete
    # catalog (its bytes must be the sidecar's) and compare N_complete / V_c(zmax) with
    # n0. A sidecar copied next to other products (or hand-edited) is refused here.
    density = None
    comp = os.path.join(os.path.dirname(os.path.abspath(catalog_path)), COMPLETE_NAME)
    if not os.path.isfile(comp):
        errs.append(f"no {COMPLETE_NAME} next to the catalog: the density label cannot be "
                    "checked against the data")
    else:
        got = sha256_file(comp)
        want = (files.get(COMPLETE_NAME) or {}).get("sha256")
        checked["complete_catalog"] = {"path": comp, "sha256": got, "matches_sidecar": got == want}
        if got != want:
            errs.append(f"{comp} is not the sidecar's {COMPLETE_NAME}")
        import h5py

        with h5py.File(comp, "r") as f:
            n_comp = int(f["z"].shape[0])
        try:
            density = density_check(n_comp, float(sc["n0"]), float(sc["zmax"]), float(sc["H0"]),
                                    float(sc["Om0"]), float(sc["w0"]), float(sc["wa"]),
                                    float(sc["delta"]))
        except (KeyError, TypeError, ValueError) as exc:
            errs.append(f"sidecar lacks the fields of the density check: {exc!r}")
        else:
            if n_comp != sc.get("n_complete"):
                errs.append(f"{COMPLETE_NAME} holds {n_comp} galaxies, the sidecar says "
                            f"{sc.get('n_complete')}")
            if not density["ok"]:
                errs.append(f"the data imply n0 = {density['n_complete_over_V_c']!r} "
                            f"(N_complete {n_comp} / V_c(z<{sc['zmax']}) {density['V_c_Mpc3_numpy']!r}"
                            f" Mpc^3), not the sidecar's n0 = {sc['n0']!r} (ratio "
                            f"{density['ratio_to_n0']!r}, tolerance {density['tol']!r})")
    for role, p in (("catalog", catalog_path), ("pe", pe_path), ("sel", sel_path)):
        name = sc["harness_inputs"][role]
        want = (files.get(name) or {}).get("sha256")
        got = sha256_file(p)
        checked[role] = {"path": os.path.abspath(p), "expected_name": name,
                         "sha256": got, "matches_sidecar": got == want}
        if got != want:
            errs.append(f"{role} file {p} (sha256 {got[:16]}...) is not the fixture's {name} "
                        f"({str(want)[:16]}...)")
    ev = {
        "sidecar": path,
        "sidecar_sha256": sha256_file(path),
        "fixture": sc.get("name"),
        "n0": sc.get("n0"),
        "log10n0": log10n0,
        "log10n0_prior": {k: list(v[:2]) + [v[2]] for k, v in plans.LOG10N0_PRIOR.items()},
        "inside_prior": inside,
        "survey_fiducials_plans": dict(fid),
        "density_check": density,
        "inputs": checked,
        "status": "ok" if not errs else "refused",
        "errors": errs,
    }
    if errs:
        raise FixturePreflightError("; ".join(errs))
    return ev


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("--fixture-dir", required=True)
    w.add_argument("--name", required=True)
    w.add_argument("--generate-log", required=True)
    w.add_argument("--generator-copy", required=True)
    w.add_argument("--wrapper-copy", required=True)
    w.add_argument("--reference-generator", required=True)
    w.add_argument("--reference-wrapper", required=True)
    w.add_argument("--reference-sha", required=True)
    w.add_argument("--invocation", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--fixture-dir", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "write":
        body = write_sidecar(a)
        print(json.dumps({k: body[k] for k in ("name", "n0", "log10n0", "zmax", "n_complete",
                                                "nobs", "nsamp", "ndraw", "n_detected", "nside",
                                                "inside_both")}))
        return 0
    res = verify_sums(a.fixture_dir)
    d = os.path.abspath(a.fixture_dir)
    _p, sc = load_sidecar_for(os.path.join(d, _catalog_name(d)))
    hi = sc["harness_inputs"]
    try:
        pre = preflight(os.path.join(d, hi["catalog"]), os.path.join(d, hi["pe"]),
                        os.path.join(d, hi["sel"]), None)
        res["preflight"] = "ok"
        res["log10n0"] = pre["log10n0"]
    except FixturePreflightError as exc:
        res["preflight"] = f"refused: {exc}"
    print(json.dumps(res))
    return 0 if res["ok"] and res["preflight"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
