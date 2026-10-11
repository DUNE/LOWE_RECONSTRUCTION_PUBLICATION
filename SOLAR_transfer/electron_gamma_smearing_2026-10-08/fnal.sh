#!/bin/bash
# usage: fnal.sh 'remote command'   (runs on dunegpvm03 via gaeuidc1)
P=~/.solar_sync_pass
CMD=$(printf '%q' "$1")
sshpass -f $P ssh -T -o "ProxyCommand=sshpass -f $P ssh -W %h:%p pcae22" solar~localhost "cd /pc/choozdsk01/users/manthey/SOLAR && eval \"\$(python3 kinit_fnal.py --env)\" >/dev/null 2>&1; ssh -o BatchMode=yes -o ConnectTimeout=20 smanthey@dunegpvm03.fnal.gov $CMD"
