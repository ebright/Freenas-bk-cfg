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
"""
    -\-                                                     
    \-- \-                                                  
     \  - -\                                                
      \      \\                                             
       \       \                                            
        \       \\                                              
         \        \\                                            
         \          \\                                        
         \           \\\                                      
          \            \\                                                 
           \            \\                                              
           \. .          \\                                  
            \    .       \\                                 
             \      .    \\                                            
              \       .  \\                                 
              \         . \\                                           
              \            <=)                                         
              \            <==)                                         
              \            <=)                                           
               \           .\\                                           _-
               \         .   \\                                        _-//
               \       .     \\                                     _-_/ /
               \ . . .        \\                                 _--_/ _/
                \              \\                              _- _/ _/
                \               \\                      ___-(O) _/ _/ 
                \                \                  __--  __   /_ /      ***********************************
                \                 \\          ____--__----  /    \_       I AM A MOTHERFUCKING PTERODACTYL
                 \                  \\       -------       /   \_  \_     HERE TO PTERO-YOU A NEW ASSHOLE
                  \                   \                  //   // \__ \_   **********************************
                   \                   \\              //   //      \_ \_ 
                    \                   \\          ///   //          \__- 
                    \                -   \\/////////    //            
                    \            -         \_         //              
                    /        -                      //                
                   /     -                       ///                  
                  /   -                       //                      
             __--/                         ///
  __________/                            // |               
//-_________      ___                ////  |                
        ____\__--/                /////    |                
   -----______    -/---________////        |                
     _______/  --/    \                   |                 
   /_________-/       \                   |                 
  //                  \                   /                 
                       \.                 /                 
                       \     .            /                 
                        \       .        /                  
                       \\           .    /                  
                        \                /                  
                        \              __|                  
                        \              ==/                  
                        /              //                   
                        /          .  //                    
                        /   .  .    //                      
                       /.           /                       
                      /            //                       
                      /           /
                     /          //
                    /         //
                 --/         /
                /          //
            ////         //
         ///_________////
"""




import os
import shutil
import datetime
import sys
import logging

d = datetime.datetime.now()
date_format = "%Y_%m_%d_%H_%M"
log_file = "/tmp/freenas-backup.log"
db_file = "/data/freenas-v1.db"
bk_path = "/tmp/"
backup_name = "backup"
archive_name = "archive"
ext = ".db"

matched = None
fname = None
backup_len = len(backup_name)

console = logging.StreamHandler()
console.setLevel(logging.INFO)


logging.basicConfig(filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs).03d     %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')
logging.getLogger('').addHandler(console)

if  os.stat(log_file)[6]==0:
        logging.debug('Version 1.0 build 16')
        logging.debug('Automatic Backup Script for FreeNAS Configuration File')
        logging.debug('Script Created By: Eric Bright Copyright (C) 2013')
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
        with open(db_file, "rb") as f:
            read1 = f.read()
        with open(bk_file, "rb") as f:
            read2 = f.read()
        if read1 == read2:
                logging.info('Configuration has not changed. Aborting backup')
                sys.exit()
        else:
                logging.debug('Configuration changed. Archiving previous backup')
                logging.debug(bk_file + ' >> ' + bk_path + archive_name + fname[backup_len:])
                shutil.move(bk_file,  bk_path + archive_name + fname[backup_len:])
                logging.info('Creating backup ' + bk_path + backup_name + '_' + d.strftime(date_format) + ext)
                shutil.copy2(db_file, bk_path + backup_name + '_' + d.strftime(date_format) + ext)

else:
        bk_file = bk_path + backup_name + '_' + d.strftime(date_format) + ext
        logging.info('No previous backup found. Create new backup: ' + bk_file)
        shutil.copy2(db_file, bk_file)
sys.exit()
