#!/usr/bin/env python
import curses
import os
import sys
from xml.dom.minidom import parse

#########################################
##                                     ##
##     Skrevet af Poul Kalff           ##
##       Juli - August, 2009           ##
##          Februar, 2012              ##
##                                     ##
#########################################

# --- Variabler ----------------------------------------------------------------------------------

x = 0
X = 1
SystemNr = 0
dontrun = 0
Systems = [' Arcade', ' Amiga ', '  C64  ']    # Name of the systems
Systems_exec = ['mame', 'e-uae', 'x64']        # Executables of the systems
GameList = [[], [], []]

# --- Class / Funktions --------------------------------------------------------------------------


class GameInst():
    Navn = ''
    Sti1 = ''
    Sti2 = ''
    Sti3 = ''
    Sti4 = ''
    System = ''


def compare(a, b):
        return cmp(a.Navn, b.Navn)


def DisplaySystems(Object, Nr):
    if Nr == 0:
        Object.addstr(33, 33, "-----------------------------------", curses.color_pair(3))
        Object.addstr(34, 35, Systems[1], curses.color_pair(3))
        Object.addstr(34, 47, Systems[0], curses.color_pair(4))
        Object.addstr(34, 59, Systems[2], curses.color_pair(3))
        Object.addstr(35, 33, "-----------------------------------", curses.color_pair(3))
        Object.addstr(36, 0, "")
    if Nr == 1:
        Object.addstr(33, 33, "-----------------------------------", curses.color_pair(3))
        Object.addstr(34, 35, Systems[2], curses.color_pair(3))
        Object.addstr(34, 47, Systems[1], curses.color_pair(4))
        Object.addstr(34, 59, Systems[0], curses.color_pair(3))
        Object.addstr(35, 33, "-----------------------------------", curses.color_pair(3))
        Object.addstr(36, 0, "")
    if Nr == 2:
        Object.addstr(33, 33, "-----------------------------------", curses.color_pair(3))
        Object.addstr(34, 35, Systems[0], curses.color_pair(3))
        Object.addstr(34, 47, Systems[2], curses.color_pair(4))
        Object.addstr(34, 59, Systems[1], curses.color_pair(3))
        Object.addstr(35, 33, "-----------------------------------", curses.color_pair(3))
        Object.addstr(36, 0, "")


def DisplaySelected(System, Spil):  # Bruges ikke, til test
    screen.clear()
    screen.addstr(7, 30, "Spil Nr     : " + str(System))
    screen.addstr(8, 30, "Systems Nr  : " + str(Spil))
    screen.addstr(9, 30, "Spil        : " + GameList[System][Spil].Navn)
    screen.addstr(10, 30, "Systems     : " + GameList[System][Spil].System)
    screen.addstr(11, 30, "Sti         : " + GameList[System][Spil].Sti)
    screen.refresh()


def RunGame(System, Spil):
    Game = GameList[System][Spil]
    if System == 0:  # Hvis Arcade
        Command = Systems_exec[System] + ' -inipath . ' + Game.Sti1
    elif System == 1:    # Hvis Amiga
        Command = Systems_exec[System] + " -0 " + Game.Sti1
        if Game.Sti2 != '':
            Command += " -1 " + Game.Sti2
        if Game.Sti3 != '':
            Command += " -2 " + Game.Sti3
        if Game.Sti4 != '':
            Command += " -3 " + Game.Sti4
    elif System == 2:  # Hvis C64
        Command = Systems_exec[System] + " -autostart " + Game.Sti1
        if Game.Sti2 != '':
            Command += " -8 " + Game.Sti2
    # ----------- Start Process -----------
    if dontrun:
        print()
        print(Command)
        sys.exit()
    Handle = os.popen(Command, 'r')
    Handle.readlines()
    # ----------- Start Process -----------


def SortXml(Path):
    # Sorterer pt. kun paa system
    file_ind = open(Path, 'r')
    xml_ud = '<collection>\n'
    SortParser = parse(file_ind)
    file_ind.close()
    for Game in SortParser.getElementsByTagName('game'):
        if Game.getElementsByTagName('system')[0].childNodes[0].nodeValue == 'Amiga':
            xml_ud += "  " + Game.toxml() + '\n'
    for Game in SortParser.getElementsByTagName('game'):
        if Game.getElementsByTagName('system')[0].childNodes[0].nodeValue == 'Arcade':
            xml_ud += "  " + Game.toxml() + '\n'
    for Game in SortParser.getElementsByTagName('game'):
        if Game.getElementsByTagName('system')[0].childNodes[0].nodeValue == 'C64':
            xml_ud += "  " + Game.toxml() + '\n'
    for Game in SortParser.getElementsByTagName('game'):
        if Game.getElementsByTagName('system')[0].childNodes[0].nodeValue == 'WHDLoad':
            xml_ud += "  " + Game.toxml() + '\n'
    xml_ud += '</collection>\n'
    file_ud = open(Path, 'w')
    file_ud.write(xml_ud)
    file_ud.close()


