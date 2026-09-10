#!/usr/bin/env python3
"""
Generate the solar-neutrino interaction spectrum in liquid argon as a
plot-ready .pkl.

Folds a standard-solar-model neutrino flux with the SNOwGLoBES argon and
electron cross sections to get the number of true interactions per bin of
neutrino energy, split by channel (CC / ES / NC), and writes it in the same
schema as the SOLAR pipeline's *_Cutflow.pkl files so both
scripts/script_aggregate_table.py and the plotting scripts can read it.

Energy axis
-----------
Output bins default to 1 MeV wide, centred on 0.5, 1.5, ... 29.5 MeV, matching
the axis used by *_SolarEnergy_*_Cutflow.pkl. Because the bins are 1 MeV wide,
Counts is simultaneously "events per bin" and "events / MeV", so summing the
array over bins gives the integrated rate.

The fold is done on a fine grid built from the solar-model component spectra
rather than on the 0.2 MeV SNOwGLoBES flux file, so line components (pep, 7Be)
land at their true energy and output bin edges are respected exactly. Passing
--check reruns the integral off the binned flux file as a cross-check.

Physics inputs
--------------
  <spectra pkl>                   per-component dphi/dE, B16-GS98 normalised
  fluxes/solar_*_mixed.dat        supplies P_ee(E) (and the --check integral)
  xscns/xs_{nue,numu,nutau}_e.dat nu-e elastic scattering (Marciano et al.)
  xscns/xs_nue_Ar40*.dat          nu_e + 40Ar CC (default / klmv / marley)
  xscns/xs_nc_{flavour}_Ar40.dat  nu + 40Ar NC

No smearing matrix or efficiency curve is applied: these are interaction
counts, not reconstructed events.
"""

import argparse
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

N_A = 6.02214076e23      # Avogadro
M_AR = 39.948            # g/mol, natural argon (SNOwGLoBES itself uses 1/40; -0.13%)
Z_AR = 18                # electrons per argon atom
SEC_PER_YEAR = 3.1536e7  # 365 days

# Display multipliers on the line entries of the plotting pkl, divided out here.
LINE_DISPLAY_SCALE = {"pep": 1.4, "b7": 4.7}

CC_MODELS = {
    "default": "xs_nue_Ar40.dat",        # SNOwGLoBES default, threshold 3.0 MeV
    "klmv": "xs_nue_Ar40_klmv.dat",      # Kolbe/Langanke/Martinez-Pinedo/Vogel, 1.5 MeV
    "marley": "xs_nue_Ar40_marley.dat",  # MARLEY tabulation, 5.0 MeV
}


# --------------------------------------------------------------------------- inputs

def read_xs(path, col, grid):
    """SNOwGLoBES xs file: log10(E/GeV), then sigma/E in 1e-38 cm^2/GeV per flavour."""
    data = np.loadtxt(path, comments="#")
    energy = 10 ** data[:, 0] * 1e3                                    # MeV
    sigma = np.clip(data[:, col] * 10 ** data[:, 0], 0, None) * 1e-38  # cm^2
    order = np.argsort(energy)
    return np.interp(grid, energy[order], sigma[order], left=0.0, right=0.0)


def load_components(path, model):
    """Split the plotting pkl into (lines, continua) with display scaling removed."""
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


def survival_probability(reference, grid):
    """P_ee(E) read off a mixed SNOwGLoBES flux file."""
    data = np.loadtxt(reference, comments="#")
    energy = data[:, 0] * 1e3
    nue = np.clip(data[:, 1], 0, None)
    nux = np.clip(data[:, 2], 0, None) + np.clip(data[:, 3], 0, None)
    total = nue + nux
    good = total > 0
    return np.interp(grid, energy[good], nue[good] / total[good])


# --------------------------------------------------------------------------- fold

