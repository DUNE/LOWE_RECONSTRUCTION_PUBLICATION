#!/usr/bin/env python3
"""Solar-neutrino interaction rates in liquid argon (thesis table tab:solar_spectra_lar), with SNUfish.

The rates are those of the solar Phase I paper (SNUfish scripts/dune_phase1_rates.py: B16-GS98 8B + hep, SOLAR's
oscillation parameters, night at SURF with night share 0.507, annual, per kt-yr, CC model ar40_marley1_allowed =
DUNE's MARLEY v1 samples, no detector response), evaluated on the thesis grid of thresholds: true neutrino energy
E_nu > 5, 8, 10, 15 MeV (CC, ES, NC) and electron kinetic energy T_e > 5, 8, 10, 15 MeV (CC, ES; NC has no
electron). It replaces the SNOwGLoBES table of scripts/generate_snowglobes_solar_interactions.py.

Run with SNUfish's environment, from a clean checkout of SNUfish main (its commit is written into the table):

    ~/Code/snufish/.venv/bin/python scripts/snufish_solar_rates_table.py [--snufish ~/Code/snufish]

Writes output/tables/solar_rates_lar_b16gs98_snufish_table.tex (copy it to THESIS/tables/).
"""

import argparse
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = (5.0, 8.0, 10.0, 15.0)
CHANNELS = {"Enu": ("CC", "ES", "NC"), "Te": ("CC", "ES")}


def number(value):
    """\\num{} with three significant figures, as the SNOwGLoBES table it replaces ('---' below 1e-3)."""
    return f"\\num{{{significant(value)}}}" if value >= 1e-3 else "---"


def significant(value, digits=3):
    decimals = max(0, digits - 1 - math.floor(math.log10(value)))
    return f"{float(f'{value:.{digits}g}'):.{decimals}f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--snufish", type=Path,
                        default=Path(os.environ.get("SNUFISH_ROOT", Path.home() / "Code" / "snufish")))
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "tables" / "solar_rates_lar_b16gs98_snufish_table.tex")
    args = parser.parse_args()
    snufish = args.snufish.expanduser().resolve()
    os.environ.setdefault("SNUFISH_ROOT", str(snufish))
    sys.path.insert(0, str(snufish / "scripts"))
    import dune_phase1_rates as paper  # noqa: E402  (SNUfish's own script: same settings as the paper)

    paper.CUTS = [(c, axis, t) for t in THRESHOLDS for axis, channels in CHANNELS.items() for c in channels]
    values = {key: v["annual"] for key, v in paper.rates().items()}

    rows = []
    for t in THRESHOLDS:
        cells = [number(values[c, axis, t]) for axis, channels in CHANNELS.items() for c in channels]
        rows.append(f"$>$\\qty{{{t:g}}}{{\\mega\\electronvolt}} & " + " & ".join(cells) + " & --- \\\\\n")
    header = (f"% Written by LOWE_RECONSTRUCTION_PUBLICATION scripts/snufish_solar_rates_table.py with SNUfish "
              f"{paper.__version__} ({paper.commit()}): do not edit.\n"
              f"% Annual rates per kt-yr of liquid argon, the settings of SNUfish scripts/dune_phase1_rates.py "
              f"(the solar Phase I paper), CC model {paper.CC_MODEL}.\n")
    table = (header + "\\begin{tabular}{lcccccc}\n\\toprule\n"
             "Threshold & \\multicolumn{3}{c}{Neutrino energy $E_\\nu$} & \\multicolumn{3}{c}{Electron energy $T_e$} \\\\\n"
             " & CC & ES & NC & CC & ES & NC \\\\\n\\midrule\n" + "".join(rows) + "\\bottomrule\n\\end{tabular}\n")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(table)
    print(table, end="")
    print(f"Wrote {args.out}\n\n% THESIS references/metrics/main.tex (\\fomSolar<Nu|Te><Channel><Threshold>):")
    words = {5.0: "Five", 8.0: "Eight", 10.0: "Ten", 15.0: "Fifteen"}
    for axis, prefix in (("Enu", "Nu"), ("Te", "Te")):
        for c in CHANNELS[axis]:
            for t in THRESHOLDS:
                value = values[c, axis, t]
                text = significant(value) if value >= 1e-3 else "<0.01"
                print(f"\\newcommand{{\\fomSolar{prefix}{c}{words[t]}}}{{\\num{{{text}}}\\xspace}}")


if __name__ == "__main__":
    main()
