#!/usr/bin/env python3

"""
Script: integrated yield versus a categorical column in DUNE style.

Each dataframe row carries an array column (``--y``, e.g. ``Counts``) binned
along another array column (``--integrate_over``, e.g. ``Energy``) and a
categorical column (``--x``, e.g. ``Stage``). The macro integrates ``y`` over
the ``--integrate_over`` axis (optionally within ``--integration_range``) and
draws one point per category, one line per ``--iterable`` value (colour) and,
optionally, per ``--comparable`` value (linestyle).

Written for the SOLAR cutflow pkls (one row per selection stage with a
30-bin spectrum each), e.g. integrated signal and background counts per
selection stage:

    scripts/script_compare_integral.py --datafile SolarEnergy_DayNight_Cutflow \
        --configs hd_1x2x6_centralAPA --names marley gamma neutron radiological \
        --overlay_names -x Stage -y Counts --integrate_over Energy \
        -i Component --logy --xtick_mapping stage_dict
"""

from _bootstrap import ensure_src_path

ensure_src_path()

import matplotlib.lines as mlines
from rich import print as rprint

from lib import *
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args
from lib.imports import import_data, prepare_import
from lib.plot import (
    apply_legend_style,
    create_common_subplots,
    apply_note_to_figure,
    add_centered_suptitle,
    draw_horizontal_lines,
    plot_data,
)
from lib.selection import filter_dataframe
from common_args import add_common_args, map_iterable_label, map_iterable_color, resolve_axis_label


parser = argparse.ArgumentParser(
    description="Integrate an array column per category and plot the integral versus the category"
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
        "filename_select",
        "x",
        "y",
        "labelx",
        "labely",
        "logy",
        "rangey",
        "plot_type",
        "title",
        "output",
        "subfolder",
        "horizontal",
        "horizontal_label",
        "horizontal_style",
        "horizontal_color",
        "note",
        "multiply",
        "debug",
    ],
    overrides={
        "datafile": {"required": True},
        "x": {"required": True, "help": "Categorical column (one point per unique value), e.g. Stage"},
        "y": {"required": True, "help": "Array column integrated per row, e.g. Counts"},
        "iterable": {"required": True, "help": "Column whose values become separate lines (colour), e.g. Component"},
        "plot_type": {"choices": ["line", "scatter", "bar"], "default": "line"},
    },
)

parser.add_argument("--integrate_over", type=str, default="Energy", help="Array column giving the bin centres of --y (default: Energy)")
parser.add_argument("--integration_range", type=float, nargs=2, default=None, metavar=("LO", "HI"), help="Only integrate bins whose --integrate_over value lies in [LO, HI]")
parser.add_argument(
    "--integral_mode",
    type=str,
    default="integrate",
    choices=["integrate", "sum"],
    help="'integrate' multiplies each bin by its width (densities such as events/MeV -> events); 'sum' adds the raw values",
)
parser.add_argument("--comparable", "-c", type=str, default=None, help="Secondary column drawn with distinct linestyles, e.g. Study or Config")
parser.add_argument("--comparable_linestyles", nargs="+", type=str, default=None, help="Linestyles cycled over --comparable values (default: - -- : -.)")
parser.add_argument("--comparable_mapping", type=str, default=None, help="plot_params mapping used to rename --comparable values in the legend")
parser.add_argument("--comparable_title", type=str, default=None, help="Legend heading for the comparable section (default: the column name)")
parser.add_argument("--iterable_mapping", type=str, default=None, help="plot_params mapping used to rename --iterable values in the legend")
parser.add_argument("--iterable_color_mapping", type=str, default=None, help="plot_params mapping giving the colour per --iterable value")
parser.add_argument("--xtick_mapping", type=str, default=None, help="plot_params mapping used to rename the --x categories on the axis")
parser.add_argument("--x_order", nargs="+", type=str, default=None, help="Explicit order of the --x categories (default: first-seen order)")
parser.add_argument("--errory", action="store_true", default=False, help="Propagate --y's Error column (added in quadrature) as error bars")
parser.add_argument(
    "--overlay_names",
    action="store_true",
    default=False,
    help="Combine all --configs/--names combinations into a single figure instead of one figure per pair",
)

