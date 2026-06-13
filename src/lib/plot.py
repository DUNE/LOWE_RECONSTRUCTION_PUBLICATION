import numpy as np
import matplotlib.pyplot as plt
from typing import Any

from . import (
    default_linewidth,
    legend_style,
    note_style,
    legendfontsize,
    legendtitlefontsize,
    figure_base_width,
    figure_panel_width,
    figure_height,
    figure_margins_inches,
    figure_two_panel_hspace,
)


PLOT_STYLE_OPTIONS = {
    "-": "-",
    "--": "--",
    ":": ":",
    "-.": "-.",
    "solid": "-",
    "dashed": "--",
    "dotted": ":",
    "dashdot": "-.",
    "none": "None",
    "": "None",
}


def get_common_figsize(ncols=1):
    panel_count = max(1, int(ncols))
    width = figure_base_width + figure_panel_width * (panel_count - 1)
    return (float(width), float(figure_height))


def apply_common_figure_margins(fig, hspace=None):
    """Apply common margins to a figure, converting from absolute inches to normalized coordinates.
    
    Args:
        fig: matplotlib Figure object
        hspace: Optional override for hspace (height space between subplots)
    """
    if not isinstance(figure_margins_inches, dict):
        return
    
    figwidth = fig.get_figwidth()
    figheight = fig.get_figheight()
    
    # Convert absolute-inch margins to normalized coordinates (0-1 scale)
    margins_normalized = {}
    for key, value in figure_margins_inches.items():
        if key == "left":
            margins_normalized[key] = value / figwidth
        elif key == "right":
            # right is measured from right edge, so: 1 - (right_inch / width)
            margins_normalized[key] = 1 - (value / figwidth)
        elif key == "bottom":
            margins_normalized[key] = value / figheight
        elif key == "top":
            # top is measured from top edge, so: 1 - (top_inch / height)
            margins_normalized[key] = 1 - (value / figheight)
        else:
            # wspace, hspace, etc. are already in proper units
            margins_normalized[key] = value
    
    if hspace is not None:
        margins_normalized["hspace"] = hspace
    
    if margins_normalized:
        fig.subplots_adjust(**margins_normalized)


def create_common_subplots(nrows=1, ncols=1, **kwargs) -> tuple[Any, Any]:
    fig, ax = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=get_common_figsize(ncols=ncols),
        constrained_layout=False,
        **kwargs,
    )
    apply_common_figure_margins(fig)
    return fig, ax


def create_common_two_panel_figure(ncols=1, height_ratios=(3, 1), hspace=None) -> tuple[Any, Any]:
    fig = plt.figure(figsize=get_common_figsize(ncols=ncols))
    resolved_hspace = figure_two_panel_hspace if hspace is None else hspace
    grid = fig.add_gridspec(
        nrows=2,
        ncols=ncols,
        height_ratios=height_ratios,
        hspace=resolved_hspace,
    )
    apply_common_figure_margins(fig, hspace=resolved_hspace)
    return fig, grid


def _resolve_plot_style(plot_style):
    if plot_style is None:
        return None

    key = str(plot_style).strip()
    key_normalized = key.lower()

    if key_normalized in PLOT_STYLE_OPTIONS:
        return PLOT_STYLE_OPTIONS[key_normalized]

    if key in PLOT_STYLE_OPTIONS:
        return PLOT_STYLE_OPTIONS[key]

    available = ", ".join(PLOT_STYLE_OPTIONS.keys())
    raise ValueError(
        f"Unknown plot_style '{plot_style}'. Available options: {available}"
    )


def _apply_plot_style(kwargs, plot_style):
    if plot_style is None:
        return
    if "ls" in kwargs or "linestyle" in kwargs:
        return
    kwargs["ls"] = plot_style

from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter


def _make_threshold_formatter(threshold=0.1):
    def _formatter(value, _position):
        if not np.isfinite(value):
            return ""
        if value == 0:
            return "0"
        if abs(value) < threshold:
            scientific = f"{value:.1e}"
            mantissa, exponent = scientific.split("e")
            if mantissa.endswith(".0"):
                mantissa = mantissa[:-2]
            sign = exponent[0]
            digits = exponent[1:].lstrip("0") or "0"
            return f"{mantissa}e{sign}{digits}"
        return f"{value:g}"

    return FuncFormatter(_formatter)


