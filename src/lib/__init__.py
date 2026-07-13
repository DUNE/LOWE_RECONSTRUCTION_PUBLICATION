# Write here common initialization code for the scripts and shared variables

import os
import json
import pickle
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import LogNorm

from itertools import product

# Use DUNE style
import dunestyle.matplotlib as dunestyle

def _load_plot_params_config():
    default_config = {
        "rcparams": {"font.size": 11},
        "font_sizes": {
            "titlefontsize": "xx-large",
            "subtitlefontsize": "x-large",
            "legendtitlefontsize": "xx-large",
            "legendfontsize": "x-large",
            "xlabelfontsize": "xx-large",
            "ylabelfontsize": "xx-large",
            "xsublabelfontsize": "x-large",
            "ysublabelfontsize": "x-large",
            "linelabelfontsize": "large",
        },
        "plot_settings": {
            "nbins": 50,
            "default_linewidth": 2,
            "legend_style": {
                "fontsize": "x-large",
                "title_fontsize": "xx-large",
                "frameon": False,
                "loc": "best",
            },
            "figure_layout": {
                "base_width": 8,
                "panel_width": 5,
                "height": 6,
                "margins": {
                    "left": 0.12,
                    "right": 0.95,
                    "bottom": 0.12,
                    "top": 0.90,
                    "wspace": 0.25,
                    "hspace": 0.15,
                },
                "two_panel_hspace": 0,
            },
        },
        "mappings": {
            "config_dict": {
                "hd_1x2x6": "Signal",
                "hd_1x2x6_lateralAPA": "Lateral",
                "hd_1x2x6_centralAPA": "Central",
                "vd_1x8x14_3view_30deg": "Signal",
                "vd_1x8x14_3view_30deg_nominal": "Top",
                "vd_1x8x14_3view_30deg_shielded": "Bottom Shielded",
            },
            "config_color": {
                "hd_1x2x6": "C1",
                "hd_1x2x6_lateralAPA": "C1",
                "hd_1x2x6_centralAPA": "C1",
                "vd_1x8x14_3view_30deg": "C2",
                "vd_1x8x14_3view_30deg_nominal": "C2",
                "vd_1x8x14_3view_30deg_shielded": "C4",
            },
            "config_line": {
                "hd_1x2x6": "-",
                "hd_1x2x6_lateralAPA": "--",
                "hd_1x2x6_centralAPA": "-",
                "vd_1x8x14_3view_30deg": "-",
                "vd_1x8x14_3view_30deg_nominal": "-",
                "vd_1x8x14_3view_30deg_shielded": "-",
            },
            "particle_dict": {
                "11": "electron",
                "22": "gamma",
                "2112": "neutron",
                "2212": "proton",
                "1000020040": "alpha",
            },
            "particle_color": {
                "electron": "C3",
                "gamma": "C0",
                "neutron": "C4",
                "proton": "C1",
                "alpha": "C2",
            },
            "component_color": {
                "Ar39": "C1",
                "Kr85": "C2",
                "Ar42": "C3",
                "Rn22X": "C5",
                "CPA": "C6",
                "APA": "C7",
                "Gamma": "C0",
                "Neutron": "C4",
            },
            "simple_plane_dict": {"-1": "Total", "0": "APA"},
            "simple_plane_color": {},
            "plane_dict": {
                "-1": "Total",
                "0": "Cathode",
                "1": "Left Membrane",
                "2": "Right Membrane",
                "3": "FrontCap",
                "4": "EndCap",
            },
            "plane_color": {},
            "config_order": [
                "HD Signal",
                "HD Lateral",
                "HD Central",
                "VD Signal",
                "VD Top",
                "VD Bottom",
            ],
            "particle_order": ["marley", "neutrino", "alpha", "gamma", "neutron"],
            "solar_dict": {
                "pp": "pp",
                "pep": "pep",
                "be7": "⁷Be",
                "b7": "⁷Be",
                "b8": "⁸B",
                "hep": "HEP",
                "n13": "¹³N",
                "o15": "¹⁵O",
                "f17": "¹⁷F",
            },
            "solar_color": {
                "pp": "C0",
                "pep": "C1",
                "be7": "C2",
                "b7": "C2",
                "b8": "C3",
                "hep": "C4",
                "n13": "C5",
                "o15": "C6",
                "f17": "C7",
            },
            "sn_dict": {
                "nue": r"$\nu_e$",
                "nuebar": r"$\bar{\nu}_e$",
                "nux": r"$\nu_x$",
                "total": "Total",
            },
            "sn_color": {
                "nue": "C1",
                "nuebar": "C0",
                "nux": "C4",
                "total": "gray",
            },
        },
    }

    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "config", "plot_params.json")
    )

    if not os.path.exists(config_path):
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            loaded = json.load(config_file)
    except (json.JSONDecodeError, OSError):
        return default_config

    loaded_mappings = loaded.get("mappings", {})
    merged_mappings = {**default_config["mappings"], **loaded_mappings}

    return {
        "rcparams": loaded.get("rcparams", default_config["rcparams"]),
        "font_sizes": loaded.get("font_sizes", default_config["font_sizes"]),
        "plot_settings": loaded.get("plot_settings", default_config["plot_settings"]),
        "mappings": merged_mappings,
    }


