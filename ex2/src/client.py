import socket
import time
import utils
import os
from server import NEW_CLIENT_MASSAGE
from server import CLOSE_CONNECTION
from server import sendMsg
from server import getMsg
from watchdog.observers import Observer

def connect(sock, path, isNewClient, directoryApplayer):
    if not isNewClient:
        msg = getMsg(sock)
        while msg != utils.PROTOCOL_END_OF_MODIFICATION:
            directoryApplayer.handleNewModify(msg)

    # upload the dir
    directoryApplayer.sendDir(path)


def updateServer(sock, id, directoryApplayer, modify_queue):
    sendMsg(sock, id)

    msg = getMsg(sock)
    while msg != utils.PROTOCOL_END_OF_MODIFICATION:
        directoryApplayer.handleNewModify(msg)

    # upload the changes
    while len(modify_queue) != 0:
        command = modify_queue.pop(0)
        sendMsg(sock, command)

        if command.split(',')[0] == "created":
            utils.sendFile(command.split(',')[1],sock)

def main():
    ip = '127.0.0.1'
    port = 12345
    path = f"../test"
    timeout = 5

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    directoryApplayer = utils.DirectoryApplayer(path, sock)

    # In case of a new client
    id = ""
    isNewClient = False
    if id == "":
        sendMsg(sock, NEW_CLIENT_MASSAGE)
        isNewClient = True
    else:
        sendMsg(sock, id)

    id = getMsg(sock)
    sock.recv(1024) #getting ack
    connect(sock, path, isNewClient, directoryApplayer)
    sendMsg(sock, CLOSE_CONNECTION)

    #start observing
    modify_queue = []
    directoryObserver = utils.DirectoryObserver(modify_queue)
    observer = Observer()
    observer.schedule(directoryObserver, path, recursive=True)
    observer.start()
    while True:
        updateServer(sock, id, directoryApplayer, modify_queue)
        sendMsg(sock, CLOSE_CONNECTION)
        time.sleep(timeout)


if __name__ == "__main__":
    main()