def channel_cross_sections(xs_dir, grid):
    """Per channel, the cross section seen by (nu_e, nu_mu, nu_tau) and its target."""
    channels = {
        "ES": (
            [read_xs(xs_dir / "xs_nue_e.dat", 1, grid),
             read_xs(xs_dir / "xs_numu_e.dat", 2, grid),
             read_xs(xs_dir / "xs_nutau_e.dat", 3, grid)],
            "electron",
        ),
        "NC": (
            [read_xs(xs_dir / "xs_nc_nue_Ar40.dat", 1, grid),
             read_xs(xs_dir / "xs_nc_numu_Ar40.dat", 2, grid),
             read_xs(xs_dir / "xs_nc_nutau_Ar40.dat", 3, grid)],
            "argon",
        ),
    }
    zero = np.zeros_like(grid)
    for model, fname in CC_MODELS.items():
        channels[f"CC/{model}"] = ([read_xs(xs_dir / fname, 1, grid), zero, zero], "argon")
    return channels


def compute_spectra(spectra, solar_model, reference, xs_dir, edges, mass_kt, step=0.002):
    """Interaction rate per output bin, in events / bin / (mass_kt kt) / year."""
    lines, continua = load_components(spectra, solar_model)

    grid = np.arange(edges[0], edges[-1] + step, step)
    # Unoscillated dphi/dE summed over the continuum components [1/cm^2/s/MeV]
    density = np.zeros_like(grid)
    for _, energy, spectrum in continua:
        density += np.interp(grid, energy, spectrum, left=0.0, right=0.0)

    p_ee = survival_probability(reference, grid)
    # Flavour split: nu_mu and nu_tau share the non-electron flux equally.
    flavour_density = [density * p_ee, density * (1 - p_ee) / 2, density * (1 - p_ee) / 2]

    n_ar = mass_kt * 1e9 / M_AR * N_A
    targets = {"argon": n_ar, "electron": Z_AR * n_ar}
    channels = channel_cross_sections(xs_dir, grid)

    # Line components are delta functions: evaluate the cross sections there and
    # drop the whole contribution into the bin that contains the line.
    line_grid = np.array([energy for _, energy, _ in lines])
    line_flux = np.array([flux for _, _, flux in lines])
    line_pee = survival_probability(reference, line_grid)
    line_flavour = [line_flux * line_pee, line_flux * (1 - line_pee) / 2,
                    line_flux * (1 - line_pee) / 2]
    line_channels = channel_cross_sections(xs_dir, line_grid)
    line_bin = np.digitize(line_grid, edges) - 1

    spectra_out = {}
    for channel, (sigmas, target) in channels.items():
        rate = sum(phi * sig for phi, sig in zip(flavour_density, sigmas))
        rate *= targets[target] * SEC_PER_YEAR                    # events / MeV / year

        binned = np.zeros(len(edges) - 1)
        for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
            mask = (grid >= lo) & (grid <= hi)
            if mask.sum() > 1:
                binned[i] = np.trapezoid(rate[mask], grid[mask])

        line_sigmas = line_channels[channel][0]
        line_rate = sum(phi * sig for phi, sig in zip(line_flavour, line_sigmas))
        line_rate = line_rate * targets[target] * SEC_PER_YEAR    # events / year
        for i, value in zip(line_bin, np.atleast_1d(line_rate)):
            if 0 <= i < len(binned):
                binned[i] += value

        spectra_out[channel] = binned
    return spectra_out


def _rates_from_flux_file(flux_path, xs_dir, mass_kt):
    """Per-native-bin rates off a 0.2 MeV binned SNOwGLoBES flux file."""
    flux = np.loadtxt(flux_path, comments="#")
    energy = flux[:, 0] * 1e3
    phi = np.clip(flux[:, 1:4], 0, None)
    n_ar = mass_kt * 1e9 / M_AR * N_A
    targets = {"argon": n_ar, "electron": Z_AR * n_ar}

    rates = {}
    for channel, (sigmas, target) in channel_cross_sections(xs_dir, energy).items():
        per_bin = sum(phi[:, i] * s for i, s in enumerate(sigmas))
        rates[channel] = per_bin * targets[target] * SEC_PER_YEAR
    return energy, rates


