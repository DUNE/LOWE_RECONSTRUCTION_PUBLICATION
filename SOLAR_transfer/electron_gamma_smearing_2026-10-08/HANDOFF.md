# Electron / gamma / capture-cascade smearing study: handoff (2026-10-08)

Goal: explain why 10 MeV CC electrons smear wider than 10 MeV gammas in `fig:SMEARING_CHAIN_SLICE`
(thesis `chapters/7_chapter/7_6_section.tex`). Add neutron-capture cascades to the discussion. Characterise
the MARLEY de-excitation pile-up in chapter 7 against a pure-electron sample. Deliverable: revised §7.6 text
and new appendix F figures. Plan file: `~/.claude/plans/we-need-to-understand-parsed-shamir.md`.

## Files in this folder (copies; the live versions are on the remotes)
- `06_electron_gamma_response.py`, `07_gun_energy_ladder.py`: live in SOLAR-sb `src/physics/detector/tpc/`. Uncommitted.
- `gun_chain.jobscript`, `gun_1008.sh`, `local_test.sh`: live in FNAL `/exp/dune/app/users/smanthey/justin/gun_1008/`.
- `SolarNuAna_module.cc.fnal_patched` / `.fnal_orig`: FNAL `larsoft_v10_08_01/srcs/duneana/duneana/SolarNuAna/`.
  It adds the `SaveClusterEDep` option (default false), which writes SignalEDep and SignalNElectrons per cluster,
  SignalHitEDep, SignalHitNElectrons, SignalIDEEDep and SignalIDENElectrons per plane, and restricts the
  TSignal*DepList entries to the collection view. The library is built and installed, and the justIN tarball is
  rebuilt. Backups: `*.bak-20261008`. The change is not in any git branch yet.
- `fnal.sh '<cmd>'` runs a command on dunegpvm03 through gaeuidc1 (it runs `kinit_fnal.py`). `sl7.sh` gives an SL7
  apptainer wrapper (dunesw needs SL7). `check_out.py`, `check2.py` and `check3.py` inspect gun outputs with uproot
  (LCG_105 view). `meta.sh` is a metacat setup.
- `plots_review/`: Phase A figures rendered so far.

## justIN workflows (scope usertests; outputs in /pnfs/dune/scratch/users/smanthey/ana/<dir>/fnal/<wf>/...)
**v1 workflows 21760–21768 (dirs gun_1008_*) are INVALID.** Two problems were found on 2026-10-08:
- Every job produced the same events. SingleGen seeds its engine with 0 unless `generator.Seed` is set, and the
  other stages used the default perEvent seeds.
- Only 10 events per job reached g4 and beyond, because the official fcls set `source.maxEvents: 10` and `-s`
  inputs were read without `-n -1`.

The HD v1 outputs had 10 unique events. The VD v1 workflows were stopped (finish-workflow). The v1 merged files
were moved to `/exp/dune/data/users/smanthey/gun_merged_v1_invalid`. The jobscript is fixed (v1 kept as
`gun_chain.jobscript.v1_broken`): it now sets `generator.Seed`, wraps every stage in a fcl with an
autoIncrement NuRandomService whose base seed depends on the workflow, job counter and stage, and passes `-n -1`.
Verified locally: 12/12 events through every stage, and different workflow IDs give different events.

v2 (submitted 2026-10-08 ~19:55 CEST, dirs gun_1008b_*):
| wf | sample | jobs × ev | dir |
|---|---|---|---|
| 21778 | HD e⁻ 10 MeV | 200 × 50 | gun_1008b_hd_electron_10MeV |
| 21779 | HD γ 10 MeV | 200 × 50 | gun_1008b_hd_gamma_10MeV |
| 21780 | VD e⁻ 10 MeV | 400 × 25 | gun_1008b_vd_electron_10MeV |
| 21781 | VD γ 10 MeV | 400 × 25 | gun_1008b_vd_gamma_10MeV |
| 21782 | HD thermal n, default NeutronHP | 200 × 50 | gun_1008b_hd_neutron_thermal |
| 21783 | HD thermal n, photon evaporation | 200 × 50 | gun_1008b_hd_neutron_thermal_photonevap |
| 21784 | VD thermal n, default | 400 × 25 | gun_1008b_vd_neutron_thermal |
| 21785 | HD pure e⁻ flat 2–30 MeV | 400 × 50 | gun_1008b_hd_electron_flat2-30MeV |
| 21786 | VD pure e⁻ flat 2–30 MeV | 480 × 25 | gun_1008b_vd_electron_flat2-30MeV |

