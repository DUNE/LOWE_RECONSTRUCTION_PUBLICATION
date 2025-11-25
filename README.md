# DUNE Matplotlib Style Examples

Template repository for creating publication-quality plots for DUNE (Deep Underground Neutrino Experiment) using matplotlib with custom DUNE styling.

## Overview

This repository provides examples and templates for creating consistent, publication-ready plots following DUNE collaboration standards. It includes:

- **Custom DUNE matplotlib style** - Professional styling for scientific plots
- **Example scripts** - Demonstrations of common plot types
- **Template structure** - Organized directory layout for your analysis

## Quick Start

### Installation

1 Clone this repository:

```bash
git clone https://github.com/DUNE/matplotlib_dunestyle_examles.git
cd matplotlib_dunestyle_examles
```

2 Installation of required dependencies:

```bash
pip install -r requirements.txt
```

### Running Examples

After having installed the dune_plot_style repo. Run all examples at once:

```bash
python run_examples.py
```

Or run individual examples:

```bash
python styles/dune_plot_style*/examples/example_lineplot.py
python styles/dune_plot_style*/examples/example_histogram.py
python styles/dune_plot_style*/examples/example_errorbar.py
python styles/dune_plot_style*/examples/example_2dplot.py
python styles/dune_plot_style*/examples/example_multipanel.py
```

Output plots will be saved in the `plots/` directory.

## Using DUNE Style in Your Plots

To use the DUNE style in your own scripts:

```python
import os
import matplotlib.pyplot as plt

# Use DUNE style
import dunestyle.matplotlib as dunestyle

# Create your plot
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_xlabel('x [units]')
ax.set_ylabel('y [units]')
ax.set_title('My DUNE Plot')

# Save with high resolution
plt.savefig('plots/my_plot.png', dpi=300, bbox_inches='tight')
```

## Data Directory

Place your data files here. Supported formats:

- CSV (.csv)
- NumPy arrays (.npy, .npz)
- JSON (.json)
- HDF5 (.h5, .hdf5)
- ROOT files (.root)

### Example Data Structure

```code
data/
├── raw/           # Raw experimental data
├── processed/     # Processed data ready for plotting
└── simulated/     # Simulated/MC data
```

### Loading Data in Your Scripts

```python
import numpy as np
import pandas as pd

# Load CSV data
data = pd.read_csv('data/mydata.csv')

# Load numpy array
data = np.load('data/mydata.npy')
```

## Plots Output Directory

Generated plots will be saved here automatically when you run the example scripts.

All plots are saved with:

- High resolution (300 DPI) for publication quality
- PNG format with tight bounding boxes
- Consistent DUNE styling

You can also save plots in other formats by changing the extension:

- `.pdf` - Vector format, ideal for publications
- `.svg` - Scalable vector graphics
- `.eps` - Encapsulated PostScript
- `.jpg` - Compressed raster format

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
