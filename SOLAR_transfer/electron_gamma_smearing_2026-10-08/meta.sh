SP=/cvmfs/dune.opensciencegrid.org/spack/packages/linux-x86_64_v3
PY=/cvmfs/dune.opensciencegrid.org/spack/v1.1.1/opt/spack/linux-x86_64_v3/python-venv-1.0-aofrg7dbqqn43y2ujmz6jims6a4f5uvn/bin/python3
export PYTHONPATH=$({ ls -d $SP/metacat-4.1.4-*/lib/python3.11/site-packages; ls -d $SP/py-*/lib/python3.11/site-packages /cvmfs/dune.opensciencegrid.org/spack/v1.1.1/opt/spack/linux-x86_64_v3/py-*/lib/python3.11/site-packages 2>/dev/null | awk -F/ '{n=$(NF-3); sub(/-[0-9].*/,"",n); if(!(n in s)){s[n]=1; print}}'; } | tr "\n" ":")
export METACAT_SERVER_URL=https://metacat.fnal.gov:9443/dune_meta_prod/app
export METACAT_AUTH_SERVER_URL=https://metacat.fnal.gov:8143/auth/dune
mc() { $PY $SP/metacat-4.1.4-*/bin/metacat "$@"; }
F=$(mc query "files from fardet-hd:fardet-hd__le_mc_2024a_reco2__full-reconstructed__v09_91_04d01__reco2_supernova_dune10kt_1x2x6__prodmarley_nue_cc_flat_dune10kt_1x2x6__out1__v1_official limit 1" 2>&1)
echo "FILE $F"
for i in 1 2 3 4 5 6; do
  echo "--- $F"
  mc file show -m -p "$F" 2>&1 | grep -E "core.application|dune.config_file|core.data_tier|core.runs\b|core.event_count|parents|^  *[a-z-]+:[A-Za-z0-9_.-]+$|fcl|dune.output_status" | head -20
  F=$(mc file show -p "$F" 2>&1 | grep -A2 -i "parents" | grep -oE "[a-z-]+:[A-Za-z0-9_.-]+\.root" | head -1)
  [ -z "$F" ] && break
done
