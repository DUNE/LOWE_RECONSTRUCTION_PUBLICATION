# usage: sl7 'cmds' -> run inside SL7 container on dunegpvm03
sl7() { /cvmfs/oasis.opensciencegrid.org/mis/apptainer/current/bin/apptainer exec -B /cvmfs,/exp,/pnfs,/nashome,/tmp /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest bash -c "$1"; }
