#!/bin/bash
for cluster in adroit della perseus tigressdata traverse
do
  ssh jdh4@${cluster}.princeton.edu "getent passwd > /home/jdh4/.lft/${cluster}_getent.txt 2>/dev/null"
  scp jdh4@${cluster}.princeton.edu:/home/jdh4/.lft/${cluster}_getent.txt /tigress/jdh4/python-devel/lft 2>/dev/null
done
getent passwd > ./tiger_getent.txt 2>/dev/null
/usr/licensed/anaconda3/2020.7/bin/python combine_getent.py 2>/dev/null
