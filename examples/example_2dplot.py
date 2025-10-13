#!/usr/bin/env python3
"""
Example 4: 2D Heatmap/Contour Plot
Demonstrates 2D data visualization typical for detector responses
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Use DUNE style
plt.style.use(os.path.join(os.path.dirname(__file__), '..', 'styles', 'dunestyle.mplstyle'))

def main():
    # Generate sample 2D data (e.g., detector response)
    np.random.seed(42)
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X**2 + Y**2) / 10) * np.cos(X) * np.sin(Y)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Heatmap
    im1 = ax1.pcolormesh(X, Y, Z, shading='auto', cmap='viridis')
    ax1.set_xlabel('x position [cm]')
    ax1.set_ylabel('y position [cm]')
    ax1.set_title('Heatmap: Detector Response')
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Signal Strength [a.u.]')
    
    # Contour plot
    levels = np.linspace(Z.min(), Z.max(), 15)
    cs = ax2.contour(X, Y, Z, levels=levels, cmap='viridis')
    ax2.clabel(cs, inline=True, fontsize=8)
    ax2.set_xlabel('x position [cm]')
    ax2.set_ylabel('y position [cm]')
    ax2.set_title('Contour: Detector Response')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'example_2dplot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    
    # Display
    plt.show()

if __name__ == '__main__':
    main()