The v1 HD jobs took about 1 h for 10 events; v2 jobs process 50 (HD) or 25 (VD) events, so expect several hours.
Before merging, check that SignalParticleX is unique across files and that each file holds NUM_EVENTS events.
For the flat sample, check that K spans 2–30 MeV. SolarNuAna MaxSignalK is 30 MeV, so events above 30 MeV are
dropped.

## Next steps
1. When the workflows finish, merge the outputs per sample (hadd) and copy them to SOLAR pnfs under new names, never
   overwriting existing samples:
   - `data/hd/hd_1x2x6_centralAPA/SolarNuAna_{electrongun_10MeV,gammagun_10MeV,neutrongun_thermal,neutrongun_thermal_photonevap,electrongun_flat}.root`
   - `data/vd/vd_1x8x14_3view_30deg_nominal/SolarNuAna_{electrongun_10MeV,gammagun_10MeV,neutrongun_thermal,electrongun_flat}.root`
2. Run `07_gun_energy_ladder.py --config <cfg> --names electrongun_10MeV gammagun_10MeV neutrongun_thermal [neutrongun_thermal_photonevap]`
   in the SOLAR container. It covers the energy breakdown (containment → hit threshold → clustering → charge
   response), the topology, pair vs Compton production, and the cascade sum and multiplicity.
3. Pure electrons for the de-excitation pile-up (user request). Process `electrongun_flat` into SOLAR npy
   (`src/tools/process_sample.py`) and run `04_smearing_chain.py --name electrongun_flat --true_range 9.5 10.5 --unweighted`
   plus the full range. Then compare against marley_final: the slice and full chain, the >10.5 MeV tail, and the
   <5 MeV population. 04 needs a truth entry for the family `electrongun` (SignalParticleK).
4. Plots: `LOWE_RECONSTRUCTION_PUBLICATION/input/plots/smearing_response_scripts.txt` (run with
   `run_plot_scripts.py -s smearing_response`; output key `smearing_response` → THESIS/figures/reco/smearing/).
   Sections 1–3 (10 MeV) are tested. Section 4 (6 MeV with capture cascades) runs are finished. Its data were fetched to
   `input/data/TPC/smearing/*/*/at6MeV_unweighted/`, and the review renders are in `plots_review/*6mev*`; they
   have not been routed to THESIS yet. The event-sum plot shows two effects above 1: the neutron tail
   (NeutronHP non-conservation) and the CC tail (de-excitation γ against the ElectronK reference). Fetch only the Response_* files with tar (see the memory note); do not use `sync_solar_data.sh --smearing`.
   Add commands for the gun ladder (`Gun_Ladder`, -i Name) and the pure-electron vs marley chain.
5. Thesis: revise the §7.6 paragraphs and add an appendix F subsection. Put the de-excitation pile-up
   characterisation in ch. 7. New numbers go in as macros in `references/metrics/main.tex`. Production issues go
   in `% REVIEW` comments only: the RecoY/adjacency artefact, the HD Central gamma optical artefact, and NeutronHP
   energy non-conservation.

## Findings so far (charge-response step: true drift time, flat gain)
- **10 MeV, same core:** σ/E ≈ 4 % for both e⁻ and γ. Peak at 1.00 (e⁻) and 0.87–0.90 (γ). The leading cluster has
  a median of 5–6 hits for e⁻ and 3–4 for γ, at the same energy per hit.
- **De-excitation pile-up (marley):** 94 % of events have prompt γ (mean 3.7 MeV). Classes in HD Central: electron
  only 62 %, electron + merged de-excitation γ 15 % (half of these lie above 10.5 MeV, and they make up about half
  of the >10.5 MeV tail), γ-only primaries 22 % (97 % of them below 5 MeV, about 80 % of the <5 MeV population).
  There are 1.32 primaries per event (VD Shielded 1.45).
