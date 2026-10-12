#!/bin/bash
# 10 MeV single-particle (e- and gamma) productions for the electron/gamma smearing study (2026-10-08,
# thesis sec. 7.6). Full le_mc_2024a chain (gen..reco1 v09_91_04d00, reco2 v09_91_04d01) + SolarNuAna
# (v10_08_01 tarball, final marley defaults, SignalLabel generator, SaveSignalEDep/SaveClusterEDep),
# see gun_chain.jobscript. Usage: bash gun_1008.sh test|full|neutron|flat
set -u
MODE=${1:-test}
cd /exp/dune/app/users/smanthey/justin/gun_1008
JU=$(ls -d /cvmfs/dune.opensciencegrid.org/spack/packages/linux-x86_64_v3/justin-01.06.05-*/bin)/justin
export PATH=$(dirname $JU):$PATH
INPUT_TAR_DIR_LOCAL=`justin-cvmfs-upload ../larsoft_v10_08_01.tar.gz`
if [ -z "$INPUT_TAR_DIR_LOCAL" ]; then echo "justin-cvmfs-upload failed - not submitting"; exit 1; fi
echo "tarball: $INPUT_TAR_DIR_LOCAL"
FNALURL="https://fndcadoor.fnal.gov:2880/dune/scratch/users"
sub() { # geom pdg njobs nevents rss outdir [ke_mev] [photon_evaporation] [ke_max_mev]
  justin simple-workflow --monte-carlo $3 --jobscript gun_chain.jobscript \
    --env INPUT_TAR_DIR_LOCAL="$INPUT_TAR_DIR_LOCAL" --env GEOM=$1 --env PDG=$2 --env KE_MEV=${7:-10} --env NUM_EVENTS=$4 \
    --env PHOTON_EVAPORATION=${8:-0} ${9:+--env KE_MAX_MEV=$9} \
    --rss-mb $5 --wall-seconds 43200 --scope usertests --lifetime-days 5 \
    --output-pattern "gun_*_hist.root:$FNALURL/$USER/$6" 2>&1 | tail -3
}
if [ "$MODE" = slice ]; then
  # Free electrons flat in 9.5-10.5 MeV (2026-10-11): same true-energy slice as the CC/gamma rows of fig:SMEARING_CHAIN_SLICE
  sub hd 11 200 50 4000 ana/gun_1011_hd_electron_9.5-10.5MeV 9.5 0 10.5
  sub vd 11 400 25 4000 ana/gun_1011_vd_electron_9.5-10.5MeV 9.5 0 10.5
elif [ "$MODE" = flat ]; then
  # Pure electrons, flat 2-30 MeV: smearing chain without MARLEY de-excitation products
  sub hd 11 400 50 4000 ana/gun_1008b_hd_electron_flat2-30MeV 2 0 30
  sub vd 11 480 25 4000 ana/gun_1008b_vd_electron_flat2-30MeV 2 0 30
elif [ "$MODE" = neutron ]; then
  # Thermal neutrons (0.025 eV): Ar-40(n,gamma) capture cascades; default NeutronHP (as the official samples)
  # and the energy-conserving photon-evaporation variant (HD only)
  sub hd 2112 200 50 4000 ana/gun_1008b_hd_neutron_thermal 2.5e-8 0
  sub hd 2112 200 50 4000 ana/gun_1008b_hd_neutron_thermal_photonevap 2.5e-8 1
  sub vd 2112 400 25 4000 ana/gun_1008b_vd_neutron_thermal 2.5e-8 0
elif [ "$MODE" = test ]; then
  sub hd 11 2 5 4000 ana/test_gun_1008_hd_electron_10MeV
  sub vd 22 2 5 6000 ana/test_gun_1008_vd_gamma_10MeV
else
  sub hd 11 200 50 4000 ana/gun_1008b_hd_electron_10MeV
  sub hd 22 200 50 4000 ana/gun_1008b_hd_gamma_10MeV
  sub vd 11 400 25 4000 ana/gun_1008b_vd_electron_10MeV
  sub vd 22 400 25 4000 ana/gun_1008b_vd_gamma_10MeV
fi
