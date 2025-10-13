#!/usr/bin/env python3
"""
Example 1: Simple Line Plot with DUNE Style
Demonstrates basic line plotting with custom styling
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Use DUNE style
plt.style.use(os.path.join(os.path.dirname(__file__), '..', 'styles', 'dunestyle.mplstyle'))

def main():
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.exp(-x/10)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot data
    ax.plot(x, y1, label='sin(x)', linewidth=2)
    ax.plot(x, y2, label='cos(x)', linewidth=2)
    ax.plot(x, y3, label='sin(x) * exp(-x/10)', linewidth=2, linestyle='--')
    
    # Add labels and title
    ax.set_xlabel('x [arbitrary units]')
    ax.set_ylabel('y [arbitrary units]')
    ax.set_title('DUNE Style Example: Oscillating Functions')
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'example_lineplot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    
    # Display
    plt.show()

if __name__ == '__main__':
    main()
