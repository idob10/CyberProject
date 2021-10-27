import socket
import sys

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #in case of error, print it and exit after closing the socket.
    try:
        s.bind(('', sys.argv[1]))
    except Exception as e:
        print(e)
        s.close()
        return

    expactedPacketnumber = 1

    #wiating for packets from client
    while True:
        data, addr = s.recvfrom(100)
        data = data.decode("utf-8").split('\n', 1)
        packetNumber, massage = data[0], data[1]

        #check that the packet the client send, is the one that should be sent.
        #if not, it ignore it.
        if int(packetNumber) == expactedPacketnumber:
            print(str(massage), end='')
            s.sendto(massage.encode(), addr)
            expactedPacketnumber += 1

if __name__ == "__main__":
    main()