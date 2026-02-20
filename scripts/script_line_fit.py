
#!/usr/bin/env python3

"""
Script 4: Fit representation of a Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling and fit representation
"""

import warnings

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args
from lib.imports import import_data, prepare_import
from lib.functions import resolution, gaussian, correction_func

# Remove RuntimeWarning: overflow encountered in divide
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)

parser.add_argument(
    '--datafile',
    type=str,
    default="NHit_Distributions",
    help='Path to the input data file (pkl format)',
)

parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=None,
    help='DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)',
)

parser.add_argument(
    '--names',
    nargs='+',
    type=str,
    default=None,
    help='Name of the simulation configuration (e.g. marley_official, marley, etc.)',
)

parser.add_argument(
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='List of variable parameters to filter data (e.g. SignalParticleK, BackgroundType, etc.)',
)

parser.add_argument(
    '-x',
    type=str,
    default="Values",
    help='Column name for x-axis values',
),

parser.add_argument(
    '-y',
    type=str,
    default="Density",
    help='Column name for y-axis values',
),

parser.add_argument(
    '--iterable', '-i',
    type=str,
    default=None,
    help='List of iterable parameters to produce plots',
)

parser.add_argument(
    '--select',
    nargs='+',
    type=str,
    default=None,
    help='List of iterable parameters to produce plots',
)

parser.add_argument(
    '--save_values', '-s',
    nargs='+',
    default=None,
    help='If iterable value is provided, save plots for which iterable equals this value',
)

parser.add_argument(
    '--labelx',
    type=str,
    default=f"True Neutrino Energy (MeV)",
    help='Label for x-axis on plot',
)

parser.add_argument(
    '--labely',
    type=str,
    default=None,
    help='Label for y-axis on plot',
)

parser.add_argument(
    '--logx',
    action='store_true',
    help='Set x-axis to logarithmic scale',
    default=False,
)

parser.add_argument(
    '--logy',
    action='store_true',
    help='Set y-axis to logarithmic scale',
    default=False,
)

parser.add_argument(
    '--chi2',
    action='store_true',
    help='Display chi2 on the plot',
    default=False,
)

parser.add_argument(
    '--fitlegendposition',
    type=tuple,
    help='Position of the fit legend on the plot as (x,y) coordinates in axes fraction',
    default=(0.60, 0.90),
)

parser.add_argument(
    '--errorx',
    action='store_true',
    help='Set x-axis to show error bars',
    default=False,
)

parser.add_argument(
    '--errory',
    action='store_true',
    help='Set y-axis to show error bars',
    default=False,
)

parser.add_argument(
    '--rangex',
    nargs=2,
    type=int,
    default=None,
    help='Font size for legend',
)

parser.add_argument(
    '--rangey',
    nargs=2,
    type=int,
    default=None,
    help='Font size for legend',
)

parser.add_argument(
    '--output', '-o',
    type=str,
    default=None,
    help='Output filepath for the plot',
)

parser.add_argument(
    '--debug', "-d",
    action='store_true',
    help='Enable debug mode',
)

args = parser.parse_args()


