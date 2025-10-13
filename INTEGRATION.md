# Integration with dune_plot_style

This repository provides standalone matplotlib styling for DUNE plots. However, if you want to use the official [dune_plot_style](https://github.com/DUNE/dune_plot_style) package, you can easily integrate it.

## Installing dune_plot_style

```bash
pip install git+https://github.com/DUNE/dune_plot_style.git
```

## Using dune_plot_style with These Examples

You can modify any example script to use the official dune_plot_style:

```python
#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

# Option 1: Use official dune_plot_style (if installed)
try:
    import dune_plot_style as dps
    dps.set_style()
except ImportError:
    # Option 2: Fallback to local dunestyle
    import os
    style_path = os.path.join(os.path.dirname(__file__), '..', 'styles', 'dunestyle.mplstyle')
    plt.style.use(style_path)

# Your plotting code here
x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x, y)
ax.set_xlabel('x [units]')
ax.set_ylabel('y [units]')
ax.set_title('My Plot')

plt.savefig('plots/my_plot.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Differences

### Local Style (dunestyle.mplstyle)
- Standalone, no external dependencies
- Customizable directly in this repository
- Good for quick start and learning

### Official dune_plot_style Package
- Official DUNE collaboration styling
- May include additional utilities and functions
- Stays up-to-date with DUNE standards
- May have more features and consistency checks

## Recommendation

- **For beginners or quick prototyping**: Use the local `dunestyle.mplstyle`
- **For official publications**: Consider using the official `dune_plot_style` package
- **For custom needs**: Modify the local style to suit your specific requirements

## Customizing the Local Style

The local DUNE style is defined in `styles/dunestyle.mplstyle`. You can customize:

1. **Colors**: Edit the `axes.prop_cycle` line
2. **Font sizes**: Adjust `font.size`, `axes.labelsize`, etc.
3. **Figure size**: Change `figure.figsize`
4. **Grid appearance**: Modify `grid.alpha`, `grid.linestyle`

Example customization:

```python
# In your script, after loading the style
plt.rcParams['figure.figsize'] = (10, 8)  # Larger figures
plt.rcParams['font.size'] = 14  # Bigger fonts
```

## Contributing

If you find differences between this local style and the official dune_plot_style that should be synchronized, please open an issue or pull request.