def apply_scientific_threshold_formatter(ax, threshold=0.1, axis="both"):
    formatter = _make_threshold_formatter(threshold=threshold)

    if axis in ("x", "both") and hasattr(ax, "xaxis") and ax.xaxis is not None:
        ax.xaxis.set_major_formatter(formatter)

    if axis in ("y", "both") and hasattr(ax, "yaxis") and ax.yaxis is not None:
        ax.yaxis.set_major_formatter(formatter)


def _capitalize_legend_label(label):
    if not isinstance(label, str):
        return label

    words = label.split(" ")
    formatted_words = []
    for word in words:
        if not word:
            formatted_words.append(word)
            continue

        first_char = word[0]
        if first_char.isalpha():
            formatted_words.append(first_char.upper() + word[1:])
        else:
            formatted_words.append(word)

    return " ".join(formatted_words)


def _normalize_boolean_legend_label(label, title):
    title_text = str(title).strip() if title is not None else ""
    if not title_text:
        return label

    if isinstance(label, bool):
        return title_text if label else f"Not {title_text}"

    if isinstance(label, str):
        label_text = label.strip().lower()
        if label_text == "true":
            return title_text
        if label_text == "false":
            return f"Not {title_text}"

    return label


def _is_boolean_legend_label(label):
    if isinstance(label, bool):
        return True

    if isinstance(label, str):
        return label.strip().lower() in {"true", "false"}

    return False


def apply_legend_style(
    ax,
    title=None,
    handles=None,
    labels=None,
    capitalize_labels=True,
    **overrides,
):
    style = dict(legend_style) if isinstance(legend_style, dict) else {}

    if "fontsize" not in style:
        style["fontsize"] = legendfontsize
    if "title_fontsize" not in style:
        style["title_fontsize"] = legendtitlefontsize

    if title is not None:
        style["title"] = title

    style.update(overrides)

    if handles is None and labels is None:
        handles, labels = ax.get_legend_handles_labels()

    if labels is not None and any(_is_boolean_legend_label(label) for label in labels):
        style.pop("title", None)

    if labels is not None:
        labels = [_normalize_boolean_legend_label(label, title) for label in labels]

    if labels is not None and capitalize_labels:
        labels = [_capitalize_legend_label(label) for label in labels]

    if handles is not None or labels is not None:
        return ax.legend(handles=handles, labels=labels, **style)

    return ax.legend(**style)


