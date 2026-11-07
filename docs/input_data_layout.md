# input/data layout

Every pkl the plot and table macros read lives in a named folder. Nothing sits
loose in `input/data/`. Commands point at a folder with `--path <folder>`; a
bare `--datafile` without `--path` resolves to the reference results in
`studies/truncated/default/`.

Reorganised on 2026-09-25. Every command in `input/plots/*_scripts.txt` and
`input/tables/*_scripts.txt` was traced before and after the move and reads
byte-identical data.

## Synced from SOLAR (`scripts/sync_solar_data.sh`)

The registry in `src/lib/solar_studies.py` decides what is fetched and where it
goes. Folder names mirror SOLAR's `output/data/` tree without the
`{config}/{name}/` levels, so the loader's `{config}_{name}_{Kind}.pkl` lookup
works inside each folder.

| Folder | SOLAR source | Sync selector | Contents |
|---|---|---|---|
| `studies/{folder}/{label}/` | `analysis/`, `solar/cutflow/`, `solar/nhits/` | `--study <label or group>` | Day-Night / HEP / Sensitivity results, cutflows, fiducial nhits distributions (truncated/default). Analysis-agnostic files (Oscillogram, Signal1D_*) sit one level deeper in `daynight/`, `hep/`, `sensitivity/`. |
| `vertex/{resolution,reconstruction,fiducial,smearing,maps}/` | same | `--study reconstruction` | vertex resolution, efficiency, fiducialisation, smearing, efficiency maps |
| `TPC/{adjcluster,resolution/neutrino,resolution/electron,resolution/sources}/` | same | `--study reconstruction` | adjacent clusters, neutrino/electron energy resolution, smearing sources and gamma tagging |
| `PDS/{matchedopflash,adjopflash,opflash,flash,ophit}/` | same | `--study reconstruction` | flash matching, adjacent flashes, light maps, flash counts and flash-vertex distances, OpHit light yield |
| `preselection/{clustering,efficiency,production}/` | same | `--study reconstruction` | clustering and preselection efficiency, production distributions and limits (not regenerated) |
| `workflow/{calibration,correction}/` | same | `--study calibration` | energy calibration, charge/lifetime corrections |
| `workflow/{reconstruction,discrimination,wire_comparison}/` | same | `--study workflow` | energy reconstruction, cluster discrimination, wire planes |
| `marley/stacked/` | same | `--study marley` | MARLEY generator-level distributions |
| `background/` | `background/` | `--study background` | background spectra summaries (global and per config) |
| `event/` | `event/` | `--study event` | event displays, energy-deposition studies |
| `solar/weighted/` | same | `--study analysisdata` | per-component `SolarEnergy_Sensitivity_AnalysisData` |
| `truth_position/` | `solar/truth_position/export_repo/` | `--truth-position` | truth-position export (synced as a unit) |
| `PDS/waveform/` | `PDS/waveform/export/` | `--waveform` | PDS waveform characterisation, HD vs VD (synced as a unit; plots: `waveform_scripts.txt`) |
| `solar/fiducial/`, `solar/fiducial_profiles*/` | `solar/fiducial/export/` (SOLAR-sb) | `--fiducial` | fiducial-stage export: margin profiles per profile set, BestFiducials records, simulated background counts per volume (plots: `fidprofile_scripts.txt`) |
| `best-sigma-json/{config}/` | `config/{config}/best-sigma-json/` (not under `output/data/`) | `--best-cuts` | selected-cut json files of the analyses, read by `--panel_vertical_file` |
| `TPC/smearing/{config}/{name}/{sample}/` | `TPC/smearing/` (`TPC_SMEARING_CHAIN`) | `--smearing` | primary-cluster energy smearing chain, TrueEnergy to SolarEnergy (synced as a unit, SOLAR layout kept; see below) |

Which sample names and configs a flat family syncs is set by its selections,
for example `marley` × the four configs for the thesis and `marley_official`
for the lowe paper. `--name` replaces them.
`--check-remote-labels` lists folders and kinds on the remote that the registry
does not know.

