import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd


def _load_module_and_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["script_compare_contour.py", "--datafile", "mock"])

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    src_dir = repo_root / "src"
    monkeypatch.syspath_prepend(str(scripts_dir))
    monkeypatch.syspath_prepend(str(src_dir))
    monkeypatch.syspath_prepend(str(repo_root))

    module = importlib.import_module("scripts.script_compare_contour")
    module = importlib.reload(module)
    from scripts.script_compare_contour import main

    return module, main


class _DummyMappable:
    def __init__(self, array=None):
        self.array = np.array([0.0, 1.0, 2.0]) if array is None else np.asarray(array)
        self.clim = None

    def get_array(self):
        return self.array

    def set_array(self, array):
        self.array = array

    def set_clim(self, low, high):
        self.clim = (low, high)


class _DummyAxis:
    def __init__(self):
        self.contour_calls = []
        self.pcolormesh_calls = []
        self.legend_calls = []

    def contour(self, x, y, z, **kwargs):
        self.contour_calls.append(
            {
                "x": np.asarray(x, dtype=float),
                "y": np.asarray(y, dtype=float),
                "z": np.asarray(z, dtype=float),
                **kwargs,
            }
        )
        return None

    def pcolormesh(self, x, y, z, **kwargs):
        self.pcolormesh_calls.append(
            {
                "x": np.asarray(x, dtype=float),
                "y": np.asarray(y, dtype=float),
                "z": np.asarray(z, dtype=float),
                **kwargs,
            }
        )
        return _DummyMappable(z)

    def plot(self, *args, **kwargs):
        pass

    def axhline(self, *args, **kwargs):
        pass

    def axvline(self, *args, **kwargs):
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

    def legend(self, *args, **kwargs):
        self.legend_calls.append({"args": args, "kwargs": kwargs})


class _DummyColorbar:
    def __init__(self):
        self.label = None
        self.ax = SimpleNamespace(
            yaxis=SimpleNamespace(set_label_position=lambda *args, **kwargs: None)
        )

    def set_label(self, value):
        self.label = value


class _DummyFig:
    def __init__(self):
        self.colorbars = []
        self.suptitle_calls = []

    def colorbar(self, _mappable, ax=None):
        cbar = _DummyColorbar()
        self.colorbars.append(cbar)
        return cbar

    def suptitle(self, *args, **kwargs):
        self.suptitle_calls.append({"args": args, "kwargs": kwargs})


def _mk_args(tmp_path, operation=None, background="all"):
    return SimpleNamespace(
        datafile="mock",
        configs=["cfg_a", "cfg_b"],
        names=["sample_a", "sample_b"],
        variables=None,
        x="XGrid",
        y="YGrid",
        z="ZGrid",
        percentile=[0, 100],
        iterable=None,
        select=None,
        save_values=None,
        labelx=None,
        labely=None,
        labelz=None,
        rangex=None,
        rangey=None,
        logz=False,
        density=False,
        zoom=False,
        matchx=False,
        matchy=False,
        horizontal=None,
        vertical=None,
        diagonal=False,
        operation=operation,
        background=background,
        contour_sigmas=[1.0, 2.0],
        contour_linewidth=2.0,
        contour_alpha=0.95,
        title=None,
        output=str(tmp_path / "artifact-root"),
        debug=False,
    )


def _patch_common(
    monkeypatch,
    module,
    args,
    df,
    artifact_name,
    axis=None,
    fig=None,
    stub_render=True,
):
    monkeypatch.setattr(module, "args", args, raising=False)
    monkeypatch.setattr(module, "import_data", lambda _args: df)
    monkeypatch.setattr(module, "filter_dataframe", lambda _df, _args: _df)
    monkeypatch.setattr(
        module, "prepare_import", lambda _args: (_args.configs, _args.names)
    )
    monkeypatch.setattr(module, "make_subtitle_from_args", lambda *a, **k: "sub")
    monkeypatch.setattr(module, "make_title_from_args", lambda _args: "title")
    monkeypatch.setattr(
        module,
        "make_name_from_args",
        lambda _args, prefix=None, suffix=None: artifact_name,
    )
    monkeypatch.setattr(module, "config_color", {"cfg_a": "C1", "cfg_b": "C2"}, raising=False)
    monkeypatch.setattr(module, "config_line", {"cfg_a": "-", "cfg_b": "--"}, raising=False)
    monkeypatch.setattr(module, "config_dict", {"cfg_a": "A", "cfg_b": "B"}, raising=False)
    monkeypatch.setattr(module, "subtitlefontsize", 10, raising=False)
    monkeypatch.setattr(module, "titlefontsize", 12, raising=False)
    monkeypatch.setattr(module, "rprint", lambda *a, **k: None)

    if stub_render:
        axis = axis or _DummyAxis()
        fig = fig or _DummyFig()
        monkeypatch.setattr(module.plt, "subplots", lambda **kwargs: (fig, axis))
        monkeypatch.setattr(
            module.plt,
            "savefig",
            lambda path: Path(path).write_bytes(b"test contour artifact"),
        )
        monkeypatch.setattr(module.plt, "close", lambda *a, **k: None)
        return axis, fig

    return None, None


