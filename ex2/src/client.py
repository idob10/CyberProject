import socket
import time
import utils
import os
import sys
from server import NEW_CLIENT_MASSAGE
from server import CLOSE_CONNECTION
from server import sendMsg
from server import getMsg
from watchdog.observers import Observer

def connect(sock, path, isNewClient, directoryApplayer):
    # download the current folder at the server
    if not isNewClient:
        msg = getMsg(sock)
        while msg != utils.PROTOCOL_END_OF_MODIFICATION:
            directoryApplayer.handleNewModify(msg)
            msg = getMsg(sock)


def updateServer(sock, directoryApplayer, observer, modify_queue, path):
    # download the new changes
    msg = getMsg(sock)
    while msg != utils.PROTOCOL_END_OF_MODIFICATION:
        directoryApplayer.handleNewModify(msg)
        msg = getMsg(sock)
    
    sock.recv(1024) #recive ack

    # upload the changes
    while len(modify_queue) != 0:
        command = modify_queue.pop(0)
        if (command in list(directoryApplayer.getCmdServer())):
            continue

        if command.split(',')[0] == "created":
            # check if it is a folder
            if command.split(',')[2] == "True":
                sendMsg(sock, command)
                directoryApplayer.sendDir(os.path.join(path, command.split(',')[1]))
            elif command.split(',')[1][-1] == '~':
                duplicate = ""
                # getting out from the queue a duplicate massges of the watchdog
                while not duplicate.split(',')[0] == "deleted":
                    duplicate = modify_queue.pop(0)
                create, filePath, isDir = command.split(',')
                sendMsg(sock, create + ',' + filePath[0 : -1] + ',' +  isDir)
                utils.sendFile(os.path.join(path,filePath[0 : -1]),sock)
            else:
                sendMsg(sock, command)
                utils.sendFile(os.path.join(path,command.split(',')[1]),sock)
        elif command.split(',')[0] == "modified":
            sendMsg(sock, command)
            utils.sendFile(os.path.join(path,command.split(',')[1]),sock)
        else:
            sendMsg(sock, command)

    directoryApplayer.clear()

def main():
    if (len(sys.argv)!=5 or len(sys.argv)!=6):
        print("Args are not valid!")
        return

    # initialize parameters
    ip = sys.argv[1]
    port = sys.argv[2]
    path = sys.argv[3]
    timeout = sys.argv[4]
    id = ""
    if (len(sys.argv)==6):
        id = sys.argv[5]

    # creating a socket
    os.makedirs(path,exist_ok=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    directoryApplayer = utils.DirectoryApplayer(path, sock)

    # In case of a new client
    isNewClient = False
    if id == "":
        sendMsg(sock, NEW_CLIENT_MASSAGE)
        isNewClient = True
        id = getMsg(sock)
        sock.recv(1024)  # change sending order
    else:
        sendMsg(sock, id)
        id = getMsg(sock)

    connect(sock, path, isNewClient, directoryApplayer)
    time.sleep(0.1)
    sendMsg(sock, CLOSE_CONNECTION)
    sock.close()

    #start observing
    modify_queue = []
    directoryObserver = utils.DirectoryObserver(modify_queue, path)
    observer = Observer()
    observer.schedule(directoryObserver, path, recursive=True)
    observer.start()
    while True:
        # connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        directoryApplayer.set_sock(sock)
        sendMsg(sock, id)
        id = getMsg(sock)

        # sync with the server
        updateServer(sock, directoryApplayer, directoryObserver, modify_queue, path)
        sendMsg(sock, CLOSE_CONNECTION)
        sock.close()
        time.sleep(timeout)


if __name__ == "__main__":
    main()