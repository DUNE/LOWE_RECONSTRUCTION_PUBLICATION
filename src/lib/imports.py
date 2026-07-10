import os
import pickle
import pandas as pd

from rich import print as rprint


def _dataframe_from_pickle_payload(data):
    if isinstance(data, dict):
        if data and all(isinstance(value, pd.DataFrame) for value in data.values()):
            return pd.concat(data, names=["Source"]).reset_index(level=0)

        if data and all(not isinstance(value, (list, tuple, dict, pd.Series, pd.Index)) for value in data.values()):
            return pd.DataFrame([data])

    return pd.DataFrame(data)

def prepare_import(args):
    '''
    Imports are defined by the unique combinations of configurations and names. Scripts can be run by selecting different configurations for a single name, or by selecting different names for a single configuration.
    Additionally, both can be strictly defined by providing the same amount of configurations and names.
    Also, any of the two can be left as None to import all data files matching the other parameter.
    '''
    # At least one of configs or names must be provided
    if args.configs is None and args.names is None:
        return None, None
    
    # Create new variables for configs and names
    if args.configs is None:
        new_names = args.names
        new_configs = [None] * len(args.names)
    elif args.names is None:
        new_configs = args.configs
        new_names = [None] * len(args.configs)
    else:
        if len(args.configs) == 1 and len(args.names) == 1:
            new_configs = args.configs
            new_names = args.names
        elif len(args.configs) == 1 and len(args.names) > 1:
            new_configs = args.configs * len(args.names)
            new_names = args.names
        elif len(args.names) == 1 and len(args.configs) > 1:
            new_names = args.names * len(args.configs)
            new_configs = args.configs
        elif len(args.configs) == len(args.names):
            new_configs = args.configs
            new_names = args.names
        else:
            rprint("[red]Error:[/red] When providing multiple configurations and names, they must either be of the same length, or one of them must be of length 1.")
            return None, None

    return new_configs, new_names

def import_data(args):
    # Initialize an empty DataFrame to store combined data
    df = pd.DataFrame()
    
    configs, names = prepare_import(args)

    if args.configs is None and args.names is None:
        datafile = os.path.join(
            os.path.dirname(__file__), "../..", "input", "data", f"{args.datafile}.pkl"
        )
        if not os.path.exists(datafile):
            print(f"Data file not found: {datafile}")
            return df
        with open(datafile, 'rb') as f:
            data = pickle.load(f)
        df = _dataframe_from_pickle_payload(data)
    
    else:
        loaded_chunks = []
        # Loop through each configuration provided in args.configs
        for config, name in zip(configs, names):
            candidate_paths = []
            # Construct the path to the data file
            if args.configs is None:
                candidate_paths.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../..",
                        "input",
                        "data",
                        f"{name}_{args.datafile}.pkl",
                    )
                )
            elif args.names is None:
                candidate_paths.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../..",
                        "input",
                        "data",
                        f"{config}_{args.datafile}.pkl",
                    )
                )
                candidate_paths.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../..",
                        "input",
                        "data",
                        f"{args.datafile}.pkl",
                    )
                )
            else:
                candidate_paths.append(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../..",
                        "input",
                        "data",
                        f"{config}_{name}_{args.datafile}.pkl",
                    )
                )

            datafile = next((path for path in candidate_paths if os.path.exists(path)), None)
            
            # Check if the data file exists
            if datafile is None:
                print(f"Data file not found: {candidate_paths[0]}")
                continue
            
            # Load the data from the pickle file
            with open(datafile, 'rb') as f:
                data = pickle.load(f)

            loaded_df = _dataframe_from_pickle_payload(data)
            loaded_df = loaded_df.dropna(axis=1, how="all")
            if loaded_df.empty:
                continue

            loaded_chunks.append(loaded_df)

        if loaded_chunks:
            df = pd.concat(loaded_chunks, ignore_index=True)
    
    # Print the DataFrame if debug mode is enabled
    if args.debug:
        # Print list of df columns and their types with python comprehension
        rprint("DataFrame columns and types:")
        rprint({col: df[col].dtype for col in df.columns})
        rprint("\nDataFrame preview:")
        rprint(df)
    
    return df
