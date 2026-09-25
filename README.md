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
python3 scripts/script_aggregate_table.py --help
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

SOLAR study results are pulled by `scripts/sync_solar_data.sh` (driven by the study registry in [`src/lib/solar_studies.py`](src/lib/solar_studies.py)) into two places: the reference copy (`truncated/default` results, plus the truncated cutflow and weighted-distribution files) flat in `input/data/`, and every `(folder, label)` pair under `input/data/studies/{folder}/{label}/` (`folder` is the background model `truncated|nominal|reduced`, `label` the study, e.g. `charge_Q100`). Loaders resolve three spellings against that tree: `--path studies --datafile DayNight_Exposure_charge_Q100` (label as a datafile suffix), `--path studies/truncated/charge_Q100 --datafile DayNight_Exposure`, and `--path studies/nominal --datafile DayNight_Exposure` (the `default` label of that folder). Every loaded frame carries `Study`, `_Folder` and `_Label` columns; Sensitivity frames that mix different `NHits/OpHits/AdjCl` working points trigger a warning (and a `[cuts differ]` legend marker in `script_compare_contour.py`). `input/plots/results_scripts.txt` (`./scripts/update_plots.sh -s results`) holds the plot commands for the Counts, Exposure, Contours, Cutflow and Weighted_Distributions_Fiducial families.

### 2. Pick A Macro Type

The repository includes several reusable macro patterns:

- [`script_iterable_scan.py`](scripts/script_iterable_scan.py): scans one iterable and overlays multiple series
- [`script_compare_configuration.py`](scripts/script_compare_configuration.py): compares configurations or names on common axes
- [`script_compare_hist1d.py`](scripts/script_compare_hist1d.py): builds 1D histograms
- [`script_compare_hist2d.py`](scripts/script_compare_hist2d.py): builds 2D histograms and density maps
- [`script_compare_reduction.py`](scripts/script_compare_reduction.py): reduces distributions into boxplots or summary scatters
- [`script_line_fit.py`](scripts/script_line_fit.py): draws fit curves and residual panels
- [`script_aggregate_table.py`](scripts/script_aggregate_table.py): creates summary tables from grouped values

### 3. Run A Single Command

Examples:

```bash
python3 scripts/script_compare_hist1d.py --datafile Example_Distribution -x Values -i Category
python3 scripts/script_compare_hist2d.py --datafile Example_Calibration -x TrueEnergy -y RecoEnergy --diagonal
python3 scripts/script_compare_configuration.py --datafile Example_Efficiency -y Efficiency -x Values -v X Y Z
python3 scripts/script_line_fit.py --datafile Example_Fit -x Values -y Density --errory --chi2
python3 scripts/script_aggregate_table.py --datafile Example_Table -y Efficiency --variables X Y Z -t Coordinate
```

For [`script_compare_configuration.py`](scripts/script_compare_configuration.py), you can group multiple input lines into combined lines with:

- `--combine <criterion>` where criterion is `Geometry`, `Config`, or `Name`
- `--combine_operation <mode>` where mode is `mean`, `sum`, or `squared_sum`

Example (combine two config families into summary lines):

```bash
python3 scripts/script_compare_configuration.py --datafile Example_Efficiency --configs config_a config_b -y Efficiency -x Coordinate -v X --combine Geometry --combine_operation sum
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
scripts/script_aggregate_table.py --datafile Example_Table -y Efficiency --variables X Y Z -t Coordinate
scripts/script_aggregate_table.py --datafile Example_Table -y RMS --variables MethodA MethodB -t Algorithm
```

Run it with:

```bash
python3 run_table_scripts.py -s my_tables
```

## Truth-position study (thesis section on position information)

Figures and tables from the SOLAR `truth_position` export (`export_repo/`: 80 pickles `{config}_all_{Kind}.pkl`, `README.md`, `meta.json`), built with the existing macros only.

```bash
./scripts/sync_solar_data.sh --truth-position          # fetch the export into input/data/truth_position/ (gitignored *.pkl)
python scripts/truth_position_check.py                 # reference numbers, four-face sums and file structure must reproduce
python run_plot_scripts.py -s truth_position           # input/plots/truth_position_scripts.txt  -> output/plots/truth_position/ (PNG)
python run_table_scripts.py -s truth_position          # input/tables/truth_position_scripts.txt -> output/tables/ (.tex)
```

The plot list calls `script_iterable_scan.py` and `script_compare_hist1d.py`; the table list calls `script_aggregate_table.py`.
Table captions and the caveats (raw weights only, definition of the truth pipeline, radiological MC counts, truth X outside the VD box,
off-scale medians, HD central statistics) are in `input/captions/truth_position_*.txt`. The colours of the species and faces are the
mappings `truth_species_color` and `truth_face_color` in `config/plot_params.json`. A description of every generated file for other
agents is in [`docs/truth_position_outputs.md`](docs/truth_position_outputs.md).

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

- Matplotlib documentation: https://matplotlib.org/stable/
- NumPy documentation: https://numpy.org/doc/stable/
- pandas documentation: https://pandas.pydata.org/docs/

## License

See [`LICENSE`](LICENSE).
