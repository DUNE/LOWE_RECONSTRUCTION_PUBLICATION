#!/usr/bin/env bash
# sync_solar_data.sh — Pull SOLAR study results (plot-ready .pkl files) from a
# remote SOLAR installation into local input/data/.
#
# The sync is driven by the study registry in src/lib/solar_studies.py, which
# mirrors SOLAR's lib/study.py STUDY_VARIANTS: it encodes which study labels
# are live, in which background folder(s) and analyses each one is run, and
# where every result family lives under SOLAR's output/data/:
#
#   analysis/{day-night|hep|sensitivity}/{config}/marley/{folder}/{label}/{config}_marley_{Analysis}_{Kind}.pkl
#   solar/cutflow/{config}/{name}/{folder}/{analysis}/{config}_{name}_{Energy}_{Analysis}_Cutflow{suffix}.pkl
#   solar/nhits/{config}/{name}/truncated/{daynight|hep}/{config}_{name}_Weighted_Distributions_Fiducial_{Analysis}.pkl
#   {subdir}/{config}/{name}/{config}_{name}_{Kind}.pkl                              flat families
#
# Flat families are SOLAR trees without folder/label/analysis levels, each with
# its own --study selector (FLAT_FAMILIES in the registry lists the folders, the
# exact case-sensitive kinds and the synced config x name selections):
#   reconstruction  vertex/*, TPC/*, PDS/*, preselection/*  (marley x 4 configs regenerated
#                   2026-09-24; marley_official for the lowe paper; backgrounds, scans, legacy configs)
#   calibration     workflow/calibration, workflow/correction
#   workflow        workflow/reconstruction, workflow/discrimination, workflow/wire_comparison
#   marley          marley/stacked
#   background      background (global and per-config spectra summaries)
#   event           event (event displays, energy-deposition studies)
#   analysisdata    solar/weighted (per-component SolarEnergy_Sensitivity_AnalysisData)
# Legacy kinds still on the remote (the *_NHits{N} splits, Reco_NHit_Efficiency_*,
# AdjCluster_Distributions, Adjacent_Cluster_Counts_slim, nested sub-folders, ...)
# are never fetched; --check-remote-labels lists unknown ones.

