"""Registry of SOLAR study outputs and the local layout they are synced into.

SOLAR's study orchestrator (``src/pipelines/run_studies.py``) writes every
per-study result under ``output/data`` in three trees (paths relative to it):

    analysis/{day-night|hep|sensitivity}/{config}/marley/{folder}/{label}/{config}_marley_{Analysis}_{Kind}.pkl
    solar/cutflow/{config}/{name}/{folder}/{analysis}/{config}_{name}_{Energy}_{Analysis}_Cutflow{suffix}.pkl
    solar/nhits/{config}/{name}/truncated/{daynight|hep}/{config}_{name}_Weighted_Distributions_Fiducial_{DayNight|HEP}.pkl

``{folder}`` is the background model (``truncated`` is the reference) and
``{label}`` the study label (``default`` for the main analysis). The label is
a directory, so filenames are identical across studies and the folder/label
dimensions would collide when flattened by basename. Locally the files are
therefore laid out as

    input/data/{config}_{name}_{...}.pkl                      reference copy (truncated/default, cutflow and nhits of the truncated folder)
    input/data/studies/{folder}/{label}/{config}_{name}_{...}.pkl   every (folder, label) pair, including truncated/default

and ``lib.imports`` resolves ``--path studies --datafile {Kind}_{label}`` (the
legacy flat convention), ``--path studies/{folder}/{label} --datafile {Kind}``
and ``--path studies/{folder} --datafile {Kind}_{label}`` against that tree.

The study table below mirrors ``lib/study.py`` ``STUDY_VARIANTS`` in SOLAR
(as of 2026-09-17). It is the single source of truth for which label
directories are live: the remote also still holds directories of retired
labels that must not be synced.

This module is used both as a library (``from lib.solar_studies import ...``)
and as a CLI by ``scripts/sync_solar_data.sh``:

    python3 src/lib/solar_studies.py rules  [filters]      rsync include rules (stdin for --include-from)
    python3 src/lib/solar_studies.py route  MIRROR DATA_DIR [--force] [--dry-run] [filters]
    python3 src/lib/solar_studies.py expected [filters]    expected remote paths, one per line
    python3 src/lib/solar_studies.py labels                live labels (one per line)
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

# ---------------------------------------------------------------------------
# Static registry
# ---------------------------------------------------------------------------

CONFIGS = (
    "hd_1x2x6_centralAPA",
    "hd_1x2x6_lateralAPA",
    "vd_1x8x14_3view_30deg_nominal",
    "vd_1x8x14_3view_30deg_shielded",
)
VD_CONFIGS = tuple(c for c in CONFIGS if c.startswith("vd_"))

SIGNAL_NAME = "marley"
COMPONENT_NAMES = ("marley", "gamma", "neutron", "radiological")

# Analysis name as written in filenames -> directory name under analysis/
ANALYSES = {"DayNight": "day-night", "HEP": "hep", "Sensitivity": "sensitivity"}
ANALYSIS_BY_DIR = {v: k for k, v in ANALYSES.items()}
# Lower-case directory names used by solar/cutflow and solar/nhits
ANALYSIS_LOWER = {"DayNight": "daynight", "HEP": "hep", "Sensitivity": "sensitivity"}
ANALYSIS_BY_LOWER = {v: k for k, v in ANALYSIS_LOWER.items()}
ALL_ANALYSES = tuple(ANALYSES)

FOLDERS = ("truncated", "nominal", "reduced")
REFERENCE_FOLDER = "truncated"
DEFAULT_LABEL = "default"
STUDIES_DIRNAME = "studies"

# Result kinds per analysis (the "important" families). Everything else in a
# live label directory (Significance, Oscillogram, Signal1D_*, Projections,
# Templates) is synced too, but only these are checked for completeness.
KINDS = {
    "DayNight": ("Counts", "Exposure"),
    "HEP": ("Counts", "Exposure"),
    "Sensitivity": ("Counts", "Contours", "10Y_Contours"),
}
FAMILIES = ("Counts", "Exposure", "Contours", "10Y_Contours", "Cutflow", "Weighted")

CUTFLOW_DEFAULT_ENERGY = "SolarEnergy"
CUTFLOW_SUFFIX_LABELS = ("fiduc_truth",)  # studies with their own cutflow file, tagged by a filename suffix


@dataclass(frozen=True)
class Study:
    label: str
    group: str
    folders: tuple = (REFERENCE_FOLDER,)
    analyses: tuple = ALL_ANALYSES
    configs: tuple = CONFIGS
    cutflow_energy: Optional[str] = None  # study-specific cutflow energy label (shared by the group)


STUDIES: tuple = (
    Study(DEFAULT_LABEL, "default", FOLDERS, ALL_ANALYSES, cutflow_energy=CUTFLOW_DEFAULT_ENERGY),
    # 9.1.2 uncertainty impacts
    Study("unc_bkg0", "unc", FOLDERS, ALL_ANALYSES),
    Study("unc_bkg4", "unc", FOLDERS, ALL_ANALYSES),
    Study("unc_bkg6", "unc", (REFERENCE_FOLDER,), ALL_ANALYSES),
    Study("unc_sig20", "unc", (REFERENCE_FOLDER,), ("HEP",)),
    Study("unc_sig40", "unc", (REFERENCE_FOLDER,), ("HEP",)),
    Study("unc_sig0", "unc", (REFERENCE_FOLDER,), ("Sensitivity",)),
    Study("unc_sig2", "unc", (REFERENCE_FOLDER,), ("Sensitivity",)),
    Study("unc_sig6", "unc", (REFERENCE_FOLDER,), ("Sensitivity",)),
    # nuisance decomposition
    Study("nuisance_nominal", "nuisance", (REFERENCE_FOLDER,), ("Sensitivity",)),
    Study("nuisance_sin13", "nuisance", (REFERENCE_FOLDER,), ("Sensitivity",)),
    Study("nuisance_escale", "nuisance", (REFERENCE_FOLDER,), ("Sensitivity",)),
    # oscillation best-fit point
    Study("oscpoint_solar", "oscpoint", (REFERENCE_FOLDER,), ("DayNight", "HEP")),
    Study("oscpoint_reactor", "oscpoint", (REFERENCE_FOLDER,), ("DayNight", "HEP")),
    # energy estimator
    Study("energy_spk", "energy", (REFERENCE_FOLDER,), ("DayNight",), cutflow_energy="SignalParticleK"),
    Study("energy_maink", "energy", (REFERENCE_FOLDER,), ("DayNight",), cutflow_energy="MainK"),
    # charge threshold scan (all share the SelectedEnergy cutflow)
    Study("charge_Q0", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    Study("charge_Q50", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    Study("charge_Q100", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    Study("charge_Q500", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    # background model normalisation (folder provides the isolation)
    Study("bkgmodel_nominal", "bkgmodel", ("nominal",), ALL_ANALYSES),
    Study("bkgmodel_reduced", "bkgmodel", ("reduced",), ALL_ANALYSES),
    # truth fiducialisation (has its own cutflow, tagged with a _fiduc_truth suffix)
    Study("fiduc_truth", "fiduc_truth", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy=CUTFLOW_DEFAULT_ENERGY),
    # background gamma energy model
    Study("bkg_gamma_cluster", "bkg_gamma", (REFERENCE_FOLDER,), ("DayNight", "HEP")),
    Study("bkg_gamma_total", "bkg_gamma", (REFERENCE_FOLDER,), ("DayNight", "HEP")),
    # membrane veto (VD only)
    Study("membrane_veto_off", "membrane_veto", (REFERENCE_FOLDER,), ALL_ANALYSES, configs=VD_CONFIGS),
    # legacy fitter (FitMethod=legacy; do not overlay with pull-fit contours)
    Study("legacy_fit", "legacy_fit", (REFERENCE_FOLDER,), ("Sensitivity",)),
)

STUDY_BY_LABEL = {s.label: s for s in STUDIES}
LIVE_LABELS = tuple(s.label for s in STUDIES)
GROUPS = tuple(dict.fromkeys(s.group for s in STUDIES))

# Retired labels that still have directories on the remote. Listed only so the
# sync can tell "known dead" from "unknown, maybe new" when it reports them.
DEAD_LABELS = frozenset(
    {
        "metric_raw",
        "metric_smoothed",
        "unc_bkg10",
        "unc_bkg20",
        "unc_bkg4_nobkgfit",
        "unc_bkg6_nobkgfit",
        "unc_sig8",
        "charge_Q200",
        "bkg_gamma",
    }
)


def studies_in_group(group: str) -> list:
    return [s for s in STUDIES if s.group == group]


def labels_for(analysis: str, folder: str = REFERENCE_FOLDER, config: Optional[str] = None) -> list:
    """Live labels that exist for this analysis/folder (and config)."""
    out = []
    for s in STUDIES:
        if analysis not in s.analyses or folder not in s.folders:
            continue
        if config is not None and config not in s.configs:
            continue
        out.append(s.label)
    return out


# ---------------------------------------------------------------------------
# Filters (shared by rules / expected / route)
# ---------------------------------------------------------------------------


@dataclass
class Filters:
    configs: list = field(default_factory=list)
    exclude_configs: list = field(default_factory=list)
    names: list = field(default_factory=list)
    exclude_names: list = field(default_factory=list)
    folders: list = field(default_factory=list)
    exclude_folders: list = field(default_factory=list)
    studies: list = field(default_factory=list)
    exclude_studies: list = field(default_factory=list)
    analyses: list = field(default_factory=list)
    exclude_analyses: list = field(default_factory=list)
    energies: list = field(default_factory=list)
    exclude_energies: list = field(default_factory=list)

    @staticmethod
    def _norm_analysis(value: str) -> str:
        return value.replace("-", "").replace("_", "").lower()

    @staticmethod
    def _ok(value: Optional[str], include: list, exclude: list, norm=lambda v: v.lower()) -> bool:
        if value is None:
            return True
        v = norm(value)
        if include and v not in {norm(i) for i in include}:
            return False
        if exclude and v in {norm(e) for e in exclude}:
            return False
        return True

    def config_ok(self, config: str) -> bool:
        return self._ok(config, self.configs, self.exclude_configs)

    def name_ok(self, name: str) -> bool:
        return self._ok(name, self.names, self.exclude_names)

    def folder_ok(self, folder: str) -> bool:
        return self._ok(folder, self.folders, self.exclude_folders)

    def study_ok(self, label: str) -> bool:
        return self._ok(label, self.studies, self.exclude_studies)

    def analysis_ok(self, analysis: str) -> bool:
        return self._ok(analysis, self.analyses, self.exclude_analyses, self._norm_analysis)

    def energy_ok(self, energy: Optional[str]) -> bool:
        return self._ok(energy, self.energies, self.exclude_energies)

    def study_group_ok(self, study: Study) -> bool:
        """--study accepts a label or a group name."""
        if not self.studies and not self.exclude_studies:
            return True
        keys = {study.label.lower(), study.group.lower()}
        if self.studies and not keys & {s.lower() for s in self.studies}:
            return False
        if self.exclude_studies and keys & {s.lower() for s in self.exclude_studies}:
            return False
        return True

    @classmethod
    def from_args(cls, args) -> "Filters":
        return cls(
            configs=args.config or [],
            exclude_configs=args.exclude_config or [],
            names=args.name or [],
            exclude_names=args.exclude_name or [],
            folders=args.folder or [],
            exclude_folders=args.exclude_folder or [],
            studies=args.study or [],
            exclude_studies=args.exclude_study or [],
            analyses=args.analysis or [],
            exclude_analyses=args.exclude_analysis or [],
            energies=args.energy or [],
            exclude_energies=args.exclude_energy or [],
        )


def add_filter_args(parser: argparse.ArgumentParser) -> None:
    for dim in ("config", "name", "folder", "study", "analysis", "energy"):
        parser.add_argument(f"--{dim}", action="append", default=None)
        parser.add_argument(f"--exclude-{dim}", dest=f"exclude_{dim}", action="append", default=None)


# ---------------------------------------------------------------------------
# Remote path model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RemoteFile:
    """One pkl under SOLAR output/data, decoded from its path."""

    relpath: str
    family: Optional[str]  # one of FAMILIES, or None for other kinds in live dirs
    tree: str  # analysis | cutflow | nhits
    config: str
    name: str
    folder: str
    label: str  # study label (default for the main analysis)
    analysis: str  # DayNight | HEP | Sensitivity
    kind: str  # filename kind, e.g. Counts, Exposure, SolarEnergy_DayNight_Cutflow
    energy: Optional[str] = None  # cutflow energy token

    @property
    def basename(self) -> str:
        return self.relpath.rsplit("/", 1)[-1]

    @property
    def study(self) -> Optional[Study]:
        return STUDY_BY_LABEL.get(self.label)

    @property
    def analysis_agnostic_basename(self) -> bool:
        return self.tree == "analysis" and f"_{self.analysis}_" not in self.basename

    def local_targets(self) -> list:
        """Paths (relative to input/data) this file is copied to."""
        targets = []
        if self.tree == "analysis":
            if self.analysis_agnostic_basename:
                # Oscillogram / Signal1D_* / *_Templates are written by every
                # analysis with the same basename (and slightly different
                # contents). Keep them apart per analysis; the flat reference
                # copy comes from the first analysis in registry order.
                targets.append(f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{ANALYSIS_LOWER[self.analysis]}/{self.basename}")
                if self.folder == REFERENCE_FOLDER and self.label == DEFAULT_LABEL and self.analysis == ALL_ANALYSES[0]:
                    targets.append(self.basename)
                return targets
            targets.append(f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{self.basename}")
            if self.folder == REFERENCE_FOLDER and self.label == DEFAULT_LABEL:
                targets.append(self.basename)
        elif self.tree == "cutflow":
            plain = f"{self.config}_{self.name}_{self.energy}_{self.analysis}_Cutflow.pkl"
            targets.append(f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{plain}")
            if self.folder == REFERENCE_FOLDER:
                targets.append(self.basename)  # keeps the _fiduc_truth suffix for the flat copy
        elif self.tree == "nhits":
            targets.append(self.basename)
        return targets


_CUTFLOW_RE = re.compile(r"^(?P<energy>[A-Za-z0-9]+)_(?P<analysis>DayNight|HEP|Sensitivity)_Cutflow(?P<suffix>(_[A-Za-z0-9_]+)?)\.pkl$")
_ANALYSIS_RE = re.compile(r"^(?P<analysis>DayNight|HEP|Sensitivity)_(?P<kind>[A-Za-z0-9_]+)\.pkl$")


def _strip_prefix(basename: str, config: str, name: str) -> Optional[str]:
    prefix = f"{config}_{name}_"
    return basename[len(prefix):] if basename.startswith(prefix) else None


def decode_remote_path(relpath: str) -> tuple:
    """Return (RemoteFile | None, reason). reason is '' when accepted."""
    parts = relpath.split("/")
    if len(parts) < 2 or not relpath.endswith(".pkl"):
        return None, "not a pkl"

    if parts[0] == "analysis":
        if len(parts) != 7:
            return None, "stale pre-August-2026 layout (no study label directory)"
        _, adir, config, name, folder, label, fn = parts
        analysis = ANALYSIS_BY_DIR.get(adir)
        if analysis is None:
            return None, f"unknown analysis directory {adir}"
        if label in DEAD_LABELS:
            return None, f"dead label {label}"
        study = STUDY_BY_LABEL.get(label)
        if study is None:
            return None, f"unknown label {label}"
        if analysis not in study.analyses or folder not in study.folders:
            return None, f"stale: {label} is not run for {analysis}/{folder}"
        if config not in study.configs:
            return None, f"stale: {label} is not run for {config}"
        rest = _strip_prefix(fn, config, name)
        if rest is None:
            return None, "basename does not carry config/name"
        m = _ANALYSIS_RE.match(rest)
        kind = m.group("kind") if m and m.group("analysis") == analysis else rest[:-4]
        family = kind if (m and kind in KINDS[analysis]) else None
        return RemoteFile(relpath, family, "analysis", config, name, folder, label, analysis, kind), ""

    if parts[0] == "solar" and parts[1] == "cutflow":
        if len(parts) != 7:
            return None, "malformed cutflow path (missing component name)"
        _, _, config, name, folder, alow, fn = parts
        if name not in COMPONENT_NAMES:
            return None, f"unknown component {name}"
        analysis = ANALYSIS_BY_LOWER.get(alow)
        if analysis is None:
            return None, f"unknown analysis directory {alow}"
        rest = _strip_prefix(fn, config, name)
        if rest is None:
            return None, "malformed cutflow basename (missing name token)"
        m = _CUTFLOW_RE.match(rest)
        if m is None or m.group("analysis") != analysis:
            return None, "malformed cutflow basename"
        energy = m.group("energy")
        suffix = m.group("suffix").lstrip("_")
        if suffix:
            if suffix not in STUDY_BY_LABEL:
                return None, f"cutflow suffix {suffix} is not a live label"
            label = suffix
        else:
            label = DEFAULT_LABEL
            owners = [s for s in STUDIES if s.cutflow_energy == energy and s.label not in CUTFLOW_SUFFIX_LABELS]
            if not owners:
                return None, f"cutflow energy {energy} belongs to no live study"
            if not any(analysis in s.analyses and folder in s.folders for s in owners):
                return None, f"stale: {energy} cutflow is not produced for {analysis}/{folder}"
        return RemoteFile(relpath, "Cutflow", "cutflow", config, name, folder, label, analysis, rest[:-4], energy), ""

    if parts[0] == "solar" and parts[1] == "nhits":
        if len(parts) != 7:
            return None, "not a weighted fiducial distribution"
        _, _, config, name, folder, alow, fn = parts
        if name not in COMPONENT_NAMES:
            return None, f"unknown component {name}"
        analysis = ANALYSIS_BY_LOWER.get(alow)
        if analysis is None:
            return None, f"unknown analysis directory {alow}"
        rest = _strip_prefix(fn, config, name)
        if rest is None or rest != f"Weighted_Distributions_Fiducial_{analysis}.pkl":
            return None, "not a weighted fiducial distribution"
        return RemoteFile(relpath, "Weighted", "nhits", config, name, folder, DEFAULT_LABEL, analysis, rest[:-4]), ""

    return None, "outside the synced trees"


def passes_filters(rf: RemoteFile, flt: Filters) -> bool:
    study = rf.study
    return (
        flt.config_ok(rf.config)
        and flt.name_ok(rf.name)
        and flt.folder_ok(rf.folder)
        and flt.analysis_ok(rf.analysis)
        and flt.energy_ok(rf.energy)
        and (study is None or flt.study_group_ok(study))
    )


# ---------------------------------------------------------------------------
# Expected files
# ---------------------------------------------------------------------------


def expected_files(flt: Optional[Filters] = None) -> list:
    """Every file of the five families that should exist on the remote."""
    flt = flt or Filters()
    out = []

    for study in STUDIES:
        if not flt.study_group_ok(study):
            continue
        for folder in study.folders:
            if not flt.folder_ok(folder):
                continue
            for analysis in study.analyses:
                if not flt.analysis_ok(analysis):
                    continue
                for config in study.configs:
                    if not flt.config_ok(config) or not flt.name_ok(SIGNAL_NAME):
                        continue
                    for kind in KINDS[analysis]:
                        rel = (
                            f"analysis/{ANALYSES[analysis]}/{config}/{SIGNAL_NAME}/{folder}/{study.label}/"
                            f"{config}_{SIGNAL_NAME}_{analysis}_{kind}.pkl"
                        )
                        out.append(RemoteFile(rel, kind, "analysis", config, SIGNAL_NAME, folder, study.label, analysis, kind))

    # Cutflow: one file per (config, name, folder, analysis, energy [, suffix])
    seen = set()
    for study in STUDIES:
        if study.cutflow_energy is None or not flt.study_group_ok(study):
            continue
        suffix = f"_{study.label}" if study.label in CUTFLOW_SUFFIX_LABELS else ""
        label = study.label if suffix else DEFAULT_LABEL
        for folder in study.folders:
            if not flt.folder_ok(folder):
                continue
            for analysis in study.analyses:
                if not flt.analysis_ok(analysis) or not flt.energy_ok(study.cutflow_energy):
                    continue
                for config in study.configs:
                    if not flt.config_ok(config):
                        continue
                    for name in COMPONENT_NAMES:
                        if not flt.name_ok(name):
                            continue
                        rel = (
                            f"solar/cutflow/{config}/{name}/{folder}/{ANALYSIS_LOWER[analysis]}/"
                            f"{config}_{name}_{study.cutflow_energy}_{analysis}_Cutflow{suffix}.pkl"
                        )
                        if rel in seen:
                            continue
                        seen.add(rel)
                        kind = f"{study.cutflow_energy}_{analysis}_Cutflow{suffix}"
                        out.append(RemoteFile(rel, "Cutflow", "cutflow", config, name, folder, label, analysis, kind, study.cutflow_energy))

    # Weighted fiducial distributions: truncated only, DayNight and HEP only
    if flt.folder_ok(REFERENCE_FOLDER) and flt.study_ok(DEFAULT_LABEL):
        for analysis in ("DayNight", "HEP"):
            if not flt.analysis_ok(analysis):
                continue
            for config in CONFIGS:
                if not flt.config_ok(config):
                    continue
                for name in COMPONENT_NAMES:
                    if not flt.name_ok(name):
                        continue
                    kind = f"Weighted_Distributions_Fiducial_{analysis}"
                    rel = f"solar/nhits/{config}/{name}/{REFERENCE_FOLDER}/{ANALYSIS_LOWER[analysis]}/{config}_{name}_{kind}.pkl"
                    out.append(RemoteFile(rel, "Weighted", "nhits", config, name, REFERENCE_FOLDER, DEFAULT_LABEL, analysis, kind))

    return out


# ---------------------------------------------------------------------------
# rsync include rules
# ---------------------------------------------------------------------------


def rsync_rules(flt: Optional[Filters] = None) -> list:
    """Include rules (for ``rsync --include-from``) anchored at output/data.

    Directories are all included (``*/``) and the caller appends ``--exclude='*'``
    plus ``--prune-empty-dirs``; only files matching a rule below transfer.
    """
    flt = flt or Filters()
    rules = ["+ */"]

    configs = [c for c in CONFIGS if flt.config_ok(c)]
    config_glob = "*" if len(configs) == len(CONFIGS) else None

    for study in STUDIES:
        if not flt.study_group_ok(study):
            continue
        study_configs = [c for c in study.configs if flt.config_ok(c)]
        for folder in study.folders:
            if not flt.folder_ok(folder):
                continue
            for analysis in study.analyses:
                if not flt.analysis_ok(analysis) or not flt.name_ok(SIGNAL_NAME):
                    continue
                cfgs = [config_glob] if (config_glob and len(study_configs) == len(study.configs)) else study_configs
                for cfg in cfgs:
                    rules.append(f"+ /analysis/{ANALYSES[analysis]}/{cfg}/{SIGNAL_NAME}/{folder}/{study.label}/*.pkl")

    names = [n for n in COMPONENT_NAMES if flt.name_ok(n)]
    for name in names:
        for cfg in ([config_glob] if config_glob else configs):
            for folder in [f for f in FOLDERS if flt.folder_ok(f)]:
                for analysis in [a for a in ALL_ANALYSES if flt.analysis_ok(a)]:
                    rules.append(f"+ /solar/cutflow/{cfg}/{name}/{folder}/{ANALYSIS_LOWER[analysis]}/*_Cutflow*.pkl")
            if flt.folder_ok(REFERENCE_FOLDER):
                for analysis in [a for a in ("DayNight", "HEP") if flt.analysis_ok(a)]:
                    rules.append(
                        f"+ /solar/nhits/{cfg}/{name}/{REFERENCE_FOLDER}/{ANALYSIS_LOWER[analysis]}/*_Weighted_Distributions_Fiducial_{analysis}.pkl"
                    )
    return rules


# ---------------------------------------------------------------------------
# Routing a synced mirror into input/data
# ---------------------------------------------------------------------------


def iter_mirror(mirror: Path) -> Iterator[str]:
    mirror = Path(mirror)
    for root, _dirs, files in os.walk(mirror):
        for fn in files:
            if fn.endswith(".pkl"):
                yield os.path.relpath(os.path.join(root, fn), mirror)


def _same_file(src: Path, dst: Path) -> bool:
    try:
        a, b = src.stat(), dst.stat()
    except FileNotFoundError:
        return False
    return a.st_size == b.st_size and int(a.st_mtime) == int(b.st_mtime)


def route_mirror(mirror: Path, data_dir: Path, flt: Filters, force: bool = False, dry_run: bool = False, verbose: bool = False) -> dict:
    """Copy every accepted mirror file to its local targets; return a report."""
    mirror, data_dir = Path(mirror), Path(data_dir)
    report = {
        "copied": defaultdict(Counter),  # family -> {new, updated, unchanged}
        "skipped": Counter(),  # reason -> count
        "skipped_paths": defaultdict(list),
        "present": set(),  # accepted remote relpaths (after filters)
        "targets": {},  # remote relpath -> [local relpaths]
    }
    for rel in sorted(iter_mirror(mirror)):
        rf, reason = decode_remote_path(rel)
        if rf is None:
            report["skipped"][reason] += 1
            report["skipped_paths"][reason].append(rel)
            continue
        if not passes_filters(rf, flt):
            report["skipped"]["filtered out"] += 1
            continue
        report["present"].add(rel)
        family = rf.family or "other"
        targets = rf.local_targets()
        report["targets"][rel] = targets
        src = mirror / rel
        for target in targets:
            dst = data_dir / target
            if dst.exists() and not force and _same_file(src, dst):
                report["copied"][family]["unchanged"] += 1
                continue
            status = "updated" if dst.exists() else "new"
            report["copied"][family][status] += 1
            if verbose:
                print(f"    {status:8s} {target}")
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    return report


def legacy_flat_study_files(data_dir: Path) -> list:
    """Old flat ``input/data/studies/*.pkl`` copies (pre-tree layout)."""
    studies = Path(data_dir) / STUDIES_DIRNAME
    if not studies.is_dir():
        return []
    return sorted(p for p in studies.iterdir() if p.is_file() and p.suffix == ".pkl")


def missing_report(expected: list, present: set) -> dict:
    """Group missing expected files: (family, folder/label, analysis, kind) -> [configs/names]."""
    grouped = defaultdict(list)
    for rf in expected:
        if rf.relpath in present:
            continue
        who = rf.config if rf.name == SIGNAL_NAME and rf.tree == "analysis" else f"{rf.config}/{rf.name}"
        grouped[(rf.family, f"{rf.folder}/{rf.label}", rf.analysis, rf.kind)].append(who)
    return grouped


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_rules = sub.add_parser("rules", help="Print rsync include rules")
    add_filter_args(p_rules)

    p_exp = sub.add_parser("expected", help="Print expected remote paths")
    add_filter_args(p_exp)
    p_exp.add_argument("--family", action="append", default=None)

    p_lab = sub.add_parser("labels", help="Print live study labels")
    p_lab.add_argument("--dead", action="store_true", help="Print retired labels instead")

    p_route = sub.add_parser("route", help="Copy a synced mirror into input/data and report")
    p_route.add_argument("mirror")
    p_route.add_argument("data_dir")
    p_route.add_argument("--force", action="store_true")
    p_route.add_argument("--dry-run", action="store_true")
    p_route.add_argument("--verbose", action="store_true")
    p_route.add_argument("--prune-legacy", action="store_true", help="Delete flat input/data/studies/*.pkl files from the old layout")
    add_filter_args(p_route)

    args = parser.parse_args(argv)

    if args.command == "labels":
        for label in (sorted(DEAD_LABELS) if args.dead else LIVE_LABELS):
            print(label)
        return 0

    flt = Filters.from_args(args)

    if args.command == "rules":
        print("\n".join(rsync_rules(flt)))
        return 0

    if args.command == "expected":
        for rf in expected_files(flt):
            if args.family and rf.family not in args.family:
                continue
            print(rf.relpath)
        return 0

    if args.command == "route":
        report = route_mirror(args.mirror, args.data_dir, flt, force=args.force, dry_run=args.dry_run, verbose=args.verbose)
        expected = expected_files(flt)
        present = report["present"]

        print("==> Copied into input/data (per family)")
        print(f"    {'family':14s} {'new':>6s} {'updated':>8s} {'unchanged':>10s}")
        for family in list(FAMILIES) + ["other"]:
            c = report["copied"].get(family)
            if not c:
                continue
            print(f"    {family:14s} {c['new']:6d} {c['updated']:8d} {c['unchanged']:10d}")

        if report["skipped"]:
            print("==> Skipped mirror files")
            for reason, n in sorted(report["skipped"].items(), key=lambda kv: -kv[1]):
                print(f"    {n:5d}  {reason}")

        print("==> Expected files (five families) per family")
        exp_by_family = Counter(rf.family for rf in expected)
        have_by_family = Counter(rf.family for rf in expected if rf.relpath in present)
        for family in FAMILIES:
            n_exp, n_have = exp_by_family.get(family, 0), have_by_family.get(family, 0)
            if n_exp:
                print(f"    {family:14s} {n_have:5d} / {n_exp:<5d} present" + ("" if n_have == n_exp else f"   ({n_exp - n_have} missing)"))

        missing = missing_report(expected, present)
        if missing:
            print("==> Expected files missing on the remote")
            for (family, where, analysis, kind), who in sorted(missing.items()):
                print(f"    {family:12s} {where:28s} {analysis:12s} {kind:45s} {', '.join(who)}")
        else:
            print("==> No expected file is missing on the remote")

        legacy = legacy_flat_study_files(args.data_dir)
        if legacy:
            if args.prune_legacy and not args.dry_run:
                for p in legacy:
                    p.unlink()
                print(f"==> Deleted {len(legacy)} legacy flat file(s) from input/data/studies/ (old layout)")
            else:
                print(
                    f"==> {len(legacy)} legacy flat file(s) remain in input/data/studies/ from the old layout; "
                    "the tree copies take precedence, pass --prune-legacy to delete them"
                )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(_cli())
