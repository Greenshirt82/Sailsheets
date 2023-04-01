# Monthly backup
#
# This file creates a backup of the Sailsheets.db file but only if
#   a backup is older than 5 days.
#
# This script is executed via cron at 0000 on 1st day of every month
#   or
# on rebood of the computer.

import datetime 
from datetime import timedelta, datetime
from pathlib import Path
import glob
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


# This function was lifted from the Sailsheets App.
#   It simply sends a plain text email.
#
def send_email(em_address, em_subject, em_body):
    msg = EmailMessage()
    msg.set_content(em_body)
    msg['Subject'] = em_subject
    msg['From'] = 'npsc.sailor@gmail.com'
    msg['To'] = em_address

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    logger.info('Email subject: ' + em_subject + '; sent to ' + em_address)
    return

# This next bit of code simply figures out what day it is
#
DateNow = datetime.now()
today = datetime.today()
delta = timedelta(days=5)

# Make sure we know what the file path is to the backup directory.
#
backuppath = dir_path + '/Backups/' + str(today.year)
p = Path(backuppath) 

# If the backup path does not exist, create it.
#
if not Path(backuppath).exists():
    p.mkdir(parents=True)

# This next line is a special function I pulled in to easily find the db files
#
files = glob.glob(backuppath + '/*.db')

# Now figure out the date of the most recent backup.
#
paths = [os.path.join(p, basename) for basename in files]
MostRecentFile = os.path.basename(max(paths, key = os.path.getctime))

# if the most recent backup is less than the time delat, ignore
#   otherwise, make a new backup and send an email to the Commodore
#
if DateNow - delta <= datetime.fromtimestamp(os.path.getctime(max(paths, key = os.path.getctime))):
    logger.info('Recent backup file exists.')
else:
    logger.info('Backup file started.')
    primedb = sqlite3.connect('Sailsheets.db')
    backupdb = sqlite3.connect(backuppath + '/' + str(today.strftime('%Y-%m-%d')) + '_' + 'Backup.db')
    primedb.backup(backupdb)
    logger.info('Backup file completed.')
    send_email('comm@navypaxsail.com', 'Monthly Backup', str(today.strftime('%Y-%m-%d')) + '_' + 'Backup.db' + ' created')