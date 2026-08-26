#!/usr/bin/env python3

"""Side-by-side 2D scatter projections of a 3D event display."""

from _bootstrap import ensure_src_path

ensure_src_path()

from pathlib import Path
import pickle
import pandas as pd
import numpy as np
from rich import print as rprint

from lib import *
from lib.plot import apply_legend_style, create_common_subplots, apply_note_to_figure, add_centered_suptitle
from lib.format import make_title_from_args
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.selection import filter_dataframe
from lib.imports import import_data, prepare_import
from common_args import add_common_args, map_iterable_label, map_iterable_color, resolve_axis_label

parser = argparse.ArgumentParser(
    description="Plot side-by-side 2D projections of a 3D event display"
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
        "remove_value",
        "x",
        "y",
        "z",
        "labelx",
        "labelz",
        "rangex",
        "rangey",
        "logz",
        "title",
        "output",
        "subfolder",
        "note",
        "debug",
    ],
    overrides={
        "datafile": {"required": True, "help": "Input pickle path or basename in input/data"},
        "x": {"default": "X", "help": "Column for the shared horizontal axis"},
        "y": {"default": "Y", "help": "Column for the left panel vertical axis"},
        "z": {"default": "Z", "help": "Column for the right panel vertical axis"},
        "labelz": {"help": "Legend title (iterable) or colorbar label (--colorby)"},
    },
)

# Override labely to accept 1 or 2 values: first for Y panel, second for Z panel
parser.add_argument(
    "--labely",
    nargs="+",
    type=str,
    default=None,
    help="Y-axis label(s). One value applies to both panels; two values label left then right panel.",
)

parser.add_argument(
    "--colorby",
    type=str,
    default=None,
    help="Column to map to a continuous colormap (e.g. E for energy). Overrides iterable coloring.",
)

parser.add_argument(
    "--marker_size",
    "--ms",
    type=float,
    default=120.0,
    help="Scatter marker size (default: 120)",
)

parser.add_argument(
    "--sizeby",
    type=str,
    default=None,
    help="Column to scale dot size by (e.g. E for energy). Values are normalised to "
    "[marker_size/sizeby_scale, marker_size*sizeby_scale].",
)

parser.add_argument(
    "--sizeby_scale",
    type=float,
    default=4.0,
    help="How much --sizeby is allowed to shrink/grow marker_size: sizes range over "
    "[marker_size/sizeby_scale, marker_size*sizeby_scale] (default: 4, i.e. a 16x min-to-max spread). "
    "Larger values exaggerate the size differences; 1 disables scaling (all points render at marker_size).",
)

parser.add_argument(
    "--labelsize",
    type=str,
    default=None,
    help="Title label for the size legend (defaults to the column name given to --sizeby).",
)

parser.add_argument(
    "--iterable_mapping",
    type=str,
    default=None,
    help="Optional mapping dict name for renaming iterable legend labels",
)

parser.add_argument(
    "--iterable_color_mapping",
    type=str,
    default=None,
    help="Optional mapping dict name for iterable scatter colors",
)

parser.add_argument(
    "--markerby",
    type=str,
    default=None,
    help="Column to map to distinct marker shapes (e.g. Variable for truth vs reco). "
    "Composes with --colorby/--iterable/--sizeby and adds its own marker-shape legend.",
)

args = parser.parse_args()


def _load_display_df(args):
    """Load a display pkl that may live directly at the given path or in input/data/."""
    candidate = Path(args.datafile)
    repo_root = Path(__file__).resolve().parents[1]
    input_dir = repo_root / "input" / "data"

    candidates = [candidate]
    if candidate.suffix == ".pkl":
        candidates.append(input_dir / candidate.name)
    else:
        candidates.append(input_dir / f"{candidate.name}.pkl")
        candidates.append(input_dir / f"{candidate.stem}.pkl")

    # Study-variant pkls (e.g. ..._charge_Q100.pkl) live under
    # input/data/studies/ instead of flat in input/data/ — fall back there
    # rather than maintaining a suffix allowlist.
    candidates += [input_dir / "studies" / c.name for c in candidates if c.is_relative_to(input_dir)]

    for path in candidates:
        if not path.exists():
            continue
        with path.open("rb") as fh:
            data = pickle.load(fh)
        if isinstance(data, pd.DataFrame):
            return data
        return pd.DataFrame(data)

    # Fall back to import_data convention
    return import_data(args)


