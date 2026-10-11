#!/bin/bash
# VD Top marley_final extension (FNAL justIN 21827-21831, files 10000-59999 of the radiological MARLEY reco2 dataset):
# transfer, archive the 10k-file sample, merge 0-59999, convert to npy, vertex/PDS stages, calibration + analysis rerun.
# Run on gaeuidc1 once every workflow has finished:  bash vdtop_ext_20261011.sh [transfer|merge|process|calib|all]
set -eu
STEP=${1:-all}
export KRB5_CONFIG=/pc/choozdsk01/users/manthey/SOLAR/.krb5_fnal.conf:/etc/krb5.conf
export KRB5CCNAME=FILE:/tmp/krb5cc_fnal_33159
R=/pnfs/dune/scratch/users/smanthey/ana
RAW=/pc/choozdsk01/users/manthey/SOLAR_transfer/final_raw   # as transfer_nfs.sh / hadd2_nfs.sh (files 0-9999 in vd_nominal_marley_final)
DATA=/pnfs/ciemat.es/data/neutrinos/DUNE/SOLAR/data/vd/vd_1x8x14_3view_30deg_nominal
W=/pc/choozdsk01/users/manthey/SOLAR_transfer/final_2026-09-29/vdtop_ext_20261011; mkdir -p $W
B=/pc/choozdsk01/users/manthey/SOLAR-sb; S=/pc/choozdsk01/users/manthey/SOLAR
IMG="apptainer exec -B /pnfs,/afs,/pc,/cvmfs --home=$B/ --pwd $B/ $S/containers/solar_v1.0.sif"
SSHOPTS="-o GSSAPIAuthentication=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30"
log(){ echo "$(date "+%F %T") $*"; }

if [ $STEP = transfer ] || [ $STEP = all ]; then
  python3 $S/kinit_fnal.py > /dev/null
  mkdir -p $RAW/vd_nominal_marley_final_ext
  ssh $SSHOPTS smanthey@dunegpvm01.fnal.gov "tar czf - -C $R/solar_ana_marley_adjflash_final_radiological_decay0_dunevd10kt_1x8x14_3view_30deg_nominal_ext fnal" \
    | tar xzf - -C $RAW/vd_nominal_marley_final_ext
  log "transferred $(find $RAW/vd_nominal_marley_final_ext -name '*.root' | wc -l) files"
fi

if [ $STEP = merge ] || [ $STEP = all ]; then
  # Keep the 10k-file sample: the ROOT file and its npy folder move to marley_final_10k (never overwrite old samples)
  [ -e $DATA/SolarNuAna_marley_final_10k.root ] || mv $DATA/SolarNuAna_marley_final.root $DATA/SolarNuAna_marley_final_10k.root
  [ -e $DATA/SolarNuAna_marley_final_10k ] || mv $DATA/SolarNuAna_marley_final $DATA/SolarNuAna_marley_final_10k
  ( source /cvmfs/sft.cern.ch/lcg/views/LCG_109/x86_64-el9-gcc13-opt/setup.sh
    find $RAW/vd_nominal_marley_final $RAW/vd_nominal_marley_final_ext -name "*.root" -size +0 | sort > $W/hadd_files.txt
    # chunked merge from the NFS copy, as hadd2_nfs.sh
    C=$RAW/chunks_vdtop_ext; rm -rf $C; mkdir -p $C
    split -l 1000 -d -a 3 $W/hadd_files.txt $C/chunk_
    ls $C/chunk_* | xargs -P 8 -I{} sh -c "xargs -a {} -s 1900000 hadd -k {}.root > /dev/null 2>&1 || echo CHUNK_FAIL {}"
    hadd -k $RAW/.tmp_vdtop_ext.root $C/chunk_*.root > $W/hadd.log 2>&1
    mv $RAW/.tmp_vdtop_ext.root $DATA/SolarNuAna_marley_final.root; rm -rf $C )
  log "merged $(wc -l < $W/hadd_files.txt) files -> $DATA/SolarNuAna_marley_final.root"
fi

if [ $STEP = process ] || [ $STEP = all ]; then
  cd $B
  $IMG python3 src/tools/process_sample.py --config vd_1x8x14_3view_30deg_nominal --name marley_final > $W/convert.log 2>&1
  A="--config vd_1x8x14_3view_30deg_nominal --name marley_final --rewrite --no-debug"
  for s in vertex/01_smearing vertex/02_vertex vertex/03_fiducial vertex/04_reconstruction pds/02_adj_opflash pds/03_matched_opflash pds/04_matched_efficiency \
           tpc/01_electron_energy tpc/02_adj_clusters; do
    $IMG python3 src/physics/detector/$s.py $A > $W/out_$(basename $s).log 2>&1 && log "  $s OK" || log "  $s FAIL"
  done
fi

if [ $STEP = calib ] || [ $STEP = all ]; then
  # Full calibration (01 F0 table ... chain) and the analysis for VD Top only, as the other configs (rerun 15 settings)
  bash /pc/choozdsk01/users/manthey/SOLAR_transfer/final_runs/final_run2.sh -l rerun_vdtop60k -f calib -c vd_1x8x14_3view_30deg_nominal > $W/final_run.log 2>&1
  log "calibration + analysis: $(tail -1 $W/final_run.log)"
fi
