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
    files.clear()
    with open(PASFILE, mode='r') as pasfile:    
            # Creates reader object
            csvreader=csv.DictReader(pasfile)
            for ids in csvreader:
                files.append(ids)


# Initializes the curses screen
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.clear()

def steelbox():
    reloadFiles()
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

    while True:
        termGlobals()
        reloadFiles()
        displayItems()
        stdscr.move(0, 0)
        command()


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
            passPswd = randString()
        # wtf = write to file
        wtf = {'service' : passService, 'user' : passUser, 'pswd' : passPswd}
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
    # Extracts the file to be modified
    modFile = files[GLOBAL_CURSOR]
    # Removes it from the main file
    files.pop(GLOBAL_CURSOR)
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
    if passPswd == '':
        passPswd = randString()
    modFile = {'service' : passService, 'user' : passUser, 'pswd' : passPswd}
    files.insert(GLOBAL_CURSOR, modFile)
    with open(PASFILE, mode='w') as pasfile:
        # Creates writer object and writes to the csv file
        csvwriter = csv.DictWriter(pasfile, fields)
        csvwriter.writeheader()
        csvwriter.writerows(files)
    reloadFiles()


def delFile():
    dlWin = curses.newwin(3, 22, int(TERM_LINES/2), int(TERM_COLS/2))
    dlWin.border()
    dlWin.refresh()
    STATUS_MESSAGE = "Delete " + displayList[GLOBAL_CURSOR] + "?"
    displayStatus(STATUS_MESSAGE)
    dlWin.addstr(1, 1, "Are you sure? (y/N)")
    c = dlWin.getch()
    if c == ord('y'):
        files.pop(GLOBAL_CURSOR)
        with open(PASFILE, mode='w') as pasfile:
            csvwriter = csv.DictWriter(pasfile, fields)
            csvwriter.writeheader()
            csvwriter.writerows(files)
        reloadFiles()
    


# Opens a new window with a random string of length 45
def rwin():
    ranWin = curses.newwin(3, 49, int(TERM_LINES/2), int(TERM_COLS/2))
    ranWin.border()
    ranWin.addstr(0, 1, "Random string")
    ranWin.addstr(1, 1, randString())
    ranWin.refresh()
    ranWin.getch()


# Copies password to clipboard
def copy():
    if len(files) > 0:
        pc.copy(files[GLOBAL_CURSOR]['pswd'])
        STATUS_MESSAGE = "Copied password for " + files[GLOBAL_CURSOR]['service']
        displayStatus(STATUS_MESSAGE)
        mainwin.getch()



# Cleans the windows
def cleanWins():
    mainwin.clear()
    statuswin.clear()
    mainwin.border()
    statuswin.border()
    mainwin.addstr(0, 1, "SteelBox V" + str(version))
    mainwin.refresh()
    statuswin.refresh()



# Displays the items on the screen properly
def displayItems():
    cleanWins()
    global NROWS
    global ITEM_CURSOR
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
    STATUS_MESSAGE = "(n)ew,(d|el),(c)opy,(m)odify,(h)elp,(q)uit"
    displayStatus(STATUS_MESSAGE)
    mainwin.refresh()


# Displays on the status window
def displayStatus(msg):
    statuswin.border()
    statuswin.addstr(0,0, msg)
    statuswin.refresh()

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
def randString():
    result = ''
    for _ in range(45):
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