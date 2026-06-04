import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import mock_open

import pandas as pd

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

import lib.imports as imports_module


def test_import_data_wraps_scalar_dict_payload(monkeypatch):
    args = SimpleNamespace(
        datafile="background_spectra_summary",
        configs=None,
        names=None,
        debug=False,
    )

    monkeypatch.setattr(imports_module.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(imports_module, "open", mock_open(), raising=False)
    monkeypatch.setattr(
        imports_module.pickle,
        "load",
        lambda _handle: {"Config": "cfg_a", "Name": "name_a", "Flux": 1.23},
    )

    df = imports_module.import_data(args)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 3)
    assert df.iloc[0].to_dict() == {"Config": "cfg_a", "Name": "name_a", "Flux": 1.23}