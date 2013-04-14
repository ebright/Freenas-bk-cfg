Freenas-bk-cfg
==============

Python script to backup FreeNAS configuration file
Created by Eric Bright Copyright (C) 2013

This script will copy the FreeNAS configuration file (/data/freenas-v1.db) to the location of your choice.
The script copies the configuration only when a change has been made to the FreeNAS Configuration file.  Previous 
backups will be archived when a new backup is created. 

Install Instructions
===================

1. Copy backup.py to any accessible folder you like. (ex. /tmp/backup.py)
2. Change permissions to add execute to backup.py (ex. chmod +x /tmp/backup.py)
3. Log into the FreeNAS Web Interface
5. Expand System, expand Cron Jobs
5. Select Add Cron Job
6. User = root 
   Command = /tmp/backup.py
   Select the minute that you want the script to start
   Select the hour that you want the script to start
   Move the slider to run the script ever N day
   Select the days and the months that you want the script to run
7. Uncheck Redirect Stdout to receive email updates for the backup operation
8. Uncheck Redirect Stderr to receive email updates for errors processing the script
9. Check Enabled to enable this job

*emails sent to root account's email address
