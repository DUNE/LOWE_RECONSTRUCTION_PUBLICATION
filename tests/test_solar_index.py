import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

import lib.solar_index as solar_index_module

filter_index_tree = solar_index_module.filter_index_tree


def _sample_tree():
    return {
        "_themes": {
            "daynight": "Day/night asymmetry plots",
            "hep": "HEP flux plots",
        },
        "daynight": {
            "rate_hist.pkl": {
                "themes": ["daynight"],
                "publication_export": True,
            },
            "asymmetry.pkl": {
                "themes": ["daynight", "hep"],
                "publication_export": False,
            },
        },
        "hep": {
            "flux.pkl": {
                "themes": ["hep"],
                "publication_export": True,
            },
        },
    }


def test_filter_index_tree_no_filter_returns_all_paths():
    tree = _sample_tree()

    result = filter_index_tree(tree)

    assert result == sorted([
        "daynight/rate_hist.pkl",
        "daynight/asymmetry.pkl",
        "hep/flux.pkl",
    ])


def test_filter_index_tree_by_theme():
    tree = _sample_tree()

    result = filter_index_tree(tree, themes=["daynight"])

    assert result == sorted(["daynight/rate_hist.pkl", "daynight/asymmetry.pkl"])


def test_filter_index_tree_publication_only():
    tree = _sample_tree()

    result = filter_index_tree(tree, publication_only=True)

    assert result == sorted(["daynight/rate_hist.pkl", "hep/flux.pkl"])


def test_filter_index_tree_unknown_theme_raises_with_available_themes():
    tree = _sample_tree()

    with pytest.raises(ValueError) as excinfo:
        filter_index_tree(tree, themes=["nonexistent"])

    message = str(excinfo.value)
    assert "nonexistent" in message
    assert "daynight" in message
    assert "hep" in message


def test_filter_index_tree_empty_tree_returns_empty_list():
    assert filter_index_tree({}) == []


def test_filter_index_tree_unwraps_top_level_tree_key():
    wrapped = {
        "_themes": {"daynight": "Day/night asymmetry plots"},
        "_publication_exports": ["analysis/day-night/rate_hist.pkl"],
        "tree": {
            "analysis": {
                "day-night": {
                    "rate_hist.pkl": {
                        "themes": ["daynight"],
                        "publication_export": True,
                    },
                },
            },
        },
    }

    result = filter_index_tree(wrapped)

    assert result == ["analysis/day-night/rate_hist.pkl"]
    assert not any(p.startswith("tree/") for p in result)
