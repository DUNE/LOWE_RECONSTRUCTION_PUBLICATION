#!/usr/bin/env python3
"""Point the registered classifier-input plot commands at the current highest-importance features.

The commands in input/plots/{set}_scripts.txt that plot --datafile Signal_Background_Features (one
panel per --variables entry) list the features by hand. After a retrain the ranking can change, so
this script reads the Features export of each command's --configs/--names, which holds every
classifier input with its Rank and Importance, and rewrites in place:
  --variables            the top-N features by Rank (N = the number already listed, or --top)
  --variable_label_map   the panel titles of those features (FEATURE_LABELS below)

Input: input/data/workflow/discrimination/{config}_{name}_Signal_Background_Features.pkl
(SOLAR 03c export, synced by sync_solar_data.sh). Other flags of the commands are left untouched;
check the legend placement (--legend_panel) after regenerating the plots.

Example:
    python3 scripts/update_feature_commands.py --scripts reco            # rewrite the commands
    python3 scripts/update_feature_commands.py --scripts reco --dry-run  # only report the changes
"""

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "input" / "data" / "workflow" / "discrimination"

# Panel title of every classifier input (SOLAR 03b feature list).
FEATURE_LABELS = {
    "NHits": "Primary-cluster TPC hits",
    "AdjClNum": "Adjacent clusters",
    "SelectedAdjClNum": "Selected adjacent clusters",
    "Energy": "Primary energy (MeV)",
    "TotalEnergy": "Total energy (MeV)",
    "SelectedEnergy": "Selected energy (MeV)",
    "SelectedAdjClEnergy": "Selected adjacent-cluster energy (MeV)",
    "SelectedAdjClEnergyRatio": "Selected adjacent-cluster energy ratio",
    "SelectedMaxAdjClEnergy": "Selected maximum adjacent-cluster energy (MeV)",
    "TotalAdjClEnergy": "Total adjacent-cluster energy (MeV)",
    "MaxAdjClEnergy": "Maximum adjacent-cluster energy (MeV)",
    "MatchedOpFlashPE": "Matched-flash PE",
    "MatchedOpFlashNHits": "Matched-flash optical hits",
}

VARIABLES_RE = re.compile(r"(--variables)((?:\s+(?!-)\S+)+)")
LABEL_MAP_RE = re.compile(r"(--variable_label_map)\s+'[^']*'")


def flag_values(tokens, flag):
    """Values following `flag` up to the next option."""
    if flag not in tokens:
        return []
    values = []
    for token in tokens[tokens.index(flag) + 1:]:
        if token.startswith("-"):
            break
        values.append(token)
    return values


def top_features(config, name, n, region):
    path = DATA_DIR / f"{config}_{name}_Signal_Background_Features.pkl"
    df = pd.read_pickle(path)
    if "Region" in df.columns and region is not None:
        df = df[df["Region"] == region]
    ranked = df.drop_duplicates("Feature").sort_values("Rank")
    missing = [f for f in ranked["Feature"] if f not in FEATURE_LABELS]
    if missing:
        sys.exit(f"Error: no panel title for {missing} in FEATURE_LABELS ({path.name})")
    return ranked.head(n)[["Feature", "Importance"]].values.tolist()


def update_line(line, top, datafile):
    tokens = shlex.split(line)
    if flag_values(tokens, "--datafile") != [datafile]:
        return line, None
    configs, names = flag_values(tokens, "--configs"), flag_values(tokens, "--names")
    if len(configs) != 1 or len(names) != 1:
        sys.exit(f"Error: expected one --configs and one --names value in:\n{line}")
    current = flag_values(tokens, "--variables")
    selects, values = flag_values(tokens, "--select"), flag_values(tokens, "--save_values") or flag_values(tokens, "-s")
    region = dict(zip(selects, values)).get("Region")
    ranked = top_features(configs[0], names[0], top or len(current), region)
    features = [f for f, _ in ranked]

    labels = json.dumps({f: FEATURE_LABELS[f] for f in features}, separators=(",", ":"))
    new = VARIABLES_RE.sub(lambda m: f"{m.group(1)} {' '.join(features)}", line, count=1)
    if LABEL_MAP_RE.search(new):
        new = LABEL_MAP_RE.sub(lambda m: f"{m.group(1)} '{labels}'", new, count=1)
    else:
        new = new.rstrip("\n") + f" --variable_label_map '{labels}'\n"
    summary = f"{configs[0]}: {' '.join(current)} -> " + ", ".join(f"{f} ({100 * i:.1f}%)" for f, i in ranked)
    return new, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scripts", default="reco", help="Command set: input/plots/{set}_scripts.txt (default: reco)")
    parser.add_argument("--datafile", default="Signal_Background_Features", help="Datafile of the commands to update")
    parser.add_argument("--top", type=int, default=None, help="Number of features per command (default: keep the current count)")
    parser.add_argument("--dry-run", action="store_true", help="Report the changes without writing the file")
    args = parser.parse_args()

    script_file = ROOT / "input" / "plots" / f"{args.scripts}_scripts.txt"
    lines = script_file.read_text().splitlines(keepends=True)
    changed = 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith(("#", "%")) or f"--datafile {args.datafile}" not in line:
            continue
        new, summary = update_line(line, args.top, args.datafile)
        if summary is None:
            continue
        print(("updated   " if new != line else "unchanged ") + summary)
        changed += new != line
        lines[i] = new
    if changed and not args.dry_run:
        script_file.write_text("".join(lines))
    print(f"{changed} command(s) {'would change' if args.dry_run else 'changed'} in {script_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
