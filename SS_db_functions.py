# Sailsheets db funtions
#
# This file contains all of the db functions we will call, 
# specific to the Sailsheets app.
#

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import datetime 
from datetime import timedelta, datetime
from pathlib import Path
import os
import csv
import logging
import sqlite3

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('sailsheets.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def export_excel():
        # This function simply exports each of the tables into separate .csv files 
        # into a Backups directory that is at the same level as the Apps directory.
        #
    
    today = datetime.date.today()
    
    backuppath = './Backups/' + str(today.year)
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
        
        with open(backuppath + '/' + str(today) + '_' + table_name + '.csv', 'w', newline='') as f:
            w = csv.writer(f, dialect='excel')
            for record in result:
                w.writerow(record)
              
    # commit the command and close the db
    db.commit()
    db.close()
    logger.info('All tables exported to backup folder.')
    messagebox.showinfo('', "All tables exported to backup folder.")
    return

############################################
#
# This next bit of code runs at import of this module and simply
# makes a backup of the db if one does not exist.
# 
# Future version will figure out the date of the file and if less
# than 5 days not make a backup.
#
DateNow = datetime.now()
today = datetime.today()
delta = timedelta(days=5)

backuppath = './Backups/' + str(today.year)
p = Path(backuppath) 

if not Path(backuppath).exists():
    p.mkdir(parents=True)

files = os.listdir(p)
paths = [os.path.join(p, basename) for basename in files]
MostRecentFile = os.path.basename(max(paths, key = os.path.getctime))

if DateNow - delta <= datetime.fromtimestamp(os.path.getctime(max(paths, key = os.path.getctime))):
    logger.info('Recent backup file exists.')
else:
    logger.info('Backup file started.')
    primedb = sqlite3.connect('Sailsheets.db')
    backupdb = sqlite3.connect(backuppath + '/' + str(today.strftime('%Y-%m-%d')) + '_' + 'Backup.db')
    primedb.backup(backupdb)
    logger.info('Backup file completed.')
