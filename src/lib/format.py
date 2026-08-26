import sys
import os
import re
import numpy as np
import pandas as pd
from . import config_dict, config_color, config_line, name_color, name_dict


def get_simple_title_from_script(args=None):
    """
    Generate a simple, human-readable title from the script name.
    
    Extracts the script name from sys.argv[0] and converts it to a user-friendly format.
    Examples:
        script_compare_configuration.py -> Compare Configuration
        script_compare_hist1d.py -> Compare Histogram 1D
        script_aggregate_table.py -> Aggregate Table
    
    Returns:
        str: A simple title based on the script name
    """
    try:
        if args is not None and hasattr(args, "datafile") and args.datafile:
            title_source = str(args.datafile)
        else:
            # Fallback to the script basename (without directories)
            script_name = sys.argv[0] if sys.argv else "script"
            script_base = os.path.basename(script_name)
            if script_base.endswith(".py"):
                script_base = script_base[:-3]
            if script_base.startswith("script_"):
                script_base = script_base[7:]
            title_source = script_base

        # Replace underscores with spaces
        title = title_source.replace("_", " ")
        # Title case each word first
        title = " ".join(word.capitalize() for word in title.split())
        # Handle common abbreviations after title casing
        title = title.replace("Hist1d", "Histogram 1D")
        title = title.replace("Hist2d", "Histogram 2D")
        return title
    except Exception:
        return "Plot"


def make_title_from_args(args, verbose=False):
    """
    Generate a plot title from arguments.
    
    Parameters:
    args : argparse.Namespace
        The arguments namespace
    verbose : bool, optional
        If True, use verbose title with all details (datafile, configs, names, etc.)
        If False (default), use simple script-based title
    
    Returns:
    str
        The generated title
    """
    # Check for explicit title first
    if hasattr(args, "title") and args.title is not None:
        return args.title
    
    if verbose:
        return make_verbose_title_from_args(args)
    else:
        return get_simple_title_from_script(args)


def make_verbose_title_from_args(args):
    """
    Generate a verbose plot title from all available arguments.
    
    This is the original detailed title generation that includes datafile,
    configurations, names, variables, x/y axes, and iterables.
    
    Parameters:
    args : argparse.Namespace
        The arguments namespace
    
    Returns:
    str
        The verbose title combining multiple argument details
    """
    title_parts = []

    if hasattr(args, "datafile"):
        title_parts.append(args.datafile)

    if hasattr(args, "configs") and args.configs:
        if args.configs is not None:
            title_parts.append("_".join(args.configs))

    if hasattr(args, "names") and args.names:
        if args.names is not None:
            title_parts.append("_".join(args.names))

    if hasattr(args, "x") and args.x and isinstance(args.x, str):
        title_parts.append(args.x)

    if hasattr(args, "y") and args.y and isinstance(args.y, str):
        title_parts.append(args.y)

    if hasattr(args, "variables") and args.variables:
        title_parts.append("_".join(args.variables))

    if hasattr(args, "iterable") and args.iterable:
        if hasattr(args, "select") and args.select is None:
            title_parts.append(args.iterable)

        elif (hasattr(args, "select") and args.select is not None) and (
            hasattr(args, "save_values") and args.save_values is not None
        ):
            select_save_parts = []
            for sel, val in zip(args.select, args.save_values):
                if sel and val:  # Check if both sel and val have content
                    select_save_parts.append(f"{sel}: {val}")
            if select_save_parts:  # Only add if select_save_parts is not empty
                title_parts.append(", ".join(select_save_parts))

    return " - ".join(title_parts) if title_parts else "Plot"


def make_subtitle_from_args(args, iterables, plot_type="hist1d", idx=None):
    subtitle_parts = []

    if hasattr(args, "subtitle") and args.subtitle:
        subtitle_parts.append(args.subtitle)
    else:
        if plot_type == "hist2d":
            if hasattr(args, "iterable") and args.iterable:
                subtitle_parts.append(f"{args.iterable}: {iterables[idx]}")

        else:
            if hasattr(args, "variables") and args.variables:
                if idx is not None and 0 <= idx < len(args.variables):
                    subtitle_parts.append(args.variables[idx])
                else:
                    subtitle_parts.append("_".join(args.variables))

            if hasattr(args, "iterable") and args.iterable:
                if (hasattr(args, "select") and args.select is not None) and (
                    hasattr(args, "save_values") and args.save_values is not None
                ):
                    select_save_parts = []
                    for sel, val in zip(args.select, args.save_values):
                        if sel and val:  # Check if both sel and val have content
                            select_save_parts.append(f"{sel}: {val}")
                    if select_save_parts:  # Only add if select_save_parts is not empty
                        subtitle_parts.append(", ".join(select_save_parts))
                elif hasattr(args, "iterable") and args.iterable:
                    subtitle_parts.append(f"{args.iterable}")

    return " - ".join(subtitle_parts)


