# lft is looking for trouble

`lft` is a Python code that tries to identify problems with the a user's startup scripts, software installations and jobs. It generates information by crawling the  user's `/home` directory and running numerous commands.

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

## What does it do?

`lft` runs multiple commands such as ldapsearch, groups, sponsor_report, sshare, sacct, squeue, scontrol show reservation. It also crawls the user's `/home` directory in identifying installed software and potential problems with it.

`lft' will:

+ identify an email alias and automatically use the netid.
+ show all the clusters where the user has a /home directory. This information is updated every 2 hours M-F from 8 AM to 6 PM.
+ scan `.bashrc` and `.bash_profile` files looking for the loading of environment modules. It also identifies when certain enivronment variables are set such as `PYTHONPATH`, `R_LIBS`, `R_LIBS_USER`.
+ It checks for the use of miniconda or Anaconda.
+ If it find a .condarc file it will attempt to follow the conda_envs path to obtain information about Conda environments.
+ Identify OnDemand jobs and replace the job name with either `O-JUPYTER`, `O-RSTUDIO`, `O-MATLAB` or `O-STATA`.
+ show when last active as determine by the modification time of `/home`
+ show which filesystems are world-readable (`/home`, `/tigress`, `/scratch/gpfs`)
+ list Conda environments in `~/.conda/envs` as well as the packages (with `-v` option for verbose output)
+ list Python packages found in `~/.local`
+ list R packages found in `~/R/`
+ parallel R packages and problematic packages are color coded
+ list R packages found in Conda environemnts
+ list Julia packages found in `~/.julia/packages` (with `-v` option for verbose output)
+ show which MATLAB modules the user has used and when they last used OnDemand MATLAB
+ show which Stata modules the user has used and when they last used OnDemand Stata
+ show the user's fairshare value, 30-day group usage and group share of the cluster
+ compute the memory and time efficiency of each job. The `MT` column report the memory efficiency (M) and the time efficiency (T) which is the elapsed time of the job divided by the allocated time. Both of the these quantities are scaled to be between 0 and 9.
+ show the job state's of F, TO and OOM is red.
+ show the previous and upcoming downtime, RC workshops, reservations on Adroit for RC workshops and all university holidays

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
