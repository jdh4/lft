# lft is looking for trouble

This command crawls the /home directory of a specified user and reports on their configuration and jobs.

- it can find the true netid when given an alias (thanks to R. Knight)
- identifies MATLAB users

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
