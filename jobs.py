from time import time
from datetime import datetime
import subprocess
from subprocess import PIPE as sPIPE

############
## sshare ##
############
def sshare(term, gutter, host, netid):
  """Return fairshare, group usage and group cluster share"""
  cmd = f"sshare -l -u {netid}"
  output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
  lines = output.stdout.decode("utf-8").split('\n')
  usage = []
  for i, line in enumerate(lines):
    if ' ' + netid + ' ' in line and i != 0:
      fairshare = f"{float(line.split()[7]):.2f}"
      group = lines[i - 1].split()[0].upper()
      normShares = float(lines[i - 1].split()[2])
      normUsage  = float(lines[i - 1].split()[4])
      if normShares == 0:
        ratio = "N/A"
      else:
        ratio = int(round(100 * normUsage / normShares, -1))
        ratio = f"{ratio}%"
      clr = f"{term.bold}{term.red}" if ratio != "N/A" and int(ratio.replace("%", "")) > 200 else ""
      gshare = f"{round(100 * normShares)}%"
      usage.append(f"{gutter}Fairshare: {fairshare}   30-day {group} usage: {clr}{ratio}{term.normal}"
                   f"   {group} share of cluster: {gshare}")
  return usage

############
## squeue ##
############
def squeue(gutter, host, netid):
  """Return number of running and queued jobs plus more"""
  if host != 'tigressdata':
    cmd = "squeue -u " + netid
    output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
    lines = output.stdout.decode("utf-8").split('\n')
    running = 0
    pending = 0
    qosmax = 0
    reqnode = 0
    for line in lines:
      if (' R ' in line): running += 1
      if (' PD ' in line): pending += 1
      if (' QOSMax' in line): qosmax += 1
      if ('ReqNodeNotAvail' in line): reqnode += 1
    if (running or pending or qosmax or reqnode):
      return (f"{gutter}Running: {running}   Pending: {pending}   QOSMax+: {qosmax}"
              f"   ReqNodeNotAvail: {reqnode}")
    else:
      return ""
  else:
    return ""

###########
## sacct ##
###########

# https://wiki.hpcc.msu.edu/display/ITH/Show+Job+Steps+by+sacct+and+srun+Commands
# <jobid>.0 is first srun/mpirun job step
# <jobid>.1 is second srun/mpirun job step
# https://stackoverflow.com/questions/52447602/slurm-sacct-shows-batch-and-extern-job-names
# Each job contains multiple job steps and each step is accounted for.
# %j.batch accounts for the resources needed for the batch script
# %j.extern accounts for all resource usage by the job outside of slurm (e.g., ssh)
# %j is the overall job

def format_elapsed_time(x):
  # 2-23:52:33 or 23:57:47 or 8:55
  if x.count(":") == 1:
    minutes, seconds = map(int, x.split(":"))
    if minutes > 0:
      return f"{round(minutes + seconds / 60)} min"
    else:
      return f"{seconds} sec"
  elif x.count(":") == 2 and "-" not in x:
    hours, minutes, seconds = map(int, x.split(":"))
    if (hours + minutes + seconds == 0):
      return "0 sec"
    elif (hours + minutes == 0):
      return f"{seconds} sec"
    elif (hours == 0):
      return f"{round(minutes + seconds / 60)} min"
    elif (hours == 1):
      return f"{round(60 + minutes + seconds / 60)} min"
    else:
      return f"{round(hours + minutes / 60 + seconds / 3600)} hrs"
  elif x.count(":") == 2 and "-" in x:
    days = int(x.split("-")[0])
    hours, minutes, seconds = map(int, x.split("-")[1].split(":"))
    return f"{round(24 * days + hours + minutes / 60 + seconds / 3600)} hrs"
  else:
    return " -- "

def format_start(x):
  if x == "Unknown":
    return x
  else:
    try:
      start = datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").strftime("%m/%d %H:%M")
    except:
      return "--"
    else:
      return start

def format_memory(x):
  return x.replace("4000Mc", "4Gc").replace("Mc", " Mc").replace("Gc", " Gc").replace("Gn", " Gn")

def format_state(x, state):
  x = "CANCELLED" if "CANCELLED" in x else x
  return state[x] if x in state else "--"