- **RecoY artefact:** 87 % of the same-side de-excitation-γ primaries lie within dZ<100 cm of the electron but have
  dY>100 cm. RecoY of 1-hit clusters fails (34 % have |y|>600), so the adjacency fails.
- **Flash:** at the lifetime step the gamma core widens to σ 0.08–0.13 (HD Central gamma: 63 % no flash, which is
  the sample's optical artefact; VD: 69 % wrong flash).
- **6 MeV comparison (leading cluster / true energy, median):** e⁻ 0.99 (82 % >0.9), single γ 0.66–0.69 (9–11 % >0.9),
  capture cascade 0.43–0.44 (3–7 % >0.9). The capture cascade has 1.3–1.8 primaries per event. For 4–12 % of
  capture events, the summed clusters exceed 1.05 × 6.1 MeV.
- **Gun tests (few events):** electrons and 10 MeV γ keep about 75–90 % of the deposited energy in hits; capture
  cascades keep about 57 %. The gain G absorbs the electron loss.
- **NeutronHP:** the default capture cascades do not conserve energy (sums of 5.4–13.3 MeV in 5 test events).
  Photon evaporation conserves 6.099 MeV but always takes the same 4.10 + 1.83 + 0.17 MeV path. Neither is the
  real Ar-41 cascade; keep this as a caveat.

## Narrative status (2026-10-08 ~21:00)
- Thesis §7.6 now has `fig:SMEARING_CAPTURE_SIX` and a "6 MeV electrons, gammas and neutron captures" paragraph block
  after the 10 MeV paragraphs. It uses the new macros `\fomSmearSix*`, `\fomCaptureQValue`, `\fomArFirstExcitedState`
  and `\fomSmearNeutronMaxK` in `references/metrics/main.tex`. Two `% REVIEW` notes cover NeutronHP and the RecoY
  artefact, and a `% TODO` points to the gun studies. The build is clean (pages 167–168).
- The combined figure command is `smearing_response_scripts.txt` §4 (`--filename_suffix clusters_6mev`). It uses the new
  standard option `--rebin N` (`--rebin_sum` for counts) in `scripts/script_iterable_scan.py`, plus the new mappings
  `smearing_slice_sample_labels` and `smearing_reference_labels` in `config/plot_params.json`.

## Status 2026-10-09 ~20:45
- All v2 workflows finished with full statistics: 10k events per 10 MeV/neutron sample, 20k HD and 12k VD flat
  electrons. Validation: event vertices unique, flat K = 2–30 MeV (VD has 6 events with K=0, dummies).
- Merged on FNAL in `/exp/dune/data/users/smanthey/gun_merged_v2/` and copied to SOLAR pnfs as
  `SolarNuAna_{electrongun_10MeV,gammagun_10MeV,neutrongun_thermal,neutrongun_thermal_photonevap(HD only),electrongun_flat}.root`
  (HD under hd_1x2x6_centralAPA, VD under vd_1x8x14_3view_30deg_nominal).
- 07 ladder ran (SOLAR-sb `_runs/gun_ladder_20261009/`, outputs `TPC/smearing/<cfg>/<name>/gun/`). Medians, HD / VD:
  - In hits / deposited: e⁻ 0.86/0.83, γ 0.80/0.79 (pair 0.79, Compton 0.82–0.80), capture 0.69/0.73.
  - In leading cluster / in hits: median 1.00 for e⁻ and γ. Means: e⁻ 0.96/0.95, γ 0.89/0.88. Compton γ median
    0.91/0.89, pair γ 1.00. Capture 0.35/0.33.
  - Containment (interior gun): median ≥0.99 for all particles.
  - Total peak: e⁻ 1.003/0.966, γ 0.902/0.869. This matches gamma_final (0.898/0.871).
  - Default NeutronHP cascade sum: median 11.7 MeV (16–84 %: 6.3–18.4), multiplicity 4. Photon evaporation: 6.099 MeV,
    multiplicity 3. Leading cluster / 6.099 MeV: median 0.45 (default) vs 0.48 (photon evaporation).
- Next: sync the gun outputs to the plotting repo (tar the Gun_* files) and add Gun_Ladder plot commands. Process
  `electrongun_flat` into SOLAR npy (process_sample.py) for the 04 chain against marley_final (de-excitation pile-up).
  Update the §7.6 text: the gamma 0.90 peak comes from the extra sub-threshold loss; the Compton tail comes from
  clustering.

## Narrative rewrite (2026-10-09 ~21:15)
- §7.6 was restructured. Order: intro (hep window vs the 14 MeV gamma, ~10 MeV neutron-gamma and 18.8 MeV hep
  endpoints) → Response at 6 MeV (fig:SMEARING_CAPTURE_SIX) → Neutron-capture simulation (NeutronHP caveat, now in the
  rendered text as the user decided) → CC electron tail (self pile-up) → 10 MeV CC and pure electrons
  (fig:SMEARING_CHAIN_SLICE, now 3 rows) → 10 MeV gammas (new fig:SMEARING_GUN_LADDER) → Full energy range → Reach of
  the hep window (new window shares). Appendix F gained a "Single-particle samples" paragraph and
  fig:APP_SMEARING_GUN_LADDER_VD.
- SOLAR-sb changes for the gun chain:
  - lib/cluster.py `_calib_fallback`: *gun names → marley_final.
  - lib/weights.py: *gun names skip the surface computation (also fixed a rich-markup bug).
  - lib/reco.py: new param COMPUTE_WEIGHTS.
  - 04_smearing_chain.py: SAMPLE_TRUTH entries for electrongun/gammagun; gun workflow params.
  - npy of electrongun_10MeV and electrongun_flat processed for HD and VD (TSignal*DepList skipped).
- Plotting repo: smearing_scripts.txt §1b (pure electron chain); smearing_response_scripts.txt §5 (Gun_Ladder); mappings
  smearing_gun_*.
- Open items:
  - The flat pure-electron sample is not used yet (% TODO).
  - fig:SMEARING_CHAIN_FULL_STEPS / SMEARING_CHAIN_GAMMA and their macros still come from the local full Chain files of
    10-07. SOLAR-sb reran marley/gamma full on 10-09 (rerun 15/17); resync and regenerate before final numbers.
  - VD pure electron has 38 % no-flash clusters (% REVIEW).
  - The page budget \pcstart{s76}{2} is now exceeded (about 6 pages).

## Refresh 2026-10-10/11
- HD Central gamma_final/neutron_final were replaced on 2026-10-09 (new PIC production with light overlay) and the
  marley_final energy calibration was rerun on 10-09. All smearing outputs were rerun (_runs/smearing_refresh_20261010.sh):
  04 full for neutron/radiological, 04 slices for marley/gamma, 06 at 10 and 6 MeV. Everything was synced with
  sync_solar_data --smearing from SOLAR-sb, all figures (smearing + smearing_response) and tables/smearing were
  regenerated, and the macros updated. HD Central gamma now has 3 % no-flash; the 10 MeV gamma overshoot is wrong-flash
  dominated (90 % HDC, 98 % VD).
- 7.1: CHARGE_CONVERSION_EFFECT figures moved to appendix sec:APP_CHARGE_CONVERSION; self pile-up introduced, pointing
  to 7.6. fig:DRIFT_ATTENUATION_CORRECTION now uses marley_final (HD Central / VD Top, SOLAR-sb 01b_lifetime_reco.py
  copied from SOLAR main). Reco vs true correction differs by >5 % for 22 % (HDC) / 41 % (VDT) of the clusters. The old
  figure (legacy marley_official, hd_1x2x6) showed no difference.
- Budgets: \pcstart{s76}{7}, \pcstart{ch7}{25}. The chapter 7 intro was rewritten to cover 7.6 and fit on the first page.

## VD Top marley_final extension (2026-10-11)
- Requested by the user: VD Top statistics should match the other configs.
- Original sample: final_0929.sh (FNAL `justin/final_0929.sh`) ran the final adjflash SolarNuAna on files 0-9999 of the
  official VD radiological MARLEY reco2 dataset (1 event per file, >150k files). Outputs are in FNAL scratch
  `ana/solar_ana_marley_adjflash_final_..._nominal`, with an NFS copy in `SOLAR_transfer/final_raw/vd_nominal_marley_final`
  (merged by hadd2_nfs.sh).
- Extension: FNAL `justin/vd_ext_1011.sh` with `gun_1008/solar_ana_multi.jobscript` (5 files per job, same fcl and tarball).
  Workflows 21827-21831 cover files 10000-59999. Output: `ana/..._nominal_ext`. Test 21825 (`..._ext_test`) must NOT be merged.
- Cost: about 27 CPU-min per event (heavy radiological light). Expect about a week.
- 2026-10-12 fast SolarNuAna takeover:
  - FNAL build: WhichGeneratorType without the per-hit map copy, the same fix as PIC (~30x faster).
  - Tarball: `justin/larsoft_v10_08_01_fast.tar.gz`; the old one is backed up as `.bak-20261012`.
  - Workflows 21827-21831 are PAUSED. Their 10,506 processed or held files are in `justin/vd_ext_1012/skip_dids.txt`.
  - `justin/vd_ext_1012.sh full` submitted 21854-21858: the same MQL ranges, with `gun_1008/solar_ana_multi_skip.jobscript`, MAX_FILES=20, into the same `..._nominal_ext` output directory.
  - Test 21852 (`..._ext_fasttest`) must NOT be merged. Its output equals the old test except Flag; it took ~11-16 min per 5-file job.
  - Once the paused workflows drain, check for held files that ended unprocessed. A MetaCat dataset create was refused (permission error), so use a second skip-list pass instead.

- Downstream, once finished: SOLAR `SOLAR_transfer/final_2026-09-29/vdtop_ext_20261011.sh [transfer|merge|process|calib|all]`.
  - It archives the 10k sample as `marley_final_10k` and merges files 0-59999 chunked from NFS.
  - It runs process_sample plus the vertex/pds/tpc stages, then `final_run2.sh -l rerun_vdtop60k -f calib -c vd_..._nominal`.
  - After that, every VD Top thesis figure, table and macro must be refreshed.
  - Check `/pc/choozdsk01` space first (98 % full on 2026-10-11).

## VD no-flash default (2026-10-11)
- Cause of the VD pure-electron bump at 11-13 MeV: lib/main.py placed no-flash clusters at the drift edge chosen by the
  sign of the TRUE X (truth leak in VD).
- Change on SOLAR-sb, uncommitted (backup lib/main.py.bak-20261011): VD no-flash clusters now get RecoX = middle of the
  drift; HD is unchanged.
- Effect on the VD pure electrons (10 MeV slice, after calibration): no separate bump, but a broader shoulder above the
  peak. 10.5-13 MeV now holds about 18 % (was about 5 %) and 8-9 MeV holds 10 % (was 20 %). Most no-flash VD clusters lie
  near the anode, so the middle default over-corrects them by a median of 11 %.
- Full VD rerun launched 2026-10-11 17:16: `SOLAR_transfer/final_runs/final_run2.sh -l rerun18_vdmid -f calib -c "vd_top vd_shielded"`
  (log `final_runs/rerun18_vdmid.log`).
- After it: rerun the VD neutron/radiological full chains and the marley/gamma 10 MeV slices (04), sync --smearing,
  regenerate the figures, tables and macros, and refresh the ch.8/9 VD numbers. VD Top must be rerun again after the
  60k extension.

## Free electrons flat in 9.5-10.5 MeV (2026-10-12)
- Why: the free-electron row of fig:SMEARING_CHAIN_SLICE used the mono-energetic 10 MeV gun, while the CC and gamma rows
  are flat in true 9.5-10.5 MeV. The 2-30 MeV flat sample holds only ~700 (HD) / ~430 (VD) events in that slice.
- `gun_1008.sh slice`: justIN 21836 (HD, 200 x 50, ana/gun_1011_hd_electron_9.5-10.5MeV) and 21837 (VD, 400 x 25,
  ana/gun_1011_vd_electron_9.5-10.5MeV). Same jobscript as v2 (gun_chain.jobscript, KE_MEV=9.5 KE_MAX_MEV=10.5).
- If the justIN upload fails within 1 s, the bearer token has expired: `htgettoken -a htvaultprod.fnal.gov -i dune --nooidc`
  on dunegpvm03 (Kerberos from kinit_fnal.py). If `justin time` asks for authorisation, the user must open the link
  (each call makes a new link, so do not poll).
- Next: validate (unique vertices, K in 9.5-10.5), merge as SolarNuAna_electrongun_slice10MeV.root (HD + VD), process to npy,
  run 04_smearing_chain.py --name electrongun_slice10MeV --true_range 9.5 10.5 --unweighted --bin_width 0.5, add the name
  to SAMPLE_TRUTH / gun handling (pattern *gun*), sync --smearing, change command 1b in smearing_scripts.txt to the new name,
  regenerate, refresh the fomSmearPureElectron* macros, remove the % TODO under fig:SMEARING_CHAIN_SLICE.
- Thesis layout (same day): fig:SMEARING_CHAIN_SLICE is now CC + free electron (2 rows); gamma row is fig:SMEARING_CHAIN_SLICE_GAMMA.
- 2026-10-12: VD Top smearing outputs refreshed with the mid-drift no-flash default (SOLAR-sb _runs/smearing_refresh_vdtop_20261012:
  marley/gamma slices, neutron/radiological full, 06 at 10 and 6 MeV), synced, figures/tables regenerated, macros updated
  (gamma slice VD Top: 14 % above 10.5 MeV, overshoot 71 % wrong flash / 29 % no flash). VD Bottom Shielded slices and
  neutron/radiological chains still old default (wait for thesis-2c's VD Shielded studies).
- 2026-10-12 evening: 21836/21837 finished (HD 200 good files + 1 empty, VD 400). Merged on FNAL gun_merged_v3, 10k events each,
  copied to SOLAR pnfs as SolarNuAna_electrongun_slice10MeV.root; processed + 04 chain (SOLAR-sb _runs/gun_slice_20261012).
  fig:SMEARING_CHAIN_SLICE bottom row now uses it (smearing_scripts.txt 1b); fomSmearPureElectron* updated; TODO removed.
- 2026-10-12 23:00, split agreed with thesis-cf:
  - thesis-cf owns the VD Top PIC backgrounds (2096825 gamma, 2096826 neutron). They will go in as gamma_final / neutron_final for vd_..._nominal only; the old shared files are archived and VD Shielded is untouched.
  - thesis-cf also owns the single VD Top calibration, analysis and studies rerun with all new samples.
  - Do NOT run merge/process/calib of vdtop_ext_20261011.sh or final_run2 -l rerun_vdtop60k. Only the 'transfer' step is allowed.
  - Signal extension: fast workflows 21854-21858 (thesis-5b polls them). After thesis-cf reports final outputs, refresh the ch.6/7 and app. E/F VD Top figures, tables and macros (reco exports: vertex 01-04, tpc/01, 01b, tpc/03 --no-sb-classifier, smearing).

## marley_official removal + appendix renames (2026-10-13)
- Appendix files now match their TOC letters: d=PDS, e=reco (was f), f=sensitivity (+f_a), g=studies.
- S/B ROC / threshold scan / AUC: new SOLAR-sb script src/physics/calibration/03d_signal_background_roc.py, uncommitted.
  It reads the 03b held-out scores; rerun it after every 03b. Exports were fetched by hand: the registry does not
  route these kinds and SOLAR-sb stores them nested.
- Switched to marley_final: SelectedEnergy limits table + fig:ADJCL_SELECTION, offset-classifier figures (7.4),
  adjacent-count tables (renamed marley_final_*), cheated electron calibration (7.2.1 left, now reco_scripts),
  HD Central gamma energy (7.3 right).
- Signal-only final production: FNAL signal_only_1013.sh, justIN 21865 (HD 1x2x6) and 21866 (VD 1x8x14_3view_30deg).
  Runs files 0-999 of the official signal-only datasets with the fast tarball and the adjflash fcls.
  - Output: ana/solar_ana_marley_adjflash_final_{dune10kt_1x2x6,dunevd10kt_1x8x14_3view_30deg}.
  - TODO when done:
    - merge to data/{hd/hd_1x2x6,vd/vd_1x8x14_3view_30deg}/SolarNuAna_marley_final.root and process_sample;
    - run calibration 01,02,03,04,05 (no 03b: no backgrounds), tpc/01,03 (+no-sb), preselection, pds and vertex scripts;
    - switch the signal-only commands (reco/thesis scripts + thesis versions of the lowe figures) to marley_final;
    - update the e_appendix dataset text (signal-only = marley_final).
  - Remaining marley_official assets: ch.4 (neutrino_cc_*), ch.6 (preselection, cluster distributions, wire planes,
    light map, tpc efficiency scans, 6.4.1 HD/VD comparison), 7.2.1 (ideal fit, HD/VD comparisons),
    7.3 (signal-only gamma energy), 7.4.1 (signal-only comparison).
- 2026-10-13 05:30: signal-only finals done. 21865 HD (319 files, 315k events) and 21866 VD (339 files, 332k events),
  merged as SolarNuAna_marley_final.root in hd_1x2x6 / vd_1x8x14_3view_30deg.
  - SOLAR-sb _runs/signal_only_final_20261013 ran the calibration, detector exports and truth scripts.
  - Every thesis marley_official asset was switched, except the 6.4.1 light-map fits: final samples have no OpFlash
    branches (REVIEW in text).
  - Text corrections:
    - VD flash-finding 3 m macros: ~70 % / ~60 %.
    - 7.2.1: the 11 % is p2, not p0.
    - 7.2.1: background no longer "factor two".
    - 7.4.1: HD signal slightly better than VD.
  - Plot commands: reco_scripts.txt has thesis copies of the lowe-paper signal-only figures; the paper's own
    lowe_scripts.txt is untouched.
- 2026-10-13 06:00: VD Top extension check.
  - 21854-21858 finished, and 'transfer' put 2850 files (162,454 events) in final_raw/vd_nominal_marley_final_ext.
  - The original 10k files held 39,151 events (~3.9 per file), so ~33k events were missing.
  - Cause: of the 10,506 DIDs in vd_ext_1012/skip_dids.txt, only 2,553 had actually been processed by the paused
    21827-21831; the other 7,953 were skipped and never run.
  - Recovery: FNAL vd_ext_1013.sh with gun_1008/solar_ana_multi_include.jobscript (processes only
    vd_ext_1013/include_dids.txt), justIN 21870-21874, same output dir _ext.
  - When done: rerun 'transfer' (it re-tars the whole _ext dir) and check ~196k events in total for files 10000-59999.
    Then tell thesis-cf the transfer is complete; merge/calib is theirs.
- Duplicate guard (agreed with thesis-cf):
  - All 160 files still allocated to the paused 21827-21831 are in the include list (FNAL vd_ext_1013/overlap_allocated_include.txt).
  - Cutoff is 2026-10-13T04:14:47Z (vd_ext_1013/cutoff_utc.txt). At that time the old workflows had 11/27/184/149/148 outputs under _ext/fnal/218{27..31}.
  - At the final transfer, EXCLUDE any hist file under fnal/21827-21831 newer than the cutoff. thesis-cf also de-duplicates (Flag, Event, SignalParticleE) at merge.
- 2026-10-13 14:30: interim VD Top for ch.6/7/app. E.
  - Sample: marley_60k_final, 13,933 files merged (10k orig + 3,933 ext), 1.49 GB; pipeline at SOLAR_transfer/vdtop_interim_20261013.
  - Plot and table commands point VD Top at marley_60k_final through per-config --names pairs. Tables use the new
    script_aggregate_table.py --rename_names marley_60k_final=marley_final.
  - plot_params mappings were extended. Backup of the pre-edit command files: scratchpad scripts_backup_pre60k.
  - Thesis includes for the VD-only figures point to *_marley_60k_final_*; the macros were updated (interim comments)
    and there is a REVIEW in 7_1_section.tex.
  - When thesis-cf's final VD Top rerun lands, revert the commands and includes to marley_final and regenerate.