# Retired label directories still present on the remote, the pre-August-2026
# pkls sitting directly in {folder}/, and the multi-hundred-MB
# Weighted_Distributions.pkl dumps are never fetched. SOLAR's output/data/
# index.json and pkl_paths.json are not consulted.
#
# Two steps per run:
#   1. rsync the selected remote files into a persistent mirror
#      (input/data/.solar_mirror/, same tree as the remote) — incremental, so
#      re-runs only transfer what changed upstream; remote deletions propagate.
#   2. Route the mirror into the local layout the plot macros read (one copy per
#      file, nothing flat in input/data itself; see docs/input_data_layout.md):
#        input/data/studies/{folder}/{label}/{config}_{name}_{...}.pkl
#                         analysis results, cutflows (the label directory replaces the
#                         _fiduc_truth suffix) and, in truncated/default, the nhits
#                         distributions. A bare --datafile falls back to truncated/default.
#        input/data/studies/{folder}/{label}/{daynight|hep|sensitivity}/{...}.pkl
#                         analysis-agnostic basenames (Oscillogram, Signal1D_*)
#        input/data/{subdir}/{config}_{name}_{Kind}.pkl
#                         flat families; commands pass --path {subdir}
#      A file is (re)copied whenever the mirror copy differs from the local one.
#
# The run ends with a per-family summary (Counts, Exposure, Contours,
# 10Y_Contours, Cutflow, Weighted and the flat families), the list of expected
# files that do not exist on the remote, and a warning for flat-family pkls whose
# content is identical across configs once Config/Version/Geometry are dropped
# (a sign that one sample is a copy of another config's ntuple).
#
# Usage:
#   ./sync_solar_data.sh [OPTIONS]
#
# Core options:
#   --remote HOST:PATH       Remote SOLAR root directory
#                            Default: gae_out:/pc/choozdsk01/users/manthey/SOLAR
#   --force                  Re-copy every routed file even if unchanged
#   --dry-run                List what rsync would transfer and exit (no copies)
#   --show-sources           Print the rsync include rules and exit
#   --prune-legacy           Delete the flat input/data/studies/*.pkl files of the
#                            previous (collision-prone) layout after routing
#   --check-remote-labels    Also list study label directories and reconstruction
#                            kinds on the remote that the registry does not know
#                            (new or renamed studies/outputs; dead ones are counted)
#   -y, --yes                Skip the "Proceed with download?" confirmation
#                            prompt — required for unattended/non-interactive runs
#   -h, --help               Show this help and exit
#
# Data selection:
#   --truth-position         Fetch only the truth-position export (17 pandas pickles, README.md,
#                            meta.json) from SOLAR's output/data/solar/truth_position/export_repo/
#                            into input/data/truth_position/ instead of the study results.
#                            Content filters do not apply; --dry-run and --yes are honoured.
#                            Plots/tables: python run_plot_scripts.py -s truth_position
#                                          python run_table_scripts.py -s truth_position
#                            Regenerate on the SOLAR side (about 10 min):
#                              python src/physics/signal/truth_position_study.py --stage export
#
#   --study-status            Fetch the newest study_status_<timestamp>.md report from SOLAR's
#                            output/logs/ (the timestamped file, not the named variants like
#                            study_status_orange.md) into input/status/study_status.md, always
#                            overwriting that one fixed filename — no timestamped copies pile up
#                            locally. Content filters do not apply; --dry-run and --yes are honoured.
#
# Non-interactive SSH auth:
#   --ssh-password-file PATH  File containing the SSH password, fed to every
#                            ssh/rsync connection via sshpass instead of
#                            prompting on the terminal. Default: ~/.solar_sync_pass
#                            (used automatically when it exists; requires
#                            'sshpass' to be installed; chmod 600 recommended).
#
# Content filters (each flag accepts one value; repeat to allow multiple):
#   --config VALUE           Detector config (hd_1x2x6_centralAPA, ...)
#   --name VALUE             Sample name (marley, gamma, neutron, radiological)
#   --folder VALUE           Background folder (truncated, nominal, reduced)
#   --study VALUE            Study label (charge_Q50, ...) or group (charge, unc, ...);
#                            a flat-family selector (reconstruction, calibration, workflow,
#                            marley, background, event, analysisdata) selects that family only
#   --analysis VALUE         daynight, hep or sensitivity (any spelling)
#   --energy VALUE           Cutflow energy label (SolarEnergy, SelectedEnergy, ...)
#   --exclude-<dim> VALUE    Exclude instead of include, for every dimension above
#
#   Include filters are OR-ed within a dimension; all dimensions must pass (AND).
#   Filters narrow both what is fetched and the completeness report.
#   Flat-family files have no folder/study/analysis/energy: an include filter on
#   any of those drops them (except --study <family>); --config filters and
#   --name replaces the sample names of the family's selections.
#
# Deletion scope: --delete/--delete-excluded only act inside the rsync
# destination, the mirror input/data/.solar_mirror/, and only in the trees that
# have include rules this run. Routing into input/data only copies (overwrites
# files it owns, never deletes); --prune-legacy deletes nothing but the flat
# input/data/studies/*.pkl files of the old layout.
#
# Deprecated (accepted, ignored with a warning): --pnfs, --theme,
#   --publication, --list-themes — index.json discovery is gone.
#
# Examples:
#   ./sync_solar_data.sh
#   ./sync_solar_data.sh --config hd_1x2x6_centralAPA --analysis sensitivity
#   ./sync_solar_data.sh --study charge --study default
#   ./sync_solar_data.sh --study reconstruction     # only the reconstruction pkls
#   ./sync_solar_data.sh --study calibration --study workflow
#   ./sync_solar_data.sh --yes --prune-legacy       # unattended full re-sync
#   ./sync_solar_data.sh --dry-run
#   ./sync_solar_data.sh --show-sources
#   ./sync_solar_data.sh --truth-position           # only the truth-position export
#   ./sync_solar_data.sh --study-status              # only the latest study-status report

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$SCRIPT_DIR/input/data"
MIRROR_DIR="$DATA_DIR/.solar_mirror"
REGISTRY_PY="$SCRIPT_DIR/src/lib/solar_studies.py"
REMOTE_DATA_SUBDIR="output/data"

DEFAULT_REMOTE="gae_out:/pc/choozdsk01/users/manthey/SOLAR"
REMOTE="$DEFAULT_REMOTE"
FORCE=false
DRY_RUN=false
SHOW_SOURCES=false
AUTO_YES=false
PRUNE_LEGACY=false
CHECK_REMOTE_LABELS=false
TRUTH_POSITION=false
TRUTH_POSITION_SUBDIR="solar/truth_position/export_repo"   # under output/data/ on the remote
STUDY_STATUS=false
REMOTE_LOGS_SUBDIR="output/logs"                            # under REMOTE_ROOT on the remote
STUDY_STATUS_LOCAL="$SCRIPT_DIR/input/status/study_status.md"

