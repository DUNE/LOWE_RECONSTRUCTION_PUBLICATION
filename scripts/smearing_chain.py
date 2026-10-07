#!/usr/bin/env python3
"""
Primary-cluster energy smearing chain (SOLAR output/data/TPC/smearing/, synced with
``scripts/sync_solar_data.sh --smearing`` into input/data/TPC/smearing/).

SOLAR decomposes the reconstructed primary-cluster energy (SolarEnergy) into steps,
each swapping one truth ingredient for its reco counterpart:

    TrueEnergy -> Charge -> PileUp -> Lifetime -> Gain -> Calibration -> Offset -> Map

Every primary cluster enters (no cuts, no fiducial volume, no smoothing). This
script reads the *_final productions: "full" (analysis weights) and, for gamma,
the unweighted true 9.5-10.5 MeV slice "true9.5-10.5_unweighted".

Plots (--plots, default):
  1. <config>_<name>_full:       step overlay of the unit-area spectrum, linear + log
  2. <config>_gamma_final_slice: the same for the 10 MeV gamma slice
  3. <config>_<step>_samples:    the four samples at one step, unit area, linear + log
  4. <config>_cutflow:           absolute counts per stage and sample (combined Chain_Cutflow)
Tables (--tables): LaTeX (siunitx) + CSV, see write_tables().

Run through the registries:  python run_plot_scripts.py -s smearing
                             python run_table_scripts.py -s smearing
"""

from _bootstrap import ensure_src_path

ensure_src_path()

import json
import os
from pathlib import Path

from rich import print as rprint

from lib import *
from lib.exports import save_figure_to_paths, save_table_to_paths
from lib.plot import apply_legend_style, create_common_subplots, add_centered_suptitle

DATA_DIR = Path(__file__).resolve().parents[1] / "input" / "data" / "TPC" / "smearing"
DEFAULT_PLOT_DIR = str(Path(__file__).resolve().parents[1] / "output" / "plots" / "smearing")
DEFAULT_TABLE_DIR = str(Path(__file__).resolve().parents[1] / "output" / "tables" / "smearing")

CONFIGS = [
    "hd_1x2x6_centralAPA",
    "hd_1x2x6_lateralAPA",
    "vd_1x8x14_3view_30deg_nominal",
    "vd_1x8x14_3view_30deg_shielded",
]
import lib as _lib

CONFIG_LABELS = _lib._MAPPINGS.get("config", {})
CONFIG_MACROS = {
    "hd_1x2x6_centralAPA": r"\cfgHDCentral",
    "hd_1x2x6_lateralAPA": r"\cfgHDLateral",
    "vd_1x8x14_3view_30deg_nominal": r"\cfgVDTop",
    "vd_1x8x14_3view_30deg_shielded": r"\cfgVDShielded",
}
SAMPLES = ["marley_final", "gamma_final", "neutron_final", "radiological_final"]
SAMPLE_LABELS = {"marley_final": "CC Neutrino", "gamma_final": "Gamma", "neutron_final": "Neutron", "radiological_final": "Radiological"}
SAMPLE_COLORS = {  # as the analysis cutflows (daynight_component_color): DUNE colour cycle
    "marley_final": "C0",
    "gamma_final": "C2",
    "neutron_final": "C4",
    "radiological_final": "C3",
}
SLICE = "true9.5-10.5_unweighted"

STEPS = ["TrueEnergy", "Charge", "PileUp", "Lifetime", "Gain", "Calibration", "Offset", "Map"]
STEP_LABELS = {
    "TrueEnergy": "True energy",
    "Charge": "Charge response",
    "PileUp": "Pile-up",
    "Lifetime": "Lifetime correction",
    "Gain": "Hit-dependent conversion",
    "Calibration": "Electron calibration",
    "Offset": "Discriminant offset",
    "Map": "SolarEnergy",
}
# Steps in the order of the DUNE colour cycle (C0..C7), as in plot_params smearing_step_color.
STEP_COLORS = {
    "TrueEnergy": "C0",
    "Charge": "C1",
    "PileUp": "C2",
    "Lifetime": "C3",
    "Gain": "C4",
    "Calibration": "C5",
    "Offset": "C6",
    "Map": "C7",
}
FLASH_CATEGORIES = ["NoFlash", "WrongFlash", "CorrectFlash"]
FLASH_LABELS = {"NoFlash": "No flash", "WrongFlash": "Wrong flash", "CorrectFlash": "Correct flash"}
LOG_DECADES = 6