def align_columns(rows, cols, max_width, gutter):
  trans = {'jobid':'JobID ', 'jobname':'Name  ', 'state':'ST', 'start':'Start   ', \
           'elapsed':'Elap ', 'partition':'Prt', 'ncpus':'n', 'nnodes':'N', \
           'reqmem':'Mem ', 'timelimit':'limit'}
  abbr = [trans[col] if col in trans else col for col in cols]

  # manually adjust width
  max_width['jobname'] = 8
  max_width['state'] = max(2, max_width['state'])

  line = gutter
  for i, col in enumerate(cols):
    field = " " * max_width[col] + abbr[i]
    field = field[-max_width[col]:]
    line += field + "  "
  sct = [line]
  for row in rows:
    line = gutter
    for col in cols:
      if col == "jobname":
        field = getattr(row, col)
        field = field if len(field) <= 8 else field[:7] + "+"
        field = " " * (8 - len(field)) + field
        line += field + "  "
      else:
        field = " " * max_width[col] + getattr(row, col)
        field = field[-max_width[col]:]
        line += field + "  "
    sct.append(line)
  return sct

def sacct(gutter, host, netid, days=3):
  """Return output of sacct over the last N days."""
  state = {
  'BF'  :'BOOT_FAIL',
  'CLD' :'CANCELLED',
  'COM' :'COMPLETED',
  'DL'  :'DEADLINE',
  'F'   :'FAILED',
  'NF'  :'NODE_FAIL',
  'OOM' :'OUT_OF_MEMORY',
  'PD'  :'PENDING',
  'PR'  :'PREEMPTED',
  'R'   :'RUNNING',
  'RQ'  :'REQUEUED',
  'RS'  :'RESIZING',
  'RV'  :'REVOKED',
  'S'   :'SUSPENDED',
  'TO'  :'TIMEOUT'
  }
  state = dict(zip(state.values(), state.keys()))
  # sacct format is YYYY-MM-DD[THH:MM[:SS]]
  start = datetime.fromtimestamp(time() - days * 24 * 60 * 60).strftime('%Y-%m-%d-%H:%M')
  if (host == "tiger"):
    # sacct -u hzerze -S 09/24 -o jobid%20,start,end,state,jobname%20,reqtres%40
    frmt = 'jobid%20,state,start,elapsed,ncpus,nnodes,reqmem,partition,reqgres,qos,timelimit,jobname%8'
  else:
    frmt = 'jobid%20,start,end,state,ncpus,nnodes,partition,jobname%8,reqtres%40'
  cmd = f"sacct -S {start} -u {netid} -o {frmt} -n -p | egrep -v '[0-9].extern|[0-9].batch|[0-9]\.[0-9]\|'"
  output = subprocess.run(cmd, stdout=sPIPE, shell=True, timeout=3, text=True)
  lines = output.stdout.split('\n')
 
  # avoid dependency on pandas (and slow startup) by using namedtuple
  from collections import namedtuple
  columns = [col.split('%')[0] for col in frmt.split(",")]
  Job = namedtuple("Job", columns)
  #breakpoint()
  max_width = dict(zip(columns, [0] * len(columns)))
  sct = []
  if lines[-1] == '': lines = lines[:-1]
  if (len(lines) == 0):
    return [f"{gutter}No jobs in last {24 * days} hours"]
  else:
    try:
      if (len(lines) > 1):
        if len(lines) > 10: lines = lines[-10:]
        for line in lines:
          items = line.split("|")[:-1]
          #print(items)
          j = Job(*items)
          # format of start is 2020-09-13T11:42:34
          j = j._replace(start = format_start(j.start))
          j = j._replace(state = format_state(j.state, state))
          j = j._replace(elapsed = format_elapsed_time(j.elapsed))
          j = j._replace(reqmem = format_memory(j.reqmem))
          j = j._replace(timelimit = format_elapsed_time(j.timelimit))
          for col in columns:
            if len(getattr(j, col)) > max_width[col]: max_width[col] = len(getattr(j, col))
          sct.append(j)
        sct = align_columns(sct, columns, max_width, gutter)
    except:
      return [f"{gutter}Misformatted sacct output found"]
    else:
      return sct
