#!/usr/bin/env python3
"""Generate solar-neutrino interaction spectra in liquid argon as plotting pickles.

A standard-solar-model neutrino flux is folded with neutrino cross sections on
argon nuclei and electrons, giving the number of true interactions per energy
bin for each channel (no detector response). The output follows the
``*_Cutflow.pkl`` convention consumed by ``script_aggregate_table.py`` and the
plotting scripts.

Outputs (in ``input/data/snowglobes/`` by default)
--------------------------------------------------
``<config>_<name>_SolarInteractions_Cutflow.pkl``
    Counts against true neutrino energy E_nu: CC, ES and NC.
``<config>_<name>_SolarElectronEnergy_Cutflow.pkl``
    Counts against electron kinetic energy T_e: CC and ES.
``<config>_<name>_SolarSpectra_Combined.pkl``
    Both of the above plus the oscillated neutrino flux, one row per spectrum,
    for tables and plots that compare them on a common energy axis.

Each file is also written without the ``<config>_<name>_`` prefix. Counts are
events / MeV / kt-year in 1 MeV bins from 0 to 30 MeV (events per bin for the
default binning).

Thresholds quoted in the literature, e.g. "events above 5 MeV" in Capozzi et al.
(2019), refer to T_e. A cut on E_nu keeps far more ES events, because the recoil
electron carries only part of the neutrino energy.

Usage
-----
    export SNOWGLOBES=/path/to/snowglobes
    export MARLEY=/path/to/marley
    python3 scripts/generate_snowglobes_solar_interactions.py
    python3 scripts/generate_snowglobes_solar_interactions.py --flux solar_bs05op_mixed

    python3 scripts/script_aggregate_table.py --path snowglobes \\
        --datafile SolarSpectra_Combined --configs lar_b16gs98 --names snowglobes \\
        -x Energy -y Counts --operation sum --select XSecModel Stage -s marley2009 Truth \\
        --rangex 5 20 --row_name Particle --row_name_mapping threshold_dict --drop_config \\
        --variable_name Component --variables CC ES NC --scientific --no_table

Physics
-------
Flux
    B16-GS98 [1], built from the per-component spectra in
    ``input/data/Solar_Neutrino_Spectrum.pkl`` with the pep and 7Be lines at
    their true energies. Models without component spectra, such as the BS05(OP)
    file shipped with SNOwGLoBES, are folded off the 0.2 MeV SNOwGLoBES flux
    file instead, spreading each bin's flux uniformly across it.
Oscillations
    nu_e = P_ee phi, nu_mu = nu_tau = (1 - P_ee) phi / 2. P_ee(E) is read from
    SNOwGLoBES ``fluxes/solar_bs05op_mixed.dat``: an adiabatic MSW-LMA curve with
    sin^2(theta_12) ~ 0.30, theta_13 = 0 and no Earth regeneration, so the rates
    are daytime rates.
ES, nu + e-
    Tree-level dsigma/dT shape, normalised per E_nu to the SNOwGLoBES totals [2],
    which include radiative corrections. Below 0.5 MeV, where the SNOwGLoBES
    tables start, the correction factor is held at its 0.5 MeV value.
CC, nu_e + 40Ar -> e- + 40K*
    ``marley2009``: sum over 40K* levels in the allowed approximation,
        sigma_i = G_F^2 |V_ud|^2 / pi * p_e E_e F(Z=19, E_e) * B_i,
        T_e = E_nu - Q_gs - E_x,i,
    using the B(F) and B(GT) strengths of MARLEY's [3]
    ``ve40ArCC_Bhattacharya2009.react`` (measurements of [4] plus QRPA above
    8 MeV). MARLEY's effective-momentum approximation and nuclear recoil are not
    included.
    ``default``, ``klmv``, ``marley``: SNOwGLoBES total cross-section tables. They
    carry no level information, so on the T_e axis only ``marley`` is provided,
    with its sigma(E_nu) shared among levels in the ``marley2009`` proportions.
NC, nu + 40Ar
    SNOwGLoBES tables. No outgoing electron: zero on the T_e axis.

Reference values (B16-GS98, events per kt-year, T_e > 5 MeV)
    CC (marley2009) 1146, CC (marley) 748, ES 358. Rescaled to the 8B flux of
    5.25e6 cm^-2 s^-1 used in [5], CC (marley2009) 1102 and ES 345, against
    ~1125 and ~321 derived from [5].

References
----------
[1] N. Vinyoles et al., Astrophys. J. 835, 202 (2017).
[2] SNOwGLoBES, https://github.com/SNOwGLoBES/snowglobes; nu-e cross sections
    from W. J. Marciano and Z. Parsa, J. Phys. G 29, 2629 (2003).
[3] S. Gardiner, Comput. Phys. Commun. 269, 108123 (2021).
[4] M. Bhattacharya et al., Phys. Rev. C 80, 055501 (2009).
[5] F. Capozzi, S. W. Li, G. Zhu and J. F. Beacom, Phys. Rev. Lett. 123, 131803 (2019).
"""

