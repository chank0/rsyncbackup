# rsyncbackup
A script to perform backups through the network with snapshots

This script is an implementation of the method described in http://www.mikerubel.org/computers/rsync_snapshots/ for performing backups with snapshots.

The initial features are:
- Transfers are done through ssh
- Backup any number of local directories
- Store any number of snapshots
- Snapshots make use of hard links (this is, duplicated files in the snapshots do not use extra disk space)

## Disclaimer
This script is meant for my personal use, and has been developed without considering potential security issues. It is not advised to use it for handling sensitive data and/or over untrusted networks.

## Requirements

- python 2.7
- rsync
- ssh

## Usage

It is necessary to initialize the backup server the first time the script is going to be used. It is achieved by running
`rsyncBackup.py init`

This generates a keyfile (it prompts for a passphrase, which **must be empty**). The keyfile is then copied to the server.

Afther this initialization, just execute `rsyncBackup.py update`. Every time it is executed, a new snapshot is created in the remote server. You probably want to execute it by means of a cron job.
