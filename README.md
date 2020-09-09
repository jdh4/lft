# lft is looking for trouble

This command crawls the /home directory of a specified user and reports on their configuration and jobs.

- it can find the true netid when given an alias (thanks to R. Knight)
- identifies MATLAB users

## Installation

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

On Traverse:

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
