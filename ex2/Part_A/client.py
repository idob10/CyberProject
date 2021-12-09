import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 12345))

s.send(b'Yogev Abarbanel, Ido Barkai')
data = s.recv(100)
print("Server sent: ", data)
s.send(b'326116910, 326629987')

s.close()