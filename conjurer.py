#!/usr/bin/env python3
import os, sys, pygame
import urllib.request
from xml.dom.minidom import parse
from pygame import font, image
from pygame.locals import *
from optparse import OptionParser

# --- Init ----------------------------------------------------------------------

pygame.init()
pygame.mouse.set_visible(0)
pygame.key.set_repeat(500, 100)
font10 =  pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 10)
font12 =  pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 12)
font14 =  pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 14)
font14b = pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 14)
font20 =  pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 20)
font20b = pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 20)
font40 =  pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 40)
font40b = pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', 40)


# --- Functions -----------------------------------------------------------------


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
			if _gameinstance.System in _gamedict:
				_gamedict[_gameinstance.System].append(_gameinstance)
			else:
				_gamedict[_gameinstance.System] = [_gameinstance]
	for _inst in _gamedict.keys():
		_gamedict[_inst].sort(key=lambda a: a.Navn)
	return _gamedict


def getCommandlineOptions():
	# Gets and handles commandline options
	_parser = OptionParser()
	_parser.add_option('-x', '--scrape', action='store_true', dest='scrape', default=False, help='NOT IMPLEMENTED! Tries to find gfx for games online')
	_parser.add_option('-d', '--dontrun', action='store_true', dest='dontRun', default=False, help='Do not run the chosen game, instead show all info about running it')
	_parser.add_option('-t', '--testpaths', action='store_true', dest='testPaths', default=False, help='Test paths in XML-file')
	_parser.add_option('-s', '--sortxml', action='store_true', dest='sortXML', default=False, help='Sort entries in the XML-file')
	_parser.add_option('-l', '--locked', action='store_true', dest='locked', default=False, help='Lock program to only display Arcade Games')
	_parser.add_option('-v', '--version', action='store_true', dest='version', default=False, help='Show program version')
	_parser.add_option('-r', '--rungame', action='store', dest='runGame', default=False, help='Run emulator <EmulatorNo> with <gameNo> as Conjurer starts', nargs=2)
	_parser.add_option('-m', '--multiplayer', action='store_true', dest='mpGames', default=False, help='Show only games with two or more players')
	_parser.add_option('-f', '--fullscreen', action='store_true', dest='fullscreen', default=False, help='run in fullscreen-mode')
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
		if _gameinstance.System in _gamedict:
			_gamedict[_gameinstance.System].append(_gameinstance)
		else:
			_gamedict[_gameinstance.System] = [_gameinstance]
	for _inst in _gamedict.keys():
		_gamedict[_inst].sort(key=lambda a: a.Navn)


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
	print('Found ', len(rom_liste), ' rom paths in file "games.xml"')
	print('Found ', len(screen_liste), ' screenshot paths in file "games.xml"')
	raw_input('Press <return> to test these paths')
	print('\n-------------------------------------------------------------------------------------------')
	for x in rom_liste:
		y = x.split(';')
		for z in y:
			if not os.path.exists(z.strip()):
				counter += 1
				print("----->'" + z.strip() + "' MANGLER!")
	for x in screen_liste:
		if not os.path.exists(x):
			counter += 1
			print("----->'" + x + "' MANGLER!")
	if not counter:
		print("  All items found")
	print('-------------------------------------------------------------------------------------------')


# --- Classes -------------------------------------------------------------------


