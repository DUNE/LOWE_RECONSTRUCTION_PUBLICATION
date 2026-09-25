# Truth-position study: generated files

Where everything comes from and goes, for agents working with the LOWE_RECONSTRUCTION_PUBLICATION ("plot repo") outputs of the truth-position study. Nothing here recomputes physics; the numbers are the SOLAR export's.

## Pipeline
| step | command | result |
|---|---|---|
| export (SOLAR repo) | `python src/physics/signal/truth_position_study.py --stage export`, then `src/tools/export_truth_position_repo.py` | `output/data/solar/truth_position/export_repo/` (84 pickles, `README.md`, `meta.json`), tarball `truth_position_export_repo.tar.gz` |
| sync | `./scripts/sync_solar_data.sh --truth-position [--dry-run] [--yes]` | `input/data/truth_position/` (pickles gitignored; `README.md` and `meta.json` come along) |
| check | `python scripts/truth_position_check.py` | fails loudly if the reference numbers, the SOLAR Table F1 cross-check or the file structure do not hold |
| plots | `python run_plot_scripts.py -s truth_position` | `output/plots/truth_position/*.png` (97 files), and (via `config/output_paths.json`) `THESIS/figures/study/fiducial/` |
| tables | `python run_table_scripts.py -s truth_position` | `output/tables/*.tex` (37 float files with caption + 37 bare `*_tabular.tex`, booktabs) |

## Input data: `input/data/truth_position/`
`{config}_all_{Kind}.pkl`, 4 configs x 21 Kinds. Configs: `hd_1x2x6_centralAPA`, `hd_1x2x6_lateralAPA`, `vd_1x8x14_3view_30deg_nominal`, `vd_1x8x14_3view_30deg_shielded`. Every row carries `Analysis` (DayNight|HEP|Sensitivity), `Geometry`, `Config`, `Name` (constant `all`), `Study` (`default`), and `Sample` (marley, gamma, neutron, neutron_agree, neutron_disagree, radiological) wherever a sample exists. Curves are single rows holding equal-length arrays; categorical values are strings. Per-Kind columns and the figure each Kind feeds are in the export's own `README.md`. Kinds: WallCdf, ShellRatio, Residuals, ResidualsWide, ResidualSummary, FlashMismatch, Cuts, FiducialVolumes, PassFractions, Significance, FaceComposition, XEntryHist, XEntrySummary, ScanGrid, ScanCurves, BestFoM, SignalRecovered, BackgroundSplit, SurvivorStatistics, SurvivorEvents, and (added 2026-09-21) **TruthKeyCheck** -- which truth key (Main/MainParent/End/SignalParticle) lies within 30 cm of the reconstructed cluster; not yet wired into any plot or table command.

Selection behind all numbers: Truncated folder, `SolarEnergy` 10-20 MeV, default best cut of each analysis, raw `SignalParticleWeight` only.

## Command lists (the source of truth for how each output is made)
- `input/plots/truth_position_scripts.txt`: 30 commands, `script_iterable_scan.py` and `script_compare_hist1d.py`. One figure per `--configs` entry (`--overlay_names` puts all configs in one figure). Panels come from the `Variable` column via `--variables`.
- `input/tables/truth_position_scripts.txt`: 74 commands, all `script_aggregate_table.py`: 37 tables, each written twice, once as a float and once with `--table_env none`. Rows = Geometry x Config x `--row_name`; columns = the `-n` column restricted to `--variables`; one file per quantity.
- Analysis-independent Kinds (WallCdf, ShellRatio, Residuals*, ResidualSummary) are stored under all three Analysis labels, so every command filters on `Analysis` (DayNight).
- Captions: `input/captions/truth_position_{background_split,survivor_statistics,x_entry_summary,best_fom,signal_recovered,residual_summary,fiducial_volumes,face_composition}.txt`.
- Colours: `truth_species_color`, `truth_face_color`, `truth_species`, `truth_position_source` in `config/plot_params.json`.

## Plots (`output/plots/truth_position/`, PNG; file name = script prefix + config + columns + filters)
| prefix | content | files |
|---|---|---|
| `wallcdf_` | cumulative weighted fraction vs distance to the nearest face, marley/neutron/gamma, truth solid and reco dashed, lines at 20 and 100 cm | 4 (per config) |
| `shellratio_` | (B/S in shell)/(B/S in 100-200 cm), gamma and neutron, error bars, log y | 4 |
| `residuals_` / `residualswide_` | reco - truth histograms X/Y/Z panels, marley and gamma; HD configs use 5 cm bins (+-150 cm), VD configs the +-700 cm 20 cm bins | 2 + 2 |
| `survivorevents_` | neutron survivors: 3D-distance histogram (MC events, split by agree at 30 cm) and reco X vs truth X; DayNight and Sensitivity | 16 |
| `passfractions_` | fiducial pass fraction per sample group for the four position treatments (VariantIndex 0-3); DayNight and Sensitivity | 8 |
| `significance_` | default vs fiduc_truth vs fiduc_truth_refvol, all configs in one figure; DayNight, HEP, Sensitivity | 3 |
| `facecomposition_` | share of the four entry faces at three selection stages, gamma/neutron/radiological, DayNight | 12 |
| `xentryhist_` | |RecoX - truth X| within 100 cm of the entry face, gamma and neutron, window and after the cut, DayNight | 8 |
| `scancurves_` | signal efficiency vs gamma+neutron weight and S/sqrt(B) vs fiducial cut, X-only and Y-only panels, five position modes; three analyses | 24 |
| `signalrecovered_` | signal efficiency and gamma+neutron weight at the FoM-best X cut, reco X vs truth X, per config; three analyses | 6 |

