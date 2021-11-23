import socket
import string
import random
import utils

clientList = {}

# protocol constant
NEW_CLIENT_MASSAGE = "new client"
CLOSE_CONNECTION = "close connection"

def id_generator():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    id = ''.join(random.choice(chars) for _ in range(128))
    while id == NEW_CLIENT_MASSAGE:
        id = ''.join(random.choice(chars) for _ in range(128))

    return id

def sendMsg(sock,msg):
    sock.send(msg.encode())
    print("send:" + msg)
    r = sock.recv(1024)
    print("recv:" + r.decode())

def getMsg(sock):
    msg = sock.recv(1024).decode()
    print("recv:" + msg)
    sock.send(utils.PROTOCOL_ACK.encode())
    print("send:" + utils.PROTOCOL_ACK)
    return msg

def handleClient(clientSock,clientAddr):
    msg = getMsg(clientSock)
    print(msg)
    if (msg==NEW_CLIENT_MASSAGE):
        id = id_generator()
        print (id)
        sendMsg(clientSock, id)
        clientSock.send(utils.PROTOCOL_ACK.encode())
        d = utils.DirectoryApplayer(f'./serverFiles/{id}',clientSock)
        d.createFile("","True")
        clientList[id]={clientAddr:[]}
    else:
        id = msg
        sendMsg(clientSock, id)
        d = utils.DirectoryApplayer(id,clientSock)
        #new client, need to download
        try:
            if (clientAddr not in clientList[id]):
                clientList[id].append({clientAddr:[]})
                d.sendDir(f'./serverFiles/{id}')
                sendMsg(clientSock, utils.PROTOCOL_END_OF_MODIFICATION)
            else:
                # upload the changes
                while len(clientList[id][clientAddr]) != 0:
                    command = clientList[id][clientAddr].pop(0)
                    sendMsg(clientAddr, command)

                    if command.split(',')[0] == "created":
                        utils.sendFile(command.split(',')[1], clientSock)
        except:
            sendMsg(clientSock,'Client does not exsist in the system')


    handleCommands(clientSock,clientAddr,id)

def handleCommands(sock,clientAddr,id):
    d = utils.DirectoryApplayer(f'./serverFiles/{id}',sock)
    while (True): #need to reconect?
        cmd = getMsg(sock)
        if (cmd==CLOSE_CONNECTION):
            break
        d.handleNewModify(cmd)
        for key,value in clientList[id].items():
            if key!=clientAddr:
                value.append(cmd)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 12345))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        handleClient(client_socket,client_address)
        client_socket.close()


if __name__=="__main__":
    main()