class Conjurer:
	# Main class

	def __init__(self, options):
		self.dontRun = options.dontRun
		self.extPath = '/mnt/roms/'
		self._showPoweroff = 4
		self._showExitProgram = 4
		self._showHelp = FlipSwitch(0)
		if options.fullscreen:
			info = pygame.display.Info()
			self.windowWidth = info.current_w
			self.windowHeight = info.current_h
			self.display = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.FULLSCREEN)
			self.center_x = self.display.get_rect().centerx
			self.center_y = self.display.get_rect().centery
			# simple hotfix for dual monitors stacked
			if self.center_y > self.center_x:
				self.center_y += self.center_y / 2
		else:
			width = 800
			height = 600
			self.display = pygame.display.set_mode([width,height])
			self.center_x = self.display.get_rect().centerx
			self.center_y = self.display.get_rect().centery
			self.windowWidth = width
			self.windowHeight = height
		self.doubled = True if self.center_y > (320 * 4) else False		# double size of display if screen is big enough
		self.font_regular = font40 if self.doubled else font20
		self.font_bold =    font40b if self.doubled else font20b
		self.gamelist = SortGames(options.mpGames)
		self.path_pointer = RangeIterator(5)
		self.systems = StringIterator(list(self.gamelist.keys()))
		self.game_pointers = []
		for game in self.gamelist.keys():
			self.game_pointers.append(RangeIterator(len(self.gamelist[game]) - 1, False))
		self._locked = FlipSwitch(options.locked)
		self._running = True
		if options.runGame: # Run the game, enter the loop when it exits
			system = self.systems.GetByNr(int(options.runGame[0]))
			self.run_game(system, self.gamelist[system][int(options.runGame[1])].Paths)
			options.runGame = False
		self._loop()


	def _stringBuilder(self, System, FileList):
		"""Builds an executable string to be passed to the OS"""

		systemExecs = {'Amiga':['uae', ' -0 ', ' -1 ', ' -2 ', ' -3 '], 
					   'Arcade':['mame', ' -inipath . '], 
					   'C64':['x64', ' -autostart ', ' -8 ']}
		_systems = systemExecs
		_command = _systems[System][0]
		_count = 0
		for item in FileList:
			_count += 1
			_command += _systems[System][_count]
			_command += '"' + item + '"'
		return _command


	def run_game(self, System, FileList):
		"""Runs a game of type System, using files in FileList"""

		Command = self._stringBuilder(System, FileList)
		# ----------- Start Process -----------
		if self.dontRun:
			print('\n(' + Command + ')')
			sys.exit('Stopped because -norun parameter was given\n')
		pygame.display.quit()   # pygame blokerer displayet, saa vi draeber det
		os.popen(Command)
		self.display = pygame.display.set_mode([800,600])
		pygame.display.init()   # og starter det igen
		# ----------- Start Process -----------


	def _displayPoweroff(self):
		if self._showPoweroff == 0:
			self._showPoweroff = 'Bye!'
		pygame.draw.rect(self.display, (255,255,255), (200, 200, 400, 100)) 
		pygame.draw.line(self.display, (0, 0, 0), (210, 240), (590, 240), 1)
		textRect1 = pygame.Rect(220, 210, 600, 300)
		textRect2 = pygame.Rect(240, 250, 600, 300)
		textRect3 = pygame.Rect(395, 270, 405, 290)
		test_message1 = font20.render('Please confirm system shutdown', True, (0, 0, 0), (255,255,255))
		test_message2 = font14.render('Press Button 5 again to shutdown Arcade', True, (0, 0, 0), (255,255,255))
		test_message3 = font20.render(str(self._showPoweroff), True, (0, 0, 0), (255,255,255))
		self.display.blit(test_message1, textRect1)
		self.display.blit(test_message2, textRect2)
		self.display.blit(test_message3, textRect3)
		if self._showPoweroff == 'Bye!':
			os.system('poweroff 0')


	def _displayExitProgram(self):
		if self._showExitProgram == 0:
				self._showExitProgram = 'Bye!'
		pygame.draw.rect(self.display, (255,255,255), (200, 200, 400, 100)) 
		pygame.draw.line(self.display, (0, 0, 0), (210, 240), (590, 240), 1)
		textRect1 = pygame.Rect(220, 210, 600, 300)
		textRect2 = pygame.Rect(240, 250, 600, 300)
		textRect3 = pygame.Rect(395, 270, 405, 290)
		test_message1 = font20.render('Please confirm exit program', True, (0, 0, 0), (255,255,255))
		test_message2 = font14.render('Press Button 4 again to exit Conjurer', True, (0, 0, 0), (255,255,255))
		test_message3 = font20.render(str(self._showExitProgram), True, (0, 0, 0), (255,255,255))
		self.display.blit(test_message1, textRect1)
		self.display.blit(test_message2, textRect2)
		self.display.blit(test_message3, textRect3)
		if self._showExitProgram == 'Bye!':
			self._running = False


	def _displayHelp(self):
		_helpImage = pygame.image.load('help.jpg').convert()
		_helpImage = pygame.transform.scale2x(_helpImage)
		self.display.blit(_helpImage, (200, 100, 400, 410))
		_head =   font20.render('Conjurer Help', True, (255, 0, 0))
		_main1 =  font14.render('Keys to Quit Emulators:', True, (0, 0, 255))
		_main2 =  font14.render('Amiga  : F12 + Q', True, (0, 0, 255))
		_main3 =  font14.render('C64    : F12', True, (0, 0, 255))
		_main4 =  font14.render('Arcade : <escape>', True, (0, 0, 255))
		_main5 =  font14.render('Keys used in Conjurer:', True, (0, 0, 255))
		_main6 =  font14.render('Change System:    P1 joystick Left/Right', True, (0, 0, 255))
		_main7 =  font14.render('Change Game:      P1 joystick Up/Down', True, (0, 0, 255))
		_main8 =  font14.render('Change x10 Games: Shift + P1 joy Up/Down', True, (0, 0, 255))
		_main9 =  font14.render('Start Selected:   P1 Button 1', True, (0, 0, 255))
		_main10 = font14.render('Show Help:        P1 Button 2', True, (0, 0, 255))
		_main11 = font14.render('External Games:   P1 Button 3', True, (0, 0, 255))
		_main12 = font14.render('Exit Conjurer:    P1 Button 4', True, (0, 0, 255))
		_main13 = font14.render('Poweroff Machine: P1 Button 5', True, (0, 0, 255))
		pygame.draw.line(self.display, (255, 0, 0), (210, 150), (590, 150), 2)
		pygame.draw.line(self.display, (0, 0, 255), (320, 195), (480, 195), 1)
		pygame.draw.line(self.display, (0, 0, 255), (480, 195), (480, 260), 1)
		pygame.draw.line(self.display, (0, 0, 255), (320, 195), (320, 260), 1)
		pygame.draw.line(self.display, (0, 0, 255), (320, 260), (480, 260), 1)
		head_rect = _head.get_rect();   head_rect.centerx = self.center_x; head_rect.top = 120
		main1_rect = head_rect.copy();  main1_rect.left = 310;        main1_rect.top = 173
		main2_rect = head_rect.copy();  main2_rect.left = 335;        main2_rect.top = 200
		main3_rect = head_rect.copy();  main3_rect.left = 335;        main3_rect.top = 220
		main4_rect = head_rect.copy();  main4_rect.left = 335;        main4_rect.top = 240
		main5_rect = head_rect.copy();  main5_rect.left = 310;        main5_rect.top = 300
		main6_rect = head_rect.copy();  main6_rect.left = 240;        main6_rect.top = 340
		main7_rect = head_rect.copy();  main7_rect.left = 240;        main7_rect.top = 355
		main8_rect = head_rect.copy();  main8_rect.left = 240;        main8_rect.top = 370
		main9_rect = head_rect.copy();  main9_rect.left = 240;        main9_rect.top = 385
		main10_rect = head_rect.copy(); main10_rect.left = 240;       main10_rect.top = 400
		main11_rect = head_rect.copy(); main11_rect.left = 240;       main11_rect.top = 415
		main12_rect = head_rect.copy(); main12_rect.left = 240;       main12_rect.top = 430
		main13_rect = head_rect.copy(); main13_rect.left = 240;       main13_rect.top = 445
		pygame.draw.line(self.display, (0, 0, 255), (220, 320), (580, 320), 1)
		pygame.draw.line(self.display, (0, 0, 255), (580, 320), (580, 480), 1)
		pygame.draw.line(self.display, (0, 0, 255), (220, 320), (220, 480), 1)
		pygame.draw.line(self.display, (0, 0, 255), (220, 480), (580, 480), 1)
		self.display.blit(_head, head_rect)
		self.display.blit(_main1, main1_rect)
		self.display.blit(_main2, main2_rect)
		self.display.blit(_main3, main3_rect)
		self.display.blit(_main4, main4_rect)
		self.display.blit(_main5, main5_rect)
		self.display.blit(_main6, main6_rect)
		self.display.blit(_main7, main7_rect)
		self.display.blit(_main8, main8_rect)
		self.display.blit(_main9, main9_rect)
		self.display.blit(_main10, main10_rect)
		self.display.blit(_main11, main11_rect)
		self.display.blit(_main12, main12_rect)
		self.display.blit(_main13, main13_rect)


	def _displayScreen(self, _systemName, foc_game):
		_image = self.gamelist[_systemName][foc_game].Screen
		_image = pygame.transform.scale2x(_image)
		if self.doubled :	# scale twice if picture is high enough
			_image = pygame.transform.scale2x(_image)
		_hw = _image.get_width() / 2
		_hh = _image.get_height() / 2
		self.display.blit(_image,(self.center_x - _hw, self.center_y - _hh))


	def _displayGamesList(self, _systemName, foc_game):
		spacer = 50 if self.doubled else 25
		calulatedCenter = 500 if self.doubled else 250
		for entry, nr in enumerate(range(20)):
			if nr + foc_game - 10 < 0 or nr + foc_game - 10 > len(self.gamelist[_systemName]) - 1:
				_game = self.font_regular.render(' ', True, (0, 255, 255))
			else:
				if nr == 10:
					_game = self.font_bold.render(self.gamelist[_systemName][nr + foc_game - 10].Navn, True, (255, 0, 0))
				else:
					_game = self.font_regular.render(self.gamelist[_systemName][nr + foc_game - 10].Navn, True, (0, 255, 255))
			entry_rect = _game.get_rect()
			entry_rect.centerx = self.center_x
			entry_rect.centery = self.center_y - calulatedCenter + nr * spacer
			self.display.blit(_game, entry_rect)
		return
		# For testing output
		textRect = pygame.Rect(0,0,500,100)
		test_message = self.font_regular.render(str(self.ticktime), True, (255, 255, 255), (250,0,0))
		self.display.blit(test_message, textRect)


	def _displaySystems(self, focused, ypos):
		spacer = 2 if self.doubled else 1
		_systems_string1 = self.font_regular.render(self.systems.GetLeft(), True, (0, 0, 255))
		_systems_string2 = self.font_bold.render(self.systems.GetCentral() , True, (0, 200, 0))
		_systems_string3 = self.font_regular.render(self.systems.GetRight() , True, (0, 0, 255))
		self.display.blit(_systems_string2, pygame.Rect((self.center_x - 50 + (84 - _systems_string2.get_width()) / 2, ypos), (120, 50)))
		if not self._locked.Get():
			self.display.blit(_systems_string1, pygame.Rect((self.center_x - 50 - (100 * spacer) + (84 - _systems_string1.get_width()) / 2, ypos), (120, 50)))
			self.display.blit(_systems_string3, pygame.Rect((self.center_x - 50 + (100 * spacer) + (84 - _systems_string3.get_width()) / 2, ypos), (120, 50)))


	def _render(self):
		self.display.fill((0,0,0))
		self._displayScreen(self.systems.GetCentral(), self.game_pointers[self.systems.GetFocusedIndex()].Get())
		self._displayGamesList(self.systems.GetCentral(), self.game_pointers[self.systems.GetFocusedIndex()].Get())
		self._displaySystems(self.systems.GetCentral(), self.windowHeight - 50)
		if self._showHelp.Get():
			self._displayHelp()
		elif self._showPoweroff < 4:
			self._displayPoweroff()
		elif self._showExitProgram < 4:
			self._displayExitProgram()
		pygame.display.update()


	def _getkeys(self):
		"""Recieves input from keyboard while class is active"""
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:                                    # Escape, exit class
					self._running = False
				elif event.key == K_RCTRL:                                   # Button 1 = Run selected
					system = self.systems.GetCentral()
					no = self.game_pointers[self.systems.GetFocusedIndex()].Get()
					self.run_game(system, self.gamelist[system][no].Paths)
				elif event.key == K_LALT:                                    # Button 2 = Show Help
					self._showHelp.flip()
				elif event.key == K_SPACE:                                   # Button 3 = File dialogue
					_extSel = SelectExternal(self.extPath).Return()
					self.run_game(_extSel['system'], _extSel['gameFiles'])
				elif event.key == K_LSHIFT:                                  # Button 4 = Kill Conjurer
					self._showExitProgram -= 1
				elif event.key == K_x:                                       # Button 5 = Power off
					self._showPoweroff -= 1
				elif event.key == K_z:                                       # Button 6 = NOT CURRENTLY USED
					pass
				elif event.key == K_BACKSPACE:                               # Backspace = Change lock status
					self._locked.flip()
				elif event.key == K_RIGHT and not self._locked.Get():        # Key RIGHT
					self.systems.Next()
				elif event.key == K_LEFT and not self._locked.Get():         # Key LEFY
					self.systems.Prev()
				elif event.key == K_DOWN:                                    # Key DOWN
					self.game_pointers[self.systems.GetFocusedIndex()].Inc()
				elif event.key == K_UP:                                      # Key UP
					self.game_pointers[self.systems.GetFocusedIndex()].Dec()
				elif event.key == K_m:                                       # Shift + UP
					self.game_pointers[self.systems.GetFocusedIndex()].Dec(10)
				elif event.key == K_p:                                       # Shift + DOWN
					self.game_pointers[self.systems.GetFocusedIndex()].Inc(10)
				# Reset counters
				if event.key != K_LSHIFT:
					self._showExitProgram = 4
				if event.key != K_x:
					self._showPoweroff = 4


	def _loop(self):
		while self._running:
			self._render()
			self._getkeys()
		print("self.center_x: " + str(self.center_x))
		print("self.center_y: " + str(self.center_y))
		pygame.quit()


