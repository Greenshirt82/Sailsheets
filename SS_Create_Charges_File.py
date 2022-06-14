#####################################
#
#	This file creates a csv file of charges that can be uploaded
#	to Club Express as a means of automating the charge process.
#
#	Format of the CSV is:
#
#	Column	Column title	Example data	Ledger Table source Field
#	A 		Member Number	1234			l_billto_id
#	B 		Charge Type		Charge 			"Charge"
#	C 		Charge Date 	mm/dd/yyyy		l_date
#	D 		Dollar amount	12.34 			l_fee
#	E 		Description		Racing - Wed	l_description
#	F 		Financial acct	Racing			l_account
#
#	Note: Charge Type can be "Charge" or "Credit".

import logging
import sqlite3
import datetime as dt
from pathlib import Path
from datetime import date
import csv

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def CreateChargesFile(mymonth, myyear):
    month_list = ['01', '02', '03',
                    '04', '05', '06', 
                    '07', '08', '09',
                    '10', '11', '12']

    rpt_yr_mo = str(myyear) + '-' + month_list[mymonth-1]
    
    reportpath = './Transfer/' + str(myyear)
    p = Path(reportpath) 
    
    if not Path(reportpath).exists():
        p.mkdir(parents=True)

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()

    c.execute("""SELECT l_billto_id, l_date, l_fee, l_description, l_account, ledger_id, l_name
        FROM Ledger 
        WHERE strftime('%Y-%m', l_date) == :rpt_date
        ORDER BY l_date, l_billto_id
        """, {'rpt_date': rpt_yr_mo,})

    chargetable = c.fetchall()

    db.commit()
    db.close()

    logger.info('Fetched charge data for ' + rpt_yr_mo + ' from the Ledger table.')

    myfilename = reportpath + '/' + str(myyear) + '-' + month_list[mymonth-1] + '-' + 'charges_and_credits' + '.csv'

    with open(myfilename, 'w', newline='') as f:
        w = csv.writer(f, dialect='excel')
 
        w.writerow(["Member Number", "Charge Type", "Charge Date", 
            "Dollar Amount", "Description", "Financial Account Name"])

        for record in chargetable:
            # First, only look at ledger records with a fee 
            if record[2] > 0:
                w.writerow([str(record[0]), "Charge", 
                    record[1][8:10] + '/' + record[1][5:7] + '/' + record[1][0:4], 
                    record[2], str(record[5]) + ': ' + record[6] + ' - ' + record[3], record[4]])

    logger.info('Charges file ' + myfilename + ' written to transfer folder.')

if __name__ == '__main__':
    CreateChargesFile(5, 2022)