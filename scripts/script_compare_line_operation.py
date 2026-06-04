#!/usr/bin/env python3

"""
Script: Iterable line comparison with operation subplot
Combines iterable line scanning with a lower panel that shows operations
between lines (e.g. relative difference in percent).
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_legend_style, plot_data, create_common_subplots, create_common_two_panel_figure, apply_note_to_figure, place_vertical_label, place_horizontal_label, place_point_label
from common_args import add_common_args, load_computation_settings, map_iterable_label, map_iterable_color, resolve_plot_kwargs

import matplotlib.lines as mlines

parser = argparse.ArgumentParser(
    description="Compare iterable lines and plot a lower-panel operation",
)

add_common_args(
    parser,
    [
        "datafile",
        "configs",
        "names",
        "variables",
        "iterable",
        "select",
        "save_values",
        "x",
        "y",
        "reduce",
        "labelx",
        "labely",
        "labelz",
        "logx",
        "logy",
        "rangex",
        "rangey",
        "plot_style",
        "plot_type",
        "title",
        "output",
        "horizontal",
        "horizontal_label",
        "vertical",
        "vertical_label",
        "point",
        "point_label",
        "note",
        "debug",
    ],
    overrides={
        "datafile": {
            "required": True,
            "help": "Name of the input data file (pkl format)",
        },
        "names": {"flags": ["--names"]},
        "variables": {"help": "Optional list of variable filters"},
        "iterable": {"required": True, "help": "Iterable column to produce lines"},
        "select": {
            "help": "If provided, apply save_values filtering using these keys"
        },
        "save_values": {
            "help": "If select keys are provided, save only these matching values"
        },
        "x": {"required": True},
        "y": {"required": True},
        "labelx": {"default": "True Neutrino Energy (MeV)", "help": "Label for x-axis"},
        "labely": {"help": "Label for top subplot y-axis"},
        "labelz": {"help": "Legend title for iterable labels"},
        "rangey": {"help": "Range for top subplot y-axis (min max)"},
        "plot_style": {"help": "Line style (e.g. -, --, :, -.)"},
        "plot_type": {
            "default": "step",
            "choices": ["step", "plot", "line", "scatter", "errorbar"],
            "help": "Default plot type for top and bottom panels",
        },
    },
)

parser.add_argument(
    "--operation",
    type=str,
    default=None,
    choices=[
        "relative_difference",
        "absolute_relative_difference",
        "asymmetry",
        "subtract",
        "ratio",
        "add",
        "sum",
        "mean",
        "rms",
    ],
    help="Operation to show in the lower subplot",
)

parser.add_argument(
    "--default_operation",
    type=str,
    default=None,
    help="Default lower-panel behavior when --operation is not specified: operation name or dataframe column (overrides config default)",
)

parser.add_argument(
    "--lower_series_data",
    type=str,
    default=None,
    help=(
        "DataFrame column name to use for the lower-panel series. "
        "When provided, the lower panel will display these values directly."
    ),
)

parser.add_argument(
    "--reference",
    type=int,
    default=0,
    help="Reference line index for pairwise operations",
)

parser.add_argument(
    "--reference_value",
    type=str,
    default=None,
    help="Reference iterable value for pairwise operations (overrides --reference)",
)

parser.add_argument(
    "--bottom_labely",
    type=str,
    default=None,
    help="Label for lower subplot y-axis",
)

parser.add_argument(
    "--bottom_rangey",
    nargs=2,
    type=float,
    default=None,
    help="Range for lower subplot y-axis (min max)",
)

parser.add_argument(
    "--no_lower_plot",
    action="store_true",
    default=False,
    help="Disable rendering of the lower subplot",
)

parser.add_argument(
    "--stacked",
    action="store_true",
    default=False,
    help="Stack compatible top-panel series on top of each other",
)

parser.add_argument(
    "--stack_reverse",
    dest="stack_reverse_requested",
    action="store_true",
    default=None,
    help="Reverse stacked order so the first series is drawn on top",
)

parser.add_argument(
    "--no_stack_reverse",
    dest="stack_reverse_requested",
    action="store_false",
    help="Keep stacked order as plotted",
)

parser.add_argument(
    "--iterable_color_mapping",
    type=str,
    default=None,
    help=(
        "Optional mapping dictionary name from plot_params mappings used to "
        "set iterable line colors in legend/plot (supports Cn and rgb(r,g,b))"
    ),
)

parser.add_argument(
    "--comparable", '-c',
    type=str,
    default=None,
    help=(
        "DataFrame column to overlay as an additional line-shape dimension. "
        "Each unique value in this column gets a distinct linestyle; a separate "
        "black legend maps lineshape to value."
    ),
)

parser.add_argument(
    "--comparable_linestyles",
    nargs="+",
    type=str,
    default=None,
    help=(
        "Linestyle per comparable value in order (e.g. solid dashed dotted). "
        "Accepted values: solid/-, dashed/--, dotted/:, dashdot/-. "
        "Defaults to cycling through [-, --, :, -.]."
    ),
)

parser.add_argument(
    "--comparable_linewidths",
    nargs="+",
    type=float,
    default=None,
    help=(
        "Line width per comparable value in order (e.g. 1.0 3.0). "
        "Defaults to the global line width when omitted."
    ),
)

args = parser.parse_args()
args.stack_reverse = True if getattr(args, "stack_reverse_requested", None) is None else args.stack_reverse_requested

_COMPARABLE_LINESTYLES = ["-", "--", ":", "-."]

def _extract_line_arrays(subset, x_col, y_col):
    expanded = subset.explode(column=[x_col, y_col])
    if expanded.empty:
        return None, None

    try:
        x = expanded[x_col].astype(float).to_numpy()
        y = expanded[y_col].astype(float).to_numpy()
    except ValueError:
        return None, None

    mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[mask]
    y = y[mask]

    if x.size == 0 or y.size == 0:
        return None, None

    return x, y

def _extract_bottom_column_arrays(subset, x_col, bottom_col):
    expanded = subset.explode(column=[x_col, bottom_col])
    if expanded.empty:
        return None, None

    try:
        x = expanded[x_col].astype(float).to_numpy()
        y = expanded[bottom_col].astype(float).to_numpy()
    except ValueError:
        return None, None

    mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[mask]
    y = y[mask]

    if x.size == 0 or y.size == 0:
        return None, None

    return x, y

def _resolve_bottom_series_label(subset, bottom_col, fallback_label):
    label_col = f"{bottom_col}Label"

    if label_col not in subset.columns:
        return fallback_label

    label_values = subset[label_col].dropna()
    if label_values.empty:
        return fallback_label

    resolved_label = label_values.iloc[0]
    if resolved_label is None:
        return fallback_label

    return str(resolved_label)

def _stacked_plot_type(selected_plot_type, resolved_plot_kwargs):
    if selected_plot_type == "bar":
        return "bar"
    resolved_type = resolved_plot_kwargs.get("plot_type")
    return resolved_type if resolved_type is not None else selected_plot_type

def _resolve_stacked_bar_width(x_values):
    try:
        x_array = np.asarray(x_values, dtype=float)
    except (TypeError, ValueError):
        return 0.8

    if x_array.size <= 1:
        return 0.8

    sorted_unique = np.unique(np.sort(x_array))
    if sorted_unique.size <= 1:
        return 0.8

    diffs = np.diff(sorted_unique)
    positive_diffs = diffs[diffs > 0]
    if positive_diffs.size == 0:
        return 0.8

    return float(np.min(positive_diffs))

def _resolve_comparable_style(sdx, args):
    user_styles = getattr(args, "comparable_linestyles", None)
    user_widths = getattr(args, "comparable_linewidths", None)
    ls = (
        user_styles[sdx]
        if user_styles is not None and sdx < len(user_styles)
        else _COMPARABLE_LINESTYLES[sdx % len(_COMPARABLE_LINESTYLES)]
    )
    lw = (
        user_widths[sdx]
        if user_widths is not None and sdx < len(user_widths)
        else None
    )
    return ls, lw

def _compute_pairwise(reference, other, operation):
    if operation == "subtract":
        return other - reference
    if operation == "add":
        return other + reference
    if operation == "ratio":
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.divide(other, reference)
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "relative_difference":
        with np.errstate(divide="ignore", invalid="ignore"):
            result = 100.0 * np.divide(other - reference, reference)
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "absolute_relative_difference":
        with np.errstate(divide="ignore", invalid="ignore"):
            result = 100.0 * np.abs(np.divide(other - reference, reference))
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "asymmetry":
        with np.errstate(divide="ignore", invalid="ignore"):
            denominator = 0.5 * (reference + other)
            result = np.divide(reference - other, denominator)
        result[~np.isfinite(result)] = np.nan
        return result

    raise ValueError(f"Unsupported pairwise operation: {operation}")

def compute_bottom_series(labels, line_arrays, operation, reference_index=0):
    if len(labels) != len(line_arrays):
        raise ValueError("labels and line_arrays must have the same length")
    if len(line_arrays) == 0:
        return []

    op = operation.lower()

    if op in ["sum", "mean", "rms"]:
        stacked = np.vstack(line_arrays)
        if op == "sum":
            y_out = np.sum(stacked, axis=0)
            return [("sum", y_out)]
        if op == "mean":
            y_out = np.mean(stacked, axis=0)
            return [("mean", y_out)]
        y_out = np.sqrt(np.mean(stacked**2, axis=0))
        return [("rms", y_out)]

    if len(line_arrays) < 2:
        return []

    ref_idx = max(0, min(reference_index, len(line_arrays) - 1))
    ref_label = labels[ref_idx]
    ref_array = line_arrays[ref_idx]

    output = []
    for idx, (label, y_values) in enumerate(zip(labels, line_arrays)):
        if idx == ref_idx:
            continue
        y_out = _compute_pairwise(ref_array, y_values, op)
        if op == "subtract":
            out_label = f"{label} - {ref_label}"
        elif op == "add":
            out_label = f"{label} + {ref_label}"
        elif op == "ratio":
            out_label = f"{label}/{ref_label}"
        elif op == "relative_difference":
            out_label = f"({label} - {ref_label})/{ref_label} [%]"
        elif op == "absolute_relative_difference":
            out_label = f"|{label} - {ref_label}|/{ref_label} [%]"
        elif op == "asymmetry":
            out_label = f"({ref_label} - {label})/(0.5*({ref_label}+{label}))"
        else:
            out_label = f"{label} ({op})"
        output.append((out_label, y_out))

    return output

def _default_bottom_label(operation):
    labels = {
        "subtract": "Difference",
        "add": "Sum",
        "sum": "Sum",
        "mean": "Mean",
        "rms": "RMS",
        "ratio": "Ratio",
        "asymmetry": "Asymmetry",
        "relative_difference": "Relative Difference (%)",
        "absolute_relative_difference": "Absolute Relative Difference (%)",
    }
    return labels.get(operation, operation)

def _make_output_dir(output_arg):
    if output_arg is not None:
        paths = output_arg if isinstance(output_arg, list) else [output_arg]
        for path in paths:
            out_dir = os.path.dirname(path) or "."
            os.makedirs(out_dir, exist_ok=True)
        return os.path.dirname(paths[0]) or "."

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def main():
    allowed_operations = [
        "relative_difference",
        "absolute_relative_difference",
        "asymmetry",
        "subtract",
        "ratio",
        "add",
        "sum",
        "mean",
        "rms",
    ]

    # Load default operation from computation settings
    computation_settings = load_computation_settings()
    config_default_behavior = computation_settings.get("default_operation")

    operation = None
    bottom_column = None

    # If the user explicitly provided a dataframe column for the lower series,
    # use it and prefer it over any computed operation. Warn if both are set.
    if getattr(args, "lower_series_data", None):
        bottom_column = args.lower_series_data
        if args.operation is not None:
            rprint(
                "[yellow]Warning:[/yellow] Both --lower_series_data and --operation were provided;"
                " displaying --lower_series_data and ignoring --operation."
            )
    else:
        if args.operation is not None:
            operation = args.operation
        else:
            default_behavior = args.default_operation or config_default_behavior
            if default_behavior in allowed_operations:
                operation = default_behavior
            elif default_behavior is not None:
                bottom_column = default_behavior
            else:
                operation = "relative_difference"

    # If the default behavior named a column called 'Significance', allow the
    # user to override which dataframe column should be used by providing
    # --lower_series_data.
    if bottom_column is not None and str(bottom_column).lower() == "significance":
        if getattr(args, "lower_series_data", None):
            bottom_column = args.lower_series_data
    
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        if config is not None and name is None:
            df_config = df[(df["Config"] == config)]
        elif config is None and name is not None:
            df_config = df[(df["Name"] == name)]
        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]
        else:
            df_config = df.copy()

        if args.iterable not in df_config.columns:
            rprint(
                f"[red]Error:[/red] Iterable column '{args.iterable}' not found in dataframe."
            )
            continue

        df_config_all = df_config.copy()
        df_config = df_config[df_config[str(args.iterable)].notna()]
        iterable_values = df_config[args.iterable].unique()
        two_line_mode = iterable_values.size == 2

        if iterable_values.size == 0:
            rprint("[yellow]Warning:[/yellow] No iterable entries found after filtering.")
            continue

        render_lower_plot = not getattr(args, "no_lower_plot", False)
        if render_lower_plot:
            fig, gs = create_common_two_panel_figure(
                ncols=1,
                height_ratios=[3, 1],
            )
            ax_top = fig.add_subplot(gs[0])
            ax_bottom = fig.add_subplot(gs[1], sharex=ax_top)
            # Hide x-axis tick labels on the upper panel when a lower panel exists
            ax_top.tick_params(labelbottom=False)
        else:
            fig, ax_top = create_common_subplots(nrows=1, ncols=1)
            ax_bottom = None
        selected_plot_type = getattr(args, "plot_type", "step")
        plot_kwargs = resolve_plot_kwargs(selected_plot_type)

        # Comparable mode: overlay a second line-shape dimension from this column
        comparable_col = getattr(args, "comparable", None)
        comparable_values_arr = np.array([])
        if comparable_col is not None:
            if comparable_col not in df_config.columns:
                rprint(
                    f"[red]Error:[/red] Inspect column '{comparable_col}' not found in dataframe."
                )
                comparable_col = None
            else:
                comparable_values_arr = df_config[comparable_col].dropna().unique()

        stacked_requested = getattr(args, "stacked", False)
        stacked_enabled = stacked_requested and comparable_col is None
        if stacked_requested and comparable_col is not None:
            rprint(
                "[yellow]Warning:[/yellow] --stacked is not supported together with "
                f"--comparable={comparable_col}; ignoring --stacked."
            )

        stack_reverse_requested = getattr(args, "stack_reverse_requested", None)
        reverse_stacking = stacked_enabled and (
            stack_reverse_requested is None or stack_reverse_requested
        )
        if stack_reverse_requested is True and not stacked_enabled:
            rprint(
                "[yellow]Warning:[/yellow] --stack_reverse only applies when --stacked is active; ignoring --stack_reverse."
            )

        top_labels = []
        top_arrays = []
        bottom_arrays = []
        top_by_comparable = {}   # comparable_val -> ([labels], [arrays])
        bottom_by_comparable = {}  # comparable_val -> [(label, arr)]
        stacked_bottom = None
        stacked_bottom_by_comparable = {}
        x_reference = None
        stack_mode = "bar" if stacked_enabled else _stacked_plot_type(selected_plot_type, plot_kwargs)
        iterable_index_lookup = {value: idx for idx, value in enumerate(iterable_values.tolist())}
        iterable_order = iterable_values[::-1] if reverse_stacking else iterable_values

        for iterable in iterable_order:
            iterable_index = iterable_index_lookup[iterable]

            if iterable_values.size > 8 and args.reduce and iterable_index % 2 == 1:
                rprint(
                    f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding"
                )
                continue

            df_iterable = df_config[(df_config[args.iterable] == iterable)]
            label = map_iterable_label(iterable, args.iterable, unique_iterables_count=iterable_values.size)
            mapped_color = map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
            line_color = (
                f"C{iterable_index}"
                if two_line_mode or (comparable_col is not None and mapped_color is None)
                else mapped_color
            )

            if comparable_col is not None and comparable_values_arr.size > 0:
                for sdx, comparable_val in enumerate(comparable_values_arr):
                    df_comparable_sub = df_iterable[df_iterable[comparable_col] == comparable_val]
                    subset_comparable = filter_dataframe(df_comparable_sub, args)
                    if subset_comparable.empty:
                        continue

                    x_v, y_v = _extract_line_arrays(subset_comparable, args.x, args.y)
                    if x_v is None or y_v is None:
                        if args.debug:
                            rprint(
                                f"[yellow]Warning:[/yellow] Could not extract numeric arrays for iterable={iterable}, {comparable_col}={comparable_val}"
                            )
                        continue

                    if x_reference is None:
                        x_reference = x_v
                    elif x_v.size != x_reference.size or not np.allclose(
                        x_v, x_reference, equal_nan=True
                    ):
                        rprint(
                            f"[yellow]Warning:[/yellow] Skipping iterable={iterable}, {comparable_col}={comparable_val} because x-values are not aligned."
                        )
                        continue

                    comparable_ls, comparable_lw = _resolve_comparable_style(sdx, args)
                    comparable_style_kwargs = {"linewidth": comparable_lw} if comparable_lw is not None else {}
                    plot_bottom = None
                    plot_type_kwargs = dict(plot_kwargs)
                    if stacked_enabled:
                        plot_bottom = stacked_bottom_by_comparable.setdefault(
                            comparable_val,
                            np.zeros_like(y_v, dtype=float),
                        )
                        plot_type_kwargs = {
                            "plot_type": "bar",
                            "width": _resolve_stacked_bar_width(x_v),
                            "edgecolor": "none",
                            "linewidth": 0,
                        }
                    plot_data(
                        args,
                        ax_top,
                        x_v,
                        y=y_v,
                        label=label if sdx == 0 else None,
                        color=line_color,
                        **({"linestyle": comparable_ls} if not stacked_enabled else {}),
                        **comparable_style_kwargs,
                        **plot_type_kwargs,
                        **({"bottom": plot_bottom} if plot_bottom is not None else {}),
                    )

                    if plot_bottom is not None:
                        plot_bottom += y_v

                    comparable_entry = top_by_comparable.setdefault(comparable_val, ([], [], []))
                    comparable_entry[0].append(label)
                    comparable_entry[1].append(y_v)
                    comparable_entry[2].append(line_color)

                    if bottom_column is not None and bottom_column in subset_comparable.columns:
                        local_sub = subset_comparable[subset_comparable[bottom_column].notna()]
                        if not local_sub.empty:
                            x_b, y_b = _extract_bottom_column_arrays(
                                local_sub, args.x, bottom_column
                            )
                            if x_b is not None and y_b is not None:
                                if x_b.size == x_reference.size and np.allclose(
                                    x_b, x_reference, equal_nan=True
                                ):
                                    b_label = _resolve_bottom_series_label(
                                        local_sub, bottom_column, label
                                    )
                                    bottom_by_comparable.setdefault(comparable_val, []).append(
                                        (b_label, y_b, line_color)
                                    )
            else:
                subset = filter_dataframe(df_iterable, args)
                if subset.empty:
                    continue

                x_values, y_values = _extract_line_arrays(subset, args.x, args.y)
                if x_values is None or y_values is None:
                    if args.debug:
                        rprint(
                            f"[yellow]Warning:[/yellow] Could not extract numeric arrays for iterable={iterable}"
                        )
                    continue

                if x_reference is None:
                    x_reference = x_values
                elif x_values.size != x_reference.size or not np.allclose(
                    x_values, x_reference, equal_nan=True
                ):
                    rprint(
                        f"[yellow]Warning:[/yellow] Skipping iterable={iterable} because x-values are not aligned with the first line."
                    )
                    continue

                plot_type_kwargs = dict(plot_kwargs)
                if stacked_enabled:
                    stacked_bottom = (
                        np.zeros_like(y_values, dtype=float)
                        if stacked_bottom is None
                        else stacked_bottom
                    )
                    plot_type_kwargs = {
                        "plot_type": "bar",
                        "width": _resolve_stacked_bar_width(x_values),
                        "edgecolor": "none",
                        "linewidth": 0,
                    }

                plot_data(
                    args,
                    ax_top,
                    x_values,
                    y=y_values,
                    label=label,
                    color=line_color,
                    **plot_type_kwargs,
                    **({"bottom": stacked_bottom} if stacked_enabled else {}),
                )

                if stacked_enabled:
                    stacked_bottom += y_values

                top_labels.append(label)
                top_arrays.append(y_values)

                if bottom_column is not None:
                    if bottom_column not in subset.columns:
                        rprint(
                            f"[yellow]Warning:[/yellow] Bottom column '{bottom_column}' not found for iterable={iterable}."
                        )
                        continue

                    local_bottom_subset = subset[subset[bottom_column].notna()]

                    if local_bottom_subset.empty:
                        if args.debug:
                            rprint(
                                f"[yellow]Warning:[/yellow] No non-null values found for bottom column '{bottom_column}' for iterable={iterable}."
                            )
                        continue

                    x_bottom, y_bottom = _extract_bottom_column_arrays(
                        local_bottom_subset,
                        args.x,
                        bottom_column,
                    )
                    if x_bottom is None or y_bottom is None:
                        if args.debug:
                            rprint(
                                f"[yellow]Warning:[/yellow] Could not extract numeric bottom arrays for iterable={iterable}, column={bottom_column}"
                            )
                        continue

                    if x_bottom.size != x_reference.size or not np.allclose(
                        x_bottom, x_reference, equal_nan=True
                    ):
                        rprint(
                            f"[yellow]Warning:[/yellow] Skipping bottom column for iterable={iterable} because x-values are not aligned with the first line."
                        )
                        continue

                    bottom_label = _resolve_bottom_series_label(
                        local_bottom_subset,
                        bottom_column,
                        label,
                    )

                    bottom_arrays.append((bottom_label, y_bottom))

        has_lines = bool(top_by_comparable) if comparable_col is not None else len(top_arrays) > 0
        if not has_lines:
            rprint("[yellow]Warning:[/yellow] No valid lines available to plot.")
            plt.close(fig)
            continue

        bottom_series = []
        bottom_has_content = False
        if ax_bottom is not None:
            ref_index = args.reference
            if args.reference_value is not None:
                ref_labels = (
                    next(iter(top_by_comparable.values()))[0]
                    if comparable_col is not None and top_by_comparable
                    else top_labels
                )
                try:
                    ref_index = ref_labels.index(str(args.reference_value))
                except ValueError:
                    rprint(
                        f"[yellow]Warning:[/yellow] reference_value '{args.reference_value}' not found in plotted labels. Using reference index {args.reference}."
                    )

            if comparable_col is not None and top_by_comparable:
                for sdx, comparable_val in enumerate(comparable_values_arr):
                    if comparable_val not in top_by_comparable:
                        continue
                    comparable_ls, comparable_lw = _resolve_comparable_style(sdx, args)
                    comparable_style_kwargs = {"linewidth": comparable_lw} if comparable_lw is not None else {}

                    if bottom_column is not None:
                        bottom_s_raw = bottom_by_comparable.get(comparable_val, [])
                        bottom_s = [(lbl, vals) for lbl, vals, _c in bottom_s_raw]
                        bottom_colors = [c for _lbl, _vals, c in bottom_s_raw]
                        op_label = (
                            args.bottom_labely if args.bottom_labely is not None else bottom_column
                        )
                    else:
                        labels_at, arrays_at, colors_at = top_by_comparable[comparable_val]
                        bottom_s = compute_bottom_series(
                            labels_at, arrays_at, operation, reference_index=ref_index
                        )
                        op_label = (
                            args.bottom_labely
                            if args.bottom_labely is not None
                            else _default_bottom_label(operation or "")
                        )
                        if operation in {"sum", "mean", "rms"}:
                            bottom_colors = [None] * len(bottom_s)
                        else:
                            clamped_ref = max(0, min(ref_index, len(colors_at) - 1))
                            bottom_colors = [
                                colors_at[i]
                                for i in range(len(colors_at))
                                if i != clamped_ref
                            ]

                    for idx, (_label, values) in enumerate(bottom_s):
                        plot_data(
                            args,
                            ax_bottom,
                            x_reference,
                            y=values,
                            label=(op_label if idx == 0 and sdx == 0 else None),
                            color=bottom_colors[idx] if idx < len(bottom_colors) else None,
                            linestyle=comparable_ls,
                            **comparable_style_kwargs,
                            **plot_kwargs,
                        )
                        bottom_has_content = True
                    bottom_series = bottom_s

                operation_label = (
                    args.bottom_labely
                    if args.bottom_labely is not None
                    else (
                        bottom_column
                        if bottom_column is not None
                        else _default_bottom_label(operation or "")
                    )
                )
            else:
                if bottom_column is not None:
                    bottom_series = bottom_arrays
                    operation_label = (
                        args.bottom_labely if args.bottom_labely is not None else bottom_column
                    )
                else:
                    bottom_series = compute_bottom_series(
                        top_labels,
                        top_arrays,
                        operation,
                        reference_index=ref_index,
                    )

                    operation_label = (
                        args.bottom_labely
                        if args.bottom_labely is not None
                        else _default_bottom_label(operation)
                    )

                for idx, (_label, values) in enumerate(bottom_series):
                    plot_data(
                        args,
                        ax_bottom,
                        x_reference,
                        y=values,
                        label=(operation_label if idx == 0 else None),
                        linestyle=args.plot_style,
                        **plot_kwargs,
                    )
                bottom_has_content = bool(bottom_series)

            ax_bottom.axhline(y=0, color="r", zorder=-1)

        ax_top.set_ylabel(
            args.labely if args.labely is not None else f"{args.y}",
            fontsize=ysublabelfontsize,
        )
        if ax_bottom is not None:
            bottom_ylabel = (
                args.bottom_labely
                if args.bottom_labely is not None
                else (bottom_column if bottom_column is not None else _default_bottom_label(operation or ""))
            )
            ax_bottom.set_ylabel(
                str(bottom_ylabel),
                fontsize=ysublabelfontsize,
            )
            ax_bottom.set_xlabel(
                args.labelx if args.labelx is not None else f"{args.x}",
                fontsize=xlabelfontsize,
            )
        else:
            ax_top.set_xlabel(
                args.labelx if args.labelx is not None else f"{args.x}",
                fontsize=xlabelfontsize,
            )

        if args.rangex is not None:
            ax_top.set_xlim(args.rangex)
            if ax_bottom is not None:
                ax_bottom.set_xlim(args.rangex)
        if args.rangey is not None:
            ax_top.set_ylim(args.rangey)
        if ax_bottom is not None and args.bottom_rangey is not None:
            ax_bottom.set_ylim(args.bottom_rangey)

        if args.logy:
            ax_top.set_yscale("log")
        if args.logx:
            ax_top.set_xscale("log")
            if ax_bottom is not None:
                ax_bottom.set_xscale("log")

        leg1 = apply_legend_style(
            ax_top,
            title=args.labelz if args.labelz is not None else args.iterable,
            capitalize_labels=not getattr(args, "no_capitalize_legend", False),
        )
        if comparable_col is not None and comparable_values_arr.size > 0:
            ax_top.add_artist(leg1)
            comparable_handles = [
                mlines.Line2D(
                    [],
                    [],
                    color="black",
                    linestyle=_resolve_comparable_style(sdx, args)[0],
                    linewidth=_resolve_comparable_style(sdx, args)[1],
                    label=str(val),
                )
                for sdx, val in enumerate(comparable_values_arr)
            ]
            apply_legend_style(
                ax_top,
                handles=comparable_handles,
                labels=[str(v) for v in comparable_values_arr],
                title=comparable_col,
                capitalize_labels=False,
                loc="lower right",
            )
        if ax_bottom is not None and bottom_has_content:
            apply_legend_style(
                ax_bottom,
                capitalize_labels=not getattr(args, "no_capitalize_legend", False),
            )

        vertical = getattr(args, "vertical", None)
        vertical_label = getattr(args, "vertical_label", None)
        horizontal = getattr(args, "horizontal", None)
        horizontal_label = getattr(args, "horizontal_label", None)

        if vertical is not None:
            ax_top.axvline(vertical, color="gray", linestyle="--", linewidth=1)
            if ax_bottom is not None:
                ax_bottom.axvline(vertical, color="gray", linestyle="--", linewidth=1)
            if vertical_label is not None:
                place_vertical_label(ax_top, vertical, vertical_label, fontsize=linelabelfontsize)

        if horizontal is not None:
            ax_top.axhline(horizontal, color="gray", linestyle="--", linewidth=1)
            if horizontal_label is not None:
                place_horizontal_label(ax_top, horizontal, horizontal_label, fontsize=linelabelfontsize)

        point_values = parse_point_pairs(getattr(args, "point", None))
        point_labels, point_label_warning = normalize_point_labels(
            getattr(args, "point_label", None), len(point_values)
        )
        if point_label_warning is not None:
            rprint(f"[yellow]Warning:[/yellow] {point_label_warning}")

        if point_values:
            for point_idx, (point_x, point_y) in enumerate(point_values):
                ax_top.scatter(point_x, point_y, color="gray", s=40, zorder=6)
                if point_labels is not None:
                    place_point_label(ax_top, point_x, point_y, point_labels[point_idx], fontsize=linelabelfontsize)

        figure_title = make_title_from_args(args)
        fig.suptitle(figure_title, fontsize=titlefontsize)

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_suffix = (
            "stacked_line_operation.png"
            if getattr(args, "stacked", False)
            else "line_operation.png"
        )
        output_file = make_name_from_args(
            args,
            kdx,
            prefix=None,
            suffix=output_suffix,
        )
        output_dir = _make_output_dir(args.output)
        default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)

if __name__ == "__main__":
    main()