def _wants_scientific(value, args):
    """
    Decide whether `value` should be rendered in scientific notation:
    always when --scientific is set, or automatically when its magnitude
    falls outside the [--scientific_threshold_low, --scientific_threshold_high]
    window (either bound may be None/unset).
    """
    if args is None:
        return False

    if getattr(args, "scientific", False):
        return True

    abs_value = abs(value)

    low = getattr(args, "scientific_threshold_low", None)
    if low is not None and abs_value < low:
        return True

    high = getattr(args, "scientific_threshold_high", None)
    if high is not None and abs_value > high:
        return True

    return False


def _resolve_decimal_places(error):
    """Number of decimal places (plain notation) needed to show `error` to
    1 significant figure, or 2 if its leading digit is 1 (PDG rounding rule).
    Can be negative for errors coarser than the ones place (e.g. an error of
    ~20000 resolves to -3, i.e. round to the nearest thousand).
    Returns None if the error can't be used to resolve a precision.
    """
    if error is None or not np.isfinite(error) or error <= 0:
        return None

    exponent = int(np.floor(np.log10(abs(error))))
    leading_digit = int(abs(error) / 10**exponent + 1e-9)
    sig_figs = 2 if leading_digit == 1 else 1
    return sig_figs - 1 - exponent


def _too_many_digits(error_digits, max_digits=3):
    """True if the parenthetical error digits have grown past what 1-2
    significant figures should ever produce (allowing a little rounding
    slack, e.g. 9.6 -> "10"). A large digit count means the error's own
    magnitude is wildly different from the value's, usually an unconstrained
    or degenerate fit parameter, where the parenthetical notation breaks down.
    """
    return len(str(abs(error_digits))) > max_digits


def _format_value_with_paren_error(base_format, value, error):
    """Format `value +/- error` in compact parenthetical notation (e.g.
    "1.35(6)e-08" instead of "1.35e-08 +/- 6e-09"), the standard convention
    used in PDG/CODATA tables: the digits in parentheses are the error rounded
    to the value's last significant decimal place, in units of that place.
    Falls back to a plain formatted value if the error can't resolve a precision.
    """
    decimals = _resolve_decimal_places(error)
    if decimals is None:
        return format(value, base_format)

    match = re.match(r"^\.?\d*([a-zA-Z%])$", base_format)
    type_char = match.group(1) if match else "f"

    if type_char in "fF%":
        error_digits = int(round(abs(error) * 10**decimals))
        if decimals >= 0:
            value_str = format(value, f".{decimals}{type_char}")
        else:
            # format() can't take negative precision; pre-round to the
            # resolved place (e.g. nearest thousand) and show 0 decimals
            value_str = format(round(value, decimals), f".0{type_char}")
        if _too_many_digits(error_digits):
            # Error dwarfs the value (e.g. an unconstrained/degenerate fit
            # parameter) -- parenthetical notation isn't meaningful, fall back
            # to showing value and error independently.
            return f"{value_str} $\\pm$ {format(error, base_format)}"
        return f"{value_str}({error_digits})"

    if type_char in "eEgG":
        value_exponent = (
            int(np.floor(np.log10(abs(value)))) if value != 0 and np.isfinite(value) else 0
        )
        mantissa_decimals = max(decimals + value_exponent, 0)
        mantissa_part, _, exponent_part = format(
            value, f".{mantissa_decimals}{type_char}"
        ).partition("e")
        error_digits = int(round(abs(error) / 10 ** (value_exponent - mantissa_decimals)))
        if _too_many_digits(error_digits):
            return f"{format(value, base_format)} $\\pm$ {format(error, base_format)}"
        return f"{mantissa_part}({error_digits})e{exponent_part}"

    return format(value, base_format)


def format_with_error(
    row, args=None, threshold=1e-3, significant_figures=1, error_format="±"
):
    mean = row[(args.y, getattr(args, "operation", "mean"))]
    error = row[(f"{args.y}Error", "<lambda>")]

    threshold = getattr(args, "threshold", threshold) if args is not None else threshold

    if abs(mean) < threshold:  # Check if mean is smaller than threshold
        return "---"  # Return '---' if mean is below threshold

    scientific = _wants_scientific(mean, args)
    decimals = significant_figures if significant_figures is not None else 1

    if pd.isna(error) or np.isinf(error) or error == 0 or error > 100 * abs(mean):
        if scientific:
            return f"{mean:.{decimals}e} ± {np.nan}"
        return f"{mean:.2f} ± {np.nan}"  # Return mean ± error with 2 decimal places

    if scientific:
        if args is not None and getattr(args, "compact_scientific", False):
            return _format_value_with_paren_error("e", mean, error)
        if error_format == "±":
            format_string = f"{{:.{decimals}e}} ± {{:.{decimals}e}}"
        elif error_format == "()":
            format_string = f"{{:.{decimals}e}}({{:.{decimals}e}})"
        else:
            print(f"Unknown format: {error_format}. Defaulting to '±'")
            format_string = f"{{:.{decimals}e}} ± {{:.{decimals}e}}"
        return format_string.format(mean, error)

    # Determine significant figures based on error if not provided
    error_magnitude = -int(np.floor(np.log10(abs(error)))) + 1
    if significant_figures is None:
        significance = max(
            2, error_magnitude
        )  # Use error to decide significant figures

    else:
        significance = error_magnitude - 2 + significant_figures
        if significance < 0:
            significance = 0

    if error_format == "±":
        format_string = f"{{:.{significance}f}} ± {{:.{significance}f}}"

    elif error_format == "()":
        format_string = f"{{:.{significance}f}}({{:.{significance}f}})"  # Ensure at least specified significant figures

    else:
        print(f"Unknown format: {error_format}. Defaulting to '±'")
        format_string = f"{{:.{significance}f}} ± {{:.{significance}f}}"

    return format_string.format(mean, error)


