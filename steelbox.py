import csv
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import os
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


# Initializes Curses' screen
def main(stdscr):
    # Opens password file
    with open(PASFILE, mode='r') as pasfile:    
        # Creates reader and writer objects
        csvreader=csv.DictReader(pasfile)
        for ids in csvreader:
            files.append(ids)
    ## Initializes color pairs
    # Password pallete (Foreground = Background)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
    pwd_pallete = curses.color_pair(1)
    # Main window pallete
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    main_pallete = curses.color_pair(2)

    # Clears screen
    stdscr.clear()
    # Determines terminal size
    global TERM_LINES
    TERM_LINES=curses.LINES - 1
    if TERM_LINES <= 15:
        sys.exit("ERROR: Your terminal is too small!")
    global TERM_COLS
    TERM_COLS=curses.COLS - 1 
    if TERM_COLS <=60:
        sys.exit("ERROR: Your terminal is too small!")
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



    # Initializes the main window
    mainwin = curses.newwin(TERM_LINES -1, TERM_COLS, 0, 0)
    mainwin.keypad(True)
    mainwin.bkgd(' ', main_pallete)
    mainwin.clear()

    # Initializes the bottom window
    statusWin = curses.newwin(3, TERM_COLS, TERM_LINES, 0)
    statusWin.keypad(True)
    statusWin.border()
    statusWin.bkgd(' ', main_pallete)
    statusWin.clear()


    while True:
        # Creates a name list
        displayList = []

        # This makes sure the cursor stays on the screen TODO: delete this
        if ITEM_CURSOR < 0: ITEM_CURSOR = 0
        if ITEM_CURSOR > MAX_ITEMS or ITEM_CURSOR > len(files)-1: ITEM_CURSOR = 0

        # Makes sure the windows are properly clean
        mainwin.clear()
        statusWin.clear()
        mainwin.border()
        mainwin.addstr(0, 1, "SteelBox V" + str(version))
        mainwin.refresh()
        statusWin.border()
        statusWin.refresh()
        # Reset global necessities
        LINE = 0
        COLUMN = 0
        currItem = 0
        highOpt = ()
        # Defines what to display
        startDisplay = (CURR_PAGE-1)*MAX_ITEMS
        stopDisplay = CURR_PAGE*MAX_ITEMS

        # Appends the names in the CSV to display on the main window
        for ps_name in files:
            displayList.append(ps_name['service'][:15])
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
        mainwin.refresh()
        STATUS_MESSAGE = "cmds: PrvPage(F1),NxtPage(F2),(q)uit,(e)xmn,(n)ew"
        statusWin.addstr(0,0, STATUS_MESSAGE)
        statusWin.refresh()


        ## Command logic
        # The GLOBAL_CURSOR points to the main files object, so that it gets the right file.
        global c
        c = mainwin.getch()
        if c == ord('q'):
            return(0)       
        elif c == curses.KEY_DOWN:
            if GLOBAL_CURSOR < len(files):
                ITEM_CURSOR+=1
                GLOBAL_CURSOR+=1
        elif c == curses.KEY_UP:
            if GLOBAL_CURSOR > 0:
                ITEM_CURSOR-=1
                GLOBAL_CURSOR-=1
        elif c == curses.KEY_RIGHT:
            if CUROW < NROWS:
                ITEM_CURSOR+=MAX_LINES - 1
                GLOBAL_CURSOR+=MAX_LINES - 1
                CUROW+=1
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
        
        # For some reason, KEY_UP is 10, instead of the 343 the debbuger flags... Welp ¯\_(ツ)_/¯
        elif c == 10 or c == curses.KEY_ENTER or c == ord('e'):
            # highOpt = Coordinates of the first option's character
            LINE = highOpt[0]
            COLUMN = highOpt[1]
            # These if statements make it so files being shown will always do so inside the terminal screen
            if COLUMN+32 > TERM_COLS:
                COLUMN-=int(TERM_COLS/MAX_ROWS)
            if LINE+10 > TERM_LINES:
                LINE-=10
            # Initializes the file viewer window
            fileWin = curses.newwin(5, 40, LINE+5, COLUMN)
            # Clears the window
            fileWin.clear()
            fileWin.border()

            passService = files[GLOBAL_CURSOR]['service'][:45]
            passUser = files[GLOBAL_CURSOR]['user'][:45]
            passPswd = files[GLOBAL_CURSOR]['pswd'][:45]
            fileWin.addstr(0, 1, "View Password")
            fileWin.addstr(1, 1, "SRVC: " + passService)
            fileWin.addstr(2, 1, "NAME: " + passUser)
            fileWin.addstr(3, 1, "PSWD: " + passPswd)
            statusWin.clear()
            STATUS_MESSAGE = "cmds:(d|DEL)ete "
            statusWin.addstr(0,0, STATUS_MESSAGE)
            statusWin.refresh()
            fileWin.refresh()
            # Gets command to act on the highlighted file
            c = fileWin.getch()
            if c == ord('d') or c == curses.KEY_DC:
                dlWin = curses.newwin(3, 22, int(TERM_LINES/2), int(TERM_COLS/2))
                dlWin.border()
                dlWin.refresh()
                statusWin.clear()
                STATUS_MESSAGE = "Delete " + displayList[GLOBAL_CURSOR] + "?"
                statusWin.addstr(0,0, STATUS_MESSAGE)
                statusWin.refresh()
                dlWin.addstr(1, 1, "Are you sure? (y/N)")
                c = dlWin.getch()
                if c == ord('y'):
                    files.pop(GLOBAL_CURSOR)
                    with open(PASFILE, mode='r+') as pasfile:
                        csvwriter = csv.DictWriter(pasfile, fields)
                        csvwriter.writeheader()
                        csvwriter.writerows(files)

            

        elif c == ord('n'):
            # Initializes the 'new password' window
            npWin = curses.newwin(5, 52,int(TERM_LINES/2)-2, int(TERM_COLS/2)-18)
            nwCord = npWin.getbegyx()
            # Initializes the windows in which the textboxes will reside for input
            svWin = curses.newwin(1, 45, nwCord[0]+1, nwCord[1]+6)
            svBox = Textbox(svWin)
            usWin = curses.newwin(1, 45, nwCord[0]+2, nwCord[1]+6)
            usBox = Textbox(usWin)
            psWin = curses.newwin(1, 45, nwCord[0]+3, nwCord[1]+6)
            psBox = Textbox(psWin)
            
            # Clears the 'new password' window
            npWin.clear()
            npWin.border()

            npWin.addstr(0, 1, "New password")
            npWin.addstr(1, 1, "SRVC:")
            npWin.addstr(2, 1, "USER:")
            npWin.addstr(3, 1, "PSWD:")
            STATUS_MESSAGE = "CTRL+G to enter, Leave any empty to cancel, MAX 45 CHARS"
            statusWin.addstr(0,0, STATUS_MESSAGE)
            statusWin.refresh()
            npWin.refresh()

            # Takes data
            svBox.edit()
            passService = svBox.gather()
            usBox.edit()
            passUser = usBox.gather()
            psBox.edit()
            passPswd = psBox.gather()

            if passService != '' and passUser != '' and passPswd != '':
                # wtf = write to file
                wtf = {'service' : passService, 'user' : passUser, 'pswd' : passPswd}
                files.append(wtf)
                with open(PASFILE, mode='r+') as pasfile:
                    csvwriter = csv.DictWriter(pasfile, fields)
                    csvwriter.writeheader()
                    csvwriter.writerows(files)    


wrapper(main)