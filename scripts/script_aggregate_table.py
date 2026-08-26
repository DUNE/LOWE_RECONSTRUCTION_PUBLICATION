#!/usr/bin/env python3


"""
Script 6: Combined Line Plot with DUNE Style
Demonstrates combined data to table conversion with custom styling
"""
# Import config from __init__.py
import html

from _bootstrap import ensure_src_path

ensure_src_path()

from lib import *
from lib.functions import resolution, gaussian, double_gaussian, exponential_decay
from lib.selection import prepare_selection, filter_dataframe
from lib.imports import import_data
from lib.format import format_with_error, format_value
from lib.exports import make_name_from_args, save_table_to_paths
from lib.plot import apply_note_to_figure
from common_args import add_common_args

# Import with args parser
parser = argparse.ArgumentParser(
    description="Plot the energy distribution of the particles"
)

add_common_args(
    parser,
    [
        "datafile",
        "configs",
        "names",
        "variables",
        "iterable",
        "select",
        "save_values",
        "remove_value",
        "x",
        "rangex",
        "y",
        "output",
        "note",
        "debug",
    ],
    overrides={
        "datafile": {"default": "Vertex_Reconstruction_Efficiency"},
        "configs": {
            "default": [
                "hd_1x2x6",
                "hd_1x2x6_centralAPA",
                "hd_1x2x6_lateralAPA",
                "vd_1x8x14_3view_30deg",
                "vd_1x8x14_3view_30deg_nominal",
            ]
        },
        "names": {"flags": ["--names"]},
        "variables": {"help": "Filter variable name"},
        "output": {"help": "Output filepath for the plot"},
        "debug": {"flags": ["--debug"]},
    },
)

parser.add_argument(
    "--variable_title",
    "-t",
    "--labely",
    type=str,
    default=None,
    help="Display name substituted for the raw --y column name in the table "
    "(e.g. -y Percentage --labely 'Purity' shows 'Purity' as the column group "
    "header instead of 'Percentage')",
)

parser.add_argument(
    "--variable_name",
    "-n",
    type=str,
    default=None,
    help="Column used as the pivot for table columns (default: 'Variable', or "
    "'Particle' when --name_columns is set)",
)

parser.add_argument(
    "--name_columns",
    action="store_true",
    help="Layout the table as rows=configs x columns=names (derived from "
    "--names) instead of collapsing configs into name rows",
)

parser.add_argument(
    "--row_name",
    "-r",
    type=str,
    default=None,
    help="Extra column added to the row index alongside Geometry/Config (e.g. "
    "'Stage'), so it can be combined with --variable_name for the columns "
    "(e.g. --row_name Stage --variable_name Component)",
)

parser.add_argument(
    "--row_name_mapping",
    type=str,
    default=None,
    help="Optional mapping dictionary name from plot_params mappings (e.g. "
    "'stage_dict') used to rename the --row_name values displayed in the "
    "table's row labels",
)

parser.add_argument(
    "--drop_config",
    action="store_true",
    help="Drop Geometry/Config from the row index entirely, so rows are keyed "
    "only by --row_name (e.g. one row per Stage, with all samples' values "
    "spread across the --variable_name columns instead of one row per "
    "sample). Only meaningful for a single Geometry/Config combination.",
)


parser.add_argument(
    "--variable_units",
    nargs="+",
    type=str,
    default=None,
    help="Units for each entry in --variables, appended to the matching column title as ' (unit)'",
)

parser.add_argument(
    "--variable_mapping",
    type=str,
    default=None,
    help="Optional mapping dictionary name from plot_params mappings used to "
    "rename and reorder the --variable_name column titles (mirrors "
    "--row_name_mapping, but for columns instead of rows)",
)

parser.add_argument(
    "--emph",
    type=int,
    default=None,
    help="Index of the columns to emphasize in the table",
),

parser.add_argument(
    "--it",
    type=int,
    default=None,
    help="Index of the columns to italicize in the table",
),

parser.add_argument(
    "--html",
    action="store_true",
    help="Also export the table as an HTML file (disabled by default)",
)

parser.add_argument(
    "--title",
    type=str,
    default=None,
    help="Title for the table: used as the HTML export's heading, and as the "
    "LaTeX caption when --caption isn't given separately",
)

