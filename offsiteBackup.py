#!/usr/bin/python

# Offsite backup script.
#
# This script is intended to replicate a given folder into a remote location.
# The replication is meant to serve as an offsite backup. This is, data flows
# only from the source to the destination. Deleted files in the source are removed
# from the destination as well

import os
import subprocess
import sys

#####################################
#Script configuration. Modify as required
#####################################

# Server (ip address or hostname) where the backups shall be stored
BACKUP_SERVER="X.X.X.X" 

# Username used to connect to the server
BACKUP_SERVER_USERNAME="XXXXX"

# Root (path in the remote server) where the backups shall be stored
BACKUP_REMOTE_PATH="/home/XXXXX/backups/"

# Local directory that shall be backed up
SAVED_DIRECTORY = "/tmp/"

# Local path where the ssh key for connecting to the server without password shall be stored
LOCAL_KEYFILE = "/home/XXXXX/.offsiteBackup.key"

#####################################
#Sanity checks
#####################################
assert(BACKUP_REMOTE_PATH[-1:] == "/")
assert(BACKUP_SERVER_USERNAME != "root")
assert(SAVED_DIRECTORY[-1:] == "/")

def runRemoteCommand(RemoteCommand, stdoutFd = None):
    """
    Run the given command in the remote server. The standard output can be optionally captured.
    """
    print "Running remote command : " + RemoteCommand
    if stdoutFd == None:
        code = subprocess.call(["ssh", "-i", LOCAL_KEYFILE, BACKUP_SERVER_USERNAME + "@" + BACKUP_SERVER, RemoteCommand])
    else:
        code = subprocess.call(["ssh", "-i", LOCAL_KEYFILE, BACKUP_SERVER_USERNAME + "@" + BACKUP_SERVER, RemoteCommand], stdout = stdoutFd)
    return code
    
def showHelp():
    """
    Display the script help
    """
    print "call with " + sys.argv[0] + " [command]"
    print " "
    print " Available commands: "
    print "  help : Show this help"
    print "  update : Run the routine backup"
    print "  init : Create ssh keys and set up everything"
    print " "

def doInit():
    """
    Initialize the remote server to allow backups to be stored
    """

    if os.path.isfile(LOCAL_KEYFILE):
        print "Local keyfile " + LOCAL_KEYFILE + " already exists. Please remove it manually"
        return

    print "Generating new ssh key under " + LOCAL_KEYFILE
    print "Make sure the passphrase is empty"
    os.system("ssh-keygen -f " + LOCAL_KEYFILE)

    os.system("ssh-copy-id -i " + LOCAL_KEYFILE + " " + BACKUP_SERVER_USERNAME + "@" + BACKUP_SERVER)
    
def doUpdate():
    """
    Syncrhonize the local folder with the remote server
    """
    #Synchronize the local directories into the current directory in the remote server
    destDirName = BACKUP_REMOTE_PATH

    cdirname = os.path.basename(os.path.dirname(SAVED_DIRECTORY)) + "/"
    destdir = os.path.join(destDirName, cdirname)
    command = "rsync -a -v -e -H -z 'ssh -i " + LOCAL_KEYFILE + "' --delete " + SAVED_DIRECTORY + " " + BACKUP_SERVER_USERNAME + "@" + BACKUP_SERVER + ":" + destdir

    print "running rsync " + command
    subprocess.call([command], shell = True)


def isHostUp():
    """
    Returns True if the given host is up. False otherwise
    """
    
    res = os.system("ping -c 1 " + BACKUP_SERVER + " > /dev/null")
    if res == 0:
        out = True
    else:
        out = False
        
    return out

########################################
# Main program
########################################
arg = "help"
if len(sys.argv) > 1:
    arg = sys.argv[1]

if arg == "help":
    showHelp()
    sys.exit(0)
    
elif arg == "init":
    up = isHostUp()
    if up:
        doInit()
    else:
        sys.exit(1)
    sys.exit(0)
    
elif arg == "update":
    up = isHostUp()
    if up:
        doUpdate()
    else:
        sys.stderr.write("Backup server is down" + '\n')
        sys.exit(1)
    sys.exit(0)
    
else:
    showHelp()
    sys.exit(0)


