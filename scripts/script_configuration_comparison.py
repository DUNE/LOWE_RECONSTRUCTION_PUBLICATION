
#!/usr/bin/env python3


"""
Script 5: Combined Line Plot with DUNE Style
Demonstrates combined data plotting with custom styling
"""
# Import config from __init__.py
from lib import *
from lib.functions import resolution, gaussian

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
    default='Config',
    help='List of comparable parameter to produce plots',
)

parser.add_argument(
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='Row filter variable name',
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
        df["Variable"] = ""
    
    # Prepare the df filtering. The argument 'iterable' allows to filter the dataframe to only include rows with unique values in the specified columns
    unique_values = {}
    for col in args.iterable or []:
        if col not in df.columns:
            print(f"Iterable filter column '{col}' not found in data columns.")
            return
        unique_values[col] = df[col].unique()
        if len(unique_values[col]) > 1:
            print(f"Column '{col}' has multiple unique values: {unique_values[col]}. of type {type(unique_values[col][0])}")

    # Filter the dataframe to include rows with unique value combinations in the specified columns
    if args.iterable != None and args.save_values != None:
        print(f"Applying save_values filter: {args.save_values} for iterables: {args.iterable}")
    
    unique_combinations = list(product(*unique_values.values()))
    for combination in unique_combinations:
        this_df = df.copy()
        for col, val in zip(unique_values.keys(), combination):
            if val is np.nan or (isinstance(val, float) and np.isnan(val)):
                this_df = this_df[this_df[col].isna()]
            else:
                this_df = this_df[this_df[col] == val]
            # print(f"Filtering {col}={val}, resulting entries: {len(this_df)}")
        if this_df.empty:
            print(f"No data for combination: {', '.join([f'{col}={val}' for col, val in zip(unique_values.keys(), combination)])}. Skipping.")
            continue
        
        if args.save_values is not None:
        
            if len(args.iterable) == len(args.save_values):
                for i, col in enumerate(args.iterable):
                    if col in this_df.columns:
                        if args.save_values[i] == "nan":
                            this_df = this_df[this_df[args.iterable[i]].isna()]
                        
                        else:
                            # Check for boolean dtype
                            if pd.api.types.is_bool_dtype(this_df[args.iterable[i]]):
                                # print(f"Applying boolean save_value filter: {args.save_values[i]} for column: {col}")
                                if str(args.save_values[i]).lower() in ['true', '1']:
                                    bool_value = True
                                elif str(args.save_values[i]).lower() in ['false', '0']:
                                    bool_value = False
                                else:
                                    print(f"Warning: Could not convert '{args.save_values[i]}' to boolean. Skipping filter.")
                                    continue
                                this_df = this_df[this_df[args.iterable[i]] == bool_value]

                            elif pd.api.types.is_numeric_dtype(this_df[args.iterable[i]]):
                                # print(f"Applying numeric save_value filter: {args.save_values[i]} for column: {col}")
                                if not this_df.empty:
                                    try:
                                        # print(f"Applying save_value filter: {args.save_values[i]} of type {type(args.save_values[i])} for column: {col} of type {this_df[args.iterable[i]].dtype}, resulting entries before filter: {len(this_df)}")
                                        save_value_converted = type(this_df[args.iterable[i]].iloc[0])(args.save_values[i])
                                        # print(f"Converted save_value: {save_value_converted} to type {type(this_df[args.iterable[i]].iloc[0])}")
                                        this_df = this_df[this_df[args.iterable[i]] == save_value_converted]  # Ensure comparison is done as strings

                                    except ValueError:
                                        print(f"Warning: Could not convert '{args.save_values[i]}' to type {type(this_df[args.iterable[i]].iloc[0])}. Skipping filter.")
                            
                            elif this_df[args.iterable[i]].dtype == 'object':
                                # Check if the column contains the value as is
                                if args.save_values[i] in this_df[args.iterable[i]].values:
                                    # print(f"Value '{args.save_values[i]}' found in column '{col}' as is. Applying filter.")
                                    this_df = this_df[this_df[args.iterable[i]] == args.save_values[i]]
                                else:
                                    # Convert both to string for comparison
                                    # print(f"Value '{args.save_values[i]}' not found in column '{col}' as is (choose from {this_df[args.iterable[i]].unique()}). Trying string comparison.")
                                    this_df[args.iterable[i]] = this_df[args.iterable[i]].astype(str)
                                    this_df = this_df[this_df[args.iterable[i]].astype(str) == str(args.save_values[i])]
                                    # print(f"Applying save_value filter: {args.save_values[i]} of type {type(args.save_values[i])} for column: {col} of type {this_df[args.iterable[i]].dtype}, resulting entries after filter: {len(this_df)}")

                            
                            else:
                                this_df[args.iterable[i]] = this_df[args.iterable[i]].astype(str)
                                this_df = this_df[this_df[args.iterable[i]].astype(str) == str(args.save_values[i])]
                                # print(f"Applying save_value filter: {args.save_values[i]} of type {type(args.save_values[i])} for column: {col} of type {this_df[args.iterable[i]].dtype}, resulting entries after filter: {len(this_df)}")
                
                    # print(f"Resulting entries after filter: {len(this_df)}")
                
                if this_df.empty:
                    continue
    
        ncols = len(args.variables)
        fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
        for jdx, variable in enumerate(args.variables):
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[jdx]
            
            if variable != "":
                df_var = this_df[this_df["Variable"] == variable] 
            
            else:
                df_var = this_df.copy()
            # plt.figure()
            for idx, geom in enumerate(sorted(df_var['Geometry'].unique())):
                # print(f"Processing Geometry: {geom}")
                df_geom = df_var[df_var['Geometry'] == geom]
                
                for config, (kdx, value) in product(df_geom["Config"].unique(), enumerate(df_geom[args.comparable].unique())):
                    # print(f"Config: {config}, {args.comparable}: {value}")
                    df_config = df_geom[(df_geom[args.comparable] == value) & (df_geom['Config'] == config)]

                    if len(df_config) > 1:
                        print(f"Warning: Multiple entries found for Config: {config}, {args.comparable}: {value}. Using the first entry.")
                        # Print the df_config for debugging
                        if args.debug:
                            print(df_config)
                        df_config = df_config.iloc[[0]]
                    df_config = df_config.explode(column=[args.x, args.y])
                    # If entries in args.x or args.y are nan, remove them
                    df_config = df_config.dropna(subset=[args.x, args.y])

                    label = config_dict[value] if value in config_dict else str(value)
                    if not df_config.empty:
                        ax_current.hist(df_config[args.x], 
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
            
            if variable != "":
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
            elif args.y == "RMS":
                ax_current.set_ylim(0, 0.5)

            if args.logy:
                ax_current.set_yscale('log')
            if args.logx:
                ax_current.set_xscale('log')
            
            if jdx == len(args.variables) -1:
                ax_current.legend()
            
        figure_title = f"{args.datafile.replace('_', ' ')}"
        if args.iterable is not None:
            figure_title += f" ({', '.join([f'{col}={val}' for col, val in zip(unique_values.keys(), combination)])})"
        fig.suptitle(figure_title, fontsize=titlefontsize)
        # dunestyle.WIP()
            
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{args.name.lower()}_{args.datafile.lower()}"
        if args.iterable is not None:
            output_filename += '_' + '_'.join([f"{str(col).lower()}{str(combination[idx]).lower()}" for idx, col in enumerate(unique_values.keys())])
        # Add variables to filename
        if args.variables != [""]:
            output_filename += '_' + '_'.join(args.variables).lower()
        
        output_filename = output_filename.replace('#','n')
        output_file = os.path.join(output_dir, f"{output_filename}.png")
        plt.savefig(output_file)
        
        print(f"Plot saved to {output_file}")
        plt.close()

if __name__ == '__main__':
    main()