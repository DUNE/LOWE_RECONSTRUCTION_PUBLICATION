
#!/usr/bin/env python3

"""
Script 5: Combined Line Plot with DUNE Style
Demonstrates combined data plotting with custom styling
"""

from lib import *
from lib.imports import import_data, prepare_import
from lib.exports import make_name_from_args
from lib.functions import resolution, gaussian
from lib.selection import prepare_selection, filter_dataframe

from rich import print as rprint

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)

parser.add_argument(
    '--datafile',
    type=str,
    default="Vertex_Reconstruction_Efficiency",
    help='Path to the input data file (pkl format)',
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
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='Row filter variable name',
)

parser.add_argument(
    '--iterable', '-i',
    type=str,
    default=None,
    help='Iterable column to produce plots',
)

parser.add_argument(
    '--select',
    nargs='+',
    type=str,
    default=None,
    help='List of columns to filter the iterable or variables',
)

parser.add_argument(
    '--save_values', '-s',
    nargs='+',
    default=None,
    help='If select is provided, only save these values from the iterable column(s)',
)

parser.add_argument(
    '--comparable', '-c',
    type=str,
    default='Config',
    help='List of comparable parameter to produce plots',
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
    '--errory',
    action='store_true',
    help='Plot y-axis error bars',
    default=False,
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
    '--mirror',
    type=str,
    default=None,
    help='Mirror histogram data around the final x value',
)