def _explode_point_columns(df, markerby=None):
    """Explode per-point list-valued columns (e.g. X, Y, Z, E, PDG, Charge, Purity) into one row per point.

    Newer display pkls store one row per (Config, Name, Variable) group with each column holding a
    list of per-point values instead of one row per point; this restores the flat, per-point shape
    the rest of the script expects.

    Once exploded, the different Variable groups (e.g. truth vs reco, or truth/ccint/vertex) become
    indistinguishable points in the same scatter unless --markerby is set to tell them apart. So when
    markerby isn't given, only the first group per (Config, Name) is kept -- silently merging e.g.
    truth and reco points would misrepresent the data -- and a warning is printed since this drops
    rows the caller may not expect.
    """
    list_cols = [col for col in df.columns if df[col].apply(lambda v: isinstance(v, list)).any()]
    if not list_cols:
        return df

    if not markerby:
        group_cols = [c for c in ("Config", "Name") if c in df.columns]
        restricted = df.groupby(group_cols, sort=False, group_keys=False).head(1) if group_cols else df.head(1)
        if len(restricted) < len(df):
            if "Variable" in df.columns:
                kept = restricted["Variable"].tolist()
                dropped = sorted(set(df["Variable"]) - set(kept))
                detail = f"keeping Variable={kept} and dropping Variable={dropped}"
            else:
                detail = f"keeping the first {len(restricted)} of {len(df)} row(s)"
            rprint(
                f"[yellow]Warning:[/yellow] --markerby not set: {detail} per Config/Name to avoid "
                "silently merging distinct groups (e.g. truth/reco) into one undistinguished scatter. "
                "Pass --markerby <column> (e.g. --markerby Variable) to plot and distinguish all of them."
            )
        df = restricted

    try:
        return df.explode(column=list_cols).reset_index(drop=True)
    except ValueError:
        rprint(
            f"[yellow]Warning:[/yellow] Could not explode list columns {list_cols} "
            "(mismatched lengths within a row). Data left as-is."
        )
        return df


def _size_scale(base_size, scale=4.0):
    return base_size / scale, base_size * scale


def _resolve_sizes(df_subset, sizeby_col, base_size, vmin=None, vmax=None, scale=4.0):
    """Return a per-point size array scaled to [base/scale, base*scale], or a scalar if no column.

    Pass vmin/vmax to normalise against a global range (required for consistency across groups).
    """
    if sizeby_col is None or sizeby_col not in df_subset.columns:
        return base_size
    vals = df_subset[sizeby_col].astype(float).to_numpy()
    if vmin is None:
        vmin = vals.min()
    if vmax is None:
        vmax = vals.max()
    if vmax == vmin:
        return base_size
    normed = (vals - vmin) / (vmax - vmin)
    s_min, s_max = _size_scale(base_size, scale)
    sizes = s_min + normed * (s_max - s_min)
    # A point whose own sizeby value is NaN would otherwise get a NaN marker size; a scatter
    # group made up entirely of such points crashes matplotlib's extent computation on render
    # (ValueError: need at least one array to concatenate). Fall back to base_size per point instead.
    return np.where(np.isnan(sizes), base_size, sizes)


