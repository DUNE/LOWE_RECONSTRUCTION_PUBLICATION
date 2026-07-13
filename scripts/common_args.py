import copy
import json
import os
import re
import ast
import sys

# Add parent directory to path so we can import from src.lib
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

# Lazy imports for the mapping functions - only imported when functions are called
_get_mapping_dict = None
_resolve_mapped_color = None
_particle_dict = None
_plane_dict = None
_simple_plane_dict = None

def _load_lib_imports():
    """Load lib imports lazily to avoid circular imports."""
    global _get_mapping_dict, _resolve_mapped_color, _particle_dict, _plane_dict, _simple_plane_dict
    if _get_mapping_dict is None:
        try:
            from lib import get_mapping_dict, resolve_mapped_color, particle_dict, plane_dict, simple_plane_dict
            _get_mapping_dict = get_mapping_dict
            _resolve_mapped_color = resolve_mapped_color
            _particle_dict = particle_dict
            _plane_dict = plane_dict
            _simple_plane_dict = simple_plane_dict
        except ImportError as e:
            raise ImportError(f"Failed to import from lib: {e}")


def _auto_wrap_mathtext(value):
    """Wrap simple caret/subscript math notation in Matplotlib math text delimiters.

    This keeps plain text labels unchanged, but turns examples like
    "Cross Section (10^{-38} cm^{2})" into
    "Cross Section ($10^{-38} cm^{2}$)".
    """
    if not isinstance(value, str):
        return value

    if "$" in value:
        return value

    if re.search(r"[\^_]\{[^}]+\}", value) is None:
        return value

    wrapped = re.sub(
        r"\(([^()]*[\^_]\{[^}]+\}[^()]*)\)",
        lambda match: f"(${match.group(1)}$)",
        value,
    )

    if wrapped != value:
        return wrapped

    return f"${value}$"


def parse_plot_label(value):
    """Parse CLI label values, including raw-literal-like terminal input.

    Supported forms:
    - r'...'/r"..." passed as a single argument token.
    - shell-collapsed form from bash, e.g. r'Cross Section (...)' becoming
      rCross Section (...).
    - explicit r* prefix for unambiguous raw-style input, e.g.
      r*Cross Section (10^{-38} cm^{2}).
    """
    if value is None or not isinstance(value, str):
        return value

    text = value.strip()
    if not text:
        return value

    # Treat the literal string "None" as an explicit request for no label.
    if text.lower() == "none":
        return ""

    if text.startswith(("r'", 'r"', "R'", 'R"')):
        try:
            text = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            pass
    elif text.startswith(("r*", "R*")):
        text = text[2:].lstrip()
    elif (
        len(text) > 1
        and text[0] in {"r", "R"}
        and text[1].isupper()
        and any(token in text for token in ("^{", "_{", "\\", "$"))
    ):
        text = text[1:]

    return _auto_wrap_mathtext(text)


