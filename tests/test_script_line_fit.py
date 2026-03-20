import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd


def _load_module_and_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script_line_fit.py", "--datafile", "mock"])

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_line_fit")
    module = importlib.reload(module)
    from scripts.script_line_fit import main

    return module, main


class _DummyAxis:
    def __init__(self):
        self.plot_calls = []
        self.transAxes = object()

    def plot(self, x, y, **kwargs):
        self.plot_calls.append(
            {"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float), **kwargs}
        )

    def errorbar(self, x, y, **kwargs):
        self.plot(x, y, **kwargs)

    def text(self, *args, **kwargs):
        pass

    def set_ylabel(self, *args, **kwargs):
        pass

    def set_xlim(self, *args, **kwargs):
        pass

    def set_ylim(self, *args, **kwargs):
        pass

    def set_yscale(self, *args, **kwargs):
        pass

    def set_xscale(self, *args, **kwargs):
        pass

    def set_title(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass

    def axhline(self, *args, **kwargs):
        pass

    def set_xlabel(self, *args, **kwargs):
        pass


class _DummyGridSpec:
    def __init__(self, axes):
        self.axes = axes

    def subplots(self, sharex=True):
        return self.axes


class _DummyFig:
    def __init__(self, axes):
        self.axes = axes

    def add_gridspec(self, **kwargs):
        return _DummyGridSpec(self.axes)

    def suptitle(self, *args, **kwargs):
        pass


def test_main_plots_fit_and_zero_residuals_for_matching_data(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        x="Values",
        y="Density",
        iterable=None,
        select=None,
        save_values=None,
        reduce=False,
        labelx="Energy",
        labely="Density",
        labelz=None,
        logx=False,
        logy=False,
        chi2=False,
        fitindex=0,
        fitlegendposition=(0.55, 0.90),
        errorx=False,
        errory=False,
        rangex=None,
        rangey=None,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
    )

    linear = lambda x, slope, intercept: slope * x + intercept
    x = np.array([1.0, 2.0, 3.0])
    y = linear(x, 2.0, 1.0)

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Values": x,
                "Density": y,
                "Params": np.array([2.0, 1.0]),
                "ParamsFormat": [".2f", ".2f"],
                "ParamsLabels": ["m", "b"],
                "ParamsError": np.array([0.1, 0.1]),
                "FitFunction": linear,
                "FitFunctionLabel": "Linear",
            }
        ]
    )

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(module, "prepare_import", lambda _args: (_args.configs, _args.names))
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_line_fit.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    main()

    output_file = plot_artifact_dir / "test_script_line_fit.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0