def check_against_flux_file(snowglobes, flux_name, threshold, mass_kt):
    """Integrated rates recomputed off the 0.2 MeV binned SNOwGLoBES flux file."""
    energy, rates = _rates_from_flux_file(
        Path(snowglobes) / "fluxes" / f"{flux_name}.dat",
        Path(snowglobes) / "xscns", mass_kt)
    above = energy >= threshold
    return {channel: float(rate[above].sum()) for channel, rate in rates.items()}


def compute_spectra_from_flux_file(snowglobes, flux_name, xs_dir, edges, mass_kt,
                                   native_width=0.2):
    """Binned rates for a solar model we only have as a SNOwGLoBES flux file.

    Each native 0.2 MeV bin spans [c - w/2, c + w/2]; its content is split
    across the output bins in proportion to the overlap, which assumes the flux
    is uniform inside a native bin. Coarser than the fine-grid path (line
    components are already smeared over their native bin) but it avoids an
    offset between the two binnings.
    """
    centres, rates = _rates_from_flux_file(
        Path(snowglobes) / "fluxes" / f"{flux_name}.dat", xs_dir, mass_kt)
    lo, hi = centres - native_width / 2, centres + native_width / 2

    out = {}
    for channel, rate in rates.items():
        binned = np.zeros(len(edges) - 1)
        for i, (a, b) in enumerate(zip(edges[:-1], edges[1:])):
            overlap = np.clip(np.minimum(hi, b) - np.maximum(lo, a), 0, None) / native_width
            binned[i] = float((rate * overlap).sum())
        out[channel] = binned
    return out


# --------------------------------------------------------------------------- output