import argparse
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import loggamma

# Target and exposure
N_A = 6.02214076e23      # mol^-1
M_AR = 39.948            # g/mol, natural argon (SNOwGLoBES uses 1/40, a 0.13% difference)
Z_AR = 18                # electrons per argon atom
SEC_PER_YEAR = 3.1536e7  # 365 days

# Physical constants (CODATA 2018 / PDG)
M_E = 0.51099895          # MeV
ALPHA = 1 / 137.035999
G_F = 1.1663787e-11       # MeV^-2
V_UD = 0.97373
HBARC = 197.3269804       # MeV fm
HBARC2 = 3.893794e-22     # cm^2 MeV^2
SIN2_THETA_W = 0.23122
SIG0_ES = 2 * G_F ** 2 * M_E / np.pi * HBARC2  # cm^2 / MeV
Q_GS_K40 = 1.50441        # MeV, M(40K) - M(40Ar), atomic: nu_e threshold to the 40K ground state
Z_K40 = 19

# Display multipliers applied to the line entries of the solar-spectrum pickle
LINE_DISPLAY_SCALE = {"pep": 1.4, "b7": 4.7}

SNOWGLOBES_CC = {
    "default": "xs_nue_Ar40.dat",
    "klmv": "xs_nue_Ar40_klmv.dat",
    "marley": "xs_nue_Ar40_marley.dat",
}
MODEL_ORDER = ["marley2009", "default", "klmv", "marley"]
MARLEY_CC_REACT = "ve40ArCC_Bhattacharya2009.react"

SOLAR_MODEL_LABELS = {"b16gs98": "B16-GS98", "bs05op": "BS05(OP)"}


# ------------------------------------------------------------------------------ flux

def load_components(path, model):
    """Split the solar-spectrum pickle into (lines, continua), display scaling removed."""
    df = pickle.load(open(path, "rb"))
    df = df[df["Plot"] == model]
    if df.empty:
        raise SystemExit(f"No rows with Plot == {model!r} in {path}")
    lines, continua = [], []
    for _, row in df.iterrows():
        energy = np.asarray(row["Energy"], dtype=float)
        flux = np.asarray(row["Flux"], dtype=float)
        scale = LINE_DISPLAY_SCALE.get(row["Source"], 1.0)
        if energy.size == 2 and energy[0] == energy[1]:
            lines.append((row["Source"], energy[0], flux.max() / scale))
        else:
            continua.append((row["Source"], energy, flux / scale))
    return lines, continua


def flux_points_from_spectra(path, model, emax, step=0.002):
    """Unoscillated flux as sample points: (energy [MeV], flux per point [cm^-2 s^-1])."""
    lines, continua = load_components(path, model)
    mid = np.arange(step / 2, emax, step)
    density = sum(np.interp(mid, e, s, left=0.0, right=0.0) for _, e, s in continua)
    energy = np.concatenate([mid, [e for _, e, _ in lines]])
    weight = np.concatenate([density * step, [f for _, _, f in lines]])
    return energy, weight


