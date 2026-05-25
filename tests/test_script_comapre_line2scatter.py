import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _load_module(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_comapre_line2scatter")
    return importlib.reload(module)


def test_main_renders_waveform_and_lower_panel(monkeypatch, plot_artifact_dir):
    module = _load_module(monkeypatch)

    output_file = plot_artifact_dir / "waveform_panel.png"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "script_comapre_line2scatter.py",
            "--datafile",
            "mock.pkl",
            "--iterable",
            "DisplayMode",
            "--iterable-value",
            "ophits",
            "--select",
            "Selection",
            "--save_values",
            "keep",
            "--output",
            str(output_file),
            "--title",
            "Waveform Panel",
        ],
    )

    df = pd.DataFrame(
        [
            {
                "DisplayMode": "ophits",
                "Selection": "keep",
                "TimeNS": np.array([0.0, 1.0, 2.0, 3.0]),
                "UpperY": np.array([0.2, 0.4, 0.3, 0.1]),
                "TruePhotonTimeNS": np.array([0.5, 1.5, 2.5]),
                "TruePhotonCount": np.array([1.0, 2.0, 1.0]),
                "OphitPeakNS": np.array([0.75, 2.25]),
                "OphitAreaPE": np.array([3.0, 1.5]),
                "OphitStartNS": np.array([0.25, 1.75]),
                "OphitEndNS": np.array([1.25, 2.75]),
            }
        ]
    )

    monkeypatch.setattr(module, "load_df", lambda _path: df)

    module.main()

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_parse_args_allows_default_output_structure(monkeypatch):
    module = _load_module(monkeypatch)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "script_comapre_line2scatter.py",
            "--datafile",
            "mock.pkl",
        ],
    )

    args = module.parse_args()
    assert args.output is None


def test_parse_args_accepts_underscore_lower_flags(monkeypatch):
    module = _load_module(monkeypatch)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "script_comapre_line2scatter.py",
            "--datafile",
            "mock.pkl",
            "--lower_series",
            "Photon",
            "--lower_plot_style",
            "hist",
            "--lower_show_range_bars",
            "--lower_vertical_lines",
            "--lower_labely",
            "Photon Density (PE / ns)",
            "--lower_series_density",
        ],
    )

    args = module.parse_args()
    assert args.lower_series == "Photon"
    assert args.lower_plot_style == "hist"
    assert args.lower_show_range_bars is True
    assert args.lower_vertical_lines is True
    assert args.lower_labely == "Photon Density (PE / ns)"
    assert args.lower_series_density is True


def test_main_supports_lower_hist_and_range_bars(monkeypatch, plot_artifact_dir):
    module = _load_module(monkeypatch)

    output_file = plot_artifact_dir / "waveform_panel_hist_ranges.png"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "script_comapre_line2scatter.py",
            "--datafile",
            "mock.pkl",
            "--iterable",
            "DisplayMode",
            "--iterable-value",
            "deconvolved",
            "--lower-series",
            "OpHit",
            "--lower-plot-style",
            "scatter",
            "--lower-series-range",
            "--lower-vertical-lines",
            "--output",
            str(output_file),
            "--title",
            "Line + Hist/Range",
        ],
    )

    df = pd.DataFrame(
        [
            {
                "DisplayMode": "deconvolved",
                "TimeNS": np.array([0.0, 1.0, 2.0, 3.0]),
                "UpperY": np.array([0.1, 0.3, 0.25, 0.2]),
                "TruePhotonTimeNS": np.array([0.4, 1.2, 2.6]),
                "TruePhotonCount": np.array([1.0, 1.0, 2.0]),
                "OphitPeakNS": np.array([0.75, 2.25]),
                "OphitAreaPE": np.array([3.0, 1.5]),
                "OphitStartNS": np.array([0.25, 1.75]),
                "OphitEndNS": np.array([1.25, 2.75]),
            }
        ]
    )

    monkeypatch.setattr(module, "load_df", lambda _path: df)

    module.main()

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_main_without_iterable_column(monkeypatch, plot_artifact_dir):
    module = _load_module(monkeypatch)

    output_file = plot_artifact_dir / "waveform_no_iterable.png"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "script_comapre_line2scatter.py",
            "--datafile",
            "mock.pkl",
            "--output",
            str(output_file),
            "--title",
            "No Iterable",
        ],
    )

    df = pd.DataFrame(
        [
            {
                "TimeNS": np.array([0.0, 1.0, 2.0, 3.0]),
                "UpperY": np.array([0.1, 0.2, 0.3, 0.4]),
                "PhotonTime": np.array([0.2, 1.3, 2.5]),
                "PhotonCount": np.array([1.0, 2.0, 1.0]),
            }
        ]
    )

    monkeypatch.setattr(module, "load_df", lambda _path: df)

    module.main()

    assert output_file.exists()
    assert output_file.stat().st_size > 0