---
marp: true
math: mathjax
title: Day-Night Asymmetry and HEP Discovery Significance
paginate: true
theme: default
style: |
  section {
    font-size: 28px;
    padding: 48px;
    padding-bottom: 88px; /* reserve space for bottom notes */
    justify-content: flex-start; /* keep slide titles/content at top */
    position: relative; /* anchor absolute bottom-note */
  }
  section.titlepage {
    justify-content: center; /* exception: title page */
  }
  h1, h2 {
    color: #0f3d5e;
    margin-top: 0;
  }
  .small {
    font-size: 20px;
  }
  .tiny {
    font-size: 16px;
  }
  .center {
    text-align: center;
  }
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    align-items: top;
  }
  .bottom-note {
    position: absolute;
    left: 48px;
    right: 48px;
    bottom: 24px;
    color: #555;
  }
  img {
    max-width: 100%;
    max-height: 520px;
    object-fit: contain;
  }
  table {
    margin-left: auto;
    margin-right: auto;
  }
---

<!-- _class: titlepage -->
# Combined Day-Night Asymmetry and HEP Discovery

<div class="bottom-note">
Sergio Manthey Corchado
</div>

---

## Overview

Presenting the latest results on the combined Day-Night Asymmetry and High-Energy Tail (HEP) discovery significance as a function of DUNE exposure.

- **Day-Night:** can we resolve the difference between night and day solar neutrino rates?
- **HEP**: can we see the yet unobserved high-energy tail of the solar neutrino spectrum above 8B and detector backgrounds?
- Oscillation Parameters: can we measure the solar neutrino oscillation parameters with high precision?

<div class="small bottom-note">
This presentation focuses on the first two analyses. The oscillation parameter sensitivity will be covered in a future presentation.
</div>

<!-- <div class="small">
Based on <code>src/analysis/12DayNight.py</code>, <code>src/analysis/12DayNightExposurePlot.py</code>, <code>src/analysis/13HEP.py</code>, and <code>src/analysis/13HEPExposurePlot.py</code>.
</div> -->

---

## Theoretical Assumptions

<div class="two-col">
  <div>
  Best fit values for the solar oscillation parameters from NuFIT 5.2 (2024).
  <br><br>

  | Parameter | Value |
  |:---:|:---:|
  | $\sin^2\theta_{12}$ | 0.303 |
  | $\Delta m^2_{21}$ (eV$^2$) | $6.0 \times 10^{-5}$ |
  | $\sin^2\theta_{13}$ | 0.021 |
  
  </div>
  <div>
  Solar neutrino fluxes and uncertainties are taken from the latest B16-GS98 solar model.
  <img src="../plots/solar_neutrino_spectrum_energy_flux_source_logx_logy_scan.png" alt="Solar neutrino spectrum with fluxes and uncertainties">
  </div>
</div>

---

## Analysis Workflow

Both analyses (**Day-Night** / **HEP**) follow identical steps:

1. Build signal and background spectra after a chosen set of cuts.
2. Compute a per-bin significance above an energy threshold.
3. Combine bins in quadrature and scan exposure to evaluate the significance curve as a function of experiment time.

Currently, using:

- Common fiducialization cut.
- **Day-Night** analysis threshold of `8 MeV`.
- **HEP** analysis threshold of `10 MeV`.
- Scan over `NHits`, `OpHits`, and `AdjCl` cut combinations and select the best-performing one.

---

## Day-Night: What Is the Signal?

The signal is not "all solar events". It is the **difference** between the night and day solar spectra. Consequently, the background is the combination of day solar events and all other backgrounds:

$$
s_i = \mathcal{E} M \left(N_i^{\mathrm{night}} - N_i^{\mathrm{day}}\right) \quad \text{and} \quad
b_i = \mathcal{E} M \left(\frac{B_i}{2} + N_i^{\mathrm{day}}\right)
$$

where:

- $N_i^{\mathrm{night}}$ is the expected night solar neutrino spectrum in bin `i`
- $N_i^{\mathrm{day}}$ is the expected day solar neutrino spectrum in bin `i`
- $B_i$ is the total background in bin `i` (cavern backgrounds + radiological)

---

## Day-Night: How Asymmetry Uncertainties are Assessed

