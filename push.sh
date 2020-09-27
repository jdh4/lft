#!/bin/bash
cp lft ../../python-utilities
scp lft jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/lft
scp combined_ls.csv jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/.lft
ssh jdh4@adroit.princeton.edu "sed -i '1!b;s/gpfs/network/' /scratch/network/jdh4/python-utilities/lft"
scp holidays.csv     jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/.lft 2>/dev/null
scp rc_workshops.csv jdh4@adroit.princeton.edu:/scratch/network/jdh4/python-utilities/.lft 2>/dev/null
