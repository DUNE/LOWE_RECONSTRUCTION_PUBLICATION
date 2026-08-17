#!/usr/bin/env python3

"""
Script: Pareto-style scatter between two variables of the same pkl
Plots one variable (e.g. Completeness) against another (e.g. Purity) from the
same datafile, one point/curve per --configs/--names combination, with error
bars propagated from the dataframe's error column. Meant to visualize a
trade-off (Pareto frontier) rather than compute a single winning metric.
"""

from _bootstrap import ensure_src_path

ensure_src_path()

import re

import matplotlib.lines as mlines
from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_config_label_from_args, make_config_color_and_style_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_legend_style, create_common_subplots, apply_note_to_figure, add_centered_suptitle
from common_args import add_common_args, resolve_axis_label, map_iterable_label, map_iterable_color

parser = argparse.ArgumentParser(
    description="Scatter one variable against another (e.g. Purity vs Completeness) across configs/names",
)

add_common_args(
    parser,
    [
        "datafile",
        "configs",
        "names",
        "variables",
        "select",
        "save_values",
        "remove_value",
        "iterable",
        "reduce",
        "x",
        "y",
        "labelx",
        "labely",
        "labelz",
        "rangex",
        "rangey",
        "title",
        "output",
        "subfolder",
        "note",
        "debug",
    ],
    overrides={
        "datafile": {
            "required": True,
            "help": "Name of the input data file (pkl format)",
        },
        "variables": {
            "required": True,
            "help": "Exactly two Variable values: x-axis metric then y-axis metric (e.g. Completeness Purity)",
        },
        "x": {
            "default": "Values",
            "help": "DataFrame column used to align the two variables' points (e.g. energy bins)",
        },
        "y": {
            "default": "Counts",
            "help": "DataFrame column holding the metric value to scatter",
        },
    },
)

parser.add_argument(
    "--error_column",
    type=str,
    default="CountsError",
    help="DataFrame column with per-point errors for --y (used for error bars and weighted aggregation)",
)

parser.add_argument(
    "--aggregate",
    type=str,
    choices=["weighted_mean", "mean", "none"],
    default="weighted_mean",
    help=(
        "How to combine multiple --x bins per name into point(s): "
        "'weighted_mean'/'mean' collapse to a single point per name, "
        "'none' plots every bin as its own point"
    ),
)

parser.add_argument(
    "--connect",
    action="store_true",
    default=False,
    help="Draw a line connecting the per-name points, in the order given by --names (only with --aggregate != none)",
)

parser.add_argument(
    "--iterable_color_mapping",
    type=str,
    default=None,
    help=(
        "Optional mapping dictionary name from plot_params mappings used to "
        "set --iterable point colors (supports Cn and rgb(r,g,b))"
    ),
)

parser.add_argument(
    "--annotate",
    action="store_true",
    default=False,
    help="Label each aggregated point with its config/name",
)

parser.add_argument(
    "--annotate_bins",
    action="store_true",
    default=False,
    help="When --aggregate none, label each point with its --x value",
)

parser.add_argument(
    "--label_map",
    nargs="+",
    default=None,
    metavar="RAW_NAME=DISPLAY_LABEL",
    help=(
        "Exact --names overrides for the legend, e.g. --label_map "
        "'marley=AdjChannels 3' (checked before --label_regex)."
    ),
)

parser.add_argument(
    "--label_regex",
    nargs=2,
    default=None,
    metavar=("PATTERN", "REPLACEMENT"),
    help=(
        "re.sub(PATTERN, REPLACEMENT, name) applied to legend labels for names "
        "not covered by --label_map, e.g. --label_regex 'marley_adjchannel(\\d+)' "
        "'AdjChannels \\1'"
    ),
)

parser.add_argument(
    "--label_regex_scale",
    type=float,
    default=None,
    help=(
        "Divide --label_regex's first capture group (\\1), interpreted as a "
        "number, by this factor before substitution, e.g. --label_regex_scale 2 "
        "turns captured '20' into '10' wherever \\1 appears in REPLACEMENT."
    ),
)

args = parser.parse_args()


def _format_number(value):
    return str(int(value)) if value == int(value) else str(value)


def _format_iterable_value(value):
    try:
        return _format_number(float(value))
    except (TypeError, ValueError):
        return str(value)


