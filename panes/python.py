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

# TODO: nobel, anaconda lib (mpich)

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

def condarc_path(netid):
  # this function extracts the path like below  
  # envs_dirs:
  # - /scratch/gpfs/jdh4/CONDA/envs

  path = f"/home/{netid}/.condarc"
  if os.path.isfile(path) and utils.is_r(path):
    with open(path, "r") as f:
      lines = f.readlines()
    for i, line in enumerate(lines):
      if "envs_dirs:" in line:
        return lines[i + 1].replace("-", "").strip()
  return None

def get_libs(path):
  libs = os.listdir(path)
  for lib in libs:
    if "libmpich.so" in lib:
      return ["libmpich.so"]
  return []

def python_packages(netid, evars, term, gutter, width, verbose):
  versions = ['2.6', '2.7', '3.6', '3.7', '3.8', '3.9']
  frmt = "(%b %Y)"
  parallel = ['mpi4py', 'libmpich.so', 'intel_openmp', 'dask', 'joblib', 'tbb']
  gpu      = ['cudatoolkit', 'cudnn', 'cupy', 'numba', 'jax']
  green    = ['fenics', 'geopandas', 'tensorflow', 'tensorflow_gpu', 'ipython', \
              'torch', 'pystan', 'jupyter', 'jupyterlab', 'deepmd-kit', 'yt', \
              'cobaya']
  red      = parallel + gpu

  printed_divider = False
  print_single = False

  paths = [f"/home/{netid}/.conda"]
  paths_envs = [f"/home/{netid}/.conda/envs"]

  condarc_envs_path = condarc_path(netid)
  if condarc_envs_path:
    x = "/".join(condarc_envs_path.split("/")[:-1])
    paths.append(x)
    paths_envs.append(condarc_envs_path)

  # conda environments
  for i, path in enumerate(paths):
    if isdir(path):
      if utils.is_rx(path):
        pe = paths_envs[i]
        if isdir(pe):
          if utils.is_rx(pe):
            envs = os.listdir(pe)
            if '.conda_envs_dir_test' in envs: envs.remove('.conda_envs_dir_test')
            for env in envs:
              success_per_env = False
              for version in versions:
                path_site = f"{pe}/{env}/lib/python{version}/site-packages"
                r_env = True if isdir(f"{pe}/{env}/lib/R") else False
                if isdir(path_site) and utils.is_rx(path_site) and not r_env:
                  success_per_env = True
                  if verbose:
                    printed_divider = check_python(printed_divider, term, gutter, width)
                    if print_single and printed_divider: print('-' * width)
                    mtime = datetime.fromtimestamp(os.stat(f"{pe}/{env}").st_mtime)
                    mtime = mtime.strftime(frmt)
                    print(f"     {pe}/{term.bold}{env}{term.normal}/lib/python"
                          f"{version}/site-packages {mtime}")
                    pkgs = os.listdir(path_site)
                    pkgs = [pkg for pkg in pkgs if isdir(os.path.join(path_site, pkg))]
                    libs = get_libs(f"{pe}/{env}/lib")
                    pkgs = clean_python_packages(pkgs + libs)
                    utils.print_packages(term, gutter, width, pkgs, red, green, max_chars=13)
                    print_single = True
                  else:
                    printed_divider = check_python(printed_divider, term, gutter, width)
                    print(f"{gutter}{pe}/{term.bold}{env}{term.normal} (v{version})")
                    print_single = True
              if not success_per_env and not r_env:
                printed_divider = check_python(printed_divider, term, gutter, width)
                print(f"{gutter}{pe}/{env}: exists")
          else:
            printed_divider = check_python(printed_divider, term, gutter, width)
            print(f"{gutter}{pe}: private")
      else:
        printed_divider = check_python(printed_divider, term, gutter, width)
        print(f"{gutter}{path}: private")

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
            utils.print_packages(term, gutter, width, pkgs, red, green, max_chars=13)
            print_single = True
          else:
            print(f"{gutter}~/.local/lib/{term.bold}python{version}{term.normal}/site-packages")
            print_single = True
        else:
          printed_divider = check_python(printed_divider, term, gutter, width)
          if print_single and printed_divider and verbose: print('-' * width)
          print(f"{gutter}~/.local/lib/{term.bold}python{version}{term.normal}/site-packages (private)")
          print_single = True

  # .local does not exist or is private
  path = f"/home/{netid}/.local"
  dot_local_exists = True if isdir(path) else False
  dot_local_private = False # TODO rewrite
  if dot_local_exists:
    dot_local_private = True if not utils.is_rx(path) else False

  path = f"/home/{netid}/.condarc"
  condarc = True if os.path.isfile(path) else False

  # .cache
  path = f"/home/{netid}/.cache"
  dot_cache = True if isdir(path) else False
  # TODO /home/jdh4/.cache/pip/wheels

  pythonpath = evars['pythonpath']
  anaconda = evars['anaconda']
  miniconda = evars['miniconda']

  opath = f"/home/{netid}/ondemand/data/sys/dashboard/batch_connect/sys/jupyter/output"
  ondemand = isdir(opath)

  if condarc or pythonpath[0] or anaconda or miniconda or ondemand:
    printed_divider = check_python(printed_divider, term, gutter, width)
    if print_single and printed_divider: print('-' * width)

    if not dot_local_exists:
      print(f"{gutter}~/.local (does not exist)")
    elif dot_local_private:
      print(f"{gutter}~/.local (private)")
    if condarc: print(f"{gutter}{term.bold}{term.red}~/.condarc{term.normal}")
    if pythonpath[0]: print(f"{gutter}PYTHONPATH set in ~/{pythonpath[1]}")
    if anaconda: print(f"{gutter}Anaconda: yes")
    if miniconda: print(f"{gutter}Miniconda: yes")
    #if dot_cache and printed_divider: print(f"{gutter}~/.cache")
    if ondemand: utils.ondemand_last_used("Jupyter", opath, gutter)
