#!/usr/bin/env bash
# update_plots.sh — Activate venv, optionally sync remote data, run a named
# batch of plot scripts, and report results.
#
# Usage:
#   ./update_plots.sh -s <script_set> [OPTIONS]
#
# Required:
#   -s, --script-set NAME        Batch to run: solar, thesis, lowe, reco, all
#                                (must match a file in input/plots/{NAME}_scripts.txt)
#
# Options:
#   --sync                       Pull latest .pkl data from remote before plotting
#   --remote HOST:PATH           Override default SOLAR remote (passed to sync_solar_data.sh)
#   --pnfs HOST:PATH             Override default PNFS root (passed to sync_solar_data.sh)
#   --force-sync                 Overwrite existing local data files during sync
#   --dry-run-sync               Show what sync would do without copying files
#   --tables                     Also run the matching table script set
#   -h, --help                   Show this help and exit
#
# Content filters (only applied when --sync is active):
#   --flags  DIM [DIM ...]       Filter dimensions to apply: any of
#                                  name  config  folder  energy
#                                  (prefix with 'no-' to exclude instead of include)
#   --variables VAL [VAL ...]    Values corresponding 1-to-1 with --flags
#
#   --flags and --variables must have the same number of arguments.
#   Each pair (DIM, VAL) translates to --DIM VAL on sync_solar_data.sh:
#     name   → --name VAL        (include only files matching sample name)
#     config → --config VAL      (include only files matching detector config)
#     folder → --folder VAL      (include only files whose path contains folder)
#     energy → --energy VAL      (include only files matching energy label)
#   Prefix with 'no-' to exclude instead:
#     no-name → --exclude-name VAL,  no-config → --exclude-config VAL, etc.
#
# Examples:
#   ./update_plots.sh -s solar --sync
#   ./update_plots.sh -s thesis
#   ./update_plots.sh -s solar --sync \
#       --flags name config folder energy \
#       --variables marley hd_1x2x6_centralAPA Truncated SolarEnergy
#   ./update_plots.sh -s solar --sync \
#       --flags name name no-folder \
#       --variables marley gamma Truncated
#   ./update_plots.sh -s all --sync --force-sync --tables

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv/bin/activate"
SYNC_SCRIPT="$SCRIPT_DIR/sync_solar_data.sh"

SCRIPT_SET=""
DO_SYNC=false
DO_TABLES=false
REMOTE_ARG=""
PNFS_ARG=""
FORCE_SYNC=false
DRY_RUN_SYNC=false
FILTER_FLAGS=()
FILTER_VARS=()

# --- Argument parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--script-set)  SCRIPT_SET="$2"; shift 2 ;;
        --sync)           DO_SYNC=true; shift ;;
        --remote)         REMOTE_ARG="$2"; shift 2 ;;
        --pnfs)           PNFS_ARG="$2";   shift 2 ;;
        --force-sync)     FORCE_SYNC=true; shift ;;
        --dry-run-sync)   DRY_RUN_SYNC=true; shift ;;
        --tables)         DO_TABLES=true; shift ;;
        --flags)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                FILTER_FLAGS+=("$1"); shift
            done ;;
        --variables)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                FILTER_VARS+=("$1"); shift
            done ;;
        -h|--help)
            awk 'NR>1{if(/^#/){sub(/^# ?/,""); print} else if(NF){exit}}' "$0"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Validate --flags / --variables pairing
