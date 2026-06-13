#!/usr/bin/env python3

from _bootstrap import ensure_src_path

ensure_src_path()

from pathlib import Path
import argparse
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich import print as rprint

from common_args import add_common_args
from lib import titlefontsize, xlabelfontsize, ysublabelfontsize, linelabelfontsize
from lib.format import make_title_from_args
from lib.selection import filter_dataframe
from lib.plot import apply_legend_style, plot_data, create_common_subplots, create_common_two_panel_figure, apply_note_to_figure, apply_common_figure_margins, draw_vertical_lines, draw_horizontal_lines, place_point_label



def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Two-panel line and scatter macro. "
            "Upper panel draws a line series, lower panel draws a single scatter comparison series."
        )
    )

    add_common_args(
        parser,
        [
            "datafile",
            "iterable",
            "variables",
            "select",
            "save_values",
            "x",
            "y",
            "labelx",
            "labely",
            "labelz",
            "rangex",
            "rangey",
            "logx",
            "logy",
            "horizontal",
            "horizontal_label",
            "horizontal_style",
            "horizontal_color",
            "vertical",
            "vertical_label",
            "vertical_style",
            "vertical_color",
            "plot_style",
            "title",
            "output",
            "note",
            "debug",
        ],
        overrides={
            "datafile": {
                "required": True,
                "help": "Input pickle path or basename of a data file in input/data",
            },
            "iterable": {
                "default": None,
                "help": "Optional column used for splitting rows",
            },
            "x": {"default": "TimeNS", "help": "X column for upper panel"},
            "y": {"default": "UpperY", "help": "Y column for upper panel"},
            "labelx": {"default": "Time [ns]"},
            "labely": {"default": "Amplitude"},
            "labelz": {"help": "Legend title for the upper panel"},
            "output": {"required": False, "help": "Output image path or directory"},
        },
    )

    parser.add_argument(
        "--iterable_value",
        "--iterable-value",
        type=str,
        default=None,
        help="Optional single iterable value to plot",
    )
    parser.add_argument(
        "--lower_series",
        "--lower-series",
        type=str,
        default="OpHit",
        help="Lower panel series prefix to render (for example OpHit or Photon)",
    )
    parser.add_argument(
        "--line_label",
        "--line-label",
        type=str,
        default=None,
        help="Legend label for the upper line",
    )
    parser.add_argument(
        "--lower_labely",
        "--lower-labely",
        "--lower_label",
        "--lower-label",
        type=str,
        default="Scatter value",
        help="Y-axis label for lower panel",
    )
    parser.add_argument(
        "--lower_plot_style",
        "--lower-plot-style",
        type=str,
        choices=["scatter", "hist"],
        default="scatter",
        help="Rendering style for lower panel series",
    )
    parser.add_argument(
        "--lower_hist_bins",
        "--lower-hist-bins",
        type=int,
        default=50,
        help="Number of bins used when --lower_plot_style hist is selected",
    )
    parser.add_argument(
        "--lower_series_density",
        "--lower-series-density",
        action="store_true",
        default=False,
        help="When using lower hist mode, divide each bin amplitude by bin width",
    )
    parser.add_argument(
        "--lower_series_range",
        "--lower-series-range",
        action="store_true",
        default=False,
        help="Use *Start/*End columns for the lower series and draw horizontal range bars",
    )
    parser.add_argument(
        "--lower_show_range_bars",
        "--lower-show-range-bars",
        action="store_true",
        default=False,
        help="Deprecated alias for --lower_series_range",
    )
    parser.add_argument(
        "--lower_vertical_lines",
        "--lower-vertical-lines",
        action="store_true",
        default=False,
        help="Draw vertical guide lines at each lower-panel scatter x-position through both panels",
    )
    parser.add_argument(
        "--show_highlights",
        "--show-highlights",
        action="store_true",
        default=False,
        help="Overlay highlight windows on the upper panel",
    )
    parser.add_argument(
        "--highlight_start_column",
        "--highlight-start-column",
        type=str,
        default=None,
        help="Start column for upper panel highlight windows",
    )
    parser.add_argument(
        "--highlight_end_column",
        "--highlight-end-column",
        type=str,
        default=None,
        help="End column for upper panel highlight windows",
    )
    parser.add_argument(
        "--highlight_center_column",
        "--highlight-center-column",
        type=str,
        default=None,
        help="Center marker column for upper panel highlight windows",
    )
    parser.add_argument(
        "--highlight_color",
        "--highlight-color",
        type=str,
        default="C1",
        help="Color for upper panel highlight windows",
    )

    return parser.parse_args()


