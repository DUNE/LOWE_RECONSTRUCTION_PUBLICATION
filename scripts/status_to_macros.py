#!/usr/bin/env python3
"""Regenerate results/macros.tex from a SOLAR study-status markdown file.

Usage:  python3 LOWE_RECONSTRUCTION_PUBLICATION/scripts/status_to_macros.py [STATUS.md] [-o results/macros.tex]

Without STATUS.md the newest results/study_status_*.md is used.
The status file has one table per detector configuration with the columns
folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend.

Macro names are  \\res<Cfg><Folder><Ana><study><Qty>  with letters only (digits are
spelled out), e.g. \\resHDcTruncDNchargeQfiftyTwenty.  See the header written to the
output file for the full legend.
"""
import argparse
import os
import math
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# Thesis repository (outputs go to its results/ and tables/); override with THESIS_DIR.
ROOT = Path(os.environ.get("THESIS_DIR", Path.home() / "Code" / "THESIS"))

CFG = {"central": "HDc", "lateral": "HDl", "nominal": "VDn", "shielded": "VDs"}
FOLDER = {"Truncated": "Trunc", "Nominal": "Nom", "Reduced": "Red"}
ANA = {"DayNight": "DN", "HEP": "HEP", "Sensitivity": "Sens"}
REF_FOLDER, REF_STUDY = "Truncated", "default"
STALE_TAGS = ("epoch", "behind_default")

ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

VALUE_RE = re.compile(r"^(?:Δχ²\s*)?(\d+(?:\.\d+)?)(?:/(\d+(?:\.\d+)?))?(?:σ)?@(\d+)y$")


def words(n):
    """Spell a non-negative integer (< 1000) as one lowercase word."""
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + (ONES[n % 10] if n % 10 else "")
    hundreds = "hundred" if n // 100 == 1 else ONES[n // 100] + "hundred"
    return hundreds + (words(n % 100) if n % 100 else "")


