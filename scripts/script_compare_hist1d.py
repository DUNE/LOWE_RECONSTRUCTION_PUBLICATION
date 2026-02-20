
#!/usr/bin/env python3

"""
Script 2: Simple Histogram Plot with DUNE Style
Demonstrates basic plotting with custom styling
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
    help='List of column names to use as variables for multiple subplots',
)

parser.add_argument(
    '-x',
    nargs='+',
    type=str,
    default=None,
    help='Column names for x-axis data',
    required=True,
)

parser.add_argument(
    '--operation',
    type=str,
    default="subtract",
    help='Operation to perform on data (e.g. mean, sum, etc.)',
)

parser.add_argument(
    '--iterable', '-i',
    type=str,
    default=None,
    help='Column name for iterable data',
)

parser.add_argument(
    '--reduce',
    action='store_true',
    help='Reduce number of lines plotted for clarity',
    default=False,
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
    help='If provided, filter plots for which according to select columns and these values'
)

parser.add_argument(
    '--bins', '-b',
    type=int,
    default=nbins,
    help='Number of bins for histogram',
)

parser.add_argument(
    '--percentile', '-p',
    nargs='+',
    type=float,
    default=[0, 100],
    help='Percentile range for axis limits (e.g. 1 99)',
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
    default="Density",
    help='Label for y-axis on plot',
    choices=['Counts', 'Density'],
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
    help='Range for x-axis values',
)

parser.add_argument(
    '--rangey',
    nargs=2,
    type=float,
    default=None,
    help='Range for y-axis values',
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
    
    print(f"Number of unique variables for plotting: {ncols}")

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
        hist_range = None
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
            elif iterable is not None and variable is not None:
                if args.debug:
                    rprint(f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}")
                df_iterable = df_config[(df_config["Variable"] == variable) & (df_config[args.iterable] == iterable)]
            else:
                df_iterable = df_config.copy()

            subset = filter_dataframe(df_iterable, args)

            if len(args.x) == 1:
                x = subset[args.x[0]].values[0]  # Convert to NumPy array

            else:
                # Prepare empty array
                x = subset[args.x[0]].values[0]
                for col in args.x[1:]:
                    if args.operation in ["mean", "sum"]:
                        x = np.add(x, np.array(subset[col].values[0]))
                    elif args.operation in ["subtract", "relative"]:
                        x = np.subtract(x, np.array(subset[col].values[0]))
                    elif args.operation == "rms":
                        x = np.add(x**2, np.array(subset[col].values[0])**2)
                
                if args.operation == "mean":
                    x = x / len(args.x)
                elif args.operation == "relative":
                    x = x / np.array(subset[col].values[0])
                elif args.operation == "rms":
                    x = np.sqrt(x / len(args.x))
            # print(x)
            if hist_range is None:
                if args.percentile is None:
                    hist_range = [np.min(x), np.max(x)]
                else:
                    hist_range = [np.percentile(x, args.percentile[0]), np.percentile(x, args.percentile[1])] 
            
            # print(hist_range)
            ax_current.hist(x, histtype='step', label=f"{iterable}", bins=args.bins, range=hist_range, density=args.labely == "Density")

        for idx, variable in enumerate(variables):
            if ncols == 1:
                ax_current = ax
            
            else:
                ax_current = ax[idx]
                
            if ncols > 1:
                ax_current.set_title(f"Variable: {variable}" if variable is not None else None, fontsize=subtitlefontsize)

            ax_current.set_xlabel(args.labelx if args.labelx is not None else f"{args.x}")
            ax_current.set_ylabel(args.labely if args.labely is not None else f"{args.y}") if idx == 0 else None
            
            if args.rangex is None:
                ax.set_xlim(hist_range)
            else:
                ax_current.set_xlim(args.rangex[0], args.rangex[1])
            
            if args.rangey is not None:
                ax_current.set_ylim(args.rangey[0], args.rangey[1])
            
            if args.logy:
                ax_current.semilogy()
            
            if args.logx:
                ax_current.semilogx()

            ax_current.legend(title=args.iterable, title_fontsize=legendtitlefontsize, fontsize=legendfontsize) if idx == ncols - 1 else None
        # Set title
        plot_title = f"{args.datafile.replace('_', ' ')}"
        if config is not None:
            plot_title += f" - {config}"
        
        if args.select is not None:
            if args.save_values is not None:
                for save_key, save_value in zip(args.select, args.save_values):
                    plot_title += f" - {save_key}: {save_value}"
            else:
                plot_title += f" - {variable}"


        fig.suptitle(plot_title, fontsize=titlefontsize)
        # dunestyle.WIP()

        output_file = make_name_from_args(args, kdx, prefix=None, suffix="hist1d.png")
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