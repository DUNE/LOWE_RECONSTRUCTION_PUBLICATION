#!/usr/bin/env python3

"""
Script 5: Combined Line Plot with DUNE Style
Demonstrates combined data plotting with custom styling
"""
# Import config from __init__.py
from lib import *
from lib.functions import resolution, gaussian
from lib.selection import prepare_selection, filter_dataframe
from lib.imports import import_data

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)
parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=["hd_1x2x6", "hd_1x2x6_lateralAPA", "hd_1x2x6_centralAPA", "vd_1x8x14_3view_30deg", "vd_1x8x14_3view_30deg_nominal"],
    help='DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)',
)

parser.add_argument(
    '--names',
    nargs='+',
    type=str,
    default=['marley_official'],
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
    '--rangex',
    nargs=2,
    type=float,
    default=None,
    help='Range for x-axis values',
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
    '--align',
    type=str,
    default="mid",
    help='Alignment of histogram bars (e.g. mid, left, right)',
)

parser.add_argument(
    '--debug',
    action='store_true',
    help='Enable debug mode',
)
args = parser.parse_args()

def main():
    """
    Main function to process simulation configurations, load data files,
    and generate plots based on the provided arguments.
    """
    df = import_data(args)

    # Check if the DataFrame is empty
    if df.empty:
        print("No data to plot. Exiting.")
        return

    # Set default variable if none are provided
    if args.variables is None:
        args.variables = [""]
        df["Variable"] = ""
    
    # Prepare unique combinations and values for plotting
    unique_combinations, unique_values = prepare_selection(df, args)
    
    # Loop through each unique combination for plotting
    for combination in unique_combinations:
        this_df = filter_dataframe(df, args, unique_values, combination)
                
        # Skip if the filtered DataFrame is empty
        if this_df.empty:
            continue
    
        ncols = len(args.variables)
        fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
        
        # Loop through each variable for plotting
        for jdx, variable in enumerate(args.variables):
            ax_current = ax if ncols == 1 else ax[jdx]
            
            # Filter DataFrame based on the current variable
            df_var = this_df[this_df["Variable"] == variable] if variable != "" else this_df.copy()
           
            # Loop through unique geometries for plotting
            for idx, geom in enumerate(sorted(df_var['Geometry'].unique())):
                df_geom = df_var[df_var['Geometry'] == geom]
                
                # Loop through configurations and comparable values
                for config, (kdx, value) in product(df_geom["Config"].unique(), enumerate(df_geom[args.comparable].unique())):
                    df_config = df_geom[(df_geom[args.comparable] == value) & (df_geom['Config'] == config)]

                    # Handle multiple entries for the same configuration
                    if len(df_config) > 1:
                        print(f"Info: Multiple entries found for Config: {config}, {args.comparable}: {value}. Skipping explode.")
                    else:
                        df_config = df_config.explode(column=[args.x, args.y])
                    
                    df_config = df_config.dropna(subset=[args.x, args.y])
                    if args.rangex is not None:
                        df_config = df_config[(df_config[args.x] >= args.rangex[0]) & (df_config[args.x] <= args.rangex[1])]
                    
                    label = config_dict[value] if value in config_dict else str(value)
                    
                    # Plot the histogram for the current configuration
                    if not df_config.empty:
                        x = np.asarray(df_config[args.x].unique().tolist())
                        x_bin = x[1] - x[0] if len(x) > 1 else 1
                        x_edges = np.linspace(x[0] - x_bin/2, x[-1] + x_bin/2, len(x) + 1)

                        try:
                            ax_current.hist(x, 
                                bins=x_edges,
                                weights=df_config[args.y],
                                histtype='step',
                                align=args.align,
                                label=f"{geom.upper()}, {label}" if jdx == len(args.variables) -1 else None,
                                color=f'C{idx}',
                                ls='-' if kdx == 0 else '--' if kdx == 1 else ':' if kdx == 2 else '-.'
                            )

                        except ValueError:
                            ax_current.hist(x[::-1], 
                                bins=x_edges[::-1],
                                weights=df_config[args.y][::-1],
                                histtype='step',
                                align=args.align,
                                label=f"{geom.upper()}, {label}" if jdx == len(args.variables) -1 else None,
                                color=f'C{idx}',
                                ls='-' if kdx == 0 else '--' if kdx == 1 else ':' if kdx == 2 else '-.'
                            )
            
            # Set titles and labels for the axes
            if variable != "":
                ax_current.set_title(f"Variable: {variable}", fontsize=14)
            
            ax_current.set_xlabel(args.labelx[jdx] if args.labelx and len(args.labelx) == len(args.variables) else args.labelx[0] if args.labelx else args.x)
            if jdx == 0:
                ax_current.set_ylabel(args.labely if args.labely else args.y)

            # Set y-axis limits based on the y variable
            if args.y == "Efficiency":
                ax_current.set_ylim(0, 110)
                ax_current.axhline(100, color='gray', linestyle='--', linewidth=1)
            elif args.y == "RMS":
                ax_current.set_ylim(0, 0.5)

            # Set logarithmic scale if specified
            if args.logy:
                ax_current.set_yscale('log')
            if args.logx:
                ax_current.set_xscale('log')
            
            # Add legend for the last variable
            if jdx == len(args.variables) -1:
                ax_current.legend()
            
        # Set the figure title
        figure_title = f"{args.datafile.replace('_', ' ')}"
        if args.iterable is not None:
            figure_title += f" ({', '.join([f'{col}={val}' for col, val in zip(unique_values.keys(), combination)])})"
        fig.suptitle(figure_title, fontsize=titlefontsize)
        
        # Create output directory and save the plot
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"comparison_{args.datafile.lower()}"
        if args.iterable is not None:
            output_filename += '_' + '_'.join([f"{str(col).lower()}{str(combination[idx]).lower()}" for idx, col in enumerate(unique_values.keys())])
        if args.variables != [""]:
            output_filename += '_' + '_'.join(args.variables).lower()
        
        output_filename = output_filename.replace('#','n')
        output_file = os.path.join(output_dir, f"{output_filename}.png")
        plt.savefig(output_file)
        
        print(f"Plot saved to {output_file}")
        plt.close()

if __name__ == '__main__':
    main()