def _proxy_scatter(ax, **kwargs):
    """Create a scatter handle for legend use only: drawn on ax to inherit its styling, then
    immediately removed so it contributes no empty-data artist to the actual rendered plot.

    Using bare `plt.scatter([], [], ...)` for this (the previous approach) attaches an empty
    PathCollection to whatever axes pyplot's global state considers "current" -- not necessarily
    the intended one -- and matplotlib can crash while rendering an all-empty collection
    (ValueError: need at least one array to concatenate). Scoping to a specific ax and removing
    the artist avoids both problems while keeping it fully usable as a legend handle.
    """
    handle = ax.scatter([], [], **kwargs)
    handle.remove()
    return handle


def _add_size_legend(ax, label, vmin, vmax, base_size, scale=4.0, n_levels=4, loc="best"):
    """Add a legend on ax showing how dot area maps to column values, without discarding any
    legend already on ax (e.g. a size legend for another --markerby group)."""
    existing = ax.get_legend()
    levels = np.linspace(vmin, vmax, n_levels)
    s_min, s_max = _size_scale(base_size, scale)
    # NaN-safe: a NaN vmin/vmax (e.g. a --markerby group whose --sizeby column is entirely NaN)
    # would otherwise produce NaN-sized legend swatches, which crashes matplotlib on render even
    # though the swatch artists are removed from the axes (the Legend redraws them on its own).
    valid_range = not (pd.isna(vmin) or pd.isna(vmax)) and vmax != vmin
    sizes = s_min + (levels - vmin) / (vmax - vmin) * (s_max - s_min) if valid_range else np.full(n_levels, base_size)
    handles = [
        _proxy_scatter(ax, s=s, color="gray", alpha=0.85, linewidths=0)
        for s in sizes
    ]
    labels = [f"{v:.2e}" for v in levels]
    legend = apply_legend_style(
        ax, title=label, handles=handles, labels=labels, capitalize_labels=False, scatterpoints=1, loc=loc
    )
    if existing is not None:
        ax.add_artist(existing)
    return legend


_HOLLOW_SCALE = 2.0  # how much bigger a hollow marker's visible diameter is vs. a filled one
# matplotlib's scatter `s` is marker AREA (points^2), not diameter, so matching a diameter ratio
# requires squaring it here: area ~ diameter^2, e.g. a 2x-diameter marker needs 4x the area.
_HOLLOW_SIZE_MULTIPLIER = _HOLLOW_SCALE ** 2


def _scatter_group(ax, x_vals, y_vals, color, label, size, marker="o", hollow=False, alpha=0.85, zorder=3):
    if hollow:
        ax.scatter(
            x_vals, y_vals, s=np.asarray(size) * _HOLLOW_SIZE_MULTIPLIER, marker=marker, label=label,
            alpha=alpha, zorder=zorder, facecolors="none", edgecolors=color, linewidths=1.5,
        )
    else:
        ax.scatter(x_vals, y_vals, c=color, s=size, marker=marker, label=label, alpha=alpha, zorder=zorder, linewidths=0)


_MARKER_CYCLE = ["o", "^", "s", "D", "P", "X", "v", "*"]


def _build_marker_map(df, col):
    """Assign each unique value of col a (marker, hollow) style, sorted for a deterministic mapping.

    With exactly two values, both keep the same marker shape ("o") and are told apart by fill: the
    first (sorted) value renders hollow/open, the second renders filled. With more than two values,
    distinct marker shapes are cycled instead, since fill alone can't distinguish more than two
    categories.
    """
    if col is None or col not in df.columns:
        return None
    values = sorted(df[col].dropna().unique().tolist(), key=str)
    if not values:
        return None
    if len(values) == 2:
        return {values[0]: ("o", True), values[1]: ("o", False)}
    return {v: (_MARKER_CYCLE[i % len(_MARKER_CYCLE)], False) for i, v in enumerate(values)}


