#!/bin/bash

cd /tigress/jdh4/python-devel/lft

# tiger cluster
rm -rf panes/__pycache__
cp -p lft    $HOME/bin
cp -r panes  $HOME/bin
cp -r remind $HOME/bin

# other clusters
for cluster in adroit della stellar-intel tiger3
do
  echo ${cluster}
  scp    lft    jdh4@${cluster}.princeton.edu:/home/jdh4/bin
  scp -r panes  jdh4@${cluster}.princeton.edu:/home/jdh4/bin
  scp -r remind jdh4@${cluster}.princeton.edu:/home/jdh4/bin
  echo
done
