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
from lib.plot import apply_legend_style, create_common_subplots, apply_note_to_figure
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
    default=8.0,
    help="Scatter marker size (default: 8)",
)

parser.add_argument(
    "--sizeby",
    type=str,
    default=None,
    help="Column to scale dot size by (e.g. E for energy). Values are normalised to [marker_size/4, marker_size*4].",
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


def _size_scale(base_size):
    return base_size / 4, base_size * 4


def _resolve_sizes(df_subset, sizeby_col, base_size, vmin=None, vmax=None):
    """Return a per-point size array scaled to [base/4, base*4], or a scalar if no column.

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
    s_min, s_max = _size_scale(base_size)
    return s_min + normed * (s_max - s_min)


def _add_size_legend(ax, label, vmin, vmax, base_size, n_levels=4):
    """Add a legend on ax showing how dot area maps to column values."""
    levels = np.linspace(vmin, vmax, n_levels)
    s_min, s_max = _size_scale(base_size)
    sizes = s_min + (levels - vmin) / (vmax - vmin) * (s_max - s_min) if vmax != vmin else np.full(n_levels, base_size)
    handles = [
        plt.scatter([], [], s=s, color="gray", alpha=0.85, linewidths=0)
        for s in sizes
    ]
    labels = [f"{v:.2e}" for v in levels]
    apply_legend_style(ax, title=label, handles=handles, labels=labels, capitalize_labels=False, scatterpoints=1)


def _scatter_group(ax, x_vals, y_vals, color, label, size, alpha=0.85, zorder=3):
    ax.scatter(x_vals, y_vals, c=color, s=size, label=label, alpha=alpha, zorder=zorder, linewidths=0)


def main():
    df = _load_display_df(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No data loaded. Exiting.")
        return

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

        sizeby = getattr(args, "sizeby", None)
        size_vmin = size_vmax = None
        if sizeby and sizeby in df_config.columns:
            size_vmin = df_config[sizeby].astype(float).min()
            size_vmax = df_config[sizeby].astype(float).max()
        sizes = _resolve_sizes(df_config, sizeby, args.marker_size, size_vmin, size_vmax)

        if use_colorby:
            c_vals = df_config[args.colorby].astype(float).to_numpy()
            norm = LogNorm(vmin=c_vals[c_vals > 0].min(), vmax=c_vals.max()) if args.logz else None

            sc_left = ax_left.scatter(
                df_config[args.x].to_numpy(),
                df_config[args.y].to_numpy(),
                c=c_vals,
                s=sizes,
                norm=norm,
                alpha=0.85,
                linewidths=0,
            )
            sc_right = ax_right.scatter(
                df_config[args.x].to_numpy(),
                df_config[args.z].to_numpy(),
                c=c_vals,
                s=sizes,
                norm=norm,
                alpha=0.85,
                linewidths=0,
            )

            cbar = fig.colorbar(sc_right, ax=[ax_left, ax_right], shrink=0.9, pad=0.02)
            colorbar_label = args.labelz if args.labelz is not None else args.colorby
            if args.logz:
                colorbar_label += " (log scale)"
            cbar.set_label(colorbar_label)

        else:
            use_iterable = args.iterable is not None and args.iterable in df_config.columns

            if use_iterable:
                df_config = df_config.dropna(subset=[args.iterable])
                iterable_values = df_config[args.iterable].unique()

                for jdx, iterable in enumerate(iterable_values):
                    subset = df_config[df_config[args.iterable] == iterable]

                    iterable_label = map_iterable_label(
                        iterable,
                        args.iterable,
                        getattr(args, "iterable_mapping", None),
                        len(iterable_values),
                    )
                    iterable_color = map_iterable_color(
                        iterable, getattr(args, "iterable_color_mapping", None)
                    ) or f"C{jdx}"

                    if args.debug:
                        rprint(f"[blue]Debug:[/blue] {args.iterable}={iterable} -> label={iterable_label}, color={iterable_color}, n={len(subset)}")

                    subset_sizes = _resolve_sizes(subset, sizeby, args.marker_size, size_vmin, size_vmax)
                    _scatter_group(
                        ax_left,
                        subset[args.x].to_numpy(),
                        subset[args.y].to_numpy(),
                        iterable_color,
                        iterable_label,
                        subset_sizes,
                    )
                    _scatter_group(
                        ax_right,
                        subset[args.x].to_numpy(),
                        subset[args.z].to_numpy(),
                        iterable_color,
                        None,
                        subset_sizes,
                    )

                legend_title = args.labelz if args.labelz is not None else args.iterable
                apply_legend_style(
                    ax_left,
                    title=legend_title,
                    capitalize_labels=not getattr(args, "no_capitalize_legend", False),
                )

            else:
                _scatter_group(
                    ax_left,
                    df_config[args.x].to_numpy(),
                    df_config[args.y].to_numpy(),
                    "C0",
                    None,
                    sizes,
                )
                _scatter_group(
                    ax_right,
                    df_config[args.x].to_numpy(),
                    df_config[args.z].to_numpy(),
                    "C0",
                    None,
                    sizes,
                )

        if sizeby and size_vmin is not None and size_vmin != size_vmax:
            size_legend_label = getattr(args, "labelsize", None) or sizeby
            _add_size_legend(ax_right, size_legend_label, size_vmin, size_vmax, args.marker_size)

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
        fig.suptitle(plot_title, fontsize=titlefontsize)

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="event_display.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)


if __name__ == "__main__":
    main()
