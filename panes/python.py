#      ___                                 ___           ___           ___     
#     /  /\        ___         ___        /__/\         /  /\         /__/\    
#    /  /::\      /__/|       /  /\       \  \:\       /  /::\        \  \:\   
#   /  /:/\:\    |  |:|      /  /:/        \__\:\     /  /:/\:\        \  \:\  
#  /  /:/~/:/    |  |:|     /  /:/     ___ /  /::\   /  /:/  \:\   _____\__\:\ 
# /__/:/ /:/   __|__|:|    /  /::\    /__/\  /:/\:\ /__/:/ \__\:\ /__/::::::::\
# \  \:\/:/   /__/::::\   /__/:/\:\   \  \:\/:/__\/ \  \:\ /  /:/ \  \:\~~\~~\/
#  \  \::/       ~\~~\:\  \__\/  \:\   \  \::/       \  \:\  /:/   \  \:\  ~~~ 
#   \  \:\         \  \:\      \  \:\   \  \:\        \  \:\/:/     \  \:\     
#    \  \:\         \__\/       \__\/    \  \:\        \  \::/       \  \:\    
#     \__\/                               \__\/         \__\/         \__\/    

import os
from os.path import isdir
from datetime import datetime
from panes import utils
from panes.utils import divider

def clean_python_packages(pkgs):
  noshow = ['lib', 'bin', '__pycache__', 'six', 'pasta', 'pip', 'wheel', \
            'setuptools', 'pkgconfig', '_pytest']
  pkgs_cleaned = []
  for pkg in pkgs:
    parts = pkg.split('-')
    if len(parts) > 1 and parts[1][0].isalpha():
      pkg_cleaned = '-'.join([parts[0], parts[1]])
    else:
      pkg_cleaned = parts[0]
    pkgs_cleaned.append(pkg_cleaned)
  return sorted(list(set(pkgs_cleaned) - set(noshow)), key=lambda p: p.lower())

def check_python(printed_divider, term, gutter, width):
  if not printed_divider:
    divider(term.bold('Python'), '', gutter, width)
  return True

def python_packages(netid, evars, term, gutter, width, verbose):
  versions = ['2.6', '2.7', '3.6', '3.7', '3.8']
  frmt = "(%b %Y)"
  parallel = ['mpi4py', 'mpich', 'intel_openmp', 'dask', 'joblib', 'tbb']
  gpu      = ['cudatoolkit', 'cudnn', 'cupy', 'numba', 'jax']
  green    = ['fenics', 'geopandas', 'tensorflow', 'tensorflow_gpu', 'ipython', \
              'torch', 'pystan', 'jupyter', 'jupyterlab', 'deepmd-kit', 'yt']
  red      = parallel + gpu

  printed_divider = False
  print_single = False

  # conda environments
  path = f"/home/{netid}/.conda"
  if isdir(path):
    if utils.is_rx(path):
      path = f"/home/{netid}/.conda/envs"
      if isdir(path):
        if utils.is_rx(path):
          envs = os.listdir(path)
          if '.conda_envs_dir_test' in envs: envs.remove('.conda_envs_dir_test')
          for env in envs:
            success_per_env = False
            for version in versions:
              path = f"/home/{netid}/.conda/envs/{env}/lib/python{version}/site-packages"
              r_env = True if isdir(f"/home/{netid}/.conda/envs/{env}/lib/R") else False
              if isdir(path) and utils.is_rx(path) and not r_env:
                success_per_env = True
                if verbose:
                  printed_divider = check_python(printed_divider, term, gutter, width)
                  if print_single and printed_divider: print('-' * width)
                  mtime = datetime.fromtimestamp(os.stat(f"/home/{netid}/.conda/envs/{env}").st_mtime)
                  mtime = mtime.strftime(frmt)
                  print(f"     ~/.conda/envs/{term.bold}{env}{term.normal}/lib/python"
                        f"{version}/site-packages {mtime}")
                  pkgs = os.listdir(path)
                  pkgs = [pkg for pkg in pkgs if isdir(os.path.join(path, pkg))]
                  pkgs = clean_python_packages(pkgs)
                  utils.print_packages(term, gutter, width, pkgs, red, green)
                  print_single = True
                else:
                  printed_divider = check_python(printed_divider, term, gutter, width)
                  print(f"{gutter}~/.conda/envs/{term.bold}{env}{term.normal}")
                  print_single = True
            if not success_per_env and not r_env:
              printed_divider = check_python(printed_divider, term, gutter, width)
              print(f"{gutter}~/.conda/envs/{env}: exists")
        else:
          printed_divider = check_python(printed_divider, term, gutter, width)
          print(f"{gutter}~/.conda/envs: private")
    else:
      printed_divider = check_python(printed_divider, term, gutter, width)
      print(f"{gutter}~/.conda: private")

  # .local (pip install --user <package>)
  path = f"/home/{netid}/.local"
  if isdir(path) and utils.is_rx(path):
    for version in versions:
      path = f"/home/{netid}/.local/lib/python{version}/site-packages"
      if isdir(path):
        if utils.is_rx(path):
          printed_divider = check_python(printed_divider, term, gutter, width)
          if verbose:
            if print_single and printed_divider: print('-' * width)
            print(f"     ~/.local/lib/{term.bold}python{version}{term.normal}/site-packages")
            pkgs = os.listdir(path)
            pkgs = [pkg for pkg in pkgs if isdir(path + '/' + pkg)]
            pkgs = clean_python_packages(pkgs)
            utils.print_packages(term, gutter, width, pkgs, red, green)
            print_single = True
          else:
            print(f"{gutter}~/.local/lib/{term.bold}python{version}{term.normal}/site-packages")
            print_single = True
        else:
          printed_divider = check_python(printed_divider, term, gutter, width)
          if print_single and printed_divider and verbose: print('-' * width)
          print(f"{gutter}~/.local/lib/{term.bold}python{version}{term.normal}/site-packages (private)")
          print_single = True

  # .local does not exist
  dot_local = True if not isdir(f"/home/{netid}/.local") else False

  path = f"/home/{netid}/.condarc"
  condarc = True if os.path.isfile(path) else False

  # .cache
  path = f"/home/{netid}/.cache"
  dot_cache = True if isdir(path) else False

  pythonpath = evars['pythonpath']
  anaconda = evars['anaconda']
  miniconda = evars['miniconda']

  if dot_local or condarc or pythonpath[0] or anaconda or miniconda:
    printed_divider = check_python(printed_divider, term, gutter, width)
    if print_single and printed_divider: print('-' * width)

    if dot_local: print(f"{gutter}~/.local does not exist")
    if condarc: print(f"{gutter}{term.bold}{term.red}~/.condarc{term.normal}")
    if pythonpath[0]: print(f"{gutter}PYTHONPATH set in ~/{pythonpath[1]}")
    if anaconda: print(f"{gutter}anaconda: yes")
    if miniconda: print(f"{gutter}miniconda: yes")
    #if dot_cache and printed_divider: print(f"{gutter}~/.cache")
