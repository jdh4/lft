#!/bin/bash
cd /tigress/jdh4/python-devel/lft

# update master file for home directions
./cron/clusters_ls_home.sh
./cron/combine_ls.py

# update master file for getent passwd
# ./cron/clusters_getent_passwd.sh
# ./cron/combine_getent.py

# tiger cluster
rm -rf panes/__pycache__
cp -p lft    $HOME/bin
cp -r panes  $HOME/bin
cp -r remind $HOME/bin
cp    cron/*.csv $HOME/bin/cron

# other clusters
for cluster in adroit della perseus tigressdata traverse
do
  echo == ${cluster} ==
  scp    lft    jdh4@${cluster}.princeton.edu:/home/jdh4/bin
  scp -r panes  jdh4@${cluster}.princeton.edu:/home/jdh4/bin
  scp -r remind jdh4@${cluster}.princeton.edu:/home/jdh4/bin
  scp    cron/*.csv jdh4@${cluster}.princeton.edu:/home/jdh4/bin/cron
  echo
done

# modify path to conda env in shebang
ssh jdh4@adroit.princeton.edu      "sed -i '1!b;s/gpfs/network/' /home/jdh4/bin/lft"
ssh jdh4@tigressdata.princeton.edu "sed -i '1!b;s+/scratch/gpfs+/home+' /home/jdh4/bin/lft"
ssh jdh4@perseus.princeton.edu     "sed -i '1!b;s+/scratch/gpfs/jdh4+/home/jdh4/bin+' /home/jdh4/bin/lft"
