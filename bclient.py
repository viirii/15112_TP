import socket
from _thread import *
from queue import Queue


HOST = '67.171.68.212'
PORT = 50009

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

server.connect((HOST,PORT))
print("connected to server")

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

# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *

####################################
# customize these functions
####################################

def init(data):
    data.playerReady = False
    data.otherPlayers = []
    data.items = []
    data.mode = "main"

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    signal = -1
    if event.keysym == "Q" or event.keysym == "q" :
        print("q")
        data.gameOver = True
        signal = 0
    elif event.keysym == "R" or event.keysym == "r" :
        print("r")
        data.playerReady = not data.playerReady
        signal = 1
    elif event.keysym == "Z" or event.keysym == "z" :
        print("z")
        if len(data.items) > 0 :
            useItem(data)
            if data.items[0].type == "attack" :
                signal = data.items[0].identity
    if signal >= 0 :
        msg = "%d\n" % (signal)
        print("sending: ", msg, end="")
        print("")
        print("SENT MSG", bytes(msg, "UTF-8"))
        data.server.send(bytes(msg, "UTF-8"))

def timerFired(data):
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
                applyItem(data) # other player used attack item on me
            elif msg.startswith("allReady") :
                data.gameOn = True
            elif msg.startswith("Winner") :
                msg = msg.split()
                winnerID = int(msg[1])
        except:
            print("failed")
            serverMsg.task_done()

def redrawAll(canvas, data) :
    pass

####################################
# use the run function as-is
####################################

def run(width, height, serverMsg=None, server=None):
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
    data.timerDelay = 100 # milliseconds
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

serverMsg = Queue(100)
start_new_thread(handleServerMsg, (server, serverMsg))

run(200, 200, serverMsg, server)