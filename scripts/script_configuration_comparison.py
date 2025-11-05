
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
    default=["hd_1x2x6", "hd_1x2x6_centralAPA", "hd_1x2x6_lateralAPA", "vd_1x8x14_3view_30deg", "vd_1x8x14_3view_30deg_nominal"],
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
    default="Vertex_Reconstruction_Efficiency",
    help='Path to the input data file (pkl format)',
)

parser.add_argument(
    '--iterable', '-i',
    type=str,
    default='Config',
    help='List of iterable parameters to produce plots',
)

parser.add_argument(
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='Row filter variable name',
)

parser.add_argument(
    '--exclusive', '-e',
    nargs='+',
    type=str,
    default=None,
    help='Column name for exclusive filtering',
)

parser.add_argument(
    '-x',
    type=str,
    default="Values",
    help='Column name for x-axis values',
)

parser.add_argument(
    '-y',
    type=str,
    default=None,
    help='Column name for y-axis values',
),

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
    '--labelx',
    nargs='+',
    type=str,
    default=None,
    help='Label for x-axis on plot',
)

parser.add_argument(
    '--labely',
    type=str,
    default=None,
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
    if args.variables is None:
        args.variables = [""]
    
    ncols = len(args.variables)
    fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
    for jdx, variable in enumerate(args.variables):
        if variable != "":
            df_var = df[df["Variable"] == variable] 
        else:
            df_var = df.copy()
        # plt.figure()
        for idx, geom in enumerate(sorted(df_var['Geometry'].unique())):
            # print(f"Processing Geometry: {geom}")
            df_geom = df_var[df_var['Geometry'] == geom]
            
            for config, (kdx, value) in product(df_geom["Config"].unique(), enumerate(df_geom[args.iterable].unique())):
                # print(f"Config: {config}, {args.iterable}: {value}")
                df_config = df_geom[(df_geom[args.iterable] == value) & (df_geom['Config'] == config)]
                if args.exclusive is not None:
                    for col in args.exclusive:
                        unique_values = df_config[col].unique()
                        # print(f"Filtering {col} with unique values: {unique_values}")
                        # If there is some NaN value, filter the rest out
                        if any(np.isnan(unique_values)):
                            # print(f"Column {col} has NaN values, filtering to keep only NaNs")
                            df_config = df_config[df_config[col].isna()]
                        else:
                            if unique_values.size > 0:  # Check if unique_values is not empty
                                df_config = df_config[df_config[col] == unique_values[0]]

                df_config = df_config.explode(column=[args.x, args.y])
                label = config_dict[value] if value in config_dict else str(value)
                if not df_config.empty:
                    ax[jdx].hist(df_config[args.x], 
                                bins=len(df_config[args.x].unique()),
                                weights=df_config[args.y],
                                histtype='step',
                                label=f"{geom.upper()}, {label}" if jdx == len(args.variables) -1 else None,
                                color=f'C{idx}',
                                ls='-' if kdx == 0 else '--' if kdx == 1 else ':' if kdx == 2 else '-.'
                            )
        
        if ncols == 1:
            ax_current = ax
        else:
            ax_current = ax[jdx]
        
        ax_current.set_title(f"Variable: {variable}", fontsize=14)
        
        if args.labelx is not None:
            if len(args.labelx) == len(args.variables):
                ax_current.set_xlabel(args.labelx[jdx])
            elif len(args.labelx) == 1:
                ax_current.set_xlabel(args.labelx[0])
            else:
                ax_current.set_xlabel(args.x)
        else:
            ax_current.set_xlabel(args.x)
        
        if jdx == 0:
            if args.labely is not None:
                ax_current.set_ylabel(args.labely)
            else:
                ax_current.set_ylabel(args.y)

        if args.y == "Efficiency":
            ax_current.set_ylim(0, 110)
            # Draw horizontal line at 100%
            ax_current.axhline(100, color='gray', linestyle='--', linewidth=1)

        if args.logy:
            ax_current.set_yscale('log')
        if args.logx:
            ax_current.set_xscale('log')
        
        if jdx == len(args.variables) -1:
            ax_current.legend()
        
    
    fig.suptitle(f'{args.datafile.replace("_", " ")}', fontsize=18)
    # dunestyle.WIP()
        
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{args.name.lower()}_{args.datafile.lower()}_{'_'.join(args.variables).lower()}.png")
    plt.savefig(output_file)
    
    print(f"Plot saved to {output_file}")
    plt.close()

if __name__ == '__main__':
    main()