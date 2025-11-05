
#!/usr/bin/env python3


"""
Script 5: Simple Line Plot with DUNE Style
Demonstrates basic df column plotting with custom styling
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
    default='marley_official',
    help='Name of the simulation configuration (e.g. marley_official, marley, etc.)',
)

parser.add_argument(
    '--datafile',
    type=str,
    default="Clustering_Efficiency",
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
    type=str,
    default=["Purity", "Completeness"],
    help='Column name for x-axis values',
)

parser.add_argument(
    '--logx',
    action='store_true',
    help='Set x-axis to logarithmic scale',
    default=False,
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
    default="Counts",
    help='Column name for y-axis values',
),

parser.add_argument(
    '--labely',
    type=str,
    default="Density",
    help='Label for y-axis on plot',
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

    # Select the entries in the dataframe with with name matching args.name and nake a plot for each iterable
    for config, variable, iterable in product(args.configs, args.variables, args.iterables):
        df_config = df[(df['Config'] == config) & (df["Variable"] == variable)]
        plt.figure(figsize=(8, 6))
        unique_values = df_config[iterable].unique()
        for value in sorted(unique_values):
            subset = df_config[df_config[iterable] == value]
            subset = subset.explode(column=[args.x, args.y])
            plt.hist(subset[args.x], bins=len(subset[args.x].unique()), weights=subset[args.y], histtype='step', label=f"{value}")
        
        plt.xlabel(f"Cluster {variable} (%)")
        plt.ylabel(args.labely)
        if args.logy:
            plt.yscale('log')
        if args.logx:
            plt.xscale('log')
        
        plt.legend(title=iterable, title_fontsize=14, fontsize=12)
        plt.title(f"Cluster Distribution - {config}", fontsize=18)
        # dunestyle.WIP()
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{config.lower()}_{args.name.lower()}_{variable.lower()}.png")
        plt.savefig(output_file)
        
        print(f"Plot saved to {output_file}")
        plt.close()

if __name__ == '__main__':
    main()