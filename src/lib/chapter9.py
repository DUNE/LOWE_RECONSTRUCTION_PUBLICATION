"""Data layer for the thesis chapter 9 figures.

Everything the chapter 9 scripts (``scripts/ch9_*.py``) share lives here:

* the SOLAR status table (``study_status_<tag>.md`` / ``.csv`` from SOLAR
  ``output/logs/``) and its row tags,
* loading of the per-study ``Exposure`` / ``Contours`` / ``10Y_Contours`` pkls
  from the tree written by ``scripts/sync_solar_data.sh``,
* the cross-check of every plotted number against the status table,
* the "preliminary" bookkeeping that drives the watermark.

The values quoted in the status table are reproduced with the same recipe as
SOLAR's ``src/tools/study_status.py`` (Smoothed Exposure curve interpolated at
the quoted exposure; Delta chi2 of the contour grid at the alternate
oscillation point), so a plotted number either equals the table entry at the
table's printed precision or a :class:`StatusTableMismatch` is raised.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Static description of the chapter 9 analysis
# ---------------------------------------------------------------------------

CONFIGS = (
    "hd_1x2x6_centralAPA",
    "hd_1x2x6_lateralAPA",
    "vd_1x8x14_3view_30deg_nominal",
    "vd_1x8x14_3view_30deg_shielded",
)
VD_CONFIGS = tuple(c for c in CONFIGS if c.startswith("vd_"))
MAIN_CONFIG = "hd_1x2x6_centralAPA"
SIGNAL = "marley"

ANALYSES = ("DayNight", "HEP", "Sensitivity")
# Exposure at which the chapter quotes its numbers. The analyses run to 30 yr.
QUOTED_EXPOSURE = {"DayNight": 20.0, "HEP": 20.0, "Sensitivity": 10.0}
MAX_EXPOSURE = 30.0
ANALYSIS_TITLE = {"DayNight": "Day-Night", "HEP": "$hep$", "Sensitivity": "Sensitivity"}

CONFIG_TITLE = {
    "hd_1x2x6_centralAPA": "HD Central",
    "hd_1x2x6_lateralAPA": "HD Lateral",
    "vd_1x8x14_3view_30deg_nominal": "VD Top",
    "vd_1x8x14_3view_30deg_shielded": "VD Bottom Shielded",
}

FOLDERS = ("Truncated", "Nominal", "Reduced")
FOLDER_DIR = {f: f.lower() for f in FOLDERS}

# Oscillation reference values (SOLAR config/analysis/physics.json).
SIN12 = 0.304
SOLAR_DM2 = 6e-5
REACT_DM2 = 7.54e-5

# Status tags that make a row preliminary (brief: epoch / behind_default). ``values_bug`` marks a row whose
# stored numbers SOLAR itself flags as wrong, so it is stamped as well.
PRELIMINARY_TAGS = ("epoch", "behind_default", "values_bug")

# Rows that are preliminary whatever the status table says. Each entry maps
# (analysis, study) -> reason. The Sensitivity charge-threshold rows do not
# follow the Day-Night/HEP trend and are to be shown "as they are" but marked.
FORCED_PRELIMINARY: Dict[Tuple[str, str], str] = {
    ("Sensitivity", "charge_Q50"): "Sensitivity charge-threshold trend not understood",
    ("Sensitivity", "charge_Q100"): "Sensitivity charge-threshold trend not understood",
    ("Sensitivity", "charge_Q500"): "Sensitivity charge-threshold trend not understood",
    ("*", "fiduc_truth"): "fiduc_truth still in development",
}


class Chapter9Error(RuntimeError):
    """Base class for data problems that must stop a figure from being made."""


class StatusTableMismatch(Chapter9Error):
    """A number derived from the pkls disagrees with the SOLAR status table."""


class MissingData(Chapter9Error):
    """A requested (config, folder, analysis, study) has no usable input."""


# ---------------------------------------------------------------------------
# Status table
# ---------------------------------------------------------------------------

_SIGMA_RE = re.compile(r"^\s*([0-9.]+)σ@(\d+)y\s*$")
_CHI2_RE = re.compile(r"^\s*Δχ²\s*([0-9.]+)/([0-9.]+)@(\d+)y\s*$")
_TAG_RE = re.compile(r"cut!=ref\([^)]*\)|[A-Za-z_]+(?:!=[A-Za-z_]+)?")


def _parse_cut(text: str) -> Optional[Tuple[int, int, int]]:
    text = str(text).strip()
    if not text or text == "-":
        return None
    parts = text.split("/")
    if len(parts) != 3:
        return None
    return tuple(int(p) for p in parts)  # type: ignore[return-value]


def _parse_quantity(text: str) -> Tuple[Tuple[float, ...], Optional[float]]:
    """``"4.47σ@20y"`` -> ((4.47,), 20.0); ``"Δχ² 2.13/2.08@10y"`` -> ((2.13, 2.08), 10.0)."""
    m = _SIGMA_RE.match(text)
    if m:
        return (float(m.group(1)),), float(m.group(2))
    m = _CHI2_RE.match(text)
    if m:
        return (float(m.group(1)), float(m.group(2))), float(m.group(3))
    return (), None


@dataclass(frozen=True)
class StatusRow:
    config: str
    folder: str
    analysis: str
    study: str
    cut: Optional[Tuple[int, int, int]]
    fiducial: str
    value_text: str
    at_eval_text: str
    record: str
    status: str
    trend: str

    @property
    def tags(self) -> Tuple[str, ...]:
        return tuple(t for t in _TAG_RE.findall(self.status) if t and t != "ok")

    @property
    def value(self) -> Tuple[float, ...]:
        return _parse_quantity(self.value_text)[0]

    @property
    def value_exposure(self) -> Optional[float]:
        return _parse_quantity(self.value_text)[1]

    @property
    def at_eval(self) -> Tuple[float, ...]:
        return _parse_quantity(self.at_eval_text)[0]

    @property
    def eval_exposure(self) -> Optional[float]:
        return _parse_quantity(self.at_eval_text)[1]

    @property
    def status_preliminary(self) -> bool:
        return any(t in PRELIMINARY_TAGS for t in self.tags)

    @property
    def forced_reason(self) -> Optional[str]:
        return FORCED_PRELIMINARY.get((self.analysis, self.study)) or FORCED_PRELIMINARY.get(("*", self.study))

    @property
    def preliminary(self) -> bool:
        return self.status_preliminary or self.forced_reason is not None

    def preliminary_reasons(self) -> List[str]:
        reasons = [t for t in self.tags if t in PRELIMINARY_TAGS]
        if self.forced_reason:
            reasons.append(self.forced_reason)
        return reasons

    @property
    def key(self) -> Tuple[str, str, str, str]:
        return (self.config, self.folder, self.analysis, self.study)


@dataclass
class StatusTable:
    path: Path
    rows: List[StatusRow]
    header: str = ""
    _index: Dict[Tuple[str, str, str, str], StatusRow] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._index = {r.key: r for r in self.rows}

    def get(self, config: str, folder: str, analysis: str, study: str) -> StatusRow:
        try:
            return self._index[(config, folder, analysis, study)]
        except KeyError:
            raise MissingData(
                f"No status-table row for config={config} folder={folder} analysis={analysis} "
                f"study={study} in {self.path}"
            ) from None

    def has(self, config: str, folder: str, analysis: str, study: str) -> bool:
        return (config, folder, analysis, study) in self._index


def _row_from_cells(config: str, cells: Sequence[str]) -> StatusRow:
    folder, analysis, study, cut, fiducial, value, at_eval, record, status, trend = (c.strip() for c in cells[:10])
    return StatusRow(config, folder, analysis, study, _parse_cut(cut), fiducial, value, at_eval, record, status, trend)


def read_status_table(path: str | Path) -> StatusTable:
    """Read a SOLAR ``study_status_*.md`` (or its ``.csv`` twin)."""
    path = Path(path)
    if not path.is_file():
        raise MissingData(f"Status table not found: {path}")
    rows: List[StatusRow] = []
    if path.suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        for _, r in df.iterrows():
            rows.append(
                _row_from_cells(
                    r["config"],
                    [r["folder"], r["analysis"], r["study"], r["cut"], r["fiducial"], r["value"], r["at_eval"], r["record"], r["status"], r["trend"]],
                )
            )
        return StatusTable(path, rows)

    header_lines: List[str] = []
    config = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            config = line[3:].strip()
            continue
        if config is None:
            header_lines.append(line)
            continue
        if not line.startswith("|"):
            continue
        cells = [c for c in line.strip().strip("|").split("|")]
        if len(cells) < 10 or cells[0].strip() in ("folder", "---") or set(cells[0].strip()) <= {"-"}:
            continue
        rows.append(_row_from_cells(config, cells))
    if not rows:
        raise MissingData(f"No table rows parsed from {path}")
    return StatusTable(path, rows, "\n".join(header_lines))


# ---------------------------------------------------------------------------
# Loading series from the synced pkls
# ---------------------------------------------------------------------------


def result_path(data_dir: str | Path, config: str, folder: str, study: str, analysis: str, kind: str) -> Path:
    """``{data_dir}/{folder}/{study}/{config}_marley_{analysis}_{kind}.pkl`` (studies tree of the sync)."""
    return Path(data_dir) / FOLDER_DIR[folder] / study / f"{config}_{SIGNAL}_{analysis}_{kind}.pkl"


@dataclass
class Series:
    """One curve (Day-Night, HEP) or one pair of points (Sensitivity)."""

    config: str
    folder: str
    analysis: str
    study: str
    x: np.ndarray
    y: np.ndarray
    cut: Optional[Tuple[int, int, int]]
    row: StatusRow
    sources: List[Path]
    variable: str = ""
    y_alt: Optional[np.ndarray] = None  # Sensitivity: reactor-fit-at-solar Delta chi2
    at_quoted: float = float("nan")
    at_quoted_alt: float = float("nan")
    at_max: float = float("nan")  # value at 30 yr

    @property
    def is_curve(self) -> bool:
        return self.analysis in ("DayNight", "HEP")

    @property
    def quoted_exposure(self) -> float:
        return QUOTED_EXPOSURE[self.analysis]

    @property
    def preliminary(self) -> bool:
        return self.row.preliminary

    def value_at(self, exposure: float) -> float:
        """Value of the (first) quantity at ``exposure`` (curve: log-linear-safe np.interp as in SOLAR)."""
        if self.is_curve:
            return float(np.interp(exposure, self.x, self.y))
        idx = np.where(np.isclose(self.x, exposure))[0]
        if idx.size == 0:
            raise MissingData(f"{self.describe()} has no value at {exposure:g} yr (only {self.x.tolist()})")
        return float(self.y[idx[0]])

    def describe(self) -> str:
        return f"{self.config}/{self.folder}/{self.analysis}/{self.study}"


class Checker:
    """Collects (or raises on) disagreements with the status table."""

    def __init__(self, mode: str = "raise"):
        if mode not in ("raise", "warn"):
            raise ValueError("mode must be 'raise' or 'warn'")
        self.mode = mode
        self.mismatches: List[str] = []
        self.checked = 0

    def fail(self, message: str) -> None:
        self.mismatches.append(message)
        if self.mode == "raise":
            raise StatusTableMismatch(message)

    def expect(self, condition: bool, message: str) -> None:
        self.checked += 1
        if not condition:
            self.fail(message)

    def finalize(self) -> None:
        if self.mismatches and self.mode == "raise":
            raise StatusTableMismatch("; ".join(self.mismatches))


def _fmt2(x: float) -> str:
    return f"{x:.2f}"


#: the reported test statistic per analysis (matches solar_scripts.txt / study_scripts.txt: DayNight
#: uses "-s Asimov Smoothed", HEP uses "-s ProfileLikelihood Smoothed"). A Gaussian row also exists in
#: both files (a per-bin S/sqrt(B) quadrature sum, not profile-likelihood-treated) and reads
#: structurally higher for HEP; picking "whichever Smoothed row has the largest 30 yr value" silently
#: substitutes it. Select the Variable explicitly instead.
REPORTED_VARIABLE = {"DayNight": "Asimov", "HEP": "ProfileLikelihood"}


def _load_exposure_curve(path: Path, analysis: str, cut: Optional[Tuple[int, int, int]]):
    """Recipe of study_status.read_exposure: the analysis's reported Variable, Smoothed (HEP: NoRebin), at cut."""
    if not path.is_file():
        raise MissingData(f"Missing input: {path}")
    df = pd.read_pickle(path)
    sel = df[(df["SpectrumType"] == "Smoothed") & (df["Variable"] == REPORTED_VARIABLE[analysis])]
    if analysis == "HEP" and "Mode" in sel.columns:
        sel = sel[sel["Mode"] == "NoRebin"]
    if cut is not None:
        sel = sel[(sel["NHits"] == cut[0]) & (sel["OpHits"] == cut[1]) & (sel["AdjCl"] == cut[2])]
    best = None
    for _, r in sel.iterrows():
        e = np.atleast_1d(np.asarray(r["Exposure"], float))
        s = np.atleast_1d(np.asarray(r["Significance"], float))
        if e.size != s.size or e.size < 2:
            continue
        s30 = float(np.interp(MAX_EXPOSURE, e, s))
        if best is None:
            best = (s30, e, s, str(r.get("Variable", "")), (int(r["NHits"]), int(r["OpHits"]), int(r["AdjCl"])))
    if best is None:
        have = df[["Variable", "SpectrumType", "NHits", "OpHits", "AdjCl"]].drop_duplicates().values.tolist()
        raise MissingData(
            f"{path}: no {REPORTED_VARIABLE[analysis]} Smoothed row at cut {cut}; rows present: {have}"
        )
    return best