class FlipSwitch():
	# Represents a switch with on and off-state

	def __init__(self, Ind):
		self._value = Ind

	def flip(self):
		if self._value == 1:
			self._value = 0
		else:
			self._value = 1

	def Get(self):
		return self._value


class Scraper():
	# Contacts thegamesdb.net and tries to find data for a given game or gamelist

	def __init__(self):
		self.api_getList = "http://thegamesdb.net/api/GetGamesList.php?name=%s&platform=%s"
		self.api_getList2 = "http://www.mobygames.com/search/quick?q=%s&p=%s&sFilter=1&sG=on"
		self.headers = 	{'User-Agent': 'Mozilla/5.0'}

	def findGame_moby(self, name, platform_id):
		""" Searches for NAME and returns a dictionary of name:id of found matches"""
		print("  Looking up '" + name + "'...", end='')
		xmlQuestion = self.api_getList2 % (name.replace(' ', ''), str(platform_id))	# 143 = arcade
		xmlRequest = urllib2.Request(xmlQuestion, headers=self.headers)
		xmlResponse = urllib2.urlopen(xmlRequest)
		soup = BeautifulSoup(xmlResponse.read())
		searchResults = soup.find_all("div", class_="searchResult")
		gameInfo = {}
		allLinks = []
		for result in searchResults:
			links = result.find_all("a")
			for link in links:
				allLinks.append(link)
		for l in allLinks:
			gameInfo[l.text.encode('utf-8')] = l['href']
		print("matches:", len(gameInfo))
		return gameInfo

	def findGame_tgdb(self, name, platform):
		""" Searches for NAME and returns a dictionary of name:id of found matches"""
		print("  Looking up '" + name + "' on '" + platform + "'...", end='')
		xmlQuestion = self.api_getList % (name.replace(' ', ''), platform)
		xmlRequest = urllib2.Request(xmlQuestion, headers=self.headers)
		xmlResponse = urllib2.urlopen(xmlRequest)
		xmlData = xmlResponse.read()
		xmlParser = parseString(xmlData)
		xmlRoot = xmlParser.getElementsByTagName('Data')[0]
		gameInfo = {}
		for game in xmlRoot.getElementsByTagName('Game'):
			name = game.getElementsByTagName('GameTitle')[0].childNodes[0].nodeValue
			id = int(game.getElementsByTagName('id')[0].childNodes[0].nodeValue)
			gameInfo[name.encode('utf-8')] = id
		print("matches:", len(gameInfo))
		return gameInfo

	def showList(self, gameInfo):
		""" Displays the content of a dictionary of name:id of found matches"""
		print(' ', 110 * '-')
		for key in gameInfo:
			print('   ', key, ' : ', end='') 
			print(' ' * (100 - len(key) - len(str(gameInfo[key]))), end='')
			print(gameInfo[key])
		print(' ', 110 * '-')

	def getList(self, file, system):
		""" Loads a conjurer xml-file and returns a list of all game names by platform"""
		print("  Searching through '" + file + "'... ", end= '')
		file_ind = open(file, 'r')
		games = []
		SortParser = parse(file_ind)
		file_ind.close()
		for Game in SortParser.getElementsByTagName('game'):
			if Game.getElementsByTagName('system')[0].childNodes[0].nodeValue == system:
				games.append(str(Game.getElementsByTagName('name')[0].childNodes[0].nodeValue))
		prin("found", len(games), "games in file")
		return games


