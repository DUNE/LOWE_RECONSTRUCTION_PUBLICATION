
#!/usr/bin/env python3


"""
Script 6: Combined Line Plot with DUNE Style
Demonstrates combined data to table conversion with custom styling
"""
# Import config from __init__.py
from lib import *
from lib.functions import resolution, gaussian
from lib.selection import prepare_selection, filter_dataframe
from lib.imports import import_data
from lib.format import format_with_error

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
    '--names',
    nargs='+',
    type=str,
    default=None,
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
    '--variable_name', '-n',
    type=str,
    default="Variable",
    help='Title for the variable on the table',
)

parser.add_argument(
    '-x',
    type=str,
    default=None,
    help='Column name for x-axis values',
)

parser.add_argument(
    '--rangex',
    nargs=2,
    type=float,
    default=None,
    help='Range for x-axis values as (min, max)',
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
    """
    Main function to process simulation configurations, load data files,
    and generate tables based on the provided arguments.
    """
    df = import_data(args)

    # Check if the DataFrame is empty
    if df.empty:
        print("No data to plot. Exiting.")
        return

    # Set default variable if none are provided
    if args.variables is None:
        args.variables = [""]
        df[args.variable_name] = ""
    
    # Prepare unique combinations and values for plotting
    unique_combinations, unique_values = prepare_selection(df, args)
    
    # Capitalize all letters in df["Geometry"]
    df["Geometry"] = df["Geometry"].str.upper()
        
    # Substitute the names in df["Config"] to be more readable with the config_dict
    df["Config"] = df["Config"].map(lambda x: config_dict.get(x, x))

    for combination in unique_combinations:
        this_df = filter_dataframe(df, args, unique_values, combination)
                
        # Skip if the filtered DataFrame is empty
        if this_df.empty:
            continue
    
        if args.variables != [""]:
            # Select entries in df column "Variable" matching any of the entries in args.variables list
            df_var = this_df[this_df[args.variable_name].isin(args.variables)].copy()
        
        else:
            df_var = this_df.copy()

        cols = [args.x, args.y] if args.x is not None else [args.y]
        if f"{args.y}Error" in df_var.columns:
            cols.append(f"{args.y}Error")
        if f"{args.x}Error" in df_var.columns:
            cols.append(f"{args.x}Error")

        df_config = df_var.explode(column=cols)
        df_config = df_config.dropna(subset=cols + [args.variable_name])

        if args.rangex is not None and args.x is not None:
            df_config[args.x] = df_config[args.x].astype(float)
            print(f"Applying x-axis range filter: {args.rangex[0]} to {args.rangex[1]}")
            df_config = df_config[(df_config[args.x] >= args.rangex[0]) & (df_config[args.x] <= args.rangex[1])]

        # If error columns exist, combine the mean and error into a single string column. E.g. "0.95 ± 0.02" Use a precision based on the error value
        if f"{args.y}Error" not in df_config.columns:
            df_config[f"{args.y}Error"] = df_config[args.y]
        
        df_table = df_config.groupby(["Geometry", "Config", args.variable_name]).agg({
            args.y : ['mean'],
            f"{args.y}Error" : lambda x: np.sqrt(np.sum(x**2)) / len(x)
        })

        df_table[args.y] = df_table.apply(lambda row: format_with_error(row, args=args), axis=1)
        df_table = df_table.drop(columns=[(f"{args.y}Error", '<lambda>')])
        df_table.columns = df_table.columns.droplevel(1)

        if args.variable_title is not None:
            df_table = df_table.rename(columns={args.y: args.variable_title})
            df_table = df_table.pivot_table(index=["Geometry", "Config"], columns=args.variable_name, values=[args.variable_title], aggfunc='first')
        
        else:
            df_table = df_table.pivot_table(index=["Geometry", "Config"], columns=args.variable_name, values=[args.y], aggfunc='first')
        
        # Combine the "Geometry" and "Config" index into a single index called "Configuration"
        if len(args.configs) <= 2 and len(args.names) == 1:
            df_table.index = df_table.index.map(lambda x: f"{x[0]}")
        elif len(args.configs) > 2 and len(args.names) == 1:
            df_table.index = df_table.index.map(lambda x: f"{x[0]} {x[1]}")
        elif len(args.configs) == 1 and len(args.names) > 1:
            df_table.index = df_table.index.map(lambda x: f"{x[1]}")
        else:
            df_table.index = df_table.index.map(lambda x: f"{x[0]} {x[1]}")
        
        df_table.index.name = "Configuration"
        # Sort columns as they appear in args.variables
        if args.variable_title is not None:
            df_table = df_table.reindex(columns=args.variables, level=1)

        # Sort according to the configuration column and config_order
        if len(args.configs) > 2 and len(args.names) == 1:
            df_table = df_table.reindex(config_order, level='Configuration')
        # Drop rows with all NaN values
        df_table = df_table.dropna(how='all')

        # Make the "Configuration" index a column and drop the index
        df_table = df_table.reset_index()
        # Add a title to the table based on the iterable values
        title_parts = [f"{col}={val}" for col, val in zip(unique_values.keys(), combination)]
        if title_parts:
            print(f"Table for {', '.join(title_parts)}")
        else:
            print("Table")

        # Don't print the row index
        print(df_table.to_string(index=False))

        output_dir = os.path.join(os.path.dirname(__file__), '..', 'tables')
        os.makedirs(output_dir, exist_ok=True)
        
        if len(args.configs) == 1 and len(args.names) == 1:
            output_filename = f"configuration_comparison_{args.configs[0].lower()}_{args.datafile.lower()}"
        elif len(args.configs) == 2 and len(args.names) == 1:
            output_filename = f"{args.names[0].lower()}_{args.datafile.lower()}"
        elif len(args.configs) > 2 and len(args.names) == 1:
            output_filename = f"configuration_comparison_{args.names[0].lower()}_{args.datafile.lower()}"
        elif len(args.configs) == 1 and len(args.names) > 1:
            output_filename = f"configuration_iteration_{args.configs[0].lower()}_{args.datafile.lower()}"   
        else:
            output_filename = f"comparison_{args.datafile.lower()}"     
        
        if args.iterable is not None:
            output_filename += '_' + '_'.join([f"{str(col).lower()}{str(combination[idx]).lower()}" for idx, col in enumerate(unique_values.keys())])
        # Add variables to filename
        if args.variables != [""]:
            output_filename += '_' + '_'.join(args.variables).lower()
        if args.rangex is not None:
            output_filename += f"_xrange{args.rangex[0]}-{args.rangex[1]}"
        
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