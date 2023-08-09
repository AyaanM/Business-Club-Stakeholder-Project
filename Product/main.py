'''
title: Deca Member Tracker
author: Ayaan Merchant
date-created: 2021-06-14
'''

import sqlite3
import pathlib
from tabulate import tabulate # need to install prior to running
import sys

### --- VARIABLES --- ###
FILE = "Product/CurrentMembers.csv" # access file from the product folder
DB_FILE = "Product/deca_tracker.db" # create file in the product folder
FIRST_RUN = True

if (pathlib.Path.cwd() / DB_FILE).exists(): # checks if the file with DB's already exists
    FIRST_RUN = False

CONNECTION = sqlite3.connect(DB_FILE)
CURSOR = CONNECTION.cursor()

### --- SUBROUTINES --- ###
def startScreen():
    '''
    shows starting text
    :return: None
    '''
    print('Welcome to the DECA Member Tracker')

## INPUTS
def checkInt(NUM):
    '''
    checks if NUM is a number and converts to int
    :param NUM: (str) user input
    :return: (int) user input converted to integer
    '''
    if NUM.isnumeric():
        NUM = int(NUM)
        return NUM
    else:
        print('Enter a number please')
        NEW_NUM = input("> ")
        return checkInt(NEW_NUM)

def checkFloat(NUM):
    '''
    tries to convert NUM to float
    :param NUM: (str) user input
    :return: (float) user input converted to float
    '''
    try:
        NUM = float(NUM)
        return NUM
    except ValueError:
        print("This should be a number or decimal")
        NEW_NUM = input("> ")
        return checkFloat(NEW_NUM)

# DB creation
def readData(FILENAME):
    '''
    read data from CSV file and extract into 2D array
    :param FILENAME: the CSV file to be read
    :return: (list) 2D array of data
    '''
    FILE = open(FILENAME)
    CONTENT = FILE.readlines()
    FILE.close()

    # sanitize array
    for i in range(len(CONTENT)):
        CONTENT[i] = CONTENT[i].rstrip() # removes \n at the end
        CONTENT[i] = CONTENT[i].split(",")

    # remove headings
    CONTENT.pop(0)

    # change datatype to meet DB constraints
    for i in range(len(CONTENT)):
        CONTENT[i][0] = int(CONTENT[i][0]) # ID
        CONTENT[i][2] = int(CONTENT[i][2]) # grade
        CONTENT[i][6] = float(CONTENT[i][6])  # money_owed

    return CONTENT

def createMemberDB(DATA):
    '''
    create member info database and import DATA from CSV
    :param DATA: (list) 2D array of data to import
    :return: None
    '''
    global CURSOR, CONNECTION

    # create DB
    CURSOR.execute('''
        CREATE TABLE
            members(
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                grade INTEGER NOT NULL,
                status TEXT NOT NULL,
                email TEXT NOT NULL,
                registered_paid TEXT NOT NULL,
                money_owed FLOAT NOT NULL,
                payment_method TEXT NOT NULL
                )
    ;''')

    # import data
    for i in range(len(DATA)):
        CURSOR.execute('''
            INSERT INTO
                members
            VALUES(
                ?, ?, ?, ?, ?, ?, ?, ?
                ) 
        ;''', DATA[i])

    CONNECTION.commit()

def createAttendanceDB():
    '''
    create database to take member attendance and import IDs
    :return: None
    '''
    global CURSOR, CONNECTION

    # create DB
    CURSOR.execute('''
        CREATE TABLE
            attendance(
                id INTEGER NOT NULL PRIMARY KEY,
                sep TEXT,
                oct TEXT,
                nov TEXT,
                dec TEXT,
                jan TEXT,
                feb TEXT,
                mar TEXT,
                apr TEXT,
                may TEXT,
                jun TEXT
                )
    ;''')
    # months are nullable so if any member joins after a meeting has taken place, no error will occur

    # import ID's from member DB
    CURSOR.execute('''
            INSERT INTO 
                attendance (id)
            SELECT
                id
            FROM
                members
        ;''')

    CONNECTION.commit()

