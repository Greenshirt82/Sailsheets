#####################################################################
#
# NavyPaxSail Sailsheets application (admin only)
#
#      VERSION 2
#
# This module contains the functions for printing monthly reports.
#
#####################################################################

import logging
import sqlite3
import datetime 
from pathlib import Path
from datetime import date
from tkinter import messagebox
import csv

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


global mymonth, myyear

def ReportUsage(mymonth, myyear, NPSCOnly):
    d = datetime.date(day=1, month=mymonth, year=myyear)
    month_list = ['January', 'February', 'March',
                    'April', 'May', 'June', 
                    'July', 'August', 'September',
                    'October', 'November', 'December']

    reportpath = './Reports/' + str(d.year)
    p = Path(reportpath) 
    
    if not Path(reportpath).exists():
        p.mkdir(parents=True)

    if NPSCOnly == 1:
        myreportname = reportpath + '/' + str(d.year) + ' ' + month_list[mymonth-1] + ' Usage - NPSC' + '.csv'
    else:
        myreportname = reportpath + '/' + str(d.year) + ' ' + month_list[mymonth-1] + ' Usage Fees Payable to MWR' + '.csv'

    #####################################################################
    # 
    # This module reads the AllMembers.csv file exported from Club Express
    # and compares each member in that file to the Members table in the db.
    # If any records are not identical, the Members table is then updated
    # to reflect what is in the AllMembers.csv file because that is the 
    # official membership record.
    #
    # The following fields should match:
    #   Members usagetable  AllMembers.csv (field/column #)
    #    m_id int           member_number (A)
    #    m_name text        last_name (C) + ', ' + first_name (B)
    #    m_status text      status (AD)
    #    m_expdate text     date_expired (AB)
    #    m_type text        membership_type (AE)
    #    m_prime text       primary_member (AI)

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
        
    """CREATE TABLE Members (m_id int primary key,
        m_name text,
        m_status text,
        m_expdate text,
        m_type text,
        m_prime text,
        m_suspended int, not used set to 0
        m_debt int, not used set to 0
        m_ignore int); not used set to 0
    
    CREATE TABLE Settings (discount int, pw text, delay int);

    CREATE TABLE Boats (boat_id int primary key,
        boat_type text,
        boat_class text,
        boat_name text,
        QualRequired int,
        E5HourRate real,
        E5DayRate real,
        HourRate real,
        DayRate real,
        NPSCHourRate real,
        NPSCDayRate real,
        Down int,
        DownDescription text,
        Retired int);

    """

    if NPSCOnly == 1:
        c.execute("""SELECT Boats.boat_class AS boatclass, SailPlan.sp_sailboat as Sailboat, ledger_id, 
            l_date, l_member_id, l_name, l_skipper, SailPlan.sp_purpose AS purpose, Ledger.l_sp_id, 
            SailPlan.sp_hours AS hours, SailPlan.sp_mwrbilldue AS revenue
            FROM Ledger 
            JOIN SailPlan on Ledger.l_sp_id=SailPlan.sp_id
            JOIN Boats on SailPlan.sp_sailboat=Boats.boat_Name
            ORDER BY boatclass, Sailboat, purpose, l_date
            """)
        logger.info('Fetched data for NPSC Usage.')
    else:
        c.execute("""SELECT Boats.boat_class AS boatclass, SailPlan.sp_sailboat as Sailboat, ledger_id, 
            l_date, l_member_id, l_name, l_skipper, SailPlan.sp_purpose AS purpose, Ledger.l_sp_id, 
            SailPlan.sp_hours AS hours, SailPlan.sp_mwrbilldue AS revenue
            FROM Ledger 
            JOIN SailPlan on Ledger.l_sp_id=SailPlan.sp_id
            JOIN Boats on SailPlan.sp_sailboat=Boats.boat_Name
            WHERE SailPlan.sp_sailboat!='Skyline'
            ORDER BY boatclass, Sailboat, purpose, l_date
            """)
        logger.info('Fetched data for MWR Usage.')
        
    usagetable = c.fetchall()
        
    with open(myreportname, 'w', newline='') as f:
        w = csv.writer(f, dialect='excel')
        w.writerow(["Report period: ", month_list[mymonth-1], myyear])
        w.writerow([" "])
        #w.writerow([" ", "Note: The purpose of this report is to document amount payable to MWR from NPSC."])
        #w.writerow([" ", " ", "Additionally, the last column should be used to spot check the charges file."])
        #w.writerow([" "])
        
        firstrecord = usagetable[0]
        boatclass = firstrecord[0]
        boat = firstrecord[1]
        boatpurpose = firstrecord[7]
        w.writerow(["Boat Class: " + str(boatclass)])
        w.writerow([" ", boat, "Ledger ID", "Date of sail", "Skipper ID", "Skipper", 
            "Purpose", "Sailplan ID", "Hours", "Payable to MWR"])
        #w.writerow([" "])
        
        # Set the totals to zero 
        #
        hrs_purpose_total = 0
        hrs_boat_total = 0
        hrs_class_total = 0
        hrs_grand_total = 0
        revenue_purpose_total = 0
        revenue_boat_total = 0
        revenue_class_total = 0
        revenue_grand_total = 0

        for record in usagetable:
            myrow = ([' ', ' ', 
                str(record[2]), 
                str(record[3]), 
                str(record[4]), 
                str(record[5]),
                str(record[7]), 
                str(record[8]), 
                str(round(record[9],1)), 
                str(round(record[10],2))])
            mydate = date.fromisoformat(str(record[3]))
            if (boatclass == record[0] 
                    and boat == record[1] 
                    and boatpurpose == record[7] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear 
                    and record[6] == 1):
                
                hrs_purpose_total += record[9]
                hrs_boat_total += record[9]
                hrs_class_total += record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total += record[10]
                revenue_boat_total += record[10]
                revenue_class_total += record[10]
                revenue_grand_total += record[10]
                #
                w.writerow(myrow)
                #
            elif (boatclass == record[0] 
                    and boat == record[1] 
                    and boatpurpose != record[7] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear 
                    and record[6] == 1):
                w.writerow([" ", " ", " ", " ", " ", " ", " ", "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                boatpurpose = record[7]
                w.writerow([" ", boat, "Ledger ID", "Date of sail", "Skipper ID", "Skipper", 
                    "Purpose", "Sailplan ID", "Hours", "Payable to MWR"])
                
                hrs_purpose_total = record[9]
                hrs_boat_total += record[9]
                hrs_class_total += record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total += record[10]
                revenue_class_total += record[10]
                revenue_grand_total += record[10]
                
                w.writerow(myrow)
                #
            elif (boatclass == record[0] 
                    and boat != record[1] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear 
                    and record[6] == 1):
                w.writerow([" ", " ", " ", " ", " ", " ", " ", "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", "Boat Subtotal:", 
                    str(round(hrs_boat_total,1)), 
                    str(round(revenue_boat_total, 2))])
                w.writerow([" "])
                boat = record[1]
                boatpurpose = record[7]
                w.writerow([" ", boat, "Ledger ID", "Date of sail", "Skipper ID", "Skipper", 
                    "Purpose", "Sailplan ID", "Hours", "Payable to MWR"])
                #
                hrs_purpose_total = record[9]
                hrs_boat_total = record[9]
                hrs_class_total += record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total = record[10]
                revenue_class_total += record[10]
                revenue_grand_total += record[10]
                #
                w.writerow(myrow)
                #
            elif (boatclass != record[0] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear 
                    and record[6] == 1):
                w.writerow([" ", " ", " ", " ", " ", " ", " ", "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", "Boat Subtotal:", 
                    str(round(hrs_boat_total,1)), 
                    str(round(revenue_boat_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", "Boat Class Total:", 
                    str(round(hrs_class_total,1)), 
                    str(round(revenue_class_total, 2))])
                w.writerow([" "])
                boatclass = record[0]
                boat = record[1]
                boatpurpose = record[7]
                
                w.writerow(["Boat Class: " + str(boatclass)])
                w.writerow([" ", boat, "Ledger ID", "Date of sail", "Skipper ID", "Skipper", 
                    "Purpose", "Sailplan ID", "Hours", "Payable to MWR"])

                hrs_purpose_total = record[9]
                hrs_boat_total = record[9]
                hrs_class_total = record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total = record[10]
                revenue_class_total = record[10]
                revenue_grand_total += record[10]
                
                w.writerow(myrow)
        
        w.writerow([" ", " ", " ", " ", " ", " ", " ", "Boat Subtotal:", str(round(hrs_boat_total,1)), 
            str(round(revenue_boat_total, 2))])
        w.writerow([" "])
        w.writerow([" ", " ", " ", " ", " ", " ", " ", "Boat Class Total:", str(round(hrs_class_total,1)), 
            str(round(revenue_class_total, 2))])
        w.writerow([" "])
        w.writerow([" ", " ", " ", " ", " ", " ", " ", "Grand Total:", str(round(hrs_grand_total,1)), 
            str(round(revenue_grand_total, 2)), "<-- Payable to MWR before maintenance deductions."])
        w.writerow([" "])

    db.commit()
    db.close()
    logger.info('Executed reportusage ' + str(NPSCOnly) + ' (1=NPSC only)')
    return myreportname

    # if NPSCOnly == 1:
    #     messagebox.showinfo('', "NPSC Boat usage report in folder: " + reportpath)
    # else:
    #     messagebox.showinfo('', "MWR Boat usage report in folder: " + reportpath)

def ReportDetailUse():
    
    #####################################################################
    # 
    # This report reads the SailPlan table and summarizes utilization by 
    # month for the previous calendar year.  Each boat and boat type is
    # summarized with hours and revenues.
    #

    month_list = ['January', 'February', 'March',
                    'April', 'May', 'June', 
                    'July', 'August', 'September',
                    'October', 'November', 'December']

    reportpath = './Reports'
    
    myreportname = reportpath + '/' + ' Detailed Utilization' + '.csv'

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
        
    c.execute("""SELECT Boats.boat_class AS boatclass, SailPlan.sp_sailboat as Sailboat, ledger_id, 
        l_date, l_member_id, l_name, l_skipper, SailPlan.sp_purpose AS purpose, Ledger.l_sp_id, 
        SailPlan.sp_hours AS hours, l_fee AS revenue
        FROM Ledger 
        JOIN SailPlan on Ledger.l_sp_id=SailPlan.sp_id
        JOIN Boats on SailPlan.sp_sailboat=Boats.boat_Name
        ORDER BY l_date, l_sp_id, boatclass, Sailboat, purpose, l_member_id
        """)
    logger.info('Fetched data for Utilization Report.')
        
    usagetable = c.fetchall()
        
    with open(myreportname, 'w', newline='') as f:
        firstrecord = usagetable[0]
        boatclass = firstrecord[0]
        boat = firstrecord[1]
        boatpurpose = firstrecord[7]
        myspid = firstrecord[8]
        mydate = date.fromisoformat(str(firstrecord[3]))
        myyear = mydate.year
        mymonth = mydate.month
        myday = mydate.day
        w = csv.writer(f, dialect='excel')
        w.writerow(["Report period Beginning: ", str(mydate)])
        w.writerow(["Report period ends with current year."])
        w.writerow([" "])

        w.writerow(["Year: " + str(myyear)])
        w.writerow(["Month:" + str(month_list[mymonth-1])])
        w.writerow([" ", "Boat Class: " + str(boatclass)])
        w.writerow([" ", " ", "Sailplan ID", "Date", "Boat", "Purpose", "Name", "Hours", "Revenue"])
        #w.writerow([" "])
        
        # Set the totals to zero 
        #
        # hrs_purpose_month_total = 0
        # hrs_purpose_year_total = 0
        hrs_purpose_total = 0
        
        hrs_boat_month_total = 0
        hrs_boat_year_total = 0
        hrs_boat_total = 0
        
        hrs_class_month_total = 0
        hrs_class_year_total = 0
        hrs_class_total = 0

        hrs_month_total = 0
        hrs_year_total = 0
        
        hrs_grand_total = 0
        
        revenue_purpose_total = 0
        revenue_boat_total = 0
        revenue_class_total = 0
        revenue_month_total = 0
        revenue_year_total = 0
        revenue_grand_total = 0

        for record in usagetable:
            mydate = date.fromisoformat(str(record[3]))
            myrow = ([' ', ' ', 
                str(record[8]), 
                str(mydate), 
                str(record[1]), 
                str(record[7]),
                str(record[5]),
                str(round(record[9],1)), 
                str(round(record[10],2))])

            if (myspid == record[8] 
                    and boat == record[1] 
                    and boatclass == record[0] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear):

                # This is the case that simply lists the crew.
                
                hrs_purpose_total = record[9]
                #hrs_boat_total = record[9]
                #hrs_class_total = record[9]
                #hrs_month_total = record[9]
                #hrs_year_total = record[9]
                #hrs_grand_total = record[9]
                revenue_purpose_total += record[10]
                revenue_boat_total += record[10]
                revenue_class_total += record[10]
                revenue_month_total += record[10]
                revenue_year_total += record[10]
                revenue_grand_total += record[10]
                #
                w.writerow(myrow)
                #
            elif (myspid != record[8] 
                    and boat == record[1] 
                    and boatclass == record[0] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear):

                # This is the case for a new sail plan, so start over.

                #w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ", 
                    "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])

                boatpurpose = record[7]
                myspid = record[8]
                boat = record[1]
                boatclass = record[0]
                mymonth = mydate.month
                myyear = mydate.year
        
                hrs_purpose_total = record[9]
                hrs_boat_total += record[9]
                hrs_class_total += record[9]
                hrs_month_total += record[9]
                hrs_year_total += record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total += record[10]
                revenue_class_total += record[10]
                revenue_month_total += record[10]
                revenue_year_total += record[10]
                revenue_grand_total += record[10]
                
                w.writerow(myrow)
                #
            elif (boat != record[1] 
                    and boatclass == record[0] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear):
                #w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ", 
                    "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ",  " ", " ",
                    "Boat Subtotal:", 
                    str(round(hrs_boat_total,1)), 
                    str(round(revenue_boat_total, 2))])
                w.writerow([" "])
                
                boatpurpose = record[7]
                myspid = record[8]
                boat = record[1]
                boatclass = record[0]
                mymonth = mydate.month
                myyear = mydate.year
        
                w.writerow([" ", " ", "Sailplan ID", "Date", "Boat", "Purpose", "Name", "Hours", "Revenue"])
                
                hrs_purpose_total = record[9]
                hrs_boat_total = record[9]
                hrs_class_total += record[9]
                hrs_month_total += record[9]
                hrs_year_total += record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total = record[10]
                revenue_class_total += record[10]
                revenue_month_total += record[10]
                revenue_year_total += record[10]
                revenue_grand_total += record[10]
                #
                w.writerow(myrow)
                #
            elif (boatclass != record[0] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear):
                #w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ", 
                    "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Boat Subtotal:", 
                    str(round(hrs_boat_total,1)), 
                    str(round(revenue_boat_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Boat Class Total:", 
                    str(round(hrs_class_total,1)), 
                    str(round(revenue_class_total, 2))])
                w.writerow([" "])

                boatpurpose = record[7]
                myspid = record[8]
                boat = record[1]
                boatclass = record[0]
                mymonth = mydate.month
                myyear = mydate.year
        
                w.writerow([" ", "Boat Class: " + str(boatclass)])
                w.writerow([" ", " ", "Sailplan ID", "Date", "Boat", "Purpose", "Name", "Hours", "Revenue"])
        
                hrs_purpose_total = record[9]
                hrs_boat_total = record[9]
                hrs_class_total = record[9]
                hrs_month_total += record[9]
                hrs_year_total += record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total = record[10]
                revenue_class_total = record[10]
                revenue_month_total += record[10]
                revenue_year_total += record[10]
                revenue_grand_total += record[10]
                
                w.writerow(myrow)
        
            elif (mydate.month != mymonth 
                    and mydate.year == myyear):
                
                #w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Boat Subtotal:", 
                    str(round(hrs_boat_total,1)), 
                    str(round(revenue_boat_total, 2))])
                
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Boat Class Total:", 
                    str(round(hrs_class_total,1)), 
                    str(round(revenue_class_total, 2))])

                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Month Total:", 
                    str(round(hrs_month_total,1)), 
                    str(round(revenue_month_total, 2))])
                
                w.writerow([" "])

                boatpurpose = record[7]
                myspid = record[8]
                boat = record[1]
                boatclass = record[0]
                mymonth = mydate.month
                myyear = mydate.year
        
                w.writerow(["Month: " + str(month_list[mydate.month-1])])
                w.writerow([" ", "Boat Class: " + str(boatclass)])
                w.writerow([" ", " ", "Sailplan ID", "Date", "Boat", "Purpose", "Name", "Hours", "Revenue"])
        
                hrs_purpose_total = record[8]
                hrs_boat_total = record[8]
                hrs_class_total = record[8]
                hrs_month_total = record[8]
                hrs_year_total += record[8]
                hrs_grand_total += record[8]
                revenue_purpose_total = record[9]
                revenue_boat_total = record[9]
                revenue_class_total = record[9]
                revenue_month_total = record[9]
                revenue_year_total += record[9]
                revenue_grand_total += record[9]
                
                w.writerow(myrow)

            elif (mydate.year != myyear):
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Purpose Subsubtotal:", 
                    str(round(hrs_purpose_total,1)), 
                    str(round(revenue_purpose_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Boat Subtotal:", 
                    str(round(hrs_boat_total,1)), 
                    str(round(revenue_boat_total, 2))])
                w.writerow([" "])
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Boat Class Subotal:", 
                    str(round(hrs_class_total,1)), 
                    str(round(revenue_class_total, 2))])

                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Month Subtotal:", 
                    str(round(hrs_month_total,1)), 
                    str(round(revenue_month_total, 2))])
                
                w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
                    "Year Subtotal:", 
                    str(round(hrs_year_total,1)), 
                    str(round(revenue_year_total, 2))])
                
                w.writerow([" "])
                
                boatpurpose = record[7]
                myspid = record[8]
                boat = record[1]
                boatclass = record[0]
                mymonth = mydate.month
                myyear = mydate.year
        
                w.writerow(["Year: " + str(mydate.year)])
                w.writerow(["Month: " + str(month_list[mydate.month-1])])
                w.writerow([" ", "Boat Class: " + str(boatclass)])
                w.writerow([" ", " ", "Sailplan ID", "Date", "Boat", "Purpose", "Name", "Hours", "Revenue"])
        
                hrs_purpose_total = record[9]
                hrs_boat_total = record[9]
                hrs_class_total = record[9]
                hrs_month_total = record[9]
                hrs_year_total = record[9]
                hrs_grand_total += record[9]
                revenue_purpose_total = record[10]
                revenue_boat_total = record[10]
                revenue_class_total = record[10]
                revenue_month_total = record[10]
                revenue_year_total = record[10]
                revenue_grand_total += record[10]
                
                w.writerow(myrow)


        w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
            "Purpose Subsubtotal:", 
            str(round(hrs_purpose_total,1)), 
            str(round(revenue_purpose_total, 2))])
        w.writerow([" "])
        w.writerow([" ", " ", " ", " ", " ", " ", 
            "Boat Subtotal:", str(round(hrs_boat_total,1)), 
            str(round(revenue_boat_total, 2))])
        w.writerow([" "])

        w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
            "Boat Class Total:", str(round(hrs_class_total,1)), 
            str(round(revenue_class_total, 2))])
        w.writerow([" "])

        w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
            "Month Subtotal:", str(round(hrs_month_total,1)), 
            str(round(revenue_month_total, 2))])
        w.writerow([" "])

        w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
            "Year Subtotal:", str(round(hrs_year_total,1)), 
            str(round(revenue_year_total, 2))])
        w.writerow([" "])

        w.writerow([" ", " ", " ", " ", " ", " ", " ", " ",
            "Grand Total:", str(round(hrs_grand_total,1)), 
            str(round(revenue_grand_total, 2))])
        w.writerow([" "])

    db.commit()
    db.close()
    logger.info('Executed ReportDetailUse ')
    # messagebox.showinfo('', "Detailed Boat usage report in folder: " + reportpath)
    
