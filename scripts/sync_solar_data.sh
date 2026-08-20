#!/usr/bin/env bash
# sync_solar_data.sh — Pull plot-ready .pkl files from a remote SOLAR installation
# into local input/data/, driven by the OUTPUT_ONLY section of
# config/analysis/pkl_paths.json in the SOLAR source repo.
#
# pkl_paths.json partitions all pkl files into INTERMEDIATE (pipeline-internal)
# and OUTPUT_ONLY (never read back by any other SOLAR script — safe to copy for
# external plotting). Only OUTPUT_ONLY files are synced here.
#
# Base paths in pkl_paths.json use two root variables:
#   {root}  — SOLAR installation root (set by --remote)
#   {PATH}  — PNFS shared storage (set by --pnfs; some OUTPUT_ONLY files live
#             there when in_pnfs is true)
#
# Paths are truncated at the first remaining template variable so they resolve
# to the widest concrete directory that can be rsynced. Content filters then
# narrow down which files are actually copied.
#
# SOLAR's save_df() encodes config/name into every filename:
#   {config}_{name}_{datafile}.pkl
# so all files are safely flattened by basename into input/data/.
#
# Usage:
#   ./sync_solar_data.sh [OPTIONS]
#
# Core options:
#   --remote HOST:PATH       Remote SOLAR root directory
#                            Default: gae_out:/pc/choozdsk01/users/manthey/SOLAR
#   --pnfs HOST:PATH         Remote PNFS root for in_pnfs=true OUTPUT_ONLY files
#                            Default: gae_out:/pnfs/ciemat.es/data/neutrinos/DUNE/SOLAR
#   --force                  Overwrite existing local .pkl files (default: skip)
#   --dry-run                Show what would be synced without copying anything
#   --show-sources           Print resolved source directories and exit
#   -h, --help               Show this help and exit
#
# Content filters (each flag accepts one value; repeat to allow multiple):
#   --config VALUE           Include only files matching this detector config
#   --exclude-config VALUE   Exclude files matching this detector config
#   --name VALUE             Include only files matching this sample name
#   --exclude-name VALUE     Exclude files matching this sample name
#   --folder VALUE           Include only files whose path contains this folder
#   --exclude-folder VALUE   Exclude files whose path contains this folder
#   --energy VALUE           Include only files whose name contains this energy label
#   --exclude-energy VALUE   Exclude files whose name contains this energy label
#   --study VALUE             Include only files under this study subdirectory
#                              (e.g. default, unc_bkg0, charge_Q100, oscpoint_solar
#                              — the variant folder some outputs are grouped under,
#                              one level above the .pkl file). Files with no study
#                              subdirectory at all are left untouched by this filter
#                              — it only rejects files under a *different* study.
#   --exclude-study VALUE     Exclude files under this study subdirectory
#   --analysis VALUE           Include only files belonging to this physics
#                              analysis: daynight, hep, or sensitivity. Matched
#                              case-insensitively against the full path and
#                              filename with hyphens stripped, so "day-night",
#                              "DayNight", "HEP", "Sensitivity" all match.
#   --exclude-analysis VALUE   Exclude files belonging to this analysis
#
# Filter logic: all filters are matched against the full remote path and filename.
# Include filters are OR-ed within a dimension; all dimensions must pass (AND).
#
# index.json theme/publication discovery (additive — does not change the
# default OUTPUT_ONLY sync described above):
#   --theme VALUE             Also fetch files tagged with this theme in
#                              output/data/index.json (repeat to allow multiple;
#                              OR-ed together). Combined with --publication, both
#                              conditions must hold (AND).
#   --publication              Also fetch files with publication_export=true in
#                              output/data/index.json
#   --list-themes              Print available themes from index.json and exit
#                              (does not sync anything)
#
# Examples:
#   ./sync_solar_data.sh
#   ./sync_solar_data.sh --config hd_1x2x6_centralAPA --name marley
#   ./sync_solar_data.sh --name marley --name gamma --exclude-folder Truncated
#   ./sync_solar_data.sh --energy SolarEnergy --force
#   ./sync_solar_data.sh --study default --exclude-study unc_bkg0
#   ./sync_solar_data.sh --analysis daynight --name marley --folder truncated
#   ./sync_solar_data.sh --show-sources
#   ./sync_solar_data.sh --list-themes
#   ./sync_solar_data.sh --theme daynight --publication

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$SCRIPT_DIR/input/data"
MANIFEST_PATH="config/analysis/pkl_paths.json"
INDEX_PATH="output/data/index.json"
SOLAR_INDEX_PY="$SCRIPT_DIR/src/lib/solar_index.py"

