#!/usr/bin/python

import llfuse

import sys
import time
import stat
import os
import errno
import commands
import subprocess

class RunFS(llfuse.Operations):
    def __init__(self):
        super(RunFS, self).__init__()
        self.inodes = {}
        self.parents = {}
        self.fhs = {}
        self.next_inode = 2
        self.next_fh = 0

    def lookup(self, inode_p, name):
        print "lookup(%s, %s)" % (inode_p, name)
        inode = self.next_inode
        self.next_inode += 1
        self.inodes[inode] = name
        self.parents[inode] = inode_p
        return self.getattr(inode)

    def getattr(self, inode):
        print "getattr(%s)" % inode
        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = 300
        entry.attr_timeout= 300
        if inode == 1 or not self.inodes[inode].endswith("$"):
            entry.st_mode = stat.S_IFDIR
        else:
            entry.st_mode = stat.S_IFREG
        entry.st_nlink = 1

        entry.st_uid = 0
        entry.st_gid = 0
        entry.st_rdev = 0
        entry.st_size = 1024**2

        entry.st_blksize = 512
        entry.st_blocks = 1
        entry.st_atime = 0
        entry.st_ctime = 0
        entry.st_mtime = 0

        return entry

    def opendir(self, inode):
        print "opendir(%s)" % inode
        return stat.ENOTDIR
        raise llfuse.FUSEError(errno.ENOTDIR)
        # return inode

    def readdir(self, inode, off):
        print "readdir(%s, %s)" % (inode, off)
        return []

    def open(self, inode, flags):
        print "open(%s, %s)" % (inode, flags)
        cmd = self.inodes[inode]
        fh = self.next_fh
        self.next_fh += 1

        assert cmd.endswith("$")
        cmd = cmd[:-1]
        while self.parents[inode] != 1:
            inode = self.parents[inode]
            cmd = self.inodes[inode] + "/" + cmd
            print inode, cmd
        p = subprocess.Popen(cmd, shell=True, stdin=open("/dev/null"), stdout=subprocess.PIPE, close_fds=True)
        out, err = p.communicate()
        self.fhs[fh] = out
        return fh

    def read(self, fh, offset, length):
        print "read(%s, %s, %s)" % (fh, offset, length)
        s = self.fhs[fh]
        if offset >= len(s):
            print 'eof'
            raise EOFError()
        print repr(s[offset:offset+length])
        return s[offset:offset+length]

    def release(self, fh):
        print "release(%s)" % fh
        del self.fhs[fh]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit('Usage: %s <mountpoint>' % sys.argv[0])

    mountpoint = sys.argv[1]
    fs = RunFS()

    llfuse.init(fs, mountpoint,
                [  b'fsname=llfuse_xmp', b"nonempty" ])


    os.chdir("/")
    llfuse.main(single=True)
    llfuse.close()
