#!/usr/bin/env python3

"""
Run all example plots
"""

import sys
import os
import argparse
import json
import shlex
import subprocess

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
    captured_lines = []
    proc = subprocess.Popen(
        [sys.executable] + shlex.split(script_name),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in proc.stdout:
        sys.stdout.write(line)
        captured_lines.append(line)
    proc.wait()
    captured_output = "".join(captured_lines).strip()
    return proc.returncode, captured_output


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

    # Each entry: (original_script_line, exit_code, captured_output)
    run_records = []
    for script_name in scripts:
        external_outputs = output_paths.get(args.scripts) or []
        # Ensure external_outputs is a list
        if not isinstance(external_outputs, list):
            external_outputs = [external_outputs]

        full_script = script_name
        if (
            external_outputs
            and " -o " not in full_script
            and " --output " not in full_script
        ):
            output_args = " ".join([shlex.quote(path) for path in external_outputs])
            full_script += f" -o {output_args}"
        if args.plot:
            full_script += " -p"
        if args.debug:
            full_script += " -d"

        exit_code, captured_output = run_script(full_script)

        if exit_code != 0:
            rprint(f"[yellow]Script failed (exit {exit_code}):[/yellow] {' '.join(script_name.split())}")

        run_records.append((script_name, exit_code, captured_output))

    if all(r[1] == 0 for r in run_records):
        rprint("\n[green]All scripts executed successfully![/green]")
    else:
        rprint("\n[red]--- Failed scripts summary ---[/red]")
        for original_cmd, result, output in run_records:
            if result != 0:
                rprint(f"\n[red]Error (exit {result}):[/red] {' '.join(original_cmd.split())}")
                if output:
                    last_lines = "\n".join(output.splitlines()[-10:])
                    rprint(f"[dim]{last_lines}[/dim]")
