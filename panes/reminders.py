import os
import csv
import subprocess
from subprocess import PIPE as sPIPE
from datetime import datetime

##############
## downtime ##
##############
def second_tues_of_month(year, month):
  """Return a date object for the second Tuesday of the current month."""
  import calendar
  c = calendar.Calendar(firstweekday=calendar.SUNDAY)
  monthcal = c.monthdatescalendar(year, month)
  all_tues_of_month = [day for week in monthcal for day in week if \
                       day.weekday() == calendar.TUESDAY and \
                       day.month == month]
  second_tues = all_tues_of_month[1]
  return second_tues

def previous_and_next_downtime_dates(term, gutter, verbose):
  """Display days from/to the previous/next downtime when close."""
  today = datetime.today().date()
  year = today.year
  month = today.month

  second_tues = second_tues_of_month(year, month)
  dt = today - second_tues

  fmt = '%b %-d'
  if dt.days >= 0:
    # downtime in current month is lower bound so get downtime next month
    month += 1
    month, year = (1, year + 1) if month == 13 else (month, year)
    previous_tues = second_tues
    upcoming_tues = second_tues_of_month(year, month)
  else:
    # downtime in current month is upper bound so get downtime previous month
    month -= 1
    month, year = (12, year - 1) if month == 0 else (month, year)
    previous_tues = second_tues_of_month(year, month)
    upcoming_tues = second_tues

  dt_previous = today - previous_tues
  dt_upcoming = upcoming_tues - today
  previous_tues = previous_tues.strftime(fmt)
  upcoming_tues = upcoming_tues.strftime(fmt)

  # format previous downtime
  clr = f"{term.bold}{term.red}" if dt_previous.days <= 3 else ""
  if dt_previous.days == 0:
    prv = f"{previous_tues} ({clr}today{term.normal})"
  elif dt_previous.days == 1:
    prv = f"{previous_tues} ({clr}yesterday{term.normal})"
  else:
    prv = f"{previous_tues} ({clr}{dt_previous.days} days ago{term.normal})"

  # format upcoming downtime
  clr = f"{term.bold}{term.red}" if dt_upcoming.days <= 7 else ""
  if dt_upcoming.days == 0:
    nxt = f"({clr}today{term.normal}) {upcoming_tues}"
  elif dt_upcoming.days == 1:
    nxt = f"({clr}tomorrow{term.normal}) {upcoming_tues}"
  else:
    nxt = f"({clr}{dt_upcoming.days} days ahead{term.normal}) {upcoming_tues}"

  if (dt_previous.days <= 5 or dt_upcoming.days <= 9 or verbose):
    return f"{gutter}{prv} --- Downtime --> {nxt}"
  else:
    return None

########################
## slurm reservations ##
########################
def get_reservations(term, gutter, days_away=7):
  """Return a list of upcoming Slurm reservations to be printed."""
  cmd = "scontrol show reservation"
  output = subprocess.run(cmd, stdout=sPIPE, shell=True, timeout=3, text=True)
  lines = output.stdout.split('\n')
  res = []
  for line in lines:
    # ReservationName=hpcr StartTime=2020-11-10T16:30:00 ...
    if 'ReservationName=' in line and 'StartTime=' in line:
      items = line.split()
      if 'ReservationName=' in items[0]:
        name = items[0].split("=")[1]
        if 'StartTime=' in items[1]:
          stime = items[1].split("=")[1]
          when = datetime.strptime(stime, "%Y-%m-%dT%H:%M:%S").date()
          today = datetime.today().date()
          dt = when - today
          if (0 <= dt.days <= days_away):
            if (dt.days == 0):
              res.append(f"{gutter}Reservation \"{name}\" is {term.bold}{term.red}today{term.normal}")
            elif (dt.days == 1):
              res.append(f"{gutter}Reservation \"{name}\" is {term.bold}{term.red}tomorrow{term.normal}")
            else:
              res.append(f"{gutter}Reservation \"{name}\" in {dt.days} days on {stime}")
  return res

############################
## workshops and holidays ##
############################
def get_reminders(term, gutter, flnm, host, days_away=7):
  """Return a list of upcoming events to be printed."""
  flnm = "/home/jdh4/bin/remind/" + flnm
  reminders = []
  if os.path.isfile(flnm):
    with open(flnm, mode='r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      result = sorted(csv_reader, key=lambda d: d["date"])
      for row in result:
        event = row["event"]
        when = datetime.strptime(row["date"], "%m/%d/%Y").date()
        today = datetime.today().date()
        dt = when - today
        if (0 <= dt.days <= days_away):
          if (dt.days == 0):
            reminders.append(f"{gutter}{event} is {term.bold}{term.red}today{term.normal}")
          elif (dt.days == 1):
            reminders.append(f"{gutter}{event} is {term.bold}{term.red}tomorrow{term.normal}")
          else:
            when = when.strftime("%A, %b %-d")
            reminders.append(f"{gutter}{event} in {dt.days} days on {when}")
  else:
    reminders.append(f"Warning: {flnm} not found")
  return reminders
