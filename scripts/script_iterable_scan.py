#!/usr/bin/env python3

"""
Script 1: Simple Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_subtitle_from_args
from lib.imports import import_data, prepare_import
from lib.functions import resolution
import matplotlib.lines as mlines
import math

from lib.plot import (
    apply_legend_style,
    plot_data,
    create_common_subplots,
    apply_note_to_figure,
    add_centered_suptitle,
    draw_vertical_lines,
    draw_horizontal_lines,
    place_point_label,
)
from common_args import add_common_args, map_iterable_label, map_iterable_color, resolve_axis_label


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
        "subfolder",
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
        "debug",
    ],
    overrides={
        "datafile": {
            "required": True,
            "help": "Name of the input data file (pkl format)",
        },
        "names": {"flags": ["--names"]},
        "iterable": {"required": True},
        "select": {
            "help": "If provided, use these key to apply save_values filtering"
        },
        "save_values": {
            "help": "If select key is provided, save plots for which select key equals this value"
        },
        "x": {"required": True},
        "y": {"required": True},
        "plot_style": {
            "help": "Plot line style for connected plots (options: -, --, :, -., solid, dashed, dotted, dashdot, none)",
        },
        "plot_type": {
            "choices": ["scatter", "line", "bar", "barh", "step", "plot", "errorbar"],
            "help": "Explicit plot type override (scatter, line, bar, barh, step, plot, errorbar)",
        },
    },
)

parser.add_argument(
    "--errorx",
    action="store_true",
    help="Include error bars on x-axis",
    default=False,
)

parser.add_argument(
    "--stacked",
    action="store_true",
    help="Create stacked histograms",
    default=False,
)

parser.add_argument(
    "--comparable",
    "-c",
    type=str,
    default=None,
    help=(
        "Optional DataFrame column to overlay as a secondary line dimension. "
        "Each unique value in this column gets a distinct linestyle."
    ),
)

parser.add_argument(
    "--comparable_linestyles",
    nargs="+",
    type=str,
    default=None,
    help=(
        "Linestyles to cycle through for comparable values (e.g. solid dashed dotted). "
        "Defaults to cycling through [-, --, :, -.]."
    ),
)

parser.add_argument(
    "--connect",
    action="store_true",
    help="(Deprecated) Connect data points with lines; use `--plot_type line` instead",
    default=False,
)

parser.add_argument(
    "--extrapolate",
    action="store_true",
    help="Show extrapolated data (marked by an '{y}Extrapolated' column) as a dashed continuation of the line",
    default=False,
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

args = parser.parse_args()

_MISSING_ITERABLE_MAPPING_WARNING_SHOWN = False

_COMPARABLE_LINESTYLES = ["-", "--", ":", "-."]

_EXTRAPOLATED_LINESTYLE = "--"


def _build_extrapolated_segments(x, y, extrapolated_mask):
    """Return (x_norm, y_norm, x_ext, y_ext) where x_ext/y_ext is ready to plot
    as a single call with NaN breaks between disconnected extrapolated groups.
    Each group is padded with the adjacent non-extrapolated point on both sides
    so the dashed segment visually touches the solid segment.
    """
    x_norm = x[~extrapolated_mask]
    y_norm = y[~extrapolated_mask]

    ext_indices = np.where(extrapolated_mask)[0]
    breaks = np.where(np.diff(ext_indices) > 1)[0] + 1
    groups = np.split(ext_indices, breaks)

    parts_x, parts_y = [], []
    for grp in groups:
        xi = list(x[grp])
        yi = list(y[grp])
        # prepend last adjacent normal point
        i0 = grp[0]
        if i0 > 0 and not extrapolated_mask[i0 - 1]:
            xi = [x[i0 - 1]] + xi
            yi = [y[i0 - 1]] + yi
        # append first adjacent normal point
        i1 = grp[-1]
        if i1 + 1 < len(x) and not extrapolated_mask[i1 + 1]:
            xi = xi + [x[i1 + 1]]
            yi = yi + [y[i1 + 1]]
        parts_x.append(np.array(xi))
        parts_y.append(np.array(yi))

    nan_sep = np.array([np.nan])
    x_ext = np.concatenate([v for p in parts_x for v in (p, nan_sep)][:-1]) if parts_x else np.array([])
    y_ext = np.concatenate([v for p in parts_y for v in (p, nan_sep)][:-1]) if parts_y else np.array([])

    return x_norm, y_norm, x_ext, y_ext


def _resolve_comparable_linestyle(index, args):
    user_styles = getattr(args, "comparable_linestyles", None)
    if user_styles:
        return user_styles[index % len(user_styles)]
    return _COMPARABLE_LINESTYLES[index % len(_COMPARABLE_LINESTYLES)]

def main():
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    if args.iterable not in df.columns:
        available_columns = ", ".join(map(str, df.columns.tolist()))
        rprint(
            f"[red]Error:[/red] Iterable column '{args.iterable}' was not found in the imported data. Available columns: {available_columns}"
        )
        return

    # Select the entries in the dataframe with with name matching args.names and nake a plot for each iterable
    if args.variables is None:
        n_vars, nrows, ncols = 1, 1, 1
    else:
        n_vars = len(args.variables)
        if n_vars <= 3:
            nrows, ncols = 1, n_vars
        else:
            ncols = math.ceil(math.sqrt(n_vars))
            nrows = math.ceil(n_vars / ncols)

    rprint(f"Number of unique variables for plotting: {n_vars} ({nrows}x{ncols} grid)")

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = create_common_subplots(
            nrows=nrows,
            ncols=ncols,
        )
        ax_flat = np.asarray(ax).flatten()

        if config is not None and name is None:
            df_config = df[(df["Config"] == config)]

        elif config is None and name is not None:
            df_config = df[(df["Name"] == name)]

        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]

        else:
            df_config = df.copy()

        rprint(
            f"Dataframe entries for this config and iterable: {len(df_config)}, Unique iterable values: {df_config[args.iterable].unique()}"
        )
        bottom = None
        variables = args.variables if args.variables is not None else [None]
        last_x = np.array([])
        axes_with_extrapolated = {}  # ax -> [(iterable_label, color), ...]
        # Drop None values from df in iterable column
        iterable_column = str(args.iterable)
        df_config = df_config[df_config[iterable_column].notna()]
        iterable_values = df_config[args.iterable].unique()
        two_line_mode = iterable_values.size == 2

        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables), enumerate(iterable_values)
        ):
            if iterable_values.size > 8 and args.reduce:
                if jdx % 2 == 1:
                    rprint(
                        f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding"
                    )
                    continue

            ax_current = ax_flat[idx]

            if variable is not None and iterable is None:
                if args.debug:
                    rprint(f"[blue]Info:[/blue] Filtering for variable: {variable}")
                df_iterable = df_config[(df_config["Variable"] == variable)]

            elif iterable is not None and variable is None:
                if args.debug:
                    rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
                df_iterable = df_config[(df_config[args.iterable] == iterable)]

            elif variable is not None and iterable is not None:
                if args.debug:
                    rprint(
                        f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}"
                    )
                df_iterable = df_config[
                    (df_config["Variable"] == variable)
                    & (df_config[args.iterable] == iterable)
                ]
            else:
                df_iterable = df_config.copy()

            comparable_col = getattr(args, "comparable", None)
            comparable_mode = False
            comparable_values = np.array([])
            if comparable_col is not None:
                if comparable_col not in df_iterable.columns:
                    if args.debug:
                        rprint(
                            f"[yellow]Warning:[/yellow] Comparable column '{comparable_col}' not found. Falling back to a single line."
                        )
                else:
                    comparable_values = df_iterable[comparable_col].dropna().unique()
                    comparable_mode = comparable_values.size > 0

            if comparable_mode:
                for sdx, comparable_value in enumerate(comparable_values):
                    df_iterable_comparable = df_iterable[
                        df_iterable[comparable_col] == comparable_value
                    ]

                    if args.debug:
                        rprint(
                            f"[blue]Info:[/blue] Filtering for comparable: {comparable_col}={comparable_value}"
                        )

                    subset = filter_dataframe(df_iterable_comparable, args)

                    subset = subset.explode(
                        column=(
                            [args.x, args.y, "Error"]
                            if "Error" in subset.columns
                            else [args.x, args.y]
                        )
                    )
                    if subset.empty:
                        rprint(
                            f"[yellow]Warning:[/yellow] No data for iterable {args.iterable}={iterable}, {comparable_col}={comparable_value}, Variable={variable}. Skipping."
                        )
                        continue

                    extrap_col_name = f"{args.y}Extrapolated"
                    extrap_raw_c = subset[extrap_col_name].to_numpy() if extrap_col_name in subset.columns else None
                    y = subset[args.y].astype(float).to_numpy()
                    x_edges = None
                    x = np.array([])
                    extrapolated_mask = np.zeros(0, dtype=bool)
                    try:
                        x = subset[args.x].astype(float).to_numpy()
                        x_bin = x[1] - x[0] if len(x) > 1 else 1
                        x_edges = np.linspace(x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1)
                        x_error = (
                            subset[f"Error"].astype(float).to_numpy()
                            if f"Error" in subset.columns
                            else None
                        )
                        mask = ~np.isnan(x) & ~np.isnan(y)
                        x = x[mask]
                        y = y[mask]
                        x_edges = x_edges[np.append(mask, True) | np.append(True, mask)]
                        if x_error is not None:
                            x_error = x_error[mask]
                        extrapolated_mask = pd.array(extrap_raw_c[mask], dtype="boolean").fillna(False).astype(bool).__array__() if extrap_raw_c is not None else np.zeros(len(x), dtype=bool)

                    except ValueError:
                        x = subset[args.x].astype(str)
                        x_error = None
                        extrapolated_mask = np.zeros(len(x), dtype=bool)

                    if extrapolated_mask.any() and not args.extrapolate:
                        keep = ~extrapolated_mask
                        x = x[keep]
                        y = y[keep]
                        if isinstance(x_error, np.ndarray):
                            x_error = x_error[keep]
                        extrapolated_mask = np.zeros(len(x), dtype=bool)

                    last_x = x

                    if bottom is None:
                        bottom = np.zeros(len(x)) if args.stacked else None

                    iterable_label = map_iterable_label(
                        iterable,
                        args.iterable,
                        getattr(args, "iterable_mapping", None),
                        len(iterable_values),
                    )
                    comparable_label = str(comparable_value)
                    if len(comparable_values) > 1:
                        iterable_label = f"{iterable_label} ({comparable_col}={comparable_label})"

                    iterable_color = (
                        f"C{jdx}"
                        if two_line_mode
                        else map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
                    )
                    comparable_linestyle = _resolve_comparable_linestyle(sdx, args)

                    if args.plot_type is not None:
                        rprint(
                            f"\tPlotting {len(x)} points with explicit plot_type={args.plot_type} for {args.iterable}={iterable} ({comparable_col}={comparable_label}), Variable={variable}"
                        )

                        plot_label = iterable_label if idx == n_vars - 1 else None

                        if args.plot_type == "line":
                            if extrapolated_mask.any():
                                x_norm, y_norm, x_ext, y_ext = _build_extrapolated_segments(x, y, extrapolated_mask)
                                plot_data(args, ax_current, x_norm, y=y_norm, label=plot_label, color=iterable_color, plot_type="line", linestyle=comparable_linestyle)
                                plot_data(args, ax_current, x_ext, y=y_ext, label=None, color=iterable_color, plot_type="line", linestyle=_EXTRAPOLATED_LINESTYLE)
                                axes_with_extrapolated.setdefault(ax_current, []).append((iterable_label, iterable_color))
                            else:
                                plot_data(
                                    args,
                                    ax_current,
                                    x,
                                    y=y,
                                    errory=x_error,
                                    label=plot_label,
                                    color=iterable_color,
                                    plot_type="line",
                                    linestyle=comparable_linestyle,
                                )
                        else:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                label=plot_label,
                                color=iterable_color,
                                plot_type=args.plot_type,
                                linestyle=comparable_linestyle,
                            )

                        continue

                    if x_error is not None and args.errorx:
                        rprint(
                            f"\tPlotting {len(x)} points with error bars for {args.iterable}={iterable_label}, Variable={variable}"
                        )
                        if args.stacked:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                errory=x_error,
                                label=iterable_label if idx == n_vars - 1 else None,
                                color=iterable_color,
                                plot_type="bar",
                                bottom=bottom,
                            )
                            bottom += y
                        else:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                errory=x_error,
                                label=iterable_label if idx == n_vars - 1 else None,
                                color=iterable_color,
                                plot_type="errorbar",
                                fmt="o",
                            )

                    else:
                        rprint(
                            f"\tPlotting {len(x)} points for {args.iterable}={iterable_label}, Variable={variable}"
                        )
                        if args.stacked:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                label=iterable_label if idx == n_vars - 1 else None,
                                color=iterable_color,
                                plot_type="bar",
                                bottom=bottom,
                            )
                            bottom += y
                        else:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                label=iterable_label if idx == n_vars - 1 else None,
                                color=iterable_color,
                                plot_type="line",
                                linestyle=comparable_linestyle,
                            )

                continue

            subset = filter_dataframe(df_iterable, args)

            subset = subset.explode(
                column=(
                    [args.x, args.y, "Error"]
                    if "Error" in subset.columns
                    else [args.x, args.y]
                )
            )
            if subset.empty:
                rprint(
                    f"[yellow]Warning:[/yellow] No data for iterable {args.iterable}={iterable}, Variable={variable}. Skipping."
                )
                continue

            extrap_col_name = f"{args.y}Extrapolated"
            extrap_raw = subset[extrap_col_name].to_numpy() if extrap_col_name in subset.columns else None
            y = subset[args.y].astype(float).to_numpy()
            x_edges = None
            x = np.array([])
            extrapolated_mask = np.zeros(0, dtype=bool)
            try:
                x = subset[args.x].astype(float).to_numpy()
                x_bin = x[1] - x[0] if len(x) > 1 else 1
                x_edges = np.linspace(x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1)
                x_error = (
                    subset[f"Error"].astype(float).to_numpy()
                    if f"Error" in subset.columns
                    else None
                )
                mask = ~np.isnan(x) & ~np.isnan(y)
                # Remove indices in x, x_error and y where any of them is NaN
                x = x[mask]
                y = y[mask]
                x_edges = x_edges[
                    np.append(mask, True) | np.append(True, mask)
                ]  # Keep edges corresponding to valid x values
                if x_error is not None:
                    x_error = x_error[mask]
                extrapolated_mask = pd.array(extrap_raw[mask], dtype="boolean").fillna(False).astype(bool).__array__() if extrap_raw is not None else np.zeros(len(x), dtype=bool)

            except ValueError:
                x = subset[args.x].astype(str)
                x_error = None
                extrapolated_mask = np.zeros(len(x), dtype=bool)

            if extrapolated_mask.any() and not args.extrapolate:
                keep = ~extrapolated_mask
                x = x[keep]
                y = y[keep]
                if isinstance(x_error, np.ndarray):
                    x_error = x_error[keep]
                extrapolated_mask = np.zeros(len(x), dtype=bool)

            last_x = x

            if bottom is None:
                bottom = np.zeros(len(x)) if args.stacked else None

            iterable_label = map_iterable_label(
                iterable,
                args.iterable,
                getattr(args, "iterable_mapping", None),
                len(iterable_values),
            )
            iterable_color = (
                f"C{jdx}"
                if two_line_mode
                else map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
            )

            if args.plot_type is not None:
                rprint(
                    f"\tPlotting {len(x)} points with explicit plot_type={args.plot_type} for {args.iterable}={iterable} (legend={iterable_label}), Variable={variable}"
                )

                plot_label = iterable_label if idx == n_vars - 1 else None

                if args.plot_type == "bar":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="bar",
                        bottom=bottom if args.stacked else None,
                    )

                elif args.plot_type == "barh":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="barh",
                    )
                    if args.stacked:
                        bottom += y

                elif args.plot_type == "step":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        x_edges=x_edges,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="step",
                        linestyle=args.plot_style,
                    )

                elif args.plot_type == "errorbar":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        errory=x_error,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="errorbar",
                        fmt="o",
                        linestyle=args.plot_style,
                    )

                elif args.plot_type == "line":
                    if extrapolated_mask.any():
                        x_norm, y_norm, x_ext, y_ext = _build_extrapolated_segments(x, y, extrapolated_mask)
                        plot_data(args, ax_current, x_norm, y=y_norm, label=plot_label, color=iterable_color, plot_type="line", linestyle=args.plot_style)
                        plot_data(args, ax_current, x_ext, y=y_ext, label=None, color=iterable_color, plot_type="line", linestyle=_EXTRAPOLATED_LINESTYLE)
                        axes_with_extrapolated.setdefault(ax_current, []).append((iterable_label, iterable_color))
                    else:
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            label=plot_label,
                            color=iterable_color,
                            plot_type="line",
                            linestyle=args.plot_style,
                        )

                elif args.plot_type == "scatter":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="scatter",
                        fmt="o",
                    )

                else:
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="plot",
                        marker="o",
                        linestyle=args.plot_style,
                    )

                continue

            if x_error is not None and args.errorx:
                rprint(
                    f"\tPlotting {len(x)} points with error bars for {args.iterable}={iterable_label}, Variable={variable}"
                )
                if args.stacked:
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        errory=x_error,
                        label=iterable_label if idx == n_vars - 1 else None,
                        color=iterable_color,
                        plot_type="bar",
                        bottom=bottom,
                    )
                    bottom += y

                else:
                    if args.connect or getattr(args, 'plot_type', None) == 'line':
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            linestyle=args.plot_style,
                            color=iterable_color,
                            label=None,
                            plot_type="plot",
                        )
                    else:
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            errory=x_error,
                            label=iterable_label if idx == n_vars - 1 else None,
                            color=iterable_color,
                            plot_type="errorbar",
                            fmt="o",
                        )

            else:
                rprint(
                    f"\tPlotting {len(x)} points for {args.iterable}={iterable_label}, Variable={variable}"
                )
                if args.stacked:
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=iterable_label if idx == n_vars - 1 else None,
                        color=iterable_color,
                        plot_type="bar",
                        bottom=bottom,
                    )
                    bottom += y
                else:
                    if args.connect or getattr(args, 'plot_type', None) == 'line':
                        plot_data(
                            args,
                            ax_current,
                            x,
                            x_edges=x_edges,
                            y=y,
                            label=iterable_label if idx == n_vars - 1 else None,
                            color=iterable_color,
                            plot_type="step",
                            linestyle=args.plot_style,
                        )
                    else:
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            label=iterable_label if idx == n_vars - 1 else None,
                            color=iterable_color,
                            plot_type="plot",
                            marker="o",
                            linestyle="None",
                        )

        _has_rotated_xlabels = False
        _has_categorical_ylabels = False
        for idx, variable in enumerate(variables):
            ax_current = ax_flat[idx]

            if n_vars > 1:
                ax_current.set_title(
                    variable if variable is not None else "",
                    fontsize=subtitlefontsize,
                )

            # -x's values are the string/categorical ones, but which axis they're
            # actually drawn on depends on plot orientation: barh puts them on y
            # (category per horizontal bar), everything else puts them on x.
            _categorical_axis = "y" if args.plot_type == "barh" else "x"
            if args.plot_type == "barh":
                ax_current.set_xlabel(resolve_axis_label(args.labely, args.y, df))
            else:
                ax_current.set_xlabel(resolve_axis_label(args.labelx, args.x, df))
            _x_is_categorical = (
                (isinstance(last_x, np.ndarray) and last_x.dtype.kind in ('U', 'S', 'O'))
                or (isinstance(last_x, pd.Series) and not pd.api.types.is_numeric_dtype(last_x))
            )
            if _x_is_categorical:
                if _categorical_axis == "x":
                    ax_current.tick_params(axis='x', labelrotation=45)
                    _has_rotated_xlabels = True
                else:
                    # barh labels are already horizontal and don't need rotation,
                    # but long feature names still need extra left margin below.
                    _has_categorical_ylabels = True

            (
                ax_current.set_ylabel(
                    resolve_axis_label(args.labelx, args.x, df)
                    if args.plot_type == "barh"
                    else resolve_axis_label(args.labely, args.y, df)
                )
                if idx % ncols == 0
                else None
            )

            if args.y == "Efficiency" or args.labely == "Efficiency (%)":
                ax_current.set_ylim(0, 105)
                ax_current.axhline(100, color="gray", linestyle="--", linewidth=1)

            if args.rangex is not None:
                ax_current.set_xlim(args.rangex[0], args.rangex[1])
            if args.rangey is not None:
                ax_current.set_ylim(args.rangey[0], args.rangey[1])

            if args.logy:
                ax_current.semilogy()

            if args.logx:
                ax_current.semilogx()

            if iterable_values.size > 1:
                if args.stacked:
                    if idx == n_vars - 1:
                        apply_legend_style(
                            ax_current,
                            title=args.labelz if args.labelz is not None else args.iterable,
                            loc="upper left",
                            bbox_to_anchor=(0, 1),
                            capitalize_labels=getattr(args, "capitalize_legend", False),
                        )
                else:
                    if idx == n_vars - 1:
                        source_legend = apply_legend_style(
                            ax_current,
                            title=args.labelz if args.labelz is not None else args.iterable,
                            capitalize_labels=getattr(args, "capitalize_legend", False),
                        )
                        if ax_current in axes_with_extrapolated:
                            existing = ax_current.get_legend()
                            if existing is not None:
                                handles = list(existing.legend_handles)
                                labels = [t.get_text() for t in existing.get_texts()]
                                for lbl, color in axes_with_extrapolated[ax_current]:
                                    proxy = mlines.Line2D([], [], color=color, linestyle=_EXTRAPOLATED_LINESTYLE, linewidth=1)
                                    handles.append(proxy)
                                    labels.append(f"{lbl} Extrapolated")
                                apply_legend_style(
                                    ax_current,
                                    title=args.labelz if args.labelz is not None else args.iterable,
                                    handles=handles,
                                    labels=labels,
                                    capitalize_labels=getattr(args, "capitalize_legend", False),
                                )

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

        # Hide any unused panels in a grid that isn't fully filled.
        for _i in range(n_vars, nrows * ncols):
            ax_flat[_i].set_visible(False)

        # Materialise tick-label Text objects so ha can be set before layout.
        if _has_rotated_xlabels:
            fig.canvas.draw()
            for _ax in fig.get_axes():
                plt.setp(_ax.get_xticklabels(), ha='right')

        plot_title = make_title_from_args(args)

        if nrows > 1:
            # For multi-row grids let tight_layout compute hspace (inter-row
            # spacing) and the top margin so that panel titles, x-axis labels
            # and the suptitle never overlap. When a suptitle is present reserve
            # 5 % of figure height for it; otherwise use the full height.
            _tl_rect = [0, 0, 1, 0.95] if plot_title else [0, 0, 1, 1.0]
            try:
                fig.tight_layout(rect=_tl_rect)
            except Exception:
                pass
        elif _has_rotated_xlabels or _has_categorical_ylabels:
            # For single-row plots with rotated x labels or long barh category
            # labels, grow the figure downward/leftward to accommodate them
            # without compressing the axes area.
            _sp = fig.subplotpars
            _left, _right, _bottom, _top = _sp.left, _sp.right, _sp.bottom, _sp.top
            old_h = fig.get_figheight()
            old_w = fig.get_figwidth()
            tl_bottom, tl_left = _bottom, _left
            try:
                fig.tight_layout()
                tl_bottom = fig.subplotpars.bottom
                tl_left = fig.subplotpars.left
            except Exception:
                pass
            fig.subplots_adjust(left=_left, right=_right, bottom=_bottom, top=_top)

            if _has_rotated_xlabels:
                extra_in = max(0.0, (tl_bottom - _bottom) * old_h) + 0.1
                if extra_in > 0.1:
                    new_h = old_h + extra_in
                    fig.set_figheight(new_h)
                    top_margin_in = (1.0 - _top) * old_h
                    axes_h_in    = (_top - _bottom) * old_h
                    new_top = 1.0 - top_margin_in / new_h
                    fig.subplots_adjust(bottom=new_top - axes_h_in / new_h, top=new_top)

            if _has_categorical_ylabels:
                extra_in_w = max(0.0, (tl_left - _left) * old_w) + 0.1
                if extra_in_w > 0.1:
                    new_w = old_w + extra_in_w
                    fig.set_figwidth(new_w)
                    right_margin_in = (1.0 - _right) * old_w
                    axes_w_in       = (_right - _left) * old_w
                    new_right = 1.0 - right_margin_in / new_w
                    fig.subplots_adjust(left=new_right - axes_w_in / new_w, right=new_right)

        if plot_title:
            add_centered_suptitle(fig, plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="scan.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)

if __name__ == "__main__":
    main()