## Tables (`output/tables/*.tex`, prefix = Kind in lower case, `_all_` then the quantity)
`backgroundsplit_` (6: weights, radiological fraction, MC counts, before/after the truth pipeline), `survivorstatistics_` (9), `xentrysummary_` (5: median, fractions above 30/100 cm, RecoX at the edge, MC events; DayNight), `bestfom_` (5: S/sqrt(B) for the X-and-Y, X-only, Y-only scans, and the best FiducialX/Y), `signalrecovered_` (5: efficiency and weight under reco X and truth X, and the difference in percentage points), `residualsummary_` (3: median, fraction within 30 cm, beyond 150 cm), `fiducialvolumes_` (3: best FiducialX/Y/Z, default vs fiduc_truth), `facecomposition_all_weightfraction_stage_face_table.tex` (1: entry-face shares in percent, Config x Sample rows, Stage x Face columns, DayNight; `--column_group Stage --block_rows`, `table*` float; replaces the `facecomposition_` line plots for the thesis). Each has the caption of its Kind.

### Bare tabulars (`*_tabular.tex`)
Every table command is repeated with `--table_env none` (alias `--bare`): only `\begin{tabular}...\end{tabular}`, no float, no `\centering`, no `\caption`, no `\label`, written to the same name with `_tabular` before `.tex` (e.g. `facecomposition_all_weightfraction_stage_face_table_tabular.tex`). The thesis `\input`s these inside its own `\fitwidth`/`table`/`\caption`/`\label`; the caption text stays in `input/captions/`. The float files are unchanged, except that the face table now also has the math headers and capitalised samples below and `\label{tab:fiduc_truth_faces}` (`--label`, emitted after the caption, float only).

Related `script_aggregate_table.py` options: `--table_env` (default `table*`), `--label`, `--variable_titles` (display titles of `--variables`, with `--column_group`), `--row_titles` (display titles of `--row_order`).

## Caveats to carry with any number from these outputs
- Weights are raw `SignalParticleWeight`: no oscillation, no MC-support gate, no smoothing. These outputs diagnose position information; they are not replacement significances.
- Truth position: SignalParticleX/Y/Z (marley), EndX/Y/Z (gamma), MainX/Y/Z (neutron, radiological). For neutron and radiological it is the label particle; for VD backgrounds truth X can lie outside the active box while RecoX cannot.
- The truth pipeline = truth position + truth containment cut + (backgrounds) consistency cut (|dX| <= 100 cm, |dY|,|dZ| <= 50 cm), as the `fiduc_truth` study applies it.
- Radiological has 1-65 MC events per selection with weights ~1e5: its fractions are not statistical statements. HD central truth pipeline removes every radiological MC event (0% means all rejected, not an empty denominator).
- The four entry faces sum to 1; `OutsideFraction` is a separate flag that overlaps them.
- VD gamma and neutron X medians (about -340 to -380 cm) are outside the +-150 cm histograms (use `ResidualsWide`); VD signal has 37% of its X weight beyond 150 cm.
- HD central: no gamma after the cut and one neutron MC event, so those entry-face panels/rows are empty or single-event. Its FoM-best truth X cut (320 cm, 16% signal efficiency, barely above 5 gamma+neutron MC events) is not quotable. Its X-and-Y best volume coincides with the Y-only one.
- The Sensitivity significance unit is `\Delta\chi^2` (`SignificanceUnit`); SOLAR's `Score` = 0.5*(chi2_solar(theta_react) + chi2_react(theta_solar)), a wrong-hypothesis Delta chi^2, so the label is correct as given. DayNight and HEP significance are in sigma. (Confirmed 2026-09-21; the sigma-equivalent for Sensitivity, if ever needed, is sqrt(Score).)
- **Wall/face definition changed 2026-09-21** (SOLAR git `0eb6b74`): HD lateral now counts only the x = 0 plane as a wall (x = 360 no longer does -- background piles up there instead of leaving through it), so `FaceComposition`, `WallCdf` "distance to nearest face" and the entry-face figures for HD lateral no longer have an "X high" component (it is 0 everywhere). HD central gained a second X wall (x = -360, in addition to +360; x = 0 stays interior). VD is unchanged (x = +-330). `scripts/truth_position_check.py`'s SOLAR Table F1 cross-check was updated to the new HD lateral numbers.

## What the macros cannot draw (dropped or moved into tables)
Grouped or stacked bars (shell ratio, pass fractions, significance and face shares are line/scatter plots), text annotations (medians, MC counts, xN labels), ratio panels under the significance figure, highlighted table rows.