def build_dataframe(spectra, centres, threshold, mass_kt, config, name,
                    solar_model, flux_name, bin_width):
    exposure_unit = "kt-year" if mass_kt == 1.0 else f"{mass_kt:g} kt-year"
    rows = []
    for model in CC_MODELS:
        components = {
            "Solar": spectra[f"CC/{model}"] + spectra["ES"] + spectra["NC"],
            "CC": spectra[f"CC/{model}"],
            "ES": spectra["ES"],
            "NC": spectra["NC"],
        }
        for component, counts in components.items():
            rows.append(
                {
                    "Config": config,
                    "Name": name,
                    "Folder": "snowglobes",
                    "Component": component,
                    "Stage": "Truth",
                    "XSecModel": model,
                    "SolarModel": solar_model,
                    "Flux": flux_name,
                    "Threshold": threshold,
                    "BinWidth": bin_width,
                    "EnergyUnit": "MeV",
                    "CountsUnit": f"events / MeV / {exposure_unit}",
                    "Exposure": 1.0,
                    "ExposureUnit": exposure_unit,
                    "Energy": list(centres),
                    "Counts": list(counts / bin_width),
                }
            )
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--snowglobes", default=os.environ.get(
        "SNOWGLOBES", "/home/smanthey/Code/GLoBES/snowglobes"),
        help="Path to the SNOwGLoBES installation (default: $SNOWGLOBES)")
    parser.add_argument("--spectra", default=None,
                        help="Pickled per-component solar spectra "
                             "(default: input/data/Solar_Neutrino_Spectrum.pkl)")
    parser.add_argument("--flux", default="solar_b16gs98_mixed",
                        help="Flux file stem inside <snowglobes>/fluxes, used for P_ee(E) "
                             "and --check (default: solar_b16gs98_mixed)")
    parser.add_argument("--solar-model", dest="solar_model", default=None,
                        help="'Plot' value selected from --spectra and the label written "
                             "to the SolarModel column (default: inferred from --flux)")
    parser.add_argument("--emin", type=float, default=0.0, help="First bin edge in MeV")
    parser.add_argument("--emax", type=float, default=30.0, help="Last bin edge in MeV")
    parser.add_argument("--bin-width", dest="bin_width", type=float, default=1.0,
                        help="Output bin width in MeV (default: 1.0)")
    parser.add_argument("--threshold", type=float, default=1.0,
                        help="Neutrino-energy threshold in MeV recorded in the Threshold "
                             "column and used for the printed integrals (default: 1.0)")
    parser.add_argument("--mass", type=float, default=1.0,
                        help="Exposure in kt used for the count normalisation, so the "
                             "default emits events per kt-year")
    parser.add_argument("--config", default=None,
                        help="Config tag in the filename (default: lar_<flux tag>)")
    parser.add_argument("--name", default="snowglobes", help="Name tag in the filename")
    parser.add_argument("--datafile", default="SolarInteractions_Cutflow",
                        help="Datafile stem, i.e. the value passed to --datafile")
    parser.add_argument("--outdir", default=None,
                        help="Output directory (default: input/data/snowglobes)")
    parser.add_argument("--method", choices=["fine", "fluxfile"], default=None,
                        help="fine: fold the per-component spectra on a fine grid "
                             "(exact bin edges and line energies). fluxfile: fold the "
                             "0.2 MeV SNOwGLoBES flux file and redistribute by overlap, "
                             "for models with no component spectra. Default: fine when "
                             "--spectra has the model, otherwise fluxfile.")
    parser.add_argument("--check", action="store_true",
                        help="Also print the integrals recomputed off the 0.2 MeV "
                             "SNOwGLoBES flux file")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    flux_tag = args.flux.replace("solar_", "").replace("_mixed", "")
    if args.solar_model is None:
        args.solar_model = {"b16gs98": "B16-GS98", "bs05op": "BS05(OP)"}.get(flux_tag, flux_tag)
    if args.config is None:
        args.config = f"lar_{flux_tag}"
    spectra_path = Path(args.spectra) if args.spectra else \
        repo / "input" / "data" / "Solar_Neutrino_Spectrum.pkl"
    outdir = Path(args.outdir) if args.outdir else repo / "input" / "data" / "snowglobes"
    outdir.mkdir(parents=True, exist_ok=True)

    edges = np.arange(args.emin, args.emax + args.bin_width / 2, args.bin_width)
    centres = (edges[:-1] + edges[1:]) / 2
    snowglobes = Path(args.snowglobes)
    reference = snowglobes / "fluxes" / f"{args.flux}.dat"

    method = args.method
    if method is None:
        available = set(pickle.load(open(spectra_path, "rb"))["Plot"].unique())
        method = "fine" if args.solar_model in available else "fluxfile"
        if method == "fluxfile":
            print(f"No component spectra for {args.solar_model!r} in "
                  f"{spectra_path.name}; folding {args.flux}.dat instead.")

    if method == "fine":
        spectra = compute_spectra(spectra_path, args.solar_model, reference,
                                  snowglobes / "xscns", edges, args.mass)
    else:
        spectra = compute_spectra_from_flux_file(snowglobes, args.flux,
                                                 snowglobes / "xscns", edges, args.mass)
    df = build_dataframe(spectra, centres, args.threshold, args.mass, args.config,
                         args.name, args.solar_model, args.flux, args.bin_width)
    df["Method"] = method

    bare = df.copy()
    bare["Config"] = None
    bare["Name"] = None
    for path, frame in [(outdir / f"{args.config}_{args.name}_{args.datafile}.pkl", df),
                        (outdir / f"{args.datafile}.pkl", bare)]:
        with path.open("wb") as handle:
            pickle.dump(frame, handle)
        print(f"Wrote {path}")

    unit = "kt-year" if args.mass == 1.0 else f"{args.mass:g} kt-year"
    keep = centres >= args.threshold
    print(f"\n{args.solar_model}, E_nu > {args.threshold} MeV, events / {unit}:")
    for channel in ["ES", "NC"] + [f"CC/{m}" for m in CC_MODELS]:
        print(f"  {channel:12s} {spectra[channel][keep].sum():12.6g}")

    if args.check:
        print(f"\ncross-check off {args.flux}.dat (0.2 MeV bins, centres >= threshold):")
        ref = check_against_flux_file(args.snowglobes, args.flux, args.threshold, args.mass)
        for channel in ["ES", "NC"] + [f"CC/{m}" for m in CC_MODELS]:
            fine = spectra[channel][keep].sum()
            print(f"  {channel:12s} {ref[channel]:12.6g}  vs fine {fine:12.6g}"
                  f"   ratio {fine / ref[channel]:.4f}")


if __name__ == "__main__":
    main()
