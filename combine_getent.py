#!/usr/licensed/anaconda3/2020.7/bin/python

# The output of "getent passwd" is combined and filtered for the
# different clusters. Adroit is handled as a special case since
# it does not contain name_sponsor info for most users.

import pandas as pd
#pd.set_option('display.max_rows', 5000)

def fix_lastname_first_comma(full_name):
  parts = full_name.split()
  if (parts[0].endswith(',')):
    return ' '.join(parts[1:] + [parts[0][:-1]])
  else:
    return full_name

def remove_middle_initial(full_name):
  parts = full_name.split()
  cnt = len(parts)
  if (cnt > 2):
    for i in range(1, cnt - 1):
      if (parts[i].endswith('.') and (len(parts[i]) == 2)) or len(parts[i]) == 1:
        _ = parts.pop(i)
      return ' '.join(parts)
  else:
    return full_name

def format_sponsor(s):
  # extract last name from sponsor (taken from dossier.py)
  if pd.isna(s): return ''
  names = list(filter(lambda x: x not in ['Jr.', 'II', 'III', 'IV'], s.split()))
  if len(names) == 2:
    if len(names[1]) > 1: return names[1]
    else: return s
  elif (len(names) > 2):
    idx = 0
    while (names[idx].endswith('.') and (idx < len(names) - 1)):
      idx += 1
    names = names[idx:]
    e = ''.join([str(int(name.endswith('.'))) for name in names])
    if '1' in e: return ' '.join(names[e.index('1') + 1:])
    else: return names[-1]
  else:
    return s

def extract_name(s):
  # TODO: split on , then find index of dept (eg, PNI, CSES, RC, Chemistry)
  import re
  phone = re.compile(r'\d\d\d-\d\d\d-\d\d\d\d')
  has_number = re.compile(r'\d')
  if s.endswith(',,,'):
    # Anna Chorniy,,,
    return s.replace(',', '')
  elif bool(phone.search(s)):
    # Christine M. McCoy,110 Peretsman Scully Hall,609-258-4442,
    return s.split(',')[0]
  elif bool(has_number.search(s)) or s.endswith(',NONE,'):
    # Jonathan T. Wilding,317 87 Prospect Avenue,8-6025,
    # Prasad S. Lakkaraju,101 Frick Lab,NONE,
    return s.split(',')[0]
  elif len(s.split(',')[0].split(' ')) == 1:
    # Park, Noel R.,Genomics,Shawn M. Davidson
    # Hossein Valavi,PNI,Peter J. Ramadge,Naveen Verma
    parts = s.split(',')
    return parts[1].strip() + ' ' + parts[0]
  elif s.count(',') == 2:
    return s.split(',')[0]
  else:
    return s.split(',')[0]

files = ['tigressdata_getent.txt', 'adroit_getent.txt', 'della_getent.txt', \
         'perseus_getent.txt', 'tiger_getent.txt', 'traverse_getent.txt']

df = pd.DataFrame()
for f in files:
  tmp = pd.read_csv(f, header=None, delimiter=':')
  tmp['cluster'] = 'adroit' if 'adroit' in f else 'other'
  df = df.append(tmp)
df.columns = ['netid', 'sym', 'uid', 'gid', 'name_sponsor', \
              'home', 'login', 'cluster']

# clean the dataframe
df = df[['netid', 'name_sponsor', 'home', 'cluster']]
df = df[df.name_sponsor.notna() & df.name_sponsor.str.contains(',')]
df = df[df.home.str.contains('/home/', regex=False)]
df.drop(columns='home', inplace=True)
msk1 = ~df.name_sponsor.str.contains('pniguest', regex=False)
msk2 = ~df.name_sponsor.str.contains('Class account', regex=False)
df = df[msk1 & msk2]
df.drop_duplicates(inplace=True)

# add count (cnt) field
df['cnt'] = df.netid.apply(lambda x: df[df.netid == x].shape[0])

# remove adroit entry when second entry exists
msk2 = (df.cnt > 1) & (~df.cluster.str.contains('adroit', regex=False))
df = df[(df.cnt == 1) | msk2]

# assume records are equal in a sense across clusters
df = df[['netid', 'name_sponsor']].drop_duplicates('netid', keep='first')

df['NAME'] = df.name_sponsor.apply(extract_name)

df = df[['netid', 'NAME']].sort_values(by='netid', ascending=True)
df.to_csv('combined_getent.csv', index=False)
