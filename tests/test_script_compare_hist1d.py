import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd


def _load_module_and_main(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["script_compare_hist1d.py", "--datafile", "mock", "-x", "Values"],
    )

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_compare_hist1d")
    module = importlib.reload(module)
    from scripts.script_compare_hist1d import main

    return module, main


class _DummyAxis:
    def __init__(self):
        self.plot_calls = []

    def plot(self, x, y, **kwargs):
        self.plot_calls.append(
            {"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float), **kwargs}
        )

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

    def semilogy(self, *args, **kwargs):
        pass

    def semilogx(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass


class _DummyFig:
    def suptitle(self, *args, **kwargs):
        pass


def test_main_plots_histogram_for_each_iterable(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        x=["Values"],
        operation="subtract",
        iterable="Category",
        weight=None,
        reduce=False,
        select=None,
        save_values=None,
        bins=2,
        percentile=None,
        labelx="X",
        labely="Counts",
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
    )

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "first",
                "Values": np.array([0.0, 0.2, 0.8, 1.0]),
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "second",
                "Values": np.array([0.1, 0.4, 0.6, 0.9]),
            },
        ]
    )

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(module, "prepare_import", lambda _args: (_args.configs, _args.names))
    monkeypatch.setattr(module, "make_subtitle_from_args", lambda _args, _idx: "sub")
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_compare_hist1d.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    main()

    output_file = plot_artifact_dir / "test_script_compare_hist1d.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0
