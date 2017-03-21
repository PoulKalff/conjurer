import sys, urllib2
from bs4 import BeautifulSoup
from xml.dom.minidom import parse

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
        print "  Looking up '" + name + "'...",
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
        print "matches:", len(gameInfo)
        return gameInfo

    def findGame_tgdb(self, name, platform):
        """ Searches for NAME and returns a dictionary of name:id of found matches"""
        print "  Looking up '" + name + "' on '" + platform + "'...",
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
        print "matches:", len(gameInfo)
        return gameInfo

    def showList(self, gameInfo):
        """ Displays the content of a dictionary of name:id of found matches"""
        print ' ', 110 * '-'
        for key in gameInfo:
            print '   ', key, ' : ', 
            print ' ' * (100 - len(key) - len(str(gameInfo[key]))),
            print gameInfo[key]
        print ' ', 110 * '-'
        print

    def getList(self, file, system):
        """ Loads a conjurer xml-file and returns a list of all game names by platform"""
        print
        print "  Searching through '" + file + "'... ",
        file_ind = open(file, 'r')
        games = []
        SortParser = parse(file_ind)
        file_ind.close()
        for Game in SortParser.getElementsByTagName('game'):
            if Game.getElementsByTagName('system')[0].childNodes[0].nodeValue == system:
                games.append(str(Game.getElementsByTagName('name')[0].childNodes[0].nodeValue))
        print "found", len(games), "games in file"
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
            sys.exit('Must have list')

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
            return len(self.liste) / 2
        else:
            return (len(self.liste) / 2) - 1

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















