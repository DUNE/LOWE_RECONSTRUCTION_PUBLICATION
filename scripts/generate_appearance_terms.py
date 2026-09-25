#!/usr/bin/env python3
"""Generate DUNE appearance-probability terms as a plotting pickle.

The output follows the series-table convention consumed by
``script_compare_configuration.py``. For example:

    python3 scripts/script_compare_configuration.py \
        --datafile appearance_terms_1300km --iterable Term \
        -x Energy -y Contribution --plot_type line
"""

import argparse
from pathlib import Path
import pickle

import numpy as np
import pandas as pd


# NuFIT 6.1, normal ordering; values also used in tables/pmns_bestfit.tex.
TH12 = np.arcsin(np.sqrt(0.3088))
TH13 = np.arcsin(np.sqrt(0.02249))
TH23 = np.arcsin(np.sqrt(0.470))
DM21 = 7.537e-5  # eV^2
DM31 = 2.521e-3  # eV^2
DCP = -np.pi / 2

BASELINE_KM = 1300.0
AVERAGE_DENSITY = 2.85  # g/cm^3


def phases(energy, dcp=DCP, anti=False):
    """Return dimensionless oscillation phases and matter term."""
    d31 = 1.267 * DM31 * BASELINE_KM / energy
    d21 = 1.267 * DM21 * BASELINE_KM / energy
    aL = (BASELINE_KM / 3500.0) * (AVERAGE_DENSITY / 3.0)
    if anti:
        aL = -aL
        dcp = -dcp
    return d31, d21, aL, dcp


def terms(energy, anti=False):
    """Return atmospheric, interference, and solar contributions."""
    d31, d21, aL, dcp = phases(energy, anti=anti)
    t1 = (
        np.sin(TH23) ** 2
        * np.sin(2 * TH13) ** 2
        * np.sin(d31 - aL) ** 2
        / (d31 - aL) ** 2
        * d31**2
    )
    t2 = (
        np.sin(2 * TH23)
        * np.sin(2 * TH13)
        * np.sin(2 * TH12)
        * np.sin(d31 - aL)
        / (d31 - aL)
        * d31
        * np.sin(aL)
        / aL
        * d21
        * np.cos(d31 + dcp)
    )
    t3 = (
        np.cos(TH23) ** 2
        * np.sin(2 * TH12) ** 2
        * np.sin(aL) ** 2
        / aL**2
        * d21**2
    )
    return t1, t2, t3


def build_table(energy, anti=False):
    t1, t2, t3 = terms(energy, anti=anti)
    contributions = {
        "P(nu_mu->nu_e)": t1 + t2 + t3,
        "T1 (atmospheric)": t1,
        "T2 (interference)": t2,
        "T3 (solar)": t3,
    }

    rows = [
        {
            "Config": "appearance_terms",
            "Name": "nu_mu_to_nu_e",
            "Term": term_name,
            "Energy": energy,
            "Contribution": values,
        }
        for term_name, values in contributions.items()
    ]
    return pd.DataFrame(rows)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    default_output = (
        Path(__file__).resolve().parents[1]
        / "input"
        / "data"
        / "theory"
        / "appearance_terms_1300km.pkl"
    )
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--energy-min", type=float, default=0.5)
    parser.add_argument("--energy-max", type=float, default=8.0)
    parser.add_argument("--points", type=int, default=3000)
    parser.add_argument("--anti", action="store_true", help="Generate antineutrino terms")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.points < 2:
        raise ValueError("--points must be at least 2")
    if args.energy_min <= 0 or args.energy_max <= args.energy_min:
        raise ValueError("Require 0 < --energy-min < --energy-max")

    energy = np.geomspace(args.energy_min, args.energy_max, args.points)
    table = build_table(energy, anti=args.anti)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as output_file:
        pickle.dump(table, output_file, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"wrote {args.output} ({len(table)} rows)")


if __name__ == "__main__":
    main()