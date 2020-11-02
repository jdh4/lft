#!/bin/bash
cd /tigress/jdh4/python-devel/lft

rm -rf panes/__pycache__

cp    lft    $HOME/bin
cp -r panes  $HOME/bin
cp -r cron   $HOME/bin
cp -r remind $HOME/bin

scp    lft    jdh4@adroit.princeton.edu:/home/jdh4/bin
scp -r panes  jdh4@adroit.princeton.edu:/home/jdh4/bin
scp -r cron   jdh4@adroit.princeton.edu:/home/jdh4/bin
scp -r remind jdh4@adroit.princeton.edu:/home/jdh4/bin
ssh jdh4@adroit.princeton.edu "sed -i '1!b;s/gpfs/network/' /home/jdh4/bin/lft"

#scp lft jdh4@tigressdata.princeton.edu:/home/jdh4/bin
#scp -r panes jdh4@tigressdata.princeton.edu:/home/jdh4/bin
# TODO ssh jdh4@tigressdata.princeton.edu "sed -i '1!b;s/gpfs/network/' /scratch/network/jdh4/python-utilities/lft"
