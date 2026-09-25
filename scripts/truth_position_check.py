#!/usr/bin/env python3

"""
Sanity checks of the SOLAR truth-position export (input/data/truth_position/{config}_all_{Kind}.pkl).

Fails loudly when a synced pickle does not reproduce the reference numbers of the export:
  - WallCdf, HD central, truth, 20 cm: gamma ~0.46, marley ~0.10, neutron ~0.08
  - Significance, HD lateral, DayNight: default 1.537, fiduc_truth 2.113, fiduc_truth_refvol 1.517
  - PassFractions, DayNight, HD central, neutron_disagree, VariantIndex 0..3: 0.011, 0.995, 0.0066, 0.0066 (NMC = 12)
  - BestFoM, DayNight, HD central, reco, X and Y scan: 369.34
and the structure of the files: Name == 'all', equal-length arrays in every row, the four faces of FaceComposition summing to 1.
FaceComposition percentages (DayNight) are also checked against SOLAR Table F1 (13 values, tolerance 0.06 points).

Run it after ./scripts/sync_solar_data.sh --truth-position and before run_plot_scripts.py -s truth_position.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DIR = Path(__file__).resolve().parents[1] / "input" / "data" / "truth_position"
CONFIGS = ["hd_1x2x6_centralAPA", "hd_1x2x6_lateralAPA", "vd_1x8x14_3view_30deg_nominal", "vd_1x8x14_3view_30deg_shielded"]
CENTRAL, LATERAL, NOMINAL, SHIELDED = CONFIGS
CUT, RECO = "+ analysis cut", "+ cut + reco fiducial"
# SOLAR Table F1 (truth_position_faces_daynight.md): (config, sample, stage, face, percent).
# HD lateral's wall definition changed 2026-09-21 (SOLAR git 0eb6b74): only x=0 counts as a wall now (x=360 no
# longer does, see meta.json "notes"), so HD lateral's "X high" face is 0 everywhere and the "X low"/Y/Z split
# shifted; the HD lateral rows below were updated from that export and the "X high" checks now pin it at 0.
FACE_REFERENCE = [
    (NOMINAL, "gamma", RECO, "X high", 98.3), (NOMINAL, "gamma", RECO, "Y", 0.9),
    (LATERAL, "gamma", RECO, "X low", 90.55), (LATERAL, "gamma", CUT, "Y", 51.89), (LATERAL, "gamma", RECO, "Y", 3.66),
    (LATERAL, "neutron", RECO, "X low", 57.89), (LATERAL, "neutron", RECO, "X high", 0.0),
    (SHIELDED, "neutron", RECO, "X high", 74.2), (SHIELDED, "neutron", RECO, "X low", 25.1),
    (CENTRAL, "gamma", RECO, "Y", 99.2), (CENTRAL, "neutron", RECO, "Y", 94.3),
    (LATERAL, "radiological", RECO, "X high", 0.0), (LATERAL, "radiological", RECO, "Z", 75.0),
]


def check(data_dir):
    load = lambda config, kind: pd.read_pickle(data_dir / f"{config}_all_{kind}.pkl")
    meta = data_dir / "meta.json"
    if meta.exists():
        info = json.loads(meta.read_text())
        print(f"export generated {info['generated']} from SOLAR {info['git_head']}")

    files = sorted(data_dir.glob("*_all_*.pkl"))
    assert len(files) == 4 * len(sorted({f.stem.split("_all_")[1] for f in files})), "missing {config}_all_{Kind}.pkl files"
    for f in files:
        df = pd.read_pickle(f)
        assert set(df["Name"]) == {"all"}, f"{f.name}: Name must be 'all'"
        assert not df.isna().all().any(), f"{f.name}: all-NaN column"
        for col in df.columns:
            if df[col].dtype == object and len(df) and isinstance(df[col].iloc[0], (list, np.ndarray)):
                arrays = [c for c in df.columns if df[c].dtype == object and isinstance(df[c].iloc[0], (list, np.ndarray))]
                lengths = df[arrays].apply(lambda r: {len(v) for v in r}, axis=1)
                assert (lengths.map(len) == 1).all(), f"{f.name}: arrays of unequal length in a row"
                break
    print(f"{len(files)} files: Name == 'all', no all-NaN columns, equal-length arrays")

    w = load(CENTRAL, "WallCdf")
    w = w[w.Analysis == "DayNight"]
    for sample, want in (("gamma", 0.46), ("marley", 0.10), ("neutron", 0.08)):
        row = w[(w.Sample == sample) & (w.Position == "truth")]
        assert len(row) == 1, f"WallCdf: expected one row for {sample}, found {len(row)}"
        r = row.iloc[0]
        got = float(np.asarray(r.CDF)[list(r.Distance).index(20)])
        assert abs(got - want) < 0.02, f"WallCdf HD central {sample} at 20 cm: {got:.3f}, expected ~{want}"
        print(f"WallCdf {sample:8s} {got:.3f} (~{want})")

    s = load(LATERAL, "Significance")
    s = s[s.Analysis == "DayNight"].set_index("Variant").Significance
    for variant, want in (("default", 1.537), ("fiduc_truth", 2.113), ("fiduc_truth_refvol", 1.517)):
        assert abs(s[variant] - want) < 5e-4, f"Significance HD lateral DayNight {variant}: {s[variant]:.4f}, expected {want}"
        print(f"Significance {variant:20s} {s[variant]:.3f}")

    p = load(CENTRAL, "PassFractions")
    p = p[(p.Analysis == "DayNight") & (p.Sample == "neutron_disagree")].sort_values("VariantIndex")
    assert list(p.VariantIndex) == [0, 1, 2, 3] and (p.NMC == 12).all(), "PassFractions neutron_disagree: unexpected rows or NMC"
    assert np.allclose(p.PassFraction, [0.011, 0.995, 0.0066, 0.0066], atol=6e-4), f"PassFractions neutron_disagree: {list(p.PassFraction.round(4))}"
    print("PassFractions neutron_disagree", list(p.PassFraction.round(4)))

    b = load(CENTRAL, "BestFoM")
    fom = float(b[(b.Analysis == "DayNight") & (b.Mode == "reco") & (b.Scan == "X and Y")].FoM.iloc[0])
    assert abs(fom - 369.34) < 0.01, f"BestFoM DayNight HD central reco X and Y: {fom:.2f}, expected 369.34"
    print(f"BestFoM DayNight HD central reco (X and Y) {fom:.2f}")

    for config in CONFIGS:
        f = load(config, "FaceComposition")
        sums = f.groupby(["Analysis", "Sample", "Stage"]).WeightFraction.sum()
        assert np.allclose(sums, 1.0, atol=1e-9), f"FaceComposition {config}: the four faces do not sum to 1"
    print("FaceComposition: the four faces sum to 1")

    for config, sample, stage, face, want in FACE_REFERENCE:
        f = load(config, "FaceComposition")
        row = f[(f.Analysis == "DayNight") & (f.Sample == sample) & (f.Stage == stage) & (f.Face == face)]
        assert len(row) == 1, f"FaceComposition {config} {sample} {stage} {face}: expected one row, found {len(row)}"
        got = 100 * float(row.WeightFraction.iloc[0])
        assert abs(got - want) < 0.06, f"FaceComposition {config} {sample} {stage} {face}: {got:.2f}%, expected {want}%"
    print(f"FaceComposition: {len(FACE_REFERENCE)} SOLAR Table F1 values reproduced (tolerance 0.06 points)")
    print("OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", type=Path, default=DEFAULT_DIR, help="folder with the truth_position pickles")
    try:
        check(ap.parse_args().path)
    except (AssertionError, FileNotFoundError) as err:
        sys.exit(f"FAILED: {err}")
