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
            "script_mean_table.py",
            "--datafile",
            "mock",
        ],
    )

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    src_dir = repo_root / "src"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(src_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_mean_table")
    module = importlib.reload(module)
    from scripts.script_mean_table import main

    return module, main


def test_main_generates_table_latex_output(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["hd_1x2x6"],
        names=["marley_official"],
        variables=["Energy", "Momentum"],
        iterable=None,
        select=None,
        save_values=None,
        x=None,
        rangex=None,
        y="Counts",
        output=str(plot_artifact_dir / "out"),
        debug=False,
        variable_title="Test Variable",
        variable_name="Variable",
        emph=None,
        it=None,
    )

    # Create sample data for a mean table
    df = pd.DataFrame({
        "Geometry": ["HD", "HD"],
        "Config": ["hd_1x2x6", "hd_1x2x6"],
        "Name": ["marley_official", "marley_official"],
        "Variable": ["Energy", "Momentum"],
        "Counts": [100.5, 200.3],
    })

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, prefix=None, suffix=None: f"test_script_mean_table.{suffix.split('.')[-1]}" if suffix else "test_script_mean_table",
    )

    main()
    
    # The test passes if main() completes without error
    # HTML and LaTeX files are generated internally