def flux_points_from_file(path, native_width=0.2, sub=20):
    """Unoscillated flux points from a 0.2 MeV bin-centred SNOwGLoBES flux file."""
    data = np.loadtxt(path, comments="#")
    centres = data[:, 0] * 1e3
    total = np.clip(data[:, 1:4], 0, None).sum(axis=1)
    offsets = ((np.arange(sub) + 0.5) / sub - 0.5) * native_width
    energy = (centres[:, None] + offsets[None, :]).ravel()
    weight = np.repeat(total / sub, sub)
    keep = energy > 0
    return energy[keep], weight[keep]


def survival_probability(reference, energy):
    """P_ee(E) = phi_nue / (phi_nue + phi_numu + phi_nutau) from a mixed SNOwGLoBES flux file."""
    data = np.loadtxt(reference, comments="#")
    e = data[:, 0] * 1e3
    nue = np.clip(data[:, 1], 0, None)
    nux = np.clip(data[:, 2], 0, None) + np.clip(data[:, 3], 0, None)
    good = (nue + nux) > 0
    return np.interp(energy, e[good], nue[good] / (nue + nux)[good])


# ------------------------------------------------------------------------------ cross sections

def read_xs(path, col, energy):
    """Cross section [cm^2] from a SNOwGLoBES file (log10(E/GeV), sigma/E in 1e-38 cm^2/GeV)."""
    data = np.loadtxt(path, comments="#")
    e = 10 ** data[:, 0] * 1e3
    sigma = np.clip(data[:, col] * 10 ** data[:, 0], 0, None) * 1e-38
    order = np.argsort(e)
    return np.interp(energy, e[order], sigma[order], left=0.0, right=0.0)


def es_t_max(energy):
    return energy / (1 + M_E / (2 * energy))


def es_antiderivative(t, energy, g_l):
    """Integral over T of the ES shape g_L^2 + g_R^2 (1 - T/E)^2 - g_L g_R m_e T / E^2."""
    g_r = SIN2_THETA_W
    return (g_l ** 2 * t - g_r ** 2 * energy / 3 * (1 - t / energy) ** 3
            - g_l * g_r * M_E * t ** 2 / (2 * energy ** 2))


def es_tree_total(energy, g_l):
    return SIG0_ES * (es_antiderivative(es_t_max(energy), energy, g_l)
                      - es_antiderivative(0.0, energy, g_l))


def es_cross_sections(xs_dir, energy):
    """Per flavour: (total sigma [cm^2], g_L), tree level scaled to the SNOwGLoBES totals."""
    out = []
    for fname, col, g_l in [("xs_nue_e.dat", 1, 0.5 + SIN2_THETA_W),
                            ("xs_numu_e.dat", 2, -0.5 + SIN2_THETA_W),
                            ("xs_nutau_e.dat", 3, -0.5 + SIN2_THETA_W)]:
        data = np.loadtxt(xs_dir / fname, comments="#")
        e = 10 ** data[:, 0] * 1e3
        sigma = data[:, col] * 10 ** data[:, 0] * 1e-38
        order = np.argsort(e)
        factor = sigma[order] / es_tree_total(e[order], g_l)
        # np.interp clamps outside the table, holding the end-point correction factor
        out.append((es_tree_total(energy, g_l) * np.interp(energy, e[order], factor), g_l))
    return out


def load_marley_levels(path):
    """(excitation energy [MeV], strength) for every level in a MARLEY react file."""
    rows = [line.split() for line in open(path)
            if not line.startswith("#") and len(line.split()) == 3]
    levels = np.array(rows, dtype=float)
    return levels[:, 0], levels[:, 1]


def fermi_function(total_energy, z=Z_K40, a=40):
    """Relativistic Fermi function with a uniform-sphere nuclear radius 1.2 A^(1/3) fm."""
    p = np.sqrt(np.clip(total_energy ** 2 - M_E ** 2, 1e-12, None))
    gamma = np.sqrt(1 - (ALPHA * z) ** 2)
    eta = ALPHA * z * total_energy / p
    radius = 1.2 * a ** (1 / 3) / HBARC
    log_f = (np.log(2 * (1 + gamma)) + (2 * gamma - 2) * np.log(2 * p * radius) + np.pi * eta
             + 2 * np.real(loggamma(gamma + 1j * eta)) - 2 * np.real(loggamma(2 * gamma + 1)))
    return np.exp(log_f)


