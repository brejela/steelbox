# Steelbox, the password manager for your terminal.
# Full license inside the manual at doc/
# Copyright (C) 2022 Kamal Curi
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PUR-
# POSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Founda-
# tion, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.
# You can contact the developer by sending an email to kamalcuri@outlook.com

import csv
import curses
from curses.textpad import Textbox
import sys
import os
import pyperclip as pc
import random

version = sys.argv[1]

## Initialization of bottomline dependencies

# Array of names
files = []

# Make sure these are defined as global

# CSV fields
fields = ["service", "user", "pswd"]

# Password file
HOMEDIR = os.environ['HOME']
PASFILE=HOMEDIR+"/.pasfile.csv"

def reloadFiles():
    global SQUERY
    files.clear()
    with open(PASFILE, mode='r') as pasfile:    
            # Creates reader object
            csvreader=csv.DictReader(pasfile)
            if SQUERY == '':
                for ids in csvreader:
                    files.append(ids)
            else:
                for ids in csvreader:
                    if ids['service'].find(SQUERY) != -1:
                        files.append(ids)



# Initializes the curses screen
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.clear()

def init():
    # Initializes the main window
    global mainwin 
    mainwin = curses.newwin(TERM_LINES -1, TERM_COLS, 0, 0)
    mainwin.keypad(True)
    mainwin.border()

    # Initializes the bottom window
    global statuswin 
    statuswin= curses.newwin(3, TERM_COLS, TERM_LINES, 0)
    statuswin.keypad(True)
    statuswin.border()
    cleanWins()


def populate():
    wtf = {'service' : 'ServiceExample', 'user' : 'UserExample', 'pswd' : randString(45)}
    files.append(wtf)
    with open(PASFILE, mode='w') as pasfile:
        csvwriter = csv.DictWriter(pasfile, fields)
        csvwriter.writeheader()
        csvwriter.writerows(files)
    reloadFiles()

# Main function
def steelbox():
    reloadFiles()
    init()

    while True:
        termGlobals()
        reloadFiles()
        if len(files) < 1 and SQUERY == '':
            populate()
        displayItems()
        stdscr.move(0, 0)
        command()

# Displays the items on the screen properly
def displayItems():
    cleanWins()
    global NROWS
    global ITEM_CURSOR
    global SQUERY
    # Creates a name list
    global displayList
    displayList = []
    # Appends the names in the CSV to display on the main window
    for ps_name in files:
        displayList.append(ps_name['service'][:15])

    # Reset global necessities
    LINE = 0
    COLUMN = 0
    currItem = 0
    NROWS = 0
    global highOpt
    highOpt = ()
    # Defines what to display
    startDisplay = (CURR_PAGE-1)*MAX_ITEMS
    stopDisplay = CURR_PAGE*MAX_ITEMS

    for item in displayList[startDisplay:stopDisplay]:
        # If the item is the one with the cursor, highlight it
        if currItem == ITEM_CURSOR:
            mode = curses.A_REVERSE
            highOpt = mainwin.getyx()
        else:
            mode = curses.A_NORMAL
        mainwin.addstr(1 + LINE, 1 + COLUMN, item, mode)
        LINE+=1
        currItem+=1
        if LINE >= WINLIMIT:
            LINE = 0
            COLUMN+=16
            NROWS+=1
    STATUS_MESSAGE = "(n)ew,(d|el),(s)earch,(c)opy,(m)odify,(h)elp,(q)uit"
    displayStatus(STATUS_MESSAGE)
    mainwin.refresh()