def ReportSummaryUse():
    
    #####################################################################
    # 
    # This report reads the SailPlan table and summarizes utilization by 
    # month for the previous calendar year.  Each boat and boat type is
    # summarized with hours and revenues.
    #

    month_list = ['January', 'February', 'March',
                    'April', 'May', 'June', 
                    'July', 'August', 'September',
                    'October', 'November', 'December']

    reportpath = './Reports'
    
    myreportname = reportpath + '/' + ' Summary Utilization' + '.csv'

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
        
    c.execute("""SELECT Boats.boat_class AS boatclass, SailPlan.sp_sailboat as Sailboat, 
        SailPlan.sp_timeout AS sp_date, 
        SailPlan.sp_hours AS hours, SailPlan.sp_feesdue AS revenue, SailPlan.sp_id
        FROM SailPlan 
        JOIN Boats on SailPlan.sp_sailboat=Boats.boat_Name
        ORDER BY boatclass, Sailboat, SailPlan.sp_timeout
        """)    
    
    usagetable = c.fetchall()
        
    logger.info('Fetched data for Summary Use Report.')
    
    with open(myreportname, 'w', newline='') as f:
        firstrecord = usagetable[0]
        boatclass = firstrecord[0]
        boat = firstrecord[1]
        mydate = date.fromisoformat(str(firstrecord[2])[0:10])
        myyear = mydate.year
        mymonth = mydate.month
        
        # Set the totals to zero 
        #
        hrs_boat_month_total = 0
        hrs_boat_year_total = 0
        hrs_boat_total = 0
        
        rev_boat_month_total = 0
        rev_boat_year_total = 0
        rev_boat_total = 0

        hrs_class_month_total = 0
        hrs_class_year_total = 0
        hrs_class_total = 0

        rev_class_month_total = 0
        rev_class_year_total = 0
        rev_class_total = 0

        hrs_month_total = 0
        hrs_year_total = 0
        
        rev_month_total = 0
        rev_year_total = 0

        hrs_grand_total = 0
        rev_grand_total = 0        

        w = csv.writer(f, dialect='excel')
        
        w.writerow(["Summary Report"])
        w.writerow([" "])
        w.writerow(["Boat Class: " + str(boatclass)])
        w.writerow([" ", "Boat", "Year", "Month", "Hours", "Revenue"])
        
        for record in usagetable:
            mydate = date.fromisoformat(str(record[2])[0:10])
 #           myrow = ([' ', 
 #               str(record[1]), 
 #               str(mydate.year), 
 #               str(month_list[mydate.month-1]),
 #               str(round(record[3],1)), 
 #               str(round(record[4],2))])

            if (boatclass == record[0]      
                    and boat == record[1] 
                    and mydate.month == mymonth 
                    and mydate.year == myyear):

                hrs_boat_month_total += record[3]
                hrs_boat_year_total += record[3]
                hrs_boat_total += record[3]
                
                hrs_class_month_total += record[3]
                hrs_class_year_total += record[3]
                hrs_class_total += record[3]

                hrs_month_total += record[3]
                hrs_year_total += record[3]
                hrs_grand_total += record[3]

                rev_boat_month_total += record[4]
                rev_boat_year_total += record[4]
                rev_boat_total += record[4]

                rev_class_month_total += record[4]
                rev_class_year_total += record[4]
                rev_class_total += record[4]
                
                rev_month_total += record[4]
                rev_year_total += record[4]
                rev_grand_total += record[4]

