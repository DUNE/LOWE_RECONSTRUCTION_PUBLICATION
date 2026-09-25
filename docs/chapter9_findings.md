- **Thesis section mapping.** The thesis text defines 9.1.2 (Energy Resolution) as `SolarEnergy` against `SignalParticleK`/`MainK` and 9.1.3
  (Energy Reconstruction) as the gamma-background model; its prose, table and captions are written that way and its `\includegraphics` match.
  The scripts follow the thesis. (The first brief had the two reversed; an earlier note here suggesting to swap the tex was wrong.)
- **Old list versus status table.** Replaying the old commands through `import_data`/`filter_dataframe` gives 139 distinct exposure curves:
  111 match the table at printed precision, 7 are within 0.01 (the Asimov row against the table's slightly larger Gaussian row), 11 are Raw or
  scenario curves that the table does not quote, 9 come from the old `input/data/phaseI` files (no table row), and 1 differs: HD central HEP
  `oscpoint_reactor`, a row the table itself flags `values_bug`. 49 of the 139 curves sit on rows tagged `epoch`/`behind_default`.
- **Not redrawable.** HEP energy-estimator figures (lines 59 to 66 of the list) and the Sensitivity energy contour (67): SOLAR runs
  `energy_spk`/`energy_maink` for Day-Night only. Line 5 (old HEP metric comparison) misses a `phaseI` file for VD shielded. The thesis
  already carries a `\todo` for the HEP energy rows.
- **`phaseI` metric figures (lines 3 to 5)** use `input/data/phaseI`, whose HEP numbers differ from the current analysis (HD central profile
  likelihood 10.49σ at cuts 4/12/5, against 10.62σ at 4/13/5 in the status table). They are stamped as legacy data.
- **List lines corrected (2026-09-20)**, in `study_scripts.txt` (a backup was kept in the session scratch area): line 47 title `Q=0` -> `Q=50` (the data is `charge_Q50`);
  line 84 fourth configuration `nominal` -> `shielded` (it repeated VD Top, so the combined contour counted it twice); lines 26 to 29 lost the dead
  first `--subfolder uncertainty` (the last, `metrics`, always won, so all four nuisance contours go to `metrics/`); the reactor marker moved from
  Δm² 7.45e-5 and sin²θ₁₂ 0.303 to SOLAR's 7.54e-5 and 0.304 in `study_scripts.txt`, `solar_scripts.txt`, `phaseI_scripts.txt` and `results_scripts.txt`.
  The existing PNGs in THESIS still show the old marker and, for lines 28 and 29, sit in `uncertainty/`.
- **Nominal and Reduced** in the new 9.1.5 figures use the `bkgmodel_*` studies, as the old `bkgmodel` figures do, not the older `default`
  runs of those folders (tagged `epoch`, and different: HD central Day-Night Reduced 5.24σ from the old default run, 4.53σ from `bkgmodel_reduced`).
- **`bkg_gamma_*` Sensitivity files** were not being synced (the registry listed Day-Night and HEP only); fixed in `src/lib/solar_studies.py`.
- **SOLAR plot scripts.** `output/scripts_for_lowe_publication/` on the remote is empty; `src/physics/common/*_plot.py` are Plotly HTML exporters.
- **Status table.** `.md` and `.csv` carry identical rows. Two rows outside chapter 9 need attention on the SOLAR side: HD lateral HEP
  `fiduc_truth_refvol` (unexpected on fresh results) and HD central HEP `oscpoint_reactor` (`values_bug`).
