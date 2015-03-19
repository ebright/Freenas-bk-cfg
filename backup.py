#!/usr/local/bin/python
#
#FreeNAS Configuration Backup Script (version 3)
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
#log location has been changed to /var/log/FreeNASConf-backup.log


import os
import shutil
import datetime
import sys
import logging
import socket
import getopt
import optparse
import subprocess

from subprocess import Popen, PIPE
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header

localhost = socket.gethostname()

#Define the arguments and add help describtions. YOU NEED TO CHANGE THE DEFAULT VALUES!!!!!!!!!!!!!!

parser = optparse.OptionParser()
parser.add_option('-n', '--name', default='Default FreeNAS Name', help="Name of the system", action="store")
parser.add_option('-p', '--passwd', default='defaultpassword', help="Beaware that this is in cleartext. This password will also be used for encryption.", action="store")
parser.add_option('-t', '--emailto', default='default@domain.com', help="Mail you want to send the file to", action="store")
parser.add_option('-f', '--emailfrom', default='default@domain.com', help="Naming of the email adress sent from. Mostly the same as your mailaccount", action="store")

options, args = parser.parse_args()

name = systemname = options.name
passwd = systemname = options.passwd
emailto = systemname = options.emailto
emailfrom = systemname = options.emailfrom

#Define all other Variables:

d = datetime.datetime.now()
date_format = "%Y_%m_%d_%H_%M"
log_file = "/var/log/FreeNASConf-backup.log"
db_file = "/data/freenas-v1.db"
bk_path = os.path.join(subprocess.check_output("zfs list | grep cores | awk -vORS= '{ print $5 }'", shell=True), '')
backup_name = "FreeNAS-backup"
archive_name = "FreeNAS-archive"
ext = ".db"
enc = ".enc"

systemname = options.name
UUID = subprocess.check_output("dmidecode | grep UUID | sed 's/.*: //'", shell=True)

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
	logging.debug('Version 3.0 ')
	logging.debug('Automatic Backup Script for FreeNAS Configuration File')
	logging.debug('Original Script Created By: Eric Bright Copyright (C) 2013')
	logging.debug('https://github.com/ebright/FreeNas_Config/')
	logging.debug('Refined by Dennis Juhler Aagaard')
	logging.debug('https://github.com/kulmosen/Freenas-bk-cfg')
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
		
		#Add function to encrypt the log file to secure the mail transmit using openssl enc -e
		#need to make a script to ease the deencryption on client side.
		
		subprocess.call(['openssl', 'aes-256-cbc', '-a', '-salt', '-in', bk_path + backup_name + '_' + d.strftime(date_format) + ext, '-out', bk_path + backup_name + '_' + d.strftime(date_format) + ext + enc, '-k', passwd])
		

		#Building the email with attachment using sendmail in system going away from SMTP lib

		#Define variables in mail
		attachment = MIMEText(file(bk_path + backup_name + '_' + d.strftime(date_format) + ext + enc).read())
		filename = file(backup_name + '_' + d.strftime(date_format) + ext)
		date = d.strftime(date_format)
		filename2 = '%s_%s%s%s' % (backup_name, date, ext, enc)
		#fromaddr = formataddr((str(Header(u'%s' % name , 'utf-8')), "%s" % emailfrom))
		#sendername = '%s <%s>' % (name, emailfrom)
		fromaddr = '%s <%s>' % (name, emailfrom)
		msg = MIMEMultipart()
		msg['Subject'] = 'Backup of FreeNAS Configfile in hostname: %s. with the name: %s.' % (localhost, systemname)
		#msg['From'] = '%s' % fromaddr
		msg['From'] = formataddr((str(Header(u'%s' % name , 'utf-8')), "%s" % emailfrom))
		msg['Reply-to'] = '%s@%s' % (name, localhost)
		msg['To'] = '%s' % emailto
		
		 
		# That is what u see if dont have an email reader:
		msg.preamble = 'Multipart massage.\n'
		 
		# This is the textual part:
		part = MIMEText('You have recieved this mail because the FreeNAS configurations on \n \n %s \n \n with the name \n \n %s \n \n UUID: %s \n has been changed... \n' % (localhost, systemname, UUID))
		msg.attach(part)
		 
		# This is the binary part(The Attachment):
		part = MIMEApplication(open("%s%s" % (bk_path, filename2),"rb").read())
		part.add_header('Content-Disposition', 'attachment', filename="%s" % filename2)
		msg.attach(part)
		 
		p = Popen(["/usr/sbin/sendmail", "-t", "-oi", "-f", '%s <%s>' % (name, emailfrom)], stdin=PIPE)
		p.communicate(msg.as_string())
		print "successfully sent email"
		
		#remove the encrypted file after sending it. 
		subprocess.call(['rm', '-R', bk_path + backup_name + '_' + d.strftime(date_format) + ext + enc]) 



else:
	bk_file = bk_path + backup_name + '_' + d.strftime(date_format) + ext
	logging.info('No previous backup found. Create new backup: ' + bk_file)
	shutil.copy2(db_file, bk_file)
	subprocess.call(['openssl', 'aes-256-cbc', '-a', '-salt', '-in', bk_path + backup_name + '_' + d.strftime(date_format) + ext, '-out', bk_path + backup_name + '_' + d.strftime(date_format) + ext + enc, '-k', passwd])
		

	#Building the email with attachment using sendmail in system going away from SMTP lib

	#Define variables in mail
	attachment = MIMEText(file(bk_path + backup_name + '_' + d.strftime(date_format) + ext + enc).read())
	filename = file(backup_name + '_' + d.strftime(date_format) + ext)
	date = d.strftime(date_format)
	filename2 = '%s_%s%s%s' % (backup_name, date, ext, enc)
	#fromaddr = formataddr((str(Header(u'%s' % name , 'utf-8')), "%s" % emailfrom))
	#sendername = '%s <%s>' % (name, emailfrom)
	fromaddr = '%s <%s>' % (name, emailfrom)
	msg = MIMEMultipart()
	msg['Subject'] = 'Backup of FreeNAS Configfile in hostname: %s. with the name: %s.' % (localhost, systemname)
	#msg['From'] = '%s' % fromaddr
	msg['From'] = formataddr((str(Header(u'%s' % name , 'utf-8')), "%s" % emailfrom))
	msg['Reply-to'] = '%s@%s' % (name, localhost)
	msg['To'] = '%s' % emailto
	
	 
	# That is what u see if dont have an email reader:
	msg.preamble = 'Multipart massage.\n'
	 
	# This is the textual part:
	part = MIMEText('You have recieved this mail because the FreeNAS configurations on \n \n %s \n \n with the name \n \n %s \n \n UUID: %s \n has been changed... \n' % (localhost, systemname, UUID))
	msg.attach(part)
	 
	# This is the binary part(The Attachment):
	part = MIMEApplication(open("%s%s" % (bk_path, filename2),"rb").read())
	part.add_header('Content-Disposition', 'attachment', filename="%s" % filename2)
	msg.attach(part)
	 
	p = Popen(["/usr/sbin/sendmail", "-t", "-oi", "-f", '%s <%s>' % (name, emailfrom)], stdin=PIPE)
	p.communicate(msg.as_string())
	print "successfully sent email"
	
	#remove the encrypted file after sending it. 
	subprocess.call(['rm', '-R', bk_path + backup_name + '_' + d.strftime(date_format) + ext + enc]) 
sys.exit()






