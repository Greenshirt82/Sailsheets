# Sailsheets db funtions
#
# This file contains all of the db functions we will call, 
# specific to the Sailsheets app.
#

import datetime 
from datetime import timedelta, datetime
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


def send_files(files=[]):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
    """
    #em_subject = 'NPSC Club Computer Monthly Reports'
    #em_address = 'treas@navypaxsail.com'
    em_subject = "Weekly Sailsheets backup files"
    em_address = 'greenshirt82@gmail.com'

    msg = EmailMessage()

    msg['From'] = 'npsc.sailor@gmail.com'
    msg['To'] = em_address
    #msg['Cc'] = 'comm@navypaxsail.com'
    msg['Subject'] = em_subject

    msg.set_content('Weekly backup csv files are attached.','plain')

    for path in files:
        with open(path, 'rb') as file:
            csv_data = file.read()
        msg.add_attachment(csv_data, maintype='text', subtype='csv', filename=os.path.basename(path))

    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)
    #s.quit()
    logger.info('Email subject: ' + em_subject + '; sent to ' + em_address)


today = datetime.today()

backuppath = dir_path + '/Backups/' + str(today.year)
p = Path(backuppath) 

if not Path(backuppath).exists():
    p.mkdir(parents=True)

db = sqlite3.connect('Sailsheets.db')
c = db.cursor()


# This query gets the list of tables in the db.
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_list = c.fetchall()

for table_name in table_list:
    table_name = table_name[0]
    
    c.execute("SELECT * FROM " + table_name)
    result = c.fetchall()    
    # open the backup file: a=append, r=readonly, w=write (new)
    
    with open(backuppath + '/' + str(today.strftime('%Y-%m-%d')) + '_' + table_name + '.csv', 'w', newline='') as f:
        w = csv.writer(f, dialect='excel')
        for record in result:
            w.writerow(record)
          
# commit the command and close the db
db.commit()
db.close()
logger.info('All tables exported to backup folder.')

file_list = []

for table_name in table_list:
    table_name = table_name[0]
    
    file_list.append(backuppath + '/' + str(today.strftime('%Y-%m-%d')) + '_' + table_name + '.csv')

send_files(file_list)

logger.info('All files sent to greenshirt82@gmail.com.')