def load_df(path):
    candidate = Path(path)
    repo_root = Path(__file__).resolve().parents[1]
    input_dir = repo_root / "input" / "data"

    candidates = [candidate]
    if candidate.suffix == ".pkl":
        candidates.append(input_dir / candidate.name)
    else:
        candidates.append(input_dir / f"{candidate.name}.pkl")

    for resolved_path in candidates:
        if not resolved_path.exists():
            continue

        with resolved_path.open("rb") as input_file:
            data = pickle.load(input_file)

        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict):
            return pd.DataFrame(data)

        return pd.DataFrame(data)

    raise FileNotFoundError(f"Could not find input data file for '{path}'")


def _to_array(row, column):
    value = row[column]
    return np.asarray(value, dtype=float).ravel()


def _to_array_or_zero(row, column, fallback_length):
    if column is None or column not in row:
        return np.zeros(fallback_length, dtype=float)

    values = np.asarray(row[column], dtype=float).ravel()
    if values.size == 0:
        return np.zeros(fallback_length, dtype=float)

    if values.size == 1 and fallback_length > 1:
        value = values[0]
        if np.isfinite(value):
            return np.full(fallback_length, value, dtype=float)
        return np.zeros(fallback_length, dtype=float)

    if values.size < fallback_length:
        padded = np.zeros(fallback_length, dtype=float)
        padded[: values.size] = values
        return padded

    return values[:fallback_length]


def _normalize_lower_series(value):
    series_raw = str(value).strip()
    if not series_raw:
        raise ValueError("Invalid --lower-series. Provide a non-empty prefix such as OpHit or Photon")
    return series_raw


def _resolve_column(row, explicit_column, fallback_candidates):
    if explicit_column is not None:
        return explicit_column

    for candidate in fallback_candidates:
        if candidate in row:
            return candidate

    return None


def _resolve_prefixed_column(row, prefix, preferred_tokens, fallback_tokens=()):
    if prefix is None:
        return None

    prefix_text = str(prefix).strip()
    if not prefix_text:
        return None

    lower_prefix = prefix_text.lower()
    available_columns = list(row.index)

    exact_candidates = []
    for token in preferred_tokens:
        exact_candidates.extend(
            [
                f"{prefix_text}{token}",
                f"{prefix_text}{token}NS",
                f"{prefix_text}{token}PE",
                f"{prefix_text}{token}MeV",
                f"{prefix_text}{token}GeV",
            ]
        )
    for token in fallback_tokens:
        exact_candidates.extend(
            [
                f"{prefix_text}{token}",
                f"{prefix_text}{token}NS",
                f"{prefix_text}{token}PE",
            ]
        )

    exact_candidates.extend(
        [
            f"True{prefix_text}{token}" for token in preferred_tokens
        ]
    )

    for candidate in exact_candidates:
        if candidate in row:
            return candidate

    if prefix_text in row:
        return prefix_text

    for column in available_columns:
        column_text = str(column)
        column_lower = column_text.lower()
        if not (column_lower.startswith(lower_prefix) or column_lower.startswith(f"true{lower_prefix}")):
            continue
        if preferred_tokens and any(token.lower() in column_lower for token in preferred_tokens):
            return column_text
        if fallback_tokens and any(token.lower() in column_lower for token in fallback_tokens):
            return column_text

    return None


