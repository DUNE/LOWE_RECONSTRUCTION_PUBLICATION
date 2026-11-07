# Study status rerun40_final_20261021

Epochs: DayNight=2026-09-18T13:00, Sensitivity=2026-09-18T13:00, HEP=2026-09-18T13:00

cut = NHits/OpHits/AdjCl. fiducial = FiducialX/Y/Z (cm) from BestFiducials*.json for that config/folder/analysis/energy (- if no record; * = an essential background has fewer than 2x the MC threshold in the chosen volume, † = the MC gate changed the chosen volume; see MCLimitedReason). DayNight/HEP: smoothed Asimov / profile-likelihood significance; Sensitivity: Δχ² solar-fit-at-reactor / reactor-fit-at-solar (full profile unless a nuisance study).

trend: 🟢 study follows the expected relation to its reference; 🟠 it does not, but one side has a known bug or still awaits its rerun (re-check after the queue); 🔴 it does not and both sides are fresh -> a bug to evaluate; ⚪ informational or no reference. Relations use 2% slack for >=/<= and 5% for ==; the reference for a scan is the neighbouring variant (unc_sig0 vs unc_sig2, charge_Q100 vs charge_Q50, ...). See EXPECTED_TRENDS in src/tools/study_status.py.

Trend summary: 🟢 90 expected, 🟠 4 unexpected but rerun pending, 🔴 27 unexpected on fresh results.

Rows to evaluate (unexpected, both sides fresh):

- hd_1x2x6_centralAPA / Truncated / DayNight / unc_bkg0: == default: 5.57 vs 6.25 UNEXPECTED (fresh)
- hd_1x2x6_centralAPA / Truncated / DayNight / unc_bkg4: == default: 5.57 vs 6.25 UNEXPECTED (fresh)
- hd_1x2x6_centralAPA / Truncated / DayNight / unc_bkg6: == default: 5.57 vs 6.25 UNEXPECTED (fresh)
- hd_1x2x6_centralAPA / Truncated / DayNight / oscpoint_solar: == default: 5.57 vs 6.25 UNEXPECTED (fresh)
- hd_1x2x6_centralAPA / Truncated / HEP / fiduc_truth: >= default: 13.40 vs 14.01 UNEXPECTED (fresh)
- hd_1x2x6_lateralAPA / Truncated / DayNight / unc_bkg0: == default: 2.01 vs 2.72 UNEXPECTED (fresh)
- hd_1x2x6_lateralAPA / Truncated / DayNight / unc_bkg4: == default: 2.01 vs 2.72 UNEXPECTED (fresh)
- hd_1x2x6_lateralAPA / Truncated / DayNight / unc_bkg6: == default: 2.01 vs 2.72 UNEXPECTED (fresh)
- hd_1x2x6_lateralAPA / Truncated / DayNight / oscpoint_solar: == default: 2.01 vs 2.72 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / DayNight / unc_bkg0: == default: 2.38 vs 1.48 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / HEP / unc_bkg0: == default: 1.98 vs 2.44 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / DayNight / unc_bkg4: == default: 2.38 vs 1.48 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / HEP / unc_bkg4: == default: 1.98 vs 2.44 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / DayNight / unc_bkg6: == default: 2.38 vs 1.48 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / HEP / unc_bkg6: == default: 1.98 vs 2.44 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / DayNight / oscpoint_solar: == default: 1.32 vs 1.48 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_nominal / Truncated / DayNight / membrane_veto_off: >= default: 1.21 vs 1.48 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / DayNight / unc_bkg0: == default: 4.75 vs 5.06 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / HEP / unc_bkg0: == default: 2.25 vs 3.34 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / DayNight / unc_bkg4: == default: 4.75 vs 5.06 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / HEP / unc_bkg4: == default: 2.25 vs 3.34 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / DayNight / unc_bkg6: == default: 4.75 vs 5.06 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / HEP / unc_bkg6: == default: 2.25 vs 3.34 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / Sensitivity / nuisance_sin13: >= default: 4.92 vs 5.08 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / Sensitivity / nuisance_escale: >= default: 4.55 vs 5.08 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / DayNight / oscpoint_solar: == default: 4.80 vs 5.06 UNEXPECTED (fresh)
- vd_1x8x14_3view_30deg_shielded / Truncated / DayNight / membrane_veto_off: >= default: 4.76 vs 5.06 UNEXPECTED (fresh)


