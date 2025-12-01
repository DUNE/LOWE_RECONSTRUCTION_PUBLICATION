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
        "scripts/script_mean_table.py --datafile Adjacent_Cluster_Counts -y AdjClNum --variables Signal 'Intrinsic' 'External' -i Distance -s 20 -t Source --emph 0",
        "scripts/script_mean_table.py --datafile Adjacent_Cluster_Counts -y AdjClNum --variables Signal 'Intrinsic' 'External' -i Distance -s 100 -t Source --emph 0",
        "scripts/script_mean_table.py --datafile Fiducial_Efficiency -y Efficiency --variables X Y Z -t Coordinate -i Energy Inverse Reference -s 10 'False' Reco --emph 0",
        "scripts/script_mean_table.py --datafile Vertex_Reconstruction_Efficiency -y Efficiency --variables X Y Z -t Coordinate -i Energy Sigma Tolerance -s 10 True 3 --emph 0",
        "scripts/script_mean_table.py --datafile Neutrino_Energy_Resolution -y RMS --variables TotalEnergy SelectedEnergy -t Algorithm -i Drift '#Hits' -s Reco 3 --emph 0",
        # "scripts/script_mean_table.py --datafile Neutrino_Energy_Resolution -y RMS --variables '#Hits' -t Algorithm -i Drift Variable -s Reco SelectedEnergy --emph 0",
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
