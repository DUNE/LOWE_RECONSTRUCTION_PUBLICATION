# Study status 20260921_v15

Epochs: DayNight=2026-09-18T13:00, Sensitivity=2026-09-18T13:00, HEP=2026-09-18T13:00

cut = NHits/OpHits/AdjCl. fiducial = FiducialX/Y/Z (cm) from BestFiducials*.json for that config/folder/analysis/energy (- if no record). DayNight/HEP: smoothed Asimov / profile-likelihood significance; Sensitivity: Δχ² solar-fit-at-reactor / reactor-fit-at-solar (full profile unless a nuisance study).

trend: 🟢 study follows the expected relation to its reference; 🟠 it does not, but one side has a known bug or still awaits its rerun (re-check after the queue); 🔴 it does not and both sides are fresh -> a bug to evaluate; ⚪ informational or no reference. Relations use 2% slack for >=/<= and 5% for ==; the reference for a scan is the neighbouring variant (unc_sig0 vs unc_sig2, charge_Q100 vs charge_Q50, ...). See EXPECTED_TRENDS in src/tools/study_status.py.

Trend summary: 🟢 129 expected, 🟠 0 unexpected but rerun pending, 🔴 1 unexpected on fresh results.

Rows to evaluate (unexpected, both sides fresh):

- vd_1x8x14_3view_30deg_shielded / Nominal / Sensitivity / default: <= Truncated default: 0.46 vs 0.40 UNEXPECTED (fresh)


