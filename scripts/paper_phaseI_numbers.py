#!/usr/bin/env python3
"""Derive the numbers quoted in the solar Phase I paper from the SOLAR outputs, in the paper conventions,
and write them as LaTeX macros.

Usage:  <python with numpy and pandas> LOWE_RECONSTRUCTION_PUBLICATION/scripts/paper_phaseI_numbers.py [DATA_DIR] [-o output/tables/phaseI_numbers.tex] [--check]

DATA_DIR holds the {config}_marley_* pickles (default: the synced reference results, truncated/default).

Paper conventions (they differ from the thesis, see thesis_agent_prompt.md and exposure_to_macros.py):
  * three samples: HD Central, HD Lateral and VD; the VD sample is the nominal (unshielded) VD Top
    configuration, entered twice for the full VD module (two drift volumes);
  * the HD module starts HD_DELAY years after the VD, so the HD curves are shifted by HD_DELAY;
    times are calendar years;
  * combination = quadrature sum of the significances, sqrt(Z_HDc(t-1)^2 + Z_HDl(t-1)^2 + 2 Z_VD(t)^2);
  * Day-Night curve: smoothed Asimov; HEP curve: smoothed profile likelihood (as the paper figures);
  * hep flux precision: 1 / Z_combined at 10 years (paper method, Gaussian assumption);
  * oscillation: sqrt of the summed Delta chi^2 of the solar fit at the reactor point (VD twice);
  * per-year counts and S/B: last stage of the cut flow (SolarEnergy_*_Cutflow.pkl, SmoothedCounts, the source
    of the paper's Tab. I and appendix tables) in the paper windows, divided by the 20-year exposure, VD x2.
    Each window is checked against the smoothed analysis spectra (*_Counts.pkl) to 1e-3; the script stops on
    a mismatch (the cut flows before the SOLAR-sb 6b320d4 re-export had external rates 12.57x too high).

Macro names: \\pap<Qty>, letters only. With --check the values are compared with the macros of the paper's
figuresOfMerit.tex (PAPER_DIR) and the script exits non-zero on a mismatch.
"""
import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LOWE = Path(__file__).resolve().parents[1]
DEFAULT_DATA = LOWE / "input" / "data" / "studies" / "truncated" / "default"
PAPER = Path(os.environ.get("PAPER_DIR", Path.home() / "Documents" / "solar_neutrinos_phaseI_paper"))
CFG = {"HDc": "hd_1x2x6_centralAPA", "HDl": "hd_1x2x6_lateralAPA", "VD": "vd_1x8x14_3view_30deg_nominal"}
ANA = {"DN": ("DayNight", "Asimov"), "HEP": ("HEP", "ProfileLikelihood")}
WINDOW = {"DN": (11.0, 15.0), "HEP": (15.0, 20.0)}
HD_DELAY = 1.0
VD_WEIGHT = 2
REF_EXPOSURE = 20.0
REACTOR = (0.304, 7.54e-5)  # sin^2 theta_12, Delta m^2_21 [eV^2]
GRID = np.linspace(0.0, 30.0, 30001)


def curve(data, cfg, ana):
    name, var = ANA[ana]
    df = pd.read_pickle(data / f"{CFG[cfg]}_marley_{name}_Exposure.pkl")
    row = df[(df.Variable == var) & (df.SpectrumType == "Smoothed")]
    if len(row) != 1:
        sys.exit(f"expected one {var}/Smoothed curve in {CFG[cfg]} {name}, found {len(row)}")
    row = row.iloc[0]
    x = np.concatenate([[0.0], np.asarray(row.Exposure, float)])
    y = np.concatenate([[0.0], np.asarray(row.Significance, float)])
    return lambda t: np.interp(t, x, y)


def combined(data, ana, configs=("HDc", "HDl", "VD")):
    c = {k: curve(data, k, ana) for k in configs}
    z2 = np.zeros_like(GRID)
    for k, f in c.items():
        if k == "VD":
            z2 += VD_WEIGHT * f(GRID) ** 2
        else:
            z2 += f(np.clip(GRID - HD_DELAY, 0.0, None)) ** 2
    return np.sqrt(z2), c


