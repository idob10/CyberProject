import socket
import string
import random
import utils
import time
import os
clientList = {}

# protocol constant
NEW_CLIENT_MASSAGE = "new client"
CLOSE_CONNECTION = "close connection"

def id_generator(length):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    id = ''.join(random.choice(chars) for _ in range(length))
    while id == NEW_CLIENT_MASSAGE:
        id = ''.join(random.choice(chars) for _ in range(length))

    return id

def sendMsg(sock,msg):
    sock.send(msg.encode())
    print("send:" + msg)
    r = sock.recv(1024)
    print("recv:" + r.decode())

def sendBytesMsg(sock,msg):
    sock.send(msg)
    print("sent bytes")
    r = sock.recv(1024)
    print("recv:" + r.decode())

def getMsg(sock):
    msg = sock.recv(1024).decode()
    print("recv:" + msg)
    sock.send(utils.PROTOCOL_ACK.encode())
    print("send:" + utils.PROTOCOL_ACK)
    return msg

def handleClient(clientSock):
    msg = getMsg(clientSock)
    print(msg)

    id = ""
    clientId = ""
    if (msg==NEW_CLIENT_MASSAGE):
        id = id_generator(128)
        clientId = id_generator(10)
        print (id)
        time.sleep(0.1)
        sendMsg(clientSock, id+","+clientId)
        clientSock.send(utils.PROTOCOL_ACK.encode())
        d = utils.DirectoryApplayer(f'./serverFiles/{id}',clientSock)
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
        d = utils.DirectoryApplayer(f'./serverFiles/{id}',clientSock)
        #new client, need to download
        if (clientId not in clientList[id]):
            clientList[id][clientId]=[]
            d.sendDir(f'./serverFiles/{id}')
            sendMsg(clientSock, utils.PROTOCOL_END_OF_MODIFICATION)
            clientSock.send(utils.PROTOCOL_ACK.encode())
        else:
            # upload the changes
            while len(clientList[id][clientId]) != 0:
                command = clientList[id][clientId].pop(0)
                sendMsg(clientSock, command)
                if command.split(',')[0] == "created":
                    # chek if it a folder
                    if command.split(',')[2] == "True":
                        d.sendDir(os.path.join(f'./serverFiles/{id}', command.split(',')[1]))
                    else:
                        utils.sendFile(os.path.join(f'./serverFiles/{id}',command.split(',')[1]), clientSock)

            sendMsg(clientSock, utils.PROTOCOL_END_OF_MODIFICATION)
            clientSock.send(utils.PROTOCOL_ACK.encode())

    handleCommands(clientSock,clientId,id)

def handleCommands(sock,clientId,id):
    d = utils.DirectoryApplayer(f'./serverFiles/{id}',sock)
    while (True): #need to reconect?
        cmd = getMsg(sock)
        if (cmd==CLOSE_CONNECTION):
            break
        d.handleNewModify(cmd)
        for key,value in clientList[id].items():
            if key!=clientId:
                value.append(cmd)

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