import subprocess
from panes import utils

####################
## sponsor_report ##
####################

# $ sponsor_report jdh4
# No sponsored users for jdh4 (Jonathan D. Halverson)
# This user is sponsored by curt

# $ sponsor_report aturing
# FATAL ERROR: Could not find user aturing in Princeton LDAP

# $ sponsor_report hwaight
# hwaight (Hannah C. Waight) has no Tigress account

# $ sponsor_report ethier
# Manager ethier (Stephane Ethier) has sponsored the following users
#      gascione (George Ascione) has accounts on eddy
#
# Cluster eddy has these users gascione

def get_sponsor(netid):

  cmd = f"sponsor_report {netid}"
  try:
    output = subprocess.run(cmd, capture_output=True, shell=True, timeout=5)
  except subprocess.TimeoutExpired:
    sponsor = None
  except:
    # netid not in Princeton LDAP
    sponsor = None
  else:
    lines = output.stdout.decode("utf-8").split('\n')
    if output.returncode == 1: return ("<NON-ASCII>", "<NON-ASCII>")
    if len(lines) > 1 and 'No sponsored users' in lines[0]:
      sponsor = lines[1].split()[-1]
    elif "Manager" in lines[0] and "has sponsored" in lines[0]:
      sponsor = netid
    else:
      sponsor = None

  if sponsor:
    accounts = []
    cmd = f"sponsor_report {sponsor}"
    try:
      output = subprocess.run(cmd, capture_output=True, shell=True, timeout=5)
    except:
      pass
    else:
      lines = output.stdout.decode("utf-8").split('\n')
      if output.returncode == 1: return ("<NON-ASCII>", "<NON-ASCII>")
      for line in lines:
        if "Manager" in line and "has sponsored" in line:
          # Manager pdebene (Pablo G. Debenedetti) has sponsored the following users
          sponsor_full_name = line.split('(')[1].split(')')[0]
          sponsor_full_name = utils.remove_middle_initial(sponsor_full_name)
          return (sponsor_full_name, sponsor)
  else:
    return (None, None)