# Defines global variables
def globals():
    ## Global variables
    # Determines terminal size
    global TERM_LINES
    TERM_LINES=curses.LINES - 1
    if TERM_LINES <= 20:
        close("ERROR: Your terminal is too small!")
    global TERM_COLS
    TERM_COLS=curses.COLS - 1 
    if TERM_COLS <=80:
        close("ERROR: Your terminal is too small!")
    # Global (program-wide) variables for cursor position
    global LINE
    LINE = 0
    global COLUMN
    COLUMN = 0
    # Hard limit for the main window
    global WINLIMIT
    WINLIMIT = TERM_LINES - 3
    # Maximum amount of colums displayable on the main window, considering the terminal size
    global MAX_ROWS
    MAX_ROWS = int(TERM_COLS/17)
    # Maximum amount of lines (All lines, minus border and terminal break)
    global MAX_LINES
    MAX_LINES = TERM_LINES - 2
    # Maximum amount of items a given terminal space is able to display
    global MAX_ITEMS
    MAX_ITEMS = MAX_ROWS*MAX_LINES
    # Specifies what item to highlight
    global ITEM_CURSOR
    ITEM_CURSOR = 0
    # Defines the current page
    global CURR_PAGE
    CURR_PAGE = 1
    # Defines the amount of pages needed to house all files within the terminal space
    global MAX_PAGES
    MAX_PAGES = int(len(files)/MAX_ITEMS)
    # In case there are less passwords than the amount available in the first page
    if MAX_PAGES < 1: MAX_PAGES = 1
    # Status bar message
    global STATUS_MESSAGE
    STATUS_MESSAGE = ""
    # Global pointer for the cursor's item
    global GLOBAL_CURSOR
    GLOBAL_CURSOR = 0
    # How many rows are displayed in the window
    global NROWS
    NROWS = 0
    # What row the cursor is in
    global CUROW
    CUROW = 0
    global PSERV
    PSERV = ""
    global PUSER
    PUSER = ""
    global PPSWD
    PPSWD = ""
    global SQUERY
    SQUERY = ""

# This makes sure that if anyone resizes the terminal window, it won't be smaller than the maximum size
def termGlobals():
    global TERM_LINES
    TERM_LINES=curses.LINES - 1
    if TERM_LINES <= 20:
        close("ERROR: Your terminal is too small!")
    global TERM_COLS
    TERM_COLS=curses.COLS - 1 
    if TERM_COLS <=80:
        close("ERROR: Your terminal is too small!")

# Gets user command
def command():
    # This solution, for the case where the search function finds nothing, is cursed beyond belief,
    global displayList
    if len(displayList) < 1:
        noMatch()
        return()
    # The GLOBAL_CURSOR points to the main files object, so that it gets the right file.
    global c
    global CUROW
    global ITEM_CURSOR
    global GLOBAL_CURSOR
    global CURR_PAGE
    c = mainwin.getch()
    if c == ord('q'):
        close()       
    elif c == curses.KEY_DOWN:
        if GLOBAL_CURSOR < len(files) - 1:
            ITEM_CURSOR+=1
            GLOBAL_CURSOR+=1
    elif c == curses.KEY_UP:
        if GLOBAL_CURSOR > 0:
            ITEM_CURSOR-=1
            GLOBAL_CURSOR-=1
    elif c == curses.KEY_RIGHT:
        if CUROW < NROWS and (ITEM_CURSOR + MAX_LINES) < len(files) - 1:
            ITEM_CURSOR+=MAX_LINES - 1
            GLOBAL_CURSOR+=MAX_LINES - 1
            CUROW+=1
        else:
            ITEM_CURSOR = len(files) - 1
            GLOBAL_CURSOR = len(files) - 1
            if CUROW < NROWS:
                CUROW+=1
            else:
                CUROW = NROWS
    elif c == curses.KEY_LEFT:
        if CUROW > 0:
            ITEM_CURSOR-=MAX_LINES - 1
            GLOBAL_CURSOR-=MAX_LINES - 1
            CUROW-=1
    elif c == curses.KEY_F1 or c == curses.KEY_PPAGE:
        # The next two IF statements are here to avoid unintended GLOBAL_CURSOR changes
        if CURR_PAGE > 1:
            CURR_PAGE-=1
            GLOBAL_CURSOR-=MAX_ITEMS
    elif c == curses.KEY_F2 or c == curses.KEY_NPAGE:
        if CURR_PAGE < MAX_PAGES:
            CURR_PAGE+=1
            GLOBAL_CURSOR+=MAX_ITEMS
    elif c == 10 or c == curses.KEY_ENTER or c == ord('e'):
        examine()
    elif c == ord('c') or c == curses.KEY_F3:
        copy()
    elif c == ord('s') or c == curses.KEY_F6:
        searchWin()
    elif c == ord('n') or c == curses.KEY_F4:
        newFile()
    elif c == ord('m') or c == curses.KEY_F5:
        modFile()
    elif c == ord('d') or c == curses.KEY_DC:
        delFile()
    elif c == ord('r'):
        rwin()
    elif c == ord('h'):
        sbhelp()
    # This avoids the program crashing when resizing the terminal
    elif c == curses.KEY_RESIZE:
        y, x = stdscr.getmaxyx()
        stdscr.clear()
        curses.resize_term(y, x)
        cleanWins()
        globals()
        init()

