import os

from .imports import prepare_import
from .plot import apply_common_figure_margins
from typing import Optional


def make_name_from_args(
    args,
    idx: Optional[int] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
):
    """
    Generate an export name based on provided arguments.

    Parameters:
    args : argparse.Namespace
        The arguments namespace containing relevant attributes.
    prefix : str, optional
        A prefix to add to the export name.
    suffix : str, optional
        A suffix to add to the export name.

    Returns:
    str
        The generated export name.
    """
    # Each part is tagged essential=True if it must never be dropped when the
    # name has to be shortened. datafile/configs/names are what actually
    # identify a run, so they stay; everything else (variables, select,
    # style flags, ...) is expendable filler that can be trimmed.
    name_parts = []

    def add(text, essential=False):
        if text:
            name_parts.append((text, essential))

    if prefix is not None:
        add(prefix, essential=True)

    if hasattr(args, "datafile"):
        add(args.datafile, essential=True)

    show_configs = getattr(args, "show_configs", None)

    if hasattr(args, "configs") and args.configs:
        if args.configs is not None:
            if idx is not None and 0 <= idx < len(args.configs):
                add(args.configs[idx], essential=True)
            elif show_configs:
                # Only the configs actually drawn (--show_configs) identify
                # this plot; configs loaded solely for --operation/--combine
                # don't need to be spelled out in the filename.
                shown = [c for c in args.configs if c in show_configs]
                add("_".join(shown) if shown else "_".join(args.configs), essential=True)
            else:
                add("_".join(args.configs), essential=True)

    if hasattr(args, "project") and args.project:
        for proj in args.project:
            if proj:
                add(proj)

    if hasattr(args, "names") and args.names:
        if args.names is not None:
            if idx is not None and 0 <= idx < len(args.names):
                add(args.names[idx], essential=True)
            else:
                add("_".join(args.names), essential=True)

    if hasattr(args, "x") and args.x and isinstance(args.x, str):
        add(args.x)

    if hasattr(args, "y") and args.y and isinstance(args.y, str):
        add(args.y)

    if hasattr(args, "z") and args.z and isinstance(args.z, str):
        add(args.z)

    if hasattr(args, "errory") and args.errory:
        add("error")

    if hasattr(args, "variables") and args.variables:
        add("_".join(args.variables))

    if hasattr(args, "iterable") and args.iterable:
        if (hasattr(args, "select") and args.select is None) and (
            hasattr(args, "save_values") and args.save_values is not None
        ):
            # Join each iterable item with its corresponding save-values item
            iterable_parts = []
            for val in args.save_values:
                if val:  # Check if val has content
                    iterable_parts.append(f"{val}")
            if iterable_parts:  # Only add if iterable_parts is not empty
                add("_".join(iterable_parts))
        else:
            if args.iterable:  # Check if args.iterable has content
                add(f"{args.iterable}")

    if hasattr(args, "select") and args.select:
        if hasattr(args, "save_values") and args.save_values:
            # Join each select item with its corresponding save-values item
            select_parts = []
            for sel, val in zip(args.select, args.save_values):
                if sel and val:  # Check if both sel and val have content
                    select_parts.append(f"{sel}_{val}")
            if select_parts:  # Only add if select_parts is not empty
                add("_".join(select_parts))
        else:
            if args.select:  # Check if args.select has content
                add("_".join(args.select))

    if hasattr(args, "operation") and args.operation:
        add(str(args.operation))

    if hasattr(args, "lower_series_data") and args.lower_series_data:
        add(str(args.lower_series_data))

    if hasattr(args, "lower_series") and args.lower_series:
        add(str(args.lower_series))

    if hasattr(args, "lower_plot_style") and args.lower_plot_style:
        add(str(args.lower_plot_style))

    if hasattr(args, "lower_series_density") and args.lower_series_density:
        add("density")

    if hasattr(args, "logx") and args.logx:
        add("logx")
    if hasattr(args, "logy") and args.logy:
        add("logy")
    if hasattr(args, "logz") and args.logz:
        add("logz")
    if hasattr(args, "no_lower_plot") and args.no_lower_plot:
        add("no_lower")
    if hasattr(args, "invert_style") and args.invert_style:
        add("invert_style")

    MAX_LEN = 150
    suffix_part = ("_" + suffix) if suffix is not None else ""

    def joined(drop):
        return "_".join(text for i, (text, _) in enumerate(name_parts) if i not in drop)

    dropped = set()
    if len(joined(dropped)) + len(suffix_part) > MAX_LEN:
        # Drop the biggest non-essential parts first (--variables is usually
        # the main offender) until the name fits, keeping datafile/configs/
        # names intact so runs that only differ in those stay distinct.
        droppable_by_size = sorted(
            (i for i, (_, essential) in enumerate(name_parts) if not essential),
            key=lambda i: -len(name_parts[i][0]),
        )
        for i in droppable_by_size:
            if len(joined(dropped)) + len(suffix_part) <= MAX_LEN:
                break
            dropped.add(i)

    export_name = joined(dropped)
    if len(export_name) + len(suffix_part) > MAX_LEN:
        # Even the essential parts alone don't fit; hard-truncate them so the
        # suffix (which carries the file extension, e.g. "table.tex") always
        # survives intact.
        budget = max(MAX_LEN - len(suffix_part), 0)
        export_name = export_name[:budget].rstrip("_")

    if suffix is not None:
        export_name = export_name + "_" + suffix

    export_name = export_name.replace(" ", "_").replace("-", "_").replace("#", "n")
    return export_name.lower()