def _iterable_display_label(iterable_value, iterable_name):
    mapped = map_iterable_label(iterable_value, iterable_name)
    return mapped if mapped != str(iterable_value) else _format_iterable_value(iterable_value)


def _build_label_resolver(args):
    exact = {}
    for pair in getattr(args, "label_map", None) or []:
        if "=" not in pair:
            rprint(
                f"[yellow]Warning:[/yellow] Ignoring malformed --label_map entry '{pair}' (expected raw=Display Label)."
            )
            continue
        key, _, value = pair.partition("=")
        exact[key] = value

    pattern = None
    replacement = None
    scale = getattr(args, "label_regex_scale", None)
    if getattr(args, "label_regex", None):
        pattern = re.compile(args.label_regex[0])
        replacement = args.label_regex[1]

    def _expand(match):
        template = replacement
        if scale and match.group(1) is not None:
            try:
                scaled = float(match.group(1)) / scale
                template = template.replace(r"\1", _format_number(scaled))
            except ValueError:
                pass
        return match.expand(template)

    def resolve(name):
        if name is None:
            return name
        if name in exact:
            return exact[name]
        if pattern is not None:
            new_name, n = pattern.subn(_expand, name)
            if n > 0:
                return new_name
        return name

    return resolve


def _extract_triplet(subset, x_col, y_col, err_col):
    columns = [x_col, y_col]
    has_err = err_col is not None and err_col in subset.columns
    if has_err:
        columns.append(err_col)

    expanded = subset.explode(column=columns)
    if expanded.empty:
        return None, None, None

    try:
        x = expanded[x_col].astype(float).to_numpy()
        y = expanded[y_col].astype(float).to_numpy()
        e = expanded[err_col].astype(float).to_numpy() if has_err else np.full_like(y, np.nan)
    except (ValueError, TypeError):
        return None, None, None

    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y, e = x[mask], y[mask], e[mask]

    if x.size == 0:
        return None, None, None

    return x, y, e


def _weighted_combine(values, errors):
    values = np.asarray(values, dtype=float)
    errors = np.asarray(errors, dtype=float)
    valid = np.isfinite(errors) & (errors > 0)
    if not np.any(valid):
        return float(np.mean(values)), np.nan
    w = 1.0 / errors[valid] ** 2
    mean = float(np.sum(values[valid] * w) / np.sum(w))
    err = float(1.0 / np.sqrt(np.sum(w)))
    return mean, err


def _plain_combine(values, errors):
    values = np.asarray(values, dtype=float)
    n = values.size
    mean = float(np.mean(values))
    err = float(np.std(values, ddof=1) / np.sqrt(n)) if n > 1 else np.nan
    return mean, err


def _normalize_color(color, cycle_colors):
    if isinstance(color, str) and color.startswith("C") and color[1:].isdigit():
        return cycle_colors[int(color[1:]) % len(cycle_colors)]
    return color


def _get_cycle_colors():
    return plt.rcParams["axes.prop_cycle"].by_key().get("color", [f"C{i}" for i in range(10)])


def _assign_fallback_colors(explicit):
    """explicit: list of (color_or_None, linestyle), in display order. Returns a
    same-order list of (color, linestyle) with None colors filled from the
    matplotlib cycle, skipping colors already explicitly claimed elsewhere in
    the list so the auto-cycle can't collide with an explicit color."""
    cycle_colors = _get_cycle_colors()
    used = {_normalize_color(c, cycle_colors) for c, _ in explicit if c is not None}
    fallback_pool = [c for c in cycle_colors if c not in used] or cycle_colors
    fallback_iter = iter(fallback_pool)

    resolved = []
    for color, linestyle in explicit:
        if color is None:
            try:
                color = next(fallback_iter)
            except StopIteration:
                fallback_iter = iter(fallback_pool)
                color = next(fallback_iter)
        resolved.append((color, linestyle))
    return resolved


