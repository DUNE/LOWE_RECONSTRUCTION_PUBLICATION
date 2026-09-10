import sys
from pathlib import Path

import pandas as pd

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

from lib.selection import filter_dataframe


class _Args:
    def __init__(self):
        self.variables = None
        self.select = "Variable"
        self.save_values = ["Asimov"]
        self.iterable = None
        self.debug = False


def test_filter_dataframe_accepts_string_select_column_name():
    df = pd.DataFrame(
        [
            {"Variable": None, "Value": 1},
            {"Variable": "Asimov", "Value": 2},
            {"Variable": "Gaussian", "Value": 3},
        ]
    )

    filtered = filter_dataframe(df, _Args())

    assert list(filtered["Value"]) == [2]


def test_filter_dataframe_or_matches_repeated_select_column():
    args = _Args()
    args.select = ["Variable", "SpectrumType", "SpectrumType"]
    args.save_values = ["Asimov", "Smoothed", "Raw"]
    df = pd.DataFrame(
        [
            {"Variable": "Asimov", "SpectrumType": "Smoothed", "Value": 1},
            {"Variable": "Asimov", "SpectrumType": "Raw", "Value": 2},
            {"Variable": "Asimov", "SpectrumType": "Gaussian", "Value": 3},
            {"Variable": "Gaussian", "SpectrumType": "Raw", "Value": 4},
        ]
    )

    filtered = filter_dataframe(df, args)

    assert list(filtered["Value"]) == [1, 2]