def newFile():
    # Initializes the 'new password' window
    npWin = curses.newwin(5, 60,int(TERM_LINES/2)-2, int(TERM_COLS/2)-18)
    nwCord = npWin.getbegyx()
    # Initializes the windows in which the textboxes will reside for input
    svWin = curses.newwin(1, 45, nwCord[0]+1, nwCord[1]+6)
    svBox = Textbox(svWin)
    usWin = curses.newwin(1, 45, nwCord[0]+2, nwCord[1]+6)
    usBox = Textbox(usWin)
    psWin = curses.newwin(1, 45, nwCord[0]+3, nwCord[1]+6)
    psBox = Textbox(psWin)
    
    # Clears the 'new password' window
    npWin.border()
    npWin.border()
    npWin.addstr(0, 1, "New password")
    npWin.addstr(1, 1, "SRVC:")
    npWin.addstr(2, 1, "USER:")
    npWin.addstr(3, 1, "PSWD:")
    npWin.refresh()

    # Takes data
    STATUS_MESSAGE = "Enter the service name - LEAVE EMPTY TO CANCEL"
    displayStatus(STATUS_MESSAGE)
    svBox.edit()
    passService = svBox.gather()
    STATUS_MESSAGE = "Enter the username - LEAVE EMPTY TO CANCEL"
    displayStatus(STATUS_MESSAGE)
    usBox.edit()
    passUser = usBox.gather()
    STATUS_MESSAGE = "Enter the password- LEAVE EMPTY FOR RANDOM STRING"
    displayStatus(STATUS_MESSAGE)
    psBox.edit()
    passPswd = psBox.gather()
    if passService != '' and passUser != '':
        if passPswd == '':
            passPswd = randString(45)
        elif passPswd[0] == ':':
            if len(passPswd) < 3:
                pSize = 45
            elif len(passPswd) == 3:
                if str.isnumeric(passPswd[1]):
                    pSize = int(passPswd[1])
                else:
                    pSize = 45
            else:
                if str.isnumeric(passPswd[1:3]):
                    pSize = int(passPswd[1:3])
                else:
                    pSize = 45
            if pSize > 45:
                pSize = 45
            passPswd = randString(pSize)
        # wtf = write to file
        wtf = {'service' : passService[:45], 'user' : passUser[:45], 'pswd' : passPswd[:45]}
        files.append(wtf)
        with open(PASFILE, mode='w') as pasfile:
            csvwriter = csv.DictWriter(pasfile, fields)
            csvwriter.writeheader()
            csvwriter.writerows(files)
        reloadFiles()
    

def examine():
    # highOpt = Coordinates of the first option's character
    LINE = highOpt[0]
    COLUMN = highOpt[1]
    # These if statements make it so files being shown will always do so inside the terminal screen
    if COLUMN+32 > TERM_COLS:
        COLUMN-=int(TERM_COLS/MAX_ROWS)
    if LINE+10 > TERM_LINES:
        LINE-=10
    # Initializes the file viewer window
    fileWin = curses.newwin(5, 60, LINE+5, COLUMN)
    # Clears the window
    fileWin.border()
    fileWin.border  
    passService = files[GLOBAL_CURSOR]['service'][:45]
    passUser = files[GLOBAL_CURSOR]['user'][:45]
    passPswd = files[GLOBAL_CURSOR]['pswd'][:45]
    fileWin.addstr(0, 1, "View Password")
    fileWin.addstr(1, 1, "SRVC: " + passService)
    fileWin.addstr(2, 1, "NAME: " + passUser)
    fileWin.addstr(3, 1, "PSWD: " + passPswd)
    STATUS_MESSAGE = "(d|el),(c)opy,(m)odify"
    displayStatus(STATUS_MESSAGE)
    # Gets command to act on the highlighted file
    c = fileWin.getch()
    if c == ord('d') or c == curses.KEY_DC:
        delFile()
    elif c == ord('m'):
        modFile()
    elif c == ord('c') or c == curses.KEY_F3:
        copy()

