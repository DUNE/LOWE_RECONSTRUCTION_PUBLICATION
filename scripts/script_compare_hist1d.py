
#!/usr/bin/env python3


"""
Script 3: Simple Histogram Plot with DUNE Style
Demonstrates basic plotting with custom styling
"""

from lib import *

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the charge over time distribution of the particles"
)
parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=["hd_1x2x6_centralAPA"],
    help='DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)',
)

parser.add_argument(
    '--names', '-n',
    nargs='+',
    type=str,
    default=['marley_official'],
    help='Name of the simulation configuration (e.g. marley_official, marley, etc.)',
)

parser.add_argument(
    '--datafile',
    type=str,
    default="Charge_Lifetime_Correction",
    help='Path to the input data file (pkl format)',
)

parser.add_argument(
    '-x',
    type=str,
    default="TrueEnergy",
    help='Column name for x-axis data',
)

parser.add_argument(
    '-y',
    type=str,
    default=None,
    help='Column name for y-axis data',
)

parser.add_argument(
    '--percentile', '-p',
    nargs='+',
    type=float,
    default=[1, 99],
    help='Percentile range for axis limits (e.g. 1 99)',
)

parser.add_argument(
    '--operation',
    type=str,
    default="subtract",
    help='Operation to perform on data (e.g. mean, sum, etc.)',
)

parser.add_argument(
    '--iterables', '-i',
    nargs='+',
    type=str,
    default=[],
    help='List of iterable parameters to produce plots',
)

parser.add_argument(
    '--save_values', '-s',
    nargs='+',
    type=int,
    default=[3],
    help='If iterable value is provided, save plots for which iterable equals this value',
)

parser.add_argument(
    '--comparable', '-c',
    type=str,
    default='Corrected',
    help='Column name for comparable data',
)

parser.add_argument(
    '--labelx',
    type=str,
    default=r"Time ($\mu$s)",
    help='Label for x-axis on plot',
)

parser.add_argument(
    '--labely',
    type=str,
    default="Density",
    help='Label for y-axis on plot',
    choices=['Counts', 'Density'],
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
    for config, name in product(args.configs, args.names):
        # Import data from pkl datafile
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

    # Select the entries in the dataframe with name matching args.name and make a plot for each iterable
    if args.iterables is None or len(args.iterables) == 0:
        args.iterables = [""]
        df [""] = None  # Dummy iterable column
    
    for config, name, iterable in product(args.configs, args.names, args.iterables):
        for jdx, value in enumerate(df[iterable].unique()):
            if len(args.iterables) > 0 and value not in args.save_values and iterable != "":
                continue

            plt.figure()
            ax = plt.axes()
            hist_range = []
            for idx, compare in enumerate(df[args.comparable].unique()):
                df_iter = df[(df[args.comparable] == compare) & (df['Config'] == config) & (df['Name'] == name)]
                if iterable != "":
                    df_iter = df_iter[df_iter[iterable] == value]

                x = np.array(df_iter[args.x].values[0])  # Convert to NumPy array
                if args.y is None:
                    data = x
                else:
                    y = np.array(df_iter[args.y].values[0])  # Convert to NumPy array
                    if args.operation == "mean":
                        data = np.mean(x, y)
                    elif args.operation == "subtract":
                        data = np.subtract(x, y)
                    elif args.operation == "sum":
                        data = np.sum(x, y)
                    elif args.operation == "rms":
                        data = np.sqrt(np.mean(np.square(x), np.square(y)))

                if hist_range == []:
                    hist_range = [np.percentile(data, args.percentile[0]), np.percentile(data, args.percentile[1])]
                
                plt.hist(data, histtype='step', label=f"{compare}", bins=100, range=hist_range, density=(args.labely == "Density"))

            if args.logx:
                ax.set_xscale('log')
            else:
                ax.set_xlim(hist_range)

            if args.logy:
                ax.set_yscale('log')

            plt.legend(title=args.comparable, title_fontsize=14, fontsize=12)
            plt.xlabel(args.labelx)
            plt.ylabel(args.labely)
            # Set title
            plt.title(f"Distribution - {config}", fontsize=18)
            # dunestyle.WIP()
            
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{config.lower()}_{name.lower()}_{args.datafile.lower()}_{iterable.lower()}{value}_hist1d.png")
            plt.savefig(output_file)
            
            print(f"Plot saved to {output_file}")
            plt.close()

if __name__ == '__main__':
    main()