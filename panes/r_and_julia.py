import os
from os.path import isdir
from datetime import datetime
from panes import utils
from panes.utils import divider

################
## R packages ##
################
def clean_r_packages(pkgs):
  noshow = []
  return sorted(list(set(pkgs) - set(noshow)), key=lambda p: p.lower())

def r_packages(netid, evars, term, gutter, width, verbose):
  printed_r_divider = False
  print_single = False

  frmt = "(%b %Y)"

  parallel = ['furrr', 'Rmpi', 'doMPI', 'doMC', 'doParallel', 'future', 'fastLink', 'snow']
  trouble  = ['sf', 'rstan', 'gurobi']
  green    = ['caret']

  # check for R libraries in the default location
  path = f"/home/{netid}/R"
  if isdir(path):
    for version in ['3.3', '3.4', '3.5', '3.6', '4.0', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6']:
      path = f"/home/{netid}/R/x86_64-redhat-linux-gnu-library/{version}"
      if isdir(path):
        if utils.is_rx(path):
          if not printed_r_divider:
            divider(term.bold('R'), '', gutter, width)
            printed_r_divider = True
          pkgs = os.listdir(path)
          pkgs = clean_r_packages(pkgs)
          if verbose:
            if print_single: print('-' * width)
            mtime = datetime.fromtimestamp(os.stat(path).st_mtime)
            mtime = mtime.strftime(frmt)
            print(f"     ~/R/x86_64-redhat-linux-gnu-library/{term.bold}{version}{term.normal} {mtime}")
            lock = [pkg for pkg in pkgs if 'LOCK' in pkg]
            red = parallel + trouble + lock
            utils.print_packages(term, gutter, width, pkgs, red, green, max_chars=13)
            print_single = True
          else:
            print(f"{gutter}~/R/x86_64-redhat-linux-gnu-library/{term.bold}{version}{term.normal}")
        else:
          print(f"{path} is private")

  # check for R libraries in conda environments
  path = f"/home/{netid}/.conda"
  if isdir(path):
    path = f"/home/{netid}/.conda/envs"
    if isdir(path):
      if utils.is_rx(path):
        envs = os.listdir(path)
        if '.conda_envs_dir_test' in envs: envs.remove('.conda_envs_dir_test')
        for env in envs:
          path = f"/home/{netid}/.conda/envs/{env}/lib/R/library"
          if isdir(path):
            if utils.is_rx(path):
              if not printed_r_divider:
                divider(term.bold('R'), '', gutter, width)
                printed_r_divider = True
              pkgs = os.listdir(path)
              pkgs = clean_r_packages(pkgs)
              if verbose:
                if print_single: print('-' * width)
                mtime = datetime.fromtimestamp(os.stat(path).st_mtime)
                mtime = mtime.strftime(frmt)
                print(f"     ~/.conda/envs/{term.bold}{env}{term.normal}/lib/R/library {mtime}")
                lock = [pkg for pkg in pkgs if 'LOCK' in pkg]
                red = parallel + trouble + lock
                utils.print_packages(term, gutter, width, pkgs, red, green, max_chars=13)
                print_single = True
              else:
                print(f"{gutter}~/.conda/envs/{term.bold}{env}{term.normal}/lib/R/library")
            else:
              print(f"{path} is private")

  # R misc
  opath = f"/home/{netid}/ondemand/data/sys/dashboard/batch_connect/sys/rstudio_server/output"
  ondemand = isdir(opath)
  rlibs = evars["rlibs"]
  rlibsuser = evars["rlibsuser"]
  path = f"/home/{netid}/.R/Makevars"
  path_environ = f"/home/{netid}/.Renviron"
  path_profile = f"/home/{netid}/.Rprofile"
  if printed_r_divider and (os.path.isfile(path) or os.path.isfile(path_environ) or \
     os.path.isfile(path_profile) or rlibs[0] or rlibsuser[0] or ondemand):
    print("-" * width)
    if os.path.isfile(path):
      print(f"{gutter}{term.bold}{term.red}{path}{term.normal}")
    if os.path.isfile(path_environ):
      print(f"{gutter}{term.bold}{term.red}{path_environ}{term.normal}")
    if os.path.isfile(path_profile):
      print(f"{gutter}{term.bold}{term.red}{path_profile}{term.normal}")
    if rlibs[0]: print(f"{gutter}R_LIBS set in ~/{rlibs[1]}")
    if rlibsuser[0]: print(f"{gutter}R_LIBS_USER set in ~/{rlibsuser[1]}")
    if ondemand:
      utils.ondemand_last_used("RStudio", opath, gutter)
      lpath = f"/home/{netid}/.local/share/rstudio"
      if isdir(lpath):
        print(f"{gutter}{lpath} exists")
  return None

###########
## julia ##
###########
def julia_packages(netid, term, gutter, width, verbose):
  path = f"/home/{netid}/.julia"
  if isdir(path):
    path = f"{path}/packages"
    if isdir(path):
      if utils.is_rx(path):
        pkgs = os.listdir(path)
        if pkgs:
          if verbose:
            divider(term.bold('Julia') + ' (~/.julia/packages)', '', gutter, width)
            noshow = []
            pkgs = sorted(list(set(pkgs) - set(noshow)), key=lambda p: p.lower())
            green = ['Flux', 'GPUArrays', 'CUDA', 'CUDAdrv', 'CUDAnative', 'CuArrays', \
                     'TensorFlow', 'Knet', 'ScikitLearn']
            red = []
            utils.print_packages(term, gutter, width, pkgs, red, green)
          else:
            divider(term.bold('Julia'), '', gutter, width)
            print(f"{gutter}~/.julia/packages")
      else:
        divider(term.bold('Julia'), '', gutter, width)
        print(f"{gutter}~/.julia/packages is private")
