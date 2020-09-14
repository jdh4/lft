#!/bin/bash
for cluster in adroit della perseus tigressdata traverse
do
  ssh    jdh4@${cluster}.princeton.edu "ls /home > /home/jdh4/.lft/${cluster}_ls.txt 2>/dev/null"
  scp -q jdh4@${cluster}.princeton.edu:/home/jdh4/.lft/${cluster}_ls.txt /tigress/jdh4/python-devel/lft 2>/dev/null
done
ls /home > ./tiger_ls.txt 2>/dev/null
#echo 'tiger_ls.txt'
/usr/licensed/anaconda3/2020.7/bin/python combine_ls.py 2>/dev/null
for cluster in adroit della perseus tigressdata traverse
do
  scp -q combined_ls.csv jdh4@${cluster}.princeton.edu:/home/jdh4/.lft 2>/dev/null
done
