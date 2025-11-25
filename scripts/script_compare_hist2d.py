
#!/usr/bin/env python3


"""
Script 3: Simple Heatmap Plot with DUNE Style
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
    default=None,
    help='Path to the input data file (pkl format)',
    required=True,
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
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='List of variable parameters to filter data (e.g. SignalParticleK, BackgroundType, etc.)',
)

parser.add_argument(
    '--comparable', '-c',
    type=str,
    default=None,
    help='Column name for comparable data',
)

parser.add_argument(
    '--entry', '-e',
    type=int,
    default=None,
    help='Entry in df to plot in case multiple entries exist',
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
    default=None,
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
    '--zoom',
    action='store_true',
    help='Zoom into overlapping percentile ranges',
    default=False,
)

parser.add_argument(
    '--matchx',
    action='store_true',
    help='Match x-axis ranges across subplots',
    default=False,
)

parser.add_argument(
    '--matchy',
    action='store_true',
    help='Match y-axis ranges across subplots',
    default=False,
)

parser.add_argument(
    '--horizontal',
    type=float,
    default=None,
    help='Draw horizontal line at specified y value',
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

    if args.variables is None:
        args.variables = [None]
        if "Variable" not in df.columns:
            df["Variable"] = None  # Dummy iterable column
    
    if args.comparable is None:
        args.comparable = "Comparable"
        df["Comparable"] = None  # Dummy iterable column
    
    
    for config, name, iterable, variable in product(args.configs, args.names, args.iterables, args.variables):
        for jdx, value in enumerate(df[iterable].unique()):
            if args.iterables == ["Iterable"]:
                print("Skipping dummy iterable column")
                pass
            
            else:
                if isinstance(value, int) or isinstance(value, np.integer):
                    if args.save_values is None and value != None and value != -1:
                        print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since --save_values not provided")
                        continue
                    elif args.save_values != None and str(value) not in args.save_values:
                        print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since not in --save_values {args.save_values}")
                        continue
                    else:
                        pass
                
                elif isinstance(value, float):
                    if args.save_values is None and value != None and ~np.isnan(float(value)):
                        print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since --save_values not provided")
                        continue
                    elif args.save_values != None and str(value) not in args.save_values:
                        print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since not in --save_values {args.save_values}")
                        continue
                    else:
                        pass

                elif isinstance(value, str):
                    if args.save_values is None and value != None and value.lower() != "nan":
                        print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since --save_values not provided")
                        continue
                    elif args.save_values != None and str(value) not in args.save_values:
                        print(f"Skipping value {value} ({type(value)}) for iterable {iterable} since not in --save_values {args.save_values}")
                        continue
                    else:
                        pass
                
                else:
                    print(f"Unknown type {type(value)} for iterable {iterable}. Proceeding without filtering.")
                    pass
            
            ranges = []
            ncols = len(df[args.comparable].unique())
            fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
            for idx, compare in enumerate(df[args.comparable].unique()):
                df_iter = df[(df['Config'] == config) & (df['Name'] == name)]
                # Convert df_iter[iterable] to string for comparison
                if iterable != "Iterable":
                    if args.save_values is None:
                        df_iter = df_iter[df_iter[iterable].isna()]
                    else:
                        df_iter[iterable] = df_iter[iterable].astype(str)
                        if args.debug:
                            print(f"Filtering for {iterable} == {value}")
                        df_iter = df_iter[df_iter[iterable] == str(value)]
                
                if args.comparable != "Comparable":
                    df_iter = df_iter[df_iter[args.comparable] == compare]

                if variable is not None:
                    df_iter = df_iter[(df_iter["Variable"] == variable)]

                if args.debug:
                    print(f"Plotting for {iterable}={value}, {args.comparable}={compare}, config={config}, name={name}, entries={len(df_iter)}")
                
                if len(df_iter[args.x].values) > 1 and args.entry is None:
                    print(f"Warning: Multiple entries found for {iterable}={value}, {args.comparable}={compare}. Using the first entry.")                
                    x = np.array(df_iter[args.x].values[0])  # Convert to NumPy array
                    y = np.array(df_iter[args.y].values[0])  # Convert to NumPy array
                elif args.entry != None:
                    x = np.array(df_iter[args.x].values[args.entry])
                    y = np.array(df_iter[args.y].values[args.entry])
                else:
                    x = np.array(df_iter[args.x].values[0])
                    y = np.array(df_iter[args.y].values[0])
                
                x_range = [np.percentile(x, args.percentile[0]), np.percentile(x, args.percentile[1])]
                y_range = [np.percentile(y, args.percentile[0]), np.percentile(y, args.percentile[1])]
                if idx == 0:
                    ranges = [x_range, y_range]
                
                elif args.zoom:
                    if x_range[0] > ranges[0][0]:
                        ranges[0][0] = x_range[0]
                    if x_range[1] < ranges[0][1]:
                        ranges[0][1] = x_range[1]
                    if y_range[0] > ranges[1][0]:
                        ranges[1][0] = y_range[0]
                    if y_range[1] < ranges[1][1]:
                        ranges[1][1] = y_range[1]
                
                if ncols == 1:
                    ax_current = ax
                else:
                    ax_current = ax[idx]


                hist2d = ax_current.hist2d(
                    x, y,
                    bins=args.bins,
                    range=(x_range, y_range),
                    norm=LogNorm() if args.logz else None,
                    density=True,
                )
                if args.diagonal:
                    ax_current.plot(x_range, x_range, color='k' if args.logz else 'white', linestyle='--')
                if args.horizontal != None:
                    ax_current.axhline(args.horizontal, color='k' if args.logz else 'white', linestyle='--')

            cbar = fig.colorbar(hist2d[3], ax=ax)
            cbar.set_label('Density' if not args.logz else 'Density (log scale)')
            cbar.ax.yaxis.set_label_position('right')  # Move label to the left
            
            for idx, compare in enumerate(df[args.comparable].unique()):
                if ncols == 1:
                    ax_current = ax
                else:
                    ax_current = ax[idx]
                ax_current.set_title(f"{args.comparable}: {compare}" if compare != None else None, fontsize=14)
                ax_current.set_xlabel(args.labelx if args.labelx != None else f"{args.x}" if args.x != "Time" else r"Time ($\mu$s)")
                ax_current.set_ylabel(args.labely) if idx == 0 else None
                if args.matchx:
                    ax_current.set_xlim(ranges[0])
                if args.matchy:
                    ax_current.set_ylim(ranges[1])

            # Set title
            fig.suptitle(f'{args.datafile.replace("_", " ")} ' + (f"{iterable}: {value} " if value != None else "") + f"- {config}", fontsize=titlefontsize)
            # dunestyle.WIP()
            
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
            os.makedirs(output_dir, exist_ok=True)
            output_file = ""
            if config is not None:
                output_file += f"{config.lower()}"
            if name is not None:
                output_file += f"_{name.lower()}"
            output_file += f"_{args.datafile.lower()}"
            if variable is not None:
                output_file += f"_{variable.lower()}"
            if args.comparable != "Comparable":
                output_file += f"_{args.comparable.lower()}"
            if iterable != "Iterable":
                output_file += f"_{iterable.lower()}{str(value).lower()}"
            output_file += "_hist2d.png"

            plt.savefig(os.path.join(output_dir, output_file.replace('#','n')))            
            
            print(f"Plot saved to {os.path.join(output_dir, output_file.replace('#','n'))}")
            plt.close()

if __name__ == '__main__':
    main()