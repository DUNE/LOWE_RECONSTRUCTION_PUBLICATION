#!/usr/bin/env python3

"""
Cross-check the chapter 9 inputs against the SOLAR status table, without drawing anything.

For every status-table row of a study used in chapter 9 (default, bkg_gamma_*,
energy_*, charge_*, bkgmodel_*, membrane_veto_off on VD) the quoted values are
recomputed from the synced pkls with the recipe of SOLAR's study_status.py and
compared with the table at its printed precision (2 decimals), together with the
selection cut and the quoted exposure. Every disagreement is listed and the exit
status is 1 if there is any.

Run:
    python scripts/ch9_check_status.py \\
        --data-dir input/data/studies \\
        --status-table input/status/study_status_20260921_v15.md
"""

import argparse
import sys
from collections import Counter

from _bootstrap import ensure_src_path

ensure_src_path()

from lib.chapter9 import VD_CONFIGS, Checker, MissingData, load_series, read_status_table
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "input" / "data" / "studies"
DEFAULT_STATUS_TABLE = REPO_ROOT / "input" / "status" / "study_status_20260921_v15.md"

CHAPTER9_STUDIES = {
    "default", "bkg_gamma_cluster", "bkg_gamma_total", "energy_spk", "energy_maink",
    "charge_Q0", "charge_Q50", "charge_Q100", "charge_Q500", "bkgmodel_nominal", "bkgmodel_reduced", "membrane_veto_off",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--status-table", default=str(DEFAULT_STATUS_TABLE))
    parser.add_argument("--all-studies", action="store_true", help="Check every row, not only the chapter 9 studies")
    args = parser.parse_args()

    table = read_status_table(args.status_table)
    checker = Checker("warn")
    loaded, missing = 0, []
    tags = Counter()
    for row in table.rows:
        if not args.all_studies:
            if row.study not in CHAPTER9_STUDIES:
                continue
            if row.study == "membrane_veto_off" and row.config not in VD_CONFIGS:
                continue
            if row.study == "default" and row.folder != "Truncated":
                continue  # Nominal/Reduced 'default' runs are not used: the bkgmodel_* studies replace them
        if row.study in ("fiduc_truth", "fiduc_truth_refvol", "legacy_fit"):
            continue
        try:
            load_series(args.data_dir, table, row.config, row.folder, row.analysis, row.study, checker)
            loaded += 1
            for t in row.tags:
                tags[t] += 1
        except MissingData as exc:
            missing.append(str(exc))

    print(f"status table : {args.status_table}")
    print(f"rows checked : {loaded}   checks: {checker.checked}   mismatches: {len(checker.mismatches)}   inputs missing: {len(missing)}")
    print("tags on the checked rows: " + ", ".join(f"{k} x{v}" for k, v in sorted(tags.items())))
    for m in checker.mismatches:
        print("MISMATCH", m)
    for m in missing:
        print("MISSING ", m)
    sys.exit(1 if checker.mismatches or missing else 0)


if __name__ == "__main__":
    main()