class GameInfo():
	# Represents a single game

		Navn = None
		Paths = None
		System = None
		Screen = None
		Players = None


class RangeIterator():
	# Represents a range of INTs from 0 -> X

	def __init__(self, Ind, loop=True):
		self.count = 0
		self.max = Ind
		self.loop = loop

	def Inc(self, count=1):
		self.count += count
		self._test()

	def Dec(self, count=1):
		self.count -= count
		self._test()

	def _test(self):
		if self.count >= self.max:
			if self.loop:
				self.count = 0
			else:
				self.count = self.max
		if self.count < 0:
			if self.loop:
				self.count = self.max + self.count
			else:
				self.count = 0

	def Get(self):
		return self.count


class StringIterator:
	# Represents a set of STRINGS

	def __init__(self, Ind):
		if type(Ind) == list:
			self.original = Ind[:]
			self.liste = Ind
		else:
			sys.exit('Must have list, not ' + str(type(Ind)) + str(Ind))

	def Next(self):
		self.liste.append(self.liste.pop(0))

	def Prev(self):
		self.liste.insert(0, self.liste.pop())

	def Get(self):
		""" Returns the whole list"""
		return self.liste

	def GetByNr(self, no):
		""" Returns the system requested by its number"""
		return self.original[no]

	def GetCentral(self):
		""" Returns the midle, focused string"""
		return self.liste[self._getCentralIndex()]

	def GetLeft(self):
		""" Returns the string to the left of the middle"""
		if len(self.liste) > 2:
			return self.liste[self._getCentralIndex() - 1]
		else:
			return ""

	def GetRight(self):
		""" Returns the string to the right of the middle"""
		if len(self.liste) > 1:
			return self.liste[self._getCentralIndex() + 1]
		else:
			return ""

	def _getCentralIndex(self):
		""" Returns the index of the middle, focused string"""
		if len(self.liste) % 2:
			return int(len(self.liste) / 2)
		else:
			return int((len(self.liste) / 2) - 1)

	def GetFocusedIndex(self):
		""" Returns the index of the middle, focused string compared to original list"""
		return self.original.index(self.GetCentral())


