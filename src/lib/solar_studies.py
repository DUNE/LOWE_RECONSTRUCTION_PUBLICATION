"""Registry of SOLAR study outputs and the local layout they are synced into.

SOLAR's study orchestrator (``src/pipelines/run_studies.py``) writes every
per-study result under ``output/data`` in three trees (paths relative to it):

    analysis/{day-night|hep|sensitivity}/{config}/marley/{folder}/{label}/{config}_marley_{Analysis}_{Kind}.pkl
    solar/cutflow/{config}/{name}/{folder}/{analysis}/{config}_{name}_{Energy}_{Analysis}_Cutflow{suffix}.pkl
    solar/nhits/{config}/{name}/truncated/{daynight|hep}/{config}_{name}_Weighted_Distributions_Fiducial_{DayNight|HEP}.pkl

The other SOLAR outputs the plot macros read live in trees without
folder/label/analysis levels, grouped here into flat families (FLAT_FAMILIES:
reconstruction, calibration, workflow, marley, background, event, analysisdata):

    {subdir}/{config}/{name}/{config}_{name}_{Kind}.pkl      default layout; (subdir, Kind) registered per family

``{folder}`` is the background model (``truncated`` is the reference) and
``{label}`` the study label (``default`` for the main analysis). The label is
a directory, so filenames are identical across studies and the folder/label
dimensions would collide when flattened by basename. Locally every file has
exactly one copy (nothing is written flat into input/data since 2026-09-25):

    input/data/studies/{folder}/{label}/{config}_{name}_{...}.pkl            analysis results, cutflows (no _fiduc_truth
                                                                             suffix: the label directory carries it) and,
                                                                             under truncated/default, the nhits distributions
    input/data/studies/{folder}/{label}/{daynight|hep|sensitivity}/{...}.pkl analysis-agnostic basenames (Oscillogram, Signal1D_*)
    input/data/{subdir}/{config}_{name}_{Kind}.pkl                           flat families, e.g. vertex/resolution/

``lib.imports`` falls back to ``studies/truncated/default/`` for a bare
``--datafile`` (so the reference results need no ``--path``) and resolves
``--path studies --datafile {Kind}_{label}`` (the legacy flat convention),
``--path studies/{folder}/{label} --datafile {Kind}`` and ``--path
studies/{folder} --datafile {Kind}_{label}`` against the tree. Flat-family
commands pass ``--path {subdir}``, e.g. ``script_aggregate_table.py --path
vertex/resolution --datafile Vertex_Resolution``. The full local layout,
including the local-only topic folders and archive/, is in docs/input_data_layout.md.

The study table below mirrors ``lib/study.py`` ``STUDY_VARIANTS`` in SOLAR
(as of 2026-09-17). It is the single source of truth for which label
directories are live: the remote also still holds directories of retired
labels that must not be synced.

``--study {family}`` (e.g. ``--study calibration``) selects one flat family
alone; any other ``--study``, ``--folder``, ``--analysis`` or ``--energy``
include filter drops the flat families (those dimensions do not exist for
them). ``--name`` replaces the sample names of every family selection.

This module is used both as a library (``from lib.solar_studies import ...``)
and as a CLI by ``scripts/sync_solar_data.sh``:

    python3 src/lib/solar_studies.py rules  [filters]      rsync include rules (stdin for --include-from)
    python3 src/lib/solar_studies.py route  MIRROR DATA_DIR [--force] [--dry-run] [filters]
    python3 src/lib/solar_studies.py expected [filters]    expected remote paths, one per line
    python3 src/lib/solar_studies.py labels [--dead]       live (or retired) labels, one per line
    python3 src/lib/solar_studies.py sources [filters]     remote trees to rsync (those with include rules)
    python3 src/lib/solar_studies.py kinds [--family F] [--dead]         live (or dead) flat-family "study subdir Kind" rows
    python3 src/lib/solar_studies.py kinds [--family F] --classify < relpaths   live/dead/unknown kinds on the remote
"""

from __future__ import annotations

import argparse
import os
import pickle
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
STUDY_FAMILIES = ("Counts", "Exposure", "Contours", "10Y_Contours", "Cutflow", "Weighted")

CUTFLOW_DEFAULT_ENERGY = "SolarEnergy"
CUTFLOW_SUFFIX_LABELS = ("fiduc_truth",)  # studies with their own cutflow file, tagged by a filename suffix

