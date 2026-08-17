#!/usr/bin/env python3

"""
Script 1: Simple Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_subtitle_from_args
from lib.imports import import_data, prepare_import
from lib.functions import resolution
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import math

from lib.plot import (
    apply_legend_style,
    plot_data,
    create_common_subplots,
    apply_note_to_figure,
    add_centered_suptitle,
    draw_vertical_lines,
    draw_horizontal_lines,
    place_point_label,
)
from common_args import add_common_args, map_iterable_label, map_iterable_color, resolve_axis_label


# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
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
        "reduce",
        "labelx",
        "labely",
        "labelz",
        "logx",
        "logy",
        "rangex",
        "rangey",
        "plot_style",
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
        "debug",
    ],
    overrides={
        "datafile": {
            "required": True,
            "help": "Name of the input data file (pkl format)",
        },
        "names": {"flags": ["--names"]},
        "iterable": {"required": True},
        "select": {
            "help": "If provided, use these key to apply save_values filtering"
        },
        "save_values": {
            "help": "If select key is provided, save plots for which select key equals this value"
        },
        "x": {"required": True},
        "y": {"required": True},
        "plot_style": {
            "help": "Plot line style for connected plots (options: -, --, :, -., solid, dashed, dotted, dashdot, none)",
        },
        "plot_type": {
            "choices": ["scatter", "line", "bar", "barh", "step", "plot", "errorbar"],
            "help": "Explicit plot type override (scatter, line, bar, barh, step, plot, errorbar)",
        },
    },
)

parser.add_argument(
    "--errorx",
    action="store_true",
    help="Include error bars on x-axis",
    default=False,
)

parser.add_argument(
    "--stacked",
    action="store_true",
    help="Create stacked histograms",
    default=False,
)

parser.add_argument(
    "--comparable",
    "-c",
    type=str,
    default=None,
    help=(
        "Optional DataFrame column to overlay as a secondary line dimension. "
        "Each unique value in this column gets a distinct linestyle."
    ),
)

parser.add_argument(
    "--comparable_linestyles",
    nargs="+",
    type=str,
    default=None,
    help=(
        "Linestyles to cycle through for comparable values (e.g. solid dashed dotted). "
        "Defaults to cycling through [-, --, :, -.]."
    ),
)

parser.add_argument(
    "--comparable_reverse",
    action="store_true",
    default=False,
    help="Reverse the order of linestyles assigned to comparable values.",
)

parser.add_argument(
    "--comparable_linewidths",
    nargs="+",
    type=float,
    default=None,
    help=(
        "Linewidth(s) for comparable stages. "
        "Single value: applies to all stages. "
        "N values matching the number of comparables: per-stage linewidth."
    ),
)

parser.add_argument(
    "--comparable_fill_strength",
    action="store_true",
    default=False,
    help=(
        "Encode comparable values with fill alpha instead of linestyle. "
        "All comparables are drawn with a solid line; fill opacity decreases "
        "from the first to the last comparable value. Mutually exclusive with "
        "--fill (fill_alpha is ignored when this flag is active)."
    ),
)

parser.add_argument(
    "--iterable_reverse",
    action="store_true",
    default=False,
    help=(
        "Reverse the order of linestyles assigned to --iterable values "
        "under --invert_style (the --iterable-driven counterpart of "
        "--comparable_reverse; has no effect otherwise)."
    ),
)

parser.add_argument(
    "--comparable_mapping",
    type=str,
    default=None,
    help=(
        "Optional mapping dictionary name from plot_params mappings used to "
        "rename --comparable values (e.g. Stage) in the legend."
    ),
)

parser.add_argument(
    "--comparable_title",
    type=str,
    default=None,
    help="Legend heading for the comparable overlay section (defaults to the --comparable column name). Pass 'None' to suppress the heading entirely.",
)

parser.add_argument(
    "--invert_style",
    action="store_true",
    default=False,
    help=(
        "Swap color/linestyle roles: colors are assigned to --comparable "
        "values and linestyles to --iterable values, instead of the default "
        "(colors on --iterable, linestyles on --comparable)."
    ),
)

parser.add_argument(
    "--connect",
    action="store_true",
    help="(Deprecated) Connect data points with lines; use `--plot_type line` instead",
    default=False,
)

parser.add_argument(
    "--extrapolate",
    action="store_true",
    help="Show extrapolated data (marked by an '{y}Extrapolated' column) as a dashed continuation of the line",
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
    "--overlay_names",
    action="store_true",
    default=False,
    help=(
        "Combine all --configs/--names combinations into a single figure "
        "instead of producing one figure per combination. All loaded data is "
        "treated as one dataset; use --iterable to distinguish sources by color."
    ),
)

parser.add_argument(
    "--sum_iterables",
    nargs="+",
    default=None,
    help=(
        "Iterable values to sum additively into a single combined line instead "
        "of plotting individually. When --comparable is active the sum is "
        "computed per comparable value so each stage keeps its own linestyle."
    ),
)

parser.add_argument(
    "--sum_label",
    type=str,
    default="Combined",
    help="Legend label for the line produced by --sum_iterables.",
)

parser.add_argument(
    "--sum_color",
    type=str,
    default=None,
    help="Color for the --sum_iterables line (e.g. C1, red, #RRGGBB). Auto-assigned if omitted.",
)

parser.add_argument(
    "--fill",
    action="store_true",
    default=False,
    help="Fill step histograms with a semi-transparent solid color under each line.",
)

parser.add_argument(
    "--fill_alpha",
    nargs="+",
    type=float,
    default=None,
    help=(
        "Opacity of the histogram fill (0–1). "
        "With --fill: sets the flat fill opacity (default 0.15). "
        "With --comparable_fill_strength (single value): multiplies the default alpha sequence "
        "[0.8, 0.55, 0.35, 0.15]; omitting the flag leaves the sequence unchanged. "
        "With --comparable_fill_strength (N values matching the number of comparables): "
        "each value is used as the direct alpha for the corresponding comparable layer."
    ),
)

parser.add_argument(
    "--fill_hatch_color",
    action="store_true",
    default=False,
    help=(
        "Draw hatch lines at full opacity in the data-line color instead of "
        "dimming them with --fill_alpha. The solid fill behind the hatch is "
        "still rendered at --fill_alpha."
    ),
)

parser.add_argument(
    "--comparable_hatches",
    nargs="+",
    type=str,
    default=None,
    help=(
        "Hatch patterns per comparable value in order (e.g. '' '/' '\\\\' 'x'). "
        "Defaults to cycling through [\"\", \"/\", \"\\\\\\\\\", \"x\"]. "
        "Respects --comparable_reverse. Only used when --fill is active."
    ),
)

args = parser.parse_args()

_MISSING_ITERABLE_MAPPING_WARNING_SHOWN = False

_COMPARABLE_LINESTYLES = ["-", "--", ":", "-."]
_COMPARABLE_HATCHES = ["", "/", "\\", "x", ".", "o"]
_COMPARABLE_ALPHAS = [0.8, 0.55, 0.35, 0.15]

_EXTRAPOLATED_LINESTYLE = "--"


def _build_extrapolated_segments(x, y, extrapolated_mask):
    """Return (x_norm, y_norm, x_ext, y_ext) where x_ext/y_ext is ready to plot
    as a single call with NaN breaks between disconnected extrapolated groups.
    Each group is padded with the adjacent non-extrapolated point on both sides
    so the dashed segment visually touches the solid segment.
    """
    x_norm = x[~extrapolated_mask]
    y_norm = y[~extrapolated_mask]

    ext_indices = np.where(extrapolated_mask)[0]
    breaks = np.where(np.diff(ext_indices) > 1)[0] + 1
    groups = np.split(ext_indices, breaks)

    parts_x, parts_y = [], []
    for grp in groups:
        xi = list(x[grp])
        yi = list(y[grp])
        # prepend last adjacent normal point
        i0 = grp[0]
        if i0 > 0 and not extrapolated_mask[i0 - 1]:
            xi = [x[i0 - 1]] + xi
            yi = [y[i0 - 1]] + yi
        # append first adjacent normal point
        i1 = grp[-1]
        if i1 + 1 < len(x) and not extrapolated_mask[i1 + 1]:
            xi = xi + [x[i1 + 1]]
            yi = yi + [y[i1 + 1]]
        parts_x.append(np.array(xi))
        parts_y.append(np.array(yi))

    nan_sep = np.array([np.nan])
    x_ext = np.concatenate([v for p in parts_x for v in (p, nan_sep)][:-1]) if parts_x else np.array([])
    y_ext = np.concatenate([v for p in parts_y for v in (p, nan_sep)][:-1]) if parts_y else np.array([])

    return x_norm, y_norm, x_ext, y_ext


def _resolve_comparable_linestyle(index, args, n_total=None, reverse=None):
    if getattr(args, "comparable_fill_strength", False):
        return "-"
    user_styles = getattr(args, "comparable_linestyles", None)
    styles = list(user_styles) if user_styles else list(_COMPARABLE_LINESTYLES)
    effective_reverse = getattr(args, "comparable_reverse", False) if reverse is None else reverse
    if effective_reverse and n_total is not None:
        index = n_total - 1 - index
    return styles[index % len(styles)]


def _resolve_comparable_fill_alpha(index, args, n_total=None):
    if getattr(args, "comparable_reverse", False) and n_total is not None:
        index = n_total - 1 - index
    fill_alpha = getattr(args, "fill_alpha", None)
    if fill_alpha is not None and n_total is not None and len(fill_alpha) == n_total:
        return fill_alpha[index % len(fill_alpha)]
    alpha = _COMPARABLE_ALPHAS[index % len(_COMPARABLE_ALPHAS)]
    if fill_alpha:
        alpha = min(alpha * fill_alpha[0], 1.0)
    return alpha


def _resolve_comparable_linewidth(index, args, n_total=None):
    lws = getattr(args, "comparable_linewidths", None)
    if not lws:
        return None
    if getattr(args, "comparable_reverse", False) and n_total is not None:
        index = n_total - 1 - index
    if n_total is not None and len(lws) == n_total:
        return lws[index % len(lws)]
    return lws[0]


def _resolve_comparable_hatch(index, args, n_total=None):
    user_hatches = getattr(args, "comparable_hatches", None)
    hatches = list(user_hatches) if user_hatches else list(_COMPARABLE_HATCHES)
    if getattr(args, "comparable_reverse", False) and n_total is not None:
        index = n_total - 1 - index
    return hatches[index % len(hatches)]


def _resolve_comparable_color(index, args, n_total=None, reverse=None):
    """Positional 'Cn' fallback used whenever a value has no explicit
    --iterable_color_mapping entry. Mirrors _resolve_comparable_linestyle's
    reverse handling so --comparable_reverse/--iterable_reverse consistently
    reverse whichever visual channel (color or linestyle) that dimension is
    currently driving."""
    if reverse and n_total is not None:
        index = n_total - 1 - index
    return f"C{index}"


def _apply_iterable_legend(
    ax,
    iterable_title,
    handles,
    labels,
    comparable_col,
    comparable_style_map,
    capitalize_labels,
    comparable_alpha_map=None,
    **loc_kwargs,
):
    """Draw the iterable legend. When a comparable overlay is active, fold its
    linestyle key into the *same* legend (as a second, bold-headed section)
    rather than a separate legend artist, so matplotlib's own placement search
    (loc="best") treats both as one block and every entry shares one left edge.
    """
    if not comparable_style_map and not comparable_alpha_map:
        return apply_legend_style(
            ax,
            title=iterable_title,
            handles=handles,
            labels=labels,
            capitalize_labels=capitalize_labels,
            **loc_kwargs,
        )

    if comparable_alpha_map:
        secondary_proxies = [
            mpatches.Patch(facecolor="gray", alpha=alpha, edgecolor="black", linewidth=1.0)
            for alpha in comparable_alpha_map.values()
        ]
        secondary_labels = list(comparable_alpha_map.keys())
    else:
        secondary_proxies = [
            mlines.Line2D([], [], color="black", linestyle=style, linewidth=1.5)
            for style in comparable_style_map.values()
        ]
        secondary_labels = list(comparable_style_map.keys())

    _secondary_header = comparable_col is not None
    combined_handles = (
        [mlines.Line2D([], [], linestyle="none", marker="none")]
        + list(handles)
        + ([mlines.Line2D([], [], linestyle="none", marker="none")] if _secondary_header else [])
        + secondary_proxies
    )
    combined_labels = (
        [str(iterable_title)]
        + list(labels)
        + ([str(comparable_col)] if _secondary_header else [])
        + secondary_labels
    )

    return apply_legend_style(
        ax,
        title=None,
        handles=combined_handles,
        labels=combined_labels,
        capitalize_labels=capitalize_labels,
        **loc_kwargs,
    )

def main():
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    if args.iterable not in df.columns:
        available_columns = ", ".join(map(str, df.columns.tolist()))
        rprint(
            f"[red]Error:[/red] Iterable column '{args.iterable}' was not found in the imported data. Available columns: {available_columns}"
        )
        return

    # Select the entries in the dataframe with with name matching args.names and nake a plot for each iterable
    if args.variables is None:
        n_vars, nrows, ncols = 1, 1, 1
    else:
        n_vars = len(args.variables)
        if n_vars <= 3:
            nrows, ncols = 1, n_vars
        else:
            ncols = math.ceil(math.sqrt(n_vars))
            nrows = math.ceil(n_vars / ncols)

    rprint(f"Number of unique variables for plotting: {n_vars} ({nrows}x{ncols} grid)")

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    if getattr(args, "overlay_names", False):
        configs = [None]
        names = [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = create_common_subplots(
            nrows=nrows,
            ncols=ncols,
        )
        ax_flat = np.asarray(ax).flatten()

        if config is not None and name is None:
            df_config = df[(df["Config"] == config)]

        elif config is None and name is not None:
            df_config = df[(df["Name"] == name)]

        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]

        else:
            df_config = df.copy()

        rprint(
            f"Dataframe entries for this config and iterable: {len(df_config)}, Unique iterable values: {df_config[args.iterable].unique()}"
        )
        bottom = None
        variables = args.variables if args.variables is not None else [None]
        last_x = np.array([])
        axes_with_extrapolated = {}  # ax -> [(primary_value_label, color), ...]
        comparable_style_map = {}  # comparable_label -> linestyle (secondary legend, default mode)
        comparable_alpha_map = {}  # comparable_label -> fill alpha (secondary legend, --comparable_fill_strength mode)
        iterable_style_map = {}  # iterable_label -> linestyle (secondary legend, --invert_style)
        subset_by_variable = {}  # variable idx -> a representative variable-filtered dataframe
        # Drop None values from df in iterable column
        iterable_column = str(args.iterable)
        df_config = df_config[df_config[iterable_column].notna()]
        # Derive from the --select/--remove_value-filtered view, not the raw
        # column: a value removed entirely (e.g. --remove_value on the
        # iterable column itself) would otherwise still claim a color/
        # linestyle slot -- and the "first drawn series" position used for
        # legend labeling -- despite every one of its subsets coming up
        # empty later, leaving the legend blank instead of just short one
        # entry.
        _filtered_for_legend = filter_dataframe(df_config, args)
        iterable_values = (
            _filtered_for_legend[iterable_column].dropna().unique()
            if iterable_column in _filtered_for_legend.columns
            else df_config[iterable_column].unique()
        )
        _color_mapping_name = getattr(args, "iterable_color_mapping", None)
        if _color_mapping_name is not None:
            _mapping_dict = get_mapping_dict(_color_mapping_name)
            if _mapping_dict is not None:
                _in_map = [v for v in _mapping_dict if v in set(iterable_values)]
                _not_in_map = [v for v in iterable_values if v not in set(_mapping_dict)]
                iterable_values = np.array(_in_map + _not_in_map)

        sum_set = {str(s) for s in (getattr(args, "sum_iterables", None) or [])}
        sum_label_base = getattr(args, "sum_label", "Combined")

        # When the sum label is present in the color mapping, insert it into
        # iterable_values at its mapped position so the sum line is drawn in
        # the correct z-order rather than always last (post-loop).
        _sum_label_inline = False
        if sum_set and _color_mapping_name is not None:
            _md_sum = get_mapping_dict(_color_mapping_name)
            if _md_sum is not None and sum_label_base in _md_sum:
                _map_keys = list(_md_sum.keys())
                _sum_map_pos = _map_keys.index(sum_label_base)
                _insert_at = len(iterable_values)
                for _i, _v in enumerate(iterable_values):
                    if str(_v) in _md_sum and _map_keys.index(str(_v)) > _sum_map_pos:
                        _insert_at = _i
                        break
                iterable_values = np.insert(iterable_values.astype(object), _insert_at, sum_label_base)
                _sum_label_inline = True

        reduce_active = iterable_values.size > 8 and args.reduce
        invert_style = getattr(args, "invert_style", False)
        # Exclude sum_set members and the synthetic sum_label_base from color
        # and linestyle slots: they have no dataframe rows and the sum label
        # gets its color from the mapping rather than a fallback index.
        color_idx_by_iterable = {
            value: color_idx
            for color_idx, value in enumerate(
                v for j, v in enumerate(iterable_values)
                if not (reduce_active and j % 2 == 1)
                and str(v) not in sum_set
                and str(v) != sum_label_base
            )
        }
        # Values folded into --sum_iterables never draw as their own line, so
        # they're excluded here: giving them a linestyle slot would both waste
        # a cycle position (forcing real lines to collide sooner) and add a
        # legend entry for a linestyle nothing on the plot actually uses.
        # --sum_iterables itself draws as its own single line under
        # --invert_style, though, so it takes the next slot in the same
        # cycle rather than a fixed style -- it's one more --iterable-family
        # entry, not an exception to the pattern.
        linestyle_idx_by_iterable = {
            value: style_idx
            for style_idx, value in enumerate(
                v for v in color_idx_by_iterable if str(v) not in sum_set
            )
        }
        sum_linestyle_idx = len(linestyle_idx_by_iterable)
        iterable_style_n_total = len(linestyle_idx_by_iterable) + (1 if sum_set else 0)
        if invert_style and iterable_style_n_total > 1:
            for _ival, _iidx in linestyle_idx_by_iterable.items():
                _ival_label = map_iterable_label(
                    _ival, args.iterable, getattr(args, "iterable_mapping", None), len(iterable_values)
                )
                iterable_style_map[_ival_label] = _resolve_comparable_linestyle(
                    _iidx, args, n_total=iterable_style_n_total,
                    reverse=getattr(args, "iterable_reverse", False),
                )
            if sum_set:
                iterable_style_map[sum_label_base] = _resolve_comparable_linestyle(
                    sum_linestyle_idx, args, n_total=iterable_style_n_total,
                    reverse=getattr(args, "iterable_reverse", False),
                )

        comparable_col = getattr(args, "comparable", None)
        _ct = getattr(args, "comparable_title", None)
        comparable_legend_title = None if _ct == "None" else (_ct if _ct is not None else comparable_col)
        global_comparable_values = np.array([])
        if comparable_col is not None and comparable_col in df_config.columns:
            # Reuse the same --select/--remove_value-filtered view computed
            # above for iterable_values, so a removed comparable value is
            # excluded here for the same reason.
            global_comparable_values = (
                _filtered_for_legend[comparable_col].dropna().unique()
                if comparable_col in _filtered_for_legend.columns
                else np.array([])
            )

            if len(global_comparable_values) > 1 and not invert_style:
                _cfs_active = getattr(args, "comparable_fill_strength", False)
                for _gidx, _gval in enumerate(global_comparable_values):
                    _gval_label = map_iterable_label(_gval, comparable_col, getattr(args, "comparable_mapping", None))
                    if _cfs_active:
                        comparable_alpha_map[_gval_label] = _resolve_comparable_fill_alpha(_gidx, args, n_total=len(global_comparable_values))
                    else:
                        comparable_style_map[_gval_label] = _resolve_comparable_linestyle(_gidx, args, n_total=len(global_comparable_values))

        iterable_legend_title = args.labelz if args.labelz is not None else args.iterable
        primary_legend_title = comparable_legend_title if invert_style else iterable_legend_title
        secondary_legend_title = iterable_legend_title if invert_style else comparable_legend_title
        secondary_style_map = iterable_style_map if invert_style else comparable_style_map
        secondary_alpha_map = {} if invert_style else comparable_alpha_map

        _sum_inline_drawn = False
        for (idx, variable), (jdx, iterable) in product(
            enumerate(variables), enumerate(iterable_values)
        ):
            if reduce_active:
                if jdx % 2 == 1 and str(iterable) != sum_label_base:
                    rprint(
                        f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding"
                    )
                    continue

            if sum_set and str(iterable) in sum_set:
                continue

            ax_current = ax_flat[idx]

            # Inline sum-drawing: runs at the z-order position dictated by the
            # mapping rather than always after all regular iterables.
            if _sum_label_inline and str(iterable) == sum_label_base:
                _sum_inline_drawn = True
                _comparable_active_s = comparable_col is not None and global_comparable_values.size > 0
                _comparable_iter_s = list(enumerate(global_comparable_values)) if _comparable_active_s else [(0, None)]
                _n_non_summed_s = len(color_idx_by_iterable)
                _sum_color_s = (
                    getattr(args, "sum_color", None)
                    or map_iterable_color(sum_label_base, getattr(args, "iterable_color_mapping", None))
                    or f"C{_n_non_summed_s}"
                )
                for _sdx_s, _comparable_value_s in _comparable_iter_s:
                    _sum_x_s, _sum_y_s = None, None
                    _sum_x_edges_s = None
                    for _sum_val_s in (getattr(args, "sum_iterables", None) or []):
                        _df_sv = df_config[df_config[args.iterable] == _sum_val_s]
                        if variable is not None and "Variable" in _df_sv.columns:
                            _df_sv = _df_sv[_df_sv["Variable"] == variable]
                        if _comparable_active_s and _comparable_value_s is not None:
                            _df_sv = _df_sv[_df_sv[comparable_col] == _comparable_value_s]
                        _sub_sv = filter_dataframe(_df_sv, args)
                        _ecols = ([args.x, args.y, "Error"] if "Error" in _sub_sv.columns else [args.x, args.y])
                        _sub_sv = _sub_sv.explode(column=_ecols)
                        if _sub_sv.empty:
                            continue
                        try:
                            _xv = _sub_sv[args.x].astype(float).to_numpy()
                            _yv = _sub_sv[args.y].astype(float).to_numpy()
                        except ValueError:
                            continue
                        _mask_sv = ~np.isnan(_xv) & ~np.isnan(_yv)
                        _xv, _yv = _xv[_mask_sv], _yv[_mask_sv]
                        if _xv.size == 0:
                            continue
                        if _sum_y_s is None:
                            _sum_x_s, _sum_y_s = _xv, np.zeros_like(_yv)
                        if _yv.size == _sum_y_s.size:
                            _sum_y_s = _sum_y_s + _yv
                    if _sum_x_s is None or _sum_y_s is None:
                        continue
                    _xbin_s = _sum_x_s[1] - _sum_x_s[0] if len(_sum_x_s) > 1 else 1
                    _sum_x_edges_s = np.linspace(_sum_x_s[0] - _xbin_s / 2, _sum_x_s[-1] + _xbin_s / 2, len(_sum_x_s) + 1)
                    if invert_style and _comparable_active_s:
                        _cmp_color_s = (
                            getattr(args, "sum_color", None)
                            or map_iterable_color(_comparable_value_s, getattr(args, "iterable_color_mapping", None))
                            or _resolve_comparable_color(_sdx_s, args, n_total=len(global_comparable_values), reverse=getattr(args, "comparable_reverse", False))
                        )
                        _cmp_ls_s = _resolve_comparable_linestyle(sum_linestyle_idx, args, n_total=iterable_style_n_total, reverse=getattr(args, "iterable_reverse", False))
                    else:
                        _cmp_color_s = _sum_color_s
                        _cmp_ls_s = (
                            _resolve_comparable_linestyle(_sdx_s, args, n_total=len(global_comparable_values))
                            if _comparable_active_s else getattr(args, "plot_style", None)
                        )
                    _plot_label_s = None if (invert_style and _comparable_active_s) else (sum_label_base if _sdx_s == 0 else None)
                    _cfs_s = getattr(args, "comparable_fill_strength", False)
                    _fill_active_s = getattr(args, "fill", False) or _cfs_s
                    _fill_alpha_s = (_resolve_comparable_fill_alpha(_sdx_s, args, n_total=len(global_comparable_values)) if _cfs_s
                                     else ((getattr(args, "fill_alpha", None) or [0.15])[0] if _fill_active_s else None))
                    _fill_hatch_s = _resolve_comparable_hatch(_sdx_s, args, n_total=len(global_comparable_values)) if _fill_active_s and not _cfs_s else None
                    _lw_s = _resolve_comparable_linewidth(_sdx_s, args, n_total=len(global_comparable_values))
                    rprint(f"\tPlotting sum of {list(sum_set)} ({comparable_col}={_comparable_value_s}), Variable={variable} | color={_cmp_color_s}, linestyle={_cmp_ls_s}, fill_alpha={_fill_alpha_s}, linewidth={_lw_s}")
                    _lw_kw_s = {} if _lw_s is None else {"linewidth": _lw_s}
                    plot_data(args, ax_current, _sum_x_s, x_edges=_sum_x_edges_s, y=_sum_y_s,
                              label=_plot_label_s, color=_cmp_color_s,
                              plot_type=args.plot_type or "line", linestyle=_cmp_ls_s,
                              fill_alpha=_fill_alpha_s, fill_hatch=_fill_hatch_s,
                              fill_hatch_color=getattr(args, "fill_hatch_color", False), **_lw_kw_s)
                continue

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
                        f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}"
                    )
                df_iterable = df_config[
                    (df_config["Variable"] == variable)
                    & (df_config[args.iterable] == iterable)
                ]
            else:
                df_iterable = df_config.copy()

            subset_by_variable.setdefault(idx, df_iterable)

            comparable_mode = comparable_col is not None and global_comparable_values.size > 0
            if comparable_col is not None and comparable_col not in df_iterable.columns and args.debug:
                rprint(
                    f"[yellow]Warning:[/yellow] Comparable column '{comparable_col}' not found. Falling back to a single line."
                )

            if comparable_mode:
                for sdx, comparable_value in enumerate(global_comparable_values):
                    df_iterable_comparable = df_iterable[
                        df_iterable[comparable_col] == comparable_value
                    ]

                    if args.debug:
                        rprint(
                            f"[blue]Info:[/blue] Filtering for comparable: {comparable_col}={comparable_value}"
                        )

                    subset = filter_dataframe(df_iterable_comparable, args)

                    subset = subset.explode(
                        column=(
                            [args.x, args.y, "Error"]
                            if "Error" in subset.columns
                            else [args.x, args.y]
                        )
                    )
                    if subset.empty:
                        rprint(
                            f"[yellow]Warning:[/yellow] No data for iterable {args.iterable}={iterable}, {comparable_col}={comparable_value}, Variable={variable}. Skipping."
                        )
                        continue

                    extrap_col_name = f"{args.y}Extrapolated"
                    extrap_raw_c = subset[extrap_col_name].to_numpy() if extrap_col_name in subset.columns else None
                    y = subset[args.y].astype(float).to_numpy()
                    x_edges = None
                    x = np.array([])
                    extrapolated_mask = np.zeros(0, dtype=bool)
                    try:
                        x = subset[args.x].astype(float).to_numpy()
                        x_bin = x[1] - x[0] if len(x) > 1 else 1
                        x_edges = np.linspace(x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1)
                        x_error = (
                            subset[f"Error"].astype(float).to_numpy()
                            if f"Error" in subset.columns
                            else None
                        )
                        mask = ~np.isnan(x) & ~np.isnan(y)
                        x = x[mask]
                        y = y[mask]
                        x_edges = x_edges[np.append(mask, True) | np.append(True, mask)]
                        if x_error is not None:
                            x_error = x_error[mask]
                        extrapolated_mask = pd.array(extrap_raw_c[mask], dtype="boolean").fillna(False).astype(bool).__array__() if extrap_raw_c is not None else np.zeros(len(x), dtype=bool)

                    except ValueError:
                        x = subset[args.x].astype(str)
                        x_error = None
                        extrapolated_mask = np.zeros(len(x), dtype=bool)

                    if extrapolated_mask.any() and not args.extrapolate:
                        keep = ~extrapolated_mask
                        x = x[keep]
                        y = y[keep]
                        if isinstance(x_error, np.ndarray):
                            x_error = x_error[keep]
                        extrapolated_mask = np.zeros(len(x), dtype=bool)

                    last_x = x

                    if bottom is None:
                        bottom = np.zeros(len(x)) if args.stacked else None

                    iterable_label = map_iterable_label(
                        iterable,
                        args.iterable,
                        getattr(args, "iterable_mapping", None),
                        len(iterable_values),
                    )
                    comparable_label = map_iterable_label(comparable_value, comparable_col, getattr(args, "comparable_mapping", None))

                    if invert_style:
                        line_color = (
                            map_iterable_color(comparable_value, getattr(args, "iterable_color_mapping", None))
                            or _resolve_comparable_color(
                                sdx, args, n_total=len(global_comparable_values),
                                reverse=getattr(args, "comparable_reverse", False),
                            )
                        )
                        line_linestyle = _resolve_comparable_linestyle(
                            linestyle_idx_by_iterable[iterable], args, n_total=iterable_style_n_total,
                            reverse=getattr(args, "iterable_reverse", False),
                        )
                        primary_value_label = comparable_label
                        plot_label = (
                            comparable_label
                            if (idx == n_vars - 1 and linestyle_idx_by_iterable[iterable] == 0)
                            else None
                        )
                    else:
                        line_color = (
                            map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
                            or _resolve_comparable_color(
                                color_idx_by_iterable[iterable], args, n_total=len(color_idx_by_iterable),
                                reverse=getattr(args, "iterable_reverse", False),
                            )
                        )
                        line_linestyle = _resolve_comparable_linestyle(sdx, args, n_total=len(global_comparable_values))
                        primary_value_label = iterable_label
                        plot_label = iterable_label if (idx == n_vars - 1 and sdx == 0) else None

                    _cfs_active = getattr(args, "comparable_fill_strength", False)
                    _fill_active = getattr(args, "fill", False) or _cfs_active
                    if _cfs_active:
                        _fill_alpha = _resolve_comparable_fill_alpha(sdx, args, n_total=len(global_comparable_values))
                    elif _fill_active:
                        _fill_alpha = (getattr(args, "fill_alpha", None) or [0.15])[0]
                    else:
                        _fill_alpha = None
                    _fill_hatch = _resolve_comparable_hatch(sdx, args, n_total=len(global_comparable_values)) if _fill_active and not _cfs_active else None
                    _fill_hatch_color = getattr(args, "fill_hatch_color", False)
                    line_linewidth = _resolve_comparable_linewidth(sdx, args, n_total=len(global_comparable_values))

                    if args.plot_type is not None:
                        rprint(
                            f"\tPlotting {len(x)} points with explicit plot_type={args.plot_type} for {args.iterable}={iterable} ({comparable_col}={comparable_label}), Variable={variable} | color={line_color}, linestyle={line_linestyle}, fill_alpha={_fill_alpha}, linewidth={line_linewidth}"
                        )

                        if args.plot_type == "line":
                            _lw = {} if line_linewidth is None else {"linewidth": line_linewidth}
                            if extrapolated_mask.any():
                                x_norm, y_norm, x_ext, y_ext = _build_extrapolated_segments(x, y, extrapolated_mask)
                                plot_data(args, ax_current, x_norm, y=y_norm, label=plot_label, color=line_color, plot_type="line", linestyle=line_linestyle, **_lw)
                                plot_data(args, ax_current, x_ext, y=y_ext, label=None, color=line_color, plot_type="line", linestyle=_EXTRAPOLATED_LINESTYLE, **_lw)
                                axes_with_extrapolated.setdefault(ax_current, []).append((primary_value_label, line_color))
                            else:
                                plot_data(
                                    args,
                                    ax_current,
                                    x,
                                    y=y,
                                    errory=x_error,
                                    label=plot_label,
                                    color=line_color,
                                    plot_type="line",
                                    linestyle=line_linestyle,
                                    **_lw,
                                )
                        else:
                            _lw = {} if line_linewidth is None else {"linewidth": line_linewidth}
                            plot_data(
                                args,
                                ax_current,
                                x,
                                x_edges=x_edges,
                                y=y,
                                label=plot_label,
                                color=line_color,
                                plot_type=args.plot_type,
                                linestyle=line_linestyle,
                                fill_alpha=_fill_alpha,
                                fill_hatch=_fill_hatch,
                                fill_hatch_color=_fill_hatch_color,
                                **_lw,
                            )

                        continue

                    if x_error is not None and args.errorx:
                        rprint(
                            f"\tPlotting {len(x)} points with error bars for {args.iterable}={iterable_label}, Variable={variable}"
                        )
                        if args.stacked:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                errory=x_error,
                                label=plot_label,
                                color=line_color,
                                plot_type="bar",
                                bottom=bottom,
                            )
                            bottom += y
                        else:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                errory=x_error,
                                label=plot_label,
                                color=line_color,
                                plot_type="errorbar",
                                fmt="o",
                            )

                    else:
                        rprint(
                            f"\tPlotting {len(x)} points for {args.iterable}={iterable_label}, Variable={variable}"
                        )
                        if args.stacked:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                label=plot_label,
                                color=line_color,
                                plot_type="bar",
                                bottom=bottom,
                            )
                            bottom += y
                        else:
                            plot_data(
                                args,
                                ax_current,
                                x,
                                y=y,
                                label=plot_label,
                                color=line_color,
                                plot_type="line",
                                linestyle=line_linestyle,
                            )

                continue

            subset = filter_dataframe(df_iterable, args)

            subset = subset.explode(
                column=(
                    [args.x, args.y, "Error"]
                    if "Error" in subset.columns
                    else [args.x, args.y]
                )
            )
            if subset.empty:
                rprint(
                    f"[yellow]Warning:[/yellow] No data for iterable {args.iterable}={iterable}, Variable={variable}. Skipping."
                )
                continue

            extrap_col_name = f"{args.y}Extrapolated"
            extrap_raw = subset[extrap_col_name].to_numpy() if extrap_col_name in subset.columns else None
            y = subset[args.y].astype(float).to_numpy()
            x_edges = None
            x = np.array([])
            extrapolated_mask = np.zeros(0, dtype=bool)
            try:
                x = subset[args.x].astype(float).to_numpy()
                x_bin = x[1] - x[0] if len(x) > 1 else 1
                x_edges = np.linspace(x[0] - x_bin / 2, x[-1] + x_bin / 2, len(x) + 1)
                x_error = (
                    subset[f"Error"].astype(float).to_numpy()
                    if f"Error" in subset.columns
                    else None
                )
                mask = ~np.isnan(x) & ~np.isnan(y)
                # Remove indices in x, x_error and y where any of them is NaN
                x = x[mask]
                y = y[mask]
                x_edges = x_edges[
                    np.append(mask, True) | np.append(True, mask)
                ]  # Keep edges corresponding to valid x values
                if x_error is not None:
                    x_error = x_error[mask]
                extrapolated_mask = pd.array(extrap_raw[mask], dtype="boolean").fillna(False).astype(bool).__array__() if extrap_raw is not None else np.zeros(len(x), dtype=bool)

            except ValueError:
                x = subset[args.x].astype(str)
                x_error = None
                extrapolated_mask = np.zeros(len(x), dtype=bool)

            if extrapolated_mask.any() and not args.extrapolate:
                keep = ~extrapolated_mask
                x = x[keep]
                y = y[keep]
                if isinstance(x_error, np.ndarray):
                    x_error = x_error[keep]
                extrapolated_mask = np.zeros(len(x), dtype=bool)

            last_x = x

            if bottom is None:
                bottom = np.zeros(len(x)) if args.stacked else None

            iterable_label = map_iterable_label(
                iterable,
                args.iterable,
                getattr(args, "iterable_mapping", None),
                len(iterable_values),
            )
            iterable_color = (
                map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
                or _resolve_comparable_color(
                    color_idx_by_iterable[iterable], args, n_total=len(color_idx_by_iterable),
                    reverse=getattr(args, "iterable_reverse", False),
                )
            )

            if args.plot_type is not None:
                rprint(
                    f"\tPlotting {len(x)} points with explicit plot_type={args.plot_type} for {args.iterable}={iterable} (legend={iterable_label}), Variable={variable}"
                )

                plot_label = iterable_label if idx == n_vars - 1 else None

                if args.plot_type == "bar":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="bar",
                        bottom=bottom if args.stacked else None,
                    )

                elif args.plot_type == "barh":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="barh",
                    )
                    if args.stacked:
                        bottom += y

                elif args.plot_type == "step":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        x_edges=x_edges,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="step",
                        linestyle=args.plot_style,
                    )

                elif args.plot_type == "errorbar":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        errory=x_error,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="errorbar",
                        fmt="o",
                        linestyle=args.plot_style,
                    )

                elif args.plot_type == "line":
                    if extrapolated_mask.any():
                        x_norm, y_norm, x_ext, y_ext = _build_extrapolated_segments(x, y, extrapolated_mask)
                        plot_data(args, ax_current, x_norm, y=y_norm, label=plot_label, color=iterable_color, plot_type="line", linestyle=args.plot_style)
                        plot_data(args, ax_current, x_ext, y=y_ext, label=None, color=iterable_color, plot_type="line", linestyle=_EXTRAPOLATED_LINESTYLE)
                        axes_with_extrapolated.setdefault(ax_current, []).append((iterable_label, iterable_color))
                    else:
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            label=plot_label,
                            color=iterable_color,
                            plot_type="line",
                            linestyle=args.plot_style,
                        )

                elif args.plot_type == "scatter":
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="scatter",
                        fmt="o",
                    )

                else:
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=plot_label,
                        color=iterable_color,
                        plot_type="plot",
                        marker="o",
                        linestyle=args.plot_style,
                    )

                continue

            if x_error is not None and args.errorx:
                rprint(
                    f"\tPlotting {len(x)} points with error bars for {args.iterable}={iterable_label}, Variable={variable}"
                )
                if args.stacked:
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        errory=x_error,
                        label=iterable_label if idx == n_vars - 1 else None,
                        color=iterable_color,
                        plot_type="bar",
                        bottom=bottom,
                    )
                    bottom += y

                else:
                    if args.connect or getattr(args, 'plot_type', None) == 'line':
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            linestyle=args.plot_style,
                            color=iterable_color,
                            label=None,
                            plot_type="plot",
                        )
                    else:
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            errory=x_error,
                            label=iterable_label if idx == n_vars - 1 else None,
                            color=iterable_color,
                            plot_type="errorbar",
                            fmt="o",
                        )

            else:
                rprint(
                    f"\tPlotting {len(x)} points for {args.iterable}={iterable_label}, Variable={variable}"
                )
                if args.stacked:
                    plot_data(
                        args,
                        ax_current,
                        x,
                        y=y,
                        label=iterable_label if idx == n_vars - 1 else None,
                        color=iterable_color,
                        plot_type="bar",
                        bottom=bottom,
                    )
                    bottom += y
                else:
                    if args.connect or getattr(args, 'plot_type', None) == 'line':
                        plot_data(
                            args,
                            ax_current,
                            x,
                            x_edges=x_edges,
                            y=y,
                            label=iterable_label if idx == n_vars - 1 else None,
                            color=iterable_color,
                            plot_type="step",
                            linestyle=args.plot_style,
                        )
                    else:
                        plot_data(
                            args,
                            ax_current,
                            x,
                            y=y,
                            label=iterable_label if idx == n_vars - 1 else None,
                            color=iterable_color,
                            plot_type="plot",
                            marker="o",
                            linestyle="None",
                        )

        # --- sum_iterables: one combined line per (variable, comparable) ---
        # Skipped when the sum was already drawn inline at its mapping position.
        _sum_vals = getattr(args, "sum_iterables", None)
        if _sum_vals and not _sum_inline_drawn:
            _n_non_summed = sum(1 for v in iterable_values if str(v) not in sum_set)
            _sum_color = (
                getattr(args, "sum_color", None)
                or map_iterable_color(sum_label_base, getattr(args, "iterable_color_mapping", None))
                or f"C{_n_non_summed}"
            )
            _comparable_active = comparable_col is not None and global_comparable_values.size > 0
            _comparable_iter = list(enumerate(global_comparable_values)) if _comparable_active else [(0, None)]

            for idx, variable in enumerate(variables):
                ax_current = ax_flat[idx]
                for sdx, comparable_value in _comparable_iter:
                    sum_x, sum_y = None, None
                    for sum_val in _sum_vals:
                        df_sv = df_config[df_config[args.iterable] == sum_val]
                        if variable is not None and "Variable" in df_sv.columns:
                            df_sv = df_sv[df_sv["Variable"] == variable]
                        if _comparable_active and comparable_value is not None:
                            df_sv = df_sv[df_sv[comparable_col] == comparable_value]
                        subset_sv = filter_dataframe(df_sv, args)
                        explode_cols = (
                            [args.x, args.y, "Error"] if "Error" in subset_sv.columns else [args.x, args.y]
                        )
                        subset_sv = subset_sv.explode(column=explode_cols)
                        if subset_sv.empty:
                            continue
                        try:
                            xv = subset_sv[args.x].astype(float).to_numpy()
                            yv = subset_sv[args.y].astype(float).to_numpy()
                        except ValueError:
                            continue
                        mask_sv = ~np.isnan(xv) & ~np.isnan(yv)
                        xv, yv = xv[mask_sv], yv[mask_sv]
                        if xv.size == 0:
                            continue
                        if sum_y is None:
                            sum_x, sum_y = xv, np.zeros_like(yv)
                        if yv.size == sum_y.size:
                            sum_y = sum_y + yv

                    if sum_x is None or sum_y is None:
                        continue

                    _x_bin = sum_x[1] - sum_x[0] if len(sum_x) > 1 else 1
                    _sum_x_edges = np.linspace(sum_x[0] - _x_bin / 2, sum_x[-1] + _x_bin / 2, len(sum_x) + 1)
                    if invert_style and _comparable_active:
                        # Ext. Background is one more --iterable-family entry
                        # (a stand-in for the summed values), so it takes the
                        # slot already reserved for it in the same linestyle
                        # cycle -- see sum_linestyle_idx/iterable_style_map
                        # above -- rather than a fixed style; color still
                        # tracks the comparable value, matching the per-line
                        # inversion above.
                        _cmp_color = (
                            getattr(args, "sum_color", None)
                            or map_iterable_color(comparable_value, getattr(args, "iterable_color_mapping", None))
                            or _resolve_comparable_color(
                                sdx, args, n_total=len(global_comparable_values),
                                reverse=getattr(args, "comparable_reverse", False),
                            )
                        )
                        _cmp_ls = _resolve_comparable_linestyle(
                            sum_linestyle_idx, args, n_total=iterable_style_n_total,
                            reverse=getattr(args, "iterable_reverse", False),
                        )
                    else:
                        _cmp_color = _sum_color
                        _cmp_ls = (
                            _resolve_comparable_linestyle(sdx, args, n_total=len(global_comparable_values))
                            if _comparable_active else getattr(args, "plot_style", None)
                        )

                    if invert_style and _comparable_active:
                        # Ext. Background represents summed --iterable values,
                        # not a --comparable value -- so it belongs in
                        # whichever legend section represents --iterable, not
                        # in main_handles/main_labels (which now feed the
                        # --comparable-driven primary/color section under
                        # inversion). Its entry is already registered in
                        # iterable_style_map above; just don't also label the
                        # plotted line itself.
                        _plot_label = None
                    else:
                        _plot_label = sum_label_base if sdx == 0 else None
                    _sum_cfs_active = getattr(args, "comparable_fill_strength", False)
                    _sum_fill_active = getattr(args, "fill", False) or _sum_cfs_active
                    if _sum_cfs_active:
                        _sum_fill_alpha = _resolve_comparable_fill_alpha(sdx, args, n_total=len(global_comparable_values))
                    elif _sum_fill_active:
                        _sum_fill_alpha = (getattr(args, "fill_alpha", None) or [0.15])[0]
                    else:
                        _sum_fill_alpha = None
                    _sum_fill_hatch = _resolve_comparable_hatch(sdx, args, n_total=len(global_comparable_values)) if _sum_fill_active and not _sum_cfs_active else None
                    _sum_fill_hatch_color = getattr(args, "fill_hatch_color", False)
                    _sum_linewidth = _resolve_comparable_linewidth(sdx, args, n_total=len(global_comparable_values))
                    rprint(
                        f"\tPlotting sum of {list(sum_set)} ({comparable_col}={comparable_value}), Variable={variable} | color={_cmp_color}, linestyle={_cmp_ls}, fill_alpha={_sum_fill_alpha}, linewidth={_sum_linewidth}"
                    )
                    _lw_kw = {} if _sum_linewidth is None else {"linewidth": _sum_linewidth}
                    plot_data(
                        args, ax_current, sum_x,
                        x_edges=_sum_x_edges,
                        y=sum_y,
                        label=_plot_label,
                        color=_cmp_color,
                        plot_type=args.plot_type or "line",
                        linestyle=_cmp_ls,
                        fill_alpha=_sum_fill_alpha,
                        fill_hatch=_sum_fill_hatch,
                        fill_hatch_color=_sum_fill_hatch_color,
                        **_lw_kw,
                    )

        _has_rotated_xlabels = False
        _has_categorical_ylabels = False
        for idx, variable in enumerate(variables):
            ax_current = ax_flat[idx]
            label_subset = subset_by_variable.get(idx, df)

            if n_vars > 1:
                ax_current.set_title(
                    variable if variable is not None else "",
                    fontsize=subtitlefontsize,
                )

            # -x's values are the string/categorical ones, but which axis they're
            # actually drawn on depends on plot orientation: barh puts them on y
            # (category per horizontal bar), everything else puts them on x.
            _categorical_axis = "y" if args.plot_type == "barh" else "x"
            if args.plot_type == "barh":
                ax_current.set_xlabel(resolve_axis_label(args.labely, args.y, label_subset))
            else:
                ax_current.set_xlabel(resolve_axis_label(args.labelx, args.x, label_subset))
            _x_is_categorical = (
                (isinstance(last_x, np.ndarray) and last_x.dtype.kind in ('U', 'S', 'O'))
                or (isinstance(last_x, pd.Series) and not pd.api.types.is_numeric_dtype(last_x))
            )
            if _x_is_categorical:
                if _categorical_axis == "x":
                    ax_current.tick_params(axis='x', labelrotation=45)
                    _has_rotated_xlabels = True
                else:
                    # barh labels are already horizontal and don't need rotation,
                    # but long feature names still need extra left margin below.
                    _has_categorical_ylabels = True

            (
                ax_current.set_ylabel(
                    resolve_axis_label(args.labelx, args.x, label_subset)
                    if args.plot_type == "barh"
                    else resolve_axis_label(args.labely, args.y, label_subset)
                )
                if idx % ncols == 0
                else None
            )

            if args.y == "Efficiency" or args.labely == "Efficiency (%)":
                ax_current.set_ylim(0, 105)
                ax_current.axhline(100, color="gray", linestyle="--", linewidth=1)

            if args.rangex is not None:
                ax_current.set_xlim(args.rangex[0], args.rangex[1])
            if args.rangey is not None:
                ax_current.set_ylim(args.rangey[0], args.rangey[1])

            if args.logy:
                ax_current.semilogy()

            if args.logx:
                ax_current.semilogx()

            if iterable_values.size > 1:
                if args.stacked:
                    if idx == n_vars - 1:
                        main_handles, main_labels = ax_current.get_legend_handles_labels()
                        _apply_iterable_legend(
                            ax_current,
                            primary_legend_title,
                            main_handles,
                            main_labels,
                            secondary_legend_title,
                            secondary_style_map,
                            getattr(args, "capitalize_legend", False),
                            comparable_alpha_map=secondary_alpha_map,
                            loc="upper left",
                            bbox_to_anchor=(0, 1),
                        )
                else:
                    if idx == n_vars - 1:
                        main_handles, main_labels = ax_current.get_legend_handles_labels()
                        if ax_current in axes_with_extrapolated:
                            for lbl, color in axes_with_extrapolated[ax_current]:
                                proxy = mlines.Line2D([], [], color=color, linestyle=_EXTRAPOLATED_LINESTYLE, linewidth=1)
                                main_handles.append(proxy)
                                main_labels.append(f"{lbl} Extrapolated")
                        _apply_iterable_legend(
                            ax_current,
                            primary_legend_title,
                            main_handles,
                            main_labels,
                            secondary_legend_title,
                            secondary_style_map,
                            getattr(args, "capitalize_legend", False),
                            comparable_alpha_map=secondary_alpha_map,
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

        # Hide any unused panels in a grid that isn't fully filled.
        for _i in range(n_vars, nrows * ncols):
            ax_flat[_i].set_visible(False)

        # Materialise tick-label Text objects so ha can be set before layout.
        if _has_rotated_xlabels:
            fig.canvas.draw()
            for _ax in fig.get_axes():
                plt.setp(_ax.get_xticklabels(), ha='right')

        plot_title = make_title_from_args(args)

        if nrows > 1:
            # For multi-row grids let tight_layout compute hspace (inter-row
            # spacing) and the top margin so that panel titles, x-axis labels
            # and the suptitle never overlap. When a suptitle is present reserve
            # 5 % of figure height for it; otherwise use the full height.
            _tl_rect = [0, 0, 1, 0.95] if plot_title else [0, 0, 1, 1.0]
            try:
                fig.tight_layout(rect=_tl_rect)
            except Exception:
                pass
        elif _has_rotated_xlabels or _has_categorical_ylabels:
            # For single-row plots with rotated x labels or long barh category
            # labels, grow the figure downward/leftward to accommodate them
            # without compressing the axes area.
            _sp = fig.subplotpars
            _left, _right, _bottom, _top = _sp.left, _sp.right, _sp.bottom, _sp.top
            old_h = fig.get_figheight()
            old_w = fig.get_figwidth()
            tl_bottom, tl_left = _bottom, _left
            try:
                fig.tight_layout()
                tl_bottom = fig.subplotpars.bottom
                tl_left = fig.subplotpars.left
            except Exception:
                pass
            fig.subplots_adjust(left=_left, right=_right, bottom=_bottom, top=_top)

            if _has_rotated_xlabels:
                extra_in = max(0.0, (tl_bottom - _bottom) * old_h) + 0.1
                if extra_in > 0.1:
                    new_h = old_h + extra_in
                    fig.set_figheight(new_h)
                    top_margin_in = (1.0 - _top) * old_h
                    axes_h_in    = (_top - _bottom) * old_h
                    new_top = 1.0 - top_margin_in / new_h
                    fig.subplots_adjust(bottom=new_top - axes_h_in / new_h, top=new_top)

            if _has_categorical_ylabels:
                extra_in_w = max(0.0, (tl_left - _left) * old_w) + 0.1
                if extra_in_w > 0.1:
                    new_w = old_w + extra_in_w
                    fig.set_figwidth(new_w)
                    right_margin_in = (1.0 - _right) * old_w
                    axes_w_in       = (_right - _left) * old_w
                    new_right = 1.0 - right_margin_in / new_w
                    fig.subplots_adjust(left=new_right - axes_w_in / new_w, right=new_right)

        if plot_title:
            add_centered_suptitle(fig, plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="scan.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)

if __name__ == "__main__":
    main()
