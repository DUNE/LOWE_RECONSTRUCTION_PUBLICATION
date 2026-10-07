#!/usr/bin/env python3
"""Build the ROC and threshold-scan curves of the SolarEnergy signal/background classifier.

Input is the held-out score export of SOLAR ``src/physics/calibration/03b_signal_background.py``
(``{config}_marley_final_Signal_Background_Discriminant.pkl``: one row per Population x Label with the
score array of the clusters with reconstructed Energy >= MIN_ENERGY, each scored by the fold model
that did not see it, and the analysis Threshold).

Files written next to the input (input/data/workflow/discrimination/):
  {config}_{name}_Signal_Background_ROC.pkl
      one row per Population x background Label: SignalEfficiency and BackgroundEfficiency (%) at a
      grid of score thresholds (quantiles of all scores plus the working point), AUC and its
      bootstrap standard deviation AUCError, and the working point (Threshold, WPSignalEfficiency,
      WPBackgroundEfficiency).
  {config}_{name}_Signal_Background_Threshold_Scan.pkl
      one row per Population x Label (CC Neutrino and backgrounds): signal-like fraction (%) versus
      the score threshold (Values).
  {config}_{name}_Signal_Background_WorkingPoint.json
      Threshold and the signal-like fraction per Label (All population), read by --panel_vertical_file.

Example:
    python3 scripts/generate_signal_background_curves.py --configs hd_1x2x6_centralAPA hd_1x2x6_lateralAPA \
        vd_1x8x14_3view_30deg_nominal vd_1x8x14_3view_30deg_shielded
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[1]
SIGNAL = "CC Neutrino"


def auc(s, x):
    """Mann-Whitney AUC: probability that a signal cluster scores above a background cluster (ties 1/2)."""
    r = rankdata(np.r_[s, x])
    return (r[: len(s)].sum() - len(s) * (len(s) + 1) / 2) / (len(s) * len(x))


def pass_fraction(scores, thresholds):
    """Percentage of `scores` >= each threshold."""
    srt = np.sort(scores)
    return 100 * (1 - np.searchsorted(srt, thresholds, side="left") / len(srt))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--configs", nargs="+", required=True)
    parser.add_argument("--name", default="marley_final")
    parser.add_argument("--path", default="input/data/workflow/discrimination")
    parser.add_argument("--n_points", type=int, default=2000, help="Score quantiles used as ROC thresholds")
    parser.add_argument("--n_bootstrap", type=int, default=50)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    base = ROOT / args.path
    for config in args.configs:
        disc = pd.read_pickle(base / f"{config}_{args.name}_Signal_Background_Discriminant.pkl")
        common = disc[["Geometry", "Config", "Name"]].iloc[0].to_dict()
        roc_rows, scan_rows, wp = [], [], {}
        for population, d in disc.groupby("Population", sort=False):
            d = d.set_index("Label")
            thr = float(d["Threshold"].iloc[0])
            sig = np.asarray(d.loc[SIGNAL, "Discriminant"], dtype=float)
            grid = np.unique(np.r_[np.quantile(np.concatenate([np.asarray(v, float) for v in d["Discriminant"]]),
                                               np.linspace(0, 1, args.n_points)), thr, np.inf])
            sig_eff = pass_fraction(sig, grid)
            for label in d.index:
                scores = np.asarray(d.loc[label, "Discriminant"], dtype=float)
                values = np.linspace(0, 1, 201)
                scan_rows.append({**common, "Population": population, "Label": label, "Variable": "Threshold",
                                  "Values": values, "Efficiency": pass_fraction(scores, values), "Threshold": thr})
                if population == "All":
                    wp[label] = float(np.mean(scores >= thr)) * 100
                if label == SIGNAL or len(scores) == 0:
                    continue
                boot = [auc(sig[rng.integers(0, len(sig), len(sig))], scores[rng.integers(0, len(scores), len(scores))])
                        for _ in range(args.n_bootstrap)]
                roc_rows.append({**common, "Population": population, "Label": label,
                                 "SignalEfficiency": sig_eff, "BackgroundEfficiency": pass_fraction(scores, grid),
                                 "AUC": auc(sig, scores), "AUCError": float(np.std(boot)), "Clusters": len(scores),
                                 "Threshold": thr, "WPSignalEfficiency": float(np.mean(sig >= thr)) * 100,
                                 "WPBackgroundEfficiency": float(np.mean(scores >= thr)) * 100})
            if population == "All":
                wp["Threshold"] = thr
        pd.DataFrame(roc_rows).to_pickle(base / f"{config}_{args.name}_Signal_Background_ROC.pkl")
        pd.DataFrame(scan_rows).to_pickle(base / f"{config}_{args.name}_Signal_Background_Threshold_Scan.pkl")
        with open(base / f"{config}_{args.name}_Signal_Background_WorkingPoint.json", "w") as f:
            json.dump(wp, f, indent=2)
        print(config, json.dumps(wp))
        print(pd.DataFrame(roc_rows)[["Population", "Label", "AUC", "AUCError", "WPSignalEfficiency", "WPBackgroundEfficiency"]]
              .to_string(index=False))


if __name__ == "__main__":
    main()