parser.add_argument(
    "--caption",
    type=str,
    default=None,
    help="Caption inserted into the LaTeX output, wrapping the tabular in a "
    "\\begin{table*}[t] ... \\end{table*} environment. Defaults to --title "
    "when not given separately.",
)

parser.add_argument(
    "--caption_file",
    type=str,
    default=None,
    help="Read the LaTeX caption from a text file instead of passing it inline "
    "with --caption (handy for long captions). Accepts either a direct path "
    "or a bare name resolved against input/captions/<name>.txt. Ignored if "
    "--caption is also given.",
)

parser.add_argument(
    "--no_table",
    action="store_true",
    help="Trim the \\begin{table*}[t]/\\end{table*} lines from the LaTeX "
    "export, leaving the tabular (and caption/title row, if any) to be "
    "wrapped in your own table environment. Adds '_no_table' to the filename.",
)

parser.add_argument(
    "--no_tabular",
    action="store_true",
    help="Like --no_table, but also trims the \\begin{tabular}/\\end{tabular} "
    "lines, leaving just the raw rows to be embedded in an existing tabular. "
    "Adds '_no_tabular' to the filename.",
)

parser.add_argument(
    "--operation",
    choices=["mean", "sum"],
    default="mean",
    help="Aggregation operation applied to --y within each group (default: mean)",
)

parser.add_argument(
    "--scientific",
    action="store_true",
    help="Always format table values in scientific notation (e.g. 1.2e-03), "
    "instead of only when a --scientific_threshold is crossed",
)

parser.add_argument(
    "--scientific_threshold_low",
    type=float,
    default=None,
    help="Automatically switch a value to scientific notation when its "
    "magnitude falls below this threshold",
)

parser.add_argument(
    "--scientific_threshold_high",
    type=float,
    default=None,
    help="Automatically switch a value to scientific notation when its "
    "magnitude rises above this threshold",
)

parser.add_argument(
    "--compact_scientific",
    action="store_true",
    help="Use compact PDG/CODATA-style parenthetical notation for scientific "
    "values (e.g. '1.35(6)e-08') instead of the longer 'mean ± error' form",
)

parser.add_argument(
    "--no_error",
    action="store_true",
    help="Show only the aggregated value, without a propagated error/uncertainty, "
    "even when the data has a matching *Error column to draw one from",
)

parser.add_argument(
    "--multiply",
    type=float,
    default=None,
    help="Multiply every --y value (and its error, if present) by this factor "
    "before aggregating/displaying - e.g. for unit conversion or rescaling",
)

parser.add_argument(
    "--threshold",
    type=float,
    default=1e-3,
    help="Values with magnitude below this are hidden as '---' rather than "
    "formatted (default: 1e-3). Lower it (e.g. to 0) to actually display "
    "small values instead of masking them - useful together with "
    "--scientific_threshold_low.",
)


args = parser.parse_args()


def _resolve_caption_file(value):
    """
    Read caption text from --caption_file. `value` may be a direct path
    (absolute or relative to the current directory) or a bare name resolved
    against input/captions/<name>.txt.
    """
    candidates = [value]
    if not value.endswith(".txt"):
        candidates.append(f"{value}.txt")

    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate, "r") as f:
                return f.read().strip()

    captions_dir = os.path.join(os.path.dirname(__file__), "..", "input", "captions")
    for candidate in candidates:
        path = os.path.join(captions_dir, os.path.basename(candidate))
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()

    print(f"Caption file not found: {value}")
    return None


def _trim_environment_lines(text, no_table, no_tabular):
    """
    Strip \\begin{table*}[t]/\\end{table*} lines (--no_table), and additionally
    \\begin{tabular}/\\end{tabular} lines (--no_tabular), from LaTeX table
    output. Everything else (rules, rows, caption, title row) is left as-is.
    """
    lines = text.splitlines(keepends=True)
    kept = []
    for line in lines:
        stripped = line.strip()
        if no_table and (
            stripped.startswith("\\begin{table") or stripped.startswith("\\end{table")
        ):
            continue
        if no_tabular and (
            stripped.startswith("\\begin{tabular") or stripped.startswith("\\end{tabular")
        ):
            continue
        kept.append(line)
    return "".join(kept)


