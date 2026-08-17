#!/usr/bin/env python3


"""
Script 6: Combined Line Plot with DUNE Style
Demonstrates combined data to table conversion with custom styling
"""
# Import config from __init__.py
from _bootstrap import ensure_src_path

ensure_src_path()

from lib import *
from lib.functions import resolution, gaussian, double_gaussian, exponential_decay
from lib.selection import prepare_selection, filter_dataframe
from lib.imports import import_data
from lib.format import format_with_error
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
    type=str,
    default=None,
    help="Title for the variable on the table",
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
    "--variable_units",
    nargs="+",
    type=str,
    default=None,
    help="Units for each entry in --variables, appended to the matching column title as ' (unit)'",
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


args = parser.parse_args()


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

    df_config = subset.explode(column=cols)
    df_config = df_config.dropna(subset=cols + [args.variable_name])

    if args.rangex is not None and args.x is not None:
        df_config[args.x] = df_config[args.x].astype(float)
        print(f"Applying x-axis range filter: {args.rangex[0]} to {args.rangex[1]}")
        df_config = df_config[
            (df_config[args.x] >= args.rangex[0])
            & (df_config[args.x] <= args.rangex[1])
        ]

    # If error columns exist, combine the mean and error into a single string column. E.g. "0.95 ± 0.02" Use a precision based on the error value
    if f"{args.y}Error" not in df_config.columns:
        df_config[f"{args.y}Error"] = df_config[args.y]

    df_table = df_config.groupby(["Geometry", "Config", args.variable_name]).agg(
        {
            args.y: ["mean"],
            f"{args.y}Error": lambda x: np.sqrt(np.sum(x**2)) / len(x),
        }
    )

    df_table[args.y] = df_table.apply(
        lambda row: format_with_error(row, args=args), axis=1
    )
    df_table = df_table.drop(columns=[(f"{args.y}Error", "<lambda>")])
    df_table.columns = df_table.columns.droplevel(1)

    if args.variable_title is not None:
        df_table = df_table.rename(columns={args.y: args.variable_title})
        df_table = df_table.pivot_table(
            index=["Geometry", "Config"],
            columns=args.variable_name,
            values=[args.variable_title],
            aggfunc="first",
        )

    else:
        df_table = df_table.pivot_table(
            index=["Geometry", "Config"],
            columns=args.variable_name,
            values=[args.y],
            aggfunc="first",
        )

    # Combine the "Geometry" and "Config" index into a single index called "Configuration"
    if args.name_columns:
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

    if len(args.names) > 1 and not args.name_columns:
        df_table.index.name = "Particle"
    else:
        df_table.index.name = "Configuration"

    # Sort columns as they appear in args.variables
    df_table = df_table.reindex(columns=args.variables, level=1)

    # Sort according to the configuration column and config_order
    if len(args.configs) == 1 and len(args.names) > 1 and not args.name_columns:
        df_table = df_table.reindex(particle_order, level="Particle")
        # pass
    if (len(args.configs) > 2 and len(args.names) == 1) or (
        args.name_columns and len(args.configs) > 2
    ):
        df_table = df_table.reindex(config_order, level="Configuration")

    # Relabel column titles: capitalize/display-map names (--name_columns) and
    # append units (--variable_units), both matched against the raw pivoted
    # values so they compose regardless of order.
    unit_map = (
        dict(zip(args.variables, args.variable_units))
        if args.variable_units is not None and args.variables is not None
        else {}
    )
    if args.name_columns or unit_map:

        def _display_column(raw):
            label = raw
            if args.name_columns and isinstance(raw, str):
                label = component_dict.get(raw, raw.capitalize())
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

    def _write_latex(path):
        df_table.to_latex(
            path,
            index=False,
            column_format="l" + "c" * (df_table.shape[1] - 1),
            multicolumn_format="c",
            bold_rows=False,
            escape=False,
        )

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
            <h1>Mean Table Data</h1>
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
