import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.sendto(b'Yogev Abarbanel - 326116910, Ido Barkai - ', ('127.0.0.1', 12345))
    data, addr = s.recvfrom(1024)
    print(str(data), addr)

    s.close()

if __name__ == "__main__":
    main()