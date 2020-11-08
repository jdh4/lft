import os
from os.path import isdir
from panes import utils

class StringBox(list):
  def __init__(self):
    super().__init__()
    self.width = 0
    self.height = 0
  def append(self, x):
    super().append(x)
    self.width = len(x) if len(x) > self.width else self.width
    self.height += 1
  def __setitem__(self, key, x):
    super().__setitem__(key, x)
    self.width = len(x) if len(x) > self.width else self.width

#################
## filesystems ##
#################
def filesystems(term, gutter, host, netid, width, spon, home_exists, home_rx):

  fs = StringBox()
  if host != "tigressdata":

    path = '/scratch/gpfs/' + netid
    if isdir(path):
      fs.append(utils.public_or_private(path))

    path = '/tigress/' + netid
    if isdir(path):
      fs.append(utils.public_or_private(path))

    if ('della' in host or 'adroit' in host):
      path = '/scratch/network/' + netid
      if isdir(path):
        fs.append(utils.public_or_private(path))

  # align filesystems on colon
  def align_on_colon(s):
    max_idx = max([line.index(':') for line in s])
    for i in range(fs.height):
      fs[i] = " " * (max_idx - fs[i].index(':')) + fs[i]
    return fs

  if fs: fs = align_on_colon(fs)
  if not home_exists or not home_rx: print("\n" * (fs.height - 1))

  # print filesystems
  with term.location():
    if len(fs):
      if spon:
        print(term.move_xy(width - fs.width - len(gutter), 12) + term.bold('Filesystems'))
      else:
        print(term.move_xy(width - fs.width - len(gutter), 11) + term.bold('Filesystems'))
      for i in range(fs.height):
        xc = width - fs.width - len(gutter)
        yc = 14 + i if spon else 13 + i
        if 'home' in fs[i]:
          print(term.move_xy(xc, yc) + term.red + term.bold + fs[i] + term.normal)
        else:
          print(term.move_xy(xc, yc) + fs[i])
