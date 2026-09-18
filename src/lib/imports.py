import pickle
from collections import Counter
from itertools import product
from pathlib import Path

import pandas as pd

from rich import print as rprint


# Local layout written by scripts/sync_solar_data.sh (see src/lib/solar_studies.py):
#   input/data/{config}_{name}_{kind}.pkl                          reference copy
#   input/data/studies/{folder}/{label}/{config}_{name}_{kind}.pkl   every (folder, label)
STUDIES_DIRNAME = "studies"
STUDY_FOLDER_ORDER = ("truncated", "nominal", "reduced")
DEFAULT_STUDY_LABEL = "default"
CUT_COLUMNS = ("NHits", "OpHits", "AdjCl")


def _dataframe_from_pickle_payload(data):
    if isinstance(data, dict):
        if data and all(isinstance(value, pd.DataFrame) for value in data.values()):
            return pd.concat(data, names=["Source"]).reset_index(level=0)

        if data and all(not isinstance(value, (list, tuple, dict, pd.Series, pd.Index)) for value in data.values()):
            return pd.DataFrame([data])

    return pd.DataFrame(data)


def normalize_datafiles(datafile):
    if datafile is None:
        return []
    if isinstance(datafile, (list, tuple)):
        return list(datafile)
    return [datafile]


def resolve_input_data_dir(path_override=None):
    repo_root = Path(__file__).resolve().parents[2]
    default_input_dir = repo_root / "input" / "data"

    if path_override is None:
        return default_input_dir, True

    raw_path = str(path_override).strip()
    if not raw_path or raw_path.lower() == "default":
        return default_input_dir, True

    resolved = Path(raw_path)
    if resolved.is_absolute():
        return resolved, False

    return default_input_dir / resolved, False


def pair_paths_with_datafiles(path, datafiles):
    paths = normalize_datafiles(path)
    n = len(datafiles)
    if not paths:
        return [None] * n
    if len(paths) == 1:
        return paths * n
    if len(paths) == n:
        return paths

    rprint(
        f"[red]Error:[/red] --path was given {len(paths)} value(s) but --datafile "
        f"has {n} entr{'y' if n == 1 else 'ies'}. Provide a single --path value "
        "(applied to every file) or exactly one value per --datafile entry."
    )
    return None


# --- Study tree resolution ----------------------------------------------------


def _folder_rank(name):
    return STUDY_FOLDER_ORDER.index(name) if name in STUDY_FOLDER_ORDER else len(STUDY_FOLDER_ORDER)


def _subdirs(path):
    try:
        return sorted((p for p in Path(path).iterdir() if p.is_dir()), key=lambda p: (_folder_rank(p.name), p.name))
    except (FileNotFoundError, NotADirectoryError, PermissionError):
        return []


def iter_study_label_dirs(base):
    """Yield ``(folder, label, directory)`` for a studies tree.

    ``base`` may be the studies root (``.../studies``, holding ``{folder}/{label}``),
    a folder directory (``.../studies/{folder}``) or a label directory itself.
    Folders come out in reference order (truncated, nominal, reduced).
    """
    base = Path(base)
    if not base.is_dir():
        return
    if base.name == STUDIES_DIRNAME:
        for folder_dir in _subdirs(base):
            for label_dir in _subdirs(folder_dir):
                yield folder_dir.name, label_dir.name, label_dir
    elif base.parent.name == STUDIES_DIRNAME:
        for label_dir in _subdirs(base):
            yield base.name, label_dir.name, label_dir
    elif base.parent.parent.name == STUDIES_DIRNAME:
        yield base.parent.name, base.name, base


def study_meta_from_path(path):
    """``(folder, label)`` for a file inside a studies tree, else ``(None, None)``."""
    parts = Path(path).parts
    if STUDIES_DIRNAME not in parts:
        return None, None
    idx = len(parts) - 1 - parts[::-1].index(STUDIES_DIRNAME)
    tail = parts[idx + 1 : -1]  # directories between studies/ and the file
    if len(tail) >= 2:
        return tail[0], tail[1]
    return None, None


