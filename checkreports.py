############################################
#
# This module simply checks for the existance of last month's reports
# then if they exist do nothing, if they do exist, then create and
# send the reports to the Treasurer and Commodore
#

import logging
import datetime as dt
from pathlib import Path
import reports
import email_functions
import os

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('sailsheets.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


############################################
#
# This next bit of code runs at import of this module and simply
# runs & emails monthly reports they do not exist.
# 
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

ReportPath = './Reports/' + str(ReportYear)
p = Path(ReportPath) 

if not Path(ReportPath).exists():
    p.mkdir(parents=True)

if Path(ReportPath + '/' + str(ReportYear) + ' ' + ReportMonth + ' ' + 'Fees Payable from Members.csv').is_file():
    logger.info('Report files exist.')
else:
    logger.info('Report files started.')
    
    Report1 = reports.ReportUsage(MonthNum, ReportYear, 0)
    Report2 = reports.ReportMemberUse(MonthNum, ReportYear)
    # ChargesFile = SS_Create_Charges_File.CreateChargesFile(mymonth, myyear)

    logger.info('Reports for ' + ReportMonth + '-' + str(ReportYear) + ' created.')

    logger.info('Emailing reports just created.')
#    PayableReport = ReportPath + '/' + str(ReportYear) + ' ' + ReportMonth + ' ' + 'Fees Payable from Members.csv'
#    MWRReport = ReportPath + '/' + str(ReportYear) + ' ' + ReportMonth + ' ' + 'Usage Fees Payable to MWR.csv'
    SS_Email_Functions.send_reports([Report1, Report2])
    logger.info('Reports emailed.')