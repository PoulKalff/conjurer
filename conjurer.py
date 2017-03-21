#!/usr/bin/env python
from conjurerClasses import *
from conjurerFunctions import getCommandlineOptions, TestPaths, SortXml
from conjurerMain import Conjurer

# --- Main ----------------------------------------------------------------------

version = 1.13
cmd_options = getCommandlineOptions()

# Laeg det her over i en separat fil....
if cmd_options.scrape:
    scraper = Scraper()
    list = scraper.getList('xml/games.xml', 'Arcade')
    gamesTgdb = []
    gamesMoby = []
    print
    print "  Checking thegamesdb.net for " + str(len(list)) + " games:"
    print '  -------------------------------------------------------------'
    for game in list:
        x = scraper.findGame_tgdb(game, "Arcade")
        if x != {}:
            gamesTgdb.append(x)
    print '  -------------------------------------------------------------'
    print
    print "  Checking mobygames for " + str(len(list)) + " games:"
    print '  -------------------------------------------------------------'
    for game in list:
        x = scraper.findGame_moby(game, 143)
        if x != {}:
            gamesMoby.append(x)
    print '  -------------------------------------------------------------'
    print
    print "TheGamesDB", len(gamesTgdb)
    print "MobyGames", len(gamesMoby)


    sys.exit('Scraping done!\n')
elif cmd_options.sortXML:
    SortXml()
    sys.exit('\n  Done sorting!\n  Sorted data was wwritten to "xml/games_sorted.xml"\n')
elif cmd_options.testPaths:
    TestPaths()
    sys.exit('Done testing!\n')
elif cmd_options.version:
    print '\n\n   Conjurer Version is', str(version)
    sys.exit('\n')
elif cmd_options.dontRun:
    dontrun = True

# start main program
print
conjurer_handle = Conjurer(cmd_options)

print '\nApplication terminated. "./conjurer.py" will restart it\n'




