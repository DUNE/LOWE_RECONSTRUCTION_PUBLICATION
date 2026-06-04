import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest


def _load_module_and_main(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "script_iterable_scan.py",
            "--datafile",
            "mock",
            "--iterable",
            "Label",
            "-x",
            "Values",
            "-y",
            "Counts",
        ],
    )

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    src_dir = repo_root / "src"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(src_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_iterable_scan")
    module = importlib.reload(module)
    from scripts.script_iterable_scan import main

    return module, main


class _DummyAxis:
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

    def set_xscale(self, *args, **kwargs):
        pass

    def set_yscale(self, *args, **kwargs):
        pass

    def plot(self, *args, **kwargs):
        pass

    def scatter(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass


class _DummyFig:
    def suptitle(self, *args, **kwargs):
        pass


def test_main_plots_iterable_scan(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["hd_cfg_a"],
        names=["name_a"],
        variables=None,
        iterable="Label",
        select=None,
        save_values=None,
        x="Values",
        y="Counts",
        reduce=False,
        labelx="X Axis",
        labely="Y Axis",
        labelz=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        plot_style="-",
        plot_type="plot",
        title=None,
        output=str(plot_artifact_dir / "out"),
        horizontal=None,
        horizontal_label=None,
        vertical=None,
        vertical_label=None,
        point=None,
        point_label=None,
        errorx=False,
        stacked=False,
        connect=False,
        debug=False,
    )

    # Create sample data
    x_vals = np.linspace(0, 10, 50)
    y_vals = np.sin(x_vals)
    
    df = pd.DataFrame({
        "Config": ["hd_cfg_a"] * 50,
        "Name": ["name_a"] * 50,
        "Label": ["iter_1"] * 50,
        "Values": x_vals,
        "Counts": y_vals,
    })

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(module, "prepare_import", lambda _args: (_args.configs, _args.names))
    monkeypatch.setattr(module, "make_subtitle_from_args", lambda _args, _idx: "sub")
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, idx=None, prefix=None, suffix=None: "test_script_iterable_scan.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)
    monkeypatch.setattr(module, "save_figure_to_paths", lambda *args, **kwargs: None)

    main()
    # Test passes if main() completes without error


def test_main_plots_comparable_iterable_scan(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["hd_cfg_a"],
        names=["name_a"],
        variables=None,
        iterable="Label",
        comparable="Group",
        comparable_linestyles=["solid", "dashed"],
        select=None,
        save_values=None,
        x="Values",
        y="Counts",
        reduce=False,
        labelx="X Axis",
        labely="Y Axis",
        labelz=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        plot_style="-",
        plot_type="line",
        title=None,
        output=str(plot_artifact_dir / "out"),
        horizontal=None,
        horizontal_label=None,
        vertical=None,
        vertical_label=None,
        point=None,
        point_label=None,
        errorx=False,
        stacked=False,
        connect=False,
        debug=False,
    )

    x_vals = np.linspace(0, 10, 20)
    df = pd.DataFrame(
        {
            "Config": ["hd_cfg_a"] * 40,
            "Name": ["name_a"] * 40,
            "Label": ["iter_1"] * 40,
            "Group": ["g1"] * 20 + ["g2"] * 20,
            "Values": np.concatenate([x_vals, x_vals]),
            "Counts": np.concatenate([np.sin(x_vals), np.cos(x_vals)]),
        }
    )

    captured_linestyles = []

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(module, "prepare_import", lambda _args: (_args.configs, _args.names))
    monkeypatch.setattr(module, "make_subtitle_from_args", lambda _args, _idx: "sub")
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, idx=None, prefix=None, suffix=None: "test_script_iterable_scan.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)
    monkeypatch.setattr(module, "save_figure_to_paths", lambda *args, **kwargs: None)

    original_plot_data = module.plot_data

    def _capture_plot_data(*plot_args, **plot_kwargs):
        captured_linestyles.append(plot_kwargs.get("linestyle"))
        return original_plot_data(*plot_args, **plot_kwargs)

    monkeypatch.setattr(module, "plot_data", _capture_plot_data)

    main()

    assert captured_linestyles == ["solid", "dashed"]