#                w.writerow(myrow)

            elif (boatclass == record[0] 
                    and boat == record[1] 
                    and mydate.year == myyear
                    and mydate.month != mymonth):

                # This is the case for a new month, so start over.

                hrs_boat_year_total += record[3]
                hrs_boat_total += record[3]
                
                hrs_class_month_total = record[3]
                hrs_class_year_total += record[3]
                hrs_class_total += record[3]

                hrs_month_total = record[3]
                hrs_year_total += record[3]
                hrs_grand_total += record[3]

                rev_boat_year_total += record[4]
                rev_boat_total += record[4]

                rev_class_month_total = record[4]
                rev_class_year_total += record[4]
                rev_class_total += record[4]
                
                rev_month_total = record[4]
                rev_year_total += record[4]
                rev_grand_total += record[4]
                
                myrow = ([' ', 
                    str(boat), 
                    str(myyear), 
                    str(month_list[mymonth-1]),
                    str(round(hrs_boat_month_total,1)), 
                    str(round(rev_boat_month_total,2))])
                w.writerow(myrow)
                
                hrs_boat_month_total = record[3]
                rev_boat_month_total = record[4]
                
                boatclass = record[0]
                boat = record[1]
                mymonth = mydate.month
                myyear = mydate.year

            elif (boatclass == record[0] 
                    and boat == record[1] 
                    and mydate.year != myyear):

                # This is the case for a new year, so start over.

                hrs_boat_total += record[3]
                hrs_class_total += record[3]
                hrs_grand_total += record[3]
                rev_boat_total += record[4]
                rev_class_total += record[4]
                rev_grand_total += record[4]
                
                myrow = ([' ', 
                    str(boat), 
                    str(myyear), 
                    str(month_list[mymonth-1]),
                    str(round(hrs_boat_month_total,1)), 
                    str(round(rev_boat_month_total,2))])
                w.writerow(myrow)
                # w.writerow([" year change "])

                # myrow = ([' ', 
                #     str(boatclass) + " subtotal:", 
                #     str(myyear), 
                #     str(month_list[mymonth-1]),
                #     str(round(hrs_class_year_total,1)), 
                #     str(round(rev_class_year_total,2))])
                # w.writerow(myrow)

                w.writerow([str(boatclass), str(boat), str(myyear), "Subtotals:",
                    str(round(hrs_boat_year_total, 1)), 
                    str(round(rev_boat_year_total, 2))])
                
                w.writerow([" "])

                boatclass = record[0]
                boat = record[1]
                mymonth = mydate.month
                myyear = mydate.year
        
                hrs_boat_month_total = record[3]
                hrs_boat_year_total = record[3]
                rev_boat_month_total = record[4]
                rev_boat_year_total = record[4]
                hrs_class_month_total = record[3]
                hrs_class_year_total = record[3]
                hrs_month_total = record[3]
                hrs_year_total = record[3]
                rev_class_month_total = record[4]
                rev_class_year_total = record[4]
                rev_month_total = record[4]
                rev_year_total = record[4]
                

            elif (boat != record[1]
                    and boatclass == record[0]):

                # This is the case for a new boat, so start over.

                # w.writerow([" "])
                w.writerow([str(boatclass), str(boat), str(myyear), "Subtotals:",
                    str(round(hrs_boat_year_total, 1)), 
                    str(round(rev_boat_year_total, 2))])
                w.writerow([" "])

                w.writerow([str(boatclass), str(boat), " ", "Totals:",
                    str(round(hrs_boat_total,1)), 
                    str(round(rev_boat_total, 2))])
                w.writerow([" "])

                w.writerow([" ", "Boat", "Year", "Month", "Hours", "Revenue"])
        
                boatclass = record[0]
                boat = record[1]
                mymonth = mydate.month
                myyear = mydate.year
        
                hrs_boat_month_total = record[3]
                hrs_boat_year_total = record[3]
                hrs_boat_total = record[3]
                
                hrs_class_month_total = record[3]
                hrs_class_year_total = record[3]
                hrs_class_total += record[3]

                hrs_month_total = record[3]
                hrs_year_total = record[3]
                hrs_grand_total += record[3]

                rev_boat_month_total = record[4]
                rev_boat_year_total = record[4]
                rev_boat_total = record[4]

                rev_class_month_total = record[4]
                rev_class_year_total = record[4]
                rev_class_total += record[4]
                
                rev_month_total = record[4]
                rev_year_total = record[4]
                rev_grand_total += record[4]
                
                # myrow = ([' ', 
                #     str(boat), 
                #     str(myyear), 
                #     str(month_list[mymonth-1]),
                #     str(round(hrs_boat_month_total,1)), 
                #     str(round(rev_boat_month_total,2))])
                # w.writerow(myrow)
                
                
            elif (boatclass != record[0]):

                # This is the case for a new class, so start over.

                w.writerow([str(boatclass), str(boat), str(myyear), "Subtotals:",
                    str(round(hrs_boat_year_total, 1)), 
                    str(round(rev_boat_year_total, 2))])
                w.writerow([" "])

                w.writerow([str(boatclass), str(boat), " ", "Totals:",
                    str(round(hrs_boat_total,1)), 
                    str(round(rev_boat_total, 2))])
                w.writerow([" "])

                w.writerow([str(boatclass), " ", " ", 
                    "Class Total:",
                    str(round(hrs_class_total,1)), 
                    str(round(rev_class_total, 2))])
                w.writerow([" "])

                boatclass = record[0]
                boat = record[1]
                mymonth = mydate.month
                myyear = mydate.year
        
                w.writerow(["Boat Class: " + str(boatclass)])
                w.writerow([" ", "Boat", "Year", "Month", "Hours", "Revenue"])

                hrs_boat_month_total = record[3]
                hrs_boat_year_total = record[3]
                hrs_boat_total = record[3]
                
                hrs_class_month_total = record[3]
                hrs_class_year_total = record[3]
                hrs_class_total = record[3]

                hrs_month_total = record[3]
                hrs_year_total = record[3]
                hrs_grand_total += record[3]

                rev_boat_month_total = record[4]
                rev_boat_year_total = record[4]
                rev_boat_total = record[4]

                rev_class_month_total = record[4]
                rev_class_year_total = record[4]
                rev_class_total = record[4]
                
                rev_month_total = record[4]
                rev_year_total = record[4]
                rev_grand_total += record[4]
                
                # myrow = ([' ', 
                #     str(boat), 
                #     str(myyear), 
                #     str(month_list[mymonth-1]),
                #     str(round(hrs_boat_month_total,1)), 
                #     str(round(rev_boat_month_total,2))])
                # w.writerow(myrow)


        w.writerow([str(boatclass), str(boat), str(myyear), "Subtotals:",
            str(round(hrs_boat_year_total, 1)), 
            str(round(rev_boat_year_total, 2))])
        w.writerow([" "])

        w.writerow([str(boatclass), str(boat), " ", "Totals:",
            str(round(hrs_boat_total,1)), 
            str(round(rev_boat_total, 2))])
        w.writerow([" "])

        w.writerow([str(boatclass), " ", " ", 
            "Class Total:",
            str(round(hrs_class_total,1)), 
            str(round(rev_class_total, 2))])
        w.writerow([" "])

        w.writerow([" ", " ", " ",
            "Grand Total:", str(round(hrs_grand_total,1)), 
            str(round(rev_grand_total, 2))])
        w.writerow([" "])

    db.commit()
    db.close()
    logger.info('Executed ReportSummaryUse ')
    messagebox.showinfo('', "Summary Boat usage report in folder: " + reportpath)
    
