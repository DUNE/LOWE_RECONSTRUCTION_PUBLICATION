#!/usr/bin/env python3

"""
Script 2: Simple Histogram Plot with DUNE Style
Demonstrates basic plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from matplotlib.ticker import MaxNLocator
from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_subtitle_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_scientific_threshold_formatter, apply_legend_style, plot_data, create_common_subplots, apply_note_to_figure, draw_vertical_lines, draw_horizontal_lines, place_point_label
from common_args import add_common_args, load_computation_settings, resolve_plot_kwargs


# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the charge over time distribution of the particles"
)

add_common_args(
    parser,
    [
        "datafile",
        "configs",
        "names",
        "variables",
        "x",
        "y",
        "iterable",
        "reduce",
        "select",
        "save_values",
        "bins",
        "percentile",
        "labelx",
        "labely",
        "logx",
        "logy",
        "rangex",
        "rangey",
        "plot_type",
        "title",
        "output",
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
        "datafile": {"required": True},
        "x": {"required": True, "help": "Column names for x-axis data"},
        "y": {"required": True, "help": "Column names for y-axis data"},
        "iterable": {"help": "Column name for iterable data"},
        "variables": {"help": "List of column names to use as variable for multiple subplots"},
        "percentile": {"nargs": 2, "default": (0, 100)},
        "bins": {"default": nbins},
    },
)

parser.add_argument(
    "--operation",
    type=str,
    default=None,
    help="Operation to perform on iterable data",
)

parser.add_argument(
    "--default_operation",
    type=str,
    default=None,
    help="Default operation to use when operation is not specified (overrides config default)",
)

parser.add_argument(
    "--threshold",
    action="store_true",
    help="If set, use the x axis as threshold instead of bins",
    default=False,
)

parser.add_argument(
    "--boxplot",
    action="store_true",
    help="If set, creates box plots instead of scatter",
    default=False,
)

args = parser.parse_args()

def main():
    """
    Main function to generate box plots comparing data across configurations.

    This function performs the following operations:
    1. Imports data from specified files using import_data()
    2. Prepares configurations and names through prepare_import()
    3. For each configuration/name combination:
        - Filters the dataframe based on config, name, variable, and iterable parameters
        - Creates subplots with dimensions based on the number of variables
        - Bins the x-axis data:
          * For integer x values: Creates bins with step size of 2 (e.g., [0.5, 2.5, 4.5, ...])
             and bin centers at even integers (e.g., [1, 3, 5, ...])
          * For continuous x values: Creates linearly spaced bins based on args.bins parameter
        - Generates box plots for y-values within each x bin
        - Applies formatting (labels, limits, scale, legend) to each subplot
        - Saves the figure to the specified output directory

    The width of boxes for integer x values is set to 80% of the bin width (which is 2),
    resulting in a box width of 1.6 units. This spacing prevents overlapping boxes and
    maintains visual separation between consecutive integer bins.

    Returns:
         None
    """
    # Load default operation from computation settings
    computation_settings = load_computation_settings()
    _operation_config = computation_settings.get("default_operation")
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    # Select the entries in the dataframe with with name matching args.names and nake a plot for each iterable
    if args.variables is None:
        ncols = 1
    else:
        ncols = len(args.variables)

    configs, names = prepare_import(args)
    configs = configs if (configs is not None and args.iterable != "Config") else [None]
    names = names if (names is not None and args.iterable != "Name") else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        fig, ax = create_common_subplots(
            nrows=1,
            ncols=ncols,
        )
        if config is not None and name is None and args.iterable != "Config":
            df_config = df[(df["Config"] == config)]

        elif config is None and name is not None and args.iterable != "Name":
            df_config = df[(df["Name"] == name)]

        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]

        else:
            df_config = df.copy()

        hist_range = None
        variables = args.variables if args.variables is not None else [None]
        iterables = args.iterable if args.iterable is not None else [None]

        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables),
            enumerate(
                df_config[args.iterable].unique()
                if args.iterable is not None
                else [None]
            ),
        ):
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

            elif iterable is not None and variable is not None:
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

            subset = filter_dataframe(df_iterable, args)
            x = subset[args.x].values[0]  # Convert to NumPy array
            y = subset[args.y].values[0]  # Convert to NumPy array

            # Sample the y values according to the specified x values and create a boxplot of the y values for each x bin
            # If the x values are int create bins for each int value, otherwise create bins according to the specified number of bins
            if isinstance(x, list):
                continue

            elif np.issubdtype(x.dtype, np.integer):
                if x.size > 0:
                    bins = np.arange(x.min(), x.max() + 1.5) - 0.5
                    bin_centers = np.arange(x.min(), x.max() + 1)
                    if args.reduce and len(bins) > 8:
                        bins = bins[::2]
                        bin_centers = bin_centers[::2]
                    # Check that the last entry in bin_centers is 0.5 higher than the last entry in bins, otherwise remove the last entry in bins
                    if bins[-1] < bin_centers[-1]:
                        bin_centers = bin_centers[:-1]

                else:
                    rprint(
                        f"[yellow]Warning:[/yellow] No x values found. Skipping plot."
                    )
                    continue
            else:
                bins = np.linspace(
                    x.min(), x.max(), args.bins if args.bins is not None else nbins + 1
                )
                bin_centers = (bins[:-1] + bins[1:]) / 2

            if args.boxplot:
                if args.threshold:
                    # If threshold is set, use x values as thresholds instead of bins
                    boxplot_data = [y[(x >= bins[i])] for i in range(len(bins) - 1)]
                else:
                    boxplot_data = [
                        y[(x >= bins[i]) & (x < bins[i + 1])]
                        for i in range(len(bins) - 1)
                    ]
                plot_data(
                    args,
                    ax_current,
                    bin_centers,
                    y=boxplot_data,
                    label=f"Median {args.y}",
                    plot_type="boxplot",
                    positions=bin_centers,
                    widths=(
                        np.diff(bins) * 0.8
                        if np.issubdtype(x.dtype, np.integer)
                        else None
                    ),
                    showfliers=False,
                )
            else:

                def get_operation(op):
                    ops = {
                        "mean": lambda arr: arr.mean(),
                        "average": lambda arr: arr.mean(),
                        "sum": lambda arr: arr.sum(),
                        "max": lambda arr: arr.max(),
                        "min": lambda arr: arr.min(),
                    }
                    return ops.get(op.lower() if op else "mean")

                operation = args.operation or args.default_operation or _operation_config or "mean"
                if operation.lower() not in ["mean", "average", "sum", "max", "min"]:
                    rprint(
                        f"[red]Error:[/red] Invalid operation: {operation}. Supported: mean, average, sum, max, min."
                    )
                    return

                op_func = get_operation(operation)
                mask_func = (
                    (lambda i: x >= bins[i])
                    if args.threshold
                    else (lambda i: (x >= bins[i]) & (x < bins[i + 1]))
                )
                y_scatter = [op_func(y[mask_func(i)]) for i in range(len(bins) - 1)]

                if args.operation is None:
                    source = "flag" if args.default_operation else "config"
                    rprint(
                        f"[yellow]Warning:[/yellow] No operation specified. Using default from {source}: {operation}."
                    )

                selected_plot_type = getattr(args, "plot_type", None) or "scatter_points"
                plot_kwargs = resolve_plot_kwargs(selected_plot_type)

                plot_data(
                    args,
                    ax_current,
                    bin_centers,
                    y=y_scatter,
                    label=(
                        f"{args.y}: {variable}"
                        if variable is not None
                        else (
                            f"{iterable}"
                            if args.iterable is not None
                            else f"{args.y} vs {args.x}"
                        )
                    ),
                    marker="o" if selected_plot_type == "scatter_points" else None,
                    **plot_kwargs,
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
            (
                ax_current.set_ylabel(
                    args.labely if args.labely is not None else f"{args.y}"
                )
                if idx == 0
                else None
            )
            # Limit the number of x ticks to 10 for readability by removing some of the ticks and their labels if there are more than 10
            if len(ax_current.get_xticks()) > 10 and args.reduce:
                xticks = ax_current.get_xticks()
                step = max(1, len(xticks) // 10)
                ax_current.set_xticks(xticks[::step])

            if args.rangex is None:
                ax_current.set_xlim(hist_range)
            else:
                ax_current.set_xlim(args.rangex[0], args.rangex[1])

            if args.rangey is not None:
                ax_current.set_ylim(args.rangey[0], args.rangey[1])

            apply_scientific_threshold_formatter(ax_current, threshold=0.1, axis="both")

            if args.logy:
                ax_current.semilogy()

            if args.logx:
                ax_current.semilogx()

            if idx == ncols - 1:
                apply_legend_style(
                    ax_current,
                    title=args.iterable,
                    capitalize_labels=not getattr(args, "no_capitalize_legend", False),
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

        # Set title
        plot_title = make_title_from_args(args)
        fig.suptitle(plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        # Choose output filename suffix based on plot type
        if args.boxplot:
            suffix_base = "box"
        else:
            selected_plot_type_for_filename = getattr(args, "plot_type", None) or "scatter_points"
            _suffix_map = {
                "scatter_points": "scatter",
                "scatter": "scatter",
                "step": "step",
                "plot": "plot",
                "line": "line",
                "bar": "bar",
                "errorbar": "errorbar",
            }
            suffix_base = _suffix_map.get(selected_plot_type_for_filename, selected_plot_type_for_filename)

        output_file = make_name_from_args(
            args, kdx, prefix=None, suffix=f"{suffix_base}.png"
        )
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)

if __name__ == "__main__":
    main()