def _resolve_lower_series_columns(row, prefix):
    x_column = _resolve_prefixed_column(
        row,
        prefix,
        preferred_tokens=("Time", "Peak", "X", "Position"),
        fallback_tokens=("TimeNS", "PeakNS", "X"),
    )
    y_column = _resolve_prefixed_column(
        row,
        prefix,
        preferred_tokens=("Area", "Count", "Value", "Amplitude", "Y"),
        fallback_tokens=("AreaPE", "Count", "Y"),
    )
    start_column = _resolve_prefixed_column(
        row,
        prefix,
        preferred_tokens=("Start",),
        fallback_tokens=("Start",),
    )
    end_column = _resolve_prefixed_column(
        row,
        prefix,
        preferred_tokens=("End",),
        fallback_tokens=("End",),
    )
    center_column = _resolve_prefixed_column(
        row,
        prefix,
        preferred_tokens=("Peak", "Center", "Time", "X"),
        fallback_tokens=("Peak", "Center", "X"),
    )

    if x_column == y_column:
        y_column = None

    return x_column, y_column, start_column, end_column, center_column


def _plot_scatter_series(
    ax,
    row,
    x_column,
    y_column,
    label,
    color,
    size,
    plot_style="scatter",
    hist_bins=50,
    hist_density=False,
    show_range_bars=False,
    range_start_column=None,
    range_end_column=None,
    vertical_lines=False,
    top_ax=None,
    vertical_color="gray",
    vertical_alpha=0.5,
):
    if x_column not in row:
        return

    x_values = np.asarray(row[x_column], dtype=float).ravel()
    if x_values.size == 0:
        return

    if plot_style == "hist":
        counts, edges = np.histogram(x_values, bins=hist_bins)
        values = counts.astype(float)

        if hist_density:
            widths = np.diff(edges)
            safe_widths = np.where(widths > 0.0, widths, 1.0)
            values = values / safe_widths

        centers = (edges[:-1] + edges[1:]) / 2.0
        ax.plot(
            centers,
            values,
            drawstyle="steps-mid",
            linewidth=1.5,
            color=color,
            label=label,
        )
        return

    y_values = _to_array_or_zero(row, y_column, x_values.size)
    ax.scatter(x_values, y_values, color=color, s=size, marker="o", label=label)

    if vertical_lines and top_ax is not None:
        for x_value in x_values:
            ax.axvline(x_value, color=vertical_color, linestyle="--", linewidth=0.8, alpha=vertical_alpha, zorder=0)
            top_ax.axvline(x_value, color=vertical_color, linestyle="--", linewidth=0.8, alpha=vertical_alpha, zorder=0)

    if not show_range_bars:
        return
    if range_start_column is None or range_end_column is None:
        return
    if range_start_column not in row or range_end_column not in row:
        return

    starts = np.asarray(row[range_start_column], dtype=float).ravel()
    ends = np.asarray(row[range_end_column], dtype=float).ravel()
    count = min(x_values.size, y_values.size, starts.size, ends.size)
    if count == 0:
        return

    x_used = x_values[:count]
    y_used = y_values[:count]
    starts_used = starts[:count]
    ends_used = ends[:count]

    xerr_minus = np.clip(x_used - starts_used, a_min=0.0, a_max=None)
    xerr_plus = np.clip(ends_used - x_used, a_min=0.0, a_max=None)
    xerr = np.vstack([xerr_minus, xerr_plus])

    ax.errorbar(
        x_used,
        y_used,
        xerr=xerr,
        fmt="none",
        ecolor=color,
        elinewidth=1.0,
        alpha=0.85,
        capsize=0,
    )