_PLOT_PARAMS_CONFIG = _load_plot_params_config()

plt.rcParams.update(_PLOT_PARAMS_CONFIG.get("rcparams", {}))


def load_operation_config():
    """Load operation configuration from output_paths.json."""
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "config", "output_paths.json")
    )

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            loaded = json.load(config_file)
            return loaded.get("default_operation", "mean")
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return "mean"


_OPERATION_CONFIG = load_operation_config()

_FONT_SIZES = _PLOT_PARAMS_CONFIG.get("font_sizes", {})
titlefontsize = _FONT_SIZES.get("titlefontsize", "xx-large")
subtitlefontsize = _FONT_SIZES.get("subtitlefontsize", "x-large")
legendtitlefontsize = _FONT_SIZES.get("legendtitlefontsize", "xx-large")
legendfontsize = _FONT_SIZES.get("legendfontsize", "x-large")
xlabelfontsize = _FONT_SIZES.get("xlabelfontsize", "xx-large")
ylabelfontsize = _FONT_SIZES.get("ylabelfontsize", "xx-large")
xsublabelfontsize = _FONT_SIZES.get("xsublabelfontsize", "x-large")
ysublabelfontsize = _FONT_SIZES.get("ysublabelfontsize", "x-large")
linelabelfontsize = _FONT_SIZES.get("linelabelfontsize", "large")

_PLOT_SETTINGS = _PLOT_PARAMS_CONFIG.get("plot_settings", {})
nbins = _PLOT_SETTINGS.get("nbins", 50)
default_linewidth = _PLOT_SETTINGS.get("default_linewidth", 2)

_FIGURE_LAYOUT = _PLOT_SETTINGS.get("figure_layout", {})
figure_base_width = _FIGURE_LAYOUT.get("base_width", 8)
figure_panel_width = _FIGURE_LAYOUT.get("panel_width", 5)
figure_height = _FIGURE_LAYOUT.get("height", 6)
figure_margins_inches = _FIGURE_LAYOUT.get(
    "margins_inches",
    {
        "left": 0.96,
        "right": 0.40,
        "bottom": 0.72,
        "top": 0.60,
        "wspace": 0.25,
        "hspace": 0.15,
    },
)
figure_two_panel_hspace = _FIGURE_LAYOUT.get("two_panel_hspace", 0)

legend_style = _PLOT_SETTINGS.get(
    "legend_style",
    {
        "fontsize": legendfontsize,
        "title_fontsize": legendtitlefontsize,
        "frameon": False,
        "loc": "best",
    },
)

note_style = _PLOT_SETTINGS.get(
    "note_style",
    {
        "fontsize": "large",
        "bbox": {
            "boxstyle": "round,pad=0.5",
            "facecolor": "white",
            "alpha": 0.8,
            "edgecolor": "gray",
            "linewidth": 0.5,
        },
    },
)


