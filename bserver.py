# Battle Puzzle Bobble
# Christine Baek
# Term Project - Carnegie Mellon University 15-112 Fall 2015
# server code for multi-player mode
# Multiplayer/socket CA-talk code used as starter for sockets codes but modified/adopted for this game

import socket
from _thread import *
from queue import Queue

HOST = ''
PORT = 50009
BACKLOG = 4

clientele = {} # list of players connected
currID = 0 # keep track of player IDs
playersReady = [] # keeps track of which players have readied
playersInPlay = [] # keeps track of which players are alive
gameInSession = False
winnerID = -1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")

def handleClient(client, serverChannel, cID):
  client.setblocking(1)
  msg = ""
  while True:
    msg += client.recv(10).decode("UTF-8")
    command = msg.split("\n")
    if (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverChannel.put(str(cID) + "_" + readyMsg)

# initialized once with server for clientele
def serverThread(clientele, serverChannel):
  while True:
    print("test")
    msg = serverChannel.get(True, None)
    print("msg recv: ", msg)
    senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:])
    if (msg):
      print(msg)
      if msg == "1" :
        playersReady[senderID] = True
      elif msg == "0" :
        playersInPlay[senderID] = False
      else : # player used item
        for cID in clientele:
          if cID != senderID:
            sendMsg = "itemUsed " +  str(senderID) + " " + msg + "\n"
            clientele[cID].send(bytes(sendMsg, "UTF-8"))
    serverChannel.task_done()
      # if all players are ready to play, start game
    if set(playersReady) == True :
      gameInSession = True
      for cID in clientele :
        clientele[cID].send(bytes("allReady", "UTF-8"))
      # update all players as playing
      for player in range(len(playersInPlay)) : 
        playersInPlay[player] = True
    # if gameInSession : # check following only when game is in session
    #   if checkGameOver() : # checks if game is over / one player remains
    #     gameOverAction()



serverChannel = Queue(100)
start_new_thread(serverThread, (clientele, serverChannel))

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
  print(currID)
  for cID in clientele:
    clientele[cID].send(bytes("newPlayer " + str(currID), "UTF-8"))
    client.send(bytes("newPlayer " + str(cID), "UTF-8"))
  clientele[currID] = client
  print("connection recieved")
  start_new_thread(handleClient, (client,serverChannel, currID))
  currID += 1


