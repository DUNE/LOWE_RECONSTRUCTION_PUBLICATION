#!/usr/bin/env python3

"""
Script 4: Fit representation of a Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling and fit representation
"""

from _bootstrap import ensure_src_path

ensure_src_path()

import warnings

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_title_from_args, make_subtitle_from_args
from lib.imports import import_data, prepare_import
from lib.functions import (
    resolution,
    gaussian,
    correction_func,
    quadratic_cut,
    quadratic_function,
)
from lib.plot import apply_legend_style, plot_data, create_common_subplots, create_common_two_panel_figure, apply_note_to_figure, draw_vertical_lines, draw_horizontal_lines, place_point_label

from common_args import add_common_args, resolve_axis_label

# Remove RuntimeWarning: overflow encountered in divide
warnings.filterwarnings("ignore", category=RuntimeWarning)

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
        "x",
        "y",
        "iterable",
        "select",
        "save_values",
        "reduce",
        "labelx",
        "labely",
        "labelz",
        "logx",
        "logy",
        "rangex",
        "rangey",
        "title",
        "output",
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
        "datafile": {"default": "NHit_Distributions"},
        "names": {"flags": ["--names"]},
        "x": {"default": "Values"},
        "y": {"default": "Density"},
        "labelx": {"default": "True Neutrino Energy (MeV)"},
        "labelz": {"help": "Title for legend on plot (if applicable)"},
        "reduce": {
            "help": "Reduce the number of plotted lines by only plotting every other line for cases with many unique iterables"
        },
    },
)

parser.add_argument(
    "--chi2",
    action="store_true",
    help="Display chi2 on the plot",
    default=False,
)

parser.add_argument(
    "--fitindex",
    type=int,
    default=0,
    help="Index of the fit to plot (if multiple fits are available in the data)",
)

parser.add_argument(
    "--fitlegendposition",
    nargs=2,
    type=float,
    help="Position of the fit legend on the plot as (x,y) coordinates in axes fraction",
    default=(0.55, 0.90),
)

parser.add_argument(
    "--errorx",
    action="store_true",
    help="Set x-axis to show error bars",
    default=False,
)

parser.add_argument(
    "--errory",
    action="store_true",
    help="Set y-axis to show error bars",
    default=False,
)

parser.add_argument(
    "--no_lower_plot",
    action="store_true",
    help="Disable rendering of the lower residual subplot",
    default=False,
)


