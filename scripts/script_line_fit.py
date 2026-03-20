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
from lib.exports import make_name_from_args
from lib.format import make_title_from_args, make_subtitle_from_args
from lib.imports import import_data, prepare_import
from lib.functions import (
    resolution,
    gaussian,
    correction_func,
    quadratic_cut,
    quadratic_function,
)
from lib.plot import plot_data

# Remove RuntimeWarning: overflow encountered in divide
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)

parser.add_argument(
    "--datafile",
    type=str,
    default="NHit_Distributions",
    help="Path to the input data file (pkl format)",
)

parser.add_argument(
    "--configs",
    nargs="+",
    type=str,
    default=None,
    help="DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)",
)

parser.add_argument(
    "--names",
    nargs="+",
    type=str,
    default=None,
    help="Name of the simulation configuration (e.g. marley_official, marley, etc.)",
)

parser.add_argument(
    "--variables",
    "-v",
    nargs="+",
    type=str,
    default=None,
    help="List of variable parameters to filter data (e.g. SignalParticleK, BackgroundType, etc.)",
)

parser.add_argument(
    "-x",
    type=str,
    default="Values",
    help="Column name for x-axis values",
),

parser.add_argument(
    "-y",
    type=str,
    default="Density",
    help="Column name for y-axis values",
),

parser.add_argument(
    "--iterable",
    "-i",
    type=str,
    default=None,
    help="List of iterable parameters to produce plots",
)

parser.add_argument(
    "--select",
    nargs="+",
    type=str,
    default=None,
    help="List of iterable parameters to produce plots",
)

parser.add_argument(
    "--save_values",
    "-s",
    nargs="+",
    default=None,
    help="If iterable value is provided, save plots for which iterable equals this value",
)

parser.add_argument(
    "--reduce",
    action="store_true",
    help="Reduce the number of plotted lines by only plotting every other line for cases with many unique iterables",
    default=False,
)

parser.add_argument(
    "--labelx",
    type=str,
    default=f"True Neutrino Energy (MeV)",
    help="Label for x-axis on plot",
)

parser.add_argument(
    "--labely",
    type=str,
    default=None,
    help="Label for y-axis on plot",
)

parser.add_argument(
    "--labelz",
    type=str,
    default=None,
    help="Title for legend on plot (if applicable)",
)

parser.add_argument(
    "--logx",
    action="store_true",
    help="Set x-axis to logarithmic scale",
    default=False,
)

parser.add_argument(
    "--logy",
    action="store_true",
    help="Set y-axis to logarithmic scale",
    default=False,
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
    "--rangex",
    nargs=2,
    type=float,
    default=None,
    help="Font size for legend",
)

parser.add_argument(
    "--rangey",
    nargs=2,
    type=float,
    default=None,
    help="Font size for legend",
)

parser.add_argument(
    "--title",
    type=str,
    default=None,
    help="Title for the plot",
)

parser.add_argument(
    "--output",
    "-o",
    type=str,
    default=None,
    help="Output filepath for the plot",
)

parser.add_argument(
    "--debug",
    "-d",
    action="store_true",
    help="Enable debug mode",
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
        fig = plt.figure(figsize=(8, 6))
        gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[3, 1], hspace=0)
        axs = gs.subplots(sharex=True)
        df_config = df[(df["Config"] == config) & (df["Name"] == name)]

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

            x = subset[args.x].values[0].astype(float)
            y = subset[args.y].values[0].astype(float)

            params = subset["Params"].iloc[0]
            params_format = subset["ParamsFormat"].iloc[0]
            params_labels = subset["ParamsLabels"].iloc[0]
            params_error = subset["ParamsError"].iloc[0]
            func = subset["FitFunction"].iloc[0]
            fit = func(x, *params)

            if args.errory == True:
                y_error = subset[f"{args.y}Error"].values[0]
                plot_data(
                    args,
                    axs[0],
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
                    axs[0],
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
                    axs[0],
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

                if args.errory:
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

                # Plot residuals
                if args.errory:
                    plot_data(
                        args,
                        axs[1],
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
                        axs[1],
                        x,
                        y=residuals,
                        color="black",
                        plot_type="plot",
                        marker="o",
                        linestyle="None",
                    )
                # Set the limits for the residuals plot based on the central 90% of finite residuals to avoid outliers dominating the scale
                axs[1].set_ylim(-limit, limit)

                chi2 = (
                    (diff[mask] ** 2 / fit[mask]).sum() if fit[mask].size > 0 else 0
                )  # Avoid division by zero

                for ldx, (param_label, param_format, param, param_error) in enumerate(
                    zip(params_labels, params_format, params, params_error)
                ):
                    axs[0].text(
                        args.fitlegendposition[0],
                        args.fitlegendposition[1] - 0.08 - 0.06 * ldx,
                        r"{0} = {1:{2}} $\pm$ {3:{2}}".format(
                            param_label, param, param_format, param_error
                        ),
                        fontdict={"size": legendfontsize},
                        transform=axs[0].transAxes,
                    )

                if args.chi2:
                    axs[0].text(
                        args.fitlegendposition[0],
                        args.fitlegendposition[1] - 0.08 - 0.06 * (len(params)),
                        r"$\chi^2$/ndof = {0:0.2f}/{1:d}".format(chi2, len(params)),
                        fontdict={"size": legendfontsize},
                        transform=axs[0].transAxes,
                    )

        axs[0].set_ylabel(
            args.labely if args.labely is not None else f"{args.y}",
            fontsize=ysublabelfontsize,
        )

        if args.rangex is not None:
            axs[0].set_xlim(args.rangex)
        if args.rangey is not None:
            axs[0].set_ylim(args.rangey)
        if args.logy:
            axs[0].set_yscale("log")
        if args.logx:
            axs[0].set_xscale("log")

        axs[0].set_title(
            f"{subset['FitFunctionLabel'].iloc[0]} Fit",
            fontsize=subtitlefontsize,
        )
        axs[0].text(
            args.fitlegendposition[0],
            args.fitlegendposition[1],
            "Fit Parameters:",
            fontdict={"size": legendfontsize, "weight": "bold"},
            transform=axs[0].transAxes,
        )
        axs[0].legend(
            fontsize=legendfontsize,
            title=args.labelz if args.labelz is not None else None,
            title_fontsize=legendtitlefontsize,
        )

        axs[1].axhline(y=0, color="r", zorder=-1)
        if args.rangex is not None:
            axs[1].set_xlim(args.rangex)

        axs[1].set_xlabel(
            args.labelx if args.labelx is not None else f"{args.x}",
            fontsize=xlabelfontsize,
        )
        if args.logx:
            axs[1].set_xscale("log")

        axs[1].set_ylim(-limit, limit)
        axs[1].set_ylabel("(Data - Fit)/Fit", fontsize=ysublabelfontsize)

        figure_title = make_title_from_args(args)
        fig.suptitle(figure_title, fontsize=titlefontsize)

        # dunestyle.WIP()

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="fit.png")
        if args.output is not None:
            output_dir = os.path.dirname(args.output)
            os.makedirs(output_dir, exist_ok=True)
            rprint(
                f"[green]Success:[/green] Plot saved to:\n{args.output}{output_file}"
            )
        else:
            output_dir = os.path.join(
                os.path.dirname(__file__), "..", "output", "plots"
            )
            os.makedirs(output_dir, exist_ok=True)
            rprint(
                f"[green]Success:[/green] Plot saved to:\n{os.path.join(output_dir.split('..')[1], output_file)[1:]}"
            )

        plt.savefig(os.path.join(output_dir, output_file))

        plt.close()


if __name__ == "__main__":
    main()