def cc_level_cross_sections(energy, excitation, strength):
    """Per level: cross sections [cm^2] and electron kinetic energies [MeV], shape (N, L)."""
    t = energy[:, None] - Q_GS_K40 - excitation[None, :]
    allowed = t > 0
    e_e = np.where(allowed, t + M_E, 2 * M_E)
    p_e = np.sqrt(e_e ** 2 - M_E ** 2)
    sigma = G_F ** 2 * V_UD ** 2 / np.pi * p_e * e_e * fermi_function(e_e) * strength[None, :] * HBARC2
    return np.where(allowed, sigma, 0.0), t


# ------------------------------------------------------------------------------ fold

def fold(energy, weight, p_ee, xs_dir, levels, mass_kt, edges):
    """
    Events per bin per year in mass_kt kt of argon.

    Returns (neutrino, electron) dictionaries of binned spectra keyed by channel,
    e.g. "ES", "NC", "CC/marley2009"; ``neutrino`` also holds the oscillated flux
    per bin as "Flux/nue" and "Flux/nux".
    """
    n_bins = len(edges) - 1
    n_ar = mass_kt * 1e9 / M_AR * N_A
    n_e = Z_AR * n_ar
    flavour = [weight * p_ee, weight * (1 - p_ee) / 2, weight * (1 - p_ee) / 2]

    def hist(values, index):
        out = np.zeros(n_bins)
        ok = (index >= 0) & (index < n_bins)
        np.add.at(out, index[ok], values[ok])
        return out

    nu_bin = np.digitize(energy, edges) - 1
    neutrino, electron = {}, {}

    neutrino["Flux/nue"] = hist(flavour[0], nu_bin)
    neutrino["Flux/nux"] = hist(flavour[1] + flavour[2], nu_bin)

    # ES: rate by E_nu, and spread over T_e with the analytic recoil shape
    es_rates = []
    electron["ES"] = np.zeros(n_bins)
    t_max = es_t_max(energy)
    for phi, (sigma, g_l) in zip(flavour, es_cross_sections(xs_dir, energy)):
        rate = phi * sigma * n_e * SEC_PER_YEAR
        es_rates.append(rate)
        norm = es_antiderivative(t_max, energy, g_l) - es_antiderivative(0.0, energy, g_l)
        lo = np.minimum(edges[None, :-1], t_max[:, None])
        hi = np.minimum(edges[None, 1:], t_max[:, None])
        frac = (es_antiderivative(hi, energy[:, None], g_l)
                - es_antiderivative(lo, energy[:, None], g_l)) / norm[:, None]
        electron["ES"] += (rate[:, None] * frac).sum(axis=0)
    neutrino["ES"] = hist(sum(es_rates), nu_bin)

    nc_sigma = [read_xs(xs_dir / "xs_nc_nue_Ar40.dat", 1, energy),
                read_xs(xs_dir / "xs_nc_numu_Ar40.dat", 2, energy),
                read_xs(xs_dir / "xs_nc_nutau_Ar40.dat", 3, energy)]
    neutrino["NC"] = hist(sum(p * s for p, s in zip(flavour, nc_sigma)) * n_ar * SEC_PER_YEAR, nu_bin)

    for model, fname in SNOWGLOBES_CC.items():
        neutrino[f"CC/{model}"] = hist(
            flavour[0] * read_xs(xs_dir / fname, 1, energy) * n_ar * SEC_PER_YEAR, nu_bin)

    if levels is not None:
        sigma, t = cc_level_cross_sections(energy, *levels)
        rate = flavour[0][:, None] * sigma * n_ar * SEC_PER_YEAR
        neutrino["CC/marley2009"] = hist(rate.sum(axis=1), nu_bin)
        t_bin = (np.digitize(t, edges) - 1).ravel()
        electron["CC/marley2009"] = hist(rate.ravel(), t_bin)

        # MARLEY table normalisation, shared among levels in the marley2009 proportions
        total = sigma.sum(axis=1)
        share = np.divide(sigma, total[:, None], out=np.zeros_like(sigma), where=total[:, None] > 0)
        table = read_xs(xs_dir / SNOWGLOBES_CC["marley"], 1, energy)
        rate_table = flavour[0][:, None] * share * table[:, None] * n_ar * SEC_PER_YEAR
        electron["CC/marley"] = hist(rate_table.ravel(), t_bin)

    return neutrino, electron


