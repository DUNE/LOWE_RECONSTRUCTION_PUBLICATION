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
from lib.plot import apply_scientific_threshold_formatter, apply_legend_style, plot_data, create_common_subplots, apply_note_to_figure, add_centered_suptitle, draw_vertical_lines, draw_horizontal_lines, place_point_label

from common_args import add_common_args, resolve_axis_label, parse_plot_label, map_iterable_label, map_iterable_color

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
        "remove_value",
        "filename_select",
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

parser.add_argument(
    "--panel_rangex",
    nargs="+",
    type=float,
    default=None,
    help="Per-panel x-axis histogram range as flattened min max pairs, two values per --variables "
    "entry (e.g. 0 90 0 90 0 800 for three panels). Falls back to --rangex/--percentile/auto-range "
    "if omitted.",
)

parser.add_argument(
    "--panel_title",
    nargs="+",
    type=parse_plot_label,
    default=None,
    help="Per-panel title, one per --variables entry, shown above each subplot instead of the default subtitle.",
)

parser.add_argument(
    "--panel_labelx",
    nargs="+",
    type=parse_plot_label,
    default=None,
    help="Per-panel x-axis label, one per --variables entry. Falls back to --labelx applied to every "
    "panel, or an auto-resolved label if neither is given.",
)

parser.add_argument(
    "--panel_vertical",
    nargs="+",
    type=str,
    default=None,
    help="Per-panel vertical reference line(s): one entry per --variables entry (in that panel's own x "
    "units), or 'none' to skip a panel. An entry may hold several comma-separated x-values (e.g. "
    "'26.8,63.5') to draw multiple reference lines in that panel. Drawn in addition to any --vertical "
    "lines, which apply to every panel unshifted.",
)
parser.add_argument(
    "--panel_vertical_label",
    nargs="+",
    type=str,
    default=None,
    help="Label(s) for each --panel_vertical entry, one per --variables entry ('' for no label); "
    "comma-separate multiple labels to match multiple comma-separated values in --panel_vertical.",
)
parser.add_argument(
    "--panel_vertical_style",
    nargs="+",
    type=str,
    default=None,
    help="Linestyle(s) for each --panel_vertical entry, one per --variables entry (default '--'); "
    "comma-separate multiple styles to match multiple comma-separated values in --panel_vertical.",
)
parser.add_argument(
    "--panel_vertical_color",
    nargs="+",
    type=str,
    default=None,
    help="Color(s) for each --panel_vertical entry, one per --variables entry (default 'gray'); "
    "comma-separate multiple colors to match multiple comma-separated values in --panel_vertical.",
)


parser.add_argument(
    "--iterable_mapping",
    type=str,
    default=None,
    help="Optional mapping dictionary name from plot_params mappings used to rename --iterable values in the legend",
)
parser.add_argument(
    "--iterable_color_mapping",
    type=str,
    default=None,
    help="Optional mapping dictionary name from plot_params mappings used to set the --iterable line colors (Cn or rgb(r,g,b))",
)
args = parser.parse_args()


def _parse_panel_line_values(raw_values, flag_name):
    """Parse a --panel_vertical value list into one list of floats per
    --variables entry. Each raw entry may be 'none'/'skip'/'' (no line in
    that panel), a single number, or several comma-separated numbers (to draw
    multiple reference lines in that panel)."""
    if raw_values is None:
        return None
    parsed = []
    for raw in raw_values:
        if str(raw).strip().lower() in ("none", "skip", ""):
            parsed.append(None)
        else:
            values = []
            for piece in str(raw).split(","):
                try:
                    values.append(float(piece))
                except ValueError:
                    parser.error(
                        f"{flag_name} values must be numbers or 'none' to skip a panel, got '{piece}' in '{raw}'"
                    )
            parsed.append(values)
    return parsed


def _parse_panel_line_strings(raw_values):
    """Parse a --panel_vertical_label/_style/_color list into one list of
    strings per --variables entry, splitting each raw entry on commas to
    match multiple comma-separated values in --panel_vertical."""
    if raw_values is None:
        return None
    return [str(raw).split(",") for raw in raw_values]


args.panel_vertical = _parse_panel_line_values(args.panel_vertical, "--panel_vertical")
args.panel_vertical_label = _parse_panel_line_strings(args.panel_vertical_label)
args.panel_vertical_style = _parse_panel_line_strings(args.panel_vertical_style)
args.panel_vertical_color = _parse_panel_line_strings(args.panel_vertical_color)

