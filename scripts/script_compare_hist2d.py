#!/usr/bin/env python3

"""
Script 3: Simple Heatmap Plot with DUNE Style
Demonstrates basic heatmap plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_subtitle_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_scientific_threshold_formatter, plot_data, create_common_subplots, apply_note_to_figure, add_centered_suptitle, draw_vertical_lines, draw_horizontal_lines, draw_squares, draw_lines, place_point_label

from common_args import add_common_args, resolve_axis_label

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
        "z",
        "percentile",
        "iterable",
        "select",
        "save_values",
        "remove_value",
        "bins",
        "labelx",
        "labely",
        "labelz",
        "rangex",
        "rangey",
        "rangez",
        "logz",
        "density",
        "norm",
        "zoom",
        "matchx",
        "matchy",
        "horizontal",
        "horizontal_label",
        "horizontal_style",
        "horizontal_color",
        "vertical",
        "vertical_label",
        "vertical_style",
        "vertical_color",
        "square",
        "square_label",
        "square_style",
        "square_color",
        "line",
        "line_label",
        "line_style",
        "line_color",
        "title",
        "output",
        "subfolder",
        "point",
        "point_label",
        "note",
        "debug",
    ],
    overrides={
        "datafile": {"required": True},
        "bins": {"default": nbins, "help": "Number of bins for the histogram"},
        "percentile": {"default": [0, 100]},
        "density": {"help": "Normalize histogram to density"},
        "zoom": {"help": "Zoom into overlapping percentile ranges"},
    },
)

parser.add_argument(
    "--diagonal",
    action="store_true",
    help="Draw diagonal line",
    default=False,
)



args = parser.parse_args()


def normalize_hist2d(h, mode):
    """Normalize a 2D histogram (as returned by ax.hist2d) with shape (nx, ny).

    - "global": the whole histogram sums to 1.
    - "horizontal": each y-slice sums to 1 across x (axis 0).
    - "vertical": each x-slice sums to 1 across y (axis 1).
    - "combined": each bin is divided by the sum of its own row total
      (horizontal, axis 0) and column total (vertical, axis 1).
    """
    if mode is None:
        return h

    h = h.astype(float)
    if mode == "global":
        total = h.sum()
        return h / total if total != 0 else h
    if mode == "horizontal":
        sums = h.sum(axis=0, keepdims=True)
        sums[sums == 0] = 1
        return h / sums
    if mode == "vertical":
        sums = h.sum(axis=1, keepdims=True)
        sums[sums == 0] = 1
        return h / sums
    if mode == "combined":
        horizontal_sums = h.sum(axis=0, keepdims=True)
        vertical_sums = h.sum(axis=1, keepdims=True)
        sums = horizontal_sums + vertical_sums
        sums[sums == 0] = 1
        return h / sums
    raise ValueError(f"Unknown norm mode: {mode}")


def is_integer_valued(arr):
    """True if arr's finite entries are all whole numbers (integer dtype, or floats with no fractional part)."""
    if np.issubdtype(arr.dtype, np.integer):
        return arr.size > 0
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return False
    return np.allclose(finite, np.round(finite))


def integer_bin_edges(vmin, vmax):
    """Bin edges giving one bin per integer value between vmin and vmax (inclusive), i.e. integer voxels."""
    lo = int(np.floor(vmin))
    hi = int(np.ceil(vmax))
    return np.arange(lo, hi + 2) - 0.5