## hd_1x2x6_centralAPA

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 3/11/2 | 20/100/320 | 5.47σ@30y | 4.46σ@20y | 09-22 01:53 | ok | - |
| Truncated | HEP | default | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-22 02:24 | ok | - |
| Truncated | Sensitivity | default | 3/12/2 | 0/80/100 | Δχ² 5.79/5.67@30y | Δχ² 5.79/5.67@30y | 09-18 19:48 | ok | - |
| Nominal | DayNight | default | 3/12/3 | 20/80/320 | 4.92σ@30y | 4.02σ@20y | 09-22 01:54 | ok | 🟢 <= Truncated default: 4.92 vs 5.47 OK |
| Nominal | HEP | default | 4/13/5 | 100/80/100 | 12.18σ@30y | 10.62σ@20y | 09-22 02:24 | ok | 🟢 <= Truncated default: 12.18 vs 12.18 OK |
| Nominal | Sensitivity | default | 3/12/2 | 0/80/100 | Δχ² 3.83/3.74@30y | Δχ² 3.83/3.74@30y | 09-21 22:52 | ok | 🟢 <= Truncated default: 3.83 vs 5.79 OK |
| Reduced | DayNight | default | 2/11/4 | 20/100/320 | 6.42σ@30y | 5.24σ@20y | 09-22 01:56 | ok | 🟢 >= Truncated default: 6.42 vs 5.47 OK |
| Reduced | HEP | default | 4/13/6 | 0/80/0 | 12.61σ@30y | 10.99σ@20y | 09-22 02:26 | ok | 🟢 >= Truncated default: 12.61 vs 12.18 OK |
| Reduced | Sensitivity | default | 3/12/2 | 0/80/100 | Δχ² 5.85/5.73@30y | Δχ² 5.85/5.73@30y | 09-21 22:54 | ok | 🟢 >= Truncated default: 5.85 vs 5.79 OK |
| Truncated | HEP | unc_sig20 | 4/13/5 | 0/80/0 | 13.43σ@30y | 11.71σ@20y | 09-21 19:06 | ok | 🟢 >= default: 13.43 vs 12.18 OK |
| Truncated | HEP | unc_sig40 | 4/13/5 | 0/80/0 | 10.88σ@30y | 9.49σ@20y | 09-21 22:52 | ok | 🟢 <= default: 10.88 vs 12.18 OK |
| Truncated | Sensitivity | unc_sig0 | 3/12/2 | 0/80/100 | Δχ² 13.30/13.28@30y | Δχ² 13.30/13.28@30y | 09-21 20:16 | ok | 🟢 >= unc_sig2: 13.30 vs 6.65 OK |
| Truncated | Sensitivity | unc_sig2 | 3/12/2 | 0/80/100 | Δχ² 6.65/6.50@30y | Δχ² 6.65/6.50@30y | 09-21 20:17 | ok | 🟢 >= default: 6.65 vs 5.79 OK |
| Truncated | Sensitivity | unc_sig6 | 3/12/2 | 0/80/100 | Δχ² 5.60/5.49@30y | Δχ² 5.60/5.49@30y | 09-21 20:19 | ok | 🟢 <= default: 5.60 vs 5.79 OK |
| Truncated | DayNight | unc_bkg0 | 3/11/2 | 20/100/320 | 5.47σ@30y | 4.46σ@20y | 09-21 18:40 | ok | 🟢 == default: 5.47 vs 5.47 OK |
| Truncated | HEP | unc_bkg0 | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-21 19:05 | ok | 🟢 == default: 12.18 vs 12.18 OK |
| Truncated | DayNight | unc_bkg4 | 3/11/2 | 20/100/320 | 5.47σ@30y | 4.46σ@20y | 09-21 22:55 | ok | 🟢 == default: 5.47 vs 5.47 OK |
| Truncated | HEP | unc_bkg4 | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-21 22:58 | ok | 🟢 == default: 12.18 vs 12.18 OK |
| Truncated | DayNight | unc_bkg6 | 3/11/2 | 20/100/320 | 5.47σ@30y | 4.46σ@20y | 09-21 21:11 | ok | 🟢 == default: 5.47 vs 5.47 OK |
| Truncated | HEP | unc_bkg6 | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-21 21:14 | ok | 🟢 == default: 12.18 vs 12.18 OK |
| Truncated | Sensitivity | nuisance_nominal | 3/12/2 | 0/80/100 | Δχ² 5.97/5.86@30y | Δχ² 5.97/5.86@30y | 09-21 18:46 | ok | 🟢 >= nuisance_sin13: 5.97 vs 5.97 OK |
| Truncated | Sensitivity | nuisance_sin13 | 3/12/2 | 0/80/100 | Δχ² 5.97/5.86@30y | Δχ² 5.97/5.86@30y | 09-21 19:30 | ok | 🟢 >= default: 5.97 vs 5.79 OK |
| Truncated | Sensitivity | nuisance_escale | 3/12/2 | 0/80/100 | Δχ² 5.79/5.67@30y | Δχ² 5.79/5.67@30y | 09-21 20:21 | ok | 🟢 >= default: 5.79 vs 5.79 OK |
| Truncated | DayNight | energy_spk | 4/11/7 | 20/100/320 | 3.41σ@30y | 2.79σ@20y | 09-21 11:55 | ok | ⚪ vs default: 3.41 vs 5.47 |
| Truncated | HEP | energy_spk | 4/10/2 | 0/80/0 | 26.55σ@30y | 23.11σ@20y | 09-21 11:58 | ok | ⚪ vs default: 26.55 vs 12.18 |
| Truncated | Sensitivity | energy_spk | 4/11/14 | 0/80/100 | Δχ² 0.16/0.16@30y | Δχ² 0.16/0.16@30y | 09-21 19:36 | ok | ⚪ vs default: 0.16 vs 5.79 |
| Truncated | DayNight | energy_maink | 3/11/4 | 20/100/320 | 5.67σ@30y | 4.63σ@20y | 09-21 20:49 | ok | ⚪ vs default: 5.67 vs 5.47 |
| Truncated | HEP | energy_maink | 1/15/10 | 0/80/0 | 20.49σ@30y | 17.83σ@20y | 09-21 20:55 | ok | ⚪ vs default: 20.49 vs 12.18 |
| Truncated | Sensitivity | energy_maink | 4/12/5 | 0/80/100 | Δχ² 8.20/8.01@30y | Δχ² 8.20/8.01@30y | 09-21 21:48 | ok | ⚪ vs default: 8.20 vs 5.79 |
| Truncated | DayNight | charge_Q0 | 1/11/2 | 40/180/100 | 4.42σ@30y | 3.61σ@20y | 09-19 16:34 | ok | ⚪ vs default: 4.42 vs 5.47 |
| Truncated | HEP | charge_Q0 | 4/10/3 | 80/120/60 | 11.04σ@30y | 9.63σ@20y | 09-19 16:37 | ok | ⚪ vs default: 11.04 vs 12.18 |
| Truncated | Sensitivity | charge_Q0 | 3/12/2 | 40/120/100 | Δχ² 5.15/5.04@30y | Δχ² 5.15/5.04@30y | 09-19 16:48 | ok | ⚪ vs default: 5.15 vs 5.79 |
| Truncated | DayNight | charge_Q50 | 1/11/2 | 40/180/100 | 3.47σ@30y | 2.83σ@20y | 09-21 19:50 | ok | ⚪ vs charge_Q0: 3.47 vs 4.42 |
| Truncated | HEP | charge_Q50 | 1/13/4 | 80/120/60 | 10.67σ@30y | 9.29σ@20y | 09-21 23:06 | ok | ⚪ vs charge_Q0: 10.67 vs 11.04 |
| Truncated | Sensitivity | charge_Q50 | 3/12/2 | 40/120/100 | Δχ² 7.64/7.41@30y | Δχ² 7.64/7.41@30y | 09-18 22:32 | ok | ⚪ vs charge_Q0: 7.64 vs 5.15 |
| Truncated | DayNight | charge_Q100 | 1/10/2 | 40/180/100 | 2.73σ@30y | 2.23σ@20y | 09-21 22:12 | ok | ⚪ vs charge_Q50: 2.73 vs 3.47 |
| Truncated | HEP | charge_Q100 | 4/11/5 | 80/120/60 | 9.98σ@30y | 8.70σ@20y | 09-21 22:15 | ok | ⚪ vs charge_Q50: 9.98 vs 10.67 |
| Truncated | Sensitivity | charge_Q100 | 3/12/2 | 40/120/100 | Δχ² 7.64/7.42@30y | Δχ² 7.64/7.42@30y | 09-21 22:24 | ok | ⚪ vs charge_Q50: 7.64 vs 7.64 |
| Truncated | DayNight | charge_Q500 | 2/5/4 | 40/180/100 | 1.53σ@30y | 1.25σ@20y | 09-18 22:27 | ok | ⚪ vs charge_Q100: 1.53 vs 2.73 |
| Truncated | HEP | charge_Q500 | 1/4/4 | 80/120/60 | 9.04σ@30y | 7.88σ@20y | 09-18 22:34 | ok | ⚪ vs charge_Q100: 9.04 vs 9.98 |
| Truncated | Sensitivity | charge_Q500 | 3/12/2 | 40/120/100 | Δχ² 7.39/7.20@30y | Δχ² 7.39/7.20@30y | 09-21 22:11 | ok | ⚪ vs charge_Q100: 7.39 vs 7.64 |
| Nominal | DayNight | bkgmodel_nominal | 3/11/2 | 20/80/320 | 4.88σ@30y | 3.98σ@20y | 09-18 20:32 | ok | 🟢 <= Truncated default: 4.88 vs 5.47 OK |
| Nominal | HEP | bkgmodel_nominal | 4/13/5 | 100/80/100 | 12.18σ@30y | 10.62σ@20y | 09-18 20:36 | ok | 🟢 <= Truncated default: 12.18 vs 12.18 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 3/12/2 | 0/80/100 | Δχ² 3.83/3.74@30y | Δχ² 3.83/3.74@30y | 09-18 20:46 | ok | 🟢 <= Truncated default: 3.83 vs 5.79 OK |
| Reduced | DayNight | bkgmodel_reduced | 3/11/2 | 20/100/320 | 5.55σ@30y | 4.53σ@20y | 09-18 21:26 | ok | 🟢 >= Truncated default: 5.55 vs 5.47 OK |
| Reduced | HEP | bkgmodel_reduced | 4/13/5 | 0/80/0 | 12.58σ@30y | 10.97σ@20y | 09-18 21:30 | ok | 🟢 >= Truncated default: 12.58 vs 12.18 OK |
| Reduced | Sensitivity | bkgmodel_reduced | 3/12/2 | 0/80/100 | Δχ² 5.85/5.73@30y | Δχ² 5.85/5.73@30y | 09-18 21:40 | ok | 🟢 >= Truncated default: 5.85 vs 5.79 OK |
| Truncated | DayNight | oscpoint_solar | 3/11/2 | 20/100/320 | 5.47σ@30y | 4.46σ@20y | 09-21 18:47 | ok | 🟢 == default: 5.47 vs 5.47 OK |
| Truncated | HEP | oscpoint_solar | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-21 19:11 | ok | 🟢 == default: 12.18 vs 12.18 OK |
| Truncated | DayNight | oscpoint_reactor | 3/11/2 | 20/100/320 | 4.13σ@30y | 3.37σ@20y | 09-21 19:01 | ok | 🟢 <= default: 4.13 vs 5.47 OK |
| Truncated | HEP | oscpoint_reactor | 4/13/5 | 0/80/0 | 12.16σ@30y | 10.60σ@20y | 09-21 19:19 | ok | 🟢 == default: 12.16 vs 12.18 OK |
| Truncated | DayNight | fiduc_truth | 3/11/2 | 100/80/320 | 5.47σ@30y | 4.47σ@20y | 09-20 13:43 | ok | 🟢 >= default: 5.47 vs 5.47 OK |
| Truncated | HEP | fiduc_truth | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-20 13:47 | ok | 🟢 >= default: 12.18 vs 12.18 OK |
| Truncated | Sensitivity | fiduc_truth | 3/13/3 | 0/100/20 | Δχ² 7.63/7.45@30y | Δχ² 7.63/7.45@30y | 09-20 14:34 | ok | 🟢 >= default: 7.63 vs 5.79 OK |
| Truncated | DayNight | fiduc_truth_refvol | 3/11/2 | 20/100/320 | 5.45σ@30y | 4.45σ@20y | 09-20 15:15 | ok | ⚪ vs fiduc_truth: 5.45 vs 5.47 |
| Truncated | HEP | fiduc_truth_refvol | 4/13/5 | 0/80/0 | 12.18σ@30y | 10.62σ@20y | 09-20 15:18 | ok | ⚪ vs fiduc_truth: 12.18 vs 12.18 |
| Truncated | Sensitivity | fiduc_truth_refvol | 3/12/2 | 0/80/100 | Δχ² 7.70/7.53@30y | Δχ² 7.70/7.53@30y | 09-20 16:07 | ok | ⚪ vs fiduc_truth: 7.70 vs 7.63 |
| Truncated | DayNight | bkg_gamma_cluster | 3/11/2 | 0/140/0 | 4.48σ@30y | 3.66σ@20y | 09-21 23:36 | ok | ⚪ vs default: 4.48 vs 5.47 |
| Truncated | HEP | bkg_gamma_cluster | 1/4/6 | 0/140/0 | 10.28σ@30y | 8.96σ@20y | 09-21 23:39 | ok | ⚪ vs default: 10.28 vs 12.18 |
| Truncated | Sensitivity | bkg_gamma_cluster | 3/12/2 | 0/140/0 | Δχ² 3.39/3.32@30y | Δχ² 3.39/3.32@30y | 09-21 23:48 | ok | ⚪ vs default: 3.39 vs 5.79 |
| Truncated | DayNight | bkg_gamma_total | 1/9/2 | 100/280/120 | 3.72σ@30y | 3.04σ@20y | 09-21 21:20 | ok | ⚪ vs default: 3.72 vs 5.47 |
| Truncated | HEP | bkg_gamma_total | 2/14/3 | 20/0/0 | 11.40σ@30y | 9.93σ@20y | 09-21 21:23 | ok | ⚪ vs default: 11.40 vs 12.18 |
| Truncated | Sensitivity | bkg_gamma_total | 3/12/2 | 100/280/120 | Δχ² 3.63/3.56@30y | Δχ² 3.63/3.56@30y | 09-21 21:33 | ok | ⚪ vs default: 3.63 vs 5.79 |
| Truncated | Sensitivity | legacy_fit | 3/12/2 | 0/80/100 | Δχ² 7.43/5.16@30y | Δχ² 7.43/5.16@30y | 09-18 23:23 | ok | ⚪ vs default: 7.43 vs 5.79 |

