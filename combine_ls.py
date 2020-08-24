# The output of "ls /home" for the different clusters is processed
# and written to file

import pandas as pd
#pd.set_option('display.max_rows', 5000)

files = ['adroit_ls.txt', 'della_ls.txt', 'perseus_ls.txt', \
         'tiger_ls.txt', 'tigressdata_ls.txt', 'traverse_ls.txt']

df = pd.read_csv(files[0], header=None)
df.columns = ['netid']
df['adroit'] = 'adroit'
for f in files[1:]:
  tmp = pd.read_csv(f, header=None)
  tmp.columns = ['netid']
  host = f.split('_')[0]
  tmp[host] = host
  #df = df.append(tmp)
  df = pd.merge(df, tmp, on='netid', how='outer')

df = df.sort_values(by='netid', ascending=True)
df.to_csv('combined_ls.csv', index=False)
