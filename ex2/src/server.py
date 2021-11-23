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
    sock.recv(1024)

def getMsg(sock):
    msg = sock.recv(1024).decode()
    sock.send(utils.PROTOCOL_ACK.encode())
    return msg

def handleClient(clientSock,clientAddr):
    msg = getMsg(clientSock)
    print(msg)
    if (msg==NEW_CLIENT_MASSAGE):
        id = id_generator()
        print (id)
        sendMsg(clientSock, id)
        d = utils.DirectoryApplayer(id,clientSock)
        d.createFile(f'./serverFiles/{id}',True)
        clientList[id]={clientAddr:[]}
    else:
        id = msg
        d = utils.DirectoryApplayer(id,clientSock)
        #new client, need to download
        try:
            if (clientAddr not in clientList[id]):
                clientList[id].append({clientAddr:[]})
                d.sendDir(f'./serverFiles/{id}')
                sendMsg(clientSock, utils.PROTOCOL_END_OF_MODIFICATION)
        except:
            sendMsg(clientSock,'Client does not exsist in the system')

    handleCommands(clientSock,clientAddr,id)

def handleCommands(sock,clientAddr,id):
    d = utils.DirectoryApplayer(f'./serverFiles/{id}',sock)
    while (True): #need to reconect?
        cmd = getMsg(sock)
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