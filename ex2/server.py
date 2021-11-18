import socket
import os
import time
import sys
import string
import random
import utils

def id_generator():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(128))

def sendMsg(sock,msg):
    sock.send(msg.encode())

def getMsg(sock):
    return sock.recv(1024).decode()

def handleClient(clientSock):
    msg = getMsg(clientSock)
    if (msg=="new client"):
        id = id_generator()
        print (id)
        #sendMsg(clientSock,id)
        utils.createFile(f'./try')

    else:
        pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 12345))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        handleClient(client_socket)
        client_socket.close()


if __name__=="__main__":
    main()