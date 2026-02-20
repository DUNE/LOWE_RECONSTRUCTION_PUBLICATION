#!/usr/bin/env python3

"""
Script 2: Simple Histogram Plot with DUNE Style
Demonstrates basic plotting with custom styling
"""

from matplotlib.ticker import MaxNLocator
from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args
from lib.imports import import_data, prepare_import

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the charge over time distribution of the particles"
)

parser.add_argument(
    "--datafile",
    type=str,
    default=None,
    help="Path to the input data file (pkl format)",
    required=True,
)

parser.add_argument(
    "--configs",
    nargs="+",
    type=str,
    default=None,
    help="DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)",
)

parser.add_argument(
    "--names",
    "-n",
    nargs="+",
    type=str,
    default=None,
    help="Name of the simulation configuration (e.g. marley_official, marley, etc.)",
)

parser.add_argument(
    "--variables",
    "-v",
    nargs="+",
    type=str,
    default=None,
    help="List of column names to use as variable for multiple subplots",
)

parser.add_argument(
    "-x",
    type=str,
    default=None,
    help="Column names for x-axis data",
    required=True,
)

parser.add_argument(
    "-y",
    type=str,
    default=None,
    help="Column names for y-axis data",
    required=True,
)

parser.add_argument(
    "--iterable",
    "-i",
    type=str,
    default=None,
    help="Column name for iterable data",
)

parser.add_argument(
    "--operation",
    type=str,
    default=None,
    help="Operation to perform on iterable data",
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

parser.add_argument(
    "--reduce",
    action="store_true",
    help="Reduce number of lines plotted for clarity",
    default=False,
)

parser.add_argument(
    "--select",
    nargs="+",
    default=None,
    help="If provided, filter plots for which according to select columns and values in save_values",
)

parser.add_argument(
    "--save_values",
    "-s",
    nargs="+",
    default=None,
    help="If provided, filter plots for which according to select columns and these values",
)

parser.add_argument(
    "--bins",
    "-b",
    type=int,
    default=nbins,
    help="Number of bins for histogram",
)

parser.add_argument(
    "--percentile",
    "-p",
    nargs=2,
    type=float,
    default=(0, 100),
    help="Percentile range for axis limits (e.g. 1 99)",
)

parser.add_argument(
    "--labelx",
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
    "-d",
    action="store_true",
    help="Enable debug mode",
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
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    # Select the entries in the dataframe with with name matching args.names and nake a plot for each iterable
    if args.variables == None:
        ncols = 1
    else:
        ncols = len(args.variables)

    print(f"Number of unique variables for plotting: {ncols}")

    configs, names = prepare_import(args)
    configs = configs if (configs is not None and args.iterable != "Config") else [None]
    names = names if (names is not None and args.iterable != "Name") else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = plt.subplots(
            nrows=1,
            ncols=ncols,
            figsize=(8 + 5 * (ncols - 1), 6),
            constrained_layout=ncols > 1,
        )
        if config is not None and name is None and args.iterable != "Config":
            df_config = df[(df["Config"] == config)]

        elif config is None and name is not None and args.iterable != "Name":
            df_config = df[(df["Name"] == name)]

        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]

        else:
            df_config = df.copy()

        rprint(f"Dataframe entries for this config: {len(df_config)}")

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
            if np.issubdtype(x.dtype, np.integer):
                bins = np.arange(x.min(), x.max() + 1.5) - 0.5
                bin_centers = np.arange(x.min(), x.max() + 1)
                if args.reduce and len(bins) > 8:
                    bins = bins[::2]
                    bin_centers = bin_centers[::2]
                # Check that the last entry in bin_centers is 0.5 higher than the last entry in bins, otherwise remove the last entry in bins
                if bins[-1] < bin_centers[-1]:
                    bin_centers = bin_centers[:-1]

                print(
                    f"Integer x values detected. Using bins: {bins} and bin centers: {bin_centers}"
                )

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
                ax_current.boxplot(
                    boxplot_data,
                    positions=bin_centers,
                    widths=(
                        np.diff(bins) * 0.8
                        if np.issubdtype(x.dtype, np.integer)
                        else None
                    ),
                    showfliers=False,
                    label=(
                        f"{args.y}: {variable}"
                        if variable is not None
                        else (
                            f"{iterable}"
                            if args.iterable is not None
                            else f"{args.y} vs {args.x}"
                        )
                    ),
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

                operation = args.operation or "mean"
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
                    rprint(
                        f"[yellow]Warning:[/yellow] No operation specified. Defaulting to mean."
                    )

                ax_current.scatter(
                    bin_centers,
                    y_scatter,
                    marker="o",
                    label=(
                        f"{args.y}: {variable}"
                        if variable is not None
                        else (
                            f"{iterable}"
                            if args.iterable is not None
                            else f"{args.y} vs {args.x}"
                        )
                    ),
                )

        for idx, variable in enumerate(variables):
            if ncols == 1:
                ax_current = ax

            else:
                ax_current = ax[idx]

            if ncols > 1:
                ax_current.set_title(
                    f"Variable: {variable}" if variable is not None else None,
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

            if args.logy:
                ax_current.semilogy()

            if args.logx:
                ax_current.semilogx()

            (
                ax_current.legend(
                    title=args.iterable,
                    title_fontsize=legendtitlefontsize,
                    fontsize=legendfontsize,
                )
                if idx == ncols - 1
                else None
            )
        # Set title
        plot_title = f"{args.datafile.replace('_', ' ')}"
        if config is not None:
            plot_title += f" - {config}"

        if args.select is not None:
            if args.save_values is not None:
                for save_key, save_value in zip(args.select, args.save_values):
                    plot_title += f" - {save_key}: {save_value}"
            else:
                plot_title += f" - {variable}"

        fig.suptitle(plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        output_file = make_name_from_args(
            args, kdx, prefix=None, suffix="box.png" if args.boxplot else "scatter.png"
        )
        if args.output is not None:
            output_dir = os.path.dirname(args.output)
            os.makedirs(output_dir, exist_ok=True)
            rprint(
                f"[green]Success:[/green] Plot saved to:\n{args.output}{output_file}"
            )
        else:
            output_dir = os.path.join(os.path.dirname(__file__), "..", "plots")
            os.makedirs(output_dir, exist_ok=True)
            rprint(
                f"[green]Success:[/green] Plot saved to:\n{os.path.join(output_dir.split('..')[1], output_file)}"
            )

        plt.savefig(os.path.join(output_dir, output_file))

        plt.close()


if __name__ == "__main__":
    main()
