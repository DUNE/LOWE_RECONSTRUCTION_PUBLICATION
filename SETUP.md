# Setup and Installation Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/DUNE/matplotlib_dunestyle_examles.git
cd matplotlib_dunestyle_examles
```

### 2. Create a Virtual Environment (Recommended)

#### Using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Using conda:
```bash
conda create -n dune-plots python=3.9
conda activate dune-plots
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Test the installation by running an example:

```bash
python examples/example_lineplot.py
```

You should see a message indicating the plot was saved, and the file should appear in `plots/example_lineplot.png`.

## Troubleshooting

### Common Issues

#### "No module named matplotlib"
Solution: Make sure you've activated your virtual environment and installed requirements.

```bash
pip install -r requirements.txt
```

#### Display Issues
If you're running on a headless server or encounter display-related errors:

```bash
export MPLBACKEND=Agg  # Linux/Mac
set MPLBACKEND=Agg     # Windows
```

Or add this to the beginning of your Python scripts:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

#### Permission Errors
If you encounter permission errors when saving plots:

```bash
chmod 755 plots/
```

## Using This Template for Your Project

### Option 1: Use as Template on GitHub

1. Click "Use this template" on GitHub
2. Create your new repository
3. Clone your new repository
4. Start adding your analysis scripts

### Option 2: Fork the Repository

1. Fork this repository on GitHub
2. Clone your fork
3. Add your changes
4. Push to your fork

### Option 3: Download and Customize

1. Download the repository as ZIP
2. Extract to your project directory
3. Remove the `.git` folder if starting fresh
4. Initialize your own git repository

## Next Steps

1. Review the examples in `examples/` directory
2. Copy an example that's closest to your needs
3. Modify it for your data and analysis
4. Place your data files in `data/` directory
5. Run your script to generate plots in `plots/` directory

## Additional Resources

- [Matplotlib Documentation](https://matplotlib.org/stable/index.html)
- [NumPy Documentation](https://numpy.org/doc/stable/)
- [DUNE Collaboration Website](https://www.dunescience.org/)
