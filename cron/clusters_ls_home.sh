#!/bin/bash

# pull in home directories from each cluster to here
for cluster in adroit della perseus tigressdata traverse
do
  ssh    jdh4@${cluster}.princeton.edu "ls /home > /home/jdh4/bin/cron/${cluster}_ls.txt 2>/dev/null"
  scp -q jdh4@${cluster}.princeton.edu:/home/jdh4/bin/cron/${cluster}_ls.txt /tigress/jdh4/python-devel/lft/cron 2>/dev/null
done
ls /home > ./tiger_ls.txt 2>/dev/null

# combine results then push out master file to each cluster
/usr/licensed/anaconda3/2020.7/bin/python combine_ls.py 2>/dev/null
for cluster in adroit della perseus tigressdata traverse
do
  scp -q combined_ls.csv jdh4@${cluster}.princeton.edu:/home/jdh4/bin/cron 2>/dev/null
done
cp combined_ls.csv /home/jdh4/bin/cron 2>/dev/null