def _overlay_windows(ax, row, start_column, end_column, center_column, color):
    if start_column is None or end_column is None or center_column is None:
        return

    required = [start_column, end_column, center_column]
    if any(col not in row for col in required):
        return

    starts = np.asarray(row[start_column], dtype=float).ravel()
    ends = np.asarray(row[end_column], dtype=float).ravel()
    peaks = np.asarray(row[center_column], dtype=float).ravel()

    for idx in range(min(starts.size, ends.size, peaks.size)):
        ax.axvspan(starts[idx], ends[idx], color=color, alpha=0.14, zorder=1)
        ax.axvline(peaks[idx], color=color, linestyle="--", linewidth=0.8, alpha=0.8, zorder=2)


def _resolve_output_path(args, row):
    datafile_name = Path(args.datafile).stem if Path(args.datafile).suffix else Path(args.datafile).name
    iterable_value = (
        str(row[args.iterable])
        if args.iterable is not None and args.iterable in row and pd.notna(row[args.iterable])
        else "data"
    )
    variables_part = "_".join(args.variables) if getattr(args, "variables", None) else None
    safe_parts = [datafile_name, iterable_value, args.lower_series, variables_part, args.lower_plot_style, "line_scatter_panel"]
    file_name = "_".join(
        part.replace(" ", "_").replace("/", "_") for part in safe_parts if part
    )

    # Default structure: <repo>/output/plots/<generated_name>.png
    if args.output is None:
        default_output_dir = Path(__file__).resolve().parents[1] / "output" / "plots"
        default_output_dir.mkdir(parents=True, exist_ok=True)
        return default_output_dir / f"{file_name}.png"

    output_value = args.output[0] if isinstance(args.output, list) else args.output
    output_path = Path(output_value)

    if output_path.suffix:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    output_path.mkdir(parents=True, exist_ok=True)
    return output_path / f"{file_name}.png"


def _print_dataframe_debug(df, title):
    rprint(title)
    rprint("DataFrame columns and types:")
    rprint({col: df[col].dtype for col in df.columns})
    rprint("\nDataFrame preview:")
    rprint(df)