def _resolve_unit_colors(args, units):
    """Resolve a (color, linestyle) per unit (in the same order as `units`),
    avoiding collisions between explicit name_color/config_color/iterable-color
    entries and matplotlib's own auto-cycle fallback (both of which otherwise
    independently start at C0). Returned as a list, not a dict, since a unit's
    --iterable value may be NaN and thus unsafe as a dict key."""
    explicit = []
    for unit in units:
        if unit["iterable"] is not None:
            # config/name are constant across an --iterable sweep, so falling back to
            # their color would make every point in the sweep identical; only an
            # explicit --iterable_color_mapping entry counts here, otherwise let the
            # auto-cycle fallback below differentiate by iterable value instead.
            color = map_iterable_color(
                unit["iterable"], getattr(args, "iterable_color_mapping", None), iterable_name=args.iterable
            )
            linestyle = None
        else:
            color, linestyle = make_config_color_and_style_from_args(args, config=unit["config"], name=unit["name"])
        explicit.append((color, linestyle))

    return _assign_fallback_colors(explicit)


def _resolve_group_colors(args, groups):
    """Resolve a (color, linestyle) per (config, name) group, in the same order
    as `groups` -- used in dual (color=group, shape=iterable) mode, where color
    must stay constant across a group's whole --iterable sweep."""
    explicit = [make_config_color_and_style_from_args(args, config=c, name=n) for c, n in groups]
    return _assign_fallback_colors(explicit)


_MARKER_CYCLE = ["o", "s", "^", "D", "v", "P", "X", "*", "h", "p"]


def _resolve_iterable_markers(iterable_values):
    """Assign a distinct marker shape per unique --iterable value, consistent
    across every (config, name) group, so shape alone identifies the value."""
    return {value: _MARKER_CYCLE[i % len(_MARKER_CYCLE)] for i, value in enumerate(iterable_values)}


def _rank_quadrants_by_data_density(ax, xs, ys):
    """Order the 4 legend corners from emptiest to most crowded, by counting how
    many plotted (x, y) points fall in each quadrant of the current axes limits.
    Used to auto-place two legends in different, data-sparse corners instead of
    a hardcoded corner or matplotlib's own independent (and mutually unaware)
    'best' pick per legend."""
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xmid = (xlim[0] + xlim[1]) / 2.0
    ymid = (ylim[0] + ylim[1]) / 2.0
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)

    counts = {
        "lower left": int(np.sum((xs <= xmid) & (ys <= ymid))),
        "lower right": int(np.sum((xs > xmid) & (ys <= ymid))),
        "upper left": int(np.sum((xs <= xmid) & (ys > ymid))),
        "upper right": int(np.sum((xs > xmid) & (ys > ymid))),
    }
    return sorted(counts, key=counts.get)


