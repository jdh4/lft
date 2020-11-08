from time import time
from datetime import datetime
import subprocess
from subprocess import PIPE as sPIPE

############
## sshare ##
############
def sshare(term, gutter, host, netid):
  # TODO looks like molbio has 6% of traverse
  """Return fairshare, group usage and group cluster share"""
  cmd = f"sshare -l -u {netid}"
  output = subprocess.run(cmd, capture_output=True, shell=True, timeout=3)
  lines = output.stdout.decode("utf-8").split('\n')
  usage = []
  for i, line in enumerate(lines):
    if ' ' + netid + ' ' in line and i != 0:
      fairshare = f"{float(line.split()[7]):.2f}"
      clr1 = f"{term.bold}{term.red}" if float(fairshare) < 0.15 else ""
      group = lines[i - 1].split()[0].upper()
      normShares = float(lines[i - 1].split()[2])
      normUsage  = float(lines[i - 1].split()[4])
      if normShares == 0:
        ratio = "N/A"
      else:
        ratio = int(round(100 * normUsage / normShares, -1))
        ratio = f"{ratio}%"
      clr2 = f"{term.bold}{term.red}" if ratio != "N/A" and int(ratio.replace("%", "")) > 200 else ""
      gshare = f"{round(100 * normShares)}%"
      usage.append(f"{gutter}Fairshare: {clr1}{fairshare}{term.normal}   30-day {group} usage: {clr2}{ratio}{term.normal}"
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
    priority = 0
    dependency = 0
    qosmax = 0
    reqnode = 0
    for line in lines:
      if (' R ' in line): running += 1
      if (' PD ' in line): pending += 1
      if (' (Priority) ' in line): priority += 1
      if (' (Dependency) ' in line): dependency += 1
      if ('(QOSMax' in line): qosmax += 1
      if ('ReqNodeNotAvail' in line): reqnode += 1
    if (running or pending):
      if pending:
        return (f"{gutter}Running: {running}   Pending: {pending} (Priority:{priority}, Dependency:{dependency}, QOSMax+:{qosmax}, ReqNodeNotAvail: {reqnode})")
      else:
        return (f"{gutter}Running: {running}   Pending: {pending}")
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
      return f"{round(minutes + seconds / 60)}m"
    else:
      return f"{seconds}s"
  elif x.count(":") == 2 and "-" not in x:
    hours, minutes, seconds = map(int, x.split(":"))
    if (hours + minutes + seconds == 0):
      return "0s"
    elif (hours + minutes == 0):
      return f"{seconds}s"
    elif (hours == 0):
      return f"{round(minutes + seconds / 60)}m"
    elif (hours == 1):
      return f"{round(60 + minutes + seconds / 60)}m"
    else:
      return f"{round(hours + minutes / 60 + seconds / 3600)}h"
  elif x.count(":") == 2 and "-" in x:
    days = int(x.split("-")[0])
    hours, minutes, seconds = map(int, x.split("-")[1].split(":"))
    return f"{round(24 * days + hours + minutes / 60 + seconds / 3600)}h"
  else:
    return " -- "

def format_start(x):
  if x == "Unknown":
    return x
  else:
    try:
      start = datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").strftime("%-m/%-d-%H:%M")
    except:
      return "--"
    else:
      return start

def format_memory(x):
  return x.replace("000Gn", "T/N") \
          .replace("000Gc", "T/c") \
          .replace("000Mn", "G/N") \
          .replace("000Mc", "G/c") \
          .replace("Gn", "G/N") \
          .replace("Gc", "G/c") \
          .replace("Mc", "M/c") \

def format_state(x, state):
  x = "CANCELLED" if "CANCELLED" in x else x
  return state[x] if x in state else "--"

def format_reqgres(x):
  return x.replace("PER_NODE:", "").replace("PER_TASK:", "") \
          .replace("gpu:tesla_v100", "v100") \
          .replace("gpu:tesla_k40c", "k40c").strip()

def format_qos(x):
  return x.replace("tiger", "tgr").replace("short", "sh").replace("medium", "med") \
          .replace("long", "lg").replace("test", "ts")

def format_jobname(x):
  x = x.strip()
  if x == "sys/dashboard/sys/jupyter":
    x = "O-JUPYTER"
  elif x == "sys/dashboard/sys/matlab":
    x = "O-MATLAB"
  elif x == "sys/dashboard/sys/rstudio_server":
    x = "O-RSTUDIO"
  elif x == "sys/dashboard/sys/xstata":
    x = "O-STATA"
  return x if len(x) <= 9 else x[:8] + "+"

def cmt_efficiency(elapraw, limitraw, reqmem, nnodes, ncpus, maxrss):
  # compute ratio of used to allocated time
  if limitraw.isdigit() and elapraw.isdigit():
    if int(limitraw) == 0:
      T = " "
    else:
      seconds_per_minute = 60
      ratio = float(elapraw) / (seconds_per_minute * int(limitraw))
      if ratio > 1: ratio = 1
      T = str(round(9 * ratio))
  else:
    T = " "
  # compute ratio of used to allocated memory
  if maxrss == -1 or not nnodes.isdigit() or not ncpus.isdigit():
    M = " "
  elif "N" in reqmem:
    mem = reqmem.replace("T/N", "000000000").replace("G/N", "000000") \
                .replace("M/N", "000").replace("K/N", "")
    alloc = int(nnodes) * int(mem)
    ratio = float(maxrss) / alloc
    if ratio > 1: ratio = 1
    M = str(round(9 * ratio))
  elif "c" in reqmem:
    mem = reqmem.replace("T/c", "000000000").replace("G/c", "000000") \
                .replace("M/c", "000").replace("K/c", "")
    alloc = int(ncpus) * int(mem)
    ratio = float(maxrss) / alloc
    if ratio > 1: ratio = 1
    M = str(round(9 * ratio))
  else:
    M = " "
  return f"{M}{T}"

def get_maxrss(x):
  # add dummy line in order to get memory of last row
  lines = x[::]
  lines.append("|||")
  maxmem = {}
  jobid_prev = lines[0].split("|")[0]
  if ("." in jobid_prev): return maxmem
  maxrss = -1
  for line in lines:
    items = line.split("|")
    jobid = items[0].split(".")[0]
    if (jobid != jobid_prev):
      maxmem[jobid_prev] = maxrss
      jobid_prev = jobid
      maxrss = -1
    def format_rss(x):
      x = x.replace("K", "").replace("M", "000").replace("G", "000000") \
           .replace("T", "000000000")
      return int(x) if x.isdigit() else -1
    rss = format_rss(items[-2])
    if (rss > maxrss): maxrss = rss
  return maxmem
 
def align_columns(rows, cols, max_width, term, gutter, host):
  drop = ["elapsedraw", "timelimitraw", "cputimeraw", "maxrss"]
  for d in drop:
    cols.remove(d)
  trans = {'jobid':'JobID', 'jobname':'Name', 'state':'ST', 'start':'Start', \
           'elapsed':'Elap', 'partition':'Prt', 'ncpus':'c', 'nnodes':'N', \
           'reqmem':'Mem', 'timelimit':'Lim', 'reqgres':'gres', 'qos':'QoS'}
  abbr = [trans[col] if col in trans else col for col in cols]

  # manually adjust width
  max_width['jobname'] = max(4, max_width['jobname'])
  max_width['state'] = max(2, max_width['state'])
  max_width['elapsed'] = max(4, max_width['state'])
  max_width['timelimit'] = max(3, max_width['timelimit'])
  if (host == "tiger" or host == "adroit" or host == "traverse"):
    max_width['reqgres'] = max(4, max_width['reqgres'])
  max_width['qos'] = max(3, max_width['qos'])

  line = gutter
  for i, col in enumerate(cols):
    if len(abbr[i]) >= max_width[col]:
      padding = ""
      remainder = 0
      dpadding = (len(abbr[i]) - max_width[col]) // 2
    else:
      padding = " " * ((max_width[col] - len(abbr[i])) // 2)
      remainder = max_width[col] - len(abbr[i]) - 2 * len(padding)
      dpadding = 0
    #print(abbr[i], max_width[col], len(padding), remainder, dpadding)
    field = padding + " " * remainder + abbr[i] + padding
    line += field + "  "
  sct = [line]
  for row in rows:
    line = gutter
    for col in cols:
      fieldraw = getattr(row, col)
      field = " " * max_width[col] + fieldraw + " " * dpadding * 0
      field = field[-max_width[col]:]
      if col == "state" and fieldraw in ("TO", "OOM", "F", "NF", "BF"):
        field = f"{term.bold}{term.red}{field}{term.normal}"
      if col == "jobname" and fieldraw in ("O-JUPYTER", "O-RSTUDIO", "O-MATLAB", "O-STATA"):
        field = f"{term.bold}{term.green}{field}{term.normal}"
      line += field + "  "
    sct.append(line)
  return sct

def sacct(term, gutter, verbose, host, netid, days=3):
  """Return output of sacct over the last N days. The is a messy and confusing routine."""
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
  # sacct -u hzerze -S 09/24 -o jobid%20,state,start,elapsed,ncpus,nnodes,reqmem,partition,reqgres,qos,timelimit,jobname%8
  if (host == "tiger" or host == "adroit" or host == "traverse"):
    frmt = "jobid%20,state,start,elapsed,elapsedraw,timelimit,timelimitraw,cputimeraw,ncpus,nnodes,reqmem,partition,reqgres,qos,jobname%40,maxrss"
  else:
    frmt = "jobid%20,state,start,elapsed,elapsedraw,timelimit,timelimitraw,cputimeraw,ncpus,nnodes,reqmem,partition,qos,jobname%40,maxrss"
  #cmd = f"sacct -S {start} -u {netid} -o {frmt} -n -p | egrep -v '[0-9].extern|[0-9].batch|[0-9]\.[0-9]\|'"
  cmd = f"sacct -S {start} -u {netid} -o {frmt} -n -p"
  output = subprocess.run(cmd, stdout=sPIPE, shell=True, timeout=3, text=True)
  lines = output.stdout.split('\n')
 
  # avoid dependency on pandas by using namedtuple
  from collections import namedtuple
  extra_columns = ["MT"]
  columns = [col.split('%')[0] for col in frmt.split(",")] + extra_columns
  Job = namedtuple("Job", columns)
  #breakpoint()
  sct = []
  if lines[-1] == '': lines = lines[:-1]
  if (lines == []):
    return [f"{gutter}No jobs in last {24 * days} hours"]
  else:
    try:
      maxmem_per_job = get_maxrss(lines)
      #print(lines)
      #print(maxmem_per_job)
      #breakpoint()
      max_width = dict(zip(columns, [0] * len(columns)))
      overall = []
      for line in lines:
        if "." not in line.split("|")[0]: overall.append(line)
      cut = 24 if verbose else 12 
      if len(overall) > cut: overall = overall[-cut:]
      for line in overall:
        line = line.replace("||", "|      |")
        items = line.split("|")[:-1] + [""] * len(extra_columns)
        j = Job(*items)
        # format of start is 2020-09-13T11:42:34
        j = j._replace(jobname = format_jobname(j.jobname))
        j = j._replace(start = format_start(j.start))
        j = j._replace(state = format_state(j.state, state))
        j = j._replace(elapsed = format_elapsed_time(j.elapsed))
        if (host == "tiger" or host == "adroit" or host == "traverse"):
          j = j._replace(reqgres = format_reqgres(j.reqgres))
        j = j._replace(qos = format_qos(j.qos))
        j = j._replace(reqmem = format_memory(j.reqmem))
        j = j._replace(timelimit = format_elapsed_time(j.timelimit))
        maxrss = maxmem_per_job[j.jobid] if j.jobid in maxmem_per_job else -1
        j = j._replace(MT = cmt_efficiency(j.elapsedraw, j.timelimitraw, j.reqmem, j.nnodes, j.ncpus, maxrss))
        for col in columns:
          if len(getattr(j, col)) > max_width[col]: max_width[col] = len(getattr(j, col))
        sct.append(j)
      #breakpoint()
      sct = align_columns(sct, columns, max_width, term, gutter, host)
    except:
      return [f"{gutter}Misformatted sacct output found"]
    else:
      return sct
