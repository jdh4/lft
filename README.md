# lft is looking for trouble

For a given NetID, `lft` will crawl the `/home` directory of the user and run multiple commands before generating a color-coded report that highlights potential problems with the user's shell configuration files, software installations and jobs.

## How to use it?

Add this line to your `~/.bashrc` file on each cluster (Adroit, Della, Perseus, Tiger, Tigressdata and Traverse):

```bash
alias lft='/home/jdh4/bin/lft'
```

Then look at the help menu:

```
$ lft -h

lft is looking for trouble. Example usage:
     $ lft aturing

Options:
     -v  Verbose output (show packages and more jobs)
     -s  Show sponsor
     -d  Compute the size of /home using du -sh
     -h  Show this help menu
```

## Example

![lft_example](https://tigress-web.princeton.edu/~jdh4/lft_example_report.png?123456)

## What exactly does it do?

`lft` does the following:

#### about the user
+ runs `ldapsearch` to get the full name, department and position of the user (this takes 1-2 seconds which explains why `lft` seems to hang at the start).
+ converts an email alias to the netid of the user (e.g., `halverson` is converted to `jdh4`).
+ displays the groups of the user.
+ shows when the user was last active as determined by the modification time of `/home`.
+ optionally runs `sponsor_report` to show the user's sponsor (e.g., `lft aturing -s`).
+ displays the user's login shell if not `/bin/bash` (e.g., `/bin/zsh`, `/bin/tcsh`).

#### home directories
+ shows all the clusters where the user has a `/home` directory (this information is updated every 2 hours M-F from 7:30 am to 5:30 pm).
+ shows which top-level directories are world-readable (`/home`, `/tigress`, `/scratch/gpfs`) and the number of items in each.

#### .bashrc and .bash_profile
+ scans `.bashrc` and `.bash_profile` looking for the loading of environment modules and the setting of important environment variables (`PYTHONPATH`, `R_LIBS`, `R_LIBS_USER`) while reporting the state of each startup script as either `skeleton` or `custom`.

#### Python
+ lists Conda environments in `~/.conda/envs` as well as the packages (if `-v` option) with color coding.
+ looks for a `.condarc` file and follow the `conda_envs` path to Conda environments.
+ lists Python packages found in `~/.local/lib/pythonX.Y/site-packages`.
+ reports key libraries such as `cudnn`, `mpich` (upcoming feature).
+ reports on custom installations of Anaconda or Miniconda.
+ shows when OnDemand Jupyter was last used.

#### R
+ lists existence of R libraries and packages found in `~/R/x86_64-redhat-linux-gnu-library/X.Y` as well as Conda environments in `~/.conda/envs` (packages are printed with color coding to highlight parallel packages).
+ reports the existence of `~/.R/Makevars` and `LOCK` files.
+ shows when OnDemand RStudio was last used.

#### MATLAB
+ shows which MATLAB environment modules the user loaded and when OnDemand MATLAB was last used.

#### Stata
+ shows which Stata versions the user has used and when OnDemand Stata was last used.

#### Julia
+ lists Julia packages found in `~/.julia/packages` with color coding.

#### Jobs
+ shows the user's fairshare value, 30-day group usage, group share of the cluster and number of running and queued jobs.
+ shows most recent jobs according to `sacct` including an `MT` column report which reports the memory efficiency (M) and the time efficiency (T) where both of the these independent quantities are scaled to be between 0 and 9 (time efficiency is the elapsed time of the job divided by the runtime limit).
+ shows `F`, `TO`, `OOM` and `NF` job states in red.
+ identifies OnDemand jobs and replace the job name with either `O-JUPYTER`, `O-RSTUDIO`, `O-MATLAB` or `O-STATA` instead of, e.g., `sys/dashboard/sys/jupyter`.

#### Reminders
+ shows the previous and upcoming downtime, RC workshops, reservations on Adroit and all university holidays.