## hd_1x2x6_centralAPA

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 1/5/7 | 0/200/0*† | 6.25σ@30y | 5.10σ@20y | 10-21 00:35 | ok | - |
| Truncated | HEP | default | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.22σ@20y | 10-21 00:38 | ok | - |
| Truncated | Sensitivity | default | 1/9/4 | 40/180/0*† | Δχ² 6.64/6.39@30y | Δχ² 2.47/2.38@10y | 10-21 01:47 | ok | - |
| Nominal | DayNight | default | - | 60/120/320 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | HEP | default | - | 20/160/120 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | Sensitivity | default | - | 20/160/140 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Reduced | DayNight | default | - | 140/280/260* | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Reduced | HEP | default | - | 20/160/20*† | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Reduced | Sensitivity | default | - | 160/160/320*† | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Pessimistic | DayNight | default | - | 0/200/240*† | - | - | - | missing | - |
| Pessimistic | HEP | default | - | 20/260/120† | - | - | - | missing | - |
| Pessimistic | Sensitivity | default | - | 0/240/180*† | - | - | - | missing | - |
| Truncated | HEP | unc_sig20 | 4/4/4 | 60/160/60*† | 15.36σ@30y | 13.39σ@20y | 10-20 16:37 | ok | 🟢 >= default: 15.36 vs 14.01 OK |
| Truncated | HEP | unc_sig40 | 4/4/4 | 60/160/60*† | 12.60σ@30y | 10.98σ@20y | 10-20 16:42 | ok | 🟢 <= default: 12.60 vs 14.01 OK |
| Truncated | Sensitivity | unc_sig0 | 1/4/4 | 0/200/60* | Δχ² 40.01/39.89@30y | Δχ² 13.80/13.75@10y | 10-20 16:53 | cut!=ref(1, 9, 4) | 🟢 >= unc_sig2: 40.01 vs 7.40 OK |
| Truncated | Sensitivity | unc_sig2 | 1/4/4 | 0/200/60* | Δχ² 7.40/7.11@30y | Δχ² 3.40/3.27@10y | 10-20 17:18 | cut!=ref(1, 9, 4) | 🟢 >= default: 7.40 vs 6.64 OK |
| Truncated | Sensitivity | unc_sig6 | 1/4/4 | 0/200/60* | Δχ² 6.00/5.77@30y | Δχ² 2.12/2.04@10y | 10-20 17:19 | cut!=ref(1, 9, 4) | 🟢 <= default: 6.00 vs 6.64 OK |
| Truncated | DayNight | unc_bkg0 | 1/4/4 | 100/300/60 | 5.57σ@30y | 4.55σ@20y | 10-20 17:24 | ok | **🔴 == default: 5.57 vs 6.25 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg0 | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-20 17:27 | ok | 🟢 == default: 14.01 vs 14.01 OK |
| Truncated | DayNight | unc_bkg4 | 1/4/4 | 100/300/60 | 5.57σ@30y | 4.55σ@20y | 10-20 17:50 | ok | **🔴 == default: 5.57 vs 6.25 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg4 | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-20 17:53 | ok | 🟢 == default: 14.01 vs 14.01 OK |
| Truncated | DayNight | unc_bkg6 | 1/4/4 | 100/300/60 | 5.57σ@30y | 4.55σ@20y | 10-20 17:51 | ok | **🔴 == default: 5.57 vs 6.25 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg6 | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-20 17:55 | ok | 🟢 == default: 14.01 vs 14.01 OK |
| Truncated | Sensitivity | nuisance_nominal | 1/4/4 | 0/200/60* | Δχ² 8.07/7.77@30y | Δχ² 2.94/2.83@10y | 10-20 18:50 | cut!=ref(1, 9, 4) | 🟢 >= nuisance_sin13: 8.07 vs 8.07 OK |
| Truncated | Sensitivity | nuisance_sin13 | 1/4/4 | 0/200/60* | Δχ² 8.07/7.77@30y | Δχ² 2.94/2.83@10y | 10-20 19:20 | cut!=ref(1, 9, 4) | 🟢 >= default: 8.07 vs 6.64 OK |
| Truncated | Sensitivity | nuisance_escale | 1/4/4 | 0/200/60* | Δχ² 6.22/5.99@30y | Δχ² 2.34/2.25@10y | 10-20 18:46 | cut!=ref(1, 9, 4) | **🟠 >= default: 6.22 vs 6.64 UNEXPECTED (rerun pending)** |
| Truncated | DayNight | energy_spk | 3/7/2 | 100/300/60 | 2.62σ@30y | 2.14σ@20y | 10-20 14:08 | ok | ⚪ vs default: 2.62 vs 6.25 |
| Truncated | HEP | energy_spk | 4/5/12 | 60/160/60*† | 32.24σ@30y | 28.04σ@20y | 10-20 14:11 | ok | ⚪ vs default: 32.24 vs 14.01 |
| Truncated | Sensitivity | energy_spk | 1/4/11 | 0/200/60* | Δχ² 18.04/17.51@30y | Δχ² 6.34/6.14@10y | 10-20 15:10 | ok | ⚪ vs default: 18.04 vs 6.64 |
| Truncated | DayNight | energy_maink | 3/6/7 | 100/300/60 | 5.01σ@30y | 4.09σ@20y | 10-20 10:14 | ok | ⚪ vs default: 5.01 vs 6.25 |
| Truncated | HEP | energy_maink | 4/5/9 | 60/160/60*† | 15.43σ@30y | 13.40σ@20y | 10-20 10:17 | ok | ⚪ vs default: 15.43 vs 14.01 |
| Truncated | Sensitivity | energy_maink | 3/6/4 | 0/200/60* | Δχ² 2.79/2.67@30y | Δχ² 1.19/1.14@10y | 10-20 11:50 | ok | ⚪ vs default: 2.79 vs 6.64 |
| Truncated | DayNight | charge_Q0 | 1/4/4 | 160/280/240* | 4.48σ@30y | 3.66σ@20y | 10-20 15:22 | ok | ⚪ vs default: 4.48 vs 6.25 |
| Truncated | HEP | charge_Q0 | 4/4/4 | 100/160/0*† | 4.19σ@30y | 3.66σ@20y | 10-20 15:25 | ok | ⚪ vs default: 4.19 vs 14.01 |
| Truncated | Sensitivity | charge_Q0 | 1/4/4 | 160/180/240*† | Δχ² 3.68/3.54@30y | Δχ² 1.49/1.43@10y | 10-20 15:38 | cut!=ref(1, 9, 4) | ⚪ vs default: 3.68 vs 6.64 |
| Truncated | DayNight | charge_Q50 | 1/4/4 | 160/280/240* | 4.06σ@30y | 3.31σ@20y | 10-20 15:51 | ok | ⚪ vs charge_Q0: 4.06 vs 4.48 |
| Truncated | HEP | charge_Q50 | 4/4/4 | 100/160/0*† | 4.74σ@30y | 4.13σ@20y | 10-20 15:54 | ok | ⚪ vs charge_Q0: 4.74 vs 4.19 |
| Truncated | Sensitivity | charge_Q50 | 1/4/4 | 160/180/240*† | Δχ² 8.26/8.00@30y | Δχ² 3.05/2.95@10y | 10-20 16:06 | cut!=ref(1, 9, 4) | ⚪ vs charge_Q0: 8.26 vs 3.68 |
| Truncated | DayNight | charge_Q100 | 1/4/4 | 160/280/240* | 4.08σ@30y | 3.33σ@20y | 10-20 16:03 | ok | ⚪ vs charge_Q50: 4.08 vs 4.06 |
| Truncated | HEP | charge_Q100 | 4/4/4 | 100/160/0*† | 4.49σ@30y | 3.92σ@20y | 10-20 16:06 | ok | ⚪ vs charge_Q50: 4.49 vs 4.74 |
| Truncated | Sensitivity | charge_Q100 | 1/4/4 | 160/180/240*† | Δχ² 8.38/8.11@30y | Δχ² 3.09/2.99@10y | 10-20 16:18 | cut!=ref(1, 9, 4) | ⚪ vs charge_Q50: 8.38 vs 8.26 |
| Truncated | DayNight | charge_Q500 | - | 160/280/240* | - | - | - | missing | ⚪ vs charge_Q100: n/a |
| Truncated | HEP | charge_Q500 | 2/4/2 | 100/160/0*† | 8.92σ@30y | 7.78σ@20y | 10-19 12:04 | ok | ⚪ vs charge_Q100: 8.92 vs 4.49 |
| Truncated | Sensitivity | charge_Q500 | 1/5/4 | 160/180/240*† | Δχ² 8.71/8.48@30y | Δχ² 3.18/3.09@10y | 10-19 12:17 | cut!=ref(1, 9, 4) | ⚪ vs charge_Q100: 8.71 vs 8.38 |
| Nominal | DayNight | bkgmodel_nominal | 1/4/4 | 60/120/320 | 2.15σ@30y | 1.75σ@20y | 10-20 13:17 | ok | 🟢 <= Truncated default: 2.15 vs 6.25 OK |
| Nominal | HEP | bkgmodel_nominal | 4/4/4 | 20/160/120 | 12.34σ@30y | 10.76σ@20y | 10-20 13:20 | ok | 🟢 <= Truncated default: 12.34 vs 14.01 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 1/4/4 | 20/160/140 | Δχ² 1.25/1.20@30y | Δχ² 0.62/0.59@10y | 10-20 13:33 | cut!=ref(1, 9, 4) | 🟢 <= Truncated default: 1.25 vs 6.64 OK |
| Reduced | DayNight | bkgmodel_reduced | 1/4/4 | 140/280/260* | 8.66σ@30y | 7.07σ@20y | 10-20 12:47 | ok | 🟢 >= Truncated default: 8.66 vs 6.25 OK |
| Reduced | HEP | bkgmodel_reduced | 4/4/4 | 20/160/20*† | 14.58σ@30y | 12.71σ@20y | 10-20 12:50 | ok | 🟢 >= Truncated default: 14.58 vs 14.01 OK |
| Reduced | Sensitivity | bkgmodel_reduced | 1/4/4 | 160/160/320*† | Δχ² 17.09/16.77@30y | Δχ² 5.99/5.87@10y | 10-20 13:02 | cut!=ref(1, 9, 4) | 🟢 >= Truncated default: 17.09 vs 6.64 OK |
| Pessimistic | DayNight | bkgmodel_pessimistic | 1/4/4 | 0/200/240*† | 1.41σ@30y | 1.15σ@20y | 10-21 00:35 | ok | 🟢 <= Truncated default: 1.41 vs 6.25 OK |
| Pessimistic | HEP | bkgmodel_pessimistic | 2/11/4 | 20/260/120† | 11.32σ@30y | 9.87σ@20y | 10-21 00:37 | ok | 🟢 <= Truncated default: 11.32 vs 14.01 OK |
| Pessimistic | Sensitivity | bkgmodel_pessimistic | 1/4/4 | 0/240/180*† | Δχ² 0.67/0.64@30y | Δχ² 0.34/0.33@10y | 10-21 01:48 | ok | 🟢 <= Truncated default: 0.67 vs 6.64 OK |
| Truncated | DayNight | sb_simple | 1/4/7 | 0/220/0* | 3.99σ@30y | 3.26σ@20y | 10-18 09:28 | ok | - |
| Truncated | HEP | sb_simple | 2/19/4 | 0/160/0*† | 13.24σ@30y | 11.54σ@20y | 10-18 09:30 | ok | - |
| Truncated | Sensitivity | sb_simple | 1/4/4 | 0/180/0*† | Δχ² 6.06/5.83@30y | Δχ² 2.27/2.19@10y | 10-18 10:40 | ok | - |
| Truncated | DayNight | sb_gateonly | 1/5/5 | 0/200/60*† | 3.71σ@30y | 3.03σ@20y | 10-18 09:48 | ok | - |
| Truncated | HEP | sb_gateonly | 2/8/4 | 60/160/60*† | 13.60σ@30y | 11.86σ@20y | 10-18 09:51 | ok | - |
| Truncated | Sensitivity | sb_gateonly | 1/5/4 | 40/180/60*† | Δχ² 5.71/5.49@30y | Δχ² 2.17/2.09@10y | 10-18 11:06 | ok | - |
| Truncated | DayNight | ncveto_618 | 1/4/7 | 0/220/0* | 3.99σ@30y | 3.26σ@20y | 10-18 11:53 | ok | - |
| Truncated | HEP | ncveto_618 | 2/19/4 | 0/160/0*† | 13.24σ@30y | 11.54σ@20y | 10-18 11:56 | ok | - |
| Truncated | Sensitivity | ncveto_618 | 1/4/4 | 0/180/0*† | Δχ² 6.06/5.83@30y | Δχ² 2.27/2.19@10y | 10-18 13:02 | ok | - |
| Truncated | DayNight | sb_lowthr | - | 0/200/0*† | - | - | - | missing | - |
| Truncated | HEP | sb_lowthr | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | sb_lowthr | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | HEP | sb_simple_hepwin | 4/5/3 | 0/160/0*† | 12.09σ@30y | 10.54σ@20y | 10-18 12:38 | ok | - |
| Truncated | DayNight | sb_off | 4/4/3 | 0/200/60 | 2.83σ@30y | 2.31σ@20y | 10-19 02:01 | ok | ⚪ vs default: 2.83 vs 6.25 |
| Truncated | HEP | sb_off | 4/4/4 | 60/160/60*† | 12.74σ@30y | 11.11σ@20y | 10-19 02:04 | ok | ⚪ vs default: 12.74 vs 14.01 |
| Truncated | Sensitivity | sb_off | 3/5/3 | 0/200/60* | Δχ² 3.14/3.02@30y | Δχ² 1.27/1.23@10y | 10-19 03:51 | ok | ⚪ vs default: 3.14 vs 6.64 |
| Truncated | DayNight | sb_off_veto | 1/4/4 | 0/200/60 | 5.45σ@30y | 4.45σ@20y | 10-17 19:09 | ok | ⚪ vs default: 5.45 vs 6.25 |
| Truncated | HEP | sb_off_veto | 3/4/4 | 60/160/60*† | 12.75σ@30y | 11.12σ@20y | 10-17 19:12 | ok | ⚪ vs default: 12.75 vs 14.01 |
| Truncated | Sensitivity | sb_off_veto | 1/4/4 | 0/200/60* | Δχ² 5.20/4.99@30y | Δχ² 2.00/1.92@10y | 10-17 20:18 | ok | ⚪ vs default: 5.20 vs 6.64 |
| Truncated | DayNight | sb_remove | 1/4/5 | 0/200/60*† | 3.74σ@30y | 3.05σ@20y | 10-19 16:58 | ok | - |
| Truncated | HEP | sb_remove | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-19 17:01 | ok | - |
| Truncated | Sensitivity | sb_remove | 1/4/4 | 40/180/60*† | Δχ² 5.67/5.45@30y | Δχ² 2.16/2.07@10y | 10-19 18:12 | ok | - |
| Truncated | Sensitivity | sb_remove_radsmooth | 1/4/5 | 40/180/60*† | Δχ² 3.09/2.96@30y | Δχ² 1.32/1.27@10y | 10-19 20:46 | ok | - |
| Truncated | DayNight | sb_remove_fixfid | 1/4/4 | 100/300/60 | 5.50σ@30y | 4.49σ@20y | 10-19 20:05 | ok | - |
| Truncated | HEP | sb_remove_fixfid | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-19 20:08 | ok | - |
| Truncated | Sensitivity | sb_remove_fixfid | 1/4/4 | 0/200/60* | Δχ² 6.02/5.79@30y | Δχ² 2.28/2.19@10y | 10-19 21:14 | ok | - |
| Truncated | DayNight | sb_remove_rs_noradfid | 1/4/5 | 0/200/0*† | 3.72σ@30y | 3.04σ@20y | 10-19 21:53 | ok | - |
| Truncated | HEP | sb_remove_rs_noradfid | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-19 21:57 | ok | - |
| Truncated | Sensitivity | sb_remove_rs_noradfid | 1/4/5 | 40/180/60*† | Δχ² 3.09/2.96@30y | Δχ² 1.32/1.27@10y | 10-20 00:03 | ok | - |
| Truncated | Sensitivity | sb_remove_rse_noradfid | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_fixfid | 1/4/4 | 0/200/60* | Δχ² 4.88/4.69@30y | Δχ² 1.90/1.83@10y | 10-19 23:56 | ok | - |
| Truncated | DayNight | fid_rescan | 1/4/4 | 0/200/60*† | 5.54σ@30y | 4.52σ@20y | 10-20 20:32 | ok | - |
| Truncated | HEP | fid_rescan | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-20 20:35 | ok | - |
| Truncated | Sensitivity | fid_rescan | - | 40/180/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | rad_smooth | 1/5/5 | 0/200/60* | Δχ² 3.11/2.97@30y | Δχ² 1.33/1.27@10y | 10-19 13:05 | ok | ⚪ vs default: 3.11 vs 6.64 |
| Truncated | Sensitivity | rad_smooth_end | 1/5/4 | 0/200/60* | Δχ² 4.57/4.39@30y | Δχ² 1.80/1.73@10y | 10-19 23:49 | ok | - |
| Truncated | Sensitivity | rad_floor3 | - | 0/200/60* | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth | - | 40/180/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth_end | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | DayNight | rad_unified_smooth | 1/5/7 | 0/200/0*† | 6.25σ@30y | 5.10σ@20y | 10-20 20:18 | ok | - |
| Truncated | HEP | rad_unified_smooth | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.22σ@20y | 10-20 20:21 | ok | - |
| Truncated | Sensitivity | rad_unified_smooth | 1/9/4 | 40/180/0*† | Δχ² 6.60/6.36@30y | Δχ² 2.46/2.36@10y | 10-20 21:44 | ok | - |
| Truncated | DayNight | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | HEP | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | DayNight | rad_unified | 1/5/7 | 0/200/0*† | 6.39σ@30y | 5.22σ@20y | 10-20 17:38 | ok | - |
| Truncated | HEP | rad_unified | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.22σ@20y | 10-20 17:41 | ok | - |
| Truncated | Sensitivity | rad_unified | 1/4/4 | 40/180/0*† | Δχ² 7.08/6.82@30y | Δχ² 2.62/2.52@10y | 10-20 19:06 | ok | - |
| Truncated | DayNight | rad_off | - | 0/200/0*† | - | - | - | missing | - |
| Truncated | HEP | rad_off | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | rad_off | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | HEP | hep_notail | 4/4/4 | 60/160/60*† | 14.18σ@30y | 12.36σ@20y | 10-16 12:05 | ok | ⚪ vs default: 14.18 vs 14.01 |
| Truncated | DayNight | fid_oneband | 1/5/4 | 0/200/60 | 3.72σ@30y | 3.03σ@20y | 10-16 23:41 | ok | - |
| Truncated | HEP | fid_oneband | 2/8/4 | 60/160/60*† | 13.61σ@30y | 11.86σ@20y | 10-16 23:44 | ok | - |
| Truncated | Sensitivity | fid_oneband | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 01:05 | ok | - |
| Truncated | DayNight | fid_zlim | 1/4/4 | 0/200/60 | 5.17σ@30y | 4.22σ@20y | 10-17 02:19 | ok | - |
| Truncated | HEP | fid_zlim | 2/8/4 | 60/160/60*† | 13.70σ@30y | 11.94σ@20y | 10-17 02:22 | ok | - |
| Truncated | Sensitivity | fid_zlim | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 03:31 | ok | - |
| Truncated | DayNight | fid_exp30 | 1/4/4 | 0/200/60 | 5.17σ@30y | 4.22σ@20y | 10-17 16:35 | ok | - |
| Truncated | HEP | fid_exp30 | 2/8/4 | 60/160/60*† | 13.70σ@30y | 11.94σ@20y | 10-17 16:38 | ok | - |
| Truncated | Sensitivity | fid_exp30 | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 17:47 | ok | - |
| Truncated | HEP | fid_hepbands22 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | DayNight | fid_bandmin1 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bandmin1 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bandmin1 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_bandrel5 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bandrel5 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bandrel5 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_highband | - | 0/200/60 | - | - | - | missing | - |
| Truncated | HEP | fid_highband | 2/13/4 | 40/160/0*† | 14.01σ@30y | 12.22σ@20y | 10-17 15:13 | ok | - |
| Truncated | Sensitivity | fid_highband | - | 0/200/60* | - | - | - | missing | - |
| Truncated | DayNight | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor | - | 0/200/0*† | - | - | - | missing | - |
| Truncated | HEP | fid_radfloor | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_radfloor | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor_one | 2/4/4 | 0/200/60 | 5.53σ@30y | 4.51σ@20y | 10-17 21:01 | ok | - |
| Truncated | HEP | fid_radfloor_one | 2/8/4 | 60/160/60*† | 13.61σ@30y | 11.86σ@20y | 10-17 22:17 | ok | - |
| Truncated | Sensitivity | fid_radfloor_one | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 23:28 | ok | - |
| Truncated | DayNight | fid_oldrule | 1/4/4 | 0/200/60*† | 5.32σ@30y | 4.35σ@20y | 10-18 04:55 | ok | - |
| Truncated | HEP | fid_oldrule | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_oldrule | - | 40/180/60*† | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_300_60 | 1/4/4 | 100/300/60*† | 5.52σ@30y | 4.51σ@20y | 10-18 04:44 | ok | - |
| Truncated | HEP | fid_v100_300_60 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_300_60 | - | 40/180/60*† | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_300_0 | 1/4/5 | 0/300/0*† | 3.58σ@30y | 2.92σ@20y | 10-18 05:04 | ok | - |
| Truncated | HEP | fid_v0_300_0 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_300_0 | - | 40/180/60*† | - | - | - | missing | - |
| Truncated | DayNight | fid_noveto | - | 100/300/60 | - | - | - | missing | - |
| Truncated | HEP | fid_noveto | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_noveto | - | 0/200/60* | - | - | - | missing | - |
| Truncated | DayNight | fid_dn616 | - | 0/200/60 | - | - | - | missing | - |
| Truncated | DayNight | fid_bandmax | 1/4/5 | 140/300/260 | 4.40σ@30y | 3.59σ@20y | 10-17 17:56 | ok | - |
| Truncated | HEP | fid_bandmax | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bandmax | - | 0/200/60* | - | - | - | missing | - |
| Truncated | DayNight | fid_lowband | - | 0/200/0*† | - | - | - | missing | - |
| Truncated | HEP | fid_lowband | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_lowband | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | DayNight | fid_v140_300_60 | 1/4/5 | 140/300/60*† | 5.14σ@30y | 4.20σ@20y | 10-18 04:33 | ok | - |
| Truncated | HEP | fid_v140_300_60 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v140_300_60 | - | 40/180/60*† | - | - | - | missing | - |
| Truncated | DayNight | fid_v80_240_160 | 2/4/4 | 80/240/160 | 5.13σ@30y | 4.19σ@20y | 10-17 19:33 | ok | - |
| Truncated | HEP | fid_v80_240_160 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v80_240_160 | - | 0/200/60* | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_200_260 | 1/4/4 | 0/200/260 | 5.07σ@30y | 4.14σ@20y | 10-17 19:07 | ok | - |
| Truncated | HEP | fid_v0_200_260 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_200_260 | - | 0/200/60* | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_60_480 | - | 0/200/0*† | - | - | - | missing | - |
| Truncated | HEP | fid_v100_60_480 | - | 60/160/60*† | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_60_480 | - | 40/180/0*† | - | - | - | missing | - |
| Truncated | DayNight | fid_fullspec | 1/4/3 | 0/240/60 | 3.64σ@30y | 2.97σ@20y | 10-17 01:54 | ok | - |
| Truncated | HEP | fid_fullspec | 3/4/4 | 40/180/60 | 14.11σ@30y | 12.30σ@20y | 10-17 01:57 | ok | - |
| Truncated | Sensitivity | fid_fullspec | 1/4/4 | 0/200/60 | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 03:03 | ok | - |
| Truncated | DayNight | fid_nosb | 1/4/4 | 0/200/60 | 5.17σ@30y | 4.22σ@20y | 10-17 04:47 | ok | - |
| Truncated | HEP | fid_nosb | 2/8/4 | 60/160/60*† | 13.70σ@30y | 11.94σ@20y | 10-17 04:49 | ok | - |
| Truncated | Sensitivity | fid_nosb | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 06:01 | ok | - |
| Truncated | HEP | hep_plain_opt | 3/4/4 | 60/160/60*† | 12.73σ@30y | 11.10σ@20y | 10-17 03:58 | ok | - |
| Truncated | DayNight | mcfloor_10 | 1/4/4 | 0/200/60 | 5.17σ@30y | 4.22σ@20y | 10-16 23:23 | ok | ⚪ vs default: 5.17 vs 6.25 |
| Truncated | HEP | mcfloor_10 | 2/8/4 | 60/160/60*† | 13.70σ@30y | 11.94σ@20y | 10-16 23:25 | ok | ⚪ vs default: 13.70 vs 14.01 |
| Truncated | Sensitivity | mcfloor_10 | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 00:39 | ok | ⚪ vs default: 6.05 vs 6.64 |
| Truncated | DayNight | mcfloor_25 | 1/4/4 | 0/200/60 | 5.17σ@30y | 4.22σ@20y | 10-17 07:06 | ok | ⚪ vs default: 5.17 vs 6.25 |
| Truncated | HEP | mcfloor_25 | 2/8/6 | 60/160/60*† | 13.44σ@30y | 11.71σ@20y | 10-17 07:09 | ok | ⚪ vs default: 13.44 vs 14.01 |
| Truncated | Sensitivity | mcfloor_25 | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 08:08 | ok | ⚪ vs default: 6.05 vs 6.64 |
| Truncated | DayNight | mcfloor_50 | 1/4/4 | 0/200/60 | 5.17σ@30y | 4.22σ@20y | 10-17 07:14 | ok | ⚪ vs default: 5.17 vs 6.25 |
| Truncated | HEP | mcfloor_50 | 2/4/8 | 60/160/60*† | 12.89σ@30y | 11.24σ@20y | 10-17 07:16 | ok | ⚪ vs default: 12.89 vs 14.01 |
| Truncated | Sensitivity | mcfloor_50 | 1/4/4 | 0/200/60* | Δχ² 6.05/5.84@30y | Δχ² 2.27/2.19@10y | 10-17 08:19 | ok | ⚪ vs default: 6.05 vs 6.64 |
| Truncated | DayNight | bkgsub_s1 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | bkgsub_s1 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | Sensitivity | bkgsub_s1 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | DayNight | bkgsub_s2 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | bkgsub_s2 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | Sensitivity | bkgsub_s2 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | DayNight | bkgsub_s3 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | bkgsub_s3 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | Sensitivity | bkgsub_s3 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_extmask | 3/4/4 | 60/160/60*† | 8.37σ@30y | 7.30σ@20y | 10-16 22:10 | ok | ⚪ vs default: 8.37 vs 14.01 |
| Truncated | HEP | hep_looseshape | 4/4/6 | 60/160/60*† | 15.01σ@30y | 13.08σ@20y | 10-17 04:56 | ok | ⚪ vs default: 15.01 vs 14.01 |
| Truncated | HEP | hep_looseshape_plain | 4/4/6 | 60/160/60*† | 13.72σ@30y | 11.96σ@20y | 10-17 05:53 | ok | ⚪ vs default: 13.72 vs 14.01 |
| Truncated | HEP | hep_looseshape_nh | - | 60/160/60*† | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_looseshape_win | 4/4/5 | 60/160/60*† | 13.68σ@30y | 11.92σ@20y | 10-18 12:10 | ok | ⚪ vs default: 13.68 vs 14.01 |
| Truncated | HEP | sb_hep90 | - | 60/160/60*† | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_sbmodel | 3/20/5 | 60/160/60*† | 5.58σ@30y | 4.86σ@20y | 10-09 20:43 | ok | ⚪ vs default: 5.58 vs 14.01 |
| Truncated | HEP | hep_plain | 3/20/5 | 60/160/60*† | 5.42σ@30y | 4.72σ@20y | 10-09 21:08 | ok | ⚪ vs default: 5.42 vs 14.01 |
| Truncated | DayNight | ncveto | 1/4/3 | 0/200/0*† | 4.05σ@30y | 3.30σ@20y | 10-09 14:15 | ok | ⚪ vs default: 4.05 vs 6.25 |
| Truncated | Sensitivity | ncveto | 3/5/4 | 40/180/0*† | Δχ² 3.41/3.30@30y | Δχ² 1.35/1.30@10y | 10-09 15:23 | ok | ⚪ vs default: 3.41 vs 6.64 |
| Truncated | DayNight | ncveto_off | 1/4/4 | 0/200/60 | 4.52σ@30y | 3.69σ@20y | 10-17 08:55 | ok | ⚪ vs default: 4.52 vs 6.25 |
| Truncated | Sensitivity | ncveto_off | 1/7/4 | 0/200/60* | Δχ² 3.86/3.72@30y | Δχ² 1.53/1.47@10y | 10-17 10:02 | ok | ⚪ vs default: 3.86 vs 6.64 |
| Truncated | DayNight | mcgate_50 | 1/4/3 | 0/200/0*† | 4.95σ@30y | 4.04σ@20y | 10-10 00:35 | ok | ⚪ vs default: 4.95 vs 6.25 |
| Truncated | HEP | mcgate_50 | 3/9/5 | 60/160/60*† | 7.83σ@30y | 6.83σ@20y | 10-10 00:38 | ok | ⚪ vs default: 7.83 vs 14.01 |
| Truncated | Sensitivity | mcgate_50 | 3/4/1 | 40/180/0*† | Δχ² 1.14/1.11@30y | Δχ² 0.51/0.50@10y | 10-10 01:40 | ok | ⚪ vs default: 1.14 vs 6.64 |
| Truncated | DayNight | mcgate_20 | 1/4/4 | - | 5.06σ@30y | 4.13σ@20y | 10-10 02:30 | ok | ⚪ vs default: 5.06 vs 6.25 |
| Truncated | HEP | mcgate_20 | 1/4/5 | - | 13.74σ@30y | 11.98σ@20y | 10-10 02:33 | ok | ⚪ vs default: 13.74 vs 14.01 |
| Truncated | Sensitivity | mcgate_20 | 1/13/4 | - | Δχ² 3.37/3.27@30y | Δχ² 1.31/1.27@10y | 10-10 03:44 | ok | ⚪ vs default: 3.37 vs 6.64 |
| Truncated | DayNight | mcgate_0 | 1/4/4 | 0/200/0*† | 5.06σ@30y | 4.13σ@20y | 10-10 04:29 | ok | ⚪ vs default: 5.06 vs 6.25 |
| Truncated | HEP | mcgate_0 | 1/4/5 | 60/160/60*† | 14.51σ@30y | 12.65σ@20y | 10-10 04:32 | ok | ⚪ vs default: 14.51 vs 14.01 |
| Truncated | Sensitivity | mcgate_0 | 1/13/4 | 40/180/0*† | Δχ² 3.37/3.27@30y | Δχ² 1.31/1.27@10y | 10-10 05:41 | ok | ⚪ vs default: 3.37 vs 6.64 |
| Truncated | HEP | hep_mcf3 | 1/4/6 | 60/160/60*† | 14.51σ@30y | 12.65σ@20y | 10-10 13:09 | ok | ⚪ vs default: 14.51 vs 14.01 |
| Truncated | HEP | hep_mcf5 | 1/4/5 | 60/160/60*† | 14.52σ@30y | 12.66σ@20y | 10-10 13:31 | ok | ⚪ vs default: 14.52 vs 14.01 |
| Truncated | DayNight | oscpoint_solar | 1/4/4 | 100/300/60 | 5.57σ@30y | 4.55σ@20y | 10-20 18:47 | ok | **🔴 == default: 5.57 vs 6.25 UNEXPECTED (fresh)** |
| Truncated | HEP | oscpoint_solar | 4/4/4 | 60/160/60*† | 14.01σ@30y | 12.21σ@20y | 10-20 18:50 | ok | 🟢 == default: 14.01 vs 14.01 OK |
| Truncated | DayNight | oscpoint_reactor | 1/4/4 | 100/300/60 | 4.19σ@30y | 3.42σ@20y | 10-20 12:13 | ok | 🟢 <= default: 4.19 vs 6.25 OK |
| Truncated | HEP | oscpoint_reactor | 4/4/4 | 60/160/60*† | 14.00σ@30y | 12.20σ@20y | 10-20 12:16 | ok | 🟢 == default: 14.00 vs 14.01 OK |
| Truncated | DayNight | fiduc_truth | 1/5/4 | 0/200/60*† | 6.55σ@30y | 5.34σ@20y | 10-20 10:15 | ok | 🟢 >= default: 6.55 vs 6.25 OK |
| Truncated | HEP | fiduc_truth | 3/13/4 | 0/160/60*† | 13.40σ@30y | 11.68σ@20y | 10-20 10:18 | ok | **🔴 >= default: 13.40 vs 14.01 UNEXPECTED (fresh)** |
| Truncated | Sensitivity | fiduc_truth | 1/4/4 | 0/180/60*† | Δχ² 8.24/7.93@30y | Δχ² 3.01/2.90@10y | 10-20 11:54 | ok | 🟢 >= default: 8.24 vs 6.64 OK |
| Truncated | DayNight | fiduc_truth_refvol | - | 0/200/0*† | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | HEP | fiduc_truth_refvol | - | 60/160/60*† | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | Sensitivity | fiduc_truth_refvol | - | 40/180/0*† | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | DayNight | bkg_gamma_cluster | 1/4/4 | 0/260/240 | 5.34σ@30y | 4.36σ@20y | 10-20 14:15 | ok | ⚪ vs default: 5.34 vs 6.25 |
| Truncated | HEP | bkg_gamma_cluster | 4/4/4 | 40/260/0 | 12.70σ@30y | 11.07σ@20y | 10-20 14:18 | ok | ⚪ vs default: 12.70 vs 14.01 |
| Truncated | Sensitivity | bkg_gamma_cluster | 1/4/4 | 0/260/240 | Δχ² 4.40/4.24@30y | Δχ² 1.72/1.66@10y | 10-20 14:30 | cut!=ref(1, 9, 4) | ⚪ vs default: 4.40 vs 6.64 |
| Truncated | DayNight | bkg_gamma_total | 1/4/4 | 60/300/0 | 5.88σ@30y | 4.80σ@20y | 10-20 14:43 | ok | ⚪ vs default: 5.88 vs 6.25 |
| Truncated | HEP | bkg_gamma_total | 4/4/4 | 0/300/60 | 6.79σ@30y | 5.92σ@20y | 10-20 14:46 | ok | ⚪ vs default: 6.79 vs 14.01 |
| Truncated | Sensitivity | bkg_gamma_total | 1/4/4 | 60/300/0 | Δχ² 6.12/5.90@30y | Δχ² 2.30/2.22@10y | 10-20 14:59 | cut!=ref(1, 9, 4) | ⚪ vs default: 6.12 vs 6.64 |
| Truncated | Sensitivity | legacy_fit | - | 40/180/0*† | - | - | - | missing | ⚪ vs default: n/a |