def _example_dataframe(z_a, z_b):
    x = np.array([0.0, 0.5, 1.0])
    y = np.array([0.0, 1.0])
    df = pd.DataFrame(
        [
            {"Config": "cfg_a", "Name": "sample_a", "XGrid": x, "YGrid": y, "ZGrid": z_a},
            {"Config": "cfg_b", "Name": "sample_b", "XGrid": x, "YGrid": y, "ZGrid": z_b},
        ]
    )
    return x, y, df


def test_main_draws_image_background_and_config_contours(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation=None, background="all")

    z_a = np.array([[1.0, 2.0, 0.5], [0.2, 3.0, 0.1]])
    z_b = np.array([[0.5, 1.0, 0.2], [0.1, 0.4, 0.3]])
    x, y, df = _example_dataframe(z_a, z_b)

    axis, fig = _patch_common(
        monkeypatch,
        module,
        args,
        df,
        artifact_name="test_script_compare_contour.logic1",
        stub_render=True,
    )
    main()

    assert len(axis.pcolormesh_calls) == 1
    background_call = axis.pcolormesh_calls[0]
    assert np.allclose(background_call["x"], x)
    assert np.allclose(background_call["y"], y)
    assert np.allclose(background_call["z"], z_a + z_b)

    assert len(axis.contour_calls) == 2
    assert np.allclose(axis.contour_calls[0]["z"], z_a)
    assert np.allclose(axis.contour_calls[1]["z"], z_b)
    assert axis.contour_calls[0]["colors"] == ["C1"]
    assert axis.contour_calls[1]["colors"] == ["C2"]
    assert fig.colorbars[0].label == "ZGrid"
    assert axis.legend_calls

    output_file = plot_artifact_dir / "test_script_compare_contour.logic1"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_main_squared_sum_combines_z_grids_for_background_and_contour(
    monkeypatch, plot_artifact_dir
):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", background="combined")

    z_a = np.array([[3.0, 0.0, 1.0], [0.0, 2.0, 0.0]])
    z_b = np.array([[4.0, 1.0, 0.0], [0.0, 1.0, 2.0]])
    _x, _y, df = _example_dataframe(z_a, z_b)

    axis, _fig = _patch_common(
        monkeypatch,
        module,
        args,
        df,
        artifact_name="test_script_compare_contour.logic2",
        stub_render=True,
    )
    main()

    expected_combined = np.sqrt(np.square(z_a) + np.square(z_b))

    assert len(axis.pcolormesh_calls) == 1
    combined_background = axis.pcolormesh_calls[0]
    assert np.allclose(combined_background["z"], expected_combined)

    assert len(axis.contour_calls) == 3
    assert np.allclose(axis.contour_calls[-1]["z"], expected_combined)
    assert axis.contour_calls[-1]["colors"] == ["black"]

    output_file = plot_artifact_dir / "test_script_compare_contour.logic2"
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_main_renders_real_contour_plot_artifact(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation="squared_sum", background="combined")

    x = np.linspace(-3.0, 3.0, 160)
    y = np.linspace(-2.5, 2.5, 140)
    xx, yy = np.meshgrid(x, y)

    z_a = 2.8 * np.exp(-(((xx + 0.7) / 0.9) ** 2 + ((yy - 0.2) / 0.7) ** 2) / 2)
    z_a += 1.4 * np.exp(-(((xx - 1.2) / 0.55) ** 2 + ((yy + 0.9) / 0.8) ** 2) / 2)

    z_b = 2.2 * np.exp(-(((xx - 0.4) / 1.0) ** 2 + ((yy + 0.1) / 0.6) ** 2) / 2)
    z_b += 0.9 * np.exp(-(((xx + 1.6) / 0.7) ** 2 + ((yy - 1.1) / 0.5) ** 2) / 2)

    df = pd.DataFrame(
        [
            {"Config": "cfg_a", "Name": "sample_a", "XGrid": x, "YGrid": y, "ZGrid": z_a},
            {"Config": "cfg_b", "Name": "sample_b", "XGrid": x, "YGrid": y, "ZGrid": z_b},
        ]
    )

    _patch_common(
        monkeypatch,
        module,
        args,
        df,
        artifact_name="test_script_compare_contour.png",
        stub_render=False,
    )
    main()

    output_file = plot_artifact_dir / "test_script_compare_contour.png"
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    assert output_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_main_interpolates_nan_entries_before_contouring(monkeypatch, plot_artifact_dir):
    module, main = _load_module_and_main(monkeypatch)
    args = _mk_args(plot_artifact_dir, operation=None, background="all")

    z_a = np.array([[1.0, np.nan, 0.5], [0.2, 3.0, 0.1]])
    z_b = np.array([[0.5, 1.0, 0.2], [0.1, 0.4, np.nan]])
    _x, _y, df = _example_dataframe(z_a, z_b)

    axis, _fig = _patch_common(
        monkeypatch,
        module,
        args,
        df,
        artifact_name="test_script_compare_contour.nan_fill",
        stub_render=True,
    )
    main()

    assert len(axis.contour_calls) == 2
    assert np.isfinite(axis.contour_calls[0]["z"]).all()
    assert np.isfinite(axis.contour_calls[1]["z"]).all()
