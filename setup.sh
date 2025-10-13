#!/bin/bash

# This script sets up the environment for DUNE analysis by downloading necessary styles and configurations.
mkdir -p styles

python3 -m venv .venv
source .venv/bin/activate

cd styles
export DUNE_PLOT_STYLE_LATEST_TAG=`curl --silent "https://api.github.com/repos/DUNE/dune_plot_style/releases" | jq -r 'map(select(.prerelease == false)) | first | .tag_name'`
wget --no-check-certificate https://github.com/DUNE/dune_plot_style/archive/refs/tags/${DUNE_PLOT_STYLE_LATEST_TAG}.tar.gz -O dune_plot_style.tar.gz
tar -xvzf dune_plot_style.tar.gz
# Remove "v" from tag name
export DUNE_PLOT_STYLE_LATEST_TAG=${DUNE_PLOT_STYLE_LATEST_TAG#v}
cd dune_plot_style-${DUNE_PLOT_STYLE_LATEST_TAG}

python3 -m pip install .
pip install examples/matplotlib/plotting_helpers.py
cd ../../