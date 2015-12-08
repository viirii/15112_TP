# Battle Puzzle Bobble
# Christine Baek
# Term Project - Carnegie Mellon University 15-112 Fall 2015
# server code for multi-player mode
# Multiplayer/socket CA-talk code used as starter for sockets codes but modified/adopted for this game

import socket
from _thread import *
from queue import Queue

HOST = ''
PORT = 50008
BACKLOG = 4

clientele = {} # list of players connected
currID = 0 # keep track of player IDs
playerItem = [] # keeps track of which items players are using
playersReady = [] # keeps track of which players have readied
playersInPlay = [] # keeps track of which players are alive
gameInSession = False
winnerID = -1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")

# initialized once with server for clientele
def serverThread(clientele, serverChannel):
  while True:
    # handle incoming msg
    print("test")
    msg = serverChannel.get(True, None)
    print("msg recv: ", msg)
    senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:])
    if (msg):
      if msg == "1" :
        playersReady[senderID] = True
        if checkGameStart() : startGame(clientele, serverChannel)
      elif msg == "0" :
        playersInPlay[senderID] = False
      else : # player used item
        handleItems(msg, senderID)
    serverChannel.task_done()
    handleGameplay()

serverChannel = Queue(100)
start_new_thread(serverThread, (clientele, serverChannel))

# check if all players are Ready
def checkGameStart() :
  for player in playersReady :
    if player == False : return False
  print(playersReady)
  return True

def startGame(clientele, serverChannel) :
  gameInSession = True
  for cID in clientele:
    clientele[cID].send(bytes("allReady\n", "UTF-8"))
  # update all players as playing
  for player in range(len(playersInPlay)) : 
    playersInPlay[player] = True
  print("start")

# handle message received from client
def handleClient(client, serverChannel, cID):
  client.setblocking(1)
  msg = ""
  while True:
    try : 
      msg += client.recv(10).decode("UTF-8")
      command = msg.split("\n")
      if (len(command) > 1):
        readyMsg = command[0]
        msg = "\n".join(command[1:])
        serverChannel.put(str(cID) + "_" + readyMsg)
    except :
      print("client disconnect?", client) # remove client
      print(clientele)

# check the SD list to see if any user has active shield/deflector
def scanSD(senderID) :
  noHitList = []
  # original sender exempt from item only if there is no one with deflector
  if "D" not in playerItem :
    noHitList.append(senderID)
  for player in playerItem :
    if player != "" :
      noHitList.append(player)
  return noHitList

# handle items used by clients
def handleItems(item, senderID) :
  print("senderID ", senderID, item)
  if item == "end" : playerItem[senderID] = ""
  if item == "shield" : playerItem[senderID] = "S"
  elif item == "deflect" : playerItem[senderID] = "D"
  else : # all attack items
    for cID in clientele:
      print("cID ", cID)
      if len(scanSD(senderID)) == 0: # check if anyone has shield/deflect
        if cID != senderID:
          sendMsg = "itemUsed " +  str(senderID) + " " + item + "\n"
          clientele[cID].send(bytes(sendMsg, "UTF-8"))
      else :
        saved = scanSD(senderID)
        if cID in saved : continue
        else :
          sendMsg = "itemUsed " +  str(senderID) + " " + item + "\n"
          clientele[cID].send(bytes(sendMsg, "UTF-8"))   
  print(clientele)
  print("item", playerItem)
  print("read", playersReady)
  print("play", playersInPlay)

# run/mediate game
def handleGameplay() :
  global gameInSession
  if gameInSession : # check following only when game is in session
    if checkGameOver() : # checks if game is over / one player remains
      gameOverAction()

# check if the game is over
def checkGameOver() :
  livePlayers = 0
  livePlayerIndex = -1
  for player in range(len(playersInPlay)) :
    if playersInPlay[player] == True : 
      livePlayers += 1
      livePlayerIndex = player
  if livePlayers == 1 : 
    winnerID = livePlayerIndex
    return True
  return False

# series of actions to take if the game is over
def gameOverAction() : 
  gameInSession = False
  for player in range(len(playersReady)) :
    playersReady[player] = False
  for player in range(len(playersInPlay)) :
    playersInPlay[player] = False
  if winnerID > -1 :
    for cID in clientele :
      clientele[cID].send(bytes("Winner ", winnerID, "UTF-8"))
  winnerID = -1

while True:
  client, address = server.accept()
  playersReady.append(False)
  playersInPlay.append(False)
  playerItem.append("")
  print("currID = ", currID)
  for cID in clientele:
    clientele[cID].send(bytes("newPlayer " + str(currID) + "\n", "UTF-8"))
    client.send(bytes("newPlayer " + str(cID) + "\n", "UTF-8"))
  clientele[currID] = client
  print("connection recieved")
  start_new_thread(handleClient, (client,serverChannel, currID))
  currID += 1


