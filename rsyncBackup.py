#!/usr/bin/python

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

# List of local directories that shall be backed up
SAVED_DIRECTORIES = ["/tmp/"]

# Local path where the ssh key for connecting to the server without password shall be stored
LOCAL_KEYFILE = "/home/XXXXX/.rsyncBackup.key"

# Number of snapsots to be saved remotely
NUM_SNAPSHOTS_TO_SAVE = 10

#####################################
#Sanity checks
#####################################
assert(BACKUP_REMOTE_PATH[-1:] == "/")
assert(BACKUP_SERVER_USERNAME != "root")
assert(NUM_SNAPSHOTS_TO_SAVE > 2)
for cdir in SAVED_DIRECTORIES:
    assert(cdir[-1:] == "/")

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
    Add a new snapshot to the remote server
    """

    #Check the remote directory structure
    #Create the missing directories
    for i in range(0, NUM_SNAPSHOTS_TO_SAVE):
        dirBaseName = "backup."+str(i)
        fullDirName = os.path.join(BACKUP_REMOTE_PATH, dirBaseName)
        command = 'if [ -d ' + fullDirName +' ]; then exit 0; else exit 1; fi'
        code = runRemoteCommand(command)
        if code == 1:
            print "Creating remote directory " + fullDirName
            command = "mkdir " + fullDirName
            code = runRemoteCommand(command)

    #Rotate the remote directories
    fullDirName = os.path.join(BACKUP_REMOTE_PATH, "backup." + str(NUM_SNAPSHOTS_TO_SAVE-1))
    assert(fullDirName not in ("", " ", "/", "~"))
    command = "rm -Rf " + fullDirName
    code = runRemoteCommand(command)
    for i in range(NUM_SNAPSHOTS_TO_SAVE - 1,1,-1):
        dirBaseName1 = "backup."+str(i)
        fullDirName1 = os.path.join(BACKUP_REMOTE_PATH, dirBaseName1)

        dirBaseName2 = "backup."+str(i-1)
        fullDirName2 = os.path.join(BACKUP_REMOTE_PATH, dirBaseName2)

        command = "mv " + fullDirName2 + " " + fullDirName1
        code = runRemoteCommand(command)

    #Copy (hard-link) the previous backup
    destDirName = os.path.join(BACKUP_REMOTE_PATH, "backup.1")
    srcDirName = os.path.join(BACKUP_REMOTE_PATH, "backup.0")
    command = "cp -al " + srcDirName + " " + destDirName
    code = runRemoteCommand(command)

    #Synchronize the local directories into the current directory in the remote server
    destDirName = srcDirName
    for cdir in SAVED_DIRECTORIES:

        cdirname = os.path.basename(os.path.dirname(cdir)) + "/"
        destdir = os.path.join(destDirName, cdirname)
        command = "rsync -a -v -e 'ssh -i " + LOCAL_KEYFILE + "' --delete " + cdir + " " + BACKUP_SERVER_USERNAME + "@" + BACKUP_SERVER + ":" + destdir

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