if args.panel_rangex is not None and args.variables is not None and len(args.panel_rangex) != 2 * len(args.variables):
    parser.error(
        f"--panel_rangex must provide exactly 2 values per --variables entry "
        f"({2 * len(args.variables)} expected, got {len(args.panel_rangex)})."
    )
if args.panel_title is not None and args.variables is not None and len(args.panel_title) != len(args.variables):
    parser.error(
        f"--panel_title must provide exactly one value per --variables entry "
        f"({len(args.variables)} expected, got {len(args.panel_title)})."
    )
if args.panel_labelx is not None and args.variables is not None and len(args.panel_labelx) != len(args.variables):
    parser.error(
        f"--panel_labelx must provide exactly one value per --variables entry "
        f"({len(args.variables)} expected, got {len(args.panel_labelx)})."
    )
for _flag_name, _values in (
    ("--panel_vertical", args.panel_vertical),
    ("--panel_vertical_label", args.panel_vertical_label),
    ("--panel_vertical_style", args.panel_vertical_style),
    ("--panel_vertical_color", args.panel_vertical_color),
):
    if _values is not None and args.variables is not None and len(_values) != len(args.variables):
        parser.error(
            f"{_flag_name} must provide exactly one value per --variables entry "
            f"({len(args.variables)} expected, got {len(_values)})."
        )


def main():
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    # Real NaN values in the "Variable" column are excluded by default.
    # Explicitly requesting "None" in --variables opts back in, converting
    # those NaNs to the literal string "None" so they survive filtering.
    if args.variables is not None and "None" in args.variables and "Variable" in df.columns:
        df["Variable"] = df["Variable"].fillna("None")

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
        # Keyed by panel index rather than a single shared value -- panels
        # backed by --variables commonly hold columns on very different
        # scales (e.g. a hit count vs. a distance in cm), so the auto/
        # percentile-derived range from one panel must not leak into another.
        hist_range_by_idx = {}
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
            if idx not in hist_range_by_idx:
                if args.panel_rangex is not None:
                    hist_range_by_idx[idx] = (args.panel_rangex[2 * idx], args.panel_rangex[2 * idx + 1])
                elif args.rangex is not None:
                    hist_range_by_idx[idx] = (args.rangex[0], args.rangex[1])
                elif args.percentile is None:
                    hist_range_by_idx[idx] = (np.min(x).astype(float), np.max(x).astype(float))
                else:
                    hist_range_by_idx[idx] = (
                        np.percentile(x, args.percentile[0]).astype(float),
                        np.percentile(x, args.percentile[1]).astype(float),
                    )
            hist_range = hist_range_by_idx[idx]

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
                if args.iterable_mapping is not None:
                    label = map_iterable_label(iterable, args.iterable, args.iterable_mapping)
                if args.iterable_color_mapping is not None:
                    color = map_iterable_color(iterable, args.iterable_color_mapping) or color
            
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
                plot_subtitle = args.panel_title[idx] if args.panel_title is not None else make_subtitle_from_args(args, idx)
                ax_current.set_title(
                    plot_subtitle,
                    fontsize=subtitlefontsize,
                )

            ax_current.set_xlabel(
                args.panel_labelx[idx] if args.panel_labelx is not None else resolve_axis_label(args.labelx, None, df)
            )
            (
                ax_current.set_ylabel(resolve_axis_label(args.labely, None, df))
                if idx == 0
                else None
            )

            if args.panel_rangex is not None:
                ax_current.set_xlim(args.panel_rangex[2 * idx], args.panel_rangex[2 * idx + 1])
            elif args.rangex is None:
                ax_current.set_xlim(hist_range_by_idx.get(idx))
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

            if args.panel_vertical is not None and args.panel_vertical[idx] is not None:
                draw_vertical_lines(
                    ax_current,
                    args.panel_vertical[idx],
                    labels=args.panel_vertical_label[idx] if args.panel_vertical_label is not None else None,
                    styles=args.panel_vertical_style[idx] if args.panel_vertical_style is not None else None,
                    colors=args.panel_vertical_color[idx] if args.panel_vertical_color is not None else None,
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
        add_centered_suptitle(fig, plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="hist1d.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)


if __name__ == "__main__":
    main()
