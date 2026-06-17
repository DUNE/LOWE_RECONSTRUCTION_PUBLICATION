# Plotting Macros: Syntax & Functionality Inconsistencies Review

**Date:** 2026-05-22  
**Scope:** All `scripts/script_*.py` plotting macros and `src/lib/plot.py`

## Summary

Found **5 major inconsistency categories** affecting code maintainability and DRY principle violations:

| Issue | Severity | Scripts Affected | Count |
|-------|----------|------------------|-------|
| Unused utility functions | High | hist1d, hist2d, line_operation, line_fit | 4 |
| Duplicated label placement code | High | hist1d, hist2d, line_operation, line_fit | 12 instances |
| Duplicated `_resolve_plot_kwargs` | Medium | reduce, line_fit | 2 definitions |
| Inconsistent label mapping naming | Medium | configuration, line_operation, iterable_scan | 3 functions |
| Missing utility usage | Medium | contour, comparison, iterable_scan | Optional |

---

## Issue 1: Unused Utility Functions in plot.py

**Severity:** HIGH

### Details
`src/lib/plot.py` provides sophisticated label placement functions that are **not used** in most scripts:

- `place_vertical_label()` (line 521-686)
- `place_horizontal_label()` (line 689-832)

These handle intelligent positioning to avoid overlapping with legends and plot content.

### Current Usage vs. Manual Implementation

| Script | Current Implementation | Should Use |
|--------|------------------------|------------|
| `script_compare_hist1d.py:310-317` | Manual offset calculation | `place_vertical_label()` |
| `script_compare_hist2d.py:274-282` | Manual offset calculation | `place_vertical_label()` |
| `script_compare_line_operation.py:1032-1043` | Manual offset calculation | `place_vertical_label()` |
| `script_line_fit.py:445-456` | Manual offset calculation | `place_vertical_label()` |
| `script_iterable_scan.py:593-596` | ✓ Already uses correctly | N/A |

### Example Code Duplication

**Hist1d (lines 310-317):**
```python
if vertical_label is not None:
    xlim = ax_current.get_xlim()
    ylim = ax_current.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    x_offset = x_range * 0.02
    y_offset = y_range * 0.55
    ax_current.text(vertical + x_offset, ylim[1] - y_offset, vertical_label, ...)
```

**Utility function (plot.py:675-686):**
```python
def place_vertical_label(ax, x_value, label_text, fontsize=None, pad_fraction=0.02):
    # Handles all positioning logic automatically
```

### Impact
- 4 scripts use **identical boilerplate code** instead of tested utility
- Utility function performs **intelligent positioning** (avoids legend overlap)
- Manual code uses **fixed offsets** (0.02, 0.55) that may fail with different data ranges

---

## Issue 2: Duplicated Label Placement Code Across Scripts

**Severity:** HIGH

### Pattern: Vertical Line Labels (4 occurrences)

All four scripts duplicate this pattern with minor variations:

```
Hist1d:         lines 310-317
Hist2d:         lines 274-282
LineOperation:  lines 1032-1043
LineFit:        lines 445-456
```

**Common logic:**
1. Get axis limits
2. Calculate x/y range
3. Apply fixed offset multipliers (0.02, 0.55)
4. Place text with manual coordinates

### Pattern: Horizontal Line Labels (2 occurrences)

```
Hist1d:         lines 319-325
Hist2d:         lines 284-290
LineOperation:  lines 1045-1051
LineFit:        lines 458-464
```

**Identical offsets across all:** `x_offset = x_range * 0.05`

### Pattern: Point Scatter Labels (4 occurrences)

```
Hist1d:         lines 334-344
Hist2d:         lines 299-309
LineOperation:  lines 1060-1070
LineFit:        lines 473-483
```

