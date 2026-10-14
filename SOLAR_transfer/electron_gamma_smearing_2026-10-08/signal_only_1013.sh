#!/bin/bash
# Signal-only final SolarNuAna (2026-10-13): final adjflash defaults (fast module tarball) on files 0-999 of the official
# signal-only MARLEY reco2 datasets, the same files as SolarNuAna_marley_official. Replaces the last marley_official
# inputs of the thesis (HD Signal / VD Signal). Usage: bash signal_only_1013.sh
cd /exp/dune/app/users/smanthey/justin
JU=$(ls -d /cvmfs/dune.opensciencegrid.org/spack/packages/linux-x86_64_v3/justin-01.06.05-*/bin)/justin
export PATH=$(dirname $JU):$PATH
INPUT_TAR_DIR_LOCAL=`justin-cvmfs-upload larsoft_v10_08_01_fast.tar.gz`
if [ -z "$INPUT_TAR_DIR_LOCAL" ]; then echo "justin-cvmfs-upload failed - not submitting"; exit 1; fi
echo "tarball: $INPUT_TAR_DIR_LOCAL"
FNALURL="https://fndcadoor.fnal.gov:2880/dune/scratch/users"
HD="fardet-hd:fardet-hd__le_mc_2024a_reco2__full-reconstructed__v09_91_04d01__reco2_supernova_dune10kt_1x2x6__prodmarley_nue_cc_flat_dune10kt_1x2x6__out1__v1_official"
VD="fardet-vd:le_mc_2024a_reco2__full-reconstructed__v09_91_04d01__reco2_supernova_dunevd10kt_1x8x14_3view_30deg_prod2024__prodmarley_nue_cc_flat_dunevd10kt_1x8x14_3view_30deg__out1__v1_official"
sub() { # dataset jobscript fcl outdir
  justin simple-workflow --mql "files from $1 ordered skip 0 limit 1000" --jobscript $2 \
    --env INPUT_TAR_DIR_LOCAL="$INPUT_TAR_DIR_LOCAL" --env FCL_FILE="$3" \
    --rss-mb 4000 --scope usertests --lifetime-days 3 --output-pattern "*hist.root:$FNALURL/$USER/$4" 2>&1 | tail -2
}
sub $HD solar_ana_marley_flash_dune10kt_1x2x6.jobscript solar_ana_marley_adjflash_dune10kt_1x2x6.fcl ana/solar_ana_marley_adjflash_final_dune10kt_1x2x6
sub $VD solar_ana_marley_flash_dunevd10kt_1x8x14_3view_30deg.jobscript solar_ana_marley_adjflash_dunevd10kt_1x8x14_3view_30deg.fcl ana/solar_ana_marley_adjflash_final_dunevd10kt_1x8x14_3view_30deg
