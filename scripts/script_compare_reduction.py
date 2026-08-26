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
from lib.plot import apply_scientific_threshold_formatter, apply_legend_style, plot_data, create_common_subplots, apply_note_to_figure, add_centered_suptitle, draw_vertical_lines, draw_horizontal_lines, place_point_label, get_common_figsize, apply_common_figure_margins
from common_args import add_common_args, load_computation_settings, resolve_plot_kwargs, resolve_axis_label, parse_plot_label, map_iterable_label, map_iterable_color


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
        "remove_value",
        "bins",
        "percentile",
        "labelx",
        "labely",
        "labelz",
        "logx",
        "logy",
        "rangex",
        "rangey",
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
        "multiply",
        "debug",
    ],
    overrides={
        "datafile": {"required": True},
        "x": {"help": "Column name for x-axis data (required unless --panels is used)"},
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

parser.add_argument(
    "--panels",
    nargs="+",
    type=str,
    default=None,
    help="List of x-axis column names, one per subplot panel. Compacts several otherwise-identical "
    "invocations (differing only by the x column) into a single multi-panel figure; overrides -x/--x "
    "and --variables for panel layout purposes.",
)

parser.add_argument(
    "--panel_rangex",
    nargs="+",
    type=float,
    default=None,
    help="Per-panel x-axis range as flattened min max pairs, two values per --panels entry "
    "(e.g. 0 14 3 20 0 14 for three panels). Falls back to --rangex/auto-range if omitted.",
)

parser.add_argument(
    "--panel_title",
    nargs="+",
    type=parse_plot_label,
    default=None,
    help="Per-panel title, one per --panels entry, shown above each subplot instead of the default subtitle.",
)

parser.add_argument(
    "--compact",
    action="store_true",
    default=False,
    help="Draw --panels as a single set of shared axes with concatenated x ranges instead of separate "
    "subplot columns: same y-axis, one x-axis per panel range stitched side by side, with a dark "
    "vertical line marking each boundary. Requires --panels and --panel_rangex.",
)

parser.add_argument(
    "--panel_labelx",
    nargs="+",
    type=parse_plot_label,
    default=None,
    help="Per-panel x-axis label, one per --panels entry (used with --compact). Falls back to --labelx "
    "applied to every panel, or an auto-resolved per-column label if neither is given.",
)

parser.add_argument(
    "--panel_vertical",
    nargs="+",
    type=str,
    default=None,
    help="Per-panel vertical reference line: one x-value per --panels entry (in that panel's own x "
    "units), or 'none' to skip a panel. Drawn in addition to any --vertical lines, which apply to "
    "every panel unshifted.",
)
parser.add_argument(
    "--panel_vertical_label",
    nargs="+",
    type=str,
    default=None,
    help="Label for each --panel_vertical line, one per --panels entry ('' for no label).",
)
parser.add_argument(
    "--panel_vertical_style",
    nargs="+",
    type=str,
    default=None,
    help="Linestyle for each --panel_vertical line, one per --panels entry (default '--').",
)
parser.add_argument(
    "--panel_vertical_color",
    nargs="+",
    type=str,
    default=None,
    help="Color for each --panel_vertical line, one per --panels entry (default 'gray').",
)

parser.add_argument(
    "--panel_horizontal",
    nargs="+",
    type=str,
    default=None,
    help="Per-panel horizontal reference line: one y-value per --panels entry, or 'none' to skip a "
    "panel. In --compact mode the line only spans that panel's own segment of the shared axis. "
    "Drawn in addition to any --horizontal lines, which span the full axis in every panel.",
)
parser.add_argument(
    "--panel_horizontal_label",
    nargs="+",
    type=str,
    default=None,
    help="Label for each --panel_horizontal line, one per --panels entry ('' for no label).",
)
parser.add_argument(
    "--panel_horizontal_style",
    nargs="+",
    type=str,
    default=None,
    help="Linestyle for each --panel_horizontal line, one per --panels entry (default '--').",
)
parser.add_argument(
    "--panel_horizontal_color",
    nargs="+",
    type=str,
    default=None,
    help="Color for each --panel_horizontal line, one per --panels entry (default 'gray').",
)

args = parser.parse_args()


def _parse_panel_line_values(raw_values, flag_name):
    """Parse a --panel_vertical/--panel_horizontal value list: floats, with
    'none'/'skip'/'' as an explicit per-panel sentinel meaning "no line here"."""
    if raw_values is None:
        return None
    parsed = []
    for raw in raw_values:
        if str(raw).strip().lower() in ("none", "skip", ""):
            parsed.append(None)
        else:
            try:
                parsed.append(float(raw))
            except ValueError:
                parser.error(f"{flag_name} values must be numbers or 'none' to skip a panel, got '{raw}'")
    return parsed


args.panel_vertical = _parse_panel_line_values(args.panel_vertical, "--panel_vertical")
args.panel_horizontal = _parse_panel_line_values(args.panel_horizontal, "--panel_horizontal")

if args.panels is None and args.x is None:
    parser.error("the following arguments are required: -x/--x (or use --panels)")

if args.panels is not None:
    if args.panel_rangex is not None and len(args.panel_rangex) != 2 * len(args.panels):
        parser.error(
            f"--panel_rangex must provide exactly 2 values per --panels entry "
            f"({2 * len(args.panels)} expected, got {len(args.panel_rangex)})."
        )
    if args.panel_title is not None and len(args.panel_title) != len(args.panels):
        parser.error(
            f"--panel_title must provide exactly one value per --panels entry "
            f"({len(args.panels)} expected, got {len(args.panel_title)})."
        )
    for flag_name, values in (
        ("--panel_vertical", args.panel_vertical),
        ("--panel_vertical_label", args.panel_vertical_label),
        ("--panel_vertical_style", args.panel_vertical_style),
        ("--panel_vertical_color", args.panel_vertical_color),
        ("--panel_horizontal", args.panel_horizontal),
        ("--panel_horizontal_label", args.panel_horizontal_label),
        ("--panel_horizontal_style", args.panel_horizontal_style),
        ("--panel_horizontal_color", args.panel_horizontal_color),
    ):
        if values is not None and len(values) != len(args.panels):
            parser.error(
                f"{flag_name} must provide exactly one value per --panels entry "
                f"({len(args.panels)} expected, got {len(values)})."
            )
    if args.variables is not None:
        rprint(
            "[yellow]Warning:[/yellow] --panels overrides --variables for panel layout; --variables will be ignored."
        )
elif any(
    v is not None
    for v in (
        args.panel_vertical,
        args.panel_vertical_label,
        args.panel_vertical_style,
        args.panel_vertical_color,
        args.panel_horizontal,
        args.panel_horizontal_label,
        args.panel_horizontal_style,
        args.panel_horizontal_color,
    )
):
    parser.error("--panel_vertical/--panel_horizontal (and their _label/_style/_color variants) require --panels")

if args.compact:
    if args.panels is None:
        parser.error("--compact requires --panels to define the concatenated regions")
    if args.panel_rangex is None:
        parser.error("--compact requires --panel_rangex to define each panel's x range for concatenation")
    if args.boxplot:
        parser.error("--compact does not support --boxplot")
    if args.panel_labelx is not None and len(args.panel_labelx) != len(args.panels):
        parser.error(
            f"--panel_labelx must provide exactly one value per --panels entry "
            f"({len(args.panels)} expected, got {len(args.panel_labelx)})."
        )
    if args.panel_title is not None:
        rprint(
            "[yellow]Warning:[/yellow] --panel_title is ignored with --compact — the figure keeps the "
            "same size as a single-panel plot, which leaves no room for per-panel headers; use --title "
            "for the one shared figure title instead."
        )


def _resolve_operation_func(op):
    ops = {
        "mean": lambda arr: arr.mean(),
        "average": lambda arr: arr.mean(),
        "sum": lambda arr: arr.sum(),
        "max": lambda arr: arr.max(),
        "min": lambda arr: arr.min(),
    }
    return ops.get(op.lower() if op else "mean")


def _row_index_with_data(subset, col):
    """Index of the first row in `subset` where `col` holds real data rather
    than a NaN placeholder. Some pipelines emit one row per scanned variable
    within an otherwise shared selection (e.g. one row per --panels column),
    leaving every other per-variable column NaN in that row -- blindly taking
    row 0 can grab a different row's placeholder instead of this column's
    actual array. Falls back to row 0 if every row is a NaN placeholder."""
    for i, value in enumerate(subset[col].values):
        if isinstance(value, (list, np.ndarray)):
            return i
        if not (isinstance(value, float) and np.isnan(value)):
            return i
    return 0


def run_compact_mode(df, configs, names, default_operation_config):
    """Render --panels as a single set of shared axes with concatenated x ranges
    (--compact) instead of one subplot column per panel: each panel's x range is
    shifted so it sits directly after the previous one, a dark vertical line marks
    every boundary, and each panel keeps its own x ticks and x-axis label."""
    operation = args.operation or args.default_operation or default_operation_config or "mean"
    if operation.lower() not in ["mean", "average", "sum", "max", "min"]:
        rprint(
            f"[red]Error:[/red] Invalid operation: {operation}. Supported: mean, average, sum, max, min."
        )
        return
    op_func = _resolve_operation_func(operation)
    _operation_default_warned = False

    def _warn_operation_default():
        # Only fires once a panel actually needs --operation to reduce a
        # per-event array; already-reduced (scalar) panels never call this,
        # so they aren't warned about needing an operation they don't use.
        nonlocal _operation_default_warned
        if args.operation is None and not _operation_default_warned:
            _operation_default_warned = True
            source = "flag" if args.default_operation else "config"
            rprint(
                f"[yellow]Warning:[/yellow] No operation specified. Using default from {source}: {operation}."
            )

    panel_ranges = [
        (args.panel_rangex[2 * i], args.panel_rangex[2 * i + 1]) for i in range(len(args.panels))
    ]
    panel_widths = [hi - lo for lo, hi in panel_ranges]
    offsets = []
    cum = 0.0
    for w in panel_widths:
        offsets.append(cum)
        cum += w
    total_width = cum

    selected_plot_type = getattr(args, "plot_type", None) or "scatter_points"
    plot_kwargs_base = resolve_plot_kwargs(selected_plot_type)
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["C0"])

    for kdx, (config, name) in enumerate(zip(configs, names)):
        fig, ax_current = plt.subplots(
            nrows=1,
            ncols=1,
            figsize=get_common_figsize(ncols=1, nrows=1),
            constrained_layout=False,
        )
        apply_common_figure_margins(fig)
        # Reserve extra room below the axes for the per-panel x-axis label row
        # that sits under the normal tick labels (see ax_current.text(...,
        # va="top") below), which the fixed figure margins don't allocate for.
        extra_bottom_in = 0.42
        fig.subplots_adjust(
            bottom=fig.subplotpars.bottom + extra_bottom_in / fig.get_figheight()
        )

        if config is not None and name is None and args.iterable != "Config":
            df_config = df[(df["Config"] == config)]
        elif config is None and name is not None and args.iterable != "Name":
            df_config = df[(df["Name"] == name)]
        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]
        else:
            df_config = df.copy()

        iterable_values = (
            df_config[args.iterable].unique() if args.iterable is not None else [None]
        )
        iterable_colors = {
            iterable_value: (
                map_iterable_color(iterable_value, getattr(args, "iterable_color_mapping", None))
                or color_cycle[j % len(color_cycle)]
            )
            for j, iterable_value in enumerate(iterable_values)
        }

        tick_positions = []
        tick_labels = []

        for pidx, x_col in enumerate(args.panels):
            lo, hi = panel_ranges[pidx]
            offset = offsets[pidx]
            panel_is_integer = None

            for iterable_value in iterable_values:
                if iterable_value is not None:
                    df_iterable = df_config[df_config[args.iterable] == iterable_value]
                else:
                    df_iterable = df_config.copy()

                subset = filter_dataframe(df_iterable, args)
                row_idx = _row_index_with_data(subset, x_col)
                x = subset[x_col].values[row_idx]
                y = subset[args.y].values[row_idx]

                if isinstance(x, list):
                    continue

                # Some datafiles (e.g. already-reduced/fiducial variants) store a
                # single x value per column -- an already-fixed cut, not a scan --
                # instead of a per-event array. There's only one "bin" in that
                # case: the point sits at that fixed x, and y (if still an array
                # of per-event values) is collapsed into it with --operation same
                # as any other bin; if y is also already a single value there's
                # nothing left to reduce, so --operation isn't needed at all.
                x_is_scalar = np.ndim(x) == 0
                y_is_scalar = np.ndim(y) == 0

                if not x_is_scalar and y_is_scalar:
                    rprint(
                        f"[yellow]Warning:[/yellow] '{x_col}' is an array but '{args.y}' is a single value; "
                        "can't bin one against the other. Skipping."
                    )
                    continue

                if x_is_scalar:
                    bin_centers = np.asarray([float(x)])
                elif np.issubdtype(x.dtype, np.integer):
                    if x.size == 0:
                        rprint(
                            f"[yellow]Warning:[/yellow] No x values found for panel '{x_col}'. Skipping."
                        )
                        continue
                    bins = np.arange(x.min(), x.max() + 1.5) - 0.5
                    bin_centers = np.arange(x.min(), x.max() + 1)
                    if args.reduce and len(bins) > 8:
                        bins = bins[::2]
                        bin_centers = bin_centers[::2]
                    if bins[-1] < bin_centers[-1]:
                        bin_centers = bin_centers[:-1]
                    if panel_is_integer is None:
                        panel_is_integer = True
                else:
                    if x.size == 0:
                        rprint(
                            f"[yellow]Warning:[/yellow] No x values found for panel '{x_col}'. Skipping."
                        )
                        continue
                    bins = np.linspace(
                        x.min(), x.max(), args.bins if args.bins is not None else nbins + 1
                    )
                    bin_centers = (bins[:-1] + bins[1:]) / 2
                    if panel_is_integer is None:
                        panel_is_integer = False

                if x_is_scalar and y_is_scalar:
                    # Nothing to reduce -- the single stored value is the point.
                    y_scatter = np.asarray([float(y)])
                elif x_is_scalar:
                    # Single fixed x (no scan): collapse the whole per-event y
                    # array into the one point via --operation.
                    _warn_operation_default()
                    y_scatter = np.asarray([op_func(y)])
                else:
                    mask_func = (
                        (lambda i: x >= bins[i])
                        if args.threshold
                        else (lambda i: (x >= bins[i]) & (x < bins[i + 1]))
                    )
                    _warn_operation_default()
                    y_scatter = np.array([op_func(y[mask_func(i)]) for i in range(len(bins) - 1)])

                # Concatenation requires each panel's data to stay within its own
                # region -- trim to [lo, hi] before shifting so it can't bleed
                # into a neighboring panel's segment of the shared axis.
                keep = (bin_centers >= lo) & (bin_centers <= hi)
                plot_x = bin_centers[keep] - lo + offset
                plot_y = y_scatter[keep]
                if plot_x.size == 0:
                    continue

                plot_data(
                    args,
                    ax_current,
                    plot_x,
                    y=plot_y,
                    label=(
                        map_iterable_label(
                            iterable_value,
                            args.iterable,
                            getattr(args, "iterable_mapping", None),
                            len(iterable_values),
                        )
                        if args.iterable is not None and pidx == 0
                        else None
                    ),
                    color=iterable_colors[iterable_value],
                    marker="o" if selected_plot_type == "scatter_points" else None,
                    **plot_kwargs_base,
                )

            # Build this panel's own ticks in its own value range, placed at
            # their shifted (concatenated) position on the shared axis.
            locator = MaxNLocator(
                nbins=4 if args.reduce else 6,
                integer=bool(panel_is_integer),
                steps=[1, 2, 2.5, 5, 10],
            )
            raw_ticks = locator.tick_values(lo, hi)
            raw_ticks = raw_ticks[(raw_ticks >= lo) & (raw_ticks <= hi)]
            for tick_val in raw_ticks:
                tick_positions.append(tick_val - lo + offset)
                tick_labels.append(
                    str(int(round(tick_val))) if panel_is_integer else f"{tick_val:g}"
                )

            if pidx > 0:
                ax_current.axvline(offset, color="black", linewidth=1.4, zorder=10)

            if args.panel_vertical is not None and args.panel_vertical[pidx] is not None:
                shifted_v = args.panel_vertical[pidx] - lo + offset
                draw_vertical_lines(
                    ax_current,
                    [shifted_v],
                    labels=[args.panel_vertical_label[pidx]] if args.panel_vertical_label is not None else None,
                    styles=[args.panel_vertical_style[pidx]] if args.panel_vertical_style is not None else None,
                    colors=[args.panel_vertical_color[pidx]] if args.panel_vertical_color is not None else None,
                    fontsize=linelabelfontsize,
                )

            if args.panel_horizontal is not None and args.panel_horizontal[pidx] is not None:
                h_value = args.panel_horizontal[pidx]
                h_color = args.panel_horizontal_color[pidx] if args.panel_horizontal_color is not None else "gray"
                h_style = args.panel_horizontal_style[pidx] if args.panel_horizontal_style is not None else "--"
                # Scoped to this panel's own segment only -- a full-width axhline
                # would incorrectly bleed into the neighboring panels sharing
                # this axis.
                ax_current.hlines(
                    h_value,
                    offset,
                    offset + panel_widths[pidx],
                    colors=h_color,
                    linestyles=h_style,
                    linewidth=1,
                    zorder=5,
                )
                h_label = args.panel_horizontal_label[pidx] if args.panel_horizontal_label is not None else None
                if h_label:
                    ax_current.text(
                        offset + panel_widths[pidx] * 0.97,
                        h_value,
                        h_label,
                        ha="right",
                        va="bottom",
                        fontsize=linelabelfontsize,
                        color=h_color,
                        clip_on=True,
                    )

            if args.panel_labelx is not None:
                label_text = args.panel_labelx[pidx]
            elif args.labelx is not None:
                label_text = args.labelx
            else:
                label_text = resolve_axis_label(None, x_col, df_config)
            ax_current.text(
                offset + panel_widths[pidx] / 2,
                -0.11,
                label_text,
                transform=ax_current.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=xsublabelfontsize,
                clip_on=False,
            )

        ax_current.set_xlim(0, total_width)
        ax_current.set_xticks(tick_positions)
        ax_current.set_xticklabels(tick_labels)
        ax_current.set_xlabel("")

        ax_current.set_ylabel(resolve_axis_label(args.labely, args.y, df_config))
        if args.rangey is not None:
            ax_current.set_ylim(args.rangey[0], args.rangey[1])

        # Only the y-axis formatter is applied here -- reformatting "both" would
        # replace the fixed per-panel tick labels set above with a numeric
        # formatter keyed to the shared (shifted) coordinate, not the original
        # per-panel values shown to the user.
        apply_scientific_threshold_formatter(ax_current, threshold=0.1, axis="y")

        if args.logy:
            ax_current.semilogy()

        legend_title = args.labelz if args.labelz is not None else args.iterable
        apply_legend_style(
            ax_current,
            title=legend_title,
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

        plot_title = make_title_from_args(args)
        if plot_title:
            add_centered_suptitle(fig, plot_title, fontsize=titlefontsize)

        apply_note_to_figure(fig, getattr(args, "note", None))

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
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)


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

    if args.multiply is not None:
        df[args.y] = df[args.y].apply(
            lambda v: np.asarray(v) * args.multiply if v is not None else v
        )
        if f"{args.y}Error" in df.columns:
            df[f"{args.y}Error"] = df[f"{args.y}Error"].apply(
                lambda v: np.asarray(v) * args.multiply if v is not None else v
            )

    # Select the entries in the dataframe with with name matching args.names and nake a plot for each iterable
    if args.panels is not None:
        ncols = len(args.panels)
    elif args.variables is None:
        ncols = 1
    else:
        ncols = len(args.variables)

    configs, names = prepare_import(args)
    configs = configs if (configs is not None and args.iterable != "Config") else [None]
    names = names if (names is not None and args.iterable != "Name") else [None]

    if args.compact:
        run_compact_mode(df, configs, names, _operation_config)
        return

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
        if args.panels is not None:
            variables = [None] * len(args.panels)
        else:
            variables = args.variables if args.variables is not None else [None]
        iterables = args.iterable if args.iterable is not None else [None]
        subset_by_variable = {}

        iterable_values = (
            df_config[args.iterable].unique() if args.iterable is not None else [None]
        )

        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables),
            enumerate(iterable_values),
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
            subset_by_variable.setdefault(idx, subset)
            x_col = args.panels[idx] if args.panels is not None else args.x
            row_idx = _row_index_with_data(subset, x_col)
            x = subset[x_col].values[row_idx]  # Convert to NumPy array
            y = subset[args.y].values[row_idx]  # Convert to NumPy array

            # Sample the y values according to the specified x values and create a boxplot of the y values for each x bin
            # If the x values are int create bins for each int value, otherwise create bins according to the specified number of bins
            if isinstance(x, list):
                continue

            # Some datafiles (e.g. already-reduced/fiducial variants) store a
            # single x value per column -- an already-fixed cut, not a scan --
            # instead of a per-event array. There's only one "bin" in that
            # case: the point sits at that fixed x, and y (if still an array
            # of per-event values) is collapsed into it with --operation same
            # as any other bin; if y is also already a single value there's
            # nothing left to reduce, so --operation isn't needed at all.
            x_is_scalar = np.ndim(x) == 0
            y_is_scalar = np.ndim(y) == 0

            if not x_is_scalar and y_is_scalar:
                rprint(
                    f"[yellow]Warning:[/yellow] '{x_col}' is an array but '{args.y}' is a single value; "
                    "can't bin one against the other. Skipping."
                )
                continue

            if x_is_scalar:
                if args.boxplot and y_is_scalar:
                    rprint(
                        f"[yellow]Warning:[/yellow] --boxplot needs array data; '{x_col}'/'{args.y}' are "
                        "already single values. Skipping."
                    )
                    continue
                bin_centers = np.asarray([float(x)])

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
                if x_is_scalar:
                    # Single fixed x (no scan): one box, showing the spread of
                    # the still-per-event y array at that position.
                    boxplot_data = [y]
                    box_widths = None
                else:
                    if args.threshold:
                        # If threshold is set, use x values as thresholds instead of bins
                        boxplot_data = [y[(x >= bins[i])] for i in range(len(bins) - 1)]
                    else:
                        boxplot_data = [
                            y[(x >= bins[i]) & (x < bins[i + 1])]
                            for i in range(len(bins) - 1)
                        ]
                    box_widths = (
                        np.diff(bins) * 0.8
                        if np.issubdtype(x.dtype, np.integer)
                        else None
                    )
                plot_data(
                    args,
                    ax_current,
                    bin_centers,
                    y=boxplot_data,
                    label=f"Median {args.y}",
                    plot_type="boxplot",
                    positions=bin_centers,
                    widths=box_widths,
                    showfliers=False,
                )
            else:
                if x_is_scalar and y_is_scalar:
                    # Nothing to reduce -- the single stored value is the point.
                    y_scatter = [float(y)]
                else:
                    operation = args.operation or args.default_operation or _operation_config or "mean"
                    if operation.lower() not in ["mean", "average", "sum", "max", "min"]:
                        rprint(
                            f"[red]Error:[/red] Invalid operation: {operation}. Supported: mean, average, sum, max, min."
                        )
                        return

                    op_func = _resolve_operation_func(operation)

                    if x_is_scalar:
                        # Single fixed x (no scan): collapse the whole
                        # per-event y array into the one point via --operation.
                        y_scatter = [op_func(y)]
                    else:
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
                            map_iterable_label(
                                iterable,
                                args.iterable,
                                getattr(args, "iterable_mapping", None),
                                len(iterable_values),
                            )
                            if args.iterable is not None
                            else f"{args.y} vs {args.x}"
                        )
                    ),
                    color=(
                        map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
                        if args.iterable is not None
                        else None
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
                if args.panels is not None and args.panel_title is not None:
                    plot_subtitle = args.panel_title[idx]
                else:
                    plot_subtitle = make_subtitle_from_args(args, idx)
                ax_current.set_title(
                    plot_subtitle,
                    fontsize=subtitlefontsize,
                )

            label_subset = subset_by_variable.get(idx, df)
            x_col_for_label = args.panels[idx] if args.panels is not None else args.x
            ax_current.set_xlabel(resolve_axis_label(args.labelx, x_col_for_label, label_subset))
            (
                ax_current.set_ylabel(resolve_axis_label(args.labely, args.y, label_subset))
                if idx == 0
                else None
            )
            # Limit the number of x ticks to 10 for readability by removing some of the ticks and their labels if there are more than 10
            if len(ax_current.get_xticks()) > 10 and args.reduce:
                xticks = ax_current.get_xticks()
                step = max(1, len(xticks) // 10)
                ax_current.set_xticks(xticks[::step])

            if args.panels is not None and args.panel_rangex is not None:
                ax_current.set_xlim(args.panel_rangex[2 * idx], args.panel_rangex[2 * idx + 1])
            elif args.rangex is None:
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
                legend_title = args.labelz if args.labelz is not None else args.iterable
                apply_legend_style(
                    ax_current,
                    title=legend_title,
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

            if args.panels is not None:
                if args.panel_horizontal is not None and args.panel_horizontal[idx] is not None:
                    draw_horizontal_lines(
                        ax_current,
                        [args.panel_horizontal[idx]],
                        labels=[args.panel_horizontal_label[idx]] if args.panel_horizontal_label is not None else None,
                        styles=[args.panel_horizontal_style[idx]] if args.panel_horizontal_style is not None else None,
                        colors=[args.panel_horizontal_color[idx]] if args.panel_horizontal_color is not None else None,
                        fontsize=linelabelfontsize,
                    )
                if args.panel_vertical is not None and args.panel_vertical[idx] is not None:
                    draw_vertical_lines(
                        ax_current,
                        [args.panel_vertical[idx]],
                        labels=[args.panel_vertical_label[idx]] if args.panel_vertical_label is not None else None,
                        styles=[args.panel_vertical_style[idx]] if args.panel_vertical_style is not None else None,
                        colors=[args.panel_vertical_color[idx]] if args.panel_vertical_color is not None else None,
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
        if args.panels is not None and args.panel_title is not None and args.title is None:
            # Per-panel titles already label each subplot; skip the shared figure
            # title by default so it doesn't overlap the top row of panel titles.
            plot_title = None
        else:
            plot_title = make_title_from_args(args)
        if plot_title:
            add_centered_suptitle(fig, plot_title, fontsize=titlefontsize)
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
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)

if __name__ == "__main__":
    main()