def crossing(z, level):
    idx = np.argmax(z >= level)
    return float(GRID[idx]) if z[idx] >= level else float("nan")


def at(z, t):
    return float(np.interp(t, GRID, z))


def reactor_dchi2(data, cfg, kind):
    df = pd.read_pickle(data / f"{CFG[cfg]}_marley_{kind}.pkl")
    row = df[(df.Label == "solar") & (df.Variable == "sin12")].iloc[0]
    dm2, sin12 = np.asarray(row.Dm2, float), np.asarray(row.Values, float)
    grid = np.asarray(row.Significance, float)  # Delta chi^2 of the solar fit, (Dm2, sin12)
    return float(grid[np.argmin(abs(dm2 - REACTOR[1])), np.argmin(abs(sin12 - REACTOR[0]))])


def window_counts(data, cfg, ana):
    """{Solar | 8B, hep, gamma, neutron, radiological: smoothed counts in the window} from the last cut-flow stage,
    each checked against the analysis spectra (*_Counts.pkl)."""
    name = ANA[ana][0]
    lo, hi = WINDOW[ana]
    out = {}
    for sample in ("marley", "gamma", "neutron", "radiological"):
        df = pd.read_pickle(data / f"{CFG[cfg]}_{sample}_SolarEnergy_{name}_Cutflow.pkl")
        for _, r in df[df.Stage == "NHits+OpHits+AdjCl"].iterrows():
            if r.Component in ("Solar Day", "Solar Night"):
                continue
            e = np.asarray(r.Energy, float)
            out[r.Component] = float(np.asarray(r.SmoothedCounts, float)[(e >= lo) & (e < hi)].sum())
    ref = pd.read_pickle(data / f"{CFG[cfg]}_marley_{name}_Counts.pkl")
    for _, r in ref[ref.SpectrumType == "Smoothed"].iterrows():
        if r.Component in ("Solar Day", "Solar Night"):
            continue
        e = np.asarray(r.Energy, float)
        quoted = float(np.asarray(r.Counts, float)[(e >= lo) & (e < hi)].sum())
        mine = out.get(r.Component, out.get(str(r.Component).lower()))
        if mine is None or abs(mine - quoted) > 1e-3 * max(abs(quoted), 1e-12):
            sys.exit(f"{CFG[cfg]} {name} {r.Component}: cut flow {mine} vs analysis spectra {quoted} in {lo}-{hi} MeV")
    return out


def derive(data):
    m = {}
    for ana in ANA:
        z, c = combined(data, ana)
        zc, _ = combined(data, ana, ("HDc",))
        m[f"{ana}CombThreeSigmaYr"] = crossing(z, 3)
        m[f"{ana}CombFiveSigmaYr"] = crossing(z, 5)
        m[f"{ana}HDcThreeSigmaYr"] = crossing(zc, 3)
        m[f"{ana}HDcFiveSigmaYr"] = crossing(zc, 5)
        m[f"{ana}CombAtTen"] = at(z, 10)
        m[f"{ana}CombAtTwenty"] = at(z, REF_EXPOSURE)
    m["DNTimeSavingYr"] = m["DNHDcThreeSigmaYr"] - m["DNCombThreeSigmaYr"]
    m["HEPTimeSavingYr"] = m["HEPHDcFiveSigmaYr"] - m["HEPCombFiveSigmaYr"]
    m["HEPFluxPrecisionTenPercent"] = 100.0 / m["HEPCombAtTen"]
    for kind, tag in (("Sensitivity_Contours", "Thirty"), ("Sensitivity_10Y_Contours", "Ten")):
        d2 = sum((VD_WEIGHT if k == "VD" else 1) * reactor_dchi2(data, k, kind) for k in CFG)
        m[f"SensReactorSep{tag}"] = float(np.sqrt(d2))
    dn = {k: window_counts(data, k, "DN") for k in CFG}
    hep = window_counts(data, "HDc", "HEP")
    bkg = lambda d: sum(v for k, v in d.items() if k.lower() in ("gamma", "neutron", "radiological"))
    m["DNHDcSB"] = dn["HDc"]["Solar"] / bkg(dn["HDc"])
    m["HEPHDcSB"] = (hep["8B"] + hep["hep"]) / bkg(hep)
    m["HEPHDcSBhepOnly"] = hep["hep"] / (hep["8B"] + bkg(hep))
    m["DNHDcSignalPerYear"] = dn["HDc"]["Solar"] / REF_EXPOSURE
    m["DNHDcBackgroundPerYear"] = bkg(dn["HDc"]) / REF_EXPOSURE
    m["DNSelectedSignalPerYearHD"] = (dn["HDc"]["Solar"] + dn["HDl"]["Solar"]) / REF_EXPOSURE
    m["DNSelectedSignalPerYearVD"] = VD_WEIGHT * dn["VD"]["Solar"] / REF_EXPOSURE
    m["HEPHDcEightBPerYear"] = hep["8B"] / REF_EXPOSURE
    m["HEPHDcSignalPerYear"] = hep["hep"] / REF_EXPOSURE
    m["HEPHDcBackgroundPerYear"] = bkg(hep) / REF_EXPOSURE
    return m