def _split_study_entry(entry, label):
    """``"DayNight_Counts_charge_Q50"`` with label ``charge_Q50`` -> ``"DayNight_Counts"``."""
    if entry == label:
        return None
    suffix = f"_{label}"
    if entry.endswith(suffix):
        return entry[: -len(suffix)]
    return None


def _tree_candidates(base, prefix, entry):
    """Candidates for ``entry`` inside the studies tree rooted at ``base``.

    Supports the legacy flat convention (``--path studies --datafile Kind_label``),
    ``--path studies/{folder} --datafile Kind_label`` and plain ``Kind`` entries,
    which resolve to the ``default`` label directory of each folder.
    """
    label_dirs = list(iter_study_label_dirs(base))
    out = []
    for _folder, label, directory in label_dirs:
        kind = _split_study_entry(entry, label)
        if kind is not None:
            out.append(directory / f"{prefix}{kind}.pkl")
    for _folder, label, directory in label_dirs:
        if label == DEFAULT_STUDY_LABEL:
            out.append(directory / f"{prefix}{entry}.pkl")
    return out


def resolve_datafile_candidates(input_dir, prefix, entry, include_studies_fallback=True):
    """Ordered candidate paths for ``{prefix}{entry}.pkl`` under ``input_dir``.

    Order: the studies tree inside ``input_dir`` (when ``--path`` points into
    it), the flat file in ``input_dir``, then — for the default input dir —
    the ``input/data/studies`` tree and finally the legacy flat
    ``input/data/studies/{prefix}{entry}.pkl``.
    """
    input_dir = Path(input_dir)
    candidates = []

    def add(path):
        if path not in candidates:
            candidates.append(path)

    inside_tree = STUDIES_DIRNAME in input_dir.parts
    if inside_tree:
        for path in _tree_candidates(input_dir, prefix, entry):
            add(path)
    add(input_dir / f"{prefix}{entry}.pkl")
    if include_studies_fallback:
        studies_root = input_dir / STUDIES_DIRNAME
        for path in _tree_candidates(studies_root, prefix, entry):
            add(path)
        add(studies_root / f"{prefix}{entry}.pkl")
    return candidates


def build_datafile_candidates(datafile, input_dir, include_studies_fallback=True, include_stem_fallback=False):
    """Candidates for a bare ``--datafile`` entry (no config/name prefix)."""
    input_dir = Path(input_dir)
    candidate = Path(datafile)

    candidates = [candidate]
    if candidate.suffix == ".pkl":
        entries = [candidate.stem]
        candidates.append(input_dir / candidate.name)
    else:
        entries = [candidate.name]
        if include_stem_fallback and candidate.stem != candidate.name:
            entries.append(candidate.stem)

    for entry in entries:
        for path in resolve_datafile_candidates(input_dir, "", entry, include_studies_fallback):
            if path not in candidates:
                candidates.append(path)

    return candidates


def _is_reference_copy(path, input_dir):
    """A flat ``input/data/X.pkl`` whose tree twin is ``studies/truncated/default/X.pkl``."""
    path = Path(path)
    return path.parent == Path(input_dir) and (
        Path(input_dir) / STUDIES_DIRNAME / STUDY_FOLDER_ORDER[0] / DEFAULT_STUDY_LABEL / path.name
    ).exists()


def tag_study_from_datafile(df, datafile_entry, label=None):
    """Ensure a usable ``Study`` label on every loaded row.

    Every SOLAR analysis pkl now carries its own ``Study`` column (``default``
    or the study label), which is left untouched. Files without one
    (cutflow, weighted distributions, older pkls) get ``label`` when the file
    was resolved inside the studies tree or is the flat reference copy, and
    otherwise fall back to the datafile stem — the labelling convention used
    by ``study_dict`` (e.g. "DayNight_Counts": "Reference").
    """
    fallback = label if label is not None else datafile_entry
    if "Study" not in df.columns:
        df["Study"] = fallback
    else:
        df["Study"] = df["Study"].fillna(fallback)
    return df


