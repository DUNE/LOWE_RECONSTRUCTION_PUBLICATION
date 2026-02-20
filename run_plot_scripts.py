
#!/usr/bin/env python3

"""
Run all example plots
"""

import sys
import os
import argparse

from itertools import product
from rich import print as rprint

# Add debug and show flags to run_all.py
parser = argparse.ArgumentParser(description='Run all scripts with debug output.')
parser.add_argument('-s', '--scripts', type=str, default='all', help='Specific name of source script to run (default: all)')
parser.add_argument('-p', '--plot', action='store_true', help='Show plots after running scripts')
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
args = parser.parse_args()

def run_script(script_name):
    script_name = ' '.join(script_name.split())  # Remove extra spaces
    rprint(f"\n[cyan]Running[/cyan] {script_name}")
    result = os.system(f"python {script_name}")
    if result != 0:
        rprint(f"[red]Error:[/red] {script_name} failed to execute.")
    return result

if __name__ == "__main__":
    # Read txt file with list of scripts to run in scripts/{args.scripts}_scripts.txt
    script_file = os.path.join("scripts", f"{args.scripts}_scripts.txt")
    if os.path.isfile(script_file):
        with open(script_file, 'r') as f:
            scripts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        rprint(f"[red]Error:[/red] Script file {script_file} not found.")
        sys.exit(1)

    all_results = []
    for script_name in scripts:
        if args.scripts != 'all':
            if args.scripts == "thesis":
                script_name += " -o '/home/smanthey/Code/THESIS/figures/'"
            else:
                rprint(f"[red]Error:[/red] Unknown script set {args.scripts}.")
        if args.plot:
            script_name += " -p"
        if args.debug:
            script_name += " -d"

        this_result = run_script(script_name)
        
        if this_result != 0:
            script_name = ' '.join(script_name.split())  # Remove extra spaces
            rprint(f"Script {script_name} failed. Exiting.")
        
        all_results.append(this_result)

    if sum(all_results) == 0:
        rprint("\n[green]All scripts executed successfully![/green]")
    else:
        for i, result in enumerate(all_results):
            if result != 0:
                rprint(f"[red]Error:[/red] {' '.join(scripts[i].split())}")