# ---------------------------------------------------------------------------
# Flat families: SOLAR trees without folder/label/analysis levels
# ---------------------------------------------------------------------------
# Each family owns one or more SOLAR sub-directories and lists, per
# sub-directory, the kinds that are synced (only these: kind names are matched
# exactly and case-sensitively). A remote file is {subdir}/{layout}, by default
#     {subdir}/{config}/{name}/{config}_{name}_{kind}.pkl
# and is copied to input/data/{subdir}/{basename}; commands read it with
# --path {subdir}. Which (config, name, kind) combinations are synced is given
# by the family's selections; `--study {family.study}` syncs one family alone
# and --name replaces the selections' sample names.

DEFAULT_LAYOUT = "{config}/{name}/{config}_{name}_{kind}.pkl"
LEGACY_CONFIGS = ("hd_1x2x6", "vd_1x8x14_3view_30deg")  # signal-only productions (marley_official only)
ALL_CONFIGS = CONFIGS + LEGACY_CONFIGS
BACKGROUND_NAMES = ("gamma", "neutron", "radiological")


@dataclass(frozen=True)
class Selection:
    configs: tuple
    names: tuple
    kinds: Optional[tuple] = None  # None: every kind of the family
    complete: bool = False  # every combination should exist (completeness report)


@dataclass(frozen=True, eq=False)
class FlatFamily:
    family: str  # FAMILIES entry shown in the route summary
    study: str  # --study value selecting this family
    files: dict  # {subdir: (kind, ...)}
    selections: tuple  # (Selection, ...) of synced (config, name, kind) combinations
    dead: dict = field(default_factory=dict)  # {subdir: (kind, ...)} legacy kinds still on the remote, never synced
    layouts: dict = field(default_factory=dict)  # {kind: (layout, ...)} below {subdir}; DEFAULT_LAYOUT otherwise

    @property
    def configs(self) -> tuple:
        return tuple(dict.fromkeys(c for sel in self.selections for c in sel.configs))

    def layouts_of(self, kind: str) -> tuple:
        return self.layouts.get(kind, (DEFAULT_LAYOUT,))

    def combos(self, flt: "Filters", complete_only: bool = False):
        """Unique (subdir, config, name, kind, relpath) rows selected by the filters."""
        seen = set()
        for sel in self.selections:
            if complete_only and not sel.complete:
                continue
            names = [n for n in (flt.names or sel.names) if not n or flt.name_ok(n)]
            configs = [c for c in sel.configs if flt.config_ok(c)]
            for subdir, kinds in self.files.items():
                for kind in kinds:
                    if sel.kinds is not None and kind not in sel.kinds:
                        continue
                    for layout in self.layouts_of(kind):
                        for config in (configs if "{config}" in layout else [""]):
                            for name in (names if "{name}" in layout else [""]):
                                rel = f"{subdir}/" + layout.format(config=config, name=name, kind=kind)
                                if rel not in seen:
                                    seen.add(rel)
                                    yield subdir, config, name, kind, rel

    def selected(self, flt: "Filters", config: str, name: str, kind: str) -> bool:
        if config and not flt.config_ok(config):
            return False
        for sel in self.selections:
            if sel.kinds is not None and kind not in sel.kinds:
                continue
            if config and config not in sel.configs:
                continue
            if name and name not in [n for n in (flt.names or sel.names) if flt.name_ok(n)]:
                continue
            return True
        return False

    def match(self, subdir: str, rest: str) -> tuple:
        """Decode ``rest`` (path below subdir) -> (config, name, kind, status); status live|dead|None."""
        cfg_alt = "|".join(re.escape(c) for c in sorted(self.configs, key=len, reverse=True))
        candidates = [(k, "live") for k in self.files.get(subdir, ())] + [(k, "dead") for k in self.dead.get(subdir, ())]
        for kind, status in candidates:
            for layout in (self.layouts_of(kind) if status == "live" else (DEFAULT_LAYOUT,)):
                pattern = re.escape(layout).replace(re.escape("{kind}"), re.escape(kind))
                for key, group in (("config", f"(?:{cfg_alt}|[^/]+?)"), ("name", r"[^/]+?")):
                    token = re.escape("{" + key + "}")
                    pattern = pattern.replace(token, f"(?P<{key}>{group})", 1).replace(token, f"(?P={key})")
                m = re.match(f"^{pattern}$", rest)
                if m:
                    return m.groupdict().get("config") or "", m.groupdict().get("name") or "", kind, status
        return None, None, None, None


