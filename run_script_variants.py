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
        "scripts/script_iterable_scan.py --datafile NHit_Distributions --name marley_official -v SignalParticleK",
        "scripts/script_iterable_scan.py --datafile Background -y Counts -x Energy --iterables PDG Particle --labely 'Counts per Energy 1/(kT·years·MeV)' --logy",
        "scripts/script_iterable_scan.py --name marley_official --datafile Cumulative_Vertex_Error -y Error -x Values --iterables Energy -v X Y Z --labelx 'Vertex Error (cm)' --labely 'Sample Size (%)' --logx",
        "scripts/script_preselection_efficiency.py",
        "scripts/script_clustering_efficiency.py --logy",
        "scripts/script_adjcluster_comparison.py --logx --logy",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c Corrected -i '#Hits' --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c Corrected -i '#Hits' --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)' -s 1 2 3",
        "scripts/script_compare_hist1d.py --datafile Charge_Lifetime_Correction -x ChargePerEnergy -c '#Hits' --percentile 1 90 --labely 'Density' --labelx 'TPC Conversion Factor (ADC x tick / MeV)'",
        "scripts/script_compare_hist2d.py --datafile Charge_Lifetime_Correction -x Time -y ChargePerEnergy -c Corrected -i '#Hits' --logz  --zoom",
        "scripts/script_compare_hist1d.py --datafile PrimaryEnergy_Electron_Calibration -c Calibrated -i '#Hits' -s 2 -x TrueEnergy -y RawEnergy --labely 'Density' --labelx 'True - Reco Energy (MeV)' --percentile 1 90",
        "scripts/script_compare_hist2d.py --datafile PrimaryEnergy_Electron_Calibration -c Calibrated -i '#Hits' -s 2 -x TrueEnergy -y RawEnergy --labelx 'True Electron Energy (MeV)' --labely 'Raw Electron Energy (MeV)' --diagonal --logz --zoom",
        "scripts/script_compare_hist2d.py --datafile Vertex_Smearing -c 'Coordinate' -x TrueCoordinate -y RecoCoordinate --labelx 'True Coordinate (cm)' --labely 'Reconstructed Coordinate (cm)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile Vertex_Smearing -i 'Coordinate' -s X Y Z -x TrueCoordinate -y RecoCoordinate --labelx 'True Coordinate (cm)' --labely 'Reconstructed Coordinate (cm)' --diagonal --logz",
        "scripts/script_compare_hist2d.py --datafile AdjCl_Selection -x AdjClR -y AdjClCharge -c Signal --labelx 'Vertex Distance (cm)' --labely 'Adjacent Cluster Charge (ADC x tick)' --logz",
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
