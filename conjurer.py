#!/usr/bin/env python3
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import os
import sys
import json
import subprocess
import urllib.request
from pygame import font, image
from pygame.locals import *
from optparse import OptionParser

# --- Init ----------------------------------------------------------------------

pygame.init()
pygame.mouse.set_visible(0)
pygame.key.set_repeat(500, 100)



sounds = {
		1 : pygame.mixer.Sound('sfx/mixkit-interface-device-click-2577.wav'),
		2 : pygame.mixer.Sound('sfx/mixkit-game-click-1114.wav'),
		4 : pygame.mixer.Sound('sfx/mixkit-opening-software-interface-2578.wav'),
		5 : pygame.mixer.Sound('sfx/mixkit-quest-game-interface-click-1139.wav')
}
systemExecs =	{
			'Arcade':	['mame', '-inipath', '.'],
			'C64'	:	['x64sc', '-config', 'vice.cfg', '-autostart'],
			'Amiga'	:	['fs-uae']
		}

# --- Functions -----------------------------------------------------------------

def getCommandlineOptions():
	# Gets and handles commandline options
	_parser = OptionParser()
	_parser.add_option('-d', '--dontrun',		action='store_true',	dest='dontRun',		default=False, help='Do not run the chosen game, instead show all info about running it')
	_parser.add_option('-t', '--testpaths',		action='store_true',	dest='testPaths',	default=False, help='Test paths in json-file')
	_parser.add_option('-l', '--locked',		action='store_true',	dest='locked',		default=False, help='Lock program to only display Arcade Games')
	_parser.add_option('-v', '--version',		action='store_true',	dest='version',		default=False, help='Show program version')
	_parser.add_option('-r', '--rungame',		action='store',		dest='runGame',		default=False, help='Run emulator <EmulatorNo> with <gameNo> as Conjurer starts', nargs=2)
	_parser.add_option('-m', '--multiplayer',	action='store_true',	dest='mpGames', 	default=False, help='Show only games with two or more players')
	_parser.add_option('-f', '--fullscreen',	action='store_true',	dest='fullscreen',	default=False, help='run in fullscreen-mode')
	_options, _args = _parser.parse_args()
	return _options



def TestPaths():
	# Loads all values from conjurer's json-files and verifies their validity
	counterMissing = 0
	listMissing = []
	with open('gameList.json') as json_file:
		games = json.load(json_file)
		print('\n  Veryfying ROM paths:')
		print('  -------------------------------------------------------------------------------------------')
		for system in games[0]:
			for game in games[0][system]:
				for rom in game['roms']:
					if os.path.exists(rom):
						print('    Found "' + rom + '"')
					else:
						listMissing.append('    COULD NOT FIND "' + rom + '"!!!!!!')
						counterMissing += 1
		print('\n  Veryfying screenshot paths:')
		print('  -------------------------------------------------------------------------------------------')
		for system in games[0]:
			for game in games[0][system]:
				if os.path.exists(game['screenpath']):
					print('    Found "' + game['screenpath'] + '"')
				else:
					listMissing.append('    COULD NOT FIND "' + game['screenpath'] + '"!!!!!!')
					counterMissing += 1
	for l in listMissing:
		print(l)
	print('  -------------------------------------------------------------------------------------------')
	print('   ', counterMissing, 'files missing')
	sys.exit('\n  All done\n')



# --- Classes -------------------------------------------------------------------


