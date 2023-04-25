###############################################################################
###
###	This standalone script compiles the monthly reports and emails them to the
###		Treasurer and Commodore.
###
###	The script is called via CRON on a monthly basis.  It can be executed on its
###		own and it will behave the same.  Note that no out output is sent to the 
###		terminal.
###	
###############################################################################


#from tkcalendar import Calendar
#from tkcalendar import DateEntry
import logging
import sqlite3
import datetime as dt
from datetime import timedelta

import smtplib
from email.message import EmailMessage
from pathlib import Path
import os
import reports

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

# This function is a simple bit of code lifted from the main Sailsheets App.
#	It was reduced in size/complexity to speed the script.
#
def send_reports(em_to_address='', em_cc_address='', em_subject='', em_body='', files=[]):
    
    msg = EmailMessage()

    msg['From'] = 'npsc.sailor@gmail.com'
    msg['To'] = em_to_address
    msg['Cc'] = em_cc_address
    msg['Subject'] = em_subject

    msg.set_content(em_body,'plain')

    for path in files:
        with open(path, 'rb') as file:
            csv_data = file.read()
        msg.add_attachment(csv_data, maintype='text', subtype='csv', filename=os.path.basename(path))
        #print(path)

    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)
    #s.quit()
    logger.info('Email subject: ' + em_subject + '; sent to Treasurer and Commodore')

# This next bit of code simply figures out which month should be reported.  
#	The reports are always last month's reports.  To run a report for an
#	older monht, use the Sailsheets app as the admin and choose the report.
#
Today = dt.date.today()

# Note, the below list indexes from 0-11, not 1-12.
MonthList = ['January', 'February', 'March',
    'April', 'May', 'June', 
    'July', 'August', 'September',
    'October', 'November', 'December']

if Today.month == 1:
    ReportYear = Today.year-1
    MonthNum = 11
else: 
    ReportYear = Today.year
    MonthNum = Today.month - 1

ReportMonth = MonthList[MonthNum-1]

# Now make sure the correct path is used to dump the report.
#
ReportPath = dir_path + '/Reports/' + str(ReportYear)
p = Path(ReportPath) 
logger.info('Reports directory is ' + str(p))

# If the path doesn't exist, then create it (usually only for the January reports).
#
if not Path(ReportPath).exists():
    p.mkdir(parents=True)

# If one of the reports is there, then assume both reports have already been run.
#
#	If the report is NOT there, then assume the reports need to be run and 
#	run them, log it, then send them via email.
#
if Path(ReportPath + '/' + str(ReportYear) + ' ' + ReportMonth + ' ' + 'Fees Payable from Members.csv').is_file():
    logger.info('Report files exist.')
    if str(os.uname()[1]) != 'sailsheets':
        my_to_addr = 'greenshirt82@gmail.com'
        my_cc_addr = ''
        my_subject = computer_name + ': ' + 'NPSC Sailsheets Reports for ' + str(ReportYear) + ' ' + ReportMonth
        my_files = []
        my_em_body = 'Monthly reports already exist, not attached.  This is just a validation.'
        send_reports(my_to_addr, my_cc_addr, my_subject, my_em_body, my_files)
    else:
        my_to_addr = 'treas@navypaxsail.com'
        my_cc_addr = 'comm@navypaxsail.com'
        my_subject = computer_name + ': ' + 'NPSC Sailsheets Reports for ' + str(ReportYear) + ' ' + ReportMonth
        my_files = []
        my_em_body = 'Monthly reports already exist, not attached.  This is just a validation.'
        send_reports(my_to_addr, my_cc_addr, my_subject, my_em_body, my_files)
else:
    logger.info('Report files started.')
    Report1 = reports.ReportUsage(MonthNum, ReportYear, 0)
    Report2 = reports.ReportMemberUse(MonthNum, ReportYear)
    logger.info('Reports for ' + ReportMonth + '-' + str(ReportYear) + ' created.')
    logger.info('Emailing reports just created.')
    if str(os.uname()[1]) != 'sailsheets':
        my_to_addr = 'greenshirt82@gmail.com'
        my_cc_addr = ''
        my_subject = computer_name + ': ' + 'NPSC Sailsheets Reports for ' + str(ReportYear) + ' ' + ReportMonth
        my_files = [Report1, Report2]
        my_em_body = 'Monthly reports are attached.'
        send_reports(my_to_addr, my_cc_addr, my_subject, my_em_body, my_files)
    else:
        my_to_addr = 'treas@navypaxsail.com'
        my_cc_addr = 'comm@navypaxsail.com'
        my_subject = computer_name + ': ' + 'NPSC Sailsheets Reports for ' + str(ReportYear) + ' ' + ReportMonth
        my_files = [Report1, Report2]
        my_em_body = 'Monthly reports are attached.'
        send_reports(my_to_addr, my_cc_addr, my_subject, my_em_body, my_files)
    logger.info('Reports emailed.')