def plot_data(
    args,
    ax,
    x,
    x_edges=None,
    y=None,
    errory=None,
    errory_sym=None,
    label=None,
    color=None,
    linestyle=None,
    errorx=None,
    plot_type=None,
    **kwargs,
):
    """Plot data using a shared set of matplotlib-backed plot modes.

    Supported ``plot_style`` options: ``-``, ``--``, ``:``, ``-.``,
    ``solid``, ``dashed``, ``dotted``, ``dashdot``.
    """

    plot_type = plot_type or getattr(args, "plot_type", None)
    if plot_type is None:
        plot_type = "step" if x_edges is not None else "plot"

    explicit_plot_style = kwargs.pop("plot_style", None)
    selected_plot_style = (
        explicit_plot_style
        if explicit_plot_style is not None
        else linestyle if linestyle is not None else getattr(args, "plot_style", None)
    )
    resolved_plot_style = _resolve_plot_style(selected_plot_style)

    if plot_type == "scatter":
        kwargs.setdefault("linewidth", default_linewidth)
        ax.errorbar(
            x,
            y,
            yerr=errory if getattr(args, "errory", False) else None,
            fmt=kwargs.pop("fmt", "o"),
            label=label,
            color=color,
            **kwargs,
        )
        return None

    if plot_type == "line":
        kwargs.setdefault("linewidth", default_linewidth)
        if errory is not None and getattr(args, "errory_type", None) == "bands":
            plot_kwargs = dict(kwargs)
            _apply_plot_style(plot_kwargs, resolved_plot_style)
            ax.plot(x, y, label=label, color=color, **plot_kwargs)
            ax.fill_between(
                x,
                y - errory if errory_sym == "symmetric" else y - errory[0],
                y + errory if errory_sym == "symmetric" else y + errory[1],
                color=color,
                alpha=0.2,
                edgecolor="none",
            )
        elif errory is not None and getattr(args, "errory_type", None) == "bars":
            errorbar_kwargs = dict(kwargs)
            _apply_plot_style(errorbar_kwargs, resolved_plot_style)
            ax.errorbar(
                x,
                y,
                xerr=errorx if getattr(args, "errory_x", False) else None,
                yerr=errory if errory_sym == "symmetric" else errory,
                label=label,
                color=color,
                **errorbar_kwargs,
            )
        else:
            plot_kwargs = dict(kwargs)
            _apply_plot_style(plot_kwargs, resolved_plot_style)
            ax.plot(x, y, label=label, color=color, **plot_kwargs)
        return None

    if plot_type == "step":
        hist_kwargs = dict(kwargs)
        hist_kwargs.setdefault("linewidth", default_linewidth)
        _apply_plot_style(hist_kwargs, resolved_plot_style)
        ax.hist(
            x,
            bins=x_edges,
            weights=y,
            histtype=hist_kwargs.pop("histtype", "step"),
            align=hist_kwargs.pop("align", getattr(args, "align", "mid")),
            label=label,
            color=color,
            **hist_kwargs,
        )
        return None

    if plot_type == "plot":
        plot_kwargs = dict(kwargs)
        plot_kwargs.setdefault("linewidth", default_linewidth)
        _apply_plot_style(plot_kwargs, resolved_plot_style)
        ax.plot(x, y, label=label, color=color, **plot_kwargs)
        return None

    if plot_type == "errorbar":
        errorbar_kwargs = dict(kwargs)
        errorbar_kwargs.setdefault("linewidth", default_linewidth)
        _apply_plot_style(errorbar_kwargs, resolved_plot_style)
        return ax.errorbar(
            x,
            y,
            xerr=errorbar_kwargs.pop("xerr", errorx),
            yerr=errorbar_kwargs.pop("yerr", errory),
            fmt=errorbar_kwargs.pop("fmt", "o"),
            label=label,
            color=color,
            **errorbar_kwargs,
        )

    if plot_type == "scatter_points":
        return ax.scatter(x, y, label=label, color=color, **kwargs)

    if plot_type == "bar":
        kwargs.setdefault("linewidth", default_linewidth)
        return ax.bar(
            x,
            y,
            yerr=kwargs.pop("yerr", errory),
            label=label,
            color=color,
            **kwargs,
        )

    if plot_type == "boxplot":
        boxplot_data = kwargs.pop("boxplot_data", y)
        return ax.boxplot(boxplot_data, label=label, **kwargs)

    if plot_type == "hist2d":
        return ax.hist2d(
            x,
            y,
            bins=kwargs.pop("bins", getattr(args, "bins", None)),
            range=kwargs.pop("range", None),
            norm=LogNorm() if getattr(args, "logz", False) else None,
            density=kwargs.pop("density", getattr(args, "density", False)),
            **kwargs,
        )

    if plot_type == "image":
        z = kwargs.pop("z", None)
        norm = LogNorm() if getattr(args, "logz", False) else None
        return ax.pcolormesh(x, y, z, norm=norm, shading="auto", **kwargs)

    raise ValueError(f"Unknown plot type: {plot_type}")