# paper macro -> (derived key, decimals) for --check
# Not checked: the hep flux precision (the paper quotes the thesis Fisher-information value, not 1/Z) and the
# window-integrated S/B and per-year counts, which the paper dropped on 2026-11-19 (still written as \pap macros).
CHECK = {
    "fomDayNightThreeSigmaYears": ("DNCombThreeSigmaYr", 1),
    "fomDayNightThreeSigmaYearsHDCentralOnly": ("DNHDcThreeSigmaYr", 1),
    "fomDayNightFiveSigmaYears": ("DNCombFiveSigmaYr", 1),
    "fomDayNightLateralVDTimeSavingYears": ("DNTimeSavingYr", 1),
    "fomDayNightTwentyYearSigma": ("DNCombAtTwenty", 1),
    "fomHepThreeSigmaYears": ("HEPCombThreeSigmaYr", 1),
    "fomHepFiveSigmaYears": ("HEPCombFiveSigmaYr", 1),
    "fomHepLateralVDTimeSavingYears": ("HEPTimeSavingYr", 1),
    "fomHepTwentyYearSigma": ("HEPCombAtTwenty", 1),
    "fomSensPhaseIReactorSeparation": ("SensReactorSepThirty", 1),
    "fomSensPhaseIReactorSeparationTenYear": ("SensReactorSepTen", 1),
}


def paper_value(text, name):
    m = re.search(r"\\newcommand\{\\" + name + r"\}\{(.*)\}", text)
    if not m:
        return None
    num = re.search(r"[-+]?\d+(?:\.\d+)?", re.sub(r"\\new\{|\\rev\{", "", m.group(1)))
    return float(num.group(0)) if num else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?", type=Path, default=DEFAULT_DATA)
    ap.add_argument("-o", "--output", type=Path, default=LOWE / "output" / "tables" / "phaseI_numbers.tex")
    ap.add_argument("--check", action="store_true", help="compare with the paper's figuresOfMerit.tex")
    args = ap.parse_args()

    m = derive(args.data)
    lines = ["% AUTO-GENERATED by LOWE_RECONSTRUCTION_PUBLICATION/scripts/paper_phaseI_numbers.py -- do not edit by hand.",
             f"% Source : {args.data}",
             "% Paper conventions: HD Central, HD Lateral, VD nominal x2; HD starts 1 yr after VD; 11-15 / 15-20 MeV."]
    for k, v in m.items():
        lines.append(f"\\newcommand{{\\pap{k}}}{{{v:.4g}}}")
        print(f"{k:32s} {v:.4g}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n")
    print(f"written {args.output}")

    if args.check:
        text = (PAPER / "figuresOfMerit.tex").read_text()
        bad = 0
        for name, (key, dec) in CHECK.items():
            quoted = paper_value(text, name)
            ok = quoted is not None and abs(round(m[key], dec) - quoted) < 1.01 * 10 ** (-dec)
            bad += not ok
            print(f"{'ok ' if ok else 'BAD'} {name:42s} paper {quoted}  derived {m[key]:.{dec}f}")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
