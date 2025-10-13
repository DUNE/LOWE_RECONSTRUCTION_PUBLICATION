#!/usr/bin/env python3
"""
Run all example plots
"""

import sys
import os
import importlib.util

DUNE_PLOT_STYLE_LATEST_TAG = os.getenv('DUNE_PLOT_STYLE_LATEST_TAG')  # Added line to get the environment variable
sys.path.append(f'styles/dune_plot_style-{DUNE_PLOT_STYLE_LATEST_TAG}/examples/matplotlib')

def run_example(script_path):
    """Run a single example script"""
    script_name = os.path.basename(script_path)
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")
    
    # Change to the previous script's directory to ensure relative imports work
    prev_script_dir = os.path.dirname(script_path)
    os.chdir(prev_script_dir.rsplit('/', 1)[0])
    # Create a 'images' directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    os.chdir('images')
    # Execute the script
    os.system(f'python3 {script_path}')


def main():
    # Get the examples directory
    examples_dir = os.path.join(os.path.dirname(__file__), f'styles/dune_plot_style-{DUNE_PLOT_STYLE_LATEST_TAG}/examples/matplotlib')
    
    # Find all example scripts
    example_scripts = sorted([
        os.path.join(examples_dir, f)
        for f in os.listdir(examples_dir)
        if f.startswith('example') and f.endswith('.py')
    ])
    
    if not example_scripts:
        print("No example scripts found!")
        return
    
    print(f"Found {len(example_scripts)} example(s)")
    
    # Run each example
    for script_path in example_scripts:
        try:
            run_example(script_path)
        except Exception as e:
            print(f"Error running {os.path.basename(script_path)}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print("All examples completed!")
    print(f"Check the '{script_path.rsplit('/', 1)[0]}/images' directory for output files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