class Conjurer:
	# Main class

	def __init__(self, options):
		self.extPath = '/mnt/roms/'
		self._exitTimer = 4
		self.initDisplay()
		self.font_regular = pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', int(self.windowHeight / 26))
		self.font_bold = pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf', int(self.windowHeight / 26))
		with open('gameList.json') as json_file:
			fileContents = json.load(json_file)
			self.gamelist = {}
			self.gamelist['Amiga'] = sorted(fileContents[0]['Amiga'], key=lambda x : x['name'])
			self.gamelist['Arcade'] = sorted(fileContents[0]['Arcade'], key=lambda x : x['name'])
			self.gamelist['C64'] = sorted(fileContents[0]['C64'], key=lambda x : x['name'])
		self.path_pointer = RangeIterator(5)
		self.systems = StringIterator(list(self.gamelist.keys()))
		self.game_pointers = []
		for game in self.gamelist.keys():
			self.game_pointers.append(RangeIterator(len(self.gamelist[game]) - 1, False))
		self._locked = FlipSwitch(options.locked)
		self._showDialog = False
		self._running = True
		if options.runGame: # Run the game, enter the loop when it exits
			system = self.systems.GetByNr(int(options.runGame[0]))
			self.run_game(system, self.gamelist[system][int(options.runGame[1])].Paths)
			options.runGame = False
		self._loop()



	def initDisplay(self):
		if cmd_options.fullscreen:
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


	def goToLetter(self, letterCode):
		_found = False
		_names = [x['name'] for x in self.gamelist[self.systems.GetCentral()]]
		while not _found:
			_letter = chr(letterCode)
			for _nr, _name in enumerate(_names):
				if _name[0] == _letter.upper():
					self.game_pointers[self.systems.GetFocusedIndex()].count = _nr
					_found = True
					break
			letterCode += 1
	# NB! : Add XYZ as searchable!



	def stringBuilder(self, gameData):
		"""Builds an array of strings to be passed for execution """
		commandArray = systemExecs[gameData['system']].copy()
		if gameData['system'] == 'Amiga':
			commandArray.append('--amiga-model=' + gameData['model'])
			driveType = 'cdrom' if gameData['model'].upper() == 'CD32' or gameData['model'] == 'CDTV' else 'floppy'
			for nr, item in enumerate(gameData['roms']):
				commandArray.append('--{}_drive_{}'.format(driveType, nr) + '=' + item)
				if driveType == 'floppy':
					commandArray.append('--{}_image_{}'.format(driveType, nr) + '=' + item)
		else:
			for nr, item in enumerate(gameData['roms']):
				commandArray.append(item)
		return commandArray



	def run_game(self, System, gameData):
		"""Runs a game of type System, using files in FileList"""
		gameData['system'] = System
		if 'execPath' in gameData:
			command = list(gameData['execPath'].split())
		else:
			command = self.stringBuilder(gameData)
		# ----------- Start Process -----------
		if cmd_options.dontRun:
			print(command)
			sys.exit('Stopped because -norun parameter was given\n')
		emulatorProcess = subprocess.Popen(command,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
		stdout, stderr = emulatorProcess.communicate()
		pygame.event.clear()	# clear (keyboard) events sent while emulator was running
		# ----------- Start Process -----------



	def dialogBox(self, height, textList):
		""" Shows a dialogbox in center of screen """
		# find top left corner of box
#		height += (20 * len(textList))
		width = 1000
		posX = int(self.center_x - (width / 2))
		posY = int(self.center_y - (height / 2))
		pygame.draw.rect(self.display, (255, 255, 255), (posX, posY, width, height))
		pygame.draw.rect(self.display, (0, 0, 0), (posX, posY, width, height), 2)
		pygame.draw.line(self.display, (0, 0, 0), (posX + 20, posY + 70), (posX + width - 20, posY + 70), 2)
		for row in textList:
			renderedFont = pygame.font.Font('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', int(row[1]))
			renderedText = renderedFont.render(row[2], True, (0, 0, 0), (255,255,255))
			w, h = renderedText.get_size()
			textRect = pygame.Rect(	posX + int(width / 2) - int(w / 2),
						posY + int(row[0]),
						posX + int(width / 2) - int(w / 2) + w,
						posY + int(row[0]))
			self.display.blit(renderedText, textRect)
		return


	def showDialog(self):
		if self._showDialog == 1:
			if self._exitTimer == 0:
				self._exitTimer = 'Bye!'
				self._running = False
			self.dialogBox(190, [	[10, 45, 'Please confirm program exit'],
						[90, 30, 'Press Blue Button again to shutdown Arcade'],
						[140, 40, str(self._exitTimer)]])
		elif self._showDialog == 2:
			system = self.systems.GetCentral()
			no = self.game_pointers[self.systems.GetFocusedIndex()].Get()
			gameInfo = self.gamelist[system][no]
			data = []
			xPos = 90
			data.append([ xPos, 20, 'Players: ' + gameInfo['players'] + ' ' * 70])
			rom1 = gameInfo['roms'][0].split('/')[2][:74]
			if 'model' in gameInfo.keys():
				xPos += 30
				data.append([ xPos, 20, 'Amiga Model: ' + gameInfo['model'] + ' ' * (67 - len(gameInfo['model']))])
			xPos += 30
			data.append([ xPos, 20, 'Roms: ' + rom1 + ' ' * (74 - len(rom1))])
			for romNr in range(2, len(gameInfo['roms']) + 1):
				rom = gameInfo['roms'][romNr - 1].split('/')[2][:74]
				xPos += 30
				data.append([ xPos, 20, '      ' + rom + ' ' * (74 - len(rom))])
			screen = gameInfo['screenpath'].split('/')[2][:74]
			xPos += 30
			data.append([ xPos, 20, 'Screenshot: ' + screen + ' ' * (68 -len(screen))])
			if 'notes' in gameInfo:
				for nr, l in enumerate(gameInfo['notes'].split(',')):
					xPos += 30
					line = 'Notes: ' + l if nr == 0 else '       ' + l
					line = line + ' ' * (80 - len(line))
					data.append([xPos, 20, line])
			else:
				xPos += 30
				data.append([xPos, 20, 'Notes: -' + ' ' * 72])
			xPos += 30
			self.dialogBox(xPos, [	[10, 45, gameInfo['name']], *data])
		elif self._showDialog == 3:
			if self._exitTimer == 0:
				self._exitTimer = 'Bye!'
			self.dialogBox(190, [	[10, 45, 'Please confirm system shutdown'],
						[90, 30, 'Press Green Button again to shutdown Arcade'],
						[140, 40, str(self._exitTimer)]])
			if self._exitTimer == 'Bye!':
				pygame.display.update()
				os.system('poweroff')


	def _displayScreen(self, _systemName, foc_game):
		_image = image.load(self.gamelist[_systemName][foc_game]['screenpath']).convert()
		_image = pygame.transform.scale(_image, (int(self.windowWidth * 0.95), int(self.windowHeight * 0.95)))
		_hw = int(_image.get_width() / 2)
		_hh = int(_image.get_height() / 2)
		self.display.blit(_image,(self.center_x - _hw, self.center_y - _hh))


	def _displayGamesList(self, _systemName, foc_game):
		spacer = int(self.windowHeight / 20)
		for entry, nr in enumerate(range(1, 19)):
			if nr + foc_game - 10 < 0 or nr + foc_game - 10 > len(self.gamelist[_systemName]) - 1:
				_game = self.font_regular.render(' ', True, (0, 255, 255))
			else:
				name = self.gamelist[_systemName][nr + foc_game - 10]['name']
				if nr == 10:
					_game = self.font_bold.render(name, True, (255, 0, 0))
				else:
					_game = self.font_regular.render(name, True, (0, 255, 255))
			entry_rect = _game.get_rect()
			entry_rect.centerx = self.center_x
			entry_rect.centery = nr * spacer
			self.display.blit(_game, entry_rect)
		return
		# For testing output
		textRect = pygame.Rect(0,0,500,100)
		test_message = self.font_regular.render(str(self.ticktime), True, (255, 255, 255), (250,0,0))
		self.display.blit(test_message, textRect)


	def _displaySystems(self, focused, ypos):
		_systems_string1 = self.font_regular.render(self.systems.GetLeft(), True, (0, 0, 255))
		_systems_string2 = self.font_bold.render(self.systems.GetCentral() , True, (0, 200, 0))
		_systems_string3 = self.font_regular.render(self.systems.GetRight() , True, (0, 0, 255))
		self.display.blit(_systems_string2, pygame.Rect((self.center_x - 50 + (84 - int(_systems_string2.get_width() / 2)), ypos), (120, 50)))
		if not self._locked.Get():
			self.display.blit(_systems_string1, pygame.Rect((self.center_x - 50 - 200 + (84 - int(_systems_string1.get_width() / 2)), ypos), (120, 50)))
			self.display.blit(_systems_string3, pygame.Rect((self.center_x - 50 + 200 + (84 - int(_systems_string3.get_width() / 2)), ypos), (120, 50)))


	def _render(self):
		self.display.fill((0,0,0))
		self._displayScreen(self.systems.GetCentral(), self.game_pointers[self.systems.GetFocusedIndex()].Get())
		self._displayGamesList(self.systems.GetCentral(), self.game_pointers[self.systems.GetFocusedIndex()].Get())
		self._displaySystems(self.systems.GetCentral(), self.windowHeight - 50)
		if self._showDialog:
			self.showDialog()
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
					self.run_game(system, self.gamelist[system][no])
				elif event.key == K_BACKSPACE:                               # Backspace = Change lock status
					self._locked.flip()
				elif event.key == K_RIGHT and not self._locked.Get():        # Key RIGHT
					sounds[1].play()
					self.systems.Next()
				elif event.key == K_LEFT and not self._locked.Get():         # Key LEFY
					sounds[1].play()
					self.systems.Prev()
				elif event.key == K_DOWN:                                    # Key DOWN
					sounds[2].play()
					self.game_pointers[self.systems.GetFocusedIndex()].Inc()
				elif event.key == K_UP:                                      # Key UP
					sounds[2].play()
					self.game_pointers[self.systems.GetFocusedIndex()].Dec()
				elif event.key == K_PAGEUP:                                  # Shift + UP
					self.game_pointers[self.systems.GetFocusedIndex()].Dec(10)
				elif event.key == K_PAGEDOWN:                                # Shift + DOWN
					self.game_pointers[self.systems.GetFocusedIndex()].Inc(10)
				# check dialog keys
				elif event.key == K_LSHIFT:                                  # Button 4 = Exit Conjurer
					self._exitTimer -= 1
					self._showDialog = 1 if self._exitTimer < 4 else 0
				elif event.key == K_z:                                       # Button 5 = Show Notes for game, if any
					self._exitTimer = 4
					self._showDialog = 2 if self._showDialog != 2 else 0
				elif event.key == K_x:                                       # Button 6 = Power off
					self._exitTimer -= 1
					self._showDialog = 3 if self._exitTimer < 4 else 0
				# move to letter in list
				elif 96 < event.key < 120:
					self.goToLetter(event.key)
				# Reset counters
				if event.key != K_LSHIFT and event.key != K_x and event.key != K_z:
					self._exitTimer = 4
					self._showDialog = 0


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


version = 1.29		# ( goto letter via keypress )
cmd_options = getCommandlineOptions()

if cmd_options.testPaths:
	TestPaths()
	sys.exit('Done testing!\n')
elif cmd_options.version:
	print('\n   Conjurer Version is', str(version))
	sys.exit('')

# start main program
conjurer_handle = Conjurer(cmd_options)
print('\n  Application terminated...\n')




# --- Todo ----------------------------------------------------------------------
# - NB! : Add XYZ as searchable!














