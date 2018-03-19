import os, sys
from pygame import image, joystick as js
from optparse import OptionParser
from xml.dom.minidom import parse
from conjurerClasses import GameInfo


def getJoystick():
    """ Returns list of supported, initiated joysticks, if any """
    joysticks = []
    for j in range(0, js.get_count()):
        joystick = js.Joystick(j)
        if joystick.get_name().startswith('ShanWan Gamepad '):  # Should work with any joystick, but untested!
            joystick.init()
            joysticks.append(joystick)
    print "Found", len(joysticks), "supported joysticks!"
    return joysticks


def SortGames(mp):
    # Sorter spil fra XML:
    _gamedict = {}
    _xmlPath = os.path.join('xml', 'games.xml')
    if not os.path.isfile(_xmlPath):
        sys.exit('The file "' + _xmlPath + '" was not found...')
    _gamesparser = parse(_xmlPath)
    for Game in _gamesparser.getElementsByTagName('game'):
        _gameinstance = GameInfo()
        _gameinstance.Navn =    str(Game.getElementsByTagName('name')[0].childNodes[0].nodeValue)
        _gameinstance.System =  str(Game.getElementsByTagName('system')[0].childNodes[0].nodeValue)
        _gameinstance.Paths =   str(Game.getElementsByTagName('rompath')[0].childNodes[0].nodeValue).split('; ')
        _gameinstance.Players = str(Game.getElementsByTagName('players')[0].childNodes[0].nodeValue)
        _tempScreenPath = str(Game.getElementsByTagName('screenpath')[0].childNodes[0].nodeValue)
        _gameinstance.Screen = image.load(_tempScreenPath).convert()
        if mp and int(_gameinstance.Players) == 1:
            pass
        else:
            if _gamedict.has_key(_gameinstance.System):
                _gamedict[_gameinstance.System].append(_gameinstance)
            else:
                _gamedict[_gameinstance.System] = [_gameinstance]
    for _inst in _gamedict.iterkeys():
        _gamedict[_inst].sort(lambda a,b: cmp(a.Navn,b.Navn))
    return _gamedict


def getCommandlineOptions():
    # Gets and handles commandline options
    _parser = OptionParser()
    _parser.add_option('-x', '--scrape', action='store_true', dest='scrape', default=False, help='NOT IMPLEMENTED! Tries to find gfx for games online')
    _parser.add_option('-d', '--dontrun', action='store_true', dest='dontRun', default=False, help='Do not run the chosen game, instead show all info about running it')
    _parser.add_option('-t', '--testpaths', action='store_true', dest='testPaths', default=False, help='Test paths in XML-file')
    _parser.add_option('-s', '--sortxml', action='store_true', dest='sortXML', default=False, help='Sort entries in the XML-file')
    _parser.add_option('-l', '--locked', action='store_true', dest='locked', default=False, help='Lock program to only display Arcade Games')
    _parser.add_option('-v', '--version', action='store_true', dest='version', default=False, help='Show program versiom')
    _parser.add_option('-r', '--rungame', action='store', dest='runGame', default=False, help='Run emulator <EmulatorNo> with <gameNo> as Conjurer starts', nargs=2)
    _parser.add_option('-m', '--multiplayer', action='store_true', dest='mpGames', default=False, help='Show only games with two or more players')
    _options, _args = _parser.parse_args()
    return _options


def SortXml():
    """ Sorts all games acording to System, then Name, alphabetical """
    _gamedict = {}
    xml_ud = '<collection>\n'
    _xmlPath = os.path.join('xml', 'games.xml')
    if not os.path.isfile(_xmlPath):
        sys.exit('The file "' + _xmlPath + '" was not found...')
    _gamesparser = parse(_xmlPath)
    for Game in _gamesparser.getElementsByTagName('game'):
        _gameinstance = GameInfo()
        _gameinstance.Navn =       str(Game.getElementsByTagName('name')[0].childNodes[0].nodeValue)
        _gameinstance.System =     str(Game.getElementsByTagName('system')[0].childNodes[0].nodeValue)
        _gameinstance.Paths =      str(Game.getElementsByTagName('rompath')[0].childNodes[0].nodeValue)
        _gameinstance.Players =    str(Game.getElementsByTagName('players')[0].childNodes[0].nodeValue)
        _gameinstance.ScreenPath = str(Game.getElementsByTagName('screenpath')[0].childNodes[0].nodeValue)
        if _gamedict.has_key(_gameinstance.System):
            _gamedict[_gameinstance.System].append(_gameinstance)
        else:
            _gamedict[_gameinstance.System] = [_gameinstance]
    for _inst in _gamedict.iterkeys():
        _gamedict[_inst].sort(lambda a,b: cmp(a.Navn,b.Navn))
    # Writing to new file
    for system in ['Amiga', 'Arcade', 'C64']:
        for game in _gamedict[system]:
            xml_ud += '  <game>\n'
            xml_ud += '    <name>' + game.Navn + '</name>\n'
            xml_ud += '    <system>' + game.System + '</system>\n'
            xml_ud += '    <players>' + game.Players + '</players>\n'
            xml_ud += '    <rompath>' + game.Paths + '</rompath>\n'
            xml_ud += '    <screenpath>' + game.ScreenPath + '</screenpath>\n'
            xml_ud += '  </game>\n'
    xml_ud += '</collection>\n'
    file_ud = open('xml/games_sorted.xml', 'w')
    file_ud.write(xml_ud)
    file_ud.close()


def TestPaths():
    # Loads all values from conjurer's XML-files and verifies their validity
    counter = 0
    rom_liste = []
    screen_liste = []
    xml_fil = open('xml/games.xml', 'r')
    for line in xml_fil:
        if '<rompath' in line:
            rom_liste.append(line.split('<')[1].split('>')[1])
        if '<screenpath' in line:
            screen_liste.append(line.split('<')[1].split('>')[1])
    print
    print 'Found ', len(rom_liste), ' rom paths in file "games.xml"'
    print 'Found ', len(screen_liste), ' screenshot paths in file "games.xml"'
    raw_input('Press <return> to test these paths')
    print
    print '-------------------------------------------------------------------------------------------'
    for x in rom_liste:
        y = x.split(';')
        for z in y:
            if not os.path.exists(z.strip()):
                counter += 1
                print "----->'" + z.strip() + "' MANGLER!"
    for x in screen_liste:
        if not os.path.exists(x):
            counter += 1
            print "----->'" + x + "' MANGLER!"
    if not counter:
        print "  All items found"
    print '-------------------------------------------------------------------------------------------'
    print