def main():
    """
    Main function to process simulation configurations, load data files,
    and generate tables based on the provided arguments.
    """
    if args.variable_name is None:
        args.variable_name = "Particle" if args.name_columns else "Variable"

    df = import_data(args)

    # Check if the DataFrame is empty
    if df.empty:
        print("No data to plot. Exiting.")
        return

    # Derive the "Geometry" column from the config name if it isn't already present
    if "Geometry" not in df.columns:
        df["Geometry"] = df["Config"].str.split("_").str[0]

    # Capitalize all letters in df["Geometry"]
    df["Geometry"] = df["Geometry"].str.upper()

    # Substitute the names in df["Config"] to be more readable with the config_dict
    if args.name_columns:
        # Keep Config as the detector configuration; derive Particle from Name
        df["Config"] = df["Config"].map(lambda x: config_dict.get(x, x))
        df["Particle"] = df["Name"].str.split("_").str[0]
    elif len(args.names) == 1:
        df["Config"] = df["Config"].map(lambda x: config_dict.get(x, x))
    else:
        df["Config"] = df["Name"].str.split("_").str[0]
        df["Config"] = df["Config"].map(lambda x: particle_dict.get(x, x))

    # Set default variable if none are provided
    if args.variables is None:
        if args.name_columns:
            args.variables = sorted(df[args.variable_name].unique().tolist())
        else:
            args.variables = [""]
            df[args.variable_name] = ""

    subset = filter_dataframe(df, args)
    # variables = args.variables if args.variables is not None else [None]
    # iterables = this_df[args.iterable].unique() if args.iterable is not None else [None]

    # for kdx, ((idx, variable), (jdx, iterable)) in enumerate(
    #     product(
    #         enumerate(variables),
    #         enumerate(iterables) if args.iterable is not None else enumerate([None]),
    #     )
    # ):

    #     # Skip if the filtered DataFrame is empty
    #     if this_df.empty:
    #         continue

    #     if variable is not None and iterable is not None:
    #         # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable} and iterable: {iterable}")
    #         subset = this_df[
    #             (this_df["Variable"] == variable) & (this_df[args.iterable] == iterable)
    #         ]
    #     elif variable is not None and iterable is None:
    #         # rprint(f"[blue]Info:[/blue] Filtering for variable: {variable}")
    #         subset = this_df[(this_df["Variable"] == variable)]
    #     elif iterable is not None and variable is None:
    #         # rprint(f"[blue]Info:[/blue] Filtering for iterable: {iterable}")
    #         subset = this_df[(this_df[args.iterable] == iterable)]
    #     else:
    #         subset = this_df.copy()

    cols = [args.x, args.y] if args.x is not None else [args.y]
    if f"{args.y}Error" in subset.columns:
        cols.append(f"{args.y}Error")
    if f"{args.x}Error" in subset.columns:
        cols.append(f"{args.x}Error")

    if args.drop_config:
        row_index = [args.row_name] if args.row_name else []
    else:
        row_index = ["Geometry", "Config"] + ([args.row_name] if args.row_name else [])
    # True whenever the row index deviates from the classic Geometry/Config
    # layout, so the collapsing/relabeling logic below (which assumes exactly
    # that layout) needs to be skipped.
    custom_rows = bool(args.row_name) or args.drop_config

    df_config = subset.explode(column=cols)
    df_config = df_config.dropna(subset=cols + [args.variable_name])

    if args.rangex is not None and args.x is not None:
        df_config[args.x] = df_config[args.x].astype(float)
        print(f"Applying x-axis range filter: {args.rangex[0]} to {args.rangex[1]}")
        df_config = df_config[
            (df_config[args.x] >= args.rangex[0])
            & (df_config[args.x] <= args.rangex[1])
        ]

    if args.multiply is not None:
        df_config[args.y] = df_config[args.y] * args.multiply
        if f"{args.y}Error" in df_config.columns:
            df_config[f"{args.y}Error"] = df_config[f"{args.y}Error"] * args.multiply

    # If a real error column exists, combine the aggregate and its propagated
    # error into a single string column. E.g. "0.95 ± 0.02". Without one, there
    # is no uncertainty to report, so just format the aggregated value alone
    # rather than inventing an error from the values themselves.
    has_error_column = f"{args.y}Error" in df_config.columns and not args.no_error

    if has_error_column:
        if args.operation == "sum":
            error_agg = lambda x: np.sqrt(np.sum(x**2))
        else:
            error_agg = lambda x: np.sqrt(np.sum(x**2)) / len(x)

        df_table = df_config.groupby(row_index + [args.variable_name]).agg(
            {
                args.y: [args.operation],
                f"{args.y}Error": error_agg,
            }
        )

        df_table[args.y] = df_table.apply(
            lambda row: format_with_error(row, args=args), axis=1
        )
        df_table = df_table.drop(columns=[(f"{args.y}Error", "<lambda>")])
        df_table.columns = df_table.columns.droplevel(1)
    else:
        df_table = df_config.groupby(row_index + [args.variable_name]).agg(
            {args.y: [args.operation]}
        )

        df_table[args.y] = df_table.apply(
            lambda row: format_value(row, args=args), axis=1
        )
        df_table.columns = df_table.columns.droplevel(1)

    if args.variable_title is not None:
        df_table = df_table.rename(columns={args.y: args.variable_title})
        df_table = df_table.pivot_table(
            index=row_index,
            columns=args.variable_name,
            values=[args.variable_title],
            aggfunc="first",
        )

    else:
        df_table = df_table.pivot_table(
            index=row_index,
            columns=args.variable_name,
            values=[args.y],
            aggfunc="first",
        )

    # Combine the "Geometry" and "Config" index into a single index called "Configuration".
    # Skipped for a custom row layout (--row_name / --drop_config): the row
    # index is kept as-is instead of being folded into a single label.
    if custom_rows:
        pass
    elif args.name_columns:
        if len(args.configs) <= 2:
            df_table.index = df_table.index.map(lambda x: f"{x[1]}")
        else:
            df_table.index = df_table.index.map(lambda x: f"{x[0]} {x[1]}")
    elif len(args.configs) <= 2 and len(args.names) == 1:
        df_table.index = df_table.index.map(lambda x: f"{x[0]}")
    elif len(args.configs) > 2 and len(args.names) == 1:
        df_table.index = df_table.index.map(lambda x: f"{x[0]} {x[1]}")
    elif len(args.configs) == 1 and len(args.names) > 1:
        df_table.index = df_table.index.map(lambda x: f"{x[1]}")
    else:
        df_table.index = df_table.index.map(lambda x: f"{x[0]} {x[1]}")

    if custom_rows:
        pass
    elif len(args.names) > 1 and not args.name_columns:
        df_table.index.name = "Particle"
    else:
        df_table.index.name = "Configuration"

    # Apply an optional display mapping to --row_name values (e.g. renaming
    # cutflow stage names), looked up by name from plot_params mappings. Rows
    # are also reordered to match the mapping's key order; any raw value not
    # covered by the mapping keeps its relative position, appended after the
    # mapped ones instead of being dropped.
    if args.row_name and args.row_name_mapping:
        row_mapping = get_mapping_dict(args.row_name_mapping) or {}
        is_multi = isinstance(df_table.index, pd.MultiIndex)
        raw_values = (
            df_table.index.get_level_values(args.row_name) if is_multi else df_table.index
        )
        present = list(dict.fromkeys(raw_values))
        ordered = [v for v in row_mapping if v in present] + [
            v for v in present if v not in row_mapping
        ]
        if is_multi:
            df_table = df_table.reindex(ordered, level=args.row_name)
            df_table = df_table.rename(index=row_mapping, level=args.row_name)
        else:
            df_table = df_table.reindex(ordered)
            df_table = df_table.rename(index=row_mapping)

    # Sort columns as they appear in args.variables
    df_table = df_table.reindex(columns=args.variables, level=1)

    # Optional mapping dictionary name from plot_params mappings used to
    # reorder the columns to match the mapping's key order (mirrors
    # --row_name_mapping); any raw value not covered by the mapping keeps
    # its relative position, appended after the mapped ones.
    variable_mapping = get_mapping_dict(args.variable_mapping) or {} if args.variable_mapping else {}
    if variable_mapping:
        present_cols = list(dict.fromkeys(df_table.columns.get_level_values(1)))
        ordered_cols = [v for v in variable_mapping if v in present_cols] + [
            v for v in present_cols if v not in variable_mapping
        ]
        df_table = df_table.reindex(columns=ordered_cols, level=1)

    # Sort according to the configuration column and config_order
    if custom_rows:
        pass
    elif len(args.configs) == 1 and len(args.names) > 1 and not args.name_columns:
        df_table = df_table.reindex(particle_order, level="Particle")
        # pass
    if not custom_rows and (
        (len(args.configs) > 2 and len(args.names) == 1)
        or (args.name_columns and len(args.configs) > 2)
    ):
        df_table = df_table.reindex(config_order, level="Configuration")

    # Relabel column titles: --variable_mapping takes priority, then the
    # capitalize/display-map names from --name_columns, then units are
    # appended (--variable_units) on top - all matched against the raw
    # pivoted values so they compose regardless of order.
    unit_map = (
        dict(zip(args.variables, args.variable_units))
        if args.variable_units is not None and args.variables is not None
        else {}
    )
    if variable_mapping or args.name_columns or unit_map:

        def _display_column(raw):
            if raw in variable_mapping:
                label = variable_mapping[raw]
            elif args.name_columns and isinstance(raw, str):
                label = component_dict.get(raw, raw.capitalize())
            else:
                label = raw
            unit = unit_map.get(raw)
            return f"{label} ({unit})" if unit else label

        df_table.columns = pd.MultiIndex.from_tuples(
            [(col[0], _display_column(col[1])) for col in df_table.columns]
        )

    # Drop rows with all NaN values
    df_table = df_table.dropna(how="all")

    # Make the "Configuration" index a column and drop the index
    df_table = df_table.reset_index()

    # Don't print the row index
    print(df_table.to_string(index=False))

    default_output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "tables")

    # Italicize the specified column
    if args.it is not None and 0 <= args.it < df_table.shape[1]:
        df_table.iloc[:, args.it] = "\\textit{" + df_table.iloc[:, args.it] + "}"
    # Emphasize the first column
    if args.emph is not None and 0 <= args.emph < df_table.shape[1]:
        df_table.iloc[:, args.emph] = "\\emph{" + df_table.iloc[:, args.emph] + "}"

    output_filename = make_name_from_args(args, prefix=None, suffix="table.tex")
    if args.no_tabular:
        output_filename = output_filename.replace(".tex", "_no_tabular.tex")
    elif args.no_table:
        output_filename = output_filename.replace(".tex", "_no_table.tex")

    if args.caption is not None:
        caption = args.caption
    elif args.caption_file is not None:
        caption = _resolve_caption_file(args.caption_file)
        if caption is None:
            caption = args.title
    else:
        caption = args.title

    def _write_latex(path):
        tabular = df_table.to_latex(
            index=False,
            column_format="l" + "c" * (df_table.shape[1] - 1),
            multicolumn_format="c",
            bold_rows=False,
            escape=False,
        )
        if args.title:
            # Spanning header row across the full table width, right below \toprule.
            title_row = (
                f"\\multicolumn{{{df_table.shape[1]}}}{{c}}{{{args.title}}} \\\\\n"
                "\\midrule\n"
            )
            tabular = tabular.replace("\\toprule\n", "\\toprule\n" + title_row, 1)
        if caption is not None:
            tabular = (
                "\\begin{table*}[t]\n"
                f"{tabular}"
                f"\\caption{{{caption}}}\n"
                "\\end{table*}\n"
            )
        if args.no_table or args.no_tabular:
            tabular = _trim_environment_lines(
                tabular, no_table=True, no_tabular=args.no_tabular
            )
        with open(path, "w") as f:
            f.write(tabular)

    save_table_to_paths(_write_latex, args.output, output_filename, default_output_dir)

    # Export to HTML only if explicitly requested
    if args.html:
        output_html_filename = make_name_from_args(args, prefix=None, suffix="table.html")

        # Create a styled HTML table
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                table {
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                th {
                    background-color: #4CAF50;
                    color: white;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                tr:hover {
                    background-color: #ddd;
                }
                td:first-child, th:first-child {
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <h1>""" + html.escape(args.title or "Table") + """</h1>
        """ + df_table.to_html(index=False, border=0) + """
        </body>
        </html>
        """

        def _write_html(path):
            with open(path, "w") as f:
                f.write(html_content)

        save_table_to_paths(_write_html, args.output, output_html_filename, default_output_dir)


if __name__ == "__main__":
    main()
