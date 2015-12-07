# Battle Puzzle Bobble
# Christine Baek
# Term Project - Carnegie Mellon University 15-112 Fall 2015
# starter code / run function : events-example0.py on 15-112 website
# Multiplayer/socket CA-talk code used as starter for sockets codes but modified/adopted for this game
# Multiplayer codes that used the above are marked with

from tkinter import *
import math
import random
import socket
from _thread import *
from queue import Queue

#############################################################################
# init
#############################################################################

def dimensions(data) :
    data.width = 680
    data.height = 480
    data.topMenu = 36
    data.sideMenu = 186
    data.border = 18
    data.dino = 70
    data.bottomMenu = 18
    data.sidecolor = "purple"
    data.menucolor = "turquoise"
    data.bordercolor = "pink"
    data.linecolor = "green"
    data.rows = 12
    data.cols = 8

def mainScreen(data) :
    data.mainMenuSize = 50
    data.selectedMenu = 0
    data.mainMenuX = 200
    data.mainMenu = ["Single Player", "Multi Player", "High Score", "Settings"]

def gameplay(data) :
    data.guide = False # shows guideline for where the bubble goes
    data.level = 1
    data.shotAngle = math.pi/2
    data.anchor = math.pi/2 # should be between math.pi/6 and math.pi*(5/6)
    data.anchorMin = math.pi/4
    data.anchorMax = math.pi*(3/4)
    data.anchorInc = math.pi/24
    data.anchorLen = 40
    data.anchorX = data.width//2 
    data.anchorY = data.height-(data.bottomMenu+data.dino)
    data.r = 17
    data.tangentHeight = 3**0.5*data.r
    data.bounce = False # has the ball bounced off wall ?

def temporaryBubbles(data) :
    data.tempBagX = data.sideMenu + 30
    data.tempBagY = data.height - 30
    data.tempAnchorX = data.width//2
    data.tempAnchorY = data.height-(data.bottomMenu+data.dino)
    data.bubbleVelocity = 10
    data.canShoot = True
    data.oddNeighbors = [(-1,0), (-1,+1), (0,-1), (0,+1), (+1,0), (+1,+1)]
    data.evenNeighbors = [(-1,-1), (-1,0), (0,-1), (0,+1), (+1,-1), (+1,0)]

# Read the outline of different levels from a txt file
def readLevelFile(data) :
    allLevels = []
    eachLevel = []
    for line in readFile("level.txt").splitlines() :
        if line.startswith("***") :
            allLevels.append(eachLevel)
            eachLevel = []
        elif line.startswith("COLOR") : 
            for elem in line.split() :
                if elem.startswith("COLOR") : color = elem[7:-1] 
                else : 
                    row, col = int(elem[1]), int(elem[3])
                    eachLevel.append((row, col, color))
    return allLevels

# set up the initial bubble layout as defined by the level
def initializeLevel(data) :
    level = data.curLevel
    for bubble in data.levels[level] :
        row, col, color = bubble
        addBubble(data, row, col, color)
        data.bubbleColor.update([color])
    starterBubble(data) # add new bubble to anchor
    newBubble(data) # add new bubble to bag

def initMaster(data) :
    MasterList = []
    for row in range(data.rows) :
        MasterList += [[None]*data.cols]
    return MasterList

def starterBubble(data) :
    color = random.choice(list(data.bubbleColor))
    startBubble = tempBubble(-2, -2, data.tempAnchorX, data.tempAnchorY, color)
    data.tempBubbles.append(startBubble)

def shootBubble(data) :
    data.destCol = -1 
    data.destRow = -1 
    data.blockerCol = -1 
    data.blockerRow = -1 

def itemBububles(data) :
    data.helpFeatures = ["guideline", "shield", "deflect", "freeze", "freeze", "removeLine"]
    data.attackFeatures = ["addBubble", "mask", "addLine"]

def multiPlayermode(data) :
    data.gameOn = False # turned on once all players are Ready
    data.playerReady = False
    data.otherPlayers = []
    data.items = []

