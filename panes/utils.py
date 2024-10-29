import os
import subprocess
from os import access, R_OK
from math import ceil
from datetime import datetime

def divider(title, msg, gutter, width):
  print("")
  print(f"{gutter}{title}")
  print("=" * width)
  if msg: print(msg)
  return None

def is_rx(path):
  # true if permissions are rx or rwx for other
  return oct(os.stat(path).st_mode)[-1] in ['5', '7']

def is_r(path):
  return access(path, R_OK)

def public_or_private(path):
  if is_rx(path):
    return f"{path}: public ({len(os.listdir(path))} items)"
  else:
    return f"{path}: private"

#################
## last active ##
#################
#$ last -F -R -n 1 jl40
#
#wtmp begins Tue Dec  1 03:51:13 2020

#$ last -F -R -n 1 hzerze
#hzerze   pts/3        Sat Dec 12 10:56:59 2020 - Sat Dec 12 13:08:53 2020  (02:11)    
#
#wtmp begins Tue Dec  1 03:40:19 2020

#$ last -F -R -n 1 jdh4
#jdh4     pts/11       Sat Dec 12 12:57:18 2020   still logged in                      
#
#wtmp begins Tue Dec  1 03:40:19 2020

def extract_datetime(lines):
  if len(lines) != 4:
    return None
  else:
    if "still logged in" in lines[0]:
      return "logged in"
    elif "no logout" in lines[0]:
      #syue     pts/29       Fri Jun 18 11:34:19 2021   gone - no logout
      items = lines[0].split()[3:7]
      return datetime.strptime("-".join(items), '%b-%d-%H:%M:%S-%Y')
    else:
      #syue     pts/31       Fri Jun 18 13:31:38 2021 - Fri Jun 18 19:37:05 2021  (06:05)    
      items = lines[0].split()[9:13]
      return datetime.strptime("-".join(items), '%b-%d-%H:%M:%S-%Y')
 
def last_command(netid):
  cmd = f"last -F -R -n 1 {netid}"
  try:
    output = subprocess.run(cmd, capture_output=True, shell=True, timeout=5)
  except:
    return None
  else:
    lines = output.stdout.decode("utf-8").split('\n')
    return extract_datetime(lines)

def last_active(netid):
  """The last time active is taken as the more recent of the modification time
     of /home and the top entry from the last command."""
  # from finger
  # Last login Sat Mar  9 11:26 2019 (EST) on pts/19 from vpn10-client-128-112-69-104.princeton.edu
  # Last login Thu Apr 29 15:40 (EDT) on pts/48 from mydella
  # On since Sun May  2 12:52 (EDT) on pts/60 from mydella
  # Never logged in.
  mtime = datetime.fromtimestamp(os.stat(f"/home/{netid}").st_mtime)
  ltime = last_command(netid)
  if ltime:
    if ltime == "logged in": return f"  Active: {ltime}"
    if ltime > mtime: mtime = ltime
  dt = datetime.today() - mtime
  if dt.days == 0:
    hours = dt.seconds // 3600
    minutes = dt.seconds // 60
    if hours > 1:
      return f"  Active: {hours} hours ago"
    elif minutes > 1:
      return f"  Active: {minutes} minutes ago"
    else:
      return f"  Active: {dt.seconds} seconds ago"
  elif dt.days == 1:
    if dt.seconds // 3600 < datetime.today().hour:
      return "  Active: yesterday"
    else:
      return f"  Active: 2 days ago"
  else:
    if dt.days <= 365:
      return f"  Active: {dt.days} days ago ({mtime.strftime('%b %-d')})"
    else:
      return f"  Active: {dt.days} days ago ({mtime.strftime('%-m/%-d/%Y')})"

def print_packages(term, gutter, width, pkgs, red, green, max_chars=14):
  color = []
  for pkg in pkgs:
    if pkg in green:
      color.append(f"{term.bold}{term.green}")
    elif pkg in red:
      color.append(f"{term.bold}{term.red}")
    else:
      color.append("")
  columns = (width - 2 * len(gutter)) // max_chars
  rows = ceil(len(pkgs) / columns)
  for i in range(rows):
    s = gutter
    for j in range(columns):
      idx = j + columns * i
      if idx >= len(pkgs): break
      pkg = pkgs[idx]
      if len(pkg) > max_chars - 1: pkg = pkg[:max_chars - 2] + "+ "
      s += color[idx] + pkg + term.normal + " " * (max_chars - len(pkg))
    print(s)
  return None

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

def ondemand_last_used(app, opath, gutter):
  mtime = datetime.fromtimestamp(os.stat(opath).st_mtime)
  dt = datetime.today() - mtime
  if dt.days == 0:
    hours = dt.seconds // 3600
    minutes = dt.seconds // 60
    if hours > 1:
      print(f"{gutter}OnDemand {app}: {hours} hours ago")
    elif minutes > 1:
      print(f"{gutter}OnDemand {app}: {minutes} minutes ago")
    else:
      print(f"{gutter}OnDemand {app}: {dt.seconds} seconds ago")
  elif dt.days == 1:
    print(f"{gutter}OnDemand {app}: (yesterday)")
  elif dt.days <= 31:
    print(f"{gutter}OnDemand {app}: {dt.days} days ago")
  elif dt.days <= 365:
    frmt = "%b %-d"
    mtime = mtime.strftime(frmt)
    print(f"{gutter}OnDemand {app}: {mtime}")
  else:
    frmt = "%b %-d %Y"
    mtime = mtime.strftime(frmt)
    print(f"{gutter}OnDemand {app}: {mtime}")
  print(f"{gutter}{opath} exists")

##########################
## hostname translation ##
##########################
known_hosts = {
'tigercpu.princeton.edu':'tiger',
'tigergpu.princeton.edu':'tiger',
'tiger3.princeton.edu':'tiger3',
'tiger3-vis.princeton.edu':'tiger3',
'della8.princeton.edu':'della',
'della-gpu.princeton.edu':'della',
'della-vis1.princeton.edu':'della',
'della-vis2.princeton.edu':'della',
'adroit5':'adroit',
'adroit-vis.princeton.edu':'adroit',
'stellar-intel.princeton.edu':'stellar',
'stellar-amd.princeton.edu':'stellar',
'stellar-vis1.princeton.edu':'stellar',
'stellar-vis2.princeton.edu':'stellar',
'traverse.princeton.edu':'traverse',
'tigressdata2.princeton.edu':'tigressdata'}

#####################
## default .bashrc ##
#####################
bashrc_default="""
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
""".split('\n')

###########################
## default .bash_profile ##
###########################
bash_profile_default = """
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/.local/bin:$HOME/bin

export PATH
""".split('\n')

bashrc_default8="""
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
""".split('\n')

bash_profile_default8 = """
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

# User specific environment and startup programs
""".split('\n')