# ------------------------------------------------------------------------------ output

def base_row(meta, bin_width, variable):
    return {
        "Config": meta["config"], "Name": meta["name"], "Folder": "snowglobes", "Stage": "Truth",
        "SolarModel": meta["solar_model"], "Flux": meta["flux"], "Threshold": meta["threshold"],
        "Method": meta["method"], "EnergyVariable": variable, "BinWidth": bin_width,
        "EnergyUnit": "MeV", "CountsUnit": f"events / MeV / {meta['exposure_unit']}",
        "Exposure": 1.0, "ExposureUnit": meta["exposure_unit"],
    }


def build_dataframe(spectra, centres, bin_width, meta, variable):
    """One row per (XSecModel, Component) for a single energy axis."""
    models = sorted({k.split("/", 1)[1] for k in spectra if k.startswith("CC/")},
                    key=lambda m: MODEL_ORDER.index(m) if m in MODEL_ORDER else len(MODEL_ORDER))
    rows = []
    for model in models:
        components = {"CC": spectra[f"CC/{model}"], "ES": spectra["ES"]}
        if "NC" in spectra:
            components["NC"] = spectra["NC"]
        components = {"Solar": sum(components.values()), **components}
        for component, counts in components.items():
            rows.append({**base_row(meta, bin_width, variable),
                         "Component": component, "XSecModel": model,
                         "Energy": list(centres), "Counts": list(counts / bin_width)})
    return pd.DataFrame(rows)


def build_combined(neutrino, electron, centres, bin_width, meta, models=("marley", "marley2009")):
    """
    One row per spectrum on both energy axes, plus the oscillated neutrino flux.

    ``Particle`` is "Neutrino" (E_nu axis) or "Electron" (T_e axis) and
    ``Spectrum`` is a display label such as "CC ($T_e$)". Counts and
    NeutrinoFlux are separate y columns; each row fills one and leaves the other
    NaN. ES, NC and the flux do not depend on the CC model and are repeated for
    every XSecModel, so selecting one model gives a complete set.
    """
    n = len(centres)
    empty = [np.nan] * n
    rows = []

    def add(model, particle, component, spectrum, variable, counts=None, flux=None):
        rows.append({**base_row(meta, bin_width, variable),
                     "XSecModel": model, "Particle": particle, "Component": component,
                     "Spectrum": spectrum, "FluxUnit": "nu / cm^2 / s / MeV",
                     "Energy": list(centres),
                     "Counts": list(counts / bin_width) if counts is not None else empty,
                     "NeutrinoFlux": list(flux / bin_width) if flux is not None else empty})

    for model in models:
        if f"CC/{model}" not in neutrino or f"CC/{model}" not in electron:
            continue
        axes = [
            ("Neutrino", r"$E_\nu$", "True Neutrino Energy",
             {"CC": neutrino[f"CC/{model}"], "ES": neutrino["ES"], "NC": neutrino["NC"]}),
            ("Electron", r"$T_e$", "Electron Kinetic Energy",
             {"CC": electron[f"CC/{model}"], "ES": electron["ES"], "NC": np.zeros(n)}),
        ]
        for particle, label, variable, components in axes:
            components = {"Solar": sum(components.values()), **components}
            for component, counts in components.items():
                add(model, particle, component, f"{component} ({label})", variable, counts=counts)
        for key, label in (("Flux/nue", r"Flux $\nu_e$"), ("Flux/nux", r"Flux $\nu_\mu+\nu_\tau$")):
            add(model, "Neutrino", "Flux", label, "True Neutrino Energy", flux=neutrino[key])
    return pd.DataFrame(rows)


