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
        "scripts/script_iterable_scan.py --datafile Clustering_Efficiency --config hd_1x2x6_centralAPA vd_1x8x14_3view_30deg_nominal --name marley_official -v Purity --iterables '#Hits' -y Density --reduce --labely 'Density' --logy",
        "scripts/script_iterable_scan.py --datafile Clustering_Efficiency --config hd_1x2x6_centralAPA vd_1x8x14_3view_30deg_nominal --name marley_official -v Completeness --iterables '#Hits' -y Density --reduce --labely 'Density' --logy",
        "scripts/script_iterable_scan.py --datafile Preselection_Efficiency --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -v SignalParticleK --iterables '#Hits' -y Efficiency --reduce --labely 'Efficiency (%)' --connect",
        "scripts/script_iterable_scan.py --datafile Preselection_Efficiency --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -v SignalParticleX SignalParticleY SignalParticleZ --iterables '#Hits' -y Efficiency --labely 'Efficiency (%)' --connect",
        "scripts/script_iterable_scan.py --datafile Neutrino_CC_Fraction --config hd_1x2x6 --name marley_official -y TSignalSumK -x 'SignalParticleK' --iterables PDG --labelx 'True Neutrino Energy (MeV)' --labely 'Neutrino Kinetic Energy Fraction' --stacked",
        "scripts/script_iterable_scan.py --datafile Cheated_Calibration_Fit --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -y FitValue -x '#Hits' --iterables Variable --labelx 'Number of Hits'",
        "scripts/script_iterable_scan.py --datafile Primary_Calibration_Fit --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -y FitValue -x '#Hits' --iterables Variable --labelx 'Number of Hits'",
        "scripts/script_iterable_scan.py --datafile NHit_Distributions --config hd_1x2x6 --name marley_official -v SignalParticleK --iterables '#Hits'",
        "scripts/script_iterable_scan.py --datafile NHit_Distributions --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -v ElectronK --iterables '#Hits' --reduce --labelx 'True Electron Energy (MeV)'",
        "scripts/script_iterable_scan.py --datafile Background --config hd_1x2x6_centralAPA -y Counts -x Energy --iterables PDG Particle --labely 'Counts per Energy 1/(kT·years·MeV)' --logy",
        "scripts/script_iterable_scan.py --datafile Solar_Neutrino_Spectrum -y Flux -x Energy --iterables Source --labely 'Flux (Hz / MeV·cm²)' --logx --logy",
        "scripts/script_iterable_scan.py --datafile SN_Neutrino_Spectrum -y Flux -x 'Energy (MeV)' --iterables Source --labely 'Events (1 / MeV·kT)' --labelz Model",
        "scripts/script_iterable_scan.py --datafile Adjacent_Cluster_Distributions --config vd_1x8x14_3view_30deg_nominal --name marley_official -v AdjClMainE -y Counts --iterables Signal --labelx 'True Particle Energy (MeV)' --labely 'Counts per Event' --logx --logy",
        "scripts/script_iterable_scan.py --datafile Adjacent_Cluster_Distributions --config vd_1x8x14_3view_30deg_shielded --name marley -v AdjClMainE -y Counts --iterables Signal --labelx 'True Particle Energy (MeV)' --labely 'Counts per Event' --labelz 'Adjacent Cluster' --logx --logy",
        "scripts/script_iterable_scan.py --datafile Adjacent_Cluster_Distributions --configs hd_1x2x6_lateralAPA --name marley_official -v AdjClEnergy -y Counts --iterables Signal --labelx 'Reconstructed Cluster Energy (MeV)' --labely 'Counts per Event' --labelz 'Adjacent Cluster' --logx --logy",
        "scripts/script_iterable_scan.py --datafile Adjacent_Cluster_Distributions --configs vd_1x8x14_3view_30deg_nominal --name marley_official -v AdjClEnergy -y Counts --iterables Signal --labelx 'Reconstructed Cluster Energy (MeV)' --labely 'Counts per Event' --logx --logy",
        "scripts/script_iterable_scan.py --datafile Cumulative_Vertex_Error --config hd_1x2x6_centralAPA --name marley_official -y Sample -x Values --iterables Energy -v X Y Z --labelx 'Vertex Error (cm)' --labely 'Sample Size (%)' --logx",
        "scripts/script_iterable_scan.py --datafile Cumulative_Vertex_Error --config hd_1x2x6_lateralAPA --name marley_official -y Sample -x Values --iterables Variable --save_keys Energy -s 12.0 --labelx 'Vertex Error (cm)' --labely 'Sample Size (%)' --logx",
        "scripts/script_iterable_scan.py --datafile Cumulative_Vertex_Error --config vd_1x8x14_3view_30deg_nominal --name marley_official -y Sample -x Values --iterables Variable --save_keys Energy -s 12.0 --labelx 'Vertex Error (cm)' --labely 'Sample Size (%)' --logx",
        "scripts/script_iterable_scan.py --datafile TPC_Cluster_Efficiency_Drift_Scan  --config vd_1x8x14_3view_30deg --name marley_official -y Efficiency -x Coordinate -v X --iterables Energy --connect --labelx 'Drift Coordinate (cm)' --labely 'Efficiency (%)'",
        "scripts/script_iterable_scan.py --datafile TPC_Cluster_Efficiency_Energy_Scan --config vd_1x8x14_3view_30deg --name marley_official -y Efficiency -x Energy -v X --iterables Coordinate  --connect --labelx 'True Neutrino Energy (MeV)' --labely 'Efficiency (%)'",
        "scripts/script_iterable_scan.py --datafile TPC_Cluster_Efficiency_Plane_Scan  --config vd_1x8x14_3view_30deg --name marley_official -y Efficiency -x Coordinate --iterables Plane -v X Y Z --connect --labelx 'Coordinate (cm)' --labely 'Efficiency (%)'",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c Corrected -i '#Hits' --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c Corrected -i '#Hits' -s 1.0 2.0 3.0 --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c '#Hits' --percentile 1 90 --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile PrimaryEnergy_Electron_Calibration -c Calibrated -i '#Hits' -s 1 2 3 -x TrueEnergy -y RawEnergy --labely 'Density' --labelx 'True - Reco Energy (MeV)' --percentile 1 90",
        "scripts/script_compare_hist1d.py --datafile Gamma_Energy --config hd_1x2x6_centralAPA -c Transition -x RecoEnergy --labely 'Density' --labelx 'True Energy (MeV)' --percentile 51 99",
        "scripts/script_compare_hist1d.py --datafile Gamma_Energy --config hd_1x2x6 hd_1x2x6_centralAPA -c Transition -x RecoEnergy --labely 'Density' --labelx 'True Energy (MeV)' --percentile 11 99",
        "scripts/script_compare_hist1d.py --datafile Vertex_Smearing --config hd_1x2x6_centralAPA -c 'Coordinate' -x TrueCoordinate -y RecoCoordinate -o subtract --labelx 'True - Reco (cm)' --labely 'Density' --logy",
        "scripts/script_compare_hist1d.py --datafile Vertex_Smearing --config vd_1x8x14_3view_30deg_nominal -c 'Coordinate' -x TrueCoordinate -y RecoCoordinate -o subtract -p 3 93 --labelx 'True - Reco (cm)' --labely 'Density' --logy",
        "scripts/script_compare_hist2d.py --datafile Neutrino_CC_Production --config hd_1x2x6 -x SignalParticleK -y Energy --labelx 'True Neutrino Energy (MeV)' -i Particle -s Electron --labely 'True Electron Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_CC_Production --config hd_1x2x6 -x SignalParticleK -y Energy --labelx 'True Neutrino Energy (MeV)' -i Particle -s Gamma --labely 'True Gamma Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Charge_Lifetime_Correction --config hd_1x2x6 -x Time -y ChargePerEnergy -c Corrected -i '#Hits' -s 3.0 nan --logz --zoom",
        "scripts/script_compare_hist2d.py --datafile PrimaryEnergy_Electron_Calibration -c Calibrated -i '#Hits' -s 2 -x TrueEnergy -y RawEnergy --labelx 'True Electron Energy (MeV)' --labely 'Raw Electron Energy (MeV)' --diagonal --logz --zoom",
        "scripts/script_compare_hist2d.py --datafile CheatedEnergy_Electron_Calibration -i '#Hits' -s 3 -e 1 -x TrueEnergy -y RawEnergy --labelx 'True Electron Energy (MeV)' --labely 'Reconstructed Electron Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Vertex_Smearing -c 'Coordinate' -x TrueCoordinate -y RecoCoordinate --labelx 'True Coordinate (cm)' --labely 'Reconstructed Coordinate (cm)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Vertex_Smearing -i 'Coordinate' -s X Y Z -x TrueCoordinate -y RecoCoordinate --labelx 'True Coordinate (cm)' --labely 'Reconstructed Coordinate (cm)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile AdjCl_Selection -x AdjClR -y AdjClCharge -c Signal --labelx 'Vertex Distance (cm)' --labely 'Adjacent Cluster Charge (ADC x tick)' --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_Energy -x TrueEnergy -y RecoEnergy -c Variable --labelx 'True Neutrino Energy (MeV)' --labely 'Reconstructed Neutrino Energy (MeV)' --matchx --matchy --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_Energy -x TrueEnergy -y RecoEnergy -c Calibrated -s SelectedEnergy --labelx 'True Neutrino Energy (MeV)' --labely 'Reconstructed Neutrino Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_Energy --config hd_1x2x6_lateralAPA -x TrueEnergy -y RecoEnergy -s SelectedEnergy --entry 1 --labelx 'True Neutrino Energy (MeV)' --labely 'Reconstructed Neutrino Energy (MeV)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Neutrino_Energy --config vd_1x8x14_3view_30deg_nominal -x TrueEnergy -y RecoEnergy -s SelectedEnergy --entry 1 --labelx 'True Neutrino Energy (MeV)' --labely 'Reconstructed Neutrino Energy (MeV)' --diagonal --logz",
        "scripts/script_line_fit.py --datafile Charge_Correction_Factor --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -x Values -y Factor --labelx 'Number of Hits' --labely 'Correction Factor (ADC x tick / MeV)' -i Clustering -s '' --chi2 --errory",
        "scripts/script_line_fit.py --datafile ElectronCharge_Correction_Factor --config hd_1x2x6 vd_1x8x14_3view_30deg --name marley_official -x Values -y Factor --labelx 'Number of Hits' --labely 'Correction Factor (ADC x tick / MeV)' -i Clustering -s 'Electron' --chi2 --errory",
        "scripts/script_line_fit.py --datafile Electron_Energy_Resolution --name marley_official -x Values -y RMS --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True' -i Clustering Drift '#Hits' -s Ideal True 3 --errory --chi2",
        "scripts/script_line_fit.py --datafile Purity_Match_Resolution --config hd_1x2x6_centralAPA --name marley_official -x Values -y Counts --labelx 'True - Reco (cm)' --labely 'Counts' -i Coordinate -s X --debug --logy --rangex -20 20 --rangey 1 20000",
        "scripts/script_line_fit.py --datafile Purity_Match_Resolution --config vd_1x8x14_3view_30deg_nominal --name marley_official -x Values -y Counts --labelx 'True - Reco (cm)' --labely 'Counts' -i Coordinate -s X --debug --logy --rangex -20 20 --rangey 1 1000 --errory",
        "scripts/script_configuration_comparison.py --datafile Adjacent_Cluster_Distributions --configs hd_1x2x6_lateralAPA vd_1x8x14_3view_30deg_nominal -v AdjClMainE AdjClEnergy -y Counts -c Signal --labelx 'True Particle Energy (MeV)' 'Reconstructed Cluster Energy (MeV)' --labely 'Counts per Event' --logx --logy",
        "scripts/script_configuration_comparison.py --datafile TPC_Cluster_Efficiency_Drift_Scan -y Efficiency -x Coordinate --variables X -i Energy -s 6 --labelx 'Drift Coordinate (cm)' --labely 'TPC-PDS Matching Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile TPC_Cluster_Efficiency_Drift_Scan -y Efficiency -x Coordinate --variables X -i Energy -s 14 --labelx 'Drift Coordinate (cm)' --labely 'TPC-PDS Matching Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile TPC_Cluster_Efficiency_Drift_Scan --configs hd_1x2x6 hd_1x2x6_lateralAPA hd_1x2x6_centralAPA -y Efficiency -x Coordinate --variables X -i Energy -s 10 --labelx 'Drift Coordinate (cm)' --labely 'TPC-PDS Matching Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile TPC_Cluster_Efficiency_Drift_Scan --configs vd_1x8x14_3view_30deg vd_1x8x14_3view_30deg_nominal -y Efficiency -x Coordinate --variables X -i Energy -s 10 --labelx 'Drift Coordinate (cm)' --labely 'TPC-PDS Matching Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Inverse Reference -s   6 'False' Reco --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)' --rangex 10 190 --align left",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Inverse Reference -s  10 'False' Reco --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)' --rangex 10 190 --align left",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Inverse Reference -s  14 'False' Reco --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)' --rangex 10 190 --align left",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -i Energy Inverse Reference -s nan 'False' Reco --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)' --rangex 10 190 --align left",
        "scripts/script_configuration_comparison.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y -i Energy Inverse Reference -s nan 'False' Truth --labelx 'Fiducial Cut (cm)' --labely 'Reconstruction Efficiency (%)' --rangex 10 190 --align left",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma Tolerance -s 6 True 3 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma Tolerance -s 10 True 3 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma Tolerance -s 14 True 3 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -i Energy Sigma Tolerance -s nan True 3 --labelx 'True Drift Distance (cm)' 'True Y Coordinate (cm)' 'True Z Coordinate (cm)' --labely 'Reconstruction Efficiency (%)'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s Reco True 3 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s Ideal None 3 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s Ideal True 1 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Electron_Energy_Resolution -y RMS -i Clustering Drift '#Hits' -s Reco Reco 1 --labelx 'True Electron Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Neutrino_Energy_Resolution -y RMS -v TotalEnergy SelectedEnergy -i Drift '#Hits' -s Reco 3 --labelx 'True Neutrino Energy (MeV)' --labely 'RMS (True - Reco) / True'",
        "scripts/script_configuration_comparison.py --datafile Neutrino_Energy_Resolution -y RMS -v TotalEnergy SelectedEnergy SolarEnergy -i Drift '#Hits' -s Reco 3 --labelx 'True Neutrino Energy (MeV)' --labely 'RMS (True - Reco) / True'",
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
