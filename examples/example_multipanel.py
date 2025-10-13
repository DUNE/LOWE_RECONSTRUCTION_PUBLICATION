#!/usr/bin/env python3
"""
Example 5: Multi-Panel Plot
Demonstrates creating complex figures with multiple subplots
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Use DUNE style
plt.style.use(os.path.join(os.path.dirname(__file__), '..', 'styles', 'dunestyle.mplstyle'))

def main():
    # Generate sample data
    np.random.seed(42)
    x = np.linspace(0, 10, 100)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Subplot 1: Line plot
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(x, np.sin(x), 'b-', linewidth=2)
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Signal Waveform')
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Histogram
    ax2 = fig.add_subplot(gs[0, 1])
    data = np.random.normal(100, 15, 1000)
    ax2.hist(data, bins=30, alpha=0.7, color='C1', edgecolor='black')
    ax2.set_xlabel('Energy [MeV]')
    ax2.set_ylabel('Events')
    ax2.set_title('Energy Distribution')
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Scatter plot
    ax3 = fig.add_subplot(gs[1, 0])
    x_scatter = np.random.normal(0, 1, 100)
    y_scatter = x_scatter + np.random.normal(0, 0.5, 100)
    ax3.scatter(x_scatter, y_scatter, alpha=0.6, s=50, c='C2', edgecolors='black', linewidths=0.5)
    ax3.set_xlabel('Variable 1')
    ax3.set_ylabel('Variable 2')
    ax3.set_title('Correlation Plot')
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Bar plot
    ax4 = fig.add_subplot(gs[1, 1])
    categories = ['Cat A', 'Cat B', 'Cat C', 'Cat D']
    values = [25, 40, 30, 45]
    errors = [3, 5, 4, 6]
    ax4.bar(categories, values, yerr=errors, capsize=5, alpha=0.7, 
            color='C3', edgecolor='black', ecolor='black')
    ax4.set_ylabel('Count')
    ax4.set_title('Category Comparison')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add overall title
    fig.suptitle('DUNE Style Example: Multi-Panel Analysis', fontsize=16, y=0.995)
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'example_multipanel.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    
    # Display
    plt.show()

if __name__ == '__main__':
    main()