parser = argparse.ArgumentParser(description="Plots and tables of the SOLAR energy smearing chain")
parser.add_argument("--tables", action="store_true", help="Write the tables instead of the plots")
parser.add_argument("--configs", nargs="+", default=CONFIGS, help="Detector configurations")
parser.add_argument("-o", "--output", nargs="+", default=None, help="Output directories")
parser.add_argument("-p", "--plot", action="store_true", help="Show the plots")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()


# --- Loaders -----------------------------------------------------------------------
def _sample_dir(config, name, sample="full"):
    return DATA_DIR / config / name / sample


def load_pkl(config, name, kind, sample="full"):
    """kind: SolarEnergy_Chain_Cutflow, Chain_Spectra, Chain_Endpoint, Chain_Counterfactuals, Chain_Response."""
    path = _sample_dir(config, name, sample) / f"{config}_{name}_{kind}.pkl"
    if not path.exists():
        rprint(f"[yellow]Missing:[/yellow] {path}")
        return None
    return pd.read_pickle(path)


def load_summary(config, name, sample="full"):
    path = _sample_dir(config, name, sample) / f"{config}_{name}_Chain_Summary.json"
    if not path.exists():
        rprint(f"[yellow]Missing:[/yellow] {path}")
        return None
    with open(path) as f:
        return json.load(f)


def load_combined_cutflow(config):
    path = DATA_DIR / config / "samples" / "full" / f"{config}_SolarEnergy_Chain_Cutflow.pkl"
    return pd.read_pickle(path) if path.exists() else None


def _spectrum(df, step):
    """Bin centres, unit-area density and bin width of one step of a Chain_Spectra frame."""
    row = df[df["Step"] == step].iloc[0]
    bins = np.asarray(row["Bins"], dtype=float)
    density = np.asarray(row["Density"], dtype=float)
    width = np.median(np.diff(bins)) if len(bins) > 1 else 1.0
    return bins, density, width


# --- Plot helpers ------------------------------------------------------------------
def _step_hist(ax, centres, values, width, **kwargs):
    edges = np.append(centres - width / 2, centres[-1] + width / 2)
    ax.stairs(values, edges, **kwargs)


def _finish_panels(axes, curves, reference_curves, xlim, xlabel, ylabel, endpoint=None):
    """Linear panel up to the tallest reference curve (a truth spike may go off-scale),
    log panel from the smallest positive value to the peak, at most LOG_DECADES decades."""
    lin, log = axes
    peak_ref = max((np.nanmax(v) for v in reference_curves if len(v)), default=1.0)
    peak_all = max((np.nanmax(v) for v in curves if len(v)), default=1.0)
    positive = np.concatenate([v[v > 0] for v in curves if np.any(v > 0)])
    floor = max(positive.min() if len(positive) else peak_all * 10 ** -LOG_DECADES, peak_all * 10 ** -LOG_DECADES)
    lin.set_ylim(0, 1.1 * peak_ref)
    log.set_yscale("log")
    log.set_ylim(floor, 2 * peak_all)
    for ax in axes:
        ax.set_xlim(*xlim)
        ax.set_xlabel(xlabel, fontsize=xlabelfontsize)
        if endpoint is not None:
            ax.axvline(endpoint, color="grey", linestyle="--", linewidth=1.5)
    lin.set_ylabel(ylabel, fontsize=ylabelfontsize)


def _figure_legend(fig, axes, title, ncol=4):
    """Legend below the panels, so it never hides a spectrum."""
    handles, labels = list(axes)[0].get_legend_handles_labels()
    width, height = fig.get_size_inches()
    extra = 0.45 * np.ceil(len(labels) / ncol) + 0.3
    fig.set_size_inches(width, height + extra)
    fig.subplots_adjust(bottom=(fig.subplotpars.bottom * height + extra) / (height + extra),
                        top=1 - (1 - fig.subplotpars.top) * height / (height + extra))
    fig.legend(handles, labels, loc="lower center", ncol=ncol, frameon=False,
               fontsize=legendfontsize, title=title, title_fontsize=legendtitlefontsize)


def _save(fig, name):
    if args.plot:
        plt.show()
    for ext in ("png", "pdf"):
        save_figure_to_paths(fig, args.output or [DEFAULT_PLOT_DIR], f"{name}.{ext}", DEFAULT_PLOT_DIR, rprint_func=rprint)
    plt.close(fig)