# Per-sample detector-reconstruction results. SOLAR regenerated the kinds of the
# complete selection for the four CONFIGS (name marley) on 2026-09-24.
# Adjacent_Cluster_Counts_Slim is live and Adjacent_Cluster_Counts_slim dead
# (they collide on a case-insensitive disk).
RECO_SCANS = ("Drift", "Energy", "Plane")
RECO_REGENERATED = (
    "Vertex_Resolution", "Resolution", "Purity_Match_Resolution", "Vertex_Matrix_X",
    "Vertex_Reconstruction_Efficiency", "Vertex_3D_Quantile_Thresholds", "Fiducial_Efficiency", "Fiducial_Purity",
    "Cumulative_Vertex_Error", "Vertex_Smearing", "Neutrino_Energy_Resolution", "MainK_Resolution_GaussianFit",
    "Electron_Energy_Resolution", "Adjacent_Cluster_Counts", "Adjacent_Cluster_Counts_Slim", "Adjacent_Cluster_Distributions",
    "OpFlash_Efficiency",
    *(f"{what}_Efficiency_{scan}_Scan" for what in ("MatchedOpFlash", "Neutrino", "TPC_Cluster") for scan in RECO_SCANS),
    *(f"Signal_AdjOpFlash{q}_{s}Scan" for q in ("Num", "PE") for s in ("Plane", "Radial")),
    "Preselection_Efficiency", "Clustering_Efficiency_Energy", "Clustering_Efficiency_NHit",
)
RECONSTRUCTION = FlatFamily(
    "Reconstruction",
    "reconstruction",
    files={
        "vertex/resolution": ("Vertex_Resolution", "Resolution", "Purity_Match_Resolution", "Vertex_Matrix_X"),
        "vertex/reconstruction": ("Vertex_Reconstruction_Efficiency", "Vertex_3D_Quantile_Thresholds"),
        "vertex/fiducial": ("Fiducial_Efficiency", "Fiducial_Purity"),
        "vertex/smearing": ("Cumulative_Vertex_Error", "Vertex_Smearing"),  # Vertex_Smearing ~8 MB
        "TPC/resolution/neutrino": ("Neutrino_Energy_Resolution", "MainK_Resolution_GaussianFit"),
        "TPC/resolution/electron": ("Electron_Energy_Resolution",),
        "TPC/adjcluster": ("Adjacent_Cluster_Counts", "Adjacent_Cluster_Counts_Slim", "Adjacent_Cluster_Distributions"),  # Counts up to ~11 MB
        "PDS/matchedopflash": (
            "OpFlash_Efficiency",
            *(f"{what}_Efficiency_{scan}_Scan" for what in ("MatchedOpFlash", "Neutrino", "TPC_Cluster") for scan in RECO_SCANS),
        ),
        "PDS/adjopflash": tuple(f"Signal_AdjOpFlash{q}_{s}Scan" for q in ("Num", "PE") for s in ("Plane", "Radial")),
        "PDS/opflash": ("Light_Map_Fitting_Data", "Light_Map_Fitting_Parameters"),
        "preselection/efficiency": ("Preselection_Efficiency",),
        "preselection/clustering": ("Clustering_Efficiency_Energy", "Clustering_Efficiency_NHit"),
    },
    selections=(
        Selection(CONFIGS, (SIGNAL_NAME,), RECO_REGENERATED, complete=True),  # thesis: every regenerated kind
        # lowe paper (marley_official): only the kinds its commands read
        Selection(("hd_1x2x6_centralAPA", "vd_1x8x14_3view_30deg_nominal"), ("marley_official",), (
            "Vertex_Resolution", "Purity_Match_Resolution", "Fiducial_Purity", "Vertex_Smearing", "Adjacent_Cluster_Counts",
            "Clustering_Efficiency_Energy", "Clustering_Efficiency_NHit")),
        Selection(("hd_1x2x6_centralAPA", "hd_1x2x6_lateralAPA", "vd_1x8x14_3view_30deg_nominal"), ("marley_official",), (
            "Vertex_Reconstruction_Efficiency", "Fiducial_Efficiency", "Cumulative_Vertex_Error", "Electron_Energy_Resolution",
            "TPC_Cluster_Efficiency_Drift_Scan")),
        Selection(("hd_1x2x6_lateralAPA", "vd_1x8x14_3view_30deg_nominal"), ("marley_official",), ("Adjacent_Cluster_Distributions",)),
        Selection(CONFIGS, ("marley_official",), ("Neutrino_Energy_Resolution",)),
        # background samples
        Selection(("hd_1x2x6_centralAPA", "vd_1x8x14_3view_30deg_nominal"), ("gamma", "neutron"), ("Clustering_Efficiency_Energy", "Clustering_Efficiency_NHit")),
        Selection(("hd_1x2x6_centralAPA", "vd_1x8x14_3view_30deg_nominal"), BACKGROUND_NAMES, ("Purity_Match_Resolution",)),
        Selection(("hd_1x2x6_centralAPA",), BACKGROUND_NAMES, ("Adjacent_Cluster_Counts_Slim",)),
        Selection(CONFIGS, BACKGROUND_NAMES, ("Signal_AdjOpFlashNum_RadialScan",)),
        # clustering-window and flash-matching criterion scans
        Selection(("hd_1x2x6_centralAPA",),
                  tuple(f"marley_adjchannel{n}" for n in (1, 5, 7, 9)) + tuple(f"marley_adjtime{n}" for n in (5, 10, 15, 20, 30)),
                  ("Clustering_Efficiency_Energy",)),
        Selection(("hd_1x2x6_centralAPA", "vd_1x8x14_3view_30deg_shielded"),
                  ("marley_exponent0", "marley_exponent1", "marley_exponent2", "marley_maximum"),
                  ("TPC_Cluster_Efficiency_Plane_Scan",)),
        # signal-only legacy productions
        Selection(LEGACY_CONFIGS, ("marley_official",), (
            *(f"TPC_Cluster_Efficiency_{scan}_Scan" for scan in RECO_SCANS), "Electron_Energy_Resolution", "Neutrino_Energy_Resolution",
            "Fiducial_Efficiency", "Vertex_Reconstruction_Efficiency", "Preselection_Efficiency",
            "Light_Map_Fitting_Data", "Light_Map_Fitting_Parameters")),
    ),
    # Renamed or merged by SOLAR; nested sub-folders (vertex/resolution/{config}/{name}/Vertex_Matrix_X/) are always dead.
    dead={
        "TPC/resolution/neutrino": ("Neutrino_Energy_Resolution_NHits",),
        "TPC/resolution/electron": tuple(
            f"{c}_Clustering_{d}_Drift_Correction_NHits{n}" for c in ("Ideal", "Reco") for d in ("None", "Reco", "True") for n in (1, 2, 3)
        ),
        "TPC/adjcluster": ("AdjCluster_Distributions", "Adjacent_Cluster_Counts_slim"),
        "PDS/matchedopflash": ("MatchedOpFlashEfficiency_Drift_Scan", "MatchedOpFlashEfficiency_Energy_Scan"),
        "PDS/adjopflash": ("Signal_vs_Background_Adj_OpFlashes", "Signal_vs_Background_Adj_OpFlashes_PE"),
        "preselection/clustering": ("Clustering_Efficiency", "Preselection_Efficiency", *(f"Reco_NHit_Efficiency_{n}" for n in range(1, 10))),
        "preselection/production": ("Production_Distributions", "Production_Limits"),  # not regenerated
    },
)