parser.add_argument(
    '--output', '-o',
    type=str,
    default=None,
    help='Output filepath for the plot',
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
        rprint("No data to plot. Exiting.")
        return
    
    ncols = len(args.variables) if args.variables is not None else 1
    fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
    
    this_df = filter_dataframe(df, args)
    variables = args.variables if args.variables is not None else [None]
    iterables = this_df[args.iterable].unique() if args.iterable is not None else [None]
    
    for (idx, variable), (jdx, iterable) in product(enumerate(variables), enumerate(iterables) if args.iterable is not None else enumerate([None])):
        # Filter the DataFrame based on the current variable and iterable
        if args.debug:
            rprint(f"[blue]Info:[/blue] Processing variable: {variable}, iterable: {iterable}")

        if ncols == 1:
            ax_current = ax
        else:
            ax_current = ax[idx if args.variables is not None else jdx]
        
        if variable is not None and iterable is not None:
            # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}")
            subset = this_df[(this_df["Variable"] == variable) & (this_df[args.iterable] == iterable)]
        elif variable is not None and iterable is None:
            # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable}")
            subset = this_df[(this_df["Variable"] == variable)]
        elif iterable is not None and variable is None:
            # rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
            subset = this_df[(this_df[args.iterable] == iterable)]
        else:
            subset = this_df.copy()

            
            
        configs, names = prepare_import(args)
        configs = configs if configs is not None else [None]
        names = names if names is not None else [None]
        geoms = [geom.split('_')[0] for geom in configs]

        for ldx, (geom, config, name) in enumerate(zip(geoms, configs, names)):
            rprint(f"[blue]Info:[/blue] Processing Geometry: {geom}, Config: {config}, Name: {name}")
            df_config = subset[(subset['Config'] == config) & (subset['Name'] == name)]
            
            if df_config.empty:
                rprint(f"[yellow]Warning:[/yellow] No data for Config: {config}, Name: {name}. Skipping...")
                continue

            # Define line_dash. If config / name combinations are smaller than 4, use iterable (jdx) as referece. Else use ldx and restart with every new geometry.
            if len(configs) * len(names) <= 4:
                jdx_ref = jdx
            else:
                if ldx == 0 or geom != geoms[ldx - 1]:  # Check if geom has changed
                    jdx_ref = 0  # Restart jdx_ref for new geom
                else:
                    jdx_ref = ldx
            
            line_dash = ('-' if jdx_ref == 0 else '--' if jdx_ref == 1 else ':' if jdx_ref == 2 else '-.')

            # Handle multiple entries for the same configuration
            if len(df_config) > 1:
                rprint(f"[cyan]Info:[/cyan] Multiple entries found for Config: {config}. Skipping explode...")
                pass
            else:
                df_config = df_config.explode(column=[args.x, args.y, f"{args.y}Error"] if args.errory else [args.x, args.y])
            
            df_config = df_config.dropna(subset=[args.x, args.y, f"{args.y}Error"] if args.errory else [args.x, args.y])
            if args.rangex is not None:
                df_config = df_config[(df_config[args.x] >= args.rangex[0]) & (df_config[args.x] <= args.rangex[1])]

            config_label = config_dict[config] if config in config_dict else str(config)
            if len(args.configs) <= 2 and len(args.names) == 1:
                geom_label = f"{geom.upper()}"
            elif len(args.configs) > 2 and len(args.names) == 1:
                geom_label = f"{geom.upper()}, {config_label}"
            elif len(args.configs) == 1 and len(args.names) > 1:
                geom_label = f"{geom.upper()}, {name}"
            else:
                geom_label = f"{geom.upper()}, {config_label}, {name}"
            
            if args.iterable is not None:
                geom_label += f", {iterable}"
                                    
            # Plot the histogram for the current configuration

            x = np.asarray(df_config[args.x].unique().tolist())
            y = np.asarray(df_config[args.y].tolist())
            if args.debug:
                print(f"x: {len(x)}", f"y: {len(y)}", x, y)
            x_bin = x[1] - x[0] if len(x) > 1 else 1
            x_edges = np.linspace(x[0] - x_bin/2, x[-1] + x_bin/2, len(x) + 1)

            if config == args.mirror:
                # Add extension to the data by mirroring the y values and adding the same amount of bins to the right
                x = np.concatenate((x, x + (x[-1] - x[0]) + x_bin))
                x_edges = np.linspace(x[0] - x_bin/2, x[-1] + x_bin/2, len(x) + 1)
                y = np.concatenate((y, y[::-1]))
                    # rprint(f"[blue]Info:[/blue] Mirroring data for configuration: {config}")

            try:
                if args.errory:
                    ax_current.errorbar(
                        x, 
                        y, 
                        yerr=df_config[f"{args.y}Error"] if f"{args.y}Error" in df_config.columns else None,
                        fmt='o',
                        label=geom_label if idx == ncols -1 else None,
                        color=f'C{ldx}' if len(df["Geometry"].unique()) <=1 else f'C0' if geom == 'hd' else f'C1' if geom == 'vd' else f'C2',
                        # linestyle='-',  # Connect data with a step line
                    )
                else:
                    ax_current.hist(
                        x, 
                        bins=x_edges,
                        weights=y,
                        histtype='step',
                        align=args.align,
                        label=geom_label if idx == ncols -1 else None,
                        color=f'C{ldx}' if len(df["Geometry"].unique()) <=1 else f'C0' if geom == 'hd' else f'C1' if geom == 'vd' else f'C2',
                        ls=line_dash
                    )

            except ValueError:
                if args.errory:
                    ax_current.errorbar(
                        x[::-1], 
                        y[::-1], 
                        yerr=df_config[f"{args.y}Error"][::-1] if f"{args.y}Error" in df_config.columns else None,
                        fmt='o',
                        label=geom_label if idx == ncols -1 else None,
                        color=f'C{ldx}' if len(df["Geometry"].unique()) <=1 else f'C0' if geom == 'hd' else f'C1' if geom == 'vd' else f'C2',
                        # linestyle='-',  # Connect data with a step line
                    )
                else:
                    ax_current.hist(
                        x[::-1], 
                        bins=x_edges[::-1],
                        weights=y[::-1],
                        histtype='step',
                        align=args.align,
                        label=geom_label if idx == ncols -1 else None,
                        color=f'C{ldx}' if len(df["Geometry"].unique()) <=1 else f'C0' if geom == 'hd' else f'C1' if geom == 'vd' else f'C2',
                        ls=line_dash
                    )
    
            # Set titles and labels for the axes
            if variable is not None:
                ax_current.set_title(f"Variable: {variable}", fontsize=subtitlefontsize)
            
            ax_current.set_xlabel(args.labelx[idx] if args.labelx and len(args.labelx) == ncols else args.labelx[0] if args.labelx else args.x)
            if idx == 0:
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
            if idx == ncols -1:
                ax_current.legend()
        
    # Set the figure title
    figure_title = f"{args.datafile.replace('_', ' ')}"
    if args.iterable is not None:
        figure_title += f" - {args.iterable} Scan"
    
    fig.suptitle(figure_title, fontsize=titlefontsize)
    
    # dunestyle.WIP()
        
    output_file = make_name_from_args(args, prefix=None, suffix="comparison.png")
    if args.output is not None:
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        rprint(f"[green]Success:[/green] Plot saved to:\n{args.output}{output_file}")
    else:  
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
        os.makedirs(output_dir, exist_ok=True)
        rprint(f"[green]Success:[/green] Plot saved to:\n{os.path.join(output_dir.split('..')[1], output_file)}")
    
    plt.savefig(os.path.join(output_dir, output_file)) 
    
    plt.close()

if __name__ == '__main__':
    main()