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
| `vertex/{resolution,reconstruction,fiducial,smearing}/` | same | `--study reconstruction` | vertex resolution, efficiency, fiducialisation, smearing |
| `TPC/{adjcluster,resolution/neutrino,resolution/electron}/` | same | `--study reconstruction` | adjacent clusters, neutrino/electron energy resolution |
| `PDS/{matchedopflash,adjopflash,opflash}/` | same | `--study reconstruction` | flash matching, adjacent flashes, light maps |
| `preselection/{clustering,efficiency}/` | same | `--study reconstruction` | clustering and preselection efficiency |
| `workflow/{calibration,correction}/` | same | `--study calibration` | energy calibration, charge/lifetime corrections |
| `workflow/{reconstruction,discrimination,wire_comparison}/` | same | `--study workflow` | energy reconstruction, cluster discrimination, wire planes |
| `marley/stacked/` | same | `--study marley` | MARLEY generator-level distributions |
| `background/` | `background/` | `--study background` | background spectra summaries (global and per config) |
| `event/` | `event/` | `--study event` | event displays, energy-deposition studies |
| `solar/weighted/` | same | `--study analysisdata` | per-component `SolarEnergy_Sensitivity_AnalysisData` |
| `truth_position/` | `solar/truth_position/export_repo/` | `--truth-position` | truth-position export (synced as a unit) |

Which sample names and configs a flat family syncs is set by its selections,
for example `marley` × the four configs for the thesis and `marley_official`
for the lowe paper. `--name` replaces them.
`--check-remote-labels` lists folders and kinds on the remote that the registry
does not know.

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