Evaluate uncertainty bands by varying the solar model normalization $\pm 13\%$ (corresponding to predictions of Earth's density profile by @LopezMoreno) and an additional background uncertainty term.

- Explicit signal uncertainty $\sigma_{s,i}$ set to 0.
- Explicit background uncertainty term used in the error curve:

$$
\sigma_{b,i} = \frac{1}{\sqrt{\mathcal{E} M B_i / 2}}
$$

---

## Day-Night: What is the Significance Metric?

In the case of Gaussian significance computation with signal and background uncertainties, the computations is:

$$
\alpha_i = \frac{s_i}{\sqrt{b_i + \sigma_{b,i}^2 + \sigma_{s,i}^2}} \quad
\alpha_\text{G} = \sqrt{\sum_i \sigma_i^2}
$$

---

## DUNE Combined Day-Night Asymmetry

<div class="center">
  <img src="../plots/daynight_significance_marley_exposure_significance_error_comparison.png" alt="Latest day-night exposure plot">
</div>

<div class="small">
Latest day-night exposure figure:<br>
Timestamp: 2026-03-18 15:21 UTC
</div>

---

## Combined Day-Night Asymmetry: Projections

Projecting the results to Phase II exposure with a 5-year offset we get:

<!-- Add a side-by-side plot -->
<div class="two-col">
  <div>
    <img src="../plots/daynight_significance_hd_1x2x6_lateralapa_marley_exposure_significance_error_comparison.png" alt="Latest day-night exposure plot">
  </div>
  <div>
    <img src="../plots/daynight_significance_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_marley_exposure_significance_error_comparison.png" alt="Projected day-night exposure plot">
  </div>
</div>

<div class="small">
Latest day-night exposure figure for the nominal configuration:<br>
Timestamp: 2026-03-18 15:21 UTC
</div>

---

## HEP: What Is the Signal?

The signal is the expected number of HEP events in bin `i`:
$$
s_i = \mathcal{E} M H_i^{\mathrm{HEP}} \quad
b_i = \mathcal{E} M B_i
$$

where:

- $H_i^{\mathrm{HEP}}$ is the expected HEP signal in bin `i`
- $B_i$ is the combined background in bin `i` (solar ⁸B + cavern backgrounds + radiological)

---

## HEP: How Discovery is Predicted?

Only bins with enough expected HEP yield are counted. The code requires:

$$
\mathcal{E} M H_i^{\mathrm{HEP}} \left(1 - 3\sigma_s\right) > 1
$$

Bins contribute only if more than one expected HEP event after a conservative ($3 \sigma_s$) uncertainty penalty.

- HEP signal systematic uncertainty: `30%`
- background systematic uncertainty: `2%`
- template statistical uncertainties are also included bin-by-bin

---

## HEP: What is the Significance Metric?

Gaussian significance is known to be a poor approximation for low-count searches, so the code evaluates: Asimov significance.:

$$
\alpha_{A,i} = \sqrt{2\left[(s_i+b_i)\ln\!\left(\frac{(s_i+b_i)(b_i+\sigma_{b,i}^2)}{b_i^2+(s_i+b_i)\sigma_{b,i}^2}\right) - \frac{b_i^2}{\sigma_{b,i}^2}\ln\!\left(1+\frac{\sigma_{b,i}^2 s_i}{b_i(b_i+\sigma_{b,i}^2)}\right)\right]}
$$

where:

- $s_i$ is the HEP signal in bin `i`
- $b_i$ is the total background in bin `i`
- $\sigma_{b,i}$ is the combined background uncertainty in bin `i`

---

## Combined HEP Discovery

<div class="center">
  <img src="../plots/hep_significance_marley_exposure_significance_error_variable_asimov_comparison.png" alt="Latest HEP exposure plot">
</div>

<div class="small">
Latest HEP exposure figure.
</div>

---

## Combined HEP Discovery: Projection

<div class=two-col>
  <div>
    <img src="../plots/hep_significance_hd_1x2x6_lateralapa_marley_exposure_significance_error_variable_asimov_comparison.png" alt="Latest HEP exposure plot with HD Phase II projection">
  </div>
  <div>
    <img src="../plots/hep_significance_vd_1x8x14_3view_30deg_nominal_vd_1x8x14_3view_30deg_shielded_marley_exposure_significance_error_variable_asimov_comparison.png" alt="Latest HEP exposure plot with VD Phase II projection">
  </div>
</div>

---

## Conclusions

- The combined Day-Night Asymmetry and HEP discovery significance computation as a function of global exposure (DUNE years) is completed.
- The combined Day-Night Asymmetry should reach $3\sigma$ within the first 5 years of data and $5\sigma$ within 8 (10) years for the HD (VD) Phase II projections.
- The combined HEP Discovery ($5\sigma$) should be reached within 10 years of DUNE data.
- In both cases, the main contribution comes from the HD Central dataset.

---

# Backup

---

## Day-Night Results: Super-Kamiokande

[The Super-Kamiokande experiment has observed the Day-Night asymmetry at about $3\sigma$ significance](https://doi.org/10.1103/PhysRevD.94.052010).

$$
A^{DN} = \frac{N^{\mathrm{day}} - N^{\mathrm{night}}}{\frac{1}{2}(N^{\mathrm{day}} + N^{\mathrm{night}})}
$$

Report value of $A_{DN} = -3.6\% \pm 1.6\%$ (stat) $\pm 0.6\%$ (syst) with a total exposure of 22.5 kton-year.