def plot_step_overlay(config, name, sample, xlim):
    spectra = load_pkl(config, name, "Chain_Spectra", sample)
    summary = load_summary(config, name, sample)
    if spectra is None or summary is None:
        return
    fig, axes = create_common_subplots(ncols=2)
    curves, reference = [], []
    for step in STEPS:
        if step not in set(spectra["Step"]):
            continue
        centres, density, width = _spectrum(spectra, step)
        truth = step == "TrueEnergy"
        style = dict(
            color=STEP_COLORS[step],
            linestyle=":" if truth else ("--" if step == "PileUp" else "-"),
            linewidth=default_linewidth * (1.5 if step == "Map" else 1),
            label=STEP_LABELS[step],
        )
        for ax in axes:
            _step_hist(ax, centres, density, width, **style)
        curves.append(density)
        if not truth:
            reference.append(density)
    endpoint = summary.get("endpoint_mev")
    _finish_panels(axes, curves, reference, xlim, "Reconstructed Energy (MeV)", "Density (MeV$^{-1}$)", endpoint)
    _figure_legend(fig, axes, "Stage")
    suffix = "10 MeV" if sample == SLICE else "All Clusters"
    add_centered_suptitle(fig, f"{CONFIG_LABELS.get(config, config)} Energy Smearing Chain - {SAMPLE_LABELS[name]} ({suffix})", fontsize=titlefontsize)
    tag = "slice" if sample == SLICE else "full"
    _save(fig, f"smearing_chain_{config.lower()}_{name}_{tag}_steps")


def plot_samples_at_step(config, step):
    fig, axes = create_common_subplots(ncols=2)
    curves = []
    for name in SAMPLES:
        spectra = load_pkl(config, name, "Chain_Spectra")
        if spectra is None or step not in set(spectra["Step"]):
            continue
        centres, density, width = _spectrum(spectra, step)
        for ax in axes:
            _step_hist(ax, centres, density, width, color=SAMPLE_COLORS[name],
                       linewidth=default_linewidth, label=SAMPLE_LABELS[name])
        curves.append(density)
    if not curves:
        plt.close(fig)
        return
    _finish_panels(axes, curves, curves, (0, 30), "Reconstructed Energy (MeV)", "Density (MeV$^{-1}$)")
    _figure_legend(fig, axes, "Sample")
    add_centered_suptitle(fig, f"{CONFIG_LABELS.get(config, config)} Energy Smearing Chain - {STEP_LABELS[step]}", fontsize=titlefontsize)
    _save(fig, f"smearing_chain_{config.lower()}_{step.lower()}_samples")


def plot_absolute_cutflow(config):
    """Absolute cutflow-style view (events/MeV/20 yr) of every sample and stage; the
    SolarEnergy stage equals the "Raw" stage of the analysis cutflow plots."""
    df = load_combined_cutflow(config)
    if df is None:
        return
    fig, axes = create_common_subplots(nrows=2, ncols=2, sharex=True)
    for ax, component in zip(axes.flat, df["Component"].drop_duplicates()):
        part = df[df["Component"] == component]
        peak = np.nanmax([np.nanmax(np.asarray(c, dtype=float)) for c in part["Counts"]])
        for step in STEPS:
            row = part[part["Step"] == step]
            if row.empty:
                continue
            row = row.iloc[0]
            centres = np.asarray(row["Energy"], dtype=float)
            _step_hist(ax, centres, np.asarray(row["Counts"], dtype=float), 1.0,
                       color=STEP_COLORS[step],
                       linestyle=":" if step == "TrueEnergy" else ("--" if step == "PileUp" else "-"),
                       linewidth=default_linewidth, label=STEP_LABELS[step])
        label = SAMPLE_LABELS.get(component, "CC Neutrino" if component == "Solar" else component)
        ax.set_title(label, fontsize=subtitlefontsize)
        ax.set_yscale("log")
        ax.set_ylim(peak * 10 ** -LOG_DECADES, 5 * peak)
        ax.set_xlim(0, 30)
    for ax in axes[-1]:
        ax.set_xlabel("Reconstructed Energy (MeV)", fontsize=xsublabelfontsize)
    for ax in axes[:, 0]:
        ax.set_ylabel("Counts (events / MeV / 20 yr)", fontsize=ysublabelfontsize)
    fig.subplots_adjust(hspace=0.3)
    _figure_legend(fig, axes.flat, "Stage")
    _save(fig, f"smearing_chain_{config.lower()}_cutflow")


