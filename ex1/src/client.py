import socket
import sys

def recieveData(sock):
    data,addr = sock.recvfrom(100)
    return data.decode("utf-8")

def sendData(sock,data,sockAddr):
    i=0
    packetNum=1
    while (i<len(data)):
        sliceData=str(packetNum)+"\n"
        curLen = len(sliceData)
        if (i+100-curLen<len(data)):
            sliceData += data[i:i+100-curLen]
        else:
            sliceData += data[i:]
        i+=100-curLen
        sock.sendto(sliceData.encode(),sockAddr)
        while True:
            try:
                if (recieveData(sock)==sliceData):
                    packetNum+=1
                    break
            except socket.timeout as e:
                sock.sendto(sliceData.encode(),sockAddr)


def readFile(fileName):
    fileData = open(fileName,'r').read()
    return fileData

def main():
    args = sys.argv[1:]
    if (len(args)!=3):
        print("Got wrong number of arguments")
        exit(1)

    ip,port,fileName = args
    fileData = ""
    try:
        fileData = readFile(fileName)
    except Exception as e:
        print(e)
        exit(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    try:
        sendData(s,fileData,(ip,int(port)))
    except Exception as e:
        print(e)
        s.close()
        exit(1)
        
    s.close()

if __name__ == "__main__":
    main()