def _contour_alt_values(path: Path):
    """Delta chi2 at the alternate oscillation point (solar row, reactor row) as in study_status.read_contours."""
    if not path.is_file():
        raise MissingData(f"Missing input: {path}")
    df = pd.read_pickle(path)
    out = {"solar": np.nan, "react": np.nan, "cut": None, "fit": None, "profile": None}
    for _, r in df.iterrows():
        if r.get("Variable") != "sin12":
            continue
        sig = np.asarray(r["Significance"], float)
        dm2 = np.asarray(r["Dm2"], float)
        vals = np.asarray(r["Values"], float)
        other = REACT_DM2 if r["Label"] == "solar" else SOLAR_DM2
        out[r["Label"]] = float(sig[int(np.argmin(np.abs(dm2 - other))), int(np.argmin(np.abs(vals - SIN12)))])
        out["cut"] = (int(r["NHits"]), int(r["OpHits"]), int(r["AdjCl"]))
        out["fit"] = r.get("FitMethod")
        out["profile"] = r.get("NuisanceProfile")
    return out


def load_series(
    data_dir: str | Path,
    table: StatusTable,
    config: str,
    folder: str,
    analysis: str,
    study: str,
    checker: Optional[Checker] = None,
) -> Series:
    """Load one series and cross-check it against the status table row."""
    checker = checker or Checker("raise")
    row = table.get(config, folder, analysis, study)
    tag = f"{config}/{folder}/{analysis}/{study}"

    if analysis in ("DayNight", "HEP"):
        path = result_path(data_dir, config, folder, study, analysis, "Exposure")
        s30, e, s, variable, cut = _load_exposure_curve(path, analysis, row.cut)
        order = np.argsort(e)
        series = Series(
            config, folder, analysis, study, e[order], s[order], cut, row, [path], variable=variable,
            at_quoted=float(np.interp(QUOTED_EXPOSURE[analysis], e[order], s[order])), at_max=s30,
        )
        # --- cross-check against the status table --------------------------------
        checker.expect(
            row.eval_exposure == QUOTED_EXPOSURE[analysis],
            f"{tag}: status table quotes {row.eval_exposure} yr, expected {QUOTED_EXPOSURE[analysis]:g} yr",
        )
        checker.expect(
            bool(row.at_eval) and _fmt2(series.at_quoted) == _fmt2(row.at_eval[0]),
            f"{tag}: significance at {QUOTED_EXPOSURE[analysis]:g} yr is {_fmt2(series.at_quoted)}σ from {path.name}, status table says {row.at_eval_text}",
        )
        checker.expect(cut == row.cut, f"{tag}: cut {cut} in {path.name}, status table says {row.cut}")
        # 30 yr value: the table's 'Values' comes from SOLAR's highest_* map (not synced); it must
        # agree with the exposure curve to SOLAR's own values_bug tolerance.
        if row.value:
            tol = max(0.1, 0.05 * abs(s30))
            checker.expect(
                abs(s30 - row.value[0]) <= tol,
                f"{tag}: 30 yr significance {s30:.3f}σ from {path.name} vs status table {row.value_text} (values_bug?)",
            )
        return series

    # Sensitivity: Delta chi2 at 30 yr (Contours) and 10 yr (10Y_Contours)
    p30 = result_path(data_dir, config, folder, study, analysis, "Contours")
    p10 = result_path(data_dir, config, folder, study, analysis, "10Y_Contours")
    c30, c10 = _contour_alt_values(p30), _contour_alt_values(p10)
    series = Series(
        config, folder, analysis, study,
        np.array([10.0, 30.0]), np.array([c10["solar"], c30["solar"]]),
        c30["cut"], row, [p10, p30], variable=f"{c30['fit']}/{c30['profile']}",
        y_alt=np.array([c10["react"], c30["react"]]),
        at_quoted=c10["solar"], at_quoted_alt=c10["react"], at_max=c30["solar"],
    )
    checker.expect(
        row.eval_exposure == QUOTED_EXPOSURE[analysis],
        f"{tag}: status table quotes {row.eval_exposure} yr, expected {QUOTED_EXPOSURE[analysis]:g} yr",
    )
    checker.expect(
        len(row.at_eval) == 2 and (_fmt2(c10["solar"]), _fmt2(c10["react"])) == tuple(_fmt2(v) for v in row.at_eval),
        f"{tag}: Δχ² at 10 yr is {_fmt2(c10['solar'])}/{_fmt2(c10['react'])} from {p10.name}, status table says {row.at_eval_text}",
    )
    checker.expect(
        len(row.value) == 2 and (_fmt2(c30["solar"]), _fmt2(c30["react"])) == tuple(_fmt2(v) for v in row.value),
        f"{tag}: Δχ² at 30 yr is {_fmt2(c30['solar'])}/{_fmt2(c30['react'])} from {p30.name}, status table says {row.value_text}",
    )
    checker.expect(c30["cut"] == row.cut, f"{tag}: cut {c30['cut']} in {p30.name}, status table says {row.cut}")
    checker.expect(c10["cut"] == c30["cut"], f"{tag}: 10 yr cut {c10['cut']} differs from 30 yr cut {c30['cut']}")
    return series


