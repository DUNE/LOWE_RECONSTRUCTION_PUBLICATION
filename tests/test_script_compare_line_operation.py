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
        [
            "script_compare_line_operation.py",
            "--datafile",
            "mock",
            "-i",
            "Category",
            "-x",
            "Values",
            "-y",
            "Density",
        ],
    )

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_compare_line_operation")
    module = importlib.reload(module)
    from scripts.script_compare_line_operation import main

    return module, main


def test_compute_bottom_series_relative_difference_percent(monkeypatch):
    module, _ = _load_module_and_main(monkeypatch)

    labels = ["a", "b"]
    y_ref = np.array([1.0, 2.0, 4.0])
    y_other = np.array([2.0, 4.0, 8.0])

    series = module.compute_bottom_series(
        labels,
        [y_ref, y_other],
        "relative_difference",
        reference_index=0,
    )

    assert len(series) == 1
    _, y_values = series[0]
    np.testing.assert_allclose(y_values, np.array([100.0, 100.0, 100.0]))


def test_compute_bottom_series_asymmetry(monkeypatch):
    module, _ = _load_module_and_main(monkeypatch)

    labels = ["first", "second"]
    y_first = np.array([2.0, 4.0, 8.0])
    y_second = np.array([1.0, 2.0, 4.0])

    series = module.compute_bottom_series(
        labels,
        [y_first, y_second],
        "asymmetry",
        reference_index=0,
    )

    assert len(series) == 1
    _, y_values = series[0]
    expected = (y_first - y_second) / (0.5 * (y_first + y_second))
    np.testing.assert_allclose(y_values, expected)


def test_main_generates_plot_for_relative_difference(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        iterable="Category",
        select=None,
        save_values=None,
        x="Values",
        y="Density",
        operation="relative_difference",
        reference=0,
        reference_value=None,
        reduce=False,
        labelx="X",
        labely="Y",
        labelz=None,
        bottom_labely=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        bottom_rangey=None,
        plot_style="-",
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        vertical=None,
        horizontal=None,
        vertical_label=None,
        horizontal_label=None,
    )

    x = np.array([1.0, 2.0, 3.0, 4.0])
    y_a = np.array([1.0, 2.0, 3.0, 4.0])
    y_b = np.array([2.0, 4.0, 6.0, 8.0])

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "first",
                "Values": x,
                "Density": y_a,
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "second",
                "Values": x,
                "Density": y_b,
            },
        ]
    )

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_compare_line_operation.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    main()

    output_file = plot_artifact_dir / "test_script_compare_line_operation.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_main_skips_fallback_bottom_series(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        iterable="Component",
        select=None,
        save_values=None,
        x="Energy",
        y="Counts",
        operation=None,
        default_operation="Significance",
        significance_column=None,
        reference=0,
        reference_value=None,
        reduce=False,
        labelx="X",
        labely="Y",
        labelz=None,
        bottom_labely=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        bottom_rangey=None,
        plot_style="-",
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        vertical=None,
        horizontal=None,
        vertical_label=None,
        horizontal_label=None,
        no_lower_plot=False,
    )

    x = np.array([1.0, 2.0, 3.0, 4.0])
    solar_day_counts = np.array([1.0, 2.0, 3.0, 4.0])
    solar_night_counts = np.array([2.0, 4.0, 6.0, 8.0])
    solar_day_significance = np.array([0.4, 0.5, 0.6, 0.7])

    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Component": "Solar Day",
                "Energy": x,
                "Counts": solar_day_counts,
                "Significance": solar_day_significance,
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Component": "Solar Night",
                "Energy": x,
                "Counts": solar_night_counts,
                "Significance": None,
            },
        ]
    )

    plot_labels = []

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_compare_line_operation.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)
    monkeypatch.setattr(
        module,
        "plot_data",
        lambda *a, **k: plot_labels.append(k.get("label")),
    )

    main()

    assert plot_labels.count("Significance") == 1
    assert None not in plot_labels


def test_main_warns_when_comparable_and_stacked(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        iterable="Component",
        comparable="SpectrumType",
        comparable_linestyles=["dashed", "solid"],
        comparable_linewidths=[2, 3],
        select=None,
        save_values=None,
        x="Energy",
        y="Counts",
        operation=None,
        default_operation=None,
        reference=0,
        reference_value=None,
        reduce=False,
        labelx="X",
        labely="Y",
        labelz=None,
        bottom_labely=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        bottom_rangey=None,
        plot_style="-",
        plot_type="step",
        stacked=True,
        stack_reverse_requested=False,
        no_lower_plot=True,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        vertical=None,
        horizontal=None,
        vertical_label=None,
        horizontal_label=None,
        no_capitalize_legend=False,
    )

    x = np.array([1.0, 2.0, 3.0, 4.0])
    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Component": "signal",
                "SpectrumType": "raw",
                "Energy": x,
                "Counts": np.array([1.0, 1.0, 1.0, 1.0]),
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Component": "signal",
                "SpectrumType": "smoothed",
                "Energy": x,
                "Counts": np.array([10.0, 10.0, 10.0, 10.0]),
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Component": "background",
                "SpectrumType": "raw",
                "Energy": x,
                "Counts": np.array([2.0, 2.0, 2.0, 2.0]),
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Component": "background",
                "SpectrumType": "smoothed",
                "Energy": x,
                "Counts": np.array([20.0, 20.0, 20.0, 20.0]),
            },
        ]
    )

    calls = []
    warnings = []
    suffixes = []

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: suffixes.append(suffix) or "test_script_compare_line_operation.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: warnings.append(" ".join(str(v) for v in a)))
    monkeypatch.setattr(
        module,
        "plot_data",
        lambda *a, **k: calls.append(
            {
                "ax": a[1],
                "label": k.get("label"),
                "plot_type": k.get("plot_type"),
                "width": k.get("width"),
                "linestyle": k.get("linestyle"),
                "y": None if k.get("y") is None else k.get("y").copy(),
                "bottom": None if k.get("bottom") is None else k.get("bottom").copy(),
            }
        ),
    )

    main()

    top_ax = calls[0]["ax"]
    top_calls = [call for call in calls if call["ax"] is top_ax]

    assert len(top_calls) == 4
    assert all(call["plot_type"] == "plot" for call in top_calls)
    assert any("--stacked is not supported together with --comparable" in warning for warning in warnings)
    assert suffixes == ["stacked_line_operation.png"]
    assert all(call["width"] is None for call in top_calls)
    assert top_calls[0]["linestyle"] == "dashed"
    assert top_calls[1]["linestyle"] == "solid"
    np.testing.assert_allclose(top_calls[0]["y"], np.array([1.0, 1.0, 1.0, 1.0]))
    np.testing.assert_allclose(top_calls[1]["y"], np.array([10.0, 10.0, 10.0, 10.0]))
    np.testing.assert_allclose(top_calls[2]["y"], np.array([2.0, 2.0, 2.0, 2.0]))
    np.testing.assert_allclose(top_calls[3]["y"], np.array([20.0, 20.0, 20.0, 20.0]))
    assert all(call["bottom"] is None for call in top_calls)


