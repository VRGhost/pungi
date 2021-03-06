#!/usr/bin/python -tt
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import hashlib
import logging
import os
import select
import shutil
import subprocess
import sys
import tempfile

def _doRunCommand(command, logger, rundir=None, output=None, env=None):
    """Run a command and log the output.  Error out if we get something on stderr"""

    logger.info("doRunCommand: Running %s" % subprocess.list2cmdline(command))

    if not rundir:
        rundir = tempfile.gettempdir()

    if not os.path.isdir(rundir):
        raise OSError("No %r directory" % rundir)

    proc = subprocess.Popen(
        command, cwd=rundir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, env=env
    )

    stdout_dict = {
        "fobj": proc.stdout,
        "data": "",
    }
    stderr_dict = {
        "fobj": proc.stderr,
        "data": "",
    }

    streams = {
        proc.stdout.fileno(): stdout_dict,
        proc.stderr.fileno(): stderr_dict,
    }

    poll = select.poll()
    activeStreams = 0
    for data in streams.values():
        poll.register(data["fobj"], select.POLLIN | select.POLLHUP)
        activeStreams += 1

    while activeStreams > 0:
        for (fd, event) in poll.poll():
            data = streams[fd]

            if event & select.POLLIN:
                line = data["fobj"].readline()
                data["data"] += line
                logger.info("doRunCommand: " + line.rstrip())

            if event & select.POLLHUP:
                poll.unregister(fd)
                activeStreams -= 1
    proc.wait()

    if output:
        output.write(stdout_dict["data"])

    if proc.returncode != 0:
        logger.error("doRunCommand: Got an error from %s" % command[0])
        raise OSError("Got an error (%r) from %s: %s" % (
            proc.returncode, command[0], stderr_dict["data"]
        ))
    else:
        logger.debug("doRunCommand: Execution of %r comleted successfully." % command[0])

def _link(local, target, logger, force=False):
    """Simple function to link or copy a package, removing target optionally."""

    if os.path.exists(target) and force:
        os.remove(target)

    try:
        os.link(local, target)
    except OSError, e:
        if e.errno != 18: # EXDEV
            logger.error('Got an error linking from cache: %s' % e)
            raise OSError, e

        # Can't hardlink cross file systems
        shutil.copy2(local, target)

def _ensuredir(target, logger, force=False, clean=False):
    """Ensure that a directory exists, if it already exists, only continue
    if force is set."""

    # We have to check existance of a logger, as setting the logger could
    # itself cause an issue.
    def whoops(func, path, exc_info):
        message = 'Could not remove %s' % path
        if logger:
            logger.error(message)
        else:
            sys.stderr(message)
        sys.exit(1)

    if os.path.exists(target) and not os.path.isdir(target):
        message = '%s exists but is not a directory.' % target
        if logger:
            logger.error(message)
        else:
            sys.stderr(message)
        sys.exit(1)

    if not os.path.isdir(target):
        os.makedirs(target)
    elif force and clean:
        shutil.rmtree(target, onerror=whoops)
        os.makedirs(target)
    elif force:
        return
    else:
        message = 'Directory %s already exists.  Use --force to overwrite.' % target
        if logger:
            logger.error(message)
        else:
            sys.stderr(message)
        sys.exit(1)

def _doCheckSum(path, hash, logger):
    """Generate a checksum hash from a provided path.
    Return a string of type:hash"""

    # Try to figure out what hash we want to do
    try:
        sum = hashlib.new(hash)
    except ValueError:
        logger.error("Invalid hash type: %s" % hash)
        return False

    # Try to open the file, using binary flag.
    try:
        myfile = open(path, 'rb')
    except IOError, e:
        logger.error("Could not open file %s: %s" % (path, e))
        return False

    # Loop through the file reading chunks at a time as to not
    # put the entire file in memory.  That would suck for DVDs
    while True:
        chunk = myfile.read(8192) # magic number!  Taking suggestions for better blocksize
        if not chunk:
            break # we're done with the file
        sum.update(chunk)
    myfile.close()

    return '%s:%s' % (hash, sum.hexdigest())
