#!/usr/licensed/anaconda3/2020.7/bin/python

# output of "ls /home" for the different clusters is processed
# and written to file

import pandas as pd

clusters = ['adroit_ls.txt', 'della_ls.txt', 'perseus_ls.txt', \
            'tiger_ls.txt', 'tigressdata_ls.txt', 'traverse_ls.txt']

df = pd.read_csv(clusters[0], header=None)
df.columns = ['netid']
df['adroit'] = 'adroit'
for cluster in clusters[1:]:
  tmp = pd.read_csv(cluster, header=None)
  tmp.columns = ['netid']
  host = cluster.split('_')[0]
  tmp[host] = host
  df = pd.merge(df, tmp, on='netid', how='outer')

df = df.sort_values(by='netid', ascending=True)
df.to_csv('combined_ls.csv', index=False)
