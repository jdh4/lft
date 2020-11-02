import os
from math import ceil

def divider(title, msg, gutter, width):
  print("")
  print(f"{gutter}{title}")
  print("=" * width)
  if msg: print(msg)
  return None

def is_rx(path):
  # true if permissions are rx or rwx for other
  return oct(os.stat(path).st_mode)[-1] in ['5', '7']

def public_or_private(path):
  if is_rx(path):
    return f"{path}: public ({len(os.listdir(path))} items)"
  else:
    return f"{path}: private"

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

##########################
## hostname translation ##
##########################
known_hosts = {
'tigercpu.princeton.edu':'tiger',
'tigergpu.princeton.edu':'tiger',
'della5.princeton.edu':'della',
'perseus':'perseus',
'traverse.princeton.edu':'traverse',
'adroit4':'adroit',
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
