import socket
import string
import random
from utils import *
import time
import os
import sys
import threading
clientList = {}

def id_generator(length):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    id = ''.join(random.choice(chars) for _ in range(length))
    while id == NEW_CLIENT_MASSAGE:
        id = ''.join(random.choice(chars) for _ in range(length))

    return id


def handleClient(clientSock):
    msg = getMsg(clientSock)
    id = ""
    clientId = ""

    # checks the status of the client
    if (msg==NEW_CLIENT_MASSAGE):
        id = id_generator(128)
        clientId = id_generator(10)
        print (f'***** NEW CLIENT ******\n{id}')
        time.sleep(0.1)
        sendMsg(clientSock, id+","+clientId)
        clientSock.send(PROTOCOL_ACK.encode())
        d = DirectoryApplayer(f'../serverFiles/{id}',clientSock)
        d.createFile("","True")
        clientList[id]={clientId:[]}
    else:
        if ',' in msg:
            id,clientId = msg.split(',',1)
        else:
            id = msg
            clientId = id_generator(10)
        time.sleep(0.5)
        sendMsg(clientSock, id+","+clientId)
        d = DirectoryApplayer(f'../serverFiles/{id}',clientSock)
        #new client, need to download
        if (clientId not in clientList[id]):
            clientList[id][clientId]=[]
            d.sendDir(f'../serverFiles/{id}')
            sendMsg(clientSock, PROTOCOL_END_OF_MODIFICATION)
            clientSock.send(PROTOCOL_ACK.encode())
        else:
            # upload the changes
            while len(clientList[id][clientId]) != 0:
                command = clientList[id][clientId].pop(0)
                sendMsg(clientSock, command)
                if command.split(',')[0] == "created" or command.split(',')[0] =="modified":
                    # chek if it a folder
                    if command.split(',')[2] == "True":
                        d.sendDir(os.path.join(f'../serverFiles/{id}', command.split(',')[1]))
                    else:
                        sendFile(os.path.join(f'../serverFiles/{id}',command.split(',')[1]), clientSock)

            sendMsg(clientSock, PROTOCOL_END_OF_MODIFICATION)
            clientSock.send(PROTOCOL_ACK.encode())

    handleCommands(clientSock,clientId,id)
    clientSock.close()

def handleCommands(sock,clientId,id):
    d = DirectoryApplayer(f'../serverFiles/{id}',sock)
    while (True): #need to reconect?
        cmd = getMsg(sock)
        if (cmd==CLOSE_CONNECTION):
            break
        d.handleNewModify(cmd)
        for key,value in clientList[id].items():
            if key!=clientId:
                value.append(cmd)

def main():
    if (len(sys.argv)!=2):
        print("Args are not valid!")
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(sys.argv[1])))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        t = threading.Thread(target=handleClient,args=(client_socket,))
        t.start()

if __name__=="__main__":
    main()