def add_note_to_axes(ax, note_text, fontsize=None):
    """Add a text annotation to the best position on an axes.
    
    Automatically determines the best position (corner with least content) to place
    the note. Tries positions in order: upper right, upper left, lower left, lower right.
    
    Args:
        ax: matplotlib axes object
        note_text: Text string to display
        fontsize: Font size for the note text (uses note_style default if None)
    
    Returns:
        matplotlib text object
    """
    if note_text is None or not str(note_text).strip():
        return None
    
    text_str = str(note_text).strip()
    
    # Get note style from config
    note_cfg = note_style if isinstance(note_style, dict) else {}
    configured_fontsize = note_cfg.get("fontsize", "large")
    bbox_cfg = note_cfg.get("bbox", {
        "boxstyle": "round,pad=0.5",
        "facecolor": "white",
        "alpha": 0.8,
        "edgecolor": "gray",
        "linewidth": 0.5,
    })
    
    # Use provided fontsize or fall back to config
    if fontsize is None:
        fontsize = configured_fontsize
    
    # Candidate positions: (ha, va, xy) tuples
    # xy coordinates are in axes coordinates (0-1 range)
    positions = [
        (0.98, 0.98, "upper right"),  # Upper right
        (0.02, 0.98, "upper left"),   # Upper left
        (0.02, 0.02, "lower left"),   # Lower left
        (0.98, 0.02, "lower right"),  # Lower right
    ]
    
    # Try to find the best position by checking for legend and other content
    # Default to upper right if all else fails
    best_position = positions[0]
    
    # Check if legend exists and where it is
    legend = ax.get_legend()
    if legend is not None:
        legend_bbox = legend.get_window_extent()
        legend_bbox_axes = legend_bbox.transformed(ax.transAxes.inverted())
        legend_y_center = (legend_bbox_axes.y0 + legend_bbox_axes.y1) / 2
        legend_x_center = (legend_bbox_axes.x0 + legend_bbox_axes.x1) / 2
        
        # Avoid legend position by preferring opposite corners
        if legend_y_center > 0.5:  # Legend in upper half
            best_position = positions[2]  # Use lower left
        elif legend_x_center > 0.5:  # Legend in right half
            best_position = positions[1]  # Use upper left
        else:  # Legend in lower left
            best_position = positions[0]  # Use upper right
    
    x, y = best_position[0], best_position[1]
    ha = "right" if x > 0.5 else "left"
    va = "top" if y > 0.5 else "bottom"
    
    # Add text with a semi-transparent background for readability
    text_obj = ax.text(
        x, y, text_str,
        transform=ax.transAxes,
        fontsize=fontsize,
        ha=ha,
        va=va,
        bbox=dict(bbox_cfg),
        zorder=100,  # High z-order to ensure it appears on top
    )
    
    return text_obj


def apply_note_to_figure(fig, note_text, fontsize=None):
    """Apply a text annotation to the best position on a figure's main axes.
    
    Automatically finds the first non-colorbar axes and places the note there.
    Uses note_style configuration for fontsize and styling if not explicitly provided.
    
    Args:
        fig: matplotlib figure object
        note_text: Text string to display
        fontsize: Font size for the note text (uses note_style default if None)
    
    Returns:
        matplotlib text object, or None if no valid axes found
    """
    if note_text is None or not str(note_text).strip():
        return None
    
    # Get all axes from the figure, excluding colorbars
    axes = fig.get_axes()
    
    if not axes:
        return None
    
    # Filter out colorbar axes and get the first regular axis
    main_ax = None
    for ax in axes:
        # Skip colorbar axes (they have specific names)
        if hasattr(ax, 'cbar') or 'colorbar' in str(type(ax).__name__).lower():
            continue
        # Skip small axes that might be colorbars (width < 0.1 or height < 0.1)
        bbox = ax.get_position()
        if bbox.width < 0.05 or bbox.height < 0.05:
            continue
        main_ax = ax
        break
    
    if main_ax is None and axes:
        # Fallback: use the first axis if all filtering fails
        main_ax = axes[0]
    
    if main_ax is None:
        return None
    
    return add_note_to_axes(main_ax, note_text, fontsize=fontsize)


def _format_ref_value(v):
    """Format a float reference-line value as a compact string label."""
    if v == int(v):
        return str(int(v))
    return f"{v:g}"


def _ref_line_get(seq, i, default):
    """Index into seq by position, reusing the last element when out-of-range.
    Returns *default* when seq is None or empty."""
    if not seq:
        return default
    return seq[i] if i < len(seq) else seq[-1]


def draw_vertical_lines(ax, values, labels=None, styles=None, colors=None, fontsize=None):
    """Draw one or more vertical reference lines on *ax*.

    Each positional list (``labels``, ``styles``, ``colors``) is matched to
    ``values`` by index; if shorter than ``values`` the last element is reused
    as a default.

    Labels default to the numeric value of each line (e.g. "0", "800").
    Pass ``labels=[]`` (empty list) to suppress all annotations.
    """
    if values is None:
        return
    vals = values if isinstance(values, (list, tuple)) else [values]

    for i, v in enumerate(vals):
        color = _ref_line_get(colors, i, "gray")
        style = _ref_line_get(styles, i, "--")
        label = _ref_line_get(labels, i, None) if labels is not None else _format_ref_value(v)
        xlim = ax.get_xlim()
        if v < xlim[0] or v > xlim[1]:
            ax.set_xlim(min(xlim[0], v), max(xlim[1], v))
        ax.axvline(v, color=color, linestyle=style, linewidth=1, zorder=5)
        if label:
            place_vertical_label(ax, v, label, fontsize=fontsize)


