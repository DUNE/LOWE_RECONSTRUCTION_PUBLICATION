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
Sergio Manthey Corchado - CIEMAT - Low-Energy Working Group - 25/03/2026
</div>
<!-- markdownlint-enable MD033 -->

---

## Overview

**DUNE** can address several key questions in solar neutrino physics. To do so, we need to evaluate the following:

- **Day-Night:** can we resolve small differences in solar neutrino rates?
- **HEP**: do we have the resolution to discover the high-energy tail of the solar neutrino spectrum?
- **Oscillation Parameter Sensitivity**: do we have the precision to separate current best-fit values (solar vs. reactor) of $\Delta m^2_{21}$?

**Phase I results** are based on the latest available information on FD backgrounds and reconstruction performance.
**Phase II projections** assume **2 additional HD / VD Phase I modules** with a 5-year offset, emphasizing the impact of increased exposure for each case.

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

- **CC Neutrino events** generated with MARLEY in the $4-30$ MeV range.
- **Cavern backgrounds** (gamma and neutron) propagated through the LAr buffer and reconstructed with the same algorithms as neutrino events.

All of this *SingleGen* productions are propagated within the full background model configuration (v.3), which includes all radiological, component-induced and external backgrounds. A **LowE Reconstruction Workflow** has been designed to maximize the signal efficiency with custom [TPC Clustering](https://github.com/DUNE/dunereco/blob/develop/dunereco/LowEUtils/LowECluster.h), [PDS Flash-Finding](https://github.com/DUNE/duneopdet/blob/develop/duneopdet/LowEPDSUtils/SolarOpFlash_module.cc) and [TPC-PDS Matching](https://github.com/DUNE/dunereco/blob/develop/dunereco/LowEUtils/LowEUtils.h) algorithms.

<div class="bottom-note">
The current MC production does not include SingleGen electron / alpha radiological backgrounds, which are expected to be subdominant in the energy range of interest for these analyses.
</div>

---

### Analysis Workflow: **Day-Night** / **HEP**

These analyses follow identical steps:

1. Build **signal and background energy spectra**.
2. For 4 different **[energy reconstruction algorithms](https://indico.fnal.gov/event/67363/contributions/315640/attachments/188171/259640/25_05_21_DUNE_SOLAR_NEUTRINO_STUDIES.pdf)**, iterate over a set of **analysis parameters**: number of TPC hits `nhits`, PDS optical hits `ophits`, adjacent clusters `adjcls`, and reconstructed energy threshold.
3. Compute a **per-bin significance** above an energy threshold to determine the selection leading to the highest $S/\sqrt{B}$.
4. **Combine bins in quadrature** and scan exposure to evaluate the significance curve as a function of time.

---

### Analysis Workflow: **Oscillation Parameter Sensitivity**

Oscillation Parameter Sensitivity analysis varies slightly:

1. For the selected analysis parameters, **convolve** the signal spectrum with the **oscillation probability matrix** (azimuth vs true $\nu_e$ energy) for each point in the $\Delta m^2_{21}$ vs $\sin^2\theta_{12}$ parameter space.
2. Evaluate the $\chi^2$ from a **log-likelihood ratio test** comparing the convolved signal + background to the reference signal + background hypothesis.
3. **Scan over oscillation parameters** to produce sensitivity contours.
4. Compare the sensitivity contours to the current best-fit values from solar and reactor experiments to evaluate the separation power of DUNE.

---

### Analysis Workflow: Common Assumptions

- All analyses are performed on **reconstructed energy spectra** with solar neutrino flux uncertainty of $\pm 4\%$ and background uncertainty of $\pm 2\%$.
- The analyses are performed by applying a **fiducial cut from each detector boundary**.
- Currently, the same fiducialization is applied for all analyses in each detector: <br>

| Detector | x (cm) | y (cm) | z (cm) | Volume (kT) |
| :---: | :---: | :---: | :---: | :---: |
| HD Central | $0$ (drift) | $120$ (top, bottom) | $280$ | $5.3$ |
| HD Lateral | $80$ (drift) | $240$ (top, bottom) | $240$ | $3.1$ |
| VD Top | $160$ (drift) | $300$ (left, right) | $220$ | $2.9$ |
| VD Bottom (**[Shielded](https://indico.fnal.gov/event/70212/contributions/319344/attachments/189449/261576/DUNE_EB_VDshieldingMeetingSD_26Jun2025_JR.pdf)**) | $0$ (drift) | $100$ (left, right) | $200$ | $5.9$ |

<!-- Añadir nota a pie de página sobre shielded config -->

<div class="bottom-note">
Contrary to y and z coordinates (evaluated with the TPC), the x coordinate is computed from TPC-PDS matching and is very affected by Flash-Matching efficiency.
</div>

---

## Day-Night Asymmetry

---

### Day-Night: Signal

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

### Day-Night: Single Module

Previously presented data as exposure in kT·years useful for single module studies. To add components, better multiply by each module's mass and combine exposure in DUNE years. 

<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <img src="../plots/daynight_significance_hd_1x2x6_lateralapa_marley_energy_counts_component_logy_line_operation.png" alt="Latest day-night exposure plot">
  <img src="../plots/hd_daynight_exposure_hd_1x2x6_lateralapa_marley_exposure_significance_error_comparison.png" alt="Latest day-night exposure plot">
</div>

---

### Day-Night: Combined Results

Results predict <strong>3σ (5σ)</strong> significance in <strong>5 (15) years</strong> of DUNE data.
<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <div>
  <img src="../plots/daynight_significance_marley_exposure_significance_error_comparison.png" alt="Latest day-night exposure plot">
  </div>
  <div>
    <ul>
      <li>Day-Night asymmetry significance is dominated by the HD Central module.</li>
      <li>The addition of the other modules only provides a modest increase in significance.</li>
      <li>VD modules on their own are not expected to reach 3σ significance within the first 20 years of DUNE data.</li>
      <li>Current shielding proposal for the VD Bottom module is not enough.</li>
    </ul>
  </div>
</div>

---

### Day-Night: Projections

Combined <strong>VD Phase II</strong> projection is <strong>less capable than a single HD module (Phase I)</strong> due to the higher cavern background, which dominates the significance.

<!-- markdownlint-disable MD033 -->
<div class="two-col">
  <div>
    <img src="../plots/daynight_significance_hd_1x2x6_lateralapa_marley_exposure_significance_error_comparison.png" alt="Latest day-night exposure plot">
  </div>
  <div>
    <img src="../plots/daynight_significance_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_marley_exposure_significance_error_comparison.png" alt="Projected day-night exposure plot">
  </div>
</div>

<div class="bottom-note">
Projecting the results to <strong>Phase II exposure</strong> with a <strong>5-year offset</strong>:
</div>

---

## HEP Discovery

---

### HEP: Signal

The signal is the expected number of **HEP events** in bin `i`:
$$
s_i = \mathcal{E} M H_i^{\mathrm{HEP}} \quad
b_i = \mathcal{E} M B_i
$$

where:

- $H_i^{\mathrm{HEP}}$ is the expected HEP signal in bin `i`
- $B_i$ is the combined background in bin `i` (solar ⁸B + cavern backgrounds + radiological)

---

### HEP: Discovery Criterion

Only bins with enough expected HEP yield are counted. The analysis requires:

$$
\mathcal{E} M H_i^{\mathrm{HEP}} \left(1 - 3\sigma_s\right) > 1
$$

Bins contribute only if more than one expected HEP event after a conservative (3σ_s) uncertainty penalty.

- HEP signal systematic uncertainty: `30%`
- Background systematic uncertainty: `2%`
- Template statistical uncertainties are also included bin-by-bin

---

### HEP: Significance Metric

Gaussian significance is a poor approximation for low-count searches, so we **use Asimov significance**:

$$
\alpha_{A,i} = \sqrt{2\left[(s_i+b_i)\ln\!\left(\frac{(s_i+b_i)(b_i+\sigma_{b,i}^2)}{b_i^2+(s_i+b_i)\sigma_{b,i}^2}\right) - \frac{b_i^2}{\sigma_{b,i}^2}\ln\!\left(1+\frac{\sigma_{b,i}^2 s_i}{b_i(b_i+\sigma_{b,i}^2)}\right)\right]}
$$

where:

- $s_i$ is the HEP signal in bin `i`
- $b_i$ is the total background in bin `i`
- $\sigma_{b,i}$ is the combined background uncertainty in bin `i`

$$
\sigma_{b,i} = \sqrt{b_i + \left(0.02\,b_i\right)^2}
$$

---

### HEP: Single Module

HD Central is the only sub-module expected to reach a 5σ discovery of the HEP component.

<div class="two-col">
  <img src="../plots/hep_significance_hd_1x2x6_centralapa_marley_energy_counts_component_logy_line_operation.png" alt="Latest HEP exposure plot">
  <img src="../plots/hd_hep_exposure_hd_1x2x6_centralapa_marley_exposure_significance_error_variable_asimov_comparison.png" alt="Latest HEP exposure plot">
</div>

<div class="bottom-note">
The jagged shape of the significance curve is a consequence of the conservative bin-counting criterion.
</div>

---

### HEP: Combined Results

**HEP discovery** results shows an even stronger HD Central dependence due to higher signal efficiency in the high-energy tail of the spectrum.

<div class="two-col">
  <img src="../plots/hep_significance_marley_exposure_significance_variable_asimov_comparison.png" alt="Latest HEP exposure plot">
  <div>
    <ul>
      <li>HEP discovery only achievable with the HD Central module.</li>
      <li>The addition of the other modules does not increase the significance.</li>
      <li>VD modules on their own do not reach 1σ significance.</li>
    </ul>
</div>

---

### HEP: Projection

**Phase II FD modules arrive too late** (assuming 5-year offset) to increase HEP discovery, due to the slow accumulation of high-energy events and the conservative bin-counting criterion.

<div class="two-col">
  <div>
    <img src="../plots/hep_significance_hd_1x2x6_lateralapa_marley_exposure_significance_variable_asimov_comparison.png" alt="Latest HEP exposure plot with HD Phase II projection">
  </div>
  <div>
    <img src="../plots/hep_significance_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_marley_exposure_significance_variable_asimov_comparison.png" alt="Latest HEP exposure plot with VD Phase II projection">
  </div>
</div>

---

## Oscillation Parameter Sensitivity

---

### Oscillation Parameter Sensitivity: Combined Results

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

---

### Conclusions

Phase I results are **dominated by the HD Central module**. VD technology performs worse: charge readout closest to cavern background and opposite to PDS plane.  

- Combined **Day-Night Asymmetry** reaches **$5\sigma$ ($3\sigma$)** within the first **$15$ ($5$) years** of data, which could be improved by **$7$ years** with the addition of **2 FD-HD modules to Phase II**.
- The combined **HEP discovery significance ($5\sigma$)** should be reached within **10 years** of DUNE data thanks to FD-HD, independently of the addition of Phase II modules.
- The oscillation parameter sensitivity is able to **separate the current best-fit** $\Delta m^2_{21}$ from **reactor experiments** only at the **$2\sigma$** level with Phase I (30 years) of exposure.

The addition of 2 Phase II modules (same as FD-HD or FD-VD from Phase I) is expected to improve current Day-Night Asymmetry sensitivity, but only have a minor impact on HEP discovery. The impact of Phase II on oscillation parameter sensitivity is still under evaluation.

---

### Next Steps

- **Update shielded cavern background gamma spectrum** in LArSoft.
- Review the **impact** of absolute energy-scale uncertainties on the **high-energy tail of the cavern gamma** spectrum.
- Update HEP discovery significance computation by rebinning the high-energy part of the spectrum: **smoother significance increase**.
- Explore the **impact of systematic uncertainties** and assumptions on significance.
- Prepare a final presentation for the **upcoming DUNE collaboration meeting**.
- Write a **technical note** detailing the analysis methods, assumptions, and results for internal documentation and publication.

---

<!-- _class: sectionpage -->
## Backup

---

### Day-Night Results: Super-Kamiokande

<!-- markdownlint-disable MD033 -->
[The Super-Kamiokande experiment has observed the Day-Night asymmetry at about $3\sigma$ significance](https://doi.org/10.1103/PhysRevD.94.052010).

$$
A^{DN} = \frac{N^{\mathrm{day}} - N^{\mathrm{night}}}{\frac{1}{2}(N^{\mathrm{day}} + N^{\mathrm{night}})}
$$

Report value of **$A_{DN} = -3.6\% \pm 1.6\%$ (stat) $\pm 0.6\%$ (syst)** with a total exposure of 22.5 kT-year.

Note: This follows the Super-K convention $(\mathrm{day}-\mathrm{night})$, opposite in sign to the $(\mathrm{night}-\mathrm{day})$ convention used above for $s_i$.

---

### Background Spectra Comparison

<div class="two-col">
  <div>
    <img src="../plots/weighted_nominal_vd_1x8x14_3view_30deg_nominal_gamma_config_weight_signalparticleweight_surface_nan_logy_hist1d.png" alt="Gamma background spectrum after LAr buffer propagation">
  </div>
  <div>
    <img src="../plots/weighted_nominal_vd_1x8x14_3view_30deg_nominal_neutron_config_weight_signalparticleweight_surface_nan_logy_hist1d.png" alt="Neutron background spectrum after LAr buffer propagation">
  </div>
</div>

---

### Fiducialization Impact on Background Spectra

<div class="two-col">
  <div>
    <img src="../plots/solarenergy_analysisdata_gamma_energy_truecounts_nhits_1_ophits_4_adjcl_10_logy_comparison.png" alt="Gamma background spectrum after LAr buffer propagation and fiducialization">
  </div>
  <div>
    <img src="../plots/solarenergy_analysisdata_neutron_energy_truecounts_nhits_1_ophits_4_adjcl_10_logy_comparison.png" alt="Neutron background spectrum after LAr buffer propagation and fiducialization">
  </div>
</div>

---

### Reconstructed Background Spectra

<div class="two-col">
  <div>
    <img src="../plots/solarenergy_analysisdata_gamma_energy_counts_nhits_1_ophits_4_adjcl_10_logy_comparison.png" alt="Gamma background spectrum after LAr buffer propagation and fiducialization">
  </div>
  <div>
    <img src="../plots/solarenergy_analysisdata_neutron_energy_counts_nhits_1_ophits_4_adjcl_10_logy_comparison.png" alt="Neutron background spectrum after LAr buffer propagation and fiducialization">
  </div>
</div>
<!-- markdownlint-enable MD033 -->