def parse_point_pairs(point_values):
    if point_values is None:
        return []

    if isinstance(point_values, (list, tuple)) and len(point_values) > 0 and isinstance(
        point_values[0], (list, tuple, np.ndarray)
    ):
        flattened = [value for group in point_values for value in group]
    else:
        flattened = list(point_values)

    if len(flattened) % 2 != 0:
        raise ValueError(
            "--point expects an even number of float values (x y pairs)."
        )

    return [
        (float(flattened[idx]), float(flattened[idx + 1]))
        for idx in range(0, len(flattened), 2)
    ]


def normalize_point_labels(point_labels, n_points):
    if point_labels is None:
        return None, None

    if isinstance(point_labels, str):
        labels = [point_labels]
    else:
        labels = list(point_labels)

    if len(labels) != n_points:
        return None, (
            f"--point_label expects {n_points} label(s) to match --point pairs, "
            f"but got {len(labels)}."
        )

    return labels, None


def parse_square_quads(square_values):
    if square_values is None:
        return []

    if isinstance(square_values, (list, tuple)) and len(square_values) > 0 and isinstance(
        square_values[0], (list, tuple, np.ndarray)
    ):
        flattened = [value for group in square_values for value in group]
    else:
        flattened = list(square_values)

    if len(flattened) % 4 != 0:
        raise ValueError(
            "--square expects a multiple-of-4 number of float values (x1 y1 x2 y2 per square)."
        )

    return [
        (
            float(flattened[idx]),
            float(flattened[idx + 1]),
            float(flattened[idx + 2]),
            float(flattened[idx + 3]),
        )
        for idx in range(0, len(flattened), 4)
    ]


def normalize_square_labels(square_labels, n_squares):
    if square_labels is None:
        return None, None

    if isinstance(square_labels, str):
        labels = [square_labels]
    else:
        labels = list(square_labels)

    if len(labels) != n_squares:
        return None, (
            f"--square_label expects {n_squares} label(s) to match --square groups, "
            f"but got {len(labels)}."
        )

    return labels, None


def resolve_mapped_color(color_value):
    if color_value is None:
        return None

    if not isinstance(color_value, str):
        return color_value

    stripped = color_value.strip()
    lowered = stripped.lower()

    if lowered.startswith("rgb(") and stripped.endswith(")"):
        channels = stripped[4:-1].split(",")
        if len(channels) != 3:
            return stripped

        try:
            values = [float(channel.strip()) for channel in channels]
        except ValueError:
            return stripped

        if any(value > 1.0 for value in values):
            values = [value / 255.0 for value in values]

        return tuple(min(1.0, max(0.0, value)) for value in values)

    return stripped


def get_mapping_dict(mapping_name):
    if mapping_name is None:
        return None

    mapping = _MAPPINGS.get(mapping_name)
    return mapping if isinstance(mapping, dict) else None

_MAPPINGS = _PLOT_PARAMS_CONFIG.get("mappings", {})

config_dict = _MAPPINGS.get("config_dict", {})
config_color = _MAPPINGS.get("config_color", {})
config_line = _MAPPINGS.get("config_line", {})
name_color = _MAPPINGS.get("name_color", {})

particle_dict = {
    int(key): value for key, value in _MAPPINGS.get("particle_dict", {}).items()
}
particle_color = _MAPPINGS.get("particle_color", {})

simple_plane_dict = {
    int(key): value for key, value in _MAPPINGS.get("simple_plane_dict", {}).items()
}
simple_plane_color = _MAPPINGS.get("simple_plane_color", {})
plane_dict = {int(key): value for key, value in _MAPPINGS.get("plane_dict", {}).items()}
plane_color = _MAPPINGS.get("plane_color", {})
solar_dict = _MAPPINGS.get("solar_dict", {})
solar_color = _MAPPINGS.get("solar_color", {})
sn_dict = _MAPPINGS.get("sn_dict", {})
sn_color = _MAPPINGS.get("sn_color", {})

config_order = _MAPPINGS.get("config_order", [])
particle_order = _MAPPINGS.get("particle_order", [])
