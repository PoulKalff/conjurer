#!/usr/bin/env python3
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import os
import sys
import json
import urllib.request
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
SDLsystemExecs =	{	'Amiga'	:	['uae', '-0', '-1', '-2', '-3'], 
						'Arcade':	['mame', '-inipath .'], 
						'C64'	:	['x64', '-autostart', '-8']
					}
GUIsystemExecs =	{	'Amiga'	:	['fs-uae', 'config.fs-uae'], 
						'Arcade':	['mame', '-inipath'],
						'C64'	:	['x64', '-autostart', '-8']
					}

systemExecs = GUIsystemExecs

# --- Functions -----------------------------------------------------------------

def getCommandlineOptions():
	# Gets and handles commandline options
	_parser = OptionParser()
	_parser.add_option('-d', '--dontrun',		action='store_true',	dest='dontRun',		default=False, help='Do not run the chosen game, instead show all info about running it')
	_parser.add_option('-t', '--testpaths',		action='store_true',	dest='testPaths',	default=False, help='Test paths in json-file')
	_parser.add_option('-l', '--locked',		action='store_true',	dest='locked',		default=False, help='Lock program to only display Arcade Games')
	_parser.add_option('-v', '--version',		action='store_true',	dest='version',		default=False, help='Show program version')
	_parser.add_option('-r', '--rungame',		action='store',			dest='runGame',		default=False, help='Run emulator <EmulatorNo> with <gameNo> as Conjurer starts', nargs=2)
	_parser.add_option('-m', '--multiplayer',	action='store_true',	dest='mpGames', 	default=False, help='Show only games with two or more players')
	_parser.add_option('-f', '--fullscreen',	action='store_true',	dest='fullscreen',	default=False, help='run in fullscreen-mode')
	_options, _args = _parser.parse_args()
	return _options


def TestPaths():
	# Loads all values from conjurer's json-files and verifies their validity
	counter = 0
	with open('lists/games.json') as json_file:
		games = json.load(json_file)
		print('\n  Veryfying ROM paths:')
		print('  -------------------------------------------------------------------------------------------')
		for system in games[0]:
			for game in games[0][system]:
				for rom in game['roms']:
					if os.path.exists(rom):
						print('    Found "' + rom + '"')
					else:
						print('    COULD NOT FIND "' + rom + '"!!!!!!')
		print('\n  Veryfying screenshot paths:')
		print('  -------------------------------------------------------------------------------------------')
		for system in games[0]:
			for game in games[0][system]:
				if os.path.exists(game['screenpath']):
					print('    Found "' + game['screenpath'] + '"')
				else:
					print('    COULD NOT FIND "' + game['screenpath'] + '"!!!!!!')
	print('  -------------------------------------------------------------------------------------------')
	sys.exit('\n  All done\n')


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
		with open('lists/games.json') as json_file:
			fileContents = json.load(json_file)
			fileContents[0]['Amiga'] = sorted(fileContents[0]['Amiga'], key=lambda x : x['name'])
			fileContents[0]['Arcade'] = sorted(fileContents[0]['Arcade'], key=lambda x : x['name'])
			fileContents[0]['C64'] = sorted(fileContents[0]['C64'], key=lambda x : x['name'])
			self.gamelist = fileContents
		self.path_pointer = RangeIterator(5)
		self.systems = StringIterator(list(self.gamelist[0].keys()))
		self.game_pointers = []
		for game in self.gamelist[0].keys():
			self.game_pointers.append(RangeIterator(len(self.gamelist[0][game]) - 1, False))
		self._locked = FlipSwitch(options.locked)
		self._running = True
		if options.runGame: # Run the game, enter the loop when it exits
			system = self.systems.GetByNr(int(options.runGame[0]))
			self.run_game(system, self.gamelist[system][int(options.runGame[1])].Paths)
			options.runGame = False
		self._loop()


	def _stringBuilder(self, System, FileList):
		"""Builds an executable string to be passed to the OS"""
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
		_temp = pygame.display
		pygame.display.quit()   # pygame blokerer displayet, saa vi draeber det
		os.popen(Command)



		self.display = _temp #											<--------------------------------- UTESTED!
	# pygame.display.set_mode([800,600])
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
		_main11 = font14.render('<not used>:       P1 Button 3', True, (0, 0, 255))
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
		_image = image.load(self.gamelist[0][_systemName][foc_game]['screenpath']).convert()
		_image = pygame.transform.scale2x(_image)
		if self.doubled :	# scale twice if picture is high enough
			_image = pygame.transform.scale2x(_image)
		_hw = int(_image.get_width() / 2)
		_hh = int(_image.get_height() / 2)
		self.display.blit(_image,(self.center_x - _hw, self.center_y - _hh))


	def _displayGamesList(self, _systemName, foc_game):
		spacer = 50 if self.doubled else 25
		calulatedCenter = 500 if self.doubled else 250
		for entry, nr in enumerate(range(20)):
			if nr + foc_game - 10 < 0 or nr + foc_game - 10 > len(self.gamelist[0][_systemName]) - 1:
				_game = self.font_regular.render(' ', True, (0, 255, 255))
			else:
				name = self.gamelist[0][_systemName][nr + foc_game - 10]['name']
				if nr == 10:
					_game = self.font_bold.render(name, True, (255, 0, 0))
				else:
					_game = self.font_regular.render(name, True, (0, 255, 255))
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
		self.display.blit(_systems_string2, pygame.Rect((self.center_x - 50 + (84 - int(_systems_string2.get_width() / 2)), ypos), (120, 50)))
		if not self._locked.Get():
			self.display.blit(_systems_string1, pygame.Rect((self.center_x - 50 - (100 * spacer) + (84 - int(_systems_string1.get_width() / 2)), ypos), (120, 50)))
			self.display.blit(_systems_string3, pygame.Rect((self.center_x - 50 + (100 * spacer) + (84 - int(_systems_string3.get_width() / 2)), ypos), (120, 50)))


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


# --- Main ----------------------------------------------------------------------


version = 1.22	# (removed scraper)
cmd_options = getCommandlineOptions()

if cmd_options.testPaths:
	TestPaths()
	sys.exit('Done testing!\n')
elif cmd_options.version:
	print('\n   Conjurer Version is', str(version))
	sys.exit('')
elif cmd_options.dontRun:
	dontrun = True

# start main program
conjurer_handle = Conjurer(cmd_options)
print('\n  Application terminated...\n')



# --- Todo ----------------------------------------------------------------------
# - make sure that emulators exist and can start.... even new ones, ANY emulator, I guess....




