# menus & submenus
def menu():
    '''
    take user input on step to perform
    :return: (int) user input
    '''
    print('''
Choose From the Options Below
1. View Member Database
2. View Attendance Database
3. Exit
    ''')
    CHOICE = input("> ")
    CHOICE = checkInt(CHOICE)
    if CHOICE < 1 or CHOICE > 3:
        print('Enter a number from the menu')
        return menu()
    else:
        return CHOICE

def member_submenu():
    '''
    take input from user on what to do about members
    :return: (int) user input
    '''
    print('''
Choose From the Options Below
1. Add Member
2. Remove Member
3. Edit Member
4. Return to Main Menu
5. Exit
    ''')
    CHOICE = input("> ")
    CHOICE = checkInt(CHOICE)
    if CHOICE < 1 or CHOICE > 5:
        print('Enter a number from the menu')
        return member_submenu()
    else:
        return CHOICE

def attendance_submenu():
    '''
    take input from user on what to do about attendance
    :return: (int) user input
    '''
    print('''
Choose From the Options Below
1. Take attendance
2. Return to Main Menu
3. Exit
        ''')
    CHOICE = input("> ")
    CHOICE = checkInt(CHOICE)
    if CHOICE < 1 or CHOICE > 3:
        print('Enter a number from the menu')
        return attendance_submenu()
    else:
        return CHOICE

# member information inputs
def getID():
    '''
    get the member ID and check if it exists or not
    :return: (int) ID, (list) of info tied with the ID
    '''
    ID = input("What is the member ID? ")
    ID = checkInt(ID)

    # get info tied with ID
    INFO = CURSOR.execute(''' 
        SELECT
            *
        FROM
            members
        WHERE
            id = ?
    ;''', [ID]).fetchone()
    # if INFO = None, ID dosen't exist

    return ID, INFO

def newMemberInfo(ID):
    '''
    get info on the new member to be added
    :param ID: (int) member ID
    :return: (list) of new member info
    '''
    NAME = input("New Member Name > ")
    GRADE = checkInt(input("New Member Grade > "))
    STATUS = input("New Member Club Status > ")

    # get username and convert to email by adding domain
    USERNAME = input("New Member EPSB Username > ")
    EMAIL = USERNAME + "@share.epsb.ca"

    REGISTERED_PAID = input("Has the member registered and paid? ")

    MONEY_OWED = checkFloat(input("Money Owed By New Member ($) > "))

    PAYMENT_METHOD = input("Payment Method > ")

    INPUTS = [ID, NAME, GRADE, STATUS, EMAIL, REGISTERED_PAID, MONEY_OWED, PAYMENT_METHOD]

    # check if inputs null or not to meet DB constraints
    for i in range(len(INPUTS)):
        if INPUTS[i] == "":
            print("One or more pieces of information missing, please enter information again")
            return newMemberInfo(ID)

    return INPUTS

def existingMemberInfo(MEMBER):
    '''
    get new info for the existing member
    :param MEMBER: (list) of current info for existing member
    :return: (list) of new info for existing member
    '''
    print("Leave field blank for no changes, NOTE: Member ID can't be changed")
    NAME = input(f"New Name ({MEMBER[1]}) > ")

    GRADE = input(f"New Grade ({MEMBER[2]}) > ")
    if GRADE != "":
        GRADE = checkInt(GRADE)

    STATUS = input(f"New Club Status ({MEMBER[3]}) > ")

    # get username and convert to email
    CURRENT_USERNAME = MEMBER[4].replace("@share.epsb.ca", "") # replace domain with empty string to convert email to username
    USERNAME = input(f"New EPSB Username ({CURRENT_USERNAME}) > ")
    if USERNAME != "":
        EMAIL = USERNAME + "@share.epsb.ca"
    else:
        EMAIL = ""

    REGISTERED_PAID = input(f"Has the member registered and paid? ({MEMBER[5]}) ")

    MONEY_OWED = input(f"Money Owed By Member ($) ({MEMBER[6]}) > ")
    if MONEY_OWED != "":
        MONEY_OWED = checkFloat(MONEY_OWED)

    PAYMENT_METHOD = input(f"Payment Method ({MEMBER[7]}) > ")

    INPUTS = [NAME, GRADE, STATUS, EMAIL, REGISTERED_PAID, MONEY_OWED, PAYMENT_METHOD]
    NEW_INFO = []

    # change empty string to current member info since no change to info
    for i in range(len(INPUTS)):
        if INPUTS[i] != "":
            NEW_INFO.append(INPUTS[i])
        else:
            NEW_INFO.append(MEMBER[i + 1])

    # append ID at the end to tell database to edit ID row
    NEW_INFO.append(MEMBER[0])

    return NEW_INFO