class SelectExternal():
   # Handles selection of games outside conjurer's XML-files

	def __init__(self, defPath):
		pygame.mouse.set_visible(0)
		if not os.path.exists(defPath):
			defPath = '/'
		self.display = pygame.display.set_mode([800,600])
		self._selectedFiles = [None, None, None, None]
		self.center_x = self.display.get_rect().centerx
		self.currentPath = defPath
		self._systems = StringIterator(systemExecs.keys())
		self._vcursor = RangeIterator(5)
		self._changeDir(defPath)
		self._filter = ''
		self._runlevel = 1        # Using runlevel 0, 1 and 2 in this class
		self._loop()


	def _getkeys1(self):
		"""Recieves input from keyboard while in runlevel 1"""
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self._selectedFiles = [None, None, None, None]
					self._runlevel = 0
				elif event.key == K_UP:                              # Key UP
					self._vcursor.Dec()
				elif event.key == K_DOWN:                            # Key DOWN
					self._vcursor.Inc()
				elif event.key == K_LEFT:                            # Key LEFT
					self._systems.Next()
				elif event.key == K_RIGHT:                           # Key Right
					self._systems.Prev()
				elif event.key == K_RCTRL :                          # Button 1 = Execute Choose
					if self._vcursor.Get() == 0:
						self._runlevel = 0
					else:
						self._runlevel = 2


	def _getkeys2(self):
		"""Recieves input from keyboard while in runlevel 2"""
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:                            # Key ESCAPE
					return '<escape>'
				elif event.key == K_PAGEUP:                          # Key PAGEUP
					self._pageViewed.Dec()
					self._cursor[1].count = 0
				elif event.key == K_PAGEDOWN:                        # Key PAGEDOWN
					self._pageViewed.Inc()
					self._cursor[1].count = 0
				elif event.key == K_RIGHT or event.key == K_LEFT:    # Key LEFT/RIGHT
					if len(self._files[1]) != 0:
						self._cursor[0].flip()
						if self._cursor[1].Get() > len(self._files[self._cursor[0].Get()]) - 1:
							self._cursor[1].count = len(self._files[self._cursor[0].Get()]) - 1
				elif event.key == K_DOWN:                            # Key DOWN
					if self._cursorPos < self._pageTotal:
						self._cursor[1].Inc()
					else:
						self._cursor[1].count = 0
				elif event.key == K_UP:                              # Key UP
					if (self._cursor[1].Get() == 0) and (self._pageViewed.Get() == len(self._filtered) / 38):
						self._cursor[1].count = self._pageTotal % 38
					else:
						if self._cursor[0].Get() != 0 or self._cursor[1].Get() != 0:
							self._cursor[1].Dec()
				elif event.key == K_RETURN or event.key == K_RCTRL:  # Key RETURN/RCTRL
					if self._cursor[0].Get() == 0:
						self._changeDir(self._files[0][self._cursor[1].Get()])
					elif self._cursor[0].Get() == 1:
						fil = self._filtered[self._cursor[1].Get() + self._pageViewed.Get() * 38]
						return os.path.join(self.currentPath, fil)
					else:
						sys.exit('Something is way wrong, value is ' + self._cursor[0].Get())
				elif event.key == K_BACKSPACE:                       # Key BACKSPACE
					self._filter = self._filter[:-1]
				else:
					if len(self._filter) < 10 and (event.key in range(48, 57) or event.key in range(97, 123)):
						self._filter += chr(event.key)


	def _displaySystems(self, xpos):
		_systems_string1 = font20.render(self._systems.GetLeft(), True, (0, 0, 255))
		_systems_string2 = font20b.render(self._systems.GetCentral() , True, (0, 200, 0))
		_systems_string3 = font20.render(self._systems.GetRight() , True, (0, 0, 255))
		self.display.blit(_systems_string1, pygame.Rect((self.center_x - 200 + (84 - _systems_string1.get_width()) / 2, xpos), (120, 50)))
		self.display.blit(_systems_string2, pygame.Rect((self.center_x - 50 + (84 - _systems_string2.get_width()) / 2, xpos), (120, 50)))
		self.display.blit(_systems_string3, pygame.Rect((self.center_x + 100 + (84 - _systems_string3.get_width()) / 2, xpos), (120, 50)))


	def _fileSelector(self):
		""" Loops until file is selected, then returns file"""
		_selectedFile = False
		while not _selectedFile:
			filterLength = len(self._filter)
			self._cursorPos = self._cursor[1].Get() + (38 * self._pageViewed.Get())
			if self._cursor[0].Get() == 0:
				self._pageTotal = len(self._files[0]) - 1
			else:
				self._pageTotal = len(self._filtered) - 1
			_selectedFile = self._getkeys2()
			if filterLength != len(self._filtered): # if filter updated
				self._filtered = filter(lambda x: x.lower().startswith(self._filter) , self._files[1])
				self._pageViewed.max = (len(self._filtered) / 38) + 1
			if (self._pageViewed.Get() + 1) > (len(self._filtered) / 38 + 1):
				self._pageViewed.count = 0
			self._drawFSS()
			self._drawScreenContent([self._cursor[0].Get(), self._cursor[1].Get()])
		if _selectedFile != '<escape>':
			return _selectedFile
		else:
			return None


	def _showChooseFile(self):
		"""Show the file select dialogue"""
		self.display.fill((0,0,0))
		_cursor = [0,0,0,0,0]
		_cursor[self._vcursor.Get() - 1] = 255
		_startextImage = pygame.image.load('startext.jpg').convert()
		self.display.blit(_startextImage, (100, 100, 700, 500))
		# define rectangles
		_headRect =  pygame.Rect(215, 125, 200, 50)
		_pathRect1 = pygame.Rect(125, 200, 550, 20)
		_pathRect2 = pygame.Rect(125, 250, 550, 20)
		_pathRect3 = pygame.Rect(125, 300, 550, 20)
		_pathRect4 = pygame.Rect(125, 350, 550, 20)
		_endRect =   pygame.Rect(370, 450, 50, 20)
		# define texts
		_headMessage =  font20.render('Choose an external game to run:', True, (0, 0, 0))
		_pathMessage1 = font14b.render('Path 1: ' + str(self._selectedFiles[0]) + '', True, (255, 0, 0))
		_pathMessage2 = font14b.render('Path 2: ' + str(self._selectedFiles[1]) + '', True, (255, 0, 0))
		_pathMessage3 = font14b.render('Path 3: ' + str(self._selectedFiles[2]) + '', True, (255, 0, 0))
		_pathMessage4 = font14b.render('Path 4: ' + str(self._selectedFiles[3]) + '', True, (255, 0, 0))
		_pathEnd =      font20b.render(' OK ', True, (255, 0, 0))
		# draw
		pygame.draw.line(self.display, (0, 0, 0), (210, 150), (590, 150), 1)
		pygame.draw.rect(self.display, (0, 0, _cursor[0]), (120, 196, 560, 23))
		pygame.draw.rect(self.display, (0, 0, _cursor[1]), (120, 246, 560, 23)) 
		pygame.draw.rect(self.display, (0, 0, _cursor[2]), (120, 296, 560, 23)) 
		pygame.draw.rect(self.display, (0, 0, _cursor[3]), (120, 346, 560, 23))
		pygame.draw.rect(self.display, (0, 0, 0), (210, 400, 370, 23))
		pygame.draw.rect(self.display, (0, 0, _cursor[4]), (370, 450, 50, 23))

		# blit
		self.display.blit(_headMessage, _headRect)
		self.display.blit(_pathMessage1, _pathRect1)
		self.display.blit(_pathMessage2, _pathRect2)
		self.display.blit(_pathMessage3, _pathRect3)
		self.display.blit(_pathMessage4, _pathRect4)
		self.display.blit(_pathEnd, _endRect)
		self._displaySystems(400)


	def _changeDir(self, newDir):
		if newDir == '..':
			self.currentPath = os.path.split(self.currentPath)[0]
		else:
			self.currentPath = os.path.join(self.currentPath, newDir)
		self._files = [['..'],[]]
		self._cursor = [FlipSwitch(0), RangeIterator(38, 1)]
		if self.currentPath == '/':
			self._files[0].pop()
		self._getCurrent()
		self._pageViewed = RangeIterator((len(self._filtered) / 38) + 1, 1)
		self._filter = ''
		self._drawFSS()


	def _getCurrent(self):
		filelist = os.listdir(self.currentPath)
		for file in filelist:
			if os.path.isdir(os.path.join(self.currentPath, file)):
				self._files[0].append(file)
			else:
				self._files[1].append(file)
		self._files[0].sort()
		self._files[1].sort()
		self._filtered = self._files[1]


	def _drawFSS(self):
		self.display.fill((0, 0, 0))
		_pageRect1 = pygame.Rect(5, 5, 200, 50)
		_pageRect2 = pygame.Rect(305, 5, 200, 50)
		_pageMessage1 = font12.render('Directories', True, (0, 255, 0), (0, 0, 0))
		_pageMessage2 = font12.render('Files               Filter:', True, (0, 255, 0), (0, 0, 0))
		self.display.blit(_pageMessage1, _pageRect1)
		self.display.blit(_pageMessage2, _pageRect2)
		pygame.draw.line(self.display, (255, 0, 0), (1, 1), (799, 1), 1)
		pygame.draw.line(self.display, (255, 0, 0), (799, 1), (799, 599), 1)
		pygame.draw.line(self.display, (255, 0, 0), (799, 599), (1, 599), 1)
		pygame.draw.line(self.display, (255, 0, 0), (1, 599), (1, 1), 1)
		pygame.draw.line(self.display, (255, 0, 0), (300, 1), (300, 599), 1)
		pygame.draw.line(self.display, (255, 0, 0), (1, 20), (799, 20), 1)
		# Searchfield
		pygame.draw.line(self.display, (255, 0, 0), (500, 3), (565, 3), 1)
		pygame.draw.line(self.display, (255, 0, 0), (565, 3), (565, 18), 1)
		pygame.draw.line(self.display, (255, 0, 0), (500, 18), (565, 18), 1)
		pygame.draw.line(self.display, (255, 0, 0), (500, 18), (500, 3), 1)


	def _drawScreenContent(self, cursor):
		dirRect = pygame.Rect(1, 1, 300, 599)
		fileRect = pygame.Rect(300, 1, 699, 599)
		_pageRect = pygame.Rect(700, 5, 795, 50)
		_filterRect = pygame.Rect(503, 5, 98, 15)
		_pageMessage = font12.render('Page ' + str(self._pageViewed.Get() + 1) + ' / ' + str(len(self._filtered) / 38 + 1), True, (255, 255, 255), (0, 0, 0))
		_filterMessage = font10.render(self._filter, True, (255, 255, 255), (0, 0, 0))
		self.display.blit(_pageMessage, _pageRect)
		self.display.blit(_filterMessage, _filterRect)
		# Process directories
		for nr in range(38):
			if nr < len(self._files[0]):
				if nr == cursor[1] and cursor[0] == 0:
					_dirMessage = font12.render(self._files[0][nr], True, (0, 0, 0), (255, 255, 255))
				else:
					_dirMessage = font12.render(self._files[0][nr], True, (255, 255, 255), (0,0,0))
				dirRect.left = 5
				dirRect.top = 25 + nr * 15
				self.display.blit(_dirMessage, dirRect)
		# Process files
		for nr in range(38):
			fileNr = self._pageViewed.Get() * 38 + nr
			if fileNr < len(self._filtered):
				if nr == cursor[1] and cursor[0] == 1:
					_fileMessage = font12.render(self._filtered[fileNr], True, (0, 0, 0), (255, 255, 255))
				else:
					_fileMessage = font12.render(self._filtered[fileNr], True, (255, 255, 255), (0,0,0))
				fileRect.left = 305
				fileRect.top = 25 + nr * 15
				self.display.blit(_fileMessage, fileRect)
		pygame.display.update()


	def Return(self):
		"""Returns the list of selected files"""
		return {'system':self._systems.GetCentral(), 'gameFiles':filter(None, self._selectedFiles)}


	def _loop(self):
		"""Keep displaying one of two displays: file selctor screen OR the file browser"""
		while self._runlevel:
			self.display.fill((0,0,0))
			if self._runlevel == 1:
				self._showChooseFile()
				self._getkeys1()
			elif self._runlevel == 2:
				self._selectedFiles[self._vcursor.Get() - 1] = self._fileSelector()
				self._runlevel = 1
			pygame.display.update()
		# Entering runlevel 0, Class dies, returns to calling class


