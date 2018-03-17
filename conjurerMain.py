import os, sys, pygame
from pygame import font
from pygame.locals import *
from conjurerClasses import FlipSwitch, RangeIterator, StringIterator, SelectExternal
from conjurerFunctions import SortGames, getJoystick

pygame.init()
pygame.mouse.set_visible(0)
pygame.key.set_repeat(500, 100)
font10 =  pygame.font.Font('/usr/share/fonts/truetype/ttf-liberation/LiberationMono-Regular.ttf', 10)
font12 =  pygame.font.Font('/usr/share/fonts/truetype/ttf-liberation/LiberationMono-Regular.ttf', 12)
font14 =  pygame.font.Font('/usr/share/fonts/truetype/ttf-liberation/LiberationMono-Regular.ttf', 14)
font14b = pygame.font.Font('/usr/share/fonts/truetype/ttf-liberation/LiberationMono-Bold.ttf', 14)
font20 =  pygame.font.Font('/usr/share/fonts/truetype/ttf-liberation/LiberationMono-Regular.ttf', 20)
font20b = pygame.font.Font('/usr/share/fonts/truetype/ttf-liberation/LiberationMono-Bold.ttf', 20)
systemExecs = {'Amiga':['uae', ' -0 ', ' -1 ', ' -2 ', ' -3 '], 'Arcade':['mame', ' -inipath . '], 'C64':['x64', ' -autostart ', ' -8 ']}