def r2(x):
    return str(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def diff_num(value, ref):
    """Absolute difference value - ref with an explicit sign, two decimals."""
    x = float(Decimal(value) - Decimal(ref))
    return rf"\num[retain-explicit-plus]{{{'+' if x > 0 else ''}{r2(x)}}}"


def cap(s):
    return s[:1].upper() + s[1:]


def study_token(study):
    """default -> default, charge_Q50 -> chargeQfifty, unc_sig20 -> uncSigTwenty."""
    out = []
    for i, part in enumerate(study.split("_")):
        def spell(m):
            w = words(int(m.group(2)))
            # a lone capital before the number (Q50) keeps the spelled number lower-case
            return m.group(1) + (w if len(m.group(1)) == 1 and m.group(1).isupper() else cap(w))
        part = re.sub(r"([A-Za-z]*)(\d+)", spell, part)
        out.append(part if i == 0 else cap(part))
    return "".join(out)


def cfg_code(heading):
    for key, code in CFG.items():
        if key in heading.lower():
            return code
    raise ValueError(f"unknown configuration heading: {heading!r}")


def parse(path):
    rows, epochs, cfg = [], "", None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Epochs:"):
            epochs = line[len("Epochs:"):].strip()
        elif line.startswith("## "):
            cfg = cfg_code(line[3:])
        elif line.startswith("|") and cfg:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 10 or cells[0] in ("folder",) or set(cells[0]) <= {"-"}:
                continue
            folder, ana, study, cut, fid, value, at_eval, record, status = cells[:9]
            m30, mev = VALUE_RE.match(value), VALUE_RE.match(at_eval)
            if not (m30 and mev) or folder not in FOLDER or ana not in ANA:
                print(f"skipping unparsable row: {line[:100]}", file=sys.stderr)
                continue
            rows.append(dict(cfg=cfg, folder=folder, ana=ana, study=study, cut=cut,
                             fid=fid, vals={int(m.group(3)): (m.group(1), m.group(2)) for m in (m30, mev)},
                             record=record, status=status))
    return rows, epochs


def rel_pct(value, ref):
    v, r = float(value), float(ref)
    if r == 0:
        return None
    x = (v - r) / r * 100
    s = f"{abs(x):.1f}" if abs(x) < 10 else f"{abs(x):.0f}"
    if float(s) == 0:
        return r"\SI{0.0}{\percent}"
    return rf"\SI[retain-explicit-plus]{{{'-' if x < 0 else '+'}{s}}}{{\percent}}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("status", nargs="?", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=ROOT / "results" / "macros.tex")
    args = ap.parse_args()
    src = args.status or max((ROOT / "results").glob("study_status_*.md"), default=None)
    if src is None:
        sys.exit("no results/study_status_*.md found; pass the status file explicitly")

    rows, epochs = parse(src)
    index = {}
    for r in rows:
        r["base"] = "res" + r["cfg"] + FOLDER[r["folder"]] + ANA[r["ana"]] + study_token(r["study"])
        if r["base"] in index:
            sys.exit(f"duplicate macro base {r['base']}")
        index[r["base"]] = r
    ref_of = {(r["cfg"], r["ana"]): r for r in rows if r["folder"] == REF_FOLDER and r["study"] == REF_STUDY}

    out = [
        "% ---------------------------------------------------------------------------",
        "% AUTO-GENERATED by LOWE_RECONSTRUCTION_PUBLICATION/scripts/status_to_macros.py -- do not edit by hand.",
        f"% Source : {src.name}",
        f"% Epochs : {epochs}",
        "% Regenerate with:  python3 LOWE_RECONSTRUCTION_PUBLICATION/scripts/status_to_macros.py",
        "%",
        "% Macro name = \\res <Cfg> <Folder> <Ana> <study> <Qty>   (letters only)",
        "%   Cfg    HDc HDl VDn VDs   (HD central/lateral, VD nominal/shielded)",
        "%   Folder Trunc Nom Red     (background folder)",
        "%   Ana    DN HEP Sens",
        "%   study  status-file study name in camelCase, digits spelled out",
        "% Quantities (exposure in years spelled out):",
        "%   DN/HEP : Twenty (at_eval, 20 yr), Thirty (30 yr)",
        "%   Sens   : TenSR / TenRS (Delta chi^2 solar-fit-at-reactor / reactor-fit-at-solar, 10 yr),",
        "%            Ten (both, 'a/b'), ThirtySR, ThirtyRS, Thirty (30 yr)",
        "%   Diff<Qty> absolute change (study minus default), signed",
        "%   Rel<Qty> relative change against the Truncated default of the same",
        "%            configuration and analysis (not defined for that default itself)",
        "%   Num      number only (no unit) for DN/HEP;  Score/Sep  Sens score 0.5*(SR+RS) and sqrt(score)",
        "%   Z / ZNum  Sens significance of the reactor point, sqrt(SR) (solar Asimov data fitted at the reactor point),",
        "%            with / without the sigma unit; Rel<Qty>Z / Diff<Qty>Z its change against the default",
        "%   Rel<Qty>Score / Diff<Qty>Score  relative / absolute change of the Sens score against the default",
        "%   Cuts     NHits/OpHits/AdjCl (also CutNHits, CutOpHits, CutAdjCl);  Fid  FiducialX/Y/Z in cm",
        "%   resCombDN/resCombHEP: quadrature sum of the four Truncated defaults;",
        "%   resCombSens<Ten|Thirty>Score/Sep: summed Scores of the four Truncated defaults, and its square root;",
        "%   resCombSens<study><Ten|Thirty>Score/Sep: the same for each study run in all four configurations",
        "%   Flag     ok | stale   (stale = status contains epoch or behind_default)",
        "%   CutFlag  matched | differs   (differs = status tag cut!=ref: the cuts should match",
        "%            the reference but do not; re-optimised studies are not tagged)",
        "% ---------------------------------------------------------------------------",
    ]

    def d(base, qty, body, xspace=True):
        out.append(rf"\newcommand{{\{base}{qty}}}{{{body}{chr(92) + 'xspace' if xspace else ''}}}")

    n_macros = 0
    section = None
    for r in sorted(rows, key=lambda r: (r["cfg"], r["ana"], r["folder"] != REF_FOLDER, r["folder"], r["study"] != "default", r["study"])):
        if section != (r["cfg"], r["ana"]):
            section = (r["cfg"], r["ana"])
            out += ["", f"% === {r['cfg']} / {ANA[r['ana']]} ==="]
        b, ref = r["base"], ref_of.get((r["cfg"], r["ana"]))
        is_ref = ref is r
        for yr in sorted(r["vals"]):
            v = r["vals"][yr]
            ref_v = ref["vals"].get(yr) if ref else None
            name = words(yr).capitalize()
            if r["ana"] == "Sensitivity":
                for suf, i in (("SR", 0), ("RS", 1)):
                    d(b, f"{name}{suf}", rf"\num{{{v[i]}}}")
                d(b, name, rf"\num{{{v[0]}}}/\num{{{v[1]}}}")
                score = 0.5 * (float(v[0]) + float(v[1]))
                d(b, f"{name}Score", rf"\num{{{r2(score)}}}")
                d(b, f"{name}Sep", rf"\SI{{{r2(math.sqrt(score))}}}{{\sigma}}")
                z = math.sqrt(max(float(v[0]), 0.0))
                d(b, f"{name}Z", rf"\ensuremath{{\num{{{r2(z)}}}\,\sigma}}")
                d(b, f"{name}ZNum", rf"\num{{{r2(z)}}}")
                if ref_v and not is_ref:
                    ref_z = math.sqrt(max(float(ref_v[0]), 0.0))
                    p = rel_pct(str(z), str(ref_z))
                    if p:
                        d(b, f"Rel{name}Z", p)
                    d(b, f"Diff{name}Z", diff_num(str(r2(z)), str(r2(ref_z))))
                    for suf, i in (("SR", 0), ("RS", 1)):
                        p = rel_pct(v[i], ref_v[i])
                        if p:
                            d(b, f"Rel{name}{suf}", p)
                        d(b, f"Diff{name}{suf}", diff_num(v[i], ref_v[i]))
                    ref_score = 0.5 * (float(ref_v[0]) + float(ref_v[1]))
                    p = rel_pct(score, ref_score)
                    if p:
                        d(b, f"Rel{name}Score", p)
                    d(b, f"Diff{name}Score", diff_num(str(score), str(ref_score)))
                n_macros += 3
            else:
                d(b, name, rf"\ensuremath{{\num{{{v[0]}}}\,\sigma}}")
                d(b, f"{name}Num", rf"\num{{{v[0]}}}")
                if ref_v and not is_ref:
                    p = rel_pct(v[0], ref_v[0])
                    if p:
                        d(b, f"Rel{name}", p)
                    d(b, f"Diff{name}", diff_num(v[0], ref_v[0]))
                n_macros += 1
        stale = any(t in r["status"] for t in STALE_TAGS)
        differs = "cut!=ref" in r["status"]
        d(b, "Cuts", r["cut"])
        for key, c in zip(("CutNHits", "CutOpHits", "CutAdjCl"), r["cut"].split("/")):
            d(b, key, rf"\num{{{c}}}")
        d(b, "Fid", r["fid"])
        d(b, "Flag", "stale" if stale else "ok", xspace=False)  # compared as strings: no \xspace
        d(b, "CutFlag", "differs" if differs else "matched", xspace=False)

    out += ["", "% === Phase I combination: quadrature sum of the four Truncated defaults at the evaluation exposure ==="]
    for ana in ("DN", "HEP"):
        refs = [ref_of[(c, {"DN": "DayNight", "HEP": "HEP"}[ana])] for c in CFG.values()]
        yr = min(refs[0]["vals"])
        z = math.sqrt(sum(float(r["vals"][yr][0]) ** 2 for r in refs))
        d("resComb" + ana, words(yr).capitalize(), rf"\ensuremath{{\num{{{r2(z)}}}\,\sigma}}")
        d("resComb" + ana, words(yr).capitalize() + "Num", rf"\num{{{r2(z)}}}")
    # Sensitivity: the Delta chi^2 of independent samples add, so the combined score is the sum of the
    # four Truncated default scores (nuisances profiled per configuration, i.e. not shared).
    refs = [ref_of[(c, "Sensitivity")] for c in CFG.values()]
    for yr in sorted(refs[0]["vals"]):
        score = sum(0.5 * (float(r["vals"][yr][0]) + float(r["vals"][yr][1])) for r in refs)
        name = words(yr).capitalize()
        d("resCombSens", f"{name}Score", rf"\num{{{r2(score)}}}")
        d("resCombSens", f"{name}Sep", rf"\SI{{{r2(math.sqrt(score))}}}{{\sigma}}")
        z = math.sqrt(sum(max(float(r["vals"][yr][0]), 0.0) for r in refs))
        d("resCombSens", f"{name}Z", rf"\ensuremath{{\num{{{r2(z)}}}\,\sigma}}")
        d("resCombSens", f"{name}ZNum", rf"\num{{{r2(z)}}}")
    # Phase II projection of the oscillation contours: Phase I (all four configurations) for 30 years plus two
    # HD-like or VD-like Phase II modules for 20 years; the Delta chi^2 scales linearly with exposure, so each
    # technology adds 2 modules x 2 x its 10-year Score (as in the thesis contour figures).
    score30 = sum(0.5 * (float(r["vals"][30][0]) + float(r["vals"][30][1])) for r in refs)
    for tech, codes in (("HD", ("HDc", "HDl")), ("VD", ("VDn", "VDs"))):
        added = 4 * sum(0.5 * (float(ref_of[(c, "Sensitivity")]["vals"][10][0]) + float(ref_of[(c, "Sensitivity")]["vals"][10][1]))
                        for c in codes)
        d(f"resCombSensPhaseTwo{tech}", "Score", rf"\num{{{r2(score30 + added)}}}")
        d(f"resCombSensPhaseTwo{tech}", "Sep", rf"\SI{{{r2(math.sqrt(score30 + added))}}}{{\sigma}}")
        sr30 = sum(float(r["vals"][30][0]) for r in refs)
        sr_added = 4 * sum(float(ref_of[(c, "Sensitivity")]["vals"][10][0]) for c in codes)
        d(f"resCombSensPhaseTwo{tech}", "Z", rf"\ensuremath{{\num{{{r2(math.sqrt(max(sr30 + sr_added, 0.0)))}}}\,\sigma}}")
    # The same combination for every Truncated study run in all four configurations.
    studies = {r["study"] for r in rows if r["folder"] == REF_FOLDER and r["ana"] == "Sensitivity"} - {REF_STUDY}
    for study in sorted(studies):
        per_cfg = [index.get("res" + c + FOLDER[REF_FOLDER] + "Sens" + study_token(study)) for c in CFG.values()]
        if None in per_cfg:
            continue
        for yr in sorted(set.intersection(*(set(r["vals"]) for r in per_cfg))):
            score = sum(0.5 * (float(r["vals"][yr][0]) + float(r["vals"][yr][1])) for r in per_cfg)
            name = words(yr).capitalize()
            d("resCombSens" + study_token(study), f"{name}Score", rf"\num{{{r2(score)}}}")
            d("resCombSens" + study_token(study), f"{name}Sep", rf"\SI{{{r2(math.sqrt(score))}}}{{\sigma}}")
            z = math.sqrt(sum(max(float(r["vals"][yr][0]), 0.0) for r in per_cfg))
            d("resCombSens" + study_token(study), f"{name}Z", rf"\ensuremath{{\num{{{r2(z)}}}\,\sigma}}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    n_stale = sum(any(t in r["status"] for t in STALE_TAGS) for r in rows)
    print(f"{src.name}: {len(rows)} rows -> {args.output.relative_to(ROOT) if args.output.is_absolute() and ROOT in args.output.parents else args.output} "
          f"({n_stale} stale)")


if __name__ == "__main__":
    main()
