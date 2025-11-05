
#!/usr/bin/env python3


"""
Script 1: Simple Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling
"""

from lib import *

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
    '--iterables',
    nargs='+',
    type=str,
    default=['#Hits'],
    help='List of iterable parameters to produce plots',
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
    '--debug', "-d",
    action='store_true',
    help='Enable debug mode',
)

args = parser.parse_args()


def main():
    # For each configuration provided combine the data files and plot the results
    df = pd.DataFrame()
    for config in args.configs:
        # Import data from pkl datafile
        if args.name is None:
            datafile = os.path.join(os.path.dirname(__file__), '..', 'data', f"{config}_{args.datafile}.pkl")
        else:
            datafile = os.path.join(os.path.dirname(__file__), '..', 'data', f"{config}_{args.name}_{args.datafile}.pkl")
        
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


    if args.iterables is None or len(args.iterables) == 0:
        args.iterables = ["Iterable"]
        df["Iterable"] = None  # Dummy iterable column
    
    if args.variables is None:
        args.variables = [None]
        df["Variable"] = None  # Dummy iterable column
    # Select the entries in the dataframe with with name matching args.name and nake a plot for each iterable
    ncols = len(df["Variable"].unique())
    for config, iterable in product(args.configs, args.iterables):
        fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(len(df["Variable"].unique())-1), 6), constrained_layout=ncols > 1)
        df_config = df[(df['Config'] == config)]

        for (idx, variable), value in product(enumerate(args.variables), df_config[iterable].unique()):
            if value is None:
                continue
            
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx]
            
            subset = df_config[df_config[iterable] == value]
            if variable is not None:
                subset = subset[(subset["Variable"] == variable)]
            subset = subset.explode(column=[args.x, args.y])
            x = subset[args.x].astype(float)
            x_error = subset[f"Error"].astype(float) if f"Error" in subset.columns else None
            y = subset[args.y].astype(float)
            if x_error is not None:
                ax_current.errorbar(x, y, yerr=x_error, fmt='o', label=f"{value} Error" if idx == ncols -1 else None)
            else:
                ax_current.hist(x, bins=len(x), weights=y, histtype='step', label=f"{value}" if idx == ncols -1 else None)
        
        for idx, variable in enumerate(args.variables):
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx]
            ax_current.set_title(f"Variable: {variable}" if variable is not None else None, fontsize=14)
            ax_current.set_xlabel(args.labelx if args.labelx is not None else f"{args.x}")
            ax_current.set_ylabel(args.labely if args.labely is not None else f"{args.y}") if idx == 0 else None
            if args.logy:
                ax_current.semilogy()
            if args.logx:
                ax_current.semilogx()
            ax_current.legend(title=iterable, title_fontsize=14, fontsize=12) if idx == ncols - 1 else None


        fig.suptitle(f"{iterable} Scan - {config}", fontsize=18)
        # dunestyle.WIP()
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        output_file = ""
        if config is not None:
            output_file += f"{config.lower()}"
        if args.name is not None:
            output_file += f"_{args.name.lower()}"
        if variable is not None:
            output_file += f"_{variable.lower()}"
        if iterable != "Iterable":
            output_file += f"_{iterable.lower().replace('#','n')}_scan.png"

        plt.savefig(os.path.join(output_dir, output_file))
        
        print(f"Plot saved to {os.path.join(output_dir, output_file)}")
        plt.close()

if __name__ == '__main__':
    main()