def init(data):
    # load data.xyz as appropriate
    data.mode = "main"
    data.paused = False
    data.curLevel = 0
    dimensions(data)
    mainScreen(data) # main/splash screen data
    data.bubbleColor = set() # keep track of which colors are in play
    data.levels = readLevelFile(data) # read levels from txt
    data.bubbles = initMaster(data) # static bubble list
    temporaryBubbles(data) # coodinates / data for bubbles in tempBubble class
    data.tempBubbles = [] # stores the 2 temp bubbles
    initializeLevel(data) # load the level defined in data.curLevel
    data.gameOver = False
    gameplay(data) # data for shooting / gameplay 
    shootBubble(data) # trajectory of each bubble shot

#############################################################################
# screen/mode switch
#############################################################################

def mousePressed(event, data):
    # use event.x and event.y
    if (data.mode == "main") : pass
    elif (data.mode == "solo") : pass
    elif (data.mode == "multi") : pass
    elif (data.mode == "highscore") : pass
    elif (data.mode == "settings") : pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if (data.mode == "main") : mainKeyPressed(event, data)
    elif (data.mode == "solo") : soloKeyPressed(event, data)
    elif (data.mode == "multi") : multiKeyPressed(event, data)
    elif (data.mode == "highscore") : hsKeyPressed(event, data)
    elif (data.mode == "settings") : settingsKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "main") : pass
    elif (data.mode == "solo") : soloTimerFired(data)
    elif (data.mode == "multi") : multiTimerFired(data)
    elif (data.mode == "highscore") : pass
    elif (data.mode == "settings") : pass

def redrawAll(canvas, data):
    # draw in canvas
    if (data.mode == "main") : mainReDrawAll(canvas, data)
    elif (data.mode == "solo") : soloReDrawAll(canvas, data)
    elif (data.mode == "multi") : multiReDrawAll(canvas, data)
    elif (data.mode == "highscore") : hsReDrawAll(canvas, data)
    elif (data.mode == "settings") : settingsReDrawAll(canvas, data)

#############################################################################
# main screen
#############################################################################

HOST = ''
PORT = 50009
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
serverMsg = Queue(100)

def mainKeyPressed(event, data) :
    if event.keysym == "Up" :
        if data.selectedMenu > 0 : 
            data.selectedMenu -= 1
    elif event.keysym == "Down" :
        if data.selectedMenu < (len(data.mainMenu)-1) : 
            data.selectedMenu += 1
    elif event.keysym == "Return" :
        goToSelectedMenu(data)

# change mode to the selected item on menu
def goToSelectedMenu(data) :
    if data.selectedMenu == 0 : data.mode = "solo"
    elif data.selectedMenu == 1 : 
        data.mode = "multi"
        multiPlayermode(data)
        server.connect((HOST,PORT))
        print("connected to server")
        start_new_thread(handleServerMsg, (server, serverMsg))
    elif data.selectedMenu == 2 : data.mode = "highscore"
    elif data.selectedMenu == 3 : data.mode = "settings"
 
# draw the main screen
def drawMenu(canvas, data) :
    size = data.mainMenuSize
    triangle = 1/2*size
    for entry in range(len(data.mainMenu)) :
        x = data.mainMenuX
        y = data.height//2 + size * (entry-2)
        # Draw triangle for selected menu
        if entry == data.selectedMenu : 
            canvas.create_polygon(x-size, y+(1/2)*triangle, 
                x-size, y+(3/2)*triangle, x-triangle, y+triangle, 
                fill="magenta")
        # Draw the menu entries
        canvas.create_text(x, y, text=data.mainMenu[entry], 
            font="Helvetica 40 bold", anchor=NW)

def mainReDrawAll(canvas, data) :
    drawMenu(canvas, data)

#############################################################################
# play Functions - shared between solo and multi mode
#############################################################################