# --- Main ----------------------------------------------------------------------


version = 1.21 # (converted to python3, add to one file)
cmd_options = getCommandlineOptions()

# Laeg det her over i en separat fil....
if cmd_options.scrape:
	scraper = Scraper()
	list = scraper.getList('xml/games.xml', 'Arcade')
	gamesTgdb = []
	gamesMoby = []
	print("\n  Checking thegamesdb.net for " + str(len(list)) + " games:")
	print(' -------------------------------------------------------------')
	for game in list:
		x = scraper.findGame_tgdb(game, "Arcade")
		if x != {}:
			gamesTgdb.append(x)
	print('  -------------------------------------------------------------')
	print()
	print("  Checking mobygames for " + str(len(list)) + " games:")
	print('  -------------------------------------------------------------')
	for game in list:
		x = scraper.findGame_moby(game, 143)
		if x != {}:
			gamesMoby.append(x)
	print('  -------------------------------------------------------------')
	print("\nTheGamesDB", len(gamesTgdb))
	print("MobyGames", len(gamesMoby))


	sys.exit('Scraping done!\n')
elif cmd_options.sortXML:
	SortXml()
	sys.exit('\n  Done sorting!\n  Sorted data was wwritten to "xml/games_sorted.xml"\n')
elif cmd_options.testPaths:
	TestPaths()
	sys.exit('Done testing!\n')
elif cmd_options.version:
	print('\n   Conjurer Version is', str(version))
	sys.exit('')
elif cmd_options.dontRun:
	dontrun = True

# start main program
conjurer_handle = Conjurer(cmd_options)
print('\nApplication terminated. "./conjurer.py" will restart it\n')



# --- Todo ----------------------------------------------------------------------
# - make sure that emulators exist and can start.... even new ones, ANY emulator, I guess....




















