#!/usr/local/bin/python
#
#FreeNAS Configuration Backup Script (version 1.0_15)
#Created By: Eric Bright Copyright (C) 2013
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License version 3 as
#published by the Free Software Foundation.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import shutil
import datetime
import sys
import logging

d = datetime.datetime.now()
date_format = "%Y_%m_%d_%H_%M"
log_file = "/tmp/backup.log"
db_file = "/data/freenas-v1.db"
bk_path = "/tmp/"
backup_name = "backup"
latest_name = "current"
ext = ".db"

matched = None
fname = None
latest_len = len(latest_name)

console = logging.StreamHandler()
console.setLevel(logging.INFO)


logging.basicConfig(filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs).03d     %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')
logging.getLogger('').addHandler(console)

logging.info(latest_len)

if  os.stat(log_file)[6]==0:
        logging.debug('Version 1.0 build 15')
        logging.debug('Automatic Backup Script for FreeNAS Configuration File')
        logging.debug('Script Created By: Eric Bright Copyright (C) 2013')
        logging.debug('https://github.com/ebright/FreeNas_Config/')
        logging.debug('---------------------------')

os.chdir(bk_path)
logging.debug('Searching for previous backup in ' + bk_path )
for files in os.listdir("."):
        if files.startswith(latest_name):
                fname = files
                bk_file = bk_path + files
                matched = True
                logging.debug('Found file ' + bk_file)
                break
if matched is True:
        read1 = file(db_file).read().split('\n')
        read2 = file(bk_file).read().split('\n')
        if read1 == read2:
                logging.info('Configuration has not changed. Aborting backup')
                sys.exit()
        else:
                logging.debug('Configuration changed. renaming previous backup')
                logging.debug(bk_file + ' >> ' + bk_path + backup_name + fname[latest_len:])
                shutil.move(bk_file,  bk_path + backup_name + fname[latest_len:])
                logging.info('Creating backup ' + bk_path + latest_name + '_' + d.strftime(date_format) + ext)
                shutil.copy2(db_file, bk_path + latest_name + '_' + d.strftime(date_format) + ext)

else:
        bk_file = bk_path + latest_name + '_' + d.strftime(date_format) + ext
        logging.info('No previous backup found. Create new backup: ' + bk_file)
        shutil.copy2(db_file, bk_file)
sys.exit()
