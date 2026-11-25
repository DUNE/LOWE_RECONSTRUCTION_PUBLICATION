# THESIS_PLOTS

Figures, generated tables and derived LaTeX macros of the PhD thesis of S. Manthey Corchado
(DUNE low-energy reconstruction and solar neutrinos), built from the SOLAR analysis outputs.
The thesis source is the THESIS repository (`~/Code/THESIS`).

This repository was the shared plotting repository `LOWE_RECONSTRUCTION_PUBLICATION` until
2026-11-25. The publications now have repositories of their own:

| Publication | Plotting repository |
|---|---|
| Low-energy reconstruction paper and technote | [DUNE/lowe_reco_paper_plots](https://github.com/DUNE/lowe_reco_paper_plots) (`paper` and `technote` lists) |
| Solar Phase I paper and technote | [mantheys/solar_neutrinos_phaseI_paper_plots](https://github.com/mantheys/solar_neutrinos_phaseI_paper_plots) (`paper` and `technote` lists, `scripts/paper_phaseI_numbers.py`) |
| VD X-ARAPUCA PDE paper | VD_XA_PUBLICATION |

The state of the submitted thesis (v1.0, 2026-10-23) is the tag `thesis-v1.0` (commands, captions and status files
in `thesis-v1.0-inputs`); the command lists used for the other publications before the split are in the history.

## Setup

```bash
source setup.sh        # .venv, dune_plot_style, test suite
```

## Command lists

Each list `input/{plots,tables}/<list>_scripts.txt` holds one macro call per line, only for files the thesis
includes. `python run_plot_scripts.py -s <list>` and `python run_table_scripts.py -s <list>` run a list and write
into THESIS through `config/output_paths.json` (`-o` is appended to every command without one).

| List | Commands | Written to (THESIS) |
|---|---:|---|
| plots `thesis` | 26 | `figures/exclusive/` |
| plots `lowe` | 4 | `figures/lowe/` |
| plots `reco` | 90 | `figures/reco/` |
| plots `waveform` | 9 | `figures/reco/waveform/` |
| plots `smearing`, `smearing_response` | 10, 3 | `figures/reco/smearing/` |
| plots `solar` | 76 | `figures/solar/` |
| plots `study` | 37 | `figures/study/<sub-folder>/` |
| plots `truth_position` | 4 | `figures/study/fiducial/` |
| tables `thesis` | 30 | `tables/` |
| tables `study`, `smearing` | 1, 1 | `tables/study/`, `tables/smearing/` |

Output file names are built by the macros from their arguments, so a changed option changes the name: check that
every `\includegraphics` and `\input` of the thesis still resolves after a rerun. The event display of `reco`
(line 3) reads the archived sample; the thesis file is an older render of the same command (see the comment in
the list).

The other THESIS figures and tables (literature, schematics, laboratory, X-ARAPUCA, hand-written tables) are not
produced here.

## Inputs

`scripts/sync_solar_data.sh` copies the SOLAR outputs into `input/data/` (git ignored; layout in
[`docs/input_data_layout.md`](docs/input_data_layout.md), provenance in
[`docs/study_data_provenance.md`](docs/study_data_provenance.md)). The study registry is `src/lib/solar_studies.py`;
`truncated/default` is the reference result set and a bare `--datafile` falls back to it.

## Derived numbers

The `*_to_macros.py` scripts and `fiduc_truth_data.py` write into THESIS (`THESIS_DIR`, default `~/Code/THESIS`);
the other two print their numbers or write to `output/tables/` for copying (see each script's usage):

| Script | Output |
|---|---|
| `scripts/status_to_macros.py` | `results/macros.tex` from the SOLAR study-status table |
| `scripts/exposure_to_macros.py` | exposure-curve macros (needs numpy >= 2: use `.venv/bin/python`) |
| `scripts/waveform_to_macros.py` | PDS waveform macros and parameter table |
| `scripts/fiduc_truth_data.py` | truth-position macros and table fragments |
| `scripts/hep_flux_precision.py` | hep flux precision |
| `scripts/snufish_solar_rates_table.py` | solar interaction rates in LAr (SNUfish) |

Input builders: `scripts/generate_*.py` (plotting pickles for the appearance terms, sensitivity hypotheses,
signal/background curves and solar interaction spectra), `scripts/smearing_chain.py`. Checks:
`scripts/ch9_check_status.py` (pickles against the status table), `scripts/truth_position_check.py`.

## Macros

| Macro | Use |
|---|---|
| `script_iterable_scan.py` | one or more series against a scanned variable |
| `script_compare_configuration.py` | configurations or samples on common axes |
| `script_compare_line_operation.py` | curves with a ratio or difference panel |
| `script_compare_hist1d.py`, `script_compare_hist2d.py` | 1D and 2D histograms |
| `script_compare_reduction.py` | box plots and summary scatters |
| `script_compare_contour.py` | oscillation-parameter contours |
| `script_compare_pareto.py` | purity against completeness |
| `script_line_fit.py` | fits with residual panels |
| `script_event_display.py` | event displays |
| `script_aggregate_table.py` | LaTeX tables |

Shared code is in `src/lib/`; run everything from the repository root. Tests: `python -m pytest -c tests/pytest.ini`.

## License

See [`LICENSE`](LICENSE).
