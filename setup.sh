#!/bin/bash

# This script sets up the environment for DUNE analysis by downloading necessary styles and configurations.
mkdir -p styles

# Check if .venv already exists
if [ -d ".venv" ]; then
    echo -e "\e[32m -> .venv already exists. Please remove it if you want to recreate the virtual environment.\e[0m"
    else
    echo "Creating a new virtual environment in .venv"
    python3 -m venv .venv
fi
source .venv/bin/activate

cd styles

# Check if dune_plot_style is already installed
if [ -d dune_plot_style-* ]; then
    echo -e "\e[32m -> dune_plot_style already exists. Please remove it if you want to reinstall.\e[0m"
    cd ../
    else
    echo -e "\e[33mDownloading and installing the latest dune_plot_style\e[0m"
    export DUNE_PLOT_STYLE_LATEST_TAG=`curl --silent "https://api.github.com/repos/DUNE/dune_plot_style/releases" | jq -r 'map(select(.prerelease == false)) | first | .tag_name'`
    wget --no-check-certificate https://github.com/DUNE/dune_plot_style/archive/refs/tags/${DUNE_PLOT_STYLE_LATEST_TAG}.tar.gz -O dune_plot_style.tar.gz
    tar -xvzf dune_plot_style.tar.gz
    # Remove "v" from tag name
    export DUNE_PLOT_STYLE_LATEST_TAG=${DUNE_PLOT_STYLE_LATEST_TAG#v}
    cd dune_plot_style-${DUNE_PLOT_STYLE_LATEST_TAG}

    python3 -m pip install .
    cd ../../
fi

echo -e "\e[35m -> Installing required Python packages from requirements.txt\n\e[0m"
pip install -r requirements.txt

echo -e "\e[32m \n-> Setup complete! Run the example script with \e[0m\e[33mpython3 run_examples.py\e[0m\e[32m
 or develop your own analysis scripts and run them with \e[0m\e[33mpython3 run_scripts.py\e[0m\e[32m.\n\e[0m"