def _split_by_marker(df, col, marker_map):
    """Split df into (value, subset, marker, hollow) groups per marker_map, skipping empty groups.

    Always yields filled groups before hollow ones, regardless of marker_map's own key order, so
    hollow/open markers -- drawn larger via _HOLLOW_SIZE_MULTIPLIER -- always render on top of the
    filled ones and stay visible where points overlap.

    Falls back to a single filled ("o") group covering the whole df when marker_map is None, so
    callers can use this unconditionally without changing behaviour when --markerby isn't set.
    """
    if marker_map is None:
        return [(None, df, "o", False)]
    groups = []
    for value, (marker, hollow) in sorted(marker_map.items(), key=lambda item: item[1][1]):
        subset = df[df[col] == value]
        if not subset.empty:
            groups.append((value, subset, marker, hollow))
    return groups


def _add_marker_legend(ax, title, marker_map, mapping_name=None):
    """Add a second, marker-shape/fill legend to ax without discarding its existing (color) legend."""
    existing = ax.get_legend()
    # Filled entries before hollow ones, matching the filled-first/hollow-on-top draw order.
    values = [v for v, _ in sorted(marker_map.items(), key=lambda item: item[1][1])]
    handles = []
    for v in values:
        marker, hollow = marker_map[v]
        if hollow:
            handles.append(
                _proxy_scatter(
                    ax, s=60 * _HOLLOW_SIZE_MULTIPLIER, marker=marker, facecolors="none", edgecolors="gray",
                    linewidths=1.5, alpha=0.85,
                )
            )
        else:
            handles.append(_proxy_scatter(ax, s=60, marker=marker, color="gray", alpha=0.85, linewidths=0))
    labels = [map_iterable_label(v, title, mapping_name, len(values)) for v in values]
    legend = apply_legend_style(
        ax, title=title, handles=handles, labels=labels, capitalize_labels=False, scatterpoints=1, loc="lower left"
    )
    if existing is not None:
        ax.add_artist(existing)
    return legend


