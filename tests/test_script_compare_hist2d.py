import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd


def _load_module_and_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script_compare_hist2d.py", "--datafile", "mock"])

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_compare_hist2d")
    module = importlib.reload(module)
    from scripts.script_compare_hist2d import main

    return module, main


class _DummyMappable:
    def __init__(self):
        self.array = np.array([0.0, 1.0, 2.0])
        self.clim = None

    def get_array(self):
        return self.array

    def set_array(self, array):
        self.array = array

    def set_clim(self, low, high):
        self.clim = (low, high)


class _DummyAxis:
    def __init__(self):
        self.hist2d_calls = []

    def hist2d(self, x, y, **kwargs):
        self.hist2d_calls.append(
            {"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float), **kwargs}
        )
        return (None, None, None, _DummyMappable())

    def plot(self, *args, **kwargs):
        pass

    def axhline(self, *args, **kwargs):
        pass

    def set_title(self, *args, **kwargs):
        pass

    def set_xlabel(self, *args, **kwargs):
        pass

    def set_ylabel(self, *args, **kwargs):
        pass

    def set_xlim(self, *args, **kwargs):
        pass

    def set_ylim(self, *args, **kwargs):
        pass


class _DummyColorbar:
    def __init__(self):
        self.label = None
        self.ax = SimpleNamespace(
            yaxis=SimpleNamespace(set_label_position=lambda *args, **kwargs: None)
        )

    def set_label(self, value):
        self.label = value


class _DummyFig:
    def __init__(self):
        self.colorbars = []

    def colorbar(self, _mappable, ax=None):
        cbar = _DummyColorbar()
        self.colorbars.append(cbar)
        return cbar

    def suptitle(self, *args, **kwargs):
        pass


def test_main_plots_2d_histogram_and_sets_colorbar_label(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        x="Time",
        y="ChargePerEnergy",
        percentile=[0, 100],
        iterable=None,
        select=None,
        save_values=None,
        bins=4,
        labelx=None,
        labely="Charge per Energy",
        rangex=None,
        rangey=None,
        logz=False,
        density=False,
        zoom=False,
        matchx=False,
        matchy=False,
        horizontal=None,
        vertical=None,
        diagonal=False,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
    )

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Time": np.array([0.0, 1.0, 2.0, 3.0]),
                "ChargePerEnergy": np.array([1.0, 1.5, 2.0, 2.5]),
            }
        ]
    )

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(module, "prepare_import", lambda _args: (_args.configs, _args.names))
    monkeypatch.setattr(module, "make_subtitle_from_args", lambda *a, **k: "sub")
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_compare_hist2d.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    main()

    output_file = plot_artifact_dir / "test_script_compare_hist2d.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0
