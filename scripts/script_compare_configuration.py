#!/usr/bin/env python3

"""
Script 5: Combined Line Plot with DUNE Style
Demonstrates combined data plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from lib import *
from lib.exports import make_name_from_args
from lib.format import make_subtitle_from_args, make_title_from_args
from lib.functions import resolution, gaussian
from lib.imports import import_data, prepare_import
from lib.plot import plot_data
from lib.selection import prepare_selection, filter_dataframe

from rich import print as rprint

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)

parser.add_argument(
    "--datafile",
    type=str,
    default="Vertex_Reconstruction_Efficiency",
    help="Path to the input data file (pkl format)",
)

parser.add_argument(
    "--configs",
    nargs="+",
    type=str,
    default=[
        "hd_1x2x6",
        "hd_1x2x6_lateralAPA",
        "hd_1x2x6_centralAPA",
        "vd_1x8x14_3view_30deg",
        "vd_1x8x14_3view_30deg_nominal",
    ],
    help="DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)",
)

parser.add_argument(
    "--names",
    nargs="+",
    type=str,
    default=["marley_official"],
    help="Name of the simulation configuration (e.g. marley_official, marley, etc.)",
)

parser.add_argument(
    "--variables",
    "-v",
    nargs="+",
    type=str,
    default=None,
    help="Row filter variable name",
)

parser.add_argument(
    "--iterable",
    "-i",
    type=str,
    default=None,
    help="Iterable column to produce plots",
)

parser.add_argument(
    "--select",
    nargs="+",
    type=str,
    default=None,
    help="List of columns to filter the iterable or variables",
)

parser.add_argument(
    "--save_values",
    "-s",
    nargs="+",
    default=None,
    help="If select is provided, only save these values from the iterable column(s)",
)

parser.add_argument(
    "--comparable",
    "-c",
    type=str,
    default="Config",
    help="List of comparable parameter to produce plots",
)

parser.add_argument(
    "-x",
    type=str,
    default="Values",
    help="Column name for x-axis values",
)

parser.add_argument(
    "--rangex",
    nargs=2,
    type=float,
    default=None,
    help="Range for x-axis values",
)

parser.add_argument(
    "--rangey",
    nargs=2,
    type=float,
    default=None,
    help="Range for y-axis values",
),

parser.add_argument(
    "-y",
    type=str,
    default=None,
    help="Column name for y-axis values",
),

parser.add_argument(
    "--plot_type",
    type=str,
    default="step",
    help="Style of errors.",
    choices=["scatter", "line", "step"],
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
    "--logx",
    action="store_true",
    help="Set x-axis to logarithmic scale",
    default=False,
)

parser.add_argument(
    "--logy",
    action="store_true",
    help="Set y-axis to logarithmic scale",
    default=False,
)

parser.add_argument(
    "--labelx",
    nargs="+",
    type=str,
    default=None,
    help="Label for x-axis on plot",
)

parser.add_argument(
    "--labely",
    type=str,
    default=None,
    help="Label for y-axis on plot",
)

parser.add_argument(
    "--align",
    type=str,
    default="mid",
    help="Alignment of histogram bars (e.g. mid, left, right)",
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
    "--horizontal",
    type=float,
    default=None,
    help="Draw horizontal line at specified y value",
)

parser.add_argument(
    "--vertical",
    type=float,
    default=None,
    help="Draw vertical line at specified x value",
)

parser.add_argument(
    "--title",
    type=str,
    default=None,
    help="Title for the plot",
)

parser.add_argument(
    "--output",
    "-o",
    type=str,
    default=None,
    help="Output filepath for the plot",
)

parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug mode",
)
args = parser.parse_args()


def main():
    """
    Main function to process simulation configurations, load data files,
    and generate plots based on the provided arguments.
    """
    df = import_data(args)

    # Check if the DataFrame is empty
    if df.empty:
        rprint("No data to plot. Exiting.")
        return

    ncols = len(args.variables) if args.variables is not None else 1
    fig, ax = plt.subplots(
        nrows=1,
        ncols=ncols,
        figsize=(8 + 5 * (ncols - 1), 6),
        constrained_layout=ncols > 1,
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
        geoms = [geom.split("_")[0] for geom in configs]

        # combinedy = np.array([])
        # combined_errory = np.array([]) if args.errory is not None else None
        for ldx, (geom, config, name) in enumerate(zip(geoms, configs, names)):
            rprint(
                f"[blue]Info:[/blue] Processing Geometry: {geom}, Config: {config}, Name: {name}"
            )
            df_config = subset[(subset["Config"] == config) & (subset["Name"] == name)]

            if df_config.empty:
                rprint(
                    f"[yellow]Warning:[/yellow] No data for Config: {config}, Name: {name}. Skipping..."
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
                df_config = df_config.explode(column=columns)

            df_config = df_config.dropna(subset=columns)

            config_label = config_dict[config] if config in config_dict else str(config)
            if len(args.configs) <= 2 and len(args.names) == 1:
                geom_label = f"{geom.upper()}"
            elif len(args.configs) > 2 and len(args.names) == 1:
                geom_label = f"{geom.upper()}, {config_label}"
            elif len(args.configs) == 1 and len(args.names) > 1:
                geom_label = f"{geom.upper()}, {name}"
            else:
                geom_label = f"{geom.upper()}, {config_label}, {name}"

            if args.iterable is not None:
                geom_label += f", {iterable}"

            x = np.asarray(df_config[args.x].tolist())
            y = np.asarray(df_config[args.y].tolist())

            if args.errory:
                if errory_sym == "asymmetric":
                    errory = [
                        np.asarray(df_config[f"{args.y}Error-"].tolist()),
                        np.asarray(df_config[f"{args.y}Error+"].tolist()),
                    ]
                elif errory_sym == "symmetric":
                    errory = np.asarray(df_config[f"{args.y}Error"].tolist())
                else:
                    errory = None
            else:
                errory = None

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
                # Add extension to the data by mirroring the y values and adding the same amount of bins to the right
                x = np.concatenate((x, x + (x[-1] - x[0]) + x_bin))
                x_edges = np.linspace(x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1)
                y = np.concatenate((y, y[::-1]))
                # rprint(f"[blue]Info:[/blue] Mirroring data for configuration: {config}")

            offset = 0
            if args.operation is not None:
                offset = 1

            this_color = (
                (
                    f"C{0+offset}"
                    if (geom == "hd" or len(np.unique(geoms)) == 1)
                    else (
                        f"C{1+offset}"
                        if geom == "vd" and "shielded" not in config
                        else f"C{2+offset}"
                    )
                )
                if (len(geoms) > 1 or len(args.configs) > 1)
                else f"C{kdx}"
            )
            # Track the colors added to the plot. If colot already used, change linestyle to differentiate
            this_linestyle = "-"
            if this_color in used_colors and (
                len(geoms) > 1 or len(args.configs) > 1
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
                if args.errory:
                    errory = errory[::-1]

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

        if args.operation is not None:
            if args.operation == "squared_sum":
                combinedy = np.power(combinedy, 0.5)

            # errors are accumulated as variances in both branches above
            combined_errory = (
                np.power(combined_errory, 0.5) if combined_errory is not None else None
            )

            plot_data(
                args,
                ax_current,
                x,
                x_edges,
                combinedy,
                combined_errory,
                errory_sym,
                "Combined" if idx == ncols - 1 else None,
                f"C0",
                "-",
            )

        # Set titles and labels for the axes
        if ncols > 1:
            plot_subtitle = make_subtitle_from_args(args, idx)
            ax_current.set_title(plot_subtitle, fontsize=subtitlefontsize)

        ax_current.set_xlabel(
            args.labelx[idx]
            if args.labelx and len(args.labelx) == ncols
            else args.labelx[0] if args.labelx else args.x
        )
        if idx == 0:
            ax_current.set_ylabel(args.labely if args.labely else args.y)

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

        # Add horizontal line if specified
        if args.horizontal is not None:
            ax_current.axhline(
                args.horizontal, color="gray", linestyle="--", linewidth=1
            )
        # Add vertical line if specified
        if args.vertical is not None:
            ax_current.axvline(args.vertical, color="gray", linestyle="--", linewidth=1)

        # Set logarithmic scale if specified
        if args.logy:
            ax_current.set_yscale("log")
        if args.logx:
            ax_current.set_xscale("log")

        # Add legend for the last variable
        if idx == ncols - 1:
            ax_current.legend()

    # Set the figure title
    figure_title = make_title_from_args(args)
    fig.suptitle(figure_title, fontsize=titlefontsize)

    # dunestyle.WIP()

    output_file = make_name_from_args(
        args,
        prefix=None if len(np.unique(geoms)) > 1 else np.unique(geoms)[0],
        suffix="comparison.png",
    )
    if args.output is not None:
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        rprint(f"[green]Success:[/green] Plot saved to:\n{args.output}{output_file}")
    else:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
        os.makedirs(output_dir, exist_ok=True)
        rprint(
            f"[green]Success:[/green] Plot saved to:\n{os.path.join(output_dir.split('..')[1], output_file)[1:]}"
        )

    plt.savefig(os.path.join(output_dir, output_file))

    plt.close()


if __name__ == "__main__":
    main()
