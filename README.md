Freenas-bk-cfg
Python script to backup FreeNAS configuration file Created by Eric Bright Copyright (C) 2013
Expanded by adding mail, and the use of zpool location of the backup, by Dennis Juhler Aagaard (C) 2014

This script will copy the FreeNAS configuration file (/data/freenas-v1.db) to the location /mnt/<zpool>/.system/cores. The script copies the configuration only when a change has been made to the FreeNAS Configuration file and mail it to a email account of your choosing. Previous backups will be archived when a new backup is created.

Arguments to the script has been made to make it flexible to which mail server should be used and also introduced a System name independent of hostname og the system in case you have multiple FreeNAS systems you need to have backups from.

Usage: BackupConf.py [options]

Options:
  -h, --help            show this help message and exit  
  -n NAME, --name=NAME  Name of the system
  -m MAILSERVER, --mailserver=MAILSERVER
                        Hostname of mailserver with port; hostname.org:25
  -u USER, --user=USER  Username for the mail account
  -p PASSWD, --passwd=PASSWD
                        Password for your mail account. Beaware that this is
                        in cleartext
  -t EMAILTO, --emailto=EMAILTO
                        Mail you want to send the file to
  -f EMAILFROM, --emailfrom=EMAILFROM
                        Naming of the email adress sent from. Mostly the same
                        as your mailaccount



Install Instructions

Copy BackupConf.py to /usr/local/sbin/ by first mounting the system as writeable with mount -uw /
Change permissions to add execute to backup.py (ex. chmod +x /tmp/backup.py)
Change the system back to read-only with mount -ur /

Log into the FreeNAS Web Interface
Expand System, expand Cron Jobs
Select Add Cron Job
User = root 
Command = BackupConf.py -n [name] -m [mailserver hostname] -u [mail account user] -p [password] -t [emailto] -f [emailfrom]


Set it to run each hour to catch your FreeNAS changes. If there has not been any changes, nothing will happen.

Uncheck Redirect Stdout to receive email* updates for the backup operation
Recommended is having this checked, because you will recieve an email with the .db files attached.

Uncheck Redirect Stderr to receive email* updates for errors processing the script
Recommended is to have this unchecked to recieve any errors that might happen.

Check Enabled to enable this job
*emails sent to root account's email address