def write_datafile(df, outdir, config, name, datafile):
    """Write <config>_<name>_<datafile>.pkl and the prefix-free <datafile>.pkl."""
    bare = df.copy()
    bare["Config"] = None
    bare["Name"] = None
    for path, frame in [(outdir / f"{config}_{name}_{datafile}.pkl", df),
                        (outdir / f"{datafile}.pkl", bare)]:
        with path.open("wb") as handle:
            pickle.dump(frame, handle)
        print(f"Wrote {path}")


# ------------------------------------------------------------------------------ main

def default_marley_react():
    if os.environ.get("MARLEY_CC_REACT"):
        return os.environ["MARLEY_CC_REACT"]
    if os.environ.get("MARLEY"):
        return str(Path(os.environ["MARLEY"]) / "data" / "react" / MARLEY_CC_REACT)
    return None


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--snowglobes", default=os.environ.get("SNOWGLOBES"),
                        help="SNOwGLoBES installation (default: $SNOWGLOBES)")
    parser.add_argument("--marley-react", dest="marley_react", default=default_marley_react(),
                        help=f"MARLEY 40Ar CC react file for the marley2009 model (default: "
                             f"$MARLEY_CC_REACT, else $MARLEY/data/react/{MARLEY_CC_REACT})")
    parser.add_argument("--spectra", default=None,
                        help="Per-component solar spectra pickle "
                             "(default: input/data/Solar_Neutrino_Spectrum.pkl)")
    parser.add_argument("--flux", default="solar_b16gs98_mixed",
                        help="Flux file stem in <snowglobes>/fluxes naming the solar model; "
                             "folded directly only with --method fluxfile")
    parser.add_argument("--solar-model", dest="solar_model", default=None,
                        help="'Plot' value selected from --spectra (default: inferred from --flux)")
    parser.add_argument("--pee-reference", dest="pee_reference", default="solar_bs05op_mixed",
                        help="Mixed SNOwGLoBES flux file stem supplying P_ee(E)")
    parser.add_argument("--method", choices=["fine", "fluxfile"], default=None,
                        help="fine: per-component spectra; fluxfile: 0.2 MeV flux file "
                             "(default: fine when --spectra has the solar model)")
    parser.add_argument("--emin", type=float, default=0.0, help="First bin edge [MeV]")
    parser.add_argument("--emax", type=float, default=30.0, help="Last bin edge [MeV]")
    parser.add_argument("--bin-width", dest="bin_width", type=float, default=1.0,
                        help="Bin width [MeV]")
    parser.add_argument("--threshold", type=float, default=5.0,
                        help="Threshold [MeV] stored in the Threshold column and used for the "
                             "printed summary")
    parser.add_argument("--mass", type=float, default=1.0,
                        help="Exposure in kt-year used for the normalisation")
    parser.add_argument("--config", default=None, help="Config tag (default: lar_<flux tag>)")
    parser.add_argument("--name", default="snowglobes", help="Name tag")
    parser.add_argument("--datafile", default="SolarInteractions_Cutflow",
                        help="Datafile stem for the neutrino-energy spectra")
    parser.add_argument("--electron-datafile", dest="electron_datafile",
                        default="SolarElectronEnergy_Cutflow",
                        help="Datafile stem for the electron-energy spectra")
    parser.add_argument("--combined-datafile", dest="combined_datafile",
                        default="SolarSpectra_Combined",
                        help="Datafile stem for the combined spectra")
    parser.add_argument("--outdir", default=None, help="Output directory "
                        "(default: input/data/snowglobes)")
    parser.add_argument("--check", action="store_true",
                        help="Also fold --check-flux and print the ratio of integrals")
    parser.add_argument("--check-flux", dest="check_flux", default="solar_bs05op_mixed",
                        help="0.2 MeV SNOwGLoBES flux file stem for --check")
    args = parser.parse_args()
    if not args.snowglobes:
        parser.error("set $SNOWGLOBES or pass --snowglobes")
    return args


