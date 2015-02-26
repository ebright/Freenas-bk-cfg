#!/usr/local/bin/python
#
#Decryption tool for the FreeNAS Configuration Backup Script.
#Needs to be run with the password to your mailaccount.

import os
import sys
import getopt
import optparse
import subprocess

#Define the arguments and add help describtions
parser = optparse.OptionParser()
parser.add_option('-p', '--passwd', help="Password for your mail account. Beaware that this is in cleartext", action="store")
parser.add_option('-f', '--file', help="Path the .db file you need to decrypt", action="store")
options, args = parser.parse_args()

passwd = systemname = options.passwd
path = systemname = options.file

dpath = os.path.splitext(path)[0]

if passwd:
	subprocess.call(['openssl', 'aes-256-cbc', '-d', '-a', '-salt', '-in', path, '-out', dpath, '-k', passwd])
else:
	subprocess.call(['openssl', 'aes-256-cbc', '-d', '-a', '-salt', '-in', path, '-out', dpath])