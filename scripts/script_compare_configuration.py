#!/usr/bin/env python3

"""
Script 5: Combined Line Plot with DUNE Style
Demonstrates combined data plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from lib import *
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_subtitle_from_args, make_title_from_args, make_config_label_from_args, make_config_color_and_style_from_args
from lib.functions import resolution, gaussian
from lib.imports import import_data, prepare_import
from lib.plot import apply_scientific_threshold_formatter, apply_legend_style, plot_data, create_common_subplots, apply_note_to_figure, draw_vertical_lines, draw_horizontal_lines
from lib.selection import prepare_selection, filter_dataframe
from common_args import add_common_args, map_iterable_label, map_iterable_color, resolve_axis_label


from rich import print as rprint

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
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
        "rangex",
        "rangey",
        "y",
        "plot_type",
        "logx",
        "logy",
        "labelx",
        "labely",
        "horizontal",
        "horizontal_label",
        "horizontal_style",
        "horizontal_color",
        "vertical",
        "vertical_label",
        "vertical_style",
        "vertical_color",
        "point",
        "point_label",
        "note",
        "title",
        "output",
        "debug",
    ],
    overrides={
        "configs": {
            "default": [
                "hd_1x2x6",
                "hd_1x2x6_lateralAPA",
                "hd_1x2x6_centralAPA",
                "vd_1x8x14_3view_30deg",
                "vd_1x8x14_3view_30deg_nominal",
            ]
        },
        "names": {"flags": ["--names"]},
        "x": {"default": "Values"},
        "plot_type": {"default": "step", "choices": ["scatter", "line", "step"], "help": "Style of errors."},
        "labelx": {"nargs": "+"},
        "output": {"help": "Output filepath for the plot"},
        "debug": {"flags": ["--debug"]},
    },
)

parser.add_argument(
    "--comparable",
    "-c",
    type=str,
    default="Config",
    help="List of comparable parameter to produce plots",
)

parser.add_argument(
    "--errory",
    action="store_true",
    help="Plot y-axis error bars",
    default=False,
)

parser.add_argument(
    "--errory_type",
    type=str,
    default="bars",
    help="Style of errors.",
    choices=["bars", "bands"],
)

parser.add_argument(
    "--operation",
    type=str,
    default=None,
    help="Operation to perform on data (e.g. mean, sum, etc.)",
)

parser.add_argument(
    "--align",
    type=str,
    default="mid",
    help="Alignment of histogram bars (e.g. mid, left, right)",
)

parser.add_argument(
    "--combine",
    type=str,
    default=None,
    help="Combine configurations by a key (e.g. Geometry)",
)

parser.add_argument(
    "--combine_operation",
    type=str,
    default="mean",
    choices=["mean", "sum"],
    help="Operation used when combining configurations (default: mean)",
)

parser.add_argument(
    "--mirror",
    type=str,
    default=None,
    help="Mirror histogram data around the final x value",
)

parser.add_argument(
    "--project",
    nargs="+",
    type=str,
    default=None,
    help="Project spectral data onto a different axis range",
)

parser.add_argument(
    "--project_offset",
    type=float,
    default=0,
    help="Offset to apply to x values when projecting",
)

parser.add_argument(
    "--project_scale",
    type=float,
    default=1,
    help="Scale factor to apply to y values when projecting",
)

parser.add_argument(
    "--iterable_mapping",
    type=str,
    default=None,
    help=(
        "Optional mapping dictionary name from plot_params mappings used to "
        "rename iterable values in legend labels"
    ),
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

# Styling options for the combined line
parser.add_argument(
    "--combined_color",
    type=str,
    default="C0",
    help="Color for the combined line (e.g. C0, red, #RRGGBB)",
)

parser.add_argument(
    "--combined_linestyle",
    type=str,
    default="-",
    help="Linestyle for the combined line (e.g. '-', '--', ':', '-.')",
)

parser.add_argument(
    "--combined_linewidth",
    type=float,
    default=None,
    help="Line width for the combined line (overrides default if set)",
)

parser.add_argument(
    "--combined_alpha",
    type=float,
    default=1.0,
    help="Alpha (transparency) for the combined line (0.0-1.0)",
)

parser.add_argument(
    "--combined_label",
    type=str,
    default="Combined",
    help="Legend label for the combined line",
)

args = parser.parse_args()

_MISSING_ITERABLE_MAPPING_WARNING_SHOWN = False
_MISSING_MAPPING_WARNINGS_SHOWN = set()
_MISSING_MAPPING_ENTRY_WARNINGS_SHOWN = set()


def _format_empty_result_context(args, configs, names):
    context_parts = []

    if getattr(args, "iterable", None) is not None:
        context_parts.append(f"iterable={args.iterable}")

    if getattr(args, "x", None) is not None and getattr(args, "y", None) is not None:
        context_parts.append(f"axes={args.x}/{args.y}")

    if configs:
        context_parts.append(f"configs={', '.join(map(str, configs))}")

    if names and any(name is not None for name in names):
        context_parts.append(f"names={', '.join(map(str, names))}")

    select = getattr(args, "select", None)
    save_values = getattr(args, "save_values", None)
    if select is not None and save_values is not None:
        selection_parts = []
        for save_key, save_value in zip(select, save_values):
            selection_parts.append(f"{save_key}={save_value}")
        if selection_parts:
            context_parts.append(f"select={'; '.join(selection_parts)}")

    return "; ".join(context_parts)

def _coerce_numeric_array(value):
    arr = np.asarray(value)
    if arr.ndim == 0:
        arr = np.asarray([arr.item()])
    return arr.astype(float)

def _find_fallback_x_array(row, x_key, y_key, target_len):
    for key, value in row.items():
        if key in {x_key, y_key}:
            continue
        try:
            candidate = _coerce_numeric_array(value)
        except (TypeError, ValueError):
            continue
        if candidate.size == target_len:
            return candidate
    return None

def _extract_xy_arrays(df_config, args):
    x_arrays = []
    y_arrays = []

    for _, row in df_config.iterrows():
        try:
            x = _coerce_numeric_array(row[args.x])
            y = _coerce_numeric_array(row[args.y])
        except (TypeError, ValueError, KeyError):
            continue

        if x.size == 1 and y.size > 1:
            fallback = _find_fallback_x_array(row, args.x, args.y, y.size)
            if fallback is not None:
                x = fallback
            else:
                x = np.full(y.shape, float(x[0]))
        elif y.size == 1 and x.size > 1:
            y = np.full(x.shape, float(y[0]))
        elif x.size != y.size:
            continue

        x_arrays.append(x)
        y_arrays.append(y)

    if not x_arrays:
        return None, None

    return np.concatenate(x_arrays), np.concatenate(y_arrays)

def _concat_numeric_cells(values):
    arrays = []
    for value in values:
        try:
            arrays.append(_coerce_numeric_array(value))
        except (TypeError, ValueError):
            continue
    if not arrays:
        return None
    return np.concatenate(arrays)


def _subset_for_config_name(subset, config, name):
    if name is None or "Name" not in subset.columns:
        return subset[(subset["Config"] == config)]

    return subset[(subset["Config"] == config) & (subset["Name"] == name)]


def _format_config_name_context(config, name):
    if name is None:
        return f"Config: {config}"
    return f"Config: {config}, Name: {name}"

def _build_geometry_combined_subset(subset, configs, names, args):
    combine_operation = getattr(args, "combine_operation", None) or "mean"
    grouped = {}

    for config, name in zip(configs, names):
        geom = str(config).split("_")[0]
        df_config = _subset_for_config_name(subset, config, name)
        if df_config.empty:
            continue

        x, y = _extract_xy_arrays(df_config, args)
        if x is None or y is None:
            continue

        if geom not in grouped:
            grouped[geom] = {
                "config": config,
                "name": name,
                "y_by_x": {},
            }

        for x_val, y_val in zip(x, y):
            x_key = float(x_val)
            grouped[geom]["y_by_x"].setdefault(x_key, []).append(float(y_val))

    rows = []
    combined_configs = []
    combined_names = []

    for geom, data in grouped.items():
        x_vals = np.array(sorted(data["y_by_x"].keys()), dtype=float)
        if combine_operation == "sum":
            y_vals = np.array(
                [np.sum(data["y_by_x"][xv]) for xv in x_vals], dtype=float
            )
        else:
            y_vals = np.array(
                [np.mean(data["y_by_x"][xv]) for xv in x_vals], dtype=float
            )

        rows.append(
            {
                "Config": data["config"],
                "Name": data["name"],
                args.x: x_vals,
                args.y: y_vals,
            }
        )
        combined_configs.append(data["config"])
        combined_names.append(data["name"])

    return pd.DataFrame(rows), combined_configs, combined_names

def main():
    """
    Main function to process simulation configurations, load data files,
    and generate plots based on the provided arguments.
    """
    df = import_data(args)
    plotted_geoms = set()

    # Check if the DataFrame is empty
    if df.empty:
        rprint("No data to plot. Exiting.")
        return

    ncols = len(args.variables) if args.variables is not None else 1
    fig, ax = create_common_subplots(
        nrows=1,
        ncols=ncols,
    )

    used_colors = []
    this_df = filter_dataframe(df, args)
    variables = args.variables if args.variables is not None else [None]
    iterables = this_df[args.iterable].unique() if args.iterable is not None else [None]

    for kdx, ((idx, variable), (jdx, iterable)) in enumerate(
        product(
            enumerate(variables),
            enumerate(iterables) if args.iterable is not None else enumerate([None]),
        )
    ):
        # Filter the DataFrame based on the current variable and iterable
        if args.debug:
            rprint(
                f"[blue]Info:[/blue] Processing variable: {variable}, iterable: {iterable}"
            )

        if ncols == 1:
            ax_current = ax
        else:
            ax_current = ax[idx if args.variables is not None else jdx]

        if variable is not None and iterable is not None:
            # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}")
            subset = this_df[
                (this_df["Variable"] == variable) & (this_df[args.iterable] == iterable)
            ]
        elif variable is not None and iterable is None:
            # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable}")
            subset = this_df[(this_df["Variable"] == variable)]
        elif iterable is not None and variable is None:
            # rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
            subset = this_df[(this_df[args.iterable] == iterable)]
        else:
            subset = this_df.copy()

        configs, names = prepare_import(args)
        configs = configs if configs is not None else [None]
        names = names if names is not None else [None]

        if getattr(args, "combine", None) == "Geometry":
            subset, configs, names = _build_geometry_combined_subset(
                subset, configs, names, args
            )

        single_loaded_file = len(configs) == 1 and len(names) == 1
        geoms = [str(geom).split("_")[0] if geom is not None else "" for geom in configs]
        two_line_mode = len(configs) == 2 and len(names) == 2
        plotted_geoms = set()

        combinedy = None
        combined_errory = None
        for ldx, (geom, config, name) in enumerate(zip(geoms, configs, names)):
            if args.debug:
                rprint(
                    f"[blue]Info:[/blue] Processing Geometry: {geom}, {_format_config_name_context(config, name)}"
                )
            df_config = _subset_for_config_name(subset, config, name)

            if df_config.empty:
                rprint(
                    f"[yellow]Warning:[/yellow] No data for {_format_config_name_context(config, name)}. Skipping..."
                )
                continue

            columns = []
            errory_sym = None
            if args.errory:
                if f"{args.y}Error" not in df_config.columns:
                    if (
                        f"{args.y}Error+" in df_config.columns
                        and f"{args.y}Error-" in df_config.columns
                    ):
                        if args.debug:
                            rprint(
                                f"[cyan]Info:[/cyan] Found upper and lower error values"
                            )

                        columns = [args.x, args.y, f"{args.y}Error+", f"{args.y}Error-"]
                        errory_sym = "asymmetric"
                else:
                    columns = [args.x, args.y, f"{args.y}Error"]
                    errory_sym = "symmetric"
            else:
                columns = [args.x, args.y]
                errory_sym = None

            # Handle multiple entries for the same configuration
            if len(df_config) > 1:
                rprint(
                    f"[cyan]Info:[/cyan] Multiple entries found for Config: {config}. Skipping explode..."
                )
                pass

            else:
                try:
                    df_config = df_config.explode(column=columns)
                except ValueError:
                    # Keep row as-is; downstream extraction handles mixed scalar/vector cells.
                    pass

            df_config = df_config.dropna(subset=columns)

            # Generate the label using the config naming structure function
            # Apply iterable mapping to the per-line keys (geometry/config/name).
            geom_label = make_config_label_from_args(args, config=config, name=name, iterable=None)

            if getattr(args, "combine", None) == "Geometry":
                geom_label = str(geom).upper()

            mapping_name = getattr(args, "iterable_mapping", None)
            if mapping_name is not None:
                mapped_geom = map_label_key(geom, mapping_name, "Geometry")
                mapped_config = map_label_key(config, mapping_name, "Config")
                mapped_name = map_label_key(name, mapping_name, "Name")

                geom_label = geom_label.replace(str(geom).upper(), str(mapped_geom))
                config_label = (
                    config_dict.get(config, str(config)) if config is not None else None
                )
                if config_label is not None:
                    # geom_label = geom_label.replace(str(config_label), str(mapped_config))
                    geom_label = str(mapped_config)
                if name is not None:
                    # geom_label = geom_label.replace(str(name), str(mapped_name))
                    geom_label += ", " + str(mapped_name)

            x, y = _extract_xy_arrays(df_config, args)
            if x is None or y is None:
                rprint(
                    f"[yellow]Warning:[/yellow] Could not parse x/y for Config: {config}, Name: {name}. Skipping..."
                )
                continue

            plotted_geoms.add(str(geom))

            if args.errory:
                if errory_sym == "asymmetric":
                    lower = _concat_numeric_cells(df_config[f"{args.y}Error-"].tolist())
                    upper = _concat_numeric_cells(df_config[f"{args.y}Error+"].tolist())
                    errory = [lower, upper] if lower is not None and upper is not None else None
                elif errory_sym == "symmetric":
                    errory = _concat_numeric_cells(df_config[f"{args.y}Error"].tolist())
                else:
                    errory = None
            else:
                errory = None

            mapping_name = getattr(args, "iterable_mapping", None)
            if mapping_name is not None:
                mapped_geom = map_label_key(geom, mapping_name, "Geometry")
                mapped_config = map_label_key(config, mapping_name, "Config")
                mapped_name = map_label_key(name, mapping_name, "Name")

                label_parts = [str(mapped_geom)]
                if mapped_config is not None and str(mapped_config) != str(mapped_geom):
                    label_parts.append(str(mapped_config))
                if mapped_name is not None and str(mapped_name) not in label_parts:
                    label_parts.append(str(mapped_name))

                geom_label = ", ".join(label_parts)
            else:
                geom_label = (
                    str(geom).upper()
                    if getattr(args, "combine", None) == "Geometry"
                    else make_config_label_from_args(
                        args, config=config, name=name, iterable=None
                    )
                )

            if args.operation is not None:
                if ldx == 0:
                    if args.operation == "squared_sum":
                        combinedy = np.power(y, 2)
                        combined_errory = (
                            np.power(errory, 2) if errory is not None else None
                        )
                    else:
                        combinedy = y
                        combined_errory = (
                            np.power(errory, 2) if errory is not None else None
                        )

                else:
                    if args.operation == "squared_sum":
                        combinedy = combinedy + np.power(y, 2)
                        # For independent errors: sqrt(e1^2 + e2^2)
                        if combined_errory is not None and errory is not None:
                            combined_errory = combined_errory + np.power(errory, 2)
                    else:
                        combinedy = np.add(combinedy, y)
                        if combined_errory is not None and errory is not None:
                            combined_errory = combined_errory + np.power(errory, 2)

                if args.project is not None and config in args.project:
                    # Interpolate the projected y values at the original x values to combine with the original y values
                    interpy = np.interp(
                        x,
                        (x * args.project_scale) + args.project_offset,
                        y,
                        left=0,
                    )
                    error_interpy = (
                        [
                            np.interp(
                                x,
                                (
                                    (x * args.project_scale) + args.project_offset
                                    if args.project_offset is not None
                                    and args.project_scale is not None
                                    else x
                                ),
                                (
                                    errory[i]
                                    if errory[i] is not None
                                    else np.zeros_like(x)
                                ),
                                left=0,
                                right=0,
                            )
                            for i in range(2)
                        ]
                        if errory is not None and errory_sym == "asymmetric"
                        else (
                            np.interp(
                                x,
                                (
                                    (x + args.project_offset) * args.project_scale
                                    if args.project_offset is not None
                                    and args.project_scale is not None
                                    else x
                                ),
                                errory if errory is not None else np.zeros_like(x),
                                left=0,
                                right=0,
                            )
                            if errory is not None and errory_sym == "symmetric"
                            else None
                        )
                    )

                    if args.operation == "squared_sum":
                        combinedy = combinedy + np.power(
                            interpy,
                            2,
                        )
                        if combined_errory is not None and errory is not None:
                            # For independent errors: sqrt(e1^2 + e2^2)
                            combined_errory = combined_errory + np.power(
                                error_interpy,
                                2,
                            )
                    else:
                        combinedy = np.add(
                            combinedy,
                            interpy,
                        )
                        if combined_errory is not None and errory is not None:
                            combined_errory = combined_errory + np.power(
                                error_interpy,
                                2,
                            )

            # Check that x and y have the same length
            if len(x) != len(y):
                rprint(
                    f"[red]Error:[/red] Length of x and y do not match for Config: {config}, Name: {name}. Skipping..."
                )
                continue

            x_bin = x[1] - x[0] if len(x) > 1 else 1
            # Check that all bins have the same width
            if len(x) > 2:
                x_bins = np.diff(x)
                if not np.allclose(x_bins, x_bin):
                    rprint(
                        f"[yellow]Warning:[/yellow] Bins have different widths for Config: {config}, Name: {name}."
                    )
                    # Compute suitable x_edges by extrapolating the first and last bins from the x and x_bins values
                    x_edges = np.concatenate(
                        [
                            [x[0] - x_bins[0] / 2],
                            x[:-1] + x_bins / 2,
                            [x[-1] + x_bins[-1] / 2],
                        ]
                    )

                else:
                    x_edges = np.linspace(
                        x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1
                    )
            else:
                rprint(f"[red]Error:[/red] Only found one x value. Skipping...")
                continue

            if config == args.mirror:
                # Mirror around the last bin without duplicating it at the join.
                # Skip x[-1] and y[-1] so the boundary bin appears once and the
                # reflected spectrum starts from y[-2] at (x[-1] + x_bin).
                x_mirror = x[:-1] + (x[-1] - x[0]) + x_bin
                y_mirror = y[-2::-1]
                x = np.concatenate((x, x_mirror))
                x_edges = np.linspace(x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1)
                y = np.concatenate((y, y_mirror))
                # rprint(f"[blue]Info:[/blue] Mirroring data for configuration: {config}")

            offset = 0
            if args.operation is not None:
                offset = 1

            if two_line_mode:
                this_color = f"C{ldx}"
                this_linestyle = "-"
            elif single_loaded_file:
                this_color = f"C{(kdx + offset) % 10}"
                this_linestyle = "-"
            else:
                this_color, base_linestyle = make_config_color_and_style_from_args(
                    args, config=config, name=name
                )
                if this_color is None:
                    this_color = f"C{(kdx + offset) % 10}"
                if base_linestyle is None:
                    base_linestyle = "-"
                this_linestyle = base_linestyle

                # Track the colors added to the plot. If colot already used, change linestyle to differentiate
                if this_color in used_colors and (
                    len(geoms) > 1 or len(args.configs) > 1 or len(args.names) > 2
                ):  # Only change linestyle if there are multiple geometries to compare
                    # Count and print how many times the color has been used before
                    count = used_colors.count(this_color)
                    if count == 1:
                        this_linestyle = "--"
                    elif count == 2:
                        this_linestyle = ":"
                    elif count == 3:
                        this_linestyle = "-."
                else:
                    this_linestyle = "-"

            used_colors.append(this_color)

            # If bins is not increasing monotonically
            if not np.all(np.diff(x_edges) > 0):
                rprint(
                    f"[yellow]Warning:[/yellow] x_edges are not increasing monotonically for Config: {config}, Name: {name}. Reversing data order..."
                )
                x = x[::-1]
                x_edges = x_edges[::-1]
                y = y[::-1]
                if args.errory and errory is not None:
                    errory = errory[::-1]

            if not np.all(np.diff(x_edges) > 0):
                # Fallback for duplicate/non-uniform x values: construct strictly increasing bin edges.
                unique_x = np.unique(np.sort(np.asarray(x, dtype=float)))
                if len(unique_x) == 1:
                    width = 1.0
                    x_edges = np.array(
                        [unique_x[0] - width / 2, unique_x[0] + width / 2],
                        dtype=float,
                    )
                else:
                    mids = 0.5 * (unique_x[:-1] + unique_x[1:])
                    first = unique_x[0] - 0.5 * (unique_x[1] - unique_x[0])
                    last = unique_x[-1] + 0.5 * (unique_x[-1] - unique_x[-2])
                    x_edges = np.concatenate(([first], mids, [last]))

            if args.project is not None and config in args.project:
                plot_data(
                    args,
                    ax_current,
                    x,
                    x_edges,
                    (
                        np.sqrt(y**2 + interpy**2)
                        if args.operation == "squared_sum"
                        else y + interpy
                    ),
                    errory,
                    errory_sym,
                    geom_label + " (Projected)" if idx == ncols - 1 else None,
                    this_color,
                    this_linestyle,
                )

            else:
                plot_data(
                    args,
                    ax_current,
                    x,
                    x_edges,
                    y,
                    errory,
                    errory_sym,
                    geom_label if idx == ncols - 1 else None,
                    this_color,
                    this_linestyle,
                )

        if args.operation is not None and combinedy is not None:
            if args.operation == "squared_sum":
                combinedy = np.power(combinedy, 0.5)

            # errors are accumulated as variances in both branches above
            combined_errory = (
                np.power(combined_errory, 0.5) if combined_errory is not None else None
            )

            # Use CLI-configurable styling for the combined line
            combined_label = (
                getattr(args, "combined_label", "Combined") if idx == ncols - 1 else None
            )
            combined_color = args.combined_color if getattr(args, "combined_color", None) is not None else "C0"
            combined_linestyle = args.combined_linestyle if getattr(args, "combined_linestyle", None) is not None else "-"
            combined_kwargs = {}
            if getattr(args, "combined_linewidth", None) is not None:
                combined_kwargs["linewidth"] = args.combined_linewidth
            if getattr(args, "combined_alpha", None) is not None:
                combined_kwargs["alpha"] = args.combined_alpha

            plot_data(
                args,
                ax_current,
                x,
                x_edges,
                combinedy,
                combined_errory,
                errory_sym,
                combined_label,
                combined_color,
                combined_linestyle,
                **combined_kwargs,
            )

        # Set titles and labels for the axes
        if ncols > 1:
            plot_subtitle = make_subtitle_from_args(args, idx)
            ax_current.set_title(plot_subtitle, fontsize=subtitlefontsize)

        ax_current.set_xlabel(
            args.labelx[idx]
            if args.labelx and len(args.labelx) == ncols
            else args.labelx[0] if args.labelx else resolve_axis_label(None, args.x, df)
        )
        if idx == 0:
            ax_current.set_ylabel(args.labely if args.labely else resolve_axis_label(None, args.y, df))

        # Set y-axis limits based on the y variable
        if args.rangex is not None:
            ax_current.set_xlim(args.rangex[0], args.rangex[1])

        if args.y == "Efficiency":
            ax_current.set_ylim(0, 110)
            ax_current.axhline(100, color="gray", linestyle="--", linewidth=1)

        elif args.y == "RMS":
            ax_current.set_ylim(0, 0.5)

        if args.rangey is not None:
            ax_current.set_ylim(args.rangey[0], args.rangey[1])

        apply_scientific_threshold_formatter(ax_current, threshold=0.1, axis="both")

        # Add horizontal line if specified
        draw_horizontal_lines(
            ax_current,
            getattr(args, "horizontal", None),
            labels=getattr(args, "horizontal_label", None),
            styles=getattr(args, "horizontal_style", None),
            colors=getattr(args, "horizontal_color", None),
            fontsize=linelabelfontsize,
        )
        draw_vertical_lines(
            ax_current,
            getattr(args, "vertical", None),
            labels=getattr(args, "vertical_label", None),
            styles=getattr(args, "vertical_style", None),
            colors=getattr(args, "vertical_color", None),
            fontsize=linelabelfontsize,
        )

        point_values = parse_point_pairs(getattr(args, "point", None))
        point_labels, point_label_warning = normalize_point_labels(
            getattr(args, "point_label", None), len(point_values)
        )
        if point_label_warning is not None:
            rprint(f"[yellow]Warning:[/yellow] {point_label_warning}")

        if point_values:
            for point_idx, (point_x, point_y) in enumerate(point_values):
                ax_current.scatter(point_x, point_y, color="gray", s=40, zorder=6)
                if point_labels is not None:
                        place_point_label(ax_current, point_x, point_y, point_labels[point_idx], fontsize=linelabelfontsize)

        # Set logarithmic scale if specified
        if args.logy:
            ax_current.set_yscale("log")
        if args.logx:
            ax_current.set_xscale("log")

        # Add legend for the last variable
        if idx == ncols - 1:
            apply_legend_style(
                ax_current,
                capitalize_labels=not getattr(args, "no_capitalize_legend", False),
            )

    # Set the figure title
    figure_title = make_title_from_args(args)
    fig.suptitle(figure_title, fontsize=titlefontsize)

    # dunestyle.WIP()

    apply_note_to_figure(fig, getattr(args, "note", None))

    if not plotted_geoms:
        empty_context = _format_empty_result_context(args, args.configs, args.names)
        if empty_context:
            rprint(
                f"[yellow]Warning:[/yellow] No data survived filtering. Active context: {empty_context}. Exiting without saving a plot."
            )
        else:
            rprint(
                "[yellow]Warning:[/yellow] No data survived filtering. Exiting without saving a plot."
            )
        return

    output_prefix = None if len(plotted_geoms) > 1 else next(iter(plotted_geoms))

    output_file = make_name_from_args(
        args,
        prefix=output_prefix,
        suffix="comparison.png",
    )
    default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
    save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)

if __name__ == "__main__":
    main()
