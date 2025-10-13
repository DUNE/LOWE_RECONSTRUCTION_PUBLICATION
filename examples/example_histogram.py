#!/usr/bin/env python3
"""
Example 2: Histogram with DUNE Style
Demonstrates histogram plotting typical for physics analyses
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Use DUNE style
plt.style.use(os.path.join(os.path.dirname(__file__), '..', 'styles', 'dunestyle.mplstyle'))

def main():
    # Generate sample data (e.g., energy distributions)
    np.random.seed(42)
    signal = np.random.normal(100, 15, 1000)
    background = np.random.exponential(50, 1500)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot histograms
    bins = np.linspace(0, 200, 50)
    ax.hist(background, bins=bins, alpha=0.7, label='Background', color='C1', edgecolor='black')
    ax.hist(signal, bins=bins, alpha=0.7, label='Signal', color='C0', edgecolor='black')
    
    # Add labels and title
    ax.set_xlabel('Energy [MeV]')
    ax.set_ylabel('Events')
    ax.set_title('DUNE Style Example: Energy Distribution')
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'example_histogram.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    
    # Display
    plt.show()

if __name__ == '__main__':
    main()
