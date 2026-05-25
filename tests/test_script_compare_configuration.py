import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest


def _load_module_and_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script_compare_configuration.py"])

    # Ensure src/lib is importable as top-level "lib"
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    src_dir = repo_root / "src"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(src_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_compare_configuration")
    module = importlib.reload(module)
    from scripts.script_compare_configuration import main

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

    def axhline(self, *args, **kwargs):
        pass

    def axvline(self, *args, **kwargs):
        pass

    def set_yscale(self, *args, **kwargs):
        pass

    def set_xscale(self, *args, **kwargs):
        pass

    def legend(self, *args, **kwargs):
        pass


class _DummyFig:
    def suptitle(self, *args, **kwargs):
        pass


def _mk_args(tmp_path, operation="squared_sum", errory=True):
    return SimpleNamespace(
        datafile="mock",
        configs=["hd_cfg_a", "hd_cfg_b"],
        names=["name_a", "name_b"],
        variables=None,
        iterable=None,
        select=None,
        save_values=None,
        comparable="Config",
        x="Values",
        y="Counts",
        rangex=None,
        rangey=None,
        errory=errory,
        errory_type="bars",
        operation=operation,
        logx=False,
        logy=False,
        labelx=None,
        labely=None,
        align="mid",
        mirror=None,
        project=None,
        project_offset=0.0,
        project_scale=1.0,
        combine=None,
        combine_operation=None,
        horizontal=None,
        vertical=None,
        title=None,
        output=str(tmp_path / "out"),
        debug=False,
    )


def _patch_common(monkeypatch, module, args, df):
    calls = []

    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_subtitle_from_args", lambda _args, _idx: "sub")
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module, "make_name_from_args", lambda _args, prefix, suffix: "comparison.png"
    )
    monkeypatch.setattr(
        module, "config_dict", {cfg: cfg for cfg in args.configs}, raising=False
    )
    monkeypatch.setattr(module, "subtitlefontsize", 10, raising=False)
    monkeypatch.setattr(module, "titlefontsize", 12, raising=False)
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    original_plot_data = module.plot_data

    def recording_plot_data(
        _args,
        _ax,
        x,
        x_edges,
        y,
        errory,
        errory_sym,
        label,
        color,
        linestyle,
        **kwargs,
    ):
        calls.append(
            {
                "x": np.asarray(x, dtype=float),
                "x_edges": np.asarray(x_edges, dtype=float),
                "y": np.asarray(y, dtype=float),
                "errory": None if errory is None else np.asarray(errory, dtype=float),
                "errory_sym": errory_sym,
                "label": label,
                "color": color,
                "linestyle": linestyle,
            }
        )
        return original_plot_data(
            _args,
            _ax,
            x,
            x_edges,
            y,
            errory,
            errory_sym,
            label,
            color,
            linestyle,
            **kwargs,
        )

    monkeypatch.setattr(module, "plot_data", recording_plot_data)
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, prefix, suffix: "test_script_compare_configuration.png",
    )

    return calls


def _get_combined_call(calls):
    combined = [c for c in calls if c["label"] == "Combined"]
    assert combined, "Expected a Combined plot_data call."
    return combined[0]


