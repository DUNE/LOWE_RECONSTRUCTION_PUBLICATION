# Data Directory

Place your data files here. Supported formats:
- CSV (.csv)
- NumPy arrays (.npy, .npz)
- JSON (.json)
- HDF5 (.h5, .hdf5)
- ROOT files (.root)

## Example Data Structure

```
data/
├── raw/           # Raw experimental data
├── processed/     # Processed data ready for plotting
└── simulated/     # Simulated/MC data
```

## Loading Data in Your Scripts

```python
import numpy as np
import pandas as pd

# Load CSV data
data = pd.read_csv('data/mydata.csv')

# Load numpy array
data = np.load('data/mydata.npy')
```