def main():
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    if args.variables is not None and args.iterable is not None:
        rprint("Both variables and iterable arguments provided. Please provide only one of them.")
        return
    
    ncols = len(args.variables) if args.variables is not None else len(df[args.iterable].unique()) if args.iterable is not None else 1
    
    rprint(f"Number of unique variables for plotting: {ncols}")

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    # Select the entries in the dataframe with with name matching args.name and nake a plot for each iterable
    for kdx, (config, name) in enumerate(zip(configs, names)):
        fig = plt.figure(figsize=(8,6))
        gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[3, 1], hspace=0)
        axs = gs.subplots(sharex=True)
        df_config = df[(df['Config'] == config) & (df['Name'] == name)]
        
        variables = args.variables if args.variables is not None else [None]
        iterables = df_config[args.iterable].unique() if args.iterable is not None else [None]
        
        for (jdx, variable), (idx, iterable) in product(enumerate(variables), enumerate(iterables) if args.iterable is not None else enumerate([None])):
            rprint(f"[blue]Info:[/blue] Processing variable: {variable}, iterable: {iterable}")

            # Filter the DataFrame based on the current variable and iterable
            if variable is not None and iterable is not None:
                # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}")
                df_iterable = df_config[(df_config["Variable"] == variable) & (df_config[args.iterable] == iterable)]
            
            elif variable is not None and iterable is None:
                # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable}")
                df_iterable = df_config[(df_config["Variable"] == variable)]

            elif iterable is not None and variable is None:
                # rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
                df_iterable = df_config[(df_config[args.iterable] == iterable)]
            
            else:
                df_iterable = df_config.copy()
            
            subset = filter_dataframe(df_iterable, args)

            x = subset[args.x].values[0]
            y = subset[args.y].values[0]
            if args.errory == True:
                y_error = subset[f"{args.y}Error"].values[0]
            else:
                y_error = None

            params = subset["Params"].iloc[0]
            params_format = subset["ParamsFormat"].iloc[0]
            params_labels = subset["ParamsLabels"].iloc[0]
            params_error = subset["ParamsError"].iloc[0]
            func = subset["FitFunction"].iloc[0]
            fit = func(x, *params)

            diff =  y - fit
            # Find values for which diff is sensible (i.e. not NaN or inf or bigger than 1e6)
            jdx = np.where((~np.isnan(fit)) & (np.isfinite(fit)) & (fit != 0))[0]  # Ensure fit is not zero and not too large
            residuals = np.zeros_like(diff)  # Initialize residuals
            if fit[jdx].size > 0:  # Check if there are valid fit values
                residuals[jdx] = diff[jdx] / fit[jdx]  # Calculate residuals only for valid indices
            
            if y_error is not None:
                residuals_error = np.zeros_like(y_error)  # Initialize residuals_error
                if fit[jdx].size > 0:  # Check if there are valid fit values
                    residuals_error[jdx] = y_error[jdx] / fit[jdx]  # Calculate residuals_error only for valid indices
            chi2 = (diff[jdx]**2 / fit[jdx]).sum() if fit[jdx].size > 0 else 0  # Avoid division by zero

            if y_error is None:
                axs[0].plot(x, y, marker='o', linestyle='None', label=subset[args.iterable].iloc[0] if args.iterable is not None else f"Data")
            else:
                axs[0].errorbar(x, y, yerr=y_error, fmt='o', label=subset[args.iterable].iloc[0] if args.iterable is not None else f"Data")

            if idx == (len(df[args.iterable].unique()) if args.iterable is not None else 1) - 1:
                axs[0].legend(fontsize=legendfontsize)
                # Draw the fit line
                axs[0].plot(np.linspace(np.min(x), np.max(x), 1000), func(np.linspace(np.min(x), np.max(x), 1000), *params), label="Fit", color='red')
                axs[0].set_ylabel(args.labely if args.labely is not None else f"{args.y}", fontsize=ysublabelfontsize)
                if args.rangex is not None:
                    axs[0].set_xlim(args.rangex)
                if args.rangey is not None:
                    axs[0].set_ylim(args.rangey)
                if args.logy:
                    axs[0].set_yscale('log')
                if args.logx:
                    axs[0].set_xscale('log')

                axs[0].set_title(f"{subset['FitFunctionLabel'].iloc[0]} Fit", fontsize=subtitlefontsize)
                axs[0].text(args.fitlegendposition[0], args.fitlegendposition[1], 'Fit Parameters:',
                    fontdict={'size': legendfontsize, 'weight': 'bold'},
                    transform=axs[0].transAxes)
                
                for idx, (param_label, param_format, param, param_error) in enumerate(zip(params_labels, params_format, params, params_error)):
                    axs[0].text(args.fitlegendposition[0], args.fitlegendposition[1] - 0.08 - 0.06*idx, r'{0} = {1:{2}} $\pm$ {3:{2}}'.format(param_label, param, param_format, param_error),
                        fontdict={"size": legendfontsize},
                        transform=axs[0].transAxes)
                
                if args.chi2:
                    axs[0].text(args.fitlegendposition[0], args.fitlegendposition[1] - 0.08 - 0.06*(idx+1), r'$\chi^2$/ndof = {0:0.2f}/{1:d}'.format(chi2, len(params)),
                        fontdict={"size": legendfontsize},
                        transform=axs[0].transAxes)

                # Bottom plot: residuals
                if y_error is None:
                    axs[1].plot(x[jdx], residuals[jdx], marker='o', linestyle='None', color='black')
                else:
                    axs[1].errorbar(x[jdx], residuals[jdx], yerr=residuals_error[jdx], fmt='o', color='black')
                
                axs[1].axhline(y=0, color="r", zorder=-1)
                axs[1].set_xlabel(args.labelx if args.labelx is not None else f"{args.x}", fontsize=xlabelfontsize)
                axs[1].set_ylabel("(Data - Fit)/Fit", fontsize=ysublabelfontsize)
                
                if args.rangex is not None:
                    axs[1].set_xlim(args.rangex)

                if np.max(np.abs(residuals[jdx])) < 0.99:
                    axs[1].set_ylim(-0.99, 0.99)
                else:
                    q1 = np.percentile(residuals[jdx], 25)
                    q3 = np.percentile(residuals[jdx], 75)
                    iqr = q3 - q1
                    upper_limit = q3 + 1.5 * iqr
                    lower_limit = q1 - 1.5 * iqr
                    limit = max(abs(upper_limit), abs(lower_limit))
                    if np.isfinite(limit):  # Check if limit is finite
                        axs[1].set_ylim(-limit, limit)   
                    else:
                        axs[1].set_ylim(-1, 1)
                
                if args.logx:
                    axs[1].set_xscale('log')

        figure_title = f"{args.datafile.replace('_', ' ')} Fit"
        if args.iterable is not None:
            figure_title += f" {args.iterable} Scan"
        figure_title += f" - {config}" if config is not None else ""
        
        fig.suptitle(figure_title, fontsize=titlefontsize)
        
        # dunestyle.WIP()
            
        output_file = make_name_from_args(args, kdx, prefix=None, suffix="fit.png")
        if args.output is not None:
            output_dir = os.path.dirname(args.output)
            os.makedirs(output_dir, exist_ok=True)
            rprint(f"[green]Success:[/green] Plot saved to:\n{args.output}{output_file}")
        else:  
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
            os.makedirs(output_dir, exist_ok=True)
            rprint(f"[green]Success:[/green] Plot saved to:\n{os.path.join(output_dir.split('..')[1], output_file)}")
        
        plt.savefig(os.path.join(output_dir, output_file)) 
        
        plt.close()

if __name__ == '__main__':
    main()