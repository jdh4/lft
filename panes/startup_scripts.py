import os
from blessed import Terminal

###############################
## .bashrc and .bash_profile ##
###############################
def format_modules(module_lines):
  # convert lines with multiple modules to single lines
  # e.g., module load intel intel-mpi cudatoolkit
  singles = []
  for module_line in module_lines:
    items = module_line.split()
    if len(items) > 1 and items[0] == 'module' and (items[1] == 'load' or items[1] == 'add'):
      for module in module_line.split()[2:]:
        #if module.endswith('/64'): module = module[:module.index('/64')]
        singles.append("module load " + module)
    else:
      singles.append(module_line)
  return singles

def remove_comments_and_white_space(lines):
  remove_comments = [line for line in lines if not line.strip().startswith('#')]
  trans = str.maketrans('', '', ' \n\t\r')
  return ''.join(remove_comments).translate(trans)

def analyze_startup_script(flnm, default, evars, netid):
  aliases = 0
  exports = 0
  modules = []
  path = f"/home/{netid}/{flnm}"
  if os.path.isfile(path):
    with open(path) as f:
      lines = f.readlines()
    startup_rm = remove_comments_and_white_space(lines)
    default_rm = remove_comments_and_white_space(default)
    if (startup_rm == default_rm):
      state = "default"
    else:
      state = "custom"
      for line in lines:
        line = line.strip().lower()
        if line.startswith('#'): continue # ignore comments
        if (line.startswith('module') and ('load' in line or 'add' in line) and \
          not 'alias' in line):
          modules.append(line)
        if ('alias' in line): aliases += 1
        if ('export' in line): exports += 1
        if 'miniconda' in line and 'path' in line:
          evars['miniconda'] = True
        if 'anaconda' in line and 'path' in line:
          evars['anaconda'] = True
        if ('pythonpath' in line):
          evars['pythonpath'] = (True, flnm)
        if 'r_libs' in line and 'export' in line and '_user' not in line:
          evars['rlibs'] = (True, flnm)
        if 'r_libs_user' in line and 'export' in line:
          evars['rlibsuser'] = (True, flnm)
  else:
    state = "missing"
  return (aliases, exports, modules, state, flnm)

def print_with_modules(al, ex, modules, state, flnm, term, gutter, verbose):
  print(f"{gutter}~/{flnm}: {state}")
  if modules:
    mods = format_modules(modules)
    if verbose or len(mods) < 4:
      for mod in mods:
        print(f"{gutter}  {term.bold}{term.red}{mod}{term.normal}")
    else:
      for mod in mods[:3]:
        print(f"{gutter}  {term.bold}{term.red}{mod}{term.normal}")
      print(f"{gutter}  {term.bold}{term.red}(plus {len(mods) - 3} more){term.normal}")