DEFAULT_SSH_PASSWORD_FILE="$HOME/.solar_sync_pass"
SSH_PASSWORD_FILE="$DEFAULT_SSH_PASSWORD_FILE"

FILTER_ARGS=()   # passed verbatim to the registry CLI

# --- Argument parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --remote)          REMOTE="$2";                  shift 2 ;;
        --force)           FORCE=true;                   shift   ;;
        --dry-run)         DRY_RUN=true;                 shift   ;;
        --show-sources)    SHOW_SOURCES=true;            shift   ;;
        --prune-legacy)    PRUNE_LEGACY=true;            shift   ;;
        --check-remote-labels) CHECK_REMOTE_LABELS=true; shift   ;;
        --truth-position)  TRUTH_POSITION=true;              shift   ;;
        --study-status)    STUDY_STATUS=true;                shift   ;;
        -y|--yes)          AUTO_YES=true;                shift   ;;
        --ssh-password-file) SSH_PASSWORD_FILE="$2";     shift 2 ;;
        --config|--exclude-config|--name|--exclude-name|--folder|--exclude-folder|\
        --study|--exclude-study|--analysis|--exclude-analysis|--energy|--exclude-energy)
            FILTER_ARGS+=("$1" "$2");                    shift 2 ;;
        --pnfs|--theme)
            echo "WARNING: $1 is no longer supported (index.json discovery removed); ignored." >&2
            shift 2 ;;
        --publication|--list-themes)
            echo "WARNING: $1 is no longer supported (index.json discovery removed); ignored." >&2
            shift ;;
        -h|--help)
            awk 'NR>1{if(/^#/){sub(/^# ?/,""); print} else if(NF){exit}}' "$0"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

REMOTE="${REMOTE%/}"
REMOTE_HOST="${REMOTE%%:*}"
REMOTE_ROOT="${REMOTE#*:}"
REMOTE_DATA="${REMOTE_ROOT}/${REMOTE_DATA_SUBDIR}"

# --- Setup --------------------------------------------------------------------
TMPDIR_BASE="$(mktemp -d)"
_MAIN_PID=$BASHPID

SSH_CTL_DIR="$HOME/.ssh/ctrl"
mkdir -p "$SSH_CTL_DIR"
chmod 700 "$SSH_CTL_DIR"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CTL_DIR/%C -o ControlPersist=300"

# --- Non-interactive SSH auth (optional) ---------------------------------------
# sshpass can only answer ONE password prompt per ssh process. When REMOTE_HOST
# goes through a ProxyJump hop that also asks for a password, run that hop as
# its own ssh process (explicit ProxyCommand) wrapped in its own sshpass.
SSH_CMD="ssh"
if [[ -f "$SSH_PASSWORD_FILE" ]]; then
    if ! command -v sshpass >/dev/null 2>&1; then
        echo "ERROR: $SSH_PASSWORD_FILE exists but 'sshpass' is not installed." >&2
        exit 1
    fi
    PASS_FILE_PERM="$(stat -c '%a' "$SSH_PASSWORD_FILE" 2>/dev/null || stat -f '%Lp' "$SSH_PASSWORD_FILE" 2>/dev/null || true)"
    if [[ -n "$PASS_FILE_PERM" && "$PASS_FILE_PERM" != "600" ]]; then
        echo "WARNING: $SSH_PASSWORD_FILE is not chmod 600 (found: $PASS_FILE_PERM)." >&2
    fi
    SSHPASS_SSH="sshpass -f $SSH_PASSWORD_FILE ssh"
    JUMP_HOST="$(ssh -G "$REMOTE_HOST" 2>/dev/null | awk '$1=="proxyjump"{print $2; exit}')"
    if [[ -n "$JUMP_HOST" && "$JUMP_HOST" != "none" ]]; then
        SSH_CMD="$SSHPASS_SSH -o 'ProxyCommand=$SSHPASS_SSH -W %h:%p $JUMP_HOST'"
        echo "==> Using non-interactive SSH auth via $SSH_PASSWORD_FILE (through jump host $JUMP_HOST)"
    else
        SSH_CMD="$SSHPASS_SSH"
        echo "==> Using non-interactive SSH auth via $SSH_PASSWORD_FILE"
    fi