def main():
    df = _load_display_df(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No data loaded. Exiting.")
        return

    df = _explode_point_columns(df, markerby=getattr(args, "markerby", None))

    for col in [args.x, args.y, args.z]:
        if col not in df.columns:
            rprint(f"[red]Error:[/red] Column '{col}' not found in dataframe. Available: {list(df.columns)}")
            return

    if args.debug:
        rprint(f"[blue]Debug:[/blue] Loaded {len(df)} rows, columns: {list(df.columns)}")

    # Apply select/save_values filtering
    df = filter_dataframe(df, args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No data after filtering. Exiting.")
        return

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

        df_config = df.copy()
        if config is not None:
            df_config = df_config[df_config["Config"] == config]
        if name is not None:
            df_config = df_config[df_config["Name"] == name]

        if df_config.empty:
            rprint(f"[yellow]Warning:[/yellow] No data for Config={config}, Name={name}. Skipping.")
            continue

        fig, axes = create_common_subplots(nrows=1, ncols=2)
        ax_left, ax_right = axes[0], axes[1]

        label_x = resolve_axis_label(args.labelx, args.x, df_config)
        if args.labely is None:
            label_y = resolve_axis_label(None, args.y, df_config)
            label_z_axis = resolve_axis_label(None, args.z, df_config)
        elif len(args.labely) == 1:
            label_y = args.labely[0]
            label_z_axis = args.labely[0]
        else:
            label_y = args.labely[0]
            label_z_axis = args.labely[1]

        use_colorby = args.colorby is not None and args.colorby in df_config.columns

        markerby = getattr(args, "markerby", None)
        marker_map = _build_marker_map(df_config, markerby)
        use_markerby = marker_map is not None

        sizeby = getattr(args, "sizeby", None)
        size_vmin = size_vmax = None
        # When --markerby is set, normalise --sizeby independently within each markerby group
        # instead of globally: different groups (e.g. truth's per-hit E vs reco's total-interaction
        # E) can sit on very different scales, and a single shared range lets one group's outliers
        # distort every other group's marker sizes.
        size_range_by_marker_value = None
        if sizeby and sizeby in df_config.columns:
            if use_markerby:
                size_range_by_marker_value = {}
                for value, subset, _, _ in _split_by_marker(df_config, markerby, marker_map):
                    vals = subset[sizeby].astype(float)
                    size_range_by_marker_value[value] = (vals.min(), vals.max())
            else:
                size_vmin = df_config[sizeby].astype(float).min()
                size_vmax = df_config[sizeby].astype(float).max()

        def _size_range_for(value):
            if size_range_by_marker_value is not None:
                return size_range_by_marker_value.get(value, (None, None))
            return size_vmin, size_vmax

        if use_colorby:
            c_vals_all = df_config[args.colorby].astype(float).to_numpy()
            norm = LogNorm(vmin=c_vals_all[c_vals_all > 0].min(), vmax=c_vals_all.max()) if args.logz else None

            sc_right = None
            for value, subset, marker, hollow in _split_by_marker(df_config, markerby, marker_map):
                c_vals = subset[args.colorby].astype(float).to_numpy()
                group_vmin, group_vmax = _size_range_for(value)
                subset_sizes = _resolve_sizes(subset, sizeby, args.marker_size, group_vmin, group_vmax, scale=args.sizeby_scale)
                if hollow:
                    subset_sizes = np.asarray(subset_sizes) * _HOLLOW_SIZE_MULTIPLIER
                sc_left = ax_left.scatter(
                    subset[args.x].to_numpy(),
                    subset[args.y].to_numpy(),
                    c=c_vals,
                    s=subset_sizes,
                    norm=norm,
                    marker=marker,
                    alpha=0.85,
                    linewidths=1.5 if hollow else 0,
                )
                sc_right = ax_right.scatter(
                    subset[args.x].to_numpy(),
                    subset[args.z].to_numpy(),
                    c=c_vals,
                    s=subset_sizes,
                    norm=norm,
                    marker=marker,
                    alpha=0.85,
                    linewidths=1.5 if hollow else 0,
                )
                if hollow:
                    # Keep the colormap-derived colors on the edge, drop the fill (open marker).
                    for sc in (sc_left, sc_right):
                        edge_colors = sc.get_facecolors()
                        sc.set_edgecolor(edge_colors)
                        sc.set_facecolor("none")

            cbar = fig.colorbar(sc_right, ax=[ax_left, ax_right], shrink=0.9, pad=0.02)
            colorbar_label = args.labelz if args.labelz is not None else args.colorby
            if args.logz:
                colorbar_label += " (log scale)"
            cbar.set_label(colorbar_label)

        else:
            use_iterable = args.iterable is not None and args.iterable in df_config.columns

            if use_iterable:
                df_config = df_config.dropna(subset=[args.iterable])
                # Sorted (not first-occurrence) order so the same value set always gets the same
                # color assignment, regardless of how the rows happen to be ordered in this file.
                iterable_values = sorted(df_config[args.iterable].unique().tolist(), key=str)

                legend_handles = []
                legend_labels = []

                for jdx, iterable in enumerate(iterable_values):
                    subset = df_config[df_config[args.iterable] == iterable]

                    iterable_label = map_iterable_label(
                        iterable,
                        args.iterable,
                        getattr(args, "iterable_mapping", None),
                        len(iterable_values),
                    )
                    iterable_color = map_iterable_color(
                        iterable, getattr(args, "iterable_color_mapping", None), iterable_name=args.iterable
                    ) or f"C{jdx}"

                    if args.debug:
                        rprint(f"[blue]Debug:[/blue] {args.iterable}={iterable} -> label={iterable_label}, color={iterable_color}, n={len(subset)}")

                    # Always a filled circle in the legend, independent of --markerby shape/fill.
                    legend_handles.append(
                        _proxy_scatter(ax_left, marker="o", color=iterable_color, s=60, alpha=0.85, linewidths=0)
                    )
                    legend_labels.append(iterable_label)

                    for value, marker_subset, marker, hollow in _split_by_marker(subset, markerby, marker_map):
                        group_vmin, group_vmax = _size_range_for(value)
                        subset_sizes = _resolve_sizes(marker_subset, sizeby, args.marker_size, group_vmin, group_vmax, scale=args.sizeby_scale)
                        _scatter_group(
                            ax_left,
                            marker_subset[args.x].to_numpy(),
                            marker_subset[args.y].to_numpy(),
                            iterable_color,
                            None,
                            subset_sizes,
                            marker=marker,
                            hollow=hollow,
                        )
                        _scatter_group(
                            ax_right,
                            marker_subset[args.x].to_numpy(),
                            marker_subset[args.z].to_numpy(),
                            iterable_color,
                            None,
                            subset_sizes,
                            marker=marker,
                            hollow=hollow,
                        )

                legend_title = args.labelz if args.labelz is not None else args.iterable
                apply_legend_style(
                    ax_left,
                    title=legend_title,
                    handles=legend_handles,
                    labels=legend_labels,
                    capitalize_labels=getattr(args, "capitalize_legend", False),
                    loc="upper left",
                )

            else:
                for value, subset, marker, hollow in _split_by_marker(df_config, markerby, marker_map):
                    group_vmin, group_vmax = _size_range_for(value)
                    subset_sizes = _resolve_sizes(subset, sizeby, args.marker_size, group_vmin, group_vmax, scale=args.sizeby_scale)
                    _scatter_group(
                        ax_left,
                        subset[args.x].to_numpy(),
                        subset[args.y].to_numpy(),
                        "C0",
                        None,
                        subset_sizes,
                        marker=marker,
                        hollow=hollow,
                    )
                    _scatter_group(
                        ax_right,
                        subset[args.x].to_numpy(),
                        subset[args.z].to_numpy(),
                        "C0",
                        None,
                        subset_sizes,
                        marker=marker,
                        hollow=hollow,
                    )

        if sizeby:
            size_legend_label = getattr(args, "labelsize", None) or sizeby
            if size_range_by_marker_value is not None:
                # One legend per markerby group, stacked top/bottom on the right panel, since each
                # group has its own independent size normalisation.
                size_legend_locs = ["upper right", "lower right"]
                for gdx, (_, (group_vmin, group_vmax)) in enumerate(size_range_by_marker_value.items()):
                    if pd.isna(group_vmin) or pd.isna(group_vmax) or group_vmin == group_vmax:
                        continue
                    _add_size_legend(
                        ax_right, size_legend_label, group_vmin, group_vmax, args.marker_size,
                        scale=args.sizeby_scale, loc=size_legend_locs[gdx % len(size_legend_locs)],
                    )
            elif size_vmin is not None and not pd.isna(size_vmin) and not pd.isna(size_vmax) and size_vmin != size_vmax:
                _add_size_legend(ax_right, size_legend_label, size_vmin, size_vmax, args.marker_size, scale=args.sizeby_scale)

        if use_markerby:
            _add_marker_legend(ax_left, markerby, marker_map)

        ax_left.set_xlabel(label_x, fontsize=xlabelfontsize)
        ax_left.set_ylabel(label_y, fontsize=ylabelfontsize)
        ax_right.set_xlabel(label_x, fontsize=xlabelfontsize)
        ax_right.set_ylabel(label_z_axis, fontsize=ylabelfontsize)

        if args.rangex is not None:
            ax_left.set_xlim(args.rangex)
            ax_right.set_xlim(args.rangex)
        if args.rangey is not None:
            ax_left.set_ylim(args.rangey)

        if args.title is not None:
            plot_title = args.title
        elif "Title" in df_config.columns and not df_config["Title"].isna().all():
            plot_title = str(df_config["Title"].dropna().iloc[0])
        else:
            plot_title = make_title_from_args(args)
        add_centered_suptitle(fig, plot_title, fontsize=titlefontsize)

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="event_display.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)


if __name__ == "__main__":
    main()