def modFile():
    global files
    # Extracts the file to be modified
    modFile = files[GLOBAL_CURSOR]
    # Creates the 'modify password' window
    modWin = curses.newwin(5, 60,int(TERM_LINES/2)-2, int(TERM_COLS/2)-18)
    # Gets the coordinates for the top left corner of said window
    nwCord = modWin.getbegyx()
    # Creates the fields in which the password will be edited
    svWin = curses.newwin(1, 46, nwCord[0]+1, nwCord[1]+6)
    svWin.addstr(0, 0, modFile['service'])
    svWin.move(0, 0)
    svBox = Textbox(svWin)
    usWin = curses.newwin(1, 46, nwCord[0]+2, nwCord[1]+6)
    usWin.addstr(0, 0, modFile['user'])
    usWin.move(0, 0)
    usBox = Textbox(usWin)            
    psWin = curses.newwin(1, 46, nwCord[0]+3, nwCord[1]+6)
    psWin.addstr(0, 0, modFile['pswd'])
    psWin.move(0, 0)
    psBox = Textbox(psWin)

    # Clears the 'modify password' window
    modWin.border()
    modWin.border
    modWin.addstr(0, 1, "Modify password")
    modWin.addstr(1, 1, "SRVC:")
    modWin.addstr(2, 1, "USER:")
    modWin.addstr(3, 1, "PSWD:")
    modWin.refresh()
    svWin.refresh()
    usWin.refresh()
    psWin.refresh()

    # Takes data
    STATUS_MESSAGE = "Edit SERVICE field - CTRL+G to enter, leave empty to cancel, MAX 45 CHARS"
    displayStatus(STATUS_MESSAGE)
    svBox.edit()
    passService = svBox.gather()
    STATUS_MESSAGE = "Edit USER field - CTRL+G to enter, leave empty to cancel, MAX 45 CHARS"
    displayStatus(STATUS_MESSAGE)
    usBox.edit()
    passUser = usBox.gather()
    STATUS_MESSAGE = "Edit PASSWORD field - CTRL+G to enter, leave empty for random string"
    displayStatus(STATUS_MESSAGE)
    psBox.edit()
    passPswd = psBox.gather()
    if passService != '' and passUser != '':
        if passPswd == '':
            passPswd = randString(45)
        elif passPswd[0] == ':':
            if len(passPswd) < 3:
                pSize = 45
            elif len(passPswd) == 3:
                if str.isnumeric(passPswd[1]):
                    pSize = int(passPswd[1])
                else:
                    pSize = 45
            else:
                if str.isnumeric(passPswd[1:3]):
                    pSize = int(passPswd[1:3])
                else:
                    pSize = 45
            if pSize > 45:
                pSize = 45
            passPswd = randString(pSize)
    modFile = {'service' : passService[:45], 'user' : passUser[:45], 'pswd' : passPswd[:45]}
    # This is just a copy of delfile's confirmation routine
    dlWin = curses.newwin(3, 22, int(TERM_LINES/2), int(TERM_COLS/2))
    dlWin.border()
    dlWin.refresh()
    STATUS_MESSAGE = "Modify " + displayList[GLOBAL_CURSOR] + "?"
    displayStatus(STATUS_MESSAGE)
    dlWin.addstr(1, 1, "Are you sure? (y/N)")
    c = dlWin.getch()
    if c == ord('y'):
        iCount = 0
        with open(PASFILE, mode='r') as pasfile:
            oldFiles = []
            csvreader = csv.DictReader(pasfile)
            for ids in csvreader:
                oldFiles.append(ids)
            for ids in oldFiles:
                if ids['service'] == files[GLOBAL_CURSOR]['service'] and ids['user'] == files[GLOBAL_CURSOR]['user'] and ids['pswd'] == files[GLOBAL_CURSOR]['pswd']:
                    oldFiles.pop(iCount)
                    iPos = iCount            
                iCount += 1 
            oldFiles.insert(iPos, modFile)
            files = oldFiles
        with open(PASFILE, mode='w') as pasfile:
            csvwriter = csv.DictWriter(pasfile, fields)
            csvwriter.writeheader()
            csvwriter.writerows(files)
        reloadFiles()


