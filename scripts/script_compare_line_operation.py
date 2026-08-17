#!/usr/bin/env python3

"""
Script: Iterable line comparison with operation subplot
Combines iterable line scanning with a lower panel that shows operations
between lines (e.g. relative difference in percent).
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_config_label_from_args, make_config_color_and_style_from_args
from lib.imports import import_data, prepare_import
from lib.plot import apply_legend_style, plot_data, create_common_subplots, create_common_two_panel_figure, apply_note_to_figure, add_centered_suptitle, draw_vertical_lines, draw_horizontal_lines, place_point_label
from common_args import add_common_args, load_computation_settings, map_iterable_label, map_iterable_color, resolve_plot_kwargs, resolve_axis_label

import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from scipy.special import erf

parser = argparse.ArgumentParser(
    description="Compare iterable lines and plot a lower-panel operation",
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
        "variables": {"help": "Optional list of variable filters"},
        "iterable": {"required": True, "help": "Iterable column to produce lines"},
        "select": {
            "help": "If provided, apply save_values filtering using these keys"
        },
        "save_values": {
            "help": "If select keys are provided, save only these matching values"
        },
        "x": {"required": True},
        "y": {"required": True},
        "labelx": {"default": "True Neutrino Energy (MeV)", "help": "Label for x-axis"},
        "labely": {"help": "Label for top subplot y-axis"},
        "labelz": {"help": "Legend title for iterable labels"},
        "rangey": {"help": "Range for top subplot y-axis (min max)"},
        "plot_style": {"help": "Line style (e.g. -, --, :, -.)"},
        "plot_type": {
            "default": "step",
            "choices": ["step", "plot", "line", "scatter", "errorbar"],
            "help": "Default plot type for top and bottom panels",
        },
    },
)

parser.add_argument(
    "--operation",
    type=str,
    default=None,
    choices=[
        "relative_difference",
        "absolute_relative_difference",
        "asymmetry",
        "excess",
        "excess_probability",
        "subtract",
        "ratio",
        "add",
        "multiply",
        "sum",
        "mean",
        "rms",
    ],
    help="Operation to show in the lower subplot",
)

parser.add_argument(
    "--default_operation",
    type=str,
    default=None,
    help="Default lower-panel behavior when --operation is not specified: operation name or dataframe column (overrides config default)",
)

parser.add_argument(
    "--lower_series_data",
    type=str,
    default=None,
    help=(
        "DataFrame column name to use for the lower-panel series. "
        "When provided, the lower panel will display these values directly."
    ),
)

parser.add_argument(
    "--reference",
    type=int,
    default=0,
    help="Reference line index for pairwise operations",
)

parser.add_argument(
    "--reference_value",
    type=str,
    default=None,
    help="Reference iterable value for pairwise operations (overrides --reference)",
)

parser.add_argument(
    "--reference_sum",
    nargs="+",
    default=None,
    help=(
        "Iterable values to sum into a single combined line before the "
        "pairwise --operation, instead of comparing each one individually "
        "against the reference (e.g. sum background components into one "
        "'excess over backgrounds' line)."
    ),
)

parser.add_argument(
    "--reference_sum_label",
    type=str,
    default=None,
    help="Display name for the --reference_sum combined line (defaults to the summed values joined with ' + ').",
)

parser.add_argument(
    "--reference_sum_color",
    type=str,
    default=None,
    help="Color for the --reference_sum combined line (e.g. C1, red, #RRGGBB). Auto-assigned if omitted.",
)

parser.add_argument(
    "--reference_group",
    nargs="+",
    default=None,
    help=(
        "Iterable values to sum (optionally weighted, see --reference_group_weights) "
        "into the left-hand side of a --operation subtract-with-errors "
        "comparison. Used together with --other_group; overrides "
        "--reference_value/--reference_sum for the bottom panel."
    ),
)

parser.add_argument(
    "--reference_group_weights",
    nargs="+",
    type=float,
    default=None,
    help="Weights matching --reference_group, in order (defaults to 1.0 each).",
)

parser.add_argument(
    "--reference_group_label",
    type=str,
    default=None,
    help="Display name for the --reference_group combined line (defaults to the summed values joined with ' + ').",
)

parser.add_argument(
    "--other_group",
    nargs="+",
    default=None,
    help="Iterable values to sum (optionally weighted, see --other_group_weights) into the right-hand side of the --reference_group comparison.",
)

parser.add_argument(
    "--other_group_weights",
    nargs="+",
    type=float,
    default=None,
    help="Weights matching --other_group, in order (defaults to 1.0 each).",
)

parser.add_argument(
    "--other_group_label",
    type=str,
    default=None,
    help="Display name for the --other_group combined line (defaults to the summed values joined with ' + ').",
)

parser.add_argument(
    "--show_stat_error",
    action="store_true",
    default=False,
    help=(
        "Draw the --reference_group/--other_group difference with propagated "
        "statistical error bars, from each contributing value's own --y "
        "error column (see --group_diff_uncorrelated for how shared values "
        "are combined)."
    ),
)

parser.add_argument(
    "--group_diff_uncorrelated",
    action="store_true",
    default=False,
    help=(
        "For --reference_group/--other_group: combine the two groups' "
        "errors as independent (conservative -- double-counts a value's "
        "uncertainty if it appears in both groups with the same weight) "
        "instead of the default, which cancels a value shared by both "
        "groups at equal weight from both the central value and its error "
        "(correct when it really is the same underlying quantity split "
        "between the groups, e.g. a background assumed evenly divided "
        "rather than independently resampled for each)."
    ),
)

parser.add_argument(
    "--group_diff_relative",
    action="store_true",
    default=False,
    help=(
        "Express the --reference_group/--other_group difference as a "
        "percentage of --other_group's own sum, instead of an absolute "
        "count difference. Both the value and its error shrink relative to "
        "--other_group's scale rather than being swamped by it -- useful "
        "when --other_group is a much larger background."
    ),
)

parser.add_argument(
    "--bottom_comparable_value",
    type=str,
    default=None,
    help=(
        "Restrict the --reference_group/--other_group bottom-panel line to "
        "just this one --comparable value (e.g. Smoothed), instead of "
        "drawing one line per --comparable value like the top panel does. "
        "The top panel is unaffected."
    ),
)

parser.add_argument(
    "--bottom_labely",
    type=str,
    default=None,
    help="Label for lower subplot y-axis",
)

parser.add_argument(
    "--bottom_label_mapping",
    type=str,
    default=None,
    help=(
        "Optional mapping dictionary name from plot_params mappings used to "
        "rename the default lower-panel label (keyed by --operation name, "
        "or by the --lower_series_data column when that's used instead). "
        "Overridden by --bottom_labely when both are given."
    ),
)

parser.add_argument(
    "--bottom_rangey",
    nargs=2,
    type=float,
    default=None,
    help="Range for lower subplot y-axis (min max)",
)

parser.add_argument(
    "--no_lower_plot",
    action="store_true",
    default=False,
    help="Disable rendering of the lower subplot",
)

parser.add_argument(
    "--overlay_names",
    action="store_true",
    default=False,
    help=(
        "Draw all --configs/--names combinations on the same shared figure "
        "instead of one figure per combination, colored/labeled by "
        "configuration and name (same convention as script_compare_configuration.py)."
    ),
)

parser.add_argument(
    "--stacked",
    action="store_true",
    default=False,
    help="Stack compatible top-panel series on top of each other",
)

parser.add_argument(
    "--stack_reverse",
    dest="stack_reverse_requested",
    action="store_true",
    default=None,
    help="Reverse stacked order so the first series is drawn on top",
)

parser.add_argument(
    "--no_stack_reverse",
    dest="stack_reverse_requested",
    action="store_false",
    help="Keep stacked order as plotted",
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
    "--comparable", '-c',
    type=str,
    default=None,
    help=(
        "DataFrame column to overlay as an additional line-shape dimension. "
        "Each unique value in this column gets a distinct linestyle; a separate "
        "black legend maps lineshape to value."
    ),
)

parser.add_argument(
    "--comparable_title",
    type=str,
    default=None,
    help="Legend heading for the comparable legend (defaults to the --comparable column name). Pass 'None' to suppress the heading entirely.",
)

parser.add_argument(
    "--comparable_linestyles",
    nargs="+",
    type=str,
    default=None,
    help=(
        "Linestyle per comparable value in order (e.g. solid dashed dotted). "
        "Accepted values: solid/-, dashed/--, dotted/:, dashdot/-. "
        "Defaults to cycling through [-, --, :, -.]."
    ),
)

parser.add_argument(
    "--comparable_linewidths",
    nargs="+",
    type=float,
    default=None,
    help=(
        "Line width per comparable value in order (e.g. 1.0 3.0). "
        "Defaults to the global line width when omitted."
    ),
)

parser.add_argument(
    "--comparable_reverse",
    action="store_true",
    default=False,
    help="Reverse the order of linestyles assigned to comparable values.",
)

parser.add_argument(
    "--comparable_fill_strength",
    action="store_true",
    default=False,
    help=(
        "Encode comparable values with fill alpha instead of linestyle. "
        "All comparables are drawn with a solid line; fill opacity decreases "
        "from the first to the last comparable value."
    ),
)

parser.add_argument(
    "--fill_alpha",
    nargs="+",
    type=float,
    default=None,
    help=(
        "Opacity of the histogram fill (0–1). "
        "With --comparable_fill_strength (single value): multiplies the default alpha sequence "
        "[0.8, 0.55, 0.35, 0.15]; omitting the flag leaves the sequence unchanged. "
        "With --comparable_fill_strength (N values matching the number of comparables): "
        "each value is used as the direct alpha for the corresponding comparable layer."
    ),
)

args = parser.parse_args()
args.stack_reverse = True if getattr(args, "stack_reverse_requested", None) is None else args.stack_reverse_requested

_COMPARABLE_LINESTYLES = ["-", "--", ":", "-."]
_COMPARABLE_ALPHAS = [0.8, 0.55, 0.35, 0.15]

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

def _extract_line_arrays(subset, x_col, y_col, error_col=None):
    has_error_col = bool(error_col) and error_col in subset.columns
    explode_cols = [x_col, y_col] + ([error_col] if has_error_col else [])
    expanded = subset.explode(column=explode_cols)
    if expanded.empty:
        return None, None, None

    try:
        x = expanded[x_col].astype(float).to_numpy()
        y = expanded[y_col].astype(float).to_numpy()
        y_err = expanded[error_col].astype(float).to_numpy() if has_error_col else None
    except ValueError:
        return None, None, None

    mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[mask]
    y = y[mask]
    if y_err is not None:
        y_err = y_err[mask]

    if x.size == 0 or y.size == 0:
        return None, None, None

    return x, y, y_err

def _extract_bottom_column_arrays(subset, x_col, bottom_col):
    expanded = subset.explode(column=[x_col, bottom_col])
    if expanded.empty:
        return None, None

    try:
        x = expanded[x_col].astype(float).to_numpy()
        y = expanded[bottom_col].astype(float).to_numpy()
    except ValueError:
        return None, None

    mask = ~np.isnan(x) & ~np.isnan(y)
    x = x[mask]
    y = y[mask]

    if x.size == 0 or y.size == 0:
        return None, None

    return x, y

def _resolve_bottom_series_label(subset, bottom_col, fallback_label):
    label_col = f"{bottom_col}Label"

    if label_col not in subset.columns:
        return fallback_label

    label_values = subset[label_col].dropna()
    if label_values.empty:
        return fallback_label

    resolved_label = label_values.iloc[0]
    if resolved_label is None:
        return fallback_label

    return str(resolved_label)

def _stacked_plot_type(selected_plot_type, resolved_plot_kwargs):
    if selected_plot_type == "bar":
        return "bar"
    resolved_type = resolved_plot_kwargs.get("plot_type")
    return resolved_type if resolved_type is not None else selected_plot_type

def _resolve_stacked_bar_width(x_values):
    try:
        x_array = np.asarray(x_values, dtype=float)
    except (TypeError, ValueError):
        return 0.8

    if x_array.size <= 1:
        return 0.8

    sorted_unique = np.unique(np.sort(x_array))
    if sorted_unique.size <= 1:
        return 0.8

    diffs = np.diff(sorted_unique)
    positive_diffs = diffs[diffs > 0]
    if positive_diffs.size == 0:
        return 0.8

    return float(np.min(positive_diffs))

def _resolve_comparable_style(sdx, args, n_total=None):
    user_styles = getattr(args, "comparable_linestyles", None)
    user_widths = getattr(args, "comparable_linewidths", None)
    styles = list(user_styles) if user_styles else list(_COMPARABLE_LINESTYLES)
    effective_sdx = sdx
    if getattr(args, "comparable_reverse", False) and n_total is not None:
        effective_sdx = n_total - 1 - sdx
    ls = "-" if getattr(args, "comparable_fill_strength", False) else styles[effective_sdx % len(styles)]
    if user_widths is not None:
        if n_total is not None and len(user_widths) == n_total:
            lw = user_widths[effective_sdx % len(user_widths)]
        else:
            lw = user_widths[0] if user_widths else None
    else:
        lw = None
    return ls, lw

def _compute_pairwise(reference, other, operation):
    if operation == "subtract":
        return other - reference
    if operation == "add":
        return other + reference
    if operation == "multiply":
        return other * reference
    if operation == "ratio":
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.divide(other, reference)
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "relative_difference":
        with np.errstate(divide="ignore", invalid="ignore"):
            result = 100.0 * np.divide(other - reference, reference)
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "absolute_relative_difference":
        with np.errstate(divide="ignore", invalid="ignore"):
            result = 100.0 * np.abs(np.divide(other - reference, reference))
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "asymmetry":
        with np.errstate(divide="ignore", invalid="ignore"):
            denominator = 0.5 * (reference + other)
            result = np.divide(reference - other, denominator)
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "excess":
        # Floored at 0 whenever reference doesn't exceed other (no excess to
        # report), then grows in units of sqrt(other) once it does -- the
        # standard S/sqrt(B)-style significance convention, so it reads
        # naturally alongside this analysis family's "Discovery"/
        # "Significance" framing instead of asymmetry's signed -2..+2 range.
        with np.errstate(divide="ignore", invalid="ignore"):
            result = np.maximum(0.0, reference - other) / np.sqrt(other)
        result[~np.isfinite(result)] = np.nan
        return result
    if operation == "excess_probability":
        # Same floored S/sqrt(B) significance as "excess", passed through the
        # standard Z-score -> two-sided Gaussian coverage probability
        # relationship (erf(Z/sqrt(2)); the same relationship behind "5-sigma
        # discovery" <-> p=2.87e-7 conventions in particle physics -- see
        # Cowan, Cranmer, Gross & Vitells, "Asymptotic formulae for
        # likelihood-based tests of new physics", EPJC 71 (2011) 1554,
        # arXiv:1007.1727, which underlies the S/sqrt(B)-style asymptotic
        # significance used here). Bounded in [0, 1) and, critically,
        # saturates smoothly instead of diverging when "other" -> 0 in a
        # near-empty low-statistics bin, unlike plain "excess".
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.maximum(0.0, reference - other) / np.sqrt(other)
            result = erf(z / np.sqrt(2.0))
        result[~np.isfinite(result)] = np.nan
        return result

    raise ValueError(f"Unsupported pairwise operation: {operation}")

def compute_bottom_series(
    labels, line_arrays, operation, reference_index=0,
    reference_sum_labels=None, reference_sum_display_label=None,
):
    if len(labels) != len(line_arrays):
        raise ValueError("labels and line_arrays must have the same length")
    if len(line_arrays) == 0:
        return []

    op = operation.lower()

    if op in ["sum", "mean", "rms"]:
        stacked = np.vstack(line_arrays)
        if op == "sum":
            y_out = np.sum(stacked, axis=0)
            return [("sum", y_out)]
        if op == "mean":
            y_out = np.mean(stacked, axis=0)
            return [("mean", y_out)]
        y_out = np.sqrt(np.mean(stacked**2, axis=0))
        return [("rms", y_out)]

    if len(line_arrays) < 2:
        return []

    ref_idx = max(0, min(reference_index, len(line_arrays) - 1))
    ref_label = labels[ref_idx]
    ref_array = line_arrays[ref_idx]

    # Values named in reference_sum_labels are summed into a single combined
    # "other" line (e.g. background components) instead of each producing
    # its own output line against the reference.
    sum_label_set = {str(s) for s in reference_sum_labels} if reference_sum_labels else set()
    summed_array = None
    summed_source_label = reference_sum_display_label or (
        " + ".join(str(s) for s in reference_sum_labels) if reference_sum_labels else None
    )

    output = []
    for idx, (label, y_values) in enumerate(zip(labels, line_arrays)):
        if idx == ref_idx:
            continue
        if str(label) in sum_label_set:
            summed_array = y_values if summed_array is None else summed_array + y_values
            continue
        y_out = _compute_pairwise(ref_array, y_values, op)
        # Labeled by source name (e.g. "Solar Day"), not the full pairwise
        # formula: whenever reference_sum_labels doesn't cover every
        # non-reference value, this loop and the summed block below both
        # produce entries, and the caller labels every one of them (see
        # sdx==0 gating at the plot_data call sites) -- a formula string per
        # entry would be unreadable in a legend.
        output.append((str(label), y_out))

    if summed_array is not None:
        y_out = _compute_pairwise(ref_array, summed_array, op)
        output.append((str(summed_source_label), y_out))

    return output

def _weighted_group_sum(labels, line_arrays, line_errors, group_values, group_weights):
    """Sum group_values (each an entry in labels) from line_arrays, each scaled
    by its matching weight in group_weights (default 1.0), plus the
    propagated statistical error of that weighted sum (quadrature sum of
    each contributing value's own error times its weight -- i.e. treating
    the contributing values as independent/uncorrelated, which is exact when
    they really are independent measurements and conservative (an
    over-estimate) when two such sums share the same underlying value split
    by a fixed weight, e.g. a background assumed evenly split between two
    groups rather than independently resampled for each).
    """
    label_to_idx = {str(l): i for i, l in enumerate(labels)}
    weights = list(group_weights) if group_weights is not None else [1.0] * len(group_values)
    if len(weights) != len(group_values):
        raise ValueError(
            f"Got {len(group_values)} group values but {len(weights)} weights; they must match 1:1."
        )

    total = None
    total_err_sq = None
    for value, weight in zip(group_values, weights):
        idx = label_to_idx.get(str(value))
        if idx is None:
            raise ValueError(
                f"Value '{value}' not found among plotted labels: {list(label_to_idx)}"
            )
        scaled = line_arrays[idx] * weight
        total = scaled if total is None else total + scaled

        err = line_errors[idx] if idx < len(line_errors) else None
        err_sq = (err * weight) ** 2 if err is not None else np.zeros_like(scaled)
        total_err_sq = err_sq if total_err_sq is None else total_err_sq + err_sq

    return total, np.sqrt(total_err_sq)

def _group_weights_by_label(group_values, group_weights):
    weights = list(group_weights) if group_weights is not None else [1.0] * len(group_values)
    if len(weights) != len(group_values):
        raise ValueError(
            f"Got {len(group_values)} group values but {len(weights)} weights; they must match 1:1."
        )
    out = {}
    for value, weight in zip(group_values, weights):
        out[str(value)] = out.get(str(value), 0.0) + weight
    return out

def compute_group_difference(
    labels, line_arrays, line_errors,
    reference_group, reference_group_weights, reference_group_label,
    other_group, other_group_weights, other_group_label,
    correlated=True,
    relative=False,
):
    """Compute (weighted sum of reference_group) - (weighted sum of
    other_group), plus the propagated statistical error of that difference.
    Returns a single-entry list of (label, values, errors) to keep the "one
    operation, one bottom-panel line" shape used elsewhere in this script,
    just with an errors slot the plain compute_bottom_series path doesn't
    need.

    correlated=True (default): a value appearing in both groups with the
    same weight is the same underlying quantity counted on both sides (e.g.
    a background assumed evenly split between two groups rather than
    independently resampled for each), so it's cancelled analytically --
    net weight per label = reference_weight - other_weight, and anything
    with net weight 0 contributes to neither the central value nor the
    error. This is the statistically correct treatment when the shared
    value really is shared, and it's identical to the uncorrelated result
    whenever the two groups don't overlap (e.g. HEP's hep vs. backgrounds).

    correlated=False: the two group sums are combined as if independent
    (each value's error counted once per group it appears in) -- the
    conservative choice, but one that double-counts a truly shared value's
    uncertainty instead of letting it cancel.

    relative=True: express the difference as a percentage of other_group's
    own (weighted) sum -- (diff / other_sum) * 100 -- instead of an absolute
    count difference. Useful when other_group dominates the absolute scale
    (e.g. a huge background), since both the value and its propagated error
    shrink relative to that scale instead of being swamped by it: a tiny
    signal against a huge background reads as "~-100%", not "~-1e8 counts".
    Error propagated via standard ratio propagation, treating diff and
    other_sum as independent: sigma_R = sqrt((sigma_diff/other_sum)^2 +
    (diff * sigma_other/other_sum^2)^2).
    """
    ref_label = reference_group_label or " + ".join(str(v) for v in reference_group)
    other_label = other_group_label or " + ".join(str(v) for v in other_group)
    out_label = f"{ref_label} - {other_label}"

    if correlated:
        label_to_idx = {str(l): i for i, l in enumerate(labels)}
        ref_weights = _group_weights_by_label(reference_group, reference_group_weights)
        other_weights = _group_weights_by_label(other_group, other_group_weights)
        net_weights = {
            lbl: ref_weights.get(lbl, 0.0) - other_weights.get(lbl, 0.0)
            for lbl in set(ref_weights) | set(other_weights)
        }

        diff = None
        diff_err_sq = None
        for lbl, net_weight in net_weights.items():
            if net_weight == 0:
                continue
            idx = label_to_idx.get(lbl)
            if idx is None:
                raise ValueError(f"Value '{lbl}' not found among plotted labels: {list(label_to_idx)}")
            contrib = line_arrays[idx] * net_weight
            diff = contrib if diff is None else diff + contrib

            err = line_errors[idx] if idx < len(line_errors) else None
            err_sq = (err * net_weight) ** 2 if err is not None else np.zeros_like(contrib)
            diff_err_sq = err_sq if diff_err_sq is None else diff_err_sq + err_sq

        if diff is None:
            raise ValueError("reference_group and other_group fully cancel -- nothing left to plot.")
        diff_err = np.sqrt(diff_err_sq)
    else:
        ref_sum, ref_err = _weighted_group_sum(
            labels, line_arrays, line_errors, reference_group, reference_group_weights
        )
        other_sum, other_err = _weighted_group_sum(
            labels, line_arrays, line_errors, other_group, other_group_weights
        )
        diff = ref_sum - other_sum
        diff_err = np.sqrt(ref_err**2 + other_err**2)

    if not relative:
        return [(out_label, diff, diff_err)]

    other_sum, other_err = _weighted_group_sum(
        labels, line_arrays, line_errors, other_group, other_group_weights
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = 100.0 * diff / other_sum
        rel_err = 100.0 * np.sqrt(
            (diff_err / other_sum) ** 2 + (diff * other_err / other_sum**2) ** 2
        )
    # A denominator that's merely tiny (not exactly 0) still produces a
    # finite but physically meaningless ratio -- e.g. a near-empty
    # low-statistics tail bin in an unsmoothed spectrum -- which isfinite()
    # alone won't catch. Anything below 1e-6 of the denominator's own peak
    # scale is treated the same as an exact zero: no denominator worth
    # dividing by, so no result rather than a nonsense one.
    tiny_denominator = np.abs(other_sum) < 1e-6 * np.nanmax(np.abs(other_sum))
    rel[tiny_denominator] = np.nan
    rel_err[tiny_denominator] = np.nan
    rel[~np.isfinite(rel)] = np.nan
    rel_err[~np.isfinite(rel_err)] = np.nan

    return [(f"({out_label})/{other_label} [%]", rel, rel_err)]

def _default_bottom_label(operation):
    labels = {
        "subtract": "Difference",
        "add": "Sum",
        "multiply": "Product",
        "sum": "Sum",
        "mean": "Mean",
        "rms": "RMS",
        "ratio": "Ratio",
        "asymmetry": "Asymmetry",
        "excess": "Excess Significance",
        "excess_probability": "Excess Probability",
        "relative_difference": "Relative Difference (%)",
        "absolute_relative_difference": "Absolute Relative Difference (%)",
    }
    return labels.get(operation, operation)

def _resolve_bottom_default_label(key, fallback):
    """Look up *key* (an --operation name, or the --lower_series_data column
    name) in --bottom_label_mapping, falling back to the existing default
    (_default_bottom_label's hardcoded English text, or the raw column name)
    when no mapping is given or it has no entry for this key. This feeds the
    *default* text used for both the bottom axis's ylabel and its legend
    entry -- unlike --bottom_labely, which only overrides the ylabel.
    """
    mapping_name = getattr(args, "bottom_label_mapping", None)
    if mapping_name is not None:
        mapping_dict = get_mapping_dict(mapping_name)
        if mapping_dict and key in mapping_dict:
            return str(mapping_dict[key])
    return fallback

def _make_output_dir(output_arg):
    if output_arg is not None:
        paths = output_arg if isinstance(output_arg, list) else [output_arg]
        for path in paths:
            out_dir = os.path.dirname(path) or "."
            os.makedirs(out_dir, exist_ok=True)
        return os.path.dirname(paths[0]) or "."

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def main():
    allowed_operations = [
        "relative_difference",
        "absolute_relative_difference",
        "asymmetry",
        "excess",
        "excess_probability",
        "subtract",
        "ratio",
        "add",
        "multiply",
        "sum",
        "mean",
        "rms",
    ]

    # Load default operation from computation settings
    computation_settings = load_computation_settings()
    config_default_behavior = computation_settings.get("default_operation")

    operation = None
    bottom_column = None

    # If the user explicitly provided a dataframe column for the lower series,
    # use it and prefer it over any computed operation. Warn if both are set.
    if getattr(args, "lower_series_data", None):
        bottom_column = args.lower_series_data
        if args.operation is not None:
            rprint(
                "[yellow]Warning:[/yellow] Both --lower_series_data and --operation were provided;"
                " displaying --lower_series_data and ignoring --operation."
            )
    else:
        if args.operation is not None:
            operation = args.operation
        else:
            default_behavior = args.default_operation or config_default_behavior
            if default_behavior in allowed_operations:
                operation = default_behavior
            elif default_behavior is not None:
                bottom_column = default_behavior
            else:
                operation = "relative_difference"

    # If the default behavior named a column called 'Significance', allow the
    # user to override which dataframe column should be used by providing
    # --lower_series_data.
    if bottom_column is not None and str(bottom_column).lower() == "significance":
        if getattr(args, "lower_series_data", None):
            bottom_column = args.lower_series_data
    
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    overlay_names = getattr(args, "overlay_names", False)
    shared_fig = shared_ax_top = shared_ax_bottom = None
    if overlay_names:
        if getattr(args, "no_lower_plot", False):
            shared_fig, shared_ax_top = create_common_subplots(nrows=1, ncols=1)
            shared_ax_bottom = None
        else:
            shared_fig, shared_gs = create_common_two_panel_figure(
                ncols=1,
                height_ratios=[3, 1],
            )
            shared_ax_top = shared_fig.add_subplot(shared_gs[0])
            shared_ax_bottom = shared_fig.add_subplot(shared_gs[1], sharex=shared_ax_top)
            shared_ax_top.tick_params(labelbottom=False)
    last_kdx = len(configs) - 1

    for kdx, (config, name) in enumerate(zip(configs, names)):
        if config is not None and name is None:
            df_config = df[(df["Config"] == config)]
        elif config is None and name is not None:
            df_config = df[(df["Name"] == name)]
        elif config is not None and name is not None:
            df_config = df[(df["Config"] == config) & (df["Name"] == name)]
        else:
            df_config = df.copy()

        if args.iterable not in df_config.columns:
            rprint(
                f"[red]Error:[/red] Iterable column '{args.iterable}' not found in dataframe."
            )
            continue

        df_config_all = df_config.copy()
        df_config = df_config[df_config[str(args.iterable)].notna()]
        iterable_values = df_config[args.iterable].unique()

        # When a color mapping is given, order the lines to match the order
        # of its entries instead of dataframe appearance order, so the same
        # mapping controls both color and line order across commands.
        color_mapping_dict = get_mapping_dict(getattr(args, "iterable_color_mapping", None))
        if color_mapping_dict:
            present_values = iterable_values.tolist()
            ordered_values = [v for v in color_mapping_dict if v in present_values]
            ordered_values += [v for v in present_values if v not in color_mapping_dict]
            iterable_values = np.array(ordered_values, dtype=iterable_values.dtype)

        two_line_mode = iterable_values.size == 2

        if iterable_values.size == 0:
            rprint("[yellow]Warning:[/yellow] No iterable entries found after filtering.")
            continue

        render_lower_plot = not getattr(args, "no_lower_plot", False)
        computed_only = not render_lower_plot
        if overlay_names:
            fig, ax_top, ax_bottom = shared_fig, shared_ax_top, shared_ax_bottom
        elif render_lower_plot:
            fig, gs = create_common_two_panel_figure(
                ncols=1,
                height_ratios=[3, 1],
            )
            ax_top = fig.add_subplot(gs[0])
            ax_bottom = fig.add_subplot(gs[1], sharex=ax_top)
            # Hide x-axis tick labels on the upper panel when a lower panel exists
            ax_top.tick_params(labelbottom=False)
        else:
            fig, ax_top = create_common_subplots(nrows=1, ncols=1)
            ax_bottom = None

        overlay_label = overlay_color = overlay_linestyle = None
        if overlay_names:
            overlay_label = make_config_label_from_args(args, config=config, name=name, iterable=None)
            overlay_color, overlay_linestyle = make_config_color_and_style_from_args(args, config=config, name=name)

        selected_plot_type = getattr(args, "plot_type", "step")
        plot_kwargs = resolve_plot_kwargs(selected_plot_type)

        # Comparable mode: overlay a second line-shape dimension from this column
        comparable_col = getattr(args, "comparable", None)
        comparable_values_arr = np.array([])
        if comparable_col is not None:
            if comparable_col not in df_config.columns:
                rprint(
                    f"[red]Error:[/red] Inspect column '{comparable_col}' not found in dataframe."
                )
                comparable_col = None
            else:
                comparable_values_arr = df_config[comparable_col].dropna().unique()

        stacked_requested = getattr(args, "stacked", False)
        stacked_enabled = stacked_requested and comparable_col is None
        if stacked_requested and comparable_col is not None:
            rprint(
                "[yellow]Warning:[/yellow] --stacked is not supported together with "
                f"--comparable={comparable_col}; ignoring --stacked."
            )

        stack_reverse_requested = getattr(args, "stack_reverse_requested", None)
        reverse_stacking = stacked_enabled and (
            stack_reverse_requested is None or stack_reverse_requested
        )
        if stack_reverse_requested is True and not stacked_enabled:
            rprint(
                "[yellow]Warning:[/yellow] --stack_reverse only applies when --stacked is active; ignoring --stack_reverse."
            )

        top_labels = []
        top_arrays = []
        top_errors = []  # parallel to top_arrays; None entries where no error column
        bottom_arrays = []
        top_by_comparable = {}   # comparable_val -> ([labels], [arrays], [colors])
        top_errors_by_comparable = {}  # comparable_val -> [errors], parallel to top_by_comparable's arrays list
        bottom_by_comparable = {}  # comparable_val -> [(label, arr)]
        stacked_bottom = None
        stacked_bottom_by_comparable = {}
        x_reference = None
        stack_mode = "bar" if stacked_enabled else _stacked_plot_type(selected_plot_type, plot_kwargs)
        iterable_index_lookup = {value: idx for idx, value in enumerate(iterable_values.tolist())}
        iterable_order = iterable_values[::-1] if reverse_stacking else iterable_values

        for iterable in iterable_order:
            iterable_index = iterable_index_lookup[iterable]

            if iterable_values.size > 8 and args.reduce and iterable_index % 2 == 1:
                rprint(
                    f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding"
                )
                continue

            df_iterable = df_config[(df_config[args.iterable] == iterable)]
            label = map_iterable_label(iterable, args.iterable, unique_iterables_count=iterable_values.size)
            mapped_color = map_iterable_color(iterable, getattr(args, "iterable_color_mapping", None))
            line_color = (
                f"C{iterable_index}"
                if two_line_mode or (comparable_col is not None and mapped_color is None)
                else mapped_color
            )

            if comparable_col is not None and comparable_values_arr.size > 0:
                for sdx, comparable_val in enumerate(comparable_values_arr):
                    df_comparable_sub = df_iterable[df_iterable[comparable_col] == comparable_val]
                    subset_comparable = filter_dataframe(df_comparable_sub, args)
                    if subset_comparable.empty:
                        continue

                    x_v, y_v, y_v_err = _extract_line_arrays(
                        subset_comparable, args.x, args.y, error_col=f"{args.y}Error"
                    )
                    if x_v is None or y_v is None:
                        if args.debug:
                            rprint(
                                f"[yellow]Warning:[/yellow] Could not extract numeric arrays for iterable={iterable}, {comparable_col}={comparable_val}"
                            )
                        continue

                    if x_reference is None:
                        x_reference = x_v
                    elif x_v.size != x_reference.size or not np.allclose(
                        x_v, x_reference, equal_nan=True
                    ):
                        rprint(
                            f"[yellow]Warning:[/yellow] Skipping iterable={iterable}, {comparable_col}={comparable_val} because x-values are not aligned."
                        )
                        continue

                    comparable_ls, comparable_lw = _resolve_comparable_style(sdx, args, n_total=comparable_values_arr.size)
                    comparable_style_kwargs = {"linewidth": comparable_lw} if comparable_lw is not None else {}
                    _cfs_active = getattr(args, "comparable_fill_strength", False)
                    _fill_alpha = _resolve_comparable_fill_alpha(sdx, args, n_total=comparable_values_arr.size) if _cfs_active else None
                    comparable_fill_kwargs = {"fill_alpha": _fill_alpha} if _fill_alpha is not None else {}
                    plot_bottom = None
                    plot_type_kwargs = dict(plot_kwargs)
                    if stacked_enabled:
                        plot_bottom = stacked_bottom_by_comparable.setdefault(
                            comparable_val,
                            np.zeros_like(y_v, dtype=float),
                        )
                        plot_type_kwargs = {
                            "plot_type": "bar",
                            "width": _resolve_stacked_bar_width(x_v),
                            "edgecolor": "none",
                            "linewidth": 0,
                        }
                    if not computed_only:
                        plot_data(
                            args,
                            ax_top,
                            x_v,
                            y=y_v,
                            label=label if sdx == 0 else None,
                            color=line_color,
                            **({"linestyle": comparable_ls} if not stacked_enabled else {}),
                            **comparable_style_kwargs,
                            **comparable_fill_kwargs,
                            **plot_type_kwargs,
                            **({"bottom": plot_bottom} if plot_bottom is not None else {}),
                        )

                    if plot_bottom is not None:
                        plot_bottom += y_v

                    comparable_entry = top_by_comparable.setdefault(comparable_val, ([], [], []))
                    comparable_entry[0].append(label)
                    comparable_entry[1].append(y_v)
                    comparable_entry[2].append(line_color)
                    top_errors_by_comparable.setdefault(comparable_val, []).append(y_v_err)

                    if bottom_column is not None and bottom_column in subset_comparable.columns:
                        local_sub = subset_comparable[subset_comparable[bottom_column].notna()]
                        if not local_sub.empty:
                            x_b, y_b = _extract_bottom_column_arrays(
                                local_sub, args.x, bottom_column
                            )
                            if x_b is not None and y_b is not None:
                                if x_b.size == x_reference.size and np.allclose(
                                    x_b, x_reference, equal_nan=True
                                ):
                                    b_label = _resolve_bottom_series_label(
                                        local_sub, bottom_column, label
                                    )
                                    bottom_by_comparable.setdefault(comparable_val, []).append(
                                        (b_label, y_b, line_color)
                                    )
            else:
                subset = filter_dataframe(df_iterable, args)
                if subset.empty:
                    continue

                x_values, y_values, y_values_err = _extract_line_arrays(
                    subset, args.x, args.y, error_col=f"{args.y}Error"
                )
                if x_values is None or y_values is None:
                    if args.debug:
                        rprint(
                            f"[yellow]Warning:[/yellow] Could not extract numeric arrays for iterable={iterable}"
                        )
                    continue

                if x_reference is None:
                    x_reference = x_values
                elif x_values.size != x_reference.size or not np.allclose(
                    x_values, x_reference, equal_nan=True
                ):
                    rprint(
                        f"[yellow]Warning:[/yellow] Skipping iterable={iterable} because x-values are not aligned with the first line."
                    )
                    continue

                plot_type_kwargs = dict(plot_kwargs)
                if stacked_enabled:
                    stacked_bottom = (
                        np.zeros_like(y_values, dtype=float)
                        if stacked_bottom is None
                        else stacked_bottom
                    )
                    plot_type_kwargs = {
                        "plot_type": "bar",
                        "width": _resolve_stacked_bar_width(x_values),
                        "edgecolor": "none",
                        "linewidth": 0,
                    }

                if not computed_only:
                    plot_data(
                        args,
                        ax_top,
                        x_values,
                        y=y_values,
                        label=f"{overlay_label} - {label}" if overlay_names else label,
                        color=overlay_color if overlay_names else line_color,
                        linestyle=overlay_linestyle if overlay_names and overlay_linestyle else None,
                        **plot_type_kwargs,
                        **({"bottom": stacked_bottom} if stacked_enabled else {}),
                    )

                if stacked_enabled:
                    stacked_bottom += y_values

                top_labels.append(label)
                top_arrays.append(y_values)
                top_errors.append(y_values_err)

                if bottom_column is not None:
                    if bottom_column not in subset.columns:
                        rprint(
                            f"[yellow]Warning:[/yellow] Bottom column '{bottom_column}' not found for iterable={iterable}."
                        )
                        continue

                    local_bottom_subset = subset[subset[bottom_column].notna()]

                    if local_bottom_subset.empty:
                        if args.debug:
                            rprint(
                                f"[yellow]Warning:[/yellow] No non-null values found for bottom column '{bottom_column}' for iterable={iterable}."
                            )
                        continue

                    x_bottom, y_bottom = _extract_bottom_column_arrays(
                        local_bottom_subset,
                        args.x,
                        bottom_column,
                    )
                    if x_bottom is None or y_bottom is None:
                        if args.debug:
                            rprint(
                                f"[yellow]Warning:[/yellow] Could not extract numeric bottom arrays for iterable={iterable}, column={bottom_column}"
                            )
                        continue

                    if x_bottom.size != x_reference.size or not np.allclose(
                        x_bottom, x_reference, equal_nan=True
                    ):
                        rprint(
                            f"[yellow]Warning:[/yellow] Skipping bottom column for iterable={iterable} because x-values are not aligned with the first line."
                        )
                        continue

                    bottom_label = _resolve_bottom_series_label(
                        local_bottom_subset,
                        bottom_column,
                        label,
                    )

                    bottom_arrays.append((bottom_label, y_bottom))

        has_lines = bool(top_by_comparable) if comparable_col is not None else len(top_arrays) > 0
        if not has_lines:
            rprint("[yellow]Warning:[/yellow] No valid lines available to plot.")
            if overlay_names:
                if kdx != last_kdx:
                    continue
                # Last combination had no data of its own; still finalize the
                # shared figure below using whatever earlier combinations drew.
            else:
                plt.close(fig)
                continue

        bottom_series = []
        bottom_has_content = False
        operation_label = None
        op_ax = ax_bottom if ax_bottom is not None else (ax_top if computed_only else None)

        def _bottom_legend_label(default_text):
            # --bottom_labely renames the bottom axis's y-axis label, not the
            # legend entry for its line(s) -- ax_bottom.set_ylabel below has
            # its own independent bottom_ylabel computation that still
            # applies the override. The exception is --no_lower_plot, where
            # the operation result is the only thing on ax_top and there's
            # no separate legend/ylabel to distinguish.
            if ax_bottom is None and args.bottom_labely is not None:
                return args.bottom_labely
            return default_text

        if op_ax is not None:
            use_group_diff = bool(
                getattr(args, "reference_group", None) and getattr(args, "other_group", None)
            )

            ref_index = args.reference
            if not use_group_diff and args.reference_value is not None:
                ref_labels = (
                    next(iter(top_by_comparable.values()))[0]
                    if comparable_col is not None and top_by_comparable
                    else top_labels
                )
                try:
                    ref_index = ref_labels.index(str(args.reference_value))
                except ValueError:
                    rprint(
                        f"[yellow]Warning:[/yellow] reference_value '{args.reference_value}' not found in plotted labels. Using reference index {args.reference}."
                    )

            if use_group_diff:
                show_stat_error = getattr(args, "show_stat_error", False)
                group_kwargs = dict(
                    reference_group=args.reference_group,
                    reference_group_weights=getattr(args, "reference_group_weights", None),
                    reference_group_label=getattr(args, "reference_group_label", None),
                    other_group=args.other_group,
                    other_group_weights=getattr(args, "other_group_weights", None),
                    other_group_label=getattr(args, "other_group_label", None),
                    correlated=not getattr(args, "group_diff_uncorrelated", False),
                    relative=getattr(args, "group_diff_relative", False),
                )
                operation_label = None

                if comparable_col is not None and top_by_comparable:
                    bottom_comparable_value = getattr(args, "bottom_comparable_value", None)
                    for sdx, comparable_val in enumerate(comparable_values_arr):
                        if comparable_val not in top_by_comparable:
                            continue
                        if bottom_comparable_value is not None and str(comparable_val) != bottom_comparable_value:
                            continue
                        comparable_ls, comparable_lw = _resolve_comparable_style(sdx, args, n_total=comparable_values_arr.size)
                        comparable_style_kwargs = {"linewidth": comparable_lw} if comparable_lw is not None else {}

                        labels_at, arrays_at, colors_at = top_by_comparable[comparable_val]
                        errors_at = top_errors_by_comparable.get(comparable_val, [None] * len(labels_at))
                        group_result = compute_group_difference(labels_at, arrays_at, errors_at, **group_kwargs)

                        for diff_label, values, errors in group_result:
                            if operation_label is None:
                                operation_label = _bottom_legend_label(diff_label)
                            if show_stat_error:
                                plot_data(
                                    args,
                                    op_ax,
                                    x_reference,
                                    y=values,
                                    errory=errors,
                                    label=f"{operation_label} ({comparable_val})",
                                    color=getattr(args, "reference_sum_color", None) or f"C{sdx}",
                                    plot_type="errorbar",
                                    fmt="o",
                                )
                            else:
                                plot_data(
                                    args,
                                    op_ax,
                                    x_reference,
                                    y=values,
                                    label=(operation_label if sdx == 0 else None),
                                    color=getattr(args, "reference_sum_color", None),
                                    linestyle=comparable_ls,
                                    **comparable_style_kwargs,
                                    **plot_kwargs,
                                )
                            bottom_has_content = True
                        bottom_series = group_result
                else:
                    errors_all = top_errors if top_errors else [None] * len(top_labels)
                    group_result = compute_group_difference(top_labels, top_arrays, errors_all, **group_kwargs)

                    for diff_label, values, errors in group_result:
                        operation_label = _bottom_legend_label(diff_label)
                        if show_stat_error:
                            plot_data(
                                args,
                                op_ax,
                                x_reference,
                                y=values,
                                errory=errors,
                                label=overlay_label if overlay_names else operation_label,
                                color=(overlay_color if overlay_names else None) or getattr(args, "reference_sum_color", None),
                                plot_type="errorbar",
                                fmt="o",
                            )
                        else:
                            plot_data(
                                args,
                                op_ax,
                                x_reference,
                                y=values,
                                label=overlay_label if overlay_names else operation_label,
                                color=overlay_color if overlay_names else getattr(args, "reference_sum_color", None),
                                linestyle=(overlay_linestyle if overlay_names and overlay_linestyle else args.plot_style),
                                **plot_kwargs,
                            )
                    bottom_series = group_result
                    bottom_has_content = bool(bottom_series)
            elif comparable_col is not None and top_by_comparable:
                operation_label = _bottom_legend_label(
                    _resolve_bottom_default_label(bottom_column, bottom_column)
                    if bottom_column is not None
                    else _resolve_bottom_default_label(
                        operation or "", _default_bottom_label(operation or "")
                    )
                )
                for sdx, comparable_val in enumerate(comparable_values_arr):
                    if comparable_val not in top_by_comparable:
                        continue
                    comparable_ls, comparable_lw = _resolve_comparable_style(sdx, args, n_total=comparable_values_arr.size)
                    comparable_style_kwargs = {"linewidth": comparable_lw} if comparable_lw is not None else {}

                    if bottom_column is not None:
                        bottom_s_raw = bottom_by_comparable.get(comparable_val, [])
                        bottom_s = [(lbl, vals) for lbl, vals, _c in bottom_s_raw]
                        bottom_colors = [c for _lbl, _vals, c in bottom_s_raw]
                    else:
                        labels_at, arrays_at, colors_at = top_by_comparable[comparable_val]
                        ref_sum_values = getattr(args, "reference_sum", None)
                        ref_sum_display_label = getattr(args, "reference_sum_label", None)
                        bottom_s = compute_bottom_series(
                            labels_at, arrays_at, operation, reference_index=ref_index,
                            reference_sum_labels=ref_sum_values,
                            reference_sum_display_label=ref_sum_display_label,
                        )
                        if operation in {"sum", "mean", "rms"}:
                            bottom_colors = [None] * len(bottom_s)
                        else:
                            # Look up each source line's top-panel color by
                            # its (now plain source-name) output label
                            # instead of position: --reference_sum collapses
                            # several source lines into one output entry, so
                            # positional-index alignment with colors_at no
                            # longer holds once that's active.
                            color_by_output_label = {
                                str(lbl): color for lbl, color in zip(labels_at, colors_at)
                            }
                            if ref_sum_values:
                                ref_sum_display = ref_sum_display_label or " + ".join(
                                    str(s) for s in ref_sum_values
                                )
                                color_by_output_label[str(ref_sum_display)] = (
                                    getattr(args, "reference_sum_color", None)
                                )
                            bottom_colors = [
                                color_by_output_label.get(lbl) for lbl, _vals in bottom_s
                            ]

                    for idx, (_label, values) in enumerate(bottom_s):
                        # Labeled by operation (e.g. "Excess Probability"),
                        # not by source component: every line here is the
                        # same operation applied to a different component/
                        # sum, so one legend entry names *what* is plotted;
                        # color (looked up per-line above) still ties each
                        # line back to its component via the top panel.
                        plot_data(
                            args,
                            op_ax,
                            x_reference,
                            y=values,
                            label=(operation_label if idx == 0 and sdx == 0 else None),
                            color=bottom_colors[idx] if idx < len(bottom_colors) else None,
                            linestyle=comparable_ls,
                            **comparable_style_kwargs,
                            **plot_kwargs,
                        )
                        bottom_has_content = True
                    bottom_series = bottom_s
            else:
                if bottom_column is not None:
                    bottom_series = bottom_arrays
                    operation_label = _bottom_legend_label(
                        _resolve_bottom_default_label(bottom_column, bottom_column)
                    )
                else:
                    bottom_series = compute_bottom_series(
                        top_labels,
                        top_arrays,
                        operation,
                        reference_index=ref_index,
                        reference_sum_labels=getattr(args, "reference_sum", None),
                        reference_sum_display_label=getattr(args, "reference_sum_label", None),
                    )

                    operation_label = _bottom_legend_label(
                        _resolve_bottom_default_label(
                            operation or "", _default_bottom_label(operation)
                        )
                    )

                for idx, (_label, values) in enumerate(bottom_series):
                    # Labeled by operation, not source component -- see the
                    # comparable-branch loop above.
                    plot_data(
                        args,
                        op_ax,
                        x_reference,
                        y=values,
                        label=(
                            (overlay_label if overlay_names else operation_label)
                            if idx == 0
                            else None
                        ),
                        color=overlay_color if overlay_names else None,
                        linestyle=(overlay_linestyle if overlay_names and overlay_linestyle else args.plot_style),
                        **plot_kwargs,
                    )
                bottom_has_content = bool(bottom_series)

            if ax_bottom is not None:
                ax_bottom.axhline(y=0, color="r", zorder=-1)

        if overlay_names and kdx != last_kdx:
            # Defer labels/legend/title/save until every combination has been
            # drawn onto the shared figure.
            continue

        if computed_only:
            ax_top.set_ylabel(
                resolve_axis_label(args.labely, args.y, df_iterable)
                if args.labely is not None
                else str(operation_label) if operation_label is not None
                else resolve_axis_label(args.labely, args.y, df_iterable),
                fontsize=ysublabelfontsize,
            )
        else:
            ax_top.set_ylabel(
                resolve_axis_label(args.labely, args.y, df_iterable),
                fontsize=ysublabelfontsize,
            )
        if ax_bottom is not None:
            bottom_ylabel = (
                args.bottom_labely
                if args.bottom_labely is not None
                else (
                    _resolve_bottom_default_label(bottom_column, bottom_column)
                    if bottom_column is not None
                    else _resolve_bottom_default_label(
                        operation or "", _default_bottom_label(operation or "")
                    )
                )
            )
            ax_bottom.set_ylabel(
                str(bottom_ylabel),
                fontsize=ysublabelfontsize,
            )
            ax_bottom.set_xlabel(
                resolve_axis_label(args.labelx, args.x, df_iterable),
                fontsize=xlabelfontsize,
            )
        else:
            ax_top.set_xlabel(
                resolve_axis_label(args.labelx, args.x, df_iterable),
                fontsize=xlabelfontsize,
            )

        if args.rangex is not None:
            ax_top.set_xlim(args.rangex)
            if ax_bottom is not None:
                ax_bottom.set_xlim(args.rangex)
        if args.rangey is not None:
            ax_top.set_ylim(args.rangey)
        if ax_bottom is not None and args.bottom_rangey is not None:
            ax_bottom.set_ylim(args.bottom_rangey)

        if args.logy:
            ax_top.set_yscale("log")
        if args.logx:
            ax_top.set_xscale("log")
            if ax_bottom is not None:
                ax_bottom.set_xscale("log")

        legend_title = (
            None
            if computed_only
            else (args.labelz if args.labelz is not None else args.iterable)
        )
        leg1 = apply_legend_style(
            ax_top,
            title=legend_title,
            capitalize_labels=getattr(args, "capitalize_legend", False),
        )
        if comparable_col is not None and comparable_values_arr.size > 0 and not computed_only:
            ax_top.add_artist(leg1)
            _cfs_legend = getattr(args, "comparable_fill_strength", False)
            if _cfs_legend:
                comparable_handles = [
                    mpatches.Patch(
                        facecolor="gray",
                        alpha=_resolve_comparable_fill_alpha(sdx, args, n_total=comparable_values_arr.size),
                        edgecolor="black",
                        linewidth=1.0,
                    )
                    for sdx, val in enumerate(comparable_values_arr)
                ]
            else:
                comparable_handles = [
                    mlines.Line2D(
                        [],
                        [],
                        color="black",
                        linestyle=_resolve_comparable_style(sdx, args, n_total=comparable_values_arr.size)[0],
                        linewidth=_resolve_comparable_style(sdx, args, n_total=comparable_values_arr.size)[1] or 1.5,
                        label=str(val),
                    )
                    for sdx, val in enumerate(comparable_values_arr)
                ]
            apply_legend_style(
                ax_top,
                handles=comparable_handles,
                labels=[str(v) for v in comparable_values_arr],
                title=None if getattr(args, "comparable_title", None) == "None" else (getattr(args, "comparable_title", None) or comparable_col),
                capitalize_labels=False,
                loc="lower right",
            )
        if ax_bottom is not None and bottom_has_content:
            apply_legend_style(
                ax_bottom,
                capitalize_labels=getattr(args, "capitalize_legend", False),
            )

        draw_vertical_lines(
            ax_top,
            getattr(args, "vertical", None),
            labels=getattr(args, "vertical_label", None),
            styles=getattr(args, "vertical_style", None),
            colors=getattr(args, "vertical_color", None),
            fontsize=linelabelfontsize,
        )
        if ax_bottom is not None:
            draw_vertical_lines(
                ax_bottom,
                getattr(args, "vertical", None),
                fontsize=linelabelfontsize,
            )
        draw_horizontal_lines(
            ax_top,
            getattr(args, "horizontal", None),
            labels=getattr(args, "horizontal_label", None),
            styles=getattr(args, "horizontal_style", None),
            colors=getattr(args, "horizontal_color", None),
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
                ax_top.scatter(point_x, point_y, color="gray", s=40, zorder=6)
                if point_labels is not None:
                    place_point_label(ax_top, point_x, point_y, point_labels[point_idx], fontsize=linelabelfontsize)

        figure_title = make_title_from_args(args)
        add_centered_suptitle(fig, figure_title, fontsize=titlefontsize)

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_suffix = (
            "stacked_line_operation.png"
            if getattr(args, "stacked", False)
            else "line_operation.png"
        )
        output_file = make_name_from_args(
            args,
            None if overlay_names else kdx,
            prefix=None,
            suffix=output_suffix,
        )
        output_dir = _make_output_dir(args.output)
        default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)

if __name__ == "__main__":
    main()