## hd_1x2x6_lateralAPA

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 4/4/4 | 80/140/240 | 1.54σ@30y | 1.25σ@20y | 09-22 01:56 | ok | - |
| Truncated | HEP | default | 3/8/9 | 60/80/20 | 5.67σ@30y | 4.94σ@20y | 09-22 02:38 | ok | - |
| Truncated | Sensitivity | default | 4/4/4 | 60/260/200 | Δχ² 0.41/0.40@30y | Δχ² 0.41/0.40@30y | 09-18 19:08 | ok | - |
| Nominal | DayNight | default | 4/4/4 | 80/260/220 | 1.18σ@30y | 0.96σ@20y | 09-22 01:58 | ok | 🟢 <= Truncated default: 1.18 vs 1.54 OK |
| Nominal | HEP | default | 1/8/9 | 60/220/60 | 5.59σ@30y | 4.87σ@20y | 09-22 02:37 | ok | 🟢 <= Truncated default: 5.59 vs 5.67 OK |
| Nominal | Sensitivity | default | 4/6/3 | 60/260/220 | Δχ² 0.30/0.29@30y | Δχ² 0.30/0.29@30y | 09-21 19:23 | ok | 🟢 <= Truncated default: 0.30 vs 0.41 OK |
| Reduced | DayNight | default | 4/4/4 | 80/140/240 | 3.89σ@30y | 3.18σ@20y | 09-22 02:00 | ok | 🟢 >= Truncated default: 3.89 vs 1.54 OK |
| Reduced | HEP | default | 4/8/9 | 60/80/20 | 6.33σ@30y | 5.52σ@20y | 09-22 02:42 | ok | 🟢 >= Truncated default: 6.33 vs 5.67 OK |
| Reduced | Sensitivity | default | 3/4/5 | 60/260/200 | Δχ² 2.10/2.04@30y | Δχ² 2.10/2.04@30y | 09-21 23:45 | ok | 🟢 >= Truncated default: 2.10 vs 0.41 OK |
| Truncated | HEP | unc_sig20 | 3/8/9 | 60/80/20 | 6.12σ@30y | 5.33σ@20y | 09-21 12:13 | ok | 🟢 >= default: 6.12 vs 5.67 OK |
| Truncated | HEP | unc_sig40 | 3/8/9 | 60/80/20 | 5.20σ@30y | 4.53σ@20y | 09-21 18:57 | ok | 🟢 <= default: 5.20 vs 5.67 OK |
| Truncated | Sensitivity | unc_sig0 | 4/4/4 | 60/260/200 | Δχ² 0.55/0.55@30y | Δχ² 0.55/0.55@30y | 09-19 11:22 | ok | 🟢 >= unc_sig2: 0.55 vs 0.50 OK |
| Truncated | Sensitivity | unc_sig2 | 4/4/4 | 60/260/200 | Δχ² 0.50/0.49@30y | Δχ² 0.50/0.49@30y | 09-19 00:08 | ok | 🟢 >= default: 0.50 vs 0.41 OK |
| Truncated | Sensitivity | unc_sig6 | 4/4/4 | 60/260/200 | Δχ² 0.35/0.34@30y | Δχ² 0.35/0.34@30y | 09-21 19:42 | ok | 🟢 <= default: 0.35 vs 0.41 OK |
| Truncated | DayNight | unc_bkg0 | 4/4/4 | 80/140/240 | 1.54σ@30y | 1.25σ@20y | 09-21 12:41 | ok | 🟢 == default: 1.54 vs 1.54 OK |
| Truncated | HEP | unc_bkg0 | 3/8/9 | 60/80/20 | 5.67σ@30y | 4.94σ@20y | 09-21 23:12 | ok | 🟢 == default: 5.67 vs 5.67 OK |
| Truncated | DayNight | unc_bkg4 | 4/4/4 | 80/140/240 | 1.54σ@30y | 1.25σ@20y | 09-21 23:15 | ok | 🟢 == default: 1.54 vs 1.54 OK |
| Truncated | HEP | unc_bkg4 | 3/8/9 | 60/80/20 | 5.67σ@30y | 4.94σ@20y | 09-21 23:18 | ok | 🟢 == default: 5.67 vs 5.67 OK |
| Truncated | DayNight | unc_bkg6 | 4/4/4 | 80/140/240 | 1.54σ@30y | 1.25σ@20y | 09-21 21:11 | ok | 🟢 == default: 1.54 vs 1.54 OK |
| Truncated | HEP | unc_bkg6 | 3/8/9 | 60/80/20 | 5.67σ@30y | 4.94σ@20y | 09-21 21:14 | ok | 🟢 == default: 5.67 vs 5.67 OK |
| Truncated | Sensitivity | nuisance_nominal | 4/4/4 | 60/260/200 | Δχ² 0.43/0.41@30y | Δχ² 0.43/0.41@30y | 09-19 11:23 | ok | 🟢 >= nuisance_sin13: 0.43 vs 0.43 OK |
| Truncated | Sensitivity | nuisance_sin13 | 4/4/4 | 60/260/200 | Δχ² 0.43/0.41@30y | Δχ² 0.43/0.41@30y | 09-19 00:31 | ok | 🟢 >= default: 0.43 vs 0.41 OK |
| Truncated | Sensitivity | nuisance_escale | 4/4/4 | 60/260/200 | Δχ² 0.41/0.40@30y | Δχ² 0.41/0.40@30y | 09-19 00:34 | ok | 🟢 >= default: 0.41 vs 0.41 OK |
| Truncated | DayNight | energy_spk | 4/11/8 | 80/140/240 | 1.90σ@30y | 1.55σ@20y | 09-21 11:45 | ok | ⚪ vs default: 1.90 vs 1.54 |
| Truncated | HEP | energy_spk | 4/11/6 | 60/80/20 | 32.30σ@30y | 28.08σ@20y | 09-21 11:49 | ok | ⚪ vs default: 32.30 vs 5.67 |
| Truncated | Sensitivity | energy_spk | 4/5/19 | 60/260/200 | Δχ² 0.02/0.02@30y | Δχ² 0.02/0.02@30y | 09-21 19:23 | ok | ⚪ vs default: 0.02 vs 0.41 |
| Truncated | DayNight | energy_maink | 4/7/4 | 80/140/240 | 0.84σ@30y | 0.69σ@20y | 09-21 20:30 | ok | ⚪ vs default: 0.84 vs 1.54 |
| Truncated | HEP | energy_maink | 1/4/12 | 60/80/20 | 16.44σ@30y | 14.27σ@20y | 09-21 20:34 | ok | ⚪ vs default: 16.44 vs 5.67 |
| Truncated | Sensitivity | energy_maink | 4/9/4 | 60/260/200 | Δχ² 0.43/0.41@30y | Δχ² 0.43/0.41@30y | 09-21 21:23 | ok | ⚪ vs default: 0.43 vs 0.41 |
| Truncated | DayNight | charge_Q0 | 4/4/4 | 0/0/20 | 0.93σ@30y | 0.76σ@20y | 09-19 16:33 | ok | ⚪ vs default: 0.93 vs 1.54 |
| Truncated | HEP | charge_Q0 | 3/8/9 | 40/0/120 | 2.28σ@30y | 1.99σ@20y | 09-19 16:36 | ok | ⚪ vs default: 2.28 vs 5.67 |
| Truncated | Sensitivity | charge_Q0 | 4/4/4 | 20/0/0 | Δχ² 0.16/0.15@30y | Δχ² 0.16/0.15@30y | 09-19 16:47 | ok | ⚪ vs default: 0.16 vs 0.41 |
| Truncated | DayNight | charge_Q50 | 4/4/4 | 0/0/20 | 0.82σ@30y | 0.67σ@20y | 09-21 19:00 | ok | ⚪ vs charge_Q0: 0.82 vs 0.93 |
| Truncated | HEP | charge_Q50 | 3/8/9 | 40/0/120 | 1.38σ@30y | 1.20σ@20y | 09-21 19:18 | ok | ⚪ vs charge_Q0: 1.38 vs 2.28 |
| Truncated | Sensitivity | charge_Q50 | 4/4/4 | 20/0/0 | Δχ² 2.98/2.88@30y | Δχ² 2.98/2.88@30y | 09-18 22:09 | ok | ⚪ vs charge_Q0: 2.98 vs 0.16 |
| Truncated | DayNight | charge_Q100 | 4/4/4 | 0/0/20 | 0.79σ@30y | 0.64σ@20y | 09-19 16:30 | ok | ⚪ vs charge_Q50: 0.79 vs 0.82 |
| Truncated | HEP | charge_Q100 | 3/8/9 | 40/0/120 | 0.48σ@30y | 0.42σ@20y | 09-19 16:34 | ok | ⚪ vs charge_Q50: 0.48 vs 1.38 |
| Truncated | Sensitivity | charge_Q100 | 4/4/4 | 20/0/0 | Δχ² 3.16/3.06@30y | Δχ² 3.16/3.06@30y | 09-18 22:07 | ok | ⚪ vs charge_Q50: 3.16 vs 2.98 |
| Truncated | DayNight | charge_Q500 | 1/13/7 | 0/0/20 | 0.71σ@30y | 0.58σ@20y | 09-21 22:02 | ok | ⚪ vs charge_Q100: 0.71 vs 0.79 |
| Truncated | HEP | charge_Q500 | 2/8/9 | 40/0/120 | 3.01σ@30y | 2.63σ@20y | 09-18 22:40 | ok | ⚪ vs charge_Q100: 3.01 vs 0.48 |
| Truncated | Sensitivity | charge_Q500 | 4/4/4 | 20/0/0 | Δχ² 4.59/4.46@30y | Δχ² 4.59/4.46@30y | 09-18 23:02 | ok | ⚪ vs charge_Q100: 4.59 vs 3.16 |
| Nominal | DayNight | bkgmodel_nominal | 4/4/4 | 80/260/220 | 1.18σ@30y | 0.96σ@20y | 09-18 19:42 | ok | 🟢 <= Truncated default: 1.18 vs 1.54 OK |
| Nominal | HEP | bkgmodel_nominal | 3/8/9 | 60/220/60 | 5.59σ@30y | 4.87σ@20y | 09-18 19:45 | ok | 🟢 <= Truncated default: 5.59 vs 5.67 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 4/4/4 | 60/260/220 | Δχ² 0.23/0.23@30y | Δχ² 0.23/0.23@30y | 09-18 19:57 | ok | 🟢 <= Truncated default: 0.23 vs 0.41 OK |
| Reduced | DayNight | bkgmodel_reduced | 4/4/4 | 80/140/240 | 3.89σ@30y | 3.18σ@20y | 09-18 20:32 | ok | 🟢 >= Truncated default: 3.89 vs 1.54 OK |
| Reduced | HEP | bkgmodel_reduced | 3/8/9 | 60/80/20 | 6.33σ@30y | 5.51σ@20y | 09-18 20:35 | ok | 🟢 >= Truncated default: 6.33 vs 5.67 OK |
| Reduced | Sensitivity | bkgmodel_reduced | 4/4/4 | 60/260/200 | Δχ² 1.96/1.92@30y | Δχ² 1.96/1.92@30y | 09-18 20:44 | ok | 🟢 >= Truncated default: 1.96 vs 0.41 OK |
| Truncated | DayNight | oscpoint_solar | 4/4/4 | 80/140/240 | 1.54σ@30y | 1.25σ@20y | 09-21 19:00 | ok | 🟢 == default: 1.54 vs 1.54 OK |
| Truncated | HEP | oscpoint_solar | 3/8/9 | 60/80/20 | 5.67σ@30y | 4.94σ@20y | 09-21 19:19 | ok | 🟢 == default: 5.67 vs 5.67 OK |
| Truncated | DayNight | oscpoint_reactor | 4/4/4 | 80/140/240 | 1.17σ@30y | 0.95σ@20y | 09-21 23:29 | ok | 🟢 <= default: 1.17 vs 1.54 OK |
| Truncated | HEP | oscpoint_reactor | 3/8/9 | 60/80/20 | 5.66σ@30y | 4.93σ@20y | 09-21 23:33 | ok | 🟢 == default: 5.66 vs 5.67 OK |
| Truncated | DayNight | fiduc_truth | 4/4/4 | 0/80/100 | 2.11σ@30y | 1.72σ@20y | 09-20 13:38 | ok | 🟢 >= default: 2.11 vs 1.54 OK |
| Truncated | HEP | fiduc_truth | 3/8/9 | 0/80/100 | 5.83σ@30y | 5.08σ@20y | 09-20 13:41 | ok | 🟢 >= default: 5.83 vs 5.67 OK |
| Truncated | Sensitivity | fiduc_truth | 2/4/3 | 60/60/0 | Δχ² 0.55/0.54@30y | Δχ² 0.55/0.54@30y | 09-20 14:29 | ok | 🟢 >= default: 0.55 vs 0.41 OK |
| Truncated | DayNight | fiduc_truth_refvol | 4/4/4 | 80/140/240 | 1.52σ@30y | 1.24σ@20y | 09-20 15:06 | ok | ⚪ vs fiduc_truth: 1.52 vs 2.11 |
| Truncated | HEP | fiduc_truth_refvol | 3/8/9 | 60/80/20 | 5.45σ@30y | 4.75σ@20y | 09-20 15:09 | ok | ⚪ vs fiduc_truth: 5.45 vs 5.83 |
| Truncated | Sensitivity | fiduc_truth_refvol | 2/4/3 | 60/260/200 | Δχ² 0.54/0.52@30y | Δχ² 0.54/0.52@30y | 09-20 15:56 | ok | ⚪ vs fiduc_truth: 0.54 vs 0.55 |
| Truncated | DayNight | bkg_gamma_cluster | 4/4/4 | 80/220/20 | 0.67σ@30y | 0.55σ@20y | 09-21 19:52 | ok | ⚪ vs default: 0.67 vs 1.54 |
| Truncated | HEP | bkg_gamma_cluster | 3/8/9 | 80/220/0 | 5.06σ@30y | 4.41σ@20y | 09-21 23:48 | ok | ⚪ vs default: 5.06 vs 5.67 |
| Truncated | Sensitivity | bkg_gamma_cluster | 4/4/4 | 80/220/0 | Δχ² 0.04/0.04@30y | Δχ² 0.04/0.04@30y | 09-21 23:56 | ok | ⚪ vs default: 0.04 vs 0.41 |
| Truncated | DayNight | bkg_gamma_total | 4/4/4 | 0/60/0 | 0.60σ@30y | 0.49σ@20y | 09-21 21:30 | ok | ⚪ vs default: 0.60 vs 1.54 |
| Truncated | HEP | bkg_gamma_total | 3/8/9 | 0/0/40 | 0.07σ@30y | 0.07σ@20y | 09-21 21:33 | ok | ⚪ vs default: 0.07 vs 5.67 |
| Truncated | Sensitivity | bkg_gamma_total | 4/4/4 | 0/0/40 | Δχ² 0.08/0.08@30y | Δχ² 0.08/0.08@30y | 09-21 21:42 | ok | ⚪ vs default: 0.08 vs 0.41 |
| Truncated | Sensitivity | legacy_fit | 4/4/4 | 60/260/200 | Δχ² 0.41/0.44@30y | Δχ² 0.41/0.44@30y | 09-19 02:47 | ok | ⚪ vs default: 0.41 vs 0.41 |