# --- Tables ------------------------------------------------------------------------
def _pct(value, digits=2):
    """A fraction as a percentage for siunitx: two significant figures, scientific
    notation below 0.01 % (a plain 0.000015 would be unreadable)."""
    if value is None or not np.isfinite(value):
        return "---"
    pct = 100 * value
    if pct == 0:
        return "\\num{0}"
    if abs(pct) < 1e-2:
        return f"\\num{{{pct:.1e}}}"
    return f"\\num{{{np.format_float_positional(float(f'{pct:.{digits}g}'), trim='-')}}}"


def _write(df_tex, df_csv, name, header_lines, column_format):
    def write_tex(path):
        with open(path, "w") as f:
            f.write(f"\\begin{{tabular}}{{{column_format}}}\n\\toprule\n")
            for line in header_lines:
                f.write(line + " \\\\\n")
            f.write("\\midrule\n")
            for row in df_tex:
                if row == ["\\addlinespace"]:
                    f.write("\\addlinespace\n")
                    continue
                f.write(" & ".join(row) + " \\\\\n")
            f.write("\\bottomrule\n\\end{tabular}\n")

    save_table_to_paths(write_tex, args.output or [DEFAULT_TABLE_DIR], f"{name}.tex", DEFAULT_TABLE_DIR, rprint_func=rprint)
    save_table_to_paths(lambda p: df_csv.to_csv(p, index=False), args.output or [DEFAULT_TABLE_DIR], f"{name}.csv",
                        DEFAULT_TABLE_DIR, rprint_func=rprint)


def table_endpoint(sample, name_out, endpoint_label):
    """A/B: gamma share of weight above the endpoint after each stage (one column per
    configuration), and the flash category of the clusters above it after the
    electron calibration and after SolarEnergy."""
    steps = STEPS[1:]
    endpoints = {}
    for config in args.configs:
        e = load_pkl(config, "gamma_final", "Chain_Endpoint", sample)
        if e is not None:
            endpoints[config] = e.set_index("Step")
    configs = list(endpoints)
    rows_tex = [["\\multicolumn{%d}{l}{\\textit{Share above %s after each stage (\\%%)}}" % (len(configs) + 1, endpoint_label)]]
    rows_tex += [[STEP_LABELS[step], *[_pct(endpoints[c].loc[step, "FracAboveEndpoint"]) for c in configs]]
                 for step in steps]
    for step in ("Calibration", "Map"):
        rows_tex.append(["\\midrule\n\\multicolumn{%d}{l}{\\textit{Flash category above %s, after %s (\\%%)}}"
                         % (len(configs) + 1, endpoint_label, STEP_LABELS[step].lower() if step != "Map" else "SolarEnergy")])
        for cat in FLASH_CATEGORIES:
            rows_tex.append([FLASH_LABELS[cat], *[_pct(endpoints[c].loc[step, f"AboveShare{cat}"]) for c in configs]])
    rows_csv = pd.DataFrame([
        {"Config": c, "Step": step, **endpoints[c].loc[step, ["FracAboveEndpoint", *[f"AboveShare{k}" for k in FLASH_CATEGORIES]]].to_dict()}
        for c in configs for step in steps
    ])
    header = ["Stage & " + " & ".join(CONFIG_MACROS[c] for c in configs)]
    _write(rows_tex, rows_csv, name_out, header, "l" + "c" * len(configs))


def table_counterfactuals():
    """C: gamma share above the 14 MeV endpoint with one effect restored to truth."""
    names = ["NoPileUp", "TrueLifetime", "FlatGain"]
    labels = {"NoPileUp": "No pile-up", "TrueLifetime": "True drift time", "FlatGain": "Flat conversion"}
    rows_tex, rows_csv = [], []
    for config in args.configs:
        c = load_pkl(config, "gamma_final", "Chain_Counterfactuals")
        if c is None:
            continue
        c = c.set_index("Counterfactual")
        ref = c["ReferenceFracAboveEndpoint"].iloc[0]
        vals = [c.loc[n, "FracAboveEndpoint"] for n in names]
        rows_tex.append([CONFIG_MACROS[config], _pct(ref), *[_pct(v) for v in vals]])
        rows_csv.append({"Config": config, "Reference": ref, **dict(zip(names, vals))})
    header = [
        " & & \\multicolumn{3}{c}{Restored to truth} \\\\\n\\cmidrule(lr){3-5}\n"
        "Configuration & Electron calibration (\\%) & " + " & ".join(f"{labels[n]} (\\%)" for n in names)
    ]
    _write(rows_tex, pd.DataFrame(rows_csv), "smearing_chain_gamma_counterfactuals", header, "lcccc")