def main():
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    if args.variables is not None and args.iterable is not None:
        rprint(
            "Both variables and iterable arguments provided. Please provide only one of them."
        )
        return
    ncols = (
        len(args.variables)
        if args.variables is not None
        else len(df[args.iterable].unique()) if args.iterable is not None else 1
    )

    print(f"Number of unique variables for plotting: {ncols}")

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        print(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = create_common_subplots(
            nrows=1,
            ncols=ncols,
        )
        if config is None:
            df_config = df
        else:
            df_config = df[(df["Config"] == config)]
        if name is not None:
            df_config = df_config[(df_config["Name"] == name)]

        variables = args.variables if args.variables is not None else [None]
        iterables = (
            df_config[args.iterable].unique() if args.iterable is not None else [None]
        )
        subset_by_idx = {}
        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables),
            enumerate(iterables) if args.iterable is not None else enumerate([None]),
        ):

            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx if args.variables is not None else jdx]

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
                        f"[red]Error:[/red] Filtering for variable: {variable} and iterable: {iterable} not supported simultaneously."
                    )
                return
            else:
                df_iterable = df_config.copy()

            subset = filter_dataframe(df_iterable, args)
            subset_by_idx[(idx, jdx)] = subset

            ranges = []
            if len(subset[args.x].values) > 1:
                rprint(
                    f"[red]Error:[/red] Multiple entries found for {variable if variable is not None else f'{args.iterable}={iterable}'}"
                )
                return

            x = np.array(subset[args.x].values[0])
            y = np.array(subset[args.y].values[0])
            z = np.array(subset[args.z].values[0]) if args.z is not None else None

            if z is None:
                valid_mask = np.isfinite(x) & np.isfinite(y)
                if not valid_mask.all():
                    n_dropped = (~valid_mask).sum()
                    rprint(
                        f"[yellow]Warning:[/yellow] Dropping {n_dropped} non-finite entries out of {len(valid_mask)}"
                    )
                x = x[valid_mask]
                y = y[valid_mask]

            x_range = [
                np.percentile(x, args.percentile[0]),
                np.percentile(x, args.percentile[1]),
            ]
            y_range = [
                np.percentile(y, args.percentile[0]),
                np.percentile(y, args.percentile[1]),
            ]
            if idx == 0:
                ranges = [x_range, y_range]

            elif args.zoom:
                if x_range[0] > ranges[0][0]:
                    ranges[0][0] = x_range[0]
                if x_range[1] < ranges[0][1]:
                    ranges[0][1] = x_range[1]
                if y_range[0] > ranges[1][0]:
                    ranges[1][0] = y_range[0]
                if y_range[1] < ranges[1][1]:
                    ranges[1][1] = y_range[1]

            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx if args.variables is not None else jdx]

            if z is not None:
                mappable = plot_data(
                    args,
                    ax_current,
                    x,
                    y=y,
                    plot_type="image",
                    z=z,
                )
                if args.rangez is not None:
                    mappable.set_clim(*args.rangez)
                cbar = fig.colorbar(mappable, ax=ax_current)
                z_label = resolve_axis_label(args.labelz, args.z, subset)
                cbar.set_label(z_label if not args.logz else f"{z_label} (log scale)")
            else:
                hist2d_kwargs = {"range": (x_range, y_range)}
                if is_integer_valued(x) and is_integer_valued(y):
                    x_edges = integer_bin_edges(x_range[0], x_range[1])
                    y_edges = integer_bin_edges(y_range[0], y_range[1])
                    hist2d_kwargs["bins"] = [x_edges, y_edges]
                    if args.debug:
                        rprint(
                            f"[blue]Info:[/blue] Integer-valued x/y detected; using integer-width bins "
                            f"({len(x_edges) - 1} x {len(y_edges) - 1})"
                        )
                hist2d = plot_data(
                    args,
                    ax_current,
                    x,
                    y=y,
                    plot_type="hist2d",
                    **hist2d_kwargs,
                )
                if args.norm is not None:
                    h_norm = normalize_hist2d(hist2d[0], args.norm)
                    hist2d[3].set_array(h_norm.T)
                if not args.logz:
                    hist2d[3].set_array(
                        np.ma.masked_where(
                            hist2d[3].get_array() == 0, hist2d[3].get_array()
                        )
                    )
                    hist2d[3].set_clim(0, hist2d[3].get_array().max())
                if args.rangez is not None:
                    hist2d[3].set_clim(*args.rangez)
                cbar = fig.colorbar(hist2d[3], ax=ax_current)

            if args.diagonal:
                ax_current.plot(
                    x_range,
                    x_range,
                    color="k" if args.logz else "white",
                    linestyle="--",
                )
                ax_current.set_xlim(ranges[0])
                ax_current.set_ylim(ranges[0])
        if z is None:
            if args.norm is not None:
                norm_labels = {
                    "global": "Normalized Counts",
                    "horizontal": "Normalized Counts (horizontal)",
                    "vertical": "Normalized Counts (vertical)",
                    "combined": "Normalized Counts (combined)",
                }
                base_label = norm_labels[args.norm]
            elif args.density:
                base_label = "Density"
            else:
                base_label = "Counts"
            cbar.set_label(base_label if not args.logz else f"{base_label} (log scale)")
        cbar.ax.yaxis.set_label_position("right")  # Move label to the left

        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables),
            enumerate(iterables) if args.iterable is not None else enumerate([None]),
        ):
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx if args.variables is not None else jdx]

            if ncols > 1:
                plot_subtitle = make_subtitle_from_args(
                    args, iterables, plot_type="hist2d", idx=jdx
                )
                ax_current.set_title(
                    plot_subtitle,
                    fontsize=subtitlefontsize,
                )

            label_subset = subset_by_idx.get((idx, jdx), df)
            _xlabel = resolve_axis_label(args.labelx, args.x, label_subset)
            if _xlabel == "Time":
                _xlabel = r"Time ($\mu$s)"
            ax_current.set_xlabel(_xlabel)
            ax_current.set_ylabel(resolve_axis_label(args.labely, args.y, label_subset)) if idx == 0 else None
            if args.matchx:
                ax_current.set_xlim(ranges[0])
            if args.matchy:
                ax_current.set_ylim(ranges[1])
            if args.rangex is not None:
                ax_current.set_xlim(args.rangex)
            if args.rangey is not None:
                ax_current.set_ylim(args.rangey)

            apply_scientific_threshold_formatter(ax_current, threshold=0.1, axis="both")

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

            square_quads = parse_square_quads(getattr(args, "square", None))
            square_labels, square_label_warning = normalize_square_labels(
                getattr(args, "square_label", None), len(square_quads)
            )
            if square_label_warning is not None:
                rprint(f"[yellow]Warning:[/yellow] {square_label_warning}")

            draw_squares(
                ax_current,
                square_quads,
                labels=square_labels,
                styles=getattr(args, "square_style", None),
                colors=getattr(args, "square_color", None),
                fontsize=linelabelfontsize,
            )

            line_segments = parse_line_segments(getattr(args, "line", None))
            line_labels, line_label_warning = normalize_line_labels(
                getattr(args, "line_label", None), len(line_segments)
            )
            if line_label_warning is not None:
                rprint(f"[yellow]Warning:[/yellow] {line_label_warning}")

            draw_lines(
                ax_current,
                line_segments,
                labels=line_labels,
                styles=getattr(args, "line_style", None),
                colors=getattr(args, "line_color", None),
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
                    ax_current.scatter(point_x, point_y, color="gray", s=40, zorder=6)
                    if point_labels is not None:
                        place_point_label(ax_current, point_x, point_y, point_labels[point_idx], fontsize=linelabelfontsize)

        # Set title
        plot_title = make_title_from_args(args)
        add_centered_suptitle(fig, f"{plot_title}", fontsize=titlefontsize)
        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="hist2d.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)


if __name__ == "__main__":
    main()