def main():
    if len(args.variables) != 2:
        rprint(
            f"[red]Error:[/red] --variables must have exactly two entries (x-variable y-variable), got {args.variables}."
        )
        return

    x_variable, y_variable = args.variables

    df = import_data(args)
    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    resolve_label_name = _build_label_resolver(args)

    units = []
    for config, name in zip(configs, names):
        if config is not None and name is None:
            df_config = df[(df["Config"] == config)]
        elif config is None and name is not None:
            df_config = df[(df["Name"] == name)]
        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]
        else:
            df_config = df.copy()

        subset_base = filter_dataframe(df_config, args)
        if subset_base.empty:
            rprint(f"[yellow]Warning:[/yellow] No data for {config=}, {name=}. Skipping.")
            continue

        if args.iterable is not None:
            if args.iterable not in subset_base.columns:
                rprint(f"[red]Error:[/red] Iterable column '{args.iterable}' not found in dataframe.")
                continue
            iterable_values = sorted(
                subset_base[subset_base[args.iterable].notna()][args.iterable].unique().tolist()
            )
            if not iterable_values:
                rprint(
                    f"[yellow]Warning:[/yellow] No non-null '{args.iterable}' values for {config=}, {name=}. Skipping."
                )
                continue
        else:
            iterable_values = [None]

        reduce_active = len(iterable_values) > 8 and args.reduce

        for jdx, iterable_value in enumerate(iterable_values):
            if reduce_active and jdx % 2 == 1:
                rprint(f"\tSkipping plotting for {args.iterable}={iterable_value} to avoid overcrowding")
                continue

            subset = (
                subset_base[subset_base[args.iterable] == iterable_value]
                if iterable_value is not None
                else subset_base
            )

            row_x = subset[subset["Variable"] == x_variable]
            row_y = subset[subset["Variable"] == y_variable]
            if row_x.empty or row_y.empty:
                rprint(
                    f"[yellow]Warning:[/yellow] Missing '{x_variable}' or '{y_variable}' for "
                    f"{config=}, {name=}, {args.iterable}={iterable_value}. Skipping."
                )
                continue

            xb, xv, xe = _extract_triplet(row_x, args.x, args.y, args.error_column)
            yb, yv, ye = _extract_triplet(row_y, args.x, args.y, args.error_column)
            if xb is None or yb is None:
                rprint(
                    f"[yellow]Warning:[/yellow] Could not extract numeric arrays for "
                    f"{config=}, {name=}, {args.iterable}={iterable_value}. Skipping."
                )
                continue

            if xb.size != yb.size or not np.allclose(xb, yb, equal_nan=True):
                rprint(
                    f"[yellow]Warning:[/yellow] '{x_variable}' and '{y_variable}' bins are not aligned for "
                    f"{config=}, {name=}, {args.iterable}={iterable_value}. Skipping."
                )
                continue

            units.append(
                {
                    "config": config,
                    "name": name,
                    "iterable": iterable_value,
                    "xb": xb, "xv": xv, "xe": xe,
                    "yb": yb, "yv": yv, "ye": ye,
                }
            )

    if not units:
        rprint("[yellow]Warning:[/yellow] No valid points available to plot.")
        return

    fig, ax = create_common_subplots(nrows=1, ncols=1)

    # When several --configs/--names combinations are swept over the same
    # --iterable, a single legend would need one entry per (group x iterable
    # value) combination. Instead, disentangle the two dimensions visually:
    # color identifies the config/name group, marker shape identifies the
    # iterable value, and each dimension gets its own legend.
    unique_groups = list(dict.fromkeys((u["config"], u["name"]) for u in units))
    dual_mode = args.iterable is not None and len(unique_groups) > 1

    if dual_mode:
        group_color_map = dict(zip(unique_groups, _resolve_group_colors(args, unique_groups)))
        all_iterable_values = sorted({u["iterable"] for u in units if u["iterable"] is not None})
        marker_map = _resolve_iterable_markers(all_iterable_values)
    else:
        unit_colors = _resolve_unit_colors(args, units)

    aggregate_points = []  # (group_key, label, color, px, py, pxe, pye)
    plotted_x, plotted_y = [], []  # every drawn point, for auto legend placement

    for idx, unit in enumerate(units):
        config, name, iterable_value = unit["config"], unit["name"], unit["iterable"]
        xb, xv, xe = unit["xb"], unit["xv"], unit["xe"]
        yb, yv, ye = unit["yb"], unit["yv"], unit["ye"]
        group_key = (config, name)

        iterable_label = _iterable_display_label(iterable_value, args.iterable) if iterable_value is not None else None
        label = make_config_label_from_args(
            args, config=config, name=resolve_label_name(name), iterable=iterable_label
        )

        if dual_mode:
            color = group_color_map[group_key][0]
            marker = marker_map[iterable_value]
            point_label = None  # legends are built separately from proxy handles below
        else:
            color, _linestyle = unit_colors[idx]
            marker = "o"
            point_label = label

        if args.aggregate == "none":
            ax.errorbar(
                xv,
                yv,
                xerr=xe if np.isfinite(xe).any() else None,
                yerr=ye if np.isfinite(ye).any() else None,
                marker=marker,
                linestyle="-" if args.connect else "None",
                color=color,
                label=point_label,
                capsize=2,
            )
            plotted_x.extend(xv.tolist())
            plotted_y.extend(yv.tolist())
            if args.annotate_bins:
                for bx, px, py in zip(xb, xv, yv):
                    ax.annotate(
                        f"{bx:g}",
                        (px, py),
                        textcoords="offset points",
                        xytext=(4, 4),
                        fontsize=linelabelfontsize,
                    )
        else:
            combine = _weighted_combine if args.aggregate == "weighted_mean" else _plain_combine
            px, pxe = combine(xv, xe)
            py, pye = combine(yv, ye)
            ax.errorbar(
                [px],
                [py],
                xerr=[pxe] if np.isfinite(pxe) else None,
                yerr=[pye] if np.isfinite(pye) else None,
                marker=marker,
                ms=8,
                linestyle="None",
                color=color,
                label=point_label,
                capsize=3,
            )
            if args.annotate:
                ax.annotate(
                    label,
                    (px, py),
                    textcoords="offset points",
                    xytext=(6, 6),
                    fontsize=linelabelfontsize,
                )
            aggregate_points.append((group_key, label, color, px, py, pxe, pye))
            plotted_x.append(px)
            plotted_y.append(py)

    if args.connect and args.aggregate != "none" and len(aggregate_points) > 1:
        if dual_mode:
            points_by_group = {}
            for group_key, _label, color, px, py, _pxe, _pye in aggregate_points:
                entry = points_by_group.setdefault(group_key, {"color": color, "points": []})
                entry["points"].append((px, py))
            for entry in points_by_group.values():
                if len(entry["points"]) > 1:
                    px_all = [p[0] for p in entry["points"]]
                    py_all = [p[1] for p in entry["points"]]
                    ax.plot(px_all, py_all, color=entry["color"], linestyle="--", linewidth=1, alpha=0.6, zorder=0)
        else:
            px_all = [p[3] for p in aggregate_points]
            py_all = [p[4] for p in aggregate_points]
            ax.plot(px_all, py_all, color="gray", linestyle="--", linewidth=1, zorder=0)

    if not ax.has_data():
        rprint("[yellow]Warning:[/yellow] No valid points available to plot.")
        plt.close(fig)
        return

    ax.set_xlabel(
        resolve_axis_label(args.labelx, x_variable, None),
        fontsize=xlabelfontsize,
    )
    ax.set_ylabel(
        resolve_axis_label(args.labely, y_variable, None),
        fontsize=ysublabelfontsize,
    )

    if args.annotate or args.annotate_bins:
        ax.margins(x=0.25, y=0.15)
    elif dual_mode:
        ax.margins(x=0.15, y=0.1)

    if args.rangex is not None:
        ax.set_xlim(args.rangex)
    if args.rangey is not None:
        ax.set_ylim(args.rangey)

    if dual_mode:
        # Auto-pick two distinct, data-sparse corners from the actual plotted
        # points, rather than a hardcoded corner or matplotlib's own per-legend
        # "best" (which picks each legend's spot independently and can stack
        # them on top of each other). The taller legend gets the emptiest
        # corner -- it's the one that most needs the extra room; a short
        # legend fits fine in the second-sparsest corner even if that corner
        # nominally has a bit more data in it.
        color_ncol = 2 if len(unique_groups) > 6 else 1
        shape_ncol = 2 if len(all_iterable_values) > 6 else 1
        color_rows = -(-len(unique_groups) // color_ncol)
        shape_rows = -(-len(all_iterable_values) // shape_ncol)

        ranked_corners = _rank_quadrants_by_data_density(ax, plotted_x, plotted_y)
        if shape_rows > color_rows:
            shape_loc, color_loc = ranked_corners[0], ranked_corners[1]
        else:
            color_loc, shape_loc = ranked_corners[0], ranked_corners[1]

        color_handles = [
            mlines.Line2D(
                [], [],
                marker="o",
                linestyle="None",
                color=group_color_map[group_key][0],
                label=make_config_label_from_args(
                    args, config=group_key[0], name=resolve_label_name(group_key[1]), iterable=None
                ),
            )
            for group_key in unique_groups
        ]
        leg_color = apply_legend_style(
            ax,
            handles=color_handles,
            labels=[h.get_label() for h in color_handles],
            title=args.labelz,
            capitalize_labels=getattr(args, "capitalize_legend", False),
            loc=color_loc,
            ncol=color_ncol,
        )
        ax.add_artist(leg_color)

        shape_handles = [
            mlines.Line2D(
                [], [],
                marker=marker_map[value],
                linestyle="None",
                color="black",
                label=_iterable_display_label(value, args.iterable),
            )
            for value in all_iterable_values
        ]
        apply_legend_style(
            ax,
            handles=shape_handles,
            labels=[h.get_label() for h in shape_handles],
            title=args.iterable,
            capitalize_labels=False,
            loc=shape_loc,
            ncol=shape_ncol,
        )
    else:
        apply_legend_style(
            ax,
            title=args.labelz if args.labelz is not None else args.iterable,
            capitalize_labels=getattr(args, "capitalize_legend", False),
        )

    figure_title = make_title_from_args(args)
    add_centered_suptitle(fig, figure_title, fontsize=titlefontsize)

    apply_note_to_figure(fig, getattr(args, "note", None))

    output_file = make_name_from_args(
        args,
        None,
        prefix=None,
        suffix=f"{x_variable}_vs_{y_variable}_pareto.png",
    )
    default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
    save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)


if __name__ == "__main__":
    main()
