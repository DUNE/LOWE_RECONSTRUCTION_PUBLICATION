# Study data provenance (chapter 9 figures)

## Re-sync of 2026-09-17 (current data)

```
bash scripts/sync_solar_data.sh --yes --prune-legacy
```

The sync was rewritten to follow SOLAR's `run_studies.py` layout
(`analysis/{analysis}/{config}/marley/{folder}/{label}/`, `solar/cutflow/...`,
`solar/nhits/...`): 1437 files mirrored into `input/data/.solar_mirror/` and routed
into `input/data/` (reference copy) and `input/data/studies/{folder}/{label}/`.
The 792 flat `input/data/studies/*.pkl` files of the previous layout were deleted
(`--prune-legacy`); they collided across background folders and predate the
2026-09-17 Sensitivity fix (removal of the one-expected-event template floor).

Completeness against the registry (`src/lib/solar_studies.py`): Weighted 32/32,
Counts 235/286, Exposure 164/188, Contours 72/98, 10Y_Contours 72/98, Cutflow
244/272. Everything missing is absent on the remote: `unc_bkg0/unc_bkg4` under
`nominal`/`reduced` (only centralAPA DayNight/Sensitivity Counts exist), `charge_Q0`/
`charge_Q100` Sensitivity for three configs, `legacy_fit` everywhere, and the
`SelectedEnergy`/`SignalParticleK`/`MainK` DayNight cutflows for centralAPA. Re-run
the sync to pick them up once SOLAR produces them; the summary at the end of every
run lists what is still missing.

Retired labels skipped on purpose: `metric_raw`, `metric_smoothed`, `unc_bkg10`,
`unc_bkg20`, `unc_bkg4_nobkgfit`, `unc_bkg6_nobkgfit`, `unc_sig8`, `charge_Q200`,
`bkg_gamma` (now `bkg_gamma_cluster` / `bkg_gamma_total`).
