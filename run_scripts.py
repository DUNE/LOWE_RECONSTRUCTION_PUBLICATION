#!/usr/bin/env python3
"""
Run all example plots
"""

import sys
import os
import importlib.util
from itertools import product

def run_example(script_path):
    """Run a single example script"""
    script_name = os.path.basename(script_path)
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")
    # Load and run the module
    spec = importlib.util.spec_from_file_location("script", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Run main if it exists
    if hasattr(module, 'main'):
        module.main()


def main():
    # Get the examples directory
    examples_dir = os.path.join(os.path.dirname(__file__), 'scripts')

    # Find all example scripts
    example_scripts = sorted([
        os.path.join(examples_dir, f)
        for f in os.listdir(examples_dir)
        if f.startswith('script_') and f.endswith('.py')
    ])


    if not example_scripts:
        print("No example scripts found!")
        return

    print(f"Found {len(example_scripts)} script(s)")

    # Run each example
    for script_path in example_scripts:
        try:
            run_example(script_path)
        except Exception as e:
            print(f"Error running {os.path.basename(script_path)}: {e}")
            continue


    print(f"\n{'='*60}")
    print("All examples completed!")
    print(f"Check the 'plots/' directory for output files")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