def main():
    args = parse_args()
    df = load_df(args.datafile)

    if df.empty:
        raise ValueError("Input dataframe is empty")

    if args.iterable is not None and args.iterable not in df.columns:
        if args.debug:
            rprint(
                f"[yellow]Warning:[/yellow] Iterable column '{args.iterable}' is missing; using the full dataframe."
            )

    if (
        args.iterable is not None and args.iterable in df.columns
    ) or args.variables is not None or args.select is not None or args.save_values is not None:
        df = filter_dataframe(df, args)

    if args.debug:
        _print_dataframe_debug(df, "[cyan]Debug:[/cyan] Filtered dataframe")

    if args.iterable_value is not None:
        if args.iterable is not None and args.iterable in df.columns:
            df = df[df[args.iterable] == args.iterable_value]
        elif args.debug:
            rprint(
                f"[yellow]Warning:[/yellow] --iterable-value was provided but no iterable column is active; ignoring it."
            )

    if df.empty:
        raise ValueError("No rows match iterable selection")

    if len(df) > 1 and args.iterable_value is None:
        rprint(
            f"[yellow]Warning:[/yellow] Multiple rows found; using the first one."
        )

    row = df.iloc[0]

    lower_series_prefix = _normalize_lower_series(args.lower_series)
    lower_x_column, lower_y_column, lower_start_column, lower_end_column, highlight_center = _resolve_lower_series_columns(
        row,
        lower_series_prefix,
    )
    if not (args.lower_series_range or args.lower_show_range_bars):
        lower_start_column = None
        lower_end_column = None

    highlight_start = lower_start_column
    highlight_end = lower_end_column

    x = _to_array(row, args.x)
    y = _to_array_or_zero(row, args.y, x.size)

    render_lower = True
    if render_lower:
        fig, grid = create_common_two_panel_figure(
            ncols=1,
            height_ratios=[3, 1],
        )
        ax_top = fig.add_subplot(grid[0])
        ax_bottom = fig.add_subplot(grid[1], sharex=ax_top)
    else:
        fig, ax_top = create_common_subplots(nrows=1, ncols=1)
        ax_bottom = None

    label = args.line_label if args.line_label is not None else (
        str(row[args.iterable]) if args.iterable is not None and args.iterable in row else "Line"
    )
    plot_data(
        args,
        ax_top,
        x,
        y=y,
        label=label,
        color="C0",
        linestyle=args.plot_style,
        plot_type="plot",
    )

    if args.show_highlights:
        _overlay_windows(
            ax_top,
            row,
            highlight_start,
            highlight_end,
            highlight_center,
            args.highlight_color,
        )

    ax_top.set_ylabel(args.labely, fontsize=ysublabelfontsize)
    ax_top.grid(alpha=0.25)

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

    apply_legend_style(
        ax_top,
        title=args.labelz if args.labelz is not None else None,
        capitalize_labels=not getattr(args, "no_capitalize_legend", False),
    )

    if ax_bottom is not None:
        active_x = lower_x_column
        active_y = lower_y_column
        active_label = lower_series_prefix
        active_color = "C1"
        active_size = 26

        _plot_scatter_series(
            ax_bottom,
            row,
            active_x,
            active_y,
            active_label,
            active_color,
            active_size,
            plot_style=args.lower_plot_style,
            hist_bins=args.lower_hist_bins,
            hist_density=args.lower_series_density,
            show_range_bars=args.lower_series_range or args.lower_show_range_bars,
            range_start_column=lower_start_column,
            range_end_column=lower_end_column,
            vertical_lines=args.lower_vertical_lines and args.lower_plot_style == "scatter",
            top_ax=ax_top,
            vertical_color=active_color,
            vertical_alpha=0.55,
        )

        ax_bottom.set_ylabel(args.lower_labely, fontsize=ysublabelfontsize)
        ax_bottom.set_xlabel(args.labelx, fontsize=xlabelfontsize)
        ax_bottom.grid(alpha=0.25)
        bottom_handles, _ = ax_bottom.get_legend_handles_labels()
        if bottom_handles:
            apply_legend_style(
                ax_bottom,
                capitalize_labels=not getattr(args, "no_capitalize_legend", False),
            )
    else:
        ax_top.set_xlabel(args.labelx, fontsize=xlabelfontsize)

    if args.rangex is not None:
        ax_top.set_xlim(args.rangex)
        if ax_bottom is not None:
            ax_bottom.set_xlim(args.rangex)

    if args.rangey is not None:
        ax_top.set_ylim(args.rangey)

    if ax_bottom is not None and args.rangey is None and not args.logy:
        if args.lower_plot_style == "hist":
            _bottom_min, bottom_max = ax_bottom.get_ylim()
            ax_bottom.set_ylim(0.0, bottom_max)
        else:
            bottom_min, bottom_max = ax_bottom.get_ylim()
            data_span = bottom_max - bottom_min
            if data_span < 1.0:
                # 1D scatter: all y-values are effectively the same (e.g. zero)
                mid = (bottom_min + bottom_max) / 2.0
                ax_bottom.set_ylim(mid - 0.5, mid + 1.5)
            else:
                margin = 0.15 * data_span
                ax_bottom.set_ylim(bottom_min - margin, bottom_max + margin)

    if args.logx:
        ax_top.set_xscale("log")
        if ax_bottom is not None:
            ax_bottom.set_xscale("log")

    if args.logy:
        ax_top.set_yscale("log")
        if ax_bottom is not None:
            ax_bottom.set_yscale("log")

    fig.suptitle(make_title_from_args(args), fontsize=titlefontsize)
    apply_common_figure_margins(fig)

    apply_note_to_figure(fig, getattr(args, "note", None))

    output_path = _resolve_output_path(args, row)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)

    print("Saved line panel figure to", output_path)


if __name__ == "__main__":
    main()
