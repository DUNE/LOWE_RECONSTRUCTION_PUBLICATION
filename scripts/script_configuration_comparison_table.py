
#!/usr/bin/env python3


"""
Script 6: Combined Line Plot with DUNE Style
Demonstrates combined data to table conversion with custom styling
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
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='Filter variable name',
)

parser.add_argument(
    '--variable_title', '-t',
    type=str,
    default=None,
    help='Title for the variable on the table',
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
    '--emph',
    type=int,
    default=None,
    help='Index of the columns to emphasize in the table'
),

parser.add_argument(
    '--it',
    type=int,
    default=None,
    help='Index of the columns to italicize in the table'
),

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
    
    # Capitalize all letters in df["Geometry"]
    df["Geometry"] = df["Geometry"].str.upper()
        
    # Substitute the names in df["Config"] to be more readable with the config_dict
    df["Config"] = df["Config"].map(lambda x: config_dict.get(x, x))

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
    
        if args.variables != [""]:
            # Select entries in df column "Variable" matching any of the entries in args.variables list
            df_var = this_df[this_df["Variable"].isin(args.variables)].copy()
        
        else:
            df_var = this_df.copy()



        cols = [args.x, args.y]
        if f"{args.y}Error" in df_var.columns:
            cols.append(f"{args.y}Error")
        if f"{args.x}Error" in df_var.columns:
            cols.append(f"{args.x}Error")

        df_config = df_var.explode(column=cols)
        df_config = df_config.dropna(subset=cols + ["Variable"])
        df_table = df_config.groupby(["Geometry", "Config", "Variable"]).agg({
            args.y : ['mean'],
            f"{args.y}Error" : lambda x: np.sqrt(np.sum(x**2)) / len(x) if f"{args.y}Error" in df_config.columns else np.nan,
        })

        # If error columns exist, combine the mean and error into a single string column. E.g. "0.95 ± 0.02" Use a precision based on the error value
        if f"{args.y}Error" in df_config.columns:
            def format_with_error(row, significant_figures=None):
                mean = row[(args.y, 'mean')]
                error = row[(f"{args.y}Error", '<lambda>')]
                if pd.isna(error) or error == 0:
                    return f"{mean:.2f}"  # Default to 2 significant figures if error is None or zero
                
                # Determine significant figures based on error if not provided
                if significant_figures is None:
                    error_magnitude = -int(np.floor(np.log10(abs(error)))) + 1
                    significant_figures = max(1, error_magnitude)  # Use error to decide significant figures

                format_string = f"{{:.{significant_figures}f}} ({{:.{significant_figures}f}})"  # Ensure at least specified significant figures
                return format_string.format(mean, error)
            df_table[args.y] = df_table.apply(format_with_error, axis=1)
            df_table = df_table.drop(columns=[(f"{args.y}Error", '<lambda>')])
            df_table.columns = df_table.columns.droplevel(1)
        else:
            df_table[args.y] = df_table[(args.y, 'mean')].map(lambda x: f"{x:.2f}")
            df_table = df_table.drop(columns=[(args.y, 'mean')])

        if args.variable_title is not None:
            # Rename the column of args.y to args.variable_title
            df_table = df_table.rename(columns={args.y: args.variable_title})
            df_table = df_table.pivot_table(index=["Geometry", "Config"], columns="Variable", values=[args.variable_title], aggfunc='first')
        else:
            df_table = df_table.pivot_table(index=["Geometry", "Config"], columns="Variable", values=[args.y], aggfunc='first')
        
        # Combine the "Geometry" and "Config" index into a single index called "Configuration"
        df_table.index = df_table.index.map(lambda x: f"{x[0]} {x[1]}")
        df_table.index.name = "Configuration"


        # Make the "Configuration" index a column and drop the index
        df_table = df_table.reset_index()
        # Add a title to the table based on the iterable values
        title_parts = [f"{col}={val}" for col, val in zip(unique_values.keys(), combination)]
        if title_parts:
            print(f"Table for {' ,'.join(title_parts)}")
        else:
            print("Table")

        # Don't print the row index
        print(df_table.to_string(index=False))

        output_dir = os.path.join(os.path.dirname(__file__), '..', 'tables')
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{args.name.lower()}_{args.datafile.lower()}"
        if args.iterable is not None:
            output_filename += '_' + '_'.join([f"{str(col).lower()}{str(combination[idx]).lower()}" for idx, col in enumerate(unique_values.keys())])
        # Add variables to filename
        if args.variables != [""]:
            output_filename += '_' + '_'.join(args.variables).lower()
        
        output_filename = output_filename.replace('#','n')
        output_file = os.path.join(output_dir, f"{output_filename}")
        
        # Italicize the specified column
        if args.it is not None and 0 <= args.it < df_table.shape[1]:
            df_table.iloc[:, args.it] = '\\textit{' + df_table.iloc[:, args.it] + '}'
        # Emphasize the first column
        if args.emph is not None and 0 <= args.emph < df_table.shape[1]:
            df_table.iloc[:, args.emph] = '\\emph{' + df_table.iloc[:, args.emph] + '}'

        df_table.to_latex(os.path.join(output_dir, f"{output_filename}.tex"), index=False, column_format='l' + 'c' * (df_table.shape[1] - 1), multicolumn_format='c', bold_rows=False, escape=False)
        
        print(f"Saving table to {output_file}.tex")

if __name__ == '__main__':
    main()