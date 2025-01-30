#!/usr/licensed/anaconda3/2024.10/bin/python

# output of "ls /home" for the different clusters is combined
# and written to file

import pandas as pd

clusters = ['adroit_ls.txt', 'della_ls.txt', 'stellar-intel_ls.txt', 'tiger3_ls.txt']

df = pd.read_csv(clusters[0], header=None)
df.columns = ['netid']
df['adroit'] = 'adroit'
for cluster in clusters[1:]:
  tmp = pd.read_csv(cluster, header=None)
  tmp.columns = ['netid']
  host = cluster.split('_')[0]
  tmp[host] = host
  df = pd.merge(df, tmp, on='netid', how='outer')

df["stellar-intel"] = df["stellar-intel"].apply(lambda x: x if pd.isna(x) else x.replace("stellar-intel", "stellar"))
df = df.sort_values(by='netid', ascending=True)
df.to_csv('combined_ls.csv', index=False)
