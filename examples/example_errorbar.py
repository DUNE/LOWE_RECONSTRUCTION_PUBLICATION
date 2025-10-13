#!/usr/bin/env python3
"""
Example 3: Scatter Plot with Error Bars
Demonstrates data points with uncertainties, common in experimental physics
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Use DUNE style
plt.style.use(os.path.join(os.path.dirname(__file__), '..', 'styles', 'dunestyle.mplstyle'))

def main():
    # Generate sample data with uncertainties
    np.random.seed(42)
    x = np.linspace(0, 10, 20)
    y_true = 2 * x + 5
    y_measured = y_true + np.random.normal(0, 2, len(x))
    y_errors = np.random.uniform(1, 3, len(x))
    x_errors = np.random.uniform(0.2, 0.5, len(x))
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot data with error bars
    ax.errorbar(x, y_measured, yerr=y_errors, xerr=x_errors, 
                fmt='o', capsize=5, capthick=2, label='Measured Data',
                markersize=8, elinewidth=2)
    
    # Plot true line
    ax.plot(x, y_true, 'r--', linewidth=2, label='True Relation: y = 2x + 5')
    
    # Add labels and title
    ax.set_xlabel('Independent Variable [units]')
    ax.set_ylabel('Dependent Variable [units]')
    ax.set_title('DUNE Style Example: Measurements with Uncertainties')
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'example_errorbar.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    
    # Display
    plt.show()

if __name__ == '__main__':
    main()