# attendance taking inputs
def getMeet():
    '''
    get the meeting that attendance should be taken for
    :return: (str) meet month
    '''

    MEETS = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "June"]

    # display meeting months
    NUMBER = 1
    print("Choose from options below for the meet attendance is being taken for")
    for i in range(len(MEETS)):
        print(f"{NUMBER}. {MEETS[i]}")
        NUMBER = NUMBER + 1

    MEETING = input("> ")
    MEETING = checkInt(MEETING)
    if MEETING > 10 or MEETING < 1:
        print("Choose from the options below: ")
        return getMeet()

    # change user input to meet so it's understandable by DB
    for i in range(len(MEETS)):
        if MEETING == i + 1:
            MEETING = MEETS[i]
    MEETING = MEETING.lower()  # make meet lowercase

    return MEETING

def takeattendance():
    '''
    print out members one by one asking if attended
    :return: list of attendance for meet
    '''
    global CURSOR

    # join both DB's to get member name and ID
    MEMBERS = CURSOR.execute('''
        SELECT
            attendance.id,
            members.name
        FROM
            attendance
        JOIN
            members
        ON
            attendance.id = members.id
    ;''').fetchall()

    ATTENDANCE_LIST = []

    for i in range(len(MEMBERS)):
        ATTENDED = input(f"Did {MEMBERS[i][1]} attend today's meeting? Y/n ")
        if ATTENDED == "" or ATTENDED == 'y':
            ATTENDED = "Y"
        elif ATTENDED == "n":
            ATTENDED = 'N'
        ATTENDANCE_LIST.append([ATTENDED, MEMBERS[i][0]])

    return ATTENDANCE_LIST

## PROCESSING
# member specific processes
def addMember(INFO):
    '''
    using data from INFO add new member
    :param INFO: (list) of data for new member
    :return: None
    '''
    global CURSOR, CONNECTION

    # add to memberDB
    CURSOR.execute('''
        INSERT INTO 
            members(
                id,
                name,
                grade,
                status,
                email,
                registered_paid,
                money_owed,
                payment_method
                )
        VALUES(
            ?, ?, ?, ?, ?, ?, ?, ?
            )
    ;''', INFO)

    # add ID to attendanceDB
    CURSOR.execute('''
           INSERT INTO
               attendance(
                   id
                   )
               VALUES(
                   ?
                   )
       ;''', [INFO[0]])

    CONNECTION.commit()

def removeMember(ID):
    '''
    remove the member using ID
    :param ID: (str) ID of member to remove
    :return: None
    '''
    global CURSOR, CONNECTION

    # remove ID from memberDB
    CURSOR.execute('''
        DELETE FROM
            members
        WHERE
            id = ?
    ;''', [ID])

    # remove ID from attendanceDB
    CURSOR.execute('''
        DELETE FROM
            attendance
        WHERE
            id = ?
    ;''', [ID])

    CONNECTION.commit()

def editMember(NEW_INFO):
    '''
    using NEW_INFO edit the member
    :param NEW_INFO: (list) of new info for existing member
    :return: None
    '''
    global CURSOR, CONNECTION

    # update memberDB
    CURSOR.execute('''
           UPDATE
               members
           SET
                name = ?,
                grade = ?,
                status = ?,
                email = ?,
                registered_paid = ?,
                money_owed = ?,
                payment_method = ?
           WHERE
               id = ?
       ;''', NEW_INFO)

    # attendance table not updated since ID does not change

    CONNECTION.commit()

