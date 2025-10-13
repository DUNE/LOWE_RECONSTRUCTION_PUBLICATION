# DUNE Matplotlib Style Examples

Template repository for creating publication-quality plots for DUNE (Deep Underground Neutrino Experiment) using matplotlib with custom DUNE styling.

## Overview

This repository provides examples and templates for creating consistent, publication-ready plots following DUNE collaboration standards. It includes:

- **Custom DUNE matplotlib style** - Professional styling for scientific plots
- **Example scripts** - Demonstrations of common plot types
- **Template structure** - Organized directory layout for your analysis

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone https://github.com/DUNE/matplotlib_dunestyle_examles.git
cd matplotlib_dunestyle_examles
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running Examples

Run all examples at once:
```bash
python run_examples.py
```

Or run individual examples:
```bash
python examples/example_lineplot.py
python examples/example_histogram.py
python examples/example_errorbar.py
python examples/example_2dplot.py
python examples/example_multipanel.py
```

Output plots will be saved in the `plots/` directory.

## Repository Structure

```
matplotlib_dunestyle_examles/
├── examples/           # Example plotting scripts
│   ├── example_lineplot.py      # Basic line plots
│   ├── example_histogram.py     # Histograms for distributions
│   ├── example_errorbar.py      # Data with uncertainties
│   ├── example_2dplot.py        # 2D heatmaps and contours
│   └── example_multipanel.py    # Multi-panel figures
├── styles/            # Matplotlib style configurations
│   └── dunestyle.mplstyle      # DUNE plot style
├── data/              # Place your data files here
├── plots/             # Output directory for generated plots
├── requirements.txt   # Python dependencies
└── run_examples.py    # Script to run all examples
```

## Using DUNE Style in Your Plots

To use the DUNE style in your own scripts:

```python
import matplotlib.pyplot as plt
import os

# Load DUNE style
style_path = 'styles/dunestyle.mplstyle'
plt.style.use(style_path)

# Create your plot
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_xlabel('x [units]')
ax.set_ylabel('y [units]')
ax.set_title('My DUNE Plot')

# Save with high resolution
plt.savefig('plots/my_plot.png', dpi=300, bbox_inches='tight')
```

## Examples Included

### 1. Line Plot (`example_lineplot.py`)
Demonstrates basic line plotting with multiple series, legends, and labels.

### 2. Histogram (`example_histogram.py`)
Shows how to create histograms for distributions, typical in physics analyses.

### 3. Error Bars (`example_errorbar.py`)
Illustrates plotting data points with uncertainties in both x and y directions.

### 4. 2D Plots (`example_2dplot.py`)
Creates heatmaps and contour plots for 2D data visualization.

### 5. Multi-Panel Plots (`example_multipanel.py`)
Demonstrates creating complex figures with multiple subplots.

## DUNE Style Features

The DUNE matplotlib style includes:

- **High-quality output**: 300 DPI for publications
- **Professional fonts**: Clear, readable sans-serif fonts
- **Grid lines**: Light grid for easy data reading
- **Tick marks**: Inward-pointing ticks on all sides
- **Color scheme**: Consistent, colorblind-friendly colors
- **Legend styling**: Clean, unobtrusive legends

## Customization

You can customize the style by editing `styles/dunestyle.mplstyle`. Common modifications:

- **Figure size**: Change `figure.figsize`
- **Font sizes**: Adjust `font.size`, `axes.labelsize`, etc.
- **Colors**: Modify `axes.prop_cycle`
- **Grid appearance**: Edit `grid.alpha`, `grid.linestyle`

## Contributing

To add new examples or improve existing ones:

1. Create your example script in the `examples/` directory
2. Follow the naming convention: `example_<description>.py`
3. Include docstrings and comments
4. Make sure output is saved to `plots/`

## References

- [DUNE Plot Style Repository](https://github.com/DUNE/dune_plot_style)
- [Matplotlib Documentation](https://matplotlib.org/stable/index.html)
- [DUNE Collaboration](https://www.dunescience.org/)

## License

See LICENSE file for details.