## hd_1x2x6_lateralAPA

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 2/4/5 | 60/120/0 | 2.72σ@30y | 2.22σ@20y | 10-21 00:32 | ok | - |
| Truncated | HEP | default | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-21 00:35 | ok | - |
| Truncated | Sensitivity | default | 2/4/5 | 60/120/0 | Δχ² 1.65/1.58@30y | Δχ² 0.74/0.71@10y | 10-21 01:44 | ok | - |
| Nominal | DayNight | default | - | 20/80/340 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | HEP | default | - | 0/240/100* | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | Sensitivity | default | - | 60/280/220 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Reduced | DayNight | default | - | 40/80/120 | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Reduced | HEP | default | - | 20/200/120* | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Reduced | Sensitivity | default | - | 40/80/120 | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Pessimistic | DayNight | default | - | 80/80/100 | - | - | - | missing | - |
| Pessimistic | HEP | default | - | 60/240/60 | - | - | - | missing | - |
| Pessimistic | Sensitivity | default | - | 60/240/60 | - | - | - | missing | - |
| Truncated | HEP | unc_sig20 | 2/20/8 | 60/240/0 | 3.75σ@30y | 3.27σ@20y | 10-20 13:45 | ok | 🟢 >= default: 3.75 vs 3.42 OK |
| Truncated | HEP | unc_sig40 | 2/20/8 | 60/240/0 | 3.08σ@30y | 2.68σ@20y | 10-20 13:49 | ok | 🟢 <= default: 3.08 vs 3.42 OK |
| Truncated | Sensitivity | unc_sig0 | 3/4/5 | 20/180/0 | Δχ² 3.09/3.08@30y | Δχ² 1.03/1.03@10y | 10-20 14:52 | cut!=ref(2, 4, 5) | 🟢 >= unc_sig2: 3.09 vs 1.58 OK |
| Truncated | Sensitivity | unc_sig2 | 3/4/5 | 20/180/0 | Δχ² 1.58/1.54@30y | Δχ² 0.74/0.72@10y | 10-20 14:55 | cut!=ref(2, 4, 5) | **🟠 >= default: 1.58 vs 1.65 UNEXPECTED (rerun pending)** |
| Truncated | Sensitivity | unc_sig6 | 3/4/5 | 20/180/0 | Δχ² 0.90/0.87@30y | Δχ² 0.37/0.36@10y | 10-20 14:57 | cut!=ref(2, 4, 5) | 🟢 <= default: 0.90 vs 1.65 OK |
| Truncated | DayNight | unc_bkg0 | 3/4/5 | 20/180/0 | 2.01σ@30y | 1.64σ@20y | 10-20 14:17 | ok | **🔴 == default: 2.01 vs 2.72 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg0 | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 14:20 | ok | 🟢 == default: 3.42 vs 3.42 OK |
| Truncated | DayNight | unc_bkg4 | 3/4/5 | 20/180/0 | 2.01σ@30y | 1.64σ@20y | 10-20 14:23 | ok | **🔴 == default: 2.01 vs 2.72 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg4 | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 14:26 | ok | 🟢 == default: 3.42 vs 3.42 OK |
| Truncated | DayNight | unc_bkg6 | 3/4/5 | 20/180/0 | 2.01σ@30y | 1.64σ@20y | 10-20 14:25 | ok | **🔴 == default: 2.01 vs 2.72 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg6 | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 14:28 | ok | 🟢 == default: 3.42 vs 3.42 OK |
| Truncated | Sensitivity | nuisance_nominal | 3/4/5 | 20/180/0 | Δχ² 1.11/1.07@30y | Δχ² 0.49/0.47@10y | 10-20 18:55 | cut!=ref(2, 4, 5) | 🟢 >= nuisance_sin13: 1.11 vs 1.11 OK |
| Truncated | Sensitivity | nuisance_sin13 | 3/4/5 | 20/180/0 | Δχ² 1.11/1.07@30y | Δχ² 0.49/0.47@10y | 10-20 19:22 | cut!=ref(2, 4, 5) | **🟠 >= default: 1.11 vs 1.65 UNEXPECTED (rerun pending)** |
| Truncated | Sensitivity | nuisance_escale | 3/4/5 | 20/180/0 | Δχ² 1.04/1.01@30y | Δχ² 0.48/0.47@10y | 10-20 19:00 | cut!=ref(2, 4, 5) | **🟠 >= default: 1.04 vs 1.65 UNEXPECTED (rerun pending)** |
| Truncated | DayNight | energy_spk | 4/6/20 | 20/180/0 | 5.79σ@30y | 4.73σ@20y | 10-20 15:52 | ok | ⚪ vs default: 5.79 vs 2.72 |
| Truncated | HEP | energy_spk | 4/6/16 | 60/240/0 | 26.04σ@30y | 22.64σ@20y | 10-20 15:55 | ok | ⚪ vs default: 26.04 vs 3.42 |
| Truncated | Sensitivity | energy_spk | 1/4/8 | 20/180/0 | Δχ² 7.35/7.12@30y | Δχ² 2.67/2.59@10y | 10-20 16:55 | ok | ⚪ vs default: 7.35 vs 1.65 |
| Truncated | DayNight | energy_maink | 4/4/5 | 20/180/0 | 2.13σ@30y | 1.74σ@20y | 10-20 10:12 | ok | ⚪ vs default: 2.13 vs 2.72 |
| Truncated | HEP | energy_maink | 2/4/14 | 60/240/0 | 12.42σ@30y | 10.78σ@20y | 10-20 10:14 | ok | ⚪ vs default: 12.42 vs 3.42 |
| Truncated | Sensitivity | energy_maink | 4/4/5 | 20/180/0 | Δχ² 1.36/1.31@30y | Δχ² 0.64/0.62@10y | 10-20 11:43 | ok | ⚪ vs default: 1.36 vs 1.65 |
| Truncated | DayNight | charge_Q0 | 3/7/7 | - | 1.17σ@30y | 0.96σ@20y | 10-15 09:46 | ok | ⚪ vs default: 1.17 vs 2.72 |
| Truncated | HEP | charge_Q0 | 3/6/3 | - | 1.14σ@30y | 0.99σ@20y | 10-15 09:49 | ok | ⚪ vs default: 1.14 vs 3.42 |
| Truncated | Sensitivity | charge_Q0 | 2/4/6 | - | Δχ² 0.76/0.74@30y | Δχ² 0.39/0.38@10y | 10-15 10:02 | cut!=ref(2, 4, 5) | ⚪ vs default: 0.76 vs 1.65 |
| Truncated | DayNight | charge_Q50 | 3/7/7 | - | 1.23σ@30y | 1.00σ@20y | 10-15 10:40 | ok | ⚪ vs charge_Q0: 1.23 vs 1.17 |
| Truncated | HEP | charge_Q50 | 3/6/3 | - | 1.18σ@30y | 1.02σ@20y | 10-15 10:43 | ok | ⚪ vs charge_Q0: 1.18 vs 1.14 |
| Truncated | Sensitivity | charge_Q50 | 2/4/6 | - | Δχ² 7.51/7.27@30y | Δχ² 2.71/2.62@10y | 10-15 10:55 | cut!=ref(2, 4, 5) | ⚪ vs charge_Q0: 7.51 vs 0.76 |
| Truncated | DayNight | charge_Q100 | 3/7/7 | - | 1.19σ@30y | 0.97σ@20y | 10-15 11:33 | ok | ⚪ vs charge_Q50: 1.19 vs 1.23 |
| Truncated | HEP | charge_Q100 | 3/6/3 | - | 1.14σ@30y | 1.00σ@20y | 10-15 11:37 | ok | ⚪ vs charge_Q50: 1.14 vs 1.18 |
| Truncated | Sensitivity | charge_Q100 | 2/4/6 | - | Δχ² 7.67/7.42@30y | Δχ² 2.76/2.67@10y | 10-15 11:49 | cut!=ref(2, 4, 5) | ⚪ vs charge_Q50: 7.67 vs 7.51 |
| Truncated | DayNight | charge_Q500 | 3/7/7 | - | 1.21σ@30y | 0.99σ@20y | 10-15 12:25 | ok | ⚪ vs charge_Q100: 1.21 vs 1.19 |
| Truncated | HEP | charge_Q500 | 3/4/3 | - | 0.96σ@30y | 0.83σ@20y | 10-15 12:27 | ok | ⚪ vs charge_Q100: 0.96 vs 1.14 |
| Truncated | Sensitivity | charge_Q500 | 2/4/6 | - | Δχ² 9.47/9.20@30y | Δχ² 3.36/3.26@10y | 10-15 12:39 | cut!=ref(2, 4, 5) | ⚪ vs charge_Q100: 9.47 vs 7.67 |
| Nominal | DayNight | bkgmodel_nominal | 3/4/5 | 20/80/340 | 0.58σ@30y | 0.47σ@20y | 10-20 17:25 | ok | 🟢 <= Truncated default: 0.58 vs 2.72 OK |
| Nominal | HEP | bkgmodel_nominal | 2/20/8 | 0/240/100* | 2.99σ@30y | 2.60σ@20y | 10-20 17:28 | ok | 🟢 <= Truncated default: 2.99 vs 3.42 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 3/4/5 | 60/280/220 | Δχ² 0.20/0.20@30y | Δχ² 0.09/0.09@10y | 10-20 17:41 | cut!=ref(2, 4, 5) | 🟢 <= Truncated default: 0.20 vs 1.65 OK |
| Reduced | DayNight | bkgmodel_reduced | 3/4/5 | 40/80/120 | 4.82σ@30y | 3.93σ@20y | 10-20 12:47 | ok | 🟢 >= Truncated default: 4.82 vs 2.72 OK |
| Reduced | HEP | bkgmodel_reduced | 2/20/8 | 20/200/120* | 4.87σ@30y | 4.25σ@20y | 10-20 12:50 | ok | 🟢 >= Truncated default: 4.87 vs 3.42 OK |
| Reduced | Sensitivity | bkgmodel_reduced | 3/4/5 | 40/80/120 | Δχ² 4.46/4.31@30y | Δχ² 1.69/1.63@10y | 10-20 13:02 | cut!=ref(2, 4, 5) | 🟢 >= Truncated default: 4.46 vs 1.65 OK |
| Pessimistic | DayNight | bkgmodel_pessimistic | 2/4/7 | 80/80/100 | 0.69σ@30y | 0.56σ@20y | 10-21 00:30 | ok | 🟢 <= Truncated default: 0.69 vs 2.72 OK |
| Pessimistic | HEP | bkgmodel_pessimistic | 2/19/8 | 60/240/60 | 2.92σ@30y | 2.54σ@20y | 10-21 00:33 | ok | 🟢 <= Truncated default: 2.92 vs 3.42 OK |
| Pessimistic | Sensitivity | bkgmodel_pessimistic | 2/4/5 | 60/240/60 | Δχ² 0.23/0.22@30y | Δχ² 0.10/0.10@10y | 10-21 01:41 | ok | 🟢 <= Truncated default: 0.23 vs 1.65 OK |
| Truncated | DayNight | sb_simple | 2/4/7 | 60/120/0 | 2.64σ@30y | 2.16σ@20y | 10-18 09:50 | ok | - |
| Truncated | HEP | sb_simple | 3/6/3 | 0/200/100*† | 1.56σ@30y | 1.36σ@20y | 10-18 09:53 | ok | - |
| Truncated | Sensitivity | sb_simple | 2/4/7 | 60/120/0 | Δχ² 1.41/1.35@30y | Δχ² 0.63/0.61@10y | 10-18 11:00 | ok | - |
| Truncated | DayNight | sb_gateonly | 3/4/5 | 60/120/0 | 2.57σ@30y | 2.10σ@20y | 10-18 09:28 | ok | - |
| Truncated | HEP | sb_gateonly | 3/20/5 | 60/240/0 | 1.81σ@30y | 1.58σ@20y | 10-18 09:31 | ok | - |
| Truncated | Sensitivity | sb_gateonly | 2/4/5 | 60/120/0 | Δχ² 1.46/1.41@30y | Δχ² 0.66/0.64@10y | 10-18 10:45 | ok | - |
| Truncated | DayNight | ncveto_618 | 2/4/7 | 60/120/0 | 2.65σ@30y | 2.16σ@20y | 10-18 12:07 | ok | - |
| Truncated | HEP | ncveto_618 | 3/6/3 | 0/200/100*† | 1.56σ@30y | 1.36σ@20y | 10-18 12:10 | ok | - |
| Truncated | Sensitivity | ncveto_618 | 1/5/6 | 60/120/0 | Δχ² 1.31/1.27@30y | Δχ² 0.59/0.57@10y | 10-18 13:21 | ok | - |
| Truncated | DayNight | sb_lowthr | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | sb_lowthr | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | sb_lowthr | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | sb_simple_hepwin | 3/4/4 | 0/200/100*† | 1.87σ@30y | 1.62σ@20y | 10-18 12:44 | ok | - |
| Truncated | DayNight | sb_off | 2/5/5 | 20/180/0 | 1.46σ@30y | 1.19σ@20y | 10-19 01:55 | ok | ⚪ vs default: 1.46 vs 2.72 |
| Truncated | HEP | sb_off | 3/19/8 | 60/240/0 | 3.38σ@30y | 2.94σ@20y | 10-19 01:58 | ok | ⚪ vs default: 3.38 vs 3.42 |
| Truncated | Sensitivity | sb_off | 3/16/3 | 60/280/0 | Δχ² 0.65/0.63@30y | Δχ² 0.33/0.33@10y | 10-19 03:44 | ok | ⚪ vs default: 0.65 vs 1.65 |
| Truncated | DayNight | sb_off_veto | 3/4/8 | 60/280/320 | 1.17σ@30y | 0.96σ@20y | 10-17 19:38 | ok | ⚪ vs default: 1.17 vs 2.72 |
| Truncated | HEP | sb_off_veto | 4/4/6 | 60/240/0 | 1.13σ@30y | 0.98σ@20y | 10-17 19:41 | ok | ⚪ vs default: 1.13 vs 3.42 |
| Truncated | Sensitivity | sb_off_veto | 3/4/8 | 20/280/120 | Δχ² 0.50/0.48@30y | Δχ² 0.27/0.26@10y | 10-17 20:48 | ok | ⚪ vs default: 0.50 vs 1.65 |
| Truncated | DayNight | sb_remove | 3/4/5 | 80/120/20 | 2.64σ@30y | 2.15σ@20y | 10-19 17:26 | ok | - |
| Truncated | HEP | sb_remove | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-19 17:30 | ok | - |
| Truncated | Sensitivity | sb_remove | 2/4/5 | 60/120/20 | Δχ² 1.54/1.48@30y | Δχ² 0.69/0.67@10y | 10-19 18:48 | ok | - |
| Truncated | Sensitivity | sb_remove_radsmooth | - | - | - | - | - | missing | - |
| Truncated | DayNight | sb_remove_fixfid | 3/4/5 | 20/180/0 | 1.96σ@30y | 1.60σ@20y | 10-20 00:29 | ok | - |
| Truncated | HEP | sb_remove_fixfid | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 00:32 | ok | - |
| Truncated | Sensitivity | sb_remove_fixfid | 3/4/5 | 20/180/0 | Δχ² 1.03/0.99@30y | Δχ² 0.49/0.47@10y | 10-20 01:35 | ok | - |
| Truncated | DayNight | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | HEP | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_noradfid | - | 60/120/0 | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_fixfid | 3/4/5 | 20/180/0 | Δχ² 1.03/0.99@30y | Δχ² 0.49/0.47@10y | 10-20 01:10 | ok | - |
| Truncated | DayNight | fid_rescan | 2/4/5 | 80/120/20 | 2.66σ@30y | 2.17σ@20y | 10-20 20:27 | ok | - |
| Truncated | HEP | fid_rescan | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 20:30 | ok | - |
| Truncated | Sensitivity | fid_rescan | 2/4/5 | 60/120/20 | Δχ² 1.52/1.46@30y | Δχ² 0.68/0.66@10y | 10-20 21:51 | ok | - |
| Truncated | Sensitivity | rad_smooth | 2/4/5 | 20/180/0 | Δχ² 1.00/0.96@30y | Δχ² 0.47/0.46@10y | 10-19 13:00 | ok | ⚪ vs default: 1.00 vs 1.65 |
| Truncated | Sensitivity | rad_smooth_end | 2/4/5 | 20/180/0 | Δχ² 1.02/0.99@30y | Δχ² 0.49/0.47@10y | 10-19 23:45 | ok | - |
| Truncated | Sensitivity | rad_floor3 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth_end | - | 60/120/0 | - | - | - | missing | - |
| Truncated | DayNight | rad_unified_smooth | 2/4/5 | 60/120/0 | 2.72σ@30y | 2.22σ@20y | 10-20 20:09 | ok | - |
| Truncated | HEP | rad_unified_smooth | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 20:12 | ok | - |
| Truncated | Sensitivity | rad_unified_smooth | 2/4/5 | 60/120/0 | Δχ² 1.65/1.58@30y | Δχ² 0.74/0.71@10y | 10-20 21:27 | ok | - |
| Truncated | DayNight | rad_default_check | 2/4/5 | 60/120/0 | 2.72σ@30y | 2.22σ@20y | 10-20 22:39 | ok | - |
| Truncated | HEP | rad_default_check | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | rad_default_check | 2/4/5 | 60/120/0 | Δχ² 1.65/1.58@30y | Δχ² 0.74/0.71@10y | 10-20 23:38 | ok | - |
| Truncated | DayNight | rad_unified | 2/4/5 | 60/120/0 | 2.74σ@30y | 2.24σ@20y | 10-20 17:31 | ok | - |
| Truncated | HEP | rad_unified | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 17:34 | ok | - |
| Truncated | Sensitivity | rad_unified | 2/4/5 | 60/120/0 | Δχ² 1.65/1.58@30y | Δχ² 0.74/0.71@10y | 10-20 18:56 | ok | - |
| Truncated | DayNight | rad_off | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | rad_off | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | rad_off | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | hep_notail | 2/19/16 | 60/240/0* | 3.28σ@30y | 2.85σ@20y | 10-16 12:03 | ok | ⚪ vs default: 3.28 vs 3.42 |
| Truncated | DayNight | fid_oneband | 3/4/6 | 60/300/160 | 1.94σ@30y | 1.58σ@20y | 10-16 16:07 | ok | - |
| Truncated | HEP | fid_oneband | 3/20/5 | 60/240/0* | 1.83σ@30y | 1.59σ@20y | 10-16 16:11 | ok | - |
| Truncated | Sensitivity | fid_oneband | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-16 21:14 | ok | - |
| Truncated | DayNight | fid_zlim | 3/7/7 | 60/300/160 | 1.39σ@30y | 1.14σ@20y | 10-17 00:40 | ok | - |
| Truncated | HEP | fid_zlim | 3/6/3 | 60/240/0* | 1.59σ@30y | 1.38σ@20y | 10-17 00:44 | ok | - |
| Truncated | Sensitivity | fid_zlim | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 01:54 | ok | - |
| Truncated | DayNight | fid_exp30 | 3/4/6 | 60/300/160 | 1.40σ@30y | 1.15σ@20y | 10-17 16:03 | ok | - |
| Truncated | HEP | fid_exp30 | 3/6/5 | 60/240/0 | 1.72σ@30y | 1.50σ@20y | 10-17 16:06 | ok | - |
| Truncated | Sensitivity | fid_exp30 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 17:21 | ok | - |
| Truncated | HEP | fid_hepbands22 | - | 60/240/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_bandmin1 | 3/4/6 | 60/300/160 | 1.94σ@30y | 1.58σ@20y | 10-17 18:28 | ok | - |
| Truncated | HEP | fid_bandmin1 | 3/20/5 | 60/240/0 | 1.83σ@30y | 1.59σ@20y | 10-17 18:31 | ok | - |
| Truncated | Sensitivity | fid_bandmin1 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 19:41 | ok | - |
| Truncated | DayNight | fid_bandrel5 | 3/4/6 | 60/300/160 | 1.94σ@30y | 1.58σ@20y | 10-17 15:33 | ok | - |
| Truncated | HEP | fid_bandrel5 | 3/6/3 | 60/240/0 | 1.59σ@30y | 1.38σ@20y | 10-17 15:36 | ok | - |
| Truncated | Sensitivity | fid_bandrel5 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 16:46 | ok | - |
| Truncated | DayNight | fid_highband | - | 60/300/160 | - | - | - | missing | - |
| Truncated | HEP | fid_highband | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_highband | - | 60/300/160 | - | - | - | missing | - |
| Truncated | DayNight | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | fid_radfloor | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_radfloor | - | 60/120/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor_one | 3/4/5 | 60/300/160 | 2.04σ@30y | 1.66σ@20y | 10-17 20:21 | ok | - |
| Truncated | HEP | fid_radfloor_one | 3/20/5 | 60/240/0 | 1.83σ@30y | 1.59σ@20y | 10-17 22:27 | ok | - |
| Truncated | Sensitivity | fid_radfloor_one | 2/4/5 | 20/180/0 | Δχ² 1.03/0.99@30y | Δχ² 0.49/0.47@10y | 10-17 23:44 | ok | - |
| Truncated | DayNight | fid_oldrule | 3/4/6 | 60/300/160 | 1.91σ@30y | 1.56σ@20y | 10-18 07:06 | ok | - |
| Truncated | HEP | fid_oldrule | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_oldrule | - | 60/120/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_noveto | - | 20/180/0 | - | - | - | missing | - |
| Truncated | HEP | fid_noveto | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_noveto | - | 20/180/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_dn616 | 3/4/6 | 60/300/160 | 1.94σ@30y | 1.58σ@20y | 10-17 19:15 | ok | - |
| Truncated | DayNight | fid_bandmax | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bandmax | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bandmax | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_lowband | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | fid_lowband | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_lowband | - | 60/120/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_60_480 | - | 60/120/0 | - | - | - | missing | - |
| Truncated | HEP | fid_v100_60_480 | - | 60/240/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_60_480 | - | 60/120/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_fullspec | 3/4/6 | 60/300/160 | 1.94σ@30y | 1.58σ@20y | 10-16 23:34 | ok | - |
| Truncated | HEP | fid_fullspec | 3/20/5 | 60/240/0 | 1.83σ@30y | 1.59σ@20y | 10-16 23:37 | ok | - |
| Truncated | Sensitivity | fid_fullspec | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 01:01 | ok | - |
| Truncated | DayNight | fid_nosb | 3/4/8 | 60/280/320 | 1.34σ@30y | 1.09σ@20y | 10-17 02:51 | ok | - |
| Truncated | HEP | fid_nosb | 3/6/3 | 60/240/0* | 1.59σ@30y | 1.38σ@20y | 10-17 02:54 | ok | - |
| Truncated | Sensitivity | fid_nosb | 2/4/8 | 20/280/120 | Δχ² 0.65/0.63@30y | Δχ² 0.33/0.32@10y | 10-17 04:08 | ok | - |
| Truncated | HEP | hep_plain_opt | 1/4/5 | 60/240/0* | 1.28σ@30y | 1.11σ@20y | 10-17 01:47 | ok | - |
| Truncated | DayNight | mcfloor_10 | 3/7/7 | 60/300/160 | 1.39σ@30y | 1.14σ@20y | 10-16 15:22 | ok | ⚪ vs default: 1.39 vs 2.72 |
| Truncated | HEP | mcfloor_10 | 3/6/5 | 60/240/0* | 1.57σ@30y | 1.37σ@20y | 10-16 15:25 | ok | ⚪ vs default: 1.57 vs 3.42 |
| Truncated | Sensitivity | mcfloor_10 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-16 16:56 | ok | ⚪ vs default: 0.94 vs 1.65 |
| Truncated | DayNight | mcfloor_25 | 3/7/7 | 60/300/160 | 1.39σ@30y | 1.14σ@20y | 10-16 22:16 | ok | ⚪ vs default: 1.39 vs 2.72 |
| Truncated | HEP | mcfloor_25 | 3/6/5 | 60/240/0* | 1.57σ@30y | 1.37σ@20y | 10-16 22:19 | ok | ⚪ vs default: 1.57 vs 3.42 |
| Truncated | Sensitivity | mcfloor_25 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-16 23:32 | ok | ⚪ vs default: 0.94 vs 1.65 |
| Truncated | DayNight | mcfloor_50 | 3/7/7 | 60/300/160 | 1.39σ@30y | 1.14σ@20y | 10-17 06:07 | ok | ⚪ vs default: 1.39 vs 2.72 |
| Truncated | HEP | mcfloor_50 | 3/4/16 | 60/240/0* | 1.38σ@30y | 1.20σ@20y | 10-17 06:10 | ok | ⚪ vs default: 1.38 vs 3.42 |
| Truncated | Sensitivity | mcfloor_50 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 07:21 | ok | ⚪ vs default: 0.94 vs 1.65 |
| Truncated | DayNight | bkgsub_s1 | 1/5/8 | 40/140/120 | 1.96σ@30y | 1.60σ@20y | 10-17 06:41 | ok | ⚪ vs default: 1.96 vs 2.72 |
| Truncated | HEP | bkgsub_s1 | 1/6/9 | 0/0/0*† | 1.94σ@30y | 1.42σ@20y | 10-17 06:44 | ok | ⚪ vs default: 1.94 vs 3.42 |
| Truncated | Sensitivity | bkgsub_s1 | 2/4/11 | 40/120/120 | Δχ² 1.29/1.24@30y | Δχ² 0.59/0.57@10y | 10-17 08:00 | ok | ⚪ vs default: 1.29 vs 1.65 |
| Truncated | DayNight | bkgsub_s2 | 3/4/20 | 0/300/120 | 1.47σ@30y | 1.20σ@20y | 10-17 08:19 | ok | ⚪ vs default: 1.47 vs 2.72 |
| Truncated | HEP | bkgsub_s2 | 4/11/4 | 0/0/0*† | 1.70σ@30y | 1.48σ@20y | 10-17 08:21 | ok | ⚪ vs default: 1.70 vs 3.42 |
| Truncated | Sensitivity | bkgsub_s2 | 1/4/9 | 0/100/220 | Δχ² 0.72/0.69@30y | Δχ² 0.35/0.34@10y | 10-17 09:26 | ok | ⚪ vs default: 0.72 vs 1.65 |
| Truncated | DayNight | bkgsub_s3 | 3/7/8 | 0/100/20 | 1.51σ@30y | 1.23σ@20y | 10-17 08:56 | ok | ⚪ vs default: 1.51 vs 2.72 |
| Truncated | HEP | bkgsub_s3 | 1/6/4 | 0/0/0*† | 1.89σ@30y | 1.35σ@20y | 10-17 08:59 | ok | ⚪ vs default: 1.89 vs 3.42 |
| Truncated | Sensitivity | bkgsub_s3 | 2/4/8 | 0/20/320 | Δχ² 0.75/0.72@30y | Δχ² 0.36/0.35@10y | 10-17 10:09 | ok | ⚪ vs default: 0.75 vs 1.65 |
| Truncated | HEP | hep_extmask | 2/20/13 | 60/240/0* | 3.05σ@30y | 2.66σ@20y | 10-17 04:55 | ok | ⚪ vs default: 3.05 vs 3.42 |
| Truncated | HEP | hep_looseshape | 4/10/5 | 60/240/0* | 4.02σ@30y | 3.50σ@20y | 10-17 05:02 | ok | ⚪ vs default: 4.02 vs 3.42 |
| Truncated | HEP | hep_looseshape_plain | 4/6/6 | 60/240/0* | 3.43σ@30y | 2.99σ@20y | 10-17 05:44 | ok | ⚪ vs default: 3.43 vs 3.42 |
| Truncated | HEP | hep_looseshape_nh | - | 60/240/0 | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_looseshape_win | 3/4/5 | 60/240/0 | 2.23σ@30y | 1.94σ@20y | 10-18 11:38 | ok | ⚪ vs default: 2.23 vs 3.42 |
| Truncated | HEP | sb_hep90 | - | 60/240/0 | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_sbmodel | 4/10/5 | 60/240/0 | 2.34σ@30y | 2.04σ@20y | 10-09 20:41 | ok | ⚪ vs default: 2.34 vs 3.42 |
| Truncated | HEP | hep_plain | 4/10/5 | 60/240/0 | 2.27σ@30y | 1.98σ@20y | 10-09 21:08 | ok | ⚪ vs default: 2.27 vs 3.42 |
| Truncated | DayNight | ncveto | 2/7/5 | 60/120/0 | 1.09σ@30y | 0.89σ@20y | 10-09 14:13 | ok | ⚪ vs default: 1.09 vs 2.72 |
| Truncated | Sensitivity | ncveto | 3/15/4 | 60/120/0 | Δχ² 0.66/0.63@30y | Δχ² 0.34/0.33@10y | 10-09 15:13 | ok | ⚪ vs default: 0.66 vs 1.65 |
| Truncated | DayNight | ncveto_off | 2/7/6 | 60/300/160 | 1.23σ@30y | 1.01σ@20y | 10-17 10:07 | ok | ⚪ vs default: 1.23 vs 2.72 |
| Truncated | Sensitivity | ncveto_off | 2/4/4 | 60/300/160 | Δχ² 0.78/0.75@30y | Δχ² 0.37/0.36@10y | 10-17 11:14 | ok | ⚪ vs default: 0.78 vs 1.65 |
| Truncated | DayNight | mcgate_50 | 2/7/5 | 60/120/0 | 1.27σ@30y | 1.04σ@20y | 10-10 00:33 | ok | ⚪ vs default: 1.27 vs 2.72 |
| Truncated | HEP | mcgate_50 | 2/19/14 | 60/240/0 | 3.34σ@30y | 2.91σ@20y | 10-10 00:36 | ok | ⚪ vs default: 3.34 vs 3.42 |
| Truncated | Sensitivity | mcgate_50 | 3/16/4 | 60/120/0 | Δχ² 0.59/0.57@30y | Δχ² 0.29/0.28@10y | 10-10 01:37 | ok | ⚪ vs default: 0.59 vs 1.65 |
| Truncated | DayNight | mcgate_20 | 3/7/7 | 60/300/160 | 1.39σ@30y | 1.14σ@20y | 10-17 03:00 | ok | ⚪ vs default: 1.39 vs 2.72 |
| Truncated | HEP | mcgate_20 | 3/6/3 | 60/240/0 | 1.58σ@30y | 1.38σ@20y | 10-17 03:03 | ok | ⚪ vs default: 1.58 vs 3.42 |
| Truncated | Sensitivity | mcgate_20 | 2/4/6 | 60/300/160 | Δχ² 0.94/0.90@30y | Δχ² 0.46/0.45@10y | 10-17 04:15 | ok | ⚪ vs default: 0.94 vs 1.65 |
| Truncated | DayNight | mcgate_0 | 3/8/5 | 60/120/0 | 1.25σ@30y | 1.02σ@20y | 10-10 04:09 | ok | ⚪ vs default: 1.25 vs 2.72 |
| Truncated | HEP | mcgate_0 | 2/19/14 | 60/240/0 | 3.34σ@30y | 2.91σ@20y | 10-10 04:12 | ok | ⚪ vs default: 3.34 vs 3.42 |
| Truncated | Sensitivity | mcgate_0 | 3/16/4 | 60/120/0 | Δχ² 0.57/0.56@30y | Δχ² 0.28/0.27@10y | 10-10 05:14 | ok | ⚪ vs default: 0.57 vs 1.65 |
| Truncated | HEP | hep_mcf3 | 2/19/20 | 60/240/0 | 3.34σ@30y | 2.91σ@20y | 10-10 13:08 | ok | ⚪ vs default: 3.34 vs 3.42 |
| Truncated | HEP | hep_mcf5 | 2/19/20 | 60/240/0 | 3.34σ@30y | 2.91σ@20y | 10-10 13:28 | ok | ⚪ vs default: 3.34 vs 3.42 |
| Truncated | DayNight | oscpoint_solar | 3/4/5 | 20/180/0 | 2.01σ@30y | 1.64σ@20y | 10-20 18:47 | ok | **🔴 == default: 2.01 vs 2.72 UNEXPECTED (fresh)** |
| Truncated | HEP | oscpoint_solar | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 18:51 | ok | 🟢 == default: 3.42 vs 3.42 OK |
| Truncated | DayNight | oscpoint_reactor | 3/4/5 | 20/180/0 | 1.53σ@30y | 1.25σ@20y | 10-20 12:12 | ok | 🟢 <= default: 1.53 vs 2.72 OK |
| Truncated | HEP | oscpoint_reactor | 2/20/8 | 60/240/0 | 3.42σ@30y | 2.98σ@20y | 10-20 12:15 | ok | 🟢 == default: 3.42 vs 3.42 OK |
| Truncated | DayNight | fiduc_truth | 2/4/5 | 80/80/280 | 3.17σ@30y | 2.59σ@20y | 10-20 10:09 | ok | 🟢 >= default: 3.17 vs 2.72 OK |
| Truncated | HEP | fiduc_truth | 2/6/3 | 80/220/0 | 6.87σ@30y | 5.99σ@20y | 10-20 10:12 | ok | 🟢 >= default: 6.87 vs 3.42 OK |
| Truncated | Sensitivity | fiduc_truth | 1/4/5 | 80/120/0 | Δχ² 2.93/2.82@30y | Δχ² 1.18/1.14@10y | 10-20 11:48 | ok | 🟢 >= default: 2.93 vs 1.65 OK |
| Truncated | DayNight | fiduc_truth_refvol | - | 60/120/0 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | HEP | fiduc_truth_refvol | - | 60/240/0 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | Sensitivity | fiduc_truth_refvol | - | 60/120/0 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | DayNight | bkg_gamma_cluster | 3/4/5 | 80/120/0 | 2.54σ@30y | 2.08σ@20y | 10-20 16:20 | ok | ⚪ vs default: 2.54 vs 2.72 |
| Truncated | HEP | bkg_gamma_cluster | 2/20/8 | 0/200/100 | 2.39σ@30y | 2.08σ@20y | 10-20 16:23 | ok | ⚪ vs default: 2.39 vs 3.42 |
| Truncated | Sensitivity | bkg_gamma_cluster | 3/4/5 | 80/120/0 | Δχ² 1.44/1.39@30y | Δχ² 0.66/0.63@10y | 10-20 16:36 | cut!=ref(2, 4, 5) | ⚪ vs default: 1.44 vs 1.65 |
| Truncated | DayNight | bkg_gamma_total | 3/4/5 | 80/120/40 | 2.56σ@30y | 2.09σ@20y | 10-20 16:23 | ok | ⚪ vs default: 2.56 vs 2.72 |
| Truncated | HEP | bkg_gamma_total | 2/20/8 | 20/260/100 | 0.14σ@30y | 0.13σ@20y | 10-20 16:26 | ok | ⚪ vs default: 0.14 vs 3.42 |
| Truncated | Sensitivity | bkg_gamma_total | 3/4/5 | 80/120/40 | Δχ² 1.49/1.43@30y | Δχ² 0.67/0.64@10y | 10-20 16:39 | cut!=ref(2, 4, 5) | ⚪ vs default: 1.49 vs 1.65 |
| Truncated | Sensitivity | legacy_fit | - | 60/120/0 | - | - | - | missing | ⚪ vs default: n/a |