class Conjurer:
    # Main class

    def __init__(self, options):
        self.joystick = getJoystick()
        self.dontRun = options.dontRun
        self.fonts = [font10, font12, font14, font14b, font20, font20b]
        self.extPath = '/mnt/overlord/6tb_hdd/emulator/ROM'
        self._showPoweroff = 4
        self._showExitProgram = 4
        self._showHelp = FlipSwitch(0)
        self.display = pygame.display.set_mode([800,600])
        self.center_x = self.display.get_rect().centerx
        self.center_y = self.display.get_rect().centery
        self.gamelist = SortGames(options.mpGames)
        self.path_pointer = RangeIterator(5)
        self.systems = StringIterator(self.gamelist.keys())
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
        _command = systemExecs[System][0]
        _count = 0
        for item in FileList:
            _count += 1
            _command += systemExecs[System][_count]
            _command += '"' + item + '"'
        return _command


    def run_game(self, System, FileList):
        """Runs a game of type System, using files in FileList"""

        Command = self._stringBuilder(System, FileList)
        # ----------- Start Process -----------
        if self.dontRun:
            print
            print '(' + Command + ')'
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
        _hw = _image.get_width() / 2
        _hh = _image.get_height() / 2
        self.display.blit(_image,(self.center_x - _hw, self.center_y - _hh))


    def _displayGamesList(self, _systemName, foc_game):
        for entry, nr in enumerate(range(20)):
            if nr + foc_game - 10 < 0 or nr + foc_game - 10 > len(self.gamelist[_systemName]) - 1:
                _game = font20.render(' ', True, (0, 255, 255))
            else:
                if nr == 10:
                    _game = font20b.render(self.gamelist[_systemName][nr + foc_game - 10].Navn, True, (255, 0, 0))
                else:
                    _game = font20.render(self.gamelist[_systemName][nr + foc_game - 10].Navn, True, (0, 255, 255))
            entry_rect = _game.get_rect()
            entry_rect.centerx = self.center_x
            entry_rect.centery = 50 + nr * 25
            self.display.blit(_game, entry_rect)
        return
        # For testing output
        textRect = pygame.Rect(0,0,500,100)
        test_message = font20.render(str(self.ticktime), True, (255, 255, 255), (250,0,0))
        self.display.blit(test_message, textRect)


    def _displaySystems(self, focused, xpos):
        _systems_string1 = font20.render(self.systems.GetLeft(), True, (0, 0, 255))
        _systems_string2 = font20b.render(self.systems.GetCentral() , True, (0, 200, 0))
        _systems_string3 = font20.render(self.systems.GetRight() , True, (0, 0, 255))
        self.display.blit(_systems_string2, pygame.Rect((self.center_x - 50 + (84 - _systems_string2.get_width()) / 2, xpos), (120, 50)))
        if not self._locked.Get():
            self.display.blit(_systems_string1, pygame.Rect((self.center_x - 200 + (84 - _systems_string1.get_width()) / 2, xpos), (120, 50)))
            self.display.blit(_systems_string3, pygame.Rect((self.center_x + 100 + (84 - _systems_string3.get_width()) / 2, xpos), (120, 50)))


    def _render(self):
        self.display.fill((0,0,0))
        self._displayScreen(self.systems.GetCentral(), self.game_pointers[self.systems.GetFocusedIndex()].Get())
        self._displayGamesList(self.systems.GetCentral(), self.game_pointers[self.systems.GetFocusedIndex()].Get())
        self._displaySystems(self.systems.GetCentral(), 550)
        if self._showHelp.Get():
            self._displayHelp()
        elif self._showPoweroff < 4:
            self._displayPoweroff()
        elif self._showExitProgram < 4:
            self._displayExitProgram()
        pygame.display.update()


    def _getUserInput(self):
        """Recieves input from keyboard/joystick while class is active"""
        for event in pygame.event.get():
            # Keyboard keys
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
                    _extSel = SelectExternal(self).Return()
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
                elif event.key == K_LEFT and not self._locked.Get():         # Key LEFT
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
            # Joystick buttons
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if event.button == 0 or event.button == 12:                  # JoystickButton1 = Run selected
                    system = self.systems.GetCentral()
                    no = self.game_pointers[self.systems.GetFocusedIndex()].Get()
                    self.run_game(system, self.gamelist[system][no].Paths)
                elif event.button == 1 or event.button == 13:                # JoystickButton2 = Show Help
                    self._showHelp.flip()
                elif event.button == 2 or event.button == 14:                # JoystickButton3 = File dialogue
                    _extSel = SelectExternal(self).Return()
                    self.run_game(_extSel['system'], _extSel['gameFiles'])
                elif event.button == 3 or event.button == 15:                # JoystickButton4 = NOT CURRENTLY USED
                    pass
                elif event.button == 4 or event.button == 16:                # JoystickButton L1 = 10 games back
                    self.game_pointers[self.systems.GetFocusedIndex()].Dec(10)
                elif event.button == 5 or event.button == 17:                # JoystickButton R1 = 10 games forward
                    self.game_pointers[self.systems.GetFocusedIndex()].Inc(10)
                elif event.button == 6 or event.button == 18:                # JoystickButton L2 = Kill Conjurer
                    self._showExitProgram -= 1
                elif event.button == 7 or event.button == 19:                # JoystickButton R2 = Power off
                    self._showPoweroff -= 1
                # Reset counters
                if event.button != 6 and event.button != 18:
                    self._showExitProgram = 4
                if event.button != 7 and event.button != 19:
                    self._showPoweroff = 4
            # Joystick axis
            elif event.type == pygame.JOYAXISMOTION and event.joy == 0:
                eventVal = round(event.value)
                if event.axis == 0:
                    if eventVal == -1 and not self._locked.Get():  # Joystick LEFT
                        self.systems.Prev()
                    elif eventVal == 1 and not self._locked.Get(): # Joystick RIGHT
                        self.systems.Next()
                elif event.axis == 1:
                    if eventVal == -1:                             # Joystick UP
                        self.game_pointers[self.systems.GetFocusedIndex()].Dec()
                    elif eventVal == 1:                            # Joystick DOWN
                        self.game_pointers[self.systems.GetFocusedIndex()].Inc()
                # Reset counters
                self._showExitProgram = 4
                self._showPoweroff = 4
        return 1


    def _loop(self):
        while self._running:
            self._render()
            self._getUserInput()
        pygame.quit()