# Energy calibration and charge corrections (SOLAR workflow/calibration, workflow/correction).
CALIBRATION = FlatFamily(
    "Calibration",
    "calibration",
    files={
        "workflow/calibration": ("CheatedEnergy_Electron_Calibration", "PrimaryEnergy_Electron_Calibration",
                                 "Cheated_Resolution_GaussianFit", "Primary_Resolution_GaussianFit"),
        "workflow/correction": ("Charge_Correction_Factor", "ElectronCharge_Correction_Factor", "Charge_Lifetime_Correction",
                                "Cluster_Distributions", "NHit_Distributions"),
    },
    selections=(
        Selection(LEGACY_CONFIGS, ("marley_official",), (
            "Charge_Correction_Factor", "ElectronCharge_Correction_Factor", "Charge_Lifetime_Correction", "Cluster_Distributions", "NHit_Distributions")),
        Selection(("hd_1x2x6_centralAPA",), ("marley_official",), (
            "CheatedEnergy_Electron_Calibration", "Cheated_Resolution_GaussianFit", "Primary_Resolution_GaussianFit", "Charge_Lifetime_Correction")),
        Selection(("hd_1x2x6_centralAPA", "vd_1x8x14_3view_30deg_nominal"), ("marley_official",), ("PrimaryEnergy_Electron_Calibration",)),
    ),
)

# Reconstruction-workflow studies: energy reconstruction, cluster discrimination, wire planes.
WORKFLOW = FlatFamily(
    "Workflow",
    "workflow",
    files={
        "workflow/reconstruction": ("Neutrino_Energy", "Gamma_Energy"),
        "workflow/discrimination": ("AdjCl_Selection", "Cluster_Discriminant", "Random_Forest_Importance", "Neutrino_CC_Production"),
        "workflow/wire_comparison": ("Wire_Plane_Comparison",),
    },
    selections=(
        Selection(("hd_1x2x6_centralAPA", "hd_1x2x6_lateralAPA", "vd_1x8x14_3view_30deg_nominal"), (SIGNAL_NAME, "marley_official"), ("Neutrino_Energy",)),
        Selection(("hd_1x2x6_centralAPA", "hd_1x2x6"), ("marley_official",), ("Gamma_Energy",)),
        Selection(("hd_1x2x6_centralAPA",), ("marley_official",), ("AdjCl_Selection", "Cluster_Discriminant", "Random_Forest_Importance")),
        Selection(("hd_1x2x6",), ("marley_official",), ("Neutrino_CC_Production", "Wire_Plane_Comparison")),
    ),
)

