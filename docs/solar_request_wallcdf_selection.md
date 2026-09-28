# Request for SOLAR: WallCdf at every selection stage

**Status:** done in SOLAR `f9539fa` (export 2026-09-25T23:02); synced and plotted here.

**Where:** `src/physics/signal/truth_position_study.py` (stage `export`) and `src/tools/export_truth_position_repo.py`.
**Why:** the wall-proximity figure (`wallcdf_*`) only exists for events that pass the flash-quality cut and the
10–20 MeV `SolarEnergy` window (`s.window`). It is labelled "Day-Night" in the plot repo because the export copies it under
all three Analysis labels, but no analysis cut is applied. Radiological is almost empty after this
selection (HD central 31 MC events, HD lateral 14), so we also need the distributions before it.

## What to produce

Add a `Selection` column to `WallCdf` with three stages. Everything else (grid 0–300 cm in 1 cm steps, weights
`SignalParticleWeight`, truth keys, wall definition in `wall_faces_distance`) stays as it is:

| Selection | Mask (per sample `s`) | Meaning |
|---|---|---|
| `all` | every event in the truncated cache | no selection |
| `quality` | `s.quality` | matched flash on an accepted plane, PE > 0, surface cut for surface backgrounds |
| `window` | `s.window` | quality + 10–20 MeV (today's WallCdf, unchanged numbers) |

Suggested change around line 1240 of `truth_position_study.py`:

```python
    for c in configs:
        for name in ("marley", "gamma", "neutron", "radiological"):
            s = data[c]["s"].get(name)
            if s is None:
                continue
            for sel, m in (("all", np.ones_like(s.window, bool)), ("quality", s.quality), ("window", s.window)):
                if not m.any():
                    continue
                for kind in ("truth", "reco"):
                    dist, w = s.wall_distance(kind)[m], s.w[m]
                    cdf = np.array([w[dist <= g].sum() for g in grid]) / w.sum()
                    rows += [(c, name, sel, kind, float(g), float(v), int(m.sum())) for g, v in zip(grid, cdf)]
    _write("wall_cdf", rows, ["config", "species", "selection", "position", "distance_cm", "cdf", "n_mc"])
```

and in `export_truth_position_repo.py` (line ~80) group by `selection` too and pass `"Selection": sel` into the
row dict. Update the `WallCdf` columns in the export README and `meta.json` (`Selection` after `Sample`). The
`checks` block (line ~263) must keep reading `Selection == "window"`.

Reco positions of events without a reconstructed cluster: if `reco_x/y/z` are NaN for `all`, drop them for the `reco`
rows only (NaN distances compare False, so they are already excluded from the numerator but still in `w.sum()`) —
use `ok = np.isfinite(dist)` and normalise with `w[ok].sum()`, and report `NMC = ok.sum()`.

## Resync and plot here

```bash
./scripts/sync_solar_data.sh --truth-position -y
python scripts/truth_position_check.py
```

The existing plot commands in `input/plots/truth_position_scripts.txt` (lines 12–15) then need
`Selection` added to `--select` with value `window` to keep today's figures. A no-selection version of each figure
is the same command with `-s DayNight all marley gamma neutron radiological` on
`--select Analysis Selection Sample Sample Sample Sample`.
