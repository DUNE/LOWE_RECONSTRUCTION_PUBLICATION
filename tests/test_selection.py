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