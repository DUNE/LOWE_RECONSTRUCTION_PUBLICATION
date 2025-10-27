
#!/usr/bin/env python3


"""
Script 6: Combined Line Plot with DUNE Style
Demonstrates combined data plotting with custom styling
"""
# Import config from __init__.py
from lib import *

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)
parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=["vd_1x8x14_3view_30deg_nominal", "hd_1x2x6_lateralAPA"],
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
    default="AdjCluster_Distributions",
    help='Path to the input data file (pkl format)',
)

parser.add_argument(
    '--iterables',
    nargs='+',
    type=str,
    default=['Signal'],
    help='List of iterable parameters to produce plots',
)

parser.add_argument(
    '--variables', '-v',
    nargs='+',
    type=str,
    default=["AdjClEnergy", "AdjClMainE"],
    help='Row filter variable name',
)

parser.add_argument(
    '-x',
    type=str,
    default="Values",
    help='Column name for x-axis values',
)

parser.add_argument(
    '--logx',
    action='store_true',
    help='Set x-axis to logarithmic scale',
)

parser.add_argument(
    '-y',
    type=str,
    default="Count",
    help='Column name for y-axis values',
),

parser.add_argument(
    '--logy',
    action='store_true',
    help='Set y-axis to logarithmic scale',
)

parser.add_argument(
    '--labely',
    type=str,
    default="Counts per Event",
    help='Label for y-axis on plot',
)

parser.add_argument(
    '--debug',
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
    for idx, (variable, iterable) in enumerate(product(args.variables, args.iterables)):
        df_var = df[df["Variable"] == variable] 
        plt.figure()
        unique_values = df_var[iterable].unique()
        for (jdx, config), (kdx, value) in product(enumerate(args.configs), enumerate(sorted(unique_values))):
            subset = df_var[(df_var[iterable] == value) & (df_var['Config'] == config)]
            subset = subset.explode(column=[args.x, args.y])
            label = "HD Lateral" if config == "hd_1x2x6_lateralAPA" else "VD" if config == "vd_1x8x14_3view_30deg_nominal" else config
            plt.hist(subset[args.x], 
                    bins=len(subset[args.x].unique()),
                    weights=subset[args.y],
                    histtype='step',
                    label=f"{label}, {value}",
                    color=f'C{jdx}',
                    ls='-' if kdx == 0 else '--' if kdx == 1 else ':'
                    )
        
        plt.xlabel("Reconstructed Cluster Energy (MeV)" if variable == "AdjClEnergy" else "True Particle Energy (MeV)" if variable == "AdjClMainE" else variable)
        plt.ylabel(args.labely)
        if args.logy:
            plt.yscale('log')
        if args.logx:
            plt.xscale('log')
        
        plt.legend()
        plt.title(f"Adjacent Cluster Distribution", fontsize=18)
        # dunestyle.WIP()
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{args.name.lower()}_{variable.lower()}.png")
        plt.savefig(output_file)
        
        print(f"Plot saved to {output_file}")
        plt.close()

if __name__ == '__main__':
    main()