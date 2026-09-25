# Chapter 9 figures

Two sets of scripts produce the chapter 8/9 study figures from the SOLAR outputs. Both write PDF + PNG, cross-check every drawn
series against SOLAR's status table before writing, and stamp rows the table tags stale as *preliminary*.

1. **The existing list** `input/plots/study_scripts.txt`, redrawn by `scripts/ch9_legacy_study.py`. Every command becomes a figure
   with the same data, grouping, panels and axes and the **same file name and sub-folder** as the old macro gave it, so the
   `\includegraphics` of the thesis are unchanged. Only the style changes (repository helpers), plus the status-table marking.
2. **New chapter 9 figures**, one script per thesis section:

| Thesis section | Script | Study | Output |
|---|---|---|---|
| 9.1.2 Energy resolution | `scripts/ch9_1_2_energy_resolution.py` | `energy_spk`, `energy_maink` (Day-Night) | `figures/study/energy/` |
| 9.1.3 Energy reconstruction | `scripts/ch9_1_3_energy_reconstruction.py` | `bkg_gamma_cluster`, `bkg_gamma_total` | `figures/study/deex_gamma/` |
| 9.1.4 Charge threshold | `scripts/ch9_1_4_charge_threshold.py` | `charge_Q0/50/100/500` | `figures/study/threshold/` |
| 9.1.5 Background model | `scripts/ch9_1_5_background_model.py` | `bkgmodel_nominal/reduced` vs Truncated | `figures/study/bkgmodel/` |
| 9.1.6 Membrane XAs (VD) | `scripts/ch9_1_6_membrane_xas.py` | `membrane_veto_off` | `figures/study/membrane_veto/` |
| 9.2.1 Phase I reach | `scripts/ch9_2_1_phaseI_combined.py` | default, four configs | `figures/solar/` |
| 9.2.2 Summary | `scripts/ch9_2_2_summary.py` | all of the above | `figures/study/summary/` |

The section numbering follows the thesis text (9.1.2 discusses `SolarEnergy` against `SignalParticleK`/`MainK`, 9.1.3 the gamma
background model).

## Run

```bash
source .venv/bin/activate
bash scripts/ch9_run_all.sh                       # old list + new figures + comparison + REPORT.md, about 1 minute
python scripts/ch9_legacy_study.py --subfolder threshold      # only some sub-folders of the old list
python scripts/ch9_legacy_study.py --line 35 36               # only some lines
python scripts/ch9_1_4_charge_threshold.py --configs hd_1x2x6_centralAPA
```

Arguments (all scripts):

| Argument | Default | Meaning |
|---|---|---|
| `--data-dir` | `input/data/studies` | studies tree written by `scripts/sync_solar_data.sh`; the old list's relative `--path` values start in its parent (`--input-dir` overrides) |
| `--status-table` | `input/status/study_status_20260920_v5.md` | SOLAR `output/logs/study_status_*.md` (or `.csv`) |
| `--output` | `output/chapter9` | figures go to `{output}/figures/study/<sub-folder>/` and `{output}/figures/solar/` (the layout of THESIS `figures/`) |
| `--thesis` | off | write into the folders of `config/output_paths.json` (`plots.study`, `plots.solar`) as `run_plot_scripts.py` does; overwrites same-named files |
| `--no-watermark` | off | remove the "preliminary" watermark and the legend daggers |
| `--on-mismatch` | `raise` | `warn` keeps drawing when a number disagrees with the status table |
| `--formats` | `pdf png` | |
| `--configs` | all four | new figures only; HD central is the main figure |

## Inputs

```bash
bash scripts/sync_solar_data.sh --yes                 # pkls -> input/data/studies/ (and the reference copies in input/data/)
# newest status table: copy SOLAR output/logs/study_status_<tag>.md into input/status/ (same ssh setup as the sync)
```

Use a newer table with `--status-table`; watermarks then follow its tags.

## Rules

- Exposure axes: the new figures run to 30 yr with the quoted exposure marked (20 yr Day-Night/HEP, 10 yr Sensitivity, which SOLAR
  stores only at 10 and 30 yr, so Sensitivity is drawn as points). The old list's figures keep their own axes (0 to 20 yr).
- Preliminary: a row tagged `epoch`, `behind_default` or `values_bug` in the status table, the Sensitivity charge-threshold rows
  Q50/Q100/Q500 (trend not understood), `fiduc_truth` (in development), and the old `input/data/phaseI` files (not covered by the table).
- Cross-check: the value at the quoted exposure (2 decimals), the cut, the quoted exposure and, for the new figures, the 30 yr value are
  recomputed from the pkls with the recipe of SOLAR `study_status.py`; a disagreement raises `StatusTableMismatch` before that figure is
  written. `scripts/ch9_check_status.py` checks the new figures' inputs alone, `scripts/ch9_compare_legacy.py` the old list's curves.
- A command of the old list whose input no longer exists (data SOLAR stopped writing) is not drawn and is reported; its old figure is left alone.
  `Sensitivity_SolarEnergy` (obsolete) is drawn from `Sensitivity_Contours`, keeping the old file name.
- Names come from `lib.exports.make_name_from_args`, including the macros' `.png` suffix in the length budget.

## Outputs per figure

`<name>.pdf`, `<name>.png`, `<name>.json` (source command or inputs, cuts, status tags, plotted values, verdicts), and a `.csv` for the summary.
`scripts/ch9_report.py` writes `output/chapter9/REPORT.md` from the sidecars. To copy into THESIS:

```bash
rsync -av --include='*/' --include='*.pdf' --include='*.png' --exclude='*' output/chapter9/figures/ ~/Code/THESIS/figures/
```
