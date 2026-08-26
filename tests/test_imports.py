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


def test_import_data_falls_back_to_studies_subfolder_when_no_configs_or_names(monkeypatch):
    args = SimpleNamespace(
        datafile="hd_1x2x6_centralAPA_marley_DayNight_Exposure_charge_Q100",
        configs=None,
        names=None,
        debug=False,
    )

    # Only the input/data/studies/ candidate "exists" — the flat one doesn't.
    monkeypatch.setattr(
        imports_module.os.path, "exists", lambda path: "studies" in path
    )
    monkeypatch.setattr(imports_module, "open", mock_open(), raising=False)
    monkeypatch.setattr(
        imports_module.pickle, "load", lambda _handle: {"Value": 1.23}
    )

    df = imports_module.import_data(args)

    assert not df.empty
    assert df.iloc[0].to_dict() == {"Value": 1.23}


def test_import_data_falls_back_to_studies_subfolder_for_config_name_pairs(monkeypatch):
    args = SimpleNamespace(
        datafile="DayNight_Exposure_charge_Q100",
        configs=["hd_1x2x6_centralAPA"],
        names=["marley"],
        debug=False,
        name_columns=False,
    )

    seen_paths = []

    def fake_exists(path):
        seen_paths.append(path)
        return "studies" in path

    monkeypatch.setattr(imports_module.os.path, "exists", fake_exists)
    monkeypatch.setattr(imports_module, "open", mock_open(), raising=False)
    monkeypatch.setattr(
        imports_module.pickle, "load", lambda _handle: {"Value": 4.56}
    )

    df = imports_module.import_data(args)

    assert not df.empty
    assert df.iloc[0].to_dict()["Value"] == 4.56
    # The flat input/data/ candidate must be tried before the studies/ fallback.
    assert "studies" not in seen_paths[0]
    assert any("studies" in p for p in seen_paths)