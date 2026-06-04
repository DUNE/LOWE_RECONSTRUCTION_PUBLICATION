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
from lib.plot import (
    apply_legend_style,
    plot_data,
    create_common_subplots,
    apply_note_to_figure,
    place_vertical_label,
    place_horizontal_label,
    place_point_label,
)
from common_args import add_common_args, map_iterable_label, map_iterable_color


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
            "choices": ["scatter", "line", "bar", "step", "plot", "errorbar"],
            "help": "Explicit plot type override (scatter, line, bar, step, plot, errorbar)",
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
        ncols = 1
    else:
        ncols = len(args.variables)

    rprint(f"Number of unique variables for plotting: {ncols}")

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = create_common_subplots(
            nrows=1,
            ncols=ncols,
        )

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

            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx]

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

                    y = subset[args.y].astype(float).to_numpy()
                    x_edges = None
                    x = np.array([])
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

                    except ValueError:
                        x = subset[args.x].astype(str)
                        x_error = None

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

                        plot_label = iterable_label if idx == ncols - 1 else None

                        if args.plot_type == "line":
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
                                label=iterable_label if idx == ncols - 1 else None,
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
                                label=iterable_label if idx == ncols - 1 else None,
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
                                label=iterable_label if idx == ncols - 1 else None,
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
                                label=iterable_label if idx == ncols - 1 else None,
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

            y = subset[args.y].astype(float).to_numpy()
            x_edges = None
            x = np.array([])
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

            except ValueError:
                x = subset[args.x].astype(str)
                x_error = None

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

                plot_label = iterable_label if idx == ncols - 1 else None

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
                        label=iterable_label if idx == ncols - 1 else None,
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
                            label=iterable_label if idx == ncols - 1 else None,
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
                        label=iterable_label if idx == ncols - 1 else None,
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
                            label=iterable_label if idx == ncols - 1 else None,
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
                            label=iterable_label if idx == ncols - 1 else None,
                            color=iterable_color,
                            plot_type="plot",
                            marker="o",
                            linestyle="None",
                        )

        for idx, variable in enumerate(variables):
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx]

            if ncols > 1:
                plot_subtitle = make_subtitle_from_args(args, idx)
                ax_current.set_title(
                    plot_subtitle,
                    fontsize=subtitlefontsize,
                )

            ax_current.set_xlabel(
                args.labelx if args.labelx is not None else f"{args.x}"
            )
            # If x are of string type, rotate x-axis labels for better readability
            if isinstance(last_x, np.ndarray) and last_x.dtype.kind in ('U', 'S', 'O'):
                plt.setp(ax_current.get_xticklabels(), rotation=45, ha="right")

            (
                ax_current.set_ylabel(
                    args.labely if args.labely is not None else f"{args.y}"
                )
                if idx == 0
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

            if args.stacked:
                if idx == ncols - 1:
                    apply_legend_style(
                        ax_current,
                        title=args.labelz if args.labelz is not None else args.iterable,
                        loc="upper left",
                        bbox_to_anchor=(0, 1),
                        capitalize_labels=not getattr(args, "no_capitalize_legend", False),
                    )

            else:
                if idx == ncols - 1:
                    apply_legend_style(
                        ax_current,
                        title=args.labelz if args.labelz is not None else args.iterable,
                        capitalize_labels=not getattr(args, "no_capitalize_legend", False),
                    )

            vertical = getattr(args, "vertical", None)
            vertical_label = getattr(args, "vertical_label", None)
            horizontal = getattr(args, "horizontal", None)
            horizontal_label = getattr(args, "horizontal_label", None)

            if vertical is not None:
                ax_current.axvline(vertical, color="gray", linestyle="--", linewidth=1)
                if vertical_label is not None:
                    # Place vertical label next to the line using content-aware helper
                    place_vertical_label(
                        ax_current, vertical, vertical_label, fontsize=linelabelfontsize
                    )

            if horizontal is not None:
                ax_current.axhline(horizontal, color="gray", linestyle="--", linewidth=1)
                if horizontal_label is not None:
                    # Place horizontal label next to the line using content-aware helper
                    place_horizontal_label(
                        ax_current, horizontal, horizontal_label, fontsize=linelabelfontsize
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

        plot_title = make_title_from_args(args)
        fig.suptitle(plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="scan.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)

if __name__ == "__main__":
    main()