def TestPaths(Path):
    rom_liste = []
    xml_fil = open(Path, 'r')
    for line in xml_fil:
        if '<rompath' in line:
            rom_liste.append(line.split('<')[1].split('>')[1])
    print()
    print(('Found ', len(rom_liste), ' rom paths in file "games.xml"'))
    eval(input('Press <return> to test these paths'))
    print()
    print('-------------------------------------------------------------------------------------')
    for x in rom_liste:
        if os.path.exists(x):
            print(("Fandt '" + x + "'"))
        else:
            print(("----->'" + x + "' MANGLER!"))
    print('-------------------------------------------------------------------------------------')
    print()

# --- Main Program -------------------------------------------------------------------------------

if len(sys.argv) > 1:                          # Checker commandline options
    if sys.argv[1] == '-dontrun':
        dontrun = 1  # Dont run game, but show command to run it
    elif sys.argv[1] == '-test':
        TestPaths('games.xml')
        print('Done testing!')
        print()
        sys.exit()
    elif sys.argv[1] == '-sort':
        SortXml('games.xml')
        print('Done sorting!')
        print()
        sys.exit()
    else:
        print()
        print(("   Unknown option '" + sys.argv[1] + "'"))
        print("   Format is './conjurer_curses.py [ test | sort | dontrun ]'")
        print()
        sys.exit('Quiting due to unknown parameter...')

# Sorter spil fra XML ud i tre lister:
GamesParser = parse('../xml/all.xml')
for Game in GamesParser.getElementsByTagName('game'):  # Count the games
    New = GameInst()
    try:
        New.Navn = str(Game.getElementsByTagName('name')[0].childNodes[0].nodeValue)
        New.System = str(Game.getElementsByTagName('system')[0].childNodes[0].nodeValue)
        New.Sti1 = str(Game.getElementsByTagName('rompath1')[0].childNodes[0].nodeValue)
        New.Sti2 = str(Game.getElementsByTagName('rompath2')[0].childNodes[0].nodeValue)
        New.Sti3 = str(Game.getElementsByTagName('rompath3')[0].childNodes[0].nodeValue)
        New.Sti4 = str(Game.getElementsByTagName('rompath4')[0].childNodes[0].nodeValue)
    except:
        pass
    if New.System == 'Arcade':
        GameList[0].append(New)
    elif New.System == 'Amiga' or New.System == 'WHDLoad':
        GameList[1] .append(New)
    elif New.System == 'C64':
        GameList[2] .append(New)
GameList[0].sort(compare)
GameList[1].sort(compare)
GameList[2].sort(compare)
Pointer = (len(GameList[SystemNr]) / 2) - 16

# Start en screen op
screen = curses.initscr()
screen.border(0)
curses.noecho()
curses.start_color()
curses.curs_set(0)
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)


while 1:
    screen.clear()
    for Entry in range(31):
        if Entry + Pointer < 0 or Entry + Pointer > (len(GameList[SystemNr]) - 1):
            GameToWrite = ""
        else:
            GameToWrite = GameList[SystemNr][Entry + Pointer].Navn
        XPos = 50 - (len(GameToWrite) / 2)
        if Entry != 16:
            screen.addstr(Entry + 2, XPos, GameToWrite, curses.color_pair(2))
        else:
            screen.addstr(Entry + 2, XPos, GameToWrite, curses.color_pair(1))
    DisplaySystems(screen, SystemNr)
#        screen.addstr(1, 5, str(x)) # Will display the latest input code to top left of screen
    screen.refresh()
    x = screen.getch()
    # --- Keyboard Inputs ---
    if x == 66:           # Cursor DOWN
        if Pointer + Entry < len(GameList[SystemNr]) + 13:
            Pointer += 1
    if x == 65:           # Cursor UP
        if Pointer > -16:
            Pointer -= 1
    if x == 109:          # Keypress 'n' = Cursor UP x 10
        Pointer += 10
        if Pointer + Entry > len(GameList[SystemNr]) - 14:
            Pointer = (len(GameList[SystemNr]) + 20) - Entry
    if x == 112:          # Keypress 'p' = Cursor DOWN x 10
        Pointer -= 10
        if Pointer < -16:
            Pointer = -16
    if x == 68:           # Cursor LEFT
        if SystemNr < 2:
            SystemNr += 1
        else:
            SystemNr = 0
        Pointer = (len(GameList[SystemNr]) / 2) - 16
    if x == 67:           # Cursor RIGHT
        if SystemNr > 0:
            SystemNr -= 1
        else:
            SystemNr = 2
        Pointer = (len(GameList[SystemNr]) / 2) - 16
    if x == 10:           # Return (Select)
        RunGame(SystemNr, Entry + Pointer - 14)
      #  DisplaySelected(SystemNr, Entry + Pointer - 8)
    if x == 113:          # Keypress 'Q' = End Application
        # Set everything back to normal
        screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        sys.exit('\n\nThe program was terminated normally by user\n\n')  # sys.exit,to leave loop