COMMON_ARG_SPECS = {
    "datafile": {
        "flags": ["--datafile"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Path/name of the input data file (pkl format)",
        },
    },
    "configs": {
        "flags": ["--configs"],
        "kwargs": {
            "nargs": "+",
            "type": str,
            "default": None,
            "help": "DUNE detector configuration(s) to include in the plot",
        },
    },
    "names": {
        "flags": ["--names", "-n"],
        "kwargs": {
            "nargs": "+",
            "type": str,
            "default": None,
            "help": "Name of the simulation configuration",
        },
    },
    "variables": {
        "flags": ["--variables", "-v"],
        "kwargs": {
            "nargs": "+",
            "type": str,
            "default": None,
            "help": "List of variable parameters/columns to filter data",
        },
    },
    "iterable": {
        "flags": ["--iterable", "--i", "-i"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Iterable column to produce plots",
        },
    },
    "select": {
        "flags": ["--select"],
        "kwargs": {
            "nargs": "+",
            "default": None,
            "help": "Columns/keys used for filtering",
        },
    },
    "save_values": {
        "flags": ["--save_values", "-s"],
        "kwargs": {
            "nargs": "+",
            "default": None,
            "help": "Values used alongside --select filtering",
        },
    },
    "x": {
        "flags": ["-x"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Column name for x-axis values",
        },
    },
    "y": {
        "flags": ["-y"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Column name for y-axis values",
        },
    },
    "z": {
        "flags": ["-z"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Column name for z-axis values",
        },
    },
    "reduce": {
        "flags": ["--reduce"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Reduce number of plotted lines for clarity",
        },
    },
    "bins": {
        "flags": ["--bins", "-b"],
        "kwargs": {
            "type": int,
            "default": 50,
            "help": "Number of bins for histogram",
        },
    },
    "percentile": {
        "flags": ["--percentile", "-p"],
        "kwargs": {
            "nargs": 2,
            "type": float,
            "default": None,
            "help": "Percentile range for axis limits",
        },
    },
    "labelx": {
        "flags": ["--labelx"],
        "kwargs": {
            "type": parse_plot_label,
            "default": None,
            "help": "Label for x-axis on plot",
        },
    },
    "labely": {
        "flags": ["--labely"],
        "kwargs": {
            "type": parse_plot_label,
            "default": None,
            "help": "Label for y-axis on plot",
        },
    },
    "labelz": {
        "flags": ["--labelz"],
        "kwargs": {
            "type": parse_plot_label,
            "default": None,
            "help": "Label for z/legend axis on plot",
        },
    },
    "logx": {
        "flags": ["--logx"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Set x-axis to logarithmic scale",
        },
    },
    "logy": {
        "flags": ["--logy"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Set y-axis to logarithmic scale",
        },
    },
    "logz": {
        "flags": ["--logz"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Set z-axis to logarithmic scale",
        },
    },
    "rangex": {
        "flags": ["--rangex"],
        "kwargs": {
            "nargs": 2,
            "type": float,
            "default": None,
            "help": "Range for x-axis (min max)",
        },
    },
    "rangey": {
        "flags": ["--rangey"],
        "kwargs": {
            "nargs": 2,
            "type": float,
            "default": None,
            "help": "Range for y-axis (min max)",
        },
    },
    "rangez": {
        "flags": ["--rangez"],
        "kwargs": {
            "nargs": 2,
            "type": float,
            "default": None,
            "help": "Range for z-axis/colorbar (min max)",
        },
    },
    "density": {
        "flags": ["--density"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Normalize to density",
        },
    },
    "zoom": {
        "flags": ["--zoom"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Enable zoom behavior",
        },
    },
    "matchx": {
        "flags": ["--matchx"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Match x-axis ranges across subplots",
        },
    },
    "matchy": {
        "flags": ["--matchy"],
        "kwargs": {
            "action": "store_true",
            "default": False,
            "help": "Match y-axis ranges across subplots",
        },
    },
    "horizontal": {
        "flags": ["--horizontal"],
        "kwargs": {
            "type": float,
            "nargs": "+",
            "default": None,
            "help": "Draw horizontal line(s) at specified y value(s)",
        },
    },
    "horizontal_label": {
        "flags": ["--horizontal_label"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Label(s) for horizontal line(s), one per line",
        },
    },
    "horizontal_style": {
        "flags": ["--horizontal_style"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Linestyle(s) for horizontal line(s) (e.g. -- : -. -), one per line",
        },
    },
    "horizontal_color": {
        "flags": ["--horizontal_color"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Color(s) for horizontal line(s) (e.g. gray red C0), one per line",
        },
    },
    "vertical": {
        "flags": ["--vertical"],
        "kwargs": {
            "type": float,
            "nargs": "+",
            "default": None,
            "help": "Draw vertical line(s) at specified x value(s)",
        },
    },
    "vertical_label": {
        "flags": ["--vertical_label"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Label(s) for vertical line(s), one per line",
        },
    },
    "vertical_style": {
        "flags": ["--vertical_style"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Linestyle(s) for vertical line(s) (e.g. -- : -. -), one per line",
        },
    },
    "vertical_color": {
        "flags": ["--vertical_color"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Color(s) for vertical line(s) (e.g. gray red C0), one per line",
        },
    },
    "xtick": {
        "flags": ["--xtick"],
        "kwargs": {
            "type": float,
            "nargs": "+",
            "default": None,
            "help": "X-axis position(s) at which to place a custom tick label",
        },
    },
    "xtick_label": {
        "flags": ["--xtick_label"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Label(s) for custom x-axis tick(s), one per --xtick value",
        },
    },
    "xtick_height": {
        "flags": ["--xtick_height"],
        "kwargs": {
            "type": float,
            "default": None,
            "help": "How far (axes fraction) custom x-tick labels sit below the axis; "
            "raise/lower to fit them in the space before the fixed-position x-axis title",
        },
    },
    "ytick": {
        "flags": ["--ytick"],
        "kwargs": {
            "type": float,
            "nargs": "+",
            "default": None,
            "help": "Y-axis position(s) at which to place a custom tick label",
        },
    },
    "ytick_label": {
        "flags": ["--ytick_label"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Label(s) for custom y-axis tick(s), one per --ytick value",
        },
    },
    "ytick_height": {
        "flags": ["--ytick_height"],
        "kwargs": {
            "type": float,
            "default": None,
            "help": "How far (axes fraction) custom y-tick labels sit left of the axis; "
            "raise/lower to fit them in the space before the fixed-position y-axis title",
        },
    },
    "square": {
        "flags": ["--square"],
        "kwargs": {
            "nargs": "+",
            "type": float,
            "action": "append",
            "default": None,
            "metavar": "SQUARE",
            "help": "Draw rectangle(s) as float values grouped into x1 y1 x2 y2 (opposite corners); supports 4, 8, 12... values",
        },
    },
    "square_label": {
        "flags": ["--square_label"],
        "kwargs": {
            "nargs": "+",
            "type": str,
            "default": None,
            "help": "Label(s) for square(s); one label per square",
        },
    },
    "square_style": {
        "flags": ["--square_style"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Linestyle(s) for square edge(s) (e.g. -- : -. -), one per square",
        },
    },
    "square_color": {
        "flags": ["--square_color"],
        "kwargs": {
            "type": str,
            "nargs": "+",
            "default": None,
            "help": "Color(s) for square edge(s) (e.g. gray red C0), one per square",
        },
    },
    "point": {
        "flags": ["--point"],
        "kwargs": {
            "nargs": "+",
            "type": float,
            "action": "append",
            "default": None,
            "metavar": "POINT",
            "help": "Draw point(s) as float values grouped into x y pairs; supports 2, 4, 6... values",
        },
    },
    "point_label": {
        "flags": ["--point_label"],
        "kwargs": {
            "nargs": "+",
            "type": str,
            "default": None,
            "help": "Point label(s); provide one label per point",
        },
    },
    "plot_style": {
        "flags": ["--plot_style", "--line_plot_style"],
        "kwargs": {
            "dest": "plot_style",
            "type": str,
            "default": "-",
            "help": "Plot line style",
        },
    },
    "plot_type": {
        "flags": ["--plot_type"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Plot type override",
        },
    },
    "title": {
        "flags": ["--title"],
        "kwargs": {
            "type": parse_plot_label,
            "default": None,
            "help": "Title for the plot. Pass None to suppress the title entirely.",
        },
    },
    "output": {
        "flags": ["--output", "-o"],
        "kwargs": {
            "nargs": "+",
            "type": str,
            "default": None,
            "help": "Output filepath",
        },
    },
    "subfolder": {
        "flags": ["--subfolder"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Save the plot inside this subfolder of the output path(s)",
        },
    },
    "debug": {
        "flags": ["--debug", "-d"],
        "kwargs": {
            "action": "store_true",
            "help": "Enable debug mode",
        },
    },
    "note": {
        "flags": ["--note"],
        "kwargs": {
            "type": str,
            "default": None,
            "help": "Text annotation to add to the plot (positioned automatically in best location)",
        },
    },
}


