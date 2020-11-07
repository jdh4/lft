# lft is looking for trouble

`lft` is a Python code that tries to identify problems with the a user's startup scripts, software installations and jobs. It generates information by crawling the  user's `/home` directory and running numerous commands.

`lft` runs multiple commands such as ldapsearch, groups, sponsor_report, sshare, sacct, squeue, scontrol show reservation. It also crawls the user's `/home` directory in identifying installed software and potential problems with it.

## How to use

Add this line to your `~/.bashrc` file on each cluster (Adroit, Della, Perseus, Tiger, Tigressdata and Traverse):

```bash
alias lft='/home/jdh4/bin/lft'
```

To get started look at the help menu:

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

## What exactly does it do?

`lft` will:

+ run `ldapsearch` to get the full name, department and position of the user (his call takes 1-2 seconds which explains why `lft` seems to hang at the start).
+ convert an email alias to the netid of the user (e.g., `halverson` is converted to `jdh4`).
+ run `groups` and display the groups of the user.
+ show when user was last active as determined by the modification time of `/home`.
+ optionally run `sponsor_report` to show the user's sponsor (e.g., `lft aturing -s`).
+ display the user's login shell if not `/bin/bash` (e.g., `/bin/zsh`, `/bin/tcsh`).
+ show all the clusters where the user has a `/home` directory (this information is updated every 2 hours M-F from 8 AM to 6 PM).
+ scan `.bashrc` and `.bash_profile` looking for the loading of environment modules and the setting of important environment modules (`PYTHONPATH`, `R_LIBS`, `R_LIBS_USER`) while reporting the state of each startup script as either `default` or `custom`.
+ show which top-level directories are world-readable (`/home`, `/tigress`, `/scratch/gpfs`) and the number of items in each.
+ list Conda environments in `~/.conda/envs` as well as the packages (if `-v` option) with color coding.
+ look for a `.condarc` file and follow the `conda_envs` path to Conda environments.
+ list Python packages found in `~/.local/lib/pythonX.Y/site-packages`.
+ report on custom installations of Anaconda or Miniconda.
+ show when OnDemand Jupyter, RStudio, MATLAB or Stata was last used.
+ list existence of R libraries and packages found in `~/R/x86_64-redhat-linux-gnu-library/X.Y` as well as Conda environments in `~/.conda/envs` (packages are printed with color coding to highlight parallel packages).
+ list R `LOCK` files.
+ show when OnDemand RStudio was last used.
+ list Julia packages found in `~/.julia/packages` with color coding.
+ show which MATLAB environment modules the user loaded and when OnDemand MATLAB was last used.
+ show which Stata versions the user has used and when OnDemand Stata was last used.
+ show the user's fairshare value, 30-day group usage, group share of the cluster and number of running and queued jobs.
+ show most recent jobs according to `sacct` including an `MT` column report which reports the memory efficiency (M) and the time efficiency (T) where both of the these independent quantities are scaled to be between 0 and 9 (time efficiency is the elapsed time of the job divided by the runtime limit).
+ show the job state's of F, TO, OOM, NF in red.
+ identify OnDemand jobs and replace the job name with either `O-JUPYTER`, `O-RSTUDIO`, `O-MATLAB` or `O-STATA` instead of, e.g., `sys/dashboard/sys/jupyter`.
+ show the previous and upcoming downtime, RC workshops, reservations on Adroit and all university holidays.

## Notes for jdh4

Add these lines to .condarc:

```
envs_dirs:
 - /scratch/gpfs/jdh4
```

Then run these commands:

```
$ module load anaconda3
$ conda create --name terminal-env --channel conda-forge blessed -y
```

Or on Traverse:

```
$ module load anaconda3
$ conda create --name terminal-env python=3.8
$ conda activate terminal-env
$ pip install blessed
```

Too many people have default .bashrc files these commands demonstrate:

```
# $ find /home -maxdepth 2 -name .bashrc -type f -exec diff -q /home/csimao/.bashrc {} \; 2>/dev/null | wc -l
# 435
# $ find /home -maxdepth 2 -name .bashrc -type f 2>/dev/null | wc -l
# 930
# $ ls -ld /home/* | wc -l
# 957
# $ find /home -maxdepth 2 -name .bashrc -type f -exec diff -q /home/jdh4/.bashrc {} \; 2>/dev/null | wc -l
# 929
```

Default .bashrc files are different on tiger versus perseus:

```
5c5
<         . /etc/bashrc
---
> 	. /etc/bashrc
```