## vd_1x8x14_3view_30deg_nominal

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 5/16/20 | 140/0/340 | 1.48σ@30y | 1.21σ@20y | 10-21 06:22 | ok | - |
| Truncated | HEP | default | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-21 06:25 | ok | - |
| Truncated | Sensitivity | default | 5/16/20 | 140/0/340 | Δχ² 0.63/0.61@30y | Δχ² 0.34/0.33@10y | 10-21 07:42 | ok | - |
| Nominal | DayNight | default | - | 0/60/20 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | HEP | default | - | 0/60/460 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | Sensitivity | default | - | 0/160/220 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Reduced | DayNight | default | - | 0/0/100 | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Reduced | HEP | default | - | 0/0/280 | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Reduced | Sensitivity | default | - | 0/0/0 | - | - | - | missing | ⚪ >= Truncated default: n/a |
| Pessimistic | DayNight | default | - | 140/0/340 | - | - | - | missing | - |
| Pessimistic | HEP | default | - | 0/0/400 | - | - | - | missing | - |
| Pessimistic | Sensitivity | default | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | unc_sig20 | 4/20/5 | 0/0/400 | 2.66σ@30y | 2.32σ@20y | 10-20 13:55 | ok | 🟢 >= default: 2.66 vs 2.44 OK |
| Truncated | HEP | unc_sig40 | 4/20/5 | 0/0/400 | 2.21σ@30y | 1.92σ@20y | 10-20 13:57 | ok | 🟢 <= default: 2.21 vs 2.44 OK |
| Truncated | Sensitivity | unc_sig0 | 5/16/20 | 0/0/460 | Δχ² 1.93/1.93@30y | Δχ² 0.66/0.66@10y | 10-20 14:33 | ok | 🟢 >= unc_sig2: 1.93 vs 1.08 OK |
| Truncated | Sensitivity | unc_sig2 | 5/16/20 | 0/0/460 | Δχ² 1.08/1.06@30y | Δχ² 0.51/0.50@10y | 10-20 14:35 | ok | 🟢 >= default: 1.08 vs 0.63 OK |
| Truncated | Sensitivity | unc_sig6 | 5/16/20 | 0/0/460 | Δχ² 0.46/0.45@30y | Δχ² 0.23/0.23@10y | 10-20 15:03 | ok | 🟢 <= default: 0.46 vs 0.63 OK |
| Truncated | DayNight | unc_bkg0 | 5/17/11 | - | 2.38σ@30y | 1.95σ@20y | 10-15 08:00 | ok | **🔴 == default: 2.38 vs 1.48 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg0 | 6/4/20 | - | 1.98σ@30y | 1.73σ@20y | 10-15 08:04 | ok | **🔴 == default: 1.98 vs 2.44 UNEXPECTED (fresh)** |
| Truncated | DayNight | unc_bkg4 | 5/17/11 | - | 2.38σ@30y | 1.95σ@20y | 10-15 08:27 | ok | **🔴 == default: 2.38 vs 1.48 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg4 | 6/4/20 | - | 1.98σ@30y | 1.73σ@20y | 10-15 08:30 | ok | **🔴 == default: 1.98 vs 2.44 UNEXPECTED (fresh)** |
| Truncated | DayNight | unc_bkg6 | 5/17/11 | - | 2.38σ@30y | 1.95σ@20y | 10-15 08:53 | ok | **🔴 == default: 2.38 vs 1.48 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg6 | 6/4/20 | - | 1.98σ@30y | 1.73σ@20y | 10-15 08:56 | ok | **🔴 == default: 1.98 vs 2.44 UNEXPECTED (fresh)** |
| Truncated | Sensitivity | nuisance_nominal | 5/16/20 | 0/0/460 | Δχ² 0.69/0.66@30y | Δχ² 0.36/0.35@10y | 10-20 19:24 | ok | 🟢 >= nuisance_sin13: 0.69 vs 0.69 OK |
| Truncated | Sensitivity | nuisance_sin13 | 5/16/20 | 0/0/460 | Δχ² 0.69/0.66@30y | Δχ² 0.36/0.35@10y | 10-20 19:56 | ok | 🟢 >= default: 0.69 vs 0.63 OK |
| Truncated | Sensitivity | nuisance_escale | 5/16/20 | 0/0/460 | Δχ² 0.62/0.59@30y | Δχ² 0.33/0.32@10y | 10-20 19:26 | ok | 🟢 >= default: 0.62 vs 0.63 OK |
| Truncated | DayNight | energy_spk | 5/16/20 | 0/0/460 | 3.37σ@30y | 2.75σ@20y | 10-20 15:36 | ok | ⚪ vs default: 3.37 vs 1.48 |
| Truncated | HEP | energy_spk | 6/7/16 | 0/0/400 | 32.55σ@30y | 28.34σ@20y | 10-20 15:40 | ok | ⚪ vs default: 32.55 vs 2.44 |
| Truncated | Sensitivity | energy_spk | 5/9/20 | 0/0/460 | Δχ² 2.99/2.91@30y | Δχ² 1.15/1.12@10y | 10-20 16:45 | ok | ⚪ vs default: 2.99 vs 0.63 |
| Truncated | DayNight | energy_maink | 5/16/20 | 0/0/460 | 1.37σ@30y | 1.12σ@20y | 10-20 10:16 | ok | ⚪ vs default: 1.37 vs 1.48 |
| Truncated | HEP | energy_maink | 1/4/19 | 0/0/400 | 11.60σ@30y | 10.07σ@20y | 10-20 10:19 | ok | ⚪ vs default: 11.60 vs 2.44 |
| Truncated | Sensitivity | energy_maink | 5/9/20 | 0/0/460 | Δχ² 0.84/0.81@30y | Δχ² 0.45/0.44@10y | 10-20 11:54 | ok | ⚪ vs default: 0.84 vs 0.63 |
| Truncated | DayNight | charge_Q0 | 5/16/11 | - | 2.31σ@30y | 1.89σ@20y | 10-15 12:11 | ok | ⚪ vs default: 2.31 vs 1.48 |
| Truncated | HEP | charge_Q0 | 6/4/20 | - | 1.56σ@30y | 1.36σ@20y | 10-15 12:14 | ok | ⚪ vs default: 1.56 vs 2.44 |
| Truncated | Sensitivity | charge_Q0 | 5/17/11 | - | Δχ² 0.89/0.86@30y | Δχ² 0.46/0.45@10y | 10-15 12:26 | cut!=ref(5, 16, 20) | ⚪ vs default: 0.89 vs 0.63 |
| Truncated | DayNight | charge_Q50 | 5/15/11 | - | 2.13σ@30y | 1.74σ@20y | 10-15 13:05 | ok | ⚪ vs charge_Q0: 2.13 vs 2.31 |
| Truncated | HEP | charge_Q50 | 6/4/20 | - | 1.64σ@30y | 1.43σ@20y | 10-15 13:08 | ok | ⚪ vs charge_Q0: 1.64 vs 1.56 |
| Truncated | Sensitivity | charge_Q50 | 5/17/11 | - | Δχ² 0.81/0.78@30y | Δχ² 0.45/0.43@10y | 10-15 13:20 | cut!=ref(5, 16, 20) | ⚪ vs charge_Q0: 0.81 vs 0.89 |
| Truncated | DayNight | charge_Q100 | 5/17/12 | - | 2.26σ@30y | 1.85σ@20y | 10-15 13:57 | ok | ⚪ vs charge_Q50: 2.26 vs 2.13 |
| Truncated | HEP | charge_Q100 | 6/4/20 | - | 1.47σ@30y | 1.28σ@20y | 10-15 14:00 | ok | ⚪ vs charge_Q50: 1.47 vs 1.64 |
| Truncated | Sensitivity | charge_Q100 | 5/17/11 | - | Δχ² 0.80/0.77@30y | Δχ² 0.44/0.43@10y | 10-15 14:12 | cut!=ref(5, 16, 20) | ⚪ vs charge_Q50: 0.80 vs 0.81 |
| Truncated | DayNight | charge_Q500 | 3/4/13 | - | 0.69σ@30y | 0.56σ@20y | 10-15 14:50 | ok | ⚪ vs charge_Q100: 0.69 vs 2.26 |
| Truncated | HEP | charge_Q500 | 4/9/17 | - | 0.83σ@30y | 0.72σ@20y | 10-15 14:53 | ok | ⚪ vs charge_Q100: 0.83 vs 1.47 |
| Truncated | Sensitivity | charge_Q500 | 5/17/11 | - | Δχ² 0.88/0.85@30y | Δχ² 0.41/0.40@10y | 10-15 15:07 | cut!=ref(5, 16, 20) | ⚪ vs charge_Q100: 0.88 vs 0.80 |
| Nominal | DayNight | bkgmodel_nominal | 5/16/20 | 0/60/20 | 0.39σ@30y | 0.32σ@20y | 10-20 17:43 | ok | 🟢 <= Truncated default: 0.39 vs 1.48 OK |
| Nominal | HEP | bkgmodel_nominal | 4/20/5 | 0/60/460 | 2.43σ@30y | 2.11σ@20y | 10-20 17:46 | ok | 🟢 <= Truncated default: 2.43 vs 2.44 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 5/16/20 | 0/160/220 | Δχ² 0.17/0.17@30y | Δχ² 0.07/0.07@10y | 10-20 18:00 | ok | 🟢 <= Truncated default: 0.17 vs 0.63 OK |
| Reduced | DayNight | bkgmodel_reduced | 5/16/20 | 0/0/100 | 3.41σ@30y | 2.79σ@20y | 10-20 13:03 | ok | 🟢 >= Truncated default: 3.41 vs 1.48 OK |
| Reduced | HEP | bkgmodel_reduced | 4/20/5 | 0/0/280 | 2.48σ@30y | 2.16σ@20y | 10-20 13:06 | ok | 🟢 >= Truncated default: 2.48 vs 2.44 OK |
| Reduced | Sensitivity | bkgmodel_reduced | 5/16/20 | 0/0/0 | Δχ² 2.21/2.16@30y | Δχ² 0.94/0.91@10y | 10-20 13:19 | ok | 🟢 >= Truncated default: 2.21 vs 0.63 OK |
| Pessimistic | DayNight | bkgmodel_pessimistic | 5/16/20 | 140/0/340 | 0.43σ@30y | 0.35σ@20y | 10-21 06:21 | ok | 🟢 <= Truncated default: 0.43 vs 1.48 OK |
| Pessimistic | HEP | bkgmodel_pessimistic | 2/4/3 | 0/0/400 | 2.44σ@30y | 2.12σ@20y | 10-21 06:25 | ok | 🟢 <= Truncated default: 2.44 vs 2.44 OK |
| Pessimistic | Sensitivity | bkgmodel_pessimistic | 5/16/20 | 140/0/340 | Δχ² 0.15/0.15@30y | Δχ² 0.06/0.06@10y | 10-21 07:43 | ok | 🟢 <= Truncated default: 0.15 vs 0.63 OK |
| Truncated | DayNight | sb_simple | - | - | - | - | - | missing | - |
| Truncated | HEP | sb_simple | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_simple | - | - | - | - | - | missing | - |
| Truncated | DayNight | sb_gateonly | - | - | - | - | - | missing | - |
| Truncated | HEP | sb_gateonly | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_gateonly | - | - | - | - | - | missing | - |
| Truncated | DayNight | ncveto_618 | - | - | - | - | - | missing | - |
| Truncated | HEP | ncveto_618 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | ncveto_618 | - | - | - | - | - | missing | - |
| Truncated | DayNight | sb_lowthr | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | sb_lowthr | - | 0/0/400 | - | - | - | missing | - |
| Truncated | Sensitivity | sb_lowthr | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | sb_simple_hepwin | - | - | - | - | - | missing | - |
| Truncated | DayNight | sb_off | 5/17/16 | 0/0/380 | 1.19σ@30y | 0.97σ@20y | 10-19 04:56 | ok | ⚪ vs default: 1.19 vs 1.48 |
| Truncated | HEP | sb_off | 5/4/20 | 0/0/400 | 1.99σ@30y | 1.73σ@20y | 10-19 04:59 | ok | ⚪ vs default: 1.99 vs 2.44 |
| Truncated | Sensitivity | sb_off | 5/15/14 | 0/0/460 | Δχ² 0.38/0.36@30y | Δχ² 0.19/0.19@10y | 10-19 06:11 | ok | ⚪ vs default: 0.38 vs 0.63 |
| Truncated | DayNight | sb_off_veto | 5/16/10 | 40/0/460 | 2.43σ@30y | 1.99σ@20y | 10-17 20:56 | ok | ⚪ vs default: 2.43 vs 1.48 |
| Truncated | HEP | sb_off_veto | 2/4/15 | 0/0/0 | 1.86σ@30y | 1.64σ@20y | 10-17 21:00 | ok | ⚪ vs default: 1.86 vs 2.44 |
| Truncated | Sensitivity | sb_off_veto | 5/17/11 | 0/120/0 | Δχ² 1.02/0.99@30y | Δχ² 0.49/0.47@10y | 10-17 22:28 | ok | ⚪ vs default: 1.02 vs 0.63 |
| Truncated | DayNight | sb_remove | 5/16/20 | 0/0/460 | 1.23σ@30y | 1.00σ@20y | 10-19 19:23 | ok | - |
| Truncated | HEP | sb_remove | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-19 19:27 | ok | - |
| Truncated | Sensitivity | sb_remove | 5/16/20 | 0/0/460 | Δχ² 0.60/0.57@30y | Δχ² 0.32/0.31@10y | 10-19 20:35 | ok | - |
| Truncated | Sensitivity | sb_remove_radsmooth | - | - | - | - | - | missing | - |
| Truncated | DayNight | sb_remove_fixfid | 5/16/20 | 0/0/460 | 1.23σ@30y | 1.00σ@20y | 10-20 00:47 | ok | - |
| Truncated | HEP | sb_remove_fixfid | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-20 00:50 | ok | - |
| Truncated | Sensitivity | sb_remove_fixfid | 5/16/20 | 0/0/460 | Δχ² 0.60/0.57@30y | Δχ² 0.32/0.31@10y | 10-20 01:58 | ok | - |
| Truncated | DayNight | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | HEP | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_noradfid | - | 140/0/340 | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_fixfid | 5/16/20 | 0/0/460 | Δχ² 0.60/0.57@30y | Δχ² 0.32/0.31@10y | 10-20 01:25 | ok | - |
| Truncated | DayNight | fid_rescan | 5/16/20 | 0/0/460 | 1.32σ@30y | 1.08σ@20y | 10-20 20:37 | ok | - |
| Truncated | HEP | fid_rescan | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-20 20:40 | ok | - |
| Truncated | Sensitivity | fid_rescan | - | 0/0/460 | - | - | - | missing | - |
| Truncated | Sensitivity | rad_smooth | 1/11/14 | 0/0/460 | Δχ² 0.41/0.39@30y | Δχ² 0.21/0.20@10y | 10-19 14:54 | ok | ⚪ vs default: 0.41 vs 0.63 |
| Truncated | Sensitivity | rad_smooth_end | 1/4/14 | 0/0/460 | Δχ² 0.55/0.53@30y | Δχ² 0.30/0.30@10y | 10-19 23:58 | ok | - |
| Truncated | Sensitivity | rad_floor3 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth_end | - | 140/0/340 | - | - | - | missing | - |
| Truncated | DayNight | rad_unified_smooth | 5/16/20 | 140/0/340 | 1.48σ@30y | 1.21σ@20y | 10-20 20:16 | ok | - |
| Truncated | HEP | rad_unified_smooth | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-20 20:19 | ok | - |
| Truncated | Sensitivity | rad_unified_smooth | 5/16/20 | 140/0/340 | Δχ² 0.63/0.61@30y | Δχ² 0.33/0.32@10y | 10-20 21:45 | ok | - |
| Truncated | DayNight | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | HEP | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | DayNight | rad_unified | 5/16/20 | 140/0/340 | 1.49σ@30y | 1.21σ@20y | 10-20 17:38 | ok | - |
| Truncated | HEP | rad_unified | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-20 17:41 | ok | - |
| Truncated | Sensitivity | rad_unified | 5/16/20 | 140/0/340 | Δχ² 0.63/0.61@30y | Δχ² 0.34/0.33@10y | 10-20 19:09 | ok | - |
| Truncated | DayNight | rad_off | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | rad_off | - | 0/0/400 | - | - | - | missing | - |
| Truncated | Sensitivity | rad_off | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | hep_notail | 5/16/5 | 0/0/0* | 3.44σ@30y | 3.00σ@20y | 10-16 12:07 | ok | ⚪ vs default: 3.44 vs 2.44 |
| Truncated | DayNight | fid_oneband | 5/16/11 | 40/0/480 | 1.84σ@30y | 1.50σ@20y | 10-16 23:36 | ok | - |
| Truncated | HEP | fid_oneband | 6/4/20 | 0/0/0* | 2.01σ@30y | 1.75σ@20y | 10-16 23:39 | ok | - |
| Truncated | Sensitivity | fid_oneband | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-17 01:12 | ok | - |
| Truncated | DayNight | fid_zlim | 5/17/10 | 20/0/300 | 2.59σ@30y | 2.11σ@20y | 10-17 02:17 | ok | - |
| Truncated | HEP | fid_zlim | 6/4/20 | 0/0/0* | 1.98σ@30y | 1.73σ@20y | 10-17 02:20 | ok | - |
| Truncated | Sensitivity | fid_zlim | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-17 03:32 | ok | - |
| Truncated | DayNight | fid_exp30 | 5/17/11 | 40/0/480 | 2.38σ@30y | 1.94σ@20y | 10-17 16:20 | ok | - |
| Truncated | HEP | fid_exp30 | 6/4/20 | 0/0/0 | 1.98σ@30y | 1.73σ@20y | 10-17 16:24 | ok | - |
| Truncated | Sensitivity | fid_exp30 | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-17 17:36 | ok | - |
| Truncated | HEP | fid_hepbands22 | - | 0/0/400 | - | - | - | missing | - |
| Truncated | DayNight | fid_bandmin1 | 5/16/11 | 40/0/480 | 1.84σ@30y | 1.50σ@20y | 10-17 19:00 | ok | - |
| Truncated | HEP | fid_bandmin1 | 6/4/20 | 0/0/0 | 2.01σ@30y | 1.75σ@20y | 10-17 19:03 | ok | - |
| Truncated | Sensitivity | fid_bandmin1 | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-17 20:22 | ok | - |
| Truncated | DayNight | fid_bandrel5 | 5/17/11 | 40/0/480 | 2.38σ@30y | 1.95σ@20y | 10-17 15:52 | ok | - |
| Truncated | HEP | fid_bandrel5 | 6/4/20 | 0/0/0 | 2.01σ@30y | 1.75σ@20y | 10-17 15:55 | ok | - |
| Truncated | Sensitivity | fid_bandrel5 | 5/17/11 | 0/120/0 | Δχ² 1.13/1.09@30y | Δχ² 0.53/0.52@10y | 10-17 17:03 | ok | - |
| Truncated | DayNight | fid_highband | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_highband | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_highband | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bestband | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | fid_radfloor | - | 0/0/400 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_radfloor | - | 140/0/340 | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor_one | 5/17/11 | 40/0/460 | 2.20σ@30y | 1.79σ@20y | 10-17 22:49 | ok | - |
| Truncated | HEP | fid_radfloor_one | 6/4/20 | 0/0/0 | 2.01σ@30y | 1.75σ@20y | 10-17 22:53 | ok | - |
| Truncated | Sensitivity | fid_radfloor_one | 5/13/11 | 0/280/300 | Δχ² 1.29/1.25@30y | Δχ² 0.62/0.60@10y | 10-18 00:07 | ok | - |
| Truncated | DayNight | fid_oldrule | 5/17/11 | 40/0/480 | 2.12σ@30y | 1.73σ@20y | 10-18 06:56 | ok | - |
| Truncated | HEP | fid_oldrule | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_oldrule | - | 140/0/460 | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_noveto | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_noveto | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_noveto | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_dn616 | 5/16/11 | 40/0/480 | 1.84σ@30y | 1.50σ@20y | 10-17 21:15 | ok | - |
| Truncated | DayNight | fid_bandmax | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_bandmax | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bandmax | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_lowband | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | fid_lowband | - | 0/0/400 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_lowband | - | 140/0/340 | - | - | - | missing | - |
| Truncated | DayNight | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_60_480 | - | 140/0/340 | - | - | - | missing | - |
| Truncated | HEP | fid_v100_60_480 | - | 0/0/400 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_60_480 | - | 140/0/340 | - | - | - | missing | - |
| Truncated | DayNight | fid_fullspec | 5/16/11 | 40/0/480 | 1.84σ@30y | 1.50σ@20y | 10-17 00:49 | ok | - |
| Truncated | HEP | fid_fullspec | 2/7/17 | 80/0/0 | 2.18σ@30y | 1.64σ@20y | 10-17 00:53 | ok | - |
| Truncated | Sensitivity | fid_fullspec | 5/17/11 | 0/120/20 | Δχ² 1.14/1.10@30y | Δχ² 0.53/0.52@10y | 10-17 02:10 | ok | - |
| Truncated | DayNight | fid_nosb | 5/17/11 | 40/0/460 | 2.42σ@30y | 1.98σ@20y | 10-17 04:06 | ok | - |
| Truncated | HEP | fid_nosb | 6/4/20 | 0/0/0* | 1.98σ@30y | 1.73σ@20y | 10-17 04:09 | ok | - |
| Truncated | Sensitivity | fid_nosb | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-17 05:27 | ok | - |
| Truncated | HEP | hep_plain_opt | 2/4/19 | 0/0/0* | 1.91σ@30y | 1.71σ@20y | 10-17 02:57 | ok | - |
| Truncated | DayNight | mcfloor_10 | 5/17/11 | 40/0/480 | 2.38σ@30y | 1.95σ@20y | 10-16 22:24 | ok | ⚪ vs default: 2.38 vs 1.48 |
| Truncated | HEP | mcfloor_10 | 6/4/20 | 0/0/0* | 1.98σ@30y | 1.73σ@20y | 10-16 22:27 | ok | ⚪ vs default: 1.98 vs 2.44 |
| Truncated | Sensitivity | mcfloor_10 | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-16 23:39 | ok | ⚪ vs default: 1.14 vs 0.63 |
| Truncated | DayNight | mcfloor_25 | 5/17/11 | 40/0/480 | 2.38σ@30y | 1.95σ@20y | 10-17 07:55 | ok | ⚪ vs default: 2.38 vs 1.48 |
| Truncated | HEP | mcfloor_25 | 6/4/20 | 0/0/0* | 1.98σ@30y | 1.73σ@20y | 10-17 07:57 | ok | ⚪ vs default: 1.98 vs 2.44 |
| Truncated | Sensitivity | mcfloor_25 | 5/17/11 | 0/120/0 | Δχ² 1.14/1.11@30y | Δχ² 0.53/0.52@10y | 10-17 09:07 | ok | ⚪ vs default: 1.14 vs 0.63 |
| Truncated | DayNight | mcfloor_50 | 5/17/11 | 40/0/480 | 2.38σ@30y | 1.95σ@20y | 10-17 08:08 | ok | ⚪ vs default: 2.38 vs 1.48 |
| Truncated | HEP | mcfloor_50 | 2/4/20 | 0/0/0* | 1.95σ@30y | 1.73σ@20y | 10-17 08:11 | ok | ⚪ vs default: 1.95 vs 2.44 |
| Truncated | Sensitivity | mcfloor_50 | 5/14/11 | 0/120/0 | Δχ² 1.11/1.07@30y | Δχ² 0.53/0.51@10y | 10-17 09:21 | ok | ⚪ vs default: 1.11 vs 0.63 |
| Truncated | DayNight | bkgsub_s1 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | bkgsub_s1 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | Sensitivity | bkgsub_s1 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | DayNight | bkgsub_s2 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | bkgsub_s2 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | Sensitivity | bkgsub_s2 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | DayNight | bkgsub_s3 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | bkgsub_s3 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | Sensitivity | bkgsub_s3 | - | - | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_extmask | 5/13/5 | 0/0/0* | 2.84σ@30y | 2.47σ@20y | 10-17 06:14 | ok | ⚪ vs default: 2.84 vs 2.44 |
| Truncated | HEP | hep_looseshape | 6/4/20 | 0/0/0* | 4.17σ@30y | 3.63σ@20y | 10-17 06:44 | ok | ⚪ vs default: 4.17 vs 2.44 |
| Truncated | HEP | hep_looseshape_plain | 6/4/20 | 0/0/0* | 3.50σ@30y | 3.05σ@20y | 10-17 07:00 | ok | ⚪ vs default: 3.50 vs 2.44 |
| Truncated | HEP | hep_looseshape_nh | - | 0/0/400 | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_looseshape_win | 2/4/18 | 0/0/0 | 2.61σ@30y | 2.30σ@20y | 10-17 18:36 | ok | ⚪ vs default: 2.61 vs 2.44 |
| Truncated | HEP | sb_hep90 | - | 0/0/400 | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_sbmodel | 5/15/13 | 0/0/400 | 3.81σ@30y | 3.31σ@20y | 10-09 20:36 | ok | ⚪ vs default: 3.81 vs 2.44 |
| Truncated | HEP | hep_plain | 5/15/13 | 0/0/400 | 2.64σ@30y | 2.29σ@20y | 10-09 20:48 | ok | ⚪ vs default: 2.64 vs 2.44 |
| Truncated | DayNight | ncveto | 5/15/20 | 140/0/340 | 1.32σ@30y | 1.08σ@20y | 10-09 14:08 | ok | ⚪ vs default: 1.32 vs 1.48 |
| Truncated | Sensitivity | ncveto | 5/13/19 | 140/0/340 | Δχ² 0.44/0.42@30y | Δχ² 0.21/0.20@10y | 10-09 14:44 | ok | ⚪ vs default: 0.44 vs 0.63 |
| Truncated | DayNight | ncveto_off | 5/17/11 | 40/0/480 | 2.26σ@30y | 1.85σ@20y | 10-17 09:47 | ok | ⚪ vs default: 2.26 vs 1.48 |
| Truncated | Sensitivity | ncveto_off | 5/17/11 | 0/120/0 | Δχ² 1.09/1.05@30y | Δχ² 0.51/0.49@10y | 10-17 10:55 | ok | ⚪ vs default: 1.09 vs 0.63 |
| Truncated | DayNight | mcgate_50 | 5/13/20 | 140/0/340 | 1.47σ@30y | 1.20σ@20y | 10-10 00:32 | ok | ⚪ vs default: 1.47 vs 1.48 |
| Truncated | HEP | mcgate_50 | 5/15/13 | 0/0/400 | 3.99σ@30y | 3.47σ@20y | 10-10 00:35 | ok | ⚪ vs default: 3.99 vs 2.44 |
| Truncated | Sensitivity | mcgate_50 | 5/13/19 | 140/0/340 | Δχ² 0.43/0.42@30y | Δχ² 0.20/0.20@10y | 10-10 01:12 | ok | ⚪ vs default: 0.43 vs 0.63 |
| Truncated | DayNight | mcgate_20 | 5/17/11 | 40/0/480 | 2.35σ@30y | 1.92σ@20y | 10-17 04:41 | ok | ⚪ vs default: 2.35 vs 1.48 |
| Truncated | HEP | mcgate_20 | 2/4/8 | 0/0/0 | 2.04σ@30y | 1.49σ@20y | 10-17 04:44 | ok | ⚪ vs default: 2.04 vs 2.44 |
| Truncated | Sensitivity | mcgate_20 | 5/17/11 | 0/120/0 | Δχ² 1.08/1.04@30y | Δχ² 0.51/0.49@10y | 10-17 05:59 | ok | ⚪ vs default: 1.08 vs 0.63 |
| Truncated | DayNight | mcgate_0 | 5/18/20 | 140/0/340 | 1.31σ@30y | 1.07σ@20y | 10-10 03:11 | ok | ⚪ vs default: 1.31 vs 1.48 |
| Truncated | HEP | mcgate_0 | 5/18/20 | 0/0/400 | 3.55σ@30y | 3.08σ@20y | 10-10 03:16 | ok | ⚪ vs default: 3.55 vs 2.44 |
| Truncated | Sensitivity | mcgate_0 | 5/18/18 | 140/0/340 | Δχ² 0.35/0.34@30y | Δχ² 0.16/0.16@10y | 10-10 03:50 | ok | ⚪ vs default: 0.35 vs 0.63 |
| Truncated | HEP | hep_mcf3 | 5/15/13 | 0/0/400 | 3.99σ@30y | 3.47σ@20y | 10-10 13:04 | ok | ⚪ vs default: 3.99 vs 2.44 |
| Truncated | HEP | hep_mcf5 | 5/19/20 | 0/0/400 | 6.35σ@30y | 5.54σ@20y | 10-10 13:16 | ok | ⚪ vs default: 6.35 vs 2.44 |
| Truncated | DayNight | oscpoint_solar | 5/16/20 | 0/0/460 | 1.32σ@30y | 1.08σ@20y | 10-20 19:20 | ok | **🔴 == default: 1.32 vs 1.48 UNEXPECTED (fresh)** |
| Truncated | HEP | oscpoint_solar | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-20 19:24 | ok | 🟢 == default: 2.44 vs 2.44 OK |
| Truncated | DayNight | oscpoint_reactor | 5/16/20 | 0/0/460 | 1.00σ@30y | 0.82σ@20y | 10-20 12:23 | ok | 🟢 <= default: 1.00 vs 1.48 OK |
| Truncated | HEP | oscpoint_reactor | 4/20/5 | 0/0/400 | 2.44σ@30y | 2.13σ@20y | 10-20 12:27 | ok | 🟢 == default: 2.44 vs 2.44 OK |
| Truncated | DayNight | fiduc_truth | 2/7/20 | 120/120/0* | 6.77σ@30y | 5.53σ@20y | 10-20 10:14 | ok | 🟢 >= default: 6.77 vs 1.48 OK |
| Truncated | HEP | fiduc_truth | 2/4/20 | 120/80/0*† | 7.00σ@30y | 6.10σ@20y | 10-20 10:17 | ok | 🟢 >= default: 7.00 vs 2.44 OK |
| Truncated | Sensitivity | fiduc_truth | 2/7/20 | 120/100/0*† | Δχ² 6.75/6.53@30y | Δχ² 2.50/2.42@10y | 10-20 11:54 | ok | 🟢 >= default: 6.75 vs 0.63 OK |
| Truncated | DayNight | fiduc_truth_refvol | - | 140/0/340 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | HEP | fiduc_truth_refvol | - | 0/0/400 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | Sensitivity | fiduc_truth_refvol | - | 140/0/340 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | DayNight | bkg_gamma_cluster | 5/16/20 | 0/0/460 | 1.42σ@30y | 1.16σ@20y | 10-20 17:52 | ok | ⚪ vs default: 1.42 vs 1.48 |
| Truncated | HEP | bkg_gamma_cluster | 4/20/5 | 160/0/400 | 2.27σ@30y | 1.98σ@20y | 10-20 17:56 | ok | ⚪ vs default: 2.27 vs 2.44 |
| Truncated | Sensitivity | bkg_gamma_cluster | 5/16/20 | 0/0/460 | Δχ² 0.68/0.65@30y | Δχ² 0.36/0.35@10y | 10-20 18:12 | ok | ⚪ vs default: 0.68 vs 0.63 |
| Truncated | DayNight | bkg_gamma_total | 5/16/20 | 40/60/220 | 1.47σ@30y | 1.20σ@20y | 10-20 17:56 | ok | ⚪ vs default: 1.47 vs 1.48 |
| Truncated | HEP | bkg_gamma_total | 4/20/5 | 80/0/0 | 1.55σ@30y | 1.35σ@20y | 10-20 18:00 | ok | ⚪ vs default: 1.55 vs 2.44 |
| Truncated | Sensitivity | bkg_gamma_total | 5/16/20 | 60/120/180 | Δχ² 0.60/0.58@30y | Δχ² 0.31/0.31@10y | 10-20 18:17 | ok | ⚪ vs default: 0.60 vs 0.63 |
| Truncated | DayNight | membrane_veto_off | 5/16/20 | 0/0/460 | 1.21σ@30y | 0.99σ@20y | 10-20 13:05 | ok | **🔴 >= default: 1.21 vs 1.48 UNEXPECTED (fresh)** |
| Truncated | HEP | membrane_veto_off | 4/20/5 | 0/0/400 | 2.45σ@30y | 2.14σ@20y | 10-20 13:09 | ok | 🟢 >= default: 2.45 vs 2.44 OK |
| Truncated | Sensitivity | membrane_veto_off | 5/16/20 | 0/0/460 | Δχ² 0.45/0.44@30y | Δχ² 0.24/0.23@10y | 10-20 13:23 | ok | ⚪ vs default: 0.45 vs 0.63 |
| Truncated | Sensitivity | legacy_fit | - | 140/0/340 | - | - | - | missing | ⚪ vs default: n/a |