def delFile():
    global GLOBAL_CURSOR
    global ITEM_CURSOR
    global files
    dlWin = curses.newwin(3, 22, int(TERM_LINES/2), int(TERM_COLS/2))
    dlWin.border()
    dlWin.refresh()
    STATUS_MESSAGE = "Delete " + displayList[GLOBAL_CURSOR] + "?"
    displayStatus(STATUS_MESSAGE)
    dlWin.addstr(1, 1, "Are you sure? (y/N)")
    c = dlWin.getch()
    if c == ord('y'):
        iCount = 0
        with open(PASFILE, mode='r') as pasfile:
            oldFiles = []
            csvreader = csv.DictReader(pasfile)
            for ids in csvreader:
                oldFiles.append(ids)
            for ids in oldFiles:
                if ids['service'] == files[GLOBAL_CURSOR]['service'] and ids['user'] == files[GLOBAL_CURSOR]['user'] and ids['pswd'] == files[GLOBAL_CURSOR]['pswd']:
                    oldFiles.pop(iCount)
                iCount += 1 
            files = oldFiles
        with open(PASFILE, mode='w') as pasfile:
            csvwriter = csv.DictWriter(pasfile, fields)
            csvwriter.writeheader()
            csvwriter.writerows(files)
        reloadFiles()
    if GLOBAL_CURSOR > 0:
        GLOBAL_CURSOR -= 1
        ITEM_CURSOR -= 1
    


# Opens a new window with a random string of length 45
def rwin():
    ranWin = curses.newwin(3, 49, int(TERM_LINES/2), int(TERM_COLS/2))
    ranWin.border()
    ranWin.addstr(0, 1, "Random string")
    ranWin.addstr(1, 1, randString(45))
    ranWin.refresh()
    ranWin.getch()


# Copies password to clipboard
def copy():
    if len(files) > 0:
        pc.copy(files[GLOBAL_CURSOR]['pswd'])
        STATUS_MESSAGE = "Copied password for " + files[GLOBAL_CURSOR]['service']
        displayStatus(STATUS_MESSAGE)
        mainwin.getch()

def searchWin():
    global STATUS_MESSAGE
    global TERM_LINES
    global TERM_COLS
    global SQUERY
    global ITEM_CURSOR
    global GLOBAL_CURSOR
    searchWin = curses.newwin(3, 49, int(TERM_LINES/2), int(TERM_COLS/2))
    searchWin.border()
    searchWin.addstr(0, 1, "Search service")
    winPosY = searchWin.getbegyx()[0]
    winPosX = searchWin.getbegyx()[1]
    swin = curses.newwin(1, 45, winPosY + 1, winPosX + 1)
    sbox = Textbox(swin)
    STATUS_MESSAGE = "Type in service name"
    displayStatus(STATUS_MESSAGE)
    searchWin.refresh()
    sbox.edit()
    SQUERY = sbox.gather()
    l = len(SQUERY)
    SQUERY = SQUERY[:l-1]
    ITEM_CURSOR = 0
    GLOBAL_CURSOR = 0


def noMatch():
    global SQUERY
    nomwin = curses.newwin(3, 40, int(TERM_LINES/2), int(TERM_COLS/2))
    nomwin.border()
    nomwin.addstr(1, 1, "No passwords match the search criteria")
    SQUERY = ''
    nomwin.getch()


# Cleans the windows
def cleanWins():
    stdscr.clear()
    mainwin.clear()
    statuswin.clear()
    mainwin.border()
    statuswin.border()
    mainwin.addstr(0, 1, "SteelBox V" + str(version))
    mainwin.refresh()
    statuswin.refresh()

# Displays on the status window
def displayStatus(msg):
    statuswin.border()
    statuswin.addstr(0,0, msg)
    statuswin.refresh()

# Displays the help file
def sbhelp():
    helpwin = curses.newwin(TERM_LINES - 1, TERM_COLS - 1, 0, 0)
    helpwin.border()
    helpwin.addstr(1, 1, "Steelbox V." + version)
    line = 2
    with open("/opt/sbhelp", mode='r') as sbhfile:
        sbh = sbhfile.readlines()
        for lines in sbh:
            helpwin.addstr(line, 1, lines)
            line+=1
    line+=1
    helpwin.addstr(line, 1, "PRESS ANY KEY TO CONTINUE", curses.A_REVERSE)
    helpwin.getch()

# Returns a random string of length 45
def randString(size):
    result = ''
    for _ in range(size):
        ascNum = random.randint(33, 126)
        if ascNum == 32:
            ascNum += random.randint(1, 10)
        result += chr(ascNum)
    return(result)

# Finishes the application
def close(error = ''):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    sys.exit(error)

globals()
steelbox()
close()