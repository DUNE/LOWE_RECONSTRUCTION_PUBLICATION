#!/bin/bash
# VD Top marley_final extension (2026-10-11): files 10000-59999 of the VD radiological MARLEY reco2 dataset (one event per
# file) with the same final adjflash SolarNuAna configuration as final_0929.sh (files 0-9999), five files per job (about 27 CPU-min per event).
# Usage: bash vd_ext_1011.sh test|full
set -u
MODE=${1:-test}
cd /exp/dune/app/users/smanthey/justin
JU=$(ls -d /cvmfs/dune.opensciencegrid.org/spack/packages/linux-x86_64_v3/justin-01.06.05-*/bin)/justin
export PATH=$(dirname $JU):$PATH
INPUT_TAR_DIR_LOCAL=`justin-cvmfs-upload larsoft_v10_08_01.tar.gz`
if [ -z "$INPUT_TAR_DIR_LOCAL" ]; then echo "justin-cvmfs-upload failed - not submitting"; exit 1; fi
echo "tarball: $INPUT_TAR_DIR_LOCAL"
FNALURL="https://fndcadoor.fnal.gov:2880/dune/scratch/users"
VD="fardet-vd:le_mc_2024a_reco2__full-reconstructed__v09_91_04d01__reco2_supernova_dunevd10kt_1x8x14_3view_30deg_prod2024__prodmarley_nue_cc_flat_radiological_decay0_dunevd10kt_1x8x14_3view_30deg__out1__v1_official"
FCL=solar_ana_marley_adjflash_radiological_decay0_dunevd10kt_1x8x14_3view_30deg.fcl
OUT=ana/solar_ana_marley_adjflash_final_radiological_decay0_dunevd10kt_1x8x14_3view_30deg_nominal_ext
sub() { # skip limit outdir
  justin simple-workflow --mql "files from $VD ordered skip $1 limit $2" --jobscript gun_1008/solar_ana_multi.jobscript \
    --env INPUT_TAR_DIR_LOCAL="$INPUT_TAR_DIR_LOCAL" --env FCL_FILE="$FCL" --env MAX_FILES=5 \
    --rss-mb 4000 --wall-seconds 28800 --scope usertests --lifetime-days 5 \
    --output-pattern "*hist.root:$FNALURL/$USER/$3" 2>&1 | tail -2
}
if [ "$MODE" = test ]; then
  sub 10000 20 ${OUT}_test
else
  for S in $(seq 10000 10000 50000); do sub $S 10000 $OUT; done
fi