**Identical code block:**
```python
for point_idx, (point_x, point_y) in enumerate(point_values):
    ax_current.scatter(point_x, point_y, color="gray", s=40, zorder=6)
    if point_labels is not None:
        xlim = ax_current.get_xlim()
        ylim = ax_current.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        x_offset = x_range * 0.02
        y_offset = y_range * 0.03
        ax_current.text(...)
```

### Maintenance Risk
- Bug fix in one location requires updates in **4 separate files**
- Inconsistent behavior if edits are missed in some scripts
- Harder to improve positioning logic globally

---

## Issue 3: Duplicated `_resolve_plot_kwargs` Function

**Severity:** MEDIUM

### Details

Function defined identically in TWO scripts:

**script_compare_reduction.py:105-113**
```python
def _resolve_plot_kwargs(selected_plot_type):
    if selected_plot_type == "step":
        return {
            "plot_type": "plot",
            "drawstyle": "steps-mid",
        }
    return {
        "plot_type": selected_plot_type,
    }
```

**script_line_fit.py:344-352**
```python
def _resolve_plot_kwargs(selected_plot_type):
    if selected_plot_type == "step":
        return {
            "plot_type": "plot",
            "drawstyle": "steps-mid",
        }
    return {
        "plot_type": selected_plot_type,
    }
```

### Impact
- Identical logic means any enhancement needs dual updates
- Hidden dependency between scripts
- Should be centralized in `common_args.py` or `src/lib/`

---

## Issue 4: Inconsistent Label Mapping Function Naming

**Severity:** MEDIUM

### Pattern Inconsistency

Three similar functions with different names and locations:

| Function | Location | Name Pattern | Issue |
|----------|----------|--------------|-------|
| `map_iterable_label` | script_compare_configuration.py:325 | CamelCase | ✓ |
| `_map_iterable_label` | script_compare_line_operation.py:238 | Private with leading underscore | ⚠️ Inconsistent |
| `map_iterable_label` | script_iterable_scan.py:142 | CamelCase | ✓ |

### Code Comparison

**Configuration (lines 325-362):**
```python
def map_iterable_label(iterable_value, iterable_name, mapping_name, unique_iterables_count):
    mapped_value = iterable_value
    # Handles PDG particle dict, Plane dict lookups
    if mapping_name is not None:
        mapping_dict = get_mapping_dict(mapping_name)
        # ...
    return mapped_value
```

**LineOperation (lines 238-257):**
```python
def _map_iterable_label(iterable_name, raw_value, n_unique):
    mapped_value = raw_value
    # Same logic, different parameter order & naming
    if iterable_name == "PDG":
        mapped_value = particle_dict.get(int(raw_value), str(raw_value))
    # ...
    return str(mapped_value)
```

### Key Differences
1. Parameter order differs (`value, iterable_name` vs `iterable_name, value`)
2. Naming: `iterable_value` vs `raw_value`, `mapping_name` vs none
3. Return type: implicit vs explicit `str()`
4. Access pattern: `get_mapping_dict()` vs direct dict access

### Risk
- Functions appear different but serve same purpose
- Developers may duplicate instead of reuse
- Hard to maintain consistent behavior across scripts

---

## Issue 5: Syntax Inconsistencies in Common Patterns

**Severity:** LOW

### Condition Checking

**Inconsistent None checks:**
```python
# Hist1d line 213
if args.horizontal != None:

# Hist2d line 213  
if args.horizontal != None:

# Line Operation line 1032
if horizontal is not None:

# Line Fit line 445
if horizontal is not None:
```

Should use consistent `is None` / `is not None` (PEP 8 compliant).

### Variable Naming Conventions

**Inconsistent prefix usage:**
- `jdx` (j-index in hist1d/hist2d) vs `sdx` (s-index in line_operation)
- `kdx` (k-index) used universally for config iteration ✓
- `idx` (i-index) used universally for variable iteration ✓
- `jdx` used inconsistently for iterable iteration

### Import Organization

