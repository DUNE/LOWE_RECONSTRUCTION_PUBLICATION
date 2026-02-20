
#!/usr/bin/env python3

"""
Script 1: Simple Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling
"""

from rich import print as rprint

from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args
from lib.imports import import_data, prepare_import

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)

parser.add_argument(
    '--datafile',
    type=str,
    default=None,
    help='Name of the input data file (pkl format)',
    required=True
)

parser.add_argument(
    '--configs',
    nargs='+',
    type=str,
    default=None,
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
    '--variables', '-v',
    nargs='+',
    type=str,
    default=None,
    help='List of variable parameters to filter data (e.g. SignalParticleK, BackgroundType, etc.)',
)

parser.add_argument(
    '--iterable', '-i',
    type=str,
    default=None,
    help='Iterable column to produce plots',
    required=True
)

parser.add_argument(
    '--select',
    nargs='+',
    default=None,
    help='If provided, use these key to apply save_values filtering',
)

parser.add_argument(
    '--save_values', '-s',
    nargs='+',
    default=None,
    help='If select key is provided, save plots for which select key equals this value',
)

parser.add_argument(
    '-x',
    type=str,
    default=None,
    help='Column name for x-axis values',
    required=True
)

parser.add_argument(
    '--errorx',
    action='store_true',
    help='Include error bars on x-axis',
    default=False,
)

parser.add_argument(
    '-y',
    type=str,
    default=None,
    help='Column name for y-axis values',
    required=True
)

parser.add_argument(
    '--stacked',
    action='store_true',
    help='Create stacked histograms',
    default=False,
)

parser.add_argument(
    '--reduce',
    action='store_true',
    help='Reduce number of lines plotted for clarity',
    default=False,
)

parser.add_argument(
    '--labelx',
    type=str,
    default=f"True Neutrino Energy (MeV)",
    help='Label for x-axis on plot',
)

parser.add_argument(
    '--labely',
    type=str,
    default=None,
    help='Label for y-axis on plot',
)

parser.add_argument(
    '--labelz',
    type=str,
    default=None,
    help='Label for iterable data in legend',
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
    '--rangex',
    nargs=2,
    type=float,
    default=None,
    help='Range for x-axis (min max)',
)

parser.add_argument(
    '--rangey',
    nargs=2,
    type=float,
    default=None,
    help='Range for y-axis (min max)',
)