# Known theme names (mirrors index.json's "_themes"). Some outputs are grouped
# into subdirectories with these names (e.g. solar/nhits/.../daynight/) — that's
# a thematic grouping, not a study/systematic variant, so --study/--exclude-study
# must never treat them as one even when --theme wasn't passed this run.
KNOWN_THEME_DIRS=(daynight hep sensitivity)

DEFAULT_REMOTE="gae_out:/pc/choozdsk01/users/manthey/SOLAR"
DEFAULT_PNFS="gae_out:/pnfs/ciemat.es/data/neutrinos/DUNE/SOLAR"

REMOTE="$DEFAULT_REMOTE"
PNFS="$DEFAULT_PNFS"
FORCE=false
DRY_RUN=false
SHOW_SOURCES=false

INCLUDE_CONFIGS=()
EXCLUDE_CONFIGS=()
INCLUDE_NAMES=()
EXCLUDE_NAMES=()
INCLUDE_FOLDERS=()
EXCLUDE_FOLDERS=()
INCLUDE_ENERGIES=()
EXCLUDE_ENERGIES=()
INCLUDE_STUDIES=()
EXCLUDE_STUDIES=()
INCLUDE_ANALYSES=()
EXCLUDE_ANALYSES=()

INCLUDE_THEMES=()
PUBLICATION_ONLY=false
LIST_THEMES=false

# --- Argument parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --remote)          REMOTE="$2";                  shift 2 ;;
        --pnfs)            PNFS="$2";                    shift 2 ;;
        --force)           FORCE=true;                   shift   ;;
        --dry-run)         DRY_RUN=true;                 shift   ;;
        --show-sources)    SHOW_SOURCES=true;            shift   ;;
        --config)          INCLUDE_CONFIGS+=("$2");      shift 2 ;;
        --exclude-config)  EXCLUDE_CONFIGS+=("$2");      shift 2 ;;
        --name)            INCLUDE_NAMES+=("$2");        shift 2 ;;
        --exclude-name)    EXCLUDE_NAMES+=("$2");        shift 2 ;;
        --folder)          INCLUDE_FOLDERS+=("$2");      shift 2 ;;
        --exclude-folder)  EXCLUDE_FOLDERS+=("$2");      shift 2 ;;
        --energy)          INCLUDE_ENERGIES+=("$2");     shift 2 ;;
        --exclude-energy)  EXCLUDE_ENERGIES+=("$2");     shift 2 ;;
        --study)           INCLUDE_STUDIES+=("$2");      shift 2 ;;
        --exclude-study)   EXCLUDE_STUDIES+=("$2");      shift 2 ;;
        --analysis)        INCLUDE_ANALYSES+=("$2");     shift 2 ;;
        --exclude-analysis) EXCLUDE_ANALYSES+=("$2");    shift 2 ;;
        --theme)           INCLUDE_THEMES+=("$2");       shift 2 ;;
        --publication)     PUBLICATION_ONLY=true;        shift   ;;
        --list-themes)     LIST_THEMES=true;             shift   ;;
        -h|--help)
            awk 'NR>1{if(/^#/){sub(/^# ?/,""); print} else if(NF){exit}}' "$0"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

REMOTE="${REMOTE%/}"
PNFS="${PNFS%/}"

# Derive the SSH host from the remote (HOST:PATH → HOST)
REMOTE_HOST="${REMOTE%%:*}"
PNFS_HOST="${PNFS%%:*}"