## vd_1x8x14_3view_30deg_nominal

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 6/13/6 | 0/20/60 | 0.86σ@30y | 0.70σ@20y | 09-22 02:51 | ok | - |
| Truncated | HEP | default | 5/4/14 | 0/0/40 | 2.76σ@30y | 2.39σ@20y | 09-22 03:51 | ok | - |
| Truncated | Sensitivity | default | 6/4/6 | 0/0/20 | Δχ² 0.08/0.08@30y | Δχ² 0.08/0.08@30y | 09-18 20:11 | ok | - |
| Nominal | DayNight | default | 5/19/5 | 140/100/0 | 0.89σ@30y | 0.72σ@20y | 09-22 02:51 | ok | 🟢 <= Truncated default: 0.89 vs 0.86 OK |
| Nominal | HEP | default | 2/4/14 | 0/0/40 | 2.75σ@30y | 2.41σ@20y | 09-22 03:51 | ok | 🟢 <= Truncated default: 2.75 vs 2.76 OK |
| Nominal | Sensitivity | default | 8/10/8 | 0/0/20 | Δχ² 0.04/0.04@30y | Δχ² 0.04/0.04@30y | 09-21 23:32 | ok | 🟢 <= Truncated default: 0.04 vs 0.08 OK |
| Reduced | DayNight | default | 6/14/7 | 0/20/60 | 2.09σ@30y | 1.71σ@20y | 09-22 02:54 | ok | 🟢 >= Truncated default: 2.09 vs 0.86 OK |
| Reduced | HEP | default | 6/4/14 | 0/0/40 | 3.04σ@30y | 2.64σ@20y | 09-22 03:52 | ok | 🟢 >= Truncated default: 3.04 vs 2.76 OK |
| Reduced | Sensitivity | default | 8/10/8 | 0/0/20 | Δχ² 0.33/0.32@30y | Δχ² 0.33/0.32@30y | 09-21 23:40 | ok | 🟢 >= Truncated default: 0.33 vs 0.08 OK |
| Truncated | HEP | unc_sig20 | 5/4/14 | 0/0/40 | 2.96σ@30y | 2.56σ@20y | 09-21 23:52 | ok | 🟢 >= default: 2.96 vs 2.76 OK |
| Truncated | HEP | unc_sig40 | 5/4/14 | 0/0/40 | 2.54σ@30y | 2.20σ@20y | 09-19 00:40 | ok | 🟢 <= default: 2.54 vs 2.76 OK |
| Truncated | Sensitivity | unc_sig0 | 6/4/6 | 0/0/20 | Δχ² 0.09/0.09@30y | Δχ² 0.09/0.09@30y | 09-21 18:59 | ok | 🟢 >= unc_sig2: 0.09 vs 0.09 OK |
| Truncated | Sensitivity | unc_sig2 | 6/4/6 | 0/0/20 | Δχ² 0.09/0.09@30y | Δχ² 0.09/0.09@30y | 09-21 19:47 | ok | 🟢 >= default: 0.09 vs 0.08 OK |
| Truncated | Sensitivity | unc_sig6 | 6/4/6 | 0/0/20 | Δχ² 0.07/0.07@30y | Δχ² 0.07/0.07@30y | 09-21 20:22 | ok | 🟢 <= default: 0.07 vs 0.08 OK |
| Truncated | DayNight | unc_bkg0 | 6/13/6 | 0/20/60 | 0.86σ@30y | 0.70σ@20y | 09-19 00:14 | ok | 🟢 == default: 0.86 vs 0.86 OK |
| Truncated | HEP | unc_bkg0 | 5/4/14 | 0/0/40 | 2.76σ@30y | 2.39σ@20y | 09-19 00:18 | ok | 🟢 == default: 2.76 vs 2.76 OK |
| Truncated | DayNight | unc_bkg4 | 6/13/6 | 0/20/60 | 0.86σ@30y | 0.70σ@20y | 09-19 00:24 | ok | 🟢 == default: 0.86 vs 0.86 OK |
| Truncated | HEP | unc_bkg4 | 5/4/14 | 0/0/40 | 2.76σ@30y | 2.39σ@20y | 09-19 00:29 | ok | 🟢 == default: 2.76 vs 2.76 OK |
| Truncated | DayNight | unc_bkg6 | 6/13/6 | 0/20/60 | 0.86σ@30y | 0.70σ@20y | 09-19 00:33 | ok | 🟢 == default: 0.86 vs 0.86 OK |
| Truncated | HEP | unc_bkg6 | 5/4/14 | 0/0/40 | 2.76σ@30y | 2.39σ@20y | 09-19 00:38 | ok | 🟢 == default: 2.76 vs 2.76 OK |
| Truncated | Sensitivity | nuisance_nominal | 6/4/6 | 0/0/20 | Δχ² 0.09/0.09@30y | Δχ² 0.09/0.09@30y | 09-21 20:23 | ok | 🟢 >= nuisance_sin13: 0.09 vs 0.09 OK |
| Truncated | Sensitivity | nuisance_sin13 | 6/4/6 | 0/0/20 | Δχ² 0.09/0.09@30y | Δχ² 0.09/0.09@30y | 09-21 20:39 | ok | 🟢 >= default: 0.09 vs 0.08 OK |
| Truncated | Sensitivity | nuisance_escale | 6/4/6 | 0/0/20 | Δχ² 0.08/0.08@30y | Δχ² 0.08/0.08@30y | 09-21 20:40 | ok | 🟢 >= default: 0.08 vs 0.08 OK |
| Truncated | DayNight | energy_spk | 7/4/15 | 0/20/60 | 2.18σ@30y | 1.78σ@20y | 09-21 22:54 | ok | ⚪ vs default: 2.18 vs 0.86 |
| Truncated | HEP | energy_spk | 7/4/20 | 0/0/40 | 31.19σ@30y | 27.15σ@20y | 09-21 22:59 | ok | ⚪ vs default: 31.19 vs 2.76 |
| Truncated | Sensitivity | energy_spk | 6/7/5 | 0/0/20 | Δχ² 0.08/0.08@30y | Δχ² 0.08/0.08@30y | 09-21 23:46 | ok | ⚪ vs default: 0.08 vs 0.08 |
| Truncated | DayNight | energy_maink | 6/19/14 | 0/20/60 | 1.53σ@30y | 1.25σ@20y | 09-22 00:43 | ok | ⚪ vs default: 1.53 vs 0.86 |
| Truncated | HEP | energy_maink | 1/4/19 | 0/0/40 | 12.72σ@30y | 11.03σ@20y | 09-22 00:47 | ok | ⚪ vs default: 12.72 vs 2.76 |
| Truncated | Sensitivity | energy_maink | 6/19/14 | 0/0/20 | Δχ² 0.42/0.41@30y | Δχ² 0.42/0.41@30y | 09-22 01:32 | ok | ⚪ vs default: 0.42 vs 0.08 |
| Truncated | DayNight | charge_Q0 | 6/13/6 | 0/20/20 | 0.69σ@30y | 0.56σ@20y | 09-19 16:44 | ok | ⚪ vs default: 0.69 vs 0.86 |
| Truncated | HEP | charge_Q0 | 5/4/14 | 0/120/40 | 1.88σ@30y | 1.64σ@20y | 09-19 16:48 | ok | ⚪ vs default: 1.88 vs 2.76 |
| Truncated | Sensitivity | charge_Q0 | 6/4/6 | 120/40/40 | Δχ² 0.05/0.04@30y | Δχ² 0.05/0.04@30y | 09-19 16:58 | ok | ⚪ vs default: 0.05 vs 0.08 |
| Truncated | DayNight | charge_Q50 | 6/13/6 | 0/20/20 | 0.68σ@30y | 0.56σ@20y | 09-19 11:31 | ok | ⚪ vs charge_Q0: 0.68 vs 0.69 |
| Truncated | HEP | charge_Q50 | 5/4/14 | 0/120/40 | 2.15σ@30y | 1.88σ@20y | 09-18 23:49 | ok | ⚪ vs charge_Q0: 2.15 vs 1.88 |
| Truncated | Sensitivity | charge_Q50 | 6/4/6 | 120/40/40 | Δχ² 0.40/0.39@30y | Δχ² 0.40/0.39@30y | 09-18 23:59 | ok | ⚪ vs charge_Q0: 0.40 vs 0.05 |
| Truncated | DayNight | charge_Q100 | 6/13/6 | 0/20/20 | 0.67σ@30y | 0.55σ@20y | 09-19 16:37 | ok | ⚪ vs charge_Q50: 0.67 vs 0.68 |
| Truncated | HEP | charge_Q100 | 5/4/14 | 0/120/40 | 2.20σ@30y | 1.92σ@20y | 09-19 11:28 | ok | ⚪ vs charge_Q50: 2.20 vs 2.15 |
| Truncated | Sensitivity | charge_Q100 | 6/4/6 | 120/40/40 | Δχ² 0.42/0.41@30y | Δχ² 0.42/0.41@30y | 09-19 16:47 | ok | ⚪ vs charge_Q50: 0.42 vs 0.40 |
| Truncated | DayNight | charge_Q500 | 6/4/13 | 0/20/20 | 0.49σ@30y | 0.40σ@20y | 09-18 23:54 | ok | ⚪ vs charge_Q100: 0.49 vs 0.67 |
| Truncated | HEP | charge_Q500 | 5/4/14 | 0/120/40 | 2.19σ@30y | 1.90σ@20y | 09-18 23:58 | ok | ⚪ vs charge_Q100: 2.19 vs 2.20 |
| Truncated | Sensitivity | charge_Q500 | 6/4/6 | 120/40/40 | Δχ² 0.76/0.74@30y | Δχ² 0.76/0.74@30y | 09-19 00:09 | ok | ⚪ vs charge_Q100: 0.76 vs 0.42 |
| Nominal | DayNight | bkgmodel_nominal | 6/13/6 | 140/100/0 | 0.86σ@30y | 0.70σ@20y | 09-18 20:51 | ok | 🟢 <= Truncated default: 0.86 vs 0.86 OK |
| Nominal | HEP | bkgmodel_nominal | 5/4/14 | 0/0/40 | 2.75σ@30y | 2.39σ@20y | 09-18 20:55 | ok | 🟢 <= Truncated default: 2.75 vs 2.76 OK |
| Nominal | Sensitivity | bkgmodel_nominal | 6/4/6 | 0/0/20 | Δχ² 0.08/0.08@30y | Δχ² 0.08/0.08@30y | 09-18 21:05 | ok | 🟢 <= Truncated default: 0.08 vs 0.08 OK |
| Reduced | DayNight | bkgmodel_reduced | 6/13/6 | 0/20/60 | 1.93σ@30y | 1.58σ@20y | 09-18 21:47 | ok | 🟢 >= Truncated default: 1.93 vs 0.86 OK |
| Reduced | HEP | bkgmodel_reduced | 5/4/14 | 0/0/40 | 2.94σ@30y | 2.55σ@20y | 09-18 21:51 | ok | 🟢 >= Truncated default: 2.94 vs 2.76 OK |
| Reduced | Sensitivity | bkgmodel_reduced | 6/4/6 | 0/0/20 | Δχ² 0.42/0.41@30y | Δχ² 0.42/0.41@30y | 09-18 22:02 | ok | 🟢 >= Truncated default: 0.42 vs 0.08 OK |
| Truncated | DayNight | oscpoint_solar | 6/13/6 | 0/20/60 | 0.86σ@30y | 0.70σ@20y | 09-19 01:09 | ok | 🟢 == default: 0.86 vs 0.86 OK |
| Truncated | HEP | oscpoint_solar | 5/4/14 | 0/0/40 | 2.76σ@30y | 2.39σ@20y | 09-19 01:17 | ok | 🟢 == default: 2.76 vs 2.76 OK |
| Truncated | DayNight | oscpoint_reactor | 6/13/6 | 0/20/60 | 0.66σ@30y | 0.54σ@20y | 09-22 00:13 | ok | 🟢 <= default: 0.66 vs 0.86 OK |
| Truncated | HEP | oscpoint_reactor | 5/4/14 | 0/0/40 | 2.74σ@30y | 2.38σ@20y | 09-22 00:16 | ok | 🟢 == default: 2.74 vs 2.76 OK |
| Truncated | DayNight | fiduc_truth | 6/13/6 | 20/0/400 | 0.86σ@30y | 0.70σ@20y | 09-20 13:44 | ok | 🟢 >= default: 0.86 vs 0.86 OK |
| Truncated | HEP | fiduc_truth | 5/4/14 | 0/0/40 | 2.75σ@30y | 2.39σ@20y | 09-20 13:48 | ok | 🟢 >= default: 2.75 vs 2.76 OK |
| Truncated | Sensitivity | fiduc_truth | 4/4/5 | 100/80/60 | Δχ² 0.87/0.86@30y | Δχ² 0.87/0.86@30y | 09-20 14:38 | ok | 🟢 >= default: 0.87 vs 0.08 OK |
| Truncated | DayNight | fiduc_truth_refvol | 6/13/6 | 0/20/60 | 0.86σ@30y | 0.70σ@20y | 09-20 15:18 | ok | ⚪ vs fiduc_truth: 0.86 vs 0.86 |
| Truncated | HEP | fiduc_truth_refvol | 5/4/14 | 0/0/40 | 2.75σ@30y | 2.39σ@20y | 09-20 15:22 | ok | ⚪ vs fiduc_truth: 2.75 vs 2.75 |
| Truncated | Sensitivity | fiduc_truth_refvol | 2/12/6 | 0/0/20 | Δχ² 0.76/0.74@30y | Δχ² 0.76/0.74@30y | 09-20 16:15 | ok | ⚪ vs fiduc_truth: 0.76 vs 0.87 |
| Truncated | DayNight | bkg_gamma_cluster | 6/13/6 | 60/0/20 | 0.76σ@30y | 0.62σ@20y | 09-22 00:47 | ok | ⚪ vs default: 0.76 vs 0.86 |
| Truncated | HEP | bkg_gamma_cluster | 5/4/14 | 0/0/60 | 2.46σ@30y | 2.14σ@20y | 09-22 00:50 | ok | ⚪ vs default: 2.46 vs 2.76 |
| Truncated | Sensitivity | bkg_gamma_cluster | 6/4/6 | 140/0/20 | Δχ² 0.05/0.05@30y | Δχ² 0.05/0.05@30y | 09-22 00:59 | ok | ⚪ vs default: 0.05 vs 0.08 |
| Truncated | DayNight | bkg_gamma_total | 5/18/4 | 0/60/40 | 0.53σ@30y | 0.43σ@20y | 09-21 21:54 | ok | ⚪ vs default: 0.53 vs 0.86 |
| Truncated | HEP | bkg_gamma_total | 5/4/14 | 60/120/20 | 0.04σ@30y | 0.03σ@20y | 09-21 21:58 | ok | ⚪ vs default: 0.04 vs 2.76 |
| Truncated | Sensitivity | bkg_gamma_total | 6/4/6 | 0/0/0 | Δχ² 0.03/0.03@30y | Δχ² 0.03/0.03@30y | 09-21 22:07 | ok | ⚪ vs default: 0.03 vs 0.08 |
| Truncated | DayNight | membrane_veto_off | 6/13/6 | 0/20/60 | 0.88σ@30y | 0.72σ@20y | 09-20 18:14 | ok | 🟢 >= default: 0.88 vs 0.86 OK |
| Truncated | HEP | membrane_veto_off | 5/4/14 | 0/0/40 | 2.77σ@30y | 2.40σ@20y | 09-20 18:19 | ok | 🟢 >= default: 2.77 vs 2.76 OK |
| Truncated | Sensitivity | membrane_veto_off | 6/4/6 | 0/0/20 | Δχ² 0.07/0.07@30y | Δχ² 0.07/0.07@30y | 09-20 18:30 | ok | ⚪ vs default: 0.07 vs 0.08 |
| Truncated | Sensitivity | legacy_fit | 6/4/6 | 0/0/20 | Δχ² 0.22/0.20@30y | Δχ² 0.22/0.20@30y | 09-19 03:32 | ok | ⚪ vs default: 0.22 vs 0.08 |