parser.add_argument(
    '--connect',
    action='store_true',
    help='Connect data points with lines',
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
    
    # Select the entries in the dataframe with with name matching args.names and nake a plot for each iterable
    if args.variables == None:
        ncols = 1
    else:
        ncols = len(args.variables)
    
    rprint(f"Number of unique variables for plotting: {ncols}")
    
    configs, names = prepare_import(args)
    configs = configs if configs is not None else [None]
    names = names if names is not None else [None]

    for kdx, (config, name) in enumerate(zip(configs, names)):
        rprint(f"Plotting for Config: {config}, Name: {name}")

        fig, ax = plt.subplots(nrows=1, ncols=ncols, figsize=(8 + 5*(ncols-1), 6), constrained_layout=ncols > 1)
        
        if config is not None and name is None:
            df_config = df[(df['Config'] == config)]
        
        elif config is None and name is not None:
            df_config = df[(df['Name'] == name)]
        
        elif config is not None and name is not None:
            df_config = df[(df['Config'] == config) & (df['Name'] == name)]
        
        else:
            df_config = df.copy()
        

        
        rprint(f"Dataframe entries for this config and iterable: {len(df_config)}, Unique iterable values: {df_config[args.iterable].unique()}")
        bottom = None
        variables = args.variables if args.variables is not None else [None]
        for (idx, variable), (jdx, iterable) in product(enumerate(variables), enumerate(df_config[args.iterable].unique())):
            if df_config[args.iterable].unique().size > 8 and args.reduce:
                if jdx % 2 == 1:
                    rprint(f"\tSkipping plotting for {args.iterable}={iterable} to avoid overcrowding")
                    continue
            
            if iterable is None:
                rprint("Skipping None iterable value")
                continue
            
            if ncols == 1:
                ax_current = ax
            else:
                ax_current = ax[idx]
            
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
                    rprint(f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}")
                df_iterable = df_config[(df_config["Variable"] == variable) & (df_config[args.iterable] == iterable)]
            else:
                df_iterable = df_config.copy()
                
            subset = filter_dataframe(df_iterable, args)

            subset = subset.explode(column=[args.x, args.y, "Error"] if "Error" in subset.columns else [args.x, args.y])
            if subset.empty:
                rprint(f"[yellow]Warning:[/yellow] No data for iterable {args.iterable}={iterable}, Variable={variable}. Skipping.")
                continue
                
            x = subset[args.x].astype(float).to_numpy()
            y = subset[args.y].astype(float).to_numpy()
            x_bin = x[1] - x[0] if len(x) > 1 else 1
            x_edges = np.linspace(x[0] - x_bin/2, x[-1] + x_bin/2, len(x) + 1)
            x_error = subset[f"Error"].astype(float).to_numpy() if f"Error" in subset.columns else None
            # Remove indices in x, x_error and y where any of them is NaN
            mask = ~np.isnan(x) & ~np.isnan(y)
            x = x[mask]
            y = y[mask]
            x_edges = x_edges[np.append(mask, True) | np.append(True, mask)]  # Keep edges corresponding to valid x values
            if x_error is not None:
                x_error = x_error[mask]
            
            if bottom is None:
                bottom = np.zeros(len(x)) if args.stacked else None
            
            if args.iterable == "PDG":
                rprint(f"\tMapping PDG codes to particle names for iterable {args.iterable}")
                try:
                    value_int = int(iterable)
                    value_str = particle_dict.get(value_int, str(iterable))
                    iterable = value_str
                except (ValueError, TypeError):
                    pass  # If conversion fails, keep original iterable value
            
            if args.iterable == "Plane":
                rprint(f"\tMapping Plane numbers to names for iterable {args.iterable}")
                if len(df_config[args.iterable].unique()) > 2:
                    try:
                        value_int = int(iterable)
                        value_str = plane_dict.get(value_int, str(iterable))
                        iterable = value_str
                    except (ValueError, TypeError):
                        pass
                else:
                    try:
                        value_int = int(iterable)
                        value_str = simple_plane_dict.get(value_int, str(iterable))
                        iterable = value_str
                    except (ValueError, TypeError):
                        pass
            
            if x_error is not None and args.errorx:
                rprint(f"\tPlotting {len(x)} points with error bars for {args.iterable}={iterable}, Variable={variable}")
                if args.stacked:
                    ax_current.bar(x, y, yerr=x_error, label=f"{iterable}" if idx == ncols -1 else None, bottom=bottom)
                    bottom += y
                else:
                    if args.connect:
                        ax_current.plot(x, y, linestyle='-', label=None)
                    else:
                        ax_current.errorbar(x, y, yerr=x_error, fmt='o', label=f"{iterable}" if idx == ncols -1 else None)
            
            else:
                rprint(f"\tPlotting {len(x)} points for {args.iterable}={iterable}, Variable={variable}")
                if args.stacked:
                    ax_current.bar(x, y, label=f"{iterable}" if idx == ncols -1 else None, bottom=bottom)
                    bottom += y
                else:
                    if args.connect:
                        ax_current.hist(x, bins=x_edges, weights=y, histtype='step', label=f"{iterable}" if idx == ncols -1 else None)
                    else:
                        ax_current.plot(x, y, marker='o', linestyle='None', label=f"{iterable}" if idx == ncols -1 else None)
        
        for idx, variable in enumerate(variables):
            if ncols == 1:
                ax_current = ax  
            else:
                ax_current = ax[idx]
            
            if ncols > 1:
                ax_current.set_title(f"Variable: {variable}" if variable is not None else None, fontsize=subtitlefontsize)
            
            ax_current.set_xlabel(args.labelx if args.labelx is not None else f"{args.x}")
            ax_current.set_ylabel(args.labely if args.labely is not None else f"{args.y}") if idx == 0 else None
            
            if args.y == "Efficiency" or args.labely == "Efficiency (%)":
                ax_current.set_ylim(0, 105)
                ax_current.axhline(100, color='gray', linestyle='--', linewidth=1)
            
            if args.rangex is not None:
                ax_current.set_xlim(args.rangex[0], args.rangex[1])
            if args.rangey is not None:
                ax_current.set_ylim(args.rangey[0], args.rangey[1])
            
            if args.logy:
                ax_current.semilogy()
            
            if args.logx:
                ax_current.semilogx()
            
            if args.stacked:
                if idx == ncols - 1:
                    ax_current.legend(title=args.iterable, title_fontsize=legendtitlefontsize, fontsize=legendfontsize, loc='upper left', bbox_to_anchor=(0, 1))
            else:
                ax_current.legend(title=args.iterable, title_fontsize=legendtitlefontsize, fontsize=legendfontsize) if idx == ncols - 1 else None
            
            if args.labelz is not None:
                legend = ax_current.get_legend()
                if legend is not None:
                    legend.set_title(args.labelz)

        plot_title = f"{args.datafile.replace('_', ' ')}"
        if config is not None:
            plot_title += f" - {config}"
        
        if args.save_values is not None:
            if args.select is None:
                plot_title += f" ({args.iterable}={', '.join(map(str, args.save_values))})"
            else:
                plot_title += f" ({', '.join([f'{k}={v}' for k,v in zip(args.select, args.save_values)])})"


        fig.suptitle(plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()
        
        output_file = make_name_from_args(args, kdx, prefix=None, suffix="scan.png")
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