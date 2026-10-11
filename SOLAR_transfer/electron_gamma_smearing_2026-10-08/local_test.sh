#!/bin/bash
# Local test of gun_chain.jobscript inside SL7: bash local_test.sh hd|vd 11|22 NEVENTS
GEOM=$1; PDG=$2; N=${3:-2}
T=/exp/dune/data/users/smanthey/gun_test/${GEOM}_${PDG}${5:-}
rm -rf $T; mkdir -p $T/fakejustin
cat > $T/fakejustin/justin-get-file <<'X'
#!/bin/bash
echo "monte-carlo-000001 000001 MONTECARLO"
X
chmod +x $T/fakejustin/justin-get-file
cd $T
/cvmfs/oasis.opensciencegrid.org/mis/apptainer/current/bin/apptainer exec -B /cvmfs,/exp,/pnfs,/nashome,/tmp /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest \
  env -i HOME=$HOME USER=$USER PATH=/usr/bin:/bin JUSTIN_PATH=$T/fakejustin JUSTIN_WORKFLOW_ID=${7:-0} GEOM=$GEOM PDG=$PDG KE_MEV=${4:-10} PHOTON_EVAPORATION=${6:-0} NUM_EVENTS=$N \
  INPUT_TAR_DIR_LOCAL=/exp/dune/app/users/smanthey bash -c "cd $T && bash /exp/dune/app/users/smanthey/justin/gun_1008/gun_chain.jobscript" > $T/job.log 2>&1
echo "EXIT=$?" >> $T/job.log
