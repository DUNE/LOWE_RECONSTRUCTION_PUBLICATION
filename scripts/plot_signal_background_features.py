#!/usr/bin/env python3
"""Plot the four highest-importance inputs of each final-sample SB classifier.

Uses the pre-binned, unweighted cluster distributions exported by SOLAR's
03c_signal_background_features.py. Rank and importance come from the same
export, so each configuration selects its own top four automatically.
"""

from _bootstrap import ensure_src_path

ensure_src_path()

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lib import _MAPPINGS


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "input/data/workflow/discrimination"
DEFAULT_OUTPUT = ROOT / "output/plots/reco"
CONFIGS = (
    "hd_1x2x6_centralAPA",
    "hd_1x2x6_lateralAPA",
    "vd_1x8x14_3view_30deg_nominal",
    "vd_1x8x14_3view_30deg_shielded",
)
SAMPLES = ("CC Neutrino", "Gamma", "Neutron", "Radiological")
LABELS = {
    "Energy": "Primary-cluster energy (MeV)",
    "SelectedEnergy": "Selected energy (MeV)",
    "TotalEnergy": "Total energy (MeV)",
    "NHits": "Primary-cluster TPC hits",
    "AdjClNum": "Adjacent clusters",
    "MatchedOpFlashNHits": "Matched-flash optical hits",
}
TITLES = {
    "Energy": "Primary energy",
    "SelectedEnergy": "Selected energy",
    "TotalEnergy": "Total energy",
    "NHits": "TPC hit count",
    "AdjClNum": "Adjacent-cluster count",
    "MatchedOpFlashNHits": "Optical-hit count",
}


def bin_edges(centres):
    centres = np.asarray(centres, dtype=float)
    if len(centres) < 2 or not np.all(np.diff(centres) > 0):
        raise ValueError("Feature histogram needs at least two ordered bin centres")
    mids = (centres[:-1] + centres[1:]) / 2
    return np.r_[centres[0] - (mids[0] - centres[0]), mids,
                 centres[-1] + (centres[-1] - mids[-1])]


def plot_config(config, name, region, output):
    path = DATA_DIR / f"{config}_{name}_Signal_Background_Features.pkl"
    data = pd.read_pickle(path)
    data = data[data["Region"] == region]
    if data.empty:
        raise ValueError(f"No {region} feature distributions in {path}")
    leaders = (data[["Feature", "Rank", "Importance"]].drop_duplicates()
               .sort_values("Rank").head(4))
    if len(leaders) != 4 or list(leaders["Rank"]) != [1, 2, 3, 4]:
        raise ValueError(f"Expected four ranked features in {path}")

    colors = _MAPPINGS["sb_sample_color"]
    config_label = _MAPPINGS.get("config", {}).get(config, config)
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.0))
    for ax, leader in zip(axes.flat, leaders.itertuples(index=False)):
        feature = leader.Feature
        frame = data[data["Feature"] == feature].set_index("Label")
        if set(frame.index) != set(SAMPLES):
            raise ValueError(f"Unexpected samples for {config}/{feature}: {list(frame.index)}")
        reference = np.asarray(frame.loc[SAMPLES[0], "Bins"], dtype=float)
        edges = bin_edges(reference)
        for sample in SAMPLES:
            row = frame.loc[sample]
            centres = np.asarray(row["Bins"], dtype=float)
            density = np.asarray(row["Density"], dtype=float)
            if len(density) != len(reference) or not np.array_equal(centres, reference):
                raise ValueError(f"Incompatible bins for {config}/{feature}/{sample}")
            ax.stairs(density, edges, color=colors[sample], linewidth=2,
                      label=sample)
        ax.set_title(f"{TITLES.get(feature, feature)} (#{leader.Rank}, {100 * leader.Importance:.1f}%)",
                     fontsize=14, pad=8)
        ax.set_xlabel(LABELS.get(feature, feature), fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.tick_params(labelsize=10)
        ax.set_yscale("log")
        ax.set_xlim(edges[0], edges[-1])
        ax.grid(axis="y", alpha=0.2)
        if bool(frame.loc[SAMPLES[0], "Unmatched"]):
            ax.axvspan(edges[0], edges[1], color="grey", alpha=0.12)
            ax.text(edges[0] + 0.5 * (edges[1] - edges[0]), 0.94,
                    "no flash", rotation=90, va="top", ha="center",
                    fontsize=8, transform=ax.get_xaxis_transform())
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False,
               fontsize=12)
    fig.suptitle(f"{config_label}: signal/background classifier inputs ({region.lower()} clusters)",
                 fontsize=17)
    fig.tight_layout(rect=(0.02, 0.06, 0.98, 0.94), h_pad=2.2, w_pad=1.5)
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"signal_background_top4_features_{config.lower()}_{name}_{region.lower()}.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    print(f"{target}: {', '.join(leaders['Feature'])}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configs", nargs="+", default=CONFIGS)
    parser.add_argument("--name", default="marley_final")
    parser.add_argument("--region", choices=("All", "Window"), default="All")
    parser.add_argument("-o", "--output", nargs="+", type=Path, default=[DEFAULT_OUTPUT])
    args = parser.parse_args()
    for config in args.configs:
        for output in args.output:
            plot_config(config, args.name, args.region, output)


if __name__ == "__main__":
    main()
