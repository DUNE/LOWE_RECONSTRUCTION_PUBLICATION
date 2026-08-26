import pickle
from collections import Counter
from itertools import product
from pathlib import Path

import pandas as pd

from rich import print as rprint


def _dataframe_from_pickle_payload(data):
    if isinstance(data, dict):
        if data and all(isinstance(value, pd.DataFrame) for value in data.values()):
            return pd.concat(data, names=["Source"]).reset_index(level=0)

        if data and all(not isinstance(value, (list, tuple, dict, pd.Series, pd.Index)) for value in data.values()):
            return pd.DataFrame([data])

    return pd.DataFrame(data)


def resolve_input_data_dir(path_override=None):
    repo_root = Path(__file__).resolve().parents[2]
    default_input_dir = repo_root / "input" / "data"

    if path_override is None:
        return default_input_dir, True

    raw_path = str(path_override).strip()
    if not raw_path:
        return default_input_dir, True

    resolved = Path(raw_path)
    if resolved.is_absolute():
        return resolved, False

    return default_input_dir / resolved, False


def build_datafile_candidates(datafile, input_dir, include_studies_fallback=True, include_stem_fallback=False):
    input_dir = Path(input_dir)
    candidate = Path(datafile)

    candidates = [candidate]
    if candidate.suffix == ".pkl":
        candidates.append(input_dir / candidate.name)
    else:
        candidates.append(input_dir / f"{candidate.name}.pkl")
        if include_stem_fallback:
            candidates.append(input_dir / f"{candidate.stem}.pkl")

    if include_studies_fallback:
        candidates += [input_dir / "studies" / c.name for c in candidates if c.is_relative_to(input_dir)]

    deduped_candidates = []
    for path in candidates:
        if path in deduped_candidates:
            continue
        deduped_candidates.append(path)

    return deduped_candidates

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

    if getattr(args, "name_columns", False) and args.configs is not None and args.names is not None:
        # Cross-product loading: every (config, name) pair gets its own file lookup
        # instead of the strict 1-to-1/1-to-N pairing used by prepare_import.
        pairs = list(product(args.configs, args.names))
        configs = [config for config, _ in pairs]
        names = [name for _, name in pairs]
    else:
        configs, names = prepare_import(args)

    input_dir, include_studies_fallback = resolve_input_data_dir(getattr(args, "path", None))

    if args.configs is None and args.names is None:
        candidate_paths = build_datafile_candidates(
            args.datafile,
            input_dir,
            include_studies_fallback=include_studies_fallback,
        )
        datafile = next((path for path in candidate_paths if path.exists()), None)
        if datafile is None:
            print(f"Data file not found: {candidate_paths[0]}")
            return df
        with datafile.open('rb') as f:
            data = pickle.load(f)
        df = _dataframe_from_pickle_payload(data)
    
    else:
        pair_counts = Counter(zip(configs, names))
        duplicates = [pair for pair, count in pair_counts.items() if count > 1]
        if duplicates:
            dup_desc = "; ".join(
                f"Config={c}, Name={n}" if n is not None else f"Config={c}"
                for c, n in duplicates
            )
            rprint(
                f"[yellow]Warning:[/yellow] Duplicate config/name pair(s) requested: "
                f"{dup_desc}. Each occurrence will be loaded and plotted as an "
                "independent line."
            )

        loaded_chunks = []
        # Loop through each configuration provided in args.configs. `occurrence`
        # tags which requested slot a row came from so duplicate (config, name)
        # pairs stay distinguishable further down the pipeline instead of
        # collapsing into a single, ambiguous merged block of rows.
        for occurrence, (config, name) in enumerate(zip(configs, names)):
            candidate_paths = []
            # Construct the path to the data file
            if args.configs is None:
                candidate_paths.append(input_dir / f"{name}_{args.datafile}.pkl")
            elif args.names is None:
                candidate_paths.append(input_dir / f"{config}_{args.datafile}.pkl")
                candidate_paths.append(input_dir / f"{args.datafile}.pkl")
            else:
                candidate_paths.append(input_dir / f"{config}_{name}_{args.datafile}.pkl")

            # Study-variant pkls (e.g. ..._charge_Q100.pkl) live under
            # input/data/studies/ instead of flat in input/data/ — fall back
            # there for each candidate rather than maintaining a suffix
            # allowlist. Flat candidates are still tried first.
            if include_studies_fallback:
                candidate_paths += [
                    path.parent / "studies" / path.name
                    for path in candidate_paths
                ]

            datafile = next((path for path in candidate_paths if path.exists()), None)

            # Check if the data file exists
            if datafile is None:
                print(f"Data file not found: {candidate_paths[0]}")
                continue
            
            # Load the data from the pickle file
            with datafile.open('rb') as f:
                data = pickle.load(f)

            loaded_df = _dataframe_from_pickle_payload(data)
            loaded_df = loaded_df.dropna(axis=1, how="all")
            if loaded_df.empty:
                continue

            loaded_df["_Occurrence"] = occurrence
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
