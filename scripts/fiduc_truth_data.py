#!/usr/bin/env python3
"""Turn the truth-position export (pickles) into LaTeX macros and table fragments.

Usage:
    python3 LOWE_RECONSTRUCTION_PUBLICATION/scripts/fiduc_truth_data.py DATA_DIR [-o results/fiduc_truth_macros.tex]
            [--tables-dir results/fiduc_truth] [--status results/study_status_*.md]
            [--inventory] [--lowe-data LOWE/input/data]

DATA_DIR holds the export written by SOLAR's truth_position_study.py (LOWE schema):
``{config}_all_{Kind}.pkl`` for the four configurations, plus ``meta.json``.  The pickles were
written with numpy 2, so run the script with an interpreter that has numpy>=2 and pandas
(for example LOWE_RECONSTRUCTION_PUBLICATION/.venv/bin/python).

Outputs
  * results/fiduc_truth_macros.tex   event-level numbers as \\ft... macros (see the header)
  * results/fiduc_truth/*.tex        tabular fragments (no caption) for the chapter
  * results/fiduc_truth/report.md    pickle inventory, cross-checks against the status file and
                                     against the reference values quoted in the writing brief

Significances (Day-Night, HEP, Sensitivity) are NOT written here: they come from the status-file
macros (LOWE_RECONSTRUCTION_PUBLICATION/scripts/status_to_macros.py).  The pickle significances are only cross-checked.
"""
import argparse
import os
import glob
import json
import sys
from pathlib import Path

import pandas as pd