# --- Filter function ----------------------------------------------------------
matches_filter() {
    local path="$1"
    # Substring match — val anywhere in path or filename.
    _any_match() {
        local str="$1"; shift
        local val; for val in "$@"; do [[ "$str" == *"$val"* ]] && return 0; done; return 1
    }
    # Path-component match — val must be an exact directory segment (/val/).
    # Prevents 'marley' from matching 'marley_official', 'hd_1x2x6' from
    # matching 'hd_1x2x6_centralAPA', etc.
    _path_match() {
        local str="$1"; shift
        local val; for val in "$@"; do [[ "$str" == *"/$val/"* ]] && return 0; done; return 1
    }
    if (( ${#INCLUDE_CONFIGS[@]}  > 0 )); then _path_match "$path" "${INCLUDE_CONFIGS[@]}"  || return 1; fi
    if (( ${#EXCLUDE_CONFIGS[@]}  > 0 )); then _path_match "$path" "${EXCLUDE_CONFIGS[@]}"  && return 1; fi
    if (( ${#INCLUDE_NAMES[@]}    > 0 )); then _path_match "$path" "${INCLUDE_NAMES[@]}"    || return 1; fi
    if (( ${#EXCLUDE_NAMES[@]}    > 0 )); then _path_match "$path" "${EXCLUDE_NAMES[@]}"    && return 1; fi
    if (( ${#INCLUDE_FOLDERS[@]}  > 0 )); then _any_match  "$path" "${INCLUDE_FOLDERS[@]}"  || return 1; fi
    if (( ${#EXCLUDE_FOLDERS[@]}  > 0 )); then _any_match  "$path" "${EXCLUDE_FOLDERS[@]}"  && return 1; fi
    if (( ${#INCLUDE_ENERGIES[@]} > 0 )); then _any_match  "$path" "${INCLUDE_ENERGIES[@]}" || return 1; fi
    if (( ${#EXCLUDE_ENERGIES[@]} > 0 )); then _any_match  "$path" "${EXCLUDE_ENERGIES[@]}" && return 1; fi

    # Study filter: only some outputs are organised under an extra study/variant
    # subdirectory (e.g. default, unc_bkg0, charge_Q100) directly above the
    # .pkl file; most aren't. --study/--exclude-study must not reject paths
    # that have no such subdirectory in the first place — only paths where one
    # is present and doesn't match. A directory is treated as "structural"
    # (i.e. not a study) when it equals one of the active --config/--name/
    # --folder values, or a known theme name (daynight/hep/sensitivity —
    # thematic grouping, not a study variant); anything else immediately above
    # the filename is taken to be a study segment. (Without any --config/
    # --name/--folder filters active, every other immediate parent directory
    # is treated as a study segment.)
    if (( ${#INCLUDE_STUDIES[@]} > 0 || ${#EXCLUDE_STUDIES[@]} > 0 )); then
        local parent="${path%/*}"
        parent="${parent##*/}"
        local is_study=true val
        for val in "${INCLUDE_CONFIGS[@]}" "${EXCLUDE_CONFIGS[@]}" \
                   "${INCLUDE_NAMES[@]}"   "${EXCLUDE_NAMES[@]}"   \
                   "${INCLUDE_FOLDERS[@]}" "${EXCLUDE_FOLDERS[@]}" \
                   "${INCLUDE_THEMES[@]}"  "${KNOWN_THEME_DIRS[@]}"; do
            [[ "$parent" == "$val" ]] && { is_study=false; break; }
        done
        if $is_study; then
            if (( ${#INCLUDE_STUDIES[@]} > 0 )); then
                local found=false
                for val in "${INCLUDE_STUDIES[@]}"; do [[ "$parent" == "$val" ]] && { found=true; break; }; done
                $found || return 1
            fi
            if (( ${#EXCLUDE_STUDIES[@]} > 0 )); then
                for val in "${EXCLUDE_STUDIES[@]}"; do [[ "$parent" == "$val" ]] && return 1; done
            fi
        fi
    fi

    # Analysis filter: select by physics analysis (daynight/hep/sensitivity).
    # Matched case-insensitively against the full path, with hyphens stripped,
    # so "day-night" directories and "DayNight"/"HEP"/"Sensitivity" filename
    # fragments are all recognised regardless of which spelling is requested.
    if (( ${#INCLUDE_ANALYSES[@]} > 0 || ${#EXCLUDE_ANALYSES[@]} > 0 )); then
        local path_norm="${path//-/}"
        path_norm="${path_norm,,}"
        local val val_norm
        if (( ${#INCLUDE_ANALYSES[@]} > 0 )); then
            local found=false
            for val in "${INCLUDE_ANALYSES[@]}"; do
                val_norm="${val//-/}"; val_norm="${val_norm,,}"
                [[ "$path_norm" == *"$val_norm"* ]] && { found=true; break; }
            done
            $found || return 1
        fi
        if (( ${#EXCLUDE_ANALYSES[@]} > 0 )); then
            for val in "${EXCLUDE_ANALYSES[@]}"; do
                val_norm="${val//-/}"; val_norm="${val_norm,,}"
                [[ "$path_norm" == *"$val_norm"* ]] && return 1
            done
        fi
    fi

    return 0
}

# --- Setup --------------------------------------------------------------------
TMPDIR_BASE="$(mktemp -d -p "$SCRIPT_DIR")"
_MAIN_PID=$BASHPID

# Open persistent SSH control sockets so all rsync calls share one connection
# per host — avoids a password prompt for every source directory.
# %C is a short SHA hash of (host,port,user) — keeps socket path under the
# 108-character Unix domain socket limit regardless of temp dir depth.
SSH_CTL_DIR="$HOME/.ssh/ctrl"
mkdir -p "$SSH_CTL_DIR"
chmod 700 "$SSH_CTL_DIR"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CTL_DIR/%C -o ControlPersist=300"
RSYNC_E=(-e "ssh $SSH_OPTS")

_close_ssh() {
    for host in "$REMOTE_HOST" "$PNFS_HOST"; do
        ssh -O exit -o "ControlPath=$SSH_CTL_DIR/%C" "$host" 2>/dev/null || true
    done
    [[ "${BASHPID}" == "${_MAIN_PID}" ]] && rm -rf "$TMPDIR_BASE"
}
trap '_close_ssh' EXIT
trap 'echo "ERROR at line $LINENO: $BASH_COMMAND" >&2' ERR

# --- Print active configuration -----------------------------------------------
echo "==> Syncing SOLAR OUTPUT_ONLY plot data"
echo "    Remote root  : $REMOTE"
echo "    PNFS root    : $PNFS"
echo "    Manifest     : $MANIFEST_PATH"
echo "    Local data   : $DATA_DIR"
$FORCE       && echo "    Mode         : force (overwrite existing)"
$DRY_RUN     && echo "    Mode         : dry-run (no files will be written)"
(( ${#INCLUDE_CONFIGS[@]}  > 0 )) && echo "    +config      : ${INCLUDE_CONFIGS[*]}"
(( ${#EXCLUDE_CONFIGS[@]}  > 0 )) && echo "    -config      : ${EXCLUDE_CONFIGS[*]}"
(( ${#INCLUDE_NAMES[@]}    > 0 )) && echo "    +name        : ${INCLUDE_NAMES[*]}"
(( ${#EXCLUDE_NAMES[@]}    > 0 )) && echo "    -name        : ${EXCLUDE_NAMES[*]}"
(( ${#INCLUDE_FOLDERS[@]}  > 0 )) && echo "    +folder      : ${INCLUDE_FOLDERS[*]}"
(( ${#EXCLUDE_FOLDERS[@]}  > 0 )) && echo "    -folder      : ${EXCLUDE_FOLDERS[*]}"
(( ${#INCLUDE_ENERGIES[@]} > 0 )) && echo "    +energy      : ${INCLUDE_ENERGIES[*]}"
(( ${#EXCLUDE_ENERGIES[@]} > 0 )) && echo "    -energy      : ${EXCLUDE_ENERGIES[*]}"
(( ${#INCLUDE_STUDIES[@]}  > 0 )) && echo "    +study       : ${INCLUDE_STUDIES[*]}"
(( ${#EXCLUDE_STUDIES[@]}  > 0 )) && echo "    -study       : ${EXCLUDE_STUDIES[*]}"
(( ${#INCLUDE_ANALYSES[@]} > 0 )) && echo "    +analysis    : ${INCLUDE_ANALYSES[*]}"
(( ${#EXCLUDE_ANALYSES[@]} > 0 )) && echo "    -analysis    : ${EXCLUDE_ANALYSES[*]}"
(( ${#INCLUDE_THEMES[@]}   > 0 )) && echo "    +theme       : ${INCLUDE_THEMES[*]}"
$PUBLICATION_ONLY && echo "    publication  : only publication_export files"
echo ""

# --- index.json (theme/publication discovery) ---------------------------------
# Additive to the OUTPUT_ONLY sync below: index.json is SOLAR's own file-level
# discovery manifest (output/data/index.json), tagging each file with themes
# and a publication_export flag. Only fetched/consulted when --theme,
# --publication, or --list-themes is passed — default behaviour is unchanged.
FILTERED_RELPATHS=()

if $LIST_THEMES || (( ${#INCLUDE_THEMES[@]} > 0 )) || $PUBLICATION_ONLY; then
    INDEX_LOCAL="$TMPDIR_BASE/index.json"
    echo "--> Fetching index.json ..."
    rsync -az "${RSYNC_E[@]}" "${REMOTE}/${INDEX_PATH}" "$INDEX_LOCAL"

    if $LIST_THEMES; then
        python3 "$SOLAR_INDEX_PY" list-themes --index "$INDEX_LOCAL"
        exit 0
    fi

    INDEX_FILTER_ARGS=()
    for t in "${INCLUDE_THEMES[@]}"; do INDEX_FILTER_ARGS+=(--theme "$t"); done
    $PUBLICATION_ONLY && INDEX_FILTER_ARGS+=(--publication)

    mapfile -t FILTERED_RELPATHS < <(python3 "$SOLAR_INDEX_PY" filter \
        --index "$INDEX_LOCAL" "${INDEX_FILTER_ARGS[@]}")

    echo "==> ${#FILTERED_RELPATHS[@]} file(s) in index.json matched theme/publication filters"
    echo ""
fi

# --- Fetch manifest -----------------------------------------------------------
MANIFEST_LOCAL="$TMPDIR_BASE/pkl_paths.json"
echo "--> Fetching manifest ..."
rsync -az "${RSYNC_E[@]}" "${REMOTE}/${MANIFEST_PATH}" "$MANIFEST_LOCAL"

# --- Parse OUTPUT_ONLY base directories from the manifest --------------------
# For each entry in OUTPUT_ONLY we extract every base/bases/full_path/full_paths
# string, substitute {root} and {PATH}, then truncate at the first remaining
# {template} to yield the widest concrete directory we can rsync from.
# pnfs vs local is inferred per path from its {PATH}/{root} prefix, so entries
# with in_pnfs: "partial" (mixed bases) are handled correctly.
#
# Output lines:  "<pnfs|local> <concrete_directory>"
mapfile -t SOURCE_ENTRIES < <(python3 - "$MANIFEST_LOCAL" \
    "${REMOTE##*:}" "${PNFS##*:}" <<'EOF'
import json, sys, re

manifest_path, root, pnfs_root = sys.argv[1], sys.argv[2], sys.argv[3]

with open(manifest_path) as f:
    data = json.load(f)

def extract_base_strings(obj):
    """Yield path strings from base/bases/full_path/full_paths/base_signal/base_background keys."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("base", "base_signal", "base_background",
                     "full_path", "full_paths", "bases"):
                if isinstance(v, str):
                    yield v
                elif isinstance(v, dict):
                    yield from (s for s in v.values() if isinstance(s, str))
            else:
                yield from extract_base_strings(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from extract_base_strings(item)

def resolve_base(raw, root, pnfs_root):
    """Substitute root variables and truncate at the first remaining template variable."""
    path = raw.replace("{root}", root).replace("{PATH}", pnfs_root)
    match = re.search(r'\{[^}]+\}', path)
    if match:
        path = path[:match.start()].rstrip("/")
    return path or None

# Collect REPRODUCIBILITY base directories — these must never be synced.
# We check against these even if a path accidentally appears in OUTPUT_ONLY
# (e.g. when the remote pkl_paths.json is out of sync with the repo).
repro_bases = set()
for entry_name, entry in data.get("REPRODUCIBILITY", {}).items():
    if entry_name.startswith("_"):
        continue
    for raw in extract_base_strings(entry):
        p = resolve_base(raw, root, pnfs_root)
        if p:
            repro_bases.add(p)

def is_reproducibility(path):
    """True if path is under (or equal to) any REPRODUCIBILITY base directory."""
    return any(path == rb or path.startswith(rb + "/") or rb.startswith(path + "/")
               for rb in repro_bases)

seen = set()
for entry_name, entry in data.get("OUTPUT_ONLY", {}).items():
    if entry_name.startswith("_"):
        continue

    for raw in extract_base_strings(entry):
        path = resolve_base(raw, root, pnfs_root)
        if not path or path in seen:
            continue
        if is_reproducibility(path):
            continue  # skip — belongs to REPRODUCIBILITY, not OUTPUT_ONLY
        # Determine remote type per path: {PATH} prefix → pnfs, {root} → local.
        # This handles in_pnfs: "partial" entries where individual bases differ.
        remote_type = "pnfs" if raw.startswith("{PATH}") else "local"
        seen.add(path)
        print(f"{remote_type} {path}")
EOF
)

if [[ ${#SOURCE_ENTRIES[@]} -eq 0 ]]; then
    echo "ERROR: no OUTPUT_ONLY source directories found in manifest" >&2
    exit 1
fi

# Deduplicate: drop any source whose path is a subdirectory of another source.
DEDUPED_ENTRIES=()
for entry in "${SOURCE_ENTRIES[@]}"; do
    dir="${entry#* }"
    covered=false
    for other in "${SOURCE_ENTRIES[@]}"; do
        other_dir="${other#* }"
        [[ "$other_dir" == "$dir" ]] && continue
        [[ "$dir" == "$other_dir"/* ]] && { covered=true; break; }
    done
    $covered || DEDUPED_ENTRIES+=("$entry")
done
SOURCE_ENTRIES=("${DEDUPED_ENTRIES[@]}")

echo "--> Resolved OUTPUT_ONLY source directories:"
for entry in "${SOURCE_ENTRIES[@]}"; do
    kind="${entry%% *}"
    dir="${entry#* }"
    host="$( [[ "$kind" == "pnfs" ]] && echo "$PNFS_HOST" || echo "$REMOTE_HOST" )"
    echo "    [$kind] $host:$dir"
done
echo ""

$SHOW_SOURCES && exit 0

# --- Preview: list only the files that pass active filters -------------------
# --list-only prints the remote file listing without syncing, honouring the
# same --include/--exclude rules. Output format: "perms size date time path"
# — we extract $NF (last field = path) and filter to *.pkl lines.
PREVIEW_COUNT=0
PREVIEW_BYTES=0
ACTIVE_SOURCES=()   # source dirs that had at least one matching file

echo "--> Scanning ${#SOURCE_ENTRIES[@]} source director(ies) for matching files..."
echo ""

for entry in "${SOURCE_ENTRIES[@]}"; do
    kind="${entry%% *}"
    dir="${entry#* }"
    [[ "$kind" == "pnfs" ]] && continue
    host="$REMOTE_HOST"
    remote_src="${host}:${dir}/"

    printf "    scanning %-60s\r" "${dir}/"

    # Each hit is stored as "raw_bytes human_size rel_path"
    source_hits=()
    while IFS=' ' read -r raw fmt rel; do
        matches_filter "${dir}/${rel}" || continue
        source_hits+=("$raw $fmt $rel")
        PREVIEW_BYTES=$(( PREVIEW_BYTES + raw ))
    done < <(rsync --list-only -r "${RSYNC_E[@]}" \
        --exclude='*_calib/' \
        --include='*.pkl' --include='*/' --exclude='*' \
        "$remote_src" 2>/dev/null \
        | awk '/\.pkl/{
            gsub(",","",$2); b=$2+0
            if     (b>=1073741824) s=sprintf("%.1fG", b/1073741824)
            else if(b>=1048576)    s=sprintf("%.1fM", b/1048576)
            else if(b>=1024)       s=sprintf("%.1fK", b/1024)
            else                   s=sprintf("%dB",   b)
            print b, s, $NF
        }' || true)

    if (( ${#source_hits[@]} > 0 )); then
        printf "%-72s\n" ""   # clear the \r line
        echo "    [local] ${host}:${dir}/"
        for hit in "${source_hits[@]}"; do
            raw="${hit%% *}"; rest="${hit#* }"; fmt="${rest%% *}"; rel="${rest#* }"
            printf "        %-8s %s\n" "$fmt" "$rel"
        done
        echo ""
        PREVIEW_COUNT=$(( PREVIEW_COUNT + ${#source_hits[@]} ))
        ACTIVE_SOURCES+=("$entry")   # remember only sources with hits
    fi
done

printf "\r\033[K"   # clear last scanning line (width-independent — dir paths vary in length)

# --- Preview: index.json theme/publication-selected files --------------------
# These are explicit output/data/-relative file paths from index.json. Skip
# anything already reachable through an OUTPUT_ONLY "local" source directory
# above — otherwise the same physical file gets counted (and rsynced) twice,
# once per discovery mechanism. Byte sizes aren't queried per-file here, so
# surviving entries aren't reflected in PREVIEW_BYTES.
INDEX_SELECTED=()
if (( ${#FILTERED_RELPATHS[@]} > 0 )); then
    LOCAL_SOURCE_DIRS=()
    for entry in "${SOURCE_ENTRIES[@]}"; do
        [[ "${entry%% *}" == "local" ]] && LOCAL_SOURCE_DIRS+=("${entry#* }")
    done

    for rel in "${FILTERED_RELPATHS[@]}"; do
        matches_filter "output/data/$rel" || continue

        full_path="${REMOTE##*:}/output/data/${rel}"
        covered=false
        for dir in "${LOCAL_SOURCE_DIRS[@]}"; do
            if [[ "$full_path" == "$dir" || "$full_path" == "$dir"/* ]]; then
                covered=true
                break
            fi
        done
        $covered || INDEX_SELECTED+=("$rel")
    done

    if (( ${#INDEX_SELECTED[@]} > 0 )); then
        echo "    [index] theme/publication-selected files under output/data/ (not already covered above):"
        for rel in "${INDEX_SELECTED[@]}"; do
            printf "        %s\n" "$rel"
        done
        echo ""
        PREVIEW_COUNT=$(( PREVIEW_COUNT + ${#INDEX_SELECTED[@]} ))
    fi
fi

TOTAL_FMT=$(awk -v b="$PREVIEW_BYTES" 'BEGIN{
    if     (b>=1073741824) printf "%.1f GB", b/1073741824
    else if(b>=1048576)    printf "%.1f MB", b/1048576
    else if(b>=1024)       printf "%.1f KB", b/1024
    else                   printf "%d B",    b
}')
echo "==> ${PREVIEW_COUNT} file(s) selected  (${TOTAL_FMT})"
echo ""

if (( PREVIEW_COUNT == 0 )); then
    echo "    Nothing to download."
    exit 0
fi

$DRY_RUN && { echo "    (dry-run — no files will be written)"; exit 0; }

read -r -p "Proceed with download? [y/N] " _confirm
[[ "$_confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 2; }

# --- Download each source directory -------------------------------------------
echo "--> Downloading ${PREVIEW_COUNT} file(s) (${TOTAL_FMT})..."

for entry in "${ACTIVE_SOURCES[@]}"; do
    kind="${entry%% *}"
    dir="${entry#* }"
    remote_src="${REMOTE_HOST}:${dir}/"
    local_tmp="$TMPDIR_BASE/$(echo "$dir" | tr '/' '_')"
    mkdir -p "$local_tmp"
    echo "    rsync $remote_src"
    rsync -az "${RSYNC_E[@]}" \
        --exclude='*_calib/' \
        --include='*.pkl' --include='*/' --exclude='*' \
        "$remote_src" "$local_tmp/" || true
done

for rel in "${INDEX_SELECTED[@]}"; do
    remote_src="${REMOTE_HOST}:${REMOTE##*:}/output/data/${rel}"
    local_dest="$TMPDIR_BASE/_index_selected/${rel}"
    mkdir -p "$(dirname "$local_dest")"
    echo "    rsync $remote_src"
    rsync -az "${RSYNC_E[@]}" "$remote_src" "$local_dest" || true
done

TOTAL_FETCHED=$(find "$TMPDIR_BASE" -name '*.pkl' | wc -l)
echo "    Downloaded ${TOTAL_FETCHED} file(s)"
echo ""

# --- Flatten, filter, and copy to input/data/ ---------------------------------
NEW=0; SKIPPED=0; UPDATED=0

while IFS= read -r -d '' src; do
    matches_filter "$src" || continue

    base="$(basename "$src")"
    dest="$DATA_DIR/$base"

    if [[ -f "$dest" ]] && ! $FORCE; then (( SKIPPED++ )) || true; continue; fi

    if [[ -f "$dest" ]]; then cp "$src" "$dest"; (( UPDATED++ )) || true
    else                      cp "$src" "$dest"; (( NEW++     )) || true; fi
done < <(find "$TMPDIR_BASE" -name '*.pkl' -print0)

# --- Summary ------------------------------------------------------------------
echo "==> Done"
echo "    New      : $NEW"
echo "    Updated  : $UPDATED"
echo "    Skipped  : $SKIPPED  (use --force to overwrite)"