args = parser.parse_args()


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

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    # Select the entries in the dataframe with with name matching args.name and nake a plot for each iterable
    for kdx, (config, name) in enumerate(zip(configs, names)):
        render_lower_plot = not getattr(args, "no_lower_plot", False)
        if render_lower_plot:
            fig, gs = create_common_two_panel_figure(
                ncols=1,
                height_ratios=[3, 1],
            )
            ax_top = fig.add_subplot(gs[0])
            ax_bottom = fig.add_subplot(gs[1], sharex=ax_top)
        else:
            fig, ax_top = create_common_subplots(nrows=1, ncols=1)
            ax_bottom = None

        limit = 1
        df_config = df[(df["Config"] == config) & (df["Name"] == name)]
        fit_function_label = None

        # variables = args.variables if args.variables is not None else [None]
        iterables = (
            df_config[args.iterable].unique() if args.iterable is not None else [None]
        )
        for jdx, iterable in enumerate(iterables):
            if args.reduce and args.iterable is not None:
                if df_config[args.iterable].unique().size > 8:
                    if jdx % 2 == 1:
                        rprint(
                            f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding"
                        )
                        continue
                else:
                    rprint(
                        f"\tNot reducing plotted lines for {args.iterable} since there are only {df_config[args.iterable].unique().size} unique values"
                    )

            if iterable is not None:
                if args.debug:
                    rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
                df_iterable = df_config[(df_config[args.iterable] == iterable)]

            else:
                df_iterable = df_config.copy()

            subset = filter_dataframe(df_iterable, args)
            if subset.empty:
                continue

            fit_function_label = subset["FitFunctionLabel"].iloc[0]

            x = subset[args.x].values[0].astype(float)
            y = subset[args.y].values[0].astype(float)

            params = subset["Params"].iloc[0]
            params_format = subset["ParamsFormat"].iloc[0]
            params_labels = subset["ParamsLabel"].iloc[0]
            params_error = subset["ParamsError"].iloc[0]
            params_units = subset["ParamsUnit"].iloc[0] if "ParamsUnit" in subset.columns else None
            func = subset["FitFunction"].iloc[0]
            fit = func(x, *params)
            y_error = None

            if params_units is None or (
                isinstance(params_units, float) and np.isnan(params_units)
            ):
                params_units = [""] * len(params)
            elif isinstance(params_units, str):
                params_units = [params_units] * len(params)
            elif isinstance(params_units, (list, tuple, np.ndarray, pd.Series)):
                params_units = list(params_units)
            else:
                params_units = [str(params_units)] * len(params)

            if len(params_units) < len(params):
                params_units = params_units + [""] * (len(params) - len(params_units))
            elif len(params_units) > len(params):
                params_units = params_units[: len(params)]

            if args.errory == True:
                y_error = subset[f"{args.y}Error"].values[0]
                plot_data(
                    args,
                    ax_top,
                    x,
                    y=y,
                    errory=y_error,
                    label=(
                        subset[args.iterable].iloc[0]
                        if args.iterable is not None
                        else f"Data"
                    ),
                    plot_type="errorbar",
                    fmt="o",
                )

            else:
                plot_data(
                    args,
                    ax_top,
                    x,
                    y=y,
                    plot_type="plot",
                    marker="o",
                    linestyle="None",
                    label=(
                        subset[args.iterable].iloc[0]
                        if args.iterable is not None
                        else f"Data"
                    ),
                )

            if (
                jdx == args.fitindex
            ):  # Only add legend for the first iterable to avoid duplicates

                # Draw the fit line
                fit_x = np.linspace(np.min(x), np.max(x), 1000)
                plot_data(
                    args,
                    ax_top,
                    fit_x,
                    y=func(fit_x, *params),
                    label="Fit",
                    color="red",
                    plot_type="plot",
                    linestyle="-",
                )

                # Compute residuals only for valid (finite, nonzero fit) points
                diff = y - fit
                mask = np.isfinite(fit) & (fit != 0) & np.isfinite(diff)
                residuals = np.full_like(diff, np.nan)
                residuals[mask] = diff[mask] / fit[mask]

                if args.errory and y_error is not None:
                    residuals_error = np.full_like(y, np.nan)
                    residuals_error[mask] = y_error[mask] / fit[mask]
                else:
                    residuals_error = None

                # Focus on central 90% of finite residuals for y-limits
                finite_res = residuals[mask]
                if finite_res.size > 0:
                    lower, upper = np.percentile(finite_res, [5, 95])
                    limit = (
                        max(abs(lower), abs(upper)) * 2
                    )  # Add some padding to the limits
                    if limit == 0 or not np.isfinite(limit):
                        limit = 1e-3
                else:
                    limit = 1

                # If limits are still dominated by outliers, set to a default small value to avoid an empty plot
                if limit > 1e3 or not np.isfinite(limit):
                    # Set limit to number of free parameters in the fit as a more reasonable default if the computed limit is unreasonably large or not finite
                    limit = len(params)

                if ax_bottom is not None:
                    # Plot residuals
                    if args.errory:
                        plot_data(
                            args,
                            ax_bottom,
                            x,
                            y=residuals,
                            errory=residuals_error,
                            color="black",
                            plot_type="errorbar",
                            fmt="o",
                        )
                    else:
                        plot_data(
                            args,
                            ax_bottom,
                            x,
                            y=residuals,
                            color="black",
                            plot_type="plot",
                            marker="o",
                            linestyle="None",
                        )
                    # Set the limits for the residuals plot based on the central 90% of finite residuals to avoid outliers dominating the scale
                    ax_bottom.set_ylim(-limit, limit)

                chi2 = (
                    (diff[mask] ** 2 / fit[mask]).sum() if fit[mask].size > 0 else 0
                )  # Avoid division by zero

                for ldx, (param_label, param_format, param, param_error, param_unit) in enumerate(
                    zip(params_labels, params_format, params, params_error, params_units)
                ):
                    unit_text = str(param_unit).strip()
                    param_display = param
                    param_error_display = param_error
                    if unit_text in {"%", "\\%"}:
                        param_display = param * 100
                        param_error_display = param_error * 100

                    unit_suffix = f" {unit_text}" if unit_text else ""
                    ax_top.text(
                        args.fitlegendposition[0],
                        args.fitlegendposition[1] - 0.08 - 0.06 * ldx,
                        r"{0} = {1:{2}} $\pm$ {3:{2}}{4}".format(
                            param_label,
                            param_display,
                            param_format,
                            param_error_display,
                            unit_suffix,
                        ),
                        fontdict={"size": legendfontsize},
                        transform=ax_top.transAxes,
                    )

                if args.chi2:
                    ax_top.text(
                        args.fitlegendposition[0],
                        args.fitlegendposition[1] - 0.08 - 0.06 * (len(params)),
                        r"$\chi^2$/ndof = {0:0.2f}/{1:d}".format(chi2, len(params)),
                        fontdict={"size": legendfontsize},
                        transform=ax_top.transAxes,
                    )

        if fit_function_label is None:
            rprint("[yellow]Warning:[/yellow] No valid fit entries available to plot.")
            plt.close(fig)
            continue

        ax_top.set_ylabel(
            resolve_axis_label(args.labely, args.y, df),
            fontsize=ysublabelfontsize,
        )

        if args.rangex is not None:
            ax_top.set_xlim(args.rangex)
        if args.rangey is not None:
            ax_top.set_ylim(args.rangey)
        if args.logy:
            ax_top.set_yscale("log")
        if args.logx:
            ax_top.set_xscale("log")

        ax_top.set_title(
            f"{fit_function_label} Fit",
            fontsize=subtitlefontsize,
        )
        ax_top.text(
            args.fitlegendposition[0],
            args.fitlegendposition[1],
            "Fit Parameters:",
            fontdict={"size": legendfontsize, "weight": "bold"},
            transform=ax_top.transAxes,
        )

        # Ensure the fit line appears last in the legend ordering.
        legend_handles, legend_labels = ax_top.get_legend_handles_labels()
        fit_indices = [
            idx for idx, label in enumerate(legend_labels) if str(label).strip() == "Fit"
        ]
        if fit_indices:
            fit_idx = fit_indices[0]
            fit_handle = legend_handles.pop(fit_idx)
            fit_label = legend_labels.pop(fit_idx)
            legend_handles.append(fit_handle)
            legend_labels.append(fit_label)

        apply_legend_style(
            ax_top,
            title=args.labelz if args.labelz is not None else None,
            handles=legend_handles,
            labels=legend_labels,
            capitalize_labels=not getattr(args, "no_capitalize_legend", False),
        )

        if ax_bottom is not None:
            ax_bottom.axhline(y=0, color="r", zorder=-1)
            if args.rangex is not None:
                ax_bottom.set_xlim(args.rangex)

            ax_bottom.set_xlabel(
                resolve_axis_label(args.labelx, args.x, df),
                fontsize=xlabelfontsize,
            )
            if args.logx:
                ax_bottom.set_xscale("log")

            ax_bottom.set_ylim(-limit, limit)
            ax_bottom.set_ylabel("(Data - Fit)/Fit", fontsize=ysublabelfontsize)
        else:
            ax_top.set_xlabel(
                resolve_axis_label(args.labelx, args.x, df),
                fontsize=xlabelfontsize,
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
        fig.suptitle(figure_title, fontsize=titlefontsize)

        # dunestyle.WIP()

        apply_note_to_figure(fig, getattr(args, "note", None))

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="fit.png")
        default_output_dir = os.path.join(
            os.path.dirname(__file__), "..", "output", "plots"
        )
        save_figure_to_paths(fig, args.output, output_file, default_output_dir, rprint)


if __name__ == "__main__":
    main()