if [[ ${#FILTER_FLAGS[@]} -ne ${#FILTER_VARS[@]} ]]; then
    echo "Error: --flags and --variables must have the same number of arguments." >&2
    echo "       Got ${#FILTER_FLAGS[@]} flag(s) and ${#FILTER_VARS[@]} variable(s)." >&2
    exit 1
fi

if [[ -z "$SCRIPT_SET" ]]; then
    echo "Error: -s/--script-set is required." >&2
    echo "       Run with --help for usage." >&2
    exit 1
fi

PLOT_LIST="$SCRIPT_DIR/input/plots/${SCRIPT_SET}_scripts.txt"
if [[ ! -f "$PLOT_LIST" ]]; then
    echo "Error: no script list found at $PLOT_LIST" >&2
    echo "       Available sets: $(ls "$SCRIPT_DIR/input/plots/"*_scripts.txt | \
        sed 's|.*/||; s|_scripts.txt||' | tr '\n' ' ')" >&2
    exit 1
fi

# --- Virtualenv ---------------------------------------------------------------
if [[ ! -f "$VENV" ]]; then
    echo "Error: virtualenv not found at $VENV" >&2
    echo "       Run 'source setup.sh' first to set up the environment." >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$VENV"

# --- Optional data sync -------------------------------------------------------
if $DO_SYNC; then
    echo "==> Syncing remote SOLAR data..."
    SYNC_ARGS=()
    [[ -n "$REMOTE_ARG" ]] && SYNC_ARGS+=(--remote "$REMOTE_ARG")
    [[ -n "$PNFS_ARG"   ]] && SYNC_ARGS+=(--pnfs   "$PNFS_ARG")
    $FORCE_SYNC             && SYNC_ARGS+=(--force)
    $DRY_RUN_SYNC           && SYNC_ARGS+=(--dry-run)

    # Translate --flags / --variables pairs into sync_solar_data.sh filter flags.
    # 'no-DIM' prefixes become --exclude-DIM; plain 'DIM' become --DIM.
    for i in "${!FILTER_FLAGS[@]}"; do
        dim="${FILTER_FLAGS[$i]}"
        val="${FILTER_VARS[$i]}"
        case "$dim" in
            name      ) SYNC_ARGS+=(--name           "$val") ;;
            no-name   ) SYNC_ARGS+=(--exclude-name   "$val") ;;
            config    ) SYNC_ARGS+=(--config          "$val") ;;
            no-config ) SYNC_ARGS+=(--exclude-config  "$val") ;;
            folder    ) SYNC_ARGS+=(--folder          "$val") ;;
            no-folder ) SYNC_ARGS+=(--exclude-folder  "$val") ;;
            energy    ) SYNC_ARGS+=(--energy          "$val") ;;
            no-energy ) SYNC_ARGS+=(--exclude-energy  "$val") ;;
            *) echo "Warning: unknown filter dimension '$dim' — ignored" >&2 ;;
        esac
    done

    bash "$SYNC_SCRIPT" "${SYNC_ARGS[@]}" || {
        _sync_exit=$?
        # Exit code 2 = user declined the download prompt — skip plotting.
        [[ $_sync_exit -eq 2 ]] && { echo "Download aborted — skipping plots."; exit 0; }
        exit "$_sync_exit"
    }
    echo ""
fi

# --- Plot generation ----------------------------------------------------------
START_TIME=$(date +%s)

echo "==> Running plot batch: $SCRIPT_SET"
echo "    Script list : $PLOT_LIST"
echo ""

python3 "$SCRIPT_DIR/run_plot_scripts.py" -s "$SCRIPT_SET"

if $DO_TABLES; then
    TABLE_LIST="$SCRIPT_DIR/input/tables/${SCRIPT_SET}_scripts.txt"
    if [[ -f "$TABLE_LIST" ]]; then
        echo ""
        echo "==> Running table batch: $SCRIPT_SET"
        python3 "$SCRIPT_DIR/run_table_scripts.py" -s "$SCRIPT_SET"
    else
        echo "    (no table list found for '$SCRIPT_SET' — skipping)"
    fi
fi

# --- Summary ------------------------------------------------------------------
END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))

echo ""
echo "==> Done in ${ELAPSED}s"

# Show output destinations from output_paths.json if jq is available
if command -v jq &>/dev/null; then
    PATHS=$(jq -r --arg key "$SCRIPT_SET" '.plots[$key]? // [] | .[]' \
        "$SCRIPT_DIR/config/output_paths.json" 2>/dev/null || true)
    if [[ -n "$PATHS" ]]; then
        echo "    Output paths:"
        while IFS= read -r p; do
            COUNT=$(find "$p" -name '*.png' 2>/dev/null | wc -l)
            printf "      %-60s (%s PNG files)\n" "$p" "$COUNT"
        done <<< "$PATHS"
    fi
fi
