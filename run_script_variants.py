#!/usr/bin/env python3
"""
Run all example plots
"""

import sys
import os
import argparse

from itertools import product

# Add debug and show flags to run_all.py
parser = argparse.ArgumentParser(description='Run all scripts with debug output.')
parser.add_argument('-p', '--plot', action='store_true', help='Show plots after running scripts')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
args = parser.parse_args()

def run_script(script_name):
    print(f"Running {script_name}...")
    result = os.system(f"python {script_name}")
    if result != 0:
        print(f"Error: {script_name} failed to execute.")
    return result

if __name__ == "__main__":
    scripts = [
        "scripts/script_preselection_efficiency.py",
        "scripts/script_clustering_efficiency.py --logy",
        "scripts/script_iterable_scan.py --datafile Neutrino_CC_Fraction --config hd_1x2x6 --name marley_official -y TSignalSumK -x 'SignalParticleK' --iterables PDG --labelx 'True Neutrino Energy (MeV)' --labely 'Neutrino Kinetic Energy Fraction' --stacked",
        "scripts/script_iterable_scan.py --datafile Cheated_Calibration_Fit --config hd_1x2x6 --name marley_official -y FitValue -x '#Hits' --iterables Variable --labelx 'Number of Hits'",
        "scripts/script_iterable_scan.py --datafile Primary_Calibration_Fit --config hd_1x2x6 --name marley_official -y FitValue -x '#Hits' --iterables Variable --labelx 'Number of Hits'",
        "scripts/script_iterable_scan.py --datafile NHit_Distributions --name marley_official -v SignalParticleK --iterables '#Hits'",
        "scripts/script_iterable_scan.py --datafile Background -y Counts -x Energy --iterables PDG Particle --labely 'Counts per Energy 1/(kT·years·MeV)' --logy",
        "scripts/script_iterable_scan.py --name marley_official --datafile Cumulative_Vertex_Error -y Sample -x Values --iterables Energy -v X Y Z --labelx 'Vertex Error (cm)' --labely 'Sample Size (%)' --logx",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c Corrected -i '#Hits' --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c Corrected -i '#Hits' -s 1 2 3 --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c '#Hits' --percentile 1 90 --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile PrimaryEnergy_Electron_Calibration -c Calibrated -i '#Hits' -s 1 2 3 -x TrueEnergy -y RawEnergy --labely 'Density' --labelx 'True - Reco Energy (MeV)' --percentile 1 90",
        "scripts/script_compare_hist1d.py --datafile Vertex_Smearing -c 'Coordinate' -x TrueCoordinate -y RecoCoordinate -o subtract --labelx 'True - Reco (cm)' --labely 'Density' --logy",
        "scripts/script_compare_hist2d.py --datafile Neutrino_CC_Production --config hd_1x2x6 -x SignalParticleK -y Energy --labelx 'True Neutrino Energy (MeV)' -i Particle -s Electron --labely 'True Electron Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_CC_Production --config hd_1x2x6 -x SignalParticleK -y Energy --labelx 'True Neutrino Energy (MeV)' -i Particle -s Gamma --labely 'True Gamma Energy (MeV)' --logz",
        "scripts/script_compare_hist2d.py --datafile Charge_Lifetime_Correction -x Time -y ChargePerEnergy -c Corrected -i '#Hits' -s 1 2 3 --logz  --zoom",
        "scripts/script_compare_hist2d.py --datafile PrimaryEnergy_Electron_Calibration -c Calibrated -i '#Hits' -s 2 -x TrueEnergy -y RawEnergy --labelx 'True Electron Energy (MeV)' --labely 'Raw Electron Energy (MeV)' --diagonal --logz --zoom",
        "scripts/script_compare_hist2d.py --datafile CheatedEnergy_Electron_Calibration -i '#Hits' -s 3 -e 1 -x TrueEnergy -y RawEnergy --labelx 'True Electron Energy (MeV)' --labely 'Reconstructed Electron Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Vertex_Smearing -c 'Coordinate' -x TrueCoordinate -y RecoCoordinate --labelx 'True Coordinate (cm)' --labely 'Reconstructed Coordinate (cm)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Vertex_Smearing -i 'Coordinate' -s X Y Z -x TrueCoordinate -y RecoCoordinate --labelx 'True Coordinate (cm)' --labely 'Reconstructed Coordinate (cm)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile AdjCl_Selection -x AdjClR -y AdjClCharge -c Signal --labelx 'Vertex Distance (cm)' --labely 'Adjacent Cluster Charge (ADC x tick)' --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_Energy -x TrueEnergy -y RecoEnergy -c Calibrated -s SelectedEnergy --labelx 'True Neutrino Energy (MeV)' --labely 'Reconstructed Neutrino Energy (MeV)' --diagonal --logz",
        "scripts/script_line_fit.py --datafile Electron_Energy_Resolution --name marley_official -x Values -y RMS --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True' -i Clustering Drift '#Hits' -s Ideal True 3"
        "scripts/script_line_fit.py --datafile Purity_Match_Resolution --name marley_official -x Values -y Density --labelx 'True - Reco (cm)' --labely 'Density' -i Coordinate -s X",
        "scripts/script_configuration_comparison.py --datafile Adjacent_Cluster_Distributions --configs hd_1x2x6_lateralAPA vd_1x8x14_3view_30deg_nominal -v AdjClMainE AdjClEnergy -y Count -c Signal --labelx 'True Particle Energy (MeV)' 'Reconstructed Cluster Energy (MeV)' --labely 'Counts per Event' --logx --logy",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s None 3 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s None 5 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s 6 5 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s 10 5 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s None 3 --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s 6 3 --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma -s 10 3 --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s reco true 3 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s ideal none 3 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s ideal true 1 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s reco reco 1 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Neutrino_Energy_Resolution -y RMS -v TotalEnergy SelectedEnergy -i Drift '#Hits' -s reco 3 --labelx 'True Neutrino Energy (MeV)' --labely 'RMS (True - Reco) / True'",
    ]

    all_results = []
    for script in scripts:
        if args.plot and args.debug:
            this_result = run_script(script + " -p -d")  # Adding -s flag to show plots
        elif args.plot:
            this_result = run_script(script + " -p")
        elif args.debug:
            this_result = run_script(script + " -d")
        else:
            this_result = run_script(script)
        
        if this_result != 0:
            print(f"Script {script} failed. Exiting.")
        all_results.append(this_result)

    if sum(all_results) == 0:
        print("\033[92m" + "All scripts executed successfully." + "\033[0m")
    else:
        for i, result in enumerate(all_results):
            if result != 0:
                print("\033[91m" + f"Script {scripts[i]} encountered an error." + "\033[0m")