def main():
    args = parse_args()

    repo = Path(__file__).resolve().parents[1]
    snowglobes = Path(args.snowglobes)
    xs_dir = snowglobes / "xscns"
    flux_file = snowglobes / "fluxes" / f"{args.flux}.dat"
    reference = snowglobes / "fluxes" / f"{args.pee_reference}.dat"
    flux_tag = args.flux.replace("solar_", "").replace("_mixed", "")
    solar_model = args.solar_model or SOLAR_MODEL_LABELS.get(flux_tag, flux_tag)
    config = args.config or f"lar_{flux_tag}"
    spectra_path = Path(args.spectra) if args.spectra else repo / "input" / "data" / "Solar_Neutrino_Spectrum.pkl"
    outdir = Path(args.outdir) if args.outdir else repo / "input" / "data" / "snowglobes"
    outdir.mkdir(parents=True, exist_ok=True)

    edges = np.arange(args.emin, args.emax + args.bin_width / 2, args.bin_width)
    centres = (edges[:-1] + edges[1:]) / 2

    levels = None
    if args.marley_react and Path(args.marley_react).exists():
        levels = load_marley_levels(args.marley_react)
    else:
        print(f"MARLEY react file not found ({args.marley_react}): skipping the marley2009 "
              "model and the electron-energy and combined datafiles.")

    method = args.method
    if method is None:
        available = set(pickle.load(open(spectra_path, "rb"))["Plot"].unique())
        method = "fine" if solar_model in available else "fluxfile"
        if method == "fluxfile":
            print(f"No component spectra for {solar_model!r}: folding {flux_file.name}.")
    if method == "fine":
        energy, weight = flux_points_from_spectra(spectra_path, solar_model, args.emax)
    else:
        energy, weight = flux_points_from_file(flux_file)

    neutrino, electron = fold(energy, weight, survival_probability(reference, energy),
                              xs_dir, levels, args.mass, edges)

    exposure_unit = "kt-year" if args.mass == 1.0 else f"{args.mass:g} kt-year"
    meta = dict(config=config, name=args.name, solar_model=solar_model, flux=args.flux,
                threshold=args.threshold, method=method, exposure_unit=exposure_unit)
    write_datafile(build_dataframe(neutrino, centres, args.bin_width, meta, "True Neutrino Energy"),
                   outdir, config, args.name, args.datafile)
    if levels is not None:
        write_datafile(build_dataframe(electron, centres, args.bin_width, meta, "Electron Kinetic Energy"),
                       outdir, config, args.name, args.electron_datafile)
        write_datafile(build_combined(neutrino, electron, centres, args.bin_width, meta),
                       outdir, config, args.name, args.combined_datafile)

    keep = edges[:-1] >= args.threshold
    print(f"\n{solar_model}, events / {exposure_unit}, lower bin edge >= {args.threshold} MeV")
    print(f"  {'channel':16s} {'E_nu axis':>11s} {'T_e axis':>11s}")
    for channel in ["CC/marley2009", "CC/default", "CC/klmv", "CC/marley", "ES", "NC"]:
        if channel not in neutrino:
            continue
        el = f"{electron[channel][keep].sum():11.1f}" if channel in electron else f"{'-':>11s}"
        print(f"  {channel:16s} {neutrino[channel][keep].sum():11.1f} {el}")

    if args.check:
        f_energy, f_weight = flux_points_from_file(snowglobes / "fluxes" / f"{args.check_flux}.dat")
        ref_nu, _ = fold(f_energy, f_weight, survival_probability(reference, f_energy),
                         xs_dir, levels, args.mass, edges)
        print(f"\nRatio to {args.check_flux} (E_nu axis, same threshold):")
        for channel in neutrino:
            a, b = neutrino[channel][keep].sum(), ref_nu[channel][keep].sum()
            print(f"  {channel:16s} {a:11.4g} / {b:11.4g} = {a / b if b else float('nan'):.4f}")


if __name__ == "__main__":
    main()