def add_common_args(parser, arg_names, overrides=None):
    overrides = overrides or {}

    for arg_name in arg_names:
        if arg_name not in COMMON_ARG_SPECS:
            raise KeyError(f"Unknown common arg '{arg_name}'")

        base = COMMON_ARG_SPECS[arg_name]
        flags = list(base["flags"])
        kwargs = copy.deepcopy(base["kwargs"])

        override = copy.deepcopy(overrides.get(arg_name, {}))
        if "flags" in override:
            flags = list(override.pop("flags"))

        kwargs.update(override)
        parser.add_argument(*flags, **kwargs)

    if "--capitalize_legend" not in parser._option_string_actions:
        parser.add_argument(
            "--capitalize_legend",
            action="store_true",
            default=False,
            help="Capitalize the first letter of each word in legend entries",
        )


def load_computation_settings():
    """
    Load computation settings from config/computation_settings.json.

    Returns:
        dict: Configuration dictionary with keys like 'default_operation'
        or empty dict if file doesn't exist.
    """
    config_file = os.path.join("config", "computation_settings.json")
    if not os.path.isfile(config_file):
        return {}

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, IOError):
        return {}


_MISSING_ITERABLE_MAPPING_WARNING_SHOWN = False
_MISSING_MAPPING_WARNINGS_SHOWN = set()


