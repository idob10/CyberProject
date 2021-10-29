import socket
import sys

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #in case of error, print it and exit after closing the socket.
    try:
        s.bind(('', int(sys.argv[1])))
    except Exception as e:
        print(e)
        s.close()
        return

    expactedPacketnumber = 1

    #wiating for packets from client
    while True:
        data, addr = s.recvfrom(100)
        data = data.decode("utf-8")
        packetNumber, message = data.split('\n',1)[0], data.split('\n',1)[1]

        #check that the packet the client send, is the one that should be sent.
        #if not, it ignore it.
        if int(packetNumber) == expactedPacketnumber:
            print(str(message), end='')
            s.sendto(data.encode(), addr)
            expactedPacketnumber += 1
        else:
            s.sendto(data.encode(), addr)

if __name__ == "__main__":
    main()