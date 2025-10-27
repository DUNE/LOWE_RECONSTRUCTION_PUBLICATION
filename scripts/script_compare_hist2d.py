
#!/usr/bin/env python3


"""
Script 4: Simple Heatmap Plot with DUNE Style
Demonstrates basic heatmap plotting with custom styling
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
    default="Time",
    help='Column name for x-axis data',
)

parser.add_argument(
    '-y',
    type=str,
    default="ChargePerEnergy",
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
    default="Charge per Energy (ADC x tick / MeV)",
    help='Label for y-axis on plot',
)

parser.add_argument(
    '--logz',
    action='store_true',
    help='Set z-axis to logarithmic scale',
    default=False,
)

parser.add_argument(
    '--diagonal',
    action='store_true',
    help='Draw diagonal line',
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
            
            ranges = []
            fig, ax = plt.subplots(nrows=1, ncols=len(df[args.comparable].unique()), figsize=(6 * len(df[args.comparable].unique()), 5), constrained_layout=True)
            for idx, compare in enumerate(df[args.comparable].unique()):
                df_iter = df[(df[args.comparable] == compare) & (df['Config'] == config) & (df['Name'] == name)]
                if iterable != "":
                    df_iter = df_iter[df_iter[iterable] == value]

                x = np.array(df_iter[args.x].values[0])  # Convert to NumPy array
                y = np.array(df_iter[args.y].values[0])  # Convert to NumPy array
                
                x_range = [np.percentile(x, args.percentile[0]), np.percentile(x, args.percentile[1])]
                y_range = [np.percentile(y, args.percentile[0]), np.percentile(y, args.percentile[1])]
                if idx == 0:
                    ranges = [x_range, y_range]
                else:
                    if x_range[0] > ranges[0][0]:
                        ranges[0][0] = x_range[0]
                    if x_range[1] < ranges[0][1]:
                        ranges[0][1] = x_range[1]
                    if y_range[0] > ranges[1][0]:
                        ranges[1][0] = y_range[0]
                    if y_range[1] < ranges[1][1]:
                        ranges[1][1] = y_range[1]
                
                hist2d = ax[idx].hist2d(
                    x, y,
                    bins=100,
                    range=(x_range, y_range),
                    norm=LogNorm() if args.logz else None,
                    density=True,
                )
                if args.diagonal:
                    ax[idx].plot(ranges[1], ranges[1], color='k' if args.logz else 'white', linestyle='--')

            cbar = fig.colorbar(hist2d[3], ax=ax)
            cbar.set_label('Density' if not args.logz else 'Density (log scale)')
            cbar.ax.yaxis.set_label_position('right')  # Move label to the left
            for idx, compare in enumerate(df[args.comparable].unique()):
                ax[idx].set_xlabel(args.labelx)
                ax[idx].set_ylabel(args.labely) if idx == 0 else None
                ax[idx].set_title(f"{args.comparable}: {compare}", fontsize=14)
                ax[idx].set_xlim(ranges[0])
                ax[idx].set_ylim(ranges[1])

            # Set title
            fig.suptitle(f"Charge Lifetime Correction - {config}", fontsize=18)
            # dunestyle.WIP()
            
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{config.lower()}_{name.lower()}_{args.datafile.lower()}_{iterable.lower()}{value}_hist2d.png")
            plt.savefig(output_file)
            
            print(f"Plot saved to {output_file}")
            plt.close()

if __name__ == '__main__':
    main()