## vd_1x8x14_3view_30deg_shielded

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 5/10/20 | 0/0/0 | 5.06σ@30y | 4.13σ@20y | 10-21 06:16 | ok | - |
| Truncated | HEP | default | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-21 06:20 | ok | - |
| Truncated | Sensitivity | default | 4/4/15 | 20/0/0 | Δχ² 5.08/4.90@30y | Δχ² 1.91/1.84@10y | 10-21 07:22 | ok | - |
| Nominal | DayNight | default | - | 40/0/0 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | HEP | default | - | 0/0/60 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Nominal | Sensitivity | default | - | 0/0/520 | - | - | - | missing | ⚪ <= Truncated default: n/a |
| Pessimistic | DayNight | default | - | 0/0/0 | - | - | - | missing | - |
| Pessimistic | HEP | default | - | 0/260/520 | - | - | - | missing | - |
| Pessimistic | Sensitivity | default | - | 20/0/0 | - | - | - | missing | - |
| Truncated | HEP | unc_sig20 | 3/19/2 | 0/0/0 | 3.60σ@30y | 3.14σ@20y | 10-20 14:08 | ok | 🟢 >= default: 3.60 vs 3.34 OK |
| Truncated | HEP | unc_sig40 | 3/19/2 | 0/0/0 | 3.06σ@30y | 2.66σ@20y | 10-20 14:10 | ok | 🟢 <= default: 3.06 vs 3.34 OK |
| Truncated | Sensitivity | unc_sig0 | 4/4/15 | 20/0/160 | Δχ² 26.86/26.81@30y | Δχ² 9.22/9.20@10y | 10-20 15:20 | ok | 🟢 >= unc_sig2: 26.86 vs 5.46 OK |
| Truncated | Sensitivity | unc_sig2 | 4/4/15 | 20/0/160 | Δχ² 5.46/5.27@30y | Δχ² 2.52/2.44@10y | 10-20 15:21 | ok | 🟢 >= default: 5.46 vs 5.08 OK |
| Truncated | Sensitivity | unc_sig6 | 4/4/15 | 20/0/160 | Δχ² 4.37/4.22@30y | Δχ² 1.55/1.50@10y | 10-20 15:28 | ok | 🟢 <= default: 4.37 vs 5.08 OK |
| Truncated | DayNight | unc_bkg0 | 5/11/18 | - | 4.75σ@30y | 3.88σ@20y | 10-15 06:17 | ok | **🔴 == default: 4.75 vs 5.06 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg0 | 6/8/18 | - | 2.25σ@30y | 1.96σ@20y | 10-15 06:21 | ok | **🔴 == default: 2.25 vs 3.34 UNEXPECTED (fresh)** |
| Truncated | DayNight | unc_bkg4 | 5/11/18 | - | 4.75σ@30y | 3.88σ@20y | 10-15 06:36 | ok | **🔴 == default: 4.75 vs 5.06 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg4 | 6/8/18 | - | 2.25σ@30y | 1.96σ@20y | 10-15 06:39 | ok | **🔴 == default: 2.25 vs 3.34 UNEXPECTED (fresh)** |
| Truncated | DayNight | unc_bkg6 | 5/11/18 | - | 4.75σ@30y | 3.88σ@20y | 10-15 06:54 | ok | **🔴 == default: 4.75 vs 5.06 UNEXPECTED (fresh)** |
| Truncated | HEP | unc_bkg6 | 6/8/18 | - | 2.25σ@30y | 1.96σ@20y | 10-15 06:57 | ok | **🔴 == default: 2.25 vs 3.34 UNEXPECTED (fresh)** |
| Truncated | Sensitivity | nuisance_nominal | 4/4/15 | 20/0/160 | Δχ² 4.92/4.74@30y | Δχ² 1.85/1.78@10y | 10-20 19:27 | ok | 🟢 >= nuisance_sin13: 4.92 vs 4.92 OK |
| Truncated | Sensitivity | nuisance_sin13 | 4/4/15 | 20/0/160 | Δχ² 4.92/4.74@30y | Δχ² 1.85/1.78@10y | 10-20 19:55 | ok | **🔴 >= default: 4.92 vs 5.08 UNEXPECTED (fresh)** |
| Truncated | Sensitivity | nuisance_escale | 4/4/15 | 20/0/160 | Δχ² 4.55/4.39@30y | Δχ² 1.72/1.66@10y | 10-20 19:29 | ok | **🔴 >= default: 4.55 vs 5.08 UNEXPECTED (fresh)** |
| Truncated | DayNight | energy_spk | 5/20/20 | 20/0/160 | 3.68σ@30y | 3.00σ@20y | 10-20 16:14 | ok | ⚪ vs default: 3.68 vs 5.06 |
| Truncated | HEP | energy_spk | 6/4/6 | 0/0/0 | 32.80σ@30y | 28.59σ@20y | 10-20 16:18 | ok | ⚪ vs default: 32.80 vs 3.34 |
| Truncated | Sensitivity | energy_spk | 4/7/18 | 20/0/160 | Δχ² 4.61/4.44@30y | Δχ² 1.81/1.74@10y | 10-20 17:09 | ok | ⚪ vs default: 4.61 vs 5.08 |
| Truncated | DayNight | energy_maink | 5/10/20 | 20/0/160 | 4.41σ@30y | 3.60σ@20y | 10-20 12:51 | ok | ⚪ vs default: 4.41 vs 5.06 |
| Truncated | HEP | energy_maink | 1/4/19 | 0/0/0 | 16.45σ@30y | 14.28σ@20y | 10-20 12:54 | ok | ⚪ vs default: 16.45 vs 3.34 |
| Truncated | Sensitivity | energy_maink | 4/4/14 | 20/0/160 | Δχ² 5.18/4.97@30y | Δχ² 1.96/1.88@10y | 10-20 13:48 | ok | ⚪ vs default: 5.18 vs 5.08 |
| Truncated | DayNight | charge_Q0 | 5/11/18 | - | 4.48σ@30y | 3.66σ@20y | 10-15 08:55 | ok | ⚪ vs default: 4.48 vs 5.06 |
| Truncated | HEP | charge_Q0 | 6/8/18 | - | 1.57σ@30y | 1.37σ@20y | 10-15 08:58 | ok | ⚪ vs default: 1.57 vs 3.34 |
| Truncated | Sensitivity | charge_Q0 | 4/13/18 | - | Δχ² 4.22/4.07@30y | Δχ² 1.62/1.56@10y | 10-15 09:08 | cut!=ref(4, 4, 15) | ⚪ vs default: 4.22 vs 5.08 |
| Truncated | DayNight | charge_Q50 | 5/11/18 | - | 3.36σ@30y | 2.74σ@20y | 10-15 09:37 | ok | ⚪ vs charge_Q0: 3.36 vs 4.48 |
| Truncated | HEP | charge_Q50 | 6/8/18 | - | 1.63σ@30y | 1.42σ@20y | 10-15 09:41 | ok | ⚪ vs charge_Q0: 1.63 vs 1.57 |
| Truncated | Sensitivity | charge_Q50 | 4/13/18 | - | Δχ² 6.51/6.31@30y | Δχ² 2.39/2.31@10y | 10-15 09:50 | cut!=ref(4, 4, 15) | ⚪ vs charge_Q0: 6.51 vs 4.22 |
| Truncated | DayNight | charge_Q100 | 5/11/18 | - | 3.22σ@30y | 2.63σ@20y | 10-15 10:18 | ok | ⚪ vs charge_Q50: 3.22 vs 3.36 |
| Truncated | HEP | charge_Q100 | 6/8/18 | - | 1.61σ@30y | 1.40σ@20y | 10-15 10:22 | ok | ⚪ vs charge_Q50: 1.61 vs 1.63 |
| Truncated | Sensitivity | charge_Q100 | 4/13/18 | - | Δχ² 6.58/6.38@30y | Δχ² 2.41/2.34@10y | 10-15 10:31 | cut!=ref(4, 4, 15) | ⚪ vs charge_Q50: 6.58 vs 6.51 |
| Truncated | DayNight | charge_Q500 | 4/7/15 | - | 2.18σ@30y | 1.78σ@20y | 10-15 10:57 | ok | ⚪ vs charge_Q100: 2.18 vs 3.22 |
| Truncated | HEP | charge_Q500 | 4/7/19 | - | 1.41σ@30y | 1.23σ@20y | 10-15 10:59 | ok | ⚪ vs charge_Q100: 1.41 vs 1.61 |
| Truncated | Sensitivity | charge_Q500 | 4/13/18 | - | Δχ² 7.15/6.96@30y | Δχ² 2.59/2.51@10y | 10-15 11:09 | cut!=ref(4, 4, 15) | ⚪ vs charge_Q100: 7.15 vs 6.58 |
| Nominal | DayNight | bkgmodel_nominal | 5/10/20 | 40/0/0 | 1.66σ@30y | 1.35σ@20y | 10-20 18:35 | ok | 🟢 <= Truncated default: 1.66 vs 5.06 OK |
| Nominal | HEP | bkgmodel_nominal | 3/19/2 | 0/0/60 | 3.33σ@30y | 2.90σ@20y | 10-20 18:39 | ok | 🟢 <= Truncated default: 3.33 vs 3.34 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 4/4/15 | 0/0/520 | Δχ² 0.83/0.80@30y | Δχ² 0.43/0.41@10y | 10-20 18:50 | ok | 🟢 <= Truncated default: 0.83 vs 5.08 OK |
| Pessimistic | DayNight | bkgmodel_pessimistic | 5/15/20 | 0/0/0 | 1.73σ@30y | 1.41σ@20y | 10-21 06:15 | ok | 🟢 <= Truncated default: 1.73 vs 5.06 OK |
| Pessimistic | HEP | bkgmodel_pessimistic | 1/20/2 | 0/260/520 | 2.31σ@30y | 2.01σ@20y | 10-21 06:18 | ok | 🟢 <= Truncated default: 2.31 vs 3.34 OK |
| Pessimistic | Sensitivity | bkgmodel_pessimistic | 4/4/15 | 20/0/0 | Δχ² 0.91/0.87@30y | Δχ² 0.46/0.45@10y | 10-21 07:19 | ok | 🟢 <= Truncated default: 0.91 vs 5.08 OK |
| Truncated | DayNight | sb_simple | 5/11/19 | 0/20/0 | 4.81σ@30y | 3.92σ@20y | 10-18 08:59 | ok | - |
| Truncated | HEP | sb_simple | 2/7/10 | 0/0/0 | 2.38σ@30y | 1.84σ@20y | 10-18 09:02 | ok | - |
| Truncated | Sensitivity | sb_simple | 5/13/15 | 20/20/0 | Δχ² 2.85/2.75@30y | Δχ² 1.14/1.10@10y | 10-18 09:55 | ok | - |
| Truncated | DayNight | sb_gateonly | 5/12/18 | 0/20/0 | 4.68σ@30y | 3.82σ@20y | 10-18 09:10 | ok | - |
| Truncated | HEP | sb_gateonly | 2/7/10 | 0/0/0 | 2.38σ@30y | 1.84σ@20y | 10-18 09:13 | ok | - |
| Truncated | Sensitivity | sb_gateonly | 5/10/18 | 20/20/0 | Δχ² 4.33/4.19@30y | Δχ² 1.65/1.59@10y | 10-18 10:00 | ok | - |
| Truncated | DayNight | ncveto_618 | 5/11/19 | 0/20/0 | 4.81σ@30y | 3.92σ@20y | 10-18 10:59 | ok | - |
| Truncated | HEP | ncveto_618 | 1/11/14 | 0/0/0 | 2.49σ@30y | 1.91σ@20y | 10-18 11:02 | ok | - |
| Truncated | Sensitivity | ncveto_618 | 5/6/14 | 20/20/0 | Δχ² 4.58/4.42@30y | Δχ² 1.73/1.67@10y | 10-18 12:00 | ok | - |
| Truncated | DayNight | sb_lowthr | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | sb_lowthr | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | sb_lowthr | - | 20/0/0 | - | - | - | missing | - |
| Truncated | HEP | sb_simple_hepwin | 6/4/18 | 0/0/0 | 2.51σ@30y | 2.19σ@20y | 10-18 12:51 | ok | - |
| Truncated | DayNight | sb_off | 5/14/14 | 0/0/420 | 3.73σ@30y | 3.04σ@20y | 10-19 05:03 | ok | ⚪ vs default: 3.73 vs 5.06 |
| Truncated | HEP | sb_off | 5/19/8 | 0/0/520 | 2.50σ@30y | 2.18σ@20y | 10-19 05:07 | ok | ⚪ vs default: 2.50 vs 3.34 |
| Truncated | Sensitivity | sb_off | 5/14/14 | 0/0/420 | Δχ² 2.56/2.09@30y | Δχ² 1.06/0.89@10y | 10-19 05:56 | ok | ⚪ vs default: 2.56 vs 5.08 |
| Truncated | DayNight | sb_off_veto | 5/11/19 | 0/40/0 | 4.61σ@30y | 3.77σ@20y | 10-17 21:29 | ok | ⚪ vs default: 4.61 vs 5.06 |
| Truncated | HEP | sb_off_veto | 5/20/15 | 0/120/520 | 1.79σ@30y | 1.56σ@20y | 10-17 21:33 | ok | ⚪ vs default: 1.79 vs 3.34 |
| Truncated | Sensitivity | sb_off_veto | 5/10/15 | 0/40/0 | Δχ² 3.17/3.05@30y | Δχ² 1.26/1.21@10y | 10-17 22:32 | ok | ⚪ vs default: 3.17 vs 5.08 |
| Truncated | DayNight | sb_remove | 5/11/20 | 0/20/0 | 4.86σ@30y | 3.97σ@20y | 10-19 17:03 | ok | - |
| Truncated | HEP | sb_remove | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-19 17:06 | ok | - |
| Truncated | Sensitivity | sb_remove | 5/6/15 | 0/20/0 | Δχ² 4.74/4.58@30y | Δχ² 1.78/1.72@10y | 10-19 18:10 | ok | - |
| Truncated | Sensitivity | sb_remove_radsmooth | 5/4/15 | 0/20/0 | Δχ² 4.41/4.26@30y | Δχ² 1.67/1.61@10y | 10-19 21:20 | ok | - |
| Truncated | DayNight | sb_remove_fixfid | 5/10/20 | 20/0/160 | 4.65σ@30y | 3.79σ@20y | 10-19 22:16 | ok | - |
| Truncated | HEP | sb_remove_fixfid | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-19 22:20 | ok | - |
| Truncated | Sensitivity | sb_remove_fixfid | 5/10/20 | 20/0/160 | Δχ² 4.39/4.26@30y | Δχ² 1.67/1.62@10y | 10-19 23:44 | ok | - |
| Truncated | DayNight | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | HEP | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rs_noradfid | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_noradfid | - | 20/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | sb_remove_rse_fixfid | 5/4/15 | 20/0/160 | Δχ² 4.17/4.03@30y | Δχ² 1.59/1.54@10y | 10-19 23:37 | ok | - |
| Truncated | DayNight | fid_rescan | 5/11/20 | 0/20/0 | 5.01σ@30y | 4.09σ@20y | 10-20 20:38 | ok | - |
| Truncated | HEP | fid_rescan | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-20 20:41 | ok | - |
| Truncated | Sensitivity | fid_rescan | 4/4/15 | 0/20/0 | Δχ² 5.05/4.88@30y | Δχ² 1.89/1.82@10y | 10-20 21:48 | ok | - |
| Truncated | Sensitivity | rad_smooth | 5/6/15 | 20/0/160 | Δχ² 3.95/3.81@30y | Δχ² 1.51/1.46@10y | 10-19 14:36 | ok | ⚪ vs default: 3.95 vs 5.08 |
| Truncated | Sensitivity | rad_smooth_end | 5/6/15 | 20/0/160 | Δχ² 4.09/3.95@30y | Δχ² 1.56/1.51@10y | 10-19 23:31 | ok | - |
| Truncated | Sensitivity | rad_floor3 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_floor3_smooth_end | - | 20/0/0 | - | - | - | missing | - |
| Truncated | DayNight | rad_unified_smooth | 5/10/20 | 0/0/0 | 5.06σ@30y | 4.13σ@20y | 10-20 20:19 | ok | - |
| Truncated | HEP | rad_unified_smooth | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-20 20:23 | ok | - |
| Truncated | Sensitivity | rad_unified_smooth | 4/4/15 | 20/0/0 | Δχ² 5.12/4.94@30y | Δχ² 1.92/1.85@10y | 10-20 21:26 | ok | - |
| Truncated | DayNight | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | HEP | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | rad_default_check | - | - | - | - | - | missing | - |
| Truncated | DayNight | rad_unified | 5/10/20 | 0/0/0 | 5.09σ@30y | 4.16σ@20y | 10-20 17:39 | ok | - |
| Truncated | HEP | rad_unified | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-20 17:42 | ok | - |
| Truncated | Sensitivity | rad_unified | 3/4/15 | 20/0/0 | Δχ² 5.52/5.32@30y | Δχ² 2.06/1.98@10y | 10-20 18:44 | ok | - |
| Truncated | DayNight | rad_off | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | rad_off | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | rad_off | - | 20/0/0 | - | - | - | missing | - |
| Truncated | HEP | hep_notail | 4/19/2 | 0/0/520 | 3.32σ@30y | 2.89σ@20y | 10-16 12:04 | ok | ⚪ vs default: 3.32 vs 3.34 |
| Truncated | DayNight | fid_oneband | 5/11/18 | 0/0/0 | 4.68σ@30y | 3.82σ@20y | 10-16 16:20 | ok | - |
| Truncated | HEP | fid_oneband | 1/8/19 | 0/0/520 | 2.09σ@30y | 1.49σ@20y | 10-16 16:25 | ok | - |
| Truncated | Sensitivity | fid_oneband | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-16 20:53 | ok | - |
| Truncated | DayNight | fid_zlim | 5/11/18 | 0/0/0 | 4.75σ@30y | 3.88σ@20y | 10-17 01:18 | ok | - |
| Truncated | HEP | fid_zlim | 6/8/18 | 0/0/0 | 2.29σ@30y | 2.00σ@20y | 10-17 01:22 | ok | - |
| Truncated | Sensitivity | fid_zlim | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 02:13 | ok | - |
| Truncated | DayNight | fid_exp30 | 5/10/18 | 0/0/0 | 4.20σ@30y | 3.43σ@20y | 10-17 16:43 | ok | - |
| Truncated | HEP | fid_exp30 | 1/12/13 | 0/0/0 | 2.44σ@30y | 1.90σ@20y | 10-17 16:46 | ok | - |
| Truncated | Sensitivity | fid_exp30 | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 17:40 | ok | - |
| Truncated | HEP | fid_hepbands22 | - | 0/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_bandmin1 | 5/11/18 | 0/0/0 | 4.68σ@30y | 3.82σ@20y | 10-17 18:50 | ok | - |
| Truncated | HEP | fid_bandmin1 | 1/8/19 | 0/0/520 | 2.09σ@30y | 1.49σ@20y | 10-17 18:53 | ok | - |
| Truncated | Sensitivity | fid_bandmin1 | 5/8/15 | 0/0/0 | Δχ² 4.20/4.05@30y | Δχ² 1.60/1.54@10y | 10-17 19:44 | ok | - |
| Truncated | DayNight | fid_bandrel5 | 5/11/18 | 0/0/0 | 4.68σ@30y | 3.82σ@20y | 10-17 16:02 | ok | - |
| Truncated | HEP | fid_bandrel5 | 6/8/18 | 0/0/520 | 2.25σ@30y | 1.96σ@20y | 10-17 16:06 | ok | - |
| Truncated | Sensitivity | fid_bandrel5 | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 16:56 | ok | - |
| Truncated | DayNight | fid_highband | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | fid_highband | 5/19/15 | 0/260/520 | 1.57σ@30y | 1.37σ@20y | 10-17 20:31 | ok | - |
| Truncated | Sensitivity | fid_highband | - | 0/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_bestband | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | fid_bestband | 1/11/14 | 0/0/0 | 2.49σ@30y | 1.91σ@20y | 10-17 20:07 | ok | - |
| Truncated | Sensitivity | fid_bestband | - | 0/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | fid_radfloor | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_radfloor | - | 20/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_radfloor_one | 5/10/18 | 0/0/0 | 4.41σ@30y | 3.60σ@20y | 10-17 20:46 | ok | - |
| Truncated | HEP | fid_radfloor_one | 1/11/14 | 0/0/0 | 2.49σ@30y | 1.91σ@20y | 10-17 22:20 | ok | - |
| Truncated | Sensitivity | fid_radfloor_one | 5/7/14 | 20/0/160 | Δχ² 4.04/3.90@30y | Δχ² 1.55/1.49@10y | 10-17 23:17 | ok | - |
| Truncated | DayNight | fid_oldrule | 5/10/20 | 0/0/0 | 4.63σ@30y | 3.78σ@20y | 10-18 07:13 | ok | - |
| Truncated | HEP | fid_oldrule | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_oldrule | - | 20/20/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_300_60 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_300_0 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_noveto | - | 0/0/160 | - | - | - | missing | - |
| Truncated | HEP | fid_noveto | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_noveto | - | 20/0/160 | - | - | - | missing | - |
| Truncated | DayNight | fid_dn616 | 5/11/18 | 0/40/0 | 4.66σ@30y | 3.81σ@20y | 10-17 19:58 | ok | - |
| Truncated | DayNight | fid_bandmax | 5/11/18 | 60/20/20 | 4.75σ@30y | 3.88σ@20y | 10-17 17:55 | ok | - |
| Truncated | HEP | fid_bandmax | - | 0/0/520 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_bandmax | - | 0/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_lowband | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | fid_lowband | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_lowband | - | 20/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v140_300_60 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v80_240_160 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | HEP | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v0_200_260 | - | - | - | - | - | missing | - |
| Truncated | DayNight | fid_v100_60_480 | - | 0/0/0 | - | - | - | missing | - |
| Truncated | HEP | fid_v100_60_480 | - | 0/0/0 | - | - | - | missing | - |
| Truncated | Sensitivity | fid_v100_60_480 | - | 20/0/0 | - | - | - | missing | - |
| Truncated | DayNight | fid_fullspec | 5/11/18 | 0/0/0 | 4.68σ@30y | 3.82σ@20y | 10-16 23:41 | ok | - |
| Truncated | HEP | fid_fullspec | 1/8/19 | 0/0/520 | 2.09σ@30y | 1.49σ@20y | 10-16 23:45 | ok | - |
| Truncated | Sensitivity | fid_fullspec | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 00:52 | ok | - |
| Truncated | DayNight | fid_nosb | 5/11/18 | 0/40/0 | 4.67σ@30y | 3.81σ@20y | 10-16 17:02 | ok | - |
| Truncated | HEP | fid_nosb | 6/4/18 | 0/120/520 | 2.19σ@30y | 1.91σ@20y | 10-16 17:11 | ok | - |
| Truncated | Sensitivity | fid_nosb | 5/6/14 | 0/40/0 | Δχ² 5.21/4.29@30y | Δχ² 1.95/1.62@10y | 10-16 21:15 | ok | - |
| Truncated | HEP | hep_plain_opt | 5/20/15 | 0/0/520 | 1.80σ@30y | 1.57σ@20y | 10-17 01:33 | ok | - |
| Truncated | DayNight | mcfloor_10 | 5/11/18 | 0/0/0 | 4.75σ@30y | 3.88σ@20y | 10-16 15:31 | ok | ⚪ vs default: 4.75 vs 5.06 |
| Truncated | HEP | mcfloor_10 | 6/8/18 | 0/0/520 | 2.25σ@30y | 1.96σ@20y | 10-16 15:35 | ok | ⚪ vs default: 2.25 vs 3.34 |
| Truncated | Sensitivity | mcfloor_10 | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-16 16:39 | ok | ⚪ vs default: 4.33 vs 5.08 |
| Truncated | DayNight | mcfloor_25 | 5/11/18 | 0/0/0 | 4.75σ@30y | 3.88σ@20y | 10-16 23:12 | ok | ⚪ vs default: 4.75 vs 5.06 |
| Truncated | HEP | mcfloor_25 | 6/8/18 | 0/0/520 | 2.25σ@30y | 1.96σ@20y | 10-16 23:15 | ok | ⚪ vs default: 2.25 vs 3.34 |
| Truncated | Sensitivity | mcfloor_25 | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 00:08 | ok | ⚪ vs default: 4.33 vs 5.08 |
| Truncated | DayNight | mcfloor_50 | 5/11/18 | 0/0/0 | 4.75σ@30y | 3.88σ@20y | 10-17 04:46 | ok | ⚪ vs default: 4.75 vs 5.06 |
| Truncated | HEP | mcfloor_50 | 6/8/18 | 0/0/520 | 2.25σ@30y | 1.96σ@20y | 10-17 04:49 | ok | ⚪ vs default: 2.25 vs 3.34 |
| Truncated | Sensitivity | mcfloor_50 | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 05:46 | ok | ⚪ vs default: 4.33 vs 5.08 |
| Truncated | DayNight | bkgsub_s1 | 5/7/14 | 20/0/0 | 4.66σ@30y | 3.81σ@20y | 10-17 04:45 | ok | ⚪ vs default: 4.66 vs 5.06 |
| Truncated | HEP | bkgsub_s1 | 5/20/14 | 0/0/20*† | 2.93σ@30y | 2.55σ@20y | 10-17 04:49 | ok | ⚪ vs default: 2.93 vs 3.34 |
| Truncated | Sensitivity | bkgsub_s1 | 5/7/15 | 0/260/20 | Δχ² 4.35/4.22@30y | Δχ² 1.65/1.59@10y | 10-17 05:45 | ok | ⚪ vs default: 4.35 vs 5.08 |
| Truncated | DayNight | bkgsub_s2 | 5/11/18 | 20/0/0 | 4.79σ@30y | 3.91σ@20y | 10-17 06:48 | ok | ⚪ vs default: 4.79 vs 5.06 |
| Truncated | HEP | bkgsub_s2 | 5/19/16 | 20/0/0*† | 2.56σ@30y | 2.23σ@20y | 10-17 06:51 | ok | ⚪ vs default: 2.56 vs 3.34 |
| Truncated | Sensitivity | bkgsub_s2 | 5/11/18 | 20/0/0 | Δχ² 4.27/4.03@30y | Δχ² 1.63/1.54@10y | 10-17 07:41 | ok | ⚪ vs default: 4.27 vs 5.08 |
| Truncated | DayNight | bkgsub_s3 | 5/10/12 | 0/0/0 | 4.59σ@30y | 3.74σ@20y | 10-17 06:51 | ok | ⚪ vs default: 4.59 vs 5.06 |
| Truncated | HEP | bkgsub_s3 | 5/20/16 | 0/0/0*† | 2.85σ@30y | 2.48σ@20y | 10-17 06:54 | ok | ⚪ vs default: 2.85 vs 3.34 |
| Truncated | Sensitivity | bkgsub_s3 | 5/11/15 | 0/0/0 | Δχ² 4.77/4.62@30y | Δχ² 1.79/1.73@10y | 10-17 07:51 | ok | ⚪ vs default: 4.77 vs 5.08 |
| Truncated | HEP | hep_extmask | 4/19/2 | 0/0/520 | 3.29σ@30y | 2.86σ@20y | 10-16 22:05 | ok | ⚪ vs default: 3.29 vs 3.34 |
| Truncated | HEP | hep_looseshape | 5/20/15 | 0/0/520 | 5.26σ@30y | 4.59σ@20y | 10-17 02:58 | ok | ⚪ vs default: 5.26 vs 3.34 |
| Truncated | HEP | hep_looseshape_plain | 5/20/15 | 0/0/520 | 4.40σ@30y | 3.84σ@20y | 10-17 03:39 | ok | ⚪ vs default: 4.40 vs 3.34 |
| Truncated | HEP | hep_looseshape_nh | - | 0/0/0 | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_looseshape_win | 6/4/18 | 0/0/0 | 2.51σ@30y | 2.19σ@20y | 10-18 10:52 | ok | ⚪ vs default: 2.51 vs 3.34 |
| Truncated | HEP | sb_hep90 | 5/17/20 | 0/0/0 | 1.60σ@30y | 1.40σ@20y | 10-08 04:32 | ok | ⚪ vs default: 1.60 vs 3.34 |
| Truncated | HEP | hep_sbmodel | 4/19/2 | 0/0/0 | 0.94σ@30y | 0.82σ@20y | 10-09 20:39 | ok | ⚪ vs default: 0.94 vs 3.34 |
| Truncated | HEP | hep_plain | 4/19/2 | 0/0/0 | 0.83σ@30y | 0.72σ@20y | 10-09 20:58 | ok | ⚪ vs default: 0.83 vs 3.34 |
| Truncated | DayNight | ncveto | 5/11/19 | 0/0/0 | 3.64σ@30y | 2.97σ@20y | 10-09 14:11 | ok | ⚪ vs default: 3.64 vs 5.06 |
| Truncated | Sensitivity | ncveto | 5/11/15 | 20/0/0 | Δχ² 3.05/2.95@30y | Δχ² 1.20/1.16@10y | 10-09 15:03 | ok | ⚪ vs default: 3.05 vs 5.08 |
| Truncated | DayNight | ncveto_off | 5/14/15 | 0/0/0 | 4.55σ@30y | 3.72σ@20y | 10-17 08:18 | ok | ⚪ vs default: 4.55 vs 5.06 |
| Truncated | Sensitivity | ncveto_off | 5/11/18 | 0/0/0 | Δχ² 4.12/3.98@30y | Δχ² 1.57/1.52@10y | 10-17 09:10 | ok | ⚪ vs default: 4.12 vs 5.08 |
| Truncated | DayNight | mcgate_50 | 5/11/18 | 0/0/0 | 4.90σ@30y | 4.00σ@20y | 10-10 00:38 | ok | ⚪ vs default: 4.90 vs 5.06 |
| Truncated | HEP | mcgate_50 | 4/19/2 | 0/0/0 | 3.02σ@30y | 2.63σ@20y | 10-10 00:42 | ok | ⚪ vs default: 3.02 vs 3.34 |
| Truncated | Sensitivity | mcgate_50 | 5/11/15 | 20/0/0 | Δχ² 3.02/2.92@30y | Δχ² 1.19/1.15@10y | 10-10 01:31 | ok | ⚪ vs default: 3.02 vs 5.08 |
| Truncated | DayNight | mcgate_20 | 5/11/18 | 0/0/0 | 4.75σ@30y | 3.88σ@20y | 10-17 02:39 | ok | ⚪ vs default: 4.75 vs 5.06 |
| Truncated | HEP | mcgate_20 | 6/8/18 | 0/0/520 | 2.25σ@30y | 1.96σ@20y | 10-17 02:42 | ok | ⚪ vs default: 2.25 vs 3.34 |
| Truncated | Sensitivity | mcgate_20 | 4/13/18 | 0/0/0 | Δχ² 4.33/4.18@30y | Δχ² 1.66/1.60@10y | 10-17 03:38 | ok | ⚪ vs default: 4.33 vs 5.08 |
| Truncated | DayNight | mcgate_0 | 5/11/18 | 0/0/0 | 3.87σ@30y | 3.16σ@20y | 10-10 04:05 | ok | ⚪ vs default: 3.87 vs 5.06 |
| Truncated | HEP | mcgate_0 | 4/19/2 | 0/0/0 | 2.98σ@30y | 2.60σ@20y | 10-10 04:08 | ok | ⚪ vs default: 2.98 vs 3.34 |
| Truncated | Sensitivity | mcgate_0 | - | 20/0/0 | - | - | - | missing | ⚪ vs default: n/a |
| Truncated | HEP | hep_mcf3 | 4/19/2 | 0/0/0 | 3.13σ@30y | 2.73σ@20y | 10-10 13:06 | ok | ⚪ vs default: 3.13 vs 3.34 |
| Truncated | HEP | hep_mcf5 | 5/11/2 | 0/0/0 | 3.75σ@30y | 3.27σ@20y | 10-10 13:22 | ok | ⚪ vs default: 3.75 vs 3.34 |
| Truncated | DayNight | oscpoint_solar | 5/10/20 | 20/0/160 | 4.80σ@30y | 3.92σ@20y | 10-20 19:25 | ok | **🔴 == default: 4.80 vs 5.06 UNEXPECTED (fresh)** |
| Truncated | HEP | oscpoint_solar | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-20 19:29 | ok | 🟢 == default: 3.34 vs 3.34 OK |
| Truncated | DayNight | oscpoint_reactor | 5/10/20 | 20/0/160 | 3.63σ@30y | 2.97σ@20y | 10-20 12:30 | ok | 🟢 <= default: 3.63 vs 5.06 OK |
| Truncated | HEP | oscpoint_reactor | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-20 12:34 | ok | 🟢 == default: 3.34 vs 3.34 OK |
| Truncated | DayNight | fiduc_truth | 4/7/20 | 160/100/0*† | 10.29σ@30y | 8.40σ@20y | 10-20 12:44 | ok | 🟢 >= default: 10.29 vs 5.06 OK |
| Truncated | HEP | fiduc_truth | 2/4/19 | 160/60/0* | 10.00σ@30y | 8.72σ@20y | 10-20 12:47 | ok | 🟢 >= default: 10.00 vs 3.34 OK |
| Truncated | Sensitivity | fiduc_truth | 4/7/20 | 160/80/0*† | Δχ² 15.05/14.71@30y | Δχ² 5.26/5.14@10y | 10-20 13:35 | ok | 🟢 >= default: 15.05 vs 5.08 OK |
| Truncated | DayNight | fiduc_truth_refvol | - | 0/0/0 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | HEP | fiduc_truth_refvol | - | 0/0/0 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | Sensitivity | fiduc_truth_refvol | - | 20/0/0 | - | - | - | missing | ⚪ vs fiduc_truth: n/a |
| Truncated | DayNight | bkg_gamma_cluster | 5/10/20 | 0/0/160 | 4.38σ@30y | 3.58σ@20y | 10-20 18:12 | ok | ⚪ vs default: 4.38 vs 5.06 |
| Truncated | HEP | bkg_gamma_cluster | 3/19/2 | 80/0/0 | 1.67σ@30y | 1.45σ@20y | 10-20 18:17 | ok | ⚪ vs default: 1.67 vs 3.34 |
| Truncated | Sensitivity | bkg_gamma_cluster | 4/4/15 | 0/0/160 | Δχ² 4.53/4.37@30y | Δχ² 1.72/1.66@10y | 10-20 18:30 | ok | ⚪ vs default: 4.53 vs 5.08 |
| Truncated | DayNight | bkg_gamma_total | 5/10/20 | 0/0/0 | 4.73σ@30y | 3.86σ@20y | 10-20 18:44 | ok | ⚪ vs default: 4.73 vs 5.06 |
| Truncated | HEP | bkg_gamma_total | 3/19/2 | 20/40/40 | 1.31σ@30y | 1.14σ@20y | 10-20 18:49 | ok | ⚪ vs default: 1.31 vs 3.34 |
| Truncated | Sensitivity | bkg_gamma_total | 4/4/15 | 100/40/0 | Δχ² 3.11/3.01@30y | Δχ² 1.22/1.18@10y | 10-20 19:00 | ok | ⚪ vs default: 3.11 vs 5.08 |
| Truncated | DayNight | membrane_veto_off | 5/10/20 | 20/0/160 | 4.76σ@30y | 3.88σ@20y | 10-20 13:19 | ok | **🔴 >= default: 4.76 vs 5.06 UNEXPECTED (fresh)** |
| Truncated | HEP | membrane_veto_off | 3/19/2 | 0/0/0 | 3.34σ@30y | 2.91σ@20y | 10-20 13:22 | ok | 🟢 >= default: 3.34 vs 3.34 OK |
| Truncated | Sensitivity | membrane_veto_off | 4/4/15 | 20/0/160 | Δχ² 4.97/4.80@30y | Δχ² 1.86/1.79@10y | 10-20 13:32 | ok | ⚪ vs default: 4.97 vs 5.08 |
| Truncated | Sensitivity | legacy_fit | - | 20/0/0 | - | - | - | missing | ⚪ vs default: n/a |
