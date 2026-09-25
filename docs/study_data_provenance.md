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
2026-09-17 Sensitivity fix (removal of the one-expected-event template floor), so
everything below this heading about "which variant is stale" is superseded.

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

## Sync of 2026-09-06 (superseded)

**Synced:** 2026-09-06 16:02 from `gae_out:/pc/choozdsk01/users/manthey/SOLAR`

```
bash scripts/sync_solar_data.sh --name marley --folder truncated --force --yes
```

554 files selected / 758 downloaded → 176 new, 378 updated.
`input/data/studies/` now holds 440 study-variant pkls across 4 configs.

## ⚠ These figures are PROVISIONAL

The SOLAR-side study summary carries a **"REQUIRED RERUN"** notice that had **not
been actioned** when this data was pulled. Two upstream changes invalidate most
published study numbers:

1. **`--skip_best_cuts` bug** — it gated `01_daynight.py` / `01_hep.py` in addition to
   `04_best_cuts.py`. Any DayNight/HEP variant carrying that flag never computed its own
   significance grid and reported nominal or stale numbers under its own study label.
2. **One-knob policy** — every variant now holds cuts and smoothing sigmas at nominal
   (`skip_best_cuts=True`, `skip_best_sigmas=True`) so a variant can no longer look
   better merely because its cuts were re-fit.

### Classification at sync time

| Group | Variants | Status |
|---|---|---|
| **A — numbers wrong** | `unc_bkg0/4/6`, `unc_sig20/40`, `oscpoint_solar`, `fiduc`, `bkgmodel`, `membrane_veto` | grid never computed under the bug |
| **B — not comparable** | `energy_spk/maink`, `charge_Q*`, `fiduc_truth`, `bkg_gamma`, `oscpoint_reactor` | valid physics, but produced with re-tuned cuts |
| **C — no rerun needed** | `unc_sig0/2/6/8`, `nuisance_nominal/sin13/escale` | Sensitivity-only; the bug never reached them |

Only **Group C** figures should be treated as final. Everything else must be
regenerated once the SOLAR reruns land — that is a re-run of the same batch
(`python3 run_plot_scripts.py -s study`), not rework.

## Known data gaps (commands present, inputs absent)

- `Sensitivity_Significance_bkg_gamma` — missing for all 4 configs; the Sens arm of the
  improved-gamma study has not been produced upstream.
- `Sensitivity_*_energy_maink` — absent; only `energy_spk` exists, cAPA only.
- `Sensitivity_*_charge_Q500` — absent; Sens charge scan stops at Q50/Q100/Q200.
- `metric_raw` / `metric_smoothed` — cAPA only.
- `membrane_veto_off` — vertical-drift configs only (by design).

## Note on staleness checking

`sync_solar_data.sh` copies with plain `cp`, so local mtimes are reset to the sync
time and cannot be used to tell which variants are stale. Using `cp -p` would
preserve the remote generation time and make this checkable directly.

## Post-sync value audit (2026-09-06)

Cross-checking the synced pkls against the artifact's quoted numbers
(centralAPA, Truncated, @10 yr) separates trustworthy variants from stale ones.

**Agrees with the artifact (trustworthy):**

| Variant | analysis | synced | artifact |
|---|---|---|---|
| baseline | DN Asimov | 2.407 | 2.412 |
| baseline | HEP PL | 7.609 | 7.624 |
| `oscpoint_reactor` | DN Asimov | 1.305 | 1.307 |
| `oscpoint_reactor` | HEP PL | 7.598 (Δ−0.012) | 7.613 (Δ−0.011) |
| `energy_maink` | DN Asimov | 0.327 | 0.328 |
| `bkg_gamma` | DN Asimov | 2.248 | 2.253 |
| `unc_sig20` | HEP PL | 8.387 | 8.404 |
| `unc_sig40` | HEP PL | 6.799 | 6.813 |
| `charge_Q500` | DN Asimov | 1.629 | 1.632 |

`unc_bkg*` returning exactly the baseline is **correct physics**, not a defect:
the DN Asimov statistic is $\sigma_{bkg}$-invariant by construction, and HEP PL is
$\sigma_{bkg}$-independent for centralAPA.

**Does NOT agree — stale or nominal-contaminated:**

| Variant | analysis | synced | artifact | symptom |
|---|---|---|---|---|
| `fiduc_truth` | HEP PL | 7.607 (Δ−0.002) | 8.180 (Δ+0.556) | reports baseline under its own label |
| `metric_raw` | HEP PL | 7.609 (Δ0.000) | 4.379 | reports baseline |
| `metric_smoothed` | HEP PL | 7.609 (Δ0.000) | — | reports baseline |
| `metric_raw` | DN Asimov | 2.562 | 2.619 | see below |
| `metric_smoothed` | DN Asimov | 2.562 | 2.412 | see below |
| `charge_Q50` | DN Asimov | 2.562 | 1.584 | see below |
| `charge_Q100` | DN Asimov | 2.562 | 1.365 | see below |
| `charge_Q200` | DN Asimov | 2.562 | — | see below |

The five DN entries at exactly **2.562** are five different variants returning one
identical non-baseline value — a cross-contamination signature, not physics. This is
precisely the `--skip_best_cuts` failure mode the artifact documents: the stage never
ran, and nominal/stale results were seeded under the study's own label.

**Consequence for chapter 9.** These figures are wired in but currently show
degenerate content and must not be interpreted until the SOLAR rerun lands:

- `fig:study_fiducialisation_hep` — variant lies on top of the baseline
- `fig:study_charge_threshold_dn` (and the DN charge spectrum) — Q50/Q100/Q200 degenerate
- the metric-choice figures in `sec:DISCUSSION_METRICS`

Everything else in the chapter reproduces the artifact to within interpolation noise.
