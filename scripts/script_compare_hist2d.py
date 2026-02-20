
#!/usr/bin/env python3

"""
Script 3: Simple Heatmap Plot with DUNE Style
Demonstrates basic heatmap plotting with custom styling
"""

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args
from lib.imports import import_data, prepare_import

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the charge over time distribution of the particles"
)

parser.add_argument(
    '--datafile',
    type=str,
    default=None,
    help='Path to the input data file (pkl format)',
    required=True,
)

parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=None,
    help='DUNE detector configuration(s) to include in the plot (e.g. hd_1x2x6_centralAPA, hd_1x2x6, etc.)',
)

parser.add_argument(
    '--names', '-n',
    nargs='+',
    type=str,
    default=None,
    help='Name of the simulation configuration (e.g. marley_official, marley, etc.)',
)

parser.add_argument(
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='List of variable parameters to filter data (e.g. SignalParticleK, BackgroundType, etc.)',
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
    default=[0, 100],
    help='Percentile range for axis limits (e.g. 1 99)',
)

parser.add_argument(
    '--iterable', '-i',
    type=str,
    default=None,
    help='List of iterable parameters to produce plots',
)

parser.add_argument(
    '--select',
    nargs='+',
    default=None,
    help='If provided, filter plots for which according to select columns and values in save_values'
)

parser.add_argument(
    '--save_values', '-s',
    nargs='+',
    default=None,
    help='If iterable value is provided, save plots for which iterable equals this value',
)

parser.add_argument(
    '--bins', '-b',
    type=int,
    default=nbins,
    help='Number of bins for the histogram',
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
    '--density',
    action='store_true',
    help='Normalize histogram to density',
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
    '--vertical',
    type=float,
    default=None,
    help='Draw vertical line at specified x value',
)

parser.add_argument(
    '--diagonal',
    action='store_true',
    help='Draw diagonal line',
    default=False,
)

parser.add_argument(
    '--output', '-o',
    type=str,
    default=None,
    help='Output filepath for the plot',
)

parser.add_argument(
    '--debug', "-d",
    action='store_true',
    help='Enable debug mode',
)


args = parser.parse_args()


def main():
    # For each configuration provided combine the data files and plot the results
    df = import_data(args)

    if df.empty:
        rprint("[yellow]Warning:[/yellow] No datafiles found. Exiting...")
        return

    if args.variables is not None and args.iterable is not None:
        rprint("Both variables and iterable arguments provided. Please provide only one of them.")
        return
    ncols = len(args.variables) if args.variables is not None else len(df[args.iterable].unique()) if args.iterable is not None else 1
    
    print(f"Number of unique variables for plotting: {ncols}")

    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]
    
    for kdx, (config, name) in enumerate(zip(configs, names)):
        print(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
        if config is None:
            df_config = df
        else:
            df_config = df[(df['Config'] == config)]
        if name is not None:
            df_config = df_config[(df_config['Name'] == name)]
        
        variables = args.variables if args.variables is not None else [None]
        iterables = df_config[args.iterable].unique() if args.iterable is not None else [None]
        for (idx, variable), (jdx, iterable) in product(enumerate(variables), enumerate(iterables) if args.iterable is not None else enumerate([None])):
            
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx if args.variables is not None else jdx]
            
            if variable is not None and iterable is None:
                if args.debug:
                    rprint(f"[blue]Info:[/blue] Filtering for variable: {variable}")
                df_iterable = df_config[(df_config["Variable"] == variable)]

            elif iterable is not None and variable is None:
                if args.debug:
                    rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
                df_iterable = df_config[(df_config[args.iterable] == iterable)]
            
            elif variable is not None and iterable is not None:
                if args.debug:
                    rprint(f"[red]Error:[/red] Filtering for variable: {variable} and iterable: {iterable} not supported simultaneously.")
                return
            else:
                df_iterable = df_config.copy()
            
            subset = filter_dataframe(df_iterable, args)

            ranges = []
            if len(subset[args.x].values) > 1:
                rprint(f"[red]Error:[/red] Multiple entries found for {variable if variable is not None else f'{args.iterable}={iterable}'}")
                return
            
            x = np.array(subset[args.x].values[0])
            y = np.array(subset[args.y].values[0])
            
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
                ax_current = ax[idx if args.variables is not None else jdx]


            hist2d = ax_current.hist2d(
                x, y,
                bins=args.bins,
                range=(x_range, y_range),
                norm=LogNorm() if args.logz else None,
                density=args.density,
            )
            if args.diagonal:
                ax_current.plot(x_range, x_range, color='k' if args.logz else 'white', linestyle='--')
                ax_current.set_xlim(ranges[0])  # Set x limits to match the heatmap range
                ax_current.set_ylim(ranges[0])  # Set y limits to match the heatmap range
            if args.horizontal != None:
                ax_current.axhline(args.horizontal, color='k' if args.logz else 'white', linestyle='--')

            cbar = fig.colorbar(hist2d[3], ax=ax_current)
            if not args.logz:
                hist2d[3].set_array(np.ma.masked_where(hist2d[3].get_array() == 0, hist2d[3].get_array()))  # Mask zero values
                hist2d[3].set_clim(0, hist2d[3].get_array().max())  # Set color limits
        
        if args.density:
            cbar.set_label('Density' if not args.logz else 'Density (log scale)')
        else:
            cbar.set_label('Counts' if not args.logz else 'Counts (log scale)')
        cbar.ax.yaxis.set_label_position('right')  # Move label to the left
        
        for (idx, variable), (jdx, iterable) in product(enumerate(variables), enumerate(iterables) if args.iterable is not None else enumerate([None])):
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx if args.variables is not None else jdx]
            
            if ncols > 1:
                ax_current.set_title(f"Variable: {variable}" if variable is not None else f"{args.iterable}: {iterable}", fontsize=subtitlefontsize)
            
            ax_current.set_xlabel(args.labelx if args.labelx != None else f"{args.x}" if args.x != "Time" else r"Time ($\mu$s)")
            ax_current.set_ylabel(args.labely) if idx == 0 else None
            if args.matchx:
                ax_current.set_xlim(ranges[0])
            if args.matchy:
                ax_current.set_ylim(ranges[1])

        # Set title
        fig.suptitle(f'{args.datafile.replace("_", " ")} - {config}', fontsize=titlefontsize)
        # dunestyle.WIP()
            
        output_file = make_name_from_args(args, kdx, prefix=None, suffix="hist2d.png")
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