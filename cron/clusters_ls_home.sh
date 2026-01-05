#!/bin/bash

cd /projects/CSES/jdh4/python-devel/lft/cron

# pull in home directories from each cluster to here
for cluster in adroit stellar-intel tiger3
do
  ssh    jdh4@${cluster}.princeton.edu "ls /home > /home/jdh4/bin/cron/${cluster}_ls.txt 2>/dev/null"
  scp -q jdh4@${cluster}.princeton.edu:/home/jdh4/bin/cron/${cluster}_ls.txt . 2>/dev/null
done
ls /home > ./della_ls.txt 2>/dev/null
ls /home.old >> ./della_ls.txt 2>/dev/null
sort della_ls.txt | uniq > temp.txt && mv temp.txt della_ls.txt

# combine results from each cluster
/usr/licensed/anaconda3/2024.10/bin/python combine_ls.py 2>/dev/null

# push out master file to each cluster
for cluster in adroit stellar-intel tiger3
do
  scp -q combined_ls.csv jdh4@${cluster}.princeton.edu:/home/jdh4/bin/cron 2>/dev/null
done
cp combined_ls.csv /home/jdh4/bin/cron 2>/dev/null