# attendance specific processes
def addAttendance(ATTENDANCE, MEET):
    '''
    adds ATTENDANCE to table in specific MEET
    :param ATTENDANCE: (list) 2D array of attendance tied with member ID
    :param MEET: (str) DB column to add attendance to
    :return: None
    '''
    global CURSOR, CONNECTION

    # for each member in 2D array add attendance
    for i in range(len(ATTENDANCE)):
        CURSOR.execute(f'''
            UPDATE
                attendance
            SET
                {MEET} = ?
            WHERE
                id = ?
        ;''', ATTENDANCE[i])

## OUTPUTS
def memberDB():
    '''
    extract information and display the member database
    :return: None
    '''
    global CURSOR

    # extract data
    MEMBERS = CURSOR.execute('''
        SELECT
            *
        FROM
            members
    ;''').fetchall()

    # table columns (needed for tabulate table)
    COLUMNS = ["ID", "Name", "Grade", "Club Status", "Email", "Registered/Paid", "Money Owed ($)", "Payment Method"]

    # display extracted data
    print(tabulate(MEMBERS, headers=COLUMNS, tablefmt='fancy_grid'))

def attendanceDB():
    '''
    join the member and attendance databases and display attendance database
    :return: None
    '''
    global CURSOR

    # join both DB's (to get member name since that needs to be displayed)
    ATTENDANCE = CURSOR.execute('''
        SELECT
            attendance.id,
            members.name,
            sep,
            oct,
            nov,
            dec,
            jan,
            feb,
            mar,
            apr,
            may,
            jun
        FROM
            attendance
        JOIN
            members
        ON
            attendance.id = members.id
    ;''').fetchall()

    COLUMNS = ["ID", "Name", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "June"]

    print(tabulate(ATTENDANCE, headers=COLUMNS, tablefmt='fancy_grid'))

## MAIN PROGRAM SUBROUTINE
def main():
    '''
    subroutine to run everything in the program (helps easily restart program when needed)
    :return: None
    '''
    CHOICE = menu()

    ## member database functions
    if CHOICE == 1:
        memberDB()
        SUB_CHOICE = member_submenu() # get input on what to do
        # add new member
        if SUB_CHOICE == 1:
            ID, INFO = getID()
            if INFO == None:
                MEMBER_INFO = newMemberInfo(ID)
                addMember(MEMBER_INFO)
                print(f"Successfully added {MEMBER_INFO[1]}")
                main()
            else:
                print(f"Member with ID {ID} already exists!")
                main() # "restarts" program
        # remove existing member
        elif SUB_CHOICE == 2:
            ID, INFO = getID()
            if INFO != None:
                removeMember(ID)
                print(f"Successfully deleted {ID}")
                main()
            else:
                print(f"Member with ID {ID} doesn't exist!")
                main()
        # edit existing member
        elif SUB_CHOICE == 3:
            ID, INFO = getID()
            if INFO != None:
                NEW_INFO = existingMemberInfo(INFO)
                editMember(NEW_INFO)
                print(f"Successfully edited {NEW_INFO[0]}")
                main()
            else:
                print(f"Member with ID {ID} doesn't exist!")
                main()
        # restart program
        elif SUB_CHOICE == 4:
            main()
        # exit subroutine to exit program
        else:
            return
    ## attendance database functions
    elif CHOICE == 2:
        attendanceDB()
        SUB_CHOICE = attendance_submenu() # get input on what to do
        # take attendance
        if SUB_CHOICE == 1:
            MEETING = getMeet()
            ATTENDANCE = takeattendance()
            addAttendance(ATTENDANCE, MEETING)
            print("Successfully taken attendance!")
            main()
        # restart program
        elif SUB_CHOICE == 2:
            main()
        # exit subroutine to exit program
        else:
            return
    ## exit subroutine to exit program
    else:
        return


### --- MAIN PROGRAM CODE --- ###
if FIRST_RUN:
    CONTENT = readData(FILE)
    createMemberDB(CONTENT)
    createAttendanceDB()
startScreen()
main()
sys.exit()



