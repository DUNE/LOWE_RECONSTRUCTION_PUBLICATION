
#!/usr/bin/env python3


"""
Script 4: Fit representation of a Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling and fit representation
"""

from lib import *
from lib.functions import resolution, gaussian, correction_func

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)
parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=["hd_1x2x6_centralAPA"],
    help='DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)',
)

parser.add_argument(
    '--name',
    nargs='+',
    type=str,
    default=None,
    help='Name of the simulation configuration (e.g. marley_official, marley, etc.)',
)

parser.add_argument(
    '--datafile',
    type=str,
    default="NHit_Distributions",
    help='Path to the input data file (pkl format)',
)

parser.add_argument(
    '--iterables', '-i',
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
    '--debug', "-d",
    action='store_true',
    help='Enable debug mode',
)

args = parser.parse_args()


def main():
    # For each configuration provided combine the data files and plot the results
    df = pd.DataFrame()
    for config, name in product(args.configs, args.name if args.name is not None else [None]):
        # Import data from pkl datafile
        if args.name is None:
            datafile = os.path.join(os.path.dirname(__file__), '..', 'data', f"{config}_{args.datafile}.pkl")
        else:
            datafile = os.path.join(os.path.dirname(__file__), '..', 'data', f"{config}_{name}_{args.datafile}.pkl")
        
        if not os.path.exists(datafile):
            print(f"Data file not found: {datafile}")
            continue
        
        with open(datafile, 'rb') as f:
            data = pickle.load(f)
        # Append to df
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    
    if df.empty:
        print("No data to plot. Exiting.")
        return

    if args.debug:
        print(df)
    

    # Select the entries in the dataframe with with name matching args.name and nake a plot for each iterable
    for config, name in product(args.configs, args.name):
        fig = plt.figure(figsize=(8,6))
        gs = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[3, 1], hspace=0)
        axs = gs.subplots(sharex=True)
        df_config = df[(df['Config'] == config) & (df['Name'] == name)]
        # Filter df_config according to each iterable and save_values
        subset = df_config[
            df_config[args.iterables].apply(
                lambda row: all(
                    (str(row[iterable]) == str(value)) if args.save_values is not None else True
                    for iterable, value in zip(args.iterables, args.save_values)
                ),
                axis=1
            )
        ]
 
        for idx in range(len(subset))[::-1]:
            if np.sum(subset[args.y].values[idx]) < 1:
                continue

            x = subset[args.x].values[idx]
            y = subset[args.y].values[idx]
            if args.errory == True:
                y_error = subset[f"{args.y}Error"].values[idx]
            else:
                y_error = None

            params = subset["Params"].iloc[idx]
            params_format = subset["ParamsFormat"].iloc[idx]
            params_labels = subset["ParamsLabels"].iloc[idx]
            params_error = subset["ParamsError"].iloc[idx]
            func = subset["FitFunction"].iloc[idx]
            fit = func(x, *params)

            diff =  y - fit
            # Find vlaues for which diff is sensible (i.e. not NaN or inf or bigger than 1e6)
            residuals = diff / fit
            if y_error is not None:
                residuals_error = y_error / fit
            jdx = np.where((~np.isnan(residuals)) & (np.isfinite(residuals)) & (np.abs(residuals) < 1e2))[0]
            chi2 = (diff[jdx]**2 / fit[jdx]).sum()

            if y_error is None:
                axs[0].plot(x, y, marker='o', linestyle='None', label="Data" if len(subset) == 1 else subset["Label"].iloc[idx])
            else:
                axs[0].errorbar(x, y, yerr=y_error, fmt='o', label="Data" if len(subset) == 1 else subset["Label"].iloc[idx])

            if idx == len(subset)-1:
                # Draw the fit line
                axs[0].plot(np.linspace(np.min(x), np.max(x), 1000), func(np.linspace(np.min(x), np.max(x), 1000), *params), label="Fit", color='red')
                axs[0].set_ylabel(args.labely if args.labely is not None else f"{args.y}", fontsize=14)
                if args.rangex is not None:
                    axs[0].set_xlim(args.rangex)
                if args.rangey is not None:
                    axs[0].set_ylim(args.rangey)
                if args.logy:
                    axs[0].set_yscale('log')
                if args.logx:
                    axs[0].set_xscale('log')

                axs[0].set_title(f"{args.datafile.replace('_',' ')} Fit - {config}", fontsize=18)
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
                axs[1].set_ylabel("(Data - Fit)/Fit", fontsize=ylabelfontsize)
                
                if args.rangex is not None:
                    axs[1].set_xlim(args.rangex)

                if np.max(np.abs(residuals[jdx])) < 0.99:
                    axs[1].set_ylim(-0.99,0.99)
                
                else:
                    axs[1].set_ylim(0.1, np.max(residuals[jdx]))
                    axs[1].set_yscale('log')
        
        # dunestyle.WIP()
        axs[0].legend(fontsize=legendfontsize)

        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        output_file = ""
        if config is not None:
            output_file += f"{config.lower()}"
        if name is not None:
            output_file += f"_{name.lower()}"
        if args.iterables is not None:
            for iterable, value in zip(args.iterables, args.save_values):
                output_file += f"_{str(value).lower()}{iterable.lower()}"
        output_file = f"{output_file}_fit.png".replace('#','n')
        plt.savefig(os.path.join(output_dir, output_file))
        
        print(f"Plot saved to {os.path.join(output_dir, output_file)}")
        plt.close()

if __name__ == '__main__':
    main()