def _load_datafile(datafile, datafile_entry, input_dir):
    with Path(datafile).open("rb") as f:
        data = pickle.load(f)

    loaded_df = _dataframe_from_pickle_payload(data)
    loaded_df = loaded_df.dropna(axis=1, how="all")
    if loaded_df.empty:
        return loaded_df

    folder, label = study_meta_from_path(datafile)
    if label is None and _is_reference_copy(datafile, input_dir):
        folder, label = STUDY_FOLDER_ORDER[0], DEFAULT_STUDY_LABEL

    loaded_df["_Datafile"] = datafile_entry
    loaded_df["_Folder"] = folder
    loaded_df["_Label"] = label
    return tag_study_from_datafile(loaded_df, datafile_entry, label)


# --- Selection-cut consistency (Sensitivity) ------------------------------------


def _cut_triplet(row):
    return tuple(None if pd.isna(row[c]) else float(row[c]) for c in CUT_COLUMNS)


def cut_triplets_by_group(df, analysis="Sensitivity"):
    """``{(Config, Study, _Datafile): {(NHits, OpHits, AdjCl), ...}}`` for ``analysis`` rows.

    Returns an empty dict when the frame has no cut columns or no rows of that
    analysis (DayNight and HEP scan their own cuts, so only Sensitivity matters).
    """
    if not all(c in df.columns for c in CUT_COLUMNS):
        return {}
    sub = df
    if "Analysis" in df.columns:
        sub = df[df["Analysis"].astype(str).str.lower() == analysis.lower()]
    elif "_Datafile" in df.columns:
        sub = df[df["_Datafile"].astype(str).str.contains(analysis, case=False, regex=False)]
    else:
        return {}
    if sub.empty:
        return {}

    keys = [c for c in ("Config", "Study", "_Datafile") if c in sub.columns]
    groups = {}
    for key, frame in sub.groupby(keys, dropna=False, sort=False):
        key = key if isinstance(key, tuple) else (key,)
        groups[key] = {_cut_triplet(row) for _, row in frame[list(CUT_COLUMNS)].iterrows()}
    return groups


def cut_mismatch_flags(df, analysis="Sensitivity", quiet=False):
    """Warn when Sensitivity rows compare different (NHits, OpHits, AdjCl) working points.

    Studies are read as comparisons against ``default``, so a different cut on
    either side makes the comparison meaningless. Returns the set of
    ``(Config, _Datafile)`` pairs whose cut differs from the reference cut of
    that config (the ``default`` study when loaded, else the first group).
    """
    groups = cut_triplets_by_group(df, analysis)
    if not groups:
        return set()

    def fmt(trips):
        return " | ".join("/".join("nan" if v is None else f"{v:g}" for v in t) for t in sorted(trips, key=str))

    key_names = [c for c in ("Config", "Study", "_Datafile") if c in df.columns]
    by_config = {}
    for key, trips in groups.items():
        cfg = key[key_names.index("Config")] if "Config" in key_names else None
        by_config.setdefault(cfg, []).append((key, trips))

    flagged = set()
    for cfg, items in by_config.items():
        reference = next(
            (trips for key, trips in items if "Study" in key_names and key[key_names.index("Study")] == DEFAULT_STUDY_LABEL),
            items[0][1],
        )
        for key, trips in items:
            if trips != reference:
                datafile = key[key_names.index("_Datafile")] if "_Datafile" in key_names else None
                flagged.add((cfg, datafile))

    all_trips = set().union(*groups.values())
    if len(all_trips) > 1 and not quiet:
        rprint(
            f"[yellow]Warning:[/yellow] {analysis} rows use different NHits/OpHits/AdjCl selection cuts; "
            "study-vs-default and config-vs-config comparisons are only meaningful at the same working point:"
        )
        for key, trips in groups.items():
            marker = " [red]<- differs from reference[/red]" if (
                (key[key_names.index("Config")] if "Config" in key_names else None,
                 key[key_names.index("_Datafile")] if "_Datafile" in key_names else None) in flagged
            ) else ""
            desc = ", ".join(f"{n}={v}" for n, v in zip(key_names, key))
            rprint(f"    {desc}: NHits/OpHits/AdjCl = {fmt(trips)}{marker}")
    return flagged


