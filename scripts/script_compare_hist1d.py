
#!/usr/bin/env python3


"""
Script 2: Simple Histogram Plot with DUNE Style
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
    default=None,
    help='Path to the input data file (pkl format)',
    required=True,
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
    '--operation', '-o',
    type=str,
    default="subtract",
    help='Operation to perform on data (e.g. mean, sum, etc.)',
)

parser.add_argument(
    '--reduce',
    action='store_true',
    help='Reduce number of lines plotted for clarity',
    default=False,
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
    '--comparable', '-c',
    type=str,
    default=None,
    help='Column name for comparable data',
)

parser.add_argument(
    '--bins', '-b',
    type=int,
    default=nbins,
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
    if args.datafile is None:
        print("Error: --datafile argument is required.")
        return
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
        args.iterables = ["Iterable"]
        df["Iterable"] = None  # Dummy iterable column
    if args.comparable is None:
        args.comparable = "Comparable"
        df["Comparable"] = None  # Dummy iterable column
    
    for config, name, iterable in product(args.configs, args.names, args.iterables):
        for jdx, value in enumerate(df[iterable].unique()):
            if args.iterables == ["Iterable"]:
                pass
            else:
                if args.save_values is None and value is not None and ~np.isnan(float(value)):
                    print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since --save_values not provided")
                    continue
                elif args.save_values is not None and str(value) not in args.save_values:
                    print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since not in --save_values {args.save_values}")
                    continue
                else:
                    pass
            
            plt.figure(figsize=(8, 6))
            ax = plt.axes()
            hist_range = []
            for idx, compare in enumerate(df[args.comparable].unique()):
                if len(df[args.comparable].unique()) > 8 and args.reduce:
                    if idx % 2 == 1:
                        print(f"Skipping plotting for {args.comparable}={compare} to avoid overcrowding")
                        continue

                df_iter = df[(df['Config'] == config) & (df['Name'] == name)]
                if iterable != "Iterable":
                    if args.save_values is None:
                        df_iter = df_iter[df_iter[iterable].isna()]
                    else:
                        df_iter[iterable] = df_iter[iterable].astype(str)
                        if args.debug:
                            print(f"Filtering for {iterable} == {value}")
                        df_iter = df_iter[df_iter[iterable] == str(value)]
                if args.comparable != "Comparable":
                    df_iter[args.comparable] = df_iter[args.comparable].astype(str)
                    if args.debug:
                        print(f"Filtering for {args.comparable} == {compare}")
                    df_iter = df_iter[df_iter[args.comparable] == str(compare)]
                
                if len(df_iter) == 0:
                    print(f"No data for {compare} in {config} {name} {iterable}={value}, skipping.")
                    continue
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
                
                plt.hist(data, histtype='step', label=f"{compare}" if args.comparable != "Comparable" else f"{iterable}" if args.comparable != "Iterable" else None, bins=args.bins, range=hist_range, density=(args.labely == "Density"))

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
            plt.title(f"{iterable}: {value} - {config}" if args.iterables != ["Iterable"] else f"{args.comparable} Distribution - {config}", fontsize=18)
            # dunestyle.WIP()
            
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{config.lower()}_{name.lower()}_{args.datafile.lower()}_{iterable.lower().replace('#','n')}{value}_hist1d.png")
            plt.savefig(output_file)
            
            print(f"Plot saved to {output_file}")
            plt.close()

if __name__ == '__main__':
    main()