fi
RSYNC_E=(-e "$SSH_CMD $SSH_OPTS")

_close_ssh() {
    ssh -O exit -o "ControlPath=$SSH_CTL_DIR/%C" "$REMOTE_HOST" 2>/dev/null || true
    [[ "${BASHPID}" == "${_MAIN_PID}" ]] && rm -rf "$TMPDIR_BASE"
}
trap '_close_ssh' EXIT
trap 'echo "ERROR at line $LINENO: $BASH_COMMAND" >&2' ERR

# Plain ssh for one-off remote commands (same auth/control socket as rsync).
# $1 is a single shell command string executed on the remote.
_remote_sh() {
    local cmd="$1"
    eval "$SSH_CMD $SSH_OPTS \"\$REMOTE_HOST\" \"\$cmd\""
}

# rsync exit codes 23/24 mean "some files vanished or could not be read";
# everything else transferred, so keep going and let the completeness report
# show what is missing.
_rsync_tolerant() {
    local rc=0
    rsync "$@" || rc=$?
    if (( rc != 0 && rc != 23 && rc != 24 )); then
        echo "ERROR: rsync failed with exit code $rc" >&2
        return "$rc"
    fi
    (( rc != 0 )) && echo "    WARNING: rsync reported partial transfer (exit $rc); see the completeness report" >&2
    return 0
}

