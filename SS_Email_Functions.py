from screeninfo import get_monitors
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.ttk import Treeview, Style, Button, Entry
from tkcalendar import Calendar
from tkcalendar import DateEntry
import logging
import sqlite3
import datetime as dt
from datetime import timedelta

import smtplib
from email.message import EmailMessage

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


###############################################################################
###
###	This module handles all the emailing functions.
###
###	The primary objective is to send the monthly reports to the Treasurer on the 
###		first use/opening of the app in a month.
###
###	The secondary objective is to send email notifications from the app when a Skipper
###		completes a sail, and to the Commodore when a sail has started/ended.
###	
###############################################################################

def send_email(em_address, em_subject, em_body):
	msg = EmailMessage()
	msg.set_content(em_body)
	msg['Subject'] = em_subject
	msg['From'] = 'NPSC_Sailor@clubhousepc'
	msg['To'] = em_address

	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()
	logger.info('Email subject: ' + em_subject + '; sent to ' + em_address)
	return

def sailplan_closed_email(sailplan_df):
	# df has format of:
	# sailplan_df[0] = sp_id int
	# sailplan_df[1] = sp_timeout text
	# sailplan_df[2] = sp_skipper_id real
	# sailplan_df[3] = sp_sailboat text
	# sailplan_df[4] = sp_purpose text
	# sailplan_df[5] = sp_description text
	# sailplan_df[6] = sp_estrtntime text
	# sailplan_df[7] = sp_timein text
	# sailplan_df[8] = sp_hours real
	# sailplan_df[9] = sp_feeeach real
	# sailplan_df[10] = sp_feesdue real
	# sailplan_df[11] = sp_mwrbilldue real
	# sailplan_df[12] = sp_billmembers int
	# sailplan_df[13] = sp_completed int

	mytitle = 'This is not a bill.  Do not click any links that may be in this email.' + '\n' + '\n'

	myheader = 'The following sailplan has completed: ' + str(sailplan_df[0]) + '\n' + '\n'

	myskipper = 'Skipper ID: ' + str(sailplan_df[2]) + '\n' + '\n'
	myboat = 'Sailboat: ' + sailplan_df[3] + '\n'
	mypurpose = 'Purpose: ' + sailplan_df[4] + '\n'
	mydescription = 'Description: ' + sailplan_df[5] + '\n'
	mybillmembers = 'Members onboard boat: ' + str(sailplan_df[12]) + '\n' + '\n'
	mytimeoutin = 'Times out/in: ' + sailplan_df[1] + ' / ' + sailplan_df[7] + '\n'
	myhours = 'Hours used: ' + str(sailplan_df[8]) + '\n'
	myfee_each = 'Fee each: $ ' + str(sailplan_df[9]) + '\n'
	myfeesdue = 'Fees due NPSC: $ ' + str(sailplan_df[10]) + '\n'
	mymwrbill = 'Payable to MWR for this sail: $ ' + str(sailplan_df[11]) + '\n'


	myemailbody = mytitle + myheader + myskipper + myboat + mypurpose + mydescription + mybillmembers + mytimeoutin + myhours + myfee_each + myfeesdue + mymwrbill

	send_email('greenshirt82@gmail.com', 'Closed Sailplan', myemailbody)
	send_email('comm@navypaxsail.com', 'Closed Sailplan #: ' + str(sailplan_df[0]), myemailbody)

	return

def sailplan_open_email(sailplan_df):
	return

def reports_email(MWRPayableFile, ClubUsageFile, SailplanFile, LedgerFile):
	return

def member_email(ledgerid, sailplanid):
	return

if __name__ == '__main__':
    send_email('greenshirt82@gmail.com', 'Test email subject', 'This is just a test of the smtp library for Sailsheets.')
