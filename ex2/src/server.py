import socket
import string
import random
import utils

clientList = {}

def id_generator():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(128))

def sendMsg(sock,msg):
    sock.send(msg.encode())

def getMsg(sock):
    return sock.recv(1024).decode()

def handleClient(clientSock,clientAddr):
    msg = getMsg(clientSock)
    print(msg)
    if (msg=="new client"):
        id = id_generator()
        print (id)
        sendMsg(clientSock,id)
        d = utils.DirectoryApplayer(id,clientSock)
        d.createFile(f'./{id}',True)
        clientList[id]={clientAddr:[]}
    else:
        id = msg
        d = utils.DirectoryApplayer(id,clientSock)
        #new client, need to download
        try:
            if (clientAddr not in clientList[id]):
                clientList[id].append({clientAddr:[]})
                d.sendDir(f'./{id}')  
        except:
            sendMsg(clientSock,'Client does not exsist in the system')

    handleCommands(clientSock,clientAddr,id)

def handleCommands(sock,clientAddr,id):
    d = utils.DirectoryApplayer(id,sock)
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