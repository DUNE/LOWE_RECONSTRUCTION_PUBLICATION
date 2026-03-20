#!/bin/bash

# This script sets up the environment for DUNE analysis by downloading necessary styles and configurations.

_setup_is_sourced=0
if [ "${BASH_SOURCE[0]}" != "$0" ]; then
    _setup_is_sourced=1
fi

_setup_finish() {
    local status=$1
    if [ "$_setup_is_sourced" -eq 1 ]; then
        return "$status"
    fi
    exit "$status"
}

setup_main() {
local _setup_shell_opts=$-
if [[ $_setup_shell_opts == *e* ]]; then
    trap 'set -e' RETURN
else
    trap 'set +e' RETURN
fi
set -e

REPO_ROOT=$(pwd)

mkdir -p styles
mkdir -p tests/output/plots

# Check if .venv already exists
if [ -d ".venv" ]; then
    echo -e "\e[32m -> .venv already exists. Please remove it if you want to recreate the virtual environment.\e[0m"
    else
    echo "Creating a new virtual environment in .venv"
    python3 -m venv .venv
fi
source .venv/bin/activate

cd styles

# Check if dune_plot_style source is already available locally
if [ -d dune_plot_style-* ]; then
    echo -e "\e[32m -> dune_plot_style source already exists locally.\e[0m"
    cd ../
else
    echo -e "\e[33mDownloading and installing the latest dune_plot_style\e[0m"
    export DUNE_PLOT_STYLE_LATEST_TAG=`curl --silent "https://api.github.com/repos/DUNE/dune_plot_style/releases" | jq -r 'map(select(.prerelease == false)) | first | .tag_name'`
    wget --no-check-certificate https://github.com/DUNE/dune_plot_style/archive/refs/tags/${DUNE_PLOT_STYLE_LATEST_TAG}.tar.gz -O dune_plot_style.tar.gz
    tar -xvzf dune_plot_style.tar.gz
    cd ../../
fi

echo -e "\e[35m -> Installing dunestyle directly into the active environment\n\e[0m"
STYLE_DIR=$(find "$REPO_ROOT/styles" -maxdepth 1 -type d -name 'dune_plot_style-*' | head -n 1)
if [ -z "$STYLE_DIR" ]; then
    echo -e "\e[31m -> Could not locate dune_plot_style source directory.\e[0m"
    exit 1
fi

if python3 -m pip install --no-build-isolation "$STYLE_DIR"; then
    echo -e "\e[32m -> Installed dunestyle with pip.\e[0m"
else
    echo -e "\e[33m -> pip install failed; falling back to direct package install into site-packages.\e[0m"
    SITE_PACKAGES=$(python3 - <<'PY'
import site
paths = [p for p in site.getsitepackages() if p.endswith("site-packages")]
print(paths[0] if paths else "")
PY
)
    if [ -z "$SITE_PACKAGES" ]; then
        echo -e "\e[31m -> Could not locate site-packages for the active environment.\e[0m"
        exit 1
    fi

    rm -rf "$SITE_PACKAGES/dunestyle"
    mkdir -p "$SITE_PACKAGES/dunestyle/matplotlib" "$SITE_PACKAGES/dunestyle/root" "$SITE_PACKAGES/dunestyle/data" "$SITE_PACKAGES/dunestyle/stylelib"
    cp "$STYLE_DIR/src/__init__.py" "$SITE_PACKAGES/dunestyle/__init__.py"
    cp "$STYLE_DIR/src/matplotlib/python/__init__.py" "$SITE_PACKAGES/dunestyle/matplotlib/__init__.py"
    cp "$STYLE_DIR/src/matplotlib/python/dunestyle.py" "$SITE_PACKAGES/dunestyle/matplotlib/dunestyle.py"
    cp "$STYLE_DIR/src/root/python/__init__.py" "$SITE_PACKAGES/dunestyle/root/__init__.py"
    cp "$STYLE_DIR/src/root/python/dunestyle.py" "$SITE_PACKAGES/dunestyle/root/dunestyle.py"
    cp "$STYLE_DIR/src/matplotlib/stylelib/dune.mplstyle" "$SITE_PACKAGES/dunestyle/stylelib/dune.mplstyle"
    cp "$STYLE_DIR/src/root/cpp/include/DUNEStyle.h" "$SITE_PACKAGES/dunestyle/data/DUNEStyle.h"
    : > "$SITE_PACKAGES/dunestyle/stylelib/__init__.py"
    : > "$SITE_PACKAGES/dunestyle/data/__init__.py"
fi
python3 -c "import dunestyle.matplotlib; print('dunestyle import OK')"

echo -e "\e[35m -> Installing required Python packages from requirements.txt\n\e[0m"
python3 -m pip install -r requirements.txt pytest

echo -e "\e[35m -> Running plotting test workflow and generating visual artifacts\n\e[0m"
python3 -m pytest \
    tests/test_script_compare_configuration.py \
    tests/test_script_compare_hist1d.py \
    tests/test_script_compare_hist2d.py \
    tests/test_script_compare_reduction.py \
    tests/test_script_line_fit.py

echo -e "\e[32m \n-> Setup complete! Run a plot command list with \e[0m\e[33mpython3 run_plot_scripts.py -s <name>\e[0m\e[32m.
 Run a table command list with \e[0m\e[33mpython3 run_table_scripts.py -s <name>\e[0m\e[32m.
 Visual test artifacts are available at \e[0m\e[33mtests/output/index.html\e[0m\e[32m.\n\e[0m"
}

if setup_main; then
    :
else
    status=$?
    echo -e "\e[31m -> Setup failed with exit code ${status}.\e[0m"
    _setup_finish "$status"
fi