# select and place a new bubble with random color from palette
def newBubble(data) :
    color = random.choice(list(data.bubbleColor))
    newBubble = tempBubble(-2, -2, data.tempBagX, data.tempBagY, color)
    data.tempBubbles.append(newBubble)

# add bubble to the static bubble list
def addBubble(data, row, col, color) :
    x, y = Bubble.getXY(data, row, col)
    newBubble = Bubble(row, col, x, y, color)
    data.bubbles[row][col] = newBubble

# bubble is shot on the board
def shoot(data) :
    # store the angle of the anchor @ the time of shot
    data.canShoot = False
    data.shotAngle = data.anchor
    # move the bubble & place it on the board
    shooter = data.tempBubbles[0]
    shooter.dx = data.bubbleVelocity * math.cos(data.shotAngle)
    shooter.dy = data.bubbleVelocity * math.sin(data.shotAngle)
    # move over the bubble that was in bag to its new spot
    bagBubble = data.tempBubbles[1]
    bagBubble.x = data.tempAnchorX
    bagBubble.y = data.tempAnchorY
    Bubble = newBubble(data)
    destination, blocker = checkDestination(data)
    data.destRow, data.destCol = destination
    data.blockerRow, data.blockerCol = blocker

# returns list of empty cells in the bubble's trajectory
def destination(data) :
    leftMargin = data.sideMenu + data.border
    height = data.tangentHeight
    path = []
    for row in range(data.rows-1, -1, -1) :
        destX = data.anchorX - height // (math.tan(data.shotAngle))
        if row % 2 == 0 :
            col = int((destX - leftMargin)//(2*data.r))
            if col > 7 : 
                col = 7-abs(col-7)
                data.bounce = not data.bounce
            if col < 0 : 
                col = -col
                data.bounce = not data.bounce
        else : 
            col = int((destX - leftMargin-data.r)//(2*data.r))
            if col > 6 : 
                col = 7-abs(col-6)
                data.bounce = not data.bounce
            if col == -1 : 
                col = 0
                data.bounce = not data.bounce
            if col < 0 : 
                col = abs(col)-2
                data.bounce = not data.bounce
        if data.bubbles[row][col] == None : # path/cell is empty
            path.append((row, col))
            height += data.tangentHeight # check next row
            if row == 0 :
                path.append((-1, -1))
                break
        else :
            path.append((row, col)) # add the one that 'blocked' 
            break
    print(path)
    return path

# check where the moving bubble will end up in based on its traectory at the time of shot
def checkDestination(data) :
    # check if the destination row/col is occuppied 
    path = destination(data)
    # there is nowhere for the bubble to go
    if len(path) == 1 : data.gameOver = True
    else : 
        # given the list of bubble's trajectory cells, check if it can pass through the neighbors at all points
        for index in range(len(path)-1) : # check all neighbors except for 'certified blocker bubble'
            row, col = path[index]
            neighbors = [-1, +1]
            for neighbor in neighbors :
                if 0 <= col + neighbor < 8 :
                    neighborBubble = data.bubbles[row][col+neighbor]
                    if neighborBubble != None :
                        check = tempBubble.canPass(data, neighborBubble)
                        print(check)
                        if check == False : # if the bubble can't pass through :
                            destRow, destCol = path[index-1]
                            blockerRow, blockerCol = row, col+neighbor
                            # modify path for extremely angled shots
                            return editDestination(data, destRow, destCol, blockerRow, blockerCol)
        destRow, destCol = path[-2]
        blockerRow, blockerCol = path[-1]
        #if blockerRow == -1 : 
        return ((destRow, destCol), (blockerRow, blockerCol))
        #return editDestination(data, destRow, destCol, blockerRow, blockerCol)

# modify the destination of moving bubble depending on the row & trajectory
def editDestination(data, destRow, destCol, blockerRow, blockerCol) :
    if destRow % 2 == 0 : # even row
        if (destCol - blockerCol) == 2 : destCol = blockerCol + 1
        elif (destCol - blockerCol) > 2 : 
            destRow, destCol = blockerRow, blockerCol+1
        elif (blockerCol - destCol) == 1 : destCol = blockerCol
        elif (blockerCol - destCol) > 1 : 
            destRow, destCol = blockerRow, blockerCol-1
    else : # odd row
        if (destCol - blockerCol) == 1 : destCol = blockerCol
        elif (destCol - blockerCol) > 1 : 
            destRow, destCol = blockerRow, blockerCol + 1
        elif (blockerCol - destCol) == 2 : destCol = blockerCol-1
        elif (blockerCol - destCol) > 2 : 
            destRow, destCol = blockerRow, blockerCol-1
    return ((destRow, destCol), (blockerRow, blockerCol))

# check if the level is won, and move to the next level
# level is finished if there are no bubbles attached to the top
def checkGameWon(data) :
    for bubble in data.bubbles[0] :
        if bubble != None : return 
    if data.curLevel < len(data.levels) - 1 : data.curLevel += 1
    else : data.curLevel = 0
    data.bubbleColor = set()
    data.tempBubbles = []
    initializeLevel(data)

# check if game is over by checking if there are any bubbles in the last row
def checkGameOver(data) :
    for bubble in data.bubbles[data.rows-1] :
        if bubble != None :
            data.gameOver = True

# when the moving bubble collides with the static bubble
# check if bubble & its neighbors can be popped and pop if applicable
def reorganizeBubble(data) :
    shooter = data.tempBubbles[0]
    popList = Bubble.neighborPop(data, data.destRow, data.destCol, shooter.color)
    if len(popList) > 2 : 
        for elem in popList :
            row, col = elem
            data.bubbles[row][col] = None
    data.tempBubbles.pop(0)

# check to see if each bubble is still connected to the top of the board somehow          
def dropBubble(data) :
    for row in range(len(data.bubbles)) :
        for col in range(len(data.bubbles[row])) :
            bubble = data.bubbles[row][col]
            if bubble != None : 
                # check if each bubble is still connected to the top of the board
                check = checkConnection(data, row, col)
                if not check :
                    data.bubbles[row][col] = None # bubble is removed

# check if the bubble @ given row & col is connected
def checkConnection(data, row, col) :
    link = set()
    def check(newRow, newCol) :
        if (newRow, newCol) in link : return False
        link.add((newRow, newCol))
        if newRow == 0 and data.bubbles[newRow][newCol] != None : return True
        # recursion !! Woohoo!!
        if newRow % 2 == 1 : neighbors = data.oddNeighbors
        elif newRow % 2 == 0 : neighbors = data.evenNeighbors
        for neighbor in neighbors :
            dRow, dCol = neighbor
            if data.bubbles[newRow+dRow][newCol+dCol] != None :
                if check(newRow+dRow, newCol+dCol) : return True
        link.remove((newRow, newCol))
        return False
    return True if check(row, col) else False

# collection of functions to run after moving bubble collides
def processPostCol(data, color) :
    data.canShoot = True
    addBubble(data, data.destRow, data.destCol, color)
    reorganizeBubble(data)
    dropBubble(data)
    checkGameWon(data)

#############################################################################
# draw Functions - shared between solo and multi mode
#############################################################################

# draw the background/static part
def drawBG(canvas, data) :
    # left
    canvas.create_rectangle(0,0,data.sideMenu, data.height, 
        width=0, fill=data.menucolor)
    # right
    canvas.create_rectangle(data.width-data.sideMenu, 0, 
        data.width, data.height, width=0, fill=data.menucolor)    
    # top
    canvas.create_rectangle(0,0, data.width, data.topMenu, 
        width=0, fill=data.sidecolor)
    # bottom
    canvas.create_rectangle(0,data.height-data.bottomMenu, 
        data.width, data.height, width=0, fill=data.sidecolor)
    # dinos
    canvas.create_line(data.sideMenu,data.height-(data.bottomMenu+data.dino), data.width-data.sideMenu, data.height-(data.bottomMenu+data.dino), width=3, fill=data.linecolor)
    # left border
    canvas.create_rectangle(data.sideMenu, data.topMenu, 
        data.sideMenu+data.border, data.height-data.bottomMenu, 
        width=0, fill=data.bordercolor)
    # right border
    canvas.create_rectangle(data.width-data.sideMenu-data.border, 
        data.topMenu, data.width-data.sideMenu, data.height-data.bottomMenu,
         width=0, fill=data.bordercolor)    
    # top border
    canvas.create_rectangle(data.sideMenu, data.topMenu, 
        data.width-data.sideMenu, data.topMenu+data.border, 
        width=0, fill=data.bordercolor)
    # draw anchor (static part)
    # draw bubble bag

# draw the anchor shooting the bubble
def drawAnchor(canvas, data) :
    x = data.anchorX
    y = data.anchorY
    anchorTop = data.anchorLen
    anchorBot = data.anchorLen//2
    x0 = x - anchorTop * math.cos(data.anchor)
    y0 = y - anchorTop * math.sin(data.anchor)
    x1 = x + anchorBot * math.cos(data.anchor)
    y1 = y + anchorBot * math.sin(data.anchor)
    canvas.create_line(x0, y0, x1, y1, fill="orange", width=5)    

# draw if game is over
def drawGameOver(canvas, data) :
    canvas.create_text(data.width//2, data.height//2, text="Game Over")

#############################################################################
# solo player mode
#############################################################################

def soloKeyPressed(event, data) :
    if event.keysym == "Escape" :
        init(data)
    if not data.gameOver :
        if data.canShoot : 
            if event.keysym == "space" :
                shoot(data)
        if event.keysym == "P" :
            data.paused = not data.paused
        elif event.keysym == "G" :
            data.guide = not data.guide
        elif event.keysym == "Left" :
            if data.anchorMin < data.anchor :
                data.anchor -= data.anchorInc
        elif event.keysym == "Right" :
            if data.anchor < data.anchorMax :
                data.anchor += data.anchorInc

def soloTimerFired(data) :
    shooter = data.tempBubbles[0]
    color = shooter.color
    shooter.move(data)
    blocker = data.bubbles[data.blockerRow][data.blockerCol]
    if data.blockerRow == -1 :
        if shooter.hitTop(data) :
            processPostCol(data, color)
    if blocker != None :
        if shooter.isCol(blocker, data) :
            processPostCol(data, color)
    checkGameOver(data)

def soloReDrawAll(canvas, data) :
    drawBG(canvas, data)
    drawAnchor(canvas, data)
    for row in range(len(data.bubbles)):
        for bubble in data.bubbles[row] :
            if bubble != None :
                bubble.draw(canvas)
    for tempBubble in data.tempBubbles :
        tempBubble.draw(canvas)
    if data.gameOver :
        drawGameOver(canvas, data)

#############################################################################
# item bubble handling
#############################################################################

# attack bubble has been used
def applyOtherItem(data, item) : 
    if item == "addBubble" : pass
    elif item == "mask" : pass
    elif item == "addLine" : pass

def generateItemBubble(data) :
    pass

# use the self-help item bubble
def useItem(data, item) :
    if item == "guideline" : pass 
    elif item == "shield" : pass
    elif item == "deflect" : pass
    elif item == "freeze" : pass
    elif item == "removeLine" : removeLine(data)

def removeLine(data) :
    for row in range(len(data.bubbles)-1):
        for col in range(len(data.bubbles[row])) :
            bubble[row][col] = bubble[row+1][col]
    lastRow = data.rows - 1
    for col in range(len(data.bubbles[lastRow])) :
        bubble[lastRow][col] = None       

#############################################################################
# multi player data / thread / socket / queue 
# This section has been modified from the CA-led talk
#############################################################################

# modified from CA-led talk
def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    if (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)

# modified from CA-led talk
def handleMsg(data) :
    if (serverMsg.qsize() > 0):
        msg = serverMsg.get(False)
        try:
            print("recieved: ", msg)
            print(data.otherStrangers)
            if msg.startswith("newPlayer"):
                msg = msg.split()
                newPID = int(msg[1])
                data.otherPlayers.append(newPID)
            elif msg.startswith("itemUsed"):
                msg = msg.split()
                PID = int(msg[1])
                item = string(msg[2])
                applyOtherItem(data, item) # other player used attack item on me
            elif msg.startswith("allReady") :
                data.gameOn = True
            elif msg.startswith("Winner") :
                msg = msg.split()
                winnerID = int(msg[1])
        except:
            print("failed")
        serverMsg.task_done()

#############################################################################
# multi player mode
# some codes in this section have been modified from CA-led talk
#############################################################################

# modified from CA-led talk
def multiKeyPressed(event, data) :
    signal = -1
    if event.keysym == "Escape" :
        init(data)
        # disconnect with the server
    elif event.keysym == "R" or event.keysym == "r" :
        print("r")
        data.playerReady = not data.playerReady
        signal = 1
    if not data.gameOver :
        if data.canShoot : 
            if event.keysym == "space" :
                shoot(data) # shoot dat bubble
            elif event.keysym == "Left" :
                if data.anchorMin < data.anchor :
                    data.anchor -= data.anchorInc
            elif event.keysym == "Right" :
                if data.anchor < data.anchorMax :
                    data.anchor += data.anchorInc
            elif event.keysym == "Q" or event.keysym == "q" :
                print("q")
                data.gameOver = True
                signal = 0
            elif event.keysym == "Z" or event.keysym == "z" :
                print("z")
                if len(data.items) > 0 :
                    item = data.items[0].feature
                    useItem(data, item)
                    if data.items[0].type == "attack" :
                        signal = data.items[0].identity
    if signal >= 0 :
        msg = "%d\n" % (signal)
        print("sending: ", msg, end="")
        data.server.send(bytes(msg, "UTF-8"))
        signal = -1
    # signal = -1
    # if event.keysym == "Q" or event.keysym == "q" :
    #     print("q")
    #     data.gameOver = True
    #     signal = 0
    # elif event.keysym == "R" or event.keysym == "r" :
    #     print("r")
    #     data.playerReady = not data.playerReady
    #     signal = 1
    # elif event.keysym == "Z" or event.keysym == "z" :
    #     print("z")
    #     if len(data.items) > 0 :
    #         useItem(data)
    #         if data.items[0].type == "attack" :
    #             signal = data.items[0].identity
    # if signal >= 0 :
    #     msg = "%d\n" % (signal)
    #     print("sending: ", msg, end="")
    #     print("")
    #     print("SENT MSG", bytes(msg, "UTF-8"))
    #     data.server.send(bytes(msg, "UTF-8"))


def multiTimerFired(data) :
    # handle messages
    handleMsg(data)
    # gameplay
    shooter = data.tempBubbles[0]
    color = shooter.color
    shooter.move(data)
    blocker = data.bubbles[data.blockerRow][data.blockerCol]
    if data.blockerRow == -1 :
        if shooter.hitTop(data) :
            processPostCol(data, color)
    if blocker != None :
        if shooter.isCol(blocker, data) :
            processPostCol(data, color)
    checkGameOver(data)

def multiReDrawAll(canvas, data) :
    drawBG(canvas, data)
    drawAnchor(canvas, data)
    for row in range(len(data.bubbles)):
        for bubble in data.bubbles[row] :
            if bubble != None :
                bubble.draw(canvas)
    for tempBubble in data.tempBubbles :
        tempBubble.draw(canvas)
    if data.gameOver :
        drawGameOver(canvas, data)

#############################################################################
# high score screen
#############################################################################

def hsKeypressed(event, data) :
    pass

def hsReDrawall(canvas, data) :
    pass

#############################################################################
# settings
#############################################################################

def settingsKeyPressed(event, data) :
    pass

def settingsReDrawAll(canvas, data) :
    pass

#############################################################################
# Classes
#############################################################################

class Bubble(object) :
    r = 17 # bubble size
    def __init__(self, row, col, x, y, color) :
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.r = Bubble.r # Bubble diameter = 34px
        self.color = color

    def __repr__(self) :
        return "%d %d %s" % (self.row, self.col, self.color)

    def draw(self, canvas) :
        x = self.x
        y = self.y
        r = self.r
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.color)

    @staticmethod
    def getXY(data, row, col) :
        r = Bubble.r
        tangentHeight = 3**0.5*r
        leftMargin = data.sideMenu + data.border
        topMargin = data.topMenu + data.border
        if row % 2 == 0 :
            x = leftMargin + (2*col+1) * r
        else : 
            x = leftMargin + 2*(col+1) * r
        if row == 0 :
            y = topMargin + r
        else :
            y = topMargin + r + row*tangentHeight
        return x, y

    @staticmethod
    def neighborPop(data, popRow, popCol, color) : # input the newly added bubble's row/col/color
        popList = set()
        checked = []
        def search(row, col) :
            if (row, col) in checked : return          
            else : 
                checked.append((row, col))                              
                if row % 2 == 1 :
                    neighbors = data.oddNeighbors
                else :
                    neighbors = data.evenNeighbors 
                for neighbor in neighbors :
                    dRow, dCol = neighbor
                    newRow = row + dRow
                    newCol = col + dCol
                    if 0 <= newRow < data.rows and 0 <= newCol < data.cols :
                        bubble = data.bubbles[newRow][newCol]
                        if bubble != None :
                            if bubble.color == color :
                                popList.add((row,col))
                                search(newRow, newCol) 
        search(popRow, popCol)
        return popList

class tempBubble(Bubble) :
    def __init__(self, row, col, x, y, color) :
        super().__init__(row, col, x, y, color)
        self.row = -2
        self.col = -2
        self.dx = 0
        self.dy = 0
        self.wallHit = 0

    def draw(self, canvas) :
        super().draw(canvas)    

    def move(self, data) :
        leftBound = data.sideMenu+data.border+self.r
        rightBound = data.width-data.sideMenu-data.border-self.r
        self.x -= self.dx
        self.y -= self.dy
        if self.x < leftBound or self.x > rightBound :
            self.dx = -self.dx
            self.wallHit += 1 

    def hitTop(self, data) :
        topBound = data.topMenu+data.border
        if (self.y - self.r - data.bubbleVelocity * math.sin(data.shotAngle)) < topBound :
            return True
        return False

    def isCol(self, bubble, data) :
        if ((self.x-bubble.x)**2 + (self.y-bubble.y)**2)**0.5 <= (2*self.r + data.bubbleVelocity) : return True
        else : return False

    @staticmethod
    # finds closest point of shooter bubble & neighbor bubble, and see if it can pass
    def canPass(data, bubble) :
        r = Bubble.r
        if data.bounce : data.shotAngle = -1/(data.shotAngle)
        shooterm = math.tan(data.shotAngle)
        bubblem = -1/(shooterm)
        bubbleb = bubble.y-(bubblem*bubble.x)
        shooterb = data.anchorY-(shooterm*data.anchorX)
        shooterx = (bubbleb-shooterb)/(shooterm-bubblem)
        shootery = shooterm*shooterx + shooterb
        print(shooterm, bubblem, bubbleb, shooterb, shooterx, shootery)
        if ((bubble.x-shooterx)**2+(bubble.y-shootery)**2)**0.5 < 2*r : 
            return False
        else : return True

class Item(Bubble) :
    def __init__(self, feature, Bubbletype) :
        super().__init__(self)
        self.feature = feature
        self.type = Bubbletype # attack or help

#############################################################################
# graphics & Run function
# functions below this line are from 15-112 website Graphics & Strings week
# they were used as-is with minimal to no modification
# all codes above this section are either original, 
# or heavily modified from 15-112 provided code (commented appropriately)
#############################################################################

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

def run(width=680, height=480, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 3 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(680, 480, serverMsg, server)