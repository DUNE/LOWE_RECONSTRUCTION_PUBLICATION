import numpy as np
import pandas as pd

from itertools import product
from rich import print as rprint


def _normalize_selection_columns(select):
    if select is None:
        return []
    if isinstance(select, str):
        return [select]
    return list(select)


def prepare_selection(df, args):
    """
    Prepare the selection process for filtering the DataFrame based on unique values in specified columns.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    args (Namespace): An object containing 'iterable' and 'save_values' attributes for filtering.

    Returns:
    tuple: A tuple containing:
        - unique_combinations (list): A list of unique value combinations for the specified columns.
        - unique_values (dict): A dictionary mapping each column to its unique values.
    """
    # Initialize a dictionary to hold unique values for each specified column
    unique_values = {}

    # Iterate over the columns specified in 'iterable' to collect unique values
    for col in _normalize_selection_columns(args.select):
        if col not in df.columns:
            rprint(f"Column '{col}' not found in DataFrame columns. Skipping...")
            continue

        # Store unique values for the column
        unique_values[col] = df[col].unique()

        # Check if the column has multiple unique values and print a warning if so
        if len(unique_values[col]) > 1:
            print(
                f"Column '{col}' has multiple unique values: {unique_values[col]} of type {type(unique_values[col][0])}"
            )

    # If both 'select' and 'save_values' are provided, print the filtering information
    if args.select is not None and args.save_values is not None:
        print(
            f"Applying save_values filter: {args.save_values} for column: {args.select}"
        )

    # Generate all unique combinations of values from the specified columns
    unique_combinations = list(product(*unique_values.values()))

    return unique_combinations, unique_values


def filter_dataframe(df, args):
    """
    Filter the DataFrame based on unique values and specified conditions.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    args (Namespace): An object containing 'iterable' and 'save_values' attributes for filtering.
    unique_values (dict): A dictionary mapping each column to its unique values.
    combination (tuple): A tuple of values corresponding to the unique values for filtering.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    this_df = (
        df.copy()
    )  # Create a copy of the DataFrame to avoid modifying the original

    # Filter the DataFrame according to the input variables
    if args.variables is not None:
        if hasattr(args, "variable_name") and args.variable_name is not None:
            this_df = this_df[this_df[args.variable_name].isin(args.variables)]
        else:
            this_df = this_df[this_df["Variable"].isin(args.variables)]
        # rprint(f"Filtered DataFrame to only include variables: {args.variables}. New size: {len(this_df)}")

    # Filter the DataFrame based on the unique value combinations for the selected columns
    if args.select is not None and args.save_values is not None:
        for idx, (save_key, save_value) in enumerate(
            zip(_normalize_selection_columns(args.select), args.save_values)
        ):
            # Check that the save_key exists in the dataframe and their entries match the type of save_value
            if save_key not in this_df.columns:
                rprint(
                    f"Save key {save_key} not found in dataframe columns. Skipping..."
                )
                continue

            if this_df.empty:
                # if args.debug:
                #     rprint(f"No data left in dataframe to apply save_key {save_key}. Skipping...")
                continue

            if args.debug:
                rprint(
                    f"\tApplying select filtering on {save_key}={save_value} with values {this_df[save_key].unique().tolist()}"
                )

            if isinstance(save_value, str) and save_value.lower() == "nan":
                save_value = None  # Convert string 'nan' to None

            # Convert to boolean if input is True or False
            if isinstance(save_value, str) and save_value.lower() in ["true", "false"]:
                save_value = save_value.lower() == "true"

            if isinstance(this_df[save_key].iloc[0], np.bool_):
                save_value = np.bool_(save_value)

            if save_value is None:
                if args.debug:
                    rprint(f"\t\tSelecting missing values for {save_key}")
                this_df = this_df[this_df[save_key].isna()]

            elif type(this_df[save_key].iloc[0]) != type(save_value):
                if args.debug:
                    rprint(
                        f"\t\tType mismatch for save_key {save_key}: dataframe has type {type(this_df[save_key].iloc[0])}, but save_value has type {type(save_value)}."
                    )
                    rprint(
                        f"\t\tTrying to convert save_value to type {type(this_df[save_key].iloc[0])}."
                    )
                try:
                    if isinstance(this_df[save_key].iloc[0], int) or isinstance(
                        this_df[save_key].iloc[0], np.integer
                    ):
                        save_value_converted = int(save_value)
                    elif isinstance(this_df[save_key].iloc[0], float) or isinstance(
                        this_df[save_key].iloc[0], np.floating
                    ):
                        save_value_converted = float(save_value)
                    else:
                        save_value_converted = str(save_value)

                    save_value = save_value_converted

                    if args.debug:
                        rprint(
                            f"\t\tConverted save_value to {type(save_value)} and selecting {save_key}={save_value}"
                        )

                except ValueError:
                    rprint(
                        f"[red]Error:[/red] Could not convert save_value {save_value} to type {type(this_df[save_key].iloc[0])}. Skipping."
                    )
                    continue

            if save_value is not None:
                this_df = this_df[this_df[save_key] == save_value]

            if args.debug:
                rprint(f"\tSize after filtering: {len(this_df)}")

    elif args.save_values is not None:
        if args.debug:
            print(f"Applying save_values filtering on {args.iterable}")

        this_df = this_df[this_df[args.iterable].isin(args.save_values)]

    else:
        # if args.debug:
        #     rprint("No additional save_values filtering applied.")
        pass

    return this_df  # Return the filtered DataFrame
