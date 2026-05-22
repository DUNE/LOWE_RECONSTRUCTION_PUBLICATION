#!/usr/bin/env python3

"""
Script: image-style background with contour overlays in DUNE style.

This macro follows the loading/filtering/output structure of
`script_compare_hist2d.py`, but it expects gridded image data instead of raw
point clouds. Each selected dataframe row should provide x, y, and z arrays,
where z is a 2D image and contours are extracted directly from z.

Expected input dataframe structure
---------------------------------
A typical dataframe row should look like:

    pd.DataFrame(
        [
            {
                "Config": "hd_1x2x6",
                "Name": "marley_official",
                "Variable": "electron",
                "Plane": -1,
                "XGrid": np.array([0.0, 0.5, 1.0]),
                "YGrid": np.array([0.0, 1.0]),
                "ZGrid": np.array(
                    [
                        [1.0, 2.0, 1.0],
                        [0.5, 3.0, 0.2],
                    ]
                ),
            },
            {
                "Config": "hd_1x2x6_centralAPA",
                "Name": "marley_official",
                "Variable": "electron",
                "Plane": -1,
                "XGrid": np.array([0.0, 0.5, 1.0]),
                "YGrid": np.array([0.0, 1.0]),
                "ZGrid": np.array(
                    [
                        [0.4, 1.8, 0.6],
                        [0.2, 2.2, 0.1],
                    ]
                ),
            },
        ]
    )

The macro draws the z matrix as an image-like background and overlays contours
from the same z values. When `--operation squared_sum` is used, the combined
contour/background is computed bin-by-bin as `sqrt(sum_i(z_i^2))`.
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from matplotlib.lines import Line2D
from rich import print as rprint

from lib import *
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_subtitle_from_args, make_title_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_scientific_threshold_formatter, apply_legend_style, create_common_subplots, apply_note_to_figure, place_vertical_label, place_horizontal_label, place_point_label

from lib.selection import filter_dataframe
from common_args import add_common_args


parser = argparse.ArgumentParser(
    description="Plot configuration contours on top of a gridded image background"
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
        "labelx",
        "labely",
        "labelz",
        "rangex",
        "rangey",
        "logz",
        "density",
        "zoom",
        "matchx",
        "matchy",
        "horizontal",
        "vertical",
        "point",
        "point_label",
        "note",
        "title",
        "output",
        "debug",
    ],
    overrides={
        "datafile": {"required": True},
        "x": {"required": True, "help": "Column name for x-grid data"},
        "y": {"required": True, "help": "Column name for y-grid data"},
        "z": {
            "required": True,
            "help": "Column name for z-grid values used for the image and contours",
        },
        "percentile": {
            "default": [0, 100],
            "help": "Retained for CLI compatibility; grid plotting uses the explicit x/y coordinates",
        },
        "iterable": {"help": "List of iterable parameters to produce plots"},
        "select": {
            "help": "If provided, filter plots according to select columns and values in save_values"
        },
        "save_values": {
            "help": "If iterable value is provided, save plots for which iterable equals this value"
        },
        "density": {"help": "Normalize each z image to unit sum before plotting/combining"},
        "zoom": {
            "help": "Retained for CLI compatibility; grid plotting uses the explicit x/y coordinates"
        },
    },
)


parser.add_argument(
    "--diagonal",
    action="store_true",
    help="Draw diagonal line",
    default=False,
)

parser.add_argument(
    "--operation",
    type=str,
    default=None,
    choices=["squared_sum"],
    help="Combine configuration z-grids before drawing a combined contour",
)

parser.add_argument(
    "--combined_contours_only",
    action="store_true",
    default=False,
    help="Only draw the combined contour when --operation squared_sum is used",
)

parser.add_argument(
    "--combined_color",
    type=str,
    default="black",
    help="Color for the combined contour line",
)

parser.add_argument(
    "--combined_linestyle",
    type=str,
    default="-",
    help="Linestyle for the combined contour line",
)

parser.add_argument(
    "--combined_linewidth",
    type=float,
    default=None,
    help="Line width for the combined contour line",
)

parser.add_argument(
    "--combined_alpha",
    type=float,
    default=1.0,
    help="Alpha for the combined contour line",
)

parser.add_argument(
    "--combined_label",
    type=str,
    default="Combined",
    help="Legend label for the combined contour line",
)

parser.add_argument(
    "--background",
    type=str,
    default="all",
    choices=["all", "combined", "first", "none"],
    help="Source for the background image",
)

parser.add_argument(
    "--contour_sigmas",
    nargs="+",
    type=float,
    default=[1.0, 2.0, 3.0],
    help="Sigma-equivalent contour levels to draw",
)

parser.add_argument(
    "--contour_linestyles",
    nargs="+",
    type=str,
    default=None,
    help="Linestyles for each sigma contour level, in the same order as --contour_sigmas",
)

parser.add_argument(
    "--contour_level_mode",
    type=str,
    default="z_values",
    choices=["z_values", "sigma_probability"],
    help="How contour levels are computed: exact z values or cumulative sigma probability thresholds",
)

parser.add_argument(
    "--contour_linewidth",
    type=float,
    default=2.0,
    help="Line width for contour overlays",
)

parser.add_argument(
    "--contour_alpha",
    type=float,
    default=0.95,
    help="Alpha for contour overlays",
)

parser.add_argument(
    "--contour_smoothing_sigma",
    type=float,
    default=0.0,
    help="Gaussian smoothing sigma applied to z-grid before contour extraction",
)

parser.add_argument(
    "--background_smoothing_sigma",
    type=float,
    default=0.0,
    help="Gaussian smoothing sigma applied to z-grid before drawing the background image",
)

parser.add_argument(
    "--contour_min_vertices",
    type=int,
    default=0,
    help="Minimum number of vertices for a contour segment to be kept (filters tiny discontinuities)",
)

parser.add_argument(
    "--nan_fill",
    type=str,
    default="interpolate",
    choices=["interpolate", "nearest", "zero", "none"],
    help="How to fill NaN values in z-grids before plotting/contouring",
)

parser.add_argument(
    "--nan_interp_method",
    type=str,
    default="linear",
    choices=["cubic", "linear"],
    help="Interpolation method used when --nan_fill interpolate",
)



args = parser.parse_args()


SIGMA_TO_CUMULATIVE = {
    1.0: 0.3934693402873666,
    2.0: 0.8646647167633873,
    3.0: 0.9888910034617577,
}


def sigma_to_cumulative_probability(sigma):
    rounded = round(float(sigma), 6)
    if rounded in SIGMA_TO_CUMULATIVE:
        return SIGMA_TO_CUMULATIVE[rounded]
    return 1.0 - np.exp(-(float(sigma) ** 2) / 2.0)


def resolve_contour_linestyles(level_count, fallback_style):
    styles = getattr(args, "contour_linestyles", None)
    if not styles:
        return fallback_style

    styles = list(styles)
    if level_count <= 0:
        return styles
    if len(styles) >= level_count:
        return styles[:level_count]
    return styles + [styles[-1]] * (level_count - len(styles))


def compute_contour_levels(image, sigmas):
    if getattr(args, "contour_level_mode", "z_values") == "z_values":
        levels = [float(level) for level in sigmas if np.isfinite(level)]
        return sorted(set(levels))

    flat = np.asarray(image, dtype=float).ravel()
    flat = flat[np.isfinite(flat)]
    flat = flat[flat > 0]

    if flat.size == 0:
        return []

    descending = np.sort(flat)[::-1]
    cumsum = np.cumsum(descending)
    total = cumsum[-1]

    levels = []
    for sigma in sigmas:
        target = sigma_to_cumulative_probability(sigma) * total
        index = np.searchsorted(cumsum, target, side="left")
        index = min(index, descending.size - 1)
        threshold = float(descending[index])
        if threshold > 0:
            levels.append(threshold)

    return sorted(set(levels))


def smooth_contour_image(z):
    z_smoothed = np.asarray(z, dtype=float)
    sigma = float(getattr(args, "contour_smoothing_sigma", 0.0))
    if sigma <= 0:
        return z_smoothed

    try:
        from scipy.ndimage import gaussian_filter

        return gaussian_filter(z_smoothed, sigma=sigma)
    except Exception:
        if args.debug:
            rprint(
                "[yellow]Warning:[/yellow] scipy.ndimage.gaussian_filter unavailable; proceeding without contour smoothing."
            )
        return z_smoothed


def apply_contour_discontinuity_filter(contour_set):
    min_vertices = int(getattr(args, "contour_min_vertices", 0))
    if min_vertices <= 0:
        return

    for collection in contour_set.collections:
        paths = collection.get_paths()
        filtered_paths = [path for path in paths if len(path.vertices) >= min_vertices]
        collection.set_paths(filtered_paths)


def smooth_background_image(z):
    z_smoothed = np.asarray(z, dtype=float)
    sigma = float(getattr(args, "background_smoothing_sigma", 0.0))
    if sigma <= 0:
        return z_smoothed

    try:
        from scipy.ndimage import gaussian_filter

        return gaussian_filter(z_smoothed, sigma=sigma)
    except Exception:
        if args.debug:
            rprint(
                "[yellow]Warning:[/yellow] scipy.ndimage.gaussian_filter unavailable; proceeding without background smoothing."
            )
        return z_smoothed


def normalize_image(z):
    z = np.asarray(z, dtype=float)
    if not args.density:
        return z
    total = np.nansum(z)
    return z / total if total > 0 else z


def fill_nan_image(z, x=None, y=None, strategy=None):
    strategy = strategy or getattr(args, "nan_fill", "interpolate")
    z = np.asarray(z, dtype=float)

    if not np.isnan(z).any() or strategy == "none":
        return z

    if strategy == "zero":
        return np.nan_to_num(z, nan=0.0)

    if strategy not in ["interpolate", "nearest"]:
        raise ValueError(f"Unknown NaN fill strategy: {strategy}")

    if strategy == "interpolate":
        try:
            from scipy.interpolate import griddata

            if x is not None and y is not None:
                x_arr = np.asarray(x, dtype=float)
                y_arr = np.asarray(y, dtype=float)
                if x_arr.ndim == 1 and y_arr.ndim == 1:
                    xx, yy = np.meshgrid(x_arr, y_arr)
                else:
                    xx, yy = x_arr, y_arr
            else:
                yy, xx = np.indices(z.shape, dtype=float)

            valid_mask = np.isfinite(z)
            points = np.column_stack((xx[valid_mask], yy[valid_mask]))
            values = z[valid_mask]

            if values.size == 0:
                return np.zeros_like(z, dtype=float)

            z_filled = np.array(z, dtype=float, copy=True)
            nan_mask = ~valid_mask
            if nan_mask.any():
                query_points = np.column_stack((xx[nan_mask], yy[nan_mask]))

                interp_values = griddata(
                    points,
                    values,
                    query_points,
                    method=getattr(args, "nan_interp_method", "cubic"),
                )

                if np.isnan(interp_values).any():
                    linear_values = griddata(
                        points,
                        values,
                        query_points,
                        method="linear",
                    )
                    interp_values = np.where(
                        np.isnan(interp_values), linear_values, interp_values
                    )

                if np.isnan(interp_values).any():
                    nearest_values = griddata(
                        points,
                        values,
                        query_points,
                        method="nearest",
                    )
                    interp_values = np.where(
                        np.isnan(interp_values), nearest_values, interp_values
                    )

                z_filled[nan_mask] = interp_values

        except Exception:
            z_df = pd.DataFrame(z)
            z_df = z_df.interpolate(method="linear", axis=0, limit_direction="both")
            z_df = z_df.interpolate(method="linear", axis=1, limit_direction="both")
            z_df = z_df.ffill(axis=0).bfill(axis=0).ffill(axis=1).bfill(axis=1)
            z_filled = z_df.to_numpy(dtype=float)

    else:
        z_df = pd.DataFrame(z)
        z_df = z_df.ffill(axis=0).bfill(axis=0).ffill(axis=1).bfill(axis=1)
        z_filled = z_df.to_numpy(dtype=float)

    if np.isnan(z_filled).any():
        z_filled = np.nan_to_num(z_filled, nan=0.0)

    return z_filled


def validate_grid_shapes(x, y, z):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    if z.ndim != 2:
        raise ValueError(f"{args.z} must be a 2D array, got shape {z.shape}.")

    if x.ndim == 1 and y.ndim == 1:
        if z.shape != (y.size, x.size):
            raise ValueError(
                f"Grid mismatch: expected {args.z}.shape == (len({args.y}), len({args.x})) = {(y.size, x.size)}, got {z.shape}."
            )
    elif x.ndim == 2 and y.ndim == 2:
        if x.shape != z.shape or y.shape != z.shape:
            raise ValueError(
                f"Grid mismatch: {args.x}, {args.y}, and {args.z} must share the same 2D shape."
            )
    else:
        raise ValueError(
            f"{args.x} and {args.y} must both be 1D axes or both be 2D coordinate grids."
        )

    return x, y, z


def extract_extent(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return [float(np.nanmin(x)), float(np.nanmax(x))], [float(np.nanmin(y)), float(np.nanmax(y))]


def grids_match(reference, candidate):
    return (
        reference[0].shape == candidate[0].shape
        and reference[1].shape == candidate[1].shape
        and np.allclose(reference[0], candidate[0])
        and np.allclose(reference[1], candidate[1])
    )


def aggregate_config_grid(df_config):
    reference_grid = None
    summed_z = None

    for _, row in df_config.iterrows():
        x, y, z = validate_grid_shapes(row[args.x], row[args.y], row[args.z])
        z = fill_nan_image(z, x=x, y=y)
        z = normalize_image(z)

        if reference_grid is None:
            reference_grid = (x, y)
            summed_z = np.array(z, dtype=float, copy=True)
        
        else:
            if not grids_match(reference_grid, (x, y)):
                raise ValueError("All grids for a given selection must share the same x/y coordinates.")
            summed_z = summed_z + z

    if reference_grid is None:
        return None

    return {"x": reference_grid[0], "y": reference_grid[1], "z": summed_z}


def draw_image_background(ax, fig, x, y, z):
    positive = smooth_background_image(z)
    if args.logz:
        positive = np.ma.masked_less_equal(positive, 0)

    mesh = ax.pcolormesh(
        x,
        y,
        positive,
        shading="auto",
        norm=LogNorm() if args.logz else None,
    )
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label(
        args.labelz
        if args.labelz is not None
        else ("Density" if args.density else args.z)
    )
    cbar.ax.yaxis.set_label_position("right")
    return mesh


def build_config_label(config, name, iterable=None):
    config_label = config_dict[config] if config in config_dict else str(config)
    geom = config.split("_")[0].upper() if config is not None else "ALL"

    if args.configs is None and args.names is None:
        label = "Selection"
    elif args.configs is not None and len(set(args.configs)) > 1 and (
        args.names is None or len(set([n for n in args.names if n is not None])) <= 1
    ):
        label = f"{geom}, {config_label}"
    elif args.names is not None and len(set(args.names)) > 1 and (
        args.configs is None or len(set([c for c in args.configs if c is not None])) <= 1
    ):
        label = f"{geom}, {name}"
    else:
        label = ", ".join(
            [part for part in [geom, config_label, name] if part not in [None, "None"]]
        )

    if iterable is not None:
        label += f", {iterable}"

    return label


def validate_filter_inputs(df):
    available_columns = set(df.columns)

    if args.iterable is not None and args.iterable not in available_columns:
        rprint(
            f"[yellow]Warning:[/yellow] Iterable key '{args.iterable}' not found in dataframe columns. Ignoring --iterable filtering."
        )
        args.iterable = None

    if args.select is None:
        return

    if args.save_values is None:
        valid_select = []
        for key in args.select:
            if key in available_columns:
                valid_select.append(key)
            else:
                rprint(
                    f"[yellow]Warning:[/yellow] Selected key '{key}' not found in dataframe columns. Skipping this filter key."
                )
        args.select = valid_select if valid_select else None
        return

    valid_pairs = []
    for key, value in zip(args.select, args.save_values):
        if key in available_columns:
            valid_pairs.append((key, value))
        else:
            rprint(
                f"[yellow]Warning:[/yellow] Selected key '{key}' not found in dataframe columns. Skipping filter '{key}={value}'."
            )

    if len(args.select) != len(args.save_values):
        rprint(
            "[yellow]Warning:[/yellow] --select and --save_values lengths differ; extra entries are ignored."
        )

    if valid_pairs:
        args.select, args.save_values = [list(values) for values in zip(*valid_pairs)]
    else:
        args.select = None
        args.save_values = None


def main():
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    validate_filter_inputs(df)

    if args.variables is not None and args.iterable is not None:
        rprint(
            "[red]Error:[/red] Both variables and iterable arguments were provided. Please use only one."
        )
        return

    if args.combined_contours_only and args.operation != "squared_sum":
        rprint(
            "[yellow]Warning:[/yellow] --combined_contours_only requires --operation squared_sum; ignoring the flag."
        )
        args.combined_contours_only = False

    ncols = (
        len(args.variables)
        if args.variables is not None
        else len(df[args.iterable].unique()) if args.iterable is not None else 1
    )

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    fig, ax = create_common_subplots(
        nrows=1,
        ncols=ncols,
    )

    variables = args.variables if args.variables is not None else [None]
    filtered_df = filter_dataframe(df, args)
    iterables = (
        filtered_df[args.iterable].unique() if args.iterable is not None else [None]
    )

    matched_ranges = [None, None]

    for (idx, variable), (jdx, iterable) in product(
        enumerate(variables),
        enumerate(iterables) if args.iterable is not None else enumerate([None]),
    ):
        ax_current = ax if ncols == 1 else ax[idx if args.variables is not None else jdx]

        if variable is not None and iterable is None:
            subset = filtered_df[(filtered_df["Variable"] == variable)]
        elif iterable is not None and variable is None:
            subset = filtered_df[(filtered_df[args.iterable] == iterable)]
        elif variable is None and iterable is None:
            subset = filtered_df.copy()
        else:
            rprint(
                "[red]Error:[/red] Simultaneous variable and iterable contour splitting is not supported."
            )
            return

        if subset.empty:
            rprint(
                f"[yellow]Warning:[/yellow] No data for {variable if variable is not None else iterable}. Skipping..."
            )
            continue

        payloads = []
        sum_background = None
        combined_z = None
        reference_grid = None
        x_range_local = None
        y_range_local = None

        for cdx, (config, name) in enumerate(zip(configs, names)):
            df_config = subset.copy()
            if config is not None:
                df_config = df_config[df_config["Config"] == config]
            if name is not None:
                df_config = df_config[df_config["Name"] == name]

            if df_config.empty:
                if args.debug:
                    rprint(
                        f"[yellow]Warning:[/yellow] No data for Config={config}, Name={name}. Skipping contour."
                    )
                continue

            try:
                grid = aggregate_config_grid(df_config)
            except ValueError as exc:
                rprint(f"[red]Error:[/red] {exc}")
                continue

            if grid is None:
                continue

            x_grid = grid["x"]
            y_grid = grid["y"]
            z_grid = grid["z"]

            if reference_grid is None:
                reference_grid = (x_grid, y_grid)
                sum_background = np.zeros_like(z_grid, dtype=float)
                combined_z = np.zeros_like(z_grid, dtype=float)
                x_range_local, y_range_local = extract_extent(x_grid, y_grid)
            elif not grids_match(reference_grid, (x_grid, y_grid)):
                rprint(
                    "[red]Error:[/red] Configuration grids do not share the same x/y coordinates, so they cannot be combined on one contour plot."
                )
                continue

            sum_background = sum_background + z_grid
            if args.operation == "squared_sum":
                combined_z = combined_z + np.square(z_grid)

            color = config_color[config] if config in config_color else f"C{cdx % 10}"
            linestyle = config_line[config] if config in config_line else "-"

            payloads.append(
                {
                    "x": x_grid,
                    "y": y_grid,
                    "z": z_grid,
                    "color": color,
                    "linestyle": linestyle,
                    "label": build_config_label(config, name, iterable),
                    "config": config,
                    "name": name,
                }
            )

        if not payloads or reference_grid is None:
            continue

        if args.operation == "squared_sum":
            combined_z = np.sqrt(combined_z)
        else:
            combined_z = sum_background

        background_x, background_y = reference_grid
        if args.background == "all":
            draw_image_background(ax_current, fig, background_x, background_y, sum_background)
        elif args.background == "first":
            draw_image_background(
                ax_current,
                fig,
                payloads[0]["x"],
                payloads[0]["y"],
                payloads[0]["z"],
            )
        elif args.background == "combined":
            draw_image_background(ax_current, fig, background_x, background_y, combined_z)

        legend_handles = []
        if not args.combined_contours_only:
            for payload in payloads:
                contour_image = smooth_contour_image(
                    smooth_background_image(payload["z"])
                )
                levels = compute_contour_levels(contour_image, args.contour_sigmas)
                if not levels:
                    continue

                if args.debug:
                    z_min = np.nanmin(np.asarray(contour_image, dtype=float)).item()
                    z_max = np.nanmax(np.asarray(contour_image, dtype=float)).item()
                    rprint(
                        f"[blue]Info:[/blue] Contour levels for {payload['label']}: {levels} (z-range: {z_min:.4g} to {z_max:.4g})"
                    )

                contour_set = ax_current.contour(
                    payload["x"],
                    payload["y"],
                    contour_image,
                    levels=levels,
                    colors=[payload["color"]],
                    linestyles=resolve_contour_linestyles(len(levels), payload["linestyle"]),
                    linewidths=args.contour_linewidth,
                    alpha=args.contour_alpha,
                    zorder=5,
                )
                apply_contour_discontinuity_filter(contour_set)
                legend_linestyle = resolve_contour_linestyles(1, payload["linestyle"])
                if isinstance(legend_linestyle, list):
                    legend_linestyle = legend_linestyle[0]
                legend_handles.append(
                    Line2D(
                        [0],
                        [0],
                        color=payload["color"],
                        linestyle=legend_linestyle,
                        linewidth=args.contour_linewidth,
                        label=payload["label"],
                    )
                )

        if args.operation == "squared_sum":
            combined_contour_image = smooth_contour_image(
                smooth_background_image(combined_z)
            )
            combined_levels = compute_contour_levels(
                combined_contour_image, args.contour_sigmas
            )
            if combined_levels:
                if args.debug:
                    z_min = np.nanmin(
                        np.asarray(combined_contour_image, dtype=float)
                    ).item()
                    z_max = np.nanmax(
                        np.asarray(combined_contour_image, dtype=float)
                    ).item()
                    rprint(
                        f"[blue]Info:[/blue] Combined contour levels: {combined_levels} (z-range: {z_min:.4g} to {z_max:.4g})"
                    )

                combined_linewidth = (
                    args.combined_linewidth
                    if getattr(args, "combined_linewidth", None) is not None
                    else args.contour_linewidth + 0.5
                )

                contour_set = ax_current.contour(
                    background_x,
                    background_y,
                    combined_contour_image,
                    levels=combined_levels,
                    colors=[args.combined_color],
                    linestyles=resolve_contour_linestyles(
                        len(combined_levels), args.combined_linestyle
                    ),
                    linewidths=combined_linewidth,
                    alpha=args.combined_alpha,
                    zorder=6,
                )
                apply_contour_discontinuity_filter(contour_set)
                combined_legend_linestyle = resolve_contour_linestyles(
                    1, args.combined_linestyle
                )
                if isinstance(combined_legend_linestyle, list):
                    combined_legend_linestyle = combined_legend_linestyle[0]
                legend_handles.append(
                    Line2D(
                        [0],
                        [0],
                        color=args.combined_color,
                        linestyle=combined_legend_linestyle,
                        linewidth=combined_linewidth,
                        label=args.combined_label,
                    )
                )

        if x_range_local is not None and y_range_local is not None:
            if matched_ranges[0] is None:
                matched_ranges = [list(x_range_local), list(y_range_local)]
            else:
                if args.matchx:
                    matched_ranges[0] = [
                        min(matched_ranges[0][0], x_range_local[0]),
                        max(matched_ranges[0][1], x_range_local[1]),
                    ]
                if args.matchy:
                    matched_ranges[1] = [
                        min(matched_ranges[1][0], y_range_local[0]),
                        max(matched_ranges[1][1], y_range_local[1]),
                    ]

        if args.diagonal and x_range_local is not None and y_range_local is not None:
            diagonal_range = [
                min(x_range_local[0], y_range_local[0]),
                max(x_range_local[1], y_range_local[1]),
            ]
            ax_current.plot(
                diagonal_range,
                diagonal_range,
                color="k" if args.logz else "white",
                linestyle="--",
            )

        if args.horizontal is not None:
            ax_current.axhline(
                args.horizontal,
                color="k" if args.logz else "white",
                linestyle="--",
            )

        if args.vertical is not None:
            ax_current.axvline(
                args.vertical,
                color="k" if args.logz else "white",
                linestyle="--",
            )

        if ncols > 1:
            plot_subtitle = make_subtitle_from_args(
                args, iterables, plot_type="hist2d", idx=jdx
            )
            ax_current.set_title(plot_subtitle, fontsize=subtitlefontsize)

        ax_current.set_xlabel(args.labelx if args.labelx is not None else args.x)
        if idx == 0:
            ax_current.set_ylabel(args.labely if args.labely is not None else args.y)

        if args.matchx and matched_ranges[0] is not None:
            ax_current.set_xlim(matched_ranges[0])
        elif x_range_local is not None:
            ax_current.set_xlim(x_range_local)

        if args.matchy and matched_ranges[1] is not None:
            ax_current.set_ylim(matched_ranges[1])
        elif y_range_local is not None:
            ax_current.set_ylim(y_range_local)

        if args.rangex is not None:
            ax_current.set_xlim(args.rangex)
        if args.rangey is not None:
            ax_current.set_ylim(args.rangey)

        apply_scientific_threshold_formatter(ax_current, threshold=0.1, axis="both")

        point_values = parse_point_pairs(getattr(args, "point", None))
        point_labels, point_label_warning = normalize_point_labels(
            getattr(args, "point_label", None), len(point_values)
        )
        if point_label_warning is not None:
            rprint(f"[yellow]Warning:[/yellow] {point_label_warning}")

        point_color = "k" if args.logz else "white"
        point_edge_color = "white" if args.logz else "black"
        if point_values:
            for point_idx, (point_x, point_y) in enumerate(point_values):
                ax_current.scatter(
                    point_x,
                    point_y,
                    color=point_color,
                    edgecolors=point_edge_color,
                    linewidths=1.0,
                    s=85,
                    zorder=100,
                )
                if point_labels is not None:
                    place_point_label(ax_current, point_x, point_y, point_labels[point_idx], fontsize=linelabelfontsize)

        if legend_handles:
            apply_legend_style(
                ax_current,
                handles=legend_handles,
                capitalize_labels=not getattr(args, "no_capitalize_legend", False),
            )

    plot_title = make_title_from_args(args)
    fig.suptitle(plot_title, fontsize=titlefontsize)

    apply_note_to_figure(fig, getattr(args, "note", None))

    output_file = make_name_from_args(args, prefix=None, suffix="contour.png")
    default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
    save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)


if __name__ == "__main__":
    main()