def try_load_series(*args, **kwargs) -> Optional[Series]:
    """``load_series`` that returns ``None`` when the input simply does not exist."""
    try:
        return load_series(*args, **kwargs)
    except MissingData:
        return None


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------


def cut_text(cut: Optional[Tuple[int, int, int]]) -> str:
    return "/".join(str(c) for c in cut) if cut else "-"


def series_label(
    base: str,
    series: Series,
    reference: Optional[Series] = None,
    always_cuts: bool = False,
    mark_preliminary: bool = True,
) -> str:
    """Legend text: base name, cuts when they differ from the reference (or always), preliminary dagger."""
    text = base
    show_cuts = always_cuts or (reference is not None and series.cut != reference.cut)
    if show_cuts and series.cut:
        text += f" (cuts {cut_text(series.cut)})"
    if mark_preliminary and series.preliminary:
        text += " †"
    return text


# ---------------------------------------------------------------------------
# Day-Night reconstructed-energy spectra (companion figure of section 9.1.3)
# ---------------------------------------------------------------------------


@dataclass
class DayNightSpectrum:
    """Smoothed 'Solar' spectrum and its Night-minus-Day excess for one study."""

    config: str
    folder: str
    study: str
    energy: np.ndarray
    solar: np.ndarray
    excess: np.ndarray
    energy_label: str
    counts_unit: str
    excess_label: str
    cut: Optional[Tuple[int, int, int]]
    row: StatusRow
    source: Path

    @property
    def preliminary(self) -> bool:
        return self.row.preliminary


