#!/usr/bin/env python3

"""
Digitizes the reference SiPM relative PDE vs. angle-of-incidence measurement
(nEXO:2019jhg) and fits it with three candidate models, saving one pkl per
model for script_line_fit.py:

  - FresnelProduct: A * cos(theta) * T(theta)   (Fresnel transmittance into a
    denser window; the Fresnel term can only steepen the cos(theta) falloff,
    so it fits poorly here -- kept for the record).
  - FresnelInverse: A * cos(theta) / T(theta)   (Fresnel term treated as a
    compensating funnelling gain instead of a loss).
  - SqrtCosine:     A * sqrt(cos(theta))        (empirical, best chi2/ndof).
"""

import os
import pickle

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from _bootstrap import ensure_src_path

ensure_src_path()

from lib.functions import (
    angular_pde_cosine_fresnel,
    angular_pde_cosine_fresnel_inverse,
    angular_pde_sqrt_cosine,
)

# Digitized from the nEXO:2019jhg relative-PDE-vs-angle-of-incidence figure
ANGLE = np.array([0, 0, 0, 15, 15, 20, 35, 35, 45, 55, 55, 60, 65, 65], dtype=float)
RELATIVE_PDE = np.array(
    [0.955, 0.965, 0.995, 0.895, 0.955, 0.905, 0.885, 0.835, 0.830, 0.785, 0.76, 0.72, 0.65, 0.62]
)
RELATIVE_PDE_ERROR = np.full_like(RELATIVE_PDE, 0.02)

MODELS = {
    "SiPMAngleFresnelProduct": {
        "func": angular_pde_cosine_fresnel,
        "label": "Cosine x Fresnel Angular PDE",
        "p0": [1.0, 1.3],
        "bounds": ([0, 1.001], [3, 5]),
        "params_label": ["$A$", "$n$"],
        "params_format": [".3f", ".3f"],
        "params_unit": ["", ""],
    },
    "SiPMAngleFresnelInverse": {
        "func": angular_pde_cosine_fresnel_inverse,
        "label": "Cosine / Fresnel Angular PDE",
        "p0": [0.97, 1.3],
        "bounds": ([0, 1.001], [3, 5]),
        "params_label": ["$A$", "$n$"],
        "params_format": [".3f", ".3f"],
        "params_unit": ["", ""],
    },
    "SiPMAngleSqrtCosine": {
        "func": angular_pde_sqrt_cosine,
        "label": "Sqrt-Cosine Angular PDE",
        "p0": [1.0],
        "bounds": ([0], [3]),
        "params_label": ["$A$"],
        "params_format": [".3f"],
        "params_unit": [""],
    },
}


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "input", "data")

    for name, spec in MODELS.items():
        popt, pcov = curve_fit(
            spec["func"],
            ANGLE,
            RELATIVE_PDE,
            p0=spec["p0"],
            sigma=RELATIVE_PDE_ERROR,
            absolute_sigma=True,
            bounds=spec["bounds"],
            maxfev=20000,
        )
        perr = np.sqrt(np.diag(pcov))
        fit = spec["func"](ANGLE, *popt)
        chi2 = float(np.sum(((RELATIVE_PDE - fit) / RELATIVE_PDE_ERROR) ** 2))
        ndof = len(ANGLE) - len(popt)

        df = pd.DataFrame(
            [
                {
                    "Config": "DUNE",
                    "Name": name,
                    "Angle": ANGLE,
                    "RelativePDE": RELATIVE_PDE,
                    "RelativePDEError": RELATIVE_PDE_ERROR,
                    "Params": popt,
                    "ParamsFormat": spec["params_format"],
                    "ParamsLabel": spec["params_label"],
                    "ParamsError": perr,
                    "ParamsUnit": spec["params_unit"],
                    "FitFunction": spec["func"],
                    "FitFunctionLabel": spec["label"],
                    "Chi2": chi2,
                }
            ]
        )

        output_file = os.path.join(output_dir, f"DUNE_{name}_AngularPDE.pkl")
        with open(output_file, "wb") as f:
            pickle.dump(df, f)
        print(
            f"Saved -> {os.path.normpath(output_file)} "
            f"(chi2/ndof = {chi2 / ndof:.2f}, params = {popt})"
        )


if __name__ == "__main__":
    main()