def table_flash_categories():
    """D: flash-matching category per config x sample and the lifetime-correction
    ratio (median, 1st-99th percentile) per category."""
    rows_tex, rows_csv = [], []
    for config in args.configs:
        for i, name in enumerate(SAMPLES):
            s = load_summary(config, name)
            if s is None:
                continue
            cats = s["flash_categories"]
            ratio = s["lifetime_ratio_p01_p50_p99"]
            cells = [CONFIG_MACROS[config] if i == 0 else "", SAMPLE_LABELS[name]]
            cells += [_pct(cats[c]) for c in FLASH_CATEGORIES]
            cells += [f"\\num{{{ratio[c][1]:.2f}}} (\\numrange{{{ratio[c][0]:.2f}}}{{{ratio[c][2]:.2f}}})"
                      for c in FLASH_CATEGORIES]
            rows_tex.append(cells)
            rows_csv.append({"Config": config, "Name": name, **cats,
                             **{f"LifetimeRatio_{c}_{p}": ratio[c][k]
                                for c in FLASH_CATEGORIES for k, p in enumerate(("P01", "P50", "P99"))}})
        rows_tex.append(["\\addlinespace"])
    rows_tex = rows_tex[:-1]
    header = [
        " & & \\multicolumn{3}{c}{Flash category (\\%)} & \\multicolumn{3}{c}{Lifetime-correction ratio} \\\\\n"
        "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\n"
        "Configuration & Sample & " + " & ".join(FLASH_LABELS[c] for c in FLASH_CATEGORIES)
        + " & " + " & ".join(FLASH_LABELS[c] for c in FLASH_CATEGORIES)
    ]
    _write(rows_tex, pd.DataFrame(rows_csv), "smearing_chain_flash_categories", header, "llcccccc")


def table_charge_response():
    """E: Charge-step response E_step/E_true: peak mean and width, 99th percentile."""
    rows_tex, rows_csv = [], []
    for config in args.configs:
        cells = [CONFIG_MACROS[config]]
        for name in SAMPLES:
            r = load_pkl(config, name, "Chain_Response")
            if r is None:
                cells += ["---", "---"]
                continue
            r = r.set_index("Step").loc["Charge"]
            cells += [f"\\num{{{r['PeakMean']:.2f}}} (\\num{{{r['PeakSigma']:.2f}}})", f"\\num{{{r['P99']:.2f}}}"]
            rows_csv.append({"Config": config, "Name": name, "PeakMean": r["PeakMean"],
                             "PeakSigma": r["PeakSigma"], "P99": r["P99"], "Median": r["Median"]})
        rows_tex.append(cells)
    header = [
        " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{SAMPLE_LABELS[n]}}}" for n in SAMPLES) + " \\\\\n"
        + "".join(f"\\cmidrule(lr){{{2 + 2 * k}-{3 + 2 * k}}}" for k in range(len(SAMPLES))) + "\n"
        "Configuration" + " & Peak (width) & P99" * len(SAMPLES)
    ]
    _write(rows_tex, pd.DataFrame(rows_csv), "smearing_chain_charge_response", header, "l" + "cc" * len(SAMPLES))


def write_tables():
    table_endpoint("full", "smearing_chain_gamma_endpoint_full", "\\qty{14}{\\mega\\electronvolt}")
    table_endpoint(SLICE, "smearing_chain_gamma_endpoint_slice", "\\qty{10.5}{\\mega\\electronvolt}")
    table_counterfactuals()
    table_flash_categories()
    table_charge_response()


def write_plots():
    for config in args.configs:
        for name in SAMPLES:
            plot_step_overlay(config, name, "full", (0, 30))
        plot_step_overlay(config, "gamma_final", SLICE, (0, 20))
        for step in STEPS:
            plot_samples_at_step(config, step)
        plot_absolute_cutflow(config)


if __name__ == "__main__":
    write_tables() if args.tables else write_plots()