### Energy smearing chain (`TPC/smearing/`)

SOLAR decomposes the primary-cluster SolarEnergy into steps that each swap one truth
ingredient for its reco counterpart: `TrueEnergy`, `Charge` (own charge, true drift,
flat gain), `PileUp`, `Lifetime` (drift from the matched flash), `Gain` (NHits
charge-per-MeV), `Calibration` (the `Energy` branch), `Offset` (random-forest
Q-value offset), `Map` (final SolarEnergy, equal to the analysis cutflow "Raw"
stage). Every primary cluster enters: no cuts, no fiducial volume, no smoothing.
`{sample}` is `full` (analysis weights; marley oscillated day+night mean) or, for
gamma only, `true9.5-10.5_unweighted` (MC counts, 0.25 MeV bins).
`samples/full/{config}_SolarEnergy_Chain_Cutflow.pkl` combines the four samples.

| File | Contents |
|---|---|
| `*_SolarEnergy_Chain_Cutflow.pkl` | cutflow_plot.py schema, one row per `Stage`/`Step`: `Counts` in events/MeV/20 yr (1 MeV bins) |
| `*_Chain_Spectra.pkl` | per step: `Bins` (centres), `Counts`, unit-area `Density` |
| `*_Chain_Endpoint.pkl` | share above the true endpoint per step, split by flash category and discriminant branch |
| `*_Chain_Counterfactuals.pkl` | share above the endpoint with `NoPileUp` / `TrueLifetime` / `FlatGain` restored |
| `*_Chain_Response.pkl` | E_step/E_true on the electron scale: `Median`, `P84`, `P99`, `PeakMean`, `PeakSigma` |
| `*_Chain_Summary.json` | flash categories, lifetime-ratio percentiles, response, cutflow closure |

Plots and tables: `scripts/smearing_chain.py` (`run_plot_scripts.py -s smearing`,
`run_table_scripts.py -s smearing`), routed to `THESIS/figures/reco/smearing/` and
`THESIS/tables/smearing/`.

## Local-only inputs (not on SOLAR)

| Folder | Contents | Produced by |
|---|---|---|
| `pde/` | X-ARAPUCA / PDE paper inputs (`DUNE_XA_*`, `DUNE_SiPM*_AngularPDE`, megacell, XA spectra) | hand-made; `scripts/generate_angular_pde_fits.py` writes the AngularPDE fits here |
| `theory/` | solar and SN spectra, cross sections, Bethe-Bloch, appearance terms, day-night asymmetry | hand-made; `scripts/generate_appearance_terms.py` writes here, `generate_snowglobes_solar_interactions.py` reads the solar spectrum here |
| `pandora/` | Pandora reconstruction comparisons (`Pandora*`, `*_marley_pandora_*`) | hand-made |
| `lowe/` | LowE waveform/template examples, cluster-merging BDT, efficiency summaries | hand-made |
| `ophit/` | OpHit / main-OpFlash signal histograms | hand-made |
| `weighted_nominal/` | old per-component `Weighted_Nominal` distributions (used by the `all` list only) | hand-made |
| `snowglobes/` | SNOwGLoBES interaction spectra | `scripts/generate_snowglobes_solar_interactions.py` |
| `sensitivity/templates/{config}/` | Sensitivity reactor/solar templates of one cut, copied by hand from SOLAR PNFS (`SENSITIVITY/{config}/marley_final/truncated/SolarEnergy`) | read by `scripts/generate_sensitivity_hypotheses.py` (see `input/plots/thesis_scripts.txt`) |

## archive/

`archive/` keeps every file no command reads, under its old relative path:
old flat reference copies whose identical twin is in the studies tree, dead or
renamed SOLAR kinds, the `phaseI/`, `default/`, `electron/` and
`input/input/` leftovers, and so on. Nothing reads from it. To bring a file
back, move it out of `archive/` to the folder above and pass `--path` to the
command that needs it.

The sync never writes into `archive/`. `studies/` files the sync produces
stay in place even when no command reads them today, because the next sync
would recreate them.
