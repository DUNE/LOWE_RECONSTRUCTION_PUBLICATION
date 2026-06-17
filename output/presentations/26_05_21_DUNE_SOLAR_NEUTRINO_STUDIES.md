---
marp: true
math: mathjax
paginate: true
theme: dune
---

<!-- _class: titlepage -->
# Solar Neutrino Significance in DUNE

Combined (FD-HD & FD-VD complete simulation) results for **Day-Night Asymmetry**, **HEP Discovery**, and **Oscillation Parameter Sensitivity**.

<!-- markdownlint-disable MD033 -->
<div class="bottom-note">
Sergio Manthey Corchado - CIEMAT - DUNE Collaboration Meeting - 21/05/2026
</div>
<!-- markdownlint-enable MD033 -->

---

## Overview

**DUNE** can address several key questions in solar neutrino physics. To do so, we need to evaluate the following:

- **Day-Night:** can we resolve small differences in solar neutrino rates?
- **HEP**: do we have the resolution to discover the high-energy tail of the solar neutrino spectrum?
- **Oscillation Parameter Sensitivity**: do we have the precision to separate current best-fit values (solar vs. reactor) of $\Delta m^2_{21}$?

**Phase I results** are based on the latest available information on FD backgrounds and reconstruction performance.
**Phase II projections** assume **2 additional FD HD / VD Phase I modules** with a **5-year offset**, emphasizing the impact of increased exposure for each case.

---

### Theoretical Assumptions