def format_value(row, args=None, threshold=1e-3):
    """
    Format an aggregated value with no uncertainty, for use when the source
    data has no *Error column to propagate (see format_with_error for the
    version that includes a propagated error).
    """
    mean = row[(args.y, getattr(args, "operation", "mean"))]

    threshold = getattr(args, "threshold", threshold) if args is not None else threshold

    if abs(mean) < threshold:  # Check if mean is smaller than threshold
        return "---"

    if _wants_scientific(mean, args):
        return f"{mean:.2e}"

    return f"{mean:.2f}"


def make_config_label_from_args(args, config=None, name=None, iterable=None):
    """
    Generate a configuration label using the same naming structure as script_compare_configuration.py.
    
    This function applies conditional naming logic based on the number of configs and names:
    - 1 config + 1 name: use geometry only
    - 2+ configs + 1 name: use "GEOMETRY, CONFIG_LABEL"
    - 1 config + 2+ names: use "GEOMETRY, NAME"
    - Otherwise: use "GEOMETRY, CONFIG_LABEL, NAME"
    
    If --iterable is provided, append ", ITERABLE" to the label.
    
    Parameters:
    args : argparse.Namespace
        The arguments namespace containing configs, names, and iterable.
    config : str, optional
        The current configuration value (can be None).
    name : str, optional
        The current name value (can be None).
    iterable : optional
        The current iterable value (can be None).
    
    Returns:
    str
        The formatted configuration label.
    """
    # Extract geometry from config (first part before underscore)
    if config is not None:
        geom = str(config).split("_")[0]
    else:
        geom = ""
    
    # Get config label from dictionary
    config_label = config_dict.get(config, str(config)) if config is not None else None

    # Get human-readable label for name, falling back to the raw value
    name_label = name_dict.get(name, str(name)) if name is not None else None

    # Get number of configs and names
    num_configs = len(args.configs) if hasattr(args, "configs") and args.configs else 0
    num_names = len(args.names) if hasattr(args, "names") and args.names else 0

    # Apply naming logic based on number of configs and names
    if num_configs < 2 and num_names == 1:
        # Use geometry only
        geom_label = f"{geom.upper()}"
    elif num_configs >= 2 and num_names == 1:
        # Use "GEOMETRY, CONFIG_LABEL"
        geom_label = f"{geom.upper()}, {config_label}"
    elif num_configs == 1 and num_names > 1:
        # Use "GEOMETRY, NAME"
        geom_label = f"{geom.upper()}, {name_label}"
    else:
        # Use "GEOMETRY, CONFIG_LABEL, NAME"
        geom_label = f"{geom.upper()}, {config_label}, {name_label}"
    
    # Append iterable if provided
    if iterable is not None and hasattr(args, "iterable") and args.iterable is not None:
        geom_label += f", {iterable}"
    
    return geom_label


def make_config_color_and_style_from_args(args, config=None, name=None):
    """
    Get the color and line style for a given configuration.
    
    Uses the config_color and config_line dictionaries from lib/__init__.py.
    If the config is not found in the dictionaries, returns default values.
    
    When there is only a single config but multiple names, uses name_color 
    to assign different colors based on the name instead of config.
    
    Parameters:
    args : argparse.Namespace
        The arguments namespace containing configs and names.
    config : str, optional
        The configuration value (can be None).
    name : str, optional
        The name value (used for name-based coloring when single config).
    
    Returns:
    tuple
        (color, linestyle) - both are strings or None if not found
    """
    if config is None:
        return None, None
    
    # If only one config but multiple names, use name-based colors for differentiation
    num_configs = len(args.configs) if hasattr(args, "configs") and args.configs else 0
    num_names = len(args.names) if hasattr(args, "names") and args.names else 0
    
    if num_configs == 1 and num_names > 1:
        # Use name-based coloring when single config with multiple names
        color = name_color.get(name, None) if name else None
        return color, None
    
    # Get color and linestyle from config dictionaries
    color = config_color.get(config, None)
    linestyle = config_line.get(config, None)
    
    return color, linestyle
