#!/usr/bin/env python3

"""
Script 2: Simple Histogram Plot with DUNE Style
Demonstrates basic plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_subtitle_from_args, make_title_from_args, make_config_label_from_args, make_config_color_and_style_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_scientific_threshold_formatter, apply_legend_style, plot_data, create_common_subplots, apply_note_to_figure, place_vertical_label, place_horizontal_label, place_point_label

from common_args import add_common_args

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
        "datafile": {"required": True},
        "x": {"nargs": "+", "required": True, "help": "Column names for x-axis data"},
        "iterable": {"help": "Column name for iterable data"},
        "variables": {"help": "List of column names to use as variables for multiple subplots"},
        "percentile": {"nargs": 2},
        "labelx": {"default": r"Time ($\mu$s)"},
        "labely": {"default": "Density"},
    },
)

parser.add_argument(
    "--operation",
    type=str,
    default="subtract",
    help="Operation to perform on data (e.g. mean, sum, etc.)",
)

parser.add_argument(
    "--weight",
    "-w",
    type=str,
    default=None,
    help="Column name for weight data",
)



args = parser.parse_args()


def main():
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

    print(f"Number of unique variables for plotting: {ncols}")

    configs, names = prepare_import(args)
    configs = configs if (configs is not None and args.iterable != "Config") else [None]
    names = names if (names is not None and args.iterable != "Name") else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

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

        # rprint(f"Dataframe entries for this config and iterable: {len(df_config)}, Unique iterable values: {df_config[args.iterable].unique()}")
        hist_range = None
        variables = args.variables if args.variables is not None else [None]
        iterables = args.iterable if args.iterable is not None else [None]
        iterable_values = (
            df_config[args.iterable].unique() if args.iterable is not None else [None]
        )
        two_line_mode = len(iterable_values) == 2
        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables),
            enumerate(
                iterable_values
            ),
        ):
            if args.iterable is not None:
                if len(iterable_values) > 8 and args.reduce:
                    if jdx % 2 == 1:
                        rprint(
                            f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding"
                        )
                        continue

            if iterable is None:
                rprint("Skipping None iterable value")
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

            if len(args.x) == 1:
                x = subset[args.x[0]].values[0]  # Convert to NumPy array

            else:
                # Prepare empty array
                x = subset[args.x[0]].values[0]
                for col in args.x[1:]:
                    if args.operation in ["mean", "sum"]:
                        x = np.add(x, np.array(subset[col].values[0]))
                    elif args.operation in [
                        "subtract",
                        "relative",
                        "absolute_relative",
                    ]:
                        x = np.subtract(x, np.array(subset[col].values[0]))
                    elif args.operation == "rms":
                        x = np.add(x**2, np.array(subset[col].values[0]) ** 2)

                if args.operation == "mean":
                    x = x / len(args.x)
                elif args.operation == "relative":
                    x = x / np.array(subset[args.x[-1]].values[0])
                elif args.operation == "absolute_relative":
                    x = np.abs(x) / np.array(subset[args.x[-1]].values[0])
                elif args.operation == "rms":
                    x = np.sqrt(x / len(args.x))
            # print(x)
            if hist_range is None:
                if args.percentile is None:
                    hist_range = (np.min(x).astype(float), np.max(x).astype(float))
                else:
                    hist_range = (
                        np.percentile(x, args.percentile[0]).astype(float),
                        np.percentile(x, args.percentile[1]).astype(float),
                    )

            # print(hist_range)
            hist, bins = np.histogram(
                x,
                bins=args.bins,
                range=hist_range,
                density=args.labely == "Density",
                weights=(
                    subset[args.weight].values[0] if args.weight is not None else None
                ),
            )
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            # Generate label, color, and linestyle based on iterable type
            if args.iterable == "Config":
                # When iterating over configs, use the config naming structure and styling
                label = make_config_label_from_args(args, config=iterable, name=name)
                color, linestyle = make_config_color_and_style_from_args(args, config=iterable, name=name)
                if two_line_mode:
                    color = f"C{jdx}"
            else:
                # For other iterables, use the iterable value directly
                label = f"{iterable}"
                color = f"C{jdx}" if two_line_mode else None
                linestyle = None
            
            plot_data(
                args,
                ax_current,
                bin_centers,
                y=hist,
                label=label,
                color=color,
                linestyle=linestyle,
                plot_type="plot",
                drawstyle="steps-mid",
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

            if args.rangex is None:
                ax.set_xlim(hist_range)
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

            vertical = getattr(args, "vertical", None)
            vertical_label = getattr(args, "vertical_label", None)
            horizontal = getattr(args, "horizontal", None)
            horizontal_label = getattr(args, "horizontal_label", None)

            if vertical is not None:
                ax_current.axvline(vertical, color="gray", linestyle="--", linewidth=1)
                if vertical_label is not None:
                    place_vertical_label(ax_current, vertical, vertical_label, fontsize=linelabelfontsize)

            if horizontal is not None:
                ax_current.axhline(horizontal, color="gray", linestyle="--", linewidth=1)
                if horizontal_label is not None:
                    place_horizontal_label(ax_current, horizontal, horizontal_label, fontsize=linelabelfontsize)

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

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="hist1d.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)


if __name__ == "__main__":
    main()