def export_plot(fig, plot_name, output_dir="plots"):
    """
    Export the given plot figure to a file.

    Parameters:
    fig : matplotlib.figure.Figure
        The figure object to be saved.
    plot_name : str
        The name of the plot file (without extension).
    output_dir : str
        The directory where the plot will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plot_path = os.path.join(output_dir, f"{plot_name}.png")
    apply_common_figure_margins(fig)
    fig.savefig(plot_path, dpi=300)
    print(f"Plot saved to {'/'+plot_path}")


def export_table(df, table_name, output_dir="tables"):
    """
    Export the given DataFrame to a CSV file.

    Parameters:
    df : pandas.DataFrame
        The DataFrame to be saved.
    table_name : str
        The name of the table file (without extension).
    output_dir : str
        The directory where the table will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    table_path = os.path.join(output_dir, f"{table_name}.csv")
    df.to_csv(table_path, index=False)
    print(f"Table saved to {table_path}")


def save_table_to_paths(write_func, output_arg, output_file, default_output_dir, rprint_func=None, subfolder=None):
    """
    Save a table to one or multiple output paths.

    Handles both single path (str) and multiple paths (list) via args.output.
    If output_arg is None, saves to default_output_dir.

    Parameters:
    write_func : callable
        Function taking a full file path and writing the table contents to it.
    output_arg : str, list, or None
        Output path(s) from args.output (can be str for single, list for multiple, or None)
    output_file : str
        The filename for the output
    default_output_dir : str
        Default directory to use if output_arg is None
    rprint_func : callable, optional
        Rich print function for logging (if None, uses print)
    subfolder : str, optional
        Subfolder appended to each output path (default or explicit) before saving
    """
    if rprint_func is None:
        rprint_func = print

    # Convert output_arg to a list of paths
    output_paths = []
    if output_arg is not None:
        if isinstance(output_arg, list):
            output_paths = output_arg
        else:
            output_paths = [output_arg]

    # Save to each output path
    if output_paths:
        for output_path in output_paths:
            output_dir = os.path.dirname(output_path) if os.path.splitext(output_path)[1] else output_path
            if subfolder:
                output_dir = os.path.join(output_dir, subfolder)
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(output_dir, output_file)
            write_func(full_path)
            rprint_func(f"[green]Success:[/green] Table saved to:\n{full_path}")
    else:
        # Use default output directory
        output_dir = os.path.join(default_output_dir, subfolder) if subfolder else default_output_dir
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, output_file)
        write_func(full_path)
        rprint_func(f"Table saved to {full_path}")


def save_figure_to_paths(fig, output_arg, output_file, default_output_dir, rprint_func=None, subfolder=None):
    """
    Save a figure to one or multiple output paths.

    Handles both single path (str) and multiple paths (list) via args.output.
    If output_arg is None, saves to default_output_dir.

    Parameters:
    fig : matplotlib.figure.Figure
        The figure to save
    output_arg : str, list, or None
        Output path(s) from args.output (can be str for single, list for multiple, or None)
    output_file : str
        The filename for the output
    default_output_dir : str
        Default directory to use if output_arg is None
    rprint_func : callable, optional
        Rich print function for logging (if None, uses print)
    subfolder : str, optional
        Subfolder appended to each output path (default or explicit) before saving
    """
    import os

    if rprint_func is None:
        rprint_func = print

    # Convert output_arg to a list of paths
    output_paths = []
    if output_arg is not None:
        if isinstance(output_arg, list):
            output_paths = output_arg
        else:
            output_paths = [output_arg]

    # Save to each output path
    if output_paths:
        for output_path in output_paths:
            output_dir = os.path.dirname(output_path) if os.path.splitext(output_path)[1] else output_path
            if subfolder:
                output_dir = os.path.join(output_dir, subfolder)
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(output_dir, output_file)
            fig.savefig(full_path)
            rprint_func(f"[green]Success:[/green] Plot saved to:\n{full_path}")
    else:
        # Use default output directory
        output_dir = os.path.join(default_output_dir, subfolder) if subfolder else default_output_dir
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, output_file)
        fig.savefig(full_path)
        rprint_func(f"[green]Success:[/green] Plot saved to:\n{os.path.join(output_dir.split('..')[1], output_file)[1:]}")