def load_daynight_spectrum(
    data_dir: str | Path,
    table: StatusTable,
    config: str,
    folder: str,
    study: str,
    checker: Optional[Checker] = None,
) -> DayNightSpectrum:
    """Smoothed Solar spectrum (events / MeV / 20 yr) and Night-Day excess from ``DayNight_Counts``."""
    checker = checker or Checker("raise")
    row = table.get(config, folder, "DayNight", study)
    path = result_path(data_dir, config, folder, study, "DayNight", "Counts")
    if not path.is_file():
        raise MissingData(f"Missing input: {path}")
    df = pd.read_pickle(path)
    sel = df[(df["Component"] == "Solar") & (df["SpectrumType"] == "Smoothed")]
    if len(sel) != 1:
        raise MissingData(f"{path}: expected one Solar/Smoothed row, found {len(sel)}")
    r = sel.iloc[0]
    cut = (int(r["NHits"]), int(r["OpHits"]), int(r["AdjCl"]))
    tag = f"{config}/{folder}/DayNight/{study}"
    checker.expect(cut == row.cut, f"{tag}: cut {cut} in {path.name}, status table says {row.cut}")
    checker.expect(float(r["Exposure"]) == QUOTED_EXPOSURE["DayNight"],
                   f"{tag}: Counts exposure {r['Exposure']} yr, expected {QUOTED_EXPOSURE['DayNight']:g} yr")
    return DayNightSpectrum(
        config, folder, study,
        np.asarray(r["Energy"], float), np.asarray(r["Counts"], float), np.asarray(r["Metric"], float),
        str(r["EnergyLabel"]), str(r["CountsUnit"]), str(r["MetricLabel"]), cut, row, path,
    )