def draw_horizontal_lines(ax, values, labels=None, styles=None, colors=None, fontsize=None):
    """Draw one or more horizontal reference lines on *ax*.

    Each positional list (``labels``, ``styles``, ``colors``) is matched to
    ``values`` by index; if shorter than ``values`` the last element is reused
    as a default.

    Annotations are suppressed by default. Pass ``labels`` explicitly to show them.
    """
    if values is None:
        return
    vals = values if isinstance(values, (list, tuple)) else [values]

    for i, v in enumerate(vals):
        color = _ref_line_get(colors, i, "gray")
        style = _ref_line_get(styles, i, "--")
        label = _ref_line_get(labels, i, None) if labels is not None else None
        ylim = ax.get_ylim()
        if v < ylim[0] or v > ylim[1]:
            ax.set_ylim(min(ylim[0], v), max(ylim[1], v))
        ax.axhline(v, color=color, linestyle=style, linewidth=1, zorder=5)
        if label is not None and label:
            place_horizontal_label(ax, v, label, fontsize=fontsize)


def place_vertical_label(ax, x_value, label_text, fontsize=None, pad_fraction=0.02):
    """Place a label next to a vertical line at `x_value` in the least-populated vertical gap.

    The function inspects existing plotted data (lines, scatter collections, bars)
    and chooses the largest empty vertical gap at `x_value` to place the text.

    Args:
        ax: matplotlib Axes
        x_value: numeric x coordinate where the vertical line is placed
        label_text: text to display
        fontsize: optional font size
        pad_fraction: fraction of x-range to offset the label horizontally from the line

    Returns:
        matplotlib Text object or None
    """
    if label_text is None or not str(label_text).strip():
        return None

    text_str = str(label_text).strip()

    try:
        x0 = float(x_value)
    except Exception:
        # Fallback: place in upper-right corner
        return add_note_to_axes(ax, text_str, fontsize=fontsize)

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0] if xlim[1] != xlim[0] else 1.0

    # Collect y-positions occupied at/near x0
    y_occupied = []

    # Line2D objects
    for line in ax.get_lines():
        try:
            xd = np.asarray(line.get_xdata())
            yd = np.asarray(line.get_ydata())
            if xd.size == 0:
                continue
            xmin, xmax = xd.min(), xd.max()
            if xmin <= x0 <= xmax:
                y_at = np.interp(x0, xd, yd)
                if np.isfinite(y_at):
                    y_occupied.append(float(y_at))
        except Exception:
            continue

    # PathCollections (scatter)
    for col in getattr(ax, "collections", []):
        try:
            offsets = col.get_offsets()
            if offsets is None or len(offsets) == 0:
                continue
            xs = np.asarray(offsets)[:, 0]
            ys = np.asarray(offsets)[:, 1]
            x_tol = x_range * 0.02
            mask = np.isfinite(xs) & (np.abs(xs - x0) <= x_tol)
            y_occupied.extend(list(ys[mask]))
        except Exception:
            continue

    # Bars / patches: treat rectangles as occupying their vertical span if x0 falls inside
    for patch in getattr(ax, "patches", []):
        try:
            bbox = patch.get_bbox()
            if bbox.x0 <= x0 <= bbox.x1:
                y_occupied.append((bbox.y0 + bbox.y1) / 2.0)
        except Exception:
            continue

    # Build candidate gaps between ylim edges and occupied positions
    clean_points = [float(y) for y in y_occupied if np.isfinite(y) and ylim[0] <= y <= ylim[1]]
    candidates = [ylim[0]] + sorted(clean_points) + [ylim[1]]

    # For each gap, evaluate how many plotted points are within a small
    # rectangle around (x0, y_center). Choose gap with minimal nearby points
    # (avoids placing label on top of lines). Tie-breaker: larger gap.
    x_tol = max(x_range * 0.03, 1e-8)
    y_range = ylim[1] - ylim[0]
    text_height_est = max(0.06 * y_range, 0.0)

    best_candidate = None
    best_score = None
    for i in range(len(candidates) - 1):
        y0_gap = candidates[i]
        y1_gap = candidates[i + 1]
        gap_size = y1_gap - y0_gap
        if gap_size <= 0:
            continue
        y_center = (y0_gap + y1_gap) / 2.0
        # text vertical span to avoid (use fraction of gap and estimated text height)
        y_span = min(gap_size * 0.9, text_height_est if text_height_est > 0 else gap_size)
        ymin = y_center - y_span / 2.0
        ymax = y_center + y_span / 2.0

        count = 0

        # Count line points in neighborhood
        for line in ax.get_lines():
            try:
                xd = np.asarray(line.get_xdata())
                yd = np.asarray(line.get_ydata())
                if xd.size == 0:
                    continue
                # consider only points near x0 (interpolation gives single value, but sample nearby)
                mask = np.isfinite(xd) & np.isfinite(yd) & (xd >= x0 - x_tol) & (xd <= x0 + x_tol) & (yd >= ymin) & (yd <= ymax)
                count += int(np.count_nonzero(mask))
            except Exception:
                continue

        # Count scatter/collection offsets
        for col in getattr(ax, "collections", []):
            try:
                offsets = col.get_offsets()
                if offsets is None or len(offsets) == 0:
                    continue
                xs = np.asarray(offsets)[:, 0]
                ys = np.asarray(offsets)[:, 1]
                mask = np.isfinite(xs) & np.isfinite(ys) & (xs >= x0 - x_tol) & (xs <= x0 + x_tol) & (ys >= ymin) & (ys <= ymax)
                count += int(np.count_nonzero(mask))
            except Exception:
                continue

        # Count patches (bars) that intersect the rectangle
        for patch in getattr(ax, "patches", []):
            try:
                bbox = patch.get_bbox()
                if (bbox.x1 >= x0 - x_tol) and (bbox.x0 <= x0 + x_tol) and (bbox.y1 >= ymin) and (bbox.y0 <= ymax):
                    count += 1
            except Exception:
                continue

        score = (count, -gap_size)  # prefer fewer counts, then larger gap
        if best_score is None or score < best_score:
            best_score = score
            best_candidate = (y_center, gap_size)

    if best_candidate is None:
        y_text = (ylim[0] + ylim[1]) / 2.0
    else:
        y_text = best_candidate[0]

    # Horizontal offset: place label on side with more space (left/right)
    x_mid = (xlim[0] + xlim[1]) / 2.0
    pad = pad_fraction * x_range
    if x0 > x_mid:
        ha = "right"
        x_text = x0 - pad
    else:
        ha = "left"
        x_text = x0 + pad

    text_obj = ax.text(
        x_text,
        y_text,
        text_str,
        fontsize=fontsize,
        ha=ha,
        va="center",
        zorder=100,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
    )

    return text_obj