# --- Import ----------------------------------------------------------------------


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

    datafile_entries = normalize_datafiles(args.datafile)
    path_entries = pair_paths_with_datafiles(getattr(args, "path", None), datafile_entries)
    if path_entries is None:
        return df

    if getattr(args, "name_columns", False) and args.configs is not None and args.names is not None:
        # Cross-product loading: every (config, name) pair gets its own file lookup
        # instead of the strict 1-to-1/1-to-N pairing used by prepare_import.
        pairs = list(product(args.configs, args.names))
        configs = [config for config, _ in pairs]
        names = [name for _, name in pairs]
    else:
        configs, names = prepare_import(args)

    if args.configs is None and args.names is None:
        loaded_chunks = []
        for datafile_entry, path_entry in zip(datafile_entries, path_entries):
            input_dir, include_studies_fallback = resolve_input_data_dir(path_entry)
            candidate_paths = build_datafile_candidates(
                datafile_entry,
                input_dir,
                include_studies_fallback=include_studies_fallback,
            )
            datafile = next((path for path in candidate_paths if path.exists()), None)
            if datafile is None:
                print(f"Data file not found: {candidate_paths[0]}")
                continue

            loaded_df = _load_datafile(datafile, datafile_entry, input_dir)
            if loaded_df.empty:
                continue
            loaded_chunks.append(loaded_df)

        if loaded_chunks:
            df = pd.concat(loaded_chunks, ignore_index=True)

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
            for datafile_entry, path_entry in zip(datafile_entries, path_entries):
                input_dir, include_studies_fallback = resolve_input_data_dir(path_entry)
                # SOLAR's save_df() encodes config/name into every filename:
                # {config}_{name}_{datafile}.pkl. Each prefix is resolved flat,
                # inside the studies tree (studies/{folder}/{label}/) and, for
                # the default input dir, against the legacy flat studies/ copies.
                if args.configs is None:
                    prefixes = [f"{name}_"]
                elif args.names is None:
                    prefixes = [f"{config}_", ""]
                else:
                    prefixes = [f"{config}_{name}_"]

                candidate_paths = []
                for prefix in prefixes:
                    for path in resolve_datafile_candidates(input_dir, prefix, datafile_entry, include_studies_fallback):
                        if path not in candidate_paths:
                            candidate_paths.append(path)

                datafile = next((path for path in candidate_paths if path.exists()), None)

                # Check if the data file exists
                if datafile is None:
                    print(f"Data file not found: {candidate_paths[0]}")
                    continue

                loaded_df = _load_datafile(datafile, datafile_entry, input_dir)
                if loaded_df.empty:
                    continue

                loaded_df["_Occurrence"] = occurrence
                loaded_chunks.append(loaded_df)

        if loaded_chunks:
            df = pd.concat(loaded_chunks, ignore_index=True)

    if not df.empty:
        cut_mismatch_flags(df)

    # Print the DataFrame if debug mode is enabled
    if args.debug:
        # Print list of df columns and their types with python comprehension
        rprint("DataFrame columns and types:")
        rprint({col: df[col].dtype for col in df.columns})
        rprint("\nDataFrame preview:")
        rprint(df)

    return df
