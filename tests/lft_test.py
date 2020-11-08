import sys
sys.path.append("../")
sys.path.append("/scratch/gpfs/jdh4/terminal-env/lib/python3.8/site-packages")
from panes import utils
from panes import sponsor as sp
from panes import startup_scripts as ss
from panes import jobs
from panes import reminders as rm
from datetime import datetime

def test_name():
  name = "Allen M. Turing"
  assert "Allen Turing" == utils.remove_middle_initial(name)

def test_hostname_translation():
  hostname = "adroit4"
  assert utils.known_hosts[hostname] == "adroit"

def test_is_rx():
  assert (utils.is_rx("/home"), utils.is_rx("/root")) == (True, False)

def test_sponsor():
  assert sp.get_sponsor("slala") == ("Niraj Jha", "jha")

def test_modules():
  lines = ["module load intel",
           "module load intel-mpi cudatoolkit/11.1",
           "module add cmake"]
  assert ss.format_modules(lines) == ["module load intel",
                                      "module load intel-mpi",
                                      "module load cudatoolkit/11.1",
                                      "module load cmake"]

def test_cmt():
  assert jobs.cmt_efficiency("1200", "42", "30G/N", "3", "4", 100e6) == "94"

def test_timeformat():
  elap = "2-23:52:33"
  assert jobs.format_elapsed_time(elap) == str(round(2*24 + 23 + 52/60 + 33/3600)) + "h"

def test_2nd_tues():
  assert rm.second_tues_of_month(2021, 11) == datetime(2021, 11, 9).date()