def map_iterable_label(iterable_value, iterable_name, mapping_name=None, unique_iterables_count=None):
    """Map iterable values to display labels.

    Args:
        iterable_value: Value to map
        iterable_name: Name of iterable column (e.g., 'PDG', 'Plane')
        mapping_name: Optional custom mapping dict name
        unique_iterables_count: Count of unique values (for Plane conditional logic)

    Returns:
        str: Mapped label or string representation of value
    """
    global _MISSING_ITERABLE_MAPPING_WARNING_SHOWN
    _load_lib_imports()

    def _lookup(mapping_dict, value):
        if mapping_dict is None:
            return str(value)

        if value in mapping_dict:
            return str(mapping_dict[value])

        try:
            value_int = int(value)
            if value_int in mapping_dict:
                return str(mapping_dict[value_int])
        except (ValueError, TypeError):
            pass

        return str(value)

    if mapping_name is not None:
        mapping_dict = _get_mapping_dict(mapping_name)
        if mapping_dict is None:
            if not _MISSING_ITERABLE_MAPPING_WARNING_SHOWN:
                from rich import print as rprint
                rprint(
                    f"[yellow]Warning:[/yellow] Mapping '{mapping_name}' was not found or is not a dictionary. Falling back to default labeling."
                )
                _MISSING_ITERABLE_MAPPING_WARNING_SHOWN = True
            return str(iterable_value)
        return _lookup(mapping_dict, iterable_value)

    if iterable_name == "PDG":
        return _lookup(_particle_dict, iterable_value)

    if iterable_name == "Plane":
        if unique_iterables_count is not None and unique_iterables_count > 2:
            selected_mapping = _plane_dict
        else:
            selected_mapping = _simple_plane_dict
        return _lookup(selected_mapping, iterable_value)

    return str(iterable_value)


def map_label_key(value, mapping_name, key_type):
    """`map_iterable_label` with the (value, mapping_name, key_type) argument
    order used by script_compare_configuration.py's per-line Geometry/Config/Name
    label mapping (mapping_name and key_type swapped relative to
    map_iterable_label's own (iterable_value, iterable_name, mapping_name))."""
    return map_iterable_label(value, key_type, mapping_name)


def map_iterable_color(iterable_value, mapping_name):
    """Map iterable values to matplotlib colors.

    Args:
        iterable_value: Value to map
        mapping_name: Custom mapping dict name

    Returns:
        str or None: Color spec or None if not found
    """
    _load_lib_imports()

    if mapping_name is None:
        return None

    mapping_dict = _get_mapping_dict(mapping_name)
    if mapping_dict is None:
        return None

    if iterable_value in mapping_dict:
        return _resolve_mapped_color(mapping_dict[iterable_value])

    try:
        value_int = int(iterable_value)
        if value_int in mapping_dict:
            return _resolve_mapped_color(mapping_dict[value_int])
    except (ValueError, TypeError):
        pass

    return None


def _format_unit(unit):
    """Wrap unit in math-mode delimiters if it contains LaTeX commands."""
    if not unit:
        return unit
    if unit.startswith("$") and unit.endswith("$"):
        return unit
    if re.search(r"\\[a-zA-Z]+|[\^_]\{", unit):
        return f"${unit}$"
    return unit


def resolve_axis_label(explicit_label, col_name, df=None):
    """Return axis label with unit from a *Unit column appended when available.

    The unit is always appended to the base label (explicit or derived from col_name)
    unless the unit string already appears in parentheses in the label.
    Units containing LaTeX commands (e.g. \\sigma) are automatically wrapped in math mode.
    Pass --labelx None (or --labely None) to suppress the axis label entirely.
    """
    if explicit_label == "":
        return ""
    base = explicit_label if explicit_label is not None else (col_name or "")
    if df is not None and col_name is not None:
        unit_col = f"{col_name}Unit"
        if unit_col in df.columns:
            units = df[unit_col].dropna()
            if not units.empty:
                unit = str(units.iloc[0]).strip()
                if unit:
                    formatted = _format_unit(unit)
                    if f"({formatted})" not in base and f"({unit})" not in base:
                        return f"{base} ({formatted})"
    return base


def resolve_plot_kwargs(selected_plot_type):
    """Resolve plot type to plot_type and drawstyle kwargs.

    Args:
        selected_plot_type: Plot type string (e.g., 'step', 'plot', 'line')

    Returns:
        dict: Kwargs dict with plot_type and optional drawstyle
    """
    if selected_plot_type == "step":
        return {
            "plot_type": "plot",
            "drawstyle": "steps-mid",
        }
    return {
        "plot_type": selected_plot_type,
    }

