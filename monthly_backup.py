###############################################################################
# Monthly backup
#
# This file creates a backup of the Sailsheets.db file 
#
# This script is executed via cron monthly or manually as needed.
#
###############################################################################

#import datetime 
from datetime import date
from pathlib import Path
import os
import csv
import logging
import sqlite3
import smtplib
from email.message import EmailMessage

# Set up the logging system
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'sailsheets.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(filename)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
computer_name = str(os.uname()[1]) 

# This function simply sends a plain text email.
#
def send_email(em_to_address, em_subject, em_body):
    msg = EmailMessage()
    msg.set_content(em_body)
    msg['Subject'] = em_subject
    msg['From'] = 'npsc.sailor@gmail.com'
    msg['To'] = em_to_address

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    logger.info('Email subject: ' + em_subject + '; sent to ' + em_to_address)
    return

# Make sure we know what the file path is to the backup directory.
#
today = date.today()
backuppath = dir_path + '/Backups/' + str(today.year)
p = Path(backuppath) 
logger.info('Backup directory is ' + str(p))
backupfile = str(today.strftime('%Y-%m-%d')) + '_' + 'Backup.db'

# If the backup path does not exist, create it.
#
if not Path(backuppath).exists():
    p.mkdir(parents=True)

# This next line tells the dev which computer is doing the backup
#
my_email_subject = computer_name + ': ' + 'Monthly Backup'
#
if Path(backuppath + '/' + backupfile).is_file():
    logger.info('Recent backup file exists @: ' + backupfile)
    my_to_addr = 'greenshirt82@gmail.com'
    my_email_body = 'Recent backup file exists @: ' + backupfile
    send_email(my_to_addr, my_email_subject, my_email_body)
else:
    logger.info('Backup file started.')
    primedb = sqlite3.connect(dir_path + '/' + 'Sailsheets.db')
    backupdb = sqlite3.connect(backuppath + '/' + backupfile)
    primedb.backup(backupdb)
    logger.info('Backup file completed.')
    my_to_addr = 'greenshirt82@gmail.com'
    my_email_body = backupfile + ' created'
    send_email(my_to_addr, my_email_subject, my_email_body)
exit()