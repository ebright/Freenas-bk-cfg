#!/usr/local/bin/python
#
#NaStar Configuration Backup Script (version 1.0_15)
#Original script Created By: Eric Bright Copyright (C) 2013
#Added mail feature by: Dennis Juhler Aagaard
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License version 3 as
#published by the Free Software Foundation.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.
#

#This script is supposed to be copied to /usr/local/sbin/
#The purpose of this script is to look for changes in the config database
#and then make a new copy to the zpool and wrap it up in an email
#for off-site backup purpose.
#the location of the backup is in zpool/.system/cores/
#in this way the config file is both protected by the ZFS and offsite
#backup, with a nice history.
#log location has been changed to /var/log/FreeNASconf-backup.log

import os
import shutil
import datetime
import sys
import logging
import socket
import getopt
import optparse
import subprocess

#Define the arguments and add help describtions
parser = optparse.OptionParser()
parser.add_option('-n', '--name', help="Name of the system", action="store")
parser.add_option('-m', '--mailserver', help="Hostname of mailserver with port; hostname.org:25", action="store")
parser.add_option('-u', '--user', help="Username for the mail account", action="store")
parser.add_option('-p', '--passwd', help="Password for your mail account. Beaware that this is in cleartext", action="store")
parser.add_option('-t', '--emailto', help="Mail you want to send the file to", action="store")
parser.add_option('-f', '--emailfrom', help="Naming of the email adress sent from. Mostly the same as your mailaccount", action="store")

parser.set_defaults(name='Default FreeNAS Name')
options, args = parser.parse_args()

name = systemname = options.name
mailserver = systemname = options.mailserver
user = systemname = options.user
passwd = systemname = options.passwd
emailto = systemname = options.emailto
emailfrom = systemname = options.emailfrom

#Define all other Variables
d = datetime.datetime.now()
date_format = "%Y_%m_%d_%H_%M"
log_file = "/var/log/FreeNASconf-backup.log"
db_file = "/data/freenas-v1.db"
bk_path = os.path.join(subprocess.check_output("zfs list | grep cores | awk -vORS= '{ print $5 }'", shell=True), '')
backup_name = "backup"
archive_name = "archive"
ext = ".db"
localhost = socket.gethostname()
systemname = options.name

matched = None
fname = None
backup_len = len(backup_name)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logging.basicConfig(filename=log_file,
	level=logging.DEBUG,
	format='%(asctime)s.%(msecs).03d %(message)s',
	datefmt='%m/%d/%Y %H:%M:%S')
logging.getLogger('').addHandler(console)

if os.stat(log_file)[6]==0:
	logging.debug('Version 1.0 build 16')
	logging.debug('Automatic Backup Script for FreeNAS Configuration File')
	logging.debug('Original Script Created By: Eric Bright Copyright (C) 2013')
	logging.debug('https://github.com/ebright/FreeNas_Config/')
	logging.debug('---------------------------')

os.chdir(bk_path)
logging.debug('Searching for previous backup in ' + bk_path )
for files in os.listdir("."):
	if files.startswith(backup_name):
		fname = files
		bk_file = bk_path + files
		matched = True
		logging.debug('Found file ' + bk_file)
		break
if matched is True:
	read1 = file(db_file).read().split('\n')
	read2 = file(bk_file).read().split('\n')
	if read1 == read2:
		#logging.info('Configuration has not changed. Aborting backup')
		#No need to know if it has not changed. The important thing is that the backup will run when there has been a change.
		sys.exit()
	else:
		logging.debug('Configuration changed. Archiving previous backup')
		logging.debug(bk_file + ' >> ' + bk_path + archive_name + fname[backup_len:])
		shutil.move(bk_file, bk_path + archive_name + fname[backup_len:])
		logging.info('Creating backup ' + bk_path + backup_name + '_' + d.strftime(date_format) + ext)
		shutil.copy2(db_file, bk_path + backup_name + '_' + d.strftime(date_format) + ext)
		
		#Gather all the Mailserver details + building up the mail containing text and the db file for offsite backup
		import smtplib
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
		attachment = MIMEText(file(bk_path + backup_name + '_' + d.strftime(date_format) + ext).read())
		filename = file(backup_name + '_' + d.strftime(date_format) + ext)
		date = d.strftime(date_format)
		filename2 = 'FreeNAS_Conf_%s_%s%s' % (backup_name, date, ext)
		msg = MIMEMultipart()
		s = smtplib.SMTP('%s' % mailserver)
		s.starttls()
		username = '%s' % user
		password = '%s' % passwd
		s.login(username,password)
		toEmail = '%s' % emailto
		fromEmail = '%s' % emailfrom
		msg['Subject'] = 'Backup of FreeNAS Configfile in hostname: %s. with the name: %s.' % (localhost, systemname)
		msg['From'] = localhost
		attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % filename2)
		body = 'You have recieved this mail because the FreeNAS configurations on \n \n %s \n \n with the name \n \n %s \n \n has been changed... \n' % (localhost, systemname)
		content = MIMEText(body, 'plain')
		body2 = "           \n"
		content2 = MIMEText(body2, 'plain')
		msg.attach(content)
		msg.attach(content2)
		msg.attach(attachment)
		s.sendmail(fromEmail, toEmail, msg.as_string())
					
else:
	bk_file = bk_path + backup_name + '_' + d.strftime(date_format) + ext
	logging.info('No previous backup found. Create new backup: ' + bk_file)
	shutil.copy2(db_file, bk_file)
sys.exit()