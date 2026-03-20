#!/usr/bin/env python3

"""
Run all example plots
"""

import sys
import os
import argparse
import json
import shlex

from rich import print as rprint

# Add debug and show flags to run_all.py
parser = argparse.ArgumentParser(description="Run all scripts with debug output.")
parser.add_argument(
    "-s",
    "--scripts",
    type=str,
    default="all",
    help="Specific name of source script to run (default: all)",
)
parser.add_argument(
    "-p", "--plot", action="store_true", help="Show plots after running scripts"
)
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
args = parser.parse_args()


def load_output_paths(kind):
    config_file = os.path.join("config", "output_paths.json")
    if not os.path.isfile(config_file):
        return {}

    with open(config_file, "r") as f:
        config = json.load(f)

    return config.get(kind, {})


def run_script(script_name):
    script_name = " ".join(script_name.split())  # Remove extra spaces
    rprint(f"\n[cyan]Running[/cyan] {script_name}")
    result = os.system(f"python {script_name}")
    if result != 0:
        rprint(f"[red]Error:[/red] {script_name} failed to execute.")
    return result


if __name__ == "__main__":
    output_paths = load_output_paths("plots")

    # Read txt file with list of scripts to run in input/plots/{args.scripts}_scripts.txt
    script_file = os.path.join("input", "plots", f"{args.scripts}_scripts.txt")
    if os.path.isfile(script_file):
        with open(script_file, "r") as f:
            scripts = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    else:
        rprint(f"[red]Error:[/red] Script file {script_file} not found.")
        sys.exit(1)

    all_results = []
    for script_name in scripts:
        external_output = output_paths.get(args.scripts)
        if (
            external_output is not None
            and " -o " not in script_name
            and " --output " not in script_name
        ):
            script_name += f" -o {shlex.quote(external_output)}"
        if args.plot:
            script_name += " -p"
        if args.debug:
            script_name += " -d"

        this_result = run_script(script_name)

        if this_result != 0:
            script_name = " ".join(script_name.split())  # Remove extra spaces
            rprint(f"Script {script_name} failed. Exiting.")

        all_results.append(this_result)

    if sum(all_results) == 0:
        rprint("\n[green]All scripts executed successfully![/green]")
    else:
        for i, result in enumerate(all_results):
            if result != 0:
                rprint(f"[red]Error:[/red] {' '.join(scripts[i].split())}")