def place_horizontal_label(ax, y_value, label_text, fontsize=None, pad_fraction=0.02):
    """Place a label next to a horizontal line at `y_value` in the least-populated horizontal gap.

    Similar strategy to `place_vertical_label` but mirrored for x positions.
    """
    if label_text is None or not str(label_text).strip():
        return None

    text_str = str(label_text).strip()

    try:
        y0 = float(y_value)
    except Exception:
        return add_note_to_axes(ax, text_str, fontsize=fontsize)

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_range = ylim[1] - ylim[0] if ylim[1] != ylim[0] else 1.0

    x_occupied = []

    # Lines
    for line in ax.get_lines():
        try:
            xd = np.asarray(line.get_xdata())
            yd = np.asarray(line.get_ydata())
            if yd.size == 0:
                continue
            ymin, ymax = yd.min(), yd.max()
            if ymin <= y0 <= ymax:
                x_at = np.interp(y0, yd, xd)
                if np.isfinite(x_at):
                    x_occupied.append(float(x_at))
        except Exception:
            continue

    # Scatter collections
    for col in getattr(ax, "collections", []):
        try:
            offsets = col.get_offsets()
            if offsets is None or len(offsets) == 0:
                continue
            xs = np.asarray(offsets)[:, 0]
            ys = np.asarray(offsets)[:, 1]
            y_tol = y_range * 0.02
            mask = np.isfinite(ys) & (np.abs(ys - y0) <= y_tol)
            x_occupied.extend(list(xs[mask]))
        except Exception:
            continue

    # Patches: rectangles that cross y0
    for patch in getattr(ax, "patches", []):
        try:
            bbox = patch.get_bbox()
            if bbox.y0 <= y0 <= bbox.y1:
                x_occupied.append((bbox.x0 + bbox.x1) / 2.0)
        except Exception:
            continue

    clean_points = [float(x) for x in x_occupied if np.isfinite(x) and xlim[0] <= x <= xlim[1]]
    candidates = [xlim[0]] + sorted(clean_points) + [xlim[1]]

    y_tol = max(y_range * 0.03, 1e-8)
    x_range_full = xlim[1] - xlim[0]
    text_width_est = max(0.12 * x_range_full, 0.0)

    best_candidate = None
    best_score = None
    for i in range(len(candidates) - 1):
        x0_gap = candidates[i]
        x1_gap = candidates[i + 1]
        gap_size = x1_gap - x0_gap
        if gap_size <= 0:
            continue
        x_center = (x0_gap + x1_gap) / 2.0
        x_span = min(gap_size * 0.9, text_width_est if text_width_est > 0 else gap_size)
        xmin = x_center - x_span / 2.0
        xmax = x_center + x_span / 2.0

        count = 0

        # Count line points in neighborhood
        for line in ax.get_lines():
            try:
                xd = np.asarray(line.get_xdata())
                yd = np.asarray(line.get_ydata())
                if yd.size == 0:
                    continue
                mask = np.isfinite(xd) & np.isfinite(yd) & (yd >= y0 - y_tol) & (yd <= y0 + y_tol) & (xd >= xmin) & (xd <= xmax)
                count += int(np.count_nonzero(mask))
            except Exception:
                continue

        for col in getattr(ax, "collections", []):
            try:
                offsets = col.get_offsets()
                if offsets is None or len(offsets) == 0:
                    continue
                xs = np.asarray(offsets)[:, 0]
                ys = np.asarray(offsets)[:, 1]
                mask = np.isfinite(xs) & np.isfinite(ys) & (ys >= y0 - y_tol) & (ys <= y0 + y_tol) & (xs >= xmin) & (xs <= xmax)
                count += int(np.count_nonzero(mask))
            except Exception:
                continue

        for patch in getattr(ax, "patches", []):
            try:
                bbox = patch.get_bbox()
                if (bbox.y1 >= y0 - y_tol) and (bbox.y0 <= y0 + y_tol) and (bbox.x1 >= xmin) and (bbox.x0 <= xmax):
                    count += 1
            except Exception:
                continue

        score = (count, -gap_size)
        if best_score is None or score < best_score:
            best_score = score
            best_candidate = (x_center, gap_size)

    if best_candidate is None:
        x_text = (xlim[0] + xlim[1]) / 2.0
    else:
        x_text = best_candidate[0]

    y_mid = (ylim[0] + ylim[1]) / 2.0
    pad = pad_fraction * y_range
    if y0 > y_mid:
        va = "top"
        y_pos = y0 - pad
    else:
        va = "bottom"
        y_pos = y0 + pad

    text_obj = ax.text(
        x_text,
        y_pos,
        text_str,
        fontsize=fontsize,
        ha="center",
        va=va,
        zorder=100,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
    )

    return text_obj


def place_point_label(ax, point_x, point_y, label_text, fontsize=None):
    """Place a label next to a scattered point.

    Args:
        ax: matplotlib axes object
        point_x: x coordinate of the point
        point_y: y coordinate of the point
        label_text: text to display
        fontsize: optional font size

    Returns:
        matplotlib text object
    """
    if label_text is None or not str(label_text).strip():
        return None

    text_str = str(label_text).strip()

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    x_offset = x_range * 0.02
    y_offset = y_range * 0.03

    text_obj = ax.text(
        point_x + x_offset,
        point_y + y_offset,
        text_str,
        fontsize=fontsize,
        ha="left",
        va="bottom",
        zorder=100,
        bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
    )

    return text_obj