def ReportMemberUse(mymonth, myyear):

    #######################################################
    #
    #   This function produces the Month - Year Usage - Members.csv file
    # 
    # 2022/6/7 -- Fixed summary by member to account for total bill so 
    #               that it sums to same value in the charges file
    #
    #

    d = datetime.date(day=1, month=mymonth, year=myyear)
    month_list = ['January', 'February', 'March',
                    'April', 'May', 'June', 
                    'July', 'August', 'September',
                    'October', 'November', 'December']    

    reportpath = './Reports/' + str(d.year)
    p = Path(reportpath) 

    if not Path(reportpath).exists():
        p.mkdir(parents=True)

    myreportname =  './Reports/' + str(d.year) +'/' + str(d.year) + ' ' + month_list[mymonth-1] + ' Fees Payable from Members' + '.csv'

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
        
    """CREATE TABLE Ledger (ledger_id int primary key,
        l_date text,
        l_member_id real,
        l_name text,
        l_skipper int,
        l_description text,
        l_mwrvol int,
        l_clubvol int,
        l_billto_id real,
        l_fee real,
        l_account text,
        l_sp_id int,
        l_uploaddate text);
    CREATE TABLE SailPlan (sp_id int primary key,
        sp_timeout text,
        sp_skipper_id real,
        sp_sailboat text,
        sp_purpose text,
        sp_description text,
        sp_estrtntime text,
        sp_timein text,
        sp_hours real,
        sp_feeeach real,
        sp_feesdue real,
        sp_mwrbilldue real,
        sp_billmembers int,
        sp_completed int);
    """

    c.execute("""SELECT l_date, sp_sailboat, l_member_id, l_name, 
        ledger_id, Sailplan.sp_purpose, SailPlan.sp_timeout, SailPlan.sp_timein, SailPlan.sp_hours, 
        l_fee, l_sp_id, l_billto_id
        FROM Ledger 
        JOIN SailPlan ON Ledger.l_sp_id=SailPlan.sp_id
        ORDER BY Ledger.l_date, Ledger.l_sp_id, Ledger.l_billto_id
        """)
        #
        # 6/7 removed this from the query: WHERE l_member_id != -1
        
        # Column assignments:
        # Date = 0 text
        # Boat = 1 text
        # Member ID = 2 int 
        # Member Name = 3 text
        # Ledger ID = 4 int
        # Description = 5 text
        # Time out = 6 text
        # Time in = 7 text
        # Hours = 8 real
        # fee = 9 real
        # sailplan ID = 10 int
        # bill to id = 11 int

    usagetable = c.fetchall()
        
    with open(myreportname, 'w', newline='') as f:
        w = csv.writer(f, dialect='excel')
        # These next 4 rows write the header to the report
        w.writerow(["Report period: ", month_list[mymonth-1], myyear])
        w.writerow([" "])
        w.writerow(["Sail Date", "Boat", "Bill to ID", "Member Name", "Ledger ID", "Purpose", 
            "Time Departed", "Time Returned", "Hours", "Member Fee"])
        w.writerow([" "])

        # pull the first record, then set the initial sail date, boat, membername, and timeout
        # the idea is to print a new line each time one of those change.  if timeout changes, 
        # then it's a new rental of the same boat.

        firstrecord = usagetable[0]
        firstreportrecord = 0 # not sure I remember what this does.

        saildate = firstrecord[0]
        boat = firstrecord[1]
        membername = firstrecord[3]
        timeout = firstrecord[6]
        
        # set the summing values in the report to zero, used for validation and summary reporting.
        member_hrs_grandtotal = 0
        member_bill_grandtotal = 0

        # now iterate through the entire list of records, create the row of data, and if
        # the record is for this month and year, then evaluate whether the date, boat or name
        # have changed, and then add the record's hours and/or fees to the summing values

        for record in usagetable:
            myrow = ([' ', ' ', 
                str(record[11]), 
                str(record[3]), 
                str(record[4]), 
                str(record[5]),
                str(record[6]), 
                str(record[7]), 
                str(round(record[8],1)), 
                str(round(record[9],2))])

            mydate = date.fromisoformat(str(record[0]))
            
            if (saildate == record[0] 
                    and boat == record[1] 
                    and membername == record[3] 
                    and timeout == record[6]
                    and mydate.month == mymonth and mydate.year == myyear):
                w.writerow(myrow)
                member_bill_grandtotal += record[9]
                
            elif (saildate == record[0] 
                    and boat == record[1] 
                    and membername != record[3] 
                    and timeout == record[6]
                    and mydate.month == mymonth and mydate.year == myyear):
                membername = record[3]
                member_bill_grandtotal += record[9]
                w.writerow(myrow)
            
            elif (saildate == record[0] 
                    and boat == record[1] 
                    and timeout != record[6]
                    and mydate.month == mymonth and mydate.year == myyear):
                boat = record[1]
                membername = record[3]
                w.writerow([" ", boat])
                member_hrs_grandtotal += record[8]
                member_bill_grandtotal += record[9]
                w.writerow(myrow)
            
            elif (saildate == record[0] 
                    and boat != record[1] 
                    and mydate.month == mymonth and mydate.year == myyear):
                boat = record[1]
                membername = record[3]
                timeout = record[6]
                w.writerow([" ", boat])
                member_hrs_grandtotal += record[8]
                member_bill_grandtotal += record[9]
                w.writerow(myrow)

            elif (saildate != record[0]
                    and mydate.month == mymonth and mydate.year == myyear):
                saildate = record[0]
                boat = record[1]
                membername = record[3]
                timeout = record[6]
                w.writerow([str(saildate)])
                member_hrs_grandtotal += record[8]
                member_bill_grandtotal += record[9]
                w.writerow([" ", boat])
                w.writerow(myrow)

        w.writerow([" "])
        w.writerow([" ", " ", " ", " ", " ", " ", " ", "Grand Total:", 
            str(round(member_hrs_grandtotal,1)), 
            str(round(member_bill_grandtotal, 2))])
        w.writerow([" "])

    db.commit()
    db.close()
    logger.info('Executed ReportMemberUse report.')
    return myreportname
    # messagebox.showinfo('', "Member Usage report in folder: " + reportpath)