def test_main_error_propagation_symmetric_squared_sum(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", errory=True)

    x = np.linspace(0.5, 10.0, 48)
    y1 = 12.0 + 3.5 * np.sin(0.6 * x) + 1.2 * x
    y2 = 1.5 + 0.8 * np.cos(0.8 * x) + 0.25 * x
    e1 = np.full_like(x, 1.0)
    e2 = np.full_like(x, 2.0)

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x,
                "Counts": y1,
                "CountsError": e1,
            },
            {
                "Config": "hd_cfg_b",
                "Name": "name_b",
                "Variable": "v",
                "Values": x,
                "Counts": y2,
                "CountsError": e2,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    c = _get_combined_call(calls)
    expected_y = np.sqrt(np.square(y1) + np.square(y2))
    expected_e = np.sqrt(np.square(e1) + np.square(e2))

    assert np.allclose(c["y"], expected_y)
    assert np.allclose(c["errory"], expected_e)
    assert c["errory_sym"] == "symmetric"
    output_file = plot_artifact_dir / "test_script_compare_configuration.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_main_error_propagation_asymmetric_squared_sum(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", errory=True)

    x = [1.0, 2.0, 3.0]
    y1 = [5.0, 6.0, 7.0]
    y2 = [1.0, 1.0, 1.0]
    em1 = [1.0, 1.0, 1.0]  # lower
    em2 = [2.0, 2.0, 2.0]
    ep1 = [3.0, 3.0, 3.0]  # upper
    ep2 = [4.0, 4.0, 4.0]

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x,
                "Counts": y1,
                "CountsError-": em1,
                "CountsError+": ep1,
            },
            {
                "Config": "hd_cfg_b",
                "Name": "name_b",
                "Variable": "v",
                "Values": x,
                "Counts": y2,
                "CountsError-": em2,
                "CountsError+": ep2,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    c = _get_combined_call(calls)

    expected_lower = np.sqrt(np.square(em1) + np.square(em2))
    expected_upper = np.sqrt(np.square(ep1) + np.square(ep2))
    expected_err = np.vstack([expected_lower, expected_upper])

    assert c["errory"].shape == (2, 3)
    assert np.allclose(c["errory"], expected_err)
    assert c["errory_sym"] == "asymmetric"


def test_main_error_propagation_sum_should_sqrt_variances(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="sum", errory=True)

    x = [1.0, 2.0, 3.0]
    y1 = [10.0, 20.0, 30.0]
    y2 = [1.0, 2.0, 3.0]
    e1 = [1.0, 1.0, 1.0]
    e2 = [2.0, 2.0, 2.0]

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x,
                "Counts": y1,
                "CountsError": e1,
            },
            {
                "Config": "hd_cfg_b",
                "Name": "name_b",
                "Variable": "v",
                "Values": x,
                "Counts": y2,
                "CountsError": e2,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    c = _get_combined_call(calls)
    expected_e = np.sqrt(np.square(e1) + np.square(e2))
    assert np.allclose(c["errory"], expected_e)


def test_main_combine_by_geometry_returns_two_lines(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation=None, errory=False)
    args.combine = "Geometry"
    args.configs = [
        "hd_cfg_a",
        "hd_cfg_b",
        "vd_cfg_a",
        "vd_cfg_b",
    ]
    args.names = ["name", "name", "name", "name"]

    x = np.array([1.0, 2.0, 3.0])
    y_hd_a = np.array([10.0, 20.0, 30.0])
    y_hd_b = np.array([14.0, 22.0, 34.0])
    y_vd_a = np.array([6.0, 8.0, 12.0])
    y_vd_b = np.array([10.0, 12.0, 16.0])

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name",
                "Variable": "v",
                "Values": x,
                "Counts": y_hd_a,
            },
            {
                "Config": "hd_cfg_b",
                "Name": "name",
                "Variable": "v",
                "Values": x,
                "Counts": y_hd_b,
            },
            {
                "Config": "vd_cfg_a",
                "Name": "name",
                "Variable": "v",
                "Values": x,
                "Counts": y_vd_a,
            },
            {
                "Config": "vd_cfg_b",
                "Name": "name",
                "Variable": "v",
                "Values": x,
                "Counts": y_vd_b,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    labels = [call["label"] for call in calls]
    assert labels == ["HD", "VD"]

    expected_hd = (y_hd_a + y_hd_b) / 2.0
    expected_vd = (y_vd_a + y_vd_b) / 2.0
    assert np.allclose(calls[0]["y"], expected_hd)
    assert np.allclose(calls[1]["y"], expected_vd)


def test_main_combine_operation_sum_uses_group_sum(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation=None, errory=False)
    args.combine = "Geometry"
    args.combine_operation = "sum"
    args.configs = ["hd_cfg_a", "hd_cfg_b"]
    args.names = ["name", "name"]

    x = np.array([1.0, 2.0, 3.0])
    y_a = np.array([10.0, 20.0, 30.0])
    y_b = np.array([1.0, 2.0, 3.0])

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name",
                "Variable": "v",
                "Values": x,
                "Counts": y_a,
            },
            {
                "Config": "hd_cfg_b",
                "Name": "name",
                "Variable": "v",
                "Values": x,
                "Counts": y_b,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    assert len(calls) == 1
    assert calls[0]["label"] == "HD"
    assert np.allclose(calls[0]["y"], y_a + y_b)


def test_main_combine_geometry_mismatched_x_only_combines_shared_bins(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation=None, errory=False)
    args.combine = "Geometry"
    args.combine_operation = "mean"
    args.configs = ["hd_cfg_a", "hd_cfg_b"]
    args.names = ["name", "name"]

    x_a = np.array([0.0, 1.0, 2.0, 3.0])
    y_a = np.array([10.0, 20.0, 30.0, 40.0])
    x_b = np.array([2.0, 3.0, 4.0])
    y_b = np.array([100.0, 200.0, 300.0])

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name",
                "Variable": "v",
                "Values": x_a,
                "Counts": y_a,
            },
            {
                "Config": "hd_cfg_b",
                "Name": "name",
                "Variable": "v",
                "Values": x_b,
                "Counts": y_b,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    assert len(calls) == 1
    assert calls[0]["label"] == "HD"
    assert np.allclose(calls[0]["x"], np.array([0.0, 1.0, 2.0, 3.0, 4.0]))
    assert np.allclose(
        calls[0]["y"],
        np.array([10.0, 20.0, 65.0, 120.0, 300.0]),
    )


def test_main_operation_with_no_matching_data_does_not_crash(
    monkeypatch, plot_artifact_dir
):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", errory=True)

    x = np.array([1.0, 2.0, 3.0])
    y = np.array([10.0, 20.0, 30.0])
    e = np.array([1.0, 1.0, 1.0])

    # Deliberately no rows match the requested config/name combinations.
    df = pd.DataFrame(
        [
            {
                "Config": "other_cfg",
                "Name": "other_name",
                "Variable": "v",
                "Values": x,
                "Counts": y,
                "CountsError": e,
            }
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)

    # Should not raise UnboundLocalError and should not emit a combined line.
    main()
    assert not [c for c in calls if c["label"] == "Combined"]


def test_main_mixed_row_shapes_scalar_x_vector_y_is_supported(
    monkeypatch, plot_artifact_dir
):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", errory=False)
    args.configs = ["hd_cfg_a"]
    args.names = ["name_a"]

    # First row uses scalar x with vector y (should be broadcast), second row is valid.
    x_valid = np.array([1.0, 2.0, 3.0])
    y_valid = np.array([2.0, 3.0, 4.0])
    x_scalar = 30.0
    y_scalar_row = np.array([1.0, 2.0])
    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x_scalar,
                "Counts": y_scalar_row,
            },
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x_valid,
                "Counts": y_valid,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    # Main should complete and include both rows in combined output.
    c = _get_combined_call(calls)
    expected_x = np.concatenate([np.full(y_scalar_row.shape, x_scalar), x_valid])
    expected_y = np.concatenate([y_scalar_row, y_valid])
    assert np.allclose(c["x"], expected_x[::-1])
    assert np.allclose(c["y"], expected_y)


def test_main_scalar_x_uses_matching_array_axis_when_available(
    monkeypatch, plot_artifact_dir
):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", errory=False)
    args.configs = ["hd_cfg_a"]
    args.names = ["name_a"]
    args.x = "Exposure"
    args.y = "Significance"

    energy = np.array([5.0, 10.5, 11.5, 12.5, 13.5])
    significance = np.array([0.1, 0.2, 0.5, 0.8, 1.0])

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "Asimov",
                "Exposure": 30,
                "Energy": energy,
                "Significance": significance,
            }
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    c = _get_combined_call(calls)
    assert np.allclose(c["x"], energy)
    assert np.allclose(c["y"], significance)


def test_main_non_monotonic_reversal_with_missing_errory_does_not_crash(
    monkeypatch, plot_artifact_dir
):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", errory=True)
    args.configs = ["hd_cfg_a"]
    args.names = ["name_a"]

    # errory is requested, but no CountsError* columns are present.
    # x becomes non-monotonic after scalar-x broadcasting and concatenation.
    x_valid = np.array([1.0, 2.0, 3.0])
    y_valid = np.array([2.0, 3.0, 4.0])
    x_scalar = 30.0
    y_scalar_row = np.array([1.0, 2.0])

    df = pd.DataFrame(
        [
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x_scalar,
                "Counts": y_scalar_row,
            },
            {
                "Config": "hd_cfg_a",
                "Name": "name_a",
                "Variable": "v",
                "Values": x_valid,
                "Counts": y_valid,
            },
        ]
    )

    calls = _patch_common(monkeypatch, module, args, df)
    main()

    assert _get_combined_call(calls)