args = parser.parse_args()

_LINESTYLES = ["-", "--", ":", "-."]
_MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]


def _integrate_row(row):
    y = np.asarray(row[args.y], dtype=float)
    yerr_col = f"{args.y}Error"
    yerr = np.asarray(row[yerr_col], dtype=float) if args.errory and yerr_col in row.index and row[yerr_col] is not None else None
    grid = row[args.integrate_over] if args.integrate_over in row.index else None
    if grid is None or np.ndim(grid) == 0:
        grid = np.arange(len(y), dtype=float)
    grid = np.asarray(grid, dtype=float)

    if args.integral_mode == "integrate" and len(grid) > 1:
        widths = np.gradient(grid)
    else:
        widths = np.ones_like(grid)

    mask = np.isfinite(y)
    if args.integration_range is not None:
        lo, hi = args.integration_range
        mask &= (grid >= lo) & (grid <= hi)

    value = float(np.sum(y[mask] * widths[mask]))
    error = float(np.sqrt(np.sum((yerr[mask] * widths[mask]) ** 2))) if yerr is not None and len(yerr) == len(y) else None
    if args.multiply is not None:
        value *= args.multiply
        if error is not None:
            error *= args.multiply
    return value, error


def _ordered_unique(values, explicit=None):
    seen = []
    for v in values:
        if v not in seen:
            seen.append(v)
    if explicit:
        return [v for v in explicit if v in seen] + [v for v in seen if v not in explicit]
    return seen


def _map(value, column, mapping):
    return map_iterable_label(value, column, mapping)


