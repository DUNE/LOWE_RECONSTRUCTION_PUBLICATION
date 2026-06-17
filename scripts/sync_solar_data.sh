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
#
# Filter logic: all filters are matched against the full remote path and filename.
# Include filters are OR-ed within a dimension; all dimensions must pass (AND).
#
# Examples:
#   ./sync_solar_data.sh
#   ./sync_solar_data.sh --config hd_1x2x6_centralAPA --name marley
#   ./sync_solar_data.sh --name marley --name gamma --exclude-folder Truncated
#   ./sync_solar_data.sh --energy SolarEnergy --force
#   ./sync_solar_data.sh --show-sources

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/input/data"
MANIFEST_PATH="config/analysis/pkl_paths.json"

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
    return 0
}

# --- Setup --------------------------------------------------------------------
TMPDIR_BASE="$(mktemp -d -p "$SCRIPT_DIR")"

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
    rm -rf "$TMPDIR_BASE"
}
trap '_close_ssh' EXIT

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
echo ""

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

printf "%-72s\r" ""   # clear last scanning line

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

# Background progress bar: polls TMPDIR_BASE for .pkl files while rsync runs.
_progress_bar() {
    local total=$1 tmpdir=$2 bar_width=40
    local count pct filled bar elapsed
    local start; start=$(date +%s)
    while true; do
        count=$(find "$tmpdir" -name '*.pkl' 2>/dev/null | wc -l)
        (( count > total )) && count=$total   # cap: extra files don't pass filter
        elapsed=$(( $(date +%s) - start ))
        pct=$(( total > 0 ? count * 100 / total : 0 ))
        filled=$(( total > 0 ? count * bar_width / total : 0 ))
        bar=$(printf '%*s' "$filled" '' | tr ' ' '=')
        [[ $filled -lt $bar_width ]] && bar+=">"
        printf '\r    [%-*s] %3d%%  %d/%d files  %ds elapsed' \
            "$bar_width" "$bar" "$pct" "$count" "$total" "$elapsed"
        (( count >= total )) && break
        sleep 1
    done
}
_progress_bar "$PREVIEW_COUNT" "$TMPDIR_BASE" &
_PROG_PID=$!

for entry in "${ACTIVE_SOURCES[@]}"; do   # only sources with matching files
    kind="${entry%% *}"
    dir="${entry#* }"
    remote_src="${REMOTE_HOST}:${dir}/"

    local_tmp="$TMPDIR_BASE/$(echo "$dir" | tr '/' '_')"
    mkdir -p "$local_tmp"

    rsync -az "${RSYNC_E[@]}" \
        --exclude='*_calib/' \
        --include='*.pkl' --include='*/' --exclude='*' \
        "$remote_src" "$local_tmp/" 2>/dev/null || true
done

kill "$_PROG_PID" 2>/dev/null; wait "$_PROG_PID" 2>/dev/null || true
TOTAL_FETCHED=$(find "$TMPDIR_BASE" -name '*.pkl' 2>/dev/null | wc -l)
printf '\r%-80s\n' ""
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