## vd_1x8x14_3view_30deg_shielded

| folder | analysis | study | cut | fiducial | value | at_eval | record | status | trend |
|---|---|---|---|---|---|---|---|---|---|
| Truncated | DayNight | default | 6/13/7 | 20/100/20 | 1.91σ@30y | 1.56σ@20y | 09-22 03:00 | ok | - |
| Truncated | HEP | default | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.19σ@20y | 09-22 03:59 | ok | - |
| Truncated | Sensitivity | default | 6/4/6 | 0/0/20 | Δχ² 0.40/0.39@30y | Δχ² 0.40/0.39@30y | 09-18 20:24 | ok | - |
| Nominal | DayNight | default | 6/13/7 | 20/40/60 | 1.85σ@30y | 1.51σ@20y | 09-22 03:02 | ok | 🟢 <= Truncated default: 1.85 vs 1.91 OK |
| Nominal | HEP | default | 7/4/16 | 0/0/20 | 3.65σ@30y | 3.17σ@20y | 09-22 04:00 | ok | 🟢 <= Truncated default: 3.65 vs 3.66 OK |
| Nominal | Sensitivity | default | 6/4/7 | 0/0/20 | Δχ² 0.46/0.45@30y | Δχ² 0.46/0.45@30y | 09-22 00:43 | ok | **🔴 <= Truncated default: 0.46 vs 0.40 UNEXPECTED (fresh)** |
| Reduced | DayNight | default | 6/4/6 | 20/100/20 | 2.93σ@30y | 2.40σ@20y | 09-22 03:03 | ok | 🟢 >= Truncated default: 2.93 vs 1.91 OK |
| Reduced | HEP | default | 7/4/15 | 0/0/20 | 4.18σ@30y | 3.64σ@20y | 09-22 04:04 | ok | 🟢 >= Truncated default: 4.18 vs 3.66 OK |
| Reduced | Sensitivity | default | 8/10/10 | 0/0/20 | Δχ² 0.49/0.48@30y | Δχ² 0.49/0.48@30y | 09-22 00:14 | ok | 🟢 >= Truncated default: 0.49 vs 0.40 OK |
| Truncated | HEP | unc_sig20 | 7/4/15 | 0/0/20 | 3.96σ@30y | 3.44σ@20y | 09-21 21:38 | ok | 🟢 >= default: 3.96 vs 3.66 OK |
| Truncated | HEP | unc_sig40 | 7/4/15 | 0/0/20 | 3.35σ@30y | 2.91σ@20y | 09-19 00:46 | ok | 🟢 <= default: 3.35 vs 3.66 OK |
| Truncated | Sensitivity | unc_sig0 | 6/4/6 | 0/0/20 | Δχ² 0.66/0.65@30y | Δχ² 0.66/0.65@30y | 09-21 20:43 | ok | 🟢 >= unc_sig2: 0.66 vs 0.54 OK |
| Truncated | Sensitivity | unc_sig2 | 6/4/6 | 0/0/20 | Δχ² 0.54/0.53@30y | Δχ² 0.54/0.53@30y | 09-21 20:44 | ok | 🟢 >= default: 0.54 vs 0.40 OK |
| Truncated | Sensitivity | unc_sig6 | 6/4/6 | 0/0/20 | Δχ² 0.33/0.32@30y | Δχ² 0.33/0.32@30y | 09-21 20:47 | ok | 🟢 <= default: 0.33 vs 0.40 OK |
| Truncated | DayNight | unc_bkg0 | 6/13/7 | 20/100/20 | 1.91σ@30y | 1.56σ@20y | 09-21 19:01 | ok | 🟢 == default: 1.91 vs 1.91 OK |
| Truncated | HEP | unc_bkg0 | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.19σ@20y | 09-19 00:13 | ok | 🟢 == default: 3.66 vs 3.66 OK |
| Truncated | DayNight | unc_bkg4 | 6/13/7 | 20/100/20 | 1.91σ@30y | 1.56σ@20y | 09-21 19:47 | ok | 🟢 == default: 1.91 vs 1.91 OK |
| Truncated | HEP | unc_bkg4 | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.19σ@20y | 09-19 00:24 | ok | 🟢 == default: 3.66 vs 3.66 OK |
| Truncated | DayNight | unc_bkg6 | 6/13/7 | 20/100/20 | 1.91σ@30y | 1.56σ@20y | 09-21 21:34 | ok | 🟢 == default: 1.91 vs 1.91 OK |
| Truncated | HEP | unc_bkg6 | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.19σ@20y | 09-19 00:28 | ok | 🟢 == default: 3.66 vs 3.66 OK |
| Truncated | Sensitivity | nuisance_nominal | 6/4/6 | 0/0/20 | Δχ² 0.42/0.41@30y | Δχ² 0.42/0.41@30y | 09-19 11:27 | ok | 🟢 >= nuisance_sin13: 0.42 vs 0.42 OK |
| Truncated | Sensitivity | nuisance_sin13 | 6/4/6 | 0/0/20 | Δχ² 0.42/0.41@30y | Δχ² 0.42/0.41@30y | 09-19 01:21 | ok | 🟢 >= default: 0.42 vs 0.40 OK |
| Truncated | Sensitivity | nuisance_escale | 6/4/6 | 0/0/20 | Δχ² 0.40/0.39@30y | Δχ² 0.40/0.39@30y | 09-19 01:05 | ok | 🟢 >= default: 0.40 vs 0.40 OK |
| Truncated | DayNight | energy_spk | 5/15/4 | 20/100/20 | 1.72σ@30y | 1.40σ@20y | 09-21 12:00 | ok | ⚪ vs default: 1.72 vs 1.91 |
| Truncated | HEP | energy_spk | 7/4/20 | 0/0/20 | 31.31σ@30y | 27.26σ@20y | 09-21 12:04 | ok | ⚪ vs default: 31.31 vs 3.66 |
| Truncated | Sensitivity | energy_spk | 6/7/5 | 0/0/20 | Δχ² 0.09/0.10@30y | Δχ² 0.09/0.10@30y | 09-21 19:37 | ok | ⚪ vs default: 0.09 vs 0.40 |
| Truncated | DayNight | energy_maink | 6/4/11 | 20/100/20 | 2.40σ@30y | 1.96σ@20y | 09-21 20:57 | ok | ⚪ vs default: 2.40 vs 1.91 |
| Truncated | HEP | energy_maink | 1/4/19 | 0/0/20 | 12.76σ@30y | 11.07σ@20y | 09-21 21:00 | ok | ⚪ vs default: 12.76 vs 3.66 |
| Truncated | Sensitivity | energy_maink | 6/4/11 | 0/0/20 | Δχ² 0.90/0.87@30y | Δχ² 0.90/0.87@30y | 09-21 21:54 | ok | ⚪ vs default: 0.90 vs 0.40 |
| Truncated | DayNight | charge_Q0 | 6/13/7 | 40/160/0 | 1.87σ@30y | 1.53σ@20y | 09-19 16:42 | ok | ⚪ vs default: 1.87 vs 1.91 |
| Truncated | HEP | charge_Q0 | 7/4/15 | 0/0/80 | 1.76σ@30y | 1.53σ@20y | 09-19 16:47 | ok | ⚪ vs default: 1.76 vs 3.66 |
| Truncated | Sensitivity | charge_Q0 | 6/4/6 | 60/20/0 | Δχ² 0.36/0.35@30y | Δχ² 0.36/0.35@30y | 09-19 16:58 | ok | ⚪ vs default: 0.36 vs 0.40 |
| Truncated | DayNight | charge_Q50 | 6/13/7 | 40/160/0 | 1.73σ@30y | 1.41σ@20y | 09-22 00:31 | ok | ⚪ vs charge_Q0: 1.73 vs 1.87 |
| Truncated | HEP | charge_Q50 | 7/4/15 | 0/0/80 | 2.84σ@30y | 2.48σ@20y | 09-22 00:35 | ok | ⚪ vs charge_Q0: 2.84 vs 1.76 |
| Truncated | Sensitivity | charge_Q50 | 6/4/6 | 60/20/0 | Δχ² 0.99/0.95@30y | Δχ² 0.99/0.95@30y | 09-18 23:50 | ok | ⚪ vs charge_Q0: 0.99 vs 0.36 |
| Truncated | DayNight | charge_Q100 | 6/13/7 | 40/160/0 | 1.66σ@30y | 1.36σ@20y | 09-19 17:19 | ok | ⚪ vs charge_Q50: 1.66 vs 1.73 |
| Truncated | HEP | charge_Q100 | 7/4/15 | 0/0/80 | 2.07σ@30y | 1.80σ@20y | 09-19 17:23 | ok | ⚪ vs charge_Q50: 2.07 vs 2.84 |
| Truncated | Sensitivity | charge_Q100 | 6/4/6 | 60/20/0 | Δχ² 1.01/0.98@30y | Δχ² 1.01/0.98@30y | 09-19 17:38 | ok | ⚪ vs charge_Q50: 1.01 vs 0.99 |
| Truncated | DayNight | charge_Q500 | 5/4/7 | 40/160/0 | 1.66σ@30y | 1.35σ@20y | 09-18 23:50 | ok | ⚪ vs charge_Q100: 1.66 vs 1.66 |
| Truncated | HEP | charge_Q500 | 6/4/14 | 0/0/80 | 3.06σ@30y | 2.66σ@20y | 09-21 22:07 | ok | ⚪ vs charge_Q100: 3.06 vs 2.07 |
| Truncated | Sensitivity | charge_Q500 | 6/4/6 | 60/20/0 | Δχ² 1.14/1.11@30y | Δχ² 1.14/1.11@30y | 09-19 00:00 | ok | ⚪ vs charge_Q100: 1.14 vs 1.01 |
| Truncated | DayNight | oscpoint_solar | 6/13/7 | 20/100/20 | 1.91σ@30y | 1.56σ@20y | 09-19 03:24 | ok | 🟢 == default: 1.91 vs 1.91 OK |
| Truncated | HEP | oscpoint_solar | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.19σ@20y | 09-19 03:32 | ok | 🟢 == default: 3.66 vs 3.66 OK |
| Truncated | DayNight | oscpoint_reactor | 6/13/7 | 20/100/20 | 1.46σ@30y | 1.19σ@20y | 09-22 00:33 | ok | 🟢 <= default: 1.46 vs 1.91 OK |
| Truncated | HEP | oscpoint_reactor | 7/4/15 | 0/0/20 | 3.65σ@30y | 3.18σ@20y | 09-22 00:37 | ok | 🟢 == default: 3.65 vs 3.66 OK |
| Truncated | DayNight | fiduc_truth | 6/4/6 | 100/20/480 | 1.94σ@30y | 1.59σ@20y | 09-20 13:43 | ok | 🟢 >= default: 1.94 vs 1.91 OK |
| Truncated | HEP | fiduc_truth | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.18σ@20y | 09-20 13:47 | ok | 🟢 >= default: 3.66 vs 3.66 OK |
| Truncated | Sensitivity | fiduc_truth | 1/4/5 | 100/80/140 | Δχ² 0.91/0.90@30y | Δχ² 0.91/0.90@30y | 09-20 14:37 | ok | 🟢 >= default: 0.91 vs 0.40 OK |
| Truncated | DayNight | fiduc_truth_refvol | 6/13/7 | 20/100/20 | 1.90σ@30y | 1.55σ@20y | 09-20 15:17 | ok | ⚪ vs fiduc_truth: 1.90 vs 1.94 |
| Truncated | HEP | fiduc_truth_refvol | 7/4/15 | 0/0/20 | 3.66σ@30y | 3.18σ@20y | 09-20 15:21 | ok | ⚪ vs fiduc_truth: 3.66 vs 3.66 |
| Truncated | Sensitivity | fiduc_truth_refvol | 4/18/7 | 0/0/20 | Δχ² 1.04/1.01@30y | Δχ² 1.04/1.01@30y | 09-20 16:10 | ok | ⚪ vs fiduc_truth: 1.04 vs 0.91 |
| Truncated | DayNight | bkg_gamma_cluster | 6/13/7 | 100/0/20 | 2.09σ@30y | 1.71σ@20y | 09-22 01:20 | ok | ⚪ vs default: 2.09 vs 1.91 |
| Truncated | HEP | bkg_gamma_cluster | 5/4/5 | 20/40/20 | 3.82σ@30y | 3.32σ@20y | 09-22 01:24 | ok | ⚪ vs default: 3.82 vs 3.66 |
| Truncated | Sensitivity | bkg_gamma_cluster | 6/4/6 | 0/0/20 | Δχ² 0.39/0.38@30y | Δχ² 0.39/0.38@30y | 09-22 01:32 | ok | ⚪ vs default: 0.39 vs 0.40 |
| Truncated | DayNight | bkg_gamma_total | 6/13/7 | 0/40/0 | 2.02σ@30y | 1.65σ@20y | 09-21 21:53 | ok | ⚪ vs default: 2.02 vs 1.91 |
| Truncated | HEP | bkg_gamma_total | 6/4/5 | 20/120/40 | 3.60σ@30y | 3.13σ@20y | 09-21 21:57 | ok | ⚪ vs default: 3.60 vs 3.66 |
| Truncated | Sensitivity | bkg_gamma_total | 6/4/6 | 60/80/0 | Δχ² 0.26/0.25@30y | Δχ² 0.26/0.25@30y | 09-21 22:06 | ok | ⚪ vs default: 0.26 vs 0.40 |
| Truncated | DayNight | membrane_veto_off | 6/13/7 | 20/100/20 | 1.94σ@30y | 1.59σ@20y | 09-20 18:13 | ok | 🟢 >= default: 1.94 vs 1.91 OK |
| Truncated | HEP | membrane_veto_off | 7/4/15 | 0/0/20 | 3.79σ@30y | 3.30σ@20y | 09-20 18:18 | ok | 🟢 >= default: 3.79 vs 3.66 OK |
| Truncated | Sensitivity | membrane_veto_off | 6/4/6 | 0/0/20 | Δχ² 0.34/0.33@30y | Δχ² 0.34/0.33@30y | 09-20 18:29 | ok | ⚪ vs default: 0.34 vs 0.40 |
| Truncated | Sensitivity | legacy_fit | 6/4/6 | 0/0/20 | Δχ² 1.67/2.15@30y | Δχ² 1.67/2.15@30y | 09-19 04:49 | ok | ⚪ vs default: 1.67 vs 0.40 |
