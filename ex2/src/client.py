import socket
import time
import utils
from server import NEW_CLIENT_MASSAGE
from server import CLOSE_CONNECTION
from server import sendMsg
from server import getMsg

def connect(sock, path, id, directoryApplayer):
    if id == None:
        sendMsg(sock, NEW_CLIENT_MASSAGE)
    else:
        sendMsg(sock, id)

    id = getMsg(sock)

    msg = getMsg(sock)
    while msg != utils.PROTOCOL_END_OF_MODIFICATION:
        directoryApplayer.handleNewModify(msg)

    # upload the dir
    utils.sendDir(sock, path)


def updateServer(sock,id, directoryApplayer, modify_queue):
    sendMsg(sock, id)
    id = getMsg(sock)

    msg = getMsg(sock)
    while msg != utils.PROTOCOL_END_OF_MODIFICATION:
        directoryApplayer.handleNewModify(msg)

    # upload the changes
    while len(modify_queue) != 0:
        command = modify_queue.pop(0)
        sendMsg(sock, command)


def main():
    ip = '127.0.0.1'
    port = 12345
    path = "C:\Yogev\BIU\Second year\Networks\ex2\test"
    timeout = 5

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    directoryApplayer = utils.DirectoryApplayer(path, sock)

    # In case of a new client
    id = None
    connect(sock, path, id, directoryApplayer)

    modify_queue = []
    directoryObserver = utils.DirectoryObserver(modify_queue)
    while True:
        updateServer(sock, id, directoryApplayer, modify_queue)
        time.sleep(timeout)


if __name__ == "__main__":
    main()