<!-- markdownlint-disable MD033 -->
Day-Night asymmetry (computed using the **[Prob3++](https://github.com/CIEMAT-Neutrino/Prob3plusplus) flavor oscillation software**) integrates to $-4.77\%$. Solar neutrino fluxes (HEP) are taken from the latest **[B16-GS98](https://iopscience.iop.org/article/10.1088/1742-6596/1056/1/012058/meta) solar model**. Best-fit values for the oscillation parameters are from **[NuFIT](http://www.nu-fit.org/?q=node/256) 5.2 (2022)**.

<div class="three-col">
  <div>
  <img src="../plots/daynight_asymmetry_energy_probability_label_weighted_false_line_operation.png" alt="Solar neutrino spectrum with fluxes and uncertainties">
  </div>
  <div>
  <img src="../plots/solar_neutrino_spectrum_energy_flux_source_logx_logy_scan.png" alt="Solar neutrino spectrum with fluxes and uncertainties">
  </div>
  <div>

  | Parameter | Value |
  | :---: | :---: |
  | $\sin^2\theta_{13}$ | $0.021$ |
  | $\sin^2\theta_{12}$ | $0.303$ |
  | $\Delta m^2_{21}$ (eV$^2$) | $7.4 \times 10^{-5}$ |
  | $\Delta m^2_{21}$ (eV$^2$) | *$6.0 \times 10^{-5}$ |

  </div>
</div>

<div class="bottom-note">
*Results use solar best-fit value, which is in tension with reactor measurements. The impact on oscillation parameter sensitivity projections is the subject of current studies.
</div>

---

### Data MC Production

Using a custom MC production ($\sim 150$ TB **[@PIC](https://www.pic.es/)**) based on LArSoft v09_91_04 (same as latest LowE official production). The MC includes:

- **CC Neutrino events** generated with MARLEY in the $4-30$ MeV flat range.
- **Cavern gammas (neutrons)** generated in a flat energy range $4-14$ MeV ($0-10$ MeV), propagated through the LAr buffer.
- **Radiological backgrounds** ($^{39}$Ar, $^{42}$Ar, $^{222}$Rn...) propagated through the LAr and reconstructed with the nominal production weights.

Events are propagated within the full context of the background model (v.3 radiological, component-induced and external backgrounds) and passed through the **LowE Reconstruction Workflow** designed to maximize the signal efficiency with custom [TPC Clustering](https://github.com/DUNE/dunereco/blob/develop/dunereco/LowEUtils/LowECluster.h), [PDS Flash-Finding](https://github.com/DUNE/duneopdet/blob/develop/duneopdet/LowEPDSUtils/SolarOpFlash_module.cc) and [TPC-PDS Matching](https://github.com/DUNE/dunereco/blob/develop/dunereco/LowEUtils/LowEUtils.h) algorithms.

<div class="bottom-note">
The current MC production does not include electron / alpha event candidates, which are expected to be subdominant in the energy range of interest for these analyses.
</div>

---

### Analysis Workflow: **1. Day-Night**

1. Build signal and **background** energy spectra. **New** [implemented smoothing](#histogram-smoothing).
2. The analyses are performed by applying a **fiducial cut from each detector boundary**.
3. Iterate over a set of **analysis parameters**: number of TPC hits `nhits`, PDS optical hits `ophits`, adjacent clusters `adjcls`.
4. Evaluate **Gaussian significance** curves for **all analysis cuts**.
5. Select the **optimal cut configuration** for each module and combine the results to produce the final significance curve.

---

### Analysis Workflow: **2. HEP**

1. Build signal and **background** energy spectra. **New** [implemented smoothing](#histogram-smoothing).
2. The analyses are performed by applying a **fiducial cut from each detector boundary**.
3. Iterate over a set of **analysis parameters**: number of TPC hits `nhits`, PDS optical hits `ophits`, adjacent clusters `adjcls`.
4. Evaluate **ProfileLikelihood significance** curves for **all analysis cuts**.
    Background bins with fewer than 1 raw MC event are masked using the [Barlow-Beeston lite criterion](https://www.sciencedirect.com/science/article/pii/009350659390005W) (as implemented in [ROOT HistFactory](https://root.cern.ch/doc/master/classRooStats_1_1HistFactory_1_1Measurement.html)) to suppress LLR divergence from empty bins.

5. Select the **optimal cut configuration** for each module and combine the results to produce the final significance curve.

---

### Analysis Workflow: **3. Oscillation Parameter Sensitivity**

Oscillation Parameter Sensitivity analysis varies slightly:

1. Build signal and **background** energy spectra. **New** [implemented smoothing](#histogram-smoothing).
2. The analyses are performed by applying a **fiducial cut from each detector boundary**.
3. For the selected analysis parameters, **convolve** the signal spectrum with the **oscillation probability matrix** (azimuth vs true $\nu_e$ energy) for each point in $\Delta m^2_{21}$ vs $\sin^2\theta_{12}$, add the background and build a set of **2D histogram hypothesis**.
4. Evaluate the $\chi^2$ from a **log-likelihood ratio test** comparing the convolved signal + background to the reference signal + background hypothesis.
5. **Scan over oscillation parameters** to produce sensitivity contours.
6. Compare the sensitivity contours to the current best-fit values from solar and reactor experiments to evaluate the separation power of DUNE.

---

### Analysis Workflow: Common Assumptions

- Both **Gamma & Neutron backgrounds are forced to have at least 10 raw MC events** in the significance computation. This is a conservative approach that avoids rejecting these most important backgrounds completely due to the lack of MC statistics.
- All analyses are performed on **reconstructed energy spectra** with uncertainties: $\pm 4\%$ for $^8B$, $\pm 30\%$ for HEP and $\pm 2\%$ for background.
- **New** fiducial optimization goal differs according to each analysis:

| Analysis | Signal | Backgrounds | Energy (MeV) | Metric |
| :---: | :---: | :---: | :---: | :---: |
| Day-Night | ⁸B + HEP | gamma, neutron, radiological | $6-18$ | Gaussian |
| HEP | HEP | ⁸B, gamma, neutron, radiological | $14-30$ | Asimov |
| Sensitivity | ⁸B + HEP | gamma, neutron, radiological | $10-30$ | Asimov |

---

## 1. Day-Night Asymmetry

---

### Day-Night: Signal and Background Definition

The signal is not "all solar events". It is the **difference between the night and day** solar spectra. Consequently, the background is the combination of day solar events and all other backgrounds:

$$
s_i = \mathcal{E} M \left(N_i^{\mathrm{night}} - N_i^{\mathrm{day}}\right) \quad \text{and} \quad
b_i = \mathcal{E} M \left(\frac{B_i}{2} + N_i^{\mathrm{day}}\right)
$$

where $\mathcal{E}$ is the exposure, $M$ is the detector mass, $N_i^{\mathrm{night}}$ is the expected night solar spectrum in bin $i$, $N_i^{\mathrm{day}}$ is the expected day solar spectrum in bin $i$, and $B_i$ is the total background in bin $i$.

---

### Day-Night: Assessed Uncertainties

Evaluate uncertainty bands by **varying the solar model normalization ±13%** (corresponding to predictions of Earth's density profile by [@LopezMoreno](https://indico.fnal.gov/event/68524/contributions/310932/attachments/185800/255867/low%20energy%20meeting%205%20march%202025.pdf)).

$$
\alpha_i = \frac{s_i}{\sqrt{b_i + \sigma_{b,i}^2 + \sigma_{s,i}^2}}
$$

where:

- Explicit signal uncertainty $\sigma_{s,i}$ set to 0.
- Explicit background uncertainty term used in the error curve:

$$
\sigma_{b,i} = \sqrt{\mathcal{E} M \frac{B_i}{2} + \left(0.02\,\mathcal{E} M \frac{B_i}{2}\right)^2}
$$

---

### Day-Night: Single HD Central Module

Showing data as exposure in `years`. Only using the HD Central module, we expect to reach **3σ (5σ)** significance in **5 (15) years** of DUNE data.

<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <img src="../plots/daynight_counts_hd_1x2x6_centralapa_marley_energy_counts_component_logy_line_operation.png" alt="Latest day-night significance plot">
  <img src="../plots/daynight_exposure_hd_1x2x6_centralapa_marley_exposure_significance_spectrumtype_scan.png" alt="Latest day-night exposure plot">
</div>

---

### Day-Night: Combined Results for Phase I

Results predict <strong>3σ (5σ)</strong> significance in <strong>4 (11) years</strong> of DUNE data (1 HD Module + 1 Shielded VD Module).
<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <div>
  <img src="../plots/daynight_exposure_marley_exposure_significance_error_spectrumtype_smoothed_comparison.png" alt="Latest day-night exposure plot">
  </div>
  <div>
    <ul>
      <li>Day-Night asymmetry significance is dominated by the HD Central module.</li>
      <li>The addition of the other modules only provides a modest increase in significance.</li>
      <li>Current shielding proposal for the VD Bottom module is not enough.</li>
    </ul>
  </div>
</div>

---

### Day-Night: Projections for Phase II

Combined HD Phase II reaches 5σ</strong> significance in <strong>7 years</strong>. Combined <strong>VD Phase II</strong> projection is <strong>less capable than a single HD module (Phase I)</strong>.

<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <div>
    <img src="../plots/daynight_exposure_hd_1x2x6_lateralapa_marley_exposure_significance_error_spectrumtype_smoothed_comparison.png" alt="Latest day-night exposure plot">
  </div>
  <div>
    <img src="../plots/daynight_exposure_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_marley_exposure_significance_error_spectrumtype_smoothed_comparison.png" alt="Projected day-night exposure plot">
  </div>
</div>

<div class="bottom-note">
Projecting the results to <strong>Phase II exposure</strong> with a <strong>5-year offset</strong>:
</div>

---

## 2. HEP Discovery

---

### HEP: Signal and Background Definition

The signal is the expected profile of **HEP events**:
$$
\begin{aligned}
&s_i = \mathcal{E} M H_i^{\mathrm{HEP}} \quad \text{and} \quad
b_i = \mathcal{E} M B_i\\
&n_i = s_i + b_i
\end{aligned}
$$

where:

- $H_i^{\mathrm{HEP}}$ is the expected HEP signal in bin `i`
- $B_i$ is the combined background in bin `i` (solar ⁸B + cavern backgrounds + radiological)

---

### HEP: ProfileLikelihood Model

<!--The profile-likelihood significance follows Cowan et al.\ \cite{Cowan2010}.
For the null hypothesis $\mu=0$ (no HEP signal), the test statistic is:
\begin{equation}
  q_0 = -2\ln\!\frac{\mathcal{L}(0,\,\bhat)}{\mathcal{L}(\hat{s}+b,\,1)},
  \label{eq:q0}
\end{equation}
Substituting $n_i = s_i+b_i$ into Eq.~\eqref{eq:q0}:
\begin{equation}
  q_0 = 2\sum_{i=1}^{K}
    \left[n_i\ln\!\frac{n_i}{\bhat b_i} - (n_i-\bhat b_i)\right]
    + \left(\frac{\bhat-1}{\srel}\right)^{\!2}.
  \label{eq:q0_expanded}
\end{equation} -->

- Significance is computed following [Cowan et al. 2010 (arXiv:1007.1727)](https://arxiv.org/abs/1007.1727) — the standard ATLAS/CMS formulation for discovery tests:
$$
q_0 = -2\ln\!\frac{\mathcal{L}(0,\,\hat{\beta})}{\mathcal{L}(\hat{s}+b,\,1)}
$$
- The background systematic is a **single global scale factor** $\beta$. This satisfies the closed-form quadratic (total counts $N = \sum n_i$, $B = \sum b_i$, $\sigma^2 = \sigma_\mathrm{rel}^2$) which can be analytically solved from $\hat{\beta}^2 + (B\sigma^2 - 1)\hat{\beta} - N\sigma^2 = 0$.
- The significance is then obtained as $Z = \sqrt{q_0}$:
$$
q_0 = 2\sum_{i=1}^{K}
\left[n_i\ln\!\frac{n_i}{\hat{\beta} b_i} - (n_i-\hat{\beta} b_i)\right]
+ \left(\frac{\hat{\beta}-1}{\sigma_\mathrm{rel}}\right)^{\!2}
$$

---

### HEP: Error Bands

The ±1σ bands on PL exposure curves use **signal normalization variation**: signal events are scaled by $(1 \pm \sigma_s)$ where $\sigma_s$ is the signal reconstruction efficiency systematic (**set to $30\%$**):
$$
s_i^{\pm} = s_i \cdot (1 \pm \sigma_s)
$$

The background is **never shifted**, so the profiled nuisance $\hat{\beta}$ is unaffected. Both bands collapse symmetrically when signal is negligible ($\pm\sigma_s \cdot 0 = 0$). This avoids the asymmetric-collapse artifact of background-shifting approaches, where $\hat{\beta}_{null}$ pull contributions drive the upper band non-zero independent of signal strength.

- **Upper band** ($\delta = +1$): more signal → higher $q_0$ → easier discovery.
- **Lower band** ($\delta = -1$): less signal → lower $q_0$. Both bands collapse symmetrically for configurations where signal is negligible.

---

### HEP: Single HD Central Module

HD Central is the only sub-module expected to reach a **5σ** discovery of the HEP component. Conservatory extimates predict a **5σ** discovery in **5 years** of DUNE HD Central.

<div class="two-col">
  <img src="../plots/hep_counts_hd_1x2x6_centralapa_marley_energy_counts_component_spectrumtype_smoothed_logy_stacked_line_operation.png" alt="Latest HEP exposure plot">
  <img src="../plots/hep_exposure_hd_1x2x6_centralapa_marley_exposure_significance_spectrumtype_variable_profilelikelihood_scan.png" alt="Latest HEP exposure plot">
</div>

<div class="bottom-note">
The jagged shape of the significance curve is a consequence of the conservative bin-counting criterion.
</div>

---

### HEP: Combined Results for Phase I

**HEP Discovery** results shows an even stronger HD Central dependence. Predicted **5σ** discovery of the HEP component in **4 years** of DUNE Phase I data.

<div class="two-col">
  <img src="../plots/hep_exposure_marley_exposure_significance_error_variable_profilelikelihood_spectrumtype_smoothed_comparison.png" alt="Latest HEP exposure plot">
  <div>
    <ul>
      <li>HEP discovery <strong>only achievable with the HD Central</strong> module.</li>
      <li>The addition of the other modules does not increase the significance.</li>
      <li>VD modules on their own do not reach 1σ significance.</li>
    </ul>
</div>

---

### HEP: Projection for Phase II

**Phase II FD modules arrive too late** (assuming 5-year offset) to increase HEP discovery, due to the slow accumulation of high-energy events and the conservative bin-counting criterion.

<div class="two-col">
  <div>
    <img src="../plots/hep_exposure_hd_1x2x6_lateralapa_marley_exposure_significance_error_variable_profilelikelihood_spectrumtype_smoothed_comparison.png" alt="Latest HEP exposure plot with HD Phase II projection">
  </div>
  <div>
    <img src="../plots/hep_exposure_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_marley_exposure_significance_error_variable_profilelikelihood_spectrumtype_smoothed_comparison.png" alt="Latest HEP exposure plot with VD Phase II projection">
  </div>
</div>

---

## 3. Oscillation Parameter Sensitivity

---

### Oscillation Parameter Sensitivity: Single HD Central Module

Showing the 1D projections of the 2D data maps (azimuth vs true $\nu_e$ energy) for the HD Central module.

<div class="two-col">
  <img src="../plots/sensitivity_counts_hd_1x2x6_centralapa_marley_energy_counts_component_logy_line_operation.png" alt="Latest oscillation parameter sensitivity plot with HD Phase I">
  <img src="../plots/sensitivity_solarenergy_hd_1x2x6_centralapa_values_dm2_label_solar_variable_sin12_contour.png" alt="Latest oscillation parameter sensitivity plot with HD Phase I">
</div>

---

### Oscillation Parameter Sensitivity: Combined Results

Phase I predicts **modest $2\sigma$ separation** between the current best-fit values of $\Delta m^2_{21}$ from solar and reactor experiments.

<div class="two-col">
  <img src="../plots/sensitivity_solarenergy_values_dm2_label_solar_variable_sin12_contour.png" alt="Latest oscillation parameter sensitivity plot with HD Phase I">
  <div>
    <ul>
      <li> Compared to other exerimental projections, DUNE's sensitivity is limited by the high statistics of the backgrounds and the non-ideal energy resolution in the low-energy range.</li>
      <li> Find the individual contribution of each module in the <a href="#oscillation-parameter-sensitivity-results">backup slides</a>.</li>
    </ul>
  </div>
</div>

<div class="bottom-note">
<strong>Oscillation parameter sensitivity</strong> is currently evaluated for <strong>Phase I (30 years exposure)</strong>.
<!-- The corresponding Phase II projection will be evaluated and included in the next presentation. -->
</div>

---

### DUNE Solar Neutrino Conclusions

Solar neutrino analyses Phase I results are **dominated by the HD Central module**. VD technology performs worse: charge readout closest to cavern background and opposite to PDS plane.  

- Combined **Day-Night Asymmetry** reaches **$5\sigma$ ($3\sigma$)** within the first **$11$ ($4$) years** of Phase I data, which could be improved by **$7$ years** with the addition of **2 FD-HD modules to Phase II**.
- The combined **HEP discovery significance ($5\sigma$)** should be reached within **4 years** of DUNE data thanks to FD-HD, independently of the addition of Phase II modules.
- The oscillation parameter sensitivity is able to **separate the current best-fit** $\Delta m^2_{21}$ from **reactor experiments** only at the **$2\sigma$** level with Phase I (30 years) of exposure.
- Current shielding design for VD does not get close to reach the significance reached with the HD Central. 

---

### Pending Tasks

- Needed **update shielded cavern background gamma spectrum** in LArSoft.
- Review the **impact** of absolute energy-scale uncertainties on the **high-energy tail of the cavern gamma** spectrum.
- Write, write, write... and write some more.

---

<!-- _class: sectionpage -->
## Backup

---

### Geometry Reference: HD

<div class="two-col">
  <div>
    <img src="../plots/HD_CENTRAL.png" alt="HD Central geometry reference">
  </div>
  <div>
    <img src="../plots/HD_LATERAL.png" alt="HD Lateral geometry reference">
  </div>

---

### Geometry Reference: VD

<div class="two-col">
  <div>
    <img src="../plots/VD_TOP.png" alt="VD Top geometry reference">
  </div>
  <div>
    <img src="../plots/VD_BOTTOM.png" alt="VD Bottom geometry reference">
  </div>

---

### Histogram Smoothing

Each component histogram $r_i^c$ is convolved with a one-dimensional Gaussian kernel before entering the significance computation:
$$
\tilde{r}_{i}^{c} = \sum_{j} G_\sigma(i-j)\, r_j^{c},
\qquad
G_\sigma(k) = \frac{1}{\sqrt{2\pi}\,\sigma}
\exp\!\left(-\frac{k^2}{2\sigma^2}\right),
$$
implemented via [scipy.ndimage.gaussian\_filter1d](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter1d.html) with **mode='nearest'**. The smoothing width $\sigma$ is determined by [Silverman's rule-of-thumb](https://en.wikipedia.org/wiki/Kernel_density_estimation#A_rule-of-thumb_bandwidth_estimator):
$$
\sigma_\mathrm{Silverman} = 1.06 \cdot \min\left(\mathrm{std}, \frac{\mathrm{IQR}}{1.34}\right) \cdot N^{-1/5}
$$
$$
\sigma_\mathrm{bins} = \frac{\sigma_\mathrm{Silverman}}{\text{bin\_width}}
$$

---

### Fiducialization: Day-Night

| Detector | x (cm) | y (cm) | z (cm) | Fiducial Volume (kT) |
| :---: | :---: | :---: | :---: | :---: |
| HD Central | $160$ (drift) | $120$ (top, bottom) | $120$ | $2.49$ |
| HD Lateral | $60$ (drift) | $120$ (top, bottom) | $100$ | $3.86$ |
| VD Top | $0$ (drift) | $0$ (left, right) | $240$ | $6.05$ |
| VD Bottom (**[Shielded](https://indico.fnal.gov/event/70212/contributions/319344/attachments/189449/261576/DUNE_EB_VDshieldingMeetingSD_26Jun2025_JR.pdf)**) | $0$ (drift) | $0$ (left, right) | $240$ | $6.05$ |

<!-- Añadir nota a pie de página sobre shielded config -->

<div class="bottom-note">
Contrary to y and z coordinates (evaluated with the TPC), the x coordinate is computed from TPC-PDS matching and is very affected by Flash-Matching efficiency.
</div>

---

### Best Cuts: DayNight

| Config | NHits | OpHits | AdjCl | Significance |
|---|---:|---:|---:|---:|
| HD Central | 3 | 12 | 3 | 8.094 |
| HD Lateral | 4 | 4 | 4 | 1.159 |
| VD Top | 7 | 14 | 4 | 1.356 |
| VD Bottom Shielded | 6 | 16 | 8 | 2.937 |

<div class="bottom-note">
The best cuts for the Day-Night analysis are optimized to maximize the Gaussian significance @ 30 years of exposure.
</div>

---

### Fiducialization: HEP

| Detector | x (cm) | y (cm) | z (cm) | Fiducial Volume (kT) |
| :---: | :---: | :---: | :---: | :---: |
| HD Central | $0$ (drift) | $80$ (top, bottom) | $0$ | $5.85$ |
| HD Lateral | $60$ (drift) | $80$ (top, bottom) | $0$ | $4.88$ |
| VD Top | $0$ (drift) | $0$ (left, right) | $20$ | $7.69$ |
| VD Bottom (**[Shielded](https://indico.fnal.gov/event/70212/contributions/319344/attachments/189449/261576/DUNE_EB_VDshieldingMeetingSD_26Jun2025_JR.pdf)**) | $0$ (drift) | $0$ (left, right) | $20$ | $7.69$ |

<!-- Añadir nota a pie de página sobre shielded config -->

<div class="bottom-note">
Contrary to y and z coordinates (evaluated with the TPC), the x coordinate is computed from TPC-PDS matching and is very affected by Flash-Matching efficiency.
</div>

---

###  Best Cuts: HEP

| Config | NHits | OpHits | AdjCl | Significance |
|---|---:|---:|---:|---:|
| HD Central | 4 | 13 | 5 | 11.370 |
| HD Lateral | 6 | 4 | 5 | 2.630 |
| VD Top | 10 | 10 | 7 | 3.237 |
| VD Bottom Shielded | 8 | 20 | 6 | 2.920 |

<div class="bottom-note">
The best cuts for the HEP analysis are optimized to maximize the Gaussian significance @ 30 years of exposure.
</div>

---

### Fiducialization: Oscillation Parameter Sensitivity

| Detector | x (cm) | y (cm) | z (cm) | Fiducial Volume (kT) |
| :---: | :---: | :---: | :---: | :---: |
| HD Central | $20$ (drift) | $100$ (top, bottom) | $320$ | $2.89$ |
| HD Lateral | $80$ (drift) | $260$ (top, bottom) | $20$ | $1.64$ |
| VD Top | $0$ (drift) | $0$ (left, right) | $20$ | $7.69$ |
| VD Bottom (**[Shielded](https://indico.fnal.gov/event/70212/contributions/319344/attachments/189449/261576/DUNE_EB_VDshieldingMeetingSD_26Jun2025_JR.pdf)**) | $0$ (drift) | $0$ (left, right) | $20$ | $7.69$ |

<!-- Añadir nota a pie de página sobre shielded config -->

<div class="bottom-note">
Contrary to y and z coordinates (evaluated with the TPC), the x coordinate is computed from TPC-PDS matching and is very affected by Flash-Matching efficiency.
</div>

---

### Best Cuts: Oscillation Parameter Sensitivity

| Config | NHits | OpHits | AdjCl | 1D Asimov Z (σ) |
|---|---:|---:|---:|---:|
| HD Central | 1 | 8 | 4 | 63.12 |
| HD Lateral | 3 | 10 | 2 | 21.19 |
| VD Top | 8 | 10 | 8 | 14.89 |
| VD Bottom Shielded | 8 | 10 | 10 | 73.34 |

<div class="bottom-note">
The 1D Asimov Z is computed by comparing the signal over background at the current best-fit values. No uncertainties are included in this metric, which is only used for cut optimization and not for the final sensitivity evaluation.
</div>

---

### Day-Night: Counts

Day-Night event candidate distributions for the different modules clearly determine the region of interest for this analysis at the $10-15$ MeV range, where the signal is expected to be more significant. The HD Central module has the highest signal efficiency and lowest background in this region, which explains its dominant contribution to the overall significance.

<div class="four-col">
  <div>
    <img src="../plots/daynight_counts_hd_1x2x6_centralapa_marley_energy_counts_component_logy_line_operation.png" alt="Latest day-night counts plot for HD Central module">
  </div>
  <div>
    <img src="../plots/daynight_counts_hd_1x2x6_lateralapa_marley_energy_counts_component_logy_line_operation.png" alt="Latest day-night counts plot for HD Lateral module">
  </div>
  <div>
    <img src="../plots/daynight_counts_vd_1x8x14_3view_30deg_nominal_marley_energy_counts_component_logy_line_operation.png" alt="Latest day-night counts plot for VD Top module">
  </div>
  <div>
    <img src="../plots/daynight_counts_vd_1x8x14_3view_30deg_shielded_marley_energy_counts_component_logy_line_operation.png" alt="Latest day-night counts plot for VD Bottom module">
  </div>
</div>

---

### Day-Night Results: Super-Kamiokande

<!-- markdownlint-disable MD033 -->
[The Super-Kamiokande experiment has observed the Day-Night asymmetry at about $3\sigma$ significance](https://doi.org/10.1103/PhysRevD.94.052010).

$$
A^{DN} = \frac{N^{\mathrm{day}} - N^{\mathrm{night}}}{\frac{1}{2}(N^{\mathrm{day}} + N^{\mathrm{night}})}
$$

Report value of **$A_{DN} = -3.6\% \pm 1.6\%$ (stat) $\pm 0.6\%$ (syst)** with a total exposure of 22.5 kT-year.

Note: This follows the Super-K convention $(\mathrm{day}-\mathrm{night})$, opposite in sign to the $(\mathrm{night}-\mathrm{day})$ convention used above for $s_i$.

<!-- markdownlint-enable MD033 -->

---

### HEP: Significance Comparison

Gaussian significance (overestimates low-count bins), Asimov significance (does not extract the power from profiled shape), and ProfileLikelihood (full power of the shape information).

<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <img src="../plots/hep_exposure_hd_1x2x6_centralapa_marley_exposure_significance_variable_spectrumtype_raw_scan.png" alt="Latest day-night significance plot">
  <img src="../plots/hep_exposure_hd_1x2x6_centralapa_marley_exposure_significance_variable_spectrumtype_smoothed_scan.png" alt="Latest day-night exposure plot">
</div>

---

### Oscillation Parameter Sensitivity: ProfileLikelihood Model

- Differently from the HEP case, the Sensitivity model includes two Gaussian-constrained nuisance parameters: $A_{pred}$ (signal normalization $4\%$) and $A_{bkg}$ (background normalization $2\%$). The expected counts in bin $ij$ are:
  $$
  e_{ij} = (1+A_{bkg})B_{ij} + (1+A_{pred})P_{ij}
  $$
  where $B_{ij}$ and $P_{ij}$ are the expected background and signal for a given bin $ij$.
- The stationarity conditions for the profiled nuisance parameters are:
  $$
  \begin{aligned}
  \sum_{ij} P_{ij}\!\left(1-\frac{o_{ij}}{e_{ij}}\right) = -\frac{A_{pred}}{\sigma_\mathrm{pred}^2} \quad \text{and} \quad 
  \sum_{ij} B_{ij}\!\left(1-\frac{o_{ij}}{e_{ij}}\right) = -\frac{A_{bkg}}{\sigma_\mathrm{bkg}^2}
  \end{aligned}
  $$
  which are jointly non-linear in $(A_{pred},A_{bkg})$ because $e_{ij}$ in the denominator depends on both. The profiled nuisance parameters must be solved numerically using an optimization algorithm ([scipy.optimize.minimize](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)).

---

### Oscillation Parameter Sensitivity: Results

HD modules show **modest $2\sigma$ separation** between the current best-fit values of $\Delta m^2_{21}$ from solar and reactor experiments, while **VD modules have no discriminating power**.

<div class="two-col">
  <div>
    <img src="../plots/sensitivity_solarenergy_hd_1x2x6_centralapa_hd_1x2x6_lateralapa_values_dm2_label_solar_variable_sin12_contour.png" alt="Latest oscillation parameter sensitivity plot with HD Phase I">
  </div>
  <div>
    <img src="../plots/sensitivity_solarenergy_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_values_dm2_label_solar_variable_sin12_contour.png" alt="Latest oscillation parameter sensitivity plot with VD Phase I">
  </div>
</div>

<div class="bottom-note">
<strong>Oscillation parameter sensitivity</strong> is currently evaluated for <strong>Phase I (30 years exposure)</strong>.
<!-- The corresponding Phase II projection will be evaluated and included in the next presentation. -->
</div>