# Thesis repository (outputs go to its results/ and tables/); override with THESIS_DIR.
ROOT = Path(os.environ.get("THESIS_DIR", Path.home() / "Code" / "THESIS"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import status_to_macros as sm  # noqa: E402

CFG = {"hd_1x2x6_centralAPA": "HDc", "hd_1x2x6_lateralAPA": "HDl",
       "vd_1x8x14_3view_30deg_nominal": "VDn", "vd_1x8x14_3view_30deg_shielded": "VDs"}
CFG_NAME = {"HDc": r"\cfgHDCentral", "HDl": r"\cfgHDLateral",
            "VDn": r"\cfgVDTop", "VDs": r"\VD Shielded"}
ANA = {"DayNight": "DN", "HEP": "HEP", "Sensitivity": "Sens"}
ANA_NAME = {"DN": "Day-Night", "HEP": r"\emph{hep}", "Sens": "Sensitivity"}
SAMPLE = {"marley": "Sig", "gamma": "G", "neutron": "N", "radiological": "R"}
SEL = {"reco fiducial": "Reco", "truth pipeline": "Truth", "no fiducial": "None"}
STAGE = {"window": "Win", "+ analysis cut": "Cut", "+ cut + reco fiducial": "Fid"}
FACE = {"X low": "Xlow", "X high": "Xhigh", "Y": "Y", "Z": "Z"}
XSEL = {"window": "Win", "after_cut": "Cut"}
MODE = {"reco": "Reco", "truth": "Truth", "xR": "XR", "xT": "XT", "xTnc": "XTnc"}
KINDS = ["BackgroundSplit", "BestFoM", "Cuts", "FaceComposition", "FiducialVolumes", "FlashMismatch",
         "PassFractions", "ResidualSummary", "Residuals", "ResidualsWide", "ScanCurves", "ScanGrid",
         "ShellRatio", "SignalRecovered", "Significance", "SurvivorEvents", "SurvivorStatistics",
         "WallCdf", "XEntryHist", "XEntrySummary"]
BRIEF_TOL = 0.06  # relative; the brief's reference values are rounded to two or three figures


def load(data_dir):
    frames = {}
    for kind in KINDS:
        files = sorted(glob.glob(str(data_dir / f"*_all_{kind}.pkl")))
        if not files:
            sys.exit(f"missing pickles for kind {kind} in {data_dir}")
        df = pd.concat([pd.read_pickle(f) for f in files], ignore_index=True)
        df["cfg"] = df["Config"].map(CFG)
        df["ana"] = df["Analysis"].map(ANA)
        frames[kind] = df
    return frames


# ------------------------------------------------------------------ number formatting
def num(x, sig=3):
    """siunitx \\num of x with ``sig`` significant figures (scientific from 1e4)."""
    x = float(x)
    if x == 0:
        return r"\num{0}"
    if abs(x) >= 1e4:
        m, e = f"{x:.{sig - 1}e}".split("e")
        return rf"\num{{{m.rstrip('0').rstrip('.')}e{int(e)}}}"
    s = f"{x:.{sig}g}"
    return rf"\num{{{s if 'e' not in s else f'{x:.0f}'}}}"


def pct(frac, dec=None):
    v = float(frac) * 100
    if dec is None:
        dec = 2 if 99.9 <= v < 100 else 1 if (v >= 90 or v < 1) else 0
    return rf"\SI{{{v:.{dec}f}}}{{\percent}}"


def pct1(frac):
    return pct(frac, 1)


def cm(x):
    x = float(x)
    dec = 2 if abs(x) < 1 else 1 if abs(x) < 100 else 0
    return rf"\SI{{{x:.{dec}f}}}{{\centi\meter}}"


class Macros:
    def __init__(self):
        self.lines, self.values = [], {}

    def add(self, name, body, raw=None):
        assert name[2:].isalpha(), name
        self.lines.append(rf"\newcommand{{\{name}}}{{{body}\xspace}}")
        if raw is not None:
            self.values[name] = float(raw)

    def comment(self, text):
        self.lines += ["", f"% === {text} ==="]


def build_macros(F):
    M = Macros()

    M.lines.append(r"\newcommand{\ftScope}{raw \texttt{SignalParticleWeight} (no oscillation weighting, MC-support gate or smoothing), "
                   r"\SIrange{10}{20}{\mega\electronvolt}, Truncated background folder, default best cut of each analysis\xspace}")
    M.comment("BackgroundSplit: total background at the analysis cut (raw weights, no MC-support gate)")
    for _, r in F["BackgroundSplit"].iterrows():
        p = f"ftBS{r.cfg}{r.ana}{SEL[r.Selection]}"
        M.add(p + "GN", num(r.SumWGammaNeutron), r.SumWGammaNeutron)
        M.add(p + "Rad", num(r.SumWRadiological), r.SumWRadiological)
        M.add(p + "RadShare", pct(r.RadiologicalFraction), 100 * r.RadiologicalFraction)
        M.add(p + "GNMC", rf"\num{{{int(r.NMCGammaNeutron)}}}", r.NMCGammaNeutron)
        M.add(p + "RadMC", rf"\num{{{int(r.NMCRadiological)}}}", r.NMCRadiological)

    M.comment("XEntrySummary: |RecoX - truth X| within 100 cm of the entry X face(s); Win = window, Cut = after cut")
    for _, r in F["XEntrySummary"].iterrows():
        p = f"ftXE{r.cfg}{r.ana}{SAMPLE[r['Sample']]}{XSEL[r.Selection]}"
        M.add(p + "Median", cm(r.MedianAbsDX), r.MedianAbsDX)
        M.add(p + "AboveHundred", pct(r.FractionDXAbove100cm), 100 * r.FractionDXAbove100cm)
        M.add(p + "AboveThirty", pct(r.FractionDXAbove30cm), 100 * r.FractionDXAbove30cm)
        M.add(p + "Edge", pct(r.FractionRecoXAtEdge, 1), 100 * r.FractionRecoXAtEdge)
        M.add(p + "MC", rf"\num{{{int(r.NMC)}}}", r.NMC)

    M.comment("FlashMismatch: window sample (10-20 MeV, no cut), whole volume")
    for _, r in F["FlashMismatch"].iterrows():
        p = f"ftFM{r.cfg}{r.ana}{SAMPLE[r['Sample']]}"
        M.add(p + "DxHundred", pct(r.FractionDXAboveDriftTol, 0), 100 * r.FractionDXAboveDriftTol)
        M.add(p + "Edge", pct(r.FractionRecoXAtEdge, 1), 100 * r.FractionRecoXAtEdge)
        M.add(p + "MC", rf"\num{{{int(r.NMC)}}}", r.NMC)

    M.comment("ResidualSummary: reco - truth X, window sample")
    for _, r in F["ResidualSummary"].iterrows():
        if r.Variable != "X":
            continue
        p = f"ftRS{r.cfg}{r.ana}{SAMPLE[r['Sample']]}"
        M.add(p + "Median", cm(abs(r.Median)), abs(r.Median))
        M.add(p + "BeyondHundredFifty", pct(r.FractionBeyond150cm, 0), 100 * r.FractionBeyond150cm)

    M.comment("FaceComposition: weight share per entry face; Win = window, Cut = + analysis cut, Fid = + cut + reco fiducial")
    for _, r in F["FaceComposition"].iterrows():
        p = f"ftFC{r.cfg}{r.ana}{SAMPLE[r['Sample']]}{STAGE[r.Stage]}{FACE[r.Face]}"
        M.add(p, pct(r.WeightFraction, 0 if r.WeightFraction * 100 >= 1 and r.WeightFraction < 0.999 else 1), 100 * r.WeightFraction)
    for (cfg, ana, smp, stg), g in F["FaceComposition"].groupby(["cfg", "ana", "Sample", "Stage"]):
        M.add(f"ftFC{cfg}{ana}{SAMPLE[smp]}{STAGE[stg]}MC", rf"\num{{{int(g.NMC.iloc[0])}}}", g.NMC.iloc[0])

    M.comment("BestFoM, X-only scan, each estimator at its own best X (Y = Z = 0 fiducial); Fom = S/sqrt(B), gamma+neutron only")
    b = F["BestFoM"]
    for _, r in b[b.Scan == "X only"].iterrows():
        p = f"ftFoM{r.cfg}{r.ana}{MODE[r.Mode]}"
        M.add(p + "Fom", num(r.FoM, 2), r.FoM)
        M.add(p + "Eff", pct1(r.SignalEfficiency), 100 * r.SignalEfficiency)
        M.add(p + "GN", num(r.SumWGammaNeutron), r.SumWGammaNeutron)
        M.add(p + "X", rf"\SI{{{r.FiducialX:.0f}}}{{\centi\meter}}", r.FiducialX)

    M.comment("SurvivorStatistics: MC events at the analysis cut and reco fiducial")
    for _, r in F["SurvivorStatistics"].iterrows():
        M.add(f"ftSS{r.cfg}{r.ana}{SAMPLE[r['Sample']]}MC", rf"\num{{{int(r.NMCRecoFiducial)}}}", r.NMCRecoFiducial)
        M.add(f"ftSS{r.cfg}{r.ana}{SAMPLE[r['Sample']]}TruthMC", rf"\num{{{int(r.NMCTruthPipeline)}}}", r.NMCTruthPipeline)
        M.add(f"ftSS{r.cfg}{r.ana}{SAMPLE[r['Sample']]}Gain",
              rf"\SI[retain-explicit-plus]{{{100 * (r.NMCTruthPipeline / r.NMCRecoFiducial - 1):+.0f}}}{{\percent}}",
              100 * (r.NMCTruthPipeline / r.NMCRecoFiducial - 1))

    M.comment("Ranges quoted in the text")
    for k, (v, body) in ranges(F).items():
        M.add("ftR" + k, body, v)
    return M


def ranges(F):
    out = {}

    def span(name, series, fmt):
        out[name + "Min"] = (series.min(), fmt(series.min()))
        out[name + "Max"] = (series.max(), fmt(series.max()))

    bs = F["BackgroundSplit"]
    reco = bs[bs.Selection == "reco fiducial"]
    vd, hdl = reco[reco.cfg.isin(["VDn", "VDs"])], reco[reco.cfg == "HDl"]
    span("RadShareVD", vd.RadiologicalFraction, lambda v: pct(v))
    span("RadShareHDl", hdl.RadiologicalFraction, lambda v: pct(v, 0))
    span("RadShareHDc", reco[reco.cfg == "HDc"].RadiologicalFraction, lambda v: pct(v, 0))
    span("RadMCVD", vd.NMCRadiological, lambda v: rf"\num{{{int(v)}}}")
    xs = F["XEntrySummary"]
    xs = xs[(xs.ana == "DN") & xs.cfg.isin(["VDn", "VDs"])]
    span("VDAboveCut", xs[xs.Selection == "after_cut"].FractionDXAbove100cm, lambda v: pct(v, 0))
    span("VDAboveWin", xs[xs.Selection == "window"].FractionDXAbove100cm, lambda v: pct(v, 0))
    span("VDNeutronMC", xs[(xs.Selection == "after_cut") & (xs.Sample == "neutron")].NMC, lambda v: rf"\num{{{int(v)}}}")
    b = F["BestFoM"]
    b = b[(b.Scan == "X only") & b.cfg.isin(["VDn", "VDs"])]
    piv = b.pivot_table(index=["ana", "cfg"], columns="Mode", values=["SignalEfficiency", "SumWGammaNeutron"])
    d = pd.DataFrame({"dEff": 100 * (piv[("SignalEfficiency", "xT")] - piv[("SignalEfficiency", "reco")]),
                      "fGN": piv[("SumWGammaNeutron", "reco")] / piv[("SumWGammaNeutron", "xT")]})
    sub = d[d.index.get_level_values("ana").isin(["DN", "Sens"])]
    span("VDDNSensEffGain", sub.dEff, lambda v: rf"\num{{{v:.1f}}}")
    span("VDDNSensGNFactor", sub.fGN, lambda v: rf"\num{{{v:.1f}}}")
    sub = d[d.index.get_level_values("ana") == "HEP"]
    span("VDHEPEffLoss", -sub.dEff, lambda v: rf"\num{{{v:.1f}}}")
    span("VDHEPGNFactor", sub.fGN, lambda v: rf"\num{{{v:.1f}}}")
    xe = F["XEntrySummary"]
    xe = xe[(xe.ana == "DN") & xe.cfg.isin(["HDl", "VDn", "VDs"])]
    out["EdgeMax"] = (100 * xe.FractionRecoXAtEdge.max(), pct(xe.FractionRecoXAtEdge.max(), 0))
    fc = F["FaceComposition"]
    fc = fc[(fc.ana == "DN") & (fc.Stage == "+ cut + reco fiducial") & (fc.Face == "Z") & fc.Sample.isin(["gamma", "neutron"])]
    fc = fc[fc.NMC >= 5]
    out["ZFaceMax"] = (100 * fc.WeightFraction.max(), pct(fc.WeightFraction.max(), 0))
    x = F["BestFoM"]
    x = x[(x.Scan == "X only") & (x.cfg == "HDl") & (x.ana == "DN")].set_index("Mode")
    out["HDlDNEffGain"] = (100 * (x.loc["xT"].SignalEfficiency - x.loc["reco"].SignalEfficiency),
                           rf"\num{{{100 * (x.loc['xT'].SignalEfficiency - x.loc['reco'].SignalEfficiency):.1f}}}")
    ch = 100 * (x.loc["xT"].SumWGammaNeutron / x.loc["reco"].SumWGammaNeutron - 1)
    out["HDlDNGNChange"] = (ch, rf"\SI{{{ch:.0f}}}{{\percent}}")
    return out


# ------------------------------------------------------------------ tables
def tab_signal_bkg(F):
    b = F["BestFoM"]
    b = b[b.Scan == "X only"]
    rows = []
    for code in ("DN", "Sens", "HEP"):
        for cfg in ("VDn", "VDs", "HDl"):
            g = b[(b.ana == code) & (b.cfg == cfg)].set_index("Mode")
            r, t = g.loc["reco"], g.loc["xT"]
            rows.append(rf"    {ANA_NAME[code]} & {CFG_NAME[cfg]} & {pct1(r.SignalEfficiency)} & {num(r.SumWGammaNeutron)} & "
                        rf"\SI{{{r.FiducialX:.0f}}}{{\centi\meter}} & {pct1(t.SignalEfficiency)} & {num(t.SumWGammaNeutron)} & "
                        rf"\SI{{{t.FiducialX:.0f}}}{{\centi\meter}} \\")
        rows.append(r"    \midrule")
    head = ("\\begin{tabular}{llrrrrrr}\n    \\toprule\n"
            "    & & \\multicolumn{3}{c}{reco $X$} & \\multicolumn{3}{c}{truth $X$} \\\\\n"
            "    \\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\n"
            "    Analysis & Configuration & Signal eff. & $\\gamma{+}n$ weight & $X$ cut & Signal eff. & $\\gamma{+}n$ weight & $X$ cut \\\\\n    \\midrule\n")
    return head + "\n".join(rows[:-1]) + "\n    \\bottomrule\n\\end{tabular}\n"


def tab_radiological(F):
    bs = F["BackgroundSplit"]
    bs = bs[bs.Selection == "reco fiducial"]
    rows = []
    for ana in ("DN", "HEP", "Sens"):
        for cfg in ("VDn", "VDs", "HDl", "HDc"):
            r = bs[(bs.ana == ana) & (bs.cfg == cfg)].iloc[0]
            rows.append(rf"    {ANA_NAME[ana]} & {CFG_NAME[cfg]} & {num(r.SumWGammaNeutron)} & {num(r.SumWRadiological)} & "
                        rf"{pct(r.RadiologicalFraction)} & \num{{{int(r.NMCRadiological)}}} \\")
        rows.append(r"    \midrule")
    head = ("\\begin{tabular}{llrrrr}\n    \\toprule\n"
            "    Analysis & Configuration & $\\gamma{+}n$ weight & Radiological weight & Radiological share & Radiological MC events \\\\\n    \\midrule\n")
    return head + "\n".join(rows[:-1]) + "\n    \\bottomrule\n\\end{tabular}\n"


def tab_dx(F):
    x = F["XEntrySummary"]
    x = x[(x.ana == "DN") & (x.Selection == "after_cut")]
    rows = []
    for cfg in ("HDl", "VDn", "VDs"):
        for smp in ("gamma", "neutron"):
            g = x[(x.cfg == cfg) & (x.Sample == smp)]
            if g.empty:
                continue
            r = g.iloc[0]
            rows.append(rf"    {CFG_NAME[cfg]} & {smp.capitalize()} & \num{{{int(r.NMC)}}} & {cm(r.MedianAbsDX)} & "
                        rf"{pct(r.FractionDXAbove100cm)} & {pct(r.FractionRecoXAtEdge, 1)} \\")
    head = ("\\begin{tabular}{llrrrr}\n    \\toprule\n"
            "    Configuration & Sample & MC events & Median $|\\Delta X|$ & $|\\Delta X|>\\SI{100}{\\centi\\meter}$ & RecoX at edge \\\\\n    \\midrule\n")
    return head + "\n".join(rows) + "\n    \\bottomrule\n\\end{tabular}\n"


# ------------------------------------------------------------------ inventory and checks
def inventory(F, data_dir, meta):
    w = meta.get("energy_window_mev", ["?", "?"])
    L = ["# fiduc_truth data report", "", f"Data directory: `{data_dir}`", "",
         f"Export generated {meta.get('generated')} from SOLAR revision {meta.get('git_head')} (`{meta.get('script')}`).",
         f"Scope: folder {meta.get('folder')}, {meta.get('energy_variable')}, {w[0]}-{w[1]} MeV, "
         f"default best cut of each analysis; weights: {meta.get('weights')}.", "",
         "Truth-position keys: " + ", ".join(f"{k}: {v}" for k, v in meta.get("truth_position_keys", {}).items()), "",
         "Notes from the export: " + " ".join(meta.get("notes", [])), "",
         "## Pickle inventory (rows over the four configurations; columns; units)", ""]
    for kind, df in F.items():
        cols = [c for c in df.columns if c not in ("cfg", "ana", "Geometry", "Name", "Study")]
        units = [f"{c}={df[c].iloc[0]}" for c in df.columns if c.endswith("Unit")]
        L.append(f"- **{kind}** ({len(df)} rows): {', '.join(cols)}" + (f"; units: {', '.join(units)}" if units else ""))
    return L


BRIEF_CHECKS = [
    ("VD nominal Day-Night reco X: signal eff (%)", "ftFoMVDnDNRecoEff", 93.9),
    ("VD nominal Day-Night reco X: gamma+n weight", "ftFoMVDnDNRecoGN", 895),
    ("VD nominal Day-Night truth X: signal eff (%)", "ftFoMVDnDNXTEff", 96.4),
    ("VD nominal Day-Night truth X: gamma+n weight", "ftFoMVDnDNXTGN", 138),
    ("VD shielded Day-Night reco X: gamma+n weight", "ftFoMVDsDNRecoGN", 65),
    ("VD shielded Day-Night truth X: gamma+n weight", "ftFoMVDsDNXTGN", 19),
    ("VD nominal Sensitivity reco X: signal eff (%)", "ftFoMVDnSensRecoEff", 80.0),
    ("VD nominal Sensitivity reco X: gamma+n weight", "ftFoMVDnSensRecoGN", 1938),
    ("VD nominal Sensitivity truth X: gamma+n weight", "ftFoMVDnSensXTGN", 587),
    ("VD shielded Sensitivity reco X: signal eff (%)", "ftFoMVDsSensRecoEff", 77.3),
    ("VD shielded Sensitivity truth X: gamma+n weight", "ftFoMVDsSensXTGN", 26),
    ("VD nominal HEP reco X: gamma+n weight", "ftFoMVDnHEPRecoGN", 2.4e4),
    ("VD nominal HEP truth X: gamma+n weight", "ftFoMVDnHEPXTGN", 8869),
    ("VD shielded HEP truth X: signal eff (%)", "ftFoMVDsHEPXTEff", 95.8),
    ("HD lateral Day-Night reco X: gamma+n weight", "ftFoMHDlDNRecoGN", 3.99e4),
    ("HD lateral Day-Night truth X: gamma+n weight", "ftFoMHDlDNXTGN", 3.58e4),
    ("VD nominal Day-Night proxy S/sqrt(B) reco", "ftFoMVDnDNRecoFom", 3.3),
    ("VD nominal Day-Night proxy S/sqrt(B) truth X", "ftFoMVDnDNXTFom", 8.6),
    ("VD shielded Day-Night proxy reco", "ftFoMVDsDNRecoFom", 14),
    ("VD shielded Day-Night proxy truth X", "ftFoMVDsDNXTFom", 27),
    ("VD nominal Sensitivity proxy reco", "ftFoMVDnSensRecoFom", 3.6),
    ("VD nominal Sensitivity proxy truth X", "ftFoMVDnSensXTFom", 7.7),
    ("VD shielded Sensitivity proxy reco", "ftFoMVDsSensRecoFom", 14),
    ("VD shielded Sensitivity proxy truth X", "ftFoMVDsSensXTFom", 36),
    ("HD lateral Day-Night proxy reco", "ftFoMHDlDNRecoFom", 6.4),
    ("HD lateral Day-Night proxy truth X", "ftFoMHDlDNXTFom", 6.8),
    ("HD lateral Day-Night proxy truth X, no containment", "ftFoMHDlDNXTncFom", 6.44),
    ("Radiological share VD nominal Day-Night (%)", "ftBSVDnDNRecoRadShare", 99.4),
    ("Radiological share VD shielded Day-Night (%)", "ftBSVDsDNRecoRadShare", 99.96),
    ("Radiological share VD nominal HEP (%)", "ftBSVDnHEPRecoRadShare", 99.7),
    ("Radiological share VD shielded HEP (%)", "ftBSVDsHEPRecoRadShare", 99.97),
    ("Radiological share VD nominal Sensitivity (%)", "ftBSVDnSensRecoRadShare", 99.0),
    ("Radiological share VD shielded Sensitivity (%)", "ftBSVDsSensRecoRadShare", 99.9),
    ("Radiological MC events VD nominal HEP", "ftBSVDnHEPRecoRadMC", 65),
    ("HD central radiological share, reco fiducial, Day-Night (%)", "ftBSHDcDNRecoRadShare", 99.9),
    ("HD central radiological share, reco fiducial, HEP (%)", "ftBSHDcHEPRecoRadShare", 99.9),
    ("HD lateral median |dX| gamma after cut (cm)", "ftXEHDlDNGCutMedian", 4.9),
    ("HD lateral median |dX| neutron after cut (cm)", "ftXEHDlDNNCutMedian", 14.5),
    ("HD lateral |dX|>100 gamma after cut (%)", "ftXEHDlDNGCutAboveHundred", 5),
    ("HD lateral |dX|>100 neutron after cut (%)", "ftXEHDlDNNCutAboveHundred", 25),
    ("VD nominal median |dX| gamma after cut (cm)", "ftXEVDnDNGCutMedian", 386),
    ("VD nominal |dX|>100 gamma after cut (%)", "ftXEVDnDNGCutAboveHundred", 78),
    ("VD nominal median |dX| neutron after cut (cm)", "ftXEVDnDNNCutMedian", 335),
    ("VD nominal neutron MC events after cut", "ftXEVDnDNNCutMC", 48),
    ("VD shielded median |dX| gamma after cut (cm)", "ftXEVDsDNGCutMedian", 357),
    ("VD shielded |dX|>100 gamma after cut (%)", "ftXEVDsDNGCutAboveHundred", 83),
    ("Signal |dX|>100 cm, HD lateral (%) [FlashMismatch, window sample]", "ftFMHDlDNSigDxHundred", 14),
    ("Signal |dX|>100 cm, VD nominal (%) [FlashMismatch, window sample]", "ftFMVDnDNSigDxHundred", 15),
    ("HD lateral Y-face share of gamma, + analysis cut (%)", "ftFCHDlDNGCutY", 49),
    ("HD lateral Y-face share of gamma, + cut + reco fiducial (%)", "ftFCHDlDNGFidY", 0.9),
    ("VD nominal top-face share of neutron, + cut + reco fiducial (%)", "ftFCVDnDNNFidXhigh", 97),
    ("VD nominal top-face share of gamma, + cut + reco fiducial (%)", "ftFCVDnDNGFidXhigh", 99),
]


def check_brief(M):
    lines = ["| check | brief | pickle | verdict |", "|---|---|---|---|"]
    n_bad = 0
    for desc, key, exp in BRIEF_CHECKS:
        got = M.values.get(key)
        if got is None:
            lines.append(f"| {desc} | {exp} | missing | MISSING |")
            n_bad += 1
            continue
        tol = 0.06 if "RadShare" in key else max(BRIEF_TOL * abs(exp), 0.06)
        ok = abs(got - exp) <= tol
        n_bad += not ok
        lines.append(f"| {desc} | {exp} | {got:.4g} | {'ok' if ok else '**DIFFERS**'} |")
    return lines, n_bad


def check_status(F, status_path):
    rows, _ = sm.parse(Path(status_path))
    idx = {(r["cfg"], r["folder"], r["ana"], r["study"]): r for r in rows}
    lines = ["| config | analysis | variant | pickle (30 yr) | status file (30 yr) | verdict |", "|---|---|---|---|---|---|"]
    n_bad = 0
    for _, r in F["Significance"].iterrows():
        if r.Variant not in ("default", "fiduc_truth"):
            continue
        st = idx.get((r.cfg, "Truncated", r.Analysis, r.Variant))
        if st is None:
            continue
        s30 = st["vals"][30]
        if r.Analysis == "Sensitivity":
            ref, txt = 0.5 * (float(s30[0]) + float(s30[1])), f"score {0.5 * (float(s30[0]) + float(s30[1])):.2f} (mean of {s30[0]}/{s30[1]})"
        else:
            ref, txt = float(s30[0]), s30[0]
        ok = abs(r.Significance - ref) <= 0.011
        n_bad += not ok
        lines.append(f"| {r.cfg} | {ANA[r.Analysis]} | {r.Variant} | {r.Significance:.3f} | {txt} | {'ok' if ok else '**DIFFERS**'} |")
    return lines, n_bad


def check_exposure(lowe_data, status_path):
    """Exposure curves (the pickles behind the fiduc_truth figures) against the status file."""
    rows, _ = sm.parse(Path(status_path))
    idx = {(r["cfg"], r["folder"], r["ana"], r["study"]): r for r in rows}
    base = Path(lowe_data)
    sel = {"DayNight": ("Asimov", "Smoothed"), "HEP": ("ProfileLikelihood", "Smoothed")}
    lines = ["| config | analysis | variant | exposure (yr) | curve pickle | status file | verdict |", "|---|---|---|---|---|---|---|"]
    n_bad = 0
    for cfg_full, cfg in CFG.items():
        for ana, (var, spec) in sel.items():
            for study, path in (("default", base / f"{cfg_full}_marley_{ana}_Exposure.pkl"),
                                ("fiduc_truth", base / "studies" / "truncated" / "fiduc_truth" / f"{cfg_full}_marley_{ana}_Exposure.pkl")):
                if not path.exists():
                    lines.append(f"| {cfg} | {ANA[ana]} | {study} | | missing {path.name} | | MISSING |")
                    n_bad += 1
                    continue
                d = pd.read_pickle(path)
                d = d[(d.Variable == var) & (d.SpectrumType == spec)].iloc[0]
                x, y = list(d.Exposure), list(d.Significance)
                st = idx[(cfg, "Truncated", ANA[ana] if False else ana, study)]
                for yr in (20, 30):
                    v = float(pd.Series(y, index=x).sort_index().pipe(lambda t: t.reindex(t.index.union([yr])).interpolate("index")).loc[yr])
                    ref = float(st["vals"][yr][0])
                    ok = abs(v - ref) <= 0.011
                    n_bad += not ok
                    lines.append(f"| {cfg} | {ANA[ana]} | {study} | {yr} | {v:.3f} | {ref} | {'ok' if ok else '**DIFFERS**'} |")
    return lines, n_bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data_dir", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=ROOT / "results" / "fiduc_truth_macros.tex")
    ap.add_argument("--tables-dir", type=Path, default=ROOT / "results" / "fiduc_truth")
    ap.add_argument("--status", type=Path, default=None)
    ap.add_argument("--lowe-data", type=Path, default=Path.home() / "Code/LOWE_RECONSTRUCTION_PUBLICATION/input/data",
                    help="LOWE input/data, for the exposure-curve cross-check")
    ap.add_argument("--inventory", action="store_true", help="print the pickle inventory and exit")
    args = ap.parse_args()

    meta = json.loads((args.data_dir / "meta.json").read_text())
    F = load(args.data_dir)
    report = inventory(F, args.data_dir, meta)
    if args.inventory:
        print("\n".join(report))
        return

    M = build_macros(F)
    header = [
        "% ---------------------------------------------------------------------------",
        "% AUTO-GENERATED by LOWE_RECONSTRUCTION_PUBLICATION/scripts/fiduc_truth_data.py -- do not edit by hand.",
        f"% Data   : {args.data_dir}",
        f"% Export : {meta.get('generated')}, SOLAR {meta.get('git_head')}",
        "% Scope  : Truncated folder, SolarEnergy 10-20 MeV, default best cut of each analysis,",
        "%          raw SignalParticleWeight (no oscillation, MC-support gate or smoothing).",
        "% Names  : \\ft<Kind><Cfg><Ana><Sample><Stage/Selection><Quantity>, letters only.",
        "%   Cfg HDc HDl VDn VDs;  Ana DN HEP Sens;  Sample Sig G N R;",
        "%   Win = 10-20 MeV window, Cut = + analysis cut, Fid = + cut + reco fiducial.",
        "%   BS BackgroundSplit, XE XEntrySummary, FM FlashMismatch, RS ResidualSummary,",
        "%   FC FaceComposition, FoM BestFoM (X-only scan; modes Reco Truth XR XT XTnc),",
        "%   SS SurvivorStatistics, R ranges (Min/Max).",
        "% ---------------------------------------------------------------------------",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(header + M.lines) + "\n", encoding="utf-8")
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in (("signal_background", tab_signal_bkg), ("radiological_share", tab_radiological), ("entry_dx", tab_dx)):
        (args.tables_dir / f"{name}.tex").write_text(fn(F), encoding="utf-8")

    status = args.status or max((ROOT / "results").glob("study_status_*.md"), default=None)
    n_status = 0
    report += ["", "## Cross-check: pickle significances against the status file", ""]
    if status:
        rl, n_status = check_status(F, status)
        report += [f"Status file: `{Path(status).name}`", ""] + rl
    else:
        report += ["No status file found."]
    n_exp = 0
    if status and args.lowe_data.exists():
        rl, n_exp = check_exposure(args.lowe_data, status)
        report += ["", "## Cross-check: exposure curves behind the fiduc_truth figures against the status file", ""] + rl
    rl, n_brief = check_brief(M)
    report += ["", f"## Cross-check: reference values of the writing brief (tolerance {BRIEF_TOL:.0%} relative, 0.06 points for radiological shares)", ""] + rl
    (args.tables_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"{len(M.lines)} macro lines -> {args.output}; tables -> {args.tables_dir}; "
          f"status mismatches: {n_status}; exposure-curve mismatches: {n_exp}; brief differences: {n_brief} (see {args.tables_dir / 'report.md'})")


if __name__ == "__main__":
    main()
