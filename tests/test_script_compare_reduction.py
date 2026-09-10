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
        ["script_compare_reduction.py", "--datafile", "mock", "-x", "X", "-y", "Y"],
    )

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_compare_reduction")
    module = importlib.reload(module)
    from scripts.script_compare_reduction import main

    return module, main


class _DummyAxis:
    def __init__(self):
        self.scatter_calls = []

    def scatter(self, x, y, **kwargs):
        self.scatter_calls.append(
            {"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float), **kwargs}
        )

    def boxplot(self, *args, **kwargs):
        pass

    def get_xticks(self):
        return np.array([0, 1, 2, 3])

    def set_xticks(self, *args, **kwargs):
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

    def semilogy(self, *args, **kwargs):
        pass

    def semilogx(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass


class _DummyFig:
    def suptitle(self, *args, **kwargs):
        pass


def test_main_reduces_points_into_binned_means(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        x="X",
        y="Y",
        iterable=None,
        operation="mean",
        threshold=False,
        boxplot=False,
        reduce=False,
        select=None,
        save_values=None,
        bins=4,
        percentile=(0, 100),
        labelx="X",
        labely="Y",
        labelz=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        multiply=None,
        subfolder=None,
        panels=None,
        panel_title=None,
        compact=False,
        plot_type=None,
        remove_value=None,
        default_operation=None,
        errory=False,
        errory_type="bars",
    )

    x_values = np.repeat(np.arange(4), 40)
    y_values = np.concatenate(
        [
            np.linspace(9.0, 15.0, 40),
            np.linspace(18.0, 26.0, 40),
            np.linspace(28.0, 36.0, 40),
            np.linspace(39.0, 47.0, 40),
        ]
    )

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "X": x_values.astype(int),
                "Y": y_values.astype(float),
            }
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
        lambda _args, _idx, prefix, suffix: "test_script_compare_reduction.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    main()

    output_file = plot_artifact_dir / "artifact-root" / "test_script_compare_reduction.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_main_wires_yerror_column_into_plot_data(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        x="X",
        y="Y",
        iterable=None,
        operation="mean",
        threshold=False,
        boxplot=False,
        reduce=False,
        select=None,
        save_values=None,
        bins=4,
        percentile=(0, 100),
        labelx="X",
        labely="Y",
        labelz=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        multiply=None,
        subfolder=None,
        panels=None,
        panel_title=None,
        compact=False,
        plot_type=None,
        remove_value=None,
        default_operation=None,
        errory=True,
        errory_type="bars",
    )

    x_values = np.repeat(np.arange(4), 40)
    y_values = np.concatenate(
        [
            np.linspace(9.0, 15.0, 40),
            np.linspace(18.0, 26.0, 40),
            np.linspace(28.0, 36.0, 40),
            np.linspace(39.0, 47.0, 40),
        ]
    )
    # Constant per-bin error so the reduced (mean) error is easy to predict.
    y_error_values = np.concatenate([np.full(40, val) for val in (1.0, 2.0, 3.0, 4.0)])

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "X": x_values.astype(int),
                "Y": y_values.astype(float),
                "YError": y_error_values.astype(float),
            }
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
        lambda _args, _idx, prefix, suffix: "test_script_compare_reduction_errory.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    calls = []
    original_plot_data = module.plot_data

    def recording_plot_data(*call_args, **call_kwargs):
        calls.append(
            {
                "y": call_kwargs.get("y"),
                "errory": call_kwargs.get("errory"),
                "plot_type": call_kwargs.get("plot_type"),
            }
        )
        return original_plot_data(*call_args, **call_kwargs)

    monkeypatch.setattr(module, "plot_data", recording_plot_data)

    main()

    assert len(calls) == 1
    assert calls[0]["plot_type"] == "errorbar"
    assert calls[0]["errory"] == [1.0, 2.0, 3.0, 4.0]
    assert calls[0]["y"] is not None

    output_file = plot_artifact_dir / "artifact-root" / "test_script_compare_reduction_errory.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0