def main():
    df = import_data(args)
    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    for col in (args.x, args.y, args.iterable):
        if col not in df.columns:
            rprint(f"[red]Error:[/red] Column '{col}' not found. Available: {', '.join(map(str, df.columns))}")
            return

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]
    if args.overlay_names:
        configs, names = [None], [None]

    comparable_col = args.comparable if args.comparable in df.columns else None
    if args.comparable is not None and comparable_col is None:
        rprint(f"[yellow]Warning:[/yellow] Comparable column '{args.comparable}' not found; drawing a single line per iterable value.")

    for kdx, (config, name) in enumerate(zip(configs, names)):
        df_config = df
        if config is not None:
            df_config = df_config[df_config["Config"] == config]
        if name is not None:
            df_config = df_config[df_config["Name"] == name]
        df_config = filter_dataframe(df_config, args)
        df_config = df_config[df_config[args.iterable].notna()]
        if df_config.empty:
            rprint(f"[yellow]Warning:[/yellow] No data for Config={config}, Name={name}. Skipping.")
            continue

        categories = _ordered_unique(df_config[args.x].tolist(), args.x_order)
        iterables = _ordered_unique(df_config[args.iterable].tolist())
        comparables = _ordered_unique(df_config[comparable_col].dropna().tolist()) if comparable_col else [None]
        linestyles = args.comparable_linestyles or _LINESTYLES
        positions = np.arange(len(categories), dtype=float)

        fig, ax = create_common_subplots(nrows=1, ncols=1)

        handles_iter = []
        handles_comp = []
        for idx, iterable in enumerate(iterables):
            color = map_iterable_color(iterable, args.iterable_color_mapping, args.iterable) or f"C{idx % 10}"
            iter_label = _map(iterable, args.iterable, args.iterable_mapping)
            handles_iter.append(mlines.Line2D([], [], color=color, linestyle="-", marker=_MARKERS[idx % len(_MARKERS)], label=iter_label))
            for cdx, comparable in enumerate(comparables):
                subset = df_config[df_config[args.iterable] == iterable]
                if comparable is not None:
                    subset = subset[subset[comparable_col] == comparable]
                if subset.empty:
                    continue
                linestyle = linestyles[cdx % len(linestyles)]
                xs, ys, es = [], [], []
                for pos, category in zip(positions, categories):
                    rows = subset[subset[args.x] == category]
                    if rows.empty:
                        continue
                    totals = [_integrate_row(row) for _, row in rows.iterrows()]
                    xs.append(pos)
                    ys.append(sum(v for v, _ in totals))
                    errs = [e for _, e in totals if e is not None]
                    es.append(float(np.sqrt(np.sum(np.square(errs)))) if errs else np.nan)
                if not xs:
                    continue
                xs, ys, es = np.asarray(xs), np.asarray(ys), np.asarray(es)
                rprint(f"\tIntegrals for {args.iterable}={iterable}" + (f", {comparable_col}={comparable}" if comparable is not None else "") + f": " + ", ".join(f"{c}={v:.3g}" for c, v in zip([categories[int(i)] for i in xs], ys)))
                if args.plot_type == "bar":
                    width = 0.8 / max(1, len(iterables))
                    ax.bar(xs + (idx - (len(iterables) - 1) / 2) * width, ys, width=width, color=color, alpha=0.9 if cdx == 0 else 0.5, label=None)
                else:
                    kwargs = {"marker": _MARKERS[idx % len(_MARKERS)]} if args.plot_type != "scatter" else {}
                    if args.errory and np.isfinite(es).any():
                        ax.errorbar(xs, ys, yerr=np.nan_to_num(es), color=color, linestyle=linestyle if args.plot_type == "line" else "none", capsize=3, **kwargs)
                    else:
                        plot_data(args, ax, xs, y=ys, color=color, plot_type=args.plot_type, linestyle=linestyle, **kwargs)
                if comparable is not None and cdx >= len(handles_comp):
                    handles_comp.append(mlines.Line2D([], [], color="black", linestyle=linestyle, label=_map(comparable, comparable_col, args.comparable_mapping)))

        ax.set_xticks(positions)
        ax.set_xticklabels([_map(c, args.x, args.xtick_mapping) for c in categories], rotation=20, ha="right", rotation_mode="anchor")
        ax.set_xlabel(resolve_axis_label(args.labelx, args.x, df_config))
        ylabel = args.labely
        if ylabel is None:
            unit = df_config["CountsUnit"].iloc[0] if "CountsUnit" in df_config.columns else None
            if unit and args.integral_mode == "integrate" and "/ MeV" in str(unit):
                unit = str(unit).replace(" / MeV", "")
            ylabel = f"Integrated {args.y}" + (f" ({unit})" if unit else "")
        ax.set_ylabel(ylabel)
        if args.logy:
            ax.set_yscale("log")
        if args.rangey is not None:
            ax.set_ylim(args.rangey)
        ax.set_xlim(-0.5, len(categories) - 0.5)
        ax.grid(True, axis="y", alpha=0.3)

        draw_horizontal_lines(
            ax,
            getattr(args, "horizontal", None),
            labels=getattr(args, "horizontal_label", None),
            styles=getattr(args, "horizontal_style", None),
            colors=getattr(args, "horizontal_color", None),
        )

        handles = list(handles_iter)
        if handles_comp:
            title = args.comparable_title if args.comparable_title is not None else comparable_col
            handles.append(mlines.Line2D([], [], color="none", label=f"$\\bf{{{title}}}$" if title else ""))
            handles += handles_comp
        apply_legend_style(ax, handles=handles, capitalize_labels=getattr(args, "capitalize_legend", False), loc="lower left")

        add_centered_suptitle(fig, make_title_from_args(args), fontsize=titlefontsize)
        apply_note_to_figure(fig, getattr(args, "note", None))
        fig.subplots_adjust(bottom=0.22)

        output_file = make_name_from_args(args, idx=None if args.overlay_names else kdx, suffix="integral.png")
        default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "plots")
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint, subfolder=args.subfolder)
        if args.overlay_names:
            break


if __name__ == "__main__":
    main()
