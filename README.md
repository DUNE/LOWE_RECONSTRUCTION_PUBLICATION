# Plot And Table Macro Repository

Reusable repository structure for generating publication-quality plots and summary tables from serialized analysis outputs.

## Overview

This repository is organized around a simple workflow:

- put input datasets in [`input/data/`](input/data/)
- put plot command lists in [`input/plots/`](input/plots/)
- put table command lists in [`input/tables/`](input/tables/)
- keep executable macros in [`scripts/`](scripts/)
- keep shared library code in [`src/lib/`](src/lib/)
- collect generated artifacts in [`output/`](output/)

## Repository Layout

```text
.
├── input/
│   ├── data/
│   ├── plots/
│   └── tables/
├── output/
│   ├── plots/
│   ├── presentations/
│   └── tables/
├── scripts/
├── src/lib/
├── run_plot_scripts.py
├── run_table_scripts.py
└── setup.sh
```

## Quick Start

Set up the environment:

```bash
source setup.sh
```

This creates or reuses `.venv`, installs dependencies, makes `dunestyle` available, and runs the test suite.

## Execution Model

There are two ways to run work in this repository.

Run a single macro directly:

```bash
python3 scripts/script_compare_configuration.py --help
python3 scripts/script_mean_table.py --help
```

Run a batch of commands from a text file:

```bash
python3 run_plot_scripts.py -s my_plots
python3 run_table_scripts.py -s my_tables
```

The `-s` value selects `<name>_scripts.txt` from:

- [`input/plots/`](input/plots/) for plot batches
- [`input/tables/`](input/tables/) for table batches

For example:

- `python3 run_plot_scripts.py -s my_plots` reads `input/plots/my_plots_scripts.txt`
- `python3 run_table_scripts.py -s my_tables` reads `input/tables/my_tables_scripts.txt`

## Tutorial Workflow

### 1. Add Input Data

Store your serialized input files in [`input/data/`](input/data/). The plotting and table macros look there by default when `--datafile` is provided.

### 2. Pick A Macro Type

The repository includes several reusable macro patterns:

- [`script_iterable_scan.py`](scripts/script_iterable_scan.py): scans one iterable and overlays multiple series
- [`script_compare_configuration.py`](scripts/script_compare_configuration.py): compares configurations or names on common axes
- [`script_compare_hist1d.py`](scripts/script_compare_hist1d.py): builds 1D histograms
- [`script_compare_hist2d.py`](scripts/script_compare_hist2d.py): builds 2D histograms and density maps
- [`script_compare_reduction.py`](scripts/script_compare_reduction.py): reduces distributions into boxplots or summary scatters
- [`script_line_fit.py`](scripts/script_line_fit.py): draws fit curves and residual panels
- [`script_mean_table.py`](scripts/script_mean_table.py): creates summary tables from grouped values

### 3. Run A Single Command

Examples:

```bash
python3 scripts/script_compare_hist1d.py --datafile Example_Distribution -x Values -i Category
python3 scripts/script_compare_hist2d.py --datafile Example_Calibration -x TrueEnergy -y RecoEnergy --diagonal
python3 scripts/script_compare_configuration.py --datafile Example_Efficiency -y Efficiency -x Values -v X Y Z
python3 scripts/script_line_fit.py --datafile Example_Fit -x Values -y Density --errory --chi2
python3 scripts/script_mean_table.py --datafile Example_Table -y Efficiency --variables X Y Z -t Coordinate
```

Generated artifacts are written by default to:

- [`output/plots/`](output/plots/)
- [`output/tables/`](output/tables/)

### 4. Create A Plot Batch

Create a plain-text file in [`input/plots/`](input/plots/) named like:

```text
my_plots_scripts.txt
```

Add one command per line, for example:

```text
scripts/script_compare_hist1d.py --datafile Example_Distribution -x Values -i Category
scripts/script_compare_hist2d.py --datafile Example_Calibration -x TrueEnergy -y RecoEnergy --diagonal
scripts/script_compare_configuration.py --datafile Example_Efficiency -y Efficiency -x Values -v X Y Z
scripts/script_line_fit.py --datafile Example_Fit -x Values -y Density --errory --chi2
```

Run it with:

```bash
python3 run_plot_scripts.py -s my_plots
```

### 5. Create A Table Batch

Create a plain-text file in [`input/tables/`](input/tables/) named like:

```text
my_tables_scripts.txt
```

Add one table command per line, for example:

```text
scripts/script_mean_table.py --datafile Example_Table -y Efficiency --variables X Y Z -t Coordinate
scripts/script_mean_table.py --datafile Example_Table -y RMS --variables MethodA MethodB -t Algorithm
```

Run it with:

```bash
python3 run_table_scripts.py -s my_tables
```

## Optional External Output Paths

Named command lists can be mapped to external output directories through [`config/output_paths.json`](config/output_paths.json).

This is useful when a specific batch should write directly to another repository, note, or presentation folder.

Example structure:

```json
{
  "plots": {
    "reco": "/absolute/path/to/figures/"
  },
  "tables": {
    "summary": "/absolute/path/to/tables/"
  }
}
```

Behavior:

- `python3 run_plot_scripts.py -s reco` will automatically append `-o /absolute/path/to/figures/` to commands in `input/plots/reco_scripts.txt` unless the command already defines `-o` or `--output`
- `python3 run_table_scripts.py -s summary` works the same way for `input/tables/summary_scripts.txt`

## Notes

- The macros are intended to be run from the repository root.
- Shared utilities live in [`src/lib/`](src/lib/), while runnable macros stay in [`scripts/`](scripts/).
- Plot and table command lists are ordinary text files, so adapting the repository to a new analysis mostly means changing `input/data/` and the command lists.

## External References

To avoid duplicating upstream documentation, refer directly to:

- Official DUNE plot style: https://github.com/DUNE/dune_plot_style
- Matplotlib documentation: https://matplotlib.org/stable/
- NumPy documentation: https://numpy.org/doc/stable/
- pandas documentation: https://pandas.pydata.org/docs/

## License

See [`LICENSE`](LICENSE).
