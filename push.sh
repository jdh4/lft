#!/bin/bash
cp lft ../../python-utilities
rm -rf panes/__pycache__
cp -r panes ../../python-utilities
scp lft jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities
scp -r panes jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities
ssh jdh4@adroit.princeton.edu "sed -i '1!b;s/gpfs/network/' /scratch/network/jdh4/python-utilities/lft"
scp cron/combined_ls.csv jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/.lft
scp cron/combined_getent.csv jdh4@adroit.princeton.edu:/home/jdh4/bin
scp holidays.csv     jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/.lft 2>/dev/null
scp rc_workshops.csv jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/.lft 2>/dev/null