# MARLEY generator-level distributions.
MARLEY = FlatFamily(
    "Marley",
    "marley",
    files={"marley/stacked": ("Neutrino_CC_Fraction", "Neutrino_Secondary_Probability")},
    selections=(Selection(("hd_1x2x6",), ("marley_official",)),),
)

# Background spectra: one global summary plus per-config files (no sample name).
BACKGROUND = FlatFamily(
    "Background",
    "background",
    files={"background": ("background_spectra_summary", "Background")},
    selections=(
        Selection(CONFIGS, ("",), ("background_spectra_summary",)),
        Selection(("hd_1x2x6_centralAPA",), ("",), ("Background",)),
    ),
    layouts={
        "background_spectra_summary": ("{kind}.pkl", "{config}/spectra/{config}_{kind}.pkl"),
        "Background": ("{config}/{config}_{kind}.pkl",),
    },
)

# Single-event displays and energy-deposition studies.
EVENT = FlatFamily(
    "Event",
    "event",
    files={"event": ("event_8719_display", "edep_electron_gap_cdf", "edep_electron_gap_percentiles")},
    selections=(Selection(("hd_1x2x6_centralAPA",), ("marley_edep",)),),
    layouts={"event_8719_display": ("{config}_{name}_{kind}.pkl",)},
)

# Weighted per-component analysis inputs (SOLAR solar/weighted/{config}/{name}/truncated/).
ANALYSIS_DATA = FlatFamily(
    "AnalysisData",
    "analysisdata",
    files={"solar/weighted": ("SolarEnergy_Sensitivity_AnalysisData",)},
    selections=(Selection(CONFIGS, ("gamma", "neutron")),),
    layouts={"SolarEnergy_Sensitivity_AnalysisData": ("{config}/{name}/truncated/{config}_{name}_{kind}.pkl",)},
)

FLAT_FAMILIES = (RECONSTRUCTION, CALIBRATION, WORKFLOW, MARLEY, BACKGROUND, EVENT, ANALYSIS_DATA)
FLAT_BY_STUDY = {f.study: f for f in FLAT_FAMILIES}
FLAT_BY_FAMILY = {f.family: f for f in FLAT_FAMILIES}
FLAT_META_COLUMNS = ("Config", "Version", "Geometry")  # ignored by the duplicate-content check


def _check_flat_families():
    owners = {}
    for f in FLAT_FAMILIES:
        for sd in {*f.files, *f.dead}:
            assert owners.setdefault(sd, f.family) == f.family, f"{sd} claimed by two families"
        for sd, kinds in f.files.items():
            assert len(set(kinds)) == len(kinds), f"duplicate kind in {sd}"
            assert not set(kinds) & set(f.dead.get(sd, ())), f"{sd}: kind both live and dead"
        all_kinds = {k for ks in f.files.values() for k in ks}
        for sel in f.selections:
            assert sel.kinds is None or set(sel.kinds) <= all_kinds, f"{f.family}: selection kind not registered"
    live = [sd for f in FLAT_FAMILIES for sd in f.files]
    for a in live:
        for b in live:
            assert a == b or not b.startswith(a + "/"), f"{b} nested in {a}"


_check_flat_families()
FAMILIES = STUDY_FAMILIES + tuple(f.family for f in FLAT_FAMILIES)