# --- Truth-position export (--truth-position): a flat folder of pickles, no registry ---
if $TRUTH_POSITION; then
    TP_DIR="$DATA_DIR/truth_position"
    if (( ${#FILTER_ARGS[@]} > 0 )); then
        echo "WARNING: content filters (${FILTER_ARGS[*]}) do not apply to --truth-position; ignored." >&2
    fi
    echo "==> Syncing the truth-position export"
    echo "    Remote : ${REMOTE_HOST}:${REMOTE_DATA}/${TRUTH_POSITION_SUBDIR}/"
    echo "    Local  : $TP_DIR"
    TP_ARGS=(-az --itemize-changes --out-format='%n' "${RSYNC_E[@]}"
             "${REMOTE_HOST}:${REMOTE_DATA}/${TRUTH_POSITION_SUBDIR}/" "$TP_DIR/")
    $DRY_RUN && TP_ARGS=(-n "${TP_ARGS[@]}")
    mkdir -p "$TP_DIR"
    if ! $DRY_RUN && ! $AUTO_YES; then
        read -r -p "Proceed with download? [y/N] " _confirm
        [[ "$_confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 2; }
    fi
    _rsync_tolerant "${TP_ARGS[@]}" | sed 's/^/    /'
    if $DRY_RUN; then
        echo "    (dry-run — nothing written)"
    else
        echo "==> $(find "$TP_DIR" -maxdepth 1 -name '*.pkl' | wc -l) pickle(s) in $TP_DIR (meta.json: $(sed -n 's/.*"generated": "\(.*\)",/\1/p' "$TP_DIR/meta.json" 2>/dev/null))"
    fi
    exit 0
fi

# --- Study-status report (--study-status): newest study_status_<timestamp>.md, one local copy ---
if $STUDY_STATUS; then
    if (( ${#FILTER_ARGS[@]} > 0 )); then
        echo "WARNING: content filters (${FILTER_ARGS[*]}) do not apply to --study-status; ignored." >&2
    fi
    REMOTE_LOGS="${REMOTE_ROOT}/${REMOTE_LOGS_SUBDIR}"
    echo "==> Syncing the latest study-status report"
    echo "    Remote : ${REMOTE_HOST}:${REMOTE_LOGS}/"
    LATEST_NAME="$(_remote_sh "ls -1 '${REMOTE_LOGS}' 2>/dev/null | grep -E '^study_status_[0-9]{8}_[0-9]{6}\.md\$' | sort | tail -n1")"
    if [[ -z "$LATEST_NAME" ]]; then
        echo "ERROR: no study_status_<timestamp>.md file found under ${REMOTE_LOGS}" >&2
        exit 1
    fi
    echo "    Latest : $LATEST_NAME"
    echo "    Local  : $STUDY_STATUS_LOCAL (fixed name — always overwritten, no timestamped copies kept)"
    if ! $DRY_RUN && ! $AUTO_YES; then
        read -r -p "Proceed with download? [y/N] " _confirm
        [[ "$_confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 2; }
    fi
    if $DRY_RUN; then
        echo "    (dry-run — nothing written)"
    else
        mkdir -p "$(dirname "$STUDY_STATUS_LOCAL")"
        _rsync_tolerant -az "${RSYNC_E[@]}" "${REMOTE_HOST}:${REMOTE_LOGS}/${LATEST_NAME}" "$STUDY_STATUS_LOCAL"
        echo "==> $STUDY_STATUS_LOCAL updated from $LATEST_NAME"
    fi
    exit 0
fi

# --- Print active configuration -----------------------------------------------
echo "==> Syncing SOLAR study results"
echo "    Remote data  : ${REMOTE_HOST}:${REMOTE_DATA}"
echo "    Mirror       : $MIRROR_DIR"
echo "    Local data   : $DATA_DIR"
$FORCE        && echo "    Mode         : force (re-copy every routed file)"
$DRY_RUN      && echo "    Mode         : dry-run (no files will be written)"
$PRUNE_LEGACY && echo "    Prune        : delete flat input/data/studies/*.pkl after routing"
(( ${#FILTER_ARGS[@]} > 0 )) && echo "    Filters      : ${FILTER_ARGS[*]}"
echo ""

# --- Build rsync include rules from the registry -------------------------------
RULES_FILE="$TMPDIR_BASE/rules.txt"
python3 "$REGISTRY_PY" rules "${FILTER_ARGS[@]}" > "$RULES_FILE"
N_RULES=$(grep -c '\.pkl' "$RULES_FILE" || true)
echo "--> ${N_RULES} include rule(s) generated from the study registry"

RSYNC_COMMON=(
    -az --relative --prune-empty-dirs
    --delete --delete-excluded
    --include-from="$RULES_FILE" --exclude='*'
    --out-format='%n'
)
# Only trees with at least one include rule become rsync sources (the registry's
# `sources` command): --delete-excluded acts inside every source, so e.g.
# --study reconstruction must not empty the mirror's analysis/ and solar/ trees.
RSYNC_SOURCES=()
for _tree in $(python3 "$REGISTRY_PY" sources "${FILTER_ARGS[@]}"); do
    if (( ${#RSYNC_SOURCES[@]} == 0 )); then
        RSYNC_SOURCES+=("${REMOTE_HOST}:${REMOTE_DATA}/./${_tree}")
    else
        RSYNC_SOURCES+=(":${REMOTE_DATA}/./${_tree}")
    fi
done
if (( ${#RSYNC_SOURCES[@]} == 0 )); then
    echo "ERROR: the filters select nothing (no include rule generated)" >&2
    exit 1
fi

if $SHOW_SOURCES; then
    echo ""
    echo "    rsync sources (relative to ${REMOTE_HOST}:${REMOTE_DATA}; only trees with rules):"
    printf '        %s/\n' "${RSYNC_SOURCES[@]##*/./}"
    echo "    include rules:"
    sed 's/^/        /' "$RULES_FILE"
    exit 0
fi

# --- Optional: unknown label directories on the remote -------------------------
if $CHECK_REMOTE_LABELS; then
    echo "--> Checking remote study label directories against the registry ..."
    REMOTE_LABELS="$TMPDIR_BASE/remote_labels.txt"
    _remote_sh "find '${REMOTE_DATA}/analysis' -mindepth 5 -maxdepth 5 -type d -printf '%f\n' | sort -u" > "$REMOTE_LABELS" || true
    LIVE="$TMPDIR_BASE/live.txt"; DEAD="$TMPDIR_BASE/dead.txt"
    python3 "$REGISTRY_PY" labels > "$LIVE"
    python3 "$REGISTRY_PY" labels --dead > "$DEAD"
    UNKNOWN="$(comm -23 "$REMOTE_LABELS" <(sort -u "$LIVE" "$DEAD"))"
    if [[ -n "$UNKNOWN" ]]; then
        echo "    WARNING: label directories on the remote unknown to src/lib/solar_studies.py (not synced):"
        echo "$UNKNOWN" | sed 's/^/        /'
    else
        echo "    every remote label directory is either live or a known dead label"
    fi
    FLAT_STATUS="$TMPDIR_BASE/flat_status.txt"
    FLAT_TOPS="$(python3 "$REGISTRY_PY" kinds; python3 "$REGISTRY_PY" kinds --dead)"
    FLAT_TOPS="$(echo "$FLAT_TOPS" | awk '{print $2}' | sort -u | tr '\n' ' ')"
    _remote_sh "cd '${REMOTE_DATA}' && find ${FLAT_TOPS} -name '*.pkl' 2>/dev/null" \
        | python3 "$REGISTRY_PY" kinds --classify > "$FLAT_STATUS" || true
    echo "    flat-family kinds on the remote: $(grep -c '^live' "$FLAT_STATUS" || true) live, $(grep -c '^dead' "$FLAT_STATUS" || true) known dead (never synced)"
    if grep -q '^unknown' "$FLAT_STATUS"; then
        echo "    WARNING: kinds in flat-family folders unknown to the registry (not synced; any config/name):"
        grep '^unknown' "$FLAT_STATUS" | sed 's/^unknown */        /'
    fi
    echo ""
fi

# --- Preview ------------------------------------------------------------------
echo "--> Listing files to transfer (rsync dry-run) ..."
PREVIEW="$TMPDIR_BASE/preview.txt"
rsync -n "${RSYNC_COMMON[@]}" "${RSYNC_E[@]}" "${RSYNC_SOURCES[@]}" "$MIRROR_DIR/" 2>"$TMPDIR_BASE/rsync_err.txt" \
    | grep '\.pkl$' > "$PREVIEW.all" || true
if [[ -s "$TMPDIR_BASE/rsync_err.txt" ]]; then
    echo "    rsync stderr:" >&2
    sed 's/^/        /' "$TMPDIR_BASE/rsync_err.txt" >&2
fi
grep -v '^deleting ' "$PREVIEW.all" > "$PREVIEW" || true
N_TRANSFER=$(wc -l < "$PREVIEW")
N_DELETE=$(grep -c '^deleting ' "$PREVIEW.all" || true)
N_MIRROR=$( { [[ -d "$MIRROR_DIR" ]] && find "$MIRROR_DIR" -name '*.pkl'; } 2>/dev/null | wc -l || true)
echo "==> ${N_TRANSFER} file(s) to transfer, ${N_DELETE} to delete from the mirror (mirror currently holds ${N_MIRROR})"
if (( N_TRANSFER + N_DELETE > 0 )); then
    # Bucket keys: analysis/{analysis}/{folder}/{label}, solar/{tree}/{name}/{folder},
    # reconstruction {subdir}/{name} (the config level is dropped everywhere).
    # Mirror deletions (no longer selected or gone upstream) are prefixed "mirror delete".
    awk -F/ '{ d=sub(/^deleting /, "")
               if ($1=="analysis") k="analysis/"$2"/"$5"/"$6
               else if ($1=="solar") k=$1"/"$2"/"$4"/"$5
               else { k=$1; for (i=2; i<=NF-3; i++) k=k"/"$i; k=k"/"$(NF-1) }
               if (d) k="mirror delete  "k
               c[k]++ } END { for (k in c) printf "    %5d  %s\n", c[k], k }' "$PREVIEW.all" | sort -k2
fi
echo ""

if $DRY_RUN; then
    echo "    (dry-run — nothing written; run without --dry-run to fetch and route)"
    exit 0
fi

if (( N_TRANSFER + N_DELETE > 0 )) && ! $AUTO_YES; then
    read -r -p "Proceed with download? [y/N] " _confirm
    [[ "$_confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 2; }
fi

# --- Download into the mirror -------------------------------------------------
if (( N_TRANSFER + N_DELETE > 0 )); then
    echo "--> Downloading ${N_TRANSFER} file(s) into the mirror (${N_DELETE} mirror deletion(s)) ..."
    mkdir -p "$MIRROR_DIR"
    _rsync_tolerant "${RSYNC_COMMON[@]}" "${RSYNC_E[@]}" "${RSYNC_SOURCES[@]}" "$MIRROR_DIR/" > "$TMPDIR_BASE/transferred.txt"
    echo "    Transferred $(grep -v '^deleting ' "$TMPDIR_BASE/transferred.txt" | grep -c '\.pkl$' || true) file(s), deleted $(grep -c '^deleting .*\.pkl$' "$TMPDIR_BASE/transferred.txt" || true) from the mirror"
    echo ""
fi

# --- Route the mirror into input/data -----------------------------------------
echo "--> Routing mirror into ${DATA_DIR} ..."
ROUTE_ARGS=()
$FORCE        && ROUTE_ARGS+=(--force)
$PRUNE_LEGACY && ROUTE_ARGS+=(--prune-legacy)
python3 "$REGISTRY_PY" route "$MIRROR_DIR" "$DATA_DIR" "${ROUTE_ARGS[@]}" "${FILTER_ARGS[@]}"
echo "==> Done"