**Inconsistent import order:**
```python
# Hist1d: imports in specific order
from lib import *
from lib.selection import filter_dataframe
from lib.exports import make_name_from_args, save_figure_to_paths
from lib.format import make_subtitle_from_args, make_title_from_args

# Line Fit: partially uses direct imports, partially uses *
from lib import *
from lib.selection import filter_dataframe
```

---

## Recommendations

### Priority 1: Migrate Label Placement Code (High Impact)

**Action:** Refactor 4 scripts to use utility functions

```python
# BEFORE (Hist1d, Hist2d, LineOperation, LineFit)
if vertical_label is not None:
    xlim = ax_current.get_xlim()
    ylim = ax_current.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    x_offset = x_range * 0.02
    y_offset = y_range * 0.55
    ax_current.text(vertical + x_offset, ylim[1] - y_offset, vertical_label, ...)

# AFTER
if vertical_label is not None:
    place_vertical_label(ax_current, vertical, vertical_label, fontsize=linelabelfontsize)
```

**Files to update:**
- `script_compare_hist1d.py:308-317`
- `script_compare_hist2d.py:273-282`
- `script_compare_line_operation.py:1032-1043`
- `script_line_fit.py:445-456`

**Same for horizontal labels and point labels.**

### Priority 2: Consolidate Duplicated Functions

**Action:** Move `_resolve_plot_kwargs` to shared location

```python
# Move from script_compare_reduction.py and script_line_fit.py
# TO: src/lib/plot.py or scripts/common_args.py

# Add to imports in both scripts:
# from common_args import resolve_plot_kwargs  # or from lib.plot import resolve_plot_kwargs
```

### Priority 3: Standardize Label Mapping Functions

**Action:** Create single authoritative function

```python
# Move to: src/lib/ or scripts/common_args.py
def map_iterable_label(iterable_name, raw_value, mapping_name=None, unique_count=None):
    """
    Unified label mapping for iterable values.
    
    Args:
        iterable_name: Name of iterable column (e.g., "PDG", "Plane")
        raw_value: Raw value to map
        mapping_name: Optional custom mapping dict name
        unique_count: Count of unique values (for conditional logic)
    """
    # Consolidate logic from all three implementations
```

**Usage standardization:**
- Remove `_map_iterable_label` from script_compare_line_operation.py
- Remove duplicate from script_compare_configuration.py
- Keep single version in script_iterable_scan.py (or centralize)

### Priority 4: Fix Syntax Inconsistencies

**Action:** Standardize across all scripts

1. Use `is None` / `is not None` consistently
2. Standardize index variable naming (`jdx` → reserved for j-iteration, or use single naming scheme)
3. Use consistent import ordering (stdlib → third-party → local)

---

## Testing Recommendations

After refactoring:

1. **Visual regression testing:** Compare output plots before/after for all affected scripts
2. **Point label placement:** Verify labels don't overlap with legends in edge cases
3. **Line label positioning:** Test with various data ranges (large/small, log scales)
4. **All plot types:** Verify scatter, step, plot, line, errorbar, bar modes still render correctly

---

## Files Requiring Updates

| File | Changes | Priority | Impact |
|------|---------|----------|--------|
| `script_compare_hist1d.py` | Remove manual label code, use utilities | P1 | 3 locations |
| `script_compare_hist2d.py` | Remove manual label code, use utilities | P1 | 3 locations |
| `script_compare_line_operation.py` | Remove manual label code, use utilities; consolidate label mapping | P1 | 4 locations |
| `script_line_fit.py` | Remove manual label code, use utilities; move `_resolve_plot_kwargs` | P1 | 4 locations |
| `script_compare_reduction.py` | Move `_resolve_plot_kwargs` to shared location | P2 | 1 location |
| `src/lib/plot.py` | Already has utilities - no changes needed | - | - |
| `scripts/common_args.py` | Add consolidated functions (P2-P3) | P2 | New content |
| `src/lib/__init__.py` | Add consolidated label mapping (P3) | P3 | New content |