def MemberUseLog(member_id):
    
    month_list = ['January', 'February', 'March',
                    'April', 'May', 'June', 
                    'July', 'August', 'September',
                    'October', 'November', 'December']    

    reportpath = './Reports/UserLogs'
    p = Path(reportpath) 

    if not Path(reportpath).exists():
        p.mkdir(parents=True)

    myreportname =  reportpath + '/UsageLog for ID - ' + str(member_id) + '.csv'

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
        
    """CREATE TABLE Ledger (ledger_id int primary key,
        l_date text,
        l_member_id real,
        l_name text,
        l_skipper int,
        l_description text,
        l_mwrvol int,
        l_clubvol int,
        l_billto_id real,
        l_fee real,
        l_account text,
        l_sp_id int,
        l_uploaddate text);
    CREATE TABLE SailPlan (sp_id int primary key,
        sp_timeout text,
        sp_skipper_id real,
        sp_sailboat text,
        sp_purpose text,
        sp_description text,
        sp_estrtntime text,
        sp_timein text,
        sp_hours real,
        sp_feeeach real,
        sp_feesdue real,
        sp_mwrbilldue real,
        sp_billmembers int,
        sp_completed int);
    """

    c.execute("""SELECT l_date, sp_sailboat, l_member_id, l_name, 
        ledger_id, Sailplan.sp_purpose, SailPlan.sp_timeout, SailPlan.sp_timein, SailPlan.sp_hours, 
        l_sp_id
        FROM Ledger 
        JOIN SailPlan ON Ledger.l_sp_id=SailPlan.sp_id
        WHERE l_member_id = :mid
        ORDER BY Ledger.l_date, Ledger.l_sp_id
        """, {'mid': member_id,})
        #
        # Column assignments:
        # Date = 0 text
        # Boat = 1 text
        # Member ID = 2 int
        # Member Name = 3 text
        # Ledger ID = 4 int
        # Description = 5 text
        # Time out = 6 text
        # Time in = 7 text
        # Hours = 8 real
        # sailplan ID = 9 int


    usagetable = c.fetchall()
        
    with open(myreportname, 'w', newline='') as f:
        firstrecord = usagetable[0]
        w = csv.writer(f, dialect='excel')
        w.writerow(["Report for member ID: ", str(member_id), "Name:", firstrecord[3]])
        w.writerow([" "])
        w.writerow(["Sail Date", "Boat", "Member ID", "Member Name", "Ledger ID", "Purpose", 
            "Time Departed", "Time Returned", "Hours"])
        w.writerow([" "])
        saildate = firstrecord[0]
        boat = firstrecord[1]
        membername = firstrecord[3]
    
        member_hrs_grandtotal = 0

        for record in usagetable:
            myrow = ([
                str(record[0]),
                str(record[1]), 
                str(record[2]), 
                str(record[3]), 
                str(record[4]), 
                str(record[5]),
                str(record[6]), 
                str(record[7]), 
                str(round(record[8],1))])

            w.writerow(myrow)
            member_hrs_grandtotal += record[8]

        w.writerow([" "])
        w.writerow([" ", " ", " ", " ", " ", " ", " ", "Grand Total:", 
            str(round(member_hrs_grandtotal,1))])
        w.writerow([" "])

    db.commit()
    db.close()
    logger.info('Executed MemberUseLog report.')
    messagebox.showinfo('', "MemberUseLog report in folder: " + reportpath)