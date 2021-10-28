import socket
import sys

def recieveData(sock):
    data,addr = sock.recvfrom(100)
    return data.decode()

def sendData(sock,data,sockAddr):
    i=0
    while (i<len(data)):
        sliceData=""
        if (i+100<len(data)):
            sliceData = data[i:i+100]
        else:
            sliceData = data[i:]
        i+=100
        sock.sendto(sliceData.encode(),sockAddr)
        if (recieveData(sock)==sliceData):
            pass


def readFile(fileName):
    fileData = open(fileName,'r').read()
    return fileData

def main():
    args = sys.argv[1:]
    if (len(args)!=3):
        print("Got wrong number of arguments")
        exit(1)

    ip,port,fileName = args
    fileData = readFile(fileName)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendData(s,fileData,(ip,int(port)))
    s.close()

if __name__ == "__main__":
    main()