@dataclass(frozen=True)
class Study:
    label: str
    group: str
    folders: tuple = (REFERENCE_FOLDER,)
    analyses: tuple = ALL_ANALYSES
    configs: tuple = CONFIGS
    cutflow_energy: Optional[str] = None  # study-specific cutflow energy label (shared by the group)
    exclude: tuple = ()  # (analysis, config) pairs retired on the remote; never expected, never synced

    def analysis_configs(self, analysis: str) -> tuple:
        return tuple(c for c in self.configs if (analysis, c) not in self.exclude)


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
    Study("energy_spk", "energy", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SignalParticleK"),
    Study("energy_maink", "energy", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="MainK"),
    Study("energy_electronk", "energy", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="ElectronEnergy"),
    # charge threshold scan (all share the SelectedEnergy cutflow)
    Study("charge_Q0", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    Study("charge_Q50", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    Study("charge_Q100", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    Study("charge_Q500", "charge", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy="SelectedEnergy"),
    # background model normalisation (folder provides the isolation)
    Study("bkgmodel_nominal", "bkgmodel", ("nominal",), ALL_ANALYSES,
          exclude=(("Sensitivity", "vd_1x8x14_3view_30deg_shielded"),)),  # Sensitivity retired on the remote for VD shielded
    Study("bkgmodel_reduced", "bkgmodel", ("reduced",), ALL_ANALYSES,
          exclude=(("Sensitivity", "vd_1x8x14_3view_30deg_shielded"),)),  # Sensitivity retired on the remote for VD shielded
    # truth fiducialisation (has its own cutflow, tagged with a _fiduc_truth suffix)
    Study("fiduc_truth", "fiduc_truth", (REFERENCE_FOLDER,), ALL_ANALYSES, cutflow_energy=CUTFLOW_DEFAULT_ENERGY),
    Study("fiduc_truth_refvol", "fiduc_truth", (REFERENCE_FOLDER,), ALL_ANALYSES),
    # background gamma energy model
    # (Sensitivity outputs appear in the 2026-09-20 status table, so all three analyses are synced)
    Study("bkg_gamma_cluster", "bkg_gamma", (REFERENCE_FOLDER,), ALL_ANALYSES),
    Study("bkg_gamma_total", "bkg_gamma", (REFERENCE_FOLDER,), ALL_ANALYSES),
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

    def flat_ok(self, fam: "FlatFamily") -> bool:
        """Flat families have no folder/analysis/energy/label: any include filter
        on those dimensions drops them, unless --study names the family."""
        if fam.study in {s.lower() for s in self.exclude_studies}:
            return False
        if self.studies:
            return fam.study in {s.lower() for s in self.studies}
        return not (self.folders or self.analyses or self.energies)

    def flat_only(self) -> bool:
        """--study names only flat families: skip the analysis/cutflow/nhits rules."""
        return bool(self.studies) and all(s.lower() in FLAT_BY_STUDY for s in self.studies)

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
    tree: str  # analysis | cutflow | nhits | flat
    config: str
    name: str
    folder: Optional[str]  # None for flat families
    label: str  # study label (default for the main analysis and flat families)
    analysis: Optional[str]  # DayNight | HEP | Sensitivity; None for flat families
    kind: str  # filename kind, e.g. Counts, Exposure, SolarEnergy_DayNight_Cutflow, Vertex_Resolution
    energy: Optional[str] = None  # cutflow energy token
    subdir: Optional[str] = None  # flat-family subdir (FlatFamily.files key)

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
        """Paths (relative to input/data) this file is copied to: exactly one per file.

        Nothing is written flat into input/data any more. A bare ``--datafile``
        without ``--path`` still finds the reference (truncated/default) results,
        because ``lib.imports`` falls back to ``studies/truncated/default/``.
        """
        if self.tree == "analysis":
            if self.analysis_agnostic_basename:
                # Oscillogram / Signal1D_* / *_Templates are written by every
                # analysis with the same basename (and slightly different
                # contents): one sub-folder per analysis (--path studies/{folder}/{label}/{analysis}).
                return [f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{ANALYSIS_LOWER[self.analysis]}/{self.basename}"]
            return [f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{self.basename}"]
        if self.tree == "cutflow":
            # the label directory replaces the _fiduc_truth filename suffix
            return [f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{self.config}_{self.name}_{self.energy}_{self.analysis}_Cutflow.pkl"]
        if self.tree == "nhits":
            return [f"{STUDIES_DIRNAME}/{self.folder}/{self.label}/{self.basename}"]
        if self.tree == "flat":
            return [f"{self.subdir}/{self.basename}"]  # --path {subdir}
        return []


_CUTFLOW_RE = re.compile(r"^(?P<energy>[A-Za-z0-9]+)_(?P<analysis>DayNight|HEP|Sensitivity)_Cutflow(?P<suffix>(_[A-Za-z0-9_]+)?)\.pkl$")
_ANALYSIS_RE = re.compile(r"^(?P<analysis>DayNight|HEP|Sensitivity)_(?P<kind>[A-Za-z0-9_]+)\.pkl$")


def _strip_prefix(basename: str, config: str, name: str) -> Optional[str]:
    prefix = f"{config}_{name}_"
    return basename[len(prefix):] if basename.startswith(prefix) else None


FLAT_LAYOUT_REASON = "dead flat file outside the family layout (nested sub-folder)"


def _flat_subdir(relpath: str) -> tuple:
    """(family, subdir) owning ``relpath`` (longest subdir match), or (None, None)."""
    best = (None, None)
    for fam in FLAT_FAMILIES:
        for sd in (*fam.files, *fam.dead):
            if relpath.startswith(sd + "/") and (best[1] is None or len(sd) > len(best[1])):
                best = (fam, sd)
    return best


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
        if (analysis, config) in study.exclude:
            return None, f"retired: {label} is not run for {analysis}/{config}"
        rest = _strip_prefix(fn, config, name)
        if rest is None:
            # Per-sample exports (e.g. *_PDSPlanes.pkl) put every sample in the marley/ directory.
            for sample in COMPONENT_NAMES:
                rest = _strip_prefix(fn, config, sample)
                if rest is not None:
                    name = sample
                    break
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

    fam, subdir = _flat_subdir(relpath)
    if fam is not None:
        config, name, kind, status = fam.match(subdir, relpath[len(subdir) + 1:])
        if status is None:
            nested = relpath.count("/") > subdir.count("/") + 3
            return None, FLAT_LAYOUT_REASON if nested else f"unknown {fam.study} kind {subdir} {relpath.rsplit('/', 1)[-1]}"
        if status == "dead":
            return None, f"dead {fam.study} kind {subdir} {kind}"
        if config and config not in fam.configs:
            return None, f"{fam.study} config {config} not in the registry"
        return RemoteFile(relpath, fam.family, "flat", config, name, None, DEFAULT_LABEL, None, kind, subdir=subdir), ""

    return None, "outside the synced trees"


def passes_filters(rf: RemoteFile, flt: Filters) -> bool:
    if rf.tree == "flat":
        fam = FLAT_BY_FAMILY[rf.family]
        return flt.flat_ok(fam) and fam.selected(flt, rf.config, rf.name, rf.kind)
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
    """Every file of the registered families that should exist on the remote."""
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
                for config in study.analysis_configs(analysis):
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

    # Flat families: the complete selections (the others are sparse by design)
    for fam in FLAT_FAMILIES:
        if flt.flat_ok(fam):
            for subdir, config, name, kind, rel in fam.combos(flt, complete_only=True):
                out.append(RemoteFile(rel, fam.family, "flat", config, name, None, DEFAULT_LABEL, None, kind, subdir=subdir))

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

    # Flat families: one rule per selected file (configs are always explicit;
    # the remote flat trees also hold configs and samples nobody reads).
    for fam in FLAT_FAMILIES:
        if flt.flat_ok(fam):
            rules.extend("+ /" + rel for *_, rel in fam.combos(flt))
    if flt.flat_only():
        return rules

    for study in STUDIES:
        if not flt.study_group_ok(study):
            continue
        for folder in study.folders:
            if not flt.folder_ok(folder):
                continue
            for analysis in study.analyses:
                if not flt.analysis_ok(analysis) or not flt.name_ok(SIGNAL_NAME):
                    continue
                study_analysis_configs = study.analysis_configs(analysis)
                cfgs_filtered = [c for c in study_analysis_configs if flt.config_ok(c)]
                cfgs = (
                    [config_glob]
                    if (config_glob and len(cfgs_filtered) == len(study_analysis_configs) and len(study_analysis_configs) == len(CONFIGS))
                    else cfgs_filtered
                )
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
        who = rf.config if rf.name == SIGNAL_NAME and rf.tree in ("analysis", "flat") else f"{rf.config}/{rf.name}"
        where = rf.subdir if rf.tree == "flat" else f"{rf.folder}/{rf.label}"
        grouped[(rf.family, where, rf.analysis or "-", rf.kind)].append(who)
    return grouped


def _strip_flat_meta(payload):
    """Drop the per-config bookkeeping columns so only physics content is compared."""
    if hasattr(payload, "drop") and hasattr(payload, "columns"):
        return payload.drop(columns=list(FLAT_META_COLUMNS), errors="ignore")
    if isinstance(payload, dict):
        return {k: _strip_flat_meta(v) for k, v in payload.items() if k not in FLAT_META_COLUMNS}
    return payload


def _payload_equal(a, b) -> bool:
    if type(a) is not type(b):
        return False
    if hasattr(a, "equals"):  # DataFrame / Series (ndarray cells compare fine)
        return bool(a.equals(b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_payload_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_payload_equal(x, y) for x, y in zip(a, b))
    try:
        import numpy as np

        return bool(np.array_equal(a, b, equal_nan=True))
    except (TypeError, ValueError):
        return bool(a == b)


class _PlaceholderUnpickler(pickle.Unpickler):
    """Unpickler that stands in a string for globals missing here (e.g. fit
    functions pickled from SOLAR's __main__, such as double_gaussian)."""

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except (AttributeError, ImportError):
            return f"<missing {module}.{name}>"


def _load_flat_pickle(path: Path):
    import pandas as pd

    try:
        return pd.read_pickle(path)
    except (AttributeError, ImportError):
        with open(path, "rb") as fh:
            return _PlaceholderUnpickler(fh).load()


def flat_duplicate_report(mirror: Path, present: set) -> tuple:
    """Configs whose flat-family pkls are identical once Config/Version/Geometry are dropped.

    Returns (duplicates, unreadable): duplicates is a list of
    ((subdir, name, kind), [[config, ...], ...]) with one list per group of
    identical configs; unreadable lists relpaths that failed to unpickle.
    Guards against a sample being a copy of another config's ntuple (SOLAR's
    VD nominal marley once was a copy of VD shielded).
    """
    try:
        import pandas  # noqa: F401  (used by _load_flat_pickle)
    except ImportError:
        return [], []
    groups = defaultdict(dict)
    for rel in present:
        rf, _ = decode_remote_path(rel)
        if rf is not None and rf.tree == "flat":
            groups[(rf.subdir, rf.name, rf.kind)][rf.config] = rel
    duplicates, unreadable = [], []
    for key, by_config in sorted(groups.items()):
        if len(by_config) < 2:
            continue
        loaded = []  # (config, payload)
        for config in sorted(by_config):
            try:
                loaded.append((config, _strip_flat_meta(_load_flat_pickle(Path(mirror) / by_config[config]))))
            except Exception:
                unreadable.append(by_config[config])
        clusters = []  # [[config, ...], representative payload]
        for config, payload in loaded:
            for cluster in clusters:
                try:
                    same = _payload_equal(cluster[1], payload)
                except Exception:
                    same = False
                if same:
                    cluster[0].append(config)
                    break
            else:
                clusters.append([[config], payload])
        same_groups = [c[0] for c in clusters if len(c[0]) > 1]
        if same_groups:
            duplicates.append((key, same_groups))
    return duplicates, unreadable


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

    p_rk = sub.add_parser("kinds", help="Print live flat-family 'family subdir Kind' rows, or classify remote paths read from stdin")
    p_rk.add_argument("--family", action="append", default=None, help="Family name or --study selector (repeatable)")
    p_rk.add_argument("--dead", action="store_true", help="Print dead (legacy) kinds instead")
    p_rk.add_argument("--classify", action="store_true", help="Read remote relpaths on stdin; print '{live|dead|unknown|other} subdir kind' counts")

    p_src = sub.add_parser("sources", help="Print the remote trees (relative to output/data) that have include rules")
    add_filter_args(p_src)

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

    if args.command == "kinds":
        wanted = {w.lower() for w in (args.family or [])}
        fams = [f for f in FLAT_FAMILIES if not wanted or {f.family.lower(), f.study} & wanted]
        if args.classify:
            status = Counter()
            for line in sys.stdin:
                rel = line.strip()
                if not rel.endswith(".pkl"):
                    continue
                fam, subdir = _flat_subdir(rel)
                if fam is None or fam not in fams:
                    continue
                rf, reason = decode_remote_path(rel)
                if rf is not None:
                    status[("live", subdir, rf.kind)] += 1
                elif reason == FLAT_LAYOUT_REASON:
                    status[("dead", subdir, rel.split("/")[-2] + "/ (nested sub-folder)")] += 1
                elif reason.startswith(("dead ", "unknown ")):
                    status[(reason.split()[0], subdir, reason.rsplit(" ", 1)[1])] += 1
                else:
                    status[("other", subdir, reason)] += 1
            for (state, subdir, kind), n in sorted(status.items()):
                print(f"{state:8s} {n:4d}  {subdir} {kind}")
            return 0
        for fam in fams:
            for subdir, kinds in (fam.dead if args.dead else fam.files).items():
                for kind in kinds:
                    print(f"{fam.study} {subdir} {kind}")
        return 0

    flt = Filters.from_args(args)

    if args.command == "rules":
        print("\n".join(rsync_rules(flt)))
        return 0

    if args.command == "sources":
        rules = [r[3:] for r in rsync_rules(flt) if r.startswith("+ /")]
        trees = ["analysis", "solar/cutflow", "solar/nhits"] + [sd for f in FLAT_FAMILIES for sd in f.files]
        for tree in trees:
            if any(r.startswith(tree + "/") for r in rules):
                print(tree)
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

        print("==> Expected files per family")
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

        duplicates, unreadable = flat_duplicate_report(args.mirror, present)
        if duplicates:
            print("==> WARNING: reconstruction pkls with identical content across configs (Config/Version ignored)")
            for (subdir, name, kind), same_groups in duplicates:
                for configs in same_groups:
                    print(f"    {subdir:24s} {name:12s} {kind:40s} {' == '.join(configs)}")
            print("    A sample is probably a copy of another config's ntuple; check SOLAR before using these.")
        if unreadable:
            print(f"==> {len(unreadable)} reconstruction pkl(s) could not be unpickled for the duplicate check (skipped)")

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