def test_main_uses_full_width_for_stacked_bars(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        iterable="Category",
        select=None,
        save_values=None,
        x="Energy",
        y="Counts",
        operation=None,
        default_operation=None,
        reference=0,
        reference_value=None,
        reduce=False,
        labelx="X",
        labely="Y",
        labelz=None,
        bottom_labely=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        bottom_rangey=None,
        plot_style="-",
        plot_type="step",
        stacked=True,
        stack_reverse_requested=False,
        no_lower_plot=True,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        vertical=None,
        horizontal=None,
        vertical_label=None,
        horizontal_label=None,
        no_capitalize_legend=False,
    )

    x = np.array([1.0, 2.0, 3.0, 4.0])
    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "first",
                "Energy": x,
                "Counts": np.array([1.0, 1.0, 1.0, 1.0]),
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "second",
                "Energy": x,
                "Counts": np.array([2.0, 2.0, 2.0, 2.0]),
            },
        ]
    )

    calls = []

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_compare_line_operation.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)
    monkeypatch.setattr(
        module,
        "plot_data",
        lambda *a, **k: calls.append(
            {
                "ax": a[1],
                "plot_type": k.get("plot_type"),
                "width": k.get("width"),
                "bottom": None if k.get("bottom") is None else k.get("bottom").copy(),
            }
        ),
    )

    main()

    top_ax = calls[0]["ax"]
    top_calls = [call for call in calls if call["ax"] is top_ax]

    assert len(top_calls) == 2
    assert all(call["plot_type"] == "bar" for call in top_calls)
    np.testing.assert_allclose(top_calls[0]["width"], 1.0)
    np.testing.assert_allclose(top_calls[1]["width"], 1.0)
    np.testing.assert_allclose(top_calls[0]["bottom"], np.zeros_like(x, dtype=float))
    np.testing.assert_allclose(top_calls[1]["bottom"], np.array([1.0, 1.0, 1.0, 1.0]))


def test_main_reverses_stack_order_when_requested(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)

    args = SimpleNamespace(
        datafile="mock",
        configs=["cfg_a"],
        names=["sample_a"],
        variables=None,
        iterable="Category",
        select=None,
        save_values=None,
        x="Energy",
        y="Counts",
        operation=None,
        default_operation=None,
        reference=0,
        reference_value=None,
        reduce=False,
        labelx="X",
        labely="Y",
        labelz=None,
        bottom_labely=None,
        logx=False,
        logy=False,
        rangex=None,
        rangey=None,
        bottom_rangey=None,
        plot_style="-",
        plot_type="step",
        stacked=True,
        stack_reverse_requested=True,
        no_lower_plot=True,
        title=None,
        output=str(plot_artifact_dir / "artifact-root"),
        debug=False,
        vertical=None,
        horizontal=None,
        vertical_label=None,
        horizontal_label=None,
        no_capitalize_legend=False,
    )

    x = np.array([1.0, 2.0, 3.0, 4.0])
    df = pd.DataFrame(
        [
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "first",
                "Energy": x,
                "Counts": np.array([1.0, 1.0, 1.0, 1.0]),
            },
            {
                "Config": "cfg_a",
                "Name": "sample_a",
                "Category": "second",
                "Energy": x,
                "Counts": np.array([2.0, 2.0, 2.0, 2.0]),
            },
        ]
    )

    calls = []

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, _idx, prefix, suffix: "test_script_compare_line_operation.png",
    )
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)
    monkeypatch.setattr(
        module,
        "plot_data",
        lambda *a, **k: calls.append(
            {
                "ax": a[1],
                "label": k.get("label"),
                "plot_type": k.get("plot_type"),
                "bottom": None if k.get("bottom") is None else k.get("bottom").copy(),
            }
        ),
    )

    main()

    top_ax = calls[0]["ax"]
    top_calls = [call for call in calls if call["ax"] is top_ax]

    assert len(top_calls) == 2
    assert [call["label"] for call in top_calls] == ["second", "first"]
    np.testing.assert_allclose(top_calls[0]["bottom"], np.zeros_like(x, dtype=float))
    np.testing.assert_allclose(top_calls[1]["bottom"], np.array([2.0, 2.0, 2.0, 2.0]))
