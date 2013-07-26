fuserun
=======

A simple fuse "filesystem" that lets you treat program executions as files


One of my favorite bash-isms is "process substitution", where you can treat the output of programs as files, such as
```
diff <(curl server1/) cached_copy.txt
```

Unfortunately, this only works when you're working on the shell, and I've sometimes found myself wanting a solution that works for other contexts.  One particularly interesting case is using this kind of substitution to write out custom configuration files for different machines: instead of having a system that seeds each machine with its own config file, just put the same config-generator on all the machines.

This is a simple fuse filesystem that interprets paths as commands, where the contents of the "file" are the stdout, and writing to the "file" writes to stderr:
> $ python fuserun.py /mnt/fuserun &
> $ cat '/tmp/fuserun/ls /home$'
> kmod
> $ fusermount -u /mnt/fuserun

Note: due to a technical limitation, currently you must end all paths with a dollar sign to signal that it is the end of the path.

Warning
-------
This is a proof-of-concept implementation that is entirely unsuitable for real-world use.  I didn't worry about security or long-term performance, so this is provided only as an example and you use it at your own risk.
