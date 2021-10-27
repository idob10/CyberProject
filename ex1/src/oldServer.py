import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 12345))

    while True:
        data, addr = s.recvfrom(100)
        print(str(data), addr)
        s.sendto(data, addr)


if __name__ == "__main__":
    main()